"""IP-1068 — White Cell controls are refused at the server boundary unless the request names the
``white`` seat (FS-106 v2.4, FR-4310 clock authority, FR-4320 session-configuration authority).
Same client-asserted-seat trust level as the Observer refusal (IP-1130); not authentication.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.ui_web.server import create_app  # noqa: E402

TLE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"

# seat -> request params. `None` is "no seat named at all".
NON_WHITE = ["blue", "red", "observer", None]


def _params(seat):
    return {} if seat is None else {"cell": seat}


def _client():
    app = create_app()
    return TestClient(app), app.state.api


def _session(c, started):
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    if started:
        assert c.post(f"/api/sessions/{sid}/start", params={"cell": "white"}).status_code == 200
        # Freeze the lazy real-time clock so snapshots differ only by what a call itself did.
        assert c.post(f"/api/sessions/{sid}/clock", json={"running": False},
                      params={"cell": "white"}).status_code == 200
    return sid


def _snapshot(api, sid):
    mgr = api._sessions[sid]
    return (mgr.started, mgr.sim.clock.now, len(api.get_eventlog(sid, 0)),
            len(mgr.world.assets), mgr._clock_running, mgr._rate,
            repr(sorted(mgr.ctx.param_values.items())))


CLOCK_ROUTES = {
    "clock": ("clock", {"running": False, "rate": 1.0}),
    "step": ("step", {"dt_sim_s": 60.0}),
    "advance": ("advance", None),   # body built from the current sim time
    "rewind": ("rewind", {"t": 0}),
    "undo": ("undo", {"n": 1}),
}

CONFIG_ROUTES = {
    "start": ("start", None),
    "param": ("param", {"param_id": "red_kinetic_authorized", "value": True}),
    "inject": ("inject", {"inject": "commercial_imagery_leak"}),
    "force/tle": ("force/tle", {"id": "WO-TLE-1", "line1": TLE1, "line2": TLE2}),
    "force/bulk_import": ("force/bulk_import", {
        "format": "tle", "content": "\n".join(["WO-BULK-1", TLE1, TLE2]),
        "assignments": {"WO-BULK-1": {"asset_id": "WO-BULK-1", "owner": "blue"}}}),
    "force/ground": ("force/ground", {"id": "WO-GND-1", "lat_deg": 10.0, "lon_deg": 20.0}),
}


def _body(api, sid, name, body):
    if name == "advance":
        return {"t": api._sessions[sid].sim.clock.now + 60 * 1_000_000}
    return body




@pytest.mark.verifies("FR-4310")
@pytest.mark.parametrize("seat", NON_WHITE, ids=lambda s: str(s))
@pytest.mark.parametrize("name", list(CLOCK_ROUTES))
def test_clock_controls_refused_for_non_white(name, seat):
    c, api = _client()
    sid = _session(c, started=True)
    before = _snapshot(api, sid)
    route, body = CLOCK_ROUTES[name]
    r = c.post(f"/api/sessions/{sid}/{route}", json=_body(api, sid, name, body), params=_params(seat))
    assert r.status_code == 403
    assert r.json()["detail"]
    assert _snapshot(api, sid) == before


@pytest.mark.verifies("FR-4310")
@pytest.mark.parametrize("name", list(CLOCK_ROUTES))
def test_clock_controls_accepted_for_white(name):
    c, api = _client()
    sid = _session(c, started=True)
    # Give undo/rewind something to act on.
    c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 120.0}, params={"cell": "white"})
    before = _snapshot(api, sid)
    route, body = CLOCK_ROUTES[name]
    r = c.post(f"/api/sessions/{sid}/{route}", json=_body(api, sid, name, body), params={"cell": "white"})
    assert r.status_code == 200, r.text
    if name == "clock":
        assert api._sessions[sid]._clock_running is False
    elif name == "rewind":
        assert api._sessions[sid].sim.clock.now == 0
    else:
        assert _snapshot(api, sid) != before


@pytest.mark.verifies("FR-4320")
@pytest.mark.parametrize("seat", NON_WHITE, ids=lambda s: str(s))
@pytest.mark.parametrize("name", list(CONFIG_ROUTES))
def test_config_controls_refused_for_non_white(name, seat):
    c, api = _client()
    # Draft sessions accept asset adds without a started clock; a normal unstarted one is used for
    # start/param, a started one for inject.
    sid = _session(c, started=(name == "inject"))
    before = _snapshot(api, sid)
    route, body = CONFIG_ROUTES[name]
    r = c.post(f"/api/sessions/{sid}/{route}", json=body, params=_params(seat))
    assert r.status_code == 403
    assert r.json()["detail"]
    assert _snapshot(api, sid) == before


@pytest.mark.verifies("FR-4320")
@pytest.mark.parametrize("name", list(CONFIG_ROUTES))
def test_config_controls_accepted_for_white(name):
    c, api = _client()
    sid = _session(c, started=(name == "inject"))
    before = _snapshot(api, sid)
    route, body = CONFIG_ROUTES[name]
    r = c.post(f"/api/sessions/{sid}/{route}", json=body, params={"cell": "white"})
    assert r.status_code == 200, r.text
    if name in ("force/tle", "force/bulk_import", "force/ground"):
        # Asset adds on a started session are refused by the session layer; on an unstarted one
        # they must land.
        assert _snapshot(api, sid)[3] == before[3] + 1
    elif name == "start":
        assert api._sessions[sid].started is True
    else:
        assert _snapshot(api, sid) != before


@pytest.mark.verifies("FR-4320")
@pytest.mark.parametrize("seat", NON_WHITE, ids=lambda s: str(s))
def test_load_save_refused_for_non_white_accepted_for_white(seat):
    c, api = _client()
    sid = _session(c, started=True)
    state = c.get(f"/api/sessions/{sid}/save").json()
    n = len(api._sessions)
    r = c.post("/api/sessions/load_save", json=state, params=_params(seat))
    assert r.status_code == 403
    assert len(api._sessions) == n
    ok = c.post("/api/sessions/load_save", json=state, params={"cell": "white"})
    assert ok.status_code == 200
    assert len(api._sessions) == n + 1


@pytest.mark.verifies("FR-4320")
@pytest.mark.parametrize("seat", ["blue", "red"])
def test_seat_assignment_and_observer_designation_refused_for_player_seats(seat):
    c, api = _client()
    sid = _session(c, started=False)
    staffing = c.get(f"/api/sessions/{sid}/roles/staffing").json()
    designation = c.get(f"/api/sessions/{sid}/observer/designation").json()
    a = c.post(f"/api/sessions/{sid}/roles/assign",
               json={"cell": seat, "seat": "seat-1", "asset_or_constellation": "ISR-EO-1", "role": "both"}).json()
    assert a["ok"] is False and a["reason"]
    o = c.post(f"/api/sessions/{sid}/observer/view", json={"cell": seat, "designation": "red"}).json()
    assert o["ok"] is False and o["reason"]
    assert c.get(f"/api/sessions/{sid}/roles/staffing").json() == staffing
    assert c.get(f"/api/sessions/{sid}/observer/designation").json() == designation


@pytest.mark.verifies("FR-4310", "FR-4320")
@pytest.mark.parametrize("name", list(CLOCK_ROUTES) + list(CONFIG_ROUTES))
def test_unknown_session_is_404_before_the_seat_check(name):
    c, _ = _client()
    route, body = {**CLOCK_ROUTES, **CONFIG_ROUTES}[name]
    body = {"t": 0} if name == "advance" else body
    r = c.post(f"/api/sessions/nope/{route}", json=body, params={"cell": "blue"})
    assert r.status_code == 404
