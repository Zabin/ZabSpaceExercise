# FS-133 — Test-Origin Traceability & Major-Release Verification

> **Document ID:** FS-133
> **Version:** 1.1 (2026-10-23, pipeline run #228: adds `NFR-2850` — the matrix's Test column is generated from the markers, `BL-0322`). v1.0: run #214.
> **Status:** ✅ Ready for implementation planning
> **Approved input:** the Feature Catalog entry `FEAT-12100` (Test-Origin Traceability &
> Major-Release Verification, Epic `EP-12000`) in
> [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md),
> following the FS-130–FS-132 convention (a catalog row, not a DOM/ADS chain, is the approved
> input). Owner directions it elaborates: `BL-0310` (test origins; audit at major releases only;
> the marker form, run #209) and `BL-0299` (dependencies locked at major releases), in
> [`docs/pipeline/backlog.md`](../pipeline/backlog.md).
> **Referenced By:** [feature index](feature-index.md); `FEAT-12100`; [IP-1330](../implementation/packages/IP-1330-test-origin-marker-and-checks.md)–[IP-1333](../implementation/packages/IP-1333-test-origin-backfill-web.md) (planned 2026-10-23); [IP-1334](../implementation/packages/IP-1334-test-origin-retag.md) (retag, 2026-10-24)
> **Related Topics:** `FEAT-12300` (documentation-integrity checks, `BL-0297` — shares the check
> runner, not yet specified); [GDS-10](../architecture/10-requirements-traceability-matrix.md) §6
> F3 and OQ1–OQ2; [GDS-06](../architecture/06-non-functional-requirements.md) NFR-5, NFR-7, NFR-18

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. Its "system" is
the project's test suite and release process rather than the simulator: the users are the
pipeline's stages and the people who run them, not exercise cells.*

## Feature ID

FS-133

## Title

Test-Origin Traceability & Major-Release Verification

## Purpose

Make every test say what it verifies, so the traceability matrix's Test column is read rather than
inferred, and give each major release a relevance audit and a reproducible dependency set — per
`FEAT-12100`'s Purpose (owner directions `BL-0310`, `BL-0299`). Today no test cites a requirement
ID (GDS-10 F3); the suite holds 1,111 collected tests in 72 modules (collection on 2026-10-23), none
of them tagged.

## Scope

In scope:

- the origin marker's registration and its rules (which IDs, in what order of preference);
- the backfill of every existing test with a marker;
- an automated check, run with the full suite, that every test declares an origin and every
  declared ID resolves to a live baseline item;
- a read-only origin report that the RTM's Test column (`04`) and the major-release relevance audit
  (`11`) read;
- the major-release dependency lock: what it must contain and how its presence is checked.

Out of scope: the browser suite (`NFR-2840`, FEAT-12200 — its tests will carry the marker like any
other); the documentation-integrity checks `NFR-3800`–`NFR-3830` (FEAT-12300), though the
resolution check here may share their runner; engine coverage and the import guard (`NFR-1900`,
FEAT-1100); running the audit or committing a lock for any particular release (`11-release-readiness`'s
job, which consumes what this Feature supplies); judging whether a test is still meaningful (the
judgment half of the audit, done by a person at `11`).

## Requirements Implemented

NFR-1510 (released builds install identical dependency versions), NFR-2820 (every test declares
the requirement or feature it verifies), NFR-2830 (test relevance audited at each major release),
NFR-3840 (every declared test origin resolves), *(v1.1)* NFR-2850 (the traceability matrix's Test
column is generated from declared test origins) — per `FEAT-12100`'s `Included Requirements`.

## Design Decisions

Settled by the owner (`BL-0310` run #209, `BL-0299`) and carried forward verbatim, not re-decided:

1. **Marker form.** A registered pytest marker, `verifies`, taking one or more IDs, applied per
   test, or per module when every test in the module verifies the same IDs. The marker is declared
   in the project's pytest configuration (`pyproject.toml`) so that, under strict-marker mode, an
   unregistered or misspelt marker fails collection.
2. **ID preference.** A requirement leaf (`FR-xxxx`/`NFR-xxxx`); else a feature specification
   (`FS-xxx`); a package (`IP-xxxx`) only for a test of a package's own completion criteria with no
   leaf. Several IDs are allowed when a test genuinely verifies several leaves.
3. **Gate tests tag their invariant's leaf.** No separate invariant tag: invariant 1 → `NFR-1500`
   or `FR-1120`, 2 → `NFR-1900`, 3 → `NFR-2300` or `FR-6210`, 4 → `FR-3110`, 5 → `NFR-1700`,
   6 → `NFR-2000` (GDS-06 invariant table).
4. **The relevance audit runs only at major-release verification**, in `11-release-readiness`; the
   mechanical checks (every test tagged, every tag resolves) run with the full suite on every run
   (`BL-0297`: the integrity checks are part of the suite, so every `09` run gates on them).
5. **Minimum versions during development, an exact lock at each major release** (`BL-0299`,
   `NFR-1510`).

## User Workflows

1. **Writing a test** — an `08` implementer writes a test and marks it with the IDs that the
   package's `Tests to Add` names (`07`); the suite run checks the marker exists and resolves.
2. **Backfilling** — a `08` implementer, working one package, reads each existing test module,
   decides what each test checks, and marks the module or each test.
3. **Verifying a package** — `09` runs the full suite; the origin checks fail if any test the
   package added is untagged or names an ID that does not exist; `09` also reads each new tag
   against the package's covered requirements (a judgment the check cannot make).
4. **Regenerating the RTM Test column** *(v1.1, `NFR-2850`)* — whoever changes a test's origin (an
   `08` implementer, a backfill package) or a requirement leaf (`04`) regenerates the matrix's Test
   column with the origin report in the same commit. Regeneration is mechanical — no judgment, no
   hand edits — so any stage may run it. The suite fails if the committed column differs from what
   the report would generate.
5. **Retiring a requirement** — a `04` pass retires or supersedes a leaf; the next suite run fails on
   every test still citing it, naming the test and the retired ID; the owning stage retags or
   retires the test.
6. **Major-release verification** — `11` runs the origin report for the release's scope and records
   untagged tests, tests citing retired IDs, in-scope requirements with no test, and likely
   duplicates (tests naming the same IDs, which a person then compares); it confirms a dependency
   lock file is committed for the release, and records a missing lock as NO-GO.
7. **Cutting the lock** — at a major release, a maintainer generates the lock from the current
   declared dependencies, installs from it in a clean environment, runs the full suite against it,
   and commits it with the release.

## System Behaviour

- **Registration** (NFR-2820, Decision 1): the `verifies` marker is declared in the pytest
  configuration. Once the backfill is complete, strict-marker mode is on, so a misspelt marker
  (`verify`, `verfies`) fails collection. Edge case: during a staged backfill, strict mode may be
  turned on before every test is tagged — strict mode checks marker *names*, not their presence.
- **Every test declares an origin** (NFR-2820): an automated check in the full suite collects every
  test and fails, listing each test with no `verifies` marker (directly or through its module). A
  marker with no IDs counts as no marker. Edge case: parametrized tests inherit their function's
  marker, so 1,111 collected items do not need 1,111 markers.
- **Every declared ID resolves** (NFR-3840): the same check reads every declared ID and fails,
  naming the test and the ID, when the ID is not a live baseline item. The live baseline is:
  numbered `FR-xxxx` leaves in `docs/requirements/01-functional-requirements.md` and `NFR-xxxx`
  leaves in `02-non-functional-requirements.md` (not Candidate Requirements); `FS-xxx`
  specifications listed in `docs/features/feature-index.md`; `IP-xxxx` packages listed in
  `docs/implementation/packages/INDEX.md`. Edge cases: an ID in a malformed shape (`FR-12`,
  `REQ-1`) fails; a Candidate Requirement ID fails (candidates are not baseline); a leaf marked
  retired or superseded fails (how retirement is marked is Open Question 1).
- **Origin report** (NFR-2830, workflows 4 and 6): a read-only command lists, from one collection
  of the suite, each test with its declared IDs, and the inverse — each baseline requirement with
  the tests that name it, and the requirements no test names — optionally limited to a set of
  requirement IDs (a release's scope). It writes nothing into the repository and changes no test
  state. It is what lets the RTM's Test column be generated rather than inferred (GDS-10 OQ1/OQ2).
- *(v1.1)* **Generated Test column** (`NFR-2850`): the report has a second mode that rewrites only
  the Test cells of `docs/requirements/03-requirements-traceability-matrix.md` — each requirement
  row's cell becomes the list of tests whose origin names it (by module and test name), or
  `UNASSIGNED`; every other column and every other line of the file is left byte-identical.
  Candidate rows stay as they are. A suite check regenerates the column in memory and fails,
  naming the rows, if it differs from the committed file — so a hand edit, a stale cell, or a
  tagged test whose row was not regenerated is caught. Edge cases: a requirement row the report
  doesn't know (not a baseline leaf) is reported, not silently skipped; a test naming a feature or
  package ID appears in no requirement row (those IDs have no row).
- *(v1.1)* **When the check turns on.** The first regeneration replaces today's hand-filled cells
  (kept as hints in git history at `9d50ed6` and listed in `requirements-change-log.md` CHG-020)
  with mostly `UNASSIGNED` cells; each backfill package then regenerates as it tags. The check is
  on from the package that delivers the generator.
- **Backfill accuracy**: each marker names what the test *asserts*, not what its file name
  suggests; a test that asserts no requirement-level behavior gets the package ID that introduced
  it (Decision 2). Edge case: a test with no traceable origin at all is recorded for the
  major-release audit rather than given an invented ID (Open Question 3).
- **Major-release lock** (NFR-1510): the release's lock file resolves every dependency, including
  indirect ones, to an exact version, for every dependency group the release supports (core, the
  content and UI extras, and the test group). Between major releases, the declared dependencies
  stay as minimum versions and no lock is required. Edge case: a lock that no clean install has
  been tested against does not count — the suite must pass in an environment installed from it.

## Subsystem Responsibilities

The architecture's component set (C1–C12) has no component for the test suite, its configuration
or the release process (feature review F-16 and F-22); these rows name the existing locations.

| Location | Responsibility |
|---|---|
| `pyproject.toml` (pytest configuration, dependency declarations) | Registers the `verifies` marker; enables strict-marker mode once the backfill lands; keeps dependencies as minimum versions. |
| `spacesim/tests/` (every test module) | Carries the markers (backfill); hosts the origin-check test, which reads `docs/` the way `test_training_sources.py` already does (`NFR-3400`). |
| The origin report (a read-only command, location chosen at `07`) | Lists tests by origin and requirements by test; shared by `04` and `11`. |
| The release's lock file (committed at each major release) | Records exact versions (`NFR-1510`). |
| `docs/requirements/`, `docs/features/feature-index.md`, `docs/implementation/packages/INDEX.md` | Read-only sources of the live baseline IDs. |

## Interfaces Used

None of the ICD's `INT-xxxx` interfaces — this Feature touches no runtime component. The only
"interfaces" are the pytest marker and collection mechanism and the markdown ledgers it reads,
neither of which is an ICD interface (consistent with FEAT-12100's catalog entry).

## Data Model Changes

None to the Domain Model or any runtime data. The repository gains one registered marker, one lock
file per major release, and no new documentation format.

## State Changes

None at runtime. Repository state: markers added to tests; strict-marker mode switched on once
(after the backfill); a lock file added at each major release.

## Error Handling

- Untagged test → the origin check fails, listing every untagged test (not just the first).
- Tag names an unknown, malformed, candidate, retired or superseded ID → the check fails, naming
  test and ID.
- Misspelt marker name → collection fails under strict-marker mode.
- A baseline ledger unreadable or missing (renamed file) → the check fails with a message naming the
  ledger, rather than silently resolving nothing.
- No lock committed at a major release → NO-GO at `11` (that skill's existing rule); a lock whose
  install fails the suite → NO-GO.

## Performance Considerations

The origin check reads a few markdown files and the collected test list; it must not add a second
collection of the suite inside the run (the check uses the items pytest has already collected).
No NFR sets a time budget; none is invented.

## Security Considerations

None runtime. The lock file pins exact versions, which supports `NFR-2200`'s reproducibility; it
does not by itself screen dependencies for vulnerabilities, and nothing here claims it does.

## Acceptance Criteria

1. The `verifies` marker is registered; with strict-marker mode on, a test marked `verfies` fails
   collection.
2. Every collected test in the suite carries at least one `verifies` ID (directly or through its
   module); the origin check passes on the backfilled tree.
3. Adding an untagged test makes the origin check fail and name that test.
4. Tagging a test with a non-existent ID (`FR-9999`), a malformed one, or a Candidate Requirement ID
   makes the check fail and name the test and ID.
5. Each permanent gate test (`test_determinism.py`, `test_import_guard.py`) names its invariant's
   leaf per Decision 3.
6. The origin report, run on the backfilled tree, lists for a given requirement ID the tests that
   name it, and lists the requirements no test names; running it changes no file.
6a. *(v1.1)* Regenerating the matrix changes only Test cells; a second regeneration changes nothing;
   hand-editing one Test cell, or tagging a test without regenerating, makes the suite fail naming
   the row.
7. A sample of at least one test per backfilled module, read by the verifier, asserts behavior that
   its marker's requirement describes (checked at `09`).
8. At the first major release: a committed lock file resolves every dependency (core, extras, test
   group) to an exact version, and the full suite passes in a clean environment installed from it.

## Verification Plan

- Criteria 1–6: Test (the origin check is itself a test; criteria 3–4 are checked by tests that run
  the check against a small synthetic test set, not by breaking the real suite).
- Criterion 7: Inspection at `09`.
- Criterion 8: Inspection plus a clean-install test run at the first major release, recorded in its
  Release Assessment (`NFR-1510`'s verification method).
- Criterion 6a: Test (against a copy of the matrix in a temporary directory, not the real file).
- Every new test carries `@pytest.mark.verifies(...)` naming `NFR-2820`, `NFR-3840`, `NFR-2830` or
  `NFR-2850`.

## Dependencies

`FEAT-1100` and `FEAT-5300` per the catalog (`NFR-1510` cites `NFR-1500` and `NFR-2200`) — both
built. No `FS-xxx` prerequisite. Coordinates with FEAT-12300 (shared runner, Open Question 2).

## Risks

- **Tagging by file name.** A backfill that tags `test_jam.py` with whatever leaf mentions jamming,
  without reading what each test asserts, would recreate the inference GDS-10 F3 found. Mitigation:
  criterion 7, and the audit at each major release.
- **Size of the backfill.** 72 modules in one package is large to review; `07` may split it into
  several packages by module group, with strict mode and the completeness check enabled only when
  the last lands (or with an allow-list that may only shrink, the pattern `BL-0297` sets for
  broken links).
- **Ledger formats drift.** The resolution check parses markdown ledgers; a reformatted ledger could
  make every ID unresolvable. Mitigation: fail loudly when a ledger yields no IDs (Error Handling).

## Open Questions

1. **How retirement is marked.** `NFR-3840` fails a test citing a retired or superseded ID, but the
   requirements documents have no uniform retired/superseded marker, and `BL-0297`'s
   retired-documents register is still undecided in form. Matters because without a marker the
   check can only test existence. **Resolution path:** `04` defines how a leaf is retired (and
   `FEAT-12300`'s specification defines the register); until then the check tests existence and
   candidate status only, and says so.
2. **One runner or two.** Whether the origin check and FEAT-12300's documentation checks share one
   test module and one ledger parser. Matters for duplication, not behavior. **Resolution path:**
   `07`, when it plans FEAT-12300's package alongside this one.
3. **Tests with no traceable origin.** Some existing tests may check behavior no requirement, FS or
   package names (GDS-10 F5 found 16 test files no package names). Matters because inventing an ID
   defeats the purpose. **Resolution path:** the backfill lists them; `04` decides at the next pass
   whether each reveals a missing requirement or a test to retire. The completeness check needs them
   tagged, so the backfill tags each with the package that introduced it where one exists and
   records the rest for `04`.
4. **What counts as a major release.** `NFR-1510` and `NFR-2830` apply "at each major release",
   but the release plan's buckets (Prototype, MVP, Release 1, Release 2) do not say which are major;
   `11-release-readiness` defers to "a bucket the release plan marks as major, or one the owner
   names". **Resolution path:** owner decision, recorded in `01-release-plan.md` by `05`.
5. **Lock tooling.** No ADR names a lock tool (ADR-0020 lists the stack, not packaging tools).
   **Resolution path:** `07` chooses for the first major release; if the choice constrains
   contributors, `03` records it as an ADR.

## Related ADRs

ADR-0002 (deterministic core — the reason `NFR-1510` exists), ADR-0020 (tech stack: pytest, the
declared dependencies).

## Related Interfaces

None.
