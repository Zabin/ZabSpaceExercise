"""IP-1310 — load-time vignette validation (FS-131 v1.1; FR-5310–FR-5314, NFR-1600, NFR-2200).

A vignette loaded by id either becomes a session or is refused with ``VignetteValidationError``
naming every failing element. Refusals reach HTTP as 400/404, never 500, and leave the session
registry untouched. Closes `BL-0220` (bare 500, silent Load) and `BL-0237` (a malformed TLE
crashing the first clock advance).
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from spacesim.content import vignette as vmod
from spacesim.content.vignette import (
    VIGNETTE_DIR,
    Vignette,
    VignetteValidationError,
    list_vignettes,
    load_vignette,
)
from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import SessionManager
from spacesim.ui_web.server import create_app

GOOD_TLE1 = "1 43013U 17073A   24001.50000000  .00000023  00000-0  12345-4 0  9995"
GOOD_TLE2 = "2 43013  98.5691 100.1234 0001234  90.1234 270.1234 14.19560570123456"


def _raw(filename: str) -> dict:
    return yaml.safe_load((VIGNETTE_DIR / filename).read_text(encoding="utf-8"))


def _write(tmp_path: Path, vid: str, mutate, base: str = "03-gnss-ew-campaign.yaml") -> str:
    data = copy.deepcopy(_raw(base))
    data["vignette"]["id"] = vid
    mutate(data["vignette"])
    (tmp_path / f"{vid}.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    return vid


def _refusal(tmp_path: Path, vid: str) -> VignetteValidationError:
    with pytest.raises(VignetteValidationError) as info:
        load_vignette(vid, external_dirs=[tmp_path])
    return info.value


def _wheres(err: VignetteValidationError) -> str:
    return " | ".join(f"{p['where']}: {p['reason']}" for p in err.problems)


def _sat(v: dict) -> dict:
    return next(a for a in v["blue_forces"] if a.get("kind", "satellite") == "satellite")


# --------------------------------------------------------------------------- #
# Test 1 — sensor field rules surface at load (criteria 1–2, BL-0220)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("field,value", [
    ("beam_mode", "Fence"),
    ("usable_phase_angle_deg", [100, 20]),
    ("altitude_band_affinity", "Leo"),
])
def test_sensor_field_rules_refused_at_load(tmp_path, field, value):
    def mutate(v):
        sensor = v["sensors"][0]
        sensor[field] = value
        if field == "usable_phase_angle_deg":
            sensor["needs_lighting"] = True
        if field == "altitude_band_affinity":
            sensor["kind"] = "space_based"
            sensor.pop("location", None)
            sensor["orbit"] = dict(_sat(v)["orbit"])
    vid = _write(tmp_path, f"bad-sensor-{field.replace('_', '-')}", mutate, base="04-co-orbital-threat-escort.yaml")
    err = _refusal(tmp_path, vid)
    sid = _raw("04-co-orbital-threat-escort.yaml")["vignette"]["sensors"][0]["id"]
    text = _wheres(err)
    assert f"sensors[{sid}]" in text
    assert field in text


# --------------------------------------------------------------------------- #
# Test 2 — TLE parse (criterion 3, FR-5311, BL-0237)
# --------------------------------------------------------------------------- #
def test_malformed_tle_refused_naming_asset(tmp_path):
    def mutate(v):
        _sat(v)["orbit"] = {"source": "tle", "tle_line1": "1 99999U garbage", "tle_line2": "2 nonsense"}
    vid = _write(tmp_path, "bad-tle", mutate)
    err = _refusal(tmp_path, vid)
    sat_id = _sat(_raw("03-gnss-ew-campaign.yaml")["vignette"])["id"]
    assert sat_id in _wheres(err)


def test_good_tle_loads(tmp_path):
    def mutate(v):
        _sat(v)["orbit"] = {"source": "tle", "tle_line1": GOOD_TLE1, "tle_line2": GOOD_TLE2}
    vid = _write(tmp_path, "good-tle", mutate)
    vig = load_vignette(vid, external_dirs=[tmp_path])
    assert vig.id == vid


# --------------------------------------------------------------------------- #
# Test 3 — orbit / location presence (criterion 11, FR-5312; cyber units exempt)
# --------------------------------------------------------------------------- #
def test_satellite_without_orbit_refused(tmp_path):
    def mutate(v):
        _sat(v).pop("orbit")
    err = _refusal(tmp_path, _write(tmp_path, "sat-no-orbit", mutate))
    assert "BLUE-GNSS" in _wheres(err) and "orbit" in _wheres(err)


def test_jammer_without_location_refused(tmp_path):
    def mutate(v):
        next(a for a in v["red_forces"] if a["kind"] == "jammer").pop("location")
    err = _refusal(tmp_path, _write(tmp_path, "jam-no-loc", mutate))
    assert "RED-JAM" in _wheres(err) and "location" in _wheres(err)


def test_cyber_unit_without_location_loads():
    raw = _raw("06-satcom-cyber-link.yaml")["vignette"]
    cyber = [a for a in raw["red_forces"] if a.get("kind") == "cyber_unit"]
    assert cyber and all("location" not in a for a in cyber)
    assert load_vignette(raw["id"]).id == raw["id"]


# --------------------------------------------------------------------------- #
# Test 4 — duplicate ids (criterion 5, FR-5313)
# --------------------------------------------------------------------------- #
def test_duplicate_asset_id_across_forces_refused(tmp_path):
    def mutate(v):
        clone = copy.deepcopy(_sat(v))
        v["red_forces"].append(clone)
    err = _refusal(tmp_path, _write(tmp_path, "dup-asset", mutate))
    assert "BLUE-GNSS" in _wheres(err)


def test_duplicate_sensor_id_refused(tmp_path):
    def mutate(v):
        v["sensors"].append(copy.deepcopy(v["sensors"][0]))
    vid = _write(tmp_path, "dup-sensor", mutate, base="04-co-orbital-threat-escort.yaml")
    err = _refusal(tmp_path, vid)
    sid = _raw("04-co-orbital-threat-escort.yaml")["vignette"]["sensors"][0]["id"]
    assert sid in _wheres(err)


# --------------------------------------------------------------------------- #
# Test 5 — roles_needed references (criterion 4, FR-5314)
# --------------------------------------------------------------------------- #
def test_roles_needed_unknown_reference_refused(tmp_path):
    def mutate(v):
        v["roles_needed"] = [{"asset_or_constellation": "NO-SUCH-SAT", "role": "bus"}]
    err = _refusal(tmp_path, _write(tmp_path, "role-unknown", mutate))
    assert "NO-SUCH-SAT" in _wheres(err)


def test_roles_needed_asset_and_group_references_load(tmp_path):
    def mutate(v):
        _sat(v)["group"] = "NAV-GROUP"
        v["roles_needed"] = [{"asset_or_constellation": "BLUE-GNSS", "role": "bus"},
                             {"asset_or_constellation": "NAV-GROUP", "role": "payload"}]
    vid = _write(tmp_path, "role-ok", mutate)
    assert len(load_vignette(vid, external_dirs=[tmp_path]).roles_needed) == 2


# --------------------------------------------------------------------------- #
# Test 6 — every problem is collected
# --------------------------------------------------------------------------- #
def test_all_problems_collected(tmp_path):
    def mutate(v):
        _sat(v).pop("orbit")
        v["roles_needed"] = [{"asset_or_constellation": "GHOST", "role": "both"}]
    err = _refusal(tmp_path, _write(tmp_path, "two-defects", mutate))
    text = _wheres(err)
    assert "BLUE-GNSS" in text and "GHOST" in text
    assert len(err.problems) >= 2


def test_schema_error_is_a_validation_error(tmp_path):
    def mutate(v):
        v["estimated_duration_min"] = "long"
    err = _refusal(tmp_path, _write(tmp_path, "schema-bad", mutate))
    assert "estimated_duration_min" in _wheres(err)


def test_bad_start_epoch_refused(tmp_path):
    def mutate(v):
        v["start_epoch_utc"] = "yesterday"
    err = _refusal(tmp_path, _write(tmp_path, "epoch-bad", mutate))
    assert "start_epoch_utc" in _wheres(err)


# --------------------------------------------------------------------------- #
# Test 7 — HTTP mapping (criteria 1, 6; BL-0220)
# --------------------------------------------------------------------------- #
@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(vmod, "_configured_external_dirs", lambda: [tmp_path])
    api = InProcessSession()
    return TestClient(create_app(api), raise_server_exceptions=False), api


def test_http_invalid_vignette_is_400(tmp_path, client):
    c, _ = client

    def mutate(v):
        v["sensors"][0]["beam_mode"] = "Fence"
    vid = _write(tmp_path, "http-bad", mutate, base="04-co-orbital-threat-escort.yaml")
    r = c.post("/api/sessions", json={"vignette_id": vid, "seed": 1})
    assert r.status_code == 400
    detail = r.json()["detail"]
    assert detail["error"] == "invalid_vignette"
    assert detail["vignette"] == vid
    assert any(p["where"].startswith("sensors[BLUE-RADAR]") and "beam_mode" in p["where"] + p["reason"]
               for p in detail["problems"])
    assert "beam_mode" in detail["message"]
    t = c.get(f"/api/vignettes/{vid}/tutorial")
    assert t.status_code == 400


def test_http_unknown_id_is_404(client):
    c, _ = client
    r = c.post("/api/sessions", json={"vignette_id": "no-such-vignette", "seed": 1})
    assert r.status_code == 404
    assert "no-such-vignette" in r.json()["detail"]


def test_http_traversal_id_is_400(client):
    c, _ = client
    r = c.post("/api/sessions", json={"vignette_id": "../etc", "seed": 1})
    assert r.status_code == 400


# --------------------------------------------------------------------------- #
# Test 8 — registry untouched on refusal (criterion 8, FS-131 OQ5)
# --------------------------------------------------------------------------- #
def test_refused_load_leaves_registry_untouched(tmp_path, monkeypatch):
    monkeypatch.setattr(vmod, "_configured_external_dirs", lambda: [tmp_path])

    def mutate(v):
        v["sensors"][0]["beam_mode"] = "Fence"
    bad = _write(tmp_path, "reg-bad", mutate, base="04-co-orbital-threat-escort.yaml")
    api = InProcessSession()
    with pytest.raises(VignetteValidationError):
        api.load_vignette(bad)
    assert api._sessions == {} and api._counter == 0
    assert api.load_vignette("training-basics") == "sess-1"


def test_refused_load_at_cap_evicts_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(vmod, "_configured_external_dirs", lambda: [tmp_path])
    monkeypatch.setattr(InProcessSession, "MAX_LIVE_SESSIONS", 2)

    def mutate(v):
        v["roles_needed"] = [{"asset_or_constellation": "GHOST", "role": "both"}]
    bad = _write(tmp_path, "cap-bad", mutate)
    api = InProcessSession()
    first = api.load_vignette("training-basics")
    second = api.load_vignette("training-basics")
    with pytest.raises(VignetteValidationError):
        api.load_vignette(bad)
    assert list(api._sessions) == [first, second] and api._counter == 2
    third = api.load_vignette("training-basics")
    assert list(api._sessions) == [second, third]


# --------------------------------------------------------------------------- #
# Test 9 — the shipped library is unchanged (criterion 9)
# --------------------------------------------------------------------------- #
def test_every_shipped_vignette_loads():
    built_in = [v["id"] for v in list_vignettes(external_dirs=[]) if v["origin"] == "built-in"]
    assert len(built_in) == 19
    for vid in built_in:
        assert load_vignette(vid, external_dirs=[]).id == vid


@pytest.mark.parametrize("filename", ["03-gnss-ew-campaign.yaml", "06-satcom-cyber-link.yaml"])
def test_gate_does_not_change_the_built_session(filename):
    raw = _raw(filename)["vignette"]
    gated = SessionManager(load_vignette(raw["id"]), seed=21)
    ungated = SessionManager(Vignette.model_validate(copy.deepcopy(raw)), seed=21)
    assert gated.sim.world.model_dump() == ungated.sim.world.model_dump()
    gated.start(); ungated.start()
    gated.step(1800); ungated.step(1800)
    assert gated.sim.world.model_dump() == ungated.sim.world.model_dump()
    assert ([e.model_dump() for e in gated.sim.eventlog.entries]
            == [e.model_dump() for e in ungated.sim.eventlog.entries])
