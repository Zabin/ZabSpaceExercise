# R413 — Data Analysis and Reporting

> **Document ID:** R413
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R403](R403-statistics-foundations.md), [R412](R412-survey-and-assessment-instrument-design.md)
> **Referenced By:** —
> **Produces:** the vocabulary for turning collected exercise data (eventlog, AAR, DOM-002 dimensions, future survey instruments) into a defensible finding rather than a raw data dump
> **Feature Mapping:** AAR (`spacesim/session/aar.py`), any future cross-session analytics/reporting feature, DOM-002 (Assessment Framework)
> **Related Topics:** [R403](R403-statistics-foundations.md) (Statistics Foundations), [R412](R412-survey-and-assessment-instrument-design.md) (Survey and Assessment Instrument
> Design — a frequent input to this topic's reporting), [R405](R405-uncertainty-analysis.md) (Uncertainty Analysis — uncertainty
> reporting as part of a defensible finding)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A/B graphical-integrity + statistical-ethics sources — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The AAR (`spacesim/session/aar.py`) already produces a record of what happened during an exercise.
This topic closes the gap between "data was recorded" and "a defensible finding was reported" —
the analysis and write-up discipline that prevents a future facilitator-debrief writeup or
cross-session analytics report from overstating what the underlying data actually supports.

## 2. Scope

Covers: stating evidentiary basis, the description/inference/recommendation distinction,
cherry-picking avoidance, honest data visualization, and uncertainty reporting, as applied to a
future AAR-derived debrief or cross-session analytics report. Does **not** cover: the statistical
vocabulary a finding's evidentiary basis is stated in ([R403](R403-statistics-foundations.md),
assumed established), the instrument that produced a survey-derived input to this topic's reports
([R412](R412-survey-and-assessment-instrument-design.md)'s job), or the uncertainty-quantification
mechanics themselves ([R405](R405-uncertainty-analysis.md)'s job, referenced here only for its role
in a defensible report).

## 3. Concepts

**A finding should state its evidentiary basis explicitly.** "Blue's custody discipline improved" is
a claim; "Blue's median custody-confidence score (DOM-002 dimension) rose from 0.41 to 0.68 across
sessions 3-7, N=5" is a finding with stated evidence — the difference matters because the first form
invites unchecked overclaiming and the second is falsifiable by anyone who can re-examine the same
data.

**Distinguishing description from inference, and inference from recommendation.** Three distinct
claim types should not be blurred together in a single sentence: "the data shows X" (description),
"X suggests Y is generally true" (inference, requiring [R401](R401-experimental-design-and-controls.md)/[R402](R402-hypotheses-and-variables.md)'s controlled-comparison rigor to
support), and "therefore do Z" (a recommendation, requiring additional judgment about goals/tradeoffs
beyond what the data alone establishes) — a debrief report that moves from raw description straight
to a confident recommendation, skipping the inference step's required rigor, is doing more than its
evidence supports.

**Avoiding cherry-picking.** The American Statistical Association's
[*Ethical Guidelines for Statistical Practice*](https://www.amstat.org/docs/default-source/amstat-documents/EthicalGuidelines.pdf?v=0825)
names this directly: "cherry-picking promising findings, also known as data dredging, significance
chasing, or 'p-hacking,' leads to a spurious excess of statistically significant results ... and
should be vigorously avoided," and requires the ethical statistician to identify and mitigate any
preference that "might predetermine or influence the analyses/results." Selectively reporting only
the sessions or dimensions that support a preferred narrative, while omitting contrary data, is the
most common form of reporting bias — a defensible report states its full dataset's scope (which
sessions, which dimensions) and reports contrary or null findings alongside supportive ones, not just
the latter.

**Visualizing data honestly.** Edward Tufte's
[*The Visual Display of Quantitative Information*](https://infovis-wiki.net/wiki/Lie_Factor) (1983)
formalizes this as the **Lie Factor** — the size of the effect shown in a graphic divided by the
actual size of the effect in the underlying data — and states that an honest graphic should keep this
ratio between 0.95 and 1.05; Tufte specifically names truncated value axes and inconsistent scales
across compared series as common, avoidable sources of a high Lie Factor. Any future analytics
dashboard reporting DOM-002 trends across sessions should use consistent, non-misleading axis scales
and should show the full available data range rather than a flattering excerpt, per Tufte's standard.

**Reporting uncertainty and limitations alongside the finding, not as a footnote.** Per [R405](R405-uncertainty-analysis.md)'s
uncertainty-reporting discipline and [R401](R401-experimental-design-and-controls.md)'s confound-awareness, a defensible report states its
sample size, the comparison's control quality, and any known confounds in the same breath as its
headline finding, not buried in fine print — consistent with the ASA guidelines' broader requirement
to report "sufficient information to give readers a clear understanding of ... any limitations on its
validity."

### Sources

- *American Statistical Association (2022 revision). Ethical Guidelines for Statistical Practice.*
  Prepared by the Committee on Professional Ethics —
  [live](https://www.amstat.org/docs/default-source/amstat-documents/EthicalGuidelines.pdf?v=0825)
  · [snapshot](https://web.archive.org/web/2026*/https://www.amstat.org/docs/default-source/amstat-documents/EthicalGuidelines.pdf?v=0825)
  · accessed 2026-07-02.
- *Tufte, E.R. (1983). The Visual Display of Quantitative Information.* Graphics Press — Lie Factor
  concept summarized at [InfoVis:Wiki, "Lie Factor"](https://infovis-wiki.net/wiki/Lie_Factor) (used
  as a navigational pointer to Tufte's primary text per methodology §2 Tier D usage rules; the
  substantive claim is attributed to Tufte's original 1983 book, not to the wiki page) —
  [snapshot](https://web.archive.org/web/2026*/https://infovis-wiki.net/wiki/Lie_Factor)
  · accessed 2026-07-02.

## 4. Operational Context

The discipline of moving from raw data to a defensible, appropriately-qualified finding is
foundational to credible reporting in any applied research or program-evaluation context — the ASA's
formal ethical guidelines and Tufte's graphical-integrity standard both exist precisely because
military operational assessment and training-program evaluation specifically have well-documented
historical failure modes (selective reporting of favorable metrics, inference overreach from small
samples, misleading charts) that this topic's discipline is the standard corrective for.

### Sources

Uses the same sources cited inline in §3 (ASA Ethical Guidelines; Tufte 1983); no additional sources
introduced in this section.

## 5. Implementation Guidance

- **Any future AAR-derived debrief writeup or cross-session report should state its evidentiary
  basis explicitly** (which sessions, which DOM-002 dimensions, what sample size) alongside any
  headline finding, per [R403](R403-statistics-foundations.md)/[R405](R405-uncertainty-analysis.md).
- **Keep description, inference, and recommendation visibly distinct in any report** — a finding
  that moves to a recommendation should explicitly flag the additional judgment involved, not present
  the recommendation as if the data alone compelled it.
- **Report the full scope of examined data, including null or contrary results**, in any future
  cross-session analytics feature or written debrief — per the ASA guidelines' anti-cherry-picking
  requirement, a report that shows only favorable sessions is not defensible regardless of how
  accurate each individual number is.
- **Any future analytics dashboard should keep its Lie Factor near 1.0 (Tufte's standard)** — use
  consistent, honest chart scales and default to showing the full available data range rather than a
  curated excerpt; a truncated y-axis on a DOM-002 trend chart is exactly the kind of distortion
  Tufte's standard flags.

## 6. Feature Mapping

The AAR (`spacesim/session/aar.py`) and any future cross-session analytics/reporting feature are the
direct consumers.

## 7. Related Topics

[R403](R403-statistics-foundations.md) (Statistics Foundations), [R412](R412-survey-and-assessment-instrument-design.md) (Survey and Assessment Instrument Design), [R405](R405-uncertainty-analysis.md) (Uncertainty
Analysis).
