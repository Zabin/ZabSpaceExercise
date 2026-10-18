# IP-1280 — Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint

> **Package ID:** IP-1280
> **Version:** 1.0
> **Status:** 🟡 READY *(authorized 2026-09-27 by the project owner's direct instruction, MSTR-006 §3)*
> **Dependencies:** [FS-128](../../features/FS-128-variable-speed-aar-replay.md) v1.0 (`FR-7330`),
> `session/aar.py` (`IP-1070`, `VERIFIED`), `session/cells.py` (baseline, `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0078` (item B12), `BL-0119`/`BL-0120`
> (this Feature's two Open Questions), `BL-0093` (the `INT-0014` interface-stretch note)
> **Produces:** continuous, speed-adjustable timeline playback from ground truth or a fog-respecting
> single-cell viewpoint, satisfying `FR-7330` in full
> **Feature Reference:** [FS-128 — Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint](../../features/FS-128-variable-speed-aar-replay.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/session/aar.py`](../../../spacesim/session/aar.py),
> [`spacesim/session/cells.py`](../../../spacesim/session/cells.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package.*

## Package ID

IP-1280

## Title

Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint

## Objective

Add continuous, speed-adjustable timeline playback over a recorded exercise, from ground truth or a
single named cell's fog-of-war-respecting viewpoint, built entirely on `FR-7310`'s existing
point-in-time reconstruction (`state_at`/`state_at_time`) called repeatedly at successive simulated
moments.

> **This package is authorized for coding.** Per MSTR-006 §3, the project owner gave explicit
> go-ahead 2026-09-27 (batched with five sibling packages from the same Should-tier intake round).

## Feature Reference

[FS-128 — Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint](../../features/FS-128-variable-speed-aar-replay.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-7330 | Variable-speed AAR replay from truth or a single cell's viewpoint | A new playback controller repeatedly invokes `session/aar.py`'s existing `state_at_time()` at successive simulated moments (paced by the requested speed), passing each reconstructed state through `CellController`'s existing fog-of-war filter for a cell viewpoint, or through the existing no-cell ground-truth path for a truth viewpoint. |

## Architecture Components

- **C2 Session/Application Layer** (`session/aar.py`) — owns `state_at`/`state_at_time`, called
  repeatedly by this package's new playback controller; unmodified itself.
- **C2 Session/Application Layer** (`session/cells.py`, `CellController`) — owns the fog-of-war
  filter the cell-viewpoint playback path calls at each played-back moment; unmodified, reused.
- **C4 Operator Console** (`ui_web/`) — presents the playback control (speed, viewpoint selection,
  pause).

## Interfaces

`INT-0014` (AAR/Replay → Engine) — the existing interface `FR-7310`'s reconstruction already
operates through; this package's continuous playback stretches its documented shape a second way
(per `BL-0093`'s extended entry), not a new interface. `INT-0006` (Console → SessionAPI seam) — the
playback control operates through this existing interface.

## Design Decisions (resolving FS-128's Open Questions)

1. **Open Question 1 (`BL-0119`) — a mid-playback viewpoint switch continues from the same
   simulated moment under the new viewpoint; it does not restart playback.** Rationale: restarting
   would silently discard the facilitator's current position in the timeline, which is more
   surprising than continuing — this mirrors how switching god-view/view-as (`FR-4610`) already
   preserves the current simulated moment rather than resetting to session start.
2. **Open Question 2 (`BL-0120`) — a requested cell viewpoint naming a cell that did not
   participate in the recorded exercise is rejected at the request boundary, before any playback
   begins**, with a specific reason distinguishable from a generic failure — mirroring how every
   other cell-scoped request in this project rejects an invalid/nonexistent cell rather than
   silently defaulting to an empty or ground-truth view.

## Files to Create

None.

## Files to Modify

- `spacesim/session/aar.py` — a new playback-controller function/class (e.g. `PlaybackSession`)
  wrapping repeated `state_at_time()` calls at a caller-driven pace, tracking current simulated
  moment and viewpoint; switching viewpoint updates only the filter applied to subsequent calls
  (Design Decision 1), never the tracked moment.
- `spacesim/ui_web/server.py` — new routes for starting/advancing/pausing a playback session and
  selecting its speed/viewpoint, validating a requested cell viewpoint against the recorded
  exercise's actual participant list (Design Decision 2).

## Implementation Tasks

1. Write a failing test asserting playback at a non-default speed does not disturb the live
   session (reusing `FR-7310`'s existing non-disturbance guarantee), before writing the playback
   controller.
2. Write `session/aar.py`'s playback controller, reusing `state_at_time()` unmodified.
3. Write a failing test asserting a cell-viewpoint playback's state at any moment matches what
   `CellController`'s fog-of-war filter would produce for that cell at that simulated time, before
   wiring the filter in.
4. Write a failing test asserting a ground-truth-viewpoint playback's state matches the existing
   no-cell ground-truth view (`FR-6220`), before wiring that path in.
5. Write a failing test asserting a mid-playback viewpoint switch continues from the same simulated
   moment (Design Decision 1), before implementing the switch behavior.
6. Write a failing test asserting a requested cell viewpoint naming a non-participating cell is
   rejected at the request boundary (Design Decision 2), before adding the validation.
7. Re-run the full existing suite; confirm zero regressions to any existing AAR/replay test.

## Tests to Add

- `spacesim/tests/test_aar.py` — playback controller's non-disturbance guarantee; ground-truth and
  cell-viewpoint playback matching their respective existing views at sampled moments; mid-playback
  viewpoint-switch continuity.
- `spacesim/tests/test_web.py` — the new playback routes; non-participating-cell rejection.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — the playback controller is a read-only repeated invocation of an already
deterministic function, no wall-clock read or global RNG use introduced.

## Documentation Updates

- `CLAUDE.md` Code Map — `session/aar.py`'s entry gains a one-line note for the playback
  controller.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-7330`'s row's `Impl.
  Package`/`Test` cells updated from `UNASSIGNED` to `IP-1280`/the named test files.
- `docs/design/05-interface-control-document.md` — `INT-0014`'s prose updated to note this
  package's playback-mode stretch alongside `FR-7410`/`FR-7420`'s existing export-format stretch
  (citation-only, per `BL-0093`'s own tracked note — not an ICD redesign).
- `docs/features/FS-128-variable-speed-aar-replay.md` — `Referenced By` metadata gains this
  package's link.
- `docs/pipeline/backlog.md` — `BL-0119`/`BL-0120` flip `DONE` (resolved by Design Decisions 1-2
  above).

## Definition of Done

- [ ] Cell-viewpoint playback matches `CellController`'s fog-of-war filter at every sampled moment.
- [ ] Ground-truth playback matches the existing no-cell ground-truth view.
- [ ] Playback at a non-default speed does not disturb the live session.
- [ ] A mid-playback viewpoint switch continues from the same simulated moment.
- [ ] A non-participating cell viewpoint is rejected at the request boundary.
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Every new test named above exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Independently confirm the playback controller never bypasses `CellController`'s fog-of-war
  filter for a cell-viewpoint request, by direct code read.

## Dependencies

- **Upstream:** [FS-128](../../features/FS-128-variable-speed-aar-replay.md) v1.0 (approved, `✅
  Ready for implementation planning`); `session/aar.py` (`IP-1070`, `VERIFIED`); `session/cells.py`
  (baseline, `VERIFIED`).
- **Downstream:** none.
- **Build-sequencing:** independent of every other package in this batch (no shared file).

## Risks

- **`INT-0014` interface-stretch, already tracked (`BL-0093`).** Not a new risk this package
  introduces — folded into the existing tracked finding rather than filed separately.

## Rollback Considerations

The playback controller is additive, built entirely on existing, unmodified reconstruction/
filtering functions; removing the new controller/routes fully removes this package's capability
with no data-migration concern.
