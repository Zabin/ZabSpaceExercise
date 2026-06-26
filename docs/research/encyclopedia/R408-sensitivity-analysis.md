# R408 — Sensitivity Analysis

> **Document ID:** R408
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R407
> **Referenced By:** R404, R405
> **Produces:** the technique DOM-005 §5 names for checking an assessment instrument's "sensitivity to manipulation"
> **Feature Mapping:** DOM-005 §5 (instrument validation), Red-preset and vignette-difficulty calibration
> **Related Topics:** R407 (Monte Carlo Methods — the batch mechanism sensitivity analysis sweeps
> across), R404 (Measurement Theory — the instrument-validation use of this technique), R405
> (Uncertainty Analysis — parameter uncertainty, the complementary concern to sampling uncertainty)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-005 §5 lists "sensitivity to manipulation" as one of three checks for validating a future
assessment instrument, citing this topic by ID. This document supplies the general sensitivity-
analysis technique that check is a specific application of: systematically varying one input to see
how much it moves an output, used both to find an instrument's gameable inputs and, more broadly, to
find which of a model's parameters actually matter.

## 2. Concepts

**Sensitivity analysis: vary one input, hold others fixed, observe the output's response.** This is
the controlled-comparison method (R401) applied specifically to a model's input parameters rather
than to an experimental treatment — sweeping a single doctrine-preset parameter (e.g. an
aggressiveness dial) across its range while holding the vignette and seed fixed shows how much that
one parameter actually drives the outcome.

**Identifying which parameters matter and which don't.** A model with many parameters often has only
a few that meaningfully drive the output — sensitivity analysis surfaces this, which is directly
useful for `redai.py` preset design: a parameter that sensitivity analysis shows barely moves Red's
behavior is either redundant or mis-wired, and a parameter that moves Red's behavior a great deal
deserves the most documentation/calibration attention (per DOM-009's doctrine-translation rigor).

**Local vs. global sensitivity.** Local sensitivity analysis varies a parameter near its current,
nominal value (small perturbations); global sensitivity analysis sweeps its entire plausible range —
local sensitivity is cheaper but can miss a parameter whose effect is non-linear or only matters at
an extreme value; a Red-preset aggressiveness dial should generally be checked globally (across its
full 0-1 or equivalent range) since a vignette author might plausibly set it anywhere in that range.

**Sensitivity to manipulation, as DOM-005 §5 names it: does gaming an input inflate a score without
improving the real underlying construct.** This is sensitivity analysis applied to an assessment
instrument's gameable inputs specifically — e.g., does an operator who deliberately delays issuing
orders just to inflate a "deliberation time" sub-score actually improve, or does the score move while
the real construct (decision quality) stays flat or worsens; an instrument failing this check is
measuring the wrong thing under deliberate adversarial input, not just under honest noise.

## 3. Operational Context

Sensitivity analysis is standard practice in simulation-based decision analysis specifically because
complex models frequently have a small number of parameters that dominate the output and a larger
number that barely matter — without systematically checking, a modeler's intuition about which inputs
matter is frequently wrong, and an un-swept assessment instrument's gameable inputs are a documented,
recurring failure mode in real training-evaluation programs.

## 4. Implementation Guidance

- **Apply R407's Monte Carlo batch mechanism while sweeping one parameter at a time to perform
  sensitivity analysis on a `redai.py` preset's tunable parameters** — this identifies which
  parameters most need careful, doctrine-grounded calibration (DOM-009) vs. which are low-stakes.
- **Before trusting a new DOM-002 measurement dimension or future assessment-instrument item, run
  the sensitivity-to-manipulation check from DOM-005 §5**: construct a deliberately gaming-oriented
  play sequence and confirm the score doesn't inflate disproportionately to the actual underlying
  construct it claims to measure.
- **Prefer global sensitivity sweeps (full plausible parameter range) over local ones for any
  parameter a vignette author might plausibly set at an extreme value** — a doctrine preset's
  aggressiveness dial is exactly this kind of author-facing, full-range parameter.

## 5. Feature Mapping

DOM-005 §5 (instrument validation) and `redai.py` preset calibration work are the direct consumers.

## 6. Related Topics

R407 (Monte Carlo Methods, the batch mechanism this technique sweeps across), R404 (Measurement
Theory), R405 (Uncertainty Analysis, the complementary parameter-uncertainty concern).
