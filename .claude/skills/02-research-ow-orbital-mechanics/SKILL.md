---
name: 02-research-ow-orbital-mechanics
description: Produce or refresh expert-level, citation-grounded research on orbital warfare (counterspace effects — EW/cyber/DE/kinetic/RPO) and orbital mechanics (regimes, propagation, access geometry, custody) to ground new specs/features for the Space Control & Orbital Warfare Exercise Simulator. Use when asked to research OW/counterspace or orbital-mechanics topics, to add/extend `docs/research/encyclopedia/R1xx-*` topics, to refresh the `03-05` primers, or to gather implementation-grounding facts before drafting an FS-xxx/IMP-xxx spec that touches orbits, access, custody, jamming, cyber, DE, or kinetic effects. Not for novice tutorials — those belong in `docs/training/`.
---

# Research: Orbital Warfare & Orbital Mechanics

Produces the **R100-tier encyclopedia** (`docs/research/encyclopedia/R101`–`R120`) and grounds the
pre-existing primers `docs/research/03-counterspace-taxonomy.md`,
`04-orbital-mechanics-primer.md`, and `05-mission-types-and-counters.md`. The governing rules are
[`docs/master/MSTR-007-research-philosophy.md`](../../../docs/master/MSTR-007-research-philosophy.md)
(purpose, tier shape, authoring cadence) and
[`docs/research/10-sources-and-methodology.md`](../../../docs/research/10-sources-and-methodology.md)
(citation format, source-quality tiers, review cadence). Read both before producing anything —
this skill does not restate them, it operationalizes them for this domain.

## What this is for (and what it is not)

> "The purpose is domain understanding, not academic research… give a future coding LLM agent
> enough domain understanding to implement a feature correctly." — MSTR-007 §2

This skill exists to answer "if an agent is about to implement or spec something touching orbits,
access windows, custody, jamming, cyber, directed energy, kinetic engagement, or RPO, what does it
need to know to not get it wrong" — never "explain orbital mechanics to a beginner." If a request
is actually "teach me what an orbit is," redirect to `docs/training/` or the primers' existing
prose; do not write novice-grade tutorial content into the encyclopedia. Every document this skill
produces should be dense enough that a domain expert would not roll their eyes, and every claim
must trace to a real, cited source — never invented numbers, never approximate Pₖ/effectiveness
figures presented as fact without a source.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| [`R100-index.md`](../../../docs/research/encyclopedia/R100-index.md) + `R101`–`R120` | Implementation-grounding encyclopedia entries — orbital regimes, propagator fidelity, SDA, C2, custody, ground/constellation/sensor ops, comms, power/thermal, propulsion/maneuver, ADCS, CDH, EW, cyber, DE/kinetic, SSN, data fusion, access/geometry. |
| `docs/research/03-counterspace-taxonomy.md` | The five-D (deceive/disrupt/deny/degrade/destroy) effect taxonomy and the cyber exception — the "why" layer R1xx topics point back to. |
| `docs/research/04-orbital-mechanics-primer.md` | Full derivations (regimes, Kepler+J2, access geometry, eclipse) — R101/R112/R120 are implementation-focused pointers into this, not duplicates. |
| `docs/research/05-mission-types-and-counters.md` | Mission-type ↔ counter-mission mapping (ISR denial, RPO shadowing, GNSS EW, etc.). |
| Engine grounding | `spacesim/engine/{orbit,propagator,access,custody,effects,jam,engage,cyber,sigint,isr,perturbations,sun,maneuver}.py` — every topic must trace to the real code module(s) it constrains. |
| Feature Mapping targets | FS-101 (Mission Planning), FS-103 (Custody Management), FS-104 (SDA Tasking), FS-105 (Spacecraft Operations), and any new FS-xxx touching orbits/effects. |

**Tier R100 is closed (all 20 topics ✅ per MSTR-007 §6/§7).** Do not bulk-author new topics by
default — only add a new `R1xx` row (marked `⛔ Planned` first, per the index-before-content rule)
when a genuine coverage gap appears: a new `engine/` subsystem, a new five-D effect category, or a
new access channel that has no topic document an implementer extending it would read first. The
day-to-day invocation of this skill is usually **maintenance and grounding work**, not new-topic
authoring:

1. **Pre-spec grounding** — before an FS-xxx/IMP-xxx spec touching this domain is drafted, verify
   the relevant R1xx topics (and 03-05 primer sections) already say what the spec needs; if a gap
   exists, fill it (existing topic edit, or new topic if truly novel) before the spec is written,
   not after.
2. **Citation-rot maintenance** — per the methodology's review cadence, re-verify live URLs still
   resolve, refresh Wayback snapshots and `accessed` dates, and flag any source that 404s with no
   live replacement.
3. **Depth/gap fill** — when an audit (e.g. `docs/AUDIT-2026-06*.md`) or a new feature reveals a
   topic was under-specified for implementation, expand that topic's §3 Concepts / §5 Implementation
   Guidance rather than letting the gap leak into ad hoc spec prose.

## Workflow

1. **Read the trigger context.** What spec/feature/code change needs grounding? Identify which
   `R1xx` topic(s) and which `03-05` primer section(s) are implicated.
2. **Check existing coverage first.** Read [`R100-index.md`](../../../docs/research/encyclopedia/R100-index.md)
   and the relevant topic file(s) before assuming a gap exists — most domain questions are already
   answered there; re-reading beats re-researching.
3. **If a gap exists:** add the row to `R100-index.md` (`⛔ Planned` status, ID, title, one-line
   scope, dependencies) before writing the topic file — the index-before-content rule (MSTR-007 §6).
4. **Research with tiered sources** (`10-sources-and-methodology.md` §2): prefer Tier A (primary —
   doctrine text, engine code itself, test records, treaty text) and Tier B (government/think-tank
   technical reports) over news summaries. Use `WebSearch`/`WebFetch` for live sources; capture a
   Wayback Machine snapshot URL for every external citation.
5. **Write/update the topic file** following the mandatory seven-section shape (MSTR-007 §4):
   Purpose, Scope, Concepts, Operational Context, Implementation Guidance, Feature Mapping,
   Related Topics. **A document missing §5 has not done the job** — every concept must resolve to a
   concrete "do/don't do this in the implementation" statement, not just an explanation.
   - Frontmatter: Document ID, Version, Status, Dependencies, Referenced By, Produces (file paths
     into `spacesim/`), Feature Mapping, Related Topics — mirror the existing `R101` frontmatter
     exactly.
   - Inline-cite every numerical claim, named system, dated event, at the claim site (no
     footnote-style end-of-section citation lists) per §1.1 of the methodology.
   - Every `##` section ends with a `### Sources` subsection: live URL + Wayback snapshot + accessed
     date, per §1.2.
   - Date-stamp every real-event claim at first mention (§1.3).
   - Keep the file in the 3-8 page band (MSTR-006 §4) — split into a new topic rather than letting
     one file sprawl.
6. **Cross-link both directions.** Update `Referenced By` in any topic this one now depends on; add
   this topic to the `Related Topics` of any topic/primer it elaborates; add it to `Feature Mapping`
   on the FS-xxx spec(s) it grounds.
7. **Flip the index status** to `✅` once the topic satisfies the quality bar below.
8. **Verify, then commit.** Re-read the topic against the checklist; commit as
   `docs(research): R1xx — <what changed>` consistent with this branch's existing commit style.

## Quality gate (before calling a topic/edit done)

- [ ] Every claim has an inline citation at the claim site (not just listed at the section foot).
- [ ] Every `##` section has a `### Sources` subsection with live + Wayback snapshot + accessed date.
- [ ] §5 Implementation Guidance gives concrete do/don't statements tied to real `spacesim/engine/`
      file paths and function names — not generic advice.
- [ ] No content duplicates an existing `03-05` primer; if it would, the topic is a short pointer +
      implementation-implications note instead (MSTR-007 §5).
- [ ] Frontmatter `Dependencies`/`Referenced By`/`Feature Mapping` are bidirectionally consistent
      with the files they reference.
- [ ] Nothing in the document is novice-tutorial prose ("an orbit is a path a satellite takes
      around…") — if it reads like that, cut it; point to `docs/training/` instead.
- [ ] File length stays in the 3-8 page band; oversized topics get split.

## Gotchas

- Tier R100 being "closed" means *complete*, not *frozen* — edit existing topics freely when a gap
  or staleness is found; just don't spawn new topics without a real coverage gap.
- Don't re-derive Kepler's equations or full eclipse math inside an `R1xx` file — that's
  `04-orbital-mechanics-primer.md`'s job; the encyclopedia topic is the implementation-focused
  pointer plus consequences.
- A single-source claim at any tier must be flagged inline per the methodology §3 — don't silently
  present a one-source number as settled fact.
- This skill does not touch Tier R200 (decision sciences, no skill yet), Tier R300 (military
  analysis/doctrine/exercises — `02-research-doctrine-exercises`), Tier R400 (research methods —
  `02-research-methods-and-validation`), or Tier R500 (future operations —
  `02-research-future-operations`).

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
