# memory.md — working memory & decision log

Living scratchpad for the Space Control sim build. `CLAUDE.md` holds durable project facts; this
file holds **current status, open decisions, review findings to resolve, and a dated decision
log.** Update it as work progresses.

## Status

**Phases 0–4.5 complete and green (66 tests).** P0–P4 as below; **P4.5** adds the planning &
tasking layer: command **delivery paths** (ground uplink / ISL relay via a crosslink-capable peer /
stored program — earliest wins, re-validated at execute), **sensor tasking** (intents, `auto`
sensor selection, incremental confidence, and contention that serializes tasks onto later windows),
and the **safe-mode recovery chain** (`RecoverySystem`: confirm at first contact → multi-pass
recovery sized by `safe_mode_recovery_difficulty`, with **re-safe-on-persistence** until the root
cause — e.g. an unpatched cyber vuln — is removed). New `isl_link` access channel. Next action:
**Phase 5** — the UI over the SessionAPI (2D map, pass-timeline, order/queue panels, fleet SOH,
White-Cell controls), per `09-gui-principles.md`. Build sequence/invariants in `CLAUDE.md`.

### Earlier (P4) summary
P4 adds the session layer:
`SessionManager` (authoritative; owns Simulation + OrderSystem + BusSystem, time control, and
`rewind_to`/`undo_last` via the engine's replay primitive, re-arming scripted schedule on rewind),
`CellController` fog-of-war (`CellView`: own assets in full, other-side only via own tracks,
effects as attribution-limited symptoms), and an in-process `SessionAPI`. **Vignette 1** is authored
as YAML and runs end-to-end through the API: Blue downlinks imagery for a win, then the session
**rewinds and branches** to a Red win (Red jams the downlink). Fog-of-war verified (Red view never
contains Blue assets/state).

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
- **[RESOLVED P4] Content file format:** chose **YAML** (matches 3 design docs; human-authorable).
  Loader is `spacesim/content/vignette.py` (pyyaml + pydantic). The build-spec's "JSON per vignette"
  wording is noted but not followed; JSON could be added trivially behind the same loader if needed.
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
- **[RESOLVED P3] Effect resolution:** chosen **probabilistic** — `EffectResolver` draws the seeded
  RNG against a per-effect `success_prob` (modulated by cyber posture / patched vector). Success →
  intended outcome, failure → `none`; deterministic under replay (draw is in-state).
- **[RESOLVED P3.5] Safe-mode triggers:** subsystem enum fixed as
  `power|attitude|thermal|propulsion|cdh|comms` (`bus.py`). Attack inducement (cyber/ew) implemented
  via the §6.1 susceptibility check with hardening + patched-vuln counterplay; `cause` records
  `cyber|ew|bus_stress|fault|environment`. Bus-fault/environmental inducement paths are modeled in
  data (`cause`) but only cyber is exercised in tests so far — wire EW + power-crisis inducement
  when the relevant vignettes land (P6).
- **[RESOLVED P3] Enum overload:** `safe_mode` added to the `Outcome` literal as a **special
  outcome** (not a sixth D); the resolver branches on it to call `enter_safe_mode`.
- **[RESOLVED P3] ROE:** `OrderSystem` takes a `roe` dict of boolean flags (`kinetic_authorized`,
  `cyber_authorized`); engage/cyber orders are rejected at validation when their flag is unset.
  Vignettes will surface these as `parameters` and pass them through.
- **[RESOLVED P3] Kinetic marker:** explicit `kinetic: bool` on `EffectInstance` (debris + political
  consequence keyed off it), not category-sniffing.
- **Posture persistence (P3.5/P4.5):** `def.harden` / `def.set_threat_warning` lifecycle is
  undefined — add `active` and an optional `expires_at`.
- **[RESOLVED P4.5] Sensor contention:** a sensor does one task at a time; `OrderSystem` tracks
  per-sensor bookings and pushes an overlapping task to the next non-overlapping window (serialize,
  don't reject). `auto` sensor selection picks the cell's earliest viable, non-contended sensor.
- **[PARTIAL P4] Vignettes not yet engine-loadable:** Vignette 1 now exists as a concrete,
  engine-loadable YAML (real orbit, ground-site coords positioned for an early pass, typed
  parameters, objective metrics + landing-window deadline) — the content schema is locked.
  Vignettes 2–8 still need authoring with the same concreteness (Phase 6).
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
- **2026-05-24:** Phase 3 design — orders execute as **scheduled simulation events** (queued at the
  next access window), so execution lands in the event log and replays exactly; validation runs at
  issue time (re-validation at execute time is a Phase-4.5 refinement). Effect success is
  probabilistic (seeded), `kinetic` is an explicit flag, ROE is a boolean-flag dict on `OrderSystem`.
- **2026-05-24:** Phase 3.5 — bus evolution runs as scheduled `bus_tick` events (eclipse computed
  from orbit + analytic Sun), keeping continuous SOH change inside the deterministic event log;
  `bus.py` is pure data/limits (no heavy imports) so `world.py` can hold `BusState` without a cycle,
  and `busmodel.py` holds the propagator-aware integration. Pass-gating modeled as a `ground_view`
  snapshot refreshed only by a `telemetry_contact` event.
- **2026-05-24:** Phase 4 — `rewind_to`/`undo_last` rebuild state by truncating the event log and
  replaying from the initial state (deterministic core makes this exact); pending future events are
  dropped, so SessionManager **re-arms** scripted bus-ticks/time-injects after a rewind. Injects run
  as logged `inject` events so their world-state effects (message/reveal_asset/political/patch) are
  replay-safe; `change_roe`/`modify_parameter` mutate live (non-engine) state and are noted as not
  replay-safe across a rewind (avoid mid-branch). CellView exposes own assets fully; other-side only
  via the cell's own tracks; effects as symptoms (source shown only if attribution is overt).
- **2026-05-24:** Phase 4.5 — command delivery picks the **earliest** of ground/ISL/stored windows
  and stamps `delivery_path`; ISL modeled as a new `isl_link` access channel (sat-sat LOS within
  `isl_max_range_m`) via a cell-owned `isl_capable` relay. Sensor reports raise confidence
  incrementally (default gain 1.0; characterize gated by intent). Contention is a live (non-world)
  booking registry on `OrderSystem` — it resets implicitly when a new OrderSystem is built but NOT
  on an in-place rewind; acceptable for now (note for Phase 5 session integration). Safe-mode
  recovery sized by difficulty (quick=1/realistic=2/punishing=3 passes); re-safe if the cause
  (unpatched cyber vuln) persists.
- **Still open:** UI stack — **decide at Phase 5 start** (recommendation: FastAPI + web). Posture/
  defense command persistence (`def.harden`, `def.set_threat_warning`) — implement with the Phase 5
  command set. EW/bus-stress safe-mode inducement + Vignettes 2–8 — Phase 6. Order is an engine
  dataclass crossing the API in-process; make it a serializable pydantic message when the network
  transport lands. Contention registry not rewind-safe (see above).
