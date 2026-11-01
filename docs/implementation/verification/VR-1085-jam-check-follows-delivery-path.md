# VR-1085 — Verification Report: Jam Check Follows the Delivery Path (FR-1440, H-2)

> **Document ID:** VR-1085
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1085](../packages/IP-1085-jam-check-follows-delivery-path.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1085`
> **Feature Mapping:** [FS-129](../../features/FS-129-jamming-delivery-and-effect-detectability.md), [FS-102](../../features/FS-102-command-scheduling.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1085 v1.0, implementing commit `c26f944` on branch `claude/ip-1085-build` (parent `b022b1e`). Verified in a fresh
session in a separate worktree; the implementation was not done in this session.

## Result

**VERIFIED** — 0 failed checks. Two Low observations (below); neither blocks.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Stored program never denied; ground uplink denied by an uplink jam only; relay denied by a crosslink jam on actor or relay only | `_delivery_jammed` (`engine/orders.py`) read in full; the 3 paths x 6 jam conditions x {maneuver, command} matrix (36 cases) passes; re-read `_plan_command`: windows are `stored` / `command_uplink` (path `ground_uplink`) / `isl_link` from relay `rid` to actor (path `isl_relay`, `win.actor` = the relay), so `_delivery_keys` maps all three correctly | pass |
| Existing logs and saves replay byte-identically; new payloads carry the path | Old-log replay below; payload test `test_delivery_path_and_relay_are_in_the_logged_payload` (12 cases) passes | pass |
| Review reproduction is a permanent HTTP test | `test_http_stored_program_maneuver_runs_under_an_uplink_jam` on `01-leo-isr-denial`; fails on the parent, passes here | pass |
| New tests green; RTM Test column regenerated; full suite, determinism, import guard, doc integrity, test origins green; no allow-list grew | See Test run; `--origin-report=rtm` leaves `git status` clean; `git show --stat` touches no allow-list | pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Re-derive H-2 on the parent | Parent (`b022b1e`, detached worktree) with the new test file copied in: 22 tests fail. HTTP: stored maneuver under an in-force uplink jam logs `applied: False` on the parent; `applied: True` and `delivery_path: stored_program` on the fix | pass |
| Re-derive the crosslink gap on the parent | Parent: `isl_relay` x `crosslink_actor` and x `crosslink_relay` (maneuver and command, plus the boundary cases) fail because the command executes; on the fix they fail delivery (`achieved: jammed`, `path: isl_relay:crosslink`) | pass |
| Path table checked against `_plan_command` | Re-read the three branches (above) | pass |
| Payload without new keys behaves as pre-fix; pre-fix log replays equal | Legacy-payload test passes; real old-log replay below | pass |
| `effects.py::is_link_denied` byte-unchanged; planning and `dry_run` do not consult jams | `git diff b022b1e c26f944 --stat` shows no `effects.py`, `session/`, or `ui_web/` change; `grep is_link_denied orders.py`: only `_delivery_jammed` and `_h_downlink`; `test_dry_run_ignores_jams_for_all_three_paths` passes | pass |
| Permanent gates, documentation checks | Test run below | pass |

## Requirements audit

| Req | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-1440 | `_delivery_keys`, `_delivery_jammed`, `_jammed_record`, both handlers | `test_jam_delivery_paths.py` (all tests marked) | Test column lists the new module's tests; `--origin-report=rtm` reports no change (equals tool output) | pass |
| FR-3110 | planning unchanged | `test_dry_run_ignores_jams_for_all_three_paths` | gained the test | pass |
| FR-3410 | denial still decided at execute-time re-validation (handlers) | matrix | covered via FR-1440 cell | pass |
| ADR-0002 | path read from the logged payload; no clock/RNG | determinism, replay-equals-live (6 cases), old-log replay | n/a | pass |

All `verifies` markers name live baseline IDs (the origin suite is green).

## Independent probes

- **Parent vs fix.** Scratch parent worktree under a private subdirectory; the builder's test module copied in: parent fails 22 of the 63 new tests (the defect, the missing crosslink check, and the missing `path`/`delivery_path` keys); fix passes all 63.
- **Direct uplink under uplink jam** still denied (matrix); **jam outside footprint** and **jam on a different link** (downlink on actor; uplink on an unrelated asset) never deny; cyber/engage/jam/observe/downlink actions are not touched by the diff (only `_exec_payload`'s two maneuver/command branches and the two handlers).
- **Old-log replay.** Using the real HTTP API on a detached copy of the parent, I recorded saves (jam orders against several satellites on uplink and crosslink, maneuver and command orders via a station, 12 h of stepping) for `leo-isr-denial`, `geo-rpo-shadowing`, `gnss-ew-campaign`, `satcom-cyber-link`, `nv-isl-relay-debris`, `mt-isr-sar`, `co-orbital-threat-escort`, plus a dedicated jam case (an in-force uplink jam, then stored-program maneuver, ground-uplink maneuver, stored command). Loaded on the fix via `load_save`: the event log is identical for all 8 and the god-view is identical except `now` (the live lazy clock, which differs the same way when the save is loaded on the parent itself). The dedicated case shows the parent log with the stored maneuver `applied: False` (defect) and the same save reloaded on the fix reproduces the recorded history unchanged (replay is recorded-history exact, as designed).
- **Fix-recorded logs.** The same cases recorded on the fix (payloads carry `delivery_path`; stored maneuver `applied: True`, ground-uplink maneuver `applied: False`) reload on the fix with an identical event log and god-view (modulo `now`).
- **Deviation judged: `effect_log` failure record `path` key written only when the payload carries `delivery_path`.** The package text (Interfaces) says the record "gains an additive `path` key". Writing it unconditionally would change the `effect_log` of a replayed pre-fix jammed command, so `world.model_dump_json()` of a replayed old log would differ from the one recorded — contradicting Design Decision 3 and the Definition of Done ("existing logs replay byte-identically"). The deviation is therefore required by the package's own stronger requirement, is complete (every new-payload failure carries `path`, every legacy failure does not), and is pinned both ways: `test_a_payload_without_the_new_keys...` asserts no `path` on the legacy record; the matrix asserts `path` on new ones. A mutation that always writes `path` is caught (below). Accepted.
- **Vignette/playbook grep** for `stored_at` and `link_target`: no shipped vignette or training document uses either, matching the package Risk.

## Mutations (scratch worktree at the fix commit; real tree untouched)

| Mutation | Result |
|---|---|
| Always apply the old rule (path forced to `ground_uplink`) | fails (matrix) |
| Ignore stored (stored program denied by an uplink jam) | fails |
| Ignore relay (crosslink checked on actor only) | fails |
| Ignore crosslink (relay path never denied) | fails |
| Drop `delivery_path`/`relay` from the command payload | fails |
| Drop them from the maneuver payload | fails |
| Break the legacy-payload fallback (missing key treated as `stored_program`) | fails |
| Write the `path` key unconditionally | fails |

Each run stopped at the first failure (`pytest -x`) in `test_jam_delivery_paths.py` + `test_orders.py`.

## Test run

All from the worktree, real exit codes, `--junitxml`.

| Command | Result |
|---|---|
| `python3 -m pytest -q --junitxml=full.xml` (unfiltered) | exit 0; 1874 tests, 0 failures, 0 errors, 3 skipped |
| `python3 -m pytest -q -m "not browser"` | exit 0; 1841 tests, 0 failures, 4 skipped (the 3 above plus the partial-collection RTM-equality test, which the unfiltered run executes) |
| `python3 -m pytest -q -m browser` | exit 0; 33 tests, 0 skipped |
| `test_determinism.py test_import_guard.py test_doc_integrity.py test_test_origins.py test_origin_retag.py` | exit 0 |
| `python3 -m pytest --origin-report=rtm` | no change; `git status` clean |

## Scope audit

Changed by `c26f944`: `spacesim/engine/orders.py`, new `spacesim/tests/test_jam_delivery_paths.py`, `CLAUDE.md`, `ROADMAP.md`, the MBP, `packages/INDEX.md`, the RTM. All inside the package's file set and Documentation Updates; `test_orders.py` was (correctly) left unmodified. `effects.py`, `session/`, `ui_web/`, `docs/pipeline/`, `docs/training/` untouched.

## Ledger audit

Tally recounted from the MBP package-table status column before this update: 84 `VERIFIED`, 1 `COMPLETE` (`IP-1085`), 4 `READY`, 89 packages, matching the 08 note. After this update: 85 `VERIFIED`, 4 `READY`, 89. The RTM Test column equals the tool output. The `CLAUDE.md` `orders.py` sentence matches the code.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | Package test list items not fully realised: the HTTP regression omits the "same order with `via` a station fails as before" half (item 7), and the legacy-payload test does not itself replay a recorded log containing the legacy event (item 5, second half). Both behaviours are covered elsewhere (the matrix pins ground uplink failing; this report's old-log replay and `test_replay_equals_live...` cover replay), so no behaviour is unpinned. | Low | none required; optional `08` top-up |
| F2 | Training-manual impact (Blue/Red text on the stored-program path versus the uplink jam; `15-manual-traceability.md` §15.1 `FR-1440` row) is routed by the package (Design Decision 7) but no `15` row mentions `IP-1085` yet. Not edited here. | Low | `08-training-manual-authoring` (file via `00-intake`/pipeline manager) |

## Independence

Fresh session; the builder's tests were run, but every behavioural claim above was re-derived with separate probes, a parent worktree and mutations.
