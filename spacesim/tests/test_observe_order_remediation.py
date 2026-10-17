"""IP-1041 — observe-order remediation (FR-3210, FR-1610).

- BL-0219: a windowless observe was rejected ``sensor_contended`` (the console shows "Sensor is
  busy"), not ``no_window``. ``sensor_contended`` now means a window was found and every window
  found was booked.
- BL-0217 (widened): a malformed observe param (non-string ``beam_mode``; non-numeric or
  non-finite ``look_angle_deg``/``duration_s``/``gain``) raised inside ``_exec_payload`` -> HTTP
  500 on ``POST /order`` while ``dry_run`` said ok, and left a phantom sensor booking. It is now
  rejected ``invalid_param`` by both paths before anything is booked; an explicit ``null`` means
  the param is absent.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from spacesim.content.vignette import load_vignette
from spacesim.engine.entities import Asset, Sensor
from spacesim.engine.geometry import R_EARTH_EQ, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.isr import beam_params
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState
from spacesim.session.manager import SessionManager
from spacesim.ui_web.server import app

PROP = ModeratePropagator()


def _leo(ta: float = 0.0, alt_m: float = 550e3) -> OrbitState:
    return OrbitState(a_m=R_EARTH_EQ + alt_m, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0,
                      ta_deg=ta, epoch=0)


def _subpoint(orbit: OrbitState, t: int):
    r, _ = PROP.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    g.alt_m = 0.0
    return g


def _world(*sensors: Sensor) -> WorldState:
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=_leo())
    for s in sensors:
        world.sensors[s.id] = s
    return world


def _radar(sid: str = "RDR", **kw) -> Sensor:
    return Sensor(id=sid, owner="blue", kind="ground_radar", location=_subpoint(_leo(), 0), **kw)


def _osys(world: WorldState) -> tuple[Simulation, OrderSystem]:
    sim = Simulation(world, seed=7)
    return sim, OrderSystem(sim, roe={"blue": {}, "red": {}})


def _obs(actor: str = "RDR", target: str = "TGT", **params) -> Order:
    return Order(cell="blue", actor=actor, action="observe", target=target,
                 params={"intent": "track", **params})


def _payloads(sim: Simulation) -> list[dict]:
    return [dict(tup[2].payload) for tup in sim.scheduler._heap if tup[2].kind == "execute_observe"]


# --------------------------------------------------------------------------- #
# Tests 1-4 — BL-0219: the rejection reason says what actually happened
# --------------------------------------------------------------------------- #

def _windowless_worlds():
    # A ground radar whose 1 m range cap leaves no window; a space-based sensor whose range floor
    # exceeds any achievable range (FR-1630).
    yield _world(_radar(max_range_m=1.0))
    yield _world(Sensor(id="RDR", owner="blue", kind="space_based", orbit=_leo(ta=40.0, alt_m=700e3),
                        min_range_km=1.0e6))


@pytest.mark.parametrize("actor", ["RDR", "auto"])
@pytest.mark.parametrize("method", ["issue", "dry_run"])
def test_windowless_sensor_is_no_window(actor, method):
    for world in _windowless_worlds():
        _, osys = _osys(world)
        order = getattr(osys, method)(_obs(actor))
        assert order.status == "rejected"
        assert order.fail_reason == "no_window"
        assert osys._sensor_bookings == {} or all(not b for b in osys._sensor_bookings.values())


def test_every_window_booked_is_sensor_contended():
    _, osys = _osys(_world(_radar()))
    reasons = []
    for _ in range(60):
        order = osys.issue(_obs())
        reasons.append(order.fail_reason if order.status == "rejected" else "queued")
        if order.status == "rejected":
            break
    assert reasons[0] == "queued"               # the radar does have windows
    assert reasons[-1] == "sensor_contended"    # ... and once all are booked, it is contended
    assert osys.dry_run(_obs()).fail_reason == "sensor_contended"


def test_existing_reasons_unchanged():
    _, osys = _osys(_world(_radar(), Sensor(id="RED-RDR", owner="red", kind="ground_radar",
                                             location=_subpoint(_leo(), 0))))
    assert osys.dry_run(_obs("RED-RDR")).fail_reason == "not_owner"
    assert osys.dry_run(_obs("NOPE")).fail_reason == "no_such_sensor"
    _, osys = _osys(_world())   # no sensor at all
    assert osys.dry_run(_obs("auto")).fail_reason == "no_window"


def test_unknown_target_on_shipped_radar_is_no_window():
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    mgr.set_clock(False)
    order = Order(cell="blue", actor="RADAR-TRN", action="observe", target="NO-SUCH-OBJECT",
                  params={"intent": "track"})
    assert mgr.validate_order("blue", order).reason == "no_window"
    assert mgr.issue_order("blue", order).reason == "no_window"


# --------------------------------------------------------------------------- #
# Tests 5-7 — BL-0217: malformed params rejected before booking, no 500
# --------------------------------------------------------------------------- #

MALFORMED = [
    {"beam_mode": ["fence"]},
    {"beam_mode": {"a": 1}},
    {"beam_mode": 3},
    {"look_angle_deg": "abc"},
    {"gain": "high"},
    {"duration_s": "long"},
    {"look_angle_deg": "inf"},
    {"gain": float("nan")},
    {"duration_s": [1, 2]},
]


@pytest.mark.parametrize("bad", MALFORMED, ids=lambda b: f"{next(iter(b))}={b[next(iter(b))]!r}")
@pytest.mark.parametrize("actor", ["RDR", "auto"])
def test_malformed_param_rejected_by_both_paths(bad, actor):
    _, osys = _osys(_world(_radar()))
    assert osys.dry_run(_obs(actor, **bad)).fail_reason == "invalid_param"
    order = osys.issue(_obs(actor, **bad))
    assert order.status == "rejected" and order.fail_reason == "invalid_param"


def test_no_phantom_booking_after_malformed_attempts():
    _, fresh = _osys(_world(_radar()))
    expected = fresh.issue(_obs()).earliest_window
    _, osys = _osys(_world(_radar()))
    for bad in MALFORMED:
        osys.issue(_obs(**bad))
        assert all(not b for b in osys._sensor_bookings.values())
        assert osys._order_sensor == {}
    order = osys.issue(_obs())
    assert order.status == "queued"
    assert order.earliest_window == expected


def test_http_malformed_param_is_not_a_500():
    c = TestClient(app, raise_server_exceptions=False)
    sid = c.post("/api/sessions", json={"vignette_id": "training-basics", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    body = {"cell": "blue", "actor": "RADAR-TRN", "action": "observe", "target": "RED-TGT",
            "params": {"intent": "track", "beam_mode": ["fence"]}}
    for route in ("order/validate", "order"):
        r = c.post(f"/api/sessions/{sid}/{route}", json=body)
        assert r.status_code == 200, r.text
        assert r.json()["ok"] is False and r.json()["reason"] == "invalid_param"


# --------------------------------------------------------------------------- #
# Tests 8-9 — null means absent; well-formed orders unchanged
# --------------------------------------------------------------------------- #

def _payload_for(**params) -> dict:
    sim, osys = _osys(_world(_radar()))
    order = osys.issue(_obs(**params))
    assert order.status == "queued", order.fail_reason
    (p,) = _payloads(sim)
    p.pop("__order_id", None)
    return p


def test_null_params_mean_absent():
    nulls = _payload_for(look_angle_deg=None, duration_s=None, gain=None, beam_mode=None)
    assert nulls == _payload_for()


def test_well_formed_orders_unchanged():
    assert _payload_for(look_angle_deg="10", duration_s="120") == \
        _payload_for(look_angle_deg=10.0, duration_s=120.0)
    # IP-1223 (FS-122 v1.2): the fixture is a radar, so its own mode (a SAR name is now refused).
    assert _payload_for(gain=0.5, beam_mode="dish") == _payload_for(gain=0.5, beam_mode="dish")
    for odd in (["fence"], {"a": 1}, 3):
        assert beam_params("isr_sar", odd) == beam_params("isr_sar", None)
        assert beam_params("ground_radar", odd) == beam_params("ground_radar", None)
