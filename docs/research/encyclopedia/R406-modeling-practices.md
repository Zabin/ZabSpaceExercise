# R406 — Modeling Practices

> **Document ID:** R406
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R407](R407-monte-carlo-methods.md), [R409](R409-verification.md)
> **Produces:** the documentation-discipline vocabulary that makes a model's assumptions auditable rather than implicit in code
> **Feature Mapping:** every `engine/` subsystem (`Propagator`, `AccessProvider`, `EffectResolver`, the doctrine presets in `redai.py`), DOM-005 (Validation Framework), DOM-009 (Doctrine Development Framework)
> **Related Topics:** [R409](R409-verification.md) (Verification — confirming a model matches its own spec, the next step
> after this topic's documentation discipline), [R410](R410-validation.md) (Validation), DOM-009 (Doctrine Development
> Framework — the doctrine-to-parameter translation this topic's assumption-documentation discipline
> directly supports)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A/B modeling-and-simulation practice sources — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Every subsystem in `engine/` is a model: the propagator is a model of orbital motion, the jam/cyber/
engage modules are models of effect resolution, a `redai.py` doctrine preset is a model of adversary
decision-making. This topic gives the vocabulary for documenting a model's assumptions and
limitations explicitly, so a future implementer extending it knows what the model does and does not
claim to represent — the precondition for both verification ([R409](R409-verification.md)) and validation ([R410](R410-validation.md)).

## 2. Scope

Covers: conceptual-model documentation discipline (stated assumptions, scope of validity, parsimony,
auditability), applied to `engine/` subsystems and `redai.py` presets. Does **not** cover: confirming
a model matches its own documented specification ([R409](R409-verification.md)'s job — this topic is
the precondition, stating what the spec *is*) or confirming a model matches the real-world phenomenon
it represents ([R410](R410-validation.md)'s job) — this topic is purely about making a model's
assumptions legible and checkable, prior to either kind of check.

## 3. Concepts

**Every model rests on simplifying assumptions; the discipline is stating them, not avoiding them.**
Robert Sargent's widely-cited framework for simulation modeling,
[*Verification and Validation of Simulation Models*](https://www.informs-sim.org/wsc11papers/016.pdf)
(Winter Simulation Conference, updated through multiple editions), treats the **conceptual model** —
the explicit statement of a simulation's assumptions, structure, and intended problem entity — as the
foundational artifact that both verification and validation are checked against; a simulation
without a documented conceptual model has nothing precise for either check to compare against.
[`engine/propagator.py`](../../../spacesim/engine/propagator.py)'s Keplerian+J2 fidelity already
deliberately omits J3/J4 and atmospheric drag (handled separately in `perturbations.py`, behind a
seam for future high-fidelity drop-in per CLAUDE.md) — the documentation discipline is stating which
simplifications were made and why, not pretending the model is complete.

**A model's scope of validity: where it is expected to hold and where it breaks down.** Sargent's
framework specifically distinguishes **conceptual model validity** (are the assumptions and structure
reasonable for the intended purpose) from **operational validity** (does the model's output behave
accurately enough for that purpose) — both presuppose the model's intended scope is stated, since
neither question is answerable without knowing what regime the model claims to cover. A model
calibrated for one regime can give silently wrong answers outside it (e.g. a Keplerian+J2 propagator
in deep LEO with significant drag, or a Red doctrine preset calibrated for one strategic posture
applied to a scenario assuming a different one, [R312](R312-space-strategy.md)) — documenting scope of validity prevents a
future implementer from extending a model past the regime it was actually built for without
realizing it.

**Parsimony: prefer the simplest model that captures the needed behavior.** A model with more free
parameters than the data/use-case justifies risks overfitting to a specific scenario rather than
capturing the general phenomenon — this is the modeling-practice grounding for CLAUDE.md's "content
is data, not code" principle: a vignette-specific special case hardcoded into engine logic is a
parsimony violation, since it adds model complexity that should instead live in the data layer.

**Auditability: a model's assumptions should be checkable by someone who didn't write it.** The
Department of Defense's own institutional requirement for this is formal, not aspirational:
[DoDI 5000.61, *DoD Modeling and Simulation (M&S) Verification, Validation, and Accreditation
(VV&A)*](https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/500061p.pdf) requires that
"M&S will not be accredited until V&V has been completed for the intended evaluation in the intended
domain," and references MIL-STD-3022 for minimum VV&A *documentation* requirements specifically so a
model's assumptions are reviewable by someone other than its author. A model whose key assumptions
live only in a contributor's head (or in comments scattered through implementation code) is not
auditable in this sense — DOM-009's doctrine-to-parameter translation pipeline depends on a
`redai.py` preset's strategic assumptions being stated somewhere a reviewer can check them against the
doctrine source, not just inferable from reading the parameter values.

### Sources

- *Sargent, R.G. Verification and Validation of Simulation Models.* Proceedings of the Winter
  Simulation Conference (recurring; cited edition via INFORMS Simulation Society) —
  [live](https://www.informs-sim.org/wsc11papers/016.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.informs-sim.org/wsc11papers/016.pdf)
  · accessed 2026-07-02.
- *U.S. Department of Defense. DoD Instruction 5000.61: DoD Modeling and Simulation (M&S)
  Verification, Validation, and Accreditation (VV&A).* —
  [live](https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/500061p.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/500061p.pdf)
  · accessed 2026-07-02.

## 4. Operational Context

Documenting model assumptions, scope of validity, and parsimony tradeoffs explicitly is standard
practice across computational science and operations research specifically because an undocumented
model's limitations tend to be rediscovered the hard way — by a downstream user applying it outside
its valid regime and getting a silently wrong answer rather than an explicit warning. The DoD's own
formal VV&A accreditation requirement (DoDI 5000.61, §3) makes this a hard gate rather than a
best-practice suggestion for any M&S tool used in operational test and evaluation, which is a
considerably higher bar than this project needs to clear but establishes the direction the discipline
points in.

### Sources

Uses the same sources cited inline in §3 (Sargent; DoDI 5000.61); no additional sources introduced in
this section.

## 5. Implementation Guidance

- **Each `engine/` subsystem with seam documentation (`Propagator`, `AccessProvider`,
  `EffectResolver` per CLAUDE.md) should have its scope of validity stated alongside its interface**
  — the existing fidelity note ("moderate: Keplerian + J2 ... behind interfaces so a high-fidelity
  model drops in later") is the right pattern, and functions as this project's lightweight analog of
  Sargent's conceptual-model statement; extend it to other subsystems that currently lack an
  equivalent explicit statement.
- **A new `redai.py` doctrine preset's modeling assumptions (which strategic posture, what
  information access, what aggressiveness calibration) should be documented alongside the preset**,
  per [R312](R312-space-strategy.md)'s strategic-culture concept and DOM-009's translation-pipeline requirement — not left
  inferable only from reading the parameter values.
- **Resist adding a vignette-specific special case to engine logic; route it through content data
  instead** — per CLAUDE.md's "content is data" invariant, this is this topic's parsimony principle
  applied directly; a special case in code is a parsimony violation that also breaks auditability for
  a reviewer who only checks the data layer.

## 6. Feature Mapping

Every `engine/` subsystem with a documented seam interface, DOM-005, and DOM-009 are the direct
consumers.

## 7. Related Topics

[R409](R409-verification.md) (Verification, the next step after assumption documentation), [R410](R410-validation.md) (Validation), DOM-009
(Doctrine Development Framework).
