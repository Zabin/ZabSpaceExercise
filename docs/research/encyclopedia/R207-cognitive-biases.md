# R207 — Cognitive Biases

> **Document ID:** R207
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R205](R205-cognitive-psychology-foundations.md)
> **Referenced By:** DOM-002, [R301](R301-campaign-design.md)
> **Produces:** the bias vocabulary DOM-002 §9 uses to keep rubric design from mistaking expected bias for incompetence
> **Feature Mapping:** FS-201 (Competency Assessment)
> **Related Topics:** [R205](R205-cognitive-psychology-foundations.md) (Cognitive Psychology Foundations), [R201](R201-probability-and-bayesian-reasoning.md) (Probability — the normative
> baseline biases depart from), [R105](R105-custody-theory.md) (Custody Theory — where misjudgment of confidence is most
> consequential), DOM-002 §9

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Custody misjudgment in this simulator is not always a tradecraft failure — sometimes it is a
predictable, well-documented cognitive bias acting on an otherwise competent operator. This topic
catalogs the biases most relevant to SDA/custody/engagement decisions so a future assessment rubric
(DOM-002) does not mistake an expected, human-universal bias for a unique personal failing, per
DOM-002 §9's explicit caution.

## 2. Concepts

**Confirmation bias.** The tendency to weight new evidence as confirming a prior belief and
discount disconfirming evidence — directly relevant to custody: an operator who has decided a track
is hostile may interpret an ambiguous subsequent observation as confirming that belief rather than
updating toward uncertainty, the opposite of the Bayesian ideal ([R201](R201-probability-and-bayesian-reasoning.md)).

**Anchoring.** Over-reliance on the first piece of information encountered, with insufficient
adjustment afterward — an operator's first SSN product or first custody read can anchor their
assessment even as fresher, more diagnostic organic observations arrive (relevant to [R119](R119-space-situational-data-fusion.md)'s
last-observation-wins fusion model: the *engine* doesn't anchor, but the *operator reading the
display* might, independent of the underlying data).

**Overconfidence / miscalibration.** Stated confidence systematically exceeding actual accuracy —
relevant directly to the weapons-quality threshold ([R105](R105-custody-theory.md) §3): an operator who treats a borderline
track as "basically weapons-quality" before the engine's threshold says so is exhibiting exactly this
bias, and the engine's hard gate (`is_weapons_quality()`) exists partly to prevent this bias from
having lethal consequences.

**Recency and availability bias.** Overweighting the most recent or most vivid information relative
to its actual diagnostic value — an operator who over-reacts to the latest alarm badge while
discounting a slower-building pattern (e.g. gradual SoC decline) across the fleet rail is exhibiting
this bias; [R205](R205-cognitive-psychology-foundations.md)'s discussion of change blindness is the flip side of the same attentional economy.

**Escalation bias / sunk cost.** A tendency to continue or intensify a committed course of action
because of prior investment, independent of new evidence that it's no longer the best option —
relevant to kinetic engagement decisions ([R117](R117-directed-energy-and-kinetic-effects.md)) where an operator who has already expended ammo or
custody-building effort against a target may be biased toward following through even if circumstances
have changed.

## 3. Operational Context

Intelligence and operations literature treats these biases as well-documented, recurring failure
modes in real SDA/targeting decision chains (the same biases drive real-world misidentification and
escalation incidents), which is exactly why structured analytic techniques (devil's advocacy,
red-teaming per [R308](R308-red-teaming-methodology.md), explicit confidence-interval reporting per [R201](R201-probability-and-bayesian-reasoning.md)) exist as institutional
counter-measures rather than relying on individual analyst discipline alone.

## 4. Implementation Guidance

- **A DOM-002 rubric dimension must distinguish a biased-but-common error pattern from a
  competence gap** — e.g., scoring "engaged a track at exactly the confidence threshold under time
  pressure" differently from "engaged a track well below the threshold with no apparent custody
  basis"; the former is consistent with known overconfidence effects under time pressure (a
  pedagogically interesting AAR topic), the latter is a tradecraft gap.
- **A future AI advisor or coaching-note feature may name a likely bias in a debrief context** (e.g.
  "this read may reflect anchoring on the first SSN product") as a *diagnostic AAR aid*, but per
  DOM-008 §4 must not pre-empt the decision in real time by correcting for the bias automatically.
- **Don't design UI in a way that amplifies a known bias** — e.g., a persistent "first guess" field
  that stays visible and anchors later judgment, or an alarm system so noisy it induces availability-
  bias over-reaction; [R205](R205-cognitive-psychology-foundations.md)'s salience guidance and this topic's bias catalog should be checked
  together for any new alerting feature.

## 5. Feature Mapping

FS-201 (Competency Assessment) is the direct consumer — DOM-002's rubric design must consult this
catalog before scoring any judgment-quality dimension.

## 6. Related Topics

[R205](R205-cognitive-psychology-foundations.md) (the perceptual substrate biases act on), [R201](R201-probability-and-bayesian-reasoning.md) (the normative Bayesian baseline biases depart
from), [R105](R105-custody-theory.md) (Custody Theory, the highest-stakes application), DOM-002 §9.
