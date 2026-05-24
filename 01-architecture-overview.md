# Architecture Overview

This document describes the overall shape of the simulator so Claude Code can build it in the
right order with the right seams. The guiding principle: **a UI-agnostic Python engine that
is deterministic, single-machine in v1, and explicitly seamed for later high-fidelity physics
and LAN multiplayer.**

## Design principles

1. **Deterministic core.** Given `(initial_state, ordered_action_log, seed)`, the engine
   produces identical results. This is what makes **rewind and undo exact** and is the single
   most important property — build everything else around it.
2. **UI-agnostic engine.** The simulation core has *no* dependency on any GUI. The UI is a
   client of the engine's API, whether that API is called in-process (v1) or over a network
   (future). The choice of PyQt vs. web does not touch the engine.
3. **Fidelity behind interfaces.** All orbital/RF math sits behind `AccessProvider`,
   `Propagator`, and `EffectResolver` interfaces. v1 ships "moderate" implementations; high
   fidelity is a drop-in swap.
4. **Data-driven content.** Vignettes, asset templates, and effect templates are data files,
   not code. Content authors and White Cell never edit Python.
5. **Single source of truth for time.** One simulation clock. Everything — windows, custody
   decay, maneuvers, injects — is a pure function of sim time and state.

## Layered structure

```
┌─────────────────────────────────────────────────────────────┐
│  PRESENTATION (UI)  — swappable: PyQt desktop OR web (FastAPI │
│  + browser). Renders cell views; sends user intents to the    │
│  Session API. Knows nothing about orbital math.               │
├─────────────────────────────────────────────────────────────┤
│  SESSION / APPLICATION LAYER                                  │
│   • SessionManager  — loads vignette, owns the clock, applies │
│     White Cell controls (play/pause/ff/rewind/undo/inject)    │
│   • CellController (Red / Blue / White) — validates that an   │
│     actor may take an action *now* (permissions + access      │
│     windows), queues orders, applies fog-of-war filtering     │
│   • API boundary  ← THIS is the future network seam           │
├─────────────────────────────────────────────────────────────┤
│  SIMULATION ENGINE (deterministic core)                       │
│   • WorldState     — all entities, orbits, custody, fuel, etc.│
│   • Clock / Scheduler — advances sim time; fires due events   │
│   • AccessProvider — computes access windows  ⟵ fidelity seam │
│   • Propagator     — orbit propagation         ⟵ fidelity seam│
│   • EffectResolver — resolves effects→outcomes ⟵ fidelity seam│
│   • EventLog       — append-only ordered action/event history │
├─────────────────────────────────────────────────────────────┤
│  DATA / CONTENT                                               │
│   • Vignette files, asset templates, effect templates (YAML)  │
│   • TLE import (real named satellites added by White Cell)    │
│   • Save/replay files (state snapshots + event log)           │
└─────────────────────────────────────────────────────────────┘
```

## How a player action flows (v1, single machine)

1. UI shows Blue Cell that satellite SAT-7's next command window is in 4:12 via STATION-BRAVO.
2. Blue queues "downlink imagery" — UI sends the intent to the **Session API**.
3. `CellController` checks: does Blue own SAT-7? Is the action type permitted by this vignette's
   ROE/parameters? It then **queues** the order tagged for execution at the next valid
   `access_window`.
4. The **Clock** advances (at White Cell's current multiplier). When sim time reaches the
   window start, the **Scheduler** fires the order; `EffectResolver` resolves it; `WorldState`
   updates; the action+result are appended to the **EventLog**.
5. UI re-queries the (fog-filtered) state and re-renders. Blue sees the imagery delivered.

> The only thing that changes for future multiplayer is step 2/4's transport: in-process calls
> become network messages to/from separate Red/Blue/White clients. The engine is unchanged.

## Determinism, rewind, and undo (how they actually work)

- **State snapshots** are taken periodically (e.g., every N sim-minutes) and on demand.
- The **EventLog** is the authoritative ordered list of every action and inject with its sim
  timestamp.
- **Rewind to T:** load the latest snapshot ≤ T, then re-apply EventLog entries up to T. Because
  the core is deterministic, this reproduces the exact world at T.
- **Undo last action:** drop the most recent action(s) from the log and re-derive from the
  nearest prior snapshot. (See `06-white-cell-controls.md` for the full semantics, including
  what undo means when an effect has already cascaded.)
- **Fast-forward** is just running the clock at a high multiplier; **branching** ("what-if")
  is rewinding and continuing with a different action set, saved as a new branch.

## Single-machine v1 vs. future multiplayer (the one seam)

| Concern | v1 (single machine) | Future (LAN multiplayer) |
|---|---|---|
| Processes | One process; one player drives any cell via a cell-switcher | Server process + 3 thin clients (Red/Blue/White) |
| API transport | In-process function calls | Same API over WebSocket/gRPC |
| Authority | Local SessionManager | Server is authoritative; clients send intents |
| Fog-of-war | Applied per-cell view in the same process | Applied server-side before sending to each client |

**Action for Claude Code:** define the Session API as an abstract interface now, implement the
in-process version in v1, and never let the engine import UI or transport code. The multiplayer
future then costs a transport adapter, not a rewrite.

## Cross-references
- Engine internals & event loop: `03-simulation-engine.md`
- Entities & schemas: `04-data-model.md`
- What each cell can see/do: `05-cell-interfaces.md`
- Time travel & vignette control: `06-white-cell-controls.md`
- The API contract & network seam: `07-api-and-networking.md`
- Build order: `08-build-roadmap.md`
