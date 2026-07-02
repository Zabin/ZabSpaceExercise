# Master Build Plan — Implementation Packages

> **Document ID:** IMPL-PLAN-00
> **Version:** 1.0
> **Status:** ♻️ Living (updated as package status changes)
> **Dependencies:** all `IP-xxxx` packages in [`packages/`](packages/INDEX.md), the Feature
> Specification corpus (`docs/features/`), the Functional/Non-Functional Requirements baseline
> (`docs/requirements/`)
> **Referenced By:** `ROADMAP.md` (Theme: Implementation Packages)
> **Produces:** the executable sequencing, dependency graph, and status ledger for every
> Implementation Package in this pass
> **Feature Mapping:** FS-101 through FS-107, FS-201, FS-301 (9 of 11 catalog entries; FS-108/
> FS-202 excluded, see §"Scope and exclusions")
> **Related Topics:** [`packages/INDEX.md`](packages/INDEX.md), [`docs/implementations/INDEX.md`](../implementations/INDEX.md) (the superseded prior corpus), [`.claude/skills/code-implementation/SKILL.md`](../../.claude/skills/code-implementation/SKILL.md) (the downstream skill that executes packages against this plan)

[↑ Docs index](../INDEX.md) · [Packages index](packages/INDEX.md) · [Feature index](../features/feature-index.md)

## Purpose

This is the master build plan for converting this project's approved Feature Specifications
(`FS-xxx`, `docs/features/`) into executable Implementation Packages (`IP-xxxx`,
[`packages/`](packages/INDEX.md)). It states the implementation sequence, critical path,
dependency graph, parallel-execution opportunities, and current status of every package, per the
authoritative engineering baseline (Research Encyclopedia, ConOps, System Context, System
Architecture, Domain Model, ICD, ADRs, Functional/Non-Functional Requirements, Requirements
Traceability Matrix, Feature Catalog, Epic Catalog, Feature Specifications). **No architecture was
redesigned, no requirement was modified, and no new functionality was introduced to produce this
plan or the packages it sequences** — every package is a build-ready restatement of an already-
approved Feature Specification's scope.

## Scope and exclusions

The Feature Catalog ([`feature-index.md`](../features/feature-index.md)) lists 11 entries. This
build plan covers the **9 approved** entries (FS-101–107, FS-201, FS-301). **FS-108** (Inject
Authoring) and **FS-202** (Rubric Authoring) are explicitly excluded: both are marked
"(candidate)" / 🅿️ *Scoped, not authorized* per [MSTR-006](../master/MSTR-006-governance-principles.md)
§3 — the Feature Catalog's own governance rule is that no Implementation Package work may begin
against an unauthorized Feature Specification. This mirrors the exclusion already applied by the
prior `docs/implementations/` corpus (see §"Relationship to the prior corpus" below); it is not a
new decision introduced by this plan.

## Relationship to the prior `docs/implementations/` corpus

This project previously produced an equivalent Implementation Package tier at
[`docs/implementations/`](../implementations/INDEX.md) (`IMP-xxxA` IDs, 10 packages covering the
same 9 Feature Specifications). **This new `docs/implementation/packages/` tree (`IP-xxxx` IDs)
supersedes that corpus as the canonical Implementation Package record.** The two trees describe the
same underlying architecture, files, and design content — re-derived and re-verified against the
current source tree under this task's required template (Package ID, Objective, Requirements
Covered, Architecture Components, Interfaces, Files to Create/Modify, Implementation Tasks, Tests to
Add, Documentation Updates, Definition of Done, Verification Checklist, Dependencies, Risks,
Rollback Considerations) rather than the prior corpus's own template. The prior corpus's files are
**not deleted** — each carries a superseded-by banner pointing at its `IP-xxxx` successor, since
they remain useful historical/narrative reading and nothing in the corpus depends on their removal.

Every package in this pass observes the same hard governance rules the prior corpus established and
that continue to bind this tree ([MSTR-006](../master/MSTR-006-governance-principles.md)):

- **§8, the Implementation-Package boundary:** no package document contains literal committed code;
  each describes architecture, data models, tasks, and tests in prose/pseudocode-level detail
  sufficient for a future coding agent to implement.
- **§3, the authorization gate:** a package being fully specified (even to `READY` status) is not
  itself an authorization to begin coding. This binds **IP-2010** and **IP-3010** specifically —
  both are forward-design packages for capabilities that do not exist in `spacesim/` today, and
  **implementation work against either requires a separate, explicit user go-ahead**, independent
  of this plan's sequencing.

## Package status

| ID | Feature | Situation | Status | Blocking dependency |
|---|---|---|---|---|
| [IP-1010](packages/IP-1010-mission-planning.md) | FS-101 Mission Planning | As-built | ✅ VERIFIED | none |
| [IP-1020](packages/IP-1020-command-scheduling.md) | FS-102 Command Scheduling | As-built | ✅ VERIFIED | none |
| [IP-1030](packages/IP-1030-custody-management.md) | FS-103 Custody Management | As-built | ✅ VERIFIED | none |
| [IP-1040](packages/IP-1040-sda-tasking.md) | FS-104 SDA Tasking | As-built | ✅ VERIFIED | none |
| [IP-1050](packages/IP-1050-spacecraft-operations-bus-payload.md) | FS-105 §3.1 Spacecraft Ops (bus/payload) | As-built | ✅ VERIFIED | none |
| [IP-1051](packages/IP-1051-spacecraft-operations-effects-console.md) | FS-105 §3.2-4 Spacecraft Ops (effects) | As-built | ✅ VERIFIED | none |
| [IP-1060](packages/IP-1060-white-cell-dashboard.md) | FS-106 White Cell Dashboard | As-built | ✅ VERIFIED | none |
| [IP-1070](packages/IP-1070-after-action-review.md) | FS-107 After Action Review | As-built | ✅ VERIFIED | none |
| [IP-2010](packages/IP-2010-competency-assessment.md) | FS-201 Competency Assessment | Forward design | 🟡 READY | authorization only (MSTR-006 §3) |
| [IP-3010](packages/IP-3010-research-analytics.md) | FS-301 Research Analytics | Forward design | 🔴 BLOCKED | IP-2010 → `COMPLETE`, **and** authorization (MSTR-006 §3) |

8 of 10 packages are `VERIFIED` (the entire as-built surface — every shipped capability this pass
covers is already implemented, tested, and re-confirmed against the current source tree). The
remaining 2 are the project's only genuinely forward-looking Implementation Packages.

## Implementation sequence

Because 8 of 10 packages describe already-shipped code, "sequence" here has two distinct readings,
both given below: (a) the sequence in which the as-built packages' *code* was actually built
(useful for onboarding/history), and (b) the sequence remaining *work* must follow (the only
actionable sequencing question this plan poses going forward).

### (a) As-built dependency order (historical/onboarding reference)

```
Wave 1 (no package-level dependency):     IP-1010   IP-1030   IP-1060
Wave 2 (depends only on Wave 1):          IP-1020 ← IP-1010
                                           IP-1040 ← IP-1030
                                           IP-1070 ← IP-1030
Wave 3 (depends on Wave 1+2):             IP-1050 ← IP-1020
                                           IP-1051 ← IP-1030, IP-1010, IP-1020
```

### (b) Remaining work (the only actionable forward sequence)

```
IP-2010 (READY, blocked only on authorization)
   │  must reach COMPLETE before IP-3010's schema is more than provisional
   ▼
IP-3010 (BLOCKED on IP-2010; also independently requires its own authorization)
```

There is no other remaining sequencing question in this plan — every other package is already
`VERIFIED`.

## Dependency graph

```
IP-1010 (Mission Planning) ──────┬──► IP-1020 (Command Scheduling) ──┬──► IP-1050 (Bus/Payload)
                                  │                                    │
                                  └────────────────────────────────────┼──► IP-1051 (Effects/Console)
                                                                        │         ▲
IP-1030 (Custody Management) ────┬──► IP-1040 (SDA Tasking)            │         │
                                  │                                    │         │
                                  ├──► IP-1051 (Effects/Console) ◄─────┘         │
                                  │                                              │
                                  └──► IP-1070 (After Action Review) ────┐       │
                                                                          │       │
IP-1010, IP-1020 ─────────────────────────────────────────────────────┐ │       │
                                                                        ▼ ▼       │
IP-1060 (White Cell Dashboard) [independent — no downstream package]  IP-2010 (Competency Assessment)
                                                                          │
                                                                          ▼
                                                                     IP-3010 (Research Analytics)
```

Every edge above is drawn directly from the citing package's own **Dependencies** field (no edge is
inferred beyond what each package document already states). `IP-1060` is the one package with no
downstream consumer inside this pass's 10 packages (FS-108, the dashboard extension it would
otherwise feed, is out of scope per §"Scope and exclusions").

## Critical path

**Critical path length: 4 packages**, and it is the *only* path in this graph with any remaining
actionable work — every package on it except the last two hops is already `VERIFIED`:

```
IP-1010 ──► IP-1020 ──► IP-2010 ──► IP-3010      (length 4)
IP-1030 ──► IP-1070 ──► IP-2010 ──► IP-3010      (length 4, co-critical)
```

Both four-hop chains converge at **IP-2010**, which is accordingly the single highest-leverage
package in this plan: it is the sole gate between "every upstream dependency already shipped" and
"the entire forward-design surface of this catalog." Because IP-1010/IP-1020/IP-1030/IP-1070 are
all `VERIFIED`, the *effective* remaining critical path — the one with real, un-shipped work on it —
is exactly the two-package chain in §"Implementation sequence (b)" above: **IP-2010 → IP-3010**,
gated at each step by the MSTR-006 §3 authorization rule, not by any missing prerequisite.

## Parallel implementation opportunities

- **Among the as-built packages (historical):** Wave 1 (`IP-1010`, `IP-1030`, `IP-1060`) had zero
  inter-package dependencies and could have been built by three independent workstreams in
  parallel; Wave 2's three packages (`IP-1020`, `IP-1040`, `IP-1070`) likewise had no dependency on
  each other, only on their respective Wave 1 predecessor. This is retrospective value only — all
  eight packages are already `VERIFIED` — but it is the applicable precedent if any as-built package
  ever needs a from-scratch rebuild (e.g., after a major refactor).
- **Among the remaining forward-design work:** there is **no parallel opportunity** — `IP-3010`'s
  schema is explicitly provisional until `IP-2010` lands (FS-301 §4's "must not reimplement FS-201's
  computation" constraint means the export schema is defined *in terms of* IP-2010's actual output
  shape, not merely its current sketch). The two packages must be authorized and executed
  sequentially, not concurrently.
- **Independent of the critical path:** `IP-1060` (White Cell Dashboard) has no downstream consumer
  in this pass and could always have been (and could still be, for any future rework) developed on
  an entirely independent track from every other package.

## Summary

- **Total Features (Feature Catalog):** 11 (`docs/features/feature-index.md`)
- **Total Features covered by this plan:** 9 — FS-101 through FS-107, FS-201, FS-301
- **Features excluded (unauthorized candidates, MSTR-006 §3):** 2 — FS-108, FS-202
- **Total Packages:** 10 (`packages/IP-1010` through `IP-3010`; FS-105 is the only Feature split
  across two lettered-equivalent packages, `IP-1050`/`IP-1051`, per the size-discipline precedent
  this corpus follows)
- **Average Package Size:** 162 lines of Markdown per package (1,621 total lines across 10 package
  files; range 144–200 lines) — comparable in depth to the prior `docs/implementations/` corpus's
  packages, re-templated to this task's required 17-field structure
- **Critical Path Length:** 4 packages (`IP-1010`/`IP-1030` → `IP-1020`/`IP-1070` → `IP-2010` →
  `IP-3010`); the *effective remaining* critical path (excluding already-`VERIFIED` work) is 2
  packages: `IP-2010` → `IP-3010`
- **Parallel Work Opportunities:** 2 historical parallel waves among the (now-complete) as-built
  packages (3 packages, then 3 packages, running independently); **zero** parallel opportunities
  remain in the forward-design surface — `IP-2010` and `IP-3010` are strictly sequential
- **Package Status:** 8 `VERIFIED`, 1 `READY` (`IP-2010`), 1 `BLOCKED` (`IP-3010`); 0 `NOT STARTED`,
  0 `IN PROGRESS`, 0 `COMPLETE` (unverified)

### Risks requiring architectural attention

1. **Authorization gate is the actual blocker, not design completeness, for both remaining
   packages.** `IP-2010` is `READY` — every upstream dependency it needs is already `VERIFIED` — yet
   cannot start without an explicit, separate user go-ahead per MSTR-006 §3. This is a governance
   risk, not a technical one: a future session could mistake "fully specified" for "authorized" and
   begin coding against either package without the required go-ahead. Each package's own Definition
   of Done makes this explicit as its first, unchecked line item.
2. **`IP-2010`'s "aware vs. unaware" divergence signal is an unresolved design question**, not an
   implementation detail — `aar.py` as currently built does not derive a signal for whether a cell
   *recognized* its belief was wrong, only *that* it diverged. Implementing a plausible-but-
   unvalidated heuristic without flagging it as unvalidated (per DOM-005 §7's validation-disclosure
   discipline) would misrepresent an unvalidated metric as settled — an architectural/methodological
   risk that belongs to the assessment-framework domain (`DOM-002`), not to this build plan to
   resolve.
3. **Nine of eleven Feature Specifications carry a documented FR/NFR traceability gap.** Every FS-xxx
   this plan covers states, in its own "Requirements Implemented" field, that no FR-xxxx/NFR-xxxx
   explicitly cites it — confirmed independently against `docs/requirements/01-functional-
   requirements.md` and the Requirements Traceability Matrix during this pass. This plan's
   "Requirements Covered" sections cite the FR/NFR leaves that trace to each package's *files* (via
   the RTM's own file-level reverse index), not to the Feature ID itself — an honest secondary
   mapping, not a claim that the primary FS↔FR traceability gap is closed. Closing it is Phase 8
   traceability-review work (MSTR-006 §7) and is out of this build plan's scope to resolve by
   inference.
4. **FS-201's three deferred measurement dimensions (resource economy, escalation discipline,
   time-to-decision) and its longitudinal per-trainee persistence layer have no designed baseline.**
   `IP-2010` deliberately does not design them (no vignette-schema resource/ROE budget baseline, no
   OODA-tightness reference baseline, and no trainee-identity/cross-session persistence model exist
   in `spacesim/` today). Any future package adding them needs its own design pass, not an extension
   grafted onto `IP-2010`'s current scope — flagged here so a future planner does not assume they
   are already covered.
5. **`IP-3010`'s human-subjects boundary is a standing risk if a future package silently expands
   scope.** FS-301 §6 and both forward-design packages are explicit that no human-subjects research
   capability (cross-institution de-identified trainee data, IRB-gated consent) is in scope without
   separate authorization and the institution's own IRB/ethics process. This is restated once more
   here because it is the one non-goal in this plan whose violation would have consequences outside
   the engineering process (regulatory/ethical), not merely a defect to fix in code.

## Related

[`packages/INDEX.md`](packages/INDEX.md) · [`docs/features/feature-index.md`](../features/feature-index.md) ·
[`docs/implementations/INDEX.md`](../implementations/INDEX.md) (superseded prior corpus) ·
[`docs/master/MSTR-006-governance-principles.md`](../master/MSTR-006-governance-principles.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md) ·
`ROADMAP.md` (Theme: Implementation Packages)
