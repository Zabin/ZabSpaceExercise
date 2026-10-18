"""Bus-model integration with the deterministic event loop (``01-research/06`` §4.1-4.2).

``BusSystem`` registers the event handlers that evolve every satellite's ``BusState`` over time
and that deliver pass-gated telemetry. Eclipse (lighting) is computed from orbit geometry + the
analytic Sun direction, so a ``bus_tick`` event is a pure function of world + time and replays
exactly. Scheduling a cadence of ``bus_tick`` events keeps the (otherwise continuous) bus
evolution inside the event log, preserving the determinism guarantee.

Handlers:
  * ``bus_tick``         — advance all sats' bus state (charge/drain, ISR storage fill).
  * ``telemetry_contact``— refresh a sat's ground-view snapshot (pass-gated discovery).
  * ``isr_downlink``     — empty a sat's onboard storage at a downlink pass.
"""

from __future__ import annotations

import numpy as np

from spacesim.engine.bus import advance_bus, downlink_storage, refresh_ground_view
from spacesim.engine.orbit import MU_EARTH, R_EARTH_EQ
from spacesim.engine.perturbations import drag_multiplier, secular_drag_decay
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.sun import eclipse_fraction
from spacesim.engine.world import WorldState


class BusSystem:
    def __init__(self, sim, propagator: ModeratePropagator | None = None,
                 tick_period_s: float = 300.0) -> None:
        self.sim = sim
        self.prop = propagator or ModeratePropagator()
        # IP-1230 (ADR-0039 decision 7) — the drag step's dt: a construction-time constant, so
        # live advance, rewind and replay all apply the identical per-tick decrement.
        self.tick_period_s = float(tick_period_s)
        sim.register_handler("bus_tick", self._h_tick)
        sim.register_handler("telemetry_contact", self._h_contact)
        sim.register_handler("isr_downlink", self._h_downlink)

    def schedule_ticks(self, period_s: float, until: int, start: int | None = None,
                       anchor: int | None = None) -> None:
        """Queue a regular cadence of ``bus_tick`` events up to ``until``.

        IP-1064 (BL-0132): with ``anchor``, ticks fall on the grid ``anchor + k·step`` — the first
        tick is the next grid point after ``start`` — so re-arming after a rewind to a time between
        ticks does not shift the cadence. Without it, the grid starts at ``start`` (unchanged)."""
        step = int(period_s * 1_000_000)
        t = self.sim.clock.now if start is None else start
        if anchor is not None and t >= anchor:
            t = anchor + ((t - anchor) // step) * step
        t += step
        while t <= until:
            self.sim.schedule(t, "bus_tick")
            t += step

    def _sunlit(self, world: WorldState, asset, t: int) -> float:
        """Lit fraction in [0, 1] (penumbra-aware) so the power tick ramps smoothly
        through terminator crossings instead of binary-switching."""
        if asset.orbit is None:
            return 1.0
        r, _ = self.prop.rv(asset.orbit, t)
        return eclipse_fraction(r, t)

    def _h_tick(self, world: WorldState, payload: dict, rng) -> None:
        sw = str(world.space_weather.get("severity", "none"))
        for asset in world.assets.values():
            if asset.bus_state is None:
                continue
            advance_bus(asset.bus_state, asset.payload_state, world.now,
                        self._sunlit(world, asset, world.now), space_weather=sw)
        self._apply_index_drag(world)

    def _apply_index_drag(self, world: WorldState) -> None:
        """IP-1230 (FR-1230, ADR-0039 decision 7) — opt-in, index-driven secular LEO drag.

        No declared series → return at once (no state change, no RNG): every vignette that does
        not opt in is byte-identical. Otherwise each ``kepler`` LEO/LEO_SSO asset with an authored
        ballistic coefficient loses ``secular_drag_decay(alt, BC, dt) × f_solar × f_geo`` of
        semi-major axis, applied as the equivalent retrograde along-track Δv through the
        propagator seam (re-epoched at this tick, so position is continuous). Environment, not a
        manoeuvre: no ``delta_v_ms`` is charged."""
        series = world.space_weather.get("index_series")
        if not series:
            return
        mult = drag_multiplier(series, world.now)
        for asset in world.assets.values():
            orbit, bc = asset.orbit, asset.ballistic_coeff_m2_kg
            if (orbit is None or orbit.source != "kepler" or bc is None or bc <= 0
                    or orbit.regime not in ("LEO", "LEO_SSO")):
                continue
            r, v = self.prop.rv(orbit, world.now)
            a = float(np.linalg.norm(r))
            speed = float(np.linalg.norm(v))
            drop = -secular_drag_decay(a - R_EARTH_EQ, bc, self.tick_period_s) * mult
            if drop <= 0.0 or speed == 0.0:
                continue
            dv = MU_EARTH * drop / (2.0 * a * a * speed)
            asset.orbit = self.prop.apply_impulse(orbit, -dv * (v / speed), world.now)

    def _h_contact(self, world: WorldState, payload: dict, rng) -> None:
        asset = world.assets.get(payload["asset"])
        if asset is not None and asset.bus_state is not None:
            refresh_ground_view(asset.bus_state, world.now)

    def _h_downlink(self, world: WorldState, payload: dict, rng) -> None:
        asset = world.assets.get(payload["asset"])
        if asset is not None and asset.bus_state is not None:
            downlink_storage(asset.bus_state, payload.get("fraction", 1.0))
