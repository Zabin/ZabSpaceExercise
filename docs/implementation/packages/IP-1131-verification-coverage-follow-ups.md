# IP-1131 — Verification-Coverage Follow-Ups: Observer Rejection, SSN Rewind Parity, Training Source Anchors (BL-0023, BL-0024, BL-0259, BL-0260)

> **Package ID:** IP-1131
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-17 by `07-implementation-planning`, pipeline run #166.
> Every dependency is `VERIFIED`. **Authorization (MSTR-006 §3):** falls under the project owner's
> standing pre-authorization of 2026-10-11 for the packages this iteration reaches.
> **Dependencies:** [FS-113](../../features/FS-113-observer-read-only-access.md) /
> [IP-1130](IP-1130-observer-read-only-access.md), [FS-115](../../features/FS-115-session-setup.md) /
> [IP-1151](IP-1151-seat-role-assignment.md), [FS-102](../../features/FS-102-command-scheduling.md)
> v1.1 / [IP-1040](IP-1040-sda-tasking.md), and `NFR-3400` (amended 2026-10-17) — all packages
> `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0023`, `BL-0024`, `BL-0259`, `BL-0260`
> **Produces:** four regression tests for behaviour that is already correct but unproven by a test.
> **Feature Reference:** FS-113, FS-115, FS-102 v1.1; `NFR-3400`.
> **Related Topics:** [`spacesim/tests/`](../../../spacesim/tests/)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Test-only package (no production code), part of the owner-prioritized `DEFERRED` backlog clearance
(2026-10-17). The TWBS records why four FS slices share one package: they share a test-only seam
and no production file.*

---

## Package ID

IP-1131 (FS-113 → `IP-113x`; the Observer tests are the first item).

## Title

Verification-coverage follow-ups.

## Objective

Each item is behaviour that verification confirmed correct by reading, with no test:

1. **`BL-0023`** — `POST /roles/assign` and `POST /observer/view` are protected by a White-only
   check in `session/inprocess.py`, not by `_reject_observer`; no test sends `cell="observer"` to
   either.
2. **`BL-0024`** — `InProcessSession.assign_role` is tested with `cell="blue"` only
   (`test_only_white_cell_can_assign_roles`), not `cell="observer"`.
3. **`BL-0259`** — `FR-3310`'s Acceptance Criterion for an SSN request: rewinding to before an SSN
   collection returns the request to its pre-execution state, as a command does. No test.
4. **`BL-0260`** — `NFR-3400` (amended 2026-10-17) names an automated test that every code path and
   symbol a `docs/training/` `> Sources:` footer names still exists. A pre-check at `de4f732` found
   67 footers, 174 resolvable paths and 278 symbols, none missing.

## Feature Reference

FS-113 (Observer cannot mutate), FS-115 (White-only role assignment), FS-102 v1.1 (`FR-3310`),
`NFR-3400` verification method.

## Requirements Covered

`FR-6510` (1, 2), `FR-4210` (2), `FR-3310` (3), `NFR-3400` (4).

## Architecture Components

Test suite only (`spacesim/tests/`). No production component changes.

## Interfaces

None changed. Tests exercise INT-0001 (HTTP) for 1, INT-0006 for 2, INT-0008/INT-0009/INT-0010 for 3.

### Design Decisions

1. **Observer tests** go in `spacesim/tests/test_observer.py` (HTTP, like the existing
   `_MUTATING_ROUTES` table) and `spacesim/tests/test_session_setup.py` (direct `assign_role`).
2. **SSN rewind parity** goes in `spacesim/tests/test_ssn.py`: submit an SSN request and a command
   in the same session, advance past the collection, rewind to before it, and assert both are back
   to their pre-execution state (the SSN request pending again, its track delivery absent).
3. **Source-anchor test** goes in a new `spacesim/tests/test_training_sources.py`: parse every
   `> Sources:` footer (the line and its `> ` continuation lines) in `docs/training/*.md`; for each
   backticked file path, resolve it (as written, or under `spacesim/` and its subpackages, as the
   footers abbreviate); assert the file exists unless it is a glob; for each backticked identifier
   that follows the path in the same `·`-separated segment, assert its last dotted part occurs in
   that file. Add a self-test on a synthetic footer naming a missing symbol, so the checker is shown
   to fail. Skip URL and route segments (`/api/...`).

## Files to Create

- `spacesim/tests/test_training_sources.py`.

## Files to Modify

- `spacesim/tests/test_observer.py`, `spacesim/tests/test_session_setup.py`,
  `spacesim/tests/test_ssn.py` (new test functions only).

## Implementation Tasks

1. Write each test; record which pass on arrival (all are expected to, since the behaviour is
   correct) and the synthetic-failure self-test for item 4.
2. If any test fails, stop: that is a real defect — record it as an Outstanding Issue and route it
   (`00-intake`), do not change production code here.
3. Full suite + both gates.

## Tests to Add

As above: two Observer HTTP tests, one direct `assign_role(..., "observer", ...)` test, one SSN
rewind-parity test, the source-anchor test plus its self-test. Permanent gates:
`test_determinism.py`, `test_import_guard.py`.

## Documentation Updates

- RTM Test cells for `FR-6510`, `FR-4210`, `FR-3310`, `NFR-3400`.
- `docs/training/15-manual-traceability.md` §15.3/§15.4 mention the new automated gate — a
  `08-training-manual-authoring` edit (file the manual impact).
- `strategic-assumptions-register.md` A12 can note the mitigation is in place — `01-vision`'s file
  (route, do not edit).

## Definition of Done

- [ ] All tests pass; the self-test proves the anchor checker fails on a broken footer.
- [ ] No production file changed (`git show --stat` lists tests and ledgers only).
- [ ] Full suite and both gates green; RTM and ledgers updated; follow-ups filed.

## Verification Checklist

- [ ] Confirm each test exercises the named route/method with the named cell.
- [ ] Break a footer symbol in a scratch copy and confirm `test_training_sources.py` fails.
- [ ] Full suite and both gates by name.

## Dependencies

Named packages all `VERIFIED`. Independent of the rest of this tranche.

## Risks

- The anchor test becomes a permanent gate on documentation: a future code rename now fails the
  suite until the footer moves. That is the intent (A12), but it couples doc upkeep to CI.
- Footer formats vary; the parser must stay tolerant (Design Decision 3) rather than force a
  reformat of the corpus.

## Rollback Considerations

Delete the new test functions/module. No production effect.
