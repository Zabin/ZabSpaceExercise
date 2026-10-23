# IP-1331 — Test-Origin Backfill: Engine and Content Test Modules (NFR-2820)

> **Package ID:** IP-1331
> **Version:** 1.0
> **Status:** 🔴 BLOCKED — on [IP-1330](IP-1330-test-origin-marker-and-checks.md) reaching
> `VERIFIED` (the marker, the checks and the allow-list this package shrinks). Authored 2026-10-23
> by `07-implementation-planning`, pipeline run #221.
> **Authorization (MSTR-006 §3):** **not yet given.**
> **Dependencies:** [FS-133](../../features/FS-133-test-origin-traceability.md) v1.0;
> [IP-1330](IP-1330-test-origin-marker-and-checks.md).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0310`
> **Produces:** every test in the 22 engine and content modules below carries a `verifies` origin; those
> modules leave the allow-list.
> **Feature Reference:** [FS-133](../../features/FS-133-test-origin-traceability.md) (`FEAT-12100`)
> **Related Topics:** the sibling backfill packages IP-1332, IP-1333

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package; test-only.*

---

## Package ID

IP-1331.

## Objective

Tag every test in these 22 modules (about 186 test functions at `a8cf7bd`, more items once
parametrized) with `@pytest.mark.verifies(...)` naming what each test **asserts**, and remove the
modules from `spacesim/tests/test_origin_allowlist.txt`:

- `test_access.py`
- `test_bus.py`
- `test_cats_angle.py`
- `test_clock_and_time.py`
- `test_config.py`
- `test_custody.py`
- `test_defensive_modifiers.py`
- `test_effects.py`
- `test_orbit.py`
- `test_orders.py`
- `test_propagator.py`
- `test_recovery.py`
- `test_reference_skyfield.py`
- `test_safe_mode.py`
- `test_version.py`
- `test_bulk_import.py`
- `test_content.py`
- `test_phase_angle_gain.py`
- `test_sensor_modality_wiring.py`
- `test_tle_export.py`
- `test_typed_payload_params.py`
- `test_vignette_export.py`

## Requirements Covered

NFR-2820 (and, through the resolution check, NFR-3840 for the IDs added).

## Architecture Components

`spacesim/tests/` only. No production code, no assertion changes.

## Interfaces

None.

## Files to Create/Modify

- **Modify** each module listed in Objective — add markers (a module-level `pytestmark` where every
  test in the file verifies the same IDs; per-test markers otherwise). Nothing else in the file
  changes.
- **Modify** `spacesim/tests/test_origin_allowlist.txt` — remove these modules.
- **Modify** `docs/requirements/03-requirements-traceability-matrix.md` — Test cells only, by
  regeneration.
- Untraceable tests (task 3) are listed in this package's completion note, for `04` (FS-133 Open
  Question 3); no new file.

## Implementation Tasks

1. For each module, read every test and decide what it asserts.
2. Choose IDs by FS-133 Decision 2: a requirement leaf (`FR-xxxx`/`NFR-xxxx`) by preference, read
   from the leaf's Acceptance Criteria; else an `FS-xxx`; an `IP-xxxx` only for a package's own
   completion check with no leaf. Gate tests follow FS-133 Decision 3. Use the packages' `Tests to
   Add` and the RTM as hints, never as the answer — the test's assertions decide.
3. A test with no traceable origin: tag it with the package that introduced it if one exists
   (`git log` of the test), and list it in the completion note for `04`. Never invent an ID.
4. Remove the modules from the allow-list; regenerate the matrix's Test column with the origin
   report (`NFR-2850`, IP-1330 v1.1 — never edit a cell by hand); run the full suite (the origin
   checks and the column check must pass). The pre-generation hints for these modules' tests are in
   git at `9d50ed6` and in change-log CHG-020.
5. Run `--origin-report` for the requirements these modules touch and include the summary in the
   completion note.

## Tests to Add

None new. The checks from IP-1330 (`test_test_origins.py`, verifies `NFR-2820`/`NFR-3840`) now cover
these modules; their passing with the modules removed from the allow-list is this package's test.

## Documentation Updates

RTM Test cells for the requirements these modules now name (`04`'s matrix reads the markers; `08`
may fill the cells it can derive from the report). 

## Definition of Done

1. Every collected test in the listed modules has a resolvable `verifies` origin.
2. The listed modules are off the allow-list; the origin checks pass.
3. No assertion, fixture or test body changed (diff shows only marker lines and imports).
4. Untraceable tests (if any) listed for `04`.
5. Full suite and both permanent gates green.

## Verification Checklist

- [ ] `git diff` of the listed modules contains only marker additions (and `import pytest` where
      missing).
- [ ] A sample of at least one test per module: its marker's requirement describes what it asserts
      (FS-133 criterion 7).
- [ ] The allow-list no longer names these modules.
- [ ] Full suite counts unchanged from before the package; both gates green by name.

## Dependencies

IP-1330 (must be `VERIFIED`). Independent of the sibling backfill packages; they can land in any
order.

## Risks

- **Tagging by file name** rather than by assertion (FS-133 Risks) — the per-module sample at `09`.
- **Disagreement with the RTM.** A test whose assertions fit a different leaf than the RTM claims is
  a finding for `04`, recorded in the completion note, not resolved by bending the tag.

## Rollback Considerations

Revert the commit and restore the allow-list entries; markers are inert otherwise.
