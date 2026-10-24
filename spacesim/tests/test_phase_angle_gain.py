"""IP-1221 (FR-1670, FS-122 v1.1) — CATS illumination phase-angle observation-gain refinement.

A passive-EO (``needs_lighting``) sensor may declare ``usable_phase_angle_deg = (lo, hi)``. The
observe order's scheduled gain is unchanged when the Sun-target-sensor phase angle at the
observation instant (``win.start``) lies inside the range, and multiplied by a linear fall-off
factor outside it (1 at the bound, 0 at 0°/180°; Design Decision 3). Undeclared sensors are
unaffected. The phase angle is computed only by ``engine/sun.py::cats_phase_angle_deg``.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from spacesim.engine.entities import Asset, Sensor
from spacesim.engine.geometry import R_EARTH_EQ, GeoPoint, ecef_to_eci, ecef_to_geodetic, eci_to_ecef, geodetic_to_ecef
from spacesim.engine.isr import beam_params, effective_gain, phase_angle_factor
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simulation import Simulation
from spacesim.engine.sun import cats_phase_angle_deg
from spacesim.engine.world import WorldState

PROP = ModeratePropagator()


def _leo(ta: float = 0.0, alt_km: float = 550.0, raan: float = 33.0) -> OrbitState:
    return OrbitState(a_m=R_EARTH_EQ + alt_km * 1e3, e=0.0, i_deg=51.6, raan_deg=raan,
                      argp_deg=0, ta_deg=ta, epoch=0)


# --------------------------------------------------------------------------- #
# Test 1 — factor shape (Design Decision 3)
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1670")
def test_factor_is_one_inside_the_range_including_both_bounds():
    for theta in (10.0, 20.0, 55.0, 90.0):
        assert phase_angle_factor(theta, (10.0, 90.0)) == 1.0


@pytest.mark.verifies("FR-1670")
def test_factor_falls_linearly_to_zero_at_180_above_the_range():
    rng = (0.0, 90.0)
    assert phase_angle_factor(180.0, rng) == pytest.approx(0.0)
    assert phase_angle_factor(135.0, rng) == pytest.approx(0.5)
    # strictly below 1 just outside, tends to 1 approaching the bound (continuity)
    assert phase_angle_factor(90.001, rng) < 1.0
    assert phase_angle_factor(90.001, rng) == pytest.approx(1.0, abs=1e-4)
    # non-increasing moving away from the range
    vals = [phase_angle_factor(t, rng) for t in (91.0, 100.0, 120.0, 150.0, 179.0, 180.0)]
    assert all(a >= b for a, b in zip(vals, vals[1:]))
    assert all(v < 1.0 for v in vals)


@pytest.mark.verifies("FR-1670")
def test_factor_falls_linearly_to_zero_at_0_below_the_range():
    rng = (40.0, 150.0)
    assert phase_angle_factor(0.0, rng) == pytest.approx(0.0)
    assert phase_angle_factor(20.0, rng) == pytest.approx(0.5)
    assert phase_angle_factor(39.999, rng) < 1.0
    vals = [phase_angle_factor(t, rng) for t in (39.0, 30.0, 10.0, 0.0)]
    assert all(a >= b for a, b in zip(vals, vals[1:]))


@pytest.mark.verifies("FR-1670")
def test_factor_with_bound_at_the_domain_edge_has_no_outside_region():
    assert phase_angle_factor(180.0, (0.0, 180.0)) == 1.0
    assert phase_angle_factor(0.0, (0.0, 180.0)) == 1.0


# --------------------------------------------------------------------------- #
# Test 2 — effective_gain composition + regression (Design Decision 1)
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1670")
def test_effective_gain_without_phase_argument_is_unchanged():
    bp, _ = beam_params("isr_eo", None)
    base = effective_gain(1.0, 20.0, bp)
    banded = effective_gain(1.0, 20.0, bp, target_regime="GEO", band_affinity="LEO")
    assert effective_gain(1.0, 20.0, bp, phase_angle_deg=None, usable_phase_range=None) == base
    assert effective_gain(1.0, 20.0, bp, target_regime="GEO", band_affinity="LEO",
                          phase_angle_deg=170.0, usable_phase_range=None) == banded


@pytest.mark.verifies("FR-1670")
def test_effective_gain_applies_factor_after_existing_terms():
    bp, _ = beam_params("isr_eo", None)
    base = effective_gain(1.0, 20.0, bp)
    assert effective_gain(1.0, 20.0, bp, phase_angle_deg=60.0, usable_phase_range=(0.0, 90.0)) == base
    outside = effective_gain(1.0, 20.0, bp, phase_angle_deg=135.0, usable_phase_range=(0.0, 90.0))
    assert outside == pytest.approx(base * 0.5)
    both = effective_gain(1.0, 20.0, bp, target_regime="GEO", band_affinity="LEO",
                          phase_angle_deg=135.0, usable_phase_range=(0.0, 90.0))
    banded = effective_gain(1.0, 20.0, bp, target_regime="GEO", band_affinity="LEO")
    assert both == pytest.approx(banded * 0.5)
    assert both < outside


# --------------------------------------------------------------------------- #
# Tests 3-5 — through OrderSystem: the scheduled execute_observe payload's gain
# --------------------------------------------------------------------------- #

def _observe(world: WorldState, sensor_id: str, target: str) -> tuple[float, int]:
    sim = Simulation(world, seed=7)
    osys = OrderSystem(sim, roe={"blue": {}, "red": {}})
    order = osys.issue(Order(cell="blue", actor=sensor_id, action="observe", target=target,
                             params={"intent": "track"}))
    assert order.status == "queued", order.fail_reason
    ev = [tup[2] for tup in sim.scheduler._heap if tup[2].kind == "execute_observe"]
    assert len(ev) == 1
    return float(ev[0].payload["gain"]), int(order.earliest_window[0])


def _space_world(sensor: Sensor, extra_assets: dict | None = None) -> WorldState:
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=_leo(0.0))
    for k, a in (extra_assets or {}).items():
        world.assets[k] = a
    world.sensors[sensor.id] = sensor
    return world


def _space_sensor(**kw) -> Sensor:
    return Sensor(id="SBO", owner="blue", kind="space_based", orbit=_leo(3.0), needs_lighting=True, **kw)


def _theta_space(observer_orbit: OrbitState, t: int) -> float:
    r_t, _ = PROP.rv(_leo(0.0), t)
    r_o, _ = PROP.rv(observer_orbit, t)
    return cats_phase_angle_deg(r_t, r_o, t)


@pytest.mark.verifies("FR-1670")
def test_no_declared_range_leaves_scheduled_gain_unchanged_space_based():
    """Test 3 / AC10 — a sensor without a range behaves exactly as before, at any geometry."""
    g_plain, t_plain = _observe(_space_world(_space_sensor()), "SBO", "TGT")
    # The same sensor with a range covering every angle gives the identical gain and window.
    g_full, t_full = _observe(_space_world(_space_sensor(usable_phase_angle_deg=(0.0, 180.0))), "SBO", "TGT")
    assert (g_full, t_full) == (g_plain, t_plain)
    assert g_plain > 0.0


@pytest.mark.verifies("FR-1670")
def test_space_based_gain_unchanged_inside_and_strictly_lower_outside():
    """Test 5 / AC9 — space-based optical sensor; the angle is evaluated at win.start."""
    g_plain, t0 = _observe(_space_world(_space_sensor()), "SBO", "TGT")
    theta = _theta_space(_leo(3.0), t0)
    inside = (0.0, min(180.0, theta + 5.0))
    g_in, t_in = _observe(_space_world(_space_sensor(usable_phase_angle_deg=inside)), "SBO", "TGT")
    assert t_in == t0 and g_in == pytest.approx(g_plain)
    if theta > 10.0:
        outside = (0.0, theta - 10.0)
    else:
        outside = (theta + 10.0, 180.0)
    g_out, t_out = _observe(_space_world(_space_sensor(usable_phase_angle_deg=outside)), "SBO", "TGT")
    assert t_out == t0, "a declared range must not change window selection"
    assert g_out < g_plain
    assert g_out == pytest.approx(g_plain * phase_angle_factor(theta, outside))


@pytest.mark.verifies("FR-1670", "FR-1660")
def test_hosted_sensor_uses_host_orbit_as_observer_position():
    """Test 5 / AC9 + FR-1660 — observer position is the host asset's current orbit."""
    host_orbit = _leo(3.0)
    host = Asset(id="HOST", owner="blue", kind="satellite", orbit=host_orbit)

    def hosted(**kw) -> Sensor:
        return Sensor(id="HSO", owner="blue", kind="space_based", host_asset_id="HOST",
                      orbit=_leo(40.0), needs_lighting=True, **kw)  # own orbit must be ignored

    g_plain, t0 = _observe(_space_world(hosted(), {"HOST": host}), "HSO", "TGT")
    theta_host = _theta_space(host_orbit, t0)
    theta_own = _theta_space(_leo(40.0), t0)
    assert abs(theta_host - theta_own) > 1.0, "fixture: host vs own orbit must give distinct angles"
    rng = (0.0, theta_host - 2.0) if theta_host > 4.0 else (theta_host + 2.0, 180.0)
    g_out, _ = _observe(_space_world(hosted(usable_phase_angle_deg=rng), {"HOST": host}), "HSO", "TGT")
    assert g_out == pytest.approx(g_plain * phase_angle_factor(theta_host, rng))


@pytest.mark.verifies("FR-1670")
def test_ground_optical_gain_unchanged_inside_and_strictly_lower_outside():
    """Test 4 / AC7 — a ground-optical sensor (observer = ground site ECI at win.start)."""
    from spacesim.engine.access import AccessConfig  # noqa: F401  (documents the default twilight rule)

    tgt_orbit = _leo(0.0)
    found = None
    # Search candidate sites under the target's ground track for one with an access window.
    for k in range(0, 48):
        t = k * 15 * 60 * 1_000_000
        r, _ = PROP.rv(tgt_orbit, t)
        g = ecef_to_geodetic(eci_to_ecef(r, t))
        loc = GeoPoint(lat_deg=g.lat_deg, lon_deg=g.lon_deg)
        opt = Sensor(id="OPT", owner="blue", kind="ground_optical", location=loc, needs_lighting=True,
                     elevation_mask_deg=10.0)
        world = _space_world(opt)
        sim = Simulation(world, seed=7)
        osys = OrderSystem(sim, roe={"blue": {}, "red": {}})
        order = osys.issue(Order(cell="blue", actor="OPT", action="observe", target="TGT",
                                 params={"intent": "track"}))
        if order.status == "queued":
            found = loc
            break
    if found is None:
        pytest.skip("fixture: no ground-optical access window in 12 h for this orbit")

    def ground(**kw) -> Sensor:
        return Sensor(id="OPT", owner="blue", kind="ground_optical", location=found, needs_lighting=True,
                      elevation_mask_deg=10.0, **kw)

    g_plain, t0 = _observe(_space_world(ground()), "OPT", "TGT")
    r_t, _ = PROP.rv(tgt_orbit, t0)
    theta = cats_phase_angle_deg(r_t, ecef_to_eci(geodetic_to_ecef(found), t0), t0)
    g_in, _ = _observe(_space_world(ground(usable_phase_angle_deg=(0.0, min(180.0, theta + 1.0)))), "OPT", "TGT")
    assert g_in == pytest.approx(g_plain)
    rng = (0.0, theta - 5.0) if theta > 6.0 else (theta + 5.0, 180.0)
    g_out, t_out = _observe(_space_world(ground(usable_phase_angle_deg=rng)), "OPT", "TGT")
    assert t_out == t0
    assert g_out < g_plain
    assert g_out == pytest.approx(g_plain * phase_angle_factor(theta, rng))


# --------------------------------------------------------------------------- #
# Test 6 — validator (Design Decisions 4-5)
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1670")
@pytest.mark.parametrize("rng", [(90.0, 10.0), (-1.0, 90.0), (0.0, 181.0)])
def test_malformed_range_is_rejected(rng):
    with pytest.raises(ValidationError):
        Sensor.model_validate({"id": "X", "kind": "ground_optical", "needs_lighting": True,
                               "usable_phase_angle_deg": list(rng)})


@pytest.mark.verifies("FR-1670")
def test_range_on_a_non_passive_eo_sensor_is_rejected():
    with pytest.raises(ValidationError, match="usable_phase_angle_deg"):
        Sensor.model_validate({"id": "R", "kind": "ground_radar", "usable_phase_angle_deg": [0, 90]})


@pytest.mark.verifies("FR-1670")
def test_valid_range_on_a_passive_eo_sensor_is_accepted():
    s = Sensor.model_validate({"id": "X", "kind": "space_based", "needs_lighting": True,
                               "usable_phase_angle_deg": [0, 150]})
    assert tuple(s.usable_phase_angle_deg) == (0.0, 150.0)
    assert Sensor(id="Y").usable_phase_angle_deg is None


# --------------------------------------------------------------------------- #
# Test 7 — shipped content unchanged (AC10)
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("NFR-2010")
def test_no_shipped_vignette_sensor_declares_a_range():
    from spacesim.content.vignette import build_world, list_vignettes, load_vignette

    ids = [v["id"] for v in list_vignettes()]
    assert len(ids) >= 19
    for vid in ids:
        world, _ = build_world(load_vignette(vid))
        for s in world.sensors.values():
            assert s.usable_phase_angle_deg is None, (vid, s.id)
