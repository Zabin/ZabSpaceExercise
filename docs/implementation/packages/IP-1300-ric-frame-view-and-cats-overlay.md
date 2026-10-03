# IP-1300 — Live RIC-Frame Relative-Motion View & CATS Overlay

> **Package ID:** IP-1300
> **Version:** 1.0
> **Status:** 🟡 READY *(fully specified; every cited dependency — `FS-121`/`IP-1210`,
> `FS-105`, `FS-106` — is `VERIFIED`. **Not authorized for coding** — MSTR-006 §3 authorization is
> a separate, explicit project-owner decision not given as part of this planning pass.)*
> **Dependencies:** [FS-130](../../features/FS-130-ric-frame-view-and-cats-overlay.md) v1.0
> (`FR-8210`/`FR-8220`), `session/ephemeris.py::to_ric()`/`engine/maneuver.py::lvlh_frame()`
> ([IP-1210](IP-1210-ephemeris-export.md), `VERIFIED`), `engine/sun.py::sun_unit_eci()`
> (`IP-1030`-era baseline, `VERIFIED`), `session/cells.py`/`session/scene.py::build_scene()`
> (`FS-105`, `VERIFIED` — the sibling fog-of-war-filtered rendering pattern this package follows),
> `session/manager.py`'s existing god-view path (`FS-106`, `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0107`, `BL-0111`, `BL-0154`
> (CATS-banding, left open — see Design Decisions), `BL-0155` (route/parameter shape — resolved
> below), `BL-0156` (origin-selection persistence — resolved below)
> **Produces:** a live, operator-selectable RIC-frame relative-motion view (`FR-8210`) and a live
> CATS illumination-phase-angle overlay for the view's selected chase satellite (`FR-8220`),
> satisfying both in full except for the one named open Design Decision (CATS-banding, non-blocking
> for either requirement's own stated Acceptance Criteria)
> **Feature Reference:** [FS-130 — Live RIC-Frame Relative-Motion View & CATS Overlay](../../features/FS-130-ric-frame-view-and-cats-overlay.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/engine/maneuver.py`](../../../spacesim/engine/maneuver.py),
> [`spacesim/engine/sun.py`](../../../spacesim/engine/sun.py),
> [`spacesim/session/scene.py`](../../../spacesim/session/scene.py),
> [`spacesim/session/cells.py`](../../../spacesim/session/cells.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package — genuinely not yet built. This package resolves two of `FS-130`'s three
Open Questions (`BL-0155`/`BL-0156`) at the implementation-planning level, per that spec's own
explicit routing; `BL-0154` (CATS-angle display-banding) is carried forward unresolved as a named
Design Decision, consistent with this skill's own rule against inventing a design the inputs don't
actually settle.*

## Package ID

IP-1300

## Title

Live RIC-Frame Relative-Motion View & CATS Overlay

## Objective

Add a live, fog-of-war-correct, operator-selectable RIC-frame relative-motion view, and a CATS
illumination-phase-angle readout layered on it for a selected chase/observer satellite — both
read-only, pure-derivation renderings over existing engine state, following the exact architectural
pattern `session/scene.py::build_scene()` already establishes for the belief-map/3D-globe surfaces.

> **This package is NOT authorized for coding.** No MSTR-006 §3 go-ahead is on record for `IP-1300`
> — this planning pass documents a build-ready design, nothing more. `08-code-implementation` may
> not begin against this package until the project owner gives explicit authorization.

## Feature Reference

[FS-130 — Live RIC-Frame Relative-Motion View & CATS Overlay](../../features/FS-130-ric-frame-view-and-cats-overlay.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-8210 | Live, operator-selectable RIC-frame relative-motion view | A new, pure, read-only function in `session/ephemeris.py` (reusing `to_ric()`'s existing transform against the *live* current-sim-time state rather than a stored time-span sample) computes every cell-visible object's position relative to an operator-selected origin; exposed through a new `SessionManager`/`InProcessSession`/`SessionAPI` read method and a new cell-scoped HTTP route, mirroring `get_scene()`'s exact call chain. |
| FR-8220 | CATS illumination-phase-angle overlay for the RIC view's selected chase satellite | A new, pure function (new module-level helper, `engine/sun.py` or a thin wrapper beside it — Design Decision 2) computing the Sun-target-observer phase angle from `sun_unit_eci()` and the live state the `FR-8210` computation already has in hand; surfaced as an additional field on the same read's response when a chase/observer selection is also supplied. |

## Architecture Components

- **C2 Session/Application Layer** (`session/ephemeris.py`) — gains the new live relative-state
  query function, built on the existing `to_ric()` (unmodified).
- **C1 Simulation Engine** (`engine/maneuver.py`, `engine/sun.py`) — read, not modified; `lvlh_frame()`
  and `sun_unit_eci()` are consumed exactly as they already exist.
- **C2 Session/Application Layer** (`session/cells.py`, `session/manager.py`) — the fog-of-war
  boundary (`CellController`) and the new `SessionManager.get_ric_view()` read method, following
  `get_scene()`'s exact placement and call shape.
- **C4 Operator Console** (`ui_web/server.py`, `ui_web/static/`) — the new HTTP route and a new
  client-side rendering surface alongside the existing 2D map/3D globe.

## Interfaces

`INT-0001` (Browser ↔ Operator Console), `INT-0006` (Console → SessionAPI seam), `INT-0007`
(CellController → Engine Custody) — all three pre-existing, consistent with `FS-130`'s own
Interfaces Used field; no new ICD interface is introduced.

## Design Decisions

1. **Resolving `BL-0155` (route/parameter shape).** New route:
   `GET /api/sessions/{sid}/ric_view/{cell}?origin=<asset_or_track_id>&chase=<id>&target=<id>`
   — `origin` is required (`FR-8210`); `chase`/`target` are both optional and only produce the
   `FR-8220` CATS field when both are present, mirroring the exact query-parameter style
   `/telemetry/{cell}/{asset}/{param}` already uses for its own optional `t0`/`t1`/`n`/`nominal`
   parameters. This is a new *route*, not a new *interface* — it rides `INT-0001`/`INT-0006`/
   `INT-0007` exactly like every sibling cell-scoped route. `GET` (not `POST`) is used because the
   origin/chase/target selection is read-only state, matching every other cell-scoped read route
   in `ui_web/server.py` (none of which is a `POST`).
2. **CATS-angle computation placement.** Add a small, pure helper — `cats_phase_angle_deg(r_target,
   r_chaser, micros)` — beside `sun_unit_eci()` in `engine/sun.py` (same module that already owns
   every other Sun-geometry primitive this engine has), rather than inside `session/ephemeris.py`
   (which owns the RIC transform, a different geometric concern). `session/ephemeris.py`'s new live
   query function calls this helper when both `chase`/`target` are supplied, keeping the two
   computations composable but independently testable — directly addressing `BL-0152`'s own
   finding that `FR-8220` and `FEAT-1600`'s future `FR-1670` should share one phase-angle function:
   placing it in `engine/sun.py` (a module both the session layer and a future `engine/access.py`
   predicate can import without a layering violation) is what makes that sharing possible without
   `engine/access.py` importing from `session/`.
3. **Resolving `BL-0156` (origin-selection persistence).** The operator's current origin/chase/
   target selection is **not** written to any session-shared state (`WorldState`, `EventLog`, or a
   `SessionManager` field) — it is pure per-request UI state, supplied fresh on every poll via the
   query parameters in Design Decision 1. A per-viewer *convenience* remembering the last selection
   across a page reload, if the client-side implementation wants one, belongs in the browser's own
   `localStorage`, per `CLAUDE.md`'s explicit browser-storage guidance — this package does not
   require that convenience to satisfy `FR-8210`'s/`FR-8220`'s own Acceptance Criteria, and leaves
   it to `08-code-implementation`'s own judgment whether to add it, since neither requirement
   depends on it.
4. **`BL-0154` (CATS-angle display-banding) — left open, not decided here.** `FS-130`'s own Risk
   analysis already narrows this: `R109` v1.3 §3.11's ground≈90°/space≈150° figures ground an
   *access-gating* default for `FR-1670` (a different Feature), not a committed display-threshold
   for `FR-8220`'s purely informational readout. This package implements `FR-8220` as an unbanded
   numeric value (0°-180°, no color/flag) — the simplest design that is fully grounded and fully
   satisfies `FR-8220`'s own stated Acceptance Criteria — and defers any visual banding to a future,
   separately-authorized enhancement once `BL-0154` is resolved (by a second corroborating source,
   or an explicit project-owner decision). This is a scope-narrowing choice, not a guess at the
   unresolved question's answer.

## Files to Create

None — every change is additive to existing files (see Files to Modify).

## Files to Modify

- `spacesim/engine/sun.py` — add `cats_phase_angle_deg(r_target_eci, r_chaser_eci, micros) -> float`,
  a pure function using the existing `sun_unit_eci()` and basic vector math (no new imports beyond
  what the module already has); returns the angle in degrees between the target→Sun and
  target→chaser unit vectors, per `FR-8220`'s own definition (0° = fully illuminated as seen from
  the chaser, 180° = backlit).
- `spacesim/session/ephemeris.py` — add a new pure function (name TBD at implementation time, e.g.
  `live_ric_view(mgr_world, cell, origin, chase=None, target=None)`) that: resolves the origin
  object's live state (ground truth for the no-cell/White path, the cell's own `Track`/owned-asset
  state for a cell-scoped request — mirroring `to_ric()`'s existing fog-of-war-agnostic signature,
  with the *caller* responsible for the fog-of-war-correct state it passes in, exactly as
  `build_scene()`'s caller pattern already works); calls the existing `to_ric()` for every other
  cell-visible object relative to that origin; calls the new `cats_phase_angle_deg()` when
  `chase`/`target` are both supplied. Does not touch `to_ric()`/`lvlh_frame()` themselves.
- `spacesim/session/manager.py` — add `SessionManager.get_ric_view(cell, origin, chase=None,
  target=None)`, structured identically to the existing `get_scene(cell)` (reads fog-of-war-filtered
  state for a cell-scoped request; the White-Cell/no-cell variant must be implemented by reading
  the existing `get_godview()`'s own ground-truth-assembly path rather than assumed to "just work"
  through `cell="white"` — **this is Implementation Task 1, verify-before-reuse**, since
  `build_scene()`'s own asset loop filters strictly on `a.owner != cell` with no special case for
  `"white"`, unlike `_owns()`'s explicit `cell == "white"` bypass used elsewhere).
- `spacesim/session/inprocess.py` — add `InProcessSession.get_ric_view(session, cell, origin,
  chase=None, target=None)`, structured identically to the existing `get_scene(session, cell)`
  (`with self._locked_read(session) as mgr: return mgr.get_ric_view(...)`).
- `spacesim/ui_web/server.py` — add `GET /api/sessions/{sid}/ric_view/{cell}` per Design Decision 1,
  structured identically to the existing `get_scene` route (same `_require(sid)` call, same
  `api.get_ric_view(sid, cell, ...)` dispatch).
- `spacesim/ui_web/static/app.js` (and/or a new sibling file, e.g. `ricview.js`, mirroring
  `globe.js`'s own separation from `app.js`) — a new rendering surface: an origin-satellite
  selector, a live-updating RIC-coordinate plot, and (when a chase/target pair is selected) the
  CATS-angle readout. The exact UI layout/interaction design is implementation detail this package
  does not specify beyond the data it renders — consistent with this skill's own rule against
  describing implementation this far downstream of behavior.

## Implementation Tasks

1. **Before any other task, read `session/manager.py::get_scene()`/`get_godview()`'s actual
   current implementations directly from the shipped code** to confirm exactly how (or whether) the
   White-Cell/no-cell ground-truth variant should be wired — per the Files-to-Modify note above,
   `build_scene()`'s own `cell=="white"` handling is not a given; do not assume it without checking.
2. Write a failing test asserting `cats_phase_angle_deg()` returns 0° for a geometry where the
   chaser is exactly between the target and the Sun's direction as seen from the target (full
   illumination), and 180° for the opposite geometry, before adding the function.
3. Add `cats_phase_angle_deg()` to `engine/sun.py`.
4. Write a failing test asserting the new `session/ephemeris.py` live-RIC function's output matches
   `to_ric()`'s own existing output for a known origin/target pair at a fixed sim time, before
   adding the new function.
5. Add the new live-RIC function to `session/ephemeris.py`, reusing `to_ric()` directly.
6. Write a failing test asserting a cell-scoped request for an origin/chase/target the requesting
   cell cannot see is rejected, mirroring the existing fog-of-war rejection pattern any other
   cell-scoped read already uses, before wiring the `SessionManager`/`InProcessSession` methods.
7. Add `SessionManager.get_ric_view()`, `InProcessSession.get_ric_view()`, and the new HTTP route;
   confirm the White-Cell/no-cell variant against Task 1's findings.
8. Write a failing test asserting the White-Cell/no-cell variant renders every object (not only one
   cell's belief), matching `FR-4610`'s own exact-match standard, before finalizing that path.
9. Re-run the full existing suite; confirm zero regressions to any existing scene/ephemeris/sun
   test.

## Tests to Add

- `spacesim/tests/test_sun.py` (or a new `test_cats_angle.py`) — `cats_phase_angle_deg()` at 0°,
  90°, and 180° reference geometries, independently derived, not copied from the implementation.
- `spacesim/tests/test_ephemeris.py` — the new live-RIC function's output matches `to_ric()`'s
  existing output for a known case; fog-of-war rejection for an out-of-custody origin/chase/target.
- `spacesim/tests/test_web.py` — the new route end-to-end: a cell-scoped request returns only that
  cell's visible objects; the White-Cell/no-cell request returns every object.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — every new function is a pure, read-time derivation reading existing state;
no wall-clock read or global RNG use is introduced, and no new engine-layer import crosses the
UI/network boundary `test_import_guard.py` enforces.

## Documentation Updates

- `CLAUDE.md` Code Map — `engine/sun.py`, `session/ephemeris.py` entries each gain a one-line note
  for the new functions; `ui_web/server.py`/`static/` entries gain a note for the new route/surface.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-8210`/`FR-8220` rows' `Test`/
  `Impl. Package` cells updated from `UNASSIGNED` to this package's ID and the named test files.
- `docs/features/FS-130-ric-frame-view-and-cats-overlay.md` — `Referenced By` metadata gains this
  package's link.
- `docs/pipeline/backlog.md` — `BL-0155`/`BL-0156` confirmed `DONE` (resolved by this package's
  Design Decisions 1/3); `BL-0154` confirmed still open/`SCHEDULED`, unchanged (this package
  narrows its scope per Design Decision 4 but does not resolve it).

## Definition of Done

- [ ] `cats_phase_angle_deg()` returns correct values at the 0°/90°/180° reference geometries.
- [ ] The live-RIC function's output matches `to_ric()`'s own existing output for a known case.
- [ ] A cell-scoped request renders only that cell's visible objects; an out-of-custody
  origin/chase/target selection is rejected; the White-Cell/no-cell variant renders every object.
- [ ] The CATS overlay appears only when both `chase`/`target` are supplied; it does not alter
  `FR-8210`'s own view when absent.
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Every new test named above exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Independently confirm, by reading the shipped code, that the White-Cell/no-cell variant
  actually renders ground truth (not a cell-filtered subset) — this package's own Implementation
  Task 1 flags this as a verify-before-reuse risk, not a given.
- [ ] Independently confirm `cats_phase_angle_deg()` is not duplicated anywhere else in
  `engine/` — per Design Decision 2's shared-function intent for `BL-0152`.

## Dependencies

- **Upstream:** [FS-130](../../features/FS-130-ric-frame-view-and-cats-overlay.md) v1.0 (approved
  for this planning pass — see this package's own header note on `FS-130`'s Status line wording);
  `session/ephemeris.py::to_ric()`/`engine/maneuver.py::lvlh_frame()` (`IP-1210`, `VERIFIED`);
  `engine/sun.py::sun_unit_eci()` (baseline, `VERIFIED`); `session/scene.py::build_scene()`/
  `session/cells.py` (`FS-105`, `VERIFIED`); `session/manager.py`'s god-view path (`FS-106`,
  `VERIFIED`).
- **Downstream:** none currently. `FEAT-1600`/`FR-1670`'s forthcoming Feature Specification (not
  yet authored) should, per Design Decision 2, import `engine/sun.py::cats_phase_angle_deg()`
  rather than re-implement it — a forward note for whoever specifies that Feature next, not a
  build-order dependency *this* package has on it.
- **Build-sequencing:** none required; this package has no dependency on any other currently
  `READY`/`BLOCKED` package in this plan.

## Risks

- **Ambiguity risk (White-Cell/no-cell variant wiring).** Flagged explicitly as Implementation
  Task 1 — `build_scene()`'s existing `cell=="white"` handling is not confirmed to exist, and this
  package's design must not assume it does without checking the actual shipped code first.
- **Consistency risk (shared phase-angle function, `BL-0152`).** If `FEAT-1600`/`FR-1670`'s future
  package does not import `engine/sun.py::cats_phase_angle_deg()` and instead re-implements the
  same geometry, the two could silently drift apart — flagged in Dependencies above for whoever
  plans that package next.
- **Scope risk (CATS-banding, `BL-0154`).** This package deliberately ships the simplest grounded
  design (an unbanded numeric readout) rather than guessing at a visual-banding scheme the inputs
  don't commit to — low risk, since narrowing scope to what's grounded cannot itself introduce a
  defect, but a future enhancement pass will need to revisit this once `BL-0154` closes.

## Rollback Considerations

Every change in this package is additive — a new engine function, a new session-layer read method,
a new HTTP route, and a new client-side rendering surface, none of which modifies or removes any
existing function, route, or rendering surface. Reverting this package's changes removes the new
capability entirely with no data-migration concern: no vignette, save file, or `EventLog` entry
shipped before this package depends on anything it adds (the operator's origin/chase/target
selection is explicitly non-persistent, per Design Decision 3).
