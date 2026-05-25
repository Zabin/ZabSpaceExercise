# Space Control & Orbital Warfare Exercise Simulator — Research & Design Package

This repository contains both the **research & design package** (doctrinal research, the exercise
vignette library, and the software design spec) **and a working implementation** of the professional
military education (PME) wargaming tool for space control and orbital warfare.

> **Status:** Backend feature-complete through Phase 7 (deterministic engine, orbits & access
> windows, effects/cyber/custody, bus & safe mode, the session layer with fog-of-war, planning &
> tasking, the FastAPI web layer, the belief scene + 2D map, all eight vignettes, and AAR replay).
> 81 tests pass. The chosen stack is **Python + FastAPI/web**.
>
> **New here?** Read **[`docs/TRAINING-MANUAL.md`](docs/TRAINING-MANUAL.md)** to install, run, and
> drive your first exercise. Project conventions and invariants live in `CLAUDE.md`.

## Quick start

```bash
pip install pydantic numpy sgp4 pyyaml fastapi uvicorn      # runtime deps
pip install pytest hypothesis skyfield httpx                # to run the tests
uvicorn spacesim.ui_web.server:app                          # then open http://127.0.0.1:8000/
python3 -m pytest                                           # run the full test suite
```

## What this is for

A facilitator (**White Cell**) runs a space-warfare exercise. **Red** and **Blue** cells
each command a fleet of space and ground assets and may only act on those assets when
physics allows it — a satellite can only be commanded when it is in view of a ground
station, sensors can only observe targets during a pass, and weapons can only be employed
inside a valid engagement window. Time flows in real time, but White Cell can fast-forward,
rewind, pause, and undo. White Cell picks a vignette, tunes its parameters, and injects
events as the scenario unfolds.

## Design assumptions (confirmed with the user)

| Topic | Decision |
|---|---|
| Primary purpose | Professional military education / wargaming |
| Target users | **Semi-technical CAF (and allied) space operators.** They know the domain; they are not necessarily software power-users. The UI does the math; operators make decisions. See `03-software-design/09-gui-principles.md`. |
| Orbital-mechanics fidelity | **Moderate now, upgradeable to high.** Simplified two-body/SGP4 passes and approximate access windows behind interfaces that allow a high-fidelity propagator and RF link-budget model to be swapped in later. |
| Sourcing | Reputable open sources only (doctrine documents, think-tank reports). No classified material. |
| Capability domains | Orbital warfare (co-orbital/RPO/kinetic), electromagnetic warfare (jam/spoof/dazzle), space domain awareness/tracking, **all satellite mission types and their counters**. Cyber included as a link/ground-segment effect. |
| West vs. non-West | West = US/USSF + allied (UK, France, NATO). Non-West = PLA (Aerospace Force) and Russia (VKS), lighter coverage of others. |
| Architecture | **Single-machine first** (one player can drive any cell; White Cell adjusts menus live). LAN three-cell multiplayer (Red/Blue/White) is a documented future path, not built in v1. |
| Assets | Fictional/generic constellations by default; **White Cell can add and name real satellites via TLEs.** Data model accepts TLEs natively. |
| Stack | **Python core** (UI-agnostic engine); UI either Python-native (e.g., PyQt) or web (FastAPI + browser). Recommendation in tech-stack doc; core never depends on the UI choice. |

## Package contents

```
space-control-sim/
├── README.md                         ← you are here
├── 01-research/
│   ├── 01-doctrine-western.md         US/USSF + allied space control doctrine
│   ├── 02-doctrine-non-western.md     PLA and Russian doctrine
│   ├── 03-counterspace-taxonomy.md    The 5-category threat taxonomy + effects
│   ├── 04-orbital-mechanics-primer.md Access windows, passes, regimes (the sim's physics)
│   ├── 05-mission-types-and-counters.md Every satellite mission type and how to counter it
│   └── 06-bus-and-payload-operations.md How operators really fly the bus & each payload type
├── 02-vignettes/
│   ├── 00-vignette-framework.md       Common structure + tunable parameter schema
│   ├── 01-leo-isr-denial.md
│   ├── 02-geo-rpo-shadowing.md
│   ├── 03-gnss-ew-campaign.md
│   ├── 04-co-orbital-threat-escort.md
│   ├── 05-da-asat-crisis.md
│   ├── 06-satcom-cyber-link.md
│   ├── 07-sda-custody-hunt.md
│   └── 08-multi-domain-taiwan.md
└── 03-software-design/
    ├── 00-BUILD-SPECIFICATION.md      ★ START HERE — the binding v1 project spec (~20 pp)
    ├── 01-architecture-overview.md
    ├── 02-tech-stack-recommendation.md
    ├── 03-simulation-engine.md        Time, orbits, access windows, event loop
    ├── 04-data-model.md               Entities, assets, actions, schemas
    ├── 05-cell-interfaces.md          Red/Blue/White UX and permitted actions
    ├── 06-white-cell-controls.md      Vignette selection, time travel, injects
    ├── 07-api-and-networking.md       Client–server contract (future)
    ├── 08-build-roadmap.md            Phased milestones (expanded in 00-BUILD-SPECIFICATION)
    ├── 09-gui-principles.md           UX for semi-technical CAF space operators
    ├── 10-sda-3d-viewer.md            3D viewer of the cell's SDA belief (v1.1)
    ├── 11-command-planning-and-tasking.md  Plan-first commanding (pass/ISL) + sensor tasking
    ├── 12-safe-mode-loop.md           Safe-mode attack/detection/recovery + White Cell dials
    ├── 13-operator-command-catalog.md Defined bus & payload commands by mission type
    ├── 14-delta-v-economy.md          Fuel as finite resource; lifetime-vs-maneuver trade
    └── 15-worked-asset-templates.md   ★ Copy-me: 3 complete asset templates + instantiation
```

## How Claude Code should use this

1. **Read `03-software-design/00-BUILD-SPECIFICATION.md` first** — the binding ~20-page
   project-start spec (confirmed decisions, scope, requirements, architecture, data formats, UI,
   milestones M0–M8 with acceptance criteria, traceability, risks). Where it and an older design
   note disagree, the build spec wins for v1. Then read `08-build-roadmap.md` for the milestone
   narrative — it sequences the work for a **single-machine Python build** with a clear seam for
   later LAN multiplayer.
2. Treat `04-data-model.md` and `03-simulation-engine.md` as the contract. The "moderate
   fidelity" math lives behind interfaces named in those files so a high-fidelity module
   drops in without touching gameplay code. The same separation keeps the **engine
   UI-agnostic** so a Python or web GUI can sit on top.
3. Each vignette in `02-vignettes/` is a data file the engine loads, not hard-coded logic.
4. Two principles are load-bearing for the UI and must not be compromised for convenience:
   **(a)** Red/Blue see only their **own SDA belief state**, never ground truth — the 2D map
   and 3D viewer both render from the cell's `TrackCatalog` (`10-sda-3d-viewer.md`).
   **(b)** Operators **plan commands** that execute at the next valid pass / ISL relay, and
   **task sensors** for collection — they never act instantly on perfect knowledge
   (`11-command-planning-and-tasking.md`).
4. The engine runs **one process, one player driving any cell** in v1; the API doc marks the
   exact boundary where a network transport replaces in-process calls for future multiplayer.

## Sourcing note

All doctrinal content is drawn from public documents: the USSF *Space Warfighting: A
Framework for Planners* (2025) and *Space Force Doctrine Document 1* (2025); Secure World
Foundation *Global Counterspace Capabilities* (2025/2026); CSIS, Atlantic Council, USCC,
and Chatham House analyses; and reporting on PLA and Russian programs. Specific citations
are inline in the research files. This is an unclassified training aid; named real systems
are used only as publicly reported and the simulator defaults to fictional assets.
