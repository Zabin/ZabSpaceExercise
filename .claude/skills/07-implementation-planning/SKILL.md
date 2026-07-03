---
name: 07-implementation-planning
description: Transform approved, authorized Feature Specifications (FS-xxx) into an executable implementation plan under docs/implementation/ — a Technical Work Breakdown, build-ready Implementation Packages (IP-xxxx, the 14-field template), and the Master Build Plan (sequencing, dependency graph, critical path, status ledger). Use when asked to "plan the implementation of FS-xxx," "write the implementation package for this feature," "break this spec into work packages," "update the Master Build Plan," or to bridge an approved Feature Specification into units 08-code-implementation can execute. This skill writes no production code (packages describe work in prose/pseudocode only, MSTR-006 §8), performs no new research, no architecture redesign, no requirements authoring, and never modifies the Feature Specification it plans — and authoring a package is never itself an authorization to code it (MSTR-006 §3). Do not use it to write Feature Specifications (that belongs to 06-feature-specification) or to implement packages (that belongs to 08-code-implementation).
---

# Implementation Planning

Turns **approved, authorized Feature Specifications** into an **executable implementation plan**:
a Technical Work Breakdown, one or more Implementation Packages (`IP-xxxx`), and an up-to-date
Master Build Plan. This skill sits strictly downstream of feature-specification work and strictly
upstream of code execution. It decides *how the work is cut and sequenced*, never *what the system
does* (upstream's job) and never *the code itself* (downstream's job).

## What this is for (and what it is not)

This skill answers one question: *given one or more approved Feature Specifications, what is the
smallest set of build-ready, independently executable work packages that covers them, what does
each package touch, and in what order must they be executed?*

It SHALL NOT:

- **Write production code.** Per `MSTR-006` §8 (the Implementation-Package boundary), no package
  document contains literal committed code — architecture, data models, tasks, and tests are
  described in prose/pseudocode-level detail sufficient for a coding agent, never as compilable
  source.
- **Modify Feature Specifications, requirements, or architecture.** All strictly read-only inputs.
  A spec that turns out to be unimplementable as written, or a requirement conflict discovered
  while planning, is a finding to route upstream — never something to fix by quietly planning
  around it.
- **Authorize coding.** Per `MSTR-006` §3, a package being fully specified — even to `READY` — is
  **not** an authorization to begin implementation. Authorization is a separate, explicit user
  decision recorded per package. This skill states each package's authorization status honestly
  and never conflates "planned" with "approved to build."
- **Execute anything.** No file in the source tree changes. The moment work turns into editing
  `spacesim/`, it belongs to `08-code-implementation`.
- **Plan unauthorized Features.** A Feature Specification marked candidate / 🅿️ *Scoped, not
  authorized* gets no Implementation Package at all (MSTR-006 §3) — mirroring how FS-108/FS-202
  are excluded from the existing plan.

It treats the following as **authoritative inputs**, never as something it edits:
Feature Specifications (`docs/features/`, and `docs/features/specifications/` for new-template
specs), the Feature Catalog / Release Plan / Dependency Graph (`docs/feature-planning/`), the
requirements baseline (`docs/requirements/`), the architecture ladder + ADRs
(`docs/architecture/`), and the ICD/API specification.

## Outputs

All under `docs/implementation/` (this skill's sole write scope):

1. **`docs/implementation/01-technical-work-breakdown.md`** — the Technical Work Breakdown (TWBS):
   for the tranche being planned, a hierarchical decomposition from Feature Specification →
   work units → the package(s) that own each unit, with the rationale for every package split
   (e.g. FS-105 → IP-1050 + IP-1051 was split by bus/payload vs. effects-console seam). Create it
   on first use; extend it per tranche thereafter. If a tranche is a single small package, a short
   TWBS section is still written — the record of *why the cut is what it is* is the artifact.
2. **`docs/implementation/packages/IP-xxxx-<slug>.md`** — one Implementation Package per unit of
   work, using the repository's established **14-field template**, every field populated:
   Package ID · Objective · Requirements Covered · Architecture Components · Interfaces ·
   Files to Create/Modify · Implementation Tasks · Tests to Add · Documentation Updates ·
   Definition of Done · Verification Checklist · Dependencies · Risks · Rollback Considerations.
   Carry the standard MSTR-006 §5 metadata block (Document ID, Version, Status, Dependencies,
   Referenced By, Produces, Feature Mapping, Related Topics) exactly as the existing `IP-1010`…
   `IP-3010` files do.
3. **`docs/implementation/00-master-build-plan.md`** — updated, not regenerated: new package rows
   in the status table, dependency-graph edges, critical-path recalculation if it changed,
   parallel-opportunity notes, and the authorization status of every new package stated
   explicitly. Also update `docs/implementation/packages/INDEX.md` in the same pass — the index
   and the plan must never disagree.

## Conventions (this repository)

- **ID scheme:** `IP-<series><seq>0` mirrors the FS series — FS-1xx → `IP-10x0` (lettered slices
  become `IP-10x0`/`IP-10x1`), FS-2xx → `IP-20x0`, FS-3xx → `IP-30x0`. Check
  `packages/INDEX.md` for claimed IDs before assigning; use gapped numbering so slices can be
  inserted without renumbering.
- **Status vocabulary** (the execution ledger, used verbatim): `NOT STARTED / READY / IN PROGRESS /
  BLOCKED / COMPLETE / VERIFIED`. This skill only ever writes `NOT STARTED`, `READY`, or `BLOCKED`
  — `IN PROGRESS`/`COMPLETE` belong to `08-code-implementation`, `VERIFIED` exclusively to
  `09-package-verification`.
- **`READY` means:** the package is fully specified **and** every dependency package is
  `VERIFIED`. A package whose dependency is merely `COMPLETE` stays `BLOCKED` with a note.
- **As-built vs. forward design:** a package documenting an already-implemented capability is an
  as-built record (as the existing IP-1010…IP-1110 are) and may be born `VERIFIED` only if a
  verification pass has actually confirmed it — otherwise it enters at `COMPLETE` pending
  `09-package-verification`. A forward-design package enters at `NOT STARTED`/`READY`/`BLOCKED`.

## Workflow

### Step 0 — Confirm the inputs are approved and authorized

The target Feature Specification(s) must be approved (not candidate/🅿️), the requirements baseline
they cite must be approved, and every Open Question in the spec that blocks a planning decision
must be resolved. If not, stop and report which gate is open and who owns it — planning against a
moving or unauthorized spec produces packages that need rework the moment upstream shifts.

### Step 1 — Technical Work Breakdown

Decompose each Feature Specification into work units along real seams: subsystem boundaries,
interface boundaries, test boundaries, and the repository's own architecture (engine / session /
content / ui_web). Right-size: one package should be executable by `08-code-implementation` in a
single focused run against a single coherent Definition of Done. Split (lettered slices) when a
spec spans seams; never split just to raise the package count. Record every split decision and its
rationale in the TWBS.

### Step 2 — Author the Implementation Package(s)

One `IP-xxxx-<slug>.md` per work unit, all 14 fields, grounded in the *current* source tree —
verify every file path, class, and function the package cites actually exists as described (or is
honestly marked "to create"). A package whose `Files to Modify` list is guessed rather than
checked is the single most expensive defect this skill can produce, because
`08-code-implementation` treats drift as a hard Blocking condition. `Tests to Add` must honor the
repository's test-first mandate and name the two permanent gates (`test_determinism.py`,
`test_import_guard.py`) in the Verification Checklist.

### Step 3 — Update the Master Build Plan and package index

Add the new package rows (status, blocking dependencies, authorization state), extend the
dependency graph, recompute the critical path and parallel opportunities if the new packages
change them, and update `packages/INDEX.md` to match. State explicitly, per new package, whether
MSTR-006 §3 authorization has been given — default is **not authorized** until the user says so.

### Step 4 — Cross-link and commit

Update each planned Feature Specification's `Referenced By`/`Produces` metadata to point at its
new package(s) (metadata cross-links only — never the spec's content), flip `ROADMAP.md`'s
implementation-theme rows, and commit as `docs(implementation): IP-xxxx — <what was planned>`.

## Quality gate (before calling a planning pass done)

- [ ] Every planned FS was confirmed approved + authorized before any package was drafted.
- [ ] Every package has all 14 fields populated — no field silently blank, no literal code anywhere.
- [ ] Every `Files to Create`/`Files to Modify` entry was checked against the current source tree.
- [ ] Every `Requirements Covered` ID exists in `docs/requirements/` and matches the FS's own
      `Requirements Implemented` list — none invented, none dropped.
- [ ] Dependency edges are consistent between each package's `Dependencies` field, the Master
      Build Plan's graph, and `packages/INDEX.md`.
- [ ] No package is marked `READY` whose dependencies aren't all `VERIFIED`; no package is marked
      authorized without an explicit user go-ahead on record.
- [ ] The TWBS records the rationale for every split/no-split decision made this pass.

## Gotchas

- **Two implementation trees exist in this repository.** `docs/implementation/` (`IP-xxxx`) is
  canonical; `docs/implementations/` (`IMP-xxxA`) is the superseded prior corpus, kept with
  banners. Never write into the old tree, never reuse its IDs, and keep the "Relationship to the
  prior corpus" section of the Master Build Plan accurate if the relationship evolves.
- **Don't let a package become a second Feature Specification.** The FS owns behavior; the package
  owns files/tasks/tests/sequencing. A package restating the whole spec is bloat; a package
  contradicting the spec is a defect.
- **Plan for verification at authoring time.** A vague `Verification Checklist` makes
  `09-package-verification` guess — every checklist item should be objectively checkable against
  the tree and test run.
- The existing plan's governance notes (IP-2010/IP-3010 authorization gates, the FS-106 v2.0
  split lineage) are load-bearing history — extend them, don't flatten them in an update pass.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 07 — Implementation Planning** of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md); stages run in numeric order, and
`00-pipeline-status` reports where the project currently stands). Upstream:
`06-feature-specification`. Downstream: `08-code-implementation`.

End **every** invocation — new packages, a plan update, or a blocked stop — with a chat summary
containing exactly these three parts:

1. **What changed** — TWBS sections, packages authored (IDs + paths), Master Build Plan / index
   rows added or updated, and each new package's status + authorization state.
2. **Recommendations** — spec defects or Open Questions routed upstream, right-sizing concerns,
   critical-path or dependency risks the user should know before authorizing work.
3. **Next step** — say explicitly what to run next and why: if the new package(s) are `READY` and
   the user has authorized them, advance to `08-code-implementation` naming the first package to
   execute (critical-path first); if authorization is missing, ask the user for the explicit
   go-ahead (MSTR-006 §3) before anything is implemented; if planning was blocked on an upstream
   gap, name the owning skill (`06-feature-specification`, `04-requirements-engineering`, or
   `03-architecture-design-synthesis`) and what it must resolve.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
