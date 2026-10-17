"""IP-1223 (FS-122 v1.2, FR-1610) — beam-mode choice follows the executing sensor's modality.

An observe order naming a beam mode the executing sensor's modality does not offer is refused
``invalid_param`` by both the preview (``dry_run``) and issue paths, before anything is scheduled.
It is never scored on another modality's table (before this package a ground radar asked for
``spotlight`` was scored on the imaging-SAR table, gain 1.8 > its own ``dish`` 1.6). An
auto-selected observe considers only the cell's sensors that offer the requested mode.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from spacesim.engine.entities import Asset, Sensor
from spacesim.engine.geometry import R_EARTH_EQ, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.isr import beam_params, effective_gain
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState

PROP = ModeratePropagator()
APP_JS = Path(__file__).resolve().parents[1] / "ui_web" / "static" / "app.js"


def _leo() -> OrbitState:
    return OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0,
                      ta_deg=0.0, epoch=0)


def _subpoint():
    r, _ = PROP.rv(_leo(), 0)
    g = ecef_to_geodetic(eci_to_ecef(r, 0))
    g.alt_m = 0.0
    return g


def _radar(sid: str = "RDR", **kw) -> Sensor:
    return Sensor(id=sid, owner="blue", kind="ground_radar", location=_subpoint(), **kw)


def _optical(sid: str = "OPT") -> Sensor:
    # Lighting-gated, so the observe path scores it on the EO table. The target satellite sits
    # over the site at t=0; lighting may still close the window, which only matters for tests
    # that expect a queued order (those use radars).
    return Sensor(id=sid, owner="blue", kind="ground_optical", location=_subpoint(),
                  needs_lighting=True)


def _world(*sensors: Sensor) -> WorldState:
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=_leo())
    for s in sensors:
        world.sensors[s.id] = s
    return world


def _osys(world: WorldState) -> tuple[Simulation, OrderSystem]:
    sim = Simulation(world, seed=11)
    return sim, OrderSystem(sim, roe={"blue": {}, "red": {}})


def _observe(world: WorldState, actor: str, params: dict, method: str = "issue"):
    sim, osys = _osys(world)
    order = getattr(osys, method)(Order(cell="blue", actor=actor, action="observe", target="TGT",
                                        params={"intent": "track", **params}))
    events = [tup[2] for tup in sim.scheduler._heap if tup[2].kind == "execute_observe"]
    return order, events


@pytest.mark.parametrize("method", ["issue", "dry_run"])
def test_radar_refuses_a_sar_mode(method):
    order, events = _observe(_world(_radar()), "RDR", {"beam_mode": "spotlight"}, method)
    assert order.status == "rejected"
    assert order.fail_reason == "invalid_param"
    assert events == []


def test_radar_own_modes_and_absent_mode_unchanged():
    gains = {}
    for mode in ("fence", "dish", None, "auto", ""):
        params = {} if mode is None else {"beam_mode": mode}
        order, events = _observe(_world(_radar()), "RDR", params)
        assert order.status == "queued", (mode, order.fail_reason)
        gains[mode] = events[0].payload["gain"]
    assert gains["fence"] == effective_gain(1.0, 0.0, beam_params("ground_radar", "fence")[0])
    assert gains["dish"] == effective_gain(1.0, 0.0, beam_params("ground_radar", "dish")[0])
    # No request (absent, "auto" or empty) keeps the radar's legacy isr_sar stripmap gain.
    legacy = effective_gain(1.0, 0.0, beam_params("isr_sar", None)[0])
    assert gains[None] == gains["auto"] == gains[""] == legacy


@pytest.mark.parametrize("method", ["issue", "dry_run"])
def test_optical_sensor_refuses_a_radar_mode(method):
    order, events = _observe(_world(_optical()), "OPT", {"beam_mode": "fence"}, method)
    assert order.status == "rejected"
    assert order.fail_reason == "invalid_param"
    assert events == []


def test_auto_picks_a_sensor_offering_the_requested_mode():
    order, events = _observe(_world(_optical("A-OPT"), _radar("Z-RDR")), "auto", {"beam_mode": "dish"})
    assert order.status == "queued", order.fail_reason
    assert order.actor == "Z-RDR"
    assert events[0].payload["beam_mode"] == "dish"


@pytest.mark.parametrize("method", ["issue", "dry_run"])
def test_auto_refuses_a_mode_no_own_sensor_offers(method):
    order, events = _observe(_world(_radar("R1"), _radar("R2")), "auto", {"beam_mode": "polarimetric"},
                             method)
    assert order.status == "rejected"
    assert order.fail_reason == "invalid_param"
    assert events == []


def test_console_builds_the_mode_list_from_the_tasked_sensor():
    js = APP_JS.read_text(encoding="utf-8")
    assert "function beamModesForSensor" in js
    assert "ground_radar" in js and '"fence"' in js and '"dish"' in js
    assert "populateBeamModes" in js
