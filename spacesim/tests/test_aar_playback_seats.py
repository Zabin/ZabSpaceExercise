"""IP-1077 (FR-7340, FR-4320, FR-6210) — the AAR playback routes obey the requesting seat."""

from __future__ import annotations

import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.ui_web.server import create_app  # noqa: E402

pytestmark = pytest.mark.verifies("FR-7340")

WORLD_KEYS = ("assets", "tracks")


def _session():
    app = create_app()
    c = TestClient(app)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 300})
    return app, c, sid


def _p(sid, leaf):
    return f"/api/sessions/{sid}/aar/playback/{leaf}"


def _post(c, sid, leaf, body, seat):
    q = f"?cell={seat}" if seat is not None else ""
    return c.post(_p(sid, leaf) + q, json=body)


def _get_state(c, sid, seat):
    q = f"?cell={seat}" if seat is not None else ""
    return c.get(_p(sid, "state") + q)


def _snap(c, sid):
    s = _get_state(c, sid, "white").json()
    return json.dumps(s, sort_keys=True, default=str)


def test_white_succeeds_for_every_viewpoint_and_action():
    _, c, sid = _session()
    for vp in ("truth", "blue", "red"):
        assert _post(c, sid, "start", {"viewpoint": vp}, "white").json()["ok"] is True
    for vp in ("truth", "red", "blue"):
        assert _post(c, sid, "viewpoint", {"viewpoint": vp}, "white").json()["ok"] is True
    assert _post(c, sid, "advance", {"dt_s": 10}, "white").status_code == 200
    assert _post(c, sid, "speed", {"speed": 4.0}, "white").json()["ok"] is True
    assert _get_state(c, sid, "white").status_code == 200


@pytest.mark.parametrize("seat,other", [("blue", "red"), ("red", "blue")])
def test_player_start_only_own_viewpoint_and_refusal_creates_nothing(seat, other):
    _, c, sid = _session()
    for vp in ("truth", other):
        r = _post(c, sid, "start", {"viewpoint": vp}, seat)
        assert r.status_code == 403
        assert _get_state(c, sid, "white").status_code == 404  # no playback created
    assert _post(c, sid, "start", {"viewpoint": seat}, seat).status_code == 200
    assert _get_state(c, sid, "white").status_code == 200


def test_player_viewpoint_switch_refused_unchanged_and_own_continues():
    _, c, sid = _session()
    _post(c, sid, "start", {"viewpoint": "truth", "speed": 2.0}, "white")
    _post(c, sid, "advance", {"dt_s": 20}, "white")
    before = _snap(c, sid)
    for vp in ("truth", "red"):
        assert _post(c, sid, "viewpoint", {"viewpoint": vp}, "blue").status_code == 403
    assert _snap(c, sid) == before
    r = _post(c, sid, "viewpoint", {"viewpoint": "blue"}, "blue")
    assert r.status_code == 200 and r.json()["ok"] is True
    after = _get_state(c, sid, "blue").json()
    assert "own_assets" in after


def test_state_read_refused_for_other_viewpoint_and_discloses_nothing():
    _, c, sid = _session()
    _post(c, sid, "start", {"viewpoint": "truth"}, "white")
    r = _get_state(c, sid, "red")
    assert r.status_code == 403
    assert not any(k in r.json() for k in WORLD_KEYS)
    _post(c, sid, "viewpoint", {"viewpoint": "blue"}, "white")
    assert _get_state(c, sid, "red").status_code == 403
    ok = _get_state(c, sid, "blue")
    assert ok.status_code == 200 and "own_assets" in ok.json()


def test_player_advance_and_speed_refused_when_viewpoint_not_own():
    app, c, sid = _session()
    _post(c, sid, "start", {"viewpoint": "truth", "speed": 2.0}, "white")
    before = _snap(c, sid)
    assert _post(c, sid, "advance", {"dt_s": 30}, "blue").status_code == 403
    assert _post(c, sid, "speed", {"speed": 9.0}, "blue").status_code == 403
    assert _snap(c, sid) == before
    assert app.state.api._playbacks[sid].speed == 2.0


def test_observer_mutations_refused_and_unchanged_read_allowed():
    _, c, sid = _session()
    _post(c, sid, "start", {"viewpoint": "truth", "speed": 2.0}, "white")
    before = _snap(c, sid)
    assert _post(c, sid, "start", {"viewpoint": "truth"}, "observer").status_code == 403
    assert _post(c, sid, "advance", {"dt_s": 30}, "observer").status_code == 403
    assert _post(c, sid, "viewpoint", {"viewpoint": "blue"}, "observer").status_code == 403
    assert _post(c, sid, "speed", {"speed": 9.0}, "observer").status_code == 403
    assert _snap(c, sid) == before
    assert _get_state(c, sid, "observer").status_code == 200


@pytest.mark.parametrize("seat", [None, "nobody"])
def test_no_seat_or_unknown_seat_refused_on_every_route(seat):
    _, c, sid = _session()
    _post(c, sid, "start", {"viewpoint": "truth"}, "white")
    before = _snap(c, sid)
    assert _post(c, sid, "start", {"viewpoint": "truth"}, seat).status_code == 403
    assert _post(c, sid, "advance", {"dt_s": 5}, seat).status_code == 403
    assert _post(c, sid, "viewpoint", {"viewpoint": "blue"}, seat).status_code == 403
    assert _post(c, sid, "speed", {"speed": 3}, seat).status_code == 403
    assert _get_state(c, sid, seat).status_code == 403
    assert _snap(c, sid) == before


def test_check_order_refusal_precedes_400_and_404():
    _, c, sid = _session()
    # no playback yet: a player acting is 403 (not 404); White keeps 404
    assert _post(c, sid, "advance", {"dt_s": 5}, "blue").status_code == 403
    assert _post(c, sid, "speed", {"speed": 2}, "blue").status_code == 403
    assert _get_state(c, sid, "blue").status_code == 403
    assert _post(c, sid, "advance", {"dt_s": 5}, "white").status_code == 404
    assert _get_state(c, sid, "white").status_code == 404
    # non-participant viewpoint: player 403, White keeps its 200/ok False
    assert _post(c, sid, "start", {"viewpoint": "ghost"}, "blue").status_code == 403
    r = _post(c, sid, "start", {"viewpoint": "ghost"}, "white")
    assert r.status_code == 200 and r.json()["ok"] is False


def test_layering_session_and_pure_check():
    from spacesim.session.inprocess import InProcessSession, playback_seat_decision
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    api.start(sid)
    ack = api.playback_start(sid, "truth", 1.0, seat="blue")
    assert ack.ok is False and ack.reason
    assert sid not in api._playbacks
    assert playback_seat_decision("white", "start", "truth", None) is None
    assert playback_seat_decision("blue", "start", "truth", None)


# (seat, action, requested, current) -> allowed ; the documented Interfaces matrix.
_MATRIX = []
for _seat in ("white", "blue", "red", "observer", None, "nobody"):
    for _act in ("start", "viewpoint"):
        for _req in ("truth", "blue", "red"):
            _allowed = _seat == "white" or (_seat in ("blue", "red") and _req == _seat)
            _MATRIX.append((_seat, _act, _req, "truth", _allowed))
    for _act in ("advance", "speed", "state"):
        for _cur in ("truth", "blue", "red", None):
            if _seat == "white":
                _allowed = True
            elif _seat in ("blue", "red"):
                _allowed = _cur == _seat
            elif _seat == "observer":
                _allowed = _act == "state"
            else:
                _allowed = False
            _MATRIX.append((_seat, _act, None, _cur, _allowed))


def test_pure_check_matches_documented_matrix():
    from spacesim.session.inprocess import playback_seat_decision
    for seat, action, req, cur, allowed in _MATRIX:
        got = playback_seat_decision(seat, action, req, cur)
        assert (got is None) is allowed, (seat, action, req, cur)


def test_refused_requests_leave_session_and_log_untouched():
    _, c, sid = _session()
    _post(c, sid, "start", {"viewpoint": "truth"}, "white")
    def snap():
        # the live clock is wall-driven (lazy), so compare the log, not the world's ``now``
        return c.get(f"/api/sessions/{sid}/eventlog").text

    before = snap()
    for seat in ("blue", "red", "observer", None):
        _post(c, sid, "start", {"viewpoint": "red"}, seat)
        _post(c, sid, "advance", {"dt_s": 50}, seat)
        _post(c, sid, "viewpoint", {"viewpoint": "red"}, seat)
        _post(c, sid, "speed", {"speed": 50}, seat)
    assert snap() == before


@pytest.mark.verifies("IP-1077")
def test_matrix_is_nonempty_and_white_row_all_allowed():
    assert all(a for (s, _, _, _, a) in _MATRIX if s == "white")
    assert not any(a for (s, _, _, _, a) in _MATRIX if s in (None, "nobody"))
