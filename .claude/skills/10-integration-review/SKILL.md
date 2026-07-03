---
name: 10-integration-review
description: Review a set of VERIFIED Implementation Packages together — an epic, a release bucket, or an explicitly named package set — for cross-package integration defects that per-package verification cannot see: interface mismatches between packages, violated load-bearing invariants (determinism, engine import boundary, fog-of-war at the SessionAPI seam, plan-first, sub-stepped clock, content-as-data), duplicated or contradictory behavior, seams left half-wired, and documentation/index/ROADMAP incoherence across the set. Produces an Integration Report under docs/reviews/. Use when asked to "run the integration review," "check that the verified packages work together," "review the epic/release integration," or after 09-package-verification closes the last package of a tranche. This skill is read-only with respect to code, packages, specs, and requirements — it reports and routes findings, it never fixes them. Do not use it to verify a single package (09-package-verification) or to make the release go/no-go call (11-release-readiness).
---

# Integration Review

Reviews **a set of `VERIFIED` Implementation Packages as a whole** — the seams *between* packages
that no single-package verification pass can see. This skill sits strictly downstream of
`09-package-verification` (every package in scope must already be `VERIFIED`) and strictly
upstream of `11-release-readiness`. It is a pure review: it observes, exercises, and reports; it
changes nothing but its own report.

## What this is for (and what it is not)

This skill answers one question: *now that these packages are individually verified, do they
compose — same interfaces, same invariants, same vocabulary, no gaps and no double-coverage at
their seams — into the coherent capability the epic/release promised?*

It SHALL NOT fix code, edit packages/specs/requirements, re-verify individual packages
(`09-package-verification` already did; spot-checks are for evidence, not re-adjudication), or
make the release decision (`11-release-readiness`'s job, which consumes this report).

## Scope selection

The review scope is one of: an **Epic** (per `docs/feature-planning/02-epic-catalog.md`), a
**release bucket** (per `docs/feature-planning/01-release-plan.md`), or an **explicit package
list** the user names. Every package in scope must be `VERIFIED` on the Master Build Plan — if any
isn't, stop and report which, rather than reviewing around the hole.

## What to check (the review dimensions)

1. **Interface consistency** — where two packages touch the same interface (ICD/API spec,
   `SessionAPI`, endpoint shapes, YAML schemas), do both sides agree on the contract as shipped?
   Exercise the real seam where practical (run the suite; drive endpoints via the `run-spacesim`
   utility skill when a live check is warranted).
2. **Invariant sweep** — the repository's load-bearing invariants hold *across* the set:
   determinism (no wall clock/global RNG in `engine/`), the engine import boundary, fog-of-war
   enforced at the `SessionAPI`/`CellController` boundary (never leaked into UI by a later
   package), plan-first ordering, sub-stepped clock, content-as-data. Run the permanent gates and
   grep the seams the packages touched.
3. **Behavioral coherence** — no two packages implement the same behavior divergently; no workflow
   that spans packages dead-ends at a seam (e.g. an order type one package plans that another's
   telemetry can't observe).
4. **Traceability coherence** — the RTM, feature catalog, Master Build Plan, package index, and
   `ROADMAP.md` tell the same story about what this set delivered; cross-references are
   bidirectional and unbroken.
5. **Documentation coherence** — `CLAUDE.md`'s code map and status line, the affected `INDEX.md`
   files, and the training/manual docs reflect the integrated result, not per-package snapshots.

## Output

**`docs/reviews/integration-review-<scope>.md`** (matching `docs/reviews/`' existing descriptive
naming convention), containing: the scope and package list (with the commit hash reviewed), the
evidence gathered per dimension above, and findings as one row each —
`Finding | Packages/artifacts involved | Description | Severity | Recommended owner` — using the
same Critical/High/Medium/Low scale as the project's other review documents. A clean review states
what was actually exercised to earn the "clean," not just an absence of rows. Update
`ROADMAP.md`'s review theme if it tracks review documents.

## Quality gate

- [ ] Every package in scope confirmed `VERIFIED` before the review began.
- [ ] All five dimensions were actually exercised — a dimension with nothing to report says what
      was checked, not just "OK."
- [ ] Full suite + permanent gates run against the reviewed commit, results recorded.
- [ ] Every finding has a severity and a concrete recommended owner; none was fixed in-pass.
- [ ] Nothing but the report (and review-tracker rows) was written.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 10 — Integration Review** of the documentation-driven-development pipeline
(see [`.claude/skills/README.md`](../README.md); stages run in numeric order, and
`00-pipeline-manager` reports where the project currently stands). Upstream:
`09-package-verification`. Downstream: `11-release-readiness`.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — the Integration Report written (path), scope reviewed, headline result
   (clean / N findings by severity).
2. **Recommendations** — each finding with its recommended owner: integration defects in shipped
   code go to `07-implementation-planning` (author a remediation package) then
   `08-code-implementation`; stale documentation/traceability goes to its owning artifact's skill;
   upstream design flaws go to `03-architecture-design-synthesis`/`04-requirements-engineering`.
3. **Next step** — say explicitly what to run next and why: with no Critical/High findings,
   advance to `11-release-readiness` for the release this scope belongs to; with Critical/High
   findings, run `07-implementation-planning` to package the remediation work and loop
   07→08→09 until a re-run of this review is clean.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
