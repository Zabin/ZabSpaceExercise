"""IP-1052 — order-parameter hardening (FR-3110, FR-1310, FR-1410, FR-1420; BL-0222).

``IP-1041`` closed the malformed-param class for ``observe`` only. Every other action had it:

- jam/engage/cyber numeric params passed ``dry_run`` but raised inside ``issue`` (HTTP 500), leaving
  a ghost ``queued`` order in ``OrderSystem.orders`` with no scheduled event;
- maneuver ``dv`` and command ``stored_at``/``verb``/``via`` raised on both paths (ghost ``draft``);
- ``power_w: "inf"`` drove the jammer's power to ``-inf``; ``dv: [NaN, 0, 0]`` made the orbit and
  delta-v ``NaN``; a wrong-length ``dv`` was queued and raised inside ``Simulation.advance_to``.

Malformed params are now rejected ``invalid_param`` by ``_validate`` (so ``dry_run`` and ``issue``
agree), an explicit ``null`` means absent, and the planners build the payload before committing
anything, so a failed plan leaves no booking, registry entry, ``queued`` status or event behind.
"""

from __future__ import annotations

import copy
import math

import pytest
from fastapi.testclient import TestClient

from spacesim.content.vignette import load_vignette
from spacesim.engine.custody import Track
from spacesim.engine.orders import Order, OrderSystem
from spacesim.session.manager import SessionManager
from spacesim.ui_web.server import app

NAN, INF = float("nan"), float("inf")


@pytest.fixture(scope="module")
def vignette():
    return load_vignette("leo-isr-denial")


@pytest.fixture
def mgr(vignette):
    m = SessionManager(vignette, seed=5)
    m.start()
    # Open the gates that would otherwise answer before the param check (ROE, weapons-quality).
    for cell in ("blue", "red"):
        m.osys._static_roe.setdefault(cell, {}).update(kinetic_authorized=True, cyber_authorized=True)
    m.world.tracks.append(Track(object="ISR-EO-1", owner="red", last_observation=m.world.now,
                                confidence=1.0, characterized=True))
    return m


def _jam(**p) -> Order:
    return Order(cell="red", actor="JAM-NORTH", action="jam", target="ISR-EO-1",
                 params={"modulation": "barrage", **p})


def _engage(**p) -> Order:
    return Order(cell="red", actor="RED-ASAT", action="engage", target="ISR-EO-1",
                 params={"interceptor_class": "mrbm_kkv", **p})


def _cyber(**p) -> Order:
    return Order(cell="red", actor="JAM-NORTH", action="cyber", target="ISR-EO-1",
                 params={"vector": "rf", **p})


def _maneuver(**p) -> Order:
    return Order(cell="blue", actor="ISR-EO-1", action="maneuver", params={"via": "GS-NORTH", **p})


def _command(**p) -> Order:
    return Order(cell="blue", actor="ISR-EO-1", action="command",
                 params={"verb": "eps.shed_load", "via": "GS-NORTH", **p})


def _downlink(**p) -> Order:
    return Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH", **p})


def _snapshot(osys: OrderSystem) -> tuple:
    return (dict(osys.orders), dict(osys._pass_bookings), dict(osys._order_pass),
            {k: list(v) for k, v in osys._sensor_bookings.items()}, dict(osys._order_sensor),
            len(osys.sim.scheduler._heap))


def _assert_refused_by_both(mgr, make) -> None:
    before = _snapshot(mgr.osys)
    dry = mgr.osys.dry_run(make())
    assert (dry.status, dry.fail_reason) == ("rejected", "invalid_param"), dry
    order = mgr.osys.issue(make())
    assert (order.status, order.fail_reason) == ("rejected", "invalid_param"), order
    after = _snapshot(mgr.osys)
    # Nothing booked or scheduled; the only registry change is the rejected order itself.
    assert after[1:] == before[1:]
    assert [o.status for o in after[0].values() if o.id not in before[0]] == ["rejected"]
    assert not any(o.status in ("queued", "draft") for o in after[0].values() if o.id not in before[0])


# --------------------------------------------------------------------------- #
# Tests 1-5 — every action's malformed params are refused by dry_run and issue alike
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("params", [
    {"power_w": "abc"}, {"power_w": "inf"}, {"power_w": NAN},
    {"bandwidth_hz": [1]}, {"victim_bandwidth_hz": {"a": 1}}, {"modulation": ["spot"]},
    {"link_target": 3},
])
def test_jam_params_refused(mgr, params):
    _assert_refused_by_both(mgr, lambda: _jam(**params))


@pytest.mark.parametrize("params", [
    {"salvo_n": "abc"}, {"salvo_n": "nan"}, {"salvo_n": INF}, {"salvo_n": NAN},
    {"interceptor_class": 3},
])
def test_engage_params_refused(mgr, params):
    _assert_refused_by_both(mgr, lambda: _engage(**params))


@pytest.mark.parametrize("params", [
    {"dwell_s": "abc"}, {"persistence_h": "inf"}, {"sm_susceptibility": [1]},
    {"persistence_bonus": NAN}, {"vector": ["x"]}, {"payload": 7}, {"segment": {"a": 1}},
])
def test_cyber_params_refused(mgr, params):
    _assert_refused_by_both(mgr, lambda: _cyber(**params))


@pytest.mark.parametrize("dv", ["abc", [1, "x", 0], [1, 2], [1, 2, 3, 4], [NAN, 0, 0], [0, INF, 0], 5])
def test_maneuver_dv_refused_and_state_untouched(mgr, dv):
    asset = mgr.world.assets["ISR-EO-1"]
    orbit_before, dv_before = asset.orbit.model_copy(), asset.resources.delta_v_ms
    _assert_refused_by_both(mgr, lambda: _maneuver(dv=dv))
    mgr.advance_to(mgr.sim.clock.now + 6 * 3600 * 1_000_000)   # past any would-be window; must not raise
    asset = mgr.world.assets["ISR-EO-1"]
    assert asset.resources.delta_v_ms == dv_before and math.isfinite(asset.resources.delta_v_ms)
    assert math.isfinite(asset.orbit.a_m) and asset.orbit.a_m == orbit_before.a_m


@pytest.mark.parametrize("make", [
    lambda: _command(stored_at="abc"), lambda: _command(stored_at=NAN), lambda: _command(verb=[1]),
    lambda: _command(via=[1]), lambda: _maneuver(dv=[0, 0, 0], via={"a": 1}),
    lambda: _downlink(via=[1]),
], ids=["stored_at-abc", "stored_at-nan", "verb-list", "command-via-list", "maneuver-via-dict",
        "downlink-via-list"])
def test_routing_params_refused(mgr, make):
    _assert_refused_by_both(mgr, make)


# --------------------------------------------------------------------------- #
# Test 6 — an explicit null means the param is absent
# --------------------------------------------------------------------------- #

def _scheduled(osys: OrderSystem, order_id: str) -> dict:
    (ev,) = [tup[2] for tup in osys.sim.scheduler._heap if tup[2].tag == order_id]
    payload = copy.deepcopy(dict(ev.payload))
    payload.pop("__order_id", None)
    return payload


def _payload_for(vignette, make) -> dict:
    m = SessionManager(vignette, seed=5)
    m.start()
    order = m.osys.issue(make())
    assert order.status == "queued", order.fail_reason
    return _scheduled(m.osys, order.id)


def test_null_params_mean_absent(vignette, mgr):
    assert _payload_for(vignette, lambda: _jam(power_w=None, bandwidth_hz=None, victim_bandwidth_hz=None)) \
        == _payload_for(vignette, lambda: _jam())
    order = mgr.osys.issue(_maneuver(dv=None))
    assert order.status == "queued", order.fail_reason
    assert _scheduled(mgr.osys, order.id)["dv"] == [0.0, 0.0, 0.0]
    nocmd = mgr.osys.issue(_command(via=None))
    assert (nocmd.status, nocmd.fail_reason) == ("rejected", "no_command_station")


# --------------------------------------------------------------------------- #
# Test 7 — HTTP: no 500, and the preview agrees with the order
# --------------------------------------------------------------------------- #

def test_http_malformed_jam_is_not_a_500():
    c = TestClient(app, raise_server_exceptions=False)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 5}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    body = {"cell": "red", "actor": "JAM-NORTH", "action": "jam", "target": "ISR-EO-1",
            "params": {"modulation": "barrage", "power_w": "abc"}}
    for route in ("order/validate", "order"):
        r = c.post(f"/api/sessions/{sid}/{route}", json=body)
        assert r.status_code == 200, r.text
        assert r.json()["ok"] is False and r.json()["reason"] == "invalid_param"
    listed = c.get(f"/api/sessions/{sid}/orders/red").json()
    assert not any(o.get("status") in ("queued", "draft") for o in listed), listed


# --------------------------------------------------------------------------- #
# Test 8 — a failed plan leaves no state behind (plan, then commit)
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("make", [
    lambda: _jam(power_w=150.0),
    lambda: _command(),
    lambda: Order(cell="blue", actor="BLUE-RADAR", action="observe", target="ISR-EO-1",
                  params={"intent": "track"}),
], ids=["jam", "command-ground-uplink", "observe"])
def test_failed_plan_leaves_no_state(mgr, monkeypatch, make):
    expected = mgr.osys.dry_run(make()).earliest_window
    assert expected is not None, "fixture order must be plannable"
    before = _snapshot(mgr.osys)

    def boom(self, order, win):
        raise RuntimeError("payload construction failed")

    monkeypatch.setattr(OrderSystem, "_exec_payload", boom)
    order = make()
    with pytest.raises(RuntimeError):
        mgr.osys.issue(order)
    assert _snapshot(mgr.osys) == before
    assert order.status != "queued"
    monkeypatch.undo()
    retry = mgr.osys.issue(make())
    assert retry.status == "queued" and retry.earliest_window == expected


def test_failed_cyber_plan_leaves_no_state(mgr, monkeypatch):
    import spacesim.engine.cyber as cyber
    before = _snapshot(mgr.osys)

    def boom(*a, **k):
        raise RuntimeError("effect construction failed")

    monkeypatch.setattr(cyber, "effective_success", boom)
    order = _cyber()
    with pytest.raises(RuntimeError):
        mgr.osys.issue(order)
    assert _snapshot(mgr.osys) == before
    assert order.status != "queued"


# --------------------------------------------------------------------------- #
# Tests 9-10 — well-formed orders unchanged; observe unchanged
# --------------------------------------------------------------------------- #

def test_numeric_strings_still_accepted_with_identical_payloads(vignette):
    assert _payload_for(vignette, lambda: _jam(power_w="200", bandwidth_hz="1000000")) \
        == _payload_for(vignette, lambda: _jam(power_w=200.0, bandwidth_hz=1e6))
    m = SessionManager(vignette, seed=5)
    m.start()
    m.osys._static_roe.setdefault("red", {}).update(kinetic_authorized=True, cyber_authorized=True)
    m.world.tracks.append(Track(object="ISR-EO-1", owner="red", last_observation=m.world.now,
                                confidence=1.0, characterized=True))
    a = m.osys.issue(_engage(salvo_n="1"))
    b = m.osys.dry_run(_engage(salvo_n=1))
    assert a.status == b.status == "queued", (a.fail_reason, b.fail_reason)
    c = m.osys.issue(_cyber(dwell_s="30"))
    assert c.status == "queued", c.fail_reason
    m.world.assets["ISR-EO-1"].stored_program = True
    t = m.sim.clock.now + 600 * 1_000_000
    s = m.osys.issue(_command(via=None, stored_at=str(t)))
    assert s.status == "queued" and s.delivery_path == "stored_program" and s.earliest_window == (t, t)
    mv = m.osys.issue(_maneuver(dv=["0", "1.5", "0"]))
    assert mv.status == "queued", mv.fail_reason
    assert _scheduled(m.osys, mv.id)["dv"] == [0.0, 1.5, 0.0]


def test_salvo_float_truncation_unchanged(vignette, mgr):
    # IP-1320 (FR-1460) — RED-ASAT holds 1 round in leo-isr-denial; give it enough that the
    # salvo bound is not what this truncation test exercises.
    mgr.world.assets["RED-ASAT"].resources.ammo = 3
    order = mgr.osys.issue(_engage(salvo_n=2.7))
    assert order.status == "queued", order.fail_reason
    assert _scheduled(mgr.osys, order.id)["consume"]["ammo"] == 2


def test_observe_param_check_unchanged(mgr):
    _assert_refused_by_both(mgr, lambda: Order(cell="blue", actor="BLUE-RADAR", action="observe",
                                               target="ISR-EO-1",
                                               params={"intent": "track", "beam_mode": ["fence"]}))
