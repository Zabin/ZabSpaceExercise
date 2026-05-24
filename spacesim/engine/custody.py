"""SDA custody / tracks with confidence decay and the weapons-quality gate (``04-data-model.md`` §5).

A cell's knowledge of an object is a ``Track`` whose confidence **decays with time since the last
observation** and is **reset by an observation window**; uncertainty volumes grow between
observations and shrink on report. A "weapons-quality track" (confidence above threshold AND
characterized) is the gate other subsystems read before allowing an engagement. Confidence is
stored as the value at ``last_observation`` and decayed on demand, so the model is a pure function
of time (no hidden mutation) and stays deterministic under replay.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from spacesim.engine.orbit import OrbitState

DEFAULT_HALF_LIFE_S = 1800.0          # confidence halves every 30 min without observation
DEFAULT_GROWTH_KM_PER_S = 0.02        # uncertainty growth rate between observations
WEAPONS_QUALITY_THRESHOLD = 0.8


class TrackUncertainty(BaseModel):
    along_track_km: float = 0.0
    radial_km: float = 0.0
    cross_track_km: float = 0.0


class Track(BaseModel):
    object: str
    owner: str                         # the cell holding this track
    last_observation: int = 0
    confidence: float = 1.0            # value AT last_observation
    characterized: bool = False
    classification: str = "unknown"    # friend|hostile|neutral|unknown
    state_estimate: Optional[OrbitState] = None
    uncertainty: TrackUncertainty = Field(default_factory=TrackUncertainty)
    uncertainty_at_obs: TrackUncertainty = Field(default_factory=TrackUncertainty)
    source: str = "own_sensor"

    def current_confidence(self, now: int, half_life_s: float = DEFAULT_HALF_LIFE_S) -> float:
        dt = max(0.0, (now - self.last_observation) / 1_000_000)
        return self.confidence * (0.5 ** (dt / half_life_s))

    def current_uncertainty_km(self, now: int, growth: float = DEFAULT_GROWTH_KM_PER_S) -> float:
        dt = max(0.0, (now - self.last_observation) / 1_000_000)
        return self.uncertainty_at_obs.along_track_km + growth * dt

    def is_weapons_quality(self, now: int, threshold: float = WEAPONS_QUALITY_THRESHOLD) -> bool:
        return self.characterized and self.current_confidence(now) >= threshold


def observe(
    track: Track,
    now: int,
    quality: float = 1.0,
    characterizes: bool = True,
    classification: Optional[str] = None,
) -> None:
    """Apply a sensor report: reset confidence/last-observation and collapse the uncertainty volume."""
    track.confidence = max(0.0, min(1.0, quality))
    track.last_observation = now
    track.uncertainty = TrackUncertainty()
    track.uncertainty_at_obs = TrackUncertainty()
    if characterizes:
        track.characterized = True
    if classification is not None:
        track.classification = classification
