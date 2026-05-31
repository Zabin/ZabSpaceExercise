"""Cyber attack vector database and attribution scoring.

Pure computation — read-only previews for cyber orders.  Mirrors the ISR/jam pattern.

Vectors (how the payload reaches the target):
    rf             RF link injection (uplink command injection or downlink spoof)
    supply_chain   Pre-deployment compromise (firmware/ground software)
    insider        Authorized operator account misuse
    ground_segment Operator-station compromise (telemetry/command pipeline)

Payloads (what the access does):
    data_exfil     Read protected data; reversible (low blast radius)
    wiper          Destroy firmware/state; not reversible
    spoof          Inject false telemetry/commands; reversible until detected
    dwell          Establish persistence; long-tail callback
"""
from __future__ import annotations

import math
from typing import Optional


VECTORS: dict[str, dict] = {
    "rf":             {"base_success": 0.30, "attribution_bias": "ambiguous", "patchable": True,
                       "detect_rate": 0.40, "min_persistence_h": 0.5},
    "supply_chain":   {"base_success": 0.70, "attribution_bias": "covert",    "patchable": False,
                       "detect_rate": 0.10, "min_persistence_h": 24.0},
    "insider":        {"base_success": 0.55, "attribution_bias": "ambiguous", "patchable": True,
                       "detect_rate": 0.20, "min_persistence_h": 1.0},
    "ground_segment": {"base_success": 0.45, "attribution_bias": "ambiguous", "patchable": True,
                       "detect_rate": 0.30, "min_persistence_h": 2.0},
}

PAYLOADS: dict[str, dict] = {
    "data_exfil": {"reversible": True,  "escalation_weight": 2, "intended_outcome": "deceive"},
    "wiper":      {"reversible": False, "escalation_weight": 6, "intended_outcome": "destroy"},
    "spoof":      {"reversible": True,  "escalation_weight": 3, "intended_outcome": "deceive"},
    "dwell":      {"reversible": True,  "escalation_weight": 2, "intended_outcome": "degrade"},
}

POSTURE_FACTORS = {"low": 1.25, "medium": 1.00, "high": 0.65}


def vector_params(v: Optional[str]) -> tuple[dict, str]:
    name = v if (v and v in VECTORS) else "rf"
    return dict(VECTORS[name]), name


def payload_params(p: Optional[str]) -> tuple[dict, str]:
    name = p if (p and p in PAYLOADS) else "data_exfil"
    return dict(PAYLOADS[name]), name


def effective_success(vector: Optional[str], target_posture: str = "medium",
                       dwell_s: float = 0.0) -> float:
    """Probability the access succeeds given vector × posture × dwell time."""
    vp, _ = vector_params(vector)
    base = vp["base_success"] * POSTURE_FACTORS.get(target_posture, 1.0)
    # Each extra minute of dwell raises chance of success by 1% (capped at +30%)
    dwell_bonus = min(0.30, 0.01 * (max(0.0, dwell_s) / 60.0))
    return max(0.0, min(0.99, base + dwell_bonus))


def attribution_score(vector: Optional[str], dwell_s: float = 0.0,
                       persistence_h: float = 0.0) -> dict:
    """Compute (attribution risk, detect probability) — high attribution = easier to blame.

    Dwell time and persistence both raise both numbers; covert vectors (supply_chain)
    start with low detection.
    """
    vp, name = vector_params(vector)
    detect = vp["detect_rate"]
    # Long dwell + long persistence increase detection
    dwell_uplift = min(0.40, 0.05 * (dwell_s / 60.0))
    persist_uplift = min(0.30, 0.02 * persistence_h)
    detect_p = min(0.99, detect + dwell_uplift + persist_uplift)
    attribution = vp["attribution_bias"]
    return {"vector": name, "attribution_bias": attribution,
            "detect_prob": round(detect_p, 3),
            "min_persistence_h": vp["min_persistence_h"]}


def available_vectors() -> list[str]:
    return list(VECTORS.keys())


def available_payloads() -> list[str]:
    return list(PAYLOADS.keys())
