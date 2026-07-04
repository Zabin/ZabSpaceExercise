# Tier R600 — Training Pedagogy & Instructional Design

[↑ Encyclopedia index](INDEX.md)

Grounding for the **training corpus as a co-equal product** (owner decision 2026-07-04; MSTR-001
§2, GDS-00/GDS-01 same-dated sections): the learning science behind *how this tool teaches* — the
manuals under `docs/training/`, the vignette learning path, the in-app briefs/tutorials, and the
AAR debrief practice. Consumed by the `08-training-manual-authoring`, `08-vignette-development`,
and `09-training-manual-review` skills the way R100 is consumed by code-implementation packages.
Distinct from [R300](R300-index.md) (wargame *design* for its own sake — campaign design,
red-teaming, COA analysis) — R600 is about the **learner**: how a novice becomes a competent
operator of this simulator and the doctrine it encodes. Owned by the
`02-research-training-pedagogy` skill. 8 topics.

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| R601 | Instructional Systems Design | ADDIE/backward-design applied to simulator training: from training objective to manual module and vignette rung. | — | ⛔ Planned |
| R602 | Adult Learning Theory | Andragogy/self-direction for the professional-military-education audience; implications for manual tone, length, and sequencing. | R601 | ⛔ Planned |
| R603 | Simulation-Based Learning & Debriefing | What makes simulation training transfer; debriefing/AAR practice as the payoff step (ties to MSTR-001 §1 item 3). | R601 | ⛔ Planned |
| R604 | Cognitive Load & Scaffolding in Complex-System Training | Managing intrinsic/extraneous load when teaching a many-panel operator console; fidelity/`ops_fidelity` as a scaffolding dial. | R602 | ⛔ Planned |
| R605 | Learning-Path & Progression Design | Novice→expert sequencing, part-task training, and mastery gating — the theory behind `training/16-learning-path.md`'s rung structure. | R601, R604 | ⛔ Planned |
| R606 | Minimalist & Procedural Documentation | Carroll's minimalism, task-oriented manuals, and role-scoped procedure layers — the craft behind the cell manuals' shape. | R602 | ⛔ Planned |
| R607 | Assessment of Learning in Wargames & Exercises | Measuring whether training worked without corrupting the exercise; connects to DOM-002 and the R400 measurement tier. | R603 | ⛔ Planned |
| R608 | Software Onboarding & Tutorial Design | In-app tutorial/tooltip/guided-first-run patterns; when embedded guidance beats a manual (the `00-training-basics` step-script pattern). | R604, R606 | ⛔ Planned |

**Status: 0 of 8 topics authored — tier scaffolded 2026-07-04, authoring not yet begun.** Per
MSTR-007 §6 the tier index is authored before its topic documents; this index is that step. Topic
authoring belongs to the `02-research-training-pedagogy` skill and must meet the full
`docs/research/10-sources-and-methodology.md` bar from the first draft (inline citations at claim
sites, `### Sources` per `##` section with live URL + Wayback snapshot + accessed date, §2 Scope
per MSTR-007 §4.2, `Last Reviewed`/`Primary Sources Consulted` frontmatter) — this tier starts
*after* the GAP-13 lesson, so it never enters the uncited state R400/R500 had to be remediated
out of. Do not treat any R600 topic as an available dependency for an FS/IP or manual-review pass
until its row here reads ✅.

**Anchor literature the topics are expected to draw from** (named here so the authoring skill
starts from real sources, not vibes): Gagné's *Conditions of Learning*; Merrill's First Principles
of Instruction; Knowles on andragogy; Sweller's cognitive load theory; Ericsson on deliberate
practice; Carroll's *The Nurnberg Funnel* (minimalist documentation); Kirkpatrick's four levels +
its wargaming critiques; Fanning & Gaba on simulation debriefing; the military AAR literature
(TC 25-20); van Merriënboer's 4C/ID for complex-skill training. Each claim still requires its own
verified citation at authoring time — this list is a starting bibliography, not a citation.
