# R411 — Human Subjects Research

> **Document ID:** R411
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R401](R401-experimental-design-and-controls.md)
> **Referenced By:** —
> **Produces:** the ethics/consent vocabulary applying to any future collection of trainee performance data beyond a single session
> **Feature Mapping:** any future analytics feature persisting per-trainee data across sessions, DOM-002 (Assessment Framework) if extended to longitudinal trainee tracking
> **Related Topics:** [R401](R401-experimental-design-and-controls.md) (Experimental Design and Controls), [R413](R413-data-analysis-and-reporting.md) (Data Analysis and Reporting),
> DOM-002 (Assessment Framework — currently single-session scoped, not yet a longitudinal
> trainee-tracking system)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A U.S. federal human-subjects ethics sources — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-002's six measurement dimensions currently apply within a single exercise session. If any future
feature extends this to persisted, cross-session, per-trainee performance tracking (e.g. for a
training-program competency record), it crosses into human-subjects-research ethical territory this
topic names — the consent, privacy, and institutional-oversight considerations that apply once data
about identifiable individuals' performance is collected and retained, not just computed transiently
during a session.

## 2. Scope

Covers: when human-subjects-research ethics apply (persisted, identifiable data vs. transient
in-session computation), informed consent, privacy/data minimization, and the training-record-keeping
vs. research distinction, per the Belmont Report and Common Rule framework. Does **not** cover: the
experimental-design controls a formal human-subjects study would need
([R401](R401-experimental-design-and-controls.md)'s job, assumed established here), or the data-
analysis/reporting practices applied once data is collected ([R413](R413-data-analysis-and-reporting.md)'s
job) — this topic is specifically about the ethical/consent gate that precedes both.

## 3. Concepts

**Human subjects research ethics apply once data about identifiable individuals is collected and
retained, not just computed transiently.** The foundational U.S. framework,
[*The Belmont Report: Ethical Principles and Guidelines for the Protection of Human Subjects of
Research*](https://www.hhs.gov/ohrp/sites/default/files/the-belmont-report-508c_FINAL.pdf) (National
Commission for the Protection of Human Subjects of Biomedical and Behavioral Research, 1979), states
three governing principles — **Respect for Persons** (autonomy and informed consent), **Beneficence**
(maximizing benefit, minimizing harm), and **Justice** (fair distribution of research burdens and
benefits) — that the current U.S. regulatory system, the
[Common Rule (45 CFR 46)](https://www.hhs.gov/ohrp/regulations-and-policy/regulations/common-rule/index.html),
implements as binding regulation for federally funded and many institutional research programs. A
live in-session DOM-002 score, computed and displayed to the trainee and facilitator during the
exercise and then discarded, is meaningfully different from the same score persisted, attributed to a
named trainee, and retained for later review or comparison across sessions — the latter is the point
at which IRB-adjacent (Institutional Review Board) considerations become applicable, even in a PME
training context rather than a formal research study.

**Informed consent.** The Belmont Report's Respect for Persons principle, operationalized by the
Common Rule's informed-consent requirements, holds that a research subject should know, before
participating, what data will be collected, how it will be used, who can see it, and how long it is
retained — applied here, a trainee should have the equivalent visibility, especially relevant if
exercise data is ever used for purposes beyond the immediate training session (e.g. aggregated into a
unit-level report, or used in a future research publication about PME effectiveness).

**Privacy and data minimization.** Collecting and retaining only the data actually needed for the
stated purpose, and de-identifying or aggregating it where individual-level detail isn't required —
a feature that persists per-trainee DOM-002 scores should default to the minimum retention/
identification level the stated use case actually requires, not retain maximal detail "in case it's
useful later." This follows from the Belmont Report's Beneficence principle: unnecessary retention of
identifiable performance data is an unminimized risk with no corresponding benefit.

**The distinction between training-record-keeping and research.** A facilitator reviewing a
trainee's AAR for in-program coaching purposes is ordinary training administration; using the same
data, with identifiable trainees, to draw and publish generalizable conclusions about training
effectiveness is human-subjects research in the Common Rule's formal sense and may trigger
institutional review requirements that don't apply to ordinary record-keeping — the Common Rule's own
scope language (45 CFR 46 Subpart A) is what draws this line at the federal regulatory level.

### Sources

- *National Commission for the Protection of Human Subjects of Biomedical and Behavioral Research
  (1979). The Belmont Report: Ethical Principles and Guidelines for the Protection of Human Subjects
  of Research.* U.S. Department of Health and Human Services —
  [live](https://www.hhs.gov/ohrp/sites/default/files/the-belmont-report-508c_FINAL.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.hhs.gov/ohrp/sites/default/files/the-belmont-report-508c_FINAL.pdf)
  · accessed 2026-07-02.
- *U.S. Department of Health and Human Services. Federal Policy for the Protection of Human Subjects
  ("Common Rule"), 45 CFR 46.* —
  [live](https://www.hhs.gov/ohrp/regulations-and-policy/regulations/common-rule/index.html)
  · [snapshot](https://web.archive.org/web/2026*/https://www.hhs.gov/ohrp/regulations-and-policy/regulations/common-rule/index.html)
  · accessed 2026-07-02.

## 4. Operational Context

Human-subjects-research ethics (consent, privacy, IRB review) are a formal, often legally mandated
discipline in any context — military, academic, or corporate — where data about identifiable
individuals is collected for purposes beyond their own immediate, transient benefit; the Common
Rule's binding force on federally funded research (including much military and defense-academic PME
research) means this is not a hypothetical concern for a training program that later seeks to publish
or formally study its own effectiveness. PME training programs that move from purely in-session
feedback toward persisted, comparative trainee records have historically been a context where this
line is crossed inadvertently, without anyone explicitly deciding to conduct "research."

### Sources

Uses the same sources cited inline in §3 (Belmont Report 1979; Common Rule/45 CFR 46); no additional
sources introduced in this section.

## 5. Implementation Guidance

- **Any future feature that persists per-trainee performance data across sessions (rather than
  computing it transiently within one session) should be evaluated against this topic's consent and
  data-minimization principles before being built**, not after data collection has already begun.
- **If exercise data is ever proposed for use beyond the immediate training session** (a published
  effectiveness study, an aggregated cross-unit report), **flag explicitly that this crosses into
  human-subjects-research territory** per the Common Rule's scope and may require informed consent
  and/or institutional review, distinct from ordinary in-program training record-keeping.
- **Default any new persisted-data feature to the minimum identification/retention level the stated
  use case requires** — per the Belmont Report's Beneficence principle, prefer aggregated or
  de-identified data over individually-attributed retained records unless the specific use case
  requires the latter.

## 6. Feature Mapping

Any future analytics feature persisting per-trainee data across sessions is the direct consumer;
currently no such feature exists (DOM-002 is single-session scoped), making this topic forward-
looking guidance rather than a description of an existing gap.

## 7. Related Topics

[R401](R401-experimental-design-and-controls.md) (Experimental Design and Controls), [R413](R413-data-analysis-and-reporting.md) (Data Analysis and Reporting), DOM-002 (Assessment
Framework).
