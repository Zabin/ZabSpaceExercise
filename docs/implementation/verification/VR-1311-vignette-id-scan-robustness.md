# VR-1311 — Verification Report: Vignette Id Scan Robustness (FR-5310, NFR-1600)

> **Document ID:** VR-1311
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1311](../packages/IP-1311-vignette-id-scan-robustness.md) v1.0,
> [FS-131](../../features/FS-131-load-time-vignette-validation.md) v1.1
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1311` (closes `BL-0252`)
> **Feature Mapping:** FS-131 (`FEAT-5300`)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1311 — Vignette Id Scan Robustness (v1.0)
- **Implementing commit:** `a7a036d` (branch `claude/ip-1311-build`); tree verified at that commit.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 1 Low and 1 Info finding (neither blocks).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Tests exist and pass; 1-3 seen failing first | `test_vignette_id_scan.py` has 6 tests, all pass. Reproduced failing-first: parent `vignette.py` (`HEAD~1`, scratch swap, restored) fails tests 1, 2, 3 and 5 (4 and 6 pass) | Pass |
| 2 | Full suite green, gates green | Below | Pass |
| 3 | Reproduction table statuses | Tests assert 404 (unknown id), 200 (valid after bad file), 400 `invalid_vignette` (`broken-x`, `bad-yaml`) over `TestClient` | Pass |
| 4 | Diff touches only `vignette.py`, new test, docs | `git show --stat`: ROADMAP, MBP, packages/INDEX, the package header, RTM, `vignette.py`, new test only | Pass |
| 5 | Docs done, status COMPLETE | MBP row/count, packages/INDEX, ROADMAP, package header, RTM FR-5310/NFR-1600 cells | Pass |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | One helper for both scans | `vignette.py` `_declared_vignette_id` (lines ~253-267); both scans call it (built-in ~290, external ~304); no remaining unguarded `safe_load`/`.get("id")` in `load_vignette` | Pass |
| 2 | Bad file first: unknown id 404, later valid id 200 | Own reproduction via tests 1 and 2 on the new code (HTTP); parent code fails the same tests | Pass |
| 3 | Non-mapping `vignette:` skipped in both roots | Test 3 (list and string, built-in and external); mutation removing the block check makes it fail | Pass |
| 4 | Exact-name bad file still refused with IP-1310 message | Test 4 passes (`where` = `bad-yaml.yaml`, reason `not valid YAML`, HTTP 400) | Pass |
| 5 | `list_vignettes` unchanged | `list_vignettes` not in the diff; test 6 resolves every shipped id | Pass |
| 6 | Suite and gates green | Below | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-5310 | `vignette.py::_declared_vignette_id`, `load_vignette` | all 6 tests (module `verifies("FR-5310","NFR-1600")`) | Test cell lists `test_vignette_id_scan.py` tests | Pass |
| NFR-1600 | same | same | Test cell lists them | Pass |

Both IDs are live (`--origin-report` accepts the marker; `test_test_origins.py` green).

## Test run

- `python3 -m pytest -m "not browser" --junitxml=...`: exit 0; junit `tests="1280" failures="0" errors="0" skipped="4"`.
- `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_vignette_id_scan.py` run by name: exit 0 (re-run after the ledger edits below).
- Mutations of the fix (each restored; tree clean afterwards): drop the `vignette`-block mapping check, 1 test fails (caught); drop `yaml.YAMLError` from the except, 3 tests fail (caught); drop the top-level `isinstance(raw, dict)` check, **0 tests fail (survives)**.

## Scope audit

In scope. Production change limited to `spacesim/content/vignette.py`; new `test_vignette_id_scan.py`; documentation edits are those the package names plus the RTM cells. No `docs/pipeline/`, engine, or session files touched.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F-1 | Mutation survives: no test has a file whose top-level YAML is a list/scalar (only `vignette:` values are non-mapping). The `isinstance(raw, dict)` branch is unpinned, so a regression to `raw.get` on a list (`AttributeError`, a 500) would pass the suite. | Low | `08-code-implementation` (add a top-level-list file to test 3) |
| F-2 | Skip count is 4 in the non-browser run versus the 3 quoted in earlier reports and `CLAUDE.md`; not attributable to this package (no skip markers added). | Info | none (note for status-line upkeep) |

## Next step

`10-integration-review` for the tranche, or `08-code-implementation` on the next READY package (`IP-1102`, `IP-1072`, `IP-1073`, `IP-1334`).
