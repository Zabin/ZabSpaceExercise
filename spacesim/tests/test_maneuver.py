"""Tests for spacesim/engine/maneuver.py — all six maneuver entry modes."""
from __future__ import annotations

import math

import numpy as np
import pytest

from spacesim.engine.geometry import MU_EARTH, R_EARTH_EQ
from spacesim.engine.maneuver import compute_maneuver, lvlh_frame, lvlh_to_eci
from spacesim.engine.orbit import OrbitState, elements_to_rv
from spacesim.engine.propagator import ModeratePropagator

PROP = ModeratePropagator()


def _leo_orbit(alt_km: float = 500.0, i_deg: float = 28.5) -> OrbitState:
    """Circular LEO orbit at the given altitude."""
    a_m = alt_km * 1000.0 + R_EARTH_EQ
    return OrbitState(source="kepler", epoch=0, a_m=a_m, e=0.0001,
                      i_deg=i_deg, raan_deg=45.0, argp_deg=90.0, ta_deg=0.0)


# ---------------------------------------------------------------------------
# LVLH frame helpers
# ---------------------------------------------------------------------------

def test_lvlh_frame_orthonormal():
    orbit = _leo_orbit()
    r, v = PROP.rv(orbit, 0)
    R_hat, T_hat, N_hat = lvlh_frame(r, v)
    for hat in (R_hat, T_hat, N_hat):
        assert abs(np.linalg.norm(hat) - 1.0) < 1e-10
    assert abs(np.dot(R_hat, T_hat)) < 1e-10
    assert abs(np.dot(R_hat, N_hat)) < 1e-10
    assert abs(np.dot(T_hat, N_hat)) < 1e-10


def test_lvlh_radial_is_outward():
    orbit = _leo_orbit()
    r, v = PROP.rv(orbit, 0)
    R_hat, _, _ = lvlh_frame(r, v)
    assert float(np.dot(r / np.linalg.norm(r), R_hat)) > 0.999


def test_lvlh_normal_aligns_with_angular_momentum():
    orbit = _leo_orbit()
    r, v = PROP.rv(orbit, 0)
    _, _, N_hat = lvlh_frame(r, v)
    h = np.cross(r, v)
    h_hat = h / np.linalg.norm(h)
    assert abs(float(np.dot(N_hat, h_hat)) - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# Mode: eci
# ---------------------------------------------------------------------------

def test_eci_mode_passthrough():
    orbit = _leo_orbit()
    dv_in = [1.0, 2.0, -3.0]
    res = compute_maneuver(orbit, "eci", {"dv": dv_in}, 0, PROP)
    assert res["dv"] == pytest.approx(dv_in, abs=1e-5)
    assert res["cost"] == pytest.approx(math.sqrt(1 + 4 + 9), abs=1e-3)
    assert res["second_burn"] is None


def test_eci_zero_dv_gives_same_orbit():
    orbit = _leo_orbit()
    res = compute_maneuver(orbit, "eci", {"dv": [0, 0, 0]}, 0, PROP)
    o = res["new_orbit"]
    assert abs(o["a_km"] - (orbit.a_m / 1000.0)) < 0.1


# ---------------------------------------------------------------------------
# Mode: lvlh
# ---------------------------------------------------------------------------

def test_lvlh_along_track_raises_energy():
    orbit = _leo_orbit(alt_km=400.0)
    # Prograde burn raises the orbit's semi-major axis.
    res_pos = compute_maneuver(orbit, "lvlh", {"dv_r": 0, "dv_t": 10.0, "dv_n": 0}, 0, PROP)
    res_neg = compute_maneuver(orbit, "lvlh", {"dv_r": 0, "dv_t": -10.0, "dv_n": 0}, 0, PROP)
    a_orig = orbit.a_m / 1000.0
    assert res_pos["new_orbit"]["a_km"] > a_orig
    assert res_neg["new_orbit"]["a_km"] < a_orig


def test_lvlh_normal_dv_parallel_to_orbit_normal():
    """The N-component burn must produce a dv aligned with the orbit angular momentum."""
    orbit = _leo_orbit(i_deg=28.5)
    r, v = PROP.rv(orbit, 0)
    _, _, n_hat = lvlh_frame(r, v)
    res = compute_maneuver(orbit, "lvlh", {"dv_r": 0, "dv_t": 0, "dv_n": 50.0}, 0, PROP)
    dv = np.array(res["dv"])
    # dv should be parallel to n_hat (allow sign flip)
    cos_angle = abs(float(np.dot(dv / np.linalg.norm(dv), n_hat)))
    assert cos_angle > 0.9999


def test_lvlh_normal_changes_inclination_at_node():
    """Normal burn at the ascending node (ta≈270° for argp=90°) changes inclination."""
    orbit = OrbitState(source="kepler", epoch=0, a_m=6871e3, e=0.0001,
                       i_deg=28.5, raan_deg=45.0, argp_deg=90.0, ta_deg=270.0)
    res = compute_maneuver(orbit, "lvlh", {"dv_r": 0, "dv_t": 0, "dv_n": 200.0}, 0, PROP)
    # At the node a 200 m/s normal burn produces a noticeable inclination shift.
    assert abs(res["new_orbit"]["i_deg"] - 28.5) > 0.5


def test_lvlh_radial_changes_eccentricity():
    orbit = _leo_orbit()
    res = compute_maneuver(orbit, "lvlh", {"dv_r": 20.0, "dv_t": 0, "dv_n": 0}, 0, PROP)
    assert res["new_orbit"]["e"] > orbit.e


def test_lvlh_eci_equivalence():
    """A purely-along-track LVLH burn equals the same magnitude in the v̂ direction."""
    orbit = _leo_orbit()
    r, v = PROP.rv(orbit, 0)
    _, T_hat, _ = lvlh_frame(r, v)
    expected_dv = 5.0 * T_hat

    res_lvlh = compute_maneuver(orbit, "lvlh", {"dv_t": 5.0}, 0, PROP)
    assert np.allclose(res_lvlh["dv"], expected_dv, atol=1e-5)


# ---------------------------------------------------------------------------
# Mode: finite_burn
# ---------------------------------------------------------------------------

def test_finite_burn_along_track():
    orbit = _leo_orbit()
    res = compute_maneuver(orbit, "finite_burn",
                           {"direction_r": 0, "direction_t": 1, "direction_n": 0,
                            "magnitude_ms": 10.0, "duration_s": 120.0},
                           0, PROP)
    assert res["cost"] == pytest.approx(10.0, rel=1e-4)
    assert res["duration_s"] == pytest.approx(120.0)


def test_finite_burn_normalises_direction():
    orbit = _leo_orbit()
    res_unit = compute_maneuver(orbit, "finite_burn",
                                {"direction_r": 0, "direction_t": 1, "direction_n": 0,
                                 "magnitude_ms": 5.0}, 0, PROP)
    res_scaled = compute_maneuver(orbit, "finite_burn",
                                  {"direction_r": 0, "direction_t": 100.0, "direction_n": 0,
                                   "magnitude_ms": 5.0}, 0, PROP)
    assert np.allclose(res_unit["dv"], res_scaled["dv"], atol=1e-5)


def test_finite_burn_zero_direction_raises():
    orbit = _leo_orbit()
    with pytest.raises(ValueError, match="zero"):
        compute_maneuver(orbit, "finite_burn",
                         {"direction_r": 0, "direction_t": 0, "direction_n": 0,
                          "magnitude_ms": 5.0}, 0, PROP)


# ---------------------------------------------------------------------------
# Mode: target_coe
# ---------------------------------------------------------------------------

def test_target_coe_same_orbit_zero_dv():
    """Targeting the current orbit should yield ~zero Δv."""
    orbit = _leo_orbit(alt_km=500.0, i_deg=28.5)
    res = compute_maneuver(orbit, "target_coe",
                           {"a_km": orbit.a_m / 1000.0,
                            "e": orbit.e,
                            "i_deg": orbit.i_deg},
                           0, PROP)
    assert res["cost"] < 0.01   # essentially zero


def test_target_coe_inclination_change_nonzero_at_equatorial_crossing():
    """Target-COE inclination change at the equatorial crossing (node) is non-zero."""
    # argp=0, ta=0 puts the satellite at the ascending node, where velocity has a z-component
    # that is sensitive to inclination.
    orbit = OrbitState(source="kepler", epoch=0, a_m=6871e3, e=0.0001,
                       i_deg=28.5, raan_deg=45.0, argp_deg=0.0, ta_deg=0.0)
    delta_i_deg = 5.0
    res = compute_maneuver(orbit, "target_coe", {"i_deg": 28.5 + delta_i_deg}, 0, PROP)
    assert res["cost"] > 10.0   # non-trivial burn required for 5° inclination change


def test_target_coe_partial_override():
    """Omitting elements should use current orbit defaults; specified elements are applied."""
    # Use argp=0 so inclination changes are visible at ta=0 (velocity has z component).
    orbit = OrbitState(source="kepler", epoch=0, a_m=6871e3, e=0.0001,
                       i_deg=28.5, raan_deg=45.0, argp_deg=0.0, ta_deg=0.0)
    # Only override e; other elements should stay the same.
    res = compute_maneuver(orbit, "target_coe", {"e": 0.05}, 0, PROP)
    # A large eccentricity change requires a non-trivial burn.
    assert res["cost"] > 1.0


# ---------------------------------------------------------------------------
# Mode: hohmann
# ---------------------------------------------------------------------------

def test_hohmann_raise_positive_dv1():
    orbit = _leo_orbit(alt_km=400.0)
    res = compute_maneuver(orbit, "hohmann", {"target_alt_km": 600.0}, 0, PROP)
    assert res["cost"] > 0
    assert res["second_burn"] is not None


def test_hohmann_lower_negative_dv1():
    orbit = _leo_orbit(alt_km=600.0)
    res = compute_maneuver(orbit, "hohmann", {"target_alt_km": 400.0}, 0, PROP)
    # Lowering orbit: first burn is retrograde (dv_t < 0 → cost > 0 but dv along -T)
    assert res["cost"] > 0
    assert res["second_burn"]["dv_t_ms"] < 0   # second burn also retrograde


def test_hohmann_second_burn_delay():
    orbit = _leo_orbit(alt_km=400.0)
    a_transfer = ((400e3 + R_EARTH_EQ) + (600e3 + R_EARTH_EQ)) / 2.0
    expected_delay = math.pi * math.sqrt(a_transfer ** 3 / MU_EARTH)
    res = compute_maneuver(orbit, "hohmann", {"target_alt_km": 600.0}, 0, PROP)
    assert abs(res["second_burn"]["delay_s"] - expected_delay) < 1.0


def test_hohmann_total_cost_matches_analytic():
    """Total Δv (burn1 + burn2) should match the textbook Hohmann formula."""
    alt1_km, alt2_km = 400.0, 600.0
    r1 = alt1_km * 1000.0 + R_EARTH_EQ
    r2 = alt2_km * 1000.0 + R_EARTH_EQ
    a_t = (r1 + r2) / 2.0
    dv1_expected = abs(math.sqrt(MU_EARTH * (2.0/r1 - 1.0/a_t)) - math.sqrt(MU_EARTH / r1))
    dv2_expected = abs(math.sqrt(MU_EARTH / r2) - math.sqrt(MU_EARTH * (2.0/r2 - 1.0/a_t)))

    orbit = _leo_orbit(alt_km=alt1_km)
    res = compute_maneuver(orbit, "hohmann", {"target_alt_km": alt2_km}, 0, PROP)
    # e=0.0001 introduces a small radial velocity component; allow 0.5 m/s tolerance.
    assert abs(res["cost"] - dv1_expected) < 0.5
    assert abs(res["second_burn"]["cost_ms"] - dv2_expected) < 0.5


def test_hohmann_same_altitude_raises():
    # Use a purely circular orbit (e=0) so current radius matches the nominal altitude exactly.
    orbit = OrbitState(source="kepler", epoch=0, a_m=6871e3, e=0.0,
                       i_deg=28.5, raan_deg=45.0, argp_deg=0.0, ta_deg=0.0)
    target_alt_km = (orbit.a_m - R_EARTH_EQ) / 1000.0  # exact same altitude
    with pytest.raises(ValueError, match="same"):
        compute_maneuver(orbit, "hohmann", {"target_alt_km": target_alt_km}, 0, PROP)


# ---------------------------------------------------------------------------
# Mode: plane_change
# ---------------------------------------------------------------------------

def test_plane_change_magnitude_formula():
    """Cost ≈ 2 v sin(Δi/2) — the classic textbook result."""
    orbit = _leo_orbit(alt_km=500.0)
    r, v = PROP.rv(orbit, 0)
    v_mag = float(np.linalg.norm(v))
    delta_i_deg = 5.0
    delta_i = math.radians(delta_i_deg)

    res = compute_maneuver(orbit, "plane_change", {"delta_i_deg": delta_i_deg}, 0, PROP)
    expected_cost = 2.0 * v_mag * math.sin(delta_i / 2.0)
    assert abs(res["cost"] - expected_cost) < 0.5   # within 0.5 m/s (position-dependent approx)


def test_plane_change_zero_delta_zero_dv():
    orbit = _leo_orbit()
    res = compute_maneuver(orbit, "plane_change", {"delta_i_deg": 0.0}, 0, PROP)
    assert res["cost"] < 1e-6


def test_plane_change_changes_inclination():
    # At the node (argp=0, ta=0) the inclination change is most effective.
    orbit = OrbitState(source="kepler", epoch=0, a_m=6871e3, e=0.0001,
                       i_deg=28.5, raan_deg=45.0, argp_deg=0.0, ta_deg=0.0)
    res = compute_maneuver(orbit, "plane_change", {"delta_i_deg": 10.0}, 0, PROP)
    # Inclination should have changed by at least 5 degrees.
    assert abs(res["new_orbit"]["i_deg"] - 28.5) > 5.0


def test_plane_change_negative_decreases_inclination():
    orbit = _leo_orbit(i_deg=30.0)
    res_pos = compute_maneuver(orbit, "plane_change", {"delta_i_deg": 5.0}, 0, PROP)
    res_neg = compute_maneuver(orbit, "plane_change", {"delta_i_deg": -5.0}, 0, PROP)
    assert res_pos["new_orbit"]["i_deg"] > 30.0 - 1.0
    assert res_neg["new_orbit"]["i_deg"] < 30.0 + 1.0


# ---------------------------------------------------------------------------
# Orbit preview output shape
# ---------------------------------------------------------------------------

def test_new_orbit_contains_required_keys():
    orbit = _leo_orbit()
    res = compute_maneuver(orbit, "eci", {"dv": [0, 5, 0]}, 0, PROP)
    for key in ("a_km", "e", "i_deg", "alt_periapsis_km", "alt_apoapsis_km", "regime"):
        assert key in res["new_orbit"], key


def test_new_orbit_regime_is_leo():
    orbit = _leo_orbit()
    res = compute_maneuver(orbit, "eci", {"dv": [0, 1, 0]}, 0, PROP)
    assert "LEO" in (res["new_orbit"]["regime"] or "")


# ---------------------------------------------------------------------------
# Server endpoint integration
# ---------------------------------------------------------------------------

def test_compute_maneuver_via_session():
    """Full round-trip through InProcessSession (no HTTP)."""
    from spacesim.content.vignette import load_vignette
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    sid = api.load_vignette("training-basics")
    api.start(sid)

    # Get an asset with an orbit.
    from spacesim.session.manager import SessionManager
    mgr: SessionManager = api._sessions[sid]
    asset_id = next(
        (aid for aid, a in mgr.world.assets.items() if a.orbit is not None),
        None
    )
    assert asset_id, "training-basics should have at least one satellite"

    res = api.compute_maneuver(sid, "blue", asset_id, "lvlh",
                               {"dv_r": 0, "dv_t": 10.0, "dv_n": 0})
    assert "error" not in res
    assert res["cost"] == pytest.approx(10.0, rel=1e-3)
    assert "new_orbit" in res


def test_compute_maneuver_unknown_mode_returns_error_via_session():
    """Unknown mode returns {"error": ...} at the session layer (errors are caught there)."""
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    sid = api.load_vignette("training-basics")
    api.start(sid)
    mgr = api._sessions[sid]
    asset_id = next(
        (aid for aid, a in mgr.world.assets.items() if a.orbit is not None), None
    )
    res = api.compute_maneuver(sid, "blue", asset_id, "bogus_mode", {})
    assert "error" in res
