"""SessionManager — the authoritative owner of a running exercise.

Wires the deterministic Simulation to the OrderSystem and BusSystem, loads a vignette into a
WorldState, controls time (step / rewind / undo via the engine's replay primitive), applies
injects through the event loop (so they are logged and replay-safe), and evaluates objectives.
Players send *intents*; the manager validates and mutates state — never the other way round.
"""

from __future__ import annotations

import math
import threading
import time as _time
from typing import Literal, Optional

from spacesim.content.vignette import Vignette, build_world, evaluate_objectives
from spacesim.engine import telemetry
from spacesim.engine.access import AccessProvider, COMMAND_UPLINK, TELEMETRY_DOWNLINK
from spacesim.engine.bus import enter_safe_mode, exit_safe_mode
from spacesim.engine.busmodel import BusSystem
from spacesim.engine.custody import Track
from spacesim.engine.entities import Asset
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem, scene_from_world
from spacesim.engine.recovery import RecoverySystem
from spacesim.engine.simulation import Simulation
from spacesim.engine.ssn import SSNRequest, SSNSystem
from spacesim.engine.world import WorldState
from spacesim.session.api import OrderAck
from spacesim.session.cells import CellController
from spacesim.session.scene import build_scene

BUS_TICK_PERIOD_S = 300.0


class SessionManager:
    def __init__(
        self, vignette: Vignette, overrides: Optional[dict] = None, seed: int = 0,
        classification: Optional[str] = None,
    ) -> None:
        self.vignette = vignette
        # IP-1120 — resolved once, here, so the UI-facing read path and every export path
        # (aar.export_csv, save_state) read this single value, never re-deriving it independently.
        self.classification = classification or vignette.classification
        # IP-1151 (FR-4210) — seat -> {asset_or_constellation, role} bindings, set by White Cell at
        # session setup. Not itself gameplay/exercise state (no engine/WorldState involvement) —
        # a pre-start staffing concern only, per FS-115's own Scope boundary.
        self.role_assignments: dict[str, dict] = {}
        # IP-1174 (FR-5160) — cell -> declared seat-id list, set by White Cell during Creator
        # authoring. Same placement rationale as role_assignments above: UI-setup state, not
        # exercise state.
        self.seats_declared: dict[str, list[str]] = {}
        self.world, self.ctx = build_world(vignette, overrides)
        self.sim = Simulation(self.world, seed=seed)
        self.sim.register_handler("inject", self._h_inject)
        self.sim.register_handler("condition_check", self._h_condition_check)
        self.osys = OrderSystem(self.sim, roe=dict(self.ctx.roe), gating_rules=list(self.ctx.gating_rules))
        self.bus = BusSystem(self.sim)
        self.recovery = RecoverySystem(
            self.sim,
            difficulty=self.ctx.param_values.get("safe_mode_recovery_difficulty", "realistic"),
            root_cause_persists=bool(self.ctx.param_values.get("safe_mode_root_cause_persists", True)),
            access_config=self.osys.access_config,
        )
        # Mock SSN — per-cell networks, request-tasked. Constructed always (empty dict if vignette opted out).
        # FUTURE-WORK §7 — optional per-cell collection budget. Vignette params:
        #   ssn_blue_budget / ssn_red_budget (int); None = unlimited (legacy default).
        ssn_budgets = None
        bbudget = self.ctx.param_values.get("ssn_blue_budget")
        rbudget = self.ctx.param_values.get("ssn_red_budget")
        if overrides is not None:
            bbudget = overrides.get("ssn_blue_budget", bbudget)
            rbudget = overrides.get("ssn_red_budget", rbudget)
        if bbudget is not None or rbudget is not None:
            ssn_budgets = {}
            if bbudget is not None: ssn_budgets["blue"] = int(bbudget)
            if rbudget is not None: ssn_budgets["red"] = int(rbudget)
        # FUTURE-WORK §7 — third-party / commercial SSN feed. Vignette param
        # ssn_commercial_dispersion (off|sparse|regional|global|proliferated) opts in.
        ssn_nets = dict(self.ctx.ssn_networks)
        ccdisp = self.ctx.param_values.get("ssn_commercial_dispersion", "off")
        if overrides is not None:
            ccdisp = overrides.get("ssn_commercial_dispersion", ccdisp)
        if str(ccdisp) not in ("off", ""):
            from spacesim.engine.ssn import instantiate_network as _ssn_instantiate
            # Network is keyed "commercial" (so submit_request finds it via req.network); sensors
            # themselves are owned 'neutral' since Sensor.owner is Literal[blue|red|neutral].
            cnet = _ssn_instantiate(self.world, "commercial", str(ccdisp),
                                     affiliation="commercial", sensor_owner="neutral")
            if cnet is not None:
                ssn_nets["commercial"] = cnet
        self.ssn = SSNSystem(self.sim, ssn_nets,
                              access_config=self.osys.access_config, budgets=ssn_budgets)
        # FUTURE-WORK §7: organic→SSN auto-cueing. Opt-in via parameter ssn_auto_cue (vignette
        # default OR session override accepted, since not every vignette declares the dial).
        ssn_auto = bool(self.ctx.param_values.get("ssn_auto_cue", False))
        if not ssn_auto and overrides is not None:
            ssn_auto = bool(overrides.get("ssn_auto_cue", False))
        if ssn_auto and self.ctx.ssn_networks:
            self.osys.auto_cue_ssn = self.ssn
        self.started = False
        self.horizon = self.ctx.start_epoch + int(self.vignette.estimated_duration_min * 60 * 4 * 1_000_000)
        # Multiplayer/server-clock state. NOT engine state — never read by spacesim/engine/, so
        # determinism + import-guard stay intact. RLock so nested locked calls can't deadlock.
        self._lock = threading.RLock()
        self._clock_running = False
        self._wall_anchor: Optional[float] = None   # epoch seconds (time.time())
        self._sim_anchor: Optional[int] = None      # sim microseconds at the wall anchor
        self._rate = 1.0                             # sim seconds per wall second
        # Audit Jun 2026 §F2 — clock-lag watchdog. The 24/48-satellite "cap" is
        # not an engine limit; it was sized for typical White-Cell hardware.
        # User-authored vignettes can carry more, but if catch_up() takes long
        # enough that the wall clock outruns the sim repeatedly, the hardware
        # is insufficient for this scenario and White Cell needs to know.
        self._catch_up_lag_history: list[float] = []  # last few catch_up wall-cost samples (s)
        self._clock_lag_warning: Optional[dict] = None  # surfaced by clock_state()

    # -- seat-to-role assignment (IP-1151, FR-4210) -----------------------------
    def assign_role(self, seat: str, asset_or_constellation: str, role: str) -> None:
        self.role_assignments[seat] = {"asset_or_constellation": asset_or_constellation, "role": role}

    @staticmethod
    def _role_covers(assigned: str, required: str) -> bool:
        """A "both" assignment covers any requirement; otherwise the roles must match exactly."""
        return assigned == "both" or assigned == required

    def staffing_report(self) -> list[dict]:
        """Every mandatory ``roles_needed`` entry with no covering seat assignment. Empty for a
        vignette that declares nothing (every vignette shipped before this package) — this method
        must never itself block a start; ``InProcessSession.start()`` is what gates on it."""
        return [
            {"asset_or_constellation": req.asset_or_constellation, "role": req.role, "mandatory": req.mandatory}
            for req in self.vignette.roles_needed
            if req.mandatory and not any(
                a["asset_or_constellation"] == req.asset_or_constellation and self._role_covers(a["role"], req.role)
                for a in self.role_assignments.values()
            )
        ]

    # -- lifecycle -------------------------------------------------------------
    def start(self) -> None:
        self.started = True
        self._arm_schedule(self.sim.clock.now, initial=True)
        self.set_clock(True)   # auto-start real-time clock (matches "Start begins ticking" UX)

    def _arm_schedule(self, from_t: int, initial: bool = False) -> None:
        """(Re)queue bus ticks and scripted time-injects after ``from_t`` — also used after a
        rewind, since a rewind clears pending future events.

        IP-1061 (BL-0062, A1): the *initial* arm at ``start()`` uses ``at >= from_t`` so an inject
        scripted for exactly the start epoch (``at_sim_s: 0``) fires rather than being silently
        skipped by a strict ``>``. A *re-arm* after a rewind still guards with ``at > from_t`` for
        everything strictly in the future, but additionally re-arms an inject whose scheduled time
        equals ``from_t`` only if no retained event-log entry shows it already fired — a rewind
        keeps every entry with ``sim_time <= t`` (``engine/simulation.py``'s ``rewind_to()``), so an
        inject that already fired at exactly ``from_t`` is found there and is not re-queued
        (no double fire), while one that never fired (e.g. rewinding to the start epoch before the
        first ``advance_to``) is re-armed (not lost)."""
        self.bus.schedule_ticks(BUS_TICK_PERIOD_S, until=self.horizon, start=from_t)
        # IP-1062 (FR-4420) — only when the vignette actually declares a condition-triggered
        # inject, so the other 18 of 19 library vignettes gain zero extra eventlog entries.
        if any((inj.trigger or {}).get("type") == "condition" for inj in self.vignette.injects):
            step = int(BUS_TICK_PERIOD_S * 1_000_000)
            t = from_t + step
            while t <= self.horizon:
                self.sim.schedule(t, "condition_check")
                t += step
        fired_at_from_t: Optional[set[str]] = None
        if not initial:
            fired_at_from_t = {
                e.payload.get("inject_id") for e in self.sim.eventlog.entries
                if e.kind == "inject" and e.sim_time == from_t
            }
        for inj in self.vignette.injects:
            trig = inj.trigger or {}
            if trig.get("type") == "time" and "at_sim_s" in trig:
                at = self.ctx.start_epoch + int(float(trig["at_sim_s"]) * 1_000_000)
                if initial:
                    schedule = at >= from_t
                else:
                    schedule = at > from_t or (at == from_t and inj.id not in fired_at_from_t)
                if schedule:
                    self.sim.schedule(at, "inject", {"effects": inj.effects, "inject_id": inj.id})

    # -- time control ----------------------------------------------------------
    def step(self, dt_sim_s: float) -> None:
        self.advance_to(self.sim.clock.now + int(dt_sim_s * 1_000_000))

    def advance_to(self, t: int) -> None:
        self.sim.advance_to(t)
        self.world = self.sim.world
        # Re-anchor so a manual jump doesn't get instantly "undone" by a stale wall-clock anchor.
        if self._clock_running:
            self._wall_anchor = _time.time()
            self._sim_anchor = self.sim.clock.now

    # -- server-authoritative real-time clock (multiplayer) -------------------
    def set_clock(self, running: bool, rate: float = 1.0) -> None:
        """Arm or disarm the wall-clock anchor used by ``catch_up``.

        Pausing folds the elapsed real time into the sim first, so the clock freezes at the
        correct sim instant. Resuming starts a fresh anchor from the current sim time.
        """
        if running:
            self._wall_anchor = _time.time()
            self._sim_anchor = self.sim.clock.now
            self._rate = float(rate)
            self._clock_running = True
        else:
            self._catch_up_locked()
            self._clock_running = False
            self._wall_anchor = None
            self._sim_anchor = None

    def _catch_up_locked(self) -> None:
        """Advance the sim to the wall-derived target. No-op if not running or target<=now.

        Caller must already hold ``self._lock``. Safe because ``sim.advance_to`` raises only
        when target<current; the explicit guard against ``sim.clock.now`` makes a stale or
        equal wall reading a true no-op.

        Audit Jun 2026 §F2 — instrument the advance with a wall-cost sample so
        the watchdog can detect hardware-insufficient sessions.
        """
        if not self._clock_running or self._wall_anchor is None:
            return
        elapsed_before = _time.time() - self._wall_anchor
        target = self._sim_anchor + int(elapsed_before * self._rate * 1_000_000)
        if target > self.sim.clock.now:
            wall_before = _time.time()
            self.sim.advance_to(target)
            self.world = self.sim.world
            wall_cost = _time.time() - wall_before
            sim_advanced_s = (self.sim.clock.now - (target - int(elapsed_before * self._rate * 1_000_000) + self._sim_anchor + 0)) / 1e6
            # We measured wall_cost s of compute to advance the sim ahead.
            # If wall_cost >= ~0.5 * (catch-up interval), the next tick will
            # consistently fall further behind real time.
            self._record_catch_up_lag(wall_cost, target_us=target)

    def _record_catch_up_lag(self, wall_cost_s: float, target_us: int) -> None:
        """Audit Jun 2026 §F2 — clock-lag watchdog.

        Keeps a short ring of recent ``advance_to`` wall-cost samples. If the
        recent average exceeds a threshold (i.e. we're spending most of the
        polling window catching up), set a warning the UI will surface to
        White Cell so they know the scenario is too heavy for the hardware.
        """
        self._catch_up_lag_history.append(wall_cost_s)
        # Keep last 8 samples (~12 s of poll history at the default 1.5 s tick).
        if len(self._catch_up_lag_history) > 8:
            self._catch_up_lag_history.pop(0)
        if len(self._catch_up_lag_history) < 4:
            return
        avg = sum(self._catch_up_lag_history) / len(self._catch_up_lag_history)
        # Threshold: catch_up consistently >300 ms means we're using >20 % of a
        # 1.5 s poll just advancing — about to fall behind real time.
        if avg > 0.3:
            asset_count = len(self.world.assets) if self.world is not None else 0
            self._clock_lag_warning = {
                "severity": "high" if avg > 0.8 else "medium",
                "avg_wall_cost_s": round(avg, 3),
                "asset_count": asset_count,
                "message": (
                    f"Server clock lag — average catch_up wall cost {avg:.2f}s "
                    f"with {asset_count} assets. Hardware insufficient for this "
                    f"scenario; consider a smaller fleet, slower rate, or a "
                    f"more capable host."
                ),
            }
        else:
            self._clock_lag_warning = None

    def catch_up(self) -> None:
        with self._lock:
            self._catch_up_locked()

    def clock_state(self) -> dict:
        return {
            "running": self._clock_running,
            "rate": self._rate,
            "now": self.sim.clock.now,
            # Audit Jun 2026 §F2 — None when healthy, dict when lagging.
            "lag_warning": self._clock_lag_warning,
        }

    def rewind_to(self, t: int) -> None:
        self.sim.rewind_to(t)
        self._rebind()
        if self.started:
            self._arm_schedule(t)
        # Re-anchor at the rewound time so the wall clock can't snap the sim back to where it was.
        if self._clock_running:
            self._wall_anchor = _time.time()
            self._sim_anchor = self.sim.clock.now

    def undo_last(self, n: int = 1) -> None:
        self.sim.undo_last(n)
        self._rebind()
        if self._clock_running:
            self._wall_anchor = _time.time()
            self._sim_anchor = self.sim.clock.now

    def _rebind(self) -> None:
        # After a replay-based rewind the world object is fresh; repoint live references at it.
        self.world = self.sim.world
        self.osys.world = self.sim.world
        self.osys.orders.clear()           # queued events were dropped by the rewind
        # IP-1270 (FR-3430, Design Decision 2) — a pending-approval order still awaiting a
        # decision is discarded on rewind/undo, same as any other queued-not-yet-executed order.
        self.osys._pending.clear()
        self.osys._sensor_bookings.clear()
        self.osys._order_sensor.clear()
        self.osys._pass_bookings.clear()
        self.osys._order_pass.clear()
        # Rebuild sensor bookings from executed observe events still in the (truncated) eventlog.
        for entry in self.sim.eventlog.entries:
            if entry.kind == "execute_observe":
                sid = entry.payload.get("sensor_id")
                win_end = entry.payload.get("window_end")
                if sid and win_end:
                    self.osys._sensor_bookings.setdefault(sid, []).append((entry.sim_time, win_end))
        # SSN requests + bookings + in-flight counters are all gone with the rewind too.
        self.ssn.requests.clear()
        self.ssn._bookings.clear()
        for c in self.ssn._inflight:
            self.ssn._inflight[c] = 0
        self.ssn._counter = 0

    # -- intents ---------------------------------------------------------------
    def issue_order(self, cell: str, order: Order) -> OrderAck:
        order.cell = cell
        result = self.osys.issue(order)
        return self._order_ack(result)

    def validate_order(self, cell: str, order: Order) -> OrderAck:
        """Dry-run an order for the UI: would it be accepted, with which window/path, or why not?

        Read-only (no scheduling, no registry, no bookings) so the console can pre-disable buttons
        and preview the scheduled window without mutating the session (`docs/build-spec/07-operator-console.md` §16.9).
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
        return self._force_add_tle_object(asset_id, line1, line2, owner, kind)

    # IP-1190 (FR-5220) — the per-object body `add_tle` used to inline, extracted so the new
    # bulk-import path reuses the exact same construction/validation, unchanged, for its
    # single-object TLE case (Files to Modify's own "behavior-preserving refactor" instruction).
    def _force_add_tle_object(self, asset_id: str, line1: str, line2: str, owner: str, kind: str) -> tuple[bool, str]:
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

    # IP-1190 (FR-5220) — the CCSDS OMM sibling of `_force_add_tle_object`. OMM's Keplerian
    # mean-elements set maps onto the existing `OrbitState(source="kepler", ...)` shape exactly;
    # the one conversion needed (mean anomaly -> true anomaly at epoch) reuses the new
    # `engine/orbit.py::mean_to_true()`. Mirrors the TLE helper's error-handling shape: any
    # exception while building elements becomes a per-object failure string, never propagates.
    # Like `add_tle`, the elements are anchored at the session's own `ctx.start_epoch` rather
    # than the OMM's own `EPOCH` field — the same simplification `add_tle` already makes for a
    # TLE's own epoch, kept consistent rather than introducing a second epoch-handling
    # convention in the same package.
    def _force_add_omm_object(self, asset_id: str, elements: dict, owner: str, kind: str) -> tuple[bool, str]:
        required = ("a_m", "e", "i_deg", "raan_deg", "argp_deg", "mean_anomaly_deg")
        missing = [k for k in required if elements.get(k) is None]
        if missing:
            return False, f"invalid OMM element set: missing {', '.join(missing)}"
        try:
            from spacesim.engine.orbit import mean_to_true
            e = float(elements["e"])
            mean_anom_rad = math.radians(float(elements["mean_anomaly_deg"]))
            ta_deg = math.degrees(mean_to_true(mean_anom_rad, e))
            orbit = OrbitState(
                source="kepler",
                a_m=float(elements["a_m"]),
                e=e,
                i_deg=float(elements["i_deg"]),
                raan_deg=float(elements["raan_deg"]),
                argp_deg=float(elements["argp_deg"]),
                ta_deg=ta_deg,
                epoch=self.ctx.start_epoch,
            )
        except Exception as exc:  # malformed OMM elements are a normal rejection, not a crash
            return False, f"invalid OMM element set: {exc}"
        self.world.assets[asset_id] = Asset(id=asset_id, owner=owner, kind=kind, orbit=orbit)
        self.sim._initial_state = self.world.model_dump()
        return True, ""

    def bulk_import(self, file_format: Literal["tle", "omm"], content: str,
                     assignments: dict[str, dict]) -> list[dict]:
        """White-Cell force edit: import many objects from one multi-object TLE or CCSDS OMM
        (KVN) file in a single operation (IP-1190, FR-5220) — generalizes, does not replace,
        `add_tle`'s single-object path. A per-object entry present in the file but absent from
        `assignments` is reported as a per-object failure, never silently dropped. A file
        recognized as neither format raises `ValueError` before any object is processed (Design
        Decision 1) — the caller's problem, not a per-object report."""
        if self.started:
            return []
        from spacesim.content.bulk_import import parse_ccsds_omm, parse_multi_tle
        objects = parse_multi_tle(content) if file_format == "tle" else parse_ccsds_omm(content)
        reports: list[dict] = []
        for obj in objects:
            raw_id = obj["raw_id"]
            assignment = assignments.get(raw_id)
            if assignment is None:
                reports.append({"raw_id": raw_id, "asset_id": None, "ok": False,
                                 "reason": "no side/template assignment provided"})
                continue
            asset_id = assignment.get("asset_id", raw_id)
            owner = assignment.get("owner", "blue")
            kind = assignment.get("kind", "satellite")
            if obj["format"] == "tle":
                ok, reason = self._force_add_tle_object(asset_id, obj["line1"], obj["line2"], owner, kind)
            else:
                ok, reason = self._force_add_omm_object(asset_id, obj, owner, kind)
            reports.append({"raw_id": raw_id, "asset_id": asset_id, "ok": ok, "reason": reason})
        return reports

    def save_as_scenario(self, vignette_id: str, title: str,
                          classification: str = "UNCLASSIFIED-TRAINING") -> str:
        """IP-1200 (FR-5510) — save this session's current mid-exercise state (tracks, remaining
        resources, asset health, space weather) as a new vignette whose declared start is the
        save moment. Requires a started session (`SessionManager` has no "ended" lifecycle state
        — only `self.started` — so this is the only precondition there is to check); a draft
        (unstarted Creator) session already has its own dedicated save path (`save_vignette`
        below), unaffected by this method."""
        if not self.started:
            raise ValueError("cannot save-as-scenario: session has not been started")
        from spacesim.content.vignette_export import save_vignette
        return save_vignette(self.world, self.ctx, vignette_id, title,
                             classification=classification, start_epoch=self.sim.clock.now)

    # -- Vignette Creator UI surfaces (IP-1174) --------------------------------
    # One state, two views: every method below reads or mutates the same `self.world.assets`
    # dict the form UI and the JSON view both present — there is no second, cached
    # representation to fall out of sync with (FR-5120's own convergence requirement).

    def add_ground_asset(self, asset_id: str, lat_deg: float, lon_deg: float,
                         owner: str = "blue", kind: str = "ground_station") -> tuple[bool, str]:
        """White-Cell force edit: add a ground asset by lat/long (FR-5140's lat/long entry path,
        alongside `add_tle`'s orbital path). BL-0124 remediation: validates via `Asset` the same
        way `creator_set_state` does, so a malformed `owner`/`kind` or out-of-range lat/long
        rejects with `Ack(ok=False, ...)` instead of an unhandled 500."""
        if self.started:
            return False, "cannot edit force after start"
        from spacesim.engine.geometry import GeoPoint
        try:
            asset = Asset(id=asset_id, owner=owner, kind=kind,
                          location=GeoPoint(lat_deg=lat_deg, lon_deg=lon_deg))
        except Exception as exc:
            return False, f"invalid ground asset: {exc}"
        self.world.assets[asset_id] = asset
        self.sim._initial_state = self.world.model_dump()
        return True, ""

    def creator_state(self) -> dict:
        """FR-5120 — the JSON view's read: every asset, as the form UI would also see it."""
        return {"assets": [a.model_dump() for a in self.world.assets.values()]}

    def maneuver_ledger(self, cell: str, asset_id: str) -> Optional[list[dict]]:
        """IP-1250 (FR-1320) — a derived, read-only per-asset manoeuvre ledger: no new persisted
        state, purely a filtered read of the existing `EventLog`. Excludes an execute-time
        re-validation failure (`applied=False`) — no delta-v was actually spent, so it belongs in
        `world.effect_log`'s failure record, not this ledger. Fog-scoped like `get_telemetry`:
        ``None`` when the cell doesn't own the asset (White sees any asset)."""
        if not self._owns(cell, asset_id):
            return None
        return [
            {
                "t": e.sim_time,
                "cost": e.payload.get("cost", 0.0),
                "purpose_tag": e.payload.get("purpose_tag", ""),
                "remaining_delta_v_ms": e.payload.get("remaining_delta_v_ms"),
            }
            for e in self.sim.eventlog.entries
            if e.kind == "execute_maneuver" and e.payload.get("actor") == asset_id
               and e.payload.get("applied", True)
        ]

    def creator_set_state(self, assets: list[dict]) -> tuple[bool, str]:
        """FR-5120 — the JSON view's write: replace the whole asset list atomically. Validates
        every entry via `Asset` before committing any of them, so a malformed JSON edit can't
        half-apply."""
        if self.started:
            return False, "cannot edit force after start"
        try:
            validated = {a["id"]: Asset.model_validate(a) for a in assets}
        except Exception as exc:
            return False, f"invalid asset list: {exc}"
        self.world.assets = validated
        self.sim._initial_state = self.world.model_dump()
        return True, ""

    def creator_edit_asset(self, asset_id: str, patch: dict) -> tuple[bool, str]:
        """FR-5150 — edit an existing asset's fields in place (e.g. owner, kind, group)."""
        if self.started:
            return False, "cannot edit force after start"
        asset = self.world.assets.get(asset_id)
        if asset is None:
            return False, f"no such asset: {asset_id}"
        merged = {**asset.model_dump(), **patch, "id": asset_id}
        try:
            self.world.assets[asset_id] = Asset.model_validate(merged)
        except Exception as exc:
            return False, f"invalid edit: {exc}"
        self.sim._initial_state = self.world.model_dump()
        return True, ""

    def creator_delete_asset(self, asset_id: str) -> tuple[bool, str]:
        """FR-5150 — remove an asset from the draft/pre-start force."""
        if self.started:
            return False, "cannot edit force after start"
        if asset_id not in self.world.assets:
            return False, f"no such asset: {asset_id}"
        del self.world.assets[asset_id]
        self.sim._initial_state = self.world.model_dump()
        return True, ""

    def creator_scene(self) -> dict:
        """FR-5130 — ground-truth 2D/3D preview: every asset at its true position, with no
        `CellController` fog-of-war filtering. `session/scene.py`'s `build_scene(world, cell)`
        filters internally to assets owned by exactly `cell` (it's the per-cell belief renderer,
        not a ground-truth mode), and `Asset.owner` is one of {blue, red, neutral} — never
        "white" — so a single `build_scene(world, "white")` call would always return an empty
        scene. Ground truth is the union of every owner's own (unfiltered-for-itself) scene;
        this composes `build_scene()` unmodified once per owner and merges the results, still
        with no `CellController` import or call anywhere in this method."""
        merged_assets: list = []
        sun_lat = sun_lon = 0.0
        for owner in ("blue", "red", "neutral"):
            s = build_scene(self.world, owner)
            merged_assets.extend(s.assets)
            sun_lat, sun_lon = s.sun_lat_deg, s.sun_lon_deg
        return {"cell": "godview", "now": self.world.now, "sun_lat_deg": sun_lat,
                "sun_lon_deg": sun_lon, "assets": [a.model_dump() for a in merged_assets],
                # No cross-cell tracks/footprints exist in ground-truth mode (every asset is
                # already rendered directly, at its true position) — empty so the existing
                # drawMap()/Globe.render() consumers (which iterate scene.tracks unconditionally)
                # work unmodified against this scene shape too.
                "tracks": [], "footprints": []}

    def declare_seats(self, cell: str, count: int) -> list[str]:
        """FR-5160 — generate `count` seat identifiers for `cell` (e.g. `blue-1`..`blue-N`),
        replacing any previous declaration for that cell. The seat/role matrix UI then calls the
        existing `assign_role` once per checked cell — this only creates the seat ids to check
        against, reusing IP-1151's mechanism unmodified."""
        seats = [f"{cell}-{i}" for i in range(1, count + 1)]
        self.seats_declared[cell] = seats
        return seats

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
                        "window": o.earliest_window, "reason": o.fail_reason,
                        "issued_at": o.issued_at})
        return out

    def cancel_order(self, cell: str, order_id: str) -> bool:
        o = self.osys.orders.get(order_id)
        if o is None or (cell != "white" and o.cell != cell):
            return False
        return self.osys.cancel(order_id)

    def decide_gated_order(self, cell: str, order_id: str, approve: bool) -> tuple[bool, str]:
        """IP-1270 (FR-3430) — approve/deny a pending-approval order; only the gate's own
        required_role cell may decide."""
        return self.osys.decide_gated_order(cell, order_id, approve)

    def issue_roe_change(self, cell: str, target_cell: str, flag: str, value: bool) -> tuple[bool, str]:
        """IP-1270 (FR-3440) — a controller-issued, live, logged mid-session ROE-flag change."""
        return self.osys.issue_roe_change(cell, target_cell, flag, value)

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

    def next_contacts(self, cell: str) -> dict:
        """Per own-satellite time of the next command/telemetry contact — the fleet-rail countdown (§4.1).

        One fog-filtered call the UI can make per tick instead of N per-asset window queries; reuses
        the same AccessProvider path as ``windows_ahead`` so the value matches the pass timeline.
        """
        nxt: dict[str, Optional[int]] = {}
        for aid, a in self.sim.world.assets.items():
            if a.orbit is None or not self._owns(cell, aid):
                continue
            wa = self.windows_ahead(cell, aid)
            nxt[aid] = wa["windows"][0]["start"] if wa and wa["windows"] else None
        return {"now": self.sim.clock.now, "next": nxt}

    # -- safe-mode recovery (12-safe-mode-loop.md / §5.5 recovery strip) ------
    _RECOVERY_STEPS = ["establish_contact", "dump_telemetry", "clear_fault", "restore_loads",
                       "set_attitude", "enable_payload", "verify_nominal"]

    def recovery_status(self, cell: str, asset_id: str) -> Optional[dict]:
        """Safe-mode + recovery state for the UI recovery strip (fog: own assets only)."""
        if not self._owns(cell, asset_id):
            return None
        a = self.sim.world.assets.get(asset_id)
        if a is None or a.bus_state is None:
            return None
        sm = a.bus_state.safe_mode
        return {
            "asset": asset_id,
            "safe_mode": a.bus_state.mode == "safe_mode",
            "confirmed": sm.defender_confirmed,
            "diagnosis": sm.defender_diagnosis,
            "passes_used": sm.passes_used,
            "passes_needed": self.recovery.passes_needed(),
            "blocked_reason": sm.blocked_reason,
            "steps": list(self._RECOVERY_STEPS),
        }

    def begin_recovery(self, cell: str, asset_id: str, via: str = "") -> dict:
        """Schedule the multi-pass recovery chain for a safed own satellite over command windows.

        Auto-selects an uplink station (the caller's ``via`` is tried first, then any own station
        with a command window) so the UI need not guess which ground site has a pass.
        """
        if not self._owns(cell, asset_id):
            return {"ok": False, "reason": "not_owner"}
        a = self.sim.world.assets.get(asset_id)
        if a is None or a.bus_state is None or not a.bus_state.safe_mode.active:
            return {"ok": False, "reason": "not_safed"}
        owner = a.owner
        stations = ([via] if via else []) + [
            sid for sid, s in self.sim.world.assets.items()
            if s.owner == owner and s.location is not None and sid != via
        ]
        for station in stations:
            res = self.recovery.begin_recovery(asset_id, station)
            if res.get("ok"):
                return {**res, "via": station}
        return {"ok": False, "reason": "no_pass"}

    # -- SSN (mock Space Surveillance Network — docs/SSN-DESIGN.md) -----------
    def submit_ssn_request(self, cell: str, intent: str, target: str, regime: str,
                           priority: str = "priority"):
        """Submit a per-cell SSN request — returns the SSNAck (assigned sensor + collect/product times)."""
        req = SSNRequest(id="", cell=cell, intent=intent, target=target, regime=regime, priority=priority)
        return self.ssn.submit_request(cell, req)

    def list_ssn_requests(self, cell: str) -> list[dict]:
        return self.ssn.list_requests(cell)

    def cancel_ssn_request(self, cell: str, rid: str) -> bool:
        return self.ssn.cancel_request(cell, rid)

    def ssn_coverage(self, cell: str, regime: str) -> dict:
        return self.ssn.coverage(cell, regime)

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
            "classification": self.classification,
            "seed": self.sim._seed,
            "final_time": self.sim.clock.now,
            "started": self.started,
            "eventlog": self.sim.eventlog.model_dump(),
            "pending": [{"t": ev.t, "kind": ev.kind, "actor": ev.actor, "payload": ev.payload, "tag": ev.tag}
                        for ev in self.sim.scheduler.pending()],
            "orders": [vars(o) for o in self.osys.orders.values()],
            "ssn_requests": [vars(r) for r in self.ssn.requests.values()],
        }

    @classmethod
    def from_state(cls, state: dict) -> "SessionManager":
        from spacesim.content.vignette import load_vignette as _load
        from spacesim.engine.eventlog import EventLog
        mgr = cls(_load(state["vignette_id"]), overrides=state.get("overrides"), seed=state["seed"],
                  classification=state.get("classification"))
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
        # SSN requests: rebuild the registry, in-flight counters, and sensor bookings from saved state.
        for rd in state.get("ssn_requests", []):
            r = SSNRequest(**rd)
            mgr.ssn.requests[r.id] = r
            if r.state == "SCHEDULED":
                mgr.ssn._inflight[r.cell] = mgr.ssn._inflight.get(r.cell, 0) + 1
                if r.assigned_sensor and r.collect_at is not None and r.product_at is not None:
                    mgr.ssn._bookings.setdefault(r.assigned_sensor, []).append((r.collect_at, r.product_at))
        rnums = [int(r.id.split("-")[1]) for r in mgr.ssn.requests.values() if r.id.startswith("ssn-")]
        mgr.ssn._counter = max(rnums, default=0)
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

    def fire_inject(self, inject, at_sim_t: Optional[int] = None) -> None:
        """Fire an inject immediately, or schedule it for ``at_sim_t`` (microseconds, abs sim time).

        ``inject`` may be a list of effects, a dict with ``{"effects": [...]}``, or an id string
        resolved against the loaded vignette.  When ``at_sim_t`` is set and > current sim time,
        the inject is scheduled deterministically through the event log so it replays exactly.
        """
        effects = inject if isinstance(inject, list) else self._inject_effects(inject)
        now = self.sim.clock.now
        requested = int(at_sim_t) if at_sim_t is not None else now
        when = max(now, requested)   # past timestamps clamp to "now" (no backwards time travel)
        if when > now:
            # FW §11.D.19 — future-dated inject: schedule deterministically (replay-safe).
            self.sim.schedule(when, "inject", {"effects": effects})
            return
        self.sim.schedule(when, "inject", {"effects": effects})
        self.sim.advance_to(when)  # apply + log immediately (so it replays through the event log)
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
        self._apply_inject_effects(world, payload.get("effects", []), rng)

    def _apply_inject_effects(self, world: WorldState, effects: list, rng) -> None:
        """IP-1062 — shared per-effect dispatch, extracted from `_h_inject`'s previous inline
        body with no behavior change for any of the eight prior effect types, so both the
        time/immediate trigger path (`_h_inject`) and the new condition-triggered path
        (`_h_condition_check`) apply effects identically."""
        for eff in effects:
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
            elif kind == "gs_outage":
                # FUTURE-WORK §10.D.15: ground-station outage (cable cut, power loss, antenna damage).
                # The site is marked `health=degraded` so AccessProvider skips it for the inject window.
                # `restore` clears the outage; downstream effect: order validation rejects "no_window".
                asset = world.assets.get(eff["target"])
                if asset is not None and getattr(asset, "kind", "") == "ground_station":
                    asset.health = "degraded" if eff.get("restore") is not True else "nominal"
                    world.messages.append({"to": ["white", "blue", "red"],
                                           "text": f"{eff['target']}: outage {'cleared' if asset.health == 'nominal' else 'declared (' + eff.get('cause', 'unspecified') + ')'}",
                                           "t": world.now})
            elif kind == "space_weather":
                # FUTURE-WORK §10.C.11: storm severity scales eclipse drain in advance_bus and is
                # surfaced to telemetry signatures (FSW errors climb in 'severe').
                # severity ∈ {none, minor, severe}; "clear" is an alias for none; any other value
                # is coerced to "minor" rather than rejected, so a malformed inject cannot abort a
                # running exercise (IP-1061, BL-0064 — this merges what were two divergent
                # branches, the second of which validated but was unreachable).
                sev = str(eff.get("severity", "minor"))
                if sev == "clear":
                    sev = "none"
                if sev not in ("none", "minor", "severe"):
                    sev = "minor"
                world.space_weather = {"severity": sev}
                world.messages.append({"to": ["white", "blue", "red"],
                                       "text": f"Space weather: severity={sev}",
                                       "t": world.now})
            elif kind == "conjunction_warning":
                # FUTURE-WORK §2: pre-load a conjunction advisory so prop.collision_avoid
                # has something to react to. Effect carries {a, b, range_km, t_close}.
                world.conjunctions.append({"a": eff.get("a"), "b": eff.get("b"),
                                            "range_km": float(eff.get("range_km", 1.0)),
                                            "t_close": int(eff.get("t_close", world.now))})
                world.messages.append({"to": ["white", "blue"],
                                       "text": f"Conjunction warning: {eff.get('a')}↔{eff.get('b')} @ {eff.get('range_km', '?')} km",
                                       "t": world.now})
            elif kind == "spawn_debris":
                # FW §11.D.19 — inject-library debris event.  Records a new DebrisField
                # so downstream conjunction screening surfaces the elevated risk.  Region
                # is opaque to the engine; the UI / next conjunction tick consumes it.
                from spacesim.engine.effects import DebrisField, _persistence_estimate
                world.debris.append(DebrisField(
                    created_at=world.now,
                    source=str(eff.get("source", "inject")),
                    region={
                        "regime": eff.get("regime"),
                        "altitude_km": eff.get("altitude_km"),
                        "n_fragments": int(eff.get("n_fragments", 0)),
                    },
                    persistence_estimate=_persistence_estimate(eff.get("altitude_km")),
                ))
                if eff.get("message"):
                    world.messages.append({"to": ["white", "blue", "red"],
                                            "text": str(eff["message"]), "t": world.now})
            elif kind == "anomaly":
                # IP-1062 (FR-4430) — a controller-set spacecraft anomaly. Design Decision 4:
                # subsystem "bus" -> whole-bus safe mode (reuses the existing safe-mode/
                # RecoverySystem recovery loop); subsystem "telemetry" -> comms degraded (the
                # closest existing BusState field to "telemetry").
                # BL-0128 remediation: the "bus" branch previously set `bus_state.mode` directly,
                # leaving `safe_mode.active`/`cause`/`entered_at` unset — `begin_recovery` refused
                # with `not_safed` and the asset was operator-unrecoverable. Routed through
                # `engine/bus.py`'s `enter_safe_mode()`/`exit_safe_mode()` so the safe-mode state
                # is fully consistent and the existing RecoverySystem loop actually applies.
                asset = world.assets.get(eff["target"])
                if asset is not None and asset.bus_state is not None:
                    restore = eff.get("restore") is True
                    if eff.get("subsystem") == "bus":
                        if restore:
                            exit_safe_mode(asset.bus_state)
                        else:
                            cause = str(eff.get("cause", "anomaly"))
                            enter_safe_mode(asset.bus_state, world.now, cause)
                    elif eff.get("subsystem") == "telemetry":
                        asset.bus_state.comms.status = "green" if restore else "red"
                    world.messages.append({"to": ["white", "blue", "red"],
                                           "text": f"{eff['target']}: anomaly {'cleared' if restore else 'declared (' + str(eff.get('cause', 'unspecified')) + ')'}",
                                           "t": world.now})
            elif kind == "sensor_outage":
                # IP-1062 (FR-4430) — mirrors gs_outage's health-flag pattern for a sensor.
                sensor = world.sensors.get(eff["target"])
                if sensor is not None:
                    sensor.health = "nominal" if eff.get("restore") is True else "degraded"
                    world.messages.append({"to": ["white", "blue", "red"],
                                           "text": f"{eff['target']}: sensor outage {'cleared' if sensor.health == 'nominal' else 'declared (' + str(eff.get('cause', 'unspecified')) + ')'}",
                                           "t": world.now})
            elif kind == "forced_custody_loss":
                # IP-1062 (FR-4430) — a missing target is a no-op (Design Decision 2's posture),
                # never another cell's Track (world.track_for is already cell-scoped, ADR-0004).
                tr = world.track_for(eff["cell"], eff["target"])
                if tr is not None:
                    if eff.get("mode") == "drop":
                        world.tracks.remove(tr)
                    else:
                        tr.confidence = float(eff.get("degrade_to", 0.0))
                        tr.last_observation = world.now
            elif kind == "scripted_manoeuvre":
                # IP-1062 (FR-4430) — Design Decisions 1/3: resolves through the existing six
                # manoeuvre entry modes via compute_maneuver(), the same propagator call
                # OrderSystem._h_maneuver already uses, deliberately bypassing
                # asset.resources.delta_v_ms (injects are the documented plan-first bypass,
                # ADR-0005) — never checked, never deducted.
                asset = world.assets.get(eff["target"])
                if asset is not None and asset.orbit is not None:
                    from spacesim.engine.maneuver import compute_maneuver
                    result = compute_maneuver(asset.orbit, eff["mode"], eff.get("params", {}),
                                              world.now, self.osys.prop)
                    import numpy as _np
                    dv = _np.asarray(result["dv"], dtype=float)
                    asset.orbit = self.osys.prop.apply_impulse(asset.orbit, dv, world.now)
                    world.messages.append({"to": ["white"],
                                           "text": f"{eff['target']}: scripted manoeuvre ({eff['mode']}), "
                                                   f"cost={result['cost']:.1f} m/s",
                                           "t": world.now})

    def _condition_inject_already_fired(self, inj_id: str, before_t: int) -> bool:
        """IP-1062 (FR-4420) — derived from event-log history, no new WorldState field: mirrors
        `_arm_schedule`'s own time-filtered eventlog-scan pattern, safe under both live-run and
        replay since eventlog entries are strictly time-ordered immutable history."""
        for e in self.sim.eventlog.entries:
            if e.kind == "condition_check" and e.sim_time < before_t:
                if any(f.get("inject_id") == inj_id for f in e.payload.get("fired", [])):
                    return True
        return False

    def _h_condition_check(self, world: WorldState, payload: dict, rng) -> None:
        """IP-1062 (FR-4420) — evaluates every not-yet-fired condition-triggered inject against
        the current (replayed) WorldState. Mutates this event's own `payload` dict in place
        rather than calling `eventlog.append()` from inside the handler — `Simulation.advance_to`'s
        existing post-handler append captures this same dict, so the firing tick and evaluated
        condition are recorded with no additional/nested append (a mid-handler append would
        corrupt `_rebuild()`/`replay()`'s iteration over the entries list — see the package's
        own Risks)."""
        from spacesim.content.vignette import _evaluate_metric
        fired: list[dict] = []
        for inj in self.vignette.injects:
            trig = inj.trigger or {}
            if trig.get("type") != "condition":
                continue
            if self._condition_inject_already_fired(inj.id, world.now):
                continue
            # A condition targeting a deleted/expired asset/track/cell simply evaluates false
            # forever (Design Decision resolving BL-0095 part 1) — _evaluate_metric's own
            # existing None-handling already produces this, no new error-handling branch needed.
            if _evaluate_metric(world, self.ctx, trig.get("metric", {})):
                self._apply_inject_effects(world, inj.effects, rng)
                fired.append({"inject_id": inj.id, "value": True})
        payload["fired"] = fired
