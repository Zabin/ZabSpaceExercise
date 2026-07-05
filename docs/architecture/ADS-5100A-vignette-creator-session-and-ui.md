> **Document ID:** ADS-5100A
> **Version:** 1.0
> **Status:** ✅ Authored
> **Dependencies:** [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md),
> [R107](../research/encyclopedia/R107-ground-segment-operations.md),
> [R137](../research/encyclopedia/R137-bus-and-payload-parameter-catalog.md),
> `docs/requirements/01-functional-requirements.md` `CR-11`,
> `docs/feature-planning/03-feature-catalog.md` `FEAT-5100`/`FEAT-5200`/`FEAT-5300`,
> `docs/vignettes/GROUND-INFRASTRUCTURE.md`
> **Referenced By:** [ADS-5100B](ADS-5100B-typed-parameters-and-per-cell-roe.md) (the sibling
> synthesis this document's UI surfaces expose), [FS-117](../features/FS-117-vignette-creator.md)
> (the Feature Specification this document grounds)
> **Produces:** the eventual Vignette Creator Feature Specification's System Architecture/User
> Workflows sections (`docs/pipeline/backlog.md` `BL-0052`, folding in `BL-0051`)
> **Feature Mapping:** `FEAT-5100` (which this synthesis will supersede/consolidate, not be
> absorbed into), `BL-0051`, `BL-0052`
> **Related Topics:** [ADS-5100B](ADS-5100B-typed-parameters-and-per-cell-roe.md),
> [ADR-0004](adr/ADR-0004-fog-of-war-at-boundary.md) (the fog-of-war boundary this document's
> ground-truth preview decision is consistent with, not an exception to)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

# ADS-5100A — Vignette Creator: Authoring Session & UI Architecture

*Workflow B (per-cluster synthesis), authored per the project owner's explicit instruction that the
Vignette Creator is a large, distinct feature and must be documented as such — not blended into any
other Feature Specification. Split from the sibling [ADS-5100B](ADS-5100B-typed-parameters-and-per-cell-roe.md)
by capability seam per this tier's own size discipline (`MSTR-006` §4): this document covers the
authoring-session architecture and UI surfaces; the sibling covers two Domain Model extensions
(typed payload/bus parameters, per-cell ROE) the UI here exposes but which are independently
significant design decisions. Anchored to `FEAT-5100` (In-App Iterative Vignette Builder, `EP-5000`,
0% built — no FS, no code) as the natural existing catalog entry, and folds in `BL-0051` (seat-count
declaration + role-assignment matrix UI), which shares this document's own UI surface.*

## 1. Executive Design Overview

`FEAT-5100` exists in the Feature Catalog but has never been built — White Cell still authors
vignettes by hand-editing YAML, which the Independent Strategic Review Board's own strategic
review already flagged as "White-Cell-hostile in practice" (`docs/feature-planning/02-epic-catalog.md`
EP-5000 Risk). The single biggest design tension this document resolves is **`CR-11`** — an
already-open Candidate Requirement asking where in-progress, unsaved vignette-authoring state
should live (server-session-scoped vs. browser-local) — which no approved document had answered
until the project owner decided directly this session: a **server-side draft session**, reusing
the existing engine/session machinery rather than a parallel browser-only mechanism. Everything
else in this document (JSON view, 2D/3D preview, TLE/lat-long/asset entry, the asset menu, the
seat/role matrix) is a UI surface over that one architectural decision, not a separate design
problem each.

## 2. System Architecture

- **C2 Session / Application Layer** owns the new **Draft Vignette Session** concept: a
  `SessionManager` instance created but never `start()`-ed (no clock advance, no scheduler tick,
  no order execution) — purely an in-memory staging area shaped like whatever `build_world()`
  would produce from a `Vignette`. Every mutation the Creator's UI performs (add/edit/reassign/
  delete an asset, add a ground site, set a bus/payload parameter, assign a seat to a role) is a
  method call against this draft session, reusing existing mechanisms wherever one already exists
  — most importantly the already-built `POST /api/sessions/{sid}/force/tle` endpoint (`sgp4`-
  validated, currently pre-start-only with zero UI wiring per this session's own code audit) for
  TLE-based asset entry, and `FS-115`/`IP-1151`'s `assign_role`/`staffing_report` for seat-to-role
  binding.
- **"Save as Vignette"** is a new, one-directional serialization: draft-session `WorldState` →
  `Vignette` object → YAML file. This is the *reverse* of `content/vignette.py`'s existing
  `build_world(vignette)` — a new function this synthesis names but does not implement (that is
  an Implementation Package's job), conceptually `vignette_from_world(world) -> Vignette`. It is
  **not** the same mechanism as `SessionManager.save_state()`/`from_state()` (`FS-110`, Save &
  Resume), which serialize/restore a *running* session's exact deterministic state (event log,
  RNG, scheduler) — the Creator's draft session never runs, so there is no event log or RNG state
  to round-trip; only the declarative initial-force/parameter shape a `Vignette` file already
  represents.
- **C4 Operator Console** owns the Creator's own UI surfaces, all reading/writing against the one
  draft session via C2:
  - **JSON view** — a raw-JSON read/write surface over the *same* draft-session state the form-based
    UI edits. Both views must read from and write to one shared source of truth (the draft session
    itself), never two independently-maintained data structures — see Risks §8.
  - **2D/3D initial-state preview** — reuses the existing render-from-custody scene/globe/map
    pipeline (`scene_from_world`, `globe.js`/`world.js`) in **ground-truth mode**: the draft session
    has no `CellController`/fog-of-war filtering applied, consistent with the existing precedent
    that White Cell's own godview endpoints (`/godview`, `/eventlog`) already expose ground truth
    without a cell binding (`CLAUDE.md` "LAN trust model") — this is the same trust boundary, not a
    new one, since only White Cell can reach the Creator at all.
  - **TLE entry** (asset type + cell assignment + name entry alongside) routes through the draft
    session's TLE-add path; **lat/long entry** for ground infrastructure routes through a
    draft-session equivalent of adding a `GroundSite`-backed `Asset`, paired with the same
    asset-type/cell/name fields, and should default-offer `docs/vignettes/GROUND-INFRASTRUCTURE.md`'s
    curated ~45-site list before falling back to free-entry coordinates (per
    [R107](../research/encyclopedia/R107-ground-segment-operations.md)'s siting-methodology
    subsection).
  - **Asset menu** (edit/reassign/delete) operates on the draft session's current asset list —
    no new data structure, just CRUD-style operations against the same in-memory `WorldState`
    every other surface reads.
  - **Seat/role matrix** (`BL-0051`): a setup step asking White Cell how many seats exist per cell,
    generating seat identifiers (e.g. `blue-1`..`blue-N`), then presenting a checkbox-grid UI
    (seats × assets, bus/payload/both) that calls the *same* `assign_role(seat, asset_or_constellation,
    role)` mechanism `FS-115`/`IP-1151` already ships — this document adds the seat-count
    declaration step and the matrix *presentation*, not a new assignment mechanism underneath it.

## 3. Domain Model

No new persistent entity beyond the **Draft Vignette Session** concept (§2) — a session-layer
lifecycle state, not a new Domain Model class the way `GDS-04` defines entities. The Creator reads
and writes the *existing* `Vignette`/`RoleRequirement`/`Parameter`/`Inject` schema (`content/vignette.py`)
unchanged: it is a new *authoring surface* over that schema, not a new schema — preserving the
content-as-data invariant (`CLAUDE.md` load-bearing invariant 6). Seat/role assignment reuses the
existing `role_assignments` mapping (`SessionManager`, `FS-115`) with one small addition: an
explicit seat-count declaration per cell (a list of generated seat identifiers), which today's
mechanism has no equivalent for — White Cell currently free-types an arbitrary seat-name string
per `assign_role` call with no upfront "how many seats exist" step.

## 4. User Stories

- *As White Cell, I open a blank Vignette Creator, add three Blue satellites by pasting TLEs and
  two Red ground stations by lat/long entry (picking from the curated site list), name and assign
  each to a cell, watch them appear on the 2D map and 3D globe immediately, and save the result as
  a new vignette file — without ever hand-editing YAML.*
- *As White Cell, I open an existing vignette in the Creator, see its raw JSON alongside the form
  view, edit a satellite's parameters in the form, and watch the JSON view update to match — never
  the two views disagreeing.*
- *As White Cell, I declare "Blue has 2 seats, Red has 1 seat," then check boxes in a matrix to
  assign bus/payload roles per seat per asset, before the exercise can start.*
- *As White Cell, I select an existing asset in the asset menu, reassign its owning cell, or delete
  it entirely, and see the 2D/3D preview update to match.*

## 5. Functional Requirements

This document creates no `FR-xxxx` (that is `04-requirements-engineering`'s job against `FEAT-5100`'s
eventual FS) — it states the capability-level requirements a future baseline pass should formalize,
each traceable to a citation:

- The system shall let White Cell compose a vignette's initial force (satellites, ground
  infrastructure) via TLE paste and lat/long entry, each requiring asset-type, cell-assignment, and
  name fields — grounded in [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md)
  (TLE plausibility by regime) and [R107](../research/encyclopedia/R107-ground-segment-operations.md)
  (siting methodology).
- The system shall preview the vignette's initial state in 2D and 3D before the exercise starts,
  reusing the existing render-from-custody pipeline in ground-truth mode.
- The system shall expose a synchronized raw-JSON view of the vignette alongside its form-based UI.
- The system shall let White Cell edit, reassign, or delete any already-added asset via a dedicated
  asset menu.
- The system shall let White Cell declare a seat count per cell and assign bus/payload/both roles
  to those seats against assets via a matrix UI (`BL-0051`), reusing `FS-115`/`IP-1151`'s existing
  `assign_role` mechanism underneath.
- The system shall serialize the completed draft into a valid `Vignette` YAML file on an explicit
  save action — no partial/incomplete file is ever written from an in-progress session (carried
  forward verbatim from `FEAT-5100`'s own catalog entry).

## 6. Non-functional Requirements

- **Determinism (`CLAUDE.md` invariant 1):** the draft session never calls `start()`, never
  advances its clock, and schedules no events — it cannot produce a non-deterministic event log
  because it never produces an event log at all. This is a hard architectural constraint, not an
  incidental property: any implementation that lets the draft session's clock advance (even to
  preview a "what happens next" state) would need its own separate determinism analysis this
  document does not clear.
- **Fog-of-war (`CLAUDE.md` invariant 3):** does not apply to this cluster — the draft session has
  exactly one viewer (White Cell), and White Cell already sees ground truth everywhere else in
  this system. The 2D/3D preview's ground-truth mode is consistent with, not an exception to,
  `ADR-0004`'s fog-of-war-at-the-boundary pattern (the boundary simply has nothing to filter for a
  single-viewer, no-other-cell-present authoring surface).
- **Plan-first / six access channels (invariant 4):** does not apply — the draft session issues no
  orders and has no access windows to compute; it is pure world-state construction. Flagged
  explicitly so a future implementer doesn't over-engineer window/access modeling into authoring
  time.
- **Content-as-data (invariant 6):** the Creator must read/write the existing `Vignette` schema via
  YAML, never introduce a second, parallel authoring format.

## 7. Constraints

- Must not add a UI or transport concept to `engine/` (invariant 2) — the draft-session mechanism
  lives entirely in `session/`, consuming `engine/` exactly the way `SessionManager` already does
  for a live session.
- Must produce a `Vignette` YAML file via the existing schema on save — no new file format.
- Must not require the exercise to be running — this document's entire scope is authoring-time-only,
  per the project owner's explicit phasing (a later, separately-scoped phase reuses a similar menu
  alongside the existing White-Cell inject mechanism for mid-exercise edits; out of scope here,
  see Open Questions).
- The JSON view and form view must read/write one shared draft-session state — never two
  independently-maintained representations (see Risks).

## 8. Risks

- **Two data paths for one draft is the single most likely implementation defect.** If the JSON
  view and the form-based UI are built against independent client-side state rather than both
  reading/writing the same draft-session server state on every change, they will drift — a
  half-finished form edit and a stale JSON view disagreeing is worse than not offering a JSON view
  at all. Mitigated architecturally (§2) by making both views thin clients over one server-side
  draft session, not by testing convergence after the fact.
- **Abandoned draft sessions have no stated lifecycle.** `CR-11`'s resolution (server-side draft
  state) trades browser-refresh data loss for a different risk: what happens to a draft session if
  White Cell's browser tab closes mid-authoring and never returns? Left as an Open Question (§9) —
  a future FS must pick a policy (indefinite retention, a TTL, or an explicit "resume draft" list),
  not silently accumulate abandoned sessions or silently discard active work.
- **The reverse-serialization function (`vignette_from_world`) does not yet exist and is nontrivial.**
  `build_world()` is a one-way, lossy-in-the-other-direction transform (a `Vignette`'s declarative
  fields become a fully-populated `WorldState`); writing its inverse correctly (recovering the
  *declarative* shape from a populated world, not just dumping every runtime-computed field) is
  real design/implementation work this document flags but does not solve.

## 9. Open Questions

1. **Exact JSON-view read/write semantics** — fully bidirectional live-editable JSON, or a
   read-only JSON view paired with form-only editing? Left to the eventual Feature Specification;
   both satisfy this document's "one shared source of truth" constraint, but they are different
   scopes of UI work.
2. **Abandoned-draft-session lifecycle policy** — indefinite retention, a TTL, or an explicit
   resume-list — per Risks above. Needs a product decision, not an architectural one; route to
   `06-feature-specification` or ask the project owner directly when that spec is drafted.
3. **Exact seat/role matrix UI layout** (checkbox grid dimensions, whether "both" is a third
   checkbox or a toggle spanning bus+payload) — a UI-design-level decision below this synthesis's
   altitude; the eventual FS should specify it concretely.
4. **Whether "Save as Vignette" can also directly become session-zero** (start the exercise
   immediately from the draft, skipping the file round-trip) or must always produce a file first —
   not decided here; either satisfies this document's architecture, but they imply different FS
   scope.
5. **The mid-exercise reuse phase's own architecture** (reusing this UI surface alongside the
   inject mechanism) is explicitly out of this document's scope per the project owner's phasing —
   noted here as a forward pointer, not resolved.

## 10. Decision Log

| # | Decision | Rationale | Alternatives considered |
|---|---|---|---|
| 1 | Draft-authoring state lives in a **server-side draft session** — an unstarted `SessionManager` instance — resolving `CR-11`. | Reuses existing engine/session machinery (TLE validation, asset mutation, `assign_role`) rather than duplicating it client-side; enables the 2D/3D preview to reuse the existing render pipeline directly. | Browser-local draft state — rejected: would require re-implementing TLE/sgp4 validation and world-state construction client-side, duplicating logic the server already has, and gives up the ability to reuse the existing render-from-custody preview pipeline. |
| 2 | The 2D/3D preview reuses the **existing scene/globe/map pipeline in ground-truth mode**, not a bespoke visualization. | Consistent with the existing godview/no-fog-of-war precedent for White-Cell-only surfaces (`ADR-0004`); avoids building and maintaining a second rendering path. | A dedicated "authoring preview" renderer — rejected: pure duplication with no fog-of-war reason to diverge, since the draft session has exactly one possible viewer. |
| 3 | `BL-0051`'s seat-count/matrix UI is **folded into this same document**, not synthesized separately. | Both concerns are White-Cell setup-time UI over the same underlying seat/asset/role concepts (per run #38's own bundling triage decision) — designing them independently risks two competing conventions for the same workflow moment. | Separate `ADS-xxx` for `BL-0051` — rejected per the explicit triage decision already recorded in `docs/pipeline/backlog.md`. |
| 4 | The mid-exercise "reuse this menu alongside inject" phase is **explicitly deferred**, stated but not designed here. | Matches the project owner's own explicit phasing instruction; keeps this document's scope to what v1 actually needs, avoiding speculative design for an unscoped future phase. | Designing both phases together now — rejected: the project owner explicitly separated them, and the inject mechanism's own extension point isn't yet characterized against this feature's needs. |

---

**Next step:** this document and its sibling [ADS-5100B](ADS-5100B-typed-parameters-and-per-cell-roe.md)
together ground the Vignette Creator Feature Specification `06-feature-specification` should author
next, consolidating `FEAT-5100`'s catalog entry and folding in `BL-0051`. Five Open Questions above
are non-blocking for that FS to begin, but should be resolved during its drafting, not silently
left open again.
