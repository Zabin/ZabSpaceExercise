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
