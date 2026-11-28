# MSTR-005 — Documentation Map

> **Document ID:** MSTR-005
> **Version:** 1.0
> **Status:** ♻️ Living (update whenever a directory or tier is added)
> **Dependencies:** MSTR-001
> **Referenced By:** `docs/INDEX.md`, `ROADMAP.md`, MSTR-006, all FS-*, all IMP-*
> **Produces:** the routing rules every new document must follow
> **Feature Mapping:** N/A — program-level
> **Related Topics:** > [`ROADMAP.md`](../../ROADMAP.md) (per-document completion tracker)

[↑ Docs index](../INDEX.md)

## 1. Purpose

This is the map of the *entire* `docs/` tree after the documentation-driven-development expansion —
both the pre-existing themes (`research/`, `training/`, `vignettes/`; the earlier build-specification
and design themes are retired into `architecture/`)
and the five new directories this expansion adds (`master/`, `features/`,
`implementation/`, `architecture/`, `scenarios/`). `docs/INDEX.md` is the live router; this
document is the rationale and the rule set for where a new document belongs. `ROADMAP.md` is the
per-document status tracker — this document answers "where does X go," `ROADMAP.md` answers "is X
done."

### 1a. Documentation principles

Carried over from the earlier documentation plan (retired 2026-11-10), which this document succeeds:

1. **Single-topic files a reader can take in whole.** A file is small enough (about 50 to 300
   lines) to be opened fully and read for one topic, not scrolled as a monolith.
2. **An index at every level.** A master `docs/INDEX.md` plus one `INDEX.md` per theme act as
   routers: read the index, then open exactly the module needed.
3. **Stable, descriptive filenames.** Files are named by topic; a numeric prefix only sets reading
   order within a theme.
4. **Themed directories.** Each theme is a directory with its own index.

## 2. Full directory tree

```
docs/
├── INDEX.md                      ← master router
│
├── master/                       ← NEW: MSTR-001..007, the stable program-defining documents
│   ├── MSTR-001-program-vision.md
│   ├── MSTR-002-architecture-principles.md
│   ├── MSTR-003-educational-philosophy.md
│   ├── MSTR-004-glossary.md
│   ├── MSTR-005-documentation-map.md         ← this file
│   ├── MSTR-006-governance-principles.md
│   └── MSTR-007-research-philosophy.md
│
├── research/                     ← EXPANDED: existing 01-07 doctrine/physics primers (unchanged)
│   │                                + NEW R1xx-R5xx encyclopedia tiers for coding-agent domain understanding
│   ├── INDEX.md
│   ├── 01-doctrine-western.md … 07-legal-norms-and-roe.md     (existing, unchanged)
│   ├── 10-sources-and-methodology.md                          (existing, unchanged)
│   └── encyclopedia/
│       ├── R100-index.md   R101…  (Space Operations Foundation)
│       ├── R200-index.md   R201…  (Decision Sciences)
│       ├── R300-index.md   R301…  (Military Analysis)
│       ├── R400-index.md   R401…  (Research Methods)
│       └── R500-index.md   R501…  (Future Operations)
│
├── features/                     ← NEW: FS-1xx..FS-3xx, capability specs (no implementation detail)
│   ├── feature-index.md
│   └── FS-101-mission-planning.md …
│
├── implementation/                ← IP-xxxx Implementation Packages, the Master Build Plan, verification reports
│   ├── 00-master-build-plan.md
│   └── packages/IP-1010-… .md
│
├── architecture/                  ← NEW: ADS-xxx Design Synthesis documents (the bridge from
│   │                                  Grounding+Research into a Feature Specification)
│   ├── INDEX.md
│   └── ADS-xxx-<slug>.md          ← one per capability cluster; ten fixed sections (§3a)
│
├── scenarios/                     ← NEW: scenario-design guidance distinct from the vignette *content* library
│   └── (how to design a vignette to hit a training/assessment objective; the vignette files themselves stay in vignettes/)
│
├── training/                      ← UNCHANGED: user-facing manual
├── vignettes/                     ← UNCHANGED: the 19-vignette content library + framework
└── manual/                        ← UNCHANGED: generated UI screenshots
```

## 3. How the new tree relates to the pre-existing themes

The expansion does **not** duplicate or replace existing content. Specifically:

- **The v1 build specification and design corpus are retired.** Their content was folded into the
  `architecture/` GDS ladder, the single binding source (`architecture/INDEX.md`; `CLAUDE.md`).
  `MSTR-002` (Architecture Principles) elevates and explains invariants that the ladder already
  states (GDS-03); it does not introduce new ones. Where this tree's wording and the ladder's
  wording differ, the ladder wins (MSTR-001 §7).
- **`research/01-07` are the doctrine/physics primers; the new `research/encyclopedia/` (R1xx-R5xx)
  is a *coding-agent-oriented* encyclopedia** with a different purpose (domain understanding for
  implementation, not doctrinal justification for design choices — see MSTR-007 §2). The
  encyclopedia cross-references the existing primers rather than re-deriving their content; e.g.
  R101 (Orbital Mechanics for Operations) points to `research/04-orbital-mechanics-primer.md` for
  the physics derivations already written there and focuses instead on implementation implications.
- **`vignettes/` stays the content library** (the 19 YAML scenarios + framework doc). The new
  `scenarios/` directory is about *how to design* a vignette to hit a stated training/assessment
  objective (the vignette framework and FS-201 territory) — process guidance, not additional scenario content.
- **`architecture/` is upstream of `features/`.** It is where a capability cluster's research and
  domain inputs get synthesized into a buildable shape *before* a Feature Specification commits
  to one, not a record of a decision already made about an existing subsystem. `ADS-xxx`
  documents in `architecture/` are produced earlier, to decide what `features/` should say.

### 3a. The Design Synthesis document shape (`architecture/ADS-xxx-*.md`)

Each `ADS-xxx` synthesizes one capability cluster's GDS grounding and its research
`research/encyclopedia/` (R1xx-R5xx) + `research/01-07` primer citations into ten fixed sections,
in this order:

1. **Executive Design Overview** — one paragraph: what capability cluster this covers, what
   problem it solves, and the single biggest design tension it resolves.
2. **System Architecture** — the seams/interfaces/data flow this cluster needs, expressed at the
   level GDS-03 (`architecture/03-architecture.md`) and GDS-07 (`architecture/07-data-model.md`) already use (engine/session/
   content/ui boundaries), not literal code.
3. **Domain Model** — the entities, their relationships, and the invariants that must hold,
   independent of any specific UI or API shape.
4. **User Stories** — cell-perspective ("as Blue/Red/White, I need to...") scenarios the cluster
   must support, traceable back to the vignette/training objective that motivates them.
5. **Functional Requirements** — what the capability must do, numbered, each traceable to a
   GDS (`GDS-nn`) or research (`R-xxx`) citation.
6. **Non-functional Requirements** — performance, determinism, fog-of-war, replay-safety, and
   other load-bearing invariants (`CLAUDE.md` §"Load-bearing invariants") that constrain this
   cluster specifically.
7. **Constraints** — fixed boundaries the design must work within (existing engine seams, the
   plan-first invariant, the six access channels, the five-D taxonomy) that are not up for
   revision in this synthesis.
8. **Risks** — what could go wrong in implementation or design (scope creep, a conflated FS
   boundary, an invariant violation) and how the synthesis mitigates or flags each.
9. **Open Questions** — genuine ambiguities not resolved by this synthesis, per MSTR-006 §6
   (flagged, not silently resolved).
10. **Decision Log** — the choices this synthesis actually made among competing options, each with
    a one-line rationale, so a later reader can see what was considered and rejected.

An `ADS-xxx` never contains production code (MSTR-006 §8) and never duplicates citations already
established in its grounding `GDS-nn`/`R-xxx` documents — it cites them, it doesn't re-derive
them. It is a **design document, not a research document**: its job is synthesis and decision, not
new domain-knowledge claims.

### 3b. The global Design Synthesis ladder (`architecture/GDS-00`…`GDS-10`)

Distinct from the per-cluster `ADS-xxx` shape in §3a, `architecture/` also holds a single, global,
strictly-sequential ladder spanning the whole project, scaffolded by user request and tracked in
`architecture/INDEX.md` §1 and `ROADMAP.md`'s "Global ladder" table:

| ID | Title | Purpose |
|---|---|---|
| GDS-00 | Vision | Project goals |
| GDS-01 | Concept of Operations | How users interact with the system |
| GDS-02 | System Context | External systems and interfaces |
| GDS-03 | Architecture | High-level subsystem decomposition |
| GDS-04 | Domain Model | Core entities and relationships |
| GDS-05 | Functional Requirements | The authoritative specification |
| GDS-06 | Non-functional Requirements | Performance, reliability, security, usability |
| GDS-07 | Data Model | Persistent data structures |
| GDS-08 | UI Architecture | Screens, navigation, workflows |
| GDS-09 | API Specification | Service boundaries and contracts |
| GDS-10 | Requirements Traceability Matrix | Maps requirements to features, tests, and implementation |

**Gating rule (binding):** `GDS-(N+1)` may not be started until `GDS-N` is authored *and* has
merged in whatever existing-corpus content overlaps it (per-document merge targets are listed in
`architecture/INDEX.md` §1). The merge is part of "done," not follow-up cleanup — this is an
explicit instruction, not a default convention like the rest of this corpus's looser
cross-linking expectations (contrast MSTR-006 §5's "best-effort" `Referenced By`).

This ladder is **new, separate content** — it does not silently replace `MSTR-001`; each
`GDS-NN`'s merge step explicitly folded in the content of the v1 build specification and design
corpus, both now retired. It coexists with, and is a different granularity from, the per-cluster `ADS-xxx` shape
in §3a: the ladder is one instance for the whole system; `ADS-xxx` is zero-or-more instances, one
per capability cluster with real design tension the ladder doesn't resolve at the system level.

## 4. The traceability chain

Every capability in this program should be expressible as an unbroken chain:

```
Training Objective  (named in a vignette's intro_brief / the vignette framework's objective taxonomy)
        ↓
Grounding            (GDS level or ADS — which architecture level states this capability)
        ↓
Research Documents   (R1xx-R5xx — what domain knowledge justifies the design)
        ↓
Design Synthesis     (ADS-xxx — grounding+research synthesized into an architecture, domain model,
                       requirements, constraints, risks, and decisions — see §3a)
        ↓
Feature Specification (FS-xxx — what the capability must do, no implementation detail;
                       **all FS-xxx authoring, old and new, is governed by the `06-feature-specification`
                       skill and its 20-field template — this supersedes the prior ad hoc per-section
                       structure; existing FS files retain their paths, IDs, and MSTR-006 §5 metadata**)
        ↓
Implementation Package (IMP-xxxA/B/C — how it is built: data model, state machine, API, tests)
        ↓
Code                 (spacesim/...)
        ↓
Tests                (spacesim/tests/...)
```

`ADS-xxx` is optional in the chain for small/uncontested features (a one-paragraph-scope FS like
those already authored does not need a synthesis step first) — it earns its place when a
capability cluster has real design tension: conflicting candidate requirements, multiple plausible
architectures, or assumptions that need to be made explicit and recorded before an FS-xxx can
commit to one shape. Skipping it is a judgment call, not a violation; an FS-xxx that does the
synthesis work inline in its own §1-2 has just absorbed the ADS-xxx role into itself.

Each document in the chain must carry, in its metadata block, the IDs of its immediate neighbors
(`Dependencies`, `Referenced By`, `Produces`, `Feature Mapping`). Phase 8 (Traceability Review, see
`ROADMAP.md`) is the periodic check that no link in this chain is missing or dangling.

## 5. Where does a new document go? (decision rule)

1. Is it stable, program-defining, and rarely revised? → `master/`.
2. (Retired.) The `domains/` folder held the domain frameworks; they were retired into the GDS ladder, MSTR-003 §2a, MSTR-006 §3a and §6a, FS-201 and the vignette framework. Do not add new ones; state the capability in the GDS ladder instead.
3. Is it domain knowledge a coding agent needs to implement correctly, written for that audience? →
   `research/encyclopedia/`, tiered R1xx-R5xx by subject (see MSTR-007 §3 for the tier definitions).
4. Does it describe *what* a capability must do, with no implementation detail? → `features/`,
   authored using the `06-feature-specification` skill's 20-field template.
5. Does it describe *how* to build a specific Feature Spec (data model, API, tests, migration)? →
   `implementation/packages/`.
6. Does it synthesize a capability cluster's domain+research inputs into an architecture, domain
   model, requirements, constraints, risks, and decisions *before* a Feature Specification commits
   to a shape? → `architecture/` as `ADS-xxx` (see §3a). Produced by the
   `03-architecture-design-synthesis` skill.
7. Is it process guidance for designing a vignette/scenario (not the scenario content itself)? →
   `scenarios/`.
8. Otherwise: does it already have a home in `architecture/`, `research/01-07`,
   `training/`, or `vignettes/`? Expand the existing file/theme rather than creating a new top-level
   directory — per the standing instruction to integrate, not replace.

## 6. Maintenance

- Update this tree diagram whenever a directory's top-level shape changes (a new tier, a new
  `architecture/`/`scenarios/` subdirectory convention).
- `ROADMAP.md` is the authoritative per-document status list — keep it synchronized with every
  document created or completed under this map.
