# MSTR-006 — Governance Principles

> **Document ID:** MSTR-006
> **Version:** 1.0
> **Status:** ✅ Stable
> **Dependencies:** MSTR-001, MSTR-005
> **Referenced By:** DOM-006, DOM-008, all FS-*, all IMP-*, `ROADMAP.md`
> **Produces:** the authoring/versioning/authorization rules every document and package must follow
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`docs/FUTURE-WORK.md`](../FUTURE-WORK.md) §12.5.0 (authoring-cadence precedent),
> [`docs/master/MSTR-005-documentation-map.md`](MSTR-005-documentation-map.md)

[↑ Docs index](../INDEX.md) · [Master index](MSTR-005-documentation-map.md)

## 1. Purpose

Defines how documents in this corpus are versioned, statused, authorized, and kept consistent over
time — so the corpus itself doesn't decay the way undocumented codebases do. DOM-006 (Governance
Framework) is the domain-level elaboration of this for feature/process governance generally; this
document is specifically about the documentation corpus's own lifecycle.

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
`docs/FUTURE-WORK.md` §12's research-corpus-expansion plan: fully scoped (file IDs, line-count
targets, dependencies) but marked "planned, not yet authorized," with later tiers explicitly
requiring the user to be asked before starting.

**Rule:** any document or document-set marked 🅿️ requires an explicit user go-ahead before an agent
begins producing it, even if it is fully specified and even if a previous, smaller tier of the same
initiative was authorized. Authorization is scoped to what was actually approved — approval of Tier
1 of a research expansion does not imply approval of Tier 2-4 (this mirrors the project's general
"actions are authorized at the scope specified, not beyond" working rule).

## 4. AI authoring constraints

Documents in this corpus are written to be **independently retrievable**: an agent that opens one
file should have what it needs, via explicit cross-references, not implicit context from sibling
files. Concretely:

- **Size discipline**, by document class (a soft target, not a hard limit — clarity wins over
  strict page-count compliance):
  - Master documents: ~10-20 pages equivalent.
  - Domain documents: ~15-30 pages equivalent.
  - Research encyclopedia topics: ~3-8 pages equivalent — short and single-topic on purpose.
  - Design Synthesis documents (`ADS-xxx`): ~8-15 pages equivalent across its ten fixed sections
    (MSTR-005 §3a) — a synthesis that needs more room is a sign the capability cluster should be
    split into two `ADS-xxx` documents, not one oversized one.
  - Feature Specifications: ~5-10 pages equivalent.
  - Implementation Packages: ~10-25 pages equivalent; **split a feature across multiple lettered
    packages** (`IMP-101A`, `IMP-101B`, ...) rather than writing one oversized package.
- **Token-budget discipline for batch authoring.** When a coding/authoring agent is asked to
  produce several documents in one pass (e.g. an R1xx tier), cap the unit of work per subagent
  invocation (the precedent in `FUTURE-WORK.md` §12.5.0 is ≤20k tokens per invocation) — whole-tier,
  whole-file-dump invocations have previously blown token budgets and produced shallow output.
  Prefer one-document or small-batch invocations with explicit per-document review.
- **Every document carries the full metadata block** (§5) so an agent can determine relevance and
  dependencies without reading the whole tree.

## 5. Required metadata block

Every document in `master/`, `domains/`, `research/encyclopedia/`, `features/`, `implementations/`,
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

1. `docs/build-spec/` wins over everything (MSTR-001 §7) — this is unchanged by the expansion.
2. Within the new tree, a more specific document (an Implementation Package) does not override a
   less specific one (a Feature Specification, a Domain document) on matters of *intent* — if an
   IMP package's design seems to contradict its parent FS's stated purpose, that's a defect in the
   IMP package, not a silent reinterpretation of the FS.
3. Genuine ambiguity that isn't resolved by (1)/(2) should be raised explicitly (flagged in the
   document with a `> **Open question:**` callout, recorded in `FUTURE-WORK.md`, or — for anything
   that changes scope or strategic direction — asked of the user) rather than resolved by silent
   authorial choice.

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
