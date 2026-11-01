"""IP-1093 / NFR-1510: pyproject floors equal the release lock's pins for direct packages."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.verifies("NFR-1510")


def _norm(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def _lock():
    pins = {}
    for line in (ROOT / "requirements.lock").read_text().splitlines():
        m = re.match(r"^([A-Za-z0-9_.-]+)==(\S+)$", line.strip())
        if m:
            pins[_norm(m.group(1))] = m.group(2)
    return pins


def _floors():
    text = (ROOT / "pyproject.toml").read_text()
    return {_norm(n): v for n, v in re.findall(r'"([A-Za-z0-9_.-]+)>=([0-9][^",\s]*)"', text)}


def test_floors_equal_locked_pins():
    pins, floors = _lock(), _floors()
    assert floors, "no floors parsed from pyproject.toml"
    for name, floor in floors.items():
        if name in {"basemap", "basemap-data"}:
            continue
        assert name in pins, f"{name} has a floor but no lock pin"
        assert pins[name] == floor, f"{name}: floor {floor} != lock pin {pins[name]}"
