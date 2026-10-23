# IP-1330 — Test-Origin Marker, Origin Checks and Origin Report (NFR-2820, NFR-3840, NFR-2830)

> **Package ID:** IP-1330
> **Version:** 1.1 (2026-10-23, run #229: adds the generated RTM Test column, FS-133 v1.1 `NFR-2850`, `BL-0322`). v1.0: run #221.
> **Status:** 🟢 READY — authored 2026-10-23 by `07-implementation-planning`, pipeline run #221.
> No package dependencies.
> **Authorization (MSTR-006 §3):** **not yet given.** Owner direction `BL-0310` decided the
> marker form and cadence; the build go-ahead is separate.
> **Dependencies:** [FS-133](../../features/FS-133-test-origin-traceability.md) v1.0 (the spec).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [IP-1331](IP-1331-test-origin-backfill-engine-content.md), [IP-1332](IP-1332-test-origin-backfill-session.md),
> [IP-1333](IP-1333-test-origin-backfill-web.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0310`
> **Produces:** the registered `verifies` marker, a suite check that every test declares a
> resolvable origin (with a shrink-only allow-list for the not-yet-backfilled modules), and a
> read-only origin report.
> **Feature Reference:** [FS-133](../../features/FS-133-test-origin-traceability.md) (`FEAT-12100`)
> **Related Topics:** FS-135 (documentation-integrity checks — may later share the ledger reader)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. The infrastructure half of FS-133; the backfill is IP-1331–IP-1333.*

---

## Package ID

IP-1330.

## Objective

**As built at `a8cf7bd`**, `pyproject.toml`'s `[tool.pytest.ini_options]` declares no markers;
the only marker in use is `parametrize`; no test names its origin; there is no `conftest.py` in
`spacesim/tests/`. The suite collects 1,111 tests in 72 modules.

After this package:

1. `verifies` is a registered marker and strict-marker mode is on (FS-133 Decision 1).
2. A suite check fails on any collected test without a `verifies` origin unless its module is on a
   committed **allow-list** of not-yet-backfilled modules, and fails on any declared ID that is not a
   live baseline item (FS-133 System Behaviour). The allow-list may only shrink: a listed module
   that is fully tagged fails the check until removed.
3. A read-only origin report lists tests by declared ID and baseline requirements by test.
4. *(v1.1)* The report can regenerate the Test column of
   `docs/requirements/03-requirements-traceability-matrix.md` (Test cells only), and a suite check
   fails when the committed column differs from the generated one (`NFR-2850`).

## Design Decisions

1. **Where the check runs.** A new `spacesim/tests/conftest.py` records each collected item's
   `verifies` IDs (and module) during collection, once (no second collection — FS-133 Performance).
   A test module `test_test_origins.py` asserts on that record. When only part of the suite is
   collected, the check covers what was collected; the full run, which `09` uses, covers everything.
2. **The baseline reader** lives in one helper module beside the tests (not a `test_` module),
   reading: `#### FR-xxxx` leaves above "Candidate Requirements" in `requirements/01`; `- **NFR-xxxx`
   leaves above it in `requirements/02`; `FS-xxx` links in `docs/features/feature-index.md`;
   `IP-xxxx` links in `docs/implementation/packages/INDEX.md`. It fails loudly when a ledger yields
   no IDs. FS-135's checks may reuse it later (FS-133 Open Question 2: one reader, decided here;
   whether the tests share a module is FS-135's package's call).
3. **Retirement** (FS-133 Open Question 1, `BL-0317`): until `04` defines a retired marker, the
   check tests existence and non-candidate status only, and its failure message says so.
4. **The report is a pytest option** registered in the same `conftest.py` (for example
   `--origin-report`, optionally limited to a list of requirement IDs), printing after collection and
   running no tests. It needs no separate tool and reuses the same collection and reader.
5. **The allow-list starts with all 72 modules** minus the files this package itself tags, and each
   backfill package removes its modules. The target is empty, reached when IP-1333 lands.
6. **The dependency lock (`NFR-1510`) is not in this package.** It is produced at the first major
   release (which releases are major: `BL-0318`); FS-133 criterion 8 is checked by
   `11-release-readiness` then. The TWBS records this.
7. *(v1.1)* **Matrix regeneration.** A second mode of the report option (for example
   `--origin-report=rtm`) rewrites only the Test cell of each baseline requirement row in the
   matrix: the tests whose origin names that requirement (`module::test`, grouped by module), or
   `UNASSIGNED`. It parses the matrix's tables by their header row (the column named `Test`),
   leaves every other cell and line byte-identical, leaves candidate rows alone, and reports a row
   whose ID is not a baseline leaf. The check (`test_test_origins.py`) runs the same generation in
   memory against the committed file. This package runs the first regeneration, which replaces the
   hand-filled cells (hints preserved at `9d50ed6` and in change-log CHG-020) — after it, only the
   two gate modules are tagged, so nearly every cell reads `UNASSIGNED`, the honest state.

## Requirements Covered

NFR-2820, NFR-3840, NFR-2830 (the report the major-release audit reads), *(v1.1)* NFR-2850 (the
generated Test column). `NFR-1510` is FS-133's
but deferred to the first major release (Design Decision 6).

## Architecture Components

Test configuration and the test suite only (`pyproject.toml`, `spacesim/tests/`); no runtime code.

## Interfaces

None runtime. Reads the four ledgers named in Design Decision 2.

## Files to Create/Modify

- **Modify** `pyproject.toml` — `[tool.pytest.ini_options]`: register `verifies` with a one-line
  description; add `--strict-markers` to `addopts` (keeping `-q`).
- **Create** `spacesim/tests/conftest.py` — collection recorder (Decision 1) and the report option
  (Decision 4).
- **Create** `spacesim/tests/baseline_ids.py` — the ledger reader (Decision 2).
- **Create** `spacesim/tests/test_origin_allowlist.txt` — one module name per line (Decision 5).
- **Create** `spacesim/tests/test_test_origins.py` — the checks.
- **Modify** `spacesim/tests/test_determinism.py`, `test_import_guard.py` — tag them now (FS-133
  criterion 5: invariant 1 → `NFR-1500`/`FR-1120`; invariant 2 → `NFR-1900`), and leave them off
  the allow-list.
- **Modify** `docs/requirements/03-requirements-traceability-matrix.md` — *(v1.1)* Test cells only,
  by running the regeneration (never by hand).
- **Docs:** `CLAUDE.md` "Test-driven workflow" (one sentence on the marker and the report option)
  and "Build/test commands" (the report command); RTM `NFR-2820`/`NFR-3840`/`NFR-2830` rows.

## Implementation Tasks

1. Baseline suite run.
2. Write `test_test_origins.py` against a synthetic set of items/ledger snippets first (criteria
   3–4 are tested on synthetic inputs, not by breaking the real suite); confirm they fail.
3. Implement the reader, recorder, allow-list handling and report.
4. Register the marker; turn on strict markers; tag the two gate modules.
5. Full suite, both gates; docs.

## Tests to Add

In `spacesim/tests/test_test_origins.py`:

| Test | Verifies | Asserts |
|---|---|---|
| Every collected test outside the allow-list has a non-empty `verifies` origin | `NFR-2820` | none missing (the real suite) |
| Allow-list only shrinks: no listed module is fully tagged; every listed module exists | `NFR-2820` | no stale entries |
| Untagged synthetic item outside the allow-list is reported by name | `NFR-2820` | report names it |
| Unknown (`FR-9999`), malformed (`FR-12`) and candidate (`CR-01`) IDs are reported | `NFR-3840` | each reported with test and ID |
| A real FR leaf, NFR leaf, indexed FS and indexed IP each resolve | `NFR-3840` | no report |
| A ledger yielding no IDs fails loudly | `NFR-3840` | error names the ledger |
| Every declared ID in the real suite resolves | `NFR-3840` | none unresolved |
| The report lists, for a given ID, the tests naming it, and the requirements no test names; it writes no file | `NFR-2830` | output content; repository unchanged |
| Strict markers on: a misspelt marker fails collection (run pytest on a temp file in a subprocess) | `NFR-2820` | non-zero exit, message names the marker |
| *(v1.1)* Committed matrix Test column equals the generated one | `NFR-2850` | no differing rows |
| *(v1.1)* On a temp copy of the matrix: regeneration changes only Test cells; a second run changes nothing; a hand-edited cell is reported by row; an unknown row ID is reported | `NFR-2850` | as stated |

## Documentation Updates

`CLAUDE.md` (marker, report command); RTM rows. The `04` skill already says to read the Test column
from the markers; no skill change.

## Definition of Done

1. `verifies` registered; strict markers on; the full suite passes with the allow-list.
2. The two gate modules tagged per FS-133 Decision 3.
3. The checks and the report work as tested above; the report's listing mode changes no file.
3a. *(v1.1)* The matrix's Test column was regenerated by the tool, and the column check passes.
4. Every new test tagged; failing-first run recorded.
5. Full suite and both gates green; docs updated.

## Verification Checklist

- [ ] `pyproject.toml` registers `verifies` and `addopts` contains `--strict-markers`.
- [ ] Removing a tag from a non-allow-listed test makes `test_test_origins.py` fail naming it
      (demonstrate once, then restore).
- [ ] The report runs (`python3 -m pytest --origin-report …` or the name chosen) and its output
      names `test_determinism.py` under `NFR-1500`.
- [ ] The allow-list holds exactly the modules not yet tagged.
- [ ] Full suite counts recorded; both gates green by name.

## Dependencies

None. IP-1331, IP-1332 and IP-1333 depend on this package.

## Risks

- **Strict mode breaking third-party markers** (plugins): none are used today; the full suite run
  is the check.
- **The allow-list as a permanent escape hatch.** Mitigation: the shrink-only rule and the three
  backfill packages that empty it; `10`/`11` report its size.
- **Ledger format changes** silently emptying the baseline: the loud-failure rule.

## Rollback Considerations

Revert the commit. Markers on tests are inert without the checks; nothing runtime changes.
