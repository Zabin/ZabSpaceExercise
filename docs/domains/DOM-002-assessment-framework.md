# DOM-002 — Assessment Framework

> **Document ID:** DOM-002
> **Version:** 1.0
> **Status:** ⛔ Planned (framework specified; FS-201/FS-301 and their design-only IMP-201A/IMP-301A
> packages exist, but no code implements assessment in the simulator today)
> **Dependencies:** MSTR-001, MSTR-003, DOM-001
> **Referenced By:** DOM-005, DOM-007, FS-201, FS-301, FS-107
> **Produces:** FS-201 Competency Assessment, FS-202 (candidate) Rubric Authoring, FS-301 Research Analytics
> **Feature Mapping:** FS-201, FS-301
> **Related Topics:** R206 (bounded rationality), R207 (cognitive bias), R401-R413 (research methods), DOM-005 (Validation)

[↑ Docs index](../INDEX.md)

## 1. Purpose

Defines how learning is *measured*, as distinct from how it is *delivered* (DOM-001). Today
SpaceSim has no assessment instrumentation beyond binary objective-flip success/failure; this
framework specifies what a credible competency-assessment capability needs to look like before it
is built, so FS-201 inherits a coherent design rather than an ad-hoc scoring hack.

## 2. Scope

In scope: what to measure, how to score it, how to report it to a facilitator/evaluator. Out of
scope: the statistical validity of any specific instrument (DOM-005, Validation Framework, owns
that) and the pedagogical *design* of what's being assessed (DOM-001 owns objective classes).

## 3. Why binary objective-flip is insufficient

The current engine surfaces objective completion as a boolean per cell per vignette. This answers
"did the cell win" but not "did the cell demonstrate the competency the vignette was designed to
exercise" (MSTR-003 §8). A cell can flip an objective through luck, through an exploit of an
unintended engine gap, or through brute-force trial without ever forming a correct custody-based
belief — and conversely can demonstrate excellent tradecraft and still lose to a harder-than-typical
Red posture. Assessment needs a richer signal than the win/loss bit.

## 4. Proposed measurement dimensions

| Dimension | What it captures | Candidate data source |
|---|---|---|
| **Custody quality** | Was an engagement/observation backed by a genuinely weapons-quality track, or attempted speculatively? | `Track` confidence history at time of action vs. at decision |
| **Window discipline** | Were orders planned against real access windows, or did the cell repeatedly attempt invalid actions (denied by the engine)? | `OrderSystem` rejection rate, `dry_run()` usage pattern |
| **Resource economy** | Δv/SoC/sensor-tasking efficiency relative to the vignette's resource budget. | `propulsion`, `BusState` SOH history, sensor contention logs |
| **Escalation discipline** | Were kinetic/irreversible options used proportionate to ROE and threat, with the confirm gate engaged deliberately rather than reflexively? | Order log filtered to kinetic/cyber/jam categories, ROE chip state at time of order |
| **Belief-truth divergence** | How far did the cell's belief state (custody picture) diverge from ground truth at key decision points, and did the cell act as if aware of that uncertainty? | AAR's god-view vs. belief-view diff at `snapshot_at()` |
| **Time-to-decision** | How much simulated/wall time elapsed between an access window opening and the cell acting on it — a proxy for OODA-loop tightness (R208). | Eventlog timestamps vs. window open/close times |

These six dimensions are designed to be derivable largely from data the engine already produces
(eventlog, custody history, order log) — see FS-201 §"Dependencies" for the exact engine surfaces a
scoring implementation would read.

## 5. Scoring model principle: rubric, not single score

A single composite "score" collapses dimensions that are not commensurable (window discipline and
escalation discipline are different *kinds* of competency) and invites gaming a denominator. The
framework specifies a **rubric model**: each dimension is reported on its own scale (often
qualitative tiers — e.g., "speculative / adequate / disciplined" for custody quality — rather than
a forced numeric average), and a facilitator-facing summary view presents the rubric, not a single
leaderboard number. Aggregation into a single score, if ever needed (e.g., for a research study
comparing cohorts), is a DOM-005/R400 statistical-methods question, not something baked into the
base instrument.

## 6. Self-assessment vs. facilitator assessment vs. automated assessment

Three assessment modes, not mutually exclusive:

- **Automated, in-engine** — the six dimensions in §4, computed from eventlog/state data, always
  available without facilitator effort. This is the FS-201 baseline.
- **Facilitator rubric** — a White Cell observer's qualitative judgment during/after the exercise,
  informed by but not limited to the automated dimensions (a facilitator may see something the data
  can't capture, e.g. effective verbal coordination in a cooperative session).
- **Self-assessment / debrief reflection** — the AAR is itself a self-assessment instrument when
  the cell walks its own decision points; this mode requires no new engine feature beyond AAR
  (FS-107), only facilitation guidance (DOM-003).

## 7. Reporting surface

A future "competency report" (FS-201 candidate scope) should be viewable: (a) per-cell per-exercise
(the immediate debrief artifact), and (b) longitudinally per-trainee across exercises in the
progression (DOM-001 §4), so an instructor can see whether a trainee's custody quality or
escalation discipline is actually improving across sessions — this is the link to DOM-005
(validating that the instrument actually tracks real skill growth, not noise).

## 8. What this framework expects from FS-201

FS-201 (Competency Assessment) must: enumerate which of the six §4 dimensions it implements in its
first iteration (it need not implement all six at once — explicitly state which are deferred and
why); specify the rubric tiers per dimension; specify where the report surfaces (UI panel,
exportable artifact, or both); and state explicitly that it adds *no new gameplay mechanic* — it is
a read-only analytics layer over existing engine state (consistent with MSTR-002 §5's replay-safety
principle; a scoring computation must not mutate `WorldState`).

## 9. Related topics

R206 (bounded rationality — informs what "good" decision-making looks like under realistic
constraints, not idealized optimality), R207 (cognitive bias — informs rubric design so common,
expected biases aren't mistaken for incompetence), R401-R413 (Research Methods — instrument
validity, the actual statistical machinery DOM-005 would apply), DOM-007 (Human Factors — ensuring
the rubric reporting UI itself doesn't introduce cognitive load that undermines the debrief).
