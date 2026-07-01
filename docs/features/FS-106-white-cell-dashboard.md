# FS-106 — White Cell Dashboard

> **Document ID:** FS-106
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md), [DOM-001](../domains/DOM-001-training-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md)
> **Referenced By:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md), [IMP-106A](../implementations/IMP-106A-white-cell-dashboard.md)
> **Produces:** the facilitation surface [FS-108](FS-108-inject-authoring.md) (candidate) would extend
> **Feature Mapping:** FS-106 (this document)
> **Related Topics:** [FS-107](FS-107-after-action-review.md) (White-only AAR controls), [DOM-002](../domains/DOM-002-assessment-framework.md) §6 (facilitator-rubric
> assessment mode, hosted here)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-106

## Title

White Cell Dashboard

## Purpose

The White Cell Dashboard is the facilitator's console: unrestricted god-view across both cells,
inject authoring/scheduling, clock/pacing authority, and session administration. Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §1,
it must trace back to White Cell's role as instructional designer ([MSTR-003](../master/MSTR-003-educational-philosophy.md) §7), not a neutral
referee — every capability in this spec exists to let a facilitator *shape* the learning experience
in real time, not merely observe it.

## Scope

In scope: god-view rendering (both cells' belief + ground truth simultaneously), the inject
build/schedule panel, clock pause/resume and AAR-adjacent rewind/undo/branch controls, session
discovery/save-resume/pop-out layout management, and Red-doctrine-preset selection/hand-tuning.
Out of scope: the AAR replay/scrub instrument itself ([FS-107](FS-107-after-action-review.md) — though White-only controls for it
are hosted in this dashboard), the content of specific inject templates (vignette/scenario content),
and an inject-authoring UX upgrade ([FS-108](FS-108-inject-authoring.md), a separate, currently-candidate spec).

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

## User Workflows

- The White Cell facilitator opens the god-view, observing both cells' belief states and ground
  truth simultaneously without granting either cell additional ground-truth access.
- The facilitator selects an inject template from the existing `inject_library.yaml` five-template
  set, edits its parameters as JSON, and schedules it for Now / +seconds / absolute-UTC delivery.
- The facilitator pauses or resumes the exercise clock — this applies to every connected client
  identically; there is no per-tab negotiation.
- The facilitator rewinds/undoes/branches a replay point from this dashboard's clock-control
  surface (the AAR instrument itself lives in [FS-107](FS-107-after-action-review.md)).
- The facilitator saves, resumes, or shares a session URL; opens pop-out layout windows to spread
  the console across multiple monitors.
- The facilitator views and adjusts the Red doctrine preset (switching presets or hand-tuning
  parameters mid-exercise for pacing reasons).
- The facilitator observes mission-set/campaign sequencing, including which vignette in the
  sequence is active.
- The facilitator observes the assess beat across both cells simultaneously ([R106](../research/encyclopedia/R106-mission-operations.md) §5) — a
  perspective [FS-105](FS-105-spacecraft-operations.md)'s per-cell console does not provide.

## System Behaviour

- **Must expose unrestricted god-view without granting Red/Blue any new ground-truth access.** Per
  [DOM-003](../domains/DOM-003-white-cell-framework.md) §3, any new god-view-only capability is acceptable; any capability that would let
  Red/Blue access ground truth through this dashboard is a fog-of-war violation regardless of
  framing.
- **Inject authoring must work against the existing `inject_library.yaml` mechanism, not duplicate
  it.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §4, the dashboard exposes the five reusable templates with editable-JSON +
  Now/+seconds/absolute-UTC scheduler; the inject *execution* path is engine-side and out of scope
  to re-implement.
- **Clock/pacing controls must remain a single point of authority.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §5, pause/resume
  and rewind/undo/branch must stay White-only and apply identically to every connected client — no
  per-tab pacing negotiation (consistent with ADR-0016, single point of time control).
- **Session administration is a facilitation concern, not a generic platform concern.** Per
  [DOM-003](../domains/DOM-003-white-cell-framework.md) §6, save/resume, session discovery, and pop-out layout decisions should be evaluated
  against facilitation needs (multi-week course continuity, classroom multi-monitor display) rather
  than treated as infrastructure plumbing.
- **Red-doctrine-preset visibility and control is a tooling requirement, not optional.** Per
  [DOM-003](../domains/DOM-003-white-cell-framework.md) §7, the facilitator needs visibility into which preset drives Red and the ability to
  switch or hand-tune it mid-exercise — an unconvincing or passive Red undermines training per
  [R308](../research/encyclopedia/R308-red-teaming-methodology.md).
- **Mission-set/campaign sequencing must be visible.** Per [R301](../research/encyclopedia/R301-campaign-design.md) §5, the facilitator must be able
  to see which vignette in a mission-set sequence is active, even though full campaign-progression
  tracking is out of this spec's scope.
- **The assess beat must be visible from White's cross-cell vantage point.** Per [R106](../research/encyclopedia/R106-mission-operations.md) §5, unlike
  [FS-105](FS-105-spacecraft-operations.md)'s per-cell plan/task beats, this dashboard's distinct contribution is the assess beat
  viewed across both cells at once.
- **Authority-tier statement ([DOM-003](../domains/DOM-003-white-cell-framework.md) §8).** This spec touches all four authority tiers:
  visibility (god-view), inject, clock, and administration. It confirms it grants Red/Blue no new
  god-view access; every capability described here is additive to White Cell's existing authority,
  not a back door into either cell's fog-of-war boundary.

## Subsystem Responsibilities

The source document does not provide a per-subsystem breakdown. Per [`CLAUDE.md`](../../CLAUDE.md): `SessionManager`
owns clock control (pause/resume, rewind/undo, `set_clock`/`catch_up`); `redai.py` owns Red
doctrine preset selection; `InProcessSession.inject_library()` owns inject execution; `aar.py`
provides the replay/branch surface invoked from this dashboard. The source document does not assign
responsibilities to these components in a formal table. Flagged as an Open Question below.

## Interfaces Used

Per the verified mapping for FS-106: INT-0002 (White Cell Facilitator ↔ Operator Console, exercise
control) and INT-0003 (in-app scenario builder) — per `docs/design/05-interface-control-document.md`.
The source document does not itself cite ICD interface IDs; these are carried forward from the
verified Related Interfaces mapping (field 21).

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. The dashboard consumes
existing session state without the source document specifying new Domain Model entities. Flagged as
an Open Question below.

## State Changes

- Clock transitions (running/paused, rate changes) propagate to all connected clients via the
  server-authoritative lazy-clock mechanism (ADR-0014).
- Inject scheduling commits an inject to the session's inject queue; the inject executes at the
  scheduled sim time via `WorldState` direct mutation (INT-0016, per the ICD).
- Red doctrine preset changes take effect immediately for the AI-Red session-layer feature
  (ADR-0021).
- Session save/resume transitions are round-trip operations (INT-0012 per the ICD).

## Error Handling

- Clock authority conflicts (multiple tabs attempting simultaneous pacing changes) are prevented by
  the server-authoritative single-clock model (ADR-0016) and per-session RLock (ADR-0014).
- The source document does not enumerate failure modes for inject scheduling, save/resume, or
  pop-out layout beyond these architectural constraints.

## Performance Considerations

- **Single point of time control.** All clock transitions must apply identically and simultaneously
  across all connected clients — no per-tab divergence. This is an architectural invariant (ADR-0016
  and ADR-0014), not a performance target in the ordinary sense.
- **Human factors.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §3, the god-view's role is instructional — the facilitator is
  shaping learning, not merely observing — and the dashboard's design must reflect this purpose.

## Security Considerations

- The dashboard must not expose any capability that grants Red/Blue ground-truth access — this is
  the single most critical invariant for this feature ([DOM-003](../domains/DOM-003-white-cell-framework.md) §3).
- The LAN trust model (ADR-0015) applies to all sessions: the cell selector is client-side trust,
  and the dashboard's god-view is one of the no-cell ground-truth endpoints. The source document
  does not go beyond this statement.

## Acceptance Criteria

Derived from the source document's capability requirements, restated as checkable conditions:

- God-view renders both cells' belief states and ground truth simultaneously without modifying
  either cell's fog-of-war-filtered view.
- Inject authoring works against the existing `inject_library.yaml` five-template set with
  editable-JSON + Now/+seconds/absolute-UTC scheduling; no duplicate inject-execution path exists.
- Clock pause/resume and rewind/undo/branch controls are White-only and apply to all connected
  clients identically.
- Session save/resume, discovery URL, and pop-out layout operate from this dashboard without
  requiring a separate administration surface.
- Red doctrine preset is viewable and adjustable (switch preset or hand-tune parameters)
  mid-exercise from this dashboard.
- Mission-set/campaign sequence visibility is available from this dashboard.
- The assess beat across both cells simultaneously is visible from this dashboard.

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is implied
for clock-authority enforcement and god-view fog-of-war correctness; Demonstration is likely the
appropriate method for inject-scheduling UX and multi-monitor pop-out layout. Flagged as an Open
Question below.

## Dependencies

[DOM-003](../domains/DOM-003-white-cell-framework.md), [DOM-001](../domains/DOM-001-training-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md) (per the existing
metadata block's Dependencies field). [FS-107](FS-107-after-action-review.md) (the AAR instrument this dashboard's controls
invoke) and [FS-108](FS-108-inject-authoring.md) (the candidate inject-authoring UX extension) are downstream or adjacent
features, not upstream dependencies of FS-106 itself.

## Risks

- Composing multiple inject templates into a pre-scripted sequence ahead of a session is named in
  [DOM-003](../domains/DOM-003-white-cell-framework.md) §9 as not currently possible — treating it as in scope would be a silent scope
  addition requiring a dedicated FS (FS-108 or a new ID).
- Granting any capability to Red/Blue through this dashboard that provides indirect ground-truth
  access would compromise the fog-of-war boundary regardless of how the capability is framed.

## Open Questions

- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-106; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- The source document does not assign a per-subsystem Subsystem Responsibilities table.
- The source document does not address Data Model Changes; whether the dashboard requires any new
  Domain Model entities (e.g., a structured inject-sequence representation) is unresolved.
- The source document does not state formal Verification Methods per criterion.

## Related ADRs

ADR-0016 (single point of time control) —
`docs/architecture/adr/ADR-0016-single-point-of-time-control.md`;
ADR-0027 (scenario-authoring boundary — the in-app vignette builder is a distinct
boundary-crossing interaction) — `docs/architecture/adr/ADR-0027-scenario-authoring-boundary.md`.

## Related Interfaces

INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control); INT-0003 (in-app scenario
builder) — per `docs/design/05-interface-control-document.md`.
