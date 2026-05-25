# CLAUDE.md — Space Control & Orbital Warfare Exercise Simulator

Durable project guide for Claude Code. Read this first, then the docs in the order below.

## What this is

A single-machine, hot-seat **professional military education (PME) wargaming tool** for space
control and orbital warfare. A White Cell facilitator runs an exercise; Red and Blue cells command
fleets of space/ground assets as bus and payload operators, constrained by orbital geometry
(you can only command, observe, or attack when access windows permit). Most effects are reversible
(EW/cyber/proximity), not kinetic.

**Status: backend feature-complete through Phase 7 (81 tests green).** Deterministic engine
(P0–P4.5), the web layer (P5, FastAPI + browser front end), the render-from-custody belief
scene + 2D map (P5.5), all **eight vignettes** as YAML + TLE force-add + Red doctrine presets (P6),
and the **capstone Vignette 8 + AAR replay** (P7: read-only replay/scrub, branch comparison,
campaign summary). Code under `spacesim/`; content is YAML; UI stack = **web**. The browser GUI is
unverified headless, but every backend path (endpoints, fog, objectives, AAR) is test-covered.
Remaining: P5.5 full CesiumJS 3D globe (v1.1) and P8 (fidelity/multiplayer seam proofs).

## Authoritative source & reading order

1. `00-BUILD-SPECIFICATION.md` — the binding v1 spec. **On any conflict, the build spec wins.**
2. `01-architecture-overview.md` + `04-data-model.md` — the architecture and data contract.
3. `01-research/` files (`01`–`06`) — *why* the rules are what they are.
4. `08-build-roadmap.md` — phased build sequence (the plan of record).
5. Remaining design docs (`03`,`05`–`07`,`09`–`15`) and `02-vignettes/` as each phase needs them.

## Tech stack (leading recommendation — confirm at Phase 0)

From `02-tech-stack-recommendation.md`: Python 3.11+, NumPy, **Skyfield**/`sgp4`, **pydantic v2**,
content as data files, **pytest**. UI = **FastAPI + web (Option A)** — the LAN-multiplayer seam
comes nearly free. Desktop PyQt (Option B) is the fallback; the engine is identical either way.

Project layout (`02-tech-stack-recommendation.md` §"Suggested project layout"):
```
spacesim/
├── engine/   # deterministic core — NO ui, NO network imports
├── session/  # SessionManager, CellController (+fog-of-war), SessionAPI (the network seam)
├── content/  # vignettes / assets / effects (data) + TLE import
├── ui_web/   # (or ui_qt/) chosen front end — depends on session, not engine
└── tests/    # pytest, incl. the determinism property test
```

## Load-bearing invariants (never compromise these)

1. **Deterministic core.** No wall-clock reads and no global RNG anywhere in `engine/`.
   `(initial_state, ordered eventlog, seed) → byte-identical state`. This is what makes
   rewind/undo/branch exact. The Phase-1 determinism property test gates all later work and must
   stay green forever.
2. **UI-agnostic engine.** `engine/` imports no UI or transport code (enforce with import-linter).
3. **Fog-of-war at the boundary.** Filtering lives at the `SessionAPI`/`CellController` layer,
   never in the UI. Red/Blue render only their own `TrackCatalog`/`CellView` — never ground truth.
4. **Plan-first.** Operators *plan* commands that execute at the next valid access window and
   *task* sensors for collection; they never act instantly on perfect knowledge.
5. **Sub-step the clock.** Advance to the next scheduled event, never past it — a naive large step
   at 600× skips short LEO passes and breaks realism.
6. **Content is data.** Vignettes, asset templates, and effect templates are data files, not
   Python. If scenario logic starts leaking into code, move it back into data + inject/effect primitives.

## Key facts

- Largest v1 scenario: **≤24 satellites** (hard ceiling 48); **constellations ≤3 sats**, each
  operated/monitored individually.
- **Six access channels:** `command_uplink`, `telemetry_downlink`, `sensor_observation`,
  `jam_footprint`, `weapon_engagement`, `rpo_proximity`.
- **Five effect categories → five D's:** deceive / disrupt / deny / degrade / destroy. **Cyber is
  the exception** — not window-gated; resolves against `{access_vector, success_prob, persistence,
  patchable}` subject to the defender's cyber posture.
- Orbital fidelity: **moderate** (Keplerian + J2, TLE via Skyfield), behind interfaces
  (`Propagator`, `AccessProvider`, `EffectResolver`) so a high-fidelity model drops in later.

## Build phases (from `08-build-roadmap.md`)

- **P0** Skeleton + import guard.
- **P1** Deterministic core (`WorldState`, `SimClock`, `Scheduler`, `EventLog`, `Snapshot`, seeded
  RNG) + determinism property test.
- **P2** Orbits & all six access channels (moderate fidelity).
- **P3** Orders, five-D effects, cyber exception, custody/Track + weapons-quality gate.
- **P3.5** Bus & payload model + safe mode (headless).
- **P4** Session layer (SessionManager / CellController / SessionAPI) + Vignette 1 end-to-end with
  fog-of-war. *(Note: this header is missing in the roadmap — its bullets are appended to P3.5.)*
- **P4.5** Planning & tasking scheduler + safe-mode recovery chain. ✓
- **P5** UI over the API (FastAPI + web). ✓ (backend tested; browser GUI unverified headless)
  **P5.5** Render-from-custody belief scene + 2D map. ✓ (full Cesium 3D globe is the v1.1 follow-on)
- **P6** Vignettes 2–7 (data) + TLE force-add + Red doctrine profiles. ✓ (all 8 vignette files load/run)
- **P7** Capstone Vignette 8 + AAR replay (read-only replay/scrub, branch compare). ✓
  **P8** Document/scaffold fidelity & multiplayer seams.

## Test-driven workflow (mandatory)

Build every phase **test-first**: encode that phase's roadmap "**done when**" check as a failing
`pytest` test, then implement until it passes. Never write production code without a failing test
driving it. Add a regression test for each design gap you resolve (see `memory.md`). Run `pytest`
before every commit and keep the suite green on the branch. The Phase-1 determinism property test
is the canonical permanent gate.

## Build/test commands

```bash
pip install pydantic numpy sgp4 pyyaml pytest hypothesis skyfield fastapi uvicorn httpx
uvicorn spacesim.ui_web.server:app            # serve the web UI at http://127.0.0.1:8000/
python3 -m pytest                              # runs the whole suite (testpaths = spacesim/tests)
python3 -m pytest spacesim/tests/test_determinism.py    # the Phase-1 determinism gate
python3 -m pytest spacesim/tests/test_import_guard.py   # the Phase-0 engine guardrails
```

The import-guard is a plain pytest test (`test_import_guard.py`), not import-linter — it AST-scans
`spacesim/engine/` for forbidden imports, wall-clock reads, and any `random` use outside `rng.py`.

## Code map (current)

- `spacesim/engine/simtime.py` — sim-UTC as integer microseconds; ISO conversion at the boundary.
- `spacesim/engine/rng.py` — `SeededRng`, the only randomness source; serializable state.
- `spacesim/engine/clock.py` — `SimClock` + `Scheduler` (sub-stepped, deterministic ordering).
- `spacesim/engine/eventlog.py` — `EventLog`, `EventLogEntry`, `Snapshot`.
- `spacesim/engine/world.py` — `WorldState` (pydantic; minimal in P1, extended later).
- `spacesim/engine/handlers.py` — event-handler registry (`(world, payload, rng) -> None`).
- `spacesim/engine/simulation.py` — `Simulation` driver + `replay()` + `SavedSession`.
- `spacesim/engine/geometry.py` — frames (GMST ECI↔ECEF), WGS84 geodety, topocentric look angles.
- `spacesim/engine/sun.py` — analytic Sun direction + cylindrical eclipse/lighting test.
- `spacesim/engine/orbit.py` — `OrbitState`, Kepler+J2 element↔state, regime classification.
- `spacesim/engine/propagator.py` — `Propagator` seam: Kepler+J2 (fictional) / sgp4 (TLE).
- `spacesim/engine/entities.py` — `Asset`/`AssetResources`, `GroundSite`, `Sensor`.
- `spacesim/engine/access.py` — `AccessProvider` seam: all six channels + window caching.
- `spacesim/engine/custody.py` — `Track` (on-demand confidence decay) + weapons-quality gate.
- `spacesim/engine/effects.py` — `EffectInstance`/`EffectResolver` seam (5 D's), `is_link_denied`.
- `spacesim/engine/orders.py` — `Order` + `OrderSystem` (validate → window → execute), cyber
  exception, ISL/stored delivery, sensor tasking (auto-select + contention).
- `spacesim/engine/recovery.py` — `RecoverySystem`: multi-pass safe-mode recovery + re-safe-on-persistence.
- `spacesim/engine/bus.py` — `BusState`/`PayloadState` SOH (limits, gating, safe mode, pass-gated view).
- `spacesim/engine/busmodel.py` — `BusSystem`: bus-evolution / telemetry-contact / downlink handlers.
- `spacesim/content/vignette.py` + `vignettes/*.yaml` — vignette schema, loader, world-builder, objectives.
- `spacesim/session/` — `SessionManager` (clock/rewind/inject/TLE-add), `CellController` (fog-of-war),
  `api.py` (`SessionAPI` + `CellView`/`Ack`), `inprocess.py`, `scene.py` (render-from-custody belief),
  `redai.py` (Red doctrine presets), `aar.py` (replay/scrub/branch-compare).
- `spacesim/ui_web/` — `server.py` (FastAPI over the SessionAPI) + `static/` front end: `app.js`
  (command menu + 2D belief map w/ zoom-pan-layers), `globe.js` (self-contained 3D orthographic
  globe w/ rotate-tilt-zoom-zoomto), `style.css`, `index.html`.
- `spacesim/content/vignettes/00-training-basics.yaml` — guided tutorial vignette with a per-cell
  `tutorial` step script (≥5 steps each); drives the manual walkthrough + its screenshots.
- `docs/TRAINING-MANUAL.md` (first-time setup + guided walkthrough) and `docs/manual/` (29 UI
  screenshots incl. 3D globe, command/system menus, and the step-by-step walkthrough; generated by
  `tools/render_manual.py`).
  Run: `uvicorn spacesim.ui_web.server:app` then open http://127.0.0.1:8000/.
