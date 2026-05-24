# Tech Stack Recommendation

The user's direction: **Python-based core**, with the UI either Python-native or web, and the
core kept UI-agnostic. This document recommends a concrete stack and justifies it, while
leaving the final call to Claude Code. Nothing here is binding except the principle that the
**engine must not depend on the UI**.

## Recommended stack (primary recommendation)

| Layer | Recommendation | Why |
|---|---|---|
| **Language** | Python 3.11+ | User's choice; rich astrodynamics ecosystem; fast enough at moderate fidelity with vectorized NumPy. |
| **Engine math** | NumPy; **Skyfield** and/or **Astropy** for time/coordinate frames | Skyfield handles TLEs, SGP4, GMST, topocentric look-angles cleanly — exactly the moderate-fidelity needs, and it *is* the high-fidelity path too. |
| **Orbit propagation** | `sgp4` library (via Skyfield) + a simple Keplerian+J2 fallback | TLE-native (satisfies the real-satellite requirement) with a lightweight analytic option for fictional assets. |
| **Data model** | `pydantic` v2 | Typed entities, validation, and clean (de)serialization of vignette/asset/effect YAML and save files. |
| **Content files** | YAML (via `ruamel.yaml` or `pyyaml`) | Human-authorable vignettes and templates. |
| **Session API** | Plain Python abstract base classes / Protocols in v1 | The in-process API; becomes the network contract later. |
| **Persistence** | JSON save files (snapshots + event log); SQLite optional later | Simple, inspectable, replay-friendly. |
| **Tests** | `pytest` + property tests for determinism | Determinism must be enforced by tests (same seed → same result). |

## UI options — pick one, engine is unaffected

### Option A (recommended for v1): **Web UI** — FastAPI + a browser front end
- **Backend:** FastAPI wrapping the Session API; serves state and accepts intents over HTTP/
  WebSocket. In v1 it talks to the engine in-process.
- **Front end:** a single-page app (plain JS/Svelte/React — Claude Code's choice) with:
  - a **2D world map** with ground tracks, footprints, and ground stations (Leaflet/D3, or a
    canvas), plus an optional simple **3D globe** (CesiumJS) later;
  - per-asset **pass-timeline ribbons** and **next-contact countdowns**;
  - the White Cell control panel.
- **Why recommended:** the future LAN-multiplayer story is *trivial* with a web stack — the
  three cells just open three browsers pointed at the server. WebSocket is the natural network
  seam. Cross-platform with zero install for players.

### Option B: **Python-native desktop** — PyQt6 / PySide6 (with `pyqtgraph` for plots)
- One desktop app embedding the engine directly; cell-switcher for the single player.
- **Why you might choose it:** fully offline, no browser, tight integration, easy to package
  with PyInstaller. **Trade-off:** multiplayer later means adding a network layer the web
  option gets almost for free.

### Recommendation
**Build the web option (A).** It best fits "single machine now, LAN multiplayer later" because
the network seam is already there, and it keeps the UI completely decoupled from the engine. If
strict offline/no-browser operation is a hard requirement, choose B — the engine code is
identical either way.

## Mapping / visualization libraries (whichever UI)
- 2D ground tracks & footprints: D3 or Leaflet (web) / `pyqtgraph` (desktop).
- 3D globe (optional, later): CesiumJS (web) — excellent for orbital visualization.
- Orbit/coverage geometry comes from the engine; the UI only draws what the engine computes.

## Dependencies to avoid in the engine
- **No UI imports in the engine package** (enforced by project structure / import-linter).
- **No wall-clock calls in resolution logic** — only the injected sim clock, or determinism
  breaks.
- **No hidden global RNG** — a single seeded RNG passed through state, or rewind won't reproduce.

## Suggested project layout
```
spacesim/
├── engine/            # deterministic core — NO ui, NO network imports
│   ├── world.py       # WorldState, entities (pydantic)
│   ├── clock.py       # sim clock + scheduler
│   ├── propagator.py  # Propagator interface + moderate impl (Skyfield/Kepler+J2)
│   ├── access.py      # AccessProvider interface + moderate impl
│   ├── effects.py     # EffectResolver interface + impl (5 D's, debris, cyber)
│   ├── custody.py     # SDA tracks + decay
│   ├── eventlog.py    # append-only log + snapshots
│   └── rng.py         # seeded RNG
├── session/           # application layer
│   ├── api.py         # Session API (abstract) ← network seam
│   ├── session.py     # SessionManager (clock control, undo/rewind, injects)
│   ├── cells.py       # CellController + permissions + fog-of-war filter
│   └── inprocess.py   # in-process API impl (v1)
├── content/
│   ├── vignettes/*.yaml
│   ├── assets/*.yaml
│   ├── effects/*.yaml
│   └── tle_import.py  # add/name real satellites from TLEs
├── ui_web/            # OR ui_qt/ — the chosen front end (depends on session, not engine)
└── tests/             # pytest, incl. determinism property tests
```

## Performance note
At moderate fidelity with tens-to-low-hundreds of objects, propagating positions and recomputing
upcoming windows a few times per simulated minute is cheap. Cache windows and only recompute on
maneuver or when the look-ahead horizon advances. This easily sustains high time-multipliers.
