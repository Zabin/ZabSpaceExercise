"""Phase 7: capstone Vignette 8 — a synchronized Red campaign + AAR replay/scrub/branch-compare."""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.session import aar
from spacesim.session.manager import SessionManager
from spacesim.session.redai import RedDoctrine
from spacesim.engine.simtime import minutes


def _campaign(overrides=None):
    mgr = SessionManager(load_vignette("multi-domain-taiwan"), overrides=overrides, seed=1)
    mgr.start()
    return mgr


def test_capstone_runs_a_synchronized_red_campaign():
    mgr = _campaign()
    acks = RedDoctrine(mgr).step()  # china_integrated: jam + cyber together
    assert sum(a.status == "queued" for a in acks) >= 2
    mgr.advance_to(mgr.world.now + minutes(1))
    # The cyber arm safes the SATCOM bird; the AAR shows it.
    assert mgr.world.assets["SATCOM-1"].bus_state.mode == "safe_mode"
    rep = aar.report(mgr)
    assert rep.vignette == "multi-domain-taiwan"
    assert rep.timeline and any("cyber" in e.summary for e in rep.timeline)


def test_state_at_time_reconstructs_world_at_arbitrary_time():
    """IP-1210 (FR-7410/FR-7420) — state_at_time()'s applied-event set matches exactly the
    events with sim_time <= t, and world.now == t (not the last applied event's own time)."""
    mgr = _campaign()
    RedDoctrine(mgr).step()
    mgr.advance_to(mgr.world.now + minutes(1))

    mid_t = mgr.sim.eventlog.entries[0].sim_time
    world_at_mid = aar.state_at_time(mgr, mid_t)
    assert world_at_mid.now == mid_t
    expected_seq = sum(1 for e in mgr.sim.eventlog.entries if e.sim_time <= mid_t)
    world_at_seq = aar.state_at(mgr, seq=expected_seq)
    world_at_seq.now = mid_t  # state_at() doesn't pin final_time; align before comparing
    assert world_at_mid.model_dump() == world_at_seq.model_dump()

    # Read-only: the live sim is untouched.
    live_now = mgr.sim.clock.now
    aar.state_at_time(mgr, mid_t)
    assert mgr.sim.clock.now == live_now


def test_aar_scrub_is_read_only_and_reconstructs_earlier_state():
    mgr = _campaign()
    RedDoctrine(mgr).step()
    mgr.advance_to(mgr.world.now + minutes(1))
    live_now = mgr.sim.clock.now

    # Objectives at the very start vs at the end differ; scrubbing must not disturb the live sim.
    early = aar.objectives_at(mgr, seq=0)
    final = aar.objectives_at(mgr, seq=None)
    assert early["red"]["disable_satcom"] is False
    assert final["red"]["disable_satcom"] is True
    assert mgr.sim.clock.now == live_now            # read-only replay left the live clock alone
    assert mgr.world.assets["SATCOM-1"].bus_state.mode == "safe_mode"


def test_branch_comparison_shows_objective_flip():
    # Branch A: Red cyber safes the SATCOM (modem unpatched).
    a = _campaign()
    RedDoctrine(a).step()
    a.advance_to(a.world.now + minutes(1))
    report_a = aar.report(a)
    assert report_a.final_objectives["red"]["disable_satcom"] is True

    # Branch B: Blue patches the modem first, so the same Red campaign fails to safe SATCOM.
    b = _campaign()
    b.fire_inject("patch_modem")
    RedDoctrine(b).step()
    b.advance_to(b.world.now + minutes(1))
    report_b = aar.report(b)
    assert report_b.final_objectives["red"]["disable_satcom"] is False

    diff = aar.compare_branches(report_a, report_b)
    assert "red.disable_satcom" in diff["objective_flips"]
    assert diff["objective_flips"]["red.disable_satcom"] == {"a": True, "b": False}
