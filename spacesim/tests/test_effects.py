"""EffectResolver: the five D's, kinetic side effects, reversible denial, and the cyber exception."""

from __future__ import annotations

from spacesim.engine.effects import (
    EffectInstance,
    ModerateEffectResolver,
    is_link_denied,
)
from spacesim.engine.entities import Asset
from spacesim.engine.rng import SeededRng
from spacesim.engine.world import WorldState


def _world_with_target(**asset_kw) -> WorldState:
    w = WorldState(now=1000)
    w.assets["TGT"] = Asset(id="TGT", owner="blue", kind="satellite", **asset_kw)
    return w


def test_kinetic_destroy_spawns_debris_and_political_consequence():
    w = _world_with_target()
    eff = EffectInstance(
        category="direct_ascent", segment="orbital", actor="INT", target="TGT",
        kinetic=True, debris_risk="high", attribution="overt", escalation_weight=8,
        intended_outcome="destroy", success_prob=1.0,
    )
    out = ModerateEffectResolver().resolve(eff, w, SeededRng(1))
    assert out.success and out.achieved_outcome == "destroy"
    assert w.assets["TGT"].health == "destroyed"
    assert len(w.debris) == 1
    assert any(se["type"] == "political_consequence" and se["severity"] == "high" for se in out.side_effects)


def test_reversible_deny_creates_active_link_effect_for_its_window():
    w = _world_with_target()
    eff = EffectInstance(
        category="electronic_warfare", segment="link", actor="JAM", target="TGT",
        intended_outcome="deny", success_prob=1.0, window_start=2000, window_end=5000,
    )
    out = ModerateEffectResolver().resolve(eff, w, SeededRng(1))
    assert out.achieved_outcome == "deny"
    assert is_link_denied(w, "TGT", 3000)        # inside the window
    assert not is_link_denied(w, "TGT", 6000)    # after the window
    assert w.assets["TGT"].health == "nominal"   # reversible: no permanent damage


def test_failed_effect_changes_nothing():
    w = _world_with_target()
    eff = EffectInstance(target="TGT", intended_outcome="deny", success_prob=0.0)
    out = ModerateEffectResolver().resolve(eff, w, SeededRng(1))
    assert not out.success and out.achieved_outcome == "none"
    assert not w.active_effects


def test_cyber_blocked_by_patched_or_missing_vector():
    res = ModerateEffectResolver()

    patched = _world_with_target(cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": True}])
    eff = EffectInstance(category="cyber", target="TGT", access_vector="ground_modem",
                         intended_outcome="deny", success_prob=1.0, requires="none")
    assert not res.resolve(eff, patched, SeededRng(1)).success  # patched vuln closed

    no_vector = _world_with_target(cyber_vulnerabilities=[])
    assert not res.resolve(eff, no_vector, SeededRng(1)).success  # no foothold


def test_cyber_succeeds_through_open_vector_and_respects_posture():
    res = ModerateEffectResolver()
    w = _world_with_target(
        cyber_posture="low",
        cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": False}],
    )
    eff = EffectInstance(category="cyber", target="TGT", access_vector="ground_modem",
                         intended_outcome="deny", success_prob=1.0, requires="none", persistence_s=3600)
    out = res.resolve(eff, w, SeededRng(1))
    assert out.success and out.achieved_outcome == "deny"
    assert is_link_denied(w, "TGT", w.now + 1_000_000)  # denial persists outside any pass window
