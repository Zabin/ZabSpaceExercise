# R401 — Experimental Design and Controls

> **Document ID:** R401
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R402](R402-hypotheses-and-variables.md), [R411](R411-human-subjects-research.md)
> **Produces:** the vocabulary for isolating one variable's effect on an outcome when evaluating a vignette, Red preset, or assessment instrument change
> **Feature Mapping:** DOM-005 (Validation Framework), any future feature-effectiveness study (e.g. "does the new fleet-rail alarm badge actually improve time-to-decision")
> **Related Topics:** [R402](R402-hypotheses-and-variables.md) (Hypotheses and Variables — the next step after a controlled design),
> [R407](R407-monte-carlo-methods.md) (Monte Carlo Methods — the seeded-repetition mechanism that supplies a control's repeatability
> in this simulator), DOM-005 (Validation Framework)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A foundational experimental-design and military-OR texts — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Any future claim of the form "feature X improved outcome Y" (a UI change improved time-to-decision,
a Red preset revision improved Blue's learning curve) requires isolating X's effect from confounds —
session-to-session variance in operator skill, vignette difficulty, or random seed. This topic gives
the implementer the experimental-design vocabulary to make such a claim defensibly, rather than
informally, from a handful of unstructured playtest sessions.

## 2. Scope

Covers: control-group logic, between-subjects vs. within-subjects design, randomization, and
confound identification, as applied to a feature-effectiveness claim in this simulator. Does **not**
cover: stating the claim itself as a falsifiable hypothesis with named variables
([R402](R402-hypotheses-and-variables.md)'s job), the statistical test used to analyze the resulting
data ([R403](R403-statistics-foundations.md)'s job), or the seeded-repetition mechanism this topic's
within-subjects design leans on ([R407](R407-monte-carlo-methods.md)'s job, referenced here only for
its role as a control).

## 3. Concepts

**Controls isolate the variable of interest by holding everything else constant.** A controlled
comparison changes exactly one thing between conditions (the feature under test) while holding the
vignette, Red preset, and (where the engine allows) the RNG seed fixed — without this, an observed
difference in outcome cannot be attributed to the changed variable rather than to one of the held
variables drifting uncontrolled. This is the foundational logic Ronald Fisher formalized for
agricultural field trials and that Donald Campbell and Julian Stanley's classic monograph,
[*Experimental and Quasi-Experimental Designs for Research*](https://www.sfu.ca/~palys/Campbell&Stanley-1959-Exptl&QuasiExptlDesignsForResearch.pdf)
(1963), systematized into a taxonomy of research designs and their associated "threats to internal
validity" — alternative plausible explanations for an observed effect that a design fails to rule
out.

**Between-subjects vs. within-subjects designs.** A between-subjects design compares different
operators/sessions under different conditions (more realistic, more confound-prone — operator skill
varies); a within-subjects design compares the same operator's repeated runs under different
conditions (controls for skill, but vulnerable to a learning-effect confound across repeated runs of
similar content — Campbell & Stanley's "testing" and "maturation" threats to internal validity apply
directly here) — this simulator's seeded determinism (`SeededRng`, [`engine/rng.py`](../../../spacesim/engine/rng.py)) makes a
within-subjects design unusually feasible: the same seed reproduces an identical Red/environment
behavior across two runs that differ only in the feature being tested.

**Random assignment controls for unknown confounds.** Where a between-subjects comparison is
necessary (e.g. comparing two cohorts of trainees), randomly assigning which cohort gets which
condition is the standard defense against Campbell & Stanley's **"selection"** threat — an unmeasured
confound (e.g. one cohort happening to be more experienced) systematically favoring one condition.

**A confound is a variable that varies alongside the variable of interest and could explain the
observed effect instead.** Campbell & Stanley's **"history"** threat — events occurring between
measurements other than the experimental variable itself — is the most common confound risk in this
simulator's context: if a vignette's YAML is edited between "before" and "after" measurement for any
reason other than the feature under test, difficulty itself becomes an uncontrolled confound, not the
feature.

### Sources

- *Campbell, D.T. & Stanley, J.C. (1963). Experimental and Quasi-Experimental Designs for Research.*
  Houghton Mifflin — [live](https://www.sfu.ca/~palys/Campbell&Stanley-1959-Exptl&QuasiExptlDesignsForResearch.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.sfu.ca/~palys/Campbell&Stanley-1959-Exptl&QuasiExptlDesignsForResearch.pdf)
  · accessed 2026-07-02.

## 4. Operational Context

Controlled experimental design is the foundational discipline underlying every quantitative claim in
applied research, military operations research included. The U.S. military's own operations-research
tradition traces to Philip Morse and George Kimball's WWII anti-submarine-warfare analysis work,
published unclassified as
[*Methods of Operations Research*](https://www.loc.gov/item/2015490946/) (1951) — explicitly adopting
controlled-comparison methodology (measuring the effect of a specific tactical or equipment change)
specifically because uncontrolled before/after comparisons in real-world military contexts are
notoriously confound-prone (force composition, weather, and adversary behavior all vary
simultaneously). This simulator's determinism gives an implementer a control standard real-world
military OR analysts of the Morse/Kimball era rarely had access to.

### Sources

- *Morse, P.M. & Kimball, G.E. (1951). Methods of Operations Research.* Technology Press/John Wiley &
  Sons — [live (Library of Congress catalog record)](https://www.loc.gov/item/2015490946/)
  · [snapshot](https://web.archive.org/web/2026*/https://www.loc.gov/item/2015490946/)
  · accessed 2026-07-02.

## 5. Implementation Guidance

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
  in any study design, per Campbell & Stanley's "history" threat — a difficulty-affecting YAML change
  between "before" and "after" runs invalidates a same-seed comparison's controlled-comparison claim.
- **A future feature-effectiveness study design document should state its design type** (between-
  vs. within-subjects, randomized vs. not, and which Campbell & Stanley internal-validity threats it
  addresses) explicitly, per [R402](R402-hypotheses-and-variables.md)'s hypothesis-and-variable vocabulary,
  rather than leaving the comparison's structure implicit.

## 6. Feature Mapping

DOM-005 (Validation Framework) and any future feature-effectiveness study are the direct consumers.

## 7. Related Topics

[R402](R402-hypotheses-and-variables.md) (Hypotheses and Variables, the next step), [R407](R407-monte-carlo-methods.md) (Monte Carlo Methods, this simulator's
seeded-repetition control mechanism), DOM-005 (Validation Framework).
