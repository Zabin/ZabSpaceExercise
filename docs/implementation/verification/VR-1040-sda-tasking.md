[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md) ·
[Verification index](INDEX.md) · [Docs index](../../INDEX.md)

# VR-1040 — Verification Report: SDA Tasking (Sensor Tasking & SSN Request Lifecycle)

## Package

- **ID:** IP-1040
- **Title:** SDA Tasking — Sensor Tasking & SSN Request Lifecycle
- **Version verified:** 1.0
- **Commit hash verified:** `86db642c32516bf8cbc290f0bf7fd7d9897a6642`

**Process note:** 4 of 11 as-built packages in the `BL-0004` retro-verification sweep.

## Result

**✅ VERIFIED** (0 failures; 1 Low citation-drift finding — same class as prior packages in this
sweep)

## Definition of Done audit

| Item | Evidence | Pass/fail |
|---|---|---|
| A tasking action's SDA-chain-stage intent (`search\|track\|characterize`) is carried through to the confidence gain computed on delivery | `_h_deliver()` (`ssn.py:379-381`): `base = 0.95 if intent == "characterize" else 0.5`, scaled by window quality (`wq`) — a direct, confirmed read of the gain computation. | ✅ Pass |
| Sensor contention (own-sensor and SSN) is surfaced with a distinct rejection reason, never a silent winner selection | Own-sensor: `_plan_collection()`'s `fail_reason = "sensor_contended"` (confirmed in `VR-1010`). SSN: `submit_request()` sets `"no_coverage_regime"` (`ssn.py:247`) vs. `"no_coverage_within_sla"` (`:266`) — two distinct, named failure reasons, never a silent fallback. | ✅ Pass |
| Collected and delivered are two separately observable, separately cancelable events | `_h_collect()` (`:341-358`) stages on `world.ssn_staged` and sets `state = "COLLECTED"`, touching no `Track`; `_h_deliver()` (`:360-392`) pops the staged data and sets `state = "DELIVERED"` only after calling `observe()`. `cancel_request()` (`:301`) only succeeds while `state == "SCHEDULED"` (before either fires) — a genuinely separate, earlier cancellation window. | ✅ Pass |
| Priority/SLA tradeoff and coalition-affiliation delay are visible on the returned `SSNAck` | `MAX_WAIT_S`/`PROCESSING_DELAY_S`/`COALITION_DELAY_MULTIPLIER` (`:38,39,44`) all resolved inside `submit_request()` before the `SSNAck` is constructed; failure acks carry the specific `reason` string. | ✅ Pass |
| Delivery writes through the same `observe()`/`Track` model IP-1030 documents — no parallel SSN-specific confidence representation exists | `_h_deliver()` (`:383`) calls `observe(track, ...)` directly, importing the same function `custody.py` exports — no SSN-specific confidence field or shadow representation exists anywhere in `ssn.py`. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/fail |
|---|---|---|
| `orders.py:282,314,319` and `ssn.py:105,208,221,301,324,341,360` read and confirmed | **`ssn.py`'s own citations are exact — zero drift** for every one of `SSNRequest.state` (`:105`), `_eligible` (`:208`), `submit_request` (`:221`), `cancel_request` (`:301`), `coverage` (`:324`), `_h_collect`/`_h_deliver` (`:341`/`:360`). `orders.py`'s three citations have drifted +5 each (`_plan_collection` `:282→287`, `_candidate_sensors` `:314→319`, `_contended` `:319→324`) — the same file-wide drift `VR-1010`/`VR-1020`/`VR-1030` already found. Content confirmed correct throughout. | ✅ Pass (citation drift, Finding 1) |
| `spacesim/tests/test_ssn.py` present and green | 12 tests, all passing. | ✅ Pass |
| No FR/NFR explicitly cites FS-104 | Confirmed independently: no "FS-104" hits in `01-functional-requirements.md`. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state (before → after) | Pass/fail |
|---|---|---|---|---|
| FR-3210 | `engine/ssn.py` (`submit_request`, `_eligible`) | `test_ssn.py` | Test: `UNASSIGNED` → filled; Impl. Package: `engine/ssn.py` → `IP-1040` (exclusively owned file) | ✅ Pass |
| FR-3220 | `engine/ssn.py` (`_h_deliver`, calls `IP-1030`'s `observe()`) | `test_ssn.py` | Same update as `FR-3210` | ✅ Pass |
| FR-1510 | Consumed transitively (`_h_deliver` is the SSN-side caller) | Already covered by `VR-1030` | No cell change — this package consumes `IP-1030`'s requirement, doesn't implement it | ✅ Pass |
| NFR-2100 | `SSNSystem` as a seam per ADR-0010 | — | **Not updated**: the RTM's existing citation for `NFR-2100` names `propagator.py`/`access.py`/`effects.py` only — a different, narrower seam grouping than this package's own broader "seam" claim. Left as-is rather than force-fitting `ssn.py` into a citation that doesn't currently include it; a genuine scope question for `04-requirements-engineering`, not resolved here. | — (observation, not a finding) |

## Test run

```
$ python3 -m pytest
566 passed, 3 skipped, 1 warning in 68.73s

$ python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
14 passed in 0.92s

$ python3 -m pytest spacesim/tests/test_ssn.py -v
12 passed in 1.25s
```

No regression from `VR-1030` (run #21)'s count.

## Scope audit

**Files to Create: none. Files to Modify: none.** The three "Reference files" (`orders.py`,
`ssn.py`, `isr.py`) were each read for this verification (`isr.py` referenced only for the
beam-mode database, correctly out of this package's own scope per its own text).

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | `orders.py`'s three cited functions (`_plan_collection`, `_candidate_sensors`, `_contended`) have all drifted +5 lines — the same file-wide drift `VR-1010`/`VR-1020`/`VR-1030` already found and attributed to earlier unrelated insertions in this file. `ssn.py`'s own citations have zero drift. Content confirmed correct throughout. | Low | Fold into `IP-1040`'s next package-maintenance touch; no dedicated run. Same drift class as `BL-0016`/`BL-0032`/`BL-0037`/`BL-0038`. |

No Critical/High/Medium findings — every DoD item and the package's own Objective vocabulary
match the shipped code exactly.

## Related

[`IP-1040`](../packages/IP-1040-sda-tasking.md) ·
[`FS-104`](../../features/FS-104-sda-tasking.md) ·
[`00-master-build-plan.md`](../00-master-build-plan.md) ·
[`03-requirements-traceability-matrix.md`](../../requirements/03-requirements-traceability-matrix.md)
