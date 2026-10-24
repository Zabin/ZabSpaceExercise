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
    c.post(f"/api/sessions/{sid}/start?cell=white")
    return sid


@pytest.mark.verifies("FR-8110")
def test_static_index_is_served():
    c = _client()
    r = c.get("/")
    assert r.status_code == 200 and "Exercise Simulator" in r.text


@pytest.mark.verifies("NFR-1600")
def test_unknown_session_is_404():
    c = _client()
    assert c.get("/api/sessions/nope/view/blue").status_code == 404


@pytest.mark.verifies("NFR-3400")
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


@pytest.mark.verifies("FS-115")
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


@pytest.mark.verifies("FR-6210")
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


@pytest.mark.verifies("FR-3110")
def test_full_flow_order_advance_objectives_and_rewind():
    c = _client()
    sid = _new_session(c)
    start = c.get(f"/api/sessions/{sid}/godview").json()["now"]

    ack = c.post(f"/api/sessions/{sid}/order", json={
        "cell": "blue", "actor": "ISR-EO-1", "action": "downlink", "params": {"via": "GS-NORTH"}}).json()
    assert ack["ok"] and ack["status"] == "queued" and ack["earliest_window"] is not None

    c.post(f"/api/sessions/{sid}/advance?cell=white", json={"t": start + 800 * 1_000_000})
    objs = c.get(f"/api/sessions/{sid}/objectives").json()
    assert objs["blue"]["deliver_isr"] is True

    # Rewind clears the delivery (exact replay-based rewind through the API).
    c.post(f"/api/sessions/{sid}/rewind?cell=white", json={"t": start})
    assert c.get(f"/api/sessions/{sid}/objectives").json()["blue"]["deliver_isr"] is False


@pytest.mark.verifies("NFR-3020")
def test_rejected_order_returns_reason():
    c = _client()
    sid = _new_session(c)
    # Engage with no weapons-quality track + kinetic ROE off → rejected with a human reason.
    ack = c.post(f"/api/sessions/{sid}/order", json={
        "cell": "red", "actor": "RED-ASAT", "action": "engage", "target": "ISR-EO-1"}).json()
    assert ack["ok"] is False and ack["reason"]


@pytest.mark.verifies("FR-4410")
def test_inject_reveals_track_to_blue_over_api():
    c = _client()
    sid = _new_session(c)
    assert c.get(f"/api/sessions/{sid}/view/blue").json()["known_tracks"] == []
    c.post(f"/api/sessions/{sid}/inject?cell=white", json={"inject": "commercial_imagery_leak"})
    tracks = c.get(f"/api/sessions/{sid}/view/blue").json()["known_tracks"]
    assert any(t["object"] == "RED-SURF" for t in tracks)


# -- Stage C: critical-path API smoke tests -----------------------------------

@pytest.mark.verifies("FR-8110")
def test_scene_returns_assets():
    c = _client()
    sid = _new_session(c)
    r = c.get(f"/api/sessions/{sid}/scene/blue")
    assert r.status_code == 200
    body = r.json()
    assert "assets" in body and len(body["assets"]) > 0


@pytest.mark.verifies("FR-2110")
def test_telemetry_param_list():
    c = _client()
    sid = _new_session(c)
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1")
    assert r.status_code == 200
    body = r.json()
    assert "subsystems" in body and len(body["subsystems"]) > 0


@pytest.mark.verifies("FR-2310")
def test_telemetry_series_count():
    c = _client()
    sid = _new_session(c)
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/battery_soc?n=30")
    assert r.status_code == 200
    body = r.json()
    assert "points" in body and len(body["points"]) == 30


@pytest.mark.verifies("FR-2320")
def test_telemetry_series_route_matches_export_csv():
    """IP-1261 (BL-0170 scenario D, FR-2320 parity) — the live series route and the CSV export
    report the same value/status at every instant both sample; an anomaly is not back-dated."""
    import csv, io
    c = _client()
    sid = _new_session(c)
    c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": False})
    start = c.get(f"/api/sessions/{sid}/clock").json()["now"]
    c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 600})
    c.post(f"/api/sessions/{sid}/inject?cell=white", json={"inject": {"effects": [
        {"type": "anomaly", "target": "ISR-EO-1", "subsystem": "bus", "cause": "route test"}]}})
    c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 600})
    t1 = start + 1200 * 10**6
    series = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/snr_db",
                   params={"t0": start, "t1": t1, "n": 5}).json()["points"]
    csv_r = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/export.csv",
                  params={"t1": start, "t2": t1, "interval_s": 300})
    exported = {int(r["t"]): r for r in csv.DictReader(io.StringIO(csv_r.text)) if r["param"] == "snr_db"}
    assert [p["t"] for p in series] == sorted(exported)
    for p in series:
        assert p["value"] == pytest.approx(float(exported[p["t"]]["value"]))
        assert p["status"] == exported[p["t"]]["status"]
    assert all(p["status"] == "green" for p in series if p["t"] < start + 600 * 10**6)


@pytest.mark.verifies("FR-1320", "FR-6210")
def test_maneuver_ledger_route_and_csv_export_are_fog_scoped():
    """IP-1250 (FR-1320) — the ledger route/CSV export mirror /telemetry's fog-of-war behavior:
    an operator cannot fetch another cell's Asset ledger."""
    c = _client()
    sid = _new_session(c)
    r = c.post(f"/api/sessions/{sid}/order", json={
        "cell": "blue", "actor": "ISR-EO-1", "action": "maneuver",
        "params": {"dv": [5.0, 0.0, 0.0], "via": "GS-NORTH", "purpose_tag": "test-tag"}})
    assert r.json()["ok"], r.json()
    win = r.json()["earliest_window"]
    c.post(f"/api/sessions/{sid}/advance?cell=white", json={"t": win[0] + 1})

    ledger = c.get(f"/api/sessions/{sid}/maneuver_ledger/blue/ISR-EO-1")
    assert ledger.status_code == 200
    rows = ledger.json()
    assert len(rows) == 1 and rows[0]["purpose_tag"] == "test-tag"

    csv_r = c.get(f"/api/sessions/{sid}/maneuver_ledger/blue/ISR-EO-1/export.csv")
    assert csv_r.status_code == 200
    assert "test-tag" in csv_r.text

    denied = c.get(f"/api/sessions/{sid}/maneuver_ledger/red/ISR-EO-1")
    assert denied.status_code == 404


@pytest.mark.verifies("FR-2320")
def test_telemetry_export_csv_route_is_cell_scoped_like_telemetry():
    """IP-1260 (FR-2320) — /telemetry/{cell}/{asset}/export.csv mirrors /telemetry/{cell}/{asset}'s
    fog-of-war scoping (own assets only, White sees any; 404 otherwise), serializes CSV, clamps a
    partially out-of-range span and rejects a wholly out-of-range one (400)."""
    import csv, io
    c = _client()
    sid = _new_session(c)
    c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": False})
    c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 600})
    now = c.get(f"/api/sessions/{sid}/clock").json()["now"]

    span = {"t1": now - 600 * 10**6, "t2": now, "interval_s": 300}
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/export.csv", params=span)
    assert r.status_code == 200
    rows = list(csv.DictReader(io.StringIO(r.text)))
    assert list(rows[0]) == ["t", "utc", "asset", "subsystem", "param", "value", "unit", "status"]
    assert {row["asset"] for row in rows} == {"ISR-EO-1"}
    assert len({row["t"] for row in rows}) == 3 and int(rows[-1]["t"]) == now
    # The final sample's values equal the live JSON endpoint's reading at the same sim time.
    live = {p["id"]: p for sub in c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1").json()
            ["subsystems"].values() for p in sub}
    for row in rows:
        if int(row["t"]) == now:
            assert float(row["value"]) == pytest.approx(live[row["param"]]["value"])
            assert row["status"] == live[row["param"]]["status"]

    white = c.get(f"/api/sessions/{sid}/telemetry/white/ISR-EO-1/export.csv", params=span)
    assert white.status_code == 200 and white.text == r.text
    assert c.get(f"/api/sessions/{sid}/telemetry/red/ISR-EO-1/export.csv").status_code == 404
    assert c.get(f"/api/sessions/{sid}/telemetry/blue/JAM-NORTH/export.csv").status_code == 404

    clamped = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/export.csv",
                    params={"t1": now - 10**12, "t2": now + 10**9, "interval_s": 60})
    # A partially out-of-range span is clamped to the recorded range == the omitted-bounds default.
    full = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/export.csv", params={"interval_s": 60})
    assert clamped.status_code == 200 and full.status_code == 200 and clamped.text == full.text
    clamped_t = sorted({int(row["t"]) for row in csv.DictReader(io.StringIO(clamped.text))})
    assert clamped_t[-1] <= now and len(clamped_t) == 11
    out = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/export.csv",
                params={"t1": now + 10**9, "t2": now + 2 * 10**9})
    assert out.status_code == 400 and "wholly outside" in out.json()["detail"]
    # The /{param} series route is unaffected by the new sibling path.
    assert c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/snr_db?n=5").status_code == 200


@pytest.mark.verifies("FR-6210")
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


@pytest.mark.verifies("NFR-3020")
def test_dry_run_feasible_order():
    c = _client()
    sid = _new_session(c)
    r = c.post(f"/api/sessions/{sid}/order/validate", json={
        "cell": "blue", "actor": "ISR-EO-1", "action": "downlink",
        "params": {"via": "GS-NORTH"}})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True and body["earliest_window"] is not None


@pytest.mark.verifies("FR-3210")
def test_ssn_endpoint_available():
    """SSN request endpoint round-trips without error for a vignette that opts in."""
    c = _client()
    # Use a vignette with SSN enabled (training-basics has ssn_blue_dispersion parameter)
    sid = c.post("/api/sessions", json={"vignette_id": "training-basics", "seed": 1,
                                        "overrides": {"ssn_blue_dispersion": "regional"}}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
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


@pytest.mark.verifies("FR-6310")
def test_lazy_clock_advances_on_read(monkeypatch):
    c = _client()
    _patch_wall(monkeypatch, 1000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")   # auto-arms the clock at wall=1000
    now0 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 1010.0)        # +10s wall
    now1 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 1030.0)        # +30s wall
    now2 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert now1 - now0 == 10 * 1_000_000
    assert now2 - now0 == 30 * 1_000_000   # monotonic


@pytest.mark.verifies("FR-6310")
def test_lazy_clock_idempotent_for_multi_reader(monkeypatch):
    """Three concurrent reads at one fixed wall time advance sim ONCE, not N times."""
    c = _client()
    _patch_wall(monkeypatch, 2000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
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


@pytest.mark.verifies("FR-6310")
def test_clock_pause_freezes_then_resumes(monkeypatch):
    c = _client()
    _patch_wall(monkeypatch, 5000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    now0 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 5010.0)
    now_running = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert now_running - now0 == 10 * 1_000_000
    # Pause.
    state = c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": False}).json()
    assert state["running"] is False
    paused_at = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 5025.0)        # +15s wall while paused
    after_paused = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert after_paused == paused_at        # sim frozen
    # Resume — re-anchors at the current wall.
    c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": True})
    _patch_wall(monkeypatch, 5030.0)        # +5s after resume
    after_resume = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert after_resume - paused_at == 5 * 1_000_000


@pytest.mark.verifies("FR-6310")
def test_rewind_re_anchors_clock(monkeypatch):
    """After rewind, the wall clock must not 'snap forward' the sim by the elapsed wall time."""
    c = _client()
    _patch_wall(monkeypatch, 7000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    start_now = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 7030.0)        # run +30s of wall time
    advanced = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert advanced - start_now == 30 * 1_000_000
    # Rewind sets sim.clock.now back; re-anchor must reset wall_anchor to wall=now and
    # sim_anchor to the new sim time. So +5s of further wall time should yield +5s of sim.
    c.post(f"/api/sessions/{sid}/rewind?cell=white", json={"t": start_now})
    after_rewind = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    _patch_wall(monkeypatch, 7035.0)        # +5s after rewind
    after_5s = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    # Must advance by exactly 5s relative to the rewound point — NOT by the 35s of total wall.
    assert after_5s - after_rewind == 5 * 1_000_000


@pytest.mark.verifies("FR-6410")
def test_session_discovery_lists_sessions():
    c = _client()
    s1 = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    s2 = c.post("/api/sessions", json={"vignette_id": "training-basics", "seed": 2}).json()["session"]
    c.post(f"/api/sessions/{s1}/start?cell=white")
    listing = c.get("/api/sessions").json()
    by_sid = {s["sid"]: s for s in listing}
    assert s1 in by_sid and s2 in by_sid
    assert by_sid[s1]["vignette_id"] == "leo-isr-denial"
    assert by_sid[s1]["started"] is True
    assert by_sid[s2]["started"] is False
    assert by_sid[s1]["running"] is True
    assert by_sid[s2]["running"] is False
    assert "now" in by_sid[s1] and "title" in by_sid[s1]


@pytest.mark.verifies("FR-4510")
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


@pytest.mark.verifies("FR-4510")
def test_session_discovery_surfaces_classification_for_joining_tabs():
    """IP-1120 — a second tab joining via list_sessions() (join-by-hash) sees the same resolved
    value the creating tab got, never re-deriving it."""
    c = _client()
    sid = c.post("/api/sessions", json={
        "vignette_id": "leo-isr-denial", "seed": 1, "classification": "UNCLASSIFIED//EXERCISE",
    }).json()["session"]
    by_sid = {s["sid"]: s for s in c.get("/api/sessions").json()}
    assert by_sid[sid]["classification"] == "UNCLASSIFIED//EXERCISE"


@pytest.mark.verifies("FR-4510")
def test_aar_csv_export_embeds_classification_over_http():
    c = _client()
    sid = c.post("/api/sessions", json={
        "vignette_id": "leo-isr-denial", "seed": 1, "classification": "UNCLASSIFIED//EXERCISE",
    }).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    csv_text = c.get(f"/api/sessions/{sid}/aar/export.csv").text
    assert "UNCLASSIFIED//EXERCISE" in csv_text


@pytest.mark.verifies("FR-4510")
def test_save_export_embeds_classification_over_http():
    c = _client()
    sid = c.post("/api/sessions", json={
        "vignette_id": "leo-isr-denial", "seed": 1, "classification": "UNCLASSIFIED//EXERCISE",
    }).json()["session"]
    saved = c.get(f"/api/sessions/{sid}/save").json()
    assert saved["classification"] == "UNCLASSIFIED//EXERCISE"


@pytest.mark.verifies("FR-6320")
def test_concurrent_reads_and_writes_lock_safe():
    """ThreadPool hammers mutations + reads on one session; state stays consistent."""
    import concurrent.futures as cf
    c = _client()
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    # Pause the clock so wall-time noise doesn't mask the lock test.
    c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": False})

    def step():       return c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 1.0}).status_code
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


@pytest.mark.verifies("FR-6310")
def test_advance_guard_no_op_at_same_wall_time(monkeypatch):
    """Two consecutive reads at the SAME patched wall time → second is a no-op, no ValueError."""
    c = _client()
    _patch_wall(monkeypatch, 9000.0)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    _patch_wall(monkeypatch, 9010.0)        # +10s
    n1 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    # Same wall time, second read: catch_up sees target == current, must be a no-op.
    n2 = c.get(f"/api/sessions/{sid}/godview").json()["now"]
    assert n1 == n2


@pytest.mark.verifies("FR-6310")
def test_resumed_session_loads_paused():
    """A saved + resumed session starts with the clock paused (anchor cleared)."""
    c = _client()
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    state = c.get(f"/api/sessions/{sid}/save").json()
    sid2 = c.post("/api/sessions/load_save?cell=white", json=state).json()["session"]
    listing = {s["sid"]: s for s in c.get("/api/sessions").json()}
    assert listing[sid2]["started"] is True
    assert listing[sid2]["running"] is False   # resumed paused — must not silently fast-forward


@pytest.mark.verifies("FR-5110")
def test_draft_session_create_add_asset_and_save_as_vignette(tmp_path, monkeypatch):
    """IP-1173 (FR-5110) — the Vignette Creator's HTTP surface end to end. save_vignette() has
    no implicit VIGNETTE_DIR default (IP-1180) — a user_save_dir must be configured."""
    cfg_path = tmp_path / "spacesim.config.yaml"
    save_dir = tmp_path / "user_saves"
    save_dir.mkdir()
    cfg_path.write_text(
        f"content:\n  user_save_dir: {save_dir}\n  external_vignette_dirs:\n    - {save_dir}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("SPACESIM_CONFIG", str(cfg_path))
    c = _client()
    sid = c.post("/api/sessions/draft", json={"title": "HTTP Draft"}).json()["session"]
    # A draft session exists and is registered like any other, but never started.
    listing = {s["sid"]: s for s in c.get("/api/sessions").json()}
    assert listing[sid]["started"] is False

    # Time control is refused against it.
    step = c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 60.0})
    assert step.status_code == 400 and "draft" in step.json()["detail"]    # IP-1076: refusal is a 400

    # Force-add an asset the same way any session's asset entry already works.
    tle1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
    tle2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"
    ack = c.post(f"/api/sessions/{sid}/force/tle?cell=white",
                 json={"id": "HTTP-SAT", "line1": tle1, "line2": tle2, "owner": "blue"}).json()
    assert ack["ok"] is True

    # Save as vignette — a real, loadable file.
    resp = c.post(f"/api/sessions/{sid}/save_vignette?cell=white",
                  json={"vignette_id": "test-ip1173-http-draft", "title": "HTTP Draft Saved"}).json()
    assert resp["vignette_id"] == "test-ip1173-http-draft"
    try:
        from spacesim.content.vignette import build_world, load_vignette
        vig = load_vignette("test-ip1173-http-draft")
        assert vig.title == "HTTP Draft Saved"
        world, _ = build_world(vig)
        assert "HTTP-SAT" in world.assets
    finally:
        from pathlib import Path
        Path(resp["path"]).unlink(missing_ok=True)


@pytest.mark.verifies("FR-5220")
def test_bulk_import_tle_route_end_to_end():
    """IP-1190 (FR-5220) — the new /force/bulk_import route, TLE format, end to end."""
    c = _client()
    sid = c.post("/api/sessions/draft", json={"title": "Bulk Import"}).json()["session"]
    tle1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
    tle2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"
    content = "\n".join(["HTTP-BULK-1", tle1, tle2])
    resp = c.post(f"/api/sessions/{sid}/force/bulk_import?cell=white",
                   json={"format": "tle", "content": content,
                         "assignments": {"HTTP-BULK-1": {"asset_id": "HTTP-BULK-1", "owner": "blue"}}})
    reports = resp.json()
    assert len(reports) == 1
    assert reports[0]["ok"] is True
    assert reports[0]["asset_id"] == "HTTP-BULK-1"

    # An unrecognizable file surfaces as a 400, not a per-object report.
    bad_resp = c.post(f"/api/sessions/{sid}/force/bulk_import?cell=white",
                       json={"format": "tle", "content": "not a tle file", "assignments": {}})
    assert bad_resp.status_code == 400


@pytest.mark.verifies("FR-5510")
def test_save_as_scenario_route_end_to_end(tmp_path, monkeypatch):
    """IP-1200 (FR-5510) — start a session, advance it, save-as-scenario, load the result: the
    new session's start epoch equals the save moment and initial state carries forward."""
    cfg_path = tmp_path / "spacesim.config.yaml"
    save_dir = tmp_path / "user_saves"
    save_dir.mkdir()
    cfg_path.write_text(
        f"content:\n  user_save_dir: {save_dir}\n  external_vignette_dirs:\n    - {save_dir}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("SPACESIM_CONFIG", str(cfg_path))
    c = _client()
    sid = _new_session(c)
    c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 600.0})
    c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": False})  # stop catch-up drift
    save_moment = c.get(f"/api/sessions/{sid}/save").json()["final_time"]

    resp = c.post(f"/api/sessions/{sid}/save_vignette?cell=white",
                  json={"vignette_id": "test-ip1200-http-scenario", "title": "HTTP Scenario",
                        "as_scenario": True}).json()
    try:
        from spacesim.content.vignette import load_vignette
        from spacesim.engine import simtime
        vig = load_vignette("test-ip1200-http-scenario")
        assert vig.start_epoch_utc == simtime.to_iso(save_moment)
        assert vig.simulator_version
    finally:
        from pathlib import Path
        Path(resp["path"]).unlink(missing_ok=True)

    # A draft session's own "Save as Vignette" (as_scenario omitted/False) is unaffected.
    draft_sid = c.post("/api/sessions/draft", json={"title": "Still Draft"}).json()["session"]
    draft_resp = c.post(f"/api/sessions/{draft_sid}/save_vignette?cell=white",
                        json={"vignette_id": "test-ip1200-draft-unaffected", "title": "Draft"})
    assert draft_resp.status_code == 200
    from pathlib import Path
    Path(draft_resp.json()["path"]).unlink(missing_ok=True)


@pytest.mark.verifies("FR-7410")
def test_ephemeris_truth_route_no_cell_binding():
    """IP-1210 (FR-7410) — reachable with no cell query param, like /godview."""
    c = _client()
    sid = _new_session(c)
    t0 = c.get(f"/api/sessions/{sid}/save").json()["final_time"]
    r = c.get(f"/api/sessions/{sid}/ephemeris/truth",
              params={"object_id": "ISR-EO-1", "reference_id": "JAM-NORTH",
                      "t1": t0, "t2": t0, "interval_s": 1.0})
    assert r.status_code == 200
    assert "eci_r_x_m" in r.text  # CSV header present


@pytest.mark.verifies("FR-7410")
def test_ephemeris_truth_route_wholly_out_of_range_is_400():
    c = _client()
    sid = _new_session(c)
    t0 = c.get(f"/api/sessions/{sid}/save").json()["final_time"]
    r = c.get(f"/api/sessions/{sid}/ephemeris/truth",
              params={"object_id": "ISR-EO-1", "reference_id": "JAM-NORTH",
                      "t1": t0 + 10_000_000_000, "t2": t0 + 20_000_000_000})
    assert r.status_code == 400


@pytest.mark.verifies("FR-7420")
def test_ephemeris_cell_observed_route_fog_of_war_enforced():
    """IP-1210 (FR-7420) — a cell with no Track on the requested object gets an empty export,
    never another cell's belief or ground truth, mirroring test_scene.py's fog-of-war pattern."""
    c = _client()
    sid = _new_session(c)
    t0 = c.get(f"/api/sessions/{sid}/save").json()["final_time"]
    r = c.get(f"/api/sessions/{sid}/ephemeris/red",
              params={"object_id": "ISR-EO-1", "reference_id": "JAM-NORTH",
                      "t1": t0, "t2": t0, "interval_s": 1.0})
    assert r.status_code == 200
    lines = r.text.strip().splitlines()
    assert len(lines) == 1  # header only — red has no track on blue's ISR-EO-1


@pytest.mark.verifies("FR-7410")
def test_ephemeris_oem_format():
    c = _client()
    sid = _new_session(c)
    t0 = c.get(f"/api/sessions/{sid}/save").json()["final_time"]
    r = c.get(f"/api/sessions/{sid}/ephemeris/truth",
              params={"object_id": "ISR-EO-1", "reference_id": "JAM-NORTH",
                      "t1": t0, "t2": t0, "interval_s": 1.0, "format": "oem"})
    assert r.status_code == 200
    assert "CCSDS_OEM_VERS" in r.text


@pytest.mark.verifies("FR-3440")
def test_roe_change_route_is_white_cell_only():
    """IP-1270 (FR-3440) — only White Cell may issue a live ROE change."""
    c = _client()
    sid = _new_session(c)
    denied = c.post(f"/api/sessions/{sid}/roe/change", json={
        "cell": "blue", "target_cell": "blue", "flag": "kinetic_authorized", "value": True})
    assert denied.json()["ok"] is False and denied.json()["reason"] == "not_controller"

    allowed = c.post(f"/api/sessions/{sid}/roe/change", json={
        "cell": "white", "target_cell": "blue", "flag": "kinetic_authorized", "value": True})
    assert allowed.json()["ok"] is True


@pytest.mark.verifies("FR-3430")
def test_gate_decide_route_rejects_unknown_pending_order():
    """IP-1270 (FR-3430) — the decision route rejects a nonexistent/unmatched pending order id
    (this session's loaded vignette declares no gating rules, so nothing is ever pending)."""
    c = _client()
    sid = _new_session(c)
    r = c.post(f"/api/sessions/{sid}/gate/decide", json={
        "cell": "white", "order_id": "no-such-order", "approve": True})
    assert r.json()["ok"] is False and r.json()["reason"] == "no_such_pending_order"


@pytest.mark.verifies("FR-7330")
def test_aar_playback_start_advance_and_viewpoint_switch():
    """IP-1280 (FR-7330) — the playback routes: start, advance, viewpoint switch."""
    c = _client()
    sid = _new_session(c)
    c.post(f"/api/sessions/{sid}/order", json={
        "cell": "blue", "actor": "ISR-EO-1", "action": "downlink", "params": {"via": "GS-NORTH"}})

    start = c.post(f"/api/sessions/{sid}/aar/playback/start?cell=white", json={"viewpoint": "truth", "speed": 2.0})
    assert start.json()["ok"] is True

    adv = c.post(f"/api/sessions/{sid}/aar/playback/advance?cell=white", json={"dt_s": 30.0})
    assert adv.status_code == 200
    assert "assets" in adv.json()  # ground-truth WorldState shape

    switched = c.post(f"/api/sessions/{sid}/aar/playback/viewpoint", json={"viewpoint": "blue"})
    assert switched.json()["ok"] is True
    state = c.get(f"/api/sessions/{sid}/aar/playback/state")
    assert "own_assets" in state.json()  # CellView shape, not ground truth


@pytest.mark.verifies("FR-7330")
def test_aar_playback_rejects_nonparticipating_cell():
    c = _client()
    sid = _new_session(c)
    r = c.post(f"/api/sessions/{sid}/aar/playback/start?cell=white", json={"viewpoint": "not-a-real-cell"})
    assert r.json()["ok"] is False


@pytest.mark.verifies("FR-7330")
def test_aar_playback_advance_without_start_is_404():
    c = _client()
    sid = _new_session(c)
    r = c.post(f"/api/sessions/{sid}/aar/playback/advance?cell=white", json={"dt_s": 10.0})
    assert r.status_code == 404


@pytest.mark.verifies("FR-7430")
def test_ephemeris_ric_companion_format():
    """FR-7430 — the companion RIC-specific export file, reachable via format=ric on both the
    truth and cell-observed ephemeris routes (BL-0136's resolution of the FR-7410/OEM tension)."""
    c = _client()
    sid = _new_session(c)
    t0 = c.get(f"/api/sessions/{sid}/save").json()["final_time"]
    r = c.get(f"/api/sessions/{sid}/ephemeris/truth",
              params={"object_id": "ISR-EO-1", "reference_id": "JAM-NORTH",
                      "t1": t0, "t2": t0, "interval_s": 1.0, "format": "ric"})
    assert r.status_code == 200
    assert "ric_r_x_m" in r.text
    assert "eci_r_x_m" not in r.text


# -- IP-1300 (FR-8210/FR-8220) — live RIC-frame view route -------------------------------------

def _coorbital_session(c: TestClient) -> str:
    sid = c.post("/api/sessions",
                 json={"vignette_id": "co-orbital-threat-escort", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    return sid


@pytest.mark.verifies("FR-8210")
def test_ric_view_route_cell_scoped_returns_only_cells_own_picture():
    c = _client()
    sid = _coorbital_session(c)
    r = c.get(f"/api/sessions/{sid}/ric_view/blue", params={"origin": "BLUE-HVA"})
    assert r.status_code == 200
    body = r.json()
    assert body["origin"] == "BLUE-HVA" and body["cell"] == "blue"
    ids = {o["id"] for o in body["objects"]}
    assert ids == {"BLUE-ESCORT"}  # blue holds no Track on RED-COORB: never rendered
    assert body["cats"] is None


@pytest.mark.verifies("FR-8210")
def test_ric_view_route_rejects_origin_outside_cells_custody():
    c = _client()
    sid = _coorbital_session(c)
    r = c.get(f"/api/sessions/{sid}/ric_view/blue", params={"origin": "RED-COORB"})
    assert r.status_code == 404
    r = c.get(f"/api/sessions/{sid}/ric_view/blue",
              params={"origin": "BLUE-HVA", "chase": "BLUE-ESCORT", "target": "RED-COORB"})
    assert r.status_code == 404


@pytest.mark.verifies("FR-8210")
def test_ric_view_route_white_renders_every_object_from_ground_truth():
    """Implementation Task 1/8 — `build_scene()` has no `cell == "white"` case, so the White
    variant is wired explicitly through the `get_godview()` ground-truth world, not `cell="white"`
    filtering; it renders every on-orbit object (FR-4610 exact-match standard)."""
    c = _client()
    sid = _coorbital_session(c)
    r = c.get(f"/api/sessions/{sid}/ric_view/white",
              params={"origin": "RED-COORB", "chase": "RED-COORB", "target": "BLUE-HVA"})
    assert r.status_code == 200
    body = r.json()
    assert {o["id"] for o in body["objects"]} == {"BLUE-HVA", "BLUE-ESCORT"}
    assert all(o["source"] == "asset" for o in body["objects"])
    assert 0.0 <= body["cats"]["phase_angle_deg"] <= 180.0
    # Ground truth agrees with the god-view state: co-orbital, same plane -> ~zero cross-track.
    for o in body["objects"]:
        assert abs(o["ric_r"][2]) < 1.0


@pytest.mark.verifies("FR-8210")
def test_ric_view_client_surface_is_served():
    c = _client()
    assert 'src="/ricview.js"' in c.get("/").text
    js = c.get("/ricview.js")
    assert js.status_code == 200 and "/ric_view/" in js.text


@pytest.mark.verifies("FR-8210")
def test_ric_view_route_requires_origin():
    c = _client()
    sid = _coorbital_session(c)
    assert c.get(f"/api/sessions/{sid}/ric_view/blue").status_code == 422


# -- IP-1211 (FR-7440) — quick TLE export route ------------------------------------------------

def _coorbital_with_blue_track():
    """A co-orbital session in which Blue holds a state-bearing Track on RED-COORB (seeded the same
    way an observation does — a copy of the truth orbit at observation time, `orders.py`)."""
    from spacesim.engine.custody import Track
    from spacesim.session.inprocess import InProcessSession

    api = InProcessSession()
    c = TestClient(create_app(api))
    sid = _coorbital_session(c)
    world = api._sessions[sid].sim.world
    world.tracks.append(Track(object="RED-COORB", owner="blue", last_observation=world.now,
                              confidence=0.9,
                              state_estimate=world.assets["RED-COORB"].orbit.model_copy(deep=True)))
    return c, sid


@pytest.mark.verifies("FR-7440")
def test_tle_route_returns_lines_for_tracked_object():
    pytest.importorskip("sgp4")
    c, sid = _coorbital_with_blue_track()
    r = c.get(f"/api/sessions/{sid}/tle/blue", params={"object_id": "RED-COORB"})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "track" and body["object_id"] == "RED-COORB" and body["cell"] == "blue"
    assert len(body["line1"]) == 69 and len(body["line2"]) == 69
    assert body["line1"].startswith("1 ") and body["line2"].startswith("2 ")
    assert body["fit_error_m"] <= 1000.0 and body["note"]


@pytest.mark.verifies("FR-7440")
def test_tle_route_untracked_is_404():
    pytest.importorskip("sgp4")
    c = _client()
    sid = _coorbital_session(c)
    r = c.get(f"/api/sessions/{sid}/tle/blue", params={"object_id": "RED-COORB"})
    assert r.status_code == 404
    assert "track" in r.json()["detail"]


@pytest.mark.verifies("FR-7440")
def test_tle_route_requires_object_id():
    c = _client()
    sid = _coorbital_session(c)
    assert c.get(f"/api/sessions/{sid}/tle/blue").status_code == 422


@pytest.mark.verifies("FR-7440")
def test_tle_route_white_reads_truth():
    pytest.importorskip("sgp4")
    c = _client()
    sid = _coorbital_session(c)
    r = c.get(f"/api/sessions/{sid}/tle/white", params={"object_id": "RED-COORB"})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "truth" and body["cell"] == "white"
    assert len(body["line1"]) == 69


@pytest.mark.verifies("FR-7440")
def test_tle_route_own_satellite_200():
    """IP-1212 (FR-7440 amended, FS-121 v2.1 AC11) — a cell exports its own satellite with no Track;
    the other cell (no Track either) is still refused; an own asset with no orbit is refused."""
    pytest.importorskip("sgp4")
    c = _client()
    sid = _coorbital_session(c)
    assets = c.get(f"/api/sessions/{sid}/godview").json()["assets"]
    own = next(a["id"] for a in assets.values() if a["owner"] == "blue" and a.get("orbit"))
    r = c.get(f"/api/sessions/{sid}/tle/blue", params={"object_id": own})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "own" and body["cell"] == "blue" and body["object_id"] == own
    assert len(body["line1"]) == 69 and len(body["line2"]) == 69
    assert c.get(f"/api/sessions/{sid}/tle/red", params={"object_id": own}).status_code == 404

    sid2 = _new_session(c)   # leo-isr-denial: GS-NORTH is a Blue-owned asset with no orbit
    r = c.get(f"/api/sessions/{sid2}/tle/blue", params={"object_id": "GS-NORTH"})
    assert r.status_code == 404 and "orbit" in r.json()["detail"]


@pytest.mark.verifies("FR-7440")
def test_tle_export_client_lists_own_satellites():
    """IP-1212 Design Decisions 2/5 — the served picker labels the new "own" source."""
    js = _client().get("/tleexport.js").text
    assert '"own"' in js


@pytest.mark.verifies("FR-7440")
def test_tle_export_client_surface_is_served():
    c = _client()
    assert 'src="/tleexport.js"' in c.get("/").text
    js = c.get("/tleexport.js")
    assert js.status_code == 200 and "/tle/" in js.text


# -- IP-1262 (BL-0176) — export sampling bounds at the route ---------------------------------------

@pytest.mark.verifies("NFR-3710")
def test_ephemeris_routes_reject_non_positive_interval_400():
    """Test 5 — interval_s <= 0 is a 400 on both ephemeris routes (was a 1 us step / hang)."""
    c = _client()
    sid = _new_session(c)
    c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": False})
    c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 600})
    now = c.get(f"/api/sessions/{sid}/clock").json()["now"]
    base = {"object_id": "ISR-EO-1", "reference_id": "JAM-NORTH", "t1": now - 20_000, "t2": now}
    r = c.get(f"/api/sessions/{sid}/ephemeris/truth", params={**base, "interval_s": 0})
    assert r.status_code == 400
    r = c.get(f"/api/sessions/{sid}/ephemeris/blue", params={**base, "interval_s": -1})
    assert r.status_code == 400


@pytest.mark.verifies("NFR-3710")
def test_telemetry_export_route_rejects_over_ceiling_interval_400():
    """Test 6 — a tiny positive interval_s (passes gt=0) is a 400 naming the ceiling."""
    from spacesim.session import ephemeris
    c = _client()
    sid = _new_session(c)
    c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": False})
    c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 600})
    now = c.get(f"/api/sessions/{sid}/clock").json()["now"]
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/export.csv",
              params={"t1": now - 20_000, "t2": now, "interval_s": 0.000001})
    assert r.status_code == 400
    assert str(ephemeris.MAX_EXPORT_SAMPLES) in r.json()["detail"]


@pytest.mark.verifies("FR-4430")
def test_inject_route_rejects_invalid_inject_400():
    """IP-1063 (BL-0188) — an inject whose FR-4430 target precondition fails is a 400 naming the
    target, not a 200 {"ok": true} that silently does nothing."""
    c = _client()
    sid = _new_session(c)
    r = c.post(f"/api/sessions/{sid}/inject?cell=white", json={"inject": {"effects": [
        {"type": "anomaly", "target": "NO-SUCH-SAT", "subsystem": "bus"}]}})
    assert r.status_code == 400
    assert "NO-SUCH-SAT" in r.json()["detail"]
    r = c.post(f"/api/sessions/{sid}/inject?cell=white", json={"inject": {"effects": [
        {"type": "message", "to": ["blue"], "text": "hello"}]}})
    assert r.status_code == 200 and r.json()["ok"] is True
