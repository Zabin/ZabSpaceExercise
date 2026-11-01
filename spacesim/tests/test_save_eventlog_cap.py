"""IP-1081 — the load-time event-log cap counts a real save's ``{"entries": [...]}`` log
(NFR-3710, FR-7230, NFR-1600), not only a bare list. No test plays 100,000 events."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import SessionManager
from spacesim.ui_web.server import create_app

from spacesim.tests.test_save_load_robustness import LOAD, _client, _good_state, _sessions

CAP = 100_000


def _rows(n: int) -> list[dict]:
    return [{"seq": i, "sim_time": 0, "kind": "inc_counter", "payload": {"name": "x"}}
            for i in range(n)]


def _with_log(log) -> dict:
    s = _good_state()
    s["eventlog"] = log
    return s


@pytest.mark.verifies("NFR-3710", "FR-7230")
def test_dict_shape_over_cap_refused_with_count_and_limit():
    state = _with_log({"entries": _rows(CAP + 1)})
    with pytest.raises(ValueError, match=r"100001.*100000"):
        SessionManager.validate_save(state)
    c = _client()
    r = c.post(LOAD, json=state)
    assert r.status_code == 400
    assert "100001" in r.json()["detail"] and "100000" in r.json()["detail"]
    assert _sessions(c) == []


@pytest.mark.verifies("NFR-3710")
def test_dict_shape_exactly_at_cap_passes_the_cap():
    state = _with_log({"entries": _rows(CAP)})
    SessionManager.validate_save(state)   # fixture is otherwise valid: no raise


@pytest.mark.verifies("NFR-3710")
def test_bare_list_over_cap_still_refused_same_message():
    state = _with_log(_rows(CAP + 1))
    with pytest.raises(ValueError, match=r"eventlog has 100001 entries; limit is 100000"):
        SessionManager.validate_save(state)
    with pytest.raises(ValueError, match="limit is 100000"):
        InProcessSession().load_save(state)


@pytest.mark.verifies("NFR-1600")
def test_bare_list_at_or_under_cap_refused_as_malformed_not_oversize():
    for n in (3, CAP):
        with pytest.raises(ValueError, match="malformed") as ei:
            SessionManager.validate_save(_with_log(_rows(n)))
        assert "limit is" not in str(ei.value)


@pytest.mark.verifies("NFR-1600")
@pytest.mark.parametrize("log", [None, "abc", 7, True, {"entries": 5}, {"entries": None},
                                 {"entries": "xyz"}])
def test_not_countable_logs_keep_existing_errors(log):
    with pytest.raises(ValueError) as ei:
        SessionManager.validate_save(_with_log(log))
    msg = str(ei.value)
    assert "limit is" not in msg
    assert "missing required key" in msg or "malformed" in msg


@pytest.mark.verifies("NFR-1600")
def test_missing_eventlog_key_unchanged():
    s = _good_state()
    del s["eventlog"]
    with pytest.raises(ValueError, match="missing required key 'eventlog'"):
        SessionManager.validate_save(s)


@pytest.mark.verifies("FR-7230", "NFR-3710")
def test_refusal_consumes_nothing_and_skips_model_validation(monkeypatch):
    from spacesim.engine import eventlog as el
    api = InProcessSession()
    calls = []
    orig = el.EventLog.model_validate.__func__

    def spy(cls, *a, **k):
        calls.append(1)
        return orig(cls, *a, **k)

    monkeypatch.setattr(el.EventLog, "model_validate", classmethod(spy))
    with pytest.raises(ValueError, match="limit is"):
        api.load_save(_with_log({"entries": _rows(CAP + 1)}))
    assert calls == []
    assert api.list_sessions() == [] or len(api.list_sessions()) == 0
    monkeypatch.undo()
    assert api.load_save(_good_state()) == "sess-1"


@pytest.mark.verifies("FR-7210")
def test_valid_saves_still_load():
    api = InProcessSession()
    sid, warnings = api.load_save_with_warnings(_good_state())
    assert sid == "sess-1" and isinstance(warnings, list)


@pytest.mark.verifies("NFR-3710")
def test_constant_alias():
    assert InProcessSession.MAX_EVENTLOG_REPLAY_ENTRIES == SessionManager.MAX_EVENTLOG_REPLAY_ENTRIES == CAP


@pytest.mark.verifies("NFR-1600")
def test_http_over_cap_is_400_json_not_500():
    r = _client().post(LOAD, json=_with_log({"entries": _rows(CAP + 1)}))
    assert r.status_code == 400
    assert isinstance(r.json()["detail"], str)
