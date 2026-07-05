"""IP-2010 — Competency Assessment: rubric-tier scoring functions.

Headless, driven directly through Simulation + OrderSystem (no session/vignette layer needed —
mirrors test_orders.py's style). ``_Mgr`` is a minimal duck type carrying just ``.sim``/``.osys``,
the only two attributes ``session/assessment.py`` and ``aar.state_at`` actually read.
"""

from __future__ import annotations

from dataclasses import dataclass

from spacesim.engine.custody import Track
from spacesim.engine.entities import Asset, AssetResources
from spacesim.engine.geometry import R_EARTH_EQ, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simtime import minutes
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState
from spacesim.session import assessment

PROP = ModeratePropagator()


@dataclass
class _Mgr:
    sim: Simulation
    osys: OrderSystem


def _leo(ta: float = 0.0, raan: float = 33.0) -> OrbitState:
    return OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=raan, argp_deg=0, ta_deg=ta, epoch=0)


def _subpoint(orbit: OrbitState, t: int):
    r, _ = PROP.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    g.alt_m = 0.0
    return g


def _mgr(world: WorldState, roe=None, seed=1) -> _Mgr:
    # IP-1172: OrderSystem.roe is now always cell-keyed; mirror a flat convenience dict to
    # both cells (matches content/vignette.py's own legacy-parameter fallback semantics).
    if roe is not None and "blue" not in roe and "red" not in roe:
        roe = {"blue": dict(roe), "red": dict(roe)}
    sim = Simulation(world, seed=seed)
    osys = OrderSystem(sim, roe=roe)
    return _Mgr(sim=sim, osys=osys)


def _jam_order(mgr: _Mgr, cell: str, target: str, actor: str) -> Order:
    order = mgr.osys.issue(Order(cell=cell, actor=actor, action="jam", target=target,
                                 params={"modulation": "barrage", "power_w": 200.0}))
    assert order.status == "queued"
    mgr.sim.advance_to(order.earliest_window[0] + 1)
    return order


def _read_only_tests_setup():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["JAM"] = Asset(id="JAM", owner="blue", kind="jammer",
                                location=_subpoint(sat, minutes(40)))
    return sat, world


# -- score_custody_quality ---------------------------------------------------------------------

def test_custody_quality_disciplined_when_confidence_stays_high():
    sat, world = _read_only_tests_setup()
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.95, characterized=True))
    mgr = _mgr(world)
    _jam_order(mgr, "blue", "RSAT", "JAM")
    assert assessment.score_custody_quality(mgr, "blue") == "disciplined"


def test_custody_quality_speculative_when_confidence_is_low():
    sat, world = _read_only_tests_setup()
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.2, characterized=True))
    mgr = _mgr(world)
    _jam_order(mgr, "blue", "RSAT", "JAM")
    assert assessment.score_custody_quality(mgr, "blue") == "speculative"


def test_custody_quality_defaults_to_speculative_with_no_qualifying_decisions():
    _, world = _read_only_tests_setup()
    mgr = _mgr(world)
    assert assessment.score_custody_quality(mgr, "blue") == "speculative"
    assert assessment.score_custody_quality(mgr, "red") == "speculative"


# -- score_window_discipline --------------------------------------------------------------------

def test_window_discipline_disciplined_with_zero_rejections():
    sat, world = _read_only_tests_setup()
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.9, characterized=True))
    mgr = _mgr(world)
    _jam_order(mgr, "blue", "RSAT", "JAM")
    assert assessment.score_window_discipline(mgr, "blue") == "disciplined"


def test_window_discipline_frequent_invalid_attempts_with_high_rejection_rate():
    sat = _leo()
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    mgr = _mgr(world, roe={"kinetic_authorized": False})
    rej = mgr.osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert rej.status == "rejected"
    assert assessment.score_window_discipline(mgr, "blue") == "frequent-invalid-attempts"


def test_window_discipline_no_orders_defaults_to_disciplined():
    _, world = _read_only_tests_setup()
    mgr = _mgr(world)
    assert assessment.score_window_discipline(mgr, "blue") == "disciplined"


# -- score_belief_truth_divergence ----------------------------------------------------------------

def test_belief_truth_divergence_low_when_belief_matches_truth():
    sat, world = _read_only_tests_setup()
    # The track's believed orbit IS the true orbit — no divergence.
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.95,
                              characterized=True, state_estimate=sat))
    mgr = _mgr(world)
    _jam_order(mgr, "blue", "RSAT", "JAM")
    assert assessment.score_belief_truth_divergence(mgr, "blue") == "low-divergence"


def test_belief_truth_divergence_unaware_when_confidence_is_high_but_belief_is_wrong():
    sat, world = _read_only_tests_setup()
    # Believed position is the opposite side of the orbit (ta=180) from the true position
    # (ta=0) — thousands of km apart, far beyond the track's (tiny, freshly-reset) uncertainty
    # band — while confidence is high (>= WEAPONS_QUALITY_THRESHOLD): nothing visible to the
    # operator suggested staleness.
    wrong_belief = _leo(ta=180.0)
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.95,
                              characterized=True, state_estimate=wrong_belief))
    mgr = _mgr(world)
    _jam_order(mgr, "blue", "RSAT", "JAM")
    assert assessment.score_belief_truth_divergence(mgr, "blue") == "high-divergence-unaware"


def test_belief_truth_divergence_aware_when_confidence_is_low_and_belief_is_wrong():
    sat, world = _read_only_tests_setup()
    wrong_belief = _leo(ta=180.0)
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.3,
                              characterized=True, state_estimate=wrong_belief))
    mgr = _mgr(world)
    _jam_order(mgr, "blue", "RSAT", "JAM")
    assert assessment.score_belief_truth_divergence(mgr, "blue") == "high-divergence-aware"


def test_belief_truth_divergence_defaults_to_low_with_no_qualifying_decisions():
    _, world = _read_only_tests_setup()
    mgr = _mgr(world)
    assert assessment.score_belief_truth_divergence(mgr, "blue") == "low-divergence"


# -- read-only / no composite score ---------------------------------------------------------------

def test_scoring_functions_never_mutate_world_state():
    sat, world = _read_only_tests_setup()
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.9,
                              characterized=True, state_estimate=sat))
    mgr = _mgr(world)
    _jam_order(mgr, "blue", "RSAT", "JAM")
    before = mgr.sim.world.model_dump_json()
    assessment.score_custody_quality(mgr, "blue")
    assessment.score_window_discipline(mgr, "blue")
    assessment.score_belief_truth_divergence(mgr, "blue")
    assessment.assessment_report(mgr)
    assert mgr.sim.world.model_dump_json() == before


def test_assessment_report_presents_dimensions_side_by_side_never_a_composite():
    sat, world = _read_only_tests_setup()
    world.tracks.append(Track(object="RSAT", owner="blue", last_observation=0, confidence=0.9,
                              characterized=True, state_estimate=sat))
    mgr = _mgr(world)
    _jam_order(mgr, "blue", "RSAT", "JAM")
    rep = assessment.assessment_report(mgr)
    assert set(rep.keys()) == {"blue", "red"}
    for cell_report in rep.values():
        assert set(cell_report.keys()) == {
            "custody_quality", "window_discipline", "belief_truth_divergence", "disclosure",
        }
        # None of the deferred dimensions (resource economy, escalation discipline,
        # time-to-decision) are present, not even as a default/null value.
        assert "resource_economy" not in cell_report
        assert "escalation_discipline" not in cell_report
        assert "time_to_decision" not in cell_report
        assert not isinstance(cell_report["custody_quality"], (int, float))


def test_belief_truth_divergence_reads_recorded_confidence_not_replay_recomputed():
    """The classic differentiating fixture (IP-2010 v1.1 Tests to Add): decay the track further
    between issue and this check so a post-hoc recompute via current_confidence() would give a
    *different* (lower) value than what was captured at issue time — proving the scorer used the
    stored custody_confidence_at_decision, not a live/replay recomputation.
    """
    sat, world = _read_only_tests_setup()
    track = Track(object="RSAT", owner="blue", last_observation=0, confidence=0.3, characterized=True,
                  state_estimate=_leo(ta=180.0))
    world.tracks.append(track)
    mgr = _mgr(world)
    order = _jam_order(mgr, "blue", "RSAT", "JAM")

    entry = next(e for e in mgr.sim.eventlog.entries if e.kind == "execute_effect")
    recorded = entry.payload["custody_confidence_at_decision"]
    # Confidence has decayed further by "now" than it was at the decision — if the scorer
    # recomputed instead of reading the recorded field, it would see a lower value here.
    much_later_confidence = track.current_confidence(order.earliest_window[0] + minutes(120))
    assert much_later_confidence < recorded
    # The classification (aware, since recorded confidence 0.3 < WEAPONS_QUALITY_THRESHOLD) must
    # still hold — it is driven by the recorded field, unaffected by the track's further decay.
    assert assessment.score_belief_truth_divergence(mgr, "blue") == "high-divergence-aware"
