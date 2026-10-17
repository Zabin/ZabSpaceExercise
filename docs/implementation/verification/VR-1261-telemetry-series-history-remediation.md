# VR-1261 — Verification Report: Telemetry Series History Remediation (Single-Pass Time-Span Replay)

> **Document ID:** VR-1261
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1261](../packages/IP-1261-telemetry-series-history-remediation.md),
> [FS-126](../../features/FS-126-telemetry-csv-export.md) v1.0 (`FR-2320`),
> [FS-121](../../features/FS-121-ephemeris-export.md) v2.0 (`FR-7410`/`FR-7420`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1261; adjudicates `BL-0173`; closes `BL-0170`
> **Feature Mapping:** FS-126 v1.0 (`FR-2320`); FS-121 v2.0 (`FR-7410`/`FR-7420`, migration only)
> **Related Topics:** [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py),
> [`spacesim/session/aar.py`](../../../spacesim/session/aar.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1261 — Telemetry Series History Remediation (Single-Pass Time-Span Replay)
- **Version verified:** 1.0
- **Tree state verified:** commit `d6f117f` (branch `claude/chart-prompt-file-90hm9u`, the tip this
  report commits onto). Implementing commit: `a5bf986` (2026-10-11); ledger-only follow-up `d6f117f`
  (pipeline journal/backlog, run #100) layered on top, untouched by this verification.
- **Independence:** first verification pass, fresh session with no involvement in `a5bf986` or any
  prior commit on this branch (confirmed: this session's working tree was checked out directly from
  `origin/claude/chart-prompt-file-90hm9u` at `d6f117f`, and no commit by this session predates this
  report). No prior `09-package-verification` run on this package.

## Result

**VERIFIED, with 1 Low finding.** `FR-2320`'s cross-route parity Postcondition is restored:
`get_series` now reads each sampled instant from the world as it actually was at that instant, via
one shared single-forward-pass helper (`session/aar.py::worlds_at_times`, built on the new additive
`engine/simulation.py::replay_stepwise`), and agrees with `telemetry_export` at every shared
instant. `FR-7410`/`FR-7420` (the two ephemeris exports) migrated onto the same helper with output
independently confirmed unchanged. `replay()` itself is confirmed byte-for-byte untouched. All four
of `BL-0170`'s original scenarios (A–D) were independently reproduced from scratch, on fresh
seeds/timings distinct from the implementer's own fixtures, and all now pass. The "single replay
per call" and "live-tail shortcut" claims were independently confirmed by instrumentation (not by
reading the docstring). The performance claim was independently re-measured and confirmed the same
order of magnitude, comfortably below the threshold that would require production snapshotting.
`BL-0173` (the reversed-window case) is **real and correctly handled**, confirmed by an independent
test built from scratch — adjudicated **accepted, no remediation required**, with one Low finding
(no regression test currently guards this path; see Findings). Full suite independently re-run:
**823 passed, 3 skipped (826 collected)**, matching the implementer's claim exactly; both permanent
gates independently re-run by name: **14 passed**.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `get_series` returns, at every sampled instant, the value/status `telemetry.sample()` gives on the world as of that instant; scenarios A–D pass | Independently reproduced all four scenarios on fresh seeds (777, 4242, 909090, 31415) and timings distinct from the implementer's fixtures (`_export_mgr()`, `_paused_mgr()`); see Test run / independent reproduction below. All passed. Also confirmed the 10 shipped tests (`test_telemetry.py` Tests 1–4,7,8; `test_aar.py` Tests 5,6; `test_ephemeris.py` Test 9; `test_web.py` Test 10) exist verbatim and pass in the full-suite run. | ✅ Pass |
| One `get_series` call performs at most one forward replay pass | Independently instrumented `engine.simulation.replay_stepwise` (monkeypatched a counting wrapper around the actual module-level name, not the implementer's own Test 8 cost-guard mechanism) on a fresh scenario (seed 5050, 6 eventlog entries spanning 6 distinct positions): exactly **1** `replay_stepwise()` generator instantiation per `get_series(n=37)` call, and total handler invocations (6) ≤ eventlog length (6). | ✅ Pass |
| `telemetry_export`, `truth_ephemeris`, `cell_observed_ephemeris` produce output identical to before, all via the shared helper | Read `ephemeris.py`'s diff directly: both functions' per-sample `aar.state_at_time(mgr, t)` loop body replaced by iterating `aar.worlds_at_times(mgr, sample_times(...))`; row construction (target/reference/track lookups, skip rules, `.tolist()` extraction) is untouched text, only the per-instant world's provenance changed. `manager.py::telemetry_export`'s old `worlds` memo dict is gone; `grep` (below) confirms no `worlds[seq]`/bare `replay(` remains in its body. Confirmed no behavior change independently (not merely re-running Test 9) — see Ephemeris migration audit below. | ✅ Pass |
| `engine/simulation.py::replay()` byte-for-byte unchanged; only engine change is the additive generator | `git show a5bf986 --stat -- spacesim/engine/` shows exactly one file changed, `53 insertions(+), 0 deletions(-)` — a pure append. Read `replay()`'s full body (lines 154–198) against the pre-commit tree (`git show a5bf986^:spacesim/engine/simulation.py`): identical. | ✅ Pass |
| RTM, `CLAUDE.md`, ledgers updated per Documentation Updates | Read the diffs for all five files directly (not the Implementation Summary's description of them) — see Traceability audit below. | ✅ Pass |
| Full suite green; both permanent gates green | Independently re-run (not re-reading the implementer's own numbers): `823 passed, 3 skipped, 1 warning in 112.60s` (full suite, exit 0); `14 passed in 1.19s` (`test_determinism.py` + `test_import_guard.py`, exit 0). | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `git diff` of the implementing commit shows `replay()` unchanged, no other `engine/` file modified | `git show a5bf986 --stat -- spacesim/engine/` → one file (`simulation.py`), insertions only. | ✅ Pass |
| `grep -n "self.sim.world" spacesim/session/manager.py` shows `get_series` no longer passes the live world to `telemetry.series()`/`sample()` for its window | Ran the grep directly: every remaining `self.sim.world` hit in `manager.py` is in a different method (`get_telemetry`, `get_scene`, `get_ric_view`, `get_tle`, `get_godview`, `objectives`, etc.); `get_series`'s body (lines ~857–876) contains none — it calls `telemetry.sample(world, ...)` per `(t, world)` yielded from `aar.worlds_at_times`. | ✅ Pass |
| `grep -n "state_at_time" spacesim/session/ephemeris.py` returns no per-sample calls; `telemetry_export` has no `worlds[seq]`/bare `replay(` | Ran both greps directly: `ephemeris.py`'s only `state_at_time` hit is the module docstring's prose description of what the shared helper reconstructs (not a call); `telemetry_export`'s body contains neither `worlds[seq]` nor a bare `replay(`. | ✅ Pass |
| Each of the 10 new tests exists and passes; Tests 1–4 and 10 were observed failing before the fix | All 10 confirmed present by name and passing in the independent full-suite run. "Observed failing before the fix" is a historical claim about the implementer's own test-first process (not independently re-creatable without reverting the fix); taken as asserted, consistent with this report's own independent finding that the pre-fix behavior (naive live-world sampling) does in fact fail scenarios A/B/D — confirmed by constructing the counterfactual directly: calling `telemetry.sample(mgr.sim.world, ...)` (the pre-`IP-1261` code path) on this report's own fresh scenario A fixture reproduces the leak (3/7 pre-onset points read `red`, as `BL-0170`'s original reproduction also found). | ✅ Pass |
| `BL-0170` scenario D re-run against the fixed tree shows pre-onset `snr_db` points `green`, matching `export.csv` | Independently re-built scenario D from scratch (seed 31415, different onset timing than the implementer's `?n=120` re-run) through the actual `TestClient`/HTTP route with no explicit `t0`/`t1` (`?n=120` only): 40/40 pre-onset points read `green`. | ✅ Pass |
| `python3 -m pytest` passes in full; both permanent gates pass | See Test run. | ✅ Pass |
| RTM `FR-2320`/`FR-7410`/`FR-7420` rows cite `IP-1261`; `FR-2310`'s row unchanged | Read the diff directly: all three rows gained an `IP-1261 (...)` clause naming the real new test functions (cross-checked every named test exists); `FR-2310`'s row has zero diff lines. | ✅ Pass |
| MBP row, `packages/INDEX.md` row, `ROADMAP.md` row, package header all agree on status | All four read directly: all said `COMPLETE` consistently before this report; all four are flipped to `VERIFIED` by this report (see Ledger updates). | ✅ Pass |

## Independent reproduction — BL-0170 scenarios A–D (fresh seeds/timings, not the implementer's fixtures)

Built four standalone scenarios in this session, distinct from `_export_mgr()`/`_paused_mgr()`:

- **Scenario A (pre-onset leak).** `training-basics`, seed `777`, bus anomaly on `ISR-EO-1` at
  +450 s (implementer used +600 s), run to +1500 s, `get_series(n=11)`. All pre-onset `snr_db`
  points read `green`, all post-onset read `red`; every point matched the `aar.state_at_time`
  replay reference exactly.
- **Scenario B (forward-vanish-after-recovery).** Seed `4242`, anomaly at +300 s, cleared at
  +700 s, run to +1100 s, `get_series(n=23)`. The in-episode window (+300 s to +700 s) read `red`
  throughout — the cleared episode did not vanish from history — and every point matched the
  replay reference.
- **Scenario C (route-vs-CSV parity).** Seed `909090`, anomaly at +500 s, run to +900 s. Compared
  `get_series(n=9)` directly against `telemetry_export(interval_s=...)` chosen so their instants
  coincide: all 9 shared instants agreed in both value (exact) and status.
- **Scenario D (live HTTP route, console default shape).** Fresh `TestClient` session (seed
  `31415`), `step 200s → inject → step 400s`, then `GET /telemetry/blue/ISR-EO-1/snr_db?n=120`
  with **no explicit `t0`/`t1`** (the console's actual default call shape). 40/40 pre-onset points
  read `green`.

All four independently constructed scenarios passed against the shipped tree. (Scripts retained at
`/tmp/claude-0/.../scratchpad/verify_ip1261.py` for this session; not committed — scratch, not a
project artifact.)

## `worlds_at_times()` / `replay_stepwise()` claim audit (independent instrumentation)

- **Single-pass claim.** Built a fresh scenario (seed `5050`, two anomaly injects, 6 eventlog
  entries) and monkeypatched the actual `spacesim.engine.simulation.replay_stepwise` module
  attribute (and the name `session.aar` imported directly) with a counting wrapper, independently
  of the implementer's own Test 8 mechanism. One `get_series(n=37)` call — whose 37 sampled
  instants span all 6 distinct event-log positions — instantiated the generator **exactly once**
  and invoked handlers **6 times total** (≤ eventlog length). Confirms the claim is not an
  unexercised docstring assertion.
- **Live-tail shortcut.** On the same scenario, calling `aar.worlds_at_times(mgr, [last_entry_time,
  now])` (both at/after the last entry) instantiated `replay_stepwise` **zero** times — the live
  world was yielded directly, as the code's `all(p == len(entries) for p in positions)` branch
  (read directly in `aar.py`) specifies.
- **Positional-indexing correctness.** `replay_stepwise`'s inner loop indexes `entries[applied]`
  directly rather than filtering by `entry.seq` as `replay()` does. Read `engine/eventlog.py`
  directly: `seq` is defined as "0-based and contiguous" and assigned `len(self.entries)` at
  append time — i.e., `entries[i].seq == i` always holds for an append-only log (no out-of-order
  insertion anywhere in the engine). This makes the two indexing schemes provably equivalent, not
  just coincidentally so on the tested fixtures.

## Ephemeris migration audit (independent, not re-running Test 9 alone)

Read `session/ephemeris.py`'s diff directly: the only change in `truth_ephemeris`/
`cell_observed_ephemeris` is replacing `for t in sample_times(...): world = aar.state_at_time(mgr,
t)` with `for t, world in aar.worlds_at_times(mgr, sample_times(...))`. Row construction,
target/reference lookups, and skip rules are identical, unedited lines. Since `worlds_at_times`'s
own contract (independently confirmed above) guarantees each yielded world is field-equal to
`state_at_time(mgr, t)` at the moment it is read, and both functions read every field they need
immediately within the same loop iteration (no world reference is retained across a yield — read
directly, confirmed), the migration cannot change output. Additionally ran the implementer's own
Test 9 (`test_ephemeris_exports_unchanged_after_migration`) in the full-suite run: passed. All 29
pre-existing `test_ephemeris.py` tests (predating this package, unrelated to its own fixtures)
remain green, independently confirmed in the same full-suite run.

## `BL-0173` adjudication — reversed window (`t1 < t0`)

**Real, and correctly handled; adjudicated accepted, no remediation required to IP-1261 itself.**

Read `get_series`'s body directly: `backwards = t1 < t0`; when true, the (already-descending,
since `step = (t1-t0)/(n-1)` is negative) `times` list is reversed to ascending before being passed
to `worlds_at_times` (which requires non-decreasing input and would otherwise raise `ValueError`
on a genuinely descending sequence), and the resulting points are reversed back before return.

Independently verified this is not merely plausible-looking but actually correct: built a fresh
scenario (seed `606`, anomaly at +400 s) and called `get_series` twice — once forward
(`t0=start, t1=now`), once reversed (`t0=now, t1=start`) — both `n=9`. The reversed call did not
raise. Its returned timestamps were the forward call's timestamps in reverse order, and at every
shared instant the value and status matched the forward call exactly.

This closes a real gap the package text does not mention (its Interfaces section describes only
the ascending-window case) — but the code change is a small, correct, behavior-preserving
addition (the pre-`IP-1261` route, built on a different mechanism, already answered a reversed
window without crashing, by virtue of sampling the live world uniformly regardless of order; this
addition keeps that property under the new mechanism, which does require ascending input
internally). No regression tests exist in the implementer's own 10 new tests for this path (`grep
-rn "backwards\|reversed" spacesim/tests/test_telemetry.py spacesim/tests/test_web.py` returns
nothing). **This is a Low finding** (see Findings) — the behavior is correct today, but nothing in
the suite would catch a future regression of it. It does not block `VERIFIED`: the package's own
Definition of Done and Verification Checklist never claimed reversed-window handling, so its
absence from the package text is a documentation gap, not a broken claim.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-2320 | `session/manager.py::get_series` (now via `aar.worlds_at_times`), `telemetry_export` (same helper) | `test_telemetry.py` Tests 1,2,3,4,7,8 (new) + the 7 pre-existing `IP-1260` export tests (unaffected, all green); `test_web.py` Test 10 (new) | RTM row cites `IP-1261` and names every new test; all named tests independently confirmed to exist and pass | ✅ Pass |
| FR-7410 | `session/ephemeris.py::truth_ephemeris` (migrated onto `worlds_at_times`) | `test_ephemeris.py` Test 9 (new, migration-equality) + all 29 pre-existing ephemeris tests (green, unaffected) | RTM row cites `IP-1261`, names Test 9 | ✅ Pass |
| FR-7420 | `session/ephemeris.py::cell_observed_ephemeris` (same migration) | Same Test 9 (covers both functions) + pre-existing suite | RTM row cites `IP-1261`, names Test 9 | ✅ Pass |

`FR-2310`'s row: confirmed zero diff lines (package correctly declined to claim it, per its own
Requirements Covered section; `BL-0171` — the pass-gating question — remains open and unaffected).

## Test run

- `python3 -m pytest` (full suite, independently re-run, no `-q` truncation issues after
  verification): **823 passed, 3 skipped, 1 warning in 112.60s** — exit code 0. Matches the
  implementer's claimed baseline-plus-ten exactly (baseline 813 + 10 new = 823; 826 collected).
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py`
  (independently re-run by name): **14 passed in 1.19s** — exit code 0.
- Both commands run directly in this session against the tree at `d6f117f` plus the unmodified
  implementing commit `a5bf986` already on this branch — not re-quoted from the Implementation
  Summary.

## Scope audit

`git show a5bf986 --stat` confirms the implementing diff touched exactly: `spacesim/engine/
simulation.py`, `spacesim/session/aar.py`, `spacesim/session/ephemeris.py`, `spacesim/session/
manager.py`, the four declared test files, plus the declared documentation/ledger files
(`CLAUDE.md`, `ROADMAP.md`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/
packages/INDEX.md`, the package's own file, `docs/requirements/03-requirements-traceability-matrix.md`).
No file outside the package's declared `Files to Modify` / `Documentation Updates` lists was
touched. `docs/training/` was correctly left untouched, with the manual-impact note routed to the
backlog (`BL-0172`) rather than edited in-session — confirmed by `git log` on the three manual
files showing no commit by `a5bf986`.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 | `get_series`'s reversed-window handling (`BL-0173`) is correct (independently verified) but has no regression test anywhere in the suite — a future refactor of `get_series` or `worlds_at_times` could silently reintroduce a crash or wrong ordering on a reversed window with nothing failing. | Low | `08-code-implementation` (a small, additive follow-up test; not blocking this package's `VERIFIED` status — the package's own DoD never claimed this case) |

No Medium/High/Critical findings. No defect found in the core remediation, the shared-helper
mechanism, or either migrated export.

## Ledger updates applied by this report

- **Master Build Plan** (`docs/implementation/00-master-build-plan.md`): `IP-1261` row status
  `🔵 COMPLETE → ✅ VERIFIED`, with this report linked and `BL-0173`'s adjudication summarized.
- **`packages/INDEX.md`**: `IP-1261` row status updated to `✅ VERIFIED 2026-10-11 via VR-1261`.
- **`ROADMAP.md`**: `IP-1261` row status updated to match.
- **Verification `INDEX.md`**: new row added for `VR-1261`.
- **RTM**: no cell correction needed — `FR-2320`/`FR-7410`/`FR-7420` rows already correctly named
  `IP-1261` and its real tests; left as-is (confirmed correct, not re-written).
- **`FS-126`/`FS-121`'s own `Referenced By` fields**: left untouched (still name `COMPLETE`/the
  package in general terms) — this skill does not edit Feature Specifications, matching `VR-1260`'s
  and `VR-1211`'s identical treatment.

## Related

[`00-master-build-plan.md`](../00-master-build-plan.md) · [`packages/INDEX.md`](../packages/INDEX.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../../requirements/03-requirements-traceability-matrix.md)
