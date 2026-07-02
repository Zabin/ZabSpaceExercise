# IP-1010 — Mission Planning: Dry-Run Preview & Window/Δv Display

> **Package ID:** IP-1010
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-101
> **Referenced By:** IP-1020 (shares the validate path), IP-1050/IP-1051 (renders this package's preview surface), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the planning-preview surface IP-1050/IP-1051's console renders
> **Feature Reference:** [FS-101 — Mission Planning](../../features/FS-101-mission-planning.md)
> **Supersedes:** [`docs/implementations/IMP-101A-mission-planning.md`](../../implementations/IMP-101A-mission-planning.md) (content re-derived and re-organized under this package's template; see that file's superseded-by banner)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py), [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-1010

## Title

Mission Planning — Dry-Run Preview & Window/Δv Display

## Objective

Give a cell a read-only, no-commitment preview of a candidate order — whether it would validate,
when its access window opens/closes, and (for maneuvers) its Δv cost — across all six maneuver
entry modes, so the operator learns the domain constraint blocking a plan rather than receiving a
bare pass/fail. This is the code-level expression of the project's plan-first invariant
(`CLAUDE.md` §"Load-bearing invariants" #4) at the pre-commit stage; FS-102/IP-1020 owns the
post-commit lifecycle of the same order once issued.

**Situation: this capability is already implemented, tested, and in production use.** This package
is a build-ready specification of *existing* code (module/function/line references verified against
the current `spacesim/` tree), not a proposal — it exists so a future maintenance or extension task
against this capability has one canonical, current reference instead of re-deriving it from source.

## Feature Reference

[FS-101 — Mission Planning](../../features/FS-101-mission-planning.md)

## Requirements Covered

FS-101's own "Requirements Implemented" field states no FR/NFR explicitly cites this Feature ID —
a documented traceability gap (FS-101 §"Requirements Implemented", Phase 8 review item per
MSTR-006 §7). The following FR/NFR leaves are covered *functionally* by this package's code, per
the Requirements Traceability Matrix's file-level mapping (`docs/requirements/03-requirements-
traceability-matrix.md`, "Reverse index — Requirement → Implementation Package"), since this
package's files (`engine/orders.py`, `engine/access.py`) are exactly the files that matrix cites:

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-3110 | Plan-first order issuance with delivery path | `dry_run()` mirrors the identical `_plan()` path `issue()` uses (§System Architecture below) |
| FR-3410 | Execute-time re-validation (ownership/window/resource/ROE/track gate) | The same `_validate()` (`orders.py:323`) both preview and commit call |
| FR-1220 | Access-window computation across six channels | `_next_window()` (`orders.py:386`) calls the real `AccessProvider.windows()` (`access.py:107`) |
| FR-1310 | Impulsive maneuver Δv-budget enforcement | `compute_maneuver()` (`inprocess.py:314`) previews the same six-entry-mode cost `_h_maneuver` charges on commit |
| NFR-1600 | Robustness to invalid input | `_validate()`'s `tuple[bool, str]` contract rejects invalid orders with a named reason, never a crash |
| NFR-1500 | Determinism (engine-wide) | `dry_run()` schedules/books nothing, so it cannot introduce replay divergence (§ Definition of Done) |

## Architecture Components

- **C1 Simulation Engine** (`spacesim/engine/`) — `OrderSystem` (`orders.py`), `AccessProvider`
  (`access.py`), `engine/maneuver.py` (six-entry-mode Δv computation).
- **C2 Session / Application Layer** (`spacesim/session/`) — `InProcessSession.validate_order()`,
  `compute_maneuver()`, `preview_consequence()` (`inprocess.py`).
- **C4 Operator Console (Presentation)** — consumes this package's preview output (pre-disabled
  buttons, window/Δv display); the console's own UI code is out of this package's scope.

## Interfaces

Per `docs/design/05-interface-control-document.md` and FS-101's verified Related Interfaces field:
**INT-0006** (Console → SessionAPI seam, the transport this preview surface rides), **INT-0008**
(SessionManager → Simulation Engine Clock/Scheduler/EventLog/OrderSystem, where `dry_run()` lives).

## Files to Create

None — this capability is already implemented. (See "Reference files" below.)

## Files to Modify

None — this package proposes no code changes; it documents the current, shipped implementation.

### Reference files (implement this capability; not modification targets of this package)

- `spacesim/engine/orders.py` — `OrderSystem.dry_run()` (`:136`), `OrderSystem.issue()` (`:128`),
  the shared `_plan(order, commit)` (`:147`), `_validate()` (`:323`), `_next_window()` (`:386`).
- `spacesim/session/inprocess.py` — `validate_order()` (`:186`), `compute_maneuver()` (`:314`),
  `preview_consequence()` (`:466`), the `_locked_read()` context manager (`:49`).
- `spacesim/engine/access.py` — `AccessProvider.windows()` (`:107`), the real bisection-based
  geometry both preview and commit query.
- `spacesim/engine/maneuver.py` — the six-entry-mode (eci/lvlh/finite_burn/target_coe/hohmann/
  plane_change) Δv computation `compute_maneuver()` and the committed handler both call.

## Implementation Tasks

All tasks below are **already complete** (as-built record, not a work plan):

1. ✅ Implement a single shared `_plan(order, commit: bool)` method so preview and commit can never
   diverge into two maintained code paths (`orders.py:147`).
2. ✅ Implement `dry_run()` as the `commit=False` branch: validate → compute window/cost → return a
   populated `Order`, booking/scheduling/registering nothing (`orders.py:136`).
3. ✅ Implement `_validate()` returning `tuple[bool, str]` so a rejection carries a named reason
   (no window / regime mismatch / insufficient resource), not a bare boolean (`orders.py:323`).
4. ✅ Expose `dry_run()` at the session layer as `validate_order()` under the same read-lock every
   other read uses, so a preview cannot race a concurrent mutation (`inprocess.py:186`, `:49`).
5. ✅ Expose Δv-cost preview (`compute_maneuver()`) and kinetic-consequence preview
   (`preview_consequence()`) as the two console-facing preview entry points beyond plain
   validate/window (`inprocess.py:314`, `:466`).

## Tests to Add

None — already covered by the existing suite (this package documents tested code, it does not add
new test obligations):

- `dry_run()`/`issue()` parity is implicitly exercised in any test asserting a preview matches the
  eventual commit (order-system test suite).
- The Phase-1 determinism property test (`spacesim/tests/test_determinism.py`) guarantees `_plan()`'s
  commit branch is replay-exact, which transitively guarantees the preview branch (identical code
  path up to the `commit` flag) introduces no divergence.

## Documentation Updates

- This package supersedes [`docs/implementations/IMP-101A-mission-planning.md`](../../implementations/IMP-101A-mission-planning.md)
  (superseded-by banner added there per the migration described in
  [`00-master-build-plan.md`](../00-master-build-plan.md) §"Relationship to the prior `docs/implementations/` corpus").
- `ROADMAP.md`'s "Theme: Implementation Packages" section updated to point at this package.
- No other document requires an update — FS-101's existing `Referenced By` field pointing at
  `IMP-101A` remains a valid pointer to an extant (now-superseded, not deleted) document.

## Definition of Done

- [x] `dry_run()` produces no `WorldState` mutation under any input (verified: no booking/scheduling
  call exists on the `commit=False` branch of `_plan()`).
- [x] `dry_run()` and `issue()` share one `_plan()` implementation — no parallel preview-only
  validate/window logic exists anywhere in `orders.py`.
- [x] A rejected preview names the specific blocking constraint via `_validate()`'s `str` reason.
- [x] Δv preview covers all six maneuver entry modes, matching the committed handler's computation.
- [x] Window preview is computed via the same `AccessProvider.windows()` bisection geometry the
  engine gates execution on — no separate display-only estimator exists.
- [x] The Phase-1 determinism property test is green on the branch (permanent gate, `CLAUDE.md`).

## Verification Checklist

- [x] `orders.py:136` (`dry_run`), `:147` (`_plan`), `:323` (`_validate`), `:386` (`_next_window`)
  read and confirmed against the current tree.
- [x] `inprocess.py:186` (`validate_order`), `:314` (`compute_maneuver`), `:466`
  (`preview_consequence`), `:49` (`_locked_read`) read and confirmed against the current tree.
- [x] `spacesim/tests/test_determinism.py` present and part of `testpaths` (per `CLAUDE.md` build
  commands: `python3 -m pytest spacesim/tests/test_determinism.py`).
- [x] No FR/NFR explicitly cites FS-101 (confirmed absence in `docs/requirements/01-functional-
  requirements.md` and the RTM) — recorded above as a traceability gap, not silently closed.

## Dependencies

- **Upstream:** None — this package's code depends only on already-shipped `engine/access.py` and
  `engine/maneuver.py`.
- **Downstream:** IP-1020 (Command Scheduling) shares the same `_plan()`/`_validate()` code path for
  the commit side; IP-1050/IP-1051 (Spacecraft Operations) render this package's preview output in
  the operator console.
- **Build-sequencing:** None — already shipped; no ordering constraint against any other package in
  this Master Build Plan.

## Risks

- Course-of-action comparison (planning and weighing *multiple* candidate plans against each other,
  [R311](../../research/encyclopedia/R311-course-of-action-analysis.md) §5) is an explicit FS-101
  non-goal; a future author treating it as in-scope without a deliberate scope decision (a new
  Feature Spec ID or an FS-101 revision) would silently expand this package's boundary.
- The FR/NFR traceability gap noted above (no requirement explicitly cites FS-101) means a future
  requirements change could alter this feature's obligations without an automatic cross-reference
  surfacing the conflict; Phase 8 traceability review (MSTR-006 §7) is the mechanism that should
  close this, not this package.

## Rollback Considerations

This is already-shipped, tested code; "rollback" here means the surface a maintainer would need to
revert if a regression were found, not an undeployment plan:

- The rollback surface is confined to `spacesim/engine/orders.py` (`_plan`, `dry_run`, `_validate`,
  `_next_window`) and `spacesim/session/inprocess.py` (`validate_order`, `compute_maneuver`,
  `preview_consequence`) — no persisted schema or save-file format is touched by this capability
  (`Order` carries no separate "preview" variant, per FS-101's Data Model Changes field), so a
  revert requires no data migration.
- Reverting this code would also revert IP-1020's commit path, since both share `_plan()` — a
  targeted rollback of preview-only behavior without touching commit behavior is not possible given
  the single-shared-path design, and should not be attempted (it would reintroduce the
  preview/commit divergence risk this design deliberately eliminates).
