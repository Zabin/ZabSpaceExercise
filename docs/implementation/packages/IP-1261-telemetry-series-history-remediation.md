# IP-1261 — Telemetry Series History Remediation (Single-Pass Time-Span Replay)

> **Package ID:** IP-1261
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-11 ([VR-1261](../verification/VR-1261-telemetry-series-history-remediation.md), fresh session; COMPLETE before that).
> **Earlier status record (superseded by the line above; retained as history, unedited):** 🔵 COMPLETE *(implemented 2026-10-11 by `08-code-implementation`; authorized by the
> project owner 2026-10-11, MSTR-006 §3. `engine/simulation.py::replay_stepwise()` (additive;
> `replay()` untouched) + `session/aar.py::worlds_at_times()` (single forward pass, live-tail
> shortcut); `get_series`, `telemetry_export`, `truth_ephemeris`, `cell_observed_ephemeris` all
> route through it. 10 new tests (6 in `test_telemetry.py`, 2 in `test_aar.py`, 1 each in
> `test_ephemeris.py`/`test_web.py`); Tests 1-4 + 10 and the cost guard observed failing first.
> Full suite 823 passed/3 skipped (826 collected, JUnit-tallied; baseline 813/3), both permanent
> gates green (14 passed). Measured cost on `multi-domain-taiwan` at +6 h (73 entries): ~4.3-4.7
> ms per `get_series(n=120)` call, ~90-100 ms per 21-call drill rebuild. Awaiting a fresh-session
> `09-package-verification` to advance to `VERIFIED`.)*
> **Dependencies:** [FS-126](../../features/FS-126-telemetry-csv-export.md) v1.0 (`FR-2320`),
> [FS-121](../../features/FS-121-ephemeris-export.md) v2.0 (`FR-7410`/`FR-7420` — behaviour
> preserved, not changed), [IP-1260](IP-1260-telemetry-csv-export.md) (`VERIFIED` 2026-10-10,
> [`VR-1260`](../verification/VR-1260-telemetry-csv-export.md)),
> [IP-1210](IP-1210-ephemeris-export.md) (`VERIFIED`, [`VR-1210`](../verification/VR-1210-ephemeris-export.md))
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0170` (the defect),
> `BL-0171` (adjacent pass-gating question — explicitly **not** in this package)
> **Produces:** a live telemetry series route (`get_series`) that shows each historical sample
> point as the world actually was at that instant — agreeing with the telemetry CSV export at
> every shared instant — through one shared single-forward-pass time-span replay helper, onto
> which the telemetry CSV export and both ephemeris exports are migrated with unchanged output
> **Feature Reference:** [FS-126 — Per-Asset Telemetry CSV Export Over a Time Span](../../features/FS-126-telemetry-csv-export.md)
> (`FR-2320` Postcondition: cross-route parity); [FS-121 — Ephemeris Export](../../features/FS-121-ephemeris-export.md)
> (`FR-7410`/`FR-7420`, migration only)
> **Supersedes:** none — new remediation package
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/aar.py`](../../../spacesim/session/aar.py),
> [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py),
> [`spacesim/engine/telemetry.py`](../../../spacesim/engine/telemetry.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package. Source: `BL-0170` (`00-intake`, 2026-10-10, independently reproduced; triaged
`SCHEDULED` for this `07` pass by `00-pipeline-manager` run #98). Numbered `IP-1261` as the next
slice in the FS-126 series (mirroring `IP-1061` under `IP-1060`): `IP-1260` is `VERIFIED` and is not
reopened. Requirements anchor: the project owner confirmed (2026-10-11) that the windowed console
telemetry graphs are a desired, kept feature, so `FR-2320`'s cross-route parity Postcondition plus
`FR-2310` (timestamped telemetry) are accepted as sufficient anchor — no `04` pre-step. Every file,
function, and line cited below was re-checked against the tree at `55d27a4`.*

## Package ID

IP-1261

## Title

Telemetry Series History Remediation (Single-Pass Time-Span Replay)

## Objective

1. **Fix the defect.** `SessionManager.get_series` must evaluate each sampled instant `t` against
   the world *as it was at `t`* (the same per-instant state `aar.state_at_time(mgr, t)` produces),
   not against the live world. Today it passes `self.sim.world` to `engine/telemetry.py::series()`
   for the whole window, so every state-dependent channel (`health` → LOS, `_baseline()`'s SoC /
   storage / propellant / bus voltage, `_mitigation()`, the `safed` gate in `_attack_term`) is
   back-dated across the window — and a cleared safe-mode episode vanishes from history. The
   `nominal=1` ghost is affected the same way and is fixed by the same change.
2. **Do it without a lock-hold regression.** Use one shared helper that replays **once** per call:
   a single forward pass over the event log, sampling each requested instant as the pass reaches
   it (`BL-0170` Option (2)), plus a live-tail shortcut that needs no replay at all when every
   requested instant is at or after the last event-log entry (Option (3)). Per-call cost is
   O(event-log length), independent of `n` and of how many distinct event-log positions the window
   spans.
3. **Single-source the mechanism.** Migrate `telemetry_export` (`IP-1260`) and both ephemeris
   exports (`IP-1210`: `truth_ephemeris`, `cell_observed_ephemeris`) onto the same helper, with
   output identical to today's (Option (4)). This removes three hand-rolled per-instant replay
   loops and turns ephemeris export from one full replay *per sample* into one pass per call.

**Out of scope:** `FR-2310` pass-gating of historical points (`BL-0171`, a separate `04`
question — this package reproduces today's "every sampled instant shown" semantics, only
correctly); production snapshotting (`BL-0170` Option (5), deferred); any replayed-world cache
(Option (6), rejected); `PlaybackSession` (single-instant reads, not time-span reads — unchanged);
any UI change (`graph.js`/`app.js` keep calling the same route with the same parameters).

## Feature Reference

[FS-126](../../features/FS-126-telemetry-csv-export.md) (`FR-2320`) — its Postcondition requires the
exported values to be "identical to what the same cell's own live telemetry endpoint would show at
each sampled point"; today the windowed live endpoint and the export disagree at every historical
point (`BL-0170` scenario D). [FS-121](../../features/FS-121-ephemeris-export.md) (`FR-7410`/`FR-7420`)
— migrated onto the shared helper with no behaviour change.

## Requirements Covered

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-2320 | Per-asset telemetry CSV export over a time span | Restores the Postcondition's cross-route parity: after this package, `get_series` and `telemetry_export` evaluate the same `telemetry.sample()` on the same per-instant world, so at any instant both sample they report the same value/status. `telemetry_export` itself moves onto the shared helper with identical rows. |
| FR-7410 | Truth ephemeris export | Migration only — rows identical to today's `state_at_time`-per-sample output; one replay pass per call instead of one per sample. |
| FR-7420 | Cell-observed ephemeris export | Migration only — same as `FR-7410`; fog-of-war rule (own `Track.state_estimate`, own-asset reference only) untouched. |

`FR-2310` (timestamped telemetry, RTM `UNASSIGNED` FS) is the anchor context for "the value at
each timestamp is the value at that time" but is **not** claimed as covered: its pass-gating
clause is the open `BL-0171` question, which this package deliberately does not answer.

## Architecture Components

- **C1 Simulation Engine — one additive function, nothing modified.** `engine/simulation.py`
  gains a stepwise sibling of `replay()` (see Interfaces) so the forward-pass loop, handler merge
  (`DEFAULT_HANDLERS` + overrides), RNG carry-over and snapshot shortcut stay single-sourced in
  the module that already owns them. `replay()` itself (`:153-198`) is **not** modified, so the
  determinism gate's subject is untouched. No wall-clock read, no RNG draw outside the replayed
  copy's own `SeededRng`, no new import (the import guard is unaffected).
- **C2 Session / Application Layer.**
  - `session/aar.py` gains the time-keyed helper beside `state_at_time()` (`:53-67`).
  - `session/manager.py` — `get_series()` (`:857-866`) and `telemetry_export()` (`:868-908`)
    route through it.
  - `session/ephemeris.py` — `truth_ephemeris()` (`:229-248`) and `cell_observed_ephemeris()`
    (`:251-283`) route through it.
- **C4 Web / UI: no change.** `ui_web/server.py:779-789` (series route) and the export routes are
  unchanged; the fog check (`_owns`, evaluated on the live world) is unchanged.
- **Invariants.** Determinism (1): every read uses a private replayed copy (or, on the live-tail
  shortcut, reads the live world without mutating it); nothing is logged or scheduled. Fog-of-war
  (3): unchanged — the ownership gate runs before any replay, exactly as today.

## Interfaces

- **New engine function (additive) — `engine/simulation.py`, name at `08`'s discretion (e.g.
  `replay_stepwise`).** Inputs: the same `(initial_state, seed, eventlog, handlers, snapshots)`
  as `replay()`, plus a **non-decreasing** sequence of event-log positions. Behaviour: build the
  start world/RNG exactly as `replay()` does (latest in-range snapshot ≤ the first position, else
  the initial state), then walk forward once, applying each entry exactly as `replay()`'s loop
  does (`world.now = entry.sim_time`, then the handler), and yield the *same* mutable world object
  each time the walk reaches a requested position. Contract: the world yielded for position `p`
  is field-for-field equal to `replay(..., up_to_seq=p)` at the moment it is yielded; the consumer
  must finish reading it before advancing the generator. A decreasing position raises
  `ValueError` (no caller produces one; fail loudly rather than silently re-replaying).
- **New session helper — `session/aar.py`, e.g. `worlds_at_times(mgr, times)`.** Input: a
  non-decreasing sequence of sim times (µs). Yields `(t, world)` per requested time, in input
  order, where `world`'s state equals `state_at_time(mgr, t)`'s in every field **except possibly
  `now`** (see below). Position for `t` is computed exactly as `state_at_time` does today: the
  count of entries with `sim_time <= t`.
  - **Replayed copies:** the helper pins `world.now = t` before yielding (as `state_at_time`
    does via `final_time`), so these are fully equal including `now`.
  - **Live-tail shortcut:** if *every* requested `t` maps to position `len(entries)` (all at or
    after the last entry, including any `t > clock.now` the route already answers with current
    state), the helper yields the live `mgr.sim.world` for each `t` without replaying and
    **without** pinning `now` (it must never mutate the live world). Once a forward pass is under
    way, reaching `len(entries)` simply keeps using the replayed copy.
  - Consumers therefore use the yielded `t`, never `world.now`. Every current consumer already
    does: `telemetry.sample()` never reads `world.now` (no `world.now` reference in
    `engine/telemetry.py`); the ephemeris functions pass `t` explicitly to `_PROP.rv` and
    `Track.current_confidence/uncertainty`.
- **`get_series` contract (unchanged signature, corrected values).** Same parameters, same
  default window (`[max(start_epoch, now−1 h), now]`), same `n` bounds (route enforces 2–2000),
  same sample instants (`int(t0 + i·step)`, exactly `telemetry.series()`'s spacing), same response
  shape `{asset, param, nominal, points: [{t, value, status}]}`. Only the values change, to the
  per-instant ones. Instants before `start_epoch` resolve to the initial state; instants after
  `now` resolve to the current state (today's behaviour).
- **`telemetry.series()` (engine) — unchanged.** `get_series` stops calling it with the live world
  and instead computes the same instants and calls `telemetry.sample()` per `(t, world)`; whether
  the instant-spacing arithmetic is shared by factoring a tiny pure helper out of `series()` or
  re-stated is `08`'s choice, provided instants are bit-identical (Test 7 checks this).
- **No public API, schema, persisted-format, or `SavedSession` change.**

## Files to Create

None. All tests go into existing test files.

## Files to Modify

| File | Change |
|---|---|
| `spacesim/engine/simulation.py` | Add the stepwise replay generator beside `replay()` (`:153`). `replay()` untouched. |
| `spacesim/session/aar.py` | Add the time-keyed helper beside `state_at_time()` (`:53`), with the live-tail shortcut. `state_at_time()` itself unchanged (other callers keep using it for single instants). |
| `spacesim/session/manager.py` | `get_series()` (`:857-866`): compute the window and instants as today, then evaluate `telemetry.sample(world, asset_id, param, t, seed, nominal=nominal)` per `(t, world)` from the helper. `telemetry_export()` (`:868-908`): replace the per-seq `replay(...)` memo loop (`worlds` dict, `:893-901`) with the helper; drop the now-unused local `replay` import if nothing else in the method uses it. Docstrings updated to cite IP-1261. |
| `spacesim/session/ephemeris.py` | `truth_ephemeris()` (`:229-248`) and `cell_observed_ephemeris()` (`:251-283`): iterate the helper over `sample_times(...)` instead of calling `aar.state_at_time(mgr, t)` per sample. Module docstring (`:4-5`) updated to name the shared helper. Row construction and skip rules unchanged. |
| `spacesim/tests/test_telemetry.py` | Add the `BL-0170` regression tests (Tests 1-4, 7, 8). |
| `spacesim/tests/test_aar.py` | Add the helper/engine contract tests (Tests 5, 6). |
| `spacesim/tests/test_ephemeris.py` | Add the ephemeris migration parity test (Test 9). |
| `spacesim/tests/test_web.py` | Add the route-level parity test (Test 10). |

## Implementation Tasks

Test-first: write each test in Tests to Add, observe the defect tests (1-4, 10) fail against the
current tree, then implement.

1. **Engine generator.** Add the stepwise replay function to `engine/simulation.py` per Interfaces.
   Reuse `replay()`'s exact start-state construction and per-entry application semantics (copying
   the handful of lines is acceptable; do **not** refactor `replay()` itself onto it in this
   package — keep the determinism gate's subject byte-for-byte unchanged).
2. **Session helper.** Add the time-keyed helper to `session/aar.py`: map each `t` to its position
   (entries with `sim_time <= t` — compute positions by a single merge walk over the sorted
   entries, or `bisect` on the entries' `sim_time`s, not a per-`t` linear `sum`), apply the
   live-tail shortcut, otherwise drive the engine generator once, pin `now = t` on the replayed
   copy, and yield `(t, world)`. Pass `handlers=mgr.sim.handlers()` and
   `snapshots=mgr.sim.snapshots` (matching `telemetry_export`'s current call).
3. **`get_series`.** Route through the helper (Objective 1). Keep the `_owns`/`PARAMS` gate first.
4. **`telemetry_export`.** Replace the memo loop with the helper. Rows must be identical.
5. **Ephemeris exports.** Replace `aar.state_at_time(mgr, t)` per sample with the helper. Rows
   must be identical.
6. **Docs** (see Documentation Updates).
7. Run the full suite and both permanent gates; flip this package to `COMPLETE`.

## Tests to Add

Scenarios reuse `BL-0170`'s reproduction shape on `training-basics`, seed 1, clock paused
(`set_clock(False)`), building on `test_telemetry.py`'s existing `_export_mgr()` pattern. "Replay
reference" below means `telemetry.sample(aar.state_at_time(mgr, t), asset, param, t, seed)` at the
same instant `t` — the oracle `IP-1260`'s own test already uses.

1. **`test_series_pre_onset_matches_replay` (scenario A, `test_telemetry.py`).** Bus `anomaly`
   inject on `ISR-EO-1` at +600 s, run to +1200 s; `get_series` over `[start, +1200 s]`, `n=7`, for
   `snr_db`, `attitude_error_deg` and `battery_soc`: every point equals the replay reference;
   pre-onset `snr_db` points are `green`. Fails today (3/7 `red`).
2. **`test_series_cyber_cpu_load_pre_onset_matches_replay` (scenario B).** Same with
   `cause: cyber`; `cpu_load_pct` equals the replay reference at all 7 points. Fails today.
3. **`test_series_cleared_episode_stays_in_history` (scenario C).** Anomaly at +300 s, cleared at
   +600 s (the same clear/recovery path `BL-0170` scenario C used), run to +900 s; `snr_db` at the
   in-episode instants equals the replay reference (`red`), not the post-recovery live value.
   Fails today (episode vanishes).
4. **`test_series_destroyed_asset_not_los_before_kill`.** Destroy an asset mid-window through the
   existing kinetic/`execute_effect` path (`08` reuses the cheapest existing fixture — grep
   `"destroyed"` in `test_effects.py`/`test_orders.py`); pre-kill points carry real values, post-kill
   points are `los`. Fails today (whole window `los`).
5. **`test_worlds_at_times_matches_state_at_time` (`test_aar.py`, property-style).** On a session
   with a non-trivial log (several injects/bus ticks), for a sorted list of instants that includes
   `start_epoch`, instants exactly equal to entry `sim_time`s, instants between entries, and
   instants ≥ the last entry: each yielded world's `model_dump()` equals
   `state_at_time(mgr, t).model_dump()` — excluding only `now` on the live-tail-shortcut path (and
   that path is asserted to have yielded the live world object without changing its `now`).
   Also: a decreasing input raises `ValueError`; the live world is unchanged (`model_dump()`
   before == after) by a full helper iteration.
6. **`test_stepwise_replay_matches_replay_at_every_position` (`test_aar.py`).** For every position
   `p` in `0..len(entries)`, the engine generator's yielded world (dumped at yield time) equals
   `replay(..., up_to_seq=p)`.
7. **`test_series_instants_and_shape_unchanged` (`test_telemetry.py`).** The `t` values returned by
   `get_series` for a given `(t0, t1, n)` are identical to `telemetry.series()`'s instants for the
   same arguments, and the response keys/shape are unchanged.
8. **`test_series_replay_cost_is_single_pass` (cost guard, `test_telemetry.py`).** On a session
   whose 1 h window spans several distinct event-log positions, one `get_series(n=120)` call
   applies at most `len(eventlog.entries)` handler invocations and constructs the start world from
   `initial_state` at most once (measure by monkeypatching/wrapping — e.g. counting calls through
   wrapped handlers passed via `mgr.sim.handlers()`, or counting the engine generator's starts;
   `08` picks the mechanism, the assertion is fixed). Today's per-seq approach (`BL-0170` Option 1)
   would exceed it.
9. **`test_ephemeris_exports_unchanged_after_migration` (`test_ephemeris.py`).** On a session with
   several events in the span, `truth_ephemeris` and `cell_observed_ephemeris` rows equal a
   reference built in the test by the pre-migration algorithm (`state_at_time` per
   `sample_times` instant, same row construction) — compared exactly, including skipped
   (no-track) instants. The existing 29 ephemeris tests must also stay green unchanged.
10. **`test_telemetry_series_route_matches_export_csv` (scenario D, `test_web.py`).** Via
    `TestClient`: step 600 s, `anomaly` inject, step 600 s; request
    `/telemetry/blue/ISR-EO-1/snr_db?t0=<start>&t1=<start+1200 s>&n=5` and
    `/telemetry/blue/ISR-EO-1/export.csv` over the same span with `interval_s=300` (so the instants
    coincide): `snr_db` value and status agree at all 5 shared instants; pre-onset points `green`.
    Fails today.

- **Existing tests that must stay green unchanged:** `test_telemetry.py`'s seven `IP-1260` export
  tests (incl. `test_telemetry_export_matches_live_endpoint_and_engine_sample_at_each_point`, which
  already pins export == replay reference), `test_ephemeris.py` (29), `test_aar.py` (9),
  `test_web.py::test_telemetry_series_count`.
- **Permanent gates:** `spacesim/tests/test_determinism.py` and `spacesim/tests/test_import_guard.py`
  green. Full suite green (baseline 813 passed / 3 skipped at `IP-1260`'s verification; expected
  new count = baseline + the 10 tests above).

## Documentation Updates

- RTM (`docs/requirements/03-requirements-traceability-matrix.md`): add `IP-1261` to the
  `Impl. Package` cells of `FR-2320`, `FR-7410`, `FR-7420`, and name the new tests in `FR-2320`'s
  test column. Do **not** touch `FR-2310`'s row (see Requirements Covered).
- `CLAUDE.md` code map: the `engine/simulation.py` bullet (`:225`) names the new stepwise replay
  function; the `session/aar.py` bullet (`:441`) names the time-keyed helper and that `get_series`/
  `telemetry_export`/both ephemeris exports share it.
- `docs/training/15-manual-traceability.md` §15.1: check the telemetry-graph / drill-down rows. The
  as-built behaviour of the graphs *changes* (history is now correct). If any manual section
  describes the windowed graphs in a way that depended on (or documented) the back-dated behaviour,
  route a manual-impact finding to `08-training-manual-authoring` — do not edit `docs/training/`
  from `08-code-implementation`.
- This package's Status header; the Master Build Plan row; `packages/INDEX.md`; `ROADMAP.md`'s
  implementation-package row.

## Definition of Done

- `get_series` returns, at every sampled instant, the value/status `telemetry.sample()` gives on
  the world as of that instant; scenarios A-D (Tests 1-4, 10) pass.
- One `get_series` call performs at most one forward replay pass (Test 8).
- `telemetry_export`, `truth_ephemeris` and `cell_observed_ephemeris` produce output identical to
  before (Test 9 + all existing export/ephemeris tests green) and all go through the shared helper.
- `engine/simulation.py::replay()` is byte-for-byte unchanged; the only engine change is the
  additive generator.
- RTM, `CLAUDE.md` and ledgers updated per Documentation Updates.
- Full suite green; both permanent gates green.

## Verification Checklist

- [ ] `git diff` of the implementing commit shows `replay()`'s body in `engine/simulation.py`
      unchanged, and no other `spacesim/engine/` file modified.
- [ ] `grep -n "self.sim.world" spacesim/session/manager.py` shows `get_series` no longer passes
      the live world to `telemetry.series()`/`sample()` for its window.
- [ ] `grep -n "state_at_time" spacesim/session/ephemeris.py` returns no per-sample calls;
      `grep -n "worlds\[seq\]\|replay(" ` within `telemetry_export` returns none — both route
      through the shared helper.
- [ ] Each of the 10 new tests exists and passes; Tests 1-4 and 10 were observed failing before the
      fix (recorded in the Implementation Summary).
- [ ] The `BL-0170` intake reproduction (scenario D: the console's own `?n=120` default-window call
      after step/inject/step) re-run against the fixed tree shows pre-onset `snr_db` points `green`,
      matching `export.csv`.
- [ ] `python3 -m pytest` passes in full; `test_determinism.py` and `test_import_guard.py` pass.
- [ ] RTM `FR-2320`/`FR-7410`/`FR-7420` rows cite `IP-1261`; `FR-2310`'s row is unchanged.
- [ ] The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header
      all agree on status.

## Dependencies

- **Packages:** [IP-1260](IP-1260-telemetry-csv-export.md) (`VERIFIED` 2026-10-10) and
  [IP-1210](IP-1210-ephemeris-export.md) (`VERIFIED`) — the two time-span replay call sites this
  package consolidates. Both `VERIFIED`, so this package is `READY`.
- **Authorization:** granted by the project owner 2026-10-11 (MSTR-006 §3) — the owner
  pre-authorized `08-code-implementation` for the package(s) this pipeline iteration reaches,
  following the same precedent as `IP-1211` (`BL-0109`) and `IP-1300`/`IP-1260`.
- **Not a dependency:** `BL-0171` (`FR-2310` pass-gating on historical points). A pass-gating
  change, if `04` decides one is wanted, would be a separate additive package layered on this
  package's helper.
- **Parallelism:** no ordering constraint with any other open package (`IP-1160` is
  authorization-blocked and touches disjoint files).

## Risks

- **Live world ≠ full replay.** The live-tail shortcut assumes the live world equals a full
  replay — the determinism invariant. If any live-only mutation exists outside the event log, the
  tail and replayed points would differ. Mitigation: Test 5 compares the shortcut path against
  `state_at_time` field-for-field; a failure there is a determinism finding to route, not to paper
  over.
- **Shared mutable world across yields.** The helper yields one mutating object. A consumer that
  keeps a reference to a nested object (e.g. a `Track`) across yields would read later state.
  Today's consumers extract scalars/lists immediately (`sample()` returns a dict of scalars;
  ephemeris rows use `.tolist()` and call `current_confidence(t)` immediately). Document the
  read-before-advance rule in the helper's docstring.
- **Lock-hold time on long sessions.** One full replay per call (~3.6 ms at 73 entries on
  `multi-domain-taiwan`, `BL-0170`'s measurement) × ~21 calls per drill rebuild ≈ 75 ms, linear in
  log length, versus ~0.9 ms × 21 today (wrong but cheap). Record the measured per-call cost on
  `multi-domain-taiwan` at +6 h in the Implementation Summary. If it is materially worse than the
  estimate, file a finding for `BL-0170` Option (5) (production snapshotting) rather than adding a
  cache in this package.
- **Historically absent assets.** An asset force-added (TLE/OMM) mid-session reads `los` at instants
  before it existed (replayed world has no such asset) — correct history, and identical to what
  `telemetry_export` already does; note it in the Implementation Summary.
- **Ephemeris output drift.** Any accidental difference in sampling instants or skip rules would
  silently change exports. Test 9's exact-equality reference plus the existing 29 tests are the
  guard.

## Rollback Considerations

Reverting the implementing commit restores the prior behaviour exactly: the engine change is a
purely additive function, no schema, API, persisted format or `SavedSession` field changes, and no
data migration is needed. A partial rollback (keeping the exports on the helper but reverting
`get_series`) would reintroduce the `FR-2320` parity defect and is not recommended.
