"""Lean coverage for FUTURE-WORK §11 batch 11 features.

One test file covers items 2-11 + 17-18 since each item ships a small pure module + a
session API surface; broader UI behaviour is exercised by the existing web smoke tests.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from spacesim.engine import cyber, engage, perturbations, sigint, sun


# ---------------------------------------------------------------------------
# Item 2 — engage targeting math
# ---------------------------------------------------------------------------

def test_engage_closing_geometry_straight_on_approach():
    r_a = np.array([7_000_000.0, 0.0, 0.0])
    v_a = np.array([0.0, 7500.0, 0.0])
    r_b = np.array([7_000_000.0 + 20_000.0, 0.0, 0.0])  # 20 km ahead
    v_b = np.array([0.0, 7400.0, 0.0])                  # closing at 100 m/s
    geom = engage.closing_geometry(r_a, v_a, r_b, v_b)
    assert geom["range_km"] == pytest.approx(20.0, abs=0.1)
    # Range rate should be small (mostly perpendicular geometry)
    assert geom["closing_speed_kms"] == pytest.approx(0.1, abs=0.01)


def test_engage_pk_higher_with_salvo():
    pk1 = engage.kill_probability(0.6, miss_km=0.0, interceptor_dv_ms=300.0, salvo_n=1)
    pk3 = engage.kill_probability(0.6, miss_km=0.0, interceptor_dv_ms=300.0, salvo_n=3)
    assert pk3 > pk1


def test_engage_pk_capped_at_99():
    pk = engage.kill_probability(0.99, miss_km=0.0, interceptor_dv_ms=500.0, salvo_n=10)
    assert pk <= 0.99


def test_engage_pk_low_when_interceptor_underpowered():
    pk_low = engage.kill_probability(0.9, miss_km=0.0, interceptor_dv_ms=20.0)
    pk_high = engage.kill_probability(0.9, miss_km=0.0, interceptor_dv_ms=300.0)
    assert pk_low < pk_high


def test_engage_debris_cone_scales_with_velocity():
    d_low = engage.debris_cone_estimate(0.0, 5.0)
    d_high = engage.debris_cone_estimate(0.0, 15.0)
    assert d_high["fragments_est"] > d_low["fragments_est"]


# ---------------------------------------------------------------------------
# Item 3 — cyber vectors
# ---------------------------------------------------------------------------

def test_cyber_supply_chain_more_successful_than_rf():
    s_supply = cyber.effective_success("supply_chain", "medium", dwell_s=0.0)
    s_rf = cyber.effective_success("rf", "medium", dwell_s=0.0)
    assert s_supply > s_rf


def test_cyber_high_posture_reduces_success():
    s_low = cyber.effective_success("rf", "low")
    s_high = cyber.effective_success("rf", "high")
    assert s_low > s_high


def test_cyber_dwell_increases_success_capped():
    s_short = cyber.effective_success("rf", "medium", dwell_s=0.0)
    s_long = cyber.effective_success("rf", "medium", dwell_s=600.0)
    assert s_long > s_short
    assert s_long <= 0.99


def test_cyber_attribution_supply_chain_is_covert():
    attr = cyber.attribution_score("supply_chain", dwell_s=0.0, persistence_h=1.0)
    assert attr["attribution_bias"] == "covert"


def test_cyber_payloads_wiper_irreversible():
    pp, _ = cyber.payload_params("wiper")
    assert pp["reversible"] is False
    assert pp["escalation_weight"] > 3


# ---------------------------------------------------------------------------
# Item 6 — SIGINT geolocation accuracy
# ---------------------------------------------------------------------------

def test_sigint_longer_dwell_better_geoloc():
    e_short = sigint.geolocation_error_km("L", "geolocate", dwell_s=60.0)
    e_long = sigint.geolocation_error_km("L", "geolocate", dwell_s=600.0)
    assert e_long < e_short


def test_sigint_more_collectors_better_geoloc():
    e_one = sigint.geolocation_error_km("L", "geolocate", 180.0, n_collectors=1)
    e_four = sigint.geolocation_error_km("L", "geolocate", 180.0, n_collectors=4)
    assert e_four < e_one


def test_sigint_higher_freq_worse_geoloc():
    """Ka band has higher atmospheric loss than L band → worse geoloc."""
    e_L = sigint.geolocation_error_km("L", "geolocate", 180.0)
    e_Ka = sigint.geolocation_error_km("Ka", "geolocate", 180.0)
    assert e_Ka > e_L


def test_sigint_scan_mode_drains_less_than_geolocate():
    d_scan = sigint.soc_drain("scan", 60.0)
    d_geo = sigint.soc_drain("geolocate", 60.0)
    assert d_geo > d_scan


# ---------------------------------------------------------------------------
# Item 7 — atmospheric drag / decay
# ---------------------------------------------------------------------------

def test_atmospheric_density_decreases_with_altitude():
    rho_low = perturbations.atmospheric_density(200_000.0)
    rho_high = perturbations.atmospheric_density(800_000.0)
    assert rho_low > rho_high


def test_atmospheric_density_zero_above_1000km():
    assert perturbations.atmospheric_density(1_200_000.0) == 0.0


def test_drag_decay_negative_for_leo():
    """A LEO sat with positive ballistic coefficient should lose altitude over time."""
    decay = perturbations.secular_drag_decay(400_000.0, ballistic_coeff=0.01, dt_s=86400.0)
    assert decay < 0


def test_drag_acceleration_opposes_velocity():
    r = np.array([6_778_000.0, 0.0, 0.0])    # 400 km altitude
    v = np.array([0.0, 7670.0, 0.0])
    a = perturbations.drag_acceleration(r, v, ballistic_coeff=0.01)
    # Drag should be antiparallel to velocity (mostly negative y component)
    assert a[1] < 0


# ---------------------------------------------------------------------------
# Item 8 — J3/J4 perturbations
# ---------------------------------------------------------------------------

def test_j3_acceleration_nonzero_off_equator():
    r = np.array([6_778_000.0 * math.cos(math.radians(45)),
                  0.0,
                  6_778_000.0 * math.sin(math.radians(45))])
    a = perturbations.j3_acceleration(r)
    assert np.linalg.norm(a) > 0


def test_j4_acceleration_radial_direction():
    r = np.array([6_778_000.0, 0.0, 0.0])
    a = perturbations.j4_acceleration(r)
    # J4 contribution should be (close to) radial — purely along x for this position
    assert abs(a[1]) < abs(a[0])
    assert abs(a[2]) < abs(a[0])


# ---------------------------------------------------------------------------
# Item 9 — solar radiation pressure
# ---------------------------------------------------------------------------

def test_srp_zero_in_eclipse():
    r = np.array([7_000_000.0, 0.0, 0.0])
    sun_vec = np.array([1.0, 0.0, 0.0])
    a = perturbations.srp_acceleration(r, sun_vec, srp_area_m2=10.0, mass_kg=500.0,
                                       eclipse_fraction=0.0)
    assert np.linalg.norm(a) == 0.0


def test_srp_nonzero_when_sunlit():
    r = np.array([7_000_000.0, 0.0, 0.0])
    sun_vec = np.array([1.0, 0.0, 0.0])
    a = perturbations.srp_acceleration(r, sun_vec, srp_area_m2=10.0, mass_kg=500.0,
                                       eclipse_fraction=1.0)
    assert np.linalg.norm(a) > 0


def test_srp_scales_with_area():
    r = np.array([7_000_000.0, 0.0, 0.0])
    sun_vec = np.array([1.0, 0.0, 0.0])
    a1 = perturbations.srp_acceleration(r, sun_vec, srp_area_m2=10.0, mass_kg=500.0)
    a2 = perturbations.srp_acceleration(r, sun_vec, srp_area_m2=20.0, mass_kg=500.0)
    assert np.linalg.norm(a2) == pytest.approx(2 * np.linalg.norm(a1), rel=1e-6)


# ---------------------------------------------------------------------------
# Item 10 — penumbra / eclipse fraction
# ---------------------------------------------------------------------------

def test_eclipse_fraction_full_sunlight_on_sun_side():
    r_sat = np.array([1e7, 0.0, 0.0])
    # At t=0 the Sun is roughly in the +x direction (close to vernal equinox geometry)
    frac = sun.eclipse_fraction(r_sat, 0)
    # The satellite is on the same side as the Sun → fully sunlit
    assert frac == 1.0


def test_eclipse_fraction_zero_in_full_umbra():
    sun_vec = sun.sun_unit_eci(0)
    # Place sat directly behind Earth from the Sun (anti-sun) but inside Earth's umbra
    r_sat = -sun_vec * 7_000_000.0  # 7000 km on the anti-sun axis
    frac = sun.eclipse_fraction(r_sat, 0)
    assert frac == 0.0


def test_eclipse_fraction_in_range():
    """A few off-axis points behind Earth should land in [0, 1]."""
    sun_vec = sun.sun_unit_eci(0)
    for radial in [6_500_000.0, 7_000_000.0, 8_000_000.0]:
        for offset in [0.0, 3_000_000.0, 7_000_000.0]:
            # Build a perpendicular displacement
            perp = np.array([sun_vec[1], -sun_vec[0], 0.0])
            perp_norm = perp / np.linalg.norm(perp)
            r = -sun_vec * radial + perp_norm * offset
            frac = sun.eclipse_fraction(r, 0)
            assert 0.0 <= frac <= 1.0


# ---------------------------------------------------------------------------
# Item 17/18 — coaching + consequence preview via the session API
# ---------------------------------------------------------------------------

def _api_with_session():
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    sid = api.load_vignette("training-basics")
    api.start(sid)
    return api, sid


def test_coaching_notes_empty_by_default():
    api, sid = _api_with_session()
    notes = api.coaching_notes(sid, "blue")
    assert notes == []


def test_coaching_notes_respects_cell_filter():
    """Inject coaching notes directly on the vignette and verify the per-cell filter."""
    api, sid = _api_with_session()
    mgr = api._sessions[sid]
    mgr.vignette.coaching = [
        {"at_sim_t": None, "cell": "red", "title": "Red only", "body": "..."},
        {"at_sim_t": None, "cell": "blue", "title": "Blue only", "body": "..."},
        {"at_sim_t": None, "cell": "white", "title": "All cells", "body": "..."},
    ]
    blue = api.coaching_notes(sid, "blue")
    titles = sorted(n["title"] for n in blue)
    assert titles == ["All cells", "Blue only"]


def test_coaching_notes_time_filter():
    api, sid = _api_with_session()
    mgr = api._sessions[sid]
    future = mgr.world.now + 1_000_000_000
    mgr.vignette.coaching = [
        {"at_sim_t": 0, "cell": "blue", "title": "Past", "body": ""},
        {"at_sim_t": future, "cell": "blue", "title": "Future", "body": ""},
    ]
    notes = api.coaching_notes(sid, "blue")
    titles = [n["title"] for n in notes]
    assert "Past" in titles
    assert "Future" not in titles


def test_consequence_preview_kinetic_is_high():
    api, sid = _api_with_session()
    res = api.preview_consequence(sid, "blue", "engage", "RED-TGT", {})
    assert res["severity"] == "high"
    assert res["debris_risk"] == "high"
    assert res["reversible"] is False


def test_consequence_preview_observe_is_low():
    api, sid = _api_with_session()
    res = api.preview_consequence(sid, "blue", "observe", "RED-TGT", {})
    assert res["severity"] == "low"


def test_consequence_preview_cyber_wiper_irreversible():
    api, sid = _api_with_session()
    res = api.preview_consequence(sid, "blue", "cyber", "RED-TGT",
                                    {"payload": "wiper", "vector": "supply_chain"})
    assert res["reversible"] is False
    assert "irreversible" in " ".join(res["notes"]).lower()


# ---------------------------------------------------------------------------
# Compute endpoints round-trip — engage, cyber, sigint
# ---------------------------------------------------------------------------

def test_compute_engage_returns_geometry_and_pk():
    api, sid = _api_with_session()
    mgr = api._sessions[sid]
    orbital = [a for a in mgr.world.assets.values() if a.orbit is not None]
    if len(orbital) < 2:
        pytest.skip("need two orbital assets")
    a_id, b_id = orbital[0].id, orbital[1].id
    res = api.compute_engage(sid, "blue", a_id, b_id, {"salvo_n": 2})
    assert "error" not in res
    assert "kill_probability" in res
    assert "miss_km" in res
    assert res["salvo_n"] == 2


def test_compute_cyber_returns_attribution():
    api, sid = _api_with_session()
    mgr = api._sessions[sid]
    target = next(iter(mgr.world.assets), None)
    res = api.compute_cyber(sid, "blue", "any_actor", target,
                              {"vector": "rf", "payload": "spoof"})
    assert "error" not in res
    assert res["vector"] == "rf"
    assert res["attribution_default"] in ("covert", "ambiguous", "overt")


def test_compute_sigint_returns_geolocation_error():
    api, sid = _api_with_session()
    mgr = api._sessions[sid]
    actor = next(iter(mgr.world.assets), None)
    res = api.compute_sigint(sid, "blue", actor, {"band": "X", "intercept_mode": "geolocate"})
    assert "error" not in res
    assert res["geolocation_error_km"] > 0
    assert res["band"] == "X"
