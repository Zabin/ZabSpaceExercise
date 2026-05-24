"""Effects model and the five-D resolver (``03-counterspace-taxonomy.md``, ``04-data-model.md`` §4).

Every offensive action resolves to one of the five D's — deceive / disrupt / deny / degrade /
destroy — via a probabilistic, seeded-RNG resolver (so outcomes are reproducible under replay).
The resolver is the third fidelity seam: the moderate model rolls success against a per-effect
probability modulated by target posture/defenses, then applies the world changes (health for
destroy/degrade, an active reversible denial for deny/disrupt/deceive) and emits side effects
(debris + political consequence for kinetic strikes, attribution signals, resource consumption).

Design decisions (see memory.md): effect success is **probabilistic**; "kinetic" is an explicit
flag on the instance; reversible link effects carry a window/persistence span.
"""

from __future__ import annotations

from typing import Literal, Optional, Protocol

from pydantic import BaseModel, Field

from spacesim.engine.bus import enter_safe_mode
from spacesim.engine.rng import SeededRng

# WorldState is only referenced in annotations (strings under ``from __future__ import
# annotations``) and via duck-typed attribute access at runtime, so it is intentionally NOT
# imported here — that would create an import cycle (world.py holds these effect models).

Outcome = Literal["deceive", "disrupt", "deny", "degrade", "destroy", "safe_mode", "none"]
Category = Literal["direct_ascent", "co_orbital", "electronic_warfare", "directed_energy", "cyber"]

REVERSIBLE_LINK_OUTCOMES = {"deceive", "disrupt", "deny"}


class EffectInstance(BaseModel):
    template: str = ""
    category: Category = "electronic_warfare"
    segment: Literal["orbital", "link", "terrestrial"] = "link"
    actor: str = ""
    target: str = ""
    reversible: bool = True
    kinetic: bool = False
    debris_risk: Literal["none", "low", "high"] = "none"
    attribution: Literal["overt", "ambiguous", "covert"] = "ambiguous"
    escalation_weight: int = 0
    requires: str = "none"            # gating access channel (none for cyber)
    intended_outcome: Outcome = "deny"

    # Resolution inputs:
    success_prob: float = 0.9             # base probability / base susceptibility for safe_mode
    access_vector: Optional[str] = None   # cyber: which modeled vulnerability
    persistence_s: float = 0.0            # reversible duration when no window span is given
    window_start: Optional[int] = None    # filled by the order layer from the access window
    window_end: Optional[int] = None
    # Safe-mode inducement (12-safe-mode-loop.md §6.1); only read when intended_outcome=safe_mode:
    sm_susceptibility: float = 1.0        # White-Cell master dial multiplier
    persistence_bonus: float = 1.0        # sustained vs. one-shot attempt


class EffectOutcome(BaseModel):
    achieved_outcome: Outcome
    success: bool
    side_effects: list[dict] = Field(default_factory=list)


class ActiveEffect(BaseModel):
    target: str
    outcome: Outcome
    start: int
    end: int
    reversible: bool = True
    attribution: str = "ambiguous"


class DebrisField(BaseModel):
    created_at: int
    source: str
    region: dict = Field(default_factory=dict)


class EffectResolver(Protocol):
    def resolve(self, effect: EffectInstance, world: "WorldState", rng: SeededRng) -> EffectOutcome: ...


_POSTURE_FACTOR = {"low": 1.25, "medium": 1.0, "high": 0.6}


class ModerateEffectResolver:
    def resolve(self, effect: EffectInstance, world: "WorldState", rng: SeededRng) -> EffectOutcome:
        target = world.assets.get(effect.target)
        if target is not None and target.health == "destroyed":
            return EffectOutcome(achieved_outcome="none", success=False)

        p = self._effective_probability(effect, world)
        if effect.intended_outcome == "safe_mode":
            # §6.1 susceptibility: base × WC dial × (1 − hardening) × persistence, clamped.
            hardening = float(getattr(target, "hardening", 0.0)) if target is not None else 0.0
            p = min(0.98, p * effect.sm_susceptibility * (1.0 - hardening) * effect.persistence_bonus)
        # Draw first (keeps the RNG sequence stable regardless of branch), then branch.
        roll = rng.random()
        success = roll < p

        side: list[dict] = []
        if not success:
            if effect.attribution != "covert":
                side.append({"type": "attribution_signal", "to": _victim_cell(world, effect), "confidence": 0.2})
            return EffectOutcome(achieved_outcome="none", success=False, side_effects=side)

        achieved = effect.intended_outcome
        start = effect.window_start if effect.window_start is not None else world.now
        end = effect.window_end if effect.window_end is not None else int(start + effect.persistence_s * 1_000_000)

        if achieved == "destroy":
            if target is not None:
                target.health = "destroyed"
            if effect.kinetic and effect.debris_risk != "none":
                world.debris.append(
                    DebrisField(created_at=world.now, source=effect.actor, region={"about": effect.target})
                )
                severity = "high" if (effect.escalation_weight >= 7 or effect.debris_risk == "high") else "medium"
                side.append({"type": "political_consequence", "severity": severity, "cause": effect.template})
        elif achieved == "degrade":
            if target is not None:
                target.health = "degraded"
        elif achieved == "safe_mode":
            if target is not None and target.bus_state is not None:
                cause = "cyber" if effect.category == "cyber" else "ew" if effect.category == "electronic_warfare" else "bus_stress"
                enter_safe_mode(target.bus_state, world.now, cause)
        elif achieved in REVERSIBLE_LINK_OUTCOMES:
            world.active_effects.append(
                ActiveEffect(
                    target=effect.target,
                    outcome=achieved,
                    start=start,
                    end=end,
                    reversible=True,
                    attribution=effect.attribution,
                )
            )

        conf = {"overt": 0.95, "ambiguous": 0.5, "covert": 0.15}[effect.attribution]
        side.append({"type": "attribution_signal", "to": _victim_cell(world, effect), "confidence": conf})
        return EffectOutcome(achieved_outcome=achieved, success=True, side_effects=side)

    def _effective_probability(self, effect: EffectInstance, world: "WorldState") -> float:
        p = effect.success_prob
        if effect.category == "cyber":
            target = world.assets.get(effect.target)
            if target is not None:
                for vuln in target.cyber_vulnerabilities:
                    if vuln.get("vector") == effect.access_vector:
                        if vuln.get("patched"):
                            return 0.0  # patched vulnerability: the access vector is closed
                        break
                else:
                    if effect.access_vector is not None:
                        return 0.0  # no matching access vector → no foothold
                p *= _POSTURE_FACTOR.get(getattr(target, "cyber_posture", "medium"), 1.0)
        return max(0.0, min(1.0, p))


def _victim_cell(world: "WorldState", effect: EffectInstance) -> str:
    target = world.assets.get(effect.target)
    return target.owner if target is not None else "unknown"


def is_link_denied(world: "WorldState", target_id: str, t: int) -> bool:
    return any(
        ae.target == target_id and ae.outcome in {"deny", "disrupt"} and ae.start <= t <= ae.end
        for ae in world.active_effects
    )
