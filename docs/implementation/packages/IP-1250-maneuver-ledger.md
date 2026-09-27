# IP-1250 — Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export

> **Package ID:** IP-1250
> **Version:** 1.0
> **Status:** 🟡 READY *(authorized 2026-09-27 by the project owner's direct instruction, MSTR-006 §3)*
> **Dependencies:** [FS-125](../../features/FS-125-maneuver-ledger.md) v1.0 (`FR-1320`),
> `engine/orders.py`/`engine/eventlog.py` (`VERIFIED` baseline code, `IP-1010`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0072` (item B6), `BL-0116` (this
> Feature's one Open Question)
> **Produces:** a per-asset, purpose-tagged manoeuvre ledger view and CSV export, satisfying
> `FR-1320` in full
> **Feature Reference:** [FS-125 — Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export](../../features/FS-125-maneuver-ledger.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/eventlog.py`](../../../spacesim/engine/eventlog.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package.*

## Package ID

IP-1250

## Title

Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export

## Objective

Add an operator-entered purpose tag to manoeuvre-order issuance, and a derived, read-only per-asset
ledger view (time, delta-v cost, purpose tag, remaining budget) plus CSV export, both reconstructed
from the existing `EventLog` history — no new persisted state.

> **This package is authorized for coding.** Per MSTR-006 §3, the project owner gave explicit
> go-ahead 2026-09-27 (batched with five sibling packages from the same Should-tier intake round).

## Feature Reference

[FS-125 — Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export](../../features/FS-125-maneuver-ledger.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-1320 | Per-asset manoeuvre ledger with purpose tags and export | A manoeuvre order's existing payload gains an additive purpose-tag field, carried through into its `EventLog` entry; a new derived read (`session/manager.py`) filters an Asset's manoeuvre-event history into a ledger view; a CSV export serializes the same rows. |

## Architecture Components

- **C1 Simulation Engine** (`engine/orders.py`, `engine/eventlog.py`) — `orders.py`'s manoeuvre-order
  payload gains the purpose-tag field; `eventlog.py`'s existing manoeuvre-event entry shape gains
  the same field, additive.
- **C2 Session/Application Layer** (`session/manager.py`) — owns deriving the per-asset ledger view
  from the `EventLog`, a pure read.
- **C4 Operator Console** (`ui_web/`) — presents the ledger view and drives the CSV export request.

## Interfaces

`INT-0006` (Console → SessionAPI seam) — the ledger-view/export request operates through this
existing interface. `INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the
purpose-tag-carrying order payload and the `EventLog` read both operate through this existing
interface.

## Design Decisions (resolving FS-125's Open Question)

1. **Open Question 1 (`BL-0116`) — the purpose tag is optional; a manoeuvre order with no supplied
   tag is accepted, recorded with an empty-string tag.** Rationale: `FR-1310`'s existing maneuver
   order-issuance path has no other mandatory free-text field, and making the tag mandatory would
   be a stricter validation rule than the requirement's own text commits to ("supplied at order-
   issue time" describes the mechanism, not an enforcement rule). An empty tag is a valid, if
   uninformative, ledger row — consistent with "no manoeuvre order is ever rejected on tag
   grounds," a reasonable minimal-surprise default.

## Files to Create

None.

## Files to Modify

- `spacesim/engine/orders.py` — the manoeuvre-order payload (`FR-3110`'s existing planned-activity
  shape) gains an additive `purpose_tag: str = ""` field, threaded through to the resulting
  `EventLog` entry at execution time.
- `spacesim/engine/eventlog.py` — the existing manoeuvre-event entry shape gains the same
  `purpose_tag` field, additive — no existing entry shape altered.
- `spacesim/session/manager.py` — a new read method (e.g. `maneuver_ledger(asset_id) ->
  list[LedgerRow]`) filtering the `EventLog`'s manoeuvre-event history for the named Asset, in
  chronological order, each row carrying time/delta-v cost/purpose tag/resulting remaining budget
  (already present on the existing manoeuvre-event entry).
- `spacesim/ui_web/server.py` — a new cell-scoped route exposing the ledger view and a CSV-export
  variant of the same data, mirroring the existing per-asset route-scoping convention.

## Implementation Tasks

1. Write a failing test asserting a manoeuvre order accepts and carries an operator-supplied
   `purpose_tag` through to its `EventLog` entry, before adding the field.
2. Add `purpose_tag` to the order payload and `EventLog` entry shape.
3. Write a failing test asserting a blank/omitted `purpose_tag` is accepted (recorded as `""`), per
   Design Decision 1.
4. Write a failing test asserting `maneuver_ledger(asset_id)` returns exactly N rows for an Asset
   with N recorded manoeuvres, each matching the `EventLog`'s own values, before writing the method.
5. Write `session/manager.py::maneuver_ledger()`.
6. Write a failing test asserting the new route's cell-scoping matches every other Asset-scoped
   route's existing fog-of-war behavior, before adding the route.
7. Add the ledger-view and CSV-export routes.
8. Re-run the full existing suite; confirm zero regressions to any existing manoeuvre/order test.

## Tests to Add

- `spacesim/tests/test_orders.py` — `purpose_tag` accepted, carried through to the `EventLog` entry;
  blank tag accepted.
- `spacesim/tests/test_session_features.py` (or equivalent) — `maneuver_ledger()` returns the
  expected N rows with correct values for a known manoeuvre sequence.
- `spacesim/tests/test_web.py` — the new route(s) return the expected ledger/CSV content;
  cell-scoping matches every other Asset-scoped route's fog-of-war behavior (an operator cannot
  fetch another cell's Asset ledger).

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — no wall-clock read or global RNG use introduced.

## Documentation Updates

- `CLAUDE.md` Code Map — `engine/orders.py`, `session/manager.py` entries each gain a one-line note
  for the purpose tag/ledger.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-1320`'s row's `Impl.
  Package`/`Test` cells updated from `UNASSIGNED` to `IP-1250`/the named test files.
- `docs/features/FS-125-maneuver-ledger.md` — `Referenced By` metadata gains this package's link.
- `docs/pipeline/backlog.md` — `BL-0116` flips `DONE` (resolved by Design Decision 1 above).

## Definition of Done

- [ ] Manoeuvre orders accept and carry an operator-supplied (or blank) purpose tag through to the
  `EventLog`.
- [ ] `maneuver_ledger()` returns exactly N rows for an Asset with N recorded manoeuvres, matching
  the `EventLog`.
- [ ] The ledger-view/CSV-export routes are cell-scoped identically to every other Asset-scoped
  route.
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Every new test named above exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Independently confirm the ledger view is a pure derivation from the `EventLog` (no separate,
  independently-mutable ledger state exists that could drift from it).

## Dependencies

- **Upstream:** [FS-125](../../features/FS-125-maneuver-ledger.md) v1.0 (approved, `✅ Ready for
  implementation planning`); `engine/orders.py`/`engine/eventlog.py` (`IP-1010`, `VERIFIED`).
- **Downstream:** none.
- **Build-sequencing:** independent of every other package in this batch (no shared file).

## Risks

- **Fog-of-war regression risk.** A new Asset-scoped console surface must reuse the console's
  existing cell-scoping mechanism, not introduce a parallel one — Implementation Task 6/the
  corresponding test guards against this.

## Rollback Considerations

The purpose tag and ledger view are additive; reverting the order-payload/`EventLog`-entry field
and removing the ledger method/routes fully removes this package's capability with no
data-migration concern — no manoeuvre order issued before this package carries a `purpose_tag`
field at all, and none is required to.
