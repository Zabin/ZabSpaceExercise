# VR-1334 — Verification Report: Test-Origin Retag (NFR-2820, NFR-2850)

> **Document ID:** VR-1334
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1334](../packages/IP-1334-test-origin-retag.md) v1.0,
> [FS-133](../../features/FS-133-test-origin-traceability.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1334` (closes `BL-0341`, `BL-0344`, `BL-0347`)
> **Feature Mapping:** FS-133

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1334 — Test-Origin Retag (v1.0, test-only)
- **Implementing commits:** `cd77d85` (first pass, merged at `a7b2b77`), `d08f514` (tags for the IP-1103/1074/1335/1075 tests); tree verified at `703513b` on `claude/test-tag-review-1`.
- **Independence:** fresh session; did not write or review these tags.

## Result

**✅ VERIFIED** — 0 failed checks. 1 Low finding (weak tags, 11% of the judged sample, 0 wrong), 1 Info.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Guard exists, was seen failing first, passes | `test_origin_retag.py`: 171 pinned `(module, function)` rows + no-lost-ID + count bound = 173 items; whole-suite run passes. Mutation: `test_bus_commands.py:686` `FR-1310`→`FS-105` makes `test_each_listed_retag_is_in_place[test_bus_commands.py::test_prop_station_keep_consumes_delta_v]` fail; restored (`git status` clean). "Failing first" is the implementer's claim; the mutation shows the guard discriminates | pass |
| Every table retag applied or declined with reason | Completion note lists declined/left-on-nearest cases (bus/defence verbs → `FS-105`, etc.); retags checked by the guard rows | pass |
| RTM regenerated; `test_test_origins.py` passes | `--origin-report=rtm` twice: "regenerated (unchanged)", `git status` clean; `test_test_origins.py` 21 passed, 1 skipped | pass |
| Collected count unchanged; suite and gates green | `--collect-only` per-file sum: `claude/ip-1075-build` 1464, tip 1637 = 1464 + 173 guard items; not-browser run green; determinism and import guard green | pass |
| Only tests, RTM, plan docs changed; no production diff | `git diff --name-status claude/ip-1075-build HEAD -- spacesim` lists only `spacesim/tests/` (one `A`: `test_origin_retag.py`); other files are docs/RTM/pipeline merge content | pass |
| Docs done; status COMPLETE | MBP row, packages index, ROADMAP row, tally lines present | pass |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Touched modules change only `verifies(...)` arguments | Script (`ast_cmp`): for each of 36 changed test modules vs `claude/ip-1075-build`, parse old and new, strip `verifies` decorators, `verifies` entries in `pytestmark` (assignment dropped if it empties) and `import pytest` lines, compare `ast.dump`. **Identical for all 36.** Same at the earlier base (`claude/ip-1073-build` vs `a7b2b77`, 35 modules): identical. A line-level pass found no changed line outside `verifies`/`pytestmark`/`import pytest`/ID continuation lines. No module differs | pass |
| 2 | Nothing outside tests, RTM, plan docs | See DoD; the only non-doc file added is `test_origin_retag.py`; `git show --stat d08f514` non-test files: MBP, package, RTM, ledger docs | pass |
| 3 | Spot-check retags against leaf text | 97 judged (below); 0 WRONG | pass |
| 4 | `--origin-report=rtm` produces no further change | Run twice at tip: unchanged; Test column equals tool output (`test_test_origins.py`) | pass |
| 5 | Collected count equals pre-change | 1464 → 1637, delta exactly the 173 guard items | pass |
| 6 | Full suite and gates green | Below | pass |

## Requirements audit

| ID | Implemented / tested | RTM | Result |
|---|---|---|---|
| `NFR-2820` | Every test declares a live ID: `--origin-report` ends "untagged tests: 0"; `test_test_origins.py` resolves every declared ID | Test column regenerated | pass |
| `NFR-2850` | Column generated, idempotent (two runs unchanged) | matches tool | pass |

## Test run

- `python3 -m pytest -m "not browser" --junitxml`: exit 0, 1614 tests, 0 failures, 0 errors, 6 skipped.
- `python3 -m pytest -m browser --junitxml`: exit 0, 23 tests, 0 skipped (ran).
- By name: `test_determinism.py` 6 pass; `test_import_guard.py` 8 pass; `test_test_origins.py` 21 pass, 1 skip; `test_doc_integrity.py` 9 pass; `test_origin_retag.py` whole suite pass.
- `test_origin_retag.py` alone: 27 skipped, 1 passed (rows skip with "not collected in this run"; the count test skips "partial run") — benign.
- Tests with no origin: 0.

## Judgement of tags (independent)

Population: 153 test functions whose effective ID set (own plus module-level mark) differs from `claude/ip-1075-build`. Judged **all 35 tests in the four modules where a module-level `pytestmark` was removed** (`test_self_contained_save.py`, `test_save_load_robustness.py`, `test_white_control_correctness.py`, `test_white_only_controls.py`) plus a seeded random sample of 62 others: **97 judged** against the leaf text in `docs/requirements/`.

| Outcome | Count |
|---|---|
| AGREE | 86 |
| WEAK | 11 |
| WRONG | 0 |

Disagreement rate with the retagger: 11/97 = 11% WEAK, 0% WRONG. WEAK items (a defensible leaf exists; the chosen one is loose or a better one was removed):

- `test_self_contained_save.py::test_invalid_content_portion_refused_with_problems_and_no_session`, `::test_invalid_baseline_refused_and_no_session` (`FR-7230`+`NFR-1800`; refusal of a bad save is `NFR-1600`/`FR-7230` input validation, which `FR-7230`'s AC does not state), `::test_simulator_version_mismatch_resumes_with_warning_naming_both` (`FR-7230` covers changed vignette files, not version warnings).
- `test_white_control_correctness.py::test_the_span_edges_are_allowed`, `::test_a_rewind_leaves_the_running_state_and_reanchors`, `::test_clock_state_exposes_start_epoch` (`FR-4310` is White-only restriction; these test rewind bounds/clock state, closer to `NFR-1600`/`FR-1110`).
- `test_telemetry.py::test_series_pre_onset_matches_replay`, `::test_series_cleared_episode_stays_in_history` (`FR-2330` attack signature; `FR-2320` history fit better).
- `test_web.py::test_scene_returns_assets` (`FR-8110` generic), `test_ssn.py::test_harden_reduces_safe_mode_probability` (`FR-1420`: hardening is not the cyber window exception), `test_vignette_creator_session.py::test_draft_session_evicted_by_existing_max_live_sessions_cap` (`NFR-3710` is bounded work on untrusted input; a session cap is loosely related).

No tag names a leaf that contradicts the test; every WEAK is a loose fit that still resolves and is not misleading. Bus/defence verb tests on `FS-105` are the declared no-leaf set (`FR-2410` is payload-type-specific); accepted.

## Scope audit

Test modules (tag lines only), `test_origin_retag.py`, RTM Test column, plan/ledger docs. No `spacesim/` non-test file changed.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F-1 | 11 of 97 judged tags are WEAK (listed above); a better leaf exists or the neighbour was dropped. None wrong, none blocks. | Low | `04`/next retag pass, optional |
| F-2 | The package text says 170 retagged and the guard pins 171 rows; the tree's effective changed set vs the pre-retag stack is 153 functions. Counts differ by baseline (first-pass base vs the stack). | Info | none |
