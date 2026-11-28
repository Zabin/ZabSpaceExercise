# MSTR-006 — Governance Principles

> **Document ID:** MSTR-006
> **Version:** 1.0
> **Status:** ✅ Stable
> **Dependencies:** MSTR-001, MSTR-005
> **Referenced By:** all FS-*, all IMP-*, `ROADMAP.md`
> **Produces:** the authoring/versioning/authorization rules every document and package must follow
> **Feature Mapping:** N/A — program-level
> **Related Topics:** the former future-work list §12.5.0 (authoring-cadence precedent),
> [`docs/master/MSTR-005-documentation-map.md`](MSTR-005-documentation-map.md)

[↑ Docs index](../INDEX.md) · [Master index](MSTR-005-documentation-map.md)

## 1. Purpose

Defines how documents in this corpus are versioned, statused, authorized, and kept consistent over
time — so the corpus itself doesn't decay the way undocumented codebases do. §3a and §6a below are the elaboration of this for the simulator's content and feature scope; §1 to
§3 and the rest are specifically about the documentation corpus's own lifecycle.

## 2. Document lifecycle and status taxonomy

Every document carries a `Status` field using this fixed vocabulary (consistent with the symbols
already established in `ROADMAP.md`):

| Symbol | Status | Meaning |
|---|---|---|
| ✅ | Done | Complete and current; safe to depend on. |
| 🚧 | In progress | Drafted but incomplete or under active revision. |
| ⛔ | Planned | Identified and scoped, not yet started. |
| ♻️ | Living | Intentionally never "done" — updated continuously (glossaries, indexes, TODO lists). |
| 🖼️ | Generated | Produced by a tool from another source of truth; edit the source, not this file. |
| 🅿️ | Scoped, not authorized | Fully specified but requires explicit go-ahead before work starts (see §3). |

A document's status is a claim about *that document*, not about the feature/capability it
describes — a `✅` Feature Specification can map to code that is `⛔ Planned`. Status drift between
related documents (a `✅` Feature Spec whose only Implementation Package is `⛔`) is expected and
fine; it is tracked, not hidden, in `ROADMAP.md`.

## 3. Authorization gate for large undertakings

Some scoped work is large enough (in token cost, review burden, or strategic commitment) that it
should not start merely because it has been specified. The precedent is
The former future-work list §12's research-corpus-expansion plan: fully scoped (file IDs, line-count
targets, dependencies) but marked "planned, not yet authorized," with later tiers explicitly
requiring the user to be asked before starting.

**Rule:** any document or document-set marked 🅿️ requires an explicit user go-ahead before an agent
begins producing it, even if it is fully specified and even if a previous, smaller tier of the same
initiative was authorized. Authorization is scoped to what was actually approved — approval of Tier
1 of a research expansion does not imply approval of Tier 2-4 (this mirrors the project's general
"actions are authorized at the scope specified, not beyond" working rule).

## 3a. Content change classes

*Moved here from the retired governance domain document (§3). Governs the simulator's content and
feature scope, where §1 to §3 govern the documentation corpus.*

| Class | Example | Authorization needed |
|---|---|---|
| **Additive, low-risk** | A new inject template, a new vignette within an existing progression slot (the [vignette framework](../vignettes/00-vignette-framework.md), Skill-progression model) | Author discretion; record in `ROADMAP.md`/vignette INDEX |
| **Additive, scope-expanding** | A new effect category, a new access channel, a new sensor modality | Feature Specification required (Phase 4 process) before any Implementation Package |
| **Modifying existing balance** | Recalibrating power-drain constants (the Jun 2026 audit precedent), ROE defaults | Documented audit/rationale (see `AUDIT-2026-06*.md` under `docs/reviews/` as the precedent format) + regression test |
| **Large, multi-tier undertaking** | The research-corpus 10× expansion (§3), a new top-level domain | 🅿️ explicit user authorization per §3, tier by tier |

## 4. AI authoring constraints

Documents in this corpus are written to be **independently retrievable**: an agent that opens one
file should have what it needs, via explicit cross-references, not implicit context from sibling
files. Concretely:

- **Size discipline**, by document class (a soft target, not a hard limit — clarity wins over
  strict page-count compliance):
  - Master documents: ~10-20 pages equivalent.
  - Research encyclopedia topics: ~3-8 pages equivalent — short and single-topic on purpose.
  - Design Synthesis documents (`ADS-xxx`): ~8-15 pages equivalent across its ten fixed sections
    (MSTR-005 §3a) — a synthesis that needs more room is a sign the capability cluster should be
    split into two `ADS-xxx` documents, not one oversized one.
  - Feature Specifications: ~5-10 pages equivalent.
  - Implementation Packages: ~10-25 pages equivalent; **split a feature across multiple lettered
    packages** (`IMP-101A`, `IMP-101B`, ...) rather than writing one oversized package.
- **Token-budget discipline for batch authoring.** When a coding/authoring agent is asked to
  produce several documents in one pass (e.g. an R1xx tier), cap the unit of work per subagent
  invocation (the precedent in the former future-work list §12.5.0 is ≤20k tokens per invocation) — whole-tier,
  whole-file-dump invocations have previously blown token budgets and produced shallow output.
  Prefer one-document or small-batch invocations with explicit per-document review.
- **Every document carries the full metadata block** (§5) so an agent can determine relevance and
  dependencies without reading the whole tree.

## 5. Required metadata block

Every document in `master/`, `research/encyclopedia/`, `features/`, `implementation/`,
`architecture/`, and `scenarios/` opens with:

```
> **Document ID:** <prefix>-<number>[<letter>]
> **Version:** <semantic-ish, e.g. 1.0>
> **Status:** <symbol> <word>
> **Dependencies:** <IDs this document assumes/builds on, or "none">
> **Referenced By:** <IDs known to depend on this — best-effort, update as new dependents appear>
> **Produces:** <IDs this document is the source for, if any>
> **Feature Mapping:** <FS-xxx IDs, or "N/A — program-level">
> **Related Topics:** <cross-links to companion documents>
```

`Referenced By` is necessarily best-effort (a document cannot know all its future dependents at
creation time) — Phase 8 traceability review (§7) is where this is reconciled in both directions.

## 6. Conflict resolution

If two documents disagree:

1. `docs/architecture/` (the GDS-00…GDS-10 ladder) wins over everything (`CLAUDE.md`; MSTR-001 §7) —
   this replaces the former rule that the v1 build specification won.
2. Within the new tree, a more specific document (an Implementation Package) does not override a
   less specific one (a Feature Specification, an architecture level) on matters of *intent* — if an
   IMP package's design seems to contradict its parent FS's stated purpose, that's a defect in the
   IMP package, not a silent reinterpretation of the FS.
3. Genuine ambiguity that isn't resolved by (1)/(2) should be raised explicitly (flagged in the
   document with a `> **Open question:**` callout, recorded in the former future-work list, or — for anything
   that changes scope or strategic direction — asked of the user) rather than resolved by silent
   authorial choice.

## 6a. Decision rights

*Moved here from the retired governance domain document (§6).*

| Decision | Who decides |
|---|---|
| Whether a deferred item on the backlog (`docs/pipeline/backlog.md`) or a LATER row of the Release 2.0 plan graduates to a Feature Specification | Any contributor, by writing the FS — no separate approval gate for *specifying* |
| Whether a 🅿️-tier or large undertaking is authorized to *start* | The user/program owner (§3) |
| Whether a vignette content change is balanced/correct doctrine | White Cell subject-matter judgment ([MSTR-003](MSTR-003-educational-philosophy.md) §7; the vignette framework, Doctrine to content) |
| Whether an architecture/invariant (MSTR-002) may be relaxed for a feature | Not a unilateral author decision — requires explicit escalation per §6 |

## 7. Periodic reviews (Phases 6-8)

- **Phase 6 — Consistency review:** every document's metadata block is internally consistent
  (status matches actual content completeness; dependencies actually exist as files).
- **Phase 7 — Dependency review:** no document depends on something that doesn't exist or is
  itself unresolved in a way that breaks the chain.
- **Phase 8 — Traceability review:** the full chain in MSTR-005 §4 is walked for every Feature
  Specification, confirming Training Objective → Domain → Research → FS → IMP → Code → Tests has no
  gap. Findings become `ROADMAP.md` entries, not silent fixes, if they require a judgment call.

## 8. Implementation-package boundary (hard rule)

Per the standing instruction for this documentation-expansion effort: **no document in this corpus
may contain production code**, and no document creation in this phase should modify
`spacesim/**/*.py`, tests, or any other source file. Implementation Packages describe architecture,
data models, state machines, algorithms, interfaces, and test/migration plans in prose, diagrams,
and pseudocode-level detail sufficient for a future coding agent to implement — never as literal
committed code.
