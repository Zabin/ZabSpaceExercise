# VR-1021 — Verification Report: Failure-Atomic Event Application: a Raising Handler Leaves No Trace in Live State (ADR-0038, FR-1120, NFR-1600, NFR-2600)

> **Document ID:** VR-1021
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1021](../packages/IP-1021-failure-atomic-event-application.md),
> [ADR-0038](../../architecture/adr/ADR-0038-failure-atomic-event-application.md),
> [FS-102](../../features/FS-102-command-scheduling.md) v1.1, [IP-1020](../packages/IP-1020-command-scheduling.md) (`VERIFIED`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0264`
> (from `BL-0227`)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1021`
> **Feature Mapping:** FS-102 v1.1 (`FR-3310`, the shared scheduler); ADR-0038 (`FR-1120`,
> `NFR-1600`, `NFR-2600`)
> **Related Topics:** [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py),
> [`spacesim/engine/handlers.py`](../../../spacesim/engine/handlers.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py);
> [VR-1052](VR-1052-order-param-hardening.md) (the fresh-mechanism/byte-for-byte reproduction
> standard this report follows; its §6 is the original independent reproduction of the general
> `BL-0227` gap this package closes)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1021 — Failure-Atomic Event Application: a handler that raises mid-advance is
  rolled back to the replayed state, logged as a no-op failure record, and the advance continues
  (ADR-0038).
- **Version verified:** 1.0
- **Tree state verified:** commit `6c0a4e7` (branch `claude/chart-prompt-file-90hm9u`, this
  session's local tracking branch `verify-ip1021-local`). Implementing commit: `071e3d5`
  (2026-10-17, pipeline run #167). Six ledger-only/other-package commits (`60799fd`, `2519c50`,
  and others up to `6c0a4e7`) are layered on top, untouched by this verification, and do not touch
  `simulation.py`/`handlers.py`/`test_failure_atomic_events.py`.
- **Independence:** first verification pass. Fresh session with no involvement in `071e3d5` or
  any prior `IP-1021` work; no prior `09-package-verification` run exists on this package. The
  task's own instructions required a fresh session for exactly this reason, given this package's
  direct bearing on the determinism invariant.

## Result

**VERIFIED, clean — no findings against the package itself.** The rollback is confirmed, by direct
reconstruction rather than by re-running the implementer's own fixtures, to be a genuine
"as-if-never-scheduled" rollback: a world built by advancing past a scheduled-and-crashed event is
byte-for-byte identical (including RNG export state) to a world built the same way except the
crashing event was never scheduled at all — not merely "some other consistent state." This was
proved on three independent, fresh reproduction scenarios, each using a mechanism distinct from
the implementer's own test module (`test_failure_atomic_events.py`'s custom `_mutate_draw_then_raise`/
`_raise_only` handlers registered directly on a bare `Simulation`):

1. A **real catalog handler** (`OrderSystem._h_maneuver`), monkeypatched to mutate a real asset's
   `resources.power_w`, draw from the RNG, and raise `RuntimeError`, scheduled via `sim.schedule`
   on a real `SessionManager`/vignette session — **bypassing `OrderSystem`/`_validate`/`_plan`
   entirely**, the exact mechanism `VR-1052` §6 used to prove the pre-fix gap was live. Live state
   after `advance_to` equals `replay()` byte-for-byte; the mutated `power_w` is back to its
   pre-crash value; a `handler_error` record is logged; the simulation advances further
   afterward.
2. An **engine-level "as-if-never-scheduled" differential test**: two bare `Simulation`s built
   from the identical seed/initial state, one with a crashing event (a new handler kind,
   `probe_effect`, raising `KeyError` — a third exception class, after the implementer's
   `ValueError` and this report's own `RuntimeError`) scheduled among other real events, one
   without it scheduled at all. The two final worlds are byte-for-byte identical (`model_dump_json`
   equality after `json.loads`-normalization) and the RNG export states are identical — this is
   the strongest form of "genuine rollback" proof available, because it compares against a world
   that never ran the crashing handler at all, not against a hand-derived expectation.
3. A **multiplayer-lock-seam reproduction** through `InProcessSession` (the per-session `RLock`
   named in the package's Architecture Components C2): a crashing `execute_maneuver` driven
   through `InProcessSession.advance_to` leaves the session lock released and immediately
   re-acquirable, a subsequent mutating call through the same service succeeds normally, a
   concurrent-style read (`list_sessions`/`clock_state`) sees a consistent session, and
   `mgr.world`/`mgr.osys.world` stay the same object as `mgr.sim.world` throughout — confirming
   Design Decision 2 end-to-end through the actual session/lock boundary, not just inside a bare
   `Simulation`.

The non-crashing path is confirmed unregressed: the full suite (1016 passed, 3 skipped — grown
from the implementer's recorded 992/3 by tests from the five other same-batch packages landed
since, not a regression) and both permanent gates (14/14) pass; `advance_to`'s success-path loop
is read directly and confirmed to add no per-event copy or rebuild (the only new work is inside
the `except` branch). One incidental, pre-existing, out-of-scope observation is recorded below
(not a finding against this package): `SessionManager._catch_up_locked`'s docstring ("Safe because
`sim.advance_to` raises only when target<current") was already true of the *new* behaviour at the
time it was written (run order places the docstring after the fix), and is independently confirmed
accurate post-fix — included here as a positive cross-check, not a defect.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All seven tests pass; at least tests 1, 2 and 4 failed before the change. | `test_failure_atomic_events.py` run by name: 7 passed. Pre-implementation reproduction, independently constructed (the shipped test file does not exist before `071e3d5`, so it cannot be run directly against an earlier commit): copied the whole tree into a scratch directory and reverted exactly `spacesim/engine/simulation.py` and `spacesim/engine/handlers.py` to their content at `071e3d5^` (confirmed by `grep` to contain no `_record_failed_event`/`HANDLER_ERROR_KIND`), then ran the shipped (post-fix) `test_failure_atomic_events.py` against that scratch tree: **all 7 of 7 fail** — stronger than the package's own "at least tests 1, 2 and 4" claim, and confirming every test genuinely exercises new behaviour, none a pre-existing pass. | ✅ Pass |
| Full suite green; `test_determinism.py` and `test_import_guard.py` green. | See Test run below. | ✅ Pass |
| No success-path behaviour change: every pre-existing test passes unchanged. | Full-suite re-run (below) shows no pre-existing test broken. Read `advance_to`'s success-path loop directly (`simulation.py:75-87`): identical shape to the pre-fix code except the `try`/`except` wrapper around `self._apply(...)`; no copy, no rebuild, no extra RNG/world touch on the non-raising path. | ✅ Pass |
| `CLAUDE.md` and RTM cells updated; package status `COMPLETE` on MBP/INDEX/ROADMAP. | `CLAUDE.md`'s `engine/simulation.py` code-map bullet (read directly) now states `advance_to` is failure-atomic (ADR-0038/IP-1021). RTM `FR-1120`/`NFR-2600` rows cite `IP-1021` and `test_failure_atomic_events.py`. MBP/`packages/INDEX.md`/`ROADMAP.md` all read `COMPLETE 2026-10-17 … awaiting 09-package-verification` prior to this report's own updates. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Read `advance_to`: the success path has no added copy or rebuild. | Confirmed directly (`simulation.py:71-87`): the loop pops, sets `clock.now`/`world.now`, `try: self._apply(...)`, `except Exception: self._record_failed_event(...); continue`, else `self.eventlog.append(...)`. The copy/rebuild (`copy.deepcopy`, `WorldState.model_validate`, the re-run-all-handlers loop) lives entirely inside `_record_failed_event` (`:89-122`), reached only from the `except` branch. | ✅ Pass |
| Reproduce test 1 independently with a fresh handler and seed. | Done three times over, each with a mechanism distinct from the implementer's own fixture Simulation/custom handlers — see Independent reproduction §1–§3 below. All three show live state == `replay()` byte-for-byte (and, in §2, == a world that never scheduled the crashing event at all — a strictly stronger proof). | ✅ Pass |
| Confirm the failure-record kind is registered and no-op, and that a save file containing one loads and replays. | `HANDLER_ERROR_KIND = "handler_error"` registered in `DEFAULT_HANDLERS` (`handlers.py:35,51`); `_handler_error` (`:38-44`) is a literal `return None`. The package's own Test 5 (`test_save_round_trip_with_a_failure_record_reproduces_state`) round-trips a `SavedSession` containing a `handler_error` record through `model_validate_json`/`replay()` and asserts equality — independently re-run, passes. Independently re-derived on repro §1's real-vignette session: `mgr.sim.to_save()` → `SavedSession.model_validate_json(...).model_dump_json()` round-trips without error (payload is plain strings/dicts, JSON-serializable as the package claims). | ✅ Pass |
| Confirm Design Decision 2 by reading how the rollback keeps `SessionManager` references valid. | Read `_record_failed_event` (`:108-111`): `world.now = event.t; for name in type(self.world).model_fields: setattr(self.world, name, getattr(world, name)); self.rng.import_state(rng.export_state())` — every field is copied **into** the existing `self.world`/`self.rng` objects, never replacing them, so `SessionManager.world`/`OrderSystem.world` (both holding the same object reference) stay valid automatically; `manager.py`/`orders.py` needed no change, matching the package's "preferred" option and its Files-to-Modify list (no `manager.py` entry in the diff). Independently confirmed through the session/lock boundary in Independent reproduction §3 (`mgr.sim.world is world_obj_before`, `mgr.world is mgr.sim.world`, `mgr.osys.world is mgr.sim.world`, all true after the crash). | ✅ Pass |
| Run the full suite and both permanent gates by name. | See Test run below. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-1120` (determinism) | `engine/simulation.py::Simulation.advance_to` / `_record_failed_event` (`:71-122`) — live state equals replay on the failure path | `test_failure_atomic_events.py` (Tests 1, 7); independently re-derived with three fresh mechanisms, including an engine-level differential proof against a world that never scheduled the crashing event (§2) | `03-requirements-traceability-matrix.md` — `FR-1120` row cites `ADR-0038`, `test_failure_atomic_events.py`, and `IP-1021` against `engine/simulation.py` — accurate | ✅ Pass |
| `NFR-1600` (robustness — never crash on a legal operator action) | `advance_to`'s `try`/`except Exception` around `_apply` (`:78-82`) — a raising handler no longer propagates out of `advance_to` | `test_failure_atomic_events.py::test_advance_continues_past_the_failure`; independently re-derived in all three repros (none raised past `advance_to`/`InProcessSession.advance_to`) | Not a distinct RTM data row in this matrix's current layout (NFR-1600 is referenced inline by ADR-0038/the package, not a numbered RTM line); content independently confirmed correct regardless | ✅ Pass |
| `NFR-2600` (complete action log) | `_record_failed_event`'s `eventlog.append(..., kind=HANDLER_ERROR_KIND, ...)` (`:112-122`) — the failure is recorded, not silently dropped | `test_failure_atomic_events.py::test_failure_record_carries_the_failed_event_and_replays_as_noop`; independently re-derived in all three repros (`handler_error` present, carrying `failed_kind`/`error_type`/`error` matching the real crash) | `03-requirements-traceability-matrix.md` — `NFR-2600` row cites `ADR-0038`, the specific test, and `IP-1021` — accurate | ✅ Pass |

`FR-3310` (FS-102's own leaf, "one deterministic scheduler for every kind") is consumed, not
changed — independently confirmed by reading `Scheduler`/`pop_due` (`clock.py:58-64`): `pop_due`
returns a generator bound directly to the `Scheduler` object it was called on; `_record_failed_event`'s
temporary `self.scheduler = Scheduler()` swap (to absorb any event a replayed handler might
re-schedule as a side effect) does not and cannot affect that already-created generator's internal
heap reference, and the `finally: self.scheduler = live_scheduler` restores the live scheduler
before any caller next reads `self.scheduler` — the Risks section's "generator safety" concern is
real but is independently confirmed handled correctly, not merely asserted.

## Test run

Exact commands run in this session (tree at `6c0a4e7`, worktree `verify-ip1021-local`):

```
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -q
python3 -m pytest spacesim/tests/test_failure_atomic_events.py -v
python3 -m pytest -p no:warnings                                   # full suite, exact summary line
```

- **Permanent gates, run by name:** `test_determinism.py` + `test_import_guard.py` → **14 passed**
  (6 + 8). Given this package's direct bearing on the determinism invariant, these were read as
  well as run: `test_determinism.py`'s property test constructs its own fresh `Simulation` with no
  crashing handler anywhere in its scenario, so it exercises only the success path this package
  leaves untouched — it passing is necessary but not sufficient evidence for the failure path,
  which is why Independent reproduction §1–§3 below exist as the real test of this package's claim.
- **This package's own tests, run by name:** `test_failure_atomic_events.py` → **7 passed** (0
  failed, 0 skipped), matching the claimed 7.
- **Full suite:** **1016 passed, 3 skipped** (1019 collected). The implementer recorded 992
  passed/3 skipped at `071e3d5`; the +24 passed here come from the five sibling packages in the
  same owner-prioritized clearance batch (`IP-1223`, `IP-1065`, `IP-1064`, `IP-1131`) landed on
  this branch after `071e3d5` and already independently accounted for in the journal's run #168–171
  entries — not a regression introduced by or discovered in this verification.
- **Pre-fix differential check (this report's own, not the implementer's):** reverted
  `engine/simulation.py` and `engine/handlers.py` to their immediate pre-`071e3d5` content in a
  scratch copy of the tree (confirmed by direct inspection to lack `_record_failed_event`/
  `HANDLER_ERROR_KIND`) and ran the shipped `test_failure_atomic_events.py` against it with a
  driver that forces the scratch tree's `spacesim` package ahead of the real one on `sys.path`
  (otherwise Python's own cwd-first import order silently picks up the fixed tree): **all 7 of 7
  failed**, each with `advance_to` itself raising (`ValueError`/the test's own raising handlers
  propagating straight out), exactly matching `BL-0227`'s and ADR-0038's description of the pre-fix
  defect — `advance_to` not returning at all, rather than returning with a rolled-back state.

## Scope audit

`git show 071e3d5 --stat` (8 files): `CLAUDE.md`, `ROADMAP.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/engine/handlers.py`,
`spacesim/engine/simulation.py`, `spacesim/tests/test_failure_atomic_events.py` (new) — exactly
the package's declared "Files to Create" (the new test module) and "Files to Modify" (`simulation.py`,
`handlers.py`), plus the documentation/ledger files its own "Documentation Updates" section names.
`spacesim/session/manager.py` — named in the package as a conditional modify, "only if Design
Decision 2's callback option is chosen" — is **absent** from the diff, correctly: the implementer
chose the in-place-`setattr` option (confirmed above), which needed no session-layer change. No
excursion.

## Independent reproduction (fresh mechanisms, not the implementer's own)

Scripts run in this session; mechanisms and fixtures are listed to show none reuses the
implementer's own `_mutate_draw_then_raise`/`_raise_only` custom handlers or `WorldState(now=0)`
bare-Simulation fixture pattern beyond what §2 deliberately keeps minimal for its differential
proof.

### §1 — Real catalog handler, direct-schedule bypass of `OrderSystem`, on a real session

`SessionManager(load_vignette("leo-isr-denial"), seed=4242)`. `OrderSystem._h_maneuver` was
monkeypatched to subtract `9999.0` from a real asset's `resources.power_w`, increment
`world.counters["maneuver_attempts"]`, draw `rng.randint(1, 1_000_000_000)`, then raise
`RuntimeError`. The event was scheduled directly via `mgr.sim.schedule(..., "execute_maneuver", ...)`
— bypassing `OrderSystem.issue`/`_validate`/`_plan` entirely, the identical bypass mechanism
`VR-1052` §6 used to prove the pre-fix gap was reachable via *any* handler, not just order-param
ones.

Result: `advance_to` did not raise; the handler ran exactly once (no retry); `mgr.sim.world.model_dump_json()
== mgr.sim.replay().model_dump_json()`; `power_w` after the crash equals its pre-crash value
exactly (`1500.0 == 1500.0`, not merely "finite" or "plausible"); `maneuver_attempts` is absent
from `world.counters`; a `handler_error` record carries `failed_kind="execute_maneuver"`,
`error_type="RuntimeError"`, and the exact message; `mgr.sim.world is world_obj_before` (object
identity preserved); the clock reached the requested target, i.e. the advance genuinely continued.

### §2 — Engine-level "as-if-never-scheduled" differential proof

Two bare `Simulation(WorldState(now=0), seed=4242)` instances, built identically except one
schedules a new handler kind `probe_effect` (mutates `world.messages`/`world.mission`, draws
`rng.random()`, raises `KeyError` — a third exception type, after the implementer's `ValueError`
and §1's `RuntimeError`) between two `random_roll` events, and the other never schedules it at
all. Both advance to the same target (`100`).

Result: the two final worlds are **byte-for-byte identical** (`json.loads`-normalized equality,
to rule out key-ordering artifacts) — this is the strongest available proof that the rollback is
genuinely "as if it never happened," since it compares against a world that *actually never ran*
the crashing handler, not against a hand-computed expectation of what it "should" look like. The
RNG export states are also identical between the two sims. The crashing sim's event log reads
`["inc_counter", "random_roll", "handler_error", "random_roll", "inc_counter"]` — the later
`random_roll`/`inc_counter` events fired normally, and `replay()` matches live state.

(An earlier attempt at this exact comparison through two separately-constructed `SessionManager`s
loading the same vignette/seed showed a spurious 1-microsecond difference in `world.now` — traced
to the lazy multiplayer clock's wall-time-coupled `catch_up()`, which legitimately advances the sim
clock by a few microseconds of real elapsed Python execution time between `start()` and
`set_clock(False)` on two sequentially-constructed sessions. This is a documented, intentional
property of the server-authoritative lazy clock (`CLAUDE.md`'s multiplayer section), unrelated to
`IP-1021`/`ADR-0038` and outside the deterministic core's own guarantee — the engine-level
differential test above avoids it entirely by using bare `Simulation` objects with no wall-clock
coupling, which is the correct level at which to test invariant 1. Not filed as a finding: it is
pre-existing, intentional, session-layer behaviour, not an engine defect, and no instruction in
ADR-0038/IP-1021 claims two independently-`start()`-ed sessions share a wall-clock-free epoch.)

### §3 — Multiplayer lock-seam reproduction through `InProcessSession`

Drove the crash through `InProcessSession.advance_to` (the real `with mgr._lock:` seam named in
the package's Architecture Components C2), with `OrderSystem._h_maneuver` monkeypatched to mutate
and raise as in §1. After the crashing `advance_to` call returned (did not raise, did not hang):

- The session's `threading.RLock` was immediately re-acquirable from a separate thread
  (`timeout=5`, acquired well under it) — the lock is not left held.
- A further mutating call through the same service (`svc.advance_to(sid, ...)`, handler restored)
  completed normally and advanced the clock to the expected target.
- `svc.list_sessions()` and `svc.clock_state(sid)` — the concurrent-read seam
  (`_locked_read`/`catch_up`) — both returned normally and showed a consistent session.
- `mgr.world is mgr.sim.world` and `mgr.osys.world is mgr.sim.world` held true throughout,
  confirming Design Decision 2 end-to-end through the session/lock boundary, not just inside a
  bare `Simulation`.
- A `handler_error` record was present and `mgr.sim.replay().model_dump_json() ==
  mgr.sim.world.model_dump_json()`.

This directly answers the task's multiplayer-interaction question: because `advance_to` no longer
*raises* for a handler exception (it only did, pre-fix, for the `target < self.clock.now` guard,
unaffected by this package), the per-session `RLock`'s normal `with` — `__exit__` always runs,
whether the `with` body raised or not — was never actually at risk from this class of crash either
before or after this package; what changed is that before the fix the *caller* of `advance_to`
(e.g. `_catch_up_locked`) would have seen the exception propagate up past the lock release (still
releasing the lock correctly, since `with` always releases) but leaving live state diverged from
replay. After the fix, neither the lock-release question nor the divergence question is live.

## Findings

None against the package.

One informational, non-blocking observation, recorded for completeness and not filed as a
backlog entry: `session/manager.py::_catch_up_locked`'s docstring ("Safe because `sim.advance_to`
raises only when target<current") is read as fully accurate post-`IP-1021` — before this package,
it was incomplete (handler exceptions were a second way `advance_to` could raise, pre-fix), but the
docstring's text was already written in its current form and does not need updating as a
consequence of this package; this is simply confirmation that the architecture-invariant comment
and the shipped behaviour now agree, not a finding against either file.

## Traceability actions taken by this report

- `IP-1021` package header, Master Build Plan row, `packages/INDEX.md` row, `ROADMAP.md` row:
  `COMPLETE → VERIFIED`.
- `FS-102`'s `Referenced By` entry for `IP-1021`: tagged `VERIFIED` (`VR-1021`).
- `docs/requirements/03-requirements-traceability-matrix.md` `FR-1120`/`NFR-2600` rows:
  `IP-1021 (COMPLETE 2026-10-17, awaiting 09)` → `IP-1021 (VERIFIED 2026-10-17, VR-1021)`.
- `BL-0264` (root implementation-tracking entry, `IN PIPELINE`, "closes on `VERIFIED`"): closed
  `DONE` — independently confirmed the rollback is genuine and the non-crashing path is unregressed.
- `BL-0227` (the original general-gap finding): already `DONE` as of run #161 (ADR-0038 accepted,
  implementation filed as `BL-0264`); left unchanged — this report's own independent reproduction
  (§1–§3) confirms the general gap `BL-0227` described is now closed for every mechanism tried,
  consistent with its existing `DONE` disposition.
- `BL-0270` (the batch verification tracker for all five new packages): left as `SCHEDULED` with
  its existing text — this report is the first of the five it names to land; the pipeline manager's
  own next journal entry should record `IP-1021` as verified and the remaining four as still owed.
- `BL-0271`/`BL-0272`/`BL-0273` (manual-impact notes, deferred until their own packages verify):
  left exactly as found — none bear on `IP-1021` (which the package's own Documentation Updates
  section correctly says has no manual impact).
- `BL-0171`/`BL-0181`/`BL-0187`/`BL-0215`/`BL-0233`/`BL-0249` (`NEEDS-USER`) and `BL-0184`
  (rejected): left exactly as found — unrelated to this package, parked for the project owner per
  their own entries.
