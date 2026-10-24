# IP-1334 — Test-Origin Retag: Replace Weak Tags With the Leaf the Test Verifies (NFR-2820, test-only)

> **Package ID:** IP-1334
> **Version:** 1.0
> **Status:** COMPLETE — implemented 2026-10-24 by `08-code-implementation` (awaiting `09`); authored 2026-10-24 by
> `07-implementation-planning` (release-push remediation pass).
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24,
> recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, authorizes
> remediation packages for bugs, in-progress and critical items. This test-only package closes the
> weak-tag findings left by the three backfill verifications (`BL-0341`, `BL-0344`, `BL-0347`).
> Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [FS-133](../../features/FS-133-test-origin-traceability.md) (the spec);
> [IP-1330](IP-1330-test-origin-marker-and-checks.md), [IP-1331](IP-1331-test-origin-backfill-engine-content.md),
> [IP-1332](IP-1332-test-origin-backfill-session.md), [IP-1333](IP-1333-test-origin-backfill-web.md)
> (all `VERIFIED`).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0341`, `BL-0344`,
> `BL-0347`
> **Produces:** the concrete retags the three verification reports found, a guard test that pins
> them, and a regenerated RTM Test column. No behaviour changes.
> **Feature Reference:** [FS-133](../../features/FS-133-test-origin-traceability.md) (`FEAT-12100`;
> `NFR-2820`, `NFR-2830`, `NFR-2850`)
> **Related Topics:** [VR-1331](../verification/VR-1331-test-origin-backfill-engine-content.md) F-1,
> F-2; [VR-1332](../verification/VR-1332-test-origin-backfill-session.md) F-1, F-2;
> [VR-1333](../verification/VR-1333-test-origin-backfill-web.md) F-1

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (test-only). Low risk: it edits `@pytest.mark.verifies(...)` arguments and one
new test module. No production file changes.*

---

## Package ID

IP-1334 (FS-133 → `IP-133x`; `IP-1330`–`IP-1333` are taken).

## Title

Test-origin retag: weak tags to the fitting leaf.

## Objective

The backfill (`IP-1331`, `IP-1332`, `IP-1333`) gave every test an origin. The independent
verifications found 0 wrong tags and a minority of weak ones: a test carrying a feature (`FS-201`,
`FS-301`) or a neighbouring leaf where a fitting leaf exists. FS-133's Decision 2 prefers the leaf.
The reports (tallies over all test functions: 165 of 180 agree, 328 of 447, 231 of 273) list the
retags that have a fitting leaf:

| Source | Retags with a fitting leaf |
|---|---|
| `BL-0341` / VR-1331 F-1 | `test_orders.py`: the `IP-2010` confidence-at-decision tests (two) → `FR-10110`; the replay-identical test → `FR-1120`. The dry-run zero-footprint test keeps `FS-201` (no better leaf). |
| `BL-0341` / VR-1331 F-2 | `test_config.py` four `content_*` tests → `NFR-2700`; `test_orbit.py` two `mean_to_true` tests → `FR-1210`; `test_content.py::test_vignette_1_loads_and_builds_a_world` → `FR-5310`. |
| `BL-0344` / VR-1332 F-1 | `test_assessment.py` (13 tests) `FS-201` → `FR-10110`; `test_research_batch.py` (7) `FS-301` → `FR-10210`. |
| `BL-0344` / VR-1332 F-2 | the sensor-contention test → `FR-3210`; 3 eclipse tests → `FR-1210`; 2 drag tests → `FR-1230`; the debris-estimate test → `FR-1430`; the harden test → `FR-1420`; 2 cell-activity inject rows → `FS-101`. |
| `BL-0347` / VR-1333 F-1 | nine invalid-parameter tests in `test_order_param_hardening.py` and two in `test_observe_order_remediation.py` → `NFR-1600`; `test_web.py::test_ephemeris_cell_observed_route_fog_of_war_enforced` → `FR-7420`; `test_web.py::test_maneuver_ledger_route_and_csv_export_are_fog_scoped` → `FR-1320`; the no-drag-coefficient test → `FR-1230`; single tests in `test_web.py` and `test_telemetry.py` → `FR-8110`, `FR-2310`, `FR-6410`, `FR-1120`; the inject-rejection test in `test_console_small_fixes.py` → `NFR-1600` or `FS-106`; the `period_s` test → `NFR-1600`; and the `test_defensive_audit` and `test_space_weather_index` items VR-1333 names. |

The roughly 90 tests the reports say have **no** leaf are not retagged: they need new leaves, which
is `04-requirements-engineering`'s work (`BL-0342`, `BL-0345`, `BL-0348`), and are out of scope here.

### Design Decisions

1. **The reports are the work list; the requirement text is the check.** The implementer derives
   each concrete function name from the "groups above" tables in VR-1331, VR-1332 and VR-1333, and
   reads the target leaf's text in `docs/requirements/` before applying it. A retag whose leaf does
   not describe what the test verifies is not applied; it is recorded in the completion note as a
   finding. The reports' own wording ("suggest", "or") leaves a few choices (`FS-106` vs `NFR-1600`;
   `FS-201` vs `FR-10110`): choose the leaf, per FS-133 Decision 2.
2. **Retag, never add or drop an ID that is not in the table without a reason.** A test may keep an
   existing ID when it still fits and the new one is added; the table says "→" where the old ID is
   replaced. Never remove the last ID from a test.
3. **A guard test pins the result.** A new module encodes each retag as `(module, function) →
   expected ID set` and asserts the collected origin records match. It fails first (test-first),
   passes after the retag, and protects the improvement from later drift. It reads the same
   collected-record view the origin checks use.
4. **Counts are stated from the tree.** `IP-1331`'s header and note said 186 tests where the modules
   hold 180 functions (208 collected items) and `IP-1332` said "about 300" for 447. This package
   does not edit those packages' text (header corrections are a separate documentation pass,
   `BL-0355`); the completion note reports the actual numbers it observed.

## Feature Reference

[FS-133](../../features/FS-133-test-origin-traceability.md): Decision 2 (prefer the requirement leaf
over the feature, the feature over the package ID) and the backfill criteria.

## Requirements Covered

| ID | How |
|---|---|
| `NFR-2820` | Every test continues to declare an origin, and the origin is the most specific live baseline item that fits. |
| `NFR-2850` | The RTM Test column is regenerated from the new tags, never hand edited. |

Both are in FS-133's Requirements Implemented; none added, none dropped.

## Architecture Components

- **Test suite only** (`spacesim/tests/`), plus the generated RTM Test column
  (`docs/requirements/03-requirements-traceability-matrix.md`).

No production code, engine, session, web or content change; determinism and import guard unaffected.

## Interfaces

None changed. The `verifies` marker and the origin-check machinery (`IP-1330`) are used as-is.

## Files to Create

- `spacesim/tests/test_origin_retag.py` (the guard table).

## Files to Modify

Test modules that carry a retag (marker arguments only), per the table above. Checked against the
tree at `fca85bf`: `test_orders.py` (the `IP-2010` tests near lines 534–598 and the replay-identical
test), `test_config.py` (`test_content_*`, lines 60–102), `test_orbit.py` (lines 27–39),
`test_content.py` (line 47), `test_assessment.py`, `test_research_batch.py`, `test_planning.py`
(line 105), `test_future_work_batch11.py` (drag, eclipse tests), `test_effects.py` (debris estimate),
`test_ssn.py` (line 202, harden), `test_order_param_hardening.py`,
`test_observe_order_remediation.py`, `test_web.py` (lines 195 and 643, and the single tests
VR-1333 names), `test_telemetry.py`, `test_space_weather_index.py`, `test_console_small_fixes.py`,
`test_defensive_audit_2026.py`, `test_cell_activity.py`. If a function named by a report has been
renamed or removed, say so in the completion note rather than guessing a substitute.

- `docs/requirements/03-requirements-traceability-matrix.md`: Test column regenerated, not edited.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, index, `ROADMAP.md`) before editing.
2. Write `test_origin_retag.py` with the full expected table (from the three reports, each leaf
   checked against `docs/requirements/`). Run it: it fails, listing each test whose tags differ.
3. Apply the retags, module by module. Re-run the guard until green.
4. Run `python3 -m pytest --origin-report=rtm` to regenerate the matrix Test column, and commit it
   in the same change.
5. Run the full suite, `test_determinism.py` and `test_import_guard.py`; confirm the number of
   collected items is unchanged from before the package.
6. Documentation updates, then mark `COMPLETE`.

## Tests to Add

`spacesim/tests/test_origin_retag.py`, module marker `@pytest.mark.verifies("NFR-2820")`:

1. **Each listed retag is in place.** One parametrized case per `(module, function)` row of the
   expected table; passes only when the test's declared IDs equal the expected set. Before the
   change: every row fails (the old, weaker IDs).
2. **No test lost its last ID and none gained an unresolvable one.** Over the whole suite, every
   collected test still declares at least one ID and every ID resolves (`NFR-2820`; this is the
   existing origin check's assertion, repeated here only for the retagged set, so a bad retag names
   itself).
3. **Collected count unchanged.** The number of collected tests equals the number before the
   retag, read from a constant recorded at implementation time. (Tag changes must not add or
   remove tests.) Use a lower and upper bound taken from the pre-change run rather than an exact
   equality if the suite grows from parametrization elsewhere.

The existing `test_test_origins.py` checks (the committed matrix Test column equals the generated
one; every declared ID resolves) are the second gate and must pass unchanged.

## Documentation Updates

- RTM Test column regenerated (above); no hand edit.
- `docs/features/FS-133-test-origin-traceability.md`: `Referenced By` only.
- MBP row and tally, `packages/INDEX.md`, `ROADMAP.md`, this header.
- Findings for `04` (no-leaf tests, `BL-0342`/`0345`/`0348`) are not worked here; the completion
  note lists any retag that was declined because its leaf did not fit.

## Definition of Done

- The guard test exists, was seen failing first, and passes.
- Every retag in the table is applied, or declined with a stated reason in the completion note.
- The RTM Test column is regenerated and `test_test_origins.py` passes.
- Collected test count unchanged; full suite green; `test_determinism.py` and `test_import_guard.py`
  green.
- `git diff --stat` shows only tests, the RTM, and package/plan docs; `git diff -- spacesim/ ':!spacesim/tests'`
  is empty.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. `git diff` of every touched test module changes only `verifies(...)` arguments (and nothing else).
2. No file outside `spacesim/tests/`, the RTM and the plan docs changed.
3. Spot-check five retags against the requirement text: each leaf describes what the test checks.
4. `python3 -m pytest --origin-report=rtm` produces no further change to the matrix.
5. Collected item count equals the pre-change count.
6. Full suite and both permanent gates green.

## Dependencies

`IP-1330`, `IP-1331`, `IP-1332`, `IP-1333` (all `VERIFIED`). **Carve-out (release-push pass 2):**
the `test_assessment.py` (13) and `test_research_batch.py` (7) rows of the table above need `FR-10110`/
`FR-10210`, which the origin reader cannot accept until [`IP-1335`](IP-1335-test-origin-id-widening.md)
(`BL-0368`) widens it; `IP-1335` delivers those 20 retags and `IP-1334` builds after it and omits those
two modules from its guard table. Ordering: build **last** in the release
push. `IP-1102`, `IP-1072` and `IP-1073` add and edit tests in several of the same modules
(`test_web.py`, `test_self_contained_save.py`, `test_browser_console_rules.py`) and regenerate the
same RTM column; retagging after them avoids merge conflicts and a stale matrix. It is otherwise
independent and low risk.

## Risks

- **A retag that does not fit.** Mitigated by Design Decision 1 (read the leaf, decline if it does not
  describe the test) and the spot-check in the checklist.
- **Matrix churn.** The Test column changes for many rows; the regeneration is deterministic and
  idempotent (`test_test_origins.py` checks both).
- **Concurrent edits to tag lines.** Any other package in flight that edits the same decorator lines
  conflicts; hence the ordering above.

## Rollback Considerations

Revert the commit. Marker arguments and one new test module only; the RTM column regenerates to the
previous values.

## Completion Note (2026-10-24, `08`)

- **Scope as built.** I reviewed every test function independently, not only the report tables:
  977 functions (1,284 collected), plus the tests that the merged `IP-1311`/`IP-1102`/`IP-1072`/`IP-1073`
  stack and the later `IP-1103`/`IP-1074`/`IP-1335`/`IP-1075` stack added (1,464 collected without the guard). 170 functions
  were retagged (the 20 assessment/research tests are `IP-1335`'s FR-10110/FR-10210 retag, kept as it landed). Every change is to a
  `verifies(...)` argument, or a dropped/re-homed module-level mark; no assertion, fixture or production line changed.
- **Beyond the report tables.** Read paths tagged `NFR-2410` (controller view, RIC view, quick TLE,
  telemetry export, dry-run, AAR reconstruction). White-only refusals tagged `FR-4320` (inject
  edit/cancel, seat assignment, Creator seats, vignette load). New leaves applied: `FR-2330` (telemetry
  attack signatures and nominal trace, 15 tests) and `FR-4460` (inject library, 6 tests). Module-level
  over-claims dropped in `test_self_contained_save.py`, `test_white_only_controls.py` and
  `test_save_load_robustness.py` and `test_white_control_correctness.py` (the save-validation tests that relied on the
  module mark now carry `FR-7230`/`NFR-1600` each). Bus/defence verb tests → `FS-105`, AAR export → `FS-107`, and the
  vignette-source endpoint → `FS-115`, because no leaf fits them.
- **Five-digit IDs.** `IP-1335` widened `baseline_ids.py`, so `FR-10110`/`FR-10210` now resolve: the two
  `test_orders.py` confidence-at-decision tests now carry `FR-10110`. `test_collect_blocked_when_storage_full` stays on `FR-2210`, whose
  AC states the storage-full rejection. `FS-106` vs `NFR-1600` for the inject-rejection test: chose the leaf.
- **Guard.** `spacesim/tests/test_origin_retag.py` pins 171 `(module, function)` origin sets. I saw it
  fail on the old tags before the retag. Collected-count bounds: 1,464 to 1,700, excluding the guard module.
- **No-leaf tests for `04`** (left on the nearest ID): bus/defence verbs; perturbation functions;
  AAR export; sim-time representation; SIGINT geolocation; telemetry series history shape/cost;
  vignette library content/placement; scene content fields; tutorial endpoint and SSN smoke check;
  window cache, ops-fidelity levels and the single phase-angle definition; space-weather severity coercion; ISR
  beam-mode behaviour.
