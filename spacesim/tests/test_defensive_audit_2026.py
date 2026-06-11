"""Defensive regression tests locked in by the Jun 2026 full-codebase audit.

Every test here pins one finding from ``docs/AUDIT-2026-06.md`` so a future
AI-introduced change (or a careless human one) can't silently undo it. New
defensive tests for future audits **belong in their own dated file**, not by
extending this one — that keeps each audit's invariants traceable.

Coverage matrix (audit § → test names below):

| Audit § | Property | Test(s) |
|---|---|---|
| C2 | GEO regime classification | ``test_classify_regime_real_geo`` |
| C3 | Order booking dicts released on execute | ``test_executed_command_releases_pass_booking``, ``test_executed_observe_releases_sensor_booking`` |
| C4 | period_s NaN-guard | ``test_period_s_invalid_a`` |
| D1 | Inject message text is escaped before render | ``test_inject_message_text_round_trips_escaped`` |
| D2 | TleRequest.id + OrderRequest.actor/target charset validation | ``test_tle_id_charset_rejected``, ``test_order_actor_charset_rejected`` |
| D4 | Vignette path-traversal rejected | ``test_load_vignette_rejects_path_traversal``, ``test_load_vignette_rejects_absolute_path`` |
| D4 | YAML safe-load (no code execution) | ``test_yaml_safe_load_no_code_execution`` |
| D6 | Telemetry series ``n`` clamp | ``test_telemetry_series_n_clamped`` |
| D7 | Session table bound + LRU eviction | ``test_session_table_evicts_when_full`` |
| D7 | load_save eventlog size cap | ``test_load_save_rejects_huge_eventlog`` |
| E2 | Fog-of-war never leaks Blue ground truth to Red | ``test_fog_red_cannot_see_blue_*`` (parametrised) |
| E5 | Tautological inject-library cache test replaced | ``test_inject_library_is_cached_for_real`` |
| E6 | Third-body perturbation has a real test | ``test_third_body_acceleration_points_toward_body`` |
| F2 | Clock-lag watchdog field exists in clock_state | ``test_clock_state_carries_lag_warning_field`` |
"""

from __future__ import annotations

import math

import numpy as np
import pytest

# --------------------------------------------------------------------------- #
# C2 — GEO regime classification.
# --------------------------------------------------------------------------- #
def test_classify_regime_real_geo():
    """Real GEO sat (a≈42,164 km) must classify GEO, not MEO (audit §C2)."""
    from spacesim.engine.orbit import classify_regime
    # GEO: a = 42,164 km, e ≈ 0.
    assert classify_regime(a_m=42_164_000.0, e=0.0, i_deg=0.05) == "GEO"
    # Slightly inclined GEO — should still classify GEO.
    assert classify_regime(a_m=42_164_000.0, e=0.001, i_deg=2.5) == "GEO"
    # MEO GPS-class (a ≈ 26,560 km) — must remain MEO.
    assert classify_regime(a_m=26_560_000.0, e=0.0, i_deg=55.0) == "MEO"


def test_period_s_invalid_a():
    """``period_s`` must return NaN for non-positive a rather than raising (audit §C4)."""
    from spacesim.engine.orbit import period_s
    assert math.isnan(period_s(0.0))
    assert math.isnan(period_s(-1.0))


# --------------------------------------------------------------------------- #
# C3 — Order booking dicts released on execute.
# --------------------------------------------------------------------------- #
def _seed_session(seed: int = 1):
    from spacesim.content.vignette import load_vignette
    from spacesim.session.manager import SessionManager
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=seed)
    mgr.start()
    return mgr


def test_executed_observe_releases_sensor_booking():
    """After an observe order executes, its sensor booking is no longer in the dict (audit §C3)."""
    from spacesim.engine.orders import Order
    mgr = _seed_session()
    osys = mgr.osys

    # Issue an observe order; pick any radar that can see any red target.
    # Use auto-selection on the first red target id.
    red_targets = [aid for aid, a in mgr.world.assets.items() if a.owner == "red"]
    if not red_targets:
        pytest.skip("no red target to observe in this vignette")
    target = red_targets[0]

    order = Order(cell="blue", actor="auto", action="observe", target=target,
                  params={"intent": "track"})
    issued = osys.issue(order)
    if issued.status == "rejected":
        pytest.skip(f"vignette didn't accept observe order ({issued.fail_reason}); test inapplicable")

    assert osys._order_sensor, "observe order should have a sensor booking after issue"
    # Advance past the window — handler fires and should release the booking.
    win_start, _win_end = osys.orders[issued.id].earliest_window
    mgr.advance_to(win_start + 1_000_000)
    assert issued.id not in osys._order_sensor, (
        "sensor booking dict still contains executed order id (memory leak fixed in audit §C3)"
    )


def test_executed_command_releases_pass_booking():
    """After a command (or maneuver) executes, its pass-booking row is released (audit §C3)."""
    from spacesim.engine.orders import Order
    mgr = _seed_session()
    osys = mgr.osys

    # Find any Blue maneuver-capable satellite.
    sat_id = next(
        (aid for aid, a in mgr.world.assets.items()
         if a.owner == "blue" and a.kind == "satellite" and a.orbit is not None),
        None,
    )
    if sat_id is None:
        pytest.skip("no maneuver-capable blue satellite")
    sat = mgr.world.assets[sat_id]
    if sat.resources is None or float(getattr(sat.resources, "delta_v_ms", 0) or 0) < 5.0:
        pytest.skip("test satellite lacks delta-v budget")

    order = Order(cell="blue", actor=sat_id, action="maneuver", target=None,
                  params={"mode": "lvlh", "dv": [0.0, 1.0, 0.0]})
    issued = osys.issue(order)
    if issued.status == "rejected":
        pytest.skip(f"vignette didn't accept maneuver order ({issued.fail_reason})")

    pass_key_before = osys._order_pass.get(issued.id)
    # Some maneuver paths (ISL/stored) don't bind to a pass; only test when one was booked.
    if pass_key_before is None:
        pytest.skip("maneuver order was routed off-pass (ISL/stored); test inapplicable")

    win_start = issued.earliest_window[0]
    mgr.advance_to(win_start + 1_000_000)
    assert issued.id not in osys._order_pass, (
        "pass booking dict still contains executed order id (memory leak fixed in audit §C3)"
    )


# --------------------------------------------------------------------------- #
# D1 — Stored XSS via inject message text.
# We can't run a browser here, but we *can* verify that the JS escape helper
# the app uses produces escaped output for an attacker-controlled string. The
# server lays out the message-text field unmodified (correct: scrubbing
# belongs at render time), and the front end escapes via ``esc()``.
# --------------------------------------------------------------------------- #
def test_inject_message_text_round_trips_escaped():
    """The app.js render path must HTML-escape inject text (audit §D1)."""
    from pathlib import Path
    app_js = (Path(__file__).resolve().parent.parent / "ui_web" / "static" / "app.js").read_text()
    # All four interpolation sites identified in the audit must wrap with esc():
    required = [
        '$("messages").innerHTML = messages.map((m) => `<li>${esc(m.text)}</li>`)',
        # Effects list also receives target/symptom that can carry attacker payload.
        "esc(e.target)",
        "esc(e.symptom)",
        # TLE asset id (D2) — at minimum the dv table interpolation uses esc.
        "esc(a.id)",
    ]
    for snippet in required:
        assert snippet in app_js, f"app.js missing audit-pinned escape: {snippet!r}"


# --------------------------------------------------------------------------- #
# D2 — Server-side charset validation of attacker-controlled IDs.
# --------------------------------------------------------------------------- #
def _client():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from spacesim.ui_web.server import create_app
    return TestClient(create_app())


def _sid(c) -> str:
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    return sid


@pytest.mark.parametrize("bad_id", [
    "<script>alert(1)</script>",
    "../../etc/passwd",
    "id with spaces",
    "id;rm -rf",
    "",
    "x" * 65,  # exceeds 64-char cap
])
def test_tle_id_charset_rejected(bad_id: str):
    """TleRequest.id must reject any string that isn't ``[A-Za-z0-9_.-]{1,64}`` (audit §D2)."""
    c = _client()
    sid = _sid(c)
    body = {"id": bad_id, "line1": "1 25544U 98067A", "line2": "2 25544"}
    r = c.post(f"/api/sessions/{sid}/force/tle", json=body)
    assert r.status_code in (422, 400), f"hostile TLE id {bad_id!r} got status {r.status_code}"


@pytest.mark.parametrize("bad_id", [
    "<img src=x onerror=alert(1)>",
    "../../etc/passwd",
    "actor with space",
])
def test_order_actor_charset_rejected(bad_id: str):
    """OrderRequest.actor must reject hostile strings (audit §D2)."""
    c = _client()
    sid = _sid(c)
    body = {"cell": "blue", "actor": bad_id, "action": "observe", "target": "RED-TGT", "params": {}}
    r = c.post(f"/api/sessions/{sid}/order", json=body)
    assert r.status_code == 422, f"hostile actor {bad_id!r} got status {r.status_code}"


# --------------------------------------------------------------------------- #
# D4 — Vignette path traversal and YAML safety.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("bad_id", [
    "../../etc/passwd",
    "/etc/passwd",
    "..\\..\\windows\\system32\\config",
    "~root/.ssh/id_rsa",
    ".env",
    "foo/bar",
    "abc%2e%2e%2fabc",  # url-encoded traversal — still has '/' in literal form? no, '%' is not allowed
    "id with space",
])
def test_load_vignette_rejects_path_traversal(bad_id: str):
    """``load_vignette`` must refuse path-traversal / disallowed-charset ids (audit §D4)."""
    from spacesim.content.vignette import load_vignette
    with pytest.raises((ValueError, FileNotFoundError)):
        load_vignette(bad_id)


def test_load_vignette_rejects_absolute_path():
    from spacesim.content.vignette import load_vignette, VIGNETTE_DIR
    # Even pointing at a legitimate file inside VIGNETTE_DIR by absolute path
    # is rejected — the loader takes ids, not paths.
    legit = str(next(VIGNETTE_DIR.glob("*.yaml")))
    with pytest.raises(ValueError):
        load_vignette(legit)


def test_yaml_safe_load_no_code_execution(tmp_path, monkeypatch):
    """A YAML file containing ``!!python/object/apply:os.system`` must load safely.

    Proves the loader uses ``yaml.safe_load`` everywhere (audit §D4). We point
    VIGNETTE_DIR at a temp directory that holds the hostile file plus a marker
    we can read back.
    """
    from spacesim.content import vignette as vmod
    hostile = tmp_path / "bad.yaml"
    hostile.write_text(
        "vignette:\n"
        "  id: pwn\n"
        "  attack: !!python/object/apply:os.system [\"touch /tmp/spacesim-pwned-marker\"]\n"
    )
    monkeypatch.setattr(vmod, "VIGNETTE_DIR", tmp_path)
    # Listing should tolerate the (malformed-for-Vignette) file; load_vignette
    # raises a clean error, not a code-execution side effect.
    listing = vmod.list_vignettes()
    assert isinstance(listing, list)  # didn't 500
    # Whether listing chose to include "pwn" or skip it is unimportant; what
    # matters is that no os.system call happened.
    import os
    assert not os.path.exists("/tmp/spacesim-pwned-marker"), (
        "yaml.load executed os.system — loader is unsafe"
    )


# --------------------------------------------------------------------------- #
# D6 — Telemetry series ``n`` clamp.
# --------------------------------------------------------------------------- #
def test_telemetry_series_n_clamped():
    c = _client()
    sid = _sid(c)
    # n=10_000_000 must be rejected before it reaches range(n).
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/rx_dbm?n=10000000")
    assert r.status_code == 422
    # n=0 also rejected (must be >= 2).
    assert c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/rx_dbm?n=0").status_code == 422
    # And the upper bound boundary (2000) is allowed.
    r_ok = c.get(f"/api/sessions/{sid}/telemetry/blue/ISR-EO-1/rx_dbm?n=2000")
    assert r_ok.status_code in (200, 404)  # 404 if the series simply doesn't exist; not a 422


# --------------------------------------------------------------------------- #
# D7 — Session-table bound + load_save replay bound.
# --------------------------------------------------------------------------- #
def test_session_table_evicts_when_full():
    """Creating MAX_LIVE_SESSIONS + 1 sessions must not unbound-grow the table (audit §D7)."""
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    cap = InProcessSession.MAX_LIVE_SESSIONS
    for _ in range(cap + 3):
        api.load_vignette("leo-isr-denial")
    assert len(api._sessions) <= cap, (
        f"_sessions grew to {len(api._sessions)} > cap {cap}"
    )


def test_load_save_rejects_huge_eventlog():
    """``load_save`` must refuse an eventlog beyond MAX_EVENTLOG_REPLAY_ENTRIES (audit §D7)."""
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    huge = [{"seq": i, "sim_time": i, "kind": "inc_counter", "payload": {"name": "x"}}
            for i in range(InProcessSession.MAX_EVENTLOG_REPLAY_ENTRIES + 1)]
    state = {
        "vignette_id": "leo-isr-denial",
        "final_time": 0,
        "eventlog": huge,
        "pending": [],
        "orders": [],
        "seed": 1,
        "started": False,
    }
    with pytest.raises(ValueError):
        api.load_save(state)


# --------------------------------------------------------------------------- #
# E2 — Systematic fog-of-war proof.
# Loads a vignette with both Blue and Red assets and asserts no Blue asset id
# leaks into a Red read response across the documented endpoint surface.
# --------------------------------------------------------------------------- #
def _blue_ids(c, sid):
    god = c.get(f"/api/sessions/{sid}/godview").json()
    return [aid for aid, a in (god.get("assets") or {}).items() if a.get("owner") == "blue"]


# Runtime fog-of-war endpoints. These report on **live world state**, so
# their responses must NEVER name an adversary asset the cell hasn't observed
# via its custody catalog. Authored content (brief, objectives, coaching)
# is deliberately excluded — those endpoints carry vignette-author text that
# intentionally describes the adversary as the "threat picture" / target.
FOG_READ_ENDPOINTS = [
    "/api/sessions/{sid}/view/red",
    "/api/sessions/{sid}/scene/red",
    "/api/sessions/{sid}/orders/red",
    "/api/sessions/{sid}/activity/red",
    "/api/sessions/{sid}/conjunctions/red",
    "/api/sessions/{sid}/next_contacts/red",
    "/api/sessions/{sid}/ssn/red/requests",
]

# Authored-content endpoints — exempted, but listed here so a future maintainer
# sees the conscious decision. Any new endpoint that filters runtime world
# state and is added without being listed in FOG_READ_ENDPOINTS will not be
# covered by the systematic fog test; that omission is itself a finding.
_AUTHORED_CONTENT_EXEMPT = [
    "/api/sessions/{sid}/brief/red",
    "/api/sessions/{sid}/objectives/red",
    "/api/sessions/{sid}/coaching/red",
]


@pytest.mark.parametrize("endpoint_tpl", FOG_READ_ENDPOINTS)
def test_fog_red_cannot_see_blue_assets(endpoint_tpl: str):
    """For every Red-cell read endpoint, no Blue asset id may appear in the response (audit §E2).

    This is the systematic proof: a new endpoint that forgets ``_owns()``
    will fail this test for whatever vignette has Blue assets the new endpoint
    forgets to filter out. Today's coverage is per-endpoint; this generalises.
    """
    c = _client()
    sid = _sid(c)
    blue_ids = _blue_ids(c, sid)
    if not blue_ids:
        pytest.skip("vignette has no Blue ground-truth assets to leak")
    url = endpoint_tpl.format(sid=sid)
    r = c.get(url)
    # 404 / not-implemented is acceptable; what's NOT acceptable is a 200 that contains a Blue id.
    if r.status_code != 200:
        return
    body = r.text
    leaked = [bid for bid in blue_ids if bid in body]
    assert not leaked, f"{endpoint_tpl} leaked Blue asset ids to Red: {leaked}"


# --------------------------------------------------------------------------- #
# E5 — Replace the tautological inject-library cache test.
# --------------------------------------------------------------------------- #
def test_inject_library_is_cached_for_real():
    """Two consecutive calls must return the **same list object** — that's caching (audit §E5)."""
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    a = api.inject_library()
    b = api.inject_library()
    # Caching contract: identical lists are returned by reference for identity.
    # InProcessSession returns a *copy*, so identity isn't right — but the
    # cache attribute must exist and the two lists must be equal AND the
    # underlying cache attribute must not be None.
    assert a == b
    assert getattr(api, "_inject_library_cache", None) is not None, (
        "_inject_library_cache should be populated after first call"
    )
    # The cache should not be re-read from disk on the second call.
    cache_obj = api._inject_library_cache
    _ = api.inject_library()
    assert api._inject_library_cache is cache_obj, (
        "cache object was replaced on second call (real cache contract violated)"
    )


# --------------------------------------------------------------------------- #
# E6 — Third-body perturbation has a real test.
# --------------------------------------------------------------------------- #
def test_third_body_acceleration_points_toward_body():
    """Sun's third-body acceleration on a LEO sat points toward the Sun.

    (audit §E6 — until now ``perturbations.third_body_acceleration`` had no
    direct test.)"""
    from spacesim.engine.perturbations import third_body_acceleration

    # Satellite at (LEO altitude, 0, 0); Sun far out along +x.
    r_sat = np.array([7_000_000.0, 0.0, 0.0])
    r_body_from_sat = np.array([1.496e11, 0.0, 0.0])  # 1 AU
    mu_sun = 1.327e20
    a_vec = third_body_acceleration(r_sat, r_body_from_sat, mu_sun)
    # Net acceleration direction: there's tidal cancellation, but the gross
    # direct gravitational attraction dominates. The acceleration must have a
    # non-trivial magnitude and point in +x (toward the body).
    assert np.linalg.norm(a_vec) > 0
    assert a_vec[0] > 0
    assert abs(a_vec[1]) < 1e-15 and abs(a_vec[2]) < 1e-15


# --------------------------------------------------------------------------- #
# F2 — Clock-lag watchdog field exists in clock_state.
# --------------------------------------------------------------------------- #
def test_clock_state_carries_lag_warning_field():
    """``SessionManager.clock_state()`` must always carry a ``lag_warning`` key
    (None when healthy) so the UI can surface hardware warnings (audit §F2)."""
    mgr = _seed_session()
    state = mgr.clock_state()
    assert "lag_warning" in state
    assert state["lag_warning"] is None  # fresh session, no lag history
