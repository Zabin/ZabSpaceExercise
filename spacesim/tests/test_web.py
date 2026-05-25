"""Phase 5: the FastAPI layer over the SessionAPI (fog enforced server-side, full flow headless).

We can't click the browser UI here, so these tests drive the same endpoints the front end calls
and assert the backend supports the whole Vignette-1 flow with fog-of-war applied at the boundary.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.ui_web.server import create_app  # noqa: E402


def _client() -> TestClient:
    return TestClient(create_app())


def _new_session(c: TestClient) -> str:
    assert any(v["id"] == "leo-isr-denial" for v in c.get("/api/vignettes").json())
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    return sid


def test_static_index_is_served():
    c = _client()
    r = c.get("/")
    assert r.status_code == 200 and "Exercise Simulator" in r.text


def test_unknown_session_is_404():
    c = _client()
    assert c.get("/api/sessions/nope/view/blue").status_code == 404


def test_fog_of_war_applied_server_side():
    c = _client()
    sid = _new_session(c)
    red = c.get(f"/api/sessions/{sid}/view/red").json()
    blue = c.get(f"/api/sessions/{sid}/view/blue").json()
    red_ids = {a["id"] for a in red["own_assets"]}
    blue_ids = {a["id"] for a in blue["own_assets"]}
    assert "ISR-EO-1" in blue_ids and "ISR-EO-1" not in red_ids
    assert "ISR-EO-1" not in c.get(f"/api/sessions/{sid}/view/red").text  # nothing leaks
    # White god-view sees both sides.
    god = c.get(f"/api/sessions/{sid}/godview").json()
    assert {"ISR-EO-1", "JAM-NORTH"} <= set(god["assets"].keys())


def test_full_flow_order_advance_objectives_and_rewind():
    c = _client()
    sid = _new_session(c)
    start = c.get(f"/api/sessions/{sid}/godview").json()["now"]

    ack = c.post(f"/api/sessions/{sid}/order", json={
        "cell": "blue", "actor": "ISR-EO-1", "action": "downlink", "params": {"via": "GS-NORTH"}}).json()
    assert ack["ok"] and ack["status"] == "queued" and ack["earliest_window"] is not None

    c.post(f"/api/sessions/{sid}/advance", json={"t": start + 800 * 1_000_000})
    objs = c.get(f"/api/sessions/{sid}/objectives").json()
    assert objs["blue"]["deliver_isr"] is True

    # Rewind clears the delivery (exact replay-based rewind through the API).
    c.post(f"/api/sessions/{sid}/rewind", json={"t": 0})
    assert c.get(f"/api/sessions/{sid}/objectives").json()["blue"]["deliver_isr"] is False


def test_rejected_order_returns_reason():
    c = _client()
    sid = _new_session(c)
    # Engage with no weapons-quality track + kinetic ROE off → rejected with a human reason.
    ack = c.post(f"/api/sessions/{sid}/order", json={
        "cell": "red", "actor": "RED-ASAT", "action": "engage", "target": "ISR-EO-1"}).json()
    assert ack["ok"] is False and ack["reason"]


def test_inject_reveals_track_to_blue_over_api():
    c = _client()
    sid = _new_session(c)
    assert c.get(f"/api/sessions/{sid}/view/blue").json()["known_tracks"] == []
    c.post(f"/api/sessions/{sid}/inject", json={"inject": "commercial_imagery_leak"})
    tracks = c.get(f"/api/sessions/{sid}/view/blue").json()["known_tracks"]
    assert any(t["object"] == "RED-SURF" for t in tracks)
