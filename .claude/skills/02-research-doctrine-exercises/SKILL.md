---
name: 02-research-doctrine-exercises
description: Produce or refresh expert-level, citation-grounded research on military doctrine (Western/non-Western counterspace doctrine, legal norms/ROE) and exercise/wargaming design (campaign design, operational art, deterrence/escalation, mission analysis, wargaming theory, red teaming, COG, EBO, COA analysis) to ground White Cell, Red AI, vignette, and scenario specs/features. Use when asked to research doctrine or wargaming-design topics, to add/extend `docs/research/encyclopedia/R3xx-*` topics, to refresh the `01/02/07` primers, or to gather grounding facts before drafting an FS-xxx/IMP-xxx spec or vignette/Red-doctrine-profile that touches White Cell rules, ROE, escalation, or exercise structure. Not for novice tutorials — those belong in `docs/training/`.
---

# Research: Military Doctrine & Exercise Design

Produces the **R300-tier encyclopedia** (`docs/research/encyclopedia/R301`–`R312`) and grounds the
pre-existing primers `docs/research/01-doctrine-western.md`, `02-doctrine-non-western.md`, and
`07-legal-norms-and-roe.md`. The governing rules are
[`docs/master/MSTR-007-research-philosophy.md`](../../../docs/master/MSTR-007-research-philosophy.md)
(purpose, tier shape, authoring cadence) and
[`docs/research/10-sources-and-methodology.md`](../../../docs/research/10-sources-and-methodology.md)
(citation format, source-quality tiers, review cadence). Read both before producing anything —
this skill does not restate them, it operationalizes them for this domain.

## What this is for (and what it is not)

> "The purpose is domain understanding, not academic research… give a future coding LLM agent
> enough domain understanding to implement a feature correctly." — MSTR-007 §2

This skill answers "if an agent is about to spec or build something touching doctrine, ROE,
escalation, White Cell adjudication, Red AI posture, or exercise/vignette structure, what does it
need to know to not get it wrong" — never "explain what a wargame is to a beginner." Real doctrine
citations (CCS Block 10.2, JP series, NATO/allied publications, treaty text, UNGA resolutions) and
real wargaming/operational-art literature are the bar; invented doctrine or paraphrased-without-
citation claims do not meet it. If a request is actually introductory ("what is a wargame," "what
is deterrence theory at a 101 level"), redirect to `docs/training/`; do not write that into the
encyclopedia or the primers.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| [`R300-index.md`](../../../docs/research/encyclopedia/R300-index.md) + `R301`–`R312` | Campaign design, operational art, deterrence/escalation, mission analysis, operational assessment, wargaming theory, red teaming, COG analysis, EBO, COA analysis, space strategy. |
| `docs/research/01-doctrine-western.md` | Western counterspace doctrine corpus (CCS, allied publications, the 5-D order, defensive actions, cross-cutting functions, responsible-counterspace norms). |
| `docs/research/02-doctrine-non-western.md` | Non-Western (PRC/Russia-class) counterspace doctrine corpus — the comparative basis for Red AI posture (`session/redai.py`). |
| `docs/research/07-legal-norms-and-roe.md` | Treaty floor (OST/Liability/Registration), LOAC-in-space, the 2022 DA-ASAT moratorium, CBMs/norms-under-negotiation — constrains White Cell ROE and ethics gates. |
| Grounding docs | `docs/master/DOM-003-white-cell-framework.md`, `DOM-009-doctrine-development-framework.md`, `DOM-006-governance-framework.md`. |
| Engine/content grounding | `spacesim/session/redai.py` (Red doctrine presets), `spacesim/content/vignettes/coa-*.yaml` (Course-of-Action content), `spacesim/content/vignettes/*.yaml` (scenario/exercise structure), the kinetic consequence-confirm gate in `ui_web` (escalation-dynamics grounded). |
| Feature Mapping targets | FS-106 (White Cell Dashboard), FS-108 (Inject Authoring), FS-301 (Research Analytics), and any new FS-xxx/vignette touching ROE, escalation, or exercise/scenario design. |

**Tier R300 is closed (all 12 topics ✅ per MSTR-007 §6/§7).** As with R100, do not bulk-author new
topics by default — add a new `R3xx` row (marked `⛔ Planned` first) only when a genuine gap
appears: a new Red doctrine profile with no grounding topic, a new White Cell adjudication
mechanism with no operational-art/escalation grounding, or a new vignette mechanic (e.g. a new COA
type) that has no topic an author would read first. The recurring invocation pattern is:

1. **Pre-spec/pre-vignette grounding** — before a new FS-xxx spec, Red doctrine profile, or
   vignette/COA file is authored, verify the relevant `R3xx` topic(s) and `01/02/07` primer
   sections already cover what's needed; fill the gap first if not.
2. **Citation-rot maintenance** — re-verify live URLs, refresh Wayback snapshots/`accessed` dates
   per the methodology's review cadence; doctrine-portal and treaty-tracker URLs reorganize on a
   multi-year cadence and are flagged as citation-rot risk in the methodology (§1.2).
3. **Depth/gap fill** — when an audit or a new Red AI posture / White Cell rule reveals a topic
   under-specifies the implementation-relevant consequence, expand §3/§5 rather than letting the
   gap leak into ad hoc spec or vignette-authoring prose.

## Workflow

1. **Read the trigger context.** What spec/vignette/Red-doctrine-profile/White-Cell mechanic needs
   grounding? Identify which `R3xx` topic(s) and which `01/02/07` primer section(s) are implicated.
2. **Check existing coverage first.** Read [`R300-index.md`](../../../docs/research/encyclopedia/R300-index.md)
   and the relevant topic file(s) before assuming a gap exists.
3. **If a gap exists:** add the row to `R300-index.md` (`⛔ Planned` status, ID, title, one-line
   scope, dependencies) before writing the topic file — index-before-content (MSTR-007 §6).
4. **Research with tiered sources** (`10-sources-and-methodology.md` §2): prefer Tier A (the actual
   doctrine document, treaty text, government primary source) and Tier B (think-tank/government
   technical reports — CSIS, SWF, IISS) over secondary news summaries, especially for non-Western
   doctrine where primary translations are scarce and must be flagged as such rather than silently
   treated as equivalent-confidence to a primary Western source.
5. **Write/update the topic file** following the mandatory seven-section shape (MSTR-007 §4):
   Purpose, Scope, Concepts, Operational Context, Implementation Guidance, Feature Mapping, Related
   Topics. §5 here means: what should a White Cell rule, Red AI posture function, or vignette author
   do differently *because* this doctrine/theory point is true — never left as pure exposition.
   - Frontmatter mirrors the existing `R301`-style block: Document ID, Version, Status,
     Dependencies, Referenced By, Produces (DOM-xxx / `redai.py` / vignette files it constrains),
     Feature Mapping, Related Topics.
   - Inline-cite every doctrinal assertion, named system, dated event, legal interpretation at the
     claim site (§1.1); no end-of-section-only citation lists.
   - Every `##` section ends with a `### Sources` subsection: live URL + Wayback snapshot + accessed
     date (§1.2).
   - Date-stamp every real-event claim at first mention (§1.3) — doctrine corpora especially need
     this since policy positions shift year to year (e.g. the 2022 DA-ASAT moratorium signatory
     list growing over time).
   - Keep the file in the 3-8 page band (MSTR-006 §4).
6. **Cross-link both directions** — `Referenced By`, `Related Topics`, and `Feature Mapping` on the
   FS-xxx spec(s)/DOM-xxx framework doc(s)/vignette(s) it grounds.
7. **Flip the index status** to `✅` once the topic satisfies the quality gate below.
8. **Verify, then commit.** Commit as `docs(research): R3xx — <what changed>` consistent with this
   branch's existing commit style.

## Quality gate (before calling a topic/edit done)

- [ ] Every doctrinal/legal/historical claim has an inline citation at the claim site.
- [ ] Every `##` section has a `### Sources` subsection with live + Wayback snapshot + accessed date.
- [ ] Non-Western doctrine claims sourced indirectly (via Western analysis of translated doctrine)
      are flagged as such, not presented with the same confidence as a primary source (methodology
      §2/§3).
- [ ] §5 Implementation Guidance gives concrete consequences for `redai.py`, White Cell rules,
      vignette/COA authoring, or ROE gates — not generic strategic commentary.
- [ ] No content duplicates an existing `01/02/07` primer; if it would, the topic is a short pointer
      + implementation-implications note instead (MSTR-007 §5).
- [ ] Frontmatter `Dependencies`/`Referenced By`/`Feature Mapping` are bidirectionally consistent.
- [ ] Nothing reads like a novice 101 explainer ("deterrence means discouraging an action…") without
      immediately moving to the implementation-relevant nuance; if it does, cut it or point to
      `docs/training/`.
- [ ] File length stays in the 3-8 page band; oversized topics get split.

## Gotchas

- Tier R300 being "closed" means *complete*, not *frozen* — edit freely on a real gap; don't spawn
  new topics speculatively.
- Treaty/policy-tracker URLs (UN OEWG, SWF moratorium tracker, government portals) move on a
  multi-year cadence — the Wayback snapshot is not optional for these (methodology §1.2).
- Don't let Red AI posture or White Cell rule changes get justified by doctrine claims that exist
  only in code comments or PR descriptions — the citation belongs in the `R3xx`/primer file, and the
  code/PR should point to it, not the other way around.
- This skill does not touch Tier R100 (orbital mechanics/OW — `02-research-ow-orbital-mechanics`'s
  scope) or Tiers R200 (decision sciences, no skill yet), R400 (research methods —
  `02-research-methods-and-validation`), or R500 (future operations — `02-research-future-operations`).

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
