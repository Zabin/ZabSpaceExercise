# VR-1350 — Verification Report: Documentation Integrity Checks (NFR-3800, NFR-3820, NFR-3830)

> **Document ID:** VR-1350
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1350](../packages/IP-1350-documentation-integrity-checks.md) v1.0,
> [FS-135](../../features/FS-135-documentation-integrity-checks.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1350`
> **Feature Mapping:** FS-135 (`FEAT-12300`)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1350 — Documentation Integrity Checks: Links, Indexes, Ledgers (v1.0)
- **Implementing commit:** `18a9c89`; tree verified at `92ba158` (branch `claude/ip-1069-rerun`; no later commit touches the package's files).
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 1 Medium and 4 Low findings (none blocks the transition).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Three checks in the full suite; pass with the committed allow-lists | `test_doc_integrity.py` read in full: `test_real_tree_*` x3 (links, indexes, ledgers); full suite exit 0, file 9 passed | Pass |
| 2 | Allow-lists hold exactly today's defects, each with an owning stage; shrink-only enforced | Independent measurement (below): 82 occurrences / 62 distinct pairs, 3 unlisted, 2 ledger disagreements = list contents; every line has a ` \| owner`; `_gate` fails on stale lines (demonstrated) | Pass (see F-2: the lists hold distinct pairs, not occurrences) |
| 3 | Synthetic tests prove each check fails on a seeded defect | Six synthetic tests present; mutation runs below show links/fence/span/sub-index-listing/ledger are pinned, two gaps (F-3) | Pass |
| 4 | Every test tagged; failing-first run recorded | All 9 tests carry `verifies(...)` naming `NFR-3800/3820/3830` (all live; `--origin-report` lists them, "requirements no test names" empty). Failing-first: **not recorded** — journal run #235 states checks and tests were written together, "no separate failing-first run"; the real-tree checks do fail with empty allow-lists (not run by this verifier) | Pass with finding F-1 |
| 5 | Full suite and both gates green; docs updated | See Test run; `CLAUDE.md` Test-driven workflow sentence present; RTM rows carry the tests | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Adding a broken link to a live document fails the suite naming it | Appended `[x](nope-seed.md)` to `docs/FUTURE-WORK.md`: failure `docs/FUTURE-WORK.md -> nope-seed.md`; restored (`git checkout`) | Pass |
| Allow-list counts match the Objective's measurements | Own script (`scratchpad/measure.py`, a line-based walker independent of the package's code): 369 live / 136 frozen files; 83 broken occurrences in 11 files; the extra is `docs/features/FS-115-session-setup.md:99`, a link destination hard-wrapped across a line, which is not a link under CommonMark and which the package's regex also ignores, so **82 in 10 files** (`ROADMAP.md` 24; primers 01–07 and 10: 15+13+10+6+6+4+2+1 = 57; R101 1) = Objective. Distinct (file, target) pairs 62 = the 62 allow-list lines. Own index script: 14 live `INDEX.md`, 3 unlisted (`docs/INDEX.md` x2 AUDIT files; `docs/architecture/INDEX.md` strategic-assumptions-register) = list. Own ledger check: Master Build Plan vs packages index agree on all 69 packages; `FS-106` and `FS-110` differ (feature-index "Done … ; later Ready", spec header "Ready … ; v1 Done") = list; the Objective's expected 0 was 2, disclosed in journal #235 | Pass |
| Frozen-history paths excluded exactly as Decision 1 lists | `FROZEN_PREFIXES` = verification/, reviews/, adr/, both archives; journal split at `## Run log`; my walker found 136 frozen files (63 + 31 + 40 + 2) and `.claude/` files are live as Decision 1 states; synthetic test covers a frozen file and the journal run log | Pass |
| Both gates green by name; full suite counts recorded | See Test run | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| NFR-3800 | `broken_links()` | real-tree gate; synthetic link test; shrink-only test | Test column lists the three tests (generated); Impl. Package `IP-1350` — corrected to VERIFIED by this run | Pass |
| NFR-3820 | `unlisted_documents()`/`_listed_by()` | real-tree gate; two synthetic tests; shrink-only test | as above | Pass |
| NFR-3830 | `ledger_disagreements()` | real-tree gate; two synthetic tests; shrink-only test | as above | Pass |

## Test run

- `python3 -m pytest --tb=short --junitxml=…` : exit 0, junit 1284 tests, 0 failures, 0 errors, 3 skipped (1281 passed, 3 skipped, 190 s).
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -q`: all passed (green).
- `python3 -m pytest spacesim/tests/test_doc_integrity.py`: 9 passed.
- Seeded-defect demonstrations, each restored by `git checkout`/`rm` (tree clean afterwards): broken link -> `docs/FUTURE-WORK.md -> nope-seed.md`; unlisted `docs/zz-seeded-unlisted.md` -> `docs/INDEX.md -> zz-seeded-unlisted.md`; ledger (IP-1340 flipped to VERIFIED in the packages index only) -> `packages: IP-1340 is COMPLETE in Master Build Plan but VERIFIED in packages/INDEX.md`; stale allow-list line -> `docs/INDEX.md -> fixed-already.md` reported as "no longer occur".
- Mutations of the test module (restored): sub-index folder restriction removed -> only the **real-tree** index test fails; fence skip off -> synthetic link test fails; inline-code blanking off -> synthetic link test fails; absolute-path branch disabled -> **no test fails**.

## Scope audit

Implementing commit `18a9c89` touches: the test module, the three allow-lists, `CLAUDE.md`, RTM, Master Build Plan, packages index, `ROADMAP.md`, `pipeline-journal.md`. No production file (`git diff --name-only` checked; nothing under `spacesim/` outside `spacesim/tests/`). In scope.

## Judgement: the sub-index rule

The implementation lets a linked sub-index vouch only for documents at or below its own folder. FS-135 says a document counts as listed "by a sub-index the index links" and gives no folder condition; the rule therefore adds a restriction the text does not state. It is **a defensible reading**: "sub-index" implies subordinate, so a sub-index vouching for a document in a parent or sibling folder is not a sub-index relationship; without the restriction the research encyclopedia's `R400-index.md` hides the real omission of `strategic-assumptions-register.md` (journal #235), which is a false negative of exactly the kind the check exists to catch; and it still serves the spec's own example (`encyclopedia/INDEX.md` through the same-folder `R100-index.md`…). Weaknesses: it was calibrated after seeing the real tree (the spec's measured "three" was reproduced only with it), it is not stated in FS-135 or the package, and no synthetic test pins it (F-3). The rule is also loose in two ways: any linked `.md` whose name merely contains "index" counts as a sub-index, and backticked paths resolve from the index folder, its parent or the repo root, and inside fenced blocks.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F-1 | DoD 4 "failing-first run recorded" was not met: the checks and tests were written together; the journal admits it. The ledger-pair and shrink-only behaviour is nevertheless demonstrated here by seeded defects. | Low | `08-code-implementation` (process note; no re-run needed) |
| F-2 | Allow-lists are keyed on (file, target), so 82 occurrences are 62 lines: a second broken occurrence of an already-listed target in the same file, or a fix of one of two occurrences, goes unnoticed. Failure messages for the real tree also omit the line number FS-135 asks for ("file and line, for checks 1 and 2"), though `broken_links()` returns it. | Medium | `07-implementation-planning` (key form), then `08` |
| F-3 | Test gaps: the sub-index folder restriction is pinned only by the real-tree test (no synthetic case where a sub-index lists a document outside its folder); the absolute-`/docs/...` link branch is untested in effect (the synthetic case still fails with the branch disabled, because `/docs/b.md` does not exist on disk). Fence, inline-code and frozen/run-log exemptions are properly exercised. | Low | `08-code-implementation` |
| F-4 | The sub-index rule is not stated in FS-135 or IP-1350 (see judgement). | Low | `06-feature-specification` (add the rule), `07` |
| F-5 | Ledger pair (iii) reduces a composite status ("Done v1; Ready v2") to its first word, so it flags `FS-106`/`FS-110` as disagreements that are really wording differences; the package's Objective expected 0. Allow-listed to `05`/`06` with a reason. | Low | `05-feature-decomposition` / `06` |
| F-6 | Package and master-plan row text still reads "not yet authorized" for a package the owner authorized on 2026-10-23 (historical wording). Not edited here beyond the status cell. | Low | `00-pipeline-manager` |

## Ledger updates

`IP-1350` flipped `COMPLETE → VERIFIED` in the Master Build Plan (table row and a status note), `packages/INDEX.md`, `ROADMAP.md`; the RTM `Impl. Package` marker of `NFR-3800`/`NFR-3820`/`NFR-3830` updated; the Test column was not hand-edited (the generated-column check passes in the full run). `IP-1350` blocks no package.
