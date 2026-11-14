"""Refactor packet A4 — the behaviour baseline.

Pins what the simulator does today, so a behaviour-preserving change (a module split, a lint fix,
a move) can prove it changed nothing. For each of the 19 built-in vignettes one fixed, scripted
exercise is run through the ``SessionAPI`` seam (``InProcessSession``): a fixed seed, orders of
every action type from both cells, Red-doctrine steps, an SSN request, an ROE change, an order
cancellation, one immediate and one future-dated White inject, and two simulated hours advanced
in eight steps. What comes out is hashed and compared with the committed
``baseline/behaviour_baseline.json``.

What is pinned per vignette:

* ``world``    — the final ground-truth world;
* ``eventlog`` — the whole event log;
* ``pending``  — what a save carries beyond the log: pending scheduled events, the order registry
  and the SSN requests;
* ``views``    — the fog-filtered Blue and Red views and the objectives;
* ``floats``   — the floating-point values of those four documents (see the float rule);
* ``acks``     — every acknowledgement the script received, in order, readable;
* ``final_time``, ``eventlog_entries`` — plain numbers, to make a mismatch easier to read.

The float rule. The engine's floats are reproducible on one machine but not bit-for-bit across
CPUs: NumPy's linear algebra runs on OpenBLAS, which picks a kernel per CPU model (run with
``OPENBLAS_CORETYPE=Haswell`` to see it), and the last bits differ by up to about 4e-11 relative
in ill-conditioned orbital elements. So each document is pinned in two parts. Its *exact part* is
a SHA-256 of the canonical JSON (sorted keys) with every float replaced by a marker: every
integer, string, boolean, key, list length and the position and type of every float must match
exactly. Its floats are stored in traversal order and compared one by one within
``FLOAT_REL_TOL`` (1e-8 relative, about 250 times the largest cross-kernel difference seen, and
far below any change in behaviour). Nothing is rounded before hashing, so no value can sit on a
rounding boundary and flip between machines. Replay, save/reload and the sleep run are compared
on one machine and stay bit-exact.

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
SECTIONS = ("world", "eventlog", "pending", "views")
EXACT = (*SECTIONS, "acks", "final_time", "eventlog_entries")   # compared with ==
PINNED = (*EXACT, "floats")                                     # floats: within the tolerance
FLOAT_REL_TOL = 1e-8     # see "The float rule" above
FLOAT_ABS_TOL = 1e-12    # for values at or next to zero
FLOAT_MARK = "\x00float"

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


def _documents(api: InProcessSession, sid: str) -> dict:
    """The four documents that describe a session, as plain JSON-ready data."""
    save = api.save(sid)
    return {
        "world": _dump(api.get_godview(sid)),
        "eventlog": _dump(api._sessions[sid].sim.eventlog),
        "pending": {k: save[k] for k in ("pending", "orders", "ssn_requests")},
        "views": {"blue": _dump(api.get_view(sid, "blue")), "red": _dump(api.get_view(sid, "red")),
                  "objectives": api.objectives(sid)},
    }


def _digest(api: InProcessSession, sid: str) -> Digest:
    """Bit-exact hashes, floats included: for comparisons made on one machine."""
    docs = _documents(api, sid)
    return Digest(world=_sha(docs["world"]), eventlog=_sha(docs["eventlog"]),
                  pending=_sha(docs["pending"]), views=_sha(docs["views"]),
                  final_time=docs["world"]["now"], eventlog_entries=len(docs["eventlog"]["entries"]))


# -- the portable form: exact part + floats ------------------------------------------------------
def _split(obj, path: str, floats: list, paths: list):
    """Return ``obj`` with each float replaced by a marker; collect the floats and their paths in
    canonical (sorted-key) traversal order. ``bool`` and ``int`` are not floats and stay exact."""
    if isinstance(obj, float):
        floats.append(obj)
        paths.append(path)
        return FLOAT_MARK
    if isinstance(obj, dict):
        return {k: _split(obj[k], f"{path}/{k}", floats, paths) for k in sorted(obj)}
    if isinstance(obj, list):
        return [_split(v, f"{path}/{i}", floats, paths) for i, v in enumerate(obj)]
    return obj


def _portable(docs: dict) -> tuple[dict, dict]:
    """``({section: exact-part hash, "floats": {section: [...]}}, {section: [float paths]})``."""
    out: dict = {"floats": {}}
    paths: dict = {}
    for name in SECTIONS:
        floats: list = []
        paths[name] = []
        out[name] = _sha(_split(docs[name], "", floats, paths[name]))
        out["floats"][name] = floats
    return out, paths


def _floats_close(want: float, got: float) -> bool:
    return abs(want - got) <= max(FLOAT_ABS_TOL, FLOAT_REL_TOL * max(abs(want), abs(got)))


def _float_mismatches(want: dict, got: dict, paths: dict) -> list[str]:
    """Readable lines for every float outside the tolerance (or a float count that changed)."""
    out = []
    for name in SECTIONS:
        w, g = want[name], got[name]
        if len(w) != len(g):
            out.append(f"{name}: {len(w)} floats in the baseline, {len(g)} now")
            continue
        out.extend(f"{name}{paths[name][i]}: baseline {a!r} -> now {b!r}"
                   for i, (a, b) in enumerate(zip(w, g)) if not _floats_close(a, b))
    return out


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
    portable: dict           # the live session in the portable form (exact parts + floats)
    float_paths: dict        # where each float of ``portable`` lives, for messages

    def pinned(self) -> dict:
        return {**self.portable, "final_time": self.live.final_time,
                "eventlog_entries": self.live.eventlog_entries, "acks": list(self.acks)}


@functools.cache
def exercise(vignette_id: str) -> Exercise:
    """The scripted run and its save/reload/replay companions, computed once per vignette."""
    api, sid, acks = run_script(vignette_id)
    live = _digest(api, sid)
    portable, float_paths = _portable(_documents(api, sid))
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
                    reloaded_continued=_digest(api, reloaded_sid),
                    portable=portable, float_paths=float_paths)


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
    ex = exercise(vignette_id)
    got = ex.pinned()
    want = _committed()["vignettes"][vignette_id]
    moved = [k for k in EXACT if got[k] != want[k]]
    floats = _float_mismatches(want["floats"], got["floats"], ex.float_paths)
    lines = [f"  {k}: baseline {want[k]} -> now {got[k]}" for k in moved if k != "acks"]
    if "acks" in moved:
        pairs = list(zip(want["acks"], got["acks"]))
        first = next((i for i, (a, b) in enumerate(pairs) if a != b), len(pairs))
        lines.append(f"  first differing acknowledgement #{first}:\n    baseline: "
                     f"{want['acks'][first] if first < len(want['acks']) else '<none>'}\n    now:      "
                     f"{got['acks'][first] if first < len(got['acks']) else '<none>'}")
    lines += [f"  float {line}" for line in floats[:12]]
    if len(floats) > 12:
        lines.append(f"  ... and {len(floats) - 12} more floats")
    assert not moved and not floats, (
        f"behaviour moved for vignette '{vignette_id}' in: "
        f"{', '.join(moved + (['floats'] if floats else []))}\n" + "\n".join(lines) + "\n"
        "A behaviour-preserving change must not move the baseline (refactor-plan.md §3)."
    )


def test_portable_comparison_is_still_sensitive():
    """The float rule hides the last bits and nothing else: a float moved by one part in a million,
    a float that became an integer, an integer off by one and a dropped float are all caught."""
    doc = {"now": 1899784800000000, "orbit": {"a_m": 6977714.458269298, "e": 8.196301708160927e-05},
           "hits": [0.0, 1.0, 3], "ok": True}

    def portable(d):
        floats, paths = [], []
        return _sha(_split(d, "", floats, paths)), floats, paths

    sha, floats, paths = portable(doc)
    assert paths == ["/hits/0", "/hits/1", "/orbit/a_m", "/orbit/e"]
    one = {s: [] for s in SECTIONS}

    def mismatches(new_floats):
        return _float_mismatches({**one, "world": floats}, {**one, "world": new_floats},
                                 {**one, "world": paths})

    assert mismatches(list(floats)) == []
    last_bits = [floats[0], floats[1], floats[2] * (1 + 4e-11), floats[3] * (1 - 4e-11)]
    assert mismatches(last_bits) == []                      # the cross-CPU difference: accepted
    for i in range(len(floats)):                            # one part in a million, or zero moved
        moved = list(floats)
        moved[i] = moved[i] * (1 + 1e-6) if moved[i] else 1e-9
        assert len(mismatches(moved)) == 1, paths[i]
    assert mismatches(floats[:-1]) != []                    # a float disappeared
    for change in ({"now": doc["now"] + 1}, {"hits": [0.0, 1, 3]}, {"hits": [0.0, 1.0, 4]},
                   {"ok": False}, {"orbit": {"a_m": doc["orbit"]["a_m"]}}):
        assert portable({**doc, **change})[0] != sha, change   # the exact part moved


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
        assert sorted(row["floats"]) == sorted(SECTIONS), vid
