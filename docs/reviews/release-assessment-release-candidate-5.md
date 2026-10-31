[↑ Docs index](../INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md) ·
[Release plan](../feature-planning/01-release-plan.md) · [Previous assessment (REV-REL-002)](release-assessment-release-candidate-1.md) ·
[First assessment (REV-REL-001)](release-assessment-fs-tracked-baseline.md)

# Release Assessment — Release Candidate 5 (whole repository)

> **Document ID:** REV-REL-003
> **Skill:** `11-release-readiness` (fresh session, higher-tier model at the owner's request; took no part
> in implementing, verifying, integration-reviewing or training-reviewing any package)
> **Date:** 2026-10-31
> **Commit assessed:** `f7cdc6d` (branch `claude/release-assessment-2`, tip = `origin/claude/release-candidate-5`)
> **Status:** IN PROGRESS — sections are filled as evidence arrives.
> **Decision owner:** the project owner. This document is advisory. **No baseline record was flipped.**

## 0. Recommendation (summary)

_Pending evidence._

## 1. Scope audit

_Pending._

## 2. Evidence

### 2.1 Test suite — run once per mode by this assessment, real exit codes, `--junitxml` on every run

System interpreter CPython 3.13.17, commit `f7cdc6d`, `-p no:cacheprovider`, Chromium from `/opt/pw-browsers`.

| Mode | Exit | Tests (junit) | Passed | Skipped | Failures/errors | Expected |
|---|---|---|---|---|---|---|
| unfiltered | **0** | 2165 | 2161 | 4 | 0/0 | 2165 / 4 — match |
| `-m "not browser"` | **0** | 2123 | 2118 | 5 | 0/0 | 2123 / 5 — match |
| `-m browser` (really ran in Chromium) | **0** | 42 | 42 | 0 | 0/0 | 42 / 0 — match |

2123 + 42 = 2165. The fifth non-browser skip is the partial-collection guard in `test_test_origins.py` (it
runs and passes in the unfiltered run). The four unfiltered skips are tests whose precondition the chosen
vignette does not meet (`test_activity_fog_matrix::test_row_10_neutral_owned_effect_white_only` — no neutral
asset; two `test_defensive_audit_2026` booking-release tests — order refused `no_window` /
`no_command_station`; `test_derived_probabilities::test_jam_ignores_operator_success_prob_override` — no SATCOM
target). They never execute their assertion in any mode: see §2.5 finding R-2.

**Permanent gates, by name, from the unfiltered junit:** `test_determinism` 6/6 pass, `test_import_guard` 8/8
pass, `test_doc_integrity` 9/9 pass, `test_vignette_tutorials` 115/115 pass, test-origin tests (`test_origin*`,
`test_test_origins`) 217/217 pass.

**Allow-lists (non-comment entries):** `test_origin_allowlist.txt` **0**; `doc_integrity_allow_indexes.txt`
**0**; `doc_integrity_allow_ledgers.txt` **0**; `doc_integrity_allow_links.txt` **38** (known broken relative
links, list only shrinks; `BL-0334` notes its (file, target) keying).

Note: the system interpreter carries `pydantic 2.13.5`, below the `pyproject.toml` floor `2.14.1`; the suite is
green there too, and §2.4 repeats the run on the locked and the latest sets.

### 2.2 Verification Reports

Recounted from the Master Build Plan package table: **90 package rows, 90 distinct ids, 90 `VERIFIED`**, 0
`BLOCKED`/`READY`/`IN PROGRESS`. Every one of the 90 has a `VR-xxxx` file in `docs/implementation/verification/`
(90 ids; none missing). Spot-reads: `VR-1160` v3.0 final **VERIFIED** (third pass after two RETURNs); `VR-1084`,
`VR-1087` v1.0 **VERIFIED**.

**Finding V-1 (Low, documentation, → `09-package-verification`):** `VR-1088`'s header still reads
`Version: 2.0`, `Produces: the COMPLETE → IN PROGRESS return of IP-1088 (not VERIFIED)`, and its `## Result`
section says **RETURNED**; the v3.0 **VERIFIED** result exists only as an appended section (commit `4fb4847`).
The INDEX, MBP and package header say `VERIFIED` (v3.0). The verdict is real (code diff since v2.0 empty; v2.0
ran the full suite green), but a reader of the report's top sees the wrong outcome. Fix the header and Result.

### 2.3 Integration coverage — derived independently from each report's scope line

| Report | Scope (explicit package list) | Count | Headline |
|---|---|---|---|
| [18-package tranche](integration-review-18-package-tranche.md) | `IP-1010`…`1151`, `2010`, `3010` | 18 | clean |
| [Tranche 2](integration-review-tranche-2-white-controls-saves-test-origins.md) | `IP-1068`, `1101`, `1091`, `1069`, `1330`, `1350`, `1340`, `1331`–`1333` | 10 | 0 C / 0 H |
| [Tranche 3](integration-review-tranche-3-release-push-remediation.md) | `IP-1311`, `1102`, `1072`–`1075`, `1103`, `1334`, `1335` | 9 | — |
| [Release candidate 1](integration-review-release-candidate-1.md) | Tranche 3 + `IP-1076`–`1081` | 15 (6 new) | 0 C / 0 H / 3 M |
| [Unreviewed packages](integration-review-unreviewed-packages.md) (closes REV-REL-002 B1) | the 40 (§1.2 groups A–F) + `IP-1082` | 41 | 0 C / **3 H** / 6 M / 9 L |
| [RC-3 delta](integration-review-rc3-delta.md) | `IP-1082`–`1087`, `IP-1160` + vignette/tutorial/manual/lock changes | 7 | 0 C / 0 H / 4 M / 9 L; **GO, conditional** |

Union computed by script against the MBP: **89 of 90 covered. Not covered: `IP-1088`** (fog-correct activity
feed, `FR-6210`/`FR-6220`/`FR-4450`). `IP-1084`–`1087` are covered by the RC-3 delta's scope line; `IP-1160` is
covered by the RC-3 delta (verdict "Holds, with the two known deviations", its `M-2`). The unreviewed-packages
review's three Highs are recorded **Closed** by the RC-3 delta (§4.1: H-1 via `IP-1084` with a fog probe, H-2
via `IP-1085`, H-3 re-driven with a stale ISS TLE).

**`IP-1088` was authored, built and verified after the RC-3 delta (2026-10-31) to close that review's `M-1`**
(Blue and Red saw White's scheduled injects on `GET /activity/{cell}`). It changes `CellController` — the
fog-of-war boundary, a load-bearing invariant — and no Stage-10 report has read it alongside the other 89.
This assessment's own probe (§7) supports the fix but is not an integration review → **finding B-1** (§0).
### 2.4 NFR-1510 — dependency lock
### 2.5 NFR-2830 — test-relevance audit
### 2.6 Documentation verified

## 3. Closure of REV-REL-002 and REV-REL-001 findings

## 4. Deviations

## 5. Residual risks and open backlog

## 6. LAN trust model

## 7. End-to-end smoke

## 8. Assessment

## 9. Records that would flip on a GO
