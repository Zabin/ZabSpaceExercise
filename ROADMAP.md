# Documentation Roadmap

Single authoritative tracker for **every document this project produces or has planned** — what
exists, what depends on what, and what's still open. Humans and future Claude Code sessions
should read this file first to answer "what's done, what's in flight, what's left" without
re-deriving it from `git log`, `docs/FUTURE-WORK.md` §12, or scanning the docs tree.

**Update this file whenever a document's status changes.** Finish a doc → flip it to ✅ (note the
commit if useful, the research-expansion tables already do this). Start one → flip it to 🚧.
Identify a new doc that needs writing → add a row with an ID, its dependencies, and `⛔ Planned`.
Don't let this file drift from reality — it exists so nobody has to re-read everything to find
out.

## Status legend

| Symbol | Meaning |
|---|---|
| ✅ | Done — written, current, matches the implementation/research it describes. |
| 🚧 | In progress — drafted but incomplete, or mid-subsection under the §12.5.0 cadence. |
| ⛔ | Planned — identified as needed, not yet started. |
| ♻️ | Living — intentionally never "done"; updated continuously as the project evolves. |
| 🖼️ | Generated — produced by a script from live data, not hand-authored prose. |
| 🅿️ | Planned but **not yet authorized** — scoped in detail, no green light to start (the §12 research expansion). |

`Depends on` lists the IDs whose content this document assumes, cites, or must stay consistent
with — not a build order. The **Build Spec wins on any conflict** regardless of dependency arrows.

---

## Root guides

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RT-README | Project overview & quick start | `README.md` | — | ✅ |
| RT-CLAUDE | Durable agent guide | `CLAUDE.md` | BS-00, all themes | ♻️ |
| RT-MEMORY | Rolling design-decision log | `memory.md` | — | ♻️ |
| RT-ROADMAP | This file | `ROADMAP.md` | all IDs below | ♻️ |
| RT-INDEX | Master docs router | `docs/INDEX.md` | all theme indexes | ✅ |
| RT-PLAN | Documentation IA rationale | `docs/DOCUMENTATION-PLAN.md` | RT-INDEX | ✅ |
| RT-FUTURE | Cross-cutting v1.1+ TODO (also the source of the §12 research-expansion plan tracked below) | `docs/FUTURE-WORK.md` | — | ♻️ |

## Audit reports (point-in-time deliverables, not living docs)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| AU-01 | Full-codebase audit, June 2026 (research/docs/engine/security/tests, 5 streams) | `docs/AUDIT-2026-06.md` | all themes | ✅ |
| AU-02 | Commands audit — order/verb realism, probability mechanics, form UX | `docs/AUDIT-2026-06-COMMANDS.md` | AU-01, DS-13 | ✅ |
| AU-03 | UI + TT&C audit — panel layout, power model, telemetry, target picker | `docs/AUDIT-2026-06-UI-TTC.md` | AU-02 | ✅ |

## Theme: Build Spec (legacy reference, superseded — `docs/build-spec/`)

> **Superseded in its entirety by `docs/architecture/` (the GDS-00…GDS-10 ladder)**, per
> `CLAUDE.md`'s "Authoritative source & reading order." No longer "binding v1 spec" — modules below
> are legacy reference, citable for orientation only, not as a tie-breaker.

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| BS-00 | Build Spec index | `build-spec/INDEX.md` | BS-01…BS-08 | ✅ |
| BS-01 | Context & scope (§0–4) | `build-spec/01-context-and-scope.md` | — | ✅ |
| BS-02 | Requirements & operations (§5–6) | `build-spec/02-requirements-and-operations.md` | BS-01 | ✅ |
| BS-03 | Architecture & data (§7–8) | `build-spec/03-architecture-and-data.md` | BS-01, BS-02 | ✅ |
| BS-04 | NFRs, milestones & risks (§9–12) | `build-spec/04-nfr-milestones-and-risks.md` | BS-03 | ✅ |
| BS-05 | Workflows & state machines (§13–14) | `build-spec/05-workflows-and-state-machines.md` | BS-03 | ✅ |
| BS-06 | Test plan & schedule (§15–17 Pt.3) | `build-spec/06-test-plan-and-schedule.md` | BS-04 | ✅ |
| BS-07 | Operator console spec (§16 Pt.4) | `build-spec/07-operator-console.md` | BS-05 | ✅ |
| BS-08 | Mock SSN spec (§17 Pt.4) | `build-spec/08-ssn.md` | BS-03 | ✅ |

> `BS-04`'s milestone table still reads through P7; the LAN-multiplayer work that shipped as P8
> (`RT-FUTURE` §1) post-dates the last build-spec edit. Updating §10's milestone table to record
> P8 as done is a small open edit — add it as `BS-04-REV` if/when someone does that pass.

## Theme: Design corpus (the *how* — `docs/design/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| DS-00 | Design index | `design/INDEX.md` | DS-01…DS-15 | ✅ |
| DS-01 | Architecture overview | `design/01-architecture-overview.md` | BS-03 | ✅ |
| DS-02 | Tech stack recommendation | `design/02-tech-stack-recommendation.md` | DS-01 | ✅ |
| DS-03 | Simulation engine | `design/03-simulation-engine.md` | DS-01 | ✅ |
| DS-04 | Data model | `design/04-data-model.md` | DS-01 | ✅ |
| DS-05 | Cell interfaces (Red/Blue/White) | `design/05-cell-interfaces.md` | DS-04 | ✅ |
| DS-06 | White Cell controls | `design/06-white-cell-controls.md` | DS-05 | ✅ |
| DS-07 | API & networking | `design/07-api-and-networking.md` | DS-01, DS-04 | ✅ |
| DS-09 | GUI principles & UX | `design/09-gui-principles.md` | DS-05 | ✅ |
| DS-10 | SDA 3D viewer | `design/10-sda-3d-viewer.md` | DS-09 | ✅ |
| DS-11 | Command planning & tasking | `design/11-command-planning-and-tasking.md` | DS-04, BS-05 | ✅ |
| DS-12 | Safe-mode loop | `design/12-safe-mode-loop.md` | DS-04 | ✅ |
| DS-13 | Operator command catalog | `design/13-operator-command-catalog.md` | DS-04, DS-11 | ✅ |
| DS-14 | Delta-V economy | `design/14-delta-v-economy.md` | DS-03 | ✅ |
| DS-15 | Worked asset templates | `design/15-worked-asset-templates.md` | DS-04, DS-13 | ✅ |

> The LAN multiplayer transport (`RT-FUTURE` §1) shipped as HTTP polling against the existing
> FastAPI server rather than the `WebSocketSession` stub — `DS-07` describes the seam but has not
> been revised to describe the polling implementation actually shipped. Flag as `DS-07-REV` if
> someone picks that up; not currently planned.

## Theme: Research corpus (the *why* — `docs/research/`)

### Current corpus (8 files, live)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RS-00 | Research index | `research/INDEX.md` | RS-01…RS-07, RS-1.0 | ✅ |
| RS-01 | Western doctrine | `research/01-doctrine-western.md` | — | ✅ *(Tier 1 expansion landed, commit `a4c5780`, 289 lines / 48 cites — see RS-1.1; cross-linked to encyclopedia)* |
| RS-02 | Non-Western doctrine | `research/02-doctrine-non-western.md` | RS-01 | ✅ *(Tier 1 expansion landed, commit `25b3b17`, 217 lines / 57 cites — see RS-1.2; cross-linked to encyclopedia)* |
| RS-03 | Counterspace taxonomy (the 5 D's) | `research/03-counterspace-taxonomy.md` | RS-01, RS-02 | ✅ *(Tier 1 expansion landed, commit `b39c24f`, 821 lines / 147 cites — see RS-1.3; cross-linked to encyclopedia)* |
| RS-04 | Orbital mechanics primer | `research/04-orbital-mechanics-primer.md` | — | ✅ *(Tier 1 expansion landed, commits `dde9739..14c2454`, 822 lines / 204 cites — see RS-1.4; cross-linked to encyclopedia)* |
| RS-05 | Mission types & their counters | `research/05-mission-types-and-counters.md` | RS-03, RS-04 | ✅ *(Tier 1 expansion landed, commit `2794958`, 360 lines / 61 cites — see RS-1.5; cross-linked to encyclopedia)* |
| RS-06 | Bus & payload operations | `research/06-bus-and-payload-operations.md` | RS-04 | ✅ *(Tier 1 expansion landed, commit `6c17e04`, 674 lines / 99 cites — see RS-1.6; cross-linked to encyclopedia)* |
| RS-07 | Legal norms & ROE | `research/07-legal-norms-and-roe.md` | RS-03 | ✅ *(Tier 1 expansion landed, commits `469c8e8..cd37fe2`, 795 lines / 106 cites — see RS-1.7; cross-linked to encyclopedia)* |
| RS-10 | Sources & methodology (citation convention for the whole corpus) | `research/10-sources-and-methodology.md` | — | ✅ *(landed first, commit `968c4be`, 363 lines — see RS-1.0; cross-linked to encyclopedia)* |

### Research encyclopedia (`research/encyclopedia/`, R100-R600, 68 authored + 8 planned topics + 6 tier indexes)

> **Tracking gap fixed in this revision.** This file claims to be "the single authoritative
> tracker for every document this project produces" (top of file), but until now it carried zero
> per-tier rows for the encyclopedia — only the `(cross-linked to encyclopedia)` parenthetical on
> RS-01…RS-10 above. The encyclopedia's own `INDEX.md`/`R*00-index.md` files were the only place
> tracking it, and they claimed "✅ Done" / "fully authored" without ever applying RS-10's citation
> convention to themselves. Both gaps are fixed below.

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RE-00 | Encyclopedia index | `research/encyclopedia/INDEX.md` | RE-100…RE-500 | 🚧 *(re-audited this revision; flips tier status table from ✅ to 🚧, documents the two systemic defects below)* |
| RE-100 | Tier R100 — Space Operations Foundation (37 topics authored, 0 planned — *this row was stale at 30 before this revision; the aggregate "68 authored" count in this section's header above predates R131-R137 too and is not otherwise reconciled by this pass*) | `research/encyclopedia/R100-index.md` | RS-04, RS-05, RS-06 | 🚧 *(37/37 authored topics closed. **R137** (Bus and Payload Configuration Parameter Catalog) authored 2026-07-05 — a completeness/navigation index of every bus-subsystem and payload-type configuration parameter, cross-referenced to whichever topic characterizes it, grounding `docs/pipeline/backlog.md` `BL-0052` (Vignette Creator); surfaces the `weather`/`mw` `BEAM_MODES` coverage gap plus four smaller candidate gaps. Same-day, **R101/R107/R109/R110/R111/R112/R134** extended with realistic parameter-range grounding for the same `BL-0052` need (TLE format, ground-station siting, weather/missile-warning sensor characteristics, SATCOM bandwidth, EPS power budgets, Δv budgets, PNT accuracy). Prior: **R130** (Downlink Operations and Data Return) closed the one `engine/orders.py` action verb (`downlink`) R103/R107/R114 each disclaimed covering; **R129** (SIGINT Collection and Geolocation Accuracy) closed the 2026-06-27 re-audit gap on `engine/sigint.py`)* |
| RE-200 | Tier R200 — Decision Sciences (14 topics) | `research/encyclopedia/R200-index.md` | MSTR-003 | 🚧 *(14/14 authored; 14/14 missing §2 Scope; 0/14 cite-compliant)* |
| RE-300 | Tier R300 — Military Analysis (12 topics) | `research/encyclopedia/R300-index.md` | RS-01, RS-02, RS-07 | 🚧 *(12/12 authored; 12/12 missing §2 Scope; 0/12 cite-compliant — doctrinal/legal claims in this tier are the highest-stakes uncited content in the corpus)* |
| RE-400 | Tier R400 — Research Methods (13 topics) | `research/encyclopedia/R400-index.md` | DOM-002, DOM-005 | ✅ *(13/13 authored; 13/13 have §2 Scope; 13/13 cite-compliant — GAP-13 closed 2026-07-02)* |
| RE-500 | Tier R500 — Future Operations (9 topics) | `research/encyclopedia/R500-index.md` | DOM-008 | ✅ *(9/9 authored; 9/9 have §2 Scope; 9/9 cite-compliant — GAP-13 closed 2026-07-02)* |
| RE-600 | Tier R600 — Training Pedagogy & Instructional Design (8 topics) | `research/encyclopedia/R600-index.md` | MSTR-001 §2, MSTR-003 | ✅ *(authored 2026-07-04: 8/8 topics — Instructional Systems Design, Adult Learning Theory, Simulation-Based Learning & Debriefing, Cognitive Load & Scaffolding, Learning-Path & Progression Design, Minimalist & Procedural Documentation, Assessment of Learning in Wargames, Software Onboarding & Tutorial Design — each with §2 Scope + full citations from first draft, never entering the uncited state R400/R500 were remediated out of; formal WebFetch verification pass open, BL-0028, since this session's WebFetch was policy-blocked)* |

**Status:** R400 and R500 (22 topics) closed GAP-13 remediation 2026-07-02 — both now carry the
mandatory §2 Scope section and full inline-citation + `### Sources`-subsection coverage per RS-10
(`research/10-sources-and-methodology.md`), grounded in Tier A/B sources (NIST standards, DoDI
5000.61, the Belmont Report, ECSS/NASA/DARPA/DoD primary sources, and foundational peer-reviewed
methods literature — see each tier index's closing status paragraph for the full source list). The
remaining tiers' status above (RE-200, RE-300) may be stale relative to this revision — R300's own
index (`R300-index.md`) already self-reports fully closed as of 2026-07-01/02, which this row has
not been reconciled against; a full ROADMAP re-audit against each tier's own index remains
outstanding and is not part of the R400/R500 GAP-13 remediation this revision covers.

### 🅿️ Planned: research corpus 10× expansion (`RT-FUTURE` §12 — scoped, not yet authorized)

A 25-target-file expansion across four priority tiers, organized into six content tracks
(doctrine, counterspace systems, orbital physics, mission sets, ops/legal/history,
cross-cutting). **Tier 1 is the only tier authorized to start** — it's the corpus's own citation
backfill, sequenced first because it locks the methodology (`RS-10`) that every later file
follows. Tiers 2–4 are fully scoped (lit-review tasks, analysis tasks, line-count targets) but
need an explicit go-ahead before work begins, per `RT-FUTURE` §12.1.

**Tier 1 — citation backfill + methodology (9 files; gates Tiers 2–4):**

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RS-1.0 | Sources & methodology — citation convention, first deliverable | `research/10-sources-and-methodology.md` | — | ✅ Landed (commit `968c4be`) |
| RS-1.1 | `01-doctrine-western.md` ~3× expansion (USSF Spacepower, AFDP 3-14, JP 3-14, allied doctrine) | same file, in place | RS-1.0 | ✅ Landed (commit `a4c5780`) |
| RS-1.2 | `02-doctrine-non-western.md` ~3× expansion (CASI, post-2024 PLA reorg, Hendrickx) | same file, in place | RS-1.0, RS-1.1 | ✅ Landed (commit `25b3b17`) |
| RS-1.3 | `03-counterspace-taxonomy.md` ~3× expansion | same file, in place | RS-1.0 | ✅ Landed (commit `b39c24f`) — structural exemplar for the rest of the cadence |
| RS-1.4 | `04-orbital-mechanics-primer.md` ~2× expansion | same file, in place | RS-1.0 | ✅ Landed (commits `dde9739..14c2454`) |
| RS-1.5 | `05-mission-types-and-counters.md` ~1.5× (depth deferred to Tier 2 Track D) | same file, in place | RS-1.0, RS-1.3 | ✅ Landed (commit `2794958`) |
| RS-1.6 | `06-bus-and-payload-operations.md` ~2× expansion | same file, in place | RS-1.0 | ✅ Landed (commit `6c17e04`) |
| RS-1.7 | `07-legal-norms-and-roe.md` ~2× expansion | same file, in place | RS-1.0, RS-1.3 | ✅ Landed (commits `469c8e8..cd37fe2`) |
| RS-1.8 | `research/INDEX.md` regenerated for post-expansion taxonomy | `research/INDEX.md` | RS-1.0…RS-1.7 | ✅ Landed — added the missing `10-sources-and-methodology.md` row |

**Tier 2 — per-mission and per-actor deep-dives (6 new files):**

| ID | Document | Path (new) | Depends on | Status |
|---|---|---|---|---|
| RS-2.1 | ISR (EO/SAR) deep-dive — Maxar/Planet/Capella, NRO KH-program history, NIIRS, TPED | `research/05a-isr-eo-sar.md` | RS-1.5 | ⛔ Planned (authorized) |
| RS-2.2 | SATCOM/PNT deep-dive — WGS/AEHF/Milstar, GPS IS-GPS-200E flex power, Galileo/GLONASS/BeiDou | `research/05b-satcom-pnt.md` | RS-1.5 | ⛔ Planned (authorized) |
| RS-2.3 | SIGINT/MW/weather/SDA deep-dive — Trumpet/Mercury/Mentor, SBIRS, GOES-R MDS, SSN tasking | `research/05c-sigint-mw-wx-sda.md` | RS-1.5 | ⛔ Planned (authorized) |
| RS-2.4 | China deep-dive — 2024 PLA SSF→ASF reorg, SoS doctrine, 36th Test Base | `research/02a-china-deep-dive.md` | RS-1.2 | ⛔ Planned (authorized) |
| RS-2.5 | Russia deep-dive — VKS/RVSN, EW Troops (Bylina/Tirada-2/Pole-21), Tobol | `research/02b-russia-deep-dive.md` | RS-1.2 | ⛔ Planned (authorized) |
| RS-2.6 | Emerging actors — India, Iran, DPRK, Israel, commercial counterspace | `research/02c-emerging-actors.md` | RS-1.2 | ⛔ Planned (authorized) |

**Tier 3 — counterspace systems and physics (8 new files):**

| ID | Document | Path (new) | Depends on | Status |
|---|---|---|---|---|
| RS-3.1 | DA-ASAT systems — SC-19/DN-3, Nudol/A-235, SM-3, PDV-Mk2 | `research/03a-da-asat-systems.md` | RS-1.3 | ⛔ Planned (authorized) |
| RS-3.2 | Co-orbital/RPO systems — SJ-21/15, Burevestnik, Olymp-K/Luch-2, GSSAP, MEV-1/2 | `research/03b-coorbital-rpo.md` | RS-1.3 | ⛔ Planned (authorized) |
| RS-3.3 | EW/jamming — CCS Block 10.2, Tirada-2/Pole-21/Bylina, Tobol, AEHF ECCM, J/S analysis | `research/03c-ew-jamming.md` | RS-1.3 | ⛔ Planned (authorized) |
| RS-3.4 | Directed energy — Sokol-Eshelon, Peresvet, Zimu-1, optical hardening | `research/03d-directed-energy.md` | RS-1.3 | ⛔ Planned (authorized) |
| RS-3.5 | Cyber — Viasat KA-SAT incident reconstruction, SPARTA TTPs, ROSAT/TDRS history | `research/03e-cyber.md` | RS-1.3 | ⛔ Planned (authorized) |
| RS-3.6 | Nuclear/EMP — Starfish Prime, Soviet K-series tests, OST Art. IV (deferred to v2) | `research/03f-nuclear-emp.md` | RS-1.3 | ⛔ Planned (authorized) |
| RS-3.7 | Propagator fidelity — Kepler+J2 vs SGP4 vs high-precision validation | `research/04a-propagator-fidelity.md` | RS-1.4 | ⛔ Planned (authorized) |
| RS-3.8 | Debris & conjunction — NASA ORDEM/ESA MASTER, Cosmos 1408 vs FY-1C persistence | `research/04b-debris-and-conjunction.md` | RS-1.4 | ⛔ Planned (authorized) |

**Tier 4 — operations, legal, history, forward-looking (5 deliverables):**

| ID | Document | Path (new) | Depends on | Status |
|---|---|---|---|---|
| RS-4.1 | Ground segment — AFSCN, TDRSS, AWS Ground Station, KSAT/ATLAS/Viasat-RTE | `research/06a-ground-segment.md` | RS-1.6 | ⛔ Planned (authorized) |
| RS-4.2 | Incident record — dated catalog of named counterspace incidents (PME instructor reference) | `research/07a-incident-record.md` | RS-1.7, RS-3.x | ⛔ Planned (authorized) |
| RS-4.3 | Commercial & allied — Starlink/Kuiper/OneWeb proliferation, Five Eyes SST, non-state actors | `research/08-commercial-and-allied.md` | RS-2.x | ⛔ Planned (authorized) |
| RS-4.4 | Emerging tech — optical ISLs, software-defined payloads, on-orbit refueling | `research/09-emerging-tech.md` | RS-2.x | ⛔ Planned (authorized) |
| RS-4.5 | (Shared lit-review workflow note for RS-4.3/RS-4.4 — overlapping proliferation research, not a standalone file) | — | RS-4.3, RS-4.4 | ⛔ Planned (authorized) |

> **Tiers 2-4 are authorized.** Tier 1 (RS-1.0 through RS-1.8) is fully landed. Work proceeds one
> tier at a time, per file, per the binding cadence below — see the "Open documentation work"
> section near the foot of this file for live in-progress status.
>
> **Authoring cadence (binding for all of Tier 1+):** one `deep-research` subsection at a time,
> ≤20k subagent tokens per invocation, integration pass per file, commit-and-push per subsection.
> See `RT-FUTURE` §12.5.0 — a "rewrite the whole file" brief blew the token budget in 3 of 4
> attempts under the old cadence.

## Theme: Architecture / Design Synthesis (the bridge — `docs/architecture/`)

New tier, defined by this revision (see "Phase 6-8 review" open question below, now resolved).
Sits between Domain+Research and Feature Specification in the `MSTR-005` §4 chain: Training
Objective → Domain → Research → **Design Synthesis** → Feature Specification → Implementation
Package → Code → Tests. Each `ADS-xxx` document has ten fixed sections (Executive Design Overview,
System Architecture, Domain Model, User Stories, Functional Requirements, Non-functional
Requirements, Constraints, Risks, Open Questions, Decision Log — `MSTR-005` §3a) and is produced by
the `03-architecture-design-synthesis` skill. Optional per `MSTR-005` §4 — only used for capability
clusters with real design tension; small/uncontested features skip straight to `FS-xxx`. Router:
[`architecture/INDEX.md`](docs/architecture/INDEX.md).

| ID | Document | Capability cluster | Owning domain | Status |
|---|---|---|---|---|
| ADS-00 | Architecture index | `architecture/INDEX.md` | — | ✅ |
| ADS-3500 | Role-Scoped Command Enforcement | `architecture/ADS-3500-role-scoped-command-enforcement.md` | (no owning DOM) | ✅ Authored (2026-07-05) — the first `ADS-xxx` in this project |
| ADS-5100A | Vignette Creator — Authoring Session & UI Architecture | `architecture/ADS-5100A-vignette-creator-session-and-ui.md` | (no owning DOM) | ✅ Authored (2026-07-05) |
| ADS-5100B | Vignette Creator — Typed Parameter Schemas & Per-Cell ROE Enforcement | `architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md` | (no owning DOM) | ✅ Authored (2026-07-05) |

**ADS-3500** resolves two Open Questions [`FS-116`](docs/features/FS-116-role-scoped-command-catalog.md)
(`FEAT-3500`) surfaced: extends the operator-command interface to carry a `seat` identifier
(amending `INT-0004`/`INT-0006`'s concrete realization) and classifies every `DEFENSE_VERBS` verb
individually as `bus` or `payload` (v1.1, per the project owner's direction that there is no third
"defense" role-scope category — six are `bus`, two — `def.harden`/`def.set_deception_mode` — are
`payload`). Authored via Workflow B since `GDS-09` (the ladder level that would eventually formally
own interface contracts) remains scaffold-only and gated behind `GDS-06`-`08`.

**ADS-5100A/B** synthesize the Vignette Creator (`docs/pipeline/backlog.md` `BL-0052`, folding in
`BL-0051`'s seat-count/matrix UI) — a large, distinct White-Cell authoring feature anchored to
`FEAT-5100`, split by capability seam per this tier's own size discipline: **5100A** covers the
authoring-session architecture (resolving `CR-11`) and UI surfaces (JSON view, 2D/3D preview,
TLE/lat-long/asset entry, asset menu, seat/role matrix); **5100B** covers the two Domain Model
extensions the UI surfaces but which are independently significant — typed per-payload-type/bus
parameter sub-schemas and real per-cell ROE enforcement.

### Global ladder (`GDS-00`…`GDS-10`, scaffolded this revision, content not yet authored)

A single, global, top-to-bottom design-synthesis ladder for the whole project, distinct from the
per-cluster `ADS-xxx` table above. **Strictly gated**: `GDS-(N+1)` cannot start until `GDS-N` is
authored *and* has merged in whatever existing-corpus content overlaps it (see
`architecture/INDEX.md` §1's gating rule). Scaffolded as stub files with metadata blocks and merge
gates; no level has been authored yet.

| ID | Document | Path | Merges from | Status |
|---|---|---|---|---|
| GDS-00 | Vision | `architecture/00-vision.md` | MSTR-001 | ✅ Authored, merge gate closed |
| GDS-01 | Concept of Operations | `architecture/01-concept-of-operations.md` | build-spec/01, build-spec/04 §11, build-spec/05 §13-14, training/05, training/07 | ✅ Authored, merge gate closed |
| GDS-02 | System Context | `architecture/02-system-context.md` | build-spec/01 | ✅ Authored, merge gate closed |
| GDS-03 | Architecture | `architecture/03-architecture.md` | design/01 | ✅ Authored, merge gate closed |
| GDS-04 | Domain Model | `architecture/04-domain-model.md` | design/04 (entity/relationship portion) | ✅ Authored, merge gate closed |
| GDS-05 | Functional Requirements | `architecture/05-functional-requirements.md` | build-spec/02 §5-6 | ✅ Authored, merge gate closed (supersedes build-spec/02 §5-6) |
| GDS-06 | Non-functional Requirements | `architecture/06-non-functional-requirements.md` | build-spec/04 §9 | ⛔ Planned (scaffold only) |
| GDS-07 | Data Model | `architecture/07-data-model.md` | design/04 (schema portion) | ⛔ Planned (scaffold only) |
| GDS-08 | UI Architecture | `architecture/08-ui-architecture.md` | design/09, design/05, design/10 | ⛔ Planned (scaffold only) |
| GDS-09 | API Specification | `architecture/09-api-specification.md` | design/07 | ⛔ Planned (scaffold only) |
| GDS-10 | Requirements Traceability Matrix | `architecture/10-requirements-traceability-matrix.md` | *(net-new — no counterpart)* | ⛔ Planned (scaffold only) |

**Next:** GDS-00 through GDS-05 are authored with merge gates closed. As of this revision, the
entire `docs/architecture/` ladder is declared authoritative over `docs/build-spec/` **in full**,
not just module-by-module as levels close their gates (see `CLAUDE.md` and `architecture/INDEX.md`
for the supersession declaration). GDS-06–10 remain scaffold-only and now carry added urgency:
until each is authored, its topic has no authoritative content at all (the corresponding
build-spec module is legacy reference, not a binding fallback). Author GDS-06 (Non-functional
Requirements, merging `build-spec/04-nfr-milestones-and-risks.md` §9) next, per the gate.

**Strategic review disposition (2026-07):** [`reviews/strategic-review-2026-07.md`](docs/reviews/strategic-review-2026-07.md)
was dispositioned in full by [`reviews/architecture-update.md`](docs/reviews/architecture-update.md)
(new — see RT-FUTURE §13 for the deferred-recommendation tracking that produced). GDS-00 through
GDS-04 each received a "Strategic review reconciliation" amendment (versions bumped, no merge gate
reopened); two new ADRs were added (`ADR-0030` AI-determinism doctrine, `ADR-0031` governance-record
consistency); a new living document,
[`architecture/strategic-assumptions-register.md`](docs/architecture/strategic-assumptions-register.md)
(RT-STRAT-REG, ♻️ Living), consolidates the review's A1–A11 assumption set.
`architecture-update.md` itself left `docs/requirements/` untouched (out of its six-document
scope, and no recommendation required a requirements-baseline change at that pass). A follow-up
requirements-tier pass, [`reviews/requirements-update-report.md`](docs/reviews/requirements-update-report.md)
(new), independently confirmed that finding — no numbered `FR-1xxx`/`NFR-1xxx` requirement was
added or modified — but added seven Candidate Requirements (`CR-12`–`CR-18`) and one Candidate NFR
(`CNFR-07`) mirroring the architecture tier's new not-built candidate components/concepts, updated
the traceability matrix accordingly, and corrected stale pre-supersession "build spec wins"
language independently duplicated in `docs/requirements/01`/`02`'s own header notes (the same
defect `ADR-0031` fixed in `architecture/00-vision.md` §7, but outside that document's scope).

**DOM-002/004/005 backfill (2026-07):** a second follow-up requirements-tier pass, closing
`docs/feature-planning/05-feature-review.md` Finding F-01, ran `04-requirements-engineering` against
DOM-002 (Assessment)/DOM-004 (Research)/DOM-005 (Validation) — the three domains grounding
FS-201/FS-202/FS-301 with no prior requirement at all. Found that DOM-002/FS-201's automated
rubric computation conflicts with Accepted ADR-0017 (no automated scoring/assessment mechanism in
v1) and DOM-004/FS-301's dedicated research-export interface directly conflicts with Accepted
ADR-0029 (existing raw AAR/event-log export already deemed sufficient; a dedicated interface
explicitly considered and rejected). **Zero new baselined `FR-1xxx`/`NFR-1xxx` requirements were
added** — three new Candidate Requirements (`CR-19`–`CR-21`) were added instead, and DOM-005
yielded no new leaf at all (validation methodology, not a system capability). Full analysis:
[`reviews/requirements-domain-backfill-report.md`](docs/reviews/requirements-domain-backfill-report.md).

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RT-STRAT-REG | Strategic Assumptions Register | `architecture/strategic-assumptions-register.md` | GDS-01, ADR-0030 | ♻️ |

## Theme: Feature Specifications (the *what* — `docs/features/`)

Phase 4 of the documentation-driven-development expansion (MSTR-005 §4 chain: Training Objective →
Domain → Research → **Feature Specification** → Implementation Package → Code → Tests). Each
`FS-xxx` describes what a capability must do, with no implementation detail (MSTR-005 §5 rule 4).
Router: [`features/feature-index.md`](docs/features/feature-index.md).

| ID | Document | Path | Owning domain | Status |
|---|---|---|---|---|
| FS-00 | Feature index | `features/feature-index.md` | — | ✅ |
| FS-101 | Mission Planning | `features/FS-101-mission-planning.md` | DOM-001 | ✅ |
| FS-102 | Command Scheduling | `features/FS-102-command-scheduling.md` | (R103-grounded) | ✅ |
| FS-103 | Custody Management | `features/FS-103-custody-management.md` | DOM-009 | ✅ |
| FS-104 | SDA Tasking | `features/FS-104-sda-tasking.md` | DOM-009 | ✅ |
| FS-105 | Spacecraft Operations | `features/FS-105-spacecraft-operations.md` | DOM-001, DOM-007 | ✅ |
| FS-106 | White Cell Dashboard *(v2.0, narrowed)* | `features/FS-106-white-cell-dashboard.md` | DOM-003 | ✅ |
| FS-107 | After Action Review | `features/FS-107-after-action-review.md` | DOM-001, DOM-003 | ✅ |
| FS-108 | Inject Authoring *(candidate)* | `features/FS-108-inject-authoring.md` | DOM-003 | ⛔ Planned (authorized) |
| FS-109 | Multiplayer / LAN Session Transport | `features/FS-109-multiplayer-session-transport.md` | DOM-003 §6 | ✅ |
| FS-110 | Save & Resume | `features/FS-110-save-and-resume.md` | DOM-003 §6 | ✅ |
| FS-111 | AI-Red Doctrine Automation | `features/FS-111-ai-red-doctrine-automation.md` | DOM-009, DOM-008 | ✅ |
| FS-112 | Classification Banner | `features/FS-112-classification-banner.md` | DOM-003 | ✅ (build unverified) |
| FS-113 | Observer Read-Only Access | `features/FS-113-observer-read-only-access.md` | (no owning DOM) | ✅ (build unverified) |
| FS-114 | Hot-Seat Hand-Off Screen-Blank Menu | `features/FS-114-hot-seat-handoff.md` | (no owning DOM) | ✅ (build unverified) |
| FS-115 | Session Setup: Vignette Selection & Seat Assignment | `features/FS-115-session-setup.md` | DOM-003 | ✅ (build unverified) |
| FS-116 | Role-Scoped Command Catalog & Assignment Scoping | `features/FS-116-role-scoped-command-catalog.md` | (no owning DOM) | ✅ Ready for implementation planning (v1.2 — both Open Questions closed via ADS-3500 v1.1; per-verb DEFENSE_VERBS classification corrected) |
| FS-201 | Competency Assessment | `features/FS-201-competency-assessment.md` | DOM-002 | ✅ |
| FS-202 | Rubric Authoring *(candidate)* | `features/FS-202-rubric-authoring.md` | DOM-002 | ⛔ Planned (authorized) |
| FS-301 | Research Analytics | `features/FS-301-research-analytics.md` | DOM-004, DOM-005 | ✅ |

FS-108 and FS-202 are intentionally lighter-weight stubs (not full specs) — both are marked
"(candidate)" in their owning domain document and require explicit user authorization (MSTR-006 §3)
before promotion to a full spec or any Implementation Package work.

**FS-106 split (2026-07), per `docs/feature-planning/05-feature-review.md` Finding F-03:** v1.0
bundled the White Cell facilitator UI with three architecturally distinct capabilities, each now
its own document — FS-109 (multiplayer/LAN session transport, ADR-0014/0015/0026), FS-110
(save/resume, ADR-0022), and FS-111 (AI-Red doctrine automation, ADR-0021/0024/0030). FS-106 v2.0
retains god-view/view-as, inject authoring/firing, clock/pacing control authority (trigger surface
only), and manual adjudication. **`IMP-106A`/`IP-1060` (below) were written against FS-106's prior,
broader scope and have not yet been reconciled against this split** — each new document's own Risks
section flags this as an open follow-on task, not resolved by the split itself. Vignette selection
(FR-4110) and seat-to-role assignment (FR-4210) remain uncovered by any Feature Specification —
confirmed, not newly introduced, by this split (see FS-106 v2.0's own Scope section).

**F-02/F-10 closure (2026-07):** FS-112 (Classification Banner), FS-113 (Observer Read-Only
Access), FS-114 (Hot-Seat Hand-Off Screen-Blank Menu), and FS-115 (Session Setup: Vignette
Selection & Seat Assignment) newly authored — four Must-priority baselined FRs (FR-4510, FR-6510,
FR-6610, FR-4110/FR-4210) that had zero presence in any prior `FS-xxx` document. Unlike the FS-106
split, these four had no prior narrative description anywhere in the corpus to verify against —
each document explicitly flags its own **build status as unverified** and is ready to hand to an
Implementation Package if confirmed unbuilt, or needs only an RTM-citation closure if confirmed
already shipped.

**Next:** Phase 5 (Implementation Packages, `docs/implementations/`) is complete (below), but see
the FS-106-split note above for its now-stale scope alignment. FS-112/113/114/115's build-status
verification is now done and each has an Implementation Package
(`IP-1120`/`IP-1130`/`IP-1140`/`IP-1150`/`IP-1151` — see the Implementation Packages theme below).
Phase 6-8 (Consistency/Dependency/Traceability review, MSTR-006 §7) is also complete (see the
dedicated theme section below), predating this split and these four new specs/packages.

**FS-116 authored (2026-07-05), closing a release-blocking gap:** `11-release-readiness`'s
[release assessment](reviews/release-assessment-fs-tracked-baseline.md) found `FEAT-3500`
(Role-Scoped Command Catalog & Assignment Scoping) — Must-priority, Release-1-bucketed — had **zero
owning Feature Specification and zero implementation anywhere in the codebase**, despite the release
plan's own text characterizing its RTM `UNASSIGNED` cells as "a traceability gap, not new
development." `FS-116` is the new spec closing that gap (`FR-3510`/`FR-3520`), authored per the
project owner's explicit Path-A choice (implement, rather than descope). v1.0 carried two Open
Questions blocking `07-implementation-planning`; both are **closed as of v1.1** via
[`ADS-3500`](architecture/ADS-3500-role-scoped-command-enforcement.md) — the first `ADS-xxx`
authored in this project — which (1) extends the operator-command interface with an optional `seat`
identifier (preserving `GDS-01`'s multi-seat concurrency model rather than narrowing it) and (2)
classified `DEFENSE_VERBS` by role scope. **`IP-1160` was then planned against v1.1; the project
owner subsequently gave further direction that there is no third "defense" role-scope category** —
`ADS-3500` v1.1 (self-revised) and `FS-116` v1.2 now classify each `DEFENSE_VERBS` entry
individually as `bus` or `payload` by which subsystem it actually mutates (six `bus`, two
`payload` — `def.harden`/`def.set_deception_mode`). **`IP-1160` v1.1 carries the matching
correction** — including reversing its own v1.0 plan to "fix" `app.js`'s already-correct
`def.harden: "payload"` tag, and fixing the one real bug the audit found (`def.set_deception_mode`
silently defaulting to `"bus"`). `FS-116`/`IP-1160` remain ready for `07-implementation-planning`.

## Theme: Feature Planning — `05-feature-decomposition` skill output (`docs/feature-planning/`)

New, 2026-07 — an audit of the document hierarchy found only 11 `FS-xxx` documents against a
94-leaf-citation (49 unique baselined leaves) `docs/requirements/` corpus, with the RTM carrying no
FR→FS column and every existing FS's own "Requirements Implemented" section reading "None
identified." The `05-feature-decomposition` skill was run against the approved requirements baseline
(`docs/requirements/01`–`03`) to produce a planning-grain Feature Catalog upstream of `FS-xxx`. Its
`FEAT-xxxx` rows are a **different artifact** from this theme's own `FS-xxx` documents (see
`docs/feature-planning/05-feature-review.md`'s mapping note) — not a replacement or renumbering.

| ID | Document | Path | Status |
|---|---|---|---|
| — | Feature Planning index | `feature-planning/INDEX.md` | ✅ |
| — | Release Plan | `feature-planning/01-release-plan.md` | ✅ |
| — | Epic Catalog (`EP-1000`–`EP-10000`, 10 Epics) | `feature-planning/02-epic-catalog.md` | ✅ |
| — | Feature Catalog (`FEAT-1100`–`FEAT-10200`, 38 Features) | `feature-planning/03-feature-catalog.md` | ✅ |
| — | Feature Dependency Graph | `feature-planning/04-feature-dependency-graph.md` | ✅ |
| — | Feature Review | `feature-planning/05-feature-review.md` | ✅ |

**Key findings:** all 49 baselined FR + 23 baselined NFR leaves are traced to exactly one Feature
each (36 total); three Features (Classification Banner, Observer Read-Only Access, Hot-Seat
Hand-Off) have zero presence in any existing `FS-xxx` document, confirming the motivating audit;
`FS-106-white-cell-dashboard.md` bundles ten catalog Features across three Epics and is flagged as
oversized; DOM-002/004/005 (Assessment/Research/Validation) have shipped `FS-201`/`FS-301` with no
corresponding FR/NFR baseline entry at all, a requirements-tier gap this catalog cannot close
itself. The reconciliation of "36 Features today" against the ~50–80 expected once Candidate
Requirements, Candidate NFRs, and the strategic review's Future Concepts/Gaps are baselined is
worked out in full in `05-feature-review.md`'s closing section.

**Update (2026-07):** Finding F-03 (split `FS-106`) is done — see FS-106/FS-109/FS-110/FS-111 in the
Feature Specifications theme above. **Findings F-02 and F-10 are also done** — FS-112/FS-113/
FS-114/FS-115 newly authored, each with build status explicitly flagged unverified.

**Update (2026-07):** `IMP-106A`/`IP-1060` reconciliation is done — IP-1060 narrowed to v2.0,
IP-1090/IP-1100/IP-1110 authored (see the Implementation Packages theme above).

**Update (2026-07):** Build-status verification for FS-112/113/114/115 against the actual
`spacesim/` source tree is **done** (`07-implementation-planning`'s Tranche 1,
`docs/implementation/01-technical-work-breakdown.md`) — each Feature was found partially or fully
built, none matching its spec exactly. Five packages now exist:
`IP-1120`/`IP-1130`/`IP-1140`/`IP-1150`/`IP-1151` (see the Implementation Packages theme below).

**Update (2026-07):** Finding F-01 is **fully resolved, in two stages**. Stage 1 (`requirements-
engineering` against DOM-002/004/005 — `reviews/requirements-domain-backfill-report.md`): zero new
baselined FR/NFR; `CR-19`/`CR-20`/`CR-21` added instead, two blocked on an ADR-0017/ADR-0029
conflict this pass discovered. Stage 2 (direct project-owner decision, same session): `ADR-0032`
narrows `ADR-0017`; `ADR-0033` supersedes `ADR-0029`; `CR-19`/`CR-20` promoted to baselined
`FR-10110`/`FR-10210` (new Epic `EP-10000`, Features `FEAT-10100`/`FEAT-10200`, in the Feature
Catalog above). `IP-2010` returned to `READY`; `IP-3010` remained `BLOCKED` on `IP-2010` reaching
`COMPLETE` (unrelated to the now-resolved ADR conflict) — as of this writing, both that dependency
and `IP-3010`'s own MSTR-006 §3 authorization have since cleared (see the Implementation Packages
theme below for current status). `CR-21` remains an active Candidate.
`05-feature-review.md`'s own reconciliation table still showed FS-201/FS-301 mapping to
"none — see Finding F-01" after this stage — a stale back-reference, since `FEAT-10100`/`FEAT-10200`
now own exactly the requirements those two specs already implement. Fixed directly (mechanical,
same class of fix as the Phase 7 dependency reconciliation below): the table now reads
FS-201→FEAT-10100, FS-301→FEAT-10200, with an "Update (2026-07)" note explaining no new FS document
was needed — the existing specs already fully describe what their new owning Feature names.

**Next:** verify build status for FS-112/113/114/115; separately, baseline as many of the remaining
`CR-01–18,21`/`CNFR-01–07` as the project owner authorizes for the ones with no ADR-level blocker
(Finding F-04), then re-run this skill's Step 0 incrementally against the delta.

## Theme: Implementation Packages (the *how* — `docs/implementation/packages/`, canonical; `docs/implementations/`, superseded)

Phase 5 of the documentation-driven-development expansion (MSTR-005 §4 chain: ... → Feature
Specification → **Implementation Package** → Code → Tests). Each `IP-xxxx` describes architecture,
data model, files, tasks, tests, Definition of Done, and rollback considerations in prose/
pseudocode, never literal committed code (MSTR-006 §8). Situations per package **at authoring
time**: as-built, independently `VERIFIED` (FS-101 through FS-107, FS-109, FS-110, FS-111);
as-built, `COMPLETE` pending verification (FS-114, and FS-115's FR-4110 slice); partially built /
gap-closing forward design (FS-112); and fully forward design, capability not yet implemented,
coding work not yet authorized by this documentation per MSTR-006 §3 (FS-201, FS-301, FS-113, and
FS-115's FR-4210 slice). **All of these have since moved**: FS-115's FR-4110 slice (`IP-1150`) and
FS-114 (`IP-1140`) are now `VERIFIED`; FS-201/FS-113/FS-115's FR-4210 slice/FS-301
(`IP-2010`/`IP-1130`/`IP-1151`/`IP-3010`) were all authorized and implemented (`COMPLETE`, pending
their own `09-package-verification`) — see the status table below for current, not authoring-time,
status. FS-112/113/114/115 (new 2026-07) now have five
packages between them —
`IP-1120`/`IP-1130`/`IP-1140`/`IP-1150`/`IP-1151` — authored after a build-status verification
pass found each Feature partially or fully built (see `docs/implementation/
01-technical-work-breakdown.md` Tranche 1).
Router: [`implementation/packages/INDEX.md`](docs/implementation/packages/INDEX.md); sequencing/
dependency-graph/critical-path in [`implementation/00-master-build-plan.md`](docs/implementation/00-master-build-plan.md);
work-breakdown rationale in [`implementation/01-technical-work-breakdown.md`](docs/implementation/01-technical-work-breakdown.md).

**Canonical tier as of this revision.** `docs/implementation/packages/` (`IP-xxxx` IDs) supersedes
the prior `docs/implementations/` tier (`IMP-xxxA` IDs) in full — same underlying design content,
re-derived and re-verified against the current source tree under a different template/ID
scheme/location. The prior tier's files are retained (each carries a superseded-by banner) but are
no longer the document of record; see the Master Build Plan's "Relationship to the prior
`docs/implementations/` corpus" section for the full rationale.

| ID | Document | Path | FS | Situation | Status |
|---|---|---|---|---|---|
| IMPL-PLAN-00 | Master Build Plan (sequence, critical path, dependency graph, parallel opportunities) | `implementation/00-master-build-plan.md` | — | — | ✅ |
| IP-00 | Implementation Packages index | `implementation/packages/INDEX.md` | — | — | ✅ |
| IP-1010 | Mission Planning — dry-run preview & window/Δv display | `implementation/packages/IP-1010-mission-planning.md` | FS-101 | As-built | ✅ VERIFIED |
| IP-1020 | Command Scheduling — Order/OrderSystem lifecycle | `implementation/packages/IP-1020-command-scheduling.md` | FS-102 | As-built | ✅ VERIFIED |
| IP-1030 | Custody Management — Track confidence model | `implementation/packages/IP-1030-custody-management.md` | FS-103 | As-built | ✅ VERIFIED |
| IP-1040 | SDA Tasking — sensor tasking & SSN request lifecycle | `implementation/packages/IP-1040-sda-tasking.md` | FS-104 | As-built | ✅ VERIFIED |
| IP-1050 | Spacecraft Operations — bus/payload command & telemetry | `implementation/packages/IP-1050-spacecraft-operations-bus-payload.md` | FS-105 | As-built | ✅ VERIFIED |
| IP-1051 | Spacecraft Operations — effect resolution & console UX | `implementation/packages/IP-1051-spacecraft-operations-effects-console.md` | FS-105 | As-built | ✅ VERIFIED |
| IP-1060 | White Cell Dashboard — god-view, inject, clock-authority trigger & adjudication *(v2.0, narrowed)* | `implementation/packages/IP-1060-white-cell-dashboard.md` | FS-106 v2.0 | As-built | ✅ VERIFIED |
| IP-1070 | After Action Review — replay/scrub/branch-compare | `implementation/packages/IP-1070-after-action-review.md` | FS-107 | As-built | ✅ VERIFIED |
| IP-1090 | Multiplayer / LAN Session Transport — lazy clock, mutation locking, hot-seat/LAN sharing | `implementation/packages/IP-1090-multiplayer-session-transport.md` | FS-109 | As-built | ✅ VERIFIED |
| IP-1100 | Save & Resume — deterministic round trip & content/session split | `implementation/packages/IP-1100-save-and-resume.md` | FS-110 | As-built | ✅ VERIFIED |
| IP-1110 | AI-Red Doctrine Automation — doctrine-preset-driven Red activity generation | `implementation/packages/IP-1110-ai-red-doctrine-automation.md` | FS-111 | As-built | ✅ VERIFIED |
| IP-2010 | Competency Assessment — rubric computation | `implementation/packages/IP-2010-competency-assessment.md` | FS-201 | Forward design | ✅ VERIFIED (2026-07-04, `VR-2010` — two Medium findings against FS-201's own Acceptance Criteria scope, routed to `06-feature-specification`, not against this package) |
| IP-3010 | Research Analytics — multi-run export | `implementation/packages/IP-3010-research-analytics.md` | FS-301 | Forward design | ✅ VERIFIED (2026-07-04, run #12, `VR-3010` — `BL-0018`/`BL-0017` re-confirmed, no new findings) |
| IP-1120 | Classification Banner — wire render/export path to the vignette's classification value | `implementation/packages/IP-1120-classification-banner.md` | FS-112 | Partially built (gap-closing) | ✅ VERIFIED (2026-07-04, run #13, `VR-1120` — both documented deviations confirmed accurate, one Low informational finding) |
| IP-1130 | Observer Read-Only Access — designated read-only seat, server-side mutation rejection | `implementation/packages/IP-1130-observer-read-only-access.md` | FS-113 | Forward design | ✅ VERIFIED (2026-07-04, run #14, `VR-1130` — `BL-0011`'s predicted route-guard drift investigated, not yet materialized) |
| IP-1140 | Hot-Seat Hand-Off Screen-Blank Menu — blank/blur/resume overlay | `implementation/packages/IP-1140-hot-seat-handoff.md` | FS-114 | As-built (documented spec divergence, adjudicated) | ✅ VERIFIED (2026-07-03, `VR-1140` — FR-6610 trigger/menu divergence adjudicated **not satisfied**, High finding routed to `07-implementation-planning`) |
| IP-1150 | Session Setup: Vignette Selection & Parameter Tuning | `implementation/packages/IP-1150-vignette-selection.md` | FS-115 §FR-4110 | As-built | ✅ VERIFIED (2026-07-03, `VR-1150`) |
| IP-1151 | Session Setup: Seat-to-Role Assignment | `implementation/packages/IP-1151-seat-role-assignment.md` | FS-115 §FR-4210 | Forward design | ✅ VERIFIED (2026-07-04, run #15, `VR-1151` — `BL-0014`'s no-consumer finding independently re-derived, still true; one new Low finding) |
| IP-1160 | Role-Scoped Command Catalog & Assignment Scoping | `implementation/packages/IP-1160-role-scoped-command-enforcement.md` | FS-116 | Forward design | 🔴 BLOCKED (not authorized — MSTR-006 §3; every dependency already `VERIFIED`) |

FS-108/FS-202 have no Implementation Package (unauthorized candidates, MSTR-006 §3). **IP-1160 is
new (2026-07-05)**, closing `FEAT-3500`'s implementation gap that `11-release-readiness` found —
see the Master Build Plan's Tranche 2 note and `01-technical-work-breakdown.md` for the no-split
rationale.

**IP-1090/IP-1100/IP-1110 are new (2026-07, tranche 1)**, split out of IP-1060 v1.0 per
`docs/feature-planning/05-feature-review.md` Finding F-03, mirroring the FS-106 split — no new code
verification was performed, these three packages reorganize `IP-1060` v1.0's already-verified
citations under the new Feature boundaries. `docs/implementations/IMP-106A-white-cell-
dashboard.md` (superseded, frozen historical content) gained a forward-pointer note to the three
new packages without otherwise being altered.

**IP-1120/IP-1130/IP-1140/IP-1150/IP-1151 are new (2026-07, tranche 2)** — the first Implementation
Packages against FS-112/113/114/115, following the build-status verification pass noted above.

**Authorization update (2026-07-03):** the project owner reviewed every package gated on MSTR-006
§3 and authorized `IP-2010`, `IP-1130`, `IP-1120`, and `IP-1151` (recorded in
`docs/pipeline/pipeline-journal.md` run #2); `IP-3010` was **not** authorized this round.

**Verification update (2026-07-03):** `IP-1150` passed `09-package-verification`
([`VR-1150`](docs/implementation/verification/VR-1150-vignette-selection.md), the first
Verification Report this project has produced) and flipped to `VERIFIED` — full suite 490
passed/3 skipped, both permanent gates green, and a stale RTM cell (`FR-4110`'s `Test`/`Impl.
Package` columns) corrected. This cleared `IP-1120`/`IP-1151`'s sole blocking dependency; both
flip `BLOCKED → READY` (already authorized above).

**Implementation update (2026-07-03, runs #5–#8):** `IP-2010`, `IP-1120`, `IP-1130`, and `IP-1151`
were all implemented (`READY → COMPLETE`), each pending its own `09-package-verification` pass.

**Authorization update (2026-07-03, run #9):** `IP-3010` — the one package not authorized in the
round above — was subsequently authorized. Its `IP-2010`-reaching-`COMPLETE` dependency had already
cleared (run #5), so it flips `BLOCKED → READY`.

**Verification update (2026-07-03, run #9):** `IP-1140` passed `09-package-verification`
([`VR-1140`](docs/implementation/verification/VR-1140-hot-seat-handoff.md)) and flipped to
`VERIFIED` — full suite 559 passed/3 skipped, both permanent gates green, RTM `FR-6610` `Test`/
`Impl. Package` cells (were `UNASSIGNED`) corrected. **The package's documented FR-6610
trigger/menu divergence was adjudicated, not waived**: the shipped manual-button/auto-cycle
mechanism does not satisfy FR-6610's full intent — a High-severity finding, routed to
`07-implementation-planning` for a gap-closing package. **Risk-acceptance update (2026-07-04):**
the project owner explicitly accepted this risk rather than authorizing a gap-closing package
("I accept the risk of a cell not blanking the screen during handover as long as hot seat is an
option") — no further remediation planned unless hot-seat mode's availability is reconsidered.

**Implementation update (2026-07-04, run #10):** `IP-3010` was implemented (`READY → COMPLETE`) —
a new `spacesim/tools/` subpackage (`research_batch.run_batch()`, seeded-Monte-Carlo batch runner)
and `session/research_export.py` (`RunRecord` + CSV/JSON export extending `aar.export_csv()`'s
pattern), reading `session/assessment.py`'s already-computed rubric output once per run, never
reimplementing it. 7 new tests; full suite 566 passed/3 skipped, both permanent gates green.
Pending its own `09-package-verification` pass.

**Verification update (2026-07-04, run #11):** `IP-2010` passed `09-package-verification`
([`VR-2010`](docs/implementation/verification/VR-2010-competency-assessment.md)) and flipped to
`VERIFIED` — full suite 566 passed/3 skipped, both permanent gates green, RTM `FR-10110` cell
updated. **Two Medium findings**: FS-201's own Acceptance Criteria include a longitudinal
per-trainee report (already disclosed as deferred by the package itself) and self-assessment/
debrief-mode accessibility (not implemented, not flagged as excluded) — both routed to
`06-feature-specification` to reconcile FS-201's stated scope against what was actually built.

**Verification update (2026-07-04, run #12):** `IP-3010` passed `09-package-verification`
([`VR-3010`](docs/implementation/verification/VR-3010-research-analytics.md)) and flipped to
`VERIFIED` — full suite 566 passed/3 skipped (unchanged), both permanent gates green, RTM
`FR-10210` cell updated. `BL-0018` (schema-stability dependency on `IP-2010`) and `BL-0017`
(imprecise `tools/` precedent citation) both re-confirmed against the current tree. No new
findings. The `IP-2010 → IP-3010` critical-path chain is now `VERIFIED` end-to-end.

**Verification update (2026-07-04, run #13):** `IP-1120` passed `09-package-verification`
([`VR-1120`](docs/implementation/verification/VR-1120-classification-banner.md)) and flipped to
`VERIFIED` — full suite 566 passed/3 skipped, both permanent gates green, RTM `FR-4510`/`NFR-3100`
cells updated. Both documented Implementation Tasks deviations confirmed accurate, harmless,
in-scope. One Low, informational-only finding (a DoD-text naming imprecision).

**Verification update (2026-07-04, run #14):** `IP-1130` passed `09-package-verification`
([`VR-1130`](docs/implementation/verification/VR-1130-observer-read-only-access.md)) and flipped to
`VERIFIED` — full suite 566 passed/3 skipped, both permanent gates green, RTM `FR-6510` cell
updated. `BL-0011`'s predicted Observer route-guard maintenance-drift risk was investigated
directly against the current route table (not merely re-confirmed from the package's own text):
both routes added since IP-1130 shipped (`/roles/assign` from `IP-1151`, and IP-1130's own
`/observer/view` POST) remain protected, via a stricter White-Cell-only allowlist check in
`session/inprocess.py` rather than `_reject_observer`'s denylist — the predicted drift has not
materialized. One new Low finding (a test-coverage gap: neither route has an explicit
`cell="observer"` rejection test, though the underlying enforcement is confirmed correct by
reading).

**Verification update (2026-07-04, run #15):** `IP-1151` passed `09-package-verification`
([`VR-1151`](docs/implementation/verification/VR-1151-seat-role-assignment.md)) and flipped to
`VERIFIED` — full suite 566 passed/3 skipped, both permanent gates green, RTM `FR-4210` cell
updated. `BL-0014` (no role-based command-filtering consumer exists for the Role Assignment
records this package produces) was independently re-derived directly against the current tree, not
merely re-cited from the package's own text: `role_assignments` remains read only by
`staffing_report()`, and nothing landed since the package's implementation (run #8) introduces
role-based command authorization anywhere in the codebase — still true. One new Low finding, same
family as `BL-0023`: `assign_role`'s White-Cell-only gate is tested against `cell="blue"`, not
`cell="observer"` specifically.

**This closes the "iterate through all `09-package-verification`" sweep the user requested (runs
#11–#15).** `docs/implementation/00-master-build-plan.md`'s package table, dependency graph,
parallel-opportunity list, critical-path note, and summary statistics have been updated accordingly
(now 18 packages total: **18 `VERIFIED`**, 0 `COMPLETE`, 0 `READY`, 0 `BLOCKED` — every package in
this plan has reached `VERIFIED`, with `IP-1140` carrying a standing user-accepted-risk note rather
than an outstanding gap-closing package). The next stage-appropriate step for this tranche is
`10-integration-review`.

**Integration review (2026-07-04):** [`reviews/integration-review-18-package-tranche.md`](docs/reviews/integration-review-18-package-tranche.md)
reviewed all 18 packages as a set — full suite 566 passed/3 skipped, both permanent gates green,
no Critical/High findings, no behavioral or interface divergence found. Three documentation/
traceability-coherence findings: a Medium gap (5 of 7 tranche-2/forward-design features —
`IP-1120`/`IP-1130`/`IP-1151`/`IP-2010`/`IP-3010` — have no coverage anywhere in the per-cell
training manuals or `training/15-manual-traceability.md` §15.1, routed to
`08-training-manual-authoring`), and two Low package-doc/feature-index staleness items (`IP-1150`'s
own header still reads `COMPLETE`; `feature-index.md`'s FS-112–115 descriptions still say "build
status unverified"), both routed to `07-implementation-planning`/`06-feature-specification`. This
tranche is clear to proceed to `11-release-readiness` on functional grounds.

**Retro-verification sweep complete (2026-07-04, runs #18, #20–#29):** the integration review's
`BL-0004` finding (the 11 original as-built packages carried `VERIFIED` with no formal `VR-xxxx`
evidence) is now fully closed — the project owner chose to retro-verify all 11 rather than accept
the gap. `IP-1010` through `IP-1110` each received an independent `09-package-verification` pass
(see `docs/implementation/verification/INDEX.md`); **all 18 packages on the Master Build Plan now
carry a formal Verification Report.** Sweep results: 8 of 11 clean with only routine citation-drift
findings, 2 with one Medium finding each (`IP-1020`'s lifecycle-naming mismatch; `IP-1100`'s
overclaim that Role Assignments are persisted), `IP-1110` with zero findings — no Critical/High
finding anywhere in the sweep. The tranche's evidence base for `11-release-readiness` is now
complete.

**Training review (2026-07-05):** [`reviews/training-review-runs16-19-scope.md`](docs/reviews/training-review-runs16-19-scope.md)
independently reviewed the training-corpus scope runs #16/#19 touched (`training/02`, `12`, `13`,
`14`, `15`, `INDEX`) against shipped behavior — all Observer/classification/staffing/assessment/
research-batch prose claims confirmed accurate, playbook suite green (16/16), no Critical/High
findings. One Medium traceability finding: `WCM-1`/`BLU-1`/`RED-1` and `training/15` §15.1/§15.2
cite a nonexistent `spacesim/session/controller.py` for the fog-of-war boundary — the real file is
`spacesim/session/cells.py` — routed to `08-training-manual-authoring`.

### Superseded prior tier (`docs/implementations/`, `IMP-xxxA` IDs — retained, not deleted)

| ID | Document | Path | FS | Situation | Status |
|---|---|---|---|---|---|
| IMP-00 | Implementation index (now carries a supersession banner) | `implementations/INDEX.md` | — | — | ♻️ superseded |
| IMP-101A…IMP-107A/B | (7 as-built packages) | `implementations/IMP-*.md` | FS-101–107 | As-built | ♻️ superseded by IP-1010…IP-1070/1051 |
| IMP-201A | Competency Assessment — rubric computation design | `implementations/IMP-201A-competency-assessment.md` | FS-201 | Forward design | ♻️ superseded by IP-2010 |
| IMP-301A | Research Analytics — multi-run export design | `implementations/IMP-301A-research-analytics.md` | FS-301 | Forward design | ♻️ superseded by IP-3010 |

**Next:** Phase 6-8 (Consistency/Dependency/Traceability review, MSTR-006 §7) is complete (below).
Re-running that review against the new `docs/implementation/packages/` tier (rather than assuming
its findings carry over unchanged from the superseded `docs/implementations/` pass) is not yet
done — flagged here as an open item, not silently assumed equivalent.

## Theme: Phase 6-8 review (Consistency / Dependency / Traceability, MSTR-006 §7)

Scope: every document under `docs/master/`, `docs/domains/`, `docs/research/encyclopedia/`,
`docs/features/`, `docs/implementations/`, `docs/architecture/`, `docs/scenarios/` (MSTR-006 §5).

**Phase 6 — Consistency.** Scanned all 115 in-scope content documents (excludes the 13 `INDEX.md`/
tier-index router files, see open question below) for the required 7-field metadata block. All 115
have a complete block with a valid MSTR-006 §2 status symbol. No duplicate Document IDs. Two stale
status-claim wordings fixed (mechanical, not a judgment call — the text was simply out of date
after Phase 5 added the packages it was denying existed):
- `FS-201` / `FS-301`: each said "no Implementation Package exists yet"; this became false once
  IMP-201A/IMP-301A were authored in Phase 5. Reworded to state the package exists as design-only
  per MSTR-006 §3, not implementation-authorizing.
- `DOM-002`: said "no FS/IMP exist yet"; FS-201/FS-301/IMP-201A/IMP-301A all exist as documents.
  Reworded to "FS-201/FS-301 and their design-only IMP-201A/IMP-301A packages exist, but no code
  implements assessment in the simulator today" — preserving the true claim (no code) while fixing
  the false one (no documents).

**Phase 7 — Dependency.** Cross-checked every `Dependencies`/`Referenced By`/`Produces` ID against
the actual corpus: zero references to a nonexistent ID. Reconciled `Dependencies`/`Referenced By`
bidirectionally (MSTR-005 §5's "best-effort... reconciled at Phase 8" note) and found 12 genuine
one-directional gaps, all mechanical (the citing document's claim was correct; the cited document's
back-reference was simply never added) — fixed directly, no judgment call involved:
- `FS-101`/`FS-102`/`FS-103`/`FS-104`/`FS-105`/`FS-106`/`FS-107` each gained their `IMP-xxxA`/`B`
  package in `Referenced By` (the IMP packages' `Dependencies` already correctly cited the FS).
- `FS-201` gained `IMP-201A` and `FS-202`; `FS-301` gained `IMP-301A`.
- `DOM-002` gained `FS-107` (which cites DOM-002 §6); `DOM-003` gained `FS-107` (same).
- `MSTR-001` gained `MSTR-004`; `MSTR-002` gained `MSTR-007`; `MSTR-005` gained `MSTR-006`;
  `MSTR-006` gained `DOM-008` — each was already a real, stated `Dependencies` entry in the citing
  document, just missing from the cited document's back-reference list.

**Phase 8 — Traceability.** Walked the MSTR-005 §4 chain (Training Objective → Domain → Research →
FS → IMP → Code → Tests) for all 11 Feature Specifications:
- FS-101 through FS-107: every leg present. Each IMP package's code citations resolve to real files
  in `spacesim/` (verified by path existence check); each has at least one corresponding test module
  under `spacesim/tests/` (e.g. FS-101→`test_orders.py`/`test_validate_order.py`, FS-103→
  `test_custody.py`, FS-105→`test_bus.py`/`test_bus_commands.py`, FS-107→`test_aar.py`).
- FS-108/FS-202: chain stops at FS (⛔ Planned (authorized)) — no IMP, no code, no tests. Expected
  per MSTR-006 §3; not a defect.
- FS-201/FS-301: chain reaches IMP-201A/IMP-301A (design-only) and stops there — no code, no tests.
  Expected per their own Status annotations; not a defect.

> **Open question (`docs/architecture/` half resolved this revision):** at the time of the Phase
> 6-8 review, `docs/architecture/` and `docs/scenarios/` were both empty (no files, no git history)
> despite MSTR-006 §5 listing them as in-scope directories for the metadata-block requirement.
> `docs/architecture/` is now resolved per option (a) — it was aspirational MSTR-006 §5 scope, now
> given real content: the `ADS-xxx` Design Synthesis tier (`MSTR-005` §3a/§4,
> `docs/architecture/INDEX.md`, the theme table above), produced by the
> `03-architecture-design-synthesis` skill. It does not replace `docs/design/`, which stays the
> detailed "how" for architecture that exists or is being built — `ADS-xxx` is upstream of that,
> synthesizing domain+research inputs before a Feature Spec commits to a shape (`MSTR-005` §3a).
> `docs/scenarios/` remains unresolved — still empty, still unclear whether it should eventually
> receive content distinct from `docs/vignettes/`, or whether MSTR-005/MSTR-006 should drop that
> path. Left for the user to decide; no document was edited to resolve the `scenarios/` half.

> **Open question:** the 13 router/index files (`*/INDEX.md`, `R100-index.md` ... `R500-index.md`,
> `features/feature-index.md`) carry no metadata block at all, while MSTR-006 §5 says "every
> document in `master/`, `domains/`, ... opens with" the 7-field block. All 13 are internally
> consistent with each other (100% omit it, none partially comply), suggesting an unstated but
> consistently-applied convention that router/navigation pages are exempt. Flagged rather than
> silently resolved per MSTR-006 §6 — either MSTR-006 §5 should be amended to state the router
> exemption explicitly, or all 13 files should gain a block. No file was edited to resolve it.

## Theme: Training manual (`docs/training/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| TR-00 | Training index | `training/INDEX.md` | TR-01…TR-11 | ✅ |
| TR-01 | Install & run | `training/01-install-and-run.md` | BS-01 | ✅ |
| TR-02 | The interface at a glance | `training/02-interface.md` | TR-01, BS-07 | ✅ |
| TR-03 | First exercise (Vignette 1) | `training/03-first-exercise.md` | TR-02, VG-IDX | ✅ |
| TR-04 | Guided training vignette walkthrough | `training/04-guided-vignette.md` | TR-03 | ✅ |
| TR-05 | Core concepts | `training/05-core-concepts.md` | TR-02, BS-05 | ✅ |
| TR-06 | The full 19-vignette library at a glance | `training/06-the-vignette-library.md` | VG-IDX | ✅ |
| TR-07 | White Cell facilitation | `training/07-white-cell-facilitation.md` | DS-06 | ✅ |
| TR-08 | HTTP API reference | `training/08-http-api-reference.md` | DS-07 | ✅ |
| TR-09 | Troubleshooting & glossary | `training/09-troubleshooting-and-glossary.md` | — | ✅ |
| TR-10 | UI reference (all 14 panels) | `training/10-ui-reference.md` | BS-07, MAN-00 | ✅ |
| TR-11 | Per-vignette playbooks — how each cell completes objectives, move by move, verified against the engine | `training/11-vignette-playbooks.md` | VG-IDX, TR-06 | ✅ |
| TR-12 | Role-scoped **White Cell** manual (facilitator procedure layer; sections `WCM-n`) | `training/12-white-cell-manual.md` | TR-02, TR-05, TR-07, TR-15 | ✅ |
| TR-13 | Role-scoped **Blue cell** manual (defender procedure layer; sections `BLU-n`) | `training/13-blue-cell-manual.md` | TR-02, TR-05, TR-15 | ✅ |
| TR-14 | Role-scoped **Red cell** manual (adversary procedure layer; sections `RED-n`) | `training/14-red-cell-manual.md` | TR-02, TR-05, TR-15 | ✅ |
| TR-15 | Per-cell manual **traceability matrix** — bidirectional feature ⇄ manual-section index; hooked into skills 08 (doc-update step) and 10 (doc-coherence dimension) | `training/15-manual-traceability.md` | TR-12, TR-13, TR-14 | ✅ |
| TR-17 | **Vignette learning path** — 19 vignettes sequenced onboarding→ladder→mission-set/doctrine tracks; each rung linked to manual prerequisites + verified playbook (FR-11310/11320) | `training/16-learning-path.md` | TR-06, TR-11, TR-15 | ✅ |
| TR-16 | Browser-GUI verification harness guide (Playwright e2e) | *not yet created* | TR-10 | ⛔ Planned — blocked on the harness itself existing; AU-03 confirms ad hoc Playwright verification was used for the panel-manager audit but no committed harness/doc exists yet |

## Theme: Vignette library (`docs/vignettes/`)

> The original per-vignette stub design notes (`01-leo-isr-denial.md` … `08-multi-domain-taiwan.md`)
> were removed as stale May-2024 drafts that no longer matched the shipped YAMLs. The **YAML is
> now canonical**: each vignette's `intro_brief: {blue, red}` block is the authoritative premise/
> OoB/ROE/success-criteria, surfaced in-tool via the Mission Brief panel. Operator-facing
> walkthroughs live in `TR-11` instead of per-vignette design docs.

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| VG-IDX | Vignettes index | `vignettes/INDEX.md` | VG-FW, VG-ARCH | ✅ |
| VG-FW | Vignette framework & parameter schema | `vignettes/00-vignette-framework.md` | RS-05 | ✅ |
| VG-ARCH | Library architecture (4-track design) | `vignettes/00-LIBRARY-ARCHITECTURE.md` | VG-FW | ✅ |
| VG-GI | Ground infrastructure (real-world coordinates) | `vignettes/GROUND-INFRASTRUCTURE.md` | — | ✅ |
| VG-YAML | 19 runnable vignette YAMLs (8 canonical + training-basics + 5 Red COA + 3 mission-set + 1 learning + 1 novel), each self-documenting via `intro_brief` | `spacesim/content/vignettes/*.yaml` | VG-ARCH | ✅ |

## Theme: Manual screenshots (`docs/manual/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| MAN-00 | Screenshot index (52 generated panel images) | `manual/INDEX.md` | `tools/render_manual.py`, live UI | 🖼️ |

---

## How to read "done"

Every document above marked ✅ exists, is current, and matches the implementation/research it
describes as of this roadmap's last update. "Done" for prose docs does **not** mean "frozen" —
when code changes invalidate a doc's claims, flip it back to 🚧 and fix it before merging, the same
way the test-driven workflow in `CLAUDE.md` treats code.

## Open documentation work (rolled up from the tables above)

1. ~~RS-1.1, RS-1.2, RS-1.5, RS-1.8~~ — **done.** All of Tier 1 (RS-1.0 through RS-1.8) actually
   landed already (real commits, see the Research corpus theme table above); this rollup entry was
   stale and is removed.
2. **RS-2.x / RS-3.x / RS-4.x (19 files)** — Tier 2–4 research expansion. **Authorized** (per-tier,
   in progress) — see the Research corpus theme table for per-file status. Using the per-subsection
   `deep-research` cadence (§12.5.0), committed/pushed incrementally per subsection.
3. **TR-12** — Playwright DOM/render smoke-test guide. Blocked on a committed e2e harness; the
   commands/UI audits used ad hoc Playwright verification but didn't leave one behind. Authorized;
   not yet started.
4. **BS-04-REV / DS-07-REV** (optional, not assigned IDs above until someone starts them) — the
   build spec's milestone table and the API/networking design doc both predate the shipped P8
   LAN-multiplayer polling implementation and could use a refresh pass. Authorized; not yet started.

Everything else in the documentation corpus is ✅ or ♻️ as of this writing. New planned docs go
in the relevant theme table above with a fresh ID, not in a separate list — keep this file as the
single place that answers "what's left."
