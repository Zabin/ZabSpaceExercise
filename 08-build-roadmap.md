# Build Roadmap — Phased Milestones for Claude Code

Read this first. It sequences the build so each phase is **independently testable** and the
risky/foundational pieces come early. The ordering principle: **engine determinism → access
windows → orders → one vignette end-to-end → UI → remaining vignettes → White Cell polish →
future seams.** Each phase lists a concrete "done when" check.

## Phase 0 — Project skeleton & guardrails
- Set up the `spacesim/` layout from `02-tech-stack-recommendation.md`.
- Add `pytest`, `pydantic`, NumPy, Skyfield/`sgp4`, YAML.
- Add an **import guard** (e.g., import-linter) enforcing: `engine/` imports no UI/transport;
  resolution code reads no wall clock and no global RNG.
- **Done when:** empty engine package imports clean and the import guard test passes.

## Phase 1 — Deterministic core foundation
- Implement `WorldState`, entities, and schemas (`04-data-model.md`) as pydantic models.
- Implement `SimClock`, `Scheduler` (with sub-stepping), `EventLog`, `Snapshot`, seeded `Rng`.
- Implement save/replay: `{initial_state, seed, snapshots, eventlog}` round-trips.
- **Determinism property test:** replaying the same eventlog from snapshot 0 with the same seed
  yields byte-identical state. *This test gates everything after it.*
- **Done when:** determinism test passes and a session can be saved, loaded, and replayed exactly.

## Phase 2 — Orbits & access windows (moderate fidelity)
- Implement `Propagator` (Kepler + J2; TLE path via Skyfield) and `AccessProvider` with all six
  channels (uplink, downlink, observation, jam footprint, weapon engagement, RPO proximity).
- Implement maneuver as impulsive burns editing elements; track delta-v budgets.
- Implement window caching (recompute on maneuver / horizon advance).
- **Done when:** for a known LEO sat + ground station, computed pass times/durations match a
  reference (e.g., Skyfield direct calc) within tolerance; GEO shows continuous regional access;
  MEO shows long passes. Unit tests cover each channel.

## Phase 3 — Orders, effects, and the resolver
- Implement `Order` issue → validate (ownership/ROE/resources/window/track gate) → queue →
  execute at window.
- Implement `EffectResolver` for the five categories → five D's, with reversibility, debris
  spawn (kinetic), attribution signals, resource consumption.
- Implement the **cyber exception** (not window-gated; `{vector, success_prob, persistence,
  patchable}`).
- Implement `custody`/`Track` with decay and the weapons-quality gate.
- **Done when:** orders correctly queue to the next window; a jam denies a link during its
  footprint window; a kinetic strike spawns debris and trips a political-consequence side effect;
  cyber resolves outside any pass; custody decays and resets on observation. All covered by tests.

## Phase 3.5 — Bus & payload operations model (HEADLESS)
Implements `01-research/06-bus-and-payload-operations.md`. Adds the authentic operator texture.
- Implement `BusState` per satellite (power+eclipse, attitude/pointing, propellant, thermal,
  storage, comms) evolving in the engine tick, each with soft/hard limits → green/yellow/red.
- Gate the payload on the bus: no power → payload off; bad attitude → can't point; full storage
  → can't collect; propellant drained → can't maneuver.
- Implement **safe mode** as a state entered from a bus fault, power crisis, or a cyber/EW
  effect; it disables the payload until the operator spends pass(es) recovering it. Inducement
  is the **probabilistic susceptibility check** from `12-safe-mode-loop.md` §6.1 (not
  automatic), modulated by the `safe_mode_susceptibility` dial and defender hardening/posture.
- Implement **pass-gated telemetry**: the *ground-visible* SOH snapshot updates only on contact
  (pass/ISL); a stored-telemetry dump at the next pass can reveal an out-of-contact event
  (e.g., entered safe mode an hour ago).
- Implement per-type `payload_state` (SATCOM interference; ISR collection queue/storage/downlink;
  SIGINT/SDA tasking feeding `TrackCatalog`; space-control effector + uncertain effect
  assessment) and the `telemetry_db`/`command_db` per asset template.
- Add the `ops_fidelity` vignette parameter (`tactical | realistic | full_ttc`).
- **Done when (headless):** a satellite drains its battery in eclipse and trips a yellow→red
  power alarm; a cyber effect forces safe mode and the operator only learns of it at the next
  pass via the stored-telemetry dump; ISR storage fills and blocks further collection until a
  downlink; and `ops_fidelity=tactical` collapses the bus to a single health bar.
- Implement `SessionManager` (load/tune/start, clock control, **rewind/undo/branch** via
  truncate+replay), `CellController` (permissions + **fog-of-war `CellView`**), and the
  in-process `SessionAPI`.
- Implement the vignette/parameter/inject loaders.
- Bring up **Vignette 1 (LEO ISR Denial)** fully, driven by a test harness (no GUI yet).
- **Done when:** a scripted test plays Vignette 1 to a win condition, then **rewinds and branches**
  to a different outcome, all through the `SessionAPI`, with fog-of-war verified (Red cannot see
  Blue hidden state via the API).

## Phase 4.5 — Planning & tasking scheduler (HEADLESS)
- Implement the unified **PlannedActivity** scheduler (`04-data-model.md` §6.5,
  `11-command-planning-and-tasking.md`) handling both `command` and `collection` kinds.
- Command delivery paths: **ground uplink** (next station pass), **ISL relay** (via an
  isl_capable peer when geometry permits — much sooner than a distant ground pass), and
  **stored program** (time/condition-triggered onboard). Re-validate at execute time.
- Sensor tasking: search/track/characterize/cue intents; sensor selection by viable
  collection window and expected yield; **task contention/prioritization** (a sensor does one
  thing at a time); reports update the `TrackCatalog` and shrink uncertainty.
- Implement the **safe-mode recovery procedure** as a `PlannedActivity` chain (detect→confirm→
  diagnose→clear-faults→re-point→re-enable-payload→verify) with per-step failure/retry across
  passes, plus the **re-safe-on-persistence** logic and the `safe_mode_recovery_difficulty` /
  `safe_mode_root_cause_persists` dials (`12-safe-mode-loop.md`).
- **Done when (headless):** an operator script can queue a command to a sat with no current
  ground pass and see it execute at the next pass *or* sooner via ISL; can task a sensor,
  watch a track's confidence rise / uncertainty fall on report, and find that the resulting
  weapons-quality track now unlocks a previously-blocked engagement (**task → custody → unlock
  command → execute at window**); and — with `safe_mode_susceptibility=fragile` — a cyber
  effect safes a Blue sat, Blue confirms it only at the next pass, runs a multi-pass recovery,
  is **re-safed** because the modem vuln is unpatched, then succeeds after patching; setting
  `safe_mode_recovery_difficulty=quick` collapses recovery to one pass.

## Phase 5 — UI (chosen stack) over the API
Read `09-gui-principles.md` first — it is a hard constraint set, not decoration (CAF
semi-technical operator audience; geometry never hidden; show belief + uncertainty; always
answer "why can't I?"; plan-first).
- **2D world map** with ground tracks/footprints, per-asset **pass-timeline ribbon** +
  next-contact countdown, **order panel** with scheduled-execution display, **command/collection
  queue** (editable/cancellable), **track panel** with decaying confidence, message feed.
- **Fleet SOH rollup + drill-down** (fleet → satellite → subsystem → parameter) with limit-based
  red/yellow/green coloring, an **alarm/event log**, and a **telemetry & payload panel** showing
  the last pass-gated snapshot with its timestamp (per `01-research/06`). Pass-plan building
  validates before release.
- **White Cell control panel** (vignette picker + parameter controls + time controls + inject
  panel) and the **single-player cell-switcher** (White/Red/Blue views over one session).
- Implement the shared **render-from-custody layer**: the map draws only the cell's
  `TrackCatalog`, with affiliation + confidence symbology (solid / aging+ellipse / ghost / "?").
- **Done when:** a facilitator can load Vignette 1, tune parameters, start, play/ff/rewind/undo,
  fire an inject, switch cells, plan a command into a future window, task a sensor, and watch
  windows + custody gate every action — entirely from the GUI, with every disabled control
  explaining itself.

## Phase 5.5 — SDA-derived 3D viewer
- Build the 3D globe per `10-sda-3d-viewer.md` as a **pure consumer** of the same per-cell
  belief stream the 2D map uses (no truth ever reaches Red/Blue clients).
- Render own assets (known), tracks with **growing uncertainty volumes** between observations,
  ground-site coverage, day/night terminator, LOS/observation/RPO overlays, and predicted
  paths; bind to the sim clock so volumes bloom over time and snap on sensor reports.
- White Cell viewer mode may toggle ground truth and "see-as Red/Blue" for adjudication/AAR.
- Suggested: CesiumJS on the web stack. **Done when:** in Vignette 2, Blue watches a hostile
  GEO track's uncertainty volume grow after it stops tasking, then shrink when it re-tasks an
  optical sensor — and the Red client never sees anything Red hasn't observed.

## Phase 6 — Remaining vignettes & content tooling
- Author Vignettes 2–7 as data files; verify each exercises its target subsystem
  (RPO closing, EW geolocation loop, escort interpose, debris/escalation, cyber-outside-passes,
  custody hunt).
- Implement **TLE add/name** in the White Cell force editor (real named satellites alongside
  fictional defaults) with validation + error surfacing.
- Add the **Red doctrine profiles** (china_integrated / russia_ew_first / generic) as selectable
  AI-Red behavior presets.
- **Done when:** all seven run from the picker with their parameters, and a real satellite added
  by TLE propagates and generates correct passes next to fictional assets.

## Phase 7 — Capstone & after-action review
- Bring up **Vignette 8 (Multi-Domain Capstone)** — the integration test for every subsystem.
- Polish the **AAR replay**: event-log scrubber, jump-to-decision, branch comparison,
  objective/escalation tracker, exportable session summary.
- **Done when:** Vignette 8 runs a full synchronized Red campaign; White Cell can replay it
  end-to-end, scrub to any decision point, and compare two branches.

## Phase 8 — Future seams (document/scaffold, don't fully build)
- Confirm the **high-fidelity swap**: write a thin alternate `Propagator`/`AccessProvider`/
  `EffectResolver` stub behind the same interfaces to prove the seam (e.g., a real link-budget
  `quality`), even if not completed.
- Confirm the **multiplayer seam**: stand up a minimal FastAPI/WebSocket wrapper over
  `SessionAPI` serving `CellView`s to two browser tabs as a proof, per `07-api-and-networking.md`.
- **Done when:** swapping a fidelity implementation requires no engine/gameplay changes, and a
  second machine/tab can receive a fog-filtered view through the network wrapper.

---

## Definition of done for v1 (single-machine PME tool)
1. Deterministic engine with exact rewind/undo/branch (property-tested).
2. Moderate-fidelity orbits + all six access-window channels, TLE-capable.
3. Full order/effect/cyber/custody model with the five-D's resolver and debris/escalation.
4. Session layer with fog-of-war and the in-process `SessionAPI`.
5. A working UI: world map, pass timelines, countdowns, order queue, and the full White Cell
   control surface (vignette tuning, time travel, injects, AAR replay).
6. All eight vignettes loadable and tunable; fictional defaults plus real-TLE asset addition.
7. Clean seams proven for high fidelity and LAN multiplayer.

## Risk notes for Claude Code
- **Determinism is load-bearing.** If rewind/undo ever diverge, the cause is almost always a
  stray wall-clock read or un-seeded RNG. The Phase-1 property test must stay green forever.
- **Sub-stepping the clock** is essential — a naive large time step at 600× will skip short LEO
  passes and break realism. Always advance to the next event, never past it.
- **Keep fog-of-war at the API**, not in the UI, or the future multiplayer clients will leak
  state.
- **Vignettes are data.** If scenario logic starts leaking into Python, stop and move it back
  into the YAML + inject/effect primitives.
