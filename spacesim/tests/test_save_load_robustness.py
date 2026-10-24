"""IP-1102 — Save load robustness (FS-110 v2.0; FR-7220, FR-7230, NFR-1600).

Every unusable save is a 400 with a reason naming the problem (never a 500), a refused load leaves
no trace, and a save's content portion is the force the session actually had at save time.
"""

from __future__ import annotations

import copy
import json

import pytest
from fastapi.testclient import TestClient

from spacesim.content.vignette import Vignette, load_vignette
from spacesim.session.manager import SessionManager
from spacesim.ui_web.server import create_app


TLE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"
BASE = "leo-isr-denial"
LOAD = "/api/sessions/load_save?cell=white"


def _rt(state: dict) -> dict:
    return json.loads(json.dumps(state))


def _client() -> TestClient:
    return TestClient(create_app(), raise_server_exceptions=False)


def _good_state(started: bool = True) -> dict:
    mgr = SessionManager(load_vignette(BASE), seed=4)
    if started:
        mgr.start()
        mgr.set_clock(False)
        mgr.step(300)
    return _rt(mgr.save_state())


def _legacy(state: dict) -> dict:
    s = copy.deepcopy(state)
    for k in ("save_format", "content", "baseline", "simulator_version"):
        s.pop(k, None)
    return s


def _sessions(c: TestClient) -> list:
    return [s["sid"] for s in c.get("/api/sessions").json()]


def _refused(c: TestClient, state: dict, needle: str) -> None:
    before = _sessions(c)
    r = c.post(LOAD, json=state)
    assert r.status_code == 400, r.text
    assert needle in r.json()["detail"], r.json()
    assert _sessions(c) == before   # test 5: a refused load registers nothing


def _bad_cases() -> list[tuple[str, dict, str]]:
    good = _good_state()
    out: list[tuple[str, dict, str]] = []
    gone = _legacy(good)
    gone["vignette_id"] = "no-such-vignette-file"
    out.append(("legacy-missing-file", gone, "no-such-vignette-file"))
    for k in ("seed", "eventlog", "final_time"):
        s = copy.deepcopy(good)
        del s[k]
        out.append((f"self-missing-{k}", s, k))
    for k in ("vignette_id", "seed", "eventlog", "final_time"):
        s = _legacy(good)
        del s[k]
        out.append((f"legacy-missing-{k}", s, k))
    s = copy.deepcopy(good); s["pending"] = "nope"
    out.append(("pending-not-list", s, "pending"))
    s = copy.deepcopy(good); s["orders"] = ["not-a-mapping"]
    out.append(("orders-entry-not-mapping", s, "orders"))
    s = copy.deepcopy(good); s["orders"] = [{"cell": "blue"}]
    out.append(("orders-entry-missing-fields", s, "orders"))
    s = copy.deepcopy(good); s["ssn_requests"] = [{"id": "ssn-1"}]
    out.append(("ssn-entry-missing-fields", s, "ssn_requests"))
    s = copy.deepcopy(good); s["eventlog"] = "nope"
    out.append(("eventlog-not-mapping", s, "eventlog"))
    s = copy.deepcopy(good); s["seed"] = "x"
    out.append(("seed-not-int", s, "seed"))
    return out


CASES = _bad_cases()


@pytest.mark.verifies("FR-7230", "NFR-1600")
@pytest.mark.parametrize("name,state,needle", CASES, ids=[c[0] for c in CASES])
def test_bad_save_is_400_naming_the_problem_and_leaves_no_trace(name, state, needle):
    _refused(_client(), state, needle)


@pytest.mark.verifies("NFR-1600")
def test_refused_loads_do_not_consume_a_session_id():
    c = _client()
    for _, state, needle in CASES[:4]:
        _refused(c, state, needle)
    r = c.post(LOAD, json=_good_state())
    assert r.status_code == 200, r.text
    assert r.json()["session"] == "sess-1"


@pytest.mark.verifies("FR-7210", "FR-7230")
def test_valid_saves_still_load_with_same_warnings():
    c = _client()
    good = _good_state()
    r = c.post(LOAD, json=good)
    assert r.status_code == 200, r.text
    assert r.json()["warnings"] == []
    r = c.post(LOAD, json=_legacy(good))
    assert r.status_code == 200, r.text
    assert len(r.json()["warnings"]) == 1 and "legacy save" in r.json()["warnings"][0]


def _edited_pre_start():
    mgr = SessionManager(load_vignette(BASE), seed=9)
    ids = list(mgr.world.assets)
    assert len(ids) >= 3
    deleted, moved, untouched = ids[0], ids[1], ids[2:]
    orig_owner = mgr.world.assets[moved].owner
    new_owner = "red" if orig_owner != "red" else "blue"
    assert mgr.creator_delete_asset(deleted)[0]
    assert mgr.creator_edit_asset(moved, {"owner": new_owner})[0]
    assert mgr.add_tle("FORCE-TLE-1", TLE1, TLE2, owner="blue")[0]
    return mgr, deleted, moved, new_owner, untouched


def _ids_by_bucket(content: dict) -> dict[str, set]:
    return {b: {a["id"] for a in content[f"{b}_forces"]} for b in ("blue", "red", "neutral")}


@pytest.mark.verifies("FR-7220")
def test_content_equals_the_saved_force_after_pre_start_edits():
    mgr, deleted, moved, new_owner, untouched = _edited_pre_start()
    content = _rt(mgr.save_state())["content"]
    by = _ids_by_bucket(content)
    everything = set().union(*by.values())
    assert deleted not in everything
    assert moved in by[new_owner]
    assert sum(moved in v for v in by.values()) == 1
    assert "FORCE-TLE-1" in by["blue"]
    authored = load_vignette(BASE).model_dump(mode="json")
    authored_entries = {a["id"]: a for b in ("blue", "red", "neutral") for a in authored[f"{b}_forces"]}
    saved_entries = {a["id"]: a for b in ("blue", "red", "neutral") for a in content[f"{b}_forces"]}
    for aid in untouched:
        assert saved_entries[aid] == authored_entries[aid]
    # The content's force ids equal the baseline's.
    assert everything == set(mgr.save_state()["baseline"]["assets"])


@pytest.mark.verifies("FR-7210", "FR-7220")
def test_resume_unchanged_and_content_alone_builds_same_force():
    mgr, *_ = _edited_pre_start()
    state = _rt(mgr.save_state())
    resumed = SessionManager.from_state(state)
    assert resumed.sim.world.model_dump() == mgr.sim.world.model_dump()
    from spacesim.content.vignette import build_world
    rebuilt, _ = build_world(Vignette.model_validate(state["content"]), state["overrides"])
    assert set(rebuilt.assets) == set(state["baseline"]["assets"])
    assert {i: a.owner for i, a in rebuilt.assets.items()} == \
        {i: a["owner"] for i, a in state["baseline"]["assets"].items()}


@pytest.mark.verifies("FR-7220")
def test_untouched_session_content_is_the_authored_vignette():
    mgr = SessionManager(load_vignette(BASE), seed=2)
    assert _rt(mgr.save_state())["content"] == load_vignette(BASE).model_dump(mode="json")


# ---------------------------------------------------------------------------------------------
# IP-1103 — save validation completion (VR-1102 F-1/F-2): the remaining malformed fields are 400s.
# ---------------------------------------------------------------------------------------------

def _with(good: dict, **kw) -> dict:
    s = copy.deepcopy(good)
    s.update(kw)
    return s


def _last_event_time(state: dict) -> int:
    ents = state["eventlog"]["entries"]
    return max((e["sim_time"] for e in ents), default=0)


@pytest.mark.verifies("FR-7230", "NFR-1600")
@pytest.mark.parametrize("bad", ["a string", ["x"], 7], ids=["str", "list", "num"])
def test_non_mapping_overrides_is_400_naming_overrides(bad):
    _refused(_client(), _with(_good_state(), overrides=bad), "overrides")


@pytest.mark.verifies("FR-7230", "NFR-1600")
@pytest.mark.parametrize("t", [None, "5", 1.5, True], ids=["null", "str", "float", "bool"])
def test_pending_row_with_bad_t_is_400(t):
    row = {"t": t, "kind": "bus_tick", "actor": "system", "payload": {}, "tag": ""}
    _refused(_client(), _with(_good_state(), pending=[row]), "pending")


@pytest.mark.verifies("FR-7230", "NFR-1600")
@pytest.mark.parametrize("row", [{"t": 5}, {"t": 5, "kind": ""}, {"t": 5, "kind": 3},
                                 {"t": 5, "kind": "x", "payload": "no"}],
                         ids=["no-kind", "empty-kind", "int-kind", "str-payload"])
def test_pending_row_with_bad_kind_or_payload_is_400(row):
    _refused(_client(), _with(_good_state(), pending=[row]), "pending")


@pytest.mark.verifies("FR-7230", "NFR-1600")
def test_valid_pending_rows_still_load():
    good = _good_state()
    r = _client().post(LOAD, json=_with(good, pending=good["pending"]))
    assert r.status_code == 200, r.text


def _order(**kw) -> dict:
    o = {"cell": "blue", "actor": "x", "action": "observe", "target": None, "params": {},
         "issued_at": 0, "earliest_window": None, "delivery_path": None, "status": "draft",
         "fail_reason": None, "id": "ord-1"}
    o.update(kw)
    return o


@pytest.mark.verifies("FR-7230", "NFR-1600")
@pytest.mark.parametrize("kw", [{"cell": "green"}, {"actor": 5}, {"action": ["a"]}, {"id": 7},
                                {"bogus_field": 1}, {"params": "x"}],
                         ids=["cell", "actor", "action", "id", "unknown-field", "params"])
def test_junk_order_row_is_400_naming_orders_and_index(kw):
    c = _client()
    before = _sessions(c)
    r = c.post(LOAD, json=_with(_good_state(), orders=[_order(), _order(**{"id": "ord-2", **kw})]))
    assert r.status_code == 400, r.text
    assert "orders" in r.json()["detail"] and "1" in r.json()["detail"]
    assert _sessions(c) == before


def _ssn(**kw) -> dict:
    s = {"id": "ssn-1", "cell": "blue", "intent": "track", "target": "t", "regime": "LEO",
         "priority": "routine"}
    s.update(kw)
    return s


@pytest.mark.verifies("FR-7230", "NFR-1600")
@pytest.mark.parametrize("kw", [{"cell": "green"}, {"id": 4}, {"intent": 3}, {"bogus": 1},
                                {"collect_at": "soon"}],
                         ids=["cell", "id", "intent", "unknown-field", "collect_at"])
def test_junk_ssn_row_is_400_naming_ssn_requests(kw):
    _refused(_client(), _with(_good_state(), ssn_requests=[_ssn(**kw)]), "ssn_requests")


@pytest.mark.verifies("FR-7230", "NFR-1600")
def test_valid_order_and_ssn_rows_still_load():
    r = _client().post(LOAD, json=_with(_good_state(), orders=[_order()], ssn_requests=[_ssn()]))
    assert r.status_code == 200, r.text


def _start_us(state: dict) -> int:
    from spacesim.engine import simtime
    return simtime.from_iso(state["content"]["start_epoch_utc"])


@pytest.mark.verifies("FR-7230", "NFR-1600")
@pytest.mark.parametrize("which", ["negative", "before-start", "below-last-event", "above-ceiling"])
def test_out_of_range_final_time_is_400_naming_final_time(which):
    good = _good_state()
    ft = {"negative": -1, "before-start": _start_us(good) - 1,
          "below-last-event": _last_event_time(good) - 1,
          "above-ceiling": _start_us(good) + SessionManager.MAX_SAVE_SPAN_US + 1}[which]
    _refused(_client(), _with(good, final_time=ft), "final_time")


@pytest.mark.verifies("FR-7230", "NFR-1600", "FR-4330")
def test_final_time_boundaries_load():
    good = _good_state()
    c = _client()
    r = c.post(LOAD, json=_with(good, final_time=_last_event_time(good)))
    assert r.status_code == 200, r.text
    assert c.post(LOAD, json=good).status_code == 200


@pytest.mark.verifies("FR-7230", "NFR-1600", "FR-4330")
def test_final_time_ceiling_is_one_year_and_exceeds_shipped_horizons():
    assert SessionManager.MAX_SAVE_SPAN_US == 366 * 86400 * 1_000_000
    from spacesim.content.vignette import list_vignettes
    longest = max(load_vignette(v["id"] if isinstance(v, dict) else v.id).estimated_duration_min
                  for v in list_vignettes())
    assert longest * 60 * 4 * 1_000_000 < SessionManager.MAX_SAVE_SPAN_US


@pytest.mark.verifies("FR-7230", "NFR-1600")
@pytest.mark.parametrize("bad", [5, {"a": 1}, ["x"]], ids=["num", "obj", "list"])
def test_non_string_classification_is_400(bad):
    _refused(_client(), _with(_good_state(), classification=bad), "classification")


@pytest.mark.verifies("FR-7230", "NFR-1600")
def test_absent_and_string_classification_load():
    good = _good_state()
    c = _client()
    s = copy.deepcopy(good); s.pop("classification", None)
    assert c.post(LOAD, json=s).status_code == 200
    assert c.post(LOAD, json=_with(good, classification="UNCLASSIFIED")).status_code == 200


@pytest.mark.verifies("FR-7230", "NFR-1600")
def test_whole_refused_set_leaves_registry_unchanged_and_valid_saves_unchanged():
    c = _client()
    good = _good_state()
    before = _sessions(c)
    for s in (_with(good, overrides="x"), _with(good, final_time=-1), _with(good, classification=1),
              _with(good, pending=[{"t": None, "kind": "x"}])):
        assert c.post(LOAD, json=s).status_code == 400
    assert _sessions(c) == before
    r = c.post(LOAD, json=good)
    assert r.status_code == 200 and r.json()["warnings"] == []
    r = c.post(LOAD, json=_legacy(good))
    assert r.status_code == 200 and len(r.json()["warnings"]) == 1


def _legacy_missing() -> dict:
    s = _legacy(_good_state())
    s["vignette_id"] = "no-such-vignette-file"
    return s


@pytest.mark.verifies("FR-7230", "NFR-1600")
def test_legacy_missing_vignette_wording_is_pinned():
    r = _client().post(LOAD, json=_legacy_missing())
    assert r.status_code == 400
    assert "not available in the content directories" in r.json()["detail"]
    assert "no-such-vignette-file" in r.json()["detail"]


@pytest.mark.verifies("FR-7230", "NFR-1600")
def test_server_backstop_alone_turns_missing_vignette_into_400(monkeypatch):
    monkeypatch.setattr(SessionManager, "validate_save", staticmethod(lambda state: None))
    r = _client().post(LOAD, json=_legacy_missing())
    assert r.status_code == 400, r.text


@pytest.mark.verifies("FR-7230", "NFR-1600")
def test_validate_save_reraises_missing_vignette_as_value_error():
    with pytest.raises(ValueError) as ei:
        SessionManager.validate_save(_legacy_missing())
    assert not isinstance(ei.value, FileNotFoundError)
    assert "not available in the content directories" in str(ei.value)
