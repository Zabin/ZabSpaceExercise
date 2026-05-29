"""Lightweight entities the AccessProvider geometry needs (subset of ``04-data-model.md`` §3).

Kept minimal and standalone for Phase 2 (orbits & windows). The full ``Asset`` model — resources,
posture, bus/payload state — is layered on in later phases; these are the spatial primitives.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from spacesim.engine.bus import BusState, PayloadState
from spacesim.engine.geometry import GeoPoint
from spacesim.engine.orbit import OrbitState


class AssetResources(BaseModel):
    delta_v_ms: float = 0.0   # remaining maneuver budget (satellites)
    power_w: float = 0.0
    ammo: int = 0             # interceptors / kinetic effectors


class Asset(BaseModel):
    """A commandable entity (subset of ``04-data-model.md`` §3 used through Phase 3)."""

    id: str
    owner: Literal["blue", "red", "neutral"] = "neutral"
    kind: str = "satellite"   # satellite|ground_station|sensor|jammer|interceptor|directed_energy|...
    orbit: Optional[OrbitState] = None
    location: Optional[GeoPoint] = None
    elevation_mask_deg: float = 5.0
    resources: AssetResources = Field(default_factory=AssetResources)
    health: Literal["nominal", "degraded", "destroyed"] = "nominal"
    hardening: float = 0.0    # passive defense 0..1; lowers safe-mode susceptibility
    cyber_posture: Literal["low", "medium", "high"] = "medium"
    cyber_vulnerabilities: list[dict] = Field(default_factory=list)  # {vector, patchable, patched}
    bus_state: Optional[BusState] = None
    payload_state: Optional[PayloadState] = None
    isl_capable: bool = False          # can relay commands to peers via crosslink
    isl_peers: list[str] = Field(default_factory=list)
    stored_program: bool = True        # accepts time/condition-triggered onboard commands
    threat_warning: bool = False       # def.set_threat_warning posture (informational)

    def as_ground_site(self) -> "GroundSite":
        if self.location is None:
            raise ValueError(f"asset {self.id} has no location")
        return GroundSite(id=self.id, location=self.location, elevation_mask_deg=self.elevation_mask_deg)


class GroundSite(BaseModel):
    """Any fixed surface location with a horizon mask: station, jammer, launch site, user area."""

    id: str
    location: GeoPoint
    elevation_mask_deg: float = 5.0


class Sensor(BaseModel):
    id: str
    owner: Literal["blue", "red", "neutral"] = "neutral"
    kind: Literal["ground_radar", "ground_optical", "space_based"] = "ground_radar"
    location: Optional[GeoPoint] = None  # ground sensors
    orbit: Optional[OrbitState] = None   # space-based sensors
    elevation_mask_deg: float = 5.0
    needs_lighting: bool = False         # optical: target sunlit + site in darkness
    max_range_m: Optional[float] = None  # None = unlimited (geometry only)
