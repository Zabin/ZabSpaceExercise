"""IP-1072 — White Cell controls, second tranche (FR-4320 as extended 2026-10-24): Creator edits,
vignette/scenario saves, the Red doctrine AI step and the seat declaration are refused unless the
request names the ``white`` seat; session / draft creation is refused when it *names* a player seat
(an absent seat is allowed — deliberate asymmetry, IP-1072 Design Decision 2). Same client-asserted
seat trust level as IP-1068 / IP-1130; not authentication.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.ui_web.server import create_app  # noqa: E402

pytestmark = pytest.mark.verifies("FR-4320")

from tle_helpers import in_epoch_tle  # noqa: E402 — IP-1086: a TLE valid at the 2030 exercise start
TLE1, TLE2 = in_epoch_tle()

NON_WHITE = ["blue", "red", "observer", None]
PLAYER_SEATS = ["blue", "red", "observer"]
IN_SESSION = ["save_vignette", "creator_state_put", "creator_asset_patch",
              "creator_asset_delete", "red_step", "creator_seats"]


def _params(seat):
    return {} if seat is None else {"cell": seat}


@pytest.fixture
def save_dir(tmp_path, monkeypatch):
    d = tmp_path / "user_saves"
    d.mkdir()
    cfg = tmp_path / "spacesim.config.yaml"
    cfg.write_text(f"content:\n  user_save_dir: {d}\n", encoding="utf-8")
    monkeypatch.setenv("SPACESIM_CONFIG", str(cfg))
    return d


def _client():
    app = create_app()
    return TestClient(app), app.state.api


def _draft_with_asset(c):
    sid = c.post("/api/sessions/draft", json={"title": "WO2"}).json()["session"]
    r = c.post(f"/api/sessions/{sid}/force/tle", params={"cell": "white"},
               json={"id": "WO2-SAT", "line1": TLE1, "line2": TLE2, "owner": "blue"})
    assert r.status_code == 200 and r.json()["ok"] is True
    return sid


def _snapshot(api, sid, save_dir):
    mgr = api._sessions[sid]
    return (sorted(mgr.world.assets), repr(sorted(mgr.world.assets.items(), key=lambda kv: kv[0])),
            len(api.get_eventlog(sid, 0)), len(mgr.osys.queue) if hasattr(mgr.osys, "queue") else 0,
            sorted(p.name for p in save_dir.iterdir()), repr(getattr(api, "_seats_declared", None)))


def _call(c, name, sid, seat):
    p = _params(seat)
    base = f"/api/sessions/{sid}"
    if name == "save_vignette":
        return c.post(f"{base}/save_vignette", params=p, json={"vignette_id": "wo2-save", "title": "WO2"})
    if name == "creator_state_put":
        return c.put(f"{base}/creator/state", params=p, json={"assets": []})
    if name == "creator_asset_patch":
        return c.patch(f"{base}/creator/asset/WO2-SAT", params=p, json={"patch": {"owner": "red"}})
    if name == "creator_asset_delete":
        return c.delete(f"{base}/creator/asset/WO2-SAT", params=p)
    if name == "red_step":
        return c.post(f"{base}/red_step", params=p)
    if name == "creator_seats":
        return c.post(f"{base}/creator/seats", params=p, json={"cell": "blue", "count": 2})
    raise AssertionError(name)


@pytest.mark.parametrize("seat", NON_WHITE, ids=str)
@pytest.mark.parametrize("name", [n for n in IN_SESSION if n != "creator_seats"])
def test_in_session_controls_refused_for_non_white(name, seat, save_dir):
    c, api = _client()
    sid = _draft_with_asset(c)
    before = _snapshot(api, sid, save_dir)
    r = _call(c, name, sid, seat)
    assert r.status_code == 403, r.text
    assert r.json()["detail"]
    assert _snapshot(api, sid, save_dir) == before


@pytest.mark.parametrize("seat", NON_WHITE, ids=str)
def test_seat_declaration_refused_for_non_white(seat, save_dir):
    c, api = _client()
    sid = _draft_with_asset(c)
    before = c.get(f"/api/sessions/{sid}/creator/seats").json()
    r = _call(c, "creator_seats", sid, seat)
    assert r.status_code == 403, r.text
    assert c.get(f"/api/sessions/{sid}/creator/seats").json() == before


@pytest.mark.parametrize("seat", PLAYER_SEATS)
def test_creation_refused_when_it_names_a_player_seat(seat):
    c, api = _client()
    before = len(c.get("/api/sessions").json())
    r1 = c.post("/api/sessions", params={"cell": seat},
                json={"vignette_id": "leo-isr-denial", "seed": 1})
    r2 = c.post("/api/sessions/draft", params={"cell": seat}, json={"title": "x"})
    assert r1.status_code == 403 and r2.status_code == 403
    assert r1.json()["detail"] and r2.json()["detail"]
    assert len(c.get("/api/sessions").json()) == before
    assert len(api._sessions) == before


def test_save_vignette_writes_nothing_for_refused_seat_and_one_file_for_white(save_dir):
    c, api = _client()
    sid = _draft_with_asset(c)
    for seat in NON_WHITE:
        assert _call(c, "save_vignette", sid, seat).status_code == 403
    assert list(save_dir.iterdir()) == []
    r = _call(c, "save_vignette", sid, "white")
    assert r.status_code == 200, r.text
    assert len(list(save_dir.iterdir())) == 1


def test_white_succeeds_everywhere(save_dir):
    c, api = _client()
    r = c.post("/api/sessions", params={"cell": "white"}, json={"vignette_id": "leo-isr-denial", "seed": 1})
    assert r.status_code == 200
    started = r.json()["session"]
    assert c.post("/api/sessions/draft", params={"cell": "white"}, json={"title": "x"}).status_code == 200
    sid = _draft_with_asset(c)
    assert _call(c, "creator_asset_patch", sid, "white").status_code == 200
    assert _call(c, "creator_state_put", sid, "white").status_code == 200
    assert _call(c, "creator_seats", sid, "white").status_code == 200
    assert _call(c, "save_vignette", sid, "white").status_code == 200
    assert c.post(f"/api/sessions/{sid}/force/tle", params={"cell": "white"},
                  json={"id": "WO2-SAT", "line1": TLE1, "line2": TLE2, "owner": "blue"}).status_code == 200
    assert _call(c, "creator_asset_delete", sid, "white").status_code == 200
    assert c.post(f"/api/sessions/{started}/start", params={"cell": "white"}).status_code == 200
    assert _call(c, "red_step", started, "white").status_code == 200


def test_creation_with_no_seat_still_works():
    c, _ = _client()
    assert c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).status_code == 200
    assert c.post("/api/sessions/draft", json={"title": "x"}).status_code == 200


@pytest.mark.parametrize("seat", ["white", "blue", None], ids=str)
@pytest.mark.parametrize("name", IN_SESSION)
def test_unknown_session_is_404_before_seat_check(name, seat):
    c, _ = _client()
    assert _call(c, name, "sess-nope", seat).status_code == 404


def test_draft_reads_stay_open_with_no_seat(save_dir):
    c, _ = _client()
    sid = _draft_with_asset(c)
    for path in ("creator/state", "creator/scene", "creator/seats"):
        assert c.get(f"/api/sessions/{sid}/{path}").status_code == 200
