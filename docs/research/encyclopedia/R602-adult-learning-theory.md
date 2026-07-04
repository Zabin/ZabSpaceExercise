# R602 — Adult Learning Theory

> **Document ID:** R602
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R601](R601-instructional-systems-design.md)
> **Referenced By:** [R604](R604-cognitive-load-and-scaffolding.md), [R606](R606-minimalist-and-procedural-documentation.md)
> **Produces:** the audience-model that governs manual tone/structure decisions in NFR-3600
> **Feature Mapping:** NFR-3600 (learner-appropriate presentation)
> **Related Topics:** [R601](R601-instructional-systems-design.md) (Instructional Systems Design — the
> *method* this topic's audience assumptions should be applied through),
> [R606](R606-minimalist-and-procedural-documentation.md) (Minimalist & Procedural Documentation,
> which operationalizes this topic's self-direction/relevance assumptions into manual prose)

> **Verification note (this authoring pass):** citations below were sourced via live web search and
> corroborated across ≥2 independent results per claim; direct WebFetch of source pages was blocked
> by this session's egress policy (proxy denial on external hosts, per `/root/.ccr/README.md`) and is
> deferred to this corpus's separate formal verification pass
> ([`../10-sources-and-methodology.md`](../10-sources-and-methodology.md) §5.3).

> **Last Reviewed:** 2026-07-04
> **Primary Sources Consulted:** 1

[↑ Tier R600 index](R600-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The simulator's stated audience is **CAF/allied space operators in facilitated PME settings** —
adults, already professionally competent in an adjacent domain, learning a new tool and the doctrine
it encodes (GDS-01 §2; strategic-assumptions-register A8). Andragogy (Knowles' theory of adult
learning) is the formal grounding for *why* this audience needs manuals and vignettes shaped
differently than a general-audience tutorial would be, and this topic gives
`08-training-manual-authoring`/`09-training-manual-review` a concrete checklist to apply that
difference against, rather than an unstated assumption everyone applies inconsistently.

## 2. Scope

Covers Malcolm Knowles' andragogy: the six core assumptions distinguishing adult learners from
pedagogy's child-learner assumptions, and their direct implications for manual tone and structure.
Does **not** cover the systematic design *process* those assumptions should be applied within
([R601](R601-instructional-systems-design.md)), cognitive-load management during complex-system
training ([R604](R604-cognitive-load-and-scaffolding.md)), or the minimalist-writing craft that turns
these assumptions into actual prose ([R606](R606-minimalist-and-procedural-documentation.md)).

## 3. Concepts

**Andragogy vs. pedagogy: adults are not big children in a classroom.** Malcolm Knowles' adult
learning theory rests on six assumptions distinguishing how adults engage with learning, relative to
child-learner pedagogy: (1) **need to know** — adults want to understand *why* before engaging, not
just comply; (2) **self-directed learning** — adults prefer autonomy over pace, method, and
self-assessment of their own progress; (3) **prior experience as a resource** — adults integrate
personal/professional experience into new learning rather than starting from a blank slate;
(4) **self-concept** — adults resist being treated as dependent; (5) **readiness to learn** — tied
to a real task or role, not an abstract curriculum sequence; (6) **motivation** — predominantly
internal (competence, respect, problem-solving) over external reward
([Knowles' six assumptions, corroborated across `learningrevolution.net`](https://www.learningrevolution.net/adult-learning-theory/),
[Growth Engineering](https://www.growthengineering.co.uk/adult-learning-theory/), and
[University of Phoenix](https://www.phoenix.edu/articles/education/adult-learning-theory-and-the-principles-of-andragogy.html)).

**"Need to know" is the assumption most directly load-bearing for this corpus.** Every manual section
under `docs/training/` already follows a "why this matters, then how" implicit pattern (e.g.
`13-blue-cell-manual.md` BLU-4 opens with "You don't get the sky for free" before the SDA tasking
procedure) — andragogy names this as a requirement, not a stylistic preference: an adult professional
reading a procedure with no stated rationale disengages faster than a child-learner would, because the
need-to-know assumption is specifically about *professional* adults evaluating whether instruction is
worth their attention.

**Self-direction implies a manual is a reference, not a forced sequence.** Adults prefer to choose
their own path through material and self-assess progress — this is the direct grounding for why the
training corpus is organized as independently-retrievable modules with an index router (per
`DOCUMENTATION-PLAN.md`'s goals) rather than a single linear document a reader must traverse start to
finish, and for why the vignette learning path (`training/16`) is framed as a *recommendation* a
facilitator can enter at any rung matched to trainee level, not a mandatory single-file march.

### Sources

- *Adult Learning Theory & Andragogy: Knowles' 6 Principles* — corroborated summary across three independent listings — [live](https://www.learningrevolution.net/adult-learning-theory/) · [snapshot](https://web.archive.org/web/2026*/https://www.learningrevolution.net/adult-learning-theory/) · accessed 2026-07-04.
- *What Is Malcolm Knowles' Adult Learning Theory?* — Growth Engineering — [live](https://www.growthengineering.co.uk/adult-learning-theory/) · [snapshot](https://web.archive.org/web/2026*/https://www.growthengineering.co.uk/adult-learning-theory/) · accessed 2026-07-04.
- *Adult learning theory and the principles of andragogy* — University of Phoenix — [live](https://www.phoenix.edu/articles/education/adult-learning-theory-and-the-principles-of-andragogy.html) · [snapshot](https://web.archive.org/web/2026*/https://www.phoenix.edu/articles/education/adult-learning-theory-and-the-principles-of-andragogy.html) · accessed 2026-07-04.

## 4. Operational Context

PME programs across NATO militaries assume andragogy implicitly in how they run courses: a mid-career
officer sitting through a lecture that re-derives first-year-undergraduate reasoning disengages
precisely because the "need to know" and "prior experience as a resource" assumptions are violated —
the officer already has professional judgment to integrate the new material against, and a course
that ignores that is worse than one that names it and builds on it. The same dynamic applies at
tool-training scale: a CAF space operator learning this simulator already has orbital-operations or
adjacent professional judgment; the manuals should activate that judgment (Merrill's principle,
[R601](R601-instructional-systems-design.md)), not treat the reader as a blank slate.

## 5. Implementation Guidance

- **Every manual section should open with a one-line "why this matters" before the procedure** —
  already the corpus's practice; this topic makes it a checked convention rather than an accident.
  `09-training-manual-review`'s pedagogy dimension should flag a section that opens directly with
  steps and no stated rationale.
- **Never force a linear read order.** Keep the module-plus-index-router structure
  (`DOCUMENTATION-PLAN.md` goals 1-2) rather than merging modules into a monolith "for completeness" —
  self-direction is a *design constraint*, not a nice-to-have, given this audience.
- **Don't write down to the audience.** Assume professional-adult prior competence in an adjacent
  domain (per assumption A8's CAF/allied-operator framing); jargon specific to *this tool* should be
  introduced or glossary-linked (NFR-3600), but doctrine/orbital-mechanics vocabulary the audience
  already plausibly knows should not be over-explained at the expense of module length (NFR-3500).
- **Frame role-scoped manuals around the trainee's actual role-readiness moment** (assumption 5,
  "readiness to learn tied to a real task"), which is exactly why FR-11110 requires role-scoped
  coverage rather than one undifferentiated manual — a Blue operator's readiness moment is defensive
  tasking, not Red's offensive sequencing, even though the underlying mechanics overlap.

## 6. Feature Mapping

NFR-3600 (learner-appropriate presentation) is this topic's most direct consumer — its citation
requirement ("pedagogical choices... cite their R600 grounding") is satisfied by this document for
any audience-tone decision. FR-11110's role-scoped-coverage rationale traces to assumption 5 above.

## 7. Related Topics

[R601](R601-instructional-systems-design.md) (Instructional Systems Design, the process these
assumptions should be applied within), [R604](R604-cognitive-load-and-scaffolding.md) (Cognitive Load
& Scaffolding, managing complexity for this same professional-adult audience),
[R606](R606-minimalist-and-procedural-documentation.md) (Minimalist & Procedural Documentation, the
writing craft that turns self-direction/need-to-know into actual prose), GDS-01 §2 (intended users),
strategic-assumptions-register A8 (training-audience assumption).
