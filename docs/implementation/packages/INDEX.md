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
| **Capability already implemented** | Documents the *actual* existing architecture against its Feature Spec — a retroactive as-built record, verified against real module/class/method names in `spacesim/`. Status `VERIFIED`. | FS-101 through FS-107 |
| **Capability not yet implemented** | Proposes a from-scratch design satisfying the Feature Spec's requirements — genuinely forward-looking, not yet built, and **not authorized for coding merely by being documented** (MSTR-006 §3). Status `READY` or `BLOCKED`. | FS-201, FS-301 |

FS-108 and FS-202 have no Implementation Package in this pass — both remain unauthorized
"(candidate)" Feature Specs ([feature-index.md](../../features/feature-index.md)); per
[MSTR-006](../../master/MSTR-006-governance-principles.md) §3, no package work may begin against an
unauthorized FS.

## Index

| ID | Title | FS | Situation | Status |
|---|---|---|---|---|
| [IP-1010](IP-1010-mission-planning.md) | Mission Planning — dry-run preview & window/Δv display | [FS-101](../../features/FS-101-mission-planning.md) | As-built | ✅ VERIFIED |
| [IP-1020](IP-1020-command-scheduling.md) | Command Scheduling — Order/OrderSystem lifecycle | [FS-102](../../features/FS-102-command-scheduling.md) | As-built | ✅ VERIFIED |
| [IP-1030](IP-1030-custody-management.md) | Custody Management — Track confidence model | [FS-103](../../features/FS-103-custody-management.md) | As-built | ✅ VERIFIED |
| [IP-1040](IP-1040-sda-tasking.md) | SDA Tasking — sensor tasking & SSN request lifecycle | [FS-104](../../features/FS-104-sda-tasking.md) | As-built | ✅ VERIFIED |
| [IP-1050](IP-1050-spacecraft-operations-bus-payload.md) | Spacecraft Operations — bus/payload command & telemetry | [FS-105](../../features/FS-105-spacecraft-operations.md) §3.1 | As-built | ✅ VERIFIED |
| [IP-1051](IP-1051-spacecraft-operations-effects-console.md) | Spacecraft Operations — effect resolution & console UX | [FS-105](../../features/FS-105-spacecraft-operations.md) §3.2-4 | As-built | ✅ VERIFIED |
| [IP-1060](IP-1060-white-cell-dashboard.md) | White Cell Dashboard — session/inject/clock control plane | [FS-106](../../features/FS-106-white-cell-dashboard.md) | As-built | ✅ VERIFIED |
| [IP-1070](IP-1070-after-action-review.md) | After Action Review — replay/scrub/branch-compare | [FS-107](../../features/FS-107-after-action-review.md) | As-built | ✅ VERIFIED |
| [IP-2010](IP-2010-competency-assessment.md) | Competency Assessment — rubric computation | [FS-201](../../features/FS-201-competency-assessment.md) | Forward design | 🟡 READY (not authorized) |
| [IP-3010](IP-3010-research-analytics.md) | Research Analytics — multi-run export | [FS-301](../../features/FS-301-research-analytics.md) | Forward design | 🔴 BLOCKED (on IP-2010; also not authorized) |

FS-108/FS-202 have no Implementation Package (unauthorized candidates, MSTR-006 §3).

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

**As-built packages are `VERIFIED`, not `COMPLETE`**, because this authoring pass read and confirmed
every cited file/line reference against the current source tree rather than merely asserting the
code exists.

## Authoring note

Each as-built package was written against the real module/class/method names in `spacesim/` (cited
inline), re-verified by reading the relevant source file's signatures during this pass — these are
not idealized descriptions but should be re-checked against the code if it changes materially after
this pass. Each forward-design package is explicitly speculative, states its open design questions
rather than presenting invented detail as settled, and is **not** an authorization to begin coding
(MSTR-006 §3) — see [`00-master-build-plan.md`](../00-master-build-plan.md) for the authorization
gate stated once, program-wide, rather than repeated ad hoc per package.
