"""IP-1062 (FR-4420) — deterministic condition-triggered inject firing: evaluated only on
scheduled engine ticks, fires exactly once, reproduces under replay, and adds zero eventlog
bloat for a vignette that declares none."""
from __future__ import annotations

import pytest

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
    # IP-1064 (BL-0131, FR-4420 Outputs) — the record carries the measured custody confidence that
    # decided the firing, not just a boolean.
    (fired,) = condition_entries[0].payload["fired"]
    assert fired["inject_id"] == "cond-inject"
    assert isinstance(fired["value"], float) and not isinstance(fired["value"], bool)
    assert 0.5 <= fired["value"] <= 1.0


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


# --------------------------------------------------------------------------- #
# IP-1064 — evaluated value for range metrics, anchored tick grids, one scan per tick
# --------------------------------------------------------------------------- #

def test_condition_record_carries_measured_range_for_a_proximity_metric():
    """BL-0131 — a range metric records the measured range in km (at or below the threshold)."""
    vig = _custody_condition_vignette({"kind": "proximity", "a": "SAT-BLUE", "b": "SAT-RED",
                                       "max_km": 1e9})
    raw = vig.model_dump()
    orbit = {"source": "kepler", "a_m": 6978137.0, "e": 0.0, "i_deg": 97.8, "raan_deg": 342.0,
             "argp_deg": 0.0, "ta_deg": 0.0}
    raw["blue_forces"][0]["orbit"] = orbit
    raw["red_forces"][0]["orbit"] = {**orbit, "ta_deg": 1.0}
    mgr = SessionManager(Vignette.model_validate(raw), seed=0)
    mgr.start()
    mgr.advance_to(mgr.sim.clock.now + int(BUS_TICK_PERIOD_S * 1_000_000))
    (entry,) = [e for e in mgr.sim.eventlog.entries if e.kind == "condition_check"]
    (fired,) = entry.payload["fired"]
    assert isinstance(fired["value"], float) and 0.0 <= fired["value"] <= 1e9


def _tick_times(mgr, after: int) -> list[tuple[str, int]]:
    return [(e.kind, e.sim_time) for e in mgr.sim.eventlog.entries
            if e.kind in ("bus_tick", "condition_check") and e.sim_time > after]


def test_tick_grids_stay_on_the_start_anchored_grid_after_an_off_grid_rewind():
    """BL-0132 — rewinding to a time between ticks, then re-advancing unchanged, reproduces the
    original tick timeline (both bus_tick and condition_check)."""
    metric = {"kind": "custody", "side": "blue", "object": "GHOST", "min_conf": 0.5}  # never fires
    step = int(BUS_TICK_PERIOD_S * 1_000_000)
    plain = SessionManager(_custody_condition_vignette(metric), seed=0)
    plain.start()
    t0 = plain.sim.clock.now
    plain.advance_to(t0 + 6 * step)

    rewound = SessionManager(_custody_condition_vignette(metric), seed=0)
    rewound.start()
    rewound.advance_to(t0 + 3 * step)
    off_grid = t0 + 2 * step + step // 3
    rewound.rewind_to(off_grid)
    rewound.advance_to(t0 + 6 * step)

    assert _tick_times(rewound, off_grid) == _tick_times(plain, off_grid)
    assert _tick_times(plain, off_grid)  # the comparison is not vacuous


def test_two_condition_injects_each_fire_once_at_the_same_tick():
    """BL-0133 — the one-scan fired lookup keeps fire-once semantics for every inject."""
    vig = _custody_condition_vignette({"kind": "custody", "side": "blue", "object": "SAT-RED", "min_conf": 0.5})
    raw = vig.model_dump()
    second = dict(raw["injects"][1])
    second["id"] = "cond-inject-2"
    second["effects"] = [{"type": "message", "to": ["blue"], "text": "second-fired"}]
    raw["injects"].append(second)
    mgr = SessionManager(Vignette.model_validate(raw), seed=0)
    mgr.start()
    mgr.advance_to(mgr.sim.clock.now + int(4 * BUS_TICK_PERIOD_S * 1_000_000))
    assert _fired_count(mgr) == 1
    assert sum(1 for m in mgr.world.messages if m["text"] == "second-fired") == 1
    fired_ticks = [e.sim_time for e in mgr.sim.eventlog.entries
                   if e.kind == "condition_check" and e.payload.get("fired")]
    assert len(fired_ticks) == 1


# --------------------------------------------------------------------------- #
# IP-1064 re-run (VR-1064 Finding 1, BL-0278) — the recorded value is the one the decision saw,
# even when the inject's own effects change the measured quantity.
# --------------------------------------------------------------------------- #

def _fired_value(mgr) -> float:
    (entry,) = [e for e in mgr.sim.eventlog.entries
                if e.kind == "condition_check" and e.payload.get("fired")]
    (fired,) = entry.payload["fired"]
    return fired["value"]


@pytest.mark.parametrize("loss", [{"degrade_to": 0.0}, {"mode": "drop"}])
def test_custody_record_value_is_measured_before_a_self_affecting_custody_loss(loss):
    """BL-0278 — a `custody >= 0.5` condition whose own effect is `forced_custody_loss` on the
    measured track records the confidence that decided the firing, not the post-effect 0.0."""
    metric = {"kind": "custody", "side": "blue", "object": "SAT-RED", "min_conf": 0.5}
    tick = int(BUS_TICK_PERIOD_S * 1_000_000)
    # Control: the same scenario with a message-only effect (the track is untouched), so its
    # recorded value is exactly the confidence the decision compared at the firing tick.
    control = SessionManager(_custody_condition_vignette(metric), seed=3)
    control.start()
    control.advance_to(control.sim.clock.now + tick)
    decided_at = _fired_value(control)
    assert decided_at >= 0.5

    raw = _custody_condition_vignette(metric).model_dump()
    raw["injects"][1]["effects"] = [{"type": "forced_custody_loss", "cell": "blue",
                                     "target": "SAT-RED", **loss}]
    mgr = SessionManager(Vignette.model_validate(raw), seed=3)
    mgr.start()
    mgr.advance_to(mgr.sim.clock.now + tick)
    assert _fired_value(mgr) == decided_at


def test_deny_custody_record_value_is_measured_before_a_self_affecting_reveal():
    """BL-0278, other direction — a `deny_custody` condition that fires with no track (the
    decision saw 0.0) and whose own effect is `reveal_asset` on that object records 0.0, not 1.0."""
    raw = _custody_condition_vignette({"kind": "deny_custody", "side": "blue", "object": "SAT-RED",
                                       "min_conf": 0.5, "by_s": 0}).model_dump()
    raw["injects"] = [raw["injects"][1]]  # drop the t=0 reveal: blue holds no track
    raw["injects"][0]["effects"] = [{"type": "reveal_asset", "to": "blue", "target": "SAT-RED"}]
    mgr = SessionManager(Vignette.model_validate(raw), seed=5)
    mgr.start()
    mgr.advance_to(mgr.sim.clock.now + int(BUS_TICK_PERIOD_S * 1_000_000))
    assert mgr.world.track_for("blue", "SAT-RED") is not None  # the effect did run
    assert _fired_value(mgr) == 0.0
