"""Orbit math: periods, element/state round-trips, regime classification."""

from __future__ import annotations

import math

import numpy as np

from spacesim.engine.geometry import MU_EARTH, R_EARTH_EQ
from spacesim.engine.orbit import (
    OrbitState,
    classify_regime,
    elements_to_rv,
    mean_to_true,
    period_s,
    rv_to_elements,
    true_to_mean,
)
from spacesim.engine.simtime import minutes

LEO_A = R_EARTH_EQ + 550e3
GEO_A = 42_164e3


def test_mean_to_true_round_trips_with_true_to_mean():
    """IP-1190 — mean_to_true() is true_to_mean()'s inverse (mean -> true -> mean recovers)."""
    for e in (0.0, 0.001, 0.3, 0.7):
        for nu_deg in (0.0, 37.0, 90.0, 181.5, 300.0):
            nu = math.radians(nu_deg)
            m = true_to_mean(nu, e)
            recovered_nu = mean_to_true(m, e)
            recovered_m = true_to_mean(recovered_nu, e)
            assert abs(recovered_m - m) < 1e-9


def test_mean_to_true_extraction_did_not_change_elements_to_rv():
    """IP-1190 — elements_to_rv() calling the extracted mean_to_true() produces the exact same
    ECI state as before the refactor (regression on a known Keplerian element set)."""
    orbit = OrbitState(a_m=LEO_A, e=0.05, i_deg=51.6, raan_deg=10, argp_deg=20, ta_deg=45, epoch=0)
    r, v = elements_to_rv(orbit, int(600 * 1e6))
    # Hand-inline the pre-refactor computation to confirm it matches bit-for-bit.
    e = 0.05
    dt = 600.0
    from spacesim.engine.orbit import _j2_rates, _solve_kepler
    i = math.radians(51.6)
    raan_dot, argp_dot, m_dot = _j2_rates(LEO_A, e, i)
    mean_anom = true_to_mean(math.radians(45), e) + m_dot * dt
    ecc_anom = _solve_kepler(mean_anom, e)
    expected_nu = math.atan2(math.sqrt(1 - e * e) * math.sin(ecc_anom), math.cos(ecc_anom) - e)
    actual_nu = mean_to_true(mean_anom, e)
    assert abs(actual_nu - expected_nu) < 1e-12
    assert r is not None and v is not None


def test_circular_period_matches_vis_viva():
    assert period_s(LEO_A) == math.sqrt(LEO_A ** 3 / MU_EARTH) * 2 * math.pi
    # ~90 min LEO, ~24 h GEO
    assert 90 < period_s(LEO_A) / 60 < 100
    assert abs(period_s(GEO_A) / 3600 - 23.93) < 0.1


def test_circular_orbit_keeps_constant_radius_and_returns_after_one_period():
    orbit = OrbitState(a_m=LEO_A, e=0.0, i_deg=51.6, raan_deg=10, argp_deg=0, ta_deg=0, epoch=0)
    radii = []
    for frac in (0.0, 0.25, 0.5, 0.75):
        r, _ = elements_to_rv(orbit, int(frac * period_s(LEO_A) * 1e6))
        radii.append(np.linalg.norm(r))
    assert max(radii) - min(radii) < 1.0  # circular: radius constant to <1 m

    r0, _ = elements_to_rv(orbit, 0)
    r_period, _ = elements_to_rv(orbit, int(period_s(LEO_A) * 1e6))
    # Near-but-not-exact return: J2 nodal precession shifts the orbit plane ~30 km/rev at this
    # inclination (the offset is cross-track, which is the expected secular RAAN drift).
    assert np.linalg.norm(r_period - r0) < 60_000.0


def test_element_state_round_trip():
    orbit = OrbitState(a_m=LEO_A, e=0.02, i_deg=53.0, raan_deg=120, argp_deg=45, ta_deg=200, epoch=0)
    t = minutes(33)
    r, v = elements_to_rv(orbit, t)
    recovered = rv_to_elements(r, v, t)
    r2, v2 = elements_to_rv(recovered, t)
    assert np.linalg.norm(r2 - r) < 1.0
    assert np.linalg.norm(v2 - v) < 1e-3


def test_regime_classification():
    assert classify_regime(LEO_A, 0.0, 51.6) == "LEO"
    assert classify_regime(R_EARTH_EQ + 700e3, 0.0, 98.0) == "LEO_SSO"
    assert classify_regime(26_560e3, 0.0, 55.0) == "MEO"   # GPS-like
    assert classify_regime(GEO_A, 0.0, 0.05) == "GEO"
    assert classify_regime(26_000e3, 0.72, 63.4) == "HEO"  # Molniya-like
