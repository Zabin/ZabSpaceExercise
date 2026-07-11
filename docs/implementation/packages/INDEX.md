# Implementation Packages — Index

[↑ Master Build Plan](../00-master-build-plan.md) · [Docs index](../../INDEX.md) ·
[Feature index](../../features/feature-index.md)

Implementation Packages (`IP-xxxx`) convert an approved Feature Specification (`FS-xxx`) into a
build-ready unit of work: architecture components, interfaces, files, tasks, tests, and a
Definition-of-Done/Verification checklist. Each package traces to exactly one Feature Specification
(or a lettered slice of one, where a Feature was too large for a single package, e.g. FS-105 →
IP-1050 + IP-1051) and to one or more Functional/Non-Functional Requirements where an explicit
citation exists.

```
Feature Specification (FS-xxx) → Implementation Package (IP-xxxx, here) → Code → Tests
```

**This tree supersedes [`docs/implementations/`](../../implementations/INDEX.md) (`IMP-xxxA`) as the
canonical Implementation Package corpus.** See
[`../00-master-build-plan.md`](../00-master-build-plan.md) §"Relationship to the prior
`docs/implementations/` corpus" for the full rationale; the prior corpus's files remain in place
with a superseded-by banner, not deleted, since they carry the same underlying design content this
tree re-derives under a different template/ID scheme/location.

## Two distinct situations this tier covers

Carried forward unchanged from the prior corpus's own framing (still accurate):

| Situation | What the package does | Applies to |
|---|---|---|
| **Capability already implemented, independently verified** | Documents the *actual* existing architecture against its Feature Spec — a retroactive as-built record, verified against real module/class/method names in `spacesim/`. Status `VERIFIED`. | FS-101 through FS-107, FS-109, FS-110, FS-111 |
| **Capability already implemented, not yet independently verified** | Same as above, but authored by `07-implementation-planning` rather than confirmed by a separate `09-package-verification` pass — per that skill's own status vocabulary, enters at `COMPLETE`, not `VERIFIED`. | FS-114, FS-115 (FR-4110 slice, `IP-1150`) |
| **Capability partially implemented (gap-closing)** | Documents what already exists, scopes the remaining gap as a build-ready forward design, and does not claim the Feature is closed. Status `READY` or `BLOCKED`, same authorization rule as a fully forward-design package. | FS-112 |
| **Capability not yet implemented** | Proposes a from-scratch design satisfying the Feature Spec's requirements — genuinely forward-looking, not yet built, and **not authorized for coding merely by being documented** (MSTR-006 §3). Status `READY` or `BLOCKED`. | FS-201, FS-301, FS-113, FS-115 (FR-4210 slice, `IP-1151`) |

FS-108 and FS-202 have no Implementation Package in this pass — both remain unauthorized
"(candidate)" Feature Specs ([feature-index.md](../../features/feature-index.md)); per
[MSTR-006](../../master/MSTR-006-governance-principles.md) §3, no package work may begin against an
unauthorized FS.

## Index

| ID | Title | FS | Situation | Status |
|---|---|---|---|---|
| [IP-1010](IP-1010-mission-planning.md) | Mission Planning — dry-run preview & window/Δv display | [FS-101](../../features/FS-101-mission-planning.md) | As-built | ✅ VERIFIED ([`VR-1010`](../verification/VR-1010-mission-planning.md), 2026-07-04) |
| [IP-1020](IP-1020-command-scheduling.md) | Command Scheduling — Order/OrderSystem lifecycle | [FS-102](../../features/FS-102-command-scheduling.md) | As-built | ✅ VERIFIED ([`VR-1020`](../verification/VR-1020-command-scheduling.md), 2026-07-04) |
| [IP-1030](IP-1030-custody-management.md) | Custody Management — Track confidence model | [FS-103](../../features/FS-103-custody-management.md) | As-built | ✅ VERIFIED ([`VR-1030`](../verification/VR-1030-custody-management.md), 2026-07-04) |
| [IP-1040](IP-1040-sda-tasking.md) | SDA Tasking — sensor tasking & SSN request lifecycle | [FS-104](../../features/FS-104-sda-tasking.md) | As-built | ✅ VERIFIED ([`VR-1040`](../verification/VR-1040-sda-tasking.md), 2026-07-04) |
| [IP-1050](IP-1050-spacecraft-operations-bus-payload.md) | Spacecraft Operations — bus/payload command & telemetry | [FS-105](../../features/FS-105-spacecraft-operations.md) §3.1 | As-built | ✅ VERIFIED ([`VR-1050`](../verification/VR-1050-spacecraft-operations-bus-payload.md), 2026-07-04) |
| [IP-1051](IP-1051-spacecraft-operations-effects-console.md) | Spacecraft Operations — effect resolution & console UX | [FS-105](../../features/FS-105-spacecraft-operations.md) §3.2-4 | As-built | ✅ VERIFIED ([`VR-1051`](../verification/VR-1051-spacecraft-operations-effects-console.md), 2026-07-04) |
| [IP-1060](IP-1060-white-cell-dashboard.md) | White Cell Dashboard — god-view, inject, clock-authority trigger & adjudication *(v2.0, narrowed)* | [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.0 | As-built | ✅ VERIFIED ([`VR-1060`](../verification/VR-1060-white-cell-dashboard.md), 2026-07-04) |
| [IP-1070](IP-1070-after-action-review.md) | After Action Review — replay/scrub/branch-compare | [FS-107](../../features/FS-107-after-action-review.md) | As-built | ✅ VERIFIED ([`VR-1070`](../verification/VR-1070-after-action-review.md), 2026-07-04) |
| [IP-1090](IP-1090-multiplayer-session-transport.md) | Multiplayer / LAN Session Transport — lazy clock, mutation locking, hot-seat/LAN sharing | [FS-109](../../features/FS-109-multiplayer-session-transport.md) | As-built | ✅ VERIFIED ([`VR-1090`](../verification/VR-1090-multiplayer-session-transport.md), 2026-07-04) |
| [IP-1100](IP-1100-save-and-resume.md) | Save & Resume — deterministic round trip & content/session split | [FS-110](../../features/FS-110-save-and-resume.md) | As-built | ✅ VERIFIED ([`VR-1100`](../verification/VR-1100-save-and-resume.md), 2026-07-04) |
| [IP-1110](IP-1110-ai-red-doctrine-automation.md) | AI-Red Doctrine Automation — doctrine-preset-driven Red activity generation | [FS-111](../../features/FS-111-ai-red-doctrine-automation.md) | As-built | ✅ VERIFIED ([`VR-1110`](../verification/VR-1110-ai-red-doctrine-automation.md), 2026-07-04) |
| [IP-2010](IP-2010-competency-assessment.md) | Competency Assessment — rubric computation | [FS-201](../../features/FS-201-competency-assessment.md) | Forward design | ✅ VERIFIED (2026-07-04, [`VR-2010`](../verification/VR-2010-competency-assessment.md) — two Medium findings against FS-201's own Acceptance Criteria scope, not against this package; briefly `BLOCKED` 2026-07-02 on an ADR-0017 conflict, resolved same-day by `ADR-0032` — see the package's own header) |
| [IP-3010](IP-3010-research-analytics.md) | Research Analytics — multi-run export | [FS-301](../../features/FS-301-research-analytics.md) | Forward design | ✅ VERIFIED (2026-07-04, [`VR-3010`](../verification/VR-3010-research-analytics.md) — `BL-0018`/`BL-0017` re-confirmed, no new findings) |
| [IP-1120](IP-1120-classification-banner.md) | Classification Banner — wire the render/export path to the vignette's classification value | [FS-112](../../features/FS-112-classification-banner.md) | Partially built (gap-closing) | ✅ VERIFIED (2026-07-04, [`VR-1120`](../verification/VR-1120-classification-banner.md) — both documented deviations confirmed accurate, one Low informational finding) |
| [IP-1130](IP-1130-observer-read-only-access.md) | Observer Read-Only Access — designated read-only seat, server-side mutation rejection | [FS-113](../../features/FS-113-observer-read-only-access.md) | Forward design | ✅ VERIFIED (2026-07-04, [`VR-1130`](../verification/VR-1130-observer-read-only-access.md) — `BL-0011`'s predicted drift investigated, not yet materialized) |
| [IP-1140](IP-1140-hot-seat-handoff.md) | Hot-Seat Hand-Off Screen-Blank Menu — blank/blur/resume overlay | [FS-114](../../features/FS-114-hot-seat-handoff.md) | As-built (documented spec divergence, adjudicated) | ✅ VERIFIED (2026-07-03, [`VR-1140`](../verification/VR-1140-hot-seat-handoff.md) — FR-6610's trigger/menu divergence adjudicated **not satisfied**, High finding routed to `07-implementation-planning`) |
| [IP-1150](IP-1150-vignette-selection.md) | Session Setup: Vignette Selection & Parameter Tuning | [FS-115](../../features/FS-115-session-setup.md) §FR-4110 | As-built | ✅ VERIFIED (2026-07-03, [`VR-1150`](../verification/VR-1150-vignette-selection.md)) |
| [IP-1151](IP-1151-seat-role-assignment.md) | Session Setup: Seat-to-Role Assignment | [FS-115](../../features/FS-115-session-setup.md) §FR-4210 | Forward design | ✅ VERIFIED (2026-07-04, run #15, `VR-1151` — one Definition-of-Done caveat re-confirmed, not resolved, see the package's own header) |
| [IP-1160](IP-1160-role-scoped-command-enforcement.md) | Role-Scoped Command Catalog & Assignment Scoping | [FS-116](../../features/FS-116-role-scoped-command-catalog.md) | Forward design | 🔴 BLOCKED (not authorized — MSTR-006 §3; every dependency `VERIFIED`) |
| [IP-1170](IP-1170-isr-beam-mode-coverage.md) | ISR Beam-Mode Coverage — weather & missile-warning (`BL-0053` prerequisite) | [FS-117](../../features/FS-117-vignette-creator.md) (prerequisite) | Forward design | ✅ VERIFIED (2026-07-05, [`VR-1170`](../verification/VR-1170-isr-beam-mode-coverage.md) — full suite 586 passed/3 skipped, both permanent gates green; one Low citation-drift finding) |
| [IP-1171](IP-1171-typed-payload-bus-parameters.md) | Typed Payload & Bus Parameter Domain Model | [FS-117](../../features/FS-117-vignette-creator.md) §`FR-5170`/`FR-5180` | Forward design | 🔵 COMPLETE (implemented 2026-07-11; 12 new tests, full suite 598 passed/3 skipped, both permanent gates green; awaiting `09-package-verification`) |
| [IP-1172](IP-1172-per-cell-roe-enforcement.md) | Per-Cell Rules of Engagement Enforcement | [FS-117](../../features/FS-117-vignette-creator.md) §`FR-3420`/`NFR-2010` | Forward design | ✅ VERIFIED (2026-07-11, [`VR-1172`](../verification/VR-1172-per-cell-roe-enforcement.md) — full suite 586 passed/3 skipped, both permanent gates green; zero findings) |
| [IP-1173](IP-1173-vignette-creator-draft-session.md) | Vignette Creator Draft Session & Reverse Serialization | [FS-117](../../features/FS-117-vignette-creator.md) §`FR-5110` | Forward design | ✅ VERIFIED (2026-07-11, [`VR-1173`](../verification/VR-1173-vignette-creator-draft-session.md) — full suite 586 passed/3 skipped, both permanent gates green; zero findings) |
| [IP-1174](IP-1174-vignette-creator-ui-surfaces.md) | Vignette Creator UI Surfaces | [FS-117](../../features/FS-117-vignette-creator.md) §`FR-5120`-`FR-5160` | Forward design | 🔴 BLOCKED (authorized 2026-07-05 — MSTR-006 §3; blocked solely on `IP-1171` reaching `VERIFIED`) |

FS-108/FS-202 have no Implementation Package (unauthorized candidates, MSTR-006 §3). **IP-1170
through IP-1174 are new (2026-07-05)** — Tranche 3, the five packages planned against `FS-117`
(Vignette Creator), split by seam (see [`../01-technical-work-breakdown.md`](../01-technical-work-breakdown.md)
Tranche 3 for the full split rationale and the three design-fork decisions resolved before
packaging). **All five authorized for coding 2026-07-05** (MSTR-006 §3, project owner). `IP-1170`,
`IP-1172`, and `IP-1173` are now all `VERIFIED` (2026-07-05, [`VR-1170`](../verification/VR-1170-isr-beam-mode-coverage.md);
2026-07-11, [`VR-1172`](../verification/VR-1172-per-cell-roe-enforcement.md)/
[`VR-1173`](../verification/VR-1173-vignette-creator-draft-session.md) — the latter two verified in
the same fresh session; full suite green throughout; `VR-1170` closes `BL-0053`); `IP-1171` has
since been implemented (`COMPLETE`, 2026-07-11 — its sole blocker, `IP-1170` reaching `VERIFIED`,
was cleared first); `IP-1174` remains
`BLOCKED` solely on `IP-1171` reaching `VERIFIED`, per this plan's own "`READY` means fully
specified and every dependency `VERIFIED`" rule. **IP-1090,
IP-1100, IP-1110 are new (2026-07)**, split out of IP-1060 v1.0 per `docs/feature-planning/
05-feature-review.md` Finding F-03, mirroring the FS-106→FS-106/109/110/111 split — see IP-1060
v2.0's own header note. **IP-1120, IP-1130, IP-1140, IP-1150, IP-1151 are new (2026-07)**, the
first Implementation Packages written against FS-112/113/114/115 — see
[`../01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) Tranche 1 for the
build-status verification pass and split rationale each required. **`IP-1150` is now `VERIFIED`**
(2026-07-03, [`VR-1150`](../verification/VR-1150-vignette-selection.md) — the first package in
this tranche, and the first in this plan, verified through the formal `09-package-verification`
process). **`IP-1140` is also now `VERIFIED`** (2026-07-03, run #9,
[`VR-1140`](../verification/VR-1140-hot-seat-handoff.md)) — its documented FR-6610 trigger/menu
divergence was adjudicated during that pass and found **not** to satisfy FR-6610's full intent; a
High-severity finding is now routed to `07-implementation-planning` for a gap-closing package,
pending the user's explicit prioritization (see `VR-1140` and Master Build Plan Risk item 6).
**`IP-2010` is now `VERIFIED`** (2026-07-04, run #11,
[`VR-2010`](../verification/VR-2010-competency-assessment.md) —
`session/assessment.py` + `custody_confidence_at_decision` in `orders.py`/`custody.py` confirmed
against the live tree; two Medium findings filed against FS-201's own Acceptance Criteria scope,
routed to `06-feature-specification`, not against this package). **`IP-1120` is now `VERIFIED`**
(2026-07-04, run #13, [`VR-1120`](../verification/VR-1120-classification-banner.md) — one resolved
`classification` value threaded through `session/manager.py`/`inprocess.py`/`aar.py`/`ui_web/`
confirmed against the live tree; both documented implementation deviations confirmed accurate).
**`IP-1130` is now `VERIFIED`** (2026-07-04, run #14,
[`VR-1130`](../verification/VR-1130-observer-read-only-access.md) — a server-side
mutation-rejection guard on every mutating route plus a White-Cell-designated Observer read path
in `session/inprocess.py`/`ui_web/server.py`/`ui_web/static/` confirmed against the live tree;
`BL-0011`'s predicted route-guard maintenance-drift risk investigated directly and found not yet
materialized). **`IP-1151` is now `VERIFIED`** (2026-07-04, run #15,
[`VR-1151`](../verification/VR-1151-seat-role-assignment.md) — `Vignette.roles_needed`/
`RoleRequirement`, `SessionManager.assign_role`/`staffing_report`,
`InProcessSession.start()` hard-gated on unmet mandatory roles, `/roles/assign`+`/roles/staffing`
endpoints, White-Cell-only seat-assignment UI, all confirmed against the live tree. `BL-0014` (no
role-based command-filtering consumer exists yet in `FS-105`/`IP-1050`/`IP-1051`) independently
re-derived, not merely re-cited — still true (see the package's own Risks section and Master Build
Plan Risk item 8); one new Low finding, `BL-0024`). **`IP-3010` is
now `VERIFIED`** (2026-07-04, run #12, [`VR-3010`](../verification/VR-3010-research-analytics.md) —
`spacesim/tools/` subpackage (`research_batch.run_batch()`) and `session/research_export.py`
(`RunRecord` + CSV/JSON export) confirmed against the live tree; `BL-0018`/`BL-0017` re-confirmed,
no new findings). **Every package in this tier is now `VERIFIED`** — the "iterate through all
`09-package-verification`" sweep (runs #11–#15) is complete.

**`IP-1160` is new (2026-07-05), Tranche 2:** `11-release-readiness`'s
[release assessment](../../reviews/release-assessment-fs-tracked-baseline.md) found `FEAT-3500`
had zero owning Feature Specification and zero implementation — `FS-116` (via `06-feature-
specification`) and `ADS-3500` (via `03-architecture-design-synthesis`, resolving `FS-116`'s two
Open Questions) closed the specification gap; `IP-1160` is the single package that closes the
implementation gap. Every one of its dependencies (`IP-1151`, `IP-1050`, `IP-1051`) is already
`VERIFIED`, so `IP-1160` is specification-complete and would flip to `READY` the moment MSTR-006 §3
authorization is granted — not yet on record as of this writing. See
[`../01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) Tranche 2 for the
no-split rationale.

**Authorization update (2026-07-03):** the project owner reviewed every package gated on MSTR-006
§3 and authorized `IP-2010`, `IP-1130`, `IP-1120`, and `IP-1151` (recorded in
`docs/pipeline/pipeline-journal.md` run #2) — `IP-3010` was **not** authorized this round.
Authorization is a separate axis from the `READY`/`BLOCKED`/`COMPLETE` status vocabulary above: at
authorization time, `IP-1120`/`IP-1151` were still `BLOCKED` on `IP-1150` reaching `VERIFIED`
regardless of being authorized — that gate cleared the same day (`VR-1150`), so both are now
`READY`. **`IP-3010` was subsequently authorized too (2026-07-03, run #9)**, and implemented
2026-07-04 (run #10) — it is now `COMPLETE`.

**Executing a package.** The `08-code-implementation` skill
(`.claude/skills/08-code-implementation/SKILL.md`) is the next stage downstream of this tier: it
selects exactly one `READY`-and-eligible package, implements it, and advances its status to
`COMPLETE`. It never authors or edits a package (that remains this tier's job) and never advances a
package past `COMPLETE` to `VERIFIED` (that belongs to `09-package-verification`). Per this
repository's MSTR-006 §3 rule, `08-code-implementation` treats `READY` status as necessary but not
sufficient for any forward-design package until a separate, explicit user go-ahead is on record —
`IP-2010`, `IP-1120`, `IP-1130`, `IP-1151`, and `IP-3010` all received that go-ahead, were all
implemented, and have since all passed `09-package-verification`. **No package in this plan
remains `READY` or `COMPLETE`** — every package has reached `VERIFIED` (`IP-1140` carries a
standing user-accepted-risk note rather than an outstanding gap-closing package).

## Status legend

Per the task's fixed status vocabulary (distinct from the general corpus's MSTR-006 §2 symbol set,
used because this tier's deliverable is an executable build plan, not a general document):

| Status | Meaning |
|---|---|
| NOT STARTED | Package is specified but no upstream dependency work has begun. |
| READY | Design complete, all upstream dependencies satisfied — blocked only on authorization/scheduling, not on missing prerequisite work. |
| IN PROGRESS | Implementation actively underway. |
| BLOCKED | Blocked on a specific named dependency (another package, an external decision) reaching a required state first. |
| COMPLETE | Implementation finished, tests passing, not yet independently re-verified. |
| VERIFIED | Implementation finished, tested, and independently confirmed against the current source tree (this pass's as-built packages: file/line citations checked against the live `spacesim/` tree at authoring time). |

**The original 11 as-built packages (`IP-1010`…`IP-1110`) are `VERIFIED`, not `COMPLETE`**, because
the pass that authored them read and confirmed every cited file/line reference against the current
source tree rather than merely asserting the code exists — that pass combined what
`07-implementation-planning` and `09-package-verification` now do as separate stages. **This
tranche's two new as-built packages (`IP-1140`, `IP-1150`) followed the current, stricter separation
instead**: `07-implementation-planning` confirmed the cited code exists, entering both at
`COMPLETE`; both have since passed independent `09-package-verification` (`VR-1150`, `VR-1140`) and
are now `VERIFIED`.

**Retro-verification sweep (started 2026-07-04, run #18):** none of the 11 as-built packages ever
had a formal `VR-xxxx` report — this was flagged as `BL-0004` and, per the project owner's explicit
choice, is being closed retroactively, one package per `09-package-verification` invocation, ahead
of `11-release-readiness` for the 18-package tranche. `IP-1010` is the first (`VR-1010` — VERIFIED,
no functional discrepancies found). `IP-1020` is the second (`VR-1020` — VERIFIED, one Medium
finding that the package's claimed lifecycle-state names don't match the code, though the
functional guarantee holds). `IP-1030` is the third (`VR-1030` — VERIFIED, no functional
discrepancies, one Low citation-drift finding). `IP-1040` is the fourth (`VR-1040` — VERIFIED, no
functional discrepancies, one Low citation-drift finding). `IP-1050` is the fifth (`VR-1050` —
VERIFIED, no functional discrepancies, one Low citation finding). `IP-1051` is the sixth
(`VR-1051` — VERIFIED, no functional discrepancies, one Low file-misattribution finding). `IP-1060`
is the seventh (`VR-1060` — VERIFIED, no functional discrepancies, one Low citation-drift finding).
`IP-1070` is the eighth (`VR-1070` — VERIFIED, no functional discrepancies, one Low citation-drift
finding). `IP-1090` is the ninth (`VR-1090` — VERIFIED, no functional discrepancies, one Low
citation-drift finding). `IP-1100` is the tenth (`VR-1100` — VERIFIED, one Medium finding — the
package overclaims that Role Assignments are persisted, which `IP-1151`'s own text already
disclosed is false — plus two Low citation findings). `IP-1110` is the eleventh and **last**
(`VR-1110` — VERIFIED, zero findings, the cleanest package in the sweep). **The `BL-0004`
retro-verification sweep is complete: all 18 packages on the Master Build Plan now carry a formal
`VR-xxxx` report.**

## Authoring note

Each as-built package was written against the real module/class/method names in `spacesim/` (cited
inline), re-verified by reading the relevant source file's signatures during this pass — these are
not idealized descriptions but should be re-checked against the code if it changes materially after
this pass. Each forward-design package is explicitly speculative, states its open design questions
rather than presenting invented detail as settled, and is **not** an authorization to begin coding
(MSTR-006 §3) — see [`00-master-build-plan.md`](../00-master-build-plan.md) for the authorization
gate stated once, program-wide, rather than repeated ad hoc per package.
