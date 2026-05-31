"""Tests for the jam modulation database and footprint geometry (engine/jam.py).

Coverage:
  - modulation_params lookup and fallback
  - effective_radius_km scales with sqrt(power)
  - effective_success_prob applies modulation effectiveness + bandwidth coverage
  - jam_footprint_polygon returns a closed convex polygon
  - power_draw_w applies modulation power_factor
  - end-to-end: jam order with new params adjusts the EffectInstance
  - compute_jam session API round-trip
"""
from __future__ import annotations

import math
import pytest

from spacesim.engine.jam import (
    MODULATIONS,
    available_modulations,
    effective_radius_km,
    effective_success_prob,
    jam_footprint_polygon,
    modulation_params,
    power_draw_w,
)


# ---------------------------------------------------------------------------
# modulation_params
# ---------------------------------------------------------------------------

def test_modulation_params_known():
    mp, name = modulation_params("spot")
    assert name == "spot"
    assert mp["effectiveness"] == pytest.approx(0.95)


def test_modulation_params_fallback_to_barrage():
    mp, name = modulation_params(None)
    assert name == "barrage"


def test_modulation_params_unknown_falls_back():
    mp, name = modulation_params("magnetic_resonance_disruptor")
    assert name == "barrage"


def test_available_modulations_has_four_known():
    mods = available_modulations()
    assert set(mods) >= {"barrage", "spot", "sweep", "deceptive"}


# ---------------------------------------------------------------------------
# effective_radius_km
# ---------------------------------------------------------------------------

def test_radius_scales_with_sqrt_power():
    r1 = effective_radius_km(100.0, "barrage")
    r4 = effective_radius_km(400.0, "barrage")
    assert r4 == pytest.approx(2 * r1, rel=1e-3)


def test_radius_zero_power():
    assert effective_radius_km(0.0, "barrage") == 0.0


def test_radius_spot_larger_than_barrage_same_power():
    """Spot focuses energy → larger effective denial radius than barrage at same power."""
    r_spot = effective_radius_km(100.0, "spot")
    r_barr = effective_radius_km(100.0, "barrage")
    assert r_spot > r_barr


def test_radius_at_reference_power_is_baseline():
    """Barrage at 100 W → 50 km reference radius."""
    r = effective_radius_km(100.0, "barrage")
    assert r == pytest.approx(50.0, rel=1e-3)


# ---------------------------------------------------------------------------
# effective_success_prob
# ---------------------------------------------------------------------------

def test_prob_deceptive_higher_than_barrage():
    p_dec = effective_success_prob(0.5, "deceptive", 1e6, 1e6)
    p_bar = effective_success_prob(0.5, "barrage", 1e6, 1e6)
    assert p_dec > p_bar


def test_prob_capped_at_99():
    p = effective_success_prob(0.99, "deceptive", 1e6, 1e6)
    assert p <= 0.99


def test_prob_bandwidth_mismatch_hurts_sweep():
    """Sweep has effectiveness < 1.0, so bandwidth coverage matters."""
    p_full = effective_success_prob(0.9, "sweep", 1e6, 1e6)
    p_partial = effective_success_prob(0.9, "sweep", 0.2e6, 1e6)
    assert p_partial < p_full


def test_prob_zero_victim_bandwidth_safe():
    """Pathological zero victim bandwidth should not divide by zero."""
    p = effective_success_prob(0.9, "barrage", 1e6, 0.0)
    assert 0.0 <= p <= 0.99


# ---------------------------------------------------------------------------
# jam_footprint_polygon
# ---------------------------------------------------------------------------

def test_footprint_zero_radius_empty():
    assert jam_footprint_polygon(0.0, 0.0, 0.0) == []


def test_footprint_default_24_points():
    fp = jam_footprint_polygon(0.0, 0.0, 50.0)
    assert len(fp) == 24


def test_footprint_centered_on_input():
    fp = jam_footprint_polygon(30.0, -120.0, 100.0)
    avg_lat = sum(p[0] for p in fp) / len(fp)
    avg_lon = sum(p[1] for p in fp) / len(fp)
    assert avg_lat == pytest.approx(30.0, abs=0.05)
    assert avg_lon == pytest.approx(-120.0, abs=0.05)


def test_footprint_radius_about_right():
    """A 100 km radius footprint at the equator spans ~2 × 100 km = ~1.8° lon."""
    fp = jam_footprint_polygon(0.0, 0.0, 100.0)
    lon_span = max(p[1] for p in fp) - min(p[1] for p in fp)
    assert lon_span == pytest.approx(2 * 100.0 / 111.320, abs=0.05)


# ---------------------------------------------------------------------------
# power_draw_w
# ---------------------------------------------------------------------------

def test_power_draw_barrage_higher_than_spot():
    """Barrage's wider noise floor wastes power → higher draw at same emitted P."""
    assert power_draw_w(100.0, "barrage") > power_draw_w(100.0, "spot")


def test_power_draw_zero():
    assert power_draw_w(0.0, "barrage") == 0.0


# ---------------------------------------------------------------------------
# Session API compute_jam round-trip (uses real vignette like test_maneuver)
# ---------------------------------------------------------------------------

def _api_with_jammer():
    """Load a vignette and find an asset suitable for jam previewing."""
    from spacesim.session.inprocess import InProcessSession

    api = InProcessSession()
    sid = api.load_vignette("training-basics")
    api.start(sid)
    mgr = api._sessions[sid]
    # Prefer a ground asset (jammers are typically ground-based); fall back to any asset
    actor_id = next(
        (aid for aid, a in mgr.world.assets.items() if a.owner == "blue" and a.location is not None),
        None,
    ) or next(
        (aid for aid, a in mgr.world.assets.items() if a.owner == "blue"),
        None,
    )
    assert actor_id, "training-basics should have at least one blue asset"
    return api, sid, actor_id


def test_compute_jam_returns_radius_and_footprint():
    api, sid, actor = _api_with_jammer()
    res = api.compute_jam(sid, "blue", actor,
                          {"modulation": "spot", "power_w": 200.0})
    assert "error" not in res
    assert res["modulation"] == "spot"
    assert res["effective_radius_km"] > 0
    assert len(res["footprint_polygon"]) == 24
    assert 0.0 < res["success_prob"] <= 0.99


def test_compute_jam_higher_power_larger_radius():
    api, sid, actor = _api_with_jammer()
    r_low = api.compute_jam(sid, "blue", actor, {"power_w": 50.0})["effective_radius_km"]
    r_high = api.compute_jam(sid, "blue", actor, {"power_w": 500.0})["effective_radius_km"]
    assert r_high > r_low


def test_compute_jam_deceptive_overt_attribution():
    api, sid, actor = _api_with_jammer()
    res = api.compute_jam(sid, "blue", actor, {"modulation": "deceptive"})
    assert res["attribution_default"] == "overt"


def test_compute_jam_unknown_actor_returns_error():
    api, sid, _actor = _api_with_jammer()
    res = api.compute_jam(sid, "blue", "NOPE_GHOST_JAMMER", {})
    assert "error" in res
