# IP-1079 — Retag Guard Redesign: Drop the Collected-Count Bounds, Keep the Pinned Tag Sets, and Leave No Check That Skips Under Both Browser Filters (test-only)

> **Package ID:** IP-1079
> **Version:** 1.0
> **Status:** READY — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 5). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, covers it; the owner then told this session to "resolve it as you see fit" (integration review `L-5`, the count-pinned guard). Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1334](IP-1334-test-origin-retag.md) (`VERIFIED`; owns `test_origin_retag.py`), [IP-1330](IP-1330-test-origin-marker-and-checks.md) (`VERIFIED`; the `verifies` marker and the collected-origin records), [IP-1340](IP-1340-browser-console-rule-suite.md) (`VERIFIED`; the `browser` marker whose split creates the always-skipped check).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 5"), [the tranche 3 integration review](../../reviews/integration-review-tranche-3-release-push-remediation.md) (`L-5`)
> **Produces:** a retag guard that fails on a deleted, renamed or retagged pinned test, never on the suite growing, and that runs (does not skip) in each of the three ways the suite is run.
> **Feature Reference:** [FS-133 — Test Origin Traceability](../../features/FS-133-test-origin-traceability.md)
> **Related Topics:** [`spacesim/tests/test_origin_retag.py`](../../../spacesim/tests/test_origin_retag.py), [`spacesim/tests/baseline_ids.py`](../../../spacesim/tests/baseline_ids.py), [`spacesim/tests/conftest.py`](../../../spacesim/tests/conftest.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Test-only remediation package. No file under `spacesim/` other than `spacesim/tests/` changes. Prose only; no code in this document.*

---

## Package ID

IP-1079.

## Title

Redesign the `IP-1334` retag guard so normal suite growth cannot fail it and no check in it is unreachable.

## Objective

**Defect (review `L-5`).** `test_origin_retag.py` pins `COLLECTED_BEFORE = 1464` and `COLLECTED_UPPER = 1700` and fails `test_collected_count_unchanged_by_the_retag` outside that range. The suite is at 1671 collected items, so the next few feature or bug tests trip a guard whose only job was to prove a one-time tag edit added or removed no test. Two further facts:

1. The count check skips unless the whole suite was collected (`_whole_suite`). The suite is run as `-m browser` and as `-m "not browser"` (and unfiltered); under either filtered run the check skips, so the check runs only in the unfiltered run.
2. The bounds protect nothing the other checks do not already cover. Each pinned row (`EXPECTED`, about 300 rows of `(module, function, tag set)`) already fails if its test is deleted, renamed or retagged (`test_each_listed_retag_is_in_place`). The count bound adds only a ceiling that punishes growth.

**Owner direction:** resolve it as the planner sees fit. **Decision:** remove the count bounds and the check that enforces them; keep every pinned tag set; make the remaining per-row check skip only when the module is genuinely not part of this run, and fail when the module no longer exists. Show by mutation that deleting a pinned test still fails the guard.

## Requirements Covered

| ID | How |
|---|---|
| `NFR-2820` | The guard module's existing origin (`pytestmark`); every test in the suite names the requirement it verifies, and the retag cannot silently drift. Unchanged. |
| `FS-133` | New tests of the guard's own logic name the feature (no requirement leaf is about the guard itself). |
| `IP-1079` | The package's own Definition of Done tests (mutation proof, no-skip proof) use the package ID. |

## Architecture Components

`spacesim/tests/test_origin_retag.py` (the guard), `spacesim/tests/baseline_ids.py` (shared helpers; only if a pure helper is placed there), `spacesim/tests/conftest.py` (read-only here: it builds `config._verifies_records`; the builder confirms whether those records cover deselected items, see Risks). No production code. No load-bearing invariant touched.

## Interfaces

None external. Internally the guard is split into a **pure function** that takes a list of origin records, the `EXPECTED` rows, the set of test files present on disk and the set of modules collected in this run, and returns a list of problem strings; the pytest tests call it on the live records and the new mutation tests call it on edited copies. This split is what lets a test prove "a deleted pinned test fails" without deleting a real test.

### Design Decisions

1. **Remove, do not widen.** Raising `COLLECTED_UPPER` repeats the defect at the next threshold. The bounds go; so do `COLLECTED_BEFORE`, `COLLECTED_UPPER` and `test_collected_count_unchanged_by_the_retag`. The "retag added or removed no test" claim is already carried by the per-row existence check: a removed pinned test fails its row. An unpinned test added or removed is not this guard's business (the origin checks of `IP-1330` require each new test to name its origin).
2. **Pinned tag sets unchanged.** `EXPECTED` keeps every row exactly. No row is added, removed or edited in this package.
3. **Skip only when the module is outside this run, fail when it is gone.** Today a row whose module has no collected record is skipped, which hides a deleted or renamed module as well as a `-m`-deselected one. New rule per row: if the module file is absent from `spacesim/tests/` on disk, the row fails ("module removed or renamed"); if the file exists but was not collected in this run (deselected by `-m`, or a partial path run), the row is not applicable and is reported as such; if collected, the function must exist with exactly the pinned tag set. Together the `-m browser` run checks the browser module's row and the `-m "not browser"` run checks the rest, and the unfiltered run checks all.
4. **No check may skip in both filtered runs.** After the redesign the guard has no `pytest.skip` that is true in both `-m browser` and `-m "not browser"`. A row that is not applicable to a run must not appear as a skip; it is parametrized only over rows applicable to the run, or the per-row check passes vacuously with a stated reason, whichever the builder finds cleaner. A test that proves it (Tests to Add 5) counts the skips of the guard module under each of the three invocations.
5. **`test_no_retagged_test_lost_its_last_id_or_declares_an_unresolvable_one` is kept** (it already skips nothing: rows with no record are passed over in the loop). Its pass-over now defers to Decision 3 for rows whose module is gone.
6. **Documentation scope.** Living docs that describe the ceiling are corrected (Documentation Updates). Verification Reports are frozen records and are not edited; package bodies of `VERIFIED` packages (`IP-1334`, `IP-1076`, `IP-1077`) describe what was true when planned and are not edited either.

## Files to Create

None.

## Files to Modify

- `spacesim/tests/test_origin_retag.py` — remove the count constants and the count test; split the row logic into the pure helper (Interfaces); add the new tests; rewrite the module docstring (drop "count unchanged"; state the new purpose). `EXPECTED` untouched.
- `spacesim/tests/baseline_ids.py` — only if the builder places the pure helper there instead of in the guard module.
- `docs/implementation/` files named under Documentation Updates.

## Implementation Tasks

1. Test-first: write the new tests (Tests to Add 1-6) against the not-yet-written helper; confirm they fail for the right reason (helper missing / count test still present).
2. Read `conftest.py` and confirm what `config._verifies_records` contains under `-m browser` and `-m "not browser"` (whether deselected items are present). Record the answer in the completion note; if deselected items are present the "applicable" set must be derived from the selected items, not from records alone.
3. Add the pure helper and make the live tests call it; delete the count constants and test.
4. Run the guard three ways: unfiltered, `-m "not browser"`, `-m browser`; record passed/skipped counts for each (Tests to Add 5 asserts this in-suite).
5. Run the mutation procedure (Verification Checklist) by hand once and record it; the in-suite tests of Tests to Add 2-4 pin it permanently.
6. Update documentation; run `test_doc_integrity.py`, `test_test_origins.py`, the full suite, `test_determinism.py`, `test_import_guard.py`; regenerate the RTM Test column (`python3 -m pytest --origin-report=rtm`) in the same commit (`NFR-2850`).

## Tests to Add

Each in `test_origin_retag.py`, marked `@pytest.mark.verifies("FS-133")` (or `IP-1079` where it tests the package's own Definition of Done):

1. **Live rows still pass.** Every `EXPECTED` row applicable to the run passes (the existing parametrized test, kept). Origin `NFR-2820` (module mark).
2. **Mutation: a deleted pinned test fails.** Take the live records, remove the record for one pinned `(module, function)`, run the pure helper: exactly one problem, naming that row and "no longer exists". Origin `FS-133`.
3. **Mutation: a retagged pinned test fails.** Replace one record's tag set (add a tag, drop a tag, empty set) and expect one problem each, naming expected and actual sets. Origin `FS-133`.
4. **Mutation: a removed module fails, a deselected module does not.** With the module file absent from the on-disk set and no record: one "module removed or renamed" problem. With the file present but no record (not collected): zero problems and the row reported not applicable. Origin `FS-133`.
5. **No double skip.** Run the guard module in a child pytest process three ways (unfiltered, `-m browser`, `-m "not browser"`) via `pytester`-style subprocess invocation (the builder uses whichever invocation the suite already uses for such tests, or the `subprocess` module with the test file path only, never the whole suite) and assert: no check is skipped in both filtered runs, and the unfiltered run skips none. Origin `IP-1079`. If a subprocess nest is judged too slow (the guard module alone is fast; the whole suite is not), the builder asserts the same property statically instead (no `pytest.skip` call remains reachable under both filters) and records why.
6. **Growth does not fail.** A synthetic record list with one more unpinned test than the live list passes the helper. Origin `IP-1079`.

Test count: about 6 added, 1 removed; the suite moves from 1671 to about 1676.

## Documentation Updates

- `spacesim/tests/test_origin_retag.py` docstring (above).
- `docs/implementation/00-master-build-plan.md`: the `IP-1079` row and tally line (pass 5 note, written in this planning pass).
- `docs/implementation/packages/INDEX.md`: the `IP-1079` row.
- `docs/implementation/01-technical-work-breakdown.md`: pass 5 section (written in this planning pass); the pass 4 "Not planned" `L-5` bullet gets a one-line forward pointer to `IP-1079` when the package is built.
- Grep the living docs for the phrases `COLLECTED_UPPER`, `1,700`, `1700`, "count-pinned" and "collected count" outside `verification/`, `docs/reviews/` and the bodies of `VERIFIED` packages; edit only a living statement that would be false after the change. The `IP-1076`/`IP-1077` checklist lines that cite the ceiling are historical and stay.
- Not edited: any `VR-xxxx`, any review report, `docs/pipeline/`.

## Definition of Done

- The count constants and the count test are gone; `EXPECTED` is byte-identical to before.
- A mutation that deletes, renames or retags any one pinned test fails the guard; a module-level deletion fails; adding any number of unpinned tests passes.
- No check in the guard skips under both `-m browser` and `-m "not browser"`; the unfiltered run skips none from this module.
- Full suite green; permanent gates unaffected; RTM Test column regenerated in the same commit; no allow-list grew.

## Verification Checklist

- [ ] `git diff` shows `EXPECTED` unchanged and the three count symbols removed.
- [ ] The verifier re-runs the mutation by hand: delete one pinned test from a copy of the tree (or rename it) and see the guard fail; restore and see it pass.
- [ ] The verifier runs the guard under the three invocations and reads the skip counts.
- [ ] Add five throwaway unpinned tests: guard still green (growth).
- [ ] `test_doc_integrity.py`, `test_test_origins.py`, full suite, `test_determinism.py`, `test_import_guard.py` green; `-m browser` run green or skipped loudly where Chromium is absent.
- [ ] Docs edits limited to living statements; no VR edited.

## Dependencies

All `VERIFIED`: `IP-1334`, `IP-1330`, `IP-1340`. No dependents. Build before `IP-1081` (which adds tests) only to keep the ceiling out of its way; it is not a hard dependency (1671 plus `IP-1081`'s tests is below 1700).

## Risks

- **`conftest.py` may not record deselected items**, in which case "applicable to this run" cannot be read from the records alone (task 2 settles it; if needed the helper takes the selected node IDs from the session instead).
- **Subprocess nesting in a test** can be slow or flaky; the fallback is the static assertion (Tests to Add 5).
- **Weakened guard?** The only protection removed is a ceiling on growth; the floor ("no test lost") is carried by the per-row checks for every pinned test and by the origin checks for every other. An unpinned existing test that is deleted is outside the retag's purpose and is visible in review diffs.
- A mistaken edit to `EXPECTED` would change what is pinned: the first checklist item compares it byte for byte.

## Rollback Considerations

Revert the commit. Test-only; restores the count bounds and the old skip behaviour.
