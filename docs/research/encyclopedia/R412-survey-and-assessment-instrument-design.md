# R412 — Survey and Assessment Instrument Design

> **Document ID:** R412
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R404](R404-measurement-theory.md), [R410](R410-validation.md)
> **Referenced By:** —
> **Produces:** the instrument-design vocabulary for any future facilitator-judged rubric or trainee self-assessment survey under DOM-002's three assessment modes
> **Feature Mapping:** DOM-002 §5 (facilitator and self-assessment modes specifically — the two of the three modes that depend on a designed instrument rather than pure automation)
> **Related Topics:** [R404](R404-measurement-theory.md) (Measurement Theory — reliability/validity, the criteria this topic's
> instruments must satisfy), [R410](R410-validation.md) (Validation — the three-check method this topic's instruments are
> validated against), DOM-002 (Assessment Framework — the three assessment modes this topic serves
> two of)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A foundational psychometric-instrument sources — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-002 §5 names three assessment modes: automated, facilitator, and self. The automated mode reads
directly from the eventlog/engine state; the facilitator and self-assessment modes require an
actual designed instrument — a rubric a facilitator fills out, or a survey a trainee completes — that
doesn't yet exist as a concrete artifact. This topic gives the implementer the instrument-design
vocabulary needed to build one that is reliable and valid ([R404](R404-measurement-theory.md)) rather than an ad hoc questionnaire.

## 2. Scope

Covers: item writing, response-scale design, piloting/item revision, socially-desirable-bias
avoidance, and cross-mode triangulation, applied to DOM-002 §5's facilitator and self-assessment
instruments. Does **not** cover: the reliability/validity criteria an instrument must satisfy
(assumed established at [R404](R404-measurement-theory.md)) or the broader validation methodology
these instruments are checked against ([R410](R410-validation.md), also assumed established) — this
topic is the concrete authoring practice that produces an instrument those two topics can then be
applied to.

## 3. Concepts

**Item writing: each question should measure one thing clearly.** A poorly written rubric item
("how well did Blue manage the engagement, generally?") conflates multiple constructs (custody
quality, escalation discipline, resource economy might all be implicated) into one ambiguous score —
good item writing isolates one DOM-002 dimension per item, consistent with [R404](R404-measurement-theory.md)'s internal-
consistency concern.

**Response scale design.** Rensis Likert's foundational 1932 dissertation,
[*A Technique for the Measurement of Attitudes*](https://archive.org/details/likert-1932)
(Archives of Psychology, No. 140), introduced the summated ordinal rating scale (the "Likert scale")
still in near-universal use for attitude and self-report measurement — a 1-5 or similar ordinal scale
("strongly disagree" to "strongly agree") is the standard format for a facilitator/self-assessment
item; the number of scale points and whether to include a neutral midpoint are deliberate design
choices Likert's own methodology treats as consequential, not arbitrary — too few points loses
discriminating power, too many invites false precision ([R405](R405-uncertainty-analysis.md)) the
facilitator's judgment can't actually support.

**Piloting and item revision.** A new instrument item should be piloted (tried on a small number of
real sessions) and checked against [R404](R404-measurement-theory.md)'s reliability criterion (do two facilitators independently
scoring the same session agree) before being trusted as a measurement tool — an unpiloted item
deployed directly into production assessment risks discovering its ambiguity only after it has
already produced unreliable data.

**Avoiding leading or socially-desirable-biased wording.** Douglas Crowne and David Marlowe's 1960
[Marlowe-Crowne Social Desirability Scale](https://en.wikipedia.org/wiki/Marlowe%E2%80%93Crowne_Social_Desirability_Scale)
work established social desirability bias — the tendency of a respondent to answer in a
culturally-sanctioned way rather than an accurate one — as a measurable, named, and pervasive
confound in self-report instrument design, cited in thousands of subsequent studies. A self-assessment
item phrased as "did you make sound, deliberate decisions throughout?" invites a socially desirable
"yes" regardless of actual performance — neutral, behaviorally specific wording ("how many times did
you reverse a planned order before its execution window?") is less prone to this bias and more
checkable against the automated-mode data the same dimension might also be measured by.

**Triangulating across assessment modes.** Where the same underlying construct (e.g. escalation
discipline) is assessed by more than one of DOM-002's three modes (automated + facilitator-judged),
comparing the two is itself a validity check ([R410](R410-validation.md)) on the facilitator instrument — a large,
persistent disagreement between the automated measure and the facilitator's rubric score on the same
sessions suggests one of the two is measuring something different than intended.

### Sources

- *Likert, R. (1932). A Technique for the Measurement of Attitudes. Archives of Psychology, 22(140),
  1-55.* — [live (Internet Archive)](https://archive.org/details/likert-1932)
  · [snapshot](https://web.archive.org/web/2026*/https://archive.org/details/likert-1932)
  · accessed 2026-07-02.
- *Crowne, D.P. & Marlowe, D. (1960). A New Scale of Social Desirability Independent of
  Psychopathology.* Journal of Consulting Psychology, 24(4), 349-354; summarized at
  [Marlowe-Crowne Social Desirability Scale, Wikipedia](https://en.wikipedia.org/wiki/Marlowe%E2%80%93Crowne_Social_Desirability_Scale)
  (used here only as a navigational pointer to the primary 1960 paper, per methodology §2 Tier D
  usage rules — the substantive claim is attributed to the original Crowne & Marlowe paper, not to
  Wikipedia) · [snapshot](https://web.archive.org/web/2026*/https://en.wikipedia.org/wiki/Marlowe%E2%80%93Crowne_Social_Desirability_Scale)
  · accessed 2026-07-02.

## 4. Operational Context

Survey and rubric instrument design is a mature subdiscipline of psychometrics and educational
measurement specifically because poorly designed instruments are the most common source of invalid
assessment data in training-evaluation programs — Likert's scale-design methodology and the
Crowne-Marlowe social-desirability-bias finding are both nearly a century and over six decades old
respectively, and remain the standard vocabulary specifically because a well-intentioned but
unpiloted rubric, deployed directly into a live training program, is a well-documented recurring
failure mode this topic's piloting/reliability discipline exists to prevent.

### Sources

Uses the same sources cited inline in §3 (Likert 1932; Crowne & Marlowe 1960); no additional sources
introduced in this section.

## 5. Implementation Guidance

- **Any future facilitator rubric or trainee self-assessment survey should isolate one DOM-002
  dimension per item** rather than writing compound, ambiguous items — per [R404](R404-measurement-theory.md)'s internal-
  consistency concern.
- **Use a Likert-style ordinal scale with a deliberately chosen number of points** (per Likert's own
  methodology) — document the choice of point-count and midpoint-inclusion rather than picking
  arbitrarily.
- **Pilot any new instrument item on a handful of real recorded sessions and check inter-rater
  reliability ([R404](R404-measurement-theory.md)) before deploying it into live assessment** — an unpiloted item should be marked
  as provisional, not yet trusted as measurement.
- **Where the same dimension is measurable by both the automated mode and a facilitator/self-
  assessment instrument, run the triangulation check periodically** — a persistent large disagreement
  is a validity red flag ([R410](R410-validation.md)) on the instrument, not necessarily on the automated measure.
- **Word self-assessment items behaviorally and specifically, avoiding socially-desirable-biased
  phrasing** — per the Crowne-Marlowe finding above, a self-report item inviting a culturally
  sanctioned answer measures social desirability, not the intended construct.

## 6. Feature Mapping

DOM-002 §5's facilitator and self-assessment modes are the direct consumers; this topic describes a
not-yet-built artifact (the instrument itself), not an existing feature.

## 7. Related Topics

[R404](R404-measurement-theory.md) (Measurement Theory), [R410](R410-validation.md) (Validation), DOM-002 (Assessment Framework).
