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
> **Feature Mapping:** FS-101 through FS-107, FS-109, FS-110, FS-111, FS-112, FS-113, FS-114,
> FS-115, FS-201, FS-301 (16 of 18 catalog entries; FS-108/FS-202 excluded, see §"Scope and
> exclusions")
> **Related Topics:** [`packages/INDEX.md`](packages/INDEX.md), [`docs/implementations/INDEX.md`](../implementations/INDEX.md) (the superseded prior corpus), [`.claude/skills/08-code-implementation/SKILL.md`](../../.claude/skills/08-code-implementation/SKILL.md) (the downstream skill that executes packages against this plan)

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

The Feature Catalog ([`feature-index.md`](../features/feature-index.md)) lists 18 entries (up from
11 — FS-109/110/111 split from FS-106, FS-112/113/114/115 newly authored, per
`docs/feature-planning/05-feature-review.md` Findings F-02/F-03/F-10). This build plan covers the
**16 approved** entries (FS-101–107, FS-109, FS-110, FS-111, FS-112, FS-113, FS-114, FS-115,
FS-201, FS-301). **FS-108** (Inject Authoring) and **FS-202** (Rubric Authoring) are explicitly
excluded: both are marked "(candidate)" / 🅿️ *Scoped, not authorized* per
[MSTR-006](../master/MSTR-006-governance-principles.md) §3 — the Feature Catalog's own governance
rule is that no Implementation Package work may begin against an unauthorized Feature
Specification. This mirrors the exclusion already applied by the prior `docs/implementations/`
corpus (see §"Relationship to the prior corpus" below); it is not a new decision introduced by this
plan.

**FS-112/113/114/115 (2026-07 tranche):** these four were approved with their build status
explicitly flagged unverified. `07-implementation-planning`'s Tranche 1
([`01-technical-work-breakdown.md`](01-technical-work-breakdown.md)) performed that verification
before authoring packages, and found each partially or fully built but diverging from its Feature
Specification in some way — see the TWBS and each package's own header for the finding. None of the
five resulting packages (`IP-1120`, `IP-1130`, `IP-1140`, `IP-1150`, `IP-1151`) is `VERIFIED`.

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

**Authorization update (2026-07-03):** the project owner reviewed every package gated on MSTR-006
§3 and authorized `IP-2010`, `IP-1130`, `IP-1120`, and `IP-1151` (recorded in
`docs/pipeline/pipeline-journal.md` run #2). `IP-3010` was **not** authorized this round — it
remained gated on its own separate go-ahead in addition to `IP-2010` reaching `COMPLETE`, per
MSTR-006 §3's rule that approval of one package never implies approval of a related one.
`IP-1120`/`IP-1151` were, at authorization time, still functionally `BLOCKED` on `IP-1150` reaching
`VERIFIED` — that gate cleared the same day (`VR-1150`, see Package status below), so both are now
fully unblocked and `READY`.

**Authorization update (2026-07-03, run #9):** the project owner subsequently authorized `IP-3010`
as well (via `00-pipeline-manager`, batching the standing ripe `BL-0005` `NEEDS-USER` item into
this run's gate check). `IP-3010`'s only other blocker — `IP-2010` reaching `COMPLETE` — cleared in
run #5; per this package's own `Dependencies` field, `COMPLETE` (not `VERIFIED`) is the stated
threshold, and the Package status table below has consistently treated that sub-condition as
already met. With authorization now also on record, `IP-3010` flips `BLOCKED → READY` — the last
package in this plan to reach that state.

## Package status

| ID | Feature | Situation | Status | Blocking dependency |
|---|---|---|---|---|
| [IP-1010](packages/IP-1010-mission-planning.md) | FS-101 Mission Planning | As-built | ✅ VERIFIED | none |
| [IP-1020](packages/IP-1020-command-scheduling.md) | FS-102 Command Scheduling | As-built | ✅ VERIFIED | none |
| [IP-1030](packages/IP-1030-custody-management.md) | FS-103 Custody Management | As-built | ✅ VERIFIED | none |
| [IP-1040](packages/IP-1040-sda-tasking.md) | FS-104 SDA Tasking | As-built | ✅ VERIFIED | none |
| [IP-1050](packages/IP-1050-spacecraft-operations-bus-payload.md) | FS-105 §3.1 Spacecraft Ops (bus/payload) | As-built | ✅ VERIFIED | none |
| [IP-1051](packages/IP-1051-spacecraft-operations-effects-console.md) | FS-105 §3.2-4 Spacecraft Ops (effects) | As-built | ✅ VERIFIED | none |
| [IP-1060](packages/IP-1060-white-cell-dashboard.md) | FS-106 White Cell Dashboard *(v2.0, narrowed)* | As-built | ✅ VERIFIED | none |
| [IP-1070](packages/IP-1070-after-action-review.md) | FS-107 After Action Review | As-built | ✅ VERIFIED | none |
| [IP-1090](packages/IP-1090-multiplayer-session-transport.md) | FS-109 Multiplayer / LAN Session Transport | As-built | ✅ VERIFIED | none |
| [IP-1100](packages/IP-1100-save-and-resume.md) | FS-110 Save & Resume | As-built | ✅ VERIFIED | none |
| [IP-1110](packages/IP-1110-ai-red-doctrine-automation.md) | FS-111 AI-Red Doctrine Automation | As-built | ✅ VERIFIED | none |
| [IP-2010](packages/IP-2010-competency-assessment.md) | FS-201 Competency Assessment | Forward design | 🔵 COMPLETE | **Implemented 2026-07-03** — `session/assessment.py` (three scoring functions + report), `custody_confidence_at_decision` captured in `orders.py`'s `_exec_payload()` via a new `custody.py` helper; full suite green (507 passed/3 skipped), both permanent gates green; awaiting `09-package-verification` |
| [IP-3010](packages/IP-3010-research-analytics.md) | FS-301 Research Analytics | Forward design | 🟡 READY | **Fully unblocked 2026-07-03 (run #9)** — `IP-2010 → COMPLETE` cleared run #5 (this package's own `Dependencies` field requires `COMPLETE`, not `VERIFIED`, already satisfied); MSTR-006 §3 authorization obtained run #9 (`docs/pipeline/pipeline-journal.md`), the last of the five gated packages to receive it; a separate ADR-0029 conflict is resolved by `ADR-0033` |
| [IP-1120](packages/IP-1120-classification-banner.md) | FS-112 Classification Banner | Partially built (gap-closing) | 🔵 COMPLETE | **Implemented 2026-07-03** (run #6) — `session/manager.py`/`session/inprocess.py`/`session/aar.py`/`ui_web/server.py`/`ui_web/static/` all threaded to one resolved `classification` value; full suite green (519 passed/3 skipped), both permanent gates green; awaiting `09-package-verification` |
| [IP-1130](packages/IP-1130-observer-read-only-access.md) | FS-113 Observer Read-Only Access | Forward design | 🔵 COMPLETE | **Implemented 2026-07-03** (run #7) — a server-side `_reject_observer` guard on all 22 mutating routes (re-derived from the live route table, one more than the package's own enumerated list — `/preview/consequence`), a White-Cell-only Observer view designation (`session/inprocess.py`), a new `observer/view`+`observer/designation` endpoint pair; full suite green (547 passed/3 skipped), both permanent gates green; awaiting `09-package-verification` |
| [IP-1140](packages/IP-1140-hot-seat-handoff.md) | FS-114 Hot-Seat Hand-Off Screen-Blank Menu | As-built (documented spec divergence) | 🔵 COMPLETE | None — awaiting `09-package-verification`, which should also adjudicate the documented trigger/menu divergence from FR-6610 |
| [IP-1150](packages/IP-1150-vignette-selection.md) | FS-115 §FR-4110 Vignette Selection & Parameter Tuning | As-built | ✅ VERIFIED | none — verified 2026-07-03, [`VR-1150`](verification/VR-1150-vignette-selection.md) |
| [IP-1151](packages/IP-1151-seat-role-assignment.md) | FS-115 §FR-4210 Seat-to-Role Assignment | Forward design | 🔵 COMPLETE | **Implemented 2026-07-03** (run #8) — `Vignette.roles_needed`/`RoleRequirement` (additive, absent for all 19 existing vignettes), `SessionManager.assign_role`/`staffing_report`, `InProcessSession.start()` hard-gated on any unmet mandatory entry, `/roles/assign`+`/roles/staffing` endpoints; full suite green (559 passed/3 skipped), both permanent gates green; awaiting `09-package-verification` — see also the Outstanding Issue about FS-105/IP-1050's claimed "existing command-filtering consumer," which this run found no evidence of in the code |

**Update (2026-07, tranche 1):** IP-1090/IP-1100/IP-1110 are new, split out of IP-1060 v1.0 per
`docs/feature-planning/05-feature-review.md` Finding F-03 (mirroring the FS-106 split). No new code
verification was performed — these three packages reorganize citations `IP-1060` v1.0 (and its
superseded predecessor `IMP-106A`) already established, under the Feature boundaries FS-109/110/111
now own.

**Update (2026-07, tranche 2):** IP-1120/IP-1130/IP-1140/IP-1150/IP-1151 are new — the first
Implementation Packages written against FS-112/113/114/115, after `07-implementation-planning`'s
required build-status verification pass found each Feature partially or fully built (never
`VERIFIED`, never fully unimplemented) — see
[`01-technical-work-breakdown.md`](01-technical-work-breakdown.md) Tranche 1 for the verification
findings and split rationale. FS-115 splits into `IP-1150` (as-built, FR-4110) and `IP-1151`
(forward design, FR-4210), mirroring the `FS-105 → IP-1050`/`IP-1051` split precedent but split by
build-status seam rather than subsystem seam.

**Update (2026-07-03, verification):** `IP-1150` passed `09-package-verification`
([`VR-1150`](verification/VR-1150-vignette-selection.md)) and flipped to `VERIFIED` — the first
package verified through the formal `VR-xxxx` process (the original 11 as-built packages predate
this convention). This cleared the sole blocking dependency for `IP-1120` and `IP-1151`, both of
which flip `BLOCKED → READY` (both were already authorized 2026-07-03, so both are now fully
unblocked and eligible for `08-code-implementation`). The verification also corrected a stale RTM
cell: `FR-4110`'s `Test`/`Impl. Package` columns had been `UNASSIGNED` despite the code and tests
existing.

12 of 18 packages are now `VERIFIED` (the original 11 as-built + `IP-1150`, this plan's first
package verified through the formal `VR-xxxx` process). 5 are `COMPLETE` (`IP-1140`, as-built,
pending its own `09-package-verification` run; `IP-2010`, `IP-1120`, `IP-1130`, and `IP-1151`, all
implemented 2026-07-03, likewise pending `09-package-verification`). 1 is `READY` (`IP-3010` —
authorized run #9, its `IP-2010`-reaching-`COMPLETE` blocker having cleared run #5). 0 are
`BLOCKED`. **Every package in this plan now has a live forward path** — five need only
`09-package-verification`, and `IP-3010` is the sole package eligible for `08-code-implementation`.

## Implementation sequence

Because 11 of 13 packages describe already-shipped code, "sequence" here has two distinct readings,
both given below: (a) the sequence in which the as-built packages' *code* was actually built
(useful for onboarding/history), and (b) the sequence remaining *work* must follow (the only
actionable sequencing question this plan poses going forward).

### (a) As-built dependency order (historical/onboarding reference)

```
Wave 1 (no package-level dependency):     IP-1010   IP-1030   IP-1060   IP-1090   IP-1100   IP-1110
Wave 2 (depends only on Wave 1):          IP-1020 ← IP-1010
                                           IP-1040 ← IP-1030
                                           IP-1070 ← IP-1030
Wave 3 (depends on Wave 1+2):             IP-1050 ← IP-1020
                                           IP-1051 ← IP-1030, IP-1010, IP-1020
```

*(IP-1090/IP-1100/IP-1110 added 2026-07, split out of IP-1060 v1.0 — see Package status above. All
three remain Wave 1: none of the other packages in this pass are their prerequisite, mirroring
IP-1060's own original independence. IP-1070's own Dependencies field cites only IP-1030, unchanged
by this split — IP-1100 (Save & Resume)'s own `Referenced By` field notes IP-1070 as a downstream
*consumer* of a resumed session's event log, but that is not a stated package-level build
dependency in IP-1070's own Dependencies field, so no new edge is added here on that basis.)*

### (b) Remaining work (the only actionable forward sequence)

```
IP-2010 (COMPLETE 2026-07-03, awaiting 09-package-verification — implemented, not yet VERIFIED)
   │  IP-3010's schema-provisional blocker is satisfied by COMPLETE (its own Dependencies field's
   │  stated threshold); IP-3010's own MSTR-006 §3 authorization obtained run #9
   ▼
IP-3010 (READY 2026-07-03, run #9 — eligible for 08-code-implementation)

IP-1150 (✅ VERIFIED 2026-07-03, VR-1150 — cleared)
   │  unblocked IP-1120/IP-1151 the moment it reached VERIFIED
   ├──► IP-1120 (COMPLETE 2026-07-03, awaiting 09-package-verification — implemented, not yet VERIFIED)
   └──► IP-1151 (COMPLETE 2026-07-03, awaiting 09-package-verification — implemented, not yet VERIFIED)

IP-1130 (COMPLETE 2026-07-03, awaiting 09-package-verification — implemented, not yet VERIFIED)

IP-1140 (COMPLETE, awaiting 09-package-verification only — no coding work remains unless
         verification adjudicates the documented FR-6610 trigger/menu divergence and routes a
         gap-closing package back through this pipeline)
```

This tranche's `IP-1150 → {IP-1120, IP-1151}` fan-out is fully cleared as of 2026-07-03 — both
`IP-1120` and `IP-1151` are now implemented (`COMPLETE`). The pre-existing `IP-2010 → IP-3010`
chain's first hop is now implemented (`IP-2010` `COMPLETE`); `IP-3010` received its own
authorization in run #9 and is now `READY`. `IP-1130` is now implemented (`COMPLETE`) too.
**`IP-3010` is now the sole package in this plan that is coding-eligible (`READY`)** —
`IP-1140`/`IP-2010`/`IP-1120`/`IP-1130`/`IP-1151` (all `COMPLETE`) are each standalone,
one-hop-from-`VERIFIED` verification work with no sequencing dependency on anything else.

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

IP-1090 (Multiplayer / LAN Transport) [independent — no downstream package in this pass]
IP-1100 (Save & Resume)               [independent — no downstream package in this pass]
IP-1110 (AI-Red Doctrine Automation)  [independent — no downstream package in this pass]

IP-1150 (Vignette Selection, FS-115 §FR-4110) ──┬──► IP-1120 (Classification Banner, FS-112)
                                                  └──► IP-1151 (Seat-to-Role Assignment, FS-115 §FR-4210)

IP-1130 (Observer Read-Only Access)   [independent — no downstream package in this pass]
IP-1140 (Hot-Seat Hand-Off)           [independent — no downstream package in this pass]
```

Every edge above is drawn directly from the citing package's own **Dependencies** field (no edge is
inferred beyond what each package document already states). `IP-1060`, `IP-1090`, `IP-1100`,
`IP-1110`, `IP-1130`, and `IP-1140` are the six packages with no downstream consumer inside this
pass's 18 packages (FS-108, the dashboard extension `IP-1060` would otherwise feed, is out of scope
per §"Scope and exclusions"; IP-1090/1100/1110's only conceptual consumer, IP-1060 itself, cites
them as the mechanism its own trigger surface sits on top of — a description, not a package-level
build-order dependency `IP-1060`'s own `Dependencies` field asserts, so no edge is drawn for it
here either, consistent with how this graph already treats every other such relationship).
`IP-1150` is new to this pass and gains two downstream consumers, `IP-1120` and `IP-1151`, per
those two packages' own `Dependencies` fields.

## Critical path

**Critical path length: 4 packages**, and it is the *longest* path in this graph with any remaining
actionable work — every package on it except the last two hops is already `VERIFIED`:

```
IP-1010 ──► IP-1020 ──► IP-2010 ──► IP-3010      (length 4)
IP-1030 ──► IP-1070 ──► IP-2010 ──► IP-3010      (length 4, co-critical)
```

Both four-hop chains converge at **IP-2010**, which was accordingly this plan's single
highest-leverage package: it was the sole gate between "every upstream dependency already shipped"
and "the entire forward-design surface of this catalog." **`IP-2010` reached `COMPLETE`
2026-07-03** (implemented, pending `09-package-verification`), and **`IP-3010` received its own
MSTR-006 §3 authorization 2026-07-03 (run #9)** — the *effective* remaining critical path is now
the single-package hop **IP-3010**, `READY` and eligible for `08-code-implementation`. A future
planner could still tighten the bar to require `IP-2010` reach `VERIFIED` rather than merely
`COMPLETE` before treating `IP-3010` as safe to build against (this package's own `Dependencies`
field only requires `COMPLETE`, already satisfied) — flagged in Risk item 1 below.

**Tranche 2 (FS-112–115)'s shorter, independent chain is now fully cleared (2026-07-03):**
`IP-1150 → IP-1120` and `IP-1150 → IP-1151` were never on the critical path above (length 2 < 4).
`IP-1120` and `IP-1151` are both now implemented (`COMPLETE`, runs #6/#8). `IP-1130` is also now
implemented (`COMPLETE`, run #7) — it had no package-level dependency at all. All five tranche 2
packages (`IP-1120`, `IP-1130`, `IP-1140`, `IP-1150` `VERIFIED`, `IP-1151`) are now shipped or
implemented; `IP-1120`/`IP-1130`/`IP-1140`/`IP-1151` are the tranche's open verification items
(`IP-1140`'s pass should also adjudicate its documented FR-6610 divergence).

## Parallel implementation opportunities

- **Among the as-built packages (historical):** Wave 1 (`IP-1010`, `IP-1030`, `IP-1060`, `IP-1090`,
  `IP-1100`, `IP-1110`) had zero inter-package dependencies and could have been built by six
  independent workstreams in parallel; Wave 2's three packages (`IP-1020`, `IP-1040`, `IP-1070`)
  likewise had no dependency on each other, only on their respective Wave 1 predecessor. This is
  retrospective value only — all eleven as-built packages are already `VERIFIED` — but it is the
  applicable precedent if any as-built package ever needs a from-scratch rebuild (e.g., after a
  major refactor). *(IP-1090/IP-1100/IP-1110 added 2026-07 — see Package status above; they were
  always independently buildable, this just wasn't visible while all three were undifferentiated
  inside `IP-1060` v1.0.)*
- **Among the remaining forward-design work:** `IP-2010` has landed (`COMPLETE` 2026-07-03), so
  `IP-3010`'s schema is no longer provisional-against-a-sketch (FS-301 §4's "must not reimplement
  FS-201's computation" constraint is satisfied by `IP-2010`'s actual, now-implemented output
  shape), and `IP-3010` received its own MSTR-006 §3 authorization 2026-07-03 (run #9) — it is now
  `READY` and can proceed independently of the five packages awaiting `09-package-verification`.
- **Independent of the critical path:** `IP-1060` (White Cell Dashboard), `IP-1090` (Multiplayer /
  LAN Transport), `IP-1100` (Save & Resume), and `IP-1110` (AI-Red Doctrine Automation) have no
  downstream consumer in this pass and could always have been (and could still be, for any future
  rework) developed on entirely independent tracks from every other package and from each other.
- **Tranche 2 (FS-112–115):** `IP-1130` (Observer Read-Only Access) and `IP-1140` (Hot-Seat
  Hand-Off) have no package-level dependency on anything in this tranche or elsewhere in this plan
  and can be verified/implemented fully in parallel with each other and with `IP-1120`/`IP-1151`.
  `IP-1150` reached `VERIFIED` 2026-07-03 (`VR-1150`), clearing the one gate `IP-1120`/`IP-1151`
  had. `IP-1120`, `IP-1130`, and `IP-1151` have since all been implemented (`COMPLETE`, runs
  #6/#7/#8) — every tranche 2 package is now either `VERIFIED` (`IP-1150`) or `COMPLETE`
  (`IP-1120`/`IP-1130`/`IP-1140`/`IP-1151`), and all four `COMPLETE` ones could proceed to
  `09-package-verification` in parallel.

## Summary

- **Total Features (Feature Catalog):** 18 (`docs/features/feature-index.md`, up from 11 —
  FS-109/110/111 split from FS-106, FS-112/113/114/115 newly authored, per
  `docs/feature-planning/05-feature-review.md` Findings F-02/F-03/F-10)
- **Total Features covered by this plan:** 16 — FS-101 through FS-107, FS-109, FS-110, FS-111,
  FS-112, FS-113, FS-114, FS-115, FS-201, FS-301. FS-112/113/114/115 were added 2026-07 (tranche 2)
  after `07-implementation-planning`'s required build-status verification pass
  (`01-technical-work-breakdown.md` Tranche 1) — see that document for what was found.
- **Features excluded (unauthorized candidates, MSTR-006 §3):** 2 — FS-108, FS-202
- **Total Packages:** 18 (`packages/IP-1010` through `IP-3010`, plus `IP-1090`/`IP-1100`/`IP-1110`
  added 2026-07 tranche 1, plus `IP-1120`/`IP-1130`/`IP-1140`/`IP-1150`/`IP-1151` added 2026-07
  tranche 2; FS-105 and FS-115 are the two Features split across two lettered-equivalent packages
  each — `IP-1050`/`IP-1051` by subsystem seam, `IP-1150`/`IP-1151` by build-status seam — per the
  size-discipline precedent this corpus follows)
- **Critical Path Length:** 4 packages (`IP-1010`/`IP-1030` → `IP-1020`/`IP-1070` → `IP-2010` →
  `IP-3010`); the *effective remaining* critical path (excluding already-`VERIFIED` work) is now
  the single-package hop `IP-3010`, `READY` and authorized (run #9) since `IP-2010` reached
  `COMPLETE` 2026-07-03. `IP-1090`/`IP-1100`/`IP-1110`/`IP-1130`/`IP-1140` do not extend the
  critical path — none has a downstream consumer in this pass. Tranche 2's
  `IP-1150 → {IP-1120, IP-1151}` chain (never on the critical path) is now fully cleared (`IP-1150`
  reached `VERIFIED` 2026-07-03).
- **Parallel Work Opportunities:** 2 historical parallel waves among the (now-complete) as-built
  packages (6 packages, then 3 packages, running independently); the pre-existing forward-design
  surface's sequential constraint (`IP-2010` before `IP-3010`) is now moot — `IP-2010` is done and
  `IP-3010` is authorized. **One package remains coding-eligible (`READY`): `IP-3010`** —
  `IP-1140`/`IP-2010`/`IP-1120`/`IP-1130`/`IP-1151` each need only a verification pass, all five
  parallelizable with each other and with `IP-3010`'s implementation.
- **Package Status:** 12 `VERIFIED` (the original 11 as-built + `IP-1150`, verified 2026-07-03 via
  `VR-1150`), 5 `COMPLETE` pending verification (`IP-1140`, `IP-2010`, `IP-1120`, `IP-1130`,
  `IP-1151`), 1 `READY` (`IP-3010` — authorized run #9, its `IP-2010`-reaching-`COMPLETE` blocker
  cleared run #5); 0 `BLOCKED`, 0 `NOT STARTED`, 0 `IN PROGRESS`.

### Risks requiring architectural attention

1. **Authorization gate was the blocker, not design completeness, for `IP-2010` — now resolved for
   `IP-3010` too.** `IP-2010` was `READY` with every upstream dependency already `VERIFIED`,
   received its MSTR-006 §3 go-ahead 2026-07-03, and is now `COMPLETE` (implemented, pending
   `09-package-verification`). `IP-3010` was in exactly the state `IP-2010` was in — fully
   specified, its prerequisite work done (`IP-2010` reached `COMPLETE`) — and received its own
   explicit, separate go-ahead per MSTR-006 §3 in run #9 (2026-07-03), so it is now `READY` and
   eligible for `08-code-implementation`. The residual governance note: `IP-3010`'s own
   `Dependencies` field accepts `IP-2010` at `COMPLETE`, not `VERIFIED` — a future planner or
   `08-code-implementation` invocation should confirm that bar is still acceptable (rather than
   assuming it) if `IP-2010`'s eventual verification pass surfaces any material finding against its
   scoring-function output shape, since `IP-3010`'s schema is defined in terms of it.
2. **`IP-2010`'s "aware vs. unaware" divergence signal — resolved 2026-07-03 (`IP-2010` v1.1,
   `BL-0002`), one residual disclosure obligation remains.** The project owner chose to instrument
   an explicit decision-time signal (`custody_confidence_at_decision`, captured in `orders.py`'s
   `_exec_payload()` and read back by the scorer, never reconstructed post-hoc via `aar.state_at()`)
   rather than a post-hoc heuristic. The aware/unaware split reuses the existing
   `WEAPONS_QUALITY_THRESHOLD` as the "operator-visibly-marginal" band; per DOM-005 §7's
   validation-disclosure discipline, `IP-2010`'s report surface must still disclose that this band
   was calibrated for the engage hard-gate, not validated as a general perceptual/awareness
   boundary — see `IP-2010`'s own Risks section for the full statement. This is now a build-ready
   design, not an open architectural question.
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
6. **`IP-1140`'s shipped mechanism diverges from FR-6610's literal trigger/menu wording**, in the
   highest-consequence-per-line-of-code Feature in the catalog (the one place fog-of-war is
   enforced client-side, not server-side — see that package's own Risks). This is a verification
   finding, not a design defect this plan resolves: `09-package-verification` should explicitly
   adjudicate whether the manual-button/auto-cycle mechanism satisfies FR-6610's intent or needs a
   gap-closing package routed back through this pipeline.
7. **The Requirements Traceability Matrix carries a Title-column defect for `FR-4510`/`FR-6510`**
   (each shows the other's — and a third, unrelated capability's — title), discovered while
   authoring `IP-1120`/`IP-1130`. Both packages cite `01-functional-requirements.md`'s own
   definitions (the RTM's authoritative source) rather than the RTM's restated titles, so this does
   not affect either package's correctness — but the RTM itself should be corrected by whoever next
   runs `04-requirements-engineering`.
8. **`IP-1151`'s claimed downstream consumer does not exist in the code — a factual error in this
   plan's own Dependencies/Downstream framing, not merely an unverified claim.** `IP-1151`'s
   Dependencies field (and this section's own earlier draft) asserted that `FS-105`/`IP-1050`/
   `IP-1051` "already `VERIFIED`... for the command-filtering consequence of a Role Assignment."
   `08-code-implementation`'s run #8 searched `FS-105`, `IP-1050`, `IP-1051`, `buscommands.py`, and
   `session/manager.py` for any role-based (bus/payload/both) command-authorization concept and
   found none — every existing command check in this codebase is `cell`-based (blue/red/white
   ownership), not role-based. The Role Assignment record `IP-1151` now produces is real and
   correctly shaped per its own schema, but **nothing in the shipped codebase currently reads it**.
   `IP-1151`'s own Verification Checklist already flagged this as unconfirmed ("confirm the
   interface, don't assume it") — run #8 confirms the interface does not exist, which is a stronger
   finding than "unconfirmed." `09-package-verification` should not check this DoD item as
   cleanly satisfied; a future package (routed through `07-implementation-planning`, scoped against
   `FS-105`) would be needed to actually consume Role Assignment records for command filtering, if
   that enforcement is still wanted.

## Related

[`packages/INDEX.md`](packages/INDEX.md) · [`docs/features/feature-index.md`](../features/feature-index.md) ·
[`docs/implementations/INDEX.md`](../implementations/INDEX.md) (superseded prior corpus) ·
[`docs/master/MSTR-006-governance-principles.md`](../master/MSTR-006-governance-principles.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md) ·
`ROADMAP.md` (Theme: Implementation Packages)
