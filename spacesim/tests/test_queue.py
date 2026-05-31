"""Command queue: listing, replay-safe cancellation, pass-timeline windows, inject list."""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.orders import Order
from spacesim.session.manager import SessionManager


def _mgr():
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    return mgr


def test_queue_lists_issued_orders():
    mgr = _mgr()
    mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"}))
    q = mgr.list_orders("blue")
    row = next(o for o in q if o["actor"] == "ISR-EO-1" and o["action"] == "downlink")
    assert row["status"] == "queued" and row["window"] is not None and row["delivery_path"] == "ground_uplink"
    # Fog: Red doesn't see Blue's queue.
    assert all(o["cell"] == "red" for o in mgr.list_orders("red"))


def test_cancel_prevents_execution_and_is_replay_safe():
    mgr = _mgr()
    ack = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"}))
    oid = mgr.list_orders("blue")[0]["id"]
    win = mgr.osys.orders[oid].earliest_window

    assert mgr.cancel_order("blue", oid) is True
    assert mgr.osys.orders[oid].status == "cancelled"
    assert mgr.cancel_order("blue", oid) is False        # can't cancel twice

    mgr.advance_to(win[1] + 1)
    assert mgr.world.mission.get("imagery_delivered") is None   # the cancelled downlink never ran
    assert not mgr.world.effect_log                              # nothing executed
    # The cancelled event was never logged, so replay reproduces the (empty) outcome exactly.
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_windows_ahead_returns_upcoming_passes_by_channel():
    mgr = _mgr()
    wa = mgr.windows_ahead("blue", "ISR-EO-1")
    assert wa is not None and wa["windows"]
    chans = {w["channel"] for w in wa["windows"]}
    assert "command_uplink" in chans or "telemetry_downlink" in chans
    assert all(w["start"] >= wa["now"] for w in wa["windows"])
    assert mgr.windows_ahead("red", "ISR-EO-1") is None          # fog


def test_next_contacts_matches_pass_timeline_and_respects_fog():
    mgr = _mgr()
    nc = mgr.next_contacts("blue")
    assert "ISR-EO-1" in nc["next"]
    # The fleet-rail countdown value is exactly the first window in the asset's pass timeline.
    wa = mgr.windows_ahead("blue", "ISR-EO-1")
    assert nc["next"]["ISR-EO-1"] == wa["windows"][0]["start"]
    assert nc["next"]["ISR-EO-1"] >= nc["now"]
    # Fog: Red's fleet rail never lists a Blue satellite.
    assert "ISR-EO-1" not in mgr.next_contacts("red")["next"]


def test_inject_list_exposes_vignette_injects():
    mgr = SessionManager(load_vignette("multi-domain-taiwan"), seed=1)
    mgr.start()
    ids = {i["id"] for i in mgr.list_injects()}
    assert "patch_modem" in ids and "commercial_imagery_leak" in ids
