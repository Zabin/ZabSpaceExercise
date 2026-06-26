# R214 — Utility Theory

> **Document ID:** R214
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R202
> **Referenced By:** R212
> **Produces:** the vocabulary for formalizing "value"/risk-attitude that R202's expected-value math and R212's MCDA scoring both depend on
> **Feature Mapping:** candidate future COA-comparison feature under FS-101
> **Related Topics:** R202 (Decision Theory), R212 (Multi-Criteria Decision Analysis — the applied
> consumer of this topic's value-function concept)

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

R202's expected-value criterion silently assumes a "value" function exists to multiply probabilities
against — utility theory is the formal account of what that value function is and why it is not
simply the raw outcome magnitude. This topic exists so a future scoring or COA-comparison feature
doesn't accidentally treat "value" as a free, self-evident quantity.

## 2. Concepts

**Utility is a function of outcome, not the outcome itself.** Two operators can value "losing one
satellite" very differently depending on risk attitude, mission criticality, and stakes — utility
theory formalizes outcome value as a function `u(outcome)`, distinct from a raw physical measure
(Δv spent, satellites lost), precisely so that risk attitude can be made explicit rather than
assumed away.

**Risk aversion, risk neutrality, risk seeking — the shape of the utility curve.** A risk-averse
utility function is concave (diminishing marginal value of gains, increasingly painful marginal
losses); risk-neutral is linear (utility equals expected raw value); risk-seeking is convex. Real
operational decision-makers facing an irreversible kinetic decision (R117) are typically modeled as
risk-averse with respect to escalation/debris consequences — a key reason MSTR-003 §5's "consequence-
confirm" gate exists structurally, not just as a UI nag: it forces a deliberate risk-attitude check
at exactly the highest-stakes decision point.

**Non-commensurable value dimensions need an explicit utility function to combine, not an implicit
one.** Combining Δv cost, custody risk, and escalation risk into a single comparable "value" (as
R212's MCDA weighting requires) is exactly a multi-attribute utility theory problem — and the
formal warning is the same as R212's: an implicit, unstated trade-off rate between dimensions is
doing real normative work and should be made visible, not buried in a weighted-sum formula's
constants.

**Utility is not the same as the engine's declared severity tags.** `debris_risk="high"` (R117 §2)
is a *declared property of the effect*, not a utility value — converting it into a number for a
COA-comparison feature requires an explicit utility judgment (how costly is "high" debris risk
relative to a given Δv expenditure), and that judgment should be stated, not silently embedded in a
conversion constant.

## 3. Operational Context

Military and policy risk analysis routinely makes risk-attitude explicit (a force-protection
posture is an explicit policy about risk aversion toward casualties, not a raw EV calculation),
exactly the same formal move utility theory describes — stating the risk attitude as policy, rather
than letting it default silently to risk-neutral EV-maximization, is standard practice precisely
because the default is rarely the actually-intended posture.

## 4. Implementation Guidance

- **Any future feature that converts a declared severity tag (e.g. `debris_risk`) into a numeric
  score for ranking/comparison must state the conversion as an explicit utility judgment**, ideally
  configurable by White Cell/scenario rather than hardcoded, since the "correct" risk attitude is a
  policy choice, not a fact derivable from the engine.
- **Don't default a comparison feature to risk-neutral EV-maximization without saying so** — per
  MSTR-003 §5's reversibility-as-teaching-gradient, the pedagogically correct default for kinetic
  options is closer to risk-averse, and a feature should make that choice visible rather than
  implicit.
- **Keep utility judgments out of the engine's effect-resolution layer** — `debris_risk` stays a
  declared tag in `engage.py` (R117 §2); a utility conversion belongs only in a UI/analysis layer
  consuming that tag, never folded back into the resolver's probability math.

## 5. Feature Mapping

A candidate future COA-comparison feature under FS-101 (Mission Planning) is the direct consumer.

## 6. Related Topics

R202 (Decision Theory, the expected-value framework this topic's value function plugs into), R212
(Multi-Criteria Decision Analysis, the direct applied consumer).
