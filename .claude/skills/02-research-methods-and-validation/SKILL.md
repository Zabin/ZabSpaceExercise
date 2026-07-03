---
name: 02-research-methods-and-validation
description: Produce and refresh the R400-tier research-methods encyclopedia (experimental design, hypotheses/variables, statistics, measurement theory, uncertainty analysis, modeling practices, Monte Carlo, sensitivity analysis, verification, validation, human-subjects research, survey/instrument design, data analysis and reporting) that grounds assessment/validation work (DOM-002, DOM-005). Use when asked to research statistics/experiment-design/measurement/validation topics, to add/extend `docs/research/encyclopedia/R4xx-*` topics, or to gather grounding facts before drafting an FS-xxx/IMP-xxx spec or assessment/validation feature that touches measurement, statistical claims, or model V&V. Tier R400 closed its GAP-13 sourcing/scope remediation 2026-07-02 — this is now steady-state maintenance, not a remediation backlog. Not for novice statistics tutorials — those belong in `docs/training/`.
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
this skill does not restate them, it operationalizes them for this domain. Tier R400 is now
**closed** (all 13 topics ✅, GAP-13 remediation complete 2026-07-02) — see "Current state" below.

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

**Tier R400 is closed (all 13 topics ✅ per MSTR-007 §6/§7, GAP-13 remediation complete
2026-07-02).** All 13 topics carry the mandatory §2 Scope section (MSTR-007 §4.2), inline citations
at every substantive claim site, and a `### Sources` subsection on every `##` section (live URL +
Wayback snapshot + accessed date, or a cited `spacesim/`/`docs/` file:line for claims about this
project's own practice). This closed GAP-13 (tracked in
[`docs/FUTURE-WORK.md`](../../../docs/FUTURE-WORK.md) §13, Recommendation R1) for this tier,
completing the R500-then-R400 sequencing that recommendation specified. As with R100/R300, "closed"
means *complete*, not *frozen* — do not bulk-author new topics by default; add a new `R4xx` row
(`⛔ Planned` first, index-before-content) only on a genuine gap.

## Workflow

### A. New-topic / gap-fill pass (only on a genuine coverage gap)

1. **Read the trigger context.** What FS-xxx/IMP-xxx spec or assessment/validation feature needs
   grounding? Identify which `R4xx` topic(s) are implicated.
2. **Check existing coverage first.** Read [`R400-index.md`](../../../docs/research/encyclopedia/R400-index.md)
   and the relevant topic file(s) before assuming a gap exists.
3. **If a gap exists:** add the row to `R400-index.md` (`⛔ Planned` status, ID, title, one-line
   scope, dependencies) before writing the topic file — index-before-content (MSTR-007 §6).
4. **Research with tiered sources** (`10-sources-and-methodology.md` §2): prefer Tier A (primary —
   the actual standard, textbook, or peer-reviewed paper; this project's own `test_determinism.py`
   and `AUDIT-2026-06-UI-TTC.md` where the claim is about *this simulator's* practice) and Tier B
   (NIST/ISO measurement standards, DoD/DOE V&V handbooks, government human-subjects guidance) over
   blog-post or Wikipedia-only summaries of statistical methods.
5. **Write the topic file** following the mandatory seven-section shape (MSTR-007 §4: Purpose,
   Scope, Concepts, Operational Context, Implementation Guidance, Feature Mapping, Related Topics).
   Scope states what the topic covers and, explicitly, what it defers to a neighboring R4xx topic
   or to DOM-002/DOM-005 (the boundary test from MSTR-007 §5) — e.g. R404 (Measurement Theory)
   explicitly does not re-derive the statistical tests that are R403's job. Inline-cite every
   substantive claim (a named statistical test, a named standard, a named methodology, a dated
   study or handbook edition — no end-of-section-only citation dumps), and add a `### Sources`
   subsection to every `##` section (live + Wayback + accessed date, or a cited file:line for
   claims about this project's own practice).
6. **Flip the index status** to `✅` once the topic satisfies the quality gate below, keeping
   `Dependencies`/`Referenced By` bidirectionally accurate.
7. **Verify, then commit** as `docs(research): R4xx — <what changed>`, consistent with this
   branch's existing commit style.

### B. Steady-state maintenance

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

- **Tier R400 is closed** (all 13 topics ✅, GAP-13 remediation complete 2026-07-02) — a file's
  `Status: ✅ Done` frontmatter is now trustworthy again; treat any topic reverting to `🚧` as a
  real regression to fix, not a stale marker to ignore.
- **Don't fabricate a citation to make the Sources requirement pass.** If a claim in a new topic
  turns out to be uncitable to a real source, soften or cut the claim rather than inventing a
  plausible-looking reference — inventing citations is exactly how this tier got into its
  pre-remediation state (drafted in one pass with no sourcing discipline).
- This simulator's own determinism (`SeededRng`, the Phase-1 property test) is an unusually strong
  Monte-Carlo/verification precedent most real-world systems don't have — R407/R409 should lean on
  it as a Tier A "primary source" in its own right, not just cite external Monte Carlo literature.
- This skill does not touch Tier R100 (orbital mechanics/OW), R200 (decision sciences, no skill
  yet), R300 (doctrine/exercises), or R500 (future operations) — those belong to
  `02-research-ow-orbital-mechanics`, a future decision-sciences skill, `02-research-doctrine-exercises`,
  and `02-research-future-operations` respectively.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 02 — Research** of the documentation-driven-development pipeline (see
[`.claude/skills/README.md`](../README.md); stages run in numeric order, and `00-pipeline-status`
reports where the project currently stands). The four `02-research-*` skills are peers at the same
stage — run whichever owns the tier the gap is in; they have no ordering among themselves.
Upstream: `01-vision`. Downstream: `03-architecture-design-synthesis` (and whichever spec-authoring
skill requested the grounding).

End **every** invocation — full topic authoring, maintenance edit, or blocked stop — with a chat
summary containing exactly these three parts:

1. **What changed** — every encyclopedia topic/primer produced or updated (paths), every index
   status flipped.
2. **Recommendations** — remaining coverage gaps, citation-rot findings, single-source claims that
   need a second source, and who owns each follow-up.
3. **Next step** — say explicitly what to run next and why: if this run closed a grounding gap
   requested by a downstream skill (`03-architecture-design-synthesis`,
   `06-feature-specification`, `07-implementation-planning`), return to that skill and resume the
   blocked artifact; if another research tier still has a gap for the current increment, name the
   sibling `02-research-*` skill that owns it; otherwise advance to
   `03-architecture-design-synthesis`.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
