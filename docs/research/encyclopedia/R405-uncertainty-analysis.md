# R405 — Uncertainty Analysis

> **Document ID:** R405
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R403](R403-statistics-foundations.md)
> **Referenced By:** —
> **Produces:** the vocabulary for reporting a derived metric's uncertainty rather than a bare point estimate
> **Feature Mapping:** DOM-005 (Validation Framework), any future analytics feature deriving a summary statistic from a Monte Carlo sweep ([R407](R407-monte-carlo-methods.md))
> **Related Topics:** [R403](R403-statistics-foundations.md) (Statistics Foundations), [R407](R407-monte-carlo-methods.md) (Monte Carlo Methods — the typical source
> of the sample this topic's uncertainty bounds are computed over), [R408](R408-sensitivity-analysis.md) (Sensitivity Analysis —
> a complementary technique addressing input uncertainty rather than sampling uncertainty)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 1 (Tier A NIST measurement-uncertainty standard — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

A point estimate ("the new Red preset wins 62% of Vignette-3 runs") without any uncertainty bound is
incomplete and can be misleading if the underlying sample is small. This topic gives the implementer
the vocabulary to report a derived metric honestly — with its uncertainty made visible rather than
hidden behind a single confident-looking number.

## 2. Scope

Covers: point estimates vs. uncertainty bounds, sampling vs. parameter uncertainty, uncertainty
propagation through a derived/composite metric, and precision-vs-accuracy, applied to reporting a
Monte Carlo–derived or DOM-002 composite metric. Does **not** cover: the sampling method that
generates the runs an uncertainty bound is computed over ([R407](R407-monte-carlo-methods.md)'s job),
or the technique for probing how much an *input* parameter's uncertainty (as opposed to sampling
count) moves an output ([R408](R408-sensitivity-analysis.md)'s job, referenced here only as the
complementary technique).

## 3. Concepts

**A point estimate is a single best-guess number; an uncertainty bound expresses how much that
number could plausibly be off.** The international measurement-science standard for this — the
*Guide to the Expression of Uncertainty in Measurement* (GUM), and its NIST implementation,
[*NIST Technical Note 1297, Guidelines for Evaluating and Expressing the Uncertainty of NIST
Measurement Results*](https://www.nist.gov/pml/nist-technical-note-1297) (Taylor & Kuyatt, 1994) —
formalizes exactly this distinction, classifying uncertainty evaluation into **Type A** (statistical
analysis of a series of observations — directly analogous to this simulator's Monte Carlo sample) and
**Type B** (evaluation by other means, e.g. a stated bound on a known systematic effect), and
defining **combined standard uncertainty** and **expanded uncertainty** (a stated-confidence
interval) as the standard reporting forms. A confidence interval (e.g. "62% ± 8%, based on N=40
runs") is the standard way of expressing this — the width of the interval shrinks as sample size (N,
[R407](R407-monte-carlo-methods.md)'s number of seeded runs) grows, which is the formal reason a
small-N claim ([R403](R403-statistics-foundations.md)) should be treated cautiously.

**Sources of uncertainty: sampling uncertainty vs. parameter uncertainty.** Sampling uncertainty
(NIST TN 1297's Type A) comes from having only a finite number of runs (more Monte Carlo seeds
shrinks it); parameter uncertainty (closer to NIST TN 1297's Type B) comes from not knowing the
"true" value of an input the model depends on (e.g. a doctrine preset's exact aggressiveness
calibration) — Monte Carlo ([R407](R407-monte-carlo-methods.md)) addresses the first; sensitivity
analysis ([R408](R408-sensitivity-analysis.md)) addresses the second by testing how much the output
changes if the uncertain parameter is varied.

**Propagating uncertainty through a derived calculation.** NIST TN 1297's **combined standard
uncertainty** concept states this formally: if a reported metric is computed by combining several
measured quantities (e.g. an aggregate "mission effectiveness" combining several DOM-002 dimensions),
the combined metric's uncertainty is generally larger than any single input's uncertainty, not
smaller — a feature that combines multiple uncertain inputs into one number without acknowledging
this compounds DOM-002 §5's caution against composite scores with an additional, distinct
uncertainty-hiding problem.

**Distinguishing precision from accuracy.** A result can be reported with many decimal places
(looking precise) while still being inaccurate (wrong, due to a bias or confound, [R401](R401-experimental-design-and-controls.md)) — false
precision (e.g. reporting "61.73% win rate" from a 20-run sample) misleads a reader into more
confidence than the underlying sample supports; NIST TN 1297's reporting guidance is explicit that a
result's stated precision should never exceed what its stated uncertainty justifies.

### Sources

- *Taylor, B.N. & Kuyatt, C.E. (1994). NIST Technical Note 1297: Guidelines for Evaluating and
  Expressing the Uncertainty of NIST Measurement Results.* National Institute of Standards and
  Technology — [live](https://www.nist.gov/pml/nist-technical-note-1297)
  · [snapshot](https://web.archive.org/web/2026*/https://www.nist.gov/pml/nist-technical-note-1297)
  · accessed 2026-07-02.

## 4. Operational Context

Uncertainty quantification is standard practice in any quantitative operations-research or scientific
reporting context specifically because a bare point estimate without an uncertainty bound is the most
common source of false confidence in applied analysis — NIST TN 1297's guidelines were written
because this failure mode was common enough across the broader measurement-science community to
require a formal, government-standard corrective. This is especially relevant to a Monte
Carlo–capable deterministic engine like this simulator's, where it is comparatively cheap (just more
seeded runs) to actually shrink sampling uncertainty rather than report a single run's result as if it
were definitive.

### Sources

Uses the same source cited inline in §3 (NIST TN 1297); no additional sources introduced in this
section.

## 5. Implementation Guidance

- **Any future feature reporting a derived metric from a Monte Carlo sweep ([R407](R407-monte-carlo-methods.md)) should report an
  uncertainty bound (e.g. a confidence interval, per NIST TN 1297's "expanded uncertainty" concept)
  alongside the point estimate**, not the point estimate alone — and should state the N (number of
  seeded runs) the bound is based on.
- **A composite metric combining several DOM-002 dimensions should propagate, not hide, the combined
  uncertainty** (NIST TN 1297's combined-standard-uncertainty rule) — report the composite's own
  uncertainty bound, which should generally be wider than any single input dimension's, rather than
  presenting the composite with false precision.
- **Avoid reporting more decimal places than the sample size justifies** — a 20-run sample does not
  support a percentage reported to two decimal places; round to a precision consistent with the
  actual uncertainty.

## 6. Feature Mapping

DOM-005 (Validation Framework) and any future Monte Carlo–derived analytics feature are the direct
consumers.

## 7. Related Topics

[R403](R403-statistics-foundations.md) (Statistics Foundations), [R407](R407-monte-carlo-methods.md) (Monte Carlo Methods, the typical uncertainty source), [R408](R408-sensitivity-analysis.md)
(Sensitivity Analysis, the complementary technique for parameter rather than sampling uncertainty).
