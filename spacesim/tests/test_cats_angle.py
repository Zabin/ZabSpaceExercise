"""IP-1300 (FR-8220) — `engine/sun.py::cats_phase_angle_deg()`, the Sun-target-observer
illumination phase angle ("CATS angle"). Reference geometries are constructed directly from the
Sun direction (chaser placed along / against / perpendicular to it as seen from the target), not
derived from the implementation under test."""
from __future__ import annotations

import numpy as np
import pytest

from spacesim.engine import simtime
from spacesim.engine.geometry import R_EARTH_EQ
from spacesim.engine.sun import cats_phase_angle_deg, sun_unit_eci

_T = simtime.from_iso("2030-03-20T12:00:00Z")
_R_TARGET = np.array([R_EARTH_EQ + 700e3, 0.0, 0.0])


def _perpendicular(u: np.ndarray) -> np.ndarray:
    p = np.cross(u, np.array([0.0, 0.0, 1.0]))
    return p / np.linalg.norm(p)


@pytest.mark.verifies("FR-8220")
def test_zero_degrees_when_chaser_sits_between_target_and_sun():
    """Chaser on the target->Sun line: the target is fully lit as seen from the chaser."""
    sun = sun_unit_eci(_T)
    chaser = _R_TARGET + 50e3 * sun
    assert cats_phase_angle_deg(_R_TARGET, chaser, _T) == pytest.approx(0.0, abs=1e-6)


@pytest.mark.verifies("FR-8220")
def test_one_eighty_degrees_when_chaser_is_behind_target_from_sun():
    """Chaser opposite the Sun as seen from the target: backlit / silhouette."""
    sun = sun_unit_eci(_T)
    chaser = _R_TARGET - 50e3 * sun
    assert cats_phase_angle_deg(_R_TARGET, chaser, _T) == pytest.approx(180.0, abs=1e-6)


@pytest.mark.verifies("FR-8220")
def test_ninety_degrees_when_chaser_is_perpendicular_to_sun_line():
    """Chaser perpendicular to the target->Sun direction: side-lit."""
    sun = sun_unit_eci(_T)
    chaser = _R_TARGET + 50e3 * _perpendicular(sun)
    assert cats_phase_angle_deg(_R_TARGET, chaser, _T) == pytest.approx(90.0, abs=1e-6)


@pytest.mark.verifies("FR-8220")
def test_sixty_degrees_intermediate_geometry():
    sun = sun_unit_eci(_T)
    perp = _perpendicular(sun)
    direction = np.cos(np.radians(60.0)) * sun + np.sin(np.radians(60.0)) * perp
    chaser = _R_TARGET + 10e3 * direction
    assert cats_phase_angle_deg(_R_TARGET, chaser, _T) == pytest.approx(60.0, abs=1e-6)


@pytest.mark.verifies("FR-8220")
def test_coincident_chaser_and_target_is_rejected():
    with pytest.raises(ValueError):
        cats_phase_angle_deg(_R_TARGET, _R_TARGET.copy(), _T)


@pytest.mark.verifies("FR-8220")
def test_phase_angle_is_defined_only_once_in_engine():
    """VC item (Design Decision 2 / BL-0152): one shared phase-angle function in `engine/`."""
    from pathlib import Path

    engine = Path(__file__).resolve().parents[1] / "engine"
    hits = [p.name for p in engine.glob("*.py") if "def cats_phase_angle_deg" in p.read_text()]
    assert hits == ["sun.py"]


@pytest.mark.verifies("FR-1670")
def test_fr1670_observe_path_reuses_the_shared_phase_angle_function():
    """IP-1221 Test 8 (FS-122 AC11, BL-0152): the FR-1670 observe-gain refinement calls the one
    shared `cats_phase_angle_deg` rather than re-deriving the geometry."""
    from pathlib import Path

    engine = Path(__file__).resolve().parents[1] / "engine"
    assert "cats_phase_angle_deg" in (engine / "orders.py").read_text()
    hits = [p.name for p in engine.glob("*.py") if "def cats_phase_angle_deg" in p.read_text()]
    assert hits == ["sun.py"]
