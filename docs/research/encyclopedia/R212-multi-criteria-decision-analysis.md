# R212 — Multi-Criteria Decision Analysis

> **Document ID:** R212
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R202](R202-decision-theory.md)
> **Referenced By:** [R311](R311-course-of-action-analysis.md)
> **Produces:** the scoring vocabulary a future COA-comparison feature would need
> **Feature Mapping:** FS-101 (Mission Planning), candidate future COA-comparison feature
> **Related Topics:** [R202](R202-decision-theory.md) (Decision Theory), [R214](R214-utility-theory.md) (Utility Theory), [R311](R311-course-of-action-analysis.md) (Course of Action Analysis —
> the military-specific application this topic underlies)

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

No engine feature today formally scores competing courses of action against multiple criteria — an
operator weighs Δv cost, custody confidence, ROE risk, and time pressure informally, in their head.
This topic gives the implementer the formal MCDA vocabulary needed *if* a future COA-comparison
feature ([R311](R311-course-of-action-analysis.md)'s military-specific framing) is ever built, so it is built on a real method rather than
an ad hoc weighted sum invented from scratch.

## 2. Concepts

**MCDA's core problem: comparing options that are good on different, non-commensurable axes.** A
maneuver option that's cheap in Δv but exposes a weak custody window is not directly comparable to
one that's Δv-expensive but custody-strong without an explicit method for trading the axes off — this
is precisely the situation a Blue operator faces informally on every non-trivial planning decision in
this simulator.

**Weighted-sum scoring and its pitfalls.** The simplest MCDA method — score each option on each
criterion, multiply by a weight, sum — is transparent but brittle: results are sensitive to the
weights chosen, and the method implicitly assumes the criteria are independent and linearly
substitutable (e.g. "is enough extra custody confidence always worth a fixed amount of Δv,
regardless of how much custody you already have" — usually false).

**Outranking methods (e.g. ELECTRE/PROMETHEE-style pairwise comparison).** An alternative to
weighted-sum that compares options pairwise on each criterion and looks for a dominant or
non-dominated set, without forcing every criterion onto a common numeric scale — more defensible
when criteria are qualitatively different in kind (Δv is a hard physical resource; ROE risk is a
judgment call), at the cost of not always producing a single ranked winner.

**Sensitivity of the ranking to the weighting scheme is itself information.** A genuinely robust
"best" option should rank highly across a range of plausible weightings; an option that's only best
under one specific weighting is fragile — this is [R408](R408-sensitivity-analysis.md)'s sensitivity-analysis method applied to a
decision-support context rather than a model-validation context.

## 3. Operational Context

Real course-of-action comparison in military planning ([R311](R311-course-of-action-analysis.md)'s "decision matrix" / COA comparison
step) is a textbook MCDA application — criteria like casualties risk, resource cost, time, and
political risk are explicitly non-commensurable, and staff planning doctrine teaches weighted
decision matrices and sensitivity checks as a standard tool, with the same caveats about weight-
sensitivity this topic raises.

## 4. Implementation Guidance

- **A future COA-comparison feature must let the operator see and adjust the weighting, not present
  a single computed "best" option as ground truth** — per DOM-008 §4, a fixed hidden weighting that
  resolves the comparison *for* the trainee crosses from decision support into decision-making.
- **If implementing weighted-sum scoring, run the sensitivity check from §2/[R408](R408-sensitivity-analysis.md) before presenting
  any ranking as robust** — and surface that sensitivity to the operator (e.g. "Option A wins under
  most reasonable weightings; Option B wins only if Δv is weighted very heavily") rather than hiding
  it.
- **Don't force ROE/legal-risk criteria onto the same numeric scale as Δv/time without an explicit,
  documented justification** — per DOM-009 §4, legal/ROE norms are load-bearing, not a flavor
  variable to be casually monetized into the same units as fuel cost.

## 5. Feature Mapping

A candidate future COA-comparison feature under FS-101 (Mission Planning) is the direct consumer.

## 6. Related Topics

[R202](R202-decision-theory.md) (Decision Theory), [R214](R214-utility-theory.md) (Utility Theory, the value-function question MCDA depends on), [R311](R311-course-of-action-analysis.md)
(Course of Action Analysis, the doctrinal/military-specific framing).
