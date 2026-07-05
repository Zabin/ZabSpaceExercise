> **Document ID:** FS-117
> **Version:** 1.1
> **Status:** ✅ Ready for implementation planning (Open Question 1 closed — see below)
> **Changelog (v1.1, 2026-07-05):** Closed Open Question 1. `04-requirements-engineering` (run #42)
> added nine new baselined requirement leaves — `FR-5120`, `FR-5130`, `FR-5140`, `FR-5150`,
> `FR-5160`, `FR-5170`, `FR-5180` (children of `FR-5100`), `FR-3420` (child of `FR-3400`), and
> `NFR-2010` (sibling of `NFR-2000`) — covering every capability this document's `ADS-5100A`/
> `ADS-5100B` grounding commits to. `Requirements Implemented`, `Produces`, `Risks`, and `Open
> Question 1` updated to cite them; no other field's substance changed.
> **Dependencies:** [FS-115](FS-115-session-setup.md) (`FR-4210` — the `assign_role`/
> `staffing_report` mechanism this Feature's seat/role matrix reuses, `VERIFIED`),
> [FS-105](FS-105-spacecraft-operations.md) (`BusState`/`PayloadState` this Feature's typed
> sub-schemas extend, `VERIFIED`), [FS-116](FS-116-role-scoped-command-catalog.md) v1.2 (role-scope
> classification this Feature's typed payload schemas must remain consistent with),
> [ADS-5100A](../architecture/ADS-5100A-vignette-creator-session-and-ui.md),
> [ADS-5100B](../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md)
> **Referenced By:** [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md)
> `FEAT-5100` (this Feature consolidates/supersedes that catalog entry's FS, per the project
> owner's explicit "document as its own distinct feature" instruction),
> [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0051`/`BL-0052` (both fully absorbed
> here, `DONE`), `BL-0055` (the requirements-baseline gap this document's v1.0 Open Question 1
> named — closed by v1.1)
> **Produces:** an in-app Vignette Creator satisfying `FR-5110`/`NFR-2000`, `FR-5120`-`FR-5180`,
> `FR-3420`, and `NFR-2010` in full — every capability the two `ADS-5100` documents commit to now
> has an owning requirement
> **Feature Mapping:** FS-117 (this document)
> **Related Topics:** [FS-113](FS-113-observer-read-only-access.md) (a structurally similar
> White-Cell-only, ground-truth-visibility precedent this Feature's 2D/3D preview follows)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. It consolidates
`FEAT-5100` (In-App Iterative Vignette Builder, `EP-5000`) — 0% built, no prior FS, no code — into
one distinct Feature Specification, per the project owner's explicit instruction that the Vignette
Creator is a large, separate feature and must be documented as such rather than blended into
another Feature's spec. It also fully absorbs `docs/pipeline/backlog.md` `BL-0051` (seat-count
declaration + role-assignment matrix UI) and `BL-0052` (the Vignette Creator itself) — neither is
tracked as a separate line item once this document exists. Grounded in the two per-cluster design
syntheses [`ADS-5100A`](../architecture/ADS-5100A-vignette-creator-session-and-ui.md) (authoring-
session architecture + UI surfaces) and [`ADS-5100B`](../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md)
(typed parameter sub-schemas + per-cell ROE), both authored this same day.*

## Feature ID

FS-117

## Title

Vignette Creator — In-App Authoring, Typed Parameters & Per-Cell ROE

## Purpose

Let White Cell compose a vignette (force lay-down, parameters, injects, intro briefs) iteratively,
in-app, across multiple round trips before a single save/build action emits a complete vignette
file — per `FEAT-5100`'s own catalog `Purpose`, carried forward verbatim — so that YAML hand-editing
stops being the only *actually used* authoring path (the strategic review's own "White-Cell-hostile
in practice" finding, `docs/feature-planning/02-epic-catalog.md` `EP-5000` Risk).

## Scope

**In scope, v1 (authoring-time only — no exercise running):**
- Iterative, in-app vignette composition backed by a server-side draft session
  ([ADS-5100A](../architecture/ADS-5100A-vignette-creator-session-and-ui.md) §2), resolving `CR-11`.
- A synchronized JSON view alongside the form-based UI.
- A 2D/3D initial-state preview reusing the existing render-from-custody pipeline in ground-truth mode.
- Asset entry via manual TLE paste and lat/long entry (ground infrastructure), each with
  asset-type/cell-assignment/name-entry fields; lat/long entry defaults to
  `docs/vignettes/GROUND-INFRASTRUCTURE.md`'s curated site list before free-entry coordinates.
- An asset menu: edit, reassign, delete any already-added asset.
- A seat-count-declaration step per cell followed by a seat/role assignment matrix UI (`BL-0051`),
  reusing `FS-115`/`IP-1151`'s existing `assign_role` mechanism underneath.
- Typed per-payload-type parameter sub-schemas (one per `satcom`/`isr_eo`/`isr_sar`/`sigint`/`sda`/
  `weather`/`pnt`/`mw`) and typed bus parameter sub-schemas (power, propulsion), per
  [ADS-5100B](../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md) §3.1.
- Real per-cell Rules of Engagement enforcement, replacing today's single global gate, per
  [ADS-5100B](../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md) §3.2.

**Out of scope, v1** (per the project owner's explicit phasing and design-fork decisions):
- Space-Track.org network TLE import — `FEAT-5200`'s own separate concern; this Feature's TLE entry
  is manual-paste-only.
- Load-time validation of the resulting vignette file — `FEAT-5300`'s own concern; this Feature's
  save action must produce a file that passes `FEAT-5300`'s validation unchanged, not duplicate it.
- **Reusing this same (or a similar) menu surface alongside the existing White-Cell inject
  mechanism for mid-exercise parameter edits and asset add/remove** — explicitly a later, separately
  scoped phase per the project owner's own instruction; stated here as a forward pointer only.

## Requirements Implemented

**`FR-5110`** (iterative in-app vignette composition — accumulate partial state across an
authoring session, emit a complete file only on explicit save/build) and **`NFR-2000`** (content as
data, not code) are the two requirements `FEAT-5100`'s Feature Catalog entry actually lists as
`Included Requirements`, and both are implemented by this Feature as scoped above.

**As of `04-requirements-engineering`'s run #42 pass (see
[`docs/reviews/requirements-update-fs117.md`](../reviews/requirements-update-fs117.md)), nine
additional baselined requirements cover the rest of this Feature's scope:**

| ID | Covers |
|---|---|
| `FR-5120` | Synchronized JSON view alongside the form UI |
| `FR-5130` | 2D/3D initial-state preview |
| `FR-5140` | TLE and lat/long asset entry |
| `FR-5150` | Asset menu (edit, reassign, delete) |
| `FR-5160` | Seat-count declaration and seat/role-assignment matrix (`BL-0051`) |
| `FR-5170` | Typed per-payload-type parameter sub-schemas |
| `FR-5180` | Typed bus parameter sub-schemas (power, propulsion) |
| `FR-3420` | Per-cell independent Rules of Engagement |
| `NFR-2010` | Additive vignette-schema evolution (all 19 shipped vignettes keep working unchanged) |

Every capability this Feature Specification describes now traces to a baselined `FR-xxxx`/
`NFR-xxxx` — Open Question 1's requirements-baseline gap is closed.

## User Workflows

- *White Cell opens a blank Vignette Creator, adds three Blue satellites by pasting TLEs and two
  Red ground stations by lat/long entry (selecting from the curated site list), names and assigns
  each to a cell, watches them appear on the 2D map and 3D globe immediately, and saves the result
  as a new vignette file.*
- *White Cell opens an existing vignette in the Creator, views its raw JSON alongside the form
  view, edits a satellite's typed bus/payload parameters in the form, and the JSON view updates to
  match.*
- *White Cell declares "Blue has 2 seats, Red has 1 seat," then checks boxes in a matrix to assign
  bus/payload roles per seat per asset, before the exercise can start.*
- *White Cell selects an existing asset in the asset menu, reassigns its owning cell, or deletes it
  entirely, and the 2D/3D preview updates to match.*
- *White Cell sets Blue's kinetic ROE to "not authorized" and Red's to "authorized"; during the
  later exercise, a Blue kinetic order is rejected while an otherwise-identical Red order succeeds.*

## System Behaviour

- **Draft session lifecycle (`FR-5110`):** opening the Creator instantiates a server-side draft
  session (an unstarted `SessionManager` instance, per `ADS-5100A` §2) — no clock advance, no
  scheduler activity. Every UI mutation (asset add/edit/reassign/delete, ground-site add, parameter
  edit, seat/role assignment, ROE selection) is applied to this draft session directly. "Save as
  Vignette" serializes the draft session's current world-state into a `Vignette` YAML file via a
  new reverse-serialization function (`ADS-5100A` §2) and — per `NFR-2000`'s postcondition — no
  partial or incomplete file is ever written before that explicit action.
- **JSON view:** reads and writes the *same* draft-session state the form UI does — an edit in
  either view is immediately reflected in the other, never two independently-maintained
  representations (`ADS-5100A` Risk 1).
- **2D/3D preview:** reuses the existing render-from-custody scene/globe/map pipeline against the
  draft session's current state, in ground-truth mode (no `CellController` fog-of-war filtering) —
  consistent with the existing precedent that White-Cell-only surfaces already show ground truth
  (`ADR-0004`).
- **TLE entry:** a manually pasted TLE is validated the same way the existing `POST
  /api/sessions/{sid}/force/tle` endpoint validates one (`sgp4`) and additionally checked for
  regime plausibility (warn, not block, per `R101`'s plausible-element-range table) — paired with
  required asset-type, cell-assignment, and name-entry fields.
- **Lat/long entry:** offers `docs/vignettes/GROUND-INFRASTRUCTURE.md`'s curated site list as the
  default path, with free-entry coordinates as the fallback, paired with the same asset-type/cell/
  name fields as TLE entry.
- **Asset menu:** edit/reassign/delete operate directly on the draft session's current asset list;
  the 2D/3D preview and JSON view both reflect the change immediately.
- **Seat/role matrix (`BL-0051`):** White Cell first declares a seat count per cell (generating seat
  identifiers), then uses a checkbox-grid UI (seats × assets, bus/payload/both) that calls the same
  `assign_role(seat, asset_or_constellation, role)` mechanism `FS-115`/`IP-1151` already ships —
  this Feature adds the seat-count-declaration step and the matrix presentation, not a new
  assignment mechanism.
- **Typed payload/bus parameters:** the Creator's parameter forms present named, validated fields
  per payload type and per relevant bus subsystem (power, propulsion), grounded in
  `R109`/`R110`/`R111`/`R112`/`R134`/`R137`. The typed power sub-schema exposes
  `charge_rate_per_s`/`drain_rate_per_s` (already-live fields), **not** `AssetResources.power_w`
  (a confirmed dead field, `R111`); the typed propulsion sub-schema exposes
  `AssetResources.delta_v_ms`. `weather`/`mw` payload sub-schemas are presented in the UI but are
  **not fully wired to engine behavior until `BL-0053`** (`engine/isr.py`'s `BEAM_MODES` gains
  entries for both types) — see Risks.
- **Per-cell ROE:** the Creator presents independent kinetic/cyber ROE selectors per cell; a
  vignette declaring only the legacy global `Parameter` pair (`red_kinetic_authorized`/
  `cyber_authorized`, all 19 shipped vignettes) resolves to both cells sharing the same values —
  behavior identical to today. A vignette explicitly declaring per-cell values gates each cell's
  orders independently, checked in `engine/orders.py` against `order.cell` rather than a single
  global dict.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| **C2 Session / Application Layer** | Owns the draft-session lifecycle, the reverse-serialization ("Save as Vignette") function, seat/role assignment (reusing `FS-115`'s existing mechanism), and per-cell ROE resolution at order-issue time. |
| **C4 Operator Console** | Owns every Creator UI surface: JSON view, 2D/3D preview, TLE/lat-long/asset-entry forms, asset menu, seat/role matrix, typed parameter forms — all as thin clients over the C2 draft session, per `ADS-5100A` §2. |
| **C6 White Cell** | The sole actor exercising this Feature — no Blue/Red operator interaction, consistent with `INT-0003`'s existing scope. |
| **C5 Content & Data** | Owns the `Vignette`/`RoleRequirement`/`Parameter`/`Inject` schema this Feature reads and writes unchanged (content-as-data, `NFR-2000`) — this Feature is a new *authoring surface* over that schema, not a new schema. |
| **C1 Simulation Engine** | Owns `PayloadState`/`BusState`'s typed field additions (mechanism per `ADS-5100B` Open Question 1) and `engine/orders.py`'s per-cell ROE check — reads a richer data shape, gains no new "UI" or "cell-authoring" concept (invariant 2 unaffected). |

## Interfaces Used

- **INT-0003** (White Cell Facilitator ↔ Operator Console, "in-app scenario builder") — the exact,
  already-named interface this Feature implements; its own ICD text ("A distinct, multi-step,
  stateful authoring interaction... composing a vignette... before a single save/build action emits
  the vignette file") already describes this Feature precisely.
- **INT-0011** (Session Layer → Content & Data, vignette/template load) — this Feature's "Save as
  Vignette" output is the file `INT-0011` subsequently loads; this Feature does not change
  `INT-0011` itself.
- **INT-0002** (White Cell Facilitator ↔ Operator Console, exercise control) — the same interface
  `FS-115`'s existing seat-assignment step uses; this Feature's seat/role matrix is a richer
  presentation over the same underlying calls, not a new interface.

**Not used, explicitly:** `INT-0013` (Content & Data → Space-Track.org) — this Feature's TLE entry
is manual-only; Space-Track network import remains `FEAT-5200`'s own, unused-here interface.

## Data Model Changes

- **Draft Vignette Session** — a session-layer lifecycle concept (an unstarted `SessionManager`
  instance), not a new persisted Domain Model entity.
- **Typed payload/bus parameter sub-schemas** — extend `PayloadState`/`BusState`'s Domain Model per
  `ADS-5100B` §3.1; the exact bridging mechanism to the engine's existing runtime representation is
  **Open Question 4** below (carried forward from `ADS-5100B`'s own Open Question 1).
- **Per-cell ROE structure** — extends `VignetteContext.roe`/the `Vignette` schema's ROE
  construction from a flat dict to a cell-keyed one; the exact YAML shape is **Open Question 5**
  below (carried forward from `ADS-5100B`'s own Open Question 3).
- **Seat-count declaration** — a small addition to the existing seat/role-assignment state (`FS-115`),
  a list of generated seat identifiers per cell; no change to the existing `role_assignments` mapping
  shape itself.

## State Changes

- **Draft session creation:** triggered by White Cell opening the Creator.
- **Draft session discard/persistence:** triggered by an explicit "Save as Vignette" action
  (produces a file) or explicit discard. **What happens to an abandoned draft session (browser tab
  closed, no save/discard action taken) is Open Question 2** (carried forward from `ADS-5100A`'s
  own Open Question 2) — not decided by this document.
- **Seat-count declaration:** a new, small piece of setup state per cell, created once per
  authoring session and consumed by the seat/role matrix.
- **Per-cell ROE:** read at order-issue time from the loaded vignette's (possibly per-cell)
  declaration; no new persistent session state beyond what the existing `VignetteContext.roe`
  already is.

## Error Handling

- A manually entered TLE that fails `sgp4` validation is rejected with the same reason the existing
  `force/tle` endpoint already produces; one that parses but is regime-implausible (per `R101`'s
  table) is flagged with a warning, not blocked — an author may deliberately want an implausible
  asset.
- An attempt to save a vignette with an unmet mandatory `roles_needed` entry is **not** this
  Feature's own gate — that remains `FS-115`'s existing `staffing_report`/start-time check,
  unaffected by this Feature.
- A command order whose issuing cell's ROE is not authorized is rejected with a role-scope-distinct,
  ROE-specific reason (existing `roe_kinetic_not_authorized`/`roe_cyber_not_authorized` reasons,
  now resolved per-cell rather than globally) — this Feature does not change the reason strings
  themselves, only which cell's flags are consulted.
- A `weather`/`mw` typed payload parameter set by an author before `BL-0053` ships has **no
  observable engine effect** — this is a known, flagged limitation (Risks), not a silent defect to
  be discovered later; the Creator's UI should surface this limitation rather than implying the
  parameter is already live.

## Performance Considerations

- **Determinism (`CLAUDE.md` invariant 1):** the draft session never calls `start()` and never
  advances its clock — it produces no event log, so it cannot introduce non-determinism. Any
  implementation that lets the draft session's clock advance for any reason would need a separate
  determinism analysis this document does not clear.
- **Content-as-data (`NFR-2000`):** the Creator reads/writes the existing `Vignette` YAML schema;
  it introduces no second, parallel authoring format.

## Security Considerations

- **Trust boundary consistency:** the Creator is reachable only by White Cell, at the same
  client-side-trust level every other White-Cell-only surface in this system already operates at
  (`CLAUDE.md` "LAN trust model") — this Feature introduces no new authentication mechanism and
  does not strengthen or weaken the existing v1 LAN trust boundary.
- **Ground-truth preview is consistent with existing precedent, not a new exception.** The 2D/3D
  preview's lack of fog-of-war filtering mirrors the existing godview/no-cell-binding endpoints
  (`/godview`, `/eventlog`) already documented as ground-truth-by-design for White Cell (`ADR-0004`).

## Acceptance Criteria

1. Given an authoring session with several incremental inputs but no final save/build action, no
   vignette file is written to disk (`FR-5110`'s own literal Acceptance Criterion).
2. Given a manually pasted, `sgp4`-valid TLE with asset-type/cell/name fields, the asset appears in
   the draft session's asset list, the 2D/3D preview, and the JSON view simultaneously.
3. Given a lat/long entry for ground infrastructure, the same three-way (asset list/preview/JSON)
   consistency holds, and the curated site list is offered before free-entry coordinates.
4. Given an edit made in the form UI, the JSON view reflects it without requiring a manual refresh,
   and vice versa.
5. Given a declared seat count per cell and a matrix assignment, the resulting `role_assignments`
   state is identical in shape to what `FS-115`'s existing `assign_role` API already produces.
6. Given a vignette with only the legacy global ROE `Parameter` pair, both cells' order-issuance
   behavior is unchanged from today.
7. Given a vignette with explicit per-cell ROE values that differ, a kinetic order from the
   not-authorized cell is rejected while an identical order from the authorized cell succeeds.
8. Given a typed bus power parameter set via the Creator, the resulting saved vignette's field maps
   to `charge_rate_per_s`/`drain_rate_per_s`, never `power_w`.
9. Given a saved vignette produced by this Feature, `FEAT-5300`'s existing load-time validation
   accepts it without modification to that validation logic.

## Verification Plan

Per `FR-5110`'s own `Verification Method` (`Test`): automated tests exercising Acceptance Criteria
1–9, plus a regression run of the full existing suite to confirm no existing vignette-loading or
ROE-check test's behavior changed. Consistent with this project's test-first mandate (`CLAUDE.md`
"Test-driven workflow") — the implementing package(s) must encode each Acceptance Criterion as a
failing test before implementation.

## Dependencies

[FS-115](FS-115-session-setup.md) (`FR-4210` — the `assign_role`/`staffing_report` mechanism
this Feature's seat/role matrix reuses; already `VERIFIED`), [FS-105](FS-105-spacecraft-operations.md)
(`BusState`/`PayloadState` — the fields this Feature's typed sub-schemas extend; already
`VERIFIED`), [FS-116](FS-116-role-scoped-command-catalog.md) v1.2 (the role-scope classification
of bus/payload/`DEFENSE_VERBS` verbs — this Feature's typed payload schemas operate on parameter
*values*, not verb classification, so should be unaffected, but any future package touching both
should confirm no interaction). `FEAT-5200` (TLE Import with Space-Track) and `FEAT-5300` (Load-Time
Vignette Validation) are named boundaries this Feature respects but does not depend on for its own
completion.

## Risks

- **The requirements-baseline gap Open Question 1 named is now closed** (v1.1) — `04-requirements-
  engineering` run #42 added `FR-5120`-`FR-5180`/`FR-3420`/`NFR-2010`. `07-implementation-planning`
  can now cite genuine traceability for every part of this Feature's scope. The one remaining,
  non-blocking gap `04`'s own review surfaced (Finding 9, `BL-0056`, Medium): `docs/architecture/
  05-functional-requirements.md` (GDS-05) has not yet folded these nine leaves in — an architecture-
  ladder reconciliation item, not a risk to this Feature's implementation-readiness.
- **Two data paths for one draft (JSON view vs. form UI) is the most likely implementation
  defect**, carried forward from `ADS-5100A`'s own Risk 1 — both must be thin clients over one
  shared draft-session state.
- **The typed-parameter-to-engine-runtime bridging mechanism is unresolved** (Open Question 4,
  from `ADS-5100B`) — a future package could underestimate this as "just add fields to a form" when
  it also requires deciding how the engine's existing dict-based mutation logic consumes the typed
  input.
- **Per-cell ROE touches already-`VERIFIED` `FS-101`/`FS-102` territory** — re-confirming their
  existing acceptance criteria still hold is part of this Feature's own verification burden, not
  optional.
- **`BL-0053` is a hard precondition for the `weather`/`mw` typed sub-schemas** — shipping those two
  sub-schemas' UI before `BL-0053`'s engine fix reproduces the exact "plausible but inert field"
  problem this document elsewhere warns against.
- **Abandoned draft sessions have no stated cleanup policy** (Open Question 2) — an implementation
  that doesn't address this could accumulate unbounded server-side session state over time.

## Open Questions

1. **CLOSED (v1.1).** `04-requirements-engineering` run #42 added `FR-5120`, `FR-5130`, `FR-5140`,
   `FR-5150`, `FR-5160`, `FR-5170`, `FR-5180`, `FR-3420`, and `NFR-2010` — every capability this
   document specifies (typed-parameter sub-schemas, per-cell ROE, and the JSON-view/2D-3D-preview/
   TLE-lat-long-entry/asset-menu/seat-role-matrix UI mechanics) now traces to a baselined
   requirement. See [`docs/reviews/requirements-update-fs117.md`](../reviews/requirements-update-fs117.md)
   for the full derivation and review. `07-implementation-planning` may now proceed against this
   Feature's full scope, not merely the `FR-5110`/`NFR-2000` slice.
2. **Abandoned-draft-session lifecycle policy** (from `ADS-5100A` Open Question 2) — indefinite
   retention, a TTL, or an explicit resume-list. A product decision, not resolved here.
3. **Exact seat/role matrix UI layout** (from `ADS-5100A` Open Question 3) — checkbox-grid
   dimensions, whether "both" is a third checkbox or a toggle spanning bus+payload.
4. **Exact typed-schema-to-engine-runtime bridging mechanism** (from `ADS-5100B` Open Question 1) —
   whether the engine's `PayloadState`/`BusState` gain new strongly-typed fields directly, or the
   Creator converts typed input to the existing `dict` shape at save time.
5. **Exact per-cell ROE YAML shape** (from `ADS-5100B` Open Question 3) — nested `{cell: {flag}}`
   dict vs. a flat `Parameter`-style list extending the existing convention.
6. **Whether `BL-0053`'s `BEAM_MODES` fix rides this Feature's own Implementation Package or ships
   as an earlier, separate prerequisite package** (from `ADS-5100B` Open Question 2) — a
   sequencing decision for `07-implementation-planning`.
7. **Whether a legacy-global-ROE vignette should be silently treated as "both cells share this
   value" forever, or auto-upgraded to an explicit per-cell block on next save** (from `ADS-5100B`
   Open Question 4).
8. **Whether "Save as Vignette" can also directly become session-zero** (start the exercise
   immediately from the draft) or must always produce a file first (from `ADS-5100A` Open Question 4).
9. **Exact JSON-view read/write semantics** — fully bidirectional live-editable JSON, or read-only
   JSON paired with form-only editing (from `ADS-5100A` Open Question 1).

## Related ADRs

ADR-0027 (scenario-authoring workflow's boundary actor/interface — `FEAT-5100`'s own cited ADR,
directly grounding this Feature's `INT-0003` usage), ADR-0007 (content-as-data, `NFR-2000`'s cited
ADR), ADR-0004 (fog-of-war-at-the-boundary pattern this Feature's ground-truth preview follows,
not an exception to).

## Related Interfaces

INT-0013 (Content & Data → Space-Track.org, `FEAT-5200`'s own interface — related but explicitly
unused by this Feature's manual-TLE-only scope).
