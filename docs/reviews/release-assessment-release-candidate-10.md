[↑ Docs index](../INDEX.md) · [Master Build Plan](../implementation/00-master-build-plan.md) ·
[Release plan](../feature-planning/01-release-plan.md) · [Previous assessment (REV-REL-003)](release-assessment-release-candidate-5.md) ·
[REV-REL-002](release-assessment-release-candidate-1.md) · [First assessment (REV-REL-001)](release-assessment-fs-tracked-baseline.md)

# Release Assessment — Release Candidate 10 (whole repository)

> **Document ID:** REV-REL-004
> **Skill:** `11-release-readiness` (fresh session, higher-tier model at the owner's request; took no part
> in implementing, verifying, integration-reviewing or training-reviewing any package)
> **Date:** 2026-10-31
> **Commit assessed:** `cfcf47f` (branch `claude/release-assessment-3`, tip = `origin/claude/release-candidate-10`)
> **Status:** Final. **GO declared by the owner, 2026-11-01** (see the final-confirmation addendum below; baseline flipped on `claude/release-flip`). Originally advisory. Every number below was produced by this session; nothing is taken from summaries.
> **Decision owner:** the project owner. This document is advisory. **No baseline record was flipped.**

## 0. Recommendation (summary)

**NO-GO on the letter of the skill's documentation gate (step 3b); GO once the owner either records two
small deferrals or has two small fixes made (§8, conditions C-1 and C-2). No code, test, dependency,
verification or integration item blocks.**

- 94 packages, 94 `VERIFIED`, 94 VRs; the integration-review union covers **94 of 94**.
- Suites at `cfcf47f`, run once per mode, real exit codes: unfiltered **2244 / 4 skipped, exit 0**;
  `-m "not browser"` **2202 / 5, exit 0**; `-m browser` **42 / 0, exit 0** (§2.1). Same green on the
  latest dependency set and on `requirements.lock`.
- **NFR-1510: met.** The latest version of every dependency is identical to the lock (no package moved); both
  venvs green.
- **NFR-2830: met with Low findings.** 0 untagged tests; 32 requirements with no test naming them, all
  classified (§2.5).
- All three REV-REL-003 blockers are closed in substance (§3). **But the gate re-opens at small size:**
  - **C-1:** the learner-walkthrough review (REV-TRN-012, `92c56c8`) is not current. Three commits after it
    changed `docs/training/` and vignette YAML (`78417d6`, `96b313c`, `62ef8a0`). I spot-checked them. M-1, L-1
    and L-2 hold. The L-3 fix added a false sentence (F-1, Low).
  - **C-2:** one Manual-impact item is still open. `BL-0286`: the White manual does not describe the
    **⚖ Compare** panel. REV-REL-003 wrongly recorded it as done.

## 1. Scope audit

### 1.1 Package ledger (recounted from the Master Build Plan table)

**94 rows, 94 distinct ids, 94 `VERIFIED`** (status column parsed; no `COMPLETE`/`READY`/`BLOCKED`/`IN
PROGRESS`). `ROADMAP.md` has 94 package rows, all `VERIFIED`. **Every package has a `VR-` file**: 94 VR ids,
none missing, none orphaned. Since REV-REL-003 (90 `VERIFIED`) four packages were added:

| Package | Closes | VR | Integration coverage |
|---|---|---|---|
| `IP-1089` ISO-8601 span bounds | REV-REL-003 B-3 (`FR-7450`) | `VR-1089` v2.0 **VERIFIED** (v1.0 RETURNED kept as history) | RC-7 |
| `IP-1092` Retired-documents check | B-3 (`NFR-3810`) | `VR-1092` v2.0 | RC-7 |
| `IP-1093` Release lock re-pin | S-3 | `VR-1093` | RC-7 |
| `IP-1094` `save_format` gate, Chromium lookup | S-1, N3 | `VR-1094` v2.0 | RC-7 |
| `IP-1088` Fog-correct activity feed (already `VERIFIED` at REV-REL-003) | RC-3 `M-1` | `VR-1088` v3.0 | **RC-7 (closes B-1)** |

### 1.2 Features (delta from REV-REL-003 §1.2; unchanged rows hold as recorded there)

`docs/features/feature-index.md`: 38 FS rows. **36 `Done`**, plus 2 `Scoped, not authorized` (`FS-108`,
`FS-202`; outside every bucket, as before). Changes:

| Feature | Was (REV-REL-003) | Now |
|---|---|---|
| FS-121 Ephemeris/TLE export | `FR-7450` unbuilt (B-3) | **Delivered.** `IP-1089` is `VERIFIED` and RC-7 reviewed it. The status header was moved to Done in `a786fca`. Probed (§7): ISO `Z` and `+00:00` bounds give 200; a non-ISO value, an out-of-range span or an oversampled span give a 400 with the reason. |
| FS-135 Doc-integrity | `NFR-3810` unbuilt (B-3) | **Delivered** (`IP-1092`). The check is green but has nothing to check on the real tree: no document is retired, and `doc_integrity_allow_retired.txt` is empty. This is RC-7 `L`, carried. |
| FS-131 Load-time validation | `FR-5310` template clause unbuilt (B-3) | **Amended, not built.** `FR-5310` now says "the content model has no template library and no template reference to validate (`BL-0233` option A, `ADR-0036`)". Starter snippets are published in `12b` (option D). I probed the snippets: they load, start and play (§7). |
| FS-116 Role-scoped commands | `BL-0388` decision pending (O-1) | **Owner accepted as v1** (`BL-0388` `DONE`, run #264). `FR-3520` was amended in run #265. The feature is still dormant in shipped content: 0 of 19 vignettes declare `roles_needed` (D-1, §4). |
| FS-106 White Cell dashboard | `IP-1088` unreviewed | RC-7 reviewed it. The fog holds (§7). |

**Unauthorized drift: none found.** Every deviation in §4 has an authorization trail.

## 2. Evidence

### 2.1 Test suite: one run per mode, real exit codes, `--junitxml` on every run

System interpreter CPython 3.13.17, commit `cfcf47f`, `-p no:cacheprovider`, Chromium `/opt/pw-browsers`.

| Mode | Exit | Tests (junit) | Failures/errors | Skipped | Expected |
|---|---|---|---|---|---|
| unfiltered | **0** | 2244 | 0 / 0 | 4 | 2244 / 4: match |
| `-m "not browser"` | **0** | 2202 | 0 / 0 | 5 | 2202 / 5: match |
| `-m browser` | **0** | 42 | 0 / 0 | 0 | 42 / 0: match (§2.1a) |

2202 + 42 = 2244. **The four unfiltered skips** are the same data-dependent tests as before:
- `test_activity_fog_matrix::test_row_10_neutral_owned_effect_white_only`
- two in `test_defensive_audit_2026` (`…releases_sensor_booking`, `…releases_pass_booking`)
- `test_derived_probabilities::test_jam_ignores_operator_success_prob_override`

**The fifth non-browser skip** is the partial-collection guard
`test_test_origins::test_the_committed_matrix_test_column_equals_the_generated_one`. It runs and passes in the
unfiltered run.

**Permanent gates, by name, from the unfiltered junit (all passed, none skipped):**

| Gate | Passed |
|---|---|
| `test_determinism` | 6 / 6 |
| `test_import_guard` | 8 / 8 |
| `test_doc_integrity` (links, INDEX listings, ledgers, retired documents) | 23 / 23 |
| `test_vignette_tutorials` | 115 / 115 |
| test-origin tests (`test_origin*`, `test_test_origins`) | 217 / 217 |

**Allow-lists (non-comment entries):**

| List | Entries |
|---|---|
| `test_origin_allowlist.txt` | **0** |
| `doc_integrity_allow_indexes.txt` | **0** |
| `doc_integrity_allow_ledgers.txt` | **0** |
| `doc_integrity_allow_retired.txt` | **0** |
| `doc_integrity_allow_links.txt` | **38** (unchanged since REV-REL-003; these lists only shrink) |

The `CLAUDE.md` status line says 2244 tests / 2240 passed / 4 skipped, which matches.

### 2.1a Browser mode
`-m browser` really drove Chromium: 42 tests executed, 0 skipped, 77.6 s (junit `time`), including the two console tutorial checks in `test_vignette_tutorials.py` (blocked-step previews, L-1) and the console-rule tests. Chromium is found via `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.

### 2.2 Verification Reports

**94 of 94 packages have a VR, and none is missing.** I spot-read three:
- `VR-1089` v2.0 **VERIFIED**. F1 Medium (stale manuals) is closed.
- `VR-1094` v2.0. Its Documentation audit passed.
- `VR-1088`. **V-1 is still open (Low):** the header still reads `Version: 2.0`,
  `Produces: … COMPLETE → IN PROGRESS … (not VERIFIED)`, and its first `## Result` says **RETURNED**. The v3.0
  VERIFIED section is appended below. The verdict is real; the report's top misleads → `09-package-verification`.

### 2.3 Integration coverage: derived from each report's scope line

| Report | Scope (explicit list) | In-ledger ids | Headline |
|---|---|---|---|
| [18-package tranche](integration-review-18-package-tranche.md) | `IP-1010`…`1151`, `2010`, `3010` | 18 | clean |
| [Tranche 2](integration-review-tranche-2-white-controls-saves-test-origins.md) | `IP-1068`, `1101`, `1091`, `1069`, `1330`, `1350`, `1340`, `1331`–`1333` | 10 | 0 C / 0 H |
| [Tranche 3](integration-review-tranche-3-release-push-remediation.md) | `IP-1311`, `1102`, `1072`–`1075`, `1103`, `1334`, `1335` | 9 | — |
| [Release candidate 1](integration-review-release-candidate-1.md) | Tranche 3 + `IP-1076`–`1081` | 15 | 0 C / 0 H / 3 M |
| [Unreviewed packages](integration-review-unreviewed-packages.md) | §1.2 groups A–F (40) + `IP-1082` | 41 (+3 named in its group-G note) | 0 C / 3 H (closed by RC-3) |
| [RC-3 delta](integration-review-rc3-delta.md) | `IP-1082`–`1087`, `IP-1160` | 7 | 0 C / 0 H / 4 M |
| [**RC-7 delta**](integration-review-rc7.md) | `IP-1088`, `1089`, `1092`, `1093`, `1094` + non-package changes `8833b91..ad727c3` | 5 | **0 C / 0 H / 3 M / 5 L; GO** |

**Script union against the MBP: 94 of 94 covered. No package sits inside no review's scope.**

**Changes after the last integration review (`ad727c3..cfcf47f`) under `spacesim/`, the lock, `pyproject.toml` or
`README.md`:** only the tutorial `expect:` strings in three vignette YAMLs and the matching
`test_vignette_tutorials.py` assertions (`62ef8a0`). Everything else is docs or pipeline. No production code has
changed since RC-7.

### 2.4 NFR-1510: dependency lock (procedure run now)

`requirements.lock` has 33 exact pins, CPython 3.13.17, and its install recipe in the header. `IP-1093` re-pinned
it today. The `pyproject.toml` floors equal the locked direct pins (`pydantic>=2.14.2`, `pytest>=9.2.0`,
`hypothesis>=6.170.14`, …).

1. **Latest versions checked.** Fresh venv, `pip install -U pip`, then `pip install -U -e ".[content,ui,dev]"`
   through the agent proxy with TLS verified (pip `cert` = `/root/.ccr/ca-bundle.crt`). Then
   `pip freeze --exclude-editable`. **The diff against the lock is empty: no package moved.**
2. **Tried.** Unfiltered suite in that venv: **exit 0, 2244 tests, 0 failures/errors, 4 skipped.** The browser
   tests ran inside it. The determinism and import-guard gates all passed (junit).
3. **Fix / hold back.** Nothing to fix. Nothing held back.
4. **Locked set validated.** Second fresh venv: `pip install -r requirements.lock && pip install --no-deps -e .`.
   The `pip freeze` diff against the lock is empty. Unfiltered suite: **exit 0, 2244 tests, 0 failures/errors, 4 skipped** (browser tests included; determinism 6/6, import guard 8/8).
5. **Carried note (Low, N7):** both venvs emit Starlette's `StarletteDeprecationWarning` ("Using `httpx` with
   `starlette.testclient` is deprecated; install `httpx2`"). This is a warning, not a failure. It is the next
   lock refresh's likely breakage → `07`.

**NFR-1510: met.** Every dependency is locked to an exact version. The latest versions were checked and tried
and are identical to the lock. The locked set was validated in a fresh venv.

### 2.5 NFR-2830: test-relevance audit (whole suite, read-only)

Source: `python3 -m pytest --origin-report` (exit 5, the report-only "no tests ran" mode, `BL-0386`) plus the
junit files and an AST pass of my own.

| Check | Result |
|---|---|
| Tests with no origin | **0** (`== untagged tests: 0 ==`; allow-list empty) |
| Tests citing an ID absent from the baseline | **0** (the suite's own gate, green) |
| Tests citing a retired/superseded requirement | **0 detectable.** `requirements-change-log` and the FR/NFR files mark nothing retired. Retirement marking for requirements is still undefined (`BL-0317`) → `04` |
| Duplicates | An AST hash of every `test_*` body found **one** identical pair: `test_origin_retag.py::test_each_listed_retag_is_in_place` / `…_browser_retag_is_in_place`. They are parametrized over different tables, so this is not a duplicate check. No semantic duplicates were found by name review. |
| **R-2 (carried): tests that never execute their assertion** | **4**, the four unfiltered skips. Their checks (`FR-6220` row 10, sensor/pass-booking release, the operator `success_prob` override) stay unverified by them → `07` |
| Requirements with no test naming them | **32** (was 33). `FR-7450`, `NFR-3810` and `NFR-1510` are no longer listed. `FR-6230` and `FR-7240` are new rows. |

The RTM agrees. It has 163 requirement rows (115 FR + 48 NFR), and 32 of them have `UNASSIGNED` in the generated
Test column, the same 32.

**The 32, classified and routed:**

| Class | Requirements | Disposition / route |
|---|---|---|
| **B. Built; tests exist but cite a sibling ID** | `FR-7240` (`save_format` refusal: `test_save_format_gate.py` cites `FR-7230`/`IP-1094`), `FR-6230` (activity-feed fog: `test_activity_fog_matrix.py` and `IP-1088` tests cite `FR-6220`). Carried: `FR-1140`, `FR-3410`, `FR-7110`, `FR-7350`, `NFR-2400`, `NFR-2500`, `NFR-2600`, `NFR-2800`, `NFR-3200` | → `07`: one retag package (Low). The two new rows arrived with requirements pass 5 after their tests were written. |
| **C. Verified by inspection / demonstration / analysis** | `FR-11110`, `FR-11120`, `FR-11210`, `FR-11310`, `FR-11320`, `FR-11410`, `FR-4710`, `FR-4720`, `FR-6110`, `FR-6610`, `NFR-1200`, `NFR-1400`, `NFR-2000`, `NFR-2100`, `NFR-2900`, `NFR-3000`, `NFR-3040`, `NFR-3060`, `NFR-3300`, `NFR-3500`, `NFR-3600` | Correctly test-less → `04`: let the origin report exclude non-Test verification methods (open since REV-REL-002) |
| A. Unbuilt | none | — |

**NFR-2830: met with Low findings.** There are zero untagged and zero unknown-ID tests. The open findings are R-2
(4 skips that never run), the class-B retag (11, 2 of them new), and the undefined retirement marking. None is
High.

### 2.6 Documentation verified (skill step 3b)

| Evidence item | Result | Detail |
|---|---|---|
| A learner-walkthrough gate report exists, walked every role, has no open High | **Yes** | [REV-TRN-012](training-review-final-rc8.md) at `92c56c8`: White / Blue / Red "Yes, could finish unaided". **0 High, 1 Medium (M-1), 3 Low (L-1..L-3).** All REV-TRN-011 findings are closed. |
| The review is **current** (it names a commit at or after the last change to `docs/training/` or vignette YAML) | **No** | Three commits after `92c56c8` change those paths: `78417d6` (`11` §11.15/§11.17 ordered Red recipe, M-1), `96b313c` (`12d` WCM-22 echoed values L-2; `15` §15.3 wording L-3), `62ef8a0` (tutorial `expect:` in `04`/`05`/`07` YAML + `11`, L-1). No `09-training-manual-review` has read them → **C-1** |
| This assessment's spot-check of those three commits (owner-requested; supporting evidence, not the gate) | **M-1, L-1, L-2 hold; L-3 introduced F-1** | **M-1** (in-process, Seed 1, literally as `11` now says: observe, +10m ×2, engage, +10m until ✓, then jam + cyber): `coa-china-md` `kill_isr` ✓ at the first +10m check after the engage (T+30) and `safe_satcom` ✓; the trap the text warns about (jam + cyber queued right after the engage) leaves `kill_isr` ✗. `coa-russia-md` gives `destroy_isr` ✓ the same way. **L-1** (headless Chromium, Blue, `co-orbital-threat-escort`, `BLUE-HVA` → maneuver with the form's defaults): the preview reads `✗ No access window in the planning horizon — wait for the next pass.` and Issue is disabled, which is the text the YAML now leads with. **L-2:** live refusals are `save_format '2' …`, `save_format True …`, `save_format None …`, `save_format 3 …`, exactly as WCM-22 now quotes. **L-3 → F-1 (Low, new):** `15` §15.3 now lists "the matrix coverage check (every verified FS spec appears in §15.1)" among the *automated* gates. **No such test exists.** No test file reads `15-manual-traceability.md`; it is a manual step of `09-training-manual-review` (`SKILL.md` line 52). The edit also left the next sentence's "it" pointing at the wrong noun. → `08-training-manual-authoring` |
| Matrix coverage (§15.1) | **Complete** | Script: all 36 `Done` FS specs appear in §15.1/§15.1a. Every VR in scope that I read has a passed Documentation audit. |
| Tutorials machine-verified | **Green** | `test_vignette_tutorials.py` 115/115 in the unfiltered run. |
| No open Manual-impact item for the scope | **Fails (one Low)** | **`BL-0286` is `SCHEDULED`:** the `IP-1067` ⚖ **Compare** panel ("truth beside each cell's picture", `index.html` line 661, `GET /controller_view`) has no procedure in the White manual. WCM-6 "Monitor both sides" does not mention it. The only hit in `docs/training/` is one row of the visibility table in `12d` (line 168). REV-REL-003 §2.6 recorded this item as "covered (`12d`)", which **was wrong**. `BL-0271`/`0272`/`0276`/`0283` are genuinely closed: `10a` row 8 now builds the Mode list from the sensor. → **C-2** |

**Result: documentation is *not verified* to the step-3b standard.** The gate review is not current (C-1) and one
Manual-impact item is open (C-2). The substance is good: every role can finish unaided per REV-TRN-012, and the
three post-gate commits behave as written except for one false sentence (F-1).

## 3. Closure of earlier blockers and findings, with evidence

### 3.1 REV-REL-003 (release candidate 5, NO-GO-for-now)

| Item | Status | Evidence |
|---|---|---|
| **B-1** `IP-1088` inside no integration review | **Closed** | [RC-7](integration-review-rc7.md) scope line names `IP-1088`. It reports 0 C / 0 H and a 19-vignette activity-feed fog matrix. My union is 94/94 (§2.3). My own probe holds (§7). |
| **B-2** training fixes lacked an independent re-review; `BL-0271` open | **Closed as stated, re-opened at smaller size** | REV-TRN-012 re-reviewed `8de366b`/`e2e1342`/`d86c845`/`5f1b34a`/`92c56c8` and found no High; all roles finish. `BL-0271` is fixed. Three later commits are unreviewed → **C-1**. A different item, `BL-0286`, is open → **C-2**. |
| **B-3** `FR-7450` / `FR-5310` clause / `NFR-3810` unbuilt, no bucket move | **Closed** | Built: `IP-1089` (`FR-7450`) and `IP-1092` (`NFR-3810`), both `VERIFIED` and RC-7-reviewed. `FR-5310` was amended (option A) and starter snippets were added (option D, probed §7). Nothing left to move, so `01-release-plan.md` needs no deferral entry. |
| O-1 `BL-0388` role gate at submission / omitted seat | **Closed by owner decision** | `BL-0388` `DONE`: accepted as v1, `FR-3520` amended. Probed: an omitted seat skips the gate (§7). |
| O-2 / D-1 role scoping dormant in shipped content | **Open, disclosed** | 0 of 19 vignettes declare `roles_needed`. The Creator does not save the matrix (`BL-0390`). No owner record → **decision O-2** (§8) |
| V-1 `VR-1088` header | **Open** | §2.2 |
| R-2 four skips that never run | **Open** | §2.5 |
| S-1 `save_format: 999` accepted | **Closed** (`IP-1094`) | 999, 3, `"2"`, `true`, `null` → 400. Legacy (absent) → 200 (§7) |
| S-2 `BL-0271` | **Closed** | `10a` row 8 describes the sensor-built Mode list |
| S-3 lock refresh available | **Closed** (`IP-1093`) | Latest = lock (§2.4) |
| N3 `run-spacesim` Chromium glob | **Closed** (`IP-1094`) | `driver.py` `find_chromium()` globs `chromium-*/chrome-linux*/chrome` and picks the newest |
| N4 `README.md` stale | **Closed** | Install from the lock (lines 34–37), trust-model section (lines 48–58), a `--reload` warning. No stale test count is left (README states no count). |
| N6 `01-release-plan.md` line 70 (`FEAT-3500` "UNASSIGNED") | **Open** (Low) | Unchanged since `9b491a4`. It flips on GO (§9). |
| N7 Starlette deprecation warning | **Open** (Low) | §2.4 |

### 3.2 REV-REL-002 and REV-REL-001

**REV-REL-002** had two blockers:
- **B1** (40 packages never inside an integration review): closed by the unreviewed-packages review plus the
  RC-3 delta, and confirmed again by the 94/94 union.
- **B2** (`FEAT-3500`): closed by delivery (`IP-1160`).

**REV-REL-001**'s sole NO-GO reason (`FEAT-3500` undelivered) is closed by delivery. Its other accepted items
still stand: hot-seat fog `BL-0015` (owner-accepted) and the LAN trust model (§6).

## 4. Deviations (delivered differently from the plan)

| Deviation | Authorization trail |
|---|---|
| `FR-3520`: the role gate is checked at **submission**; omitting `seat` skips it | Owner accepted v1 (`BL-0388`, run #264); `FR-3520` amended (run #265) |
| **D-1** `FEAT-3500` ships dormant: no shipped vignette declares `roles_needed`; the Creator saves `roles_needed: []` | Disclosed (`BLU-15`, `12b`, `12c`). **No owner acceptance on record → O-2** |
| `FR-5310` template-reference clause dropped (the content model has no templates) | `BL-0233` option A, `ADR-0036`, requirements pass 5 |
| Save-as-scenario omits gating rules, detectability config, space-weather series and the inject schedule | `BL-0389` `DONE`: documented v1.1 known deviation (`12b`/`12d`) |
| Console has no control for gate approve/deny, live ROE change, manoeuvre ledger, undo, clock rate (**HTTP only**) | `BL-0389`; the manuals say "HTTP only" (`12`/`12c`/`12d`); REV-TRN-012 White verdict "stated honestly" |
| Pause/Resume resets a custom clock rate to 1.0; Creator role matrix not saved; `mt-sigint-geolocate` `characterize_emitter` unreachable by orders; Blue availability objectives (`pnt_avail`/`satcom_avail`) score the satellite's health, not link availability (MET while jammed) | `BL-0390` `DEFERRED` ("file via 00-intake after release; Pause/Resume first"). The availability semantics are documented in the briefs, and `test_blue_availability_objectives_measure_the_satellite_not_the_link` pins them. |
| Hot-seat hand-off not automatic (`FR-6610`, `BL-0015`) | Owner-accepted |
| AI-Red reads ground truth (`ADR-0024`) | Documented design boundary |
| `NFR-3810` check has nothing to check on the real tree (no retired documents) | RC-7 Low, `BL-0393` `DEFERRED` |

## 5. Residual risks and open backlog (read-only; `docs/pipeline/` untouched)

**Open backlog** (`docs/pipeline/backlog.md`, rows not `DONE`/`DEDUPED`): **76 open**:

| Severity | Count |
|---|---|
| Critical | **0** |
| High | 3 |
| Medium | 15 |
| Low-Medium | 1 |
| Low | 56 |
| priority-"C" request | 1 |

Status counts: `SCHEDULED` 33, `DEFERRED` 28, `DECIDED` 11, `IN PIPELINE` 4. The file still holds 13 `DONE` rows
→ bookkeeping for `00-pipeline-manager`.

| ID | Sev | What | Disposition for this release |
|---|---|---|---|
| `BL-0049` | High | `FEAT-3500` undelivered | **Stale**: delivered by `IP-1160`; close in triage |
| `BL-0292` | High | Author GDS-06..10 | **Stale**: `architecture/INDEX.md` and `ROADMAP.md` show all five authored with closed gates; `CLAUDE.md` agrees |
| `BL-0310` | High | Test-origin traceability | **Stale**: delivered (0 untagged, generated RTM column) |
| `BL-0139`, `BL-0140` | Medium | OMM epoch discarded; a malformed per-object owner aborts a bulk-import batch | Known deviations (fidelity / authoring) → `07` |
| `BL-0252` | Medium | `yaml.safe_load` without a `YAMLError` guard in the built-in id scan | Built-in YAML is shipped content, so it only bites an edited install; → `07` |
| `BL-0284`, `BL-0315`, `BL-0233` | Medium | Rewind drops injects; force edits lost on resume; template clause | **Stale**: fixed (`IP-1083`; `IP-1101`/`1102`) or amended |
| `BL-0028` | Medium | R600 citations not verified by fetch | Research-confidence caveat (egress-blocked) |
| `BL-0288`, `BL-0293`, `BL-0297`, `BL-0299`, `BL-0334`, `BL-0379` | Medium | Governance / doc scope / dependency policy / allow-list keying | Not product defects; several stale |
| `BL-0390` | Low-Med | Behaviour defects (§4 row 6, plus `/start` works on a Creator draft — **reproduced: 200**; junk role accepted; bulk import after Start returns `[]`; a jammed command shows `executed`; raw-JSON Creator errors) | `DEFERRED` to post-release intake. **Two can mislead a learner or scorer** (availability objectives; Pause/Resume rate) |
| `BL-0286` | Low | ⚖ Compare panel not in the White manual | **C-2** |
| `BL-0386`, `BL-0392`, `BL-0393` | Low | Unbounded live event log; `--origin-report` exits 5; swapped `t1`/`t2` gives a header-only export; untriggered retired check | `DEFERRED`, documented |

**New findings of this assessment** (none Critical or High):

| # | Sev | Finding | Route |
|---|---|---|---|
| C-1 | Medium (process) | Learner-walkthrough gate not current after `78417d6`, `96b313c`, `62ef8a0` | `09-training-manual-review` delta on those three commits, or owner deferral |
| C-2 | Low (gate) | `BL-0286` open Manual-impact item (⚖ Compare panel) | `08-training-manual-authoring` (add to WCM-6), or owner deferral |
| F-1 | Low | `15` §15.3 calls a manual review step an automated "matrix coverage check" gate; the next sentence's "it" now dangles | `08-training-manual-authoring` (fold into C-2's pass) |
| F-2 | Low | REV-REL-003 §2.6 recorded `BL-0286` as covered in `12d`; it was not | Recorded here; no action |
| F-3 | Low | `training-basics` brief header shows "Duration: ~30 min" (`estimated_duration_min: 30`), but both cells' tutorials run to the T+1 h sim deadline | `08-vignette-development` (state wall-clock vs sim time, or align) |
| V-1, R-2, N6, N7 | Low | Carried (§3.1) | as routed |

**Residual risks shipping on a GO:**
- the LAN trust model (§6)
- hot-seat fog (`BL-0015`)
- AI-Red reads ground truth
- role scoping is advisory and dormant (O-2)
- the save-as-scenario omissions
- the `BL-0390` behaviour defects
- the unbounded live event log
- the browser GUI is covered by 42 browser tests and this smoke, not by an exhaustive UI test

## 6. The LAN trust model: the product's accepted security boundary

**There is no authentication.** Every request names its own seat (`cell=white|blue|red|observer`, plus an optional
operator `seat`), and the server believes it. Fog-of-war is enforced server-side on every cell-scoped response.
White-only controls and Observer mutations are refused server-side, but only against the *asserted* seat.

Re-checked this run (§7):
- a request naming `red` reads Red's scene (200)
- `/godview` with no cell returns truth (200)
- any client sending `?cell=white` can step the clock (200)
- an Observer order is refused (403); a Blue or seat-less `step` is refused (403)
- the operator-seat role gate is skipped by omitting `seat`
- the White pending-inject list `GET /injects/pending` is a no-cell read by design (`FR-6220` "the inject list").
  A request naming `red` gets it, including the message text. This is the boundary as specified, not a fog leak:
  the *activity feed* is fog-correct.

**What a deployer must do:**
- Run only on loopback or on an isolated, trusted LAN with cooperative participants. Never expose the port to the
  internet or to an untrusted network.
- Bind `127.0.0.1` on a single machine. Bind the LAN address only behind a host firewall limited to the
  participants' machines.
- Never use `--reload` in an exercise.
- Install from `requirements.lock`.
- Treat every participant as able to see ground truth and to act as White.
- Brief participants that seat selection and operator seats are an honour system.

The transport is plain HTTP: no TLS, and no audit beyond the event log's asserted seat. **`README.md` states this
plainly** in "Security and the LAN trust model — read before sharing a session" (no authentication, honour system,
loopback or isolated LAN behind a firewall, never the internet, no `--reload`). Per-cell tokens are listed in
`docs/FUTURE-WORK.md`. Sources: `ADR-0015`, `NFR-2300`, `FR-6220`, `CLAUDE.md` "LAN trust model", `training/01`
§2.1, `WCM-3`.

## 7. End-to-end smoke of the shipped app, following the README exactly

**Setup.** A fresh venv, then `pip install -r requirements.lock && pip install --no-deps -e .`, then
`python3 -m spacesim.ui_web` from the repository root. The server came up on `127.0.0.1:8000` from
`spacesim.config.yaml`, and `GET /` returned 200. I drove it with headless Chromium
(`/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`) through my own Playwright script, using the README's UI
path: White, then 📋 Session ▾, pick the vignette, Seed 1, **Load**, **▶ Start**, the brief opens, +10m ×3, then
switch to White, Blue and Red. **Server log: 1465 requests, 0 × 5xx.**

| Drive | Result |
|---|---|
| **Console as White / Blue / Red** on `training-basics`, `leo-isr-denial`, `coa-russia-md` and `co-orbital-threat-escort` (12 seat views) | All rendered. Load gives a `#sess-N` URL; Start works; the brief panel is populated ("Theater: …"). Fleet rows are fog-sized: `training-basics` 9 / 4 / 6, `leo-isr-denial` 8 / 5 / 4, `coa-russia-md` 10 / 6 / 5, `co-orbital` 7 / 5 / 2. The time buttons show for White only. **0 page errors**; one console 404 (`/favicon.ico`). |
| **`training-basics` tutorial path** (Blue steps 2–5, through the UI) | `RADAR-TRN` observe `RED-TGT` gives the preview `✓ will queue · sensor_collect · window 2030-03-15T06:36:07Z`, issued. `ISR-EO-1` downlink via `GS-TRN` gives `✓ will queue · ground_uplink · window …06:43:51Z`, issued. White +10m to T+60 gives **`deliver_isr` ✓ and `keep_custody` ✓**, as steps 4–5 say. The ▶ Tutorial panel (View ▾) shows "TUTORIAL — BLUE CELL Review fleet & objectives…". The Red and Blue tutorials are also machine-run by `test_vignette_tutorials.py` (green). |
| **Creator + starter snippets** | I wrote the six `12b` snippets verbatim into one file, plus the required header, in a private `external_vignette_dirs` folder. It is listed with origin `ext`; Load and Start give 200; a Blue downlink `ISR-EO-1` via `GS-NORTH` is `queued`; and **`deliver_isr` ✓**. Draft session: `creator/state` GET 200 (a named no-cell authoring read, `FR-6220`); PUT 200 as White and **403 as Blue**; step on a draft gives **400** "draft sessions cannot advance time"; `/start` on a draft gives **200** (`BL-0390`, known). |
| **Operator seat / role scope** | Snippet vignette with `roles_needed: [{ISR-EO-1, bus, mandatory: false}]`. `roles/assign` (White) gives 200. A bus seat issuing `isr.collect_now` is rejected `role_scope_out_of_scope`. The same order with no `seat` passes the role gate and fails later on `no_command_station` (the accepted `BL-0388` behaviour). `roles/scope` asked as Red about the Blue seat shows `bound: false`, so it is fog-scoped. |
| **Time bounds** | `step` 400 days gives 400 "beyond the exercise span (start_epoch + 366 days …)"; `NaN` gives 400; negative gives 400; a Blue `step` and a seat-less `step` give 403. |
| **Save / resume with warnings; `save_format` refusal** | `GET /save` carries `baseline`, `content`, `save_format: 2`, `simulator_version`. `load_save` gives `{session, warnings: []}`. With `simulator_version` set to `deadbee`, the warning reads "this save was written by simulator version deadbee; this is 0678112". As Blue it gives 403. `save_format` 3 / `"2"` / `true` / `null` / 999 all give 400 "save_format … is not supported; supported formats: legacy (absent), 2". With `save_format` absent (legacy) it gives 200. |
| **ISO export bounds (`FR-7450`)** | Telemetry CSV with `t1`/`t2` ending in `Z` gives 200 (134 lines); with `+00:00` it gives 200 (134 lines). `t1=yesterday` gives 400 "not an ISO-8601 UTC timestamp". A span wholly in 2031 gives 400 "wholly outside the session's …". `interval_s=0.01` gives 400 "180001 instants, over the export ceiling of MAX_EXPORT_SAMPLES". Blue asking for a Red asset gives 404 (fog). Truth ephemeris with ISO bounds gives 200. |
| **Activity-feed fog (Red must not see White's scheduled injects)** | On `leo-isr-denial` I scheduled two White future injects (pending = 2). `GET /activity/white` shows the inject rows (6 inject keys); **`/activity/blue` and `/activity/red` show 0 inject rows** and neither probe text; Observer follows its default god-view designation (same as White); an unknown cell `purple` gives 400. |

## 8. Assessment

**Recommendation: NO-GO as the candidate stands, on the letter of the step-3b documentation gate only. It converts
to GO on two small conditions. No code defect blocks the release.**

The engineering evidence is the strongest of the four assessments:
- 94/94 `VERIFIED` with VRs, and 94/94 inside an integration review whose latest delta (RC-7) is 0 Critical /
  0 High and GO
- no production code changed since that review
- every suite green in every mode, on the system interpreter, on the latest dependency set and on the lock
- the latest dependency set is identical to the lock
- determinism and import guard green; zero untagged tests; every allow-list empty except the 38 known links
- every blocker of REV-REL-001, -002 and -003 closed with evidence
- the shipped app ran end to end, exactly as the README says, for White, Blue and Red on four vignettes, plus the
  tutorial path, with zero 5xx

| # | Blocking condition | Gate | Clears when |
|---|---|---|---|
| **C-1** | The learner-walkthrough gate (REV-TRN-012 @ `92c56c8`) is **not current**: `78417d6`, `96b313c`, `62ef8a0` changed `docs/training/` and vignette YAML after it | Step 3b: the review must be current | **Either** a `09-training-manual-review` delta on those three commits returns no High (§2.6 is supporting evidence: M-1, L-1, L-2 hold; F-1 Low) **or** the owner records a deferral listed under Deviations |
| **C-2** | One open Manual-impact item: `BL-0286` (the ⚖ Compare panel is not in WCM-6) | Step 3b: no open Manual-impact item | **Either** `08-training-manual-authoring` adds it (and fixes F-1 in the same pass, which then needs C-1's re-review) **or** the owner records a deferral |

**The cheapest defensible path:** the owner records deferrals for C-1 (citing this document's spot-check) and C-2
(Low; the panel is White-only and self-labelled). The evidence then supports **GO today**. The cleaner path is one
`08-training-manual-authoring` pass (`BL-0286` + F-1), then one `09-training-manual-review` delta on the four
training commits, then GO.

**Conditions to attach to a GO** (non-blocking):
- **O-2:** accept that role scoping ships dormant, or add a crewed vignette via `08-vignette-development`.
- Accept the §4 deviations and §5 residual risks explicitly, in particular the two `BL-0390` items that can mislead
  a learner or scorer (availability objectives; Pause/Resume rate).
- Accept the §6 trust model.

## 9. Records that WOULD flip on a GO (none touched by this assessment)

| Record | Change |
|---|---|
| `docs/feature-planning/01-release-plan.md` | Mark the Prototype, MVP, Release 1 and Release 2 buckets released at the GO commit. Fix N6 (line 70 `FEAT-3500` "both included FRs show RTM `UNASSIGNED`", and the other stale body text). Record the owner's C-1/C-2 deferrals if that path is chosen. |
| `ROADMAP.md` | Add a "Release 1 — released" status entry dated at GO with the commit. Update this assessment's entry with the owner's decision. |
| `CLAUDE.md` | Status line: "released at `<commit>`" (counts already current: 2244 / 2240 passed / 4 skipped; non-browser 2202 / 5; browser 42) |
| `README.md` | Status line: released, version/commit. The trust and lock sections are already correct. |
| `docs/INDEX.md`, `docs/feature-planning/INDEX.md` | Point at this assessment as the release record |
| `docs/implementation/00-master-build-plan.md` | Summary line naming the release commit (package statuses unchanged: 94 `VERIFIED`) |
| This document | Date-stamp the baseline and record the owner's GO and any deferrals |

At that time, commit as `docs(release): release candidate 10 — assessment + baseline update`.

## 10. Pipeline position

Stage 11 (final). **Next step:** the owner decides C-1/C-2 (deferral or fix) and O-2. If fixing:
`08-training-manual-authoring` (`BL-0286`, F-1, optionally F-3 via `08-vignette-development`), then
`09-training-manual-review` delta, then the owner's GO on this document plus that report. If deferring: the
owner's GO, then this skill's baseline flip (§9).

## Final confirmation (REV-REL-004 addendum)

**Date:** 2026-11-01. **Commit assessed:** `935fd44` (`claude/release-candidate-12`), worktree branch
`claude/release-assessment-final`. A fresh session that did not author any of the work since `cfcf47f`. Read-only
except for this section. `docs/pipeline/` was not touched.

### A.1 What changed since `cfcf47f` (`git diff --stat cfcf47f..935fd44`: 8 files, +512 / −8)

| File class | Paths |
|---|---|
| Training manuals | `docs/training/11-vignette-playbooks.md`, `12-white-cell-manual.md`, `15-manual-traceability.md` |
| Review records | `docs/reviews/release-assessment-release-candidate-10.md` (this assessment, `79c485e`), `docs/reviews/training-review-final-rc11.md` (REV-TRN-013) |
| Ledgers | `ROADMAP.md` (status entries), `docs/pipeline/backlog.md`, `docs/pipeline/pipeline-journal.md` |
| Production code (`spacesim/`), tests, vignette YAML, `requirements.lock`, `pyproject.toml`, UI static files | **none** |

Every change since the evidence commit is documentation. No code gate needs re-running because of the diff. I re-ran
the gates anyway.

### A.2 Gates, one run per mode, real exit codes, `--junitxml`

| Run | Exit | Tests | Failures / errors | Skipped |
|---|---|---|---|---|
| Unfiltered `python3 -m pytest` | 0 | **2244** | 0 / 0 | 4 |
| `-m "not browser"` | 0 | **2202** | 0 / 0 | 5 |
| `-m browser` | 0 | **42** | 0 / 0 | 0 |
| Named gates: `test_doc_integrity`, `test_training`, `test_training_sources`, `test_vignette_tutorials`, `test_test_origins`, `test_origin_id_widening`, `test_origin_retag`, `test_determinism`, `test_import_guard` | 0 | 375 | 0 / 0 | 1 |

These match REV-REL-004 §2.1 exactly.

### A.3 Conditions C-1, C-2 and finding F-1

- **C-1 (learner review current): closed.** REV-TRN-013 (`e12311a`) reviewed `70fb36c` and found 0 High, 1 Medium,
  2 Low. The only later change to `docs/training/` or vignette YAML is `4ce7fb2`, which fixes exactly those three
  findings (`git log e12311a..HEAD -- docs/training spacesim/content/vignettes` lists only it). I checked each fix myself:
  - **M-1:** WCM-6 now says "tick **Compare (truth / Blue / Red)** under **View ▾ → Panels**; **↺ Reset layout**
    also restores it". `panels.js` builds a **Panels** section with that exact label and a `↺ Reset layout` button.
    Driven live (leo-isr-denial, Seed 1, White): unticking hides the panel, ticking shows it again; untick then Reset
    layout shows it again. On Blue and Red the panel is not shown.
  - **L-1:** §15.3 now names `test_vignette_tutorials.py` as the subject of "Since 2026-10-25 … also drives the
    five Red COA recipes".
  - **L-2:** §11.15 and §11.17 now say the kill lands by T+26 and the ✓ shows at the first **+10m** click past it,
    T+30. That matches the +10m step grid from T+20. `test_vignette_tutorials.py` is green.
- **C-2 (Compare panel in WCM-6): closed.** WCM-6 has the complete Compare procedure: White-only, the 403 for other
  seats, where to find it, how to open it, the reopen path, refresh, and the worked example.
- **F-1 (false §15.3 automated-gate sentence): closed.** §15.3 says there is no repository test for the §15.1
  coverage check, and that the learner-walkthrough review performs it.

### A.4 Ledger and allow-lists (recounted)

Master Build Plan, `docs/implementation/packages/INDEX.md` and `ROADMAP.md` each have **94** `IP-` rows. All 94 ids
are distinct and all 94 rows are `VERIFIED`. Allow-list entries (comments excluded): `test_origin_allowlist` 0,
`doc_integrity_allow_indexes` 0, `_ledgers` 0, `_retired` 0, `_links` **38**. Nothing has changed since §2.1.

### A.5 Lock sanity (informational; lock unchanged)

I built a fresh venv from `requirements.lock` (CPython 3.13.17) and ran `pip list --outdated`. One newer version
has appeared since REV-REL-004: **`pyee` 14.0.0 → 16.0.1**. It is not adoptable: the locked `playwright` 1.64.1
requires `pyee<15,>=13`. It is a test-only, transitive dependency of the browser harness. No action is needed for
this release; the next lock refresh (`07`) picks it up together with N7 (the Starlette `httpx` deprecation).
**NFR-1510 still met.**

### A.6 Smoke (README path)

I started from the same fresh venv (`pip install -r requirements.lock && pip install --no-deps -e .`) and ran
`python3 -m spacesim.ui_web`, which came up on `127.0.0.1:8000` with `GET /` returning 200. I drove it with
headless Chromium.

- **leo-isr-denial, Seed 1:** Load gave `#sess-1`. Start worked, followed by +10m ×3. I switched White → Blue →
  Red → White, and every seat rendered with the correct `data-cell`. The Compare panel is visible only on White.
- **training-basics:** Load gave `#sess-2`. The Tutorial panel opens for Blue (6 steps) and for Red (6 steps).
- **Page errors: 0.** Server log: 424 requests, 0 × 5xx. The only 4xx were two `favicon.ico` 404s, which are benign.

### A.7 What ships: the owner-accepted release baseline (journal run #266)

The owner accepted these as the release baseline. Their authorization trails are in §4.

1. `FR-3520`: the role gate is checked at submission, and omitting `seat` skips it (`BL-0388`; `FR-3520` amended).
2. **D-1 / O-2:** role scoping (`FEAT-3500`) ships as an **opt-in, dormant** feature. No shipped vignette declares
   `roles_needed`, and the Creator saves `roles_needed: []` (`BL-0390`). The owner accepted this; it closes O-2.
3. The `FR-5310` template-reference clause was dropped (`BL-0233`, `ADR-0036`).
4. Save-as-scenario omits gating rules, detectability config, the space-weather series and the inject schedule
   (`BL-0389`; v1.1).
5. These controls are **HTTP only**, with no console control: gate approve/deny, live ROE change, manoeuvre
   ledger, undo, clock rate (`BL-0389`).
6. The remaining §4 rows:
   - Pause/Resume resets a custom clock rate.
   - The Creator role matrix is not saved.
   - `mt-sigint-geolocate` `characterize_emitter` cannot be reached by orders.
   - The Blue availability objectives score the satellite's health, not link availability.
7. The hot-seat hand-off is not automatic (`FR-6610`, `BL-0015`).
8. AI-Red reads ground truth (`ADR-0024`).
9. The `NFR-3810` retired-document check has nothing to check on the real tree (`BL-0393` deferred).
10. The LAN trust model (§6): cell seats are client-asserted, with no authentication. The product is for a
    trusted LAN only.

### A.8 Records that WOULD flip on a GO (checklist; none touched here)

- [ ] `ROADMAP.md`: add a "Release 1 — released" entry dated at the GO, with the commit, and record the owner's
      decision against the REV-REL-004 entry.
- [ ] `docs/feature-planning/01-release-plan.md`: mark the Prototype, MVP, Release 1 and Release 2 buckets
      released; fix N6 (line ~70 `FEAT-3500` stale RTM text); record the C-1/C-2 closure and the O-2 acceptance.
- [ ] `CLAUDE.md`: change the status line to "released at `<commit>`". The counts are already current
      (2244 / 4 skipped; non-browser 2202 / 5; browser 42).
- [ ] `README.md`: change the status line to released, with the version and commit.
- [ ] `docs/INDEX.md` and `docs/feature-planning/INDEX.md`: point at this assessment as the release record.
- [ ] `docs/implementation/00-master-build-plan.md`: add a summary line naming the release commit (94 `VERIFIED`
      unchanged).
- [ ] This document: date-stamp the baseline and record the owner's GO.

### A.8a Owner decision and baseline flip (2026-11-01)

**The owner declared GO on 2026-11-01** (via AskUserQuestion, in the release-flip session), on the strength of this addendum. The A.8 records were flipped on branch `claude/release-flip`: `ROADMAP.md`, `docs/feature-planning/01-release-plan.md` (Release state; stale `FEAT-3500` text corrected; also `02-epic-catalog.md`, `05-feature-review.md`), `CLAUDE.md`, `README.md`, `docs/INDEX.md`, `docs/feature-planning/INDEX.md`, `docs/implementation/00-master-build-plan.md`, and the `VR-1088` header (V-1). `docs/pipeline/` was left to the manager. Baseline date: **2026-11-01**.

**Known-deviation list: exactly what ships.** The ten §A.7 items, as accepted by the owner, are the release's known deviations. Item 6 covers four sub-items (Pause/Resume rate reset; Creator role matrix not saved; `characterize_emitter` unreachable by orders; Blue availability objectives score health). Item 2 closes O-2. The three GO conditions in A.9 stand: release from `935fd44` or a documentation-only descendant, publish this list, deploy on a trusted LAN only.

### A.9 FINAL RECOMMENDATION: **GO**

Nothing blocks the release. There is no code, test, dependency, verification, integration or documentation-gate
blocker:

- C-1, C-2 and F-1 are closed, with evidence above.
- O-2 is closed by the owner's acceptance.
- Everything changed since the evidence commit is documentation.
- All three suite modes are green at the expected counts.
- The smoke run had 0 page errors.

**The GO assumes three conditions:**

1. The release is cut from `935fd44`, or a descendant whose diff from it is documentation only.
2. The §A.7 deviations are published as the release's known-deviation list.
3. The deployment stays on a trusted LAN (§6).

The §A.8 flip runs only after the owner's explicit GO. **The GO/NO-GO decision is the owner's.**
