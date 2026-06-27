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

    Legacy interface — used by the read-only ``/engage/compute`` preview and the
    operator-typed `interceptor_dv_ms` path. The Phase-B audit replaced the order
    pipeline's call with ``kill_probability_from_class`` (the realism-grounded model
    sourced from the four DA-ASAT test records); this function is retained for the
    preview UI and the back-compat of the EffectInstance payload bake.
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


# Audit 2026-06 (Commands) §M2 — interceptor-class database (realism research §14).
# Sourced from the four open-source DA-ASAT test records:
#   SC-19 (2007, FY-1C at ~865 km),   Burnt Frost (2008, USA-193 at ~247 km),
#   Mission Shakti (2019, Microsat-R at ~283 km),  Nudol (2021, Cosmos 1408 at ~480 km).
# Each class encodes (a) what altitude regime it can physically reach, (b) a base Pk
# against a cooperative tracked non-maneuvering target, and (c) a salvo_correlation
# floor that captures the dominant failure mode (a bad track defeats every round
# identically; rounds are not fully independent). See docs/AUDIT-2026-06-COMMANDS.md.
INTERCEPTORS: dict[str, dict] = {
    # BMD adaptation (Aegis SM-3-class): very low LEO only; mature IR HTK seeker.
    "bmd_adapted": {
        "base_pk": 0.85, "max_alt_km": 600, "seeker": "ir_hit_to_kill",
        "flyout_s": 180, "divert_dv_ms": 300, "salvo_correlation": 0.30,
    },
    # MRBM-derived road-mobile KKV: mid-LEO reach (FY-1C, Microsat-R envelope).
    "mrbm_kkv": {
        "base_pk": 0.70, "max_alt_km": 1000, "seeker": "ir_hit_to_kill",
        "flyout_s": 300, "divert_dv_ms": 250, "salvo_correlation": 0.35,
    },
    # ABM-derived heavy (Nudol PL-19 class): all-LEO reach, larger booster.
    "abm_heavy": {
        "base_pk": 0.75, "max_alt_km": 2000, "seeker": "radar_ir_dual",
        "flyout_s": 420, "divert_dv_ms": 200, "salvo_correlation": 0.35,
    },
    # Co-orbital interceptor / grappler (SJ-21 / Burevestnik-style): no altitude
    # ceiling (it phases there); Pk per attempt set by RPO custody, not endgame
    # homing; optionally reversible (tow/grapple) — lower escalation than impact.
    "coorbital": {
        "base_pk": 0.60, "max_alt_km": None, "seeker": "rpo_optical",
        "flyout_s": None, "divert_dv_ms": 0, "salvo_correlation": 0.00,
        "reversible_option": True,
    },
}


def kill_probability_from_class(interceptor_class: str, *,
                                 target_alt_km: float = 0.0,
                                 salvo_n: int = 1,
                                 track_quality: float = 1.0,
                                 miss_km: float = 0.0) -> float:
    """Pₖ derived from interceptor class × altitude reach × track quality × salvo.

    Hard altitude ceiling: an engagement above the class's ``max_alt_km`` returns 0.
    Co-orbital classes (``max_alt_km=None``) have no ceiling.

    Salvo combination is the standard 1 - (1-p)^n with a correlated-failure cap
    (real salvos share track / target-maneuver / seeker failures, so the asymptote
    is well below 1). The realism research's recommended ~0.95 cap is enforced.
    """
    spec = INTERCEPTORS.get(interceptor_class)
    if spec is None:
        return 0.0
    max_alt = spec["max_alt_km"]
    if max_alt is not None and target_alt_km > max_alt:
        return 0.0
    base = spec["base_pk"] * max(0.0, min(1.0, track_quality))
    if miss_km > 0.0:
        base *= math.exp(-miss_km / 5.0)
    p_single = max(0.0, min(0.99, base))
    if salvo_n <= 1:
        return round(p_single, 3)
    # Correlated-failure floor: a fraction `rho` of rounds share fate (track / seeker
    # / target-maneuver failure modes); 1-rho of rounds are independent.
    rho = float(spec.get("salvo_correlation", 0.3))
    p_indep = 1.0 - (1.0 - p_single) ** max(1, int(salvo_n))
    p_combined = (1.0 - rho) * p_indep + rho * p_single
    return round(max(0.0, min(0.95, p_combined)), 3)


def available_interceptor_classes() -> list[str]:
    return list(INTERCEPTORS.keys())


def debris_cone_estimate(miss_km: float, closing_speed_kms: float,
                          target_mass_kg: float = 750.0,
                          target_alt_km: float = 500.0) -> dict:
    """Rough debris-cone forecast for a successful hypervelocity intercept.

    Tracked fragment count scales with target mass × closing speed² — calibrated against
    the open-source test record (FY-1C ~880 kg → ~3000 fragments at ~8 km/s closing;
    Cosmos 1408 ~2000 kg → ~1789 tracked at ~8 km/s closing). Persistence is dominated
    by altitude: low-300-km debris decays in months; 500+ km debris persists for decades.
    """
    energy_factor = (closing_speed_kms ** 2) / 81.0   # baseline 9 km/s = 1.0
    fragments = max(50, int(1.5 * max(100.0, target_mass_kg) * energy_factor))
    # Persistence regime: realism research §14 (Burnt Frost 247 km → weeks; FY-1C 865 km
    # → decades; Cosmos 1408 480 km → years-to-decades).
    if target_alt_km < 350:
        persistence = "weeks-to-months"
    elif target_alt_km < 600:
        persistence = "years-to-decades"
    else:
        persistence = "decades"
    return {"fragments_est": fragments,
            "cone_half_angle_deg": round(min(45.0, 5.0 + 0.5 * closing_speed_kms), 1),
            "persistence": persistence}
