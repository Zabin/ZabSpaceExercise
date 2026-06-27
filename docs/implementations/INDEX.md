# Implementation Packages — Index

[↑ Docs index](../INDEX.md) · [Feature index](../features/feature-index.md) ·
[MSTR-005 Documentation Map](../master/MSTR-005-documentation-map.md) §4 (traceability chain) ·
[MSTR-006 Governance Principles](../master/MSTR-006-governance-principles.md) §4, §8 (size discipline, code-boundary rule)

Implementation Packages (`IMP-xxxA/B/C`) describe **how** to build a specific Feature
Specification — data model, state machine, algorithms, interfaces, test/migration plan — in
prose, diagrams, and pseudocode-level detail, never as literal committed code (MSTR-006 §8 is a
hard rule: no document in this corpus may modify `spacesim/**/*.py`, tests, or any other source
file). A feature is split across multiple lettered packages rather than one oversized package
(MSTR-006 §4).

```
Training Objective → Domain Document → Research → Feature Spec → Implementation Package (here) → Code → Tests
```

## Two distinct situations this tier covers

| Situation | What the IMP package does | Applies to |
|---|---|---|
| **Capability already implemented** | Documents the *actual* existing architecture against its Feature Spec — a retroactive as-built record, not a hypothetical design. Confirmed against the real module/class/method names in `spacesim/`. | FS-101 through FS-107 |
| **Capability not yet implemented** | Proposes a from-scratch design satisfying the Feature Spec's requirements — genuinely forward-looking, not yet built, and not authorized for coding work merely by being documented (MSTR-006 §3). | FS-201, FS-301 |

FS-108 and FS-202 have no Implementation Package in this pass — both are unauthorized "(candidate)"
Feature Specs ([feature-index.md](../features/feature-index.md)); per [MSTR-006](../master/MSTR-006-governance-principles.md) §3, no IMP work may
begin against an unauthorized FS.

## Index

| ID | Title | FS | Situation | Status |
|---|---|---|---|---|
| [IMP-101A](IMP-101A-mission-planning.md) | Mission Planning — dry-run preview & window/Δv display | [FS-101](../features/FS-101-mission-planning.md) | As-built | ✅ Done |
| [IMP-102A](IMP-102A-command-scheduling.md) | Command Scheduling — Order/OrderSystem lifecycle | [FS-102](../features/FS-102-command-scheduling.md) | As-built | ✅ Done |
| [IMP-103A](IMP-103A-custody-management.md) | Custody Management — Track confidence model | [FS-103](../features/FS-103-custody-management.md) | As-built | ✅ Done |
| [IMP-104A](IMP-104A-sda-tasking.md) | SDA Tasking — sensor tasking & SSN request lifecycle | [FS-104](../features/FS-104-sda-tasking.md) | As-built | ✅ Done |
| [IMP-105A](IMP-105A-spacecraft-operations-bus-payload.md) | Spacecraft Operations — bus/payload command & telemetry | [FS-105](../features/FS-105-spacecraft-operations.md) | As-built | ✅ Done |
| [IMP-105B](IMP-105B-spacecraft-operations-effects-console.md) | Spacecraft Operations — effect resolution & console UX | [FS-105](../features/FS-105-spacecraft-operations.md) | As-built | ✅ Done |
| [IMP-106A](IMP-106A-white-cell-dashboard.md) | White Cell Dashboard — session/inject/clock control plane | [FS-106](../features/FS-106-white-cell-dashboard.md) | As-built | ✅ Done |
| [IMP-107A](IMP-107A-after-action-review.md) | After Action Review — replay/scrub/branch-compare | [FS-107](../features/FS-107-after-action-review.md) | As-built | ✅ Done |
| [IMP-201A](IMP-201A-competency-assessment.md) | Competency Assessment — rubric computation design | [FS-201](../features/FS-201-competency-assessment.md) | Forward design | ⛔ Planned (design only; no code exists) |
| [IMP-301A](IMP-301A-research-analytics.md) | Research Analytics — multi-run export design | [FS-301](../features/FS-301-research-analytics.md) | Forward design | ⛔ Planned (design only; no code exists) |

## Status legend

Per [MSTR-006](../master/MSTR-006-governance-principles.md) §2. As-built packages (IMP-101A through IMP-107A/B) are ✅ Done as *documents*
describing code that already exists and is test-covered. Forward-design packages (IMP-201A,
IMP-301A) are ⛔ Planned — the document is complete, but the capability it describes is not
implemented and not authorized for implementation; per [MSTR-006](../master/MSTR-006-governance-principles.md) §3 any actual coding work
against them requires a separate, explicit user go-ahead.

## Authoring note

Each as-built package was written against the real module/class/method names in `spacesim/` (cited
inline), verified by reading the relevant source file's signatures — these are not idealized
descriptions but should be re-checked against the code if it changes materially after this pass.
Each forward-design package is explicitly speculative and states its open design questions rather
than presenting invented detail as settled.
