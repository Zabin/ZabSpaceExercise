"""IP-1085 (FR-1440) — a jam denies a command only on the delivery path it actually covers.

``_h_maneuver``/``_h_command`` used to test an ``uplink`` jam on the actor whatever the order's
delivery path: a stored program (which runs onboard) was denied, and a relayed command was never
tested against the crosslink. The planned path now travels in the execution payload and one shared
rule decides:

    ground_uplink  -> denied by an active ``uplink`` jam on the actor
    isl_relay      -> denied by an active ``crosslink`` jam on the actor or on the relay
    stored_program -> never denied by a link jam

A payload without the new keys keeps the pre-fix rule (an ``uplink`` jam on the actor), so every
recorded log replays unchanged.
"""

from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient

from spacesim.engine.bus import BusState
from spacesim.engine.effects import ActiveEffect, is_link_denied
from spacesim.engine.entities import Asset, AssetResources
from spacesim.engine.geometry import GeoPoint, R_EARTH_EQ, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simtime import minutes
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState
from spacesim.ui_web.server import app

PROP = ModeratePropagator()
PATHS = ["ground_uplink", "isl_relay", "stored_program"]
JAMS = ["none", "uplink_actor", "crosslink_actor", "crosslink_relay", "downlink_actor", "unrelated"]
FAILS = {("ground_uplink", "uplink_actor"), ("isl_relay", "crosslink_actor"), ("isl_relay", "crosslink_relay")}
FOREVER = 10 ** 15


def _leo():
    return OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=0.0, epoch=0)


def _subpoint(orbit, t):
    r, _ = PROP.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    g.alt_m = 0.0
    return g


def _geo_relay():
    return Asset(id="RELAY", owner="blue", kind="satellite", isl_capable=True,
                 orbit=OrbitState(a_m=42164e3, e=0.0, i_deg=0.0, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0))


def _build(path, jammers=False):
    """One small world per delivery path; returns (world, sim, osys, params)."""
    world = WorldState(now=0)
    sat = _leo()
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=sat,
                                resources=AssetResources(delta_v_ms=150.0), bus_state=BusState())
    world.assets["UNREL"] = Asset(id="UNREL", owner="blue", kind="satellite", orbit=_leo())
    if path == "ground_uplink":
        world.assets["GS"] = Asset(id="GS", owner="blue", kind="ground_station", location=_subpoint(sat, 0))
        params = {"via": "GS"}
    elif path == "isl_relay":
        world.assets["FAR-GS"] = Asset(id="FAR-GS", owner="blue", kind="ground_station",
                                       location=GeoPoint(lat_deg=-60.0, lon_deg=-90.0))
        world.assets["RELAY"] = _geo_relay()
        params = {"via": "FAR-GS"}
    else:
        params = {"stored_at": minutes(5)}
    if jammers:   # added before Simulation() so the replay baseline carries them
        world.assets["JAM"] = Asset(id="JAM", owner="red", kind="jammer", location=_subpoint(sat, 0))
        if path == "isl_relay":
            world.assets["JAM2"] = Asset(id="JAM2", owner="red", kind="jammer",
                                         location=_subpoint(world.assets["RELAY"].orbit, 0))
    sim = Simulation(world, seed=7)
    return world, sim, OrderSystem(sim), params


def _order(kind, params):
    if kind == "maneuver":
        _, v = PROP.rv(_leo(), 0)
        dv = list(10.0 * v / np.linalg.norm(v))
        return Order(cell="blue", actor="SAT", action="maneuver", params={"dv": dv, **params})
    return Order(cell="blue", actor="SAT", action="command", params={"verb": "adcs.set_mode", "mode": "slew", **params})


def _jam(world, jam, exec_t, *, start=None, end=None):
    target = {"uplink_actor": "SAT", "crosslink_actor": "SAT", "crosslink_relay": "RELAY",
              "downlink_actor": "SAT", "unrelated": "UNREL"}[jam]
    link = {"uplink_actor": "uplink", "crosslink_actor": "crosslink", "crosslink_relay": "crosslink",
            "downlink_actor": "downlink", "unrelated": "uplink"}[jam]
    world.active_effects.append(ActiveEffect(
        target=target, outcome="deny", link_target=link,
        start=exec_t - 1 if start is None else start, end=exec_t + 1 if end is None else end))


def _unchanged(world, kind):
    if kind == "maneuver":
        return (world.assets["SAT"].orbit.a_m == _leo().a_m
                and world.assets["SAT"].resources.delta_v_ms == pytest.approx(150.0))
    return world.assets["SAT"].bus_state.attitude.mode == "nominal"


def _applied(world, kind):
    if kind == "maneuver":
        return (world.assets["SAT"].orbit.a_m != _leo().a_m
                and world.assets["SAT"].resources.delta_v_ms == pytest.approx(140.0))
    return world.assets["SAT"].bus_state.attitude.mode == "slew"


def _run(kind, path, jam, **jamkw):
    world, sim, osys, params = _build(path)
    order = osys.issue(_order(kind, params))
    assert order.status == "queued", order.fail_reason
    assert order.delivery_path == path
    t = order.earliest_window[0]
    if jam != "none":
        _jam(world, jam, t, **jamkw)
    sim.advance_to(t + 1)
    return world, sim, osys, order, t


# --------------------------------------------------------------------------- #
# The matrix: 3 paths x 6 jam conditions x {maneuver, command}
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1440")
@pytest.mark.parametrize("kind", ["maneuver", "command"])
@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("jam", JAMS)
def test_jam_denies_only_the_path_it_covers(kind, path, jam):
    world, _sim, _osys, _order_, _t = _run(kind, path, jam)
    if (path, jam) in FAILS:
        assert _unchanged(world, kind)
        rec = world.effect_log[-1]
        assert rec["achieved"] == "jammed" and rec["success"] is False
        assert rec["path"] == f"{path}:{'uplink' if path == 'ground_uplink' else 'crosslink'}"
    else:
        assert _applied(world, kind)
        assert not any(r.get("achieved") == "jammed" for r in world.effect_log)


# --------------------------------------------------------------------------- #
# Timing: inclusive bounds of the jam window
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1440")
@pytest.mark.parametrize("kind", ["maneuver", "command"])
@pytest.mark.parametrize("path,jam", [("ground_uplink", "uplink_actor"), ("isl_relay", "crosslink_actor"),
                                      ("isl_relay", "crosslink_relay")])
def test_jam_window_bounds_pin_the_boundary_instants(kind, path, jam):
    # Inclusive at both ends: a jam ending exactly at, or starting exactly at, the execute instant denies.
    world, *_ = _run_with(kind, path, jam, lambda t: dict(start=t, end=t))
    assert not _applied(world, kind)
    # Expired one microsecond before, or starting one microsecond after, never denies.
    world, *_ = _run_with(kind, path, jam, lambda t: dict(start=t - 100, end=t - 1))
    assert _applied(world, kind)
    world, *_ = _run_with(kind, path, jam, lambda t: dict(start=t + 1, end=t + 100))
    assert _applied(world, kind)


def _run_with(kind, path, jam, bounds):
    world, sim, osys, params = _build(path)
    order = osys.issue(_order(kind, params))
    t = order.earliest_window[0]
    _jam(world, jam, t, **bounds(t))
    sim.advance_to(t + 1)
    return world, sim, osys, order, t


# --------------------------------------------------------------------------- #
# Footprint: an out-of-reach jam creates no effect, so denies nothing
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1440")
@pytest.mark.parametrize("kind", ["maneuver", "command"])
def test_a_jammer_out_of_reach_leaves_every_path_unaffected(kind):
    for path in PATHS:
        world, sim, osys, params = _build(path)
        world.assets["JAM"] = Asset(id="JAM", owner="red", kind="jammer",
                                    location=GeoPoint(lat_deg=-70.0, lon_deg=150.0))
        jam = osys.issue(Order(cell="red", actor="JAM", action="jam", target="SAT",
                               params={"modulation": "barrage", "power_w": 200.0, "link_target": "uplink"}))
        order = osys.issue(_order(kind, params))
        t = order.earliest_window[0]
        # Out of reach: the jam either has no window or one that opens after the command executes.
        assert jam.status == "rejected" or jam.earliest_window[0] > t + 1
        sim.advance_to(t + 1)
        assert _applied(world, kind) and not world.active_effects


@pytest.mark.verifies("FR-1440")
def test_a_real_in_reach_uplink_jam_denies_ground_uplink_only():
    """End to end through the real jam order (not a hand-built ActiveEffect)."""
    out = {}
    for path in ("ground_uplink", "stored_program"):
        world, sim, osys, params = _build(path)
        sat = world.assets["SAT"].orbit
        world.assets["JAM"] = Asset(id="JAM", owner="red", kind="jammer", location=_subpoint(sat, 0))
        jam = osys.issue(Order(cell="red", actor="JAM", action="jam", target="SAT",
                               params={"modulation": "barrage", "power_w": 200.0, "link_target": "uplink"}))
        assert jam.status == "queued"
        order = osys.issue(_order("maneuver", params))
        t = order.earliest_window[0]
        sim.advance_to(max(t, jam.earliest_window[0]) + 1)
        out[path] = (world.assets["SAT"].resources.delta_v_ms,
                     any(a.link_target == "uplink" for a in world.active_effects))
    assert out["ground_uplink"] == (pytest.approx(150.0), True)    # denied by the in-force uplink jam
    assert out["stored_program"][0] == pytest.approx(140.0)         # never denied


# --------------------------------------------------------------------------- #
# Payload keys, legacy payloads, replay
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1440")
@pytest.mark.parametrize("kind", ["maneuver", "command"])
@pytest.mark.parametrize("path", PATHS)
def test_delivery_path_and_relay_are_in_the_logged_payload(kind, path):
    _w, sim, _o, _order_, _t = _run(kind, path, "none")
    ev = [e for e in sim.eventlog.entries if e.kind == f"execute_{kind}"]
    assert len(ev) == 1
    assert ev[0].payload["delivery_path"] == path
    if path == "isl_relay":
        assert ev[0].payload["relay"] == "RELAY"
    else:
        assert ev[0].payload.get("relay") is None


@pytest.mark.verifies("FR-1440")
@pytest.mark.parametrize("kind", ["maneuver", "command"])
def test_a_payload_without_the_new_keys_keeps_the_pre_fix_uplink_rule(kind):
    """An event recorded before this package has no delivery_path: an uplink jam on the actor denies."""
    world, sim, osys, params = _build("ground_uplink")
    payload = ({"actor": "SAT", "dv": [0.0, 10.0, 0.0], "cost": 10.0, "purpose_tag": ""} if kind == "maneuver"
               else {"actor": "SAT", "verb": "adcs.set_mode", "params": {"mode": "slew"}})
    t = minutes(3)
    _jam(world, "uplink_actor", t)
    sim.schedule(t, f"execute_{kind}", payload, actor="blue")
    sim.advance_to(t + 1)
    assert world.effect_log[-1]["achieved"] == "jammed"
    assert "path" not in world.effect_log[-1]   # the legacy record is byte-identical to the pre-fix one
    assert _unchanged(world, kind)
    # ...and a crosslink jam alone does not (the legacy rule never consulted it).
    world, sim, osys, params = _build("ground_uplink")
    _jam(world, "crosslink_actor", t)
    sim.schedule(t, f"execute_{kind}", dict(payload), actor="blue")
    sim.advance_to(t + 1)
    assert _applied(world, kind)


@pytest.mark.verifies("FR-1440")
@pytest.mark.parametrize("kind", ["maneuver", "command"])
@pytest.mark.parametrize("path", PATHS)
def test_replay_equals_live_for_each_path_under_real_jams(kind, path):
    """Real jam orders (uplink on the actor; crosslink on the relay) so the effects are logged."""
    world, sim, osys, params = _build(path, jammers=True)
    osys.issue(Order(cell="red", actor="JAM", action="jam", target="SAT",
                     params={"modulation": "barrage", "power_w": 200.0, "link_target": "uplink"}))
    if path == "isl_relay":
        osys.issue(Order(cell="red", actor="JAM2", action="jam", target="RELAY",
                         params={"modulation": "barrage", "power_w": 200.0, "link_target": "crosslink"}))
    order = osys.issue(_order(kind, params))
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[0] + minutes(10))
    assert sim.replay().model_dump_json() == world.model_dump_json()


@pytest.mark.verifies("FR-1440", "FR-3110")
@pytest.mark.parametrize("kind", ["maneuver", "command"])
def test_dry_run_ignores_jams_for_all_three_paths(kind):
    for path in PATHS:
        world, sim, osys, params = _build(path)
        before = osys.dry_run(_order(kind, params))
        for jam in ("uplink_actor", "crosslink_actor", "crosslink_relay"):
            _jam(world, jam, 0, start=0, end=FOREVER)
        after = osys.dry_run(_order(kind, params))
        assert (after.status, after.delivery_path, after.earliest_window) == \
               (before.status, before.delivery_path, before.earliest_window)
        assert before.delivery_path == path


@pytest.mark.verifies("FR-1440")
def test_is_link_denied_semantics_unchanged():
    world = WorldState(now=0)
    world.active_effects.append(ActiveEffect(target="SAT", outcome="deny", link_target="downlink", start=0, end=10))
    assert is_link_denied(world, "SAT", 5, link="downlink")
    assert is_link_denied(world, "SAT", 5)
    assert not is_link_denied(world, "SAT", 5, link="uplink")
    assert not is_link_denied(world, "SAT", 11, link="downlink")


# --------------------------------------------------------------------------- #
# HTTP regression of the review's reproduction (H-2)
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1440")
def test_http_stored_program_maneuver_runs_under_an_uplink_jam():
    c = TestClient(app, raise_server_exceptions=False)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 5}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    jam = c.post(f"/api/sessions/{sid}/order", json={
        "cell": "red", "actor": "JAM-NORTH", "action": "jam", "target": "ISR-EO-1",
        "params": {"modulation": "barrage", "power_w": 200.0, "link_target": "uplink"}}).json()
    assert jam["ok"], jam
    j0, j1 = jam["earliest_window"]
    c.post(f"/api/sessions/{sid}/advance?cell=white", json={"t": j0 + 1})   # jam is now in force
    t_stored = j0 + 5_000_000
    assert j0 < t_stored < j1
    man = lambda **p: {"cell": "blue", "actor": "ISR-EO-1", "action": "maneuver",
                       "params": {"dv": [0.0, 1.0, 0.0], **p}}
    stored = c.post(f"/api/sessions/{sid}/order", json=man(stored_at=t_stored)).json()
    assert stored["ok"] and stored["delivery_path"] == "stored_program", stored
    c.post(f"/api/sessions/{sid}/advance?cell=white", json={"t": t_stored + 1})
    log = c.get(f"/api/sessions/{sid}/eventlog").json()
    ev = [e for e in log if e["kind"] == "execute_maneuver"]
    assert ev and ev[-1]["payload"]["applied"] is True
    assert ev[-1]["payload"]["delivery_path"] == "stored_program"
