# FS-101 — Mission Planning

> **Document ID:** FS-101
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-001](../domains/DOM-001-training-framework.md), [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md), [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md), [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md)
> **Referenced By:** [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md), [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md), [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md), [R311](../research/encyclopedia/R311-course-of-action-analysis.md), [IMP-101A](../implementations/IMP-101A-mission-planning.md)
> **Produces:** the planning surface consumed by [FS-105](FS-105-spacecraft-operations.md) once a plan is committed
> **Feature Mapping:** FS-101 (this document)
> **Related Topics:** [DOM-001](../domains/DOM-001-training-framework.md) §7, [R311](../research/encyclopedia/R311-course-of-action-analysis.md) (course-of-action analysis, candidate future scope)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template; it supersedes this
file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per
MSTR-006 §5.*

## Feature ID

FS-101

## Title

Mission Planning

## Purpose

Mission Planning is the capability by which a cell formulates and previews orders **before**
committing them — the UI-and-workflow expression of the project's load-bearing "plan-first"
invariant ([`CLAUDE.md`](../../CLAUDE.md) §"Load-bearing invariants" #4): operators plan commands
that execute at the next valid access window and task sensors for collection; they never act
instantly on perfect knowledge. FS-101 is the specification for that planning surface, independent
of which specific bus/payload verb is being planned (that detail belongs to
[FS-105](FS-105-spacecraft-operations.md)).

## Scope

In scope: order drafting, pre-commit validation/preview (the "why can't I?" feedback loop), window
visibility (when will this plan actually execute), and Δv/resource-cost preview for maneuver plans.

Out of scope: the actual execution-time behavior of a committed order (owned by
[FS-102](FS-102-command-scheduling.md)), and the console chrome for non-planning operator actions
([FS-105](FS-105-spacecraft-operations.md)). Also explicitly out of scope (non-goals): adding a new
effect category or gameplay mechanic — this feature is a workflow layer over existing order/window
primitives, not a new mechanic; and course-of-action comparison (planning and weighing *multiple*
candidate plans against each other) — [R311](../research/encyclopedia/R311-course-of-action-analysis.md)
§5 names a future COA-comparison feature as a candidate extension under FS-101, not a requirement of
this spec.

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

## User Workflows

The source document does not state these as step-by-step role-scoped sequences; it states them as
capability requirements. Restated as workflow shape, faithfully to that content:

- A cell (Blue or Red operator) drafts a candidate order (maneuver, tasking, or engagement plan)
  without committing it.
- The cell requests a preview of that candidate: whether it would validate, when its access window
  opens/closes, and (for maneuver plans) its Δv/resource cost — across whichever of the six entry
  modes (eci / lvlh / finite_burn / target_coe / hohmann / plane_change) is in use.
- If the candidate fails validation, the cell receives an explanation of *which* constraint blocked
  it (no window, regime mismatch, insufficient resource), not just a bare failure.
- The cell commits the plan once satisfied with the preview, handing it to
  [FS-102](FS-102-command-scheduling.md)'s execution lifecycle (out of scope for this feature).

## System Behaviour

- **Plans must be previewable without commitment.** A cell must be able to see whether a candidate
  order would validate, when its access window opens/closes, and what it would cost, without that
  preview being indistinguishable from actually issuing the order. This is a read-only operation
  with no World-state side effect.
- **Plans must reflect real regime and propagator constraints, not idealized reachability.** Per
  [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md) §6, a planning UI must
  not offer an action against a target the orbital regime makes physically unreachable, nor imply
  continuous access where the underlying geometry is windowed.
- **Maneuver plans must preview real Δv cost across all supported entry modes.** Per
  [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md) §5, a planning UI must
  surface Δv-economy honestly for whichever of the six entry modes the operator is using —
  collapsing them to a single generic "maneuver" estimate would hide a real operational tradeoff.
- **Window display must reflect genuine sampled/bisected geometry.** Per
  [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) §5, a planning UI
  showing "next window" or "window closes in" must be driven by the same access computation the
  engine uses to gate execution — not a separately-computed or idealized continuous-access estimate
  that could disagree with what actually happens at execution time.
- **A rejected/invalid plan must explain why, not just that it failed.** Consistent with the
  pre-disabled-button pattern ([DOM-007](../domains/DOM-007-human-factors-framework.md) §4), the
  planning surface should tell the operator *which* constraint blocked the plan (no window, regime
  mismatch, insufficient resource) so the operator learns the domain constraint, not just "no."

Edge case (per the source document's non-goals): course-of-action comparison across multiple
candidate plans is not part of this behavior contract in this version.

## Subsystem Responsibilities

The source document does not provide a per-subsystem responsibility table. It names the
preview/validation path as sharing the engine layer's `dry_run()` contract (see Performance
Considerations) but does not assign rows to named subsystems beyond that. Flagged as an Open
Question below.

## Interfaces Used

The source document does not cite ICD interface IDs directly. Per the verified mapping for this
Feature: INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control), INT-0003 (in-app
scenario builder), and INT-0011 (SessionManager → Content & Data, vignette/template load) — together
with the `SessionManager` module named in [`CLAUDE.md`](../../CLAUDE.md), since FS-101 is mission/
vignette planning. These are carried forward from the verified Related Interfaces mapping (field 21
below); the source document itself does not state which interface each workflow step crosses in
more granular terms. Flagged as an Open Question below.

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. Flagged as an Open
Question below.

## State Changes

The source document states that the preview/validation path must have "no World-state side effect"
— i.e., previewing a plan creates or transitions no persistent or session state. The source document
does not otherwise describe what state a *committed* plan creates (that is attributed to
[FS-102](FS-102-command-scheduling.md), out of scope here).

## Error Handling

A rejected/invalid plan must surface *which* constraint blocked it — no window, regime mismatch, or
insufficient resource — rather than a bare failure, per the pre-disabled-button pattern
([DOM-007](../domains/DOM-007-human-factors-framework.md) §4). The source document does not
enumerate a complete failure-mode table beyond these three named constraint categories.

## Performance Considerations

- **Replay-safety.** The preview/validation path must be a read-only mirror of the real
  validate→window path (the same contract `dry_run()` already provides at the engine layer per
  [`CLAUDE.md`](../../CLAUDE.md)'s order-system description) — it must schedule, register, or book
  nothing.

## Security Considerations

Not addressed in the source document — no existing content to carry forward. Flagged as an Open
Question below.

## Acceptance Criteria

Derived from the source document's capability requirements §3, restated as checkable conditions:

- A candidate order can be previewed (validation, window open/close, cost) without any resulting
  World-state mutation.
- The planning UI never offers an action against a target the orbital regime makes physically
  unreachable.
- The planning UI never implies continuous access where the underlying geometry is windowed.
- For maneuver plans, Δv cost is shown distinctly per entry mode (eci / lvlh / finite_burn /
  target_coe / hohmann / plane_change), not collapsed to one generic estimate.
- "Next window" / "window closes in" displays are computed from the same access-window logic the
  engine uses to gate execution.
- A rejected plan's UI response names the specific blocking constraint (no window / regime mismatch
  / insufficient resource).

## Verification Plan

The source document does not state a Verification Method (Test/Demonstration/Analysis/Inspection)
per criterion. Given the stated replay-safety requirement (a read-only mirror of the engine's
`dry_run()` contract) and the determinism invariant this project treats as load-bearing
([`CLAUDE.md`](../../CLAUDE.md) §"Load-bearing invariants" #1), Test is the implied method for the
no-side-effect and window-computation-parity criteria, but this is inferred from project-wide
convention, not stated in the source document itself. Flagged as an Open Question below.

## Dependencies

[DOM-001](../domains/DOM-001-training-framework.md), [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md),
[R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md),
[R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) (per the existing
metadata block's Dependencies field). [FS-102](FS-102-command-scheduling.md) and
[FS-105](FS-105-spacecraft-operations.md) are named in the source document as the features this
feature's output feeds into / lives inside, not as upstream dependencies of FS-101 itself.

## Risks

The source document does not state risks explicitly under that heading. The following are
restated faithfully from material the document does discuss as constraints/cautions:

- If `training_objectives:` is not made an explicit vignette schema field, the educational-value
  claim in the source document (exercising the "plan against real constraints" competency) remains
  implicit in `intro_brief` prose rather than a structured, checkable artifact — a traceability risk
  noted in [DOM-001](../domains/DOM-001-training-framework.md) §8.
- Course-of-action comparison ([R311](../research/encyclopedia/R311-course-of-action-analysis.md)
  §5) being treated as in-scope by a future author without a deliberate scope decision (new FS ID or
  FS-101 revision) is named as a risk to avoid in the source document's non-goals.

## Open Questions

- Whether `training_objectives:` should become an explicit vignette schema field (currently implicit
  in `intro_brief` prose) is flagged in [DOM-001](../domains/DOM-001-training-framework.md) §8 as
  candidate scope for an FS-101-derived Implementation Package — not decided in this spec.
- Course-of-action comparison ([R311](../research/encyclopedia/R311-course-of-action-analysis.md)
  §5) is named as a candidate future extension, not committed scope; if pursued, it should be
  evaluated as either an FS-101 revision or a new FS ID rather than assumed.
- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-101; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- The source document does not assign a per-subsystem Subsystem Responsibilities table; which named
  subsystem(s) beyond `SessionManager`/the engine's order system own each piece of planning-preview
  behavior is unresolved here.
- The source document does not state granular Interfaces Used at the workflow-step level beyond the
  verified INT-0002/INT-0003/INT-0011 mapping; whether additional interfaces are touched is
  unresolved.
- The source document does not address Data Model Changes; whether mission-planning preview state
  (e.g., a draft-plan representation) requires any Domain Model addition is unresolved.
- The source document does not address Security Considerations for this feature; whether fog-of-war
  or trust-boundary constraints apply to plan preview (e.g., can a cell preview a plan against a
  target it has no custody on) is unresolved.
- The source document does not state a Verification Method per acceptance criterion; the Test method
  assumed above for replay-safety/window-parity criteria is inferred from project-wide convention,
  not the source document.

## Related ADRs

ADR-0005 (plan-first commanding model) — `docs/architecture/adr/ADR-0005-plan-first-commanding.md`;
ADR-0027 (scenario-authoring boundary); ADR-0007 (content as data).

## Related Interfaces

INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control); INT-0003 (in-app scenario
builder); INT-0011 (SessionManager → Content & Data, vignette/template load) — per
`docs/design/05-interface-control-document.md`.
