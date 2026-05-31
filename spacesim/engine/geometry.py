"""Geometry & Earth-frame primitives for the moderate-fidelity model.

Pure, deterministic functions (NumPy only): frame rotations (ECI<->ECEF via GMST), WGS84
geodetic conversions, and topocentric look angles. No wall-clock reads — every function is a
function of the sim time it is given. See ``01-research/04-orbital-mechanics-primer.md``.
"""

from __future__ import annotations

import math

import numpy as np
from pydantic import BaseModel

# Physical constants (WGS84 / EGM-ish, sufficient for moderate fidelity).
MU_EARTH = 3.986004418e14          # m^3 / s^2
R_EARTH_EQ = 6378137.0             # m, equatorial radius
J2 = 1.08262668e-3                 # second zonal harmonic
OMEGA_EARTH = 7.2921159e-5         # rad/s, Earth rotation rate
WGS84_F = 1.0 / 298.257223563      # flattening
WGS84_E2 = WGS84_F * (2 - WGS84_F)  # first eccentricity squared

JD_UNIX_EPOCH = 2440587.5
SEC_PER_DAY = 86400.0
MICROS_PER_SECOND = 1_000_000


class GeoPoint(BaseModel):
    lat_deg: float
    lon_deg: float
    alt_m: float = 0.0


class ECIState(BaseModel):
    """Inertial position/velocity at an instant (engine-internal)."""

    t: int                  # sim time, micros since epoch
    r_m: list[float]        # [x, y, z] in ECI, metres
    v_ms: list[float]       # [vx, vy, vz] in ECI, m/s

    def r(self) -> np.ndarray:
        return np.array(self.r_m, dtype=float)

    def v(self) -> np.ndarray:
        return np.array(self.v_ms, dtype=float)


def micros_to_jd(micros: int) -> float:
    return JD_UNIX_EPOCH + (micros / MICROS_PER_SECOND) / SEC_PER_DAY


def gmst_rad(micros: int) -> float:
    """Greenwich Mean Sidereal Time (radians) — IAU-82 polynomial in UT1≈UTC."""
    jd = micros_to_jd(micros)
    d = jd - 2451545.0
    t = d / 36525.0
    deg = 280.46061837 + 360.98564736629 * d + 0.000387933 * t * t - (t ** 3) / 38710000.0
    return math.radians(deg % 360.0)


def _rot3_z(theta: float) -> np.ndarray:
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]])


def eci_to_ecef(r_eci: np.ndarray, micros: int) -> np.ndarray:
    return _rot3_z(gmst_rad(micros)) @ r_eci


def ecef_to_eci(r_ecef: np.ndarray, micros: int) -> np.ndarray:
    return _rot3_z(gmst_rad(micros)).T @ r_ecef


def geodetic_to_ecef(geo: GeoPoint) -> np.ndarray:
    lat = math.radians(geo.lat_deg)
    lon = math.radians(geo.lon_deg)
    sin_lat, cos_lat = math.sin(lat), math.cos(lat)
    n = R_EARTH_EQ / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    x = (n + geo.alt_m) * cos_lat * math.cos(lon)
    y = (n + geo.alt_m) * cos_lat * math.sin(lon)
    z = (n * (1.0 - WGS84_E2) + geo.alt_m) * sin_lat
    return np.array([x, y, z])


def ecef_to_geodetic(r_ecef: np.ndarray) -> GeoPoint:
    x, y, z = r_ecef
    lon = math.atan2(y, x)
    p = math.hypot(x, y)
    lat = math.atan2(z, p * (1.0 - WGS84_E2))  # initial guess
    for _ in range(6):  # Bowring fixed-point; converges fast
        sin_lat = math.sin(lat)
        n = R_EARTH_EQ / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
        alt = p / math.cos(lat) - n
        lat = math.atan2(z, p * (1.0 - WGS84_E2 * n / (n + alt)))
    sin_lat = math.sin(lat)
    n = R_EARTH_EQ / math.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    alt = p / math.cos(lat) - n
    return GeoPoint(lat_deg=math.degrees(lat), lon_deg=math.degrees(lon), alt_m=alt)


def _enu_basis(geo: GeoPoint) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lat = math.radians(geo.lat_deg)
    lon = math.radians(geo.lon_deg)
    east = np.array([-math.sin(lon), math.cos(lon), 0.0])
    north = np.array([-math.sin(lat) * math.cos(lon), -math.sin(lat) * math.sin(lon), math.cos(lat)])
    up = np.array([math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat)])
    return east, north, up


def look_angles(site: GeoPoint, r_eci_target: np.ndarray, micros: int) -> tuple[float, float, float]:
    """Return (elevation_deg, azimuth_deg, range_m) from a ground site to an ECI point."""
    r_target_ecef = eci_to_ecef(r_eci_target, micros)
    r_site_ecef = geodetic_to_ecef(site)
    rho = r_target_ecef - r_site_ecef
    rng = float(np.linalg.norm(rho))
    east, north, up = _enu_basis(site)
    e = float(np.dot(rho, east))
    n = float(np.dot(rho, north))
    u = float(np.dot(rho, up))
    elevation = math.degrees(math.asin(max(-1.0, min(1.0, u / rng))))
    azimuth = math.degrees(math.atan2(e, n)) % 360.0
    return elevation, azimuth, rng


def elevation_from_unit_dir(site: GeoPoint, unit_eci: np.ndarray, micros: int) -> float:
    """Elevation (deg) of a far-away direction (e.g. the Sun) above the site horizon."""
    dir_ecef = eci_to_ecef(unit_eci, micros)
    _, _, up = _enu_basis(site)
    return math.degrees(math.asin(max(-1.0, min(1.0, float(np.dot(dir_ecef, up))))))
