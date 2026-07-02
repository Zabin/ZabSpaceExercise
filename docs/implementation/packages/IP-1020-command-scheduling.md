# IP-1020 — Command Scheduling: Order/OrderSystem Lifecycle

> **Package ID:** IP-1020
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-102, IP-1010 (shares the validate path)
> **Referenced By:** IP-1050 (consumes the `command` action's lifecycle), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the executed-order state IP-1050/IP-1051's console displays
> **Feature Reference:** [FS-102 — Command Scheduling](../../features/FS-102-command-scheduling.md)
> **Supersedes:** [`docs/implementations/IMP-102A-command-scheduling.md`](../../implementations/IMP-102A-command-scheduling.md)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py), [`spacesim/engine/access.py`](../../../spacesim/engine/access.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-1020

## Title

Command Scheduling — Order/OrderSystem Lifecycle

## Objective

Make the real validate → window → execute → confirm latency chain a committed order survives
observable as genuinely distinct states — never collapsed to "instant" — including stored/ISL
delivery paths, the cyber non-windowed exception, and visible sensor-tasking contention, so the
scheduling surface teaches real C2 latency rather than hiding it (grounded in
[R103](../../research/encyclopedia/R103-satellite-command-and-control.md) §5).

**Situation: already implemented, tested, in production use.** Build-ready specification of
existing code; not a proposal.

## Feature Reference

[FS-102 — Command Scheduling](../../features/FS-102-command-scheduling.md)

## Requirements Covered

FS-102's "Requirements Implemented" field states no FR/NFR explicitly cites this Feature ID
(documented gap, Phase 8 review item). Functional coverage, per the RTM's file-level mapping for
`engine/orders.py`/`engine/access.py`:

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-3110 | Plan-first order issuance with delivery path | `issue()` (`orders.py:128`) drives `queued → executing` via the delivery-path branching in §2 |
| FR-3410 | Execute-time re-validation | Re-validation occurs at the `executing` transition, not only at plan time |
| FR-1130 | Sub-stepped event scheduling (no skipped windows) | The Scheduler advances to the exact tick a window opens, never past it (`engine/clock.py`, cited by `CLAUDE.md` invariant 5) |
| FR-1220 | Access-window computation across six channels | `_next_window()`/`_window_endpoints()` (`orders.py:386`, `:381`) |
| FR-1420 | Cyber resolves outside the access-window gate | `_plan_cyber()` (`orders.py:573`) never calls `_next_window` |
| NFR-1600 | Robustness to invalid input | `cancel()` (`orders.py:201`) returns an unambiguous `bool`, never an indeterminate state |

## Architecture Components

- **C1 Simulation Engine** — `OrderSystem` (`orders.py`), `Scheduler`/`SimClock` (`clock.py`),
  `AccessProvider` (`access.py`).
- **C2 Session / Application Layer** — `InProcessSession.list_orders()` (order-queue/contention
  visibility, `inprocess.py:192`).
- **C7/C8 Blue/Red Cell operator** — the consumers of this lifecycle's observable states.

## Interfaces

**INT-0004** (Blue/Red Cell Operator ↔ Operator Console); **INT-0008** (SessionManager → Simulation
Engine Clock/Scheduler/EventLog/OrderSystem) — per the ICD and FS-102's verified Related Interfaces
field.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code; it proposes no changes.

### Reference files

- `spacesim/engine/orders.py` — `issue()` (`:128`), `cancel()` (`:201`), `_plan_command`/
  `_plan_collection`/`_plan_cyber` (`:226`, `:282`, `:573`), `_best_isl_window()` (`:270`),
  `_contended()` (`:319`), `_candidate_sensors()` (`:314`).
- `spacesim/engine/clock.py` — `Scheduler`, sub-stepped event advance.
- `spacesim/session/inprocess.py` — `list_orders()` (`:192`).

## Implementation Tasks

All **already complete**:

1. ✅ Implement the four-state lifecycle (queued → executing → executed-unconfirmed → confirmed) with
   no code path that jumps directly from `queued` to `confirmed`.
2. ✅ Branch delivery path before computing the window: direct uplink/downlink, stored/ISL relay
   (`_best_isl_window`, `:270`), and the cyber non-windowed exception (`_plan_cyber`, `:573`).
3. ✅ Implement `cancel()` returning an unambiguous `bool` — `True` only while still `queued`; once
   `executing` has fired, cancellation is structurally impossible (the event already dispatched).
4. ✅ Implement sensor-tasking contention (`_contended()`, `:319`) so a second request against an
   already-booked sensor window is rejected/queued, never silently double-booked, and the booking is
   queryable via `list_orders()`.

## Tests to Add

None — covered by the existing order-system test suite (issue → window → execute → cancel-before-
execute) and cyber's dedicated non-windowed-exception test path.

## Documentation Updates

- Supersedes [`docs/implementations/IMP-102A-command-scheduling.md`](../../implementations/IMP-102A-command-scheduling.md)
  (banner added).
- `ROADMAP.md` Implementation Packages theme updated.

## Definition of Done

- [x] Four lifecycle states are each independently observable; no direct `queued → confirmed` path.
- [x] Stored/ISL delivery is visibly distinct from direct uplink via the `Order.via` field.
- [x] `cancel()` never returns an ambiguous result.
- [x] Sensor-tasking contention is visible via `list_orders()`, not silently resolved.
- [x] "Time until window" is computed from the same `AccessProvider.windows()` the engine gates
  execution on.
- [x] Cyber's non-windowed resolution is structurally distinct (`earliest_window = None`), not a
  cosmetic UI flag.

## Verification Checklist

- [x] `orders.py:128,201,226,270,282,319,573` read and confirmed against the current tree.
- [x] Order-system test suite present and green (`python3 -m pytest`, per `CLAUDE.md`).
- [x] No FR/NFR explicitly cites FS-102 (confirmed absence) — recorded as a traceability gap.

## Dependencies

- **Upstream:** IP-1010 (shares `_plan()`/`_validate()`).
- **Downstream:** IP-1050 (the `command` action's execution lifecycle), IP-1051 (effect-category
  windowed/cyber-exception display), IP-2010 (window-discipline rubric dimension reads rejection
  data this package produces).
- **Build-sequencing:** None — already shipped.

## Risks

- A display-side "time until window" estimate computed independently of `AccessProvider.windows()`
  (e.g., a client-side approximation) would silently violate the determinism-consistent-display
  requirement; any future console rework must preserve the single-source-of-truth window query.
- The cyber exception's non-windowed resolution, if not kept visually distinct in a future console
  redesign, could mislead an operator into expecting a window wait that will never come.

## Rollback Considerations

Rollback surface: `spacesim/engine/orders.py` (`issue`, `cancel`, `_plan_command`,
`_plan_collection`, `_plan_cyber`, `_contended`) and `spacesim/engine/clock.py` (`Scheduler`). No
persisted schema change; `Order`'s `via`/`status` fields are part of the existing eventlog/save
format already exercised by the determinism property test, so any revert must be re-verified
against that test rather than assumed safe.
