# R407 — Monte Carlo Methods

> **Document ID:** R407
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R403](R403-statistics-foundations.md), [R406](R406-modeling-practices.md)
> **Referenced By:** [R405](R405-uncertainty-analysis.md), [R408](R408-sensitivity-analysis.md)
> **Produces:** the seeded-repetition methodology DOM-005 §6 names as "the validation workhorse" for this simulator
> **Feature Mapping:** DOM-005 (Validation Framework §6), any future feature-effectiveness or balance study (Red preset tuning, vignette difficulty calibration)
> **Related Topics:** [R403](R403-statistics-foundations.md) (Statistics Foundations), [R405](R405-uncertainty-analysis.md) (Uncertainty Analysis — the bound this
> method's output should be reported with), [R408](R408-sensitivity-analysis.md) (Sensitivity Analysis — frequently run as a
> parameter sweep across Monte Carlo batches), [`engine/rng.py`](../../../spacesim/engine/rng.py) (`SeededRng`, the mechanism that
> makes this method exact and reproducible in this codebase)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A founding paper + this project's own determinism precedent — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-005 §6 names Monte Carlo methods as the validation workhorse for fidelity and balance claims in
this simulator, while explicitly warning that the engine's own determinism must never be relaxed "to
sample variability" — variation must instead be driven externally, across seeds. This topic supplies
the Monte Carlo vocabulary and explains exactly how that external-seed-sweep pattern is meant to
work, given [`engine/rng.py`](../../../spacesim/engine/rng.py)'s `SeededRng`.

## 2. Scope

Covers: the Monte Carlo repeated-sampling method, the seed-sweep pattern this codebase uses to apply
it without relaxing determinism, batch-size/convergence, and its role as a balance-tuning tool. Does
**not** cover: the statistical vocabulary used to summarize a Monte Carlo batch's results
([R403](R403-statistics-foundations.md), assumed established here), how to report the resulting
uncertainty bound ([R405](R405-uncertainty-analysis.md)'s job), or systematically varying a single
input parameter across batches ([R408](R408-sensitivity-analysis.md)'s job, frequently built on top
of this topic's batches but a distinct technique).

## 3. Concepts

**Monte Carlo: characterize an outcome distribution by repeated sampling rather than analytic
derivation.** The method was named and formalized by Nicholas Metropolis and Stanislaw Ulam in their
founding 1949 paper,
[*The Monte Carlo Method*](https://www.dam.brown.edu/people/dem/0123017505/MetropolisUlamJASA1949.pdf)
(Journal of the American Statistical Association, 44), developed during the Manhattan Project for
problems (neutron diffusion) where a closed-form analytic solution was intractable but repeated
statistical sampling of the underlying process could characterize the outcome distribution instead.
Where a closed-form answer to "what's the typical outcome of this Red preset against this vignette"
is similarly intractable to derive directly (because of the cascading interaction of many stochastic
effect resolutions), running many repetitions and looking at the resulting distribution of outcomes
is the same standard alternative Metropolis & Ulam formalized.

**Driving variation externally, across seeds — never by relaxing engine determinism.** DOM-005 §6's
load-bearing constraint: a single run of this simulator, given a fixed seed, is exactly reproducible
(the Phase-1 invariant, verified by `spacesim/tests/test_determinism.py`) — a Monte Carlo study does
not mean making the engine itself probabilistic in a new way; it means running the same deterministic
engine many times, once per seed value, drawn from `SeededRng`, and aggregating the resulting (each
individually exact) outcomes. This is a stronger reproducibility guarantee per individual run than
Metropolis & Ulam's original stochastic-process sampling had, since each of this simulator's runs is
itself byte-identical for a given seed rather than merely statistically characterized.

**Batch size and convergence.** The precision of a Monte Carlo estimate improves with the number of
runs, but with diminishing returns (the standard error shrinks proportional to 1/√N, the same
convergence-rate property Metropolis & Ulam's original method exhibits) — a study should report how
many runs were used and ideally show the estimate has stabilized (stopped changing meaningfully) as
more runs were added, rather than reporting a result from an arbitrarily small batch.

**Monte Carlo as a balance-tuning tool, distinct from a single illustrative playtest.** A single
hand-played session shows one possible trajectory; a Monte Carlo sweep across many seeds shows the
range of what's typical vs. what's a rare outlier — this distinction matters directly for Red-preset
tuning ([R308](R308-red-teaming-methodology.md)'s "don't tune Red to validate one intended solution path" warning): a preset that
performs reasonably across a Monte Carlo sweep's range is more credibly calibrated than one tuned to
win or lose one specific hand-played run.

### Sources

- *Metropolis, N. & Ulam, S. (1949). The Monte Carlo Method. Journal of the American Statistical
  Association, 44(247), 335-341.* —
  [live](https://www.dam.brown.edu/people/dem/0123017505/MetropolisUlamJASA1949.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.dam.brown.edu/people/dem/0123017505/MetropolisUlamJASA1949.pdf)
  · accessed 2026-07-02.
- *This simulator's own determinism precedent* — [`spacesim/engine/rng.py`](../../../spacesim/engine/rng.py) (`SeededRng`) and
  [`spacesim/tests/test_determinism.py`](../../../spacesim/tests/test_determinism.py) (the Phase-1
  property test verifying `(initial_state, eventlog, seed) → byte-identical state`).

## 4. Operational Context

Monte Carlo simulation is the standard technique across operations research, finance, and physics for
characterizing the behavior of systems too complex for closed-form analysis, and is particularly
well-suited to deterministic-but-seeded simulators like this one, where each individual run is exact
and reproducible and the only externally injected randomness is the choice of seed — this combination
(deterministic core + externally varied seeds) is closer to the idealized Monte Carlo setup Metropolis
& Ulam originally described than most real-world stochastic simulators achieve, since most Monte Carlo
applications cannot guarantee a single run is itself perfectly reproducible.

### Sources

Uses the same sources cited inline in §3 (Metropolis & Ulam 1949; this project's own
`rng.py`/`test_determinism.py`); no additional sources introduced in this section.

## 5. Implementation Guidance

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

## 6. Feature Mapping

DOM-005 §6 is the direct consumer; any future Red-preset tuning or vignette-difficulty calibration
work inherits this methodology.

## 7. Related Topics

[R403](R403-statistics-foundations.md) (Statistics Foundations), [R405](R405-uncertainty-analysis.md) (Uncertainty Analysis), [R408](R408-sensitivity-analysis.md) (Sensitivity Analysis), `engine/
rng.py`'s `SeededRng` (the mechanism this method depends on).
