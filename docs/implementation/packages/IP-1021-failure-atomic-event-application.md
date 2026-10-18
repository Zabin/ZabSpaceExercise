# IP-1021 — Failure-Atomic Event Application: a Raising Handler Leaves No Trace in Live State (ADR-0038)

> **Package ID:** IP-1021
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-17 by `07-implementation-planning`, pipeline run #166.
> Every dependency is `VERIFIED`. **Authorization (MSTR-006 §3):** falls under the project owner's
> standing pre-authorization of 2026-10-11 for the packages this iteration reaches (same precedent
> as `IP-1310`/`IP-1311`/`IP-1320`). Authoring the package is not itself the authorization.
> **Dependencies:** [ADR-0038](../../architecture/adr/ADR-0038-failure-atomic-event-application.md)
> (the decision); [FS-102](../../features/FS-102-command-scheduling.md) v1.1 (scheduled execution);
> [IP-1020](IP-1020-command-scheduling.md) (`VERIFIED`).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0264` (from `BL-0227`)
> **Produces:** an event loop in which a handler exception can no longer make live state differ
> from replayed state.
> **Feature Reference:** [FS-102 — Command Scheduling](../../features/FS-102-command-scheduling.md)
> (`FEAT-3300`, the shared scheduler every event rides)
> **Related Topics:** [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py),
> [`spacesim/engine/handlers.py`](../../../spacesim/engine/handlers.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py) (`_rebind`)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design) implementing ADR-0038, part of the owner-prioritized
`DEFERRED` backlog clearance (2026-10-17).*

---

## Package ID

IP-1021 (FS-102 → `IP-102x`; `IP-1020` is the as-built scheduling record, `IP-1021` the first
remediation slice).

## Title

Failure-atomic event application: a handler that raises mid-advance is rolled back to the replayed
state, logged as a no-op failure record, and the advance continues.

## Objective

As built (`engine/simulation.py::Simulation.advance_to`, verified at `e1e721c`), each due event is
popped, its handler applied to the live world with the live RNG, and only then appended to the
event log. If the handler raises, the event is lost, any mutation or RNG draw it made before
raising stays in live state but is never reproduced by replay, and the `advance_to` call raises.
That is a live/replay divergence against invariant 1 (`BL-0227`). ADR-0038 decides the remedy:

1. restore the live world and RNG to exactly what the event log reproduces before that event,
   keeping the scheduler's other pending events;
2. append a failure record in the event's place (a new event kind whose handler is a no-op,
   carrying the original kind, actor, sim time, payload, and the exception class and message);
3. continue the advance to its target.

## Feature Reference

[FS-102](../../features/FS-102-command-scheduling.md) v1.1 — Requirements Implemented (`FR-3310`:
one deterministic scheduler for every kind). ADR-0038 is the binding decision.

## Requirements Covered

| ID | How |
|---|---|
| `FR-1120` (determinism) | Live state equals replayed state on the failure path too. |
| `NFR-1600` (robustness) | A raising handler no longer aborts the advance. |
| `NFR-2600` (complete action log) | The failure is recorded, not lost. |

ADR-0038 names these leaves; no requirement is added (ADR-0038 Consequences: no new leaf).

## Architecture Components

- **C1 Simulation Engine** (`engine/simulation.py`, `engine/handlers.py`): the behaviour change.
- **C2 Session Layer** (`session/manager.py`): must keep its live references valid after a
  rollback (see Design Decision 2). No other behaviour change.

The import guard is unaffected: the engine still imports no UI/transport code, reads no wall clock
and uses no global RNG.

## Interfaces

- **INT-0008** (Session → Engine clock/scheduler/event log): `advance_to` no longer raises for a
  handler exception; the event log may now contain failure records.
- **INT-0014** (AAR/replay reads): replaying a failure record is a no-op, so every reconstruction
  read is unchanged in shape.

### Design Decisions

1. **Rollback by deterministic rebuild, on the failure path only.** Reuse the reconstruction
   `_rebuild` already performs (initial state + seed + logged entries), but **without** resetting
   the scheduler or the clock: a failure is not a rewind. The success path is untouched (no copy
   per event; ADR-0038 rejected that).
2. **Keep live references valid.** `SessionManager` holds `self.world` and `self.osys.world`
   pointing at `Simulation.world`, re-pointed by `_rebind()` after a rewind. A rollback that
   replaces the world object would leave them stale mid-advance. The implementation must either
   restore the rebuilt state **into the existing world object** (preferred: no session change), or
   give `Simulation` a rollback callback that `SessionManager` registers to call `_rebind()`. The
   same applies to the RNG object if anything outside `Simulation` holds it (check by grep).
3. **The failure record.** A new event kind (for example `handler_error`) registered in
   `DEFAULT_HANDLERS` with a no-op handler, so replay, rewind, undo, save/resume and AAR all treat
   it as an ordinary logged event that changes nothing. Its payload is plain data (strings and
   the original payload), so the save file stays JSON-serializable. Its `sim_time` is the failed
   event's time; its actor is the failed event's actor.
4. **What is not covered.** State a handler mutates outside `WorldState` and the RNG (for example
   an `OrderSystem` booking dict) is not restored. Replay does not reproduce such state either, so
   this is not new divergence; record it in the test module's docstring as a known limit. No alarm
   or UI surface is added (ADR-0038 Consequences).

## Files to Create

- `spacesim/tests/test_failure_atomic_events.py`.

## Files to Modify

Checked against the tree at `e1e721c`:

- `spacesim/engine/simulation.py` — `Simulation.advance_to` (the pop → `_apply` → `append` loop)
  gains the failure path; `_rebuild` is reused or factored so the rollback can rebuild without
  touching `self.scheduler`/`self.clock`.
- `spacesim/engine/handlers.py` — `DEFAULT_HANDLERS` gains the no-op failure-record kind.
- `spacesim/session/manager.py` — only if Design Decision 2's callback option is chosen
  (`_rebind`).

## Implementation Tasks

1. Write the failing tests below first (they fail today: the advance raises, live ≠ replay).
2. Add the no-op failure-record handler to `DEFAULT_HANDLERS`.
3. In `advance_to`, catch an exception from `_apply`; roll back per Design Decisions 1–2; append
   the failure record; continue with the remaining due events.
4. Run the full suite and both permanent gates.
5. Update `CLAUDE.md`'s code-map line for `engine/simulation.py` (failure-atomic advance).

## Tests to Add

In `spacesim/tests/test_failure_atomic_events.py`, with a test-only handler registered on a fresh
`Simulation` (and one `SessionManager`-level case):

1. A handler that mutates the world, draws from the RNG, then raises: after `advance_to`, the live
   world's `model_dump()` and the RNG state equal those of `replay()` of the resulting log.
2. `advance_to` does not raise, and a later due event in the same advance still fires.
3. Another pending event scheduled after the target survives (the scheduler is not reset).
4. The event log holds a failure record with the original kind, actor, sim time and exception
   class; replaying it changes nothing.
5. Save → load (`to_save`/`SavedSession`) of a log with a failure record reproduces the state.
6. Session level: on a `SessionManager`, a raising handler leaves `mgr.world is mgr.sim.world`
   and `mgr.osys.world is mgr.sim.world` true after the advance.
7. A handler that raises with no prior mutation behaves the same (the IP-1052 reproduction shape).

Permanent gates: `spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`.

## Documentation Updates

- `CLAUDE.md` code map (`engine/simulation.py`).
- `docs/requirements/03-requirements-traceability-matrix.md`: `FR-1120`/`NFR-2600` Test cells gain
  the new test module (08's traceability step).
- No manual impact: no operator-visible behaviour changes on the success path; a failure record is
  visible only as an event-log entry (§15.1 "Rewind / undo / branch" row: confirm, no edit).

## Definition of Done

- [ ] All seven tests pass; at least tests 1, 2 and 4 failed before the change.
- [ ] Full suite green; `test_determinism.py` and `test_import_guard.py` green.
- [ ] No success-path behaviour change: every pre-existing test passes unchanged.
- [ ] `CLAUDE.md` and RTM cells updated; package status `COMPLETE` on MBP/INDEX/ROADMAP.

## Verification Checklist

- [ ] Read `advance_to`: the success path has no added copy or rebuild.
- [ ] Reproduce test 1 independently with a fresh handler and seed.
- [ ] Confirm the failure-record kind is registered and no-op, and that a save file containing one
      loads and replays.
- [ ] Confirm Design Decision 2 by reading how the rollback keeps `SessionManager` references valid.
- [ ] Run the full suite and both permanent gates by name.

## Dependencies

ADR-0038 (Accepted); `IP-1020` (`VERIFIED`). No package depends on this one.

## Risks

- **Handlers that mutate their own payload in place.** `_h_condition_check` writes `payload["fired"]`
  before the append. On the failure path, the original payload (possibly half-mutated) goes into
  the failure record only; it is never replayed as a live event. Acceptable; note it in the test.
- **Generator safety.** `pop_due` is a generator over the heap; the rollback must not touch the
  scheduler, so iteration continues correctly.
- **Rebuild cost** is O(log length) per failure. Failures are rare by construction.

## Rollback Considerations

Revert the two engine files (and `manager.py` if touched). Logs containing a failure record would
then fail to replay (unknown kind), so a rollback must also be accompanied by discarding saves made
after this package. No vignette or content change.
