---
name: 02-research-training-pedagogy
description: Produce and refresh the R600-tier training-pedagogy encyclopedia (instructional systems design, adult learning, simulation-based learning and debriefing, cognitive load and scaffolding, learning-path/progression design, minimalist procedural documentation, assessment of learning in wargames, software onboarding/tutorial design) that grounds the training corpus elevated to co-equal product status (MSTR-001 §2, 2026-07-04). Use when asked to research how to teach people to use this tool, to author/extend `docs/research/encyclopedia/R6xx-*` topics, or to gather pedagogy grounding before a manual-authoring, vignette-development, or manual-review pass needs a citable basis for a sequencing/scaffolding/debrief decision. Tier R600 is scaffolded (index authored, 0/8 topics) — authoring must meet the full sources-and-methodology citation bar from the first draft; this tier never enters the uncited state R400/R500 had to be remediated out of. Not for writing the manuals themselves (08-training-manual-authoring) or vignettes (08-vignette-development) — this skill produces research, not training artifacts.
---

# Research — Training Pedagogy & Instructional Design (Tier R600)

Owns the **R600 tier** of the research encyclopedia
([`docs/research/encyclopedia/R600-index.md`](../../../docs/research/encyclopedia/R600-index.md)):
the learning science behind how this simulator teaches — manuals, the vignette learning path,
in-app briefs/tutorials, and AAR debrief practice. A peer of the other four `02-research-*`
skills; run whichever owns the gap.

## What this is for (and what it is not)

The training corpus is a co-equal product with the code (MSTR-001 §2, owner decision 2026-07-04).
Its authoring and review skills need the same kind of citable grounding that code-implementation
packages get from R100: when `08-training-manual-authoring` chooses a module structure, when
`08-vignette-development` sequences a learning-path rung, when `09-training-manual-review` judges
"is this teachable," the justification should resolve to an R600 topic with sources — not a vibe.

It SHALL NOT write or edit anything under `docs/training/` or `spacesim/content/` (those belong
to the training-artifact skills), define requirements (04), or make architecture decisions (03).
It produces research documents only: `R6xx` topics and the R600 index's status column.

## Scope (what this skill owns)

- `docs/research/encyclopedia/R601`–`R608` (and any future R6xx topics) + `R600-index.md`.
- Nothing else. Findings about manual/vignette defects discovered while researching route to
  the owning training-artifact skill via the completion summary, never fixed here.

## Current state (read this before choosing a workflow)

Tier scaffolded 2026-07-04: index authored with 8 planned topics, **0 authored**. Every topic
must meet [`docs/research/10-sources-and-methodology.md`](../../../docs/research/10-sources-and-methodology.md)
in full from its first draft — §2 Scope (MSTR-007 §4.2), inline citations at every substantive
claim site, a `### Sources` subsection per `##` section (live URL + Wayback snapshot + accessed
date), `Last Reviewed`/`Primary Sources Consulted` frontmatter. The index carries a starting
bibliography (Gagné, Merrill, Knowles, Sweller, Ericsson, Carroll, Kirkpatrick, Fanning & Gaba,
TC 25-20, van Merriënboer) — verify each citation live at authoring time; the list itself is not
a citation. An unauthored topic is **not citable** by downstream skills (`NFR-3600` and the RTM
already state this).

## Workflow

### A. Authoring a planned topic (the standard pass)

1. Pick the topic by dependency order from the R600 index (R601 first — everything depends on it)
   unless the invoker names one or a downstream skill's finding names the gap.
2. Research from Tier A/B sources (peer-reviewed learning-science literature, military training
   doctrine such as the AAR/after-action literature, standards bodies); every claim cited at the
   claim site. `[UNVERIFIED]` + non-done Status when a citation can't be verified — never guess.
3. Write the seven-section topic per MSTR-007 §4 (Purpose / Scope / Concepts / Operational
   Context / Implementation Guidance / Feature Mapping / Related Topics), with **Implementation
   Guidance aimed at the training-artifact skills**: what R602 means for manual tone, what R605
   means for rung ordering, what R603 means for the coaching-notes/AAR features.
4. Feature Mapping names the real artifacts: `docs/training/` modules, `training/16` rungs,
   vignette `tutorial:`/`coaching:` blocks, `session/aar.py`-backed debrief practice.
5. Flip the topic's index row (⛔ → ✅), update the tier status line and the encyclopedia INDEX
   count.

### B. Steady-state maintenance (once topics exist)

Refresh a topic when its sources age past the review cadence, when a downstream skill reports a
grounding gap, or when shipped training features (new tutorial mechanics, new brief fields)
change a topic's Feature Mapping. Same citation bar as authoring.

## Quality gate (before calling a topic done)

- [ ] §2 Scope present; all seven sections present.
- [ ] Every substantive claim carries an inline citation; every `##` section ends with
      `### Sources` (live URL + Wayback + accessed date).
- [ ] No claim rests on a single Tier-D source; anything unverifiable is `[UNVERIFIED]` and the
      topic Status reflects it.
- [ ] Implementation Guidance is actionable by `08-training-manual-authoring` /
      `08-vignette-development` / `09-training-manual-review` — a reader could change a real
      training artifact from it.
- [ ] Index row, tier status line, and encyclopedia INDEX all agree.

## Gotchas

- **Don't restate R300.** Wargame *design* (campaign structure, red-teaming, COA analysis) is
  R300's; R600 is the *learner's* side. Cross-reference, don't duplicate.
- **Don't slide into authoring training content.** The moment a pass wants to rewrite a manual
  paragraph "as an example," stop — route it to the owning skill.
- **The PME audience is specific** (GDS-01 §2; assumption A8): facilitated, professional,
  semi-technical. General-audience ed-tech findings need an explicit applicability argument.

## Pipeline position & completion summary (mandatory, every run)

This skill is a **Stage 02 peer** of the documentation-driven-development pipeline (see
[`.claude/skills/README.md`](../README.md)). Upstream: `01-vision` (MSTR-001 §2's elevation
decision, MSTR-003's educational philosophy). Downstream: `03-architecture-design-synthesis` and
the training-artifact skills (`08-training-manual-authoring`, `08-vignette-development`,
`09-training-manual-review`) that cite this tier.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — topics authored/refreshed (IDs + paths), index/status updates.
2. **Recommendations** — grounding gaps found but not owned here, routed to their owning skill;
   any `[UNVERIFIED]` citations needing network access or user-supplied sources.
3. **Next step** — the next topic by dependency order, or the downstream skill now unblocked by
   what this run authored.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
