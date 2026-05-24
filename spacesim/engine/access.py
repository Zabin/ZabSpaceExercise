"""AccessProvider — computes the gating windows for all six access channels.

This is the second fidelity seam (``03-simulation-engine.md`` §2-3). Every player action is gated
by a window from here: you can only command/observe/jam/engage/rendezvous when geometry permits.
The moderate v1 model uses elevation masks, line-of-sight, lighting, altitude reach, and range
thresholds; a high-fidelity link-budget / Lambert-intercept model can replace it behind the same
interface. Windows are found by sampling a boolean access predicate then bisecting the edges, and
results are cached per (actor, target, channel) until invalidated (e.g., on a maneuver).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from pydantic import BaseModel

from spacesim.engine.entities import GroundSite, Sensor
from spacesim.engine.geometry import (
    R_EARTH_EQ,
    look_angles,
    elevation_from_unit_dir,
)
from spacesim.engine.orbit import OrbitState, period_s
from spacesim.engine.propagator import ModeratePropagator, Propagator
from spacesim.engine.sun import is_sunlit, sun_unit_eci

# The six gating channels (FR-E4 / 03-counterspace-taxonomy §3).
COMMAND_UPLINK = "command_uplink"
TELEMETRY_DOWNLINK = "telemetry_downlink"
SENSOR_OBSERVATION = "sensor_observation"
JAM_FOOTPRINT = "jam_footprint"
WEAPON_ENGAGEMENT = "weapon_engagement"
RPO_PROXIMITY = "rpo_proximity"

MICROS_PER_SECOND = 1_000_000


class AccessWindow(BaseModel):
    channel: str
    actor: str
    target: str
    start: int      # sim time, micros
    end: int
    quality: float  # 0..1 (peak elevation proxy / closeness proxy)


@dataclass
class Scene:
    """The spatial inventory the provider resolves actor/target ids against."""

    satellites: dict[str, OrbitState] = field(default_factory=dict)
    sites: dict[str, GroundSite] = field(default_factory=dict)
    sensors: dict[str, Sensor] = field(default_factory=dict)


@dataclass
class AccessConfig:
    twilight_deg: float = -6.0          # site is "dark" when the Sun is below this elevation
    jam_mask_deg: float = 5.0           # min elevation of victim sat above the jammer
    interceptor_max_alt_m: float = 2_000e3   # DA-ASAT reach (LEO only by default)
    interceptor_mask_deg: float = 10.0
    rpo_threshold_m: float = 50_000.0   # proximity-window range gate
    sample_step_s: float = 20.0         # base sampling step (auto-refined for short LEO passes)
    edge_refine_s: float = 1.0          # bisection precision for window edges


class AccessProvider:
    def __init__(
        self,
        scene: Scene,
        propagator: Optional[Propagator] = None,
        config: Optional[AccessConfig] = None,
    ) -> None:
        self.scene = scene
        self.prop = propagator or ModeratePropagator()
        self.cfg = config or AccessConfig()
        self._cache: dict[tuple[str, str, str, int, int], list[AccessWindow]] = {}

    def invalidate(self, actor: Optional[str] = None) -> None:
        """Drop cached windows (call after a maneuver changes an orbit)."""
        if actor is None:
            self._cache.clear()
        else:
            for key in [k for k in self._cache if actor in (k[0], k[1])]:
                del self._cache[key]

    # -- public API ------------------------------------------------------------
    def windows(self, actor: str, target: str, channel: str, t0: int, horizon: int) -> list[AccessWindow]:
        key = (actor, target, channel, t0, horizon)
        if key in self._cache:
            return self._cache[key]
        access_fn, quality_fn = self._predicate(actor, target, channel)
        step = self._step_for(actor, target, channel)
        raw = _find_windows(access_fn, quality_fn, t0, horizon, step, self.cfg.edge_refine_s)
        out = [
            AccessWindow(channel=channel, actor=actor, target=target, start=s, end=e, quality=q)
            for (s, e, q) in raw
        ]
        self._cache[key] = out
        return out

    # -- predicate construction per channel ------------------------------------
    def _predicate(self, actor: str, target: str, channel: str) -> tuple[Callable[[int], bool], Callable[[int], float]]:
        if channel in (COMMAND_UPLINK, TELEMETRY_DOWNLINK):
            site, sat = self._site_and_sat(actor, target)
            return self._ground_sat_predicate(site, sat, site.elevation_mask_deg)
        if channel == JAM_FOOTPRINT:
            jammer = self.scene.sites[actor]
            sat = self.scene.satellites[target]
            return self._ground_sat_predicate(jammer, sat, self.cfg.jam_mask_deg)
        if channel == WEAPON_ENGAGEMENT:
            launch = self.scene.sites[actor]
            sat = self.scene.satellites[target]
            return self._weapon_predicate(launch, sat)
        if channel == SENSOR_OBSERVATION:
            sensor = self.scene.sensors[actor]
            sat = self.scene.satellites[target]
            return self._observation_predicate(sensor, sat)
        if channel == RPO_PROXIMITY:
            chaser = self.scene.satellites[actor]
            sat = self.scene.satellites[target]
            return self._rpo_predicate(chaser, sat)
        raise ValueError(f"unknown channel {channel!r}")

    def _site_and_sat(self, actor: str, target: str) -> tuple[GroundSite, OrbitState]:
        if actor in self.scene.sites:
            return self.scene.sites[actor], self.scene.satellites[target]
        return self.scene.sites[target], self.scene.satellites[actor]

    def _ground_sat_predicate(self, site: GroundSite, sat: OrbitState, mask_deg: float):
        def elevation(t: int) -> float:
            r, _ = self.prop.rv(sat, t)
            el, _, _ = look_angles(site.location, r, t)
            return el

        return (lambda t: elevation(t) >= mask_deg, lambda t: max(0.0, elevation(t)) / 90.0)

    def _weapon_predicate(self, launch: GroundSite, sat: OrbitState):
        def metrics(t: int) -> tuple[float, float]:
            r, _ = self.prop.rv(sat, t)
            el, _, _ = look_angles(launch.location, r, t)
            alt = float(np.linalg.norm(r)) - R_EARTH_EQ
            return el, alt

        def access(t: int) -> bool:
            el, alt = metrics(t)
            return el >= self.cfg.interceptor_mask_deg and alt <= self.cfg.interceptor_max_alt_m

        return access, (lambda t: max(0.0, metrics(t)[0]) / 90.0)

    def _observation_predicate(self, sensor: Sensor, sat: OrbitState):
        def sat_r(t: int) -> np.ndarray:
            r, _ = self.prop.rv(sat, t)
            return r

        if sensor.kind == "space_based":
            def access(t: int) -> bool:
                r_t = sat_r(t)
                r_s, _ = self.prop.rv(sensor.orbit, t)
                rng = float(np.linalg.norm(r_t - r_s))
                if sensor.max_range_m is not None and rng > sensor.max_range_m:
                    return False
                if not _has_line_of_sight(r_s, r_t):
                    return False
                if sensor.needs_lighting and not is_sunlit(r_t, t):
                    return False
                return True

            def quality(t: int) -> float:
                if sensor.max_range_m:
                    r_t = sat_r(t)
                    r_s, _ = self.prop.rv(sensor.orbit, t)
                    rng = float(np.linalg.norm(r_t - r_s))
                    return max(0.0, 1.0 - rng / sensor.max_range_m)
                return 1.0

            return access, quality

        # ground sensor
        def access(t: int) -> bool:
            r_t = sat_r(t)
            el, _, rng = look_angles(sensor.location, r_t, t)
            if el < sensor.elevation_mask_deg:
                return False
            if sensor.max_range_m is not None and rng > sensor.max_range_m:
                return False
            if sensor.needs_lighting:
                if not is_sunlit(r_t, t):
                    return False
                sun_el = elevation_from_unit_dir(sensor.location, sun_unit_eci(t), t)
                if sun_el >= self.cfg.twilight_deg:
                    return False
            return True

        def quality(t: int) -> float:
            el, _, _ = look_angles(sensor.location, sat_r(t), t)
            return max(0.0, el) / 90.0

        return access, quality

    def _rpo_predicate(self, chaser: OrbitState, sat: OrbitState):
        def rng(t: int) -> float:
            r_c, _ = self.prop.rv(chaser, t)
            r_t, _ = self.prop.rv(sat, t)
            return float(np.linalg.norm(r_c - r_t))

        thr = self.cfg.rpo_threshold_m
        return (lambda t: rng(t) <= thr, lambda t: max(0.0, 1.0 - rng(t) / thr))

    def _step_for(self, actor: str, target: str, channel: str) -> float:
        """Sample finely enough to catch the shortest pass (a fraction of the orbital period)."""
        sat_ids = [i for i in (actor, target) if i in self.scene.satellites]
        periods = [period_s(self.scene.satellites[i].a_m) for i in sat_ids if self.scene.satellites[i].a_m]
        if channel == RPO_PROXIMITY and periods:
            return max(2.0, min(periods) / 400.0)
        if periods:
            return max(2.0, min(self.cfg.sample_step_s, min(periods) / 120.0))
        return self.cfg.sample_step_s


def _has_line_of_sight(r_a: np.ndarray, r_b: np.ndarray) -> bool:
    """True if the segment a-b does not pass through the Earth (sphere of radius R_EARTH_EQ)."""
    d = r_b - r_a
    dd = float(np.dot(d, d))
    if dd == 0.0:
        return True
    s = -float(np.dot(r_a, d)) / dd  # closest-approach parameter along the segment
    s = max(0.0, min(1.0, s))
    closest = r_a + s * d
    return float(np.linalg.norm(closest)) >= R_EARTH_EQ


def _find_windows(
    access_fn: Callable[[int], bool],
    quality_fn: Callable[[int], float],
    t0: int,
    horizon: int,
    step_s: float,
    refine_s: float,
) -> list[tuple[int, int, float]]:
    step = max(1, int(step_s * MICROS_PER_SECOND))
    refine = max(1, int(refine_s * MICROS_PER_SECOND))

    windows: list[tuple[int, int, float]] = []
    t = t0
    prev_t = t0
    prev = access_fn(t0)
    start: Optional[int] = t0 if prev else None
    peak = quality_fn(t0) if prev else 0.0

    while t < horizon:
        t = min(t + step, horizon)
        cur = access_fn(t)
        if cur and prev:
            peak = max(peak, quality_fn(t))
        if cur != prev:
            edge = _bisect_edge(access_fn, prev_t, t, prev, refine)
            if cur and not prev:  # opening
                start = edge
                peak = quality_fn(edge)
            else:  # closing
                if start is not None:
                    windows.append((start, edge, peak))
                    start = None
        prev = cur
        prev_t = t

    if prev and start is not None:
        windows.append((start, horizon, max(peak, quality_fn(horizon))))
    return windows


def _bisect_edge(access_fn: Callable[[int], bool], lo: int, hi: int, lo_state: bool, refine: int) -> int:
    """Find the transition time in (lo, hi] to within ``refine`` micros."""
    while hi - lo > refine:
        mid = (lo + hi) // 2
        if access_fn(mid) == lo_state:
            lo = mid
        else:
            hi = mid
    return hi
