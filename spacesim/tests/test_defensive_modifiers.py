"""Defensive command verbs must actually defend — Audit 2026-06 (Commands) §C1.

This is the headline finding of the satellite-command audit: every Blue defensive verb
*except* ``def.harden`` was wired only into the telemetry signature, never into the
``EffectResolver`` Pₛ/Pₖ math. A trainee who shifted users to evade a jam saw the jam
signature drop on their telemetry graph and concluded the move worked — but on the
resolver's seeded RNG roll the jam succeeded at exactly the same rate it would have
without the defensive action. This is the opposite of the PME lesson the exercise teaches.

The audit's foundational decision (F1: rewire-where-research-named-a-fix) chose to wire
the three defender-side flags into ``effects.py:_effective_probability`` as multiplicative
modifiers. These tests fix that loop forever:

  - ``bus.comms.freq_hopping`` (set by ``def.frequency_hop``) reduces jam Pₛ.
  - ``payload_state.interference_mitigation`` (raised by ``satcom.mitigate_interference``
    and ``satcom.shift_users``) reduces jam Pₛ.
  - ``payload_state.evasion_active`` (set by ``def.maneuver_evade``) reduces kinetic Pₖ.

The cyber and safe-mode paths already consume defender state (cyber posture + patched
vulns + hardened) — those are spot-checked here to lock in the existing wiring against
regression.

All tests use ``success_prob=1.0`` and call ``_effective_probability`` directly so the
test is on the *threshold*, not the RNG draw — i.e. deterministic without reference to
the seed.
"""
from __future__ import annotations

from spacesim.engine.bus import BusState, CommsState, PayloadState
from spacesim.engine.effects import EffectInstance, ModerateEffectResolver
from spacesim.engine.entities import Asset
from spacesim.engine.world import WorldState


def _world_with_target(
    *,
    freq_hopping: bool = False,
    interference_mitigation: float = 0.0,
    evasion_active: bool = False,
    hardened: bool = False,
    cyber_vulns: list | None = None,
    cyber_posture: str = "medium",
) -> WorldState:
    w = WorldState(now=1000)
    bus = BusState(comms=CommsState(freq_hopping=freq_hopping))
    payload = PayloadState(
        type="satcom",
        interference_mitigation=interference_mitigation,
        evasion_active=evasion_active,
        hardened=hardened,
    )
    w.assets["TGT"] = Asset(
        id="TGT", owner="blue", kind="satellite",
        bus_state=bus, payload_state=payload,
        cyber_vulnerabilities=cyber_vulns or [],
        cyber_posture=cyber_posture,
    )
    return w


def _jam_effect(success_prob: float = 1.0) -> EffectInstance:
    return EffectInstance(
        category="electronic_warfare", segment="link",
        actor="JAM", target="TGT",
        intended_outcome="deny", success_prob=success_prob,
    )


def _engage_effect(success_prob: float = 1.0) -> EffectInstance:
    return EffectInstance(
        category="direct_ascent", segment="orbital",
        actor="INT", target="TGT", kinetic=True, debris_risk="high",
        attribution="overt", escalation_weight=8,
        intended_outcome="destroy", success_prob=success_prob,
    )


# --------------------------------------------------------------------------- #
# C1.a — def.frequency_hop must reduce jam success probability.
# --------------------------------------------------------------------------- #

def test_frequency_hop_reduces_jam_probability():
    """def.frequency_hop ON must lower the effective jam Pₛ — not just the telemetry display."""
    resolver = ModerateEffectResolver()
    w_off = _world_with_target(freq_hopping=False)
    w_on = _world_with_target(freq_hopping=True)
    eff = _jam_effect(success_prob=1.0)
    p_off = resolver._effective_probability(eff, w_off)
    p_on = resolver._effective_probability(eff, w_on)
    assert p_off > p_on, (
        f"def.frequency_hop must reduce jam Pₛ; got off={p_off} vs on={p_on}"
    )


def test_frequency_hop_does_not_help_against_cyber():
    """Frequency-hop is an RF technique; cyber attacks don't traverse the RF link."""
    resolver = ModerateEffectResolver()
    cyber_eff = EffectInstance(
        category="cyber", target="TGT", access_vector="ground_modem",
        intended_outcome="deny", success_prob=1.0, requires="none",
    )
    w_hop = _world_with_target(
        freq_hopping=True,
        cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": False}],
    )
    w_nohop = _world_with_target(
        freq_hopping=False,
        cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": False}],
    )
    assert (resolver._effective_probability(cyber_eff, w_hop)
            == resolver._effective_probability(cyber_eff, w_nohop))


# --------------------------------------------------------------------------- #
# C1.b — satcom.mitigate_interference / shift_users must reduce jam Pₛ.
# --------------------------------------------------------------------------- #

def test_interference_mitigation_reduces_jam_probability():
    resolver = ModerateEffectResolver()
    eff = _jam_effect(success_prob=1.0)
    p_none = resolver._effective_probability(eff, _world_with_target(interference_mitigation=0.0))
    p_part = resolver._effective_probability(eff, _world_with_target(interference_mitigation=0.4))
    p_max = resolver._effective_probability(eff, _world_with_target(interference_mitigation=0.8))
    assert p_none > p_part > p_max, (
        f"satcom mitigation must monotonically reduce jam Pₛ; got {p_none}, {p_part}, {p_max}"
    )


def test_mitigation_compounds_with_frequency_hop():
    """Both defenses applied gives stricter reduction than either alone."""
    resolver = ModerateEffectResolver()
    eff = _jam_effect(success_prob=1.0)
    p_one = resolver._effective_probability(eff, _world_with_target(freq_hopping=True))
    p_both = resolver._effective_probability(
        eff, _world_with_target(freq_hopping=True, interference_mitigation=0.6),
    )
    assert p_both < p_one


# --------------------------------------------------------------------------- #
# C1.c — def.maneuver_evade must reduce kinetic engage Pₖ.
# --------------------------------------------------------------------------- #

def test_evasion_active_reduces_engage_probability():
    """An evasion burn during fly-out must materially cut engage Pₖ.

    Sourced from the four DA-ASAT test records (§14 of the realism research): target
    maneuver during the few-minute fly-out is the dominant defensive modifier on Pₖ.
    """
    resolver = ModerateEffectResolver()
    eff = _engage_effect(success_prob=1.0)
    p_off = resolver._effective_probability(eff, _world_with_target(evasion_active=False))
    p_on = resolver._effective_probability(eff, _world_with_target(evasion_active=True))
    assert p_off > p_on
    # Engage modifier is stronger than the jam modifier — keep this floor so the
    # trainee sees a *visibly* lower roll basis.
    assert p_on <= 0.6 * p_off


def test_evasion_does_not_help_against_jam():
    """An evasion burn is an orbital action; it doesn't change RF link denial."""
    resolver = ModerateEffectResolver()
    eff = _jam_effect(success_prob=1.0)
    p_evade = resolver._effective_probability(eff, _world_with_target(evasion_active=True))
    p_static = resolver._effective_probability(eff, _world_with_target(evasion_active=False))
    assert p_evade == p_static


# --------------------------------------------------------------------------- #
# C1.d — existing wiring stays green (regression locks for def.harden,
#        patched cyber vuln, cyber posture).
# --------------------------------------------------------------------------- #

def test_harden_still_reduces_safe_mode_susceptibility():
    """def.harden was already wired; lock it against regression."""
    resolver = ModerateEffectResolver()
    sm_eff = EffectInstance(
        category="cyber", target="TGT", access_vector="ground_modem",
        intended_outcome="safe_mode", success_prob=1.0, sm_susceptibility=1.0,
        persistence_bonus=1.0,
    )
    # safe-mode resolution applies the hardened multiplier inside resolve(); we test
    # the full path here to anchor the effect on whether the world is hardened.
    w_soft = _world_with_target(
        cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": False}],
        hardened=False,
    )
    w_hard = _world_with_target(
        cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": False}],
        hardened=True,
    )
    from spacesim.engine.rng import SeededRng

    # With success_prob=1 and a fixed seed, a soft target safes and a hard one
    # is much less likely; a single seed isn't a property test but it locks the
    # wiring against accidental removal.
    soft_safed = sum(
        1
        for s in range(50)
        if resolver.resolve(sm_eff, _world_with_target(
            cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": False}],
            hardened=False,
        ), SeededRng(s)).success
    )
    hard_safed = sum(
        1
        for s in range(50)
        if resolver.resolve(sm_eff, _world_with_target(
            cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": False}],
            hardened=True,
        ), SeededRng(s)).success
    )
    assert soft_safed > hard_safed


def test_patched_vuln_still_blocks_cyber():
    resolver = ModerateEffectResolver()
    eff = EffectInstance(
        category="cyber", target="TGT", access_vector="ground_modem",
        intended_outcome="deny", success_prob=1.0, requires="none",
    )
    w = _world_with_target(cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": True}])
    assert resolver._effective_probability(eff, w) == 0.0


def test_cyber_posture_still_modulates_probability():
    resolver = ModerateEffectResolver()
    eff = EffectInstance(
        category="cyber", target="TGT", access_vector="ground_modem",
        intended_outcome="deny", success_prob=1.0, requires="none",
    )
    p_low = resolver._effective_probability(eff, _world_with_target(
        cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": False}],
        cyber_posture="low",
    ))
    p_high = resolver._effective_probability(eff, _world_with_target(
        cyber_vulns=[{"vector": "ground_modem", "patchable": True, "patched": False}],
        cyber_posture="high",
    ))
    assert p_low > p_high


# --------------------------------------------------------------------------- #
# C1.e — Property: modifiers never push Pₛ below zero, never lift above input.
# --------------------------------------------------------------------------- #

def test_modifiers_stay_in_unit_interval():
    """No combination of defender flags can push p outside [0, base]."""
    resolver = ModerateEffectResolver()
    jam = _jam_effect(success_prob=1.0)
    eng = _engage_effect(success_prob=1.0)
    for fh in (False, True):
        for im in (0.0, 0.4, 0.8):
            p = resolver._effective_probability(
                jam, _world_with_target(freq_hopping=fh, interference_mitigation=im),
            )
            assert 0.0 <= p <= 1.0
    for ev in (False, True):
        p = resolver._effective_probability(
            eng, _world_with_target(evasion_active=ev),
        )
        assert 0.0 <= p <= 1.0
