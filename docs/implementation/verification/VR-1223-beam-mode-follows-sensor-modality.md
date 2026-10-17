# VR-1223 — Verification Report: Beam-Mode Choice Follows the Sensor's Modality (FS-122 v1.2, FR-1610, NFR-1600)

> **Document ID:** VR-1223
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1223](../packages/IP-1223-beam-mode-follows-sensor-modality.md),
> [FS-122](../../features/FS-122-sensor-modality-models.md) v1.2,
> [IP-1222](../packages/IP-1222-sensor-modality-wiring-remediation.md) /
> [IP-1041](../packages/IP-1041-observe-order-reason-and-param-remediation.md) (both `VERIFIED`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0265`
> (from `BL-0224`)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1223`
> **Feature Mapping:** FS-122 v1.2 (`FR-1610`, `NFR-1600`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js),
> [`spacesim/ui_web/static/index.html`](../../../spacesim/ui_web/static/index.html);
> [VR-1222](VR-1222-sensor-modality-wiring-remediation.md) (the IP-1222 behaviour this package
> deliberately reverses in part — its Design Decision 2 SAR-table fallback)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1223 — Beam-mode choice follows the executing sensor's modality.
- **Version verified:** 1.0
- **Tree state verified:** commit `446950a` (branch `claude/chart-prompt-file-90hm9u`, local
  tracking branch `verify-batch`). Implementing commit: `bba6330` (2026-10-17, pipeline run
  #168). Of the later commits on the branch, only `2519c50` (`IP-1065`) touches any of this
  package's files (`app.js`), and its diff contains no beam-mode code (`grep -ci beam` on that
  diff → 0); `engine/orders.py` and `test_beam_mode_modality.py` are untouched since `bba6330`.
- **Independence:** first verification pass. Fresh session with no involvement in `bba6330` or
  any prior `IP-1223` work.

## Result

**VERIFIED, with one Low traceability note (corrected by this report, not a code finding).**

The central scrutiny point — the two pre-existing tests the implementer changed from a SAR mode
name to `dish` — was checked by running the **original, unmodified** versions of both tests
(extracted from `bba6330^`) against both trees:

| Test (original text) | Pre-fix tree | Post-fix tree | Failure reason post-fix |
|---|---|---|---|
| `test_isr.py::test_observe_ground_sensor_no_footprint` (radar tasked `beam_mode: "wide_area"`) | pass | **fail** | `assert 'rejected' == 'queued'` — refused `invalid_param` |
| `test_observe_order_remediation.py::test_well_formed_orders_unchanged` (radar fixture, `beam_mode: "stripmap"`) | pass | **fail** | `AssertionError: invalid_param` (from `_payload_for`'s queued assertion) |

Both originals fail post-fix **only** because they task a `ground_radar` with an imaging-SAR mode
name — exactly what FS-122 v1.2's System Behaviour and Acceptance Criterion now require to be
refused. They encoded the `IP-1222` Design Decision 2 fallback this spec version reverses; the
edit is a necessary fixture correction, not a weakening. The updated (`dish`) versions pass on
**both** the pre-fix and post-fix trees, which shows the edit does not depend on the new code to
pass — it moves the input onto the legal side of the new rule and leaves each test's actual
subject alone:

- **`test_observe_ground_sensor_no_footprint`'s subject is the footprint branch**, which in
  `_exec_payload` (`orders.py`, "Compute footprint polygon…") is gated *only* on
  `actor_orbit is not None`; the beam-mode table selects `bp`, which feeds `footprint_polygon`
  only inside that branch. A ground radar has no orbit, so the footprint stays `None` whichever
  table the mode resolves on. The `dish` version goes through the same issue → window search →
  `execute_observe` → Track creation → `last_footprint is None` path as the `wide_area` original;
  the only difference is which table `bp` comes from, and that value is never read on this path.
- **`test_well_formed_orders_unchanged`'s subject is the `IP-1041` normaliser**
  (`_observe_params_ok`): a well-formed string `beam_mode` plus a numeric `gain` passes through and
  the order queues with a deterministic payload. `dish` is a string `beam_mode` exactly like
  `stripmap`; the normaliser's string check is the same, and the queued-and-equal assertion is the
  same. The remaining three-way `beam_params` fallback loop in that test is untouched. (Observation,
  not a finding: the line compares `_payload_for(X) == _payload_for(X)` with identical arguments
  both before and after the edit — it is a determinism/queues check rather than a true
  "unchanged" comparison. This was already so before `IP-1223` and is not something this package
  introduced or weakened.)

The new behaviour was independently reproduced on a **fresh fixture distinct from the
implementer's** (shipped vignette `sda-custody-hunt`, seed `31337`, through the real HTTP routes
`/order/validate` and `/order` over a `create_app(InProcessSession())`), going further than the
implementer's probe on the same vignette: five foreign names (`spotlight`, `wide_area`, `stripmap`,
`polarimetric`, and case-mismatched `Dish`) are all refused `invalid_param` at preview with the
scheduler unchanged; `dish`/`fence`/absent are accepted; issued `dish`/`fence` orders produce
`execute_observe` events at gains **1.6** / **0.5**, matching `effective_gain(…, beam_params(
"ground_radar", …))` recomputed independently (the pre-fix SAR-table score for `spotlight` would
have been 1.8); an `auto` + `dish` order queues; `auto` + a mode no own blue sensor offers
(`full_disk`, and `nominal`, see note below) is refused `invalid_param`.

The "8 of 9 failed first" claim was re-derived on a genuine pre-fix scratch tree (whole tree
copied, exactly `orders.py`, `app.js` and `index.html` reverted to `bba6330^`, the scratch package
confirmed first on `sys.path`): **8 failed, 1 passed** — the one pass being
`test_radar_own_modes_and_absent_mode_unchanged`, the backward-compatibility test that by
design must pass on both trees. Test 1, 3 and 4 (the DoD's named "failed first" set) are all in
the 8.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Tests 1, 3, 4 failed first; all pass. Full suite + both gates green. | Pre-fix scratch tree: 8 of 9 tests in `test_beam_mode_modality.py` fail (both `test_radar_refuses_a_sar_mode` params = test 1; both `test_optical_sensor_refuses_a_radar_mode` = test 3; `test_auto_picks…` + both `test_auto_refuses…` = test 4; `test_console_builds…` = test 5); only the backward-compat test 2 passes, as it should. Post-fix: 9/9 pass. Full suite and gates: see Test run. | ✅ Pass |
| Ledgers, RTM updated; manual impact filed. | MBP row, `packages/INDEX.md`, `ROADMAP.md` all read `COMPLETE` before this report. RTM `FR-1610` row cites `test_beam_mode_modality.py` and `IP-1223` against the real helpers. Manual impact filed as `BL-0271` (`10a` §10.5 row 8, `06` beam-mode row, `BLU-4`/`RED-4`, `09` §10, §15.1 rows). **Low note:** FS-122's `Referenced By` entry for `IP-1223` (a Documentation Update the package names) still read *"planned 2026-10-17, run #166"* — not advanced at implementation. Corrected by this report's own traceability actions (straight to `VERIFIED`); does not affect any code or test claim. | ✅ Pass (with Low note) |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Probe a shipped vignette with a ground radar (`sda-custody-hunt`): `spotlight` refused, `dish` queued at 1.6. | Independent HTTP-level probe (seed 31337, `BLUE-RADAR-1` vs `RED-OBJ`): `spotlight` → `ok: False, reason: invalid_param` at both `/order/validate` and `/order`; `dish` → queued, `execute_observe` payload `beam_mode: "dish"`, `gain: 1.6`; `fence` → queued, gain `0.5`. Four more foreign names (incl. `Dish`, case mismatch) also refused; scheduler heap length identical before and after all validate calls. | ✅ Pass |
| Read the helper and confirm validation and execution call it. | `OrderSystem._observe_payload_type` / `_observe_modes` (`orders.py`, after `_candidate_sensors`). Callers, read directly: `_validate` observe branch (explicit actor: `mode not in self._observe_modes(sid)` → `invalid_param`, placed before the cue check and before any window search; `auto`: `any(mode in self._observe_modes(sid) …)` over own sensors), `_candidate_sensors` (filter), and `_exec_payload`'s observe branch (`payload_type = self._observe_payload_type(order.actor)`, replacing the inline three-way derivation byte-for-byte in logic). Validation resolves the actor via `_resolve_sensor_id` and execution reads `order.actor`, which `_plan_collection` sets to that same resolved `sid` before `_exec_payload` runs (`order.actor = sid`, "read by _exec_payload, so assigned before it") — so a hosted-sensor alias cannot make the two disagree. Since `_validate` is shared by `dry_run` and `issue`, preview and issue refuse alike (confirmed by the `method`-parametrized tests and the HTTP probe). | ✅ Pass |
| Full suite and both gates by name. | See Test run. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-1610` (fence/dish radar beam modes; no silent foreign substitution) | `engine/orders.py` `_requested_beam_mode`, `_observe_modes`, `_observe_payload_type`; `_validate`; `_candidate_sensors`; `app.js` `BEAM_MODES_BY_TYPE`/`beamModesForSensor`/`populateBeamModes`; `index.html` `#task-beam-mode` now dynamic | `test_beam_mode_modality.py` (9); the two corrected tests; independent HTTP probe above | `03-requirements-traceability-matrix.md` `FR-1610` row lists `test_beam_mode_modality.py` and `IP-1223` against the real helper names — accurate; status advanced to `VERIFIED` by this report | ✅ Pass |
| `NFR-1600` (illegal parameter blocked with a reason, not mis-scored) | Same `_validate` branch — `invalid_param`, nothing scheduled | `test_radar_refuses_a_sar_mode`, `test_optical_sensor_refuses_a_radar_mode`, `test_auto_refuses_a_mode_no_own_sensor_offers` (each asserts no `execute_observe` scheduled); HTTP probe (scheduler unchanged) | `NFR-1600` RTM row is a catch-all (`engine/orders.py`, `content/vignette.py`) citing `test_validate_order.py`; the package's own Documentation Updates names only the `FR-1610` Test cell, so no `NFR-1600` cell change was owed. Content confirmed correct | ✅ Pass |

**Console mirror.** `app.js`'s `BEAM_MODES_BY_TYPE` was compared key-for-key and order-for-order
against `engine/isr.py::BEAM_MODES` (all six tables: `isr_eo`, `isr_sar`, `sda`, `weather`, `mw`,
`ground_radar`) — identical. `beamModesForSensor` follows the server helper's own precedence
(ground radar → payload type → `needs_lighting` heuristic → EO). `/view/{cell}`'s `own_sensors`
entries really carry `kind` and `needs_lighting` (confirmed in the probe), so the client has
the inputs the mirror needs. `populateBeamModes` runs on every refresh and on `#task-sensor`
change, and for `auto` builds the union over the picker's sensors (Design Decision 4). The server
stays authoritative: a stale client list can only produce an `invalid_param` refusal, never a
foreign-table score. Browser rendering was not driven (the project's standing headless-GUI caveat).

**Risk check (package Risks §1).** `grep -rn beam_mode spacesim/content/vignettes/
docs/training/11-vignette-playbooks.md` → no hits: no shipped vignette or playbook names a beam
mode, so none can be newly refused. `test_vignette_tutorials.py` passes in the full suite.

## Test run

Exact commands run in this session (tree at `446950a`):

```
python3 -m pytest -p no:warnings                                   # full suite
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
# pre-fix scratch tree (orders.py/app.js/index.html at bba6330^), cwd = scratch copy:
python3 -m pytest -p no:warnings -p no:cacheprovider -q spacesim/tests/test_beam_mode_modality.py
# original (bba6330^) versions of the two edited tests, run against both trees
```

- **Full suite:** **1016 passed, 3 skipped** (the implementer recorded 1001/3 at `bba6330`; the +15
  come from `IP-1065`/`IP-1064`/`IP-1131`/`IP-1021`, landed later — no regression).
- **Permanent gates, run by name:** **14 passed** (`test_determinism.py` + `test_import_guard.py`).
- **This package's tests:** 9/9 pass post-fix; 8/9 fail on the pre-fix scratch tree.
- **Original edited tests:** pass pre-fix, fail post-fix with `invalid_param` (table above);
  corrected versions pass on both trees.

## Scope audit

`git show bba6330 --stat` (10 files): `spacesim/engine/orders.py`, `spacesim/ui_web/static/app.js`,
`spacesim/ui_web/static/index.html` (the declared Files to Modify); `spacesim/tests/test_beam_mode_modality.py`
(new — the package's own named option); `spacesim/tests/test_isr.py` and
`spacesim/tests/test_observe_order_remediation.py` (one line each, the disclosed fixture corrections,
justified above); `ROADMAP.md`, MBP, `packages/INDEX.md`, RTM (ledgers). `engine/isr.py` is read
only, as declared. No excursion.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | FS-122 `Referenced By` entry for `IP-1223` not advanced past "planned" by the implementing run (a Documentation Update the package names). | Low | Corrected by this report (traceability-only, in this skill's ledger remit); no re-run needed |

Informational, not findings: (a) the self-comparison line in `test_well_formed_orders_unchanged`
existed before this package (above); (b) on `sda-custody-hunt` a `space_based` sensor without a
`payload_state` (`BLUE-SSN-SBO-1`) is scored on the EO table by the `needs_lighting` heuristic, so
SDA-table names (`nominal`) are not offered to it. That is `IP-1222`'s heuristic, which `IP-1223`
Design Decision 1 deliberately keeps ("otherwise the existing lighting heuristic"), not new
behaviour — refusing `nominal` there is consistent with the declared rule.

## Traceability actions taken by this report

- MBP row, `packages/INDEX.md` row, `ROADMAP.md` row: `COMPLETE → VERIFIED`; MBP Package Status
  line added.
- `FS-122` `Referenced By` entry for `IP-1223`: "planned" → `VERIFIED` (`VR-1223`) (Finding 1).
- RTM `FR-1610` row: `IP-1223 (COMPLETE …, awaiting 09)` → `VERIFIED 2026-10-17 via VR-1223`.
- `BL-0265` → `DONE`. `BL-0224` already `DONE` (decided run #163) — left unchanged.
- `BL-0270`: `IP-1223` recorded as verified; still owed `IP-1065`/`IP-1064`/`IP-1131`.
- `BL-0271` (manual impact of this package): left as found (`SCHEDULED` for the next
  `08-training-manual-authoring` run). The as-built behaviour it describes (`auto`/`fence`/`dish`
  for a radar; foreign mode refused `invalid_param`; raw-JSON workaround obsolete) is confirmed
  accurate by this report, so that run can proceed on it unchanged.
- `BL-0272`/`BL-0273` and the parked `NEEDS-USER`/`REJECTED` entries: untouched.
