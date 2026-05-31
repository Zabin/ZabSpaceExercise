"""ISR beam mode database and footprint geometry.

Pure computation — no world state mutation.  Called by orders.py at observe-schedule time
to compute an effective gain (accounting for beam selection and off-nadir angle) and a
ground footprint polygon that is stored on the Track for 2-D map rendering.

Beam mode hierarchy:
    isr_eo  — electro-optical  (spotlight/stripmap/wide_area/scan)
    isr_sar — synthetic-aperture radar  (spotlight/fine/stripmap/wide_area/polarimetric)
    sda     — space domain awareness  (fine/nominal/wide_area)
"""
from __future__ import annotations

import math
from typing import Optional


# Beam mode look-up by payload type.
# -----------------------------------------------------------------------
#   swath_km     : cross-track swath width at nadir (km)
#   resolution_m : GSD (m) at nadir — degrades at high look angles
#   power_factor : relative power draw × baseline (affects SOC drain)
#   duty_cycle   : fraction of pass window the sensor can collect
#                  (thermal budget limit — a spotlight pass runs hot)
#   gain_factor  : confidence-gain multiplier vs. stripmap baseline 1.0
# -----------------------------------------------------------------------
BEAM_MODES: dict[str, dict[str, dict]] = {
    "isr_eo": {
        "wide_area":  {"swath_km": 100.0, "resolution_m": 10.0, "power_factor": 1.0,  "duty_cycle": 0.30, "gain_factor": 0.70},
        "stripmap":   {"swath_km":  30.0, "resolution_m":  3.0, "power_factor": 1.2,  "duty_cycle": 0.40, "gain_factor": 1.00},
        "spotlight":  {"swath_km":   5.0, "resolution_m":  0.5, "power_factor": 1.5,  "duty_cycle": 0.50, "gain_factor": 1.50},
        "scan":       {"swath_km": 400.0, "resolution_m": 30.0, "power_factor": 0.8,  "duty_cycle": 0.25, "gain_factor": 0.50},
    },
    "isr_sar": {
        "wide_area":    {"swath_km": 500.0, "resolution_m": 25.0, "power_factor": 1.2, "duty_cycle": 0.10, "gain_factor": 0.60},
        "stripmap":     {"swath_km":  25.0, "resolution_m":  3.0, "power_factor": 1.8, "duty_cycle": 0.15, "gain_factor": 1.00},
        "fine":         {"swath_km":  10.0, "resolution_m":  1.0, "power_factor": 2.0, "duty_cycle": 0.12, "gain_factor": 1.50},
        "spotlight":    {"swath_km":   4.0, "resolution_m":  0.3, "power_factor": 2.5, "duty_cycle": 0.08, "gain_factor": 1.80},
        "polarimetric": {"swath_km":  30.0, "resolution_m":  5.0, "power_factor": 2.5, "duty_cycle": 0.20, "gain_factor": 1.20},
    },
    "sda": {
        "wide_area": {"swath_km": 2000.0, "resolution_m": 1000.0, "power_factor": 0.8, "duty_cycle": 0.60, "gain_factor": 0.60},
        "nominal":   {"swath_km":  500.0, "resolution_m":  500.0, "power_factor": 1.0, "duty_cycle": 0.80, "gain_factor": 1.00},
        "fine":      {"swath_km":  100.0, "resolution_m":  100.0, "power_factor": 1.5, "duty_cycle": 0.50, "gain_factor": 1.80},
    },
}

_DEFAULT_MODE: dict[str, str] = {
    "isr_eo": "stripmap",
    "isr_sar": "stripmap",
    "sda": "nominal",
}

# Base SoC drain for a full-duty 300-second stripmap pass on a healthy bus.
_BASE_SOC_DRAIN = 0.05


def beam_params(payload_type: str, beam_mode: Optional[str] = None) -> tuple[dict, str]:
    """Return (params_dict, resolved_mode_name) for the given payload type and requested mode.

    Falls back to the payload type's default mode if beam_mode is None or unrecognized.
    Falls back to generic EO stripmap params if the payload type is unknown.
    """
    modes = BEAM_MODES.get(payload_type) or BEAM_MODES.get("isr_eo", {})
    default = _DEFAULT_MODE.get(payload_type, "stripmap")
    resolved = beam_mode if (beam_mode and beam_mode in modes) else default
    params = dict(modes.get(resolved) or modes.get(default) or next(iter(modes.values()),
        {"swath_km": 30.0, "resolution_m": 3.0, "power_factor": 1.0, "duty_cycle": 0.40, "gain_factor": 1.0}))
    return params, resolved


def available_modes(payload_type: str) -> list[str]:
    """List the beam mode names available for a payload type."""
    return list(BEAM_MODES.get(payload_type, BEAM_MODES["isr_eo"]).keys())


def effective_gain(base_gain: float, look_angle_deg: float, bp: dict) -> float:
    """Compute confidence-gain adjusted for beam-mode and off-nadir angle.

    EO: off-nadir degrades resolution and thus gain (cosine weighting).
    SAR: look angle is required for operation; little gain penalty within ±45°.
    The caller passes the per-mode gain_factor; look-angle penalty applies to both.
    """
    look_rad = math.radians(max(0.0, min(45.0, look_angle_deg)))
    angle_factor = math.cos(look_rad)        # 1.0 at nadir, 0.707 at 45°
    return base_gain * bp["gain_factor"] * angle_factor


def soc_drain(bp: dict, duration_s: float) -> float:
    """Estimate battery SoC drain for an ISR collection of given duration.

    Scales _BASE_SOC_DRAIN by power_factor and duration relative to the 300-second baseline.
    Returns a positive fraction to subtract from battery_soc.
    """
    return _BASE_SOC_DRAIN * bp["power_factor"] * max(0.0, duration_s) / 300.0


def ground_heading_deg(orbit, t_us: int, prop) -> float:
    """Approximate ground-track heading (degrees clockwise from north) via finite difference.

    Propagates 30 seconds forward and computes the azimuth between the two sub-satellite
    points.  Accurate to ±0.5° for LEO; handles the antimeridian crossing gracefully.
    """
    from spacesim.engine.geometry import eci_to_ecef, ecef_to_geodetic

    dt = 30_000_000  # 30 s in microseconds
    r1, _ = prop.rv(orbit, t_us)
    r2, _ = prop.rv(orbit, t_us + dt)
    g1 = ecef_to_geodetic(eci_to_ecef(r1, t_us))
    g2 = ecef_to_geodetic(eci_to_ecef(r2, t_us + dt))
    dlat = g2.lat_deg - g1.lat_deg
    dlon = g2.lon_deg - g1.lon_deg
    if dlon > 180:
        dlon -= 360
    if dlon < -180:
        dlon += 360
    cos_lat = math.cos(math.radians(g1.lat_deg))
    return math.degrees(math.atan2(dlon * cos_lat, dlat)) % 360.0


def footprint_polygon(
    lat_deg: float,
    lon_deg: float,
    alt_m: float,
    heading_deg: float,
    bp: dict,
    look_angle_deg: float = 0.0,
) -> list[list[float]]:
    """Compute a 4-corner collection footprint in geographic coordinates.

    The footprint is modelled as a rectangle on the surface:
      - Along-track length = effective swath width (roughly square)
      - Cross-track swath shrinks with off-nadir angle (EO-style cosine roll-off)
      - Center of footprint is offset cross-track by alt × tan(look_angle)

    heading_deg : azimuth of satellite ground track (0 = north, 90 = east).
    look_angle_deg : off-nadir look angle to the right of the flight direction (0–45°).

    Returns a list of 4 [lat_deg, lon_deg] corners in clockwise order starting front-left:
        [front-left, front-right, rear-right, rear-left]
    """
    alt_km = alt_m / 1000.0
    look_rad = math.radians(max(0.0, min(45.0, look_angle_deg)))
    head_rad = math.radians(heading_deg)

    eff_swath_km = bp["swath_km"] * math.cos(look_rad)
    eff_along_km = eff_swath_km          # square footprint (extendable)
    ct_offset_km = alt_km * math.tan(look_rad)  # shift center right of ground track

    # Flat-Earth linear unit conversions (valid for ≲500 km footprints)
    km_per_deg_lat = 111.320
    km_per_deg_lon = 111.320 * math.cos(math.radians(lat_deg)) + 1e-12

    # Along-track unit vector (direction of satellite motion)
    fwd_dlat = math.cos(head_rad) / km_per_deg_lat
    fwd_dlon = math.sin(head_rad) / km_per_deg_lon
    # Right-of-track (perpendicular, 90° clockwise from heading)
    rt_dlat = -math.sin(head_rad) / km_per_deg_lat
    rt_dlon = math.cos(head_rad) / km_per_deg_lon

    # Footprint center shifted to the right by the look-angle offset
    ctr_lat = lat_deg + ct_offset_km * rt_dlat
    ctr_lon = lon_deg + ct_offset_km * rt_dlon

    half_s = eff_swath_km / 2.0
    half_a = eff_along_km / 2.0
    corners = []
    for da, ds in [(half_a, -half_s), (half_a, half_s), (-half_a, half_s), (-half_a, -half_s)]:
        corners.append([
            round(ctr_lat + da * fwd_dlat + ds * rt_dlat, 4),
            round(ctr_lon + da * fwd_dlon + ds * rt_dlon, 4),
        ])
    return corners
