# R401 — Experimental Design and Controls

> **Document ID:** R401
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R402](R402-hypotheses-and-variables.md), [R411](R411-human-subjects-research.md)
> **Produces:** the vocabulary for isolating one variable's effect on an outcome when evaluating a vignette, Red preset, or assessment instrument change
> **Feature Mapping:** DOM-005 (Validation Framework), any future feature-effectiveness study (e.g. "does the new fleet-rail alarm badge actually improve time-to-decision")
> **Related Topics:** [R402](R402-hypotheses-and-variables.md) (Hypotheses and Variables — the next step after a controlled design),
> [R407](R407-monte-carlo-methods.md) (Monte Carlo Methods — the seeded-repetition mechanism that supplies a control's repeatability
> in this simulator), DOM-005 (Validation Framework)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Any future claim of the form "feature X improved outcome Y" (a UI change improved time-to-decision,
a Red preset revision improved Blue's learning curve) requires isolating X's effect from confounds —
session-to-session variance in operator skill, vignette difficulty, or random seed. This topic gives
the implementer the experimental-design vocabulary to make such a claim defensibly, rather than
informally, from a handful of unstructured playtest sessions.

## 2. Concepts

**Controls isolate the variable of interest by holding everything else constant.** A controlled
comparison changes exactly one thing between conditions (the feature under test) while holding the
vignette, Red preset, and (where the engine allows) the RNG seed fixed — without this, an observed
difference in outcome cannot be attributed to the changed variable rather than to one of the held
variables drifting uncontrolled.

**Between-subjects vs. within-subjects designs.** A between-subjects design compares different
operators/sessions under different conditions (more realistic, more confound-prone — operator skill
varies); a within-subjects design compares the same operator's repeated runs under different
conditions (controls for skill, but vulnerable to a learning-effect confound across repeated runs of
similar content) — this simulator's seeded determinism (`SeededRng`, [`engine/rng.py`](../../../spacesim/engine/rng.py)) makes a
within-subjects design unusually feasible: the same seed reproduces an identical Red/environment
behavior across two runs that differ only in the feature being tested.

**Random assignment controls for unknown confounds.** Where a between-subjects comparison is
necessary (e.g. comparing two cohorts of trainees), randomly assigning which cohort gets which
condition is the standard defense against an unmeasured confound (e.g. one cohort happening to be
more experienced) systematically favoring one condition.

**A confound is a variable that varies alongside the variable of interest and could explain the
observed effect instead.** The most common confound risk in this simulator's context is vignette
difficulty drift across versions — if a vignette's YAML is edited between "before" and "after"
measurement for any reason other than the feature under test, difficulty itself becomes an
uncontrolled confound, not the feature.

## 3. Operational Context

Controlled experimental design is the foundational discipline underlying every quantitative claim in
applied research, military operations research included — the U.S. military's own operations-research
tradition (dating to WWII operational analysis) explicitly adopted controlled-comparison methodology
specifically because uncontrolled before/after comparisons in real-world military contexts are
notoriously confound-prone (force composition, weather, and adversary behavior all vary
simultaneously); this simulator's determinism gives an implementer a control standard real-world
military OR analysts rarely have access to.

## 4. Implementation Guidance

- **Any future feature-effectiveness claim (DOM-005 §4's validation method) should be evaluated under
  a controlled comparison**: same vignette, same Red preset, same seed where feasible, varying only
  the feature under test — an uncontrolled "we shipped it and players seemed happier" claim does not
  meet this bar.
- **Exploit the engine's determinism for within-subjects designs**: because `(initial_state,
  eventlog, seed) → byte-identical state` (the Phase-1 invariant), a feature-comparison study can
  replay the identical Red/environment behavior across "before" and "after" conditions, removing
  random-seed variance as a confound entirely — a comparison study should state explicitly whether it
  exploited this or not.
- **Treat vignette-YAML edits between measurement conditions as a confound risk to flag explicitly**
  in any study design — a difficulty-affecting YAML change between "before" and "after" runs
  invalidates a same-seed comparison's controlled-comparison claim.
- **A future feature-effectiveness study design document should state its design type** (between-
  vs. within-subjects, randomized vs. not) explicitly, per [R402](R402-hypotheses-and-variables.md)'s hypothesis-and-variable vocabulary,
  rather than leaving the comparison's structure implicit.

## 5. Feature Mapping

DOM-005 (Validation Framework) and any future feature-effectiveness study are the direct consumers.

## 6. Related Topics

[R402](R402-hypotheses-and-variables.md) (Hypotheses and Variables, the next step), [R407](R407-monte-carlo-methods.md) (Monte Carlo Methods, this simulator's
seeded-repetition control mechanism), DOM-005 (Validation Framework).
