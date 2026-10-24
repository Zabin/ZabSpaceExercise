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
