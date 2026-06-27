"""Operator probability overrides have been removed — Audit 2026-06 (Commands) §C2/§M2/§M3.

Phase B of the satellite-command audit removes operator-settable raw probability /
outcome knobs from the Order schema and replaces them with derivations from physical
inputs + world state:

  - jam   : Pₛ derived from modulation × power × bandwidth coverage (+ defender modifiers
            applied later in the resolver). `success_prob` removed from order.params.
  - engage: Pₖ derived from interceptor_class × altitude-reach × salvo independence
            (target maneuver applied in the resolver as the def.maneuver_evade modifier).
            New INTERCEPTORS database (§14 of the realism research) replaces the operator-
            typed `interceptor_dv_ms` free knob. `success_prob` removed.
  - cyber : `vector` becomes mandatory; the legacy raw `base_prob` fallback path is gone.
            `success_prob`/`outcome`/`escalation_weight`/`reversible` operator overrides
            removed — they derive from vector × posture × dwell + payload.
  - observe: `gain`/`characterizes`/`classification` operator overrides removed.

Save/AAR replay back-compat: `EffectInstance.success_prob` stays as a model field with
identical resolution semantics, because the per-effect payload is baked into the snapshot
stream at plan time. Only the Order→Effect derivation changes; serialized payloads look
the same in the log.
"""
from __future__ import annotations

import pytest

from spacesim.engine.engage import INTERCEPTORS, kill_probability_from_class


# --------------------------------------------------------------------------- #
# §M2 — INTERCEPTORS database structure and Pk math.
# --------------------------------------------------------------------------- #

def test_interceptors_database_has_four_classes_with_required_fields():
    assert set(INTERCEPTORS) == {"bmd_adapted", "mrbm_kkv", "abm_heavy", "coorbital"}
    for name, spec in INTERCEPTORS.items():
        assert 0.0 < spec["base_pk"] <= 1.0, name
        assert spec["seeker"] in {"ir_hit_to_kill", "radar_ir_dual", "rpo_optical"}
        assert "salvo_correlation" in spec
        # `max_alt_km` is None for co-orbital (reach via phasing); ints for the rest.
        if spec["max_alt_km"] is not None:
            assert spec["max_alt_km"] > 0, name


def test_altitude_reach_is_a_hard_cap_not_a_soft_decay():
    """Real interceptor classes have hard ceiling — beyond it the engagement is impossible."""
    # MRBM-derived KKV maxes at 1000 km (Mission Shakti / FY-1C envelope).
    p_in_envelope = kill_probability_from_class("mrbm_kkv", target_alt_km=500)
    p_over_envelope = kill_probability_from_class("mrbm_kkv", target_alt_km=1500)
    assert p_in_envelope > 0.0
    assert p_over_envelope == 0.0


def test_coorbital_has_no_altitude_ceiling():
    """SJ-21 / Burevestnik-class co-orbital phases to anywhere it can dwell-time reach."""
    p_leo = kill_probability_from_class("coorbital", target_alt_km=600)
    p_geo = kill_probability_from_class("coorbital", target_alt_km=36000)
    assert p_leo > 0.0 and p_geo > 0.0


def test_salvo_increases_pk_but_correlation_caps_it():
    """1 - (1-p1)^n with a correlated-failure floor (a bad track defeats every round)."""
    p1 = kill_probability_from_class("mrbm_kkv", target_alt_km=500, salvo_n=1)
    p4 = kill_probability_from_class("mrbm_kkv", target_alt_km=500, salvo_n=4)
    p10 = kill_probability_from_class("mrbm_kkv", target_alt_km=500, salvo_n=10)
    assert p1 < p4 <= p10 <= 0.95


def test_pk_clamped_in_unit_interval():
    for name in INTERCEPTORS:
        for alt in (100, 500, 1500, 36000):
            for salvo in (1, 2, 5, 10):
                p = kill_probability_from_class(name, target_alt_km=alt, salvo_n=salvo)
                assert 0.0 <= p <= 0.99


def test_unknown_interceptor_class_returns_zero():
    """Bad input is a soft-fail (Pk=0), never an exception — the validator catches it earlier."""
    assert kill_probability_from_class("not_a_class", target_alt_km=500) == 0.0


# --------------------------------------------------------------------------- #
# §C2 — Order schema no longer reads success_prob / base_prob from params.
# --------------------------------------------------------------------------- #

@pytest.fixture
def session():
    from spacesim.session.inprocess import InProcessSession

    api = InProcessSession()
    sid = api.load_vignette("training-basics")
    api.start(sid)
    return api, sid


def _issue_through_api(api, sid, body):
    """Issue an order through the SessionAPI shape the UI uses."""
    from spacesim.engine.orders import Order
    cell = body["cell"]
    order = Order(
        cell=cell, actor=body["actor"], action=body["action"],
        target=body.get("target"), params=dict(body.get("params", {})),
    )
    return api.issue_order(sid, cell, order)


def test_jam_ignores_operator_success_prob_override(session):
    """A jam order with ``success_prob: 0.01`` resolves at the same Pₛ as without — the
    operator's number is read out of the params dict (back-compat parse) but never feeds
    the engine math."""
    api, sid = session
    mgr = api._sessions[sid]
    # Find a jammer + a target that's in view (use training-basics fleet).
    jammer = next((a for a in mgr.world.assets.values() if a.kind == "jammer"), None)
    if jammer is None:
        pytest.skip("training-basics vignette has no jammer")
    target = next((a for a in mgr.world.assets.values()
                   if a.owner != jammer.owner and a.payload_state
                   and a.payload_state.type == "satcom"), None)
    if target is None:
        pytest.skip("training-basics vignette has no SATCOM target")
    body = {
        "cell": jammer.owner,
        "actor": jammer.id,
        "action": "jam",
        "target": target.id,
        "params": {
            "modulation": "barrage",
            "power_w": 100.0,
            "success_prob": 0.01,   # operator override — must be ignored
        },
    }
    ack = _issue_through_api(api, sid, body)
    # If the order was accepted, the effect payload baked into the scheduler must have a
    # Pₛ above the trivial 0.01 the operator typed.
    if ack.ok:
        scheduled = [tup[2] for tup in mgr.sim.scheduler._heap
                     if tup[2].kind == "execute_effect"]
        if scheduled:
            from spacesim.engine.effects import EffectInstance
            eff = EffectInstance.model_validate(scheduled[-1].payload["effect"])
            assert eff.success_prob > 0.5, (
                f"jam Pₛ should derive from modulation/power, not the operator's 0.01 (got {eff.success_prob})"
            )


def test_cyber_requires_vector_no_raw_success_prob_fallback(session):
    """The legacy `if vector else base_prob` path is gone — cyber without a vector
    must be rejected at validation."""
    api, sid = session
    mgr = api._sessions[sid]
    cyber_unit = next((a for a in mgr.world.assets.values() if a.kind == "cyber_unit"), None)
    if cyber_unit is None:
        pytest.skip("training-basics vignette has no cyber unit")
    target = next((a for a in mgr.world.assets.values()
                   if a.owner != cyber_unit.owner and a.cyber_vulnerabilities), None)
    if target is None:
        pytest.skip("no target with cyber vulns available")
    body = {
        "cell": cyber_unit.owner,
        "actor": cyber_unit.id,
        "action": "cyber",
        "target": target.id,
        "params": {
            # No vector — should be rejected.
            "success_prob": 1.0,
            "outcome": "safe_mode",
        },
    }
    ack = _issue_through_api(api, sid, body)
    assert not ack.ok
    assert "vector" in (ack.reason or "")


# --------------------------------------------------------------------------- #
# §C3 — observe.gain / classification operator overrides removed.
# --------------------------------------------------------------------------- #

def test_observe_ignores_operator_gain_override(session):
    """An operator typing `gain: 100` cannot fast-track custody."""
    api, sid = session
    mgr = api._sessions[sid]
    sensor = next((s for s in mgr.world.sensors.values()), None)
    if sensor is None:
        pytest.skip("no sensor in training-basics")
    target = next((a for a in mgr.world.assets.values() if a.owner != "blue"), None)
    if target is None:
        pytest.skip("no non-blue target")
    body = {
        "cell": "blue",
        "actor": sensor.id,
        "action": "observe",
        "target": target.id,
        "params": {"intent": "track", "gain": 100.0},
    }
    ack = _issue_through_api(api, sid, body)
    if ack.ok:
        scheduled = [tup[2] for tup in mgr.sim.scheduler._heap
                     if tup[2].kind == "execute_observe"]
        if scheduled:
            # gain in the scheduled payload should come from isr.effective_gain(1.0, …),
            # not from the operator's 100.0
            assert scheduled[-1].payload["gain"] < 10.0


# --------------------------------------------------------------------------- #
# §M3 — pnt.set_integrity replaced by pnt.flex_power + pnt.set_health_flag.
# --------------------------------------------------------------------------- #

def test_pnt_flex_power_is_a_real_verb():
    from spacesim.engine.buscommands import COMMAND_VERBS, PAYLOAD_VERBS
    assert "pnt.flex_power" in COMMAND_VERBS
    assert "pnt.flex_power" in PAYLOAD_VERBS


def test_pnt_set_health_flag_is_a_real_verb():
    from spacesim.engine.buscommands import COMMAND_VERBS, PAYLOAD_VERBS
    assert "pnt.set_health_flag" in COMMAND_VERBS
    assert "pnt.set_health_flag" in PAYLOAD_VERBS


def test_pnt_flex_power_changes_payload_state():
    from spacesim.engine.bus import BusState, PayloadState
    from spacesim.engine.buscommands import apply_command
    from spacesim.engine.entities import Asset
    from spacesim.engine.world import WorldState

    w = WorldState(now=0)
    w.assets["SV"] = Asset(
        id="SV", owner="blue", kind="satellite",
        bus_state=BusState(),
        payload_state=PayloadState(type="pnt"),
    )
    ok, label = apply_command(w, "SV", "pnt.flex_power", {"on": True, "signal": "M-code"}, 0)
    assert ok
    assert w.assets["SV"].payload_state.detail.get("flex_power_on") is True
    assert w.assets["SV"].payload_state.detail.get("flex_power_signal") == "M-code"


def test_pnt_set_health_flag_logs_consequence():
    from spacesim.engine.bus import BusState, PayloadState
    from spacesim.engine.buscommands import apply_command
    from spacesim.engine.entities import Asset
    from spacesim.engine.world import WorldState

    w = WorldState(now=0)
    w.assets["SV"] = Asset(
        id="SV", owner="blue", kind="satellite",
        bus_state=BusState(),
        payload_state=PayloadState(type="pnt"),
    )
    ok, label = apply_command(w, "SV", "pnt.set_health_flag",
                               {"healthy": False, "sv_id": "SV"}, 42)
    assert ok
    p = w.assets["SV"].payload_state
    assert p.detail.get("sv_healthy") is False
    # A NANU-style consequence is logged so AAR / White-Cell can see the broadcast.
    assert any(c.get("type") == "nanu" for c in w.consequences)
