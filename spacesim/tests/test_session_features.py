"""Save/resume, AAR scrubber snapshots, and the fleet alarms feed."""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.orders import Order
from spacesim.session import aar
from spacesim.session.manager import SessionManager
from spacesim.session.redai import RedDoctrine
from spacesim.engine.simtime import minutes


def _capstone():
    mgr = SessionManager(load_vignette("multi-domain-taiwan"), seed=3)
    mgr.start()
    return mgr


def test_save_resume_reproduces_state_and_queue():
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    mgr.issue_order("blue", Order(cell="blue", actor="RADAR-TRN", action="observe", target="RED-TGT",
                                  params={"intent": "characterize"}))
    dl = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"}))
    mgr.step(120)  # advance a little (history accrues; the downlink is still queued ahead)

    state = mgr.save_state()
    resumed = SessionManager.from_state(state)

    # World, clock, and objectives are reproduced exactly.
    assert resumed.sim.clock.now == mgr.sim.clock.now
    assert resumed.get_godview().model_dump_json() == mgr.get_godview().model_dump_json()
    assert resumed.objectives() == mgr.objectives()
    # The queued (not-yet-executed) downlink survived the round-trip…
    rq = {o["id"]: o for o in resumed.list_orders("blue")}
    assert rq[dl.id]["status"] == "queued"
    # …and still fires on resume, delivering imagery exactly as the original would have.
    resumed.advance_to(dl.earliest_window[1] + 1)
    mgr.advance_to(dl.earliest_window[1] + 1)
    assert resumed.world.mission.get("imagery_delivered") is True
    assert resumed.get_godview().model_dump_json() == mgr.get_godview().model_dump_json()


def test_aar_snapshot_scrubs_read_only_across_the_campaign():
    mgr = _capstone()
    RedDoctrine(mgr).step()
    mgr.advance_to(mgr.world.now + minutes(2))
    live_now = mgr.sim.clock.now

    start = aar.snapshot_at(mgr, seq=0)
    end = aar.snapshot_at(mgr, seq=None)
    assert start["objectives"] != end["objectives"]      # the campaign changed the outcome
    assert end["n_events"] >= start["seq"]
    assert mgr.sim.clock.now == live_now                  # scrubbing never disturbs the live session


def test_alarms_feed_lists_symptoms_for_own_assets_only():
    mgr = _capstone()
    RedDoctrine(mgr).step()
    mgr.advance_to(mgr.world.now + minutes(2))            # cyber safes SATCOM-1
    blue = mgr.alarms("blue")
    assert any(a["asset"] == "SATCOM-1" for a in blue)    # the safed bird raises alarms
    # Fog: Red's feed never names a Blue asset.
    assert all(a["asset"] != "SATCOM-1" for a in mgr.alarms("red"))
