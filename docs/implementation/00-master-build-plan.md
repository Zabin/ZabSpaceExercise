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
remains gated on its own separate go-ahead in addition to `IP-2010` reaching `COMPLETE`, per
MSTR-006 §3's rule that approval of one package never implies approval of a related one.
`IP-1120`/`IP-1151` were, at authorization time, still functionally `BLOCKED` on `IP-1150` reaching
`VERIFIED` — that gate cleared the same day (`VR-1150`, see Package status below), so both are now
fully unblocked and `READY`.

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
| [IP-2010](packages/IP-2010-competency-assessment.md) | FS-201 Competency Assessment | Forward design | 🟡 READY *(authorized)* | Was `BLOCKED` (Unreconciled conflict with ADR-0017 — resolved 2026-07 by `ADR-0032`); **MSTR-006 §3 authorization obtained 2026-07-03** — no remaining blocker, ready for `08-code-implementation` |
| [IP-3010](packages/IP-3010-research-analytics.md) | FS-301 Research Analytics | Forward design | 🔴 BLOCKED *(not authorized)* | IP-2010 → `COMPLETE`, **and** authorization (MSTR-006 §3) — **not authorized** in the 2026-07-03 authorization round; a separate ADR-0029 conflict is resolved by `ADR-0033` but does not change this package's blocking status |
| [IP-1120](packages/IP-1120-classification-banner.md) | FS-112 Classification Banner | Partially built (gap-closing) | 🟡 READY *(authorized)* | **Unblocked 2026-07-03** — `IP-1150` reached `VERIFIED` (`VR-1150`); no remaining blocker, ready for `08-code-implementation` |
| [IP-1130](packages/IP-1130-observer-read-only-access.md) | FS-113 Observer Read-Only Access | Forward design | 🟡 READY *(authorized)* | **MSTR-006 §3 authorization obtained 2026-07-03** — no remaining blocker, ready for `08-code-implementation` |
| [IP-1140](packages/IP-1140-hot-seat-handoff.md) | FS-114 Hot-Seat Hand-Off Screen-Blank Menu | As-built (documented spec divergence) | 🔵 COMPLETE | None — awaiting `09-package-verification`, which should also adjudicate the documented trigger/menu divergence from FR-6610 |
| [IP-1150](packages/IP-1150-vignette-selection.md) | FS-115 §FR-4110 Vignette Selection & Parameter Tuning | As-built | ✅ VERIFIED | none — verified 2026-07-03, [`VR-1150`](verification/VR-1150-vignette-selection.md) |
| [IP-1151](packages/IP-1151-seat-role-assignment.md) | FS-115 §FR-4210 Seat-to-Role Assignment | Forward design | 🟡 READY *(authorized)* | **Unblocked 2026-07-03** — `IP-1150` reached `VERIFIED` (`VR-1150`); no remaining blocker, ready for `08-code-implementation` |

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
package verified through the formal `VR-xxxx` process). 1 is `COMPLETE` (`IP-1140`, as-built,
pending its own `09-package-verification` run). 4 are `READY` (`IP-2010`, `IP-1130`, `IP-1120`,
`IP-1151` — all forward design, fully specified, and all four now authorized; `IP-1120`/`IP-1151`
were unblocked by `IP-1150` reaching `VERIFIED`). 1 is `BLOCKED` (`IP-3010` — not authorized, and
still depends on `IP-2010` reaching `COMPLETE`).

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
IP-2010 (READY, authorized 2026-07-03 — ready for 08-code-implementation)
   │  must reach COMPLETE before IP-3010's schema is more than provisional
   ▼
IP-3010 (BLOCKED on IP-2010 → COMPLETE; not authorized)

IP-1150 (✅ VERIFIED 2026-07-03, VR-1150 — cleared)
   │  unblocked IP-1120/IP-1151 the moment it reached VERIFIED
   ├──► IP-1120 (READY, authorized 2026-07-03 — ready for 08-code-implementation)
   └──► IP-1151 (READY, authorized 2026-07-03 — ready for 08-code-implementation)

IP-1130 (READY, authorized 2026-07-03 — ready for 08-code-implementation)

IP-1140 (COMPLETE, awaiting 09-package-verification only — no coding work remains unless
         verification adjudicates the documented FR-6610 trigger/menu divergence and routes a
         gap-closing package back through this pipeline)
```

This tranche's `IP-1150 → {IP-1120, IP-1151}` fan-out is fully cleared as of 2026-07-03 — all three
are `VERIFIED`/`READY`. One sequencing thread remains in this plan: the pre-existing
`IP-2010 → IP-3010` chain. `IP-1130` (coding) and `IP-1140` (verification) are each standalone,
one-hop-from-done work with no sequencing dependency on anything else. Nothing else in this plan
has open sequencing questions — every other package is already `VERIFIED`.

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

Both four-hop chains converge at **IP-2010**, which is accordingly the single highest-leverage
package in this plan: it is the sole gate between "every upstream dependency already shipped" and
"the entire forward-design surface of this catalog." Because IP-1010/IP-1020/IP-1030/IP-1070 are
all `VERIFIED`, the *effective* remaining critical path — the one with real, un-shipped work on it —
is exactly the two-package chain in §"Implementation sequence (b)" above: **IP-2010 → IP-3010**,
gated at each step by the MSTR-006 §3 authorization rule, not by any missing prerequisite.

**Tranche 2 (FS-112–115)'s shorter, independent chain is now fully cleared (2026-07-03):**
`IP-1150 → IP-1120` and `IP-1150 → IP-1151` were never on the critical path above (length 2 < 4),
and `IP-1150` reaching `VERIFIED` (`VR-1150`) plus the same-day authorization round unblocked both
— `IP-1120` and `IP-1151` are now `READY` for `08-code-implementation`, no remaining gate. `IP-1130`
is likewise `READY` (authorized, no package-level dependency). `IP-1140` remains the tranche's one
open item: it needs only a verification pass (and a possible adjudication of its documented
FR-6610 divergence).

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
- **Among the remaining forward-design work:** there is **no parallel opportunity** — `IP-3010`'s
  schema is explicitly provisional until `IP-2010` lands (FS-301 §4's "must not reimplement FS-201's
  computation" constraint means the export schema is defined *in terms of* IP-2010's actual output
  shape, not merely its current sketch). The two packages must be authorized and executed
  sequentially, not concurrently.
- **Independent of the critical path:** `IP-1060` (White Cell Dashboard), `IP-1090` (Multiplayer /
  LAN Transport), `IP-1100` (Save & Resume), and `IP-1110` (AI-Red Doctrine Automation) have no
  downstream consumer in this pass and could always have been (and could still be, for any future
  rework) developed on entirely independent tracks from every other package and from each other.
- **Tranche 2 (FS-112–115):** `IP-1130` (Observer Read-Only Access) and `IP-1140` (Hot-Seat
  Hand-Off) have no package-level dependency on anything in this tranche or elsewhere in this plan
  and can be verified/implemented fully in parallel with each other and with `IP-1120`/`IP-1151`.
  `IP-1150` reached `VERIFIED` 2026-07-03 (`VR-1150`), clearing the one gate `IP-1120`/`IP-1151`
  had — the two are now themselves mutually independent and both `READY`, so `IP-1130`, `IP-1120`,
  and `IP-1151` (all authorized, all `READY`) could all three proceed to `08-code-implementation`
  in parallel today.

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
  `IP-3010`); the *effective remaining* critical path (excluding already-`VERIFIED` work) is 2
  packages: `IP-2010` → `IP-3010`. `IP-1090`/`IP-1100`/`IP-1110`/`IP-1130`/`IP-1140` do not extend
  the critical path — none has a downstream consumer in this pass. Tranche 2's `IP-1150 →
  {IP-1120, IP-1151}` chain (never on the critical path) is now fully cleared (`IP-1150` reached
  `VERIFIED` 2026-07-03).
- **Parallel Work Opportunities:** 2 historical parallel waves among the (now-complete) as-built
  packages (6 packages, then 3 packages, running independently); **zero** parallel opportunities
  remain in the pre-existing forward-design surface (`IP-2010`/`IP-3010` are strictly sequential).
  Tranche 2 now has **three fully independent, authorized, `READY` packages** (`IP-1130`, `IP-1120`,
  `IP-1151`) that could all proceed to `08-code-implementation` in parallel, plus `IP-1140` needing
  only a verification pass.
- **Package Status:** 12 `VERIFIED` (the original 11 as-built + `IP-1150`, verified 2026-07-03 via
  `VR-1150`), 1 `COMPLETE` pending verification (`IP-1140`), 4 `READY` and authorized (`IP-2010`,
  `IP-1130`, `IP-1120`, `IP-1151`), 1 `BLOCKED` (`IP-3010` — not authorized, depends on IP-2010
  reaching `COMPLETE`); 0 `NOT STARTED`, 0 `IN PROGRESS`.

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

## Related

[`packages/INDEX.md`](packages/INDEX.md) · [`docs/features/feature-index.md`](../features/feature-index.md) ·
[`docs/implementations/INDEX.md`](../implementations/INDEX.md) (superseded prior corpus) ·
[`docs/master/MSTR-006-governance-principles.md`](../master/MSTR-006-governance-principles.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md) ·
`ROADMAP.md` (Theme: Implementation Packages)
