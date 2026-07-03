# FS-108 — Inject Authoring *(candidate)*

> **Document ID:** FS-108
> **Version:** 0.1 (candidate scope — not authorized)
> **Status:** 🅿️ Scoped, not authorized
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md) §4, §9
> **Referenced By:** [DOM-003](../domains/DOM-003-white-cell-framework.md)
> **Produces:** nothing yet — no Implementation Package may begin against this ID without explicit
> user go-ahead (see [`MSTR-006`](../master/MSTR-006-governance-principles.md) §3)
> **Feature Mapping:** FS-108 (this document)
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (the dashboard this feature would extend)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-108

## Title

Inject Authoring *(candidate — not authorized)*

## Purpose

**This document records candidate scope for an unauthorized feature.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §1's
frontmatter, FS-108 is explicitly marked "(candidate)" everywhere it appears in the existing corpus.
Per [MSTR-006](../master/MSTR-006-governance-principles.md) §3, the 🅿️ authorization gate applies: this feature may not be
promoted to a full ✅ specification, and no Implementation Package may begin against this ID,
without explicit user go-ahead — which has not been given. The 20-field structure used here is for
format consistency only; it does not authorize or advance the work.

The candidate purpose: extend the White Cell Dashboard ([FS-106](FS-106-white-cell-dashboard.md)) with improved inject *authoring*
ergonomics — templated parameter forms, a preview-before-schedule step, and a library browser —
over the existing `inject_library.yaml` mechanism that [FS-106](FS-106-white-cell-dashboard.md) already surfaces as raw editable JSON.
This would not duplicate or replace the inject *execution* mechanism, which is already engine-side
and complete.

## Scope

**Conditional — not authorized.** If authorized:

In scope: templated parameter forms (vs. raw editable JSON) for the existing five inject templates,
a preview-before-schedule step, and a library browser with search as the template library grows.
Also candidate (per [DOM-003](../domains/DOM-003-white-cell-framework.md) §9, open work): composing multiple inject templates into a
pre-scripted sequence ahead of a session.

Out of scope (even if authorized): the inject *execution* mechanism (`InProcessSession.inject_library()`),
which already exists and works; this candidate's scope is authoring ergonomics only.

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference. Additionally, this feature is not authorized, so requirements
implementation is moot until authorization is granted.

## User Workflows

**Conditional — not authorized.** If authorized, candidate workflows:

- A facilitator opens the inject library browser, searches/filters the available templates, and
  selects one to author.
- The facilitator fills in structured parameter forms (not raw JSON) for the selected template and
  previews the inject before scheduling it.
- The facilitator schedules the authored inject for Now / +seconds / absolute-UTC delivery, as in
  the existing [FS-106](FS-106-white-cell-dashboard.md) mechanism.
- (Candidate, per [DOM-003](../domains/DOM-003-white-cell-framework.md) §9) The facilitator composes multiple inject templates into a
  pre-scripted sequence for a session, ahead of time.

## System Behaviour

**Conditional — not authorized.** The source document describes no detailed system behavior beyond
the authoring-ergonomics gap statement. Any system behavior specification must wait for
authorization and a full FS authoring pass, per the "Next step if authorized" section below.

## Subsystem Responsibilities

**Conditional — not authorized.** Not addressed in the source document.

## Interfaces Used

Per the verified mapping for FS-108: INT-0016 (White Cell Inject Application → Simulation Engine
WorldState, direct mutation bypass) — per `docs/design/05-interface-control-document.md`. This
interface already exists for the underlying inject execution path ([FS-106](FS-106-white-cell-dashboard.md)); FS-108 would be an
authoring-ergonomics layer above it, not a new interface.

## Data Model Changes

**Conditional — not authorized.** Not addressed in the source document. Flagged as an Open Question
below.

## State Changes

**Conditional — not authorized.** Not addressed in the source document beyond noting that the
underlying inject execution state machine is owned by [FS-106](FS-106-white-cell-dashboard.md)/the engine-side mechanism and would
not be altered by FS-108's candidate scope.

## Error Handling

**Conditional — not authorized.** Not addressed in the source document.

## Performance Considerations

**Conditional — not authorized.** Not addressed in the source document.

## Security Considerations

**Conditional — not authorized.** Not addressed in the source document. The underlying inject
execution path (INT-0016, WorldState direct mutation bypass) is already White-Cell-only per the
LAN trust model; this scope does not change that boundary.

## Acceptance Criteria

**Conditional — not authorized.** Cannot be specified until this feature is authorized and a full
FS authoring pass is completed per the "Next step if authorized" guidance below.

## Verification Plan

**Conditional — not authorized.** Cannot be specified until authorized.

## Dependencies

[DOM-003](../domains/DOM-003-white-cell-framework.md) §4, §9 (per the existing metadata block's Dependencies field). [FS-106](FS-106-white-cell-dashboard.md) is the
feature this candidate would extend; it is a prerequisite, not a co-dependency.

## Risks

- Promoting this feature to a full spec or beginning any Implementation Package without explicit
  user go-ahead violates MSTR-006 §3's authorization gate — the 🅿️ status is a hard stop, not a
  soft suggestion.
- Scoping the sequence-ahead-of-session capability ([DOM-003](../domains/DOM-003-white-cell-framework.md) §9) without deliberate decision would
  silently expand scope beyond the core authoring-ergonomics gap.

## Open Questions

- **Authorization pending.** This feature requires explicit user go-ahead before it may be promoted
  to ✅ status or before any Implementation Package work begins (MSTR-006 §3). The 20-field
  template structure used here is for format consistency only — it does not constitute authorization.
- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-108; this is a traceability gap
  for Phase 8 review (MSTR-006 §7) but is also moot until authorization is granted.
- Data Model Changes, Acceptance Criteria, Verification Plan, and Subsystem Responsibilities cannot
  be specified until the feature is authorized and a full FS authoring pass is completed.
- Whether the pre-scripted sequence capability ([DOM-003](../domains/DOM-003-white-cell-framework.md) §9) should be in scope alongside or
  deferred relative to the core authoring-ergonomics gap is an open design question for when
  authorization is sought.

## Related ADRs

None identified — no ADR in `docs/architecture/adr/` explicitly names inject authoring as a settled
decision point. This is not a traceability gap per se; the feature is unauthorized and no ADR
should be expected for unauthorized candidate scope.

## Related Interfaces

INT-0016 (White Cell Inject Application → Simulation Engine WorldState, direct mutation bypass) —
per `docs/design/05-interface-control-document.md`. This interface would be consumed by FS-108's
authoring layer if authorized; it is not a new interface introduced by this feature.

---

*Next step if authorized:* Promote this document to a full Feature Specification (status ✅,
version 1.0) following the same 20-field structure used by [FS-101](FS-101-mission-planning.md)–[FS-107](FS-107-after-action-review.md), grounded in
[DOM-003](../domains/DOM-003-white-cell-framework.md) §4/§9, and complete all conditional fields above before any Implementation Package
work begins.
