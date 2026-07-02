# R402 — Hypotheses and Variables

> **Document ID:** R402
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R401](R401-experimental-design-and-controls.md)
> **Referenced By:** —
> **Produces:** the vocabulary for stating a falsifiable claim about a feature or vignette change before measuring it
> **Feature Mapping:** DOM-005 (Validation Framework), DOM-002 (Assessment Framework)
> **Related Topics:** [R401](R401-experimental-design-and-controls.md) (Experimental Design and Controls), [R403](R403-statistics-foundations.md) (Statistics Foundations — the
> test of a stated hypothesis), DOM-002 (Assessment Framework — the six measurement dimensions are
> candidate dependent variables)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A/B foundational falsifiability + significance-testing sources — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

[R401](R401-experimental-design-and-controls.md) establishes how to isolate one variable's effect; this topic gives the vocabulary for stating,
*before* running that comparison, exactly what outcome is predicted and exactly what is being varied
— the discipline that turns "let's see what happens" into a claim that can actually be confirmed or
refuted by the resulting data.

## 2. Scope

Covers: the falsifiability requirement for a testable claim, the independent/dependent/confound
variable vocabulary, the null-hypothesis default, and operationalization of a vague construct into a
measurable variable. Does **not** cover: how to isolate a variable's effect via a controlled
comparison, assumed established by [R401](R401-experimental-design-and-controls.md); or the
statistical test used to evaluate a stated hypothesis against collected data
([R403](R403-statistics-foundations.md)'s job) — this topic is about stating the claim correctly
*before* measurement, not analyzing the result after.

## 3. Concepts

**A hypothesis must be falsifiable.** Karl Popper's **falsifiability criterion**, developed in *The
Logic of Scientific Discovery* (1934/1959 English edition), proposes falsifiability — the capacity of
a statement to conflict with a possible observation — as the demarcation between scientific and
non-scientific claims: a genuinely scientific hypothesis must specify what observation *would* refute
it, not merely what would confirm it
([Stanford Encyclopedia of Philosophy, "Karl Popper"](https://plato.stanford.edu/entries/popper/)).
A useful hypothesis states a specific, checkable prediction ("the fleet-rail alarm badge reduces
median time-to-decision by at least 10%") rather than a vague expectation ("the alarm badge should
help") — DOM-002 §4's time-to-decision metric is exactly the kind of dependent variable that makes a
falsifiable claim possible; an unfalsifiable claim cannot be wrong, which means it also cannot be
validated.

**Independent, dependent, and confound variables.** The independent variable is what the
experimenter deliberately changes (the feature under test); the dependent variable is what is
measured as a result (one of DOM-002 §4's six dimensions, e.g. window discipline or
escalation discipline); a confound ([R401](R401-experimental-design-and-controls.md)) is an uncontrolled variable that could also explain a
change in the dependent variable — a hypothesis statement should name all three explicitly.

**The null hypothesis as the default to be ruled out.** Ronald Fisher's
[*The Design of Experiments*](https://archive.org/details/in.ernet.dli.2015.502684) (1935) formalized
the null-hypothesis framework still in standard use: state a null hypothesis ("the feature has no
effect on the dependent variable") and treat the experimental hypothesis as something that must be
established as unlikely under the null, not assumed true from the outset — Fisher's own "lady tasting
tea" experiment in that book is the canonical illustration of designing a test specifically to give
the null hypothesis a fair chance to survive. This guards against confirmation bias
([R207](R207-cognitive-biases.md)) in interpreting an ambiguous result as support for the feature the
implementer already wants to ship.

**Operationalizing a vague claim into a measurable variable.** Most candidate hypotheses about this
simulator's features start vague ("does this make the exercise more realistic," "does this improve
learning") — operationalizing means picking a specific, measurable proxy (e.g. one of DOM-002's six
dimensions, or a survey instrument per [R412](R412-survey-and-assessment-instrument-design.md)) and explicitly stating the proxy's limits, since no
single proxy fully captures a vague construct like "realism" or "learning."

### Sources

- *Stanford Encyclopedia of Philosophy, "Karl Popper"* (falsifiability/demarcation criterion,
  summarizing *The Logic of Scientific Discovery*, 1934/1959) —
  [live](https://plato.stanford.edu/entries/popper/)
  · [snapshot](https://web.archive.org/web/2026*/https://plato.stanford.edu/entries/popper/)
  · accessed 2026-07-02.
- *Fisher, R.A. (1935). The Design of Experiments.* Oliver and Boyd —
  [live (Internet Archive full text)](https://archive.org/details/in.ernet.dli.2015.502684)
  · [snapshot](https://web.archive.org/web/2026*/https://archive.org/details/in.ernet.dli.2015.502684)
  · accessed 2026-07-02.

## 4. Operational Context

The hypothesis-variable discipline is foundational to the scientific method broadly and to applied
social-science/training-effectiveness research specifically — its absence is the single most common
failure mode in informal feature evaluation (the "it felt better" report), because an unstated,
unfalsifiable expectation cannot be checked against contrary evidence (Popper's demarcation problem,
§3) and tends to survive regardless of what the data actually shows.

### Sources

Uses the same sources cited inline in §3 (Popper via SEP; Fisher 1935); no additional sources
introduced in this section.

## 5. Implementation Guidance

- **Any future feature-effectiveness study (DOM-005 §4) should state its hypothesis, independent
  variable, dependent variable, and null hypothesis explicitly before measurement**, not after —
  stating these after seeing the data risks post-hoc rationalization ([R207](R207-cognitive-biases.md)'s confirmation bias) of
  whatever the data happened to show, and violates Popper's falsifiability requirement by making the
  claim unfalsifiable in practice even if it is falsifiable in principle.
- **Prefer DOM-002 §4's six measurement dimensions as off-the-shelf dependent variables** rather than
  inventing a new, unvalidated metric per study — reusing an already-discussed dimension keeps
  separate studies comparable to each other.
- **Flag any "realism" or "learning" claim as an operationalization choice, not a direct
  measurement**, in any study writeup — naming the specific proxy used (e.g. "time-to-decision as a
  proxy for OODA-loop tightness," [R208](R208-ooda-loops.md)) keeps the claim's actual scope visible rather than implicitly
  overclaiming the vague construct itself.

## 6. Feature Mapping

DOM-005 (Validation Framework) and DOM-002 (Assessment Framework) are the direct consumers.

## 7. Related Topics

[R401](R401-experimental-design-and-controls.md) (Experimental Design and Controls, the preceding step), [R403](R403-statistics-foundations.md) (Statistics Foundations, how a
stated hypothesis gets tested against data), DOM-002 (Assessment Framework).
