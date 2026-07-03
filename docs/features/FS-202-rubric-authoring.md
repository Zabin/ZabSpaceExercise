# FS-202 — Rubric Authoring *(candidate)*

> **Document ID:** FS-202
> **Version:** 0.1 (candidate scope — not authorized)
> **Status:** 🅿️ Scoped, not authorized
> **Dependencies:** [DOM-002](../domains/DOM-002-assessment-framework.md) §5, §7, [FS-201](FS-201-competency-assessment.md)
> **Referenced By:** [DOM-002](../domains/DOM-002-assessment-framework.md)
> **Produces:** nothing yet — no Implementation Package may begin against this ID without explicit
> user go-ahead (see [`MSTR-006`](../master/MSTR-006-governance-principles.md) §3)
> **Feature Mapping:** FS-202 (this document)
> **Related Topics:** [FS-201](FS-201-competency-assessment.md) (the rubric instrument this feature would let users adjust)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-202

## Title

Rubric Authoring *(candidate — not authorized)*

## Purpose

**This document records candidate scope for an unauthorized feature.** FS-202 is named as
"(candidate)" in [DOM-002](../domains/DOM-002-assessment-framework.md)'s own frontmatter (`**Produces:** FS-201 Competency Assessment,
FS-202 (candidate) Rubric Authoring`) — it is not committed scope. Per [MSTR-006](../master/MSTR-006-governance-principles.md) §3, the 🅿️
authorization gate applies: this feature requires explicit user authorization before promotion to a
full spec or before any Implementation Package work begins. The 20-field structure used here is for
format consistency only; it does not authorize or advance the work.

The candidate purpose: extend [FS-201](FS-201-competency-assessment.md)'s fixed rubric tiers with an authoring surface that lets
instructors adjust or extend the rubric without engine changes — anticipated as a future need once
FS-201 has field experience, but explicitly not committed in [DOM-002](../domains/DOM-002-assessment-framework.md) the way FS-201's requirements
are committed in §8.

## Scope

**Conditional — not authorized.** If authorized (inferred from [DOM-002](../domains/DOM-002-assessment-framework.md) §5/§7):

In scope: adjusting or relabeling rubric tiers for a given course/cohort without engine changes;
enabling/disabling specific [FS-201](FS-201-competency-assessment.md) dimensions per vignette or training program; defining new
measurement dimensions beyond [DOM-002](../domains/DOM-002-assessment-framework.md) §4's original six.

Explicit non-goal (even if authorized): any rubric-authoring tool must not introduce a path to
collapse the rubric into a single composite score — per [DOM-002](../domains/DOM-002-assessment-framework.md) §5's rubric-not-single-score
principle, which remains out of scope for the underlying instrument regardless of authoring
flexibility.

Out of scope: the underlying [FS-201](FS-201-competency-assessment.md) rubric computation itself (this feature is an authoring
surface above it, not a replacement).

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7). Additionally,
this feature is not authorized, so requirements implementation is moot until authorization is
granted.

## User Workflows

**Conditional — not authorized.** If authorized, candidate workflows (inferred from [DOM-002](../domains/DOM-002-assessment-framework.md) §5/§7):

- An instructor adjusts or relabels rubric tiers (e.g., renames "speculative" to a
  course-specific label) for their cohort without requiring engine changes.
- An instructor enables or disables specific [FS-201](FS-201-competency-assessment.md) dimensions for a given vignette or
  training program.
- An instructor defines a new measurement dimension beyond [DOM-002](../domains/DOM-002-assessment-framework.md) §4's original six, with
  data-source and tier-definition specified.

## System Behaviour

**Conditional — not authorized.** Not addressed in the source document. Any system behavior
specification must wait for authorization and a full FS authoring pass.

## Subsystem Responsibilities

**Conditional — not authorized.** Not addressed in the source document.

## Interfaces Used

Not addressed in the source document. No ICD interface explicitly names rubric authoring as a
distinct interface boundary. Flagged as an Open Question below.

## Data Model Changes

**Conditional — not authorized.** Not addressed in the source document. Rubric-tier adjustment
implies per-cohort or per-vignette overrides to the rubric structure that FS-201 fixes in its
base instrument — new Domain Model entities would likely be required, but the source document does
not specify them. Flagged as an Open Question below.

## State Changes

**Conditional — not authorized.** Not addressed in the source document.

## Error Handling

**Conditional — not authorized.** Not addressed in the source document.

## Performance Considerations

**Conditional — not authorized.** Not addressed in the source document.

## Security Considerations

**Conditional — not authorized.** Not addressed in the source document. Per [DOM-002](../domains/DOM-002-assessment-framework.md) §5's
non-single-score principle, the authoring surface must not introduce a path to composite scoring
regardless of how it is framed.

## Acceptance Criteria

**Conditional — not authorized.** Cannot be specified until this feature is authorized and a full
FS authoring pass is completed per the "Next step if authorized" guidance below.

## Verification Plan

**Conditional — not authorized.** Cannot be specified until authorized.

## Dependencies

[DOM-002](../domains/DOM-002-assessment-framework.md) §5, §7 and [FS-201](FS-201-competency-assessment.md) (per the existing metadata block's Dependencies field). [FS-201](FS-201-competency-assessment.md)
is both a dependency and a prerequisite: authoring tooling for an instrument that does not yet have
an Implementation Package and field experience would be speculative, per the source document's own
"Next step if authorized" guidance.

## Risks

- Promoting this feature to a full spec or beginning any Implementation Package without explicit
  user go-ahead violates MSTR-006 §3's authorization gate.
- Authorizing rubric authoring before [FS-201](FS-201-competency-assessment.md) has an Implementation Package and field
  experience risks building an authoring surface for a rubric instrument whose tier definitions may
  still change — the source document explicitly names this as the reason authorization should wait.
- Any authoring path that introduces a composite-score output violates [DOM-002](../domains/DOM-002-assessment-framework.md) §5's explicit
  non-single-score principle.

## Open Questions

- **Authorization pending.** This feature requires explicit user go-ahead before it may be promoted
  to ✅ status or before any Implementation Package work begins (MSTR-006 §3). The 20-field
  template structure here is for format consistency only — it does not constitute authorization.
- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-202; this is a traceability gap
  for Phase 8 review (MSTR-006 §7) but is also moot until authorization is granted.
- Data Model Changes, Acceptance Criteria, Verification Plan, and Subsystem Responsibilities cannot
  be specified until authorized and until [FS-201](FS-201-competency-assessment.md) has sufficient field experience to inform
  what rubric aspects instructors actually want to adjust.
- No ICD interface explicitly names rubric authoring; whether a new INT-xxxx interface is required
  is unresolved for Phase 8.

## Related ADRs

None identified — no ADR in `docs/architecture/adr/` explicitly names rubric authoring as a
settled decision point. This is not a traceability gap per se; the feature is unauthorized and no
ADR should be expected for unauthorized candidate scope.

## Related Interfaces

None identified — no ICD interface in `docs/design/05-interface-control-document.md` explicitly
names a rubric-authoring boundary. This is a gap for Phase 8 traceability review if FS-202 is ever
authorized.

---

*Next step if authorized:* Promote this document to a full Feature Specification (status ✅,
version 1.0) following the same 20-field structure used by [FS-101](FS-101-mission-planning.md)–[FS-107](FS-107-after-action-review.md), grounded in
[DOM-002](../domains/DOM-002-assessment-framework.md) and informed by real usage patterns from [FS-201](FS-201-competency-assessment.md)'s Implementation Package and field
experience — authoring tooling for an instrument that does not yet exist would be speculative.
