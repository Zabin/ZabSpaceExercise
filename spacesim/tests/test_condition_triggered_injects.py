"""IP-1062 (FR-4420) — deterministic condition-triggered inject firing: evaluated only on
scheduled engine ticks, fires exactly once, reproduces under replay, and adds zero eventlog
bloat for a vignette that declares none."""
from __future__ import annotations

from spacesim.content.vignette import Vignette
from spacesim.session.manager import BUS_TICK_PERIOD_S, SessionManager


def _custody_condition_vignette(metric: dict) -> Vignette:
    """One blue satellite, one red satellite, a t=0 scripted reveal (custody-granting, fully
    event-driven so the whole scenario replays byte-identically), and a condition-triggered
    inject watching the given metric."""
    raw = {
        "id": "test-condition-inject", "title": "Condition inject test",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [{"id": "SAT-BLUE", "kind": "satellite"}],
        "red_forces": [{"id": "SAT-RED", "kind": "satellite"}],
        "neutral_forces": [], "sensors": [],
        "injects": [
            {
                "id": "reveal-t0",
                "trigger": {"type": "time", "at_sim_s": 0},
                "effects": [{"type": "reveal_asset", "to": "blue", "target": "SAT-RED"}],
            },
            {
                "id": "cond-inject",
                "trigger": {"type": "condition", "metric": metric},
                "effects": [{"type": "message", "to": ["blue"], "text": "condition-fired"}],
            },
        ],
    }
    return Vignette.model_validate(raw)


def _fired_count(mgr) -> int:
    return sum(1 for m in mgr.world.messages if m["text"] == "condition-fired")


def test_condition_inject_fires_at_first_true_tick_and_records_fired_payload():
    vig = _custody_condition_vignette({"kind": "custody", "side": "blue", "object": "SAT-RED", "min_conf": 0.5})
    mgr = SessionManager(vig, seed=0)
    mgr.start()
    start = mgr.sim.clock.now
    mgr.advance_to(start + int(BUS_TICK_PERIOD_S * 1_000_000))
    assert _fired_count(mgr) == 1
    condition_entries = [e for e in mgr.sim.eventlog.entries if e.kind == "condition_check"]
    assert len(condition_entries) == 1
    assert condition_entries[0].payload["fired"] == [{"inject_id": "cond-inject", "value": True}]


def test_condition_inject_never_refires_once_fired():
    vig = _custody_condition_vignette({"kind": "custody", "side": "blue", "object": "SAT-RED", "min_conf": 0.5})
    mgr = SessionManager(vig, seed=0)
    mgr.start()
    start = mgr.sim.clock.now
    mgr.advance_to(start + int(4 * BUS_TICK_PERIOD_S * 1_000_000))
    assert _fired_count(mgr) == 1  # not once per tick despite the condition staying true


def test_condition_inject_targeting_deleted_object_never_fires():
    vig = _custody_condition_vignette({"kind": "custody", "side": "blue", "object": "GHOST", "min_conf": 0.5})
    mgr = SessionManager(vig, seed=0)
    mgr.start()
    start = mgr.sim.clock.now
    mgr.advance_to(start + int(6 * BUS_TICK_PERIOD_S * 1_000_000))
    assert _fired_count(mgr) == 0
    # No exception was raised getting here — Design Decision 2's "no-op forever" posture.


def test_vignette_with_no_condition_injects_schedules_zero_condition_check_events():
    api_vig = Vignette.model_validate({
        "id": "test-no-condition-injects", "title": "No condition injects",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [], "red_forces": [], "neutral_forces": [], "sensors": [],
        "injects": [{
            "id": "t0-inject",
            "trigger": {"type": "time", "at_sim_s": 0},
            "effects": [{"type": "message", "to": ["blue"], "text": "hi"}],
        }],
    })
    mgr = SessionManager(api_vig, seed=0)
    mgr.start()
    mgr.advance_to(mgr.sim.clock.now + int(6 * BUS_TICK_PERIOD_S * 1_000_000))
    assert not any(e.kind == "condition_check" for e in mgr.sim.eventlog.entries)


def test_condition_inject_fires_at_identical_tick_under_replay():
    """FS-106 v2.1's own Acceptance Criterion — deterministic replay reproduces the same firing
    tick exactly, since firing is a pure function of replayed WorldState."""
    vig = _custody_condition_vignette({"kind": "custody", "side": "blue", "object": "SAT-RED", "min_conf": 0.5})
    mgr = SessionManager(vig, seed=0)
    mgr.start()
    start = mgr.sim.clock.now
    mgr.advance_to(start + int(3 * BUS_TICK_PERIOD_S * 1_000_000))
    live_fired_entries = [
        (e.seq, e.sim_time) for e in mgr.sim.eventlog.entries
        if e.kind == "condition_check" and e.payload.get("fired")
    ]
    assert len(live_fired_entries) == 1

    replayed = mgr.sim.replay()
    replayed_fired_count = sum(1 for m in replayed.messages if m["text"] == "condition-fired")
    assert replayed_fired_count == 1
    # And the replayed world's message carries the same sim time the live run recorded it at.
    fired_seq, fired_time = live_fired_entries[0]
    assert any(m["text"] == "condition-fired" and m["t"] == fired_time for m in replayed.messages)
