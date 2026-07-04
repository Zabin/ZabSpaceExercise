"""IP-1130 — Observer Read-Only Access: a White-Cell-designated read-only seat whose every
mutating request is rejected server-side, independent of what the UI offers (FS-113, FR-6510).
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.ui_web.server import create_app  # noqa: E402


def _client() -> TestClient:
    return TestClient(create_app())


def _new_session(c: TestClient) -> str:
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    return sid


def _new_unstarted_session(c: TestClient) -> str:
    """Not started — the server-authoritative real-time clock only advances once a session is
    started, so two reads taken here are exact-snapshot comparable (no `now` drift between calls)."""
    return c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]


def test_observer_view_defaults_to_godview():
    c = _client()
    sid = _new_unstarted_session(c)
    god = c.get(f"/api/sessions/{sid}/godview").json()
    obs = c.get(f"/api/sessions/{sid}/observer/view").json()
    assert obs == god


def test_white_can_designate_observer_view_to_a_cell():
    c = _client()
    sid = _new_unstarted_session(c)
    ack = c.post(f"/api/sessions/{sid}/observer/view", json={"cell": "white", "designation": "blue"}).json()
    assert ack["ok"] is True

    blue_view = c.get(f"/api/sessions/{sid}/view/blue").json()
    obs_view = c.get(f"/api/sessions/{sid}/observer/view").json()
    assert obs_view == blue_view   # byte-for-byte identical to what Blue's own operator would see


def test_observer_designation_endpoint_lets_client_reuse_the_same_view_endpoints():
    """app.js's refresh() fetches this, then calls /godview or /view/{designation} directly —
    the same call every other seat already makes, no merged-shape parsing needed client-side."""
    c = _client()
    sid = _new_unstarted_session(c)
    assert c.get(f"/api/sessions/{sid}/observer/designation").json() == {"designation": "godview"}
    c.post(f"/api/sessions/{sid}/observer/view", json={"cell": "white", "designation": "red"})
    assert c.get(f"/api/sessions/{sid}/observer/designation").json() == {"designation": "red"}


def test_non_white_cannot_designate_observer_view():
    c = _client()
    sid = _new_unstarted_session(c)
    ack = c.post(f"/api/sessions/{sid}/observer/view", json={"cell": "blue", "designation": "red"}).json()
    assert ack["ok"] is False
    # Designation is unchanged (still defaults to godview) — the rejected request had no effect.
    god = c.get(f"/api/sessions/{sid}/godview").json()
    obs = c.get(f"/api/sessions/{sid}/observer/view").json()
    assert obs == god


# -- Every mutating route rejects an Observer-seated caller (FS-113 Acceptance Criteria #2) -----
# Re-derived from the live route table (ui_web/server.py) at test-authoring time per IP-1130's own
# Risks section ("re-derived... not copied from this document's Files to Modify list which may
# drift") — not merely the package's own enumerated list, which is a subset of this one
# (notably missing /preview/consequence).

_MUTATING_ROUTES = [
    # (method, path template, kwargs for the request — "cell" already set to "observer" where needed)
    ("post", "/api/sessions/{sid}/clock", {"json": {"running": True}, "params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/param", {"json": {"param_id": "red_kinetic_authorized", "value": True}, "params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/start", {"params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/step", {"json": {"dt_sim_s": 60.0}, "params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/advance", {"json": {"t": 10**15}, "params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/rewind", {"json": {"t": 0}, "params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/undo", {"json": {"n": 1}, "params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/inject", {"json": {"inject": "commercial_imagery_leak"}, "params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/force/tle", {"json": {"id": "X-1", "line1": "1 x", "line2": "2 x"}, "params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/red_step", {"params": {"cell": "observer"}}),
    ("post", "/api/sessions/{sid}/order", {"json": {"cell": "observer", "actor": "ISR-EO-1", "action": "downlink", "params": {"via": "GS-NORTH"}}}),
    ("post", "/api/sessions/{sid}/order/validate", {"json": {"cell": "observer", "actor": "ISR-EO-1", "action": "downlink", "params": {"via": "GS-NORTH"}}}),
    ("post", "/api/sessions/{sid}/maneuver/compute", {"json": {"cell": "observer", "actor": "ISR-EO-1", "mode": "eci", "params": {}}}),
    ("post", "/api/sessions/{sid}/jam/compute", {"json": {"cell": "observer", "actor": "ISR-EO-1", "params": {}}}),
    ("post", "/api/sessions/{sid}/engage/compute", {"json": {"cell": "observer", "actor": "ISR-EO-1", "target": "X", "params": {}}}),
    ("post", "/api/sessions/{sid}/cyber/compute", {"json": {"cell": "observer", "actor": "ISR-EO-1", "target": "X", "params": {}}}),
    ("post", "/api/sessions/{sid}/sigint/compute", {"json": {"cell": "observer", "actor": "ISR-EO-1", "params": {}}}),
    ("post", "/api/sessions/{sid}/preview/consequence", {"json": {"cell": "observer", "actor": "ISR-EO-1", "action": "downlink", "params": {}}}),
    ("post", "/api/sessions/{sid}/cancel", {"json": {"cell": "observer", "order_id": "ord-1"}}),
    ("post", "/api/sessions/{sid}/recovery/observer/ISR-EO-1", {"json": {"via": "GS-NORTH"}}),
    ("post", "/api/sessions/{sid}/ssn/observer/request", {"json": {"intent": "track", "target": "X", "regime": "LEO"}}),
    ("post", "/api/sessions/{sid}/ssn/observer/cancel", {"json": {"request_id": "req-1"}}),
]


@pytest.mark.parametrize("method,path,kwargs", _MUTATING_ROUTES,
                         ids=[p for _, p, _ in _MUTATING_ROUTES])
def test_every_mutating_route_rejects_observer(method, path, kwargs):
    c = _client()
    sid = _new_session(c)
    # Compare eventlog length, not a full godview snapshot — the session is started, so its
    # server-authoritative real-time clock advances `now` on every read regardless of whether a
    # guarded route did anything; the eventlog only grows when an actual event is applied.
    before = len(c.get(f"/api/sessions/{sid}/eventlog").json())

    resp = getattr(c, method)(path.format(sid=sid), **kwargs)
    assert resp.status_code == 403, f"{path} did not reject an Observer-seated request"

    after = len(c.get(f"/api/sessions/{sid}/eventlog").json())
    assert after == before   # no WorldState change occurred


def test_observer_rejection_holds_even_calling_the_route_directly_bypassing_any_ui():
    """The parametrized test above already calls raw HTTP routes with no JS/UI involved at all —
    this test just makes that property explicit for a representative sample, per FS-113's own
    Security Considerations ("must hold even against a request that bypasses the UI entirely")."""
    c = _client()
    sid = _new_session(c)
    resp = c.post(f"/api/sessions/{sid}/order", json={
        "cell": "observer", "actor": "ISR-EO-1", "action": "downlink", "params": {"via": "GS-NORTH"},
    })
    assert resp.status_code == 403


def test_non_observer_seats_still_work_normally():
    """The guard must reject Observer specifically, not accidentally break White/Blue/Red."""
    c = _client()
    sid = _new_session(c)
    resp = c.post(f"/api/sessions/{sid}/order", json={
        "cell": "blue", "actor": "ISR-EO-1", "action": "downlink", "params": {"via": "GS-NORTH"},
    })
    assert resp.status_code == 200 and resp.json()["ok"] is True
