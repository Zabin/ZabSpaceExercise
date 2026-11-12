"""Refactor packet A4 — the behaviour baseline.

Pins what the simulator does today, so a behaviour-preserving change (a module split, a lint fix,
a move) can prove it changed nothing. For each of the 19 built-in vignettes one fixed, scripted
exercise is run through the ``SessionAPI`` seam (``InProcessSession``): a fixed seed, orders of
every action type from both cells, Red-doctrine steps, an SSN request, an ROE change, an order
cancellation, one immediate and one future-dated White inject, and two simulated hours advanced
in eight steps. What comes out is hashed and compared with the committed
``baseline/behaviour_baseline.json``.

What is pinned per vignette:

* ``world``    — SHA-256 of the final ground-truth world (canonical JSON, sorted keys);
* ``eventlog`` — SHA-256 of the whole event log;
* ``pending``  — SHA-256 of what a save carries beyond the log: pending scheduled events, the
  order registry and the SSN requests;
* ``views``    — SHA-256 of the fog-filtered Blue and Red views and the objectives;
* ``acks``     — every acknowledgement the script received, in order, readable;
* ``final_time``, ``eventlog_entries`` — plain numbers, to make a mismatch easier to read.

Wall time never reaches the engine: ``SessionManager.start()`` arms the lazy real-time clock, and
pausing it folds the elapsed wall time into the simulation, so the harness freezes ``time.time``
for exactly the start-then-pause pair and asserts the clock is stopped at the start epoch. From
then on the clock is off and every advance is an explicit ``step``. ``test_wall_time_never_reaches
_the_simulation`` proves it by re-running a script with real sleeps between the steps.

Re-blessing (``docs/pipeline/refactor-plan.md`` §3, "The behaviour baseline"): the default run
only reads the file. To rewrite it, run

    SPACESIM_REBLESS_BASELINE=1 python3 -m pytest spacesim/tests/test_behaviour_baseline.py

(add ``-k "<vignette-id>"`` to rewrite only some rows), then run the module again without the
variable. Under the variable each vignette is run twice from scratch and must hash identically
before its row is written. A behaviour-preserving packet must leave the file
byte-identical; only a defect-fix package may re-bless, and only the vignettes its fix explains.

The suite's own test counts are deliberately not part of the baseline.
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

from spacesim.content.vignette import list_vignettes
from spacesim.engine.orders import Order
from spacesim.engine.simulation import replay
from spacesim.session.inprocess import InProcessSession

pytestmark = pytest.mark.verifies("NFR-1500", "FR-1120")

BASELINE_FILE = Path(__file__).resolve().parent / "baseline" / "behaviour_baseline.json"
REBLESS_ENV = "SPACESIM_REBLESS_BASELINE"
SEED = 20261112
STEP_S = 900                      # eight steps of 15 simulated minutes = two simulated hours
N_STEPS = 8
ORDER_ROUNDS = {0: 0, 2: 1, 5: 2}  # before step index -> order-round number
RED_DOCTRINE_BEFORE = (0, 4)      # Red-doctrine steps: at the start and at one simulated hour
FROZEN_WALL = 1_800_000_000.0     # the instant the wall clock is frozen at across start + pause
PINNED = ("world", "eventlog", "pending", "views", "acks", "final_time", "eventlog_entries")

VIGNETTE_IDS = sorted(v["id"] for v in list_vignettes() if v.get("origin") == "built-in")


# -- canonical hashing ---------------------------------------------------------------------------
def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _sha(obj) -> str:
    return hashlib.sha256(_canon(obj).encode("utf-8")).hexdigest()


def _dump(model):
    return model.model_dump(mode="json")


@dataclass(frozen=True)
class Digest:
    """Everything observable about one session at one instant, reduced to hashes."""
    world: str
    eventlog: str
    pending: str
    views: str
    final_time: int
    eventlog_entries: int


def _digest(api: InProcessSession, sid: str) -> Digest:
    save = api.save(sid)
    log = _dump(api._sessions[sid].sim.eventlog)
    return Digest(
        world=_sha(_dump(api.get_godview(sid))),
        eventlog=_sha(log),
        pending=_sha({k: save[k] for k in ("pending", "orders", "ssn_requests")}),
        views=_sha({"blue": _dump(api.get_view(sid, "blue")), "red": _dump(api.get_view(sid, "red")),
                    "objectives": api.objectives(sid)}),
        final_time=save["final_time"],
        eventlog_entries=len(log["entries"]),
    )


# -- the scripted exercise -----------------------------------------------------------------------
def _start_without_wall_time(api: InProcessSession, sid: str) -> None:
    """Start the session and stop its real-time clock with no wall time folded in.

    ``start()`` arms the wall-clock anchor and the pause folds ``time.time() - anchor`` into the
    simulation; with ``time.time`` frozen across exactly that pair the fold is zero. After this the
    clock is off, so no later call can advance the simulation from the wall clock.
    """
    start_epoch = api._sessions[sid].sim.clock.now
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(time, "time", lambda: FROZEN_WALL)
        ack = api.start(sid)
        assert ack.ok, ack.reason
        api.set_clock(sid, False)
    state = api.clock_state(sid)
    assert state["running"] is False, state
    assert api._sessions[sid].sim.clock.now == start_epoch, "wall time reached the simulation at start"


def _pick(items: list[str], n: int, default: str) -> str:
    return items[n % len(items)] if items else default


def _order_round(api: InProcessSession, sid: str, n: int, acks: list[str]) -> None:
    """One round of orders from each cell, every action type, chosen from sorted ids."""
    world = api.get_godview(sid)
    now = world.now
    for cell, foe in (("blue", "red"), ("red", "blue")):
        own = sorted(i for i, a in world.assets.items() if a.owner == cell)
        own_sats = [i for i in own if world.assets[i].orbit is not None]
        own_sites = [i for i in own if world.assets[i].location is not None]
        own_sensors = sorted(i for i, s in world.sensors.items() if s.owner == cell)
        foes = sorted(i for i, a in world.assets.items() if a.owner == foe)
        foe_sats = [i for i in foes if world.assets[i].orbit is not None]
        target = _pick(foe_sats or foes, n, "NO-TARGET")
        sat = _pick(own_sats or own, n, "NO-ASSET")
        site = _pick(own_sites, n, "NO-STATION")

        jammer = _pick([i for i in own if world.assets[i].kind == "jammer"] or own, n, "NO-ASSET")
        cyber_unit = _pick([i for i in own if world.assets[i].kind == "cyber_unit"] or own, n, "NO-ASSET")
        armed = _pick([i for i in own if world.assets[i].resources.ammo > 0] or own, n, "NO-ASSET")
        vulnerable = [(i, v.get("vector")) for i in foes for v in world.assets[i].cyber_vulnerabilities]
        cyber_target, vector = vulnerable[n % len(vulnerable)] if vulnerable else (target, "supply_chain")
        verb, verb_params = (("eps.set_charge_mode", {"mode": "fast"}), ("adcs.desaturate", {}),
                             ("cdh.clear_fault", {}))[n % 3]
        uplink = {"via": site} if n != 1 else {"stored_at": now + 600 * 1_000_000}
        script = [
            ("observe", _pick(own_sensors, n, "NO-SENSOR"), target,
             {"intent": ("track", "characterize", "track")[n % 3]}),
            ("observe", "auto", target, {"intent": "track"}),
            ("jam", jammer, target, {"modulation": "barrage", "power_w": 200.0}),
            ("cyber", cyber_unit, cyber_target, {"vector": vector, "payload": "seize_c2"}),
            ("engage", armed, target, {"salvo_n": 1}),
            ("downlink", sat, None, {"via": site}),
            ("command", sat, None, {"verb": verb, **verb_params, **uplink}),
            ("maneuver", sat, None, {"dv": [0.5, 0.0, 0.0], "purpose_tag": f"baseline-{n}", **uplink}),
        ]
        issued = []
        for action, actor, tgt, params in script:
            ack = api.issue_order(sid, cell, Order(cell=cell, actor=actor, action=action,
                                                   target=tgt, params=params))
            issued.append(ack)
            acks.append(f"r{n} {cell} {action} {actor}->{tgt}: ok={ack.ok} status={ack.status} "
                        f"reason={ack.reason!r} path={ack.delivery_path} window={ack.earliest_window}")
        if n == 1:   # cancel the first order this cell got queued this round
            queued = [a.id for a in issued if a.ok and a.id]
            if queued:
                ack = api.cancel_order(sid, cell, queued[0])
                acks.append(f"r{n} {cell} cancel {queued[0]}: ok={ack.ok} reason={ack.reason!r}")
        if n == 0:
            regime = "GEO" if "geo" in api._sessions[sid].vignette.id else "LEO"
            ssn = api.submit_ssn_request(sid, cell, "track", target, regime)
            acks.append(f"r{n} {cell} ssn track {target} {regime}: {_canon(_ssn_ack(ssn))}")


def _ssn_ack(ack) -> dict:
    return {k: v for k, v in sorted(vars(ack).items())}


def _white_actions(api: InProcessSession, sid: str, acks: list[str]) -> None:
    """One immediate and one future-dated inject, and one live ROE change, all White Cell."""
    world = api.get_godview(sid)
    now = world.now
    sites = sorted(i for i, a in world.assets.items() if a.kind == "ground_station")
    immediate = [{"type": "message", "to": ["blue", "red"], "text": "baseline: immediate inject"},
                 {"type": "space_weather", "severity": "minor"}]
    later = [{"type": "message", "to": ["blue", "red"], "text": "baseline: future-dated inject"},
             {"type": "political_consequence", "cause": "baseline", "severity": "low"}]
    if sites:
        later.append({"type": "gs_outage", "target": sites[0], "cause": "baseline"})
    ack = api.fire_inject(sid, immediate)
    acks.append(f"white inject now: ok={ack.ok} reason={ack.reason!r}")
    ack = api.fire_inject(sid, later, at_sim_t=now + 3600 * 1_000_000)
    acks.append(f"white inject +3600s: ok={ack.ok} reason={ack.reason!r}")
    ack = api.issue_roe_change(sid, "white", "blue", "kinetic_authorized", True)
    acks.append(f"white roe blue kinetic_authorized=True: ok={ack.ok} reason={ack.reason!r}")


def run_script(vignette_id: str, sleep_s: float = 0.0) -> tuple[InProcessSession, str, list[str]]:
    """Run the fixed exercise; ``sleep_s`` puts a real wall-clock pause between the steps."""
    api = InProcessSession()
    sid = api.load_vignette(vignette_id, seed=SEED)
    _start_without_wall_time(api, sid)
    acks: list[str] = []
    for i in range(N_STEPS):
        if i == 0:
            _white_actions(api, sid, acks)
        if i in ORDER_ROUNDS:
            _order_round(api, sid, ORDER_ROUNDS[i], acks)
        if i in RED_DOCTRINE_BEFORE:
            for ack in api.red_doctrine_step(sid):
                acks.append(f"red doctrine before step {i}: ok={ack.ok} status={ack.status} "
                            f"reason={ack.reason!r} path={ack.delivery_path} window={ack.earliest_window}")
        if sleep_s:
            time.sleep(sleep_s)
        ack = api.step(sid, STEP_S)
        assert ack.ok, ack.reason
    return api, sid, acks


@dataclass(frozen=True)
class Exercise:
    live: Digest             # after the script
    acks: tuple[str, ...]
    replayed_world: str      # the event log replayed from the initial state to the live instant
    reloaded: Digest         # save -> JSON text -> load, before any further step
    live_continued: Digest   # the live session one step further
    reloaded_continued: Digest   # the reloaded session one step further

    def pinned(self) -> dict:
        d = self.live
        return {"world": d.world, "eventlog": d.eventlog, "pending": d.pending, "views": d.views,
                "final_time": d.final_time, "eventlog_entries": d.eventlog_entries,
                "acks": list(self.acks)}


@functools.cache
def exercise(vignette_id: str) -> Exercise:
    """The scripted run and its save/reload/replay companions, computed once per vignette."""
    api, sid, acks = run_script(vignette_id)
    live = _digest(api, sid)
    sim = api._sessions[sid].sim
    replayed = replay(sim._initial_state, sim._seed, sim.eventlog, handlers=sim.handlers(),
                      final_time=sim.clock.now)
    reloaded_sid = api.load_save(json.loads(json.dumps(api.save(sid))))
    reloaded = _digest(api, reloaded_sid)
    for s in (sid, reloaded_sid):
        ack = api.step(s, STEP_S)
        assert ack.ok, ack.reason
    return Exercise(live=live, acks=tuple(acks), replayed_world=_sha(_dump(replayed)),
                    reloaded=reloaded, live_continued=_digest(api, sid),
                    reloaded_continued=_digest(api, reloaded_sid))


def _committed() -> dict:
    return json.loads(BASELINE_FILE.read_text(encoding="utf-8"))


def _rebless(vignette_id: str) -> None:
    """Rewrite one vignette's row. Runs the script a second time from scratch first: two identical
    runs that hash differently are a determinism defect, never something to re-bless."""
    ex = exercise(vignette_id)
    api, sid, acks = run_script(vignette_id)
    assert _digest(api, sid) == ex.live and tuple(acks) == ex.acks, (
        f"'{vignette_id}' is not stable across two identical runs: a determinism defect")
    doc = _committed() if BASELINE_FILE.exists() else {"vignettes": {}}
    doc["about"] = ("Behaviour baseline (refactor packet A4). Generated by "
                    "spacesim/tests/test_behaviour_baseline.py; never hand-edited. Re-bless rule: "
                    "docs/pipeline/refactor-plan.md section 3.")
    doc["seed"] = SEED
    doc["script"] = {"step_s": STEP_S, "steps": N_STEPS}
    doc["vignettes"][vignette_id] = ex.pinned()
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text(json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=True) + "\n",
                             encoding="utf-8")


# -- the tests -----------------------------------------------------------------------------------
@pytest.mark.parametrize("vignette_id", VIGNETTE_IDS)
def test_scripted_run_matches_the_baseline(vignette_id):
    """The pinned comparison. It only reads the file, unless ``SPACESIM_REBLESS_BASELINE=1``, when
    it rewrites this vignette's row instead of comparing (``-k`` re-blesses chosen vignettes)."""
    if os.environ.get(REBLESS_ENV) == "1":
        _rebless(vignette_id)
        return
    got = exercise(vignette_id).pinned()
    want = _committed()["vignettes"][vignette_id]
    moved = [k for k in PINNED if got[k] != want[k]]
    if "acks" in moved:
        pairs = list(zip(want["acks"], got["acks"]))
        first = next((i for i, (a, b) in enumerate(pairs) if a != b), len(pairs))
        detail = (f"first differing acknowledgement #{first}:\n  baseline: "
                  f"{want['acks'][first] if first < len(want['acks']) else '<none>'}\n  now:      "
                  f"{got['acks'][first] if first < len(got['acks']) else '<none>'}")
    else:
        detail = "\n".join(f"  {k}: baseline {want[k]} -> now {got[k]}" for k in moved)
    assert not moved, (
        f"behaviour moved for vignette '{vignette_id}' in: {', '.join(moved)}\n{detail}\n"
        "A behaviour-preserving change must not move the baseline (refactor-plan.md §3)."
    )


@pytest.mark.parametrize("vignette_id", VIGNETTE_IDS)
def test_replaying_the_event_log_reproduces_the_live_world(vignette_id):
    ex = exercise(vignette_id)
    assert ex.replayed_world == ex.live.world


@pytest.mark.verifies("FR-7210", "FR-7230")
@pytest.mark.parametrize("vignette_id", VIGNETTE_IDS)
def test_save_reload_and_continue_equal_the_live_session(vignette_id):
    ex = exercise(vignette_id)
    assert ex.reloaded == ex.live, "the reloaded session differs from the live one at the save instant"
    assert ex.live_continued.final_time == ex.live.final_time + STEP_S * 1_000_000
    assert ex.reloaded_continued == ex.live_continued, "the two sessions diverged after the same step"


@pytest.mark.parametrize("vignette_id", VIGNETTE_IDS)
def test_wall_time_never_reaches_the_simulation(vignette_id):
    """The same script with real sleeps between the steps yields the same hashes: at the default
    1x rate each 20 ms sleep would otherwise add 20 000 simulated microseconds."""
    api, sid, acks = run_script(vignette_id, sleep_s=0.02)
    ex = exercise(vignette_id)
    assert _digest(api, sid) == ex.live
    assert tuple(acks) == ex.acks


def test_baseline_covers_exactly_the_built_in_library():
    """Last in the module, so a re-bless run checks the file it has just rewritten."""
    assert len(VIGNETTE_IDS) == 19, VIGNETTE_IDS
    doc = _committed()
    assert doc["seed"] == SEED
    assert doc["script"] == {"step_s": STEP_S, "steps": N_STEPS}
    assert sorted(doc["vignettes"]) == VIGNETTE_IDS
    for vid, row in doc["vignettes"].items():
        assert sorted(row) == sorted(PINNED), vid
