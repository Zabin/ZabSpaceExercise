# IP-1082 — White Control Routes Refuse Non-Finite and Absurd Values at the Boundary, the Toolbar Step Buttons Show a Refusal, and the Code Map Catches Up (NFR-1600, FR-4330, FR-4310, FR-7330)

> **Package ID:** IP-1082
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-25 ([VR-1082](../verification/VR-1082-white-control-nonfinite-input-and-toolbar-refusal.md) v2.0, fresh-session re-verification after the RETURNED v1.0, 0 failed checks) — authored 2026-10-25 by `07-implementation-planning` (release-push remediation pass 6; `READY` before that). Every dependency was `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (fix bugs; no new features) and confirmed at run #260, covers it: the three Mediums of the release-candidate integration review are bugs in `VERIFIED` packages' behaviour or documentation. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1068](IP-1068-white-only-controls-server-enforcement.md), [IP-1074](IP-1074-white-control-correctness.md), [IP-1076](IP-1076-time-bound-and-console-refusals.md), [IP-1077](IP-1077-aar-playback-seat-checks.md), [IP-1340](IP-1340-browser-console-rule-suite.md) (all `VERIFIED`); the doc step also describes `IP-1081` and `IP-1103` (`VERIFIED`).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 6"); source: [`integration-review-release-candidate-1.md`](../../reviews/integration-review-release-candidate-1.md) `M-1`, `M-2`, `M-3`, `L-2`, `L-4`.
> **Produces:** one shared boundary check for non-finite JSON constants and out-of-range clock values on every White control route; a toolbar step handler that reports a refusal in `#control-status`; a current `CLAUDE.md` code map and two corrected stale lines.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) (clock, step, advance, rewind, undo, param); [FS-107 — After Action Review](../../features/FS-107-after-action-review.md) (playback speed and cursor)
> **Related Topics:** [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py), [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py), [`spacesim/session/aar.py`](../../../spacesim/session/aar.py), [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Bug-fix package (three small defects and their documentation). Prose only; no code in this document.*

---

## Package ID

IP-1082.

## Title

Reject non-finite and absurd values at every White control route; show a refused toolbar step; bring the `CLAUDE.md` code map up to date.

## Objective

Three defects from the release-candidate integration review, one unit each.

**Unit 1 (review `M-1`) — a non-finite number reaches the clock.** `ClockRequest.rate` is a plain `float`; Starlette's JSON parser accepts the literals `NaN`, `Infinity` and `-Infinity`; `SessionManager.set_clock` stores `float(rate)` unchecked. From then on every read of that session (`GET /clock`, `/godview`, `/scene/{cell}`, `/save`, `/objectives`, each of which calls `catch_up`) is HTTP 500 for every seat until White posts a finite rate; the pause call also 500s. `{"t": NaN}` on `advance` and `rewind` is a 500, not the 400 `FR-4330` promises. A negative rate and `1e18` are accepted. White is client-asserted, so any LAN participant can deny the session with one request. Correct behaviour (`NFR-1600`: never a 500 on a legal-looking request, an illegal action is blocked with an explanation; `FR-4330`; `FR-4310`): every White control route refuses a non-finite number, and the clock route refuses a rate outside its bounds, with HTTP 400 and a reason, changing nothing; finite in-range behaviour is unchanged.

**Unit 2 (review `M-2`) — the toolbar `+1m/+10m/+1h` buttons are unwrapped.** The handler bound at `app.js` line 2351 calls `step()` (line 370), which posts and refreshes with no `try/catch`. The palette's `stepBy` (line 2749) was fixed to catch, call `reportControlError("Advance", e)` and return. At the span end the toolbar produces an uncaught page error whose text is the raw JSON `detail`, and `#control-status` stays empty, contrary to `IP-1076`'s acceptance criterion and `12-white-cell-manual.md` WCM-4. Correct behaviour: the refusal text appears in `#control-status`, no page error is raised, and a successful step clears the message.

**Unit 3 (review `M-3`, `L-4`) — documentation.** The `CLAUDE.md` code map has no text for `IP-1076`, `IP-1077`, `IP-1081`, `IP-1103` (as the review shows, a grep for `_span_ceiling`, `playback_seat_decision`, `MAX_SAVE_SPAN`, `366`, `MAX_EVENTLOG` finds none); line 125 still says "browser GUI unverified headless"; `ROADMAP.md` line 26 still says the Build Spec wins on any conflict, which `CLAUDE.md` declares applies nowhere.

**Cheap Low in the same files, taken because it is a real invalid state (review `L-2`).** `PlaybackSession.advance` clamps the cursor to `[start_epoch, live now]`, but `state()` does not; after a live rewind or undo the cursor can sit beyond the end of the recorded log and `state()` reports a moment that no longer exists. The same invariant, enforced where it is read (clamp when reading; no mutation of the cursor outside `advance`/`set_*`, or clamp-and-store: the builder picks one and tests it).

**Left alone, by decision.** `--origin-report` exit code 5 (`L-3`, cosmetic: a read-only report that runs no tests; changing pytest's exit status risks the report contract, `NFR-2850`). The unbounded live event log (`L-1`, a design question for `04`). Duplicated parsers (`F-12`). Whether a rewind pauses a running clock (`L-6`, decided immaterial; `FR-4330` Notes). GDS-10 §6 counts (`03`).

## Requirements Covered

| ID | How |
|---|---|
| `NFR-1600` | No White control request can make a session unreadable or produce a 500; refusal with a reason (Units 1, 2). |
| `FR-4330` | `advance`/`step`/`rewind`/`undo` targets refused when non-finite, with the span rule unchanged; the running clock's rate is bounded. |
| `FR-4310` | The seat rule is unchanged and runs first (a non-White request is still 403 before the new validation). |
| `FR-7330` | Playback `speed` and `dt_s` refuse non-finite values; the cursor stays inside the recorded span (`L-2`). |
| `NFR-2840` | The console rule "a refused control shows its reason and raises no page error" is extended to the toolbar by a browser test. |
| `NFR-1100` | The rate bound keeps the 600x multiplier the requirement names fully usable. |

## Architecture Components

`ui_web/server.py` (request models and the White control routes: `clock`, `step`, `advance`, `rewind`, `undo`, `param`, and the playback `start`/`advance`/`speed` routes), `session/manager.py::SessionManager.set_clock` (and `advance_to`/`rewind_to`/`undo_last` for in-process callers), `session/inprocess.py` (the `ValueError` to `Ack(ok=False)` mapping already used by step/advance/rewind/undo, extended to `set_clock`), `session/aar.py::PlaybackSession` (`set_speed`, `advance`, `state`), `ui_web/static/app.js` (toolbar step handler). Load-bearing invariants: deterministic core untouched (nothing in `engine/`); fog-of-war untouched; the seat rule (`FR-4310`) untouched and evaluated first.

## Interfaces

- `POST /api/sessions/{sid}/clock` `{running, rate}`: a non-finite `rate`, or (when `running` is true) a `rate` not in `(0, MAX_CLOCK_RATE]`, is a 400 with the reason, the clock state unchanged. Success body unchanged.
- `POST …/step`, `…/advance`, `…/rewind`, `…/undo`, `…/param`: a non-finite number in any numeric field (for `param`, anywhere inside `value`, including nested lists/objects) is a 400 with the reason and nothing changed. Existing 400/403/404 behaviour is unchanged.
- `POST …/aar/playback/start|advance|speed`: the same for `speed` and `dt_s`; `speed` must also be finite (sign is not restricted beyond this package, as today).
- `SessionManager.set_clock`: raises `ValueError` for the same inputs; `InProcessSession.set_clock` maps it to a returned refusal consistent with the sibling methods.
- Console: toolbar step buttons show the refusal in `#control-status`.

### Design Decisions

1. **One shared validator, applied at the route layer, with a manager-level backstop.** A single helper in `server.py` walks a request's decoded numbers and raises HTTP 400 naming the field when one is `NaN`, `Infinity` or `-Infinity`; every White control route calls it right after `_require_white`, so the seat rule stays first and no route re-implements the test. The helper is the only place the policy lives; routes do not each write their own `isfinite`. Because Starlette decodes the JSON constants before pydantic sees them, the check is applied to the parsed body (the builder chooses between a dependency, a helper called per route, or typing the fields so the model itself refuses; whichever is chosen must yield a **400 with a reason**, not FastAPI's default 422, and must be one mechanism for all routes; a test asserts the route table has no White control route without it, in the style of the existing seat-rule route-table test). `SessionManager.set_clock` and the time methods also raise `ValueError` so a non-HTTP caller (tests, tools) cannot poison a session either; `step` already does this for its own argument.
2. **Where integers are declared.** `TimeRequest.t` and `UndoRequest.n` are `int`. A JSON `NaN`/`Infinity` for them currently reaches a 500; after this package they are a 400 from the shared check. A float with a fractional part for an `int` field keeps whatever behaviour it has today (out of scope; the builder records it in the matrix if it differs).
3. **The rate range.** The requirements state the bound only from below: `NFR-1100` asks for multipliers "up to at least 600×", and no shipped upper limit exists (the console sends the default `1.0`; the review exercised 600, and 1e18 is clamped to the span ceiling by `IP-1076`). The package therefore fixes: finite, greater than 0, and at most `MAX_CLOCK_RATE = 10_000` (`SessionManager` constant, one home), a figure with headroom over 600× that no hand-driven exercise approaches. This is a design decision recorded here, not a requirement; **`04-requirements-engineering` is asked to state the range under `NFR-1600`/`FR-4330`** (routed in the completion note; the build does not wait on it). A `rate` sent with `running: false` is ignored by the clock but must still be finite (the shared check), so pausing is never refused for an irrelevant value. Zero and negative rates with `running: true` are refused (a clock that runs backwards or not at all is the wrong control).
4. **Existing finite behaviour is kept.** In-range rates (including 1, 60, 600), the span clamp, the pinned running clock, every `Ack` shape, and the console's own calls are unchanged. The one intended change to previously accepted input: a rate of `1e18`, a negative rate or zero is now a 400 (the review called these "accepted and harmless"; they are absurd, and the 400 is the consistent contract).
5. **Poisoned-session regression.** The review's reproduction is turned into a permanent test: after a rejected `NaN` rate the session's `GET /clock`, `/godview`, `/save` still answer 200 and a following valid `clock` call works.
6. **Toolbar: route through the palette's handler.** The toolbar `[data-step]` buttons call the same function as the palette (`stepBy`), so there is one place that posts `/step`, catches, reports and clears. The unused `step()` helper is removed or left as a one-line alias; the builder greps for other callers first. `setServerClock` (Pause) cannot be refused for White and is not changed.
7. **Playback cursor (L-2).** Taken because the cursor beyond the recorded span is an invalid state by `advance`'s own invariant; the fix is local to `PlaybackSession` (read-time clamp to `[start_epoch, live now]`), read-only for ground truth and cell views alike, no change to fog-of-war. If the builder finds that the clamped read already cannot occur (a rewind already resets `_playbacks`), the item is closed with a test that pins the behaviour and no production change.
8. **Documentation scope.** `CLAUDE.md` and `ROADMAP.md` are edited by `08` in its doc step (this planning pass writes only `docs/implementation/`). Training pages that state the clock route's behaviour (`docs/training/08-http-api-reference.md`, WCM-4) are affected through `15-manual-traceability.md` §15.1 and are routed to `08-training-manual-authoring` as a manual-impact finding; the builder does not edit `docs/training/` unless the tree's own rule for the doc step says it may.

## Files to Create

- `spacesim/tests/test_white_control_nonfinite.py` — the matrix for Unit 1 and the `L-2` cases (a new file avoids touching pinned rows in `test_origin_retag.py`).

## Files to Modify

- `spacesim/ui_web/server.py` — shared check, applied to the White control routes and the playback start/advance/speed routes; `set_clock` route returns 400 on refusal.
- `spacesim/session/manager.py` — `set_clock` validation and `MAX_CLOCK_RATE`; backstop checks in the time methods where missing.
- `spacesim/session/inprocess.py` — map the new `ValueError` from `set_clock` like the siblings.
- `spacesim/session/aar.py` — `PlaybackSession` cursor read-time clamp; `set_speed` finite check.
- `spacesim/ui_web/static/app.js` — toolbar step handler (lines about 370 and 2351) and the `stepBy` helper reuse.
- `spacesim/tests/test_browser_console_rules.py` — the toolbar browser test (Unit 2); check any pinned row for this module in `test_origin_retag.py` before adding.
- `CLAUDE.md`, `ROADMAP.md` — documentation step.
- `docs/requirements/03-requirements-traceability-matrix.md` — Test column regenerated by `python3 -m pytest --origin-report=rtm` (generated, never hand edited).

## Implementation Tasks

1. Test-first: write the matrix below; confirm the NaN/Infinity cases fail today (500, or a poisoned session) and the finite cases pass.
2. Add the shared check and apply it; add `MAX_CLOCK_RATE` and the `set_clock` validation; map the refusal to a 400 with the reason.
3. Enumerate the White control routes from the live route table (not from this package's list) and make the route-table test fail for any White control route without the check.
4. Playback: finite `speed`/`dt_s`; clamp the cursor on read; test after rewind and undo.
5. Console: write the browser test first (it must fail on the parent: an uncaught page error and an empty `#control-status`), then route the toolbar buttons through `stepBy`.
6. Run the new tests, `test_white_control_correctness.py`, `test_white_only_controls.py`, `test_clock_and_time.py`, `test_undo_clock_floor.py`, the playback tests, `python3 -m pytest -m browser`, `test_determinism.py`, `test_import_guard.py`, then the full suite; regenerate the RTM Test column in the same commit.
7. Documentation step: the four `CLAUDE.md` code-map bullets (below), line 125 ("browser GUI unverified headless" replaced by the as-built wording already used at lines 27-29), `ROADMAP.md` line 26 (the "Build Spec wins" sentence replaced by the GDS-ladder rule `CLAUDE.md` states); add a bullet for this package's own change to the `server.py`/`manager.py` entries; run `test_doc_integrity.py`.

## Tests to Add

Each carries `@pytest.mark.verifies(...)` with the leaf shown.

**Unit 1 (`NFR-1600`, `FR-4330`).** All through the HTTP test client with `cell=white`, each asserting status, a non-empty `detail`, and that the clock state is unchanged afterwards.
1. Rate matrix on `POST /clock` with `running: true`: `NaN`, `Infinity`, `-Infinity`, `0`, `-5`, `1e18`, `MAX_CLOCK_RATE + 1` are each 400; `1`, `60`, `600`, `MAX_CLOCK_RATE` are 200. Sent as raw JSON text (the literals are not valid for a Python `json.dumps` default round trip, so the test posts a hand-built body).
2. `running: false` with a finite arbitrary `rate` is 200; with a non-finite `rate` it is 400.
3. Poisoned-session regression: after a rejected `NaN` rate, `GET /clock`, `/godview`, `/scene/blue`, `/save`, `/objectives` are 200 and a valid `clock` call succeeds.
4. Time targets: `NaN`, `Infinity`, `-Infinity` for `advance.t` and `rewind.t`; `NaN`/`Infinity` for `step.dt_sim_s`; the same for `undo.n`; each 400, nothing changed. The existing span matrix (negative, `1e30`, `10**30`, `true`) still passes unchanged.
5. `param` with a non-finite number at the top level and nested inside a list and an object: 400, nothing changed; a finite value is unchanged.
6. Playback `start` (`speed`), `speed` and `advance` (`dt_s`) with a non-finite value: 400 (never 500), the playback state unchanged.
7. Seat first (`FR-4310`): a non-White request with a `NaN` body is 403, not 400.
8. Route-table test: every White control route in the live route table has the shared check (the test names the routes it found so a new route cannot slip by).
9. In-process backstop: `SessionManager.set_clock(True, float("nan"))` and the three time methods with non-finite input raise `ValueError` and leave the session readable.
10. Concurrency note: a refused clock call does not move the wall anchor (read `clock_state` before and after).

**`L-2` (`FR-7330`).**
11. Start a playback, advance it to the end, rewind live to an earlier time: `state` reports a moment within `[start_epoch, live now]`; the same after `undo`; ground-truth and a cell viewpoint alike; no change to what a cell viewpoint may see.

**Unit 2 (`NFR-2840`, `FR-4330`) — the browser suite.**
12. White, session advanced to within a minute of the span end; click the toolbar `+1h` (and `+1m`): `#control-status` shows the reason (contains "span"), the page's error list is empty, the clock did not move; then a rewind and a toolbar step that succeeds clears the message.

**Documentation checks.**
13. `test_doc_integrity.py` and `test_test_origins.py` green; no allow-list grew.

About 12 test functions (several parametrised).

## Documentation Updates

- `CLAUDE.md` code map: one short bullet each, in the existing style (these are the text `M-3` found missing). `IP-1076`: `SessionManager._span_ceiling()` (start + `MAX_SAVE_SPAN_US`, 366 days) bounds `step`/`advance_to` and the lazy clock, a refused step/advance is a `ValueError` mapped to `Ack(ok=False)` and HTTP 400, and the running clock pins at the ceiling instead of pausing. `IP-1077`: `playback_seat_decision()` and `PlaybackSeatRefused` in `session/inprocess.py` gate the five `aar/playback/*` routes by the requesting seat (White any viewpoint, a player its own cell, Observer state-read only, 403 before any change). `IP-1081`: the 100,000-entry load cap now lives at `SessionManager.MAX_EVENTLOG_REPLAY_ENTRIES` (alias on `InProcessSession`), the first rung of `validate_save`, counting a real save's `{"entries": [...]}` log. `IP-1103`: `MAX_SAVE_SPAN_US` and `_check_final_time_span` refuse a save whose `final_time` is more than 366 days past its start. Plus a clause for `IP-1082` on the `server.py` and `manager.py` entries (shared non-finite check, `MAX_CLOCK_RATE`).
- `CLAUDE.md` line 125 and `ROADMAP.md` line 26: corrected as stated in Task 7.
- `docs/requirements/` (a rate-range statement under `NFR-1600`/`FR-4330`), `docs/training/` (clock route text, WCM-4), GDS-10 §6 counts and `docs/pipeline/` are not written by this package; each is routed to its owner in the completion note.
- `docs/implementation/00-master-build-plan.md`, `packages/INDEX.md`, the TWBS: written in this planning pass.

## Definition of Done

- No White control request, in or out of range, can make a session's reads fail; every non-finite number is a 400 with a reason, from one shared mechanism that the route-table test pins.
- The clock rate is bounded as Design Decision 3 states; finite in-range behaviour, the seat rule and every existing response are unchanged.
- The toolbar step buttons show a refusal in `#control-status` with no page error (browser test green).
- The playback cursor never reports a moment outside the recorded span (or the item is closed with a pinning test and no code change, per Decision 7).
- The four code-map bullets, line 125 and `ROADMAP.md` line 26 are current.
- The new tests are green; the RTM Test column is regenerated in the same commit; the full suite, `python3 -m pytest -m browser`, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py` are green; no allow-list grew.

## Verification Checklist

- [ ] Re-derive `M-1` on the parent commit: `NaN` rate poisons every read; on this commit it is a 400 and the session stays readable (`GET /clock` 200).
- [ ] Every White control route in the live route table (re-listed by the verifier, not copied from the package) refuses `NaN`/`Infinity`; the seat rule still answers first.
- [ ] Rate boundaries behave as Decision 3 states; 600 is accepted.
- [ ] Re-derive `M-2`: on the parent, a toolbar click at the span end leaves a page error and an empty status; on this commit it shows the reason and no error. Palette path unchanged.
- [ ] Playback after rewind and undo reports an in-span moment; fog-of-war unchanged.
- [ ] `CLAUDE.md` now contains `_span_ceiling`, `playback_seat_decision`, `MAX_SAVE_SPAN_US`, `366`, `MAX_EVENTLOG_REPLAY_ENTRIES`; line 125 and `ROADMAP.md` line 26 no longer carry the stale statements.
- [ ] Nothing under `engine/` changed; permanent gates, documentation checks and the browser suite green; the excluded items (exit code 5, live event-log cap, parser duplication, rewind-pause) are untouched.

## Dependencies

All `VERIFIED`: `IP-1068`, `IP-1074`, `IP-1076`, `IP-1077`, `IP-1340`. Independent of every other open package (`IP-1160` is `BLOCKED` on authorization only and edits `engine/orders.py`, not these files).

## Risks

- **422 versus 400.** FastAPI/pydantic validation answers 422 by default; the contract here is 400 with a reason (as every sibling White route). A typed-field approach must be checked to produce the 400, or the helper approach used instead.
- **A hidden client of the old tolerance.** A tool that posts a rate outside the new range would now be refused; the builder greps `tools/`, `spacesim/tools/`, the training curls and the tests for `rate` and records the result.
- **Browser test fragility.** It needs a session advanced to the span end; it reuses the pattern of the existing span browser test (`advance` to `ceiling - 600 s`, then click) rather than waiting in real time.
- **Pinned retag rows.** Adding a test to `test_browser_console_rules.py` must not break a pinned row in `test_origin_retag.py`; checked in Task 6.
- **Doc step edits `CLAUDE.md`,** the project guide: edit only the named bullets and lines.

## Rollback Considerations

Revert the commit. The clock route returns to accepting any float (the defect returns); no data format, save format or event-log record changes, so nothing written under this package needs migrating.
