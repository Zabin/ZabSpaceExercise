"""Lightweight entities the AccessProvider geometry needs (subset of ``04-data-model.md`` §3).

Kept minimal and standalone for Phase 2 (orbits & windows). The full ``Asset`` model — resources,
posture, bus/payload state — is layered on in later phases; these are the spatial primitives.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

from spacesim.engine.geometry import GeoPoint
from spacesim.engine.orbit import OrbitState


class GroundSite(BaseModel):
    """Any fixed surface location with a horizon mask: station, jammer, launch site, user area."""

    id: str
    location: GeoPoint
    elevation_mask_deg: float = 5.0


class Sensor(BaseModel):
    id: str
    kind: Literal["ground_radar", "ground_optical", "space_based"] = "ground_radar"
    location: Optional[GeoPoint] = None  # ground sensors
    orbit: Optional[OrbitState] = None   # space-based sensors
    elevation_mask_deg: float = 5.0
    needs_lighting: bool = False         # optical: target sunlit + site in darkness
    max_range_m: Optional[float] = None  # None = unlimited (geometry only)
