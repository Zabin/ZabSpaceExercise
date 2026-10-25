"""IP-1086 — one shared asset validator at every authoring boundary (H-3, M-1, M-3).

Stale-epoch TLEs and unphysical Keplerian elements are refused at force-add, bulk/OMM import,
Creator edit and the load gate alike; the Creator save validates before writing; the scene,
window and contact reads survive an asset that still cannot be propagated.
"""
from __future__ import annotations

import ast
import copy
import re
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
import yaml  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.content import vignette as vig_mod  # noqa: E402
from spacesim.engine import simtime  # noqa: E402
from spacesim.engine.entities import Asset  # noqa: E402
from spacesim.engine.orbit import OrbitState  # noqa: E402
from spacesim.session import InProcessSession  # noqa: E402
from spacesim.ui_web.server import create_app  # noqa: E402
from tle_helpers import in_epoch_tle  # noqa: E402

# A 2024-epoch TLE that SGP4 accepts at its own epoch (the pre-IP-1086 force-add proof) but cannot
# propagate to the 2030 exercise start (sgp4 error code 1). The plain 2024 ISS TLE happens to
# propagate in 2030 under sgp4 2.27, so the test uses this decay-prone element set instead; the
# planning pass's reproduction of the 2024 ISS TLE depends on the installed sgp4 build.
STALE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
STALE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 16.20000000999993"
GOOD1, GOOD2 = in_epoch_tle()
START = simtime.from_iso("2030-03-15T06:00:00Z")


@pytest.fixture(autouse=True)
def save_dir(tmp_path, monkeypatch):
    cfg = tmp_path / "spacesim.config.yaml"
    d = tmp_path / "user_saves"
    d.mkdir()
    cfg.write_text(f"content:\n  user_save_dir: {d}\n  external_vignette_dirs:\n    - {d}\n", encoding="utf-8")
    monkeypatch.setenv("SPACESIM_CONFIG", str(cfg))
    return d


@pytest.fixture
def c():
    return TestClient(create_app(), raise_server_exceptions=False)


def _kep(**kw):
    o = dict(source="kepler", a_m=7_000_000.0, e=0.001, i_deg=51.0, raan_deg=10.0, argp_deg=0.0,
             ta_deg=0.0, epoch=START)
    o.update(kw)
    return o


def _sat(aid="K-1", owner="blue", **orbit_kw):
    return {"id": aid, "owner": owner, "kind": "satellite", "orbit": _kep(**orbit_kw)}


def _load(c, vid="leo-isr-denial"):
    return c.post("/api/sessions", json={"vignette_id": vid, "seed": 1}).json()["session"]


def _draft(c):
    return c.post("/api/sessions/draft", json={"title": "D"}).json()["session"]


def _start(c, sid):
    assert c.post(f"/api/sessions/{sid}/start?cell=white").status_code == 200


def _reads_ok(c, sid, asset=None):
    if asset is None:
        asset = next(a["id"] for a in c.get(f"/api/sessions/{sid}/scene/blue").json()["assets"]
                     if a["on_orbit"])
    for url in (f"/api/sessions/{sid}/scene/blue", f"/api/sessions/{sid}/windows/blue/{asset}",
                f"/api/sessions/{sid}/next_contacts/blue"):
        r = c.get(url)
        assert r.status_code == 200, (url, r.status_code)


# ---------------------------------------------------------------- Unit 1
@pytest.mark.verifies("FR-5311")
@pytest.mark.parametrize("draft", [False, True])
def test_stale_epoch_tle_force_add_is_refused_and_reads_stay_200(c, draft):
    sid = _draft(c) if draft else _load(c)
    ack = c.post(f"/api/sessions/{sid}/force/tle?cell=white",
                 json={"id": "STALE", "line1": STALE1, "line2": STALE2, "owner": "blue"}).json()
    assert ack["ok"] is False
    assert "STALE" in ack["reason"] and "TLE does not parse/propagate" in ack["reason"]
    if draft:
        assert all(a["id"] != "STALE" for a in c.get(f"/api/sessions/{sid}/creator/state").json()["assets"])
        assert c.get(f"/api/sessions/{sid}/creator/scene").status_code == 200
    else:
        _start(c, sid)
        _reads_ok(c, sid)


def _tle_file(*entries):
    return "\n".join(f"{n}\n{a}\n{b}" for n, a, b in entries)


@pytest.mark.verifies("FR-5220", "FR-5311")
def test_bulk_import_stale_is_per_object_failure_valid_imports_malformed_reported(c):
    sid = _load(c)
    text = _tle_file(("OLD", STALE1, STALE2), ("NEW", GOOD1, GOOD2), ("BAD", GOOD1, "2 short"))
    r = c.post(f"/api/sessions/{sid}/force/bulk_import?cell=white", json={
        "format": "tle", "content": text,
        "assignments": {n: {"asset_id": f"B-{n}", "owner": "blue"} for n in ("OLD", "NEW", "BAD")}})
    assert r.status_code == 200
    rep = r.json()
    assert [x["raw_id"] for x in rep] == ["OLD", "NEW", "BAD"]
    assert [x["ok"] for x in rep] == [False, True, False]
    assert "B-OLD" in rep[0]["reason"] and "propagate" in rep[0]["reason"]
    _start(c, sid)
    _reads_ok(c, sid, "B-NEW")
    assert c.get(f"/api/sessions/{sid}/scene/blue").status_code == 200


@pytest.mark.verifies("FR-5311", "FR-5220")
@pytest.mark.parametrize("path", ["force", "bulk", "creator_put", "creator_patch"])
def test_in_epoch_tle_is_accepted_on_every_path_and_renders(c, path):
    sid = _draft(c)
    if path == "force":
        assert c.post(f"/api/sessions/{sid}/force/tle?cell=white",
                      json={"id": "OK", "line1": GOOD1, "line2": GOOD2}).json()["ok"]
    elif path == "bulk":
        rep = c.post(f"/api/sessions/{sid}/force/bulk_import?cell=white", json={
            "format": "tle", "content": _tle_file(("OK", GOOD1, GOOD2)),
            "assignments": {"OK": {"asset_id": "OK", "owner": "blue"}}}).json()
        assert rep[0]["ok"]
    else:
        orbit = {"source": "tle", "tle_line1": GOOD1, "tle_line2": GOOD2, "epoch": START}
        if path == "creator_put":
            assert c.put(f"/api/sessions/{sid}/creator/state?cell=white", json={"assets": [
                {"id": "OK", "owner": "blue", "kind": "satellite", "orbit": orbit}]}).json()["ok"]
        else:
            c.put(f"/api/sessions/{sid}/creator/state?cell=white", json={"assets": [
                {"id": "OK", "owner": "blue", "kind": "satellite"}]})
            assert c.patch(f"/api/sessions/{sid}/creator/asset/OK?cell=white",
                           json={"patch": {"orbit": orbit}}).json()["ok"]
    scene = c.get(f"/api/sessions/{sid}/creator/scene")
    assert scene.status_code == 200 and any(a["id"] == "OK" for a in scene.json()["assets"])


_TABLE = {
    "valid_tle": ({"source": "tle", "tle_line1": GOOD1, "tle_line2": GOOD2, "epoch": START}, True),
    "stale_tle": ({"source": "tle", "tle_line1": STALE1, "tle_line2": STALE2, "epoch": START}, False),
    "malformed_tle": ({"source": "tle", "tle_line1": GOOD1, "tle_line2": "2 short", "epoch": START}, False),
    "e_1_5": (_kep(e=1.5), False),
    "a_neg": (_kep(a_m=-5.0), False),
    "a_1000": (_kep(a_m=1000.0), False),
    "e_999_subsurface": (_kep(e=0.999), False),
    "valid_leo": (_kep(), True),
}


@pytest.mark.verifies("FR-5311", "FR-5310")
@pytest.mark.parametrize("name", sorted(_TABLE))
def test_load_gate_and_creator_edit_and_force_add_agree(name):
    orbit, valid = _TABLE[name]
    asset = {"id": "X-1", "owner": "blue", "kind": "satellite", "orbit": orbit}
    # (a) the shared function
    shared = vig_mod.asset_authoring_problems(Asset.model_validate(asset), START)
    assert (shared == []) is valid
    # (b) the load gate
    v = vig_mod.load_vignette("leo-isr-denial")
    v.blue_forces = list(v.blue_forces) + [copy.deepcopy(asset)]
    gate = [p["reason"] for p in vig_mod.validate_vignette(v) if "X-1" in p["where"]]
    assert gate == shared
    # (c) the Creator edit (same strings, naming the asset)
    api = InProcessSession()
    sid = api.create_draft_session(title="t")
    ok, reason = api._sessions[sid].creator_set_state([asset])
    assert ok is valid
    if not valid:
        assert all(s in reason for s in shared) and "X-1" in reason
    # (d) force-add paths
    mgr = api._sessions[sid]
    if orbit["source"] == "tle":
        ok2, reason2 = mgr.add_tle("X-2", orbit["tle_line1"], orbit["tle_line2"])
        if len(orbit["tle_line2"]) >= 69:
            assert ok2 is valid
            if not valid:
                assert all(s in reason2 for s in shared)
    else:
        ok2, reason2 = mgr._force_add_omm_object("X-2", {
            "a_m": orbit["a_m"], "e": orbit["e"], "i_deg": orbit["i_deg"], "raan_deg": 0.0,
            "argp_deg": 0.0, "mean_anomaly_deg": 0.0}, "blue", "satellite")
        assert ok2 is valid
        if not valid:
            assert all(s in reason2 for s in shared)


@pytest.mark.verifies("FR-5311")
def test_no_second_validation_propagation_outside_shared_function():
    root = Path(vig_mod.__file__).resolve().parents[1]
    hits = []
    for rel in ("content", "session/manager.py"):
        p = root / rel
        for f in ([p] if p.is_file() else sorted(p.rglob("*.py"))):
            tree = ast.parse(f.read_text("utf-8"))
            for fn in ast.walk(tree):
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for n in ast.walk(fn):
                        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                and n.func.attr == "rv" and getattr(n.func.value, "id", "") in ("prop", "propagator")):
                            hits.append((f.name, fn.name))
    assert set(hits) <= {("vignette.py", "asset_authoring_problems"),
                        ("vignette.py", "_range_km")}, hits   # _range_km: objective metric, not validation
    text = (root / "session" / "manager.py").read_text("utf-8")
    assert "sat.sgp4(sat.jdsatepoch" not in text


# ---------------------------------------------------------------- Unit 2
_OMM = """CCSDS_OMM_VERS = 2.0
META_START
OBJECT_NAME = {n}
OBJECT_ID = 2030-001A
CENTER_NAME = EARTH
REF_FRAME = TEME
TIME_SYSTEM = UTC
MEAN_ELEMENT_THEORY = SGP4
META_STOP
EPOCH = 2030-03-15T06:00:00.000
SEMI_MAJOR_AXIS = {a}
ECCENTRICITY = {e}
INCLINATION = 51.6
RA_OF_ASC_NODE = 10.0
ARG_OF_PERICENTER = 0.0
MEAN_ANOMALY = 0.0
"""


@pytest.mark.verifies("FR-5220", "FR-5310")
def test_omm_bulk_import_unphysical_objects_are_per_object_failures(c):
    sid = _load(c)
    sma = lambda m: m / 1000.0   # noqa: E731 — KVN SEMI_MAJOR_AXIS is in km
    content = "\n".join([_OMM.format(n="E1", a=sma(7e6), e=1.2), _OMM.format(n="NEG", a=-5, e=0.001),
                         _OMM.format(n="SUB", a=1, e=0.001), _OMM.format(n="OK", a=sma(7e6), e=0.001)])
    rep = c.post(f"/api/sessions/{sid}/force/bulk_import?cell=white", json={
        "format": "omm", "content": content,
        "assignments": {n: {"asset_id": n, "owner": "blue"} for n in ("E1", "NEG", "SUB", "OK")}}).json()
    by = {r["raw_id"]: r for r in rep}
    assert [by[n]["ok"] for n in ("E1", "NEG", "SUB", "OK")] == [False, False, False, True]
    assert all(by[n]["reason"] for n in ("E1", "NEG", "SUB"))


_BAD_EDITS = [
    ("e1.5", _sat(e=1.5)), ("aneg", _sat(a_m=-5.0)), ("a1000", _sat(a_m=1000.0)),
    ("i200", _sat(i_deg=200.0)),
    ("negdv", {**_sat(), "resources": {"delta_v_ms": -1.0}}),
    ("negammo", {**_sat(), "resources": {"ammo": -1}}),
    ("negpower", {**_sat(), "resources": {"power_w": -3.0}}),
    ("trav", {**_sat(), "id": "../x"}), ("space", {**_sat(), "id": "a b"}),
]


@pytest.mark.verifies("FR-5120", "FR-5310")
@pytest.mark.parametrize("name,asset", _BAD_EDITS, ids=[n for n, _ in _BAD_EDITS])
def test_creator_put_refuses_never_valid_values_atomically(c, name, asset):
    sid = _draft(c)
    good = _sat("GOOD")
    assert c.put(f"/api/sessions/{sid}/creator/state?cell=white", json={"assets": [good]}).json()["ok"]
    ack = c.put(f"/api/sessions/{sid}/creator/state?cell=white", json={"assets": [good, asset]}).json()
    assert ack["ok"] is False and ack["reason"]
    assert asset["id"] in ack["reason"]
    ids = [a["id"] for a in c.get(f"/api/sessions/{sid}/creator/state").json()["assets"]]
    assert ids == ["GOOD"]
    assert c.get(f"/api/sessions/{sid}/creator/scene").status_code == 200


@pytest.mark.verifies("FR-5150", "FR-5310")
@pytest.mark.parametrize("patch", [{"orbit": _kep(e=1.5)}, {"orbit": _kep(a_m=-5.0)},
                                   {"orbit": _kep(a_m=1000.0)}, {"orbit": _kep(i_deg=200.0)},
                                   {"resources": {"delta_v_ms": -1.0}}])
def test_creator_patch_refuses_never_valid_values(c, patch):
    sid = _draft(c)
    c.put(f"/api/sessions/{sid}/creator/state?cell=white", json={"assets": [_sat("P-1")]})
    ack = c.patch(f"/api/sessions/{sid}/creator/asset/P-1?cell=white", json={"patch": patch}).json()
    assert ack["ok"] is False and "P-1" in ack["reason"]
    st = c.get(f"/api/sessions/{sid}/creator/state").json()["assets"][0]
    assert st["orbit"]["e"] == 0.001 and st["orbit"]["a_m"] == 7_000_000.0
    assert c.get(f"/api/sessions/{sid}/creator/scene").status_code == 200


@pytest.mark.verifies("FR-5312", "FR-5120")
def test_creator_put_still_accepts_incomplete_assets(c):
    sid = _draft(c)
    ack = c.put(f"/api/sessions/{sid}/creator/state?cell=white", json={"assets": [
        {"id": "NOORBIT", "owner": "blue", "kind": "satellite"},
        {"id": "NOLOC", "owner": "blue", "kind": "ground_station"}]}).json()
    assert ack["ok"] is True


@pytest.mark.verifies("FR-5310")
@pytest.mark.parametrize("orbit_kw,needle", [({"e": 1.5}, "e"), ({"a_m": -5.0}, "a_m")])
def test_load_gate_refuses_unphysical_elements(c, save_dir, orbit_kw, needle):
    v = vig_mod.load_vignette("leo-isr-denial")
    data = v.model_dump(exclude_none=True)
    data["id"] = "ip1086-bad-orbit"
    data["blue_forces"] = list(data["blue_forces"]) + [_sat("BADORB", **orbit_kw)]
    (save_dir / "ip1086-bad-orbit.yaml").write_text(yaml.safe_dump({"vignette": data}), encoding="utf-8")
    r = c.post("/api/sessions", json={"vignette_id": "ip1086-bad-orbit"})
    assert r.status_code == 400 and "BADORB" in r.text
    assert c.get("/api/vignettes").status_code == 200


@pytest.mark.verifies("FR-5310", "FR-5311")
def test_sweep_shipped_content_passes_the_shared_validator():
    from spacesim.content.vignette import list_vignettes
    n = 0
    for entry in list_vignettes():
        v = vig_mod.load_vignette(entry["id"])        # runs validate_vignette (load gate)
        start = simtime.from_iso(v.start_epoch_utc)
        for owner, force in vig_mod._force_sections(v):
            for spec in force:
                a = Asset.model_validate(vig_mod._asset_data(copy.deepcopy(spec), owner, start))
                assert vig_mod.asset_authoring_problems(a, start) == [], (entry["id"], a.id)
                n += 1
    assert n > 50
    from spacesim.content.ground_sites import load_ground_sites
    assert load_ground_sites()


@pytest.mark.verifies("FR-5310")
def test_review_reproduction_draft_refuses_e_1_5_at_first_put(c):
    sid = _draft(c)
    ack = c.put(f"/api/sessions/{sid}/creator/state?cell=white", json={"assets": [_sat(e=1.5)]}).json()
    assert ack["ok"] is False
    assert c.get(f"/api/sessions/{sid}/creator/scene").status_code == 200


# ---------------------------------------------------------------- Unit 3
def _draft_with(c, assets):
    sid = _draft(c)
    ack = c.put(f"/api/sessions/{sid}/creator/state?cell=white", json={"assets": assets}).json()
    assert ack["ok"], ack
    return sid


_INVALID_DRAFTS = {
    "no_orbit": [{"id": "S", "owner": "blue", "kind": "satellite"}],
    "no_location": [{"id": "G", "owner": "blue", "kind": "ground_station"}],
}


@pytest.mark.verifies("FR-5110")
@pytest.mark.parametrize("name", sorted(_INVALID_DRAFTS))
@pytest.mark.parametrize("existing", [False, True])
def test_invalid_draft_save_is_400_and_writes_nothing(c, save_dir, name, existing):
    sid = _draft_with(c, _INVALID_DRAFTS[name])
    target = save_dir / "ip1086-save.yaml"
    if existing:
        target.write_bytes(b"vignette: sentinel\n")
    r = c.post(f"/api/sessions/{sid}/save_vignette?cell=white",
               json={"vignette_id": "ip1086-save", "title": "T"})
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert "ip1086-save" in detail and ("must declare" in detail)
    if existing:
        assert target.read_bytes() == b"vignette: sentinel\n"
    else:
        assert not target.exists()


@pytest.mark.verifies("FR-5110")
def test_bad_tle_draft_cannot_be_saved(save_dir):
    """A bad TLE can no longer be put in a draft; injecting one below the edit gate is still not saved."""
    api = InProcessSession()
    sid = api.create_draft_session(title="t")
    mgr = api._sessions[sid]
    mgr.world.assets["T"] = Asset(id="T", owner="blue", orbit=OrbitState(
        source="tle", tle_line1=STALE1, tle_line2=STALE2, epoch=START))
    with pytest.raises(ValueError, match="TLE does not parse/propagate"):
        api.save_vignette(sid, "ip1086-badtle", "T")
    assert not (save_dir / "ip1086-badtle.yaml").exists()


@pytest.mark.verifies("FR-5110")
def test_valid_draft_saves_and_loads_and_save_as_scenario_round_trips(c):
    sid = _draft_with(c, [_sat("V-1"), {"id": "GS", "owner": "blue", "kind": "ground_station",
                                         "location": {"lat_deg": 10.0, "lon_deg": 20.0}}])
    r = c.post(f"/api/sessions/{sid}/save_vignette?cell=white", json={"vignette_id": "ip1086-ok", "title": "T"})
    assert r.status_code == 200
    assert c.post("/api/sessions", json={"vignette_id": "ip1086-ok"}).status_code == 200
    for vid in ("leo-isr-denial", "training-basics", "geo-rpo-ambiguity"):
        try:
            s = _load(c, vid)
        except KeyError:
            continue
        _start(c, s)
        out = c.post(f"/api/sessions/{s}/save_vignette?cell=white",
                     json={"vignette_id": f"ip1086-sas-{vid}", "title": "T", "as_scenario": True})
        assert out.status_code == 200, (vid, out.text)
        assert c.post("/api/sessions", json={"vignette_id": f"ip1086-sas-{vid}"}).status_code == 200


@pytest.mark.verifies("FR-5110")
def test_creator_console_surfaces_refused_save_message():
    """The console's api helper surfaces a non-2xx ``detail``; pinned at source level here (the
    Playwright run of the same handler lives in test_vignette_creator_ui.py)."""
    js = (Path(vig_mod.__file__).resolve().parents[1] / "ui_web" / "static" / "creator.js").read_text("utf-8")
    app = (Path(vig_mod.__file__).resolve().parents[1] / "ui_web" / "static" / "app.js").read_text("utf-8")
    assert "save_vignette" in js
    assert re.search(r"detail", app)


# ---------------------------------------------------------------- Read-path robustness
def _poisoned_session():
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    mgr = api._sessions[sid]
    mgr.world.assets["BROKEN"] = Asset(id="BROKEN", owner="blue", kind="satellite",
                                       orbit=OrbitState(**_kep(e=1.5)))
    mgr.sim._initial_state = mgr.world.model_dump()
    api.start(sid)
    return api, sid, mgr


@pytest.mark.verifies("NFR-1600")
def test_reads_skip_an_unpropagatable_asset_instead_of_500(c):
    api, sid, mgr = _poisoned_session()
    blue_ids = [a.id for a in api.get_scene(sid, "blue").assets]
    assert "BROKEN" not in blue_ids and len(blue_ids) >= 1
    red_before = [a.id for a in api.get_scene(sid, "red").assets]
    w = api.windows_ahead(sid, "blue", "BROKEN")
    assert w["windows"] == [] and w["error"] == "propagation_failed"
    nc = api.next_contacts(sid, "blue")
    assert "BROKEN" in nc["next"] and nc["next"]["BROKEN"] is None
    assert [a.id for a in api.get_scene(sid, "red").assets] == red_before
    api.get_view(sid, "blue")  # the fleet view/orders/alarms still answer


@pytest.mark.verifies("NFR-1600")
def test_guarded_reads_over_http_are_200_and_creator_scene_too(c):
    api, sid, mgr = _poisoned_session()
    # Put the same manager behind the app's registry.
    app = create_app(api)
    cl = TestClient(app, raise_server_exceptions=False)
    for url in (f"/api/sessions/{sid}/scene/blue", f"/api/sessions/{sid}/windows/blue/BROKEN",
                f"/api/sessions/{sid}/next_contacts/blue"):
        assert cl.get(url).status_code == 200, url
    assert cl.get(f"/api/sessions/{sid}/windows/blue/BROKEN").json()["error"] == "propagation_failed"
    assert mgr.creator_scene()["assets"] is not None


@pytest.mark.verifies("NFR-1600")
def test_guarded_reads_mutate_nothing():
    api, sid, mgr = _poisoned_session()
    before = mgr.world.model_dump_json()
    from spacesim.session.scene import build_scene
    build_scene(mgr.world, "blue"); mgr.windows_ahead("blue", "BROKEN"); mgr.next_contacts("blue")
    mgr.creator_scene()
    assert mgr.world.model_dump_json() == before
