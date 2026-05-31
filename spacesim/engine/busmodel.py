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

from spacesim.engine.bus import advance_bus, downlink_storage, refresh_ground_view
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.sun import is_sunlit
from spacesim.engine.world import WorldState


class BusSystem:
    def __init__(self, sim, propagator: ModeratePropagator | None = None) -> None:
        self.sim = sim
        self.prop = propagator or ModeratePropagator()
        sim.register_handler("bus_tick", self._h_tick)
        sim.register_handler("telemetry_contact", self._h_contact)
        sim.register_handler("isr_downlink", self._h_downlink)

    def schedule_ticks(self, period_s: float, until: int, start: int | None = None) -> None:
        """Queue a regular cadence of ``bus_tick`` events up to ``until``."""
        step = int(period_s * 1_000_000)
        t = self.sim.clock.now if start is None else start
        t += step
        while t <= until:
            self.sim.schedule(t, "bus_tick")
            t += step

    def _sunlit(self, world: WorldState, asset, t: int) -> bool:
        if asset.orbit is None:
            return True
        r, _ = self.prop.rv(asset.orbit, t)
        return is_sunlit(r, t)

    def _h_tick(self, world: WorldState, payload: dict, rng) -> None:
        sw = str(world.space_weather.get("severity", "none"))
        for asset in world.assets.values():
            if asset.bus_state is None:
                continue
            advance_bus(asset.bus_state, asset.payload_state, world.now,
                        self._sunlit(world, asset, world.now), space_weather=sw)

    def _h_contact(self, world: WorldState, payload: dict, rng) -> None:
        asset = world.assets.get(payload["asset"])
        if asset is not None and asset.bus_state is not None:
            refresh_ground_view(asset.bus_state, world.now)

    def _h_downlink(self, world: WorldState, payload: dict, rng) -> None:
        asset = world.assets.get(payload["asset"])
        if asset is not None and asset.bus_state is not None:
            downlink_storage(asset.bus_state, payload.get("fraction", 1.0))
