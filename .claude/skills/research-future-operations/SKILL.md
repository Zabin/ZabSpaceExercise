---
name: research-future-operations
description: Produce, refresh, and — as the current primary job — remediate the R500-tier future-operations encyclopedia (human-AI teaming, autonomy in space operations, AI decision support, future space warfare concepts, multi-domain operations, machine reasoning, autonomous planning systems, future command and control, AI integration patterns) that grounds forward-looking AI/autonomy context (DOM-008). Use when asked to research AI/autonomy/future-C2/multi-domain topics, to add/extend `docs/research/encyclopedia/R5xx-*` topics, to close the R500 sourcing/scope defect (GAP-13 — every topic is missing the mandatory §2 Scope section and carries zero citations, the review's stated first priority since this tier is "zero citations, most speculative claims"), or to gather grounding facts before drafting an FS-xxx/IMP-xxx spec touching in-world AI, autonomy, or future C2. Not for novice AI tutorials — those belong in `docs/training/`.
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
this skill does not restate them, it operationalizes them for this domain. Unlike the R100/R300
tiers, R500 is **not yet closed** — see "Current state" below.

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

**Tier R500 is structurally drafted but not done, and is the review's stated first-priority gap.**
All 9 topics exist with substantive §1 Purpose / Concepts / Operational Context / Implementation
Guidance / Feature Mapping / Related Topics content, and each one already carries the mandatory
**"DOM-008 §6 tag"** line classifying it as in-world AI, coding-agent practice, both, or neither —
but **every single topic is missing the mandatory §2 Scope section** (MSTR-007 §4.2) and **carries
zero citations**: no inline sourcing at any claim site, no `### Sources` subsections, despite this
tier making forward-looking claims about AI/autonomy precedent that would normally need Tier A-C
sourcing more than any other tier, not less. This is tracked as **GAP-13** in
[`docs/FUTURE-WORK.md`](../../../docs/FUTURE-WORK.md) §13 (Recommendation R1), which explicitly
names R500 as **"first (zero citations, most speculative claims); gate for citing the encyclopedia
externally."** Treat this tier as the priority remediation target ahead of R400. Do not add new
R5xx topics while this remediation backlog is open — [`R509`](../../../docs/research/encyclopedia/R509-ai-integration-patterns.md)
is already the intended capstone; finish the 9 first.

## Workflow

### A. Remediation pass (the current priority — GAP-13, do this before R400)

1. **Pick the next unremediated topic** from [`R500-index.md`](../../../docs/research/encyclopedia/R500-index.md)
   (any topic still marked `🚧`), in ID order unless directed otherwise — R501 (Human-AI Teaming)
   is the tier's dependency root, so remediating it first keeps `Referenced By` cross-links honest.
2. **Read the current file fully**, including its DOM-008 §6 tag line — the substantive content is
   already there; the job is adding Scope + citations, not rewriting the analysis, unless a claim
   turns out to be uncitable (see Gotchas).
3. **Insert a `## 2. Scope` section** immediately after Purpose, then renumber every following
   section to the mandatory seven-part shape: 1 Purpose, 2 Scope, 3 Concepts, 4 Operational
   Context, 5 Implementation Guidance, 6 Feature Mapping, 7 Related Topics — keep the DOM-008 §6
   tag line where it currently sits, directly under the frontmatter/breadcrumb, before §1.
   Scope states the boundary against neighboring R5xx topics and against DOM-008 itself (e.g. R502
   Autonomy in Space Operations should explicitly defer the *doctrine* of autonomous engagement to
   R300, and cover only the bus/payload autonomy-degree vocabulary).
4. **Research with tiered sources** (`10-sources-and-methodology.md` §2): prefer Tier A/B —
   published human-automation-teaming studies (aviation automation research, e.g. FAA/NASA
   human-factors reports), named military human-machine-teaming doctrine, peer-reviewed AI-planning
   and machine-reasoning literature, and this project's own `spacesim/session/redai.py` where a
   claim is about present-tense in-world AI. Flag any single-source or clearly speculative claim
   inline as such (methodology §3) rather than presenting forward-looking material with false
   settled-fact confidence — this matters more here than in any other tier.
5. **Add an inline citation at every substantive claim site** — a named study, a named doctrine
   publication, a named autonomy-level framework (e.g. SAE/DoD autonomy taxonomies), a dated
   precedent system. No end-of-section-only citation dumps.
6. **Add a `### Sources` subsection to every `##` section**: live URL + Wayback snapshot + accessed
   date, or a cited `spacesim/session/redai.py` file:line for claims about the simulator's present
   AI.
7. **Correct the frontmatter `Status` field** to `🚧` if it currently (falsely) reads `✅ Done`;
   flip to `✅ Done` only once the topic passes the quality gate below.
8. **Update the row in `R500-index.md`** from `🚧 (no §2 Scope; uncited)` to `✅` once done, keeping
   `Dependencies`/`Referenced By` bidirectionally accurate.
9. **Once all 9 topics are `✅`**, rewrite `R500-index.md`'s tier-level status paragraph to the
   closed-tier framing R100/R300 use, and notify/hand off to `research-methods-and-validation` that
   R400 is now the GAP-13 priority per the review's sequencing.
10. **Verify, then commit** as `docs(research): R5xx — <what changed>`.

### B. Steady-state maintenance (once the tier is closed)

Same three activities as the closed R100/R300 tiers — do not bulk-author new topics by default;
add a new `R5xx` row (`⛔ Planned` first, index-before-content) only on a genuine gap:

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

- **This tier is the review's named first priority for GAP-13** (`docs/FUTURE-WORK.md` §13 R1) —
  if only one of this skill or `research-methods-and-validation` is being run, run this one first.
- **Don't trust a file's own `Status: ✅ Done` frontmatter line right now** — it predates the
  sourcing/scope audit and is currently false for all 9 topics.
- **Don't let a forward-looking topic slide into unsourced speculation dressed as fact.** This is
  the single biggest risk in this tier specifically — "most speculative claims" per the review —
  so a claim with no real source should read as clearly hypothetical, not confidently asserted.
- **Never let this tier's forward-looking framing bleed into implying an in-world AI advisor
  feature is currently authorized or built.** Only `spacesim/session/redai.py` (Red doctrine
  presets) exists today; everything else in DOM-008 §4/§6 is 🅿️ pending.
- Keep the in-world-AI vs. coding-agent-practice distinction crisp per DOM-008 §6 — a topic tagged
  "coding-agent practice" should ground how *this repository's own agents* work (documentation-
  driven development, the GDS ladder, this very skill-authoring pattern), not get merged with the
  in-world-advisor discussion.
- This skill does not touch Tier R100 (orbital mechanics/OW), R200 (decision sciences, no skill
  yet), R300 (doctrine/exercises), or R400 (research methods) — those belong to
  `research-ow-orbital-mechanics`, a future decision-sciences skill, `research-doctrine-exercises`,
  and `research-methods-and-validation` respectively.
