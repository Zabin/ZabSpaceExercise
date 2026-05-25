"""Phase 5.5: the render-from-custody belief scene (fog + growing/shrinking uncertainty)."""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.custody import Track, observe
from spacesim.engine.entities import Asset
from spacesim.engine.geometry import R_EARTH_EQ
from spacesim.engine.orbit import OrbitState
from spacesim.engine.simtime import minutes
from spacesim.session.manager import SessionManager
from spacesim.session.scene import build_scene
from spacesim.engine.world import WorldState


def test_scene_renders_own_assets_and_respects_fog():
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    blue = mgr.get_scene("blue")
    red = mgr.get_scene("red")
    blue_ids = {a.id for a in blue.assets}
    red_ids = {a.id for a in red.assets}
    assert "ISR-EO-1" in blue_ids                 # Blue draws its own satellite
    assert "ISR-EO-1" not in red_ids              # Red never sees Blue's assets
    assert "JAM-NORTH" in red_ids
    # Belief frame only: no enemy truth appears as an "asset" for either side.
    assert "JAM-NORTH" not in blue_ids


def test_track_uncertainty_grows_between_looks_and_collapses_on_report():
    sat = OrbitState(a_m=42_164e3, e=0.0, i_deg=0.0, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0)  # a GEO object
    world = WorldState(now=0)
    world.assets["HOSTILE"] = Asset(id="HOSTILE", owner="red", kind="satellite", orbit=sat)
    tr = Track(object="HOSTILE", owner="blue", last_observation=0, confidence=1.0,
               characterized=True, state_estimate=sat.model_copy(deep=True))
    world.tracks.append(tr)

    fresh = build_scene(world, "blue").tracks[0]
    assert fresh.uncertainty_km == 0.0

    world.now = minutes(40)                       # Blue stopped tasking → volume blooms
    grown = build_scene(world, "blue").tracks[0]
    assert grown.uncertainty_km > 0.0
    assert grown.confidence < 1.0

    observe(tr, world.now)                         # re-task an optical sensor → it snaps back
    snapped = build_scene(world, "blue").tracks[0]
    assert snapped.uncertainty_km == 0.0
    assert snapped.confidence == 1.0
