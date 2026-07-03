---
name: 09-package-verification
description: Independently verify exactly one COMPLETE Implementation Package against the shipped code — re-check every Definition of Done and Verification Checklist item against the actual source tree, run the full test suite plus the permanent gates, audit the traceability updates the implementation claimed, produce a Verification Report (VR-xxxx) under docs/implementation/verification/, and advance the package COMPLETE→VERIFIED (or send it back with findings). This is the ONLY skill authorized to write VERIFIED on the Master Build Plan. Use when asked to "verify IP-xxxx," "check the last implemented package," "advance a COMPLETE package to VERIFIED," or after any 08-code-implementation run finishes. It verifies against what the package and its Feature Specification already say — it never fixes code (that goes back to 08-code-implementation), never edits the package or spec, and never verifies its own same-session implementation work. Do not use it to implement packages (08-code-implementation) or to review a whole release's packages together (10-integration-review).
---

# Package Verification

Independently confirms that **one Implementation Package marked `COMPLETE`** actually delivers what
it claims, then — and only then — advances it to `VERIFIED`. This skill sits strictly downstream of
`08-code-implementation` and is the sole authority for the `COMPLETE → VERIFIED` transition. Its
value is independence: it re-derives every claim from the tree and the test run, taking nothing in
the Implementation Summary on faith.

## What this is for (and what it is not)

This skill answers one question: *does the shipped code, as it exists in the tree right now,
satisfy every item of this package's Definition of Done and Verification Checklist, every
requirement in its `Requirements Covered`, and the repository's permanent invariants — yes or no,
with evidence?*

It SHALL NOT:

- **Fix anything.** A failed check is a finding routed back to `08-code-implementation` (or
  upstream, if the defect is in the package/spec itself) — never a same-session patch. A verifier
  that edits code stops being independent.
- **Edit the package, the Feature Specification, requirements, or architecture.** All read-only.
  A package whose checklist turns out to be unverifiable as written is a finding for
  `07-implementation-planning`, not something to reinterpret leniently.
- **Verify work implemented in the same session.** If this conversation just ran
  `08-code-implementation` on the package, state that independence is degraded and recommend the
  verification run in a fresh session; proceed only if the user accepts that caveat explicitly.
- **Verify more than one package per invocation.** One package, one report, one status transition.
- **Rubber-stamp.** `VERIFIED` with any checklist item unchecked, any test failing, or any
  traceability cell still stale is a corrupted ledger — the whole pipeline downstream trusts this
  status.

## Inputs (all read-only)

The target package (`docs/implementation/packages/IP-xxxx-*.md`), its Feature Specification,
its `Requirements Covered` FR/NFRs and the Requirements Traceability Matrix
(`docs/requirements/03-requirements-traceability-matrix.md`), the Master Build Plan
(read + status-write), the architecture/ICD/ADRs it cites, and the live source tree + test suite.

## Outputs

1. **`docs/implementation/verification/VR-xxxx-<slug>.md`** — the Verification Report, numbered to
   match the package (IP-1050 → VR-1050). Create the directory and an `INDEX.md` (one row per
   report: VR ID, package, date, result, headline findings) on first use. Report structure:

   | Section | Content |
   |---|---|
   | **Package** | ID, title, version verified, commit hash of the tree state verified |
   | **Result** | `VERIFIED` / `RETURNED` (with the count of failed checks) |
   | **Definition of Done audit** | One row per DoD item: item · evidence (file:line, test name, command output) · pass/fail |
   | **Verification Checklist audit** | Same, for every checklist item |
   | **Requirements audit** | One row per `Requirements Covered` ID: where implemented · where tested · RTM cell state · pass/fail |
   | **Test run** | Full-suite counts (pass/fail/skip) + the permanent gates by name, with the exact commands run |
   | **Scope audit** | Whether the implementing diff stayed inside `Files to Create`/`Files to Modify` (+ implied tests/docs) — name any file touched outside scope |
   | **Findings** | One row per failure/concern: description · severity · recommended owner (`08-code-implementation` re-run, `07-implementation-planning` package repair, upstream) |

2. **Updated Master Build Plan + `packages/INDEX.md`**: on pass, the package's status flips to
   `VERIFIED`, and any downstream package `BLOCKED` solely on this one reaching `VERIFIED` gets
   its blocking note updated (and flips to `READY` only if *all* its dependencies are now
   `VERIFIED` and it is fully specified). On fail, the package flips back to `IN PROGRESS` (or
   `BLOCKED`, if the defect is upstream) with a one-line pointer to the report.

3. **Updated Requirements Traceability Matrix** — only to *correct* trace cells the audit proved
   wrong or confirm ones the implementation filled; never to paper over a gap the code doesn't
   actually close.

## Workflow

1. **Select and gate.** The target package must be exactly `COMPLETE`. Anything else — including
   "it's basically done" — is ineligible; report the actual status and stop.
2. **Read the package in full**, plus its FS, requirements, and cited architecture/ADR sections.
   Build the checklist inventory: every DoD item, every Verification Checklist item, every
   `Requirements Covered` ID, every named file.
3. **Audit the tree.** For every claimed file/change: confirm it exists and does what the package
   says, by reading the code — not by trusting the Implementation Summary. Diff-scope check: the
   implementing change stayed inside the package's declared file set.
4. **Run the tests.** Full suite (`python3 -m pytest`) plus the permanent gates by name
   (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`). Record exact
   counts. Any failure — even one that looks pre-existing — is investigated far enough to assign
   ownership: this package's defect (fail the verification) or pre-existing (finding with
   evidence, e.g. the failure reproduces on the pre-package commit).
5. **Audit traceability.** Every `Requirements Covered` ID must trace in the RTM to real files and
   real tests this package shipped — no placeholder, no stale cell.
6. **Write the Verification Report**, update the ledger(s) per Outputs, and commit as
   `docs(verification): VR-xxxx — <result>`.

## Quality gate (before writing `VERIFIED`)

- [ ] Every DoD and Verification Checklist item has recorded evidence — none waved through.
- [ ] Full suite green; both permanent gates green, run by name.
- [ ] Every covered requirement traces to real code and a real test in the RTM.
- [ ] The implementing change stayed in scope, or every excursion is explained and accepted.
- [ ] The report's Result matches the ledger status written — never `VERIFIED` in one place and
      hedged in the other.
- [ ] No code, package, spec, or requirement was edited by this run.

## Gotchas

- **As-built packages** (the IP-1010…IP-1110 record of already-shipped capabilities) are verified
  the same way — against the current tree, not against the historical claim. If the tree has
  drifted since the as-built record was written, that drift is a finding.
- A `RETURNED` result is a *normal* outcome, not a failure of the pipeline — cheap detection here
  is the point. Route the finding, don't soften the result to avoid the round-trip.
- Severity honesty: a cosmetic doc-path typo in the package is a Low finding that can pass with a
  note; an unchecked DoD item is a hard fail. Don't let smallness of the fix tempt you into making
  it — even a one-line fix belongs to `08-code-implementation`.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 09 — Package Verification** of the documentation-driven-development pipeline
(see [`.claude/skills/README.md`](../README.md); stages run in numeric order, and
`00-pipeline-status` reports where the project currently stands). Upstream:
`08-code-implementation`. Downstream: `10-integration-review` (once a release/epic's packages are
all `VERIFIED`), or back to `08-code-implementation` for the next package.

End **every** invocation — pass, return, or blocked stop — with a chat summary containing exactly
these three parts:

1. **What changed** — the Verification Report written (path + Result), status transitions applied
   to the Master Build Plan / package index, RTM cells corrected.
2. **Recommendations** — every finding with its severity and owner; independence caveats if any.
3. **Next step** — say explicitly what to run next and why: on `RETURNED`, re-run
   `08-code-implementation` on this package against the report's findings; on `VERIFIED` with more
   `READY` packages remaining in the tranche, run `08-code-implementation` naming the next one
   (critical-path first); on `VERIFIED` with the tranche's packages all `VERIFIED`, advance to
   `10-integration-review` for the tranche.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
