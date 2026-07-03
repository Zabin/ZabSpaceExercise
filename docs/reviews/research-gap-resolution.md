# Research Gap Resolution — Strategic Review Follow-Through

> **Status:** Resolution report — informational, non-binding. Does not modify any architecture,
> requirements, ADR, domain, feature, or implementation document.
> **Source:** Part 3 (Research Gap Analysis), [`docs/reviews/strategic-review-2026-07.md`](strategic-review-2026-07.md)
> (GAP-01 through GAP-13).
> **Method:** Every gap was checked against the existing encyclopedia (R100–R500), the `01-07`
> primers, and the domain/architecture documents named in the strategic review before any new
> content was written, per the classification the user requested: **already covered**,
> **partially covered**, or **genuinely missing**. New encyclopedia entries were authored only for
> genuinely-missing (or missing-at-the-relevant-depth) topics, using the two research skills whose
> scope covers this corpus: `02-research-ow-orbital-mechanics` (R1xx tier) and
> `02-research-doctrine-exercises` (R3xx tier). Gaps outside both skills' tier ownership, and gaps
> judged too large to responsibly bulk-author in one pass, are recorded as `⛔ Planned` index rows
> (the corpus's own index-before-content convention, MSTR-007 §6) rather than left undocumented.
> **Ground rules honored:** no file under `docs/architecture/`, `docs/requirements/`, `docs/adr/`,
> or `docs/domains/` was modified by this pass — verified by `git status` immediately before this
> document was written. "Affected architecture areas" / "Affected requirements" below name the
> areas a future authorized change would touch; they are not edits.

[↑ Docs index](../INDEX.md) · [Strategic review](strategic-review-2026-07.md)

---

## Summary table

| Gap | Topic | Classification | Resolution this pass | New topic |
|---|---|---|---|---|
| GAP-01 | Space environment & space weather operations | Genuinely missing | **Authored** | [R131](../research/encyclopedia/R131-space-environment-and-space-weather-operations.md) |
| GAP-02 | Debris environment evolution & post-event persistence | Partially covered | Deferred (extends R117, not a new topic) | — |
| GAP-03 | Commercial space ecosystem & contested commercial services | Partially covered | Deferred (`⛔ Planned` R320, extends R312) | — |
| GAP-04 | Cislunar / xGEO operations | Genuinely missing | Deferred (`⛔ Planned` R136) | — |
| GAP-05 | Space logistics: launch, reconstitution, servicing economics | Genuinely missing | Deferred (`⛔ Planned` R133) | — |
| GAP-06 | Attribution, signaling, and public messaging in space incidents | Genuinely missing | **Authored** | [R318](../research/encyclopedia/R318-attribution-confidence-and-public-messaging.md) |
| GAP-07 | Training transfer & simulation-based learning effectiveness | Out of scope | Not addressed — belongs to the R4xx tier, which neither invoked skill owns | — |
| GAP-08 | Adversary emulation fidelity & Red behavior validation | Partially covered | **Authored** (extends R308's principle with a method) | [R319](../research/encyclopedia/R319-red-behavior-validation-methodology.md) |
| GAP-09 | PNT warfare and navigation-denial operations | Genuinely missing | Deferred (`⛔ Planned` R134) | — |
| GAP-10 | Proliferated-constellation C2 and mesh operations | Genuinely missing | **Authored** | [R132](../research/encyclopedia/R132-proliferated-constellation-c2-and-mesh-operations.md) |
| GAP-11 | Distributed simulation & exercise interoperability | Genuinely missing | Not authored — judged an architecture-tier concern, not a clean R3xx research topic (see below) | — |
| GAP-12 | Ground-segment operations as contested terrain | Genuinely missing | Deferred (`⛔ Planned` R135) | — |
| GAP-13 | Corpus-wide sourcing & scope defect | Process defect, not a topic | Partially addressed (the 4 new topics meet the citation bar in full; systemic fix stays out of scope) | — |

**4 of 13 gaps closed with full new encyclopedia entries this pass; 5 recorded as tracked `⛔ Planned`
gaps; 1 (GAP-02) folded into an existing topic's future extension rather than a new row; 2 (GAP-07,
GAP-11) explicitly out of either invoked skill's tier ownership; 1 (GAP-13) is a process defect,
not a content gap, and is incrementally — not fully — addressed by this pass's own citation
discipline.**

---

## Gaps resolved this pass (new encyclopedia content)

### GAP-01 — Space environment & space weather operations

- **Classification:** Genuinely missing. No prior R1xx topic grounded storm-driven drag, RF
  scintillation, or SEU effects, or the attack-vs-environment telemetry disambiguation problem —
  confirmed by reading R110, R111, R121, R127 and finding no coverage.
- **Research added:** [R131 — Space Environment and Space Weather Operations](../research/encyclopedia/R131-space-environment-and-space-weather-operations.md)
  (new, ✅ Done). Covers storm-driven LEO drag physics, ionospheric scintillation's overlap with the
  EW-jam telemetry signature, NOAA's G/S/R severity-scale vocabulary as external corroboration,
  single-event-upset causation, and the real precedent for forecast-driven (not just reactive)
  storm posture changes.
- **Sources incorporated:** NOAA/NWS Space Weather Prediction Center ("Geomagnetic Storms,"
  "Ionospheric Scintillation," "NOAA Space Weather Scales"); Orbital Radar ("How Solar Storms
  Affect Satellites"); Space.com and Baruah et al. (*Space Weather*, 2024) on the 2022-02-03/08
  Starlink drag-loss event; Wikipedia's single-event-upset overview (Tier D, used only as a
  navigational pointer to the peer-reviewed SEU-mechanism literature it surveys, per methodology
  §2's Tier D rule).
- **Affected architecture areas (named, not modified):** `engine/perturbations.py`
  (`atmospheric_density`/`drag_acceleration`/`secular_drag_decay` exist but are not yet called from
  the propagator or connected to `world.space_weather`); `engine/telemetry.py` (does not currently
  read `world.space_weather` at all, despite `session/manager.py`'s inline comment describing an
  intended "FSW errors climb in 'severe'" linkage — a genuine implementation gap this topic
  identifies precisely); GDS-04 Domain Model (no distinct "environmental state" concept alongside
  `Access Window`/effect entities).
- **Affected requirements (named, not modified):** No dedicated FR currently exists for
  environmental telemetry effects; the topic is relevant to whatever FR cluster eventually governs
  `engine/telemetry.py`'s signature model (the existing attack-signature requirements this topic's
  disambiguation problem sits beside) if one is authored. No FR was edited.

### GAP-06 — Attribution, signaling, and public messaging in space incidents

- **Classification:** Genuinely missing at the operational-craft level. R303/R304 cover the general
  deterrence/escalation theory and both cite R213 (Signaling Theory) for the underlying mechanism,
  but none of the three addresses the applied question of attribution-confidence-building and
  public-messaging choice for a real space incident. Confirmed by reading R303, R304, and R213
  directly — none names attribution-confidence thresholds or messaging-as-response.
- **Research added:** [R318 — Attribution Confidence and Public Messaging in Space Incidents](../research/encyclopedia/R318-attribution-confidence-and-public-messaging.md)
  (new, ✅ Done). Grounds the real 2015/2018 Luch (Olymp-K) proximity-operations incidents (US
  diplomatic protest over Intelsat 7/901 proximity, French public "space espionage" accusation over
  Athena-Fidus) as the doctrinal precedent for messaging as a deliberate response tier distinct
  from technical/kinetic response, and identifies that `engine/effects.py`'s `attribution_signal`
  side effect — a real, already-implemented graded-confidence mechanism (0.95/0.5/0.15 for
  overt/ambiguous/covert) — is computed on every effect resolution but currently has **no consumer
  anywhere in the codebase** (verified by grep: only `effects.py` itself references
  `attribution_signal`).
- **Sources incorporated:** CSIS Aerospace Security Project, "Unusual Behavior in GEO: Luch
  (Olymp-K)"; SpaceNews, "Russian Satellite Maneuvers, Silence Worry Intelsat." Both flagged
  `*Single source (Tier B/C corroboration only)*` per methodology §3 because full-page WebFetch
  verification 403'd during this session — the claims rest on cross-corroborated search-index
  retrieval (CSIS, SpaceNews, The Space Review, Militarnyi independently converging on the same
  dates/distances/officials) rather than a single unverified source, but full verification is
  flagged as pending a future session with WebFetch access.
- **Affected architecture areas (named, not modified):** `engine/effects.py`
  (`EffectTemplate.attribution` field and the `attribution_signal` side effect — fully implemented,
  zero consumers); GDS-04 Domain Model (no entity models the attribution-signal concept at all,
  despite it being a real, computed engine output); GDS-01 ConOps §5's ROE/adjudication workflow
  description (no mention of a messaging-response step).
- **Affected requirements (named, not modified):** FR-1410 ("Five-D's effect resolution with
  reversibility and attribution," `docs/requirements/01-functional-requirements.md`) already
  specifies attribution signal as a postcondition/output of effect resolution — this research
  explains *why* that output currently has no consumer and what a real consuming feature should
  look like, but does not add, remove, or reword FR-1410.

### GAP-08 — Adversary emulation fidelity and Red behavior validation

- **Classification:** Partially covered. R308 (Red Teaming Methodology) already supplies the
  qualitative doctrinal-plausibility principle in full — confirmed by reading R308 directly, which
  correctly states Red must be neither passive nor optimal/omniscient and must retain structural
  independence. What R308 does not supply, and what GAP-08 specifically named, is a *checkable
  method* for validating whether a given `redai.py` preset (or future AI-Red) actually satisfies
  that principle.
- **Research added:** [R319 — Red Behavior Validation Methodology](../research/encyclopedia/R319-red-behavior-validation-methodology.md)
  (new, ✅ Done). Extends R308 with: sequence-level behavioral-fidelity comparison against
  historical adversary action patterns as a checkable method distinct from expert impression;
  "getting Red right" as a named, recurring professional-wargaming failure category; the
  distinction (and potential conflict) between fidelity validation and playability/balance
  validation; and — the topic's sharpest finding — that AI-Red's current ground-truth read
  (`RedDoctrine._blue_satellites()`/`_red_assets()`/`_first_vulnerable()` reading `self.mgr.world`
  directly, confirmed in ADR-0024) is not merely a realism defect but a **precondition failure**
  for any future fidelity-validation effort: comparing an information-privileged decision-maker to
  a historical record of information-constrained real adversaries is not a meaningful comparison
  regardless of method sophistication.
- **Sources incorporated:** US Naval Institute *Proceedings*, "War Gaming Must Get Red Right"
  (January 2017) — flagged `*Single source (Tier C)*` per methodology §3 (WebFetch to the live URL
  403'd; the citation rests on title/venue/date retrieved via search index, corroborated by
  R308's own independently-sourced Zenko (2015) and UK MOD Handbook (2021) material converging on
  the same failure mode).
- **Affected architecture areas (named, not modified):** `session/redai.py`'s `RedDoctrine` class
  (the ground-truth-read precondition problem this topic names, already tracked as a gap in
  ADR-0024 — this research adds the validation-methodology argument for *why* that gap should be
  sequenced before any fidelity-validation effort, not a new finding of the gap itself); DOM-005
  Validation Framework (currently `⛔ Planned` — this topic supplies grounding for the Red-fidelity
  portion of DOM-005's eventual scope, per DOM-005 §1's own verification-vs-validation distinction).
- **Affected requirements (named, not modified):** FR-9110 ("AI-Red issues Planned Activities per a
  doctrine preset") already documents the ground-truth-read trade-off as an accepted v1 limitation
  citing ADR-0024 and `FUTURE-WORK.md` §1 — this research does not change FR-9110's priority or
  scope, but supplies the validation-methodology argument that would apply once (or if) the
  epistemic-parity fix FR-9110 references is undertaken.

### GAP-10 — Proliferated-constellation C2 and mesh operations

- **Classification:** Genuinely missing. Confirmed by reading R108 directly — it explicitly scopes
  itself to the ≤3-sat, individually-operated model (ADR-0019) and states "no fleet-level
  aggregation primitive exists yet," which is a statement of the *current* model, not research
  grounding for what changes above that threshold.
- **Research added:** [R132 — Proliferated-Constellation C2 and Mesh Operations](../research/encyclopedia/R132-proliferated-constellation-c2-and-mesh-operations.md)
  (new, ✅ Done). Grounds the real US Space Development Agency Proliferated Warfighter Space
  Architecture (PWSA) Tranche 1 — 150+ satellites, optical inter-satellite mesh links, dedicated
  operations centers — as the concrete precedent for what changes: the operator's unit of command
  shifting from satellite to layer, exception-based health rollup (NASA's REACH system) replacing
  per-asset drill-down, onboard autonomy absorbing routine tasking, and tasking contention becoming
  a layer-capacity problem rather than a per-satellite queue. Explicitly research-first per its own
  scope — it does not design the constellation-aggregation feature `FUTURE-WORK.md` §4 defers.
- **Sources incorporated:** Space Development Agency, "Proliferated Warfighter Space Architecture —
  Tranche 1" factsheet and "Tranche 1 Transport Layer" factsheet (Tier A, primary program-office
  sources); US GAO-25-106838 ("Laser Communications: Space Development Agency Should Create Links
  Between...", Tier A/B government report); Cognitive Space and NASA Spinoff (fleet-automation/
  health-monitoring precedent, the former already cited by R108 and re-cited here for a distinct
  claim).
- **Affected architecture areas (named, not modified):** ADR-0019 (the sizing-guideline decision
  this topic's real-world scale comparison is read against — not superseded, since ADR-0019's own
  "Alternatives Considered" already correctly defers aggregation to v2); GDS-01 §10 (the sizing
  guideline text); GDS-04 Domain Model (`Asset` entity has no mesh-adjacency or layer-membership
  concept); `engine/entities.py` (no layer/mesh object).
- **Affected requirements (named, not modified):** No dedicated FR currently governs constellation
  sizing or aggregation (the ≤24/≤3 figures live in ADR-0019 and GDS-01 §10, not in the FR
  document) — this research would inform a future FR if constellation aggregation is authorized as
  a feature, but no existing FR was found or touched.

---

## Gaps deferred (tracked as `⛔ Planned`, not authored this pass)

Per MSTR-007 §6's authoring-cadence rule and §7's "gaps found this way are tracked... not silently
left out" instruction, five gaps are recorded as `⛔ Planned` index rows in `R100-index.md` /
`R300-index.md` rather than fully authored in the same pass — each is a genuine coverage gap, but
authoring all thirteen gaps' worth of full, properly-cited, 3-8-page topics in one sitting would
have produced shallow content, which is precisely the corpus discipline (index-before-content,
incremental tier authoring) the review's own GAP-13 finding warns against repeating.

| Planned ID | Topic | Tier | Closes | Depends on |
|---|---|---|---|---|
| R133 | Space Logistics: Launch, Reconstitution, and Servicing Economics | R100 | GAP-05 | R112 |
| R134 | PNT Warfare and Navigation-Denial Operations | R100 | GAP-09 | R109, R110 |
| R135 | Ground Segment Operations as Contested Terrain | R100 | GAP-12 | R107, R116 |
| R136 | Cislunar and xGEO Operations | R100 | GAP-04 | R101, R102 |
| R320 | Commercial Space Actors and Strategic Ambiguity | R300 | GAP-03 | R312 |

**Affected architecture areas (named, not modified), by gap:**

- **GAP-04 (cislunar/xGEO):** `engine/geometry.py` (GMST ECI↔ECEF frames are Earth-centric only),
  `engine/propagator.py` (the `Propagator` seam ADR-0009 designed for exactly this kind of
  fidelity substitution, but no cislunar implementation exists behind it), GDS-03 Architecture
  (subsystem decomposition assumes Earth-centric regimes throughout).
- **GAP-05 (space logistics):** GDS-04 Domain Model (no launch/reconstitution entity; `Asset` loss
  is currently terminal within a session), `engine/entities.py` (`AssetResources` models Δv as
  non-renewable).
- **GAP-09 (PNT warfare):** `engine/buscommands.py` (`pnt.set_integrity`/`pnt.report_status` verbs
  are implemented per `FUTURE-WORK.md` §3 but have no dedicated research grounding).
- **GAP-12 (ground segment as contested terrain):** GDS-04 Domain Model (`GroundSite` entity has no
  attack-surface property), `engine/cyber.py` (`ground_segment` is one of five `VECTORS` but is not
  grounded against ground-segment-specific doctrine).
- **GAP-03 (commercial actors):** GDS-02 System Context (external-systems table has no commercial-
  provider category), GDS-04 Domain Model (no "commercial/third-party actor" entity).

**Affected requirements:** none of the five deferred gaps map to an existing FR-xxxx; each would
motivate a *new* FR only if and when a consuming feature is authorized. No requirements document
was touched.

---

## Gaps not authored — out of scope of the two invoked skills

### GAP-07 — Training transfer & simulation-based learning effectiveness

**Classification:** Genuinely missing, and explicitly **out of scope for both
`02-research-ow-orbital-mechanics` (R1xx) and `02-research-doctrine-exercises` (R3xx)** — this gap
belongs to the R4xx (Research Methods) tier per MSTR-007 §3's tier table ("what justifies
assessment/validation work, DOM-002/DOM-005"), which neither invoked skill owns. No R4xx-authoring
skill exists in this project's `.claude/skills/` directory as of this pass.

- **Affected architecture areas (named, not modified):** DOM-002 (Assessment Framework, `⛔
  Planned`), DOM-005 (Validation Framework, `⛔ Planned`) — both already flagged as the project's
  least-mature tier in the strategic review's finding W2; this gap is a direct contributor to that
  immaturity.
- **Affected requirements:** none — no FR currently depends on training-transfer evidence existing.
- **Recommendation (not an action taken):** commission this research either by extending one of the
  two existing skills' mandate, authoring a new R4xx-scoped skill, or manual authoring outside the
  skill workflow — consistent with the strategic review's own recommendation R9.

### GAP-11 — Distributed simulation & exercise interoperability

**Classification:** Genuinely missing, and judged to sit at the boundary between exercise design
(`02-research-doctrine-exercises`'s nominal scope) and systems architecture rather than cleanly inside
either. Federation standards (HLA/DIS/SISO), LVC integration patterns, and what they would demand
of the `SessionAPI` seam are primarily an architecture/interface question — evaluating them well
requires reading `docs/architecture/03-architecture.md` and `docs/architecture/09-api-specification.md`
against a federation model, which is design-synthesis work, not doctrine/wargaming-theory research.
Forcing this into an R3xx research topic risked producing content that read like an architecture
proposal wearing a research-topic's citation format — worse than leaving the gap explicitly named
for the right skill.

- **Affected architecture areas (named, not modified):** GDS-02 System Context (external-interfaces
  table has no federation/LVC entry), GDS-03 Architecture (the `SessionAPI` single-seam design,
  ADR-0003, was not evaluated against federation compatibility), `docs/FUTURE-WORK.md` §1 ("push
  deltas instead of polling" — the nearest existing deferred item, not the same question but
  architecturally adjacent).
- **Affected requirements:** none — no FR currently addresses external-system federation.
- **Recommendation (not an action taken):** route this gap through the `architecture-design-
  synthesis` skill (GDS-06–10 authoring, already a standing priority per `CLAUDE.md`) rather than
  a research-encyclopedia topic, consistent with the strategic review's own GAP-11 entry noting
  "examine *before* any transport rework, not after."

---

## GAP-13 — Corpus-wide sourcing & scope defect

**Classification:** Process/hygiene defect, not a topic-coverage gap — already self-flagged in
every tier's own index file (R100–R500) before this pass began, per the strategic review's own
framing.

**Resolution this pass:** Partial, incidental. All four topics authored in this pass (R131, R132,
R318, R319) meet the full citation bar from creation — inline citations at the claim site, a
`### Sources` subsection with live + Wayback + accessed-date per URL, and explicit single-source
flagging where full verification could not be completed (R318, R319 — both WebFetch-403'd during
authoring and flagged accordingly rather than silently presented as fully verified). This does not
reduce the *existing* debt in R200/R400/R500 (uncited) or the pre-existing R100/R300 topics
(already cited per their own tier remediation passes, per each index's own status notes) — it only
avoids adding to it. The systemic fix across R200/R400/R500 remains out of scope of both invoked
skills (R500 in particular is R5xx tier, owned by neither) and is tracked as the strategic review's
own **recommendation R1** (Immediate priority), not resolved by this pass.

**Affected architecture areas / requirements:** none — this is a documentation-corpus hygiene
matter with no architecture or requirements surface.

---

## What changed, in one list

**New files (4):**
- `docs/research/encyclopedia/R131-space-environment-and-space-weather-operations.md`
- `docs/research/encyclopedia/R132-proliferated-constellation-c2-and-mesh-operations.md`
- `docs/research/encyclopedia/R318-attribution-confidence-and-public-messaging.md`
- `docs/research/encyclopedia/R319-red-behavior-validation-methodology.md`

**Modified files (index + bidirectional cross-links only, all under `docs/research/encyclopedia/`):**
`R100-index.md`, `R300-index.md`, `R108`, `R110`, `R111`, `R118`, `R121`, `R127`, `R213`, `R303`,
`R304`, `R308` — each modified only to add the new topics to an existing `Referenced By` field or
to add the new index rows, per the corpus's bidirectional cross-linking convention (MSTR-007 §4.7,
research-tier skill workflow step 6).

**Not modified:** anything under `docs/architecture/`, `docs/requirements/`, `docs/domains/`,
`docs/features/`, `docs/implementations/`, `ROADMAP.md`, `CLAUDE.md`, or `spacesim/` — this pass is
research-tier content only, per both invoked skills' explicit scope boundaries and this document's
own instructions.

---

*This report is informational and non-binding, matching the convention of
[`strategic-review-2026-07.md`](strategic-review-2026-07.md) and
[`architecture-review.md`](architecture-review.md). Any finding above that the project's
maintainers accept as actionable should be resolved through the corpus's own mechanisms (Open
Questions, ADRs, `ROADMAP.md`, `FUTURE-WORK.md`, or a future authorized authoring pass for the
`⛔ Planned` rows) — not by further edits to this file.*
