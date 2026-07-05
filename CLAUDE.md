# CLAUDE.md — Space Control & Orbital Warfare Exercise Simulator

Durable project guide for Claude Code. Read this first, then the docs in the order below. All
prose docs live under `docs/`, routed by [`docs/INDEX.md`](docs/INDEX.md); the structure and its
rationale are in [`docs/DOCUMENTATION-PLAN.md`](docs/DOCUMENTATION-PLAN.md). For "what documents
exist, what's left to write, and what depends on what," check [`ROADMAP.md`](ROADMAP.md) first —
keep it current as you finish or start documentation work.

## What this is

A **professional military education (PME) wargaming tool** for space control and orbital
warfare. A White Cell facilitator runs an exercise; Red and Blue cells command fleets of
space/ground assets as bus and payload operators, constrained by orbital geometry (you can only
command, observe, or attack when access windows permit). Most effects are reversible
(EW/cyber/proximity), not kinetic. Runs single-machine hot-seat *and* multi-tab / LAN
cooperative — every browser tab points at one FastAPI server, fog-of-war is enforced server-side
at the `SessionAPI` / `CellController` boundary.

**Status: backend feature-complete through Phase 8; commands-layer audit completed Jun 2026 (469 tests green, 3 skipped).** Deterministic engine
(P0–P4.5), the web layer (P5, FastAPI + browser front end), the render-from-custody belief
scene + 2D map (P5.5), the full **19-vignette library** (the canonical 8 numbered + the
training-basics onboarding + 5 Red COA + 3 mission-set + 1 learning + 1 novel) as YAML +
TLE force-add + Red doctrine presets (P6 + library expansion), the **capstone Vignette 8 +
AAR replay** (P7), and the **LAN multiplayer transport** (P8:
server-authoritative lazy clock + per-session RLock + session discovery + join-by-hash URL +
multi-monitor pop-out windows). Code under `spacesim/`; content is YAML; UI stack = **web**.
The browser GUI is unverified headless, but every backend path (endpoints, fog, objectives,
AAR, multiplayer clock + locking) is test-covered.

## Authoritative source & reading order

**`docs/architecture/` (the GDS-00…GDS-10 ladder) is the single authoritative architecture and
requirements source for this project, effective immediately — it supersedes `docs/build-spec/` in
its entirety.** This is a deliberate escalation, made by explicit project-owner instruction, beyond
the prior rule (under which a build-spec module stayed authoritative only until its specific GDS
level's own merge gate closed). The supersession is no longer gated module-by-module: build-spec is
superseded as a whole, immediately, including for GDS levels that have not yet been authored.

**What this means where a GDS level is not yet authored.** Per
[`docs/architecture/INDEX.md`](docs/architecture/INDEX.md) §1, GDS-06 (Non-Functional
Requirements) through GDS-10 (Requirements Traceability Matrix) are currently
`⛔ Planned (scaffold only)` — there is no authored content at those levels yet. The corresponding
`build-spec/` module may still be read as the only available descriptive text on that topic, but it
is now **deprecated legacy reference, not a binding tie-breaker**. The old rule ("on any conflict,
the build spec wins") no longer applies anywhere in this project. Where a topic has no authored GDS
level yet, treat it as **not yet having an authoritative statement** — read the legacy build-spec
text for orientation, but do not cite it as binding, and flag a gap rather than treating its
wording as settled. Authoring GDS-06 through GDS-10 to close this gap is now a standing priority.

**Current GDS-ladder status** (full table: [`docs/architecture/INDEX.md`](docs/architecture/INDEX.md)
§1): GDS-00 through GDS-05 are authored with closed merge gates and are fully authoritative.
GDS-06–GDS-10 are scaffold-only; their build-spec counterparts (`04-nfr-milestones-and-risks.md`
§9, `design/04-data-model.md` schema portion, `design/09-gui-principles.md` +
`05-cell-interfaces.md` + `10-sda-3d-viewer.md`, `design/07-api-and-networking.md`, none) are legacy
reference only, per the rule above.

1. [`docs/architecture/INDEX.md`](docs/architecture/INDEX.md) — the GDS ladder; the authoritative
   entry point for architecture and requirements, full stop.
2. [`docs/architecture/05-functional-requirements.md`](docs/architecture/05-functional-requirements.md)
   (GDS-05) for functional/operational requirements, elaborated in full traceability detail at
   [`docs/requirements/01-functional-requirements.md`](docs/requirements/01-functional-requirements.md).
3. For any topic with no authored GDS level yet, [`docs/build-spec/INDEX.md`](docs/build-spec/INDEX.md)
   as **legacy, non-binding reference** pending migration into the GDS ladder.
4. `docs/design/01-architecture-overview.md` + `docs/design/04-data-model.md` — architecture/data
   reference pending their own GDS-03 (already merged)/GDS-07 (pending) migration.
5. [`docs/research/INDEX.md`](docs/research/INDEX.md) (`01`–`06`) — *why* the rules are what they are.
6. `docs/build-spec/04-nfr-milestones-and-risks.md` §10 — the consolidated phase plan (M0–M7) with
   current status (legacy reference; not yet migrated to a GDS level). Deferred items live in
   [`docs/FUTURE-WORK.md`](docs/FUTURE-WORK.md).
7. Remaining [`docs/design/`](docs/design/INDEX.md) docs and [`docs/vignettes/`](docs/vignettes/INDEX.md)
   as each phase needs them.

## Tech stack (leading recommendation — confirm at Phase 0)

From `docs/design/02-tech-stack-recommendation.md`: Python 3.11+, NumPy, **Skyfield**/`sgp4`,
**pydantic v2**, content as data files, **pytest**. UI = **FastAPI + web (Option A)** — the
LAN-multiplayer seam comes nearly free. Desktop PyQt (Option B) is the fallback; the engine is
identical either way.

Project layout (`docs/design/02-tech-stack-recommendation.md` §"Suggested project layout"):
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

- Sample-vignette sizing: **~24 satellites** as a soft guideline for typical White-Cell
  hardware (no engine-enforced cap — user vignettes may scale up). The
  **clock-lag watchdog** in `SessionManager._record_catch_up_lag` warns White Cell when
  the hardware can't keep up. **Constellations ≤3 sats**, each operated/monitored individually.
- **Six access channels:** `command_uplink`, `telemetry_downlink`, `sensor_observation`,
  `jam_footprint`, `weapon_engagement`, `rpo_proximity`.
- **Five effect categories → five D's:** deceive / disrupt / deny / degrade / destroy. **Cyber is
  the exception** — not window-gated; resolves against `{access_vector, success_prob, persistence,
  patchable}` subject to the defender's cyber posture.
- Orbital fidelity: **moderate** (Keplerian + J2, TLE via Skyfield), behind interfaces
  (`Propagator`, `AccessProvider`, `EffectResolver`) so a high-fidelity model drops in later.

## Build phases (consolidated in `docs/build-spec/04-nfr-milestones-and-risks.md` §10)

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
  **P5.5** Render-from-custody belief scene + 2D map + self-contained orthographic 3D globe. ✓
- **P6** Vignettes 2–7 (data) + TLE force-add + Red doctrine profiles. ✓ (all 19 vignette files
  load/run: 8 canonical + training-basics + 5 COA + 3 mission-set + 1 learning + 1 novel)
- **P7** Capstone Vignette 8 + AAR replay (read-only replay/scrub, branch compare). ✓
- **P8** LAN multiplayer transport + multi-monitor pop-outs. ✓ (server-authoritative lazy clock
  + per-session RLock + `/api/sessions` discovery + join-by-URL-hash + Pop-out submenu opens
  layout-culled tabs that join the same session — see `docs/FUTURE-WORK.md` §1).

## The skill pipeline (documentation-driven development)

All spec/doc/implementation work runs through the **numbered skill pipeline** in
[`.claude/skills/README.md`](.claude/skills/README.md) — the number is the run order:
`01-vision` → `02-research-*` (×5, parallel peers — incl. `02-research-training-pedagogy` for the
R600 tier) → `03-architecture-design-synthesis` → `04-requirements-engineering` →
`05-feature-decomposition` → `06-feature-specification` → `07-implementation-planning` →
`08-code-implementation` → `09-package-verification` → `10-integration-review` →
`11-release-readiness`. The training corpus rides the same ladder through **stage peers**:
`08-training-manual-authoring` and `08-vignette-development` (Stage 08 write-siblings of
`08-code-implementation`, splitting the write surface — code / `docs/training/` / vignette YAML)
and `09-training-manual-review` (Stage 09 sibling of `09-package-verification`).
`00-pipeline-manager` is the driver: it keeps a
persistent journal at `docs/pipeline/pipeline-journal.md` (position + run log, reconciled against
the tree's ledgers every run — the tree wins on disagreement), harvests every invoked skill's
findings into `docs/pipeline/backlog.md` and triages every open entry at the start of the next
run, executes the next step by invoking the owning skill (one step per run), and stops at every
human gate. `00-intake` is its stage-00 peer — new features/bugs/observations are filed into the
same backlog (classified, deduped, routed to an entry stage), never implemented by side-channel;
`run-spacesim` is an unnumbered utility. Each skill writes
only its own output scope, routes findings to the owning stage instead of fixing them locally,
and ends every run by saying in chat what changed, what it recommends, and which skill to run
next. Only `08-code-implementation` writes `spacesim/` production code; only `09-package-verification`
writes `VERIFIED`; a specified package is not an authorized one (MSTR-006 §3).

## Test-driven workflow (mandatory)

Build every phase **test-first**: encode that phase's roadmap "**done when**" check as a failing
`pytest` test, then implement until it passes. Never write production code without a failing test
driving it. Add a regression test for each design gap you resolve (see `memory.md`). Run `pytest`
before every commit and keep the suite green on the branch. The Phase-1 determinism property test
is the canonical permanent gate.

## Build/test commands

```bash
pip install pydantic numpy sgp4 pyyaml pytest hypothesis skyfield fastapi uvicorn httpx
python3 -m spacesim.ui_web                                       # reads host/port/reload from spacesim.config.yaml (defaults 127.0.0.1:8000)
uvicorn spacesim.ui_web.server:app                               # equivalent if you prefer uvicorn's CLI
uvicorn spacesim.ui_web.server:app --host 0.0.0.0 --reload       # LAN multiplayer: bind to host IP, share URL
python3 -m pytest                                                # runs the whole suite (testpaths = spacesim/tests)
python3 -m pytest spacesim/tests/test_determinism.py             # the Phase-1 determinism gate
python3 -m pytest spacesim/tests/test_import_guard.py            # the Phase-0 engine guardrails
```

**Server config.** Host, port, and reload come from `spacesim.config.yaml` at the repo root
(loaded by `spacesim/config.py`). Override the path with `SPACESIM_CONFIG=/some/path.yaml`. The
`uvicorn …` CLI form still works for one-off overrides; `python3 -m spacesim.ui_web` is the
config-driven launcher.

**Multiplayer workflow.** White loads + starts a session → URL becomes `…/#sess-N` (shareable).
Open that URL in another tab or LAN machine, click **Blue** or **Red**. The server-side clock
advances exactly once regardless of tab count (lazy catch_up on every read). White-only ⏸ Pause /
▶ Resume toolbar button drives `/api/sessions/{sid}/clock` for all connected clients. **Pop-out
windows** (View → Pop out submenu) join the same session at `?layout=<token>&cell=<cell>` so a
single facilitator can spread globe / map / fleet / order / AAR across multiple monitors.

**LAN trust model (load-bearing).** The cell selector (`White` / `Blue` / `Red`) is **client-side
trust** — there is no per-cell authentication. The fog-of-war filter is applied by
`SessionAPI` / `CellController` to every cell-scoped response, but the no-cell ground-truth
endpoints (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`) deliberately expose ground
truth without a cell binding. **Deploy only on a trusted LAN with cooperative participants.** A
hostile participant on the LAN can read another cell's belief state through `/scene/{cell}` or
`/telemetry/{cell}/...` by sending the other cell's name in the URL. This is by design for the
v1 PME training context (everyone in the room is on the same team learning together) and is
documented as the explicit trust boundary; see `docs/AUDIT-2026-06.md` §D5 / §F1. Hardening
options (per-cell tokens) are tracked in [`docs/FUTURE-WORK.md`](docs/FUTURE-WORK.md).
**The Observer seat's mutation-rejection (IP-1130) is enforced at this same trust level, not a
stronger one** — the server rejects any request asserting `cell=observer`, a real structural
enforcement (it holds even for a request that bypasses the UI entirely), but the seat assertion
itself is still client-side trust like every other cell: a hostile participant simply lying about
`cell` bypasses it the same way they could already impersonate another cell today. This adds a new
rejection rule, not a new authentication mechanism.

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
- `spacesim/engine/access.py` — `AccessProvider` seam: all six channels + window caching; unknown
  endpoint ids (e.g. a command planned `via` a station not in the force) degrade to no-access, not a crash.
- `spacesim/engine/custody.py` — `Track` (on-demand confidence decay) + weapons-quality gate.
- `spacesim/engine/effects.py` — `EffectInstance`/`EffectResolver` seam (5 D's), `is_link_denied`.
- `spacesim/engine/orders.py` — `Order` + `OrderSystem` (validate → window → execute), cyber
  exception, ISL/stored delivery, sensor tasking (auto-select + contention), order queue + cancel.
  Actions: `jam/engage/observe/maneuver/downlink/cyber` + `command` (bus/payload verbs, see `buscommands.py`).
  `dry_run()` is a read-only mirror of `issue()` (validate + window/delivery-path, but schedules/
  registers/books nothing) → powers the UI's "why can't I?" pre-disabled buttons; replay-safe like `scene.py`.
  ROE (`engage`/`cyber`) is resolved per issuing cell (`self.roe[order.cell]`, IP-1172/FR-3420) — the
  engine never branches on legacy-vs-explicit vignette shape, only on the always-cell-keyed dict
  `content/vignette.py`'s `build_world()` produces.
- `spacesim/engine/recovery.py` — `RecoverySystem`: multi-pass safe-mode recovery + re-safe-on-persistence.
- `spacesim/engine/ssn.py` — mock Space Surveillance Network (per `docs/build-spec/08-ssn.md` §17): per-cell
  `SSNNetwork`s instantiated from a dispersion preset (`sparse`/`regional`/`global`/`proliferated`),
  hybrid-turnaround request resolution (earliest viable window inside the priority SLA + processing
  delay; coalition vs. national affiliation), and two deterministic handlers (`ssn_collect` /
  `ssn_deliver`) that stage on `world.ssn_staged` and deliver into the requester's `TrackCatalog`.
  Replay-safe; cancel-before-collect tag-skips both events.
- `spacesim/engine/telemetry.py` — read-time seeded subsystem telemetry (graphs/logs) + attack
  signatures (jam→RX power, cyber→FSW errors, DE→SNR, power sag, kinetic→loss-of-signal). Pure,
  never mutates state/RNG (like `scene.py`). `sample/series(..., nominal=True)` drop the attack term
  → the clean baseline ghost the "compare to nominal" overlay draws (`&nominal=1` on the series endpoint).
- `spacesim/engine/buscommands.py` — real catalog bus/payload/defense verbs (EPS shed/restore/charge-
  mode, `adcs.set_mode`, `cdh.dump_storage`, `satcom.mitigate_interference`/`shift_users`,
  `isr.collect_now`/`schedule_collection`, `def.patch_cyber` for the recovery-loop root-cause fix);
  `apply_command` mutates `BusState`/`PayloadState`/`cyber_vulnerabilities` inside the deterministic
  `execute_command` handler (replay-safe, observable in SOH/telemetry), `can_issue` is the plan-time
  validator gate (payload verbs gated by payload type + bus availability). Carried by the order
  system's `command` action (uplink/stored delivery like `maneuver`). New verbs extend `apply_command`.
- `spacesim/engine/bus.py` — `BusState`/`PayloadState` SOH (limits, gating, safe mode, pass-gated view).
  `ThermalState` carries `temp_c`/`heater_watts`/`radiator_capacity_w` (FW §11.B.11).
- `spacesim/engine/busmodel.py` — `BusSystem`: bus-evolution / telemetry-contact / downlink handlers.
- `spacesim/engine/maneuver.py` — pure compute for six manoeuvre entry modes
  (eci / lvlh / finite_burn / target_coe / hohmann / plane_change).
- `spacesim/engine/isr.py` — ISR beam-mode database (EO/SAR/SDA/weather/mw — the last two added
  by IP-1170, closing `BL-0053`), `effective_gain()`, `soc_drain()`, footprint polygon +
  ground-heading helpers.
- `spacesim/engine/jam.py` — jam modulation database (barrage/spot/sweep/deceptive),
  `effective_radius_km()`, `effective_success_prob()`, footprint polygon (FW §11.A.1).
- `spacesim/engine/engage.py` — kinetic-engagement math (closing geometry, salvo Pₖ,
  debris-cone estimate; FW §11.A.2).
- `spacesim/engine/cyber.py` — cyber `VECTORS` × `PAYLOADS` database + `effective_success()`
  + `attribution_score()` (FW §11.A.3).
- `spacesim/engine/sigint.py` — SIGINT bands/modes + `geolocation_error_km()` scaling by
  √dwell × √N collectors × atmospheric loss (FW §11.A.6).
- `spacesim/engine/perturbations.py` — drag, J3/J4, third-body (Sun/Moon), SRP perturbations
  and `secular_drag_decay()` (FW §11.B.7-9); pure functions composed by future high-fidelity
  propagators.
- `spacesim/engine/sun.py` — `sun_unit_eci`, binary `is_sunlit()`, smooth `eclipse_fraction()`
  (umbra/penumbra interpolation; FW §11.B.10).
- `spacesim/content/vignette.py` + `vignettes/*.yaml` — vignette schema, loader, world-builder, objectives.
  `RoleRequirement`/`Vignette.roles_needed` (IP-1151, FR-4210) — optional, additive staffing
  requirements; absent for every vignette shipped before this package.
  `Vignette.coaching` is a list of `{at_sim_t?, cell, title, body}` notes (FW §11.D.17).
  `Vignette.roe` (IP-1172, FR-3420/NFR-2010) — optional per-cell
  `{blue: {kinetic_authorized, cyber_authorized}, red: {...}}`; absent for every vignette shipped
  before this package, in which case `build_world()` mirrors the legacy flat
  `red_kinetic_authorized`/`cyber_authorized` parameters to both cells.
- `spacesim/content/inject_library.yaml` — five reusable white-cell inject templates
  (debris breakup, GNSS-jam advisory, ambiguous RPO, GS outage, geomagnetic storm).
  Loaded via `InProcessSession.inject_library()`; surfaced in the white-cell GUI's
  **Build / schedule inject** panel with editable JSON + Now/+seconds/absolute-UTC scheduler
  (FW §11.D.19).
- `spacesim/session/` — `SessionManager` (clock/rewind/inject/TLE-add/save-resume/queue/alarms,
  `validate_order` dry-run, `next_contacts` fleet countdown, `begin_recovery`/`recovery_status`
  wiring `RecoverySystem` for the safe-mode recovery strip; **multiplayer:** server-authoritative
  lazy-clock fields `(_wall_anchor, _sim_anchor, _rate, _clock_running)` + `RLock`, `set_clock /
  catch_up / clock_state`, re-anchor on `start/rewind/undo/advance` so the wall clock can't snap
  the sim back),
  `CellController` (fog-of-war), `api.py` (`SessionAPI` + `CellView`/`Ack`), `inprocess.py`
  (**multiplayer:** `_locked(sid)` cm wraps every mutation; every read pass-through calls
  `catch_up(sid)` first; `list_sessions / set_clock / clock_state` added;
  **IP-1130:** `set_observer_view`/`get_observer_view`/`observer_designation` — a fourth,
  White-Cell-designated read-only seat dispatching unmodified to `get_godview`/`get_view`, no
  parallel filtering path; **IP-1151:** `assign_role`/`staffing_report` — seat-to-role bindings
  against a vignette's `roles_needed`, hard-gating `start()` on any unmet mandatory entry),
  `scene.py` (render-from-custody belief), `redai.py` (Red doctrine presets),
  `aar.py` (replay/scrub/branch-compare + `snapshot_at`),
  `assessment.py` (IP-2010 — read-only competency-rubric scoring: `score_custody_quality`/
  `score_window_discipline`/`score_belief_truth_divergence` + `assessment_report`, never a
  composite score; belief-truth divergence classifies aware/unaware from `custody_confidence_at_decision`,
  a new field `orders.py`'s `_exec_payload()` records at order-issue time via `custody.py`'s
  `confidence_at_decision()` helper, read back verbatim — never recomputed via replay),
  `research_export.py` (IP-3010 — `RunRecord` pydantic schema: `vignette_id`/`seed`/
  `condition_label` + IP-2010's `assessment_report` output verbatim, never reimplemented;
  `export_csv`/`export_json` extend `aar.export_csv()`'s flattening pattern to a multi-run table).
- `spacesim/tools/` (IP-3010 — first subpackage of its kind: offline/CLI-style utilities that
  drive the deterministic engine externally, not through the live `ui_web`/`session` request
  path) — `research_batch.py`'s `run_batch(vignette_id, seeds, condition_label,
  n_steps_or_until)` constructs one fresh seeded `SessionManager` per seed (no shared mutable
  state between runs), advances to `n_steps_or_until` sim-seconds (or the vignette's own
  estimated-duration horizon if omitted), and reads `session/assessment.py`'s `assessment_report`
  once per run. Distinct from the repo-root `tools/` directory (non-package build scripts like
  `tools/build_coastlines.py`) — this one must be importable by `spacesim/tests/`.
- `spacesim/ui_web/` — `server.py` (FastAPI over the SessionAPI; `/scene`, `/telemetry`;
  **IP-1130:** `_reject_observer(cell)` guards every mutating route — re-derived from the live
  route table at implementation time, not merely IP-1130's own enumerated list, per that package's
  own Risks note — plus `/observer/view` + `/observer/designation`) + `static/`
  front end: `app.js` (command menu with live dry-run preview + pre-disabled Issue + kinetic
  consequence-confirm, fleet rail with next-contact countdown/SoC/alarm badge/filter + alarm
  deep-link, `j/k/c/g` keyboard nav, presentation mode, supersede-guarded refresh, 2D belief map,
  subsystem drill-down whose cards carry per-subsystem telemetry + command-verb buttons; `api.post`
  attaches the caller's own seat as a `cell` query param to every mutating call), `globe.js` (3D
  orthographic globe), `world.js` (+committed `world.json` coastlines/borders), `graph.js`
  (telemetry line graphs), `style.css`, `index.html`.
- `tools/build_coastlines.py` — regenerates the committed `static/world.json` (low-res world map)
  from `basemap-data` (offline; coarse fallback if unavailable). `tools/render_manual.py` draws it.
- `spacesim/content/vignettes/00-training-basics.yaml` — guided tutorial vignette with a per-cell
  `tutorial` step script (≥5 steps each); drives the manual walkthrough + its screenshots.
- **All 19 vignettes carry a per-cell `intro_brief:` block** (situation, mission, friendly forces,
  threat picture, deadline note, ROE note, success criteria, tool tips). Surfaced in the
  **Mission brief panel** at the top of `<main>` via `GET /api/sessions/{sid}/brief/{cell}` (combined
  with live ROE + objective deadlines + countdown). Auto-opens on first session load;
  collapse state persisted per-session in `localStorage`. White sees both cells side-by-side.
- **The 8 canonical numbered vignettes also carry a per-cell `tutorial:` block** (how each cell
  completes its objectives, move by move). Surfaced via `GET /api/vignettes/{id}/tutorial` in the
  in-UI **Tutorial panel** (View ▾) and mirrored in `docs/training/11-vignette-playbooks.md`. The
  achievable objective-flips are verified by `spacesim/tests/test_vignette_tutorials.py`; ROE /
  weapons-quality / command-station gates that block the rest are documented in each block's `expect`.
- **Docs are modular under `docs/`** — routed by `docs/INDEX.md` (structure & rationale in
  `docs/DOCUMENTATION-PLAN.md`). Themes: `docs/build-spec/` (the binding spec, 8 modules),
  `docs/training/` (user manual, 16 modules — shared onboarding 01–11 plus the role-scoped
  **per-cell manuals** 12 White / 13 Blue / 14 Red, their 15 traceability matrix, and the 16
  vignette learning path), `docs/design/`, `docs/research/`, `docs/vignettes/`, each with its own
  `INDEX.md`.
- **Training corpus is a co-equal product with the code (owner decision 2026-07-04).** The manuals,
  vignette learning path, and in-app briefs/tutorials are requirement-bearing artifacts, not doc
  exhaust. Grounding: research tier **R600** (`docs/research/encyclopedia/R600-index.md`, authored
  8/8 2026-07-04). Governance: **FR-11000** family + **NFR §16** (`docs/requirements/`). Production/review:
  dedicated pipeline peers `02-research-training-pedagogy`, `08-training-manual-authoring`,
  `08-vignette-development`, `09-training-manual-review` (the 08 peers split the write surface —
  only `08-code-implementation` writes `spacesim/` Python). Rationale in MSTR-001 §2; ConOps note in
  GDS-00/GDS-01 "Training-corpus elevation (2026-07-04)"; residual risk in assumptions-register A12.
- **Per-cell training manuals + traceability (load-bearing for doc upkeep).** The three role-scoped
  manuals (`docs/training/12-white-cell-manual.md` `WCM-n`, `13-blue-cell-manual.md` `BLU-n`,
  `14-red-cell-manual.md` `RED-n`) are the facilitator/defender/adversary procedure layers over the
  shared concept modules; the current per-cell layout is a seed that satisfies FR-11110's
  role-scoped-*coverage* mandate, not a fixed structure (layout follows the requirements/architecture).
  `docs/training/15-manual-traceability.md` is a **bidirectional** feature ⇄ manual-section index
  (change a feature → §15.1 names the sections to update; edit a section → §15.2 + the inline
  `> Sources:` footer names the backing code) and now also tracks the vignette⇄learning-path linkage
  (§15.4). `docs/training/16-learning-path.md` sequences the 19 vignettes into a rung ladder, each
  rung naming its manual prerequisites + verified playbook. Upkeep is wired into the pipeline: skill
  `08-code-implementation`'s doc-update step, the dedicated training skills, and skill
  `10-integration-review`'s doc-coherence dimension all consult §15.1 for feature-changing work.
- `docs/training/` (first-time setup + guided walkthrough) and `docs/manual/` (UI screenshots incl.
  3D globe, command/system menus, and the step-by-step walkthrough; generated by
  `tools/render_manual.py`). The v1 operator-console spec is `docs/build-spec/07-operator-console.md`;
  the SSN spec is `docs/build-spec/08-ssn.md`.
- `docs/FUTURE-WORK.md` — single-source TODO list (v1.1+): remaining catalog-verb gaps,
  multiplayer transport, constellation aggregation, APP-6 symbology pack, Δv panel, and other
  deferred items.
  Run: `uvicorn spacesim.ui_web.server:app` then open http://127.0.0.1:8000/.
