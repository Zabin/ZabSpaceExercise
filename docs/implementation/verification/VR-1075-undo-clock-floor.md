# VR-1075 — Verification Report: Undo Clock Floor (FR-4310, NFR-1600)

> **Document ID:** VR-1075
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1075](../packages/IP-1075-undo-clock-floor.md) v1.0,
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1075` (closes `VR-1074` F1)
> **Feature Mapping:** FS-106

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1075 — Undo Clock Floor (v1.0)
- **Implementing commit:** `dfa63b4` (branch `claude/ip-1075-build`); tree verified at that commit.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 2 Low findings (a test gap and a redundant guard), none blocking.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Tests 1-12 exist, seen failing first, pass | `test_undo_clock_floor.py` (22 collected incl. parametrisation). With the parent `simulation.py`/`manager.py`/`inprocess.py`/`server.py` restored in the worktree, 17 of them fail (empty-log, n<1, 1970 landing, oversize n, rewind-to-start, random sequences x5, tick resume x2, running clock, engine unit, save); files restored afterwards | pass |
| No sequence of undo/rewind/advance/step leaves `now < start_epoch` | Own probe: seeded random op sequences on all 19 vignettes, `now >= start_epoch` after every call; the module's property test passes | pass |
| `/undo` on an empty log is 400, nothing changed; undo to the beginning lands on `start_epoch` | HTTP probe below | pass |
| A save after undo reloads | Test 11 passes; `validate_save` still refuses `final_time < start_epoch` | pass |
| Full suite, gates, doc integrity, test origins green; RTM regenerated | See Test run; `--origin-report=rtm` says "unchanged" and `git status` is clean | pass |
| Docs updated; MBP row `COMPLETE` | CLAUDE.md `session/` bullet, `12-white-cell-manual.md`, FS-106 Referenced By, MBP, packages index, ROADMAP | pass |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Reproduce on the parent and see it gone | Parent files: 17 tests fail (incl. `…lands_on_start_epoch_not_1970`); fixed tree: clock is `start_epoch` after undo-all | pass |
| 2 | Every test names its origin; failing-first recorded | Module `pytestmark` FR-4310/NFR-1600; per-test `IP-1075`, `FR-7220`, `FR-4320`; `test_test_origins.py` green | pass |
| 3 | `engine/` imports no UI, no wall clock | `test_import_guard.py` green; the engine change reads `_initial_state["now"]` only | pass |
| 4 | Determinism green; landing-time change does not alter replay of retained entries | `test_determinism.py` green; own probe: random undo/rewind/step sequences on all 19 vignettes, then `world` JSON of the live session equals `sim.replay()` byte for byte, 0 mismatches. A fresh-vs-undo-all-then-step comparison differs only by the 2-3 microsecond lazy-clock offset between `start()` and `set_clock(False)`, which also appears on the `rewind_to` path (not a defect) | pass |
| 5 | `rewind_to`, `advance_to`, `from_state` unchanged | `git diff HEAD~1 -- spacesim` touches only `undo_last` in the engine and manager | pass |
| 6 | Existing-test edits listed, none weakens | See Existing-test edit | pass |
| 7 | doc integrity and test origins green; no allow-list grew | Both run; no `*allow*` file in the diff | pass |
| 8 | Re-arm matches `rewind_to`, no double schedule | Scheduler heap after undo(1) of 3 steps = 46 entries, equal to a `rewind_to` to the same instant (46). On 19 vignettes, after undo-all then 3600 s, no duplicate `bus_tick` times, and tick count equals the rewind-to-start path | pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-4310 | `manager.py::undo_last`, `simulation.py::undo_last` | `test_undo_clock_floor.py`, `test_white_only_controls.py`, browser case | regenerated, unchanged | pass |
| NFR-1600 | `ValueError` → `Ack(ok=False)` → HTTP 400 | tests 1, 2, 5 | same | pass |
| FR-7220 | pinned only | test 11 | same | pass |

## Test run

- `python3 -m pytest -m "not browser"` — **1437 passed, 4 skipped, 23 deselected**.
- `python3 -m pytest -m browser -rs` — **23 passed, 0 skipped** (Chromium ran, including the new undo case).
- Gates by name: `test_determinism.py`, `test_import_guard.py`, `test_undo_clock_floor.py`, `test_doc_integrity.py`, `test_test_origins.py` — 66 passed, 1 skipped (the RTM-column check, which needs the whole suite and passes in the full run).
- `python3 -m pytest --origin-report=rtm` — "unchanged"; Test column equals tool output.

### Behavioural probes (real `/undo` route, TestClient over `create_app`, leo-isr-denial)

| Case | Result |
|---|---|
| Fresh started session, `n=1` | 400, clock unchanged |
| `n=0`, `n=-1` (fresh and after many steps) | 400 each |
| After `step 100` (log still empty) | 400 |
| After `step 400` (one entry), `n=1` | 200, `now == start_epoch` |
| After 9 steps, `n=1` then `n=10**12` | 200, 200, `now == start_epoch`; a further undo 400 |
| Then `rewind` to `start_epoch` | 200 (the VR-1074 F1 symptom is gone) |
| `n="x"` | 422 |
| blue, red, observer, no seat | 403 each, clock unchanged |

All 19 vignettes: undo-all landed on `start_epoch`, an immediate second undo was refused, rewind-to-start then worked.

### Mutations (scratch edits in the worktree, restored with `git checkout`)

| Mutation | Result |
|---|---|
| Drop the empty-log refusal | 2 tests fail |
| Drop the `n < 1` refusal | 2 tests fail |
| Engine fallback to `0` | `test_engine_undo_on_empty_log_keeps_initial_time` fails |
| Remove the re-arm | `test_bus_ticks_resume_after_undo`, `test_undo_to_start_then_step_resumes_ticks` fail |
| Remove the `/undo` 400 mapping | the HTTP cases fail |
| Whole fix reverted (parent files) | 17 fail |
| Remove the manager's `start_epoch` floor alone | **no test fails** (F1) |
| Arm the schedule twice | **no test fails**, and it does produce duplicate ticks (F2) |

### Existing-test edit

`test_white_only_controls.py::test_clock_controls_accepted_for_white` steps 600 s instead of 120 s so the log is non-empty (an empty-log undo is now refused by design). Every assertion is unchanged (200, the `rewind` and `clock` effects, state changed). Not weakened.

## Scope audit

Within the file lists, plus the browser test (`test_browser_console_rules.py`, the "1 browser case" the completion note states) and the CLAUDE.md/FS-106/manual/ROADMAP/MBP/RTM documentation. The console needed no change: the shipped client has no Undo control. `docs/pipeline/` untouched. The package header still reads `READY`; the build correctly did not edit the package.

## Findings

| ID | Description | Severity | Owner |
|---|---|---|---|
| F1 | The manager-level `start_epoch` floor (`if self.sim.clock.now < floor: _rebuild`) is unreachable once the engine fallback is in place, and no test removes-and-notices it. It is documented as belt and braces. | Low | None required; note for the record |
| F2 | The package's own Risk (re-arm "could double-queue ticks") is controlled only by reasoning: no test asserts that ticks are not duplicated, so arming twice passes all 22 tests (probe: 15 ticks, 9 distinct times). The shipped code arms once, confirmed by heap size and tick uniqueness. | Low | `08` follow-up test, or `07` note |
