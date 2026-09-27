> **Document ID:** FS-125
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined requirement
> itself — `docs/requirements/01-functional-requirements.md` `FR-1320` — plus the real baseline
> code it extends (`engine/orders.py`, `engine/eventlog.py`, `engine/entities.py`).
> **Dependencies:** None (additive presentation/export layer over existing `FR-1310`/`FR-7110`
> state)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0072` (item B6),
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-1320`, `docs/FUTURE-WORK.md` "Δv panel" item
> **Produces:** a per-asset, purpose-tagged manoeuvre ledger view and CSV export, satisfying
> `FR-1320` in full
> **Feature Mapping:** FS-125 (this document)
> **Related Topics:** [FS-101](FS-101-mission-planning.md) (Mission Planning — the plan-first order
> authoring surface a purpose tag is entered through, per `FR-3110`)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-125 — Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export

## Purpose

Give an operator or facilitator a per-asset, chronological record of every manoeuvre applied
against an Asset — with an operator-entered purpose tag — viewable in the console and exportable as
CSV, closing the gap `docs/FUTURE-WORK.md`'s "Δv panel" item and `FR-1320`'s own Rationale both
name: every manoeuvre is already deducted from `delta_v_ms` and logged in the `EventLog`, but
neither is presented as a reviewable, purpose-tagged ledger.

## Scope

**In scope:** recording a purpose tag alongside each manoeuvre order at issue time; presenting a
per-asset ledger view (time, delta-v cost, purpose tag, remaining budget); exporting the same rows
as CSV.

**Out of scope (named, not silently absorbed):** any change to `FR-1310`'s own delta-v
budget-enforcement rule; any change to how a manoeuvre order is planned/validated/executed beyond
adding the purpose-tag field to its existing payload.

## Requirements Implemented

- `FR-1320` — Per-asset manoeuvre ledger with purpose tags and export.

## User Workflows

1. **An operator issues a manoeuvre order.** The existing plan-first order-issuance surface
   (`FR-3110`) gains one additional field: an operator-entered purpose tag (free-text or a declared
   short label), supplied at the same time as the manoeuvre's own parameters — not a separate
   action.
2. **An operator or facilitator opens an Asset's manoeuvre ledger.** The console shows every
   manoeuvre recorded against that Asset, in chronological order, with time, delta-v cost, the
   purpose tag, and the resulting remaining delta-v budget.
3. **An operator or facilitator exports the ledger.** The same rows are available as a CSV download/
   copy for a requested Asset.

## System Behaviour

- **Normal path.** The ledger view and its CSV export are both derived, read-only projections of the
  existing `EventLog` history for the requested Asset's manoeuvre events — never a separate,
  independently-mutable state that could drift from it (`FR-1320`'s own Postconditions).
- **Edge case — no purpose tag supplied.** Not addressed by `FR-1320`'s own text (Open Question 1) —
  whether the tag is mandatory or may be blank is not stated.
- **Edge case — Asset with zero recorded manoeuvres.** The ledger view and export both show zero
  rows, consistent with `FR-1320`'s Acceptance Criteria's "exactly N rows" framing at N=0.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `engine/orders.py` (`OrderSystem`) | Owns manoeuvre-order issuance (`FR-3110`); extended so the order's payload carries the operator-entered purpose tag alongside its existing manoeuvre parameters. |
| `engine/eventlog.py` | Owns the `EventLog` this Feature's ledger is derived from — unchanged; the manoeuvre event's existing entry already carries time/delta-v cost/resulting budget, extended to also carry the purpose tag. |
| `session/manager.py` | Owns deriving the per-asset ledger view (a read, not a mutation) from the `EventLog`'s manoeuvre-event history for a requested Asset. |
| Operator Console (`ui_web/`) | Presents the ledger view and drives the CSV export request. |

## Interfaces Used

- `INT-0006` (Console → SessionAPI seam) — the existing interface the ledger-view/export request
  operates through.
- `INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the existing interface
  the purpose-tag-carrying order payload and the `EventLog` read both operate through.

## Data Model Changes

The manoeuvre order's existing payload (per `FR-3110`) gains an additive purpose-tag field; the
corresponding `EventLog` entry for a manoeuvre's execution carries the same tag through, alongside
its existing time/delta-v-cost/resulting-budget fields. No new top-level entity — the ledger itself
is a derived view, not a new persisted structure (`FR-1320`'s own Postconditions).

## State Changes

None beyond the additive purpose-tag field on the manoeuvre order/event — the ledger view/export
itself creates no new session state, being a pure derivation from the existing `EventLog`.

## Error Handling

None named beyond Open Question 1 (blank/missing purpose tag) — every other path is a
straightforward read-and-render of existing `EventLog` data.

## Performance Considerations

None named by `FR-1320` — deriving a per-asset ledger from the `EventLog` is a bounded, per-request
filter/read, not a new computational class.

## Security Considerations

`ADR-0004` (fog-of-war at the boundary): the ledger view/export must respect the same cell-scoping
the console already applies to any Asset-specific view — an operator sees/exports only their own
cell's Assets' ledgers, consistent with every other Asset-scoped surface (not a new rule this
Feature introduces, an existing one it must not bypass).

## Acceptance Criteria

1. Given an Asset with N recorded manoeuvres, the ledger view and its CSV export both list exactly N
   rows, each with the correct time/cost/tag/remaining-budget values matching the `EventLog`.
   *(`FR-1320`)*

## Verification Plan

- Criterion 1 — Test: an Asset with a known sequence of manoeuvres (including varying purpose tags);
  assert the ledger view and CSV export both reproduce the expected N rows and values.

## Dependencies

`FR-1310` (impulsive maneuver with delta-v budget enforcement) and `FR-7110` (event log) — both
pre-existing, unchanged by this Feature, which is purely a presentation/export layer over their
combined existing state.

## Risks

- **Ambiguity risk (Open Question 1 below).** Low — a narrow UI-input-validation question, not a
  behavioral gap.
- **Fog-of-war regression risk.** Because this is a new Asset-scoped console surface, an
  Implementation Package must confirm it reuses the console's existing cell-scoping mechanism rather
  than introducing a parallel one that could accidentally omit it.

## Open Questions

1. **Is the operator-entered purpose tag mandatory, or may a manoeuvre order be issued with a blank
   tag?** `FR-1320`'s own text states the tag is "supplied at order-issue time" but does not state
   whether the order-issuance surface must reject a blank tag or accept it silently. Needs a
   `07-implementation-planning` design decision — this document does not invent one.

## Related ADRs

None directly — a presentation/export layer over existing `FR-1310`/`FR-7110` state, not a new
resource-accounting or effect-resolution rule, per `FR-1320`'s own Related ADRs field.

## Related Interfaces

None beyond `INT-0006`/`INT-0008` already cited under Interfaces Used.
