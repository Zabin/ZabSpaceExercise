"""IP-1200 (FR-5510) — simulator_version() never raises, always returns a non-empty string."""
from __future__ import annotations

import pytest
from spacesim.version import simulator_version


@pytest.mark.verifies("FR-5510")
def test_simulator_version_never_raises_and_is_nonempty():
    v = simulator_version()
    assert isinstance(v, str)
    assert v != ""
