# R507 — Autonomous Planning Systems

> **Document ID:** R507
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R502](R502-autonomy-in-space-operations.md), [R506](R506-machine-reasoning.md)
> **Referenced By:** [R508](R508-future-command-and-control.md)
> **Produces:** the vocabulary for evaluating any future feature that would generate or adapt a plan with reduced human involvement
> **Feature Mapping:** any future auto-planning or auto-COA-generation feature proposal (distinct from and going beyond the human-driven COA-comparison feature in [R311](R311-course-of-action-analysis.md))
> **Related Topics:** [R502](R502-autonomy-in-space-operations.md) (Autonomy in Space Operations), [R506](R506-machine-reasoning.md) (Machine Reasoning), [R311](R311-course-of-action-analysis.md) (Course of
> Action Analysis — the human-driven comparison feature this topic's auto-generation concept goes
> beyond), DOM-008 §4
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A/B real flight-precedent sources — see §3 Sources)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** in-world AI primarily (a hypothetical future trainee-facing or White-Cell-facing
auto-planning feature); coding-agent implications noted in §5.

## 1. Purpose

[R311](R311-course-of-action-analysis.md) already names a *human-driven* COA-comparison feature (operator generates candidate COAs,
matrix scores them, operator selects) as a candidate future capability that never auto-selects. This
topic addresses the further, distinct step some future proposal might suggest — a system that
*generates* or *adapts* candidate plans itself, not just compares human-generated ones — and supplies
the vocabulary for evaluating such a proposal against this project's existing constraints.

## 2. Scope

Covers: the plan-generation-vs-plan-comparison distinction, real flight-proven autonomous
planning/replanning precedent (NASA's EO-1 Autonomous Sciencecraft, SpaceX Starlink's automated
collision avoidance), and the operational-efficiency-vs-training-pedagogy tension specific to
applying either precedent in this simulator. Does **not** cover: the human-driven COA-comparison
feature that stops short of auto-generation ([R311](R311-course-of-action-analysis.md)'s job), the
symbolic-vs-sub-symbolic implementation choice for a planner's internal reasoning
([R506](R506-machine-reasoning.md)'s job, assumed established here), or the C2-architecture question
of where in a future system an autonomous planner would sit
([R508](R508-future-command-and-control.md)'s job).

## 3. Concepts

**Plan generation vs. plan comparison are categorically different capabilities.** [R311](R311-course-of-action-analysis.md)'s COA-
comparison feature operates on operator-authored candidate plans; an autonomous planning system
additionally generates the candidates themselves — this is a substantially larger capability with a
substantially larger set of design risks (an auto-generated "doctrinally implausible" plan, an
auto-generated plan that narrows the operator's own candidate-generation practice, the pedagogical
cost of removing the COA-development skill [R311](R311-course-of-action-analysis.md) identifies as worth training).

**Real flight-proven autonomous planning precedent exists, and it clusters around two distinct
patterns.** NASA's **Autonomous Sciencecraft Experiment**, flown continuously on the *Earth
Observing-1* mission since 2003, used the **CASPER** onboard continuous planner in a three-layer
architecture (CASPER as the deliberative planning layer, a scripting execution layer, and the base
flight-software skills layer) to replan science-collection activities onboard in response to
onboard-detected science events, without waiting for ground command
([Chien et al., *Integrated AI in Space: The Autonomous Sciencecraft on Earth Observing One*, AAAI 2006](https://cdn.aaai.org/AAAI/2006/AAAI06-238.pdf)).
This is **goal-directed onboard replanning** (ECSS level E4 in [R502](R502-autonomy-in-space-operations.md)'s vocabulary) for a
low-consequence, fully reversible task (which science target to image next). By contrast, SpaceX's
**Starlink** constellation runs fully autonomous, no-human-in-the-loop collision-avoidance maneuver
decisions onboard each satellite — pulling conjunction-tracking data, evaluating collision
probability against a stated maneuver threshold, and firing thrusters without ground sign-off, while
keeping ground personnel on call for external-operator coordination, not for the maneuver decision
itself ([Starlink, *Space Station Conjunction Avoidance*, SAT-51385 public filing](https://starlink.com/public-files/space_station_conjunction_avoidance.pdf)).
This is **autonomous execution of a single, narrowly-scoped, time-critical safety decision** — closer
to [R502](R502-autonomy-in-space-operations.md)'s "collision avoidance is the classic case for higher autonomy" example than to CASPER's
broader goal-directed replanning. Both are real, flight-proven, multi-year-operational precedents —
neither is speculative — but they represent different points on the autonomy spectrum, and a future
proposal citing "autonomous planning is already flight-proven" should specify which pattern it means,
since the design-risk profile differs substantially between them.

**Plan adaptation/replanning under changing conditions.** A more autonomous planning system might not
just generate an initial plan but adapt it as conditions change during execution — CASPER's continuous
onboard replanning (§3 above) is exactly this pattern in its real precedent form. This raises the
decision-authority question (DOM-008 §4) acutely: an adapting plan that re-decides without operator
sign-off each time is functionally closer to level-4 autonomous decision-making ([R210](R210-decision-support-systems.md)/[R503](R503-ai-decision-support.md)) than a
one-time initial-plan suggestion would be, even if each individual adaptation is framed as a
"recommendation" — this is true of CASPER's real design (it does not ask permission per replan) and
would be equally true of a hypothetical in-simulator analog.

**The pedagogical cost of removing a trainable skill.** Per MSTR-003's plan-execute-as-the-unit-of-
learning framing and [R311](R311-course-of-action-analysis.md)'s COA-development emphasis on generating genuinely distinct options, an
autonomous planning system that generates plans *for* the trainee risks removing exactly the skill
(plan generation/comparison/judgment) the exercise exists to train — this is a sharper version of
[R503](R503-ai-decision-support.md)'s "always-correct advisor undermines the exercise" concern, since plan generation is even more
central to the trained skill than reacting to a recommendation.

**Where autonomous planning is appropriate in real space operations vs. in a training exercise.**
Both CASPER (efficiency: more science return per ground-contact-limited downlink budget) and Starlink
(safety: a maneuver decision faster than any ground-in-the-loop process could execute at
constellation scale) are justified in their real deployments by operational efficiency or safety, not
by any concern for training a human's judgment — this is the opposite of this simulator's PME
context, where operator skill development is the explicit point (CLAUDE.md), which is the central
reason an autonomous-planning feature here needs much stronger pedagogical justification than either
real precedent needed operationally.

### Sources

- *Chien, S. et al. (2006). Integrated AI in Space: The Autonomous Sciencecraft on Earth Observing
  One.* Proceedings of AAAI 2006 —
  [live](https://cdn.aaai.org/AAAI/2006/AAAI06-238.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://cdn.aaai.org/AAAI/2006/AAAI06-238.pdf)
  · accessed 2026-07-02.
- *Starlink. Space Station Conjunction Avoidance, SAT-51385 public filing* —
  [live](https://starlink.com/public-files/space_station_conjunction_avoidance.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://starlink.com/public-files/space_station_conjunction_avoidance.pdf)
  · accessed 2026-07-02.

## 4. Operational Context

Autonomous planning systems are an active and growing area of real space-operations practice — EO-1's
CASPER planner has been in continuous operational use since 2003 (over two decades of flight history)
and Starlink's autonomous collision-avoidance system executes on the order of tens of thousands of
maneuvers per year at constellation scale — precisely because operational efficiency and safety
benefit from reduced human-in-the-loop latency. But this efficiency/safety rationale does not
transfer to a training context whose explicit purpose (CLAUDE.md, MSTR-003) is developing the human
operator's own planning judgment, which is the central tension this topic exists to name before any
such feature is proposed.

### Sources

Uses the same sources cited inline in §3 (Chien et al. 2006; Starlink SAT-51385); no additional
sources introduced in this section.

## 5. Implementation Guidance

- **Any future auto-plan-generation proposal must be justified pedagogically, not just
  operationally** — per the skill-removal concern above, "this would make the simulator more
  realistic/efficient" is an insufficient justification in a PME training context whose explicit goal
  is developing the trainee's own planning judgment; citing CASPER or Starlink as flight precedent
  does not by itself supply that justification, since neither system's real-world deployment needed
  one.
- **A future plan-adaptation/replanning feature must require explicit operator sign-off on each
  adaptation**, not silently re-decide like CASPER's real onboard replanning does, to stay within
  DOM-008 §4's advisor-only constraint — treat repeated silent re-adaptation as functionally level-4
  even if each step is individually framed as advisory.
- **A narrowly-scoped, time-critical safety decision (the Starlink pattern) is a categorically
  different, lower-risk proposal than a broad goal-directed replanner (the CASPER pattern)** — a
  future conjunction-avoidance-style automation proposal for this simulator should be evaluated
  against the Starlink precedent specifically, not conflated with a general auto-planning feature.
- **If an auto-planning feature is ever pursued, ground its plan-generation logic symbolically
  ([R506](R506-machine-reasoning.md))**, consistent with the engine's determinism invariant, rather than via a learned/adaptive
  approach.
- **Distinguish clearly, in any design document, between [R311](R311-course-of-action-analysis.md)'s human-driven COA-comparison feature
  (already-scoped, lower-risk) and this topic's auto-generation concept (currently unscoped,
  higher-risk)** — conflating the two understates the latter's design risk.

## 6. Feature Mapping

Any future auto-planning/auto-COA-generation feature is the direct consumer; none exists or is
currently authorized — this remains forward-looking context.

## 7. Related Topics

[R502](R502-autonomy-in-space-operations.md) (Autonomy in Space Operations), [R506](R506-machine-reasoning.md) (Machine Reasoning), [R311](R311-course-of-action-analysis.md) (Course of Action Analysis),
DOM-008 §4.
