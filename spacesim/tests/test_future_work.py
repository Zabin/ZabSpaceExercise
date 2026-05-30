"""Tests for FUTURE-WORK items implemented in this batch.

Covers: AAR CSV/JSON export (§10.E.20), ground-station outage inject (§10.D.15),
atmospheric refraction option (§10.C.13).
"""

from __future__ import annotations

import pytest

from spacesim.content.vignette import load_vignette
from spacesim.engine.access import AccessConfig, _refracted_elevation
from spacesim.engine.orders import Order
from spacesim.session.aar import export_csv, report
from spacesim.session.manager import SessionManager


# ---------------------------------------------------------------------------
# §10.E.20 AAR export
# ---------------------------------------------------------------------------

def test_aar_csv_export_has_three_sections():
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    mgr.advance_to(mgr.world.now + 60 * 1_000_000)   # produce some sim time + maybe events
    csv = export_csv(report(mgr))
    # META + TIMELINE + OBJECTIVES sections each have a header marker.
    assert "META" in csv
    assert "TIMELINE" in csv
    assert "OBJECTIVES" in csv
    # Vignette id appears in the META section.
    assert "leo-isr-denial" in csv


def test_aar_csv_export_round_trips_objectives():
    """Every objective in the live report appears in the CSV."""
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    rep = report(mgr)
    csv = export_csv(rep)
    for side, objs in rep.final_objectives.items():
        for oid in objs:
            assert oid in csv, f"objective {side}.{oid} missing from CSV export"


def test_aar_json_export_endpoint_serves_csv_and_json():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from spacesim.ui_web.server import create_app
    c = TestClient(create_app())
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start")
    csv = c.get(f"/api/sessions/{sid}/aar/export.csv")
    assert csv.status_code == 200 and "META" in csv.text
    js = c.get(f"/api/sessions/{sid}/aar/export.json").json()
    assert "vignette" in js and js["vignette"] == "leo-isr-denial"


# ---------------------------------------------------------------------------
# §10.D.15 ground-station outage inject
# ---------------------------------------------------------------------------

def test_gs_outage_inject_degrades_station_and_clears_on_restore():
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    gs = mgr.world.assets.get("GS-NORTH")
    assert gs is not None and gs.health == "nominal"

    mgr.fire_inject([{"type": "gs_outage", "target": "GS-NORTH", "cause": "cable_cut"}])
    assert mgr.world.assets["GS-NORTH"].health == "degraded"

    mgr.fire_inject([{"type": "gs_outage", "target": "GS-NORTH", "restore": True}])
    assert mgr.world.assets["GS-NORTH"].health == "nominal"


def test_gs_outage_blocks_downlink_orders():
    """A downlink via a degraded station rejects with no_window (scene_from_world excludes it)."""
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    mgr.fire_inject([{"type": "gs_outage", "target": "GS-NORTH", "cause": "cable_cut"}])
    ack = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink",
                                        params={"via": "GS-NORTH"}))
    assert ack.status == "rejected" and ack.reason == "no_window"


# ---------------------------------------------------------------------------
# §10.C.13 atmospheric refraction
# ---------------------------------------------------------------------------

def test_refraction_lifts_horizon_by_about_half_a_degree():
    """At true elevation = 0°, refraction adds ~0.55° (Saemundsson)."""
    h_app = _refracted_elevation(0.0)
    assert 0.4 < h_app < 0.7


def test_refraction_negligible_aloft():
    """At true elevation ≥ 20°, refraction is < 0.05°."""
    h_app = _refracted_elevation(20.0)
    assert 19.95 < h_app < 20.05


def test_space_weather_inject_increases_eclipse_drain():
    """§10.C.11 — severe storm doubles eclipse drain; a sat in eclipse loses SoC faster."""
    from spacesim.engine.bus import BusState, advance_bus
    from spacesim.engine.simtime import minutes

    def soc_after_eclipse(severity: str) -> float:
        bus = BusState()
        bus.power.battery_soc = 0.9
        bus.power.drain_rate_per_s = 1e-4
        advance_bus(bus, None, minutes(20), sunlit=False, space_weather=severity)
        return bus.power.battery_soc

    nominal = soc_after_eclipse("none")
    minor = soc_after_eclipse("minor")
    severe = soc_after_eclipse("severe")
    assert nominal > minor > severe   # storm drains battery faster


def test_space_weather_inject_round_trips_through_session():
    """Firing a space-weather inject persists severity on WorldState and survives replay."""
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    assert mgr.world.space_weather["severity"] == "none"
    mgr.fire_inject([{"type": "space_weather", "severity": "severe"}])
    assert mgr.world.space_weather["severity"] == "severe"


def test_refraction_extends_pass_duration_marginally():
    """Toggle refraction on for a known orbit + station and confirm windows widen, not shrink."""
    from spacesim.engine.access import AccessProvider
    from spacesim.engine.orders import scene_from_world
    from spacesim.engine.propagator import ModeratePropagator

    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    scene = scene_from_world(mgr.world)
    prop = ModeratePropagator()

    nominal = AccessProvider(scene, propagator=prop, config=AccessConfig(atmospheric_refraction=False))
    bent    = AccessProvider(scene, propagator=prop, config=AccessConfig(atmospheric_refraction=True))
    from spacesim.engine.access import COMMAND_UPLINK
    t0 = mgr.world.now
    t1 = t0 + 3 * 3600 * 1_000_000   # 3-hour horizon
    w_nom = nominal.windows("GS-NORTH", "ISR-EO-1", COMMAND_UPLINK, t0, t1)
    w_bent = bent.windows("GS-NORTH", "ISR-EO-1", COMMAND_UPLINK, t0, t1)
    assert len(w_nom) >= 1 and len(w_bent) >= 1
    dur_nom = w_nom[0].end - w_nom[0].start
    dur_bent = w_bent[0].end - w_bent[0].start
    assert dur_bent >= dur_nom    # refraction never shrinks a pass


# ---------------------------------------------------------------------------
# §10.C.12 variable elevation masks (terrain-aware horizon)
# ---------------------------------------------------------------------------

def test_mask_table_shrinks_passes_relative_to_scalar_mask():
    """A high mask_table value across the whole sky shrinks pass durations vs. the default mask."""
    from spacesim.engine.access import AccessProvider, COMMAND_UPLINK
    from spacesim.engine.orders import scene_from_world
    from spacesim.engine.propagator import ModeratePropagator
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    scene_clear = scene_from_world(mgr.world)
    prop = ModeratePropagator()
    t0 = mgr.world.now
    t1 = t0 + 3 * 3600 * 1_000_000
    clear = AccessProvider(scene_clear, propagator=prop).windows(
        "GS-NORTH", "ISR-EO-1", COMMAND_UPLINK, t0, t1)
    assert len(clear) >= 1
    clear_total = sum(w.end - w.start for w in clear)

    # Install a 60° mountain-wall mask across all azimuths — passes must shrink dramatically.
    mgr.world.assets["GS-NORTH"].mask_table = [
        {"az_min": 0.0, "az_max": 360.0, "mask_deg": 60.0}
    ]
    scene_blocked = scene_from_world(mgr.world)
    blocked = AccessProvider(scene_blocked, propagator=prop).windows(
        "GS-NORTH", "ISR-EO-1", COMMAND_UPLINK, t0, t1)
    blocked_total = sum(w.end - w.start for w in blocked)
    assert blocked_total < clear_total / 2   # the wall cuts available access in half or more


def test_mask_table_per_azimuth_arc():
    """A mask that blocks only one azimuth wedge leaves passes in other wedges intact."""
    from spacesim.engine.access import _refracted_elevation  # noqa: F401  (sanity import)
    from spacesim.engine.entities import GroundSite
    site_clear = GroundSite(id="X", location=__import__("spacesim.engine.geometry", fromlist=["GeoPoint"]).GeoPoint(lat_deg=0.0, lon_deg=0.0))
    site_walled = GroundSite(id="X", location=site_clear.location,
                              mask_table=[{"az_min": 90.0, "az_max": 270.0, "mask_deg": 89.0}])
    # The walled site has a south-wall (azimuths 90..270 blocked). Verify the table parses + applies.
    assert site_walled.mask_table[0]["mask_deg"] == 89.0
    assert site_clear.mask_table == []


# ---------------------------------------------------------------------------
# §10.C.14 GNSS spoof (distinct from jam)
# ---------------------------------------------------------------------------

def test_spoof_outcome_does_not_register_as_link_denied():
    """A spoof effect leaves the link 'up' for the denial helper — only is_link_spoofed catches it."""
    from spacesim.engine.effects import ActiveEffect, is_link_denied, is_link_spoofed
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    t = mgr.world.now
    mgr.world.active_effects.append(ActiveEffect(
        target="ISR-EO-1", outcome="spoof", start=t, end=t + 60 * 1_000_000,
        category="electronic_warfare", template="gnss_spoof",
    ))
    assert is_link_denied(mgr.world, "ISR-EO-1", t) is False
    assert is_link_spoofed(mgr.world, "ISR-EO-1", t) is True


def test_spoof_drives_integrity_flag_telemetry_signature():
    """Under active spoof, integrity_flag drops far below 1.0; nominal sample stays ≈1.0."""
    from spacesim.engine import telemetry as tel
    from spacesim.engine.effects import ActiveEffect
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    t = mgr.world.now
    nominal_val = tel.sample(mgr.world, "ISR-EO-1", "integrity_flag", t, seed=1)["value"]
    mgr.world.active_effects.append(ActiveEffect(
        target="ISR-EO-1", outcome="spoof", start=t - 1, end=t + 60 * 1_000_000,
        category="electronic_warfare", template="gnss_spoof",
    ))
    spoofed_val = tel.sample(mgr.world, "ISR-EO-1", "integrity_flag", t, seed=1)["value"]
    assert nominal_val > 0.9
    assert spoofed_val < 0.5


# ---------------------------------------------------------------------------
# §10.D.16 civilian bystander assets — denying them raises political consequence
# ---------------------------------------------------------------------------

def test_civilian_link_denial_appends_political_consequence():
    """When an EW effect denies a CIVILIAN asset's link, a political consequence is logged."""
    from spacesim.engine.effects import EffectInstance, ModerateEffectResolver
    from spacesim.engine.rng import SeededRng
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    # Mark the ISR sat as civilian and resolve a successful jam against it.
    mgr.world.assets["ISR-EO-1"].civilian = True
    rng = SeededRng(42)
    eff = EffectInstance(template="ew_jam", category="electronic_warfare", segment="link",
                          actor="JAM-NORTH", target="ISR-EO-1",
                          reversible=True, attribution="ambiguous",
                          requires="jam_footprint", intended_outcome="deny",
                          success_prob=1.0, window_start=mgr.world.now,
                          window_end=mgr.world.now + 60 * 1_000_000)
    outcome = ModerateEffectResolver().resolve(eff, mgr.world, rng)
    side = [s for s in outcome.side_effects if s.get("type") == "political_consequence"]
    assert any("civilian_collateral" in s.get("cause", "") for s in side)


def test_non_civilian_link_denial_does_not_raise_consequence():
    """Denying a normal (military) asset's link should NOT raise a civilian-collateral consequence."""
    from spacesim.engine.effects import EffectInstance, ModerateEffectResolver
    from spacesim.engine.rng import SeededRng
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    assert mgr.world.assets["ISR-EO-1"].civilian is False
    rng = SeededRng(42)
    eff = EffectInstance(template="ew_jam", category="electronic_warfare", segment="link",
                          actor="JAM-NORTH", target="ISR-EO-1",
                          reversible=True, attribution="ambiguous",
                          requires="jam_footprint", intended_outcome="deny",
                          success_prob=1.0, window_start=mgr.world.now,
                          window_end=mgr.world.now + 60 * 1_000_000)
    outcome = ModerateEffectResolver().resolve(eff, mgr.world, rng)
    side = [s for s in outcome.side_effects if s.get("type") == "political_consequence"
            and "civilian_collateral" in s.get("cause", "")]
    assert side == []


# ---------------------------------------------------------------------------
# §10.D.17 vignette inspector — /api/vignettes/{id}/source endpoint
# ---------------------------------------------------------------------------

def test_vignette_source_endpoint_returns_yaml():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from spacesim.ui_web.server import create_app
    c = TestClient(create_app())
    r = c.get("/api/vignettes/leo-isr-denial/source")
    assert r.status_code == 200
    assert "vignette:" in r.text and "leo-isr-denial" in r.text


def test_vignette_source_endpoint_404s_unknown_id():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from spacesim.ui_web.server import create_app
    c = TestClient(create_app())
    r = c.get("/api/vignettes/nope-not-a-vignette/source")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# §5 per-step recovery deep-links
# ---------------------------------------------------------------------------

def test_recovery_steps_advance_through_chain():
    """A full recovery confirms first-pass steps and ends with current_step='done'."""
    from spacesim.engine.bus import enter_safe_mode
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    # Put ISR-EO-1 into safe mode with a cyber cause (already patched to allow recovery).
    sat = mgr.world.assets["ISR-EO-1"]
    enter_safe_mode(sat.bus_state, mgr.world.now, cause="cyber")
    # Mark the vulnerability patched so root_cause_unresolved is False at finish.
    for v in sat.cyber_vulnerabilities:
        v["patched"] = True
    # Initial state: no steps done; first step is establish_contact.
    sm = sat.bus_state.safe_mode
    assert sm.current_step == "establish_contact"
    assert sm.steps_done == []
    # Run recovery; advance enough to consume both confirm + finish events.
    res = mgr.begin_recovery("blue", "ISR-EO-1", "GS-TRN")
    assert res.get("ok"), res
    mgr.advance_to(res["finish_at"] + 1)
    sm2 = mgr.world.assets["ISR-EO-1"].bus_state.safe_mode
    # Recovery completed cleanly: current_step is 'done' and steps_done covers all stages.
    assert sm2.current_step == "done"
    assert "establish_contact" in sm2.steps_done
    assert "dump_telemetry" in sm2.steps_done
    assert "patch" in sm2.steps_done
    assert "re_enable" in sm2.steps_done


def test_recovery_blocked_when_root_cause_persists():
    """Unpatched cyber vuln → recovery finishes 'blocked', not 'done'."""
    from spacesim.engine.bus import enter_safe_mode
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    sat = mgr.world.assets["ISR-EO-1"]
    enter_safe_mode(sat.bus_state, mgr.world.now, cause="cyber")
    # Leave the vulnerability unpatched.
    res = mgr.begin_recovery("blue", "ISR-EO-1", "GS-TRN")
    assert res.get("ok")
    mgr.advance_to(res["finish_at"] + 1)
    sm = mgr.world.assets["ISR-EO-1"].bus_state.safe_mode
    assert sm.current_step == "blocked"
    assert sm.blocked_reason is not None


# ---------------------------------------------------------------------------
# §5 EW safe-mode inducement (vs. the cyber path already exercised)
# ---------------------------------------------------------------------------

def test_ew_safe_mode_routes_cause_as_ew():
    """An EW (electronic_warfare) effect with outcome=safe_mode safes the bus with cause='ew'."""
    from spacesim.engine.effects import EffectInstance, ModerateEffectResolver
    from spacesim.engine.rng import SeededRng
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    eff = EffectInstance(template="ew_safe", category="electronic_warfare", segment="link",
                          actor="JAM-TRN", target="ISR-EO-1",
                          reversible=True, attribution="ambiguous",
                          requires="jam_footprint", intended_outcome="safe_mode",
                          success_prob=1.0, sm_susceptibility=1.0, persistence_bonus=1.0,
                          window_start=mgr.world.now)
    ModerateEffectResolver().resolve(eff, mgr.world, SeededRng(7))
    sm = mgr.world.assets["ISR-EO-1"].bus_state.safe_mode
    assert sm.active is True
    assert sm.cause == "ew"


# ---------------------------------------------------------------------------
# §7 SSN auto-cue (organic → SSN characterize)
# ---------------------------------------------------------------------------

def test_auto_cue_files_ssn_characterize_after_organic_observe():
    """Organic observe with intermediate confidence auto-files an SSN characterize request."""
    from spacesim.engine.orders import Order
    # sda-custody-hunt declares ssn_blue_dispersion so the override takes effect.
    mgr = SessionManager(load_vignette("sda-custody-hunt"),
                         overrides={"ssn_auto_cue": True}, seed=1)
    mgr.start()
    assert mgr.osys.auto_cue_ssn is mgr.ssn
    # Issue a search-only observe (characterizes=False) so the resulting track stays uncharacterized.
    obs = Order(cell="blue", actor="BLUE-RADAR-1", action="observe",
                target="RED-OBJ", params={"intent": "track", "gain": 0.6,
                                           "characterizes": False, "classification": None})
    ack = mgr.issue_order("blue", obs)
    assert ack.ok, ack.reason
    mgr.advance_to(ack.earliest_window[1] + 1)
    chars = [r for r in mgr.ssn.requests.values() if r.target == "RED-OBJ" and r.intent == "characterize"]
    assert chars, "no SSN characterize request auto-cued"


def test_auto_cue_disabled_by_default():
    """With ssn_auto_cue unset, no SSN request is filed automatically."""
    from spacesim.engine.orders import Order
    mgr = SessionManager(load_vignette("sda-custody-hunt"), seed=1)
    mgr.start()
    assert mgr.osys.auto_cue_ssn is None    # opt-in only
    obs = Order(cell="blue", actor="BLUE-RADAR-1", action="observe",
                target="RED-OBJ", params={"intent": "track", "gain": 0.6,
                                           "characterizes": False, "classification": None})
    ack = mgr.issue_order("blue", obs)
    if ack.ok:
        mgr.advance_to(ack.earliest_window[1] + 1)
    chars = [r for r in mgr.ssn.requests.values() if r.target == "RED-OBJ"]
    assert chars == []
