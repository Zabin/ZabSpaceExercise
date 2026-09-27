# IP-1260 — Per-Asset Telemetry CSV Export Over a Time Span

> **Package ID:** IP-1260
> **Version:** 1.0
> **Status:** 🔴 BLOCKED *(fully specified; not authorization-blocked — blocked on a dependency
> package reaching `VERIFIED`, see Dependencies)*
> **Dependencies:** [FS-126](../../features/FS-126-telemetry-csv-export.md) v1.0 (`FR-2320`),
> `engine/telemetry.py` (`VERIFIED` baseline code), [IP-1062](IP-1062-condition-triggered-injects-and-new-effects.md)
> (`FR-4430`'s `anomaly` effect — `COMPLETE`, **not yet `VERIFIED`** — this package's own
> Acceptance Criterion 1 requires it)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0075` (item B9), `BL-0117` (this
> Feature's one Open Question)
> **Produces:** a fog-of-war-respecting, per-asset telemetry CSV export over a requested time span,
> satisfying `FR-2320` in full — pending `IP-1062` reaching `VERIFIED`
> **Feature Reference:** [FS-126 — Per-Asset Telemetry CSV Export Over a Time Span](../../features/FS-126-telemetry-csv-export.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/telemetry.py`](../../../spacesim/engine/telemetry.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Per this skill's own `READY`-requires-`VERIFIED`-dependencies rule: this
package's Acceptance Criterion 1 (export reflects an active `FR-4430` anomaly-inject perturbation)
depends on `IP-1062`'s `anomaly` effect, which is currently `COMPLETE` but not yet `VERIFIED`
(awaiting `09-package-verification` in a fresh session, per the same-session-verification-
exclusion rule). This package is therefore `BLOCKED`, not `READY`, even though it is fully
specified and its own code has no other blocker — it is safe to author now (so `08` can begin the
moment `IP-1062` clears) but not safe to mark eligible for implementation yet.*

## Package ID

IP-1260

## Title

Per-Asset Telemetry CSV Export Over a Time Span

## Objective

Export a requesting cell's own pass-gated telemetry channel values for a named Asset and simulated
time span as CSV, reusing the existing telemetry-sampling function and fog-of-war filter — never
ground truth, never another cell's view.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins. Independent of authorization, this package cannot begin
> `08-code-implementation` until `IP-1062` reaches `VERIFIED` (see Dependencies).

## Feature Reference

[FS-126 — Per-Asset Telemetry CSV Export Over a Time Span](../../features/FS-126-telemetry-csv-export.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-2320 | Per-asset telemetry CSV export over a time span | A new route reads `engine/telemetry.py`'s existing sampled-value function across a requested Asset/cell/time span, applying the requesting cell's existing fog-of-war filter (`FR-6210`), and serializes the result as CSV. |

## Architecture Components

- **C1 Simulation Engine** (`engine/telemetry.py`) — owns the sampled-value function this export
  reuses directly; unmodified.
- **C2 Session/Application Layer** (`session/manager.py`) — owns deriving the sampled-and-filtered
  export rows, applying the existing fog-of-war filter.
- **C4 Operator Console** (`ui_web/`) — exposes the new export route, cell-scoped like every other
  cell-scoped route.

## Interfaces

`INT-0006` (Console → SessionAPI seam) — the export request operates through this existing
interface. `INT-0007` (CellController → Engine Custody) — the fog-of-war-filtered read operates
through this existing interface, per `FR-2320`'s own citation of `FR-6210`.

## Design Decisions (resolving FS-126's Open Question)

1. **Open Question 1 (`BL-0117`) — a requested time span partially outside the recorded session
   range is silently clamped to the valid range; a wholly out-of-range span is rejected outright.**
   Rationale: this reuses `FS-121`/`IP-1210`'s own existing, already-implemented precedent for the
   structurally identical question in `session/ephemeris.py`'s `_clamp_or_reject()` — the
   established pattern in this codebase for "requested span vs. recorded range" across every export
   capability, avoiding a second, inconsistent rule for this Feature alone.

## Files to Create

None.

## Files to Modify

- `spacesim/session/manager.py` — a new read method (e.g. `telemetry_export(asset_id, cell,
  t1, t2) -> list[TelemetryRow]`) sampling `engine/telemetry.py`'s existing function across the
  requested span, applying the requesting cell's fog-of-war filter, and applying `FS-121`'s
  existing `_clamp_or_reject()` range-handling pattern (Design Decision 1).
- `spacesim/ui_web/server.py` — a new cell-scoped route exposing the CSV export, mirroring the
  existing telemetry-endpoint cell-scoping convention.

## Implementation Tasks

1. Write a failing test asserting an Asset with an active `anomaly` inject effect (`FR-4430`)
   perturbing one telemetry channel shows the perturbation at the correct simulated times in the
   exported rows, before writing `telemetry_export()`. **Do not start this task until `IP-1062`
   reaches `VERIFIED`.**
2. Write `session/manager.py::telemetry_export()`, reusing `engine/telemetry.py`'s existing sampled-
   value function directly (no parallel computation).
3. Write a failing test asserting a different cell's export of the same Asset never shows data that
   cell's own fog-of-war filter would not otherwise expose, before wiring the fog-of-war filter in.
4. Write a failing test for Design Decision 1's clamp/reject behavior (partially out-of-range span
   clamped; wholly out-of-range span rejected), reusing `FS-121`/`IP-1210`'s own existing test
   parametrization shape.
5. Add the new export route.
6. Re-run the full existing suite; confirm zero regressions to any existing telemetry test.

## Tests to Add

- `spacesim/tests/test_telemetry.py` (or `test_session_features.py`) — `telemetry_export()` reflects
  an active anomaly-inject perturbation at the correct times; fog-of-war-filtered per requesting
  cell; clamp/reject behavior for out-of-range spans.
- `spacesim/tests/test_web.py` — the new route's cell-scoping matches every other cell-scoped
  telemetry route.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — no wall-clock read or global RNG use introduced.

## Documentation Updates

- `CLAUDE.md` Code Map — `engine/telemetry.py`, `session/manager.py` entries each gain a one-line
  note for the export.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-2320`'s row's `Impl.
  Package`/`Test` cells updated from `UNASSIGNED` to `IP-1260`/the named test files.
- `docs/features/FS-126-telemetry-csv-export.md` — `Referenced By` metadata gains this package's
  link.
- `docs/pipeline/backlog.md` — `BL-0117` flips `DONE` (resolved by Design Decision 1 above).

## Definition of Done

- [ ] Export reflects an active `anomaly`-inject perturbation at the correct simulated times.
- [ ] Export is fog-of-war-filtered per requesting cell; a different cell's export never leaks data.
- [ ] A partially out-of-range span is clamped; a wholly out-of-range span is rejected.
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Every new test named above exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Independently confirm the export route calls `engine/telemetry.py`'s existing function
  directly (no parallel/duplicated computation that could drift from the live JSON endpoint).

## Dependencies

- **Upstream:** [FS-126](../../features/FS-126-telemetry-csv-export.md) v1.0 (approved, `✅ Ready
  for implementation planning`); `engine/telemetry.py` (baseline, `VERIFIED`); **[IP-1062](IP-1062-condition-triggered-injects-and-new-effects.md)
  (`COMPLETE`, not yet `VERIFIED`) — this package's own Acceptance Criterion 1 requires the
  `anomaly` effect it introduces, so this package stays `BLOCKED` until `IP-1062` reaches
  `VERIFIED`**, per this skill's own eligibility rule (a dependency merely `COMPLETE` is not
  sufficient for `READY`).
- **Downstream:** none.
- **Build-sequencing:** blocked on `09-package-verification` clearing `IP-1062` in a fresh session;
  otherwise independent of every other package in this batch (no shared file).

## Risks

- **Dependency risk (the dominant risk for this package).** If `IP-1062`'s own verification surfaces
  a material finding against the `anomaly` effect's shape, this package's Acceptance Criterion 1
  (and its own test) may need revisiting before it can proceed.
- **Fog-of-war regression risk.** A new export route must reuse the console's existing cell-scoping
  mechanism, not introduce a parallel one.

## Rollback Considerations

The export is additive and read-only over existing `engine/telemetry.py` state; removing the new
method/route fully removes this package's capability with no data-migration concern.
