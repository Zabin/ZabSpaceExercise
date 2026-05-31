"""Custody: confidence decay, observation reset, and the weapons-quality gate."""

from __future__ import annotations

from spacesim.engine.custody import Track, observe
from spacesim.engine.simtime import minutes


def test_confidence_decays_with_time_and_resets_on_observation():
    tr = Track(object="OBJ", owner="blue", last_observation=0, confidence=1.0, characterized=True)
    assert tr.current_confidence(0) == 1.0
    # 30-min half-life: ~0.5 after 30 min, lower after 60.
    assert abs(tr.current_confidence(minutes(30)) - 0.5) < 1e-6
    assert tr.current_confidence(minutes(60)) < tr.current_confidence(minutes(30))

    observe(tr, minutes(60), quality=1.0)
    assert tr.last_observation == minutes(60)
    assert tr.current_confidence(minutes(60)) == 1.0


def test_weapons_quality_requires_characterized_and_confidence():
    tr = Track(object="OBJ", owner="blue", last_observation=0, confidence=1.0, characterized=False)
    assert not tr.is_weapons_quality(0)            # not characterized yet
    observe(tr, 0, quality=1.0, characterizes=True)
    assert tr.is_weapons_quality(0)                # fresh + characterized
    assert not tr.is_weapons_quality(minutes(120))  # confidence decayed below threshold


def test_uncertainty_grows_between_observations_and_collapses_on_report():
    tr = Track(object="OBJ", owner="blue", last_observation=0)
    assert tr.current_uncertainty_km(0) == 0.0
    grown = tr.current_uncertainty_km(minutes(30))
    assert grown > 0.0
    observe(tr, minutes(30))
    assert tr.current_uncertainty_km(minutes(30)) == 0.0
