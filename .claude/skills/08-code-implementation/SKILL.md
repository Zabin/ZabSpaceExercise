---
name: 08-code-implementation
description: Implement exactly one approved, eligible Implementation Package end-to-end — write the source code and tests it describes, run the full test suite, fix defects this package's own changes introduced, update the documentation and traceability the package names, and advance that package's status on the Master Build Plan. Use when asked to "implement IP-xxxx," "pick up the next ready package and build it," "execute the next step of the Master Build Plan," or to turn one already-written Implementation Package into working, tested code. This is the first skill in the documentation-driven-development chain authorized to write or modify production source code — unlike the upstream planning/spec-authoring skills, which never touch code. It selects and implements exactly one package per invocation, never redesigns architecture, never edits requirements, never modifies the Feature Specification or Implementation Package it is executing, and never chooses work outside the Master Build Plan. Do not use it to convert Feature Specifications into Implementation Packages or to author a Master Build Plan (that's 07-implementation-planning's job) or to independently re-verify/audit an already-COMPLETE package against the shipped code (that's 09-package-verification's job, which alone may advance a package to VERIFIED).
---

# Code Implementation

Turns **one approved, eligible Implementation Package** into **working, tested code**. This skill
sits strictly downstream of architecture, requirements, feature-specification, and
implementation-planning work (whatever produced the Master Build Plan and the Implementation
Package it executes), and strictly upstream of independent verification. It does not do either
neighbor's job, and it does not do more than one package's worth of its own job per invocation.

## What this is for (and what it is not)

This skill answers one question: *given one approved, eligible Implementation Package and
everything already decided about it upstream, what is the smallest, most faithful set of code and
test changes that satisfies exactly what that package describes — no more, no less — leaving the
repository in a fully green, fully traceable state when it's done?*

It SHALL NOT:

- **Redesign architecture.** Subsystem boundaries, interfaces, data models, and ADRs are inputs,
  not decisions this skill makes. If the package's design doesn't actually fit the existing
  architecture once you're inside the code, that is a finding for the Blocking Report (see
  below), never a license to quietly redraw a boundary to make the code compile.
- **Change requirements.** No `FR-xxxx`/`NFR-xxxx` (or project equivalent) is added, removed, or
  reworded by this skill. A requirement that turns out to be unimplementable as written is a
  Blocking Report finding, not something to silently satisfy a different way and call done.
- **Modify Feature Specifications.** The FS this package traces to is read-only input.
- **Modify Implementation Packages.** The package being executed — its Objective, Files to
  Create/Modify, Implementation Tasks, Tests to Add, Definition of Done — is read-only input.
  Discovering the package is wrong, incomplete, or stale relative to the current source tree is a
  Blocking Report finding, never a same-session rewrite of the package to match what you'd rather
  build.
- **Select work outside the Master Build Plan.** This skill implements the package it selected (or
  the package the user named) and nothing else — not a "while I'm in here" adjacent fix, not a
  second package, not a refactor the package didn't ask for.

It treats the following as **authoritative inputs**, never as something it edits or adds to:

- Master Build Plan
- Implementation Package (the one being executed)
- Feature Specification (the package's `Feature Reference`)
- Requirements (Functional + Non-Functional, and any Traceability Matrix)
- Architecture (subsystem decomposition, domain model)
- ICD / interface definitions
- ADRs (Architecture Decision Records)

**If any of these inputs conflict with each other, or with the current state of the source tree,
stop and produce a Blocking Report — do not resolve the conflict unilaterally.** A same-session
guess that "this is probably what they meant" is exactly the failure mode this skill exists to
prevent: it would silently break the traceability chain the entire upstream pipeline built package
by package.

## Activation criteria

Invoke this skill when:

- The user asks to implement a specific Implementation Package by ID ("implement IP-2010," "build
  IMP-105A," "start work on the bus-command package").
- The user asks to pick up, execute, or advance "the next ready package," "the next step of the
  Master Build Plan," or equivalent.
- The user asks to turn an already-written Implementation Package into real code and tests.

Do **not** invoke this skill when:

- No Master Build Plan or Implementation Package exists yet for the work in question — that's an
  upstream planning skill's job (produce the plan/package first).
- The request is to design, size, or write an Implementation Package — that is strictly upstream
  of this skill, not this skill's job.
- The request is to independently verify, audit, or re-confirm a package already marked `COMPLETE`
  against the shipped code — that is a separate verification skill's job; this skill only takes a
  package as far as `COMPLETE`, never to `VERIFIED`.
- The request spans multiple packages ("implement everything that's ready," "build the whole next
  phase") — invoke this skill once per package instead of trying to satisfy it in one pass; see
  Workflow Step 11 for why a single invocation stops after one package even when others are also
  eligible.
- The target package's own governing documentation requires a separate authorization gate beyond
  "eligible" status (see Workflow Step 2) and that authorization hasn't been given — ask the user
  first; do not treat "eligible" as "authorized."

## Primary Objective

Implement exactly one approved, eligible Implementation Package.

## Inputs

| Input | Role |
|---|---|
| **Master Build Plan** | The sequencing ledger — package statuses, dependency graph, critical path. This is where "next eligible package" is determined and where this skill writes its status updates back. |
| **Implementation Package** | The package being executed — Objective, Requirements Covered, Architecture Components, Interfaces, Files to Create/Modify, Implementation Tasks, Tests to Add, Documentation Updates, Definition of Done, Verification Checklist, Dependencies, Risks, Rollback Considerations. This is the work order; nothing outside it is in scope. |
| **Feature Specification** | The package's `Feature Reference` — the behavior contract the code must satisfy. Consult it whenever the package's own text under-specifies a behavior the code needs to decide. |
| **Requirements** (FR/NFR + Traceability Matrix) | Every requirement the package's `Requirements Covered` cites — the acceptance bar for "done," and the traceability record this skill updates on completion. |
| **Architecture** (subsystem decomposition, domain model) | The seams and entities the implementation must live inside — never a license to add a new one not already named by the package's Architecture Components. |
| **ICD / interface definitions** | Existing interfaces the package's `Interfaces` field names — the implementation must not cross a boundary the package didn't declare. |
| **ADRs** | Binding decisions the implementation must remain consistent with. |

If a project's actual layout differs from these roles (a different name or location for the
Master Build Plan, a different package-ID scheme, a combined requirements/architecture corpus),
adapt the *reading* to whatever artifacts actually carry that role locally — the workflow and
output shape below are the same regardless of how the inputs are organized. See Gotchas for how
these roles map onto this repository specifically.

## Outputs

- Real changes to the repository's source tree and test suite, scoped exactly to the executed
  package's `Files to Create`/`Files to Modify`/`Tests to Add` fields (plus any file the package's
  own Definition of Done implies but didn't enumerate — flag that gap rather than silently
  expanding scope without noting it).
- Updated documentation, at exactly the locations the package's `Documentation Updates` field
  names — no unrelated documentation rewritten "while you're in there."
- Updated traceability — whatever mechanism the repository already uses to link a requirement to
  the file(s) that implement it (a Traceability Matrix's reverse index, a code comment convention,
  a manifest) gets the executed package's `Requirements Covered` entries filled in with real,
  verified file paths, replacing any placeholder/`UNASSIGNED` value.
- An updated Master Build Plan: the executed package's status row, and (read-only note, not an
  auto-promotion — see Workflow Step 10) which downstream packages' blocking-dependency notes are
  now satisfied.
- An **Implementation Summary**, presented to the user at the end of every run:

  | Field | Content |
  |---|---|
  | **Package Implemented** | ID and title |
  | **Files Modified** | Path list, one line each |
  | **Files Created** | Path list, one line each |
  | **Tests Added** | Path(s) + what each covers |
  | **Tests Passed** | Full-suite result (pass count, fail count, skip count) — never a partial run presented as if it were the whole suite |
  | **Requirements Implemented** | The `Requirements Covered` IDs this run satisfies, cross-checked against the Definition of Done |
  | **Documentation Updated** | Path list |
  | **Traceability Updated** | What changed, where |
  | **Outstanding Issues** | Anything noticed but explicitly out of this package's scope (a pre-existing unrelated test failure, a Risk from the package that materialized, an Open Question this run couldn't resolve) — named, not fixed |

## Workflow

### Step 0 — Read the Master Build Plan

Locate the project's Master Build Plan (or equivalent sequencing ledger). Read the full package
status table and dependency graph before selecting anything — a package that looks eligible in
isolation may not be once its actual upstream dependency chain is checked.

### Step 1 — Select the next eligible package

If the user named a specific package, that is the candidate — still run the eligibility check
below before touching any code; a named package that fails eligibility produces a Blocking Report,
it is not implemented anyway "because the user asked."

If the user asked for "the next ready package" with no ID given, select deterministically:

1. Filter to packages whose Master Build Plan status is exactly `READY` (not `NOT STARTED`, not
   `IN PROGRESS`, not `BLOCKED`, not `COMPLETE`, not `VERIFIED` — `READY` only).
2. Of those, keep only packages whose every listed dependency is at `VERIFIED` — **`COMPLETE` is
   not sufficient**. A dependency that has been implemented but not yet independently verified is
   not a safe foundation to build on; treat it the same as `BLOCKED`.
3. If more than one package survives both filters, prefer the one on the Master Build Plan's
   stated critical path; if still tied, prefer the lowest package ID; if the plan gives no way to
   break the tie, list the eligible candidates and ask the user to pick rather than choosing
   silently.
4. If zero packages survive, stop — there is nothing eligible to implement. Report which packages
   are closest to eligible and what they're waiting on (this is informational, not a Blocking
   Report, since no work was selected to be blocked).

**Eligibility is necessary but not sufficient — it is not the same as authorization.** Some
repositories impose a separate go-ahead gate on top of "eligible" status for specific packages
(forward-design work that hasn't been greenlit for coding yet, work touching a regulated domain,
etc. — see this repository's own rule in Gotchas). Check for that gate before proceeding to Step 2
even for a package that is technically `READY`; if it applies and hasn't been satisfied, ask the
user explicitly rather than treating "eligible" as "go."

### Step 2 — Read the selected Implementation Package in full

Every field, not just Implementation Tasks. `Files to Create`/`Files to Modify` bounds what you're
allowed to touch; `Definition of Done` and `Verification Checklist` are the acceptance bar;
`Dependencies` tells you what must already exist and be trustworthy; `Risks` and `Rollback
Considerations` tell you what to watch for and what "undo" looks like if this goes wrong.

### Step 3 — Read every authoritative input the package cites

Feature Specification, the specific Requirements it names, the relevant Architecture/ICD/ADR
sections. Build a working inventory (your own notes, not a deliverable):

- What does the package claim about the current source tree (existing files, existing function
  signatures, existing tests) — and is that claim still true? An Implementation Package written
  even a short time ago can drift from a source tree that kept moving. A material drift (a cited
  file no longer exists, a cited function signature changed shape) is a Blocking Report finding,
  not something to route around by inventing a plausible substitute.
- Every requirement ID in `Requirements Covered` — each must be satisfied by what you're about to
  build, and each must end this run with a verifiable trace to real code.
- Whether the repository mandates a test-first workflow (check its own contributor guide/agent
  instructions — e.g. a `CLAUDE.md`, `CONTRIBUTING.md`, or equivalent). If so, follow it: write the
  failing test named in `Tests to Add` before writing the implementation it drives, not after.

### Step 4 — Mark the package `IN PROGRESS` before writing any code

Update the Master Build Plan's status table for this package to `IN PROGRESS` before the first
edit. This is what keeps a second invocation (or a second agent) from independently picking the
same package while you're mid-implementation.

### Step 5 — Implement only the work described

File by file, per `Files to Create`/`Files to Modify` and the `Implementation Tasks` list. Do not:

- touch a file the package doesn't name, even to fix something you notice in passing (name it in
  Outstanding Issues instead);
- add an abstraction, configuration flag, or "while I'm here" refactor the package didn't ask for;
- implement a task the package's own text marks as explicitly out of scope (most packages state
  these directly — respect them as strictly as the in-scope tasks).

If the repository's convention is test-first, alternate: write the next failing test from `Tests
to Add`, then the minimal implementation that makes it pass, then the next test — rather than
writing all the implementation first and backfilling tests at the end.

### Step 6 — Run all available tests

The full suite, not just the new tests this package added — a package's own Definition of Done is
necessary but a regression it introduced elsewhere is still this package's responsibility to catch
before calling it done. Run any project-specific permanent gates by name if the project documents
one (e.g., a determinism property test, an import-boundary guard) — these exist specifically to
catch the class of defect a well-intentioned but scope-broadening change can introduce.

### Step 7 — Fix defects this package's own changes introduced

If the full-suite run in Step 6 surfaces a failure, determine whether it's caused by this
package's changes or pre-existing on the branch before touching anything:

- **Caused by this package:** fix it — this is still this package's scope, not scope creep.
- **Pre-existing, unrelated to this package:** do not fix it as part of this run. Record it in
  Outstanding Issues with enough detail (failing test name, apparent cause if known) that someone
  can pick it up separately. Fixing an unrelated pre-existing failure inside this package's change
  set breaks the traceability this whole pipeline exists to preserve — that fix belongs to its own
  package or a dedicated maintenance package, not a rider on this one.

### Step 8 — Update documentation referenced by the package

Exactly the locations named in the package's `Documentation Updates` field (a code map, a module
docstring convention, an architecture doc's file-listing section, etc.). If the package names none
but the repository has an obvious convention this package's new files should follow (e.g. every
other module in this subsystem is listed in a central code map), follow that convention and note
the addition in the Implementation Summary — but do not go looking for unrelated documentation to
"also" update.

### Step 9 — Update traceability

Update whatever mechanism the repository uses to link a requirement to the code that implements
it — a Traceability Matrix's reverse index, an in-code citation convention, a manifest file — so
every requirement ID in this package's `Requirements Covered` now traces to the real file(s) you
just wrote, replacing any placeholder value the matrix previously carried for those IDs.

### Step 10 — Update the Master Build Plan

Set the executed package's status to `COMPLETE` (never `VERIFIED` — that transition belongs
exclusively to the downstream verification skill, after it independently re-confirms this run's
work against the shipped code). Re-read the dependency graph: any package that was `BLOCKED` solely
on this one reaching `COMPLETE` should have that specific blocking note updated to reflect the new
state — but do **not** flip a dependent package's own status to `READY` yourself if its
eligibility rule (Step 1) requires the dependency to be `VERIFIED`, not merely `COMPLETE`. Leave it
`BLOCKED` with an updated note ("blocked on IP-xxxx reaching VERIFIED, now COMPLETE") until the
verification skill actually closes that gap.

### Step 11 — Produce the Implementation Summary and stop

Present the Implementation Summary (see Outputs). **Stop.** Do not select or begin another
package, even if Step 1's eligibility filter would now return a different result because of this
run's own status update — a fresh invocation makes that selection deliberately, this run does not
chain into it automatically.

## Status updates

```
READY
   │  (Step 1: selected + eligibility confirmed + any repo-specific authorization gate cleared)
   ▼
IN PROGRESS
   │  (Steps 5-9: implementation, tests, docs, traceability)
   ▼
COMPLETE
   │  (a separate, downstream verification skill re-confirms this run's work
   │   against the shipped code — not performed by this skill)
   ▼
VERIFIED
```

**Off-ramp, from any state before `COMPLETE`:**

```
(any pre-COMPLETE state) ──► BLOCKED
```

This skill only ever writes `IN PROGRESS` and `COMPLETE` (or `BLOCKED`, if it stops early). It
never writes `VERIFIED` — that status change belongs exclusively to whatever downstream skill or
process independently re-confirms the work, per this repository's own status-legend convention
(see Gotchas).

## Blocking conditions

Stop immediately, without partial or speculative work-arounds, when:

- The selected/named package fails eligibility (wrong status, an unresolved dependency not yet
  `VERIFIED`, or an unmet repository-specific authorization gate).
- The package's cited files, signatures, or interfaces have materially drifted from the current
  source tree, such that following `Files to Create`/`Files to Modify` literally would not produce
  what the package's `Objective`/`Definition of Done` actually require.
- Executing the package as written would require redesigning architecture, changing a requirement,
  or otherwise exceeding this skill's SHALL-NOT list.
- A `Dependencies` field names something that does not exist, or a cited upstream artifact
  (Feature Spec, Requirement, ADR) cannot be located.

Produce a **Blocking Report** instead of any further code change:

| Field | Content |
|---|---|
| **Reason** | What specifically stopped this run — cite the exact eligibility check, drift, or scope conflict |
| **Missing dependency** | What has to exist/change first, named precisely (a package ID, a requirement, an ADR, an authorization) |
| **Required action** | The concrete next step — not "someone should look at this," but what decision or artifact would unblock it |
| **Recommended owner** | Who is positioned to resolve it (the Master-Build-Plan/package author, the architecture owner, the user directly for an authorization gate) |

Set the package's Master Build Plan status to `BLOCKED` with a one-line pointer to the Blocking
Report. **Do not begin another package** in the same run as a consolation — a blocked run ends in
a Blocking Report, not a substitute unit of work chosen instead.

## Quality rules

- **Never implement outside package scope.** If it isn't in `Files to Create`/`Files to Modify` or
  directly implied by `Implementation Tasks`, it doesn't happen in this run.
- **Never begin another package.** One invocation, one package — even when finishing early, even
  when another package is now eligible because of this run's own status update.
- **Never skip tests.** Not "the new ones passed so it's fine" — the full suite, every run, and
  any named permanent gate specifically, before calling a package `COMPLETE`.
- **Never bypass traceability.** A `Requirements Covered` ID that isn't updated to point at real,
  verified code by the end of the run is an incomplete run, not a detail to catch up on later.
- **Always maintain repository consistency.** The repository must be left in a state where the
  full test suite is green and no other package's `Files to Create`/`Files to Modify` were touched
  — a run that "mostly" finishes but leaves the tree red or another package's scope disturbed has
  not satisfied this skill's job, regardless of how much of the target package it completed.

## Examples

**"Implement the next ready package."**
Read the Master Build Plan. Filter to `READY` packages whose dependencies are all `VERIFIED`. If
exactly one survives, select it. Check for any repository-specific authorization gate on that
package before proceeding. Read the package, its Feature Spec, and its cited requirements/
architecture/ADRs. Mark it `IN PROGRESS`. Implement, test, document, update traceability. Mark it
`COMPLETE`. Produce the Implementation Summary. Stop — do not continue to whatever is eligible
next.

**"Implement IP-2010."**
Even though named explicitly, still run the eligibility check. If the repository's own governance
requires a separate go-ahead for this specific package beyond "eligible" (see Gotchas for an
example), and that go-ahead hasn't been given in this conversation, stop and ask the user for it
explicitly before writing any code — naming a package is not the same as authorizing it.

**A package's `Files to Modify` names a function that no longer exists in the current source
tree.**
This is drift, not an implementation decision. Do not guess at the function's likely successor and
proceed. Produce a Blocking Report: Reason = "cited function `X` not found in `path/to/file`, last
touched in commit Y"; Missing dependency = "an updated Implementation Package reflecting the
current source shape"; Required action = "re-derive this package's `Files to Modify` against the
current tree"; Recommended owner = "whoever maintains the Implementation Package corpus."

**Mid-run, the full test suite shows one failure unrelated to anything this package touched.**
Do not fix it as part of this package's change set. Finish this package's own work, confirm its
own tests are green, and record the unrelated failure in Outstanding Issues with the failing test
name and any apparent cause — a separate run (its own package, or a maintenance task) owns that
fix.

**"While you're implementing this, also clean up the naming in the module next to it."**
Decline within this run. That's a scope addition the Implementation Package doesn't describe;
implementing it here would make the eventual verification pass unable to cleanly attribute changes
to the package it's checking. Suggest it as a follow-up package or a separate, explicitly-scoped
request instead.

## Limitations

- This skill cannot produce a correct implementation from a genuinely wrong or incomplete
  Implementation Package — a package with a real design gap or a stale file reference produces a
  Blocking Report, which is the correct outcome, not a failure of this skill.
- It does not perform the architectural or requirements judgment calls that should already have
  been resolved upstream (by architecture-design/requirements/feature-specification/
  implementation-planning work) — it implements a decision already made, it does not make one.
- It does not independently verify its own output beyond running the test suite and checking the
  package's own Definition of Done — a deeper, independent code review, security review, or
  re-audit against the shipped code is the downstream verification skill's job, not this one's.
- It cannot merge, deploy, or release anything — its output ends at `COMPLETE`, tested and
  documented in the working tree, ready for verification and whatever the repository's normal
  review/merge process requires next.
- It is not a substitute for a well-formed Master Build Plan or Implementation Package — a
  thin or ambiguous package produces either a thin implementation with a long Outstanding Issues
  list, or (correctly) a Blocking Report, not a plausible-looking implementation invented to fill
  the gap.

## Recommended repository layout

```
docs/
├── requirements/                          # input — FR/NFR/traceability matrix (read-only)
├── architecture/                          # input — subsystem decomposition, ICD, ADRs (read-only)
├── features/                              # input — Feature Specifications (read-only)
├── implementation/  (or your project's equivalent name)
│   ├── 00-master-build-plan.md            # read + write — status table, dependency graph
│   └── packages/
│       └── IP-xxxx-name.md                # input — the package being executed (read-only)
<source tree>/                             # write scope — exactly what the package names
<test tree>/                               # write scope — exactly what the package names
```

## Gotchas

- **In this repository specifically**, the Master Build Plan is
  `docs/implementation/00-master-build-plan.md` and packages live under
  `docs/implementation/packages/IP-xxxx-name.md` (see that directory's own `INDEX.md` for the full
  status legend). The status vocabulary is exactly `NOT STARTED / READY / IN PROGRESS / BLOCKED /
  COMPLETE / VERIFIED` — use these values verbatim, not this project's separate `MSTR-006` §2
  symbol taxonomy (✅/🚧/⛔/♻️/🖼️/🅿️), which governs the *documentation corpus* generally, not this
  execution ledger specifically.
- **Authorization is a separate gate from eligibility in this repository.** Per
  `docs/master/MSTR-006-governance-principles.md` §3, a package being `READY` (fully specified,
  every dependency satisfied) is explicitly **not** itself an authorization to begin coding for
  any package whose Implementation Package or Feature Specification is marked forward-design/not
  yet authorized (currently `IP-2010` Competency Assessment and `IP-3010` Research Analytics — see
  `docs/implementation/00-master-build-plan.md`). Ask the user for explicit go-ahead before Step 4
  for either of these, even though the Master Build Plan lists one of them as `READY`.
- **This repository mandates test-first development.** Its `CLAUDE.md` states: "Build every phase
  test-first: encode that phase's roadmap 'done when' check as a failing `pytest` test, then
  implement until it passes. Never write production code without a failing test driving it." Step
  3/5 above are not optional guidance here — they are this repository's binding workflow.
- **Two permanent gates must stay green after every package in this repository:**
  `spacesim/tests/test_determinism.py` (the Phase-1 determinism property test) and
  `spacesim/tests/test_import_guard.py` (the engine-boundary AST guard). Run them by name in
  addition to the full suite in Step 6 — a package that breaks either, even indirectly, is not
  `COMPLETE` regardless of what its own new tests show.
- **The engine (`spacesim/engine/`) is UI/network/wall-clock/global-RNG-free by construction** —
  per `CLAUDE.md`'s load-bearing invariants. Never add an import, a `datetime.now()`/wall-clock
  read, or a `random`-module call inside `spacesim/engine/` to satisfy a package's task, even if it
  would be the locally convenient way to do it; `test_import_guard.py` exists specifically to catch
  this class of defect, and a package that seems to require it has drifted from the architecture —
  treat that as a Blocking Report, not a one-off exception.
- **The Traceability Matrix's reverse indices in this repository are honest about gaps** (see
  `docs/requirements/03-requirements-traceability-matrix.md`) — many `Requirements Covered` cells
  are `UNASSIGNED` by design where no prior work closed the citation. Step 9 in this repository
  means updating exactly the cells this package's own `Requirements Covered` field names, from
  `UNASSIGNED` (or a prior package's stale value) to the real file(s) this run produced — not
  attempting to close every `UNASSIGNED` cell in the matrix, which is out of this package's scope.

## Best practices

- **Read the whole package before writing the first line of code.** A `Files to Modify` list read
  in isolation, without the package's `Objective` and `Definition of Done`, invites implementing
  the letter of a file list while missing the point of the change.
- **Prefer the smallest change that satisfies the Definition of Done.** A package's own text is the
  scope contract — resist the pull toward a "better" design not asked for; that instinct belongs in
  a future package's `Risks`/Open-Questions trail, not this run's diff.
- **Keep the Implementation Summary honest about partial success.** If a `Tests to Add` item
  couldn't be written exactly as specified (e.g., the package's proposed test fixture doesn't
  exist), say so in Outstanding Issues rather than quietly substituting a different test and
  presenting the summary as fully satisfying the package.
- **Treat a stale Implementation Package as a finding, not an obstacle to route around.** The
  Blocking Report exists precisely so drift between planning-time and execution-time state doesn't
  get silently absorbed into ad hoc improvisation.
- **Leave the tree exactly as green as (or greener than) you found it.** A pre-existing failure you
  noticed but correctly left alone (Step 7) should still be visible in Outstanding Issues — silence
  about a known-red test is worse than a documented one.

## Quality checklist

Use this as the final gate before presenting a package as `COMPLETE`:

- [ ] The executed package's status was `READY` (or explicitly re-confirmed eligible if named
      directly by the user), every dependency was `VERIFIED`, and any repository-specific
      authorization gate beyond eligibility was explicitly cleared before Step 4.
- [ ] Every file touched appears in the package's `Files to Create`/`Files to Modify`, or is a test
      file implied by `Tests to Add` — nothing else.
- [ ] Every `Tests to Add` item exists and passes; the full test suite (plus any named permanent
      gates) passes, not just this package's own new tests.
- [ ] Every `Requirements Covered` ID now traces to real, verified file paths in whatever
      traceability mechanism the repository maintains — no ID left pointing at a placeholder.
- [ ] Every `Documentation Updates` location named by the package was actually updated; no
      unrelated documentation was touched.
- [ ] Any test failure surfaced during the run was either fixed (if caused by this package) or
      recorded in Outstanding Issues with enough detail to act on (if pre-existing/unrelated) —
      none silently ignored.
- [ ] The Master Build Plan reflects this package at `COMPLETE` (never `VERIFIED`), and any
      downstream package whose blocking note referenced this one was updated to reflect the new
      state without being auto-promoted past its own eligibility rule.
- [ ] No other package's status, scope, or files were touched.
- [ ] The Implementation Summary is complete and accurate against the actual diff, not an
      idealized description of what was intended.

## Success criteria

The implementation run is successful when:

1. **Fidelity** — the code and tests produced match exactly what the executed Implementation
   Package described; nothing broader, nothing narrower, nothing substituted without being flagged.
2. **Verifiability** — the full test suite (and any named permanent gates) passes, and every claim
   in the Implementation Summary can be checked directly against the diff and the test run.
3. **Traceability preserved** — every requirement the package claimed to cover now traces to real
   code, and the Master Build Plan accurately reflects the package's new status and its effect on
   downstream dependents.
4. **Scope discipline** — exactly one package was implemented; no architecture, requirement,
   Feature Specification, or Implementation Package was modified; no unrelated file was touched;
   no second package was begun.
5. **Honesty under uncertainty** — a package that could not be safely implemented as written
   produced a clear, actionable Blocking Report instead of a plausible-looking but silently
   incorrect implementation.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 08 — Package Execution** of the documentation-driven-development pipeline
(see [`.claude/skills/README.md`](../README.md); stages run in numeric order, and
`00-pipeline-manager` reports where the project currently stands). Upstream:
`07-implementation-planning` (which authors the Master Build Plan and the `IP-xxxx` packages this
skill executes). Downstream: `09-package-verification` (the only skill that may advance a package
to `VERIFIED`).

The Implementation Summary (Step 11) already carries the run's factual record; in the same closing
message, additionally state:

1. **Recommendations** — every Outstanding Issue with its suggested owner (a follow-up package via
   `07-implementation-planning`, an upstream artifact owner, or the user).
2. **Next step** — say explicitly what to run next and why: after a package reaches `COMPLETE`,
   the next step is always `09-package-verification` for that same package — never another
   implementation run first, and never chained automatically by this run; after a Blocking Report,
   the next step is whatever the report's "Required action"/"Recommended owner" names (usually
   `07-implementation-planning` to repair the package, or the user for an authorization gate).

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
