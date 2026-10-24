"""IP-1076 — time advance bounded to the exercise span (FR-4330): ``[now, start_epoch + 366 days]``.
A refused advance/step is HTTP 400 with a reason and changes nothing; the running clock stops at the
span end; every reachable session saves and loads."""

from __future__ import annotations

import random

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.content.vignette import load_vignette  # noqa: E402
from spacesim.session.api import Ack  # noqa: E402
from spacesim.session.manager import SessionManager  # noqa: E402
from spacesim.ui_web.server import create_app  # noqa: E402

pytestmark = pytest.mark.verifies("FR-4330", "NFR-1600")

W = {"cell": "white"}
VIG = "leo-isr-denial"
DAY = 86400 * 1_000_000
SPAN = SessionManager.MAX_SAVE_SPAN_US


def _client():
    app = create_app()
    return TestClient(app), app.state.api


def _started(c):
    sid = c.post("/api/sessions", json={"vignette_id": VIG, "seed": 1}).json()["session"]
    assert c.post(f"/api/sessions/{sid}/start", params=W).status_code == 200
    assert c.post(f"/api/sessions/{sid}/clock", json={"running": False}, params=W).status_code == 200
    return sid


def _state(api, sid):
    m = api._sessions[sid]
    return (m.sim.clock.now, len(api.get_eventlog(sid, 0)), m._clock_running)


def _adv(c, sid, t, **kw):
    return c.post(f"/api/sessions/{sid}/advance", json={"t": t}, params=W, **kw)


def _step(c, sid, dt):
    return c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": dt}, params=W)


def _save_loads(c, sid):
    save = c.get(f"/api/sessions/{sid}/save").json()
    return c.post("/api/sessions/load_save", json=save, params=W)


def _to_ceiling(c, api, sid):
    m = api._sessions[sid]
    ceiling = m.ctx.start_epoch + SPAN
    t = m.sim.clock.now
    while t < ceiling:
        t = min(ceiling, t + 30 * DAY)
        assert _adv(c, sid, t).status_code == 200
    return ceiling


# 1
def test_advance_to_the_ceiling_ok_one_microsecond_more_refused():
    c, api = _client()
    sid = _started(c)
    ceiling = _to_ceiling(c, api, sid)
    assert api._sessions[sid].sim.clock.now == ceiling
    before = _state(api, sid)
    r = _adv(c, sid, ceiling + 1)
    assert r.status_code == 400
    assert "span" in r.json()["detail"].lower() or "366" in r.json()["detail"]
    assert _state(api, sid) == before


# 2
def test_backwards_advance_is_400_and_equal_is_a_noop():
    c, api = _client()
    sid = _started(c)
    assert _step(c, sid, 120.0).status_code == 200
    now = api._sessions[sid].sim.clock.now
    before = _state(api, sid)
    r = _adv(c, sid, now - 1)
    assert r.status_code == 400 and r.json()["detail"]
    assert _state(api, sid) == before
    assert _adv(c, sid, now).status_code == 200
    assert _state(api, sid) == before


# 3
def test_negative_step_is_400_zero_is_ok():
    c, api = _client()
    sid = _started(c)
    assert _step(c, sid, 60.0).status_code == 200
    before = _state(api, sid)
    assert _step(c, sid, -5.0).status_code == 400
    assert _state(api, sid) == before
    assert _step(c, sid, 0.0).status_code == 200
    assert _state(api, sid) == before


# 4
def test_non_finite_and_huge_step_are_400_never_500():
    c, api = _client()
    sid = _started(c)
    before = _state(api, sid)
    for body in ('{"dt_sim_s": NaN}', '{"dt_sim_s": Infinity}', '{"dt_sim_s": -Infinity}',
                 '{"dt_sim_s": 1e300}'):
        r = c.post(f"/api/sessions/{sid}/step", content=body, params=W,
                   headers={"content-type": "application/json"})
        assert r.status_code in (400, 422), (body, r.status_code)
        if r.status_code == 400:
            assert r.json()["detail"]
    r = _step(c, sid, 1e300)
    assert r.status_code == 400
    assert _state(api, sid) == before


# 5
def test_over_advanced_session_can_no_longer_be_produced_so_every_save_loads():
    c, api = _client()
    sid = _started(c)
    start = api._sessions[sid].ctx.start_epoch
    assert _adv(c, sid, start + 30 * DAY).status_code == 200
    assert _save_loads(c, sid).status_code == 200
    ceiling = _to_ceiling(c, api, sid)
    assert _save_loads(c, sid).status_code == 200
    assert _adv(c, sid, start + 370 * DAY).status_code == 400
    assert api._sessions[sid].sim.clock.now == ceiling


# 6
def test_lazy_clock_is_clamped_at_the_ceiling():
    c, api = _client()
    sid = _started(c)
    m = api._sessions[sid]
    ceiling = m.ctx.start_epoch + SPAN
    m.set_clock(True, rate=1.0)
    m._sim_anchor = ceiling - 5_000_000          # anchor 5 sim-s below the ceiling ...
    m._wall_anchor -= 3600                        # ... with an hour of wall time elapsed
    m.sim.advance_to(m._sim_anchor) if m.sim.clock.now < m._sim_anchor else None
    m.catch_up()
    assert m.sim.clock.now == ceiling
    m.catch_up()                                  # pinned: a further catch-up is a no-op
    assert m.sim.clock.now == ceiling
    assert _save_loads(c, sid).status_code == 200


# 7
def test_bounds_are_measured_from_the_start_epoch_after_rewind_or_undo():
    c, api = _client()
    sid = _started(c)
    m = api._sessions[sid]
    start = m.ctx.start_epoch
    assert _adv(c, sid, start + 10 * DAY).status_code == 200
    assert c.post(f"/api/sessions/{sid}/rewind", json={"t": start + 60_000_000}, params=W).status_code == 200
    assert _adv(c, sid, start + SPAN).status_code == 200
    assert _adv(c, sid, start + SPAN + 1).status_code == 400
    assert c.post(f"/api/sessions/{sid}/rewind", json={"t": start}, params=W).status_code == 200
    assert _adv(c, sid, start + SPAN + 1).status_code == 400
    assert _adv(c, sid, start + SPAN).status_code == 200


# 8
def test_layering_value_error_then_ack_then_400():
    c, api = _client()
    sid = _started(c)
    m = api._sessions[sid]
    before = _state(api, sid)
    with pytest.raises(ValueError):
        m.advance_to(m.ctx.start_epoch + SPAN + 1)
    with pytest.raises(ValueError):
        m.step(float("nan"))
    with pytest.raises(ValueError):
        m.step(-1.0)
    for ack in (api.advance_to(sid, m.ctx.start_epoch + SPAN + 1), api.step(sid, float("inf")),
                api.step(sid, -1.0), api.advance_to(sid, m.sim.clock.now - 1)):
        assert isinstance(ack, Ack) and ack.ok is False and ack.reason
    assert _state(api, sid) == before
    assert _adv(c, sid, m.ctx.start_epoch + SPAN + 1).status_code == 400


# 9
@pytest.mark.verifies("FR-4310", "FR-4320")
def test_seat_check_precedes_the_bound():
    c, api = _client()
    sid = _started(c)
    far = api._sessions[sid].ctx.start_epoch + 999 * DAY
    before = _state(api, sid)
    for params in ({"cell": "blue"}, {"cell": "red"}, {"cell": "observer"}, {}):
        assert c.post(f"/api/sessions/{sid}/advance", json={"t": far}, params=params).status_code == 403
        assert c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": -5.0}, params=params).status_code == 403
    assert _state(api, sid) == before


# 10
@pytest.mark.verifies("FR-4310")
def test_draft_sessions_keep_their_refusal():
    c, api = _client()
    dsid = api.create_draft_session(VIG)
    for ack in (api.advance_to(dsid, 0), api.step(dsid, 10.0)):
        assert ack.ok is False and "draft" in ack.reason


# 11
def test_invariant_now_stays_inside_the_span_over_random_sequences():
    rng = random.Random(1076)
    c, api = _client()
    sid = _started(c)
    m = api._sessions[sid]
    lo, hi = m.ctx.start_epoch, m.ctx.start_epoch + SPAN
    for _ in range(60):
        op = rng.choice(["step", "adv", "rewind", "undo"])
        if op == "step":
            api.step(sid, rng.choice([60.0, 3600.0, 40 * 86400.0, 400 * 86400.0, -30.0]))
        elif op == "adv":
            api.advance_to(sid, lo + rng.randint(-DAY, 400 * DAY))
        elif op == "rewind":
            api.rewind_to(sid, lo + rng.randint(0, 366 * DAY))
        else:
            api.undo_last(sid, 1)
        assert lo <= m.sim.clock.now <= hi
    assert _save_loads(c, sid).status_code == 200


# 12
def test_refusals_log_nothing_event_log_equals_accepted_only():
    def run(with_refusals):
        m = SessionManager(load_vignette(VIG), seed=3)
        m.start()
        m.set_clock(False)
        base = m.sim.clock.now      # pausing folds in a few wall microseconds (tick phase too); compare relative offsets
        for dt in (600.0, 1200.0):
            if with_refusals:
                for bad in (lambda: m.step(-1.0), lambda: m.step(float("nan")),
                            lambda: m.advance_to(m.ctx.start_epoch + SPAN + 1),
                            lambda: m.advance_to(m.sim.clock.now - 1)):
                    with pytest.raises(ValueError):
                        bad()
            m.step(dt)
        ents = m.sim.eventlog.entries
        return [(e.sim_time - ents[0].sim_time, e.kind) for e in ents], m.sim.clock.now - base

    assert run(True) == run(False)


# 13
@pytest.mark.verifies("IP-1076")
def test_session_advanced_to_the_ceiling_replays_from_its_own_event_log():
    c, api = _client()
    sid = _started(c)
    ceiling = _to_ceiling(c, api, sid)
    m = api._sessions[sid]
    r = _save_loads(c, sid)
    assert r.status_code == 200
    sid2 = r.json()["session"]
    m2 = api._sessions[sid2]
    assert m2.sim.clock.now == ceiling
    assert [(e.sim_time, e.kind) for e in m2.sim.eventlog.entries] == \
           [(e.sim_time, e.kind) for e in m.sim.eventlog.entries]
