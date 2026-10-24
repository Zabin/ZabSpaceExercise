# VR-1331 — Verification Report: Test-Origin Backfill, Engine and Content Modules (NFR-2820)

> **Document ID:** VR-1331
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1331](../packages/IP-1331-test-origin-backfill-engine-content.md) v1.0,
> [FS-133](../../features/FS-133-test-origin-traceability.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1331`
> **Feature Mapping:** FS-133 (`FEAT-12100`)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1331 — Test-Origin Backfill: Engine and Content Test Modules (v1.0)
- **Implementing commit:** `4641d1a` ("test: IP-1331 — tag 22 engine and content test modules ..."), compared with its parent `4641d1a~1`. Tree verified at `15e24a0` (branch `claude/ip-1333-backfill-web`, which also holds IP-1332/IP-1333 work; the 22 modules are not touched by later commits).
- **Independence:** fresh session; did not implement this package or any sibling.

## Result

**✅ VERIFIED** — 0 failed checks. Tag judgements (every test of the 22 modules, 180 test functions / 208 collected items): **165 agree, 15 weak, 0 wrong**. 0 tags name a nonexistent ID. Findings are for `08`/`04`/`07`; none blocks the transition.

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Every collected test in the listed modules has a resolvable origin | `--origin-report`: "untagged tests: 0"; `test_every_collected_test_outside_the_allowlist_declares_an_origin` and `test_every_declared_id_in_the_real_suite_resolves` pass; all 45 distinct IDs used were looked up in the requirements files (FR/NFR leaves exist; `IP-2010` and `FS-201` are live package/feature IDs) | Pass |
| 2 | Modules off the allow-list; origin checks pass | Allow-list diff: 22 lines removed (70 → 48); `grep` of the 22 module names in the list at HEAD: 0 hits; `test_test_origins.py` green | Pass |
| 3 | No assertion, fixture or test body changed | Script 1 (line level, `git diff -U0` per module): 0 removed lines; every added line is a `@pytest.mark.verifies(...)` (incl. wrapped continuation lines), a `pytestmark =` line, `import pytest` or blank. Script 2 (AST): for all 22 modules the AST with `verifies` decorators, `pytestmark` and `import pytest` stripped is identical before and after | Pass |
| 4 | Untraceable tests listed for `04` | The IP-1331 completion note (journal run #248) does not list the four `IP-2010` tests as untraceable in the package; see finding F-1: the claim does not hold | Pass with finding |
| 5 | Full suite and both gates green | See Test run | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| `git diff` of the listed modules contains only marker additions (and `import pytest`) | See DoD 3; two independent scripts | Pass |
| Sample per module, marker describes what the test asserts (FS-133 criterion 7) | Assertions of **all 180 test functions** extracted and read, not only a sample; leaf text read for each distinct ID; judgements below | Pass (165 agree / 15 weak / 0 wrong) |
| Allow-list no longer names these modules | `test_origin_allowlist.txt`: 0 matches for the 22 names | Pass |
| Full-suite counts unchanged; gates green by name | 1284 collected, 3 skipped, 0 failed; see Test run | Pass |
| `--origin-report=rtm` changes nothing | Output "regenerated (unchanged)"; `git status` clean afterwards | Pass |

### Tag judgements per module

Counts are test functions. "Weak" means the leaf is related but does not describe what the test asserts; a better ID is suggested.

| Module (tests) | Agree | Weak | Notes |
|---|---|---|---|
| test_version (1, all read) | 1 | 0 | `FR-5510` records the simulator version; test asserts the version string is non-empty and never raises. |
| test_clock_and_time (3, all) | 2 | 1 | `FR-1130` ordering/sub-step tests agree. `test_simtime_iso_round_trip_is_exact` -> `FR-1110` is weak: it asserts time-unit conversion, not a single authoritative clock. No better leaf exists. |
| test_custody (3, all) | 3 | 0 | `FR-1510` decay/reset/uncertainty, `FR-1520` weapons-quality gate: agree. |
| test_propagator (3, all) | 3 | 0 | `FR-1210` look angle at zenith and ground-track altitude; `FR-1310` prograde impulse raises orbit. The zenith test is at the edge of `FR-1210` but acceptable. |
| test_recovery (3, all) | 3 | 0 | `FR-2510` multi-pass recovery: agree. |
| test_reference_skyfield (2, all) | 2 | 0 | `NFR-2810` (reference validation) + `FR-1210`; TLE access passes `FR-1220`: agree. |
| test_safe_mode (4, all) | 4 | 0 | `FR-2510`/`FR-1420` cyber-induced safe mode; `FR-2310` discovered only at next contact; `FR-1120` replay: agree. |
| test_access (12) | 11 | 1 | `FR-1220` channel/regime tests agree; `FR-1620/1630/1660`, `NFR-2010` agree. `test_window_cache_and_invalidate` -> `FR-1220` weak: asserts cache identity, which the leaf does not state. |
| test_bus (6) | 5 | 1 | `FR-2110` limit colouring, eclipse drain, recharge agree; `FR-2210` payload gating agrees. `test_ops_fidelity_collapses_or_expands_the_bus_view` -> `FR-2110` weak: no leaf describes the ops-fidelity view levels. |
| test_cats_angle (7) | 6 | 1 | Four geometry cases, coincident rejection, `FR-1670` reuse: agree. `test_phase_angle_is_defined_only_once_in_engine` is a source scan for a single definition (`BL-0152`), tagged `FR-8220`: weak; the nearest ID is the feature/package that set the design decision (`FS-122` / `IP-1300`). |
| test_config (10) | 6 | 4 | The five `ServerConfig` tests and the shared-file test agree with `NFR-2700`. The four `content_*` tests (`test_content_defaults_when_no_file`, `..._yaml_overrides`, `..._partial_override_keeps_other_defaults`, `..._env_var_overrides_default_path`) are tagged `FR-5410`+`FR-5420`: weak; they assert config parsing only. `NFR-2700` was amended to include the `content:` section and fits better. |
| test_defensive_modifiers (10) | 10 | 0 | Probability modifiers tagged `FR-1410`/`FR-1420`, `def.harden` `FR-2510`: agree, though no leaf names defender posture modifiers specifically (observation O-1). |
| test_effects (9) | 9 | 0 | `FR-1410`, `FR-1420`, `FR-1430`, `FR-1450`: agree. |
| test_orbit (6) | 4 | 2 | `FR-1210` four tests agree. `test_mean_to_true_round_trips_with_true_to_mean` and `test_mean_to_true_extraction_did_not_change_elements_to_rv` -> `FR-5220`: weak; they test orbit-element maths (a refactor regression). `FR-1210` fits the assertions; `FR-5220` is the consumer. |
| test_orders (26) | 22 | 4 | Gating `FR-3430`, ROE `FR-3420/3440`, jam/uplink `FR-1440`, cue `FR-1640`, maneuver `FR-1310/1320`, `FR-1120` replay, `FR-1520` gate: agree. The four `IP-2010` tests: weak, see F-1. |
| test_bulk_import (7) | 7 | 0 | `FR-5220` parse/reject behaviour: agree. |
| test_content (19) | 18 | 1 | External dirs `FR-5410`, traversal `NFR-3700`, ROE `FR-3420`, caps `NFR-1300`, additive `NFR-2010`, `FR-5510` agree. `test_vignette_1_loads_and_builds_a_world` -> `FR-4110`: weak; it asserts vignette content and build, not parameter selection; the load-time gate leaf `FR-5310` fits better. |
| test_phase_angle_gain (14) | 14 | 0 | `FR-1670` (+`FR-1660`, `NFR-2010`): agree. |
| test_sensor_modality_wiring (9) | 9 | 0 | `FR-1610`, `FR-1630`, `FR-1640`, `NFR-2010`: agree. |
| test_tle_export (8) | 8 | 0 | `FR-7440`: agree. |
| test_typed_payload_params (12) | 12 | 0 | `FR-5170`/`FR-5180`/`NFR-2010`: agree. |
| test_vignette_export (6) | 6 | 0 | `FR-5420`, `NFR-3700`, `FR-5510`: agree. |
| **Total (180)** | **165** | **15** | **0 wrong** |

Weak tags, with suggested better IDs:

| Test | Current | Suggested |
|---|---|---|
| test_clock_and_time::test_simtime_iso_round_trip_is_exact | FR-1110 | keep, or a sim-time-representation leaf if `04` adds one |
| test_access::test_window_cache_and_invalidate | FR-1220 | no leaf; `FS-` of the access provider or a new performance leaf from `04` |
| test_bus::test_ops_fidelity_collapses_or_expands_the_bus_view | FR-2110 | no leaf; candidate for `04` |
| test_cats_angle::test_phase_angle_is_defined_only_once_in_engine | FR-8220 | FS-122 or IP-1300 |
| test_config::test_content_defaults_when_no_file, test_content_yaml_overrides, test_content_partial_override_keeps_other_defaults, test_content_env_var_overrides_default_path | FR-5410, FR-5420 | NFR-2700 |
| test_orbit::test_mean_to_true_round_trips_with_true_to_mean, test_mean_to_true_extraction_did_not_change_elements_to_rv | FR-5220 | FR-1210 (FR-5220 optional second ID) |
| test_content::test_vignette_1_loads_and_builds_a_world | FR-4110 | FR-5310 |
| test_orders::test_custody_confidence_at_decision_captured_for_targeted_actions, ..._none_without_target_or_track | IP-2010 | FR-10110 (or FS-201) |
| test_orders::test_dry_run_never_captures_custody_confidence | IP-2010 | FS-201 (no fitting leaf found for the dry-run no-footprint property) |
| test_orders::test_custody_confidence_at_decision_replays_byte_identically | IP-2010 | FR-1120 |

### The `IP-2010` claim

The claim that the custody-confidence tests (the brief says five; `test_orders.py` holds four, tagged `IP-2010`) are untraceable to any leaf **does not hold**. `FR-10110` (competency rubric computation) lists as its Inputs "`Track` confidence history at time of action vs. decision (custody quality)", which is what `custody_confidence_at_decision` records; the sibling `test_assessment.py` tests use `FS-201`, the feature spec that owns the same data. The replay test is exactly `FR-1120` ("replay reproduces identical state"), which the neighbouring `test_engage_sequence_replays_byte_identical` already uses. Only the dry-run zero-footprint test lacks a leaf, and `FS-201` fits it. `IP-2010` resolves, so the gate passes, but FS-133 Decision 2 prefers a leaf and allows an `IP-xxxx` only where none exists.

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| NFR-2820 | the `verifies` markers in 22 modules; `test_origin_allowlist.txt` shrunk | `test_test_origins.py` (checks from IP-1330) over these modules; `--origin-report` shows 0 untagged | Test column regenerated by the tool in the implementing commit; `--origin-report=rtm` run now: unchanged | Pass |
| NFR-3840 (IDs added) | all added IDs resolve against the live baseline | `test_every_declared_id_in_the_real_suite_resolves` | as above | Pass |

## Test run

- `python3 -m pytest --tb=short --junitxml=…`: exit 0; junit 1284 tests, 0 failures, 0 errors, 3 skipped (1281 passed, 3 skipped, 178 s). Counts unchanged from before the package (1284 collected, 3 skipped).
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -q`: all passed.
- `python3 -m pytest --origin-report=rtm`: "traceability matrix Test column regenerated (unchanged)"; working tree clean afterwards.
- `python3 -m pytest --origin-report`: "untagged tests: 0".
- `python3 -m pytest spacesim/tests/test_doc_integrity.py` after the ledger edits of this run: green.

## Scope audit

The implementing commit touched the 22 modules, the allow-list, the RTM (generated Test column), and the status ledgers (`ROADMAP.md`, master build plan, packages index, pipeline journal). All within the package's declared file set plus the ledger updates `08` owns. No production code touched.

## Findings

| ID | Finding | Severity | Owner |
|---|---|---|---|
| F-1 | Four `IP-2010` tags in `test_orders.py` have fitting leaves: `FR-10110` (or `FS-201`) for three, `FR-1120` for the replay test. The "untraceable" claim is false. | Low | `08` (retag) |
| F-2 | Eleven further weak tags (table above): four `content_*` config tests -> `NFR-2700`; two `mean_to_true` tests -> `FR-1210`; `test_vignette_1_loads` -> `FR-5310`; plus the clock ISO, window-cache, ops-fidelity and single-definition tests, for which no better leaf exists. | Low | `08` for the retags; `04` for the no-leaf cases |
| F-3 | Gap candidates for `04`: no leaf for access-window caching, the bus ops-fidelity view levels, or defender posture modifiers (frequency hop, evasion, interference mitigation) as distinct behaviour; these tests carry the nearest leaf. | Low | `04` |
| F-4 | `IP-1331` package file header still reads "Status: BLOCKED / Authorization: not yet given" although the master plan records it authorized and complete. Package files are not edited by `09`. | Low | `07` |
| F-5 | The master-plan row says "186 tests"; the 22 modules hold 180 test functions, 208 collected items. Cosmetic. | Low | `08` |
