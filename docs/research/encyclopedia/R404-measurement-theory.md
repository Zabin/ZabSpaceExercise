# R404 — Measurement Theory

> **Document ID:** R404
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R403](R403-statistics-foundations.md)
> **Referenced By:** [R412](R412-survey-and-assessment-instrument-design.md)
> **Produces:** the reliability/validity vocabulary DOM-002's measurement dimensions and any future rubric instrument must satisfy
> **Feature Mapping:** DOM-002 (Assessment Framework), DOM-005 (Validation Framework §5's instrument-validation checks)
> **Related Topics:** [R403](R403-statistics-foundations.md) (Statistics Foundations), [R410](R410-validation.md) (Validation — the broader validation
> concept this topic's instrument-specific case feeds), [R412](R412-survey-and-assessment-instrument-design.md) (Survey and Assessment Instrument
> Design — the direct consumer)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A foundational psychometrics sources — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-002 proposes six measurement dimensions (custody quality, window discipline, resource economy,
escalation discipline, belief-truth divergence, time-to-decision) and DOM-005 §5 lists three checks
for validating an assessment instrument (face validity, internal consistency, sensitivity to
manipulation, citing [R408](R408-sensitivity-analysis.md)). This topic supplies the measurement-theory vocabulary underlying both:
what it means for a measurement to be reliable and valid, and the standard scale types a metric can
take.

## 2. Scope

Covers: the four scale types (nominal/ordinal/interval/ratio) and the reliability/validity/internal-
consistency vocabulary, applied specifically to DOM-002's six dimensions and any future rubric
instrument. Does **not** cover: the descriptive/inferential statistics used once a measurement is
taken ([R403](R403-statistics-foundations.md), assumed established here), the broader
verification-vs-validation distinction for a whole model or simulator claim
([R410](R410-validation.md)'s job — this topic is the narrower instrument-level case), or the
concrete survey/rubric-authoring process that applies this vocabulary
([R412](R412-survey-and-assessment-instrument-design.md)'s job).

## 3. Concepts

**Scales of measurement: nominal, ordinal, interval, ratio.** S.S. Stevens's foundational 1946 paper,
[*On the Theory of Scales of Measurement*](https://www.science.org/doi/10.1126/science.103.2684.677)
(Science 103), defined this four-level taxonomy — determined by which transformations of the
numbers leave the underlying empirical relationships unchanged — that remains the standard framework
in social-science measurement. A nominal scale only names categories (effect category:
deceive/disrupt/deny/degrade/destroy — no inherent order); an ordinal scale ranks
without equal intervals (a 1-5 rubric score where the gap between 3 and 4 isn't necessarily equal to
the gap between 4 and 5); an interval scale has equal intervals but no true zero; a ratio scale has
both (resource economy expressed as a literal Δv/SoC quantity is ratio-scaled, supporting all
arithmetic operations per Stevens) — DOM-002's six dimensions mix scale types, and averaging across
mismatched scales (e.g. treating an ordinal rubric score and a ratio resource-cost number as
interchangeably "numeric") is a measurement-theory error Stevens's framework exists specifically to
catch.

**Reliability: does the measurement give consistent results.** A reliable measure produces the same
score for the same underlying performance across repeated administrations or raters — for an
automated DOM-002 dimension (e.g. window discipline, computable directly from the eventlog) this is
close to guaranteed by the engine's determinism; for a facilitator-judged dimension, reliability
requires inter-rater consistency, which an undocumented, ad hoc rubric does not guarantee.

**Validity: does the measurement actually measure the construct it claims to.** A measure can be
perfectly reliable (consistent) while still being invalid (consistently measuring the wrong thing) —
DOM-005 §5's "face validity" check (does the metric look, on inspection, like it measures the claimed
construct) is the most basic validity check; [R408](R408-sensitivity-analysis.md)'s sensitivity-to-manipulation check (does an
operator who deliberately games the metric without actually performing better score higher) is a
stronger one.

**Internal consistency for multi-item instruments.** Where a single construct (e.g. "escalation
discipline") is measured by combining multiple sub-items, those sub-items should correlate with each
other if they're genuinely measuring the same underlying construct. Lee Cronbach's 1951 paper,
[*Coefficient Alpha and the Internal Structure of Tests*](https://www.psychometricsociety.org/sites/main/files/file-attachments/cronbach_citation_classic_alpha.pdf?1582948431=)
(Psychometrika 16), introduced **Cronbach's alpha**, the standard internal-consistency reliability
coefficient still in near-universal use — low inter-item correlation (low alpha) suggests the
instrument is measuring multiple different things under one label, undermining DOM-002 §5's
rubric-not-single-score principle's implicit assumption that each named dimension is coherent.

### Sources

- *Stevens, S.S. (1946). On the Theory of Scales of Measurement. Science, 103(2684), 677-680.* —
  [live (DOI)](https://www.science.org/doi/10.1126/science.103.2684.677)
  · [snapshot](https://web.archive.org/web/2026*/https://www.science.org/doi/10.1126/science.103.2684.677)
  · accessed 2026-07-02.
- *Cronbach, L.J. (1951). Coefficient Alpha and the Internal Structure of Tests. Psychometrika,
  16(3), 297-334.* —
  [live (Psychometric Society reprint)](https://www.psychometricsociety.org/sites/main/files/file-attachments/cronbach_citation_classic_alpha.pdf?1582948431=)
  · [snapshot](https://web.archive.org/web/2026*/https://www.psychometricsociety.org/sites/main/files/file-attachments/cronbach_citation_classic_alpha.pdf?1582948431=)
  · accessed 2026-07-02.

## 4. Operational Context

Reliability and validity are the foundational quality criteria for any measurement instrument in
psychometrics and educational/training assessment specifically — Stevens's scale taxonomy and
Cronbach's alpha are both still the standard vocabulary and standard reliability statistic,
respectively, in current psychometric practice, three-quarters of a century after their original
publication. A training-assessment instrument that is reliable but not valid (consistently measures
the wrong thing) is a well-documented and common failure mode in real military and corporate
training-evaluation programs, which is exactly the failure DOM-005 §5's instrument-validation checks
are designed to catch before a metric is trusted.

### Sources

Uses the same sources cited inline in §3 (Stevens 1946; Cronbach 1951); no additional sources
introduced in this section.

## 5. Implementation Guidance

- **Any future automated DOM-002 dimension should state its scale type explicitly** (nominal,
  ordinal, interval, ratio, per Stevens's taxonomy) — this determines what operations (averaging,
  ranking, summing across sessions) are statistically defensible on it; treating an ordinal rubric
  score as ratio-scaled by averaging it is a common, avoidable error.
- **Before trusting any new facilitator-judged rubric item, check its reliability** by having two
  facilitators independently score the same recorded session and comparing — low agreement means the
  item's wording is ambiguous and needs revision before it's trusted as a measurement.
- **For any future multi-item DOM-002 sub-instrument, compute Cronbach's alpha across its items**
  before treating the combined score as measuring one coherent construct — an alpha below the
  conventional 0.70 threshold signals the items may be measuring different things.
- **Apply DOM-005 §5's three validity checks (face validity, internal consistency, sensitivity to
  manipulation) to any new instrument before it ships**, not after — per [R408](R408-sensitivity-analysis.md), an instrument that a
  gaming operator can inflate without actually improving the underlying construct has failed the
  sensitivity-to-manipulation check regardless of how good it looks on inspection.

## 6. Feature Mapping

DOM-002 (Assessment Framework) and DOM-005 §5 (instrument-validation checks) are the direct
consumers.

## 7. Related Topics

[R403](R403-statistics-foundations.md) (Statistics Foundations), [R410](R410-validation.md) (Validation, the broader concept), [R412](R412-survey-and-assessment-instrument-design.md) (Survey and Assessment
Instrument Design, the direct downstream consumer of this topic's reliability/validity vocabulary).
