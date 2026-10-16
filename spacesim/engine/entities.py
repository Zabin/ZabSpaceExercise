"""Lightweight entities the AccessProvider geometry needs (subset of ``04-data-model.md`` §3).

Kept minimal and standalone for Phase 2 (orbits & windows). The full ``Asset`` model — resources,
posture, bus/payload state — is layered on in later phases; these are the spatial primitives.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from spacesim.engine.bus import BusState, PayloadState
from spacesim.engine.geometry import GeoPoint
from spacesim.engine.orbit import OrbitState, Regime


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
    group: Optional[str] = None         # constellation / formation identifier (≤3 sats per group)
    civilian: bool = False              # FUTURE-WORK §10.D.16 — denying a civilian link raises political cost
    isl_capable: bool = False          # can relay commands to peers via crosslink
    isl_peers: list[str] = Field(default_factory=list)
    stored_program: bool = True        # accepts time/condition-triggered onboard commands
    threat_warning: bool = False       # def.set_threat_warning posture (informational)

    # FUTURE-WORK §10.C.12 — terrain-aware horizon: optional per-azimuth mask table.
    # Each entry: {az_min, az_max, mask_deg}. Azimuths in [0, 360); mask wins by first match.
    mask_table: list[dict] = Field(default_factory=list)

    def as_ground_site(self) -> "GroundSite":
        if self.location is None:
            raise ValueError(f"asset {self.id} has no location")
        return GroundSite(id=self.id, location=self.location,
                          elevation_mask_deg=self.elevation_mask_deg,
                          mask_table=list(self.mask_table))


class GroundSite(BaseModel):
    """Any fixed surface location with a horizon mask: station, jammer, launch site, user area."""

    id: str
    location: GeoPoint
    elevation_mask_deg: float = 5.0
    mask_table: list[dict] = Field(default_factory=list)  # see Asset.mask_table


class Sensor(BaseModel):
    id: str
    owner: Literal["blue", "red", "neutral"] = "neutral"
    kind: Literal["ground_radar", "ground_optical", "space_based"] = "ground_radar"
    location: Optional[GeoPoint] = None  # ground sensors
    orbit: Optional[OrbitState] = None   # space-based sensors
    elevation_mask_deg: float = 5.0
    needs_lighting: bool = False         # optical: target sunlit + site in darkness
    max_range_m: Optional[float] = None  # None = unlimited (geometry only)
    network: bool = False                # SSN member (request-only, not directly taskable)
    # IP-1062 (FR-4430) — the sensor_outage inject effect's target field. Additive; every
    # existing vignette's sensors have no `health` key in YAML, defaulting to "nominal" (zero
    # behavior change). Mirrors Asset.health's degraded/nominal pair (no "destroyed" state for
    # a sensor — outages are reversible, per the effect's own `restore` flag).
    health: Literal["nominal", "degraded"] = "nominal"
    # IP-1220 (FR-1610-FR-1660) — six additive, optional/default-absent sensor-modality fields.
    # A Sensor declaring none of these behaves exactly as before this package.
    beam_mode: Optional[str] = None            # FR-1610 — a key into engine/isr.py's BEAM_MODES
    exclusion_angle_deg: Optional[float] = None  # FR-1620 — ground-optical solar exclusion radius
    min_range_km: Optional[float] = None         # FR-1630 — space-based hard-reject range floor
    # FR-1630 — IP-1222 (BL-0214): typed as a Regime, so a misspelt band fails at load.
    altitude_band_affinity: Optional[Regime] = None
    requires_cue: bool = False                    # FR-1640 — tasking gated on an existing Track
    host_asset_id: Optional[str] = None           # FR-1660 — position follows this Asset's orbit
    # IP-1221 (FR-1670) — optional usable Sun-target-sensor phase-angle range (lo, hi) in degrees
    # for a passive-EO (needs_lighting) sensor; outside it the observation gain falls off
    # (engine/isr.py::phase_angle_factor). Absent = unaffected. R109 v1.3 §3.11's recommended
    # author values: (0, 90) ground-based, (0, 150) space-based — never an implicit default.
    usable_phase_angle_deg: Optional[tuple[float, float]] = None

    @model_validator(mode="after")
    def _check_usable_phase_angle(self) -> "Sensor":
        """IP-1221 Design Decisions 4-5 — a malformed range, or one on a sensor that is not
        passive EO (``needs_lighting``), is rejected at load rather than misbehaving at run time."""
        rng = self.usable_phase_angle_deg
        if rng is None:
            return self
        lo, hi = rng
        if not (0.0 <= lo <= hi <= 180.0):
            raise ValueError(f"usable_phase_angle_deg must satisfy 0 <= lo <= hi <= 180, got {rng!r}")
        if not self.needs_lighting:
            raise ValueError("usable_phase_angle_deg applies only to a passive-EO sensor "
                             "(needs_lighting: true)")
        return self

    @model_validator(mode="after")
    def _check_radar_beam_mode(self) -> "Sensor":
        """IP-1222 Design Decision 3 (BL-0212) — a ground radar's declared ``beam_mode`` must name
        a ``BEAM_MODES["ground_radar"]`` entry (``fence``/``dish``). Other sensor kinds are not
        checked: their table depends on the dual-registered asset's payload type."""
        if self.kind == "ground_radar" and self.beam_mode is not None:
            from spacesim.engine.isr import BEAM_MODES
            modes = BEAM_MODES["ground_radar"]
            if self.beam_mode not in modes:
                raise ValueError(f"ground_radar beam_mode must be one of {sorted(modes)}, "
                                 f"got {self.beam_mode!r}")
        return self
