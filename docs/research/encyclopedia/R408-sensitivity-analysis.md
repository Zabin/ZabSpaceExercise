# R408 — Sensitivity Analysis

> **Document ID:** R408
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R407](R407-monte-carlo-methods.md)
> **Referenced By:** [R404](R404-measurement-theory.md), [R405](R405-uncertainty-analysis.md)
> **Produces:** the technique DOM-005 §5 names for checking an assessment instrument's "sensitivity to manipulation"
> **Feature Mapping:** DOM-005 §5 (instrument validation), Red-preset and vignette-difficulty calibration
> **Related Topics:** [R407](R407-monte-carlo-methods.md) (Monte Carlo Methods — the batch mechanism sensitivity analysis sweeps
> across), [R404](R404-measurement-theory.md) (Measurement Theory — the instrument-validation use of this technique), [R405](R405-uncertainty-analysis.md)
> (Uncertainty Analysis — parameter uncertainty, the complementary concern to sampling uncertainty)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier B sensitivity-analysis textbook + foundational validity-theory paper — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-005 §5 lists "sensitivity to manipulation" as one of three checks for validating a future
assessment instrument, citing this topic by ID. This document supplies the general sensitivity-
analysis technique that check is a specific application of: systematically varying one input to see
how much it moves an output, used both to find an instrument's gameable inputs and, more broadly, to
find which of a model's parameters actually matter.

## 2. Scope

Covers: the general sensitivity-analysis technique (local vs. global, one-at-a-time), and its
specific application to an assessment instrument's gameable inputs (DOM-005 §5's "sensitivity to
manipulation" check). Does **not** cover: the Monte Carlo batch mechanism this technique typically
sweeps across ([R407](R407-monte-carlo-methods.md), assumed established here), or the broader
reliability/validity vocabulary this check is one instance of
([R404](R404-measurement-theory.md)'s job).

## 3. Concepts

**Sensitivity analysis: vary one input, hold others fixed, observe the output's response.** This is
the controlled-comparison method ([R401](R401-experimental-design-and-controls.md)) applied specifically to a model's input parameters rather
than to an experimental treatment — sweeping a single doctrine-preset parameter (e.g. an
aggressiveness dial) across its range while holding the vignette and seed fixed shows how much that
one parameter actually drives the outcome.

**Identifying which parameters matter and which don't.** A model with many parameters often has only
a few that meaningfully drive the output — sensitivity analysis surfaces this, which is directly
useful for `redai.py` preset design: a parameter that sensitivity analysis shows barely moves Red's
behavior is either redundant or mis-wired, and a parameter that moves Red's behavior a great deal
deserves the most documentation/calibration attention (per DOM-009's doctrine-translation rigor).

**Local/one-at-a-time (OAT) vs. global sensitivity analysis.** Andrea Saltelli et al.'s standard
reference text,
[*Global Sensitivity Analysis: The Primer*](https://www.researchgate.net/publication/23961124_Global_Sensitivity_Analysis_The_Primer_by_Andrea_Saltelli_Marco_Ratto_Terry_Andres_Francesca_Campolongo_Jessica_Cariboni_Debora_Gatelli_Michaela_Saisana_Stefano_Tarantola)
(Wiley, 2008), formalizes this distinction and its consequences: **local/OAT** sensitivity analysis
varies one parameter near its current nominal value while holding others fixed — computationally
cheap, but Saltelli et al. show it explores only a "hypercross" through parameter space and can
produce misleading rankings when parameters interact or the output responds non-linearly; **global**
sensitivity analysis instead sweeps the full plausible range (and, in Saltelli et al.'s variance-based
methods, considers parameter *combinations*), giving robust rankings in the presence of non-linearity
and interaction effects that OAT methods miss. A Red-preset aggressiveness dial should generally be
checked globally (across its full 0-1 or equivalent range, and ideally jointly with other tunable
parameters) since a vignette author might plausibly set it anywhere in that range and its effect
could interact with another preset parameter.

**Sensitivity to manipulation, as DOM-005 §5 names it: does gaming an input inflate a score without
improving the real underlying construct.** This is sensitivity analysis applied to an assessment
instrument's gameable inputs specifically, and maps directly onto Samuel Messick's foundational
validity-theory concept of **construct-irrelevant variance** — one of his two named threats to
validity (alongside construct underrepresentation): systematic score variance driven by something
other than the construct the instrument claims to measure
([Messick, *Validity of Psychological Assessment*, American Psychologist 50, 1995](https://people.bath.ac.uk/edspd/Weblinks/MA_Ass/Resources/Quality%20issues/Messick%201995%20AP.pdf)).
Does an operator who deliberately delays issuing orders just to inflate a "deliberation time"
sub-score actually improve, or does the score move while the real construct (decision quality) stays
flat or worsens — an instrument failing this check is exhibiting construct-irrelevant variance under
deliberate adversarial input, not just under honest noise, which is a more severe failure than
ordinary measurement error.

### Sources

- *Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J., Gatelli, D., Saisana, M. &
  Tarantola, S. (2008). Global Sensitivity Analysis: The Primer.* John Wiley & Sons —
  [live](https://www.researchgate.net/publication/23961124_Global_Sensitivity_Analysis_The_Primer_by_Andrea_Saltelli_Marco_Ratto_Terry_Andres_Francesca_Campolongo_Jessica_Cariboni_Debora_Gatelli_Michaela_Saisana_Stefano_Tarantola)
  · [snapshot](https://web.archive.org/web/2026*/https://www.researchgate.net/publication/23961124_Global_Sensitivity_Analysis_The_Primer_by_Andrea_Saltelli_Marco_Ratto_Terry_Andres_Francesca_Campolongo_Jessica_Cariboni_Debora_Gatelli_Michaela_Saisana_Stefano_Tarantola)
  · accessed 2026-07-02.
- *Messick, S. (1995). Validity of Psychological Assessment: Validation of Inferences from Persons'
  Responses and Performances as Scientific Inquiry into Score Meaning. American Psychologist, 50(9),
  741-749.* — [live](https://people.bath.ac.uk/edspd/Weblinks/MA_Ass/Resources/Quality%20issues/Messick%201995%20AP.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://people.bath.ac.uk/edspd/Weblinks/MA_Ass/Resources/Quality%20issues/Messick%201995%20AP.pdf)
  · accessed 2026-07-02.

## 4. Operational Context

Sensitivity analysis is standard practice in simulation-based decision analysis specifically because
complex models frequently have a small number of parameters that dominate the output and a larger
number that barely matter — Saltelli et al.'s Primer exists specifically because OAT intuition about
which inputs matter is frequently wrong without systematic global checking. Messick's
construct-irrelevant-variance concept is likewise foundational, not a niche concern: an
un-swept assessment instrument's gameable inputs are a documented, recurring failure mode in real
training-evaluation programs, which is exactly what his validity framework names as a first-class
threat rather than a minor implementation detail.

### Sources

Uses the same sources cited inline in §3 (Saltelli et al. 2008; Messick 1995); no additional sources
introduced in this section.

## 5. Implementation Guidance

- **Apply [R407](R407-monte-carlo-methods.md)'s Monte Carlo batch mechanism while sweeping one parameter at a time to perform
  sensitivity analysis on a `redai.py` preset's tunable parameters** — this identifies which
  parameters most need careful, doctrine-grounded calibration (DOM-009) vs. which are low-stakes.
- **Before trusting a new DOM-002 measurement dimension or future assessment-instrument item, run
  the sensitivity-to-manipulation check from DOM-005 §5**: construct a deliberately gaming-oriented
  play sequence and confirm the score doesn't inflate disproportionately to the actual underlying
  construct it claims to measure — per Messick's framework, treat any such inflation as
  construct-irrelevant variance, a first-class validity failure, not a minor edge case.
- **Prefer global sensitivity sweeps (full plausible parameter range, and joint sweeps where two
  parameters might interact) over local/OAT ones** for any parameter a vignette author might plausibly
  set at an extreme value or that might interact with another parameter — per Saltelli et al., a
  doctrine preset's aggressiveness dial is exactly this kind of author-facing, full-range parameter,
  and an OAT-only sweep risks missing an interaction with another preset parameter.

## 6. Feature Mapping

DOM-005 §5 (instrument validation) and `redai.py` preset calibration work are the direct consumers.

## 7. Related Topics

[R407](R407-monte-carlo-methods.md) (Monte Carlo Methods, the batch mechanism this technique sweeps across), [R404](R404-measurement-theory.md) (Measurement
Theory), [R405](R405-uncertainty-analysis.md) (Uncertainty Analysis, the complementary parameter-uncertainty concern).
