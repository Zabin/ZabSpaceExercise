"""Access windows for all six channels (moderate fidelity)."""

from __future__ import annotations

from spacesim.engine.access import (
    AccessConfig,
    AccessProvider,
    Scene,
    COMMAND_UPLINK,
    JAM_FOOTPRINT,
    RPO_PROXIMITY,
    SENSOR_OBSERVATION,
    WEAPON_ENGAGEMENT,
)
from spacesim.engine.entities import GroundSite, Sensor
from spacesim.engine.geometry import (
    GeoPoint,
    R_EARTH_EQ,
    ecef_to_geodetic,
    eci_to_ecef,
)
from spacesim.engine.orbit import OrbitState
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simtime import hours, minutes

PROP = ModeratePropagator()
LEO = OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=0, epoch=0)
GEO = OrbitState(a_m=42_164e3, e=0.0, i_deg=0.0, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0)
MEO = OrbitState(a_m=26_560e3, e=0.0, i_deg=55.0, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0)
DAY = hours(24)


def _subpoint(orbit: OrbitState, t: int) -> GeoPoint:
    r, _ = PROP.rv(orbit, t)
    return ecef_to_geodetic(eci_to_ecef(r, t))


def _provider(scene: Scene, cfg: AccessConfig | None = None) -> AccessProvider:
    return AccessProvider(scene, propagator=PROP, config=cfg)


def test_leo_uplink_has_several_short_passes_per_day():
    station = GroundSite(id="ST", location=GeoPoint(lat_deg=45.0, lon_deg=0.0), elevation_mask_deg=5.0)
    ap = _provider(Scene(satellites={"SAT": LEO}, sites={"ST": station}))
    wins = ap.windows("ST", "SAT", COMMAND_UPLINK, 0, DAY)
    assert 2 <= len(wins) <= 20
    for w in wins:
        dur_min = (w.end - w.start) / 1e6 / 60
        assert 0 < dur_min < 15        # LEO passes are minutes long
        assert 0.0 < w.quality <= 1.0


def test_geo_gives_continuous_regional_access():
    sub = _subpoint(GEO, 0)
    station = GroundSite(id="EQ", location=GeoPoint(lat_deg=0.0, lon_deg=sub.lon_deg))
    ap = _provider(Scene(satellites={"GEO": GEO}, sites={"EQ": station}))
    wins = ap.windows("EQ", "GEO", COMMAND_UPLINK, 0, DAY)
    assert len(wins) == 1
    assert (wins[0].end - wins[0].start) / 1e6 > 23 * 3600  # essentially always in view


def test_meo_passes_are_long():
    sub = _subpoint(MEO, 0)
    station = GroundSite(id="MS", location=GeoPoint(lat_deg=sub.lat_deg, lon_deg=sub.lon_deg))
    ap = _provider(Scene(satellites={"MEO": MEO}, sites={"MS": station}))
    wins = ap.windows("MS", "MEO", COMMAND_UPLINK, 0, DAY)
    assert wins
    assert max((w.end - w.start) for w in wins) / 1e6 / 3600 > 1.0  # hours, not minutes


def test_weapon_engagement_reaches_leo_but_not_geo():
    sub = _subpoint(LEO, 0)
    launch = GroundSite(id="LP", location=GeoPoint(lat_deg=sub.lat_deg, lon_deg=sub.lon_deg))
    scene = Scene(satellites={"LEO": LEO, "GEO": GEO}, sites={"LP": launch})
    ap = _provider(scene)
    assert ap.windows("LP", "LEO", WEAPON_ENGAGEMENT, 0, DAY)        # LEO within reach
    # GEO launch site: place under the GEO sat; still unreachable on altitude.
    geo_sub = _subpoint(GEO, 0)
    ap.scene.sites["LP"] = GroundSite(id="LP", location=GeoPoint(lat_deg=0.0, lon_deg=geo_sub.lon_deg))
    ap.invalidate()
    assert ap.windows("LP", "GEO", WEAPON_ENGAGEMENT, 0, DAY) == []  # altitude beyond interceptor


def test_rpo_proximity_continuous_when_co_located_and_empty_when_far():
    # Co-located chaser (same elements) stays at zero range.
    scene = Scene(satellites={"CHASE": LEO.model_copy(), "TGT": LEO})
    ap = _provider(scene)
    wins = ap.windows("CHASE", "TGT", RPO_PROXIMITY, 0, minutes(95) * 1)
    assert len(wins) == 1
    assert wins[0].quality > 0.99  # range ≈ 0

    far = LEO.model_copy(update={"a_m": LEO.a_m + 400e3})  # different altitude → far apart
    scene2 = Scene(satellites={"CHASE": far, "TGT": LEO})
    ap2 = _provider(scene2)
    assert ap2.windows("CHASE", "TGT", RPO_PROXIMITY, 0, hours(3)) == []


def test_optical_sensor_lighting_reduces_access_versus_radar():
    sub = _subpoint(LEO, 0)
    loc = GeoPoint(lat_deg=sub.lat_deg, lon_deg=sub.lon_deg)
    radar = Sensor(id="RDR", kind="ground_radar", location=loc, elevation_mask_deg=5.0)
    optical = Sensor(id="OPT", kind="ground_optical", location=loc, elevation_mask_deg=5.0, needs_lighting=True)
    ap = _provider(Scene(satellites={"SAT": LEO}, sensors={"RDR": radar, "OPT": optical}))
    radar_wins = ap.windows("RDR", "SAT", SENSOR_OBSERVATION, 0, DAY)
    optical_wins = ap.windows("OPT", "SAT", SENSOR_OBSERVATION, 0, DAY)
    assert radar_wins
    radar_dur = sum(w.end - w.start for w in radar_wins)
    optical_dur = sum(w.end - w.start for w in optical_wins)
    assert optical_dur <= radar_dur  # lighting constraint never adds access


def test_jam_footprint_tracks_satellite_visibility():
    sub = _subpoint(LEO, 0)
    jammer = GroundSite(id="JAM", location=GeoPoint(lat_deg=sub.lat_deg, lon_deg=sub.lon_deg))
    ap = _provider(Scene(satellites={"SAT": LEO}, sites={"JAM": jammer}))
    wins = ap.windows("JAM", "SAT", JAM_FOOTPRINT, 0, DAY)
    assert wins  # jammer can hit the sat while it is above the local horizon


def test_window_cache_and_invalidate():
    station = GroundSite(id="ST", location=GeoPoint(lat_deg=45.0, lon_deg=0.0))
    ap = _provider(Scene(satellites={"SAT": LEO}, sites={"ST": station}))
    first = ap.windows("ST", "SAT", COMMAND_UPLINK, 0, DAY)
    assert ap.windows("ST", "SAT", COMMAND_UPLINK, 0, DAY) is first  # cached identity
    ap.invalidate("SAT")
    assert ap.windows("ST", "SAT", COMMAND_UPLINK, 0, DAY) is not first
