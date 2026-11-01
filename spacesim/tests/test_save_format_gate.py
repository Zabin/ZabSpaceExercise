"""IP-1094 — an unknown or future ``save_format`` is refused before replay (FR-7230)."""

from __future__ import annotations

import copy
import json

import pytest
from fastapi.testclient import TestClient

from spacesim.content.vignette import load_vignette
from spacesim.session.manager import SessionManager
from spacesim.ui_web.server import create_app

pytestmark = pytest.mark.verifies("FR-7230")

LOAD = "/api/sessions/load_save?cell=white"
BAD = [999, 3, 0, -1, "2", True, 2.0, None]


def _good() -> dict:
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=4)
    mgr.start()
    mgr.set_clock(False)
    mgr.step(300)
    return json.loads(json.dumps(mgr.save_state()))


def _client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


@pytest.mark.parametrize("bad", BAD, ids=[repr(b) for b in BAD])
def test_validate_save_refuses_unsupported_format(bad):
    s = _good()
    s["save_format"] = bad
    with pytest.raises(ValueError) as e:
        SessionManager.validate_save(s)
    msg = str(e.value)
    assert "supported formats" in msg and "legacy" in msg and "2" in msg
    assert repr(bad) in msg or str(bad) in msg


@pytest.mark.parametrize("bad", [999, 0, "2", None])
def test_load_save_route_400_names_supported_formats(bad):
    c = _client()
    s = _good()
    s["save_format"] = bad
    before = [x["sid"] for x in c.get("/api/sessions").json()]
    r = c.post(LOAD, json=s)
    assert r.status_code == 400, r.text
    assert "supported formats" in r.json()["detail"]
    assert [x["sid"] for x in c.get("/api/sessions").json()] == before


def test_in_process_load_refuses_before_any_session_is_built():
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    s = _good()
    s["save_format"] = 999
    before = len(api.list_sessions())
    with pytest.raises(ValueError, match="supported formats"):
        api.load_save(s)
    assert len(api.list_sessions()) == before


def test_format_2_round_trips():
    c = _client()
    r = c.post(LOAD, json=_good())
    assert r.status_code == 200, r.text


def test_legacy_save_without_format_still_loads():
    s = copy.deepcopy(_good())
    for k in ("save_format", "content", "baseline", "simulator_version"):
        s.pop(k, None)
    SessionManager.validate_save(s)
    assert _client().post(LOAD, json=s).status_code == 200
