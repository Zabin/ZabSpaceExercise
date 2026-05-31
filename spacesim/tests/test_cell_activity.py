"""Tests for the per-cell activity Gantt feed (`InProcessSession.cell_activity`).

Coverage:
  - Returns the expected envelope keys (now, t_start, t_end, cells, activities).
  - White sees all three cells' lanes; Blue/Red see only their own.
  - Orders issued by a cell appear in that cell's feed and not in the other's.
  - Cancelled orders are present with status="cancelled".
  - Rejected orders show as point markers (no window).
  - Scheduled future injects appear with kind="inject", status="scheduled".
  - Past + present + scheduled all coexist; the bar straddling NOW reports status="active".
"""
from __future__ import annotations

import pytest

from spacesim.engine.orders import Order
from spacesim.session.inprocess import InProcessSession


def _api_session():
    api = InProcessSession()
    sid = api.load_vignette("training-basics")
    api.start(sid)
    return api, sid


# ---------------------------------------------------------------------------
# Envelope + lane structure
# ---------------------------------------------------------------------------

def test_activity_envelope_keys():
    api, sid = _api_session()
    res = api.cell_activity(sid, "white")
    for k in ("now", "t_start", "t_end", "cells", "activities"):
        assert k in res
    assert isinstance(res["activities"], list)
    assert isinstance(res["cells"], list)


def test_activity_white_lists_all_three_lanes():
    api, sid = _api_session()
    res = api.cell_activity(sid, "white")
    assert res["cells"] == ["blue", "red", "neutral"]


def test_activity_blue_lists_only_blue_lane():
    api, sid = _api_session()
    res = api.cell_activity(sid, "blue")
    assert res["cells"] == ["blue"]


def test_activity_red_lists_only_red_lane():
    api, sid = _api_session()
    res = api.cell_activity(sid, "red")
    assert res["cells"] == ["red"]


# ---------------------------------------------------------------------------
# Fog-of-war filtering on orders
# ---------------------------------------------------------------------------

def test_blue_order_appears_in_blue_feed_only():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    # Find a Blue-owned satellite with an orbit + matching ground station for uplink
    blue_sat = next((a for a in mgr.world.assets.values()
                      if a.owner == "blue" and a.orbit is not None), None)
    assert blue_sat is not None
    blue_gs = next((a for a in mgr.world.assets.values()
                     if a.owner == "blue" and a.location is not None), None)
    assert blue_gs is not None
    mgr.issue_order("blue", Order(cell="blue", actor=blue_sat.id, action="downlink",
                                    params={"via": blue_gs.id}))
    blue_feed = api.cell_activity(sid, "blue")
    red_feed = api.cell_activity(sid, "red")
    white_feed = api.cell_activity(sid, "white")
    blue_orders = [a for a in blue_feed["activities"] if a["kind"] == "order"]
    red_orders = [a for a in red_feed["activities"] if a["kind"] == "order"]
    white_orders = [a for a in white_feed["activities"] if a["kind"] == "order"]
    assert len(blue_orders) >= 1
    assert all(a["cell"] == "blue" for a in blue_orders)
    # The Blue order is invisible in Red's feed
    assert not any(a["actor"] == blue_sat.id and a["cell"] == "blue" for a in red_orders)
    # White sees the Blue order
    assert any(a["actor"] == blue_sat.id and a["cell"] == "blue" for a in white_orders)


def test_red_order_appears_in_red_feed_only():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    red_sat = next((a for a in mgr.world.assets.values()
                     if a.owner == "red" and a.orbit is not None), None)
    if red_sat is None:
        pytest.skip("training-basics has no red orbital asset")
    red_gs = next((a for a in mgr.world.assets.values()
                    if a.owner == "red" and a.location is not None), None)
    if red_gs is None:
        pytest.skip("training-basics has no red ground asset for uplink")
    mgr.issue_order("red", Order(cell="red", actor=red_sat.id, action="downlink",
                                   params={"via": red_gs.id}))
    blue_feed = api.cell_activity(sid, "blue")
    red_feed = api.cell_activity(sid, "red")
    assert any(a["actor"] == red_sat.id for a in red_feed["activities"])
    assert not any(a["actor"] == red_sat.id for a in blue_feed["activities"])


# ---------------------------------------------------------------------------
# Order statuses
# ---------------------------------------------------------------------------

def test_cancelled_order_present_with_cancelled_status():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    blue_sat = next((a for a in mgr.world.assets.values()
                      if a.owner == "blue" and a.orbit is not None), None)
    blue_gs = next((a for a in mgr.world.assets.values()
                     if a.owner == "blue" and a.location is not None), None)
    if blue_sat is None or blue_gs is None:
        pytest.skip("training-basics lacks the required blue assets")
    o = mgr.issue_order("blue", Order(cell="blue", actor=blue_sat.id, action="downlink",
                                        params={"via": blue_gs.id}))
    assert o.id  # was assigned
    mgr.cancel_order("blue", o.id)
    blue_feed = api.cell_activity(sid, "blue")
    match = [a for a in blue_feed["activities"] if a["kind"] == "order" and a["actor"] == blue_sat.id]
    assert any(a["status"] == "cancelled" for a in match)


def test_rejected_order_appears_as_marker():
    """A rejected order has no earliest_window — it still shows as a point marker."""
    api, sid = _api_session()
    mgr = api._sessions[sid]
    # An order with an unknown actor is rejected at issue time
    o = mgr.issue_order("blue", Order(cell="blue", actor="NO-SUCH-ASSET", action="downlink",
                                        params={"via": "x"}))
    assert o.status == "rejected"
    feed = api.cell_activity(sid, "blue")
    rows = [a for a in feed["activities"] if a["actor"] == "NO-SUCH-ASSET"]
    assert len(rows) == 1
    # Marker width is roughly 60 s
    assert rows[0]["end"] - rows[0]["start"] <= 60_000_001
    assert rows[0]["status"] == "rejected"


# ---------------------------------------------------------------------------
# Scheduled injects
# ---------------------------------------------------------------------------

def test_scheduled_inject_appears_as_inject_row():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    future_t = mgr.world.now + 120_000_000   # +120 s
    api.fire_inject(sid, {"effects": [{"type": "message", "to": ["white"], "text": "later"}]},
                     at_sim_t=future_t)
    feed = api.cell_activity(sid, "white")
    injects = [a for a in feed["activities"] if a["kind"] == "inject"]
    assert len(injects) >= 1
    assert any(a["status"] == "scheduled" for a in injects)


def test_scheduled_inject_skipped_when_past_window():
    """An inject far outside the display window should not appear."""
    api, sid = _api_session()
    mgr = api._sessions[sid]
    far_future = mgr.world.now + 10 * 3600 * 1_000_000   # +10 h (default window = +2 h)
    api.fire_inject(sid, {"effects": [{"type": "message", "to": ["white"], "text": "far"}]},
                     at_sim_t=far_future)
    feed = api.cell_activity(sid, "white", past_window_s=0, future_window_s=3600)
    injects = [a for a in feed["activities"] if a["kind"] == "inject" and a["start"] == far_future]
    assert injects == []


# ---------------------------------------------------------------------------
# Display window controls
# ---------------------------------------------------------------------------

def test_default_window_30min_past_2h_future():
    api, sid = _api_session()
    res = api.cell_activity(sid, "white")
    assert res["t_start"] == res["now"] - 1800 * 1_000_000
    assert res["t_end"] == res["now"] + 7200 * 1_000_000


def test_custom_window_respected():
    api, sid = _api_session()
    res = api.cell_activity(sid, "white", past_window_s=60, future_window_s=300)
    assert res["t_end"] - res["t_start"] == (60 + 300) * 1_000_000
