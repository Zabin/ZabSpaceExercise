# VR-1079 — Verification Report: Retag Guard Redesign (test-only; tranche 3 review L-5)

> **Document ID:** VR-1079
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1079](../packages/IP-1079-origin-retag-guard-redesign.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1079` (closes tranche 3 review `L-5`)
> **Feature Mapping:** FS-133 `NFR-2820`

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1079 — Retag Guard Redesign (v1.0)
- **Implementing commit:** `8911647` (branch `claude/ip-1079-build`); parent `66eda6d`.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 2 Low findings and 2 Info findings, none blocking.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Count constants and count test gone; `EXPECTED` byte-identical | `COLLECTED_BEFORE`, `COLLECTED_UPPER`, `_whole_suite`, `test_collected_count_unchanged_by_the_retag` absent from the tree outside the package/ledger prose (grep). `diff` of the `EXPECTED = [ … ]` block at `HEAD~1` vs `HEAD`: identical (171 rows). A new in-suite test pins the absence | pass |
| Mutation that deletes, renames or retags any one pinned test fails; module deletion fails; adding unpinned tests passes | By-hand mutation on a scratch copy of the tree (below): (a) delete, (b) rename, (c) retag, (d) delete module all fail naming the row; (e) 50 added tests pass | pass |
| No check skips under both `-m browser` and `-m "not browser"`; unfiltered run skips none from the module | `-rs` under each of the three modes: 0 skips from `test_origin_retag.py` in every mode; no `pytest.skip`/`skipif` call remains in the module (AST test) | pass |
| Full suite green; gates unaffected; RTM regenerated; no allow-list grew | See Test run; `--origin-report=rtm` re-run leaves the tree clean (idempotent); `git diff --stat` shows no `*allow*` file | pass |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | `EXPECTED` unchanged, three count symbols removed | As above | pass |
| 2 | Mutation by hand on a tree copy | Scratch copy of the tree; guard run over `test_origin_retag.py` plus the mutated module (the guard sees only collected modules). Baseline: 196 passed. (a) delete `test_worlds_at_times_matches_state_at_time` in `test_aar.py`: rc 1, `test_each_listed_retag_is_in_place[test_aar.py::test_worlds_at_times_matches_state_at_time]` FAILED ("no longer exists"). (b) rename it: rc 1, same row FAILED. (c) change its tag set `("FR-7310","NFR-2410")` → `("FR-7310",)`: rc 1, same row FAILED ("declares … expected …"). (d) delete `test_aar.py`: both `test_aar.py` rows FAILED, message `module removed or renamed` (the guard's synthetic self-tests, which read the on-disk module set, also fail, as expected). (e) add 50 unpinned tests to `test_aar.py` and 50 in a new module: rc 0, 296 passed. Each file restored after its mutation; baseline green again (196 passed) | pass |
| 3 | Guard under the three invocations, skip counts read | `-rs`: unfiltered 186 passed, 0 skipped; `-m browser` 1 passed (the browser-marked row test), 185 deselected, 0 skipped; `-m "not browser"` 185 passed, 0 skipped. The in-suite `test_no_double_skip_across_the_three_ways_the_suite_is_run` asserts this from three child processes (junit) and passes | pass |
| 4 | Five throwaway unpinned tests keep the guard green | Done with 50 (item 2 (e)) | pass |
| 5 | `test_doc_integrity.py`, `test_test_origins.py`, full suite, determinism, import guard, browser | See Test run | pass |
| 6 | Doc edits limited to living statements; no VR edited | Diff touches `ROADMAP.md`, `00-master-build-plan.md`, `01-technical-work-breakdown.md` (one forward pointer on the `L-5` bullet), `packages/INDEX.md`, RTM Test column (2 lines). No VR, review or `docs/pipeline/` file. Grep for the ceiling phrases in living docs finds only planning/historical statements (see F1) | pass |

Browser row actually checked: with `test_browser_console_rules.py` collected and its pinned function renamed in the scratch copy, `-m browser` fails `test_each_listed_browser_retag_is_in_place[…]` (31 collected, 1 failed). Run unmutated, `-m browser` gives 31 passed, 0 skipped.

## Requirements audit

| ID | Implemented | Tested | RTM | Result |
|---|---|---|---|---|
| `NFR-2820` | module `pytestmark` retained; per-row checks in `check_rows` | `test_each_listed_retag_is_in_place`, `…_browser_retag_…`, `test_no_retagged_test_lost_its_last_id…` | Test column regenerated; second regeneration leaves `git status` clean | pass |
| `FS-133` | pure helper, mutation tests | `test_mutation_*`, `test_a_consistent_record_set…` marked `verifies("FS-133")` | n/a (not a requirement leaf) | pass |
| `IP-1079` | no-skip and growth proofs | `test_growth_in_unpinned_tests…`, `test_no_double_skip…`, `test_no_check_in_the_guard_calls_skip…`, `test_the_count_bounds…`, `test_browser_rows_are_exactly…` marked `verifies("IP-1079")` | n/a | pass |

Every added test carries a `verifies` mark naming a live baseline item (`test_test_origins.py` green).

## Test run

- `python3 -m pytest --junitxml` (unfiltered, run alone): exit 0, **1681 passed, 3 skipped, 0 failures**.
- `python3 -m pytest -m "not browser" --junitxml`: exit 0, 1653 tests, 0 failures, 4 skipped (the 3 above plus `test_test_origins.py::test_the_committed_matrix_test_column_equals_the_generated_one`, a pre-existing partial-collection skip outside the guard module).
- `python3 -m pytest -m browser --junitxml`: exit 0, 31 passed, 0 skipped.
- `test_origin_retag.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_determinism.py`, `test_import_guard.py` together: exit 0, 229 passed (+1 partial-collection skip under `-m "not browser"`).
- `python3 -m pytest --origin-report=rtm` twice: no diff.
- Note: a first unfiltered run launched concurrently with the two filtered runs ended with an incomplete progress line yet exit 0 and 1671 junit cases; it was discarded as a concurrency artifact and the run above (alone) is the evidence (F3).

## Scope audit

Files changed: `spacesim/tests/test_origin_retag.py` only under `spacesim/`; docs: ROADMAP, MBP, TWB, `packages/INDEX.md`, RTM. Within Files to Modify and Documentation Updates. `baseline_ids.py` and `conftest.py` untouched. No production code.

## Ledger tally (counted independently from the MBP table, 83 rows)

Before this report: 79 `VERIFIED`, 1 `COMPLETE` (`IP-1079`), 2 `READY` (`IP-1080`, `IP-1081`), 1 `BLOCKED` (`IP-1160`) — matches the stated tally. After: 80 `VERIFIED`, 0 `COMPLETE`, 2 `READY`, 1 `BLOCKED` — 83.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 | `01-technical-work-breakdown.md` pass 5 ordering sentence ("the `IP-1334` ceiling of 1700 …") still describes the removed ceiling; it is planning prose of the time, not a living claim about the guard. | Low | `07-implementation-planning` (optional) |
| F2 | The package's `Status` header still reads `READY`; header reconciliation is covered by `IP-1080`'s class of work, and the skill forbids editing the package. | Low | `IP-1080` / `07` |
| F3 | Three suite runs launched in parallel in one tree produced one truncated-looking run; not reproducible alone. Run the modes sequentially. | Info | none |
| F4 | The completion-note answer to task 2 (what `config._verifies_records` holds under `-m`) is not in the tree. Verifier confirmed: `conftest.py` builds records in a `trylast` `pytest_collection_modifyitems`, so deselected items are absent, which is the premise `check_rows` relies on. Also, under `-m "not browser"` a pre-existing skip in `test_test_origins.py` remains (outside this package's scope). | Info | none |
