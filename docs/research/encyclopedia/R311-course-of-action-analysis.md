# R311 — Course of Action Analysis

> **Document ID:** R311
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R305
> **Referenced By:** —
> **Produces:** the doctrinal framing for a candidate future COA-comparison feature, applying R212's MCDA vocabulary
> **Feature Mapping:** candidate future COA-comparison feature under FS-101 (Mission Planning)
> **Related Topics:** R305 (Mission Analysis — the step that precedes COA development), R212
> (Multi-Criteria Decision Analysis — the formal method this topic's military application uses), R202
> (Decision Theory)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Today an operator compares options for accomplishing a mission-analysis-derived task (R305)
informally, in their head, with no engine support beyond `dry_run()`'s single-option preview. This
topic gives the doctrinal vocabulary for the military-specific COA development/comparison/selection
process, the direct precursor to any future feature that would let an operator formally compare
multiple candidate plans before commitment.

## 2. Concepts

**COA development: generate genuinely distinct options, not variations on one idea.** Doctrine
emphasizes developing COAs that differ in a meaningful way (different approach, different
risk/resource trade-off, different timing) rather than minor parameter tweaks of a single underlying
plan — relevant to a future feature: if a COA-comparison tool only ever compares "engage now" vs.
"engage in 10 minutes," it isn't really comparing courses of action in the doctrinal sense, just
timing variants of one.

**COA comparison via a decision matrix against named criteria.** The standard military staff method
scores each COA against an explicit, agreed-upon criteria set (this is R212's MCDA applied with a
specific military process and specific typical criteria: resource cost, time, risk to force, risk to
mission, flexibility) — directly buildable on R212's general method, with the criteria set itself
being the military-specific content this topic adds.

**COA wargaming as the validation step before selection.** Before selecting a COA, doctrine calls for
wargaming each candidate against likely adversary reactions (a mini-application of R307/R308's
methods at the planning-table level, distinct from running the actual exercise) — in this simulator's
terms, `dry_run()`'s "see before you commit" preview (R103/R120) is a partial, single-COA instance of
this; a true COA-wargaming feature would need to preview multiple candidate plans against a modeled
(not just current-state) Red response, which does not exist today.

**Decision criteria and the commander's final selection.** After matrix scoring, doctrine still
reserves the final choice for human judgment, not the matrix's numeric output — directly consistent
with DOM-008 §4's advisor-only constraint: a future COA-comparison feature should present the scored
matrix, never auto-select a "winning" COA on the operator's behalf.

## 3. Operational Context

The COA development/comparison/selection sequence is a core, formally taught step of military
decision-making processes (MDMP/JOPP) specifically because the discipline of generating genuinely
distinct options and comparing them against named criteria, before committing, measurably improves
plan quality relative to acting on the first workable idea (R211's satisficing, useful under genuine
time pressure, but doctrine explicitly reserves COA analysis for decisions important enough to
warrant the extra deliberation time).

## 4. Implementation Guidance

- **A future COA-comparison feature should require/encourage genuinely distinct candidate options**,
  not present minor parameter variations as if they were doctrinally distinct COAs — a UI nudge (e.g.
  requiring the operator to name what's different about each candidate) would operationalize this.
- **Build the comparison matrix on R212's general MCDA method, with this topic's standard criteria set
  (resource cost, time, risk to force, risk to mission, flexibility) as the default, operator-
  adjustable starting point** — not a fixed, hidden weighting (R212 §4's guidance applies directly).
- **Any COA-wargaming preview must reuse the existing `dry_run()` read-only-preview pattern and
  Red-doctrine-preset machinery (`redai.py`) for modeling likely Red response, rather than inventing a
  separate prediction model** — per MSTR-002 §4's seam principle, extend existing interfaces rather
  than parallel-build a new one.
- **The feature must never auto-select a COA** — per DOM-008 §4 and §2 above, present the scored
  matrix and require an explicit operator choice.

## 5. Feature Mapping

A candidate future COA-comparison feature under FS-101 (Mission Planning) is the direct consumer.

## 6. Related Topics

R305 (Mission Analysis, the precursor step), R212 (Multi-Criteria Decision Analysis, the formal
method), R202 (Decision Theory), R307/R308 (the wargaming-validation step's broader methodology).
