# Feature Specifications — Index

[↑ Docs index](../INDEX.md) · [Master index](../master/MSTR-005-documentation-map.md) ·
[MSTR-005 Documentation Map](../master/MSTR-005-documentation-map.md) §4 (traceability chain) ·
[MSTR-006 Governance Principles](../master/MSTR-006-governance-principles.md) §5 (metadata block)

Feature Specifications (`FS-xxx`) describe **what a capability must do**, with no implementation
detail — they sit between the Domain/Research tiers (the *why*) and Implementation Packages
(`IMP-xxxA/B/C`, the *how*, Phase 5, not yet authorized) in the documentation-driven-development
chain:

```
Training Objective → Domain Document (DOM-00x) → Research (R1xx-R5xx) → Feature Spec (FS-xxx)
    → Implementation Package (IMP-xxxA/B/C) → Code → Tests
```

Per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §4, a Feature Specification is sized at roughly 5-10 pages equivalent.

## Index

| ID | Title | Owning domain | Status | Notes |
|---|---|---|---|---|
| [FS-101](FS-101-mission-planning.md) | Mission Planning | DOM-001 | ✅ Done | Plan-first order authoring against real access-window/regime constraints. |
| [FS-102](FS-102-command-scheduling.md) | Command Scheduling | (R103-grounded; no owning DOM) | ✅ Done | The validate→window→execute→confirm latency surfaced honestly to the operator. |
| [FS-103](FS-103-custody-management.md) | Custody Management | DOM-009 | ✅ Done | Custody/track confidence as the gate for weapons-quality and effect preconditions. |
| [FS-104](FS-104-sda-tasking.md) | SDA Tasking | DOM-009 | ✅ Done | Sensor/SSN tasking across the SDA chain (detect→track→ID→characterize→predict). |
| [FS-105](FS-105-spacecraft-operations.md) | Spacecraft Operations | DOM-001, DOM-007 | ✅ Done | The full operator console: bus/payload command, telemetry, effects, consequence-confirm. |
| [FS-106](FS-106-white-cell-dashboard.md) | White Cell Dashboard | DOM-003 | ✅ Done | Facilitator god-view, inject scheduling, clock/pacing authority, session admin. |
| [FS-107](FS-107-after-action-review.md) | After Action Review | DOM-001, DOM-003 | ✅ Done | Replay/scrub/branch-compare debrief instrument, incl. self-assessment mode. |
| [FS-108](FS-108-inject-authoring.md) | Inject Authoring *(candidate)* | DOM-003 | 🅿️ Scoped, not authorized | Templated/preview inject-authoring UX over the existing inject mechanism. |
| [FS-201](FS-201-competency-assessment.md) | Competency Assessment | DOM-002 | ✅ Done | Read-only rubric-based measurement layer over existing engine state. |
| [FS-202](FS-202-rubric-authoring.md) | Rubric Authoring *(candidate)* | DOM-002 | 🅿️ Scoped, not authorized | Tooling for facilitators/instructors to define/adjust FS-201 rubric tiers. |
| [FS-301](FS-301-research-analytics.md) | Research Analytics | DOM-004, DOM-005 | ✅ Done | Structured multi-run/cohort export for instrument-grade research use. |

## Status legend

Per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §2: ✅ Done · 🚧 In progress · ⛔ Planned · 🅿️ Scoped, not authorized.

FS-108 and FS-202 are written as **lighter-weight candidate-scope stubs**, not full specs — both
are explicitly named "(candidate)" everywhere they appear in the existing corpus (`DOM-002`,
`DOM-003`), meaning their owning domain documents describe the *gap* they would close but stop
short of committing to them as scoped work. Per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §3, anything beyond
documenting that gap (i.e., promoting them to full ✅ specs or beginning Implementation Packages)
requires explicit user authorization — this index does not assume that authorization.

## Authoring note

All FS files in this set follow the **`feature-specification` skill's 20-field template**
(Feature ID → Title → Purpose → Scope → Requirements Implemented → User Workflows → System
Behaviour → Subsystem Responsibilities → Interfaces Used → Data Model Changes → State Changes →
Error Handling → Performance Considerations → Security Considerations → Acceptance Criteria →
Verification Plan → Dependencies → Risks → Open Questions → Related ADRs → Related Interfaces).
The `feature-specification` skill governs all new and existing FS-xxx authoring in this repository;
the prior ad hoc per-section structure used in earlier drafts has been superseded in place — every
file retains its existing path, Document ID, and MSTR-006 §5 metadata block.

Each FS file is grounded in: (a) its owning Domain Document's `Produces`/`Feature Mapping`
frontmatter and any explicit "What this framework expects from FS-xxx" section; (b) the
research-encyclopedia topics whose own "Feature Mapping" section names that FS as a consumer; and
(c) verified ADR and ICD interface cross-references cited in each file's Related ADRs and Related
Interfaces fields. No FS file in this set introduces implementation detail (data models, API shapes,
code) — that is Phase 5's job (`docs/implementations/`, not yet authorized).
