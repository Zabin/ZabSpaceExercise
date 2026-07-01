# Tier R300 — Military Analysis

[↑ Encyclopedia index](INDEX.md)

Justifies White Cell and scenario design (DOM-003, DOM-009). 20 topics.

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| [R301](R301-campaign-design.md) | Campaign Design | Structuring a sequence of operations toward a strategic end. | — | ✅ |
| [R302](R302-operational-art.md) | Operational Art | The connective layer between tactics and strategy. | [R301](R301-campaign-design.md) | ✅ |
| [R303](R303-deterrence-theory.md) | Deterrence Theory | Discouraging action via credible cost threat; vs. compellence. | — | ✅ |
| [R304](R304-escalation-dynamics.md) | Escalation Dynamics | How conflict severity shifts; the basis for the kinetic-confirm gate. | [R303](R303-deterrence-theory.md) | ✅ |
| [R305](R305-mission-analysis.md) | Mission Analysis | Translating a higher commander's intent into executable tasks. | [R301](R301-campaign-design.md) | ✅ |
| [R306](R306-operational-assessment.md) | Operational Assessment | Judging whether an operation is achieving its intended effect. | [R310](R310-effects-based-operations.md) | ✅ |
| [R307](R307-wargaming-theory.md) | Wargaming Theory | What a wargame can validly demonstrate; design for sound conclusions. | — | ✅ |
| [R308](R308-red-teaming-methodology.md) | Red Teaming Methodology | Structured adversarial role-play to surface blind spots. | [R307](R307-wargaming-theory.md) | ✅ |
| [R309](R309-center-of-gravity-analysis.md) | Center of Gravity Analysis | Identifying the source of an actor's power/freedom of action. | [R302](R302-operational-art.md) | ✅ |
| [R310](R310-effects-based-operations.md) | Effects-Based Operations | Planning oriented around cascading effects, not direct output alone. | [R309](R309-center-of-gravity-analysis.md) | ✅ |
| [R311](R311-course-of-action-analysis.md) | Course of Action Analysis | Comparing distinct options against criteria before commitment. | [R305](R305-mission-analysis.md) | ✅ |
| [R312](R312-space-strategy.md) | Space Strategy | Strategic-level theory specific to the space domain. | [R301](R301-campaign-design.md), [R303](R303-deterrence-theory.md) | ✅ |
| [R313](R313-maritime-operator-perspective.md) | Maritime Operator Perspective | Naval sea control/denial, C2, sustainment, and escalation doctrine as analogical grounding for orbital ops and space force employment. | [R301](R301-campaign-design.md), [R303](R303-deterrence-theory.md), [R304](R304-escalation-dynamics.md) | ✅ |
| [R314](R314-land-operator-perspective.md) | Land Operator Perspective | Land-component command/staff mindset (mission command, IPB, targeting cycle, sustainment) as an analogy source for orbital ops. | [R301](R301-campaign-design.md), [R302](R302-operational-art.md), [R305](R305-mission-analysis.md) | 🟡 |
| [R315](R315-air-operator-perspective.md) | Air Operator Perspective | How air forces think operationally (not aircraft tech); twenty air-ops concepts mapped to orbital-ops lessons. | [R301](R301-campaign-design.md), [R302](R302-operational-art.md), [R305](R305-mission-analysis.md), [R312](R312-space-strategy.md) | ✅ |
| [R316](R316-joint-and-combined-operations.md) | Joint and Combined Operations Perspective | Joint command relationships, JPP, coalition/combined ops, MDO/JADC2, joint fires/targeting, and each domain's space dependencies. | [R301](R301-campaign-design.md), [R302](R302-operational-art.md), [R305](R305-mission-analysis.md) | ✅ |
| [R317](R317-space-operator-perspective.md) | Space Operator Perspective (Historical Evolution) | How the space operator's own mindset evolved — support era → warfighting domain → SDA → orbital-ops tradecraft → C2/autonomy → joint integration → decision-making → future trends. | [R301](R301-campaign-design.md), [R302](R302-operational-art.md), [R305](R305-mission-analysis.md), [R312](R312-space-strategy.md) | ✅ |
| [R318](R318-attribution-confidence-and-public-messaging.md) | Attribution Confidence and Public Messaging in Space Incidents | The operational craft between detecting an ambiguous incident and choosing a response tier (silence/protest/public statement); grounds the already-computed-but-unconsumed `attribution_signal` side effect. | [R213](R213-signaling-theory.md), [R303](R303-deterrence-theory.md) | ✅ |
| [R319](R319-red-behavior-validation-methodology.md) | Red Behavior Validation Methodology | A concrete fidelity-checking method for `redai.py`/AI-Red doctrine presets, extending R308's qualitative principle; grounds the future DOM-005 validation framework. | [R308](R308-red-teaming-methodology.md) | ✅ |
| R320 | Commercial Space Actors and Strategic Ambiguity | Third-party/commercial-actor targeting ambiguity as a strategic-frame extension of R312 — closes GAP-03. | [R312](R312-space-strategy.md) | ⛔ Planned |

**Strategic-review gap-closure pass (2026-07-01).** The Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3)
identified 13 research gaps against the full corpus; 4 fell within this tier's scope. Two — **GAP-06**
(attribution confidence and public-messaging craft, no prior topic covered the operational decision
between R303/R304's theory and a real incident response) and **GAP-08** (Red-behavior validation
methodology, R308 covered the qualitative principle but not a checkable fidelity method) — are
closed by newly authored **[R318](R318-attribution-confidence-and-public-messaging.md)** and
**[R319](R319-red-behavior-validation-methodology.md)** above. The remaining two in-tier gaps
(commercial space actors/strategic ambiguity, an extension of R312; and distributed-simulation/
exercise-interoperability standards, judged to sit at the boundary of this tier and systems
architecture rather than cleanly in it) are recorded as `⛔ Planned` (`R320`) or flagged for
architecture-tier follow-up rather than bulk-authored in the same pass — full resolution status for
every gap (including the nine outside this tier's scope) is tracked in
[`docs/reviews/research-gap-resolution.md`](../../reviews/research-gap-resolution.md).

**Status: 18 of 20 topics complete; R314 is a 🟡 draft pending citation verification and R320 is
⛔ Planned** (R314's issue: that
session's WebFetch had no network access — every test URL, including non-doctrine controls,
returned HTTP 403 — so R314's doctrine citations are unverified placeholders; see its own Sources
section). All other 18 topics carry the mandatory §2 Scope section (MSTR-007 §4.2) and are cited
per `docs/research/10-sources-and-methodology.md`'s convention — each topic has at least
one `### Sources` subsection (live URL + Wayback snapshot + accessed date) and inline citations at
the doctrinal/legal/historical claim site, with [R303](R303-deterrence-theory.md)'s single
secondary-sourced claim and [R316](R316-joint-and-combined-operations.md) §3.12's single-source
government-report claim flagged inline per the methodology's §3 single-source rule rather than
mis-cited as primary. Grounded in DOM-003 (White Cell Framework — §7/§10's red-teaming and
wargaming citations, plus [R316](R316-joint-and-combined-operations.md)'s command-relationship and
JPP vocabulary for any future multi-cell/coalition session design), DOM-009 (Doctrine Development
Framework — the translation pipeline these topics' real-world doctrine ultimately feeds), and
DOM-008 §3 (Red AI design principles, the direct consumer of
[R303](R303-deterrence-theory.md)/[R308](R308-red-teaming-methodology.md)/[R312](R312-space-strategy.md)'s strategic-posture
and red-teaming concepts).

[R313](R313-maritime-operator-perspective.md) (Maritime Operator Perspective),
[R314](R314-land-operator-perspective.md) (Land Operator Perspective), and
[R315](R315-air-operator-perspective.md) (Air Operator Perspective) were all added 2026-06-28 as
the tier's deliberate broad-survey-by-domain exceptions — each maps a mature, doctrinally
documented second domain's operational concepts onto orbital-operations lessons, closing the gap
MSTR-007 §7's coverage test flags: no prior R300 topic gave an implementer a second-domain analogy
for sea/land/air-style command tempo, custody-under-ambiguity, or tasking-cycle dynamics.
[R316](R316-joint-and-combined-operations.md) (Joint and Combined Operations Perspective) is the
tier's broadest-scope topic, added the same day to ground multi-domain/coalition vignette design
and any future joint-force-structure feature without duplicating the operational-art/campaign-
design/COG/EBO/assessment content the other 12 single-domain topics already own. See each topic's
own §2 Scope for why it departs from the tier's usual single-concept shape.
[R317](R317-space-operator-perspective.md) (Space Operator Perspective, Historical Evolution) was
added the same day as the domain's own counterpart to R313-R316 — where those four import another
domain's mindset into orbital ops, R317 traces how the space operator's own mindset evolved across
eight historical stages (support era → warfighting domain → SDA → orbital-ops tradecraft → C2/
autonomy → joint integration → decision-making → future trends), closing the remaining gap: no
prior R300 topic gave an implementer the space domain's own historical operator-mindset arc rather
than a cross-domain analogy. Last reviewed across the tier: 2026-06-28.

**ID-collision note (2026-06-28):** two independently authored topics were both committed as
`R313` (Maritime Operator Perspective and Joint and Combined Operations Perspective) by separate
concurrent branches, each unaware of the other's choice of next-available ID. Resolved by
renumbering Joint and Combined Operations Perspective to R316 (the next free ID after Air
Operator Perspective's R315) and updating every cross-reference (`R301`, `R302`, `R305`, `R102`,
`R108`, `R119`, `R208`) that pointed at the old `R313-joint-and-combined-operations.md` path.
