"""Tests for the ISR beam mode database and footprint geometry (engine/isr.py).

Coverage:
  - beam_params lookup and fallback behaviour
  - effective_gain computation (look angle + beam gain_factor)
  - soc_drain scaling
  - footprint_polygon shape and orientation
  - ground_heading_deg approximate north/south direction
  - end-to-end: observe order with beam_mode/look_angle params stored on Track
"""
from __future__ import annotations

import math
import pytest

from spacesim.engine.isr import (
    BEAM_MODES,
    available_modes,
    beam_params,
    effective_gain,
    footprint_polygon,
    ground_heading_deg,
    soc_drain,
)


# ---------------------------------------------------------------------------
# beam_params
# ---------------------------------------------------------------------------

def test_beam_params_known_type_and_mode():
    bp, mode = beam_params("isr_eo", "spotlight")
    assert mode == "spotlight"
    assert bp["swath_km"] == pytest.approx(5.0)
    assert bp["gain_factor"] == pytest.approx(1.5)


def test_beam_params_fallback_to_default_mode():
    bp, mode = beam_params("isr_eo")
    assert mode == "stripmap"
    assert bp["swath_km"] == pytest.approx(30.0)


def test_beam_params_unknown_mode_falls_back():
    bp, mode = beam_params("isr_eo", "super_secret")
    assert mode == "stripmap"  # default for isr_eo


def test_beam_params_unknown_payload_type_returns_safe():
    bp, mode = beam_params("laser_cannon")
    assert bp["gain_factor"] > 0
    assert bp["swath_km"] > 0


def test_beam_params_sda_type():
    bp, mode = beam_params("sda", "fine")
    assert mode == "fine"
    assert bp["swath_km"] == pytest.approx(100.0)


def test_beam_params_sar_wide_area():
    bp, mode = beam_params("isr_sar", "wide_area")
    assert mode == "wide_area"
    assert bp["swath_km"] == pytest.approx(500.0)


def test_available_modes_eo():
    modes = available_modes("isr_eo")
    assert set(modes) == {"wide_area", "stripmap", "spotlight", "scan"}


def test_available_modes_sar():
    modes = available_modes("isr_sar")
    assert "polarimetric" in modes
    assert "spotlight" in modes


# ---------------------------------------------------------------------------
# beam_params — weather & mw (IP-1170, BL-0053)
# ---------------------------------------------------------------------------

def test_available_modes_weather_not_eo_fallback():
    modes = available_modes("weather")
    assert set(modes) == {"mesoscale", "conus", "full_disk"}


def test_available_modes_mw_not_eo_fallback():
    modes = available_modes("mw")
    assert set(modes) == {"scan", "stare"}


def test_beam_params_weather_default_mode_is_conus():
    bp, mode = beam_params("weather")
    assert mode == "conus"
    assert bp["resolution_m"] == pytest.approx(1000.0)


def test_beam_params_weather_mesoscale_is_finest_and_fastest():
    bp, mode = beam_params("weather", "mesoscale")
    assert mode == "mesoscale"
    assert bp["resolution_m"] == pytest.approx(500.0)
    assert bp["duty_cycle"] > beam_params("weather", "conus")[0]["duty_cycle"]
    assert bp["duty_cycle"] > beam_params("weather", "full_disk")[0]["duty_cycle"]


def test_beam_params_weather_full_disk_is_coarsest_and_slowest():
    bp, mode = beam_params("weather", "full_disk")
    assert mode == "full_disk"
    assert bp["resolution_m"] == pytest.approx(2000.0)
    assert bp["duty_cycle"] < beam_params("weather", "mesoscale")[0]["duty_cycle"]


def test_beam_params_mw_default_mode_is_scan():
    bp, mode = beam_params("mw")
    assert mode == "scan"


def test_beam_params_mw_stare_has_higher_gain_than_scan():
    scan_bp, _ = beam_params("mw", "scan")
    stare_bp, _ = beam_params("mw", "stare")
    assert stare_bp["gain_factor"] > scan_bp["gain_factor"]
    assert stare_bp["swath_km"] < scan_bp["swath_km"]


def test_beam_params_weather_mw_distinct_from_isr_eo_defaults():
    # BL-0053's original symptom: weather/mw silently fell back to isr_eo's
    # generic stripmap numbers. Confirm the numbers are now type-specific.
    eo_bp, _ = beam_params("isr_eo")
    weather_bp, _ = beam_params("weather")
    mw_bp, _ = beam_params("mw")
    assert weather_bp != eo_bp
    assert mw_bp != eo_bp


def test_beam_params_isr_eo_sar_sda_unchanged_by_weather_mw_addition():
    # Regression: adding weather/mw must not touch any existing entry.
    bp, mode = beam_params("isr_eo", "spotlight")
    assert mode == "spotlight"
    assert bp["swath_km"] == pytest.approx(5.0)
    assert bp["gain_factor"] == pytest.approx(1.5)
    bp, mode = beam_params("isr_sar", "wide_area")
    assert bp["swath_km"] == pytest.approx(500.0)
    bp, mode = beam_params("sda", "fine")
    assert bp["swath_km"] == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# effective_gain
# ---------------------------------------------------------------------------

def test_effective_gain_nadir_is_full_base_times_factor():
    bp, _ = beam_params("isr_eo", "stripmap")  # gain_factor = 1.0
    g = effective_gain(1.0, 0.0, bp)
    assert g == pytest.approx(1.0, abs=1e-9)


def test_effective_gain_spotlight_is_higher():
    bp_strip, _ = beam_params("isr_eo", "stripmap")   # gain_factor 1.0
    bp_spot, _ = beam_params("isr_eo", "spotlight")   # gain_factor 1.5
    g_strip = effective_gain(1.0, 0.0, bp_strip)
    g_spot = effective_gain(1.0, 0.0, bp_spot)
    assert g_spot > g_strip


def test_effective_gain_degrades_with_look_angle():
    bp, _ = beam_params("isr_eo", "stripmap")
    g0 = effective_gain(1.0, 0.0, bp)
    g30 = effective_gain(1.0, 30.0, bp)
    g45 = effective_gain(1.0, 45.0, bp)
    assert g30 < g0
    assert g45 < g30


def test_effective_gain_45deg_approx_cosine():
    bp, _ = beam_params("isr_eo", "stripmap")  # gain_factor 1.0
    g = effective_gain(1.0, 45.0, bp)
    expected = math.cos(math.radians(45.0))
    assert g == pytest.approx(expected, rel=1e-6)


def test_effective_gain_clamps_look_angle_at_45():
    bp, _ = beam_params("isr_eo", "stripmap")
    g45 = effective_gain(1.0, 45.0, bp)
    g60 = effective_gain(1.0, 60.0, bp)  # clamped to 45
    assert g45 == pytest.approx(g60, rel=1e-6)


# ---------------------------------------------------------------------------
# soc_drain
# ---------------------------------------------------------------------------

def test_soc_drain_baseline_300s():
    bp, _ = beam_params("isr_eo", "stripmap")  # power_factor 1.2
    drain = soc_drain(bp, 300.0)
    # base 0.05 × 1.2 × (300/300) = 0.06
    assert drain == pytest.approx(0.05 * 1.2, rel=1e-6)


def test_soc_drain_spotlight_greater_than_wide_area():
    bp_wa, _ = beam_params("isr_eo", "wide_area")
    bp_sp, _ = beam_params("isr_eo", "spotlight")
    assert soc_drain(bp_sp, 300.0) > soc_drain(bp_wa, 300.0)


def test_soc_drain_proportional_to_duration():
    bp, _ = beam_params("isr_eo", "stripmap")
    d1 = soc_drain(bp, 300.0)
    d2 = soc_drain(bp, 600.0)
    assert d2 == pytest.approx(2 * d1, rel=1e-6)


def test_soc_drain_zero_duration():
    bp, _ = beam_params("isr_eo", "stripmap")
    assert soc_drain(bp, 0.0) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# footprint_polygon
# ---------------------------------------------------------------------------

def test_footprint_returns_4_corners():
    bp, _ = beam_params("isr_eo", "stripmap")
    corners = footprint_polygon(0.0, 0.0, 500_000.0, 0.0, bp, 0.0)
    assert len(corners) == 4
    for c in corners:
        assert len(c) == 2


def test_footprint_nadir_centered_on_subsatellite():
    """Nadir (0° look) footprint center should be directly below the satellite."""
    bp, _ = beam_params("isr_eo", "stripmap")
    lat, lon = 30.0, -90.0
    corners = footprint_polygon(lat, lon, 500_000.0, 0.0, bp, 0.0)
    # Average lat/lon of corners should be near the sub-satellite point
    avg_lat = sum(c[0] for c in corners) / 4
    avg_lon = sum(c[1] for c in corners) / 4
    assert avg_lat == pytest.approx(lat, abs=0.01)
    assert avg_lon == pytest.approx(lon, abs=0.01)


def test_footprint_off_nadir_shifts_cross_track():
    """A right-side look angle shifts the footprint away from the ground track."""
    bp, _ = beam_params("isr_eo", "stripmap")
    lat, lon = 0.0, 0.0
    corners_nadir = footprint_polygon(lat, lon, 500_000.0, 90.0, bp, 0.0)   # heading east
    corners_look = footprint_polygon(lat, lon, 500_000.0, 90.0, bp, 30.0)
    # Heading east, look right → footprint shifts south (negative lat shift)
    avg_lat_nadir = sum(c[0] for c in corners_nadir) / 4
    avg_lat_look = sum(c[0] for c in corners_look) / 4
    assert avg_lat_look != pytest.approx(avg_lat_nadir, abs=0.5)


def test_footprint_width_shrinks_with_look_angle():
    """Off-nadir footprint cross-track swath should be narrower (cos roll-off)."""
    bp, _ = beam_params("isr_eo", "wide_area")
    c0 = footprint_polygon(0.0, 0.0, 500_000.0, 0.0, bp, 0.0)
    c30 = footprint_polygon(0.0, 0.0, 500_000.0, 0.0, bp, 30.0)
    # For heading north, cross-track width is measured in longitude degrees
    lon_span_0 = max(c[1] for c in c0) - min(c[1] for c in c0)
    lon_span_30 = max(c[1] for c in c30) - min(c[1] for c in c30)
    assert lon_span_30 < lon_span_0


def test_footprint_spotlight_smaller_than_wide_area():
    bp_wa, _ = beam_params("isr_eo", "wide_area")
    bp_sp, _ = beam_params("isr_eo", "spotlight")
    c_wa = footprint_polygon(0.0, 0.0, 500_000.0, 0.0, bp_wa)
    c_sp = footprint_polygon(0.0, 0.0, 500_000.0, 0.0, bp_sp)
    # Rough area proxy: max lat span × max lon span
    def area(c):
        return (max(x[0] for x in c) - min(x[0] for x in c)) * \
               (max(x[1] for x in c) - min(x[1] for x in c))
    assert area(c_sp) < area(c_wa)


# ---------------------------------------------------------------------------
# ground_heading_deg
# ---------------------------------------------------------------------------

def test_heading_prograde_leo_is_northeast():
    """A prograde LEO orbit at the ascending node should head northeast (0–90°).

    At the equatorial ascending node, the ground-track heading is approximately the orbit
    inclination corrected for Earth's rotation (~35° for i=51.6°, not the inertial heading).
    """
    from spacesim.engine.orbit import OrbitState
    from spacesim.engine.propagator import ModeratePropagator
    orbit = OrbitState(
        source="kepler",
        epoch=0,
        a_m=6_778_000.0, e=0.0001, i_deg=51.6,
        raan_deg=0.0, argp_deg=0.0, ta_deg=0.0,
    )
    prop = ModeratePropagator()
    heading = ground_heading_deg(orbit, 0, prop)
    # Prograde ISS-like orbit: heading is northeast (0–90° range)
    assert 0.0 < heading < 90.0


def test_heading_retrograde_orbit_is_westward():
    """A retrograde orbit (i>90°) should have a westward heading component (>270° or <0°)."""
    from spacesim.engine.orbit import OrbitState
    from spacesim.engine.propagator import ModeratePropagator
    orbit = OrbitState(
        source="kepler",
        epoch=0,
        a_m=6_778_000.0, e=0.0001, i_deg=98.0,
        raan_deg=0.0, argp_deg=0.0, ta_deg=0.0,
    )
    prop = ModeratePropagator()
    heading = ground_heading_deg(orbit, 0, prop)
    # SSO at ascending node: slightly northwest (~348°).  Not in the northeast (0–90°) band.
    assert not (0.0 < heading < 90.0)


# ---------------------------------------------------------------------------
# End-to-end: observe order stores footprint on Track
# ---------------------------------------------------------------------------

def _make_world_with_eo_satellite():
    """Build a minimal world with a Blue EO satellite (dual-registered) and a Red target.

    The Blue ISR satellite is:
      - world.assets["SAT1"]: bus_state + payload_state for power tracking
      - world.sensors["SAT1"]: space_based Sensor so it can be the `actor` in observe orders

    Both share the same orbit.  The target is a Red satellite slightly ahead in the same plane.
    """
    from spacesim.engine.world import WorldState
    from spacesim.engine.entities import Asset, Sensor
    from spacesim.engine.bus import PayloadState, BusState
    from spacesim.engine.orbit import OrbitState
    from spacesim.engine.custody import Track

    world = WorldState()
    leo = OrbitState(
        source="kepler", epoch=0,
        a_m=6_778_000.0, e=0.0001, i_deg=51.6,
        raan_deg=0.0, argp_deg=0.0, ta_deg=0.0,
    )
    sat = Asset(id="SAT1", owner="blue", kind="satellite", orbit=leo,
                payload_state=PayloadState(type="isr_eo"),
                bus_state=BusState())
    sat.bus_state.power.battery_soc = 1.0

    # Register the same satellite as a space-based sensor (observe actor)
    sensor = Sensor(id="SAT1", owner="blue", kind="space_based", orbit=leo,
                    needs_lighting=True)  # EO sensor

    target_leo = OrbitState(
        source="kepler", epoch=0,
        a_m=6_800_000.0, e=0.0001, i_deg=51.6,
        raan_deg=0.0, argp_deg=0.0, ta_deg=5.0,
    )
    tgt = Asset(id="TGT1", owner="red", kind="satellite", orbit=target_leo)

    world.assets["SAT1"] = sat
    world.sensors["SAT1"] = sensor
    world.assets["TGT1"] = tgt
    world.tracks.append(Track(
        object="TGT1", owner="blue",
        last_observation=0, confidence=0.1, characterized=False,
    ))
    return world


def _sim_with_orders(world):
    from spacesim.engine.simulation import Simulation
    from spacesim.engine.orders import OrderSystem

    sim = Simulation(world, seed=42)
    osys = OrderSystem(sim)
    return sim, osys


def test_observe_stores_footprint_on_track():
    from spacesim.engine.orders import Order
    world = _make_world_with_eo_satellite()
    sim, osys = _sim_with_orders(world)
    order = osys.issue(Order(
        cell="blue", actor="SAT1", action="observe", target="TGT1",
        params={"intent": "characterize", "beam_mode": "spotlight", "look_angle_deg": 15.0},
    ))
    assert order.status in ("queued", "executed")
    sim.advance_to(order.earliest_window[0] + 1)
    track = world.track_for("blue", "TGT1")
    assert track.last_footprint is not None
    assert len(track.last_footprint) == 4
    assert track.last_beam_mode == "spotlight"
    assert track.last_collection_t >= 0  # may be 0 if the window opens immediately


def test_observe_applies_soc_drain():
    from spacesim.engine.orders import Order
    world = _make_world_with_eo_satellite()
    sim, osys = _sim_with_orders(world)
    initial_soc = world.assets["SAT1"].bus_state.power.battery_soc
    order = osys.issue(Order(
        cell="blue", actor="SAT1", action="observe", target="TGT1",
        params={"intent": "track", "beam_mode": "spotlight", "duration_s": 300.0},
    ))
    sim.advance_to(order.earliest_window[0] + 1)
    final_soc = world.assets["SAT1"].bus_state.power.battery_soc
    assert final_soc < initial_soc


def test_observe_wide_area_less_drain_than_spotlight():
    from spacesim.engine.orders import Order
    import copy

    world1 = _make_world_with_eo_satellite()
    sim1, osys1 = _sim_with_orders(world1)
    o1 = osys1.issue(Order(
        cell="blue", actor="SAT1", action="observe", target="TGT1",
        params={"beam_mode": "wide_area", "duration_s": 300.0},
    ))
    sim1.advance_to(o1.earliest_window[0] + 1)
    soc_wa = world1.assets["SAT1"].bus_state.power.battery_soc

    world2 = _make_world_with_eo_satellite()
    sim2, osys2 = _sim_with_orders(world2)
    o2 = osys2.issue(Order(
        cell="blue", actor="SAT1", action="observe", target="TGT1",
        params={"beam_mode": "spotlight", "duration_s": 300.0},
    ))
    sim2.advance_to(o2.earliest_window[0] + 1)
    soc_sp = world2.assets["SAT1"].bus_state.power.battery_soc

    assert soc_sp < soc_wa  # spotlight drains more


def test_observe_spotlight_higher_confidence_gain():
    """Spotlight beam gives higher effective gain than wide_area for same base gain."""
    from spacesim.engine.orders import Order

    world1 = _make_world_with_eo_satellite()
    sim1, osys1 = _sim_with_orders(world1)
    o1 = osys1.issue(Order(
        cell="blue", actor="SAT1", action="observe", target="TGT1",
        params={"beam_mode": "wide_area", "gain": 0.5},
    ))
    sim1.advance_to(o1.earliest_window[0] + 1)
    conf_wa = world1.track_for("blue", "TGT1").confidence

    world2 = _make_world_with_eo_satellite()
    sim2, osys2 = _sim_with_orders(world2)
    o2 = osys2.issue(Order(
        cell="blue", actor="SAT1", action="observe", target="TGT1",
        params={"beam_mode": "spotlight", "gain": 0.5},
    ))
    sim2.advance_to(o2.earliest_window[0] + 1)
    conf_sp = world2.track_for("blue", "TGT1").confidence

    assert conf_sp > conf_wa


def test_observe_footprint_in_scene():
    """build_scene() should include collection footprints in SceneView."""
    from spacesim.engine.orders import Order
    from spacesim.session.scene import build_scene
    world = _make_world_with_eo_satellite()
    sim, osys = _sim_with_orders(world)
    order = osys.issue(Order(
        cell="blue", actor="SAT1", action="observe", target="TGT1",
        params={"intent": "characterize", "beam_mode": "stripmap"},
    ))
    sim.advance_to(order.earliest_window[0] + 1)
    scene = build_scene(world, "blue")
    assert len(scene.footprints) == 1
    fp = scene.footprints[0]
    assert fp.target == "TGT1"
    assert fp.beam_mode == "stripmap"
    assert len(fp.corners) == 4


def test_observe_ground_sensor_no_footprint():
    """A ground sensor (no orbit) observing a space target should leave footprint None.

    The footprint computation requires the actor to have an orbit; ground sensors don't,
    so the footprint field stays None on the track.
    """
    from spacesim.engine.orders import Order
    from spacesim.engine.entities import Sensor
    from spacesim.engine.geometry import GeoPoint

    world = _make_world_with_eo_satellite()
    # Add a ground radar placed directly below TGT1's current position for immediate access
    from spacesim.engine.propagator import ModeratePropagator
    from spacesim.engine.geometry import eci_to_ecef, ecef_to_geodetic
    prop = ModeratePropagator()
    r, _ = prop.rv(world.assets["TGT1"].orbit, 0)
    geo = ecef_to_geodetic(eci_to_ecef(r, 0))
    ground_sensor = Sensor(id="GND_RDR", owner="blue", kind="ground_radar",
                           location=GeoPoint(lat_deg=geo.lat_deg, lon_deg=geo.lon_deg, alt_m=0.0))
    world.sensors["GND_RDR"] = ground_sensor

    sim, osys = _sim_with_orders(world)
    order = osys.issue(Order(
        cell="blue", actor="GND_RDR", action="observe", target="TGT1",
        params={"intent": "characterize", "beam_mode": "wide_area"},
    ))
    assert order.status == "queued"
    sim.advance_to(order.earliest_window[0] + 1)
    track = world.track_for("blue", "TGT1")
    assert track is not None
    # Ground sensor has no orbit → footprint stays None
    assert track.last_footprint is None
