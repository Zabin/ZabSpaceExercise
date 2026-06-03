"""Command queue: listing, replay-safe cancellation, pass-timeline windows, inject list."""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.orders import MAX_COMMANDS_PER_PASS, Order
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


def test_cancel_observe_frees_sensor_for_rebooking():
    """Cancelling an observe order must release the sensor booking so the same slot can be reused."""
    mgr = _mgr()
    # RADAR-TRN is the Blue ground sensor in training-basics.
    ack1 = mgr.issue_order("blue", Order(cell="blue", actor="RADAR-TRN", action="observe",
                                         target="RED-TGT", params={}))
    assert ack1.status == "queued", ack1.reason
    first_oid = ack1.id
    first_window = mgr.osys.orders[first_oid].earliest_window
    assert first_window is not None

    # The booking must be present before cancel.
    assert any(first_window in bk for bk in mgr.osys._sensor_bookings.values())

    # Cancel — booking must be removed.
    assert mgr.cancel_order("blue", first_oid) is True
    for bk_list in mgr.osys._sensor_bookings.values():
        assert first_window not in bk_list

    # After cancel, re-issuing the same observe must succeed (not be contended).
    ack2 = mgr.issue_order("blue", Order(cell="blue", actor="RADAR-TRN", action="observe",
                                         target="RED-TGT", params={}))
    assert ack2.status == "queued", f"sensor still contended after cancel: {ack2.reason}"
    assert ack2.earliest_window == first_window   # wins the same slot

    # list_orders exposes issued_at field.
    rows = mgr.list_orders("blue")
    assert all("issued_at" in r for r in rows)


def test_pass_capacity_limits_commands_per_window():
    """At most MAX_COMMANDS_PER_PASS commands can be queued for the same access window."""
    mgr = _mgr()
    # Queue MAX commands — all should be accepted into the same earliest window.
    accepted = []
    for _ in range(MAX_COMMANDS_PER_PASS):
        ack = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="command",
                                            params={"via": "GS-TRN", "verb": "cdh.dump_storage"}))
        assert ack.status == "queued", f"expected queued, got {ack.reason}"
        accepted.append(ack)
    # Verify they all share the same window (same pass slot).
    wins = [mgr.osys.orders[a.id].earliest_window for a in accepted]
    assert all(w == wins[0] for w in wins), "all queued commands should target the same pass"

    # One more — must either be rejected (pass_capacity_full) or pushed to the NEXT window.
    overflow = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="command",
                                             params={"via": "GS-TRN", "verb": "cdh.dump_storage"}))
    if overflow.status == "rejected":
        assert overflow.reason == "pass_capacity_full"
    else:
        # Accepted into a later window — must not share the first window.
        assert mgr.osys.orders[overflow.id].earliest_window != wins[0]

    # After cancelling one accepted order, the slot opens and the overflow window resets.
    mgr.cancel_order("blue", accepted[0].id)
    key = (mgr.osys.orders[accepted[0].id].cell, wins[0][0])  # won't be in _order_pass anymore
    # Pass booking decremented: capacity below MAX again.
    assert mgr.osys._pass_bookings.get(("ISR-EO-1", wins[0][0]), 0) == MAX_COMMANDS_PER_PASS - 1


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
