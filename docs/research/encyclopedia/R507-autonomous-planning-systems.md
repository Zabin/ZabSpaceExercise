# R507 — Autonomous Planning Systems

> **Document ID:** R507
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R502](R502-autonomy-in-space-operations.md), [R506](R506-machine-reasoning.md)
> **Referenced By:** [R508](R508-future-command-and-control.md)
> **Produces:** the vocabulary for evaluating any future feature that would generate or adapt a plan with reduced human involvement
> **Feature Mapping:** any future auto-planning or auto-COA-generation feature proposal (distinct from and going beyond the human-driven COA-comparison feature in [R311](R311-course-of-action-analysis.md))
> **Related Topics:** [R502](R502-autonomy-in-space-operations.md) (Autonomy in Space Operations), [R506](R506-machine-reasoning.md) (Machine Reasoning), [R311](R311-course-of-action-analysis.md) (Course of
> Action Analysis — the human-driven comparison feature this topic's auto-generation concept goes
> beyond), DOM-008 §4

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** in-world AI primarily (a hypothetical future trainee-facing or White-Cell-facing
auto-planning feature); coding-agent implications noted in §4.

## 1. Purpose

[R311](R311-course-of-action-analysis.md) already names a *human-driven* COA-comparison feature (operator generates candidate COAs,
matrix scores them, operator selects) as a candidate future capability that never auto-selects. This
topic addresses the further, distinct step some future proposal might suggest — a system that
*generates* or *adapts* candidate plans itself, not just compares human-generated ones — and supplies
the vocabulary for evaluating such a proposal against this project's existing constraints.

## 2. Concepts

**Plan generation vs. plan comparison are categorically different capabilities.** [R311](R311-course-of-action-analysis.md)'s COA-
comparison feature operates on operator-authored candidate plans; an autonomous planning system
additionally generates the candidates themselves — this is a substantially larger capability with a
substantially larger set of design risks (an auto-generated "doctrinally implausible" plan, an
auto-generated plan that narrows the operator's own candidate-generation practice, the pedagogical
cost of removing the COA-development skill [R311](R311-course-of-action-analysis.md) identifies as worth training).

**Plan adaptation/replanning under changing conditions.** A more autonomous planning system might not
just generate an initial plan but adapt it as conditions change during execution — this raises the
decision-authority question (DOM-008 §4) acutely: an adapting plan that re-decides without operator
sign-off each time is functionally closer to level-4 autonomous decision-making ([R210](R210-decision-support-systems.md)/[R503](R503-ai-decision-support.md)) than a
one-time initial-plan suggestion would be, even if each individual adaptation is framed as a
"recommendation."

**The pedagogical cost of removing a trainable skill.** Per MSTR-003's plan-execute-as-the-unit-of-
learning framing and [R311](R311-course-of-action-analysis.md)'s COA-development emphasis on generating genuinely distinct options, an
autonomous planning system that generates plans *for* the trainee risks removing exactly the skill
(plan generation/comparison/judgment) the exercise exists to train — this is a sharper version of
[R503](R503-ai-decision-support.md)'s "always-correct advisor undermines the exercise" concern, since plan generation is even more
central to the trained skill than reacting to a recommendation.

**Where autonomous planning is appropriate in real space operations vs. in a training exercise.**
Real autonomous mission planning (e.g. onboard autonomous re-tasking for some modern platforms) is
appropriate specifically because operational efficiency, not operator skill development, is the goal
— this is the opposite of this simulator's PME context, where operator skill development is the
explicit point (CLAUDE.md), which is the central reason an autonomous-planning feature here needs
much stronger pedagogical justification than the same feature would in an operational (non-training)
context.

## 3. Operational Context

Autonomous planning systems are an active and growing area of real space-operations practice
(onboard autonomous re-tasking, automated conjunction-avoidance replanning) precisely because
operational efficiency benefits from reduced human-in-the-loop latency — but this efficiency
rationale does not transfer to a training context whose explicit purpose (CLAUDE.md, MSTR-003) is
developing the human operator's own planning judgment, which is the central tension this topic exists
to name before any such feature is proposed.

## 4. Implementation Guidance

- **Any future auto-plan-generation proposal must be justified pedagogically, not just
  operationally** — per the skill-removal concern above, "this would make the simulator more
  realistic/efficient" is an insufficient justification in a PME training context whose explicit goal
  is developing the trainee's own planning judgment.
- **A future plan-adaptation/replanning feature must require explicit operator sign-off on each
  adaptation**, not silently re-decide, to stay within DOM-008 §4's advisor-only constraint — treat
  repeated silent re-adaptation as functionally level-4 even if each step is individually framed as
  advisory.
- **If an auto-planning feature is ever pursued, ground its plan-generation logic symbolically
  ([R506](R506-machine-reasoning.md))**, consistent with the engine's determinism invariant, rather than via a learned/adaptive
  approach.
- **Distinguish clearly, in any design document, between [R311](R311-course-of-action-analysis.md)'s human-driven COA-comparison feature
  (already-scoped, lower-risk) and this topic's auto-generation concept (currently unscoped,
  higher-risk)** — conflating the two understates the latter's design risk.

## 5. Feature Mapping

Any future auto-planning/auto-COA-generation feature is the direct consumer; none exists or is
currently authorized — this remains forward-looking context.

## 6. Related Topics

[R502](R502-autonomy-in-space-operations.md) (Autonomy in Space Operations), [R506](R506-machine-reasoning.md) (Machine Reasoning), [R311](R311-course-of-action-analysis.md) (Course of Action Analysis),
DOM-008 §4.
