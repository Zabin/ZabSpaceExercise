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
| [R601](R601-instructional-systems-design.md) | Instructional Systems Design | ADDIE/backward-design applied to simulator training: from training objective to manual module and vignette rung. | — | ✅ |
| [R602](R602-adult-learning-theory.md) | Adult Learning Theory | Andragogy/self-direction for the professional-military-education audience; implications for manual tone, length, and sequencing. | R601 | ✅ |
| [R603](R603-simulation-based-learning-and-debriefing.md) | Simulation-Based Learning & Debriefing | What makes simulation training transfer; debriefing/AAR practice as the payoff step (ties to MSTR-001 §1 item 3). | R601 | ✅ |
| [R604](R604-cognitive-load-and-scaffolding.md) | Cognitive Load & Scaffolding in Complex-System Training | Managing intrinsic/extraneous load when teaching a many-panel operator console; fidelity/`ops_fidelity` as a scaffolding dial. | R602 | ✅ |
| [R605](R605-learning-path-and-progression-design.md) | Learning-Path & Progression Design | Novice→expert sequencing, part-task training, and mastery gating — the theory behind `training/16-learning-path.md`'s rung structure. | R601, R604 | ✅ |
| [R606](R606-minimalist-and-procedural-documentation.md) | Minimalist & Procedural Documentation | Carroll's minimalism, task-oriented manuals, and role-scoped procedure layers — the craft behind the cell manuals' shape. | R602 | ✅ |
| [R607](R607-assessment-of-learning-in-wargames.md) | Assessment of Learning in Wargames & Exercises | Measuring whether training worked without corrupting the exercise; connects to DOM-002 and the R400 measurement tier. | R603 | ✅ |
| [R608](R608-software-onboarding-and-tutorial-design.md) | Software Onboarding & Tutorial Design | In-app tutorial/tooltip/guided-first-run patterns; when embedded guidance beats a manual (the `00-training-basics` step-script pattern). | R604, R606 | ✅ |

**Status: 8 of 8 topics authored — tier closed 2026-07-04 (same-day scaffold-to-authored, per the
user's explicit "author the R600 topics" request).** Every topic carries §2 Scope (MSTR-007 §4.2),
inline citations at every substantive claim, a `### Sources` subsection per cited `##` section (live
URL + Wayback calendar-view link + accessed date), and `Last Reviewed`/`Primary Sources Consulted`
frontmatter, per `docs/research/10-sources-and-methodology.md`.

**Verification-pass caveat (read before citing a topic as fully audited).** This authoring pass ran
in a session where direct `WebFetch` of external sources was blocked by the environment's egress
policy (a 403 organizational-policy denial, not a transient error — see each topic's own
"Verification note"). Every claim is grounded in a real, named source corroborated across ≥2
independent live web-search results (author, title, venue, year, and core finding all cross-checked
against multiple listings), which is solid grounding but is **not** the same as the fetch-and-confirm
adversarial verification pass `10-sources-and-methodology.md` §5.3 describes as this corpus's normal
quality gate. That formal verification pass — fetching each cited URL, confirming the claim, and
spot-checking Wayback availability — is an explicit open item, tracked as backlog **BL-0028**, and
should run in a session with unrestricted WebFetch before this tier is treated as fully audited to
the same standard as R100/R200/R300/R400/R500.

**Anchor literature the topics actually cite** (the starting bibliography named at scaffolding time,
now backed by real per-topic citations — see each topic's own `### Sources`): Gagné's and Merrill's
instructional-design frameworks and Wiggins & McTighe's backward design (R601); Knowles' andragogy
(R602); Fanning & Gaba on simulation debriefing and the U.S. Army's TC 25-20 AAR doctrine (R603);
Sweller's cognitive load theory and Wood/Bruner/Ross's scaffolding concept (R604); Ericsson's
deliberate practice, van Merriënboer's 4C/ID, and Bloom's mastery learning (R605); Carroll's
*The Nurnberg Funnel* (R606); Scriven's formative/summative distinction, Kirkpatrick's four levels,
and Perla's wargaming-debrief practice (R607); Nielsen's progressive disclosure (R608).
