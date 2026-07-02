# R403 — Statistics Foundations

> **Document ID:** R403
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R404](R404-measurement-theory.md), [R405](R405-uncertainty-analysis.md), [R407](R407-monte-carlo-methods.md), [R412](R412-survey-and-assessment-instrument-design.md), [R413](R413-data-analysis-and-reporting.md)
> **Produces:** the descriptive/inferential vocabulary needed to read any output DOM-002's measurement dimensions or a Monte Carlo sweep ([R407](R407-monte-carlo-methods.md)) produce
> **Feature Mapping:** DOM-002 (Assessment Framework), DOM-005 (Validation Framework), any future analytics/reporting feature over collected exercise data
> **Related Topics:** [R404](R404-measurement-theory.md) (Measurement Theory), [R405](R405-uncertainty-analysis.md) (Uncertainty Analysis), [R407](R407-monte-carlo-methods.md) (Monte Carlo
> Methods — produces the distributions this topic's vocabulary describes), [R413](R413-data-analysis-and-reporting.md) (Data Analysis and
> Reporting)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 1 (Tier A NIST government standard reference — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Several future-facing capabilities in this project — DOM-002's six measurement dimensions, DOM-005's
Monte Carlo validation workhorse (§6, citing [R407](R407-monte-carlo-methods.md)), any future cross-session analytics — eventually
produce numbers that need to be summarized and compared. This topic supplies the minimal descriptive
and inferential statistics vocabulary an implementer needs to do that correctly, without
over-claiming precision the underlying data doesn't support.

## 2. Scope

Covers: the descriptive-vs-inferential distinction, mean/median/skew, variance/spread, sample-size
caution, and correlation-vs-causation, as applied to summarizing DOM-002 measurement-dimension data
or Monte Carlo sweep output. Does **not** cover: the scales-of-measurement / reliability-vs-validity
distinction a metric itself must satisfy before these statistics are meaningful
([R404](R404-measurement-theory.md)'s job), formal uncertainty propagation
([R405](R405-uncertainty-analysis.md)'s job), or the Monte Carlo sampling method that generates the
distributions this topic describes ([R407](R407-monte-carlo-methods.md)'s job, assumed as the
producer of the data this topic summarizes).

## 3. Concepts

**Descriptive statistics summarize a dataset; inferential statistics generalize beyond it.** Mean,
median, and standard deviation describe a specific batch of recorded sessions; an inferential claim
("this feature generalizes to all future Vignette-5 runs") requires additional assumptions a purely
descriptive summary does not justify. The NIST/SEMATECH *e-Handbook of Statistical Methods* (NIST
Handbook 151), the standard U.S. government engineering-statistics reference, draws this same
distinction as foundational: descriptive statistics characterize the data at hand, while inferential
procedures draw conclusions about a population beyond the sample actually observed
([NIST/SEMATECH e-Handbook of Statistical Methods](https://www.itl.nist.gov/div898/handbook/)). A
future reporting feature should distinguish "here is what happened in these N recorded sessions"
(descriptive, always defensible) from "this will happen in general" (inferential, requires a stated
sample-size/representativeness justification).

**Mean vs. median, and why skew matters.** A skewed distribution (e.g. time-to-decision, where most
decisions are fast but a few are very slow) makes the mean misleading relative to the median — the
NIST Handbook's exploratory-data-analysis chapter specifically recommends reporting the median (or
the full distribution shape) rather than only the mean for skewed engineering data
([NIST/SEMATECH e-Handbook, EDA chapter](https://www.itl.nist.gov/div898/handbook/eda/eda.htm)) — a
future reporting feature computing DOM-002 §4's time-to-decision metric should follow the same
practice, since a handful of long outlier decisions can dominate a mean in a way that misrepresents
typical performance.

**Variance and standard deviation describe spread, not just center.** Two sessions with the same
mean escalation-discipline score but very different variance represent different things (consistently
moderate restraint vs. erratic mix of highly restrained and highly aggressive choices) — DOM-002 §5's
rubric-not-single-score principle is partly a statistical point: a single mean number collapses
exactly the spread information that distinguishes these two cases.

**Sample size and the danger of small-N over-generalization.** A handful of playtest sessions is a
small, non-representative sample; any claim drawn from it should be qualified by sample size — this is
the statistical grounding for DOM-005 §6's insistence on Monte Carlo ([R407](R407-monte-carlo-methods.md)) sweeps across many seeded
runs rather than treating a single observed run, or even a handful of manual playtests, as conclusive.

**Correlation is not causation.** Observing that sessions with higher custody-quality scores also
tend to have better mission outcomes does not establish that custody quality *causes* better
outcomes (both could be driven by a confound, e.g. operator skill, [R401](R401-experimental-design-and-controls.md)) — a future analytics feature
reporting cross-dimension correlations (DOM-002's six dimensions) should not imply causal language
without a controlled comparison ([R401](R401-experimental-design-and-controls.md)/[R402](R402-hypotheses-and-variables.md)) to back it.

### Sources

- *NIST/SEMATECH e-Handbook of Statistical Methods* (NIST Handbook 151, National Institute of
  Standards and Technology) — [live](https://www.itl.nist.gov/div898/handbook/)
  · [snapshot](https://web.archive.org/web/2026*/https://www.itl.nist.gov/div898/handbook/)
  · accessed 2026-07-02.
- *NIST/SEMATECH e-Handbook of Statistical Methods*, Exploratory Data Analysis chapter —
  [live](https://www.itl.nist.gov/div898/handbook/eda/eda.htm)
  · [snapshot](https://web.archive.org/web/2026*/https://www.itl.nist.gov/div898/handbook/eda/eda.htm)
  · accessed 2026-07-02.

## 4. Operational Context

These statistical fundamentals (descriptive vs. inferential, mean/median/variance, sample-size
caution, correlation-vs-causation) are the universal foundation underlying every quantitative claim
in applied social science and operations research, codified for engineering practice specifically in
the NIST/SEMATECH Handbook cited above; their absence is a common, well-documented source of
overclaiming in training-effectiveness literature specifically, since training studies routinely run
on small samples and are tempted to report only a favorable mean.

### Sources

Uses the same sources cited inline in §3 (NIST/SEMATECH e-Handbook of Statistical Methods); no
additional sources introduced in this section.

## 5. Implementation Guidance

- **Any future feature reporting a DOM-002 dimension across multiple sessions should report a
  distribution summary (median + spread), not a bare mean** — per the skew concern above and the
  NIST Handbook's EDA guidance, a bare mean on a small sample risks misrepresenting typical
  performance.
- **Any claim drawn from a small number of manual playtest sessions should be explicitly qualified
  by its sample size** in any writeup — per DOM-005 §6, prefer [R407](R407-monte-carlo-methods.md)'s Monte Carlo sweep across many
  seeds wherever the engine's determinism makes that feasible, rather than generalizing from a
  handful of manual runs.
- **A future cross-dimension analytics feature must not report a correlation between two DOM-002
  dimensions using causal language** ("X causes Y") without an explicit controlled comparison
  ([R401](R401-experimental-design-and-controls.md)/[R402](R402-hypotheses-and-variables.md)) behind it — report correlation as correlation.

## 6. Feature Mapping

DOM-002 (Assessment Framework) and DOM-005 (Validation Framework) are the direct consumers; any
future analytics/reporting feature over collected exercise data inherits this vocabulary.

## 7. Related Topics

[R404](R404-measurement-theory.md) (Measurement Theory), [R405](R405-uncertainty-analysis.md) (Uncertainty Analysis), [R407](R407-monte-carlo-methods.md) (Monte Carlo Methods, the source of the
distributions this topic describes), [R413](R413-data-analysis-and-reporting.md) (Data Analysis and Reporting).
