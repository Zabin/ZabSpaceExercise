# VR-1093 — Verification Report: Release Dependency Lock Re-Pin (NFR-1510)

> **Document ID:** VR-1093
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1093](../packages/IP-1093-release-lock-repin.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1093`

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package
IP-1093, implementing commit `0f8f855` (branch `claude/ip-1093-build`). Fresh session, separate worktree; took no part in the implementation.

## Result
**VERIFIED** — 0 failed checks.

## Checklist audit
| Item | Evidence | Result |
|---|---|---|
| Diff of lock/pyproject vs parent | exactly hypothesis 6.170.9→.14, opentelemetry-api 1.45.1→.2, pydantic 2.14.1→.2, pydantic_core 2.50.1→.2, pytest 9.1.1→9.2.0; floors raised for pydantic, pytest, hypothesis only; 5-line header preserved; 33 pins, all `name==version`, no editable/local entries | pass |
| Lock equals fresh-venv freeze | own venv A from `pip install -r requirements.lock` + `pip install --no-deps -e .`: `pip check` clean; `pip freeze --exclude-editable` equals the lock (case/underscore-insensitive) | pass |
| Floors equal locked direct pins | `test_release_lock.py` (`verifies("NFR-1510")`); mutation 1 (one floor above its pin) and mutation 2 (one lock pin changed) each fail it (exit 1); files restored | pass |
| No source diff | `git diff --stat` on `spacesim/`: only the new test (+36); no `engine/` change | pass |
| Docs | Manual impact none is true; `docs/training/01-install-and-run.md` installs unversioned packages and names no version or lock, so it is not stale; CLAUDE.md "Release dependency lock" paragraph still accurate | pass |

## Test run (each mode once per environment, real exit codes, `--junitxml`)
| Environment | `-m "not browser"` | `-m browser` | Unfiltered |
|---|---|---|---|
| A: from the lock | exit 0, 2138 tests, 0 failed, 5 skipped | exit 0, 42 passed | exit 0, 2180 tests, 0 failed, 0 errors, 4 skipped |
| C: latest of everything (`pip install -U -e ".[content,ui,dev]"`) | same | same | same |

Environment C resolved to exactly the lock set (`pip freeze` diff empty): no newer version has appeared since the lock. System environment, by name: `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py`, `test_determinism.py`, `test_import_guard.py`, `test_release_lock.py` all pass.

## Ledger recount
Before this update: 91 `VERIFIED`, 1 `COMPLETE` (`IP-1093`), 2 `READY` (`IP-1089`, `IP-1094`), 94 packages. Header-vs-rows script: MBP, packages INDEX and ROADMAP agree for every package; only the IP-1093 rows differed from the expected state. After: 92 / 0 / 2 / 94.

## Findings
| ID | Description | Severity | Owner |
|---|---|---|---|
| N1 | Package header `Status:` of IP-1093 still reads `READY` (headers reconciled by a separate pass, as for IP-1092) | Info | `00-pipeline-manager` |
| N2 | Skipped count is 4 unfiltered, 5 in `-m "not browser"` (same as VR-1092); not a defect | Info | none |
