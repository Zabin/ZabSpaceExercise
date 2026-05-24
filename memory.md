# memory.md — working memory & decision log

Living scratchpad for the Space Control sim build. `CLAUDE.md` holds durable project facts; this
file holds **current status, open decisions, review findings to resolve, and a dated decision
log.** Update it as work progresses.

## Status

**Phases 0–2 complete and green (30 tests).** Deterministic core (P0/P1) plus orbits & access
windows (P2): Kepler+J2 propagator for fictional assets, sgp4 for TLE assets, and an
`AccessProvider` computing all six channels (uplink/downlink, observation w/ lighting, jam
footprint, weapon engagement, RPO proximity) with edge-bisection window finding and caching. The
look-angle pipeline is validated against Skyfield (<1° over 3 h for an ISS TLE). Next action:
**Phase 3** — orders → validate → queue → execute, the five-D `EffectResolver`, the cyber
exception, and custody/`Track` with the weapons-quality gate. Build sequence/invariants in `CLAUDE.md`.

## Internalized summary

A White Cell facilitator runs a hot-seat PME exercise; Red and Blue cells fly fleets of space and
ground assets as bus + payload operators. The core loop: orbital geometry gates everything —
operators **plan** commands to the next access window and **task** scarce sensors to build/lose
custody, then weigh reversible vs. escalatory counterspace effects across the five-D ladder. A
deterministic engine sits behind a UI-agnostic `SessionAPI` with fog-of-war, enabling exact
rewind/undo/branch and a future LAN-multiplayer swap.

## Open decisions to settle at/before Phase 0

- **UI stack:** web (FastAPI + browser, recommended) vs. desktop PyQt. Confirm before Phase 5;
  doesn't block Phases 0–4.5 (engine is UI-agnostic).
- **Content file format — CONTRADICTION:** `00-BUILD-SPECIFICATION.md` §3.1 says "one **JSON**
  file per vignette," but `02-tech-stack-recommendation.md`, `01-architecture-overview.md`, and
  `08-build-roadmap.md` all describe **YAML** loaders. Lean YAML (human-authorable; 3 docs agree),
  but flag that the binding spec says JSON. Decide before writing the content loader.
- **3D viewer scope — AMBIGUITY:** build-spec defers the full globe to v1.1, but roadmap Phase 5.5
  and `10-sda-3d-viewer.md` build belief-state 3D *during* v1. Resolve as: v1 = belief-state
  filtering/rendering proof; v1.1 = full CesiumJS globe UI.

## Review findings to resolve as the relevant phase is reached

Each gets a **regression test** when fixed (test-driven workflow).

- **Doc bug — `08-build-roadmap.md`:** the **Phase 4** header is missing; the SessionManager /
  CellController / SessionAPI / Vignette-1 bullets are appended under Phase 3.5, and the phase
  numbers jump 3.5 → 4.5. Treat the appended block as Phase 4 (session layer + first vignette).
- **Caps unenforced (P0/P1):** ≤24 sats / ≤3 per constellation / 48 ceiling are stated but no
  loader/validator checks them — add pydantic validation at content load.
- **Effect resolution undefined (P3):** deterministic vs. probabilistic success is unspecified
  (`03-counterspace-taxonomy.md` vs. `06-bus-and-payload-operations.md`) — decide in `EffectResolver`.
- **Safe-mode triggers (P3.5):** which subsystem faults induce safe mode is unspecified; the
  subsystem enum (`power|attitude|thermal|propulsion|cdh|comms`) is undefined; environmental and
  bus-fault inducement are specified but only cyber is exemplified.
- **Enum overload (P3):** `intended_outcome: safe_mode` doesn't fit the five-D enum — model it as
  a special outcome, not a sixth D.
- **ROE schema missing (P3):** `kinetic_authorized`, etc. are referenced but absent from the
  vignette data model — model as boolean flags inside `parameters`.
- **Kinetic marker missing (P3):** `EffectResolver` has no flag to identify kinetic effects —
  decide `category == 'direct_ascent'` vs. an explicit `kinetic: true`.
- **Posture persistence (P3.5/P4.5):** `def.harden` / `def.set_threat_warning` lifecycle is
  undefined — add `active` and an optional `expires_at`.
- **Sensor contention (P4.5):** prioritization/preemption workflow is underspecified — default to
  FIFO with operator reorder.
- **Vignettes not yet engine-loadable (P4/P6):** all 8 lack `start_epoch_utc`, objective `metrics`,
  concrete orbit tuples/TLEs, and ground-station coordinates; `escalation_thresholds` appears only
  in vignette 05. **Vignette 1 (LEO ISR Denial) is the first spike** — use it to lock the content
  schema, then retrofit the rest.
- **Red doctrine profiles (P6):** `china_integrated` / `russia_ew_first` / `generic` are referenced
  as selectable data presets but none are authored.

## Workflow note

Development is **test-driven**: write each phase's roadmap "done when" check as a failing `pytest`
test first, implement to green, and add a regression test for every resolved finding above.
`pytest` must be green before each commit.

## Decision log

- **2026-05-24:** Sim time is stored as **integer microseconds since the Unix epoch** (not float)
  so replay is byte-identical; ISO-8601 only at the serialization/display boundary (`simtime.py`).
- **2026-05-24:** Import guard implemented as a **pytest AST scan** (`test_import_guard.py`) rather
  than adding the import-linter dependency — same enforcement, one fewer dep.
- **2026-05-24:** Save format = `SavedSession{initial_state, seed, final_time, snapshots, eventlog}`;
  `final_time` pins `world.now` so trailing idle time (advance with no events) replays exactly.
- **2026-05-24:** Moderate fidelity = two-body **+ J2 secular** precession (RAAN/argp/M rates);
  TLE assets propagate via **sgp4** with TEME treated as ECI and a GMST-only ECEF rotation —
  validated within 1° of Skyfield, well inside "moderate." `sgp4` is now a core engine dep;
  `skyfield` is dev-only (reference test). Sun/eclipse use an analytic low-precision model (no
  ephemeris download), keeping the engine offline-capable.
- **2026-05-24:** Delta-v *burn math* (`apply_impulse`) lives in the propagator now; delta-v
  *budget enforcement* (decrementing `Asset.resources.delta_v_ms`, rejecting over-budget) is
  deferred to Phase 3 with the order/validation layer, where the Asset model lands.
- **Still open:** content file format (JSON vs YAML) — not yet forced; decide before the Phase-4
  content loader. UI stack — defer to Phase 5.
