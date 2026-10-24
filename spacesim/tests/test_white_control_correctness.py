"""IP-1074 — White control correctness: a rewind stays inside the exercise's own time span
``[start_epoch, now]`` (400 otherwise; "rewind to start" means ``start_epoch``), and
``roles/assign`` / ``observer/view`` refuse by the *query* seat with 403 (FS-106 v2.4)."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.session.api import Ack  # noqa: E402
from spacesim.ui_web.server import create_app  # noqa: E402


W = {"cell": "white"}


def _client():
    app = create_app()
    return TestClient(app), app.state.api


def _started(c, run=False):
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    assert c.post(f"/api/sessions/{sid}/start", params=W).status_code == 200
    if not run:
        assert c.post(f"/api/sessions/{sid}/clock", json={"running": False}, params=W).status_code == 200
    return sid


def _state(api, sid):
    m = api._sessions[sid]
    return (m.sim.clock.now, len(api.get_eventlog(sid, 0)), m._clock_running)


def _rewind(c, sid, t, **kw):
    return c.post(f"/api/sessions/{sid}/rewind", json={"t": t}, params=W, **kw)


# -- Part A ---------------------------------------------------------------------------------------

@pytest.mark.verifies("FR-4330", "NFR-1600")
def test_rewind_to_zero_is_refused_with_the_span_and_changes_nothing():
    c, api = _client()
    sid = _started(c)
    c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 120.0}, params=W)
    before = _state(api, sid)
    r = _rewind(c, sid, 0)
    assert r.status_code == 400
    assert "start" in r.json()["detail"].lower()
    assert _state(api, sid) == before


@pytest.mark.verifies("FR-4330", "NFR-1600")
def test_rewind_before_start_and_after_now_is_refused():
    c, api = _client()
    sid = _started(c)
    c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 120.0}, params=W)
    start = api._sessions[sid].ctx.start_epoch
    now = api._sessions[sid].sim.clock.now
    before = _state(api, sid)
    for t in (start - 1, now + 1):
        assert _rewind(c, sid, t).status_code == 400
    assert _state(api, sid) == before


@pytest.mark.verifies("FR-4330")
def test_the_span_edges_are_allowed():
    c, api = _client()
    sid = _started(c)
    c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 120.0}, params=W)
    m = api._sessions[sid]
    now = m.sim.clock.now
    assert _rewind(c, sid, now).status_code == 200
    assert m.sim.clock.now == now
    assert _rewind(c, sid, m.ctx.start_epoch).status_code == 200
    assert m.sim.clock.now == m.ctx.start_epoch


@pytest.mark.verifies("FR-4330", "NFR-1600")
def test_rewind_to_start_leaves_a_start_sized_save():
    c, api = _client()
    sid = _started(c)
    fresh = len(c.get(f"/api/sessions/{sid}/save", params=W).content)
    c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 400.0}, params=W)
    assert _rewind(c, sid, api._sessions[sid].ctx.start_epoch).status_code == 200
    after = c.get(f"/api/sessions/{sid}/save", params=W).content
    assert len(after) <= fresh + 4096
    assert api._sessions[sid].sim.clock.now == api._sessions[sid].ctx.start_epoch


@pytest.mark.verifies("FR-4310")
@pytest.mark.parametrize("running", [True, False])
def test_a_rewind_leaves_the_running_state_and_reanchors(running, monkeypatch):
    c, api = _client()
    sid = _started(c)
    c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 300.0}, params=W)
    m = api._sessions[sid]
    c.post(f"/api/sessions/{sid}/clock", json={"running": running, "rate": 10.0}, params=W)
    t = m.ctx.start_epoch + 60 * 1_000_000
    assert _rewind(c, sid, t).status_code == 200
    if running:
        import spacesim.session.manager as mg
        assert m._sim_anchor == t            # re-anchored at the rewound time, not a stale one
        monkeypatch.setattr(mg._time, "time", lambda: m._wall_anchor + 2.0)
        m.catch_up()
        assert m.sim.clock.now == t + 20 * 1_000_000
    else:
        m.catch_up()
        assert m.sim.clock.now == t
    state = m.clock_state()
    assert state["running"] is running


@pytest.mark.verifies("FR-4310")
def test_clock_state_exposes_start_epoch():
    c, api = _client()
    sid = _started(c)
    assert c.get(f"/api/sessions/{sid}/clock").json()["start_epoch"] == api._sessions[sid].ctx.start_epoch


@pytest.mark.verifies("NFR-1600")
def test_layering_value_error_then_ack():
    c, api = _client()
    sid = _started(c)
    m = api._sessions[sid]
    with pytest.raises(ValueError):
        m.rewind_to(0)
    ack = api.rewind_to(sid, 0)
    assert isinstance(ack, Ack) and ack.ok is False and ack.reason
    dsid = api.create_draft_session("leo-isr-denial")
    d = api.rewind_to(dsid, 0)
    assert d.ok is False and "draft" in d.reason


@pytest.mark.verifies("FR-4310")
def test_non_white_is_403_and_non_integer_is_422():
    c, api = _client()
    sid = _started(c)
    before = _state(api, sid)
    for seat in ("blue", "red", "observer"):
        assert c.post(f"/api/sessions/{sid}/rewind", json={"t": 0}, params={"cell": seat}).status_code == 403
    assert c.post(f"/api/sessions/{sid}/rewind", json={"t": 0}).status_code == 403
    assert c.post(f"/api/sessions/{sid}/rewind", json={"t": "soon"}, params=W).status_code == 422
    assert _state(api, sid) == before


# -- Part B ---------------------------------------------------------------------------------------

ASSIGN = {"cell": "white", "seat": "seat-1", "asset_or_constellation": "ISR-EO-1", "role": "both"}
OBSERVE = {"cell": "white", "designation": "red"}


def _fresh():
    c, api = _client()
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    return c, api, sid


@pytest.mark.verifies("FR-4320")
@pytest.mark.parametrize("route,body", [("roles/assign", ASSIGN), ("observer/view", OBSERVE)])
@pytest.mark.parametrize("seat", ["blue", "red", "observer", None])
def test_seat_routes_refuse_by_query_seat(route, body, seat):
    c, api, sid = _fresh()
    staffing = dict(api._sessions[sid].role_assignments)
    desig = c.get(f"/api/sessions/{sid}/observer/designation").json()
    r = c.post(f"/api/sessions/{sid}/{route}", json=body, params={} if seat is None else {"cell": seat})
    assert r.status_code == 403
    assert api._sessions[sid].role_assignments == staffing
    assert c.get(f"/api/sessions/{sid}/observer/designation").json() == desig


@pytest.mark.verifies("FR-4320")
@pytest.mark.parametrize("route,body", [("roles/assign", ASSIGN), ("observer/view", OBSERVE)])
def test_body_seat_is_not_authority(route, body):
    c, api, sid = _fresh()
    # body white, query blue: refused (the reported hole)
    assert c.post(f"/api/sessions/{sid}/{route}", json=body, params={"cell": "blue"}).status_code == 403
    # body blue, query white: the query seat decides
    r = c.post(f"/api/sessions/{sid}/{route}", json={**body, "cell": "blue"}, params=W)
    assert r.status_code == 200 and r.json()["ok"] is True


@pytest.mark.verifies("FR-4320")
def test_white_succeeds_with_effect_visible():
    c, api, sid = _fresh()
    r = c.post(f"/api/sessions/{sid}/roles/assign", json=ASSIGN, params=W)
    assert r.status_code == 200 and r.json()["ok"] is True
    assert "seat-1" in api._sessions[sid].role_assignments
    r = c.post(f"/api/sessions/{sid}/observer/view", json=OBSERVE, params=W)
    assert r.status_code == 200 and r.json()["ok"] is True
    assert c.get(f"/api/sessions/{sid}/observer/designation").json()["designation"] == "red"


@pytest.mark.verifies("FR-4320")
def test_session_layer_still_refuses_a_non_white_cell():
    c, api, sid = _fresh()
    assert api.assign_role(sid, "blue", "seat-1", "ISR-EO-1", "both").ok is False
    assert api.set_observer_view(sid, "red", "blue").ok is False
