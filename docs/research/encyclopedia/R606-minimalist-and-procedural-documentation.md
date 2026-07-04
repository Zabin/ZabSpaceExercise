# R606 — Minimalist & Procedural Documentation

> **Document ID:** R606
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R602](R602-adult-learning-theory.md)
> **Referenced By:** [R608](R608-software-onboarding-and-tutorial-design.md)
> **Produces:** the theoretical grounding for whether/how the per-cell manual layout should be
> restructured (backlog BL-0026) — this topic supplies the craft principles that decision needs, not
> the decision itself
> **Feature Mapping:** NFR-3500 (modularity/retrievability of training modules), FR-11110 (role-scoped
> coverage — the *shape* question BL-0026 raises)
> **Related Topics:** [R602](R602-adult-learning-theory.md) (Adult Learning Theory — self-direction and
> need-to-know, which this topic operationalizes into prose), [R608](R608-software-onboarding-and-tutorial-design.md)
> (Software Onboarding & Tutorial Design, applying this topic's minimalism to in-app guidance),
> `docs/training/15-manual-traceability.md` §15.3 (the currency mechanism this topic's task-oriented
> structure makes cheaper to maintain)

> **Verification note (this authoring pass):** citations below were sourced via live web search and
> corroborated across ≥2 independent results per claim; direct WebFetch of source pages was blocked
> by this session's egress policy (proxy denial on external hosts, per `/root/.ccr/README.md`) and is
> deferred to this corpus's separate formal verification pass
> ([`../10-sources-and-methodology.md`](../10-sources-and-methodology.md) §5.3).

> **Last Reviewed:** 2026-07-04
> **Primary Sources Consulted:** 1

[↑ Tier R600 index](R600-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Backlog **BL-0026** records an open design question: FR-11110 mandates role-scoped *coverage*, not
the current per-cell-monolith manual layout, and whether to restructure toward something more
task-oriented is deferred until this topic (named explicitly in the backlog entry) grounds it. This
topic is that grounding — John Carroll's minimalist-documentation research, the strongest available
theory of what makes procedural technical writing actually usable, applied to the specific question of
whether "one manual per cell" or "one module per task" better serves this corpus's audience.

## 2. Scope

Covers John Carroll's minimalist-instruction principles for technical/procedural documentation: the
critique of comprehensive "cover everything" manuals, the case for real-task-centered organization, and
error-recovery-as-a-designed-topic rather than an afterthought. Does **not** cover the adult-learner
assumptions this craft operationalizes ([R602](R602-adult-learning-theory.md)), in-app tutorial-specific
patterns ([R608](R608-software-onboarding-and-tutorial-design.md)), or make the restructuring decision
itself (BL-0026 remains a design question for `08-training-manual-authoring` to resolve, informed by
this topic, not settled here).

## 3. Concepts

**Minimalism: the comprehensive "systems approach" manual underperforms a real-task-centered one.**
John Carroll's *The Nurnberg Funnel* is the foundational critique of the traditional "systems approach"
to technical manuals — comprehensive, feature-by-feature coverage building from simple to complex —
arguing from direct study of users' actual failures that this approach "outperformed... in every
relevant way" by a minimalist alternative organized around real, immediately-achievable tasks rather
than exhaustive feature enumeration
([Carroll, J. M. (1990). *The Nurnberg Funnel: Designing Minimalist Instruction for Practical Computer
Skill*. MIT Press](https://mitpress.mit.edu/9780262031639/the-nurnberg-funnel/)). Carroll's title itself
is a rebuke: a "funnel" implies pouring comprehensive knowledge into a learner's head, which he argues
is precisely the wrong model.

**Three concrete minimalist principles.** (1) **Support real, meaningful tasks from the start** — a
learner should complete a genuine, useful task immediately, not work through drills before touching
anything real; (2) **let the learner determine the sequence, not the manual** — since the learner (not
the system) actually drives what they need next, comprehensive front-to-back reading is the wrong
default expectation; (3) **design for error recognition and recovery as a first-class instructional
event, not a failure mode to be prevented by exhaustive up-front warning** — errors are treated as
learning opportunities the documentation should support, not eliminate by over-explaining everything
that could go wrong (same source as above).

**Applied to this corpus's own layout question.** Carroll's critique cuts specifically against
"comprehensive coverage" organization — which is exactly what a per-cell *monolith* risks becoming if
it tries to be each role's single, exhaustive reference rather than a task-centered procedure layer.
The current per-cell manuals (`training/12-14`) already lean minimalist in one respect (they deep-link
shared concept modules rather than re-explaining mechanics), which is the right instinct; the open
BL-0026 question is whether task-oriented modules cutting *across* cells (e.g., "diagnosing an attack,"
a task both Blue and Red perform) would satisfy Carroll's real-task-centered principle *better* than
per-cell files organized primarily by role rather than by task. This topic does not resolve that
question — it supplies the exact craft standard the eventual decision should be judged against:
whichever structure lets a reader accomplish a real task fastest, with the least material irrelevant to
that task, wins.

### Sources

- *Carroll, J. M. (1990). The Nurnberg Funnel: Designing Minimalist Instruction for Practical Computer Skill. MIT Press* — publisher page — [live](https://mitpress.mit.edu/9780262031639/the-nurnberg-funnel/) · [snapshot](https://web.archive.org/web/2026*/https://mitpress.mit.edu/9780262031639/the-nurnberg-funnel/) · accessed 2026-07-04.

## 4. Operational Context

Technical-writing practice broadly converged on task-oriented, minimalist documentation over the
comprehensive-reference model Carroll critiqued — modern software help systems, API quickstarts, and
procedural runbooks are near-universally organized around "how do I do X" rather than "here is
everything the system can do, alphabetically." This simulator's own `DOCUMENTATION-PLAN.md` (goals 1-2:
single-topic files an agent/reader can read whole, an index at every level) already embodies Carroll's
principles for the *engineering* documentation; this topic is the citation that says the same craft
applies to the *training* corpus, closing a gap where the engineering docs had an implicit rationale
and the training docs did not.

## 5. Implementation Guidance

- **Judge any manual restructuring (BL-0026) by task-completion speed, not comprehensiveness.** A
  proposed structure should be tested against: "can a Blue operator who just hit a jam signature find
  the diagnosis procedure fast, with minimal irrelevant material in the way" — not "does this cover
  every Blue-relevant mechanic somewhere."
  ([R601](R601-instructional-systems-design.md)'s backward-design method is the right process to run
  this test through; this topic supplies the success criterion.)
- **Preserve and extend the deep-link-don't-duplicate convention** the per-cell manuals already use —
  Carroll's critique specifically targets exhaustive re-explanation, and a manual that duplicates
  `05-core-concepts.md`'s content inside each cell manual would be regressing toward the "systems
  approach" he found underperforms.
- **Every procedure should assume the reader is mid-task, not studying** — open with the task ("You
  don't get the sky for free" before SDA tasking, already the corpus's practice), not with feature
  taxonomy.
- **Don't design manual sections to prevent every possible error by exhaustive up-front warning.**
  Where a mistake is recoverable (a cancelled order, a mis-tasked sensor), the manual should say how to
  recover, not attempt to warn away every way to make the mistake — consistent with Carroll's
  error-recovery-as-instructional-event principle and with this simulator's own plan-first,
  cancel-before-uplink design.

## 6. Feature Mapping

NFR-3500 (modularity/retrievability) is this topic's most direct requirement-level target. FR-11110's
role-scoped-coverage mandate is the requirement BL-0026 questions the *implementation shape* of — this
topic is the citation `08-training-manual-authoring` should reference when that restructuring decision
is finally made.

## 7. Related Topics

[R602](R602-adult-learning-theory.md) (Adult Learning Theory, self-direction/need-to-know assumptions
this topic operationalizes into prose craft), [R608](R608-software-onboarding-and-tutorial-design.md)
(Software Onboarding & Tutorial Design, minimalism applied to in-app rather than document-based
guidance), `docs/pipeline/backlog.md` BL-0026 (the design question this topic was authored to unblock).
