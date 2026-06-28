---
name: requirements-engineering
description: Transform an approved architecture baseline (research/encyclopedia, Concept of Operations, System Context, Architecture, Domain Model, ADRs) into a traceable requirements baseline under docs/requirements/ — hierarchical Functional Requirements (FR-xxxx), Non-Functional Requirements (NFR-xxxx), a Requirements Review report, and a Requirements Traceability Matrix. Use when asked to "derive requirements from the architecture," "write functional/non-functional requirements," "build a traceability matrix," "review the requirements for conflicts/gaps/duplicates," or to turn an approved design into an implementation-ready requirements set. This skill performs no new research, no architecture redesign, and no implementation — it is a pure derivation-and-bookkeeping step between an approved architecture and downstream feature/implementation planning. Do not use it to originate domain knowledge (that belongs to research skills) or to make architecture decisions (that belongs to architecture/design-synthesis skills).
---

# Requirements Engineering

Turns an **approved** architecture baseline into a **traceable requirements baseline**. This
skill sits strictly downstream of research and architecture work, and strictly upstream of
feature specs and implementation. It does not do either neighbor's job.

## What this is for (and what it is not)

This skill answers one question: *given what has already been researched and architected, what
must the system do, how well must it do it, and can every one of those statements be traced back
to a source and forward to a test?*

It SHALL NOT:

- **Perform new research.** If a requirement seems to need a fact that isn't in the input
  documents, that is a gap to report, not a fact to invent or look up.
- **Redesign the architecture.** If the architecture is wrong, ambiguous, or self-contradictory,
  report it in the review — do not patch it by writing around the problem in a requirement.
- **Implement code.** No code, no schemas-as-code, no API stubs. Requirements describe behavior,
  not implementation.
- **Invent features not supported by the approved documentation.** Every requirement in the
  baseline must trace to something already written down. Anything that doesn't trace goes to
  **Candidate Requirements**, explicitly excluded from the baseline, never silently promoted.

It treats the following as **authoritative inputs**, never as something it edits or adds to:

- Encyclopedia / research corpus
- Concept of Operations
- System Context
- Architecture
- Domain Model
- Architecture Decision Records (ADRs)

**If the input documents conflict with each other, report the conflict in the Requirements
Review — do not resolve it unilaterally.** Resolving a real architectural conflict is a decision
for whoever owns the architecture, not something this skill should do quietly while writing
requirements.

## Inputs

Read, in this order, before writing anything:

| Path | Role |
|---|---|
| `docs/research/` | Encyclopedia / grounding facts — *why* a requirement is true, never a source of new facts to add. |
| `docs/design/` | Concept of Operations, System Context, Architecture, Domain Model (or your project's equivalent names/locations for these). |
| `docs/architecture/adr/` | Architecture Decision Records — binding decisions a requirement must not contradict. |

If a project's actual layout differs (e.g. a combined `docs/architecture/` ladder instead of a
separate ConOps/Context/Domain Model set), adapt the *reading*, not the *output structure* —
the four deliverables below are fixed regardless of how the inputs are organized. Note the
mapping you used in the Requirements Review's front matter so a reviewer can audit it.

## Outputs

Always exactly these four files, in this order, under `docs/requirements/`:

1. `docs/requirements/01-functional-requirements.md`
2. `docs/requirements/02-non-functional-requirements.md`
3. `docs/requirements/03-requirements-review.md`
4. `docs/requirements/04-requirements-traceability-matrix.md`

Create `docs/requirements/INDEX.md` pointing at all four if the project has an `INDEX.md`
convention for other doc directories (check `docs/INDEX.md` or `docs/*/INDEX.md` for the local
pattern before deciding whether to add one).

## Workflow

Work the four steps in order. Each step's output is an input to the next — do not skip ahead to
the traceability matrix before the requirements it traces exist, and do not run the review on a
half-finished requirements set.

### Step 0 — Read the inputs and build a source map

Before drafting a single requirement, read every document in `docs/research/`, `docs/design/`,
and `docs/architecture/adr/`. While reading, keep a running list (in your own working notes, not
a deliverable) of:

- every distinct **capability** the ConOps/System Context implies the system must provide,
- every **entity and relationship** in the Domain Model,
- every **binding decision** in an ADR that constrains how a capability may be satisfied,
- anything that reads as a requirement but has **no traceable source** — flag for Candidate
  Requirements later, don't lose track of it.

This map is what makes Step 1 derivation instead of invention.

### Step 1 — Generate Functional Requirements (`01-functional-requirements.md`)

Build a **hierarchical** specification. Use a 4-digit numbering scheme that nests by leading
digit position, matching the granularity of decomposition:

```
FR-1000   Top-level capability (traces directly to a ConOps mission/capability statement)
FR-1100     Major function within that capability
FR-1110       Sub-function
FR-1111         Atomic, independently testable requirement (the leaf — most FRs end here)
```

Leave gaps in the numbering (`1000`, `1100`, `1200`, …) so related requirements can be inserted
later without renumbering the whole tree.

**Every leaf requirement** (and any non-leaf used as a grouping node) carries this fixed field
set — do not drop fields because they feel redundant for a given requirement; an empty-looking
field (e.g. "Dependencies: None") is informative, a missing field is not:

| Field | Content |
|---|---|
| **ID** | `FR-xxxx` |
| **Title** | Short, action-oriented, unique |
| **Description** | One unambiguous statement of required behavior — see the writing rules below |
| **Rationale** | Why this exists — cite the source statement, not just the document |
| **Priority** | MoSCoW (Must/Should/Could/Won't) or a project's existing scale — state which scale you used once, at the top of the document |
| **Inputs** | What the function consumes |
| **Outputs** | What the function produces |
| **Preconditions** | State required before the requirement applies |
| **Postconditions** | State guaranteed after it's satisfied |
| **Acceptance Criteria** | Concrete, checkable conditions — written so a tester with no design context could verify pass/fail |
| **Dependencies** | Other FR/NFR IDs this one presupposes |
| **Verification Method** | Test / Demonstration / Analysis / Inspection (pick one; justify Analysis/Inspection if used instead of Test) |
| **Source Documents** | Exact file + section/heading cited |
| **Related ADRs** | ADR IDs this requirement must remain consistent with |
| **Notes** | Open concerns, assumptions made explicit, anything a reviewer should know |

**Writing rules** (apply to every requirement, FR and NFR alike):

- **Atomic** — one behavior per requirement. If a sentence has an "and" joining two independently
  testable things, split it into two requirements and cross-reference them in Dependencies.
- **Unambiguous** — no "should generally," "as appropriate," "where possible." If the source
  document is itself vague, say so in Notes rather than quietly sharpening it into something the
  source didn't actually commit to.
- **Testable** — Acceptance Criteria must be checkable without consulting the requirement's own
  author.
- **Implementation independent** — describe observable behavior, not a class name, a data
  structure, or an algorithm. ("The system shall reject an order with no valid access window"
  not "the system shall raise `NoWindowError`.")
- **Consistent** — no requirement may contradict another FR, an NFR, or an ADR. A real
  contradiction is a Requirements Review finding, not something to paper over by adding caveats
  to one side.
- **Traceable** — Source Documents must name an actual section. "Implied by the architecture" is
  not a citation.
- **Complete** — every capability identified in Step 0's source map has at least one FR; if one
  doesn't, that's a gap for the Review, not a license to invent the missing requirement from
  general software-engineering judgment.

**Candidate Requirements.** End the document with a `## Candidate Requirements` section for
anything that reads like a requirement but cannot be traced to an input document — same field
set, but explicitly excluded from the numbered baseline and from the traceability matrix's
"baseline" rows (still listed in the matrix, marked `CANDIDATE — NOT BASELINED`, so the gap isn't
invisible). Never promote a candidate into the numbered tree within the same pass; that requires
the documentation gap to be closed first by whoever owns the missing input.

### Step 2 — Generate Non-Functional Requirements (`02-non-functional-requirements.md`)

Same ID discipline (`NFR-xxxx`, same field set as FRs, same writing rules) across these
categories — use them as section headings, in this order, and write `(none derivable from inputs
— see Candidate Requirements)` under any category the source documents simply don't address
rather than inventing one to fill the slot:

Performance · Reliability · Maintainability · Security · Scalability · Availability ·
Portability · Usability · Logging · Monitoring · Configuration · Data Integrity ·
Extensibility · Interoperability · Testability

NFRs are held to the same evidentiary bar as FRs: a number in an Acceptance Criterion ("99.9%
availability," "p95 < 200ms") must come from a source document, not from generic industry
convention. If the inputs don't specify a number, write the requirement qualitatively and flag
the missing target in Notes — do not manufacture a number to make the requirement look more
rigorous than the source material supports.

### Step 3 — Requirements Review (`03-requirements-review.md`)

Review the full FR + NFR set you just produced (plus Candidate Requirements) for:

- **Duplicates** — two requirements describing the same behavior under different IDs
- **Conflicts** — two requirements that cannot both be true; conflicts between a requirement and
  an ADR or architecture statement
- **Ambiguities** — anything that slipped past the Step 1/2 writing rules
- **Missing requirements** — a capability/quality attribute the source map (Step 0) implies but
  no FR/NFR covers
- **Impossible requirements** — physically or logically unsatisfiable as written, or unsatisfiable
  given a stated architectural constraint
- **Requirements that violate architecture** — contradicts the Architecture doc or an ADR
- **Requirements lacking verification** — no credible Verification Method / Acceptance Criteria
- **Requirements lacking traceability** — Source Documents empty, vague, or unverifiable

Structure the report as one finding per row: `Finding type | IDs involved | Description | Severity
| Recommendation`. State a recommendation for each finding (e.g. "split FR-1230 into two
requirements," "escalate conflict between FR-1410 and ADR-007 to architecture owner") — **do not
act on the recommendation yourself**. This document is read-only with respect to 01 and 02: it
reports, it does not edit them. If the user asks for fixes to be applied, that is an explicit,
separate follow-up action, not an implicit part of running the review.

### Step 4 — Traceability Matrix (`04-requirements-traceability-matrix.md`)

One row per FR and NFR (including Candidate Requirements, explicitly marked). Columns:

| Req ID | Title | Research Source | Architecture Section | ADR | Subsystem | Feature Spec | Implementation Package | Test |
|---|---|---|---|---|---|---|---|---|

Fill from what Steps 0-3 already established for the first three trace-back columns (Research
Source, Architecture Section, ADR). The last four columns point *forward* to artifacts that this
skill does not create (Subsystem ownership, a future `FS-xxx` Feature Spec, a future
implementation package, a future test) — write `UNASSIGNED` in any cell that can't yet be
filled. **Never invent a Feature Spec ID, subsystem name, or test name that doesn't exist yet** —
an `UNASSIGNED` cell is the correct, honest state for a requirement that hasn't reached that
stage of planning. A matrix with no `UNASSIGNED` cells on a fresh baseline is a sign something was
guessed, not a sign of thoroughness.

## Quality gate (before calling the baseline done)

- [ ] Every FR/NFR has all required fields populated (or explicitly `None` with a reason, never
      silently blank).
- [ ] Every leaf FR/NFR is atomic, unambiguous, testable, implementation-independent.
- [ ] Every numbered (non-candidate) requirement has a real Source Documents citation with a
      section, not just a document name.
- [ ] No requirement in the numbered baseline contradicts another requirement or an ADR; any that
      do are pulled to Candidate Requirements or flagged in the Review, not silently kept.
- [ ] The Review actually reviewed the final 01/02 content — not a stale earlier draft.
- [ ] The Review proposes fixes but applies none of them.
- [ ] The matrix has one row per FR/NFR including candidates, with `UNASSIGNED` used honestly
      rather than guessed values.
- [ ] Nothing in any of the four documents originates a new fact, a new architectural decision,
      or a line of implementation.

## Examples

**"Derive the requirements baseline from the approved architecture."**
Run Steps 0-4 in full, producing all four documents for the first time.

**"We added ADR-014 (switch to event sourcing) — update the requirements."**
Re-run Step 0 against the changed inputs (just the delta, not from scratch), identify which
existing FR/NFRs are now inconsistent with ADR-014, fix only those (not a wholesale rewrite), add
a dated changelog note at the top of `01-functional-requirements.md` and/or
`02-non-functional-requirements.md`, then re-run Step 3 focused on the changed area, and update
the affected rows of Step 4's matrix.

**"Why does FR-2200 exist?"**
Answer from FR-2200's own Rationale and Source Documents fields — this is a lookup, not a reason
to re-run the workflow.

**"The architecture doc doesn't say anything about retry behavior, but obviously it needs some."**
Do not write an NFR for it. Add it to Candidate Requirements with a Notes field stating plainly
that no input document addresses retry behavior, and flag it in the Review as a missing
requirement for the architecture owner to resolve.

## Limitations

- This skill cannot produce a requirement that traces to nothing — its output quality is a direct
  function of how complete and unambiguous the input architecture is. A thin or vague
  architecture baseline yields a thin requirements baseline plus a long Candidate Requirements /
  Review-findings list, which is the correct outcome, not a failure of this skill.
- It does not adjudicate conflicts it finds — someone with authority over the architecture must
  resolve a reported conflict before the affected requirements can be finalized.
- It does not know about, and must not guess at, downstream artifacts (Feature Specs,
  implementation packages, tests) that don't exist yet — those columns stay `UNASSIGNED` until a
  later skill or process fills them in.
- It is not a substitute for architecture review: a self-consistent requirements baseline can
  still faithfully reflect a bad architecture. "Internally consistent" and "correct" are not the
  same claim.

## Recommended repository layout

```
docs/
├── research/                       # input — encyclopedia / grounding (read-only to this skill)
├── design/                         # input — ConOps, System Context, Architecture, Domain Model
├── architecture/
│   └── adr/                        # input — Architecture Decision Records
└── requirements/                   # output — this skill's sole write scope
    ├── INDEX.md                    # optional, if the project uses per-directory indexes
    ├── 01-functional-requirements.md
    ├── 02-non-functional-requirements.md
    ├── 03-requirements-review.md
    └── 04-requirements-traceability-matrix.md
```

If a project's actual paths differ from `docs/research/` / `docs/design/` /
`docs/architecture/adr/` (as in this repository, where the architecture ladder lives under
`docs/architecture/GDS-*` and ADRs may not yet exist as a separate directory), treat the names
above as roles to map onto whatever the project's `docs/INDEX.md` actually shows, and record the
mapping used at the top of `03-requirements-review.md` so a reader can audit it. The four output
filenames and `docs/requirements/` as the write target stay fixed regardless.

## Gotchas

- Don't let Step 1/2 quietly become a design step. A requirement that names a class, a table
  schema, or an API shape has crossed into implementation — push it back to "what behavior is
  observable," not "how is it built."
- Don't let the Review's findings leak into edits of 01/02 in the same pass unless the user
  explicitly asks for fixes to be applied — review and remediation are separate, reviewable
  steps.
- Don't backfill a traceability cell with a plausible-sounding guess. `UNASSIGNED` is correct and
  expected for anything that depends on work this skill doesn't do.
- Don't treat "the architecture didn't mention it" as license to add an NFR from general best
  practice — that is exactly what Candidate Requirements exists for.
- If this skill is used in a project that already has its own GDS/ADS-style architecture ladder
  with FR/NFR sections baked into it (as `architecture-design-synthesis` does in this repository),
  check whether those sections are meant to be the authoritative input *for* this skill (treat
  them as part of `docs/design/`) rather than producing a second, competing FR/NFR set — name the
  relationship explicitly in `03-requirements-review.md` rather than leaving two unreconciled
  baselines in the repo.
