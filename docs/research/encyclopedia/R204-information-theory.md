# R204 — Information Theory

> **Document ID:** R204
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R201](R201-probability-and-bayesian-reasoning.md)
> **Referenced By:** [R104](R104-collection-management.md), [R210](R210-decision-support-systems.md), [R212](R212-multi-criteria-decision-analysis.md)
> **Produces:** the vocabulary for "value of a collection request" underlying [R104](R104-collection-management.md)'s tasking-priority logic
> **Feature Mapping:** FS-104 (SDA Tasking)
> **Related Topics:** [R201](R201-probability-and-bayesian-reasoning.md) (Probability), [R104](R104-collection-management.md) (Collection Management — the tasking-priority system this
> topic's value-of-information concept justifies), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks)

> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 1

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`PRIORITY_COST` ([R118](R118-space-surveillance-networks.md) §2) forces an operator to treat collection requests as a scarce, valuable
resource rather than a free query — that scarcity is only a sound design if "some collection
requests are worth more than others" is a meaningful claim. This topic gives the implementer the
formal vocabulary (information content, value of information) for why that claim holds, distinct
from the probability formalism ([R201](R201-probability-and-bayesian-reasoning.md)) it's built on.

## 2. Scope

Covers Shannon information content and value-of-information (VoI) as the formal justification for
treating collection requests as a scarce resource, plus channel capacity as a throughput metaphor.
Does **not** cover the probability formalism VoI is built on ([R201](R201-probability-and-bayesian-reasoning.md)),
the concrete SSN/sensor contention implementation this topic justifies but does not restate
([R104](R104-collection-management.md)/[R118](R118-space-surveillance-networks.md)), or multi-criteria
scoring of collection value against other costs ([R212](R212-multi-criteria-decision-analysis.md)).

## 3. Concepts

**Information content is inversely related to prior probability.** An observation that confirms
something already near-certain (a high-confidence track with a fresh, expected pass) carries little
information; an observation that resolves a genuinely uncertain situation (an ambiguous RPO
approach, a low-confidence track near the weapons-quality threshold) carries much more. This is the
intuitive content behind Shannon's `-log P(outcome)` information measure, without requiring the
implementer to compute it explicitly — it is the *justification*, not necessarily a literal formula
the engine should implement
([Shannon, C. E., "A Mathematical Theory of Communication," *Bell System Technical Journal* 27, 1948](https://pure.mpg.de/pubman/item/item_2383164_3/component/file_2383163/Shannon_Weaver_1949_Mathematical.pdf)
([Wayback](https://web.archive.org/web/2026/https://pure.mpg.de/pubman/item/item_2383164_3/component/file_2383163/Shannon_Weaver_1949_Mathematical.pdf))).

**Value of information (VoI) is decision-relevant information, not all information.** Not every
bit of reduced uncertainty matters — VoI asks: would this observation change which action the
decision-maker would take? A confirmatory SSN request that wouldn't change Blue's plan either way
has low VoI even if it's "informative" in the raw Shannon sense; `_h_observe`'s auto-cue threshold
(confidence 0.3-0.85, [R104](R104-collection-management.md) §2) is implicitly a VoI heuristic: outside that band, more observation
either wouldn't change the custody classification (already too low or already weapons-quality) or
would change it only marginally.

**Channel capacity as a metaphor for sensor/SSN throughput limits.** The `_CONCURRENCY` cap per SSN
dispersion preset ([R118](R118-space-surveillance-networks.md) §2) and per-sensor contention (`_sensor_bookings`, [R104](R104-collection-management.md) §2) are real
operational throughput constraints — information-theoretically, a bounded "channel" through which
only so many observations can be collected per unit time, motivating *prioritization* ([R118](R118-space-surveillance-networks.md)'s
`PRIORITY_COST`) over an unconstrained request model.

### Sources

- *Shannon, C. E., "A Mathematical Theory of Communication," Bell System Technical Journal* 27 (1948) — [live](https://pure.mpg.de/pubman/item/item_2383164_3/component/file_2383163/Shannon_Weaver_1949_Mathematical.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://pure.mpg.de/pubman/item/item_2383164_3/component/file_2383163/Shannon_Weaver_1949_Mathematical.pdf)
  · accessed 2026-07-02.

## 4. Operational Context

Real collection management is fundamentally an information-economics problem: every tasking
decision trades a scarce sensor/SSN slot against the question "what will I actually learn, and does
it matter to a pending decision" — exactly the VoI framing, and the doctrinal reason real
intelligence collection plans explicitly rank requests by decision relevance, not raw novelty.

## 5. Implementation Guidance

- **A future collection-priority feature should frame request value in VoI terms (will this change
  a pending decision), not raw information-content terms** — a UI surfacing "request value" should
  ask the operator what decision the request supports, mirroring real collection-management
  practice, not present an abstract entropy number.
- **The auto-cue confidence band ([R104](R104-collection-management.md) §2) is a tuned VoI heuristic, not an arbitrary threshold** —
  if it is ever retuned, retune it against "does observation in this band change the
  weapons-quality determination," not against an unrelated criterion.
- **Don't conflate "more sensors/SSN dispersion" with "always better information"** — per channel-
  capacity reasoning, a busier network with more concurrent low-value requests can still leave a
  high-VoI request waiting; a future SSN/sensor scheduling improvement should optimize for VoI-
  weighted throughput, not raw request count.

## 6. Feature Mapping

FS-104 (SDA Tasking) is the direct consumer — any tasking-priority UI improvement should be framed
in this topic's VoI vocabulary.

## 7. Related Topics

[R201](R201-probability-and-bayesian-reasoning.md) (Probability, the formalism VoI is built on), [R104](R104-collection-management.md) (Collection Management, the concrete
tasking-contention system this topic justifies), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks, the throughput-
constrained "channel").
