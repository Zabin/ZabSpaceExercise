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

## Why this is a stub, not a full spec

FS-202 is named as **"(candidate)"** in [DOM-002](../domains/DOM-002-assessment-framework.md)'s own frontmatter (`**Produces:** FS-201
Competency Assessment, FS-202 (candidate) Rubric Authoring`) — it is not committed scope, and per
[`MSTR-006`](../master/MSTR-006-governance-principles.md) §3 requires explicit user authorization before promotion to a full spec or any
Implementation Package work. This document records the candidate scope implied by [DOM-002](../domains/DOM-002-assessment-framework.md)'s
existing text.

## Candidate scope (inferred from DOM-002 §5 / §7)

[FS-201](FS-201-competency-assessment.md) fixes its rubric tiers (e.g., "speculative / adequate / disciplined" for custody quality) as
part of the base instrument. [DOM-002](../domains/DOM-002-assessment-framework.md) §7 anticipates a "competency report" viewable per-cell and
longitudinally per-trainee, which implies an institution may eventually want to:

- Adjust or relabel rubric tiers for a given course/cohort, without engine changes.
- Enable/disable specific [FS-201](FS-201-competency-assessment.md) dimensions per vignette or per training program.
- Define new measurement dimensions beyond [DOM-002](../domains/DOM-002-assessment-framework.md) §4's original six, as instructors identify
  gaps.

None of this is committed — it is inferred candidate scope, not a requirement [DOM-002](../domains/DOM-002-assessment-framework.md) itself
states explicitly the way it states FS-201's requirements in §8.

## Explicit non-goal

Per [DOM-002](../domains/DOM-002-assessment-framework.md) §5's rubric-not-single-score principle, any rubric-authoring tool must not introduce a
path to collapse the rubric into a single composite score — that remains explicitly out of scope
for the underlying instrument regardless of authoring flexibility.

## Next step if authorized

If the user authorizes this feature, it should be promoted to a full Feature Specification (status
✅, version 1.0), grounded in [DOM-002](../domains/DOM-002-assessment-framework.md) and informed by whatever real usage patterns emerge once
[FS-201](FS-201-competency-assessment.md) itself has an Implementation Package and field experience — authoring tooling for an
instrument that doesn't exist yet would be speculative.
