# FS-113 — Observer Read-Only Access

> **Document ID:** FS-113
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** (GDS-01 §2 / GDS-02 §2 row 5-grounded; no owning DOM), [ADR-0004](../architecture/adr/ADR-0004-fog-of-war-at-boundary.md)
> **Referenced By:** [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md) `FEAT-6500`, [docs/feature-planning/05-feature-review.md](../feature-planning/05-feature-review.md) Finding F-02
> **Produces:** the read-only Observer seat interaction model
> **Feature Mapping:** FS-113 (this document)
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (White Cell sets the Observer's view designation), fog-of-war filtering (`FEAT-6200` in the Feature Catalog — not yet its own Feature Specification)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. It is a **new**
Feature Specification closing Finding F-02 in `docs/feature-planning/05-feature-review.md`: this
capability had a real, Must-priority baselined FR (FR-6510) but zero presence in any of the 11
pre-existing `FS-xxx` documents. No `docs/domains/DOM-xxx` document names Observer as its own
domain concept — grounded directly in the ConOps/System-Context tier instead, mirroring FS-102's
"(R103-grounded; no owning DOM)" precedent for a capability with no clean domain home.*

## Feature ID

FS-113

## Title

Observer Read-Only Access

## Purpose

Give an Observer seat a White-Cell-designated read-only view (god-view or a specific cell's view)
with no ability to issue any command-kind or collection-kind action whatsoever — per
`docs/feature-planning/03-feature-catalog.md` `FEAT-6500`'s own Purpose field. Observers are
explicitly assessment/learning roles with no command authority (FR-6510's own Rationale, GDS-01 §2).

## Scope

In scope: White Cell's designation of an Observer seat's view (god-view or a named cell's
`CellView`), and the read-only enforcement that rejects any mutating request from that seat. Out
of scope: the fog-of-war filter itself that produces a cell's `CellView` (a dependency, specified
by a different, not-yet-authored Feature — `FEAT-6200` in the Feature Catalog); mid-exercise
reassignment of an Observer's view designation (CR-06, an unbaselined candidate requirement, not
part of this Feature).

## Requirements Implemented

FR-6510 (Observer read-only view with no command ability) — per `docs/feature-planning/03-feature-
catalog.md` `FEAT-6500`'s `Included Requirements`.

## User Workflows

- White Cell designates an Observer seat's view as either god-view or a specific cell's `CellView`.
- The Observer opens their session and sees exactly the designated view — nothing more, nothing
  less.
- The Observer attempts to submit any command-kind or collection-kind action; the request is
  rejected and no `WorldState` change occurs.

## System Behaviour

- **An Observer's view is exactly what White Cell designates** (FR-6510): either the god-view (per
  FS-106's own FR-4610 mechanism) or a specific cell's fog-of-war-filtered `CellView`.
- **No mutating request from an Observer-seated session is ever applied** (FR-6510): this is a
  structural rejection, not a UI-only restriction — a request bypassing the UI is rejected the same
  way a UI-originated one would be.
- **An Observer's read access, when viewing a specific cell, is bound by the same fog-of-war filter
  a human operator of that cell would experience** (ADR-0004) — an Observer assigned to view Blue
  sees exactly Blue's `CellView`, no more.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/api.py` (`SessionAPI`) / `session/cells.py` (`CellController`) | Serves the White-Cell-designated view (god-view or a named cell's `CellView`) to the Observer seat, reusing the existing fog-of-war filter for the cell-view case. |
| `ui_web/server.py` | Rejects any mutating request (order submission, sensor tasking, etc.) originating from an Observer-seated session, independent of whether the UI itself offers such an action. |

## Interfaces Used

INT-0005 (Observer ↔ Operator Console) — the Observer's own interaction surface. INT-0006
(Operator Console → Session Layer, the `SessionAPI` seam) — the path any attempted mutating request
would route through before being rejected.

## Data Model Changes

None beyond the existing Domain Model's seat/role concept accommodating an Observer view
designation (per `docs/architecture/02-system-context.md` §2 row 5's Observer actor entry) — no new
entity is introduced.

## State Changes

An Observer's view-designation assignment (god-view vs. a named cell) is set by White Cell and
persists for the Observer's seat occupancy; no other session state is created or transitioned by
this Feature.

## Error Handling

A mutating request from an Observer-seated session is rejected with no `WorldState` change — the
requirements baseline does not specify the exact rejection reason/error format returned to the
caller, flagged as an Open Question.

## Performance Considerations

None beyond what the underlying god-view (FS-106) or fog-of-war filter (`FEAT-6200`) already
provides — this Feature adds a read-only/reject-mutation rule on top, not a new rendering or
filtering cost.

## Security Considerations

- **This is a role-authorization boundary, not merely a UI convenience**: the rejection of mutating
  requests must hold even against a request that bypasses the UI entirely (consistent with how
  FR-3520's Role-Assignment scoping is enforced independent of UI filtering).
- Observer access to a cell's `CellView` is bound by the same LAN trust model (ADR-0015) as any
  other cell-scoped endpoint — client-side seat selection, no per-seat authentication in v1.

## Acceptance Criteria

- Given White Cell has designated an Observer's view as a specific cell, the Observer's session
  displays exactly that cell's `CellView` — no more, no less.
- Given an Observer-seated session attempting to submit any command-kind or collection-kind action,
  the request is rejected and no `WorldState` change occurs.

## Verification Plan

Test (automated) for both Acceptance Criteria above, consistent with FR-6510's own stated
Verification Method ("Test") in `docs/requirements/01-functional-requirements.md`.

## Dependencies

`FEAT-6200` (Fog-of-War Filtering at the Session Boundary) in the Feature Catalog — Observer access
to a specific cell's view reuses this filter; it is not yet its own Feature Specification. No
existing `FS-xxx` document is a prerequisite.

## Risks

- **This Feature's build status is unconfirmed** — as with FS-112, no prior FS document described
  Observer access, and the RTM's Impl. Package citation for FR-6510 is `UNASSIGNED`. This
  specification is written directly from the requirements baseline and Feature Catalog entry.
- CR-06 (mid-exercise Observer reassignment) is a related, unbaselined candidate — if authorized in
  the future, it would extend this Feature's State Changes (a view designation that can change
  mid-session rather than being fixed at seat assignment), not merely add a new Feature alongside
  it.

## Open Questions

- **Build status is unverified** — confirm against `ui_web/server.py`/`session/` directly (see
  Risks); if unbuilt, this specification is ready to hand to an Implementation Package.
- The exact rejection reason/error format for a mutating request from an Observer seat is not
  specified in the requirements baseline.
- **CR-06** (mid-exercise Observer reassignment) is a related, unbaselined candidate requirement —
  not part of this Feature's scope; noted for whoever next reviews the Candidate Requirements list.
- Whether Observer should have its own `docs/domains/` framework document (this Feature currently
  has no owning domain at all, unlike almost every other Feature in the catalog) is worth raising
  with whoever owns `docs/domains/` — not resolved here.

## Related ADRs

ADR-0004 (fog-of-war at the boundary) —
`docs/architecture/adr/ADR-0004-fog-of-war-at-boundary.md`.

## Related Interfaces

INT-0005, INT-0006 — per `docs/design/05-interface-control-document.md` (both are also this
document's Interfaces Used).
