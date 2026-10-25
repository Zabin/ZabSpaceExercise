# VR-1083 — Verification Report: A Rewind or Undo Keeps White Cell's Future-Dated Injects (FR-4410, FR-4450, BL-0284)

> **Document ID:** VR-1083
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1083](../packages/IP-1083-rewind-keeps-future-white-injects.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1083`
> **Feature Mapping:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1083 v1.0, implementing commit `c98fc8f` on branch `claude/ip-1083-build` (parent `24ee6b7`). Verified in a
fresh session in a separate worktree; the implementation was not done in this session.

## Result

**VERIFIED** — 0 failed checks. Two Info observations and one Low (below); none blocks.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Reproduction no longer loses the inject; test 1 passes | Over real HTTP (`TestClient`, `create_app`) on `00-training-basics`: schedule +2 h, advance +1 h, rewind to +11 min. Parent (`24ee6b7`, `git archive` copy): `GET /injects/pending` white rows `[]`. Fix: `['white-1']`. `test_reproduction_rewind_keeps_future_inject` passes | pass |
| Every matrix row passes; "seen failing first" rows observed failing | 25 collected cases in `test_inject_rewind_rearm.py` all pass. Parent-revert mutation (below) fails the reproduction test, so the rewind/undo/save-then-rewind rows fail without the change | pass |
| A scheduled White inject is an `inject_admin` `schedule` entry; no state outside the log | `manager.py` `fire_inject` future branch: `_log_inject_admin({handle, trigger:"time"}, "schedule", effects, when)` then `sim.schedule(..., "rev": rev, tag=handle)`. `git diff HEAD~1 -- spacesim/session/manager.py` is 11 lines; no new field on `SessionManager` or `WorldState`; `save_state`/`from_state` untouched | pass |
| No-future-inject session unchanged (test 15) | Immediate and past-clamped injects take the unchanged branch (`when <= now`); test 16 asserts no `schedule` entry; test 15 compares logs | pass |
| Determinism and import-guard green; doc-integrity and test-origins green; RTM regenerated | See Test run. `--origin-report=rtm` reports "unchanged" and leaves the tree clean | pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Reproduction on a fresh session and on the pre-change commit | Done above, parent copy fails, fix passes; also repeated on 5 shipped vignettes (below) | pass |
| Read `fire_inject`, `_h_inject_admin`, `_arm_schedule` for hidden state | Read in full. `_h_inject_admin` returns before touching `world` for `schedule`; the override fold is read from `eventlog.entries` only; `pending_injects` lists one row per handle (scheduler loop skips events carrying `rev`, override loop lists them) | pass |
| Determinism + import-guard by name | `test_determinism.py`, `test_import_guard.py` pass; `git diff HEAD~1 -- spacesim/engine` empty | pass |
| Full suite, no regressions | Unfiltered exit 0 (below) | pass |
| `test_test_origins.py`, `test_doc_integrity.py` | Pass | pass |
| Landing exactly on a fire time fires once (test 6) | Test 6 passes; independently over HTTP: inject at F and another at F+1 µs, advance to F, rewind to F gives the F inject retained as fired once and the F+1 inject pending; advance to end gives each exactly once (blue and red targeting right: blue got `Wf`, red got `Wr`) | pass |

## Requirements audit

| Req | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-4410 | `manager.py` `fire_inject`, `_arm_schedule` guard | module-level marker in `test_inject_rewind_rearm.py` | Test column lists the new module's tests; `--origin-report=rtm` says unchanged (equals tool output) | pass |
| FR-4450 | same, `_h_inject_admin` `schedule` branch | per-test `verifies("FR-4450")` on schedule/edit/cancel cases | as above | pass |
| FR-1120 (added tag) | replay-equals-live | tests 15 and one more carry `("IP-1083","FR-1120")` | RTM FR-1120 row gained the tests | pass |

All markers name live baseline IDs (the origin suite is green).

## Independent probes (real HTTP, `TestClient` over `create_app`)

- **Vignettes:** `00-training-basics`, `03-gnss-ew-campaign`, `05-da-asat-crisis`, `08-multi-domain-taiwan`, `coa-russia-md`, `mt-isr-sar`, `mt-sigint-geolocate`. Four White injects scheduled at +20/+30/+60/+120 min with the clock at +10 min; advance to +70; rewind to 45 (`white-3`, `white-4` pending), to 30 (the F=30 inject retained as fired, not re-armed), to 25 (`white-2` pending again), to the scheduling instant (all pending; verified with the exact instant, microsecond-level, not minute-truncated), to before it (none; never fire). Advance across all of them: each fires exactly once, message delivered once. `sim.replay().model_dump() == world.model_dump()` after every step.
- **Undo:** `undo n=1` straight after scheduling withdraws the inject (the schedule entry is the last log entry; clock steps log nothing) and moves the clock back to the previous entry's instant; `n` reaching the entry withdraws it. See finding F1.
- **Edit/cancel after rewind:** rewind to the scheduling instant, edit `white-1`, cancel `white-2`, step, rewind to after the edit: edited effects and cancellation persist; the edited inject fires once with the edited text, the cancelled never fires.
- **Save/load:** save after a rewind, `load_save`: pending preserved, fires once, replay equals live, a later rewind keeps it, cancelled stays cancelled. **Genuine pre-package save:** produced from a `git archive` copy of the parent (pending White event, no `rev`, no schedule entry), loaded in the fix: loads (version warning only), `white-1` pending, fires once, replay equals live; a later rewind loses it (the documented limitation, test 14). The builder's test 14 strips `rev` from the hand-built save; I confirmed that is faithful to a real parent save, which carries no `rev`.
- **Seat/fog:** Blue, Red and Observer `POST /inject` are 403. Cell-scoped reads (`/view`, `/scene`, `/messages`-class, AAR `/aar`, `/aar/at`, `/aar/export.csv|json`, playback from a Blue viewpoint) contain neither the inject text nor `inject_admin`. The only routes carrying the schedule entry or inject text are no-cell White reads that already carried it: `/eventlog`, `/save`, `/injects/pending` (FR-6220 / LAN trust model). See F2.
- **Guards:** `at_sim_t` NaN/Infinity is 400 with the log unchanged; `1e308` is 422; `10**18` is accepted, scheduled once, and rewind/undo and replay stay consistent. Out-of-span rewind is the unchanged IP-1074 400.

## Mutations (on a scratch copy; real tree untouched)

| Mutation | Result |
|---|---|
| Parent behaviour (no schedule log, guard `<=`, no handler branch) | `test_reproduction_rewind_keeps_future_inject` fails |
| Drop the `schedule` log entry only (`rev = 1`) | same test fails |
| Guard `<` reverted to `<=` | `test_landing_exactly_on_fire_time_with_own_entry_dropped_rearms_once` fails |
| Drop the `rev` carry from the scheduled event | `test_fired_then_rewind_before_fire_time_fires_again_once` fails |
| `_h_inject_admin` not handling `schedule` | `test_schedule_adds_no_message_but_cancel_and_edit_still_do` fails |
| Break the re-arm of rev-1 overrides after rewind | `test_schedule_edit_rewind_between_and_after` fails |

## Test run

All from the worktree, real exit codes, `--junitxml`.

| Command | Result |
|---|---|
| `python3 -m pytest -q --junitxml=all.xml` (unfiltered) | exit 0; 1811 tests, 0 failures, 0 errors, 3 skipped |
| `python3 -m pytest -q -m "not browser"` | exit 0; 1778 tests, 0 failures, 4 skipped (the 3 above plus `test_the_committed_matrix_test_column_equals_the_generated_one`, which skips on a partial collection by design; the unfiltered run executes it) |
| `python3 -m pytest -q -m browser` | exit 0; 33 tests, 0 skipped |
| `test_determinism.py test_import_guard.py test_doc_integrity.py test_test_origins.py test_origin_retag.py` | exit 0 |
| `python3 -m pytest --origin-report=rtm` | "regenerated (unchanged)"; `git status` clean |

## Scope audit

Changed: `spacesim/session/manager.py`, `spacesim/tests/test_inject_rewind_rearm.py`, `CLAUDE.md`, `ROADMAP.md`, the MBP, `packages/INDEX.md`, the RTM. All inside the package's file set and Documentation Updates. `spacesim/engine/` and `docs/pipeline/` untouched. Package and FS not edited.

## Ledger audit

Tally recounted from the MBP package-table status column before this update: 83 `VERIFIED`, 1 `COMPLETE` (`IP-1083`), 1 `READY` (`IP-1160`), 85 packages, matching the 08 note. After this update: 84 `VERIFIED`, 1 `READY`, 85.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | The first `undo` after scheduling a future inject now withdraws the inject (and rewinds the clock to the previous log entry's instant) instead of undoing the previous action. This is the package's stated Risk and matches cancel/edit; the user-visible effect is that Undo can silently remove a scheduled inject. Consistent with the stated behaviour. | Info | `08-training-manual-authoring` (note in the White manual's undo text, with the package's own manual-impact routing); UI text optional |
| F2 | `/eventlog` (and AAR-free ground-truth reads) now show a pending future inject's effects from the moment it is scheduled, not only once it fires. Not a new disclosure: `/injects/pending` and `/save` already expose the same data without a cell binding, and no cell-scoped read leaks it. | Info | none (FR-6220 trust model) |
| F3 | A save written before this package still loses a pending White inject on a later rewind (test 14). Accepted by the package; reproduced with a genuine parent-made save. | Low | accepted limitation, already documented |

Also noted, pre-existing and unrelated: `at_sim_t: true` is coerced to 1 and fires an immediate inject (the IP-1082 F4 boolean-coercion observation on a route outside its list).

## Independence

Fresh session; the builder's tests were run but every behavioural claim above was re-derived with separate probes and a parent copy.
