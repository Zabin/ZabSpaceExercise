# R413 — Data Analysis and Reporting

> **Document ID:** R413
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R403, R412
> **Referenced By:** —
> **Produces:** the vocabulary for turning collected exercise data (eventlog, AAR, DOM-002 dimensions, future survey instruments) into a defensible finding rather than a raw data dump
> **Feature Mapping:** AAR (`spacesim/session/aar.py`), any future cross-session analytics/reporting feature, DOM-002 (Assessment Framework)
> **Related Topics:** R403 (Statistics Foundations), R412 (Survey and Assessment Instrument
> Design — a frequent input to this topic's reporting), R405 (Uncertainty Analysis — uncertainty
> reporting as part of a defensible finding)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The AAR (`spacesim/session/aar.py`) already produces a record of what happened during an exercise.
This topic closes the gap between "data was recorded" and "a defensible finding was reported" —
the analysis and write-up discipline that prevents a future facilitator-debrief writeup or
cross-session analytics report from overstating what the underlying data actually supports.

## 2. Concepts

**A finding should state its evidentiary basis explicitly.** "Blue's custody discipline improved" is
a claim; "Blue's median custody-confidence score (DOM-002 dimension) rose from 0.41 to 0.68 across
sessions 3-7, N=5" is a finding with stated evidence — the difference matters because the first form
invites unchecked overclaiming and the second is falsifiable by anyone who can re-examine the same
data.

**Distinguishing description from inference, and inference from recommendation.** Three distinct
claim types should not be blurred together in a single sentence: "the data shows X" (description),
"X suggests Y is generally true" (inference, requiring R401/R402's controlled-comparison rigor to
support), and "therefore do Z" (a recommendation, requiring additional judgment about goals/tradeoffs
beyond what the data alone establishes) — a debrief report that moves from raw description straight
to a confident recommendation, skipping the inference step's required rigor, is doing more than its
evidence supports.

**Avoiding cherry-picking.** Selectively reporting only the sessions or dimensions that support a
preferred narrative, while omitting contrary data, is the most common form of reporting bias — a
defensible report states its full dataset's scope (which sessions, which dimensions) and reports
contrary or null findings alongside supportive ones, not just the latter.

**Visualizing data honestly.** A chart with a truncated y-axis, an inconsistent scale across compared
series, or a cherry-picked time window can misrepresent an honest underlying dataset — any future
analytics dashboard reporting DOM-002 trends across sessions should use consistent, non-misleading
axis scales and should show the full available data range rather than a flattering excerpt.

**Reporting uncertainty and limitations alongside the finding, not as a footnote.** Per R405's
uncertainty-reporting discipline and R401's confound-awareness, a defensible report states its
sample size, the comparison's control quality, and any known confounds in the same breath as its
headline finding, not buried in fine print.

## 3. Operational Context

The discipline of moving from raw data to a defensible, appropriately-qualified finding is
foundational to credible reporting in any applied research or program-evaluation context — military
operational assessment and training-program evaluation specifically have well-documented historical
failure modes (selective reporting of favorable metrics, inference overreach from small samples)
that this topic's discipline is the standard corrective for.

## 4. Implementation Guidance

- **Any future AAR-derived debrief writeup or cross-session report should state its evidentiary
  basis explicitly** (which sessions, which DOM-002 dimensions, what sample size) alongside any
  headline finding, per R403/R405.
- **Keep description, inference, and recommendation visibly distinct in any report** — a finding
  that moves to a recommendation should explicitly flag the additional judgment involved, not present
  the recommendation as if the data alone compelled it.
- **Report the full scope of examined data, including null or contrary results**, in any future
  cross-session analytics feature or written debrief — per the cherry-picking concern, a report that
  shows only favorable sessions is not defensible regardless of how accurate each individual number
  is.
- **Any future analytics dashboard should use consistent, honest chart scales** and should default to
  showing the full available data range rather than a curated excerpt.

## 5. Feature Mapping

The AAR (`spacesim/session/aar.py`) and any future cross-session analytics/reporting feature are the
direct consumers.

## 6. Related Topics

R403 (Statistics Foundations), R412 (Survey and Assessment Instrument Design), R405 (Uncertainty
Analysis).
