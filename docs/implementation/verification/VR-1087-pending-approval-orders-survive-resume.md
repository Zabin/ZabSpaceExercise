# VR-1087 — Verification Report: A Pending-Approval Order Is Still Decidable After Save and Resume (FR-3430, FR-7210, FR-7220; M-2)

> **Document ID:** VR-1087
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1087](../packages/IP-1087-pending-approval-orders-survive-resume.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1087`
> **Feature Mapping:** [FS-127](../../features/FS-127-effect-authorization-gating-and-live-roe.md), [FS-110](../../features/FS-110-save-and-resume.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1087 v1.0, implementing commit `a188929` on branch `claude/ip-1087-build` (parent `cd49d73`). Verified in a fresh session in a separate worktree; no code, package, spec or requirement was edited.

## Result

**VERIFIED** — 0 failed checks. Two Info observations, no finding against the package.

## Definition of Done audit

| Item | Evidence | Pass |
|---|---|---|
| A gated order pending at save is decidable after load, elapsed measured from the original request; decided/unreconstructable never decidable | Independent script on the fix: decide after resume `(True,'')`; after stepping past the request and resuming, deny works and replay equals live; two pending both decidable; decided-before-save answers `no_such_pending_order`. `elapsed_us` = decision time minus the original request time (test 1: at least 180 s spanning the save) | Pass |
| Unreconstructable order rejected with reason and load warning, no 500 | No request entry, later decision entry and rule removed (legacy) each load 200 with a warning naming the order and `rejected`/`gate_lost_on_resume`; `POST /load_save` returns it in `warnings` | Pass |
| Rewind/undo still discard; no-gating sessions byte-unchanged | Rewind and undo after resume leave `_pending == {}` and no orders; no-rules session: event log `model_dump` equal, order list equal, no warning | Pass |
| New tests green, RTM regenerated, suites and gates green, no allow-list grew | See Test run; `--origin-report=rtm` leaves the tree clean; diff touches no allow-list | Pass |

## Verification Checklist audit

| Item | Evidence | Pass |
|---|---|---|
| Re-derive M-2 on the parent and the fix | Parent `orders.py`/`manager.py` swapped in (restored after): `decide` after load is `no_such_pending_order`, 11 of 14 new tests fail. Fix: decidable | Pass |
| Re-read `save_state`/`from_state`/`_rebind` order; no new persisted key | `from_state`: `_rebind()`, pending events, orders restored, `_order_counter`, then `rebuild_pending()` (manager.py:1321). `_rebind` (line 565) clears `orders` and `_pending` and is untouched. Save keys with a pending order: baseline, classification, content, eventlog, final_time, orders, overrides, pending, save_format, seed, simulator_version, ssn_requests, started, vignette_id (unchanged) | Pass |
| `elapsed_us` spans the save | As above | Pass |
| Rewind-after-resume discards | As above, plus mutation M6b below | Pass |
| Three unreconstructable cases warn/reject, none 500 | As above | Pass |
| Permanent gates and doc checks green | See Test run | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Pass |
|---|---|---|---|---|
| FR-3430 | `orders.py::rebuild_pending` (line 325), call in `from_state` | `test_gated_order_resume.py` (approve, deny, wrong role, two pending, decided, rewind) | Lists the new tests; matches `--origin-report=rtm` output exactly | Pass |
| FR-7210 | same | save/load/save/load; legacy-format; route test | Row regenerated | Pass |
| FR-7220 | same | field-for-field order round trip; replay equals live after resumed decision | Row regenerated | Pass |
| NFR-1600 | warning plus `gate_lost_on_resume` | three unreconstructable cases plus route | Row regenerated | Pass |
| ADR-0002 | method reads state and log only | determinism gate; replay-equals-live | n/a | Pass |

Every test in `test_gated_order_resume.py` carries `@pytest.mark.verifies` naming live baseline IDs (the origin suite passes).

## Determinism and invariants

`rebuild_pending` uses no wall clock, no RNG, no eventlog append and adds no import (import guard green). It mutates only `_pending` and an unreconstructable order's own `status`/`fail_reason`. Independent checks on the fix: resumed session event log equals the live one before any decision; replay equals live (world JSON) after a resumed approve, after a resumed deny, after advancing 7200 s, and after a second save/load. A save recorded on the PARENT code containing a pending order loads on the fix with no warning and the order decidable. A pending order whose request was rewound away before saving is not in the save (the registry is cleared by `_rebind`), so nothing is resurrected and no warning is raised; a rewind to a later instant likewise leaves no zombie.

## Fog of war and seat rules

Pending-order data reaches a cell only through the existing cell-scoped `/orders/{cell}` (blue sees its own pending order, red sees none). The only new text is a warning in the White-only `load_save` response (non-White seat: 403); it names an order id and cause only. A wrong-role decision after resume (`red`) is `not_controller`; `cell=observer` is 403. `validate_save`, the event-log cap and the non-finite guards are untouched (no diff in those paths); a hand-edited non-numeric order id still 400s at the order-counter parse, as on the parent (pre-existing, not this package).

## Mutations (each run against `test_gated_order_resume.py`)

| Mutation | Result |
|---|---|
| Skip the rebuild call | Killed (approve-after-resume) |
| Ignore decided entries | Killed (later-decision test) |
| Ignore rule matching (fabricate a rule) | Killed (legacy rule-removed case) |
| Skip the warning | Killed (legacy and no-request-entry cases) |
| Call rebuild twice | Survives: equivalent mutant (rebuild is idempotent; a rejected order is no longer pending, so no duplicate warning) |
| Rebuild inside `_rebind` after the registry clear | Survives: equivalent (registry empty, nothing to rebuild) |
| `_rebind` keeps the registry and rebuilds pending (rewind resurrects) | Killed (`test_rewind_and_undo_after_resume_still_discard_pending`) |

## Test run

| Command | Result |
|---|---|
| `python3 -m pytest` (junit) | exit 0; 2009 tests, 0 failures, 0 errors, 3 skipped |
| `python3 -m pytest -m "not browser"` | exit 0 |
| `python3 -m pytest -m browser` | exit 0, no skips reported |
| `test_determinism.py`, `test_import_guard.py` (by name) | exit 0 each |
| `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py` | exit 0 each |
| `test_gated_order_resume.py` | 14 passed (11 fail on the parent) |
| `python3 -m pytest --origin-report=rtm` | exit 5 (runs no tests); working tree unchanged, so the committed RTM Test column equals tool output |

## Scope audit

The implementing diff is `orders.py`, `manager.py`, the new test file, and the doc step (CLAUDE.md, RTM, ROADMAP, Master Build Plan, packages index) — all named or implied by the package. No file outside scope. CLAUDE.md carries one sentence for each of `orders.py` and `manager.py` as the package asks.

## Ledger audit

Master Build Plan tally recounted from the status column before this update: 87 VERIFIED, 1 COMPLETE (IP-1087), 1 READY (IP-1160), 0 BLOCKED, 89 packages; matches the claim. After this report: 88 VERIFIED, 0 COMPLETE, 1 READY, 89.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| O1 | Package test 1 asks that the approved order "executes in its window and its effect applies"; the test asserts only that it is no longer `pending_approval` and `queued` (the fixture has no window in the stepped span). The live, never-saved session behaves identically, and replay equals live, so no behaviour gap was found | Info | none |
| O2 | A save with a non-`ord-N` order id fails the order-counter parse before `rebuild_pending` (400); identical on the parent | Info | none (pre-existing) |
