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
from spacesim.engine.access import AccessProvider, COMMAND_UPLINK, TELEMETRY_DOWNLINK
from spacesim.engine.busmodel import BusSystem
from spacesim.engine.custody import Track
from spacesim.engine.entities import Asset
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem, scene_from_world
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
        self.osys.orders.clear()           # queued events were dropped by the rewind
        self.osys._sensor_bookings.clear()

    # -- intents ---------------------------------------------------------------
    def issue_order(self, cell: str, order: Order) -> OrderAck:
        order.cell = cell
        result = self.osys.issue(order)
        return self._order_ack(result)

    def validate_order(self, cell: str, order: Order) -> OrderAck:
        """Dry-run an order for the UI: would it be accepted, with which window/path, or why not?

        Read-only (no scheduling, no registry, no bookings) so the console can pre-disable buttons
        and preview the scheduled window without mutating the session (`OPERATOR-UI-DESIGN.md` §12).
        """
        order.cell = cell
        result = self.osys.dry_run(order)
        return self._order_ack(result)

    @staticmethod
    def _order_ack(result: Order) -> OrderAck:
        return OrderAck(
            ok=result.status != "rejected",
            id=result.id,
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

    # -- command queue --------------------------------------------------------
    def list_orders(self, cell: str) -> list[dict]:
        """The cell's order queue (white sees all). Display status flips queued→executed past the window."""
        now = self.sim.clock.now
        out = []
        for o in self.osys.orders.values():
            if cell != "white" and o.cell != cell:
                continue
            status = o.status
            if status == "queued" and o.earliest_window and now > o.earliest_window[0]:
                status = "executed"
            out.append({"id": o.id, "cell": o.cell, "actor": o.actor, "action": o.action,
                        "target": o.target, "status": status, "delivery_path": o.delivery_path,
                        "window": o.earliest_window, "reason": o.fail_reason})
        return out

    def cancel_order(self, cell: str, order_id: str) -> bool:
        o = self.osys.orders.get(order_id)
        if o is None or (cell != "white" and o.cell != cell):
            return False
        return self.osys.cancel(order_id)

    def windows_ahead(self, cell: str, asset_id: str, horizon_s: float = 6 * 3600, limit: int = 16):
        """Upcoming command-uplink + telemetry-downlink windows for an own satellite (pass timeline)."""
        if not self._owns(cell, asset_id):
            return None
        asset = self.sim.world.assets.get(asset_id)
        if asset is None or asset.orbit is None:
            return {"asset": asset_id, "now": self.sim.clock.now, "windows": []}
        ap = AccessProvider(scene_from_world(self.sim.world), config=self.osys.access_config)
        now = self.sim.clock.now
        hz = now + int(horizon_s * 1_000_000)
        stations = [i for i, a in self.sim.world.assets.items()
                    if a.owner == asset.owner and a.location is not None]
        wins = []
        for st in stations:
            for ch in (COMMAND_UPLINK, TELEMETRY_DOWNLINK):
                for w in ap.windows(st, asset_id, ch, now, hz):
                    wins.append({"channel": ch, "via": st, "start": w.start, "end": w.end,
                                 "quality": round(w.quality, 2)})
        wins.sort(key=lambda w: w["start"])
        return {"asset": asset_id, "now": now, "horizon_s": horizon_s, "windows": wins[:limit]}

    def list_injects(self) -> list[dict]:
        return [{"id": i.id, "label": i.label, "trigger": (i.trigger or {}).get("type", "manual")}
                for i in self.vignette.injects]

    # -- save / resume --------------------------------------------------------
    def save_state(self) -> dict:
        """A complete, serializable snapshot: history + pending events + the order queue.

        Resume is exact because the deterministic core re-derives state from (initial, seed,
        eventlog); pending scheduled events and the order registry are persisted alongside so
        queued orders, bus ticks, and scripted injects survive a save/load."""
        return {
            "vignette_id": self.vignette.id,
            "overrides": dict(self.ctx.param_values),
            "seed": self.sim._seed,
            "final_time": self.sim.clock.now,
            "started": self.started,
            "eventlog": self.sim.eventlog.model_dump(),
            "pending": [{"t": ev.t, "kind": ev.kind, "actor": ev.actor, "payload": ev.payload, "tag": ev.tag}
                        for ev in self.sim.scheduler.pending()],
            "orders": [vars(o) for o in self.osys.orders.values()],
        }

    @classmethod
    def from_state(cls, state: dict) -> "SessionManager":
        from spacesim.content.vignette import load_vignette as _load
        from spacesim.engine.eventlog import EventLog
        mgr = cls(_load(state["vignette_id"]), overrides=state.get("overrides"), seed=state["seed"])
        mgr.sim.eventlog = EventLog.model_validate(state["eventlog"])
        mgr.sim._rebuild(stop_time=state["final_time"])   # replay history → world + rng at save time
        mgr._rebind()
        for p in state.get("pending", []):
            mgr.sim.schedule(p["t"], p["kind"], p.get("payload"), actor=p.get("actor", "system"), tag=p.get("tag", ""))
        for od in state.get("orders", []):
            o = Order(**od)
            mgr.osys.orders[o.id] = o
        nums = [int(o.id.split("-")[1]) for o in mgr.osys.orders.values() if o.id.startswith("ord-")]
        mgr.osys._order_counter = max(nums, default=0)
        mgr.started = state.get("started", False)
        return mgr

    # -- fleet SOH rollup & alarms --------------------------------------------
    def alarms(self, cell: str) -> list[dict]:
        """Aggregate off-nominal symptoms across the cell's own assets (fog: own only)."""
        out = []
        t, seed = self.sim.clock.now, self.sim._seed
        for aid, a in self.sim.world.assets.items():
            if a.bus_state is None or (cell != "white" and a.owner != cell):
                continue
            for line in telemetry.subsystem_log(self.sim.world, aid, t, seed):
                out.append({"asset": aid, "text": line})
        for cons in self.sim.world.consequences:
            if cell == "white":
                out.append({"asset": "—", "text": f"political consequence: {cons.get('cause', '')} ({cons.get('severity', '')})"})
        return out

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
                   t0=None, t1=None, n: int = 120, nominal: bool = False):
        if not self._owns(cell, asset_id) or param not in telemetry.PARAMS:
            return None
        now = self.sim.clock.now
        t1 = now if t1 is None else int(t1)
        t0 = max(self.ctx.start_epoch, now - 3600 * 1_000_000) if t0 is None else int(t0)
        return {"asset": asset_id, "param": param, "nominal": nominal,
                "points": telemetry.series(self.sim.world, asset_id, param, t0, t1, n,
                                           self.sim._seed, nominal=nominal)}

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
