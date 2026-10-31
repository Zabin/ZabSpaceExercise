[↑ Docs index](../INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md) ·
[Release plan](../feature-planning/01-release-plan.md) · [Previous assessment (REV-REL-002)](release-assessment-release-candidate-1.md) ·
[First assessment (REV-REL-001)](release-assessment-fs-tracked-baseline.md)

# Release Assessment — Release Candidate 5 (whole repository)

> **Document ID:** REV-REL-003
> **Skill:** `11-release-readiness` (fresh session, higher-tier model at the owner's request; took no part
> in implementing, verifying, integration-reviewing or training-reviewing any package)
> **Date:** 2026-10-31
> **Commit assessed:** `f7cdc6d` (branch `claude/release-assessment-2`, tip = `origin/claude/release-candidate-5`)
> **Status:** Final (advisory). Evidence gathered by this session; nothing taken from summaries.
> **Decision owner:** the project owner. This document is advisory. **No baseline record was flipped.**

## 0. Recommendation (summary)

**NO-GO as the candidate stands, converting to GO on three procedural conditions (§8): B-1 `IP-1088` outside
every integration review; B-2 the learner-walkthrough gate is not current (three training/vignette commits
after the re-check) plus one open Manual-impact item; B-3 three unbuilt partials with no recorded bucket move.**
No code defect blocks: 90/90 `VERIFIED`; unfiltered 2165 (2161 pass / 4 skip), non-browser 2123 (2118 / 5),
browser 42 (42 / 0), all exit 0; same green on the latest dependency set and on `requirements.lock`; NFR-1510
met (re-pin advisable); NFR-2830 met with Low findings; REV-REL-001 and REV-REL-002 blockers closed by delivery.
Owner decisions needed: B-3, `BL-0388` (O-1), dormant role scoping (O-2), and optionally recorded deferral of
B-1/B-2.

## 1. Scope audit

### 1.1 Package ledger (recounted from the Master Build Plan table, not from summaries)

90 package rows, 90 distinct ids, **90 `VERIFIED`**, 90 VR files. Since REV-REL-002 (84 rows, 83 `VERIFIED`,
`IP-1160` `BLOCKED`) six packages were added and `IP-1160` was authorized, built and verified:

| Package | Feature (FS) | VR | Integration coverage |
|---|---|---|---|
| `IP-1160` Role-scoped command enforcement | FS-116 (`FEAT-3500`, `FR-3510`/`FR-3520`) | `VR-1160` v3.0 | RC-3 delta |
| `IP-1083` Rewind keeps future White injects (`BL-0284`) | FS-106 | `VR-1083` | RC-3 delta |
| `IP-1084` Fog-correct controller notices (unreviewed H-1) | FS-106, FS-123 | `VR-1084` | RC-3 delta |
| `IP-1085` Jam check follows delivery path (unreviewed H-2) | FS-129, FS-102 | `VR-1085` | RC-3 delta |
| `IP-1086` Authoring boundary validation (unreviewed H-3, M-1, M-3) | FS-131, FS-119, FS-117 | `VR-1086` | RC-3 delta |
| `IP-1087` Pending-approval orders survive resume (unreviewed M-2) | FS-127, FS-110 | `VR-1087` | RC-3 delta |
| `IP-1088` Fog-correct activity feed (RC-3 `M-1`) | FS-106 | `VR-1088` v3.0 (header stale, V-1) | **none (B-1)** |

### 1.2 One row per FS-tracked Feature (delta from REV-REL-002 §1.2; unchanged rows hold as recorded there)

Every row of REV-REL-002 §1.2 that read "Yes (B1)" now has integration coverage (the unreviewed-packages
report, whose Highs the RC-3 delta closed). Changes:

| Feature | Was (REV-REL-002) | Now |
|---|---|---|
| **FS-116 Role-Scoped Command Catalog** (`FEAT-3500`, Must, Release 1) | `IP-1160` `BLOCKED`, unbuilt → B2 | **Delivered**: `IP-1160` `VERIFIED` (v3.0), RC-3 delta "Holds, with the two known deviations" (`BL-0388`: checked at submission not execution; omitting `seat` skips the gate — owner decision pending). **Dormant in shipped content:** no shipped vignette declares `roles_needed` and the Creator cannot save one (`BL-0390`), so the gate only acts on a hand-edited YAML. Driven in-process with a `roles_needed` added: a `bus` seat issuing `isr.collect_now` → `role_scope_out_of_scope`; same order with `seat` omitted passes the role gate. The manuals say so plainly (`BLU-15`: "In the 19 shipped vignettes nothing is crewed … the field is a rehearsal of crew discipline, not a lock"; `12c`). → finding **D-1** |
| FS-106 White Cell Dashboard | Yes; `BL-0284` Medium open | `IP-1083`, `IP-1084`, `IP-1088` added; `BL-0284` **fixed** (§3) |
| FS-117 / FS-119 / FS-131 | Yes (B1); `BL-0139`/`BL-0140` open | `IP-1086` hardens authoring input; `BL-0139`, `BL-0140` still open (§5) |
| FS-127 / FS-110 | Yes (B1) | `IP-1087` added |
| FS-129 / FS-102 | Yes (B1) | `IP-1085` added |
| FS-121 Ephemeris/TLE export | Yes except `FR-7450` | unchanged — `FR-7450` still unbuilt (§4) |
| FS-131 | `FR-5310` template clause unbuilt | unchanged (§4) |
| FS-135 | `NFR-3810` unbuilt | unchanged (§4) |

Pre-pipeline foundation (P0–P8) and the training corpus (`FEAT-11100`/`11300`) are as REV-REL-002 recorded,
plus the training fixes in §2.6.

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
### 2.4 NFR-1510 — dependency lock (procedure run now, at release)

`requirements.lock` exists at the root: 33 exact pins (direct and indirect), CPython 3.13.17, with the install
recipe in its header; `pyproject.toml` declares floors equal to the locked direct pins.

1. **Latest versions checked** — fresh venv, `pip install -U -e ".[content,ui,dev]"` through the proxy (TLS
   verified), `pip freeze --exclude-editable`. **Five packages moved** (all patch/minor):
   `hypothesis 6.170.9 → 6.170.14`, `opentelemetry-api 1.45.1 → 1.45.2`, `pydantic 2.14.1 → 2.14.2`,
   `pydantic_core 2.50.1 → 2.50.2`, `pytest 9.1.1 → 9.2.0`. Everything else resolved to the locked version.
2. **Tried** — unfiltered suite in that venv (browser tests ran: 42 in the junit, Chromium `/opt/pw-browsers`):
   **exit 0, 2165 tests, 2161 passed, 4 skipped** (the same four data-dependent skips), 1 warning (Starlette's
   `httpx` test-client deprecation, REV-REL-002 N7, still open).
3. **Fix / hold back** — nothing to fix; nothing held back.
4. **Locked set validated** — second fresh venv, `pip install -r requirements.lock && pip install --no-deps -e .`,
   unfiltered suite: **exit 0, 2165 tests, 2161 passed, 4 skipped** (browser tests included), installed set identical to the 33 pins (`pip freeze` diff empty).
5. **Recommendation:** the newer set passes completely, so the lock *should* be re-pinned to it before tagging
   (raise the `pydantic`, `hypothesis`, `pytest` floors, re-freeze, re-validate in a fresh venv). This
   assessment did **not** change the lock: per the skill the lock is produced by a `07`→`08` package, and the
   current lock is itself validated, so re-pinning is a hygiene condition, not a blocker. Route `07`→`08`
   (`BL-0379` procedure).

**NFR-1510: met** — every dependency locked to an exact version, latest versions checked and tried, the locked
set validated in a fresh venv; one patch-level refresh available.

### 2.5 NFR-2830 — test-relevance audit (whole suite, read-only)

Source: `python3 -m pytest --origin-report` (exit 5 — "no tests ran", the report-only mode, REV-REL-002 RC `L-3`,
still open) and the unfiltered junit.

| Check | Result |
|---|---|
| Tests with no origin | **0** (`== untagged tests: 0 ==`; `test_origin_allowlist.txt` empty) |
| Tests citing an ID absent from the baseline | **0** (the suite's own gate, green) |
| Tests citing a retired/superseded requirement | **0 detectable**; retirement marking is still undefined (`BL-0317`), so the check is existence-only → `04` |
| Duplicate checks | No new true duplicates found; the pairs REV-REL-002 examined are unchanged. Semantic duplicates are not machine-detectable |
| **R-2: tests that never execute their assertion** | **4** — the four unfiltered skips (§2.1) skip on every run because the vignette they pick lacks the precondition; their checks (`FR-6220` row 10, sensor/pass-booking release, operator `success_prob` override) are therefore unverified by them. → `07` (pick a vignette that meets the precondition, or build the fixture) |
| Requirements with no test naming them | **33** (was 38). Now tested: `FR-3510`, `FR-3520` (IP-1160), `FR-6220`, `FR-11420`, `NFR-2300` |

**The 33 untested requirements, classified and routed:**

| Class | Requirements | Disposition / route |
|---|---|---|
| **A. Unbuilt** | `FR-7450` (ISO-8601 export bounds, Should), `NFR-3810` (retired-document check) | Deviations §4 → owner, then `05`/`06` |
| **B. Built, tests exist but tagged to a sibling ID** (unchanged since REV-REL-002 — its retag recommendation was not acted on) | `FR-1140`, `FR-3410`, `FR-7110`, `FR-7350`, `NFR-2400`, `NFR-2500`, `NFR-2600`, `NFR-2800`, `NFR-3200` | → `07` one retag package (Low) |
| **C. Verified by inspection / demonstration / analysis** | `FR-11110`, `FR-11120`, `FR-11210`, `FR-11310`, `FR-11320`, `FR-11410`, `FR-4710`, `FR-4720`, `FR-6110`, `FR-6610`, `NFR-1200`, `NFR-1400`, `NFR-1510` (§2.4), `NFR-2000`, `NFR-2100`, `NFR-2900`, `NFR-3000`, `NFR-3040`, `NFR-3060`, `NFR-3300`, `NFR-3500`, `NFR-3600` | Correctly test-less; → `04`: let the origin report exclude non-Test verification methods (REV-REL-002 recommendation, still open) |

**NFR-2830: met with findings** — zero untagged, zero unknown-ID tests; findings R-2 (4 permanently-skipped
tests), class B retag (9), class A unbuilt (2), retirement marking undefined. None is High.
### 2.6 Documentation verified (skill step 3b)

| Evidence item | Result | Detail |
|---|---|---|
| Learner-walkthrough gate report exists and walked every role | **Yes** | [REV-TRN-010](training-review-release-walkthrough.md) (1 High, 10 Medium, 5 Low) and its re-check [REV-TRN-011](training-review-release-walkthrough-recheck.md) at `461d43a`: White/Blue/Red "Yes" (newcomer can finish); F1 (the High) **Closed**; **0 High, 5 Medium (N1–N5), 3 Low (L1–L3)** open at that commit. [REV-TRN-009](training-review-training-basics-n2-fix.md) closed REV-REL-002's training-basics finding (no Critical/High). |
| The review is **current** (names a commit at/after the last change to `docs/training/` or vignette YAML) | **No** | Three commits after `461d43a` change exactly those paths: `8de366b` (N1, N2, N4, L2, L3 prose), `e2e1342` (N3 tutorial YAML in `04`/`05`/`07`/`mt-sigint-geolocate` + a browser test), `d86c845` (N5, L1, L2: `learn-intermediate-recovery.yaml`, `11`/`15`/`16` + tests). No `09-training-manual-review` has read them → **finding B-2**. |
| This assessment's own learner drive of the changed steps (supporting evidence, not a substitute for the gate) | **All hold** | **N1** (`04` Step 7): `training-basics` Seed 1, Red observe → jam → cyber `seize_c2`, Blue telemetry by minute: `bus mode = SAFE_MODE; payload disabled` and `payload.snr_db … [RED]` from minute 1; `cdh.fsw_error_count` YELLOW at 3 min, RED by 10 min; `cdh.cmd_reject_count` RED by 20 min — matches "at once … a few minutes later". The panel heading `Subsystem log (symptoms — diagnose the cause yourself)` exists (`index.html:716`). **N2**: no "Order panel"/"Order queue" left in `docs/training/`; `03`, `13a` name **Satellite command**, `14a` names **Command queue**, both real headings (`index.html:385`, `:586`). **N3**: the four tutorials' blocked steps now say *Issue greyed out, red preview, `no_command_station`*, no mid-exercise Force add (YAML read); `test_console_shows_the_blocked_previews_the_steps_describe` (browser) green. **N4**: glossary has ISR, EO/SAR, SDA, SATCOM, PNT/GNSS, EW, TT&C, FSW, SoC, LEO/MEO/GEO/HEO, ASAT, SGP4, ML/MD; `13`/`14` link it. **N5**: driven literally over HTTP on Seed 1 — `RED-RADAR` observe, +10m ×2, engage `mrbm_kkv`, +10m ×2: `coa-russia-md` `destroy_isr` **true**, `coa-china-md` `kill_isr` **true**; the playbooks now call the kill chance-based with the hitting order (test `test_coa_md_kill_is_chance_based_…` green, incl. "cyber first misses on Seed 1"). **L1** (`learn-intermediate-recovery`): `test_recovery_objective_flips_exactly_at_the_deadline_not_before` asserts unmet at T+44 min with the bus nominal, met at T+45 min; YAML step 5 says so. |
| Matrix coverage (§15.1) for the scope | **Complete except one stale row** | Creator (`12b`), bulk import, save-as-scenario (`12d`), Compare panel (`12d`), space-weather `index_series` (`12d`), missed-salvo charge (`RED-5`) are now covered — so `BL-0268`, `BL-0272`, `BL-0276`, `BL-0283`, `BL-0286` are **done in the tree but still open in the backlog** (bookkeeping). **`BL-0271` is genuinely open:** `10a` §10.5 row 8 still says "On a ground radar keep `auto` … The radar modes are not listed here", but since `IP-1223` the console's Mode list is built from the tasked sensor and offers `fence`/`dish` for a radar (`app.js` `BEAM_MODES_BY_TYPE`, `beamModesForSensor`). Low, → `08-training-manual-authoring`. |
| Tutorials machine-verified | **Green** | `test_vignette_tutorials.py` 115/115 in the unfiltered run (§2.1). |
| No open Manual-impact item for the scope | **Fails (one Low)** | `BL-0271` above; the other five Manual-impact rows are stale. |

**Result: documentation is *not verified* to the step-3b standard** — the gate review is not current (B-2) and
one Manual-impact item is open (`BL-0271`). The substance is good: every changed step this assessment drove
behaves as written, and nothing found here is High.

## 3. Closure of REV-REL-002 and REV-REL-001 findings — with evidence

### 3.1 REV-REL-002 (release candidate 1, 2026-10-25, NO-GO)

| Item | Status now | Evidence |
|---|---|---|
| **B1** — 40 `VERIFIED` packages never inside an integration review | **Closed** | [integration-review-unreviewed-packages.md](integration-review-unreviewed-packages.md) scoped exactly those 40 (+`IP-1082`), found 3 High; `IP-1084`/`1085`/`1086` fixed them and the [RC-3 delta](integration-review-rc3-delta.md) §4.1 records H-1..H-3 **Closed** with probes. The same gap has re-opened at size one: `IP-1088` (→ **B-1**) |
| **B2** — `FEAT-3500` unbuilt, `IP-1160` unauthorized, no descope recorded | **Closed by delivery** | `IP-1160` authorized, `VERIFIED` (`VR-1160` v3.0), RC-3 delta scope. Two owner-decision deviations remain (`BL-0388`, §4). The B2 *recording* half for the partials (`FR-7450`, `FR-5310` clause, `NFR-3810`) is **not done**: `01-release-plan.md` is unchanged since before RC-1 (last commit `9b491a4`) → **B-3** |
| Medium `BL-0284` — rewind drops White's future injects | **Fixed in code** (`IP-1083`) | Live probe (`leo-isr-denial`): White future inject at T+2 h, step 10 min, rewind to T+1 min → pending count **2 before, 2 after**. Backlog row still `SCHEDULED` (bookkeeping) |
| Medium N2 — `training-basics` tutorial errors, not machine-verified | **Closed** | [REV-TRN-009](training-review-training-basics-n2-fix.md) (no Critical/High); `test_vignette_tutorials.py` now covers it (115 tests green) |
| Medium `BL-0268` — no Creator / bulk-import / save-as-scenario procedure | **Closed in the tree** | `12b-white-cell-vignette-creator.md`, `12d` (bulk import, save-as-scenario); re-check REV-TRN-011 drove Creator `12b` "as written". Backlog row still `SCHEDULED` |
| Medium `BL-0139` (OMM epoch discarded), `BL-0140` (bulk import batch abort) | **Open** | Backlog `SCHEDULED`; known deviations (§5) |
| Medium `BL-0233` (`FR-5310` template clause), `BL-0334` (link allow-list keying) | **Open** | §4 / §5 |
| N3 Low — `run-spacesim` driver stale (Chromium glob, `#o-target-pick`) | **Open** | Reproduced this run: "No Chromium found under /opt/pw-browsers/" (build is `chrome-linux64/`) |
| N4 Low — `README.md` stale (419 tests), `--host 0.0.0.0 --reload`, no trust warning, no lock install | **Open** | `README.md` lines 18, 42, 123; owned by this skill on GO (§9) |
| N5 Low — `CLAUDE.md` counts stale | **Closed** | `CLAUDE.md` line 19 states 2165 / 2161 passed / 4 skipped, matching §2.1 |
| N6 Low — `01-release-plan.md` body stale | **Open** | Line 70 still says `FEAT-3500` FRs are RTM `UNASSIGNED` |
| N7 Low — Starlette `httpx` test-client deprecation | **Open** | Warning in the latest-versions run |

### 3.2 REV-REL-001 (FS-tracked baseline, 2026-07-05, NO-GO)

Its sole NO-GO reason, **Finding 2 — `FEAT-3500` undelivered (High)**, is **closed by delivery** (above). The
backlog row `BL-0049` still reads `SCHEDULED` (stale). Its other items were closed or owner-accepted as
REV-REL-002 §3 recorded; unchanged: hot-seat fog risk `BL-0015` (owner-accepted) and the LAN trust model (§6).

## 4. Deviations (delivered differently from the plan)

| Deviation | Authorization trail |
|---|---|
| `FR-3520` role scope checked at **submission**, not at command-execution time as `FR-3520`/`FS-116` say; a rebinding applies only to later submissions; omitting `seat` skips the gate (`BL-0388`, RC-3 `M-2`, `VR-1160` `M-3`/`L-1`) | **None yet** — `NEEDS-USER`. Reviewers judged it not release-blocking; the owner must accept-and-amend (`04` edits `FR-3520`) or build (`07`) → **decision O-1** |
| **D-1** `FEAT-3500` is dormant in shipped content: no shipped vignette declares `roles_needed`; the Creator saves `roles_needed: []` (`BL-0390`) | Documented in `BLU-15`, `12b`, `12c`; no recorded owner acceptance → **decision O-2** (accept, or add a crewed vignette via `08-vignette-development`) |
| `FR-7450` (ISO-8601 export bounds, Should) not built; `FR-5310` template-reference clause unbuilt (`BL-0233`); `NFR-3810` retired-document check unbuilt (`BL-0319` decided: delete retired docs) | Disclosed in `feature-index.md`/RTM; **no bucket move recorded in `01-release-plan.md`** → **B-3** |
| Save-as-scenario omits gating rules, detectability config, space-weather series, inject schedule (`BL-0389`, RC-3 `M-3`) | `DEFERRED` — "documented v1.1 items"; the manuals say so (`12b`/`12d`) |
| Console has no control for gate approve/deny, live ROE change, manoeuvre ledger (RC-3 `M-4`) | Documented "HTTP only" in `12`/`12c`/`12d`; no owner record beyond the review's GO-conditional |
| Hot-seat hand-off not automatic (`FR-6610`, `BL-0015`) | Owner-accepted |
| AI-Red reads ground truth (`ADR-0024`) | Documented design boundary |

## 5. Residual risks and open backlog (read-only; `docs/pipeline/` untouched)

**Open backlog** (`docs/pipeline/backlog.md`, rows not `DONE`/`CLOSED`/`REJECTED`/`DEDUPED`): **82 open** —
3 High, 16 Medium, 1 Low-Medium, 61 Low, 1 priority-"C" request; **no Critical**. Note also that the live file
still holds many rows already marked `DONE` (its own rule moves them to the archive) — bookkeeping for
`00-pipeline-manager`.

| ID | Sev | What | Disposition for this release |
|---|---|---|---|
| `BL-0049` | High | `FEAT-3500` undelivered | **Stale** — delivered by `IP-1160`; close in triage |
| `BL-0292` | High | Author GDS-06..10 | **Stale** — `architecture/INDEX.md` shows GDS-06..10 authored, gates closed |
| `BL-0310` | High | Test-origin traceability (owner direction) | **Stale** — IP-1330 series delivered; 0 untagged tests |
| `BL-0388` | Medium | Role gate at submission / omitted seat | Owner decision O-1 (§4) |
| `BL-0389` | Medium | Save-as-scenario omissions | Known deviation, deferred v1.1 |
| `BL-0390` | Low-Med | Behaviour defects found while documenting (Pause/Resume resets rate; Creator seat matrix not saved; `/start` works on a Creator draft — **reproduced**: 200; junk role accepted; bulk import after Start returns `[]`; jammed command shows `executed`; Observer check reads body cell only; raw-JSON Creator errors; `mt-sigint-geolocate` `characterize_emitter` unreachable; availability objectives MET while jammed) | `DEFERRED` to `00-intake` after release; known deviations. The last two touch scoring of shipped vignettes — the owner should know |
| `BL-0139`, `BL-0140` | Medium | OMM epoch discarded; bulk-import batch abort | Known deviations (fidelity / authoring), `07` |
| `BL-0233` | Medium | `FR-5310` template clause | B-3 |
| `BL-0252`, `BL-0315` | Medium | `IN PIPELINE` — check: `BL-0315` (force edits lost on resume) was addressed by `IP-1101`/`1102` per REV-REL-002 (stale) | Triage |
| `BL-0284` | Medium | Rewind drops future injects | **Stale** — fixed (§3.1) |
| `BL-0268` | Medium | Creator etc. manual gap | **Stale** — covered (§2.6) |
| `BL-0028` | Medium | R600 citations unverified by fetch | Research-confidence caveat |
| `BL-0288`, `BL-0293`, `BL-0297`, `BL-0299`, `BL-0379`, `BL-0334` | Medium | Governance / doc scope / dependency policy (implemented) / allow-list keying | Not product defects; several stale |
| `BL-0271` | Low | Manual impact `IP-1223` — `10a` §10.5 row 8 wrong | **Open Manual-impact item** (§2.6) → `08-training-manual-authoring` |
| `BL-0272`, `0276`, `0283`, `0286` | Low | Manual-impact items | **Stale** — done in the tree (§2.6) |

**New findings of this assessment** (none Critical):

| # | Sev | Finding | Route |
|---|---|---|---|
| B-1 | High (process) | `IP-1088` (fog boundary) outside every integration review | `10-integration-review` delta on `IP-1088`, or owner acceptance |
| B-2 | High (process) | Learner-walkthrough gate not current: `8de366b`, `e2e1342`, `d86c845` unreviewed | `09-training-manual-review` delta re-check of those three commits |
| B-3 | Medium (process) | Partials (`FR-7450`, `FR-5310` clause, `NFR-3810`) still have no recorded bucket move | Owner decision, then `05-feature-decomposition` |
| D-1 | Medium | `FEAT-3500` dormant in shipped content | Owner (O-2) |
| V-1 | Low | `VR-1088` header/Result still say v2.0 RETURNED | `09-package-verification` |
| R-2 | Low | 4 tests skip on every run (never assert) | `07` |
| S-1 | Low | `load_save` accepts `save_format: 999` (unknown future format) silently — `validate_save` tests only truthiness (`manager.py:1303`, `:1385`); a `simulator_version` mismatch *is* warned | `04` (is a format check required?) then `07` |
| S-2 | Low | `BL-0271` (`10a` row 8) | `08-training-manual-authoring` |
| S-3 | Low | Lock refresh available (5 patch/minor bumps pass) | `07`→`08` |

**Residual risks shipping on a GO:** the LAN trust model (§6); hot-seat fog `BL-0015`; AI-Red truth;
role-scope gate is advisory (O-1/O-2); save-as-scenario omissions; the `BL-0390` behaviour defects (two of which
can mis-score shipped vignettes); unbounded live event log (RC `L-1`); the browser GUI covered by 42 browser
tests and this smoke, not by an exhaustive UI test.

## 6. The LAN trust model — the product's accepted security boundary (stated plainly)

**There is no authentication.** Every request names its own seat (`cell=white|blue|red|observer`, plus an
optional operator `seat`) and the server believes it. Fog-of-war is enforced server-side on every cell-scoped
response; White-only controls and Observer mutations are refused server-side — against the *asserted* seat.
Re-checked this run: a request naming `red` reads Red's scene (200); `/godview` with no cell returns truth (200);
any client sending `?cell=white` can step the clock (200); an Observer order is refused (403); a Blue `step`
is refused (403). The operator-seat role gate (`IP-1160`) is skipped by omitting `seat`.

**What a deployer must do:** run only on an isolated, trusted LAN or loopback with cooperative participants;
never expose the port to the internet or an untrusted network (bind `127.0.0.1` single-machine; bind the LAN
address only behind a host firewall limited to participants' machines); do not use `--reload` in an exercise;
install from `requirements.lock`; treat every participant as able to see ground truth and act as White; brief
participants that seat selection and operator seats are an honour system. Plain HTTP, no TLS, no audit beyond the
event log's asserted seat. Per-cell tokens are in `docs/FUTURE-WORK.md`. Sources: `ADR-0015`, `NFR-2300`,
`FR-6220`, `CLAUDE.md` "LAN trust model", `training/01` §2.1, `WCM-3`.

## 7. End-to-end smoke of the shipped app (this assessment)

`uvicorn spacesim.ui_web.server:app` on `127.0.0.1:8791`, headless Chromium
`/opt/pw-browsers/chromium-1243/chrome-linux64/chrome` (own Playwright script; the `run-spacesim` driver fails, N3).

| Drive | Result |
|---|---|
| Console as **White / Blue / Red** on `training-basics`, `leo-isr-denial`, `coa-russia-md` (9 runs): Session ▾ → Load → Start → +10m ×3 → switch cell → drill into the first fleet row | All 9 rendered: clock advanced (`06:30:01Z` / `14:30:01Z`), fleet rows 3–9 per cell (fog-sized), actor options 2–8, 19 sparklines; **0 page errors**, one console 404 (`/favicon.ico`). Server log: ~960 requests 200, **0 × 5xx** over the whole session |
| `training-basics` tutorial path (the `04` guided vignette, Red then Blue) | Red observe/jam/cyber accepted; `disable_isr` MET; Blue telemetry shows the symptoms as `04` Step 7 says (§2.6) |
| Learner playbooks `11.15`/`11.17` (Seed 1) | `destroy_isr` / `kill_isr` MET following the text literally (§2.6) |
| **Creator** | Draft session created; `creator/state` GET/PUT 200 as White, **403 as Blue**; `creator/scene` 200; step on a draft **400** "draft sessions cannot advance time"; save without `user_save_dir` → 400 with the message `12b` quotes; `/start` on a draft → **200** (`BL-0390`, known) |
| **Operator seat / role scope** (`IP-1160`) | `roles/assign` 200; `roles/scope` fog-scoped (Red asking about a Blue seat sees `bound: false`); with `roles_needed` declared (in-process) a bus seat's payload verb → `role_scope_out_of_scope`; omitted seat → gate skipped (`BL-0388`) |
| **Time bounds** | `step` 400 days → 400 naming the 366-day span; `NaN` → 400; Blue `step` → 403; ephemeris without required ids → 422 |
| **Save / resume with warnings** (`IP-1101`) | `GET /save` → self-contained (`baseline`, `content`, `save_format`, `simulator_version`); `load_save` → `{session, warnings: []}`; with `simulator_version` altered → warning "this save was written by simulator version deadbee; this is d862ef6"; as Blue → 403; `save_format: 999` → accepted silently (S-1) |
| **Activity feed fog** (`IP-1088`) | Blue downlink + Red jam + White future inject on `leo-isr-denial`: White sees both orders, the effect by template and both injects; **Blue** sees its own order and the effect as `electronic_warfare` (category, no template, no inject); **Red** sees only its own jam order; unknown cell `purple` → 400. Observer follows its designation (god view by default) |
| **Rewind keeps future injects** (`IP-1083`) | 2 pending before and after rewind |

## 8. Assessment

**Recommendation: NO-GO as the candidate stands, converting to GO on three procedural conditions. No code
defect blocks the release.** The engineering evidence is strong: 90/90 packages `VERIFIED` with VRs; every
suite green in every mode in the system interpreter, at the latest dependency versions and on the locked set;
determinism and import guard green; zero untagged tests; all allow-lists but the 38 known links empty; every
blocker of REV-REL-001 and REV-REL-002 closed by delivery; the shipped app ran end to end for White, Blue and Red
on three vignettes with zero 5xx; no open Critical or High product defect.

The release does not yet meet this skill's own gates in three places:

| # | Blocking condition | Gate | Clears when |
|---|---|---|---|
| **B-1** | `IP-1088` (changes `CellController`, the fog-of-war boundary) was built after the RC-3 delta and is inside **no** integration review | Quality gate: every delivered row needs integration coverage | A `10-integration-review` delta on `IP-1088` returns no Critical/High — **or** the owner records acceptance (this assessment's probe in §7 and `VR-1088` v3.0's are supporting evidence) |
| **B-2** | The learner-walkthrough gate is **not current**: three commits (`8de366b`, `e2e1342`, `d86c845`) changed `docs/training/` and vignette YAML after REV-TRN-011 (`461d43a`) with no independent re-review; plus one open Manual-impact item (`BL-0271`, Low) | Step 3b: review must be current; no open Manual-impact item | A `09-training-manual-review` delta re-check of those commits finds no High, and `BL-0271` is fixed or owner-deferred. This assessment drove every changed step and found them correct (§2.6), so the re-check should be short |
| **B-3** | `FR-7450`, the `FR-5310` template clause and `NFR-3810` are unbuilt with **no recorded bucket move** in `01-release-plan.md` (REV-REL-002 B2's recording half) | Step 2: deviations need an authorization trail | The owner decides; `05-feature-decomposition` records it |

**Conditions to attach to a GO** (non-blocking): owner decision O-1 on `BL-0388` (accept submission-time check
and amend `FR-3520`, or build); O-2 on D-1 (accept that role scoping ships dormant, or add a crewed vignette);
re-pin the lock to the passing newer set (S-3); fix `README.md` (N4) in the GO flip; accept the §5 residual
risks and the §6 trust model explicitly.

**Alternative the owner may choose:** record explicit deferrals/acceptances for B-1 and B-2 (the skill allows an
owner-recorded deferral listed under Deviations) and decide B-3 — the evidence in this document then supports GO.

## 9. Records that WOULD flip on a GO (none touched by this assessment)

| Record | Change |
|---|---|
| `docs/feature-planning/01-release-plan.md` | Mark the Prototype, MVP, Release 1 and Release 2 buckets released at the GO commit; record the B-3 bucket moves for `FR-7450`, `FR-5310` clause, `NFR-3810`; fix N6 (line 70 `FEAT-3500` "UNASSIGNED"; other stale body text) |
| `ROADMAP.md` | Add a "Release 1 — released" status entry dated at GO with the commit; update this assessment's entry with the owner's decision |
| `CLAUDE.md` | Status line: released at the commit (counts already current: 2165 / 2161 passed / 4 skipped; non-browser 2123 / 5; browser 42) |
| `README.md` | Status and counts (419 → 2165); install from `requirements.lock`; LAN section: drop `--reload`, add the §6 trust warning |
| `docs/INDEX.md`, `docs/feature-planning/INDEX.md` | Point at this assessment as the release record |
| `docs/implementation/00-master-build-plan.md` | Summary line naming the release commit (package statuses unchanged, 90 `VERIFIED`) |
| `requirements.lock` / `pyproject.toml` | Only if the re-pin (S-3) is done first by `07`→`08` |
| This document | Date-stamp the baseline and record the owner's GO |

Commit as `docs(release): release candidate 5 — assessment + baseline update` at that time.

## 10. Pipeline position

Stage 11 (final). **Next step:** owner decides B-3, O-1, O-2 (and whether to defer B-1/B-2); then
`10-integration-review` on `IP-1088` and `09-training-manual-review` on the three post-recheck training commits
(both small, independent, can run in parallel); then a short delta of this skill or the owner's GO on this
document plus those two reports.
