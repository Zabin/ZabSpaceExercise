# IP-1335 — Test-Origin ID Widening: Five-Digit Requirement IDs Can Be Declared, the Assessment and Research Tests Are Retagged, and the Top-Level-YAML Scan Case Is Pinned (NFR-2820, NFR-2850, FR-5310; test-only)

> **Package ID:** IP-1335
> **Version:** 1.0
> **Status:** ✅ COMPLETE 2026-10-24 (`08-code-implementation`; awaiting `09-package-verification`) — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 2).
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24,
> recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, authorizes
> remediation packages for bugs, in-progress and critical items. Authoring is not itself the
> authorization; that recorded decision is.
> **Dependencies:** [FS-133](../../features/FS-133-test-origin-traceability.md) (the spec);
> [IP-1330](IP-1330-test-origin-marker-and-checks.md) (the reader and checks it widens) and
> [IP-1332](IP-1332-test-origin-backfill-session.md) (the backfill whose weak tags it fixes), both
> `VERIFIED`; for the second part, [FS-131](../../features/FS-131-load-time-vignette-validation.md)
> and [IP-1311](IP-1311-vignette-id-scan-robustness.md) (`VERIFIED`, [VR-1311](../verification/VR-1311-vignette-id-scan-robustness.md)).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0368`, `BL-0361`
> **Produces:** an origin reader and RTM generator that accept `FR-` identifiers of four or five
> digits; the 20 assessment and research tests tagged `FR-10110`/`FR-10210`; a regenerated RTM Test
> column; and one new test that pins the "top-level YAML is not a mapping" branch of the vignette id
> scan.
> **Feature Reference:** [FS-133](../../features/FS-133-test-origin-traceability.md) (`FEAT-12100`);
> [FS-131](../../features/FS-131-load-time-vignette-validation.md) (`FEAT-5300`) for the scan test
> **Related Topics:** [VR-1332](../verification/VR-1332-test-origin-backfill-session.md) F-1,
> [`spacesim/tests/baseline_ids.py`](../../../spacesim/tests/baseline_ids.py),
> [IP-1334](IP-1334-test-origin-retag.md)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (test-only). No production file under `spacesim/` outside `spacesim/tests/`
changes. The test-infrastructure fix comes first because the retag cannot be applied without it.*

---

## Package ID

IP-1335 (FS-133 → `IP-133x`; `IP-1334` is the retag whose assessment/research rows this package
carries).

## Title

Test-origin ID widening, with the assessment/research retag and one vignette-scan test.

## Objective

### Part A — the defect (BL-0368, Medium)

`spacesim/tests/baseline_ids.py` knows only four-digit `FR-` identifiers. Three places encode that:

- `WELL_FORMED` (line 25): `FR-\d{4}`. A marker naming `FR-10110` fails the "well formed" check.
- `load_baseline()` (line 55): the ledger reader matches `^#### (FR-\d{4})\b`; the five-digit headings
  `#### FR-10110`, `#### FR-10210` and the whole `FR-11xxx` family (seven leaves, `FR-11110`–`FR-11420`) are
  not read, so even a well-formed ID would be "not in the baseline ledger".
- `regenerate_matrix()` (line 176): `^((?:FR|NFR)-\d{4})\b` never matches a matrix row such as
  `| FR-10110 *(new 2026-07, promoted from CR-19)* | …`, so those rows' Test cells would never be
  generated.

Result: the 13 tests in `test_assessment.py` and 7 in `test_research_batch.py` stay on the feature
IDs `FS-201`/`FS-301`, although `FR-10110` and `FR-10210` exist as baseline leaves; the training
requirements `FR-11110`–`FR-11420` can never be named by a test (relevant to `FR-11420`, whose
playbook test `test_vignette_tutorials.py` is the obvious origin).

After this package: all three places accept four- or five-digit FR identifiers; the 20 tests carry
the leaf; the RTM rows for the five-digit leaves are generated from the tags like every other row.

### Part B — retag the 20 tests

`test_assessment.py` (13 tests, currently `FS-201`) → `FR-10110`; `test_research_batch.py` (7 tests,
currently `FS-301`) → `FR-10210`, per `VR-1332` F-1. This is the same work item `IP-1334` lists for
those two modules; it moves here because it depends on Part A. `IP-1334` is adjusted (below) so the
two packages do not both do it.

### Part C — vignette scan test (BL-0361, Low)

`VR-1311` F-1: no test has a vignette file whose **top-level** YAML is a list or a scalar; only
`vignette:` values are non-mapping. Dropping the `isinstance(raw, dict)` branch of
`content/vignette.py::_declared_vignette_id` would raise `AttributeError` (a 500 on an id lookup) and
the suite would pass. One test closes it.

## Requirements Covered

| ID | How |
|---|---|
| `NFR-2820` | Every test declares an origin that is a live baseline item; five-digit leaves now qualify. |
| `NFR-2850` | The RTM Test column is generated from the tags for every leaf, five-digit ones included. |
| `FR-5310` | The vignette lookup's behaviour on a malformed neighbouring file is pinned (Part C; existing behaviour, no code change). |

`NFR-2820` and `NFR-2850` are in FS-133's list; `FR-5310` is in FS-131's. None added, none dropped.

## Architecture Components

- **Test suite only** (`spacesim/tests/`): `baseline_ids.py` (helper), the two retagged modules,
  `test_vignette_id_scan.py`, and the new guard module; plus the generated RTM Test column
  (`docs/requirements/03-requirements-traceability-matrix.md`).

No production, engine, session, web or content change; determinism and import guard unaffected.

## Interfaces

None changed. The `verifies` marker, `conftest.py` collection and the origin checks are used as-is.
`baseline_ids.py` is a test helper, not a product interface.

### Design Decisions

1. **One shared pattern for the FR identifier.** Introduce a single module-level pattern/constant for
   "FR- followed by four or five digits" in `baseline_ids.py` and use it in all three places, so the
   three cannot drift again (this is the defect's cause). NFR stays four digits (`NFR-3400`–`3600` are
   four-digit; widening NFR is not asked for, and a wider pattern would loosen the check for no
   evidence of need).
2. **Do not widen to "any digits".** Four or five, anchored with a word boundary, so `FR-123456` and
   `FR-12` are still malformed. The existing malformed-ID test cases keep passing; two new boundary
   cases are added.
3. **Baseline now includes the five-digit leaves.** `load_baseline()` returns them. This changes
   `--origin-report`'s "requirements no test names" list by the leaves that have no test (the seven
   `FR-11xxx` leaves, until a test names them). That is correct and intended; it must not fail any
   check. Confirm that no check treats "a baseline leaf with no test" as an error (none does today).
4. **Retag by the requirement text.** Read `FR-10110` and `FR-10210` (`docs/requirements/
   01-functional-requirements.md`, lines 3542 and 3589) before applying. `VR-1332` F-1 says all 13
   and 7 tests fit; a test whose behaviour is not the leaf's (for example a pure helper test) keeps
   `FS-201`/`FS-301`, and the completion note names it. Never remove the last ID from a test.
5. **`IP-1334` is adjusted, not duplicated.** `IP-1334` (retag, `READY`) lists the same two modules.
   This package's dependency note in `IP-1334` says: build after `IP-1335`; the `test_assessment.py`
   and `test_research_batch.py` rows are delivered here, and `IP-1334` omits them from its guard
   table. Only that Dependencies sentence in `IP-1334` is edited by this planning pass.
6. **Part C is test-only and expects to pass on arrival.** It documents a branch, so it is verified
   by mutation (drop the `isinstance(raw, dict)` check in a scratch copy and see the new test fail),
   not by a failing-first run. The completion note says so.

## Files to Create

- `spacesim/tests/test_origin_id_widening.py`: the guard for Parts A and B (and boundary cases).

## Files to Modify

Checked against the tree at `501b36d`:

- `spacesim/tests/baseline_ids.py`: `WELL_FORMED` (line 25), `load_baseline()` FR regex (line 55),
  `regenerate_matrix()` row regex (line 176); the error text in `resolve_problem` (it lists
  `FR-nnnn`) gains `FR-nnnnn`.
- `spacesim/tests/test_assessment.py`: the 13 `verifies("FS-201")` decorators (lines 73–214).
- `spacesim/tests/test_research_batch.py`: the 7 `verifies("FS-301")` decorators (lines 17–101).
- `spacesim/tests/test_vignette_id_scan.py`: one new test, using the existing `folder` and `client`
  fixtures (a file whose entire top-level YAML is a list, and another a scalar string, in the built-in
  root and, as in the existing non-mapping test, in an external root).
- `docs/requirements/03-requirements-traceability-matrix.md`: Test column regenerated, never edited
  by hand.
- `docs/implementation/packages/IP-1334-test-origin-retag.md`: Dependencies note only (Decision 5).

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, `ROADMAP.md`).
2. Write `test_origin_id_widening.py` and the Part C test. See the Part A and B cases fail first.
3. Implement Part A (one shared pattern; three uses; message text). Re-run the guard.
4. Apply Part B's 20 retags (decorator arguments only). Re-run the guard.
5. Run `python3 -m pytest --origin-report=rtm`; commit the regenerated matrix with the change.
   Inspect the diff: only `Test` cells change, and only for rows whose tags changed
   (`FR-10110`, `FR-10210`).
6. Full suite, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`,
   `test_test_origins.py`; confirm the collected test count changed by exactly +1 (Part C) and +the
   guard module's cases.
7. Documentation updates; mark `COMPLETE`.

## Tests to Add

`spacesim/tests/test_origin_id_widening.py`, module marker `verifies("NFR-2820", "NFR-2850")`:

1. **Five-digit ID is well formed and resolves.** `resolve_problem("FR-10110", load_baseline())` is
   `None`; same for `FR-10210` and one `FR-11xxx` leaf. Fails first (malformed).
2. **Boundaries.** `FR-123456`, `FR-12`, `FR-1011` (four digits, not in the ledger), `NFR-10110`
   are each reported as a problem. Passes before and after (pins decision 2).
3. **Baseline reads the five-digit headings.** `load_baseline()["FR"]` contains `FR-10110`,
   `FR-10210` and all seven `FR-11xxx` leaves, and still contains a sample of four-digit leaves.
4. **Matrix generation places a five-digit row.** `regenerate_matrix` on the real matrix text and
   records tagged `FR-10110` yields that row's Test cell naming the assessment tests, and reports no
   unplaced rows. Fails first.
5. **The 20 retags are in place.** Parametrized over the 13 and 7 test functions: each declares
   `FR-10110` (or `FR-10210`) and no longer `FS-201`/`FS-301`, read from the collected records the
   origin checks use. Fails first.
6. **Count guard.** The collected count of both modules is unchanged (13 and 7).

`spacesim/tests/test_vignette_id_scan.py`, existing module marker (`FR-5310`, `NFR-1600`):

7. **Top-level list or scalar files are skipped, in both roots.** With a file whose whole content is
   `- a\n- b\n` and another `just text\n` in the built-in root, and the same in an external root:
   `load_vignette("nosuch", ...)` raises `FileNotFoundError`; a valid later-sorting vignette still
   loads; `POST /api/sessions` for `nosuch` is 404. Verified by mutation (Design Decision 6).

The existing `test_test_origins.py` checks (every declared ID resolves; committed matrix equals
generated) are the second gate and must pass unchanged.

## Documentation Updates

- RTM Test column regenerated (above); no hand edit.
- `docs/features/FS-133-test-origin-traceability.md` and `FS-131`: `Referenced By` only.
- MBP row and tally, `packages/INDEX.md`, `ROADMAP.md`, this header.
- `CLAUDE.md`: no change needed unless it states the four-digit rule (check the "Test-driven
  workflow" paragraph; it names `FR-xxxx` generically; leave it unless a statement is now false).
- Not worked here: the roughly 90 tests with no fitting leaf (`04`'s `BL-0342`/`0345`/`0348`/`0369`).

## Definition of Done

- The guard test exists, was seen failing first for Parts A and B, and passes; Part C's test exists
  and fails under the stated mutation.
- `baseline_ids.py` accepts four- and five-digit FR IDs in all three places via one shared pattern;
  malformed forms are still rejected.
- The 20 tests carry `FR-10110`/`FR-10210`; RTM Test column regenerated; `test_test_origins.py` green.
- Full suite and both permanent gates green; `git diff -- spacesim/ ':!spacesim/tests'` empty.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. `git diff` of `test_assessment.py` and `test_research_batch.py` changes only `verifies(...)`
   arguments.
2. `grep` in `baseline_ids.py` shows no remaining `\d{4}` applied to an `FR` pattern outside the one
   shared definition.
3. Spot-check three retags against the text of `FR-10110`/`FR-10210`.
4. `python3 -m pytest --origin-report=rtm` produces no further change; the matrix diff touches only
   Test cells of `FR-10110` and `FR-10210`.
5. `python3 -m pytest --origin-report` lists the seven `FR-11xxx` leaves under "requirements no test
   names" and nothing fails because of it.
6. Mutation: drop the `isinstance(raw, dict)` check in a scratch copy: the new scan test fails.
7. Full suite, both gates, doc integrity and origin tests green.

## Dependencies

`IP-1330`, `IP-1332`, `IP-1311` (all `VERIFIED`). Ordering: build **after `IP-1103` and `IP-1074`**
(they add tests in modules this package's RTM regeneration must include) and **before `IP-1334`**,
which then omits the assessment/research rows. Otherwise independent.

## Risks

- **Widening loosens the check.** Mitigated by Decision 2 and boundary test 2.
- **Newly visible leaves change the report.** Mitigated by Decision 3 and checklist item 5.
- **Retag that does not fit.** Decision 4: read the leaf; decline and note.
- **Part C cannot fail first.** Stated honestly (Decision 6); mutation is the evidence.

## Rollback Considerations

Revert the commit. Helper regexes, decorator arguments, one new test module and one test; the RTM
column regenerates to its previous values.
