[↑ Docs index](../INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md) ·
[Release plan](../feature-planning/01-release-plan.md) · [Previous assessment (REV-REL-001)](release-assessment-fs-tracked-baseline.md)

# Release Assessment — Release Candidate 1 (whole repository)

> **Document ID:** REV-REL-002
> **Skill:** `11-release-readiness` (fresh session, higher-tier model at the owner's request; took no part
> in implementing, verifying or integration-reviewing any package)
> **Date:** 2026-10-25
> **Commit assessed:** `19f2653c57b74ff65717d191ea5bf3d35d4f693b` (branch `claude/release-assessment-1`,
> tip = `claude/release-candidate-1` after `IP-1082` was merged; pipeline run #261)
> **Scope:** the whole release candidate — all 84 packages on the Master Build Plan (83 `VERIFIED`;
> `IP-1160` `BLOCKED`, not authorized, excluded by the owner), every FS-tracked Feature (`FS-101`…`FS-135`,
> `FS-201`, `FS-301`; `FS-108`/`FS-202` scoped-not-authorized), the pre-pipeline foundation (P0–P8), and the
> release-push remediation since [REV-REL-001](release-assessment-fs-tracked-baseline.md) (NO-GO, 2026-07-05).
> **Upstream evidence:** 83 Verification Reports; four Integration Reports
> ([18-package](integration-review-18-package-tranche.md), [tranche 2](integration-review-tranche-2-white-controls-saves-test-origins.md),
> [tranche 3](integration-review-tranche-3-release-push-remediation.md), [release candidate 1](integration-review-release-candidate-1.md)).
> **Decision owner:** the project owner. This document is advisory. **No baseline record was flipped.**

## 0. Recommendation (summary)

**NO-GO as the candidate stands today, converting to GO when two procedural conditions are met. No code
defect blocks the release:** every suite is green in every mode, in the system environment, in a fresh
venv at the latest available dependency versions and in a fresh venv built from `requirements.lock`; zero
Critical or High code findings are open; the shipped app ran end to end for White, Blue and Red.

| # | Blocking condition | Why it blocks | Owner / route |
|---|---|---|---|
| **B1** | **40 of the 83 `VERIFIED` packages have never been inside any integration review's scope** (§2.3): the whole of Tranche 3 (`IP-1170`–`IP-1174`), the 2026-09/10 waves (`IP-1061`–`IP-1067`, `IP-1180`–`IP-1300`, `IP-1310`, `IP-1320`/`1321`, `IP-1021`, `IP-1041`, `IP-1052`, `IP-1131`, `IP-1211`/`1212`, `IP-1221`–`1223`, `IP-1230`, `IP-1261`/`1262`), and `IP-1082` (merged after the release-candidate review). | This skill's quality gate requires every delivered row to carry *integration coverage*, and "a missing report is a NO-GO input, not a gap to fill in-pass". Whole-tree mechanical checks (full suite, determinism, import guard, whole-route-table seat sweep, 19/19 vignette round-trip in RC-1) reduce the risk but are not a cross-package review of those packages' seams. | `10-integration-review` on that 40-package set (one pass), or an explicit owner acceptance of the gap recorded in this file |
| **B2** | **REV-REL-001's sole blocker is not closed by delivery.** `FEAT-3500` (Role-Scoped Command Catalog, `FR-3510`/`FR-3520`, Must, Release 1) is still unimplemented; its package `IP-1160` is unauthorized and the owner excluded it from this release, but `01-release-plan.md` still lists `FEAT-3500` in Release 1 and no descope is recorded. | Shipping a Must-priority, in-bucket Feature that provably does not exist, with no recorded authorization to descope it, is unauthorized drift (REV-REL-001 §5, Path B). | Owner decision (descope to a later bucket), then `05-feature-decomposition` records it in the release plan; same treatment for the three partial items in §4 (`FR-7450`, `FR-5310` template clause, `NFR-3810`) |

When B1 is closed clean (no new Critical/High) and B2 is recorded, the evidence in this document supports
**GO**; a short delta re-run of this skill (or the owner's GO on this document plus the B1 report) is enough.
The Medium items in §5 do not block; they ship as known deviations if the owner accepts them.

## 1. Scope audit

### 1.1 Package ledger (recounted from the Master Build Plan table, not from summaries)

84 package rows: **83 `VERIFIED`, 1 `BLOCKED` (`IP-1160`)**, 0 other. Every `VERIFIED` package has a
Verification Report on disk and a row in `verification/INDEX.md` reading `VERIFIED` (latest version where a
v1.0 was `RETURNED`: `VR-1062`, `1064`, `1069`, `1174`, `1210`, `1082`). No VR without a package.
`test_doc_integrity.py`'s ledger check (Master Build Plan vs `packages/INDEX.md`, GDS ladder vs ROADMAP) is green
with an empty allow-list.

### 1.2 One row per FS-tracked Feature

Integration coverage key: **18** = 18-package review (2026-07-04); **T2** = tranche 2; **T3** = tranche 3;
**RC** = release-candidate-1 review; **—** = package never in any review's scope (B1). Where an FS names no
`FEAT-xxxx` itself (FS-118–120, 124–129), the Feature column is derived from its requirement family.

| FS | Feature(s) | IP(s) → VR | Integration coverage | Delivered? |
|---|---|---|---|---|
| FS-101 Mission Planning | FEAT-3100 | 1010 | 18 | Yes |
| FS-102 Command Scheduling | FEAT-3300/3400 | 1020, 1021 | 18; **1021 —** | Yes |
| FS-103 Custody | FEAT-1500 | 1030 | 18 | Yes |
| FS-104 SDA Tasking | FEAT-3200 | 1040, 1041 | 18; **1041 —** | Yes |
| FS-105 Spacecraft Ops | FEAT-2100–2500, 1400 | 1050, 1051, 1052 | 18; **1052 —** | Yes |
| FS-106 White Cell Dashboard | FEAT-4300/4400/4600/4700 | 1060–1068, 1072–1076, 1082 | 18 (1060); T2 (1068); T3/RC (1072–1076); **1061–1067, 1082 —** | Yes |
| FS-107 AAR | FEAT-7300 | 1070, 1077 | 18; RC | Yes |
| FS-109 LAN Transport | FEAT-6300/6400 | 1090 (+1091 test) | 18; T2 | Yes |
| FS-110 Save & Resume | FEAT-7200 | 1100–1103, 1081 | 18; T2; T3; RC | Yes |
| FS-111 AI-Red | FEAT-9100 | 1110 | 18 | Yes |
| FS-112 Classification Banner | FEAT-4500 | 1120 | 18 | Yes |
| FS-113 Observer | FEAT-6500 | 1130, 1131 | 18; **1131 —** | Yes |
| FS-114 Hot-Seat Hand-Off | FEAT-6600 | 1140 | 18 | Yes, with the owner-accepted `BL-0015` risk |
| FS-115 Session Setup | FEAT-4100/4200 | 1150, 1151 | 18 | Yes |
| **FS-116 Role-Scoped Command Catalog** | **FEAT-3500** | **1160 `BLOCKED`** | — | **No — B2** |
| FS-117 Vignette Creator | FEAT-5100 | 1170–1174 | **—** | Yes (B1) |
| FS-118 External Vignette Dirs | FEAT-5400 | 1180 | **—** | Yes (B1) |
| FS-119 Bulk TLE/OMM | FEAT-5200 | 1190 | **—** | Yes (B1); `BL-0139`/`BL-0140` open |
| FS-120 Save-as-Scenario | FEAT-5500 | 1200 | **—** | Yes (B1) |
| FS-121 Ephemeris/TLE Export | FEAT-7400 | 1210, 1211, 1212, 1262 | **—** | Yes, except `FR-7450` (§4) |
| FS-122 Sensor Modalities | FEAT-1600 | 1220–1223 | **—** | Yes (B1) |
| FS-123 Space-Weather Coupling | FEAT-1200, FEAT-4400 | 1230 | **—** | Yes (B1) |
| FS-124 Debris Persistence | FEAT-1400 slice | 1240 | **—** | Yes (B1) |
| FS-125 Manoeuvre Ledger | FEAT-1300 | 1250 | **—** | Yes (B1) |
| FS-126 Telemetry CSV | FEAT-2300 | 1260, 1261 | **—** | Yes (B1) |
| FS-127 Effect Gating / Live ROE | FEAT-3400 (FR-3430/3440) | 1270 | **—** | Yes (B1) |
| FS-128 Variable-Speed AAR | FEAT-7300 | 1280 | **—** (1077 hardened it, RC) | Yes (B1) |
| FS-129 Jamming Delivery / Detectability | FEAT-1400 | 1290 | **—** | Yes (B1) |
| FS-130 RIC View & CATS | FEAT-8200 | 1300 | **—** | Yes (B1) |
| FS-131 Load-Time Validation | FEAT-5300 | 1310, 1311 | 1311 T3/RC; **1310 —** | Yes, except the `FR-5310` template clause (§4) |
| FS-132 Effect Resource Bounds | FEAT-1400 | 1320, 1321 | **—** | Yes (B1) |
| FS-133 Test-Origin Traceability | FEAT-12100 | 1330–1335, 1079 | T2; T3; RC | Yes |
| FS-134 Browser Console Rules | FEAT-12200 | 1340 | T2 | Yes |
| FS-135 Documentation Integrity | FEAT-12300 | 1350 | T2 | Yes for `NFR-3800/3820/3830`; `NFR-3810` unbuilt (§4) |
| FS-201 Competency Assessment | FEAT-10100 | 2010 | 18 | Yes (`BL-0019`/`BL-0020` since dispositioned DONE) |
| FS-301 Research Analytics | FEAT-10200 | 3010 | 18 | Yes |
| *(no FS)* | `NFR-1300`, `NFR-3030`, ledger hygiene | 1091, 1069, 1078, 1080 | T2; T3/RC | Yes |

**Pre-pipeline foundation** (`FEAT-1100`, `1200`, `5300` core, `6100`, `6200`, `7100`, `8100`, `11100`, `11300`):
built in P0–P8 before the FS/IP apparatus; re-verified by the permanent gates and the full suite every run
(§2), as REV-REL-001 accepted. `FEAT-11100`/`11300` (training corpus) are in place; see `BL-0268` (§5).

## 2. Evidence

### 2.1 Test suite — run by this assessment, real exit codes, `--junitxml` on every run

| Environment | Mode | Exit | Tests | Passed | Failed/Errors | Skipped |
|---|---|---|---|---|---|---|
| System Python 3.13.17 (container default; `pydantic 2.13.5`, `numpy 2.5.3` — below the floors) | unfiltered | **0** | 1786 | 1783 | 0/0 | 3 |
| Fresh venv, **latest versions** (`pip install -U -e ".[content,ui,dev]"`) | unfiltered | **0** | 1786 | 1783 | 0/0 | 3 |
| same | `-m "not browser"` | **0** | 1753 | 1749 | 0/0 | 4 |
| same | `-m browser` (Chromium `/opt/pw-browsers`, really ran) | **0** | 33 | 33 | 0/0 | 0 |
| same | gates alone (determinism, import guard, doc integrity, test origins) | **0** | 45 | 44 | 0/0 | 1 |
| Fresh venv **from `requirements.lock`** (`pip install -r requirements.lock && pip install --no-deps -e .`; `pip check` clean) | unfiltered | **0** | 1786 | 1783 | 0/0 | 3 |
| same | `-m "not browser"` | **0** | 1753 | 1749 | 0/0 | 4 |
| same | `-m browser` | **0** | 33 | 33 | 0/0 | 0 |
| same | gates alone | **0** | 45 | 44 | 0/0 | 1 |

Skips: the three long-standing data-dependent vignette skips (`test_defensive_audit_2026.py` ×2,
`test_derived_probabilities.py` ×1) in every full run; the fourth in filtered runs is the by-design
partial-collection guard in `test_test_origins.py` (it runs and passes in every unfiltered run). 1753 + 33 = 1786.

**Permanent gates by name (junit, every environment):** `test_determinism.py` **6 passed**,
`test_import_guard.py` **8 passed**, `test_doc_integrity.py` **9 passed**, `test_test_origins.py` 22 passed
unfiltered (21 + 1 partial-collection skip alone). `--origin-report=rtm` → "Test column regenerated
(unchanged)", tree clean (exit 5 = "no tests ran", RC `L-3`, still open, cosmetic).

One warning in the venv runs: `StarletteDeprecationWarning: Using httpx with starlette.testclient is
deprecated; install httpx2` — test-only, harmless today, a future dependency move (§5, L-row).

### 2.2 Verification Reports

83/83 `VERIFIED` packages carry a VR, latest verdict `VERIFIED`, each by a fresh session independent of the
implementer. VR-1082 v2.0 (2026-10-25) closes RC review `M-1`..`M-3` and `L-2` (playback cursor clamp) with a
2,646-request non-finite sweep over all 42 mutating routes (no 500) and a Chromium toolbar-refusal check. This
assessment's smoke re-confirmed the `M-1` fix on the shipped server (`{"rate": NaN}` → 400; every read 200).

### 2.3 Integration Reports and the coverage gap (B1)

| Review | Packages in scope | Result |
|---|---|---|
| [18-package](integration-review-18-package-tranche.md) (2026-07-04) | 18 (`IP-1010`…`IP-3010` originals) | 0 Crit/High |
| [Tranche 2](integration-review-tranche-2-white-controls-saves-test-origins.md) (2026-10-24) | 10 | 0 Crit/High, 9 Medium — closed (RC §8.2) |
| [Tranche 3](integration-review-tranche-3-release-push-remediation.md) (2026-10-24) | 9 | 0 Crit/High, 5 Medium — closed (RC §8.1) |
| [Release candidate 1](integration-review-release-candidate-1.md) (2026-10-25) | 15 (+ docs/requirements/lock) | 0 Crit/High; `M-1`..`M-3` closed by `IP-1082` (VR-1082 v2.0) |

Union of the four scopes: **43 packages**. Computed from each report's own scope line against the 84-row
ledger: **40 `VERIFIED` packages have never been in any integration review's scope** — listed in B1 (§0). The
pipeline archive confirms it: the run #82 entry records `10-integration-review` "on the run #81 tranche" as the
manager's default recommendation, superseded by a session override, and no later run reviewed those packages.
Partial mitigations already in the record: RC re-derived the seat rule over the **whole** live route table, ran
a 19/19-vignette replay-equals-live round-trip, and every review ran the full suite; none reviewed, for example,
`IP-1270` gating against `IP-1290` jamming delivery, `IP-1230` drag against `IP-1210` ephemeris export, or
`IP-1173`/`IP-1174` Creator against `IP-1310` load validation as cross-package seams.

### 2.4 NFR-1510 — dependency lock (procedure run now, at release)

1. **Check latest.** Fresh venv, `pip install -U -e ".[content,ui,dev]"` (proxy CA, TLS verification on).
   Resolved set **identical to `requirements.lock`** — all 33 pins, zero movement since the lock was produced
   earlier today. `pip list --outdated`: only `pyee 14.0.0` (latest `16.0.0`), held by `playwright 1.64.1`'s own
   `pyee<15,>=13` constraint — transitive, not ours, nothing to hold back on the project's side.
2. **Try the update.** Unfiltered, `-m "not browser"`, `-m browser` and the gates: all exit 0 (§2.1).
3. **Fix or hold.** Nothing broke; no fix, no held-back package.
4. **Validate and re-pin.** No newer set exists, so **no re-pin: `requirements.lock` is unchanged and correct.**
   `pyproject.toml` floors equal the lock pins (RC review recount, re-checked here). A second fresh venv from the
   lock (`pip check` clean, freeze identical to the lock) passed all three modes and the gates (§2.1).
5. **Result: NFR-1510 PASS.** Interpreter CPython 3.13.17 (lock header). Observation: the container's default
   environment is below the floors (`pydantic 2.13.5`, `numpy 2.5.3`) and also green — the floors are validated,
   not minimal; a deployer must install from the lock (README does not yet say so — §5).

### 2.5 NFR-2830 — test-relevance audit (whole suite, read-only)

Source: `python3 -m pytest --origin-report` plus an AST scan of `spacesim/tests/`. Baseline: 113 FR + 48 NFR
leaves (161), 38 FS, 84 IP.

| Check | Result |
|---|---|
| Tests with no origin | **0** (`test_origin_allowlist.txt` empty) |
| Tests citing an ID absent from the baseline | **0** (the suite's own gate) |
| Tests citing a retired/superseded requirement | **0 detectable** — neither ledger marks any leaf retired or superseded, and retirement is not yet defined (`BL-0317`, `baseline_ids.resolve_problem`). The check is therefore existence-only; not a pass on retirement. → `04` (define retirement marking) |
| Duplicate checks | **0 true duplicates.** One identical-body pair (`test_origin_retag.py::test_each_listed_retag_is_in_place` / `…_browser_retag_…`) is the same helper over disjoint parametrizations (browser vs non-browser) — intentional. Two same-name pairs across modules (`test_http_non_white_is_403`, `test_null_params_mean_absent`) test different routes/order types. Limitation: semantic duplicates with different bodies are not machine-detectable |
| Requirements with no test naming them | **38 of 161** (list below) |

**The 38 untested requirements, classified and routed:**

| Class | Requirements | Verification method declared | Disposition / route |
|---|---|---|---|
| **A. Unbuilt** (no test possible) | `FR-3510`, `FR-3520` (FEAT-3500/IP-1160); `FR-7450` (ISO-8601 span bounds, Should, `06` spec owed); `NFR-3810` (retired-doc check, waits on `BL-0319`) | Test | Deviations (§4); B2 for FR-3510/3520 → owner, then `05`; FR-7450 → `06`; NFR-3810 → owner then `07` |
| **B. Built and test-verifiable, tests exist but are tagged to a sibling ID** | `FR-1140` (integer-µs sim time — `simtime` tests), `FR-3410` (execute-time re-validation), `FR-7110` (event log), `FR-7350` (AAR CSV/JSON export, `aar.export_csv`), `FR-11420` (machine-verified playbooks — `test_vignette_tutorials.py` is tagged `NFR-3400` only), `NFR-2400` (state-hash determinism — `test_determinism.py` tagged `NFR-1500`/`FR-1120`), `NFR-2500`/`NFR-2600` (action-log sufficiency/completeness — AAR and failure-atomic tests), `NFR-2800` (gated build — the suite itself), `NFR-3200` (offline TLE/OMM import by paste/file) | Test | → `07` one retag package (add the missing `verifies` IDs; no new behaviour); `04` to confirm `NFR-2800` is meaningfully test-verifiable |
| **C. Verified by Inspection / Demonstration / Analysis** (no automated test expected) | `FR-11110`, `FR-11120`, `FR-11210`, `FR-11310`, `FR-11320`, `FR-11410`, `FR-4710`, `FR-4720`, `FR-6110`, `FR-6220`, `FR-6610`, `NFR-1200`, `NFR-1400`, `NFR-1510` (this §2.4), `NFR-2000`, `NFR-2100`, `NFR-2300`, `NFR-2900`, `NFR-3000`, `NFR-3040`, `NFR-3060`, `NFR-3300`, `NFR-3500`, `NFR-3600` | Inspection / Demo / Analysis | Correctly absent from the test report. → `04`: the origin report should exclude non-Test methods (or the RTM should say "verified by inspection, see …") so the list shows only real gaps; `FR-6110`, `FR-6220`, `NFR-2000` could gain cheap structural tests (`07`, optional) |

## 3. Closure of REV-REL-001 (2026-07-05) — each NO-GO reason and residual risk, with evidence

| REV-REL-001 item | Status now | Evidence |
|---|---|---|
| **§5 Finding 2 — FEAT-3500 undelivered (High, the sole NO-GO reason)** | **Not closed.** Spec and plan exist (`FS-116` v1.2, `ADS-3500` v1.1, `IP-1160` v1.1); code does not. Owner answered "not yet" (run #37) and excluded `IP-1160` from the release push (run #256). `BL-0049` still open High. | → **B2** |
| §4.1 Hot-seat fog-leak risk (`BL-0015`, High, accepted) | Unchanged, still **owner-accepted** | `IP-1140` header; archive `BL-0015` DONE with the owner's verbatim acceptance |
| §4.2 IP-1020 invented lifecycle vocabulary (`BL-0036`) | **Closed** | archive DONE, run #159 |
| §4.3 IP-1100 Role-Assignment persistence overclaim (`BL-0045`) | **Closed** | archive DONE, run #159 |
| §4.4 FS-201 self-assessment gap (`BL-0020`; `BL-0019`) | **Closed** (dispositioned) | archive DONE |
| §4.5 LAN trust model (`ADR-0015`) | **Unchanged by design; restated in §6** | — |
| §4.6 `training/15` wrong citation (`BL-0048`) | **Closed** | archive DONE, run #32 |
| §4.7 Package-doc / feature-index staleness (`BL-0030`/`BL-0031`) | **Closed** | archive DONE, runs #159/#163; doc-integrity ledger check now enforces it |
| §4.8 Finding 1 — `FR-3310` single scheduler (`BL-0050`) | **Closed** | archive DONE; `FR-3310` has tagged tests (origin report; `IP-1131`) |

## 4. Deviations (delivered differently from the plan)

| Deviation | Authorization trail |
|---|---|
| `FEAT-3500` / `FR-3510`, `FR-3520` not built | **Owner did not authorize `IP-1160`** (runs #37, #256) and excluded it from this release, but **no descope is recorded in the release plan** → B2 |
| `FR-7450` (ISO-8601 bounds on time-span exports, Should, promoted from `CR-22` in run #256) not built | Release-push directive paused new features (run #256/#260); no bucket move recorded → record with B2 |
| `FR-5310` template-reference clause unbuilt (FS-131 criterion 10) | `BL-0233` Medium, `ADR-0036`-routed decision pending at `03`/`04`; disclosed in `feature-index.md` → record with B2 |
| `NFR-3810` retired-document check unbuilt (FS-135) | Waits on owner decision `BL-0319`; disclosed in `feature-index.md` → record with B2 |
| Hot-seat hand-off is manual/auto-cycle, not automatic relinquish detection (`FR-6610`) | Owner-accepted risk (`BL-0015`) |
| AI-Red reads ground truth (`ADR-0024`) | Documented design boundary, Should-priority Feature |

## 5. Residual risks and open findings shipping with the release (non-blocking unless noted)

**Open backlog** (`docs/pipeline/backlog.md`, read-only here): **79 open entries** — 1 High open item that
blocks (`BL-0049` → B2); 1 High that is planning/doc work, not a product defect (`BL-0292`, GDS authoring — now
done per `architecture/INDEX.md`, entry is stale) and 1 High owner direction now implemented (`BL-0310`,
IP-1330 series — entry stale); 14 Medium; 62 Low/other. No open Critical. Every Medium and the functional Lows:

| ID | Sev | What | Disposition proposed for this release |
|---|---|---|---|
| `BL-0284` | Medium | **Rewind silently drops White's unedited future-dated injects** — reproduced by this assessment on the shipped code (pending `white-1` gone after `step` + `rewind`). Not in the White Cell manual. | Known deviation; facilitator note in WCM-4 (`08-training-manual-authoring`), fix via `07`→`08` |
| `BL-0139` | Medium | OMM `EPOCH` parsed then discarded; elements anchored at session start | Known deviation (fidelity), `07` |
| `BL-0140` | Medium | Malformed per-object assignment in bulk import reported as a 500 in the original finding; not reproduced with this assessment's input (200, empty result) — left open as recorded | Known deviation pending re-check, `08` |
| `BL-0268` | Medium | `FR-11110` coverage: the Vignette Creator has **no** procedure in `docs/training/` (only the API reference and matrix); bulk import only in the API reference; save-as-scenario only in the UI reference | Known deviation in the co-equal training corpus; `08-training-manual-authoring` |
| `BL-0233` | Medium | `FR-5310` template clause (§4) | With B2 |
| `BL-0334` | Medium | Link allow-list keyed on (file, target) hides repeat breakages | `07`→`08` |
| `BL-0028` | Medium | R600 citations unverified by fetch (egress policy) | Known research-confidence caveat |
| `BL-0288`, `BL-0293` | Medium | Governance wording / ~40 documents outside every skill's write scope | Doc governance, not product |
| `BL-0297`, `BL-0299`, `BL-0315`, `BL-0379`, `BL-0252`, `BL-0310`, `BL-0292` | Medium/High | **Stale backlog statuses**: the work is done (IP-1350, the lock, IP-1101, IP-1311, IP-1330 series, GDS-06..10) but rows still read `IN`/`SCHEDULED`/`DECIDED` | `00-pipeline-manager` triage (bookkeeping only) |
| RC `L-1` | Low | Live event log unbounded while load refuses > 100,000 entries (script-reachable only) | `04`/`07` |
| RC `L-3`, `L-5` | Low | `--origin-report` exits 5; two parsers of the same ledgers | `07` |
| RC `L-6` | Low | Rewind leaves the clock running | **Closed by owner decision** ("rewind-pause immaterial", run #260) |

**New findings of this assessment** (none Critical/High):

| # | Sev | Finding | Route |
|---|---|---|---|
| N1 | High (process) | B1 — 40 packages without integration review | `10-integration-review` |
| N2 | Medium | `training-basics` tutorial is not machine-verified (`test_vignette_tutorials.py` covers only the 8 numbered vignettes) and three of its statements do not hold on the shipped engine: Red step 4 promises safe mode, but the cyber `seize_c2` resolves stochastically (seed 0 and 2 fail, 1 and 3 succeed); Blue step 5's "next GS-TRN command pass" is ~11 h out, past the T+1 h deadline, by which time `keep_custody` has decayed, so step 6 "custody held" is false if the step is followed; the Blue brief's ROE note says "Cyber OFF for both sides by default" while the parameter default is `cyber_authorized: true` | `08-vignette-development` (+ `09-training-manual-review`) |
| N3 | Low | Run-spacesim driver is stale: its Chromium glob (`chrome-linux/`) misses the shipped `chrome-linux64/` build, so it exits "No Chromium found"; and its `target_picker` probe looks for `#o-target-pick` (now `#o-target`) | `00-intake` (unnumbered utility) |
| N4 | Low | `README.md` still says "419 tests"; its LAN section recommends `--host 0.0.0.0 --reload` (dev reload in a deployment) and carries **no trust-model warning**; it does not say to install from `requirements.lock` | Owned by this skill on GO (`BL-0293`) — fixed in the GO flip (§8) |
| N5 | Low | `CLAUDE.md` status line counts are stale (1700 / 1697 / 1669 / 31 browser vs measured 1786 / 1783 / 1753 / 33) | GO flip (§8) |
| N6 | Low | `01-release-plan.md` body is stale: FEAT-8200 "entirely unimplemented", FEAT-12100/12200/12300 "not yet implemented" — all built and `VERIFIED` | `05-feature-decomposition` (with B2) |
| N7 | Low | Starlette deprecates `httpx` for its test client (`httpx2`) | `07` at the next dependency refresh |

## 6. The LAN trust model — the product's accepted security boundary (stated plainly)

**There is no authentication.** Every request names its own seat (`cell=white|blue|red|observer`) and the
server believes it. Fog-of-war is enforced server-side for every cell-scoped response, and White-only controls
and Observer mutations are refused server-side — but against the *asserted* seat, not a verified identity.
Consequences a deployer must accept:

- Anyone who can reach the port can read any cell's belief picture (`/scene/red` from a Blue tab returned 200
  in this assessment's smoke — by design) and can drive White Cell controls by sending `?cell=white`.
- The no-cell ground-truth endpoints (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`,
  `/assessment`, `/ephemeris/truth`, Observer and White authoring reads — `FR-6220`) expose full truth to any client.
- Traffic is plain HTTP; there is no TLS and no audit of who did what beyond the event log's seat field.
- Hot-seat hand-off does not auto-blank on seat change (`BL-0015`, owner-accepted).

**What a deployer must do:** run only on an isolated, trusted LAN (or loopback) with cooperative participants;
never expose the port to the internet or an untrusted network (bind `127.0.0.1` for single-machine; bind the LAN
address only behind a host firewall limited to participants' machines); do not use `--reload` in an exercise;
install from `requirements.lock`; treat every participant as able to see ground truth; brief participants that
seat selection is an honour system. Per-cell tokens are tracked in `docs/FUTURE-WORK.md`. Source: `ADR-0015`,
`NFR-2300`, `FR-6220`, `CLAUDE.md` "LAN trust model", `training/01` §2.1, `12-white-cell-manual.md` WCM-3.

## 7. End-to-end smoke of the shipped app (this assessment)

Server: `python3 -m spacesim.ui_web` from the **lock venv** (`SPACESIM_CONFIG` → port 8765), loopback.

- **Headless Chromium (`/opt/pw-browsers/chromium-1243`), White, Blue and Red seats**, vignettes
  `training-basics` and `leo-isr-denial` (6 runs; a scratch copy of the run-spacesim driver with the Chromium
  glob fixed, N3): each loaded via Session ▾, started, stepped 3 × 10 min as White, switched seat, opened the
  telemetry drill-down. All 6 exit 0; fleet rows White 8/7, Blue 3/4, Red 5/3 (each seat sees its own fleet
  only); panel tool bars 12, sparklines 19. Blue screenshot inspected: mission brief, fleet SOH, tasking,
  command panel with live dry-run ("will queue · ground_uplink · window …"), globe, belief map, timeline and
  subsystem drill-down render; no Red asset on the Blue picture.
- **API, `training-basics` tutorial path.** Blue: observe RADAR-TRN→RED-TGT, downlink ISR-EO-1 via GS-TRN,
  advance → `deliver_isr` true (and `keep_custody` true at T+1 h in an in-process trace); manoeuvre queued for the
  next command pass (~11 h, N2). Red: observe, cyber queued off-pass, kinetic `engage` **rejected
  `roe_kinetic_not_authorized`**, +3601 s → `deny_isr` true (`disable_isr` seed-dependent, N2).
- **Seat and fog rules on the live server:** Blue `step` 403; no-seat `step` 403; Observer order 403; White
  `{"rate": NaN}` 400 and every read (clock, godview, objectives, scene, save) stays 200; Blue scene has no Red
  asset ids while godview does; Blue telemetry read of a Red asset 404; save 200. 19 vignettes listed. Server log:
  no tracebacks.

## 8. Assessment

**Recommendation: NO-GO today; GO when B1 and B2 are closed** (§0). The engineering evidence is strong — the
suite is green in all three modes in three environments, the permanent gates are green, the lock is current and
validated, zero untagged tests, the app works end to end — and every REV-REL-001 residual risk except the
FEAT-3500 blocker is closed. What is missing is procedural: integration coverage for 40 packages, and a recorded
descope for scope the owner has already decided not to build.

**Decisions needed from the owner:**
1. B1 — commission `10-integration-review` on the 40-package set, or accept the gap explicitly (record it here).
2. B2 — record the descope of `FEAT-3500` (and the `FR-7450`, `FR-5310` template-clause, `NFR-3810` partials)
   to a later bucket; or authorize `IP-1160` (Path A, longer).
3. Accept as known deviations: `BL-0284` (rewind drops future White injects), `BL-0268` (Creator manual
   coverage), `BL-0139`/`BL-0140`, N2 (training-basics tutorial accuracy), and the §6 trust model.

**Records that WOULD be flipped on a GO** (none touched by this assessment):

| Record | Change |
|---|---|
| `docs/feature-planning/01-release-plan.md` | Mark Prototype, MVP, Release 1 and Release 2 buckets released at this commit; `FEAT-3500` (and the §4 partials) moved to a later bucket per the owner's B2 decision; fix the N6 stale statements |
| `ROADMAP.md` | Add a "Release 1 (release candidate 1) — released" status entry dated at GO with the commit; refresh the IP-1082 row title (VR-1082 O1); keep `IP-1160` `BLOCKED` |
| `CLAUDE.md` | Status line: released; counts 1786 tests (1783 passed / 3 skipped; `-m "not browser"` 1753 with 4 skips; `-m browser` 33) |
| `README.md` | Status and counts (419 → 1786); install from `requirements.lock`; LAN section: drop `--reload`, add the §6 trust warning |
| `docs/INDEX.md`, `docs/feature-planning/INDEX.md` | Point at this assessment as the release record |
| `docs/implementation/00-master-build-plan.md` | Summary line naming the release commit (package statuses unchanged) |
| This document | Date-stamp the baseline and record the owner's GO |

Commit as `docs(release): release candidate 1 — assessment + baseline update` at that time.

## 9. Pipeline position

Stage 11. **Next step:** `10-integration-review` on the 40-package set (B1) and the owner's B2 decision
(recorded by `05-feature-decomposition`), then re-run `11-release-readiness` as a delta against this document.
