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


# -- IP-1220 (FR-1610-FR-1660) — sensor modality models -------------------------------------------

def test_sensor_new_fields_default_absent_zero_behavior_change():
    """The six new fields must not change any existing sensor's observed behavior when unset."""
    sub = _subpoint(LEO, 0)
    loc = GeoPoint(lat_deg=sub.lat_deg, lon_deg=sub.lon_deg)
    old = Sensor(id="OPT", kind="ground_optical", location=loc, elevation_mask_deg=5.0)
    new = Sensor(id="OPT", kind="ground_optical", location=loc, elevation_mask_deg=5.0,
                 beam_mode=None, exclusion_angle_deg=None, min_range_km=None,
                 altitude_band_affinity=None, requires_cue=False, host_asset_id=None)
    ap_old = _provider(Scene(satellites={"SAT": LEO}, sensors={"OPT": old}))
    ap_new = _provider(Scene(satellites={"SAT": LEO}, sensors={"OPT": new}))
    assert ap_old.windows("OPT", "SAT", SENSOR_OBSERVATION, 0, DAY) == ap_new.windows("OPT", "SAT", SENSOR_OBSERVATION, 0, DAY)


def test_exclusion_angle_rejects_near_sun_and_accepts_far_from_sun():
    """FR-1620 — a ground-optical sensor's declared solar exclusion cone rejects an observation
    whose target line of sight falls too close to the Sun, and accepts one that doesn't."""
    import numpy as np
    from spacesim.engine.sun import sun_unit_eci
    from spacesim.engine.geometry import ecef_to_eci, geodetic_to_ecef

    loc = GeoPoint(lat_deg=0.0, lon_deg=0.0)

    def sep_deg(t: int) -> float:
        r_t, _ = PROP.rv(LEO, t)
        r_site = ecef_to_eci(geodetic_to_ecef(loc), t)
        los = r_t - r_site
        los_hat = los / np.linalg.norm(los)
        sun_hat = sun_unit_eci(t)
        cos_a = max(-1.0, min(1.0, float(np.dot(los_hat, sun_hat))))
        return float(np.degrees(np.arccos(cos_a)))

    near_t, far_t = None, None
    for k in range(0, 6000, 15):
        t = k * 1_000_000
        s = sep_deg(t)
        if s < 20.0 and near_t is None:
            near_t = t
        if s > 60.0 and far_t is None:
            far_t = t
        if near_t is not None and far_t is not None:
            break
    assert near_t is not None and far_t is not None, "fixture: no near/far Sun geometry found"

    optical = Sensor(id="OPT", kind="ground_optical", location=loc,
                      elevation_mask_deg=-90.0, exclusion_angle_deg=30.0)
    ap = _provider(Scene(satellites={"SAT": LEO}, sensors={"OPT": optical}))
    access_fn, _ = ap._predicate("OPT", "SAT", SENSOR_OBSERVATION)
    assert access_fn(near_t) is False
    assert access_fn(far_t) is True


def test_min_range_floor_rejects_too_close_space_sensor():
    """FR-1630 — a space-based sensor's declared minimum-range floor hard-rejects a target closer
    than the threshold; a target beyond it is unaffected."""
    near_sensor_orbit = LEO.model_copy(update={"ta_deg": 0.05})
    far_sensor_orbit = LEO.model_copy(update={"ta_deg": 30.0})
    sensor_near = Sensor(id="S1", kind="space_based", orbit=near_sensor_orbit, min_range_km=50.0)
    sensor_far = Sensor(id="S2", kind="space_based", orbit=far_sensor_orbit, min_range_km=50.0)
    scene = Scene(satellites={"SAT": LEO}, sensors={"S1": sensor_near, "S2": sensor_far})
    ap = _provider(scene)
    access_near, _ = ap._predicate("S1", "SAT", SENSOR_OBSERVATION)
    access_far, _ = ap._predicate("S2", "SAT", SENSOR_OBSERVATION)
    assert access_near(0) is False
    assert access_far(0) is True


def test_hosted_sensor_follows_host_asset_orbit_and_both_identifiers_match():
    """FR-1660 — a hosted sensor's position is read from its host Asset's current orbit, not its
    own (absent) orbit; both the sensor's own id and its host_asset_id query the same access."""
    sub = _subpoint(LEO, 0)
    loc = GeoPoint(lat_deg=sub.lat_deg, lon_deg=sub.lon_deg)
    ground = Sensor(id="OPT", kind="ground_optical", location=loc, elevation_mask_deg=5.0)
    hosted_space = Sensor(id="HOSTED-SDA", kind="space_based", host_asset_id="HOST-SAT")
    scene = Scene(satellites={"SAT": LEO, "HOST-SAT": LEO.model_copy(update={"ta_deg": 5.0})},
                  sensors={"OPT": ground, "HOSTED-SDA": hosted_space})
    ap = _provider(scene)
    by_sensor_id = ap.windows("HOSTED-SDA", "SAT", SENSOR_OBSERVATION, 0, DAY)
    by_host_id = ap.windows("HOST-SAT", "SAT", SENSOR_OBSERVATION, 0, DAY)
    assert [(w.start, w.end, w.quality) for w in by_sensor_id] == \
           [(w.start, w.end, w.quality) for w in by_host_id]
    assert by_sensor_id  # sanity: some access exists
