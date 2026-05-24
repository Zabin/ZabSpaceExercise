"""End-to-end orders: queue-to-window, jam denial, kinetic strike, cyber-outside-pass, custody.

This is the Phase-3 "done when" integration check, driven headlessly through a Simulation +
OrderSystem (no GUI / session layer yet).
"""

from __future__ import annotations

import numpy as np

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
    order = osys.issue(Order(cell="red", actor="JAM", action="jam", target="SAT", params={"success_prob": 1.0}))
    assert order.status == "queued"
    assert order.earliest_window is not None
    start, end = order.earliest_window
    assert start > 0  # genuinely queued to a later pass, not executed instantly
    assert not world.active_effects  # nothing happens until the window arrives

    sim.advance_to(start + 1)        # window opened, jam fired
    assert world.effect_log and world.effect_log[-1]["achieved"] == "deny"
    assert is_link_denied(world, "SAT", start + 1)
    assert not is_link_denied(world, "SAT", end + minutes(5))  # link recovers after the window


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
    order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT", params={"success_prob": 1.0}))
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[0] + 1)
    assert world.assets["RSAT"].health == "destroyed"
    assert world.debris and world.consequences
    assert world.assets["INT"].resources.ammo == 0  # ammo consumed


def test_cyber_resolves_outside_any_pass_window():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(
        id="SAT", owner="blue", kind="satellite", orbit=sat, cyber_posture="low",
        cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": False}],
    )
    world.assets["CYB"] = Asset(id="CYB", owner="red", kind="cyber_unit")  # no location, no LOS

    sim, osys = _sim_with(world, roe={"cyber_authorized": True})
    order = osys.issue(Order(
        cell="red", actor="CYB", action="cyber", target="SAT",
        params={"access_vector": "ground_modem", "success_prob": 1.0, "outcome": "deny", "persistence_s": 3600},
    ))
    assert order.status == "queued" and order.earliest_window is None  # not window-gated

    sim.advance_to(minutes(1))
    assert world.effect_log[-1]["success"] is True
    assert is_link_denied(world, "SAT", minutes(30))  # effect persists with no pass involved


def test_observe_order_resets_custody_at_the_collection_window():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=sat)
    world.sensors["RDR"] = Sensor(id="RDR", owner="blue", kind="ground_radar", location=_subpoint(sat, 0))
    # Stale track that has decayed away.
    world.tracks.append(Track(object="TGT", owner="blue", last_observation=0, confidence=0.1, characterized=False))

    sim, osys = _sim_with(world)
    order = osys.issue(Order(cell="blue", actor="RDR", action="observe", target="TGT", params={"quality": 1.0}))
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[0] + 1)
    tr = world.track_for("blue", "TGT")
    assert tr.characterized and tr.current_confidence(world.now) > 0.9  # custody restored


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


def test_engage_sequence_replays_byte_identical():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=1.0, characterized=True))

    sim, osys = _sim_with(world, roe={"kinetic_authorized": True}, seed=42)
    order = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT",
                             params={"success_prob": 0.75}))  # probabilistic → exercises the RNG
    sim.advance_to(order.earliest_window[1] + minutes(1))
    live = sim.world.model_dump_json()
    assert sim.replay().model_dump_json() == live
