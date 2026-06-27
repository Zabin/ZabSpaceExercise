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

## Theme: Build Spec (binding v1 spec — `docs/build-spec/`)

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
| FS-106 | White Cell Dashboard | `features/FS-106-white-cell-dashboard.md` | DOM-003 | ✅ |
| FS-107 | After Action Review | `features/FS-107-after-action-review.md` | DOM-001, DOM-003 | ✅ |
| FS-108 | Inject Authoring *(candidate)* | `features/FS-108-inject-authoring.md` | DOM-003 | ⛔ Planned (authorized) |
| FS-201 | Competency Assessment | `features/FS-201-competency-assessment.md` | DOM-002 | ✅ |
| FS-202 | Rubric Authoring *(candidate)* | `features/FS-202-rubric-authoring.md` | DOM-002 | ⛔ Planned (authorized) |
| FS-301 | Research Analytics | `features/FS-301-research-analytics.md` | DOM-004, DOM-005 | ✅ |

FS-108 and FS-202 are intentionally lighter-weight stubs (not full specs) — both are marked
"(candidate)" in their owning domain document and require explicit user authorization (MSTR-006 §3)
before promotion to a full spec or any Implementation Package work.

**Next:** Phase 5 (Implementation Packages, `docs/implementations/`) is complete (below). Phase 6-8
(Consistency/Dependency/Traceability review, MSTR-006 §7) is also complete (see the dedicated
theme section below).

## Theme: Implementation Packages (the *how* — `docs/implementations/`)

Phase 5 of the documentation-driven-development expansion (MSTR-005 §4 chain: ... → Feature
Specification → **Implementation Package** → Code → Tests). Each `IMP-xxxA` describes architecture,
data model, state machines, and test/migration plan in prose/pseudocode, never literal committed
code (MSTR-006 §8). Two situations per package: as-built (documents existing, test-covered code,
FS-101 through FS-107) vs. forward design (FS-201/FS-301, capability not yet implemented, coding
work not authorized by this documentation per MSTR-006 §3). Router:
[`implementations/INDEX.md`](docs/implementations/INDEX.md).

| ID | Document | Path | FS | Situation | Status |
|---|---|---|---|---|---|
| IMP-00 | Implementation index | `implementations/INDEX.md` | — | — | ✅ |
| IMP-101A | Mission Planning — dry-run preview & window/Δv display | `implementations/IMP-101A-mission-planning.md` | FS-101 | As-built | ✅ |
| IMP-102A | Command Scheduling — Order/OrderSystem lifecycle | `implementations/IMP-102A-command-scheduling.md` | FS-102 | As-built | ✅ |
| IMP-103A | Custody Management — Track confidence model | `implementations/IMP-103A-custody-management.md` | FS-103 | As-built | ✅ |
| IMP-104A | SDA Tasking — sensor tasking & SSN request lifecycle | `implementations/IMP-104A-sda-tasking.md` | FS-104 | As-built | ✅ |
| IMP-105A | Spacecraft Operations — bus/payload command & telemetry | `implementations/IMP-105A-spacecraft-operations-bus-payload.md` | FS-105 | As-built | ✅ |
| IMP-105B | Spacecraft Operations — effect resolution & console UX | `implementations/IMP-105B-spacecraft-operations-effects-console.md` | FS-105 | As-built | ✅ |
| IMP-106A | White Cell Dashboard — session/inject/clock control plane | `implementations/IMP-106A-white-cell-dashboard.md` | FS-106 | As-built | ✅ |
| IMP-107A | After Action Review — replay/scrub/branch-compare | `implementations/IMP-107A-after-action-review.md` | FS-107 | As-built | ✅ |
| IMP-201A | Competency Assessment — rubric computation design | `implementations/IMP-201A-competency-assessment.md` | FS-201 | Forward design | ⛔ Planned (design only) |
| IMP-301A | Research Analytics — multi-run export design | `implementations/IMP-301A-research-analytics.md` | FS-301 | Forward design | ⛔ Planned (design only) |

FS-108/FS-202 have no Implementation Package (unauthorized candidates, MSTR-006 §3).

**Next:** Phase 6-8 (Consistency/Dependency/Traceability review, MSTR-006 §7) is complete (below).

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

> **Open question:** `docs/architecture/` and `docs/scenarios/` are both empty (no files, no git
> history) despite MSTR-006 §5 listing them as in-scope directories for the metadata-block
> requirement. This corpus's actual architecture/scenario content instead lives under
> `docs/design/` and `docs/vignettes/` (per `docs/INDEX.md`'s theme table, which does not list
> `architecture/`/`scenarios/` at all). Per MSTR-006 §6, this is flagged rather than silently
> resolved: it is unclear whether (a) `docs/architecture/`/`docs/scenarios/` are aspirational
> MSTR-006 §5 scope not yet populated and should eventually receive content, (b) MSTR-005/MSTR-006
> should be corrected to drop these two paths in favor of the `design/`/`vignettes/` names actually
> in use, or (c) something else. Left for the user to decide; no document was edited to resolve it.

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
| TR-12 | Browser-GUI verification harness guide (Playwright e2e) | *not yet created* | TR-10 | ⛔ Planned — blocked on the harness itself existing; AU-03 confirms ad hoc Playwright verification was used for the panel-manager audit but no committed harness/doc exists yet |

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
