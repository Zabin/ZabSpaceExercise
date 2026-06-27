# R201 — Probability and Bayesian Reasoning

> **Document ID:** R201
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R202](R202-decision-theory.md), [R204](R204-information-theory.md), [R207](R207-cognitive-biases.md), DOM-002, MSTR-003
> **Produces:** the formal vocabulary underlying [`engine/custody.py`](../../../spacesim/engine/custody.py) confidence and [`engine/cyber.py`](../../../spacesim/engine/cyber.py) attribution scoring
> **Feature Mapping:** FS-103 (Custody Management), FS-104 (SDA Tasking)
> **Related Topics:** [R105](R105-custody-theory.md) (Custody Theory — the implementation this topic's formalism justifies), [R116](R116-cyber-operations-against-space-systems.md) §2 (attribution
> scoring), [R204](R204-information-theory.md) (Information Theory), [R207](R207-cognitive-biases.md) (Cognitive Biases)

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The simulator never shows an operator ground truth directly — every belief surface (`Track`
confidence, cyber attribution, SSN product quality) is a number standing in for "how sure should
you be." This topic gives the implementer the formal vocabulary (probability as degree of belief,
Bayesian updating) that those numbers are informal stand-ins for, so a new belief-bearing feature
is designed consistently with the existing ones rather than inventing a new, incompatible notion of
"confidence."

## 2. Concepts

**Probability as degree of belief, not just frequency.** The Bayesian interpretation treats a
probability as a *quantified belief state* of an observer with particular evidence, distinct from
the frequentist notion of a long-run frequency over repeated trials. `Track.confidence` is squarely
Bayesian in this sense: it represents one cell's belief about one object's identity/state given
*that cell's* observation history, not a frequency over many objects.

**Bayes' theorem: posterior ∝ likelihood × prior.** `P(hypothesis | evidence) = P(evidence |
hypothesis) × P(hypothesis) / P(evidence)`. A new observation should *update* an existing belief
multiplicatively (weighted by how diagnostic the evidence is), not simply replace it — this is the
formal ideal that [R119](R119-space-situational-data-fusion.md) (Data Fusion) explicitly notes the engine does *not* yet implement
(`observe()` is last-observation-wins, not Bayesian combination).

**Confidence decay is a temporal prior, not a likelihood update.** `Track.current_confidence()`'s
half-life decay ([R105](R105-custody-theory.md) §2) models the Bayesian principle that a belief without fresh supporting
evidence should regress toward an uninformative prior over time — formally, this is closer to a
prior-decay term than a Bayesian update from new evidence, and the two should not be conflated when
extending custody.

**Independence vs. correlation matters for combining sources.** Two observations of the same
object from the same sensor close in time are not independent evidence — combining them as if they
were would overstate confidence. A future genuine multi-source fusion feature ([R119](R119-space-situational-data-fusion.md) §4) must treat
this explicitly: don't naively multiply or average two correlated reports as if they were
independent Bayesian updates.

## 3. Operational Context

Real intelligence and SDA tradecraft is explicitly Bayesian: an analyst's stated confidence in a
custody track or an attribution judgment is a degree-of-belief claim, revised as new sensor passes
or SIGINT arrive, and explicitly distinguished from a frequency claim ("90% of objects like this are
X") which is a different, often-confused statistical object. Intelligence Community tradecraft
standards (e.g. analytic confidence levels) are a real-world instance of exactly this formalism
applied to custody-like judgments.

## 4. Implementation Guidance

- **A new confidence-bearing field must say explicitly whether it represents a Bayesian belief
  state or a frequency/rate** — conflating the two (e.g., treating `detect_rate` in
  `cyber.py`'s `VECTORS` table, which is a frequency, as if it were a belief like `Track.confidence`)
  produces formulas that are dimensionally wrong even if they happen to compile.
- **If implementing genuine multi-source fusion ([R119](R119-space-situational-data-fusion.md)), use a real Bayesian update rule** (e.g.
  log-odds summation for conditionally independent sources) rather than an ad hoc weighted average —
  an ad hoc average can't be justified or audited the way a stated Bayesian model can.
- **Never let a derived probability (Pₖ, jam success, cyber success) feed back into a `Track`'s
  Bayesian confidence** — [R117](R117-directed-energy-and-kinetic-effects.md)/[R115](R115-electronic-warfare-in-space-operations.md)/[R116](R116-cyber-operations-against-space-systems.md) each derive an *effect* probability from a different
  process (declared interceptor tables, modulation database, vector×payload database); mixing that
  with the *custody* belief layer blurs two distinct probabilistic objects that [R102](R102-space-domain-awareness.md) §5 deliberately
  keeps separate.

## 5. Feature Mapping

FS-103 (Custody Management) and FS-104 (SDA Tasking) both depend on this topic for the formal
meaning of the confidence numbers they display and task against.

## 6. Related Topics

[R105](R105-custody-theory.md) (Custody Theory, the concrete implementation this topic formalizes), [R116](R116-cyber-operations-against-space-systems.md) §2 (attribution
scoring, a sibling belief quantity), [R204](R204-information-theory.md) (Information Theory, the value of evidence that drives a
Bayesian update), [R207](R207-cognitive-biases.md) (Cognitive Biases, the systematic ways humans depart from this formalism).
