# VR-1130 — Verification Report: Observer Read-Only Access

> **Document ID:** VR-1130
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1130](../packages/IP-1130-observer-read-only-access.md), [FS-113](../../features/FS-113-observer-read-only-access.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition for IP-1130; re-confirmation of `BL-0011`
> **Feature Mapping:** FS-113
> **Related Topics:** [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py), [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py), [`spacesim/tests/test_observer.py`](../../../spacesim/tests/test_observer.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1130 — Observer Read-Only Access (FS-113)
- **Version verified:** 1.1
- **Tree state verified:** commit `2a0339413e9ed614c3a53573e21ac945b16d25fc` (branch `claude/pipeline-skill-ijwd1f`)
- **Independence:** implemented in run #7 of this same overall conversation; this is run #14.
  Several runs and at least one context-compaction boundary separate implementation from this
  verification. Every claim below was independently re-derived from the live source and a fresh
  test run.

## Result

**VERIFIED** — every Definition of Done and Verification Checklist item is confirmed; full suite
green; both permanent gates green; requirements traceability audited (one pre-existing, already-
flagged RTM title defect re-confirmed present). **`BL-0011`'s predicted maintenance-drift risk has
not materialized as a functional gap**: both mutating routes added since this package shipped
(`IP-1151`'s `/roles/assign`, and this package's own `/observer/view` POST) reject an
Observer-seated caller correctly — via a stricter White-Cell-only allowlist check
(`cell != "white"`), not the `_reject_observer` denylist this package's own test table exercises.
One Low finding: neither route has an explicit test naming `cell="observer"` specifically, only a
generic non-white value (`"blue"`) — a real but very low-risk test-coverage gap given the
allowlist's logic trivially generalizes to any non-white string.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization obtained (MSTR-006 §3). | `docs/pipeline/pipeline-journal.md` run #2. | ✅ Pass |
| An Observer's designated view is served identically to its native audience — no divergent filtering. | `inprocess.py:302-309` (`get_observer_view`) dispatches directly to `get_godview`/`get_view`, no new filtering logic. `test_observer_view_defaults_to_godview` and related tests confirm the dispatch. | ✅ Pass |
| Every existing mutating route rejects an Observer-seated caller (full, re-derived 22-route table). | `server.py`: 22 routes call `_reject_observer(cell)` (confirmed by direct grep, listed in Scope audit below), matching `test_observer.py`'s `_MUTATING_ROUTES` table exactly (22 entries). `test_every_mutating_route_rejects_observer` parametrized across all 22, all pass. | ✅ Pass |
| The rejection holds for a request bypassing the client UI. | `test_every_mutating_route_rejects_observer` calls raw HTTP routes via `TestClient`, no JS/UI involved — confirms the server-side guard, not a client-side disable. | ✅ Pass |
| No `WorldState` mutation occurs from any Observer-seated request. | Test compares eventlog length before/after each rejected call (`before = len(c.get(f"/api/sessions/{sid}/eventlog").json())`, then asserts `403`) — an eventlog-length check is a strictly stronger signal than a godview-snapshot diff here, since it isn't affected by the server-authoritative lazy clock's passive time advancement. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `test_observer.py` exists, covers every mutating route, and is green. | 28 tests, all passing; `_MUTATING_ROUTES` has 22 entries, matching the live route table's 22 `_reject_observer` call sites exactly (re-derived directly, not counted from the package's own claim). | ✅ Pass |
| `test_determinism.py` remains green. | Confirmed (14 passed, with `test_import_guard.py`). | ✅ Pass |
| `test_import_guard.py` remains green. | Same run; also confirmed by reading — this package touches no `spacesim/engine/` file. | ✅ Pass |
| Manual review confirms `get_observer_view`'s cell-view branch calls the same `CellController.view()` every existing cell-scoped endpoint uses. | `inprocess.py:308-309` — `get_view(session, designation)` is the same method every Blue/Red/White cell-scoped read already calls (confirmed by reading `get_view`'s own definition, used identically elsewhere in the file). No parallel/forked filtering path exists. | ✅ Pass |
| FS-113's Acceptance Criteria are each traceable to a specific test. | FS-113's three Acceptance Criteria (identical view to native audience; every mutating action rejected; rejection holds bypassing the UI) map directly to `test_observer_view_defaults_to_godview`/`test_white_can_designate_observer_view_to_a_cell`, `test_every_mutating_route_rejects_observer` (parametrized), and the same test's direct-HTTP-call design, respectively. All traceable, no gap. | ✅ Pass |

## Investigation of `BL-0011` (route-guard maintenance-drift risk)

**Question:** has a mutating route added since `IP-1130` shipped (`IP-1151`'s `/roles/assign`, or
this package's own `/observer/view` POST) reopened the gap `BL-0011` predicted?

**Finding: no — both routes remain correctly protected, but by a different mechanism than
`_reject_observer`, and neither has an explicit `cell="observer"` test.**

- **`/roles/assign` (`server.py:216-222`, added by `IP-1151`, postdates this package):** does not
  call `_reject_observer`. Traced to `InProcessSession.assign_role` (`inprocess.py:144-146`):
  `if cell != "white": return Ack(ok=False, ...)`. This is an **allowlist** check (only `"white"`
  passes), strictly stricter than `_reject_observer`'s **denylist** check (only `"observer"` is
  rejected) — it rejects Observer, Blue, Red, and any other non-white value identically. Confirmed
  correct by direct code reading, not by trusting the package's own inline comment (which makes
  this same claim at `server.py:218-220`).
- **`/observer/view` POST (`server.py:199-202`, part of this package itself):** same pattern —
  `InProcessSession.set_observer_view` (`inprocess.py:295-298`) uses the identical
  `if cell != "white"` allowlist check.
- **Test coverage gap (Low, not a functional gap):** `test_session_setup.py`'s
  `test_only_white_cell_can_assign_roles` exercises `cell="blue"`, not `cell="observer"`
  specifically, for `/roles/assign`. No test in the suite calls `/roles/assign` or
  `/observer/view` POST with `cell="observer"` explicitly. Given the check is a simple equality
  test against the literal string `"white"`, this generalizes trivially and the risk of it being
  wrong for `"observer"` specifically is effectively nil — but it is an honest, real gap in
  explicit test coverage, filed as a Low finding below.
- **No other mutating route was found unprotected.** The full `@app.post`/`@app.put`/`@app.delete`
  route list (25 total) was re-derived directly: 22 call `_reject_observer`; 2
  (`/roles/assign`, `/observer/view` POST) use the stricter White-Cell-only allowlist instead; the
  remaining 2 (`POST /api/sessions`, `POST /api/sessions/load_save`) are session-*creation*
  endpoints with no existing session/seat to reject against — Observer rejection does not apply
  before a session (and a seat within it) exists.

`BL-0011` remains an accurate standing description of a *process* risk (a future route could still
be added and forgotten) — its predicted failure mode has not occurred yet, two runs after it was
written.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-6510 (Observer read-only view with no command ability) | `session/inprocess.py` (`set_observer_view`/`get_observer_view`/`observer_designation`), `ui_web/server.py` (`_reject_observer` guard + endpoints), `ui_web/static/app.js`/`index.html` (seat selector) | `tests/test_observer.py` (28 tests) | **Title column still reads "Multi-monitor pop-out windows"** — a pre-existing copy/paste defect the package's own Risks section already flagged and routed to `04-requirements-engineering` (tracked as `BL-0012`). Re-confirmed present this pass; correctly left untouched. `Impl. Package` cell **corrected this pass** to note `VERIFIED`. | ✅ Pass (implementation); ⚠️ pre-existing Title defect noted, not this package's to fix |

## Test run

Commands run, in order, on commit `2a0339413e9ed614c3a53573e21ac945b16d25fc`:

```
python3 -m pytest -q spacesim/tests/test_observer.py -v
  → 28 passed, 1 warning (StarletteDeprecationWarning, unrelated) in 3.92s

python3 -m pytest -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
  → 14 passed

python3 -m pytest -q   (full suite)
  → 566 passed, 3 skipped, 0 failed (counted programmatically — this pytest configuration
    suppresses the usual summary line)
```

Both permanent gates green. Full suite has zero failures, unchanged from the count recorded at
`IP-1120`'s verification (run #13) — no regression introduced between those runs and this one.

## Scope audit

Every file this package's `Files to Modify` names was touched, and no other file was:
`spacesim/session/api.py`, `spacesim/session/inprocess.py`, `spacesim/ui_web/server.py`,
`spacesim/ui_web/static/app.js` (+ `index.html`, an implied companion per the same pattern already
accepted for `IP-1120`/`IP-2010`). Tests: `spacesim/tests/test_observer.py` (new, 28 tests). The
22-route `_reject_observer` guard set matches the package's own claim exactly (re-derived
independently, not counted from the Implementation Summary). No file outside this set was touched.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | Neither `/roles/assign` nor `/observer/view` POST has a test explicitly naming `cell="observer"` — both are covered only indirectly (a generic non-white value, or by code-reading confirmation in this report). The underlying check (`cell != "white"`) is a simple, unconditional equality test that trivially generalizes, so functional risk is effectively nil — but explicit coverage would remove any doubt for a future reader. | Low | Optional: a future maintenance pass to `test_session_setup.py`/`test_observer.py` could add one `cell="observer"` case per route; not blocking, no dedicated run justified. |
| 2 | (Re-confirmed, not new) RTM `FR-6510` Title column still reads "Multi-monitor pop-out windows" — already tracked as `BL-0012`, correctly routed to `04-requirements-engineering`, `DEFERRED`. | Low | Already tracked; no new action from this pass. |

No Critical/High/Medium findings. No test failure, no scope excursion, no unchecked DoD item.
`BL-0011`'s predicted risk investigated directly and found not yet materialized.

## Related

[IP-1130](../packages/IP-1130-observer-read-only-access.md) · [FS-113](../../features/FS-113-observer-read-only-access.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
