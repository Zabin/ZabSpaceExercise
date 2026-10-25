# VR-1160 — Verification Report: Role-Scoped Command Catalog & Assignment Scoping (FR-3510, FR-3520)

> **Document ID:** VR-1160
> **Version:** 1.0
> **Status:** ✅ Final — result **RETURNED**
> **Dependencies:** [IP-1160](../packages/IP-1160-role-scoped-command-enforcement.md) v1.2
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` return of `IP-1160` (no `VERIFIED` written)
> **Feature Mapping:** [FS-116](../../features/FS-116-role-scoped-command-catalog.md), [ADS-3500](../../architecture/ADS-3500-role-scoped-command-enforcement.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1160 v1.2, implementing commit `00dd883` on branch `claude/ip-1160-build` (parent `3368f89`). Verified in a fresh session in a separate worktree; no code, package, spec, requirement or `docs/pipeline/` file was edited. Parent comparisons and mutations were run on private scratch copies of the tree.

## Result

**RETURNED** — 3 failed checks (1 Medium defect in the shipped code, 2 Medium requirement-vs-implementation gaps), plus Low findings. Every Definition-of-Done item and every permanent gate is green, and the 384-combination HTTP probe found no wrong accept or refuse. The return is for a regression the package introduced (a role-gated order with a list or object `verb` now returns HTTP 500, where the parent answered `invalid_param`) and for two places where the shipped behaviour does not meet the Feature Specification or the baseline's own endpoint rule.

## Definition of Done audit

| Item | Evidence | Pass |
|---|---|---|
| `issue_order`/`validate_order` and the `InProcessSession`/`SessionAPI` wrappers accept an optional operator `seat`; callers omitting it unchanged | `manager.py`, `inprocess.py`, `api.py` diff. Omitted seat on a role-gated asset: `isr.collect_now` accepted `ord-193`, identical to the parent. All 19 vignettes iterated by test 18 | Pass |
| bus-only / payload-only / both gate `issue_order` and `validate_order` | HTTP probe on a real uvicorn server (vignette with `roles_needed`): 8 seats (bus, payload, both, other-asset, role `admin`, ghost, omitted, empty) x all 48 verbs x validate and issue = 384 combinations, **0 mismatches** against an independently computed expectation | Pass |
| Offered list follows the seat's scope; client and server tables cannot drift | Headless Chromium: bus-op 17 options (no `isr.*`, no `def.harden`), pl-op 6 (`isr.*`, `def.harden`, no `eps.*`), both 21, ghost 2 (no dotted verbs), empty 21. `GET /roles/scope` `verbs` equals `ROLE_SCOPE_BY_VERB` and `set(verbs) == COMMAND_VERBS`. Static test 19 killed the drift mutation | Pass |
| `DEFENSE_VERBS` split six `bus` / two `payload` | Re-read `ROLE_SCOPE_BY_VERB` and `buscommands.apply_command`. A mutation setting `def.harden`/`def.set_deception_mode` to `bus` is killed | Pass |
| A refusal registers no order, consumes no id, writes no log entry | Per refused combination the order list length, the event-log text and the order counter were compared before and after over HTTP: unchanged for all refusals. Parent reproduction: a bus-only seat sending `isr.collect_now` is accepted (`ord-1`, counter 1); the fix refuses `role_scope_out_of_scope`, counter 0. (A queued order writes no log entry at issue, so the counter is the discriminating signal.) | Pass |
| `role_assignments` survives save/resume; old save loads | Real `GET /save` then `POST /load_save`: bindings gate identically after load. Save with the key removed: loads 200, `{}`, a seat is then `role_scope_not_assigned`, no seat unchanged. `null` loads. List, string, non-object entry, non-string role, non-string key each 400 | Pass |
| 19 shipped vignettes unaffected | Test 18 plus the full suite; no shipped vignette declares `roles_needed` | Pass |
| ICD and `CLAUDE.md` updated; RTM Test column regenerated | ICD INT-0004/INT-0006 and change-log row; `CLAUDE.md` Code Map and trust sentence. `--origin-report=rtm` run on the tree reports "regenerated (unchanged)" and leaves `git status` clean | Pass |
| Observer 403 and White-only seat rule unchanged | Real HTTP: `cell=observer` with a seat is 403 on both routes; `roles/assign` 403 for blue; the finite-number guard and 422 seat charset run before the gate. Mutation moving the gate ahead of `_reject_observer` is killed | Pass |

## Verification Checklist audit

| Item | Evidence | Pass |
|---|---|---|
| Both new modules exist and are green; browser tests pass or skip loudly | Both modules present. `-m browser`: 39 passed, 0 skipped, exit 0; `test_21`, `test_22` and `test_23` ran (junit) | Pass |
| `test_determinism.py` green | In the 562-test gates run, exit 0 | Pass |
| `test_import_guard.py` green; engine unchanged | Gates run exit 0. `git diff --stat` shows no `spacesim/engine/` file | Pass |
| Full suite, zero regressions | See Test run | Pass |
| `test_test_origins.py` and `test_doc_integrity.py` green | Gates run exit 0; no allow-list grew | Pass |
| IP-1068/1072/1082 route sweeps pass, no new row needed | `test_white_only_controls/extension`, `test_white_control_nonfinite` in the gates run | Pass |
| Re-derive the `DEFENSE_VERBS` split | As above | Pass |
| A refused order leaves orders, counter and event log exactly as before | As above | Pass |
| A pre-change save loads and plays unchanged | As above | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Pass |
|---|---|---|---|---|
| FR-3510 | `app.js` `actionsFor`, `OP_SEAT`/`ROLE_SCOPE`, `index.html` seat input; server table via `GET /roles/scope` | Browser `test_21`-`test_23`, static tests 19-20. Drill-down filter untested (Low finding L-3) | Lists the browser tests; equals `--origin-report=rtm` output | Pass for the offered list and a direct submission. See M-2 for the new endpoint |
| FR-3520 | `SessionManager.role_scope_check`, `issue_order`/`validate_order`, `OrderRequest.seat` | `test_role_scope_enforcement.py` (18 cases + scope resolver) | Lists the enforcement tests; equals tool output | **Fail in part**: submission-time only (M-3), and M-1 |
| NFR-2840 | Three browser cases tagged | Ran, not skipped | Row regenerated | Pass |

## Test run

| Run | Command (run from the worktree) | Result |
|---|---|---|
| Unfiltered | `python3 -m pytest -q -p no:cacheprovider --junitxml=...` | **2039 tests, 0 failed, 0 errors, 3 skipped, exit 0** |
| Not browser | `python3 -m pytest -q -m "not browser" --junitxml=...` | **2000 tests, 0 failed, 4 skipped (the 3 above plus the RTM-equality test, which skips on a partial collection by design), exit 0** |
| Browser | `python3 -m pytest -q -m browser --junitxml=... -rs` | **39 tests, 0 failed, 0 skipped, exit 0** |
| Gates and doc checks | `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py`, `test_determinism.py`, `test_import_guard.py`, `test_vignette_tutorials.py`, `test_white_only_controls.py`, `test_white_only_extension.py`, `test_white_control_nonfinite.py`, `test_observer.py`, `test_session_setup.py`, `test_bus_commands.py` | **562 tests, 0 failed, 1 skipped (RTM equality on a partial collection), exit 0** |
| RTM | `python3 -m pytest --origin-report=rtm` | unchanged; tree clean |

The three skips in the full run are pre-existing "vignette does not apply" skips, unrelated to this package.

### Mutations (private copy of the tree; each restored)

Killed by a failing test: gate skipped in `issue_order`; gate skipped in `validate_order`; `def.harden`/`def.set_deception_mode` scoped `bus`; `BUS_VERBS` scoped `payload`; `role_assignments` dropped from the save; restore dropped in `from_state`; `validate_save` check disabled; `role_scope_not_assigned` turned into allow; `both` no longer covering; group id not matched; seat not passed by `/order`; seat not passed by `/order/validate`; Observer ordering reversed; client filter removed (browser `test_21`); operator seat not sent (browser `test_23`); `VERB_ROLE` drift (static test 19); seat charset removed; empty `verbs` in the scope read.

**Survived:** passing no asset id to the drill-down verb filter (`verbsForSubsystem(a, sub, undefined)`) — no test covers the drill-down buttons (L-3). I confirmed the shipped drill-down by hand (below).

## Console in headless Chromium (White, Blue, Red, Observer)

Driven against a real server with the role-gated vignette. All four seats render the Operator seat field. Blue, with the seat bound bus / payload / both / ghost / empty, shows the lists above. The subsystem drill-down buttons follow the same scope (bus-op: `eps.*`, `adcs.*`, `cdh.*`, `def.frequency_hop`, no `isr.*`; pl-op: `isr.*` and `def.harden` only). A payload verb forced into the dropdown with a bus-only seat disables Issue with the text "That command belongs to the other role on this asset" before any send; no order was created (0 orders). The seat persists across a reload through `localStorage`; with `localStorage` made to throw, the seat field, filtering and the refusal reason all still work, and the seat is simply not remembered. The IP-1160 code wraps both its storage accesses in `try/catch`. With storage blocked the page logs four uncaught `SecurityError`s from older code that reads storage unguarded (brief panel, toggles — not in this diff; L-5). One unrelated 404 resource request was logged. No console error comes from IP-1160 code.

## Determinism and invariants

`engine/` is unchanged; the gate sits in `session/` before `OrderSystem`, reads session state only, uses no wall clock or RNG. Replay equals live (test 16, and the live probe: 384 refused/accepted submissions, then `from_state` equal). Fog: `GET /roles/scope` is not cell-scoped (see M-2). Pending-gate rebuild (IP-1087) and the role check on gate decisions are untouched (`test_gated_order_resume`, `test_white_only_*` green).

## Scope audit

Diff = 15 files, all in `Files to Create`/`Files to Modify` or the implied tests/ledgers (`CLAUDE.md`, `ROADMAP.md`, MBP, packages index, RTM, ICD, `test_browser_console_rules.py`). `api.py` is named in the package. No `docs/pipeline/`, no `docs/training/`, no engine file. In scope.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| **M-1** | **A role-gated order from a bound seat whose `params.verb` is a list or object returns HTTP 500.** `role_scope_check` calls `ROLE_SCOPE_BY_VERB.get(params["verb"])` and an unhashable key raises `TypeError`. Reproduced over real HTTP on both `/order` and `/order/validate` (traceback in the server log); the connection is reset. The parent (and an unseated request today) answers a normal `invalid_param` ack. A bound operator, or a UI bug, can therefore turn a malformed verb into a server error; this breaks the package's own rule that a refusal is a normal rejected `OrderAck` and the baseline's never-500 posture (`NFR-1600`). The session lock is released (the next read succeeds). No test covers it. | Medium | `08-code-implementation` re-run (guard `isinstance(verb, str)`, add a test) |
| **M-2** | **`GET /roles/scope` is a new no-cell endpoint outside the `FR-6220` named set.** `FR-6220` permits "exactly the documented set" of no-cell ground-truth reads and says nothing else bypasses cell filtering; only the staffing report is named for roles. The new read returns, to any caller including Red, `gated_assets` (the ids of every role-gated asset of either cell) and, for any seat name asked, that seat's binding. The package calls it "a no-cell read like `roles/staffing`", but no requirement was amended and no test enumerates the no-cell set. | Medium | `04-requirements-engineering` (extend `FR-6220`'s set, or decide the read is cell-scoped) then `08` |
| **M-3** | **The Feature Specification's execution-time re-check is not built.** `FS-116` System Behaviour: a command outside scope is rejected "at both submission time and ... again at execution time if state could have changed", mirroring the `FR-3410` re-validation. The package scopes the gate to `issue_order`/`validate_order`. Demonstrated: a payload-bound seat queues `isr.collect_now`; White rebinds the seat to `bus` (allowed by `assign_role` at any time); the order still executes (`execute_command` logged). The `FR-3520` acceptance test (direct submission refused) is met; the postcondition wording "rejected at execution time" and the FS text are met only at submission. | Medium | `07-implementation-planning` / owner decision: build the execute-time check, or amend FS-116 to state submission-time only |
| L-1 | Omitting `seat` skips the gate on every role-gated asset (by design, package Owner awareness 1). Confirmed over HTTP: a payload verb with no seat is accepted. Noted for the owner, as requested. | Low (owner decision) | Owner / `04` |
| L-2 | The console "Evade" quick action on the conjunction list posts `prop.collision_avoid` with no operator seat, so it skips the gate from the UI itself. The batch-issue and tasking paths use `composeBody` or are base actions. | Low | `08` |
| L-3 | No test covers the subsystem drill-down verb buttons; the mutation dropping the asset id survives. | Low | `08` |
| L-4 | `roles/assign` accepts any seat string, while `OrderRequest.seat` and `GET /roles/scope` accept only `[A-Za-z0-9_. -]{0,64}`. A seat bound as `é/x` is accepted by White and can never be used (422 on every order). A save with an unknown asset or role loads without a warning (fails closed at the gate). | Low | `08` / `07` |
| L-5 | With browser storage blocked, older console code (brief panel, toggles) throws uncaught `SecurityError`s. Pre-existing, outside this diff. | Low (pre-existing) | `00-intake` |
| I-1 | Manual-impact: the White/Blue/Red manuals describe the order panel and gain an Operator seat field; routed in the package to `08-training-manual-authoring`. | Info | `08-training-manual-authoring` |

## Ledger audit

Master Build Plan tally recounted from the table before this update: 88 `VERIFIED`, 1 `COMPLETE` (`IP-1160`), 0 `READY`, 89 packages, as claimed. After this report: 88 `VERIFIED`, 1 `IN PROGRESS` (`IP-1160`, returned), 0 `COMPLETE`, 0 `READY`, 89. The RTM Test column equals the tool output for `FR-3510`, `FR-3520` and `NFR-2840`.

## Next step

Re-run `08-code-implementation` on `IP-1160` against M-1 (code) and route M-2 and M-3 to the owner and `04`/`07` first, since both may be settled by a requirement or specification wording change rather than code.
