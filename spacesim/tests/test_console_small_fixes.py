"""IP-1065 — White Cell console and session small fixes.

- BL-0266: the activity timeline reports a queued order whose bar has ended as ``executed``,
  matching ``SessionManager.list_orders()`` (before, ``Order.status`` was passed through and a
  past order drew as a dashed queued bar for ever).
- BL-0141: a bulk-import file with two objects resolving to one asset id keeps the first and
  refuses the second (before, the second silently overwrote the first and both reported ok).
- BL-0196 / BL-0267 / BL-0145: console changes the headless suite cannot drive, checked by the
  repository's static-asset assertion pattern (the browser GUI is unverified headless).
"""
from __future__ import annotations

from pathlib import Path

from spacesim.engine.orders import Order
from spacesim.session.inprocess import InProcessSession

STATIC = Path(__file__).resolve().parents[1] / "ui_web" / "static"
_TLE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
_TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"
_TLE2_B = "2 25544  97.6416 100.4627 0006703 130.5360 325.0288 15.09560570999999"


def _downlink_session():
    api = InProcessSession()
    sid = api.load_vignette("training-basics")
    api.start(sid)
    mgr = api._sessions[sid]
    mgr.set_clock(False)
    sat = next(a for a in mgr.world.assets.values() if a.owner == "blue" and a.orbit is not None)
    gs = next(a for a in mgr.world.assets.values() if a.owner == "blue" and a.location is not None)
    ack = mgr.issue_order("blue", Order(cell="blue", actor=sat.id, action="downlink",
                                        params={"via": gs.id}))
    assert ack.ok and ack.status == "queued", ack.reason
    return api, sid, mgr, ack, sat.id


def _bar(api, sid, actor):
    feed = api.cell_activity(sid, "blue", past_window_s=6 * 3600, future_window_s=6 * 3600)
    return [a for a in feed["activities"] if a["kind"] == "order" and a["actor"] == actor]


def test_activity_reports_executed_once_the_bar_has_ended():
    api, sid, mgr, ack, actor = _downlink_session()
    (before,) = _bar(api, sid, actor)
    assert before["status"] == "queued"
    mgr.advance_to(before["end"] + 1_000_000)
    (after,) = _bar(api, sid, actor)
    assert after["status"] == "executed"
    # Same rule as the order queue's display label.
    (row,) = [o for o in mgr.list_orders("blue") if o["id"] == ack.id]
    assert row["status"] == "executed"


def test_activity_reports_active_while_the_bar_straddles_now():
    api, sid, mgr, ack, actor = _downlink_session()
    (before,) = _bar(api, sid, actor)
    mgr.advance_to(before["start"] + 1_000_000)
    (during,) = _bar(api, sid, actor)
    assert during["status"] == "active"


def test_bulk_import_duplicate_asset_id_in_one_file_keeps_the_first():
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    mgr = api._sessions[sid]
    text = "\n".join(["FIRST", _TLE1, _TLE2, "SECOND", _TLE1, _TLE2_B])
    reports = mgr.bulk_import("tle", text, {"FIRST": {"asset_id": "DUP-1", "owner": "blue"},
                                            "SECOND": {"asset_id": "DUP-1", "owner": "blue"}})
    assert [r["ok"] for r in reports] == [True, False]
    assert "FIRST" in reports[1]["reason"] and "DUP-1" in reports[1]["reason"]
    assert mgr.world.assets["DUP-1"].orbit.tle_line2 == _TLE2  # the first object's orbit kept


def test_fire_inject_reports_a_rejection():
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    start = js.index("async function fireInject")
    body = js[start:js.index("\n}\n", start)]
    assert "catch" in body and "inject-result" in body


def test_vignette_picker_groups_by_origin():
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    start = js.index("async function loadVignettes")
    body = js[start:js.index("\n}\n", start)]
    assert "origin" in body and "optgroup" in body


def test_save_as_scenario_console_control_is_white_only():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    i = html.index('id="save-scenario-btn"')
    tag = html[html.rindex("<", 0, i):html.index(">", i)]
    assert "white-only" in tag
    assert "as_scenario: true" in js
