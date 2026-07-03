---
name: 05-feature-decomposition
description: Transform an approved requirements baseline (docs/research/, docs/architecture/, docs/requirements/ — Functional Requirements, Non-Functional Requirements, ICD, Traceability Matrix, ADRs) into an implementable Release Plan, Epic Catalog, Feature Catalog, Feature Dependency Graph, and Feature Review under docs/features/. Use when asked to "decompose the requirements into features," "build a feature catalog," "group requirements into epics," "plan releases/MVP/prototype scope," "build a feature dependency graph," or to bridge an approved systems-engineering baseline into software-engineering-sized implementation units. This skill performs no new research, no architecture redesign, no requirements authoring/editing, no implementation packages, and no code — it is a pure organization-and-planning step between an approved requirements baseline and downstream Feature Specifications (FS-xxx)/implementation. Do not use it to originate requirements (that belongs to requirements-engineering) or to make architecture decisions (that belongs to architecture-design-synthesis).
---

# Feature Decomposition

Turns an **approved requirements baseline** into an **implementable Release Plan, Epic Catalog,
Feature Catalog, Feature Dependency Graph, and Feature Review**. This skill sits strictly
downstream of research, architecture, and requirements work, and strictly upstream of Feature
Specifications (`FS-xxx`) and implementation. It is the bridge between Systems Engineering
("what must the system do") and Software Engineering ("what do we build first, and in what
order"). It does not do either neighbor's job.

## What this is for (and what it is not)

This skill answers one question: *given an approved set of requirements, what is the smallest set
of cohesive, independently-implementable units that cover all of them, how do those units group
into epics, how do they depend on each other, and in what order should they ship?*

It SHALL NOT:

- **Perform new research.** If a grouping decision seems to need a fact not already in the input
  documents, that is a gap to report in `05-feature-review.md`, not a fact to invent or look up.
- **Redesign the architecture.** Subsystem and interface boundaries are inputs, not decisions this
  skill makes. If a Feature's natural boundary doesn't match an existing subsystem boundary,
  report the mismatch — do not quietly redraw the architecture to make the Feature look cleaner.
- **Create new requirements.** Every `Included Requirement` cited in a Feature must already exist
  as an FR/NFR ID in `docs/requirements/`. A capability gap discovered during decomposition is a
  **Missing Feature / unassigned requirement** finding for `05-feature-review.md`, never a license
  to draft a new FR to fill the slot.
- **Modify approved requirements.** This skill reads `docs/requirements/` and never edits it. A
  requirement that looks wrong, ambiguous, or miscategorized is a finding to report upstream, not
  something to silently reinterpret while grouping it.
- **Generate implementation packages.** No `IMP-xxx`, no task breakdowns, no sprint plans, no
  effort estimates in story points or hours. "Complexity" and "Risk" in the Feature Template are
  qualitative planning signals, not estimates.
- **Write code.** No schemas-as-code, no API stubs, no scaffolding. This skill's output is
  entirely organizational documentation.

It SHALL organize existing approved requirements into logical, cohesive implementation units —
nothing more, nothing less.

It treats the following as **authoritative inputs**, never as something it edits or adds to:

- `docs/research/` — grounding facts; read for context on *why* a requirement exists, never a
  source of new facts to add.
- `docs/architecture/` — the architecture ladder (vision, ConOps, system context, architecture,
  domain model, ADRs, ICD/API spec where authored). Subsystem and interface boundaries here are
  load-bearing inputs to Feature/Epic boundary decisions.
- `docs/requirements/` — the Functional Requirements, Non-Functional Requirements, ICD, and
  Traceability Matrix. This is the primary material being decomposed.

**If the input documents conflict with each other, or a requirement has no defensible home in any
Feature, report it in `05-feature-review.md` — do not resolve it unilaterally.** Resolving a real
upstream conflict or gap is a decision for whoever owns the requirements/architecture, not
something this skill should paper over while organizing.

## Activation criteria

Invoke this skill when:

- The user asks to decompose, organize, or group an **approved** requirements baseline into
  features, epics, or a release plan.
- The user asks for a feature catalog, epic catalog, feature dependency graph, or release plan to
  be built or refreshed from `docs/requirements/`.
- The user asks "what's the implementation order," "what can be built in parallel," "what's on
  the critical path," or "what should be in the MVP/prototype/Release 1" for an existing
  requirements baseline.
- The user asks to review an existing feature catalog for sizing, duplication, gaps, or
  double-assignment.

Do **not** invoke this skill when:

- No `docs/requirements/` baseline exists yet, or it has not been approved/baselined — run
  `04-requirements-engineering` first.
- The request is to write or revise architecture, ADRs, or requirements themselves — those belong
  to `03-architecture-design-synthesis` / `04-requirements-engineering`.
- The request is to write a Feature Specification (`FS-xxx`) body, an implementation package, or
  code for a single already-identified feature — that is downstream of this skill's output, not
  this skill's job.

## Inputs

Read, in this order, before grouping anything:

| Path | Role |
|---|---|
| `docs/research/` | Encyclopedia / grounding facts — context for *why*, never a source of new capabilities. |
| `docs/architecture/` | Vision, ConOps, System Context, Architecture, Domain Model, ADRs, and (where authored) Data Model / UI Architecture / API Specification. Subsystem decomposition and interface list are the primary structural inputs for Epic and Feature boundaries. |
| `docs/requirements/` | Functional Requirements, Non-Functional Requirements, ICD, Requirements Traceability Matrix — the material being decomposed. Every Feature's `Included Requirements` must trace here. |

If a project's actual layout differs from these three top-level paths, adapt the *reading*, not
the *output structure* — the five deliverables below are fixed regardless of how the inputs are
organized. Record the mapping used at the top of `05-feature-review.md` so a reviewer can audit
it.

**Before grouping anything, confirm the baseline is approved.** If `docs/requirements/` carries an
explicit `Status: Draft` marker with no recorded approval, or a sibling gate review (e.g. a
requirements-baseline review) has not reached `APPROVED FOR FEATURE DECOMPOSITION` or equivalent,
stop and surface that to the user before proceeding — decomposing a moving target produces a
Feature Catalog that will need rework the moment the baseline changes underneath it.

## Outputs

Always exactly these five files, in this order, under `docs/features/`:

1. `docs/features/01-release-plan.md`
2. `docs/features/02-epic-catalog.md`
3. `docs/features/03-feature-catalog.md`
4. `docs/features/04-feature-dependency-graph.md`
5. `docs/features/05-feature-review.md`

Create `docs/features/INDEX.md` pointing at all five if the project has an `INDEX.md` convention
for other doc directories (check `docs/INDEX.md` or `docs/*/INDEX.md` for the local pattern before
deciding whether to add one).

**Write order matters but differs from read order.** Although the files are numbered
release-plan-first (so a reader opens the highest-altitude document first), *produce* them in the
dependency order below — Steps 1→4 build the Feature Catalog and its graph before Step 4's release
assignment, since you cannot sequence releases for features that don't exist yet or whose
dependencies are unknown:

```
Step 1 (Features)  →  03-feature-catalog.md  (draft)
Step 2 (Epics)      →  02-epic-catalog.md
Step 3 (Dependencies) → 04-feature-dependency-graph.md
Step 4 (Releases)   →  01-release-plan.md
Step 5 (Review)      →  05-feature-review.md  (reviews 02-04, may prompt edits to 03's draft)
```

Write all five to disk only once Step 5 is complete and any review-driven tightening of the
Feature Catalog has been applied — but never let Step 5's *findings* silently rewrite Features the
review itself flags as wrong; see Step 5 below.

## Workflow

Work the five steps in order. Each step's output is an input to the next.

### Step 0 — Read the inputs and build a requirement inventory

Before drafting a single Feature, read every approved document in `docs/research/`,
`docs/architecture/`, and `docs/requirements/`. While reading, build a working inventory (your own
notes, not a deliverable) of:

- **Every Functional Requirement ID** in the baseline (`FR-xxxx` or the project's equivalent),
  with its stated subsystem/interface affiliations.
- **Every subsystem and interface** named in the architecture ladder and ICD — these are the
  structural seams Feature boundaries should align with per the Quality Rules below.
- **Every ADR** that constrains how a capability may be implemented.
- Any requirement that appears to have **no clean home** in an obvious grouping — flag it now so
  Step 1 doesn't quietly force-fit it.

This inventory is what makes Step 1 derivation instead of invention, and it is what Step 5 checks
its "every requirement assigned exactly once" rule against.

### Step 1 — Identify Implementation Capabilities → `03-feature-catalog.md` (draft)

Group related requirements into logical Features. A Feature represents **one coherent
user-visible capability or one internally complete system capability** — not an arbitrary slice
and not a catch-all.

Sizing discipline:

- **Maximize cohesion, minimize coupling.** Requirements that change together, are verified
  together, and serve one stakeholder need belong in one Feature. Requirements that merely touch
  the same subsystem but serve unrelated needs do not.
- **Do not size arbitrarily.** A Feature should be the *natural* unit implied by the requirements'
  own grouping (their hierarchy, their shared subsystem/interface citations, their shared ADRs) —
  not padded to hit a target count, and not split just to produce more rows in the catalog.
- **Feature boundaries should align with subsystem boundaries** wherever the requirements
  naturally support it (Quality Rules, below). Where a Feature must legitimately straddle two
  subsystems, say so explicitly in that Feature's Description rather than leaving it implicit.

Use IDs `FS-xxxx` (4-digit, gapped numbering — `FS-1000`, `FS-1100`, `FS-1200`, … — so related
Features can be inserted later without renumbering). Group by the top-level capability area the
requirements already cluster around (e.g. the `FR-1xxx`/`FR-2xxx`/… groupings in the requirements
baseline are a strong starting signal for where `FS-xxxx` boundaries should fall).

For each Feature, populate the full **Feature Template** (below) before moving to the next.

### Step 2 — Create Epics → `02-epic-catalog.md`

Group Features into Epics — the next altitude up. An Epic is a thematic capability area large
enough to plan and staff around, but not so broad it loses meaning (e.g. "Simulation Engine,"
"Scenario Engine," "Exercise Authoring," "Visualization," "AI," "Networking," "Persistence,"
"Administration" — adapt the actual set to the project's own architecture ladder rather than
forcing this exact list).

Each Epic entry includes:

| Field | Content |
|---|---|
| **Epic ID** | `EP-xxxx` |
| **Title** | |
| **Purpose** | What capability area this Epic represents, and why it's a coherent grouping |
| **Features Included** | List of `FS-xxxx` IDs (every included Feature, no omissions) |
| **Subsystems** | Architecture subsystems this Epic's Features touch |
| **Estimated Scope** | Qualitative — Small/Medium/Large/Very Large, with the reasoning, never a numeric estimate |
| **Risks** | Epic-level risk themes that recur across its Features |
| **Dependencies** | Other Epic IDs this Epic depends on |

**Every Feature shall belong to exactly one Epic** (Quality Rules, below) — if a Feature seems to
belong to two, that is a signal the Feature itself is mis-scoped (split it) or the Epic boundaries
are wrong (report it), not a reason to list it twice.

### Step 3 — Dependency Analysis → `04-feature-dependency-graph.md`

Analyze, across the full Feature Catalog:

- **Feature dependencies** — does Feature A's behavior presuppose Feature B existing first
  (per each Feature's own `Dependencies` field from the Template)?
- **Interface dependencies** — do two Features share an ICD interface where one is necessarily
  upstream (e.g. a producer interface before its consumer)?
- **Architectural dependencies** — does a subsystem's own dependency graph (from
  `docs/architecture/`) impose an ordering the Feature graph must respect?
- **Data ownership** — does one Feature own data another Feature reads/writes, implying the owner
  must exist first?

From that analysis, identify and document explicitly:

- **Critical path** — the longest dependency chain; Features on it are schedule-determining.
- **Blocking Features** — Features with unusually high fan-out (many other Features depend on
  them) — these are the highest-leverage early targets.
- **Parallel development opportunities** — Feature sets with no dependency edges between them,
  safe to build concurrently.
- **Circular dependencies** — if found, this is a **Critical** finding: report it in
  `05-feature-review.md` with the exact cycle (e.g. `FS-1200 → FS-1450 → FS-1210 → FS-1200`) and
  recommend which edge is spurious or which Feature needs re-scoping to break the cycle. Do not
  silently break the cycle yourself by deleting or reordering a dependency — that is a decision
  for whoever owns the affected Features.

Produce **Mermaid dependency diagrams** (`graph TD` or `graph LR`) as the primary artifact of this
file — at minimum one diagram for the whole catalog (acceptable to split into per-Epic diagrams if
the whole-catalog graph is too dense to read), plus a written summary of the critical path,
blocking Features, and parallel opportunities above the diagram(s).

### Step 4 — Release Planning → `01-release-plan.md`

Assign **every** Feature to exactly one of: **Prototype**, **MVP**, **Release 1**, **Release 2**,
**Future**. For each assignment, **document why** — the reasoning must cite at least one of: the
Feature's `User Value`/`Technical Value`, its position in the dependency graph (Step 3), its
`Risk`/`Complexity`, or an explicit project constraint. A release plan with unjustified bucket
assignments is not acceptable output.

Across the whole plan, identify and call out explicitly (as labeled lists or a summary table, not
buried in prose):

- **Highest Value** Features
- **Highest Risk** Features
- **Foundational** Features (on the critical path, or blocking per Step 3)
- **Optional** Features (no other Feature depends on them; deferrable without blocking anything)
- **Deferred** Features (explicitly `Future`-bucketed, with the reason recorded)

A Feature's bucket assignment must be consistent with Step 3's dependency graph: a Feature cannot
be scheduled in an earlier release than a Feature it depends on. If the natural value/risk
prioritization would require that, treat it as a finding for `05-feature-review.md` ("Feature
X is high-value but blocked by lower-priority Feature Y — re-sequence or re-scope"), not something
to resolve by quietly ignoring the dependency.

### Step 5 — Feature Review → `05-feature-review.md`

Review the completed Feature Catalog (and its Epic grouping and dependency graph) for:

- **Features too large** — a Feature whose `Included Requirements` spans multiple unrelated
  stakeholder needs or multiple subsystems without an explicit cross-subsystem justification.
- **Features too small** — a Feature that is a single requirement with no independent
  user/technical value of its own, that would be more cohesive merged into a sibling.
- **Duplicate Features** — two Features covering substantially the same requirement set.
- **Missing Features** — a requirement, subsystem, or interface with no Feature home at all.
- **Requirements not assigned** — any `FR-xxxx`/`NFR-xxxx` ID from Step 0's inventory absent from
  every Feature's `Included Requirements`.
- **Requirements assigned twice** — any requirement ID appearing in more than one Feature's
  `Included Requirements` (a requirement may be *referenced* by a related Feature, but it is
  *included*, i.e. owned, by exactly one).
- **Architectural inconsistencies** — a Feature/Epic boundary that contradicts the architecture's
  subsystem decomposition or an ADR.

Structure findings as one row per finding: `Finding type | Feature/Epic/Requirement IDs involved |
Description | Severity | Recommendation`, using the same Critical/High/Medium/Low severity scale
convention as the project's other review documents (check `docs/reviews/` for the local
convention before inventing a new scale).

**Recommend improvements. Do not modify Features automatically.** This step is read-only with
respect to `02-epic-catalog.md`, `03-feature-catalog.md`, and `04-feature-dependency-graph.md`: it
reports, it does not edit them. If the user asks for fixes to be applied after reading the review,
that is an explicit, separate follow-up action — re-run the affected step(s), not a silent rewrite
folded into the review pass itself.

## Feature Template

Every Feature in `03-feature-catalog.md` carries this fixed field set — an empty-looking field
(e.g. "Dependencies: None") is informative; a missing field is not:

| Field | Content |
|---|---|
| **Feature ID** | `FS-xxxx` |
| **Title** | Short, action-oriented, unique |
| **Purpose** | The single stakeholder or system need this Feature exists to satisfy |
| **Description** | What the Feature does, in behavior terms — no implementation detail |
| **Scope** | The boundary of what this Feature covers, stated positively |
| **Included Requirements** | `FR-xxxx`/`NFR-xxxx` IDs this Feature owns (each must appear in exactly one Feature project-wide — Quality Rules) |
| **Excluded Requirements** | Adjacent requirement IDs a reader might expect here but that belong to a different Feature — state where they actually live |
| **Dependencies** | Other `FS-xxxx` IDs this Feature requires to exist first |
| **Dependent Features** | Other `FS-xxxx` IDs that require this Feature first (the inverse edge — keep both directions in sync) |
| **Affected Subsystems** | From `docs/architecture/` |
| **Affected Interfaces** | ICD `INT-xxxx` IDs (or project equivalent) |
| **Related ADRs** | ADR IDs this Feature must remain consistent with |
| **User Value** | Qualitative — why a stakeholder cares, citing the requirements' own Rationale/Priority fields, not invented |
| **Technical Value** | Qualitative — what this Feature unblocks or simplifies for the system, independent of end-user visibility |
| **Complexity** | Qualitative (Low/Medium/High/Very High) with the reasoning — never a numeric estimate |
| **Risk** | What could go wrong implementing this Feature, and why (technical risk, dependency risk, ambiguity risk) |
| **Suggested Verification Strategy** | How this Feature's completion would be checked, informed by but not identical to its included requirements' own Verification Method fields |
| **Open Questions** | Anything Step 0–5 surfaced about this Feature that isn't yet resolved |

## Quality Rules

These are invariants the Feature Review (Step 5) checks, and the whole catalog must satisfy
before being considered complete:

- **Every Functional Requirement shall belong to exactly one Feature.**
- **Every Feature shall belong to exactly one Epic.**
- **Every Feature shall map to one planned release** (Prototype/MVP/Release 1/Release 2/Future).
- **Features should be independently implementable whenever practical** — a Feature with an
  unavoidable hard dependency must say so explicitly in `Dependencies`, not hide the coupling.
- **Feature boundaries should align with subsystem boundaries** — deviations must be justified in
  the Feature's own `Description`, not left implicit.
- **Maintain complete traceability back to** Requirements, Architecture, ICDs, and ADRs — every
  Feature's `Included Requirements`, `Affected Subsystems`, `Affected Interfaces`, and `Related
  ADRs` fields are how that traceability is carried forward; an empty field where a real
  relationship exists is a defect.

## Quality gate (before calling the decomposition done)

- [ ] The requirements baseline read was confirmed approved/baselined before grouping began.
- [ ] Every Feature has all Feature Template fields populated (or explicitly `None` with a reason).
- [ ] Every Epic has all Epic fields populated, including a complete `Features Included` list.
- [ ] No `FR-xxxx`/`NFR-xxxx` ID is missing from every Feature, and none appears in more than one
      Feature's `Included Requirements` (Step 5 confirms this against Step 0's inventory).
- [ ] The dependency graph contains no unresolved circular dependency — any cycle found is reported
      in the Review, not silently broken.
- [ ] Every Feature has exactly one release-plan bucket, and no Feature is scheduled before a
      Feature it depends on.
- [ ] The Mermaid dependency diagram(s) render and reflect the same edges stated in prose.
- [ ] The Review actually reviewed the final 02–04 content, not a stale earlier draft, and applies
      no fixes itself.
- [ ] Nothing in any of the five documents originates a new requirement, a new architectural
      decision, an implementation package, or a line of code.

## Examples

**"Decompose the approved requirements baseline into features and a release plan."**
Confirm the baseline's approval status first. Run Steps 0–5 in full, producing all five documents
under `docs/features/` for the first time.

**"We added FR-3520 (Role Assignment scoping) to the requirements baseline — update the feature
catalog."**
Re-run Step 0 against the delta only. Identify which existing Feature should own FR-3520 (most
likely a sibling of FR-3510's existing Feature, per the requirements baseline's own cross-reference
pattern) — or, if it warrants a new Feature, add one with a gapped `FS-xxxx` ID. Update that
Feature's entry in `03-feature-catalog.md`, its Epic's `Features Included` list in
`02-epic-catalog.md`, the dependency graph if the new/changed Feature has new edges, and the
release plan's bucket assignment for it. Do not regenerate the other, unaffected Features from
scratch.

**"Why is FS-2300 in Release 2 and not MVP?"**
Answer from FS-2300's own entry in `01-release-plan.md`'s documented reasoning — this is a lookup,
not a reason to re-run the workflow.

**"This Feature Catalog looks unbalanced — some features are huge, some are tiny."**
Run Step 5 (Feature Review) against the existing catalog without re-running Steps 1–4. Report the
oversized/undersized Features with a recommendation each. Do not split or merge Features in the
same pass unless the user explicitly asks for the recommendations to be applied.

**"The architecture doesn't assign a subsystem to this requirement, but it obviously belongs to
the engine."**
Do not assign a subsystem yourself in the Feature's `Affected Subsystems` field. Note the gap in
that Feature's `Open Questions` and flag it as a missing-architecture-detail finding in
`05-feature-review.md` for the architecture owner to resolve.

## Limitations

- This skill cannot produce a Feature Catalog better-organized than the requirements baseline it
  reads — a thin, ambiguous, or poorly-traced baseline yields a thin catalog plus a long
  `05-feature-review.md` findings list (correctly), not a polished catalog papering over the gaps.
- It does not adjudicate conflicts or gaps it finds — someone with authority over the requirements
  or architecture must resolve a reported issue before the affected Feature(s) can be finalized.
- It does not estimate effort, cost, or schedule duration in any numeric unit — `Complexity` and
  `Risk` are qualitative planning signals only, by design, since this skill has no implementation
  history or team-velocity data to ground a number in.
- It does not know about, and must not guess at, downstream artifacts (Feature Specifications,
  implementation packages, tests) that don't exist yet beyond what `docs/requirements/`'s own
  traceability matrix already states.
- It is not a substitute for architecture or requirements review: a well-organized Feature Catalog
  can still faithfully decompose a requirements baseline that has its own unresolved defects.
  "Well-organized" and "correct underneath" are not the same claim — if the upstream review hasn't
  cleared the baseline, say so rather than decomposing around the gap.

## Recommended usage

- Run this skill **once per stable requirements baseline**, then maintain its outputs
  incrementally as the baseline changes (see the FR-3520 example above) rather than regenerating
  from scratch on every small requirements edit.
- Run Step 5 (Feature Review) **standalone**, without re-running Steps 1–4, whenever the catalog
  needs a health check but the requirements baseline itself hasn't changed — this is the cheapest
  way to catch drift (e.g. a Feature that grew past its original scope through ad-hoc edits).
- Treat `04-feature-dependency-graph.md`'s critical path and blocking-Feature findings as direct
  input to sprint/milestone planning conversations, but keep that planning conversation itself
  outside this skill's output — the release plan states *which bucket*, not *which sprint*.
- When a project already has its own architecture ladder with subsystem decomposition baked in (as
  `03-architecture-design-synthesis` produces in GDS-03), always prefer aligning Epic and Feature
  boundaries to that decomposition over inventing a parallel one — a second, uncoordinated
  capability taxonomy is exactly the kind of architectural inconsistency Step 5 is meant to catch.

## Recommended repository layout

```
docs/
├── research/                          # input — encyclopedia / grounding (read-only to this skill)
├── architecture/                      # input — vision/ConOps/context/architecture/domain model/ADRs/ICD
│   └── adr/
├── requirements/                      # input — FR/NFR/ICD/traceability matrix (read-only to this skill)
└── features/                          # output — this skill's sole write scope
    ├── INDEX.md                       # optional, if the project uses per-directory indexes
    ├── 01-release-plan.md
    ├── 02-epic-catalog.md
    ├── 03-feature-catalog.md
    ├── 04-feature-dependency-graph.md
    └── 05-feature-review.md
```

If a project's actual paths differ from `docs/research/` / `docs/architecture/` /
`docs/requirements/` (e.g. a separate `docs/design/` for pre-ladder architecture documents, or an
ICD living outside `docs/architecture/`), treat the names above as roles to map onto whatever the
project's `docs/INDEX.md` actually shows, and record the mapping used at the top of
`05-feature-review.md` so a reader can audit it. The five output filenames and `docs/features/` as
the write target stay fixed regardless.

## Gotchas

- **Check for a pre-existing `docs/features/` convention before writing anything.** In *this*
  repository (`ZabSpaceExercise`), `docs/features/` already exists and is populated —
  `feature-index.md` plus full `FS-101-mission-planning.md`-style documents — governed by a
  *different* chain documented in `docs/master/MSTR-005-documentation-map.md`: `docs/research/` +
  domain framework → `ADS-xxx` (Architecture Design Synthesis, produced by the
  `03-architecture-design-synthesis` skill) → `FS-xxx` (a **full single-capability Feature
  Specification document**, the actual implementable spec) → `IMP-xxx` → code → tests. Those
  `FS-xxx` files are not this skill's catalog rows — they are downstream artifacts this skill's
  Feature Catalog entries point *forward* to, written later by a separate workflow.
  Writing this skill's five outputs into `docs/features/` in this repo would collide both on
  directory and on the `FS-xxxx` ID prefix with that existing, unrelated numbering
  (`FS-101`...`FS-301`). **Do not silently overwrite or reuse those IDs.** In this repo specifically:
  use a different output directory (e.g. `docs/feature-planning/` or `docs/decomposition/`) and a
  different catalog-row ID prefix (e.g. `FEAT-xxxx`) to keep this skill's planning-level catalog
  rows distinct from MSTR-005's full `FS-xxx` specification documents, and say so explicitly in
  `05-feature-review.md`'s mapping note. Treat this as the general rule, not a one-off: in *any*
  project, before defaulting to `docs/features/`/`FS-xxxx`, grep for an existing `docs/features/`
  directory and an existing `FS-` ID convention, and if one already names full specification
  documents (rather than catalog rows), pick non-colliding output names instead of overloading it.
- **Catalog rows are not the same artifact as a Feature Specification.** Even in a project with no
  naming collision, keep this distinction explicit in the Feature Template's `Title`/`Description`:
  this skill's Feature Catalog entry is a planning-grain summary that downstream work expands into
  a full Feature Specification — don't let the catalog entry grow into a spec body, and don't let
  a reader mistake one for the other.

## Best practices

- **Let the requirements' own hierarchy lead Feature boundaries.** A baseline that already groups
  `FR-1xxx`/`FR-2xxx`/… by capability area has done half of Step 1's work already — don't redraw
  those lines without a concrete cohesion/coupling reason.
- **Write `Dependencies` and `Dependent Features` together, every time.** A one-directional edge
  recorded on only one Feature is a traceability defect waiting to be found in Step 5 — update
  both Features in the same edit.
- **Prefer fewer, well-justified Epics over many thin ones.** An Epic that exists to hold exactly
  one Feature is a sign the Epic layer added no organizing value.
- **Keep the Mermaid diagram readable.** If a single `graph TD` for the whole catalog becomes
  illegible past roughly 25–30 nodes, split into per-Epic diagrams plus one cross-Epic summary
  diagram showing only inter-Epic edges, rather than producing one diagram no one will read.
- **Justify every release-bucket assignment in writing, not by table position alone.** A reader
  should be able to find the "why" for any Feature's bucket without cross-referencing three other
  documents.
- **Run Step 5 honestly.** A Feature Review with zero findings on a first pass is a signal to
  re-check the review, not a signal the catalog is unusually good — some amount of
  too-large/too-small/unassigned friction is the expected state of a first decomposition pass.

## Quality checklist

Use this as the final gate before presenting the decomposition as complete — distinct from, and a
superset-summary of, the per-step "Quality gate" above:

- [ ] All five `docs/features/` documents exist, in the fixed structure, with no step skipped.
- [ ] Every Feature traces back to Requirements, Architecture, ICDs, and ADRs, and forward through
      its Epic to a release bucket.
- [ ] No new requirement, architectural decision, implementation package, or code was introduced
      anywhere in the five documents.
- [ ] Every finding in `05-feature-review.md` has a clear recommendation, and none has been
      silently auto-applied to `02`–`04`.
- [ ] A reader unfamiliar with this session can open `01-release-plan.md` alone and understand
      *what ships when and why*, without needing to reconstruct reasoning from the other four
      documents.

## Success criteria

The decomposition is successful when:

1. **Completeness** — every approved FR/NFR in `docs/requirements/` is owned by exactly one
   Feature, and every Feature belongs to exactly one Epic and exactly one release bucket.
2. **Traceability** — any Feature, Epic, or release-bucket decision can be traced back to a cited
   requirement, architecture section, interface, or ADR — never to unstated judgment.
3. **Honesty about gaps** — every duplication, oversized/undersized Feature, unassigned
   requirement, double-assigned requirement, missing Feature, or architectural inconsistency found
   during Step 5 is reported, not hidden or silently fixed.
4. **Actionability** — a reader can pick `04-feature-dependency-graph.md`'s critical path and
   `01-release-plan.md`'s bucket assignments and start sequencing real implementation work (writing
   `FS-xxxx` Feature Specifications next) without needing to re-derive the grouping logic
   themselves.
5. **Stability under change** — when one requirement changes, only the directly-affected Feature
   (and its Epic/graph/release entries) need updating — the rest of the catalog remains valid
   without a full regeneration.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 05 — Feature Decomposition** of the documentation-driven-development pipeline
(see [`.claude/skills/README.md`](../README.md); stages run in numeric order, and
`00-pipeline-manager` reports where the project currently stands). Upstream:
`04-requirements-engineering`. Downstream: `06-feature-specification`.

End **every** invocation — full decomposition, delta update, standalone Feature Review, or blocked
stop — with a chat summary containing exactly these three parts:

1. **What changed** — which of the five deliverables were produced or updated (paths), and the
   headline numbers (features, epics, release buckets, critical-path length).
2. **Recommendations** — the Feature Review's key findings (unassigned/double-assigned
   requirements, oversized features, dependency cycles) and who owns each; anything requiring a
   requirements or architecture change goes upstream to `04-requirements-engineering` /
   `03-architecture-design-synthesis`.
3. **Next step** — say explicitly what to run next and why: if the Review surfaced Critical
   findings, resolve them first and re-run the affected steps; otherwise advance to
   `06-feature-specification`, naming the specific catalog entry to specify next (the
   highest-priority release bucket's first unspecified, unblocked feature per
   `01-release-plan.md` and the dependency graph).

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
