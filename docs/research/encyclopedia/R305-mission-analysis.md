# R305 — Mission Analysis

> **Document ID:** R305
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R301](R301-campaign-design.md)
> **Referenced By:** [R311](R311-course-of-action-analysis.md)
> **Produces:** the vocabulary for translating a vignette's narrative intent into its concrete `objectives` block
> **Feature Mapping:** vignette authoring (`docs/scenarios/`)
> **Related Topics:** [R301](R301-campaign-design.md) (Campaign Design), [R302](R302-operational-art.md) (Operational Art), [R311](R311-course-of-action-analysis.md) (Course of Action
> Analysis), DOM-009 (the translation pipeline this topic's output feeds)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Every vignette's `objectives` block is the product of an (often implicit) mission-analysis step:
someone decided that *these* specific, checkable conditions (e.g. "establish weapons-quality
custody on asset X") faithfully represent the vignette's higher narrative intent (e.g. "defend the
constellation"). This topic gives a vignette author the formal mission-analysis vocabulary to do that
translation deliberately rather than by intuition alone.

## 2. Concepts

**Commander's intent vs. specified/implied tasks.** Mission analysis doctrine distinguishes a
higher commander's *intent* (the desired end state, often stated narratively) from the *specified
tasks* explicitly ordered and the *implied tasks* necessary to accomplish the intent but not
explicitly stated. A vignette's `intro_brief` mission statement is the intent; its `objectives` block
is the specified tasks — and a well-designed vignette should make sure the specified, checkable
objectives actually imply accomplishing the stated intent, not merely correlate with it.

**Constraints and restraints.** A constraint is a required action ("must maintain command uplink to
station X"); a restraint is a prohibited action ("must not engage without ROE authorization"). ROE
blocks and ammo/Δv resource limits in a vignette are restraints in this formal sense; access-window
and custody requirements that must be satisfied to act are constraints — useful vocabulary for DOM-
009's doctrine-translation step when documenting *why* a vignette's ROE block reads the way it does.

**Essential tasks.** Among all implied tasks, the essential ones are those without which the mission
fails even if every other task succeeds — identifying the essential task(s) in a vignette design is
what determines which `objectives` entries should actually gate "mission success" vs. which are
secondary/bonus objectives, a distinction the engine's flat objective-flip model (DOM-002 §3) doesn't
currently make but that vignette *design* should reason about even before any engine support exists.

## 3. Operational Context

Real mission analysis (the formal MDMP "Mission Analysis" step) is precisely this translation
discipline — turning a higher commander's narrative intent into a concrete, checkable task list while
explicitly separating essential from supporting tasks and constraints from restraints — done
deliberately and documented, not left as an unstated judgment call by whoever happens to write the
operations order.

## 4. Implementation Guidance

- **A vignette author should be able to point to which `objectives` entries are essential
  (mission-defining) vs. supporting**, even if the engine doesn't yet distinguish them mechanically —
  this is useful both for DOM-009's doctrine-translation traceability and as input to a future
  weighted-objectives feature (a candidate enhancement, not yet built).
- **A vignette's ROE block should be authored by explicitly separating constraints from
  restraints** (what must be done vs. what must not be done) — this maps cleanly onto the engine's
  actual distinction between window/custody *requirements* (constraints, enforced by `_validate`)
  and ROE *prohibitions* (restraints, also enforced by `_validate` but conceptually distinct), and
  keeps a vignette's intent legible to anyone auditing it later.
- **Don't let an `objectives` block drift from the `intro_brief`'s stated intent over a vignette's
  revision history** — per DOM-009 §5's doctrine-review-cadence guidance, a revision to either should
  prompt a check that the other still matches.

## 5. Feature Mapping

Vignette authoring (`docs/scenarios/`) is the direct consumer; DOM-009's translation pipeline is the
process this topic's vocabulary feeds.

## 6. Related Topics

[R301](R301-campaign-design.md) (Campaign Design, the multi-vignette context), [R302](R302-operational-art.md) (Operational Art), [R311](R311-course-of-action-analysis.md) (Course of Action
Analysis, comparing options before commitment to a mission-analysis-derived task), DOM-009.
