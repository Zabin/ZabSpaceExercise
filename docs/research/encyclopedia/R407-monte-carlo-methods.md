# R407 — Monte Carlo Methods

> **Document ID:** R407
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R403](R403-statistics-foundations.md), [R406](R406-modeling-practices.md)
> **Referenced By:** [R405](R405-uncertainty-analysis.md), [R408](R408-sensitivity-analysis.md)
> **Produces:** the seeded-repetition methodology DOM-005 §6 names as "the validation workhorse" for this simulator
> **Feature Mapping:** DOM-005 (Validation Framework §6), any future feature-effectiveness or balance study (Red preset tuning, vignette difficulty calibration)
> **Related Topics:** [R403](R403-statistics-foundations.md) (Statistics Foundations), [R405](R405-uncertainty-analysis.md) (Uncertainty Analysis — the bound this
> method's output should be reported with), [R408](R408-sensitivity-analysis.md) (Sensitivity Analysis — frequently run as a
> parameter sweep across Monte Carlo batches), [`engine/rng.py`](../../../spacesim/engine/rng.py) (`SeededRng`, the mechanism that
> makes this method exact and reproducible in this codebase)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-005 §6 names Monte Carlo methods as the validation workhorse for fidelity and balance claims in
this simulator, while explicitly warning that the engine's own determinism must never be relaxed "to
sample variability" — variation must instead be driven externally, across seeds. This topic supplies
the Monte Carlo vocabulary and explains exactly how that external-seed-sweep pattern is meant to
work, given [`engine/rng.py`](../../../spacesim/engine/rng.py)'s `SeededRng`.

## 2. Concepts

**Monte Carlo: characterize an outcome distribution by repeated sampling rather than analytic
derivation.** Where a closed-form answer to "what's the typical outcome of this Red preset against
this vignette" is intractable to derive directly (because of the cascading interaction of many
stochastic effect resolutions), running many repetitions and looking at the resulting distribution of
outcomes is the standard alternative.

**Driving variation externally, across seeds — never by relaxing engine determinism.** DOM-005 §6's
load-bearing constraint: a single run of this simulator, given a fixed seed, is exactly reproducible
(the Phase-1 invariant) — a Monte Carlo study does not mean making the engine itself probabilistic in
a new way; it means running the same deterministic engine many times, once per seed value, drawn from
`SeededRng`, and aggregating the resulting (each individually exact) outcomes.

**Batch size and convergence.** The precision of a Monte Carlo estimate improves with the number of
runs, but with diminishing returns (the standard error shrinks proportional to 1/√N) — a study should
report how many runs were used and ideally show the estimate has stabilized (stopped changing
meaningfully) as more runs were added, rather than reporting a result from an arbitrarily small batch.

**Monte Carlo as a balance-tuning tool, distinct from a single illustrative playtest.** A single
hand-played session shows one possible trajectory; a Monte Carlo sweep across many seeds shows the
range of what's typical vs. what's a rare outlier — this distinction matters directly for Red-preset
tuning ([R308](R308-red-teaming-methodology.md)'s "don't tune Red to validate one intended solution path" warning): a preset that
performs reasonably across a Monte Carlo sweep's range is more credibly calibrated than one tuned to
win or lose one specific hand-played run.

## 3. Operational Context

Monte Carlo simulation is the standard technique across operations research, finance, and physics for
characterizing the behavior of systems too complex for closed-form analysis, and is particularly
well-suited to deterministic-but-seeded simulators like this one, where each individual run is exact
and reproducible and the only externally injected randomness is the choice of seed — this combination
(deterministic core + externally varied seeds) is closer to the idealized Monte Carlo setup than most
real-world stochastic simulators achieve.

## 4. Implementation Guidance

- **Any future balance-tuning or fidelity-validation study should run a batch of seeded repetitions
  via `SeededRng`, not rely on a single hand-played session**, per DOM-005 §6 — and should report the
  batch size (N) used.
- **Never propose relaxing engine determinism "to get sample variability" — drive variability
  externally by sweeping the seed input**, per DOM-005 §6's explicit constraint; this is the one
  non-negotiable rule this topic exists to operationalize.
- **Report a Monte Carlo result with an uncertainty bound ([R405](R405-uncertainty-analysis.md)), not a bare point estimate**, and
  state the batch size it's based on.
- **Use a Monte Carlo sweep, not a single tuned run, to evaluate whether a new/revised `redai.py`
  preset is doctrinally credible across the range of likely scenario states** — per [R308](R308-red-teaming-methodology.md)'s caution
  against tuning Red to one intended solution path.

## 5. Feature Mapping

DOM-005 §6 is the direct consumer; any future Red-preset tuning or vignette-difficulty calibration
work inherits this methodology.

## 6. Related Topics

[R403](R403-statistics-foundations.md) (Statistics Foundations), [R405](R405-uncertainty-analysis.md) (Uncertainty Analysis), [R408](R408-sensitivity-analysis.md) (Sensitivity Analysis), `engine/
rng.py`'s `SeededRng` (the mechanism this method depends on).
