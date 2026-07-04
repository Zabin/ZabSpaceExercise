# R202 — Decision Theory

> **Document ID:** R202
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R201](R201-probability-and-bayesian-reasoning.md)
> **Referenced By:** [R203](R203-game-theory.md), [R209](R209-planning-theory.md), [R210](R210-decision-support-systems.md), [R212](R212-multi-criteria-decision-analysis.md), [R214](R214-utility-theory.md), [R607](R607-assessment-of-learning-in-wargames.md), MSTR-003
> **Produces:** the formal vocabulary behind "plan under uncertainty" as MSTR-003 §3 frames it
> **Feature Mapping:** FS-201 (Competency Assessment), FS-105 (Spacecraft Operations)
> **Related Topics:** [R201](R201-probability-and-bayesian-reasoning.md) (Probability), [R206](R206-bounded-rationality.md) (Bounded Rationality — the realistic counterpart to
> this topic's idealized models), [R214](R214-utility-theory.md) (Utility Theory), DOM-002 §4 (the measurement dimensions this
> topic's vocabulary underlies)

> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Every order an operator issues in this simulator is a decision made under risk or uncertainty about
geometry, custody, and adversary intent. This topic gives the implementer the standard decision-theory
vocabulary (decisions under risk vs. uncertainty, expected value, dominance) needed to read MSTR-003's
educational claims and DOM-002's assessment dimensions precisely, rather than treating "good
decision" as an unanalyzed intuition.

## 2. Scope

Covers the formal vocabulary of decisions under risk vs. uncertainty (the Knightian distinction),
expected value as an idealized baseline, dominance/admissibility, and minimax-regret. Does **not**
cover the realistic, bounded departure from these idealized criteria ([R206](R206-bounded-rationality.md),
this topic's necessary corrective), the multi-attribute value-combination problem
([R212](R212-multi-criteria-decision-analysis.md)/[R214](R214-utility-theory.md)), or strategic
multi-agent interaction ([R203](R203-game-theory.md)).

## 3. Concepts

**Decision under risk vs. decision under uncertainty.** Risk means outcome probabilities are known
or estimable (e.g. Pₖ from `engage.kill_probability_from_class` — [R117](R117-directed-energy-and-kinetic-effects.md)); uncertainty means they are
not reliably knowable (e.g. Red's actual intent behind an ambiguous RPO approach) — the classic
"measurable risk" vs. "unmeasurable uncertainty" distinction
([Knight, F. H., *Risk, Uncertainty and Profit*, 1921](https://www.econlib.org/library/Knight/knRUP.html)
([Wayback](https://web.archive.org/web/2026/https://www.econlib.org/library/Knight/knRUP.html))). The simulator
mixes both: effect resolution is risk (a stated probability resolves via the seeded RNG), but the
operator's *custody-based read of the situation* before issuing the order is uncertainty, since the
true probability of Red's posture is not given to the player.

**Expected value as the rational-actor baseline.** Expected value (`Σ P(outcome) × value(outcome)`)
is the idealized decision criterion this topic provides as a *baseline*, not a prescription — [R206](R206-bounded-rationality.md)
(Bounded Rationality) explains why real operators, and the simulator's pedagogy, do not expect or
require literal EV-maximizing play.

**Dominance and admissibility.** An option that is at least as good as another in every state of the
world, and strictly better in at least one, dominates it and can be eliminated from consideration
without computing probabilities — a useful screening step for COA comparison ([R212](R212-multi-criteria-decision-analysis.md), [R311](R311-course-of-action-analysis.md)) before any
weighting/probability estimation is needed.

**Regret as an alternative criterion.** Minimax-regret (choosing the option whose worst-case
deviation from the best-in-hindsight choice is smallest) is a decision criterion that doesn't require
probability estimates at all — relevant where Red's doctrine/intent is genuinely unknown rather than
merely probabilistic, a common framing for White Cell scenario design ([R301](R301-campaign-design.md), [R311](R311-course-of-action-analysis.md))
— formalized as the minimax-regret criterion
([Savage, L. J., *The Foundations of Statistics*, 1954](https://archive.org/details/foundationsofsta0000sava)
([Wayback](https://web.archive.org/web/2026/https://archive.org/details/foundationsofsta0000sava))).

### Sources

- *Knight, F. H., "Risk, Uncertainty and Profit"* (1921) — [live](https://www.econlib.org/library/Knight/knRUP.html)
  · [snapshot](https://web.archive.org/web/2026/https://www.econlib.org/library/Knight/knRUP.html)
  · accessed 2026-07-02.
- *Savage, L. J., "The Foundations of Statistics"* (1954) — [live](https://archive.org/details/foundationsofsta0000sava)
  · [snapshot](https://web.archive.org/web/2026/https://archive.org/details/foundationsofsta0000sava)
  · accessed 2026-07-02.

## 4. Operational Context

Real operational decision-making under contested-space conditions is rarely a clean expected-value
calculation — commanders weigh probable adversary intent, escalation risk, and resource cost using
mixed criteria (risk-averse for irreversible kinetic options, EV-seeking for cheap reversible
options), which is exactly the asymmetry MSTR-003 §5's "reversibility as a teaching gradient" is
designed to make visible and practicable.

## 5. Implementation Guidance

- **A future COA-comparison feature ([R212](R212-multi-criteria-decision-analysis.md), [R311](R311-course-of-action-analysis.md)) should let the operator see the decision criterion
  being applied** (EV, dominance, minimax-regret), not silently compute one and present a single
  recommended choice — per DOM-008 §4, an advisor surfaces information, it does not decide.
- **Don't conflate the engine's effect-resolution probability (risk) with the operator's situational
  uncertainty** — a UI element showing "Pₖ: 62%" is showing risk; it says nothing about whether the
  operator's belief that the target is hostile (an uncertainty judgment, [R102](R102-space-domain-awareness.md)/[R105](R105-custody-theory.md)) is itself
  correct.
- **A new assessment dimension (DOM-002 candidate) that scores "decision quality" must state which
  decision-theory criterion it is scoring against** (EV-consistency, dominance violations, etc.) —
  an unstated criterion makes the score unfalsifiable and therefore unusable for DOM-005 validation.

## 6. Feature Mapping

FS-201 (Competency Assessment) is the direct future consumer — any "decision quality" rubric
dimension must cite which criterion in this topic it operationalizes.

## 7. Related Topics

[R201](R201-probability-and-bayesian-reasoning.md) (Probability, the input this topic's calculations consume), [R206](R206-bounded-rationality.md) (Bounded Rationality, the
realistic counterpart), [R214](R214-utility-theory.md) (Utility Theory, formalizing the "value" term in expected value), [R212](R212-multi-criteria-decision-analysis.md)
(Multi-Criteria Decision Analysis, the applied COA-comparison case).
