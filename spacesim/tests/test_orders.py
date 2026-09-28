"""End-to-end orders: queue-to-window, jam denial, kinetic strike, cyber-outside-pass, custody.

This is the Phase-3 "done when" integration check, driven headlessly through a Simulation +
OrderSystem (no GUI / session layer yet).
"""

from __future__ import annotations

import numpy as np
import pytest

from spacesim.engine.custody import Track
from spacesim.engine.effects import is_link_denied
from spacesim.engine.entities import Asset, AssetResources, Sensor
from spacesim.engine.geometry import (
    R_EARTH_EQ,
    ecef_to_geodetic,
    eci_to_ecef,
)
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simtime import hours, minutes
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState

PROP = ModeratePropagator()


def _leo(ta: float = 0.0) -> OrbitState:
    return OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=ta, epoch=0)


def _subpoint(orbit: OrbitState, t: int):
    r, _ = PROP.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    g.alt_m = 0.0
    return g


def _sim_with(world: WorldState, roe=None, seed=7) -> tuple[Simulation, OrderSystem]:
    # IP-1172: OrderSystem.roe is now always cell-keyed ({"blue": {...}, "red": {...}}).
    # A flat dict (this file's pre-IP-1172 convenience shape) is mirrored to both cells,
    # matching content/vignette.py's own legacy-parameter fallback semantics.
    if roe is not None and "blue" not in roe and "red" not in roe:
        roe = {"blue": dict(roe), "red": dict(roe)}
    sim = Simulation(world, seed=seed)
    osys = OrderSystem(sim, roe=roe)
    return sim, osys


def test_order_queues_to_a_future_window_then_jam_denies_link_during_it():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=sat)
    # Jammer under the sat's sub-point 40 min from now → first jam window is in the future.
    world.assets["JAM"] = Asset(id="JAM", owner="red", kind="jammer", location=_subpoint(sat, minutes(40)))

    sim, osys = _sim_with(world)
    order = osys.issue(Order(cell="red", actor="JAM", action="jam", target="SAT", params={"modulation": "barrage", "power_w": 200.0}))
    assert order.status == "queued"
    assert order.earliest_window is not None
    start, end = order.earliest_window
    assert start > 0  # genuinely queued to a later pass, not executed instantly
    assert not world.active_effects  # nothing happens until the window arrives

    sim.advance_to(start + 1)        # window opened, jam fired
    assert world.effect_log and world.effect_log[-1]["achieved"] == "deny"
    assert is_link_denied(world, "SAT", start + 1)
    assert not is_link_denied(world, "SAT", end + minutes(5))  # link recovers after the window


def test_jam_link_target_scopes_which_link_is_denied():
    """AUDIT-2026-06-COMMANDS.md §N9 — jam.link_target ∈ {uplink, downlink, crosslink}.

    CCS Block 10.2 is uplink-only by design: an uplink-scoped jam must not deny the
    downlink action, and a downlink-scoped jam must not register as an uplink denial.
    Defaults to "downlink" for back-compat with callers that omit the param.
    """
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=sat)
    world.assets["JAM"] = Asset(id="JAM", owner="red", kind="jammer", location=_subpoint(sat, minutes(40)))

    sim, osys = _sim_with(world)
    order = osys.issue(Order(cell="red", actor="JAM", action="jam", target="SAT",
                              params={"modulation": "barrage", "power_w": 200.0, "link_target": "uplink"}))
    start, _end = order.earliest_window
    sim.advance_to(start + 1)
    assert world.active_effects and world.active_effects[-1].link_target == "uplink"
    assert is_link_denied(world, "SAT", start + 1, link="uplink")
    assert not is_link_denied(world, "SAT", start + 1, link="downlink")


def test_jam_link_target_defaults_to_downlink():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=sat)
    world.assets["JAM"] = Asset(id="JAM", owner="red", kind="jammer", location=_subpoint(sat, minutes(40)))

    sim, osys = _sim_with(world)
    order = osys.issue(Order(cell="red", actor="JAM", action="jam", target="SAT",
                              params={"modulation": "barrage", "power_w": 200.0}))
    start, _end = order.earliest_window
    sim.advance_to(start + 1)
    assert world.active_effects[-1].link_target == "downlink"
    assert is_link_denied(world, "SAT", start + 1, link="downlink")


def test_kinetic_engage_requires_track_and_roe_then_spawns_debris():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(
        id="INT", owner="blue", kind="interceptor",
        location=_subpoint(sat, 0), resources=AssetResources(ammo=1),
    )

    # Without ROE → rejected even before considering geometry.
    sim, osys = _sim_with(world, roe={"kinetic_authorized": False})
    rej = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert rej.status == "rejected" and rej.fail_reason == "roe_kinetic_not_authorized"

    # With ROE but no weapons-quality track → rejected.
    sim, osys = _sim_with(world, roe={"kinetic_authorized": True})
    rej2 = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert rej2.status == "rejected" and rej2.fail_reason == "no_weapons_quality_track"

    # With a fresh, characterized track → queues and, on execution, destroys + spawns debris.
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))
    sim, osys = _sim_with(world, roe={"kinetic_authorized": True})
    order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT", params={"interceptor_class": "mrbm_kkv"}))
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[0] + 1)
    assert world.assets["RSAT"].health == "destroyed"
    assert world.debris and world.consequences
    assert world.assets["INT"].resources.ammo == 0  # ammo consumed


def test_gated_order_held_pending_until_decision_recorded():
    """IP-1270 (FR-3430) — an order matching a declared gating rule does not execute until a
    decision is recorded; the EventLog shows the request, decision, and elapsed time."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))
    sim = Simulation(world, seed=7)
    roe = {"blue": {"kinetic_authorized": True}, "red": {"kinetic_authorized": True}}
    gating_rules = [{"action_type": "engage", "required_role": "white"}]
    osys = OrderSystem(sim, roe=roe, gating_rules=gating_rules)

    order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert order.status == "pending_approval"
    sim.advance_to(sim.clock.now + 10_000_000)
    assert world.assets["RSAT"].health == "nominal"  # never executed while pending

    requests = [e for e in sim.eventlog.entries if e.kind == "effect_gate_request"]
    assert len(requests) == 1 and requests[0].payload["order_id"] == order.id

    ok, reason = osys.decide_gated_order("white", order.id, approve=True)
    assert ok, reason
    decisions = [e for e in sim.eventlog.entries if e.kind == "effect_gate_decision"]
    assert len(decisions) == 1 and decisions[0].payload["approved"] is True
    assert decisions[0].payload["elapsed_us"] >= 0
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[0] + 1)
    assert world.assets["RSAT"].health == "destroyed"


def test_gated_order_denied_is_rejected():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))
    sim = Simulation(world, seed=7)
    roe = {"blue": {"kinetic_authorized": True}, "red": {"kinetic_authorized": True}}
    osys = OrderSystem(sim, roe=roe, gating_rules=[{"action_type": "engage", "required_role": "white"}])
    order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    ok, reason = osys.decide_gated_order("white", order.id, approve=False)
    assert ok, reason
    assert order.status == "rejected" and order.fail_reason == "gate_denied"


def test_gated_order_decision_requires_the_designated_controller_role():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))
    sim = Simulation(world, seed=7)
    roe = {"blue": {"kinetic_authorized": True}, "red": {"kinetic_authorized": True}}
    osys = OrderSystem(sim, roe=roe, gating_rules=[{"action_type": "engage", "required_role": "white"}])
    order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    ok, reason = osys.decide_gated_order("blue", order.id, approve=True)
    assert not ok and reason == "not_controller"
    assert order.status == "pending_approval"


def test_unmatched_order_is_unaffected_by_gating_rules():
    """Regression: an order not matching any gating rule executes per its existing gates."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=sat)
    world.sensors["RDR"] = Sensor(id="RDR", owner="blue", kind="ground_radar", location=_subpoint(sat, 0))
    sim = Simulation(world, seed=7)
    osys = OrderSystem(sim, gating_rules=[{"action_type": "engage", "required_role": "white"}])
    order = osys.issue(Order(cell="blue", actor="RDR", action="observe", target="TGT",
                             params={"intent": "characterize"}))
    assert order.status == "queued"


def test_live_roe_change_affects_orders_after_but_not_before():
    """IP-1270 (FR-3440) — a controller-issued ROE change at simulated time T changes the
    evaluated ROE value for orders issued after T but not before T; replay reproduces the
    identical sequence of ROE states."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=2))
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))
    sim = Simulation(world, seed=7)
    osys = OrderSystem(sim, roe={"blue": {"kinetic_authorized": False}})

    before = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert before.status == "rejected" and before.fail_reason == "roe_kinetic_not_authorized"

    sim.advance_to(1_000_000)  # distinct sim time so the ROE change's timestamp differs from `before`'s
    ok, reason = osys.issue_roe_change("white", "blue", "kinetic_authorized", True)
    assert ok, reason
    after = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert after.status == "queued"

    # Replay reproduces the identical ROE-state sequence: rebuild from the eventlog and confirm
    # the same two order-issuance decisions would be made (the roe_change entry replays too).
    sim.advance_to(after.earliest_window[0] + 1)
    sim.rewind_to(after.earliest_window[0] + 1)
    assert osys.roe.get("blue", {}).get("kinetic_authorized") is True  # replayed roe_change cache
    assert osys._effective_roe("blue", before.issued_at).get("kinetic_authorized") is False
    assert osys._effective_roe("blue", after.issued_at).get("kinetic_authorized") is True


def test_only_controller_role_may_issue_a_roe_change():
    world = WorldState(now=0)
    sim = Simulation(world, seed=7)
    osys = OrderSystem(sim)
    ok, reason = osys.issue_roe_change("blue", "blue", "kinetic_authorized", True)
    assert not ok and reason == "not_controller"


def test_per_cell_roe_kinetic_divergent_gates_independently():
    # IP-1172 (FR-3420) — Blue authorized, Red not; each cell's order-issuance is independent.
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["BSAT"] = Asset(id="BSAT", owner="blue", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(
        id="INT", owner="blue", kind="interceptor",
        location=_subpoint(sat, 0), resources=AssetResources(ammo=1),
    )
    world.assets["RINT"] = Asset(
        id="RINT", owner="red", kind="interceptor",
        location=_subpoint(sat, 0), resources=AssetResources(ammo=1),
    )
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))
    world.tracks.append(Track(object="BSAT", owner="red", last_observation=0, confidence=1.0, characterized=True))

    sim, osys = _sim_with(world, roe={"blue": {"kinetic_authorized": True}, "red": {"kinetic_authorized": False}})

    blue_order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT",
                                   params={"interceptor_class": "mrbm_kkv"}))
    assert blue_order.status == "queued"

    red_order = osys.issue(Order(cell="red", actor="RINT", action="engage", target="BSAT",
                                  params={"interceptor_class": "mrbm_kkv"}))
    assert red_order.status == "rejected" and red_order.fail_reason == "roe_kinetic_not_authorized"


def test_per_cell_roe_cyber_divergent_gates_independently():
    # IP-1172 (FR-3420) — mirror image of the kinetic case, for cyber ROE.
    world = WorldState(now=0)
    world.assets["BSAT"] = Asset(
        id="BSAT", owner="blue", kind="satellite", cyber_posture="low",
        cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": False}],
    )
    world.assets["RSAT"] = Asset(
        id="RSAT", owner="red", kind="satellite", cyber_posture="low",
        cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": False}],
    )
    world.assets["RCYB"] = Asset(id="RCYB", owner="red", kind="cyber_unit")
    world.assets["BCYB"] = Asset(id="BCYB", owner="blue", kind="cyber_unit")

    sim, osys = _sim_with(world, roe={"red": {"cyber_authorized": True}, "blue": {"cyber_authorized": False}})

    red_order = osys.issue(Order(cell="red", actor="RCYB", action="cyber", target="BSAT",
                                  params={"vector": "ground_modem", "payload": "seize_c2"}))
    assert red_order.status == "queued"

    blue_order = osys.issue(Order(cell="blue", actor="BCYB", action="cyber", target="RSAT",
                                   params={"vector": "ground_modem", "payload": "seize_c2"}))
    assert blue_order.status == "rejected" and blue_order.fail_reason == "roe_cyber_not_authorized"


def test_cyber_resolves_outside_any_pass_window():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(
        id="SAT", owner="blue", kind="satellite", orbit=sat, cyber_posture="low",
        cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": False}],
    )
    world.assets["CYB"] = Asset(id="CYB", owner="red", kind="cyber_unit")  # no location, no LOS

    sim, osys = _sim_with(world, roe={"cyber_authorized": True})
    # Audit 2026-06 Commands §C2 — cyber now requires a vector + a payload. The `spoof`
    # payload sets intended_outcome=deceive, so the surviving active-effect carries the
    # deceive outcome (matches is_link_spoofed). The point of the test (cyber resolves
    # without a pass window) is preserved.
    order = osys.issue(Order(
        cell="red", actor="CYB", action="cyber", target="SAT",
        params={"vector": "ground_modem", "payload": "spoof", "persistence_s": 3600},
    ))
    assert order.status == "queued" and order.earliest_window is None  # not window-gated

    sim.advance_to(minutes(1))
    assert world.effect_log[-1]["success"] is True
    # The cyber effect produced an active reversible effect carrying the payload's
    # intended_outcome (spoof → deceive); the active-effect span persists across
    # advance(), proving cyber doesn't need a pass window to land or to keep landing.
    assert any(ae.target == "SAT" and ae.start <= minutes(30) <= ae.end
                for ae in world.active_effects)


def test_observe_order_resets_custody_at_the_collection_window():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=sat)
    world.sensors["RDR"] = Sensor(id="RDR", owner="blue", kind="ground_radar", location=_subpoint(sat, 0))
    # Stale track that has decayed away.
    world.tracks.append(Track(object="TGT", owner="blue", last_observation=0, confidence=0.1, characterized=False))

    sim, osys = _sim_with(world)
    order = osys.issue(Order(cell="blue", actor="RDR", action="observe", target="TGT",
                             params={"intent": "characterize"}))
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[0] + 1)
    tr = world.track_for("blue", "TGT")
    assert tr.characterized and tr.current_confidence(world.now) > 0.9  # custody restored


def test_cue_dependent_sensor_rejected_without_existing_track():
    """IP-1220 (FR-1640) — a requires_cue sensor's tasking is rejected against a target the
    tasking cell has no existing Track on."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=sat)
    world.sensors["RDR"] = Sensor(id="RDR", owner="blue", kind="ground_radar",
                                  location=_subpoint(sat, 0), requires_cue=True)
    sim, osys = _sim_with(world)
    order = osys.issue(Order(cell="blue", actor="RDR", action="observe", target="TGT",
                             params={"intent": "track"}))
    assert order.status == "rejected"
    assert order.fail_reason == "requires_cue"


def test_cue_dependent_sensor_accepted_with_existing_track():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=sat)
    world.sensors["RDR"] = Sensor(id="RDR", owner="blue", kind="ground_radar",
                                  location=_subpoint(sat, 0), requires_cue=True)
    world.tracks.append(Track(object="TGT", owner="blue", last_observation=0, confidence=0.5))
    sim, osys = _sim_with(world)
    order = osys.issue(Order(cell="blue", actor="RDR", action="observe", target="TGT",
                             params={"intent": "track"}))
    assert order.status == "queued"


def test_cue_dependent_dry_run_also_rejects():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=sat)
    world.sensors["RDR"] = Sensor(id="RDR", owner="blue", kind="ground_radar",
                                  location=_subpoint(sat, 0), requires_cue=True)
    sim, osys = _sim_with(world)
    order = osys.dry_run(Order(cell="blue", actor="RDR", action="observe", target="TGT",
                               params={"intent": "track"}))
    assert order.status == "rejected"
    assert order.fail_reason == "requires_cue"


def test_maneuver_consumes_delta_v_and_changes_orbit():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(
        id="SAT", owner="blue", kind="satellite", orbit=sat, resources=AssetResources(delta_v_ms=150.0),
    )
    world.assets["GS"] = Asset(id="GS", owner="blue", kind="ground_station", location=_subpoint(sat, 0))

    sim, osys = _sim_with(world)
    _, v = PROP.rv(sat, 0)
    dv = list(30.0 * v / np.linalg.norm(v))  # 30 m/s prograde
    order = osys.issue(Order(cell="blue", actor="SAT", action="maneuver", target=None,
                             params={"dv": dv, "via": "GS"}))
    assert order.status == "queued"
    a_before = world.assets["SAT"].orbit.a_m
    sim.advance_to(order.earliest_window[0] + 1)
    assert world.assets["SAT"].orbit.a_m > a_before
    assert abs(world.assets["SAT"].resources.delta_v_ms - 120.0) < 1e-6

    # Over-budget maneuver is rejected at validation.
    big = list(500.0 * v / np.linalg.norm(v))
    rej = osys.issue(Order(cell="blue", actor="SAT", action="maneuver", params={"dv": big, "via": "GS"}))
    assert rej.status == "rejected" and rej.fail_reason == "insufficient_delta_v"


def test_maneuver_purpose_tag_carried_to_eventlog_and_blank_default():
    """IP-1250 (FR-1320) — an operator-supplied purpose_tag is carried through to the resulting
    EventLog entry; an omitted tag is accepted and recorded as ""."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(
        id="SAT", owner="blue", kind="satellite", orbit=sat, resources=AssetResources(delta_v_ms=150.0),
    )
    world.assets["GS"] = Asset(id="GS", owner="blue", kind="ground_station", location=_subpoint(sat, 0))
    sim, osys = _sim_with(world)
    _, v = PROP.rv(sat, 0)
    dv = list(10.0 * v / np.linalg.norm(v))

    order = osys.issue(Order(cell="blue", actor="SAT", action="maneuver",
                             params={"dv": dv, "via": "GS", "purpose_tag": "station-keeping"}))
    sim.advance_to(order.earliest_window[0] + 1)
    entries = [e for e in sim.eventlog.entries if e.kind == "execute_maneuver"]
    assert len(entries) == 1
    assert entries[0].payload["purpose_tag"] == "station-keeping"
    assert entries[0].payload["applied"] is True
    assert entries[0].payload["remaining_delta_v_ms"] == pytest.approx(140.0, abs=1e-6)

    order2 = osys.issue(Order(cell="blue", actor="SAT", action="maneuver",
                              params={"dv": dv, "via": "GS"}))  # no purpose_tag
    sim.advance_to(order2.earliest_window[0] + 1)
    entries2 = [e for e in sim.eventlog.entries if e.kind == "execute_maneuver"]
    assert entries2[-1].payload["purpose_tag"] == ""


def test_engage_sequence_replays_byte_identical():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))

    sim, osys = _sim_with(world, roe={"kinetic_authorized": True}, seed=42)
    # Audit 2026-06 Commands §C2/M2 — Pₖ is class-derived (mrbm_kkv ≈ 0.7 at 500 km LEO,
    # cf. open-source SC-19/FY-1C scoring) so the RNG-replay path still exercises a
    # probabilistic branch rather than a guaranteed success.
    order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT",
                             params={"interceptor_class": "mrbm_kkv"}))
    sim.advance_to(order.earliest_window[1] + minutes(1))
    live = sim.world.model_dump_json()
    assert sim.replay().model_dump_json() == live


# -- IP-2010 v1.1 (BL-0002) — custody_confidence_at_decision capture -------------------------

def test_custody_confidence_at_decision_captured_for_targeted_actions():
    """engage/observe orders against an owned track record the live confidence at issue time —
    the same number scene.py's RenderTrack.confidence already surfaces to the operator."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    track = Track(object="RSAT", owner="blue", last_observation=0, confidence=0.9, characterized=True)
    world.tracks.append(track)

    sim, osys = _sim_with(world, roe={"kinetic_authorized": True})
    # Advance the clock a little first so current_confidence() has actually decayed from 0.9 —
    # proves the captured value is a live read, not the raw stored `confidence` field — while
    # staying inside the engage weapons-quality gate (>= 0.8) so the order is still accepted.
    sim.clock.now = minutes(1)
    world.now = minutes(1)
    expected = track.current_confidence(minutes(1))
    order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT",
                             params={"interceptor_class": "mrbm_kkv"}))
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[1] + minutes(1))
    entry = next(e for e in sim.eventlog.entries if e.kind == "execute_effect")
    assert entry.payload["custody_confidence_at_decision"] == round(expected, 3)


def test_custody_confidence_at_decision_none_without_target_or_track():
    """downlink (no target concept) and an engage-like target with no owned track both record
    None — the field must never be silently fabricated."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=sat)
    world.assets["GS"] = Asset(id="GS", owner="blue", kind="ground_station", location=_subpoint(sat, 0))

    sim, osys = _sim_with(world)
    order = osys.issue(Order(cell="blue", actor="SAT", action="downlink", params={"via": "GS"}))
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[0] + 1)
    entry = next(e for e in sim.eventlog.entries if e.kind == "execute_downlink")
    assert entry.payload["custody_confidence_at_decision"] is None


def test_dry_run_never_captures_custody_confidence():
    """dry_run() must stay a zero-footprint preview — it never reaches _exec_payload at all,
    so it can't touch the new capture step either (no eventlog entry is produced to check)."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))

    sim, osys = _sim_with(world, roe={"kinetic_authorized": True})
    preview = osys.dry_run(Order(cell="blue", actor="INT", action="engage", target="RSAT",
                                 params={"interceptor_class": "mrbm_kkv"}))
    assert preview.status == "queued"
    assert not sim.eventlog.entries       # zero eventlog writes
    assert not osys.orders                # zero registry writes
    assert not osys._sensor_bookings and not osys._pass_bookings   # zero booking writes


def test_custody_confidence_at_decision_replays_byte_identically():
    """The captured value is stored event-log data, not recomputed on replay — a dedicated
    regression guard alongside test_engage_sequence_replays_byte_identical above."""
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.85, characterized=True))

    sim, osys = _sim_with(world, roe={"kinetic_authorized": True}, seed=11)
    osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT",
                     params={"interceptor_class": "mrbm_kkv"}))
    order = osys.orders[next(iter(osys.orders))]
    sim.advance_to(order.earliest_window[1] + minutes(1))
    before = [e.payload.get("custody_confidence_at_decision") for e in sim.eventlog.entries]
    live = sim.world.model_dump_json()

    replayed_sim = sim.replay()
    after = [e.payload.get("custody_confidence_at_decision") for e in sim.eventlog.entries]
    assert replayed_sim.model_dump_json() == live
    assert before == after
