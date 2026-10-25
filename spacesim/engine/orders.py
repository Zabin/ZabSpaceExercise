"""Orders — issue -> validate -> queue to the next window -> execute (``03-simulation-engine.md`` §4).

Players never act instantly: an order is validated (ownership, ROE/authorities, resources, and the
weapons-quality track gate for engagements), then queued for execution at the next valid access
window for its channel. Execution fires as a deterministic event in the simulation, so it is
captured in the event log and reproduced exactly on replay. **Cyber is the exception** — it is not
window-gated and resolves against a modeled access vector subject to the defender's posture, so it
can act outside any pass.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from spacesim.engine.access import (
    AccessConfig,
    AccessProvider,
    AccessWindow,
    Scene,
    COMMAND_UPLINK,
    ISL_LINK,
    JAM_FOOTPRINT,
    SENSOR_OBSERVATION,
    TELEMETRY_DOWNLINK,
    WEAPON_ENGAGEMENT,
)
from spacesim.engine.bus import downlink_storage
from spacesim.engine.buscommands import apply_command, can_issue
from spacesim.engine.custody import (
    Track,
    WEAPONS_QUALITY_THRESHOLD,
    confidence_at_decision,
    observe,
)
from spacesim.engine.effects import EffectInstance, ModerateEffectResolver, is_link_denied
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.world import WorldState

ACTION_CHANNEL = {
    "jam": JAM_FOOTPRINT,
    "engage": WEAPON_ENGAGEMENT,
    "observe": SENSOR_OBSERVATION,
    "maneuver": COMMAND_UPLINK,
    "command": COMMAND_UPLINK,   # bus/payload verbs (eps.*, adcs.*, satcom.*) — uplink/stored delivery
    "downlink": TELEMETRY_DOWNLINK,
    "cyber": None,  # not window-gated
}

# How many command/maneuver uplinks a single asset can accept in one access window.
# Reflects realistic uplink-command budget: ACK + parameter upload takes ~30–60 s each;
# a typical 5–10 min LEO pass fits 4–6 commands with margin. GEO passes are longer but
# the same ceiling keeps the exercise planning realistic.
MAX_COMMANDS_PER_PASS = 4

# IP-1041 Design Decision 2 (BL-0217) — the observe params `_exec_payload` converts with float().
OBSERVE_NUMERIC_PARAMS = ("look_angle_deg", "duration_s", "gain")


def _requested_beam_mode(params: dict) -> Optional[str]:
    """IP-1223 — the beam mode an observe order explicitly requests, or None for no request
    (absent, ``None``, empty, or ``auto``: the sensor's own mode applies)."""
    mode = params.get("beam_mode")
    if not isinstance(mode, str) or mode in ("", "auto"):
        return None
    return mode


def _observe_params_ok(params: dict) -> bool:
    """IP-1041 Design Decisions 2-3 — normalize and check an observe order's params in place.

    An explicit ``None`` for ``beam_mode`` or a numeric param is dropped, so it takes the same
    default as an absent key everywhere the params are read later. ``beam_mode`` must then be a
    string; each numeric param must be accepted by ``float()`` (as today, so numeric strings still
    work) and finite. Returns False on the first malformed value; never raises.
    """
    for key in ("beam_mode",) + OBSERVE_NUMERIC_PARAMS:
        if key in params and params[key] is None:
            del params[key]
    if "beam_mode" in params and not isinstance(params["beam_mode"], str):
        return False
    for key in OBSERVE_NUMERIC_PARAMS:
        if key in params:
            try:
                value = float(params[key])
            except (TypeError, ValueError):
                return False
            if not math.isfinite(value):
                return False
    return True


# IP-1052 Design Decision 1 (BL-0222, FR-3110/FR-1310/FR-1410/FR-1420) — the params every other
# action converts later (in `_validate`, `_plan_command`, `_exec_payload`, `_plan_cyber`), and the
# shape each must have. Checked in `_validate`, so `dry_run` and `issue` refuse alike, before any
# window search, booking, registry entry or scheduled event.
ORDER_PARAM_RULES: dict[str, dict[str, str]] = {
    "jam": {"power_w": "float", "bandwidth_hz": "float", "victim_bandwidth_hz": "float",
            "modulation": "str", "link_target": "str"},
    "engage": {"salvo_n": "int", "interceptor_class": "str"},
    "cyber": {"dwell_s": "float", "persistence_h": "float", "sm_susceptibility": "float",
              "persistence_bonus": "float", "vector": "str", "payload": "str", "segment": "str"},
    "maneuver": {"dv": "vec3", "stored_at": "int", "via": "str"},
    "command": {"verb": "str", "stored_at": "int", "via": "str"},
    "downlink": {"via": "str"},
}


def _finite_float_ok(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def _param_value_ok(kind: str, value) -> bool:
    if kind == "str":
        return isinstance(value, str)
    if kind == "float":
        return _finite_float_ok(value)
    if kind == "int":
        # Whatever `int()` accepts today (int, integral string, float — truncated as before);
        # NaN, inf and non-numeric strings raise and are refused.
        try:
            int(value)
        except (TypeError, ValueError, OverflowError):
            return False
        return True
    if kind == "vec3":
        return (isinstance(value, (list, tuple)) and len(value) == 3
                and all(_finite_float_ok(v) for v in value))
    raise ValueError(f"unknown param kind {kind!r}")


def _order_params_ok(action: str, params: dict) -> bool:
    """IP-1052 Design Decisions 1-2 — normalize and check an order's params in place, per action.

    ``observe`` keeps `IP-1041`'s own helper. For every other action, an explicit ``None`` for a
    param in ``ORDER_PARAM_RULES`` is dropped (so it takes the absent default everywhere it is read
    later), then each present param must have its declared shape. Returns False on the first
    malformed value; never raises.
    """
    if action == "observe":
        return _observe_params_ok(params)
    rules = ORDER_PARAM_RULES.get(action)
    if not rules:
        return True
    for key in rules:
        if key in params and params[key] is None:
            del params[key]
    return all(_param_value_ok(kind, params[key]) for key, kind in rules.items() if key in params)

def _engage_rounds(params: dict) -> int:
    """IP-1320 (FR-1460) — the rounds an ``engage`` consumes: its salvo, at least one.

    The single source for both the validation bound and the plan's ``consume`` entry, so the two
    cannot drift. Called only after ``_order_params_ok`` (which drops a ``None`` salvo and rejects
    a malformed one), so ``int`` cannot fail here.
    """
    return max(1, int(params.get("salvo_n", 1)))


# Realistic bar widths for the Gantt chart (in seconds).  "None" means use the full window.
BAR_DURATION_S: dict = {
    "command":  120,   # uplink + ACK
    "maneuver": 120,   # uplink + ACK
    "downlink": 360,   # 6-min data dump
    "jam":      None,  # continuous for the window
    "engage":   120,   # target acquisition + engagement
    "cyber":     60,   # instantaneous, shown as a 1-min marker
    "observe":  None,  # use duration_s param (default 300 s) — handled per-order
}


@dataclass
class Order:
    cell: str                 # issuing cell: blue|red
    actor: str                # asset or sensor id taking the action
    action: str               # jam|engage|observe|maneuver|cyber
    target: Optional[str] = None
    params: dict = field(default_factory=dict)
    issued_at: int = 0
    earliest_window: Optional[tuple[int, int]] = None
    delivery_path: Optional[str] = None  # ground_uplink | isl_relay | stored_program | sensor_collect
    status: str = "draft"     # draft|queued|rejected|cancelled|executed
    fail_reason: Optional[str] = None
    id: str = ""


def scene_from_world(world: WorldState) -> Scene:
    # Ground stations whose health is "degraded" (gs_outage inject) are excluded — no command
    # uplink / downlink path through them until the outage is cleared.
    return Scene(
        satellites={i: a.orbit for i, a in world.assets.items() if a.orbit is not None},
        sites={i: a.as_ground_site() for i, a in world.assets.items()
               if a.location is not None and a.health != "degraded"},
        # IP-1062 (FR-4430) — a sensor_outage'd sensor (health="degraded") loses its
        # sensor_observation access the same way a degraded ground station loses uplink/downlink.
        sensors={i: s for i, s in world.sensors.items() if s.health != "degraded"},
    )


class OrderSystem:
    def __init__(
        self,
        sim,
        roe: Optional[dict] = None,
        resolver: Optional[ModerateEffectResolver] = None,
        access_config: Optional[AccessConfig] = None,
        horizon_s: float = 24 * 3600,
        wq_threshold: float = WEAPONS_QUALITY_THRESHOLD,
        gating_rules: Optional[list[dict]] = None,
    ) -> None:
        self.sim = sim
        self.world: WorldState = sim.world
        self.roe = roe or {}
        # IP-1270 (FR-3440) — the immutable, vignette-declared baseline `_effective_roe` overlays
        # roe_change history onto; `self.roe` itself becomes a "current value" convenience cache
        # only (mutated by `_h_roe_change`), never the source of point-in-time truth.
        self._static_roe = {k: dict(v) for k, v in (roe or {}).items()}
        self.resolver = resolver or ModerateEffectResolver()
        self.prop = ModeratePropagator()
        self.access_config = access_config
        self.horizon = int(horizon_s * 1_000_000)
        self.wq_threshold = wq_threshold
        # FUTURE-WORK §7: SSN auto-cue. When set (by SessionManager), an organic observe that
        # yields a track below the characterization threshold automatically files an SSN
        # characterize request via the per-cell network. None disables auto-cueing.
        self.auto_cue_ssn = None       # set externally to an SSNSystem instance
        self._sensor_bookings: dict[str, list[tuple[int, int]]] = {}  # contention: one task at a time
        self._order_sensor: dict[str, tuple[str, int, int]] = {}     # order_id → (sensor_id, start, end)
        self._pass_bookings: dict[tuple[str, int], int] = {}         # (actor_id, win_start) → count
        self._order_pass: dict[str, tuple[str, int]] = {}            # order_id → pass key (for cancel)
        self.orders: dict[str, Order] = {}   # issued orders by id (for the queue + cancellation)
        self._order_counter = 0
        # IP-1270 (FR-3430) — vignette-declared {action_type?, reversibility_category?,
        # required_role} gating rules; order_id -> (Order, matched rule) for orders currently
        # held pending a decision. Discarded (not replayed) on rewind/undo, per Design Decision 2
        # — see session/manager.py::_rebind.
        self.gating_rules = gating_rules or []
        self._pending: dict[str, tuple[Order, dict]] = {}

        sim.register_handler("execute_effect", self._h_effect)
        sim.register_handler("execute_maneuver", self._h_maneuver)
        sim.register_handler("execute_observe", self._h_observe)
        sim.register_handler("execute_downlink", self._h_downlink)
        # IP-1270 (FR-3430/FR-3440) — audit-trail-only entries (no world mutation) plus the
        # live ROE-flag-change handler; all three must be registered so replay/rewind's generic
        # per-kind handler dispatch (`Simulation._rebuild`) never KeyErrors on them.
        sim.register_handler("effect_gate_request", self._h_noop)
        sim.register_handler("effect_gate_decision", self._h_noop)
        sim.register_handler("roe_change", self._h_roe_change)
        sim.register_handler("execute_command", self._h_command)

    # -- issue pipeline --------------------------------------------------------
    def issue(self, order: Order) -> Order:
        order.issued_at = self.sim.clock.now
        self._order_counter += 1
        order.id = f"ord-{self._order_counter}"
        # IP-1052 Design Decision 3 — registered only once planning returned, so an exception
        # raised while planning leaves no ghost entry behind (it still propagates).
        self._plan(order, commit=True)
        self.orders[order.id] = order
        return order

    def dry_run(self, order: Order) -> Order:
        """Validate + compute window/delivery path **without** scheduling, registering, or booking.

        Read-only mirror of ``issue`` for the UI's "why can't I?" pre-disabled buttons and window
        preview (`docs/build-spec/07-operator-console.md` §16.9). Touches no engine state — no RNG, no event log, no
        order registry, no sensor bookings — so it is replay-safe like ``scene``/``telemetry``.
        """
        order.issued_at = self.sim.clock.now
        self._plan(order, commit=False)
        return order

    def _plan(self, order: Order, commit: bool) -> None:
        """Shared planner: validate, choose window + delivery path, and (if ``commit``) schedule."""
        ok, reason = self._validate(order)
        if not ok:
            order.status, order.fail_reason = "rejected", reason
            return

        # IP-1270 (FR-3430) — a gated order is held pending a controller decision instead of
        # being scheduled; dry_run previews the pending state but logs nothing.
        gate = self._matching_gate(order)
        if gate is not None:
            order.status = "pending_approval"
            if commit:
                self._pending[order.id] = (order, gate)
                self.sim.eventlog.append(
                    sim_time=self.sim.clock.now, kind="effect_gate_request", actor=order.cell,
                    payload={"order_id": order.id, "required_role": gate.get("required_role"),
                             "action_type": order.action},
                )
            return

        self._continue_plan(order, commit)

    def _order_classification(self, order: Order) -> tuple[str, Optional[str]]:
        """IP-1270 Design Decision 1 — the shared effect-classification enumeration this
        package's own gating rules AND IP-1290's per-class detectability settings both consume:
        order action type crossed with the five-D's reversibility category, where determinable at
        issue time (an ``engage``'s intended outcome is always ``destroy`` — the one irreversible
        category; a ``jam``'s is always ``deny``; every other action's achieved outcome is not
        reliably known before execution, so its category is ``None`` — a rule may still match on
        ``action_type`` alone in that case)."""
        category = {"engage": "destroy", "jam": "deny"}.get(order.action)
        return order.action, category

    def _matching_gate(self, order: Order) -> Optional[dict]:
        action_type, category = self._order_classification(order)
        for rule in self.gating_rules:
            rt, rc = rule.get("action_type"), rule.get("reversibility_category")
            if rt is not None and rt != action_type:
                continue
            if rc is not None and rc != category:
                continue
            return rule
        return None

    def rebuild_pending(self) -> list[str]:
        """IP-1087 (FR-3430, FR-7220) — re-derive ``_pending`` after a resume from the restored
        order registry, the restored event log and the content's gating rules (no persisted
        copy). An order that cannot be rebuilt (no ``effect_gate_request`` entry, a decision
        already logged after it, or no gate rule matching) is rejected ``gate_lost_on_resume``
        and a warning naming it is returned. Pure: no clock, RNG or eventlog append."""
        warnings: list[str] = []
        for order in self.orders.values():
            if order.status != "pending_approval":
                continue
            req_idx = dec_idx = -1
            for i, e in enumerate(self.sim.eventlog.entries):
                if e.payload.get("order_id") != order.id:
                    continue
                if e.kind == "effect_gate_request":
                    req_idx = i
                elif e.kind == "effect_gate_decision":
                    dec_idx = i
            cause = ""
            gate = None
            if req_idx < 0:
                cause = "no gate request is recorded in the event log"
            elif dec_idx > req_idx:
                cause = "a gate decision is already recorded for it"
            else:
                gate = self._matching_gate(order)
                if gate is None:
                    cause = "no gating rule in the content matches it"
            if gate is None:
                order.status, order.fail_reason = "rejected", "gate_lost_on_resume"
                warnings.append(f"order {order.id} was awaiting an approval decision but its gate "
                                f"could not be reconstructed ({cause}); it was rejected")
            else:
                self._pending[order.id] = (order, gate)
        return warnings

    def decide_gated_order(self, cell: str, order_id: str, approve: bool) -> tuple[bool, str]:
        """IP-1270 (FR-3430) — only the gate's ``required_role`` cell may decide. Approving
        resumes normal planning (window/delivery-path selection + scheduling); denying rejects
        the order outright. Both the request and the decision (with elapsed time) are logged."""
        entry = self._pending.get(order_id)
        if entry is None:
            return False, "no_such_pending_order"
        order, gate = entry
        if cell != gate.get("required_role"):
            return False, "not_controller"
        requested_at = self.sim.clock.now
        for e in reversed(self.sim.eventlog.entries):
            if e.kind == "effect_gate_request" and e.payload.get("order_id") == order_id:
                requested_at = e.sim_time
                break
        now = self.sim.clock.now
        del self._pending[order_id]
        self.sim.eventlog.append(
            sim_time=now, kind="effect_gate_decision", actor=cell,
            payload={"order_id": order_id, "approved": bool(approve),
                     "elapsed_us": now - requested_at},
        )
        if approve:
            self._continue_plan(order, commit=True)
        else:
            order.status, order.fail_reason = "rejected", "gate_denied"
        return True, ""

    def _h_noop(self, world: WorldState, payload: dict, rng) -> None:
        """IP-1270 — audit-trail-only eventlog entries (effect_gate_request/decision) carry no
        world mutation; registered purely so replay/rewind's generic per-kind dispatch doesn't
        KeyError on them."""
        return

    def _effective_roe(self, cell: str, at_time: int) -> dict:
        """IP-1270 (FR-3440) — the vignette-declared static ROE for ``cell``, overlaid with every
        ``roe_change`` eventlog entry for ``cell`` at or before ``at_time``, in chronological
        order (eventlog entries are always time-ordered, live or replayed). A pure derivation —
        no separate mutable ROE-history state exists that could drift from it."""
        roe = dict(self._static_roe.get(cell, {}))
        for e in self.sim.eventlog.entries:
            if e.kind == "roe_change" and e.payload.get("cell") == cell and e.sim_time <= at_time:
                roe[e.payload["flag"]] = e.payload["value"]
        return roe

    def _h_roe_change(self, world: WorldState, payload: dict, rng) -> None:
        """Updates the convenience 'current value' cache (`self.roe`); time-varying evaluation
        always re-derives via `_effective_roe`, so this mutation is not itself load-bearing for
        correctness, only for any caller that reads `self.roe` directly for the current value."""
        self.roe.setdefault(payload["cell"], {})[payload["flag"]] = payload["value"]

    def issue_roe_change(self, cell: str, target_cell: str, flag: str, value: bool) -> tuple[bool, str]:
        """IP-1270 (FR-3440) — a controller-issued, logged, mid-session ROE-flag change, effective
        from its simulated time. Only the designated controller role (``"white"``) may issue one."""
        if cell != "white":
            return False, "not_controller"
        if flag not in ("kinetic_authorized", "cyber_authorized"):
            return False, "unknown_flag"
        now = self.sim.clock.now
        payload = {"cell": target_cell, "flag": flag, "value": bool(value)}
        self._h_roe_change(self.world, payload, self.sim.rng)
        self.sim.eventlog.append(sim_time=now, kind="roe_change", actor=cell, payload=payload)
        return True, ""

    def _continue_plan(self, order: Order, commit: bool) -> None:
        """The pre-IP-1270 body of `_plan`, resumed after an order clears any gating check
        (immediately, if unmatched; on approval, if matched)."""
        channel = ACTION_CHANNEL[order.action]
        if channel is None:
            self._plan_cyber(order, commit)
            return
        if order.action == "observe":
            self._plan_collection(order, commit)
            return
        if order.action in ("maneuver", "command"):
            self._plan_command(order, commit)
            return

        win = self._next_window(order, channel)
        if win is None:
            order.status, order.fail_reason = "rejected", "no_window"
            return
        # IP-1052 Design Decision 3 — build the payload before any write, so a failure leaves the
        # order un-queued and nothing scheduled.
        if commit:
            kind, data = self._exec_payload(order, win)
            data["__order_id"] = order.id  # threaded through so handlers can release bookings
        order.earliest_window = (win.start, win.end)
        order.delivery_path = "ground_uplink"  # jam/engage/downlink gate on a single access window
        order.status = "queued"
        if commit:
            self.sim.schedule(win.start, kind, data, actor=order.cell, tag=order.id)

    def _release_bookings_on_execute(self, order_id: Optional[str]) -> None:
        """Pop pass / sensor booking entries for an order that just executed.

        Symmetric with cancel() so the booking dicts don't grow without bound
        across a long-running session. Safe to call with a missing/unknown id.
        """
        if not order_id:
            return
        pass_key = self._order_pass.pop(order_id, None)
        if pass_key:
            count = max(0, self._pass_bookings.get(pass_key, 1) - 1)
            if count == 0:
                self._pass_bookings.pop(pass_key, None)
            else:
                self._pass_bookings[pass_key] = count
        sensor_booking = self._order_sensor.pop(order_id, None)
        if sensor_booking:
            sensor_id, start, end = sensor_booking
            bookings = self._sensor_bookings.get(sensor_id, [])
            try:
                bookings.remove((start, end))
            except ValueError:
                pass

    def cancel(self, order_id: str) -> bool:
        """Cancel a still-queued order; the scheduled event is skipped (never logged → replay-safe)."""
        o = self.orders.get(order_id)
        if o is None or o.status != "queued":
            return False
        self.sim.cancel(order_id)
        o.status = "cancelled"
        # Release the sensor slot so it can be rebooked immediately.
        booking = self._order_sensor.pop(order_id, None)
        if booking:
            sensor_id, start, end = booking
            bookings = self._sensor_bookings.get(sensor_id, [])
            try:
                bookings.remove((start, end))
            except ValueError:
                pass
        # Release the per-pass command slot.
        pass_key = self._order_pass.pop(order_id, None)
        if pass_key:
            self._pass_bookings[pass_key] = max(0, self._pass_bookings.get(pass_key, 1) - 1)
        return True

    def _ap(self) -> AccessProvider:
        return AccessProvider(scene_from_world(self.world), propagator=self.prop, config=self.access_config)

    def _plan_command(self, order: Order, commit: bool) -> None:
        """Plan a satellite command across the three delivery paths, choosing the earliest."""
        now = self.sim.clock.now
        ap = self._ap()
        choices: list[tuple[str, AccessWindow]] = []

        stored_at = order.params.get("stored_at")
        if stored_at is not None and self.world.assets[order.actor].stored_program:
            t = int(stored_at)
            choices.append(("stored_program", AccessWindow(channel="stored", actor=order.actor,
                                                           target=order.actor, start=t, end=t, quality=1.0)))

        via = order.params.get("via")
        gs_windows_exist = False
        if via is not None:
            gs_wins = ap.windows(via, order.actor, COMMAND_UPLINK, now, now + self.horizon)
            gs_windows_exist = bool(gs_wins)
            for w in gs_wins:
                if self._pass_bookings.get((order.actor, w.start), 0) < MAX_COMMANDS_PER_PASS:
                    choices.append(("ground_uplink", w))
                    break

        isl = self._best_isl_window(ap, order.cell, order.actor, now)
        if isl is not None:
            choices.append(("isl_relay", isl))

        if not choices:
            # Distinguish "windows exist but all full" from "no window at all".
            reason = "pass_capacity_full" if gs_windows_exist else "no_window"
            order.status, order.fail_reason = "rejected", reason
            return
        path, win = min(choices, key=lambda pw: pw[1].start)
        # IP-1052 Design Decision 3 — payload first, then status, booking and schedule.
        if commit:
            kind, data = self._exec_payload(order, win)
            data["__order_id"] = order.id
        order.delivery_path = path
        order.earliest_window = (win.start, win.end)
        order.status = "queued"
        if commit:
            if path != "stored_program":
                key = (order.actor, win.start)
                self._pass_bookings[key] = self._pass_bookings.get(key, 0) + 1
                self._order_pass[order.id] = key
            self.sim.schedule(win.start, kind, data, actor=order.cell, tag=order.id)

    def _best_isl_window(self, ap: AccessProvider, cell: str, actor: str, now: int) -> Optional[AccessWindow]:
        best: Optional[AccessWindow] = None
        for rid, relay in self.world.assets.items():
            if rid == actor or relay.owner != cell or not relay.isl_capable or relay.orbit is None:
                continue
            for w in ap.windows(rid, actor, ISL_LINK, now, now + self.horizon):
                if self._pass_bookings.get((actor, w.start), 0) < MAX_COMMANDS_PER_PASS:
                    if best is None or w.start < best.start:
                        best = w
                    break
        return best

    def _plan_collection(self, order: Order, commit: bool) -> None:
        """Sensor tasking: pick a sensor (or 'auto'), respect contention, queue at the window."""
        now = self.sim.clock.now
        ap = self._ap()
        sensor_ids = self._candidate_sensors(order)
        if not sensor_ids and self._auto_blocked_by_cue(order):
            order.status = "rejected"
            order.fail_reason = "requires_cue"
            return
        chosen: Optional[tuple[str, AccessWindow]] = None
        windows_found = False
        for sid in sensor_ids:
            wins = ap.windows(sid, order.target or "", SENSOR_OBSERVATION, now, now + self.horizon)
            windows_found = windows_found or bool(wins)
            for w in wins:
                if not self._contended(sid, w.start, w.end):
                    chosen = (sid, w)
                    break
            if chosen:
                break
        if chosen is None:
            order.status = "rejected"
            # IP-1041 Design Decision 1 (BL-0219, FR-3210) — "contended" only when a window was
            # found and every one found was booked; no window at all is `no_window`, the same rule
            # `_plan_command` uses for `pass_capacity_full` vs `no_window`.
            order.fail_reason = "sensor_contended" if windows_found else "no_window"
            return
        sid, win = chosen
        order.actor = sid   # read by _exec_payload, so assigned before it
        # IP-1052 Design Decision 3 — payload first, then status, booking and schedule.
        if commit:
            kind, data = self._exec_payload(order, win)
            data["sensor_id"] = sid          # persisted in eventlog for booking reconstruction
            data["window_end"] = win.end     # on rewind/replay
            data["__order_id"] = order.id
        order.delivery_path = "sensor_collect"
        order.earliest_window = (win.start, win.end)
        order.status = "queued"
        if commit:
            self._sensor_bookings.setdefault(sid, []).append((win.start, win.end))
            self._order_sensor[order.id] = (sid, win.start, win.end)
            self.sim.schedule(win.start, kind, data, actor=order.cell, tag=order.id)

    def _candidate_sensors(self, order: Order) -> list[str]:
        if order.actor and order.actor != "auto":
            # IP-1220 (FR-1660) — an observe order may name either the sensor's own id or its
            # host_asset_id; resolve the latter to the actual sensor id so both identifiers
            # produce an identical result.
            return [self._resolve_sensor_id(order.actor) or order.actor]
        # IP-1222 Design Decision 4 (BL-0213, FR-1640) — auto-selection never picks a
        # cue-dependent sensor against a target the cell holds no Track on.
        untracked = self.world.track_for(order.cell, order.target) is None
        # IP-1223 Design Decision 3 (FS-122 v1.2) — a requested beam mode narrows auto-selection
        # to the sensors whose modality offers it.
        mode = _requested_beam_mode(order.params)
        return [sid for sid, s in self.world.sensors.items()
                if s.owner == order.cell and not (s.requires_cue and untracked)
                and (mode is None or mode in self._observe_modes(sid))]

    def _observe_payload_type(self, sid: str) -> str:
        """IP-1223 Design Decision 1 — the beam-mode table an observe by ``sid`` is scored on when
        it names no radar mode: the dual-registered asset's payload type, else the sensor-kind
        lighting heuristic, else EO (unchanged from the observe branch of ``_exec_payload``)."""
        asset = self.world.assets.get(sid)
        sensor = self.world.sensors.get(sid)
        if asset and asset.payload_state:
            return asset.payload_state.type
        if sensor:
            return "isr_eo" if sensor.needs_lighting else "isr_sar"
        return "isr_eo"

    def _observe_modes(self, sid: str) -> list[str]:
        """IP-1223 Design Decision 1 (FS-122 v1.2, FR-1610) — the beam modes the executing
        sensor's modality offers: a ground radar offers its own ``fence``/``dish``; any other
        sensor offers its payload type's table."""
        from spacesim.engine.isr import BEAM_MODES, available_modes
        sensor = self.world.sensors.get(sid)
        if sensor is not None and sensor.kind == "ground_radar":
            return list(BEAM_MODES["ground_radar"])
        return available_modes(self._observe_payload_type(sid))

    def _auto_blocked_by_cue(self, order: Order) -> bool:
        """IP-1222 Design Decision 4 — True when an ``auto`` observe has no candidate only because
        every owned sensor is cue-dependent and the cell holds no Track on the target."""
        if order.actor and order.actor != "auto":
            return False
        owned = [s for s in self.world.sensors.values() if s.owner == order.cell]
        return (bool(owned) and all(s.requires_cue for s in owned)
                and self.world.track_for(order.cell, order.target) is None)

    def _contended(self, sid: str, start: int, end: int) -> bool:
        return any(not (end <= b0 or start >= b1) for (b0, b1) in self._sensor_bookings.get(sid, []))

    def _resolve_sensor_id(self, actor: str) -> Optional[str]:
        """IP-1220 (FR-1660) — resolve either a sensor's own id or its host_asset_id to the
        actual sensor id, so an observe order naming either identifier is treated identically."""
        if actor in self.world.sensors:
            return actor
        for sid, s in self.world.sensors.items():
            if s.host_asset_id == actor:
                return sid
        return None

    # -- validation ------------------------------------------------------------
    def _validate(self, order: Order) -> tuple[bool, str]:
        if order.action not in ACTION_CHANNEL:
            return False, "unknown_action"

        # IP-1041 Design Decision 2 (BL-0217, observe) / IP-1052 Design Decision 1 (BL-0222, every
        # other action) — before any other check, window search or booking, so `dry_run` and
        # `issue` agree and nothing leaks.
        if not _order_params_ok(order.action, order.params):
            return False, "invalid_param"

        if order.action == "observe":
            mode = _requested_beam_mode(order.params)
            if order.actor == "auto":
                # IP-1223 Design Decision 3 — a mode no own sensor offers is an illegal parameter.
                if mode is not None and not any(
                        mode in self._observe_modes(sid)
                        for sid, s in self.world.sensors.items() if s.owner == order.cell):
                    return False, "invalid_param"
                return True, ""  # sensor chosen at planning time
            sid = self._resolve_sensor_id(order.actor)
            sensor = self.world.sensors.get(sid) if sid else None
            if sensor is None:
                return False, "no_such_sensor"
            if sensor.owner != order.cell:
                return False, "not_owner"
            # IP-1223 Design Decision 2 (FS-122 v1.2) — a mode the executing sensor's modality
            # does not offer is refused, never scored on another modality's table.
            if mode is not None and mode not in self._observe_modes(sid):
                return False, "invalid_param"
            # IP-1220 (FR-1640) — a cue-dependent sensor may only be tasked against a target the
            # cell already holds a Track on.
            if sensor.requires_cue and self.world.track_for(order.cell, order.target) is None:
                return False, "requires_cue"
            return True, ""

        actor = self.world.assets.get(order.actor)
        if actor is None:
            return False, "no_such_asset"
        if actor.owner != order.cell:
            return False, "not_owner"

        if order.action == "engage":
            # IP-1172 (FR-3420) — resolved per issuing cell; self.roe is always cell-keyed
            # ({"blue": {...}, "red": {...}}) by the time it reaches OrderSystem — the
            # legacy-vs-explicit-shape distinction is resolved upstream in
            # content/vignette.py's build_world(), never here.
            # IP-1270 (FR-3440) — evaluated as of the order's own issue time, so a live ROE
            # change affects orders issued after it, never ones already issued before it.
            if not self._effective_roe(order.cell, order.issued_at).get("kinetic_authorized", False):
                return False, "roe_kinetic_not_authorized"
            if actor.resources.ammo < 1:
                return False, "no_ammo"
            # IP-1320 (FR-1460) — the salvo may not exceed the rounds left (preview == issue).
            if _engage_rounds(order.params) > actor.resources.ammo:
                return False, "insufficient_ammo"
            track = self.world.track_for(order.cell, order.target or "")
            if track is None or not track.is_weapons_quality(self.sim.clock.now, self.wq_threshold):
                return False, "no_weapons_quality_track"

        if order.action == "cyber":
            if not self._effective_roe(order.cell, order.issued_at).get("cyber_authorized", False):
                return False, "roe_cyber_not_authorized"
            # Audit 2026-06 Commands §C2 — `vector` is mandatory. The legacy raw
            # base_prob fallback path is removed; cyber Pₛ now always derives from
            # vector × posture × dwell.
            if not order.params.get("vector"):
                return False, "no_cyber_vector"

        if order.action == "maneuver":
            dv = np.asarray(order.params.get("dv", [0, 0, 0]), dtype=float)
            if float(np.linalg.norm(dv)) > actor.resources.delta_v_ms + 1e-9:
                return False, "insufficient_delta_v"
            if "via" not in order.params and "stored_at" not in order.params:
                return False, "no_command_station"

        if order.action == "command":
            ok, reason = can_issue(self.world, order.actor, order.params.get("verb", ""))
            if not ok:
                return False, reason
            if "via" not in order.params and "stored_at" not in order.params:
                return False, "no_command_station"

        if order.action == "downlink" and "via" not in order.params:
            return False, "no_downlink_station"

        return True, ""

    # -- windowing -------------------------------------------------------------
    def _window_endpoints(self, order: Order) -> tuple[str, str]:
        if order.action in ("maneuver", "downlink"):
            return order.params["via"], order.actor   # uplink/downlink: station <-> satellite
        return order.actor, order.target or ""

    def _next_window(self, order: Order, channel: str) -> Optional[AccessWindow]:
        ap = AccessProvider(scene_from_world(self.world), propagator=self.prop, config=self.access_config)
        a, t = self._window_endpoints(order)
        now = self.sim.clock.now
        wins = ap.windows(a, t, channel, now, now + self.horizon)
        return wins[0] if wins else None

    # -- execution payloads ----------------------------------------------------
    def _observation_phase_angle_deg(self, sensor, target_id: Optional[str], t: int) -> Optional[float]:
        """IP-1221 (FR-1670, Design Decision 2) — the Sun-target-sensor phase angle at ``t`` from
        true positions, via the one shared ``engine/sun.py::cats_phase_angle_deg`` (BL-0152).
        Observer = ground site (ground sensor), host Asset's orbit (hosted, FR-1660 rule), else the
        sensor's own orbit. ``None`` (→ gain unaffected) for any geometry that can't be evaluated;
        never raises. Pure: reads the world, mutates nothing, draws no RNG."""
        from spacesim.engine.geometry import ecef_to_eci, geodetic_to_ecef
        from spacesim.engine.sun import cats_phase_angle_deg

        target = self.world.assets.get(target_id) if target_id else None
        if target is None or target.orbit is None:
            return None
        r_target, _ = self.prop.rv(target.orbit, t)
        if sensor.kind == "space_based":
            host = self.world.assets.get(sensor.host_asset_id) if sensor.host_asset_id else None
            obs_orbit = host.orbit if (host is not None and host.orbit is not None) else sensor.orbit
            if obs_orbit is None:
                return None
            r_obs, _ = self.prop.rv(obs_orbit, t)
        else:
            if sensor.location is None:
                return None
            r_obs = ecef_to_eci(geodetic_to_ecef(sensor.location), t)
        try:
            return cats_phase_angle_deg(r_target, r_obs, t)
        except ValueError:
            return None

    @staticmethod
    def _delivery_keys(win: AccessWindow) -> dict:
        """IP-1085 (FR-1440) — the delivery path planning chose, from the planned window's channel.

        Carried in the execution payload so the execute-time jam test is a pure function of the
        logged payload (replay-exact); ``relay`` names the crosslink relay for ``isl_relay`` only.
        """
        path = {"stored": "stored_program", "isl_link": "isl_relay"}.get(win.channel, "ground_uplink")
        return {"delivery_path": path, "relay": win.actor if path == "isl_relay" else None}

    @staticmethod
    def _delivery_jammed(world: WorldState, payload: dict) -> Optional[str]:
        """IP-1085 (FR-1440) — the jammed link on this payload's delivery path at ``world.now``, else None.

        ``stored_program`` runs onboard (no link); ``isl_relay`` needs the crosslink on the actor and
        on the relay; ``ground_uplink`` needs the uplink on the actor. A payload recorded before this
        package has no ``delivery_path`` and keeps the old rule (an uplink jam on the actor).
        """
        path = payload.get("delivery_path") or "ground_uplink"
        actor, now = payload["actor"], world.now
        if path == "stored_program":
            return None
        if path == "isl_relay":
            ends = [actor] + ([payload["relay"]] if payload.get("relay") else [])
            return "crosslink" if any(is_link_denied(world, e, now, link="crosslink") for e in ends) else None
        return "uplink" if is_link_denied(world, actor, now, link="uplink") else None

    @staticmethod
    def _jammed_record(world: WorldState, template, payload: dict, link: str) -> dict:
        """The ``effect_log`` failure record for a jam-denied command. The additive ``path`` key
        (path and jammed link) is written only for a payload that carries ``delivery_path``, so an
        event recorded before IP-1085 replays to the byte-identical record it always produced."""
        rec = {"t": world.now, "template": template, "target": payload["actor"],
               "achieved": "jammed", "success": False}
        if payload.get("delivery_path"):
            rec["path"] = f"{payload['delivery_path']}:{link}"
        return rec

    def _exec_payload(self, order: Order, win: AccessWindow) -> tuple[str, dict]:
        p = order.params
        # IP-2010 v1.1 (BL-0002) — capture the issuing cell's live track confidence for
        # order.target at the sim-time the operator actually clicked Issue (order.issued_at),
        # not the later window-open execution time. This is the same number scene.py's
        # RenderTrack.confidence already displays to the operator; recorded here, once, into
        # every DECISION_KINDS event's payload so session/assessment.py's belief-truth-divergence
        # scorer can read it back verbatim instead of recomputing it via replay. None when the
        # order has no target or the cell holds no track on it.
        custody_confidence = confidence_at_decision(
            self.world.tracks, order.cell, order.target, order.issued_at,
        )
        if order.action == "jam":
            # Audit 2026-06 Commands §C2 — Pₛ is fully derived from physical inputs
            # (modulation × power × bandwidth coverage). The operator no longer types
            # success_prob; the resolver then applies defender modifiers (frequency_hop,
            # interference_mitigation — Phase A §C1). A legacy `success_prob` in params
            # is parsed for save-file back-compat but ignored.
            from spacesim.engine.jam import (
                effective_success_prob as _jam_prob,
                modulation_params as _jam_mod,
            )
            modulation = p.get("modulation")
            power_w = float(p.get("power_w", 100.0))
            bandwidth_hz = float(p.get("bandwidth_hz", 1e6))
            link_target = p.get("link_target", "downlink")
            if link_target not in ("uplink", "downlink", "crosslink"):
                link_target = "downlink"
            victim_bw_hz = float(p.get("victim_bandwidth_hz", 1e6))
            # Base Pₛ from a power-scaled curve; doubling power above the 100 W reference
            # asymptotes to a near-certain raw threshold (defender state knocks it down).
            base_prob = min(0.98, 0.6 + 0.3 * math.sqrt(max(0.0, power_w) / 100.0))
            adj_prob = _jam_prob(base_prob, modulation, bandwidth_hz, victim_bw_hz)
            mod_params, resolved_mod = _jam_mod(modulation)
            # Deceptive jamming is overt-once-detected; all other modulations carry the
            # modulation's default attribution_bias. Operators do not override.
            attribution = mod_params["attribution_bias"]
            effect = EffectInstance(
                template="ew_jam",
                category="electronic_warfare",
                segment="link",
                actor=order.actor,
                target=order.target or "",
                reversible=True,
                attribution=attribution,
                escalation_weight=3,
                requires=JAM_FOOTPRINT,
                intended_outcome="deny",
                success_prob=adj_prob,
                window_start=win.start,
                window_end=win.end,
                link_target=link_target,
                order_action_type=order.action,
            )
            return "execute_effect", {
                "effect": effect.model_dump(),
                # IP-1320 (FR-1470, ADR-0037) — a jammer's power_w is a rating, not a
                # consumable: a jam consumes nothing from it.
                "custody_confidence_at_decision": custody_confidence,
            }

        if order.action == "engage":
            # Audit 2026-06 Commands §M2 — Pₖ from INTERCEPTORS database (4 classes
            # sourced from the four open-source DA-ASAT test records). The operator
            # picks an interceptor_class enum and a salvo size; the engine derives
            # Pₖ from the class × target altitude × salvo. Defender evasion (Phase A
            # §C1) cuts Pₖ in the resolver.
            from spacesim.engine.engage import kill_probability_from_class
            salvo_n = int(p.get("salvo_n", 1))
            interceptor_class = p.get("interceptor_class") or "mrbm_kkv"
            # Target altitude derived from the world, not operator input.
            tgt_asset = self.world.assets.get(order.target or "")
            tgt_alt_km = 500.0  # default mid-LEO if unknown (won't pass weapons-quality
                                # gate without a real target anyway)
            if tgt_asset is not None and tgt_asset.orbit is not None:
                # Periapsis altitude as a conservative reach test.
                from spacesim.engine.orbit import classify_regime
                tgt_alt_km = max(0.0, (tgt_asset.orbit.a_m - 6_378_137.0) / 1000.0)
            adj_pk = kill_probability_from_class(
                interceptor_class, target_alt_km=tgt_alt_km, salvo_n=salvo_n,
            )
            effect = EffectInstance(
                template=f"da_asat_{interceptor_class}",
                category="direct_ascent" if interceptor_class != "coorbital" else "co_orbital",
                segment="orbital",
                actor=order.actor,
                target=order.target or "",
                reversible=False,
                kinetic=True,
                debris_risk="high",
                attribution="overt",
                escalation_weight=8,
                requires=WEAPON_ENGAGEMENT,
                intended_outcome="destroy",
                success_prob=adj_pk,
                window_start=win.start,
                window_end=win.end,
                order_action_type=order.action,
            )
            return "execute_effect", {
                "effect": effect.model_dump(),
                "consume": {"actor": order.actor, "ammo": _engage_rounds(p)},
                "custody_confidence_at_decision": custody_confidence,
            }

        if order.action == "observe":
            intent = p.get("intent", "track")
            # Audit 2026-06 Commands §C3 — `characterizes` is now derived from the
            # operator's `intent`; the explicit override is removed (it let the operator
            # mark the target characterized without actually running a characterize pass).
            characterizes = (intent == "characterize")

            # ISR beam-mode parameters: beam_mode, look_angle, duration, start_offset
            beam_mode_req = p.get("beam_mode")
            look_angle_deg = float(p.get("look_angle_deg", 0.0))
            duration_s = float(p.get("duration_s", 300.0))

            # Resolve actor: assets (satellites) and sensors share the same order channel.
            # Space-based ISR sats are often dual-registered: an Asset for bus/power, a Sensor
            # for the observe access window.  We check assets first for payload type + orbit,
            # and fall back to the sensor's orbit if no asset match exists.
            actor_asset = self.world.assets.get(order.actor)
            actor_sensor = self.world.sensors.get(order.actor)
            actor_orbit = ((actor_asset.orbit if actor_asset else None)
                           or (actor_sensor.orbit if actor_sensor else None))
            # Derive payload type: asset payload_state → sensor kind heuristic → default EO
            # (IP-1223 — the same helper validation uses, so the two cannot disagree).
            payload_type = self._observe_payload_type(order.actor)
            from spacesim.engine.isr import (
                BEAM_MODES as _BEAM_MODES,
                beam_params as _bp, effective_gain as _eg, footprint_polygon, ground_heading_deg,
            )
            # IP-1222 Design Decisions 1-2 (BL-0212, FR-1610) — the order's beam_mode param wins,
            # else the executing sensor's declared beam_mode. A ground radar whose requested mode
            # is a radar entry (fence/dish) uses the ground_radar table; a radar naming no radar
            # mode stays on the payload type chosen above, unchanged.
            if beam_mode_req is None and actor_sensor is not None and actor_sensor.beam_mode:
                beam_mode_req = actor_sensor.beam_mode
            if (actor_sensor is not None and actor_sensor.kind == "ground_radar"
                    and isinstance(beam_mode_req, str)
                    and beam_mode_req in _BEAM_MODES["ground_radar"]):
                payload_type = "ground_radar"
            bp, resolved_mode = _bp(payload_type, beam_mode_req)
            # Audit 2026-06 Commands §C3 — base gain is clamped to [0, 1]: the operator
            # may deliberately request a *less*-confident observation (search-only
            # sweeps, distant looks) but cannot type a value above 1.0 to fast-track
            # custody. Beam parameters + look angle still modulate the effective gain
            # through isr.effective_gain.
            requested_gain = float(p.get("gain", 1.0))
            base_gain = max(0.0, min(1.0, requested_gain))
            # IP-1220 (FR-1630) — a space-based actor_sensor's altitude_band_affinity degrades
            # gain when the target's regime doesn't match; additive, None/None reproduces the
            # pre-package call exactly.
            target_regime = None
            band_affinity = getattr(actor_sensor, "altitude_band_affinity", None) if actor_sensor else None
            if band_affinity is not None:
                target_orbit = self.world.assets.get(order.target, None)
                target_orbit = target_orbit.orbit if target_orbit is not None else None
                if target_orbit is not None:
                    from spacesim.engine.orbit import classify_regime
                    target_regime = classify_regime(target_orbit.a_m, target_orbit.e, target_orbit.i_deg)
            # IP-1221 (FR-1670) — a passive-EO sensor declaring a usable phase-angle range has its
            # gain scaled by the Sun-target-sensor phase angle at the observation instant
            # (win.start, the time the execute event is scheduled at). Undeclared sensors and any
            # undefined geometry leave the gain unchanged.
            phase_deg = None
            usable_range = getattr(actor_sensor, "usable_phase_angle_deg", None) if actor_sensor else None
            if usable_range is not None and actor_sensor.needs_lighting:
                phase_deg = self._observation_phase_angle_deg(actor_sensor, order.target, win.start)
            gain = _eg(base_gain, look_angle_deg, bp, target_regime=target_regime, band_affinity=band_affinity,
                       phase_angle_deg=phase_deg, usable_phase_range=usable_range if phase_deg is not None else None)

            # Compute footprint polygon from the actor's current orbit position + heading.
            footprint: Optional[list] = None
            if actor_orbit is not None:
                from spacesim.engine.geometry import eci_to_ecef, ecef_to_geodetic
                r, _ = self.prop.rv(actor_orbit, self.world.now)
                geo = ecef_to_geodetic(eci_to_ecef(r, self.world.now))
                heading = ground_heading_deg(actor_orbit, self.world.now, self.prop)
                footprint = footprint_polygon(
                    geo.lat_deg, geo.lon_deg, geo.alt_m, heading, bp, look_angle_deg,
                )

            return "execute_observe", {
                "cell": order.cell,
                "object": order.target,
                "intent": intent,
                "gain": gain,
                "characterizes": characterizes,
                # Audit 2026-06 Commands §C3 — classification is never operator-set; it
                # accumulates from the observation outcome instead.
                "classification": None,
                "actor": order.actor,
                "beam_mode": resolved_mode,
                "look_angle_deg": look_angle_deg,
                "duration_s": duration_s,
                "footprint": footprint,
                "custody_confidence_at_decision": custody_confidence,
            }

        if order.action == "downlink":
            # FW §11.A.4 — extended params: station (via), bitrate_cap_kbps, priority lane,
            # partial_dump (last_n_minutes / product_ids).  All optional; defaults preserve
            # legacy single-token "delivers" behaviour.
            return "execute_downlink", {
                "actor": order.actor,
                "delivers": p.get("delivers", "imagery_delivered"),
                "via": p.get("via"),
                "bitrate_cap_kbps": p.get("bitrate_cap_kbps"),
                "priority": p.get("priority", "routine"),
                "partial_dump": p.get("partial_dump"),
                "custody_confidence_at_decision": custody_confidence,
            }

        if order.action == "command":
            return "execute_command", {
                "actor": order.actor, "verb": p.get("verb"), "params": dict(p),
                **self._delivery_keys(win),
                "custody_confidence_at_decision": custody_confidence,
            }

        # maneuver
        dv = list(np.asarray(p.get("dv", [0, 0, 0]), dtype=float))
        return "execute_maneuver", {
            "actor": order.actor,
            **self._delivery_keys(win),
            "dv": dv,
            "cost": float(np.linalg.norm(dv)),
            "custody_confidence_at_decision": custody_confidence,
            # IP-1250 (FR-1320) — an optional operator-entered purpose tag, additive; a manoeuvre
            # order with no supplied tag is accepted, recorded as "".
            "purpose_tag": str(p.get("purpose_tag", "")),
        }

    def _mark_cyber_queued(self, order: Order) -> None:
        order.status = "queued"
        order.earliest_window = None       # cyber is not pass-gated (resolves now, against posture)
        order.delivery_path = "cyber"

    def _plan_cyber(self, order: Order, commit: bool) -> None:
        if not commit:
            self._mark_cyber_queued(order)
            return
        # IP-1052 Design Decision 3 — the effect is constructed before the order is marked queued.
        p = order.params
        # Audit 2026-06 Commands §C2 — cyber Pₛ fully derived from vector × posture × dwell.
        # `vector` is mandatory (validator enforces). Payload table fixes reversibility /
        # escalation / intended_outcome. Operator overrides on success_prob / attribution /
        # outcome / reversible / escalation_weight / sm_susceptibility are removed.
        from spacesim.engine.cyber import (
            effective_success as _cyb_succ, payload_params as _cyb_pl, vector_params as _cyb_vec,
        )
        vector = p.get("vector")
        payload_name = p.get("payload")
        target_asset = self.world.assets.get(order.target or "")
        target_posture = target_asset.cyber_posture if target_asset else "medium"
        dwell_s = float(p.get("dwell_s", 0.0))
        vp, resolved_vec = _cyb_vec(vector)
        pp, resolved_pl = _cyb_pl(payload_name)
        succ = _cyb_succ(vector, target_posture, dwell_s)
        # Safe-mode susceptibility stays a White-Cell / scripted dial (not operator-typed
        # — the order form will not surface it). Persistence is a physical input on the
        # payload, defaulted from the payload's `min_persistence_h`.
        persistence_h = float(p.get("persistence_h", vp.get("min_persistence_h", 1.0)))
        effect = EffectInstance(
            template="cyber",
            category="cyber",
            segment=p.get("segment", "link"),
            actor=order.actor,
            target=order.target or "",
            reversible=pp["reversible"],
            attribution=vp["attribution_bias"],
            escalation_weight=pp["escalation_weight"],
            requires="none",
            intended_outcome=pp["intended_outcome"],
            success_prob=succ,
            # Preserve the operator's raw vector string so the vuln-dict match in
            # _effective_probability finds the target's matching access vector. The
            # cyber.VECTORS lookup above was for the Pₛ math only.
            access_vector=vector,
            persistence_s=3600.0 * max(1.0, persistence_h),
            sm_susceptibility=float(p.get("sm_susceptibility", 1.0)),
            persistence_bonus=float(p.get("persistence_bonus", 1.0)),
            window_start=self.sim.clock.now,
            order_action_type=order.action,
        )
        payload = {"effect": effect.model_dump()}
        self._mark_cyber_queued(order)
        self.sim.schedule(self.sim.clock.now, "execute_effect", payload, actor=order.cell, tag=order.id)

    # -- handlers (run inside the deterministic event loop) --------------------
    def _h_effect(self, world: WorldState, payload: dict, rng) -> None:
        effect = EffectInstance.model_validate(payload["effect"])
        cons = payload.get("consume")
        # IP-1320 (FR-1460, FR-3410) — re-check the rounds at execution: an earlier queued
        # engagement may have spent them. Mirrors _h_maneuver's failed Δv re-validation: no
        # resolution, no RNG draw, nothing charged.
        if cons and "ammo" in cons:
            shooter = world.assets.get(cons["actor"])
            if shooter is not None and shooter.resources.ammo < int(cons["ammo"]):
                world.effect_log.append({
                    "t": world.now, "template": effect.template, "category": effect.category,
                    "target": effect.target, "achieved": "failed", "success": False,
                    "reason": "insufficient_ammo",
                })
                return
        outcome = self.resolver.resolve(effect, world, rng)
        world.effect_log.append({
            "t": world.now,
            "template": effect.template,
            "category": effect.category,
            "target": effect.target,
            "achieved": outcome.achieved_outcome,
            "success": outcome.success,
        })
        for se in outcome.side_effects:
            if se.get("type") == "political_consequence":
                world.consequences.append({**se, "t": world.now})
        # IP-1321 (FR-1480, FS-132 v1.1) — a fired salvo is charged whether it hits or misses
        # (owner decision, BL-0249). "Fired" = reached resolution, so this also covers a target
        # already destroyed at execution; the re-check above returns first and charges nothing.
        if cons:
            actor = world.assets.get(cons["actor"])
            if actor is not None and "ammo" in cons:
                actor.resources.ammo -= int(cons["ammo"])
            # IP-1320 (FR-1470, ADR-0037) — no power_w branch: jamming never changes the rating.
            # A pre-IP-1320 save's jam payload may still carry a power_w entry; it is ignored.

    def _h_maneuver(self, world: WorldState, payload: dict, rng) -> None:
        self._release_bookings_on_execute(payload.get("__order_id"))
        actor = world.assets.get(payload["actor"])
        if actor is None or actor.orbit is None:
            return
        # IP-1290/IP-1085 (FR-1440) — a jam covering the link this command's delivery path uses.
        jammed = self._delivery_jammed(world, payload)
        if jammed:
            world.effect_log.append(self._jammed_record(world, "maneuver", payload, jammed))
            payload["applied"] = False
            return
        # Re-validate at execute time (resources may have changed since planning).
        if actor.resources.delta_v_ms + 1e-9 < float(payload["cost"]) or actor.health == "destroyed":
            world.effect_log.append({"t": world.now, "template": "maneuver", "target": payload["actor"],
                                     "achieved": "failed", "success": False})
            # IP-1250 (FR-1320) — mutating `payload` in place is captured by the eventlog entry
            # Simulation.advance_to() logs immediately after this handler returns (same pattern
            # IP-1062's condition_check uses); the ledger read excludes a failed re-validation.
            payload["applied"] = False
            return
        dv = np.asarray(payload["dv"], dtype=float)
        actor.orbit = self.prop.apply_impulse(actor.orbit, dv, world.now)
        actor.resources.delta_v_ms -= float(payload["cost"])
        payload["applied"] = True
        payload["remaining_delta_v_ms"] = actor.resources.delta_v_ms

    def _h_downlink(self, world: WorldState, payload: dict, rng) -> None:
        """Deliver collected product — unless the downlink is jammed at the execution moment."""
        actor = world.assets.get(payload["actor"])
        denied = is_link_denied(world, payload["actor"], world.now, link="downlink")
        flag = payload["delivers"]
        if denied:
            world.effect_log.append({"t": world.now, "template": "downlink", "target": payload["actor"],
                                     "achieved": "blocked", "success": False})
            return
        world.mission[flag] = True
        world.mission[f"{flag}_at"] = world.now
        # FW §11.A.4 — partial_dump drains storage proportional to the requested fraction
        # of buffered product (defaults to a full dump).
        partial = payload.get("partial_dump") or {}
        frac = 1.0
        if isinstance(partial, dict) and partial.get("fraction") is not None:
            try:
                frac = max(0.0, min(1.0, float(partial["fraction"])))
            except (TypeError, ValueError):
                frac = 1.0
        if actor is not None and actor.bus_state is not None:
            downlink_storage(actor.bus_state, frac)
        world.effect_log.append({"t": world.now, "template": "downlink", "target": payload["actor"],
                                 "achieved": "delivered", "success": True,
                                 "via": payload.get("via"), "priority": payload.get("priority"),
                                 "bitrate_cap_kbps": payload.get("bitrate_cap_kbps"),
                                 "fraction": frac})

    def _h_command(self, world: WorldState, payload: dict, rng) -> None:
        """Apply a bus/payload verb at its window (re-validates at execute time, like the others)."""
        self._release_bookings_on_execute(payload.get("__order_id"))
        # IP-1290/IP-1085 (FR-1440) — a jam covering the link the command's delivery path uses, at
        # execute time, fails delivery (mirrors _h_downlink's jam-check pattern).
        jammed = self._delivery_jammed(world, payload)
        if jammed:
            world.effect_log.append(self._jammed_record(world, payload.get("verb"), payload, jammed))
            return
        ok, label = apply_command(world, payload["actor"], payload.get("verb") or "",
                                   payload.get("params", {}), world.now)
        world.effect_log.append({"t": world.now, "template": payload.get("verb"),
                                 "target": payload["actor"], "achieved": label, "success": ok})

    def _h_observe(self, world: WorldState, payload: dict, rng) -> None:
        self._release_bookings_on_execute(payload.get("__order_id"))
        track = world.track_for(payload["cell"], payload["object"])
        if track is None:
            track = Track(object=payload["object"], owner=payload["cell"], last_observation=world.now, confidence=0.0)
            world.tracks.append(track)
        # A report raises confidence incrementally (toward 1.0) and shrinks uncertainty.
        quality = min(1.0, track.current_confidence(world.now) + float(payload.get("gain", 0.5)))
        observe(
            track,
            world.now,
            quality=quality,
            characterizes=payload.get("characterizes", True),
            classification=payload.get("classification"),
        )
        # Capture the measured state so the belief stream (map/3D viewer) can propagate it forward.
        obj = world.assets.get(payload["object"])
        if obj is not None and obj.orbit is not None:
            track.state_estimate = obj.orbit.model_copy(deep=True)

        # Store the collection footprint for map rendering.
        if payload.get("footprint"):
            track.last_footprint = payload["footprint"]
            track.last_beam_mode = payload.get("beam_mode", "stripmap")
            track.last_collection_t = world.now

        # Apply battery drain to the collecting asset if it has a bus state.
        # A space-based sensor may be dual-registered as an Asset (same ID) for bus tracking.
        actor_id = payload.get("actor")
        if actor_id:
            actor = world.assets.get(actor_id)
            if actor and actor.bus_state:
                from spacesim.engine.isr import beam_params as _bp, soc_drain as _drain
                payload_type = (actor.payload_state.type
                                if actor.payload_state else "isr_eo")
                bp, _ = _bp(payload_type, payload.get("beam_mode"))
                drain = _drain(bp, float(payload.get("duration_s", 300.0)))
                actor.bus_state.power.battery_soc = max(
                    0.0, min(1.0, actor.bus_state.power.battery_soc - drain)
                )
                from spacesim.engine.bus import recompute_status
                recompute_status(actor.bus_state)
        # FUTURE-WORK §7: organic detection auto-cues an SSN characterize request when the track
        # has some confidence but hasn't been characterized yet. Deterministic: submit_request
        # schedules ssn_collect/ssn_deliver events that replay exactly.
        if (self.auto_cue_ssn is not None and obj is not None and obj.orbit is not None
                and not track.characterized and 0.3 < track.confidence < 0.85):
            from spacesim.engine.orbit import classify_regime
            from spacesim.engine.ssn import SSNRequest
            regime = classify_regime(obj.orbit.a_m, obj.orbit.e, obj.orbit.i_deg)
            already = any(r.cell == payload["cell"] and r.target == payload["object"]
                          and r.intent == "characterize"
                          and r.state in ("DRAFT", "SCHEDULED", "COLLECTED")
                          for r in self.auto_cue_ssn.requests.values())
            if not already:
                req = SSNRequest(id="", cell=payload["cell"], intent="characterize",
                                 target=payload["object"], regime=regime, priority="priority")
                self.auto_cue_ssn.submit_request(payload["cell"], req)
