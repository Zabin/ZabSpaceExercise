# Documentation Roadmap

Single authoritative tracker for **every prose document this project produces** — what exists,
what depends on what, and what's still open. Humans and future Claude Code sessions should read
this file first to answer "what's done, what's in flight, what's left" without re-deriving it from
`git log` or scanning `docs/`.

**Update this file whenever a document's status changes.** When you finish a doc, flip its status
to ✅ and add the commit/PR if useful. When you start one, flip it to 🚧. When you identify a new
doc that needs writing, add a row with an ID, its dependencies, and status `⛔ Planned`. Don't let
this file drift from reality — it is the thing that replaces re-reading every file to find out.

## Status legend

| Symbol | Meaning |
|---|---|
| ✅ | Done — written, current, matches the implementation it describes. |
| 🚧 | In progress — drafted but incomplete, or known to need a revision pass. |
| ⛔ | Planned — identified as needed, not yet started. |
| ♻️ | Living — intentionally never "done"; updated continuously as the project evolves. |
| 🖼️ | Generated — produced by a script from live data, not hand-authored prose. |

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
| RT-FUTURE | Cross-cutting v1.1+ TODO | `docs/FUTURE-WORK.md` | — | ♻️ |

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
| DS-16 | Multiplayer transport implementation guide (`WebSocketSession` over-the-wire) | *not yet created* | DS-07, RT-FUTURE §1 | ⛔ |

> DS-16 covers the one architecturally significant gap called out in `RT-FUTURE` §1 (P8/M7):
> documenting how to implement the `WebSocketSession` stub's method bodies and the push-delta
> channel. Add it under `design/` with the next free numeric prefix when that work starts.

## Theme: Research corpus (the *why* — `docs/research/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| RS-00 | Research index | `research/INDEX.md` | RS-01…RS-06 | ✅ |
| RS-01 | Western doctrine | `research/01-doctrine-western.md` | — | ✅ |
| RS-02 | Non-Western doctrine | `research/02-doctrine-non-western.md` | RS-01 | ✅ |
| RS-03 | Counterspace taxonomy (the 5 D's) | `research/03-counterspace-taxonomy.md` | RS-01, RS-02 | ✅ |
| RS-04 | Orbital mechanics primer | `research/04-orbital-mechanics-primer.md` | — | ✅ |
| RS-05 | Mission types & their counters | `research/05-mission-types-and-counters.md` | RS-03, RS-04 | ✅ |
| RS-06 | Bus & payload operations | `research/06-bus-and-payload-operations.md` | RS-04 | ✅ |

## Theme: Training manual (`docs/training/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| TR-00 | Training index | `training/INDEX.md` | TR-01…TR-10 | ✅ |
| TR-01 | Install & run | `training/01-install-and-run.md` | BS-01 | ✅ |
| TR-02 | The interface at a glance | `training/02-interface.md` | TR-01, BS-07 | ✅ |
| TR-03 | First exercise (Vignette 1) | `training/03-first-exercise.md` | TR-02, VG-01 | ✅ |
| TR-04 | Guided training vignette walkthrough | `training/04-guided-vignette.md` | TR-03, VG-00-FW | ✅ |
| TR-05 | Core concepts | `training/05-core-concepts.md` | TR-02, BS-05 | ✅ |
| TR-06 | The eight vignettes at a glance | `training/06-the-eight-vignettes.md` | VG-01…VG-08 | ✅ |
| TR-07 | White Cell facilitation | `training/07-white-cell-facilitation.md` | DS-06 | ✅ |
| TR-08 | HTTP API reference | `training/08-http-api-reference.md` | DS-07 | ✅ |
| TR-09 | Troubleshooting & glossary | `training/09-troubleshooting-and-glossary.md` | — | ✅ |
| TR-10 | UI reference (all 14 panels) | `training/10-ui-reference.md` | BS-07, MAN-00 | ✅ |
| TR-11 | Browser-GUI verification harness guide (Playwright e2e) | *not yet created* | TR-10, RT-FUTURE §8 | ⛔ |

> TR-11 is the doc side of the one remaining gap in `RT-FUTURE` §8: the harness itself doesn't
> exist yet (`@pytest.mark.e2e`, opt-in), so there's nothing to document until it's built.

## Theme: Vignette library (`docs/vignettes/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| VG-IDX | Vignettes index | `vignettes/INDEX.md` | VG-FW, VG-ARCH, VG-01…VG-08 | ✅ |
| VG-FW | Vignette framework & parameter schema | `vignettes/00-vignette-framework.md` | RS-05 | ✅ |
| VG-ARCH | Library architecture (4-track design) | `vignettes/00-LIBRARY-ARCHITECTURE.md` | VG-FW | ✅ |
| VG-GI | Ground infrastructure (real-world coordinates) | `vignettes/GROUND-INFRASTRUCTURE.md` | — | ✅ |
| VG-01 | V1 — LEO ISR denial | `vignettes/01-leo-isr-denial.md` | VG-FW | ✅ |
| VG-02 | V2 — GEO RPO shadowing | `vignettes/02-geo-rpo-shadowing.md` | VG-FW | ✅ |
| VG-03 | V3 — GNSS/PNT EW campaign | `vignettes/03-gnss-ew-campaign.md` | VG-FW | ✅ |
| VG-04 | V4 — co-orbital threat & active escort | `vignettes/04-co-orbital-threat-escort.md` | VG-FW | ✅ |
| VG-05 | V5 — direct-ascent ASAT crisis | `vignettes/05-da-asat-crisis.md` | VG-FW | ✅ |
| VG-06 | V6 — SATCOM cyber & link interdiction | `vignettes/06-satcom-cyber-link.md` | VG-FW | ✅ |
| VG-07 | V7 — SDA custody hunt | `vignettes/07-sda-custody-hunt.md` | VG-FW | ✅ |
| VG-08 | V8 — multi-domain capstone (Taiwan) | `vignettes/08-multi-domain-taiwan.md` | VG-FW, VG-01…VG-07 | ✅ |
| VG-LIB | Library-expansion vignettes (10 YAML scenarios, Tracks A–D; design notes inline in YAML, not separate prose) | `spacesim/content/vignettes/*.yaml` | VG-ARCH | ✅ |

## Theme: Manual screenshots (`docs/manual/`)

| ID | Document | Path | Depends on | Status |
|---|---|---|---|---|
| MAN-00 | Screenshot index (52 generated panel images) | `manual/INDEX.md` | `tools/render_manual.py`, live UI | 🖼️ |

---

## How to read "done"

Every document above marked ✅ exists, is current, and matches the implementation/spec it
describes as of this roadmap's last update. "Done" for prose docs does **not** mean "frozen" —
when code changes invalidate a doc's claims, flip it back to 🚧 and fix it before merging, the same
way the test-driven workflow in `CLAUDE.md` treats code.

## Open documentation work (rolled up from the tables above)

1. **DS-16** — Multiplayer transport implementation guide. Blocked on someone actually
   implementing `WebSocketSession`'s method bodies (`RT-FUTURE` §1); write the doc alongside that
   work, not before it.
2. **TR-11** — Playwright DOM/render smoke-test guide. Blocked on the harness existing
   (`RT-FUTURE` §8).

Everything else in the documentation corpus is ✅ or ♻️ as of this writing. New planned docs go
in the relevant theme table above with a fresh ID, not in a separate list — keep this file as the
single place that answers "what's left."
