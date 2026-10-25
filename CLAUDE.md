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

**Status: backend feature-complete through Phase 8; commands-layer audit completed Jun 2026; the suite is 1700 tests (full run, Oct 2026: 1697 passed, 3 skipped, 0 failed; the 3 are data-dependent vignette skips in `test_defensive_audit_2026.py` ×2 and `test_derived_probabilities.py`). Skip counts differ by marker mode: `-m "not browser"` collects 1669 and reports 4 skipped (the same 3 plus 1 whole-suite guard that skips on any partial collection: `test_test_origins.py` ×1); `-m browser` is 31 tests, 0 skipped where Playwright + Chromium are present (all 31 skip, with a named reason, where they are absent).** Deterministic engine
(P0–P4.5), the web layer (P5, FastAPI + browser front end), the render-from-custody belief
scene + 2D map (P5.5), the full **19-vignette library** (the canonical 8 numbered + the
training-basics onboarding + 5 Red COA + 3 mission-set + 1 learning + 1 novel) as YAML +
TLE force-add + Red doctrine presets (P6 + library expansion), the **capstone Vignette 8 +
AAR replay** (P7), and the **LAN multiplayer transport** (P8:
server-authoritative lazy clock + per-session RLock + session discovery + join-by-hash URL +
multi-monitor pop-out windows). Code under `spacesim/`; content is YAML; UI stack = **web**.
The browser GUI is not verified end to end; a headless-Chromium suite (`-m browser`, IP-1340)
covers its load-bearing console rules, and every backend path (endpoints, fog, objectives,
AAR, multiplayer clock + locking) is test-covered.

## Authoritative source & reading order

**`docs/architecture/` (the GDS-00…GDS-10 ladder) is the single authoritative architecture and
requirements source for this project, effective immediately — it supersedes `docs/build-spec/` in
its entirety.** This is a deliberate escalation, made by explicit project-owner instruction, beyond
the prior rule (under which a build-spec module stayed authoritative only until its specific GDS
level's own merge gate closed). The supersession is no longer gated module-by-module: build-spec is
superseded as a whole, immediately, including for GDS levels that have not yet been authored.

**Current GDS-ladder status.** Per [`docs/architecture/INDEX.md`](docs/architecture/INDEX.md) §1,
all eleven levels GDS-00 through GDS-10 are authored with closed merge gates and are authoritative
(GDS-06 NFRs, GDS-07 data model, GDS-08 UI architecture, GDS-09 API specification, GDS-10
requirements traceability matrix).
The `build-spec/` modules they replaced are **deprecated legacy reference, not a binding
tie-breaker**; the old rule ("on any conflict, the build spec wins") applies nowhere in this project.
Read build-spec text only for orientation on a topic the ladder does not cover, never cite it as
binding, and flag a gap rather than treating its wording as settled. Per-level caveats (gaps handed to
`04`, companion documents such as the ICD and `requirements/03` that stay as leaf-grain companions) are
in the index's status column.

1. [`docs/architecture/INDEX.md`](docs/architecture/INDEX.md) — the GDS ladder; the authoritative
   entry point for architecture and requirements, full stop.
2. [`docs/architecture/05-functional-requirements.md`](docs/architecture/05-functional-requirements.md)
   (GDS-05) for functional/operational requirements, elaborated in full traceability detail at
   [`docs/requirements/01-functional-requirements.md`](docs/requirements/01-functional-requirements.md).
3. For any topic the ladder does not cover, [`docs/build-spec/INDEX.md`](docs/build-spec/INDEX.md)
   as **legacy, non-binding reference**.
4. `docs/design/01-architecture-overview.md` — architecture reference behind GDS-03 (merged); the
   data model is GDS-07 (`docs/design/04-data-model.md` is superseded).
5. [`docs/research/INDEX.md`](docs/research/INDEX.md) (`01`–`06`) — *why* the rules are what they are.
6. `docs/build-spec/04-nfr-milestones-and-risks.md` §10 — the consolidated phase plan (M0–M7) with
   current status (legacy reference; the phase plan is not a GDS level). Deferred items live in
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
- **P5** UI over the API (FastAPI + web). ✓ (backend tested; the console's load-bearing rules are checked in headless Chromium by `-m browser`, IP-1340; the full browser GUI is not verified end to end)
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
is the canonical permanent gate. **Every test names its origin** (`BL-0310`, IP-1330): mark it
`@pytest.mark.verifies("FR-xxxx", …)` (or a module-level `pytestmark`) with the requirement leaf it
verifies — else its `FS-xxx`, or an `IP-xxxx` for a package's own completion test. The suite fails on an
untagged test and on an ID that is not a live baseline item. The tolerance list
`spacesim/tests/test_origin_allowlist.txt` is now **empty** (the FS-133 backfill is complete, so every
test must be tagged); the mechanism remains shrink-only (`BL-0358`). The RTM's Test column is **generated, never hand
edited** (`NFR-2850`): regenerate it with `python3 -m pytest --origin-report=rtm` in the same commit.
**Documentation checks run with the suite** (IP-1350, `NFR-3800`/`3820`/`3830`): a new broken relative link,
an `INDEX.md` that omits a document in its folder, or a status-ledger disagreement fails the suite. Known
defects sit on `spacesim/tests/doc_integrity_allow_*.txt`; those lists only shrink (fix the defect, delete its
line in the same commit — the suite also fails on a stale line). The `docs/research/` primer-link lines in
`doc_integrity_allow_links.txt` are the remaining known defects (owner: `02-research`, `BL-0292` sweep).

## Build/test commands

```bash
pip install pydantic numpy sgp4 pyyaml pytest hypothesis skyfield fastapi uvicorn httpx playwright
python3 -m spacesim.ui_web                                       # reads host/port/reload from spacesim.config.yaml (defaults 127.0.0.1:8000)
uvicorn spacesim.ui_web.server:app                               # equivalent if you prefer uvicorn's CLI
uvicorn spacesim.ui_web.server:app --host 0.0.0.0 --reload       # LAN multiplayer: bind to host IP, share URL
python3 -m pytest                                                # runs the whole suite (testpaths = spacesim/tests)
python3 -m pytest spacesim/tests/test_determinism.py             # the Phase-1 determinism gate
python3 -m pytest spacesim/tests/test_import_guard.py            # the Phase-0 engine guardrails
python3 -m pytest -m browser                                     # headless-Chromium console-rule tests (IP-1340, 33 tests); skip loudly where Playwright/Chromium is absent
python3 -m pytest -m "not browser"                                # everything except the browser tests (the default CI-style run)
python3 -m pytest spacesim/tests/test_doc_integrity.py spacesim/tests/test_test_origins.py   # documentation-integrity + test-origin gates (IP-1350 / IP-1330)
python3 -m pytest --origin-report [--origin-ids=FR-1120,…]       # read-only: tests by declared origin; requirements no test names
python3 -m pytest --origin-report=rtm                            # regenerate the RTM Test column (runs no tests)
```

**Release dependency lock (NFR-1510).** `pyproject.toml` declares minimum versions only; each release
ships `requirements.lock`, an exact pin of every direct and indirect dependency. To regenerate: (1) check
latest — fresh venv, `pip install -U -e ".[content,ui,dev]"`, record what moved; (2) try the update — run
the full suite (`-m "not browser"` and `-m browser`, plus the determinism gate); (3) fix or hold — a
minimal compatibility fix in non-engine code goes in test-first; anything needing an engine or
determinism change is not made, hold that one package at its newest compatible version and report why;
(4) validate and re-pin — raise the `pyproject.toml` floors to the validated versions,
`pip freeze --exclude-editable` into `requirements.lock` (keep its header comment), install it into
another fresh venv (`pip install -r requirements.lock && pip install --no-deps -e .`) and re-run both
suites; (5) commit the lock with the floors. Install a release from the lock, not from `pyproject.toml`.

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
endpoints (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`, `/assessment`,
`/ephemeris/truth`, the Observer view, and the White Cell facilitation/authoring reads — the full
named set is `FR-6220` in `docs/requirements/01-functional-requirements.md`) deliberately expose
ground truth without a cell binding. **Deploy only on a trusted LAN with cooperative participants.** A
hostile participant on the LAN can read another cell's belief state through `/scene/{cell}` or
`/telemetry/{cell}/...` by sending the other cell's name in the URL. This is by design for the
v1 PME training context (everyone in the room is on the same team learning together) and is
documented as the explicit trust boundary; see `docs/AUDIT-2026-06.md` §D5 / §F1. Hardening
options (per-cell tokens) are tracked in [`docs/FUTURE-WORK.md`](docs/FUTURE-WORK.md).
**White Cell controls (clock start/pause/resume/multiplier, step/advance/rewind/undo, start, param, inject fire/edit/cancel, force-add (TLE/bulk/ground), save load, `roles/assign`, `observer/designation` + `observer/view`) are refused to any request not naming the `white` seat (IP-1068/IP-1074, `FR-4310`/`FR-4320`) — again a client-asserted-seat rejection, not authentication. Time controls are also bounded to the exercise span (`FR-4330`, IP-1074/1075/1076): rewind only within `[start epoch, now]`, undo lands on the last surviving entry or the start epoch (empty undo refused 400), advance/step only forward to at most 366 days after the start epoch. The AAR playback routes obey the requesting seat (`FR-7340`, IP-1077): White may request any viewpoint, Blue/Red only their own cell's, Observer may read playback state but not start or change it; refusals are 403 before any state change. IP-1072 extends the same refusal to the Vignette Creator edits (`creator/state`, `creator/asset`, `creator/seats`), `save_vignette`, and `red_step`; session and draft creation (`POST /api/sessions`, `/draft`) is refused only when the request *names* `blue`/`red`/`observer` — a request naming no seat may still create (deliberate asymmetry).**
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
- `spacesim/engine/simulation.py` — `Simulation` driver + `replay()` + `SavedSession`;
  `replay_stepwise()` (IP-1261) — one forward replay pass yielding the world at several
  non-decreasing event-log positions (`replay()` itself unchanged). `advance_to` is
  failure-atomic (IP-1021, ADR-0038): a raising handler is rolled back in place to the replayed
  world/RNG, logged as a no-op `handler_error` record (`engine/handlers.py`), and the advance
  continues.
- `spacesim/engine/geometry.py` — frames (GMST ECI↔ECEF), WGS84 geodety, topocentric look angles.
- `spacesim/engine/sun.py` — analytic Sun direction + cylindrical eclipse/lighting test.
- `spacesim/engine/orbit.py` — `OrbitState`, Kepler+J2 element↔state, regime classification.
  `mean_to_true()` (IP-1190, FR-5220) — public mean-anomaly→true-anomaly conversion, extracted from
  `elements_to_rv()`'s existing inline computation with no behavior change; reused by the CCSDS OMM
  bulk-import path, which supplies a mean anomaly the TLE path never needed.
- `spacesim/engine/propagator.py` — `Propagator` seam: Kepler+J2 (fictional) / sgp4 (TLE).
- `spacesim/engine/entities.py` — `Asset`/`AssetResources`, `GroundSite`, `Sensor`
  (`Sensor.health`, IP-1062/FR-4430 — additive `"nominal"|"degraded"`, the `sensor_outage`
  inject effect's target field). IP-1220 (FR-1610-FR-1660) — six additive, default-absent
  sensor-modality fields: `beam_mode`, `exclusion_angle_deg`, `min_range_km`,
  `altitude_band_affinity`, `requires_cue`, `host_asset_id`.
- `spacesim/engine/access.py` — `AccessProvider` seam: all six channels + window caching; unknown
  endpoint ids (e.g. a command planned `via` a station not in the force) degrade to no-access, not a crash.
  IP-1220 (FR-1620/FR-1630/FR-1660) — `_observation_predicate`'s ground-optical branch gains a
  solar-exclusion-angle reject after its lighting check; the space-based branch gains a
  min-range-floor reject; `_sensor_orbit()` substitutes a `host_asset_id`-hosted sensor's position
  from its host Asset's current orbit; `_sensor_id_for_actor()` resolves either a sensor's own id
  or its host_asset_id to the same sensor for `SENSOR_OBSERVATION` queries.
- `spacesim/engine/custody.py` — `Track` (on-demand confidence decay) + weapons-quality gate.
- `spacesim/engine/effects.py` — `EffectInstance`/`EffectResolver` seam (5 D's), `is_link_denied`.
  `EffectInstance.order_action_type` (IP-1290, FR-1450) — additive, the issuing order's action
  type, set at each of the three construction sites (jam/engage/cyber) in `orders.py`.
  `ModerateEffectResolver(detectability_config=...)`/`_class_confidence()` (IP-1290) — a declared
  per-effect-class (order action type × five-D's reversibility category, `IP-1270`'s shared
  enumeration) attribution-confidence override, consulted at the same point the existing fixed
  `{"overt":.95,"ambiguous":.5,"covert":.15}` table is; falls back to it when the class is
  undeclared.
  `DebrisField.persistence_estimate` (IP-1240, FR-1430) — a coarse, altitude-derived, display-only
  estimate (`_persistence_estimate()`) attached at both construction sites (destructive-effect
  resolution here, and `spawn_debris` in `session/manager.py`); never consulted by Access Window
  or conjunction-screening logic.
- `spacesim/engine/orders.py` — `Order` + `OrderSystem` (validate → window → execute), cyber
  exception, ISL/stored delivery, sensor tasking (auto-select + contention), order queue + cancel.
  Actions: `jam/engage/observe/maneuver/downlink/cyber` + `command` (bus/payload verbs, see `buscommands.py`).
  `dry_run()` is a read-only mirror of `issue()` (validate + window/delivery-path, but schedules/
  registers/books nothing) → powers the UI's "why can't I?" pre-disabled buttons; replay-safe like `scene.py`.
  Resource bounds (IP-1320, FR-1460/FR-1470): an `engage` whose salvo (`_engage_rounds`, at least
  1) exceeds the rounds left is rejected `insufficient_ammo`, and `_h_effect` re-checks the rounds
  at execution (a failed record, nothing resolved or charged); a jam never changes the jammer's
  `power_w` (a rating, ADR-0037). A fired salvo is charged whether it hits or misses (IP-1321,
  FR-1480 — owner decision `BL-0249`; "fired" = reached resolution).
  `_h_maneuver` (IP-1250, FR-1320) — the execute-time payload gains `purpose_tag` (additive,
  default `""`) and, on success, mutates in the same dict `applied=True`/`remaining_delta_v_ms`
  (captured by the eventlog entry logged immediately after, same pattern as IP-1062's
  `condition_check`); a re-validation failure sets `applied=False` instead. `_h_maneuver`/
  `_h_command` (IP-1290, FR-1440) — an active uplink jam covering the command's delivery path at
  execute time fails delivery (`achieved="jammed"`), checked via the existing `is_link_denied`,
  mirroring `_h_downlink`'s own jam-check pattern.
  IP-1085 (FR-1440) — the jam check is path-aware: the maneuver/command execute payloads carry
  `delivery_path`/`relay` (`_delivery_keys`, from the planned window's channel) and `_delivery_jammed`
  denies `ground_uplink` on an `uplink` jam on the actor, `isl_relay` on a `crosslink` jam on the actor
  or relay, and never `stored_program`; a payload without the keys keeps the old uplink-on-actor rule.
  ROE (`engage`/`cyber`) is resolved per issuing cell against `_effective_roe(cell, order.issued_at)`
  (IP-1172/FR-3420, IP-1270/FR-3440) — the vignette-declared static `_static_roe` overlaid with any
  `roe_change` eventlog entries at or before the order's own issue time, a pure point-in-time
  derivation (never `self.roe`, a "current value" convenience cache `_h_roe_change` also
  maintains, mutated for any direct caller that wants the live value rather than a specific
  instant's). `issue_roe_change(cell, target_cell, flag, value)` — White-Cell-only, logs a
  `roe_change` entry. `gating_rules`/`_matching_gate` (IP-1270, FR-3430) — a vignette-declared
  `{action_type?, reversibility_category?, required_role}` rule holds a matching order in a new
  `pending_approval` state (`self._pending`) instead of scheduling it; `decide_gated_order(cell,
  order_id, approve)` resumes/rejects it, role-gated against the rule's own `required_role`,
  logging `effect_gate_request`/`effect_gate_decision` (with elapsed time) — discarded (not
  replayed) on rewind/undo (`session/manager.py::_rebind`). The engine never branches on
  legacy-vs-explicit vignette shape, only on the always-cell-keyed dict `content/vignette.py`'s
  `build_world()` produces. `scene_from_world()`'s sensor filter (IP-1062,
  FR-4430) excludes a `health="degraded"` sensor (`sensor_outage` inject effect), mirroring the
  existing degraded-ground-station filter immediately above it. IP-1220 (FR-1640/FR-1660) —
  `_validate()`'s observe branch rejects a `requires_cue` sensor tasked against a target with no
  existing `Track` (`world.track_for`); `_resolve_sensor_id()`/`_candidate_sensors()` accept either
  a sensor's own id or its `host_asset_id` as the order's `actor`.
- `spacesim/engine/recovery.py` — `RecoverySystem`: multi-pass safe-mode recovery + re-safe-on-persistence.
- `spacesim/engine/ssn.py` — mock Space Surveillance Network (per `docs/build-spec/08-ssn.md` §17): per-cell
  `SSNNetwork`s instantiated from a dispersion preset (`sparse`/`regional`/`global`/`proliferated`),
  hybrid-turnaround request resolution (earliest viable window inside the priority SLA + processing
  delay; coalition vs. national affiliation), and two deterministic handlers (`ssn_collect` /
  `ssn_deliver`) that stage on `world.ssn_staged` and deliver into the requester's `TrackCatalog`.
  Replay-safe; cancel-before-collect tag-skips both events. `passive_rf_fix()` (IP-1220, FR-1650) —
  a passive-RF multilateration fix reusing `SSNNetwork`'s member-list shape, gated on the target's
  existing `bus_state.comms.status` (not a new field) and ≥3 (2D)/≥4 (3D) member receivers with
  simultaneous `SENSOR_OBSERVATION` access.
- `spacesim/engine/telemetry.py` — read-time seeded subsystem telemetry (graphs/logs) + attack
  signatures (jam→RX power, cyber→FSW errors, DE→SNR, power sag, kinetic→loss-of-signal). Pure,
  never mutates state/RNG (like `scene.py`). `sample/series(..., nominal=True)` drop the attack term
  → the clean baseline ghost the "compare to nominal" overlay draws (`&nominal=1` on the series endpoint).
  **IP-1260 (FR-2320):** `sample()` is also the sole value source for the per-asset telemetry CSV
  export (`SessionManager.telemetry_export`) — no parallel computation.
- `spacesim/engine/buscommands.py` — real catalog bus/payload/defense verbs (EPS shed/restore/charge-
  mode, `adcs.set_mode`, `cdh.dump_storage`, `satcom.mitigate_interference`/`shift_users`,
  `isr.collect_now`/`schedule_collection`, `def.patch_cyber` for the recovery-loop root-cause fix);
  `apply_command` mutates `BusState`/`PayloadState`/`cyber_vulnerabilities` inside the deterministic
  `execute_command` handler (replay-safe, observable in SOH/telemetry), `can_issue` is the plan-time
  validator gate (payload verbs gated by payload type + bus availability). Carried by the order
  system's `command` action (uplink/stored delivery like `maneuver`). New verbs extend `apply_command`.
- `spacesim/engine/bus.py` — `BusState`/`PayloadState` SOH (limits, gating, safe mode, pass-gated view).
  `ThermalState` carries `temp_c`/`heater_watts`/`radiator_capacity_w` (FW §11.B.11).
  `PayloadState` carries 8 typed, `Optional` per-payload-type sub-models (`SatcomParams`/`IsrEoParams`/
  `IsrSarParams`/`SigintParams`/`SdaParams`/`WeatherParams`/`MwParams`/`PntParams`, R109/R110/R129/R134-
  grounded), auto-populated for exactly the one field matching `PayloadState.type` — authored defaults
  distinct from `isr.py`'s `BEAM_MODES` runtime table (IP-1171, FR-5170/FR-5180).
- `spacesim/engine/busmodel.py` — `BusSystem`: bus-evolution / telemetry-contact / downlink handlers.
  IP-1230: `bus_tick` also applies opt-in index-driven LEO drag (`_apply_index_drag`) to `kepler`
  LEO assets with an authored `Asset.ballistic_coeff_m2_kg`, only while
  `world.space_weather["index_series"]` is declared (no series → no-op, byte-identical).
- `spacesim/engine/maneuver.py` — pure compute for six manoeuvre entry modes
  (eci / lvlh / finite_burn / target_coe / hohmann / plane_change).
- `spacesim/engine/isr.py` — ISR beam-mode database (EO/SAR/SDA/weather/mw — the last two added
  by IP-1170, closing `BL-0053`; `ground_radar` fence/dish variants added by IP-1220, FR-1610,
  reached by an observe order since IP-1222 when the order param or the radar's `Sensor.beam_mode`
  names one), `effective_gain()` (IP-1220, FR-1630 — optional `target_regime`/`band_affinity`
  degrade gain on an altitude-band mismatch, `LEO_SSO` counted as `LEO` via `altitude_band()`,
  IP-1222; IP-1221, FR-1670 — optional `phase_angle_deg`/`usable_phase_range` scale gain by
  `phase_angle_factor()`, a linear fall-off outside a passive-EO sensor's declared
  `Sensor.usable_phase_angle_deg`, evaluated by `OrderSystem._observation_phase_angle_deg` at the
  observation's `win.start`), `soc_drain()`, footprint polygon + ground-heading helpers.
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
  propagators. **IP-1230 (FR-1230/FR-4440, ADR-0039):** `f_solar`/`f_geo` piecewise-linear
  space-weather index factors, step-held `index_in_effect`, `drag_multiplier` (`f_solar × f_geo`),
  `anomaly_rate_multiplier` (`f_geo` only) and the shared `index_series_problems` validator.
- `spacesim/engine/sun.py` — `sun_unit_eci`, binary `is_sunlit()`, smooth `eclipse_fraction()`
  (umbra/penumbra interpolation; FW §11.B.10); `cats_phase_angle_deg()` (IP-1300, FR-8220) — the Sun-target-
  chaser illumination ("CATS") phase angle, the engine's single shared phase-angle function
  (`BL-0152`: now also called by IP-1221's `FR-1670` observe-gain refinement, not re-derived).
- `spacesim/engine/tle_export.py` (IP-1211, FR-7440) — current-epoch TLE generation from any ECI
  state: a single-epoch SGP4 mean-element fit (`state_to_tle()`; non-singular equinoctial
  elements computed directly from r/v, safeguarded Newton + fixed-point correction, bounded and
  deterministic), formatted by `sgp4.exporter.export_tle`, round-trip-checked against
  `ROUND_TRIP_BOUND_M` (1 km) or rejected with `ValueError`. `tle_identity()` carries a TLE-sourced
  orbit's catalog number/designator/B* forward; anything else gets the `99999` placeholder.
  `sgp4` is lazy-imported (optional dependency), like `propagator._tle_rv`.
- `spacesim/config.py` — `ServerConfig`/`load_server_config()`. `ContentConfig`/
  `load_content_config()` (IP-1180, FR-5410/FR-5420) — optional `content:` section
  (`external_vignette_dirs`, `user_save_dir`), same optional-file/`SPACESIM_CONFIG`-override
  pattern as `ServerConfig`; absent by default (empty catalog extension, no save target).
- `spacesim/content/vignette.py` + `vignettes/*.yaml` — vignette schema, loader, world-builder, objectives.
  **IP-1310 (FR-5310–FR-5314):** `load_vignette` is a load-time gate — `validate_vignette` (pure) collects
  every problem (entity validators, TLE parse/propagate, orbit/location with `cyber_unit` exempt, unique
  ids, `roles_needed` refs, `build_world` catch-all) and raises `VignetteValidationError(ValueError)`;
  `POST /api/sessions` maps it to 400 `invalid_vignette` (404 unknown id), and a refused load leaves the
  session registry untouched.
  `RoleRequirement`/`Vignette.roles_needed` (IP-1151, FR-4210) — optional, additive staffing
  requirements; absent for every vignette shipped before this package.
  `Vignette.coaching` is a list of `{at_sim_t?, cell, title, body}` notes (FW §11.D.17).
  `Vignette.space_weather_series` / `environmental_anomalies` (IP-1230, FR-1230/FR-4440,
  ADR-0039) — optional; a declared F10.7/Kp series (stored as `world.space_weather["index_series"]`)
  and an opt-in environmental-anomaly base rate; non-physical values refused at load.
  `Vignette.effect_gating_rules` (IP-1270, FR-3430) — additive, optional list of
  `{action_type?, reversibility_category?, required_role}`; `build_world()` passes it through
  unmodified into `VignetteContext.gating_rules`, absent (`[]`) for every vignette shipped before
  this package. `Vignette.effect_detectability_config` (IP-1290, FR-1450) — the same shared
  enumeration, each entry `{action_type?, reversibility_category?, confidence}`, passed through
  unmodified into `VignetteContext.detectability_config`.
  `Vignette.roe` (IP-1172, FR-3420/NFR-2010) — optional per-cell
  `{blue: {kinetic_authorized, cyber_authorized}, red: {...}}`; absent for every vignette shipped
  before this package, in which case `build_world()` mirrors the legacy flat
  `red_kinetic_authorized`/`cyber_authorized` parameters to both cells.
  `Vignette.initial_tracks`/`simulator_version`/`initial_space_weather` (IP-1200, FR-5510) —
  save-as-scenario's carried-forward mid-exercise state; absent/empty for every vignette shipped
  before this package, in which case `build_world()`'s consumption of them is a no-op.
  **IP-1086 (FR-5310/FR-5311):** `asset_authoring_problems(asset, start_epoch)` — the one shared, pure asset
  validator (TLE propagates at the start epoch; Keplerian `0<=e<1`, perigee above the equatorial radius,
  `0<=i<=180`; non-negative resources; id charset), called by `validate_vignette`, force-add TLE, OMM/bulk
  import and the Creator's `creator_set_state`/`creator_edit_asset`; orbit/location presence stays a save/load rule.
  `list_vignettes()`/`load_vignette()` (IP-1180, FR-5410) — enumerate/search zero or more
  configured external directories alongside `VIGNETTE_DIR`, each entry tagged `origin`
  (`"built-in"` or the external directory's basename); a same-id collision resolves built-in-first,
  external order thereafter, loser skipped + logged. `_validate_id`/`_resolve_within_root`
  (NFR-3700) — the traversal guard, extracted/generalized to any content root, shared with the
  save path below.
- `spacesim/content/vignette_export.py` (IP-1173, FR-5110; **IP-1086:** `save_vignette` runs `validate_vignette` on the exported model first — an invalid draft is a 400 and nothing is written) — reverse serialization:
  `export_vignette()`/`save_vignette()` convert a draft session's live `WorldState`+
  `VignetteContext` into a `Vignette` model and write it to a configured `user_save_dir`
  (IP-1180, FR-5420 — retargeted from `VIGNETTE_DIR`; raises if unconfigured) — the mirror image of
  `vignette.py`'s `load_vignette()`/`build_world()`, and the only code path that writes an
  authored vignette file. **IP-1200 (FR-5510):** both functions gain an optional
  `start_epoch: Optional[int] = None` (used in place of `ctx.start_epoch` when given — the
  save-as-scenario call passes the save moment; omitted, reproduces the prior behavior exactly),
  and `export_vignette()` now carries forward `world.tracks`/`world.space_weather`/
  `spacesim.version.simulator_version()` into the new `Vignette.initial_tracks`/
  `initial_space_weather`/`simulator_version` fields, consumed by `build_world()` when present.
- `spacesim/version.py` (IP-1200, FR-5510) — `simulator_version()`: the short git commit hash
  when a working tree is available, else the package's own `spacesim.__version__` — never raises.
- `spacesim/content/bulk_import.py` (IP-1190, FR-5220) — `parse_multi_tle()`/`parse_ccsds_omm()`
  (CCSDS OMM in KVN form only, XML out of scope): each parses a multi-object file into a common
  per-object dict shape; a file with zero recognizable blocks of its claimed shape is rejected
  outright, distinct from a recognizable-but-malformed block (returned for a later per-object
  force-add failure, never dropped at parse time).
- `spacesim/content/inject_library.yaml` — five reusable white-cell inject templates
  (debris breakup, GNSS-jam advisory, ambiguous RPO, GS outage, geomagnetic storm).
  Loaded via `InProcessSession.inject_library()`; surfaced in the white-cell GUI's
  **Build / schedule inject** panel with editable JSON + Now/+seconds/absolute-UTC scheduler
  (FW §11.D.19).
- `spacesim/session/` — `SessionManager` (clock/rewind/inject/TLE-add/save-resume/queue/alarms,
  **IP-1101 (FR-7210/FR-7220/FR-7230):** a save is self-contained — `save_state` adds `save_format`, `simulator_version`, a `content` portion (the vignette as loaded plus force-added assets) and the replay `baseline`; `from_state` builds from them (legacy saves reload by id), `validate_save` refuses a bad save before replay, **IP-1102 (FR-7220/FR-7230):** `validate_save` also checks required keys/types for both formats and a legacy save's vignette file (each unusable save is a 400 naming the problem, never a 500) and `save_state`'s `content` reflects pre-start edits/deletes of built assets (untouched ones verbatim from the as-authored vignette), **IP-1103 (FR-7230):** `validate_save` completes the set — non-object overrides, malformed pending/orders/SSN rows, an out-of-range `final_time` (more than 366 days past the start) and a non-string classification are each a 400, and `InProcessSession.load_save_with_warnings` returns the resume warnings (`load_save` route: `{session, warnings}`),
  **IP-1063 (BL-0129/BL-0188):** pure `validate_inject_effects` — `fire_inject` rejects a
  malformed or FR-4430-precondition-failing inject atomically (`ValueError` → `Ack(ok=False)` →
  `/inject` 400; e.g. an `anomaly` on an asset with no `bus_state`), and `_apply_inject_effects`
  skips an invalid effect with a White "inject effect skipped" message instead of raising mid-handler,
  **IP-1270 (FR-3430/FR-3440):** `decide_gated_order`/`issue_roe_change` — thin wrappers over
  `OrderSystem`'s own methods; no additional state at this layer,
  **IP-1260 (FR-2320):** `telemetry_export(cell, asset_id, t1, t2, interval_s)` — per-asset telemetry
  over a sim-time span as flat rows (one per sampled instant x parameter), each value
  `telemetry.sample()` on the world replayed to that instant; fog-scoped like `get_telemetry`;
  `ephemeris._clamp_or_reject` span rule; served as CSV at `GET /telemetry/{cell}/{asset}/export.csv`,
  **IP-1250 (FR-1320):** `maneuver_ledger(cell, asset_id)` — a derived, read-only per-asset
  manoeuvre ledger (time/delta-v cost/purpose tag/resulting remaining budget), filtered from
  `EventLog`'s `execute_maneuver` entries (`applied=True` only), fog-scoped like `get_telemetry`,
  **IP-1190 (FR-5220):** `bulk_import()` — multi-object TLE/CCSDS OMM (KVN) import, generalizing
  `add_tle()`'s single-object mechanism (extracted into `_force_add_tle_object`) via a new
  `_force_add_omm_object` sibling, per-object success/failure reporting, batch continues past a
  malformed object,
  **IP-1062 (FR-4420/FR-4430):** `_apply_inject_effects()` — the shared per-effect dispatch
  extracted from `_h_inject`'s previous inline body, now also called by a new
  `_h_condition_check()` handler that evaluates every not-yet-fired condition-triggered inject
  (`trigger.type == "condition"`, reusing `content/vignette.py`'s `_evaluate_metric()`) against
  replayed `WorldState` at a `condition_check` tick cadence `_arm_schedule` queues only when a
  vignette declares one; firing-state is derived from a time-filtered eventlog scan (no new
  `WorldState` field), mirroring `_arm_schedule`'s own pattern. Four new effect types:
  `anomaly` (bus→safe_mode / telemetry→comms degraded), `sensor_outage` (`Sensor.health`),
  `forced_custody_loss` (`Track` mutation, cell-scoped), `scripted_manoeuvre` (the six existing
  `engine/maneuver.py` entry modes via `compute_maneuver()`/`apply_impulse()`, deliberately
  bypassing `AssetResources.delta_v_ms` per `ADR-0005`),
  **IP-1200 (FR-5510):** `save_as_scenario()` — requires `self.started`, else calls
  `vignette_export.save_vignette(..., start_epoch=self.sim.clock.now)`,
  `validate_order` dry-run, `next_contacts` fleet countdown, `begin_recovery`/`recovery_status`
  wiring `RecoverySystem` for the safe-mode recovery strip; **IP-1230:** an opt-in `env_anomaly_check` tick
  (`_h_env_anomaly_check`, `FR-4440`) and a `space_weather` inject that updates keys and accepts an
  `index_series`; **IP-1066 (FR-4450):** a White-only pending-inject queue (`pending_injects`/
  `cancel_inject`/`edit_inject`) logged as `inject_admin` events whose overrides fold from the event
  log strictly before the fire instant (`_inject_overrides`); a stale event is logged `skipped`, edits
  re-arm after a rewind, White future injects carry `white-<n>` handles and are themselves logged as
  `inject_admin` `schedule` entries so rewind/undo re-arms them (`IP-1083`, `BL-0284`); **IP-1084 (H-1, FR-6210):** `_notice_by_owner()` — the one addressing helper for a controller-set `anomaly`/`sensor_outage` notice (White gets the true cause, the owning cell the fact only, the opposing cell nothing; a neutral target is White only), also reached by the condition and env-anomaly paths; `fire_inject`/`edit_inject` reject a boolean `at_sim_t`; **IP-1067 (FR-4620):**
  `controller_view()` composes the god-view and both cells' `get_view` for one instant (served
  White-only at `/controller_view`, one `_locked_read`); **multiplayer:** server-authoritative
  lazy-clock fields `(_wall_anchor, _sim_anchor, _rate, _clock_running)` + `RLock`, `set_clock /
  catch_up / clock_state`, re-anchor on `start/rewind/undo/advance` so the wall clock can't snap
  the sim back; **IP-1074 (FR-4310):** `rewind_to` raises `ValueError` outside `[ctx.start_epoch, now]`
  (→ `Ack(ok=False)` → HTTP 400) and `clock_state` carries `start_epoch`; `roles/assign` + `observer/view`
  are `_require_white` on the query seat, 403); **IP-1075 (FR-4310, NFR-1600):** `undo_last` raises `ValueError` on an empty log or `n < 1` (→ `Ack(ok=False)` → HTTP 400), an undo that drops every entry lands on `start_epoch` (never 1970; `Simulation.undo_last` falls back to the initial state's time), and the tick/inject schedule is re-armed after undo like `rewind_to`; **IP-1076 (FR-4330, NFR-1600):** `advance_to`/`step` raise `ValueError` (→ `Ack(ok=False)` → HTTP 400) for a target before now, after `start_epoch` + `MAX_SAVE_SPAN_US` (366 days), or a non-finite/negative step, and the running (lazy) clock is clamped to that ceiling and stops there,
  **IP-1086 (NFR-1600):** the scene (`scene.py::build_scene`), `windows_ahead` (`error: propagation_failed`) and
  `next_contacts` skip an un-propagatable asset instead of 500ing; read-only,
  `CellController` (fog-of-war), `api.py` (`SessionAPI` + `CellView`/`Ack`), `inprocess.py`
  (**multiplayer:** `_locked(sid)` cm wraps every mutation; every read pass-through calls
  `catch_up(sid)` first; `list_sessions / set_clock / clock_state` added;
  **IP-1130:** `set_observer_view`/`get_observer_view`/`observer_designation` — a fourth,
  White-Cell-designated read-only seat dispatching unmodified to `get_godview`/`get_view`, no
  parallel filtering path; **IP-1151:** `assign_role`/`staffing_report` — seat-to-role bindings
  against a vignette's `roles_needed`, hard-gating `start()` on any unmet mandatory entry;
  **IP-1173:** `create_draft_session`/`save_vignette` — a Vignette Creator draft session (an
  unstarted `SessionManager`, tracked in `_draft_sessions`), reusing the existing registry/
  locking/`MAX_LIVE_SESSIONS` eviction unmodified; `step`/`advance_to`/`rewind_to`/`undo_last`/
  `red_doctrine_step` all reject a draft sid rather than advancing its clock),
  `scene.py` (render-from-custody belief), `redai.py` (Red doctrine presets),
  `aar.py` (replay/scrub/branch-compare + `snapshot_at`; `state_at_time(mgr, t)` (IP-1210,
  FR-7410/FR-7420) — additive sibling of `state_at(mgr, seq)`, reconstructing at an arbitrary sim
  time instead of an eventlog sequence number; `worlds_at_times(mgr, times)` (IP-1261, BL-0170) —
  its time-span counterpart, one forward pass over `replay_stepwise()` (live-tail shortcut: no
  replay when every instant is at/after the last entry), shared by `manager.py::get_series` (the
  console's telemetry graphs, now per-instant history rather than back-dated live state),
  `telemetry_export`, and both `ephemeris.py` exports;
  `PlaybackSession` (IP-1280, FR-7330) — continuous, speed-adjustable timeline playback built
  entirely on repeated `state_at_time()` calls, from ground truth or a `CellController`-filtered
  single-cell viewpoint (`_participant_cells()` rejects a non-participating cell at construction/
  `set_viewpoint()`; switching viewpoint never resets the played-back moment); one instance per
  session, held in `InProcessSession._playbacks`, never in `SessionManager` itself),
  `ephemeris.py` (IP-1210, FR-7410/FR-7420 — truth/cell-observed ephemeris export: `sample_times()`/
  `truth_ephemeris()`/`cell_observed_ephemeris()`/`to_ric()` (reuses `engine/maneuver.py::
  lvlh_frame` directly for the RIC transform)/`write_csv()`/`write_oem()`; a wholly-out-of-range
  time span is rejected, a partially-out-of-range span is silently clamped; **IP-1262:**
  `sample_times()` is the single sampling choke point for all three time-span exports (both
  ephemeris + `telemetry_export`) — a non-finite/non-positive explicit `interval_s`, or sampling
  over `MAX_EXPORT_SAMPLES` (10,000) instants, raises `ValueError` (→ 400) before any replay; cell-observed reads
  only the requesting cell's own `Track.state_estimate`, never ground truth; **IP-1300
  (FR-8210/FR-8220):** `live_ric_view()` — the live, operator-selected-origin RIC view at the
  current sim time via the unmodified `to_ric()`, own assets at truth + own Tracks at belief only
  (or ground truth for White via `SessionManager.get_ric_view()`'s explicit `get_godview()` branch —
  `build_scene()` has no `"white"` case), plus an unbanded CATS readout when chase+target are both
  given; out-of-custody selections raise `ValueError`; **IP-1211 (FR-7440):** `quick_tle()` — a
  current-epoch TLE for one satellite via `engine/tle_export.py`, a cell exporting its own
  satellites from their actual orbit (`source: "own"`, IP-1212, `FR-7440` as amended — ownership
  beats a held Track) and anything else only from its own `Track.state_estimate`, White from ground
  truth via `SessionManager.get_tle()`'s `get_godview()` branch; rejections raise `ValueError`),
  `assessment.py` (IP-2010 — read-only competency-rubric scoring: `score_custody_quality`/
  `score_window_discipline`/`score_belief_truth_divergence` + `assessment_report`, never a
  composite score; belief-truth divergence classifies aware/unaware from `custody_confidence_at_decision`,
  a new field `orders.py`'s `_exec_payload()` records at order-issue time via `custody.py`'s
  `confidence_at_decision()` helper, read back verbatim — never recomputed via replay),
  `research_export.py` (IP-3010 — `RunRecord` pydantic schema: `vignette_id`/`seed`/
  `condition_label` + IP-2010's `assessment_report` output verbatim, never reimplemented;
  `export_csv`/`export_json` extend `aar.export_csv()`'s flattening pattern to a multi-run table).
- **Control-boundary bullets (IP-1076 / IP-1077 / IP-1081 / IP-1103 / IP-1082).**
  `IP-1076` (FR-4330): `SessionManager._span_ceiling()` (start + `MAX_SAVE_SPAN_US`, 366 days) bounds
  `step`/`advance_to` and the lazy clock; a refused step/advance is a `ValueError` mapped to
  `Ack(ok=False)` and HTTP 400, and the running clock pins at the ceiling instead of pausing.
  `IP-1077` (FR-7340): `playback_seat_decision()` and `PlaybackSeatRefused` in `session/inprocess.py`
  gate the five `aar/playback/*` routes by the requesting seat (White any viewpoint, a player its own
  cell, Observer state-read only; 403 before any change).
  `IP-1081` (NFR-3710): the 100,000-entry load cap lives at `SessionManager.MAX_EVENTLOG_REPLAY_ENTRIES`
  (alias on `InProcessSession`), the first rung of `validate_save`, counting a real save's
  `{"entries": [...]}` log as well as a bare list.
  `IP-1103` (FR-7230): `MAX_SAVE_SPAN_US` and `_check_final_time_span` refuse a save whose `final_time`
  is more than 366 days past its start.
- **`IP-1082` (NFR-1600, FR-4330, FR-7330) on `server.py` / `manager.py` / `aar.py`:** `ui_web/server.py`
  `_refuse_nonfinite`/`_first_nonfinite` are the one place the non-finite policy lives; every
  mutating route in the live route table carries a shared guard (`_finite_json_guard` on White controls:
  404, then 403, then the check; `_inject_finite_guard` on pending-inject edit/cancel; `_finite_json_guard_open`
  on the rest; `_playback_finite_guard` on `aar/playback/*`, where a seat `playback_seat_decision` refuses
  still gets its 403); a `NaN`/`Infinity` anywhere in the JSON body, or a boolean in a numeric field
  (`rate`, `t`, `n`, `dt_sim_s`, `speed`, `dt_s`), is a 400 naming the field. A route-table test derived
  from the live table pins them. `PlaybackSession.MAX_SPEED` (10,000) bounds `|speed|` and an
  overflowing advance is a 400. `SessionManager.MAX_CLOCK_RATE` (10,000) bounds
  `set_clock` to `(0, MAX_CLOCK_RATE]` when running (any rate must be finite), and
  `_require_finite` backs `step`/`advance_to`/`rewind_to`/`undo_last` for non-HTTP callers; a refused
  `set_clock` is `Ack(ok=False)` from `InProcessSession` and a 400 at the route. `PlaybackSession`
  clamps and stores its cursor to `[start_epoch, live now]` on every read and rejects a non-finite
  `speed`/`dt_s`. Console: the toolbar `+1m/+10m/+1h` buttons call `stepBy`, which reports a refusal in
  `#control-status`.
- `spacesim/tools/` (IP-3010 — first subpackage of its kind: offline/CLI-style utilities that
  drive the deterministic engine externally, not through the live `ui_web`/`session` request
  path) — `research_batch.py`'s `run_batch(vignette_id, seeds, condition_label,
  n_steps_or_until)` constructs one fresh seeded `SessionManager` per seed (no shared mutable
  state between runs), advances to `n_steps_or_until` sim-seconds (or the vignette's own
  estimated-duration horizon if omitted), and reads `session/assessment.py`'s `assessment_report`
  once per run. Distinct from the repo-root `tools/` directory (non-package build scripts like
  `tools/build_coastlines.py`) — this one must be importable by `spacesim/tests/`.
- `spacesim/tests/` support files (not tests themselves): `conftest.py` (IP-1330 — records each collected
  test's `verifies` origin once at collection; registers `--origin-report[=list|rtm]`/`--origin-ids`),
  `baseline_ids.py` (IP-1330/IP-1335 — the baseline-ledger reader, origin checks and RTM Test-column
  generator, plain functions reusable by `test_doc_integrity.py`), `test_browser_console_rules.py`
  (IP-1340 — `@pytest.mark.browser`, starts the real server on loopback and drives Chromium via
  Playwright; fog of war, plan-first disabled Issue, irreversible-effect confirm; skips with a named
  reason where Playwright/Chromium is absent), `test_doc_integrity.py` (IP-1350 — broken links,
  `INDEX.md` omissions, status-ledger agreement), and the shrink-only `test_origin_allowlist.txt` (empty)
  and `doc_integrity_allow_{links,indexes,ledgers}.txt`.
- `spacesim/ui_web/` — `server.py` (FastAPI over the SessionAPI; `/scene`, `/telemetry`;
  **IP-1300 (FR-8210/FR-8220):** `GET /ric_view/{cell}?origin=&chase=&target=` — live RIC-frame
  view (+ CATS angle), 404 on an out-of-custody selection, rendered by `static/ricview.js`
  (View ▾ → RIC frame view; selection is non-persistent per BL-0156);
  **IP-1211 (FR-7440):** `GET /tle/{cell}?object_id=` — quick current-epoch TLE export (404 on
  any rejection), rendered by `static/tleexport.js` (View ▾ → TLE export: copyable textarea + Copy
  button with a plain-HTTP `execCommand` fallback);
  **IP-1250 (FR-1320):** `/maneuver_ledger/{cell}/{asset}` (+ `/export.csv`) — the per-asset
  manoeuvre ledger view/CSV export, fog-scoped identically to `/telemetry/{cell}/{asset}`;
  **IP-1280 (FR-7330):** `/aar/playback/{start,advance,state,viewpoint,speed}` — the variable-
  speed AAR playback routes over `session/aar.py::PlaybackSession`;
  **IP-1270 (FR-3430/FR-3440):** `/gate/decide` + `/roe/change` — role-gated (checked inside
  `SessionManager`/`OrderSystem`) pending-order decision and live ROE-flag-change routes;
  **IP-1072:** `_require_white` now also guards `save_vignette`/`creator/*`/`red_step`, and `_refuse_player_seat_on_create(cell)` refuses a creation request naming a player seat (absent seat allowed); **IP-1077 (FR-7340):** the five `aar/playback/*` routes take the query seat (`playback_seat_decision` in `session/inprocess.py`; White any viewpoint, a player only its own cell, Observer state-read only, no/unknown seat refused, all 403 before any state change);
  **IP-1130:** `_reject_observer(cell)` guards every mutating route — re-derived from the live
  route table at implementation time, not merely IP-1130's own enumerated list, per that package's
  own Risks note — plus `/observer/view` + `/observer/designation`) + `static/`
  front end: `app.js` (command menu with live dry-run preview + pre-disabled Issue + kinetic
  consequence-confirm, fleet rail with next-contact countdown/SoC/alarm badge/filter + alarm
  deep-link, `j/k/c/g` keyboard nav, presentation mode, supersede-guarded refresh, 2D belief map,
  subsystem drill-down whose cards carry per-subsystem telemetry + command-verb buttons; `api.post`
  attaches the caller's own seat as a `cell` query param to every mutating call; IP-1066
  `renderPendingInjects` lists pending injects with Cancel / Edit…; IP-1067 `refreshComparePanel`
  renders the ⚖ Compare panel (truth / Blue / Red) from one `/controller_view` read; `api.put/patch/del`
  extend the same cell-query-param convention for IP-1174's routes below; IP-1073 — palette time entries offered to the White seat only, a `#control-status` aria-live line for refused time controls / save loads, and a latest-edit token discarding superseded dry-run responses), `globe.js` (3D
  orthographic globe), `world.js` (+committed `world.json` coastlines/borders), `graph.js`
  (telemetry line graphs), `creator.js` (IP-1174 — the Vignette Creator's White-Cell UI: synchronized
  JSON view, ground-truth 2D/3D preview, TLE/lat-long asset entry with a curated-site picker,
  asset menu, seat-count declaration + seat/role matrix; a thin client over a *draft* session,
  `POST /api/sessions/draft` + the `creator/*`/`force/ground`/`ground_sites` routes), `style.css`,
  `index.html`.
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
