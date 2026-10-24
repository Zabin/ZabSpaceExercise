# VR-1102 — Verification Report: Save Load Robustness (FR-7220, FR-7230, NFR-1600)

> **Document ID:** VR-1102
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1102](../packages/IP-1102-save-load-robustness.md) v1.0,
> [FS-110](../../features/FS-110-save-and-resume.md) v2.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1102` (closes `BL-0326`, `BL-0352`, `BL-0359` F-13)
> **Feature Mapping:** FS-110 (`FEAT-7200`)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1102 — Save Load Robustness (v1.0)
- **Implementing commit:** `7efa673` (branch `claude/ip-1102-build`); tree verified at that commit.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 3 Low findings and 1 Info finding (none block).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Tests exist and pass; 1, 2, 6 seen failing first | `test_save_load_robustness.py`: 19 tests pass. Scratch copy with parent `manager.py`/`server.py` (`HEAD~1`): 18 of 19 fail (all of tests 1-6 and 9; 500s and stale content), only the valid-save regression passes. Copy discarded | Pass |
| 2 | No Objective-table input returns 500 | Own HTTP probes (below): legacy missing vignette, each missing key (both formats), malformed pending/orders/ssn/eventlog all 400 with the key named | Pass |
| 3 | `content` equals the saved force after pre-start edits | Own round trip via Creator `DELETE`/`PATCH owner` + `force/ground`: deleted asset absent, re-owned asset under new bucket, added asset present; load 200, assets/owners equal; re-save content identical; content-only `SessionManager` builds the baseline's asset set | Pass |
| 4 | Full suite green, gates green | Below | Pass |
| 5 | Diff touches only `manager.py`, `server.py`, tests, docs | `git show --stat 7efa673`: those plus `CLAUDE.md`, `FS-110` Referenced By, RTM, two training pages, ledgers (all named by Documentation Updates). No engine, `inprocess.py`, or `docs/pipeline/` | Pass |
| 6 | Docs done, status COMPLETE | Header, MBP row, packages/INDEX, ROADMAP, RTM, training API/UI references, CLAUDE.md clause | Pass |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | `validate_save` checks keys/types and legacy availability before replay | `manager.py::validate_save` (required keys per format, int checks, `EventLog.model_validate`, list-of-mapping checks, legacy `load_vignette` try); `load_save_with_warnings` calls it before `from_state` (`inprocess.py` ~1066, unchanged) | Pass |
| 2 | Legacy save naming a missing vignette: 400 | Own probe: 400 "the save depends on vignette 'nope', which is not available in the content directories" | Pass |
| 3 | Delete a built asset pre-start: absent from content, resume gives post-delete world | Own round trip (DoD 3) | Pass |
| 4 | `GET /api/sessions` unchanged by a refused load | Own probe: session count stayed constant across 25+ refusals, grew only on accepted loads; test 5 asserts next id unused | Pass |
| 5 | Valid legacy and self-contained saves load with same warnings | Own probe: self-contained `[]`, legacy the one legacy warning; test 8 | Pass |
| 6 | Suite and gates green | Below | Pass |
| 7 | New tests carry `verifies` naming live IDs; RTM regenerated | Module marker `FR-7230`,`NFR-1600`; per-test `FR-7210`,`FR-7220`; `--origin-report=rtm` reports "unchanged" against the committed matrix; `test_test_origins.py` green | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-7220 | `manager.py::save_state` (`_authored_content`, `_built_asset_forms` reconciliation) | tests 6, 7, 9 | lists the new file | Pass |
| FR-7230 | `validate_save`; `server.py::load_save` backstop | tests 1-5, 8 | lists the new file | Pass |
| NFR-1600 | same | module marker, tests 1-5 | lists the new file | Pass |

## Test run

- `python3 -m pytest -m "not browser" --junitxml=...`: exit 0; `tests="1299" failures="0" errors="0" skipped="4"`.
- `test_determinism.py` + `test_import_guard.py` by name: exit 0 (14 passed). `test_doc_integrity.py` and `test_test_origins.py`: see the final run recorded in the commit (green).
- Mutations in a scratch copy (each restored): drop required-key check, 1 test fails (caught); drop content reconciliation, 1 fails (caught); drop owner-move append, 1 fails (caught); revert to `vignette.model_dump` instead of `_authored_content`, 1 fails (caught); drop the `FileNotFoundError` re-raise in `validate_save`, **0 fail (survives)**; drop only the server backstop, **0 fail (survives)** (the two defences cover each other; only dropping both would 500, and the legacy test asserts the id, not the "not available" wording).

## Determinism

`_authored_content` and `_built_asset_forms` are plain dumps taken at construction, read only by `save_state`; no engine, RNG or clock touched, not part of `WorldState`. Capturing before `build_world` is deliberate (it stamps defaults on the shared model); test 9 pins that. Replay of every previously loadable save is unchanged (own valid-save probes load 200).

## Scope audit

In scope (see DoD 5). Design Decision 4 (ground sites/sensors): ground sites are assets here and are covered by the same loop (own probe: a force-added ground site lands in content); the vignette `sensors` list has no pre-start edit route. The package header carries no explicit completion note stating this (see F-3).

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F-1 | Validation gaps still reachable: `overrides` of a non-mapping type (e.g. a string) gives HTTP **500** from `from_state` (outside the 3 listed rows but the same class as BL-0359); a `pending` entry with `t` null/non-integer, an `orders` entry with junk values, a negative or enormous `final_time`, and a non-string `classification` are accepted (200) and fail, if at all, later. A non-object JSON body is a 422 from FastAPI (acceptable). | Low | `07` package repair, then `08` (type-check `overrides`, `pending[].t`, `final_time` range) |
| F-2 | Tests do not pin the legacy "not available" wording or the backstop independently (two surviving mutations above). | Low | `08` (assert the detail text; add a case where `validate_save` is bypassed) |
| F-3 | Design Decision 4 outcome (ground sites/sensors) not recorded as a completion note in the package. | Low | `08` doc note |
| F-4 | Skip count 4 versus the 3 quoted in older status text; not attributable to this package. | Info | none |

## Next step

`08-code-implementation` on the next READY package (`IP-1072`, `IP-1073`, `IP-1334`); `IP-1073` now has its real refusals to test against. File F-1 as a backlog entry.
