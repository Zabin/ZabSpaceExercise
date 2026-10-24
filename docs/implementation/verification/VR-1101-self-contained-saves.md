# VR-1101 — Verification Report: Self-Contained Saves (FR-7210, FR-7220, FR-7230, NFR-1800)

> **Document ID:** VR-1101
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1101](../packages/IP-1101-self-contained-saves.md) v1.0,
> [FS-110](../../features/FS-110-save-and-resume.md) v2.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1101`
> **Feature Mapping:** FS-110 (`FEAT-7200`)

[↑ Verification index](INDEX.md) · [Docs index](../../INDEX.md)

## Package

IP-1101 v1.0, implementing commit `7964d6a`; tree verified at `b0607a5` (branch `claude/verify-ip-1101`,
from `claude/verify-ip-1068`). Independent fresh session (no part in implementation).

## Result

**VERIFIED** — 0 failed checks. Five findings (one Medium, four Low) are routed onward; none is a DoD
or checklist failure.

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | New save resumes identically if the vignette file is unchanged, edited, renamed or deleted | `from_state` new-format branch builds `cls(Vignette.model_validate(state["content"]))` and installs `state["baseline"]` (`manager.py` ~1031); no `load_vignette` call. Tests `test_immediate_round_trip_every_shipped_vignette` (19), `…_edited`, `…_deleted_or_renamed[delete/rename]` pass. My own run (below): file deleted, resume via the HTTP route, assets and godview equal | Pass |
| 2 | Force-added assets survive | `test_force_added_assets_survive[before-start / after-start-and-advance]`; own run with force-added TLE + ground asset, started and stepped 900 s: both present after resume | Pass |
| 3 | Content portion extracts, validates, starts a session, parameters as loaded | `test_content_portion_extracts_and_loads_as_a_fresh_vignette` (validate_vignette == [], starts, contains both force-added assets, `parameters` equal the original); fidelity test passes for all 19 shipped vignettes | Pass |
| 4 | Legacy saves resume with a warning; version mismatch warns | Tests pass; own run: mismatch -> `["this save was written by simulator version 0.0.1-old; this is b0607a5"]`; legacy path resumes by id with a "legacy save: it depended on the vignette file" warning (see F1 for the missing-file case) | Pass |
| 5 | Invalid content portion refused before replay, no session | `validate_save` runs before `from_state` and before `_evict_if_full`/counter; tests assert session list empty; own run via route: 400 `save content portion refused: blue_forces[BROKEN].orbit: a satellite must declare an orbit` | Pass |
| 6 | Tests exist, tagged, failing-first recorded; no existing assertion changed | 50 tests in `test_self_contained_save.py`; commit diff touches no existing test file. Failing-first reproduced independently: **30 of 50 failed** against `7964d6a^` (the claim was 31; see F3) | Pass |
| 7 | Full suite + both gates; docs updated | Below. `CLAUDE.md` code map has the IP-1101 entry; WCM-10 updated with Sources footer; RTM rows updated | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Each Tests-to-Add row exists and passes; edit/delete/rename tests use a temporary directory | All ten rows present. Read the file: `_copy_vignette` copies `01-leo-isr-denial.yaml` under a new id into `tmp_path/ext`, points `SPACESIM_CONFIG` at a temp cfg via `monkeypatch.setenv`; edit/unlink/rename act only on that copy. No shipped file touched (git status clean after the run) | Pass |
| Reverting `from_state` to reload by id fails the FR-7230 tests | Mutated `if state.get("save_format"):` to `if False:` in a throwaway edit (restored byte-identical; `git status` clean): 6 tests failed — `…file_is_edited`, `…deleted_or_renamed[delete]`, `[rename]`, `test_force_added_assets_survive` (both) and the version-mismatch test | Pass |
| `save_state` keeps every pre-existing key | Code adds four keys before the old literal; all ten old keys present. Own save lists all of them plus `save_format, simulator_version, content, baseline`; `test_save_keeps_every_pre_existing_key` | Pass |
| `git diff` touches only listed files | See Scope audit | Pass |
| Full suite counts; gates by name | Below | Pass |
| Every new test carries `verifies` with the IDs shown | Module `pytestmark` (FR-7210, FR-7230) plus per-test markers matching the table; origin-report lists FR-7220 and NFR-1800 on the expected tests. Module mark over-applies (F4) | Pass (Low note) |

## Requirements audit

| ID | Implemented | Tested | RTM | Result |
|---|---|---|---|---|
| FR-7210 | `save_state` baseline + `from_state` | round trip, force-add, legacy | Test cell generated; Impl. Package cell set to VERIFIED by this run | Pass |
| FR-7220 | `save_state` content portion (vignette as loaded + force-added assets) | extraction + fidelity (19 vignettes) | Impl. cell set; the "not met as built" note is `04`'s to retire (F5) | Pass |
| FR-7230 | `from_state` new branch; no file read | edit/delete/rename, immediate resume | Impl. cell set | Pass |
| NFR-1800 | fresh-`InProcessSession` resume, validation before replay | `test_resume_in_a_fresh_inprocess_session`, two refusal tests | Impl. cell set | Pass |

## Route, seat guard and console

- `POST /api/sessions/load_save`: no `cell` -> 403, `cell=blue` -> 403 (IP-1068 `_require_white` runs first, before any
  validation or session creation); `cell=white` -> 200 `{"session", "warnings"}`. `ValueError` from validation or the existing
  event-log bound now maps to 400 with the reason. Interaction with IP-1068 is correct; the merged route is coherent.
- `app.js` `loadSaveFile`: `api.post` attaches the caller's seat (`cell=`), so White works; warnings are shown with `alert(...)`
  after `SID` is set. Not exercised headless (browser tests skipped, no browser downloaded) — display verified by reading only (F2).
  `loadSaveFile` has no error handling: a 400 refusal (or the 403 for a non-White seat) is an unhandled promise rejection after
  `stopRealtimeClock()` has already run, so the user sees nothing and the old session's clock is stopped (F2).

## Own exercise (fresh scenario)

Copy of the satcom vignette under id `ex-fresh` in a temporary external content dir; created via the API, force-added a TLE
(blue) and a ground asset (red), started, stepped 900 s, saved (18.6 KB), JSON round trip, **deleted the yaml**, loaded with
`cell=white`: 200, no warnings, both force-added assets present, god-view equal to the pre-save god-view in every field except
`now` (microsecond wall-clock catch-up on a running lazy clock — expected). Legacy-stripped save with the file deleted: 500
(F1). Version mismatch: warning names both versions. Invalid content: 400 with the problem listed.

## Test run

- `python3 -m pytest --tb=short --junitxml=…` (full suite): exit 0; junit 1283 tests, 0 failures, 0 errors, 3 skipped (1280 passed).
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py`: exit 0, 14 tests, all green.
- `python3 -m pytest spacesim/tests/test_self_contained_save.py`: 50 passed.
- `python3 -m pytest --origin-report=rtm`: "Test column regenerated (unchanged)".
- Failing-first: worktree at `7964d6a^` with the new test file copied in: 30 failed, 20 passed.

## Scope audit

Implementing commit `7964d6a` touched 12 files: `session/manager.py`, `session/inprocess.py`, `ui_web/server.py`,
`ui_web/static/app.js`, the new test file, `CLAUDE.md`, RTM, `docs/training/12-white-cell-manual.md`, plus the
status bookkeeping (`ROADMAP.md`, master build plan, packages index, pipeline journal). No existing test file was modified.
All within the declared set. Save size: ~16–19 KB for a small vignette.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | A legacy save whose vignette file is missing makes `POST load_save` return 500 (`FileNotFoundError` from `load_vignette` is not mapped). The behavior matches the pre-package code, but the new warning text promises legacy handling and the route now maps `ValueError` to 400 for everything else. A clear 400 ("legacy save needs vignette file X") would fit FR-7230's intent. | Medium | `07-implementation-planning` remediation package, then `08` (via `00-intake`) |
| F2 | `loadSaveFile` has no error handling (refusal 400 / 403 produce no visible message, clock already stopped) and the new `alert` warning display is untested (no headless coverage). | Low | `07`/`08` (UI), `09`-visible via browser tests |
| F3 | Failing-first count claimed as 31 in the journal; independently reproduced 30 of 50. Immaterial to the result; process-accuracy note. | Low | `08-code-implementation` (process) |
| F4 | The module-level `pytestmark` tags every test with `FR-7210` and `FR-7230`, over-claiming (e.g. the refusal tests claim FR-7210). Per-test tags are accurate. | Low | `08-code-implementation` |
| F5 | `FR-7220`'s RTM "not met as built" note and GDS-07 §6 are stale now that the leaf is met; `04`/`03` follow-ups named by the package. | Low | `04-requirements-engineering`, `03` |

## Independence

Fresh session; no implementation work by this session. Authorization: the owner authorized all nine planned packages
2026-10-23; the package file's own "not yet authorized" banner is stale and is not a finding.
