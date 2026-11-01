"""IP-1075 — Undo cannot leave the exercise: the sim clock never goes before ``start_epoch``,
an undo with nothing to undo is refused (400), and undo re-arms the tick schedule (FS-106 v2.4)."""

from __future__ import annotations

import random

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.content.vignette import load_vignette  # noqa: E402
from spacesim.engine.simulation import Simulation  # noqa: E402
from spacesim.session.manager import SessionManager  # noqa: E402
from spacesim.ui_web.server import create_app  # noqa: E402

pytestmark = pytest.mark.verifies("FR-4330", "NFR-1600")

W = {"cell": "white"}
VIG = "leo-isr-denial"


def _mgr(seed=1):
    m = SessionManager(load_vignette(VIG), seed=seed)
    m.start()
    m.set_clock(False)
    return m


def _step_until_logged(m, n=1):
    while len(m.sim.eventlog.entries) < n:
        m.step(300)


def _client():
    app = create_app()
    return TestClient(app), app.state.api


def _started(c):
    sid = c.post("/api/sessions", json={"vignette_id": VIG, "seed": 1}).json()["session"]
    assert c.post(f"/api/sessions/{sid}/start", params=W).status_code == 200
    assert c.post(f"/api/sessions/{sid}/clock", json={"running": False}, params=W).status_code == 200
    return sid


# 1
def test_undo_on_empty_log_is_refused_and_changes_nothing():
    m = _mgr()
    assert len(m.sim.eventlog.entries) == 0
    now = m.sim.clock.now
    with pytest.raises(ValueError):
        m.undo_last()
    assert m.sim.clock.now == now and len(m.sim.eventlog.entries) == 0


def test_undo_on_empty_log_is_400_over_http_and_clock_unchanged():
    c, api = _client()
    sid = _started(c)
    before = c.get(f"/api/sessions/{sid}/clock").json()
    r = c.post(f"/api/sessions/{sid}/undo", json={"n": 1}, params=W)
    assert r.status_code == 400 and r.json()["detail"]
    assert c.get(f"/api/sessions/{sid}/clock").json()["now"] == before["now"]


# 2
@pytest.mark.parametrize("n", [0, -1])
def test_undo_with_nonpositive_n_is_refused(n):
    m = _mgr()
    _step_until_logged(m)
    now, k = m.sim.clock.now, len(m.sim.eventlog.entries)
    with pytest.raises(ValueError):
        m.undo_last(n)
    assert (m.sim.clock.now, len(m.sim.eventlog.entries)) == (now, k)


# 3
def test_undo_of_the_only_entry_lands_on_start_epoch_not_1970():
    m = _mgr()
    _step_until_logged(m)
    while len(m.sim.eventlog.entries) > 1:
        m.undo_last()
    m.undo_last()
    assert m.sim.clock.now == m.ctx.start_epoch != 0


# 4
def test_oversized_n_lands_on_start_epoch_with_empty_log():
    m = _mgr()
    _step_until_logged(m, 2)
    m.undo_last(len(m.sim.eventlog.entries) + 5)
    assert m.sim.clock.now == m.ctx.start_epoch
    assert len(m.sim.eventlog.entries) == 0


# 5
def test_rewind_to_start_works_after_undo_to_start():
    c, api = _client()
    sid = _started(c)
    c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 400.0}, params=W)
    n = len(api.get_eventlog(sid, 0))
    assert n >= 1
    assert c.post(f"/api/sessions/{sid}/undo", json={"n": n + 3}, params=W).status_code == 200
    start = c.get(f"/api/sessions/{sid}/clock").json()["start_epoch"]
    assert c.get(f"/api/sessions/{sid}/clock").json()["now"] == start
    assert c.post(f"/api/sessions/{sid}/rewind", json={"t": start}, params=W).status_code == 200


# 6
def test_partial_undo_lands_on_last_surviving_entry():
    m = _mgr()
    _step_until_logged(m, 3)
    entries = m.sim.eventlog.entries
    expect = entries[-2].sim_time
    m.undo_last()
    assert m.sim.clock.now == expect >= m.ctx.start_epoch


# 7
@pytest.mark.parametrize("seed", range(5))
def test_now_never_before_start_over_random_control_sequences(seed):
    rng = random.Random(seed)
    m = _mgr(seed=seed + 1)
    start = m.ctx.start_epoch
    for _ in range(40):
        op = rng.choice(["step", "undo", "undo", "rewind", "advance"])
        try:
            if op == "step":
                m.step(rng.choice([60, 300, 700]))
            elif op == "undo":
                m.undo_last(rng.choice([-1, 0, 1, 2, 50]))
            elif op == "rewind":
                m.rewind_to(rng.randint(start - 10**9, m.sim.clock.now + 10**9))
            else:
                m.advance_to(m.sim.clock.now + rng.randint(-10**9, 10**9))
        except ValueError:
            pass
        assert m.sim.clock.now >= start


# 8
def test_bus_ticks_resume_after_undo():
    m = _mgr()
    _step_until_logged(m, 2)
    m.undo_last()
    k = sum(e.kind == "bus_tick" for e in m.sim.eventlog.entries)
    m.step(1200)
    assert sum(e.kind == "bus_tick" for e in m.sim.eventlog.entries) > k


def test_undo_to_start_then_step_resumes_ticks():
    m = _mgr()
    _step_until_logged(m)
    m.undo_last(99)
    m.step(1200)
    assert any(e.kind == "bus_tick" for e in m.sim.eventlog.entries)


# 9
def test_running_clock_reanchors_at_start_after_undo(monkeypatch):
    import spacesim.session.manager as mod
    m = _mgr()
    _step_until_logged(m)
    m.set_clock(True)
    m.undo_last(99)
    assert m._sim_anchor == m.ctx.start_epoch
    m.catch_up()
    assert m.sim.clock.now >= m.ctx.start_epoch > 0


# 10
@pytest.mark.verifies("FR-4330")
def test_engine_undo_on_empty_log_keeps_initial_time():
    m = _mgr()
    sim: Simulation = m.sim
    # (the lazy clock may have moved a few microseconds before set_clock(False); the engine
    # must land on the *initial* time, which is the exercise start, not on 0 or on `now`)
    sim.undo_last(1)
    assert sim.clock.now == m.ctx.start_epoch != 0


# 11
@pytest.mark.verifies("FR-7220", "FR-4330")
def test_save_after_undo_to_start_validates_and_reloads():
    m = _mgr()
    _step_until_logged(m)
    m.undo_last(99)
    state = m.save_state()
    SessionManager.validate_save(state)
    m2 = SessionManager.from_state(state)
    assert m2.sim.clock.now == m2.ctx.start_epoch
    bad = dict(state, final_time=m.ctx.start_epoch - 1)
    with pytest.raises(ValueError):
        SessionManager.validate_save(bad)


# 12
@pytest.mark.verifies("FR-4330")
@pytest.mark.parametrize("seat", ["observer", "blue", "red", None])
def test_undo_still_403_for_non_white(seat):
    c, api = _client()
    sid = _started(c)
    c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 400.0}, params=W)
    params = {} if seat is None else {"cell": seat}
    r = c.post(f"/api/sessions/{sid}/undo", json={"n": 1}, params=params)
    assert r.status_code == 403
