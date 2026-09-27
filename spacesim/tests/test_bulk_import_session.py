"""IP-1190 (FR-5220) — SessionManager.bulk_import()'s per-object report shape and gating."""
from __future__ import annotations

from spacesim.session import InProcessSession

_TLE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
_TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"


def _unstarted():
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    return api, sid


def _nine_valid_one_malformed_tle_text() -> str:
    lines = []
    for n in range(9):
        lines.append(f"SAT-{n}")
        lines.append(_TLE1)
        lines.append(_TLE2)
    lines.append("SAT-BAD")
    lines.append(_TLE1)
    lines.append("2 too short")
    return "\n".join(lines)


def _assignments_for(n_valid: int, bad_name: str) -> dict[str, dict]:
    assignments = {f"SAT-{i}": {"asset_id": f"BULK-{i}", "owner": "blue"} for i in range(n_valid)}
    assignments[bad_name] = {"asset_id": "BULK-BAD", "owner": "blue"}
    return assignments


def test_bulk_import_tle_nine_valid_one_malformed_no_exception():
    api, sid = _unstarted()
    mgr = api._sessions[sid]
    reports = mgr.bulk_import("tle", _nine_valid_one_malformed_tle_text(),
                               _assignments_for(9, "SAT-BAD"))
    assert len(reports) == 10
    oks = [r for r in reports if r["ok"]]
    fails = [r for r in reports if not r["ok"]]
    assert len(oks) == 9
    assert len(fails) == 1
    assert fails[0]["raw_id"] == "SAT-BAD"
    for i in range(9):
        assert f"BULK-{i}" in mgr.world.assets
    assert "BULK-BAD" not in mgr.world.assets


_OMM_NINE_PLUS_ONE = "\n".join(
    [
        "CCSDS_OMM_VERS = 2.0",
    ] + [
        part
        for n in range(9)
        for part in (
            "META_START",
            f"OBJECT_NAME = OMM-{n}",
            "META_STOP",
            "EPOCH = 2024-001T00:00:00",
            "SEMI_MAJOR_AXIS = 6928.0",
            "ECCENTRICITY = 0.001",
            "INCLINATION = 51.6",
            "RA_OF_ASC_NODE = 100.0",
            "ARG_OF_PERICENTER = 50.0",
            "MEAN_ANOMALY = 10.0",
        )
    ] + [
        "META_START",
        "OBJECT_NAME = OMM-BAD",
        "META_STOP",
        "EPOCH = 2024-001T00:00:00",
        "SEMI_MAJOR_AXIS = 6928.0",
        # ECCENTRICITY deliberately missing -> a per-object failure.
        "INCLINATION = 51.6",
        "RA_OF_ASC_NODE = 100.0",
        "ARG_OF_PERICENTER = 50.0",
        "MEAN_ANOMALY = 10.0",
    ]
)


def test_bulk_import_omm_nine_valid_one_malformed_no_exception():
    api, sid = _unstarted()
    mgr = api._sessions[sid]
    assignments = {f"OMM-{i}": {"asset_id": f"OMMBULK-{i}", "owner": "red"} for i in range(9)}
    assignments["OMM-BAD"] = {"asset_id": "OMMBULK-BAD", "owner": "red"}
    reports = mgr.bulk_import("omm", _OMM_NINE_PLUS_ONE, assignments)
    assert len(reports) == 10
    oks = [r for r in reports if r["ok"]]
    fails = [r for r in reports if not r["ok"]]
    assert len(oks) == 9
    assert len(fails) == 1
    assert fails[0]["raw_id"] == "OMM-BAD"
    for i in range(9):
        assert f"OMMBULK-{i}" in mgr.world.assets


def test_bulk_import_unrecognizable_file_raises():
    api, sid = _unstarted()
    mgr = api._sessions[sid]
    try:
        mgr.bulk_import("tle", "not a tle file at all\njust text\n", {})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_bulk_import_object_missing_assignment_reported_as_failure_not_dropped():
    api, sid = _unstarted()
    mgr = api._sessions[sid]
    text = "\n".join(["SAT-X", _TLE1, _TLE2])
    reports = mgr.bulk_import("tle", text, {})
    assert len(reports) == 1
    assert reports[0]["ok"] is False
    assert reports[0]["raw_id"] == "SAT-X"
    assert "no side/template assignment" in reports[0]["reason"]


def test_bulk_import_against_started_session_returns_empty_no_assets_added():
    api, sid = _unstarted()
    mgr = api._sessions[sid]
    api.start(sid)
    text = "\n".join(["SAT-X", _TLE1, _TLE2])
    reports = mgr.bulk_import("tle", text, {"SAT-X": {"asset_id": "SAT-X"}})
    assert reports == []
    assert "SAT-X" not in mgr.world.assets
