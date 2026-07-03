---
name: 06-feature-specification
description: Transform an approved Feature (a Feature Catalog entry, or this project's own DOM/ADS-grounded Feature concept) into a detailed technical design specification under docs/features/specifications/ — one FS-xxxx-name.md per Feature, ready to hand to an Implementation Package. Use when asked to "write the feature spec for FS-xxxx," "turn this approved feature into a design spec," "detail the system behavior/interfaces/data model for a feature," or to bridge an approved Feature Catalog/requirements baseline into implementation-ready detail. This skill performs no new requirements, no architecture redesign, no code, and does not modify the approved Feature it specifies — it is a pure elaboration step between an approved Feature and a downstream implementation package. Do not use it to decompose requirements into features (that belongs to feature-decomposition) or to make architecture decisions (that belongs to architecture-design-synthesis).
---

# Feature Specification

Turns an **approved Feature** into a **detailed technical design specification**. This skill sits
strictly downstream of requirements, architecture, and feature-decomposition work, and strictly
upstream of implementation packages and code. It does not do either neighbor's job.

## What this is for (and what it is not)

This skill answers one question: *given one approved Feature and everything already decided about
it upstream, what exactly must the system do — its workflows, behavior, subsystem responsibilities,
interfaces, data, state, errors, and acceptance criteria — stated precisely enough that an
implementation package can be written from it without re-deciding anything design-level?*

It SHALL NOT:

- **Write code.** No schemas-as-code, no API stubs, no function signatures, no scaffolding. A
  Feature Specification describes behavior and structure in prose/tables/diagrams, not in a
  programming language.
- **Redesign architecture.** Subsystem boundaries, interfaces, and ADRs are inputs, not decisions
  this skill makes. If a Feature's natural design doesn't fit an existing subsystem/interface, that
  is a finding for the architecture owner, not a license to quietly redraw a boundary here.
- **Create new requirements.** Every requirement this spec implements must already exist as an
  `FR-xxxx`/`NFR-xxxx` (or project equivalent) in the Requirements Baseline. A capability gap
  discovered while specifying is an Open Question, never a new requirement invented to fill the
  gap.
- **Modify approved Features.** This skill reads the Feature Catalog / approved Feature entry and
  never edits it. A Feature that looks mis-scoped, too large, or missing a dependency is a finding
  to report upstream (to whoever owns `05-feature-decomposition`'s output), never something to
  silently re-scope while writing its spec.

It treats the following as **authoritative inputs**, never as something it edits or adds to:

- Feature Catalog (and Epic Catalog, for the Feature's grouping context)
- Requirements Baseline (Functional + Non-Functional Requirements, Traceability Matrix)
- Architecture (subsystem decomposition, domain model)
- ICD / interface definitions
- ADRs (Architecture Decision Records)

**If the input documents conflict with each other, or the Feature's stated scope cannot be
satisfied within the existing architecture, report the conflict in the spec's Open Questions
section — do not resolve it unilaterally.** Resolving a real upstream conflict is a decision for
whoever owns the conflicting artifact, not something this skill should paper over while writing a
design spec.

## Activation criteria

Invoke this skill when:

- The user asks to write, draft, or update a Feature Specification (`FS-xxxx`) for one or more
  **already-approved** Features.
- The user asks to turn a Feature Catalog entry (or an equivalent approved feature concept) into
  implementation-ready design detail — workflows, system behavior, interfaces, data model impact,
  acceptance criteria.
- The user asks "what would FS-xxxx actually need to do," "what interfaces does this feature
  touch," or "is this feature spec complete enough to hand to implementation."

Do **not** invoke this skill when:

- No Feature Catalog / approved Feature exists yet — run `05-feature-decomposition` first.
- The requirements baseline backing the Feature isn't approved yet — run `04-requirements-engineering`
  first.
- The request is to decompose requirements into features, size epics, or build a release plan —
  that's `05-feature-decomposition`'s job, strictly upstream of this one.
- The request is to write code, an implementation package, or tests for an already-specified
  Feature — that is downstream of this skill's output, not this skill's job.
- The request is to change the architecture, add an interface, or add an ADR to make a Feature fit
  — that's `03-architecture-design-synthesis` / the architecture owner's job; report the mismatch
  instead.

## Inputs

Read, in this order, before drafting a single spec:

| Path | Role |
|---|---|
| Feature Catalog / Epic Catalog | The approved Feature's own entry — Purpose, Scope, Included Requirements, Dependencies, Affected Subsystems/Interfaces, Related ADRs. This is the contract the spec must elaborate, not override. |
| Requirements Baseline (FR/NFR + Traceability Matrix) | Every requirement the Feature claims to implement must trace here by ID. |
| Architecture (subsystem decomposition, domain model) | The seams and entities the Feature's design must live inside. |
| ICD / interface definitions | Existing interfaces the Feature consumes or must extend. |
| ADRs | Binding decisions the spec's design must remain consistent with. |

If a project's actual layout differs from these roles (e.g. this repository's own
`docs/domains/DOM-xxx` → `docs/research/encyclopedia/R-xxx` → `docs/architecture/ADS-xxx` chain
feeding its existing `docs/features/FS-1xx-*.md` convention — see Gotchas below), adapt the
*reading* to whatever artifacts actually carry that role locally, not the *output template* — the
fixed field set below is the same regardless of how the inputs are organized. Record the mapping
used at the top of the spec (or of an index, if one exists) so a reviewer can audit it.

## Outputs

One file per Feature, under `docs/features/specifications/`:

```
docs/features/specifications/FS-xxxx-name.md
```

Use the Feature's own ID from the Feature Catalog (or the project's existing FS numbering — see
Gotchas) and a short kebab-case slug of its title, matching the sibling-skill convention already
used in this repo (e.g. `FS-1000-mission-planning.md`).

Create or update `docs/features/specifications/INDEX.md` (one row per spec: ID, title, status,
owning Epic/Domain, one-line summary) if the project has an `INDEX.md` convention for sibling
directories — check `docs/features/feature-index.md` or `docs/INDEX.md` for the local pattern
before deciding whether to add one.

## Workflow

### Step 0 — Confirm the Feature is approved, then build a reading inventory

Confirm the target Feature actually has an approved entry in the Feature Catalog (or equivalent)
before drafting anything — specifying an unapproved or still-changing Feature produces a spec that
will need rework the moment the catalog entry changes underneath it. If it isn't approved, stop and
surface that to the user.

Then read the Feature's own catalog entry plus every requirement, subsystem, interface, and ADR it
cites. Build a working inventory (your own notes, not a deliverable) of:

- The Feature's `Included Requirements` (every `FR-xxxx`/`NFR-xxxx` this spec must account for —
  every one must appear somewhere in the spec's `Requirements Implemented`).
- The Feature's `Dependencies` / `Dependent Features` (what must exist first, what waits on this).
- The Feature's `Affected Subsystems` and `Affected Interfaces` (the design surface available to
  use, not invent).
- Any `ADR` the Feature is already bound to.
- Anything the catalog entry implies but doesn't state outright — flag now as a candidate Open
  Question rather than quietly deciding it while drafting.

### Step 1 — Draft the spec using the fixed template

Populate every field of the **Feature Specification Template** (below) for the target Feature. Work
field by field, in order — each field builds on the ones before it (Scope bounds Requirements
Implemented; Requirements Implemented bounds User Workflows; User Workflows bound System Behaviour;
and so on through Acceptance Criteria).

**Writing discipline, applied to every field:**

- **Trace, don't assert.** Every non-trivial statement in the spec should be traceable to a cited
  requirement, architecture section, ADR, or interface — not to this skill's own judgment about
  what "should" happen. Where the inputs are silent on something the spec needs, that is an Open
  Question, not a gap to fill from general software-engineering convention.
- **Behavior, not implementation — unless architecture has already committed to the
  implementation detail.** Describe what the system does and how subsystems are responsible for
  it, using the vocabulary the Architecture/Domain Model/ICD already use. Only name a concrete
  data structure, schema, or algorithm if an already-approved architecture document or ADR commits
  to it — do not introduce a new one here to make the spec feel more concrete.
- **Unknowns become Open Questions, every time.** Never resolve a genuine ambiguity by picking the
  most plausible answer and writing it as settled fact. State the ambiguity, why it matters, and
  what input artifact would need to change to resolve it.
- **No scope creep past the Feature's own boundary.** If a design question only makes sense to
  answer by also specifying a *different* Feature, name that Feature and move on — don't let one
  spec quietly absorb a neighbor's scope.

### Step 2 — Self-check against the Quality Gate

Before presenting the spec as complete, run it against the Quality gate below. A spec that fails
any checked item is not done — fix the field, don't note the gap and move on (Open Questions are
for genuine upstream ambiguity, not for fields the author simply didn't finish).

### Step 3 — Update the index (if one exists)

If `docs/features/specifications/INDEX.md` (or the project's nearest equivalent) exists, add or
update this Feature's row. Do not let the index drift from the specs it lists.

## Feature Specification Template

Every spec carries this fixed field set, in this order — an empty-looking field (e.g.
"Dependencies: None") is informative; a missing field is not:

| Field | Content |
|---|---|
| **Feature ID** | `FS-xxxx`, matching the Feature Catalog entry |
| **Title** | Short, action-oriented, matching the catalog entry's Title |
| **Purpose** | The single stakeholder or system need this Feature exists to satisfy — drawn from the catalog entry's own `Purpose`/`User Value`, not reinvented |
| **Scope** | The boundary of what this spec covers, stated positively, consistent with the catalog entry's `Scope`/`Excluded Requirements` |
| **Requirements Implemented** | Every `FR-xxxx`/`NFR-xxxx` ID this Feature owns, per the catalog entry's `Included Requirements` — each must appear here; none invented |
| **User Workflows** | Step-by-step, cell/role-perspective sequences of how a user (or another subsystem) exercises this capability, end to end |
| **System Behaviour** | What the system actually does in response to each workflow step — the observable behavior contract, including normal-path and edge-case branches implied by the requirements |
| **Subsystem Responsibilities** | Which existing subsystem (per Architecture/Domain Model) owns which piece of the behavior — one row per subsystem touched, never a new subsystem invented here |
| **Interfaces Used** | Existing ICD interfaces this Feature consumes, extends, or produces through — cite interface IDs, don't describe a new interface shape unless an ADR already commits to it |
| **Data Model Changes** | Entities/attributes/relationships this Feature reads or writes, against the existing Domain Model — additions only where the requirements demand them, flagged as Open Questions if the existing model doesn't support the behavior |
| **State Changes** | What persistent or session state this Feature creates, transitions, or retires, and under what triggers |
| **Error Handling** | Failure modes implied by the requirements/workflows and the observable behavior on each — not implementation-level exception types, the user/system-visible contract |
| **Performance Considerations** | Any NFR-driven constraint (latency, throughput, determinism, replay-safety) this Feature must respect, cited to its NFR ID |
| **Security Considerations** | Any NFR/ADR-driven trust-boundary, authorization, or fog-of-war constraint this Feature must respect, cited to its source |
| **Acceptance Criteria** | Concrete, checkable conditions a reviewer could verify pass/fail without consulting this spec's own author — derived from, but not necessarily identical to, the underlying requirements' own Acceptance Criteria |
| **Verification Plan** | How completion will be checked — Test/Demonstration/Analysis/Inspection per criterion, consistent with the requirements' own Verification Method fields |
| **Dependencies** | Other `FS-xxxx` IDs (or subsystems) this Feature requires to exist first, per the catalog entry |
| **Risks** | What could go wrong specifying or implementing this Feature, and why — ambiguity risk, dependency risk, architectural-fit risk |
| **Open Questions** | Every genuine ambiguity this spec surfaced and could not resolve from approved inputs |
| **Related ADRs** | ADR IDs this Feature's design must remain consistent with |
| **Related Interfaces** | ICD interface IDs related to but not directly used by this Feature (context for a reader, distinct from `Interfaces Used`) |

## Rules

- **Every statement must trace back to approved design artifacts.** A sentence in System Behaviour,
  Data Model Changes, or any other field that cannot be tied to a requirement, architecture
  section, ADR, or interface is a defect, not detail.
- **Unknowns become Open Questions.** Never silently resolve an ambiguity by picking the most
  plausible answer.
- **No implementation details unless already established by architecture.** A spec that names a
  concrete schema, API shape, or algorithm not already committed to by an approved architecture
  document or ADR has crossed into implementation-package territory — push it back to "what
  behavior is observable, owned by which subsystem," not "how is it built."

## Quality gate (before calling a spec done)

- [ ] The Feature's catalog entry was confirmed approved before drafting began.
- [ ] Every Template field is populated (or explicitly `None` with a reason, never silently blank).
- [ ] Every `Included Requirements` ID from the catalog entry appears in `Requirements Implemented`
      — none added, none dropped.
- [ ] Every User Workflow has a corresponding System Behaviour entry covering both its normal path
      and at least one edge case implied by the requirements.
- [ ] Every Subsystem Responsibilities row names a subsystem that already exists in the
      Architecture/Domain Model — none invented.
- [ ] Every Interfaces Used entry cites an existing ICD interface ID, or is flagged as an Open
      Question if the behavior needs an interface that doesn't yet exist.
- [ ] No field contains a concrete data structure, schema, function signature, or algorithm that
      isn't already committed to by an approved architecture document or ADR.
- [ ] Every Open Question states why it matters and what upstream artifact would need to change to
      resolve it — not just "TBD."
- [ ] Acceptance Criteria are checkable by a reviewer with no other context beyond this spec and the
      cited requirements.
- [ ] The Feature Catalog entry itself was not edited, and no new `FR-xxxx`/`NFR-xxxx` was created.

## Examples

**"Write the Feature Specification for FS-1450 (Sensor Tasking Contention)."**
Confirm FS-1450 is approved in the Feature Catalog. Read its Included Requirements, Dependencies,
Affected Subsystems/Interfaces, Related ADRs. Draft `docs/features/specifications/FS-1450-sensor-
tasking-contention.md` field by field per the Template. Run the Quality gate. Update the index.

**"FS-1450's spec says contention resolves by priority, but the requirements baseline doesn't say
what happens on a priority tie."**
That's a genuine gap. Add it to Open Questions: state the tie scenario, why it matters
(non-deterministic resolution would violate the project's determinism invariant if unresolved), and
that it needs either a new NFR or an ADR before this spec can commit to a tie-breaking rule. Do not
invent a tie-breaking rule to make the spec look complete.

**"This feature obviously needs a new `TaskingQueue` interface — just add it to the spec."**
Do not author a new interface here. Name the gap in `Interfaces Used` as an Open Question
("requires an interface not yet in the ICD") and flag it for the architecture owner — adding an
interface is an architecture decision, not a specification-elaboration decision.

**"Update FS-1450's spec — the Feature Catalog now lists NFR-2210 as an additional Included
Requirement."**
Re-open the existing spec, not a fresh draft. Add NFR-2210 to `Requirements Implemented`, and update
whichever other fields (System Behaviour, Performance Considerations, Acceptance Criteria,
Verification Plan) the new requirement actually affects. Leave unaffected fields untouched.

## Limitations

- This skill cannot produce a spec more concrete than its inputs allow — a Feature Catalog entry or
  architecture that is itself thin or ambiguous yields a spec with a long Open Questions list,
  which is the correct outcome, not a failure of this skill.
- It does not adjudicate the conflicts or gaps it finds — someone with authority over the Feature
  Catalog, requirements, or architecture must resolve a reported issue before the spec can close
  its Open Questions.
- It is not a substitute for architecture or requirements review: a well-organized, fully-templated
  spec can still faithfully describe a Feature whose upstream definition has its own unresolved
  defects.

## Recommended repository layout

```
docs/
├── requirements/                        # input — FR/NFR/traceability matrix (read-only)
├── architecture/                        # input — subsystem decomposition, domain model, ICD, ADRs
├── features/
│   ├── 03-feature-catalog.md            # input — the approved Feature Catalog (read-only)
│   └── specifications/                  # output — this skill's sole write scope
│       ├── INDEX.md                     # optional, if the project uses per-directory indexes
│       └── FS-xxxx-name.md
```

## Gotchas

- **This skill's 20-field template supersedes the prior ad hoc FS-xxx structure for all Feature
  Specifications in this repository.** The existing 11 files (`FS-101-mission-planning.md` …
  `FS-301-research-analytics.md`, under `docs/features/`) have been **rewritten in place** to the
  new template — same file paths, same `FS-xxx` IDs, same MSTR-006 §5 metadata blocks, no
  renumbering. The prior DOM→R→ADS→FS chain (Training Objective → Domain Document (`DOM-xxx`) →
  Research → Design Synthesis (`ADS-xxx`) → Feature Spec → IMP) remains the upstream sourcing
  chain for this repository's Feature concepts; this skill's template is now the governing format
  for the FS stage of that chain, absorbing and replacing any prior ad hoc per-section structures.
  The `docs/features/specifications/` subdirectory named in the Outputs section below is the
  canonical write scope for **new** Feature Specifications going forward; it does not apply
  retroactively to the absorbed 11 files, which remain at their existing paths.
- **No Feature Catalog exists in this repository yet.** The repo has no `05-feature-decomposition`-
  produced catalog in `docs/features/`. When invoked here for a new Feature Specification, treat
  the relevant `DOM-xxx`/`ADS-xxx` documents as the "approved Feature" input in place of a Feature
  Catalog row, and confirm this is the intended source before drafting.
- **Check `docs/features/feature-index.md` before assigning a new `FS-xxxx` ID.** The 11 absorbed
  files claim IDs 101–107 (FS-1xx), 108 (🅿️ candidate), 201, 202 (🅿️ candidate), and 301. New
  IDs must not conflict with these.
- **Don't let a spec re-derive what its Feature Catalog entry (or `DOM-xxx`/`ADS-xxx` equivalent)
  already decided.** `Purpose`, `Scope`, `Dependencies`, `Affected Subsystems/Interfaces`, and
  `Related ADRs` should be carried forward from the upstream entry, not re-litigated.
- **Don't promote an Open Question to a settled answer just because the spec "needs" one to feel
  complete.** A spec with several honest Open Questions is more useful than one with confident
  invented answers that implementation will have to silently override later.

## Best practices

- **Carry IDs forward verbatim.** A Feature's `FS-xxxx` ID, its `Included Requirements`, and its
  `Affected Subsystems/Interfaces` should read identically between the Feature Catalog entry and
  this spec's `Requirements Implemented`/`Subsystem Responsibilities`/`Interfaces Used` — any
  divergence is a defect to fix, not a refinement to silently apply.
- **Keep `Dependencies` and `Related ADRs` aligned with their upstream source.** A one-directional
  or stale cross-reference is the kind of defect a later traceability review will catch — keep it
  correct the first time.
- **Write Acceptance Criteria a tester could use cold.** If verifying a criterion requires reading
  this spec's own prose reasoning rather than just the criterion itself, tighten the criterion.
- **Keep User Workflows concrete and role-scoped.** Name the actual cell/role/subsystem acting at
  each step — a workflow written in the passive voice ("the order is validated") hides who is
  responsible, which Subsystem Responsibilities then has to silently re-derive.
- **Run the Quality Gate before declaring a spec done, not after a user objects.** Most gate
  failures (unpopulated field, untraced statement, invented interface) are cheaper to catch while
  drafting than after the spec is presented as final.

## Quality checklist

Use this as the final gate before presenting a spec as complete:

- [ ] The target Feature was confirmed approved before drafting began.
- [ ] All Template fields are populated, in order, with no field silently skipped.
- [ ] Every requirement, subsystem, interface, and ADR named traces to an approved upstream
      artifact — none invented.
- [ ] No code, schema, API shape, or algorithm appears unless an approved architecture document or
      ADR already commits to it.
- [ ] Every genuine ambiguity is recorded as an Open Question with a stated reason and resolution
      path — none silently resolved.
- [ ] The Feature Catalog (or `DOM-xxx`/`ADS-xxx`) entry itself was not modified.
- [ ] If this repository's existing `docs/features/FS-1xx-*.md` convention applies instead of a
      Feature Catalog, that distinction is stated explicitly at the top of the new spec or its
      index entry.

## Success criteria

The specification is successful when:

1. **Traceability** — every field in the spec can be traced back to a cited Feature Catalog entry,
   requirement, architecture section, interface, or ADR — never to unstated judgment.
2. **Completeness** — every `Included Requirement` the Feature owns is accounted for in
   `Requirements Implemented`, and every workflow has a matching behavior contract.
3. **Honesty about gaps** — every ambiguity the upstream artifacts don't resolve is recorded as an
   Open Question, not papered over with an invented answer.
4. **Implementation-readiness without implementation detail** — a reader can start writing an
   Implementation Package directly from this spec's System Behaviour, Subsystem Responsibilities,
   Interfaces Used, and Acceptance Criteria sections, without needing to re-derive design decisions
   themselves, and without the spec having made any of those decisions for them prematurely.
5. **Non-interference** — the approved Feature (catalog entry or `DOM-xxx`/`ADS-xxx` source) is
   unchanged; this skill only adds a new, more detailed artifact downstream of it.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 06 — Feature Specification** of the documentation-driven-development pipeline
(see [`.claude/skills/README.md`](../README.md); stages run in numeric order, and
`00-pipeline-status` reports where the project currently stands). Upstream:
`05-feature-decomposition`. Downstream: `07-implementation-planning`.

End **every** invocation — new spec, spec update, or blocked stop — with a chat summary containing
exactly these three parts:

1. **What changed** — the spec(s) produced or updated (paths), and the index entry added/updated.
2. **Recommendations** — every Open Question the spec surfaced, with its owning upstream skill
   (`03-architecture-design-synthesis` for architecture/interface gaps, `04-requirements-engineering`
   for requirement gaps, `02-research-*` for domain-knowledge gaps), plus any mis-scoping finding
   to report to `05-feature-decomposition`'s catalog owner.
3. **Next step** — say explicitly what to run next and why: if Open Questions block
   implementation-readiness, route them upstream first and re-invoke this skill to close them;
   otherwise advance to `07-implementation-planning` to convert this spec into Implementation
   Package(s) — or, if more features in the current release bucket still need specs, re-invoke this
   skill for the next one and name it.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
