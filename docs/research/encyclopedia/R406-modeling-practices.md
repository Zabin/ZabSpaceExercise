# R406 — Modeling Practices

> **Document ID:** R406
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** R407, R409
> **Produces:** the documentation-discipline vocabulary that makes a model's assumptions auditable rather than implicit in code
> **Feature Mapping:** every `engine/` subsystem (`Propagator`, `AccessProvider`, `EffectResolver`, the doctrine presets in `redai.py`), DOM-005 (Validation Framework), DOM-009 (Doctrine Development Framework)
> **Related Topics:** R409 (Verification — confirming a model matches its own spec, the next step
> after this topic's documentation discipline), R410 (Validation), DOM-009 (Doctrine Development
> Framework — the doctrine-to-parameter translation this topic's assumption-documentation discipline
> directly supports)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Every subsystem in `engine/` is a model: the propagator is a model of orbital motion, the jam/cyber/
engage modules are models of effect resolution, a `redai.py` doctrine preset is a model of adversary
decision-making. This topic gives the vocabulary for documenting a model's assumptions and
limitations explicitly, so a future implementer extending it knows what the model does and does not
claim to represent — the precondition for both verification (R409) and validation (R410).

## 2. Concepts

**Every model rests on simplifying assumptions; the discipline is stating them, not avoiding them.**
No model is the real phenomenon — `engine/propagator.py`'s Keplerian+J2 fidelity already deliberately
omits J3/J4 and atmospheric drag (handled separately in `perturbations.py`, behind a seam for future
high-fidelity drop-in per CLAUDE.md) — the documentation discipline is stating which simplifications
were made and why, not pretending the model is complete.

**A model's scope of validity: where it is expected to hold and where it breaks down.** A model
calibrated for one regime can give silently wrong answers outside it (e.g. a Keplerian+J2 propagator
in deep LEO with significant drag, or a Red doctrine preset calibrated for one strategic posture
applied to a scenario assuming a different one, R312) — documenting scope of validity prevents a
future implementer from extending a model past the regime it was actually built for without
realizing it.

**Parsimony: prefer the simplest model that captures the needed behavior.** A model with more free
parameters than the data/use-case justifies risks overfitting to a specific scenario rather than
capturing the general phenomenon — this is the modeling-practice grounding for CLAUDE.md's "content
is data, not code" principle: a vignette-specific special case hardcoded into engine logic is a
parsimony violation, since it adds model complexity that should instead live in the data layer.

**Auditability: a model's assumptions should be checkable by someone who didn't write it.** A model
whose key assumptions live only in a contributor's head (or in comments scattered through
implementation code) is not auditable — DOM-009's doctrine-to-parameter translation pipeline depends
on a `redai.py` preset's strategic assumptions being stated somewhere a reviewer can check them
against the doctrine source, not just inferable from reading the parameter values.

## 3. Operational Context

Documenting model assumptions, scope of validity, and parsimony tradeoffs explicitly is standard
practice across computational science and operations research specifically because an undocumented
model's limitations tend to be rediscovered the hard way — by a downstream user applying it outside
its valid regime and getting a silently wrong answer rather than an explicit warning.

## 4. Implementation Guidance

- **Each `engine/` subsystem with seam documentation (`Propagator`, `AccessProvider`,
  `EffectResolver` per CLAUDE.md) should have its scope of validity stated alongside its interface**
  — the existing fidelity note ("moderate: Keplerian + J2 ... behind interfaces so a high-fidelity
  model drops in later") is the right pattern; extend it to other subsystems that currently lack an
  equivalent explicit statement.
- **A new `redai.py` doctrine preset's modeling assumptions (which strategic posture, what
  information access, what aggressiveness calibration) should be documented alongside the preset**,
  per R312's strategic-culture concept and DOM-009's translation-pipeline requirement — not left
  inferable only from reading the parameter values.
- **Resist adding a vignette-specific special case to engine logic; route it through content data
  instead** — per CLAUDE.md's "content is data" invariant, this is this topic's parsimony principle
  applied directly; a special case in code is a parsimony violation that also breaks auditability for
  a reviewer who only checks the data layer.

## 5. Feature Mapping

Every `engine/` subsystem with a documented seam interface, DOM-005, and DOM-009 are the direct
consumers.

## 6. Related Topics

R409 (Verification, the next step after assumption documentation), R410 (Validation), DOM-009
(Doctrine Development Framework).
