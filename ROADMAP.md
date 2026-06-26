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
| RS-01 | Western doctrine | `research/01-doctrine-western.md` | — | 🚧 *(Tier 1 citation backfill pending — see RS-1.1)* |
| RS-02 | Non-Western doctrine | `research/02-doctrine-non-western.md` | RS-01 | 🚧 *(Tier 1 citation backfill pending — see RS-1.2)* |
| RS-03 | Counterspace taxonomy (the 5 D's) | `research/03-counterspace-taxonomy.md` | RS-01, RS-02 | ✅ *(Tier 1 expansion landed, commit `b39c24f`, 821 lines / 147 cites — see RS-1.3)* |
| RS-04 | Orbital mechanics primer | `research/04-orbital-mechanics-primer.md` | — | ✅ *(Tier 1 expansion landed, commits `dde9739..14c2454`, 822 lines / 204 cites — see RS-1.4)* |
| RS-05 | Mission types & their counters | `research/05-mission-types-and-counters.md` | RS-03, RS-04 | 🚧 *(Tier 1 citation backfill pending — see RS-1.5; next concrete step per §12.8)* |
| RS-06 | Bus & payload operations | `research/06-bus-and-payload-operations.md` | RS-04 | ✅ *(Tier 1 expansion landed, commit `6c17e04`, 674 lines / 99 cites — see RS-1.6)* |
| RS-07 | Legal norms & ROE | `research/07-legal-norms-and-roe.md` | RS-03 | ✅ *(Tier 1 expansion landed, commits `469c8e8..cd37fe2`, 795 lines / 106 cites — see RS-1.7)* |
| RS-10 | Sources & methodology (citation convention for the whole corpus) | `research/10-sources-and-methodology.md` | — | ✅ *(landed first, commit `968c4be`, 363 lines — see RS-1.0)* |
| RS-WORK | Staging drafts for in-flight subsections (scratch, not canonical) | `research/working/07/1.7.5-roe-design-pattern.md` | — | ♻️ *(superseded once its parent file lands; safe to delete after RS-07 integration — already landed, this draft is stale and can be removed)* |

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
| RS-1.1 | `01-doctrine-western.md` ~3× expansion (USSF Spacepower, AFDP 3-14, JP 3-14, allied doctrine) | same file, in place | RS-1.0 | ⛔ Planned — next-biggest deliverable per §12.8 |
| RS-1.2 | `02-doctrine-non-western.md` ~3× expansion (CASI, post-2024 PLA reorg, Hendrickx) | same file, in place | RS-1.0, RS-1.1 | ⛔ Planned |
| RS-1.3 | `03-counterspace-taxonomy.md` ~3× expansion | same file, in place | RS-1.0 | ✅ Landed (commit `b39c24f`) — structural exemplar for the rest of the cadence |
| RS-1.4 | `04-orbital-mechanics-primer.md` ~2× expansion | same file, in place | RS-1.0 | ✅ Landed (commits `dde9739..14c2454`) |
| RS-1.5 | `05-mission-types-and-counters.md` ~1.5× (depth deferred to Tier 2 Track D) | same file, in place | RS-1.0, RS-1.3 | ⛔ Planned — **next concrete step** per §12.8 (start at §1.5.1, 12 subsections) |
| RS-1.6 | `06-bus-and-payload-operations.md` ~2× expansion | same file, in place | RS-1.0 | ✅ Landed (commit `6c17e04`) |
| RS-1.7 | `07-legal-norms-and-roe.md` ~2× expansion | same file, in place | RS-1.0, RS-1.3 | ✅ Landed (commits `469c8e8..cd37fe2`) |
| RS-1.8 | `research/INDEX.md` regenerated for post-expansion taxonomy | `research/INDEX.md` | RS-1.0…RS-1.7 | ⛔ Planned — trivial, do last in Tier 1 |

**Tier 2 — per-mission and per-actor deep-dives (6 new files):**

| ID | Document | Path (new) | Depends on | Status |
|---|---|---|---|---|
| RS-2.1 | ISR (EO/SAR) deep-dive — Maxar/Planet/Capella, NRO KH-program history, NIIRS, TPED | `research/05a-isr-eo-sar.md` | RS-1.5 | 🅿️ Scoped, not authorized |
| RS-2.2 | SATCOM/PNT deep-dive — WGS/AEHF/Milstar, GPS IS-GPS-200E flex power, Galileo/GLONASS/BeiDou | `research/05b-satcom-pnt.md` | RS-1.5 | 🅿️ Scoped, not authorized |
| RS-2.3 | SIGINT/MW/weather/SDA deep-dive — Trumpet/Mercury/Mentor, SBIRS, GOES-R MDS, SSN tasking | `research/05c-sigint-mw-wx-sda.md` | RS-1.5 | 🅿️ Scoped, not authorized |
| RS-2.4 | China deep-dive — 2024 PLA SSF→ASF reorg, SoS doctrine, 36th Test Base | `research/02a-china-deep-dive.md` | RS-1.2 | 🅿️ Scoped, not authorized |
| RS-2.5 | Russia deep-dive — VKS/RVSN, EW Troops (Bylina/Tirada-2/Pole-21), Tobol | `research/02b-russia-deep-dive.md` | RS-1.2 | 🅿️ Scoped, not authorized |
| RS-2.6 | Emerging actors — India, Iran, DPRK, Israel, commercial counterspace | `research/02c-emerging-actors.md` | RS-1.2 | 🅿️ Scoped, not authorized |

**Tier 3 — counterspace systems and physics (8 new files):**

| ID | Document | Path (new) | Depends on | Status |
|---|---|---|---|---|
| RS-3.1 | DA-ASAT systems — SC-19/DN-3, Nudol/A-235, SM-3, PDV-Mk2 | `research/03a-da-asat-systems.md` | RS-1.3 | 🅿️ Scoped, not authorized |
| RS-3.2 | Co-orbital/RPO systems — SJ-21/15, Burevestnik, Olymp-K/Luch-2, GSSAP, MEV-1/2 | `research/03b-coorbital-rpo.md` | RS-1.3 | 🅿️ Scoped, not authorized |
| RS-3.3 | EW/jamming — CCS Block 10.2, Tirada-2/Pole-21/Bylina, Tobol, AEHF ECCM, J/S analysis | `research/03c-ew-jamming.md` | RS-1.3 | 🅿️ Scoped, not authorized |
| RS-3.4 | Directed energy — Sokol-Eshelon, Peresvet, Zimu-1, optical hardening | `research/03d-directed-energy.md` | RS-1.3 | 🅿️ Scoped, not authorized |
| RS-3.5 | Cyber — Viasat KA-SAT incident reconstruction, SPARTA TTPs, ROSAT/TDRS history | `research/03e-cyber.md` | RS-1.3 | 🅿️ Scoped, not authorized |
| RS-3.6 | Nuclear/EMP — Starfish Prime, Soviet K-series tests, OST Art. IV (deferred to v2) | `research/03f-nuclear-emp.md` | RS-1.3 | 🅿️ Scoped, not authorized |
| RS-3.7 | Propagator fidelity — Kepler+J2 vs SGP4 vs high-precision validation | `research/04a-propagator-fidelity.md` | RS-1.4 | 🅿️ Scoped, not authorized |
| RS-3.8 | Debris & conjunction — NASA ORDEM/ESA MASTER, Cosmos 1408 vs FY-1C persistence | `research/04b-debris-and-conjunction.md` | RS-1.4 | 🅿️ Scoped, not authorized |

**Tier 4 — operations, legal, history, forward-looking (5 deliverables):**

| ID | Document | Path (new) | Depends on | Status |
|---|---|---|---|---|
| RS-4.1 | Ground segment — AFSCN, TDRSS, AWS Ground Station, KSAT/ATLAS/Viasat-RTE | `research/06a-ground-segment.md` | RS-1.6 | 🅿️ Scoped, not authorized |
| RS-4.2 | Incident record — dated catalog of named counterspace incidents (PME instructor reference) | `research/07a-incident-record.md` | RS-1.7, RS-3.x | 🅿️ Scoped, not authorized |
| RS-4.3 | Commercial & allied — Starlink/Kuiper/OneWeb proliferation, Five Eyes SST, non-state actors | `research/08-commercial-and-allied.md` | RS-2.x | 🅿️ Scoped, not authorized |
| RS-4.4 | Emerging tech — optical ISLs, software-defined payloads, on-orbit refueling | `research/09-emerging-tech.md` | RS-2.x | 🅿️ Scoped, not authorized |
| RS-4.5 | (Shared lit-review workflow note for RS-4.3/RS-4.4 — overlapping proliferation research, not a standalone file) | — | RS-4.3, RS-4.4 | 🅿️ Scoped, not authorized |

> **Don't start Tiers 2–4 without checking with the user first** — `RT-FUTURE` §12.1 explicitly
> scopes this as "planned, not yet authorized." Tier 1 is in flight and pre-approved; treat RS-1.1
> / RS-1.2 / RS-1.5 / RS-1.8 as the only currently-actionable research items.
>
> **Authoring cadence (binding for all of Tier 1+):** one `deep-research` subsection at a time,
> ≤20k subagent tokens per invocation, integration pass per file, commit-and-push per subsection.
> See `RT-FUTURE` §12.5.0 — a "rewrite the whole file" brief blew the token budget in 3 of 4
> attempts under the old cadence.

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

1. **RS-1.1, RS-1.2, RS-1.5, RS-1.8** — the four remaining Tier 1 research files. RS-1.5 is the
   named "next concrete step" in `RT-FUTURE` §12.8; RS-1.1 can run in parallel. Use the
   per-subsection `deep-research` cadence (§12.5.0), not a single whole-file invocation.
2. **RS-2.x / RS-3.x / RS-4.x (19 files)** — fully scoped Tier 2–4 research expansion. **Ask the
   user before starting** — explicitly "not yet authorized" per `RT-FUTURE` §12.1.
3. **TR-12** — Playwright DOM/render smoke-test guide. Blocked on a committed e2e harness; the
   commands/UI audits used ad hoc Playwright verification but didn't leave one behind.
4. **BS-04-REV / DS-07-REV** (optional, not assigned IDs above until someone starts them) — the
   build spec's milestone table and the API/networking design doc both predate the shipped P8
   LAN-multiplayer polling implementation and could use a refresh pass.

Everything else in the documentation corpus is ✅ or ♻️ as of this writing. New planned docs go
in the relevant theme table above with a fresh ID, not in a separate list — keep this file as the
single place that answers "what's left."
