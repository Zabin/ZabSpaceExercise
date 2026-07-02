# FS-106 — White Cell Dashboard

> **Document ID:** FS-106
> **Version:** 2.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md), [DOM-001](../domains/DOM-001-training-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md)
> **Referenced By:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md), [IMP-106A](../implementations/IMP-106A-white-cell-dashboard.md)
> **Produces:** the facilitation surface [FS-108](FS-108-inject-authoring.md) (candidate) would extend
> **Feature Mapping:** FS-106 (this document)
> **Related Topics:** [FS-107](FS-107-after-action-review.md) (White-only AAR controls), [FS-109](FS-109-multiplayer-session-transport.md)
> (the underlying session/clock transport this dashboard's admin panel triggers), [FS-110](FS-110-save-and-resume.md)
> (the underlying save/resume mechanism this dashboard's admin panel triggers), [FS-111](FS-111-ai-red-doctrine-automation.md)
> (the underlying doctrine-preset generation mechanism this dashboard's preset selector controls),
> [DOM-002](../domains/DOM-002-assessment-framework.md) §6 (facilitator-rubric assessment mode, hosted here)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template. **Version 2.0
narrows this document's scope** per `docs/feature-planning/05-feature-review.md` Finding F-03: the
prior v1.0 draft bundled the White Cell facilitator UI together with three architecturally distinct
capabilities (multiplayer/LAN session transport, save/resume, and AI-Red doctrine automation), each
of which now has its own dedicated Feature Specification (FS-109, FS-110, FS-111 respectively).
This version retains the existing Document ID, status, and MSTR-006 §5 metadata per that section's
rules for a re-scoping revision (not a fresh document).*

## Feature ID

FS-106

## Title

White Cell Dashboard

## Purpose

The White Cell Dashboard is the facilitator's console: unrestricted god-view across both cells,
inject authoring/scheduling, clock/pacing control authority, and manual adjudication. Per
[DOM-003](../domains/DOM-003-white-cell-framework.md) §1, it must trace back to White Cell's role
as instructional designer ([MSTR-003](../master/MSTR-003-educational-philosophy.md) §7), not a
neutral referee — every capability in this spec exists to let a facilitator *shape* the learning
experience in real time, not merely observe it.

## Scope

In scope: god-view rendering (both cells' belief + ground truth simultaneously) and view-as-cell;
the inject build/schedule panel; clock pause/resume and the rewind/undo/branch **trigger surface**
(the White-only authority to invoke these, not the replay/scrub instrument itself); manual
adjudication (the absence of automated scoring, plus live safe-mode-dial/parameter adjustment
mid-exercise); and the facilitator-facing Red-doctrine-preset **selector/hand-tuning control**
(choosing and adjusting a preset — not the automated activity-generation mechanism the preset
drives).

Out of scope, each now owned by its own Feature Specification: the AAR replay/scrub instrument
itself ([FS-107](FS-107-after-action-review.md)); a richer inject-authoring UX
([FS-108](FS-108-inject-authoring.md), a separate, currently-candidate spec); the
server-authoritative lazy clock, per-session mutation locking, and hot-seat/LAN session-sharing
mechanism this dashboard's clock controls and session-admin panel sit on top of
([FS-109](FS-109-multiplayer-session-transport.md)); the deterministic save/resume mechanism and
content/session ownership split this dashboard's save-file controls invoke
([FS-110](FS-110-save-and-resume.md)); and the doctrine-preset-driven Red activity-generation
mechanism itself, as opposed to the facilitator's control over which preset is selected
([FS-111](FS-111-ai-red-doctrine-automation.md)).

**Also explicitly out of scope, and not covered by any existing Feature Specification:** vignette
selection/parameter tuning and seat-to-role assignment at session setup (FR-4110, FR-4210) —
`docs/feature-planning/03-feature-catalog.md`'s FEAT-4100/FEAT-4200. Reading this document's actual
workflows shows they were never in scope here either, despite superficially reading as "White Cell
setup." This is flagged as a genuine documentation gap for a future Feature Specification, not
silently absorbed into this rewrite.

## Requirements Implemented

FR-4310 (exclusive White Cell clock control), FR-4410 (immediate/scheduled inject application),
FR-4610 (White Cell god-view with per-cell view-as), FR-4710 (no automated scoring), FR-4720
(live adjustment of safe-mode dials/exercise parameters) — per `docs/feature-planning/03-feature-
catalog.md` FEAT-4300/FEAT-4400/FEAT-4600/FEAT-4700's `Included Requirements`. This is the first
version of this document to cite explicit FR IDs; the RTM's own "None identified" traceability gap
for FS-106 (`docs/feature-planning/05-feature-review.md` Finding F-06) is closed for these four FRs
by this revision — a corresponding update to `docs/requirements/03-requirements-traceability-
matrix.md`'s Impl. Package column is a separate, follow-on documentation task, not performed here
(this skill does not edit the requirements baseline).

## User Workflows

- The White Cell facilitator opens the god-view, observing both cells' belief states and ground
  truth simultaneously without granting either cell additional ground-truth access.
- The facilitator selects an inject template from the existing `inject_library.yaml` five-template
  set, edits its parameters as JSON, and schedules it for Now / +seconds / absolute-UTC delivery.
- The facilitator pauses or resumes the exercise clock, or triggers rewind/undo/branch — the
  underlying mechanics of these are [FS-109](FS-109-multiplayer-session-transport.md) (clock) and
  [FS-107](FS-107-after-action-review.md) (rewind/undo/branch replay); this dashboard is the
  White-only trigger surface for both.
- The facilitator views which Red-doctrine preset is active and switches or hand-tunes it
  mid-exercise for pacing reasons; the preset's actual activity-generation behavior is
  [FS-111](FS-111-ai-red-doctrine-automation.md).
- The facilitator observes mission-set/campaign sequencing (which vignette in a sequence is
  active) — grounded in [R301](../research/encyclopedia/R301-campaign-design.md) §5, not itself
  traced to a numbered FR (see Open Questions).
- The facilitator observes the assess beat across both cells simultaneously
  ([R106](../research/encyclopedia/R106-mission-operations.md) §5) — a perspective
  [FS-105](FS-105-spacecraft-operations.md)'s per-cell console does not provide, and likewise not
  itself traced to a numbered FR (see Open Questions).

## System Behaviour

- **Must expose unrestricted god-view without granting Red/Blue any new ground-truth access.** Per
  [DOM-003](../domains/DOM-003-white-cell-framework.md) §3, any new god-view-only capability is
  acceptable; any capability that would let Red/Blue access ground truth through this dashboard is
  a fog-of-war violation regardless of framing.
- **Inject authoring must work against the existing `inject_library.yaml` mechanism, not duplicate
  it.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §4, the dashboard exposes the
  five reusable templates with editable-JSON + Now/+seconds/absolute-UTC scheduler (FR-4410); the
  inject *execution* path is engine-side and out of scope to re-implement.
- **Clock/pacing control authority (FR-4310) must remain exclusively White Cell's**, applying
  identically to every connected client — no per-tab pacing negotiation (ADR-0016). The mechanism
  that propagates a pause/resume/rate-change to every connected client is
  [FS-109](FS-109-multiplayer-session-transport.md)'s responsibility, not this Feature's.
- **God-view/view-as (FR-4610) must never grant write access to the viewed cell's state.** A
  view-as-Red request returns exactly the data INT-0004 would return to a Red-seated operator, no
  more.
- **No automated scoring exists anywhere in the outbound interface set (FR-4710).** Live parameter
  adjustment (FR-4720, e.g. safe-mode dials) takes effect on the next evaluation with no session
  restart.
- **Red-doctrine-preset visibility and control is a facilitator-tooling requirement** (DOM-003 §7):
  the facilitator needs visibility into which preset drives Red and the ability to switch or
  hand-tune it mid-exercise — an unconvincing or passive Red undermines training per
  [R308](../research/encyclopedia/R308-red-teaming-methodology.md). The preset's own behavior once
  selected is [FS-111](FS-111-ai-red-doctrine-automation.md)'s System Behaviour, not this
  document's.
- **Authority-tier statement** (DOM-003 §8): this spec now touches three of DOM-003's four
  authority tiers — visibility (god-view), inject, and clock-trigger — plus manual adjudication.
  Session administration (§6 of DOM-003) is no longer this document's own System Behaviour; it is
  [FS-109](FS-109-multiplayer-session-transport.md)/[FS-110](FS-110-save-and-resume.md)'s (see Open
  Questions for the resulting DOM-003 framing tension).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/manager.py` (`SessionManager`) | Accepts clock-control requests (pause/resume/rewind/undo/branch trigger) only from the White Cell role; rejects others (FR-4310). Delegates the actual multi-client clock propagation to the mechanism specified in FS-109. |
| `session/manager.py` (`InProcessSession.inject_library()`) | Loads/exposes the five reusable inject templates and applies scheduled/immediate injects (FR-4410). |
| `session/api.py` (`SessionAPI`) | Serves god-view and view-as-cell requests (FR-4610), reusing the fog-of-war filter FS-106 does not itself implement (that filter's own Feature is `FEAT-6200` in the Feature Catalog, specified by a different, not-yet-authored FS). |
| `session/redai.py` | Exposes the currently-selected doctrine preset for display and accepts a facilitator's preset-switch/hand-tune request (DOM-003 §7); the preset's own generation behavior is FS-111's subsystem responsibility, not this row's. |
| `ui_web/server.py` / `ui_web/static/` | Renders the dashboard panels (god-view, inject panel, clock controls, adjudication/parameter controls) over the above. |

## Interfaces Used

INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control) — per
`docs/design/05-interface-control-document.md`. INT-0003 (in-app scenario builder) is **removed**
from this revision's Interfaces Used: on inspection, this document's actual Scope (god-view,
injects, clock, adjudication) does not touch the in-app vignette builder that INT-0003 describes;
that interface belongs to `FEAT-5100` (In-App Iterative Vignette Builder), a different, currently
unspecified Feature. Carrying it here was inherited from the prior v1.0 draft without a workflow
that used it — corrected here rather than propagated.

## Data Model Changes

Not addressed in any prior version of this document — no existing content to carry forward. The
dashboard consumes existing session state without a Domain Model change. Flagged as an Open
Question below, unchanged from v1.0.

## State Changes

- Inject scheduling commits an inject to the session's inject queue; the inject executes at the
  scheduled sim time via `WorldState` direct mutation (INT-0016, per the ICD).
- Red doctrine preset changes take effect immediately for AI-Red (ADR-0021) — the effect itself is
  FS-111's State Changes, not this document's.
- Clock-control and save/resume state transitions themselves are FS-109's and FS-110's State
  Changes respectively; this document only originates the White-Cell-authorized *request* for them.

## Error Handling

- Clock-control requests from a non-White-Cell role are rejected with the clock state unchanged
  (FR-4310) — the propagation mechanism that keeps all clients consistent is FS-109's concern.
- The source document does not enumerate failure modes for inject scheduling beyond the
  architectural constraints above (unchanged from v1.0).

## Performance Considerations

- **Single point of time control.** All clock-control *requests* originate only from this
  dashboard for the White Cell role (ADR-0016); the requirement that they apply identically and
  simultaneously across all connected clients is FS-109's Performance Consideration, not
  duplicated here.
- **Human factors.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §3, the god-view's
  role is instructional — the facilitator is shaping learning, not merely observing — and the
  dashboard's design must reflect this purpose.

## Security Considerations

- The dashboard must not expose any capability that grants Red/Blue ground-truth access — this is
  the single most critical invariant for this feature (DOM-003 §3).
- The LAN trust model (ADR-0015) applies: the dashboard's god-view is one of the no-cell
  ground-truth endpoints. The trust model's multi-client/session-sharing implications are FS-109's
  Security Considerations, not restated here.

## Acceptance Criteria

- God-view renders both cells' belief states and ground truth simultaneously without modifying
  either cell's fog-of-war-filtered view.
- Inject authoring works against the existing `inject_library.yaml` five-template set with
  editable-JSON + Now/+seconds/absolute-UTC scheduling; no duplicate inject-execution path exists.
- Clock pause/resume/rewind/undo/branch **trigger** requests are accepted only from the White Cell
  role; a Blue- or Red-role request is rejected with no clock-state change.
- No outbound interface returns a computed score/win-loss field; a live safe-mode-dial adjustment
  takes effect on the next evaluation with no session restart.
- Red doctrine preset is viewable and switchable/hand-tunable mid-exercise from this dashboard.
- Mission-set/campaign sequence visibility and the cross-cell assess beat are visible from this
  dashboard (research-grounded, not FR-traced — see Open Questions).

## Verification Plan

Test (automated) for clock-authority role rejection (FR-4310) and the no-automated-scoring
inspection sweep (FR-4710); Demonstration for inject-scheduling UX, doctrine-preset switching, and
live parameter adjustment (FR-4720), consistent with those requirements' own stated Verification
Methods in `docs/requirements/01-functional-requirements.md`.

## Dependencies

[FS-109](FS-109-multiplayer-session-transport.md) (clock-control requests this dashboard issues are
propagated by FS-109's mechanism), [FS-110](FS-110-save-and-resume.md) (session-admin save/resume
requests this dashboard's panel would trigger — see Open Questions on whether that panel remains
part of this document or FS-110's own UI surface), [FS-111](FS-111-ai-red-doctrine-automation.md)
(the preset this dashboard lets a facilitator select/tune). [DOM-003](../domains/DOM-003-white-cell-framework.md),
[DOM-001](../domains/DOM-001-training-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md),
[R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md),
[R308](../research/encyclopedia/R308-red-teaming-methodology.md) (unchanged from v1.0).
[FS-107](FS-107-after-action-review.md) (the AAR instrument this dashboard's controls invoke) and
[FS-108](FS-108-inject-authoring.md) (candidate) remain downstream/adjacent, not upstream
dependencies.

## Risks

- **This split (v2.0) introduces a cross-document seam that did not exist in v1.0.** A future
  change to clock-control authority (e.g. a new role gaining partial pacing control) now requires
  coordinated updates to this document *and* FS-109; the two must be kept in sync explicitly, not
  assumed consistent.
- Composing multiple inject templates into a pre-scripted sequence ahead of a session is named in
  DOM-003 §9 as not currently possible — treating it as in scope would be a silent scope addition
  requiring FS-108 or a new ID (unchanged from v1.0).
- Granting any capability to Red/Blue through this dashboard that provides indirect ground-truth
  access would compromise the fog-of-war boundary regardless of framing (unchanged from v1.0).
- **`IMP-106A-white-cell-dashboard.md` (and its successor `IP-1060`) were written against this
  document's prior, broader v1.0 scope.** Both now over-cite this document relative to its narrowed
  v2.0 scope (they also cover material now specified by FS-109/FS-110/FS-111). Reconciling the
  Implementation Package layer against this split is a follow-on task, out of scope for this
  Feature Specification revision.

## Open Questions

- **DOM-003 §6 framing tension (new in v2.0):** DOM-003 explicitly claims "session administration
  (save/resume, multiplayer session discovery)" as White-Cell-domain territory, reasoned as a
  facilitation concern rather than an infrastructure one. This Feature Specification split
  (FS-109/FS-110 now specifying the underlying mechanisms) does not contradict that domain framing
  — DOM-003 can and does still ground multiple Feature Specifications — but it does mean DOM-003's
  own §6 text and Feature Mapping frontmatter should be read as covering FS-109/FS-110 as siblings
  of FS-106, not as implying those mechanisms belong inside this single document. DOM-003's
  frontmatter has been updated accordingly (see that document).
- Whether the save/resume and session-discovery *panel UI* (as opposed to the underlying
  mechanism, now FS-109/FS-110) belongs in this document or should move entirely to FS-109/FS-110 is
  unresolved — this revision keeps the panel-triggering workflow bullets here provisionally under
  "session administration" framing per DOM-003 §6, pending a UI-ownership decision.
- Mission-set/campaign-sequence visibility and the cross-cell assess-beat view are grounded in
  R301/R106 but trace to no numbered FR in `docs/requirements/01-functional-requirements.md` —
  unchanged from v1.0, not resolved by this revision.
- The source document does not assign a formal per-subsystem Subsystem Responsibilities table
  beyond what this revision now states; whether further decomposition is warranted is open.
- The source document does not address Data Model Changes; whether the dashboard requires any new
  Domain Model entities is unresolved (unchanged from v1.0).
- `IMP-106A`/`IP-1060` reconciliation against this narrowed scope (see Risks) is an open follow-on
  task.

## Related ADRs

ADR-0016 (single point of time control) —
`docs/architecture/adr/ADR-0016-single-point-of-time-control.md`. ADR-0027 (scenario-authoring
boundary) is **removed** from this revision's Related ADRs — it grounded the now-removed INT-0003
citation (see Interfaces Used) and does not bear on this document's narrowed scope.

## Related Interfaces

INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control) — per
`docs/design/05-interface-control-document.md`. INT-0003 is related context (consumed by a
different, unspecified Feature — FEAT-5100 in the Feature Catalog) but is not directly used by this
document — see Interfaces Used.
