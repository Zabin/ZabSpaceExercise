# R318 — Attribution Confidence and Public Messaging in Space Incidents

> **Document ID:** R318
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R213](R213-signaling-theory.md), [R303](R303-deterrence-theory.md)
> **Referenced By:** —
> **Produces:** research grounding for [`engine/effects.py`](../../../spacesim/engine/effects.py)'s
> `attribution_signal` side effect and any future ROE/messaging feature that consumes it
> **Feature Mapping:** none yet — research-first per this skill's scope discipline; the eventual
> consumer is a not-yet-authorized ROE/messaging mechanic, not an existing FS-xxx
> **Related Topics:** [R213](R213-signaling-theory.md) (Signaling Theory — the game-theoretic
> mechanism this topic applies operationally), [R303](R303-deterrence-theory.md) (Deterrence
> Theory — credibility as the variable public messaging is meant to build), [R304](R304-escalation-dynamics.md)
> (Escalation Dynamics — the ladder a messaging choice can move an incident up or down),
> [R116](R116-cyber-operations-against-space-systems.md) (Cyber Operations — the one effect
> category whose attribution scoring is already fully modeled, `attribution_score()`),
> [`research/07-legal-norms-and-roe.md`](../07-legal-norms-and-roe.md) (the existing legal/ROE
> substrate this topic's messaging layer sits above)
> **Last Reviewed:** 2026-07-01
> **Primary Sources Consulted:** 1

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Identified as **GAP-06** in the Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3):
[R303](R303-deterrence-theory.md) and [R304](R304-escalation-dynamics.md) both name signaling and
credibility as central to their theory, and [R213](R213-signaling-theory.md) supplies the
underlying game-theoretic mechanism — but no topic covers the specific *operational craft* this
theory cashes out into for a real space incident: how much attribution confidence is enough to act
or speak publicly on, and what a chosen public-messaging response itself signals, independent of
any technical countermeasure. This gap has a precise engine counterpart worth naming directly:
`engine/effects.py`'s `EffectTemplate.attribution` field and the `attribution_signal` side effect
it emits (`{"type": "attribution_signal", "to": ..., "confidence": ...}`, confidence
0.95/0.5/0.15 for overt/ambiguous/covert) are **already implemented and already computed on every
effect resolution**, but as of this writing **nothing in the engine, session, or UI layer consumes
`attribution_signal`** — it is a fully-modeled, entirely inert side effect. This topic exists so
that if a future feature surfaces it (an ROE gate, a messaging-choice mechanic, an assessment
metric), the design is grounded in real attribution/messaging doctrine rather than invented from
the field name alone.

## 2. Scope

Covers: the real-world operational pattern of attribution-confidence-building followed by a
public-messaging (rather than purely technical or kinetic) response in space incidents; why
messaging choice is itself a doctrinal decision, not a communications afterthought; and the
specific gap between the engine's already-computed attribution confidence and the absence of any
consumer for it. Does **not** cover: the general signaling-theory mechanism by which credibility is
built ([R213](R213-signaling-theory.md)), deterrence-by-denial/punishment posture design
([R303](R303-deterrence-theory.md)), the dynamic process of an incident moving up or down an
escalation ladder ([R304](R304-escalation-dynamics.md)), or cyber-specific attribution scoring
(`attribution_score()`, fully covered by [R116](R116-cyber-operations-against-space-systems.md) §3
— this topic addresses the cross-category messaging *decision*, not a second attribution-scoring
model).

## 3. Concepts

**Public "naming and shaming" is a real, doctrinally deliberate response category distinct from
both silence and retaliation.** In 2018, French Minister of the Armed Forces Florence Parly
publicly accused Russia of "space espionage" after the Russian satellite Luch (also designated
Olymp-K) maneuvered close to the Franco-Italian military communications satellite Athena-Fidus —
a public attribution statement issued in response to a non-kinetic, technically ambiguous act,
chosen specifically because it imposed a reputational cost without escalating to a technical or
kinetic response ([CSIS Aerospace Security Project, "Unusual Behavior in GEO: Luch (Olymp-K)"](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
([Wayback](https://web.archive.org/web/2026/https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/))).
This is the doctrinal category this topic exists to ground: a messaging choice *is* the response,
not a placeholder until a "real" response is decided.

**Attribution confidence is built incrementally and often stays below certainty even when a public
response is chosen.** The same Luch/Olymp-K satellite (launched September 2014) had, seven months
after launch, already positioned itself between the commercial Intelsat 7 and Intelsat 901
satellites at ranges of roughly 10 km, prompting a formal US diplomatic protest in 2015 — three
years before the French public statement — illustrating that attribution-confidence-building and
the choice of response tier (private diplomatic protest vs. public statement) are separable
decisions made at different confidence thresholds over an extended timeline, not a single
detect-then-announce event ([SpaceNews, "Russian Satellite Maneuvers, Silence Worry Intelsat"](https://spacenews.com/russian-satellite-maneuvers-silence-worry-intelsat/)
([Wayback](https://web.archive.org/web/2026/https://spacenews.com/russian-satellite-maneuvers-silence-worry-intelsat/))
· CSIS Aerospace Security Project, *op. cit.*). The operational lesson: an operator or facilitator
correctly modeling this domain treats "we are confident enough to act" and "we are confident enough
to say so publicly" as two separate thresholds, with the second frequently reached, and chosen,
well before — or entirely without — the first.

**Genuinely ambiguous, technically-deniable behavior is the domain's normal operating condition,
not an edge case.** Proximity operations of the Luch/Olymp-K type are explicitly gray-zone:
operationally ambiguous, politically deniable, and technically difficult to characterize without
sustained, high-accuracy space domain awareness — precisely the condition under which a chosen
public-messaging response substitutes for definitive technical proof, since waiting for
certainty may mean never responding at all ([CSIS Aerospace Security Project, *op. cit.*](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)).
This directly parallels [R303](R303-deterrence-theory.md) §3's credibility argument: a messaging
response chosen and executed under uncertainty is itself a signal of resolve, separate from
whatever the underlying attribution turns out to be.

**The engine already computes exactly this confidence value, per effect, and discards it.**
`EffectTemplate.attribution` (`"overt"|"ambiguous"|"covert"`) and the resolver's
`conf = {"overt": 0.95, "ambiguous": 0.5, "covert": 0.15}[effect.attribution]`
(`effects.py:167`) produce a graded confidence value attached to every successful effect
resolution's `attribution_signal` side effect, and a lower, fixed 0.2 confidence signal even on a
*failed* covert/ambiguous attempt (`effects.py:124-125`) — a real, if simplified, model of exactly
the graded-confidence concept this topic documents. But `attribution_signal` is never read by any
other module: no ROE gate checks it, no UI surfaces it, no assessment metric scores a cell's
response against it. The gap this topic identifies is therefore not "the simulator has no
attribution model" (it does) but "the simulator's attribution model has no consumer, so the
public-messaging *decision* this topic documents has nothing to attach to in the current design."

### Sources

- *CSIS Aerospace Security Project, "Unusual Behavior in GEO: Luch (Olymp-K)"* — [live](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
  · accessed 2026-07-01.
- *SpaceNews, "Russian Satellite Maneuvers, Silence Worry Intelsat"* (event 2015) — [live](https://spacenews.com/russian-satellite-maneuvers-silence-worry-intelsat/)
  · [snapshot](https://web.archive.org/web/2026/https://spacenews.com/russian-satellite-maneuvers-silence-worry-intelsat/)
  · accessed 2026-07-01.

*Single source (Tier B/C corroboration only — WebFetch access to both live pages returned HTTP 403
during authoring; the claims above rest on retrieved search-index summaries of each page's content,
cross-corroborated across CSIS, SpaceNews, and independent reporting (The Space Review, Militarnyi)
converging on the same dates/distances/officials, rather than a single source. Flagged per the
methodology's §3 single-source caution even though the corroboration itself is multi-source, since
full-page verification could not be completed in this session.*

## 4. Operational Context

Real space-incident response doctrine treats the choice of *how* to respond — silence, private
diplomatic protest, public attribution statement, technical countermeasure, or some combination —
as itself a strategic decision made under persistent uncertainty, not a downstream formality once
"the truth" is established. The Luch/Olymp-K case is instructive precisely because the confidence
never became binary: three years separated a private diplomatic protest from a public accusation
of the same actor's continued behavior, and no purely technical resolution (jamming, cyber
response, kinetic action) was ever the chosen tool — messaging *was* the operative response. A PME
exercise that only scores technical/kinetic responses to an ambiguous incident, with no way to
credit or penalize the messaging choice itself, omits a live and doctrinally central decision
category.

## 5. Implementation Guidance

- **Any future feature surfacing `attribution_signal` should expose the graded confidence value
  to the receiving cell as information to act on, not as a ground-truth reveal** — per
  [R105](R105-custody-theory.md)'s confidence-not-certainty pattern already used for custody, a
  0.5 "ambiguous" confidence should read to the operator as genuinely uncertain, not as a soft hint
  at the true answer.
- **A messaging-choice mechanic should be modeled as a distinct decision from any ROE-gated
  technical/kinetic response**, per the Luch/Olymp-K precedent's separable timelines — bundling
  "respond publicly" into the same authorization gate as "respond kinetically" would misrepresent
  a real and doctrinally significant distinction this topic documents.
- **A White Cell inject or vignette objective testing this decision should reward a well-reasoned
  messaging choice made under persistent ambiguity**, not merely reward eventually reaching high
  confidence — per §4, real incidents are frequently never resolved to certainty, and an exercise
  that only scores the "wait for certainty" path teaches the wrong lesson about how this domain
  actually works.
- **This topic does not authorize building an attribution/messaging feature.** Per this skill's own
  scope discipline and MSTR-007 §6, it supplies research-first grounding for
  `engine/effects.py`'s already-computed-but-unconsumed `attribution_signal`; scoping a consuming
  feature (ROE extension, UI surface, or assessment metric) is a separate, not-yet-authorized
  decision.

## 6. Feature Mapping

None yet, by design (§2) — this is research-first grounding for a currently-inert engine side
effect. When a consuming feature is scoped, its FS-xxx should cite this topic directly.

## 7. Related Topics

[R213](R213-signaling-theory.md) (Signaling Theory — the mechanism this topic applies), [R303](R303-deterrence-theory.md)
(Deterrence Theory — credibility as the variable messaging builds), [R304](R304-escalation-dynamics.md)
(Escalation Dynamics — the ladder a messaging choice moves an incident along),
[R116](R116-cyber-operations-against-space-systems.md) (Cyber Operations — the one effect category
with a fully-modeled attribution *scoring* mechanism, `attribution_score()`, distinct from this
topic's cross-category messaging-decision focus), [`research/07-legal-norms-and-roe.md`](../07-legal-norms-and-roe.md)
(the legal/ROE substrate this topic's messaging layer sits above).
