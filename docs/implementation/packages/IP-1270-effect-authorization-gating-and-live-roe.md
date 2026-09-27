# IP-1270 — Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes

> **Package ID:** IP-1270
> **Version:** 1.0
> **Status:** 🟡 READY *(authorized 2026-09-27 by the project owner's direct instruction, MSTR-006 §3)*
> **Dependencies:** [FS-127](../../features/FS-127-effect-authorization-gating-and-live-roe.md) v1.0
> (`FR-3430`/`FR-3440`), `engine/orders.py` (`IP-1010`/`IP-1172`, `VERIFIED`), `session/manager.py`
> (`IP-1060`, `VERIFIED`), `FR-4210` roles (`IP-1151`, `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0076` (item B10), `BL-0105` (the
> shared effect-classification taxonomy question with [IP-1290](IP-1290-jamming-delivery-and-effect-detectability.md)
> — **resolved by this package, see Design Decisions**), `BL-0118` (this Feature's other Open
> Question)
> **Produces:** an optional per-effect-type controller-role approval workflow (`FR-3430`) and a
> live, logged mid-session ROE-flag-change mechanism (`FR-3440`), satisfying both in full; **also
> produces the shared effect-classification enumeration [IP-1290](IP-1290-jamming-delivery-and-effect-detectability.md)
> must reuse**
> **Feature Reference:** [FS-127 — Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes](../../features/FS-127-effect-authorization-gating-and-live-roe.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. This package is written first in its batch (per the user-directed order)
specifically so it can settle the effect-classification enumeration `IP-1290` (`FS-129`) shares —
see Design Decisions below. `IP-1290`'s own package must cite this package's resolution, not
re-decide it.*

## Package ID

IP-1270

## Title

Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes

## Objective

Add a vignette-declared gating rule (effect classification → required controller role) that holds a
matching order pending approval, logging the request/decision/elapsed time; and a controller-issued,
logged, mid-session ROE-flag change mechanism preserving deterministic replay.

> **This package is authorized for coding.** Per MSTR-006 §3, the project owner gave explicit
> go-ahead 2026-09-27 (batched with five sibling packages from the same Should-tier intake round).

## Feature Reference

[FS-127 — Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes](../../features/FS-127-effect-authorization-gating-and-live-roe.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-3430 | Optional per-effect-type controller-role authorization gating | A vignette-declared gating rule (per the shared enumeration, Design Decision 1) holds a matching order pending a decision from the designated controller role; the request, decision, and elapsed time are recorded as `EventLog` entries. |
| FR-3440 | Live, logged mid-session Rules-of-Engagement changes | A controller-issued ROE-flag change (kinetic/cyber/any `FR-3430` gating rule) is recorded as an `EventLog` entry effective from its simulated time; `engine/orders.py`'s existing per-cell ROE resolution (`FR-3420`) reads the time-varying value instead of only the vignette's static declaration. |

## Architecture Components

- **C5 Content & Data** (`content/vignette.py`) — owns the vignette-declared gating-rule schema,
  additive to the existing `roe` block.
- **C1 Simulation Engine** (`engine/orders.py`) — owns holding a gated order pending a decision, and
  resolving `FR-3420`'s per-cell ROE flag against a live-changed value rather than only the
  vignette-declared static one.
- **C2 Session/Application Layer** (`session/manager.py`) — owns recording the approval
  request/decision/elapsed-time and the live ROE-change event into the `EventLog`, and checking the
  requesting operator against `FR-4210`'s existing role concept.
- **C6 White Cell** — the designated controller role, per `FR-4210`.

## Interfaces

`INT-0002` (White Cell ↔ Console exercise control) — the approval-decision surface and the
ROE-flag-change control both operate through this existing interface, consistent with `FR-4720`'s
existing live-parameter-adjustment precedent. `INT-0008` (SessionManager → Engine Clock/Scheduler/
EventLog/OrderSystem) — the gated-order hold/release and the ROE-change `EventLog` entry both
operate through this existing interface.

## Design Decisions (resolving FS-127's Open Questions, and the taxonomy shared with FS-129)

1. **Open Question 1 (`BL-0105`) — the shared effect-classification enumeration is: effect
   *action type* (`jam`/`engage`/`observe`/`maneuver`/`downlink`/`cyber`/`command` — the existing
   seven `OrderSystem` action values already named in `CLAUDE.md`'s Code Map) crossed with the
   existing five-D's *reversibility category* (`deceive`/`disrupt`/`deny`/`degrade`/`destroy`,
   `FR-1410`).** A gating rule or a detectability setting is declared against one or both axes (an
   action type alone, a reversibility category alone, or a specific combination) — no new
   vocabulary is introduced beyond what `FR-1410`/`OrderSystem` already name. **This package
   authors the shared enumeration; `IP-1290`'s own package must consume it by reference to this
   document, not re-derive or duplicate it.** Rationale: both `FR-3430` and `FR-1450` independently
   describe "effect type and/or reversibility category" in identical words — reusing the two
   vocabularies the engine already has (order action types, five-D's categories) is the natural,
   non-inventive reading, rather than a third, new taxonomy neither requirement's text implies.
2. **Open Question 2 (`BL-0118`) — a pending-approval order still awaiting a decision at session end
   or rewind is discarded (treated as implicitly denied), with no persisted cross-session pending
   state.** Rationale: no session-persistence mechanism exists for in-flight, undecided orders
   today (`FR-7210`'s save/resume round-trips committed state, not pending-approval requests); a
   rewind already invalidates any order queued after the rewind point per the existing
   `Simulation.rewind_to`/`undo_last` semantics, and a pending-approval order is a queued-not-yet-
   executed order in exactly that sense.

## Files to Create

None.

## Files to Modify

- `spacesim/content/vignette.py` — the existing `roe` schema (`ADR-0035`-era shape) gains an
  additive gating-rule field: a list of `{action_type?, reversibility_category?, required_role}`
  entries, per Design Decision 1's shared enumeration.
- `spacesim/engine/orders.py` — `OrderSystem` gains: (a) a check, before scheduling, of whether the
  order's action type/reversibility category matches a declared gating rule — if so, the order is
  held in a new pending-approval state rather than scheduled; (b) `FR-3420`'s existing per-cell ROE
  resolution reads a time-varying value (the latest ROE-change `EventLog` entry at or before the
  order's issue time) instead of only the vignette's static declaration.
- `spacesim/session/manager.py` — new methods for recording an approval decision (approve/deny,
  logged with elapsed time) and for issuing a live ROE-flag change (logged, effective from its
  simulated time); both check the requesting operator against `FR-4210`'s existing role mechanism.
- `spacesim/ui_web/server.py` — new routes for the pending-approval decision surface and the live
  ROE-flag-change control, White-Cell-role-gated per `FR-4210`'s existing pattern.

## Implementation Tasks

1. Write a failing test asserting an order matching a declared gating rule does not execute until a
   decision is recorded, before adding the pending-approval state.
2. Add the gating-rule schema and the pending-approval hold in `OrderSystem`.
3. Write a failing test asserting the `EventLog` records the approval request, the decision, and
   the elapsed time between them, before wiring the recording logic.
4. Write a failing test asserting an order not matching any gating rule is unaffected (executes per
   its existing gates), regression-only.
5. Write a failing test asserting a controller-issued ROE change at simulated time T changes the
   evaluated ROE value for orders issued after T but not before T, before extending `FR-3420`'s
   resolution to read the time-varying value.
6. Write a failing test asserting replaying the identical `(initial_state, ordered eventlog, seed)`
   reproduces the identical sequence of ROE states, before/alongside Task 5.
7. Write a failing test asserting only an operator holding the designated controller role may
   record an approval decision or issue a ROE change, before adding the role check.
8. Re-run the full existing suite; confirm zero regressions to any existing order/ROE test.

## Tests to Add

- `spacesim/tests/test_orders.py` — gated-order pending-hold behavior; unmatched-order regression;
  time-varying ROE resolution; replay reproduces the identical ROE-state sequence.
- `spacesim/tests/test_session_features.py` (or equivalent) — approval-decision/ROE-change recording
  and elapsed-time computation; role-gated rejection for a non-controller operator.
- `spacesim/tests/test_web.py` — the new routes' role-gating.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — the time-varying ROE resolution reads only declared/logged data, no
wall-clock read or global RNG use introduced.

## Documentation Updates

- `CLAUDE.md` Code Map — `content/vignette.py`, `engine/orders.py`, `session/manager.py` entries
  each gain a one-line note.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-3430`/`FR-3440` rows' `Impl.
  Package`/`Test` cells updated from `UNASSIGNED` to `IP-1270`/the named test files.
- `docs/features/FS-127-effect-authorization-gating-and-live-roe.md` — `Referenced By` metadata
  gains this package's link.
- `docs/pipeline/backlog.md` — `BL-0105` flips `DONE` (resolved by Design Decision 1 above,
  applying to both this package and `IP-1290`); `BL-0118` flips `DONE` (resolved by Design
  Decision 2).

## Definition of Done

- [ ] A gated order is held pending until a decision is recorded; the `EventLog` shows the request,
  decision, and elapsed time.
- [ ] An unmatched order is unaffected.
- [ ] A live ROE change is evaluated correctly relative to its simulated time; replay reproduces the
  identical ROE-state sequence.
- [ ] Only the designated controller role may decide a gated order or issue a ROE change.
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Every new test named above exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Independently confirm the pending-approval order never executes before a decision is
  recorded, by direct code read (not merely re-running the tests this package wrote).
- [ ] Independently confirm `IP-1290`'s own package cites this package's Design Decision 1
  enumeration rather than an independent one.

## Dependencies

- **Upstream:** [FS-127](../../features/FS-127-effect-authorization-gating-and-live-roe.md) v1.0
  (approved, `✅ Ready for implementation planning`); `FR-3420` (`IP-1172`, `VERIFIED`); `FR-4210`
  (`IP-1151`, `VERIFIED`); `FR-7110` (baseline `eventlog.py`, `VERIFIED`).
- **Downstream:** [IP-1290](IP-1290-jamming-delivery-and-effect-detectability.md) (`FS-129`) — must
  consume this package's Design Decision 1 enumeration.
- **Build-sequencing:** should be sequenced before `IP-1290`, or the two coordinated closely, so
  `IP-1290` builds against this package's actual landed enumeration rather than a guess.

## Risks

- **Coordination risk with `IP-1290`.** If `IP-1290` is implemented without re-reading this
  package's actual landed enumeration shape, the two mechanisms could drift apart despite this
  package's own Design Decision 1 intent.
- **Pending-approval-at-rewind risk (Design Decision 2).** Discarding a pending order on
  rewind/session-end is a reasonable default but has not been separately confirmed against every
  existing rewind/undo test path — worth an explicit regression test (Implementation Task 6 area)
  rather than an assumption.

## Rollback Considerations

Both mechanisms are additive to existing `OrderSystem`/`EventLog` state; reverting the gating-rule
check and the time-varying ROE resolution to the prior static-only behavior fully removes this
package's capability with no data-migration concern — no vignette shipped before this package
declares a gating rule, and no session's ROE history has more than one entry before this package
exists.
