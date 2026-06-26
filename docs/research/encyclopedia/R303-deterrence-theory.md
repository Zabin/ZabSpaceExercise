# R303 — Deterrence Theory

> **Document ID:** R303
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** R304, R312, DOM-009
> **Produces:** the doctrinal vocabulary behind ROE-gated kinetic authorization as a deterrence-preserving design
> **Feature Mapping:** FS-105 (Spacecraft Operations), vignette ROE design
> **Related Topics:** R304 (Escalation Dynamics), R213 (Signaling Theory), R312 (Space Strategy),
> `research/07-legal-norms-and-roe.md`

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

ROE in this simulator gates the highest-stakes capability (kinetic engagement, R117) behind explicit
authorization (`roe.get("kinetic_authorized")`) — this topic supplies the doctrinal theory of *why*
real ROE design treats kinetic authorization this way: deterrence requires credible restraint as
much as credible capability, and an ROE-design feature should reflect that, not just gate capability
arbitrarily.

## 2. Concepts

**Deterrence by denial vs. deterrence by punishment.** Deterrence by denial discourages an action by
making it unlikely to succeed (a hardened, well-defended asset with strong custody/SDA, deterring an
attack because it would likely fail); deterrence by punishment discourages an action by threatening a
costly response after the fact (a credible kinetic-response capability, deterring an attack because
retaliation would be too costly). A vignette's Blue posture can be designed to emphasize one or the
other — a defensive-EW-heavy posture leans denial; an ROE permitting proportionate kinetic response
leans punishment.

**Compellence vs. deterrence.** Deterrence discourages an adversary from *starting* an action;
compellence tries to make an adversary *stop* an ongoing action or *start* doing something it
otherwise wouldn't. Distinguishing the two matters for vignette design: an inject escalating Red's
posture mid-exercise tests Blue's compellence options (can Blue make Red stop), a different design
problem than the initial deterrence posture the vignette opens with.

**Credibility as the central deterrence variable.** A threat that is not believed to be both capable
and resolute fails to deter, regardless of its objective strength — this is the doctrinal link to
R213 (Signaling Theory): a Blue capability that is real but never credibly signaled (e.g. a kinetic
capability Red has no reason to believe Blue would actually use) deters less than the same capability
paired with credible signaling, which is why ROE/escalation posture is itself part of deterrence
design, not just a legal constraint layered on top.

**The stability-instability paradox.** Strong deterrence at the highest level (mutual capability to
inflict unacceptable costs) can paradoxically make lower-level provocations (proximity harassment,
reversible EW/cyber) more likely, since actors calculate the high-end threshold won't be crossed over
a low-stakes incident — directly relevant to why this simulator's *reversible* effect categories
(EW/cyber/RPO) are the common, expected texture of contested operations, with kinetic engagement
rare, exactly mirroring real stability-instability dynamics in counterspace competition.

## 3. Operational Context

Real space-deterrence doctrine explicitly wrestles with exactly these distinctions — credible
denial/punishment postures, the asymmetry between reversible "gray zone" actions and rare,
escalatory kinetic options, and the stability-instability dynamic are live doctrinal concerns in
real counterspace strategy discussions, not abstractions invented for this simulator.

## 4. Implementation Guidance

- **A vignette's ROE design should state explicitly which deterrence posture (denial-leaning,
  punishment-leaning, or mixed) it represents**, since this shapes which Red behaviors are
  "expected" (gray-zone reversible provocation, per the stability-instability paradox) vs. genuinely
  anomalous (an early kinetic move, which should read as a deliberate escalation-test inject, not
  default Red behavior).
- **A future Red-AI doctrine preset modeling deterrence failure (a Red posture that escalates despite
  Blue's capability) should be designed as a deliberate, named scenario variant** (testing whether
  Blue's signaling/posture was credible), not an unexplained behavior change — per DOM-008 §3, Red
  presets must stay legible to White Cell.
- **Don't conflate "Blue has ROE authorization for kinetic response" with "Blue should use it"** — a
  vignette teaching deterrence discipline should reward credible *restraint* (maintaining the
  capability without using it, when that's the doctrinally correct choice) as much as a vignette
  testing engagement skill rewards correct kinetic execution.

## 5. Feature Mapping

FS-105 (Spacecraft Operations) and vignette ROE design are the direct consumers.

## 6. Related Topics

R304 (Escalation Dynamics, the dynamic process this topic's static postures interact with), R213
(Signaling Theory, the credibility mechanism), R312 (Space Strategy), `research/07-legal-norms-and-
roe.md` (the existing ROE/legal mapping this topic's doctrine informs).
