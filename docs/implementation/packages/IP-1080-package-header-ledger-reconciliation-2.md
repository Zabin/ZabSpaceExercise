# IP-1080 — Package Header and Ledger Reconciliation, Second Pass: 31 Older Headers, Three "Not Yet Authorized" Rows, Nine "Awaiting 09" Sentences, and IP-1078's Own Header (docs only)

> **Package ID:** IP-1080
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1080](../verification/VR-1080-package-header-ledger-reconciliation-2.md)); COMPLETE earlier the same day — implemented by `08-code-implementation`; authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 5). No code dependency; every package it edits is already `VERIFIED` on the ledger.
> **Sweep result (2026-10-24, scripted over every package file against the Master Build Plan row, the `packages/INDEX.md` row and the `ROADMAP.md` row):** 83 package ids compared (83 package files). Before: 34 ids disagreed (the 31 named in the Objective, `IP-1078`, and, because `IP-1079` and `IP-1081` reached `VERIFIED` after this package was written, their two headers; `IP-1062`, `IP-1174`, `IP-1210` also carried a stale `IN PROGRESS: RETURNED` cell in `ROADMAP.md`). After: 0 disagreements. Master Build Plan notes: 3 "Not yet authorized" sentences (`IP-1068`, `IP-1101`, `IP-1340`) and 17 "Awaiting `09`" sentences beside `VERIFIED` cells rewritten; the two rows that quote the phrase to describe this sweep (`IP-1078`, `IP-1080`) and dated Package Status log lines are history and untouched. Residual exception: none. `IP-1160` is `BLOCKED` on every ledger and was correctly left alone.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, plus the owner's instruction in this session to fix stale docs before the release. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** none on code. Reads [VR-1078](../verification/VR-1078-package-header-reconciliation.md) (F1, F2, F3) and the `VR-xxxx` report of each package named below.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 5"), [VR-1078](../verification/VR-1078-package-header-reconciliation.md)
> **Produces:** package headers and Master Build Plan rows whose status and authorization statements agree with the ledger and the verification reports, with the sweep recorded in the tree.
> **Feature Reference:** none (documentation hygiene across packages of many features).
> **Related Topics:** [`00-master-build-plan.md`](../00-master-build-plan.md), [`INDEX.md`](INDEX.md), [`../verification/INDEX.md`](../verification/INDEX.md), [IP-1078](IP-1078-package-header-reconciliation.md)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Documentation-only remediation package. No file under `spacesim/` changes. Prose only.*

---

## Package ID

IP-1080.

## Title

Finish the header-versus-ledger reconciliation that `IP-1078` started, using the same rules.

## Objective

`IP-1078` fixed 14 headers (plus `IP-1076` and `IP-1077`). Its verification (`VR-1078`) found what remained, and the owner wants stale documents fixed before the release:

- **F1.** 31 older package headers still disagree with their `VERIFIED` ledger rows. At the tip of `claude/plan-remediation-5` the header `Status` lines read (leading badge; the builder re-derives the list by script):
  - `READY`: `IP-1021`, `1064`, `1065`, `1131`, `1211`, `1220`, `1223`, `1240`, `1250`, `1270`, `1280`, `1290`, `1300`
  - `COMPLETE`: `IP-1061`, `1062`, `1066`, `1067`, `1150`, `1170`, `1172`, `1173`, `1174`, `1180`, `1190`, `1200`, `1210`, `1230`, `1261`, `1310`, `1320`
  - `BLOCKED`: `IP-1260`
- **F2.** Three Master Build Plan rows (`IP-1068`, `IP-1101`, `IP-1340`) say "Not yet authorized" beside a `VERIFIED` cell, though the run #230 go-ahead is on record; and nine rows keep a historical "Awaiting 09" sentence beside `VERIFIED` (the rows for `IP-1180`, `1190`, `1200`, `1220`, `1240`, `1250`, `1270`, `1280`, `1290`; the same wording also sits in the `IP-1064`, `1065`, `1131`, `1223` rows, and the builder includes any row where a `VERIFIED` cell sits beside such a sentence).
- **F3.** `IP-1078`'s own header reads `COMPLETE`; its ledger row and `VR-1078` say `VERIFIED`.

Total header edits: 31 + `IP-1078` = 32 package files, plus up to about 16 Master Build Plan row notes.

## Requirements Covered

| ID | How |
|---|---|
| `NFR-3800`, `NFR-3820`, `NFR-3830` | The documentation-integrity family (`IP-1350`): the tree's ledgers agree. This package removes a disagreement the check cannot see; no requirement text changes. |

(Record-keeping defect; the package ID is its own origin; no test is added.)

## Architecture Components

None in `spacesim/`. Documents only: the 32 package files, `docs/implementation/00-master-build-plan.md` (row notes), `docs/implementation/packages/INDEX.md` (only a row the sweep finds in disagreement). No load-bearing invariant touched.

## Interfaces

None. The target header form is the one `IP-1078` used and the `VERIFIED` packages already carry: `VERIFIED <date> ([VR-nnnn](../verification/VR-nnnn-<slug>.md), fresh session; <prior status> before that) — authored <date> by 07-implementation-planning (<run or pass>).`

### Design Decisions

1. **Same rules as `IP-1078`.** Status and authorization lines only; substance unchanged; the ledger wins on disagreement (Master Build Plan row, `INDEX.md` row, `VR-xxxx` verdict: all three must agree or the build stops on that package and routes it); package bodies and `Version` untouched; every VR link must exist on disk (`test_doc_integrity.py` checks links).
2. **Packages with more than one verification report** (a returned report later superseded, as `IP-1064` and `IP-1069` had) cite the report the ledger row cites, and name the earlier return in parentheses only if the header already did.
3. **Authorization lines.** Where a header says "not yet given" and the ledger records the go-ahead, rewrite to "given" and cite only the run or date the Master Build Plan row already states (run #230 for the nine tranche-2 packages; the 2026-09-27 and 2026-07-05 owner instructions for the Should-tier and tranche 3 ones). The builder does not read `docs/pipeline/` for new facts and does not write there.
4. **The three "Not yet authorized" rows and the nine "Awaiting 09" sentences** become plain past-tense records ("verified by `09`, VR-nnnn" where the link is already in the row; otherwise the sentence is removed). The `Status` cell is not changed (already `VERIFIED`).
5. **`IP-1078`'s header** is rewritten to `VERIFIED` with `VR-1078`; its body (including the "Awaiting 09"-style task 6 wording) is historical and untouched.
6. **The sweep is recorded in the tree**, not only in chat (the `VR-1078` F1/F3 lesson): the completion note is also written into this package's header block as a dated "Sweep result" line stating the count compared, the disagreements fixed, and any residual exception. The guard that would stop recurrence (header versus ledger) remains a recommendation to `00-intake` (`IP-1078` Decision 3); no test is added here.
7. **This package does not edit its own sibling headers** (`IP-1079`, `IP-1081`): their statuses move with their own builds.

## Files to Create

None.

## Files to Modify

- The 32 package files under `docs/implementation/packages/`: header `Status` (and continuation lines) and, where it contradicts the ledger, the `Authorization` line. The 31 are `IP-1021`, `1061`, `1062`, `1064`, `1065`, `1066`, `1067`, `1131`, `1150`, `1170`, `1172`, `1173`, `1174`, `1180`, `1190`, `1200`, `1210`, `1211`, `1220`, `1223`, `1230`, `1240`, `1250`, `1260`, `1261`, `1270`, `1280`, `1290`, `1300`, `1310`, `1320`; plus `IP-1078`.
- `docs/implementation/00-master-build-plan.md`: the `IP-1068`, `IP-1101`, `IP-1340` row notes ("Not yet authorized" sentence), and the "Awaiting 09" sentences in the rows named in Objective F2. Status cells unchanged.
- `docs/implementation/packages/INDEX.md`: only a row the sweep finds in disagreement.
- This file: the header on completion (status and sweep line).

## Implementation Tasks

1. Script the sweep first: for every `packages/IP-*.md`, read the header status badge, the Master Build Plan row's status cell and the `INDEX.md` row; list disagreements. Expect the 32 above; record the exact count compared (every package file on the ledger at build time).
2. For each disagreeing package, read its `VR-xxxx` verdict line and date; stop on any three-way disagreement and route it.
3. Rewrite headers (Decisions 1-3, 5); reconcile authorization lines where contradictory.
4. Edit the Master Build Plan row notes (Decision 4).
5. Re-run the sweep; require zero residual disagreements, or list exceptions in the header's sweep line.
6. Run `test_doc_integrity.py` and `test_test_origins.py`, then the full suite once (a header edit can break a link or an index check); fix any link broken.
7. Set the `IP-1080` ledger row to `COMPLETE` (never `VERIFIED`).

## Tests to Add

None (documentation only; `IP-1078` Decision 3). Evidence is the recorded sweep and the existing checks: `test_doc_integrity.py` and `test_test_origins.py` green; the sweep states the number compared and zero residual disagreements. No test changes, so no RTM regeneration.

## Documentation Updates

- Master Build Plan: the `IP-1080` row and tally line (pass 5 note, written in this planning pass), and the row notes above.
- `packages/INDEX.md`: the `IP-1080` row.
- `ROADMAP.md`: implementation counters if present (the builder checks; `08`'s documented step).
- Nothing in `docs/requirements/`, `docs/architecture/`, `docs/training/`, `docs/pipeline/` or `verification/` is written (VR notes are frozen).

## Definition of Done

- All 32 headers read `VERIFIED` with the VR link the ledger names; no header's authorization line contradicts the ledger.
- The 12 to 16 Master Build Plan notes no longer show "Not yet authorized" or "Awaiting 09" beside a `VERIFIED` cell.
- The recorded sweep (in the tree) shows zero residual disagreements or lists real exceptions.
- `test_doc_integrity.py`, `test_test_origins.py` and the full suite green; no allow-list grew; nothing under `spacesim/` changed.
- The `IP-1080` row is `COMPLETE`, not `VERIFIED`.

## Verification Checklist

- [ ] `git diff --stat` shows only the files named under Files to Modify; no `spacesim/`, no `verification/`, no `docs/pipeline/`.
- [ ] The verifier re-derives the header-versus-ledger comparison by script (not from the completion note) for every package: zero disagreements.
- [ ] Diff hunks in each package file lie in the header block (status and authorization lines) only.
- [ ] Each rewritten VR link resolves; each VR's verdict reads `VERIFIED`.
- [ ] Authorization lines cite only facts already in the ledger rows.
- [ ] The tree contains the sweep line with its count.
- [ ] `test_doc_integrity.py`, `test_test_origins.py`, full suite, `test_determinism.py`, `test_import_guard.py` green.

## Dependencies

None on code. Independent of `IP-1079` and `IP-1081`. Build it last in the pass (Ordering): the Master Build Plan notes it edits sit near the status rows the two code-and-test packages update.

## Risks

- A header edit breaks a relative link: `test_doc_integrity.py` catches it.
- A real ledger disagreement is found: the build stops on that package and routes it (Decision 1); that is the design, not a failure.
- Recurrence: without the header-versus-ledger check the next tranche reproduces the defect; recommended to `00-intake`, not built.
- The count of "nine" "Awaiting 09" rows is the verifier's; the build re-derives it (about 13 by a text search at planning time).

## Rollback Considerations

Revert the commit. Documents only; nothing depends on header text except readers and the pipeline's reconciliation reads, which already prefer the ledger.
