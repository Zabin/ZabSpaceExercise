"""Mock SSN: coverage matrix, hybrid turnaround, fog, determinism, custody-loop integration.

Implements the acceptance bullets in `docs/SSN-DESIGN.md` §15. The engine's `AccessProvider`,
`Track`, and scheduler are reused — the SSN is a thin layer on top of them, so these tests are
narrow on the request lifecycle and on observable end-state effects.
"""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.access import COMMAND_UPLINK
from spacesim.engine.entities import GeoPoint
from spacesim.engine.geometry import R_EARTH_EQ
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order
from spacesim.engine.ssn import (
    COALITION_DELAY_MULTIPLIER, PROCESSING_DELAY_S, SSNRequest,
    instantiate_network,
)
from spacesim.engine.world import WorldState
from spacesim.engine.entities import Asset
from spacesim.engine.simtime import minutes
from spacesim.engine.simulation import Simulation
from spacesim.session.manager import SessionManager


def _leo_target(now: int = 0) -> Asset:
    return Asset(id="TGT", owner="red", kind="satellite",
                 orbit=OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6,
                                  raan_deg=0.0, argp_deg=0.0, ta_deg=0.0, epoch=now))


def _geo_target(now: int = 0) -> Asset:
    return Asset(id="TGT", owner="red", kind="satellite",
                 orbit=OrbitState(a_m=42_164_000.0, e=0.0, i_deg=0.0,
                                  raan_deg=0.0, argp_deg=0.0, ta_deg=0.0, epoch=now))


def _mgr_with_network(dispersion: str, *, target_factory=_leo_target) -> SessionManager:
    """Hand-build a session with a network instantiated for Blue + a single Red target satellite."""
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.world.assets.clear()
    mgr.world.assets["TGT"] = target_factory(mgr.sim.clock.now)
    mgr.world.sensors.clear()
    net = instantiate_network(mgr.world, "blue", dispersion)
    mgr.ssn.networks["blue"] = net
    mgr.ssn._inflight["blue"] = 0
    mgr.sim._initial_state = mgr.world.model_dump()       # re-baseline for replay-identity
    mgr.start()
    return mgr


# ---- coverage matrix (§5) ----------------------------------------------------

def test_sparse_radar_net_cannot_service_geo():
    mgr = _mgr_with_network("sparse", target_factory=_geo_target)
    ack = mgr.submit_ssn_request("blue", "characterize", "TGT", "GEO", "priority")
    assert not ack.ok and ack.reason == "no_coverage_regime"


def test_global_net_services_geo_request():
    mgr = _mgr_with_network("global", target_factory=_geo_target)
    cov = mgr.ssn_coverage("blue", "GEO")
    assert cov["covered"] and cov["sensors"]
    ack = mgr.submit_ssn_request("blue", "characterize", "TGT", "GEO", "priority")
    # Either scheduled (if a window exists in 1h SLA) or no_coverage_within_sla — but never the
    # regime-eligibility failure that the sparse case hits.
    assert ack.reason != "no_coverage_regime"


def test_leo_serviceable_by_every_non_empty_dispersion():
    for d in ("sparse", "regional", "global", "proliferated"):
        cov = _mgr_with_network(d).ssn_coverage("blue", "LEO")
        assert cov["covered"], f"{d} expected to cover LEO"


# ---- hybrid turnaround (§7) --------------------------------------------------

def test_hybrid_turnaround_within_sla_and_processing_delay_applied():
    mgr = _mgr_with_network("global")
    ack = mgr.submit_ssn_request("blue", "track", "TGT", "LEO", "priority")
    assert ack.ok, ack.reason
    now = mgr.sim.clock.now
    # collect_at lies in the SLA horizon.
    assert ack.collect_at >= now
    assert ack.collect_at - now <= 3600 * 1_000_000
    # product_at = collect_at + processing_delay × coalition-multiplier (Blue defaults to coalition).
    expected_delay = int(PROCESSING_DELAY_S["priority"] * COALITION_DELAY_MULTIPLIER) * 1_000_000
    assert ack.product_at == ack.collect_at + expected_delay


def test_national_red_network_uses_raw_processing_delay():
    mgr = SessionManager(load_vignette("training-basics"), seed=2)
    mgr.world.assets.clear()
    mgr.world.assets["TGT"] = _leo_target(mgr.sim.clock.now)
    mgr.world.sensors.clear()
    mgr.ssn.networks["red"] = instantiate_network(mgr.world, "red", "global")
    mgr.ssn._inflight["red"] = 0
    mgr.sim._initial_state = mgr.world.model_dump()
    mgr.start()
    ack = mgr.submit_ssn_request("red", "track", "TGT", "LEO", "priority")
    assert ack.ok
    assert ack.product_at == ack.collect_at + PROCESSING_DELAY_S["priority"] * 1_000_000


# ---- fog (§8) ----------------------------------------------------------------

def test_fog_blocks_other_cell_from_seeing_requests_and_coverage():
    mgr = _mgr_with_network("global")
    mgr.submit_ssn_request("blue", "track", "TGT", "LEO", "priority")
    # Red has no network configured here → coverage is empty + the cell sees no Blue requests.
    assert mgr.ssn_coverage("red", "LEO") == {"covered": False, "sensors": [], "next_window": None}
    assert mgr.list_ssn_requests("red") == []
    assert mgr.list_ssn_requests("blue") and mgr.list_ssn_requests("blue")[0]["target"] == "TGT"
    # White sees both.
    assert any(r["target"] == "TGT" for r in mgr.list_ssn_requests("white"))


# ---- delivery + custody loop (§7.3, §15) -------------------------------------

def test_delivery_updates_track_and_replay_is_byte_identical():
    mgr = _mgr_with_network("global")
    ack = mgr.submit_ssn_request("blue", "characterize", "TGT", "LEO", "priority")
    assert ack.ok
    mgr.advance_to(ack.product_at + 1)
    # The track is now in Blue's catalog with characterized=True and a state estimate.
    tracks = [t for t in mgr.world.tracks if t.owner == "blue" and t.object == "TGT"]
    assert tracks and tracks[0].characterized
    # Replay reproduces world state exactly (ssn_collect + ssn_deliver are logged events).
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_cancel_before_collect_is_replay_safe():
    mgr = _mgr_with_network("global")
    ack = mgr.submit_ssn_request("blue", "track", "TGT", "LEO", "routine")
    assert ack.ok
    assert mgr.cancel_ssn_request("blue", ack.id) is True
    # Advance past where the events would have fired; nothing should land in the track catalog.
    mgr.advance_to(ack.product_at + 1)
    assert not any(t.owner == "blue" and t.object == "TGT" for t in mgr.world.tracks)
    # And the cancelled events never logged, so replay is byte-identical.
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_characterize_via_ssn_unlocks_engage_gate():
    """An SSN characterize that yields a weapons-quality track unlocks a previously-blocked engage."""
    mgr = _mgr_with_network("global")
    # Give Blue a kinetic effector with ammo + ROE so only the WQ-track gate is the obstacle.
    mgr.world.assets["BLUE-KIL"] = Asset(id="BLUE-KIL", owner="blue", kind="interceptor",
                                         location=GeoPoint(lat_deg=0.0, lon_deg=0.0, alt_m=0.0))
    mgr.world.assets["BLUE-KIL"].resources.ammo = 1
    mgr.osys.roe["kinetic_authorized"] = True
    mgr.sim._initial_state = mgr.world.model_dump()
    # Pre-check: engage refused for "no_weapons_quality_track".
    ack0 = mgr.validate_order("blue", Order(cell="blue", actor="BLUE-KIL", action="engage", target="TGT"))
    assert ack0.reason == "no_weapons_quality_track"
    # Submit a characterize and advance past delivery; then engage should at least no longer be
    # blocked on the WQ gate (it may still be blocked by no_window — that's a separate gate).
    ack = mgr.submit_ssn_request("blue", "characterize", "TGT", "LEO", "priority")
    mgr.advance_to(ack.product_at + 1)
    ack1 = mgr.validate_order("blue", Order(cell="blue", actor="BLUE-KIL", action="engage", target="TGT"))
    assert ack1.reason != "no_weapons_quality_track"
