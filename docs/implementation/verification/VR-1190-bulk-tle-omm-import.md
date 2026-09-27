# VR-1190 — Verification Report: Bulk TLE and CCSDS OMM Multi-Object Import

> **Document ID:** VR-1190
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1190](../packages/IP-1190-bulk-tle-omm-import.md), [FS-119](../../features/FS-119-bulk-tle-omm-import.md) v1.0 (`FR-5220`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition for IP-1190
> **Feature Mapping:** FS-119 (`FR-5220`)
> **Related Topics:** [`spacesim/content/bulk_import.py`](../../../spacesim/content/bulk_import.py),
> [`spacesim/engine/orbit.py`](../../../spacesim/engine/orbit.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1190 — Bulk TLE and CCSDS OMM Multi-Object Import
- **Version verified:** 1.0
- **Tree state verified:** code at `d2818ff`. The branch tip is `853bd7f`, whose commits since then
  are docs only. Implementing commit: `b90cd62`.
- **Independence:** implemented by `08-code-implementation` in a prior context. This verification
  ran in a freshly spawned agent context with no memory of that work. **Disclosure:** the
  implementing commit's `Claude-Session` trailer names the same outer remote session ID this agent
  runs under. Every claim was re-derived from the source, a fresh test run, and hand-built fixtures
  in an independent probe.

## Result

**VERIFIED, with 2 Medium and 2 Low findings.** Every Definition of Done item and every
`FR-5220` Acceptance Criterion is confirmed. The full suite is green (707 passed, 3 skipped), and
both permanent gates are green. The Medium findings concern inputs outside the Acceptance
Criteria: OMM epoch handling and malformed per-object *assignments*. Neither blocks the
requirement as baselined, so both are routed for remediation planning.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization (MSTR-006 §3). | Granted 2026-09-27; recorded in the package and in the Master Build Plan. | ✅ Pass |
| 9 valid TLE objects plus 1 malformed: 9 added and 1 reported, with no abort. | `content/bulk_import.py::parse_multi_tle` captures every `"1 "`-led block, including a malformed one. `manager.py:413-440` `bulk_import()` reports each object. `test_bulk_import_tle_nine_valid_one_malformed_no_exception` passes. Probe: `T1/T2 + name + T1 + "2 x"` gave 2 objects, the malformed one kept for a per-object failure rather than dropped. | ✅ Pass |
| The same for CCSDS OMM (KVN). | `parse_ccsds_omm` splits on `OBJECT_NAME`. A block missing elements is returned with `None` values, and `_force_add_omm_object` (`manager.py:387-411`) reports it. Probe: block `B`, missing 4 elements, was reported as "missing i_deg, raan_deg, argp_deg, mean_anomaly_deg" while `A` succeeded. `test_bulk_import_omm_nine_valid_one_malformed_no_exception` passes. | ✅ Pass |
| A file recognized as neither format is rejected outright, before any object is processed. | Probe fixtures written for this report: plain text, XML OMM, and a file of only malformed TLE lines. **Both parsers raised `ValueError`** for each. `server.py:404-414` maps that to HTTP 400. | ✅ Pass |
| An object absent from the assignment map is reported as a failure, not dropped. | `manager.py` `bulk_import`: `assignment is None` → `{"ok": False, "reason": "no side/template assignment provided"}`. Test passes. | ✅ Pass |
| The single-object `force/tle`/`add_tle` and `FR-5140` lat/long paths are unchanged. | `add_tle` (`manager.py:352`) now delegates to `_force_add_tle_object`, whose body matches the pre-package inline code line for line (checked against `git show b90cd62`). All pre-existing `add_tle`/`add_ground_asset` tests pass in the full run. | ✅ Pass |
| Full suite green; both gates green. | See Test run. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `test_bulk_import.py` and the bulk-import/route tests exist and are green. | 12 tests across `test_bulk_import.py` and `test_bulk_import_session.py`, plus `test_web.py::test_bulk_import_tle_route_end_to_end`. All green. | ✅ Pass |
| `test_determinism.py` green. | 14 passed (with the import guard). | ✅ Pass |
| `test_import_guard.py` green. | Same. `engine/orbit.py`'s only change is a pure-function extraction, with no clock or RNG use. | ✅ Pass |
| Full suite, zero regressions. | 707 passed, 3 skipped. | ✅ Pass |
| Independently confirm `mean_to_true()` did not change `elements_to_rv()`, for at least one hand-computed example. | `orbit.py:86-94` holds exactly the two lines removed from `elements_to_rv` (now `:125`). Hand computation: e = 0.1, M = 1.0 rad, solved by Newton iteration, then ν = 2·atan(√((1+e)/(1−e))·tan(E/2)) = **1.1794692626997687**. `mean_to_true(1.0, 0.1)` returns the identical value. The original inline atan2 expression and the extracted function agree bit for bit at M = 1.234 (`==` → `True`). The round trip `true_to_mean(mean_to_true(1.0, 0.1), 0.1)` = 1.0. | ✅ Pass |
| Independently confirm the outright-rejection versus per-object-failure distinction with hand-built fixtures. | Done (see the DoD rows above). The fixtures were written for this report, not taken from the package's tests. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-5220 | `content/bulk_import.py`; `engine/orbit.py::mean_to_true`; `session/manager.py` (`_force_add_tle_object`, `_force_add_omm_object`, `bulk_import`); `session/inprocess.py::bulk_import`; `ui_web/server.py` `force/bulk_import` | `test_bulk_import.py`, `test_bulk_import_session.py`, `test_orbit.py::test_mean_to_true_*`, `test_web.py::test_bulk_import_tle_route_end_to_end`, `test_observer.py` (guard entry) | `:188`: accurate. Updated to `VERIFIED (VR-1190)` this pass. | ✅ Pass |

## Test run

```
PYTHONPATH=. python3 <scratchpad>/p1190.py      # independent probe (not committed)
  → hand nu 1.1794692626997687 == mean_to_true; inline==extracted True; round trip 1.0
  → garbage / xml / only-bad-tle: rejected by both parsers
  → OMM: A ok, B "missing i_deg, raan_deg, argp_deg, mean_anomaly_deg"
  → TLE batch with assignment owner="purple": BATCH ABORTED by ValidationError; later object BY not added
  → duplicate raw_id: two ok:true reports, same asset_id (silent overwrite)

python3 -m pytest -o addopts="" -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py  → 14 passed
python3 -m pytest -o addopts="" -q            → 707 passed, 3 skipped, 1 warning in 156.06s
```

## Scope audit

`git show --stat b90cd62` touches:

- **Production code:** the new `content/bulk_import.py`. Modified: `engine/orbit.py`,
  `session/manager.py`, `session/inprocess.py` and `ui_web/server.py`.
- **Tests:** the new `test_bulk_import.py` and `test_bulk_import_session.py`. Extended:
  `test_orbit.py`, `test_web.py` and `test_observer.py`.
- **Docs:** `CLAUDE.md`, `ROADMAP.md`, `FS-119`, the RTM, the Master Build Plan,
  `packages/INDEX.md`, `01-technical-work-breakdown.md`, the package, `docs/pipeline/backlog.md`
  and `docs/pipeline/pipeline-journal.md`.

Two excursions, both accepted:

- `session/inprocess.py` is not named in Files to Modify, but it is implied by the route, and the
  Master Build Plan row discloses it.
- The backlog and journal edits are named in the package's own Documentation Updates, which lists
  the backlog; the journal edits came from the implementing session doubling as pipeline manager.
  This is a process-scope observation, not a code-scope one.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| M1 | **The OMM `EPOCH` is parsed and then discarded.** `_force_add_omm_object` anchors the mean elements at the session's `ctx.start_epoch` (`manager.py:405`). The code comment justifies this as "the same simplification `add_tle` already makes", but that premise is false. A TLE asset propagates through sgp4 from the TLE's own embedded epoch at absolute Julian date (`engine/propagator.py:82-93`), so a TLE's epoch is honoured, and only `OrbitState.epoch` is nominal. An OMM object therefore lands at the wrong along-track phase by (start_epoch − EPOCH) × mean motion. The two import paths now disagree on the same real object. `FR-5220`'s Acceptance Criteria do not test positional fidelity, so this does not fail the package. | Medium | `07-implementation-planning` (remediation package: honour the OMM `EPOCH` by propagating the Kepler+J2 elements from it, or document the limitation in FS-119) |
| M2 | **A malformed per-object *assignment* aborts the whole batch.** The `Asset(id=…, owner=…, kind=…)` construction in both helpers sits outside their `try` blocks. An assignment with `owner: "purple"` raises a pydantic `ValidationError` out of `bulk_import()`. Objects already processed stay added, later objects are skipped, and the HTTP route returns 500. This contradicts the batch-continues posture for malformed input. Assignment `asset_id` values also bypass the `_validate_id` charset check that `TleRequest.id` applies. | Medium | `08-code-implementation` (small fix) / `07` for the package |
| L1 | A duplicate `raw_id` in one file (e.g. two TLEs with the same catalog number and no name lines) resolves to the same assignment. The second silently overwrites the first, and both are reported `ok: true`. | Low | `07-implementation-planning` |
| L2 | The implementing commit also edited `docs/pipeline/pipeline-journal.md`, which is outside `08-code-implementation`'s write scope under the skill rules. It was a combined pipeline-manager run. Process note only. | Low | `00-pipeline-manager` (process) |

## Related

[IP-1190](../packages/IP-1190-bulk-tle-omm-import.md) · [FS-119](../../features/FS-119-bulk-tle-omm-import.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
