# VR-1335 — Verification Report: Test-Origin ID Widening (NFR-2820, NFR-2850, FR-5310)

> **Document ID:** VR-1335
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1335](../packages/IP-1335-test-origin-id-widening.md) v1.0,
> [FS-133](../../features/FS-133-test-origin-traceability.md), [FS-131](../../features/FS-131-load-time-vignette-validation.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1335` (closes `BL-0368`, `BL-0361`)
> **Feature Mapping:** FS-133, FS-131

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1335 — Test-Origin ID Widening (v1.0)
- **Implementing commit:** `ff4b0b2` (branch `claude/ip-1335-build`); tree verified at that commit.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 2 Low findings (documentation wording), none blocking.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Guard test exists, seen failing first for Parts A and B, passes; Part C test fails under the mutation | Parent `baseline_ids.py` copied in (scratch, restored after): `test_five_digit_ids_are_well_formed_and_resolve`, `test_baseline_reads_five_digit_headings`, `test_matrix_generation_places_a_five_digit_row` fail; current tree 9 pass. Dropping the `isinstance(raw, dict)` check in `_declared_vignette_id` (`content/vignette.py:261`) fails `test_top_level_list_or_scalar_file_skipped_in_both_roots` with `AttributeError: 'list' object has no attribute 'get'`; restored | pass |
| `baseline_ids.py` accepts four- and five-digit FR IDs in all three places via one shared pattern; malformed forms rejected | `FR_ID = r"FR-\d{4,5}"` used by `WELL_FORMED`, `load_baseline()`, `regenerate_matrix()`; boundary test rejects `FR-123456`, `FR-12`, `FR-1011`, `NFR-10110` | pass |
| 20 tests carry `FR-10110`/`FR-10210`; RTM regenerated; `test_test_origins.py` green | 13 + 7 retags (below); `--origin-report=rtm` on the tree changes nothing; `test_test_origins.py` 21 passed, 1 skipped | pass |
| Full suite and both gates green; no production diff | See Test run; `git diff HEAD~1 HEAD --stat` touches only `spacesim/tests/` plus docs | pass |
| Documentation updates; status `COMPLETE` | MBP row and tally, packages index, ROADMAP row, package header, RTM Impl cells | pass |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Diff of `test_assessment.py`, `test_research_batch.py` changes only `verifies(...)` arguments | Line level: every changed line contains `verifies(`; 13 `FS-201`→`FR-10110`, 7 `FS-301`→`FR-10210`. AST level: both files parsed before and after with `verifies` call arguments emptied, `ast.dump` equal for both | pass |
| 2 | No `\d{4}` applied to an FR pattern outside the shared definition | `grep 'd{4}' baseline_ids.py`: remaining hits are the NFR (line 60) and IP (line 63) readers and the NFR/FS/IP alternatives in the shared patterns | pass |
| 3 | Spot-check retags against `FR-10110`/`FR-10210` text | All 20 judged (below), not three | pass |
| 4 | `--origin-report=rtm` produces no further change; matrix diff touches only `FR-10110`/`FR-10210` Test cells | No further change (`git status` clean after the run). The committed diff touches six rows, not two: `FR-10110`, `FR-10210` plus `FR-5310`, `NFR-1600` (the new scan test's tags) and `NFR-2820`, `NFR-2850` (the new guard module's tags). Each is a generated Test cell from a test this package added | pass (F-1) |
| 5 | `--origin-report` lists the seven `FR-11xxx` leaves as unnamed, nothing fails | `FR-11110`, `11120`, `11210`, `11310`, `11320`, `11410`, `11420` listed; no check failed | pass |
| 6 | Mutation on the scan | See DoD row 1 | pass |
| 7 | Full suite, both gates, doc integrity, origin tests | See Test run | pass |

### The 20 retags against the leaves

`FR-10110` requires per-dimension rubric tiers for custody quality, window discipline, belief-truth divergence, derived read-only, never aggregated. The 13 tests: three custody-quality, three window-discipline and four belief-truth tier tests (each a tier outcome of one named dimension); `test_scoring_functions_never_mutate_world_state` (the "derived read-only" clause); `test_assessment_report_presents_dimensions_side_by_side_never_a_composite` (the "never aggregate" clause); `test_belief_truth_divergence_reads_recorded_confidence_not_replay_recomputed` (derivation from recorded state). All fit; none is a pure helper.

`FR-10210` requires batch execution of N seeded runs exporting vignette id, seed, condition label and the `FR-10110` results, with determinism preserved. The 7 tests: record-per-seed metadata, byte-identical repeat runs, per-seed deterministic outcome, no reimplementation of the `FR-10110` scoring, fresh manager per seed, CSV export, JSON round trip. All fit.

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| `NFR-2820` | `baseline_ids.py` shared `FR_ID` | `test_origin_id_widening.py` (module marker `NFR-2820`, `NFR-2850`); `test_test_origins.py` | Test cell regenerated; Impl cell gained the `IP-1335` note | pass |
| `NFR-2850` | `regenerate_matrix()` uses `FR_ID` | `test_matrix_generation_places_a_five_digit_row`; committed-equals-generated check | same | pass |
| `FR-5310` | existing behaviour, no code change | `test_top_level_list_or_scalar_file_skipped_in_both_roots` | Test and Impl cells carry the new test | pass |

## Test run

Run in the worktree at `ff4b0b2`.

- `python3 -m pytest -m "not browser"` — 1415 passed, 4 skipped, 22 deselected.
- `python3 -m pytest -m browser` — 22 passed.
- By name: `test_determinism.py` 6 passed; `test_import_guard.py` 8 passed; `test_doc_integrity.py` 9 passed; `test_test_origins.py` 21 passed, 1 skipped (partial-collection skip when run alone); `test_origin_id_widening.py` 9 passed; `test_vignette_id_scan.py` 7 passed.
- Guard mutations (scratch edit, restored): reverting `FR_ID` to four digits in `WELL_FORMED` fails `test_five_digit_ids_are_well_formed_and_resolve` and `test_the_live_baseline_resolves_one_of_each_kind`; in `load_baseline()` fails three guard tests; in `regenerate_matrix()` fails `test_matrix_generation_places_a_five_digit_row`. Each of the three uses is covered.
- Scratch test declaring `FR-10110` and `FR-11420` is accepted (listed under both in `--origin-report`); one declaring `FR-99999` makes `test_every_declared_id_in_the_real_suite_resolves` fail with `…test_bad: origin 'FR-99999' — not in the baseline ledger…`. Scratch file removed.
- The new guard module has 9 cases (1+4+1+1+2) and Part C adds 1.

## Scope audit

Diff `ff4b0b2`: `baseline_ids.py`, `test_assessment.py`, `test_research_batch.py`, `test_vignette_id_scan.py`, new `test_origin_id_widening.py`, the RTM, the package header, MBP, packages index, ROADMAP. All inside `Files to Create`/`Files to Modify` plus the named documentation. No file under `spacesim/` outside `spacesim/tests/` changed. The `IP-1334` Dependencies sentence was a planning-pass edit and is not part of this diff.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F-1 | Checklist item 4 says the matrix diff touches only `FR-10110`/`FR-10210`; the correct diff also touches `FR-5310`, `NFR-1600`, `NFR-2820`, `NFR-2850` because this package's own new tests carry those tags. The behaviour is right and generated; the checklist wording is imprecise | Low | `07-implementation-planning` (wording only; no action needed) |
| F-2 | The retag guard `_declared` helper reads decorators with `ast.Constant` args only and takes an unused second parameter; harmless, but a future `verifies(*IDS)` form would be silently read as empty (the leaf assertion would then fail loudly, so it is safe) | Low | none |
