# IP-1076 — Time Advance Bounded to the Exercise Span, Backwards Step Refused, and the Console's Remaining Refusal Gaps (FR-4330, FR-4310, NFR-1600)

> **Package ID:** IP-1076
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1076](../verification/VR-1076-time-bound-and-console-refusals.md), fresh session; COMPLETE before that) — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 4). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (bugs, in-progress and critical items only; no new features), authorizes this bug-fix package. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4 (the spec); [IP-1074](IP-1074-white-control-correctness.md) (`VERIFIED`; the rewind span and `start_epoch` on the clock state); [IP-1075](IP-1075-undo-clock-floor.md) (`VERIFIED`; undo floor); [IP-1103](IP-1103-save-validation-completion.md) (`VERIFIED`; `MAX_SAVE_SPAN_US` and the save-side span check this package reuses); [IP-1073](IP-1073-console-refusal-wiring.md) (`VERIFIED`; `#control-status` and `reportControlError`); [IP-1340](IP-1340-browser-console-rule-suite.md) (`VERIFIED`; the browser harness). No content dependency on [IP-1077](IP-1077-aar-playback-seat-checks.md); ordering only (see Dependencies).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 4"), [the tranche 3 integration review](../../reviews/integration-review-tranche-3-release-push-remediation.md) (`M-2`, `M-4`, `L-1`, `L-2`, `L-3`)
> **Produces:** an advance or step that cannot leave the exercise span or move backwards (400 with a reason, never 500), a running clock that stops at the span's end, a palette that offers White-only inject entries to White only, refusals that appear where a player can see them, and a quiet console on load.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py), [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py), [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design; bugs only, no new feature). Prose only; no code in this document.*

---

## Package ID

IP-1076 (FS-106 → `IP-107x`; `IP-1072`…`IP-1075` taken).

## Title

Time advance bound (`FR-4330`) plus the console refusal gaps left by tranche 3 (`M-4`, `L-2`, `L-3`).

## Objective

Close five defects from the tranche 3 integration review, all in the White Cell clock and the console that drives it, in one package because they share files (`session/manager.py`, `session/inprocess.py`, `ui_web/server.py`, `ui_web/static/app.js`) and one verification pass:

| # | Defect (review ID) | Symptom, read from the tree at the tip of `claude/plan-remediation-4` | Cause |
|---|---|---|---|
| 1 | `M-2` | Advance 370 days with `POST /advance`, `GET /save`, `POST /load_save` gives 400 `final_time ... beyond the maximum span`. A session White legitimately advanced yields a save the same system refuses. | `SessionManager.advance_to` (`manager.py:376`) has no upper bound; only `validate_save` checks `MAX_SAVE_SPAN_US` (`manager.py:1097-1110`). |
| 2 | `L-1` | `POST /step` with a negative `dt_sim_s`, or `POST /advance` with `t` before now, answers HTTP 500. A non-finite `dt_sim_s` also fails with an unhelpful error. | `Simulation.advance_to` raises `ValueError("advance_to cannot move time backwards ...")` (`engine/simulation.py:73`); `InProcessSession.step`/`advance_to` (`inprocess.py:204-216`) do not catch it and `server.py:474-482` returns the `Ack` unconditionally. |
| 3 | `M-4` | Blue, Red and Observer see "fire inject ..." and "inject lib: ..." in the command palette (`PALETTE.items`, `app.js` about lines 2678-2692). Choosing one posts `/inject`, gets 403, and `fireInject` (`app.js:390-401`) writes the reason into `#inject-result`, which sits in a `.white-only` panel (`index.html:258-266`) hidden from that seat. The player sees nothing. | The inject entries are not seat-gated (the time entries were, by `IP-1073`); the refusal text goes to a hidden element. |
| 4 | `L-2` | A refused Load in a connected Blue/Red tab replaces the `#session` readout ("session sess-1") with "Load failed: ..." while the tab stays joined and live. | `showLoadFailure` (`app.js:239-243`) writes unconditionally into `#session`. |
| 5 | `L-3` | Two kinds of console error on load: (a) after switching seat to Observer, `previewOrder` keeps posting `/order/validate` and the server answers 403 (2 errors per tab); (b) `GET /windows/blue/BLUE-RADAR` answers 404 on every page load. | (a) `previewOrder` (`app.js:653-660`) has no Observer guard although `Issue` is already disabled for that seat. (b) **Cause found:** `ASSETS` (`app.js:1387`) holds assets *and sensors*; `onActorChange` (`app.js:1085`) calls `drawRibbon(id)` for the first actor, which in the first vignette is the sensor `BLUE-RADAR` (a `sensors:` entry, `01-leo-isr-denial.yaml:57-62`). `windows_ahead` returns `None` for any id not in `world.assets` (`manager.py:824-828`, `_owns` at 1324-1326) and the route maps `None` to 404 (`server.py:712-718`). The 404 is the route's documented fog/ownership contract; the client asks a question that has no answer. A real client defect, so it is fixed in the client; the route is not changed. |

**Reproductions the builder runs first (read-only):** a `TestClient` session on `leo-isr-denial`: `start`, `advance` to `start_epoch + 370 days` as `cell=white`, `GET /save`, `POST /load_save` (expect 400 today); `step` with `dt_sim_s=-5` (expect 500 today); a Chromium page as Blue, then switch to Observer, listening for `console` errors (expect 403 on `/order/validate`) and, as White on load, a `404` on `/windows/blue/BLUE-RADAR`.

## Requirements Covered

| ID | How |
|---|---|
| `FR-4330` | Acceptance criterion (3): an advance or step whose target is after `start_epoch` + 366 days, or earlier than now, is refused with a reason and the clock is unchanged; criterion (4): every session reachable through (1)-(3) saves and loads. The rewind and undo halves are already built (`IP-1074`, `IP-1075`); this package builds the advance half. |
| `FR-4310` | The White time controls stay White-only; the console offers White-only entries only to White (palette inject entries). |
| `NFR-1600` | A request that cannot be honoured is refused with a reason and changes nothing (backwards or out-of-span advance; non-finite step). |
| `NFR-3020`, `NFR-3030` | Console rules (visible, correct refusals; no avoidable console errors). Tags only where a browser case verifies them; the console-error assertion uses the existing `c.errors == []` convention. |

No requirement leaf covers the `L-2` readout or the `L-3` noise; they are defects of the console against `NFR-1600`/`NFR-3020` and are tagged to those. The 366-day figure is the save cap restated (`FR-4330` Notes); making it configurable is an owner decision, not made here.

## Architecture Components

`session/manager.py::SessionManager` (`step`, `advance_to`, `_catch_up_locked`, `MAX_SAVE_SPAN_US`, `rewind_to` for the pattern to mirror); `session/inprocess.py::InProcessSession.step/advance_to` (turn a refusal into `Ack(ok=False, reason)`); `ui_web/server.py` `/step` and `/advance` routes (map a refused `Ack` to HTTP 400 exactly as `/rewind` and `/undo` do); `ui_web/static/app.js` (palette, `fireInject`, `showLoadFailure`, `previewOrder`, `drawRibbon`, `stepBy`). Load-bearing invariants touched: deterministic core (the engine is **not** edited; the bound is checked before `Simulation.advance_to` is called, reading `ctx.start_epoch` and `sim.clock.now` only); session lock (the check runs under `_locked` like the rewind guard); fog of war and content-as-data (untouched).

## Interfaces

- `POST /api/sessions/{sid}/step` (body `{dt_sim_s}`) and `POST /api/sessions/{sid}/advance` (body `{t}`): requests unchanged. New: a non-finite or negative-resulting step, a target earlier than now, or a target later than `start_epoch + 366 days` answers **HTTP 400** with a reason naming the span, state and clock unchanged. A target equal to now, or exactly at the ceiling, is accepted. The seat rule (`_require_white`, 403) is unchanged and still checked first.
- `SessionManager.advance_to(t)` and `.step(dt)`: raise `ValueError` before any state change for a target outside `[now, start_epoch + MAX_SAVE_SPAN_US]` or a non-finite `dt`. `InProcessSession.step/advance_to` return `Ack(ok=False, reason)`, mirroring `rewind_to` (`inprocess.py:218-226`).
- `SessionManager._catch_up_locked` (the lazy real-time clock): the wall-derived target is clamped to the ceiling; at the ceiling the catch-up is a no-op and the clock stays pinned there (see Design Decision 3).
- `GET /clock`: unchanged (it already carries `start_epoch`). **No `end_epoch` field is added** (no consumer; a feature).
- Console: no new element or route. `#control-status` (the `IP-1073` aria-live line, visible to every seat, `index.html:247`) is the one place player-visible refusals go.

### Design Decisions

1. **One span, stated once.** The ceiling reuses `SessionManager.MAX_SAVE_SPAN_US` (366 days) so the controls and the save cannot disagree again (`FR-4330` Rationale). A small private helper on `SessionManager` returns the ceiling (`start_epoch` plus the constant); `validate_save`'s existing check (`_check_final_time_span`, `manager.py:1099-1110`) and the new advance check both call it where practical, but the save check's wording and behaviour are **not** changed (pinned by `IP-1103`'s tests).
2. **Where the check lives.** In `SessionManager.advance_to` (the one choke point: `step` calls it, `InProcessSession` calls it, the lazy clock is separate), next to the `IP-1074` rewind guard. **Risk and fallback:** many engine-level tests call `SessionManager.step/advance_to` directly, and some may advance on a session whose start epoch differs from what they assume or by a huge step. The build greps every caller (`grep -n "advance_to\|\.step(" spacesim`) and runs the suite after the change. If more than a handful of existing tests break for reasons that are not a real defect, move the **upper** bound (not the backwards check, which the engine already enforces) to `InProcessSession.step/advance_to`, as `IP-1173` did for the draft-session rule, and record that in the completion note. Either way the HTTP behaviour is identical.
3. **The running clock stops at the ceiling.** Without this the bound is bypassed by pressing Play and waiting (a 600x clock reaches 366 days in about 15 hours of wall time), producing the same unloadable save. `_catch_up_locked` clamps its target to the ceiling and does nothing further; it does **not** pause the clock or raise (a pinned running clock is harmless; auto-pause is a behaviour decision for the owner, the same family as the open rewind question `L-6`). If the build finds `catch_up` is called with the lock held in a way that makes the clamp awkward, it stops and routes the question instead of improvising.
4. **Non-finite steps.** `step(dt)` with `dt` not finite (`NaN`, infinity) is refused with a reason. A finite but astronomically large `dt` (for example `1e300`) is refused by the ceiling check; the build must make sure the integer conversion of the product cannot raise `OverflowError` before the check (check the finite/size condition first).
5. **Palette gate, and what else is gated.** The two inject palette sources (the `fire inject` loop and the `inject lib:` loop) are built only when the seat is White, using the same seat test `IP-1073` used for the time entries. The build also reads every other `PALETTE.items` entry against the route table's White-only list (`_require_white` routes in `server.py`) and gates any other entry that reaches one, recording the audit result (entries examined, entries gated) in the completion note. No new palette entry is added.
6. **Player-visible refusals.** `fireInject` (reachable by White via the button, and via the palette only for White) reports a failure through `reportControlError("Inject", e)` **in addition to** `#inject-result`, so a refusal is never visible only in a hidden element. For White nothing changes visibly except that the failure is also in `#control-status`; for any seat that somehow reaches the call (a pop-out, a stale handler) the reason shows.
7. **Load-failure readout.** `showLoadFailure` keeps writing into `#session` when the tab has **no live session** (`SID` unset; the first-load failure the existing tests rely on). When `SID` is set it writes the same text (message and problems list, via `refusalParts`) into `#control-status` and leaves `#session` untouched, so a refused Load never overwrites the readout of a tab that is still connected. The text keeps the words "Load failed".
8. **Observer dry-run.** `previewOrder` returns before posting when the seat is Observer (the button is already disabled for that seat). It must still clear a stale preview. No server change: the server's 403 for Observer stays (`IP-1130`).
9. **The 404.** `drawRibbon` does not request windows for an actor that is not an own satellite: it returns after drawing the existing "no passes / not a satellite" message when the actor's kind (from `ASSETS`) is not a satellite kind, or when the seat is Observer (`_owns` is false for Observer: it has no own assets). The build confirms the exact kind strings from `ASSETS` / the scene before coding the test. The route and `windows_ahead` are unchanged (their 404 is the fog/ownership contract).
10. **One advance route in the console.** The palette's `stepBy` computes `SCENE.now + s`, where `SCENE.now` is the last polled time and lags the server's lazy clock (at 600x one second of lag is ten minutes), so a +1 minute entry can land in the past and, after this package, would be a spurious refusal. `stepBy` is changed to post `/step` with `dt_sim_s: s` (the route the toolbar +1m/+10m/+1h buttons already use), so the server computes the target from its own now. This is a bug fix for the exposure `L-1` names, not a new control. Two existing browser tests that route-mock `**/advance*` are updated to the `/step` URL (see Files to Modify).
11. **Not decided here.** Whether an advance to the ceiling should pause the clock, whether rewind pauses the clock (`L-6`), and whether 366 days should be configurable: owner questions, recorded, not answered.

## Files to Create

- `spacesim/tests/test_time_advance_bound.py` — server and session cases for the advance bound, backwards refusal, non-finite step, catch-up clamp and save round trip.
- Browser cases are added to the existing `spacesim/tests/test_browser_console_rules.py` (no new browser module; it already holds the harness and the seat helper `c.seat(...)`).

## Files to Modify

- `spacesim/session/manager.py` — `advance_to`/`step` guard, ceiling helper, `_catch_up_locked` clamp (Decisions 1-4). `rewind_to`, `undo_last`, `validate_save`/`_check_final_time_span` behaviour unchanged.
- `spacesim/session/inprocess.py` — `step` and `advance_to` catch the `ValueError` and return `Ack(ok=False, reason=...)`; the draft-session rejection stays first.
- `spacesim/ui_web/server.py` — `/step` and `/advance`: a refused `Ack` becomes HTTP 400 using the same pattern as `/rewind` (`server.py:485-488`). Update both docstrings to state the span. Seat check order unchanged.
- `spacesim/ui_web/static/app.js` — `PALETTE.items` inject entries (White only; audit of the rest), `fireInject`, `showLoadFailure`, `previewOrder`, `drawRibbon`, `stepBy` (Decisions 5-10). No change to `index.html` or `style.css` is expected; if the `#control-status` line needs a rule to wrap a multi-line problems list, add it to `style.css` and say so.
- Existing tests whose assertions the change moves (each listed in the completion note, none weakened):
  - `test_browser_console_rules.py::test_a_refused_time_control_is_reported_not_thrown` (mocks `**/advance*`; the palette now posts `/step`, so the mock pattern becomes `**/step*`).
  - `test_browser_console_rules.py::test_a_refused_load_shows_its_reason_and_leaves_the_session_running` (both seats), `::test_an_unparseable_save_file_is_reported` and `::test_a_player_seat_loading_a_vignette_sees_the_refusal`: they wait on `#session` containing "Load failed". For a tab with a live `SID` the assertion moves to `#control-status`; for a tab with no session it stays on `#session`. Read each test to see which case it is before editing; the first test's name already says the session must stay running, so it additionally asserts `#session` is **unchanged**.
  - Any test in `test_web.py`, `test_white_only_controls.py`, `test_white_control_correctness.py`, `test_undo_clock_floor.py` or the engine-level modules that advances by more than 366 days or backwards and expects success: found by running the suite; updated to expect the refusal or to stay inside the span.
- **Tag-only edits (no assertion or body change), retag to `FR-4330`:**
  - `test_white_control_correctness.py`: the rewind-span tests at lines 43-81 (`test_rewind_to_zero_is_refused_...`, `test_rewind_before_start_and_after_now_is_refused`, `test_the_span_edges_are_allowed`, `test_rewind_to_start_leaves_a_start_sized_save`) from `FR-4310`/`NFR-1600` to `FR-4330` (and `NFR-1600` where the test is a refusal).
  - `test_undo_clock_floor.py`: the module-level `pytestmark` (line 18) becomes `FR-4330`, `NFR-1600`; the two tests tagged `FR-4310` at lines 173 and 199 become `FR-4330`; the `FR-7220` save case stays and gains `FR-4330` (criterion 4).
  - `test_save_load_robustness.py`: `test_final_time_boundaries_load` and `test_final_time_ceiling_is_one_year_and_exceeds_shipped_horizons` gain `FR-4330` beside `FR-7230`/`NFR-1600` (the 366-day ceiling is now stated there too).
  - **The `IP-1334` guard pins tag sets.** `spacesim/tests/test_origin_retag.py` lists `EXPECTED` rows for `test_save_load_robustness.py` (lines 112-121 at the tip), so the two retagged tests' rows are updated to the new tuples **in the same commit**; the guard's logic, counts and other rows are not touched, and a retag that moves a row not listed there needs no guard edit. Verify with the guard itself, not by reading it.
  - Regenerate the RTM Test column (`python3 -m pytest --origin-report=rtm`) in the same commit; `FR-4330` gets its first Test-column entries from this and the new tests.

## Implementation Tasks

1. Write the failing tests below first (server cases, then browser cases); run them and record that each failed for the stated reason (cases 1-8 and 11-17 expected to fail today).
2. Manager: add the ceiling helper; guard `advance_to`/`step` (backwards, above ceiling, non-finite, overflow-safe); clamp `_catch_up_locked` (Decisions 1-4). Grep all callers first (Decision 2) and run the suite before moving on.
3. Session and route: `Ack(ok=False, reason)` in `InProcessSession`; HTTP 400 in `/step` and `/advance`.
4. Console: `stepBy` to `/step`; palette inject gating and audit; `fireInject` visible failure; `showLoadFailure` split; `previewOrder` Observer guard; `drawRibbon` skip (Decisions 5-10).
5. Update the existing tests the work moves; apply the tag-only retags and the matching `EXPECTED` rows; regenerate the RTM.
6. Run the full suite (`-m "not browser"`, then `-m browser`, then unfiltered once so the count-pinned guards run), the permanent gates, `test_doc_integrity.py`, `test_test_origins.py`.
7. Update the documentation below and the Master Build Plan row to `COMPLETE` (never `VERIFIED`).

## Tests to Add

Server and session cases in `spacesim/tests/test_time_advance_bound.py`; each carries `@pytest.mark.verifies(...)` (module `pytestmark` for the shared IDs). Origins: `FR-4330` (primary), `NFR-1600`, `FR-4310`; the module's own DoD case carries `IP-1076`.

1. `POST /advance` to exactly `start_epoch + 366 days` succeeds; to one microsecond later is 400 naming the span; the clock and event log are unchanged after the refusal (`FR-4330` criterion 3).
2. `POST /advance` with `t` earlier than the current time is 400, not 500, nothing changed; `t` equal to now succeeds as a no-op (`FR-4330`, `NFR-1600`) — the backwards half fails today with 500.
3. `POST /step` with a negative `dt_sim_s` is 400, clock unchanged; `dt_sim_s = 0` succeeds (`FR-4330`).
4. `POST /step` with a non-finite `dt_sim_s` (NaN, infinity, sent as the JSON the route accepts) and with `1e300` is 400 with a reason, never 500 and never an `OverflowError` (`NFR-1600`).
5. The `M-2` probe: advance 30 days, save, load = 200; advance to the ceiling, save, load = 200; advance past the ceiling is refused so no unloadable save can be produced (`FR-4330` criterion 4; `FR-7230`). The 370-day case fails today at the load.
6. Lazy clock: with the clock running and the anchor arranged so that the wall-derived target is beyond the ceiling (rate and anchor set through `set_clock`/the manager's anchor fields, or a monkeypatched wall clock; the manager's existing tests show which), `catch_up` leaves `now == start_epoch + 366 days`, does not raise, and a following save loads (`FR-4330`).
7. `step`/`advance_to` after an undo-to-start and after a rewind: bounds are measured from the **start epoch**, not from where the clock was rewound to (`FR-4330`).
8. Layering: `SessionManager.advance_to` raises `ValueError` before any change; `InProcessSession.advance_to` returns `Ack(ok=False, reason=...)`; the route turns it into 400 (mirror of `test_layering_value_error_then_ack`) (`NFR-1600`).
9. Seat rules unchanged: Blue, Red, Observer and no seat still get 403 on both routes, **before** any bound check (a refused seat with an out-of-span body is 403, not 400) (`FR-4310`, `FR-4320`).
10. Draft sessions: both routes still answer the draft-session refusal (`FR-4310`).
11. Property-style invariant: over a seeded random sequence of `step`/`advance_to`/`rewind_to`/`undo_last` calls (refusals tolerated, durations drawn up to and past the ceiling), `start_epoch <= now <= start_epoch + 366 days` after every call and the final save loads (`FR-4330`).
12. Determinism: a session built from the same seed, advanced by a mixed accepted/refused sequence, has an event log identical to one that received only the accepted calls (a refusal logs nothing) (`FR-4330`; also covered by the permanent determinism gate).
13. Module DoD case: a session advanced to the ceiling in 30-day steps reproduces its state from its own event log (`IP-1076`).

Browser cases, appended to `spacesim/tests/test_browser_console_rules.py` (`@pytest.mark.browser`, using the `console` fixture, `c.seat(...)`, `c.errors`):

14. A Blue, a Red and an Observer seat: the palette offers no entry beginning "fire inject" or "inject lib" (use `_palette_labels(c, "inject")`); White's palette still offers them (`FR-4310`, mirror of `test_a_non_white_seat_is_not_offered_time_control_in_the_palette`).
15. White fires an inject whose request is mocked to 403 (`c.page.route`): the reason appears in `#control-status` (visible) and no unhandled rejection is recorded (`NFR-1600`).
16. Joined Blue tab (live `SID`, polling on): a refused save-file load leaves `#session` text unchanged, shows "Load failed" in `#control-status`, and the realtime clock keeps running (`NFR-1600`). Modifies the existing refused-load test as listed above rather than duplicating it.
17. Console quiet on load and seat switch: after loading `leo-isr-denial` as White with `BLUE-RADAR` selected as the actor, no request to `/windows/blue/BLUE-RADAR` is made (collect `page.on("request")`) and `c.errors == []`; after switching to Observer, no `/order/validate` request is sent and `c.errors == []`; selecting a satellite as White still requests its windows and draws the ribbon (`NFR-3030`, `NFR-1600`).
18. Palette "advance +1 min" posts to `/step` with `dt_sim_s == 60`, and with the lazy clock running at a high rate the advance is accepted (no spurious refusal from a lagging `SCENE.now`) (`FR-4330`).

## Documentation Updates

- `CLAUDE.md`: the `session/` bullet states the advance bound beside the `IP-1074` rewind range and `IP-1075` undo floor, and that the running clock stops at the span's end (one sentence). **The stale status text (469 tests, "browser GUI unverified headless") is out of scope** (`M-5`, owned by `03`/`04`/`11`).
- `docs/training/08-http-api-reference.md` and `docs/training/12-white-cell-manual.md` (clock section, `WCM-4`): `/step` and `/advance` refusals and the span; the palette inject entries are White-only; a refused Load in a joined tab shows in the status line. Use `docs/training/15-manual-traceability.md` §15.1 to find the sections; training pages are `08-training-manual-authoring`'s scope, so list any not edited in the completion note rather than leaving them silently stale.
- `docs/requirements/01-functional-requirements.md` `FR-4330` Notes: **not edited here** (`04`'s file); the completion note recommends flipping "required, not yet built" to "met as built" once `VERIFIED`.
- RTM Test column regenerated (never hand edited); `FS-106` `Referenced By` (metadata only); `packages/INDEX.md`; Master Build Plan row, tally and graph note; `ROADMAP.md`; this header.

## Definition of Done

- Tests 1-18 exist, were seen failing for the stated reason where marked, and pass.
- An advance or step beyond `start_epoch + 366 days`, before now, or non-finite is a 400 with a reason, never a 500, and changes nothing; a session at the ceiling saves and loads; a running clock stops at the ceiling.
- Blue, Red and Observer are not offered inject palette entries; a refused inject, refused Load in a joined tab and refused time control each show their reason in a visible element for every seat; the refused Load does not overwrite `#session` in a live tab.
- Loading the console and switching seats produces no console error from `/windows/<sensor>` or from Observer dry-runs.
- The retags in "Tag-only edits" are done, the `EXPECTED` rows in `test_origin_retag.py` match, the RTM is regenerated, and no allow-list grew.
- The full suite (both marker partitions and one unfiltered run), `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py` and `test_test_origins.py` are green.
- Documentation above updated; row `COMPLETE` in the Master Build Plan (not `VERIFIED`).

## Verification Checklist

- [ ] Reproduce the pre-fix symptoms on the parent commit (advance 370 days then load = 400; negative step = 500; Blue palette inject entry and its 403 written to a hidden element; Observer 403 dry-run and the `BLUE-RADAR` 404 in the console) and see each gone.
- [ ] Every new test names its origin; each failing-first case recorded.
- [ ] `git diff` of `spacesim/engine/` is empty (the bound is outside the engine); `test_import_guard.py` green.
- [ ] `test_determinism.py` green; a refused advance appends nothing to the event log.
- [ ] `validate_save` wording and `IP-1103` tests unchanged and green.
- [ ] The retagged tests' bodies are AST-identical to before (tag lines only) and the `test_origin_retag.py` `EXPECTED` rows equal the new tags.
- [ ] The existing-test edits are listed in the completion note and none weakens a check (the three load-failure tests still prove the reason is shown).
- [ ] The palette audit result (entries examined, gated) is in the completion note.
- [ ] `test_doc_integrity.py` and `test_test_origins.py` green; RTM regenerated; no allow-list grew.
- [ ] Collected-test count stays below `COLLECTED_UPPER` (1700) in `test_origin_retag.py` (about 18 added; the suite is 1637 at the review tip).

## Dependencies

All `VERIFIED`: `IP-1074`, `IP-1075`, `IP-1103`, `IP-1073`, `IP-1340` (and, through them, `IP-1068`, `IP-1130`). No package depends on `IP-1076`. Relationship to `IP-1077`: independent content, no shared production file except `server.py` (different routes) and the `ui_web` module as a whole; see Ordering.

**Ordering.** Build `IP-1076` first, then `IP-1077`, then `IP-1078` (docs only). `IP-1076` and `IP-1077` both edit `spacesim/ui_web/server.py` and add to the RTM; running them in sequence avoids a merge conflict on the RTM Test column and on `test_origin_retag.py`'s `EXPECTED` rows. They can be built in either order if sequential.

## Risks

- **Existing tests that advance past 366 days or call the manager with odd epochs** (Decision 2): mitigated by the grep and the fallback to the session layer; a failure that reveals a real vignette horizon beyond 366 days would be a finding to route (`FR-4330` would need revisiting), not to paper over. The review measured the longest shipped horizon well inside the span (`test_final_time_ceiling_is_one_year_and_exceeds_shipped_horizons`).
- **Browser tests depend on Chromium at `/opt/pw-browsers`**; they skip loudly where it is absent, as `IP-1340` defines. The new cases must not use fixed sleeps (wait on page state).
- **Count-pinned guards.** Adding about 18 tests moves the collected count from 1637 toward 1655; `COLLECTED_UPPER = 1700` (`L-5` in the review) leaves little room for `IP-1077`'s additions as well (about 20 more, total about 1675). Not widened here (a test-guard redesign is outside the bug-only brief); if the build lands within 10 of the bound it says so in the completion note so a follow-up can re-express the guard as "no test lost".
- **`app.js` is large and shared**; every edit is local to the named functions. The browser suite is the safety net.
- **Palette audit may find another White-only entry.** Gating it is in scope (same defect); finding a White-only *panel* with a hidden refusal element elsewhere is not, and is routed to the backlog.

## Rollback Considerations

Revert the commit. No data migration: no save format, no event-log shape and no route signature changes (the new behaviour is additional refusals and a clamp on the lazy clock). The only persisted effect of the old behaviour was an unloadable save from an over-advanced session; such saves remain refused by `validate_save` after a rollback, exactly as today.
