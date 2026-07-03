---
name: 11-release-readiness
description: Make the evidence-based go/no-go assessment for one release bucket and, on GO, update the engineering baseline — produce a Release Assessment under docs/reviews/ (scope delivered vs. planned, verification and integration evidence, known deviations, residual risks, explicit GO/NO-GO), and on GO flip the baseline records (ROADMAP.md statuses, release-plan bucket state, CLAUDE.md status line, affected INDEX files) so the whole tree agrees the release shipped. Use when asked "are we ready to release," "run the release readiness review," "close out the MVP/Release 1 bucket," or after 10-integration-review comes back clean for a release's scope. The GO/NO-GO recommendation is advisory — the user makes the actual release decision; this skill never writes code, never edits packages/specs/requirements, and performs no deployment. Do not use it to review package integration (10-integration-review) or to verify packages (09-package-verification).
---

# Release Readiness & Baseline Update

Closes the loop on **one release bucket** (Prototype / MVP / Release 1 / Release 2, per
`docs/feature-planning/01-release-plan.md`): assembles the evidence that the bucket's promised
scope was delivered, verified, and integration-reviewed; states an explicit **GO / NO-GO**
recommendation with the reasoning; and — on the user's GO — updates the engineering baseline so
every tracker in the tree agrees the release shipped. This is the final stage of the pipeline; its
output is the record the *next* increment plans against.

## What this is for (and what it is not)

This skill answers one question: *for this release bucket, does the evidence — not the intention —
show that everything promised is `VERIFIED`, integrated, documented, and honest about deviations,
such that declaring the release is defensible?*

It SHALL NOT: write or fix code; edit packages, specs, requirements, or architecture; re-run
verification or integration review itself (it consumes their reports — a missing report is a
NO-GO input, not a gap to fill in-pass); deploy anything; or declare GO on the user's behalf —
the recommendation is advisory and the user makes the call before any baseline flip.

## Inputs (all read-only)

The release plan + feature catalog (`docs/feature-planning/`), the Master Build Plan + package
index (`docs/implementation/`), the Verification Reports (`docs/implementation/verification/`),
the Integration Report(s) for this scope (`docs/reviews/integration-review-*.md`), the RTM
(`docs/requirements/03-requirements-traceability-matrix.md`), and `ROADMAP.md`.

## Workflow

1. **Reconstruct the promise.** From the release plan: every Feature in the bucket, and from the
   catalog/RTM every requirement those features own. This is the checklist reality is audited
   against — scope as *planned*, not as it conveniently ended up.
2. **Audit delivery.** Feature by feature: FS approved → package(s) planned → `VERIFIED` (with a
   real VR) → covered by a clean Integration Report. Any feature deferred, descoped, or split
   since planning is a **deviation** to record with its authorizing decision (or flagged as
   unauthorized drift if there isn't one).
3. **Sweep residual risk.** Outstanding Issues from Implementation Summaries, Low/Medium findings
   accepted through verification and integration review, open Candidate Requirements touching this
   scope, and known-stale docs. None of these necessarily blocks GO — unstated ones do.
4. **Write the Release Assessment** → `docs/reviews/release-assessment-<release>.md`:

   | Section | Content |
   |---|---|
   | **Release** | Bucket, date, commit hash assessed |
   | **Scope audit** | One row per planned Feature: FS → IP(s) → VR(s) → integration coverage → delivered/deviated |
   | **Evidence** | Test-suite state, permanent gates, the VR and Integration Report inventory relied on |
   | **Deviations** | Everything delivered differently than planned, each with its authorization trail |
   | **Residual risks** | Accepted findings and open issues shipping with the release |
   | **Assessment** | **GO** or **NO-GO**, with the blocking items enumerated on NO-GO |

5. **On the user's explicit GO — update the baseline** (this is the only mutating step, and it
   touches trackers only): flip the release bucket's state in `01-release-plan.md`; flip the
   delivered features'/packages' rows in `ROADMAP.md`; update `CLAUDE.md`'s status line if the
   release changes the project's headline state; update affected `INDEX.md` files; date-stamp the
   baseline in the Release Assessment itself. Commit as
   `docs(release): <release> — assessment + baseline update`. On NO-GO (or GO not yet given),
   write the assessment only and leave every tracker untouched.

## Quality gate

- [ ] Every Feature the release plan put in this bucket appears in the scope audit — none quietly
      dropped from the checklist.
- [ ] Every "delivered" row is backed by a named VR and integration coverage, not by memory.
- [ ] Every deviation has its authorization trail recorded, or is flagged as unauthorized drift.
- [ ] The GO/NO-GO reasoning is stated in the assessment, and no baseline record was flipped
      without the user's explicit GO.
- [ ] After a GO flip, release plan, ROADMAP, Master Build Plan, and CLAUDE.md agree — no tracker
      left telling the old story.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 11 — Release Readiness & Baseline Update**, the final stage of the
documentation-driven-development pipeline (see [`.claude/skills/README.md`](../README.md); stages
run in numeric order, and `00-pipeline-manager` reports where the project currently stands).
Upstream: `10-integration-review`. Downstream: the next increment's planning.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — the Release Assessment written (path + GO/NO-GO), and any baseline records
   flipped (only after an explicit user GO).
2. **Recommendations** — on NO-GO, the blocking items each with its owning skill; on GO, the
   residual risks the user is accepting and any deferred scope now owed to a future bucket.
3. **Next step** — say explicitly what to run next and why: on NO-GO, the highest-leverage
   blocking item's owning skill (usually `07-implementation-planning` →
   `08-code-implementation` → `09-package-verification`, then re-run `10-integration-review`);
   on GO with baseline updated, the next increment — `00-pipeline-manager` to survey the tree, then
   typically `05-feature-decomposition`/`06-feature-specification` for the next release bucket, or
   `01-vision`/`02-research-*` if the increment changes direction.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
