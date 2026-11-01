# IP-1075 — Undo Cannot Leave the Exercise: Clock Floor at the Start Epoch and Refused Empty Undo (FR-4310, NFR-1600)

> **Package ID:** IP-1075
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1075](../verification/VR-1075-undo-clock-floor.md), fresh session; READY before that) — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 3). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (bugs, in-progress and critical items only), authorizes this bug-fix package. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4 (the spec); [IP-1074](IP-1074-white-control-correctness.md) (`VERIFIED`; supplies the `[start_epoch, now]` rewind guard and `start_epoch` on `clock_state`); [IP-1103](IP-1103-save-validation-completion.md) (`VERIFIED`; supplies the `final_time >= start_epoch` save check this package pins)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`VR-1074`](../verification/VR-1074-white-control-correctness.md) F1
> **Produces:** an `undo` that can never put the sim clock before `start_epoch`, and an `undo` with nothing to undo that is a refused no-op.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md)
> **Related Topics:** [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py), [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design, one Medium bug, no new feature). Prose only; no code in this document.*

---

## Package ID

IP-1075 (FS-106 → `IP-107x`; `IP-1072`, `IP-1073`, `IP-1074` taken).

## Title

Undo clock floor: `undo` never leaves the exercise span; an empty undo is refused.

## Objective

**Reproduction (read-only, this worktree, 2026-10-24).** Using `SessionManager(load_vignette(<first library id>))`, `start()`, `set_clock(False)`:

| Step | Observed |
|---|---|
| fresh session (`start_epoch` 1899784800000000, 0 log entries), `undo_last()` | `sim.clock.now == 0` (1970) |
| `step(300)`, `step(100)` (log holds one `bus_tick`), `undo_last()` | `now - start_epoch == -1899784800000000` (i.e. `now == 0`); further undos stay at 0 |
| then `rewind_to(start_epoch)` | `ValueError`: target outside `[start_epoch, now=0]` (HTTP 400 at the route) |
| `undo_last(len(log)+5)` | `now == 0` |
| `save_state()` then `SessionManager.from_state()` of that state | loads, `now == 0`, `start_epoch` intact |

**Cause (file:line, tree `ff4b0b2`).**

- `spacesim/engine/simulation.py:138-143` `Simulation.undo_last`: after dropping the last `n` entries (line 141) it computes `stop = self.eventlog.entries[-1].sim_time if self.eventlog.entries else 0` (line 142) and calls `_rebuild(stop_time=stop)`. With no entries left (an empty log to begin with, or the last remaining entry dropped) the literal `0` is the stop time. It ignores the initial state's own time (`_initial_state`, line 146, whose `now` is the exercise start).
- `_rebuild` (lines 145-154) then sets `world.now`, `self.clock.now` to that value (lines 151-153) and drops the scheduler.
- `spacesim/session/manager.py:492-497` `SessionManager.undo_last` passes straight through (`self.sim.undo_last(n)`, `_rebind()`, re-anchor of the lazy clock at the new `now`) with no check against `ctx.start_epoch`. Unlike `rewind_to` (lines 475-490, `lo <= t <= hi`, `IP-1074`), undo has no guard, and unlike `rewind_to` it does not re-arm the bus-tick schedule (`_arm_schedule`), so after undo the pending ticks are gone too (see Design Decision 3).
- `spacesim/session/inprocess.py:228-233` `InProcessSession.undo_last` returns `Ack()` unconditionally, and `ui_web/server.py:494-497` routes `/undo` to it, so the damaged state is reported as success.
- Knock-on: the lazy clock re-anchors at `now == 0` (manager lines 496-497) and then advances from 1970; `rewind_to(start_epoch)` is refused by the `IP-1074` guard (`hi = 0 < lo`); the next `GET /save` carries `final_time` before `start_epoch`, which `IP-1103`'s `_check_final_time_span` (manager lines 1090-1097) refuses on reload.
- The defect predates `IP-1074` (identical on its parent commit); `IP-1074` made it visible by turning "rewind to start" into a 400 in this state (`VR-1074` F1, Medium).

**Other callers that can produce `now < start_epoch` (audited, same pass).**

| Caller | Can it produce `now < start_epoch`? |
|---|---|
| `SessionManager.undo_last` / `Simulation.undo_last` | **Yes** (this bug). |
| `SessionManager.rewind_to` | No; guarded by `IP-1074` (`manager.py:475-490`). `Simulation.rewind_to` (`simulation.py:124-136`) itself is unguarded but its only session caller is guarded; a direct engine call with `t < start` would also reach `stop_time=t`. Out of scope, noted. |
| `advance_to` / `step` / `_catch_up_locked` | No; `Simulation.advance_to` (`simulation.py:70-73`) raises on a backwards target and catch-up only advances when `target > now`. A negative `step(dt)` hits that raise. |
| `SessionManager.from_state` / `load_save` | Not for a saved state that passes `validate_save` (`IP-1103` rejects `final_time < start_epoch`, manager lines 1090-1097); but `from_state` itself calls `_rebuild(stop_time=state["final_time"])` unconditionally, so a caller that bypasses `validate_save` (the unit-level repro above did) loads a 1970 clock. Regression test pins the validated path; a belt-and-braces floor is optional (Decision 4). |
| `aar.state_at` / `state_at_time` / `PlaybackSession` | Read-only replays, not the live clock; unaffected. |

## Requirements Covered

| ID | How |
|---|---|
| `FR-4310` | Undo is a White clock control; like rewind it moves the clock only inside the exercise span `[start_epoch, now]`. |
| `NFR-1600` | A request that cannot be honoured (nothing to undo, or `n < 1`) is refused with a reason and changes nothing, instead of being accepted and damaging the session. |
| `FR-7220` | Pinned only: a save taken after any undo sequence satisfies the save-validity span and reloads (no code change expected). |

No requirement leaf states undo's postcondition. The behaviour is derived from `FR-4310` ("rewind the simulated clock"), the `IP-1074` exercise-span rule (itself derived from `FR-7330`/`FR-7410`), and `FR-1120`/`FR-1130` (an exercise has a defined start epoch). Recommendation routed to `04`: add a sentence to `FR-4310` (or a leaf) stating "undo and rewind never move the clock before the exercise start; an undo with no history is refused". It does not block.

## Architecture Components

`engine/simulation.py::Simulation.undo_last`/`_rebuild` (the rewind/undo primitive; deterministic, no wall clock). `session/manager.py::SessionManager.undo_last` (guard, floor, re-arm, lazy-clock re-anchor). `session/inprocess.py::InProcessSession.undo_last` (turns a refusal into `Ack(ok=False)`). `ui_web/server.py` `/undo` route (maps the refusal to HTTP 400, as `/rewind` does). Load-bearing invariants touched: deterministic core (the fix reads only the initial state, no wall clock, no global RNG); session lock (the guard runs under `_locked`).

## Interfaces

- `POST /api/sessions/{sid}/undo` (body `{"n": int}`): unchanged request. New response: `Ack(ok=false, reason=...)` with HTTP 400 when there is nothing to undo or `n < 1`; otherwise unchanged success.
- `SessionManager.undo_last(n)`: raises `ValueError` before any state change when the event log is empty or `n < 1`; otherwise clamps the landing time to at least `start_epoch`.
- `Simulation.undo_last(n)`: signature unchanged; its empty-log landing time becomes the initial state's time rather than `0`.
- `clock_state()`: unchanged (already carries `start_epoch` since `IP-1074`).

### Design Decisions

1. **Behaviour (the owner-facing choice).** Of the two options in the brief (refused no-op, or return to `start_epoch`), use **both, each for its own case**: an undo with **nothing to undo** (empty event log, or `n < 1`) is a **refused no-op** (`ValueError` in the manager, `Ack(ok=False)` in the session layer, 400 at the route, state and clock untouched); an undo that **drops every remaining entry** (`n >= len(log)`, log non-empty) **succeeds and lands on `start_epoch`**, the exercise's first instant, never epoch 0. A partial undo keeps today's landing time (the sim time of the last surviving entry), unchanged.
2. **Where the fix lives.** Two layers, same value. Engine: `Simulation.undo_last` falls back to the initial state's own `now` (read from `_initial_state`, deterministic) when no entries survive, so every direct engine caller (AAR branch, tests) is safe. Session: `SessionManager.undo_last` raises the refusal and takes `max(landing, start_epoch)` as a floor assertion, so the guard is stated next to the `IP-1074` rewind guard. The engine fix alone would leave the "undo on an empty log" case reporting success; the session guard alone would leave the engine primitive wrong.
3. **Re-arm after undo.** `rewind_to` calls `_arm_schedule` after a rebuild because the scheduler is dropped; `undo_last` does not, so after any undo the bus-tick/inject schedule is empty until the next `start`/`rewind`. The build must **check first** (test: step, undo, step again, assert `bus_tick` entries resume) and, if ticks do not resume, re-arm exactly as `rewind_to` does using the landing time. This is in scope only because it is the same function and the same "undo leaves a broken session" symptom; if the check shows ticks resume (for example via a lazy path), record that and add only the pinning test.
4. **`from_state` floor.** Do not add a second validation to `from_state` (it is the trusted path after `validate_save`; `IP-1103` owns the check). Add only a regression test that a validated save taken after undo-to-start reloads, and that a save with `final_time` below the start is still refused by `validate_save`.
5. **Not decided here.** Whether undo should pause the lazy clock (same open question as rewind in `IP-1074` Decision 4): the running state is preserved as today.

## Files to Create

- `spacesim/tests/test_undo_clock_floor.py` — the new regression module.

## Files to Modify

- `spacesim/engine/simulation.py` — `undo_last` empty-log landing time (Decision 2). No other engine change; `rewind_to` untouched.
- `spacesim/session/manager.py` — `undo_last` guard, floor, optional re-arm (Decisions 1-3).
- `spacesim/session/inprocess.py` — `undo_last` catches the `ValueError` and returns `Ack(ok=False, reason=...)`, mirroring `rewind_to` (lines 218-226).
- `spacesim/ui_web/server.py` — `/undo` route: a refused `Ack` becomes HTTP 400, using whatever pattern `/rewind` uses (verify at build time).
- `spacesim/static` console: check whether the toolbar/palette Undo handler surfaces a refusal; reuse the `IP-1073` refusal wiring if present; do not add a new UI surface.
- Existing tests that call `undo_last` or `/undo` on an empty log (grep `undo` in `spacesim/tests/`, including `test_white_only_controls.py`, `test_white_control_correctness.py`, `test_web.py`): any that relied on an empty-log undo succeeding are updated to expect the refusal, each noted in the completion note.

## Implementation Tasks

1. Write the failing tests below first; run them and record that each failed for the stated reason.
2. Engine: in `Simulation.undo_last`, replace the literal-zero fallback with the initial state's `now`.
3. Manager: reject an empty log or `n < 1` with `ValueError` before mutating; compute the landing time through the engine, assert it is `>= start_epoch`; check and, if needed, re-arm the schedule (Decision 3); keep the lazy-clock re-anchor.
4. Session and route: translate the refusal as above; leave `Observer`/seat checks untouched (`IP-1068`/`IP-1130` already guard `/undo`).
5. Update the existing tests the audit finds; regenerate the RTM Test column (`python3 -m pytest --origin-report=rtm`); run the full suite, then the permanent gates.
6. Update the documentation listed below and the Master Build Plan row to `COMPLETE`.

## Tests to Add

All in `spacesim/tests/test_undo_clock_floor.py`, test-first, each tagged `@pytest.mark.verifies(...)` (module `pytestmark` for the common IDs). Origins: `FR-4310`, `NFR-1600`, plus `FR-7220` on the save case.

1. Fresh started session (empty log): `undo_last()` raises `ValueError`; `now` and the log are unchanged (`FR-4310`, `NFR-1600`). Via HTTP: `/undo` answers 400 and `GET /clock` is unchanged.
2. `n = 0` and `n = -1`: refused, nothing changed (`NFR-1600`).
3. Step so the log holds one entry, `undo_last()`: succeeds, `now == start_epoch` exactly, never 0 (`FR-4310`) — fails today with `now == 0`.
4. `undo_last(len(log) + 5)` (over-large `n`): lands on `start_epoch`, log empty (`FR-4310`).
5. After the case-3 undo, `rewind_to(start_epoch)` succeeds (`200` over HTTP) — the exact `VR-1074` F1 symptom (`FR-4310`, `NFR-1600`).
6. Partial undo (two or more entries, drop one): lands on the sim time of the last surviving entry, which is `>= start_epoch`; unchanged behaviour pinned (`FR-4310`).
7. Property-style invariant: over a seeded random sequence of `step`/`undo_last`/`rewind_to`/`advance_to` calls (refusals tolerated), `start_epoch <= now` after every call (`FR-4310`, `NFR-1600`).
8. Step, undo, step again: `bus_tick` entries resume after the undo (Decision 3); expected to fail first only if the schedule is not re-armed.
9. Running clock: with the lazy clock running, an undo to start re-anchors at `start_epoch` and a following `catch_up` advances from there, not from 0 (`FR-4310`).
10. `engine/simulation.py` unit: `Simulation.undo_last` on an empty log leaves `clock.now` equal to the initial state's time (an engine-level case, `IP-1075` own DoD tag).
11. Save: after undo-to-start, `save_state()` passes `validate_save` and reloads with `now == start_epoch`; a hand-built state with `final_time < start_epoch` is still refused (`FR-7220`).
12. Observer and non-White seats are still refused 403 on `/undo` (regression, no behaviour change; `FR-4320`).

## Documentation Updates

- `CLAUDE.md`: the `session/` bullet notes undo's floor and refusal (one sentence beside the `IP-1074` rewind range).
- `docs/training/12-white-cell-manual.md` clock section and API reference: undo past the first event returns to the exercise start; undo with no history is refused. Use `docs/training/15-manual-traceability.md` §15.1 for the sections to touch; if `08-training-manual-authoring` must do them, list them in the completion note.
- RTM Test column regenerated (never hand edited); `FS-106` `Referenced By`; Master Build Plan row and tally; `packages/INDEX.md`; `ROADMAP.md`; this header.
- Not edited here: `FR-4310` text (recommendation above, `04`).

## Definition of Done

- Tests 1-12 exist, were seen failing for the stated reason (cases 1-5, 8-10 expected to fail before the change), and pass.
- No sequence of `undo_last`/`rewind_to`/`advance_to`/`step` leaves `now < start_epoch` (test 7).
- `/undo` on an empty log is 400 with nothing changed; undo to the beginning lands on `start_epoch`.
- A save taken after undo reloads (test 11).
- The full suite, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py` and `test_test_origins.py` are green; RTM regenerated in the same commit.
- Documentation above updated; row `COMPLETE` in the Master Build Plan.

## Verification Checklist

- [ ] Reproduce the pre-fix symptom (clock at 1970 after an undo) on the parent commit and see it gone.
- [ ] Every test names its origin; each failing-first case recorded.
- [ ] `engine/` still imports no UI/transport code and reads no wall clock (`test_import_guard.py`).
- [ ] `test_determinism.py` green (replay byte-identical; the landing-time change does not alter replay of retained entries).
- [ ] `rewind_to`, `advance_to`, `from_state` behaviour unchanged except as stated.
- [ ] The existing-test edits are listed and none weakens a check.
- [ ] `test_doc_integrity.py` and `test_test_origins.py` green; no allow-list grew.

## Dependencies

`IP-1074` (guard pattern, `start_epoch` on `clock_state`), `IP-1103` (save span check), both `VERIFIED`. No downstream blockers. File-conflict ordering only: build after `IP-1335` and `IP-1334` if those are still open (they touch test modules, not these source files).

## Risks

- **Existing tests that undo an empty log** may now fail; the audit step finds them. Mitigation: edit to expect the refusal and list each.
- **Engine behaviour change** (landing time on an empty log) is observable by AAR branch code; the AAR replay paths use `state_at`, not `undo_last`, so none is expected. Test 10 and the determinism gate cover it.
- **Re-arm after undo** (Decision 3) could double-queue ticks if the schedule is in fact retained; the test-first check at build time is the control.
- **Landing time for partial undo** is the last surviving entry's time, which can be earlier than the pre-undo clock by more than the dropped entries; unchanged, noted for the owner, not a bug here.

## Rollback Considerations

Revert the commit. No data format, save format or requirement text changes; saves written before or after are interchangeable. Reverting restores the 1970-clock defect and the `IP-1074` "rewind to start" 400 after an undo.
