# IP-1083 — A Rewind or Undo Keeps White Cell's Future-Dated Injects (FR-4410, FR-4450, BL-0284)

> **Package ID:** IP-1083
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-25 by `07-implementation-planning`. Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The project owner's answer of 2026-10-25, recorded in
> [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #262: fix `BL-0284` before release.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4 (`FR-4410`,
> `FR-4450`); [IP-1066](IP-1066-pending-inject-edit-cancel.md) (`VERIFIED`; the `inject_admin` log entry,
> the override fold and the re-arm loop this package reuses), [IP-1061](IP-1061-inject-and-sizing-defect-remediation.md)
> (`VERIFIED`; the re-arm-after-rewind rule), [IP-1075](IP-1075-undo-clock-floor.md) (`VERIFIED`; undo
> lands on a defined instant), [IP-1101](IP-1101-self-contained-saves.md) (`VERIFIED`; the save
> content this package checks and leaves unchanged)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 7"),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0284`
> **Produces:** a rewind or undo that never silently drops a White Cell inject that was scheduled for a
> time still ahead of the landing instant; the schedule action itself becomes part of the event log.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) v2.4
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py) (read-only reference),
> [IP-1160](IP-1160-role-scoped-command-enforcement.md) (sibling; shares `manager.py` — see "Build ordering")

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Bug-fix package (one defect, small). Prose only; no code in this document.*

---

## Package ID

IP-1083.

## Title

Log White Cell's scheduling of a future inject, so a rewind or undo re-arms it.

## Objective

**Defect (`BL-0284`, Medium; found by `07` run #191, confirmed by `09` in `VR-1066`).** An inject that
White Cell schedules for a future simulated time (`fire_inject(..., at_sim_t=…)`, `POST /inject` with
`at_sim_t`) exists only in the scheduler until it fires. A rewind (or an undo) rebuilds the scheduler
empty and re-arms only the vignette's own injects and the *edited* White ones, so the unedited White
inject vanishes with no message. Save/resume keeps it; rewind does not.

### Reproduction (read-only, in a worktree, `TestClient`, vignette `00-training-basics`)

1. Create a session, `POST /start?cell=white`, pause the clock, `POST /step` 600 s.
2. `POST /inject?cell=white` with a one-message effect and `at_sim_t = start + 2 h` → 200, ok.
3. `GET /injects/pending` → `['white-1']`.
4. `POST /advance` to `start + 1 h`, then `POST /rewind` to `start + 5 min` (both 200).
5. `GET /injects/pending` → **`[]`**. Advancing to `start + 3 h` fires nothing; the event log has no
   `inject` entry. The inject is gone.

### Cause, in file and line terms (tree of 2026-10-25)

- `spacesim/session/manager.py:1346` — `fire_inject` schedules a future-dated White inject with
  `self.sim.schedule(when, "inject", {...}, tag=handle)`. That writes to the scheduler only; **no
  event-log entry exists until the event fires** (an `inject` entry is appended at fire time by
  `Simulation.advance_to`).
- `spacesim/engine/simulation.py:157` — `_rebuild` (reached from `rewind_to`, line 124, and `undo_last`,
  line 138) ends with `self.scheduler = Scheduler()`: *pending future events do not survive a
  rewind/branch*, by design — the event log is the only source of truth.
- `spacesim/session/manager.py:358-367` — `_arm_schedule`'s re-arm loop walks `self.vignette.injects`
  only. `:372-378` re-arms the **edited** White injects, but only from `inject_admin` log entries — an
  unedited White inject has none.
- Why save/resume does not lose it: `save_state` (`manager.py:1143`) persists the scheduler's pending
  events under `"pending"` and `from_state` (`:1280`) re-schedules them. A rewind has no such carry.

### Correct behaviour (from the requirements)

- `FR-4410` Postcondition: a scheduled inject applies at its `at_sim_t` regardless of what happens in
  between; its Acceptance Criterion is stated for save/resume, and the same promise is what White
  relies on for rewind. `FR-4410` also requires "an `EventLog` entry" for the applied inject.
- `FR-4450` / `IP-1066` Design Decision 8 and `FS-106` v2.3 *Determinism*: a White action is recorded
  in the event log at the simulated instant it is made (`ADR-0002`); "a rewind to an earlier instant
  discards it with the rest of the later history"; after a rewind to before a cancel or edit "the
  inject is pending again with its original parameters". The scheduling of an inject is such a White
  action.
- `FR-1120`: the event log is the only source of truth; replay reproduces state byte-for-byte. **No
  hidden state may be added** (no side list of "remembered" injects held outside the log).

So, with *T* the landing instant of the rewind (or undo) and *A* the instant White scheduled the
inject:

| Case | Behaviour |
|---|---|
| *T* ≥ *A* and the inject's fire time *F* > *T* | The inject is pending again, exactly as scheduled (same handle, fire time, effects), or as last edited/cancelled **at or before *T***. It fires once at *F*. |
| *T* < *A* (rewound to before White scheduled it) | The inject does not exist — the scheduling action is "later history". It is not listed and never fires. |
| *F* ≤ *T* and it fired (an `inject` entry without `skipped` at or before *T*) | Not re-armed; history is kept (follows the existing replay semantics). |
| *F* = *T* and no applied entry is retained (an undo that dropped the inject's own entry but kept another entry at the same instant) | Re-armed, once — the same rule `IP-1061` gave vignette injects. |
| Undo | The same rules with *T* = the landing instant. Undoing the scheduling entry itself withdraws the inject, like undoing any other White action. |
| Save / load | A save carries the scheduling entry (it is in the event log) and the pending event; a resumed session behaves exactly as a never-saved one for every case above. |

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-4410 | Fire injects immediately or at a scheduled simulated time | A scheduled inject keeps its promise across rewind and undo, and its scheduling is an event-log entry. |
| FR-4450 | Edit or cancel a scheduled, not-yet-fired inject | The scheduling action joins the cancel/edit actions in the same logged, folded history; a rewind to before an edit shows the as-scheduled parameters, as `FS-106` v2.3 already says. |

## Architecture Components

C2 Session / Application Layer only (`SessionManager`). The engine is not touched (`Simulation.rewind_to`
and `_rebuild` keep discarding the scheduler — that is correct and must not change). No UI change: the
pending-inject list already reads from the same fold.

## Interfaces

None changed. `POST /inject`, `POST /rewind`, `POST /undo`, `GET /injects/pending`, the save format's
keys: all unchanged. The event log gains entries of an existing kind (`inject_admin`) with a new
`action` value, `"schedule"`.

## Files to Create

- `spacesim/tests/test_inject_rewind_rearm.py` — the matrix below.

## Files to Modify

- `spacesim/session/manager.py`
  - `fire_inject` (future-dated branch only): after validation and handle allocation, record the
    scheduling as a logged White action — through the existing `_log_inject_admin` with a `row` of
    `{handle, trigger: "time"}`, `action="schedule"`, the effects and fire time — which returns the
    handle's `rev` (1 for a new handle); then schedule the `inject` event **with that `rev` in its
    payload**, still tagged with the handle. The immediate branch (`when <= now`) is unchanged and logs
    nothing extra.
  - `_h_inject_admin`: for `action == "schedule"` change no state and append **no** message (cancel
    and edit keep their White-only messages). Pure on its payload, so replay matches live.
  - `_arm_schedule`'s override re-arm loop (about lines 372-378): change the guard `ov["at"] <= from_t`
    to `ov["at"] < from_t`, keeping the existing "already applied" test, so an inject whose fire time
    equals the landing instant and was not retained as fired is re-armed once (the `IP-1061` rule for
    vignette injects, applied here). No other change: a scheduled White inject is now an override entry
    (`trigger="time"`, `at`, `effects`, `rev`), so the **existing** loop re-arms it; the stale-event
    check in `_h_inject` (`rev`) already accepts a matching `rev` and skips a superseded one.
- Check, do not necessarily modify: `pending_injects()` (the scheduler loop skips events that carry a
  `rev`; the override loop lists them — confirm one row per handle), `from_state`'s handle-sequence
  restore (already reads `inject_admin` handles), `InProcessSession.cell_activity` (reads scheduler
  events of kind `inject`; a `rev` key must not change its rows), and `session/aar.py` (a new
  `inject_admin` payload `action` must not break any entry formatter or export).
- `CLAUDE.md` Code Map: a short note under the `IP-1066` bullet — "White's future-dated injects are
  logged as `inject_admin` `schedule` entries so rewind/undo re-arms them (`IP-1083`, `BL-0284`)".

No change to `save_state`/`from_state` is needed: the scheduling entry rides in the event log and the
pending event rides in `"pending"`, both already saved (`IP-1101`'s content is unchanged). Re-checked:
the save carries `eventlog`, `pending`, `orders`, `ssn_requests`; nothing here adds a key.

## Implementation Tasks

1. Write the test module (below) first; run it and see the rewind, undo and save-then-rewind cases fail.
2. `fire_inject` logs `schedule` and schedules the `rev`-carrying event.
3. `_h_inject_admin` handles `schedule` silently.
4. `_arm_schedule` guard `<=` → `<` on the override loop.
5. Re-run `test_pending_inject_queue.py` (27 tests) and the inject suites unchanged; fix only what this
   package's own change broke (none expected — no existing test pins a revision number or the absence
   of a log entry after a future-dated inject; re-check by searching for `rev` and for event-log counts
   in the files that call `fire_inject` with `at_sim_t`).
6. `CLAUDE.md` note; regenerate the RTM Test column (`--origin-report=rtm`).

## Tests to Add

`spacesim/tests/test_inject_rewind_rearm.py`, module-level `pytestmark = pytest.mark.verifies("FR-4410")`,
`FR-4450` added on the cancel/edit cases and `IP-1083` on the package's own Definition-of-Done cases.
Fixture: a small synthetic `Vignette` (as in `test_pending_inject_queue.py`) with one vignette time
inject so vignette and White injects can be mixed. Each test is written and seen failing first, except
those marked "regression" (they pass on arrival and pin behaviour that must not change).

| # | Case | Expectation | Origin |
|---|---|---|---|
| 1 | Reproduction: schedule at +2 h, advance +1 h, rewind to +5 min | `pending_injects()` still lists the handle with the same `at` and effects; advancing past +2 h fires the message exactly once | FR-4410 |
| 2 | Rewind to before the scheduling instant | handle absent; never fires | FR-4450 |
| 3 | Rewind to exactly the scheduling instant | handle present | FR-4450 |
| 4 | Fired, then rewind to before the fire time | pending again, fires again once after the rewound clock passes it | FR-4410 |
| 5 | Fired, then rewind to after the fire time | not re-armed; the message appears once; the `inject` entry is retained | FR-4410 |
| 6 | Landing exactly on the fire time with the inject's own entry dropped by an undo while another entry at that instant stays | re-armed once, fires once | FR-4410 |
| 7 | Undo past the fire entry | pending again | FR-4410 |
| 8 | Undo of the scheduling entry itself | withdrawn; not listed; never fires | FR-4450 |
| 9 | Schedule, edit, rewind to between the two | original parameters; rewind to after the edit: edited parameters | FR-4450 |
| 10 | Schedule, cancel, rewind to before the cancel | pending again; rewind to after the cancel: stays cancelled and never fires | FR-4450 |
| 11 | Two White injects and one vignette inject, one White inject cancelled, rewind | listing order and content as before the rewind; each fires once; handles are not reused for a later schedule | FR-4410 |
| 12 | Save after scheduling, load, then advance | fires once at the right instant (the `FR-4410` save/resume criterion, regression) | FR-4410 |
| 13 | Save, load, then rewind to before the fire time | still pending (the log carries the schedule) | FR-4410 |
| 14 | A save written before this package (hand-built: scheduling entry removed, `pending` kept) | loads without error and fires once; a later rewind loses it — **documented limitation, asserted so it is known** | IP-1083 |
| 15 | Determinism: the same operations on two sessions give identical event logs; replaying the log (`replay()`) gives an identical world; a session with no future-dated White inject has an event log identical to the pre-change one (no new entry) | pass | IP-1083 |
| 16 | An immediate inject (no `at_sim_t`) and a past-clamped inject write no `schedule` entry | pass (regression) | FR-4410 |
| 17 | An invalid future-dated inject is refused whole and writes no log entry (atomic, `IP-1063`) | pass (regression) | FR-4410 |
| 18 | `schedule` adds no White message; `cancel`/`edit` still do | pass | IP-1083 |
| 19 | HTTP end to end through `TestClient` (the reproduction above): `/inject`, `/advance`, `/rewind`, `/injects/pending`, `/undo` | pass | FR-4410 |

Existing tests re-run unchanged: `test_pending_inject_queue.py`, `test_inject_library.py`,
`test_cell_activity.py`, `test_white_control_nonfinite.py`, `test_white_only_controls.py`,
`test_determinism.py`, the AAR suites. No existing test needs a `?cell=` or other change. The retag
guard pins only existing rows; the new module needs none.

## Documentation Updates

- `CLAUDE.md` Code Map note (above).
- `ROADMAP.md` row; the generated RTM Test column for `FR-4410`/`FR-4450`.
- `docs/training/12-white-cell-manual.md` — its inject/rewind text, if it says that a rewind drops a
  scheduled inject, is routed to `08-training-manual-authoring` as a manual-impact finding; not edited
  here.
- Backlog: `BL-0284` is closed by the pipeline manager after `09` verifies this package (not edited
  here — `docs/pipeline/` is not this skill's write scope).

## Definition of Done

- [ ] The reproduction no longer loses the inject; test 1 passes.
- [ ] Every row of the matrix passes; the "seen failing first" rows were observed failing.
- [ ] A scheduled White inject is an `inject_admin` `schedule` entry in the event log; no state outside
  the log is added to `SessionManager` or `WorldState`.
- [ ] A session with no future-dated White injects is unchanged (same event log, test 15).
- [ ] `test_determinism.py` and `test_import_guard.py` stay green; `test_doc_integrity.py` and
  `test_test_origins.py` stay green; the RTM Test column is regenerated.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Re-run the reproduction on a fresh session (not the package's own fixture) and on a worktree of
  the pre-change commit to confirm it failed there.
- [ ] Read `fire_inject`, `_h_inject_admin` and `_arm_schedule` directly; confirm no hidden state.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py`.
- [ ] Full suite with zero regressions against the baseline at the start of the build.
- [ ] `python3 -m pytest spacesim/tests/test_test_origins.py spacesim/tests/test_doc_integrity.py`.
- [ ] A rewind landing exactly on a fire time (test 6) fires the inject once, not twice, not zero times.

## Dependencies

- **Upstream:** the packages above, all `VERIFIED`. **Authorization on record** (run #262), so `READY`.
- **Downstream:** none. `11-release-readiness` is re-run once this package and `IP-1160` are `VERIFIED`.

## Build ordering (relative to IP-1160)

Independent in behaviour. Both edit `session/manager.py`; the hunks are in different places
(`fire_inject`/`_h_inject_admin`/`_arm_schedule` here; `issue_order`/`validate_order`/`save_state`/
`from_state` there). **Build `IP-1083` first**: smaller, no UI, and it is a release blocker by the owner's
answer; `IP-1160` then adds a key to a `save_state` that already needs no change from this package.

## Risks

- **Undo count changes by one for a future-dated inject.** Scheduling now writes a log entry, so the
  first `undo` after scheduling undoes the scheduling (the inject is withdrawn) instead of the previous
  action. This is the same behaviour cancel and edit already have and follows from "a White action is
  recorded in the event log"; the White UI's undo control should be read in that light. If the owner
  prefers the old undo count, the alternative is a rewind-only carry, which needs a log-independent
  record and is therefore refused by `FR-1120`.
- **Saves written before this package** hold a pending White inject with no scheduling entry: it still
  fires after a load, but a later rewind loses it (test 14). Not repairable without writing to a
  loaded log; accepted.
- **Edit numbering shifts:** a White inject's first edit is now revision 2 (the schedule is revision 1).
  Nothing user-visible depends on the number; verified by searching the tests and UI for `rev`.
- **The `<` guard** touches the path every edited inject uses; tests 5, 6, 9 and 10 pin both sides.

## Rollback Considerations

Revert `fire_inject`'s logging, the `_h_inject_admin` branch and the guard: scheduling goes back to
scheduler-only. Event logs already written with `schedule` entries still replay (the kind and handler
exist; an old build without the `schedule` branch would label such an entry "edited" and add a
White-only message, which is cosmetic). No data migration, no save-format change.
