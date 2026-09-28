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
| [IP-1171](packages/IP-1171-typed-payload-bus-parameters.md) | FS-117 §FR-5170/FR-5180 Typed Payload & Bus Parameter Domain Model | Forward design | 🔵 COMPLETE | Implemented 2026-07-11 by `08-code-implementation` — 8 new typed `PayloadState` sub-models (`bus.py`), auto-populated per `type`, R109/R110/R129/R134-grounded; `FR-5180`'s bus power/propulsion authoring confirmed to already route through `Asset.model_validate()`, no loader change needed. 12 new tests, full suite 598 passed/3 skipped, both permanent gates green. Awaiting `09-package-verification` |
| [IP-1172](packages/IP-1172-per-cell-roe-enforcement.md) | FS-117 §FR-3420/NFR-2010 Per-Cell Rules of Engagement Enforcement | Forward design | ✅ VERIFIED | **Verified 2026-07-11 (fresh session)**, [`VR-1172`](verification/VR-1172-per-cell-roe-enforcement.md) — full suite 586 passed/3 skipped, both permanent gates green; both `_validate()` check sites independently confirmed to resolve per `order.cell` with zero legacy-shape branching inside `engine/`. Zero findings |
| [IP-1173](packages/IP-1173-vignette-creator-draft-session.md) | FS-117 §FR-5110 Vignette Creator Draft Session & Reverse Serialization | Forward design | ✅ VERIFIED | **Verified 2026-07-11 (fresh session)**, [`VR-1173`](verification/VR-1173-vignette-creator-draft-session.md) — full suite 586 passed/3 skipped, both permanent gates green; sole-writer-to-`VIGNETTE_DIR` and draft-session time-control rejection independently confirmed; independent manual round-trip beyond the existing tests. Zero findings |
| [IP-1174](packages/IP-1174-vignette-creator-ui-surfaces.md) | FS-117 §FR-5120-FR-5160 Vignette Creator UI Surfaces | Forward design | 🔵 COMPLETE | **Remediated 2026-09-27/28** against [`VR-1174`](verification/VR-1174-vignette-creator-ui-surfaces.md)'s High + 2 Medium findings (authorized 2026-09-27, MSTR-006 §3, project owner's direct instruction): `declare_seats` (`FR-5160`) now takes caller identity as the `cell` query param (the convention every other mutating route uses), leaving the body's `cell` as the pure target cell — Blue/Red seat declaration works; `creator.js`'s matrix `roles/assign` call now sends literal `"white"` caller identity instead of the assigned seat's own cell prefix. `force/ground`'s `Asset(...)` validation error now returns `Ack(ok=False, ...)` instead of an unhandled 500 (`BL-0124`); `GroundAssetRequest.owner` is `Literal["blue","red","neutral"]` with `lat_deg`/`lon_deg` range validators (`BL-0125`). This package's own stale `build_scene(world, cell)` prose corrected in place (`BL-0127`). `test_seat_declaration_rejects_non_white_cell` inverted (`test_seat_declaration_rejects_non_white_caller`) + a new allow-non-white-target-cell test added. Full suite green (both permanent gates included). *Prior state:* **RETURNED 2026-09-27 by `VR-1174`** — one failed check (High H1) plus 2 Medium/2 Low findings; `FR-5120`–`FR-5150` confirmed working then. Originally implemented 2026-09-26 (same day as `IP-1061`, a fresh session per the tranche's own eligibility filter — `IP-1061`'s COMPLETE state has no dependency edge to this package). Awaiting a fresh `09-package-verification` pass (new session, per same-session-verification-exclusion).
| [IP-1061](packages/IP-1061-inject-and-sizing-defect-remediation.md) | FS-106 §FR-4410 + NFR-1300 (ADR-0019) Inject Scheduling & Sizing-Cap Defect Remediation | Remediation (forward design) | ✅ VERIFIED | **Verified 2026-09-27 (fresh agent context)**, [`VR-1061`](verification/VR-1061-inject-and-sizing-defect-remediation.md) — full suite 707 passed/3 skipped, both permanent gates green. A1 (0 s inject fires once, no rewind double-fire or loss), A3 (single validating `space_weather` branch), A2 (comment) and A4 (caps removed) independently re-derived with a probe script beyond the package's own tests. 3 Low findings: checklist grep literal, DoD test-count wording, and the pre-existing `NFR-1300` RTM column-shape defect class. Implemented 2026-09-26; closes backlog `BL-0062`–`BL-0065`. |
| [IP-1180](packages/IP-1180-external-vignette-directories.md) | FS-118 External Vignette Directories & Safe Scenario Save Target (`BL-0082`, item B16) | Forward design | ✅ VERIFIED | **Verified 2026-09-27 (fresh agent context)**, [`VR-1180`](verification/VR-1180-external-vignette-directories.md). Full suite 707 passed/3 skipped, both permanent gates green. Built-in-wins collision, external-versus-external ordering, missing-directory skip, the retargeted save, and a single shared traversal guard were all confirmed with hand-built temporary-directory fixtures. 1 Low finding: a saved vignette is not loadable unless `user_save_dir` is also listed in `external_vignette_dirs`, and the config example does not say so. *Prior state:* implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3): new `ContentConfig`/`load_content_config()` (`config.py`); `content/vignette.py`'s `list_vignettes()`/`load_vignette()` extended to enumerate/search configured external directories (built-in-wins collision rule, unreadable-directory skip, both logged), traversal guard extracted into shared `_validate_id`/`_resolve_within_root` helpers; `content/vignette_export.py::save_vignette()` retargeted to a configured `user_save_dir`, raising when unconfigured. 23 new tests (`test_config.py`, `test_content.py`, new `test_vignette_export.py`), 3 existing save-as-vignette tests updated to configure a `tmp_path` `user_save_dir` fixture (regression, not rewrite). Full suite 661 passed/3 skipped (up from 638/3), both permanent gates green. Resolves `BL-0094`'s remaining three Design-Decision-based Open Questions in full. Awaiting `09-package-verification` in a fresh session. |
| [IP-1062](packages/IP-1062-condition-triggered-injects-and-new-effects.md) | FS-106 v2.1 Condition-Triggered Injects & New Inject Effect Types (`BL-0070`, item B4) | Forward design | 🟠 IN PROGRESS | **RETURNED 2026-09-27 by [`VR-1062`](verification/VR-1062-condition-triggered-injects-and-new-effects.md)**. One failed check (High H1): the `anomaly` effect with `subsystem: "bus"` sets `bus_state.mode = "safe_mode"` directly instead of calling `engine/bus.py::enter_safe_mode()`. `safe_mode.active` stays `False` and no cause is recorded, so the recovery strip shows safe mode while `begin_recovery` refuses with `not_safed` and the `asset_safed` metric reads `False`. Design Decision 4's promised reuse of the recovery loop is not delivered. Also 1 Medium (a malformed effect payload raises mid-handler and leaves an unlogged partial mutation) and 4 Low. `FR-4420` (the condition trigger, including replay and rewinds) was independently confirmed sound. **Remediation authorized 2026-09-27 (MSTR-006 §3, project owner's direct instruction).** Next: `08-code-implementation` re-run. *Prior state:* implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3): a new periodic `condition_check` event (`_h_condition_check`) evaluates condition-triggered injects against replayed `WorldState`, firing-state derived from a time-filtered eventlog scan (no new `WorldState` field, no mid-handler `eventlog.append`); `_h_inject`'s body extracted into a shared `_apply_inject_effects` helper, gaining four new branches (`anomaly`, `sensor_outage`, `forced_custody_loss`, `scripted_manoeuvre`); new `Sensor.health` field + `scene_from_world()` filter. 17 new tests (`test_condition_triggered_injects.py`, `test_inject_effects_v2.py`), zero changes needed to `test_inject_library.py`'s existing suite beyond its own documentation set. Full suite 678 passed/3 skipped (up from 661/3), both permanent gates green. Resolves `BL-0091`/`BL-0095` in full. Awaiting `09-package-verification` in a fresh session. |
| [IP-1200](packages/IP-1200-save-as-scenario.md) | FS-120 Save-as-Scenario (`BL-0071`, item B5) | Forward design | ✅ VERIFIED | **Verified 2026-09-27 (fresh agent context, after `IP-1180`)**, [`VR-1200`](verification/VR-1200-save-as-scenario.md). Full suite 707 passed/3 skipped, both permanent gates green. The independent round trip started `leo-isr-denial`, created a track, a bus anomaly, severe space weather and a Δv change, then saved as a scenario and reloaded. Start epoch equalled T, the tracks were identical, and all 6 assets were `model_dump()`-identical. 2 Low findings: the package's "byte-identical" checklist wording contradicts its own always-stamp-version design, and there is no browser GUI control. *Prior state:* implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3; built against `IP-1180`'s actual landed diff, per the coordination note): `export_vignette()`/`save_vignette()` gain an optional `start_epoch` parameter (defaults preserve `IP-1173`'s exact prior behavior); three new additive `Vignette` fields (`initial_tracks`, `simulator_version`, `initial_space_weather`) carried forward and consumed by `build_world()`; new `spacesim/version.py::simulator_version()` (git short hash, package-version fallback); new `SessionManager.save_as_scenario()` requiring `self.started`; `InProcessSession.save_vignette(..., as_scenario=...)` and `SaveVignetteRequest.as_scenario` wire it through the existing route (no new route). 11 new tests, full suite 689 passed/3 skipped (up from 678/3), both permanent gates green. Resolves `BL-0097` in full. Awaiting `09-package-verification` in a fresh session. |
| [IP-1190](packages/IP-1190-bulk-tle-omm-import.md) | FS-119 Bulk TLE and CCSDS OMM Multi-Object Import (`BL-0067`, item B1) | Forward design | ✅ VERIFIED | **Verified 2026-09-27 (fresh agent context)**, [`VR-1190`](verification/VR-1190-bulk-tle-omm-import.md). Full suite 707 passed/3 skipped, both permanent gates green. Every DoD and Acceptance Criterion was confirmed. `mean_to_true()` was checked against a hand-computed Kepler solution, and the reject-versus-per-object-failure split was tested with hand-built fixtures. 2 Medium findings: the OMM `EPOCH` is discarded on the false premise that `add_tle` does the same, and an invalid assignment owner/kind aborts the batch with HTTP 500. 2 Low. *Prior state:* implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3): new `content/bulk_import.py` (`parse_multi_tle`/`parse_ccsds_omm`, KVN only), new public `engine/orbit.py::mean_to_true()` extracted with zero behavior change to `elements_to_rv()`, `_force_add_tle_object`/`_force_add_omm_object`/`bulk_import()` on `SessionManager`, new `POST /api/sessions/{sid}/force/bulk_import` route (+ `InProcessSession.bulk_import()` plumbing, implied by the route but not separately named in the package's own Files to Modify). 16 new tests (`test_bulk_import.py`, `test_bulk_import_session.py`, 2 in `test_orbit.py`, 1 in `test_web.py`, 1 new Observer-guard entry), full suite 638 passed/3 skipped (up from 622/3), both permanent gates green. Resolves `BL-0096` in full. Awaiting `09-package-verification` in a fresh session. |
| [IP-1210](packages/IP-1210-ephemeris-export.md) | FS-121/FS-103 v1.1 Ephemeris Export (`BL-0069`, items B2/B3) | Forward design | 🟠 IN PROGRESS | **RETURNED 2026-09-27 by [`VR-1210`](verification/VR-1210-ephemeris-export.md)**. One failed check (High H1): `to_ric()` projects the inertial relative velocity onto the RIC axes without the rotating-frame `ω×ρ` term. A co-orbital neighbour whose RIC position is constant reports `ric_v` = −13.29 m/s radial, which is exactly n·ρ, and no test checks `ric_v`. The fault affects both the truth and cell-observed CSV. Also 2 Medium: the OEM is non-conformant (empty `META_START`/`STOP` with metadata outside, no `CREATION_DATE`/`ORIGINATOR`/`START_TIME`/`STOP_TIME`, `+00:00` epochs, `EME2000` mislabel), and the OEM has no RIC although the AC requires it. And 2 Low. ECI, RIC position, fog-of-war, range clamp/reject and determinism were independently confirmed. **Remediation authorized 2026-09-27 (MSTR-006 §3, project owner's direct instruction) — fix the RIC velocity to true rotating-frame velocity (subtract ω×ρ), and add a companion RIC-specific export file per the owner's resolution of `BL-0136`'s FR-7410/OEM tension (see the forthcoming `04` amendment).** Next: `08-code-implementation` re-run. *Prior state:* implemented 2026-09-27 by `08-code-implementation` (authorized the same day, MSTR-006 §3): new `session/ephemeris.py` (`sample_times`/`truth_ephemeris`/`cell_observed_ephemeris`/`to_ric`/`write_csv`/`write_oem`) built on a new additive `aar.state_at_time(mgr, t)` sibling of `state_at(mgr, seq)`; `engine/maneuver.py::lvlh_frame` reused unmodified for the RIC transform; two new HTTP routes (`GET .../ephemeris/truth` no-cell, `GET .../ephemeris/{cell}` cell-scoped). 18 new tests (`test_ephemeris.py`, +1 in `test_aar.py`, +4 in `test_web.py`), full suite 707 passed/3 skipped (up from 689/3), both permanent gates green. Resolves `BL-0098` in full. Awaiting `09-package-verification` in a fresh session. **This closes the five-package authorized-implementation tranche for this increment** (`IP-1180`/`IP-1062`/`IP-1200`/`IP-1190`/`IP-1210` — every one now `COMPLETE`). |
| [IP-1220](packages/IP-1220-sensor-modality-models.md) | FS-122 Sensor Modality Models (`BL-0073`/`BL-0083`, items B7/B17) | Forward design | 🟡 READY | **Authorized 2026-09-27 (MSTR-006 §3, project owner's direct instruction).** Every dependency (`IP-1010`/`1020`/`1030`/`1040`/`1050`/`1051`, all engine core) already `VERIFIED` — specification-complete, would flip to eligible-for-`08` the moment authorization is granted. |
| [IP-1240](packages/IP-1240-debris-field-persistence-estimate.md) | FS-124 Debris-Field Persistence Estimate by Altitude (`BL-0077`, item B11) | Forward design | 🟡 READY | **Authorized 2026-09-27 (MSTR-006 §3, project owner's direct instruction).** Dependency (`IP-1051`) `VERIFIED`. |
| [IP-1250](packages/IP-1250-maneuver-ledger.md) | FS-125 Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export (`BL-0072`, item B6) | Forward design | 🟡 READY | **Authorized 2026-09-27 (MSTR-006 §3, project owner's direct instruction).** Dependency (`IP-1010`) `VERIFIED`. |
| [IP-1260](packages/IP-1260-telemetry-csv-export.md) | FS-126 Per-Asset Telemetry CSV Export Over a Time Span (`BL-0075`, item B9) | Forward design | 🔴 BLOCKED | Not an authorization block. This package's own Acceptance Criterion 1 requires `IP-1062`'s `anomaly` effect. `IP-1062` was **RETURNED** by [`VR-1062`](verification/VR-1062-condition-triggered-injects-and-new-effects.md) (2026-09-27), and its High finding is in that same `anomaly` effect, so the blocker has not cleared. Per this skill's own eligibility rule, a dependency merely `COMPLETE` keeps a package `BLOCKED`, not `READY`. |
| [IP-1270](packages/IP-1270-effect-authorization-gating-and-live-roe.md) | FS-127 Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes (`BL-0076`, item B10) | Forward design | 🟡 READY | **Authorized 2026-09-27 (MSTR-006 §3, project owner's direct instruction).** Dependencies (`IP-1172`, `IP-1151`, core `eventlog.py`) `VERIFIED`. **Resolves the effect-classification enumeration `IP-1290` must reuse (`BL-0105`) — should be sequenced before or closely coordinated with `IP-1290`.** |
| [IP-1280](packages/IP-1280-variable-speed-aar-replay.md) | FS-128 Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint (`BL-0078`, item B12) | Forward design | 🟡 READY | **Authorized 2026-09-27 (MSTR-006 §3, project owner's direct instruction).** Dependency (`IP-1070`) `VERIFIED`. |
| [IP-1290](packages/IP-1290-jamming-delivery-and-effect-detectability.md) | FS-129 Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings (`BL-0081`, item B15) | Forward design | 🟡 READY | **Authorized 2026-09-27 (MSTR-006 §3, project owner's direct instruction).** Dependencies (`IP-1051`, `IP-1010`/`1020`) `VERIFIED`. **Must be sequenced after (or closely coordinated with) `IP-1270`, whose landed effect-classification schema this package's own configuration parsing must match exactly (`BL-0105`).** |

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
