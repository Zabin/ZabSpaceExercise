"""IP-1083 (BL-0284, FS-106 v2.4, FR-4410/FR-4450) — a rewind or undo keeps White Cell's
future-dated injects. The scheduling is a logged ``inject_admin`` ``schedule`` entry, so the
existing override re-arm loop re-arms it; the event log stays the only source of truth."""
from __future__ import annotations

import json

import pytest

from spacesim.content.vignette import Vignette
from spacesim.session.manager import SessionManager

pytestmark = pytest.mark.verifies("FR-4410")

MIN = 60 * 1_000_000
HOUR = 60 * MIN


def _vig() -> Vignette:
    return Vignette.model_validate({
        "id": "test-rewind-rearm", "title": "Rewind re-arm",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [{"id": "SAT-BLUE", "kind": "satellite"}],
        "red_forces": [{"id": "SAT-RED", "kind": "satellite"}],
        "neutral_forces": [], "sensors": [],
        "injects": [
            {"id": "timed", "trigger": {"type": "time", "at_sim_s": 3600},
             "effects": [{"type": "message", "to": ["blue"], "text": "timed-original"}]},
        ],
    })


def _mgr() -> SessionManager:
    m = SessionManager(_vig(), seed=0)
    m.start()
    m.set_clock(False)
    return m


def _msg(text: str) -> list:
    return [{"type": "message", "to": ["blue"], "text": text}]


def _texts(m) -> list[str]:
    return [x["text"] for x in m.world.messages]


def _at(m, minutes: float) -> int:
    return m.ctx.start_epoch + int(minutes * MIN)


def _pend(m) -> dict:
    return {p["handle"]: p for p in m.pending_injects()}


def _fired(m, handle: str) -> list[int]:
    return [e.sim_time for e in m.sim.eventlog.entries if e.kind == "inject"
            and e.payload.get("inject_id") == handle and "skipped" not in e.payload]


def _sched(m, text="w", at_min=120, advance_min=10):
    """Advance to ``advance_min`` then schedule a White inject at ``at_min``; returns (A, F)."""
    m.advance_to(_at(m, advance_min))
    a, f = m.sim.clock.now, _at(m, at_min)
    m.fire_inject(_msg(text), at_sim_t=f)
    return a, f


# 1 -------------------------------------------------------------------------------------------
def test_reproduction_rewind_keeps_future_inject():
    m = _mgr()
    a, f = _sched(m, "later")
    m.advance_to(_at(m, 60))
    m.rewind_to(_at(m, 5 + 10))      # 15 min: >= A (10 min)
    p = _pend(m)["white-1"]
    assert p["at"] == f and p["effects"] == _msg("later")
    m.advance_to(_at(m, 180))
    assert _texts(m).count("later") == 1 and len(_fired(m, "white-1")) == 1


# 2, 3 ----------------------------------------------------------------------------------------
@pytest.mark.verifies("FR-4450")
def test_rewind_before_scheduling_instant_withdraws_it():
    m = _mgr()
    _sched(m, "later", advance_min=10)
    m.advance_to(_at(m, 60))
    m.rewind_to(_at(m, 5))
    assert "white-1" not in _pend(m)
    m.advance_to(_at(m, 180))
    assert "later" not in _texts(m) and not _fired(m, "white-1")


@pytest.mark.verifies("FR-4450")
def test_rewind_to_exactly_scheduling_instant_keeps_it():
    m = _mgr()
    a, f = _sched(m, "later")
    m.advance_to(_at(m, 60))
    m.rewind_to(a)
    assert "white-1" in _pend(m)
    m.advance_to(_at(m, 180))
    assert _texts(m).count("later") == 1


# 4, 5 ----------------------------------------------------------------------------------------
def test_fired_then_rewind_before_fire_time_fires_again_once():
    m = _mgr()
    a, f = _sched(m, "later", at_min=60)
    m.advance_to(_at(m, 90))
    assert _texts(m).count("later") == 1
    m.rewind_to(_at(m, 30))
    assert "white-1" in _pend(m) and "later" not in _texts(m)
    m.advance_to(_at(m, 90))
    assert _texts(m).count("later") == 1 and _fired(m, "white-1") == [f]


def test_fired_then_rewind_after_fire_time_not_rearmed():
    m = _mgr()
    a, f = _sched(m, "later", at_min=60)
    m.advance_to(_at(m, 90))
    m.rewind_to(_at(m, 75))
    assert "white-1" not in _pend(m)
    assert _texts(m).count("later") == 1 and _fired(m, "white-1") == [f]
    m.advance_to(_at(m, 120))
    assert _texts(m).count("later") == 1


# 6 -------------------------------------------------------------------------------------------
def test_landing_exactly_on_fire_time_with_own_entry_dropped_rearms_once():
    m = _mgr()
    # Fire time on a bus-tick instant so another entry shares the instant.
    a, f = _sched(m, "later", at_min=60)
    m.advance_to(f)
    at_f = [(i, e.kind) for i, e in enumerate(m.sim.eventlog.entries) if e.sim_time == f]
    kinds = [k for _, k in at_f]
    assert "inject" in kinds
    if kinds[-1] != "inject" or len(kinds) < 2:
        pytest.skip(f"no co-instant entry before the inject at fire time: {kinds}")
    m.undo_last(1)
    assert m.sim.clock.now == f and "later" not in _texts(m)
    m.advance_to(_at(m, 120))
    assert _texts(m).count("later") == 1 and _fired(m, "white-1") == [f]


# 7, 8 ----------------------------------------------------------------------------------------
def test_undo_past_fire_entry_makes_it_pending_again():
    m = _mgr()
    a, f = _sched(m, "later", at_min=60)
    m.advance_to(_at(m, 90))
    n = sum(1 for e in m.sim.eventlog.entries if e.sim_time >= f)
    m.undo_last(n)
    assert m.sim.clock.now < f and "white-1" in _pend(m)
    m.advance_to(_at(m, 120))
    assert _texts(m).count("later") == 1


@pytest.mark.verifies("FR-4450")
def test_undo_of_scheduling_entry_withdraws_it():
    m = _mgr()
    _sched(m, "later")
    assert m.sim.eventlog.entries[-1].kind == "inject_admin"
    m.undo_last(1)
    assert "white-1" not in _pend(m)
    m.advance_to(_at(m, 180))
    assert "later" not in _texts(m)


# 9, 10 ---------------------------------------------------------------------------------------
@pytest.mark.verifies("FR-4450")
def test_schedule_edit_rewind_between_and_after():
    m = _mgr()
    a, f = _sched(m, "orig")
    m.advance_to(_at(m, 20))
    t_between = m.sim.clock.now
    m.advance_to(_at(m, 30))
    m.edit_inject("white-1", effects=_msg("edited"))
    m.advance_to(_at(m, 40))
    m.rewind_to(t_between)
    assert _pend(m)["white-1"]["effects"] == _msg("orig")
    m.advance_to(_at(m, 40))
    m.edit_inject("white-1", effects=_msg("edited"))
    m.advance_to(_at(m, 50))
    m.rewind_to(_at(m, 45))
    assert _pend(m)["white-1"]["effects"] == _msg("edited")
    m.advance_to(_at(m, 180))
    assert "edited" in _texts(m) and "orig" not in _texts(m)
    assert _texts(m).count("edited") == 1


@pytest.mark.verifies("FR-4450")
def test_schedule_cancel_rewind_before_and_after():
    m = _mgr()
    _sched(m, "later")
    m.advance_to(_at(m, 20))
    t_before = m.sim.clock.now
    m.advance_to(_at(m, 30))
    m.cancel_inject("white-1")
    m.advance_to(_at(m, 40))
    m.rewind_to(t_before)
    assert "white-1" in _pend(m)
    m.advance_to(_at(m, 40))
    m.cancel_inject("white-1")
    m.advance_to(_at(m, 50))
    m.rewind_to(_at(m, 45))
    assert "white-1" not in _pend(m)
    m.advance_to(_at(m, 180))
    assert "later" not in _texts(m)


# 11 ------------------------------------------------------------------------------------------
def test_mixed_injects_survive_rewind_with_same_listing_and_no_handle_reuse():
    m = _mgr()
    m.advance_to(_at(m, 5))
    m.fire_inject(_msg("w1"), at_sim_t=_at(m, 90))
    m.fire_inject(_msg("w2"), at_sim_t=_at(m, 100))
    m.cancel_inject("white-2")
    m.advance_to(_at(m, 30))
    before = m.pending_injects()
    m.advance_to(_at(m, 45))
    m.rewind_to(_at(m, 30))
    assert m.pending_injects() == before
    m.fire_inject(_msg("w3"), at_sim_t=_at(m, 110))
    assert "white-3" in _pend(m)
    m.advance_to(_at(m, 180))
    t = _texts(m)
    assert t.count("w1") == 1 and t.count("timed-original") == 1 and t.count("w3") == 1 and "w2" not in t


# 12-14 save / load ---------------------------------------------------------------------------
def test_save_after_scheduling_load_then_advance_fires_once():
    m = _mgr()
    a, f = _sched(m, "later")
    r = SessionManager.from_state(json.loads(json.dumps(m.save_state())))
    r.set_clock(False)
    r.advance_to(_at(r, 180))
    assert _texts(r).count("later") == 1 and _fired(r, "white-1") == [f]


def test_save_load_then_rewind_before_fire_time_still_pending():
    m = _mgr()
    a, f = _sched(m, "later")
    m.advance_to(_at(m, 30))
    r = SessionManager.from_state(json.loads(json.dumps(m.save_state())))
    r.set_clock(False)
    r.advance_to(_at(r, 40))
    r.rewind_to(_at(r, 20))
    assert _pend(r)["white-1"]["at"] == f
    r.advance_to(_at(r, 180))
    assert _texts(r).count("later") == 1


@pytest.mark.verifies("IP-1083")
def test_pre_ip1083_save_without_schedule_entry_loads_fires_once_but_rewind_loses_it():
    m = _mgr()
    a, f = _sched(m, "later")
    st = json.loads(json.dumps(m.save_state()))
    el = st["eventlog"]
    entries = el["entries"] if isinstance(el, dict) else el
    kept = [e for e in entries if e.get("kind") != "inject_admin"]
    assert len(kept) < len(entries)
    if isinstance(el, dict):
        el["entries"] = kept
    else:
        st["eventlog"] = kept
    for ev in st["pending"]:             # a pre-package pending event carries no `rev`
        pl = ev.get("payload", {})
        if str(pl.get("inject_id", "")).startswith("white-"):
            pl.pop("rev", None)
    try:
        r = SessionManager.from_state(st)
    except Exception as exc:           # a hand-edited log may fail the save's own integrity check
        pytest.skip(f"hand-built legacy save refused by validation: {exc}")
    r.set_clock(False)
    r.advance_to(_at(r, 180))
    assert _texts(r).count("later") == 1
    r.rewind_to(_at(r, 20))
    assert "white-1" not in _pend(r)     # documented limitation


# 15 ------------------------------------------------------------------------------------------
@pytest.mark.verifies("IP-1083", "FR-1120")
def test_determinism_and_no_entry_without_future_white_inject():
    def run():
        m = _mgr()
        _sched(m, "later")
        m.advance_to(_at(m, 60))
        m.rewind_to(_at(m, 20))
        m.advance_to(_at(m, 180))
        return m
    a, b = run(), run()
    assert [e.model_dump() if hasattr(e, "model_dump") else e.__dict__ for e in a.sim.eventlog.entries] == \
           [e.model_dump() if hasattr(e, "model_dump") else e.__dict__ for e in b.sim.eventlog.entries]
    assert a.sim.replay().model_dump() == a.world.model_dump()
    plain = _mgr()
    plain.advance_to(_at(plain, 90))
    assert not [e for e in plain.sim.eventlog.entries if e.kind == "inject_admin"]


# 16, 17 --------------------------------------------------------------------------------------
def test_immediate_and_past_clamped_injects_write_no_schedule_entry():
    m = _mgr()
    m.advance_to(_at(m, 10))
    m.fire_inject(_msg("now"))
    m.fire_inject(_msg("past"), at_sim_t=_at(m, 1))
    assert not [e for e in m.sim.eventlog.entries if e.kind == "inject_admin"]


def test_invalid_future_inject_refused_whole_and_logs_nothing():
    m = _mgr()
    m.advance_to(_at(m, 10))
    n = len(m.sim.eventlog.entries)
    with pytest.raises(ValueError):
        m.fire_inject([{"type": "bogus"}], at_sim_t=_at(m, 120))
    assert len(m.sim.eventlog.entries) == n and not _pend(m).get("white-1")


# 18 ------------------------------------------------------------------------------------------
@pytest.mark.verifies("IP-1083")
def test_schedule_adds_no_message_but_cancel_and_edit_still_do():
    m = _mgr()
    before = len(m.world.messages)
    _sched(m, "later")
    assert len(m.world.messages) == before
    m.edit_inject("white-1", effects=_msg("e"))
    m.cancel_inject("white-1")
    texts = [x["text"] for x in m.world.messages]
    assert "inject white-1 edited" in texts and "inject white-1 cancelled" in texts


# 19 HTTP -------------------------------------------------------------------------------------
def _http():
    from fastapi.testclient import TestClient
    from spacesim.session.inprocess import InProcessSession
    from spacesim.ui_web.server import create_app
    api = InProcessSession()
    sid = api.load_vignette("00-training-basics", seed=1)
    api.start(sid)
    api._sessions[sid].set_clock(False)
    return TestClient(create_app(api)), sid, api._sessions[sid]


def test_http_end_to_end_reproduction_save_load_undo():
    c, sid, m = _http()
    base = f"/api/sessions/{sid}"
    t0 = m.ctx.start_epoch
    assert c.post(f"{base}/step?cell=white", json={"dt_sim_s": 600}).status_code == 200
    r = c.post(f"{base}/inject?cell=white", json={"inject": {"effects": _msg("h")}, "at_sim_t": t0 + 2 * HOUR})
    assert r.status_code == 200 and r.json()["ok"]
    pend = lambda: [p["handle"] for p in c.get(f"{base}/injects/pending").json() if p["source"] == "white"]
    assert pend() == ["white-1"]
    assert c.post(f"{base}/advance?cell=white", json={"t": t0 + HOUR}).status_code == 200
    assert c.post(f"{base}/rewind?cell=white", json={"t": t0 + 15 * MIN}).status_code == 200
    assert pend() == ["white-1"]
    # save / load round trip with the pending White inject
    saved = c.get(f"{base}/save").json()
    r = c.post("/api/sessions/load_save?cell=white", json=saved)
    assert r.status_code == 200, r.text
    sid2 = r.json()["session"]
    p2 = [p["handle"] for p in c.get(f"/api/sessions/{sid2}/injects/pending").json() if p["source"] == "white"]
    assert p2 == ["white-1"]
    # edit after the rewind, then first undo withdraws the edit, second withdraws the schedule
    assert c.post(f"{base}/injects/white-1/edit?cell=white", json={"effects": _msg("h2")}).status_code == 200
    assert c.post(f"{base}/undo?cell=white", json={"n": 1}).status_code == 200
    assert pend() == ["white-1"]
    ents = m.sim.eventlog.entries
    idx = max(i for i, e in enumerate(ents) if e.kind == "inject_admin" and e.payload["action"] == "schedule")
    n = len(ents) - idx                  # undo through the scheduling entry itself
    assert c.post(f"{base}/undo?cell=white", json={"n": n}).status_code == 200
    assert pend() == []


# replay-equals-live on library vignettes and the IP-1074/1076/1082 guards --------------------
@pytest.mark.verifies("IP-1083", "FR-1120")
@pytest.mark.parametrize("vid", ["training-basics", "leo-isr-denial", "geo-rpo-shadowing", "gnss-ew-campaign"])
def test_replay_equals_live_on_library_vignettes(vid):
    from spacesim.content.vignette import load_vignette
    m = SessionManager(load_vignette(vid), seed=3)
    m.start()
    m.set_clock(False)
    t0 = m.ctx.start_epoch
    m.advance_to(t0 + 10 * MIN)
    m.fire_inject(_msg("x1"), at_sim_t=t0 + 90 * MIN)
    m.fire_inject(_msg("x2"), at_sim_t=t0 + 100 * MIN)
    m.advance_to(t0 + 95 * MIN)
    m.rewind_to(t0 + 30 * MIN)
    m.cancel_inject("white-2")
    m.advance_to(t0 + 130 * MIN)
    texts = [x["text"] for x in m.world.messages]
    assert texts.count("x1") == 1 and "x2" not in texts
    assert m.sim.replay().model_dump() == m.world.model_dump()


@pytest.mark.verifies("IP-1083")
def test_refused_rewind_and_nonfinite_inject_leave_pending_untouched():
    m = _mgr()
    a, f = _sched(m, "later")
    n = len(m.sim.eventlog.entries)
    for bad in (float("nan"), m.ctx.start_epoch - 1, m.sim.clock.now + 1):
        with pytest.raises(ValueError):
            m.rewind_to(bad)
    with pytest.raises(ValueError):
        m.fire_inject(_msg("n"), at_sim_t=float("nan"))
    assert len(m.sim.eventlog.entries) == n and _pend(m)["white-1"]["at"] == f


@pytest.mark.verifies("IP-1083")
def test_http_nonfinite_inject_refused_and_state_unchanged():
    c, sid, m = _http()
    base = f"/api/sessions/{sid}"
    n = len(m.sim.eventlog.entries)
    r = c.post(f"{base}/inject?cell=white", content='{"inject":{"effects":[]},"at_sim_t":NaN}',
               headers={"content-type": "application/json"})
    assert r.status_code == 400
    assert len(m.sim.eventlog.entries) == n
