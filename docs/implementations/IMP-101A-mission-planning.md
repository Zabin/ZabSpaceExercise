# IMP-101A — Mission Planning: Dry-Run Preview & Window/Δv Display

> **Document ID:** IMP-101A
> **Version:** 1.0
> **Status:** ✅ Done (as-built — documents existing, test-covered code)
> **Dependencies:** [FS-101](../features/FS-101-mission-planning.md)
> **Referenced By:** [IMP-102A](IMP-102A-command-scheduling.md) (shares the validate path)
> **Produces:** the planning surface [FS-105](../features/FS-105-spacecraft-operations.md)'s console renders
> **Feature Mapping:** FS-101
> **Related Topics:** [`spacesim/engine/orders.py`](../../spacesim/engine/orders.py), [`spacesim/session/inprocess.py`](../../spacesim/session/inprocess.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

> **Superseded.** This document's content has been re-derived, re-verified against the current
> source tree, and re-published under the canonical `docs/implementation/packages/` tier as
> [**IP-1010**](../implementation/packages/IP-1010-mission-planning.md). This file is retained for
> historical reference and is not deleted, but [`IP-1010`](../implementation/packages/IP-1010-mission-planning.md)
> is the document of record going forward — see
> [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> §"Relationship to the prior `docs/implementations/` corpus."

## 1. Situation

**As-built.** This package documents the existing `dry_run()` mechanism and the session-layer
preview endpoints that already implement [FS-101](../features/FS-101-mission-planning.md)'s capability requirements.

## 2. Architecture

The preview path is a read-only mirror of the commit path, not a separate implementation:

```
OrderSystem.dry_run(order)            # spacesim/engine/orders.py:136
    → _plan(order, commit=False)      # :147 — same validate/window logic as issue()
        → _validate(order)            # :323 — preconditions (resource/state)
        → _next_window(order, channel) # :386 — real AccessProvider.windows() query
        → _exec_payload / _plan_command / _plan_collection / _plan_cyber
          (commit=False branch: computes outcome, books nothing, schedules nothing)
    ← returns an Order with status/cost/window fields populated, world unmodified
```

`OrderSystem.issue(order)` (`:128`) is the commit path; it calls the identical `_plan(order,
commit=True)`. The single shared `_plan()` method (`:147`) is what guarantees preview and commit
can never silently diverge — there is exactly one validate/window code path, parameterized by a
boolean, not two maintained in parallel.

Session-layer exposure: `InProcessSession.validate_order(session, cell, order)` (`spacesim/session/
inprocess.py:186`) calls `dry_run()` under the same `_locked_read(session)` context manager used by
every other read (`:49`), and `compute_maneuver(...)` (`:314`) / `preview_consequence(...)` (`:466`)
provide the Δv-cost and kinetic-consequence preview surfaces FS-101 §3 requires, respectively.

## 3. Data model

`Order` (`spacesim/engine/orders.py:67`) carries the fields both preview and commit populate
identically: action, actor, target, params, `via` (delivery path), and — after either `dry_run()` or
`issue()` — a populated status/window/cost. No separate "preview order" type exists; this is
deliberate (§2's single-code-path guarantee would be undermined by a parallel preview schema).

## 4. Satisfying FS-101's capability requirements

- **Plans previewable without commitment** (FS-101 §3 bullet 1): `dry_run()` schedules/registers/
  books nothing — confirmed by `_plan(order, commit=False)`'s branches never calling the booking
  helpers (`_release_bookings_on_execute`, `:177`, is on the commit path only).
- **Regime/propagator-honest reachability** (FS-101 §3 bullet 2): `_validate()` (`:323`) runs before
  any window query, so a regime-unreachable target fails validation in both preview and commit,
  identically.
- **Δv preview per entry mode** (FS-101 §3 bullet 3): `compute_maneuver()` (`inprocess.py:314`)
  exposes the same six-entry-mode Δv computation `engine/maneuver.py` provides to the committed
  maneuver handler (`_h_maneuver`, `orders.py:646`).
- **Real sampled/bisected window display** (FS-101 §3 bullet 4): `_next_window()` (`:386`) calls
  `AccessProvider.windows()` (`access.py:107`) — the same bisection-based geometry the engine gates
  execution on; there is no separate display-only window estimator.
- **Rejection reasons are returned, not just a boolean** (FS-101 §3 bullet 5): `_validate()` returns
  `tuple[bool, str]` (`:323`), and the failure string propagates to the `Order`'s status — the UI's
  pre-disabled-button pattern reads this string directly.

## 5. Test coverage (existing)

The behavior this package documents is covered by the existing suite (not newly added here):
`dry_run()`/`issue()` parity is implicitly exercised everywhere both are called in the same test
(any test asserting a preview matches the eventual commit), and the Phase-1 determinism property
test guarantees `_plan()`'s commit branch is itself replay-exact. No new tests are proposed by this
package since it documents already-tested code.

## 6. Open questions

- Course-of-action comparison ([FS-101](../features/FS-101-mission-planning.md) §7, [R311](../research/encyclopedia/R311-course-of-action-analysis.md)) would need a new data shape (multiple
  named candidate `Order` sets compared side by side) — not designed here; out of this package's
  as-built scope.

## 7. Related Topics

[FS-101](../features/FS-101-mission-planning.md) (the spec this documents), [IMP-102A](IMP-102A-command-scheduling.md) (the commit-side lifecycle sharing this same
`_plan()` code path), [`spacesim/engine/orders.py`](../../spacesim/engine/orders.py), [`spacesim/session/inprocess.py`](../../spacesim/session/inprocess.py).
