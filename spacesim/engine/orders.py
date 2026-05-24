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
    JAM_FOOTPRINT,
    SENSOR_OBSERVATION,
    WEAPON_ENGAGEMENT,
)
from spacesim.engine.custody import Track, WEAPONS_QUALITY_THRESHOLD, observe
from spacesim.engine.effects import EffectInstance, ModerateEffectResolver
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.world import WorldState

ACTION_CHANNEL = {
    "jam": JAM_FOOTPRINT,
    "engage": WEAPON_ENGAGEMENT,
    "observe": SENSOR_OBSERVATION,
    "maneuver": COMMAND_UPLINK,
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
    status: str = "draft"     # draft|queued|rejected|executed
    fail_reason: Optional[str] = None


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

        sim.register_handler("execute_effect", self._h_effect)
        sim.register_handler("execute_maneuver", self._h_maneuver)
        sim.register_handler("execute_observe", self._h_observe)

    # -- issue pipeline --------------------------------------------------------
    def issue(self, order: Order) -> Order:
        order.issued_at = self.sim.clock.now
        ok, reason = self._validate(order)
        if not ok:
            order.status, order.fail_reason = "rejected", reason
            return order

        channel = ACTION_CHANNEL[order.action]
        if channel is None:
            self._queue_cyber(order)
            return order

        win = self._next_window(order, channel)
        if win is None:
            order.status, order.fail_reason = "rejected", "no_window"
            return order

        order.earliest_window = (win.start, win.end)
        order.status = "queued"
        kind, data = self._exec_payload(order, win)
        self.sim.schedule(win.start, kind, data, actor=order.cell)
        return order

    # -- validation ------------------------------------------------------------
    def _validate(self, order: Order) -> tuple[bool, str]:
        if order.action not in ACTION_CHANNEL:
            return False, "unknown_action"

        if order.action == "observe":
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
            if "via" not in order.params:
                return False, "no_command_station"

        return True, ""

    # -- windowing -------------------------------------------------------------
    def _window_endpoints(self, order: Order) -> tuple[str, str]:
        if order.action == "maneuver":
            return order.params["via"], order.actor   # command uplink: station <-> satellite
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
            return "execute_observe", {
                "cell": order.cell,
                "object": order.target,
                "quality": p.get("quality", 1.0),
                "characterizes": p.get("characterizes", True),
                "classification": p.get("classification"),
            }

        # maneuver
        dv = list(np.asarray(p.get("dv", [0, 0, 0]), dtype=float))
        return "execute_maneuver", {
            "actor": order.actor,
            "dv": dv,
            "cost": float(np.linalg.norm(dv)),
        }

    def _queue_cyber(self, order: Order) -> None:
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
            window_start=self.sim.clock.now,
        )
        order.status = "queued"
        order.earliest_window = None
        self.sim.schedule(self.sim.clock.now, "execute_effect", {"effect": effect.model_dump()}, actor=order.cell)

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
        dv = np.asarray(payload["dv"], dtype=float)
        actor.orbit = self.prop.apply_impulse(actor.orbit, dv, world.now)
        actor.resources.delta_v_ms -= float(payload["cost"])

    def _h_observe(self, world: WorldState, payload: dict, rng) -> None:
        track = world.track_for(payload["cell"], payload["object"])
        if track is None:
            track = Track(object=payload["object"], owner=payload["cell"], last_observation=world.now)
            world.tracks.append(track)
        observe(
            track,
            world.now,
            quality=payload.get("quality", 1.0),
            characterizes=payload.get("characterizes", True),
            classification=payload.get("classification"),
        )
