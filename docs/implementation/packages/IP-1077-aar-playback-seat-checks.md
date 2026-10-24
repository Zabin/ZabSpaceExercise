# IP-1077 — AAR Playback Obeys the Requesting Seat: White Any Viewpoint, a Player Its Own, Observer Read-Only (FR-7340, FR-4320)

> **Package ID:** IP-1077
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1077](../verification/VR-1077-aar-playback-seat-checks.md), fresh session; COMPLETE before that) — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 4). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (bugs, in-progress and critical items only; no new features), authorizes this package. It closes a fog-of-war gap (a player seat can request the ground-truth viewpoint), which the directive treats as a bug, not a feature; the requirement (`FR-7340`) exists and states the behaviour. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [FS-107](../../features/FS-107-after-action-review.md) (the AAR spec the playback belongs to); [IP-1280](IP-1280-variable-speed-aar-replay.md) (`VERIFIED`; the playback routes and `PlaybackSession` this package guards); [IP-1068](IP-1068-white-only-controls-server-enforcement.md) (`VERIFIED`; the query-seat pattern, `_require_white`); [IP-1130](IP-1130-observer-read-only-access.md) (`VERIFIED`; `_reject_observer`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 4"), [the tranche 3 integration review](../../reviews/integration-review-tranche-3-release-push-remediation.md) (`L-4`), [`VR-1072`](../verification/VR-1072-white-only-extension.md) F3
> **Produces:** AAR playback routes that check the requesting seat (`FR-7340`): a refused request leaves the shared playback unchanged and discloses no other viewpoint's state to a player.
> **Feature Reference:** [FS-107 — After Action Review](../../features/FS-107-after-action-review.md)
> **Related Topics:** [`spacesim/session/aar.py`](../../../spacesim/session/aar.py), [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py), [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design; one Low-severity gap with fog-of-war weight, no new feature). Prose only; no code in this document.*

---

## Package ID

IP-1077 (split from `IP-1076`; see the TWBS "Release-push remediation, pass 4" for why).

## Title

Seat checks on the AAR playback routes.

## Objective

**Reproduction (read-only, the tip of `claude/plan-remediation-4`).** The five playback routes (`server.py:960-1000` at the tip: `POST .../aar/playback/start`, `.../advance`, `.../viewpoint`, `.../speed` and `GET .../state`) take no `cell` parameter and call no seat check. With a `TestClient` session: `POST .../aar/playback/start` with `{"viewpoint": "truth"}` and **no** seat answers `{"ok": true}`; with `?cell=observer` the same; with `?cell=blue` the same. After that `GET .../aar/playback/state` returns the full ground-truth `WorldState` (`PlaybackSession.state`, `aar.py:222-229`, returns `world.model_dump()` for `"truth"`) to any caller. A Red seat can therefore read Blue's assets and tracks through playback, which is the fog-of-war boundary (`FR-6210`) applied backwards; an Observer can retarget the one playback the session holds. The existing tests (`test_web.py:695-725`) already pass `?cell=white` on `start` and `advance` (the parameter is ignored today) but not on `viewpoint` or `state`.

**Cause.** `IP-1280` (`VERIFIED`) added the routes with a session-only signature; `IP-1072`'s verifier recorded the omission as `VR-1072` F3 ("scope decision outstanding"), which the baseline pass now closes by stating the rule in `FR-7340`. `InProcessSession.playback_*` (`inprocess.py:990-1026`) hold one `PlaybackSession` per session in `self._playbacks` and carry no seat.

## Requirements Covered

| ID | How |
|---|---|
| `FR-7340` | All four acceptance criteria: (1) a `blue` start or viewpoint request naming `truth` or `red` is refused and the playback is unchanged, naming `blue` succeeds; (2) a `red` seat reading the state of a playback whose viewpoint is `truth` or `blue` is refused; (3) an `observer` start, advance, viewpoint or speed request is refused and the playback is unchanged; (4) `white` succeeds for every viewpoint. |
| `FR-4320` | The seat is the same client-asserted query seat as the other protected routes (same trust level, GDS-09 LAN trust model); a refusal is a structural rejection, not authentication. |
| `FR-6210` | No response to a player seat contains state from a viewpoint other than its own cell's. |
| `FR-7330` | Pinned only: playback's existing behaviour for permitted requests is unchanged (non-disturbance, viewpoint switch continues from the same moment, non-participant cell refused). |

## Architecture Components

`session/inprocess.py::InProcessSession.playback_start/advance/state/set_viewpoint/set_speed` (the SessionAPI boundary, where fog of war lives; a new `seat` argument and one pure check); `ui_web/server.py` playback routes (accept the query seat, map a refusal to 403); `session/aar.py::PlaybackSession` (read for its `viewpoint`; **not** edited). Load-bearing invariants touched: fog of war at the SessionAPI seam (strengthened), read-only replay (playback never touches `mgr.sim`; unchanged), deterministic core (nothing in `engine/` touched).

## Interfaces

New request convention, identical to the protected routes: an optional `cell` query parameter naming the requesting seat (`white`, `blue`, `red`, `observer`). The body shapes are unchanged.

| Route | white | blue / red | observer | no seat or unknown seat |
|---|---|---|---|---|
| `POST .../aar/playback/start` | any viewpoint | only its own cell as viewpoint | 403 | 403 |
| `POST .../aar/playback/viewpoint` | any viewpoint | only its own cell | 403 | 403 |
| `POST .../aar/playback/advance` | yes | only while the current viewpoint is its own cell | 403 | 403 |
| `POST .../aar/playback/speed` | yes | only while the current viewpoint is its own cell | 403 | 403 |
| `GET .../aar/playback/state` | yes | only while the current viewpoint is its own cell | allowed (read) | 403 |

A refusal is **HTTP 403** with a reason naming the rule (for example "a player seat may play back only its own viewpoint"). It is raised **before** any playback state changes or is read, and before the existing 404 ("no playback session") and 400 (non-participant cell) responses, so a refused seat learns nothing about whether a playback exists or which viewpoint it holds beyond its own seat's permissions. `InProcessSession.playback_*` take a keyword `seat` and return `Ack(ok=False, reason=...)` for a refusal on the `Ack` methods; `playback_advance` and `playback_state` (which return a dict or `None` today) raise a dedicated session-layer exception (or return a refusal marker; the build picks the lighter of the two and keeps the route mapping in one place) so the route can answer 403.

### Design Decisions

1. **Where the check lives.** In `InProcessSession` (the SessionAPI boundary, per the fog-of-war invariant), as one small pure function taking `(seat, action, requested_viewpoint, current_viewpoint)` and returning a refusal reason or nothing. The route extracts `cell` and passes it through; it does no seat logic of its own except mapping the refusal to 403. This keeps the rule testable without HTTP and in one place.
2. **Absent or unknown seat is refused**, on every playback route including the state read, matching `_require_white` (`IP-1068`) rather than `_refuse_player_seat_on_create`'s tolerance of an absent seat. Reason: unlike session creation, playback has no hot-seat pre-seat step and no tool that calls it without a seat (the console has no playback UI at all: `grep -rn playback spacesim/ui_web/static` is empty at the tip). The cost is that existing test calls and documented curl examples without `?cell=` must add one; they are listed under Files to Modify. If the build finds a real caller that cannot name a seat, it stops and routes the question instead of relaxing the rule.
3. **One shared cursor stays one shared cursor.** `FR-7340` Notes leave open whether a player's start replaces White's cursor or each seat gets its own; the owner's default is the smallest change that closes the disclosure, so the existing one-playback-per-session model is **kept**: a player's start or viewpoint switch to its own cell replaces the session's playback viewpoint (as White's start already does), and any seat's next read or advance is then judged against the **current** viewpoint. White always succeeds. Per-seat cursors are a design change (a new data structure and a new route contract) and are recorded as an open owner question in the completion note, not built.
4. **The checks use the current viewpoint read under the same lock as the action.** `playback_*` do not take the session lock today (`inprocess.py:990-1026`); the check and the action on a given call must see one consistent viewpoint. The build uses the session's existing lock (`_locked_read` for reads, `_locked` for the two mutations that change the cursor) around check-and-act, without changing what the permitted actions do. Playback reads `state_at_time` (a replay) so a read lock is the correct level; the build confirms this against `_locked_read`'s contract and does not hold the lock longer than the existing code effectively does.
5. **Observer reads are allowed exactly as `FR-7340` states** ("may read playback state"). The Observer's own designation (`IP-1130`, `observer_designation`) governs what the Observer sees elsewhere; the playback read is not re-filtered by it in this package. If the owner wants playback reads filtered by the Observer's designation, that is a requirements change and is recorded, not built. (A read of a ground-truth playback by an Observer is consistent with `FR-6220`: the Observer seat is already a ground-truth reader.)
6. **No UI.** There is no playback control in the console, so there is no browser case and no console change. The playback routes remain HTTP-only; the training HTTP reference is the only operator-facing description (Documentation Updates).
7. **`FR-6220` ground-truth reads are untouched.** `/aar`, `/godview`, `/eventlog`, `/aar/export.*` and the rest of the no-cell reads keep their documented LAN trust model; they are explicitly out of `FR-7340`'s scope.

## Files to Create

- `spacesim/tests/test_aar_playback_seats.py` — the seat matrix, no-change-on-refusal, no-disclosure and layering cases.

## Files to Modify

- `spacesim/session/inprocess.py` — the pure seat check, the `seat` keyword on the five `playback_*` methods, the lock around check-and-act (Decision 4). `PlaybackSession` and `aar.py` unchanged.
- `spacesim/ui_web/server.py` — the five routes accept `cell: Optional[str] = None`, pass it, and map a refusal to `HTTPException(403, ...)`; update the docstrings to state the seat rule.
- `spacesim/tests/test_web.py` (`test_aar_playback_start_advance_and_viewpoint_switch`, `test_aar_playback_rejects_nonparticipating_cell`, `test_aar_playback_advance_without_start_is_404`) and `spacesim/tests/test_aar.py` (the `PlaybackSession` unit tests are engine-level calls on the class and are expected to be untouched; check): add `cell=white` to every playback call that lacks it. Assertions unchanged. The 404-without-start case keeps its meaning only for White (a non-White seat now gets 403 first), so the test is run as White.
- Any other caller of the playback routes found by `grep -rn "aar/playback" spacesim tools docs`. The tools directory and `run-spacesim` recipe are checked; none is expected.

## Implementation Tasks

1. Write the failing tests below first; run them and record that each failed for the stated reason (all refusal cases fail today with 200).
2. Add the pure check and the `seat` keyword to the five session methods; take the lock around check-and-act.
3. Add `cell` to the five routes and the 403 mapping; update docstrings.
4. Update the existing playback tests to name `cell=white`.
5. Regenerate the RTM Test column (`python3 -m pytest --origin-report=rtm`); run the full suite (both marker partitions and one unfiltered run), then the permanent gates, `test_doc_integrity.py`, `test_test_origins.py`.
6. Update the documentation below and the Master Build Plan row to `COMPLETE` (never `VERIFIED`).

## Tests to Add

All in `spacesim/tests/test_aar_playback_seats.py`, test-first, each tagged `@pytest.mark.verifies(...)` (module-level `pytestmark` for `FR-7340`). Session setup goes through the HTTP API as `cell=white`; the live session is advanced a little first so a playback has a span to play.

1. White succeeds with `start` for `truth`, `blue` and `red`, and then `viewpoint`, `advance`, `speed` and `state` (`FR-7340` criterion 4).
2. Blue `start` with `truth` is 403 and **no playback exists afterwards** (a following White `state` read is the 404 "no playback session"); Blue `start` with `red` is 403 and the same holds; Blue `start` with `blue` is 200 (`FR-7340` criterion 1). Same three cases for Red.
3. With White's playback running on `truth`, Blue `viewpoint` to `truth` and to `red` is 403 and the viewpoint, moment and speed read back by White are unchanged; Blue `viewpoint` to `blue` is 200 and continues from the same simulated moment (`FR-7340` criterion 1; `FR-7330` Design Decision 1 pinned).
4. With the playback on `truth`: Red `state` is 403 and the body carries none of the `WorldState` keys (no `assets`, no `tracks`); with the playback on `blue`: Red `state` is 403; Blue `state` is 200 and the body is the `CellView` shape (`FR-7340` criterion 2; `FR-6210`).
5. With the playback on `truth`: Blue `advance` and Blue `speed` are 403 and the moment and speed are unchanged afterwards (`FR-7340`).
6. Observer `start`, `advance`, `viewpoint` and `speed` are each 403 and the playback (moment, viewpoint, speed) is unchanged; Observer `state` is 200 (`FR-7340` criterion 3).
7. No seat, and an unknown seat string, on each of the five routes: 403 (`FR-7340`, `FR-4320`).
8. Check order: a refused seat asking for a non-participant viewpoint, or any seat acting before a `start` exists, is 403 and not 400/404; White with the same requests keeps the existing 400/404 (`FR-7340`; `FR-7330` pinned).
9. Layering: `InProcessSession.playback_start(..., seat="blue", viewpoint="truth")` returns `Ack(ok=False, reason=...)` without creating a playback; the pure check returns the same decision for every cell of the matrix table above (a table-driven test over the matrix, one case per cell) (`FR-7340`).
10. Non-disturbance and determinism: with seat checks in place, a refused request appends nothing to the event log and does not change the live clock or world (compare `save_state()` before and after a series of refused calls) (`FR-7340`; `FR-7330` non-disturbance).
11. The existing `test_web.py` playback tests, run as White, still pass unchanged apart from the added `cell=white` (`FR-7330`; they keep their own tags).
12. Module DoD case: the matrix in Interfaces has exactly the decisions the table states (`IP-1077`, a table-driven check against the documented matrix so the table and the code cannot drift).

No browser case: no console surface exists (Decision 6).

## Documentation Updates

- `CLAUDE.md`: in the `ui_web/server.py` bullet, one sentence that the playback routes check the query seat (`IP-1077`, `FR-7340`) beside the `_reject_observer` text; the LAN trust paragraph's list of no-cell ground-truth reads is unchanged.
- `docs/training/08-http-api-reference.md` (playback routes: add the seat column and the 403 cases) and `docs/training/12-white-cell-manual.md` where playback is described; use `docs/training/15-manual-traceability.md` §15.1. Training pages belong to `08-training-manual-authoring`; list any not edited in the completion note.
- `docs/requirements/01-functional-requirements.md` `FR-7340` Notes: **not edited here**; the completion note recommends flipping "Required, not yet built" once `VERIFIED`, and recording the per-seat-cursor question for `06`/`04`.
- RTM Test column regenerated (never hand edited); `FS-107` `Referenced By` (metadata only); `packages/INDEX.md`; Master Build Plan row, tally and graph note; `ROADMAP.md`; this header.

## Definition of Done

- Tests 1-12 exist, were seen failing for the stated reason (every refusal case fails today with 200), and pass.
- No playback route answers a player seat with state from another viewpoint; no refused request changes the playback, the live session or the event log.
- The matrix in Interfaces is what the code does for every seat and route, and a test pins that.
- Existing playback tests pass with `cell=white` added and no assertion weakened.
- The full suite (both marker partitions and one unfiltered run), `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py` and `test_test_origins.py` are green; RTM regenerated in the same commit.
- Documentation above updated; row `COMPLETE` in the Master Build Plan (not `VERIFIED`).

## Verification Checklist

- [ ] Reproduce the pre-fix disclosure on the parent commit (Red reads a `truth` playback; Observer starts a playback) and see it gone.
- [ ] Every new test names its origin; each failing-first case recorded.
- [ ] `git diff` of `spacesim/engine/` and `spacesim/session/aar.py` is empty; `test_import_guard.py` green.
- [ ] `test_determinism.py` green.
- [ ] Every playback route in the route table accepts `cell` and refuses as the matrix states (re-derive the route list from the route table, `app.routes` filtered on `aar/playback`, not from this document).
- [ ] The three existing `test_web.py` edits add only `cell=white`.
- [ ] Locking: check and act happen under one lock acquisition per call, and no new lock-order issue with `_locked`/`_locked_read` (read the helper).
- [ ] `test_doc_integrity.py` and `test_test_origins.py` green; RTM regenerated; no allow-list grew.
- [ ] Collected-test count stays below `COLLECTED_UPPER` (1700) in `test_origin_retag.py`; the completion note reports the final count.

## Dependencies

All `VERIFIED`: `IP-1280`, `IP-1068`, `IP-1130`. No package depends on `IP-1077`. No content dependency on `IP-1076`; build it after `IP-1076` only to avoid a merge conflict on `server.py`, the RTM Test column and the count-pinned guards.

## Risks

- **A caller that cannot name a seat** (Decision 2): none found in the tree; the build re-greps and stops rather than relaxing the rule.
- **Single shared cursor** (Decision 3): a Blue start replaces White's truth playback. Accepted for the release push; the alternative needs a design decision from the owner.
- **Seat is client-asserted** (`FR-4320`, GDS-09): a hostile LAN participant can claim `white`. Same trust level as every other protected route; this package adds a rejection rule, not authentication.
- **Observer reads ground truth through playback** (Decision 5): consistent with the Observer's existing god-view access, but worth the owner's eye; recorded.
- **Count-pinned guards** (`L-5`): about 20 tests added; see `IP-1076` Risks.

## Rollback Considerations

Revert the commit. No data migration; no save format, event-log shape, or request body changes. The `cell` query parameter is additive, and removing the check restores the unguarded routes exactly.
