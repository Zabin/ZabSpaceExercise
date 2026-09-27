# IP-1200 — Save-as-Scenario (Mid-Exercise State → New Starting Vignette)

> **Package ID:** IP-1200
> **Version:** 1.0
> **Status:** ⚪ NOT STARTED *(forward design — not authorized for coding, MSTR-006 §3)*
> **Dependencies:** [FS-120](../../features/FS-120-save-as-scenario.md) v1.0 (`FR-5510`),
> [IP-1180](IP-1180-external-vignette-directories.md) (`FR-5420`'s user-save-directory write
> target — `⚪ NOT STARTED`, not yet authorized; this package's own write path calls the same,
> retargeted `save_vignette`, so it is sequenced after `IP-1180` at implementation time even though
> neither blocks the other's *planning*), [IP-1173](IP-1173-vignette-creator-draft-session.md)
> (`VERIFIED` — `export_vignette`/`save_vignette`, the existing reverse-serialization mechanism this
> package extends in place, not reimplements)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0071` (external validation report,
> 26 Sep 2026, item B5), `BL-0097` (FS-120's one Open Question, resolved below)
> **Produces:** a mid-exercise-state-to-new-vignette save capability satisfying `FR-5510` in full
> **Feature Reference:** [FS-120 — Save-as-Scenario](../../features/FS-120-save-as-scenario.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/content/vignette_export.py`](../../../spacesim/content/vignette_export.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Confirmed directly against the live code at authoring time:
`content/vignette_export.py::export_vignette()` (lines 25-54) already dumps each `Asset` via
`asset.model_dump(exclude={"owner"})` — which already carries `resources: AssetResources`,
`health`, `bus_state`, `payload_state` verbatim, since those are already-existing `Asset` fields.
**FR-5510's "remaining resources" and "asset health" requirements are therefore already satisfied
by the existing function with zero change** — the genuine gaps are (1) the resulting vignette's
`start_epoch_utc` is hard-coded to `ctx.start_epoch` (the *original* vignette's start, never the
save moment), (2) `world.tracks` is never read at all, (3) `world.space_weather` is never read at
all, (4) no simulator-version field exists anywhere in the schema or the codebase. `SessionManager`
has no "ended" lifecycle state — only `self.started: bool` (session/manager.py line 98) — so
`FR-5510`'s Precondition ("a running or paused session exists") reduces to a single, already-
representable check.*

## Package ID

IP-1200

## Title

Save-as-Scenario (Mid-Exercise State → New Starting Vignette)

## Objective

Let White Cell save a running (or paused) session's current state — tracks, remaining resources,
asset health, space-weather — as a new vignette whose declared start epoch is the save moment, with
the producing simulator's version recorded in the file, by extending the existing
`export_vignette()`/`save_vignette()` mechanism in place rather than duplicating it.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-120 — Save-as-Scenario](../../features/FS-120-save-as-scenario.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-5510 | Save a running session's current state as a new starting vignette | `export_vignette()`/`save_vignette()` gain an optional `start_epoch: Optional[int] = None` parameter (defaulting to `ctx.start_epoch`, preserving `IP-1173`'s existing draft-save behavior byte-for-byte when omitted); a save-as-scenario caller passes `start_epoch=world.now` explicitly. Two new `Vignette` fields (`initial_tracks`, `simulator_version`) plus reuse of the existing `space_weather` dict shape as `initial_space_weather` carry forward tracks/version/space-weather; resources/health are already carried by the existing per-`Asset` dump. A new `SessionManager`/`InProcessSession` entry point requires `self.started` before allowing the save (Design Decision 1 below). |

## Architecture Components

- **C5 Content & Data** (`content/vignette_export.py`, `content/vignette.py`) — owns the extended
  `export_vignette()`/`save_vignette()` signatures and the two new additive `Vignette` fields; owns
  `build_world()`'s consumption of `initial_tracks`/`initial_space_weather` on load.
- **C2 Session / Application Layer** (`session/manager.py`, `session/inprocess.py`) — owns the new
  "save as scenario" entry point's precondition check (`self.started`) and the `start_epoch=
  self.sim.clock.now` call-site distinguishing it from the existing draft-save call-site.
- **C4 Operator Console** (`ui_web/`) — `SaveVignetteRequest` gains an additive
  `as_scenario: bool = False` field; the existing `POST /api/sessions/{sid}/save_vignette` route is
  reused, not duplicated with a new route, since the only difference is a boolean flag threading
  through to the same underlying function.

## Interfaces

`INT-0011` (vignette/template load — the resulting file is loaded through this existing interface
unchanged, per FS-120's own Interfaces Used) and `INT-0012` (save round trip — this Feature's output
is content-side, per `ADR-0022`'s existing ownership split, same as `IP-1173`'s draft-save). No new
interface; no ICD edit.

## Design Decisions (resolving `BL-0097`'s Open Questions)

1. **Behavior of a save-as-scenario request against a session in an invalid state.** `SessionManager`
   has **no "ended" lifecycle state at all** — confirmed by reading the class directly: the only
   lifecycle flag is `self.started: bool` (`session/manager.py` line 98), set once by `start()` and
   never reset. "Mid-recovery" is asset-level `BusState.safe_mode` state, not a session-lifecycle
   gate — a session mid-recovery is still `started=True` and perfectly saveable (its degraded asset
   health is exactly what FR-5510 wants captured). **Design Decision: reject a save-as-scenario
   request when `not self.started`** (the only state a request could actually be against that isn't
   "running or paused") **with a specific error**, mirroring `IP-1180`'s own "reject with a specific
   reason" posture for its own precondition failures; accept it in every other case. A draft
   (unstarted Creator) session already has its own dedicated save path (`IP-1173`'s existing
   `save_vignette`, unaffected by this Design Decision) — this package's new entry point is simply
   not reachable for a draft session in the first place (see Files to Modify).
2. **Embedded space-weather schema representation.** Confirmed directly: the existing
   `space_weather` inject effect already stores `world.space_weather` as a **plain, already-generic
   dict** (`{"severity": sev}`, `session/manager.py::_h_inject`) — the exact same shape a new
   `Vignette.initial_space_weather: Optional[dict] = None` field can hold verbatim, with no new
   schema needed. **Design Decision: reuse this shape directly** — `export_vignette()` reads
   `dict(world.space_weather)` into the new field; `build_world()` writes it back to
   `world.space_weather` on load if present (else the engine's own existing default, empty/no
   severity, is unchanged — additive, per `NFR-2010`).

## Files to Modify

- `spacesim/content/vignette.py` — `Vignette` gains two new additive fields:
  `initial_tracks: list[dict] = Field(default_factory=list)` (each entry a
  `Track.model_dump()`-shaped dict) and `simulator_version: Optional[str] = None`; reuses the
  existing `objectives`/`roe`-style bare-dict convention for `initial_space_weather: Optional[dict]
  = None` — all three absent/empty for every one of the 19 existing library vignettes, per
  `NFR-2010`. `build_world()` extended: after constructing `world`, if `vignette.initial_tracks`,
  populate `world.tracks = [Track.model_validate(t) for t in vignette.initial_tracks]` (import
  `Track` from `engine.custody`, already imported by `session/manager.py` and available to this
  module without a new circular-import risk — verify at implementation time); if
  `vignette.initial_space_weather`, set `world.space_weather = dict(vignette.initial_space_weather)`.
- `spacesim/content/vignette_export.py` — `export_vignette()` gains `start_epoch: Optional[int] =
  None` (used in place of `ctx.start_epoch` when given), populates `initial_tracks` from
  `[t.model_dump() for t in world.tracks]`, `initial_space_weather` from
  `dict(world.space_weather)` if truthy else omitted, and `simulator_version` from a new helper
  (below) — unconditionally, since a version stamp costs nothing for the existing draft-save caller
  either. `save_vignette()` gains the same `start_epoch` passthrough parameter.
- `spacesim/version.py` *(new, small)* — `simulator_version() -> str`: attempts `git rev-parse
  --short HEAD` (run with `cwd` at the repository root, `subprocess.run(..., capture_output=True,
  timeout=<small>)`), returning the short commit hash on success; falls back to a hardcoded
  `spacesim.__version__`-style package-version string (added to `spacesim/__init__.py`, mirroring
  `pyproject.toml`'s existing `version = "0.1.0"`) if git is unavailable, not a repository, or the
  call fails/times out for any reason — never raises, per FR-5510's own framing ("source-control
  commit **or** package version").
- `spacesim/session/manager.py` — `SessionManager` gains a thin wrapper, e.g.
  `save_as_scenario(self, vignette_id, title, classification=...)`, that raises a specific
  `ValueError` when `not self.started` (Design Decision 1), else calls the extended
  `content.vignette_export.save_vignette(self.world, self.ctx, vignette_id, title, classification,
  start_epoch=self.sim.clock.now)` — a one-line, additive method beside the existing
  `save_vignette`-adjacent code, not a modification of any existing method's behavior.
- `spacesim/session/inprocess.py` — `InProcessSession.save_vignette()` gains an additive
  `as_scenario: bool = False` parameter; when `True`, calls the new
  `SessionManager.save_as_scenario(...)` instead of the existing draft-save call, under the same
  `self._locked_read(session)` context manager already used today (unchanged locking discipline).
- `spacesim/ui_web/server.py` — `SaveVignetteRequest` gains `as_scenario: bool = False` (additive,
  defaults preserve every existing caller's behavior); the existing `POST
  /api/sessions/{sid}/save_vignette` route passes `req.as_scenario` through to
  `api.save_vignette(...)` — no new route.

## Implementation Tasks

1. Write a failing test asserting `export_vignette()`/`save_vignette()` with no `start_epoch`
   argument reproduce today's exact output (regression: `IP-1173`'s existing draft-save tests must
   still pass unchanged), before adding the new parameter.
2. Write a failing test for `simulator_version()`: asserts a short-hash-shaped string when run
   inside this git repository; write it to tolerate (not assert on) the fallback branch, since CI
   environments vary — assert only that it never raises and always returns a non-empty string.
3. Add `Vignette.initial_tracks`/`simulator_version`/`initial_space_weather`; write a failing test
   asserting all 19 existing library vignettes still load unchanged (`NFR-2010` regression) before
   changing `build_world()`.
4. Extend `build_world()` to consume `initial_tracks`/`initial_space_weather`; write a failing test
   asserting a vignette with a hand-authored `initial_tracks` entry produces a `WorldState` whose
   `track_for(owner, object)` returns the expected `Track`.
5. Extend `export_vignette()`/`save_vignette()` per Files to Modify; write a failing test asserting
   a session with a populated `Track`/degraded `BusState`/non-empty `world.space_weather`, when
   exported with an explicit `start_epoch`, produces a `Vignette` whose `start_epoch_utc` matches
   that argument (not `ctx.start_epoch`) and whose `initial_tracks`/`initial_space_weather` match the
   source state.
6. Add `SessionManager.save_as_scenario()`; write a failing test asserting it raises when
   `not self.started` and succeeds otherwise, before implementing the check.
7. Wire `InProcessSession.save_vignette(..., as_scenario=...)` and the HTTP route's
   `as_scenario` field; write a failing test round-tripping the full flow (start a session, advance
   it, save-as-scenario, load the result) through the HTTP routes, asserting the resulting session's
   start time equals the save moment and its initial tracks/health/resources match the source
   session's state at that moment.
8. Re-run the full existing suite; confirm `IP-1173`'s existing draft-save tests
   (`test_vignette_creator_session.py`, `test_web.py`) still pass with the new optional parameters
   defaulted away.

## Tests to Add

- `spacesim/tests/test_content.py` — `Vignette.initial_tracks`/`simulator_version`/
  `initial_space_weather` default-absent regression (all 19 library vignettes); `build_world()`
  consumption of `initial_tracks`/`initial_space_weather` when present.
- `spacesim/tests/test_vignette_export.py` *(new, or extending an existing export-focused test
  file if `IP-1180`'s own pass already created one)* — `export_vignette()`'s `start_epoch`
  parameter; tracks/space-weather/version round trip; the existing-behavior-preserved regression
  for the omitted-`start_epoch` case.
- `spacesim/tests/test_session.py` or `test_vignette_creator_session.py` —
  `SessionManager.save_as_scenario()`'s `not self.started` rejection and success path.
- `spacesim/tests/test_web.py` — end-to-end save-as-scenario flow via the HTTP route (Task 7).
- A small, dedicated `spacesim/tests/test_version.py` — `simulator_version()` never raises, always
  returns a non-empty string.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — `spacesim/version.py`'s one `subprocess` call lives outside `engine/`, so it
introduces no wall-clock read or global RNG use inside the import-guarded boundary; `build_world()`'s
extension is pure/deterministic (reads only the passed-in `Vignette`'s data).

## Documentation Updates

- `CLAUDE.md` Code Map — `content/vignette_export.py`'s entry gains the `start_epoch`/tracks/
  version/space-weather note; a new `spacesim/version.py` entry added; `content/vignette.py`'s
  entry gains the three new additive fields.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-5510`'s `Implementation Package`
  cell updated from `UNASSIGNED` to `IP-1200`; `Test` cell updated once the named test files exist.
- `docs/features/FS-120-save-as-scenario.md` — `Referenced By` metadata gains this package's link
  (metadata cross-link only). Its one Open Question (`BL-0097`) is not struck out by this package
  directly (that belongs to `06-feature-specification`), but this package's Design Decisions section
  gives `06` everything needed to close it.
- `docs/pipeline/backlog.md` — `BL-0097` updated: fully resolved by this package's two Design
  Decisions; recommend flipping to `DONE` at the next `00-pipeline-manager` harvest.

## Definition of Done

- [ ] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3) — not yet sought or granted as of this writing.
- [ ] `export_vignette()`/`save_vignette()` with no `start_epoch` argument reproduce today's exact
  output — `IP-1173`'s draft-save behavior is unchanged.
- [ ] Given a running session at sim time T with specific track/resource/health/space-weather
  state, saving as a new scenario and loading the result produces a session whose start epoch is T
  and whose initial tracks/resources/health/space-weather match the source session's state at T.
- [ ] The resulting file records a non-empty `simulator_version`.
- [ ] A save-as-scenario request against an unstarted session is rejected with a specific error.
- [ ] All 19 existing library vignettes still load unchanged (schema additivity regression).
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `test_vignette_export.py`'s (or equivalent) new tests exist and are green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Full existing suite re-run with zero regressions, in particular every `IP-1173`-authored
  draft-save test.
- [ ] Independently confirm, by reading the shipped code, that `export_vignette()`'s
  `start_epoch=None` default path is byte-identical to its pre-`IP-1200` behavior.
- [ ] Independently round-trip a save-as-scenario file through `load_vignette()`/`build_world()`
  and confirm the resulting `WorldState` carries the expected tracks/health/resources/space-weather.
- [ ] Independently confirm `SessionManager.save_as_scenario()` is unreachable for a draft
  (unstarted) session and that `IP-1173`'s own draft-save path is untouched by this package.

## Dependencies

- **Upstream:** [FS-120](../../features/FS-120-save-as-scenario.md) v1.0 (approved,
  `✅ Ready for implementation planning`), [IP-1173](IP-1173-vignette-creator-draft-session.md)
  (`VERIFIED` — the existing `export_vignette()`/`save_vignette()` this package extends in place).
- **Build-sequencing (not a planning-time block, but load-bearing at implementation time):**
  [IP-1180](IP-1180-external-vignette-directories.md) retargets `save_vignette()`'s write directory
  from `VIGNETTE_DIR` to a configured `user_save_dir` — whichever of `IP-1180`/`IP-1200` is
  implemented second must re-read the other's actual changes to `save_vignette()`'s signature
  before extending it, to avoid one package's diff silently reverting the other's. Both packages
  touch the same function; neither depends on the other's *design* being finished first, but their
  *implementation* order matters and must be sequential, not parallel, once authorized.
- **Downstream:** none identified.

## Risks

- **Same-function coordination risk with `IP-1180` (see Dependencies).** This is the same class of
  risk `IP-1180`'s own package already names for its coordination with `IP-1173` — two forward-design
  packages touching the same function's signature. Whoever implements second must diff against the
  first's actual landed change, not against this document's description alone.
- **`initial_tracks` round-trip fidelity.** `Track.model_dump()`/`Track.model_validate()` must
  round-trip every field (including `state_estimate: Optional[OrbitState]`) losslessly — if a
  future `Track` field addition isn't a plain-serializable type, this round trip could silently
  drop data. Not a defect today (every current `Track` field is plain-serializable), but a
  regression risk to watch if `Track`'s schema grows.
- **`simulator_version()`'s git-based path assumes a git working tree is present at runtime.** In a
  packaged/non-git deployment this falls back to the hardcoded package-version string (Design
  choice, Files to Modify) — acceptable per `FR-5510`'s own "commit **or** package version" framing,
  but the fallback value will not distinguish between two different builds sharing the same package
  version number. Named, not resolved, here.

## Rollback Considerations

All three new `Vignette` fields and the `start_epoch`/`simulator_version` additions to
`export_vignette()`/`save_vignette()` are additive and default-inert — reverting them removes this
package's capability with no effect on any existing vignette file (built-in, external, or
Creator-drafted) and no effect on `IP-1173`'s existing draft-save behavior, since every new
parameter defaults to reproducing that exact prior behavior when omitted. No data-migration
concern: a save-as-scenario file already written remains an ordinary, loadable vignette file after
rollback (its `initial_tracks`/`simulator_version`/`initial_space_weather` fields would simply be
ignored by a rolled-back `build_world()`, not rejected, since pydantic tolerates unknown-to-older-
code additive fields the same way every other additive schema change in this project already does).
