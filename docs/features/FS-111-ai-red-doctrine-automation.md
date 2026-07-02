# FS-111 — AI-Red Doctrine Automation

> **Document ID:** FS-111
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [DOM-008](../domains/DOM-008-ai-integration-framework.md), [ADR-0021](../architecture/adr/ADR-0021-ai-red-session-layer-feature.md), [ADR-0024](../architecture/adr/ADR-0024-ai-red-boundary-classification.md), [ADR-0030](../architecture/adr/ADR-0030-ai-determinism-doctrine.md)
> **Referenced By:** [FS-106](FS-106-white-cell-dashboard.md) (the facilitator-facing preset selector/hand-tuning control over this mechanism), [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md) `FEAT-9100`
> **Produces:** Red-attributed Planned Activities, indistinguishable in the event log from human-issued ones
> **Feature Mapping:** FS-111 (this document)
> **Related Topics:** [FS-101](FS-101-mission-planning.md) (the plan-first command path this Feature reuses), [FS-106](FS-106-white-cell-dashboard.md)
> (the facilitator's preset selection/hand-tuning control, distinct from this mechanism), `docs/reviews/strategic-review-2026-07.md`
> FC-02/GAP-08 (fog-of-war parity, the project's own highest-priority tracked gap)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template. It is a **new**
Feature Specification, split out of `FS-106-white-cell-dashboard.md` v1.0 per
`docs/feature-planning/05-feature-review.md` Finding F-03 — the prior v1.0 draft folded the
automated Red-activity-generation mechanism (its own dedicated ADRs: ADR-0021, ADR-0024, ADR-0030,
and its own module `session/redai.py`) inside the White Cell facilitator UI document. The
facilitator's *selection/hand-tuning control* over which preset is active remains
[FS-106](FS-106-white-cell-dashboard.md)'s scope (DOM-003 §7); this document specifies the
automated mechanism that control drives.*

## Feature ID

FS-111

## Title

AI-Red Doctrine Automation

## Purpose

Substitute for an unseated Red cell by generating Planned Activities consistent with a configured
doctrine preset, through the same command path a human Red operator would use — per
`docs/feature-planning/03-feature-catalog.md` `FEAT-9100`'s own Purpose field. Grounded in
[DOM-009](../domains/DOM-009-doctrine-development-framework.md)'s doctrine-translation process
(a preset is doctrine translated into an executable Red-cell behavior profile, the same kind of
translation DOM-009 already grounds for FS-103/FS-104) and in
[DOM-008](../domains/DOM-008-ai-integration-framework.md)'s cross-cutting AI-integration principles
(DOM-008's own frontmatter names `redai.py`-derived features as exactly what it expects to touch).

## Scope

In scope: doctrine-preset-driven Planned Activity generation for an unseated Red seat
(`russia_ew_first`, `china_integrated`, `generic` presets), issued through the same plan-first path
a human operator uses, indistinguishable in the event log from human-issued activities. Out of
scope: the facilitator's selection/hand-tuning control surface over which preset is active
([FS-106](FS-106-white-cell-dashboard.md)); AI-Red's fog-of-war-parity gap (ADR-0024's accepted v1
asymmetry — AI-Red reads `WorldState` directly rather than through a filtered `CellView`; tracked
as CR-01/CNFR-06 in the requirements baseline, an unbaselined candidate this Feature does not
remediate); doctrine-preset-selection guidance for a given training objective (CR-07, a separate,
unbaselined candidate).

## Requirements Implemented

FR-9110 (AI-Red issues Planned Activities per a doctrine preset) — per
`docs/feature-planning/03-feature-catalog.md` `FEAT-9100`'s `Included Requirements`. FR-9110's own
Priority is **Should**, not Must, per its own stated rationale: a vignette remains fully playable
with a human-seated or facilitator-played Red cell — AI-Red is a valuable convenience for
under-staffed exercises, not a precondition for any vignette's playability.

## User Workflows

- When Red's seat is configured (via [FS-106](FS-106-white-cell-dashboard.md)) to use an AI-Red
  preset instead of a human operator, the system generates Red-attributed Planned Activities
  consistent with the configured preset's doctrinal profile, at the times and against the targets
  the preset's logic determines.
- A generated activity passes through the same execute-time re-validation (ownership, window,
  resources, ROE, weapons-quality gate) as a human-issued activity, and either executes or fails
  exactly as a human-issued activity would under the same conditions.
- An observer inspecting the event log cannot distinguish an AI-Red-issued activity from a
  human-Red-issued activity of the same kind, by design.

## System Behaviour

- **AI-Red generates Planned Activities consistent with the configured doctrine preset** (FR-9110):
  under `china_integrated`, `russia_ew_first`, or `generic`, resulting activities are consistent
  with that preset's doctrinal profile.
- **AI-Red substitutes for an unseated Red; it does not run alongside a human-seated Red
  simultaneously** — this configuration is mutually exclusive with a human operator concurrently
  occupying the same Role Assignment, per FR-9110's own stated Preconditions.
- **AI-Red-issued activities are indistinguishable from human-issued ones in the event log** and
  pass the same execute-time re-validation (FEAT-3400 in the Feature Catalog) as any other Planned
  Activity — no separate execution path, no special-cased validation bypass.
- **AI-Red reads `WorldState` directly, not through a fog-of-war-filtered `CellView`** (ADR-0024,
  INT-0015) — an intentional, accepted v1 epistemic asymmetry against a human Red operator's actual
  information access, not remediated by this Feature. This is the single most-flagged strategic gap
  in the project's own governance record (`strategic-review-2026-07.md` FC-02/GAP-08) and is
  restated here as a boundary of this Feature's System Behaviour, not resolved by it.
- **Non-deterministic AI-Red behavior enters the deterministic core only as ordered, logged
  events** (ADR-0030, generalizing ADR-0021's determinism-placement rule specifically to AI-Red):
  whatever internal logic a doctrine preset uses to decide an activity, its *output* is a
  Planned Activity submitted through the same path — and therefore the same replay-determinism
  guarantee (FEAT-1100) — as any other order.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/redai.py` | Owns doctrine-preset selection state and the activity-generation logic for each preset (`russia_ew_first`, `china_integrated`, `generic`); submits generated Planned Activities through the same order-issuance path (`engine/orders.py`) a human operator's console would use. |
| `engine/orders.py` (`OrderSystem`) | Applies the same validate → window → execute → confirm lifecycle and execute-time re-validation to AI-Red-issued activities as to human-issued ones — no AI-Red-specific branch. |

## Interfaces Used

INT-0008 (Session Layer → Simulation Engine, Clock/Scheduler/EventLog/`OrderSystem`) — the path
AI-Red-generated activities are submitted and executed through, identical to a human operator's.
INT-0015 (Session Layer, AI-Red/`redai.py` → Simulation Engine, `WorldState` direct read) — the
documented, accepted direct ground-truth read this Feature's System Behaviour names as an
intentional v1 asymmetry, not something this Feature remediates.

## Data Model Changes

None beyond the existing Domain Model's Planned Activity entity (`docs/architecture/04-domain-
model.md` §6.5) — AI-Red-issued activities are ordinary Planned Activity records attributed to the
Red cell, with no new entity or attribute introduced.

## State Changes

- A doctrine-preset change (via FS-106's control surface) takes effect immediately for subsequent
  AI-Red activity generation (ADR-0021) — prior already-scheduled activities are unaffected.
- Generated Planned Activities transition through the same lifecycle states (`DRAFT`/`PLANNED`/
  `ACTIVE`/`EXECUTED`/`FAILED`) as any other Planned Activity (FEAT-3100/FEAT-3400 in the Feature
  Catalog).

## Error Handling

- A generated activity that fails execute-time re-validation transitions to `FAILED` with a
  recorded reason, exactly as a human-issued activity would (FEAT-3400) — no AI-Red-specific error
  path exists or is specified.
- The requirements baseline does not specify behavior if a doctrine preset's internal logic fails
  to produce a valid activity (e.g., no legal target exists) — flagged as an Open Question.

## Performance Considerations

No NFR in the requirements baseline applies specifically to this Feature beyond the general
determinism/replay-safety properties (NFR-1500, owned by `FEAT-1100`) that ADR-0030's determinism
doctrine requires AI-Red's *output* (not its internal decision process) to respect.

## Security Considerations

- **CNFR-06** (AI-Red epistemic parity/fairness as a quality attribute) is an explicitly excluded
  candidate NFR in the requirements baseline — ADR-0024 accepts AI-Red's direct ground-truth read
  as a permanent, accepted v1 deviation, tracked only as future work (`FUTURE-WORK.md` §1), not a
  v1 commitment this Feature must meet.
- This Feature does not itself cross any fog-of-war trust boundary that a human Red operator
  wouldn't also be inside — it reads *more* than a human Red operator would (via INT-0015), which
  is the accepted asymmetry above, not an additional new exposure this Feature introduces beyond
  what ADR-0024 already names.

## Acceptance Criteria

- Under the `china_integrated` preset, resulting Planned Activities are consistent with that
  preset's doctrinal profile.
- AI-Red-issued activities pass the same execute-time re-validation (FEAT-3400) as a human-issued
  activity of the same kind, with no special-cased bypass.
- AI-Red-issued activities are indistinguishable from human-Red-issued activities of the same kind
  when inspecting the event log alone.

## Verification Plan

Test (automated) for all three Acceptance Criteria above, consistent with FR-9110's own stated
Verification Method ("Test") in `docs/requirements/01-functional-requirements.md`.

## Dependencies

`FEAT-3100` (Plan-First Command Authoring & Delivery Path) and `FEAT-3400` (Execute-Time
Re-Validation) in the Feature Catalog — AI-Red reuses both mechanisms rather than a parallel path.
[FS-101](FS-101-mission-planning.md) (Mission Planning, the human-facing specification of the same
underlying plan-first mechanism this Feature's activities are submitted through) is the nearest
existing FS-xxx sibling, though not a formal upstream dependency distinct from the Feature Catalog
entries above.

## Risks

- **AI-Red's ground-truth-read asymmetry (ADR-0024) is this Feature's largest known limitation**,
  named repeatedly across the project's own governance record (strategic review FC-02/GAP-08) as
  the highest-priority tracked gap — any future remediation (CR-01/CNFR-06, fog-of-war parity)
  would be a significant revision to this Feature's System Behaviour, not a minor patch.
- A credible-but-exploitable doctrine preset risks negative training (a trainee learns to exploit a
  consistent AI strawman rather than facing genuinely adversarial play) — named in the strategic
  review (§4.5, GAP-08) as a validation gap, not something this Feature's own specification
  resolves.
- Splitting this mechanism out of FS-106 (v1.0) creates a cross-document seam with
  [FS-106](FS-106-white-cell-dashboard.md): a future change to preset-selection UX must be
  coordinated with this document if it implies a change to the generation mechanism itself.

## Open Questions

- **Fog-of-war parity (CR-01/CNFR-06)** is the named future-work item that would close this
  Feature's largest known gap — not resolved by this specification, consistent with this skill's
  rule against inventing a remediation for an unbaselined candidate requirement.
- **Doctrine-preset validation standard (GAP-08 in the strategic review):** no research or
  requirements document states how a preset's doctrinal fidelity is validated against real
  adversary behavior — flagged here as inherited from the strategic review, not resolved by this
  Feature.
- Behavior when a doctrine preset's internal logic cannot produce a valid activity (e.g., no legal
  target exists in the current geometry) is not specified in the requirements baseline.
- **Domain ownership:** this document grounds itself in DOM-009 (doctrine translation) and DOM-008
  (AI integration, cross-cutting) rather than DOM-003 (which explicitly disclaims owning the
  generation mechanism itself, per DOM-003 §7's framing of doctrine-preset *quality and
  variety* as a "White Cell tooling concern" — the facilitator's control surface, not the
  mechanism). Neither DOM-009 nor DOM-008's existing frontmatter cited this document before this
  revision; both have been updated to reference FS-111 (see those documents).

## Related ADRs

ADR-0021 (AI-Red session-layer feature) —
`docs/architecture/adr/ADR-0021-ai-red-session-layer-feature.md`; ADR-0024 (AI-Red boundary
classification) — `docs/architecture/adr/ADR-0024-ai-red-boundary-classification.md`; ADR-0030
(AI-determinism doctrine) — `docs/architecture/adr/ADR-0030-ai-determinism-doctrine.md`.

## Related Interfaces

INT-0008, INT-0015 — per `docs/design/05-interface-control-document.md` (both are also this
document's Interfaces Used).
