"""IP-1091 — the clock-lag watchdog (NFR-1300). Synthetic wall costs are fed straight to
``SessionManager._record_catch_up_lag`` (the method NFR-1300 names as its verification target), so
there is no real timing and no sleep."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.content.vignette import load_vignette  # noqa: E402
from spacesim.session.manager import SessionManager  # noqa: E402
from spacesim.ui_web.server import create_app  # noqa: E402

pytestmark = pytest.mark.verifies("NFR-1300")


def _mgr() -> SessionManager:
    return SessionManager(load_vignette("leo-isr-denial"), seed=1)


def _feed(mgr, samples):
    for s in samples:
        mgr._record_catch_up_lag(s, 0)


def test_fewer_than_four_samples_never_warn():
    mgr = _mgr()
    _feed(mgr, [5.0, 5.0, 5.0])
    assert mgr.clock_state()["lag_warning"] is None


def test_four_samples_above_threshold_give_a_medium_warning():
    mgr = _mgr()
    _feed(mgr, [0.5, 0.5, 0.5, 0.5])
    w = mgr.clock_state()["lag_warning"]
    assert w["severity"] == "medium"
    assert w["avg_wall_cost_s"] == 0.5
    assert w["asset_count"] == len(mgr.world.assets)
    assert "0.50s" in w["message"] and str(len(mgr.world.assets)) in w["message"]


def test_average_above_point_eight_is_high():
    mgr = _mgr()
    _feed(mgr, [1.0, 1.0, 1.0, 1.0])
    assert mgr.clock_state()["lag_warning"]["severity"] == "high"


def test_average_falling_below_threshold_clears_the_warning():
    mgr = _mgr()
    _feed(mgr, [0.5] * 4)
    assert mgr.clock_state()["lag_warning"] is not None
    _feed(mgr, [0.01] * 8)   # the ring now holds only cheap samples
    assert mgr.clock_state()["lag_warning"] is None


def test_only_the_last_eight_samples_count():
    mgr = _mgr()
    _feed(mgr, [100.0])      # an old spike
    _feed(mgr, [0.1] * 8)    # eight newer samples push it out
    assert len(mgr._catch_up_lag_history) == 8
    assert mgr.clock_state()["lag_warning"] is None


def test_warning_reaches_white_through_the_clock_route():
    app = create_app()
    c = TestClient(app)
    sid = c.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    mgr = app.state.api._sessions[sid]
    _feed(mgr, [0.9] * 4)
    got = c.get(f"/api/sessions/{sid}/clock").json()["lag_warning"]
    assert got == mgr.clock_state()["lag_warning"]
    assert got["severity"] == "high"
