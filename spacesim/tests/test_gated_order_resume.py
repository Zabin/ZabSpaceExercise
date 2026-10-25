"""IP-1087 — a pending-approval order is still decidable after save and resume
(FR-3430, FR-7210, FR-7220, NFR-1600; review M-2).

``OrderSystem._pending`` is derived on resume from the restored order registry, the restored
event log and the content's gating rules; no new save key exists. Rewind still discards pending
orders (IP-1270 Decision 2).
"""

from __future__ import annotations

import copy
import json

import pytest
import yaml
from fastapi.testclient import TestClient

from spacesim.content.vignette import Vignette
from spacesim.engine.custody import Track
from spacesim.engine.orders import Order
from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import SessionManager
from spacesim.ui_web.server import create_app

RULE = {"action_type": "engage", "required_role": "white"}


def _raw(vid: str = "test-ip1087-gating", ammo: int = 2, rules=None) -> dict:
    return {
        "id": vid, "title": "Gated resume test",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [
            {"id": "INT", "kind": "interceptor", "location": {"lat_deg": 0.0, "lon_deg": 0.0},
             "resources": {"ammo": ammo}},
        ],
        "red_forces": [
            {"id": "RSAT", "kind": "satellite",
             "orbit": {"a_m": 6928137.0, "e": 0.0, "i_deg": 51.6, "raan_deg": 0.0, "argp_deg": 0.0, "ta_deg": 0.0}},
        ],
        "neutral_forces": [], "sensors": [],
        "roe": {"blue": {"kinetic_authorized": True}, "red": {"kinetic_authorized": True}},
        "effect_gating_rules": [RULE] if rules is None else rules,
    }


def _mgr(**kw) -> SessionManager:
    mgr = SessionManager(Vignette.model_validate(_raw(**kw)), seed=1)
    mgr.start()
    mgr.set_clock(False)
    mgr.world.tracks.append(Track(object="RSAT", owner="blue", confidence=1.0,
                                  characterized=True, last_observation=mgr.world.now))
    return mgr


def _engage(mgr: SessionManager) -> str:
    ack = mgr.issue_order("blue", Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert ack.status == "pending_approval", ack
    return ack.id


def _rt(state: dict) -> dict:
    return json.loads(json.dumps(state))


def _resume(mgr: SessionManager) -> SessionManager:
    return SessionManager.from_state(_rt(mgr.save_state()))


def _entries(mgr, kind):
    return [e for e in mgr.sim.eventlog.entries if e.kind == kind]


# ---- resume then decide -------------------------------------------------------------------

@pytest.mark.verifies("FR-3430", "FR-7220")
def test_approve_after_resume_queues_and_elapsed_spans_the_save():
    mgr = _mgr()
    oid = _engage(mgr)
    mgr.step(120)
    res = _resume(mgr)
    res.step(60)
    assert res.osys.orders[oid].status == "pending_approval"
    ok, reason = res.decide_gated_order("white", oid, True)
    assert ok, reason
    assert res.osys.orders[oid].status == "queued"
    dec = _entries(res, "effect_gate_decision")[-1]
    req = _entries(res, "effect_gate_request")[-1]
    assert dec.payload["elapsed_us"] == dec.sim_time - req.sim_time
    assert dec.payload["elapsed_us"] >= 180 * 1_000_000   # spans the save + post-load advance
    res.step(7200)   # executes in its window; no zombie
    assert res.osys.orders[oid].status != "pending_approval"


@pytest.mark.verifies("FR-3430")
def test_deny_after_resume_rejects_and_schedules_nothing():
    mgr = _mgr()
    oid = _engage(mgr)
    res = _resume(mgr)
    before = len(res.sim.scheduler.pending()) if hasattr(res.sim.scheduler, "pending") else None
    ok, _ = res.decide_gated_order("white", oid, False)
    assert ok
    o = res.osys.orders[oid]
    assert (o.status, o.fail_reason) == ("rejected", "gate_denied")
    if before is not None:
        assert len(res.sim.scheduler.pending()) == before


@pytest.mark.verifies("FR-3430")
def test_wrong_role_after_resume_is_not_controller_and_stays_pending():
    mgr = _mgr()
    oid = _engage(mgr)
    res = _resume(mgr)
    ok, reason = res.decide_gated_order("blue", oid, True)
    assert not ok and reason == "not_controller"
    assert res.osys.orders[oid].status == "pending_approval"
    ok, reason = res.decide_gated_order("white", oid, True)
    assert ok, reason


@pytest.mark.verifies("FR-3430")
def test_two_pending_one_decided_before_save():
    mgr = _mgr(ammo=2)
    first, second = _engage(mgr), _engage(mgr)
    ok, _ = mgr.decide_gated_order("white", first, True)
    assert ok
    res = _resume(mgr)
    assert res.osys.orders[first].status == "queued"
    assert res.decide_gated_order("white", first, True) == (False, "no_such_pending_order")
    assert res.decide_gated_order("white", second, True)[0]


@pytest.mark.verifies("FR-3430")
def test_decided_before_save_is_not_pending_after_load():
    mgr = _mgr()
    oid = _engage(mgr)
    assert mgr.decide_gated_order("white", oid, True)[0]
    res = _resume(mgr)
    assert res.osys._pending == {}
    assert res.osys.orders[oid].status == "queued"
    assert res.decide_gated_order("white", oid, False) == (False, "no_such_pending_order")
    assert res.load_warnings == []


@pytest.mark.verifies("FR-7220")
def test_save_load_save_load_still_decidable():
    mgr = _mgr()
    oid = _engage(mgr)
    res = _resume(_resume(mgr))
    assert res.osys.orders[oid].status == "pending_approval"
    assert res.decide_gated_order("white", oid, True)[0]


@pytest.mark.verifies("FR-3430", "FR-7230")
def test_legacy_format_save_pending_order_is_decidable(tmp_path, monkeypatch):
    ext = tmp_path / "ext"
    ext.mkdir()
    (ext / "gated.yaml").write_text(yaml.safe_dump({"vignette": _raw("legacy-gated")}), encoding="utf-8")
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(yaml.safe_dump({"content": {"external_vignette_dirs": [str(ext)]}}), encoding="utf-8")
    monkeypatch.setenv("SPACESIM_CONFIG", str(cfg))
    from spacesim.content.vignette import load_vignette
    mgr = SessionManager(load_vignette("legacy-gated"), seed=1)
    mgr.start()
    mgr.world.tracks.append(Track(object="RSAT", owner="blue", confidence=1.0,
                                  characterized=True, last_observation=mgr.world.now))
    oid = _engage(mgr)
    state = _rt(mgr.save_state())
    for k in ("save_format", "content", "baseline", "simulator_version"):
        state.pop(k, None)
    res = SessionManager.from_state(state)
    assert res.osys.orders[oid].status == "pending_approval"
    assert res.decide_gated_order("white", oid, True)[0]
    # test 10 — the gating rule removed from the file: warned + rejected, not a zombie
    (ext / "gated.yaml").write_text(yaml.safe_dump({"vignette": _raw("legacy-gated", rules=[])}),
                                    encoding="utf-8")
    res2 = SessionManager.from_state(copy.deepcopy(state))
    o = res2.osys.orders[oid]
    assert (o.status, o.fail_reason) == ("rejected", "gate_lost_on_resume")
    assert any(oid in w and "gate" in w for w in res2.load_warnings)
    assert res2.decide_gated_order("white", oid, True) == (False, "no_such_pending_order")


@pytest.mark.verifies("FR-7220", "FR-3430")
def test_restored_pending_order_equals_original_field_for_field():
    mgr = _mgr()
    oid = _engage(mgr)
    res = _resume(mgr)
    assert _rt(vars(res.osys.orders[oid])) == _rt(vars(mgr.osys.orders[oid]))


# ---- unreconstructable gates --------------------------------------------------------------

@pytest.mark.verifies("NFR-1600")
def test_pending_order_with_no_request_entry_is_rejected_with_warning():
    mgr = _mgr()
    oid = _engage(mgr)
    state = _rt(mgr.save_state())
    state["eventlog"]["entries"] = [e for e in state["eventlog"]["entries"]
                                    if e["kind"] != "effect_gate_request"]
    res = SessionManager.from_state(state)
    o = res.osys.orders[oid]
    assert (o.status, o.fail_reason) == ("rejected", "gate_lost_on_resume")
    assert any(oid in w for w in res.load_warnings)
    assert res.decide_gated_order("white", oid, True) == (False, "no_such_pending_order")


@pytest.mark.verifies("NFR-1600")
def test_pending_order_with_a_later_decision_entry_is_not_reopened():
    mgr = _mgr()
    oid = _engage(mgr)
    state = _rt(mgr.save_state())
    ents = state["eventlog"]["entries"]
    last = ents[-1]
    ents.append({**last, "seq": last["seq"] + 1, "kind": "effect_gate_decision", "actor": "white",
                 "payload": {"order_id": oid, "approved": True, "elapsed_us": 0}})
    res = SessionManager.from_state(state)
    o = res.osys.orders[oid]
    assert (o.status, o.fail_reason) == ("rejected", "gate_lost_on_resume")
    assert any(oid in w for w in res.load_warnings)
    assert res.osys._pending == {}


@pytest.mark.verifies("NFR-1600", "FR-3430")
def test_load_save_route_returns_warning_and_decide_route_works():
    c = TestClient(create_app(), raise_server_exceptions=False)
    mgr = _mgr()
    oid = _engage(mgr)
    good = _rt(mgr.save_state())
    r = c.post("/api/sessions/load_save?cell=white", json=good)
    assert r.status_code == 200, r.text
    sid = r.json()["session"]["sid"] if isinstance(r.json().get("session"), dict) else r.json()["session"]
    d = c.post(f"/api/sessions/{sid}/gate/decide",
               json={"cell": "white", "order_id": oid, "approve": True})
    assert d.status_code == 200 and d.json()["ok"] is True, d.text
    bad = copy.deepcopy(good)
    bad["eventlog"]["entries"] = [e for e in bad["eventlog"]["entries"]
                                  if e["kind"] != "effect_gate_request"]
    r = c.post("/api/sessions/load_save?cell=white", json=bad)
    assert r.status_code == 200, r.text
    assert any(oid in w for w in r.json()["warnings"])


# ---- unchanged behaviour ------------------------------------------------------------------

@pytest.mark.verifies("FR-3430")
def test_rewind_and_undo_after_resume_still_discard_pending():
    mgr = _mgr()
    _engage(mgr)
    res = _resume(mgr)
    assert len(res.osys._pending) == 1
    res.rewind_to(res.sim.clock.now)
    assert res.osys._pending == {}
    res2 = _resume(mgr)
    res2.undo_last()
    assert res2.osys._pending == {}


@pytest.mark.verifies("FR-7220")
def test_session_without_gating_rules_adds_no_warning_and_no_pending():
    mgr = _mgr(rules=[])
    ack = mgr.issue_order("blue", Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert ack.status != "pending_approval"
    res = _resume(mgr)
    assert res.osys._pending == {}
    assert res.load_warnings == []
    assert _rt([vars(o) for o in res.osys.orders.values()]) == _rt([vars(o) for o in mgr.osys.orders.values()])
    assert res.sim.eventlog.model_dump() == mgr.sim.eventlog.model_dump()


# ---- determinism --------------------------------------------------------------------------

@pytest.mark.verifies("FR-7220")
def test_replay_equals_live_after_resumed_decision_and_save_after_loads_same():
    mgr = _mgr()
    oid = _engage(mgr)
    res = _resume(mgr)
    assert res.decide_gated_order("white", oid, True)[0]
    res.step(300)
    assert res.sim.replay().model_dump_json() == res.world.model_dump_json()
    again = _resume(res)
    assert again.world.model_dump_json() == res.world.model_dump_json()
    assert again.osys._pending == {}
