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
> FS-115, FS-116, FS-117, FS-201, FS-301 (18 of 20 catalog entries; FS-108/FS-202 excluded, see
> §"Scope and exclusions". FS-116 was already planned via `IP-1160` — this line's omission of it
> was a pre-existing staleness, corrected here alongside FS-117's addition.)
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
Specification in some way — see the TWBS and each package's own header for the finding. At authoring
time, none of the five resulting packages (`IP-1120`, `IP-1130`, `IP-1140`, `IP-1150`, `IP-1151`)
was `VERIFIED`; `IP-1150` and `IP-1140` have since passed independent `09-package-verification`
(`VR-1150`, `VR-1140`) and are now `VERIFIED` — see Package status below for current state.

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
| [IP-1010](packages/IP-1010-mission-planning.md) | FS-101 Mission Planning | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #18)**, [`VR-1010`](verification/VR-1010-mission-planning.md), the first of 11 as-built packages closing the `BL-0004` evidence gap; full suite 566 passed/3 skipped, both permanent gates green |
| [IP-1020](packages/IP-1020-command-scheduling.md) | FS-102 Command Scheduling | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #20)**, [`VR-1020`](verification/VR-1020-command-scheduling.md), 2nd of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green; one Medium finding (the package's claimed lifecycle-state names don't match the code, functional guarantee still holds) |
| [IP-1030](packages/IP-1030-custody-management.md) | FS-103 Custody Management | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #21)**, [`VR-1030`](verification/VR-1030-custody-management.md), 3rd of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green, no functional discrepancies (one Low citation-drift finding) |
| [IP-1040](packages/IP-1040-sda-tasking.md) | FS-104 SDA Tasking | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #22)**, [`VR-1040`](verification/VR-1040-sda-tasking.md), 4th of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green, no functional discrepancies (one Low citation-drift finding) |
| [IP-1050](packages/IP-1050-spacecraft-operations-bus-payload.md) | FS-105 §3.1 Spacecraft Ops (bus/payload) | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #23)**, [`VR-1050`](verification/VR-1050-spacecraft-operations-bus-payload.md), 5th of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green, no functional discrepancies (one Low citation finding) |
| [IP-1051](packages/IP-1051-spacecraft-operations-effects-console.md) | FS-105 §3.2-4 Spacecraft Ops (effects) | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #24)**, [`VR-1051`](verification/VR-1051-spacecraft-operations-effects-console.md), 6th of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green, no functional discrepancies (one Low file-misattribution finding) |
| [IP-1060](packages/IP-1060-white-cell-dashboard.md) | FS-106 White Cell Dashboard *(v2.0, narrowed)* | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #25)**, [`VR-1060`](verification/VR-1060-white-cell-dashboard.md), 7th of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green, no functional discrepancies (one Low citation-drift finding) |
| [IP-1070](packages/IP-1070-after-action-review.md) | FS-107 After Action Review | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #26)**, [`VR-1070`](verification/VR-1070-after-action-review.md), 8th of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green, no functional discrepancies (one Low citation-drift finding) |
| [IP-1090](packages/IP-1090-multiplayer-session-transport.md) | FS-109 Multiplayer / LAN Session Transport | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #27)**, [`VR-1090`](verification/VR-1090-multiplayer-session-transport.md), 9th of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green, no functional discrepancies (one Low citation-drift finding) |
| [IP-1100](packages/IP-1100-save-and-resume.md) | FS-110 Save & Resume | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #28)**, [`VR-1100`](verification/VR-1100-save-and-resume.md), 10th of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green; one Medium finding (package overclaims Role Assignments are persisted — false, per `IP-1151`'s own text), two Low citation findings |
| [IP-1110](packages/IP-1110-ai-red-doctrine-automation.md) | FS-111 AI-Red Doctrine Automation | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #29)**, [`VR-1110`](verification/VR-1110-ai-red-doctrine-automation.md), 11th and last of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green, zero findings — the cleanest package in the sweep. **This closes `BL-0004`: all 18 packages on this plan now carry a formal `VR-xxxx` report.** |
| [IP-2010](packages/IP-2010-competency-assessment.md) | FS-201 Competency Assessment | Forward design | ✅ VERIFIED | **Verified 2026-07-04**, [`VR-2010`](verification/VR-2010-competency-assessment.md) — full suite 566 passed/3 skipped, both permanent gates green; RTM `FR-10110` updated. Two Medium findings against FS-201's own Acceptance Criteria scope (longitudinal per-trainee report, self-assessment-mode accessibility — see Risk item 9 below), not against this package's own claims |
| [IP-3010](packages/IP-3010-research-analytics.md) | FS-301 Research Analytics | Forward design | ✅ VERIFIED | **Verified 2026-07-04 (run #12)**, [`VR-3010`](verification/VR-3010-research-analytics.md) — full suite 566 passed/3 skipped, both permanent gates green; RTM `FR-10210` updated; `BL-0018`/`BL-0017` re-confirmed; no new findings |
| [IP-1120](packages/IP-1120-classification-banner.md) | FS-112 Classification Banner | Partially built (gap-closing) | ✅ VERIFIED | **Verified 2026-07-04 (run #13)**, [`VR-1120`](verification/VR-1120-classification-banner.md) — full suite 566 passed/3 skipped, both permanent gates green; RTM `FR-4510`/`NFR-3100` updated; both documented implementation deviations confirmed accurate |
| [IP-1130](packages/IP-1130-observer-read-only-access.md) | FS-113 Observer Read-Only Access | Forward design | ✅ VERIFIED | **Verified 2026-07-04 (run #14)**, [`VR-1130`](verification/VR-1130-observer-read-only-access.md) — full suite 566 passed/3 skipped, both permanent gates green; RTM `FR-6510` updated; `BL-0011`'s predicted route-guard drift investigated and found not yet materialized |
| [IP-1140](packages/IP-1140-hot-seat-handoff.md) | FS-114 Hot-Seat Hand-Off Screen-Blank Menu | As-built (documented spec divergence, adjudicated) | ✅ VERIFIED | none — verified 2026-07-03, [`VR-1140`](verification/VR-1140-hot-seat-handoff.md); the FR-6610 trigger/menu divergence was adjudicated **not satisfied** (High finding, routed to `07-implementation-planning` for a gap-closing package pending user prioritization — see Risk item 6 below) |
| [IP-1150](packages/IP-1150-vignette-selection.md) | FS-115 §FR-4110 Vignette Selection & Parameter Tuning | As-built | ✅ VERIFIED | none — verified 2026-07-03, [`VR-1150`](verification/VR-1150-vignette-selection.md) |
| [IP-1151](packages/IP-1151-seat-role-assignment.md) | FS-115 §FR-4210 Seat-to-Role Assignment | Forward design | ✅ VERIFIED | **Verified 2026-07-04 (run #15)**, [`VR-1151`](verification/VR-1151-seat-role-assignment.md) — full suite 566 passed/3 skipped, both permanent gates green; RTM `FR-4210` updated. `BL-0014` (no role-based command-filtering consumer exists) independently re-derived, not merely re-cited — still true. One new Low finding (`BL-0024`): `assign_role`'s White-Cell-only gate untested against `cell="observer"` specifically |
| [IP-1160](packages/IP-1160-role-scoped-command-enforcement.md) | FS-116 Role-Scoped Command Catalog & Assignment Scoping | Forward design | 🔴 BLOCKED | Not authorized (MSTR-006 §3). Closes `FEAT-3500`'s implementation gap (`11-release-readiness` Finding 2 / `BL-0049`) per `FS-116` v1.2 and `ADS-3500` v1.1's design (per-verb `bus`/`payload` classification — no third "defense" scope category). Every dependency (`IP-1151`, `IP-1050`, `IP-1051`) already `VERIFIED` — this package is specification-complete and would flip to `READY` the moment authorization is granted |
| [IP-1170](packages/IP-1170-isr-beam-mode-coverage.md) | FS-117 (prerequisite) ISR Beam-Mode Coverage — weather & missile-warning | Forward design | ✅ VERIFIED | **Verified 2026-07-05 (run #48, fresh session)**, [`VR-1170`](verification/VR-1170-isr-beam-mode-coverage.md) — full suite 586 passed/3 skipped, both permanent gates green; `BL-0053`'s original symptom independently re-confirmed gone, closing it. One Low citation-drift finding |
| [IP-1171](packages/IP-1171-typed-payload-bus-parameters.md) | FS-117 §FR-5170/FR-5180 Typed Payload & Bus Parameter Domain Model | Forward design | 🟢 READY | **Authorized 2026-07-05** (MSTR-006 §3, run #45). `IP-1170` reached `VERIFIED` 2026-07-05 (run #48) — its sole blocker is cleared; independent of `IP-1172`/`IP-1173` |
| [IP-1172](packages/IP-1172-per-cell-roe-enforcement.md) | FS-117 §FR-3420/NFR-2010 Per-Cell Rules of Engagement Enforcement | Forward design | ✅ VERIFIED | **Verified 2026-07-11 (fresh session)**, [`VR-1172`](verification/VR-1172-per-cell-roe-enforcement.md) — full suite 586 passed/3 skipped, both permanent gates green; both `_validate()` check sites independently confirmed to resolve per `order.cell` with zero legacy-shape branching inside `engine/`. Zero findings |
| [IP-1173](packages/IP-1173-vignette-creator-draft-session.md) | FS-117 §FR-5110 Vignette Creator Draft Session & Reverse Serialization | Forward design | ✅ VERIFIED | **Verified 2026-07-11 (fresh session)**, [`VR-1173`](verification/VR-1173-vignette-creator-draft-session.md) — full suite 586 passed/3 skipped, both permanent gates green; sole-writer-to-`VIGNETTE_DIR` and draft-session time-control rejection independently confirmed; independent manual round-trip beyond the existing tests. Zero findings |
| [IP-1174](packages/IP-1174-vignette-creator-ui-surfaces.md) | FS-117 §FR-5120-FR-5160 Vignette Creator UI Surfaces | Forward design | 🔴 BLOCKED | **Authorized 2026-07-05** (MSTR-006 §3, run #45). `IP-1172`/`IP-1173` reached `VERIFIED` 2026-07-11 — still blocked on `IP-1171` (`READY`, not yet implemented) — the last package in Tranche 3 to build |

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

**Update (2026-07-03, run #9 verification):** `IP-1140` passed `09-package-verification`
([`VR-1140`](verification/VR-1140-hot-seat-handoff.md)) and flipped to `VERIFIED` — full suite 559
passed/3 skipped, both permanent gates green, RTM `FR-6610` `Test`/`Impl. Package` cells (were
`UNASSIGNED`) corrected. **`BL-0003`'s FR-6610 trigger/menu divergence was adjudicated, not
waived:** the shipped manual-button/auto-cycle mechanism does **not** satisfy FR-6610's full intent
— a High-severity finding, routed to `07-implementation-planning` for a gap-closing package,
pending the user's explicit prioritization (see Risk item 6 below, updated accordingly).

**Update (2026-07-04, run #11 verification):** `IP-2010` passed `09-package-verification`
([`VR-2010`](verification/VR-2010-competency-assessment.md)) and flipped to `VERIFIED` — full
suite 566 passed/3 skipped, both permanent gates green, RTM `FR-10110` cell updated. `BL-0007`
adjudicated (the `index.html` panel inclusion was appropriate scope). `BL-0018` resolved (no
impact on `IP-3010`'s shipped schema). **Two Medium findings filed against FS-201's own Acceptance
Criteria being broader than what `IP-2010` built** — a longitudinal per-trainee report (already
disclosed as deferred by the package itself) and self-assessment/debrief-mode accessibility (not
implemented, not flagged as excluded) — see Risk item 9 below.

**Update (2026-07-04, run #12 verification):** `IP-3010` passed `09-package-verification`
([`VR-3010`](verification/VR-3010-research-analytics.md)) and flipped to `VERIFIED` — full suite
566 passed/3 skipped (unchanged since run #10), both permanent gates green, RTM `FR-10210` cell
updated. `BL-0018` (schema-stability vs. `IP-2010`) and `BL-0017` (imprecise `tools/` precedent
citation) both re-confirmed against the current tree. No new findings.

**Update (2026-07-04, run #13 verification):** `IP-1120` passed `09-package-verification`
([`VR-1120`](verification/VR-1120-classification-banner.md)) and flipped to `VERIFIED` — full
suite 566 passed/3 skipped, both permanent gates green, RTM `FR-4510`/`NFR-3100` cells updated.
Both documented Implementation Tasks deviations confirmed accurate, harmless, in-scope. One Low
finding (informational, a DoD-text naming imprecision — see `VR-1120`).

**Update (2026-07-04, run #14 verification):** `IP-1130` passed `09-package-verification`
([`VR-1130`](verification/VR-1130-observer-read-only-access.md)) and flipped to `VERIFIED` — full
suite 566 passed/3 skipped, both permanent gates green, RTM `FR-6510` cell updated. **`BL-0011`'s
predicted route-guard maintenance-drift risk was investigated directly and found not yet
materialized**: both mutating routes added since this package shipped (`IP-1151`'s
`/roles/assign`; this package's own `/observer/view` POST) reject Observer correctly via a
stricter White-Cell-only allowlist check. One Low finding (a test-coverage gap, not a functional
one — see `VR-1130`).

**Update (2026-07-04, run #15 verification):** `IP-1151` passed `09-package-verification`
([`VR-1151`](verification/VR-1151-seat-role-assignment.md)) and flipped to `VERIFIED` — full suite
566 passed/3 skipped, both permanent gates green, RTM `FR-4210` cell updated. `BL-0014` (no
role-based command-filtering consumer exists for the Role Assignment records this package
produces) was independently re-derived, not merely re-cited from the package's own text — still
true. One new Low finding (`BL-0024`, same family as `BL-0023`): `assign_role`'s White-Cell-only
gate is tested against `cell="blue"`, not `cell="observer"` specifically.

**All 18 packages in this plan are now `VERIFIED`** (the original 11 as-built + `IP-1150` +
`IP-1140` + `IP-2010` + `IP-3010` + `IP-1120` + `IP-1130` + `IP-1151`) — `IP-1140` carries a
standing user-accepted-risk note (Risk item 6) rather than an outstanding remediation. 0 are
`COMPLETE`, `READY`, `BLOCKED`, `NOT STARTED`, or `IN PROGRESS`. This closes the "iterate through
all `09-package-verification`" sweep the user requested (runs #11–#15). The tranche's only
open items are findings/backlog entries, not incomplete packages: `IP-1140`'s accepted risk (Risk
item 6), `IP-2010`'s two Medium FS-201-scope findings (Risk item 9), and `IP-1151`'s own `BL-0014`
(Medium, routed to `06-feature-specification`).

**Update (2026-07-04, runs #17–#29):** `10-integration-review` ran against the full 18-package
tranche (run #17) and came back clean on functional grounds — no Critical/High findings; see
[`integration-review-18-package-tranche.md`](../reviews/integration-review-18-package-tranche.md).
The review surfaced `BL-0004` (the 11 original as-built packages carried `VERIFIED` with no formal
`VR-xxxx` evidence, since that convention postdates their authoring) as a standing gap; the project
owner chose to retro-verify all 11 rather than accept the gap (run #18's gate check). That sweep is
now complete: `IP-1010` (`VR-1010`) through `IP-1110` (`VR-1110`), one package per run
(#18, #20–#29) — **every one of the 18 packages on this plan now carries a formal `VR-xxxx`
report**, closing `BL-0004` in full. The sweep's own findings (8 of 11 clean, 2 with a single
Medium finding each, 1 with zero findings) are tracked as `BL-0032`–`BL-0047` in the pipeline
backlog, none Critical/High. The next stage-appropriate step for this tranche is
`11-release-readiness`.

**Update (2026-07-05, run #31): `11-release-readiness` returned NO-GO.** Its
[release assessment](../reviews/release-assessment-fs-tracked-baseline.md) found `FEAT-3500`
(Role-Scoped Command Catalog & Assignment Scoping) — Must-priority, Release-1-bucketed — had zero
owning Feature Specification and zero implementation anywhere in the codebase, despite the release
plan's own text assuming its RTM `UNASSIGNED` cells were merely a citation gap (`BL-0049`, High).
The project owner chose Path A (implement, not descope): `06-feature-specification` authored
`FS-116`, `03-architecture-design-synthesis` authored `ADS-3500` resolving its two Open Questions,
and this pass added **`IP-1160`** — the nineteenth package on this plan, and the only one not yet
`VERIFIED`. `IP-1160` is fully specified and every one of its dependencies is already `VERIFIED`,
so it is `BLOCKED` on MSTR-006 §3 authorization alone, not on any remaining design or dependency
gap. `11-release-readiness` should be re-run once `IP-1160` reaches `VERIFIED`.

**Update (2026-07-05, runs #42-44): `04-requirements-engineering` closed `FS-117`'s requirements
gap, `06-feature-specification` amended `FS-117` to v1.1, and `07-implementation-planning` (run
#44) planned Tranche 3 in full.** Three design-fork decisions were resolved via `AskUserQuestion` before
packaging (typed engine fields for the payload/bus bridging mechanism; a nested per-cell `roe:`
YAML shape; auto-upgrade-on-save for legacy-ROE vignettes) — see
[`01-technical-work-breakdown.md`](01-technical-work-breakdown.md) Tranche 3. Five new packages —
**`IP-1170`** (prerequisite: `engine/isr.py` `BEAM_MODES` coverage for `weather`/`mw`, closing
`BL-0053`), **`IP-1171`** (typed payload/bus parameter Domain Model, `FR-5170`/`FR-5180`),
**`IP-1172`** (per-cell ROE enforcement, `FR-3420`/`NFR-2010`), **`IP-1173`** (draft-session
lifecycle + reverse serialization, `FR-5110`), **`IP-1174`** (the Creator's UI surfaces,
`FR-5120`-`FR-5160`) — bring the plan to 24 packages.

**Update (2026-07-05, run #45): the project owner authorized all five Tranche 3 packages for
`08-code-implementation` (MSTR-006 §3), via `AskUserQuestion` immediately after this planning pass.**
`IP-1170`, `IP-1172`, and `IP-1173` flip `BLOCKED → READY` (each had no package-level dependency, so
authorization was their only remaining gate). `IP-1171` and `IP-1174` remain `BLOCKED` — not on
authorization, which both now have, but on their own cited package dependencies (`IP-1170` for
`IP-1171`; `IP-1171`/`IP-1172`/`IP-1173` for `IP-1174`) not yet reaching `VERIFIED`, per this plan's
own "`READY` means fully specified and every dependency `VERIFIED`" rule. `IP-1160` (FS-116) is
unaffected — still `BLOCKED` on its own separate, unresolved authorization decision. `11-release-
readiness` should be re-run once `IP-1160` and all five Tranche 3 packages reach `VERIFIED`, or the
release plan's bucket assignment for `FEAT-5100`/`FS-117` should be confirmed first if it isn't
already Release-1/2 scoped.

**Update (2026-07-05, runs #46-#47): `IP-1170`, `IP-1172`, and `IP-1173` implemented.** `IP-1170`
(`engine/isr.py` `BEAM_MODES` for `weather`/`mw`, closing `BL-0053`) and `IP-1172` (`Vignette.roe`
+ cell-keyed `build_world()`/`engine/orders.py` ROE resolution, also fixing material drift in
`session/inprocess.py` + 7 pre-existing test files) both flipped `READY → COMPLETE`. `IP-1173`
(`InProcessSession.create_draft_session`/`save_vignette` + the new `content/vignette_export.py`
reverse-serialization module + two HTTP routes) also flipped `READY → COMPLETE`. Each pass's full
suite stayed green (575/3 → 579/3 → 586/3 skipped across the three), both permanent gates green
throughout. All three were `COMPLETE`, not `VERIFIED` — `09-package-verification` was attempted on
`IP-1170` in the same session that implemented it and stopped at that skill's own
same-session-independence gate; the project owner chose to defer verification to a fresh session
for all three rather than accept degraded independence.

**Update (2026-07-05, run #48, fresh session): `IP-1170` independently verified.**
[`VR-1170`](verification/VR-1170-isr-beam-mode-coverage.md) confirms every Definition-of-Done and
Verification-Checklist item against the live tree (full suite 586 passed/3 skipped — grown from
this package's own recorded 575/3 by the 11 tests `IP-1172`/`IP-1173` added after it, not a
regression — both permanent gates green), independently re-ran `BL-0053`'s original symptom and
confirmed it no longer reproduces, and closes `BL-0053`. `IP-1170` flips `COMPLETE → VERIFIED` —
one Low citation-drift finding (`orders.py`'s two call-site line numbers). `IP-1171` now depends
only on `IP-1170`, which is `VERIFIED` — `IP-1171` flips `BLOCKED → READY`. `IP-1172`/`IP-1173`
remain `COMPLETE`, still awaiting their own `09-package-verification` pass (this run verified
exactly one package, per that skill's own rule); `IP-1174` now depends on `IP-1171`/`IP-1172`/
`IP-1173`, one of which (`IP-1171`) is `READY` (not yet `VERIFIED`) and two of which are
`COMPLETE`, and stays `BLOCKED`.

**Update (2026-07-11, fresh session): `IP-1172` independently verified.**
[`VR-1172`](verification/VR-1172-per-cell-roe-enforcement.md) confirms every Definition-of-Done and
Verification-Checklist item against the live tree (full suite 586 passed/3 skipped, both permanent
gates green), independently re-derived both `_validate()` check sites and confirmed no
legacy-shape-awareness logic leaked into `engine/`. `IP-1172` flips `COMPLETE → VERIFIED` — zero
findings.

**Update (2026-07-11, same fresh session): `IP-1173` independently verified.**
[`VR-1173`](verification/VR-1173-vignette-creator-draft-session.md) confirms every
Definition-of-Done and Verification-Checklist item against the live tree (full suite 586 passed/3
skipped, both permanent gates green), independently confirmed `vignette_export.py`'s
`save_vignette()` is the sole writer to `VIGNETTE_DIR`, all five time-control routes reject a draft
session, and ran an independent manual round-trip beyond the existing tests. `IP-1173` flips
`COMPLETE → VERIFIED` — zero findings. `IP-1174` now depends only on `IP-1171` (`READY`, not yet
implemented) — stays `BLOCKED`.

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
IP-2010 (✅ VERIFIED 2026-07-04, VR-2010 — cleared)
   │  IP-3010's schema-stability question (BL-0018) confirmed resolved by VR-2010, re-confirmed
   │  again directly by VR-3010
   ▼
IP-3010 (✅ VERIFIED 2026-07-04, VR-3010 — cleared)

IP-1150 (✅ VERIFIED 2026-07-03, VR-1150 — cleared)
   │  unblocked IP-1120/IP-1151 the moment it reached VERIFIED
   ├──► IP-1120 (✅ VERIFIED 2026-07-04, VR-1120 — cleared)
   └──► IP-1151 (✅ VERIFIED 2026-07-04, VR-1151 — cleared)

IP-1130 (✅ VERIFIED 2026-07-04, VR-1130 — cleared)

IP-1140 (✅ VERIFIED 2026-07-03, VR-1140 — adjudicated: FR-6610's trigger/menu divergence is NOT
         satisfied; risk explicitly accepted by the project owner 2026-07-04 — no gap-closing
         package authorized, see Risk item 6)

IP-1160 (🔴 BLOCKED — not authorized, MSTR-006 §3; every dependency VERIFIED; the sole gap
         between "specified" and "buildable" is the project owner's go-ahead)

IP-1170 (✅ VERIFIED 2026-07-05, VR-1170 — cleared; closes BL-0053)
   │  prerequisite for full weather/mw engine effect
   ▼
IP-1171 (🟢 READY — authorized 2026-07-05, run #45; IP-1170 reached VERIFIED run #48)
   │
   ▼
IP-1174 (🔴 BLOCKED — authorized 2026-07-05, run #45; blocked solely on IP-1171 reaching
         VERIFIED — IP-1172/IP-1173 both cleared 2026-07-11)

IP-1172 (✅ VERIFIED 2026-07-11, VR-1172 — cleared)

IP-1173 (✅ VERIFIED 2026-07-11, VR-1173 — cleared)
```

This tranche's `IP-1150 → {IP-1120, IP-1151}` fan-out is fully cleared as of 2026-07-04 — `IP-1120`
is `VERIFIED` (run #13) and `IP-1151` is now `VERIFIED` too (`VR-1151`, run #15). The pre-existing
`IP-2010 → IP-3010` chain is fully `VERIFIED` end-to-end (`VR-2010` run #11; `VR-3010` run
#12). `IP-1130` is `VERIFIED` (`VR-1130`, run #14), and `IP-1140`/`IP-1120` are
`VERIFIED`. **All 18 original packages in this plan are `VERIFIED`** — `IP-1140` carries a standing
user-accepted-risk note (Risk item 6) rather than a gap-closing package. **`IP-1160` remains
`BLOCKED` on MSTR-006 §3 authorization alone** (FS-116, every dependency `VERIFIED`) — still awaiting
the project owner's go-ahead. **Tranche 3 (FS-117) was authorized 2026-07-05 (run #45), and
`IP-1170`/`IP-1172`/`IP-1173` were implemented the same day; `IP-1170`, `IP-1172`, and `IP-1173`
have since all passed independent verification (`VR-1170` run #48; `VR-1172`/`VR-1173`, same fresh
session, 2026-07-11) and are now `VERIFIED`, closing `BL-0053`.**
`IP-1171`
flipped `BLOCKED → READY` the moment `IP-1170` reached `VERIFIED`, and has not yet been
implemented. `IP-1174` remains `BLOCKED`,
purely on `IP-1171` reaching `VERIFIED`, not on authorization. This
tranche's remaining forward motion is a mix of standing findings/backlog work (Risk items 6/9,
`IP-1151`'s own `BL-0014`), `IP-1160`'s standing authorization gate, and `IP-1171`'s own build —
the next stage-appropriate step for the 18 pre-Tranche-3 `VERIFIED` packages
remains `10-integration-review`/`11-release-readiness`; for `IP-1160`, it is the project owner's
MSTR-006 §3 go-ahead; for Tranche 3, it is `08-code-implementation` on the now-sole-remaining
`READY` package, `IP-1171`.

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

IP-1151, IP-1050, IP-1051 ──────────────────────► IP-1160 (Role-Scoped Command Enforcement, FS-116)
                                                    [no downstream package in this pass]

IP-1170 (ISR Beam-Mode Coverage, FS-117 prereq) ──► IP-1171 (Typed Payload/Bus Params, FS-117) ──┐
                                                                                                    │
IP-1172 (Per-Cell ROE Enforcement, FS-117) ───────────────────────────────────────────────────────┼──► IP-1174 (Creator UI Surfaces, FS-117)
                                                                                                    │
IP-1173 (Creator Draft Session, FS-117) ──────────────────────────────────────────────────────────┘
```

Every edge above is drawn directly from the citing package's own **Dependencies** field (no edge is
inferred beyond what each package document already states). `IP-1060`, `IP-1090`, `IP-1100`,
`IP-1110`, `IP-1130`, `IP-1140`, and `IP-1160` are the packages with no downstream consumer inside
this pass's packages (FS-108, the dashboard extension `IP-1060` would otherwise feed, is out of
scope per §"Scope and exclusions"; IP-1090/1100/1110's only conceptual consumer, IP-1060 itself,
cites them as the mechanism its own trigger surface sits on top of — a description, not a
package-level build-order dependency `IP-1060`'s own `Dependencies` field asserts, so no edge is
drawn for it here either, consistent with how this graph already treats every other such
relationship). `IP-1150` gained two downstream consumers, `IP-1120` and `IP-1151`, per those two
packages' own `Dependencies` fields; `IP-1151`/`IP-1050`/`IP-1051` gain a downstream consumer,
`IP-1160`, per that package's own `Dependencies` field (an omission in this graph until this pass,
corrected alongside Tranche 3's addition). **Tranche 3 (FS-117, this pass):** `IP-1170` feeds
`IP-1171` (weather/mw engine parameterization); `IP-1171`, `IP-1172`, and `IP-1173` all feed
`IP-1174`, which has no downstream consumer of its own within this pass (a future mid-exercise
inject-menu reuse is explicitly out of scope, per `FS-117`'s own Scope boundary).

## Critical path

**Critical path length: 4 packages**, and it is the *longest* path in this graph with any remaining
actionable work — every package on it except the last two hops is already `VERIFIED`:

```
IP-1010 ──► IP-1020 ──► IP-2010 ──► IP-3010      (length 4)
IP-1030 ──► IP-1070 ──► IP-2010 ──► IP-3010      (length 4, co-critical)
```

Both four-hop chains converge at **IP-2010**, which was accordingly this plan's single
highest-leverage package: it was the sole gate between "every upstream dependency already shipped"
and "the entire forward-design surface of this catalog." **The entire critical path is now
`VERIFIED` end-to-end**: `IP-2010` verified 2026-07-04 (run #11, `VR-2010`), `IP-3010` verified
2026-07-04 (run #12, `VR-3010`) — `VR-3010` re-confirmed that `IP-2010`'s verification found no
material change to the output shape `IP-3010`'s schema was built against, closing the one
governance note this plan previously flagged (Risk item 1, updated accordingly).

**Tranche 2 (FS-112–115)'s shorter, independent chain is now fully cleared (2026-07-03):**
`IP-1150 → IP-1120` and `IP-1150 → IP-1151` were never on the critical path above (length 2 < 4).
`IP-1120` was implemented (run #6) and has since passed verification (`VERIFIED`, `VR-1120`, run
#13); `IP-1151` was implemented (run #8) and has since passed verification too (`VERIFIED`,
`VR-1151`, run #15). `IP-1130` was implemented (run #7) and has since passed verification too
(`VERIFIED`, `VR-1130`, run #14) — it had no package-level dependency at all. **All five tranche 2
packages are now `VERIFIED`** (`IP-1150`, `IP-1140` — whose verification pass adjudicated its
documented FR-6610 divergence as **not satisfied**, see Risk item 6 below — `IP-1120`, `IP-1130`,
`IP-1151`). This tranche has no open verification items remaining.

**`IP-1160` (FS-116) and Tranche 3 (FS-117) are not on the critical path.** `IP-1160` has no
package-level dependency chain of its own (every one of its dependencies is already `VERIFIED`) —
length 1; it remains `BLOCKED` purely on MSTR-006 §3 authorization. Tranche 3's longest internal
chain is `IP-1170 → IP-1171 → IP-1174` (length 3), shorter than the historic length-4 critical path
above, which remains fully `VERIFIED`. **Tranche 3 was authorized 2026-07-05 (run #45)** — `IP-1170`
has since reached `VERIFIED` (run #48), unblocking `IP-1171` to `READY`; `IP-1172` and `IP-1173`
have since also both reached `VERIFIED` (2026-07-11); `IP-1174` remains
`BLOCKED` solely on `IP-1171` reaching `VERIFIED`, the ordinary build-sequencing
gate every multi-package tranche has, not on authorization.

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
- **Among the remaining forward-design work:** `IP-2010` and `IP-3010` are both now `VERIFIED`
  (runs #11/#12) — `IP-3010`'s schema was confirmed to match `IP-2010`'s actual, verified output
  shape (FS-301 §4's "must not reimplement FS-201's computation" constraint satisfied); `IP-3010`
  received its own MSTR-006 §3 authorization 2026-07-03 (run #9), was implemented 2026-07-04
  (run #10), and independently verified the same day (run #12) — the critical path's forward
  motion is now fully closed out.
- **Independent of the critical path:** `IP-1060` (White Cell Dashboard), `IP-1090` (Multiplayer /
  LAN Transport), `IP-1100` (Save & Resume), and `IP-1110` (AI-Red Doctrine Automation) have no
  downstream consumer in this pass and could always have been (and could still be, for any future
  rework) developed on entirely independent tracks from every other package and from each other.
- **Tranche 2 (FS-112–115):** `IP-1130` (Observer Read-Only Access) and `IP-1140` (Hot-Seat
  Hand-Off) had no package-level dependency on anything in this tranche or elsewhere in this plan
  and could be verified/implemented fully in parallel with each other and with `IP-1120`/`IP-1151`.
  `IP-1150` reached `VERIFIED` 2026-07-03 (`VR-1150`), clearing the one gate `IP-1120`/`IP-1151`
  had. `IP-1120`, `IP-1130`, and `IP-1151` were implemented (`COMPLETE`, runs #6/#7/#8), then all
  passed verification in turn (`VERIFIED`, `VR-1140`/`VR-1120`/`VR-1130`/`VR-1151`, runs
  #9/#13/#14/#15). **Every tranche 2 package is now `VERIFIED`** (`IP-1150`, `IP-1140`, `IP-1120`,
  `IP-1130`, `IP-1151`) — no package in this tranche remains open.
- **Tranche 3 (FS-117):** `IP-1170`, `IP-1172`, and `IP-1173` had no package-level dependency on
  anything in this tranche or elsewhere in this plan and were authorized/built fully in parallel
  with each other, then all three independently verified (`VR-1170`/`VR-1172`/`VR-1173`). `IP-1171`
  depends only on `IP-1170`, now `VERIFIED` — `IP-1171` is
  `READY`, not yet implemented. `IP-1174` is the sole package still requiring `IP-1171` at
  least `COMPLETE` — the natural last package in this tranche's build order, now that `IP-1172`/
  `IP-1173` have both cleared `VERIFIED`.

## Summary

- **Total Features (Feature Catalog):** 20 (`docs/features/feature-index.md`, up from 11 —
  FS-109/110/111 split from FS-106, FS-112/113/114/115 newly authored, per
  `docs/feature-planning/05-feature-review.md` Findings F-02/F-03/F-10; FS-116 newly authored
  2026-07-05 per `11-release-readiness` Finding 2 / `BL-0049`; FS-117 newly authored 2026-07-05,
  consolidating `FEAT-5100`)
- **Total Features covered by this plan:** 18 — FS-101 through FS-107, FS-109, FS-110, FS-111,
  FS-112, FS-113, FS-114, FS-115, FS-116, FS-117, FS-201, FS-301. FS-112/113/114/115 were added
  2026-07 (tranche 2) after `07-implementation-planning`'s required build-status verification pass
  (`01-technical-work-breakdown.md` Tranche 1) — see that document for what was found. FS-116 was
  added 2026-07-05 (Tranche 2 of the *implementation* plan). FS-117 was added 2026-07-05
  (Tranche 3), per `01-technical-work-breakdown.md`.
- **Features excluded (unauthorized candidates, MSTR-006 §3):** 2 — FS-108, FS-202
- **Total Packages:** 24 (`packages/IP-1010` through `IP-3010`, plus `IP-1090`/`IP-1100`/`IP-1110`
  added 2026-07 tranche 1, plus `IP-1120`/`IP-1130`/`IP-1140`/`IP-1150`/`IP-1151` added 2026-07
  tranche 2, plus `IP-1160` added 2026-07-05 (Implementation Tranche 2), plus `IP-1170`-`IP-1174`
  added 2026-07-05 (Implementation Tranche 3); FS-105 and FS-115 are the two Features split across
  two lettered-equivalent packages each — `IP-1050`/`IP-1051` by subsystem seam, `IP-1150`/`IP-1151`
  by build-status seam — per the size-discipline precedent this corpus follows; FS-116 is not
  split; FS-117 splits across five packages by architectural seam (see
  `01-technical-work-breakdown.md` Tranche 3))
- **Critical Path Length:** 4 packages (`IP-1010`/`IP-1030` → `IP-1020`/`IP-1070` → `IP-2010` →
  `IP-3010`); this entire chain is now `VERIFIED` end-to-end (`VR-2010` run #11, `VR-3010` run #12).
  `IP-1090`/`IP-1100`/`IP-1110`/`IP-1130`/`IP-1140`/`IP-1160` do not extend the critical path — none
  has a downstream consumer in this pass. Tranche 2's `IP-1150 → {IP-1120, IP-1151}` chain (never
  on the critical path) is now fully cleared (`IP-1150` reached `VERIFIED` 2026-07-03; `IP-1151`
  reached `VERIFIED` 2026-07-04). Tranche 3's longest internal chain, `IP-1170 → IP-1171 → IP-1174`
  (length 3), is also shorter than the critical path and does not extend it.
- **Parallel Work Opportunities:** 2 historical parallel waves among the (now-complete) as-built
  packages (6 packages, then 3 packages, running independently); the pre-existing forward-design
  surface's sequential constraint (`IP-2010` before `IP-3010`) is fully resolved — both are now
  `VERIFIED`. `IP-1160` is independent of every other package. **Tranche 3, authorized 2026-07-05
  (run #45), implemented runs #46-#47, `IP-1170`/`IP-1172`/`IP-1173` all independently verified
  (run #48; 2026-07-11 fresh session):** `IP-1170`/`IP-1172`/`IP-1173` were mutually independent
  and are all now `VERIFIED`; `IP-1171` depends only on `IP-1170` and is `READY`, not yet
  implemented; `IP-1174` is the sole package still needing `IP-1171` `VERIFIED` first.
- **Package Status:** **21 `VERIFIED`, 0 `COMPLETE`, 1 `READY`, 2 `BLOCKED`** (`IP-1171` —
  authorized 2026-07-05,
  `READY` since `IP-1170` reached `VERIFIED` run #48, not yet implemented; `IP-1160` — every
  dependency already `VERIFIED`, authorization is the sole remaining gate, still not on record;
  `IP-1174` — authorized 2026-07-05, `BLOCKED` solely on `IP-1171` reaching `VERIFIED`). The 21
  `VERIFIED` packages are the original 11 as-built + `IP-1150` + `IP-1140` + `IP-2010` + `IP-3010` +
  `IP-1120` + `IP-1130` + `IP-1151` + `IP-1170` + `IP-1172` + `IP-1173`, the last nine verified
  2026-07-03 through 2026-07-11 via `VR-1140`/`VR-2010`/`VR-3010`/`VR-1120`/`VR-1130`/`VR-1151`/
  `VR-1170`/`VR-1172`/`VR-1173`. 0 `NOT STARTED`, 0 `IN PROGRESS`. The "iterate through all
  `09-package-verification`" sweep (runs #11–#15) closed 18 packages; `IP-1170` (run #48) and
  `IP-1172`/`IP-1173` (2026-07-11, this pass) bring all five of Tranche 3's implemented-or-eligible
  packages except `IP-1171` to `VERIFIED`. `IP-1171` is `READY` for `08-code-implementation`;
  `IP-1174` and `IP-1160` remain `BLOCKED`.

### Risks requiring architectural attention

1. **Authorization gate was the blocker, not design completeness, for `IP-2010` — resolved for
   `IP-3010` too, and both are now fully `VERIFIED`, closing this risk out.** `IP-2010` was `READY`
   with every upstream dependency already `VERIFIED`, received its MSTR-006 §3 go-ahead
   2026-07-03, was implemented, and passed `09-package-verification` 2026-07-04 (`VR-2010`, run
   #11). `IP-3010` followed the same path — authorized run #9, implemented run #10, verified run
   #12 (`VR-3010`). The residual governance note this risk previously flagged (`IP-3010`'s own
   `Dependencies` field accepted `IP-2010` at `COMPLETE`, not `VERIFIED`, as the threshold to build
   against) is now moot: `VR-2010` confirmed `IP-2010`'s scoring-function output shape was
   unchanged, and `VR-3010` independently re-confirmed that finding against the current tree. No
   further action needed.
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
   separate authorization and the institution's own IRB/ethics process. **`IP-3010`'s 2026-07-04
   implementation (run #10) confirmed this boundary was respected**: `RunRecord` carries only
   `vignette_id`/`seed`/`condition_label`/IP-2010's rubric output, no trainee-identifying or
   cross-institution field of any kind. This is restated once more here because it is the one
   non-goal in this plan whose violation would have consequences outside the engineering process
   (regulatory/ethical), not merely a defect to fix in code — a standing constraint on any future
   revision of this package, not closed by this implementation being clean today.
6. **`IP-1140`'s shipped mechanism diverges from FR-6610's literal trigger/menu wording — adjudicated
   2026-07-03 (`VR-1140`, run #9): the divergence is NOT accepted as satisfying FR-6610's intent.
   Risk explicitly accepted by the project owner 2026-07-04 (run #10) — no gap-closing package
   authorized.** In the highest-consequence-per-line-of-code Feature in the catalog (the one place
   fog-of-war is enforced client-side, not server-side), the missing automatic-trigger detection
   leaves a real, unmitigated failure mode: an operator who forgets to click ⏸ Handover before
   stepping away leaves their cell's content on screen indefinitely with no system-side prompt.
   `IP-1140` itself is `VERIFIED` (it accurately, non-overclaimingly documented this exact gap and
   asked for exactly this adjudication). Per this plan's own severity-honesty discipline, this
   High-severity finding (`BL-0015`) could not be silently deferred — it was put to the project
   owner, who explicitly accepted the risk ("I accept the risk of a cell not blanking the screen
   during handover as long as hot seat is an option") rather than authorizing remediation now.
   `BL-0015` closed `DEFERRED`, with a named revisit trigger: reconsider if hot-seat mode's
   continued availability is ever reconsidered, or at the next `10-integration-review`.
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
   finding than "unconfirmed." **Independently re-derived by `09-package-verification` (`VR-1151`,
   run #15): still true, unchanged.** `role_assignments` remains read only by `staffing_report()`;
   no file added since run #8 (`IP-1130`'s Observer seat, `IP-1120`'s classification banner,
   `IP-2010`'s assessment scoring, `IP-3010`'s research batch runner) introduces role-based command
   filtering. `IP-1151` is now `VERIFIED` with this DoD item correctly left unsatisfied as literally
   stated (tracked as `BL-0014`, `DEFERRED`). A future package (routed through
   `07-implementation-planning`, scoped against `FS-105`) would be needed to actually consume Role
   Assignment records for command filtering, if that enforcement is still wanted.
9. **`IP-2010`'s verification (2026-07-04, `VR-2010`, run #11) found FS-201's own Acceptance
   Criteria are broader than what `IP-2010` built** — two Medium findings against the *Feature
   Specification's* claimed closure, not against `IP-2010`'s own honesty (it never claimed to
   satisfy either). (a) FS-201 states "a longitudinal per-trainee report aggregates
   dimension-by-dimension results across exercises" as an Acceptance Criterion — entirely
   unimplemented, but this was already explicitly, knowingly deferred by `IP-2010`'s own
   Implementation Tasks item 5 (flagged there as a future `IP-2011`-equivalent's job), so not a
   surprise. (b) FS-201 states the report must be "accessible in all three assessment modes...
   self-assessment/debrief (FS-107)" — the shipped panel is White-Cell-only
   (`ui_web/static/index.html`'s `white-only` CSS class on `#assessment-panel`); Blue/Red operators
   have no in-UI path to their own rubric. Unlike (a), this exclusion was never flagged anywhere in
   `IP-2010`'s own text — it appears to have been missed at authoring time. Routed to
   `06-feature-specification` to reconcile FS-201's Acceptance Criteria against what was actually
   built, before any future package attempts to "close" FS-201 further.

## Related

[`packages/INDEX.md`](packages/INDEX.md) · [`docs/features/feature-index.md`](../features/feature-index.md) ·
[`docs/implementations/INDEX.md`](../implementations/INDEX.md) (superseded prior corpus) ·
[`docs/master/MSTR-006-governance-principles.md`](../master/MSTR-006-governance-principles.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md) ·
`ROADMAP.md` (Theme: Implementation Packages)
