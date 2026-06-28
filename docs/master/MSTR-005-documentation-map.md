# MSTR-005 — Documentation Map

> **Document ID:** MSTR-005
> **Version:** 1.0
> **Status:** ♻️ Living (update whenever a directory or tier is added)
> **Dependencies:** MSTR-001
> **Referenced By:** `docs/INDEX.md`, `ROADMAP.md`, MSTR-006, all DOM-*, all FS-*, all IMP-*
> **Produces:** the routing rules every new document must follow
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`docs/DOCUMENTATION-PLAN.md`](../DOCUMENTATION-PLAN.md) (legacy five-theme rationale),
> [`ROADMAP.md`](../../ROADMAP.md) (per-document completion tracker)

[↑ Docs index](../INDEX.md)

## 1. Purpose

This is the map of the *entire* `docs/` tree after the documentation-driven-development expansion —
both the pre-existing five themes (`build-spec/`, `design/`, `research/`, `training/`, `vignettes/`)
and the six new directories this expansion adds (`master/`, `domains/`, `features/`,
`implementations/`, `architecture/`, `scenarios/`). `docs/INDEX.md` is the live router; this
document is the rationale and the rule set for where a new document belongs. `ROADMAP.md` is the
per-document status tracker — this document answers "where does X go," `ROADMAP.md` answers "is X
done."

## 2. Full directory tree

```
docs/
├── INDEX.md                      ← master router
├── DOCUMENTATION-PLAN.md         ← legacy five-theme rationale (build-spec/design/research/training/vignettes)
├── FUTURE-WORK.md                ← cross-cutting living TODO (v1.1+), incl. §12 research-expansion plan
├── AUDIT-2026-06*.md             ← point-in-time audit reports (commands, UI/TT&C, master audit)
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
├── domains/                      ← NEW: DOM-001..009, the frameworks that generate Feature Specs
│   ├── DOM-001-training-framework.md
│   ├── DOM-002-assessment-framework.md
│   ├── DOM-003-white-cell-framework.md
│   ├── DOM-004-research-framework.md
│   ├── DOM-005-validation-framework.md
│   ├── DOM-006-governance-framework.md
│   ├── DOM-007-human-factors-framework.md
│   ├── DOM-008-ai-integration-framework.md
│   └── DOM-009-doctrine-development-framework.md
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
├── implementations/               ← NEW: IMP-xxx, implementation plans (no production code)
│   ├── implementation-index.md
│   └── IMP-101A-… .md
│
├── architecture/                  ← NEW: ADS-xxx Design Synthesis documents (the bridge from
│   │                                  Domain+Research into a Feature Specification)
│   ├── INDEX.md
│   └── ADS-xxx-<slug>.md          ← one per capability cluster; ten fixed sections (§3a)
│
├── scenarios/                     ← NEW: scenario-design guidance distinct from the vignette *content* library
│   └── (how to design a vignette to hit a training/assessment objective; the vignette files themselves stay in vignettes/)
│
├── build-spec/                    ← UNCHANGED: the binding v1 spec, 8 modules — wins on conflict
├── design/                        ← UNCHANGED: architecture & design corpus (the "how")
├── training/                      ← UNCHANGED: user-facing manual
├── vignettes/                     ← UNCHANGED: the 19-vignette content library + framework
└── manual/                        ← UNCHANGED: generated UI screenshots
```

## 3. How the new tree relates to the existing five themes

The expansion does **not** duplicate or replace existing content. Specifically:

- **`build-spec/` stays the binding spec.** `MSTR-002` (Architecture Principles) elevates and
  explains invariants that `build-spec/` and `design/01-architecture-overview.md` already state;
  it does not introduce new ones. Where this tree's wording and the build spec's wording differ,
  the build spec wins (MSTR-001 §7).
- **`research/01-07` are the doctrine/physics primers; the new `research/encyclopedia/` (R1xx-R5xx)
  is a *coding-agent-oriented* encyclopedia** with a different purpose (domain understanding for
  implementation, not doctrinal justification for design choices — see MSTR-007 §2). The
  encyclopedia cross-references the existing primers rather than re-deriving their content; e.g.
  R101 (Orbital Mechanics for Operations) points to `research/04-orbital-mechanics-primer.md` for
  the physics derivations already written there and focuses instead on implementation implications.
- **`vignettes/` stays the content library** (the 19 YAML scenarios + framework doc). The new
  `scenarios/` directory is about *how to design* a vignette to hit a stated training/assessment
  objective (DOM-001/DOM-002 territory) — process guidance, not additional scenario content.
- **`design/` stays the detailed "how."** `architecture/` is upstream of that — it's where a
  capability cluster's research and domain inputs get synthesized into a buildable shape *before*
  a Feature Specification commits to one, not a record of a decision already made about an
  existing subsystem. `design/` documents an architecture that exists or is being built; `ADS-xxx`
  documents in `architecture/` are produced earlier, to decide what `design/` and `features/`
  should say.

### 3a. The Design Synthesis document shape (`architecture/ADS-xxx-*.md`)

Each `ADS-xxx` synthesizes one capability cluster's `DOM-xxx` framework and its grounding
`research/encyclopedia/` (R1xx-R5xx) + `research/01-07` primer citations into ten fixed sections,
in this order:

1. **Executive Design Overview** — one paragraph: what capability cluster this covers, what
   problem it solves, and the single biggest design tension it resolves.
2. **System Architecture** — the seams/interfaces/data flow this cluster needs, expressed at the
   level `design/01-architecture-overview.md` and `04-data-model.md` already use (engine/session/
   content/ui boundaries), not literal code.
3. **Domain Model** — the entities, their relationships, and the invariants that must hold,
   independent of any specific UI or API shape.
4. **User Stories** — cell-perspective ("as Blue/Red/White, I need to...") scenarios the cluster
   must support, traceable back to the vignette/training objective that motivates them.
5. **Functional Requirements** — what the capability must do, numbered, each traceable to a
   domain (`DOM-xxx`) or research (`R-xxx`) citation.
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
established in its grounding `DOM-xxx`/`R-xxx` documents — it cites them, it doesn't re-derive
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

This ladder is **new, separate content** — it does not silently replace `MSTR-001`, `build-spec/`,
or `design/`, which stay authoritative until a given `GDS-NN`'s merge step explicitly folds their
content in. It coexists with, and is a different granularity from, the per-cluster `ADS-xxx` shape
in §3a: the ladder is one instance for the whole system; `ADS-xxx` is zero-or-more instances, one
per capability cluster with real design tension the ladder doesn't resolve at the system level.

## 4. The traceability chain

Every capability in this program should be expressible as an unbroken chain:

```
Training Objective  (named in a vignette's intro_brief / DOM-001's objective taxonomy)
        ↓
Domain Document      (DOM-00x — which framework owns this capability)
        ↓
Research Documents   (R1xx-R5xx — what domain knowledge justifies the design)
        ↓
Design Synthesis     (ADS-xxx — domain+research synthesized into an architecture, domain model,
                       requirements, constraints, risks, and decisions — see §3a)
        ↓
Feature Specification (FS-xxx — what the capability must do, no implementation detail)
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
2. Does it define *how a domain of capability works* and generate Feature Specs? → `domains/`.
3. Is it domain knowledge a coding agent needs to implement correctly, written for that audience? →
   `research/encyclopedia/`, tiered R1xx-R5xx by subject (see MSTR-007 §3 for the tier definitions).
4. Does it describe *what* a capability must do, with no implementation detail? → `features/`.
5. Does it describe *how* to build a specific Feature Spec (data model, API, tests, migration)? →
   `implementations/`.
6. Does it synthesize a capability cluster's domain+research inputs into an architecture, domain
   model, requirements, constraints, risks, and decisions *before* a Feature Specification commits
   to a shape? → `architecture/` as `ADS-xxx` (see §3a). Produced by the
   `architecture-design-synthesis` skill.
7. Is it process guidance for designing a vignette/scenario (not the scenario content itself)? →
   `scenarios/`.
8. Otherwise: does it already have a home in `build-spec/`, `design/`, `research/01-07`,
   `training/`, or `vignettes/`? Expand the existing file/theme rather than creating a new top-level
   directory — per the standing instruction to integrate, not replace.

## 6. Maintenance

- Update this tree diagram whenever a directory's top-level shape changes (a new tier, a new
  `architecture/`/`scenarios/` subdirectory convention).
- `ROADMAP.md` is the authoritative per-document status list — keep it synchronized with every
  document created or completed under this map.
