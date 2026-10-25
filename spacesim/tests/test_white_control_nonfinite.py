"""IP-1082 (review M-1, L-2) — every White control route refuses a non-finite number (and the clock
route an out-of-range rate) with HTTP 400 and a reason, changing nothing and leaving the session
readable (NFR-1600, FR-4330); the seat rule still answers first (FR-4310); the AAR playback cursor
never reports a moment outside the recorded span (FR-7330).

The literals ``NaN`` / ``Infinity`` are not valid strict JSON but Starlette's parser accepts them,
so each request body is posted as hand-built text.
"""

from __future__ import annotations

import inspect
import json

import pytest

pytest.importorskip("fastapi")
from fastapi.routing import APIRoute  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.session.manager import SessionManager  # noqa: E402
from spacesim.ui_web.server import create_app  # noqa: E402

W = {"cell": "white"}
JSON = {"content-type": "application/json"}
NONFINITE = ["NaN", "Infinity", "-Infinity"]


def _client():
    app = create_app()
    return TestClient(app, raise_server_exceptions=False), app


def _started(c):
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    assert c.post(f"/api/sessions/{sid}/start", params=W).status_code == 200
    assert c.post(f"/api/sessions/{sid}/clock", json={"running": False}, params=W).status_code == 200
    return sid


def _post(c, sid, route, text, params=W):
    return c.post(f"/api/sessions/{sid}/{route}", content=text, headers=JSON, params=params)


def _state(app, sid):
    mgr = app.state.api._sessions[sid]
    return (mgr.sim.clock.now, mgr._clock_running, mgr._rate, mgr._wall_anchor, mgr._sim_anchor,
            len(mgr.sim.eventlog.entries), repr(sorted(mgr.ctx.param_values.items())))


def _assert_refused(r):
    assert r.status_code == 400, (r.status_code, r.text)
    assert str(r.json()["detail"]).strip()


# -- Unit 1: the clock rate -----------------------------------------------------------------------
@pytest.mark.verifies("NFR-1600", "FR-4330")
@pytest.mark.parametrize("rate", NONFINITE + ["0", "-5", "1e18", str(SessionManager.MAX_CLOCK_RATE + 1)])
def test_clock_refuses_a_non_finite_or_out_of_range_rate_and_changes_nothing(rate):
    c, app = _client()
    sid = _started(c)
    before = _state(app, sid)
    _assert_refused(_post(c, sid, "clock", f'{{"running": true, "rate": {rate}}}'))
    assert _state(app, sid) == before          # incl. the wall anchor (a refused call does not move it)


@pytest.mark.verifies("NFR-1600", "NFR-1100", "FR-4330")
@pytest.mark.parametrize("rate", ["1", "60", "600", str(SessionManager.MAX_CLOCK_RATE)])
def test_clock_accepts_in_range_rates_including_600x(rate):
    c, app = _client()
    sid = _started(c)
    r = _post(c, sid, "clock", f'{{"running": true, "rate": {rate}}}')
    assert r.status_code == 200 and r.json()["rate"] == float(rate)
    assert _post(c, sid, "clock", '{"running": false}').status_code == 200


@pytest.mark.verifies("NFR-1600", "FR-4330")
def test_a_paused_clock_ignores_a_finite_rate_but_refuses_a_non_finite_one():
    c, app = _client()
    sid = _started(c)
    assert _post(c, sid, "clock", '{"running": false, "rate": 1e18}').status_code == 200
    assert _post(c, sid, "clock", '{"running": false, "rate": -3}').status_code == 200
    for lit in NONFINITE:
        _assert_refused(_post(c, sid, "clock", f'{{"running": false, "rate": {lit}}}'))


@pytest.mark.verifies("NFR-1600")
def test_a_rejected_nan_rate_does_not_poison_the_session():
    """The review's reproduction: before the fix every read of the session was a 500."""
    c, app = _client()
    sid = _started(c)
    _assert_refused(_post(c, sid, "clock", '{"running": true, "rate": NaN}'))
    for path in ("clock", "godview", "scene/blue", "scene/red", "save", "objectives"):
        assert c.get(f"/api/sessions/{sid}/{path}").status_code == 200, path
    assert _post(c, sid, "clock", '{"running": true, "rate": 60}').status_code == 200
    assert _post(c, sid, "clock", '{"running": false}').status_code == 200


# -- Unit 1: time targets, param -----------------------------------------------------------------
@pytest.mark.verifies("NFR-1600", "FR-4330")
@pytest.mark.parametrize("lit", NONFINITE)
@pytest.mark.parametrize("route,field", [("advance", "t"), ("rewind", "t"), ("step", "dt_sim_s"),
                                         ("undo", "n")])
def test_time_controls_refuse_a_non_finite_number_and_change_nothing(route, field, lit):
    c, app = _client()
    sid = _started(c)
    before = _state(app, sid)
    _assert_refused(_post(c, sid, route, f'{{"{field}": {lit}}}'))
    assert _state(app, sid) == before
    assert c.get(f"/api/sessions/{sid}/clock").status_code == 200


@pytest.mark.verifies("FR-4330", "NFR-1600")
def test_the_existing_span_matrix_is_unchanged():
    c, app = _client()
    sid = _started(c)
    now = app.state.api._sessions[sid].sim.clock.now
    for route, text in (("advance", '{"t": -1}'), ("advance", '{"t": 1e30}'),
                        ("advance", f'{{"t": {10**30}}}'), ("rewind", f'{{"t": {now + 10**9}}}'),
                        ("step", '{"dt_sim_s": -1}')):
        r = _post(c, sid, route, text)
        assert r.status_code in (400, 422), (route, text, r.status_code)
    assert _post(c, sid, "step", '{"dt_sim_s": 60}').status_code == 200


@pytest.mark.verifies("FR-4330", "NFR-1600")
@pytest.mark.parametrize("value", [
    "NaN", "Infinity", "[1, 2, NaN]", '{"a": {"b": [0, -Infinity]}}', '[{"k": Infinity}]'])
def test_param_refuses_a_non_finite_number_anywhere_in_value(value):
    c, app = _client()
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    before = repr(sorted(app.state.api._sessions[sid].ctx.param_values.items()))
    _assert_refused(_post(c, sid, "param", f'{{"param_id": "red_kinetic_authorized", "value": {value}}}'))
    assert repr(sorted(app.state.api._sessions[sid].ctx.param_values.items())) == before
    ok = _post(c, sid, "param", '{"param_id": "red_kinetic_authorized", "value": true}')
    assert ok.status_code == 200 and ok.json()["ok"] is True


# -- Unit 1: playback ------------------------------------------------------------------------------
@pytest.mark.verifies("FR-7330", "NFR-1600")
@pytest.mark.parametrize("lit", NONFINITE)
def test_playback_refuses_a_non_finite_speed_or_dt_and_keeps_its_state(lit):
    c, app = _client()
    sid = _started(c)
    assert _post(c, sid, "step", '{"dt_sim_s": 600}').status_code == 200
    base = "aar/playback/"
    _assert_refused(_post(c, sid, base + "start", f'{{"viewpoint": "truth", "speed": {lit}}}'))
    assert _post(c, sid, base + "start", '{"viewpoint": "truth", "speed": 2}').status_code == 200
    st = c.get(f"/api/sessions/{sid}/{base}state", params=W)
    assert st.status_code == 200
    _assert_refused(_post(c, sid, base + "speed", f'{{"speed": {lit}}}'))
    _assert_refused(_post(c, sid, base + "advance", f'{{"dt_s": {lit}}}'))
    pb = app.state.api._playbacks[sid]
    assert pb.speed == 2.0 and pb.t == app.state.api._sessions[sid].ctx.start_epoch
    assert c.get(f"/api/sessions/{sid}/{base}state", params=W).status_code == 200


@pytest.mark.verifies("FR-7330", "FR-4310")
def test_a_player_seat_refused_by_the_playback_rule_still_gets_403_before_the_value_check():
    c, app = _client()
    sid = _started(c)
    assert _post(c, sid, "aar/playback/start", '{"viewpoint": "truth"}').status_code == 200
    for seat in ("blue", None):
        r = _post(c, sid, "aar/playback/speed", '{"speed": NaN}', params={} if seat is None else {"cell": seat})
        assert r.status_code == 403, (seat, r.status_code)


# -- seat first ------------------------------------------------------------------------------------
@pytest.mark.verifies("FR-4310")
@pytest.mark.parametrize("seat", ["blue", "red", "observer", None])
@pytest.mark.parametrize("route,text", [
    ("clock", '{"running": true, "rate": NaN}'), ("advance", '{"t": NaN}'), ("rewind", '{"t": NaN}'),
    ("step", '{"dt_sim_s": NaN}'), ("undo", '{"n": NaN}'),
    ("param", '{"param_id": "x", "value": NaN}')])
def test_a_non_white_request_with_a_nan_body_is_403_not_400(route, text, seat):
    c, app = _client()
    sid = _started(c)
    r = _post(c, sid, route, text, params={} if seat is None else {"cell": seat})
    assert r.status_code == 403, (r.status_code, r.text)


@pytest.mark.verifies("FR-4310", "NFR-1600")
def test_an_unknown_session_is_still_404_before_the_seat_and_value_checks():
    c, app = _client()
    assert _post(c, "nope", "clock", '{"running": true, "rate": NaN}', params={"cell": "blue"}).status_code == 404


# -- the route table pins the shared check ---------------------------------------------------------
def _routes(app):
    return [r for r in app.routes if isinstance(r, APIRoute)
            and r.methods & {"POST", "PUT", "PATCH", "DELETE"}]


def _is_white_control(route: APIRoute) -> bool:
    return "_require_white(" in inspect.getsource(route.endpoint)


def _guards(route: APIRoute) -> set[str]:
    return {getattr(d.call, "__name__", "") for d in route.dependant.dependencies}


@pytest.mark.verifies("NFR-1600", "FR-4330")
def test_every_white_control_route_in_the_live_route_table_has_the_shared_non_finite_check():
    _, app = _client()
    white = [r for r in _routes(app) if _is_white_control(r)]
    names = {r.path.rsplit("/", 1)[-1] for r in white}
    # the discovery is not vacuous: the routes the package names are all found
    assert {"clock", "param", "step", "advance", "rewind", "undo", "start", "inject"} <= names, names
    missing = sorted(f"{sorted(r.methods)[0]} {r.path}" for r in white if "_finite_json_guard" not in _guards(r))
    assert not missing, f"White control routes without the shared non-finite check: {missing}"


@pytest.mark.verifies("FR-7330", "NFR-1600")
def test_the_playback_value_routes_have_the_shared_check_too():
    _, app = _client()
    pb = [r for r in _routes(app) if "/aar/playback/" in r.path and r.path.rsplit("/", 1)[-1] in
          ("start", "advance", "speed")]
    assert len(pb) == 3
    missing = [r.path for r in pb if "_playback_finite_guard" not in _guards(r)]
    assert not missing, missing


# -- in-process backstop -----------------------------------------------------------------------------
@pytest.mark.verifies("NFR-1600", "FR-4330")
def test_the_session_manager_refuses_non_finite_input_itself_and_stays_readable():
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    api.start(sid)
    mgr = api._sessions[sid]
    nan, inf = float("nan"), float("inf")
    before = (mgr.sim.clock.now, mgr._clock_running, mgr._rate)
    for bad in (nan, inf, -inf, 0.0, -1.0, 1e18):
        with pytest.raises(ValueError):
            mgr.set_clock(True, bad)
    with pytest.raises(ValueError):
        mgr.set_clock(False, nan)
    for call in (lambda: mgr.advance_to(nan), lambda: mgr.rewind_to(nan), lambda: mgr.advance_to(inf),
                 lambda: mgr.undo_last(nan), lambda: mgr.step(nan), lambda: mgr.step(inf)):
        with pytest.raises(ValueError):
            call()
    assert (mgr.sim.clock.now, mgr._clock_running, mgr._rate) == before
    assert api.clock_state(sid)["rate"] == before[2]
    ack = api.set_clock(sid, True, nan)
    assert getattr(ack, "ok", True) is False                       # a returned refusal, like the siblings
    assert api.get_godview(sid) is not None


# -- L-2: the playback cursor stays inside the recorded span ------------------------------------------
@pytest.mark.verifies("FR-7330")
@pytest.mark.parametrize("viewpoint", ["truth", "blue"])
@pytest.mark.parametrize("how", ["rewind", "undo"])
def test_playback_never_reports_a_moment_beyond_the_recorded_span(how, viewpoint):
    c, app = _client()
    sid = _started(c)
    for _ in range(3):
        assert _post(c, sid, "step", '{"dt_sim_s": 600}').status_code == 200
    mgr = app.state.api._sessions[sid]
    start = mgr.ctx.start_epoch
    assert _post(c, sid, "aar/playback/start", json.dumps({"viewpoint": viewpoint})).status_code == 200
    r = _post(c, sid, "aar/playback/advance", '{"dt_s": 100000}')
    assert r.status_code == 200
    pb = app.state.api._playbacks[sid]
    assert pb.t == mgr.sim.clock.now > start
    if how == "rewind":
        assert _post(c, sid, "rewind", json.dumps({"t": start + 60_000_000})).status_code == 200
    else:
        assert _post(c, sid, "undo", '{"n": 1000}').status_code == 200
    live = mgr.sim.clock.now
    assert live < pb.t                                                # the premise: the cursor is now stale
    st = c.get(f"/api/sessions/{sid}/aar/playback/state", params=W)
    assert st.status_code == 200
    assert start <= pb.t <= live
    now_in_state = st.json().get("now")
    if now_in_state is not None:
        assert start <= now_in_state <= live
