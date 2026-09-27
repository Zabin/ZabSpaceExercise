# IP-1190 — Bulk TLE and CCSDS OMM Multi-Object Import

> **Package ID:** IP-1190
> **Version:** 1.0
> **Status:** 🟢 COMPLETE *(implemented 2026-09-27, MSTR-006 §3 authorization granted the same day;
> awaiting `09-package-verification` in a fresh session — this session implemented it and may not
> verify its own work)*
> **Dependencies:** [FS-119](../../features/FS-119-bulk-tle-omm-import.md) v1.0 (`FR-5220`),
> `FR-1210` (propagator seam, unchanged, reused), `FR-5140`/`session/manager.py::add_tle` (the
> single-object mechanism this package generalizes, not replaces)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0067` (external validation report,
> 26 Sep 2026, item B1), `BL-0096` (FS-119's two Open Questions, resolved below)
> **Produces:** a bulk TLE/CCSDS OMM (KVN) multi-object import capability satisfying `FR-5220`
> **Feature Reference:** [FS-119 — Bulk TLE and CCSDS OMM Multi-Object Import](../../features/FS-119-bulk-tle-omm-import.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/engine/orbit.py`](../../../spacesim/engine/orbit.py),
> [`spacesim/engine/propagator.py`](../../../spacesim/engine/propagator.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Confirmed directly against the live code at authoring time:
`SessionManager.add_tle()` (`session/manager.py` lines 342-360) is the single-object mechanism
`FR-5220` batches — it validates a TLE via `sgp4.api.Satrec.twoline2rv()`, builds
`OrbitState(source="tle", tle_line1=..., tle_line2=..., epoch=self.ctx.start_epoch)`, force-adds an
`Asset`, and re-baselines `self.sim._initial_state`. `engine/orbit.py`'s `OrbitState` (lines 22-42)
already carries a `source: Literal["kepler", "tle"]` discriminator and a full Keplerian element set
(`a_m`/`e`/`i_deg`/`raan_deg`/`argp_deg`/`ta_deg`) — a CCSDS OMM's Keplerian mean-elements set
(`SEMI_MAJOR_AXIS`/`ECCENTRICITY`/`INCLINATION`/`RA_OF_ASC_NODE`/`ARG_OF_PERICENTER`/`MEAN_ANOMALY`)
maps onto this existing shape directly, with one conversion needed (mean anomaly → true anomaly at
epoch) that `engine/orbit.py::elements_to_rv()` (lines 112-115) already computes inline via its
private `_solve_kepler()` — extractable as a new public sibling of the existing public
`true_to_mean()` (line 70) with zero behavior change to `elements_to_rv()` itself. **No CCSDS OMM
parsing exists anywhere in this repository today** — confirmed by search; this is genuinely new
parsing logic, exactly as FS-119's own Risks section already flags.*

## Package ID

IP-1190

## Title

Bulk TLE and CCSDS OMM Multi-Object Import

## Objective

Let White Cell import many objects from one multi-object TLE file or one CCSDS OMM (KVN) file in a
single operation, each object assigned a side and asset template, with per-object success/failure
reporting so one malformed object never aborts the batch — generalizing, not replacing, the
existing single-object `add_tle`/`force/tle` path.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-119 — Bulk TLE and CCSDS OMM Multi-Object Import](../../features/FS-119-bulk-tle-omm-import.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-5220 | Bulk TLE and CCSDS OMM multi-object import | A new `content/bulk_import.py` module parses either format into a list of per-object element sets; `SessionManager` gains a batch entry point that resolves each object's assigned side/template and force-adds it through the same per-object construction path `add_tle` already uses (extracted into a shared helper), catching and reporting a per-object failure without aborting the batch; a new HTTP route exposes this to the Operator Console. |

## Architecture Components

- **C5 Content & Data** (`content/bulk_import.py`, new) — owns multi-object TLE parsing and CCSDS
  OMM (KVN) parsing into a common per-object element-set shape; no new domain entity, only a new
  parsing module, per `ADR-0007` (content as data).
- **C1 Deterministic Core** (`engine/orbit.py`) — gains one new public function
  (`mean_to_true()`), extracted from `elements_to_rv()`'s existing inline computation with zero
  behavior change to that function — reused by the OMM half of this package's import path.
- **C2 Session / Application Layer** (`session/manager.py`) — owns the batch entry point and the
  shared per-object force-add helper extracted from `add_tle`.
- **C4 Operator Console** (`ui_web/`) — a new route presenting the per-object side/template
  assignment input and the per-object success/failure report, alongside (not replacing) the
  existing single-object `force/tle` route and `FR-5140`'s lat/long entry.

## Interfaces

`INT-0013` (Content & Data → Space-Track.org, TLE import) — cited by `FR-5220` itself as the
closest existing interface, but the Requirements Review already flagged (`BL-0092`) that this
Feature's file-based, multi-object interaction is a stretched fit for `INT-0013`'s documented
network-fetch, single-object shape. **This package does not invent a new interface ID** — per
FS-119's own Open Question 1, that decision belongs to whoever next touches the ICD. This package's
own design does not require an ICD edit to proceed (the parsing module and session-layer entry
point are both new code, not a new *interface* in the ICD sense — no cross-subsystem contract this
document needs to cite differently to be buildable).

## Design Decisions (resolving `BL-0096`)

1. **A file that is neither valid multi-object TLE nor valid CCSDS OMM is rejected outright, before
   any object is force-added, with one top-level error** — distinct from a malformed *object* within
   an otherwise-recognizable file (which is a per-object failure, batch continues). **The
   distinguishing test is structural recognizability at the file level**: a TLE file must contain at
   least one syntactically well-formed two-line (or three-line, with a name line) TLE block (lines
   starting `"1 "`/`"2 "`, correct length); an OMM (KVN) file must contain at least one recognizable
   `OMM` KVN header/keyword block (e.g. `CCSDS_OMM_VERS`, `META_START`/`META_STOP`,
   `SEMI_MAJOR_AXIS`, etc.). A file with zero such blocks in either shape is rejected outright
   (`ValueError`, not a per-object failure list). A file that *does* contain at least one recognizable
   block, but where a specific block fails element-level validation (e.g. `sgp4` rejects a
   particular TLE, or an OMM block is missing a required Keplerian element), reports that one
   object's failure and continues — exactly `FR-5220`'s own Acceptance Criteria for the
   already-specified case.
2. **No new maximum batch size.** This Feature introduces no new engine-enforced cap, deferring
   entirely to the existing `~24 satellites` soft guideline (`ADR-0019`) and the existing clock-lag
   watchdog (`SessionManager._record_catch_up_lag`) — consistent with `ADR-0019`'s own already-
   settled decision that sizing is a soft guideline, not a hard limit, and with `FR-5220`'s own
   silence on the question (nothing to newly baseline).

## Files to Create

- `spacesim/content/bulk_import.py` — `parse_multi_tle(text: str) -> list[dict]`: splits a
  multi-TLE text file into individual objects (optional name line, then the existing two 69-char
  `"1 "`/`"2 "` lines this package's per-object path already validates); each returned dict is
  `{"raw_id": <name or line1's NORAD-catalog-number field>, "format": "tle", "line1": ..., "line2":
  ...}`. Raises `ValueError` (Design Decision 1's outright-rejection case) if zero recognizable
  TLE blocks are found. `parse_ccsds_omm(text: str) -> list[dict]`: parses **CCSDS OMM in KVN
  (Key=Value Notation) form only** — XML OMM is explicitly out of scope for this package (see
  Risks); each returned dict is `{"raw_id": <OBJECT_NAME or OBJECT_ID>, "format": "omm", "a_m":
  ..., "e": ..., "i_deg": ..., "raan_deg": ..., "argp_deg": ..., "mean_anomaly_deg": ...,
  "epoch_iso": ...}`. Raises `ValueError` if zero recognizable OMM KVN blocks are found.

## Files to Modify

- `spacesim/engine/orbit.py` — extract `mean_to_true(mean_anom: float, e: float) -> float` as a new
  public function (mirroring the existing public `true_to_mean()`, line 70), containing exactly the
  `_solve_kepler()` + eccentric-to-true-anomaly computation `elements_to_rv()` already performs
  inline (lines 114-115); `elements_to_rv()` itself calls the new function instead of repeating the
  inline computation — a pure, behavior-preserving refactor, verified by the existing orbit-mechanics
  test suite before this package's own OMM path calls the new function.
- `spacesim/session/manager.py` — extract `add_tle()`'s common per-object body (sgp4 validation,
  `Asset`/`OrbitState` construction, `world.assets[...] = ...`, `sim._initial_state` re-baseline)
  into a shared helper, e.g. `_force_add_tle_object(asset_id, line1, line2, owner, kind) ->
  tuple[bool, str]`, called by both the unchanged `add_tle()` (single-object path, regression-only)
  and the new batch path. Add a second shared helper, e.g. `_force_add_omm_object(asset_id,
  elements: dict, owner, kind) -> tuple[bool, str]`, building `OrbitState(source="kepler", a_m=...,
  e=..., i_deg=..., raan_deg=..., argp_deg=..., ta_deg=mean_to_true(...), epoch=...)` and force-adding
  the resulting `Asset`, mirroring the TLE helper's error-handling shape (a raised exception during
  element construction becomes a per-object failure string, never propagates). Add
  `bulk_import(self, file_format: Literal["tle", "omm"], content: str, assignments: dict[str,
  dict]) -> list[dict]`: parses via the new `content/bulk_import.py` functions (a parse failure here
  is Design Decision 1's outright rejection — propagates as a single `ValueError`, not a per-object
  report); for each parsed object, looks up `assignments.get(raw_id)` (an object with no assignment
  entry is reported as a per-object failure, "no side/template assignment provided" — not silently
  skipped and not an outright file rejection); calls the appropriate shared per-object helper; and
  returns a per-object `{"raw_id": ..., "asset_id": ..., "ok": bool, "reason": str}` report list,
  gated on `if self.started: return [...]` the same way `add_tle`/`add_ground_asset` already gate
  (a batch import is a pre-start force-edit, same authority level as every existing force-edit path).
- `spacesim/ui_web/server.py` — a new `BulkImportRequest` model (`format: Literal["tle", "omm"]`,
  `content: str`, `assignments: dict[str, dict]`) and a new route,
  `POST /api/sessions/{sid}/force/bulk_import`, calling `SessionManager.bulk_import(...)` and
  returning its per-object report list — additive, alongside the unchanged existing `force/tle`
  route (`FR-5140`'s single-object path is explicitly out of scope for modification, per FS-119's
  own Scope).

## Implementation Tasks

1. Write a failing test asserting `mean_to_true()` + `elements_to_rv()`'s existing behavior are
   unchanged after the extraction (regression: propagate a known Keplerian element set before and
   after the refactor, assert identical ECI state), before extracting the function.
2. Write a failing test for `parse_multi_tle()`: a well-formed multi-object file (with and without
   name lines) parses into the expected per-object dicts; a file with zero recognizable TLE blocks
   raises `ValueError` (Design Decision 1); a file with N-1 well-formed blocks and one malformed
   block still returns N entries (the malformed one flagged for later per-object failure, not
   dropped at parse time) — before writing the parser.
3. Write a failing test for `parse_ccsds_omm()`: a well-formed KVN OMM file with multiple `OMM`
   blocks parses into the expected per-object element dicts; a file with zero recognizable OMM
   blocks raises `ValueError`; a file that is neither TLE-shaped nor OMM-shaped is confirmed to
   raise from *both* parsers (the batch entry point's own outright-rejection path, Task 6, decides
   which error to surface) — before writing the parser.
4. Write a failing test asserting `_force_add_tle_object()`/`add_tle()` produce identical
   `Asset`/`OrbitState` results for the same inputs (regression, confirming the extraction changed
   nothing observable), before extracting the helper.
5. Write a failing test for `_force_add_omm_object()`: a valid Keplerian element set produces an
   `Asset` whose `OrbitState.ta_deg` matches the expected mean-to-true conversion at the given
   epoch, before implementing it.
6. Write a failing test for `bulk_import()`: nine valid objects + one malformed object (in a
   multi-TLE file) produce nine successful reports and one failure report, no exception raised for
   the batch as a whole (`FR-5220`'s own Acceptance Criterion 1, verbatim); the same for a CCSDS OMM
   file (Acceptance Criterion 2); a file recognized as neither format raises a single `ValueError`
   before any object is processed (Design Decision 1); an object present in the file but absent from
   `assignments` is reported as a per-object failure, not silently dropped and not an outright file
   rejection; a call against a started session returns an empty report list with no assets added,
   mirroring `add_tle`'s existing gate.
7. Wire the HTTP route and `BulkImportRequest`; write a failing test round-tripping the full flow
   via the HTTP layer for both formats, before adding the route.
8. Re-run the full existing suite; confirm `add_tle`'s and `add_ground_asset`'s existing tests still
   pass unchanged (the shared-helper extraction is behavior-preserving).

## Tests to Add

- `spacesim/tests/test_orbit.py` (or the nearest existing orbit-mechanics test file) —
  `mean_to_true()` regression + a direct round-trip assertion against `true_to_mean()` (mean→true→
  mean recovers the original value within tolerance).
- `spacesim/tests/test_bulk_import.py` *(new)* — `parse_multi_tle()`/`parse_ccsds_omm()` parsing
  correctness, the outright-rejection case for each, and the per-object malformed-entry case.
- `spacesim/tests/test_session.py` (or a new file alongside it) — `bulk_import()`'s per-object
  report shape, the nine-valid-one-malformed Acceptance Criteria for both formats, the
  no-assignment-entry per-object failure, and the `self.started` gate.
- `spacesim/tests/test_web.py` — the new `/force/bulk_import` route, end to end for at least one
  format.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — `content/bulk_import.py` is a Content & Data module (no engine-layer import
crossing); `engine/orbit.py::mean_to_true()` is a pure function extraction with no wall-clock read
or global RNG use.

## Documentation Updates

- `CLAUDE.md` Code Map — `engine/orbit.py`'s entry gains the `mean_to_true()` addition;
  `session/manager.py`'s entry gains the `bulk_import()`/shared-helper note; a new
  `content/bulk_import.py` entry added.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-5220`'s `Implementation Package`
  cell updated from `UNASSIGNED` to `IP-1190`; `Test` cell updated once the named test files exist.
- `docs/features/FS-119-bulk-tle-omm-import.md` — `Referenced By` metadata gains this package's
  link (metadata cross-link only). Open Question 1 (`INT-0013` ICD stretch, `BL-0092`) is not
  resolved by this package (routed to whoever next touches the ICD, unchanged); Open Questions 2-3
  are given this package's Design Decisions to cite once `06-feature-specification` revisits them.
- `docs/pipeline/backlog.md` — `BL-0096` updated: both Open Questions resolved by this package's
  two Design Decisions; recommend flipping to `DONE` at the next `00-pipeline-manager` harvest.
  `BL-0092` (the `INT-0013` stretch) remains open/unchanged, still routed to the ICD owner.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3) — granted 2026-09-27 by the project owner's direct instruction.
- [x] A multi-object TLE file with nine valid objects and one malformed object produces nine
  force-added Assets with the specified side/template assignments and reports the tenth's failure,
  without aborting the batch. (`test_bulk_import_tle_nine_valid_one_malformed_no_exception`)
- [x] A CCSDS OMM (KVN) file with multiple objects produces the same result.
  (`test_bulk_import_omm_nine_valid_one_malformed_no_exception`)
- [x] A file recognized as neither format is rejected outright, before any object is processed.
  (`test_bulk_import_unrecognizable_file_raises`, `test_neither_tle_nor_omm_shaped_file_raises_from_both_parsers`)
- [x] An object present in the file but missing from the caller's assignment map is reported as a
  per-object failure, not silently dropped.
  (`test_bulk_import_object_missing_assignment_reported_as_failure_not_dropped`)
- [x] The existing single-object `force/tle`/`add_tle` path and `FR-5140`'s lat/long entry path are
  both unchanged in behavior (verified: full suite green, zero regressions to
  `test_vignette_creator_session.py`/`test_web.py`'s existing `add_tle`/`add_ground_asset` tests).
- [x] Full existing test suite green, zero regressions, both permanent gates green: **638
  passed / 3 skipped** (up from 622/3), `test_determinism.py` and `test_import_guard.py` both
  green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `test_bulk_import.py` and the new `bulk_import()`/route tests exist and are green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Full existing suite re-run with zero regressions, in particular every existing `add_tle`/
  `add_ground_asset`/`force/tle` test.
- [ ] Independently confirm, by reading the shipped code, that `mean_to_true()`'s extraction did not
  change `elements_to_rv()`'s numerical output for at least one hand-computed example.
- [ ] Independently confirm the outright-rejection vs. per-object-failure distinction (Design
  Decision 1) against a hand-constructed fixture of each kind, not merely re-running this package's
  own tests.

## Dependencies

- **Upstream:** [FS-119](../../features/FS-119-bulk-tle-omm-import.md) v1.0 (approved,
  `✅ Ready for implementation planning`), `session/manager.py::add_tle()` (baseline code, extended
  in place, not replaced), `engine/orbit.py::elements_to_rv()`/`true_to_mean()` (baseline code, the
  precedent this package's `mean_to_true()` extraction mirrors).
- **Downstream:** none identified.
- **Build-sequencing:** Independent of the other Must-tier packages this increment (`IP-1180`,
  `IP-1062`, `IP-1200`) — different files, no shared seam.

## Risks

- **CCSDS OMM parsing is new format support, scoped to KVN only.** No existing code path parses
  OMM today (TLE-only baseline). This package deliberately does **not** implement CCSDS OMM's XML
  serialization (a second, more complex parser) — scoping to KVN is this package's own choice, not
  stated by `FR-5220`'s text, and is named here as a disclosed scope-narrowing, not a silent gap. If
  a user-supplied OMM file arrives as XML, it is treated identically to any other unrecognized file
  (Design Decision 1's outright rejection) until a follow-on package adds XML support.
- **Interface-model stretch (see Interfaces Used), carried unresolved from FS-119 itself** — not
  blocking this package's own buildability, per that document's own framing.
- **Shared-helper extraction risk (`add_tle`, `elements_to_rv`).** Both extractions touch code paths
  every existing TLE-related test already exercises; Implementation Tasks 1 and 4 exist specifically
  to catch a behavior change before any new code is added on top.

## Rollback Considerations

`content/bulk_import.py` is wholly new and additive; `mean_to_true()`'s extraction is a pure
refactor with no external behavior change (reverting it merely re-inlines the same computation);
`_force_add_tle_object()`/`_force_add_omm_object()`/`bulk_import()` are new additive session-layer
surfaces beside the unchanged `add_tle()`. Reverting this package's changes removes the batch-import
capability with no effect on any existing single-object TLE/lat-long entry, any existing vignette,
or any already-force-added asset (assets already added via a bulk import become ordinary `Asset`
entries indistinguishable from a single-object `add_tle()` result — no special marker, no
data-migration concern on rollback).
