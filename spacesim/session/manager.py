"""SessionManager — the authoritative owner of a running exercise.

Wires the deterministic Simulation to the OrderSystem and BusSystem, loads a vignette into a
WorldState, controls time (step / rewind / undo via the engine's replay primitive), applies
injects through the event loop (so they are logged and replay-safe), and evaluates objectives.
Players send *intents*; the manager validates and mutates state — never the other way round.
"""

from __future__ import annotations

from typing import Optional

from spacesim.content.vignette import Vignette, build_world, evaluate_objectives
from spacesim.engine import telemetry
from spacesim.engine.busmodel import BusSystem
from spacesim.engine.custody import Track
from spacesim.engine.entities import Asset
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState
from spacesim.session.api import OrderAck
from spacesim.session.cells import CellController
from spacesim.session.scene import build_scene

BUS_TICK_PERIOD_S = 300.0


class SessionManager:
    def __init__(self, vignette: Vignette, overrides: Optional[dict] = None, seed: int = 0) -> None:
        self.vignette = vignette
        self.world, self.ctx = build_world(vignette, overrides)
        self.sim = Simulation(self.world, seed=seed)
        self.sim.register_handler("inject", self._h_inject)
        self.osys = OrderSystem(self.sim, roe=dict(self.ctx.roe))
        self.bus = BusSystem(self.sim)
        self.started = False
        self.horizon = self.ctx.start_epoch + int(self.vignette.estimated_duration_min * 60 * 4 * 1_000_000)

    # -- lifecycle -------------------------------------------------------------
    def start(self) -> None:
        self.started = True
        self._arm_schedule(self.sim.clock.now)

    def _arm_schedule(self, from_t: int) -> None:
        """(Re)queue bus ticks and scripted time-injects after ``from_t`` — also used after a
        rewind, since a rewind clears pending future events."""
        self.bus.schedule_ticks(BUS_TICK_PERIOD_S, until=self.horizon, start=from_t)
        for inj in self.vignette.injects:
            trig = inj.trigger or {}
            if trig.get("type") == "time" and "at_sim_s" in trig:
                at = self.ctx.start_epoch + int(float(trig["at_sim_s"]) * 1_000_000)
                if at > from_t:
                    self.sim.schedule(at, "inject", {"effects": inj.effects})

    # -- time control ----------------------------------------------------------
    def step(self, dt_sim_s: float) -> None:
        self.advance_to(self.sim.clock.now + int(dt_sim_s * 1_000_000))

    def advance_to(self, t: int) -> None:
        self.sim.advance_to(t)
        self.world = self.sim.world

    def rewind_to(self, t: int) -> None:
        self.sim.rewind_to(t)
        self._rebind()
        if self.started:
            self._arm_schedule(t)

    def undo_last(self, n: int = 1) -> None:
        self.sim.undo_last(n)
        self._rebind()

    def _rebind(self) -> None:
        # After a replay-based rewind the world object is fresh; repoint live references at it.
        self.world = self.sim.world
        self.osys.world = self.sim.world

    # -- intents ---------------------------------------------------------------
    def issue_order(self, cell: str, order: Order) -> OrderAck:
        order.cell = cell
        result = self.osys.issue(order)
        return OrderAck(
            ok=result.status != "rejected",
            reason=result.fail_reason or "",
            status=result.status,
            earliest_window=result.earliest_window,
            delivery_path=result.delivery_path,
        )

    def add_tle(self, asset_id: str, line1: str, line2: str, owner: str = "blue", kind: str = "satellite") -> tuple[bool, str]:
        """White-Cell force edit: add a real named satellite by TLE (validated via sgp4)."""
        if self.started:
            return False, "cannot edit force after start"
        l1, l2 = line1.strip(), line2.strip()
        if not (l1.startswith("1 ") and l2.startswith("2 ") and len(l1) >= 69 and len(l2) >= 69):
            return False, "invalid TLE: expected two 69-char lines starting with '1 ' and '2 '"
        try:
            from sgp4.api import Satrec
            sat = Satrec.twoline2rv(l1, l2)
            err, _, _ = sat.sgp4(sat.jdsatepoch, sat.jdsatepochF)
            if err != 0:
                return False, f"invalid TLE: sgp4 error {err}"
        except Exception as exc:  # malformed TLE is a normal rejection, not a crash
            return False, f"invalid TLE: {exc}"
        orbit = OrbitState(source="tle", tle_line1=line1, tle_line2=line2, epoch=self.ctx.start_epoch)
        self.world.assets[asset_id] = Asset(id=asset_id, owner=owner, kind=kind, orbit=orbit)
        self.sim._initial_state = self.world.model_dump()  # re-baseline so rewind keeps the edit
        return True, ""

    def fire_inject(self, inject) -> None:
        effects = inject if isinstance(inject, list) else self._inject_effects(inject)
        now = self.sim.clock.now
        self.sim.schedule(now, "inject", {"effects": effects})
        self.sim.advance_to(now)  # apply + log immediately (so it replays through the event log)
        self.world = self.sim.world

    def _inject_effects(self, inject) -> list:
        if isinstance(inject, dict):
            return inject.get("effects", [])
        for inj in self.vignette.injects:  # look up by id
            if inj.id == inject:
                return inj.effects
        return []

    # -- reads -----------------------------------------------------------------
    def get_view(self, cell: str):
        return CellController.view(self.sim.world, cell, objectives=self.objectives().get(cell, {}))

    def get_scene(self, cell: str):
        return build_scene(self.sim.world, cell)

    def _owns(self, cell: str, asset_id: str) -> bool:
        asset = self.sim.world.assets.get(asset_id)
        return asset is not None and (cell == "white" or asset.owner == cell)

    def get_telemetry(self, cell: str, asset_id: str):
        """Subsystem telemetry DB + symptom log for an own asset (fog: own assets only)."""
        if not self._owns(cell, asset_id):
            return None
        t, seed = self.sim.clock.now, self.sim._seed
        asset = self.sim.world.assets[asset_id]
        return {
            "asset": asset_id, "now": t,
            "bus_mode": asset.bus_state.mode if asset.bus_state else None,
            "subsystems": telemetry.telemetry_db(self.sim.world, asset_id, t, seed),
            "log": telemetry.subsystem_log(self.sim.world, asset_id, t, seed),
        }

    def get_series(self, cell: str, asset_id: str, param: str,
                   t0=None, t1=None, n: int = 120):
        if not self._owns(cell, asset_id) or param not in telemetry.PARAMS:
            return None
        now = self.sim.clock.now
        t1 = now if t1 is None else int(t1)
        t0 = max(self.ctx.start_epoch, now - 3600 * 1_000_000) if t0 is None else int(t0)
        return {"asset": asset_id, "param": param,
                "points": telemetry.series(self.sim.world, asset_id, param, t0, t1, n, self.sim._seed)}

    def get_godview(self) -> WorldState:
        return self.sim.world

    def get_eventlog(self, since_seq: int = 0):
        return [e for e in self.sim.eventlog.entries if e.seq >= since_seq]

    def objectives(self) -> dict:
        return evaluate_objectives(self.sim.world, self.ctx)

    # -- inject handler (runs inside the deterministic event loop) -------------
    def _h_inject(self, world: WorldState, payload: dict, rng) -> None:
        for eff in payload.get("effects", []):
            kind = eff.get("type")
            if kind == "message":
                world.messages.append({"to": eff.get("to", []), "text": eff.get("text", ""), "t": world.now})
            elif kind == "reveal_asset":
                to = eff["to"]
                obj = eff["target"]
                if not any(t.owner == to and t.object == obj for t in world.tracks):
                    world.tracks.append(Track(object=obj, owner=to, last_observation=world.now,
                                              confidence=1.0, characterized=True, classification="hostile"))
            elif kind == "political_consequence":
                world.consequences.append({**eff, "t": world.now})
            elif kind == "patch_cyber_vuln":
                asset = world.assets.get(eff["target"])
                if asset is not None:
                    for v in asset.cyber_vulnerabilities:
                        if v.get("vector") == eff.get("vector"):
                            v["patched"] = True
