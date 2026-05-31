"""Engage (kinetic) targeting math — pure read-only previews for the engage order.

Computes closing geometry (relative velocity, closest-approach miss distance, intercept
time-of-flight) so the UI can show the operator what's about to happen *before* they
commit a one-way kinetic effect.

Engagement parameter additions (over the v1 baseline):
    salvo_n           int   — number of interceptors fired in this engagement (1..N)
    abort_after_s     float — abort if not within `abort_distance_m` by this time
    abort_distance_m  float — miss-distance threshold for abort
    interceptor_dv    float — Δv budget of each interceptor (m/s); higher = better Pₖ
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np


def closing_geometry(r_a: np.ndarray, v_a: np.ndarray,
                      r_b: np.ndarray, v_b: np.ndarray) -> dict:
    """Two-body closing-state snapshot used by intercept previews.

    Returns:
        range_km        — current separation (km)
        range_rate_kms  — range derivative (km/s; negative = closing)
        closing_speed_kms — magnitude of relative velocity (km/s)
        t_close_s       — predicted time to closest approach (s; ∞ if diverging)
        miss_km         — predicted minimum separation if no thrust applied
    """
    dr = r_b - r_a
    dv = v_b - v_a
    range_m = float(np.linalg.norm(dr))
    speed_m_s = float(np.linalg.norm(dv))
    if range_m == 0.0 or speed_m_s == 0.0:
        return {"range_km": 0.0, "range_rate_kms": 0.0,
                "closing_speed_kms": speed_m_s / 1000.0,
                "t_close_s": float("inf"), "miss_km": range_m / 1000.0}
    range_rate = float(np.dot(dr, dv) / range_m)  # m/s
    if range_rate >= 0:
        # Diverging — no future CA
        return {"range_km": range_m / 1000.0,
                "range_rate_kms": range_rate / 1000.0,
                "closing_speed_kms": speed_m_s / 1000.0,
                "t_close_s": float("inf"), "miss_km": range_m / 1000.0}
    # Time-to-CA in straight-line approximation: solve d/dt(|r + v·t|²) = 0
    t_ca = -float(np.dot(dr, dv) / (speed_m_s ** 2))
    if t_ca <= 0:
        return {"range_km": range_m / 1000.0,
                "range_rate_kms": range_rate / 1000.0,
                "closing_speed_kms": speed_m_s / 1000.0,
                "t_close_s": float("inf"), "miss_km": range_m / 1000.0}
    miss_m = float(np.linalg.norm(dr + dv * t_ca))
    return {"range_km": round(range_m / 1000.0, 2),
            "range_rate_kms": round(range_rate / 1000.0, 3),
            "closing_speed_kms": round(speed_m_s / 1000.0, 3),
            "t_close_s": round(t_ca, 1),
            "miss_km": round(miss_m / 1000.0, 3)}


def kill_probability(base_pk: float, miss_km: float, interceptor_dv_ms: float,
                      salvo_n: int = 1) -> float:
    """Estimate the achieved kill probability for a kinetic engagement.

    Increases with salvo size (independent shots), decreases with miss distance and
    falls if interceptor Δv is too low to close the geometry.  Capped at 0.99.
    """
    if interceptor_dv_ms < 50.0:
        capability = 0.3
    elif interceptor_dv_ms < 200.0:
        capability = 0.6
    else:
        capability = 1.0
    miss_penalty = math.exp(-max(0.0, miss_km) / 5.0)   # >5 km miss starts to hurt fast
    p_single = max(0.0, min(0.99, base_pk * capability * miss_penalty))
    if salvo_n <= 1:
        return round(p_single, 3)
    p_combined = 1.0 - (1.0 - p_single) ** max(1, int(salvo_n))
    return round(max(0.0, min(0.99, p_combined)), 3)


def debris_cone_estimate(miss_km: float, closing_speed_kms: float) -> dict:
    """Rough debris-cone forecast for a successful hypervelocity intercept.

    Energy ≈ ½ m v_rel² scales debris count linearly with v_rel² in this model.  Used
    only for the operator's situational awareness; full debris evolution happens in
    `engine/effects.py` if the engagement succeeds.
    """
    energy_factor = (closing_speed_kms ** 2) / 100.0   # baseline 10 km/s = 1.0
    fragments = max(50, int(500 * energy_factor))
    return {"fragments_est": fragments,
            "cone_half_angle_deg": round(min(45.0, 5.0 + 0.5 * closing_speed_kms), 1)}
