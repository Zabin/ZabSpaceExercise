"""Phase-2 reference check: validate the look-angle pipeline against Skyfield for a TLE asset.

Our moderate model propagates TLEs with sgp4 and rotates TEME->ECEF with GMST only (no polar
motion / nutation). This test confirms that simplification stays within a fraction of a degree of
Skyfield's full transformation, which is what "match a reference within tolerance" means in the
roadmap. Skipped if Skyfield (or its bundled timescale) is unavailable offline.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from spacesim.engine.access import AccessProvider, Scene, COMMAND_UPLINK
from spacesim.engine.entities import GroundSite
from spacesim.engine.geometry import GeoPoint, JD_UNIX_EPOCH, look_angles
from spacesim.engine.orbit import OrbitState
from spacesim.engine.propagator import ModeratePropagator

# Canonical valid ISS TLE (Vallado sgp4 test vector).
TLE1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"

SITE = GeoPoint(lat_deg=10.0, lon_deg=20.0, alt_m=0.0)


def _skyfield():
    try:
        from skyfield.api import EarthSatellite, load, wgs84
    except ImportError:  # optional dependency
        pytest.skip("skyfield not installed")
    try:
        ts = load.timescale()
    except Exception as exc:  # offline / missing bundled data
        pytest.skip(f"skyfield timescale unavailable: {exc}")
    return EarthSatellite, ts, wgs84


def _epoch_micros() -> int:
    from sgp4.api import Satrec

    sat = Satrec.twoline2rv(TLE1, TLE2)
    jd = sat.jdsatepoch + sat.jdsatepochF
    return round((jd - JD_UNIX_EPOCH) * 86400 * 1_000_000)


def test_tle_elevation_matches_skyfield_within_tolerance():
    EarthSatellite, ts, wgs84 = _skyfield()
    sat = EarthSatellite(TLE1, TLE2, "ISS", ts)
    site = wgs84.latlon(SITE.lat_deg, SITE.lon_deg, elevation_m=SITE.alt_m)

    orbit = OrbitState(source="tle", tle_line1=TLE1, tle_line2=TLE2, epoch=0)
    prop = ModeratePropagator()

    epoch = _epoch_micros()
    worst = 0.0
    for k in range(0, 181):  # every minute for 3 hours
        micros = epoch + k * 60 * 1_000_000
        r, _ = prop.rv(orbit, micros)
        mine, _, _ = look_angles(SITE, r, micros)

        dt = datetime.fromtimestamp(micros / 1e6, tz=timezone.utc)
        alt, _, _ = (sat - site).at(ts.from_datetime(dt)).altaz()
        worst = max(worst, abs(mine - alt.degrees))

    assert worst < 1.0, f"max elevation error {worst:.3f} deg exceeds tolerance"


def test_access_provider_finds_passes_for_tle_asset():
    orbit = OrbitState(source="tle", tle_line1=TLE1, tle_line2=TLE2, epoch=0)
    station = GroundSite(id="ST", location=SITE, elevation_mask_deg=5.0)
    ap = AccessProvider(Scene(satellites={"ISS": orbit}, sites={"ST": station}))
    epoch = _epoch_micros()
    wins = ap.windows("ST", "ISS", COMMAND_UPLINK, epoch, epoch + 24 * 3600 * 1_000_000)
    assert wins
    for w in wins:
        assert 0 < (w.end - w.start) / 1e6 / 60 < 15
