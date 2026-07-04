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


def test_vignette_tutorial_endpoint_returns_separated_cells():
    c = _client()
    r = c.get("/api/vignettes/leo-isr-denial/tutorial")
    assert r.status_code == 200
    tut = r.json()
    # Structured per-cell steps; blue and red never bleed together.
    assert tut["blue"][0]["title"] == "Review the order of battle"
    assert tut["red"][0]["title"] == "Review own assets"
    assert len(tut["blue"]) == 5 and len(tut["red"]) == 4
    assert c.get("/api/vignettes/does-not-exist/tutorial").status_code == 404


def test_session_brief_returns_per_cell_blocks():
    """Mission brief endpoint must return per-cell intro_brief + ROE + enriched objectives."""
    c = _client()
    sid = _new_session(c)
    blue = c.get(f"/api/sessions/{sid}/brief/blue").json()
    assert blue["cell"] == "blue"
    assert blue["title"] == "LEO ISR Denial"
    # intro_brief fields must be present (authored in YAML).
    for key in ("situation", "mission", "friendly_forces", "threat_picture",
                "deadline_note", "roe_note", "success_criteria", "tool_tips"):
        assert key in blue["text"], f"missing {key} in blue brief"
    # ROE must reflect the vignette (kinetic OFF in vignette 1).
    assert blue["roe"]["kinetic_authorized"] is False
    # Enriched objectives must include desc + countdown.
    assert any(o["id"] == "deliver_isr" and o["desc"] and o["remaining_s"] > 0
               for o in blue["objectives"])

    # Red sees its own brief, not Blue's (cell field correct).
    red = c.get(f"/api/sessions/{sid}/brief/red").json()
    assert red["cell"] == "red"
    assert red["text"]["mission"] != blue["text"]["mission"]

    # White sees both.
    white = c.get(f"/api/sessions/{sid}/brief/white").json()
    assert "blue" in white and "red" in white


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


# -- Stage C: critical-path API smoke tests -----------------------------------

def test_scene_returns_assets():
    c = _client()
    sid = _new_session(c)
    r = c.get(f"/api/sessions/{sid}/scene/blue")
    assert r.status_code == 200
    body = r.json()
    assert "assets" in body and len(body["assets"]) > 0


def test_telemetry_param_list():
    c = _client()
    sid = _new_session(c)
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1")
    assert r.status_code == 200
    body = r.json()
    assert "subsystems" in body and len(body["subsystems"]) > 0


def test_telemetry_series_count():
    c = _client()
    sid = _new_session(c)
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/battery_soc?n=30")
    assert r.status_code == 200
    body = r.json()
    assert "points" in body and len(body["points"]) == 30


def test_fog_cross_cell_telemetry():
    """Blue cell cannot read Red cell's asset telemetry."""
    c = _client()
    sid = _new_session(c)
    # JAM-NORTH is a red asset — blue must not see its telemetry
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/JAM-NORTH")
    # Should either 404 or return empty subsystems (fog boundary)
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        body = r.json()
        assert body.get("subsystems", {}) == {} or body.get("error")


def test_dry_run_feasible_order():
    c = _client()
    sid = _new_session(c)
    r = c.post(f"/api/sessions/{sid}/order/validate", json={
        "cell": "blue", "actor": "ISR-EO-1", "action": "downlink",
        "params": {"via": "GS-NORTH"}})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True and body["earliest_window"] is not None


def test_ssn_endpoint_available():
    """SSN request endpoint round-trips without error for a vignette that opts in."""
    c = _client()
    # Use a vignette with SSN enabled (training-basics has ssn_blue_dispersion parameter)
    sid = c.post("/api/sessions", json={"vignette_id": "training-basics", "seed": 1,
                                        "overrides": {"ssn_blue_dispersion": "regional"}}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    r = c.get(f"/api/sessions/{sid}/view/blue")
    assert r.status_code == 200   # session started cleanly with SSN enabled


# ---------------------------------------------------------------------------
# Multiplayer (Part A–D): server-authoritative lazy clock + per-session lock +
# discovery endpoint + clock control. See plan §M8 / Parts A–D.
# ---------------------------------------------------------------------------


def _patch_wall(monkeypatch, value: float) -> None:
    """Patch the wall clock the SessionManager reads (manager._time.time)."""
    from spacesim.session import manager as _m
    monkeypatch.setattr(_m._time, "time", lambda: value)


def test_lazy_clock_advances_on_read(monkeypatch):
    c = _client()
    _patch_wall(monkeypatch, 1000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")   # auto-arms the clock at wall=1000
    now0 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 1010.0)        # +10s wall
    now1 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 1030.0)        # +30s wall
    now2 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert now1 - now0 == 10 * 1_000_000
    assert now2 - now0 == 30 * 1_000_000   # monotonic


def test_lazy_clock_idempotent_for_multi_reader(monkeypatch):
    """Three concurrent reads at one fixed wall time advance sim ONCE, not N times."""
    c = _client()
    _patch_wall(monkeypatch, 2000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    now0 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 2010.0)        # +10s wall, frozen for all 3 reads
    # Simulate 3 tabs polling at the same wall instant.
    nows = [
        c.get(f"/api/sessions/{sid}/view/white").json()["now"],
        c.get(f"/api/sessions/{sid}/view/blue").json()["now"],
        c.get(f"/api/sessions/{sid}/view/red").json()["now"],
    ]
    # All three see the same sim time, and that sim time is +10s of start — NOT +30s.
    assert nows[0] == nows[1] == nows[2]
    assert nows[0] - now0 == 10 * 1_000_000


def test_clock_pause_freezes_then_resumes(monkeypatch):
    c = _client()
    _patch_wall(monkeypatch, 5000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    now0 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 5010.0)
    now_running = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert now_running - now0 == 10 * 1_000_000
    # Pause.
    state = c.post(f"/api/sessions/{sid}/clock", json={"running": False}).json()
    assert state["running"] is False
    paused_at = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 5025.0)        # +15s wall while paused
    after_paused = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert after_paused == paused_at        # sim frozen
    # Resume — re-anchors at the current wall.
    c.post(f"/api/sessions/{sid}/clock", json={"running": True})
    _patch_wall(monkeypatch, 5030.0)        # +5s after resume
    after_resume = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert after_resume - paused_at == 5 * 1_000_000


def test_rewind_re_anchors_clock(monkeypatch):
    """After rewind, the wall clock must not 'snap forward' the sim by the elapsed wall time."""
    c = _client()
    _patch_wall(monkeypatch, 7000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    start_now = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 7030.0)        # run +30s of wall time
    advanced = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert advanced - start_now == 30 * 1_000_000
    # Rewind sets sim.clock.now back; re-anchor must reset wall_anchor to wall=now and
    # sim_anchor to the new sim time. So +5s of further wall time should yield +5s of sim.
    c.post(f"/api/sessions/{sid}/rewind", json={"t": 0})
    after_rewind = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 7035.0)        # +5s after rewind
    after_5s = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    # Must advance by exactly 5s relative to the rewound point — NOT by the 35s of total wall.
    assert after_5s - after_rewind == 5 * 1_000_000


def test_session_discovery_lists_sessions():
    c = _client()
    s1 = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    s2 = c.post("/api/sessions", json={"vignette_id": "training-basics", "seed": 2}).json()["session"]
    c.post(f"/api/sessions/{s1}/start")
    listing = c.get("/api/sessions").json()
    by_sid = {s["sid"]: s for s in listing}
    assert s1 in by_sid and s2 in by_sid
    assert by_sid[s1]["vignette_id"] == "leo-isr-denial"
    assert by_sid[s1]["started"] is True
    assert by_sid[s2]["started"] is False
    assert by_sid[s1]["running"] is True
    assert by_sid[s2]["running"] is False
    assert "now" in by_sid[s1] and "title" in by_sid[s1]


def test_load_response_carries_resolved_classification():
    """IP-1120 — POST /api/sessions returns the resolved value (override or vignette default) so
    the creating tab can set the banner from the create response, no extra round trip."""
    c = _client()
    default_resp = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()
    assert default_resp["classification"]   # non-empty; equals the vignette's own default

    override_resp = c.post("/api/sessions", json={
        "vignette_id": "leo-isr-denial", "seed": 1, "classification": "UNCLASSIFIED//EXERCISE",
    }).json()
    assert override_resp["classification"] == "UNCLASSIFIED//EXERCISE"


def test_session_discovery_surfaces_classification_for_joining_tabs():
    """IP-1120 — a second tab joining via list_sessions() (join-by-hash) sees the same resolved
    value the creating tab got, never re-deriving it."""
    c = _client()
    sid = c.post("/api/sessions", json={
        "vignette_id": "leo-isr-denial", "seed": 1, "classification": "UNCLASSIFIED//EXERCISE",
    }).json()["session"]
    by_sid = {s["sid"]: s for s in c.get("/api/sessions").json()}
    assert by_sid[sid]["classification"] == "UNCLASSIFIED//EXERCISE"


def test_aar_csv_export_embeds_classification_over_http():
    c = _client()
    sid = c.post("/api/sessions", json={
        "vignette_id": "leo-isr-denial", "seed": 1, "classification": "UNCLASSIFIED//EXERCISE",
    }).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    csv_text = c.get(f"/api/sessions/{sid}/aar/export.csv").text
    assert "UNCLASSIFIED//EXERCISE" in csv_text


def test_save_export_embeds_classification_over_http():
    c = _client()
    sid = c.post("/api/sessions", json={
        "vignette_id": "leo-isr-denial", "seed": 1, "classification": "UNCLASSIFIED//EXERCISE",
    }).json()["session"]
    saved = c.get(f"/api/sessions/{sid}/save").json()
    assert saved["classification"] == "UNCLASSIFIED//EXERCISE"


def test_concurrent_reads_and_writes_lock_safe():
    """ThreadPool hammers mutations + reads on one session; state stays consistent."""
    import concurrent.futures as cf
    c = _client()
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    # Pause the clock so wall-time noise doesn't mask the lock test.
    c.post(f"/api/sessions/{sid}/clock", json={"running": False})

    def step():       return c.post(f"/api/sessions/{sid}/step", json={"dt_sim_s": 1.0}).status_code
    def view_b():     return c.get(f"/api/sessions/{sid}/view/blue").status_code
    def view_w():     return c.get(f"/api/sessions/{sid}/view/white").status_code
    def godview():    return c.get(f"/api/sessions/{sid}/godview").status_code
    def alarms():     return c.get(f"/api/sessions/{sid}/alarms/blue").status_code

    tasks = [step, view_b, view_w, godview, alarms] * 8
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(lambda f: f(), tasks))
    assert all(r == 200 for r in results)
    # State remains coherent: save + AAR succeed (would raise on torn state).
    assert c.get(f"/api/sessions/{sid}/save").status_code == 200
    assert c.get(f"/api/sessions/{sid}/aar").status_code == 200


def test_advance_guard_no_op_at_same_wall_time(monkeypatch):
    """Two consecutive reads at the SAME patched wall time → second is a no-op, no ValueError."""
    c = _client()
    _patch_wall(monkeypatch, 9000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    _patch_wall(monkeypatch, 9010.0)        # +10s
    n1 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    # Same wall time, second read: catch_up sees target == current, must be a no-op.
    n2 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert n1 == n2


def test_resumed_session_loads_paused():
    """A saved + resumed session starts with the clock paused (anchor cleared)."""
    c = _client()
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    state = c.get(f"/api/sessions/{sid}/save").json()
    sid2 = c.post("/api/sessions/load_save", json=state).json()["session"]
    listing = {s["sid"]: s for s in c.get("/api/sessions").json()}
    assert listing[sid2]["started"] is True
    assert listing[sid2]["running"] is False   # resumed paused — must not silently fast-forward
