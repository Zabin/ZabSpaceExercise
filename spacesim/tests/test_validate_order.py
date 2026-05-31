"""Dry-run order validation (`OrderSystem.dry_run` / `SessionManager.validate_order`).

Powers the operator console's "why can't I?" pre-disabled buttons + window preview
(`docs/build-spec/07-operator-console.md` §16.9). The contract: a dry-run returns the *same* accept/reject verdict,
window, and delivery path that issuing would, while mutating **no** session state — so the UI can
probe every candidate command on each tick without polluting the queue or breaking replay.
"""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.orders import Order
from spacesim.session.manager import SessionManager


def _mgr():
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    return mgr


def _downlink(actor="ISR-EO-1", via="GS-TRN"):
    return Order(cell="blue", actor=actor, action="downlink", params={"via": via})


def test_dry_run_is_side_effect_free():
    mgr = _mgr()
    before = mgr.world.model_dump_json()

    # Probe the same order many times, the way the UI would on every tick.
    for _ in range(5):
        ack = mgr.validate_order("blue", _downlink())
        assert ack.ok and ack.status == "queued"

    # Nothing registered, nothing scheduled, counter untouched, no id minted.
    assert mgr.list_orders("blue") == []
    assert mgr.osys.orders == {}
    assert mgr.osys._order_counter == 0
    assert ack.id == ""
    assert mgr.world.model_dump_json() == before
    # Replay is byte-identical: the dry-runs touched no event log / RNG.
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_dry_run_matches_issue_for_accepted_order():
    preview = _mgr().validate_order("blue", _downlink())

    mgr = _mgr()
    issued = mgr.issue_order("blue", _downlink())

    assert preview.ok == issued.ok == True
    assert preview.status == issued.status == "queued"
    assert preview.delivery_path == issued.delivery_path == "ground_uplink"
    assert preview.earliest_window == issued.earliest_window
    # Issuing schedules; the prior dry-run did not.
    assert mgr.osys._order_counter == 1


def test_dry_run_surfaces_rejection_reasons():
    mgr = _mgr()
    # Unauthorized kinetic engage -> the validator's own reason string, verbatim (§12.2).
    ack = mgr.validate_order("blue", Order(cell="blue", actor="ISR-EO-1", action="engage", target="RED-TGT"))
    assert not ack.ok and ack.status == "rejected" and ack.reason == "roe_kinetic_not_authorized"

    # Maneuver with no ground station / stored slot -> no_command_station.
    ack = mgr.validate_order("blue", Order(cell="blue", actor="ISR-EO-1", action="maneuver", params={"dv": [1, 0, 0]}))
    assert not ack.ok and ack.reason == "no_command_station"

    # Still nothing leaked into the queue after several rejections.
    assert mgr.osys.orders == {}


def test_dry_run_enforces_ownership_fog():
    mgr = _mgr()
    # Red probing a Blue-owned asset is rejected as not_owner (fog/authority at the boundary).
    ack = mgr.validate_order("red", Order(cell="red", actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"}))
    assert not ack.ok and ack.reason == "not_owner"


def test_window_search_handles_unknown_station_gracefully():
    """A command 'via' a station not in the force yields no_window, not a KeyError crash.

    Regression: the access provider used to dereference a missing id directly; the UI's auto-validate
    now probes arbitrary stations, so unknown endpoints must degrade to 'no access' for issue + dry-run.
    """
    mgr = _mgr()
    ack = mgr.validate_order("blue", _downlink(via="NO-SUCH-STATION"))
    assert not ack.ok and ack.reason == "no_window"
    # Same graceful path when actually issuing (not just dry-running).
    issued = mgr.issue_order("blue", _downlink(via="NO-SUCH-STATION"))
    assert issued.status == "rejected" and issued.reason == "no_window"
