# R312 — Space Strategy

> **Document ID:** R312
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R301, R303
> **Referenced By:** —
> **Produces:** the strategic-level vocabulary that R301-R311's operational/tactical concepts ultimately serve
> **Feature Mapping:** vignette authoring (`docs/scenarios/`), capstone Vignette 8 design
> **Related Topics:** R301 (Campaign Design), R303 (Deterrence Theory), R302 (Operational Art),
> `research/01-doctrine-western.md`, `research/02-doctrine-non-western.md`

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

This is the tier's capstone topic: every other R300 concept (campaign design, operational art,
deterrence, COG, EBO, COA analysis) ultimately serves a strategic-level question this topic names
directly — what is space control actually *for*, strategically, and how do real strategic schools of
thought frame that question differently. Closes the R300 tier by giving the implementer the top-level
frame the rest of the tier's vocabulary sits inside.

## 2. Concepts

**Space control as the strategic objective, not destruction of adversary assets as an end in
itself.** Western space doctrine (`research/01-doctrine-western.md`) generally frames the strategic
goal as *assured access and freedom of action* in the space domain for oneself while denying it to an
adversary when necessary — engagement/denial effects (the five D's) are *means*, not the strategic
end; a vignette's capstone-level design (Vignette 8) should be checkable against whether its
objectives actually serve assured-access/denial framing, not merely "did Blue destroy Red's
satellite."

**Competing strategic schools: warfighting domain vs. contested-but-managed commons.** Different
real strategic traditions frame space differently — some emphasize space as a warfighting domain
requiring offensive/defensive parity (closer to traditional military-domain strategy), others
emphasize space as a fragile shared commons where escalation/debris risk (R117, R304) makes restraint
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
strategic cost not borne only by the immediate adversary — debris from a kinetic engagement (R117 §2)
degrades the shared orbital environment for all actors, including the side that "won" the
engagement. This is a strategically unique feature of the domain (no close terrestrial analog at the
same scale) and the doctrinal reason real space strategy treats kinetic restraint as having strategic
value independent of any single engagement's tactical outcome — directly reflected in this
simulator's kinetic-as-rare/consequence-confirmed design choice (MSTR-003 §5).

## 3. Operational Context

Real space-strategy discourse (across both Western and non-Western traditions per the existing
research primers) explicitly debates exactly these framings — assured-access vs. domain-control vs.
commons-management — and the 2022 ASAT-test moratorium (`research/07-legal-norms-and-roe.md`) is a
concrete recent instance of strategic-level reasoning (the shared-commons/debris externality)
producing real policy restraint independent of any single actor's tactical interest.

## 4. Implementation Guidance

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
  shared-commons externality in its framing** — per R117's `debris_risk` declaration and MSTR-003
  §5's reversibility gradient, a vignette that rewards kinetic action without surfacing this
  strategic cost is doctrinally incomplete by this topic's standard.

## 5. Feature Mapping

Vignette authoring, especially capstone-tier vignette design (Vignette 8 and successors), is the
direct consumer.

## 6. Related Topics

R301 (Campaign Design, the operational-level implementation of strategy), R303 (Deterrence Theory),
R302 (Operational Art), `research/01-doctrine-western.md`, `research/02-doctrine-non-western.md` (the
existing doctrine primers this topic's strategic frame organizes).
