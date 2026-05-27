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
    return Scene(
        satellites={i: a.orbit for i, a in world.assets.items() if a.orbit is not None},
        sites={i: a.as_ground_site() for i, a in world.assets.items() if a.location is not None},
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
        self._sensor_bookings: dict[str, list[tuple[int, int]]] = {}  # contention: one task at a time
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
        preview (`OPERATOR-UI-DESIGN.md` §12). Touches no engine state — no RNG, no event log, no
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
            self.sim.schedule(win.start, kind, data, actor=order.cell, tag=order.id)

    def cancel(self, order_id: str) -> bool:
        """Cancel a still-queued order; the scheduled event is skipped (never logged → replay-safe)."""
        o = self.orders.get(order_id)
        if o is None or o.status != "queued":
            return False
        self.sim.cancel(order_id)
        o.status = "cancelled"
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
        if via is not None:
            g = ap.windows(via, order.actor, COMMAND_UPLINK, now, now + self.horizon)
            if g:
                choices.append(("ground_uplink", g[0]))
        isl = self._best_isl_window(ap, order.cell, order.actor, now)
        if isl is not None:
            choices.append(("isl_relay", isl))

        if not choices:
            order.status, order.fail_reason = "rejected", "no_window"
            return
        path, win = min(choices, key=lambda pw: pw[1].start)
        order.delivery_path = path
        order.earliest_window = (win.start, win.end)
        order.status = "queued"
        if commit:
            kind, data = self._exec_payload(order, win)
            self.sim.schedule(win.start, kind, data, actor=order.cell, tag=order.id)

    def _best_isl_window(self, ap: AccessProvider, cell: str, actor: str, now: int) -> Optional[AccessWindow]:
        best: Optional[AccessWindow] = None
        for rid, relay in self.world.assets.items():
            if rid == actor or relay.owner != cell or not relay.isl_capable or relay.orbit is None:
                continue
            wins = ap.windows(rid, actor, ISL_LINK, now, now + self.horizon)
            if wins and (best is None or wins[0].start < best.start):
                best = wins[0]
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
            kind, data = self._exec_payload(order, win)
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
            effect = EffectInstance(
                template=p.get("template", "ew_jam"),
                category="electronic_warfare",
                segment="link",
                actor=order.actor,
                target=order.target or "",
                reversible=True,
                attribution=p.get("attribution", "ambiguous"),
                escalation_weight=p.get("escalation_weight", 3),
                requires=JAM_FOOTPRINT,
                intended_outcome=p.get("outcome", "deny"),
                success_prob=p.get("success_prob", 0.9),
                window_start=win.start,
                window_end=win.end,
            )
            return "execute_effect", {
                "effect": effect.model_dump(),
                "consume": {"actor": order.actor, "power_w": p.get("power_cost", 0.0)},
            }

        if order.action == "engage":
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
                success_prob=p.get("success_prob", 0.9),
                window_start=win.start,
                window_end=win.end,
            )
            return "execute_effect", {
                "effect": effect.model_dump(),
                "consume": {"actor": order.actor, "ammo": 1},
            }

        if order.action == "observe":
            intent = p.get("intent", "track")
            # characterize resolves type/intent; search/track refine the state estimate.
            characterizes = p.get("characterizes", intent == "characterize")
            return "execute_observe", {
                "cell": order.cell,
                "object": order.target,
                "intent": intent,
                "gain": p.get("gain", 1.0),       # confidence added per report (toward 1.0)
                "characterizes": characterizes,
                "classification": p.get("classification"),
            }

        if order.action == "downlink":
            return "execute_downlink", {
                "actor": order.actor,
                "delivers": p.get("delivers", "imagery_delivered"),
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
        effect = EffectInstance(
            template=p.get("template", "cyber"),
            category="cyber",
            segment=p.get("segment", "link"),
            actor=order.actor,
            target=order.target or "",
            reversible=p.get("reversible", True),
            attribution="covert",
            escalation_weight=p.get("escalation_weight", 4),
            requires="none",
            intended_outcome=p.get("outcome", "deny"),
            success_prob=p.get("success_prob", 0.7),
            access_vector=p.get("access_vector"),
            persistence_s=p.get("persistence_s", 3600.0),
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
        if actor is not None and actor.bus_state is not None:
            downlink_storage(actor.bus_state, 1.0)
        world.effect_log.append({"t": world.now, "template": "downlink", "target": payload["actor"],
                                 "achieved": "delivered", "success": True})

    def _h_command(self, world: WorldState, payload: dict, rng) -> None:
        """Apply a bus/payload verb at its window (re-validates at execute time, like the others)."""
        ok, label = apply_command(world, payload["actor"], payload.get("verb") or "",
                                   payload.get("params", {}), world.now)
        world.effect_log.append({"t": world.now, "template": payload.get("verb"),
                                 "target": payload["actor"], "achieved": label, "success": ok})

    def _h_observe(self, world: WorldState, payload: dict, rng) -> None:
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
