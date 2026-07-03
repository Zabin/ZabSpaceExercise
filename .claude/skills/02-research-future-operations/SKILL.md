---
name: 02-research-future-operations
description: Produce and refresh the R500-tier future-operations encyclopedia (human-AI teaming, autonomy in space operations, AI decision support, future space warfare concepts, multi-domain operations, machine reasoning, autonomous planning systems, future command and control, AI integration patterns) that grounds forward-looking AI/autonomy context (DOM-008). Use when asked to research AI/autonomy/future-C2/multi-domain topics, to add/extend `docs/research/encyclopedia/R5xx-*` topics, or to gather grounding facts before drafting an FS-xxx/IMP-xxx spec touching in-world AI, autonomy, or future C2. Tier R500 closed its GAP-13 sourcing/scope remediation 2026-07-02 — this is now steady-state maintenance, not a remediation backlog. Not for novice AI tutorials — those belong in `docs/training/`.
---

# Research: Future Operations

Produces the **R500-tier encyclopedia** (`docs/research/encyclopedia/R501`–`R509`) and grounds
[`docs/domains/DOM-008-ai-integration-framework.md`](../../../docs/domains/DOM-008-ai-integration-framework.md)
— the framework that governs both **in-world AI** (Red doctrine presets today, any future
trainee-facing advisor) and **coding-agent practice** (this repository's own documentation-driven
development model), and is explicit that the two must never be conflated (DOM-008 §6). The
governing rules are
[`docs/master/MSTR-007-research-philosophy.md`](../../../docs/master/MSTR-007-research-philosophy.md)
(purpose, tier shape, authoring cadence) and
[`docs/research/10-sources-and-methodology.md`](../../../docs/research/10-sources-and-methodology.md)
(citation format, source-quality tiers, review cadence). Read both before producing anything —
this skill does not restate them, it operationalizes them for this domain. Tier R500 is now
**closed** (all 9 topics ✅, GAP-13 remediation complete 2026-07-02) — see "Current state" below.

## What this is for (and what it is not)

> "The purpose is domain understanding, not academic research… give a future coding LLM agent
> enough domain understanding to implement a feature correctly." — MSTR-007 §2

This skill answers "if an agent is about to spec or build something touching autonomy, an in-world
AI advisor, Red doctrine posture, or a future C2/multi-domain concept, what does it need to know to
not get it wrong, and where exactly does DOM-008's advisor-not-decider line sit" — never "explain
what AI is" or "speculate freely about future warfare." This tier is inherently more forward-
looking than R100/R300/R400 (DOM-008 §4 itself calls the human-AI-teaming material
"forward-looking"), but forward-looking is not a license to skip sourcing: real human-automation-
teaming research (aviation automation studies, published human-machine-teaming doctrine),
real named autonomy/AI-planning literature, and real precedent systems are the bar — invented
capabilities or unsourced predictions presented as settled fact are not. If a request is actually
"what is AI" or "explain autonomy levels 101," redirect to `docs/training/`.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| [`R500-index.md`](../../../docs/research/encyclopedia/R500-index.md) + `R501`–`R509` | Human-AI teaming, autonomy in space operations, AI decision support, future space warfare concepts, multi-domain operations, machine reasoning, autonomous planning systems, future command and control, AI integration patterns (the tier's capstone). |
| [`docs/domains/DOM-008-ai-integration-framework.md`](../../../docs/domains/DOM-008-ai-integration-framework.md) | §3 in-world AI today (Red doctrine presets), §4 future in-world AI (autonomy/teaming, explicitly forward-looking/R500-tier), §5 coding AI (this repo's own dev model), §6 what DOM-008 expects from R500-tier documents and any future FS touching AI — the **advisor, not decider** constraint every R5xx topic's Implementation Guidance must respect. |
| Engine grounding | `spacesim/session/redai.py` (Red doctrine presets — the only AI that exists in the simulator today; every "future" claim in this tier must be clearly distinguished from this present-tense system). |
| Feature Mapping targets | Any future in-world AI decision-support feature (🅿️ pending authorization per DOM-008 §4) and any long-horizon FS-xxx touching autonomy or future C2. |

## Current state (read this before choosing a workflow)

**Tier R500 is closed (all 9 topics ✅ per MSTR-007 §6/§7, GAP-13 remediation complete 2026-07-02).**
All 9 topics carry the mandatory §2 Scope section (MSTR-007 §4.2), inline citations at every
substantive claim site, a `### Sources` subsection on every `##` section (live URL + Wayback
snapshot + accessed date, or a cited `spacesim/session/redai.py`/`engine/recovery.py` file:line for
present-tense in-world-AI claims), and the mandatory DOM-008 §6 tag line. This closed GAP-13
(tracked in [`docs/FUTURE-WORK.md`](../../../docs/FUTURE-WORK.md) §13, Recommendation R1) for this
tier; per that recommendation's sequencing, **R400 (Research Methods,
`02-research-methods-and-validation`) is now the GAP-13 priority.** As with R100/R300, "closed" means
*complete*, not *frozen* — do not bulk-author new topics by default; add a new `R5xx` row
(`⛔ Planned` first, index-before-content) only on a genuine gap.

## Workflow

### A. New-topic / gap-fill pass (only on a genuine coverage gap)

1. **Read the trigger context.** What FS-xxx/IMP-xxx spec or in-world-AI/autonomy/future-C2
   proposal needs grounding? Identify which `R5xx` topic(s) are implicated.
2. **Check existing coverage first.** Read [`R500-index.md`](../../../docs/research/encyclopedia/R500-index.md)
   and the relevant topic file(s) before assuming a gap exists — [`R509`](../../../docs/research/encyclopedia/R509-ai-integration-patterns.md)
   is the tier's capstone; a new topic should not duplicate its synthesis role.
3. **If a gap exists:** add the row to `R500-index.md` (`⛔ Planned` status, ID, title, one-line
   scope, dependencies) before writing the topic file — index-before-content (MSTR-007 §6).
4. **Research with tiered sources** (`10-sources-and-methodology.md` §2): prefer Tier A/B —
   published human-automation-teaming studies (aviation automation research, e.g. FAA/NASA
   human-factors reports), named military human-machine-teaming doctrine (DARPA Mosaic Warfare,
   DoD JADC2), peer-reviewed AI-planning and machine-reasoning literature, and this project's own
   `spacesim/session/redai.py` where a claim is about present-tense in-world AI. Flag any
   single-source or clearly speculative claim inline as such (methodology §3) rather than
   presenting forward-looking material with false settled-fact confidence — this matters more here
   than in any other tier.
5. **Write the topic file** following the mandatory seven-section shape (MSTR-007 §4: Purpose,
   Scope, Concepts, Operational Context, Implementation Guidance, Feature Mapping, Related Topics),
   with the DOM-008 §6 tag line directly under the frontmatter/breadcrumb, before §1. Inline-cite
   every substantive claim (a named study, a named doctrine publication, a named autonomy-level
   framework, a dated precedent system — no end-of-section-only citation dumps), and add a
   `### Sources` subsection to every `##` section.
6. **Flip the index status** to `✅` once the topic satisfies the quality gate below, keeping
   `Dependencies`/`Referenced By` bidirectionally accurate.
7. **Verify, then commit** as `docs(research): R5xx — <what changed>`.

### B. Steady-state maintenance

1. **Pre-spec grounding** — before any future in-world-AI-advisor or future-C2 FS-xxx is drafted,
   verify the relevant `R5xx` topic(s) already cover what's needed against DOM-008 §4/§6.
2. **Citation-rot maintenance** — re-verify live URLs, refresh Wayback snapshots/`accessed` dates.
3. **Depth/gap fill** — when a new AI-adjacent feature proposal reveals a topic under-specifies the
   advisor-not-decider consequence, expand §5 rather than letting the gap leak into ad hoc spec
   prose that might quietly cross the DOM-008 §4 line.

## Quality gate (before calling a topic/edit done)

- [ ] The file has all seven mandatory sections in order, including a real `## 2. Scope`, plus its
      DOM-008 §6 tag line intact.
- [ ] Every AI/autonomy/teaming claim has an inline citation at the claim site — including
      forward-looking claims, which get flagged as speculative rather than left uncited.
- [ ] Every `##` section has a `### Sources` subsection with live + Wayback snapshot + accessed
      date (or a cited `spacesim/session/redai.py` file:line for present-tense in-world-AI claims).
- [ ] §5 Implementation Guidance states, concretely, what a future in-world-AI feature or Red
      doctrine change must and must not do under DOM-008 §4's "advisor, not decider" constraint —
      not generic AI-ethics commentary.
- [ ] No content quietly asserts a future in-world AI capability as if it were already
      authorized — DOM-008 §4 features remain 🅿️ pending authorization until stated otherwise.
- [ ] No content duplicates DOM-008's own text; if it would, the topic is a short pointer +
      implementation-implications note instead (MSTR-007 §5).
- [ ] Frontmatter `Dependencies`/`Referenced By`/`Feature Mapping` are bidirectionally consistent,
      and `Status` truthfully reflects whether this checklist passes.
- [ ] Nothing reads like a 101 AI explainer without moving to the DOM-008-specific implementation
      nuance; if it does, cut it or point to `docs/training/`.
- [ ] File length stays in the 3-8 page band.

## Gotchas

- **Tier R500 is closed** (all 9 topics ✅, GAP-13 remediation complete 2026-07-02) — a file's
  `Status: ✅ Done` frontmatter is now trustworthy again; treat any topic reverting to `🚧` as a
  real regression to fix, not a stale marker to ignore.
- **Don't let a forward-looking topic slide into unsourced speculation dressed as fact.** This was
  the single biggest risk in this tier during remediation — "most speculative claims" per the
  review — and remains the standard for any new topic added under Workflow A: a claim with no real
  source should read as clearly hypothetical, not confidently asserted.
- **Never let this tier's forward-looking framing bleed into implying an in-world AI advisor
  feature is currently authorized or built.** Only `spacesim/session/redai.py` (Red doctrine
  presets) exists today; everything else in DOM-008 §4/§6 is 🅿️ pending.
- Keep the in-world-AI vs. coding-agent-practice distinction crisp per DOM-008 §6 — a topic tagged
  "coding-agent practice" should ground how *this repository's own agents* work (documentation-
  driven development, the GDS ladder, this very skill-authoring pattern), not get merged with the
  in-world-advisor discussion.
- This skill does not touch Tier R100 (orbital mechanics/OW), R200 (decision sciences, no skill
  yet), R300 (doctrine/exercises), or R400 (research methods) — those belong to
  `02-research-ow-orbital-mechanics`, a future decision-sciences skill, `02-research-doctrine-exercises`,
  and `02-research-methods-and-validation` respectively.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 02 — Research** of the documentation-driven-development pipeline (see
[`.claude/skills/README.md`](../README.md); stages run in numeric order, and `00-pipeline-manager`
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
