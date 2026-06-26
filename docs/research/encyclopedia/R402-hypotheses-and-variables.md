# R402 — Hypotheses and Variables

> **Document ID:** R402
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R401
> **Referenced By:** —
> **Produces:** the vocabulary for stating a falsifiable claim about a feature or vignette change before measuring it
> **Feature Mapping:** DOM-005 (Validation Framework), DOM-002 (Assessment Framework)
> **Related Topics:** R401 (Experimental Design and Controls), R403 (Statistics Foundations — the
> test of a stated hypothesis), DOM-002 (Assessment Framework — the six measurement dimensions are
> candidate dependent variables)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

R401 establishes how to isolate one variable's effect; this topic gives the vocabulary for stating,
*before* running that comparison, exactly what outcome is predicted and exactly what is being varied
— the discipline that turns "let's see what happens" into a claim that can actually be confirmed or
refuted by the resulting data.

## 2. Concepts

**A hypothesis must be falsifiable.** A useful hypothesis states a specific, checkable prediction
("the fleet-rail alarm badge reduces median time-to-decision by at least 10%") rather than a vague
expectation ("the alarm badge should help") — DOM-002 §4's time-to-decision metric is exactly the
kind of dependent variable that makes a falsifiable claim possible; an unfalsifiable claim cannot be
wrong, which means it also cannot be validated.

**Independent, dependent, and confound variables.** The independent variable is what the
experimenter deliberately changes (the feature under test); the dependent variable is what is
measured as a result (one of DOM-002 §4's six dimensions, e.g. window discipline or
escalation discipline); a confound (R401) is an uncontrolled variable that could also explain a
change in the dependent variable — a hypothesis statement should name all three explicitly.

**The null hypothesis as the default to be ruled out.** Standard practice states a null hypothesis
("the feature has no effect on the dependent variable") and treats the experimental hypothesis as
something that must be established against that default, not assumed — this guards against
confirmation bias (R207) in interpreting an ambiguous result as support for the feature the
implementer already wants to ship.

**Operationalizing a vague claim into a measurable variable.** Most candidate hypotheses about this
simulator's features start vague ("does this make the exercise more realistic," "does this improve
learning") — operationalizing means picking a specific, measurable proxy (e.g. one of DOM-002's six
dimensions, or a survey instrument per R412) and explicitly stating the proxy's limits, since no
single proxy fully captures a vague construct like "realism" or "learning."

## 3. Operational Context

The hypothesis-variable discipline is foundational to the scientific method broadly and to applied
social-science/training-effectiveness research specifically — its absence is the single most common
failure mode in informal feature evaluation (the "it felt better" report), because an unstated,
unfalsifiable expectation cannot be checked against contrary evidence and tends to survive regardless
of what the data actually shows.

## 4. Implementation Guidance

- **Any future feature-effectiveness study (DOM-005 §4) should state its hypothesis, independent
  variable, dependent variable, and null hypothesis explicitly before measurement**, not after —
  stating these after seeing the data risks post-hoc rationalization (R207's confirmation bias) of
  whatever the data happened to show.
- **Prefer DOM-002 §4's six measurement dimensions as off-the-shelf dependent variables** rather than
  inventing a new, unvalidated metric per study — reusing an already-discussed dimension keeps
  separate studies comparable to each other.
- **Flag any "realism" or "learning" claim as an operationalization choice, not a direct
  measurement**, in any study writeup — naming the specific proxy used (e.g. "time-to-decision as a
  proxy for OODA-loop tightness," R208) keeps the claim's actual scope visible rather than implicitly
  overclaiming the vague construct itself.

## 5. Feature Mapping

DOM-005 (Validation Framework) and DOM-002 (Assessment Framework) are the direct consumers.

## 6. Related Topics

R401 (Experimental Design and Controls, the preceding step), R403 (Statistics Foundations, how a
stated hypothesis gets tested against data), DOM-002 (Assessment Framework).
