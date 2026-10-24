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
> FS-115, FS-116, FS-117, FS-118, FS-201, FS-301 (19 of 21 catalog entries; FS-108/FS-202 excluded,
> see §"Scope and exclusions". FS-116 was already planned via `IP-1160` — this line's omission of it
> was a pre-existing staleness, corrected here alongside FS-117's addition. **FS-118 added
> 2026-09-27** via `IP-1180`, the first of six Must-tier packages from the external validation
> report intake batch; **the FS-106 v2.1 slice's package (`IP-1062`), FS-120's package (`IP-1200`),
> FS-119's package (`IP-1190`), and FS-121/FS-103 v1.1's package (`IP-1210`) all added the same
> day** — this closes the six-package Must-tier tranche; FS-121/FS-103 v1.1 are not yet reflected
> in this Feature Mapping line's own list above, a bookkeeping catch-up left for the next pass that
> touches this frontmatter.)
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
| [IP-1091](packages/IP-1091-clock-lag-watchdog-test.md) | `NFR-1300` Clock-Lag Watchdog Test — six synthetic-sample tests of `_record_catch_up_lag` and the `lag_warning` it surfaces (`BL-0309`, GDS-10 F1) | Remediation (test-only) | ✅ VERIFIED | **Authored 2026-10-23** (pipeline run #224); owner-authorized 2026-10-23; implemented run #232; verified 2026-10-24 — [VR-1091](verification/VR-1091-clock-lag-watchdog-test.md). |
| [IP-1100](packages/IP-1100-save-and-resume.md) | FS-110 Save & Resume | As-built | ✅ VERIFIED | none — **retro-verified 2026-07-04 (run #28)**, [`VR-1100`](verification/VR-1100-save-and-resume.md), 10th of 11 in the `BL-0004` sweep; full suite 566 passed/3 skipped, both permanent gates green; one Medium finding (package overclaims Role Assignments are persisted — false, per `IP-1151`'s own text), two Low citation findings |
| [IP-1101](packages/IP-1101-self-contained-saves.md) | FS-110 v2.0 `FR-7230`/`FR-7220`/`FR-7210`/`NFR-1800` Self-Contained Saves — the save carries the vignette as loaded (plus force-added assets) and the replay baseline, resumes from them alone, and records format and simulator versions; fixes force edits lost on resume (`BL-0302`, `BL-0315`) | Remediation + forward design | ✅ VERIFIED | **Verified 2026-10-24** ([VR-1101](verification/VR-1101-self-contained-saves.md); fresh-session `09`; 30 of 50 failed-first reproduced; full suite 1280 passed/3 skipped). *Implemented 2026-10-23* (`08`, owner-authorized; save ≈16 KB for a small vignette, 0.5 KB before).  **Authored 2026-10-23** (`07-implementation-planning`, pipeline run #220). Dependencies `IP-1100`, `IP-1310`, `IP-1200` `VERIFIED`. **Not yet authorized** (MSTR-006 §3). |
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
| [IP-1171](packages/IP-1171-typed-payload-bus-parameters.md) | FS-117 §FR-5170/FR-5180 Typed Payload & Bus Parameter Domain Model | Forward design | ✅ VERIFIED | **VERIFIED 2026-07-12 via [`VR-1171`](verification/VR-1171-typed-payload-bus-parameters.md)** (fresh session, pipeline run #52; one Low finding, fixed in place). *Row corrected 2026-10-16 by `07-implementation-planning` (pipeline run #132, `BL-0218`): it had been left at `COMPLETE` after `VR-1171`, while the package header, `packages/INDEX.md` and `ROADMAP.md` already read `VERIFIED`; no status change, a stale-row fix only (same drift class as `BL-0008`/`BL-0085`).* Implemented 2026-07-11 by `08-code-implementation` — 8 new typed `PayloadState` sub-models (`bus.py`), auto-populated per `type`, R109/R110/R129/R134-grounded; `FR-5180`'s bus power/propulsion authoring confirmed to already route through `Asset.model_validate()`, no loader change needed. 12 new tests, full suite 598 passed/3 skipped, both permanent gates green. |
| [IP-1172](packages/IP-1172-per-cell-roe-enforcement.md) | FS-117 §FR-3420/NFR-2010 Per-Cell Rules of Engagement Enforcement | Forward design | ✅ VERIFIED | **Verified 2026-07-11 (fresh session)**, [`VR-1172`](verification/VR-1172-per-cell-roe-enforcement.md) — full suite 586 passed/3 skipped, both permanent gates green; both `_validate()` check sites independently confirmed to resolve per `order.cell` with zero legacy-shape branching inside `engine/`. Zero findings |
| [IP-1173](packages/IP-1173-vignette-creator-draft-session.md) | FS-117 §FR-5110 Vignette Creator Draft Session & Reverse Serialization | Forward design | ✅ VERIFIED | **Verified 2026-07-11 (fresh session)**, [`VR-1173`](verification/VR-1173-vignette-creator-draft-session.md) — full suite 586 passed/3 skipped, both permanent gates green; sole-writer-to-`VIGNETTE_DIR` and draft-session time-control rejection independently confirmed; independent manual round-trip beyond the existing tests. Zero findings |
| [IP-1174](packages/IP-1174-vignette-creator-ui-surfaces.md) | FS-117 §FR-5120-FR-5160 Vignette Creator UI Surfaces | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1174`](verification/VR-1174-vignette-creator-ui-surfaces.md) v2.0 (second pass) — the v1.0 High/Medium findings (`BL-0123`/`BL-0124`/`BL-0125`) confirmed fixed by independent re-probe; no High/Medium remains. **Remediated 2026-09-27/28** against [`VR-1174`](verification/VR-1174-vignette-creator-ui-surfaces.md)'s High + 2 Medium findings (authorized 2026-09-27, MSTR-006 §3, project owner's direct instruction): `declare_seats` (`FR-5160`) now takes caller identity as the `cell` query param (the convention every other mutating route uses), leaving the body's `cell` as the pure target cell — Blue/Red seat declaration works; `creator.js`'s matrix `roles/assign` call now sends literal `"white"` caller identity instead of the assigned seat's own cell prefix. `force/ground`'s `Asset(...)` validation error now returns `Ack(ok=False, ...)` instead of an unhandled 500 (`BL-0124`); `GroundAssetRequest.owner` is `Literal["blue","red","neutral"]` with `lat_deg`/`lon_deg` range validators (`BL-0125`). This package's own stale `build_scene(world, cell)` prose corrected in place (`BL-0127`). `test_seat_declaration_rejects_non_white_cell` inverted (`test_seat_declaration_rejects_non_white_caller`) + a new allow-non-white-target-cell test added. Full suite green (both permanent gates included). *Prior state:* **RETURNED 2026-09-27 by `VR-1174`** — one failed check (High H1) plus 2 Medium/2 Low findings; `FR-5120`–`FR-5150` confirmed working then. Originally implemented 2026-09-26 (same day as `IP-1061`, a fresh session per the tranche's own eligibility filter — `IP-1061`'s COMPLETE state has no dependency edge to this package). Awaiting a fresh `09-package-verification` pass (new session, per same-session-verification-exclusion).
| [IP-1061](packages/IP-1061-inject-and-sizing-defect-remediation.md) | FS-106 §FR-4410 + NFR-1300 (ADR-0019) Inject Scheduling & Sizing-Cap Defect Remediation | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-09-27 (fresh agent context)**, [`VR-1061`](verification/VR-1061-inject-and-sizing-defect-remediation.md) — full suite 707 passed/3 skipped, both permanent gates green. A1 (0 s inject fires once, no rewind double-fire or loss), A3 (single validating `space_weather` branch), A2 (comment) and A4 (caps removed) independently re-derived with a probe script beyond the package's own tests. 3 Low findings: checklist grep literal, DoD test-count wording, and the pre-existing `NFR-1300` RTM column-shape defect class. Implemented 2026-09-26; closes backlog `BL-0062`–`BL-0065`. |
| [IP-1180](packages/IP-1180-external-vignette-directories.md) | FS-118 External Vignette Directories & Safe Scenario Save Target (`BL-0082`, item B16) | Forward design | ✅ VERIFIED | **Verified 2026-09-27 (fresh agent context)**, [`VR-1180`](verification/VR-1180-external-vignette-directories.md). Full suite 707 passed/3 skipped, both permanent gates green. Built-in-wins collision, external-versus-external ordering, missing-directory skip, the retargeted save, and a single shared traversal guard were all confirmed with hand-built temporary-directory fixtures. 1 Low finding: a saved vignette is not loadable unless `user_save_dir` is also listed in `external_vignette_dirs`, and the config example does not say so. *Prior state:* implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3): new `ContentConfig`/`load_content_config()` (`config.py`); `content/vignette.py`'s `list_vignettes()`/`load_vignette()` extended to enumerate/search configured external directories (built-in-wins collision rule, unreadable-directory skip, both logged), traversal guard extracted into shared `_validate_id`/`_resolve_within_root` helpers; `content/vignette_export.py::save_vignette()` retargeted to a configured `user_save_dir`, raising when unconfigured. 23 new tests (`test_config.py`, `test_content.py`, new `test_vignette_export.py`), 3 existing save-as-vignette tests updated to configure a `tmp_path` `user_save_dir` fixture (regression, not rewrite). Full suite 661 passed/3 skipped (up from 638/3), both permanent gates green. Resolves `BL-0094`'s remaining three Design-Decision-based Open Questions in full. Awaiting `09-package-verification` in a fresh session. |
| [IP-1062](packages/IP-1062-condition-triggered-injects-and-new-effects.md) | FS-106 v2.1 Condition-Triggered Injects & New Inject Effect Types (`BL-0070`, item B4) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1062`](verification/VR-1062-condition-triggered-injects-and-new-effects.md) v2.0 (second pass) — the v1.0 High finding (`BL-0128`) confirmed fixed by independent re-probe, incl. `begin_recovery` acceptance; `BL-0129` (Medium) remains open/`SCHEDULED`, correctly out of this remediation's scope, and does not block `VERIFIED`. **Remediated 2026-09-27/28** against [`VR-1062`](verification/VR-1062-condition-triggered-injects-and-new-effects.md)'s High finding (authorized 2026-09-27, MSTR-006 §3, project owner's direct instruction): the `anomaly` effect's `subsystem: "bus"` branch now calls `engine/bus.py::enter_safe_mode(bus, world.now, cause)`/`exit_safe_mode(bus)` instead of setting `bus_state.mode` directly, so `safe_mode.active`/`cause`/`entered_at` are fully consistent and `begin_recovery` accepts the asset. Added `test_anomaly_safed_asset_is_accepted_by_begin_recovery` + stronger assertions on the existing bus-subsystem test (`test_inject_effects_v2.py`). Full suite green (both permanent gates included). This unblocks `IP-1260` once this package is re-`VERIFIED`. *Prior state:* **RETURNED 2026-09-27 by `VR-1062`** — High H1 (`begin_recovery` refused with `not_safed`), plus 1 Medium (a malformed effect payload raises mid-handler, `BL-0129`, still open/`SCHEDULED`) and 4 Low; `FR-4420` (the condition trigger, including replay and rewinds) independently confirmed sound. Originally implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3): a new periodic `condition_check` event (`_h_condition_check`) evaluates condition-triggered injects against replayed `WorldState`, firing-state derived from a time-filtered eventlog scan (no new `WorldState` field, no mid-handler `eventlog.append`); `_h_inject`'s body extracted into a shared `_apply_inject_effects` helper, gaining four new branches (`anomaly`, `sensor_outage`, `forced_custody_loss`, `scripted_manoeuvre`); new `Sensor.health` field + `scene_from_world()` filter. Resolves `BL-0091`/`BL-0095` in full. Awaiting a fresh `09-package-verification` pass (new session, per same-session-verification-exclusion). |
| [IP-1200](packages/IP-1200-save-as-scenario.md) | FS-120 Save-as-Scenario (`BL-0071`, item B5) | Forward design | ✅ VERIFIED | **Verified 2026-09-27 (fresh agent context, after `IP-1180`)**, [`VR-1200`](verification/VR-1200-save-as-scenario.md). Full suite 707 passed/3 skipped, both permanent gates green. The independent round trip started `leo-isr-denial`, created a track, a bus anomaly, severe space weather and a Δv change, then saved as a scenario and reloaded. Start epoch equalled T, the tracks were identical, and all 6 assets were `model_dump()`-identical. 2 Low findings: the package's "byte-identical" checklist wording contradicts its own always-stamp-version design, and there is no browser GUI control. *Prior state:* implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3; built against `IP-1180`'s actual landed diff, per the coordination note): `export_vignette()`/`save_vignette()` gain an optional `start_epoch` parameter (defaults preserve `IP-1173`'s exact prior behavior); three new additive `Vignette` fields (`initial_tracks`, `simulator_version`, `initial_space_weather`) carried forward and consumed by `build_world()`; new `spacesim/version.py::simulator_version()` (git short hash, package-version fallback); new `SessionManager.save_as_scenario()` requiring `self.started`; `InProcessSession.save_vignette(..., as_scenario=...)` and `SaveVignetteRequest.as_scenario` wire it through the existing route (no new route). 11 new tests, full suite 689 passed/3 skipped (up from 678/3), both permanent gates green. Resolves `BL-0097` in full. Awaiting `09-package-verification` in a fresh session. |
| [IP-1190](packages/IP-1190-bulk-tle-omm-import.md) | FS-119 Bulk TLE and CCSDS OMM Multi-Object Import (`BL-0067`, item B1) | Forward design | ✅ VERIFIED | **Verified 2026-09-27 (fresh agent context)**, [`VR-1190`](verification/VR-1190-bulk-tle-omm-import.md). Full suite 707 passed/3 skipped, both permanent gates green. Every DoD and Acceptance Criterion was confirmed. `mean_to_true()` was checked against a hand-computed Kepler solution, and the reject-versus-per-object-failure split was tested with hand-built fixtures. 2 Medium findings: the OMM `EPOCH` is discarded on the false premise that `add_tle` does the same, and an invalid assignment owner/kind aborts the batch with HTTP 500. 2 Low. *Prior state:* implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3): new `content/bulk_import.py` (`parse_multi_tle`/`parse_ccsds_omm`, KVN only), new public `engine/orbit.py::mean_to_true()` extracted with zero behavior change to `elements_to_rv()`, `_force_add_tle_object`/`_force_add_omm_object`/`bulk_import()` on `SessionManager`, new `POST /api/sessions/{sid}/force/bulk_import` route (+ `InProcessSession.bulk_import()` plumbing, implied by the route but not separately named in the package's own Files to Modify). 16 new tests (`test_bulk_import.py`, `test_bulk_import_session.py`, 2 in `test_orbit.py`, 1 in `test_web.py`, 1 new Observer-guard entry), full suite 638 passed/3 skipped (up from 622/3), both permanent gates green. Resolves `BL-0096` in full. Awaiting `09-package-verification` in a fresh session. |
| [IP-1210](packages/IP-1210-ephemeris-export.md) | FS-121/FS-103 v1.1 Ephemeris Export (`BL-0069`, items B2/B3) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1210`](verification/VR-1210-ephemeris-export.md) v2.0 (second pass) — the v1.0 High/Medium findings confirmed fixed, incl. an independent from-scratch numeric re-derivation of the ω×ρ correction. **Remediated 2026-09-27/28** against [`VR-1210`](verification/VR-1210-ephemeris-export.md)'s High + 2 Medium findings (authorized 2026-09-27, MSTR-006 §3, project owner's direct instruction — fix to true RIC-frame velocity, not rename/document): `to_ric()` now subtracts the RIC frame's own rotation term `ω × ric_r` (`ω = |h_ref|/|r_ref|²` along the reference orbit's normal) from the inertial-relative-velocity-in-RIC-axes it previously returned unmodified — the reported co-orbital-stationary probe case now correctly reports `ric_v ≈ 0` instead of −13.29 m/s. `write_oem`'s KVN structure is now CCSDS-conformant (`CREATION_DATE`/`ORIGINATOR`, a `META_START`/`META_STOP` block that actually wraps its metadata fields, CCSDS ASCII epochs, `REF_FRAME = TEME` matching the engine's own documented approximation). `BL-0136`'s OEM/RIC tension resolved per the owner's `FR-7430` amendment: new `write_ric_csv()` + a `format=ric` route option on both ephemeris endpoints. New/strengthened tests: `test_to_ric_velocity_zero_for_co_orbital_ric_stationary_neighbour`, `test_to_ric_velocity_matches_finite_difference_of_ric_position`, `test_write_oem_is_ccsds_conformant`, `test_write_ric_csv_carries_only_ric_fields` (`test_ephemeris.py`), `test_ephemeris_ric_companion_format` (`test_web.py`). Full suite green (both permanent gates included). *Prior state:* **RETURNED 2026-09-27 by `VR-1210`** — High H1 (missing `ω×ρ` term) plus 2 Medium (OEM non-conformance, no RIC in OEM) and 2 Low; ECI, RIC position, fog-of-war, range clamp/reject and determinism independently confirmed then. Originally implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3): new `session/ephemeris.py` built on a new additive `aar.state_at_time(mgr, t)` sibling of `state_at(mgr, seq)`; `engine/maneuver.py::lvlh_frame` reused unmodified for the RIC transform; two HTTP routes (`GET .../ephemeris/truth` no-cell, `GET .../ephemeris/{cell}` cell-scoped). Resolves `BL-0098` in full. Awaiting a fresh `09-package-verification` pass (new session, per same-session-verification-exclusion). **This closes the five-package authorized-implementation tranche for this increment** (`IP-1180`/`IP-1062`/`IP-1200`/`IP-1190`/`IP-1210` — every one now `COMPLETE`). |
| [IP-1220](packages/IP-1220-sensor-modality-models.md) | FS-122 Sensor Modality Models (`BL-0073`/`BL-0083`, items B7/B17) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1220`](verification/VR-1220-sensor-modality-models.md) — all six requirements confirmed; 1 Low finding (package's own doc left unupdated at implementation time; `passive_rf_fix()` confirmed unwired to any delivery path, not itself a DoD gap). **Implemented 2026-09-28** (authorized 2026-09-27, MSTR-006 §3): six additive `Sensor` fields (`beam_mode`/`exclusion_angle_deg`/`min_range_km`/`altitude_band_affinity`/`requires_cue`/`host_asset_id`); `isr.py` gains a `ground_radar` fence/dish `BEAM_MODES` entry + `effective_gain()`'s optional band-affinity degradation; `access.py`'s `_observation_predicate` gains the solar-exclusion-angle reject (ground) and min-range-floor reject + host-asset orbit substitution (space-based), plus a shared `_sensor_id_for_actor()` dual-identifier resolver; `orders.py`'s `_validate`/`_candidate_sensors` gain the `requires_cue` precondition and the same dual-identifier resolution; `ssn.py` gains `passive_rf_fix()` (FR-1650). New tests in `test_access.py`, `test_isr.py`, `test_orders.py`, `test_ssn.py`. Full suite green, both permanent gates green. Awaiting `09-package-verification`. |
| [IP-1240](packages/IP-1240-debris-field-persistence-estimate.md) | FS-124 Debris-Field Persistence Estimate by Altitude (`BL-0077`, item B11) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1240`](verification/VR-1240-debris-field-persistence-estimate.md) — clean, 1 Low finding (package's own doc left unupdated at implementation time). **Implemented 2026-09-28** (authorized 2026-09-27, MSTR-006 §3): a new `DebrisField.persistence_estimate` field, computed by a pure `_persistence_estimate(altitude_km)` (R117 v1.2 §3.1 banded figures) and attached at both construction sites (`effects.py`'s destructive-effect resolution, `manager.py`'s `spawn_debris` inject handler). New tests in `test_effects.py` (monotonic with altitude, no gating-logic coupling) and `test_inject_library.py`. Full suite green, both permanent gates green. Awaiting `09-package-verification`. |
| [IP-1250](packages/IP-1250-maneuver-ledger.md) | FS-125 Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export (`BL-0072`, item B6) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1250`](verification/VR-1250-maneuver-ledger.md) — clean, 1 Low finding (package's own doc left unupdated at implementation time). **Implemented 2026-09-28** (authorized 2026-09-27, MSTR-006 §3): manoeuvre orders gain an additive `purpose_tag` param, carried into the `execute_maneuver` payload (and thus the eventlog entry unmodified, per the existing generic-payload-dict pattern); `_h_maneuver` mutates the same payload in place with `applied`/`remaining_delta_v_ms` on success (captured by the eventlog entry logged immediately after, same technique `IP-1062`'s `condition_check` uses); `SessionManager.maneuver_ledger(cell, asset_id)` is a pure, fog-scoped derivation from `EventLog`; two new routes (`GET .../maneuver_ledger/{cell}/{asset}` + `/export.csv`), fog-scoped identically to `/telemetry`. New tests in `test_orders.py`, `test_session_features.py`, `test_web.py`. Full suite green, both permanent gates green. Awaiting `09-package-verification`. |
| [IP-1260](packages/IP-1260-telemetry-csv-export.md) | FS-126 Per-Asset Telemetry CSV Export Over a Time Span (`BL-0075`, item B9) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-10-10** via [`VR-1260`](verification/VR-1260-telemetry-csv-export.md) (first pass, fresh session) — `SessionManager.telemetry_export()` confirmed to independently satisfy FR-2320's anomaly-timing and fog-of-war postconditions on a scenario built from scratch (not the implementer's own fixture); the replay-per-sample mechanism confirmed necessary (a naive final-world sample was independently shown to leak the anomaly into every pre-onset row). `BL-0168`'s four scope notes adjudicated in full: the `inprocess.py` pass-through, the replay-per-sample design, and the URL-only reach (no console button) all accepted as necessary/in-scope; the package's own stale `BLOCKED` header confirmed genuine but cosmetic (1 Low finding, same "own doc left unupdated" pattern as this batch's other six packages). The pre-existing-quirk claim on the sibling `/{param}` series route independently confirmed via git history. Full suite 813 passed/3 skipped; both permanent gates green (14/14). *Prior state:* **`COMPLETE` 2026-10-10 (run #94, `08-code-implementation`)** — `SessionManager.telemetry_export()` (each value `engine/telemetry.py::sample()` on the world replayed to that instant; fog-scoped like `get_telemetry`; `ephemeris._clamp_or_reject` span rule) + `InProcessSession.telemetry_export` pass-through + `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv`; 8 new tests (`test_telemetry.py` ×7, `test_web.py` ×1). **Blocker cleared 2026-09-28.** `IP-1062` (this package's own Acceptance Criterion 1 dependency, the `anomaly` effect) reached `VERIFIED` via [`VR-1062`](verification/VR-1062-condition-triggered-injects-and-new-effects.md) v2.0 this same verification pass — `begin_recovery` acceptance of an anomaly-safed asset is now independently confirmed sound. This package's own dependency list names no other unverified package, and it was already part of the same authorized six-package Should-tier batch (2026-09-27, MSTR-006 §3) as `IP-1220`/`IP-1240`/`IP-1250`/`IP-1270`/`IP-1280`/`IP-1290` — so it flipped `BLOCKED → READY`, not merely unblocked-but-unauthorized. |
| [IP-1270](packages/IP-1270-effect-authorization-gating-and-live-roe.md) | FS-127 Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes (`BL-0076`, item B10) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1270`](verification/VR-1270-effect-authorization-gating-and-live-roe.md) — clean, 1 Low finding (package's own doc left unupdated); the shared effect-classification enumeration independently confirmed correctly reused by `IP-1290`. **Implemented 2026-09-28** (authorized 2026-09-27, MSTR-006 §3): `content/vignette.py` gains additive `Vignette.effect_gating_rules` (threaded through `VignetteContext.gating_rules`); `OrderSystem` gains a `_matching_gate()` check (order action type × five-D's reversibility category, Design Decision 1's shared enumeration `IP-1290` must reuse) holding a matched order `pending_approval` (`self._pending`) instead of scheduling it, `decide_gated_order()` (role-gated against the rule's `required_role`, logs `effect_gate_request`/`effect_gate_decision` with elapsed time), `_effective_roe()` (a point-in-time derivation: the immutable `_static_roe` overlaid with `roe_change` eventlog entries at or before the order's own issue time — `FR-3420`'s two ROE checks now read this instead of the static-only value), and `issue_roe_change()` (White-Cell-only, logs `roe_change`). `session/manager.py::_rebind()` discards any pending order on rewind/undo (Design Decision 2). Two new HTTP routes (`/gate/decide`, `/roe/change`). New tests in `test_orders.py`, `test_session_features.py`, `test_web.py`; one pre-existing `test_ssn.py` test updated (it mutated `osys.roe` directly for setup — now also sets the new immutable `_static_roe` baseline). Full suite green, both permanent gates green. Awaiting `09-package-verification`. **This resolves the effect-classification enumeration `IP-1290` must reuse (`BL-0105`).** |
| [IP-1280](packages/IP-1280-variable-speed-aar-replay.md) | FS-128 Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint (`BL-0078`, item B12) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1280`](verification/VR-1280-variable-speed-aar-replay.md) — clean, 1 Low finding (package's own doc left unupdated). **This is the last of the nine-package batch to reach `VERIFIED`.** **Implemented 2026-09-28** (authorized 2026-09-27, MSTR-006 §3): new `session/aar.py::PlaybackSession` — a continuous, speed-adjustable playback controller built entirely on repeated `state_at_time()` calls (unmodified), through either the no-cell ground-truth path or `CellController.view()`'s existing fog-of-war filter; `_participant_cells()` rejects a viewpoint naming a cell that owns no assets/sensors in the recorded exercise, at construction and at `set_viewpoint()`; a viewpoint switch never resets the played-back moment (Design Decision 1). One `PlaybackSession` per exercise session, held in `InProcessSession._playbacks` (UI-presentation state, not exercise state — same placement as `_observer_view`). Five new HTTP routes (`start`/`advance`/`state`/`viewpoint`/`speed`). New tests in `test_aar.py` (non-disturbance, cell/truth-viewpoint matching, viewpoint-switch continuity, non-participating-cell rejection) and `test_web.py`. Full suite green, both permanent gates green. Awaiting `09-package-verification`. **This is the last of the six-package Should-tier authorized batch — every package now `COMPLETE`.** |
| [IP-1290](packages/IP-1290-jamming-delivery-and-effect-detectability.md) | FS-129 Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings (`BL-0081`, item B15) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-09-28** via [`VR-1290`](verification/VR-1290-jamming-delivery-and-effect-detectability.md) — clean, 1 Low finding (package's own doc left unupdated); schema independently confirmed structurally identical to `IP-1270`'s landed enumeration. **Implemented 2026-09-28**, sequenced after `IP-1270` per its Build-sequencing note — read `IP-1270`'s actual landed schema (`_matching_gate`/`gating_rules` shape: `{action_type?, reversibility_category?, ...}`) before writing this package's own config parsing, per its Implementation Task 1 (authorized 2026-09-27, MSTR-006 §3): `_h_command`/`_h_maneuver` gain a check (`is_link_denied(world, actor, now, link="uplink")`) that fails delivery (`achieved="jammed"`) when an active uplink jam covers the command's execution moment, mirroring `_h_downlink`'s existing pattern; `EffectInstance.order_action_type` (additive, set at all three effect-construction sites — jam/engage/cyber) plus `ModerateEffectResolver(detectability_config=...)`/`_class_confidence()` let a vignette declare a per-effect-class attribution-confidence override, keyed by `IP-1270`'s exact enumeration, falling back to the existing fixed `{"overt":.95,"ambiguous":.5,"covert":.15}` table when undeclared; `content/vignette.py` gains the additive `Vignette.effect_detectability_config` → `VignetteContext.detectability_config` plumbing. New tests in `test_orders.py` (jam-covers-delivery + no-jam regression) and `test_effects.py` (per-class resolution, parametrized declared vs. undeclared). Full suite green, both permanent gates green. Awaiting `09-package-verification`. |
| [IP-1300](packages/IP-1300-ric-frame-view-and-cats-overlay.md) | FS-130 Live RIC-Frame Relative-Motion View & CATS Overlay (`BL-0107`/`BL-0111`) | Forward design | ✅ VERIFIED | **`VERIFIED` 2026-10-10** via [`VR-1300`](verification/VR-1300-ric-frame-view-and-cats-overlay.md) — clean, 2 Low findings (package's own doc left unupdated, same pattern as the 2026-09/2026-10 batch; `BL-0158`'s file-list-omission half is a process note for `07`, not a defect). `BL-0158` adjudicated `DONE` (both halves accepted — the omitted `index.html`/`style.css` listing is an implied, necessary consequence of adding the panel; the browser-headless verification posture exactly matches the project's own established UI-verification bar, confirmed by cross-checking every prior UI-touching VR in this index). **Implemented 2026-10-10** (authorized 2026-10-10, MSTR-006 §3, explicit project-owner go-ahead; `08-code-implementation`, pipeline run #88). Implementation Task 1 independently re-confirmed by direct code read: `build_scene()` has no `cell == "white"` case (its asset/track loops filter strictly on `owner == cell`), so `SessionManager.get_ric_view()` wires White explicitly through `get_godview()`'s ground-truth world, never through `cell="white"` filtering. New `engine/sun.py::cats_phase_angle_deg()` (single shared phase-angle function, `BL-0152`, independently confirmed the only definition in `engine/` and correct against a fresh, independently-constructed reference geometry); `session/ephemeris.py::live_ric_view()` (reuses `to_ric()` unmodified; own assets at truth, own Tracks at belief; out-of-custody origin/chase/target → `ValueError`); `SessionManager`/`InProcessSession.get_ric_view()`; `GET /api/sessions/{sid}/ric_view/{cell}?origin=&chase=&target=` (404 on out-of-custody selection, independently probed including a coincident-chase/target edge case not in the shipped tests). New tests: `test_cats_angle.py`, `test_ephemeris.py::test_live_ric_view_*`, `test_web.py::test_ric_view_*`. Full suite 772 passed/3 skipped, both permanent gates green (independently re-run). **Authored run #86 (2026-10-03), `07-implementation-planning`.** Every cited dependency (`IP-1210`, `FS-105`, `FS-106`) is `VERIFIED`; not authorized for coding at authoring time (MSTR-006 §3). Resolves `BL-0155`/`BL-0156` at the design-decision level (new `GET /ric_view/{cell}` route; origin selection kept non-persistent, a `localStorage` convenience left to `08`'s own judgment); `BL-0154` (CATS-angle display banding) left open, shipping an unbanded readout. |
| [IP-1211](packages/IP-1211-quick-tle-export.md) | FS-121 v2.0 Quick TLE Export for a Cell-Visible Satellite (`BL-0109`, `FR-7440`) | Forward design | ✅ VERIFIED | **Verified 2026-10-10** ([VR-1211](verification/VR-1211-quick-tle-export.md), `09-package-verification`, fresh session, independent of the implementing session). `BL-0164` (the safeguarded-Newton deviation from Design Decision 1's plain fixed-point iteration) adjudicated **DONE, accepted as sound and necessary** — the plain iteration's divergence for exactly/near-equatorial GEO was independently reproduced from scratch; the safeguarded version never emits an out-of-bound TLE across a fresh GEO-inclination sweep, five independently-chosen geometries, and all 40 on-orbit assets across all 19 shipped vignettes (1.5-70 m actual round-trip residual, comfortably inside the 1 km bound). The fog-of-war claim (stale belief survives a manoeuvre) independently re-tested end-to-end through `SessionManager.get_tle` on a freshly built session. Full suite 805 passed / 3 skipped (808 collected), both permanent gates green (14/14). One Low finding filed as `BL-0165` (pipeline-journal wording only, no code defect). **Implemented 2026-10-10** (pipeline run #92, `08-code-implementation`, under the project owner's pre-authorization for `BL-0109`/`FR-7440`): new `engine/tle_export.py` (`state_to_tle()` single-epoch SGP4 mean-element fit + `tle_identity()`), `session/ephemeris.py::quick_tle()`, `SessionManager`/`InProcessSession.get_tle()`, `GET /api/sessions/{sid}/tle/{cell}?object_id=`, `static/tleexport.js` (+ `index.html`/`style.css`). Tests: `test_tle_export.py`, `test_ephemeris.py::test_quick_tle_*`, `test_web.py::test_tle_*`. **Authored 2026-10-10 (pipeline run #91, `07-implementation-planning`).** Every cited dependency (`IP-1210`/`IP-1300`'s `session/ephemeris.py` helpers, the `engine/orbit.py`/`propagator.py` baseline, `Track`/`track_for`, the god-view path) is `VERIFIED`. Authorization: pre-authorized by the project owner for the `BL-0109`/`FR-7440` package(s) (MSTR-006 §3, relayed in the 2026-10-10 session task instruction; covers this package only). Resolves `BL-0110` (TLE-generation method — single-epoch SGP4 mean-element fit in non-singular equinoctial elements, uniformly for TLE- and Kepler+J2-sourced orbits, `sgp4.exporter.export_tle` formatting, ≤1 km round-trip bound), `BL-0160` (`GET /api/sessions/{sid}/tle/{cell}?object_id=`), `BL-0161` (View ▾ → TLE export panel), `BL-0162` (`99999` placeholder catalog number for non-TLE objects); follows `FR-7440` literally on own-asset scope (`BL-0159` `DEFERRED` to `04`). No package depends on it; not on the critical path. |
| [IP-1261](packages/IP-1261-telemetry-series-history-remediation.md) | FS-126 §FR-2320 (+ FS-121 `FR-7410`/`FR-7420` migration) Telemetry Series History Remediation — single-pass time-span replay (`BL-0170`) | Remediation (forward design) | ✅ VERIFIED | **`VERIFIED` 2026-10-11** via [`VR-1261`](verification/VR-1261-telemetry-series-history-remediation.md) — clean, 1 Low finding (`BL-0173`'s reversed-window handling is correct but has no regression test). `BL-0173` adjudicated **accepted, no remediation required** — independently reproduced and confirmed correct against a fresh scenario distinct from the implementer's own fixtures. All four `BL-0170` scenarios (A–D) independently re-reproduced on fresh seeds/timings; the single-forward-pass and live-tail-shortcut claims independently confirmed by instrumentation (not by reading the docstring); the ephemeris-export migration independently confirmed output-unchanged; the performance claim independently re-measured, same order of magnitude. Full suite 823 passed/3 skipped, both permanent gates green (14/14), independently re-run. **Implemented 2026-10-11** (`08-code-implementation`, pipeline run #100): `engine/simulation.py::replay_stepwise()` (additive; `replay()` itself confirmed byte-for-byte unchanged) + `session/aar.py::worlds_at_times()` (single forward pass + live-tail shortcut); `get_series`, `telemetry_export`, and both ephemeris exports all route through it. 10 new tests. **Authored 2026-10-11** (`07-implementation-planning`, pipeline run #99). Fixes `get_series` back-dating current world state across its window (breaks `FR-2320`'s cross-route parity Postcondition). Dependencies `IP-1260`/`IP-1210` both `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, 2026-10-11 session task instruction).** `BL-0171` (`FR-2310` historical pass-gating) explicitly out of scope, unaffected. |
| [IP-1262](packages/IP-1262-export-sampling-bounds.md) | FS-121 `FR-7410`/`FR-7420` + FS-126 `FR-2320` Time-Span Export Sampling Bounds — `interval_s` floor + `MAX_EXPORT_SAMPLES` ceiling (`BL-0176`; rider `BL-0174`) | Remediation (forward design) | ✅ VERIFIED | **`VERIFIED` 2026-10-11** via [`VR-1262`](verification/VR-1262-export-sampling-bounds.md) — clean, 1 Low finding (`FS-121`/`FS-126`'s `Referenced By` fields still tag `IP-1262`/`IP-1261` `READY`, stale and pre-existing; filed `BL-0183`, left unedited per this skill's own Feature-Specification boundary). The arithmetic, up-front sample-count ceiling independently confirmed real (not a disguised full-generation-then-reject) by timing a request implying ~10¹⁵–10²⁴ instants: rejected in 0.003–0.005 ms at the module level and 3.49 ms through a full HTTP round trip, with no growth tied to the attempted count. All three call sites (`truth_ephemeris`, `cell_observed_ephemeris`, `telemetry_export`) independently confirmed to share `sample_times` by direct code read. `BL-0174` rider independently re-built on a fresh scenario and confirmed correct. Fail-first claim independently reproduced on a detached pre-fix worktree (8/10 new cases failed, matching exactly). Full suite 833 passed/3 skipped, both permanent gates green (14/14), independently re-run. **Implemented 2026-10-11** (`08-code-implementation`, pipeline run #105): `MAX_EXPORT_SAMPLES = 10_000` + finite/`> 0` `interval_s` validation in `session/ephemeris.py::sample_times` (single choke point for both ephemeris exports and `telemetry_export`); 10 new tests incl. the `BL-0174` rider. **Authored 2026-10-11** (`07-implementation-planning`, pipeline run #104). Fixes the three time-span exports accepting an `interval_s` that `sample_times` floors to a 1 µs step (unbounded replay under the session lock, REV-TRN-002 F1). Dependencies `IP-1210`/`IP-1260`/`IP-1261` all `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, 2026-10-11 session task instruction).** Folds in `BL-0174` (reversed-window `get_series` regression test). |
| [IP-1063](packages/IP-1063-inject-effect-fire-time-validation.md) | FS-106 v2.1 `FR-4430`/`FR-4410` Inject Effect Fire-Time Validation — reject malformed/precondition-failing injects at the White boundary (400), skip-never-raise in the handler (`BL-0129`, `BL-0188`) | Remediation (forward design) | ✅ VERIFIED | **VERIFIED 2026-10-11 via [VR-1063](verification/VR-1063-inject-effect-fire-time-validation.md) (fresh session, first pass, clean — 1 Low finding `BL-0193`, pre-existing FS-106 doc staleness, not a defect of this package). Closes `BL-0129` and `BL-0188`.** COMPLETE 2026-10-11 (`08-code-implementation`, pipeline run #111). `validate_inject_effects` + `_inject_effect_problem` (module-level, pure) in `session/manager.py`; `fire_inject` rejects atomically; `_apply_inject_effects` skips invalid effects (+ `compute_maneuver` guard) via `_skip_inject_effect`; `InProcessSession.fire_inject` → `Ack(ok=False)`; `/inject` → 400. 15 new tests (Tests 1–7 incl. 8 parametrized cases + route test), all 15 observed failing first (Test 7 only on the not-yet-existing import; it guards shipped content and passed as soon as the validator existed, as the package anticipated). Full suite 848 passed/3 skipped (851 collected, JUnit), both permanent gates green (14).** **Authored 2026-10-11** (`07-implementation-planning`, pipeline run #110). Dependencies `IP-1062`/`IP-1061` both `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, 2026-10-11 session task instruction).** Closes `BL-0129` (VR-1062 M1: mid-handler raise → live/replay divergence) and `BL-0188` (bus-less `anomaly` accepted silently). Pure `validate_inject_effects` used at `fire_inject` (atomic reject) and per effect in `_apply_inject_effects` (skip + White message). Handler-level missing-target no-op (`IP-1062` DD2) kept. `BL-0184` not planned (by-design per `IP-1262` DD1; see TWBS). |
| [IP-1212](packages/IP-1212-own-satellite-tle-export.md) | FS-121 v2.1 `FR-7440` (amended) Quick TLE Export for a Cell's Own Satellites — own satellite exported from its actual orbit, no `Track` needed; other side's untracked satellite still rejected (`BL-0201`, from `BL-0159`) | Remediation (forward design) | ✅ VERIFIED | **VERIFIED 2026-10-15 ([VR-1212](verification/VR-1212-own-satellite-tle-export.md), `09-package-verification`, fresh session): clean — own-satellite export, ownership-beats-a-held-track precedence, the cross-cell rejection, and the no-orbit rejection all independently reproduced on `geo-rpo-shadowing`/`BLUE-HVA` (distinct from the implementer's fixtures) at both the function and HTTP levels; superseded test confirmed fully removed. Full suite 852 passed/3 skipped, gates green (14) — independently re-run. 1 Low finding (`BL-0203`, `FS-121` stale tag).** *(COMPLETE 2026-10-15, `08-code-implementation`, pipeline run #119: `quick_tle` own-asset branch ahead of the track lookup (`source: "own"`, own asset without orbit rejected, stale message fixed); `tleexport.js` picker lists own on-orbit satellites + `SOURCE_LABEL`; `get_tle`/route docstrings. Replaced the superseded `test_quick_tle_own_asset_without_track_rejected`; 5 new tests (Tests 1, 3, 4, 5 observed failing first; Test 2 passed on arrival as intended).)* **Authored 2026-10-15** (`07-implementation-planning`, pipeline run #118). Dependency `IP-1211` `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization of this iteration's packages).** Supersedes `IP-1211` Design Decision 5 only: one own-asset branch in `quick_tle` (ownership beats a held track, `source: "own"`), picker lists own on-orbit satellites. |
| [IP-1221](packages/IP-1221-cats-phase-angle-observation-gain.md) | FS-122 v1.1 `FR-1670` CATS Phase-Angle Observation-Gain Refinement — a passive-EO (`needs_lighting`) sensor declaring a usable phase-angle range gets unchanged gain inside it and linearly reduced gain outside it (to 0 at 0°/180°), from the shared `cats_phase_angle_deg` at the scheduled observation instant (`BL-0122`; resolves `BL-0151`/`BL-0208`/`BL-0209`) | Forward design | ✅ VERIFIED | **VERIFIED 2026-10-16 via [VR-1221](verification/VR-1221-cats-phase-angle-observation-gain.md) (fresh session, first pass, clean)** — the linear falloff shape, `effective_gain` backward compatibility, and the load-time `Sensor` validator all independently re-derived on fresh sample points and fresh orbit/epoch geometries distinct from the implementer's own fixtures, at both the pure-helper and full-`OrderSystem` levels; a defense-in-depth probe (forcing a range onto a non-passive-EO sensor past the validator) confirmed `orders.py`'s own `needs_lighting` guard independently blocks it too. `cats_phase_angle_deg` confirmed singly-defined; `access.py`/`sun.py` confirmed genuinely untouched. Full suite 869 passed/3 skipped, gates green (14/14) — independently re-run. No findings against the package; closes `BL-0122`. **COMPLETE 2026-10-16** (`08-code-implementation`, pipeline run #125). `Sensor.usable_phase_angle_deg` + validator; `isr.phase_angle_factor` + additive `effective_gain` args; `OrderSystem._observation_phase_angle_deg` (shared `cats_phase_angle_deg`, at `win.start`) wired into the observe gain. Tests: `test_phase_angle_gain.py` (16) + `test_cats_angle.py` Test 8. Full suite 869 passed / 3 skipped (872 collected; baseline 852/3) (JUnit), gates 14/14. **Authored 2026-10-15** (`07-implementation-planning`, pipeline run #124). Dependencies `IP-1220` and `IP-1300` both `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization of this iteration's packages).** Engine-only (`entities`/`isr`/`orders`); no window-acceptance change; malformed or misplaced range rejected at `Sensor` validation. |
| [IP-1222](packages/IP-1222-sensor-modality-wiring-remediation.md) | FS-122 v1.1 `FR-1610`/`FR-1630`/`FR-1640` Sensor-Modality Wiring Remediation — a ground radar's `fence`/`dish` request (order param, else the sensor's `beam_mode`) selects the `ground_radar` beam-mode table; `auto` sensor selection drops `requires_cue` sensors without a held track (reason `requires_cue` when none is left); `altitude_band_affinity` typed as `Regime`, `LEO`/`LEO_SSO` one band; unknown radar `beam_mode` rejected at `Sensor` validation (`BL-0212`/`BL-0213`/`BL-0214`) | Remediation (forward design) | ✅ VERIFIED | **VERIFIED 2026-10-16** (`09-package-verification`, [VR-1222](verification/VR-1222-sensor-modality-wiring-remediation.md), fresh session). Independently swept all 38 shipped-vignette `ground_radar` sensors across 15 of 19 vignette files: every one still resolves `stripmap`/gain 1.0 with no mode requested (bit-identical to the pre-package baseline), `fence`/`dish` now produce distinct gains. `auto` cue gate and the beam-mode/affinity validators independently reproduced on fresh fixtures. No findings. **COMPLETE 2026-10-16** (`08-code-implementation`, pipeline run #129). Radar `fence`/`dish` reached end to end; `auto` cue filter; `Regime`-typed affinity with `isr.altitude_band`; radar `beam_mode` validator. Tests: `test_sensor_modality_wiring.py` (10). Full suite 879 passed / 3 skipped (882 collected; baseline 869/3/872) (JUnit), gates 14/14. **Authored 2026-10-16** (`07-implementation-planning`, pipeline run #128). Dependencies `IP-1220` and `IP-1221` both `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization of this iteration's packages).** Engine-only (`orders`/`isr`/`entities`); `access.py` untouched; a radar naming no radar mode stays on today's `isr_sar` `stripmap` path, so every shipped vignette is unchanged. |
| [IP-1041](packages/IP-1041-observe-order-reason-and-param-remediation.md) | FS-104 `FR-3210` + FS-122 v1.1 `FR-1610` Observe-Order Remediation — a windowless observe is rejected `no_window` (`sensor_contended` only when every window found is booked); a malformed `beam_mode`/`look_angle_deg`/`duration_s`/`gain` is rejected `invalid_param` by `dry_run` and `issue` before any booking (no HTTP 500, no phantom booking); an explicit `null` param means absent (`BL-0219`, `BL-0217`) | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-10-16** ([VR-1041](verification/VR-1041-observe-order-reason-and-param-remediation.md), fresh session, clean — no findings): both bug sides independently reproduced on fresh fixtures/vignette/seed (windowless → `no_window` via solar exclusion; windows-exist-all-booked → still `sensor_contended`), the phantom-booking claim and the `dry_run`/`issue`-agreement claim independently proved over live HTTP on `04-co-orbital-threat-escort` seed 3, and the "`None`-drop in `_validate` also protects `inprocess.py`'s Gantt-feed timeline code" claim independently confirmed with a working counterfactual. Full suite 908 passed/3 skipped independently re-run, gates 14/14. **Implemented 2026-10-16** (`08-code-implementation`, pipeline run #133): `no_window` vs `sensor_contended` by whether a window was found; `invalid_param` for malformed observe params before booking; `null` = absent; `beam_params` type guard; `REASON_TIPS`. 29 new tests. **Authored 2026-10-16** (`07-implementation-planning`, pipeline run #132). Dependencies `IP-1040` and `IP-1222` both `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** `BL-0220` (session-load 500) was proposed for the same batch and deliberately left out: it belongs to `FR-5310`/`FEAT-5300`, which has no Feature Specification (routed to `06-feature-specification`). |
| [IP-1052](packages/IP-1052-order-param-hardening.md) | FS-105 v1.1 + FS-102 `FR-3110`/`FR-1310`/`FR-1410`/`FR-1420` Order-Parameter Hardening — a malformed jam/engage/cyber/maneuver/command/downlink param is rejected `invalid_param` by `dry_run` and `issue` before anything is booked, registered or scheduled (no HTTP 500, no ghost `queued`/`draft` order, no `-inf` power or `NaN` orbit, no wrong-length `dv` raising inside `advance_to`); explicit `null` = absent; planners build the payload before committing (`BL-0222`) | Remediation (forward design) | 🟢 VERIFIED | **Verified 2026-10-16** (`09-package-verification`, [VR-1052](verification/VR-1052-order-param-hardening.md), clean, fresh session): both `WorldState`-corruption claims (`-inf` jammer power via `power_w: "inf"`, `NaN` orbit/Δv via `dv: [NaN, 0, 0]`) independently reproduced-and-confirmed-fixed on fresh vignettes/seeds distinct from the implementer's own fixtures, including a load-bearing well-formed-order consumption counterfactual proving the jam-power mechanism is real. Ghost-order prevention independently confirmed across all five action types (jam/engage/cyber/maneuver/command) on fresh fixtures each. `_plan_collection`/`order.actor` ordering claim independently proved with a positive counterfactual (`VR-1041` standard): the mutation is real but confined to the discarded local `Order`, never leaking into shared sensor-booking state. `BL-0227` confirmed correctly scoped — the specific wrong-length-`dv` route is closed, the general `Simulation.advance_to` unlogged-drop gap is independently reconfirmed still live via an unrelated handler exception. Full suite 949 passed/3 skipped (952 collected) re-run exactly; gates 14/14. No findings against the package. **Implemented 2026-10-16** (`08-code-implementation`, pipeline run #137): per-action `invalid_param` check (`ORDER_PARAM_RULES`/`_order_params_ok`) in `_validate`; `null` = absent; registry insert after `_plan`, payload built before status/booking/schedule in every planner. 41 new tests; full suite 949 passed/3 skipped (952 collected), gates 14/14. **Authored 2026-10-16** (`07-implementation-planning`, pipeline run #136); defect class reproduced live at `d2ded6a` (`leo-isr-denial` seed 5). Dependencies `IP-1020`, `IP-1051`, `IP-1041` all `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** Range rules (`salvo_n`/`power_w`/`dwell_s` bounds) and the event-loop raising-handler question are deliberately out of scope (backlog, `BL-0226`/`BL-0227`). |
| [IP-1310](packages/IP-1310-load-time-vignette-validation.md) | FS-131 v1.1 `FR-5310`–`FR-5314`/`NFR-1600`/`NFR-2200` Load-Time Vignette Validation — one gate in `load_vignette` (`validate_vignette`, `VignetteValidationError`: entity validators at load, TLE parse, orbit/location presence with cyber units exempt, unique ids, `roles_needed` references, `build_world` catch-all); manager built before registry eviction/counter; 400/404 instead of 500; refusal shown at **Load** (`BL-0220`, `BL-0237`, `BL-0236`) | Forward design | ✅ VERIFIED | **Verified 2026-10-17** (`09-package-verification`, [VR-1310](verification/VR-1310-load-time-vignette-validation.md), fresh session, clean — no findings): the resource-exhaustion claim independently confirmed by direct state inspection (registry key set, counter, and per-slot object identity all unchanged after a rejected load at `MAX_LIVE_SESSIONS=32`, on a fresh 3-defect fixture; a subsequent legitimate load still evicts exactly the oldest slot). `BL-0237` (TLE crash-on-advance) independently reproduced on a fresh TLE corruption shape and confirmed refused at load. Multi-error collection independently confirmed on a 3-defect fixture. All three HTTP mappings (400/404/400, including a malicious-shaped traversal id) independently confirmed. Duplicate-asset-id handling confirmed a hard rejection, matching `FR-5313`/FS-131. `build_world` confirmed genuinely unchanged by diff read (only factored into a shared helper). Full suite 972 passed/3 skipped (975 collected) independently re-run exactly; gates 14/14; the "17 failed first / 6 passed" claim independently re-derived from the pre-implementation tree. **COMPLETE 2026-10-17** (`08-code-implementation`, pipeline run #146). 23 new tests; full suite 972 passed / 3 skipped (975 collected), gates 14/14. **Authored 2026-10-16** (`07-implementation-planning`, pipeline run #145). Dependencies `IP-1150`, `IP-1180` and `IP-1222` all `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** FS-131 criterion 10 (`FR-5310` template clause) is excluded, blocked on `BL-0233` (`03`). |
| [IP-1320](packages/IP-1320-effect-resource-bounds.md) | FS-132 v1.0 `FR-1460`/`FR-1470` Effect Resource Bounds — an `engage` whose consumed salvo exceeds the remaining rounds is rejected `insufficient_ammo` by `dry_run` and `issue`, and re-checked at execution (a queued engagement the rounds no longer cover logs a failed record, charges nothing); a jam no longer subtracts from the jammer's `power_w` (ADR-0037) (`BL-0238`, `BL-0245`) | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-10-17** (`09-package-verification`, [VR-1320](verification/VR-1320-effect-resource-bounds.md), fresh session, clean — no findings): all three claimed gate points (`dry_run`/`issue`/execution) and the jammer-power-unchanged claim (across three sequential jam orders) independently reproduced on fresh fixtures distinct from the implementer's own, with direct `WorldState` reads, not HTTP status alone. Failed-salvo/failed-maneuver log-shape parity and OQ3's all-or-nothing behaviour independently confirmed. Full suite 985 passed/3 skipped (988 collected) re-run exactly; gates 14/14. **COMPLETE 2026-10-17** (`08-code-implementation`, pipeline run #154). 13 new tests (6 seen failing first); full suite 985 passed / 3 skipped (988 collected), gates 14/14. One named fixture adjusted (`test_salvo_float_truncation_unchanged`). **Authored 2026-10-17** (`07-implementation-planning`, pipeline run #153). Dependencies `IP-1051` and `IP-1052` both `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** Decides FS-132 OQ1 (`insufficient_ammo`) and OQ2 (failed-manoeuvre-shaped record + `reason`). |
| [IP-1321](packages/IP-1321-missed-salvo-consumes-rounds.md) | FS-132 v1.1 `FR-1480` Missed Salvo Consumes Its Rounds — `_h_effect` charges the salvo for every engagement that reaches resolution, hit or miss (including a target already destroyed); the execute-time re-check still runs first and charges nothing when it fails (`BL-0249`, owner decision 2026-10-17) | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-10-17** (`09-package-verification`, [VR-1321](verification/VR-1321-missed-salvo-consumes-rounds.md), fresh session, clean — no findings): all four Objective-table cases (miss, hit, destroyed-target, re-check-failure-charges-nothing) independently reproduced on fresh fixtures distinct from the implementer's own (different effector/target ids, different seeds); replay determinism of a session containing a missed, charged salvo independently confirmed byte-for-byte; the "5 of 6 failed first" claim independently re-derived by mechanically reverting the fix and re-running, matching exactly. Full suite 1022 passed/3 skipped re-run exactly; gates 14/14. `BL-0249` → `DONE`; `BL-0276`'s revisit trigger fires: `DEFERRED → SCHEDULED`. **COMPLETE 2026-10-17** (pipeline run #178): `_h_effect` charges every fired salvo (the `outcome.success` term removed); 6 new tests (5 seen failing first); no fixture changed; full suite 1022 passed / 3 skipped; gates 14/14. **IN PROGRESS 2026-10-17** (pipeline run #178, `08-code-implementation`). **Authored 2026-10-17** (`07-implementation-planning`, pipeline run #176). Dependency `IP-1320` `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization; owner decision `BL-0249`).** |
| [IP-1330](packages/IP-1330-test-origin-marker-and-checks.md) | FS-133 v1.1 `NFR-2820`/`NFR-3840`/`NFR-2830`/`NFR-2850` Test-Origin Marker, Origin Checks, Origin Report and generated RTM Test column (v1.1, `BL-0322`) — registered `verifies` marker, strict markers, a suite check with a shrink-only allow-list, a `--origin-report` option; gate modules tagged (`BL-0310`) | Forward design | ✅ VERIFIED | **Authored 2026-10-23** (pipeline run #221). No dependencies. Verified 2026-10-24 by [VR-1330](verification/VR-1330-test-origin-marker-and-checks.md). `NFR-1510` (dependency lock) deferred to the first major release (`BL-0318`). |
| [IP-1331](packages/IP-1331-test-origin-backfill-engine-content.md) | FS-133 `NFR-2820` Test-Origin Backfill: engine and content modules (22) | Forward design (test-only) | 🔴 BLOCKED | On `IP-1330` reaching `VERIFIED`. Authored 2026-10-23 (run #221). Not yet authorized. |
| [IP-1332](packages/IP-1332-test-origin-backfill-session.md) | FS-133 `NFR-2820` Test-Origin Backfill: session-layer modules (32) | Forward design (test-only) | 🔴 BLOCKED | On `IP-1330` reaching `VERIFIED`. Authored 2026-10-23 (run #221). Not yet authorized. |
| [IP-1333](packages/IP-1333-test-origin-backfill-web.md) | FS-133 `NFR-2820` Test-Origin Backfill: web and cross-cutting modules (16); empties the allow-list | Forward design (test-only) | 🔴 BLOCKED | On `IP-1330` reaching `VERIFIED`. Authored 2026-10-23 (run #221). Not yet authorized. |
| [IP-1340](packages/IP-1340-browser-console-rule-suite.md) | FS-134 `NFR-2840` Browser Suite for the Load-Bearing Console Rules — Playwright + headless Chromium (installed build, explicit executable), in-process server, canvas labels observed via wrapped drawing calls; rules (a)–(c) (`BL-0304`) | Forward design (test-only) | ✅ VERIFIED | **Authored 2026-10-23** (pipeline run #222). No dependencies. **Not yet authorized** (MSTR-006 §3). |
| [IP-1350](packages/IP-1350-documentation-integrity-checks.md) | FS-135 `NFR-3800`/`NFR-3820`/`NFR-3830` Documentation Integrity Checks — relative links resolve, each `INDEX.md` lists its folder, three ledger pairs agree; shrink-only allow-lists hold today's 82 broken links and 3 unlisted documents (`BL-0297`). Check 2 (`NFR-3810`) awaits `BL-0319` | Forward design (test-only) | ✅ VERIFIED | **Authored 2026-10-23** (pipeline run #223). No dependencies. Owner-authorized 2026-10-23. Verified 2026-10-24 by [VR-1350](verification/VR-1350-documentation-integrity-checks.md). |
| [IP-1311](packages/IP-1311-vignette-id-scan-robustness.md) | FS-131 v1.1 `FR-5310`/`NFR-1600` Vignette Id Scan Robustness — `load_vignette`'s built-in and external declared-id scans share one helper that skips a file it cannot read, parse, or find a mapping `vignette` block in, so one bad file never turns an unknown id into a 500 or blocks a valid later-sorting vignette (`BL-0252`, REV-TRN-008 F2) | Remediation (forward design) | 🟢 READY | **Authored 2026-10-17** (`07-implementation-planning`, pipeline run #158). Dependencies `IP-1310` and `IP-1180` both `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** |
| [IP-1021](packages/IP-1021-failure-atomic-event-application.md) | FS-102 v1.1 + ADR-0038 `FR-1120`/`NFR-1600`/`NFR-2600` Failure-Atomic Event Application — a raising handler is rolled back to the replayed state, logged as a no-op failure record, and the advance continues (`BL-0264`, from `BL-0227`) | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-10-17** (`09-package-verification`, [VR-1021](verification/VR-1021-failure-atomic-event-application.md), fresh session, clean — no findings): the rollback independently confirmed to be a genuine "as-if-never-scheduled" state, not merely a non-crashing one, via an engine-level differential proof (a world that scheduled-and-crashed a new `probe_effect` handler is byte-for-byte identical, including RNG export state, to one that never scheduled it at all) plus a real-catalog-handler reproduction (`_h_maneuver`, direct-schedule bypass of `OrderSystem`, the `VR-1052` §6 mechanism) and a multiplayer-lock-seam reproduction through `InProcessSession` (lock released and re-acquirable, no corruption, `mgr.world`/`mgr.osys.world` identity preserved). Independently re-derived the "all tests failed first" claim — stronger than the package's own "at least 1, 2, 4" claim, confirmed all 7 of 7 fail against a genuine pre-fix scratch tree. Full suite 1016 passed/3 skipped re-run (grown from the implementer's 992/3 by sibling packages in the same batch, not a regression); both gates 14/14. **COMPLETE 2026-10-17** (pipeline run #167): failure-atomic `advance_to` + no-op `handler_error` record; 7 tests (all failed first); full suite 992 passed / 3 skipped; both gates green. **IN PROGRESS 2026-10-17** (pipeline run #167, `08-code-implementation`; baseline full suite 985 passed / 3 skipped). **Authored 2026-10-17** (`07-implementation-planning`, pipeline run #166, owner-prioritized `DEFERRED` clearance). Dependencies IP-1020 `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** |
| [IP-1064](packages/IP-1064-condition-inject-follow-ups.md) | FS-106 v2.1 `FR-4420`/`NFR-1100` Condition-Triggered Inject Follow-Ups — measured value in the firing record, start-anchored tick grids after a rewind, one log scan per tick (`BL-0131`/`BL-0132`/`BL-0133`) | Remediation (forward design) | ✅ VERIFIED | **VERIFIED 2026-10-17** (`09-package-verification`, fresh session, [VR-1064](verification/VR-1064-condition-inject-follow-ups.md) v2.0): the `BL-0278` fix independently reconfirmed on a fresh scenario (different metric/track/seed, true value computed by hand) and confirmed general on a third, distinct condition-type/effect-type pairing (`asset_operational`+`anomaly`) beyond the two shipped regression cases; anchored grids / one-scan-per-tick / `_evaluate_metric` byte-unchanged / replay-determinism all re-confirmed unregressed on fresh fixtures. Full suite 1025 passed/3 skipped; gates 14/14. No findings. **COMPLETE (re-run) 2026-10-17** (pipeline run #182, `08-code-implementation` against VR-1064 / `BL-0278`): `_h_condition_check` now captures `_measure_metric(...)` into a local **before** `_apply_inject_effects(...)` and records that captured value, so a self-affecting inject records the value the decision saw; 2 new regression tests (3 cases — `forced_custody_loss` degrade/drop on the measured track, `deny_custody` + `reveal_asset`), all 3 failed first (0.0 vs 0.8909; 1.0 vs 0.0); full suite 1025 passed / 3 skipped; gates 14 passed. Awaiting a fresh-session `09-package-verification` (not run #180's session, not run #182's). **RETURNED 2026-10-17** (`09-package-verification`, run #180, [VR-1064](verification/VR-1064-condition-inject-follow-ups.md), fresh session) — 1 failed check, Medium: `_h_condition_check` calls `_measure_metric` after `_apply_inject_effects`, so a condition inject whose own effects change the measured quantity records the post-effect value (custody ≥ 0.5 firing at 0.891 recorded as 0.0 with `forced_custody_loss`; `deny_custody` at 0.0 recorded as 1.0 with `reveal_asset`) — contradicts `FR-4420` Outputs / Objective 1 (`BL-0278`). Confirmed: anchored grids (two shipped vignettes, off-grid rewind → identical ticks and byte-identical final world; pre-fix tree differs), one scan per tick, `_evaluate_metric` byte-unchanged, the updated first-tick test a genuine correction (original passes pre-fix, fails post-fix only on `value: True`). Re-run `08-code-implementation` against VR-1064. **COMPLETE 2026-10-17** (pipeline run #170): measured value recorded (`_measure_metric`), tick grids anchored to `ctx.start_epoch`, one fired-set scan per tick; 3 new tests + 1 updated (3 failed first); full suite 1010 passed / 3 skipped; gates green. Awaiting `09-package-verification` (different session). **IN PROGRESS 2026-10-17** (pipeline run #170, `08-code-implementation`; baseline full suite 1007 passed / 3 skipped). **Authored 2026-10-17** (`07-implementation-planning`, pipeline run #166, owner-prioritized `DEFERRED` clearance). Dependencies IP-1062 `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** |
| [IP-1065](packages/IP-1065-console-and-session-small-fixes.md) | FS-106/FS-102 v1.1/FS-118 v1.1/FS-120/FS-119 `FR-4410`/`FR-3310`/`FR-5410`/`FR-5510`/`FR-5220`/`NFR-3400` White Cell Console and Session Small Fixes — Fire reports rejections, timeline shows executed, picker groups external vignettes, save-as-scenario control, bulk-import duplicate ids refused, ref-05/06 redrawn, CLAUDE.md no-cell list (`BL-0196`/`0266`/`0267`/`0145`/`0141`/`0185`/`0261`) | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-10-17** (`09-package-verification`, [VR-1065](verification/VR-1065-console-and-session-small-fixes.md), fresh session): Fire-rejection, origin grouping and the old behaviour of each, shown by running the shipped and pre-fix `app.js` functions under Node against real server responses; `executed` derivation swept over 11 instants on an observe order (`sda-custody-hunt` seed 777) — zero mismatches with `list_orders`/Design Decision 1; OMM-format duplicate ids refused (engine + HTTP); save-as-scenario white 200 / observer 403; `ref-05`/`ref-06` re-rendered pixel-identical; Pillow pre-existing and declared; 5/6 tests fail on a pre-fix tree; full suite + gates green. Low: RTM `FR-3310`/`NFR-3400` cells were missing `IP-1065` — added; `BL-0277` (older `pyproject.toml` comment / `CLAUDE.md` install-line nit) filed. **COMPLETE 2026-10-17** (pipeline run #169): timeline `executed`, bulk-import duplicate refusal, Fire shows rejections, picker optgroups by origin, White-only save-as-scenario control, ref-05/06 redrawn, CLAUDE.md no-cell set; 6 tests (5 failed first); full suite 1007 passed / 3 skipped; gates green. Manual impact filed. Awaiting `09-package-verification` (different session). **IN PROGRESS 2026-10-17** (pipeline run #169, `08-code-implementation`; baseline full suite 1001 passed / 3 skipped). **Authored 2026-10-17** (`07-implementation-planning`, pipeline run #166, owner-prioritized `DEFERRED` clearance). Dependencies IP-1063/IP-1180/IP-1190/IP-1200 `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** |
| [IP-1131](packages/IP-1131-verification-coverage-follow-ups.md) | FS-113/FS-115/FS-102 v1.1 + NFR-3400 `FR-6510`/`FR-4210`/`FR-3310`/`NFR-3400` Verification-Coverage Follow-Ups (test-only) — Observer rejection on `/roles/assign` and `/observer/view`, SSN-kind rewind parity, training `Sources:`-anchor test (`BL-0023`/`0024`/`0259`/`0260`) | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-10-17** (`09-package-verification`, run #181, [VR-1131](verification/VR-1131-verification-coverage-follow-ups.md), fresh session): the self-test claim was checked directly by mutation in a throwaway tree copy. `test_training_sources.py` fails on a renamed footer symbol, a moved path, a code-side rename (the A12 case), a deleted cited module, a continuation-line symbol, a gutted parser (count guard), and a gutted checker (the self-test). The Observer tests fail when the White-only gates admit `observer`; the FR-3310 parity test fails when `_rebind` keeps SSN requests or orders. Corpus coverage measured: 67 footers / 174 paths / 278 symbols. Full suite 1022/3; gates green. One Low hardening note (`BL-0279`): substring symbol match, corpus-wide footer-count guard, unchecked brace paths. **COMPLETE 2026-10-17** (pipeline run #171): test-only — 2 Observer HTTP tests, 1 direct `assign_role` Observer test, FR-3310 SSN/command rewind-parity test, `test_training_sources.py` (+ self-test); all passed on arrival (behaviour already correct; the self-test proves the anchor checker fails on a broken footer); no production file changed; full suite 1016 passed / 3 skipped; gates green. Awaiting `09-package-verification` (different session). **IN PROGRESS 2026-10-17** (pipeline run #171, `08-code-implementation`; baseline full suite 1010 passed / 3 skipped). **Authored 2026-10-17** (`07-implementation-planning`, pipeline run #166, owner-prioritized `DEFERRED` clearance). Dependencies IP-1130/IP-1151/IP-1040 `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** |
| [IP-1223](packages/IP-1223-beam-mode-follows-sensor-modality.md) | FS-122 v1.2 `FR-1610`/`NFR-1600` Beam-Mode Choice Follows the Sensor's Modality — a foreign mode is refused `invalid_param`; the console lists the sensor's own modes (`BL-0265`) | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-10-17** (`09-package-verification`, [VR-1223](verification/VR-1223-beam-mode-follows-sensor-modality.md), fresh session): the two edited pre-existing tests independently confirmed as necessary fixture corrections — their original (`bba6330^`) text passes pre-fix and fails post-fix only with `invalid_param`, the corrected `dish` versions pass on both trees and exercise the same footprint / normaliser paths; 8/9 new tests fail on a pre-fix scratch tree; independent HTTP probe on `sda-custody-hunt` seed 31337 (five foreign names refused, `dish` 1.6 / `fence` 0.5, auto filtered); console table mirrors `isr.BEAM_MODES` exactly; full suite 1016 passed / 3 skipped, gates 14/14. One Low traceability note (FS-122 `Referenced By` not advanced), corrected. **COMPLETE 2026-10-17** (pipeline run #168): foreign beam mode refused `invalid_param` (explicit + auto), auto filtered to sensors offering the mode, console list built from the tasked sensor; 9 tests (8 failed first); two pre-existing tests that tasked a radar with a SAR name moved to `dish` (the intended FS-122 v1.2 change); full suite 1001 passed / 3 skipped; both gates green. Awaiting `09-package-verification` (different session). **IN PROGRESS 2026-10-17** (pipeline run #168, `08-code-implementation`; baseline full suite 992 passed / 3 skipped). **Authored 2026-10-17** (`07-implementation-planning`, pipeline run #166, owner-prioritized `DEFERRED` clearance). Dependencies IP-1222/IP-1041 `VERIFIED`. **Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization).** |
| [IP-1230](packages/IP-1230-space-weather-index-coupling.md) | FS-123 v1.1 `FR-1230`/`FR-4440` Space-Weather-Index Coupling — a declared F10.7/Kp series drives opt-in LEO drag (`f_solar × f_geo`, ADR-0039) on the `bus_tick` grid and scales an opt-in environmental-anomaly base rate by `f_geo`; non-physical values refused at load and at the inject boundary (`BL-0074`, item B8) | Forward design | ✅ VERIFIED | **Verified 2026-10-18** (`09-package-verification`, [VR-1230](verification/VR-1230-space-weather-index-coupling.md), fresh session, clean — extra scrutiny given for touching orbital-perturbation physics and determinism): the ADR-0039 mapping independently re-derived on fresh inputs (`f_solar(225)=2.0`, `f_geo(6)=4.0`, etc., all matching hand computation); the drag-to-impulse conversion independently checked against the standard orbital-energy relation (`dv=μ·da/2a²v`), matching `busmodel.py` exactly; the "42 failed first / 4 passed" claim independently reproduced on a disposable pre-fix worktree. Full suite 1108 passed/3 skipped; gates 14/14. One Low bookkeeping finding (FS-123 `Referenced By` still read "planned") — corrected. **Implemented 2026-10-18 (pipeline run #189)**. 46 tests in `test_space_weather_index.py`; **42 seen failing first** on a pre-fix copy of the tree. 4 passed on arrival: the opt-out pins, the qualifying-asset pin, and the no-op replay. Full suite **1071 passed / 3 skipped** (baseline 1025/3, plus 46); gates 14/14. Deviations, disclosed: (1) Design Decision 8's validator is a pydantic `field_validator` rather than a `model_validator`, so a load refusal names `…ballistic_coeff_m2_kg`. (2) `index_series_problems` takes a `time_required` keyword, because an inject's `offset_s` defaults to 0 (Design Decision 2). (3) FS-123's `Referenced By` was not edited; `08` does not edit specs, so that is left for `09`, per the run #182 precedent. Authored 2026-10-18 (pipeline run #188). Dependencies `IP-1062`/`IP-1063`/`IP-1310`/`IP-1064`/`IP-1021` all `VERIFIED`. **Pre-authorized** (MSTR-006 §3, standing 2026-10-11 pre-authorization; owner's 2026-10-18 instruction for the stalled batch `BL-0068`–`BL-0083`). |
| [IP-1066](packages/IP-1066-pending-inject-edit-cancel.md) | FS-106 v2.3 `FR-4450` Pending-Inject Queue — White-only listing, cancel and edit of a scheduled, not-yet-fired inject as logged `inject_admin` actions (overrides folded from the event log; stale events skipped; edits rescheduled and re-armed after rewind) (`BL-0079`, item B13) | Forward design | ✅ VERIFIED | **Verified 2026-10-18** (`09-package-verification`, [VR-1066](verification/VR-1066-pending-inject-edit-cancel.md), fresh session): the "26 failed first / 1 passed" claim independently reproduced on a disposable pre-fix worktree; a fresh fixture independently confirmed cancel/edit/replay semantics. `BL-0284` (rewind drops an unedited White future-dated inject) independently reproduced and confirmed genuinely pre-existing (reproduced identically on the pre-`IP-1066` tree) — stays `SCHEDULED` for a small `07` remediation, correctly out of this package's scope. `BL-0285` (refusal vs. clamp narrowing) adjudicated acceptable. The pending-listing's no-cell gate confirmed to match FS-106 v2.3's actual Security Considerations text. Full suite 1108 passed/3 skipped; gates 14/14. No new findings. **Implemented 2026-10-18 (pipeline run #192)**. The package adds 27 tests in `test_pending_inject_queue.py`. **26 were seen failing first**; the one that passed on arrival pins an uncancelled condition inject still firing. Full suite: **1098 passed / 3 skipped** (run #189 baseline 1071/3, plus 27). Gates: 14/14. No existing test changed. Disclosed: the pending listing (`GET /injects/pending`) is a no-cell White read, like `/injects`. Only cancel and edit are 403-gated, which the package's tests specify. Authored 2026-10-18 (pipeline run #191). Dependencies `IP-1061`/`IP-1062`/`IP-1063`/`IP-1064`/`IP-1130` `VERIFIED`. **Pre-authorized** (MSTR-006 §3, standing 2026-10-11 pre-authorization; owner's 2026-10-18 instruction for the stalled batch `BL-0068`–`BL-0083`). |
| [IP-1067](packages/IP-1067-side-by-side-controller-view.md) | FS-106 v2.3 `FR-4620` Side-by-Side Controller View — one locked read returns ground truth plus Blue's and Red's `CellView` for a single simulated instant; White-only route + text Compare panel (`BL-0079`, item B13) | Forward design | ✅ VERIFIED | **Verified 2026-10-18** (`09-package-verification`, [VR-1067](verification/VR-1067-side-by-side-controller-view.md), fresh session, clean): the "9 failed first / 1 passed" claim independently reproduced on a disposable pre-fix worktree; a fresh fixture (`leo-isr-denial`) independently confirmed the read is genuinely read-only, single-instant across all three panels, byte-identical to direct `get_godview()`/`get_view(...)` calls, and leaks no cross-cell asset ids. Full suite 1108 passed/3 skipped; gates 14/14. No findings. **Implemented 2026-10-18 (pipeline run #193)**. The package adds 10 tests in `test_controller_view.py`. **9 were seen failing first**; the one that passed on arrival pins the unknown-session 404. Full suite: **1108 passed / 3 skipped** (run #192 baseline 1098/3, plus 10). Gates: 14/14. No existing test changed. Authored 2026-10-18 (pipeline run #191). Dependencies `IP-1060`/`IP-1130` `VERIFIED`. **Pre-authorized** (MSTR-006 §3, standing 2026-10-11 pre-authorization; owner's 2026-10-18 instruction for the stalled batch `BL-0068`–`BL-0083`). |
| [IP-1068](packages/IP-1068-white-only-controls-server-enforcement.md) | FS-106 v2.4 `FR-4310`/`FR-4320` White-Only Controls Enforced at the Server Boundary — every White Cell control (clock, step, advance, rewind, undo, start, param, inject, TLE/bulk/ground add, save load) refuses any request not naming `white`; a test per control (`BL-0307`, requirements review R1 High) | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-10-24** ([VR-1068](verification/VR-1068-white-only-controls-server-enforcement.md); fresh-session `09`; 37 failed-first reproduced; full suite 1280 passed/3 skipped). *Implemented 2026-10-23* (`08`, owner-authorized per MSTR-006 §3; `_require_white` guard on 11 routes + `load_save`; `test_white_only_controls.py`). *Authored 2026-10-23* (`07-implementation-planning`, pipeline run #219). Dependencies `IP-1060`, `IP-1130`, `IP-1151` `VERIFIED`. **Not yet authorized** (MSTR-006 §3): the owner chose server-side enforcement (`BL-0307`); the build go-ahead for this package is not on record. |
| [IP-1069](packages/IP-1069-white-only-panels-registered.md) | `NFR-3030` Compare and Assessment Panels Join the Panel Manager — register `compare-panel`/`assessment-panel` in `panels.js`; menu hides White-only panels from other seats; static registry test (`BL-0305`) | Remediation | ✅ VERIFIED | **Verified 2026-10-24** ([VR-1069](verification/VR-1069-white-only-panels-registered.md) v2.0; fresh-session `09`; the v1.0 `RETURNED` finding (Compare had no panel controls) closed by the `BL-0331` re-run and re-checked in Chromium; full suite 1284 passed/3 skipped). *Authored 2026-10-23* (pipeline run #224). Dependencies `IP-1067`, `IP-2010` `VERIFIED`. Owner-authorized 2026-10-23. |

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

**Update (2026-07-11, same session): `IP-1171` implemented.** `08-code-implementation` built the 8
typed `PayloadState` sub-models (`bus.py`) — `SatcomParams`/`IsrEoParams`/`IsrSarParams`/
`SigintParams`/`SdaParams`/`WeatherParams`/`MwParams`/`PntParams`, R109/R110/R129/R134-grounded,
auto-populated for exactly the field matching `PayloadState.type` via a new `model_validator` —
and confirmed `FR-5180`'s bus power/propulsion authoring already routes through
`Asset.model_validate()` to the live fields (`PowerState.charge_rate_per_s`/`drain_rate_per_s`,
`AssetResources.delta_v_ms`), never `AssetResources.power_w`, with no loader change needed. 12 new
tests (`test_typed_payload_params.py`), full suite **598 passed/3 skipped** (up from 586/3), both
permanent gates green — all 19 shipped vignettes confirmed unchanged. `IP-1171` flips
`READY → COMPLETE`. `IP-1174` remains `BLOCKED`, now solely on `IP-1171` reaching `VERIFIED`.

**Update (2026-09-27): the project owner authorized MSTR-006 §3 coding for all five Must-tier
packages queued this increment (`IP-1180`, `IP-1062`, `IP-1200`, `IP-1190`, `IP-1210`), directing
the pipeline to iterate through `08`/`09`/`10` continuously, pausing only at `11-release-readiness`'s
GO/NO-GO call.** `08-code-implementation` implemented **`IP-1190`** first (no shared-file
coordination risk with any of the other four — see `IP-1190`'s own Build-sequencing note): new
`content/bulk_import.py` (`parse_multi_tle`/`parse_ccsds_omm`, KVN-only), new public
`engine/orbit.py::mean_to_true()` (behavior-preserving extraction, confirmed via a bit-for-bit
regression test), `_force_add_tle_object`/`_force_add_omm_object`/`bulk_import()` on
`SessionManager`, and a new `POST /api/sessions/{sid}/force/bulk_import` route. 16 new tests, full
suite **638 passed/3 skipped** (up from 622/3), both permanent gates green. `IP-1190` flips
`READY → COMPLETE` (never `BLOCKED` — it had no unmet dependency, only the authorization gate,
now cleared). Resolves `BL-0096` in full. Next: `08-code-implementation` on `IP-1180` (external
vignette directories), building the coordination-flagged `save_vignette()`/`export_vignette()`
change first so `IP-1200` (implemented after it) builds against its actual landed diff.

**Update (2026-09-27, same session): `IP-1180` implemented second**, before `IP-1200`, per the
flagged coordination note. New `ContentConfig`/`load_content_config()` (`config.py`);
`content/vignette.py`'s `list_vignettes()`/`load_vignette()` extended to enumerate/search
configured external directories (built-in-wins collision rule, unreadable-directory skip, both
logged); traversal guard extracted into shared `_validate_id`/`_resolve_within_root` helpers;
`content/vignette_export.py::save_vignette()` retargeted to a configured `user_save_dir`, raising
when unconfigured. 23 new tests, 3 existing save-as-vignette tests updated (not rewritten) to
configure a `tmp_path` `user_save_dir` fixture. Full suite **661 passed/3 skipped** (up from
638/3), both permanent gates green. `IP-1180` flips `READY → COMPLETE`. Resolves `BL-0094`'s
remaining three Open Questions in full. `IP-1200` (implemented next) must build against this
landed diff — the optional `start_epoch` parameter and additive `initial_tracks`/
`simulator_version` fields `IP-1200` adds are new, non-conflicting extensions to the same
functions this run just changed. Next: `08-code-implementation` on `IP-1062` (FS-106 v2.1,
condition-triggered injects) — no shared-file coordination risk with any remaining package.

**Update (2026-09-27, same session): `IP-1062` implemented.** New `_h_condition_check` handler
+ periodic `condition_check` event, scheduled only when a vignette declares a condition-type
trigger; `_h_inject` refactored into a shared `_apply_inject_effects` helper (behavior-preserving
for all eight prior effect types — `test_inject_library.py` re-run with zero functional changes),
gaining four new branches (`anomaly`, `sensor_outage`, `forced_custody_loss`,
`scripted_manoeuvre`); new `Sensor.health` field + `scene_from_world()` filter mirroring the
existing ground-station-outage pattern. Resolved `BL-0091` (scripted-manoeuvre resolves through
the existing six entry modes, never a parallel mechanism) and `BL-0095` (a deleted-target
condition never fires; the Δv gate is deliberately bypassed per `ADR-0005`) in full. 17 new
tests, full suite **678 passed/3 skipped** (up from 661/3), both permanent gates green. `IP-1062`
flips `READY → COMPLETE`. Next: `08-code-implementation` on `IP-1200` (FS-120, save-as-scenario)
— must build against `IP-1180`'s actual landed diff, per the coordination note above.

**Update (2026-09-27, same session): `IP-1200` implemented**, built directly against `IP-1180`'s
actual landed `export_vignette()`/`save_vignette()`/`_validate_id`/`_resolve_within_root` shapes
(no conflict — additive `start_epoch` parameter and new `Vignette` fields, orthogonal to `IP-1180`'s
own changes). New `spacesim/version.py`, `SessionManager.save_as_scenario()`, and the
`as_scenario` threading through `InProcessSession`/`SaveVignetteRequest`. 11 new tests, full suite
**689 passed/3 skipped** (up from 678/3), both permanent gates green. `IP-1200` flips
`READY → COMPLETE`. Resolves `BL-0097` in full. Next: `08-code-implementation` on `IP-1210`
(FS-121/FS-103 v1.1, ephemeris export) — the last of the five authorized Must-tier packages.

**Update (2026-09-27, same session): `IP-1210` implemented — the last of the five authorized
Must-tier packages.** New `session/ephemeris.py` built exactly per `ADS-1500`'s System
Architecture: one shared time-span replay mechanism (`aar.state_at_time`, additive, does not
change `state_at`'s existing contract or its AAR-scrubber callers) and one shared ECI/RIC/CSV/OEM
serializer for both the truth (`FR-7410`) and cell-observed (`FR-7420`) variants. Resolved
`BL-0098` in full: a wholly-out-of-range time span raises naming the session's actual valid
range; a partially-out-of-range span is silently clamped. Confirmed by direct test that the
cell-observed export never reads `world.assets[...].orbit` for the target (always
`Track.state_estimate`) and resolves a merely-tracked reference object via the cell's own
(possibly stale) estimate, never ground truth. 18 new tests, full suite **707 passed/3 skipped**
(up from 689/3), both permanent gates green. `IP-1210` flips `READY → COMPLETE`. **This closes
the entire five-package Must-tier implementation tranche for this increment** — `IP-1180`,
`IP-1062`, `IP-1200`, `IP-1190`, `IP-1210` are all now `COMPLETE`, each awaiting
`09-package-verification` in its own fresh session (the same-session exclusion applies to all
five, since this session implemented every one of them).

**Update (2026-09-27, run #78): Seven new forward-design packages planned for the Should-tier
external-validation-report intake batch**, against the eight Feature Specifications
`06-feature-specification` drafted (`FS-122`, `FS-124`-`FS-129` — `FS-123` excluded, see below):
`IP-1220` (FS-122, sensor modality models, B7+B17), `IP-1240` (FS-124, debris persistence, B11),
`IP-1250` (FS-125, manoeuvre ledger, B6), `IP-1260` (FS-126, telemetry export, B9 — **`BLOCKED`**,
not `READY`, since its own Acceptance Criterion 1 needs `IP-1062`'s `anomaly` effect and `IP-1062`
is only `COMPLETE`, not yet `VERIFIED`), `IP-1270` (FS-127, effect-authorization gating + live ROE,
B10), `IP-1280` (FS-128, variable-speed AAR replay, B12), `IP-1290` (FS-129, jamming-delivery +
per-effect-class detectability, B15). `IP-1270` and `IP-1290` share one design dependency:
`IP-1270`'s Design Decision 1 authors the effect-classification enumeration (order action type ×
five-D's reversibility category) both `FR-3430` and `FR-1450` independently describe in identical
words (`BL-0105`) — `IP-1290` cites, does not re-derive, that resolution, and the two packages
should be sequenced with `IP-1270` first or closely coordinated. **No package was written for
`FS-123`** (space-weather-index drag/anomaly-rate coupling, B8) — its own Open Questions
(`BL-0104`/`BL-0121`, the index-to-scaling mapping function and implausible-index-value handling)
are genuine physics/design decisions this skill's own rules forbid inventing; `FS-123` remains
`🚧` until a `04`/`06` pass resolves them, at which point an eighth package (`IP-1230`, the next
free slot in this series) can be planned. **None of the seven is authorized (MSTR-006 §3)** — all
enter at `READY` (six) or `BLOCKED` (`IP-1260`, dependency-blocked not authorization-blocked), per
this skill's own default-unauthorized rule. See
[`01-technical-work-breakdown.md`](01-technical-work-breakdown.md) §"Should-tier batch (run #78)"
for the full split rationale (in this case, one Feature Spec → one package each, no splitting
needed — every FS in this batch fits a single coherent Definition of Done).

**Update (2026-09-27, `09-package-verification` batch, fresh agent context): `IP-1061` independently
verified.** [`VR-1061`](verification/VR-1061-inject-and-sizing-defect-remediation.md) checked every
Definition-of-Done item against the live tree at `d2818ff`: the full suite passed (707 passed, 3
skipped) and both permanent gates are green. A1, A2, A3 and A4 were re-derived with an independent
probe script, not only by re-running the package's own tests. The report also confirms that
`IP-1062`'s later `_apply_inject_effects()` refactor preserved the single validating `space_weather`
branch. `IP-1061` flips `COMPLETE → VERIFIED` with 3 Low findings, all package-text or RTM-shape
issues with no functional gap. The seven `COMPLETE` packages are being verified one per report, in
the order `IP-1061`, `IP-1174`, `IP-1190`, `IP-1180`, `IP-1062`, `IP-1200`, `IP-1210`.

**Update (2026-09-27, same verification batch): `IP-1174` RETURNED.**
[`VR-1174`](verification/VR-1174-vignette-creator-ui-surfaces.md) confirmed `FR-5120` through
`FR-5150` by driving the HTTP routes directly: JSON and form views converge, the ground-truth
preview tracks every edit, TLE and lat/long entry work, and the curated 52-site list loads. It found
one failed Definition-of-Done/requirement check. `FR-5160` requires seat-count declaration "per
cell", but `POST /creator/seats` rejects any body `cell` other than `white`, and that same field is
the target cell. Only White seats can be declared, so the Blue/Red options in the Creator UI fail
with 403. The package's own `test_seat_declaration_rejects_non_white_cell` pins this as intended.
There are also 2 Medium findings: `force/ground` has no owner/kind/lat/lon validation, and an
invalid owner produces HTTP 500. `IP-1174` flips `COMPLETE → IN PROGRESS`. Next step for it:
`08-code-implementation` re-run against `VR-1174`'s findings.

**Update (2026-09-27, same verification batch): `IP-1190` independently verified.**
[`VR-1190`](verification/VR-1190-bulk-tle-omm-import.md) confirmed every Definition-of-Done item
and both `FR-5220` Acceptance Criteria. `mean_to_true()` agrees with a hand-computed Kepler solution
and with the original inline expression bit for bit. The outright-rejection versus
per-object-failure distinction held against hand-built fixtures. `IP-1190` flips
`COMPLETE → VERIFIED` with 2 Medium findings, both routed for remediation planning rather than
blocking. First, the OMM `EPOCH` is discarded (elements are anchored at `ctx.start_epoch`) on a
false "same as `add_tle`" premise. Second, a malformed per-object assignment aborts the batch with
HTTP 500.

**Update (2026-09-27, same verification batch): `IP-1180` independently verified.** It was checked
before `IP-1200`, per both packages' coordination note.
[`VR-1180`](verification/VR-1180-external-vignette-directories.md) confirmed every
Definition-of-Done and Checklist item with hand-built temporary-directory fixtures. The confirmed
behaviours are:

- On an id collision, the built-in vignette wins and the collision is logged.
- A missing external directory is skipped, logged, and does not stop later directories being read.
- Saving goes only to `user_save_dir`, with a specific error when it is unset.
- There is a single shared traversal guard for load and save.

`IP-1180` flips `COMPLETE → VERIFIED` with 1 Low finding: a saved file cannot be loaded back unless
`user_save_dir` is also listed in `external_vignette_dirs`.

**Update (2026-09-27, same verification batch): `IP-1062` RETURNED.**
[`VR-1062`](verification/VR-1062-condition-triggered-injects-and-new-effects.md) confirmed the
condition-trigger mechanism (`FR-4420`) sound with a proximity condition on real orbits. It fires
at the first true tick, only once, with no mid-handler append. Replay equals live across plain,
exact-tick, prior-tick and non-aligned rewinds.

It also confirmed `sensor_outage`, `forced_custody_loss` and `scripted_manoeuvre` (Δv budget
untouched). It found one failed check (High H1): the `anomaly`/bus effect sets
`bus_state.mode = "safe_mode"` directly. `safe_mode.active` stays `False`, so the operator's
recovery strip shows safe mode while `begin_recovery` refuses with `not_safed`, and the
`asset_safed` metric reads `False`. The effect should go through
`enter_safe_mode()`/`exit_safe_mode()`. There is also 1 Medium finding (a malformed effect payload
raises mid-handler, leaving an unlogged partial mutation) and 4 Low findings.

`IP-1062` flips `COMPLETE → IN PROGRESS`. **`IP-1260` stays `BLOCKED`.** Its blocker (IP-1062
reaching `VERIFIED`) has not cleared, and the High finding sits in the exact `anomaly` effect
`IP-1260`'s Acceptance Criterion 1 depends on.

**Update (2026-09-27, same verification batch): `IP-1200` independently verified**, after `IP-1180`,
per the coordination note. [`VR-1200`](verification/VR-1200-save-as-scenario.md) round-tripped a
real mid-exercise session (`leo-isr-denial`). The session was saved as a scenario, reloaded, and
compared with the source session field by field. The start epoch equalled the save moment. Tracks,
space weather, and every asset's orbit, `bus_state` and resources were identical. `IP-1200` flips
`COMPLETE → VERIFIED` with 2 Low findings. The first is a package-text contradiction over
"byte-identical" output. The second is that the capability has no browser GUI control and is
reachable only through the API.

**Update (2026-09-27, same verification batch): `IP-1210` RETURNED. This closes the seven-package
verification batch.** [`VR-1210`](verification/VR-1210-ephemeris-export.md) confirmed ECI state
vectors, RIC position, the cell-observed fog-of-war rule, the range reject-versus-clamp split and
determinism. It found one failed check (High H1): the exported RIC velocity omits the rotating-frame
`ω×ρ` term. A co-orbital, RIC-stationary neighbour reports −13.29 m/s radial velocity. It also found
2 Medium findings (the OEM file is non-conformant and carries no RIC) and 2 Low findings.
`IP-1210` flips `COMPLETE → IN PROGRESS`.

**Batch outcome:**

- **`VERIFIED` (4):** `IP-1061`, `IP-1190`, `IP-1180`, `IP-1200`.
- **`RETURNED` → `IN PROGRESS` (3):** `IP-1174` (`FR-5160` seat declaration is White-only),
  `IP-1062` (`anomaly`/bus effect is half-safe and unrecoverable) and `IP-1210` (RIC velocity).
  Each needs an `08-code-implementation` re-run against its VR, followed by a fresh
  `09-package-verification`.
- **`IP-1260` stays `BLOCKED`** on `IP-1062`.

**Update (2026-09-27/28): `IP-1174` remediated, flips `IN PROGRESS → COMPLETE`.** All three
findings (`BL-0123` High, `BL-0124`/`BL-0125` Medium) fixed; `BL-0127` (stale package prose)
corrected in place. See this package's status-table row above for the fix detail. Awaiting a
fresh `09-package-verification` pass. `IP-1062` and `IP-1210` remain `IN PROGRESS`, remediation not
yet started.

**Update (2026-10-17, pipeline run #159): package-text maintenance pass, no status change.** 17
already-`VERIFIED` packages (`IP-1010`, `IP-1020`, `IP-1030`, `IP-1040`, `IP-1050`, `IP-1051`,
`IP-1060`, `IP-1061`, `IP-1070`, `IP-1090`, `IP-1100`, `IP-1140`, `IP-1150`, `IP-1170`, `IP-1190`,
`IP-1200`, `IP-3010`) gained a dated **Post-verification maintenance notes** section (plus a header
pointer) that corrects the prose and citation findings their Verification Reports raised
(`BL-0001`, `BL-0016`, `BL-0017`, `BL-0030`, `BL-0032`, `BL-0036`–`BL-0047`, `BL-0058`, `BL-0102`,
`BL-0144`, `BL-0146`, `BL-0147`). The two false claims (`IP-1020`'s four-state lifecycle vocabulary,
`IP-1100`'s persisted Role Assignments) and the one file misattribution (`IP-1051`'s residual
constants live in `effects.py`) are corrected explicitly. Line-number drift is closed by declaring
the paired symbol name the durable anchor, with current lines as of `e1e721c`. No package's scope,
Definition of Done outcome, status or authorization changed; this table is unchanged.

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
IP-1171 (✅ VERIFIED 2026-07-12, VR-1171 — cleared)
   │
   ▼
IP-1174 (🟡 READY — authorized 2026-07-05, run #45; every dependency (IP-1171/IP-1172/IP-1173)
         now VERIFIED — the last package in Tranche 3 awaiting 08-code-implementation)

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
`IP-1171` was implemented (`08-code-implementation`, run #51) and has since passed independent
verification too (`VERIFIED`, `VR-1171`, 2026-07-12, fresh session) — the 8 typed `PayloadState`
sub-models and `FR-5180`'s bus power/propulsion authoring confirmation both independently
re-derived against the live tree. **All five Tranche 3 packages except `IP-1174` are now
`VERIFIED`.** `IP-1174` flips `BLOCKED → READY` — every one of its three dependencies
(`IP-1171`/`IP-1172`/`IP-1173`) is now `VERIFIED`, and it was already authorized 2026-07-05 (run
#45). This tranche's remaining forward motion is a mix of standing findings/backlog work (Risk
items 6/9, `IP-1151`'s own `BL-0014`), `IP-1160`'s standing authorization gate, and `IP-1174`
itself — the next stage-appropriate step for the 18 pre-Tranche-3 `VERIFIED` packages remains
`10-integration-review`/`11-release-readiness`; for `IP-1160`, it is the project owner's MSTR-006
§3 go-ahead; for Tranche 3, it is `08-code-implementation` on `IP-1174`, the last package in this
tranche.

**Remediation tranche (2026-09-26):** `IP-1061` (Inject Scheduling & Sizing-Cap Defect Remediation
— `FR-4410` + `NFR-1300`/ADR-0019) was authored `READY` and authorized (run #53), sequenced ahead
of `IP-1174` by the project owner, and **implemented this same day (run #54)**: `_arm_schedule()`'s
initial-vs-re-arm distinction (A1), the merged `space_weather` branch (A3), the corrected
`inject_library.yaml` comment (A2), and the removed hard satellite/constellation cap (A4) — 5 new
tests, full suite 603 passed/3 skipped, both permanent gates green. `IP-1061` is now `COMPLETE`,
awaiting `09-package-verification` (fresh session) before `08-code-implementation` picks up
`IP-1174`.

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
IP-1060 (White Cell Dashboard) ──► IP-1061 (Inject/Sizing remediation, 2026-09-26)  IP-2010 (Competency Assessment)
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
reached `VERIFIED` (run #48), unblocking `IP-1171`; `IP-1171` was implemented and has since also
reached `VERIFIED` (`VR-1171`, 2026-07-12); `IP-1172` and `IP-1173` reached `VERIFIED` 2026-07-11.
**`IP-1174` now flips `BLOCKED → READY`** — every one of its three dependencies is `VERIFIED`, and
it was already authorized alongside the rest of this tranche; it is the sole package left to
implement in this plan.

**Note (pipeline run #224, 2026-10-23): `IP-1069` (`BL-0305`) and `IP-1091` (`BL-0309`) added — not on the critical path; dependencies `VERIFIED`; independent of each other.**

**Note (pipeline run #223, 2026-10-23): `IP-1350` (FS-135, `FEAT-12300`, `BL-0297`) added — not on the critical path; no dependencies. The `NFR-3810` check gets its own package once `BL-0319` is decided.**

**Note (pipeline run #222, 2026-10-23): `IP-1340` (FS-134, `FEAT-12200`, `BL-0304`) added — not on the critical path; no dependencies, no dependents.**

**Note (pipeline run #221, 2026-10-23): `IP-1330`–`IP-1333` (FS-133, `FEAT-12100`, `BL-0310`) added — not on the critical path.** Edges `IP-1330 ──► IP-1331`, `IP-1330 ──► IP-1332`, `IP-1330 ──► IP-1333` (chain length 2); the three backfill packages are independent of each other.

**Note (pipeline run #220, 2026-10-23): `IP-1101` (FS-110 v2.0, `FEAT-7200`, `BL-0302`/`BL-0315`) added — not on the critical path.** Dependencies `IP-1100`/`IP-1310`/`IP-1200` `VERIFIED`; no package depends on it. Shares the `load_save` route with `IP-1068` (no ordering required). `READY`, not yet authorized.

**Note (pipeline run #219, 2026-10-23): `IP-1068` (FS-106 v2.4, `FEAT-4300`, `BL-0307`) added — not on the critical path.** Dependencies `IP-1060`/`IP-1130`/`IP-1151` `VERIFIED` (chain length 1); no package depends on it. `READY`, not yet authorized.

**Note (pipeline run #191, 2026-10-18): `IP-1066` and `IP-1067` (FS-106 v2.3, `BL-0079`) added — not on the critical path.** `IP-1066`'s dependencies `IP-1061`/`IP-1062`/`IP-1063`/`IP-1064`/`IP-1130` and `IP-1067`'s `IP-1060`/`IP-1130` are all `VERIFIED` (chain length 1). The two are independent of each other; no package depends on either.

**Note (pipeline run #188, 2026-10-18): `IP-1230` (FS-123 v1.1, ADR-0039, `BL-0074`) added — not on the critical path.** Its dependencies `IP-1062`, `IP-1063`, `IP-1310`, `IP-1064` and `IP-1021` are all `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1062`/`IP-1063`/`IP-1310`/`IP-1064`/`IP-1021` ──► `IP-1230`.

**Note (pipeline run #110, 2026-10-11): `IP-1063` (`BL-0129` + `BL-0188` remediation, FS-106 `FR-4430`/`FR-4410`) added — not on the critical path.** Dependencies `IP-1062` and `IP-1061` are both `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1062 ──► IP-1063` and `IP-1061 ──► IP-1063` are recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, 2026-10-11).

**Note (pipeline run #145, 2026-10-16): `IP-1310` (FS-131 v1.1, `FEAT-5300`, `FR-5310`–`FR-5314`) added — not on the critical path.** Dependencies `IP-1150`, `IP-1180` and `IP-1222` are `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1150 ──► IP-1310`, `IP-1180 ──► IP-1310` and `IP-1222 ──► IP-1310` are recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization).

**Note (pipeline run #153, 2026-10-17): `IP-1320` (FS-132 v1.0, `FEAT-1400`, `FR-1460`/`FR-1470`) added — not on the critical path.** Dependencies `IP-1051` and `IP-1052` are `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1051 ──► IP-1320` and `IP-1052 ──► IP-1320` are recorded here and in the package's own Dependencies field. `IP-1160` (`BLOCKED`) also edits `engine/orders.py::_validate`; a later `IP-1160` rebases over this package. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization).

**Note (pipeline run #176, 2026-10-17): `IP-1321` (FS-132 v1.1, `FEAT-1400`, `FR-1480`; `BL-0249` owner decision — a missed salvo consumes its rounds) added — not on the critical path.** Dependency `IP-1320` is `VERIFIED` (chain length 1); no package depends on it. Edge `IP-1320 ──► IP-1321` is recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization).

**Note (pipeline run #166, 2026-10-17): five remediation packages added for the owner-prioritized `DEFERRED` backlog clearance — `IP-1021` (ADR-0038), `IP-1064`, `IP-1065`, `IP-1131` (test-only), `IP-1223` — none on the critical path, no edges among them or to `IP-1311`; all can run in any order.** Each depends only on `VERIFIED` packages. Suggested order: `IP-1021` first (engine invariant, Medium), then `IP-1223`, `IP-1065`, `IP-1064`, `IP-1131`.

**Note (pipeline run #158, 2026-10-17): `IP-1311` (FS-131 v1.1, `FEAT-5300`, `FR-5310`/`NFR-1600`; `BL-0252` remediation) added — not on the critical path.** Dependencies `IP-1310` and `IP-1180` are `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1310 ──► IP-1311` and `IP-1180 ──► IP-1311` are recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization).

**Note (pipeline run #136, 2026-10-16): `IP-1052` (`BL-0222` remediation, FS-105 v1.1 + FS-102, `FR-3110`/`FR-1310`/`FR-1410`/`FR-1420`) added — not on the critical path.** Dependencies `IP-1020`, `IP-1051` and `IP-1041` are `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1020 ──► IP-1052`, `IP-1051 ──► IP-1052` and `IP-1041 ──► IP-1052` are recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization). `IP-1160` (`BLOCKED`) also edits `_validate`; whichever lands second rebases.

**Note (pipeline run #132, 2026-10-16): `IP-1041` (`BL-0219` + `BL-0217` remediation, FS-104 `FR-3210` + FS-122 `FR-1610`) added — not on the critical path.** Dependencies `IP-1040` and `IP-1222` are `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1040 ──► IP-1041` and `IP-1222 ──► IP-1041` are recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization). The same pass corrected `IP-1171`'s stale status row (`BL-0218`).

**Note (pipeline run #128, 2026-10-16): `IP-1222` (`BL-0212`/`BL-0213`/`BL-0214` remediation, FS-122 v1.1 `FR-1610`/`FR-1630`/`FR-1640`) added — not on the critical path.** Dependencies `IP-1220` and `IP-1221` are `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1220 ──► IP-1222` and `IP-1221 ──► IP-1222` are recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization).

**Note (pipeline run #124, 2026-10-15): `IP-1221` (FS-122 v1.1, `FR-1670`) added — not on the critical path.** Dependencies `IP-1220` and `IP-1300` are `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1220 ──► IP-1221` and `IP-1300 ──► IP-1221` are recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization). *(Status at the time of this note; `IP-1221` is now `VERIFIED` via `VR-1221`, 2026-10-16.)*

**Note (pipeline run #118, 2026-10-15): `IP-1212` (`BL-0201` remediation, FS-121 v2.1 `FR-7440`) added — not on the critical path.** Dependency `IP-1211` is `VERIFIED` (chain length 1); no package depends on it. Edge `IP-1211 ──► IP-1212` is recorded here and in the package's own Dependencies field. `READY`, pre-authorized (MSTR-006 §3, project owner, standing 2026-10-11 pre-authorization). *(Status at the time of this note; `IP-1212` is now `VERIFIED` via `VR-1212`, 2026-10-15 — `BL-0210`.)*

**Note (pipeline run #104, 2026-10-11): `IP-1262` (`BL-0176` remediation, FS-121 + FS-126) added — not on the critical path.** Dependencies `IP-1210`, `IP-1260`, `IP-1261` are all `VERIFIED` (chain length 1); no package depends on it. Edges `IP-1210 ──► IP-1262`, `IP-1260 ──► IP-1262`, `IP-1261 ──► IP-1262` are recorded here and in the package's own Dependencies field; same scoping caveat as the run #86 note below.

**Note (pipeline run #99, 2026-10-11): `IP-1261` (`BL-0170` remediation, FS-126 `FR-2320` + FS-121 migration) added — not on the critical path.** Its dependencies (`IP-1260`, `IP-1210`) are both `VERIFIED` (chain length 1); no package depends on it. Graph edges `IP-1260 ──► IP-1261` and `IP-1210 ──► IP-1261` are recorded here and in the package's own Dependencies field; the `## Dependency graph` diagram itself is not re-drawn, same scoping caveat as the run #86 note below. No parallelism constraint with any other open package.

**Note (run #91, 2026-10-10): `IP-1211` (FS-121 v2.0, `FR-7440`) added — not on the critical path.** Its dependencies are all `VERIFIED` (chain length 1); no package depends on it. Same scoping caveat as the run #86 note below.

**Note (run #86, 2026-10-03): `IP-1300` (FS-130) added — not on the critical path.** Its only
dependencies (`IP-1210`, and the pre-dependency-graph-tracked `FS-105`/`FS-106`) are `VERIFIED`;
chain length 1. This addendum does not re-derive the full dependency graph/critical-path sections
above for the `IP-1220`-`IP-1290` Should-tier batch, which predates this addendum and is not yet
reflected in the `## Dependency graph`/`## Parallel implementation opportunities` diagrams — that
pre-existing staleness is out of this package's own scope to close.

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
  depended only on `IP-1170` and has since been implemented and independently verified too
  (`VR-1171`, 2026-07-12). `IP-1174` is the sole package remaining in this tranche — now `READY`,
  every one of its three dependencies (`IP-1171`/`IP-1172`/`IP-1173`) `VERIFIED` — the natural last
  package in this tranche's build order.

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
  (run #45), implemented runs #46-#51/2026-07-11, all four prerequisite packages independently
  verified (`IP-1170` run #48; `IP-1172`/`IP-1173` 2026-07-11; `IP-1171` 2026-07-12, all fresh
  sessions):** `IP-1170`/`IP-1172`/`IP-1173`/`IP-1171` are all now `VERIFIED`; `IP-1174` is the
  sole package remaining, now `READY`.
- **Package Status (2026-09-27, after the seven-package `09-package-verification` batch):** **26
  `VERIFIED`, 0 `COMPLETE`, 3 `IN PROGRESS`, 6 `READY`, 2 `BLOCKED`.**
  - Newly `VERIFIED`: `IP-1061` (`VR-1061`), `IP-1190` (`VR-1190`), `IP-1180` (`VR-1180`) and
    `IP-1200` (`VR-1200`).
  - RETURNED to `IN PROGRESS`: `IP-1174` (`VR-1174`), `IP-1062` (`VR-1062`) and `IP-1210`
    (`VR-1210`), each with one High finding.
  - `READY` (none authorized): `IP-1220`, `IP-1240`, `IP-1250`, `IP-1270`, `IP-1280`, `IP-1290`.
  - `BLOCKED`: `IP-1160` (authorization) and `IP-1260` (on `IP-1062`).

**Update (2026-09-27/28): all three `IN PROGRESS` packages remediated** (`IP-1174`, `IP-1062`,
`IP-1210` — see their own status-table rows above), each now `COMPLETE` awaiting a fresh
`09-package-verification` pass. **The six `READY` Should-tier packages were authorized the same
day (MSTR-006 §3, project owner's direct instruction, batched together).** `IP-1220` is now
`COMPLETE` (implemented 2026-09-28, see its own row above); the remaining five
(`IP-1240`/`IP-1250`/`IP-1270`/`IP-1280`/`IP-1290`) stay `READY`, authorized, queued for
implementation in this same session.

- **Package Status (2026-10-24, `IP-1340` verified):** `IP-1340` `VERIFIED` by `VR-1340` (fresh-session `09`; 0 failed checks, 4 Low findings). Other statuses as the `IP-1350` line below.
- **Package Status (2026-10-24, `IP-1350` verified):** `IP-1350` `VERIFIED` by `VR-1350` (fresh-session `09`; 0 failed checks, 1 Medium + 4 Low findings). Other statuses as the run #244 line below.
- **Package Status (2026-10-24, `IP-1069` re-verified):** `IP-1069` `VERIFIED` ([VR-1069](verification/VR-1069-white-only-panels-registered.md) v2.0).
- **Package Status (2026-10-24, run #244, `IP-1069` re-run):** `IP-1069` back to `COMPLETE` after `VR-1069` returned it; awaiting fresh-session `09`. Other packages: `IP-1068`, `IP-1101`, `IP-1091`, `IP-1330` `VERIFIED`; `IP-1350`, `IP-1340` `COMPLETE`; `IP-1311` `READY`; `IP-1331`–`IP-1333` eligible (`IP-1330` is `VERIFIED`) though their rows still read `BLOCKED`; `IP-1160` `BLOCKED`.
- **Package Status (2026-10-23, run #236, `IP-1340` implemented):** **57 `VERIFIED`, 7 `COMPLETE` (`IP-1068`, `IP-1069`, `IP-1091`, `IP-1101`, `IP-1330`, `IP-1340`, `IP-1350`, awaiting `09`), 1 `READY` (`IP-1311`), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333` on `IP-1330` reaching `VERIFIED`) — 69 packages total.**
- **Package Status (2026-10-23, run #235, `IP-1350` implemented):** **57 `VERIFIED`, 6 `COMPLETE` (`IP-1068`, `IP-1069`, `IP-1091`, `IP-1101`, `IP-1330`, `IP-1350`, awaiting `09`), 2 `READY` (`IP-1311`; `IP-1340`), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333` on `IP-1330` reaching `VERIFIED`) — 69 packages total.**
- **Package Status (2026-10-23, run #234, `IP-1330` implemented):** **57 `VERIFIED`, 5 `COMPLETE` (`IP-1068`, `IP-1069`, `IP-1091`, `IP-1101`, `IP-1330`, awaiting `09`), 3 `READY` (`IP-1311`; `IP-1340`, `IP-1350`), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333` — now blocked on `IP-1330` reaching `VERIFIED`, which is `COMPLETE`) — 69 packages total.**
- **Package Status (2026-10-23, run #233, `IP-1069` implemented):** **57 `VERIFIED`, 4 `COMPLETE` (`IP-1068`, `IP-1069`, `IP-1091`, `IP-1101`, awaiting `09`), 4 `READY` (`IP-1311`; `IP-1330`, `IP-1340`, `IP-1350`), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333`) — 69 packages total.**
- **Package Status (2026-10-23, run #232, `IP-1091` implemented):** **57 `VERIFIED`, 3 `COMPLETE` (`IP-1068`, `IP-1091`, `IP-1101`, awaiting `09`), 5 `READY` (`IP-1311`; `IP-1069`, `IP-1330`, `IP-1340`, `IP-1350`), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333`) — 69 packages total.**
- **Package Status (2026-10-23, run #231, `IP-1101` implemented):** **57 `VERIFIED`, 2 `COMPLETE` (`IP-1068`, `IP-1101`, awaiting `09`), 6 `READY` (`IP-1311`; `IP-1069`, `IP-1091`, `IP-1330`, `IP-1340`, `IP-1350`), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333`) — 69 packages total.**
- **Package Status (2026-10-23, run #230, `IP-1068` implemented):** **57 `VERIFIED`, 1 `COMPLETE` (`IP-1068`, awaiting `09`), 7 `READY` (`IP-1311`; `IP-1069`, `IP-1091`, `IP-1101`, `IP-1330`, `IP-1340`, `IP-1350` — all nine planned packages owner-authorized 2026-10-23), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333`) — 69 packages total.**
- **Package Status (2026-10-23, run #224, `IP-1069`/`IP-1091` added):** **57 `VERIFIED`, 0 `COMPLETE`, 8 `READY` (`IP-1311`; `IP-1068`, `IP-1069`, `IP-1091`, `IP-1101`, `IP-1330`, `IP-1340`, `IP-1350` not yet authorized), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333`) — 69 packages total.**
- **Package Status (2026-10-23, run #223, `IP-1350` added):** **57 `VERIFIED`, 0 `COMPLETE`, 6 `READY` (`IP-1311`; `IP-1068`, `IP-1101`, `IP-1330`, `IP-1340`, `IP-1350` not yet authorized), 4 `BLOCKED` — 67 packages total.**
- **Package Status (2026-10-23, run #222, `IP-1340` added):** **57 `VERIFIED`, 0 `COMPLETE`, 5 `READY` (`IP-1311`; `IP-1068`, `IP-1101`, `IP-1330`, `IP-1340` not yet authorized), 4 `BLOCKED` — 66 packages total.**
- **Package Status (2026-10-23, run #221, `IP-1330`–`IP-1333` added):** **57 `VERIFIED`, 0 `COMPLETE`, 4 `READY` (`IP-1311`; `IP-1068`, `IP-1101`, `IP-1330` not yet authorized), 4 `BLOCKED` (`IP-1160`; `IP-1331`–`IP-1333` on `IP-1330`) — 65 packages total.**
- **Package Status (2026-10-23, run #220, `IP-1101` added):** **57 `VERIFIED`, 0 `COMPLETE`, 3 `READY` (`IP-1311`; `IP-1068`, `IP-1101` not yet authorized), 1 `BLOCKED` (`IP-1160`) — 61 packages total.**
- **Package Status (2026-10-23, run #219, `IP-1068` added):** **57 `VERIFIED`, 0 `COMPLETE`, 2 `READY` (`IP-1311`, `IP-1068` — the latter not yet authorized), 1 `BLOCKED` (`IP-1160`) — 60 packages total.**
- **Package Status (2026-10-18, run #194, `09-package-verification` on `IP-1230`/`IP-1066`/`IP-1067`):** **57 `VERIFIED`, 0 `COMPLETE`, 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 59 packages total.** `IP-1230` → [VR-1230](verification/VR-1230-space-weather-index-coupling.md) (clean), `IP-1066` → [VR-1066](verification/VR-1066-pending-inject-edit-cancel.md) (two upstream findings adjudicated, no new findings), `IP-1067` → [VR-1067](verification/VR-1067-side-by-side-controller-view.md) (clean). The stalled batch `BL-0068`–`BL-0083` has no package left awaiting verification; `BL-0080` remains `NEEDS-USER` (an architecture-scope decision, not a package).
- **Package Status (2026-10-18, run #193, `08-code-implementation` on `IP-1067`):** **54 `VERIFIED`, 3 `COMPLETE` (`IP-1230`, `IP-1066`, `IP-1067`, awaiting fresh-session 09), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 59 packages total.** No package depends on `IP-1067`.
- **Package Status (2026-10-18, run #192, `08-code-implementation` on `IP-1066`):** **54 `VERIFIED`, 2 `COMPLETE` (`IP-1230`, `IP-1066`, awaiting fresh-session 09), 2 `READY` (`IP-1311`, `IP-1067`), 1 `BLOCKED` (`IP-1160`) — 59 packages total.** No package depends on `IP-1066`.
- **Package Status (2026-10-18, run #191, `IP-1066`/`IP-1067` added):** **54 `VERIFIED`, 1 `COMPLETE` (`IP-1230`, awaiting a fresh-session 09), 3 `READY` (`IP-1311`, `IP-1066`, `IP-1067`, all pre-authorized), 1 `BLOCKED` (`IP-1160`) — 59 packages total.** No package depends on either new package.
- **Package Status (2026-10-18, run #189, `08-code-implementation` on `IP-1230`):** **54 `VERIFIED`, 1 `COMPLETE` (`IP-1230`, awaiting a fresh-session 09), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 57 packages total.** No package depends on `IP-1230`.
- **Package Status (2026-10-18, run #188, `IP-1230` added):** **54 `VERIFIED`, 0 `COMPLETE`, 2 `READY` (`IP-1311`, `IP-1230`, both pre-authorized), 1 `BLOCKED` (`IP-1160`) — 57 packages total.** No package depends on `IP-1230`.
- **Package Status (2026-10-17, run #184, `09-package-verification` on `IP-1064`):** **54 `VERIFIED`, 0 `COMPLETE`, 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** `IP-1064` → `VERIFIED` via [VR-1064](verification/VR-1064-condition-inject-follow-ups.md) v2.0, clean (the `BL-0278` fix independently reconfirmed and generalized). No package depends on `IP-1064`. `BL-0270` closes.
- **Package Status (2026-10-17, run #183, `09-package-verification` on `IP-1321`, merged onto the concurrent `IP-1064` re-run):** **53 `VERIFIED`, 1 `COMPLETE` (`IP-1064` re-run, awaiting a fresh `09`), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** `IP-1321` → `VERIFIED` via [VR-1321](verification/VR-1321-missed-salvo-consumes-rounds.md), clean. No package depends on `IP-1321`.
- **Package Status (2026-10-17, run #182, `08-code-implementation` re-run on `IP-1064`):** **52 `VERIFIED`, 2 `COMPLETE` (`IP-1321`, `IP-1064` re-run, awaiting 09), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** `IP-1064` `IN PROGRESS → COMPLETE` after the `BL-0278` fix. No package depends on `IP-1064`.
- **Package Status (2026-10-17, run #181, `09-package-verification` on `IP-1131`):** **52 `VERIFIED`, 1 `COMPLETE` (`IP-1321`, awaiting 09), 1 `IN PROGRESS` (`IP-1064`, returned by [VR-1064](verification/VR-1064-condition-inject-follow-ups.md), `BL-0278`), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** `IP-1131` → `VERIFIED` via [VR-1131](verification/VR-1131-verification-coverage-follow-ups.md). No package depends on `IP-1131`.
- **Package Status (2026-10-17, run #180, `09-package-verification` on `IP-1064`):** **51 `VERIFIED`, 2 `COMPLETE` (`IP-1131`, `IP-1321`, awaiting 09), 1 `IN PROGRESS` (`IP-1064`, returned by [VR-1064](verification/VR-1064-condition-inject-follow-ups.md) — Medium `BL-0278`, re-run `08`), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** No package depends on `IP-1064`.
- **Package Status (2026-10-17, run #179, `09-package-verification` on `IP-1065`):** **51 `VERIFIED`, 3 `COMPLETE` (`IP-1064`, `IP-1131`, `IP-1321`, awaiting 09), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** `IP-1065` → `VERIFIED` via [VR-1065](verification/VR-1065-console-and-session-small-fixes.md). No package depends on `IP-1065`.
- **Package Status (2026-10-17, run #178, `08-code-implementation` on `IP-1321`):** **50 `VERIFIED`, 4 `COMPLETE` (`IP-1065`, `IP-1064`, `IP-1131` — a concurrent session is verifying them — and `IP-1321`, all awaiting 09), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** No package depends on `IP-1321`.
- **Package Status (2026-10-17, run #177, `09-package-verification` on `IP-1223`):** **50 `VERIFIED`, 3 `COMPLETE` (`IP-1065`, `IP-1064`, `IP-1131`, awaiting 09), 2 `READY` (`IP-1311`, `IP-1321`), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** `IP-1223` → `VERIFIED` via [VR-1223](verification/VR-1223-beam-mode-follows-sensor-modality.md). No package depends on `IP-1223`.
- **Package Status (2026-10-17, run #176, `IP-1321` added):** **49 `VERIFIED`, 4 `COMPLETE` (`IP-1223`, `IP-1065`, `IP-1064`, `IP-1131`, awaiting 09 — a concurrent session is verifying them), 2 `READY` (`IP-1311`, `IP-1321`, both pre-authorized), 1 `BLOCKED` (`IP-1160`) — 56 packages total.** No package depends on `IP-1321`.
- **Package Status (2026-10-17, run #173, `09-package-verification` on `IP-1021`):** **49 `VERIFIED`, 4 `COMPLETE` (`IP-1223`, `IP-1065`, `IP-1064`, `IP-1131`, awaiting 09), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 55 packages total.** `IP-1021` → `VERIFIED` via [VR-1021](verification/VR-1021-failure-atomic-event-application.md), clean. No package depends on `IP-1021`.
- **Package Status (2026-10-17, run #171, `08-code-implementation` on `IP-1131`):** **48 `VERIFIED`, 5 `COMPLETE` (`IP-1021`, `IP-1223`, `IP-1065`, `IP-1064`, `IP-1131`, awaiting 09), 1 `READY` (`IP-1311`), 1 `BLOCKED` (`IP-1160`) — 55 packages total.**
- **Package Status (2026-10-17, run #170, `08-code-implementation` on `IP-1064`):** **48 `VERIFIED`, 4 `COMPLETE` (`IP-1021`, `IP-1223`, `IP-1065`, `IP-1064`, awaiting 09), 2 `READY` (`IP-1311`, `IP-1131`), 1 `BLOCKED` (`IP-1160`) — 55 packages total.**
- **Package Status (2026-10-17, run #169, `08-code-implementation` on `IP-1065`):** **48 `VERIFIED`, 3 `COMPLETE` (`IP-1021`, `IP-1223`, `IP-1065`, awaiting 09), 3 `READY` (`IP-1311`, `IP-1064`, `IP-1131`), 1 `BLOCKED` (`IP-1160`) — 55 packages total.**
- **Package Status (2026-10-17, run #168, `08-code-implementation` on `IP-1223`):** **48 `VERIFIED`, 2 `COMPLETE` (`IP-1021`, `IP-1223`, awaiting 09), 4 `READY` (`IP-1311`, `IP-1064`, `IP-1065`, `IP-1131`), 1 `BLOCKED` (`IP-1160`) — 55 packages total.** No package depends on `IP-1223`.
- **Package Status (2026-10-17, run #167, `08-code-implementation` on `IP-1021`):** **48 `VERIFIED`, 1 `COMPLETE` (`IP-1021`, awaiting 09), 5 `READY` (`IP-1311`, `IP-1064`, `IP-1065`, `IP-1131`, `IP-1223`), 1 `BLOCKED` (`IP-1160`, authorization) — 55 packages total.** No package depends on `IP-1021`.
- **Package Status (2026-10-17, run #166, `IP-1021`/`IP-1064`/`IP-1065`/`IP-1131`/`IP-1223` added):** **48 `VERIFIED`, 0 `COMPLETE`, 6 `READY` (`IP-1311`, `IP-1021`, `IP-1064`, `IP-1065`, `IP-1131`, `IP-1223`, all pre-authorized), 1 `BLOCKED` (`IP-1160`, authorization) — 55 packages total.**
- **Package Status (2026-10-17, run #158, `IP-1311` added):** **48 `VERIFIED`, 0 `COMPLETE`, 1 `READY` (`IP-1311`, pre-authorized), 1 `BLOCKED` (`IP-1160`, authorization) — 50 packages total.**
- **Package Status (2026-10-17, run #155, `09-package-verification` on `IP-1320`):** **48 `VERIFIED`, 0 `COMPLETE`, 0 `READY`, 1 `BLOCKED` (`IP-1160`, authorization) — 49 packages total.** `IP-1320` → `VERIFIED` via [VR-1320](verification/VR-1320-effect-resource-bounds.md), clean. No package depends on `IP-1320`.
- **Package Status (2026-10-17, run #154, `08-code-implementation` on `IP-1320`):** **47 `VERIFIED`, 1 `COMPLETE` (`IP-1320`, awaiting 09), 0 `READY`, 1 `BLOCKED` (`IP-1160`, authorization) — 49 packages total.** No package depends on `IP-1320`.
- **Package Status (2026-10-17, run #153, `IP-1320` added):** **47 `VERIFIED`, 0 `COMPLETE`, 1 `READY` (`IP-1320`, pre-authorized), 1 `BLOCKED` (`IP-1160`, authorization) — 49 packages total.**
- **Package Status (2026-10-17, `09-package-verification` on `IP-1310`):** **47 `VERIFIED`, 0
  `COMPLETE`, 0 `READY`, 1 `BLOCKED` (`IP-1160`, authorization) — 48 packages total.** `IP-1310`
  verified clean, fresh session, no findings ([VR-1310](verification/VR-1310-load-time-vignette-validation.md)).
  No package depends on `IP-1310`.
- **Package Status (2026-10-17, run #146, `08-code-implementation` on `IP-1310`):** **46 `VERIFIED`, 1 `COMPLETE` (`IP-1310`, awaiting 09), 0 `READY`, 1 `BLOCKED` (`IP-1160`, authorization) — 48 packages total.** No package depends on `IP-1310`.
- **Package Status (2026-10-16, run #145, `IP-1310` added):** **46 `VERIFIED`, 0 `COMPLETE`, 1 `READY` (`IP-1310`, pre-authorized), 1 `BLOCKED` (`IP-1160`, authorization) — 48 packages total.** The earlier counts below are kept as history.
- **Package Status (2026-10-16, `09-package-verification` on `IP-1052`):** **46 `VERIFIED`, 0
  `COMPLETE`, 0 `READY`, 1 `BLOCKED` (`IP-1160`, authorization) — 47 packages total.** `IP-1052`
  reached `VERIFIED` this pass ([VR-1052](verification/VR-1052-order-param-hardening.md), clean).
  No package depends on `IP-1052`.
- **Package Status (2026-10-16, run #137, `08-code-implementation` on `IP-1052`):** **45 `VERIFIED`, 1 `COMPLETE` (`IP-1052`, awaiting 09), 0 `READY`, 1 `BLOCKED` (`IP-1160`, authorization) — 47 packages total.** No package depends on `IP-1052`.
- **Package Status (2026-10-16, run #136, `IP-1052` added):** **45 `VERIFIED`, 0 `COMPLETE`, 1 `READY` (`IP-1052`, pre-authorized), 1 `BLOCKED` (`IP-1160`, authorization) — 47 packages total.** The earlier counts below are kept as history.
- **Package Status (2026-10-16, `09-package-verification` on `IP-1041`):** **45 `VERIFIED`, 0
  `COMPLETE`, 0 `READY`, 1 `BLOCKED` (`IP-1160`, authorization) — 46 packages total.** `IP-1041`
  reached `VERIFIED` this pass ([VR-1041](verification/VR-1041-observe-order-reason-and-param-remediation.md),
  clean). No package depends on `IP-1041`; no downstream blocking note changes. The earlier counts
  below are kept as history.
- **Package Status (2026-10-16, run #132, `IP-1041` added; `IP-1171` row corrected):** **44 `VERIFIED`, 0 `COMPLETE`, 1 `READY` (`IP-1041`, pre-authorized), 1 `BLOCKED` (`IP-1160`, authorization) — 46 packages total.** Counted from the status table. The run #94 and 2026-10-10 counts below carried `IP-1171` as `COMPLETE`; it had been `VERIFIED` since 2026-07-12 (`VR-1171`, `BL-0218`). Packages added since the 2026-10-10 count (`IP-1261`, `IP-1262`, `IP-1063`, `IP-1212`, `IP-1221`, `IP-1222`) are all `VERIFIED`. The earlier counts below are kept as history.
- **Package Status (2026-10-10, `09-package-verification` on `IP-1260`):** **37 `VERIFIED`
  (`IP-1260` added via [`VR-1260`](verification/VR-1260-telemetry-csv-export.md), fresh session,
  independent of the implementing session), 1 `COMPLETE` (`IP-1171`, unchanged), 0 `READY`, 1
  `BLOCKED` (`IP-1160`, authorization) — 39 packages total.** No package depends on `IP-1260`; no
  downstream blocking note changes. The earlier count below is kept as history.
- **Package Status (2026-10-10, run #94, `IP-1260` implemented):** **36 `VERIFIED`, 2 `COMPLETE` (`IP-1171`, unchanged; `IP-1260`, implemented this run), 0 `READY`, 1 `BLOCKED` (`IP-1160`, authorization) — 39 packages total.** No package depends on `IP-1260`; no downstream blocking note changes.
- **Package Status (2026-10-10, `09-package-verification` on `IP-1211`):** **36 `VERIFIED`
  (`IP-1211` added via [`VR-1211`](verification/VR-1211-quick-tle-export.md), fresh session,
  independent of the implementing session), 1 `COMPLETE` (`IP-1171`, unchanged), 1 `READY`
  (`IP-1260`), 1 `BLOCKED` (`IP-1160`, authorization) — 39 packages total.** No package depends on
  `IP-1211`; no downstream blocking note changes. The earlier counts below are kept as history.
- **Package Status (2026-10-10, run #92, `IP-1211` implemented):** **35 `VERIFIED`, 2 `COMPLETE` (`IP-1171`, unchanged; `IP-1211`, implemented this run), 1 `READY` (`IP-1260`), 1 `BLOCKED` (`IP-1160`, authorization) — 39 packages total.** No package depends on `IP-1211`; no downstream blocking note changes.
- **Package Status (2026-10-10, run #91, `IP-1211` added):** **35 `VERIFIED`, 1 `COMPLETE` (`IP-1171`, unchanged), 2 `READY` (`IP-1260`, authorized; `IP-1211`, newly added, pre-authorized by the project owner for the `BL-0109`/`FR-7440` package(s) (MSTR-006 §3, relayed in the 2026-10-10 session task instruction; covers this package only)), 1 `BLOCKED` (`IP-1160`, authorization) — 39 packages total.** The earlier count below is kept as history.
- **Package Status (2026-10-10, `09-package-verification` on `IP-1300`):** **35 `VERIFIED`
  (`IP-1300` added via [`VR-1300`](verification/VR-1300-ric-frame-view-and-cats-overlay.md),
  clean with 2 Low findings — `BL-0158` adjudicated `DONE`), 1 `COMPLETE` (`IP-1171`, unchanged),
  1 `READY` (`IP-1260`), 1 `BLOCKED` (`IP-1160`, authorization) — 38 packages total.** No package
  depended on `IP-1300`; no downstream blocking note changes.
  The earlier count below is kept as history.
- **Package Status (2026-10-10, run #88, `IP-1300` implemented):** **34 `VERIFIED`, 2 `COMPLETE`
  (`IP-1171`, unchanged; `IP-1300`, implemented this run under the project owner's 2026-10-10
  MSTR-006 §3 authorization — awaiting `09-package-verification`), 1 `READY` (`IP-1260`), 1
  `BLOCKED` (`IP-1160`, authorization) — 38 packages total.** No package depended on `IP-1300`;
  no downstream blocking note changes.

  The earlier count below is kept as history.
- **Package Status (2026-10-03, run #86, `IP-1300` added):** **34 `VERIFIED`, 1 `COMPLETE`
  (`IP-1171`, awaiting `09-package-verification` same as before), 2 `READY` (`IP-1260`, unblocked
  since run #81; `IP-1300`, newly added this run), 1 `BLOCKED` (`IP-1160`, authorization) — 38
  packages total. `IP-1300` is not authorized for coding (MSTR-006 §3) — a separate, explicit
  project-owner decision not given as part of this planning pass. This bullet does not re-verify
  every package between run #55 and here; it is a fresh count against the current table above,
  consistent with — not a correction of — the intervening bullets' own history.

  The earlier count below is kept as history.
- **Package Status (2026-09-26, run #55, post-`IP-1174` implementation):** **22 `VERIFIED`, 2 `COMPLETE`, 0 `READY`, 1 `BLOCKED`** — `IP-1061` and `IP-1174` are both `COMPLETE`, each awaiting its own `09-package-verification` pass (independently, in fresh sessions relative to their own implementation). `IP-1160` remains the sole `BLOCKED` package (authorization). *Superseded counts, preserved:* run #54 (`IP-1174` newly implemented): 22/1/1/1; run #53 (`IP-1061` newly `READY`): 22/0/2/1; pre-run-#53: 22/0/1/1 (`IP-1174` — every
  dependency now `VERIFIED`, `READY` for `08-code-implementation`; `IP-1160` — every dependency
  already `VERIFIED`, authorization is the sole remaining gate, still not on record). The 22
  `VERIFIED` packages are the original 11 as-built + `IP-1150` + `IP-1140` + `IP-2010` + `IP-3010` +
  `IP-1120` + `IP-1130` + `IP-1151` + `IP-1170` + `IP-1172` + `IP-1173` + `IP-1171`, the last ten
  verified 2026-07-03 through 2026-07-12 via `VR-1140`/`VR-2010`/`VR-3010`/`VR-1120`/`VR-1130`/
  `VR-1151`/`VR-1170`/`VR-1172`/`VR-1173`/`VR-1171`. 0 `NOT STARTED`, 0 `IN PROGRESS`. The "iterate
  through all `09-package-verification`" sweep (runs #11–#15) closed 18 packages; `IP-1170` (run
  #48), `IP-1172`/`IP-1173` (2026-07-11), and `IP-1171` (2026-07-12) brought all five of Tranche 3's
  prerequisite packages to `VERIFIED`. `IP-1174` is now `READY`; `IP-1160` remains `BLOCKED` on
  authorization alone.

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
