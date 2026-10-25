"""IP-1101 — Self-contained saves (FS-110 v2.0; FR-7210/FR-7220/FR-7230, NFR-1800).

A new save carries the vignette as loaded (the content portion), the replay baseline, a format
version and the simulator version, so it resumes without its vignette file and keeps White Cell
force edits. Tests that edit/delete/rename a vignette file work on a copy in a temporary external
content directory — never a shipped file.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from spacesim.content.vignette import (Vignette, VIGNETTE_DIR, build_world, list_vignettes,
                                       load_vignette, validate_vignette)
from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import SessionManager


from tle_helpers import in_epoch_tle  # noqa: E402 — IP-1086: a TLE valid at the 2030 exercise start
TLE1, TLE2 = in_epoch_tle()
SHIPPED = [v["id"] for v in list_vignettes()]
BASE = "leo-isr-denial"


def _rt(state: dict) -> dict:
    """A save travels as JSON; prove it survives that."""
    return json.loads(json.dumps(state))


def _world(mgr: SessionManager) -> dict:
    return mgr.sim.world.model_dump()


def _copy_vignette(tmp_path: Path, monkeypatch, new_id: str = "copy-of-base") -> Path:
    """Copy a shipped vignette to a temporary external content dir under a new id and point the
    loader at it (IP-1180's `content:` configuration)."""
    ext = tmp_path / "ext"
    ext.mkdir()
    raw = yaml.safe_load((VIGNETTE_DIR / f"01-{BASE}.yaml").read_text(encoding="utf-8"))
    raw["vignette"]["id"] = new_id
    path = ext / f"{new_id}.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(yaml.safe_dump({"content": {"external_vignette_dirs": [str(ext)]}}), encoding="utf-8")
    monkeypatch.setenv("SPACESIM_CONFIG", str(cfg))
    return path


def _started(mgr: SessionManager, advance_s: int = 600) -> SessionManager:
    mgr.start()
    mgr.set_clock(False)
    mgr.step(advance_s)
    return mgr


@pytest.mark.verifies("FR-7210")
@pytest.mark.parametrize("vid", SHIPPED)
def test_immediate_round_trip_every_shipped_vignette(vid):
    mgr = _started(SessionManager(load_vignette(vid), seed=3), 300)
    resumed = SessionManager.from_state(_rt(mgr.save_state()))
    assert _world(resumed) == _world(mgr)
    assert resumed.sim.clock.now == mgr.sim.clock.now


@pytest.mark.verifies("FR-7230")
def test_resume_after_vignette_file_is_edited(tmp_path, monkeypatch):
    path = _copy_vignette(tmp_path, monkeypatch)
    mgr = _started(SessionManager(load_vignette("copy-of-base"), seed=5))
    state = _rt(mgr.save_state())
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    raw["vignette"]["title"] = "EDITED"
    raw["vignette"]["blue_forces"] = raw["vignette"]["blue_forces"][:1]
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    resumed = SessionManager.from_state(state)
    assert _world(resumed) == _world(mgr)
    assert len(resumed.sim.world.assets) == len(mgr.sim.world.assets)


@pytest.mark.verifies("FR-7230")
@pytest.mark.parametrize("how", ["delete", "rename"])
def test_resume_after_vignette_file_deleted_or_renamed(tmp_path, monkeypatch, how):
    path = _copy_vignette(tmp_path, monkeypatch)
    mgr = _started(SessionManager(load_vignette("copy-of-base"), seed=6))
    state = _rt(mgr.save_state())
    if how == "delete":
        path.unlink()
    else:
        path.rename(path.with_name("renamed.yaml.bak"))
    with pytest.raises(Exception):
        load_vignette("copy-of-base")   # the file really is gone
    resumed = SessionManager.from_state(state)
    assert _world(resumed) == _world(mgr)


@pytest.mark.verifies("FR-7210")
@pytest.mark.parametrize("advance", [False, True], ids=["before-start", "after-start-and-advance"])
def test_force_added_assets_survive(advance):
    mgr = SessionManager(load_vignette(BASE), seed=7)
    assert mgr.add_tle("FORCE-TLE-1", TLE1, TLE2, owner="blue")[0]
    assert mgr.add_ground_asset("FORCE-GND-1", 12.5, 45.0, owner="red")[0]
    if advance:
        _started(mgr)
    resumed = SessionManager.from_state(_rt(mgr.save_state()))
    for aid in ("FORCE-TLE-1", "FORCE-GND-1"):
        assert aid in resumed.sim.world.assets
        assert resumed.sim.world.assets[aid].model_dump() == mgr.sim.world.assets[aid].model_dump()
    assert _world(resumed) == _world(mgr)
    # Rewinding the resumed session keeps the edit too (the baseline carries it).
    resumed.rewind_to(resumed.ctx.start_epoch)
    assert "FORCE-TLE-1" in resumed.sim.world.assets


@pytest.mark.verifies("FR-7220")
def test_content_portion_extracts_and_loads_as_a_fresh_vignette():
    mgr = SessionManager(load_vignette(BASE), seed=8)
    assert mgr.add_tle("FORCE-TLE-1", TLE1, TLE2, owner="blue")[0]
    assert mgr.add_ground_asset("FORCE-GND-1", 12.5, 45.0, owner="red")[0]
    content = _rt(mgr.save_state())["content"]
    vig = Vignette.model_validate(content)
    assert validate_vignette(vig) == []
    fresh = SessionManager(vig, seed=1)
    fresh.start()
    assert {"FORCE-TLE-1", "FORCE-GND-1"} <= set(fresh.sim.world.assets)
    original = load_vignette(BASE)
    assert content["parameters"] == original.model_dump()["parameters"]
    assert content["title"] == original.title


@pytest.mark.verifies("FR-7220")
@pytest.mark.parametrize("vid", SHIPPED)
def test_content_portion_world_matches_baseline_without_force_edits(vid):
    mgr = SessionManager(load_vignette(vid), seed=2)
    state = _rt(mgr.save_state())
    rebuilt, _ = build_world(Vignette.model_validate(state["content"]), state["overrides"])
    assert rebuilt.model_dump() == state["baseline"]


@pytest.mark.verifies("FR-7230", "NFR-1800")
def test_invalid_content_portion_refused_with_problems_and_no_session():
    api = InProcessSession()
    mgr = SessionManager(load_vignette(BASE), seed=1)
    state = _rt(mgr.save_state())
    state["content"]["blue_forces"].append({"id": "BROKEN", "kind": "satellite"})  # no orbit
    with pytest.raises(ValueError) as exc:
        api.load_save(state)
    assert "BROKEN" in str(exc.value)
    assert api.list_sessions() == []


@pytest.mark.verifies("FR-7230", "NFR-1800")
def test_invalid_baseline_refused_and_no_session():
    api = InProcessSession()
    state = _rt(SessionManager(load_vignette(BASE), seed=1).save_state())
    state["baseline"] = {"not": "a world"}
    with pytest.raises(ValueError):
        api.load_save(state)
    assert api.list_sessions() == []


@pytest.mark.verifies("FR-7210")
def test_legacy_save_resumes_by_id_with_warning():
    api = InProcessSession()
    mgr = _started(SessionManager(load_vignette(BASE), seed=4))
    state = _rt(mgr.save_state())
    for key in ("save_format", "content", "baseline", "simulator_version"):
        state.pop(key, None)
    sid, warnings = api.load_save_with_warnings(state)
    assert _world(api._sessions[sid]) == _world(mgr)
    assert any(BASE in w and "vignette file" in w for w in warnings)


@pytest.mark.verifies("FR-7230")
def test_simulator_version_mismatch_resumes_with_warning_naming_both():
    api = InProcessSession()
    mgr = _started(SessionManager(load_vignette(BASE), seed=4))
    state = _rt(mgr.save_state())
    saved_version = state["simulator_version"]
    state["simulator_version"] = "0.0.0-older"
    sid, warnings = api.load_save_with_warnings(state)
    assert _world(api._sessions[sid]) == _world(mgr)
    joined = " ".join(warnings)
    assert "0.0.0-older" in joined and saved_version not in ("0.0.0-older",)
    # a matching version warns about nothing
    state["simulator_version"] = saved_version
    _, quiet = api.load_save_with_warnings(state)
    assert quiet == []


@pytest.mark.verifies("NFR-1800")
def test_resume_in_a_fresh_inprocess_session():
    mgr = _started(SessionManager(load_vignette(BASE), seed=9))
    state = _rt(mgr.save_state())
    other = InProcessSession()
    sid = other.load_save(state)
    assert _world(other._sessions[sid]) == _world(mgr)


@pytest.mark.verifies("FR-7210")
def test_save_keeps_every_pre_existing_key():
    state = SessionManager(load_vignette(BASE), seed=1).save_state()
    for key in ("vignette_id", "overrides", "classification", "seed", "final_time", "started",
                "eventlog", "pending", "orders", "ssn_requests"):
        assert key in state
    for key in ("save_format", "content", "baseline", "simulator_version"):
        assert key in state
