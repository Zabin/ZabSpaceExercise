# R412 — Survey and Assessment Instrument Design

> **Document ID:** R412
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R404, R410
> **Referenced By:** —
> **Produces:** the instrument-design vocabulary for any future facilitator-judged rubric or trainee self-assessment survey under DOM-002's three assessment modes
> **Feature Mapping:** DOM-002 §5 (facilitator and self-assessment modes specifically — the two of the three modes that depend on a designed instrument rather than pure automation)
> **Related Topics:** R404 (Measurement Theory — reliability/validity, the criteria this topic's
> instruments must satisfy), R410 (Validation — the three-check method this topic's instruments are
> validated against), DOM-002 (Assessment Framework — the three assessment modes this topic serves
> two of)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-002 §5 names three assessment modes: automated, facilitator, and self. The automated mode reads
directly from the eventlog/engine state; the facilitator and self-assessment modes require an
actual designed instrument — a rubric a facilitator fills out, or a survey a trainee completes — that
doesn't yet exist as a concrete artifact. This topic gives the implementer the instrument-design
vocabulary needed to build one that is reliable and valid (R404) rather than an ad hoc questionnaire.

## 2. Concepts

**Item writing: each question should measure one thing clearly.** A poorly written rubric item
("how well did Blue manage the engagement, generally?") conflates multiple constructs (custody
quality, escalation discipline, resource economy might all be implicated) into one ambiguous score —
good item writing isolates one DOM-002 dimension per item, consistent with R404's internal-
consistency concern.

**Response scale design.** A Likert-type ordinal scale (1-5, "strongly disagree" to "strongly
agree") is the standard format for a facilitator/self-assessment item; the number of scale points and
whether to include a neutral midpoint are deliberate design choices, not arbitrary — too few points
loses discriminating power, too many invites false precision (R405) the facilitator's judgment can't
actually support.

**Piloting and item revision.** A new instrument item should be piloted (tried on a small number of
real sessions) and checked against R404's reliability criterion (do two facilitators independently
scoring the same session agree) before being trusted as a measurement tool — an unpiloted item
deployed directly into production assessment risks discovering its ambiguity only after it has
already produced unreliable data.

**Avoiding leading or socially-desirable-biased wording.** A self-assessment item phrased as "did you
make sound, deliberate decisions throughout?" invites a socially desirable "yes" regardless of actual
performance — neutral, behaviorally specific wording ("how many times did you reverse a planned
order before its execution window?") is less prone to this bias and more checkable against the
automated-mode data the same dimension might also be measured by.

**Triangulating across assessment modes.** Where the same underlying construct (e.g. escalation
discipline) is assessed by more than one of DOM-002's three modes (automated + facilitator-judged),
comparing the two is itself a validity check (R410) on the facilitator instrument — a large,
persistent disagreement between the automated measure and the facilitator's rubric score on the same
sessions suggests one of the two is measuring something different than intended.

## 3. Operational Context

Survey and rubric instrument design is a mature subdiscipline of psychometrics and educational
measurement specifically because poorly designed instruments are the most common source of invalid
assessment data in training-evaluation programs — a well-intentioned but unpiloted rubric, deployed
directly into a live training program, is a well-documented recurring failure mode this topic's
piloting/reliability discipline exists to prevent.

## 4. Implementation Guidance

- **Any future facilitator rubric or trainee self-assessment survey should isolate one DOM-002
  dimension per item** rather than writing compound, ambiguous items — per R404's internal-
  consistency concern.
- **Pilot any new instrument item on a handful of real recorded sessions and check inter-rater
  reliability (R404) before deploying it into live assessment** — an unpiloted item should be marked
  as provisional, not yet trusted as measurement.
- **Where the same dimension is measurable by both the automated mode and a facilitator/self-
  assessment instrument, run the triangulation check periodically** — a persistent large disagreement
  is a validity red flag (R410) on the instrument, not necessarily on the automated measure.
- **Word self-assessment items behaviorally and specifically, avoiding socially-desirable-biased
  phrasing** — per the bias concern above.

## 5. Feature Mapping

DOM-002 §5's facilitator and self-assessment modes are the direct consumers; this topic describes a
not-yet-built artifact (the instrument itself), not an existing feature.

## 6. Related Topics

R404 (Measurement Theory), R410 (Validation), DOM-002 (Assessment Framework).
