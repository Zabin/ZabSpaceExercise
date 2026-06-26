# IMP-102A — Command Scheduling: Order/OrderSystem Lifecycle

> **Document ID:** IMP-102A
> **Version:** 1.0
> **Status:** ✅ Done (as-built — documents existing, test-covered code)
> **Dependencies:** [FS-102](../features/FS-102-command-scheduling.md)
> **Referenced By:** [IMP-101A](IMP-101A-mission-planning.md) (shares the validate path), [IMP-105A](IMP-105A-spacecraft-operations-bus-payload.md) (consumes
> the `command` action)
> **Produces:** the executed-order state [FS-105](../features/FS-105-spacecraft-operations.md)'s console displays
> **Feature Mapping:** FS-102
> **Related Topics:** [`spacesim/engine/orders.py`](../../spacesim/engine/orders.py), [`spacesim/engine/access.py`](../../spacesim/engine/access.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

## 1. Situation

**As-built.** This package documents the existing `Order`/`OrderSystem` execution lifecycle.

## 2. State machine

```
queued (validated, awaiting window)
   │  AccessProvider.windows() reports the channel open at tick T
   ▼
executing (engine tick T: handler fires)
   │  e.g. _h_command (orders.py:688), _h_maneuver (:646), _h_downlink (:660), _h_effect (:623)
   ▼
executed, unconfirmed (state mutated; telemetry not yet downlinked)
   │  next telemetry_downlink access window
   ▼
confirmed (operator's belief, via telemetry, matches the new state)
```

`OrderSystem.issue(order)` (`orders.py:128`) drives `queued → executing` by registering the order
against the relevant access channel via `_next_window()`/`_window_endpoints()` (`:386`, `:381`); the
Scheduler (`engine/clock.py`, per [`CLAUDE.md`](../../CLAUDE.md)) advances the sim clock to the next *scheduled
event*, never past it, which is what makes `executing` land on the exact tick the window opens.
`OrderSystem.cancel(order_id)` (`:201`) is the only path back out of `queued` — once `executing` has
fired, cancellation is no longer possible (the event has already been dispatched to its handler).

## 3. Delivery-path branching

`_plan_command`/`_plan_collection`/`_plan_cyber` (`:226`, `:282`, `:573`) each branch on delivery
path before computing the window:

- **Direct uplink/downlink**: `_next_window(order, channel)` against the named ground station.
- **Stored/ISL delivery**: `_best_isl_window(ap, cell, actor, now)` (`:270`) — a later real
  delivery time via inter-satellite relay, distinct from a direct window and displayed as such (per
  [FS-102](../features/FS-102-command-scheduling.md) §3's "stored/relay paths must be visible as distinct" requirement).
- **Cyber (the non-windowed exception)**: `_plan_cyber` (`:573`) does not call `_next_window` at
  all — cyber resolves against the target's posture immediately, the one effect category exempted
  from the access-window gate (per [`CLAUDE.md`](../../CLAUDE.md)'s "Cyber is the exception" invariant).

## 4. Contention

`_contended(sid, start, end)` (`:319`) checks whether a candidate sensor-tasking window overlaps an
already-booked window for the same sensor; `_candidate_sensors(order)` (`:314`) auto-selects among
non-contended sensors where the order doesn't pin one explicitly. Per [FS-102](../features/FS-102-command-scheduling.md) §3's
contention-visibility requirement, the booking (not just the eventual winner) is queryable via
`InProcessSession.list_orders(session, cell)` (`inprocess.py:192`).

## 5. Satisfying FS-102's capability requirements

- **Real, uncollapsed latency** (FS-102 §3 bullet 1): the four-state machine in §2 is exactly this;
  no code path jumps `queued → confirmed` directly.
- **Stored/relay delivery distinct from direct** (§3 bullet 2): §3's branching, surfaced via the
  `Order`'s `via` field (`orders.py:67`).
- **Cancellable before execution, unambiguous post-cancel state** (§3 bullet 3): `cancel()` (`:201`)
  returns `bool`; once `False` (already executing/executed), the UI must not offer cancel — this is
  enforced by `cancel()` itself, not a UI-side race.
- **Visible contention** (§3 bullet 4): §4, above.

## 6. Test coverage (existing)

Order lifecycle (issue → window → execute → cancel-before-execute) is covered by the existing order
system test suite; cyber's non-windowed exception has its own dedicated test path (distinguishing
it from the other five `_plan_*` branches). No new tests are proposed by this package.

## 7. Related Topics

[FS-102](../features/FS-102-command-scheduling.md) (the spec this documents), [IMP-101A](IMP-101A-mission-planning.md) (shared `_plan()`/validate logic), [IMP-105A](IMP-105A-spacecraft-operations-bus-payload.md)
(the `command` action consumer), [`spacesim/engine/orders.py`](../../spacesim/engine/orders.py), [`spacesim/engine/access.py`](../../spacesim/engine/access.py).
