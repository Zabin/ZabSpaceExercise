# VR-1068 — Verification Report: White-Only Controls Enforced at the Server Boundary (FR-4310, FR-4320)

> **Document ID:** VR-1068
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1068](../packages/IP-1068-white-only-controls-server-enforcement.md) v1.0,
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1068`
> **Feature Mapping:** FS-106 (`FEAT-4300`)

[↑ Verification index](INDEX.md) · [Docs index](../../INDEX.md)

## Package

IP-1068 v1.0, implementing commit `a64c438`; tree verified at `fe63caa` (branch `claude/verify-ip-1068`).
Independent fresh session (no part in implementation).

## Result

**VERIFIED** — 0 failed checks. Four findings (one Medium, three Low) are routed onward; none is a
DoD or checklist failure.

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Every Objective-table route refuses blue/red/observer/no seat, session unchanged; `roles/assign` and `observer/view` refuse blue/red with a reason | `server.py` `_require_white` (line ~340) applied to `clock, param, start, step, advance, rewind, undo, inject, force/tle, force/bulk_import, force/ground, load_save` (route table re-derived from source). `test_white_only_controls.py`: refused tests assert 403 + detail + `_snapshot` equality (started, sim time, event-log length, asset count, clock state/rate, params); `test_load_save_refused…`; `test_seat_assignment_and_observer_designation_refused_for_player_seats` asserts `ok:false` + reason and unchanged staffing/designation. | Pass |
| 2 | Same requests naming `white` behave as before | `test_clock_controls_accepted_for_white`, `test_config_controls_accepted_for_white`, load_save accepted leg; ~1,200 existing tests now name `?cell=white` and pass | Pass |
| 3 | New test file, tagged, failing-first recorded | File exists, module `pytestmark verifies(FR-4310, FR-4320)` plus per-test markers. **Failing-first reproduced independently:** worktree at `a64c438` with `server.py` replaced by `a64c438^`'s; the new file ran 72 tests, **37 failed**, 35 passed (the accepted-for-white and 404 cases). Matches the claim of 37. | Pass |
| 4 | No existing assertion changed | `git diff a64c438^ a64c438` over the 8 modified test files: 64 removed / 64 added lines; scripted pairwise check: every added line equals the removed line plus only `cell=white` (query param, `"cell":"white"` or equivalent); 0 exceptions | Pass |
| 5 | Full suite green; gates by name | Below | Pass |
| 6 | RTM, CLAUDE.md, manuals | RTM FR-4310/FR-4320 name `IP-1068` and the new test file (generated Test column); CLAUDE.md LAN-trust paragraph has the sentence; no manual section found contradicting (grep of `docs/training/12–15` for the behavior) | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| 12 guarded routes: non-White -> 403, state holds | 5 clock + 6 config parametrized over blue/red/observer/none, plus `load_save`; all green | Pass |
| `roles/assign`, `observer/view` refusals tested | `test_seat_assignment_and_observer_designation_refused_for_player_seats[blue/red]` | Pass |
| Existing-test diff only adds `cell=white` | See DoD 4 | Pass |
| `server.py` diff scope | Diff = `_require_white` helper, 11 `_reject_observer`->`_require_white` swaps, `load_save` `cell` param + guard. Nothing else. | Pass |
| Full suite + gates | Below | Pass |
| Every new test has `verifies` naming FR-4310/FR-4320 | Module `pytestmark` + per-test markers; IDs live | Pass |
| RTM rows name `IP-1068` + test file | Confirmed (rows 236–237); Impl. Package cell updated by this run to VERIFIED | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM | Result |
|---|---|---|---|---|
| FR-4310 | `_require_white` on clock/step/advance/rewind/undo | `test_clock_controls_refused_for_non_white`, `…accepted_for_white` | Test cell lists new file; Impl. Package cell set to VERIFIED | Pass |
| FR-4320 | `_require_white` on start/param/inject/force-add/bulk/load_save; engine-side refusal for roles/assign and observer/view | `test_config_controls_*`, load_save, seat/observer, 404-before-403 | same | Pass |

## Test run

- `python3 -m pytest --tb=short --junitxml=…` (full suite): exit 0, **1280 passed, 3 skipped**; junit: 1283 tests, 0 failures, 0 errors, 3 skipped. (Browser-marked tests skip where Chromium is absent; no browser downloaded.)
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py`: all green.
- `python3 -m pytest spacesim/tests/test_white_only_controls.py`: 72 passed.
- Failing-first: 37 failed of 72 against pre-fix `server.py` (above).

## Scope audit

Implementing commit `a64c438` touched 15 files, all within `Files to Create/Modify` (server.py, new test file, the 8 calling-convention test modules, RTM, CLAUDE.md) plus ROADMAP, master build plan and packages index (status bookkeeping). No out-of-scope file.

## Live route-table re-derivation (mutating routes in `server.py`)

Guarded by `_require_white`: the 12 above. Inline `cell != "white"` guard: `injects/{handle}/cancel`, `injects/{handle}/edit` (IP-1066). Engine-side White check: `roe/change` (`OrderSystem.issue_roe_change` returns `not_controller`), `roles/assign`, `observer/view`, `gate/decide` (role-gated). Still guarded **only** by `_reject_observer` (a Blue/Red seat is accepted) or unguarded: `POST /api/sessions` (load vignette), `POST /api/sessions/draft`, `PUT creator/state`, `PATCH/DELETE creator/asset/{id}`, `POST creator/seats`, `POST save_vignette` (writes a vignette file), `POST red_step` (triggers the Red doctrine AI for the whole session), and the order routes (legitimately player-facing).

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | `POST …/red_step` advances the Red AI (a facilitation control) and is accepted from Blue/Red seats; likewise the Vignette Creator authoring routes and `save_vignette` (writes to the user save dir) and session creation accept any non-observer seat. None is in FR-4320's enumerated list or the package's Objective table, so IP-1068 is complete as specified, but "every White Cell control" is not literally true of the server. | Medium | `04-requirements-engineering` (decide whether FR-4320's list should include red_step / creator / save_vignette / session creation), then a new `07` remediation package |
| F2 | FR-4310 Notes in `docs/requirements/01-functional-requirements.md` still read "Not met as built" (`IP-1068` completion note says the RTM note text is `04`'s). Stale now that the leaf is met. | Low | `04-requirements-engineering` |
| F3 | RTM FR-4310 title cell and several stale "not met as built" mentions elsewhere (GDS-09 §4 / OQ1) not re-checked here; cross-doc coherence belongs to `10`. | Low | `10-integration-review` |
| F4 | The package's "Tests to Add" says a hand-written completion note records failing-first; the number (37) is not in the package file, only in the task brief. Reproduced independently so no action beyond noting. | Low | `08-code-implementation` (process) |

## Independence

Fresh session; no implementation work by this session. Authorization: owner authorized all nine planned packages 2026-10-23 (as supplied by the pipeline manager); the package file's own "not yet authorized" banner is stale and is not a finding.
