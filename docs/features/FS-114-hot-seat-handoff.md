# FS-114 — Hot-Seat Hand-Off Screen-Blank Menu

> **Document ID:** FS-114
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** (GDS-05 "Operational Rules" OR-3-grounded; no owning DOM), [ADR-0004](../architecture/adr/ADR-0004-fog-of-war-at-boundary.md), [FS-109](FS-109-multiplayer-session-transport.md)
> **Referenced By:** [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md) `FEAT-6600`, [docs/feature-planning/05-feature-review.md](../feature-planning/05-feature-review.md) Finding F-02, [IP-1140](../implementation/packages/IP-1140-hot-seat-handoff.md)
> **Produces:** the screen-blank/seat-reselection menu shown during a pending hot-seat hand-off
> **Feature Mapping:** FS-114 (this document)
> **Related Topics:** [FS-109](FS-109-multiplayer-session-transport.md) (the one-Session-object hot-seat/LAN sharing mechanism this hand-off menu sits on top of)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. It is a **new**
Feature Specification closing Finding F-02 in `docs/feature-planning/05-feature-review.md`: this
capability had a real, Must-priority baselined FR (FR-6610, added specifically to close GDS-05's
own prior Open Question 1) but zero presence in any of the 11 pre-existing `FS-xxx` documents. No
`docs/domains/` document names hot-seat hand-off as its own domain concept — grounded directly in
GDS-05's Operational Rules instead, mirroring FS-102's "no owning DOM" precedent.*

## Feature ID

FS-114

## Title

Hot-Seat Hand-Off Screen-Blank Menu

## Purpose

Blank a departing operator's sensitive belief-state content during a pending hot-seat role change,
and present a seat-selection menu until a new seat is chosen, so the next person at the keyboard
never sees the previous occupant's cell data — per `docs/feature-planning/03-feature-catalog.md`
`FEAT-6600`'s own Purpose field. This closes GDS-05's own previously-open Open Question 1 (OQ1),
which recorded that no FR leaf covered hand-off blanking before FR-6610 was added.

## Scope

In scope: detecting a pending hot-seat role change (the current seat's occupancy has ended and a
new seat has not yet been selected), blanking the previously displayed cell's content, and
presenting a seat-selection menu that persists until a new seat is explicitly chosen. Out of scope:
the one-Session-object mechanism that makes hot-seat and LAN modes share state
([FS-109](FS-109-multiplayer-session-transport.md), a dependency); the fog-of-war filter that
determines what a cell's content actually is (`FEAT-6200` in the Feature Catalog, not yet its own
Feature Specification).

## Requirements Implemented

FR-6610 (screen-blank pending-handoff menu between hot-seat role changes) — per
`docs/feature-planning/03-feature-catalog.md` `FEAT-6600`'s `Included Requirements`.

## User Workflows

- An operator relinquishes their seat (ends their occupancy of a role) on a shared hot-seat
  browser.
- The browser immediately blanks that cell's previously displayed content and shows a
  seat-selection menu.
- The next operator selects a seat (role) from the menu; only then does the browser render that
  newly selected cell's content.

## System Behaviour

- **A pending hand-off blanks all previously displayed sensitive content** (FR-6610): once a
  seat-relinquish action triggers a pending role change, no field of the departed cell's content
  remains visible.
- **The seat-selection menu persists until a seat is explicitly selected** (FR-6610): there is no
  time-out or default selection that would render a cell's content without an explicit choice.
- **No previously displayed cell's content reappears before a new seat is selected** (FR-6610),
  even transiently — this is stated as a hard postcondition, not a best-effort behavior.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `ui_web/static/` (client) | Detects the pending-hand-off trigger, blanks the DOM/rendered state of the previously displayed cell's content, and renders the seat-selection menu until a new seat is chosen. |
| `session/inprocess.py` / `session/manager.py` (per FS-109) | Provides the underlying seat/role-occupancy state this Feature's trigger condition (a seat relinquished, none yet selected) reads from. |

## Interfaces Used

INT-0001 (Browser ↔ Operator Console) — the client-side rendering behavior (blank + menu) occurs
over this interface. INT-0006 (Operator Console → Session Layer, the `SessionAPI` seam) — the
seat-relinquish/seat-select actions that trigger and resolve the pending hand-off route through
this seam.

## Data Model Changes

None beyond the existing seat/role-occupancy state (per `docs/architecture/04-domain-model.md`'s
Role Assignment / seat concept) transitioning through a "pending hand-off" state — the requirements
baseline does not name this as a new formal entity, and this document does not invent one (see Open
Questions).

## State Changes

- A seat-relinquish action transitions that browser's session view into a "pending hand-off" state:
  no cell's content is displayed, only the seat-selection menu.
- A subsequent seat-selection action transitions out of "pending hand-off" into that newly selected
  cell's normal displayed view.

## Error Handling

The requirements baseline does not specify behavior if the seat-selection menu itself fails to load
or if a selection request is invalid (e.g., a role already occupied elsewhere) — flagged as an Open
Question; this Feature's own Acceptance Criteria are silent on that failure path.

## Performance Considerations

None beyond the immediacy implied by "no previously displayed cell's sensitive content remains
visible once the hand-off menu is shown" (FR-6610) — the blank must be effectively instantaneous
relative to the relinquish action, though no numeric latency target is stated in any source
document (consistent with the same qualitative-only pattern NFR-1100/NFR-1200 show elsewhere in the
baseline).

## Security Considerations

- **This is the one place in the whole system where a fog-of-war boundary is enforced by client-side
  screen content rather than server-side filtering** — every other cell-scoped boundary (FEAT-6200)
  is enforced at the `SessionAPI`/`CellController` seam; this Feature's blank-screen behavior is a
  UI-side control, not a server-side data-withholding one, because the departing operator's browser
  has already received that cell's data before the hand-off trigger fires. This is an explicit,
  narrow exception to the project's own "fog-of-war at the boundary, not the UI" invariant
  (`CLAUDE.md` invariant 3) — worth flagging prominently rather than leaving implicit, since it is
  the one Feature in the catalog where that invariant's usual mechanism does not apply.

## Acceptance Criteria

- Given a hot-seat hand-off from Red to Blue on the same browser, no Red-cell data remains on
  screen once the hand-off menu is shown.
- No previously displayed cell's content reappears at any point before a new seat is explicitly
  selected.

## Verification Plan

Demonstration for both Acceptance Criteria above, consistent with FR-6610's own stated Verification
Method ("Demonstration") in `docs/requirements/01-functional-requirements.md` — a UI behavior best
confirmed by direct observation rather than an automated assertion against DOM state, per that
document's own choice.

## Dependencies

[FS-109](FS-109-multiplayer-session-transport.md) (Multiplayer / LAN Session Transport) — this
Feature's hand-off trigger condition depends on FS-109's one-Session-object hot-seat/LAN sharing
mechanism (`FEAT-6400`) existing first, per the Feature Catalog's own dependency edge
(`FEAT-6600 → FEAT-6400`).

## Risks

- **This Feature's build status is unconfirmed** — as with FS-112/FS-113, no prior FS document
  described hot-seat hand-off, and the RTM's Impl. Package citation for FR-6610 is `UNASSIGNED`.
  This specification is written directly from the requirements baseline and Feature Catalog entry.
- **This Feature sits at the deepest point of the Feature Catalog's dependency graph**
  (`docs/feature-planning/04-feature-dependency-graph.md`'s critical path: Event Log → Clock/
  Determinism → Multiplayer Clock/Locking → Hot-Seat/LAN Sharing → Hot-Seat Hand-Off) — if it turns
  out to be unbuilt, it is schedule-determining for nothing else in the catalog, but its own
  correctness depends on every Feature upstream of it being correct first.
- The client-side (not server-side) enforcement mechanism (see Security Considerations) means a
  defect here is a direct fog-of-war leak with no server-side backstop — this is the single highest
  consequence-per-line-of-code Feature in the catalog for exactly that reason.

## Open Questions

- **Build status is unverified** — confirm against `ui_web/static/app.js` directly (see Risks); if
  unbuilt, this specification is ready to hand to an Implementation Package, and should likely be
  prioritized given the consequence profile noted in Security Considerations.
- Behavior on a failed/invalid seat-selection attempt during the pending-hand-off state is not
  specified in the requirements baseline.
- Whether "pending hand-off" should be a named, first-class Domain Model state (as opposed to an
  implicit UI-only state) is worth raising with the architecture owner — this document does not
  introduce one (see Data Model Changes).

## Related ADRs

ADR-0004 (fog-of-war at the boundary) —
`docs/architecture/adr/ADR-0004-fog-of-war-at-boundary.md` (cited here specifically for the
Security Considerations exception this Feature represents, not because this Feature implements
ADR-0004's usual server-side mechanism).

## Related Interfaces

INT-0001, INT-0006 — per `docs/design/05-interface-control-document.md` (both are also this
document's Interfaces Used).
