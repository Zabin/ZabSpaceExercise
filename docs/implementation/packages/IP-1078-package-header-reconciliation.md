# IP-1078 — Package Header Reconciliation: Fourteen Headers and Three Ledger Notes That Contradict Their VERIFIED Rows (docs only)

> **Package ID:** IP-1078
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1078](../verification/VR-1078-package-header-reconciliation.md), fresh session; COMPLETE before that) — authored 2026-10-24 by `07-implementation-planning`.
> **Earlier status record (superseded by the line above; retained as history, unedited):** COMPLETE — implemented 2026-10-24 by `08-code-implementation` (awaiting `09-package-verification`); authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 4). No code dependency; every package it edits is already `VERIFIED` on the ledger.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (bugs, in-progress and critical items only), covers a documentation defect that makes the tree contradict itself (`M-3` of the tranche 3 integration review, Medium). Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** none on code. Reads the `VR-xxxx` reports of the packages named below.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 4"), [the tranche 3 integration review](../../reviews/integration-review-tranche-3-release-push-remediation.md) (`M-3`)
> **Produces:** package headers and Master Build Plan notes that agree with the ledger, with a recorded sweep that no other package header disagrees.
> **Feature Reference:** none (documentation hygiene across packages of `FS-106`, `FS-110`, `FS-131`, `FS-133` and `FS-134`).
> **Related Topics:** [`00-master-build-plan.md`](../00-master-build-plan.md), [`INDEX.md`](INDEX.md), [`../verification/INDEX.md`](../verification/INDEX.md)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Documentation-only remediation package. No file under `spacesim/` changes. Prose only.*

---

## Package ID

IP-1078.

## Title

Reconcile stale package headers and ledger notes with the `VERIFIED` status the ledger and the verification reports record.

## Objective

**Defect (review `M-3`).** Fourteen of the nineteen packages touched in tranches 2 and 3 carry a header `Status` line that contradicts their `VERIFIED` ledger row, and three Master Build Plan rows keep an "awaiting `09`" sentence beside a `VERIFIED` cell. `IP-1350`'s ledger check reads the Master Build Plan, `packages/INDEX.md`, `ROADMAP.md` and the feature index, not the package files' own header, so the suite stays green.

Read at the tip of `claude/plan-remediation-4` (all `VERIFIED` on the Master Build Plan; each has a `VR-xxxx` report in `docs/implementation/verification/`):

| Package | Header `Status` today | Header should read |
|---|---|---|
| `IP-1311` | `COMPLETE ... (awaiting 09)` | `VERIFIED` with `VR-1311` |
| `IP-1102` | `COMPLETE ... (awaiting 09 ...)` | `VERIFIED` with `VR-1102` |
| `IP-1075` | `READY` | `VERIFIED` with `VR-1075` |
| `IP-1334` | `COMPLETE ... (awaiting 09)` | `VERIFIED` with `VR-1334` |
| `IP-1068` | `READY` | `VERIFIED` with `VR-1068` |
| `IP-1101` | `READY` | `VERIFIED` with `VR-1101` |
| `IP-1091` | `READY` | `VERIFIED` with `VR-1091` |
| `IP-1069` | `READY` | `VERIFIED` with `VR-1069` |
| `IP-1330` | `READY` | `VERIFIED` with `VR-1330` |
| `IP-1350` | `READY` | `VERIFIED` with `VR-1350` |
| `IP-1340` | `READY` | `VERIFIED` with `VR-1340` |
| `IP-1331` | `BLOCKED` (on `IP-1330`) | `VERIFIED` with `VR-1331` |
| `IP-1332` | `BLOCKED` (on `IP-1330`) | `VERIFIED` with `VR-1332` |
| `IP-1333` | `BLOCKED` (on `IP-1330`) | `VERIFIED` with `VR-1333` |

Ledger notes: the `IP-1311` and `IP-1334` rows in `00-master-build-plan.md` still say "awaiting `09`" and the `IP-1074` row says "pending `09`" inside a note that is next to a `VERIFIED` cell. The three `BLOCKED` backfill headers (`IP-1331`-`IP-1333`) and any `READY` tranche-2 header also state "Authorization: **not yet given**", while the ledger records the owner's go-ahead (journal run #230 for the nine tranche-2 packages; run #256 for the release-push ones); the authorization line is part of the same stale block and is reconciled with it.

## Requirements Covered

| ID | How |
|---|---|
| `NFR-3800`, `NFR-3820`, `NFR-3830` | The documentation-integrity family (`IP-1350`): the tree's ledgers agree. This package removes the disagreement the check cannot see; no requirement text changes. |
| `NFR-2850` | Not touched: no test is added or retagged, so no RTM regeneration is needed. If the optional check in Design Decision 3 is adopted by a later package, its origin is chosen there. |

(No functional requirement is involved; this is a record-keeping defect. The package ID is its own test origin.)

## Architecture Components

None in `spacesim/`. Documents only: the 14 package files, `docs/implementation/00-master-build-plan.md` (three row notes), `docs/implementation/packages/INDEX.md` (only if a row disagrees; the builder checks). No load-bearing code invariant is touched.

## Interfaces

None. The reconciled header format is the one the `VERIFIED` packages already use, for example `IP-1074`: `VERIFIED 2026-10-24 ([VR-1074](../verification/VR-1074-white-control-correctness.md), fresh session; COMPLETE before that) — authored <date> by 07-implementation-planning (<run or pass>).`

### Design Decisions

1. **A tiny package of its own, not part of `IP-1076`.** Reasons: (a) `07-implementation-planning` is forbidden to write `VERIFIED` (its skill: it writes only `NOT STARTED`, `READY`, `BLOCKED`), so the planner cannot make these edits in the planning pass, and they are not a small side effect of a code package; (b) `IP-1076` is a code-and-browser package with a heavy verification checklist, and fourteen unrelated file edits would bury its diff and make `09` re-verify documents unrelated to the clock; (c) the edit is mechanical and independent of every other package, so it can be built and verified in the same session as, or before, either code package; (d) keeping it separate keeps `IP-1076`'s `git diff` limited to files its checklist names. Folding it into `IP-1076` would save one row of ledger work and cost clarity.
2. **Ledger wins on disagreement.** The pipeline's rule (journal reconciliation) is that the tree's ledgers win; the Master Build Plan row, `packages/INDEX.md` row, `ROADMAP.md` and the `VR-xxxx` report are the evidence. For each package the build reads the Master Build Plan row (status and VR link), the `INDEX.md` row, and the `VR-xxxx` report's own verdict line, and writes the header from them. If any of the three disagrees with another, the build stops on that package and records it in the completion note (a real ledger defect, routed to the pipeline), and does not guess.
3. **A guard is recommended, not built here.** The root cause is that no check compares a package file's header with its ledger row. A new test is a new capability beyond the bug-only brief and belongs to `IP-1350`'s family (`00-intake` to file it). This package therefore ends with a one-off sweep (task 4) whose result is recorded; it adds no test and changes no allow-list.
4. **Scope is headers, authorization lines in the same stale block, and the three notes.** Package bodies (Tasks, Tests, Definition of Done) are historical records of what was planned and are not edited. No package's `Version` changes. No status other than the header's, the authorization line where it contradicts the ledger, and the three "awaiting 09" sentences is touched.
5. **Not in scope (explicit).** The remaining tranche-2 documentation findings `F-06`-`F-11` / review `M-5` (`CLAUDE.md` status text, GDS-07/08/09/10 statements, `feature-index.md` `FS-106`/`FS-110` rows and the two `doc_integrity_allow_ledgers.txt` lines, the Master Build Plan tally text beyond these three notes) belong to `03`, `04`, `06`, `11` and the `CLAUDE.md` sweep; `M-1` (training curl examples) belongs to `08-training-manual-authoring`. They are named in the TWBS "not planned" list.

## Files to Create

None.

## Files to Modify

- The 14 files named in the Objective table, under `docs/implementation/packages/`: `IP-1311-vignette-id-scan-robustness.md`, `IP-1102-save-load-robustness.md`, `IP-1075-undo-clock-floor.md`, `IP-1334-test-origin-retag.md`, `IP-1068-white-only-controls-server-enforcement.md`, `IP-1101-self-contained-saves.md`, `IP-1091-clock-lag-watchdog-test.md`, `IP-1069-white-only-panels-registered.md`, `IP-1330-test-origin-marker-and-checks.md`, `IP-1350-documentation-integrity-checks.md`, `IP-1340-browser-console-rule-suite.md`, `IP-1331-test-origin-backfill-engine-content.md`, `IP-1332-test-origin-backfill-session.md`, `IP-1333-test-origin-backfill-web.md`. The header `Status` line (and its continuation lines) and, where it contradicts the ledger, the `Authorization` line.
- `docs/implementation/00-master-build-plan.md`: the notes in the `IP-1311`, `IP-1074` and `IP-1334` rows (the "awaiting `09`" / "pending `09`" sentences become a plain past-tense record of the verification, keeping the VR link already in the row). The `Status` cell is not changed (it already reads `VERIFIED`).
- `docs/implementation/packages/INDEX.md`: only a row the sweep finds in disagreement.
- `docs/implementation/packages/IP-1078-package-header-reconciliation.md` (this file): the header on completion.

## Implementation Tasks

1. For each of the 14 packages, collect the Master Build Plan row's status and VR link, the `INDEX.md` row, and the `VR-xxxx` verdict and date (Decision 2). Stop on any disagreement.
2. Rewrite each header `Status` line in the established `VERIFIED` form (VR link, "fresh session", the prior status in parentheses, original authoring attribution kept). Reconcile the `Authorization` line where it says "not yet given" and the ledger records the go-ahead (cite the journal run the ledger row names).
3. Edit the three Master Build Plan notes (Files to Modify).
4. One-off sweep (recorded, not committed as a test): list every `packages/IP-*.md` header status and compare with its Master Build Plan row's status cell; record the count compared, the disagreements fixed here, and any further disagreements found. A further disagreement outside the 14 is fixed in the same way if mechanical and the evidence is unambiguous; otherwise it is listed in the completion note for the pipeline.
5. Run `test_doc_integrity.py` and `test_test_origins.py` (and the full suite once, since a header edit can break a link or an index check); fix any link the edits break.
6. Update the Master Build Plan row for `IP-1078` to `COMPLETE` (never `VERIFIED`) and the documentation below.

## Tests to Add

None (documentation-only, by design; Decision 3). Evidence is the sweep in task 4 and the existing documentation checks:

- `test_doc_integrity.py` stays green (links, indexes, ledger agreement: `NFR-3800`/`NFR-3820`/`NFR-3830`).
- `test_test_origins.py` stays green (no test changed).
- The sweep result states the number of headers compared and zero residual disagreements, or lists them.

## Documentation Updates

- `docs/implementation/00-master-build-plan.md`: the `IP-1078` row and tally line (see the pass 4 note), and the three row notes above.
- `docs/implementation/packages/INDEX.md`: the `IP-1078` row.
- `ROADMAP.md`: implementation-theme counters if it carries them (the builder checks; flipping them is `08`'s documented step).
- Nothing in `docs/requirements/`, `docs/architecture/`, `docs/training/` or `docs/pipeline/` is written.

## Definition of Done

- All 14 headers read `VERIFIED` with the VR link the ledger names, and no header's authorization line contradicts the ledger.
- The three Master Build Plan notes no longer say "awaiting 09" / "pending 09" next to a `VERIFIED` cell.
- The recorded sweep shows no package header disagreeing with its ledger row, or lists the exceptions for the pipeline.
- `test_doc_integrity.py` and `test_test_origins.py` green; the full suite green; no allow-list grew.
- No file under `spacesim/` changed (`git diff --stat` shows `docs/` only).
- The `IP-1078` row is `COMPLETE` (not `VERIFIED`).

## Verification Checklist

- [ ] `git diff --stat` against the parent shows only the files named under Files to Modify.
- [ ] Each of the 14 headers matches its Master Build Plan row, its `INDEX.md` row and its `VR-xxxx` verdict (three-way check by the verifier, re-derived, not copied from the completion note).
- [ ] No package body outside the header block changed (diff is limited to header lines).
- [ ] The three Master Build Plan notes are corrected and their VR links resolve.
- [ ] The sweep is recorded with its count; any listed exception is real.
- [ ] `test_doc_integrity.py`, `test_test_origins.py` and the full suite green; `test_determinism.py` and `test_import_guard.py` unaffected.
- [ ] No status was written that the ledger does not already record (the builder advanced no package it did not verify).

## Dependencies

None on code. Independent of `IP-1076` and `IP-1077`; may be built first, last or in parallel. If built in the same branch as the code packages, edit this package's rows last to avoid conflicts in the Master Build Plan.

## Risks

- **A header edit breaks a relative link** (a `VR` path typed wrongly): `test_doc_integrity.py` catches it.
- **A real ledger disagreement is found** (for example an `INDEX.md` row that says otherwise): the build stops on that package and routes it; this is a feature of Decision 2, not a failure.
- **Reconciling an authorization line is a judgement about the journal**: the builder cites only what the Master Build Plan row already states; it does not read `docs/pipeline/` for new facts and does not write there.
- **Recurrence**: without the check recommended in Decision 3 the next tranche reproduces the defect. Filed as a recommendation, not built.

## Rollback Considerations

Revert the commit. Documents only; nothing depends on the header text except human readers and the pipeline's reconciliation reads, which already prefer the ledger.
