# VR-1160 — Verification Report: Role-Scoped Command Catalog & Assignment Scoping (FR-3510, FR-3520)

> **Document ID:** VR-1160
> **Version:** 2.0 (supersedes v1.0, which `RETURNED` the package; v1.0 is kept in the appendix)
> **Status:** ✅ Final — result **RETURNED** (second time)
> **Dependencies:** [IP-1160](../packages/IP-1160-role-scoped-command-enforcement.md) v1.2
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` return of `IP-1160` (no `VERIFIED` written)
> **Feature Mapping:** [FS-116](../../features/FS-116-role-scoped-command-catalog.md), [ADS-3500](../../architecture/ADS-3500-role-scoped-command-enforcement.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1160 v1.2 after its re-run: fix commit `bdf7e23` on top of implementing commit `00dd883` and the v1.0 report `0774a03`, branch `claude/ip-1160-build` (parent of the package `3368f89`). Verified in a fresh session in a separate worktree. No code, package, spec, requirement or `docs/pipeline/` file was edited; mutations ran on a private scratch copy of the source tree.

## Result

**RETURNED** — 1 failed check (M-4, Medium), plus 1 owner-decision deviation (M-3, carried from v1.0) and Lows. v1.0's M-1 and M-2 are fixed on the routes v1.0 named, and all three Lows are closed. The return is for one residual fog-of-war leak of the same class as v1.0 M-2, still open on the order routes: **a Red request can read Blue's role-gated asset ids and Blue's seat bindings through `POST /order` and `POST /order/validate`** (M-4). Everything else is green.

## v1.0 findings re-checked

| v1.0 | Re-check | Result |
|---|---|---|
| M-1 non-string `verb` returns 500 | Over HTTP, `/order` and `/order/validate`, 4 seats (bound bus, payload, both, unbound) x 14 verb values (list, nested list, dict, nested dict, int, float, `null`, `true`, `false`, empty, 20,000-char, unknown string, `["isr.collect_now"]`): all 200, and for every non-string value the ack equals the same request without a seat (0 diffs); no order id consumed. A non-dict `params` is a 422 from the model, as before. Mutation removing the `isinstance` guard fails `test_m1_any_verb_value_gets_the_same_ack_as_without_a_seat_at_manager_level`. | Closed |
| M-2 `GET /roles/scope` leak | Probed 7 console values (none, white, blue, red, observer, bogus, empty) x 4 operator seats (bound-bus, unbound, bound-elsewhere, role `admin`). Public (no seat): 200, only `{"verbs": ...}`, no asset id, no seat. Seat without a valid `cell` (none, observer, bogus, empty): 403 for all 16. White and Blue: full scope. Red: `bound` false, `gated_assets` and `bound_assets` empty, asset id absent; the Red response for the bound-to-Blue seat equals the response for an unbound seat apart from the echoed seat name; response sizes within 3 bytes of each other and 300 sequential requests cost 3.11 ms (bound) vs 3.21 ms (unbound): no usable side channel. Client sends `cell` (browser tests 21, 23 and 24 fail when the parameter is removed). Drift test still passes. Mutations: cell filter removed, Red unbind removed, public branch returning the full scope, the 403 removed — each killed. | Closed **for the GET route**; see M-4 for the same information on the order routes |
| L-2 Evade quick action omits the seat | `app.js` now sends `o-seat`. Mutation removing it is killed — but only by a static regex test (`test_drill_down_and_evade_paths_...`), not a browser test (see L-6). | Closed |
| L-3 drill-down filter untested | `test_24` (browser, ran, 0 skipped) drives `openDrill` for a bus and a payload seat. Mutation `verbsForSubsystem(a, sub, undefined)` now fails `test_24`. | Closed |
| L-4 `roles/assign` seat charset | `RoleAssignmentRequest.seat` now applies the order route's charset. Mutation removing it is killed. The builder returns **422** where the order route's own bad-seat answer is also 422 (a Pydantic validation error, consistent with `OrderRequest.seat` and `GET /roles/scope`); v1.0's note of "400" was wrong. 422 is correct and consistent. | Closed |
| M-3 execute-time re-check | See "M-3 judgement" below. | Open as a known deviation (owner decision) |

## M-3 judgement

The role is checked at submission only; a rebinding by White applies to later submissions, and an order already queued still executes. The builder recorded this in `CLAUDE.md` (Code Map: "a rebinding applies to later submissions, already queued orders still execute ... an execute-time re-check would need rebinding to be a logged event"), the ICD (INT-0004/INT-0006: "Role is checked at submission only (a rebinding applies to later submissions)"), the MBP row and its tally note, and the package completion note. The statements are accurate, and the engineering reason is right: `role_assignments` is session state, not engine state and not in the event log, so a check inside the executed handler would read data replay does not reproduce, and replay would stop equalling live; an execute-time check would first require logging each rebinding as an event (a design change to `FS-102`/`ADS-3500`). A submission-time gate is the right call for this release.

It is still a **known deviation from the baseline text**, which no document states as such: `FR-3520` Postconditions say "rejected at execution time", and `FS-116` System Behaviour and Security Considerations say "at both submission time and ... again at execution time". `FR-3520`'s **Acceptance Criterion** ("a payload-verb command submitted directly for Asset X is rejected") is met and tested. The requirement and spec text were not amended (the diff touches neither). **For the owner:** accept the submission-time reading and amend `FR-3520`'s postcondition and `FS-116` through `04`/`06` (the recommended course), or schedule a logged-rebinding package. Not counted as a failed check.

## Definition of Done audit

| Item | Evidence | Pass |
|---|---|---|
| `issue_order`/`validate_order` and wrappers accept an optional operator `seat`; callers omitting it unchanged | `manager.py`, `inprocess.py`, `api.py` read; `role_scope` signature updated everywhere. Omitted or empty seat: the omitted and empty seats in the 768-request run were never role-refused; test 10 and test 18 (all 19 vignettes) green | Pass |
| Bus-only / payload-only / both gate both operations | Real HTTP through `TestClient` over the app: 8 seats (bus, payload, both, bound elsewhere, role `admin`, ghost, omitted, empty) x all 48 verbs x validate and issue = 768 requests, **0 mismatches** against an independently computed expectation (rule re-derived in the probe from `role_assignments` and `ROLE_SCOPE_BY_VERB`, not from the code under test) | Pass |
| Offered list follows the scope; client and server cannot drift | Browser tests 21-24 ran (junit: 4 cases, 0 skipped); static test 19; `GET /roles/scope` `verbs` equals `ROLE_SCOPE_BY_VERB` | Pass |
| `DEFENSE_VERBS` split six `bus` / two `payload` | Re-read; the `def.harden` mutation is killed | Pass |
| A refusal registers no order, consumes no id, writes no log entry | Over the 768 requests the order-list length, order counter and event-log length were compared before and after every refusal: unchanged; no refusal carried an id | Pass |
| Dry-run agrees with issue | For all 48 verbs x 2 role seats on fresh sessions, `validate_order` and `issue_order` returned identical `(ok, reason)` (96 cases) | Pass |
| `role_assignments` save/load/`validate_save` | `GET /save` then `POST /load_save` (White seat): a save with the key loads and gates the same; a save without the key and a save with `null` load as `{}`; a list, a string, a malformed entry, a non-string role and a missing field are each 400 before replay. Old save plus a seat: `role_scope_not_assigned`; no seat: unchanged | Pass |
| IP-1087 pending-approval rebuild unaffected | `test_gated_order_resume` and the White-only tests green; `from_state` path untouched in the diff | Pass |
| 19 shipped vignettes unaffected, tutorials | `test_vignette_tutorials.py` green (all 19, with and without a seat via test 18) | Pass |
| ICD and `CLAUDE.md` updated; RTM Test column regenerated | ICD rows and `CLAUDE.md` Code Map updated for the re-run; `--origin-report=rtm` reports "regenerated (unchanged)" and `git status` stays clean | Pass |
| Observer 403 and White-only rules unchanged; finite guards first | Tests green; `cell=observer` with a seat is 403 on both order routes; the NaN body is 400 before the gate | Pass |

## Verification Checklist audit

| Item | Evidence | Pass |
|---|---|---|
| Both new modules green; browser tests run | `-m browser`: 40 tests, 0 failed, 0 skipped, exit 0; tests 21-24 present in the junit file | Pass |
| `test_determinism.py`, `test_import_guard.py` green; engine unchanged | Run by name, exit 0. `git diff 3368f89 HEAD -- spacesim/engine` is empty | Pass |
| Full suite, zero regressions | See Test run | Pass |
| `test_test_origins.py`, `test_origin_retag.py`, `test_doc_integrity.py` green | Run by name, exit 0; no allow-list changed | Pass |
| IP-1068/1072/1082 sweeps, no new row | `test_white_only_*`, `test_white_control_nonfinite` green; **but** see M-4: the new no-cell and cell-scoped read has no sweep of its own | Pass with M-4 |
| A refused order leaves orders, counter and log as before | As above | Pass |
| A pre-change save loads and plays unchanged | As above | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Pass |
|---|---|---|---|---|
| FR-3510 | `app.js` `actionsFor`/`OP_SEAT`/`ROLE_SCOPE`, `index.html` seat input, `GET /roles/scope` | Browser 21-24, static tests 19-20 | Lists the browser and static tests; equals tool output | Pass |
| FR-3520 | `SessionManager.role_scope_check`, `issue_order`/`validate_order`, `OrderRequest.seat` | `test_role_scope_enforcement.py` (incl. M-1/M-2 cases) | Equals tool output | Acceptance criterion met; the postcondition wording is submission-only (M-3, owner decision); **fails the baseline's fog posture on the order routes (M-4)** |
| NFR-1600 | Non-string verb handled | `test_m1_*` | Row regenerated, equals tool output | Pass |
| FR-6220 | Public read is static; seat reads are cell-scoped and Observer-refused | `test_m2_*` | Equals tool output | Pass for `GET /roles/scope`; M-4 for the order routes |
| NFR-2840 | Four browser cases tagged | Ran, not skipped | Equals tool output | Pass |

## Test run

| Run | Command (run from the worktree) | Result |
|---|---|---|
| Unfiltered | `python3 -m pytest -q -p no:cacheprovider --junitxml=...` | **2047 tests, 0 failed, 0 errors, 3 skipped, exit 0** |
| Not browser | `python3 -m pytest -q -m "not browser" --junitxml=...` | **2007 tests, 0 failed, 4 skipped (the 3 above plus the RTM-equality test, which skips on a partial collection by design), exit 0** |
| Browser | `python3 -m pytest -q -m browser --junitxml=... -rs` | **40 tests, 0 failed, 0 skipped, exit 0** |
| Gates and doc checks | `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py`, `test_determinism.py`, `test_import_guard.py`, `test_vignette_tutorials.py`, `test_gated_order_resume.py`, `test_white_only_controls.py`, `test_observer.py` | exit 0 |
| RTM | `python3 -m pytest --origin-report=rtm` | "regenerated (unchanged)"; tree clean |

The 3 skips are pre-existing "vignette does not apply" skips. 2007 + 40 = 2047.

### Mutations (private copy; each restored)

Killed: `isinstance(verb, str)` guard removed; fog cell filter removed; Red-unbind removed; public branch returns the full scope; the seat-specific 403 removed; `roles/assign` charset removed; drill-down asset id dropped (browser `test_24`); Evade seat removed (static test); client `cell` removed (browser `test_21`). v1.0's 17 mutations were not re-run except where the fix touched them (the fix diff touches only the lines above).

## M-4 (new) — fog leak through the order routes

Reproduced over real HTTP with the shipped test fixture (Blue satellite `ISR-EO-1` covered by `roles_needed`; operator seats `bus-op` bound `bus`, `pl-op` bound `payload`; Red console seat):

| Red request (`cell=red`, `actor=ISR-EO-1`, command, validate) | Reason returned |
|---|---|
| no seat | `not_owner` |
| seat `stranger` (unbound) | `role_scope_not_assigned` |
| seat `bus-op`, verb `isr.collect_now` | `role_scope_out_of_scope` |
| seat `bus-op`, verb `eps.shed_load` | `not_owner` |
| seat `pl-op`, verb `isr.collect_now` / `eps.shed_load` | `not_owner` / `role_scope_out_of_scope` |
| unbound seat on an ungated Blue asset (`GS-NORTH`) | `not_owner` |

`role_scope_check` runs before ownership is checked, so a Red cell that sends another cell's asset id and any seat name learns (a) which of Blue's assets are role-gated (`role_scope_not_assigned` against `not_owner`) and (b) which role each guessed seat is bound to (`out_of_scope` against `not_owner`), by enumeration. That is exactly the information v1.0 M-2 had removed from `GET /roles/scope`, and what the re-run's own test (`test_m2_red_cannot_learn_blues_role_gated_assets_or_assignments`) and `CLAUDE.md` say Red cannot learn. The test covers only the GET route. It breaks invariant 3 (fog-of-war at the `SessionAPI`/`CellController` boundary) in the sense of `docs/AUDIT-2026-06.md`'s trust model, and the package's own claim that "one cell learns nothing of the other's assets or assignments". A refused probe registers no order (counter 0 after all probes). Fix direction (not applied here): run the gate only when the issuing cell owns the actor (or is White), leaving the engine's `not_owner` for everyone else, and add the order-route case to the M-2 test.

## Console in headless Chromium (White, Blue, Red, Observer)

The browser suite ran for real (40 tests, none skipped), including the White/Blue/Red/Observer console cases of the earlier packages and IP-1160's tests 21-24: the Operator seat field, the filtered action list for bound seats, the disabled Issue with the role reason before any send, the drill-down buttons and the empty-seat full list, each with `c.errors == []`. The v1.0 manual probe (seat persistence, `localStorage` failure) was not repeated; the diff does not touch those paths.

## Determinism and invariants

`engine/` unchanged. The gate sits in `session/` before `OrderSystem` and reads session state only; test 16 (replay equals live) and the 768-request run (refusals leave the world and log untouched, then `from_state` equal) hold. The only invariant breach is the fog leak in M-4.

## Scope audit

The fix commit is 14 files, all in the package's file set, the implied tests or the ledgers (`CLAUDE.md`, `ROADMAP.md`, MBP, packages index, RTM, ICD). No `docs/pipeline/`, `docs/training/`, `engine/`, requirement or spec file. In scope.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| **M-4** | **Red (or Blue) learns the other cell's role-gated asset ids and operator-seat bindings through `POST /order` and `POST /order/validate`** (table above): the gate precedes the ownership check and its reason codes differ from `not_owner`. Same class as v1.0 M-2, fixed only on `GET /roles/scope`. No test enumerates the order routes for it. | Medium | `08-code-implementation` re-run (apply the gate only for the owning cell or White; add the cross-cell cases to the test) |
| M-3 | Execute-time re-check not built (judged above; submission-time is the right engineering call and is accurately documented in `CLAUDE.md`/ICD/MBP), but `FR-3520`'s postcondition and `FS-116` still say execution time. | Medium (owner decision, not a failed check) | Owner, then `04`/`06` (amend wording) or a new package (logged rebinding) |
| L-1 | Omitting `seat` skips the gate (by design, package Owner awareness 1). Unchanged; for the owner. | Low (owner decision) | Owner / `04` |
| L-5 | With browser storage blocked, older console code throws uncaught `SecurityError`s. Pre-existing. | Low | `00-intake` |
| L-6 | The Evade seat is covered only by a regex test on `app.js`, not a browser test; a behavioural regression of the `data-evade` handler other than removing the `seat` text would survive. | Low | `08` |
| L-7 | `packages/INDEX.md`'s IP-1160 row still says "3 browser cases"; there are 4 (`test_24`). Doc nit. | Low | `08` |
| I-1 | Manual-impact: the White/Blue/Red manuals describe the order panel and gain an Operator seat field; routed in the package to `08-training-manual-authoring`. | Info | `08-training-manual-authoring` |

## Ledger audit

Master Build Plan tally recounted from the package table before this update: 88 `VERIFIED`, 1 `COMPLETE` (`IP-1160`), 0 `READY`, 89 packages, as claimed. After this report: 88 `VERIFIED`, 1 `IN PROGRESS` (`IP-1160`, returned), 0 `COMPLETE`, 89. The RTM Test column equals the tool output for `FR-3510`, `FR-3520`, `FR-6220`, `NFR-1600`, `NFR-2840`.

## Next step

Re-run `08-code-implementation` on `IP-1160` against M-4 (a small `role_scope_check` ownership condition plus a test over both order routes). Ask the owner to accept or reject the submission-time deviation (M-3) so `04`/`06` can amend `FR-3520`/`FS-116`; if accepted, the next verification should be clean. After that, `FEAT-3500` closes and the release assessment can be refreshed.

## Appendix — v1.0 (superseded)

v1.0 returned the package at implementing commit `00dd883` with M-1 (HTTP 500 on a list or object `verb`), M-2 (`GET /roles/scope` outside the `FR-6220` named set), M-3 (no execute-time re-check) and Lows L-1 to L-5; its 384-combination matrix, mutation list and browser run found no other defect. Findings are carried and re-checked in the sections above.
