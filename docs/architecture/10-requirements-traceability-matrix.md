# GDS-10 — Requirements Traceability Matrix

> **Document ID:** GDS-10
> **Version:** 1.1 (2026-10-23, run #217: §4–§5 refreshed for the run #211 leaves, `BL-0311` R9). v1.0: run #204.
> **Status:** ✅ Authored — merge gate closed (see "Merge gate" below)
> **Dependencies:** GDS-09
> **Referenced By:** — (terminal level of the ladder)
> **Produces:** —
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [GDS-05](05-functional-requirements.md) and [GDS-06](06-non-functional-requirements.md)
> (the requirement tags traced here), [`requirements/03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md)
> (the leaf-level matrix — companion, see below), [`implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> (package status), [`implementation/packages/`](../implementation/packages/INDEX.md),
> [`features/feature-index.md`](../features/feature-index.md), `spacesim/tests/`.

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

Show, for every requirement the ladder states, the chain from requirement to the feature that
specified it, the package that built it, its verification status and the tests that hold it — and
show plainly where that chain breaks. This is the ladder's last level: GDS-05 and GDS-06 say what
must be true; this level says how we know.

## Relationship to the other traceability artifacts

| Artifact | Grain | Role |
|---|---|---|
| `ROADMAP.md`, `MSTR-005` §4 | Document | Track which documents exist and whether the document chain (domain → spec → package) is complete. They never relate an individual requirement ID to an individual test. |
| `requirements/03-requirements-traceability-matrix.md` | Leaf (`FR-1110`, `NFR-1500`) | **Authoritative for leaf-level traces**: each leaf's research source, ADR, component, interface, future feature, test and package. Owned by `04`. |
| **GDS-10 (this document)** | Tag (`FR-E1`, `NFR-3`) → leaf → feature → package → test | **Authoritative for chain completeness at the ladder's grain**: does every GDS-05/06 statement reach verified code and a test? Where not, why? |

The two matrices disagree in one place, recorded as a finding for `04` (§6, F2): the leaf matrix's
requirement-to-test index has three entries and says no feature or package convention exists, but
59 packages now name the requirements they cover and the tests they add.

## 1. The ladder itself

Each level absorbed the document named and was gated on the one before:

| Level | Absorbed | State |
|---|---|---|
| GDS-00 Vision | MSTR-001 (stays authoritative) | ✅ |
| GDS-01 Concept of Operations | build-spec/01, /04 §11, /05 §13–14, training/05, /07 | ✅ |
| GDS-02 System Context | build-spec/01 | ✅ |
| GDS-03 Architecture | design/01 | ✅ |
| GDS-04 Domain Model | design/04 (conceptual half) | ✅ |
| GDS-05 Functional Requirements | build-spec/02 §5–6 (superseded) | ✅ |
| GDS-06 Non-functional Requirements | build-spec/04 §9 (superseded); DOM-005, -007, -008 content | ✅ |
| GDS-07 Data Model | design/04 (schema half; superseded); DOM-002, -004 content | ✅ |
| GDS-08 UI Architecture | design/09, /05, /10 (superseded); build-spec/07, design/06 UI content | ✅ |
| GDS-09 API Specification | design/07 (superseded); ICD kept as companion inventory | ✅ |
| GDS-10 Traceability (this) | Net-new at tag grain; companion of `requirements/03` | ✅ |

## 2. Method

The functional table (§4) was **generated, not hand-assembled**, on 2026-10-22, from four sources
read as they stand in the tree:

1. **Tag → leaf:** each GDS-05 tag's own cross-reference line (`→ FR-xxxx`).
2. **Leaf → package:** each package's "Requirements Covered" section (`docs/implementation/packages/IP-*.md`).
3. **Package → feature and status:** the package's header (feature reference) and the Master Build
   Plan's status column — the ledger, not the package file's own banner, which can lag.
4. **Package → tests:** test files the package's "Tests to Add", "Definition of Done" or
   "Verification Checklist" sections name **and that exist** in `spacesim/tests/`. Where a package
   named a file as one option ("`test_sun.py` or a new `test_cats_angle.py`"), only the file that
   exists is listed.

**Test attribution is package-grain.** A test listed against a tag belongs to a package that covers
one of the tag's leaves; it is not proof that the test asserts that particular leaf. No test file
cites a requirement ID, so leaf-grain test attribution is not derivable from the tree today (F3).

The non-functional table (§5) is **curated**: most quality attributes are enforced by standing
tests and invariants rather than by a feature package, so its test column was found by searching
the suite for each attribute's mechanism.

## 3. Permanent gates (apply to every requirement)

- `spacesim/tests/test_determinism.py` — the Phase-1 determinism property (GDS-06 NFR-3).
- `spacesim/tests/test_import_guard.py` — engine import, wall-clock and RNG guards (NFR-7).
- The full suite, green before every commit (NFR-7, `NFR-2800`).

Nearly every package names the two gate files; they are left out of the tables below so the
columns show what is specific to each requirement.

## 4. Functional requirements (GDS-05 tags)

Package column: verified packages, then any that are not yet verified, with their ledger status.

| Tag | Leaves (`requirements/01`) | Feature specs | Packages | Tests (package-grain, gates excluded) |
|---|---|---|---|---|
| FR-E1 | FR-1110, FR-1130 | FS-102 | IP-1020 | — |
| FR-E2 | FR-1120 | FS-102, FS-107, FS-301 | IP-1021, IP-1070, IP-3010 | `test_failure_atomic_events.py`, `test_research_batch.py` |
| FR-E3 | FR-1210 | — | — | — |
| FR-E4 | FR-1220 | FS-101, FS-102, FS-122 | IP-1010, IP-1020, IP-1221 +1 | `test_cats_angle.py`, `test_isr.py`, `test_orders.py` +2 |
| FR-E5 | FR-1310 | FS-101, FS-102, FS-105 | IP-1010, IP-1052 | `test_bus_commands.py`, `test_derived_probabilities.py`, `test_jam.py` +7 |
| FR-E6 | FR-1410 | FS-102, FS-105, FS-129 | IP-1051, IP-1052, IP-1290 | `test_bus_commands.py`, `test_derived_probabilities.py`, `test_effects.py` +8 |
| FR-E7 | FR-1510, FR-1520 | FS-103, FS-104, FS-105 +1 | IP-1030, IP-1040, IP-1051 +1 | `test_assessment.py`, `test_custody.py`, `test_orders.py` +1 |
| FR-E8 | FR-1420 | FS-102, FS-105 | IP-1020, IP-1051, IP-1052 | `test_bus_commands.py`, `test_derived_probabilities.py`, `test_jam.py` +7 |
| FR-B1 | FR-2110 | FS-105 | IP-1050 | — |
| FR-B2 | FR-2210 | FS-105 | IP-1050 | — |
| FR-B3 | FR-2310 | FS-121, FS-126 | IP-1261 | `test_aar.py`, `test_effects.py`, `test_ephemeris.py` +3 |
| FR-B4 | FR-2410 | FS-105 | IP-1050 | — |
| FR-B5 | FR-2510 | FS-105 | IP-1050 | — |
| FR-P1 | FR-3110, FR-3120 | FS-101, FS-102, FS-105 | IP-1010, IP-1020, IP-1052 | `test_bus_commands.py`, `test_derived_probabilities.py`, `test_jam.py` +7 |
| FR-P2 | FR-3210, FR-3220 | FS-102, FS-104, FS-105 +1 | IP-1040, IP-1041, IP-1052 | `test_bus_commands.py`, `test_derived_probabilities.py`, `test_jam.py` +9 |
| FR-P3 | FR-3310 | FS-102, FS-106, FS-113 +4 | IP-1065, IP-1131 | `test_bulk_import_session.py`, `test_cell_activity.py`, `test_training_sources.py` +1 |
| FR-P4 | FR-3410 | FS-101, FS-102, FS-104 +4 | IP-1010, IP-1020, IP-1041 +5 | `test_assessment.py`, `test_bus_commands.py`, `test_derived_probabilities.py` +10 |
| FR-P5 | FR-3510 | FS-116 | —; IP-1160 (blocked) | `test_bus_commands.py`, `test_content.py`, `test_vignette_tutorials.py` |
| FR-P6 | FR-1310, FR-3110 | FS-101, FS-102, FS-105 | IP-1010, IP-1020, IP-1052 | `test_bus_commands.py`, `test_derived_probabilities.py`, `test_jam.py` +7 |
| FR-W1 | FR-4110 | FS-115 | IP-1150 | `test_content.py`, `test_web.py` |
| FR-W2 | FR-4210 | FS-102, FS-105, FS-113 +1 | IP-1131, IP-1151 | `test_content.py`, `test_session_setup.py`, `test_training_sources.py` +1 |
| FR-W3 | FR-4310, FR-4320 | FS-106, FS-108 | IP-1060, IP-1068, IP-1072, IP-1073, IP-1074, IP-1075, IP-1076 (all `VERIFIED`; `FR-4310` met since `IP-1068`, `FR-4320` as extended since `IP-1072`; the related leaves `FR-4330` and `FR-7340` are built by `IP-1074`–`IP-1076` and `IP-1077`) | `test_session.py`, `test_white_only_controls.py`, `test_browser_console_rules.py` +4 |
| FR-W4 | FR-4410 | FS-102, FS-106, FS-108 +4 | IP-1060, IP-1061, IP-1063 +2 | `test_bulk_import_session.py`, `test_cell_activity.py`, `test_content.py` +5 |
| FR-W5 | FR-4510 | FS-112 | IP-1120 | `test_classification_banner.py`, `test_content.py` |
| FR-W6 | FR-4610 | FS-106, FS-108 | IP-1060 | `test_session.py` |
| FR-W7 | FR-4710, FR-4720 | FS-106, FS-108, FS-201 | IP-1060, IP-2010 | `test_assessment.py`, `test_orders.py`, `test_session.py` |
| FR-S1 | FR-5110 | FS-109, FS-110, FS-117 | IP-1173 | `test_session.py`, `test_session_features.py`, `test_vignette_creator_session.py` +1 |
| FR-S2 | FR-5210 | — | — | — |
| FR-S3 | FR-5310, FR-5311, FR-5314 | FS-123, FS-131 | IP-1230, IP-1310; IP-1311 (ready) | `test_defensive_audit_2026.py`, `test_space_weather_index.py`, `test_vignette_library.py` +1 |
| FR-L1 | FR-7110 | — | — | — |
| FR-L2 | FR-7110, FR-7320 | FS-107 | IP-1070 | — |
| FR-E9 | FR-1230, FR-4440 | FS-123 | IP-1230 | `test_space_weather_index.py` |
| FR-E10 | FR-1320 | FS-125 | IP-1250 | `test_orders.py`, `test_session_features.py`, `test_web.py` |
| FR-E11 | FR-1430 | FS-124 | IP-1240 | `test_effects.py` |
| FR-E12 | FR-1440, FR-1450 | FS-129 | IP-1290 | `test_effects.py`, `test_orders.py` |
| FR-E13 | FR-1460, FR-1470 | FS-132 | IP-1320, IP-1321 | `test_effect_resource_bounds.py`, `test_orders.py` |
| FR-E14 | FR-1610, FR-1670 | FS-104, FS-122 | IP-1041, IP-1220, IP-1221 +2 | `test_access.py`, `test_beam_mode_modality.py`, `test_cats_angle.py` +9 |
| FR-B6 | FR-5170, FR-5180 | FS-105, FS-117 | IP-1170, IP-1171 | `test_isr.py`, `test_typed_payload_params.py` |
| FR-B7 | FR-2320 | FS-121, FS-126 | IP-1260, IP-1261, IP-1262 | `test_aar.py`, `test_effects.py`, `test_ephemeris.py` +4 |
| FR-P7 | FR-3420, FR-3430, FR-3440 | FS-101, FS-102, FS-117 +2 | IP-1172, IP-1270 | `test_content.py`, `test_orders.py`, `test_session_features.py` +1 |
| FR-P8 | FR-3520 | FS-116 | —; IP-1160 (blocked) | `test_bus_commands.py`, `test_content.py`, `test_vignette_tutorials.py` |
| FR-W8 | FR-4420, FR-4430, FR-4450 | FS-106, FS-123 | IP-1062, IP-1063, IP-1064 +2 | `test_condition_triggered_injects.py`, `test_content.py`, `test_inject_effects_v2.py` +4 |
| FR-W9 | FR-4620 | FS-106 | IP-1066, IP-1067 | `test_pending_inject_queue.py` |
| FR-S4 | FR-5120, FR-5160 | FS-115, FS-117 | IP-1174 | `test_vignette_creator_ui.py` |
| FR-S5 | FR-5220 | FS-102, FS-106, FS-118 +2 | IP-1065, IP-1190 | `test_bulk_import.py`, `test_bulk_import_session.py`, `test_cell_activity.py` +4 |
| FR-S6 | FR-5410, FR-5420 | FS-102, FS-106, FS-117 +3 | IP-1065, IP-1180 | `test_bulk_import_session.py`, `test_cell_activity.py`, `test_config.py` +4 |
| FR-S7 | FR-5510 | FS-102, FS-106, FS-118 +2 | IP-1065, IP-1200 | `test_bulk_import_session.py`, `test_cell_activity.py`, `test_content.py` +5 |
| FR-L3 | FR-7210, FR-7220, FR-7230 | FS-106, FS-110 | IP-1100, IP-1101, IP-1102, IP-1103 (all `VERIFIED`), IP-1094 (`COMPLETE`, format gate; `FR-7220` and `FR-7230` met) | `test_session.py`, `test_save_load_robustness.py` +2 |
| FR-L4 | FR-7310, FR-7330 | FS-107, FS-128, FS-201 | IP-1070, IP-1077, IP-1280, IP-2010 | `test_aar.py`, `test_assessment.py`, `test_orders.py` +1 |
| FR-L5 | FR-7410, FR-7440 | FS-103, FS-106, FS-121 +1 | IP-1210, IP-1211, IP-1212 +2 | `test_aar.py`, `test_effects.py`, `test_ephemeris.py` +5 |
| FR-A1 | FR-10110 | FS-201, FS-301 | IP-2010, IP-3010 | `test_assessment.py`, `test_orders.py`, `test_research_batch.py` |
| FR-A2 | FR-10210 | FS-301 | IP-3010 | `test_research_batch.py` |
| FR-T1 | FR-11110, FR-11120, FR-11210 | — | — | — |
| FR-T2 | FR-11310, FR-11320 | — | — | — |
| FR-T3 | FR-11410, FR-11420 | — | — | — |

## 5. Non-functional requirements (GDS-06 tags)

*Refreshed 2026-10-23 (run #217) for the 19 NFR leaves `04` added in run #211; §4 gains `FR-4320`
(FR-W3) and `FR-7230` (FR-L3), which GDS-05 now tags. Status cells for FR-W3, FR-L3, FR-L4 and the
NFR-2, NFR-7, NFR-9 and NFR-18 rows below were restated 2026-10-24 (stale-documentation pass) to the
shipped and `VERIFIED` packages; the other rows were not re-derived.*

| Tag | Leaves (`requirements/02`) | Enforced by |
|---|---|---|
| NFR-1 Offline runtime | `NFR-3200` | Inspection only (no code makes a network call; the import guard keeps transport out of `engine/`). No test asserts the absence of network access. The Space-Track pull is dropped (`BL-0299`, ADR-0018 revision note). |
| NFR-2 Hardware floor | `NFR-1200`, `NFR-1300` | Demonstration on reference hardware (never recorded). **No test covers the clock-lag watchdog** that `NFR-1300` names as its verification (F1). |
| NFR-3 Determinism | `NFR-1500`, `NFR-2400` | `test_determinism.py` (gate); `test_failure_atomic_events.py` |
| NFR-4 Responsiveness | `NFR-1100`, `NFR-1400` | Lazy-clock and multiplayer tests in `test_web.py`; no latency measurement (GDS-06 OQ4); the ~16-participant ceiling is untested by design (ADR-0026). |
| NFR-5 Security | `NFR-2200`, `NFR-2300`, `NFR-3700`, `NFR-1510` | `test_content.py`, `test_vignette_load_validation.py`, `test_vignette_export.py`, `test_defensive_audit_2026.py` (traversal and validation); `test_observer.py` (Observer rejection); fog: `test_scene.py`, `test_controller_view.py`. |
| NFR-6 Robustness | `NFR-1600`, `NFR-1610` | `test_vignette_load_validation.py`, `test_validate_order.py`, `test_failure_atomic_events.py` (`NFR-1610`); `IP-1311` (ready) extends load validation. |
| NFR-7 Maintainability | `NFR-1900`, `NFR-2000`, `NFR-2010`, `NFR-2100`, `NFR-2800`, `NFR-2820`, `NFR-2830` | `test_import_guard.py` (gate); `test_content.py`, `test_vignette_library.py` (schema additivity); no coverage target (`BL-0299`). Test origins (`NFR-2820`, `NFR-2850`) are built (`IP-1330`–`IP-1335`, `VERIFIED`; every test names its origin and the suite fails on an untagged one); the release audit (`NFR-2830`) rests on the origin report that `IP-1330` built. |
| NFR-8 Portability | `NFR-2900`, `NFR-3300` | Inspection of the dependency list. |
| NFR-9 Usability | `NFR-3000`, `NFR-3010`–`NFR-3060`, `NFR-2840` | Inspection; `test_validate_order.py` (the reason half of `NFR-3020`); `test_browser_console_rules.py` (`NFR-2840`, `IP-1340` `VERIFIED`: fog, plan-first and consequence-confirm rules in headless Chromium, plus the console's handling of server refusals, `IP-1073`/`IP-1076`). The rest of the client is not browser-asserted (GDS-08 OQ1). The `NFR-3030` panel-manager gap is closed (`IP-1069`). |
| NFR-10 Classification | `NFR-3100` | `test_classification_banner.py` |
| NFR-11 Sub-stepped time | `NFR-1700` | `test_clock_and_time.py` |
| NFR-12 Event-log completeness | `NFR-2500`, `NFR-2600` | `test_determinism.py`, `test_aar.py`, `test_failure_atomic_events.py` |
| NFR-13 Replay-safe reads | `NFR-2410` | Per-module tests that a read leaves state unchanged (e.g. `test_bus_commands.py`, `test_effects.py`); no single cross-cutting test. |
| NFR-14 Availability | `NFR-1800` (corrected in run #211) | Save and resume: `test_web.py`, `test_session_features.py`, `test_pending_inject_queue.py`, `test_ssn.py` |
| NFR-15 Bounded resources | `NFR-3710` | `test_ephemeris.py` (`MAX_EXPORT_SAMPLES`), `test_defensive_audit_2026.py` (event-log cap), `test_vignette_creator_session.py` (session cap) |
| NFR-16 Configuration | `NFR-2700` | `test_config.py` |
| NFR-17 Training quality | `NFR-3400`, `NFR-3500`, `NFR-3600` | `test_training_sources.py`, `test_vignette_tutorials.py`, `test_training.py`; human review (`09-training-manual-review`) |
| NFR-18 Documentation integrity | `NFR-3800`–`NFR-3840` | `test_doc_integrity.py` (`NFR-3800`, `NFR-3820`, `NFR-3830`, `IP-1350` `VERIFIED`: links, index completeness, three status-ledger pairs, with shrink-only allow-lists) and `test_test_origins.py` (`NFR-3840`); the `Sources:` footer check (`test_training_sources.py`). `NFR-3810` (retired documents deleted) is not built (`BL-0319`). |
| NFR-19 Model credibility | `NFR-2810` | `test_power_calibration.py` pins one recalibrated model; no comparison tables exist yet. |

## 6. Coverage and findings

*Status note, 2026-10-24: the counts below are the run #217 figures and have not been regenerated;
since then the ledger has moved on (the Master Build Plan's tally is authoritative for package
statuses). The two leaves this section lists as "not met as built" (`FR-4310`, `FR-7220`) are now
met (`IP-1068`, `IP-1101`/`IP-1102`). Regenerating this section is the work of OQ1.*

*Update 2026-10-23 (run #217): the counts below are as of run #204. Run #211 added 2 FR leaves
(106; neither yet has a package) and 19 NFR leaves (47; none has a package — six are already
enforced by existing tests: `NFR-1610`, `NFR-2410`, `NFR-3020`'s reason half, `NFR-3710`,
`NFR-2810`'s one regression pin, and none of the documentation or test-origin leaves). Run #211 also
found two verified leaves not met as built: `FR-4310` (`BL-0307`) and `FR-7220` (`BL-0302`, now
specified in FS-110 v2.0). F3 is decided (leaf-grain origin markers, `BL-0310`, FS-133).*

**Functional (104 leaves).** 90 trace to at least one package. Of the 59 packages, 57 are
`VERIFIED`; the other two cover leaves already traced elsewhere or new scope: `IP-1160`
(`BLOCKED`, awaiting authorization: `FR-3510`/`FR-3520`, role-scoped commands) and `IP-1311`
(`READY`: `FR-5310`, `FR-5311`, `FR-5314`, `NFR-1600`). The 14 untraced leaves fall into three
groups, none of them silent:

- **Built before the package tier existed** (Phases 0–5): `FR-1110` clock, `FR-1210` propagation,
  `FR-3120` cancel before uplink, `FR-6110` all access through `SessionAPI`, `FR-7110` event log,
  `FR-8110` browser presentation layer. Tests exist (`test_clock_and_time.py`, `test_propagator.py`,
  `test_reference_skyfield.py`, `test_queue.py`, `test_import_guard.py`, `test_web.py`) but no
  package or verification report names them.
- **Training corpus** (`FR-11110`, `FR-11120`, `FR-11210`, `FR-11310`, `FR-11320`, `FR-11410`,
  `FR-11420`): verified by `09-training-manual-review` reports, `test_training_sources.py` and
  `test_vignette_tutorials.py`, not by code packages — the expected path for documentation
  artifacts.
- **Not built:** `FR-5210` Space-Track import (GDS-06 correction C2, `BL-0299` OQ3).

**Non-functional (28 leaves).** 15 trace to a package; the other 13 are enforced by standing
invariants, gates and inspection (§5) rather than by a feature.

**Findings** (for `04` unless noted):

- **F1 — The clock-lag watchdog has no test. Closed 2026-10-24:** `IP-1091` (`VERIFIED`) added
  `test_clock_lag_watchdog.py`, which feeds synthetic costs to `SessionManager._record_catch_up_lag`
  and is tagged `NFR-1300`.
- **F2 — `requirements/03` is stale in two places.** Its header says GDS-10 is unauthored, and its
  requirement-to-test and requirement-to-package indexes say no feature or package convention exists;
  59 packages and their verification reports now carry that trace.
- **F3 — No test cites a requirement ID. Closed 2026-10-24:** the owner chose leaf-grain origins
  (`BL-0310`); every test now carries `@pytest.mark.verifies(...)` (`NFR-2820`, `IP-1330`–`IP-1335`)
  and the leaf-grain matrix's Test column is generated from them (`NFR-2850`). This document keeps
  tag-grain attribution; its Test cells name files, not leaves.
- **F4 — Foundational leaves have no package.** The six pre-package leaves above are built and tested
  but not traced; a one-time attribution pass in `requirements/03` closes it (no code needed).
- **F5 — 16 test files are named by no package** (`test_bus.py`, `test_clock_and_time.py`,
  `test_console_small_fixes.py`, `test_controller_view.py`, `test_defensive_modifiers.py`,
  `test_future_work.py`, `test_future_work_batch11.py`, `test_maneuver.py`,
  `test_power_calibration.py`, `test_propagator.py`, `test_recovery.py`, `test_recovery_session.py`,
  `test_reference_skyfield.py`, `test_safe_mode.py`, `test_training.py`, `test_vignettes.py`). Most
  predate the package tier; `test_controller_view.py` and `test_console_small_fixes.py` belong to
  packages whose sections name them differently. Package-grain tracing misses them.
- Gaps G1–G6 (attributes with no leaf) are GDS-06's, already handed to `04` (`BL-0298`).

## 7. Keeping this matrix true

The functional table goes stale the moment a package is verified or a leaf is added. Two rules:

- **Regenerate, don't edit.** The table is produced by reading the four sources in §2; any `03`, `04`,
  `07` or `09` pass that changes them should regenerate it rather than hand-patch rows.
- **Check it mechanically.** "Status ledgers agree" is item 4 of the documentation-integrity suite
  (GDS-06 NFR-18, `BL-0297`). When that suite is built, it should also check that this matrix's
  package statuses match the Master Build Plan.

## Open Questions

- **OQ1 — Make the matrix a generated artifact?** The generator used here is a short read-only
  script. Should it live in `tools/` and be run (or checked) by the documentation-integrity suite,
  so this table cannot drift? That decides whether §4 is maintained by `03` by hand or by tooling
  under `BL-0297`.
- **OQ2 — Leaf-grain test traceability.** Is package-grain attribution enough, or should tests carry
  requirement IDs (F3)? Leaf-grain tracing costs a convention on every test; package-grain costs
  precision.

## Merge gate (closed)

- [x] **Searched for an existing counterpart before authoring, and recorded the result.** The
  scaffold's note ("no existing counterpart") predates `requirements/03-requirements-traceability-matrix.md`,
  which `04` authored afterwards at the owner's request: it **is** a requirement-to-test-to-package
  matrix, but at leaf grain, and its test and package indexes are nearly empty and partly stale
  (F2). `ROADMAP.md` and the `MSTR-005` §4 chain track documents and chain completeness, not
  requirement IDs against test IDs, as the scaffold said. This document therefore does not
  duplicate `requirements/03`: it traces at the ladder's grain and reports chain completeness.
- [x] **Requirement IDs drawn from GDS-05 and GDS-06; feature and test columns from the feature
  specifications, packages and `spacesim/tests/`.** The legacy `IMP-xxx` tier the scaffold
  mentioned is superseded by the `IP-xxxx` packages (`BL-0287`), so packages are the source.
- [x] **DOM content (`BL-0293`).** No DOM section has traceability content.
- [x] **Decision recorded:** **this document is authoritative for tag-grain traceability and chain
  completeness**; `requirements/03` stays the authoritative leaf-grain matrix, owned by `04`, with
  findings F2–F4 handed to it. With this gate closed, **the GDS ladder is complete**: every topic
  `docs/build-spec/` and `docs/design/` covered now has an authoritative GDS level, so both can be
  retired in the cleanup sweep (`BL-0292`), and `CLAUDE.md`'s ladder text can be updated
  (`BL-0301`).

## Next

The ladder is closed. Next, in order: the owner decisions batched in the backlog; the `04` pass that
takes GDS-06's gaps and corrections (`BL-0298`) and this document's findings F1–F4; then the cleanup
sweep that retires `docs/build-spec/` and `docs/design/` (apart from the ICD, which moves).
