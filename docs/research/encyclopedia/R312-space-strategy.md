# R312 — Space Strategy

> **Document ID:** R312
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R301](R301-campaign-design.md), [R303](R303-deterrence-theory.md)
> **Referenced By:** [R317](R317-space-operator-perspective.md)
> **Produces:** the strategic-level vocabulary that [R301](R301-campaign-design.md)-[R311](R311-course-of-action-analysis.md)'s operational/tactical concepts ultimately serve
> **Feature Mapping:** vignette authoring (`docs/scenarios/`), capstone Vignette 8 design
> **Related Topics:** [R301](R301-campaign-design.md) (Campaign Design), [R303](R303-deterrence-theory.md) (Deterrence Theory), [R302](R302-operational-art.md) (Operational Art),
> [`research/01-doctrine-western.md`](../01-doctrine-western.md), [`research/02-doctrine-non-western.md`](../02-doctrine-non-western.md)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 2

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

This is the tier's capstone topic: every other [R300](R300-index.md) concept (campaign design, operational art,
deterrence, COG, EBO, COA analysis) ultimately serves a strategic-level question this topic names
directly — what is space control actually *for*, strategically, and how do real strategic schools of
thought frame that question differently. Closes the [R300](R300-index.md) tier by giving the implementer the top-level
frame the rest of the tier's vocabulary sits inside.

## 2. Scope

Covers: the strategic (vs. operational/tactical) framing of space control, the competing real-world
schools of thought on what space strategy is for, and the debris/shared-commons externality unique to
the domain. Does **not** cover: how a strategic objective is operationalized into a campaign (that is
[R301](R301-campaign-design.md), Campaign Design) or the deterrence-specific sub-question of how a
strategic posture shapes adversary behavior short of conflict (that is
[R303](R303-deterrence-theory.md), Deterrence Theory) — this topic is the frame those two sit inside,
not a restatement of either.

## 3. Concepts

**Space control as the strategic objective, not destruction of adversary assets as an end in
itself.** US Space Force [*Space Force Doctrine Document 1, "Spacepower"*](https://starcom.spaceforce.mil/Portals/2/Space%20Force%20Doctrine%20Document%201%20FINAL_4Apr25.pdf)
(United States Space Force, signed 2025-04-03; the doctrine's content was originally established
2020-08-10 per public reporting at the time of first publication) frames *space superiority* — freedom
of action in, from, and to space for friendly forces while denying the same to an adversary when
necessary — as the Service's core strategic concern, with specific engagement/denial effects (this
simulator's five D's) cast as the *means* by which that superiority is contested, not the strategic end
itself. A vignette's capstone-level design (Vignette 8) should be checkable against whether its
objectives actually serve assured-access/denial framing, not merely "did Blue destroy Red's
satellite."

**Competing strategic schools: warfighting domain vs. contested-but-managed commons.** Different
real strategic traditions frame space differently — some emphasize space as a warfighting domain
requiring offensive/defensive parity (closer to traditional military-domain strategy, the framing
SFDD-1 itself adopts for the US Space Force), others emphasize space as a fragile shared commons where
escalation/debris risk ([R117](R117-directed-energy-and-kinetic-effects.md), [R304](R304-escalation-dynamics.md)) makes restraint
itself strategically rational even at a tactical cost. `research/01-02`'s Western/non-Western
doctrine primers already document real-world variation along this axis; this topic names the
strategic-theory frame that variation sits inside.

**Strategic culture shapes what "rational" Red behavior looks like.** A Red doctrine preset
(`redai.py`) implicitly encodes assumptions about which strategic school Red's modeled behavior
follows — DOM-008 §3's legibility requirement extends to this: White Cell should be able to state not
just "which preset" but "which strategic posture this preset is meant to represent," since that
framing is what makes Red's in-exercise behavior doctrinally interpretable rather than just a
parameter set.

**The debris/Kessler-syndrome strategic externality.** Unlike most domains, action in space has a
strategic cost not borne only by the immediate adversary — debris from a kinetic engagement ([R117](R117-directed-energy-and-kinetic-effects.md) §2)
degrades the shared orbital environment for all actors, including the side that "won" the
engagement. This is a strategically unique feature of the domain (no close terrestrial analog at the
same scale), and it is the explicit, dated reasoning behind the 2022 US destructive direct-ascent
ASAT (DA-ASAT) test moratorium — announced by US Vice President Kamala Harris on 2022-04-18 and
affirmed by UN General Assembly Resolution 77/41 (adopted 2022-12-07), per the existing primer
[`research/07-legal-norms-and-roe.md`](../07-legal-norms-and-roe.md) — a concrete, real-world instance
of strategic-level reasoning (the shared-commons/debris externality) producing policy restraint
independent of any single actor's tactical interest. This is the doctrinal reason real space strategy
treats kinetic restraint as having strategic value independent of any single engagement's tactical
outcome — directly reflected in this simulator's kinetic-as-rare/consequence-confirmed design choice
(MSTR-003 §5).

### Sources

- *United States Space Force, Space Force Doctrine Document 1, "Spacepower"* (signed 2025-04-03;
  content first published 2020-08-10) — [live](https://starcom.spaceforce.mil/Portals/2/Space%20Force%20Doctrine%20Document%201%20FINAL_4Apr25.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://starcom.spaceforce.mil/Portals/2/Space%20Force%20Doctrine%20Document%201%20FINAL_4Apr25.pdf)
  · accessed 2026-06-27.
- *UN General Assembly Resolution 77/41, "Destructive direct-ascent anti-satellite missile testing"*
  (adopted 2022-12-07) — [live](https://digitallibrary.un.org/record/3996470)
  · [snapshot](https://web.archive.org/web/2026/https://digitallibrary.un.org/record/3996470)
  · accessed 2026-06-27.

## 4. Operational Context

Real space-strategy discourse (across both Western and non-Western traditions per the existing
research primers) explicitly debates exactly these framings — assured-access vs. domain-control vs.
commons-management — and the 2022 DA-ASAT moratorium is a concrete recent instance of strategic-level
reasoning (the shared-commons/debris externality) producing real policy restraint independent of any
single actor's tactical interest.

## 5. Implementation Guidance

- **The capstone vignette (Vignette 8) and any future high-tier vignette should be designed against
  an explicitly stated strategic frame** (assured-access, domain-control, or commons-management), not
  left implicit — this gives a White Cell facilitator language for the highest-level debrief
  question ("what was actually being contested here, strategically") beyond the tactical-level AAR.
- **A new Red doctrine preset's strategic framing should be documented alongside its tactical
  parameters** — per DOM-008 §3's legibility principle extended to the strategic level, a preset
  named only by aggressiveness level (e.g. "aggressive") without a stated strategic posture is less
  useful to a facilitator than one that also states what strategic assumption the aggressiveness
  reflects.
- **Any new kinetic-adjacent capability or vignette design should explicitly account for the debris/
  shared-commons externality in its framing** — per [R117](R117-directed-energy-and-kinetic-effects.md)'s `debris_risk` declaration and MSTR-003
  §5's reversibility gradient, a vignette that rewards kinetic action without surfacing this
  strategic cost is doctrinally incomplete by this topic's standard.

## 6. Feature Mapping

Vignette authoring, especially capstone-tier vignette design (Vignette 8 and successors), is the
direct consumer.

## 7. Related Topics

[R301](R301-campaign-design.md) (Campaign Design, the operational-level implementation of strategy), [R303](R303-deterrence-theory.md) (Deterrence Theory),
[R302](R302-operational-art.md) (Operational Art), [`research/01-doctrine-western.md`](../01-doctrine-western.md), [`research/02-doctrine-non-western.md`](../02-doctrine-non-western.md) (the
existing doctrine primers this topic's strategic frame organizes).
