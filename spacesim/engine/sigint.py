"""SIGINT collection: band/dwell/intercept-mode database and geolocation accuracy model.

Mirrors `engine/isr.py` for the SIGINT payload type.  Pure computation — used to
preview a SIGINT collection's expected accuracy + power before the operator commits.

Modes:
    scan      Survey a wide band for hostile emitters; lowest accuracy, lowest power
    track     Lock onto a known emitter; modest dwell, medium accuracy
    geolocate Phase-difference / TDOA fix on an emitter; highest dwell + power
"""
from __future__ import annotations

import math
from typing import Optional


BANDS: dict[str, dict] = {
    "UHF": {"freq_ghz": 0.3,  "noise_factor": 1.20, "atmos_loss_db": 0.1},
    "L":   {"freq_ghz": 1.5,  "noise_factor": 1.00, "atmos_loss_db": 0.2},
    "S":   {"freq_ghz": 3.0,  "noise_factor": 1.00, "atmos_loss_db": 0.4},
    "X":   {"freq_ghz": 10.0, "noise_factor": 1.05, "atmos_loss_db": 0.8},
    "Ku":  {"freq_ghz": 14.0, "noise_factor": 1.10, "atmos_loss_db": 1.5},
    "Ka":  {"freq_ghz": 30.0, "noise_factor": 1.20, "atmos_loss_db": 3.0},
    "W":   {"freq_ghz": 90.0, "noise_factor": 1.50, "atmos_loss_db": 8.0},
}

MODES: dict[str, dict] = {
    "scan":      {"dwell_s_default":  10.0, "power_factor": 0.7, "accuracy_factor": 0.3},
    "track":     {"dwell_s_default":  60.0, "power_factor": 1.0, "accuracy_factor": 0.7},
    "geolocate": {"dwell_s_default": 180.0, "power_factor": 1.5, "accuracy_factor": 1.0},
}

_REF_GEOLOC_KM = 1.5    # baseline 1-σ geolocation error at L-band, 180 s dwell, single sat


def band_params(band: Optional[str]) -> tuple[dict, str]:
    name = band if (band and band in BANDS) else "L"
    return dict(BANDS[name]), name


def mode_params(mode: Optional[str]) -> tuple[dict, str]:
    name = mode if (mode and mode in MODES) else "track"
    return dict(MODES[name]), name


def geolocation_error_km(band: Optional[str], mode: Optional[str],
                          dwell_s: float, n_collectors: int = 1) -> float:
    """1-σ emitter geolocation error in km.

    Improves with √dwell (more samples) and √N (multilateration baselines), degrades
    with frequency-dependent atmospheric loss and band noise factor.
    """
    bp, _ = band_params(band)
    mp, _ = mode_params(mode)
    dwell_factor = math.sqrt(max(1.0, 180.0 / max(1.0, dwell_s)))    # ↑ if dwell shorter
    baseline_factor = 1.0 / math.sqrt(max(1, n_collectors))           # ↓ with N sats
    err = _REF_GEOLOC_KM * bp["noise_factor"] * dwell_factor * baseline_factor
    err *= (1.0 + bp["atmos_loss_db"] / 10.0)
    err /= max(0.1, mp["accuracy_factor"])
    return round(err, 2)


def soc_drain(mode: Optional[str], duration_s: float) -> float:
    """Battery SoC drain per collection (mirror of isr.soc_drain)."""
    mp, _ = mode_params(mode)
    return 0.04 * mp["power_factor"] * max(0.0, duration_s) / 60.0


def available_bands() -> list[str]:
    return list(BANDS.keys())


def available_modes() -> list[str]:
    return list(MODES.keys())
