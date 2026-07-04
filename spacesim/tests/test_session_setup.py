"""IP-1151 — Session Setup: Seat-to-Role Assignment (FS-115, FR-4210 slice).

White Cell binds seats to {asset_or_constellation, role} against a vignette's declared
roles_needed; an unmet mandatory entry hard-blocks exercise start. A vignette declaring nothing
(all 19 existing vignettes) must never be blocked by this mechanism.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.content.vignette import Vignette, load_vignette
from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import SessionManager
from spacesim.ui_web.server import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def _vignette_with_roles(roles_needed: list[dict]) -> Vignette:
    raw = {
        "id": "test-roles",
        "title": "Role test",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [{"id": "ISR-EO-1", "kind": "satellite", "orbit": {
            "epoch": 1893456000000000, "semi_major_axis_m": 6_778_000.0, "eccentricity": 0.0,
            "inclination_deg": 51.6, "raan_deg": 0.0, "arg_perigee_deg": 0.0, "true_anomaly_deg": 0.0,
        }}],
        "red_forces": [], "neutral_forces": [], "sensors": [],
        "roles_needed": roles_needed,
    }
    return Vignette.model_validate(raw)


# -- content/vignette.py schema ------------------------------------------------------------------

def test_roles_needed_defaults_to_empty_on_existing_vignettes():
    """All 19 existing vignette YAML files declare no roles_needed — this must default cleanly,
    not error, per Implementation Task 1's explicit backward-compatibility requirement."""
    vig = load_vignette("leo-isr-denial")
    assert vig.roles_needed == []


# -- session/manager.py registry + staffing gate -------------------------------------------------

def test_staffing_report_empty_and_start_unblocked_with_no_roles_needed():
    vig = _vignette_with_roles([])
    mgr = SessionManager(vig, seed=1)
    assert mgr.staffing_report() == []


def test_mandatory_unassigned_role_is_reported_unsatisfied():
    vig = _vignette_with_roles([
        {"asset_or_constellation": "ISR-EO-1", "role": "bus", "mandatory": True},
    ])
    mgr = SessionManager(vig, seed=1)
    report = mgr.staffing_report()
    assert len(report) == 1
    assert report[0]["asset_or_constellation"] == "ISR-EO-1" and report[0]["role"] == "bus"


def test_optional_unassigned_role_is_never_reported():
    vig = _vignette_with_roles([
        {"asset_or_constellation": "ISR-EO-1", "role": "bus", "mandatory": False},
    ])
    mgr = SessionManager(vig, seed=1)
    assert mgr.staffing_report() == []


def test_assigning_the_exact_role_satisfies_the_requirement():
    vig = _vignette_with_roles([
        {"asset_or_constellation": "ISR-EO-1", "role": "bus", "mandatory": True},
    ])
    mgr = SessionManager(vig, seed=1)
    mgr.assign_role("blue-bus-op", "ISR-EO-1", "bus")
    assert mgr.staffing_report() == []


def test_a_both_assignment_satisfies_either_a_bus_or_payload_requirement():
    vig = _vignette_with_roles([
        {"asset_or_constellation": "ISR-EO-1", "role": "payload", "mandatory": True},
    ])
    mgr = SessionManager(vig, seed=1)
    mgr.assign_role("blue-combined-op", "ISR-EO-1", "both")
    assert mgr.staffing_report() == []


def test_a_bus_only_assignment_does_not_satisfy_a_payload_requirement():
    vig = _vignette_with_roles([
        {"asset_or_constellation": "ISR-EO-1", "role": "payload", "mandatory": True},
    ])
    mgr = SessionManager(vig, seed=1)
    mgr.assign_role("blue-bus-op", "ISR-EO-1", "bus")
    assert len(mgr.staffing_report()) == 1


# -- InProcessSession / HTTP: the actual hard gate on Start --------------------------------------

def test_start_refused_with_unmet_mandatory_role_via_api():
    api = InProcessSession()
    vig = _vignette_with_roles([{"asset_or_constellation": "ISR-EO-1", "role": "bus", "mandatory": True}])
    api._sessions["sess-test"] = SessionManager(vig, seed=1)
    api._counter = 1
    ack = api.start("sess-test")
    assert ack.ok is False and "ISR-EO-1" in ack.reason
    assert api._sessions["sess-test"].started is False


def test_start_succeeds_once_the_mandatory_role_is_assigned():
    api = InProcessSession()
    vig = _vignette_with_roles([{"asset_or_constellation": "ISR-EO-1", "role": "bus", "mandatory": True}])
    api._sessions["sess-test"] = SessionManager(vig, seed=1)
    api.assign_role("sess-test", "white", "blue-bus-op", "ISR-EO-1", "bus")
    ack = api.start("sess-test")
    assert ack.ok is True
    assert api._sessions["sess-test"].started is True


def test_only_white_cell_can_assign_roles():
    api = InProcessSession()
    vig = _vignette_with_roles([{"asset_or_constellation": "ISR-EO-1", "role": "bus", "mandatory": True}])
    api._sessions["sess-test"] = SessionManager(vig, seed=1)
    ack = api.assign_role("sess-test", "blue", "blue-bus-op", "ISR-EO-1", "bus")
    assert ack.ok is False
    assert api._sessions["sess-test"].staffing_report()   # unchanged — assignment had no effect


def test_existing_vignette_starts_without_any_role_assignment():
    """All 19 shipped vignettes declare no roles_needed — Start must never be blocked for them."""
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    ack = api.start(sid)
    assert ack.ok is True


def test_staffing_report_and_assign_endpoints_over_http():
    c = _client()
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    assert c.get(f"/api/sessions/{sid}/roles/staffing").json() == []
    ack = c.post(f"/api/sessions/{sid}/roles/assign", json={
        "cell": "white", "seat": "blue-bus-op", "asset_or_constellation": "ISR-EO-1", "role": "bus",
    }).json()
    assert ack["ok"] is True
