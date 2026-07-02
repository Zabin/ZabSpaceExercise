# IP-1040 — SDA Tasking: Sensor Tasking & SSN Request Lifecycle

> **Package ID:** IP-1040
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-104
> **Referenced By:** IP-1030 (consumes this package's `observe()` deliveries), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** fresh custody data consumed by IP-1030
> **Feature Reference:** [FS-104 — SDA Tasking](../../features/FS-104-sda-tasking.md)
> **Supersedes:** [`docs/implementations/IMP-104A-sda-tasking.md`](../../implementations/IMP-104A-sda-tasking.md)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py), [`spacesim/engine/ssn.py`](../../../spacesim/engine/ssn.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-1040

## Title

SDA Tasking — Sensor Tasking & SSN Request Lifecycle

## Objective

Let a cell direct its own sensors (with explicit beam-mode tradeoff and visible contention) and/or
request off-board Mock SSN collection (with visible priority/SLA tradeoff and a genuine
collected-vs-delivered distinction) to advance its space domain awareness — the detect/track/ID/
characterize/predict chain — without the tasking surface hiding real sensor scarcity behind a single
"scan" button.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-104 — SDA Tasking](../../features/FS-104-sda-tasking.md)

## Requirements Covered

FS-104's "Requirements Implemented" field reports no explicit FR/NFR citation (documented gap).
Functional coverage per the RTM's `engine/ssn.py`/`engine/orders.py` mapping:

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-3210 | SSN request submission under single-task contention | `SSNSystem.submit_request()` (`ssn.py:221`), `_eligible()` (`:208`) |
| FR-3220 | SSN delivery into the requester's TrackCatalog | `_h_deliver()` (`ssn.py:360`) calls `observe()` (IP-1030) |
| FR-1510 | Track confidence reset on observation | Consumed transitively — `_h_deliver()` is the SSN-side caller of IP-1030's `observe()` |
| NFR-2100 | Independently testable fidelity seams | `SSNSystem` is a seam behind `engine/ssn.py`, per ADR-0010 |

## Architecture Components

- **C1 Simulation Engine** — `OrderSystem._plan_collection` (`orders.py:282`, own-sensor tasking).
- **C3 Mock SSN** — `engine/ssn.py` (`SSNSystem`, off-board request lifecycle).
- **C2 Session / Application Layer** — the `CellController`/`SessionAPI` tasking-request boundary.

## Interfaces

**INT-0009** (CellController/SessionAPI → Mock SSN); **INT-0010** (Mock SSN → Simulation Engine
Scheduler/EventLog/Custody, delivery) — per the ICD and FS-104's verified Related Interfaces field.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/engine/orders.py` — `_plan_collection()` (`:282`), `_candidate_sensors()` (`:314`),
  `_contended()` (`:319`).
- `spacesim/engine/ssn.py` — `SSNSystem.submit_request()` (`:221`), `SSNRequest.state`
  (`DRAFT→SCHEDULED→COLLECTED→DELIVERED`/`CANCELLED`/`FAILED`, `:105`), `_eligible()` (`:208`),
  `_h_collect`/`_h_deliver` (`:341`, `:360`), `cancel_request()` (`:301`), `coverage()` (`:324`).
- `spacesim/engine/isr.py` — the beam-mode database carried through `order.params` (out of this
  package's direct scope per FS-104 §2, referenced for the tradeoff data it supplies).

## Implementation Tasks

All **already complete**:

1. ✅ Implement own-sensor tasking (`_plan_collection`) with sensor auto-selection among the cell's
   own sensors, real access geometry per candidate, and contention rejection (`"sensor_contended"`)
   distinct from no-geometry rejection (`"no_window"`).
2. ✅ Implement the off-board SSN request state machine (`DRAFT → SCHEDULED → COLLECTED →
   DELIVERED`) with two separately-schedulable/cancelable deterministic events (`ssn_collect`,
   `ssn_deliver`) so "collected" and "delivered" are genuinely distinct observable states.
3. ✅ Implement priority/SLA resolution (`MAX_WAIT_S[priority]`, `PROCESSING_DELAY_S[priority]`,
   `COALITION_DELAY_MULTIPLIER`, saturation surcharge) with distinct failure reasons
   (`"no_coverage_regime"` vs. `"no_coverage_within_sla"`).
4. ✅ Implement `_h_collect`/`_h_deliver` so "collected" stages a measurement on
   `world.ssn_staged` without touching any `Track`, and only "delivered" calls `observe()` — the
   moment off-board collection becomes the requester's own custody belief, never another cell's.
5. ✅ Implement `cancel_request()` so a cancel-before-collection removes both scheduled events, with
   no `Track` side effect.

## Tests to Add

None — covered by `spacesim/tests/test_ssn.py` (submission resolution, collect/deliver pair,
cancel-before-collect, contention/SLA failure paths) and the order-system test suite (own-sensor
tasking contention).

## Documentation Updates

- Supersedes [`docs/implementations/IMP-104A-sda-tasking.md`](../../implementations/IMP-104A-sda-tasking.md).
- `ROADMAP.md` Implementation Packages theme updated.

## Definition of Done

- [x] A tasking action's SDA-chain-stage intent (`search | track | characterize`) is carried through
  to the confidence gain computed on delivery.
- [x] Sensor contention (own-sensor and SSN) is surfaced with a distinct rejection reason, never a
  silent winner selection.
- [x] Collected and delivered are two separately observable, separately cancelable events.
- [x] Priority/SLA tradeoff and coalition-affiliation delay are visible on the returned `SSNAck`.
- [x] Delivery writes through the same `observe()`/`Track` model IP-1030 documents — no parallel SSN-
  specific confidence representation exists.

## Verification Checklist

- [x] `orders.py:282,314,319` and `ssn.py:105,208,221,301,324,341,360` read and confirmed against
  the current tree.
- [x] `spacesim/tests/test_ssn.py` present and green.
- [x] No FR/NFR explicitly cites FS-104 (confirmed absence) — recorded as a traceability gap.

## Dependencies

- **Upstream:** IP-1030 (this package's `_h_deliver()` calls IP-1030's `observe()`).
- **Downstream:** None beyond IP-1030 consuming this package's output.
- **Build-sequencing:** None — already shipped.

## Risks

- If a future vignette's SSN dispersion preset difference required engine special-casing (rather
  than a data parameter), FS-103/IP-1030's stated uniform custody-decay behavior across vignettes
  would be violated — the current data-driven `SSNNetwork` dispersion-preset design avoids this.
- A future fusion feature introducing a second, parallel confidence representation (rather than
  writing through the existing `observe()`/`Track` model) would create a conflicting confidence
  indicator — explicitly named as a risk in FS-104 §8.

## Rollback Considerations

Rollback surface: `spacesim/engine/orders.py` (`_plan_collection`) and `spacesim/engine/ssn.py`
(all `SSNSystem` methods/handlers). `world.ssn_staged` is transient per-request state, not a
long-lived schema; a revert requires re-verification against `spacesim/tests/test_ssn.py` and the
determinism property test (both handlers participate in eventlog replay).
