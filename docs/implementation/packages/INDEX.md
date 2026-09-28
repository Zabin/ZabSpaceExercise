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
| [IP-1171](IP-1171-typed-payload-bus-parameters.md) | Typed Payload & Bus Parameter Domain Model | [FS-117](../../features/FS-117-vignette-creator.md) §`FR-5170`/`FR-5180` | Forward design | ✅ VERIFIED (2026-07-12, [`VR-1171`](../verification/VR-1171-typed-payload-bus-parameters.md) — full suite 598 passed/3 skipped, both permanent gates green; one Low finding, fixed in place) |
| [IP-1172](IP-1172-per-cell-roe-enforcement.md) | Per-Cell Rules of Engagement Enforcement | [FS-117](../../features/FS-117-vignette-creator.md) §`FR-3420`/`NFR-2010` | Forward design | ✅ VERIFIED (2026-07-11, [`VR-1172`](../verification/VR-1172-per-cell-roe-enforcement.md) — full suite 586 passed/3 skipped, both permanent gates green; zero findings) |
| [IP-1173](IP-1173-vignette-creator-draft-session.md) | Vignette Creator Draft Session & Reverse Serialization | [FS-117](../../features/FS-117-vignette-creator.md) §`FR-5110` | Forward design | ✅ VERIFIED (2026-07-11, [`VR-1173`](../verification/VR-1173-vignette-creator-draft-session.md) — full suite 586 passed/3 skipped, both permanent gates green; zero findings) |
| [IP-1174](IP-1174-vignette-creator-ui-surfaces.md) | Vignette Creator UI Surfaces | [FS-117](../../features/FS-117-vignette-creator.md) §`FR-5120`-`FR-5160` | Forward design | 🟠 IN PROGRESS: RETURNED by [`VR-1174`](../verification/VR-1174-vignette-creator-ui-surfaces.md) (2026-09-27). One High finding: `FR-5160` per-cell seat declaration works for White only, and Blue/Red get 403. Two Medium findings: `force/ground` input validation. Needs an `08-code-implementation` re-run against the report. |
| [IP-1061](IP-1061-inject-and-sizing-defect-remediation.md) | Inject Scheduling & Sizing-Cap Defect Remediation (`BL-0062`–`BL-0065`) | [FS-106](../../features/FS-106-white-cell-dashboard.md) §FR-4410 + NFR-1300 ([ADR-0019](../../architecture/adr/ADR-0019-sizing-guideline-not-engine-cap.md)) | Remediation (forward design) | ✅ VERIFIED (2026-09-27, [`VR-1061`](../verification/VR-1061-inject-and-sizing-defect-remediation.md) — full suite 707 passed/3 skipped, both permanent gates green; 3 Low findings, no functional gap) |
| [IP-1180](IP-1180-external-vignette-directories.md) | External Vignette Directories & Safe Scenario Save Target (`BL-0082`, item B16) | [FS-118](../../features/FS-118-external-vignette-directories.md) `FR-5410`/`FR-5420`/`NFR-3700` | Forward design | ✅ VERIFIED (2026-09-27, [`VR-1180`](../verification/VR-1180-external-vignette-directories.md). Full suite 707 passed/3 skipped, both permanent gates green. 1 Low finding: `user_save_dir` is not auto-loadable) |
| [IP-1062](IP-1062-condition-triggered-injects-and-new-effects.md) | Condition-Triggered Injects & New Inject Effect Types (`BL-0070`, item B4) | [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1 `FR-4420`/`FR-4430` | Forward design | 🔵 COMPLETE: remediated 2026-09-27/28 against [`VR-1062`](../verification/VR-1062-condition-triggered-injects-and-new-effects.md)'s High finding — the `anomaly`/bus effect now calls `enter_safe_mode()`/`exit_safe_mode()` instead of setting `mode="safe_mode"` directly, so `begin_recovery` accepts the asset. Awaiting a fresh `09-package-verification` pass |
| [IP-1200](IP-1200-save-as-scenario.md) | Save-as-Scenario (`BL-0071`, item B5) | [FS-120](../../features/FS-120-save-as-scenario.md) `FR-5510` | Forward design | ✅ VERIFIED (2026-09-27, [`VR-1200`](../verification/VR-1200-save-as-scenario.md). Verified after `IP-1180`. Full suite 707 passed/3 skipped, both permanent gates green. Independent end-to-end round trip showed all 6 assets, tracks and space weather identical. 2 Low findings) |
| [IP-1190](IP-1190-bulk-tle-omm-import.md) | Bulk TLE and CCSDS OMM Multi-Object Import (`BL-0067`, item B1) | [FS-119](../../features/FS-119-bulk-tle-omm-import.md) `FR-5220` | Forward design | ✅ VERIFIED (2026-09-27, [`VR-1190`](../verification/VR-1190-bulk-tle-omm-import.md). Full suite 707 passed/3 skipped, both permanent gates green. 2 Medium findings: the OMM `EPOCH` is discarded, and a malformed assignment aborts the batch. 2 Low findings) |
| [IP-1210](IP-1210-ephemeris-export.md) | Ephemeris Export, Truth and Cell-Observed (`BL-0069`, items B2/B3) | [FS-121](../../features/FS-121-ephemeris-export.md) `FR-7410`/`FR-7420`/`FR-7430`; [FS-103](../../features/FS-103-custody-management.md) v1.1 | Forward design | 🔵 COMPLETE: remediated 2026-09-27/28 against [`VR-1210`](../verification/VR-1210-ephemeris-export.md)'s High + 2 Medium findings — `to_ric()` now subtracts the ω×ρ frame-rotation term (co-orbital-stationary probe now reports `ric_v ≈ 0`), `write_oem` is CCSDS-conformant (`REF_FRAME = TEME`), and a new `write_ric_csv()`/`format=ric` companion export satisfies `FR-7430`. Awaiting a fresh `09-package-verification` pass |
| [IP-1220](IP-1220-sensor-modality-models.md) | Sensor Modality Models (`BL-0073`/`BL-0083`, items B7/B17) | [FS-122](../../features/FS-122-sensor-modality-models.md) `FR-1610`-`FR-1660` | Forward design | 🔵 COMPLETE (implemented 2026-09-28; awaiting `09-package-verification`) |
| [IP-1240](IP-1240-debris-field-persistence-estimate.md) | Debris-Field Persistence Estimate by Altitude (`BL-0077`, item B11) | [FS-124](../../features/FS-124-debris-field-persistence-estimate.md) `FR-1430` | Forward design | 🔵 COMPLETE (implemented 2026-09-28; awaiting `09-package-verification`) |
| [IP-1250](IP-1250-maneuver-ledger.md) | Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export (`BL-0072`, item B6) | [FS-125](../../features/FS-125-maneuver-ledger.md) `FR-1320` | Forward design | 🔵 COMPLETE (implemented 2026-09-28; awaiting `09-package-verification`) |
| [IP-1260](IP-1260-telemetry-csv-export.md) | Per-Asset Telemetry CSV Export Over a Time Span (`BL-0075`, item B9) | [FS-126](../../features/FS-126-telemetry-csv-export.md) `FR-2320` | Forward design | 🔴 BLOCKED (not authorization-blocked). Depends on `IP-1062` reaching `VERIFIED`. `IP-1062` was RETURNED 2026-09-27 by [`VR-1062`](../verification/VR-1062-condition-triggered-injects-and-new-effects.md), and its H1 is in the very `anomaly` effect this package's Acceptance Criterion 1 relies on, so the blocker has **not** cleared) |
| [IP-1270](IP-1270-effect-authorization-gating-and-live-roe.md) | Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes (`BL-0076`, item B10) | [FS-127](../../features/FS-127-effect-authorization-gating-and-live-roe.md) `FR-3430`/`FR-3440` | Forward design | 🔵 COMPLETE (implemented 2026-09-28; awaiting `09-package-verification`; resolves the effect-classification taxonomy `IP-1290` reuses) |
| [IP-1280](IP-1280-variable-speed-aar-replay.md) | Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint (`BL-0078`, item B12) | [FS-128](../../features/FS-128-variable-speed-aar-replay.md) `FR-7330` | Forward design | 🔵 COMPLETE (implemented 2026-09-28; awaiting `09-package-verification`) |
| [IP-1290](IP-1290-jamming-delivery-and-effect-detectability.md) | Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings (`BL-0081`, item B15) | [FS-129](../../features/FS-129-jamming-delivery-and-effect-detectability.md) `FR-1440`/`FR-1450` | Forward design | 🔵 COMPLETE (implemented 2026-09-28, sequenced after `IP-1270`; awaiting `09-package-verification`) |

FS-108/FS-202 have no Implementation Package (unauthorized candidates, MSTR-006 §3). **IP-1170
through IP-1174 are new (2026-07-05)** — Tranche 3, the five packages planned against `FS-117`
(Vignette Creator), split by seam (see [`../01-technical-work-breakdown.md`](../01-technical-work-breakdown.md)
Tranche 3 for the full split rationale and the three design-fork decisions resolved before
packaging). **All five authorized for coding 2026-07-05** (MSTR-006 §3, project owner). `IP-1170`,
`IP-1172`, `IP-1173`, and now `IP-1171` are all `VERIFIED` (2026-07-05,
[`VR-1170`](../verification/VR-1170-isr-beam-mode-coverage.md); 2026-07-11,
[`VR-1172`](../verification/VR-1172-per-cell-roe-enforcement.md)/
[`VR-1173`](../verification/VR-1173-vignette-creator-draft-session.md); 2026-07-12,
[`VR-1171`](../verification/VR-1171-typed-payload-bus-parameters.md) — all four verified in fresh
sessions independent of their implementation; full suite green throughout; `VR-1170` closes
`BL-0053`). **`IP-1174` now flips `BLOCKED → READY`** — every one of its three dependencies is
`VERIFIED`, per this plan's own "`READY` means fully specified and every dependency `VERIFIED`"
rule; it is the sole package left to implement in this tranche. **IP-1090,
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

**`IP-1180` is new (2026-09-27), Tranche 4 (external validation report, Must-tier batch):** the
first of six Implementation Packages planned against the six Must-tier Feature Specifications
authored from the 26 Sep 2026 external validation report (`docs/pipeline/backlog.md` `BL-0062`–
`BL-0083`; priority order per `docs/pipeline/pipeline-journal.md` run #63: B16, B4, B5, B1, B2/B3).
`IP-1180` closes `FS-118`'s three requirements in one package (no split — a single coherent seam
across `content/vignette.py`/`content/vignette_export.py`/`config.py`) and resolves three of
`FS-118`'s four Open Questions as explicit design decisions (see the package's own "Design
Decisions" section), the fourth by direct code reading. Its sole dependency, `IP-1173`, is already
`VERIFIED`, so it is specification-complete and would flip to `READY` the moment MSTR-006 §3
authorization is granted — not yet on record as of this writing. **`IP-1062` is the second**,
closing `FS-106` v2.1's `FR-4420`/`FR-4430` slice (`BL-0070`, item B4) — resolves `BL-0091`
(scripted-manoeuvre entry-mode ambiguity: must resolve through `engine/maneuver.py`'s six existing
entry modes) and `BL-0095` (deleted-target condition ⇒ never fires; scripted-manoeuvre bypasses the
`delta_v_ms` gate per `ADR-0005`) as explicit Design Decisions, and surfaces one new Low finding of
its own (the anomaly effect's "bus"/"telemetry" subsystem mapping is this package's own
interpretation, not a literal requirements citation). Specification-complete, no dependency to
satisfy, not yet authorized. **`IP-1200` is the third**, closing `FS-120` (save-as-scenario,
`BL-0071`, item B5) — extends the existing `export_vignette()`/`save_vignette()` mechanism
(`IP-1173`, `VERIFIED`) in place with an optional `start_epoch` parameter, two new additive
`Vignette` fields (`initial_tracks`, `simulator_version`), and reuse of the existing
`space_weather` dict shape as `initial_space_weather` — resolves `BL-0097`'s Open Question in
full as two Design Decisions. Notes a same-function implementation-sequencing coordination point
with `IP-1180` (both extend `save_vignette()`). Specification-complete, not yet authorized. **`IP-1190` is the fourth**, closing `FS-119` (bulk
TLE/CCSDS OMM import, `BL-0067`, item B1) — generalizes `session/manager.py::add_tle()`'s existing
single-object mechanism to a batch entry point via new shared per-object helpers, adds a new
`content/bulk_import.py` parser module (multi-TLE + CCSDS OMM in KVN form only — XML OMM explicitly
out of scope, see the package's own Risks), and extracts a new public `engine/orbit.py::
mean_to_true()` (mirroring the existing `true_to_mean()`) for the OMM path's mean-anomaly
conversion. Resolves `BL-0096`'s two Open Questions in full as Design Decisions (outright file-level
rejection vs. per-object failure; no new batch-size cap beyond `ADR-0019`'s existing soft
guideline). **Implemented 2026-09-27** (MSTR-006 §3 authorization granted the same day) —
`COMPLETE`, full suite 638 passed/3 skipped, both permanent gates green, awaiting
`09-package-verification` in a fresh session. **`IP-1210` is the sixth and last**,
closing `FS-121`/`FS-103` v1.1 (ephemeris export, `BL-0069`, items B2/B3) — implements `ADS-1500`'s
replay-based design exactly: a new `session/ephemeris.py` module built on a new additive
`aar.state_at_time()` sibling of the existing `state_at()`, reusing `engine/maneuver.py::
lvlh_frame` for the RIC transform. Resolves `BL-0098`'s two Open Questions in full as Design
Decisions (wholly-out-of-range spans rejected, partially-out-of-range spans clamped; no numeric
sampling-rate ceiling, a coarse default interval instead). **This closes the external validation
report intake batch's six-package Must-tier tranche** — every one of B16/B4/B5/B1/B2/B3 now has a
written, specification-complete, not-yet-authorized Implementation Package.

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
