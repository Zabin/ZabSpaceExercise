> **Document ID:** FS-130
> **Version:** 1.0
> **Status:** 🚧 Open Questions outstanding — not yet ✅ Ready for implementation planning (see
> Open Questions below; none is a research/requirements blocker, all are `07-implementation-
> planning`-level design decisions this spec deliberately leaves open per this skill's own rules)
> **Note on this repository's chain:** unlike every prior `FS-1xx`/`2xx`/`3xx` document in this
> set (each of which notes "no `05-feature-decomposition` Feature Catalog exists here"), this
> document's approved input **is** a real Feature Catalog entry — `FEAT-8200` in
> [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md),
> produced by a `05-feature-decomposition` run earlier in this same pipeline thread (run #83,
> 2026-10-03). `Purpose`/`Scope`/`Dependencies`/`Affected Subsystems`/`Related ADRs` below are
> carried forward from that catalog entry, not re-derived.
> **Dependencies:** [FS-121](FS-121-ephemeris-export.md) (Ephemeris Export — the sibling,
> one-shot CSV/CCSDS-OEM RIC export this Feature's live view reuses the same RIC-transform
> grounding from; a peer, not a build-order dependency: neither Feature requires the other to
> exist first), [FS-105](FS-105-spacecraft-operations.md) (Spacecraft Operations — the fog-of-war/
> `CellController` boundary this Feature's cell-scoped path rides), [FS-106](FS-106-white-cell-dashboard.md)
> (White Cell Dashboard — the god-view path this Feature's White-Cell/no-cell variant rides)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0107` (the live,
> operator-selectable RIC-frame view request), `BL-0111` (the CATS overlay extension), `BL-0151`
> (open phase-angle-default design ambiguity), `BL-0152` (shared phase-angle-computation note
> with `FS-122`'s forthcoming `FR-1670` spec), [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-8210`, `FR-8220`, [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md)
> `FEAT-8200`
> **Produces:** a live, operator-selectable RIC-frame relative-motion view (`FR-8210`) and, when a
> chase/observer satellite is also selected within it, a live CATS/illumination-phase-angle
> readout for that chase-target pair (`FR-8220`), satisfying both in full
> **Feature Mapping:** FS-130 (this document)
> **Related Topics:** [R127](../research/encyclopedia/R127-conjunction-assessment-and-collision-avoidance.md)
> (v1.1 — grounds the RIC/RTN-frame relative-motion display convention and operator-selectable
> origin this Feature implements), [R109](../research/encyclopedia/R109-sensor-operations.md)
> (v1.3 §3.11 — grounds the CATS/illumination phase angle this Feature's overlay displays), [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md)
> (RIC/LVLH transform math), [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md)
> (the `lvlh` maneuver-entry-mode parameterization reusing the same transform)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-130 — Live RIC-Frame Relative-Motion View & CATS Overlay

## Purpose

Let an operator (Blue/Red cell, or White Cell) select a target satellite as the origin of a live,
interactive RIC (Radial-In-track-Cross-track) relative-motion view, see other objects' position and
motion rendered relative to that chosen origin as the session clock advances, and — when a specific
chase/observer satellite is also selected within that view — see a live readout of the Sun-target-
observer illumination phase angle (the "CATS angle") for that chase-target pair, predicting whether
the chaser's optical sensor would get a usable, glare-free, or silhouetted view of the target
(`FEAT-8200`'s own `Purpose`; `FR-8210`, `FR-8220`). This is distinct from the existing one-shot
CSV/CCSDS-OEM RIC export (`FR-7410`/`FR-7420`/`FR-7430`, `FS-121`), which is non-interactive and not
rendered live — `BL-0107`'s own filed request is explicit on this distinction.

## Scope

**In scope:** the live, operator-selectable RIC-frame relative-motion view itself (`FR-8210`); the
CATS illumination-phase-angle overlay for the view's selected chase/observer satellite (`FR-8220`),
as an extension of `FR-8210` rather than a standing-alone capability, per `BL-0111`'s own stated
relationship; fog-of-war-correct rendering for a cell-scoped operator (never ground truth, never
another cell's belief); the White-Cell/no-cell ground-truth variant via the existing god-view path.

**Out of scope (named, not silently absorbed):** the underlying RIC-transform math itself
(`engine/maneuver.py::lvlh_frame`, `session/ephemeris.py::to_ric()`) — already implemented and
`VERIFIED` via `FS-121`/`IP-1210`, reused here, not re-derived; the one-shot CSV/CCSDS-OEM export
format (`FR-7410`/`FR-7420`/`FR-7430`, `FS-121`) — a sibling capability, not a dependency either
direction; using the CATS angle as an access-window *gating* criterion for passive EO sensor
tasking generally (`FR-1670`, `FEAT-1600`) — a materially broader, distinct capability with its own
forthcoming Feature Specification against `FS-122`'s existing document; the concrete default
phase-angle range/degradation-curve shape for `FR-8220`'s overlay — named as Open Question 1 below,
not invented here.

## Requirements Implemented

- `FR-8210` — Live, operator-selectable RIC-frame relative-motion view.
- `FR-8220` — CATS illumination-phase-angle overlay for the RIC view's selected chase satellite.

## User Workflows

1. **A Blue or Red operator opens the RIC-frame view and selects a satellite as the frame's
   origin.** Only satellites the requesting cell currently holds a `Track` on (or owns) are
   selectable, per the existing fog-of-war rule (`FR-6210`) every other cell-scoped view already
   enforces.
2. **The view renders every other object the same cell can see, live, relative to the selected
   origin, in RIC coordinates.** As the session clock advances, the rendered relative positions
   update without a page or session reload (`FR-8210`'s own Acceptance Criteria).
3. **The operator reselects a different origin satellite.** The view re-renders relative to the new
   origin; no other view state (e.g. White Cell's clock-pause state) is disturbed.
4. **The operator additionally selects a chase/observer satellite within the same view** (which may
   or may not be the same object as the RIC-frame origin). The view adds a live, continuously
   updating CATS-angle readout for that chase-target pair (`FR-8220`).
5. **White Cell opens the same view via the existing god-view path.** Ground truth is rendered for
   every object, not only the requesting cell's own belief — mirroring `FR-4610`'s existing
   god-view/view-as-cell mechanism (`FS-106`), not a second, parallel unfiltered route.

## System Behaviour

- **Normal path — `FR-8210`, cell-scoped.** Given a selected origin satellite the requesting cell
  holds a `Track` on (or owns), the system computes every other visible object's state relative to
  that origin in the RIC basis — reusing `session/ephemeris.py::to_ric()`'s existing transform
  (itself built on `engine/maneuver.py::lvlh_frame()`), evaluated against the live, current-sim-time
  state rather than a stored time-span sample series — and returns it for live rendering.
- **Edge case — `FR-8210`, origin not visible to the requesting cell.** The selection is rejected
  (mirroring how every other fog-of-war-scoped view already handles a request for an object the
  cell cannot see); the view does not silently fall back to a different origin or to ground truth.
- **Edge case — `FR-8210`, origin reselected mid-session.** The view re-renders relative to the new
  origin on the next read; no state outside this view's own current-origin selection changes.
- **Normal path — `FR-8220`.** Given a selected chase/observer satellite and a selected target
  within the same view, the system computes the Sun-target-observer phase angle at the current sim
  time — the Sun direction from `engine/sun.py::sun_unit_eci()`, the target→chaser vector from the
  same live state `FR-8210`'s own rendering already computes — and returns it as a read-only,
  continuously updating numeric value.
- **Edge case — `FR-8220`, no chase/observer satellite selected.** No CATS readout is computed or
  displayed; `FR-8210`'s own view is otherwise unaffected (`FR-8220`'s own Preconditions).
- **Normal path — White-Cell/no-cell variant.** Mirrors `FR-4610`'s existing god-view mechanism: the
  same computation runs against ground truth rather than a `Track`-filtered subset, through the
  same existing no-cell endpoint class `FR-6220` already names, never a new cell-scoped route that
  would leak ground truth.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/ephemeris.py` | Owns the existing `to_ric()` RIC transform (`FS-121`/`IP-1210`, `VERIFIED`); extended to also serve a live, current-sim-time relative-state query against the selected origin, not only a stored time-span sample series. |
| `engine/maneuver.py` | Owns `lvlh_frame()`, the underlying RIC/LVLH basis computation `to_ric()` already calls; unchanged — read, not modified, by this Feature. |
| `engine/sun.py` | Owns `sun_unit_eci()`, the Sun-direction primitive `FR-8220`'s phase-angle computation reads; unchanged — read, not modified, by this Feature. |
| `session/cells.py` (`CellController`) | Owns the fog-of-war filtering boundary (`FR-6210`) this Feature's cell-scoped path must be read through — the same boundary `session/scene.py::build_scene()` already reads through for the existing belief-scene/2D-map rendering this view is architecturally a sibling of. |
| `session/api.py` (`SessionAPI`) | Owns the single seam (`FR-6110`) a new cell-scoped read for this view must be exposed through, consistent with every other existing `api.get_*(sid, cell, ...)` method `ui_web/server.py`'s routes already call. |
| `ui_web/server.py` + `ui_web/static/` | Owns the new live-view's browser-facing route and rendering — a new `GET /api/sessions/{sid}/<resource>/{cell}` route following the exact shape every existing cell-scoped read route already uses (`/view/{cell}`, `/scene/{cell}`, `/telemetry/{cell}/{asset}`), and a new client-side rendering surface alongside the existing belief-map/3D-globe surfaces. The exact route path/query-parameter naming (how the origin satellite and, separately, the chase/target pair are specified) is Open Question 2 below. |
| `session/manager.py` (`SessionManager`) | Owns the White-Cell god-view/view-as-cell mechanism (`FR-4610`, `FS-106`) this Feature's White-Cell/no-cell variant rides, unmodified. |

## Interfaces Used

- `INT-0001` (Browser ↔ Operator Console) — the browser-facing side of this view's new live render
  surface.
- `INT-0006` (Console → SessionAPI seam) — the new read's path through the single `SessionAPI` seam
  (`FR-6110`), consistent with every other cell-scoped view.
- `INT-0007` (CellController → Engine Custody) — the fog-of-war-filtered `Track`/custody read this
  view's cell-scoped path consumes, identically to `session/scene.py::build_scene()`'s existing use
  of the same interface.

No new interface is introduced; this Feature's live-view route is a new *route*, not a new *ICD
interface* — it is carried by the same three existing interfaces every other cell-scoped belief
view already uses.

## Data Model Changes

None required. This Feature reads existing `WorldState`/`Track`/`Asset`/`OrbitState` fields through
the existing propagator (`ModeratePropagator`, per `engine/propagator.py`) and the existing `to_ric()`/
`lvlh_frame()`/`sun_unit_eci()` functions — it computes and renders a derived view, the same way
`session/scene.py::build_scene()` and `engine/telemetry.py`'s read-time sampling already do, without
adding, removing, or mutating any persisted field.

## State Changes

None persistent. The operator's current origin selection (and, for `FR-8220`, the current chase/
target selection) is live, per-viewer UI state — analogous to the existing 2D map/3D globe's own
currently-selected-asset state, which is not written to `WorldState`/`EventLog` today either. Per
`CLAUDE.md`'s browser-storage guidance, a convenience remembering the last-selected origin across a
page reload, if wanted, belongs in `localStorage`, never in session-shared state — Open Question 3
below names this as undecided, not assumed.

## Error Handling

- **Selecting an origin (or, for `FR-8220`, a chase/target) the requesting cell cannot see.** The
  request is rejected with the same observable-error contract every other fog-of-war-scoped read
  already uses for an out-of-custody object — no distinct new error class is introduced.
- **Selecting an origin satellite that no longer exists (destroyed, decommissioned) mid-session.**
  The view's next read for that origin fails the same way any other now-stale-object reference
  already fails elsewhere in the existing read paths — this Feature introduces no new failure mode
  here, per `FR-8210`'s own Postconditions (a cell-scoped rendering never exposes data for an object
  it should not).
- **`FR-8220` requested with only one of the two required selections (chase or target) made.** No
  CATS readout is computed; this is a normal, expected state (`FR-8220`'s own Preconditions), not an
  error.

## Performance Considerations

- `NFR-1100` ("Responsive UI at high time-multipliers") applies directly — the live view must
  re-render the selected origin's relative geometry at the same cadence the existing belief-map/3D-
  globe rendering already sustains at the documented time-multiplier range, without a separate,
  slower polling cadence.
- `NFR-1900` ("UI-agnostic engine with enforced test coverage") applies to the engine-side
  computation this view calls (`to_ric()`/`lvlh_frame()`/`sun_unit_eci()`) — all three are already
  pure, UI-agnostic functions; this Feature must not couple them to any UI-specific state to satisfy
  the live-rendering requirement.
- No new NFR is required beyond these two already-existing ones (consistent with `05-feature-
  decomposition`'s own Feature Review, which found `NFR-1100`/`NFR-1900` already cover this
  Feature's live-update quality attribute).

## Security Considerations

- `ADR-0004` (fog-of-war at the boundary) governs this Feature's entire cell-scoped path: the new
  read must be filtered at the `SessionAPI`/`CellController` boundary exactly like every existing
  cell-scoped view, never by the UI withholding data client-side.
- `ADR-0015` (the documented no-cell ground-truth exception / LAN trust model) governs the White-
  Cell/no-cell variant: it must ride the existing named exception set (`FR-6220`), not become a new,
  separately-named unfiltered route.
- No new trust boundary is introduced — this Feature's security posture is identical to every other
  existing cell-scoped belief-rendering surface (`session/scene.py::build_scene()`,
  `engine/telemetry.py`'s per-cell sampling).

## Acceptance Criteria

1. Given a running session and an operator selecting satellite X (which the requesting cell holds a
   `Track` on, or owns) as the RIC-frame origin, the view's displayed relative positions for every
   other cell-visible object match the values `to_ric()` would compute against the live `WorldState`
   at the current sim time.
2. Given the operator reselects satellite Y (also visible to the cell) as the origin, the view's
   displayed values update to be relative to Y, with no page or session reload.
3. Given a cell-scoped request, the rendered objects are limited to that cell's own `Track`/owned-
   asset set — never ground truth, never another cell's belief (verified the same way `FR-6210`'s
   own existing Acceptance Criteria is verified for every other cell-scoped view).
4. Given White Cell opens the same view via the existing god-view path, every object (not only one
   cell's belief) is rendered, matching `FR-4610`'s own exact-match standard for its god-view path.
5. Given a selected chase/observer satellite and target with a known Sun position, the displayed
   CATS angle matches the geometrically computed Sun-target-chaser angle at the current sim time to
   within floating-point tolerance.
6. Given the operator reselects a different chase or target satellite, the displayed CATS angle
   updates accordingly; given neither is selected, no CATS angle is displayed and `FR-8210`'s own
   view is otherwise unaffected.
7. Given an origin/chase/target selection naming an object the requesting cell cannot see, the
   request is rejected per the existing fog-of-war error contract (Criterion 3's same standard,
   applied to the rejection path).

## Verification Plan

- Criteria 1, 2, 5, 6: **Test** — a numeric comparison against `to_ric()`'s own existing, already-
  tested output (per `FS-121`/`IP-1210`'s existing `test_ephemeris.py` coverage) and against an
  independently-derived phase-angle value for a known Sun/target/chaser geometry.
- Criteria 3, 4, 7: **Test** — the same fog-of-war test pattern every other cell-scoped view's
  existing test suite already uses (e.g. `session/test_scene.py`-style custody-filter assertions),
  extended to this view's own route.
- No criterion requires Demonstration/Analysis/Inspection beyond what `Test` already covers, per
  `FR-8210`/`FR-8220`'s own stated Verification Method (`Test`) in both cases.

## Dependencies

- [FS-121](FS-121-ephemeris-export.md) — the sibling capability whose already-`VERIFIED` RIC-
  transform implementation (`to_ric()`/`lvlh_frame()`) this Feature reuses directly; a shared-
  utility relationship, not a build-order dependency (`FS-121`'s own code already exists and needs
  no change for this Feature to consume it).
- [FS-105](FS-105-spacecraft-operations.md) — the fog-of-war/`CellController` boundary this
  Feature's cell-scoped path is read through.
- [FS-106](FS-106-white-cell-dashboard.md) — the god-view/view-as-cell mechanism this Feature's
  White-Cell/no-cell variant rides.

## Risks

- **Ambiguity risk (Open Question 1, phase-angle default).** `R109` v1.3 §3.11 supplies a concrete,
  but explicitly single-source-flagged, starting default (0°-90° ground / 0°-150° space) for a
  *gating* use (`FR-1670`) — `FR-8220`'s *display-only* use has no stated minimum/maximum range at
  all (it is simply shown as a number across its full 0°-180° domain), so this risk is narrower than
  it first appears: the open question is really about whether to visually flag a "poor viewing
  geometry" band on the readout, not about rejecting any value. Low severity.
- **Dependency risk (Open Question 2, route/UI shape).** The exact new route path and how the
  origin/chase/target selections are specified (query parameters vs. a request body vs. a session-
  scoped selection state) is not committed by any existing architecture document — `07-
  implementation-planning` must choose a shape consistent with the existing `/view/{cell}`/
  `/scene/{cell}` convention this spec names, but this spec does not pick the exact parameter names
  itself, per this skill's own rule against inventing an API shape no ADR commits to. Low severity
  (the *pattern* is settled; only the literal names are open).
- **Consistency risk (cross-Feature, not this Feature's own defect).** `FR-8220`'s phase-angle
  computation and `FR-1670`'s (a distinct Feature, `FEAT-1600`, its own forthcoming Feature
  Specification against `FS-122`) should share one underlying phase-angle function, per `BL-0152`'s
  own finding — flagged here for whoever specifies `FR-1670` next to confirm, not resolved by this
  document (`FR-1670` is out of this Feature's scope, named above).

## Open Questions

1. **What usable/degraded-illumination banding, if any, should the CATS-angle readout visually
   flag?** `R109` v1.3 §3.11's ground≈90°/space≈150° figures are a single-AMOS-source anchor for an
   *access-gating* use (`FR-1670`), not a committed display-threshold for this Feature's purely
   informational readout. Resolving this needs either a second corroborating source for `R109`
   §3.11's figures, or an explicit project-owner decision that `FR-8220`'s display is unbanded (a
   plain number, no color/flag) until one exists. Routed to whoever runs `07-implementation-
   planning` for this Feature, or back to `02-research-ow-orbital-mechanics` if a second source is
   sought first.
2. **What is the new route's exact path and selection-parameter shape?** No existing ICD interface
   or ADR commits to a specific URL/parameter convention for this view beyond the general `GET
   /api/sessions/{sid}/<resource>/{cell}` pattern every existing cell-scoped route already follows.
   Resolving this is explicitly a `07-implementation-planning` design decision, consistent with this
   skill's own rule against specifying an API shape no architecture document has committed to.
3. **Should the operator's last-selected origin/chase/target persist across a page reload, and if
   so, where?** `CLAUDE.md`'s browser-storage guidance says a per-viewer convenience like this
   belongs in `localStorage`, never session-shared state, but no existing document states whether
   this Feature needs that convenience at all (as opposed to always starting unselected). Routed to
   `07-implementation-planning`.

## Related ADRs

`ADR-0004` (fog-of-war at the boundary), `ADR-0008` (browser-over-desktop-GUI presentation choice),
`ADR-0015` (documented no-cell ground-truth exception / LAN trust model).

## Related Interfaces

`INT-0014` (AAR/Replay → Engine) — not used directly by this Feature, but the same interface
`FS-121`'s sibling one-shot export rides; named here for a reader comparing the two Features'
interface footprints, not because this Feature consumes it.
