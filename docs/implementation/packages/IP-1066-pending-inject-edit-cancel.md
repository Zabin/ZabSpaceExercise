# IP-1066 — Pending-Inject Queue: White Cell Edits or Cancels a Scheduled, Not-Yet-Fired Inject (FR-4450)

> **Package ID:** IP-1066
> **Version:** 1.0
> **Status:** 🟡 IN PROGRESS — 2026-10-18, `08-code-implementation`, pipeline run #192.
> *(Was 🟢 READY.)* Authored 2026-10-18 by `07-implementation-planning`, pipeline run #191.
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** covered by two standing decisions:
> - the project owner's standing pre-authorization of 2026-10-11;
> - the owner's 2026-10-18 instruction extending it to every package that the stalled original
>   batch `BL-0068`–`BL-0083` reaches. This package is `BL-0079`'s (item B13).
>
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.3 (the spec). The
> following `VERIFIED` packages also apply:
> - [IP-1061](IP-1061-inject-and-sizing-defect-remediation.md): the re-arm-after-rewind rule;
> - [IP-1062](IP-1062-condition-triggered-injects-and-new-effects.md): condition injects;
> - [IP-1063](IP-1063-inject-effect-fire-time-validation.md): the whole-inject check;
> - [IP-1064](IP-1064-condition-inject-follow-ups.md): the one-scan-per-tick pattern;
> - [IP-1130](IP-1130-observer-read-only-access.md): Observer rejection.
>
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0079`
> **Produces:** a White-only pending-inject queue whose entries can be cancelled or edited before
> they fire, deterministically and replay-safe.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md)
> v2.3 (`FEAT-4400` `FR-4450`)
> **Related Topics:** [IP-1067](IP-1067-side-by-side-controller-view.md) (the sibling `FR-4620`
> package; independent of this one)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. The next FS-106 slice after `IP-1065`.*

---

## Package ID

IP-1066.

## Objective

**As built at `d35639b`** (read this run):

- `SessionManager.list_injects()` (`session/manager.py`, line 828) returns the vignette's inject
  catalog (`id`, `label`, trigger kind). It carries no status and has no edit or cancel path.
- Vignette time-triggered injects are queued by `_arm_schedule` (line 248) as `inject` events
  whose payload is `{"effects", "inject_id"}`, with no tag.
- `fire_inject` with a future `at_sim_t` (line 897) queues `{"effects": ...}` with no id.
- Condition injects are evaluated by `_h_condition_check` (line 1282), and their history comes
  from `_fired_condition_inject_ids` (line 1268).
- `_h_inject` (line 1057) applies every effect unconditionally.

After this package, White Cell can do the following:

| Action | Result |
|---|---|
| `GET …/injects/pending` | Every not-yet-fired inject, as `{handle, source, trigger, at, effects}`, with edits reflected and cancelled entries excluded |
| Cancel a pending time inject, then advance past its fire time | It never fires: no effect is applied, and its logged `inject` entry is marked `skipped: "cancelled"` |
| Cancel a pending condition inject, then make its condition true | It never fires |
| Edit the effects (and/or the fire time) of a pending inject | It fires once, at the edited time, with the edited effects |
| Edit, then rewind to before the edit | The inject is pending again with its original parameters |
| Edit or cancel an already-fired inject, an unknown handle, or an inject due now | Refused, and nothing changes |
| Any of the above from a non-White seat | 403, and nothing changes |

## Feature Reference

[FS-106](../../features/FS-106-white-cell-dashboard.md) v2.3 covers this package through:

- User Workflows (v2.3 first bullet);
- System Behaviour ("Pending-inject queue");
- Subsystem Responsibilities (the v2.3 `SessionManager` row);
- State Changes, Error Handling and Security (v2.3);
- Acceptance Criteria (v2.3 Cancel, Edit, Refusals, Replay and rewind);
- the two Risks scoping reads.

## Requirements Covered

| ID | How |
|---|---|
| `FR-4450` | Pending queue, cancel, edit, refusals and event-log recording, as described below. |

This matches FS-106 v2.3's `FR-4450` exactly. `FR-4620` belongs to `IP-1067`.

## Architecture Components

- **C2 Session Layer**: `session/manager.py` (the queue, admin actions, handler checks, re-arm),
  `session/inprocess.py` (lock plus `Ack` wrappers).
- **C4 Operator Console**: `ui_web/server.py` (three routes) and `ui_web/static/app.js` +
  `index.html` (a "Pending injects" list in the White inject panel).
- **C1 Engine**: unchanged. No WorldState field is added. Overrides are derived from the event
  log, following `IP-1062`'s `_fired_condition_inject_ids` pattern.

## Interfaces

- **INT-0002** (White ↔ console): new routes
  - `GET /api/sessions/{sid}/injects/pending`
  - `POST /api/sessions/{sid}/injects/{handle}/cancel?cell=`
  - `POST /api/sessions/{sid}/injects/{handle}/edit?cell=` with body
    `{effects?: [...], at_sim_t?: int}`

  `GET /injects` is unchanged.
- **INT-0016** (inject → engine): a new logged event kind, `inject_admin`.

### Design Decisions

1. **Handles.**
   - A vignette inject's handle is its `id`.
   - A White future-dated inject (`fire_inject` with `at_sim_t > now`) gets the handle
     `white-<n>`. `n` is a session counter, re-derived on `from_state` as the maximum existing `n`
     plus 1, and the counter is never reused. The handle is carried in the payload as `inject_id`
     and as the event `tag`.
   - Immediate fires have no handle, because they are never pending.
2. **Admin actions are logged events.**
   - `cancel_inject(handle)` and `edit_inject(handle, effects=None, at_sim_t=None)` validate the
     request (Design Decision 6), then schedule an `inject_admin` event at `now`, with payload
     `{handle, action: "cancel"|"edit", rev, effects?, at?}`, and `advance_to(now)`. This is the
     same immediate pattern `fire_inject` uses.
   - The handler `_h_inject_admin` only appends a White-only message. It mutates nothing else and
     schedules nothing.
   - `rev` is 1 + the number of earlier admin entries for that handle.
3. **Overrides from the log.**
   - `_inject_overrides(before_t)` scans `eventlog.entries` of kind `inject_admin` with
     `sim_time < before_t` and folds them in log order to
     `{handle: {"rev", "cancelled", "effects"?, "at"?}}`.
   - A later edit replaces fields, and a cancel sets `cancelled`.
   - The comparison is strict (`<`). An admin action at instant `t` therefore never affects an
     event due at `t`, which keeps live and replay identical (`_h_condition_check`'s precedent).
4. **Edits reschedule; stale events skip.**
   - Every accepted edit of a time-triggered inject (vignette or White) also schedules a fresh
     `inject` event at the edited time, falling back to the previous effective time. Its payload is
     `{"effects": edited, "inject_id": handle, "rev": k}`.
   - An edited `at` earlier than `now` is refused rather than clamped. A request at exactly `now`
     is refused as "due now", per Design Decision 6. This keeps decision 3's strict rule simple.
     FS-106 v2.3 says an earlier time is clamped to now; this package narrows that to a refusal,
     because a clamped edit would land on the admin instant. Disclosed under Risks.
   - `_h_inject` with a handle reads `ov = _inject_overrides(now).get(handle)`:
     - **No `rev` in the payload** (an original event): if `ov` exists, mark
       `payload["skipped"] = "cancelled"` or `"superseded"` and apply nothing. Otherwise apply as
       today.
     - **`rev` in the payload:** apply only if `ov` is not cancelled and `ov["rev"] == rev`.
       Otherwise mark it `"superseded"` or `"cancelled"`.
5. **Condition injects.**
   - `_h_condition_check` skips a handle whose override is cancelled, and applies `ov["effects"]`
     in place of `inj.effects` when the override carries them.
   - An edit of a condition inject may carry `effects` only. An `at_sim_t` is refused for it.
6. **Refusals** (`ValueError`, which becomes `Ack(ok=False)` and then 400). The request is refused
   when:
   - the handle names no pending inject (unknown, already fired, or already cancelled);
   - the inject is time-triggered and its effective fire time is ≤ `now` (due now);
   - the edited `at_sim_t` is ≤ `now`;
   - an `at_sim_t` is given for a condition inject;
   - the edit has neither `effects` nor `at_sim_t`;
   - the edited `effects` fail `validate_inject_effects(..., check_targets=True)`, the whole-inject
     check from IP-1063.

   Separately, the server returns **403** when `cell != "white"`, which covers the Observer as well
   as Blue and Red. The trust level is the same client-side `cell` assertion that `declare_seats`
   uses.
7. **"Already fired".**
   - A vignette time inject has fired when an `inject` log entry carries its `inject_id` and has
     no `skipped` key.
   - A condition inject has fired when its id is in `_fired_condition_inject_ids`.
   - A White inject is pending exactly while a scheduler event with its tag is pending and its
     override is not cancelled.
8. **Re-arm after rewind** (`_arm_schedule`, the non-initial path). Original vignette events are
   re-armed exactly as today; the handler skips them if an override exists. In addition, for every
   override handle with `at` greater than `from_t`, not cancelled, and not yet fired, it re-arms
   one `rev` event at `ov["at"]` carrying `ov["effects"]`. If the edit changed only the effects, it
   uses the handle's original effective time.

   A rewind to before the admin entry drops that entry from the log, so the override vanishes and
   the original parameters return (FS-106 v2.3 Behaviour).

   **Not changed:** a rewind already discards *unedited* White future-dated injects. Because
   `_arm_schedule` re-arms only vignette injects, that is pre-existing behaviour, outside this
   package, and filed as a finding.
9. **The pending listing.** `pending_injects()` lists, in order of effective fire time (condition
   injects last, in vignette order), each pending handle with `{handle, source:
   "vignette"|"white", trigger: "time"|"condition", at, effects}`. It shows effective edited values
   and excludes cancelled or fired entries.
10. **UI.**
    - The White inject panel gains a "Pending injects" list, refreshed after any inject action and
      on each `refresh()` while White.
    - Each row shows the handle, the trigger, the fire time (ISO) and the effect types, with
      **Cancel** and **Edit…** controls. Edit prompts for effects JSON (pre-filled) and an
      optional "+seconds from now" new time.
    - Errors show in `#inject-result`, following the `IP-1065` pattern.

## Files to Create

- `spacesim/tests/test_pending_inject_queue.py`.

## Files to Modify

All were checked at `d35639b`:

- `spacesim/session/manager.py`:
  - `__init__` (line 133): register `inject_admin`; add the White counter.
  - `list_injects` (828): unchanged. Add `pending_injects`, `cancel_inject`, `edit_inject` and
    `_inject_overrides` next to it.
  - `fire_inject` (897): handle and tag on the future-dated branch.
  - `_h_inject` (1057): the override check.
  - `_h_condition_check` (1282): skip on cancel; use edited effects.
  - `_arm_schedule` (248): re-arm edited entries.
  - `from_state` (854): restore the counter.
  - Add `_h_inject_admin`.
- `spacesim/session/inprocess.py`: `pending_injects`, `cancel_inject` and `edit_inject` wrappers
  under `_locked` / `_locked_read`, next to `list_injects` (line 386).
- `spacesim/ui_web/server.py`: the three routes, next to `injects_list` (line 730), with
  `_require` and the White check.
- `spacesim/ui_web/static/index.html`: a `#pending-injects` container under `#inject-result`
  (line 265).
- `spacesim/ui_web/static/app.js`: `refreshPendingInjects()`, cancel and edit handlers, and calls
  after a fire or schedule and in `refresh()` for White.
- `CLAUDE.md` code map: one clause on `session/manager.py` and one on `app.js`.

## Implementation Tasks

1. Mark `IN PROGRESS`.
2. Write the tests below and see each fail first. Test 12 (existing inject tests stay green) is a
   pin.
3. Implement Design Decisions 1–10.
4. Run the full suite plus both gates.
5. Update the ledgers: the RTM `FR-4450` row, `CLAUDE.md`, and MBP/INDEX/ROADMAP → `COMPLETE`.
   Route the manual impact (`WCM-5`) via §15.1 after `VERIFIED`.

## Tests to Add

All in `test_pending_inject_queue.py`, using a small synthetic vignette with a time inject at
+1 h, a condition inject, and a message effect:

1. The pending listing shows both vignette injects and a White future-dated one (`white-1`), with
   correct `at` and effects. An immediate fire never appears.
2. Cancelling a vignette time inject, then advancing past +1 h: its message never appears, and the
   `inject` log entry carries `skipped: "cancelled"`.
3. Cancelling a condition inject, then making its condition true: it never fires.
4. Cancelling a White future-dated inject: it never fires.
5. Editing a message text: the edited text fires and the original does not. The fire happens
   exactly once.
6. Editing the fire time (to +2 h): the inject does not fire at +1 h and fires once at +2 h.
7. A second edit supersedes the first: only the latest rev fires.
8. Refusals: an unknown handle, an already-fired inject, an already-cancelled inject, `at_sim_t` in
   the past, `at_sim_t` on a condition inject, an empty edit, and invalid effects (an `anomaly` on
   a bus-less asset). Each raises and leaves the world, the log length and the pending set
   unchanged.
9. Replay: a session with a cancel and an edit gives `sim.replay().model_dump()` equal to the live
   world.
10. Rewind to before the edit: the pending listing shows the original effects and time again, and
    the inject then fires with its original effects. Rewind to after the edit, before the edited
    time: it fires once with the edited effects at the edited time.
11. HTTP:
    - `GET /injects/pending` returns 200.
    - Cancel and edit with `cell=white` return 200.
    - `cell=blue`, `cell=observer` or no `cell` return 403.
    - A refused edit returns 400 with its reason.
12. Save and resume (`save_state` / `from_state`) keep an edited pending inject and the White
    counter (no handle reuse).

## Documentation Updates

- RTM `FR-4450` (Future Feature FS-106, the tests, `IP-1066`).
- `CLAUDE.md` code map.
- MBP, `packages/INDEX.md` and ROADMAP status.

No manual prose in this package; it is routed after `VERIFIED`.

## Definition of Done

- [ ] Design Decisions 1–10 implemented.
- [ ] Every test was seen failing first, then passing.
- [ ] Full suite green; `test_determinism.py` and `test_import_guard.py` green.
- [ ] No existing inject test changed, except where a payload-shape assertion meets the new White
  `inject_id`/`tag` (disclose any such change).
- [ ] Ledgers updated and package `COMPLETE`.

## Verification Checklist

- [ ] The override fold uses `sim_time < before_t` (strict) and reads only the event log.
- [ ] `_h_inject_admin` mutates only `world.messages` and schedules nothing.
- [ ] Every route rejects `cell != "white"` with 403 before reaching `SessionManager`.
- [ ] A cancelled or superseded event is logged with `skipped` and applies no effect.
- [ ] Replay is byte-identical, and the rewind semantics match FS-106 v2.3.
- [ ] Gates green, and the full-suite count reported.

## Dependencies

`IP-1061`, `IP-1062`, `IP-1063`, `IP-1064` and `IP-1130`, all `VERIFIED`. No package depends on
`IP-1066`.

## Risks

- **Narrowing from FS-106 v2.3.** The spec clamps an earlier edited time to now; this package
  refuses it instead (Design Decision 4), so that an admin action never lands on the instant it
  affects. This is a stricter subset, not a contradiction of `FR-4450`'s AC. `09` should confirm
  it is acceptable.
- **Pre-existing rewind loss of unedited White future-dated injects.** This package leaves that
  alone and files it as a finding.
- **Log scans.** One scan per inject or tick, the same cost class as `IP-1064`'s condition scan.

## Rollback Considerations

Purely additive: new routes, a new event kind and payload markers. Reverting restores today's
behaviour. A save made with `inject_admin` entries would fail to replay after a revert (an unknown
event kind). That is acceptable for a training tool, but note it.
