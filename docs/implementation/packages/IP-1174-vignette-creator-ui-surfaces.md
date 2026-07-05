# IP-1174 — Vignette Creator UI Surfaces

> **Package ID:** IP-1174
> **Version:** 1.0
> **Status:** 🔴 BLOCKED *(not authorized — MSTR-006 §3; also depends on
> [IP-1171](IP-1171-typed-payload-bus-parameters.md), [IP-1172](IP-1172-per-cell-roe-enforcement.md),
> and [IP-1173](IP-1173-vignette-creator-draft-session.md) — see Dependencies. This is the last
> package `08-code-implementation` should pick up in Tranche 3.)*
> **Dependencies:** [FS-117](../../features/FS-117-vignette-creator.md) v1.1 (`FR-5120`, `FR-5130`,
> `FR-5140`, `FR-5150`, `FR-5160`), [ADS-5100A](../../architecture/ADS-5100A-vignette-creator-session-and-ui.md)
> §2/§4/§5/§6, [IP-1173](IP-1173-vignette-creator-draft-session.md) (the draft-session API this UI
> is a thin client over), [IP-1171](IP-1171-typed-payload-bus-parameters.md)/
> [IP-1172](IP-1172-per-cell-roe-enforcement.md) (the schemas this UI's forms/selectors present),
> [FS-115](../../features/FS-115-session-setup.md)/[IP-1151](IP-1151-seat-role-assignment.md)
> (`assign_role`/`staffing_report` this UI's seat/role matrix reuses — `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the complete in-app Vignette Creator surface `FS-117` describes
> **Feature Reference:** [FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md)
> (`FR-5120`-`FR-5160` slice)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js),
> [`spacesim/session/scene.py`](../../../spacesim/session/scene.py),
> [`docs/vignettes/GROUND-INFRASTRUCTURE.md`](../../vignettes/GROUND-INFRASTRUCTURE.md)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package — the largest in this tranche, covering five requirements
(`FR-5120`-`FR-5160`) that together are every operator-visible surface of the Vignette Creator.
Confirmed directly against the live code at authoring time: `session/scene.py`'s `build_scene(world,
cell)` already supports a ground-truth-equivalent call (no `CellController` fog-of-war filtering
happens inside `build_scene()` itself — filtering is applied by the caller, per `CLAUDE.md`'s "fog
of war at the boundary" invariant — so this package's 2D/3D preview calls it directly against the
draft session's `world`, the same pattern White-Cell-only godview surfaces already use); the
existing `POST /api/sessions/{sid}/force/tle` route already validates a manually pasted TLE via
`sgp4` the same way this package's TLE-entry form needs.*

## Package ID

IP-1174

## Title

Vignette Creator UI Surfaces

## Objective

Build every White-Cell-facing surface of the Vignette Creator — a synchronized JSON view, a 2D/3D
initial-state preview, TLE/lat-long asset entry with type/cell/name fields, an asset menu
(edit/reassign/delete), and a seat-count-declaration + seat/role-assignment matrix — all as thin
clients over [IP-1173](IP-1173-vignette-creator-draft-session.md)'s draft-session API, presenting
[IP-1171](IP-1171-typed-payload-bus-parameters.md)'s typed parameter sub-schemas and
[IP-1172](IP-1172-per-cell-roe-enforcement.md)'s per-cell ROE selectors.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md) (`FR-5120`-`FR-5160` slice)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-5120 | Synchronized JSON view | A JSON panel reads/writes the same draft-session state the form UI does — every mutating call (asset add/edit/parameter change/ROE selection) goes through the same `IP-1173` draft-session API regardless of which view triggered it, then both views re-fetch the same current-state read endpoint, so neither view maintains independent client-side state. |
| FR-5130 | 2D/3D initial-state preview | Calls `session/scene.py`'s `build_scene(world, cell)` directly against the draft session's `world` (ground-truth mode, no `CellController` filtering — the same pattern existing White-Cell-only godview surfaces use), rendered via the existing 2D-map/3D-globe front-end code (`app.js`/`globe.js`/`world.js`), refreshed on every mutation. |
| FR-5140 | TLE and lat/long asset entry | A TLE-paste form posts to the existing `POST /api/sessions/{sid}/force/tle` route (unmodified) against the draft session id, paired with new asset-type/cell-assignment/name fields this package adds to the request; a lat/long entry form offers `docs/vignettes/GROUND-INFRASTRUCTURE.md`'s curated site list as a picker before a free-entry coordinate fallback, paired with the same three fields. |
| FR-5150 | Asset menu (edit, reassign, delete) | A per-asset menu (in both the 2D/3D preview and a plain asset list) calls new edit/reassign/delete operations against the draft session's asset list, with the JSON view and 2D/3D preview both reflecting the change on the next state read. |
| FR-5160 | Seat-count declaration and seat/role-assignment matrix | A new seat-count-declaration step (per cell) generates seat identifiers; a checkbox-grid matrix (seats × assets, bus/payload/both) calls `IP-1151`'s existing `assign_role(seat, asset_or_constellation, role)` for each checked cell — this package adds the declaration step and the matrix presentation only, reusing the existing assignment mechanism unmodified. |

## Architecture Components

Per `FS-117`'s own Subsystem Responsibilities:

- **C4 Operator Console** — `ui_web/server.py` gains the new routes below; `ui_web/static/app.js`
  (and possibly a new dedicated JS module, given the surface's size — see Files to Create) gains
  the Creator's UI: JSON view, 2D/3D preview wiring, TLE/lat-long/asset-entry forms, asset menu,
  seat/role matrix. All as thin clients over `IP-1173`'s draft-session API — no client-side
  authoritative state beyond what's needed for responsive editing before the next server read.
- **C2 Session / Application Layer** — new small additions to `session/inprocess.py`/`manager.py`
  for asset edit/reassign/delete (parallel to existing asset-add via `force/tle`) and the
  seat-count-declaration state (a small list of generated seat identifiers per cell, feeding the
  matrix UI, per `FS-117`'s own State Changes section) — this package's session-layer surface is
  thin; the substantial session-layer work is `IP-1173`'s.
- **C6 White Cell** — the sole actor exercising this package's UI, consistent with `INT-0003`'s
  existing scope (no Blue/Red operator interaction).

## Interfaces

- **INT-0003** (White Cell Facilitator ↔ Operator Console, "in-app scenario builder") — this
  package is the Operator-Console half of the same interface [IP-1173](IP-1173-vignette-creator-draft-session.md)
  builds the session-layer half of.
- **INT-0002** (White Cell Facilitator ↔ Operator Console, exercise control) — the same interface
  `IP-1151`'s existing seat-assignment step uses; this package's seat/role matrix is a richer
  presentation over the same underlying `assign_role` call, not a new interface.

**Not used, explicitly:** `INT-0013` (Content & Data → Space-Track.org) — this package's TLE entry
is manual-paste-only, per `FS-117`'s own Scope.

## Files to Create

- `spacesim/ui_web/static/creator.js` *(proposed, new)* — given the size of this surface (five
  requirements' worth of forms, a JSON editor, and 2D/3D preview wiring), a dedicated module rather
  than growing `app.js` further, following the existing pattern of `globe.js`/`graph.js` as
  separate, focused front-end modules alongside `app.js`. Handles: the JSON view's read/write
  loop, the TLE/lat-long/asset-entry forms, the asset menu, and the seat-count-declaration + matrix
  UI. Reuses `globe.js`/`world.js` (3D globe) and `app.js`'s existing 2D-map drawing code for the
  preview itself, rather than duplicating rendering logic.

## Files to Modify

- `spacesim/ui_web/server.py` *(proposed)*:
  - Extend the TLE-add flow (or add a Creator-specific variant) to accept asset-type/cell-
    assignment/name fields alongside the existing `TleRequest` shape.
  - A new lat/long asset-entry route accepting the same asset-type/cell/name fields plus either a
    curated-site-list selection or free-entry coordinates.
  - New asset edit/reassign/delete routes operating on the draft session's asset list
    ([IP-1173](IP-1173-vignette-creator-draft-session.md)'s API).
  - A new seat-count-declaration route (per cell) and a read route the matrix UI polls, alongside
    the existing `/roles/assign`/`/roles/staffing` routes (`IP-1151`, unmodified).
  - A JSON-view read/write route pair (or reuse of a single state-read/state-write pair the form UI
    also uses) — per `FR-5120`'s own requirement that both views share one state, not two parallel
    endpoints with independent semantics.
- `spacesim/ui_web/static/index.html` *(proposed)* — a new "Vignette Creator" menu entry/panel,
  mirroring the existing per-feature menu-section pattern (`IP-1151`'s seat-assignment section,
  `IP-1130`'s Observer section) rather than inventing a new page-layout convention.
- `spacesim/ui_web/static/app.js` *(proposed, minimal)* — a small entry point wiring `creator.js`
  into the existing menu/panel-switching logic, consistent with how `globe.js`/`graph.js` are
  already wired in.

**Explicitly out of scope for this package:** the draft-session lifecycle and reverse-serialization
itself ([IP-1173](IP-1173-vignette-creator-draft-session.md)'s concern — this package only calls
its API); the typed-parameter sub-schemas and per-cell ROE data model themselves
([IP-1171](IP-1171-typed-payload-bus-parameters.md)/[IP-1172](IP-1172-per-cell-roe-enforcement.md)'s
concern — this package only presents forms/selectors over them); the mid-exercise inject-menu reuse
of this same surface — an explicitly later, separately scoped phase per `FS-117`'s own Scope
boundary.

## Implementation Tasks

**Not started — not authorized (MSTR-006 §3).** Proposed sequence once authorized:

1. Confirm [IP-1173](IP-1173-vignette-creator-draft-session.md), [IP-1171](IP-1171-typed-payload-bus-parameters.md),
   and [IP-1172](IP-1172-per-cell-roe-enforcement.md) have reached at least `COMPLETE` (ideally
   `VERIFIED`) before starting — this package's forms/selectors need their APIs/schemas to exist.
2. Write failing tests for each Acceptance Criterion below before implementing each surface
   (per `CLAUDE.md`'s test-first mandate) — this package's tests are necessarily more
   integration-shaped (HTTP route + resulting draft-session state) than the engine-level packages
   in this tranche.
3. Implement the JSON view read/write route pair and confirm the form UI and JSON view converge on
   one shared state (the single most likely implementation defect this Feature names — test this
   explicitly, not just individually).
4. Implement the 2D/3D preview wiring (`build_scene(world, cell)` called against the draft
   session's `world`, ground-truth mode), reusing existing globe/map rendering code.
5. Implement TLE-paste and lat/long asset entry, including the curated-site-list picker (reading
   `docs/vignettes/GROUND-INFRASTRUCTURE.md`'s site data — confirm at implementation time whether
   this needs a small loader or the existing content is already machine-readable; if not, add the
   minimal parsing needed, not a new site-authoring format).
6. Implement the asset menu (edit/reassign/delete).
7. Implement the seat-count-declaration step and the seat/role matrix UI, calling `IP-1151`'s
   existing `assign_role` per checked cell.
8. Wire all of the above into a new "Vignette Creator" menu entry, confirming no regression to any
   existing menu/panel.

## Tests to Add

*(Proposed — none exist yet.)*

- `spacesim/tests/test_vignette_creator_ui.py` *(new)* — one test per Acceptance Criterion (HTTP-route
  level, mirroring the existing pattern of testing `ui_web/server.py` routes directly rather than
  through a browser):
  - Given an edit made via the JSON-view route, a subsequent form-view-equivalent read reflects it,
    and vice versa (`FR-5120`).
  - Given assets added/edited/reassigned/deleted, a scene-read against the draft session reflects
    each change with no fog-of-war filtering applied (`FR-5130`/`FR-5150`).
  - Given a manually pasted, valid TLE with required fields, the asset appears in the draft
    session's asset list (`FR-5140`).
  - Given a lat/long entry, the same three-way consistency holds, and the curated site list is
    offered before free-entry coordinates (`FR-5140`).
  - Given a declared seat count per cell and a matrix assignment, the resulting `role_assignments`
    state is identical in shape to what `assign_role` already produces for the same binding entered
    directly (`FR-5160`).
- A lightweight manual/`run-spacesim`-driven browser check (per `CLAUDE.md`'s "UI or frontend
  changes... test the golden path... before reporting complete") is recommended once implemented,
  since this package's browser-side behavior (JSON-view/form-view convergence, 2D/3D preview
  refresh) is not fully exercised by HTTP-route-level tests alone.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `docs/features/FS-117-vignette-creator.md`'s `Referenced By` metadata — add this package once
  authored (this pass); a future `06-feature-specification` touch should close Open Questions 3
  (matrix UI layout) and 9 (JSON-view semantics — already resolved as bidirectional by `FS-117`'s
  own System Behaviour text, just not yet marked closed in its Open Questions list) once this
  package's implementation settles the exact layout.
- `docs/training/` — once implemented, the training-manual-authoring skill (`08-training-manual-authoring`)
  should add White Cell manual coverage for this new setup-time capability, per this project's
  standing "training corpus is co-equal" policy — flagged here as a follow-up, not performed by
  this package (out of this skill's write scope).
- `CLAUDE.md`'s Code Map — a brief addition for `ui_web/static/creator.js` and the new
  Creator-specific routes.

## Definition of Done

- [ ] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3) — not yet on record.
- [ ] The JSON view and form UI never disagree about the draft session's current state (`FR-5120`).
- [ ] The 2D/3D preview updates to match every asset add/edit/reassign/delete within the same
  authoring session, with no `CellController` fog-of-war filtering (`FR-5130`).
- [ ] TLE-paste and lat/long entry both work with required type/cell/name fields, with the curated
  site list offered before free entry for lat/long (`FR-5140`).
- [ ] The asset menu's edit/reassign/delete operations are reflected consistently across the asset
  list, JSON view, and 2D/3D preview (`FR-5150`).
- [ ] A declared seat count + matrix assignment produces `role_assignments` state identical in
  shape to `assign_role`'s existing one-at-a-time mechanism (`FR-5160`).
- [ ] No regression to any existing menu/panel/route.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `spacesim/tests/test_vignette_creator_ui.py` exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (this package's routes
  operate on an unstarted draft session — no event log, no clock advance).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Full existing suite re-run with zero regressions.
- [ ] Independently confirm (not merely re-cite) that the JSON view and form UI genuinely share one
  draft-session state, by driving both a JSON-view edit and a form-equivalent edit against the same
  draft session and confirming each is visible to the other — not merely that both routes exist.
- [ ] Independently confirm the 2D/3D preview calls `build_scene()` in ground-truth mode (no
  `CellController` import/call anywhere in this package's new code), consistent with `ADR-0004`.

## Dependencies

- **Upstream:** [FS-117](../../features/FS-117-vignette-creator.md) v1.1,
  [ADS-5100A](../../architecture/ADS-5100A-vignette-creator-session-and-ui.md) §2/§4/§5/§6 (binding
  UI-surface grounding); [IP-1173](IP-1173-vignette-creator-draft-session.md) (the draft-session API
  this package is a thin client over — not yet built); [IP-1171](IP-1171-typed-payload-bus-parameters.md)/
  [IP-1172](IP-1172-per-cell-roe-enforcement.md) (the schemas this package's forms/selectors present
  — not yet built); [IP-1151](IP-1151-seat-role-assignment.md) (`assign_role`/`staffing_report` —
  `VERIFIED`, reused unmodified).
- **Downstream:** None yet — this closes `FS-117`'s full scope; a future mid-exercise inject-menu
  reuse of this same surface is explicitly out of scope (a later, separately scoped phase).
- **Build-sequencing:** Last package in Tranche 3 — depends on all four other packages in this
  tranche reaching at least `COMPLETE` for its forms/selectors to have real schemas/APIs to present.

## Risks

- **The largest, most integration-heavy package in this tranche** — five requirements, a new
  dedicated JS module, and dependencies on all four sibling packages. If `08-code-implementation`
  finds this too large for one focused run once the sibling packages' actual shapes are known, a
  further lettered split (e.g. `IP-1174A` entry/asset surfaces, `IP-1174B` seat/role matrix + JSON
  view) is a legitimate mid-implementation finding to route back through this skill, per the
  established `FS-105`/`FS-115` split precedent — not something to force into one package if the
  real seams turn out finer than planned here.
- **Two data paths for one draft (JSON view vs. form UI) is the single most likely implementation
  defect**, carried forward from `ADS-5100A`'s own Risk 1, `FS-117`'s own Risks, and
  [IP-1173](IP-1173-vignette-creator-draft-session.md)'s Risks — this package is where that risk is
  actually realized in code, so its own test suite must explicitly assert convergence, not just
  route existence.
- **Exact seat/role matrix UI layout is undecided** (`FS-117` Open Question 3) — this package's
  Implementation Tasks proceed with a reasonable default (checkbox grid, seats × assets ×
  bus/payload/both) per `ADS-5100A`'s own description; the exact dimensions/interaction details are
  left to implementation-time UI judgment, not escalated, consistent with how low-stakes UI-layout
  choices were handled in prior packages (e.g. `IP-1151`'s unsatisfied-report format).
- **`docs/vignettes/GROUND-INFRASTRUCTURE.md`'s curated site list may not yet be in a
  machine-readable format** — if it's prose/markdown-only, this package's Implementation Tasks
  include the minimal parsing needed; this is a small, disclosed unknown, not a blocking gap.
- **A browser-driven verification pass is recommended, not merely HTTP-route tests** — per
  `CLAUDE.md`'s own UI-testing guidance; flagged explicitly so `08-code-implementation` doesn't
  report this package complete on route-level tests alone without at least a `run-spacesim`-driven
  golden-path check.

## Rollback Considerations

Every new route and UI surface is additive — a new "Vignette Creator" menu entry, a new dedicated
JS module, and new session-layer asset-edit/seat-count routes. Reverting removes the entire Creator
UI with no effect on any existing menu, panel, or route (the underlying draft-session API from
[IP-1173](IP-1173-vignette-creator-draft-session.md) and the schema extensions from
[IP-1171](IP-1171-typed-payload-bus-parameters.md)/[IP-1172](IP-1172-per-cell-roe-enforcement.md)
can remain in place independent of this package's rollback, since they are read-only inputs this
package's UI consumes, not modified by it). No data-migration concern: this package writes no
persisted state beyond what the draft session and reverse-serialization function (both
[IP-1173](IP-1173-vignette-creator-draft-session.md)'s) already define.
