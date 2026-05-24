"""Propagator + frame-conversion checks (overhead geometry, ground track, impulsive burn)."""

from __future__ import annotations

import numpy as np

from spacesim.engine.geometry import (
    GeoPoint,
    R_EARTH_EQ,
    ecef_to_geodetic,
    eci_to_ecef,
    look_angles,
)
from spacesim.engine.orbit import OrbitState
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simtime import minutes

LEO_A = R_EARTH_EQ + 550e3


def test_satellite_directly_overhead_has_elevation_90():
    prop = ModeratePropagator()
    orbit = OrbitState(a_m=LEO_A, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=120, epoch=0)
    t = minutes(17)
    r, _ = prop.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    station = GeoPoint(lat_deg=g.lat_deg, lon_deg=g.lon_deg, alt_m=0.0)  # ground point below the sat
    el, _, rng = look_angles(station, r, t)
    assert el > 89.5  # essentially straight up
    assert abs(rng - (np.linalg.norm(r) - R_EARTH_EQ)) < 50_000  # range ≈ altitude when overhead


def test_ground_track_altitude_is_orbital_altitude():
    prop = ModeratePropagator()
    orbit = OrbitState(a_m=LEO_A, e=0.0, i_deg=51.6, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0)
    track = prop.ground_track(orbit, 0, minutes(95) * 1, step_s=60.0)
    alts = [p.alt_m for p in track]
    assert all(abs(a - 550e3) < 30e3 for a in alts)  # ~550 km throughout
    lats = [p.lat_deg for p in track]
    assert max(lats) <= 52.0 and min(lats) >= -52.0  # inclination bounds latitude


def test_prograde_impulse_raises_orbit():
    prop = ModeratePropagator()
    orbit = OrbitState(a_m=LEO_A, e=0.0, i_deg=51.6, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0)
    t = minutes(10)
    _, v = prop.rv(orbit, t)
    dv = 50.0 * v / np.linalg.norm(v)  # 50 m/s prograde
    raised = prop.apply_impulse(orbit, dv, t)
    assert raised.a_m > orbit.a_m            # semi-major axis grew
    assert raised.a_m * (1 + raised.e) - R_EARTH_EQ > 550e3 + 100e3  # apogee lifted
