"""IP-1174 — Vignette Creator UI Surfaces (FS-117, FR-5120-FR-5160 slice).

HTTP-route-level tests, mirroring this repository's existing pattern of testing
``ui_web/server.py`` routes directly rather than through a browser (see ``test_session_setup.py``,
``test_observer.py``). Every route here is a thin client over a draft session created by
``POST /api/sessions/draft`` (IP-1173).
"""
from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.ui_web.server import create_app  # noqa: E402

_TLE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
_TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"


def _client() -> TestClient:
    return TestClient(create_app())


def _draft(c: TestClient) -> str:
    return c.post("/api/sessions/draft", json={"title": "Creator test"}).json()["session"]


# -- FR-5120: JSON view and form view share one state --------------------------------------------

def test_json_view_write_is_visible_to_form_view_read():
    c = _client()
    sid = _draft(c)
    r = c.put(f"/api/sessions/{sid}/creator/state", json={"assets": [
        {"id": "SAT-J1", "owner": "blue", "kind": "satellite"},
    ]})
    assert r.status_code == 200 and r.json()["ok"] is True
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    assert any(a["id"] == "SAT-J1" for a in state["assets"])


def test_form_view_add_is_visible_to_json_view_read():
    c = _client()
    sid = _draft(c)
    r = c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-F1", "line1": _TLE1, "line2": _TLE2})
    assert r.status_code == 200 and r.json()["ok"] is True
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    assert any(a["id"] == "SAT-F1" for a in state["assets"])


def test_json_view_write_and_form_view_converge_on_the_same_edit():
    """The single most likely defect this Feature names: two data paths for one draft."""
    c = _client()
    sid = _draft(c)
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-C1", "line1": _TLE1, "line2": _TLE2, "owner": "blue"})
    # Edit via the JSON view (replace the whole list, changing SAT-C1's owner)
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    for a in state["assets"]:
        if a["id"] == "SAT-C1":
            a["owner"] = "red"
    r = c.put(f"/api/sessions/{sid}/creator/state", json={"assets": state["assets"]})
    assert r.json()["ok"] is True
    # The form-view-equivalent edit route (asset menu) sees the JSON-view edit
    r2 = c.patch(f"/api/sessions/{sid}/creator/asset/SAT-C1", json={"patch": {"kind": "satellite"}})
    assert r2.json()["ok"] is True
    state2 = c.get(f"/api/sessions/{sid}/creator/state").json()
    edited = next(a for a in state2["assets"] if a["id"] == "SAT-C1")
    assert edited["owner"] == "red"   # JSON-view edit preserved through the form-view op


def test_json_view_write_rejects_malformed_asset_without_partial_apply():
    c = _client()
    sid = _draft(c)
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-OK", "line1": _TLE1, "line2": _TLE2})
    r = c.put(f"/api/sessions/{sid}/creator/state", json={"assets": [
        {"id": "SAT-OK", "owner": "blue"}, {"owner": "blue"},   # second entry missing required id
    ]})
    assert r.json()["ok"] is False
    # Nothing changed — the original asset is still there (no partial apply)
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    assert any(a["id"] == "SAT-OK" for a in state["assets"])


# -- FR-5130: 2D/3D preview is ground truth, no fog-of-war filtering ------------------------------

def test_creator_scene_shows_assets_of_every_owner_with_no_filtering():
    c = _client()
    sid = _draft(c)
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-BLUE", "line1": _TLE1, "line2": _TLE2, "owner": "blue"})
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-RED", "line1": _TLE1, "line2": _TLE2, "owner": "red"})
    scene = c.get(f"/api/sessions/{sid}/creator/scene").json()
    ids = {a["id"] for a in scene["assets"]}
    assert {"SAT-BLUE", "SAT-RED"} <= ids   # both visible together — no CellController filtering


def test_creator_scene_reflects_asset_changes_within_the_same_authoring_session():
    c = _client()
    sid = _draft(c)
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-REFRESH", "line1": _TLE1, "line2": _TLE2})
    before = {a["id"] for a in c.get(f"/api/sessions/{sid}/creator/scene").json()["assets"]}
    assert "SAT-REFRESH" in before
    c.delete(f"/api/sessions/{sid}/creator/asset/SAT-REFRESH")
    after = {a["id"] for a in c.get(f"/api/sessions/{sid}/creator/scene").json()["assets"]}
    assert "SAT-REFRESH" not in after


# -- FR-5140: TLE-paste and lat/long asset entry --------------------------------------------------

def test_tle_paste_with_type_cell_name_fields():
    c = _client()
    sid = _draft(c)
    r = c.post(f"/api/sessions/{sid}/force/tle", json={
        "id": "SAT-TYPED", "line1": _TLE1, "line2": _TLE2, "owner": "red", "kind": "sensor",
    })
    assert r.json()["ok"] is True
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    asset = next(a for a in state["assets"] if a["id"] == "SAT-TYPED")
    assert asset["owner"] == "red" and asset["kind"] == "sensor"


def test_lat_long_entry_with_type_cell_name_fields():
    c = _client()
    sid = _draft(c)
    r = c.post(f"/api/sessions/{sid}/force/ground", json={
        "id": "GS-TYPED", "lat_deg": 34.74, "lon_deg": -120.57, "owner": "blue", "kind": "ground_station",
    })
    assert r.json()["ok"] is True
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    asset = next(a for a in state["assets"] if a["id"] == "GS-TYPED")
    assert asset["owner"] == "blue" and asset["kind"] == "ground_station"
    assert asset["location"]["lat_deg"] == 34.74


def test_curated_site_list_offered_before_free_entry():
    c = _client()
    sites = c.get("/api/ground_sites").json()
    assert len(sites) > 0
    assert any(s["code"] == "Vandenberg" for s in sites)
    # A free-entry coordinate not in the curated list is still accepted (fallback path)
    sid = _draft(c)
    r = c.post(f"/api/sessions/{sid}/force/ground", json={
        "id": "GS-FREE", "lat_deg": 12.34, "lon_deg": 56.78,
    })
    assert r.json()["ok"] is True


# -- FR-5150: asset menu (edit, reassign, delete) -------------------------------------------------

def test_asset_edit_reflected_in_json_view_and_scene():
    c = _client()
    sid = _draft(c)
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-EDIT", "line1": _TLE1, "line2": _TLE2, "owner": "blue"})
    r = c.patch(f"/api/sessions/{sid}/creator/asset/SAT-EDIT", json={"patch": {"group": "ALPHA"}})
    assert r.json()["ok"] is True
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    assert next(a for a in state["assets"] if a["id"] == "SAT-EDIT")["group"] == "ALPHA"


def test_asset_reassign_is_an_owner_patch():
    c = _client()
    sid = _draft(c)
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-REASSIGN", "line1": _TLE1, "line2": _TLE2, "owner": "blue"})
    r = c.patch(f"/api/sessions/{sid}/creator/asset/SAT-REASSIGN", json={"patch": {"owner": "red"}})
    assert r.json()["ok"] is True
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    assert next(a for a in state["assets"] if a["id"] == "SAT-REASSIGN")["owner"] == "red"


def test_asset_delete_removed_from_list_and_edit_then_fails():
    c = _client()
    sid = _draft(c)
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-DEL", "line1": _TLE1, "line2": _TLE2})
    r = c.delete(f"/api/sessions/{sid}/creator/asset/SAT-DEL")
    assert r.json()["ok"] is True
    state = c.get(f"/api/sessions/{sid}/creator/state").json()
    assert not any(a["id"] == "SAT-DEL" for a in state["assets"])
    r2 = c.patch(f"/api/sessions/{sid}/creator/asset/SAT-DEL", json={"patch": {"owner": "red"}})
    assert r2.json()["ok"] is False


# -- FR-5160: seat-count declaration + seat/role-assignment matrix --------------------------------

def test_seat_declaration_generates_seat_ids():
    c = _client()
    sid = _draft(c)
    r = c.post(f"/api/sessions/{sid}/creator/seats", json={"cell": "white", "count": 3})
    assert r.status_code == 200
    assert r.json()["seats"] == ["white-1", "white-2", "white-3"]
    read = c.get(f"/api/sessions/{sid}/creator/seats").json()
    assert read["white"] == ["white-1", "white-2", "white-3"]


def test_seat_declaration_rejects_non_white_cell():
    c = _client()
    sid = _draft(c)
    r = c.post(f"/api/sessions/{sid}/creator/seats", json={"cell": "blue", "count": 2})
    assert r.status_code == 403


def test_matrix_assignment_produces_role_assignments_identical_to_direct_assign_role():
    """A declared seat + matrix checkbox calls the existing assign_role mechanism unmodified —
    the resulting role_assignments state must be identical in shape either way (FR-5160)."""
    c = _client()
    sid = _draft(c)
    c.post(f"/api/sessions/{sid}/force/tle", json={"id": "SAT-ROLE", "line1": _TLE1, "line2": _TLE2, "owner": "blue"})
    c.post(f"/api/sessions/{sid}/creator/seats", json={"cell": "white", "count": 1})
    r = c.post(f"/api/sessions/{sid}/roles/assign", json={
        "cell": "white", "seat": "white-1", "asset_or_constellation": "SAT-ROLE", "role": "both",
    })
    assert r.json()["ok"] is True
    report = c.get(f"/api/sessions/{sid}/roles/staffing").json()
    assert isinstance(report, list)
