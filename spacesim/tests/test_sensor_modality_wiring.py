"""IP-1222 — sensor-modality wiring remediation (FR-1610, FR-1630, FR-1640).

Remediates three gaps in the IP-1220 wiring found by pipeline run #127:
- BL-0212: a ground radar's fence/dish beam modes were never selected by an observe order.
- BL-0213: ``auto`` sensor selection skipped the ``requires_cue`` gate.
- BL-0214: ``altitude_band_affinity`` was an unchecked string compared exactly.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from spacesim.engine.custody import Track
from spacesim.engine.entities import Asset, Sensor
from spacesim.engine.geometry import R_EARTH_EQ, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.isr import beam_params, effective_gain
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState

PROP = ModeratePropagator()
VIGNETTE_DIR = Path(__file__).resolve().parents[1] / "content" / "vignettes"


def _leo(ta: float = 0.0) -> OrbitState:
    return OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0,
                      ta_deg=ta, epoch=0)


def _subpoint(orbit: OrbitState, t: int):
    r, _ = PROP.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    g.alt_m = 0.0
    return g


def _world(*sensors: Sensor, track: bool = False) -> WorldState:
    sat = _leo()
    world = WorldState(now=0)
    world.assets["TGT"] = Asset(id="TGT", owner="red", kind="satellite", orbit=sat)
    for s in sensors:
        world.sensors[s.id] = s
    if track:
        world.tracks.append(Track(object="TGT", owner="blue", last_observation=0, confidence=0.5))
    return world


def _radar(sid: str = "RDR", **kw) -> Sensor:
    return Sensor(id=sid, owner="blue", kind="ground_radar", location=_subpoint(_leo(), 0), **kw)


def _osys(world: WorldState) -> tuple[Simulation, OrderSystem]:
    sim = Simulation(world, seed=7)
    return sim, OrderSystem(sim, roe={"blue": {}, "red": {}})


def _observe_payload(world: WorldState, actor: str, params: dict | None = None) -> dict:
    sim, osys = _osys(world)
    order = osys.issue(Order(cell="blue", actor=actor, action="observe", target="TGT",
                             params={"intent": "track", **(params or {})}))
    assert order.status == "queued", order.fail_reason
    ev = [tup[2] for tup in sim.scheduler._heap if tup[2].kind == "execute_observe"]
    assert len(ev) == 1
    return dict(ev[0].payload)


# --------------------------------------------------------------------------- #
# Tests 1-3 — FR-1610 radar beam modes reached end to end (BL-0212)
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1610")
def test_radar_beam_mode_by_order_param_end_to_end():
    fence = _observe_payload(_world(_radar()), "RDR", {"beam_mode": "fence"})
    dish = _observe_payload(_world(_radar()), "RDR", {"beam_mode": "dish"})
    none = _observe_payload(_world(_radar()), "RDR")
    assert fence["beam_mode"] == "fence"
    assert dish["beam_mode"] == "dish"
    assert none["beam_mode"] == "stripmap"
    assert fence["gain"] < none["gain"] < dish["gain"]
    # A radar naming no radar mode keeps today's isr_sar stripmap gain.
    legacy_bp, _ = beam_params("isr_sar", None)
    assert none["gain"] == effective_gain(1.0, 0.0, legacy_bp)


@pytest.mark.verifies("FR-1610")
def test_radar_beam_mode_by_sensor_declaration_and_param_override():
    declared = _observe_payload(_world(_radar(beam_mode="fence")), "RDR")
    assert declared["beam_mode"] == "fence"
    overridden = _observe_payload(_world(_radar(beam_mode="fence")), "RDR", {"beam_mode": "dish"})
    assert overridden["beam_mode"] == "dish"
    assert declared["gain"] < overridden["gain"]


@pytest.mark.verifies("FR-1610")
def test_radar_beam_mode_validator():
    with pytest.raises(ValidationError):
        _radar(beam_mode="wiggle")
    assert _radar(beam_mode="fence").beam_mode == "fence"
    assert _radar(beam_mode="dish").beam_mode == "dish"
    # Non-radar sensors are not checked (their table depends on the asset's payload type).
    Sensor(id="OPT", owner="blue", kind="ground_optical", location=_subpoint(_leo(), 0),
           needs_lighting=True, beam_mode="anything")


# --------------------------------------------------------------------------- #
# Tests 4-6 — FR-1640 cue gate on auto-selection (BL-0213)
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1640")
@pytest.mark.parametrize("method", ["issue", "dry_run"])
def test_auto_respects_cue_gate(method):
    world = _world(_radar(requires_cue=True))
    _, osys = _osys(world)
    order = getattr(osys, method)(Order(cell="blue", actor="auto", action="observe", target="TGT",
                                        params={"intent": "track"}))
    assert order.status == "rejected"
    assert order.fail_reason == "requires_cue"

    world = _world(_radar(requires_cue=True), track=True)
    _, osys = _osys(world)
    order = getattr(osys, method)(Order(cell="blue", actor="auto", action="observe", target="TGT",
                                        params={"intent": "track"}))
    assert order.status == "queued", order.fail_reason
    assert order.actor == "RDR"


@pytest.mark.verifies("FR-1640")
def test_auto_falls_through_to_sensor_without_cue_requirement():
    world = _world(_radar("CUE", requires_cue=True), _radar("PLAIN"))
    _, osys = _osys(world)
    order = osys.issue(Order(cell="blue", actor="auto", action="observe", target="TGT",
                             params={"intent": "track"}))
    assert order.status == "queued", order.fail_reason
    assert order.actor == "PLAIN"


@pytest.mark.verifies("FR-1640")
def test_auto_with_no_sensor_keeps_existing_reason():
    world = _world()
    _, osys = _osys(world)
    order = osys.issue(Order(cell="blue", actor="auto", action="observe", target="TGT",
                             params={"intent": "track"}))
    assert order.status == "rejected"
    assert order.fail_reason == "no_window"


# --------------------------------------------------------------------------- #
# Tests 7-8 — FR-1630 typed, band-compared affinity (BL-0214)
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("FR-1630")
def test_altitude_band_affinity_is_typed():
    with pytest.raises(ValidationError):
        Sensor(id="S", owner="blue", kind="space_based", orbit=_leo(), altitude_band_affinity="leo")
    for regime in ("LEO", "LEO_SSO", "MEO", "GEO", "HEO", "CISLUNAR"):
        Sensor(id="S", owner="blue", kind="space_based", orbit=_leo(), altitude_band_affinity=regime)


@pytest.mark.verifies("FR-1630")
def test_band_affinity_treats_leo_and_leo_sso_as_one_band():
    bp, _ = beam_params("sda", "nominal")
    base = effective_gain(1.0, 0.0, bp)
    assert effective_gain(1.0, 0.0, bp, target_regime="LEO_SSO", band_affinity="LEO") == base
    assert effective_gain(1.0, 0.0, bp, target_regime="LEO", band_affinity="LEO_SSO") == base
    assert effective_gain(1.0, 0.0, bp, target_regime="GEO", band_affinity="LEO") == pytest.approx(base * 0.5)
    assert effective_gain(1.0, 0.0, bp, target_regime="MEO", band_affinity="GEO") == pytest.approx(base * 0.5)


# --------------------------------------------------------------------------- #
# Test 9 — shipped content unchanged
# --------------------------------------------------------------------------- #

@pytest.mark.verifies("NFR-2010")
def test_shipped_vignettes_declare_none_of_the_remediated_fields():
    from spacesim.content.vignette import build_world, load_vignette

    files = sorted(VIGNETTE_DIR.glob("*.yaml"))
    assert files
    for path in files:
        doc = yaml.safe_load(path.read_text())
        vid = (doc.get("vignette") or doc).get("id")
        v = load_vignette(vid)
        build_world(v)
        for s in v.sensors:
            assert "beam_mode" not in s, (vid, s.get("id"))
            assert not s.get("requires_cue"), (vid, s.get("id"))
            assert "altitude_band_affinity" not in s, (vid, s.get("id"))
