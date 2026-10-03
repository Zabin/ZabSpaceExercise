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


def test_maneuver_ledger_returns_rows_matching_eventlog_and_is_fog_scoped():
    """IP-1250 (FR-1320) — maneuver_ledger() returns exactly N rows for an Asset with N recorded
    manoeuvres, matching the EventLog; fog-scoped identically to get_telemetry (own assets only,
    White sees any)."""
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    dv = [10.0, 0.0, 0.0]
    ack1 = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="maneuver",
                                         params={"dv": dv, "via": "GS-TRN", "purpose_tag": "raise perigee"}))
    assert ack1.ok
    mgr.advance_to(ack1.earliest_window[0] + 1)
    ack2 = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="maneuver",
                                         params={"dv": dv, "via": "GS-TRN"}))
    assert ack2.ok
    mgr.advance_to(ack2.earliest_window[0] + 1)

    rows = mgr.maneuver_ledger("blue", "ISR-EO-1")
    assert len(rows) == 2
    assert rows[0]["purpose_tag"] == "raise perigee"
    assert rows[1]["purpose_tag"] == ""
    assert rows[0]["remaining_delta_v_ms"] > rows[1]["remaining_delta_v_ms"]

    # Fog: Red cannot read Blue's ledger; White can read any.
    assert mgr.maneuver_ledger("red", "ISR-EO-1") is None
    assert mgr.maneuver_ledger("white", "ISR-EO-1") == rows


# ---- IP-1270 (FR-3430/FR-3440) — effect-authorization gating + live ROE via SessionManager -----

def _gated_manager():
    from spacesim.content.vignette import Vignette
    raw = {
        "id": "test-ip1270-gating", "title": "Gating test",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [
            {"id": "INT", "kind": "interceptor", "location": {"lat_deg": 0.0, "lon_deg": 0.0},
             "resources": {"ammo": 1}},
        ],
        "red_forces": [
            {"id": "RSAT", "kind": "satellite",
             "orbit": {"a_m": 6928137.0, "e": 0.0, "i_deg": 51.6, "raan_deg": 0.0, "argp_deg": 0.0, "ta_deg": 0.0}},
        ],
        "neutral_forces": [], "sensors": [],
        "roe": {"blue": {"kinetic_authorized": True}, "red": {"kinetic_authorized": True}},
        "effect_gating_rules": [{"action_type": "engage", "required_role": "white"}],
    }
    mgr = SessionManager(Vignette.model_validate(raw), seed=1)
    mgr.start()
    from spacesim.engine.custody import Track
    mgr.world.tracks.append(Track(object="RSAT", owner="blue", confidence=1.0,
                                  characterized=True, last_observation=mgr.world.now))
    return mgr


def test_session_decide_gated_order_role_gated():
    mgr = _gated_manager()
    ack = mgr.issue_order("blue", Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert ack.status == "pending_approval"
    ok, reason = mgr.decide_gated_order("blue", ack.id, True)
    assert not ok and reason == "not_controller"
    ok, reason = mgr.decide_gated_order("white", ack.id, True)
    assert ok, reason


def test_session_issue_roe_change_role_gated():
    mgr = _gated_manager()
    ok, reason = mgr.issue_roe_change("blue", "blue", "kinetic_authorized", False)
    assert not ok and reason == "not_controller"
    ok, reason = mgr.issue_roe_change("white", "blue", "kinetic_authorized", False)
    assert ok, reason


def test_pending_gated_order_discarded_on_rewind():
    """IP-1270 Design Decision 2 — a pending-approval order still awaiting a decision at rewind
    is discarded, with no persisted cross-session pending state."""
    mgr = _gated_manager()
    ack = mgr.issue_order("blue", Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert ack.status == "pending_approval"
    assert len(mgr.osys._pending) == 1
    mgr.rewind_to(mgr.sim.clock.now)
    assert len(mgr.osys._pending) == 0
