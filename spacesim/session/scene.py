"""Render-from-custody belief scene (``10-sda-3d-viewer.md``, ``05-cell-interfaces.md``).

Builds the geometry a cell is allowed to draw: its own assets at their true positions, and
other-side objects ONLY as tracks (the cell's belief) — each propagated from its last measured
state with an uncertainty volume that grows with time since the last observation. The 2D map and
the (v1.1) 3D globe are both pure consumers of this; ground truth never reaches Red/Blue here.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from spacesim.engine.geometry import ecef_to_geodetic, eci_to_ecef
from spacesim.engine.orbit import classify_regime
from spacesim.engine.propagator import ModeratePropagator


class RenderAsset(BaseModel):
    id: str
    kind: str
    lat_deg: float
    lon_deg: float
    alt_m: float
    regime: Optional[str] = None
    on_orbit: bool = True


class RenderTrack(BaseModel):
    object: str
    lat_deg: float
    lon_deg: float
    alt_m: float
    confidence: float
    uncertainty_km: float
    characterized: bool
    classification: str


class SceneView(BaseModel):
    cell: str
    now: int
    assets: list[RenderAsset] = Field(default_factory=list)
    tracks: list[RenderTrack] = Field(default_factory=list)


_PROP = ModeratePropagator()


def _geo(orbit, t):
    r, _ = _PROP.rv(orbit, t)
    return ecef_to_geodetic(eci_to_ecef(r, t))


def build_scene(world, cell: str) -> SceneView:
    now = world.now
    assets: list[RenderAsset] = []
    for a in world.assets.values():
        if a.owner != cell:
            continue
        if a.orbit is not None:
            g = _geo(a.orbit, now)
            regime = a.orbit.regime or (classify_regime(a.orbit.a_m, a.orbit.e or 0.0, a.orbit.i_deg or 0.0) if a.orbit.a_m else None)
            assets.append(RenderAsset(id=a.id, kind=a.kind, lat_deg=g.lat_deg, lon_deg=g.lon_deg,
                                      alt_m=g.alt_m, regime=regime, on_orbit=True))
        elif a.location is not None:
            assets.append(RenderAsset(id=a.id, kind=a.kind, lat_deg=a.location.lat_deg,
                                      lon_deg=a.location.lon_deg, alt_m=a.location.alt_m, on_orbit=False))

    tracks: list[RenderTrack] = []
    for t in world.tracks:
        if t.owner != cell or t.state_estimate is None:
            continue
        g = _geo(t.state_estimate, now)
        tracks.append(RenderTrack(
            object=t.object, lat_deg=g.lat_deg, lon_deg=g.lon_deg, alt_m=g.alt_m,
            confidence=round(t.current_confidence(now), 3),
            uncertainty_km=round(t.current_uncertainty_km(now), 2),
            characterized=t.characterized, classification=t.classification,
        ))
    return SceneView(cell=cell, now=now, assets=assets, tracks=tracks)
