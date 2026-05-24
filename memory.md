# memory.md — working memory & decision log

Living scratchpad for the Space Control sim build. `CLAUDE.md` holds durable project facts; this
file holds **current status, open decisions, review findings to resolve, and a dated decision
log.** Update it as work progresses.

## Status

**Phases 0–3.5 complete and green (54 tests).** P0/P1 deterministic core; P2 orbits & six access
channels (validated against Skyfield); P3 orders + five-D effects + cyber exception + custody;
**P3.5** bus & payload SOH model (`BusState`: power/eclipse, attitude, thermal, propulsion,
storage, comms with green/yellow/red limits), payload gating (safe mode / power-red / full
storage), pass-gated telemetry (`ground_view` refreshes only on contact), and safe-mode
inducement via the §6.1 susceptibility check (hardening + patched-vuln counterplay). `BusSystem`
drives bus evolution as scheduled `bus_tick` events, so it replays byte-identically. The recovery
procedure chain is deferred to Phase 4.5 per the safe-mode doc. Next action: **Phase 4** — session
layer (SessionManager / CellController / SessionAPI) + Vignette 1 end-to-end with fog-of-war.
Build sequence/invariants in `CLAUDE.md`.

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
- **2026-05-24:** Phase 3 design — orders execute as **scheduled simulation events** (queued at the
  next access window), so execution lands in the event log and replays exactly; validation runs at
  issue time (re-validation at execute time is a Phase-4.5 refinement). Effect success is
  probabilistic (seeded), `kinetic` is an explicit flag, ROE is a boolean-flag dict on `OrderSystem`.
- **2026-05-24:** Phase 3.5 — bus evolution runs as scheduled `bus_tick` events (eclipse computed
  from orbit + analytic Sun), keeping continuous SOH change inside the deterministic event log;
  `bus.py` is pure data/limits (no heavy imports) so `world.py` can hold `BusState` without a cycle,
  and `busmodel.py` holds the propagator-aware integration. Pass-gating modeled as a `ground_view`
  snapshot refreshed only by a `telemetry_contact` event.
- **Still open:** content file format (JSON vs YAML) — decide before the Phase-4 content loader
  (imminent). UI stack — defer to Phase 5. EW/bus-stress safe-mode inducement — wire in P6 vignettes.
