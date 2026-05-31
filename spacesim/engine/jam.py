"""Jam command parameter database and footprint geometry.

Mirrors the ISR pattern (`engine/isr.py`): a pure computation module that lets the UI
preview a jamming order's effective footprint, denial level, and success probability
before the operator commits.  Read-only — no world state mutation.

Modulation database:
    barrage     — broadband noise across the full bandwidth; high power, easy to detect
    spot        — narrow notch at freq_center; efficient against a single victim channel
    sweep       — frequency-hopping noise; good against agile victims, ~70% effective
    deceptive   — replays/modifies the victim's own signal; very high effectiveness but
                  requires intercept first (planning cost) and is highly attributable

Effective jam radius is computed from the radar-equation form:
    R_km = sqrt(P_w / threshold_w_per_km2) × beam_gain × pattern_factor

where the threshold is implicitly captured by the modulation effectiveness.
"""
from __future__ import annotations

import math
from typing import Optional


# Modulation lookup.
# -----------------------------------------------------------------------
#   effectiveness     : success_prob multiplier (1.0 = baseline)
#   radius_factor     : effective radius scale vs baseline barrage
#   attribution_bias  : default attribution (deceptive ≫ spot ≫ barrage)
#   detectability     : 0..1 (1 = trivially detected)
#   power_factor      : relative draw to deliver the listed effectiveness
# -----------------------------------------------------------------------
MODULATIONS: dict[str, dict] = {
    "barrage":   {"effectiveness": 1.00, "radius_factor": 1.00, "attribution_bias": "ambiguous",
                  "detectability": 0.90, "power_factor": 1.20},
    "spot":      {"effectiveness": 0.95, "radius_factor": 1.15, "attribution_bias": "ambiguous",
                  "detectability": 0.50, "power_factor": 0.70},
    "sweep":     {"effectiveness": 0.70, "radius_factor": 0.90, "attribution_bias": "ambiguous",
                  "detectability": 0.75, "power_factor": 1.00},
    "deceptive": {"effectiveness": 1.30, "radius_factor": 0.85, "attribution_bias": "overt",
                  "detectability": 0.20, "power_factor": 0.85},
}

# Reference: barrage @ 100 W produces ~ 50 km effective denial radius for a typical
# uplink threshold.  Used purely for previews — actual effect resolution stays in
# effects.py / access.py.
_REF_POWER_W = 100.0
_REF_RADIUS_KM = 50.0


def modulation_params(mod: Optional[str]) -> tuple[dict, str]:
    """Return (params_dict, resolved_modulation_name).  Falls back to barrage."""
    resolved = mod if (mod and mod in MODULATIONS) else "barrage"
    return dict(MODULATIONS[resolved]), resolved


def effective_radius_km(power_w: float, mod: Optional[str] = None) -> float:
    """Compute the effective jam denial radius from transmit power and modulation.

    Uses the inverse-square-falloff form: doubling power increases radius by sqrt(2).
    Falls back to barrage if mod is unknown.
    """
    mp, _ = modulation_params(mod)
    if power_w <= 0:
        return 0.0
    return _REF_RADIUS_KM * math.sqrt(max(0.0, power_w) / _REF_POWER_W) * mp["radius_factor"]


def effective_success_prob(base_prob: float, mod: Optional[str] = None,
                            bandwidth_hz: float = 1e6, victim_bandwidth_hz: float = 1e6) -> float:
    """Adjust success probability by modulation effectiveness + bandwidth overlap.

    A spot jammer at narrow bandwidth covering only part of the victim's signal is less
    effective; a barrage jammer with wider bandwidth than the victim's signal wastes power
    but maintains coverage.
    """
    mp, _ = modulation_params(mod)
    if victim_bandwidth_hz <= 0:
        coverage = 1.0
    else:
        coverage = min(1.0, max(0.0, bandwidth_hz / victim_bandwidth_hz))
    # Spot/deceptive prefer narrow overlap; barrage/sweep prefer wide coverage
    weight = 1.0 if mp["effectiveness"] >= 1.0 else (0.6 + 0.4 * coverage)
    return max(0.0, min(0.99, base_prob * mp["effectiveness"] * weight))


def jam_footprint_polygon(
    lat_deg: float,
    lon_deg: float,
    radius_km: float,
    n_segments: int = 24,
) -> list[list[float]]:
    """Return the jam footprint as an `n_segments`-corner polygon (great-circle approximation).

    Used for 2-D map preview — the operator sees the affected ground area before issuing.
    Coordinates are [lat_deg, lon_deg] flat-Earth (good to ~1% at radii ≲ 500 km).
    """
    if radius_km <= 0:
        return []
    km_per_deg_lat = 111.320
    km_per_deg_lon = 111.320 * math.cos(math.radians(lat_deg)) + 1e-12
    pts: list[list[float]] = []
    for i in range(n_segments):
        ang = 2 * math.pi * i / n_segments
        dlat = (radius_km * math.cos(ang)) / km_per_deg_lat
        dlon = (radius_km * math.sin(ang)) / km_per_deg_lon
        pts.append([round(lat_deg + dlat, 4), round(lon_deg + dlon, 4)])
    return pts


def power_draw_w(power_w: float, mod: Optional[str] = None) -> float:
    """Effective transmitter draw including modulation power_factor (efficiency)."""
    mp, _ = modulation_params(mod)
    return max(0.0, power_w) * mp["power_factor"]


def available_modulations() -> list[str]:
    return list(MODULATIONS.keys())
