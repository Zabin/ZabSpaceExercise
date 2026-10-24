"""IP-1211 (FR-7440) — engine-level current-epoch TLE generation (`engine/tle_export.py`).

Design Decision 1 (`BL-0110`): a single-epoch SGP4 mean-element fit, applied uniformly to any
ECI state, formatted by `sgp4.exporter.export_tle`, with a ≤ 1 km round-trip position bound at the
TLE's own epoch.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

pytest.importorskip("sgp4")
from sgp4.api import Satrec  # noqa: E402

from spacesim.engine import simtime  # noqa: E402
from spacesim.engine.geometry import R_EARTH_EQ, micros_to_jd  # noqa: E402
from spacesim.engine.orbit import OrbitState, elements_to_rv  # noqa: E402
from spacesim.engine.propagator import ModeratePropagator  # noqa: E402
from spacesim.engine.tle_export import (  # noqa: E402
    PLACEHOLDER_SATNUM, ROUND_TRIP_BOUND_M, state_to_tle, tle_identity,
)

_T = simtime.from_iso("2030-01-01T06:00:00Z")

# A real ISS TLE (sgp4 documentation sample) — valid checksums.
_ISS_L1 = "1 25544U 98067A   19343.69339541  .00001764  00000-0  38792-4 0  9991"
_ISS_L2 = "2 25544  51.6439 211.2001 0007417  17.6667  85.6398 15.50103472202482"


def _checksum_ok(line: str) -> bool:
    total = sum(int(ch) if ch.isdigit() else (1 if ch == "-" else 0) for ch in line[:68])
    return total % 10 == int(line[68])


def _round_trip_error_m(line1: str, line2: str, r_m) -> float:
    sat = Satrec.twoline2rv(line1, line2)
    err, r_km, _ = sat.sgp4(sat.jdsatepoch, sat.jdsatepochF)
    assert err == 0
    return float(np.linalg.norm(np.array(r_km) * 1000.0 - np.asarray(r_m)))


def _kepler_rv(a_m, e, i_deg, raan=40.0, argp=30.0, ta=10.0):
    orb = OrbitState(a_m=a_m, e=e, i_deg=i_deg, raan_deg=raan, argp_deg=argp, ta_deg=ta, epoch=_T)
    return elements_to_rv(orb, _T)


@pytest.mark.verifies("FR-7440")
def test_tle_lines_are_well_formed():
    r, v = _kepler_rv(R_EARTH_EQ + 550e3, 0.0005, 51.6)
    out = state_to_tle(r, v, _T)
    l1, l2 = out["line1"], out["line2"]
    assert len(l1) == 69 and len(l2) == 69
    assert l1.startswith("1 ") and l2.startswith("2 ")
    assert _checksum_ok(l1) and _checksum_ok(l2)
    Satrec.twoline2rv(l1, l2)  # the project's own TLE-import parser accepts it


@pytest.mark.verifies("FR-7440")
@pytest.mark.parametrize("a_m,e,i_deg", [
    (R_EARTH_EQ + 400e3, 0.0005, 51.6),      # ISS-like LEO
    (R_EARTH_EQ + 700e3, 0.0, 98.2),          # sun-synchronous, circular
    (26_560e3, 0.01, 55.0),                   # GPS-like MEO (deep-space SGP4)
    (42_164e3, 0.0002, 0.05),                 # GEO, near-equatorial
    (R_EARTH_EQ + 500e3, 0.0, 0.0),           # exactly equatorial-circular (singular in classic elements)
    (42_164e3, 0.0, 0.05),                    # the shipped vignettes' GEO shape (circular, i = 0.05°)
    (42_164e3, 0.0, 0.1),
    (26_600e3, 0.72, 63.4),                   # Molniya HEO
    (R_EARTH_EQ + 600e3, 0.001, 179.9),       # near-retrograde-equatorial
])
def test_tle_fit_round_trip_within_bound(a_m, e, i_deg):
    r, v = _kepler_rv(a_m, e, i_deg)
    out = state_to_tle(r, v, _T)
    err = _round_trip_error_m(out["line1"], out["line2"], r)
    assert err <= ROUND_TRIP_BOUND_M
    assert out["fit_error_m"] == pytest.approx(err, abs=1e-6)


@pytest.mark.verifies("FR-7440")
@pytest.mark.parametrize("iso", ["2026-05-17T13:00:00Z", "2030-01-01T06:00:00Z", "2031-08-02T00:00:00Z"])
@pytest.mark.parametrize("i_deg", [0.0, 0.001, 0.01])
def test_tle_never_emits_outside_bound_for_degenerate_geo(iso, i_deg):
    """Circular + (near-)equatorial deep-space states are SDP4's worst-conditioned case: the fit
    must either land within the bound or reject with a reason — never emit an out-of-bound TLE."""
    t = simtime.from_iso(iso)
    orb = OrbitState(a_m=42_164e3, e=0.0, i_deg=i_deg, raan_deg=40.0, argp_deg=30.0, ta_deg=10.0, epoch=t)
    r, v = elements_to_rv(orb, t)
    try:
        out = state_to_tle(r, v, t)
    except ValueError:
        return
    assert _round_trip_error_m(out["line1"], out["line2"], r) <= ROUND_TRIP_BOUND_M


@pytest.mark.verifies("FR-7440")
def test_tle_fits_every_shipped_vignette_orbit():
    """Every on-orbit asset in every shipped vignette (at its start epoch) exports within bound."""
    import glob
    import os

    import yaml

    from spacesim.content.vignette import VIGNETTE_DIR, Vignette, build_world

    prop = ModeratePropagator()
    count = 0
    for path in sorted(glob.glob(os.path.join(str(VIGNETTE_DIR), "*.yaml"))):
        with open(path) as fh:
            raw = yaml.safe_load(fh)
        built = build_world(Vignette.model_validate(raw.get("vignette", raw)))
        world = built[0] if isinstance(built, tuple) else built
        for asset in world.assets.values():
            if asset.orbit is None:
                continue
            r, v = prop.rv(asset.orbit, world.now)
            out = state_to_tle(r, v, world.now, **tle_identity(asset.orbit))
            assert out["fit_error_m"] <= ROUND_TRIP_BOUND_M, (path, asset.id)
            count += 1
    assert count > 0


@pytest.mark.verifies("FR-7440")
def test_tle_epoch_is_given_sim_time():
    r, v = _kepler_rv(R_EARTH_EQ + 550e3, 0.001, 45.0)
    out = state_to_tle(r, v, _T)
    sat = Satrec.twoline2rv(out["line1"], out["line2"])
    # TLE epoch resolution is 1e-8 day (~0.9 ms).
    assert (sat.jdsatepoch + sat.jdsatepochF) == pytest.approx(micros_to_jd(_T), abs=2e-8)


@pytest.mark.verifies("FR-7440")
def test_tle_sourced_identity_and_bstar_carried():
    src = OrbitState(source="tle", tle_line1=_ISS_L1, tle_line2=_ISS_L2)
    ident = tle_identity(src)
    assert ident["satnum"] == 25544 and ident["intldesg"] == "98067A"
    t = simtime.from_iso("2019-12-10T12:00:00Z")  # a day after the source TLE's own epoch
    r, v = ModeratePropagator().rv(src, t)
    out = state_to_tle(r, v, t, **ident)
    assert out["line1"][2:7] == "25544" and out["line1"][9:17].strip() == "98067A"
    new = Satrec.twoline2rv(out["line1"], out["line2"])
    assert new.bstar == pytest.approx(Satrec.twoline2rv(_ISS_L1, _ISS_L2).bstar, rel=1e-4)
    assert _round_trip_error_m(out["line1"], out["line2"], r) <= ROUND_TRIP_BOUND_M
    # The re-fitted TLE's epoch is the requested time, not the source TLE's 2019-12-09 epoch.
    assert (new.jdsatepoch + new.jdsatepochF) == pytest.approx(micros_to_jd(t), abs=2e-8)

    kep = tle_identity(OrbitState(a_m=7e6, e=0.0, i_deg=10.0))
    assert kep["satnum"] == PLACEHOLDER_SATNUM and kep["intldesg"] == "" and kep["bstar"] == 0.0
    r2, v2 = _kepler_rv(7e6, 0.0, 10.0)
    line1 = state_to_tle(r2, v2, _T, **kep)["line1"]
    assert line1[2:7] == "99999" and line1[9:17].strip() == ""


@pytest.mark.verifies("FR-7440")
def test_tle_rejects_unrepresentable():
    r = np.array([R_EARTH_EQ + 500e3, 0.0, 0.0])
    v_esc = np.array([0.0, 12_000.0, 0.0])  # hyperbolic at LEO radius
    with pytest.raises(ValueError):
        state_to_tle(r, v_esc, _T)
    r_lo, v_lo = _kepler_rv(R_EARTH_EQ + 500e3, 0.3, 30.0)  # perigee well below the surface
    with pytest.raises(ValueError):
        state_to_tle(r_lo, v_lo, _T)


@pytest.mark.verifies("FR-7440")
def test_tle_export_is_deterministic():
    r, v = _kepler_rv(R_EARTH_EQ + 800e3, 0.002, 70.0)
    a = state_to_tle(r, v, _T)
    b = state_to_tle(np.array(r), np.array(v), _T)
    assert a == b
    assert not math.isnan(a["fit_error_m"])
