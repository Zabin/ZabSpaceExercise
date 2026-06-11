"""Orders — issue -> validate -> queue to the next window -> execute (``03-simulation-engine.md`` §4).

Players never act instantly: an order is validated (ownership, ROE/authorities, resources, and the
weapons-quality track gate for engagements), then queued for execution at the next valid access
window for its channel. Execution fires as a deterministic event in the simulation, so it is
captured in the event log and reproduced exactly on replay. **Cyber is the exception** — it is not
window-gated and resolves against a modeled access vector subject to the defender's posture, so it
can act outside any pass.
"""

from __future__ import annotations

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
from spacesim.engine.custody import Track, WEAPONS_QUALITY_THRESHOLD, observe
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
        sensors=dict(world.sensors),
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
    ) -> None:
        self.sim = sim
        self.world: WorldState = sim.world
        self.roe = roe or {}
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

        sim.register_handler("execute_effect", self._h_effect)
        sim.register_handler("execute_maneuver", self._h_maneuver)
        sim.register_handler("execute_observe", self._h_observe)
        sim.register_handler("execute_downlink", self._h_downlink)
        sim.register_handler("execute_command", self._h_command)

    # -- issue pipeline --------------------------------------------------------
    def issue(self, order: Order) -> Order:
        order.issued_at = self.sim.clock.now
        self._order_counter += 1
        order.id = f"ord-{self._order_counter}"
        self.orders[order.id] = order
        self._plan(order, commit=True)
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
        order.earliest_window = (win.start, win.end)
        order.delivery_path = "ground_uplink"  # jam/engage/downlink gate on a single access window
        order.status = "queued"
        if commit:
            kind, data = self._exec_payload(order, win)
            data["__order_id"] = order.id  # threaded through so handlers can release bookings
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
        order.delivery_path = path
        order.earliest_window = (win.start, win.end)
        order.status = "queued"
        if commit:
            if path != "stored_program":
                key = (order.actor, win.start)
                self._pass_bookings[key] = self._pass_bookings.get(key, 0) + 1
                self._order_pass[order.id] = key
            kind, data = self._exec_payload(order, win)
            data["__order_id"] = order.id
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
        chosen: Optional[tuple[str, AccessWindow]] = None
        for sid in sensor_ids:
            wins = ap.windows(sid, order.target or "", SENSOR_OBSERVATION, now, now + self.horizon)
            for w in wins:
                if not self._contended(sid, w.start, w.end):
                    chosen = (sid, w)
                    break
            if chosen:
                break
        if chosen is None:
            order.status = "rejected"
            order.fail_reason = "sensor_contended" if sensor_ids else "no_window"
            return
        sid, win = chosen
        order.actor = sid
        order.delivery_path = "sensor_collect"
        order.earliest_window = (win.start, win.end)
        order.status = "queued"
        if commit:
            self._sensor_bookings.setdefault(sid, []).append((win.start, win.end))
            self._order_sensor[order.id] = (sid, win.start, win.end)
            kind, data = self._exec_payload(order, win)
            data["sensor_id"] = sid          # persisted in eventlog for booking reconstruction
            data["window_end"] = win.end     # on rewind/replay
            data["__order_id"] = order.id
            self.sim.schedule(win.start, kind, data, actor=order.cell, tag=order.id)

    def _candidate_sensors(self, order: Order) -> list[str]:
        if order.actor and order.actor != "auto":
            return [order.actor]
        return [sid for sid, s in self.world.sensors.items() if s.owner == order.cell]

    def _contended(self, sid: str, start: int, end: int) -> bool:
        return any(not (end <= b0 or start >= b1) for (b0, b1) in self._sensor_bookings.get(sid, []))

    # -- validation ------------------------------------------------------------
    def _validate(self, order: Order) -> tuple[bool, str]:
        if order.action not in ACTION_CHANNEL:
            return False, "unknown_action"

        if order.action == "observe":
            if order.actor == "auto":
                return True, ""  # sensor chosen at planning time
            sensor = self.world.sensors.get(order.actor)
            if sensor is None:
                return False, "no_such_sensor"
            if sensor.owner != order.cell:
                return False, "not_owner"
            return True, ""

        actor = self.world.assets.get(order.actor)
        if actor is None:
            return False, "no_such_asset"
        if actor.owner != order.cell:
            return False, "not_owner"

        if order.action == "engage":
            if not self.roe.get("kinetic_authorized", False):
                return False, "roe_kinetic_not_authorized"
            if actor.resources.ammo < 1:
                return False, "no_ammo"
            track = self.world.track_for(order.cell, order.target or "")
            if track is None or not track.is_weapons_quality(self.sim.clock.now, self.wq_threshold):
                return False, "no_weapons_quality_track"

        if order.action == "cyber" and not self.roe.get("cyber_authorized", False):
            return False, "roe_cyber_not_authorized"

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
    def _exec_payload(self, order: Order, win: AccessWindow) -> tuple[str, dict]:
        p = order.params
        if order.action == "jam":
            from spacesim.engine.jam import (
                effective_success_prob as _jam_prob,
                modulation_params as _jam_mod,
                power_draw_w as _jam_power,
            )
            modulation = p.get("modulation")
            power_w = float(p.get("power_w", 100.0))
            bandwidth_hz = float(p.get("bandwidth_hz", 1e6))
            victim_bw_hz = float(p.get("victim_bandwidth_hz", 1e6))
            base_prob = float(p.get("success_prob", 0.9))
            adj_prob = _jam_prob(base_prob, modulation, bandwidth_hz, victim_bw_hz)
            mod_params, resolved_mod = _jam_mod(modulation)
            # Deceptive jamming is overt by default — overrides operator attribution choice
            # unless they explicitly override.
            default_attr = mod_params["attribution_bias"]
            attribution = p.get("attribution", default_attr)
            effect = EffectInstance(
                template=p.get("template", "ew_jam"),
                category="electronic_warfare",
                segment="link",
                actor=order.actor,
                target=order.target or "",
                reversible=True,
                attribution=attribution,
                escalation_weight=p.get("escalation_weight", 3),
                requires=JAM_FOOTPRINT,
                intended_outcome=p.get("outcome", "deny"),
                success_prob=adj_prob,
                window_start=win.start,
                window_end=win.end,
            )
            return "execute_effect", {
                "effect": effect.model_dump(),
                "consume": {"actor": order.actor,
                            "power_w": p.get("power_cost", _jam_power(power_w, modulation))},
            }

        if order.action == "engage":
            from spacesim.engine.engage import kill_probability
            salvo_n = int(p.get("salvo_n", 1))
            interceptor_dv = float(p.get("interceptor_dv_ms", 200.0))
            base_pk = float(p.get("success_prob", 0.9))
            # Miss-distance is not knowable at planning; assume zero for the executed shot
            # (the closing-geometry preview is read-only and lives in the session API).
            adj_pk = kill_probability(base_pk, miss_km=0.0,
                                       interceptor_dv_ms=interceptor_dv, salvo_n=salvo_n)
            effect = EffectInstance(
                template=p.get("template", "da_asat"),
                category="direct_ascent",
                segment="orbital",
                actor=order.actor,
                target=order.target or "",
                reversible=False,
                kinetic=True,
                debris_risk="high",
                attribution="overt",
                escalation_weight=p.get("escalation_weight", 8),
                requires=WEAPON_ENGAGEMENT,
                intended_outcome="destroy",
                success_prob=adj_pk,
                window_start=win.start,
                window_end=win.end,
            )
            return "execute_effect", {
                "effect": effect.model_dump(),
                "consume": {"actor": order.actor, "ammo": max(1, salvo_n)},
            }

        if order.action == "observe":
            intent = p.get("intent", "track")
            # characterize resolves type/intent; search/track refine the state estimate.
            characterizes = p.get("characterizes", intent == "characterize")

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
            if actor_asset and actor_asset.payload_state:
                payload_type = actor_asset.payload_state.type
            elif actor_sensor:
                payload_type = "isr_eo" if actor_sensor.needs_lighting else "isr_sar"
            else:
                payload_type = "isr_eo"
            from spacesim.engine.isr import (
                beam_params as _bp, effective_gain as _eg, footprint_polygon, ground_heading_deg,
            )
            bp, resolved_mode = _bp(payload_type, beam_mode_req)
            base_gain = float(p.get("gain", 1.0))
            gain = _eg(base_gain, look_angle_deg, bp)

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
                "classification": p.get("classification"),
                "actor": order.actor,
                "beam_mode": resolved_mode,
                "look_angle_deg": look_angle_deg,
                "duration_s": duration_s,
                "footprint": footprint,
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
            }

        if order.action == "command":
            return "execute_command", {"actor": order.actor, "verb": p.get("verb"), "params": dict(p)}

        # maneuver
        dv = list(np.asarray(p.get("dv", [0, 0, 0]), dtype=float))
        return "execute_maneuver", {
            "actor": order.actor,
            "dv": dv,
            "cost": float(np.linalg.norm(dv)),
        }

    def _plan_cyber(self, order: Order, commit: bool) -> None:
        order.status = "queued"
        order.earliest_window = None       # cyber is not pass-gated (resolves now, against posture)
        order.delivery_path = "cyber"
        if not commit:
            return
        p = order.params
        # Cyber vector/payload parameters (FW §11.A.3): vector → success probability + attribution,
        # payload → reversibility + escalation weight.  Operator overrides win if explicitly set.
        from spacesim.engine.cyber import (
            effective_success as _cyb_succ, payload_params as _cyb_pl, vector_params as _cyb_vec,
        )
        vector = p.get("vector")
        payload_name = p.get("payload")
        target_asset = self.world.assets.get(order.target or "")
        target_posture = target_asset.cyber_posture if target_asset else "medium"
        dwell_s = float(p.get("dwell_s", 0.0))
        base_prob = float(p.get("success_prob", 0.7))
        vp, resolved_vec = _cyb_vec(vector)
        pp, resolved_pl = _cyb_pl(payload_name)
        succ = _cyb_succ(vector, target_posture, dwell_s) if vector else base_prob
        attribution = p.get("attribution", vp["attribution_bias"] if vector else "covert")
        effect = EffectInstance(
            template=p.get("template", "cyber"),
            category="cyber",
            segment=p.get("segment", "link"),
            actor=order.actor,
            target=order.target or "",
            reversible=p.get("reversible", pp["reversible"] if payload_name else True),
            attribution=attribution,
            escalation_weight=p.get("escalation_weight", pp["escalation_weight"] if payload_name else 4),
            requires="none",
            intended_outcome=p.get("outcome", pp["intended_outcome"] if payload_name else "deny"),
            success_prob=succ,
            access_vector=p.get("access_vector") or (resolved_vec if vector else None),
            persistence_s=p.get("persistence_s", 3600.0 * max(1.0, p.get("persistence_h", 1.0))),
            sm_susceptibility=p.get("sm_susceptibility", 1.0),
            persistence_bonus=p.get("persistence_bonus", 1.0),
            window_start=self.sim.clock.now,
        )
        self.sim.schedule(self.sim.clock.now, "execute_effect", {"effect": effect.model_dump()}, actor=order.cell, tag=order.id)

    # -- handlers (run inside the deterministic event loop) --------------------
    def _h_effect(self, world: WorldState, payload: dict, rng) -> None:
        effect = EffectInstance.model_validate(payload["effect"])
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
        cons = payload.get("consume")
        if cons and outcome.success:
            actor = world.assets.get(cons["actor"])
            if actor is not None:
                if "ammo" in cons:
                    actor.resources.ammo -= int(cons["ammo"])
                if "power_w" in cons:
                    actor.resources.power_w -= float(cons["power_w"])

    def _h_maneuver(self, world: WorldState, payload: dict, rng) -> None:
        self._release_bookings_on_execute(payload.get("__order_id"))
        actor = world.assets.get(payload["actor"])
        if actor is None or actor.orbit is None:
            return
        # Re-validate at execute time (resources may have changed since planning).
        if actor.resources.delta_v_ms + 1e-9 < float(payload["cost"]) or actor.health == "destroyed":
            world.effect_log.append({"t": world.now, "template": "maneuver", "target": payload["actor"],
                                     "achieved": "failed", "success": False})
            return
        dv = np.asarray(payload["dv"], dtype=float)
        actor.orbit = self.prop.apply_impulse(actor.orbit, dv, world.now)
        actor.resources.delta_v_ms -= float(payload["cost"])

    def _h_downlink(self, world: WorldState, payload: dict, rng) -> None:
        """Deliver collected product — unless the downlink is jammed at the execution moment."""
        actor = world.assets.get(payload["actor"])
        denied = is_link_denied(world, payload["actor"], world.now)
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
