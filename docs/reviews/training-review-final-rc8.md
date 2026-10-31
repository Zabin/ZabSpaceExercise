[↑ Docs index](../INDEX.md) · [Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md) · [Previous re-check](training-review-release-walkthrough-recheck.md)

# Training review (REV-TRN-012): final learner-walkthrough gate for release candidate 8

Independent fresh-session review (authored none of this). Commit reviewed: `92c56c8` (branch `claude/release-candidate-8`, worktree `claude/training-review-rc8`). Review-only: no prose, YAML or code was changed. Scope: the independent re-review that [`release-assessment-release-candidate-5.md`](release-assessment-release-candidate-5.md) blocker B-2 asked for, covering the training fixes landed after [REV-TRN-011](training-review-release-walkthrough-recheck.md) (`75bfe5c`: 0 High, 5 Medium, 3 Low): `8de366b`, `e2e1342`/`d86c845`, `5f1b34a` and the RC8 doc edits `92c56c8`.

**Method.** Fresh venv under a private directory, `pip install -r requirements.lock && pip install --no-deps -e .`, then `python3 -m spacesim.ui_web` exactly as the README says (HTTP 200 on `/`, pytest present in the lock). Live app driven by headless Chromium (`/opt/pw-browsers`) and the HTTP API. Note for the reader: the pip-installed `playwright` in the lock wants a newer Chromium build than `/opt/pw-browsers` holds, so a launch needed `executable_path=` (environment detail, not a manual defect).

## Verdict: could a newcomer finish unaided?

| Role | Verdict | Why |
|---|---|---|
| White | Yes | README install and run work as written; `03` Step 1 and the Fleet panel; Load/Start/step/Rewind; the 12b Creator starter snippets load, start and play; WCM-22 save-format refusals read as quoted. HTTP-only controls still need curl, stated honestly. |
| Blue | Yes | `03` Step 2 matches the live UI character for character (preview `✓ will queue · ground_uplink · window 2030-03-15T06:05:19Z`, result line, time buttons gone on the Blue seat); `04` Step 7 now describes lines that exist; the four blocked-step tutorials now describe what the console shows. |
| Red | Yes, one ordering trap | `11.15`/`11.17` recipes work as written on Seed 1 and the miss path is described. Trap: "and only then cyber/jam" is ambiguous (M-1). |

## Closure of REV-TRN-011 findings

| ID | Status | Evidence |
|---|---|---|
| N1 `04` Step 7 `cdh.faults` | **Closed** | `cdh.faults` has 0 hits in `docs/training`; Step 7 now lists `bus mode = SAFE_MODE; payload disabled`, `payload.snr_db ... [RED]`, `cdh.fsw_error_count`, `cdh.cmd_reject_count`; the live log (`learn-intermediate-recovery`, Seed 1, same signature) shows exactly the SAFE_MODE line first. |
| N2 "Order panel"/"Order queue" | **Closed** | `grep` for both strings over `docs/training`: 0 hits; `03` names the **Satellite command** panel (the order form); index.html titles are `Satellite command` / `Command queue`. |
| N3 REFUSED vs greyed Issue | **Closed in wording** | `co-orbital-threat-escort` Blue 4 / Red 2, `da-asat-crisis` Blue 2, `sda-custody-hunt` Red 3 now say "Issue order stays greyed out and the preview turns red", name the engine reason, and no longer promise a Force-add control. Live: Issue disabled, red preview. See L-1 for a residual wording difference. `mt-sigint-geolocate`: `SIGINT-1` Action menu has no `observe` entry (confirmed live), matching `11`. |
| N4 glossary acronyms | **Closed** | `09` now defines SAR (with EO), PNT/GNSS, SDA, SATCOM, EW, TT&C, SoC, MEO (with LEO/GEO/HEO), SGP4, in plain language. |
| N5 COA kills certain | **Closed** | `coa-russia-md` Seed 1: observe, engage (after two +10m) gives `destroy_isr` true; cyber `seize_c2` then lands on the second attempt exactly as `11.15` says; cyber ordered first gives `destroy_isr` false. `coa-china-md` Seed 1: observe, engage gives `kill_isr` true; jam+cyber issued before the shot resolves gives it false (see M-1). |
| L1 T+45 timing | **Closed** | `learn-intermediate-recovery` Seed 1 (patch via `GS-LEARN`, Begin recovery, 5-minute steps): `recover_to_nominal` false through T+42, true at T+47, the first step at or after T+45, as the new text says. |
| L2 Seed 2 miss | **Closed** | Seed 2: Red's cyber misses (no SAFE_MODE line); Blue step 2 and `11.13` now say so and tell Red to fire again. |
| L3 Save refusal JSON wrapper | **Closed** | `12b` quotes `error: {"detail":"no user-save directory configured — ..."}` with the wrapper noted. |

## Findings

### High

None.

### Medium

| ID | Artifact | Finding | Exact fix wanted | Owner |
|---|---|---|---|---|
| M-1 | `11` 11.15 / 11.17 | "issue observe, then engage, first, and only then cyber/jam" is ambiguous. Driven literally on `coa-china-md` Seed 1: observe, two +10m, engage, then jam and cyber queued immediately (before the engage window at T+22) makes `kill_isr` false, because the jam executes at once and uses the draw first. Waiting until the kill shows (T+30) then ordering jam and cyber keeps `kill_isr` true and both other objectives met. A learner who queues everything in one sitting follows the text and misses; the fallback (Rewind, re-issue) is described, so this is a trap, not a dead end. | Say "issue jam and cyber only after the engage has resolved and `kill_isr`/`destroy_isr` shows ✓ (about T+30 min)". | `08-vignette-development` |

### Low

| ID | Artifact | Finding | Exact fix wanted | Owner |
|---|---|---|---|---|
| L-1 | Tutorials in N3 list | Primary preview text quoted is `No command path - set a ground station (via) ...`; live with the form's auto-filled `via`, `co-orbital-threat-escort` Blue `BLUE-HVA` maneuver shows `✗ No access window in the planning horizon — wait for the next pass.` The step already gives this as a parenthetical, so a learner is covered, but the ordering is inverted. | Lead with the text the form shows first, keep the other as the parenthetical. | `08-vignette-development` |
| L-2 | `12d` WCM-22 (line ~75) | Says a text value such as `"2"`, `true` or `null` is refused "in the same words". Live: `save_format '2' is not supported ...`, `save_format True ...`, `save_format None ...` (value echoed as Python repr; `3` prints as `3`). Refusal is correct; only the echoed value differs. | "in the same words, with the value as the app prints it (`'2'`, `True`, `None`)". | `08-training-manual-authoring` |
| L-3 | `15` §15.3 (line ~259) | Still says `test_vignette_tutorials.py` "is the one automated staleness gate in the whole training corpus" (open `BL-0273`); `test_training_sources.py` and the doc-integrity checks are also gates. | Reword to "the gate for the playbooks/tutorials". | `08-training-manual-authoring` |

## New content walked

- **README top to bottom.** Install from `requirements.lock` in a fresh venv, run `python3 -m spacesim.ui_web`, open `/`, links to `docs/training/INDEX.md`, `01`, `03`, `16` resolve; run command and port as written. Completed as written.
- **12b Creator and starter snippets.** All six snippets pasted under their stated keys into one tiny vignette in a configured external dir: listed in the picker, loaded, started, a Blue `downlink` via `GS-NORTH` queued over `ground_uplink`, `deliver_isr` turned met (as the text claims). Completed as written.
- **WCM-22.** Self-contained save is `save_format` 2; unsupported values (`3`, `"2"`, null, true) refused 400 with the quoted line; save with the key removed loads with the `legacy save:` warning, as `12d` says (L-2 aside).
- **ISO bounds (12a, 08).** `ephemeris/truth` accepts `2030-03-15T06:00:00Z` and integer microseconds mixed; `+02:00`, a date only and a word give 400 naming `t1`; `interval_s=0` gives `interval_s must be a finite number > 0`. Matches. (The example needs `reference_id` too; the endpoint line in `12a` shows it.)
- **One exercise per role.** White (`03` Step 1, time buttons), Blue (`03` Step 2 in the browser; `04` signature and recovery via API), Red (`11.15`, `11.17`, `learn-intermediate-recovery` Red step) all completed.
- **Refusal messages compared with `09a` (12 matched):** `no_downlink_station`, `no_such_asset`, `not_owner`, White-control 403 (Blue and observer seats), `unknown session sess-N`, `vignette 'x' not found`, `step cannot move time backwards`, rewind outside the exercise span, the four `save_format` variants, `t1: ... is not an ISO-8601 UTC timestamp`, `interval_s must be a finite number > 0`.

## Dimension evidence

- **Coverage (mandatory).** Scripted from the Master Build Plan: 94 package rows, 36 Feature Specifications, all packages `VERIFIED`; every one of the 36 appears in `15` with a manual section or an explicit not-operator-visible row (FS-133/134/135). **Misses: none.** Changed specs checked: FS-121 v2.3 (`FR-7450` ISO bounds, `IP-1089`) maps to WCM-14/15, BLU-12/13, RED-11/12 and the maneuver-ledger row, with the ISO text present in `12a`; FS-135 v1.1 is the not-operator-visible row; FS-116 v1.3 maps to BLU-7/RED-7 and WCM-2; FS-131 v1.2 maps to WCM-2. (FS-121's own header still reads "FR-7450 specified and unbuilt" while `IP-1089` is built: a spec-status lag, not a training defect, routed to `06`.)
- **Traceability.** `test_training_sources.py` green (footers resolve); `15.1`/`15.2`/`15.4` consistent as before; the `10b` `executed` bar, the series-route docs and the WCM-1 observer note are in the tree.
- **Open Manual-impact backlog items.** `BL-0268` (Creator/bulk-import coverage): WCM-17 and the bulk-import sections now exist, substance closed. `BL-0271` (mode list), `BL-0272` (`executed`, Save as scenario in `12d`) closed in the text. `BL-0276` (RED-5 "rounds spent whether it hits or misses"): `14` line ~110 now says every salvo is spent, closed in substance. `BL-0283` (space-weather inject): covered by WCM-25. `BL-0273`: still open in prose (L-3). Several rows still read `SCHEDULED` in the backlog though their prose is fixed: the ledger lags the tree (journal reconciliation, outside this review's write scope).
- **Pedagogy.** Sequencing 01 to 04 to role manuals works; the remaining traps are ordering ambiguity (M-1) and wording order (L-1). R600 not cited by this pass.

## Tests (at `92c56c8`)

`test_doc_integrity.py`, `test_training_sources.py`, `test_training*.py`, `test_vignette_tutorials.py`, `test_test_origins.py`: 165 passed, 1 skipped, 0 failed. Full-suite counts are not re-run (code unchanged since the last integration review).

## Statement for release readiness

**The learner-walkthrough review is current for this release scope (commit `92c56c8`, RC8) and there are no open High findings.** Every REV-TRN-011 finding (N1-N5, L1-L3) is closed; the new content (README, 12b snippets, WCM-22, ISO bounds) was walked and works as written. One Medium (M-1) and three Low remain, none blocking.

## Routing

M-1, L-1: `08-vignette-development`. L-2, L-3: `08-training-manual-authoring`. FS-121 status header: `06-feature-specification`. Next step: `11-release-readiness` (B-2 satisfied); the Medium can ride the next vignette pass.
