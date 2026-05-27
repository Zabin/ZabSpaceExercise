# memory.md — working memory & decision log

Living scratchpad for the Space Control sim build. `CLAUDE.md` holds durable project facts; this
file holds **current status, open decisions, review findings to resolve, and a dated decision
log.** Update it as work progresses.

## Status

**Backend feature-complete through Phase 7 — 122 tests green.** Implemented end-to-end:
P0/P1 deterministic core · P2 orbits + six access channels (Skyfield-validated) · P3 orders +
five-D effects + cyber + custody · P3.5 bus/payload SOH + safe mode · P4 session layer
(SessionManager / CellController fog / in-process SessionAPI) + Vignette 1 · P4.5 planning &
tasking (ISL/stored delivery, sensor tasking + contention, safe-mode recovery chain) · **P5** web
layer (FastAPI over the SessionAPI + browser front end) · **P5.5** render-from-custody belief scene
(`/scene`) + 2D map · **P6** all eight vignettes as YAML + TLE force-add + Red doctrine presets +
data-driven objectives · **P7** capstone Vignette 8 + AAR (read-only replay/scrub, branch compare).
Plus `docs/manual/` (13 data-driven UI screenshots + INDEX) and `docs/TRAINING-MANUAL.md`.

**Caveat:** the browser GUI is *unverified headless* (no browser installable); every backend path
(endpoints, fog, objectives, scene, AAR) is test-covered, and the screenshots are faithful
data-driven renderings, not browser captures. **Remaining:** P5.5 full CesiumJS 3D globe (v1.1);
**P8** — document/scaffold the high-fidelity and LAN-multiplayer seam proofs. Invariants in `CLAUDE.md`.

### Earlier (P4.5) summary
**P4.5** adds the planning &
tasking layer: command **delivery paths** (ground uplink / ISL relay via a crosslink-capable peer /
stored program — earliest wins, re-validated at execute), **sensor tasking** (intents, `auto`
sensor selection, incremental confidence, and contention that serializes tasks onto later windows),
and the **safe-mode recovery chain** (`RecoverySystem`: confirm at first contact → multi-pass
recovery sized by `safe_mode_recovery_difficulty`, with **re-safe-on-persistence** until the root
cause — e.g. an unpatched cyber vuln — is removed). New `isl_link` access channel.

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
- **[RESOLVED P6] Vignettes engine-loadable:** all **eight** vignettes (`01`–`08`) are concrete,
  loadable YAML (real orbits, sited ground stations/sensors, typed dials, declarative objective
  metrics). Objective evaluation is data-driven (`evaluate_objectives` dispatches on `metric.kind`).
- **[RESOLVED P6] Red doctrine profiles:** `china_integrated` / `russia_ew_first` / `generic`
  implemented as behavior presets in `session/redai.py` (`RedDoctrine.step`), issued through the
  normal OrderSystem (window/ROE/custody constrained).
- **[RESOLVED P6] TLE force-add:** `SessionManager.add_tle` validates (format + sgp4) and adds a real
  named satellite that propagates and generates passes (`POST /force/tle`).
- **[RESOLVED P5.5] Belief render:** `session/scene.py` `build_scene` is the render-from-custody
  stream (own assets + tracks with growing uncertainty); 2D canvas map consumes it; Cesium 3D = v1.1.
- **[RESOLVED P7] AAR:** `session/aar.py` — deterministic read-only replay (`state_at`/`objectives_at`),
  decision timeline `report`, and `compare_branches`.

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
- **2026-05-24:** **UI stack = web (FastAPI + browser)** (resolves the long-open decision). Rationale:
  the LAN-multiplayer seam comes nearly free (WebSocket over the same SessionAPI), zero-install, and
  the backend is unit-testable headlessly (TestClient) whereas a PyQt GUI is not. A localhost FastAPI
  server still satisfies "offline-capable". Web layer is `spacesim/ui_web/`; engine import-guard
  unaffected (it only scans `engine/`).
- **2026-05-24:** Phase 4.5 — command delivery picks the **earliest** of ground/ISL/stored windows
  and stamps `delivery_path`; ISL modeled as a new `isl_link` access channel (sat-sat LOS within
  `isl_max_range_m`) via a cell-owned `isl_capable` relay. Sensor reports raise confidence
  incrementally (default gain 1.0; characterize gated by intent). Safe-mode recovery sized by
  difficulty (quick=1/realistic=2/punishing=3 passes); re-safe if the cause persists.
- **2026-05-25:** Phases 5.5/6/7 — belief scene (`/scene`) + 2D map; all eight vignettes as YAML with
  data-driven objective metrics; TLE force-add; `RedDoctrine` presets; capstone V8 + AAR
  (read-only replay/scrub/branch-compare). Refactor pass: `effects.py` uses a `TYPE_CHECKING`
  import for `WorldState` (pyflakes-clean, no runtime cycle); dead branches/imports removed.
- **2026-05-25:** Wrote `docs/SSN-DESIGN.md` — ~10-page plan for a mock Space Surveillance Network
  operators can submit observation requests to. User choices: **per-cell** networks (Blue coalition /
  Red national), **hybrid** turnaround (earliest viable window within priority max-wait + processing/
  dissemination delay; coalition/saturation add delay), **four** dispersion presets (sparse/regional/
  global/proliferated) with sensor-type→regime coverage (radar LEO/MEO, optical MEO/GEO, space-based
  GEO/cislunar) and global spread, **per-vignette opt-in** (on for V7/V8). Reuses AccessProvider +
  observe/Track + scheduler/eventlog + fog; resolves as logged `ssn_collect`/`ssn_deliver` events
  (replay-safe). Design only; not yet built.
- **2026-05-25:** Wrote `docs/OPERATOR-UI-DESIGN.md` — a ~20-page operator-console UI design spec
  (research synthesis of `06`/`09`/`13`/`05`/`11`/`12` + the implemented engine). Covers every
  payload/mission/operator type per cell, the button-logic contract (visible/enabled/disabled-reason/
  confirm), monitoring·troubleshooting·tasking user flows, attack-signature→action mapping, a widget
  library, per-payload detail packs, UI-state matrix, wireframes, and a panel→endpoint binding table
  (consumes existing routes; no engine change). A *future* implementation guide, not yet built.
- **2026-05-25:** Added **save/resume** (`SessionManager.save_state`/`from_state`: persists eventlog +
  pending scheduled events + the order registry; resume re-derives the world via `_rebuild` and is
  byte-identical incl. queued orders; `Scheduler.pending()`; `/save` & `/load_save`), an **AAR
  scrubber** (`aar.snapshot_at` → `/aar/at?seq=`, read-only state at any event; UI slider), and a
  **fleet SOH rollup + alarms feed** (`SessionManager.alarms` aggregates per-asset symptom logs +
  consequences, fog-filtered; `/alarms/{cell}`; UI rollup dot + feed). `OrderAck` gained `id`.
  101 tests green. Screens 33 (scrubber) + 34 (alarms/SOH) added.
- **2026-05-25:** Menu/feature flesh-out — a **cancellable command queue** (`OrderSystem` now ids +
  registers orders; `Scheduler.cancel(tag)` skips a not-yet-fired event so it never logs → cancel is
  replay-safe; `list_orders`/`cancel_order` + `/orders/{cell}` & `/cancel`), a **pass-timeline**
  (`windows_ahead` → `/windows/{cell}/{asset}`, upcoming uplink/downlink windows), and an **inject
  list** (`/injects`). UI adds the queue panel (with cancel), the ribbon, and an inject dropdown.
  98 tests green (incl. cancel-is-replay-safe).
- **2026-05-25:** Added a **country map** (coastlines + country borders) to both viewers: committed
  `static/world.json` generated offline by `tools/build_coastlines.py` from `basemap-data` (shape-
  preserving radial decimation, ~512 coast + 446 border polylines, ~314 KB; coarse fallback if
  basemap can't install). Shared `world.js` draws it under each viewer's own projection (2D + globe);
  the Pillow renderer mirrors it. Added a **subsystem telemetry drill-down**: `engine/telemetry.py`
  is a **read-time** seeded sampler (hash value-noise; never touches RNG/state) with per-vector
  **signatures** (jam→RX power↑/CN0↓/BER↑; cyber→FSW errors↑ & FSW=safe; DE→SNR↓/optics↑;
  power→SoC/voltage sag; kinetic→loss-of-signal) — symptoms only, **cause never labeled**, operator
  diagnoses. `ActiveEffect` gained `category`/`template` to drive link signatures. Endpoints
  `/telemetry/{cell}/{asset}[/{param}]` (fog-filtered). UI graphs via `graph.js`. 94 tests green.
- **2026-05-25:** Authored `docs/TRAINING-MANUAL.md` (first-time setup + run + guided walkthrough)
  and `docs/manual/` (data-driven UI screenshots, generated by `tools/render_manual.py`).
- **2026-05-25:** Added a **training vignette** (`00-training-basics.yaml`) with a per-cell
  `tutorial` step script (6 Blue + 6 Red, each a real verified order — `test_training.py`), a
  **guided walkthrough** in the manual (§5), and a self-contained **3D globe viewer** (`globe.js`,
  orthographic projection, no libs) with rotate/tilt/zoom/zoom-to/spin/reset; the 2D map gained
  zoom/pan/center/layer controls; the command panel filters actions by asset kind. `SceneView` now
  carries the subsolar point for day/night shading. Screenshot set expanded to 29 (adds 3D globe,
  White-Cell controls, command menu, and 12 walkthrough steps). User chose: own 3D viewer,
  manual-only tutorial, data-driven screenshots; CesiumJS not used.
- **2026-05-27:** Reviewed `docs/OPERATOR-UI-DESIGN.md` for consistency — endpoints (§14),
  validator reason strings (§12.2), and `cells.py`/`CellController.view` / `bus.overall_status`
  references all match the code. Then began implementing the spec's most load-bearing un-built
  element, the **§12 button-logic contract**: added `OrderSystem.dry_run()` — a read-only mirror of
  `issue()` (extracted shared `_plan`/`_plan_command`/`_plan_collection`/`_plan_cyber` planners;
  `commit=False` skips schedule/registry/booking) — plus `SessionManager.validate_order`,
  `InProcessSession.validate_order`, and `POST /order/validate`. Front-end compose form now
  **dry-runs on every edit** and pre-disables **Issue** with the engine's own reason string
  (`REASON_TIPS` plain-language tooltips) + previews the scheduled window/delivery path. Fixed a
  **pre-existing latent crash** this surfaced: `AccessProvider.windows` raised `KeyError` for an
  unknown endpoint id (e.g. a command `via` a station not in the force) — now guarded
  (`_endpoints_present`) to degrade to no-access for both `issue()` and `dry_run()`. Browser-verified
  (Playwright/bundled Chromium): accept shows "✓ will queue · ground_uplink · window …", reject
  pre-disables with the reason + tooltip, invalid-JSON guarded locally. **106 tests green** (+5:
  `test_validate_order.py` — dry-run is side-effect-free & replay-identical, matches `issue`, surfaces
  reasons, enforces ownership fog, unknown-station→no_window). pyflakes clean.
- **2026-05-27:** Continued the operator-UI build with the troubleshooting heart (§5.3 / §9):
  **compare-to-nominal**. `telemetry.sample/series` gained `nominal=True` → returns the clean
  seeded baseline+noise with **no attack term** (still read-time/replay-safe; destroyed asset keeps
  a nominal trace since LOS is itself a symptom). Threaded through `get_series`/`InProcessSession`
  and the series endpoint as `&nominal=1`; `graph.js` draws an optional faint dashed **ghost** under
  the live trace; the drill-down has a "compare to nominal" toggle. So a jam/cyber/DE signature reads
  as the gap between the two lines, cause still unlabeled (C1). **108 tests green** (+2: nominal
  strips the signature for the overlay & matches a never-attacked trace; nominal sampling is
  deterministic + read-only). Browser-verified wiring (toggle fires `nominal=1`, ghost renders, no
  console errors); the deviation magnitude itself is unit-proven.
- **2026-05-27:** Completed the buildable remainder of the operator-UI plan. **Fleet rail (§4.1)**:
  new `SessionManager.next_contacts(cell)` + `GET /next_contacts/{cell}` (reuses the pass-timeline
  search; fog-filtered) drives a **next-contact countdown** (amber <5 min / red <1 min), plus a
  **battery-SoC gauge**, **alarm badge**, and an All/Bus-red/Under-attack/Safed **filter bar**.
  **Alarm deep-link (§4.3)**: clicking an alarm opens that asset's drill-down. **Consequence-confirm
  (§12.3)**: the kinetic `engage` verb gets a deliberate confirm before issue. **Keyboard (§12.4)**:
  `j/k` cycle actor, `c` focus compose, `g` open graph (ignored in fields). Fixed a **fog-adjacent
  UI race**: a slow god-view `refresh()` could resolve after a player-cell switch and clobber the
  fog-filtered view (briefly listing the other side's assets in the command menu) — `refresh()` now
  carries a supersede token (`REFRESH_SEQ`) and aborts before writing if overtaken. **109 tests
  green** (+1: `next_contacts` matches the pass timeline & respects fog). Browser-verified (columns,
  filter empties on Safed, `j` wraps within the fog-filtered list, race gone). **Engine-blocked:**
  P-UI-2 bus-card & P-UI-4 payload-console *command buttons* need the `13-...` catalog verbs
  (`eps.*`/`adcs.*`/`satcom.*`/…) that have **no engine handlers** — deferred (an engine verb→effect
  workstream) rather than shipping dead buttons.
- **2026-05-27:** Started the **engine verb→effect workstream** so the bus/payload command buttons
  become real (unblocking P-UI-2/§6). New `spacesim/engine/buscommands.py` (`apply_command` +
  `can_issue`) implements a first deterministic, observable batch: `eps.shed_load`/`eps.restore_load`
  (adds `power.loads_shed` → `advance_bus` drains 0.4× when shed, so SoC sags slower), `adcs.set_mode`
  (sets attitude mode/pointing), `satcom.mitigate_interference`/`shift_users` (adds
  `payload_state.interference_mitigation` 0..1, capped 0.8; telemetry's jam terms now scale by
  `1−mitigation`, so anti-jam **shrinks the RX-power/CN0/BER signature** — the central troubleshooting
  loop, and it pairs with compare-to-nominal). Wired through the order system as a new **`command`
  action** (uplink/stored delivery via `_plan_command`, re-validated at the `execute_command` handler,
  logged → replay-safe). New validator reasons `unknown_command`/`no_payload_for_verb`/
  `payload_unavailable` (payload verbs gated by payload **type** + bus availability). UI: the command
  menu offers the verbs (bus verbs on satellites; payload verbs only on the matching payload type),
  composed as `action:"command", params.verb`, with the same dry-run pre-disable + tooltips.
  **117 tests green** (+8 `test_bus_commands.py`: shed slows drain, restore undoes, set_mode, mitigation
  shrinks the jam signature but not below nominal, lost-asset graceful, order executes + replay-safe,
  validation reasons incl. fog + safe-mode payload gating). Determinism + import-guard green; browser-
  verified the live verbs (offered, dry-run preview, queued). **Next verbs** (`tcs.*`/`cdh.*`/`comms.*`,
  full payload sets) extend the same dispatch; six-card bus grid layout is the remaining UI piece.
- **2026-05-27:** Verb catalog **batch 2** (ISR mission loop + telemetry recovery, all observable):
  `eps.set_charge_mode` (adds `power.charge_mode`; `advance_bus` scales charge ×1.5/0.5 fast/trickle),
  `cdh.dump_storage` (`refresh_ground_view` → fresh SOH snapshot), `isr.collect_now`/
  `isr.schedule_collection` (set `payload.collecting`, gated by `can_collect` → storage fills). Payload
  type-gating generalized to a set (`isr_eo`/`isr_sar`). UI offers them by payload type. **122 tests
  green** (+5). All extend the same `apply_command` dispatch.
- **Still open (deferred / v1.1+):** browser GUI **unverified headless** (needs a human or
  browser-driver to confirm visuals; backend covered). Sat caps ≤24/≤3/48 not yet validated at
  content load. Posture/defense command persistence (`def.harden`, `def.set_threat_warning`).
  EW/bus-stress safe-mode inducement (only cyber exercised). Contention booking registry not
  rewind-safe. `Order` is an engine dataclass crossing the API in-process — make it a serializable
  pydantic message at the network transport. Full CesiumJS 3D globe (v1.1). **P8** seam proofs.
