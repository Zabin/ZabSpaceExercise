# IMP-104A — SDA Tasking: Sensor Tasking & SSN Request Lifecycle

> **Document ID:** IMP-104A
> **Version:** 1.0
> **Status:** ✅ Done (as-built — documents existing, test-covered code)
> **Dependencies:** [FS-104](../features/FS-104-sda-tasking.md)
> **Referenced By:** [IMP-103A](IMP-103A-custody-management.md) (consumes the `observe()` calls this package's deliveries make)
> **Produces:** fresh custody data consumed by [FS-103](../features/FS-103-custody-management.md)
> **Feature Mapping:** FS-104
> **Related Topics:** [`spacesim/engine/orders.py`](../../spacesim/engine/orders.py), [`spacesim/engine/ssn.py`](../../spacesim/engine/ssn.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

> **Superseded.** This document's content has been re-derived, re-verified against the current
> source tree, and re-published under the canonical `docs/implementation/packages/` tier as
> [**IP-1040**](../implementation/packages/IP-1040-sda-tasking.md). This file is retained for
> historical reference and is not deleted, but [`IP-1040`](../implementation/packages/IP-1040-sda-tasking.md)
> is the document of record going forward — see
> [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> §"Relationship to the prior `docs/implementations/` corpus."

## 1. Situation

**As-built.** This package documents the two existing tasking paths — own-sensor tasking via
`OrderSystem._plan_collection` and off-board collection via `SSNSystem` — that together implement
FS-104.

## 2. Own-sensor tasking

`OrderSystem._plan_collection(order, commit)` (`orders.py:282`) resolves an `observe` order against
the cell's own sensors: `_candidate_sensors(order)` (`:314`) either honors an explicit
`order.actor` or auto-selects among all sensors `s.owner == order.cell`; for each candidate it
queries real geometry via `AccessProvider.windows(sid, target, SENSOR_OBSERVATION, ...)` and skips
any window that `_contended(sid, start, end)` (`:319`) finds overlapping an already-booked window
for that sensor — the same booking/contention pattern [IMP-102A](IMP-102A-command-scheduling.md) §4 documents for the
order queue generally, applied here to the sensor resource specifically. On success the order is
queued with `delivery_path = "sensor_collect"` and the chosen sensor/window recorded; on failure
the rejection reason is `"sensor_contended"` (a candidate existed but every window collided) or
`"no_window"` (no geometry at all) — distinct strings, satisfying FS-104 §3's contention-visibility
requirement (a UI reading `order.fail_reason` can tell the operator *why*, not just that tasking
failed).

The beam-mode tradeoff FS-104 §3 requires to be explicit (swath vs. resolution vs. power) is
carried in `order.params` through to the ISR beam-mode database (`engine/isr.py`, per `CLAUDE.md`'s
code map) at execution; this package documents the tasking/contention lifecycle around that choice,
not the beam-mode database itself (out of scope per FS-104 §2 — "out of scope: ... data-fusion
algorithms themselves").

## 3. Off-board SSN requests

`SSNSystem.submit_request(cell, req)` (`ssn.py:221`) is the off-board path. Its state machine —
`DRAFT → SCHEDULED → COLLECTED → DELIVERED` (or `CANCELLED`/`FAILED` at various points,
`SSNRequest.state`, `:105`) — is what makes "collected" and "delivered" visibly distinct events
per FS-104 §3's "collected-vs-delivered distinction" requirement:

- **Resolution** (`:244`-`:284`): `_eligible(net, regime)` (`:208`) filters the cell's network to
  phenomenology-matched sensors; the earliest viable, non-contended window across all eligible
  sensors within the priority's SLA horizon (`MAX_WAIT_S[priority]`) is chosen — the "hybrid
  turnaround" rule named in `CLAUDE.md`'s code map. Failure reasons are likewise specific:
  `"no_coverage_regime"` (no eligible sensor exists at all) vs. `"no_coverage_within_sla"` (sensors
  exist but no window inside the SLA) — again satisfying the visible-tradeoff requirement rather
  than a single opaque rejection.
- **Priority/SLA tradeoff** (FS-104 §3 bullet 4): `PROCESSING_DELAY_S[priority]` sets the
  collect→product delay; `COALITION_DELAY_MULTIPLIER` lengthens it for `affiliation == "coalition"`
  networks, and a saturation surcharge (`:276`-`:277`) adds a second delay increment when the
  cell's in-flight count meets the network's `concurrency` — both terms are visible on the returned
  `SSNAck`'s `collect_at`/`product_at` fields (`:113`), not hidden inside a single ETA.
- **Two deterministic events, not one** (`:291`-`:296`): `ssn_collect` fires at `collect_at`,
  `ssn_deliver` at `product_at` — separately schedulable/cancelable, both tagged with the request
  id so `cancel_request` (`:301`) cancelling before collection removes both via `sim.cancel(rid)`.

## 4. Collected vs. delivered (handlers)

`_h_collect` (`:341`) stages the measurement on `world.ssn_staged[rid]` (target orbit + window
quality) without touching any `Track` — this is the "collected" state, deliberately not yet
fog-scoped to the requester. `_h_deliver` (`:360`) is the only place a `Track` is created/updated:
it pops the staged measurement, computes a confidence gain scaled by both intent
(`base = 0.95` if `characterize` else `0.5`) and the window quality carried on the payload (§8's
"grazing pass yields a weaker product" rule), then calls `observe()` (`custody.py:57`, per
[IMP-103A](IMP-103A-custody-management.md) §2) on the requester's own `Track` — this is the exact moment off-board
collection becomes the requester's custody belief, never another cell's. `coverage(cell, regime)`
(`:324`) exposes a pre-submission phenomenology check (which sensors are kind-eligible, current
concurrency/affiliation/dispersion) so an operator can sanity-check viability before submitting.

## 5. Satisfying FS-104's capability requirements

- **Tasking traceable to an SDA-chain stage** (§3 bullet 1): `SSNRequest.intent`
  (`search | track | characterize`, `:97`) and the `observe` order's analogous intent carry this
  through to the confidence gain computed in §4.
- **Beam-mode tradeoff explicit** (§3 bullet 2): carried via `order.params` into `engine/isr.py`
  (out of this package's scope per FS-104 §2).
- **Sensor contention visible** (§3 bullet 3): §2's `_contended()`/`"sensor_contended"` distinction.
- **Priority/SLA + collected-vs-delivered visible** (§3 bullet 4): §3-4's two-event state machine
  and distinct failure reasons.
- **Fusion extends the existing display, no parallel confidence model** (§3 bullet 5): §4's
  `_h_deliver` writes through the same `observe()`/`Track` model [IMP-103A](IMP-103A-custody-management.md) documents — no
  SSN-specific confidence representation exists.

## 6. Test coverage (existing)

`spacesim/tests/test_ssn.py` covers submission resolution, the collect/deliver event pair,
cancel-before-collect, and contention/SLA failure paths; sensor-tasking contention is covered by
the order-system test suite. No new tests are proposed by this package.

## 7. Related Topics

[FS-104](../features/FS-104-sda-tasking.md) (the spec this documents), [IMP-103A](IMP-103A-custody-management.md) (the custody model this feature's
deliveries write into), [IMP-102A](IMP-102A-command-scheduling.md) (the shared contention pattern), [`spacesim/engine/orders.py`](../../spacesim/engine/orders.py),
[`spacesim/engine/ssn.py`](../../spacesim/engine/ssn.py).
