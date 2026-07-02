---
name: research-methods-and-validation
description: Produce, refresh, and — as the current primary job — remediate the R400-tier research-methods encyclopedia (experimental design, hypotheses/variables, statistics, measurement theory, uncertainty analysis, modeling practices, Monte Carlo, sensitivity analysis, verification, validation, human-subjects research, survey/instrument design, data analysis and reporting) that grounds assessment/validation work (DOM-002, DOM-005). Use when asked to research statistics/experiment-design/measurement/validation topics, to add/extend `docs/research/encyclopedia/R4xx-*` topics, to close the R400 sourcing/scope defect (GAP-13 — every topic is missing the mandatory §2 Scope section and carries zero citations), or to gather grounding facts before drafting an FS-xxx/IMP-xxx spec or assessment/validation feature that touches measurement, statistical claims, or model V&V. Not for novice statistics tutorials — those belong in `docs/training/`.
---

# Research: Research Methods & Validation

Produces the **R400-tier encyclopedia** (`docs/research/encyclopedia/R401`–`R413`) and grounds
[`docs/domains/DOM-002-assessment-framework.md`](../../../docs/domains/DOM-002-assessment-framework.md)
(how learning is measured) and
[`docs/domains/DOM-005-validation-framework.md`](../../../docs/domains/DOM-005-validation-framework.md)
(how a fidelity claim or an assessment instrument is shown to be sound). The governing rules are
[`docs/master/MSTR-007-research-philosophy.md`](../../../docs/master/MSTR-007-research-philosophy.md)
(purpose, tier shape, authoring cadence) and
[`docs/research/10-sources-and-methodology.md`](../../../docs/research/10-sources-and-methodology.md)
(citation format, source-quality tiers, review cadence). Read both before producing anything —
this skill does not restate them, it operationalizes them for this domain. Unlike the R100/R300
tiers, R400 is **not yet closed** — see "Current state" below before assuming this is steady-state
maintenance work.

## What this is for (and what it is not)

> "The purpose is domain understanding, not academic research… give a future coding LLM agent
> enough domain understanding to implement a feature correctly." — MSTR-007 §2

This skill answers "if an agent is about to design a validation study, build an assessment rubric,
run a Monte Carlo sweep, or make any statistical claim about the simulator, what does it need to
know to not get it wrong" — never "teach me what a p-value is" or "explain the scientific method."
Real methodological grounding (peer-reviewed methods texts, NIST/ISO measurement standards,
DoD/DOE V&V handbooks, published human-subjects/IRB guidance) is the bar; invented statistical
claims, uncited "textbook" assertions, or plausible-sounding numbers with no traceable source do
not meet it. If a request is actually introductory ("what is a p-value," "what does statistically
significant mean"), redirect to `docs/training/`; do not write that into the encyclopedia.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| [`R400-index.md`](../../../docs/research/encyclopedia/R400-index.md) + `R401`–`R413` | Experimental design/controls, hypotheses/variables, statistics foundations, measurement theory, uncertainty analysis, modeling practices, Monte Carlo methods, sensitivity analysis, verification, validation, human-subjects research, survey/instrument design, data analysis and reporting. |
| [`docs/domains/DOM-002-assessment-framework.md`](../../../docs/domains/DOM-002-assessment-framework.md) | What to measure (§4 measurement dimensions), how to score it (§5 rubric model), how to report it — the dependent-variable/instrument-design substrate this tier's statistics/measurement topics ground. |
| [`docs/domains/DOM-005-validation-framework.md`](../../../docs/domains/DOM-005-validation-framework.md) | The verification-vs-validation distinction (§3), the validation method for fidelity claims (§4) and for assessment instruments (§5), Monte Carlo as the validation workhorse (§6). |
| Engine grounding | `spacesim/engine/rng.py` (`SeededRng` — the Monte Carlo repeatability mechanism), `spacesim/tests/test_determinism.py` (the Phase-1 determinism property test — the verification precedent this tier's `R409` points to), `docs/AUDIT-2026-06-UI-TTC.md` §2 (the power-rate recalibration — this project's only worked validation example to date). |
| Feature Mapping targets | FS-201 (Competency Assessment), FS-301 (Research Analytics), any future feature-effectiveness study or Monte Carlo experimentation harness (`docs/FUTURE-WORK.md` §13 R8). |

## Current state (read this before choosing a workflow)

**Tier R400 is structurally drafted but not done.** All 13 topics exist with substantive §1
Purpose / Concepts / Operational Context / Implementation Guidance / Feature Mapping / Related
Topics content and plausible-looking frontmatter (several individual files even self-report
`Status: ✅ Done`) — but **every single topic is missing the mandatory §2 Scope section** (MSTR-007
§4.2) and **carries zero citations**: no inline sourcing at any claim site, no `### Sources`
subsections, no live-URL-plus-Wayback-snapshot pairs, per `docs/research/10-sources-and-
methodology.md`. This is tracked as **GAP-13** in
[`docs/FUTURE-WORK.md`](../../../docs/FUTURE-WORK.md) §13 (Recommendation R1), which says to close
R500 first (fewer, more speculative topics) and R400 second. Treat every individual file's
self-reported `✅ Done` as **stale and untrustworthy** — trust the tier index's `🚧 (no §2 Scope;
uncited)` marker and the quality gate below instead. Do not add new R4xx topics while this
remediation backlog is open unless a genuine coverage gap blocks other work — finish the 13 first.

## Workflow

### A. Remediation pass (the current priority — GAP-13)

1. **Sequencing confirmed.** `research-future-operations` (R500) closed its GAP-13 remediation
   2026-07-02 (all 9 topics ✅, see `R500-index.md`) — R400 is now the GAP-13 priority per
   `docs/FUTURE-WORK.md` §13 R1's sequencing.
2. **Pick the next unremediated topic** from [`R400-index.md`](../../../docs/research/encyclopedia/R400-index.md)
   (any topic still marked `🚧`), in ID order unless directed otherwise.
3. **Read the current file fully** before editing — the Purpose/Concepts/Operational
   Context/Implementation Guidance/Feature Mapping/Related Topics content is already substantive;
   the job is to add what's missing, not rewrite what's there, unless a claim turns out to be
   uncitable (see Gotchas).
4. **Insert a `## 2. Scope` section** immediately after Purpose, then renumber every following
   section so the file matches the mandatory seven-part shape exactly: 1 Purpose, 2 Scope,
   3 Concepts, 4 Operational Context, 5 Implementation Guidance, 6 Feature Mapping, 7 Related
   Topics. Scope states what this topic covers and, explicitly, what it defers to a neighboring
   R4xx topic or to DOM-002/DOM-005 (the boundary test from MSTR-007 §5) — e.g. R404 (Measurement
   Theory) should explicitly *not* re-derive the statistical tests that are R403's job.
5. **Research with tiered sources** (`10-sources-and-methodology.md` §2): prefer Tier A (primary —
   the actual standard, textbook, or peer-reviewed paper; this project's own `test_determinism.py`
   and `AUDIT-2026-06-UI-TTC.md` where the claim is about *this simulator's* practice) and Tier B
   (NIST/ISO measurement standards, DoD/DOE V&V handbooks, government human-subjects guidance) over
   blog-post or Wikipedia-only summaries of statistical methods.
6. **Add an inline citation at every substantive claim site** — a named statistical test, a named
   standard (e.g. ISO 5725, NIST measurement-uncertainty guidance), a named methodology (e.g.
   Sobol sensitivity indices, Latin hypercube sampling), a dated study or handbook edition. No
   end-of-section-only citation dumps (methodology §1.1).
7. **Add a `### Sources` subsection to every `##` section**: live URL + Wayback Machine snapshot +
   accessed date (methodology §1.2). A section with no external claims (e.g. one that only
   references this project's own code) can point its Sources subsection at the cited file:line
   instead of an external URL.
8. **Correct the frontmatter `Status` field** to `🚧` if it currently (falsely) reads `✅ Done`;
   flip it to `✅ Done` only once this topic individually passes the quality gate below.
9. **Update the row in `R400-index.md`** from `🚧 (no §2 Scope; uncited)` to `✅` once done, and
   cross-check `Dependencies`/`Referenced By` are still bidirectionally accurate after the edit.
10. **Once all 13 topics are `✅`**, rewrite `R400-index.md`'s tier-level status paragraph from
    "incomplete, not done" to the closed-tier framing R100/R300 use, and update this skill's
    "Current state" section accordingly (it will then read like a steady-state-maintenance skill).
11. **Verify, then commit** as `docs(research): R4xx — <what changed>`, consistent with this
    branch's existing commit style.

### B. Steady-state maintenance (once the tier is closed)

The same three activities the closed R100/R300 tiers use — do not bulk-author new topics by
default; add a new `R4xx` row (`⛔ Planned` first, index-before-content) only on a genuine gap
(a new DOM-002/DOM-005 mechanism, or a new validation technique the simulator adopts with no
grounding topic):

1. **Pre-spec grounding** — before an FS-201/FS-301/validation-study spec is drafted, verify the
   relevant `R4xx` topic(s) already cover what's needed; fill the gap first if not.
2. **Citation-rot maintenance** — re-verify live URLs, refresh Wayback snapshots/`accessed` dates
   per the methodology's review cadence.
3. **Depth/gap fill** — when a new assessment/validation feature reveals a topic under-specifies
   the implementation-relevant consequence, expand §4/§5 rather than letting the gap leak into ad
   hoc spec prose.

## Quality gate (before calling a topic/edit done)

- [ ] The file has all seven mandatory sections in order, including a real `## 2. Scope` (not a
      renamed Concepts section, not a one-line stub).
- [ ] Every statistical/methodological/named-standard claim has an inline citation at the claim
      site.
- [ ] Every `##` section has a `### Sources` subsection with live + Wayback snapshot + accessed
      date (or a cited `spacesim/`/`docs/` file:line for claims about this project's own practice).
- [ ] §5 Implementation Guidance gives concrete consequences for DOM-002/DOM-005, an assessment
      rubric, a validation study design, or a named `spacesim/` module — not generic statistics
      commentary.
- [ ] No content duplicates DOM-002/DOM-005's own text; if it would, the topic is a short pointer +
      implementation-implications note instead (MSTR-007 §5).
- [ ] Frontmatter `Dependencies`/`Referenced By`/`Feature Mapping` are bidirectionally consistent,
      and `Status` truthfully reflects whether this checklist passes.
- [ ] Nothing reads like a 101 stats explainer ("a p-value tells you...") without immediately
      moving to the implementation-relevant nuance; if it does, cut it or point to `docs/training/`.
- [ ] File length stays in the 3-8 page band; oversized topics get split.

## Gotchas

- **Don't trust a file's own `Status: ✅ Done` frontmatter line right now** — it predates the
  sourcing/scope audit and is currently false for all 13 topics. Trust `R400-index.md` and the
  quality gate above.
- **Don't fabricate a citation to make the Sources requirement pass.** If a claim in the existing
  text turns out to be uncitable to a real source, soften or cut the claim rather than inventing a
  plausible-looking reference — inventing citations is exactly how this tier got into its current
  state (drafted in one pass with no sourcing discipline).
- `docs/FUTURE-WORK.md` §13 R1 sequences GAP-13 as **R500 first, R400 second** — if both this skill
  and `research-future-operations` are being progressed together, don't race ahead of that order
  without a reason to deviate.
- This simulator's own determinism (`SeededRng`, the Phase-1 property test) is an unusually strong
  Monte-Carlo/verification precedent most real-world systems don't have — R407/R409 should lean on
  it as a Tier A "primary source" in its own right, not just cite external Monte Carlo literature.
- This skill does not touch Tier R100 (orbital mechanics/OW), R200 (decision sciences, no skill
  yet), R300 (doctrine/exercises), or R500 (future operations) — those belong to
  `research-ow-orbital-mechanics`, a future decision-sciences skill, `research-doctrine-exercises`,
  and `research-future-operations` respectively.
