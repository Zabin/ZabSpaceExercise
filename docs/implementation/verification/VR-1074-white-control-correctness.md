# VR-1074 — Verification Report: White Control Correctness (FR-4310, FR-4320, NFR-1600)

> **Document ID:** VR-1074
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1074](../packages/IP-1074-white-control-correctness.md) v1.0,
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1074` (closes `BL-0364`, VR-1073 F3, VR-1072 F1)
> **Feature Mapping:** FS-106

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1074 — White Control Correctness (v1.0)
- **Implementing commit:** `62de942` (branch `claude/ip-1074-build`); tree verified at that commit.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 1 Medium finding (pre-existing root cause, outside the package's stated scope, routed to the backlog) and 2 Low findings.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Part A and B tests exist, seen failing first, pass; browser case ran in Chromium | Restoring the parent `manager.py`/`inprocess.py`/`server.py` fails `test_rewind_to_zero_is_refused…`; the parent `app.js` fails the browser case (`test_rewind_to_start_sends_the_exercise_start_epoch_not_zero`); `-m browser` ran 22 passed, 0 skipped | pass |
| Rewind outside `[start_epoch, now]` is a 400, nothing changed; rewind to start lands on `start_epoch`; save is start-sized | Probe on all 19 vignettes: t=0, `start-1`, `now+1` all 400 with the clock unchanged; `start_epoch` → 200, clock `== start_epoch`, `GET /save` 9–32 KB (not hundreds of MB), 0.00 s | pass |
| `roles/assign`, `observer/view` 403 for non-white query seat; success unchanged | Matrix probe (below); `server.py` `_require_white(cell)` on both | pass |
| No existing assertion weakened; edits are a query seat or the documented expectation | See "Existing-test edits" | pass (note F2) |
| Full suite and both gates green; RTM regenerated | See Test run; `--origin-report=rtm` reports "unchanged" | pass |
| `git diff --stat` only named files plus docs | See Scope audit | pass (note F2) |
| Completion note records Decision 4 | MBP row states the open question; running state pinned by tests | pass |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | No FR-4320-listed route lacks `_require_white` | Live route table enumerated; `test_white_only_controls.py` covers the set; both newly guarded routes 403 for blue/red/observer/no seat | pass |
| 2 | Drive the real server and Chromium | HTTP probe on 19 vignettes; headless Chromium: palette "rewind to start" and toolbar Rewind each send `{"t": start_epoch}`, return 200, clock `now == start`, `running` unchanged, `c.errors == []` | pass |
| 3 | Mutations each fail a test | Removed lower bound → `…rewind_to_zero…` fails; removed upper bound → `…before_start_and_after_now…` fails; removed 400 mapping → `…rewind_to_zero…` fails; removed `_require_white` on `roles/assign` → `…refuse_by_query_seat[blue-roles/assign]` fails; on `observer/view` → `[blue-observer/view]` fails; on `rewind` → `…non_white_is_403…` fails; `app.js` reverted to the parent, or its `start_epoch` read replaced with `0` → the browser case fails; `start_epoch` dropped from `clock_state` → `test_clock_state_exposes_start_epoch` and the browser case fail. All run in a scratch copy and discarded. | pass |
| 4 | `engine/` unchanged | `git diff 62de942~1 62de942 -- spacesim/engine` is empty | pass |
| 5 | All eight existing in-tree `rewind_to` callers pass | Full suite green; but see F2 (three tests that rewound to 0 in `test_web.py` / `test_white_only_controls.py` had to change) | pass (F2) |
| 6 | Full suite, browser, determinism, import guard, doc integrity, test origins green | See Test run | pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-4310 | `manager.py::rewind_to` span guard; `clock_state.start_epoch`; `app.js` `exerciseStartEpoch` | `test_white_control_correctness.py`, browser case | regenerated, unchanged by `--origin-report=rtm` | pass |
| FR-4320 | `server.py` `set_observer_view`, `assign_role` | query-seat matrix tests; `test_white_only_controls.py` | same | pass |
| NFR-1600 | 400 with the span named, via `ValueError` → `Ack(ok=False)` → `HTTPException` | `test_rewind_to_zero…`, `…before_start_and_after_now…` | same | pass |

## Test run

- `python3 -m pytest -m "not browser" -rs` — **1405 passed, 4 skipped, 22 deselected** (the 4 skips are the known inapplicable ones).
- `python3 -m pytest -m browser` — **22 passed, 0 skipped** (Chromium ran).
- Gates by name: `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_white_control_correctness.py`: all green.
- `python3 -m pytest --origin-report=rtm` — "traceability matrix Test column regenerated (unchanged)", so the Test column equals the tool output.

### Behavioural probes (real HTTP routes, TestClient over `create_app`)

- **Rewind range**, on all 19 vignettes: `t=0`, `start-1`, `now+1` → 400 each, clock unchanged.
- **Valid mid-session rewind**: for each vignette, after two steps, rewind to the earlier instant. The world state (`model_dump_json`) and the event log are byte-identical to the reference snapshot taken at that instant on the same session. The determinism property test is green. The engine is untouched.
- **Rewind to `start_epoch` after advance** returns 200 and lands on `start_epoch` for every vignette where undo had not been used first.
- **Seat matrix** (`roles/assign`, `observer/view`; query seat × body seat): query white → 200 whatever the body says, including body blue; query blue/red/observer/none → 403 whatever the body says, including body white with query blue.
- **Reproduction**: the parent code accepts `t=0` (200); the fixed code gives 400.
- **AAR / branch / time-rewind**: `test_aar.py` (`state_at_time`, `PlaybackSession`, branch compare) passes; the engine and `aar.py` are untouched.

### Existing-test edits (outside the package's named list), judged

| Edit | Judgement |
|---|---|
| `test_white_only_controls.py::test_clock_controls_accepted_for_white[rewind]` (`_body` now sends `ctx.start_epoch`; expects `now == start_epoch` instead of `0`) | Legitimate. Same assertion translated into the exercise's coordinates; the effect is still asserted. |
| `test_web.py::test_full_flow_order_advance_objectives_and_rewind` (`t: 0` → `t: start`) | Legitimate. The test means "rewind to the start"; the rewound objective assertion is unchanged. |
| `test_web.py::test_rewind_re_anchors_clock` (`t: 0` → `t: start_now`) | Legitimate. It still pins re-anchoring (+5 s wall → +5 s sim after the rewind). |
| `test_observer.py`, `test_white_only_controls.py` seat tests (now expect 403 with the test's own query seat, no longer `ok:false` 200) | Legitimate and stronger. The state-unchanged assertions remain; the session-layer `ok:false` path is pinned separately by new test 13. |

## Scope audit

Within scope: `manager.py`, `inprocess.py`, `server.py`, `app.js`, the new test module, the named existing tests, the browser test and the docs. **Excursion:** `spacesim/tests/test_web.py` (two one-line edits) is not in the package's file list. Decision 1 anticipated that callers rewinding outside the span would be a finding; the edits are justified and are not a weakening (F2). `spacesim/engine/` is untouched.

## Findings

| ID | Description | Severity | Owner |
|---|---|---|---|
| F1 | `SessionManager.undo_last` (unchanged engine `Simulation.undo_last`) rebuilds with `stop_time = 0` once the event log is empty. Probe: start, step 300 s, step 100 s, undo once → sim clock is 1970 (`now = 0`), the same damaged state as the defect this package fixed. The root cause is pre-existing (identical on the parent commit) and is not in the package's scope or checklist. New interplay: in that state `hi = now = 0 < lo`, so "rewind to start" now answers 400 (it previously answered 200 and landed on 0, also wrong). Recovery is only by advancing. The package's goal "the clock cannot leave the exercise span" is therefore not fully met through undo. | Medium | Backlog it (`00-intake`) → `07-implementation-planning` remediation package: clamp undo's stop time to `start_epoch`, and/or let the guard treat `now < start_epoch` as recoverable. Does not block `IP-1074`. |
| F2 | Package said all in-tree callers pass unchanged, and DoD limited edits to query seats plus one documented expectation. Three existing tests that rewound to 0 changed (`test_web.py` ×2, `test_white_only_controls.py::_body`/`[rewind]`), and `test_web.py` is not in the file list. Not a weakening. | Low | `07` note for the record. |
| F3 | Stale curl recipes in docs and the `run-spacesim` skill: no call to the two seat routes was found without `?cell=`; the console `api.post` attaches the seat, so the UI is unaffected. | Info | None. |

## Verdict

All DoD and checklist items have evidence, the mutation set is fully caught, and the suite is green; `IP-1074` advances `COMPLETE → VERIFIED`. F1 is a separate, pre-existing defect routed for filing. Next step: file F1 via `00-intake`, then run `08-code-implementation` on `IP-1335`.
