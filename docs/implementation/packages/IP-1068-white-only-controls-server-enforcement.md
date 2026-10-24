# IP-1068 — White-Only Controls Enforced at the Server Boundary (FR-4310, FR-4320)

> **Package ID:** IP-1068
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1068](../verification/VR-1068-white-only-controls-server-enforcement.md), fresh session; READY before that) — authored 2026-10-23 by `07-implementation-planning`, pipeline run #219. Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner decided *what* to do (`BL-0307`: "Enforce server-side"); the master build plan row records the build as owner-authorized per MSTR-006 §3, and the `run #230` ledger note records the owner's go-ahead of 2026-10-23. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4 (the spec);
> [IP-1060](IP-1060-white-cell-dashboard.md) (clock authority, as recorded),
> [IP-1130](IP-1130-observer-read-only-access.md) (the Observer refusal this sits beside),
> [IP-1151](IP-1151-seat-role-assignment.md) (seat assignment) — all `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0307`
> **Produces:** a server that refuses every White Cell control unless the request names the
> `white` seat, and a test per control proving it.
> **Feature Reference:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4
> (`FEAT-4300` `FR-4310`, `FR-4320`)
> **Related Topics:** requirements review R1
> ([`reviews/requirements-update-gds-ladder-batch.md`](../../reviews/requirements-update-gds-ladder-batch.md));
> feature review F-24; GDS-09 §4 and OQ1

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design). `FR-4310` was recorded verified by `IP-1060`/VR-1060 but is
not enforced (requirements review R1, High); this package builds it and adds the missing tests.*

---

## Package ID

IP-1068.

## Objective

**As built at `1111968`**, `spacesim/ui_web/server.py` guards the White Cell controls only with
`_reject_observer(cell)` (line 330), which refuses `cell == "observer"` and accepts everything else,
including `blue`, `red` and a missing seat. After this package, every control below refuses any
request that does not name the `white` seat, before the request reaches `SessionAPI`, and leaves the
session unchanged (FS-106 v2.4 System Behaviour).

| Control | Route (`server.py`, line at `1111968`) | Leaf | Today |
|---|---|---|---|
| Clock rate/pause | `POST /api/sessions/{sid}/clock` (429) | FR-4310 | Observer refused only |
| Step | `POST …/step` (450) | FR-4310 | Observer refused only |
| Advance | `POST …/advance` (455) | FR-4310 | Observer refused only |
| Rewind | `POST …/rewind` (460) | FR-4310 | Observer refused only |
| Undo | `POST …/undo` (465) | FR-4310 | Observer refused only |
| Session start | `POST …/start` (445) | FR-4320 | Observer refused only |
| Parameter set | `POST …/param` (440) | FR-4320 | Observer refused only |
| Inject fire | `POST …/inject` (470) | FR-4320 | Observer refused only |
| TLE add | `POST …/force/tle` (487) | FR-4320 | Observer refused only |
| Bulk import | `POST …/force/bulk_import` (492) | FR-4320 | Observer refused only |
| Ground-asset add | `POST …/force/ground` (504) | FR-4320 | Observer refused only |
| Save load | `POST /api/sessions/load_save` (1022) | FR-4320 | No seat read at all |
| Seat assignment | `POST …/roles/assign` (357) | FR-4320 | Already refused in `InProcessSession.assign_role` (body `cell`); untested |
| Observer designation | `POST …/observer/view` (340) | FR-4320 | Already refused in `InProcessSession.set_observer_view` (body `cell`); untested |

## Requirements Covered

FR-4310, FR-4320 — matching FS-106 v2.4's additions for `FEAT-4300`.

## Architecture Components

C2 Session/Application Layer's HTTP boundary (`ui_web/server.py`) only. No engine, session-layer
or client change: the browser already sends its seat as `?cell=` on every mutating request
(`static/app.js` `api.post`, line 44, defaulting to `white`).

## Interfaces

INT-0002 (the HTTP surface): the listed routes gain a refusal (HTTP 403 with a reason) for any
request not naming `white`. Accepted requests are unchanged in shape and effect.

## Files to Create/Modify

- **Modify** `spacesim/ui_web/server.py` — add one White-only guard helper beside
  `_reject_observer` (it refuses with 403 and a reason naming the control unless `cell == "white"`),
  apply it to the eleven routes in the table that currently call `_reject_observer`, and add a
  `cell` query parameter plus the guard to `load_save`. `roles/assign` and `observer/view` are not
  changed (their check already exists; their refusal stays an `Ack(ok=False)` with a reason, which
  satisfies "refused, with a reason").
- **Create** `spacesim/tests/test_white_only_controls.py` — the new tests (below).
- **Modify** (calling convention only — add `?cell=white` to requests that act as White; no
  assertion changes) the existing tests that call these routes without naming a seat. Counted at
  `1111968`: `test_web.py` (44 call sites), `test_vignette_creator_ui.py` (13),
  `test_defensive_audit_2026.py` (7), and one each in `test_future_work.py`,
  `test_observe_order_remediation.py`, `test_observer.py`, `test_order_param_hardening.py`,
  `test_space_weather_index.py`. Re-count at implementation time; any other caller found is in
  scope on the same terms.
- **Modify** `docs/requirements/03-requirements-traceability-matrix.md` (`FR-4310`, `FR-4320` rows:
  package and test cells), `docs/training/12-white-cell-manual.md` and
  `docs/training/13-blue-cell-manual.md` / `14-red-cell-manual.md` only if they say a player seat
  can use a White control (check §15.1 of `docs/training/15-manual-traceability.md`), and
  `CLAUDE.md`'s LAN trust-model paragraph (one sentence: White Cell controls are refused to other
  seats at the same trust level as the Observer refusal).

## Implementation Tasks

1. Run the suite; record the baseline counts.
2. Write `test_white_only_controls.py` first (Tests to Add); run it and record which tests fail
   (expected: every `blue`/`red`/no-seat case for the eleven routes and `load_save`).
3. Add the guard helper and apply it to the twelve routes. The guard runs after the unknown-session
   check (`_require`), so an unknown session still reports 404 first (FS-106 v2.4 Error Handling).
4. Update the existing tests' calling convention (Files to Modify) until the full suite passes; do
   not change any assertion. If a test turns out to depend on a non-White seat using a White
   control, stop and report it — that is a behavior question, not a fixture fix.
5. Run the full suite and both permanent gates; update the RTM rows, `CLAUDE.md` and any manual
   section found in task 4 of Documentation Updates.

## Tests to Add

All in `spacesim/tests/test_white_only_controls.py`, through the FastAPI `TestClient`, each on a
fresh session of a shipped vignette:

| Test | Verifies (marker IDs) | Asserts |
|---|---|---|
| Clock controls refused (parametrized over `clock`, `step`, `advance`, `rewind`, `undo` × seats `blue`, `red`, `observer`, none) | `FR-4310` | 403; sim time, clock state and event-log length unchanged |
| Clock controls accepted for `white` (same five) | `FR-4310` | success, and the expected state change |
| `FR-4320` controls refused (parametrized over `start`, `param`, `inject`, `force/tle`, `force/bulk_import`, `force/ground` × the four non-White cases) | `FR-4320` | 403; started flag, parameter value, asset set and event-log length unchanged |
| `FR-4320` controls accepted for `white` (same six) | `FR-4320` | success and the expected change |
| Save load refused for non-White, accepted for White | `FR-4320` | 403 and session count unchanged; then success and one new session |
| Seat assignment and Observer designation refused for `blue`/`red` | `FR-4320` | `ok: false` with a reason; staffing report and Observer designation unchanged |
| Unknown session still 404 for a non-White seat | `FR-4320` | 404, not 403 |

Each test carries `@pytest.mark.verifies(...)` with the IDs shown (the marker may warn until FS-133's
registration lands; apply it anyway).

## Documentation Updates

- RTM rows `FR-4310` and `FR-4320`: package `IP-1068`, tests `test_white_only_controls.py`, and the
  "not met as built" note on `FR-4310` replaced by the verification reference once `09` passes (the
  RTM note text is `04`'s; `08` updates the cells, not the requirement).
- `CLAUDE.md` LAN trust model: one sentence (Files to Modify).
- Training manuals: only where they contradict the new behavior (Files to Modify).

## Definition of Done

1. Every route in the Objective table refuses a request naming `blue`, `red`, `observer`, or no
   seat, with the session unchanged; `roles/assign` and `observer/view` refuse `blue`/`red` with a
   reason.
2. The same requests naming `white` behave exactly as before.
3. `test_white_only_controls.py` exists with the tests above, each tagged; the failing-first run is
   recorded in the package's completion note.
4. No existing test assertion changed; only calling conventions.
5. Full suite green; `test_determinism.py` and `test_import_guard.py` green, run by name.
6. RTM, `CLAUDE.md` and any affected manual section updated.

## Verification Checklist

- [ ] For each of the 12 guarded routes, a non-White request returns 403 and the state checks in
      the test hold (read the tests, and run them).
- [ ] `roles/assign` and `observer/view` refusals are covered by a test.
- [ ] `git diff` of existing test files shows only added `cell=white` (or equivalent) arguments.
- [ ] `server.py` diff touches only the guard helper, the twelve routes and `load_save`'s parameter.
- [ ] Full suite: pass counts recorded; `python3 -m pytest spacesim/tests/test_determinism.py
      spacesim/tests/test_import_guard.py` green.
- [ ] Every new test carries a `verifies` marker naming `FR-4310` or `FR-4320`.
- [ ] RTM `FR-4310`/`FR-4320` rows name `IP-1068` and the new test file.

## Dependencies

`IP-1060`, `IP-1130`, `IP-1151` — all `VERIFIED`. No package depends on this one.

## Risks

- **Hidden non-White callers.** A script, tool or test that drives White controls without naming a
  seat breaks. Mitigation: task 4's re-count and the full suite; the browser client always names its
  seat. `tools/record_walkthrough.py` and `tools/render_manual.py` drive the browser, so they send
  the seat.
- **A flow where a player seat legitimately uses a listed control** (for example, a Red seat
  stepping the clock in a solo hot-seat run). None is known; if one appears it is a requirements
  question for `04`, not a fixture to bend (task 4).
- **Trust-model overclaim.** The check is client-asserted; documentation must not call it
  authentication (FS-106 v2.4 Security Considerations).

## Rollback Considerations

Revert the commit: the guard is additive at the route boundary and the test calling-convention
changes are harmless if reverted together. No data, save format or schema changes.
