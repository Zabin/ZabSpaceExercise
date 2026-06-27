# R411 — Human Subjects Research

> **Document ID:** R411
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R401](R401-experimental-design-and-controls.md)
> **Referenced By:** —
> **Produces:** the ethics/consent vocabulary applying to any future collection of trainee performance data beyond a single session
> **Feature Mapping:** any future analytics feature persisting per-trainee data across sessions, DOM-002 (Assessment Framework) if extended to longitudinal trainee tracking
> **Related Topics:** [R401](R401-experimental-design-and-controls.md) (Experimental Design and Controls), [R413](R413-data-analysis-and-reporting.md) (Data Analysis and Reporting),
> DOM-002 (Assessment Framework — currently single-session scoped, not yet a longitudinal
> trainee-tracking system)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-002's six measurement dimensions currently apply within a single exercise session. If any future
feature extends this to persisted, cross-session, per-trainee performance tracking (e.g. for a
training-program competency record), it crosses into human-subjects-research ethical territory this
topic names — the consent, privacy, and institutional-oversight considerations that apply once data
about identifiable individuals' performance is collected and retained, not just computed transiently
during a session.

## 2. Concepts

**Human subjects research ethics apply once data about identifiable individuals is collected and
retained, not just computed transiently.** A live in-session DOM-002 score, computed and displayed to
the trainee and facilitator during the exercise and then discarded, is meaningfully different from
the same score persisted, attributed to a named trainee, and retained for later review or comparison
across sessions — the latter is the point at which IRB-adjacent (Institutional Review Board)
considerations become applicable, even in a PME training context rather than a formal research study.

**Informed consent.** A trainee should know, before participating, what performance data will be
collected, how it will be used, who can see it, and how long it is retained — this is especially
relevant if exercise data is ever used for purposes beyond the immediate training session (e.g.
aggregated into a unit-level report, or used in a future research publication about PME
effectiveness).

**Privacy and data minimization.** Collecting and retaining only the data actually needed for the
stated purpose, and de-identifying or aggregating it where individual-level detail isn't required —
a feature that persists per-trainee DOM-002 scores should default to the minimum retention/
identification level the stated use case actually requires, not retain maximal detail "in case it's
useful later."

**The distinction between training-record-keeping and research.** A facilitator reviewing a
trainee's AAR for in-program coaching purposes is ordinary training administration; using the same
data, with identifiable trainees, to draw and publish generalizable conclusions about training
effectiveness is human-subjects research in the formal sense and may trigger institutional review
requirements that don't apply to ordinary record-keeping.

## 3. Operational Context

Human-subjects-research ethics (consent, privacy, IRB review) are a formal, often legally mandated
discipline in any context — military, academic, or corporate — where data about identifiable
individuals is collected for purposes beyond their own immediate, transient benefit; PME training
programs that move from purely in-session feedback toward persisted, comparative trainee records
have historically been a context where this line is crossed inadvertently, without anyone explicitly
deciding to conduct "research."

## 4. Implementation Guidance

- **Any future feature that persists per-trainee performance data across sessions (rather than
  computing it transiently within one session) should be evaluated against this topic's consent and
  data-minimization principles before being built**, not after data collection has already begun.
- **If exercise data is ever proposed for use beyond the immediate training session** (a published
  effectiveness study, an aggregated cross-unit report), **flag explicitly that this crosses into
  human-subjects-research territory** and may require informed consent and/or institutional review,
  distinct from ordinary in-program training record-keeping.
- **Default any new persisted-data feature to the minimum identification/retention level the stated
  use case requires** — prefer aggregated or de-identified data over individually-attributed retained
  records unless the specific use case requires the latter.

## 5. Feature Mapping

Any future analytics feature persisting per-trainee data across sessions is the direct consumer;
currently no such feature exists (DOM-002 is single-session scoped), making this topic forward-
looking guidance rather than a description of an existing gap.

## 6. Related Topics

[R401](R401-experimental-design-and-controls.md) (Experimental Design and Controls), [R413](R413-data-analysis-and-reporting.md) (Data Analysis and Reporting), DOM-002 (Assessment
Framework).
