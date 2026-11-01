# VR-1160 — Verification Report: Role-Scoped Command Catalog & Assignment Scoping (FR-3510, FR-3520)

> **Document ID:** VR-1160
> **Version:** 3.0 (supersedes v2.0 and v1.0, which both `RETURNED` the package; their summaries are kept in the appendices)
> **Status:** ✅ Final — result **VERIFIED** (third pass)
> **Dependencies:** [IP-1160](../packages/IP-1160-role-scoped-command-enforcement.md) v1.2
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1160`
> **Feature Mapping:** [FS-116](../../features/FS-116-role-scoped-command-catalog.md), [ADS-3500](../../architecture/ADS-3500-role-scoped-command-enforcement.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1160 v1.2 after its second re-run: fix commit `571535f` (M-4) on top of `2cfc58d` (the v2.0 report), `bdf7e23`, `00dd883`, branch `claude/ip-1160-build`. Verified in a fresh independent session in a separate worktree; the previous commit was checked out in a second private worktree for the before/after comparison. No code, package, spec, requirement or `docs/pipeline/` file was edited; mutations ran in the verification worktree and were restored (`git status` clean).

## Result

**VERIFIED** — 0 failed checks. M-4 is fixed and reproduced-then-gone; the earlier fixes still hold. Carried, none a failed check: M-3 (submission-time role check, owner-decision known deviation), L-1 (omitting `seat` skips the gate, for the owner), L-5, L-6, I-1.

## M-4 re-check

**(a) Reproduction on the parent.** Probe over real HTTP (`TestClient` over `create_app`; `leo-isr-denial` with `roles_needed` covering Blue `ISR-EO-1` and Red `RED-ASAT`; seats `bus-op` (bus) and `pl-op` (payload) on `ISR-EO-1`, `red-op` on `RED-ASAT`). Run at `2cfc58d` (private worktree) and at HEAD with the same script.

**(b) Fog matrix.** 2 cells (Red, Blue) x 4 asset cases (own gated / other cell's gated / other cell's ungated / nonexistent id) x 14 seat values (none, explicit `null`, own bound seat(s), a guessed other-cell seat, unknown, empty, four garbage strings including a 300-char one, `../../x` and an SQL-like string, and non-string `5`, list, dict, `true`) x 2 verbs (one bus, one payload) x `/order` and `/order/validate`.

| Group | `2cfc58d` | `571535f` (HEAD) |
|---|---|---|
| Other cell's gated asset: distinct full-JSON replies across seat values | 8 of 8 groups diverge (`not_owner` vs `role_scope_not_assigned` vs `role_scope_out_of_scope`) | **0 of 8; every reply is `not_owner`, byte-identical (id aside)** |
| Other cell's ungated asset | `not_owner` for every seat | `not_owner` for every seat, byte-identical |
| Nonexistent asset id | `no_such_asset` for every seat | `no_such_asset` for every seat, byte-identical |
| Own gated asset | role codes as designed | role codes as designed (`role_scope_not_assigned` / `role_scope_out_of_scope`) |

Non-200 answers (the garbage and non-string seats: 256 of 480 per run) are 422 from the request model, identically at the parent and HEAD, and carry no cell-dependent text. The own-cell refusals are the two fixed reason codes only; no seat name, role or asset appears in any refusal body. **Existence oracle:** `not_owner` (another cell's asset) against `no_such_asset` (nonexistent) is distinguishable; this is identical at the parent and is the engine's own long-standing behaviour, not introduced or worsened by the fix. The gated and ungated other-cell assets are now indistinguishable (the M-4 disclosure is closed). A note for the owner only: the existence oracle is outside this package.

## Earlier items re-checked

| Item | Evidence | Result |
|---|---|---|
| M-1 non-string verbs | HTTP spot probe at HEAD: list, dict, int, `null`, `true`, empty verbs x both routes x bound seat: 200 and the ack equals the same request without a seat (id aside); suite test `test_m1_*` green | Holds |
| `GET /roles/scope` fog | Seat `s-bus` x console cell: no seat returns only `verbs`; Red `bound` false and only Red's own gated asset listed (no Blue id); Blue and White full; Observer and bogus cell 403; suite `test_m2_*` green | Holds |
| Evade seat | `app.js` still sends `o-seat` on the Evade path; static test green | Holds |
| Drill-down | Browser `test_24` ran (40 browser tests, 0 skipped) | Holds |
| `roles/assign` seat charset | `;` and `../z` are 422, `ok-seat` and a name with a space 200 (same charset as the order route); White-only by query seat | Holds |

## (d) Seat x verb matrix (own cell)

Real HTTP, Blue operating its own `ISR-EO-1`: 8 seat cases (bus, payload, both, bound to a different asset, role `admin`, ghost, omitted, empty) x all 48 verbs x validate and issue = **768 requests, 0 wrong accepts or refusals** against an expectation derived independently from the bindings and the verb sets (not from `role_scope_check`).

## Mutations (each restored; `git status` clean)

| Mutation | Killed by |
|---|---|
| Ownership check removed from the gate (so it runs after the role gate, the engine answering it later) | `test_m4_a_request_for_another_cells_asset_gets_the_no_seat_ack_whatever_seat_is_supplied` |
| A binding leaked in a refusal (`role_scope_not_assigned:<role>`) | `test_07_a_seat_bound_to_a_different_asset_is_not_assigned` (exact reason code compare) |
| Gate skipped for White that supplies a seat | `test_m4_the_owning_cell_still_gets_the_role_refusals_and_white_keeps_its_behaviour` |

## Definition of Done and Verification Checklist

Unchanged from v2.0 except as above; each item was re-run against `571535f`: the 768-request matrix (0 wrong), refusals leave orders, counter and event log untouched (the suite's snapshot helper, test 1-5 and M-4 tests), save/load of `role_assignments` and `validate_save` (suite save tests green), replay equals live (test 16), IP-1087 pending-approval rebuild (`test_gated_order_resume`), the 19 vignettes with and without a seat (test 18, `test_vignette_tutorials.py`), Observer 403 and White-only rules first. `git diff 3368f89 HEAD -- spacesim/engine` is empty (engine unchanged). All pass.

## Requirements audit

| ID | Result |
|---|---|
| FR-3510 | Pass: browser 21-24 and static tests green |
| FR-3520 | Pass for the acceptance criterion and the fog posture on all three entry points; the postcondition's "execution time" wording is the M-3 deviation below |
| NFR-1600, NFR-2300, FR-6220, NFR-2840 | Pass: RTM cells equal the tool output; `--origin-report=rtm` reports "regenerated (unchanged)" and the tree stays clean; the new M-4 tests carry `verifies` markers naming live IDs |

## Test run

| Run | Command (from the worktree) | Result |
|---|---|---|
| Unfiltered | `python3 -m pytest -q -p no:cacheprovider --junitxml=...` | **2050 tests, 0 failed, 0 errors, 3 skipped, exit 0** |
| Not browser | `python3 -m pytest -q -m "not browser" --junitxml=...` | **2010 tests, 0 failed, 4 skipped (the 3 plus the RTM-equality test, which skips on a partial collection by design), exit 0** |
| Browser | `python3 -m pytest -q -m browser --junitxml=... -rs` | **40 tests, 0 failed, 0 skipped, exit 0** |
| Gates and doc checks | `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py`, `test_determinism.py`, `test_import_guard.py`, `test_role_scope_enforcement.py`, `test_vignette_tutorials.py` | exit 0 |
| RTM | `python3 -m pytest --origin-report=rtm` | "regenerated (unchanged)" (pytest exit 5, "no tests ran", by design); tree clean |

2010 + 40 = 2050; the 3 skips are the pre-existing "vignette does not apply" skips. No allow-list changed.

## Known deviation and owner notes

* **M-3 (owner decision, not a failed check).** The role is checked at submission only; a rebinding applies to later submissions. `CLAUDE.md` (Code Map), the ICD (INT-0004/INT-0006), the MBP row and the package completion note state this accurately and give the engineering reason (`role_assignments` is not in the event log, so an execute-time re-check would break replay determinism unless rebinding became a logged event). `FR-3520`'s postcondition and `FS-116` still say "at execution time"; they are listed here as a **known deviation from the baseline text** for the owner to accept (then `04`/`06` amend the wording) or to fund as a logged-rebinding package.
* **L-1.** Omitting `seat` skips the gate (by design, client-asserted seat at LAN trust). For the owner.

## Scope audit

Fix commit `571535f`: `manager.py` (2 lines), `test_role_scope_enforcement.py`, and the ledgers (`CLAUDE.md`, `ROADMAP.md`, MBP, packages index, RTM). In scope. No engine, `docs/pipeline/`, `docs/training/`, requirement or spec file touched.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| M-4 | Closed (reproduced at `2cfc58d`, absent at `571535f`, three mutations killed) | closed | none |
| M-3 | Execute-time re-check not built; documented accurately; `FR-3520`/`FS-116` wording says execution time | Medium (owner decision, not a failed check) | Owner, then `04`/`06` |
| L-1 | Omitting `seat` skips the gate (by design) | Low (owner decision) | Owner / `04` |
| L-5 | With browser storage blocked, older console code throws uncaught `SecurityError`s (pre-existing) | Low | `00-intake` |
| L-6 | Evade seat covered by a static regex test only | Low | `08` |
| L-8 | Existence oracle: `not_owner` vs `no_such_asset` reveals whether another cell's asset id exists (pre-existing engine behaviour, unchanged) | Low | `00-intake` / owner |
| I-1 | Manuals gain an Operator seat field; routed to `08-training-manual-authoring` | Info | `08-training-manual-authoring` |

(v2.0's L-7, the "3 browser cases" nit in `packages/INDEX.md`, is closed: the row now says 4.)

## Ledger audit

Master Build Plan tally recounted from the package table before this update: 88 `VERIFIED`, 1 `COMPLETE` (`IP-1160`), 0 `READY`, 0 `BLOCKED`, 89 packages, as claimed. After this report: **89 `VERIFIED`, 0 `COMPLETE`, 89**. RTM Test column equals the tool output.

## Next step

Run `10-integration-review` for the Tranche 3 / `FEAT-3500` set, then refresh `11-release-readiness`. In parallel the owner should decide M-3 and L-1, and `08-training-manual-authoring` should work off I-1.

## Appendix — v2.0 (superseded)

v2.0 returned the package at `bdf7e23` with one failed check, M-4 (the gate ran before the ownership check, so a Red request naming Blue's role-gated asset learned which assets are gated and which role a guessed seat holds), after confirming that v1.0's M-1, M-2 and Lows L-2/L-3/L-4 were closed (full suite 2047 passed, 3 skipped; browser 40; 768-request matrix 0 mismatches).

## Appendix — v1.0 (superseded)

v1.0 returned the package at implementing commit `00dd883` with M-1 (HTTP 500 on a list or object `verb`), M-2 (`GET /roles/scope` outside the `FR-6220` named set), M-3 (no execute-time re-check) and Lows L-1 to L-5; its 384-combination matrix, mutation list and browser run found no other defect. Findings are carried and re-checked in the sections above.
