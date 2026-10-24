"""IP-1067 (FS-106 v2.3, FR-4620) — the side-by-side controller view: ground truth plus Blue's and
Red's own views, one simulated instant, each panel exactly the existing god-view / FR-4610 view-as
result; read-only; White-only over HTTP."""
from __future__ import annotations

import pytest

from spacesim.session.inprocess import InProcessSession

HALF_HOUR = 1800 * 1_000_000


@pytest.fixture()
def api_sid():
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=4)
    api.start(sid)
    mgr = api._sessions[sid]
    mgr.set_clock(False)
    mgr.advance_to(mgr.ctx.start_epoch + HALF_HOUR)
    return api, sid, mgr


@pytest.mark.verifies("FR-4620")
def test_panels_equal_godview_and_each_cells_view(api_sid):
    api, sid, mgr = api_sid
    cv = mgr.controller_view()
    assert set(cv) == {"now", "truth", "blue", "red"}
    assert cv["now"] == mgr.world.now
    assert cv["truth"] == mgr.get_godview().model_dump()
    assert cv["blue"] == mgr.get_view("blue").model_dump()
    assert cv["red"] == mgr.get_view("red").model_dump()


@pytest.mark.verifies("FR-4620")
def test_single_instant_through_the_locked_api(api_sid):
    api, sid, mgr = api_sid
    cv = api.controller_view(sid)
    assert cv["truth"]["now"] == cv["blue"]["now"] == cv["red"]["now"] == cv["now"]


@pytest.mark.verifies("FR-4620")
def test_each_cell_panel_is_fog_filtered(api_sid):
    api, sid, mgr = api_sid
    cv = mgr.controller_view()
    assert all(a["owner"] == "blue" for a in cv["blue"]["own_assets"])
    assert all(a["owner"] == "red" for a in cv["red"]["own_assets"])
    assert all(t["owner"] == "blue" for t in cv["blue"]["known_tracks"])
    assert all(t["owner"] == "red" for t in cv["red"]["known_tracks"])


@pytest.mark.verifies("FR-4620", "NFR-2410")
def test_read_only(api_sid):
    api, sid, mgr = api_sid
    before = mgr.world.model_dump()
    n = len(mgr.sim.eventlog.entries)
    mgr.controller_view()
    api.controller_view(sid)
    assert mgr.world.model_dump() == before
    assert len(mgr.sim.eventlog.entries) == n


@pytest.fixture()
def client(api_sid):
    from fastapi.testclient import TestClient
    from spacesim.ui_web.server import create_app
    api, sid, mgr = api_sid
    return TestClient(create_app(api)), sid


@pytest.mark.verifies("FR-4620")
def test_http_white_gets_the_four_panels(client):
    c, sid = client
    r = c.get(f"/api/sessions/{sid}/controller_view?cell=white")
    assert r.status_code == 200
    assert set(r.json()) == {"now", "truth", "blue", "red"}


@pytest.mark.verifies("FR-4620")
@pytest.mark.parametrize("cell", ["blue", "red", "observer", None])
def test_http_non_white_is_403(client, cell):
    c, sid = client
    q = f"?cell={cell}" if cell else ""
    assert c.get(f"/api/sessions/{sid}/controller_view{q}").status_code == 403


@pytest.mark.verifies("FR-4620")
def test_http_unknown_session_is_404(client):
    c, sid = client
    assert c.get("/api/sessions/nope/controller_view?cell=white").status_code == 404
