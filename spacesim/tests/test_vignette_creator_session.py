"""IP-1173 (FR-5110) — Vignette Creator draft session lifecycle & reverse serialization.

A draft session is an unstarted SessionManager, registered/evicted the same way a normal
session is, that never advances its clock; "Save as Vignette" is the only code path that
writes to VIGNETTE_DIR.
"""
from __future__ import annotations

from pathlib import Path

from spacesim.content.vignette import VIGNETTE_DIR, build_world, load_vignette
from spacesim.session import InProcessSession

# A real, valid TLE pair (ISS, arbitrary epoch) — mirrors the existing force/tle test fixtures'
# convention of using a real satellite's elements so sgp4 validation passes.
_TLE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
_TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"


def test_draft_session_created_and_registered_never_started():
    api = InProcessSession()
    sid = api.create_draft_session(title="My Draft")
    assert sid in api._sessions
    mgr = api._sessions[sid]
    assert mgr.started is False
    assert mgr.sim.eventlog.entries == []


def test_draft_session_accepts_force_edit_before_any_save():
    api = InProcessSession()
    sid = api.create_draft_session()
    ok, reason = api._sessions[sid].add_tle("SAT-1", _TLE1, _TLE2, owner="blue")
    assert ok, reason
    assert "SAT-1" in api._sessions[sid].world.assets


def test_no_partial_vignette_file_written_before_save():
    api = InProcessSession()
    sid = api.create_draft_session(title="Partial")
    api._sessions[sid].add_tle("SAT-2", _TLE1, _TLE2, owner="blue")
    assert not (VIGNETTE_DIR / "test-partial-draft-not-saved.yaml").exists()


def test_save_as_vignette_produces_a_loadable_file():
    api = InProcessSession()
    sid = api.create_draft_session(title="Round Trip")
    ok, reason = api._sessions[sid].add_tle("SAT-3", _TLE1, _TLE2, owner="blue")
    assert ok, reason
    vignette_id = "test-ip1173-round-trip"
    path = api.save_vignette(sid, vignette_id, "Round Trip Test")
    try:
        assert Path(path).exists()
        vig = load_vignette(vignette_id)
        assert vig.title == "Round Trip Test"
        world, ctx = build_world(vig)
        assert "SAT-3" in world.assets
        assert world.assets["SAT-3"].owner == "blue"
    finally:
        Path(path).unlink(missing_ok=True)


def test_no_time_control_route_succeeds_against_a_draft_session():
    api = InProcessSession()
    sid = api.create_draft_session()
    initial_now = api._sessions[sid].sim.clock.now  # the vignette's start_epoch, not 0
    step_ack = api.step(sid, 60.0)
    assert step_ack.ok is False
    advance_ack = api.advance_to(sid, initial_now + 1_000_000)
    assert advance_ack.ok is False
    rewind_ack = api.rewind_to(sid, initial_now)
    assert rewind_ack.ok is False
    undo_ack = api.undo_last(sid)
    assert undo_ack.ok is False
    assert api.red_doctrine_step(sid) == []
    # The clock genuinely never moved.
    assert api._sessions[sid].sim.clock.now == initial_now


def test_draft_session_evicted_by_existing_max_live_sessions_cap():
    api = InProcessSession()
    api.MAX_LIVE_SESSIONS = 2
    sid1 = api.create_draft_session(title="First")
    api.load_vignette("leo-isr-denial")
    sid3 = api.create_draft_session(title="Third")
    # The cap is 2; creating the 3rd session evicted the oldest (sid1).
    assert sid1 not in api._sessions
    assert sid3 in api._sessions
    assert sid1 not in api._draft_sessions
