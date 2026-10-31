# VR-1092 — Verification Report: Retired-Documents Check (NFR-3810)

> **Document ID:** VR-1092
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1092](../packages/IP-1092-retired-documents-check.md) v1.0,
> [FS-135](../../features/FS-135-documentation-integrity-checks.md) v1.1
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` (`RETURNED`) transition of `IP-1092`
> **Feature Mapping:** FS-135 (`FEAT-12300`)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1092 — Retired-Documents Check (`NFR-3810`, FS-135 v1.1 check 2)
- **Implementing commit:** `7b4a9ee` (branch `claude/ip-1092-build`); tree verified at that commit.
- **Independence:** fresh session; did not implement this package.

## Result

**↩️ RETURNED** — 1 failed check (scope/ledger: Finding F1, Medium). The check itself is sound: every failure mode, the frozen-history exemption, the empty shrink-only allow-list and the root-level convention behave as FS-135 v1.1 and `NFR-3810` specify, and every mutation was killed. The only blocker is a documentation excursion fixable by reverting three ROADMAP rows.

## Definition of Done / Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Modes (a), (b), (c) each with a failing-first synthetic test | `test_retired_mode_a_*`, `_mode_b_*`, `_mode_c_*`, plus unreadable-table, folder, root, none-body, allow-list tests (11 new, all `verifies("NFR-3810")`); each killed by a mutation (below) | Pass |
| 2 | Fences / code spans scanned; check 1 unchanged | Scanner iterates `live_text(...).split("\n")` with no `_prose_lines`; fenced and `~~~` references reported (probe, test line 4). Diff to check 1 code: none | Pass |
| 3 | Allow-list exists, empty, shrink-only on (b) only | `doc_integrity_allow_retired.txt` is comments only; `retired_keys` emits mode (b) only; `_gate` stale-line test passes | Pass |
| 4 | `docs/INDEX.md` carries the section, passes check 3 | Section with body `none` = zero rows; real-tree test green with empty list | Pass |
| 5 | Root-level choice recorded and tested | `test_retired_root_path_declared_in_docs_index_is_enforced`; probe: `docs/ROADMAP.md` is not a hit, `../ROADMAP.md` and `ROADMAP.md` are | Pass |
| 6 | Gates, full suite, docs in sync | Below; CLAUDE.md doc-check paragraph names `NFR-3810`/IP-1092, INDEX section present, Manual impact `none` is true (test-only) | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM | Result |
|---|---|---|---|---|
| NFR-3810 | `retired_declarations`/`retired_findings` in `spacesim/tests/test_doc_integrity.py` | 11 `test_retired_*` tests; `python3 -m pytest --origin-report=rtm` reports Test column unchanged (matches committed) | Impl + Test cells agree | Pass |

## Test run

- `test_doc_integrity.py test_test_origins.py test_origin_retag.py test_determinism.py test_import_guard.py`: exit 0.
- Unfiltered `python3 -m pytest --junitxml`: exit 0, 2176 tests, 0 failed, 0 errors, 4 skipped.
- `-m "not browser"`: exit 0, 2134 tests, 0 failed, 5 skipped (runs 1 and 2 overlapped in wall time; one skip differs, an environment race rather than a defect).
- `-m browser`: exit 0, 42 passed, 0 skipped.
- Real tree: `retired_findings(REPO)` is empty in 0.04 s (negligible cost).

## Adversarial probes (own synthetic trees)

Pass as specified: declared-and-present (a); declared-and-absent (clean); folder row with trailing `/` (present -> a, references beneath -> b); missing date, bad date (`2026-13-45`), missing successor, missing path, nonexistent successor (c); successor resolved repo-root or index-relative; unreadable table (no separator, 3 columns, prose) names the index; `none` body zero rows; references in prose, backticks, `~~~`/``` fences and sibling INDEX bodies reported; references in `docs/reviews`, `docs/implementation/verification`, `docs/architecture/adr`, both archives and the journal run log not reported while the journal Position block is; declaring section exempt, rest of the declaring INDEX scanned; whole-token IDs (`DOC-9x`, `DOC-9-1` ignored); CRLF handled; non-INDEX files carrying the heading ignored. Real tree + fake `ROADMAP.md` row in `docs/INDEX.md` fails `test_real_tree_retired_documents_check_is_clean_with_empty_allow_list` naming `docs/INDEX.md` line 51 `ROADMAP.md`; restored.

Mutations (each applied to the test module, suite run, restored): drop (a) -> 4 failures; drop (b) -> 4+; drop frozen exclusion -> 3 (incl. check 1); drop (c) successor-exists -> `test_retired_mode_c_*` fails; scan with fences stripped -> fence test fails.

## Documentation audit

Manual impact `none` is true: no operator-visible label, route or message. CLAUDE.md doc-check paragraph updated and accurate; `docs/INDEX.md` Retired documents section present; hand-offs (retirement procedure in `.claude/skills/README.md` and the retiring skills) are recorded in the package as an owner-authorized `04`/`06` hand-off, not written here. RTM Test column regenerated and unchanged. Ledger audit: MBP tally recounted before this update, 90 VERIFIED / 1 COMPLETE / 3 READY / 94 (agrees). One disagreement: F1.

## Scope audit

Files match the package list plus implied ledgers (CLAUDE.md, MBP, packages INDEX, ROADMAP, RTM Impl cell). Excursion: the ROADMAP edit also flipped the rows of `IP-1089`, `IP-1093`, `IP-1094` to COMPLETE (F1).

## Findings

| ID | Description | Severity | Owner |
|---|---|---|---|
| F1 | `ROADMAP.md` in `7b4a9ee` changes the `IP-1089`, `IP-1093`, `IP-1094` rows from READY to COMPLETE, but the MBP and packages INDEX on this branch still say READY (no such implementation exists here). Out of scope; ledger disagreement the doc suite does not catch. Revert those three rows. | Medium | `08-code-implementation` re-run |
| F2 | A heading variant (`## retired documents`, `### Retired documents`, double space inside the title) is silently not a section: a declared-and-present file then passes. Fail-open on a typo. Suggest flagging a near-miss heading. | Low | `08` (or `06` to decide) |
| F3 | A path cell written as a link (`[o](docs/o.md)`) is not unwrapped, so mode (a) misses a still-present file (check 1 also passes as the link resolves). FS-135 says never a link, but nothing enforces it. | Low | `08` |
| F4 | A placeholder in the ID column (`—`, `n/a`) is treated as an ID and matched live. | Low | `08` |
| F5 | Observation: a relative link to a retired file written bare (`](old.md)`) is not matched by the path string; it is caught only by check 1 once deleted. Consistent with the package test; no action. | Info | none |

## Quality gate

Not all boxes: the implementing change did not stay in scope (F1), so `VERIFIED` is withheld. Re-run `08-code-implementation` on `IP-1092` (revert the three rows; F2-F4 optional), then re-verify.
