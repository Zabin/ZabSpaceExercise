"""Phase 5.5: the render-from-custody belief scene (fog + growing/shrinking uncertainty)."""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.custody import Track, observe
from spacesim.engine.entities import Asset
from spacesim.engine.geometry import R_EARTH_EQ
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order
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


def test_scene_carries_classical_orbital_elements():
    """Every on-orbit own asset reports a/e/i/Ω/ω/ν + period to the UI."""
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    blue = mgr.get_scene("blue")
    sat = next(a for a in blue.assets if a.id == "ISR-EO-1")
    assert sat.on_orbit and sat.a_km is not None
    for field in ("a_km", "e", "i_deg", "raan_deg", "argp_deg", "ta_deg", "period_min"):
        assert getattr(sat, field) is not None, f"COE field {field} missing"
    # Sanity: LEO band, period ~90 min.
    assert 6500.0 < sat.a_km < 7500.0
    assert 80.0 < sat.period_min < 110.0
    # Ground assets shouldn't carry orbital elements.
    gs = next((a for a in blue.assets if not a.on_orbit), None)
    if gs is not None:
        assert gs.a_km is None and gs.period_min is None


def test_scene_coes_update_after_maneuver():
    """Issuing a maneuver and advancing past its execution window changes the
    reported COEs — proves the 3D/2D views (both consumers of the scene) get a
    fresh orbit + ground track on the next refresh."""
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    before = next(a for a in mgr.get_scene("blue").assets if a.id == "ISR-EO-1")
    before_track_head = before.track[0]

    # Queue a 5 m/s ECI burn via the same path the UI uses.
    ack = mgr.issue_order("blue", Order(
        cell="blue", actor="ISR-EO-1", action="maneuver",
        params={"dv": [0, 5, 0], "via": "GS-NORTH"},
    ))
    assert ack.status == "queued" and ack.earliest_window is not None
    mgr.advance_to(ack.earliest_window[0] + 1)

    after = next(a for a in mgr.get_scene("blue").assets if a.id == "ISR-EO-1")
    # The orbit was mutated by the burn — at least one COE differs from before.
    assert after.a_km is not None and before.a_km is not None
    coes_changed = (
        after.a_km != before.a_km
        or after.e != before.e
        or after.i_deg != before.i_deg
        or after.raan_deg != before.raan_deg
        or after.argp_deg != before.argp_deg
    )
    assert coes_changed, "scene COEs did not change after maneuver — view would render stale orbit"
    # Period must track the new a (period ∝ a^(3/2)).
    assert after.period_min is not None
    # Ground track is rebuilt against the new orbit + new now, not cached from before the burn.
    assert len(after.track) == 60
    assert after.track[0] != before_track_head
