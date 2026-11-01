"""IP-1088 (FR-6210, FR-6220) — the per-cell activity feed is filtered at the session boundary.

Fog matrix: every entry kind the feed can carry x White / Blue / Red / Observer (both
designations); unknown cells refused; White's feed unchanged; replay equals live; the event log,
scheduler and RNG are untouched by reads.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from spacesim.engine.effects import ActiveEffect
from spacesim.engine.orders import Order
from spacesim.session.cells import CellController
from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import BUS_TICK_PERIOD_S, SessionManager
from spacesim.content.vignette import Vignette
from spacesim.ui_web.server import create_app

US = 1_000_000
MIN = 60 * US
SENTINEL = "SENTINEL-WHITE-SCRIPT-77"
CELLS = ("white", "blue", "red")


def _session(vid="leo-isr-denial"):
    api = InProcessSession()
    sid = api.load_vignette(vid, seed=1)
    api.start(sid)
    api._sessions[sid].set_clock(False)
    return api, sid


def _rows(api, sid, cell, kind=None):
    rows = api.cell_activity(sid, cell)["activities"]
    return [r for r in rows if kind is None or r["kind"] == kind]


def _inject(api, sid, minutes=45, text=SENTINEL, to=("blue",)):
    mgr = api._sessions[sid]
    ack = api.fire_inject(sid, {"effects": [{"type": "message", "to": list(to), "text": text}]},
                          at_sim_t=mgr.world.now + minutes * MIN)
    assert ack.ok, ack.reason
    return mgr.world.now + minutes * MIN


def _snapshot(mgr):
    return (json.dumps([e.model_dump() for e in mgr.sim.eventlog.entries], sort_keys=True, default=str),
            repr(mgr.sim.scheduler.pending()), repr(mgr.sim.rng.export_state()))


def _eff(mgr, target, start_off=-60, end_off=600, attribution="covert", template="cyber-secret-payload",
         category="cyber"):
    now = mgr.world.now
    mgr.world.active_effects.append(ActiveEffect(
        target=target, outcome="degrade", start=now + start_off * US, end=now + end_off * US,
        attribution=attribution, category=category, template=template))


# ---- the reported leak (HTTP repro) -------------------------------------------------------
@pytest.mark.verifies("FR-6220", "FR-4450", "FR-6210")
def test_reported_leak_repro_over_http_and_regression_after_firing():
    api, sid = _session()
    c = TestClient(create_app(api))
    mgr = api._sessions[sid]
    t = mgr.world.now + 50 * MIN
    r = c.post(f"/api/sessions/{sid}/inject?cell=white",
               json={"inject": {"effects": [{"type": "message", "to": ["blue"], "text": SENTINEL}]},
                     "at_sim_t": t})
    assert r.status_code == 200
    white = c.get(f"/api/sessions/{sid}/activity/white").json()
    assert [a["start"] for a in white["activities"] if a["start"] == t and a["kind"] == "inject"] == [t]
    for cell in ("blue", "red"):
        body = c.get(f"/api/sessions/{sid}/activity/{cell}")
        assert body.status_code == 200
        assert body.json()["activities"] == []
        assert "inject" not in body.text and str(t) not in body.text and SENTINEL not in body.text
    obs = c.get(f"/api/sessions/{sid}/activity/observer")   # default designation: godview == White
    assert obs.status_code == 200 and obs.json()["activities"] == white["activities"]
    for bad in ("neutral", "bogus"):
        assert c.get(f"/api/sessions/{sid}/activity/{bad}").status_code == 400
    # advance past firing: message reaches Blue's CellView; the feed still has no inject row
    api.advance_to(sid, t + MIN)
    assert any(SENTINEL in m["text"] for m in api.get_view(sid, "blue").messages)
    assert _rows(api, sid, "blue", "inject") == [] and _rows(api, sid, "red", "inject") == []


# ---- rows 1, 2: orders ---------------------------------------------------------------------
@pytest.mark.verifies("FR-6210", "FR-6220")
def test_rows_1_2_orders_own_cell_only_in_every_state():
    api, sid = _session()
    mgr = api._sessions[sid]
    mk = {"blue": lambda: Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"}),
          "red": lambda: Order(cell="red", actor="JAM-NORTH", action="jam", target="ISR-EO-1")}
    for c in ("blue", "red"):
        mgr.issue_order(c, mk[c]())
        o2 = mk[c]()
        mgr.issue_order(c, o2)
        mgr.cancel_order(c, o2.id)
        mgr.issue_order(c, Order(cell=c, actor="NO-SUCH-ASSET", action="downlink", params={}))
    white = _rows(api, sid, "white", "order")
    assert {r["cell"] for r in white} == {"blue", "red"}
    statuses = {r["status"] for r in white}
    assert "rejected" in statuses
    for c in ("blue", "red"):
        own = _rows(api, sid, c, "order")
        assert own == [r for r in white if r["cell"] == c] and own
        assert all(r["cell"] == c for r in own)


# ---- rows 3-6: injects -----------------------------------------------------------------------
@pytest.mark.verifies("FR-6210", "FR-6220", "FR-4450")
def test_rows_3_5_6_scheduled_inject_white_only_through_rewind_undo_edit_cancel():
    api, sid = _session()
    mgr = api._sessions[sid]
    t0 = mgr.world.now
    t = _inject(api, sid, 50)

    def check(white_n, start=None):
        w = [r for r in _rows(api, sid, "white", "inject") if r["start"] in (t, t + 5 * MIN)]
        assert len(w) == white_n
        if start is not None:
            assert [r["start"] for r in w] == [start]
        for c in ("blue", "red"):
            assert _rows(api, sid, c) == []
        for des in ("white", "blue", "red"):
            api.set_observer_view(sid, "white", des)
            assert _rows(api, sid, "observer") == _rows(api, sid, des)
        api.set_observer_view(sid, "white", "godview")

    check(1, t)
    api.advance_to(sid, t0 + 10 * MIN)
    api.rewind_to(sid, t0 + 5 * MIN)
    check(1, t)                    # IP-1083 schedule entry: re-armed, one row (not zero, not two)
    api.advance_to(sid, t0 + 10 * MIN)
    api.undo_last(sid, 1)
    check(1, t)
    api.rewind_to(sid, t0)
    check(1, t)
    handle = next(p["handle"] for p in api.pending_injects(sid) if p["handle"].startswith("white-"))
    t2 = t + 5 * MIN
    assert api.edit_inject(sid, handle, at_sim_t=t2).ok
    check(1, t2)                   # row 6: edited time
    assert api.cancel_inject(sid, handle).ok
    check(0)                       # then gone


@pytest.mark.verifies("FR-6210", "FR-6220")
def test_row_4_vignette_declared_scheduled_inject_white_only():
    for vid in ("leo-isr-denial", "training-basics"):
        api, sid = _session(vid)
        w = _rows(api, sid, "white", "inject")
        for c in ("blue", "red"):
            assert _rows(api, sid, c, "inject") == []
        assert all(r["cell"] == "white" for r in w)


@pytest.mark.verifies("FR-6210", "FR-6220", "FR-4420")
def test_row_7_condition_inject_and_condition_check_ticks_never_rows():
    vig = Vignette.model_validate({
        "id": "t-cond", "title": "t", "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [{"id": "SAT-BLUE", "kind": "satellite"}],
        "red_forces": [{"id": "SAT-RED", "kind": "satellite"}], "neutral_forces": [], "sensors": [],
        "injects": [
            {"id": "reveal", "trigger": {"type": "time", "at_sim_s": 0},
             "effects": [{"type": "reveal_asset", "to": "blue", "target": "SAT-RED"}]},
            {"id": "cond", "trigger": {"type": "condition",
                                       "metric": {"kind": "custody", "side": "blue", "object": "SAT-RED",
                                                  "min_conf": 0.5}},
             "effects": [{"type": "message", "to": ["blue"], "text": "condition-fired"}]}]})
    mgr = SessionManager(vig, seed=0)
    api = InProcessSession()
    api._sessions["s-cond"] = mgr
    mgr.start()
    mgr.set_clock(False)
    for step in range(3):
        for c in CELLS:
            assert [r for r in _rows(api, "s-cond", c) if r["kind"] == "inject"
                    and "condition" in r["label"]] == []
        for c in ("blue", "red"):
            assert _rows(api, "s-cond", c, "inject") == []
        mgr.advance_to(mgr.sim.clock.now + int(BUS_TICK_PERIOD_S * US))
    assert any(e.kind == "condition_check" for e in mgr.sim.eventlog.entries)
    assert not any(r["label"].startswith("condition_check") for r in _rows(api, "s-cond", "white"))


# ---- rows 8-11: effects -----------------------------------------------------------------------
@pytest.mark.verifies("FR-6210", "FR-6220")
def test_rows_8_to_11_effects_symptom_only_for_owner_template_for_white():
    api, sid = _session()
    mgr = api._sessions[sid]
    blue_t = next(a.id for a in mgr.world.assets.values() if a.owner == "blue" and a.orbit is not None)
    red_t = "RED-SURF"
    _eff(mgr, blue_t, attribution="covert", template="cyber-secret-payload", category="cyber")
    _eff(mgr, blue_t, attribution="overt", template="jam-spot-overt", category="electronic_warfare")
    _eff(mgr, red_t, template="red-side-template", category="cyber")
    _eff(mgr, blue_t, start_off=300, end_off=900, template="future-template", category="cyber")  # row 11
    white = _rows(api, sid, "white", "effect")
    assert len(white) == 4 and any("cyber-secret-payload" in r["label"] for r in white)
    blue = _rows(api, sid, "blue", "effect")
    assert len(blue) == 2                                           # future-start effect withheld
    body = json.dumps(blue)
    for leak in ("cyber-secret-payload", "jam-spot-overt", "future-template", "red-side-template", red_t):
        assert leak not in body
    labels = sorted(r["label"] for r in blue)
    assert sum("(attributed)" in x for x in labels) == 1
    assert all(r["target"] == blue_t and r["cell"] == "blue" for r in blue)
    red = _rows(api, sid, "red", "effect")
    assert len(red) == 1 and "red-side-template" not in json.dumps(red) and red[0]["target"] == red_t
    assert all(r["cell"] != "white" for r in blue + red)
    for des, expect in (("white", white), ("blue", blue), ("red", red)):
        api.set_observer_view(sid, "white", des)
        assert _rows(api, sid, "observer", "effect") == expect


@pytest.mark.verifies("FR-6210", "FR-6220")
def test_row_10_neutral_owned_effect_white_only():
    api, sid = _session("training-basics")
    mgr = api._sessions[sid]
    neutral = [a.id for a in mgr.world.assets.values() if a.owner == "neutral"]
    if not neutral:
        pytest.skip("no neutral asset in vignette")
    _eff(mgr, neutral[0], template="neutral-template")
    assert any(r["cell"] == "neutral" for r in _rows(api, sid, "white", "effect"))
    for c in ("blue", "red"):
        assert "neutral-template" not in json.dumps(_rows(api, sid, c))
        assert all(r["cell"] != "neutral" for r in _rows(api, sid, c))


# ---- row 12: other logged entries are never rows -------------------------------------------------
@pytest.mark.verifies("FR-6210", "FR-6220")
def test_row_12_admin_gate_role_save_load_entries_are_not_rows():
    api, sid = _session()
    mgr = api._sessions[sid]
    before = {c: _rows(api, sid, c) for c in CELLS}
    api.assign_role(sid, "white", "seat-x", mgr.world.assets and next(iter(mgr.world.assets)), "operator")
    state = api.save(sid)
    sid2 = api.load_save(state)
    api._sessions[sid2].set_clock(False)
    after = {c: _rows(api, sid, c) for c in CELLS}
    assert after == before
    for c in CELLS:
        assert _rows(api, sid2, c) == before[c]
        assert {r["kind"] for r in _rows(api, sid2, c)} <= {"order", "inject", "effect"}


# ---- special cells, golden, purity ----------------------------------------------------------------
@pytest.mark.verifies("FR-6510", "FR-6210")
@pytest.mark.parametrize("bad", ["neutral", "bogus", "", "White", "godview"])
def test_unrecognized_cells_refused(bad):
    api, sid = _session()
    with pytest.raises(ValueError):
        api.cell_activity(sid, bad)


@pytest.mark.verifies("FR-6210")
def test_white_feed_golden_unchanged_shape():
    api, sid = _session()
    mgr = api._sessions[sid]
    t = _inject(api, sid, 30)
    tgt = "ISR-EO-1"
    _eff(mgr, tgt, template="tpl", category="cyber")
    w = api.cell_activity(sid, "white")
    assert w["cells"] == ["blue", "red", "neutral"]
    inj = [r for r in w["activities"] if r["kind"] == "inject" and r["start"] == t]
    assert inj == [{"kind": "inject", "cell": "white", "actor": "white-cell", "action": "inject",
                    "target": None, "start": t, "end": t + MIN, "status": "scheduled",
                    "label": "inject (1 effects)", "delivery_path": None}]
    eff = [r for r in w["activities"] if r["kind"] == "effect"][0]
    assert eff["label"] == f"tpl → {tgt} (degrade)" and eff["action"] == "cyber"
    assert set(eff) == {"kind", "cell", "actor", "action", "target", "start", "end", "status",
                        "label", "delivery_path"}


@pytest.mark.verifies("FR-1120", "FR-6220")
def test_reads_do_not_touch_log_scheduler_rng_and_replay_equals_live():
    api, sid = _session()
    mgr = api._sessions[sid]
    t0 = mgr.world.now
    _inject(api, sid, 50)
    live = {}   # (orders live in the OrderSystem, not the log: a rewind discards them - pre-existing)
    for i, off in enumerate((2, 6, 12)):
        api.advance_to(sid, t0 + off * MIN)
        snap = _snapshot(mgr)
        live[off] = {c: api.cell_activity(sid, c) for c in CELLS}
        assert _snapshot(mgr) == snap
    api.rewind_to(sid, t0 + 2 * MIN)
    for off in (2, 6, 12):
        api.advance_to(sid, t0 + off * MIN)
        assert {c: api.cell_activity(sid, c) for c in CELLS} == live[off]
    # save/load
    sid2 = api.load_save(api.save(sid))
    api._sessions[sid2].set_clock(False)
    assert {c: api.cell_activity(sid2, c) for c in CELLS} == live[12]


# ---- fail-closed unit ------------------------------------------------------------------------------
@pytest.mark.verifies("IP-1088", "FR-6210")
def test_filter_is_fail_closed_on_unknown_kind():
    row = {"kind": "invented", "cell": "blue", "actor": "x", "action": "a", "target": None,
           "start": 0, "end": 1, "status": "x", "label": "l", "delivery_path": None}
    tagged = {"row": row, "owner": "blue"}
    now = 10
    assert CellController.activity_rows([tagged], "blue", now) == []
    assert CellController.activity_rows([tagged], "red", now) == []
    assert CellController.activity_rows([tagged], "white", now) == [row]
