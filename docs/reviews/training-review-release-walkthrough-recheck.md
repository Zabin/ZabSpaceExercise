[↑ Docs index](../INDEX.md) · [Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md) · [First walkthrough](training-review-release-walkthrough.md)

# Training review (REV-TRN-011): release learner-walkthrough re-check (RC4)

Independent fresh-session review (authored none of this). Commit reviewed: `461d43a` (release candidate 4, branch `claude/release-candidate-4`). Review-only: no prose, YAML or code was changed. This is the re-check of [REV-TRN-010](training-review-release-walkthrough.md) (1 High, 10 Medium, 5 Low).

**Method.** Real app (uvicorn on loopback 8771) driven by headless Chromium (Playwright, `/opt/pw-browsers`) as a first-time learner, plus the HTTP API for HTTP-only claims. Exercised: `01` (server start), `02`, `03` end to end (Blue win, rewind, Red branch to T+3 h 30 min), `04` Blue and Red literally (Seeds 1 and 2) including the cyber confirm dialog, the recovery strip, and the manual `def.patch_cyber` compose; the in-app Tutorial panel for `training-basics` (Blue and Red, Seeds 1 and 2) and, by executing every tutorial step in the GUI, `mt-isr-sar`, `mt-weather-collect`, `nv-isl-relay-debris`, `learn-intermediate-recovery` (Seeds 1, 2), `gnss-ew-campaign`, `co-orbital-threat-escort`, `da-asat-crisis`, `sda-custody-hunt` (SSN request chip, five re-tasks); the four requested Red COA recipes (`coa-russia-md`, `coa-china-md`, `coa-misc-iran-ml`, `coa-china-ml`); manual `12b` (Creator: menu, draft, curated-site picker, bad latitude, save), `12c`/`12d`/`13a`/`14a` labels and procedures (sampled, labels scripted against `index.html` and `static/*.js`); `09a`: 15 refusal messages triggered live and compared; the activity-feed paragraphs WCM-6/BLU-2/RED-2 against `GET /activity/{cell}`. Sampling: `12`, `13`, `14`, `05`-`08`, `10`, `10b` read by label scan only, not walked.

## Verdict: could a newcomer finish unaided?

| Role | Verdict | Why |
|---|---|---|
| White | Yes | Install, `03`, Load/Start/step/Rewind (06:00:01Z, as written), Pop out (multi-screen), Creator (`12b`) all work as written; Resume-resets-rate is now stated. HTTP-only controls (gates, ROE, undo, rate) still need curl, stated honestly in `12`/`12c`/`12d`. |
| Blue | Yes, one wrong-label trap | `03`, `04` Blue, every tutorial completes as written; the verbs are now chosen by name in the Action menu. Trap: `04` Step 7 names a log line (`cdh.faults`) that does not exist (N1). Three in-app tutorials promise a `REFUSED` result where the UI disables **Issue** (N3). |
| Red | Yes, one chance trap | `03` Red branch, `04` Red (confirm dialog, disabled engage preview) and every Red tutorial complete as written. Trap: the COA recipes `11.15`/`11.17` present a chance-based kill as certain (N5). |

## Closure of the first review's findings

| First review | Status | Evidence (live unless noted) |
|---|---|---|
| F1 (High) `03` Step 4 Deny ISR timing | **Closed** | Seed 1: Red `Deny ISR` `✗` at +30 min, `✓` at 09:30Z after +1h x3, exactly as the rewritten item 4/5 says. |
| F2 `03` Step 3 why one downlink wins | **Closed** | "Why one downlink is enough here" paragraph present and true (Blue `✓ Deliver ISR` after +20m). |
| F3 `command`/`verb` wording | **Closed** | Tutorial panel steps now read `isr.collect_now`, `def.patch_cyber`, ...; each is an Action-menu entry for the actor (`isr.collect_now` on `SAR-1`, `def.patch_cyber` on `ISR-EO-1`) and queues with `via` pre-filled; `04` Step 8 explains there is no `command` item. |
| F4 RED-DAZZLE jam-only | **Closed** | `RED-DAZZLE` Action menu offers only `jam`; the `mt-isr-sar` Red step 2 is now a "review" step that says so. |
| F5 cyber confirm dialog in `04` | **Closed** | Dialog text captured live; `04` step now says click **OK**; cancel wording matches. |
| F6 Issue disabled / red preview | **Closed** | Preview `✗ ROE does not authorize kinetic effects.`, **Issue order** disabled; `04` line 103 says so. |
| F7 COA playbooks + `15.4` table | **Closed** | `11.14`-`11.18` exist; `15.4` has a 19-row table (all ids resolve in `11` and `16`). Recipes executed (see N5 for a caveat). |
| F8 Resume resets rate | **Closed in prose** | `12d` states it with the curl re-send. The code behaviour remains a product defect (not re-tested; routed earlier to `00-intake`). |
| F9 `15.1` Spec column, FS-114/123/124/129/133-135 | **Closed** | Spec (FS) column present; FS-123/FS-124 -> WCM-25, FS-129 -> BLU-2/RED-2, FS-114 -> WCM-3, FS-133/134/135 an explicit "Not operator-visible (test / CI tooling)" row. |
| F10 glossary terms | **Partly closed** | SOH, TLE, RIC, CATS, SSN, TDOA/FDOA, hot-seat, seed, LVLH, A2/AD, Gantt are now defined. Other acronyms the manuals use are not (N4). |
| F11 `03` names, 06:00:01Z, Fleet panel title | **Closed** | **Issue order**, `06:00:01Z`, "Fleet SOH rollup" all match the live UI. |
| F12 `09a` em dash | **Closed** | `09a` quotes with the em dash used by the app. |
| F13 Pop out label | **Closed** | `View ▾ -> Pop out (multi-screen)` matches. |
| F14 learn-intermediate dependency in title | **Closed** | Step title now reads "Notice the attack (Red must fire first ...)". |
| F15 objectives "pending" | **Closed** | `04` Step 1 says "show ✗". |

## Findings (new or residual)

### High

None. Every procedure walked completes as written for a learner who follows the text.

### Medium

| ID | Artifact | Finding | Exact fix wanted | Owner |
|---|---|---|---|---|
| N1 | `04` Blue Step 7 | Says the drill-down "shows the `cdh.faults` log line that flagged the modem". No such string exists anywhere in the UI or the telemetry log. After Red's cyber lands, `/telemetry/blue/ISR-EO-1` `log` reads `cdh.fsw_error_count = 24.0 count [RED]`, `cdh.cmd_reject_count = 7.2 count [YELLOW]`, `payload.snr_db = 2.1 dB [RED]`, `bus mode = SAFE_MODE; payload disabled`; the fleet row shows `safe_mode`. A learner searches for a line that is not there. | Replace `cdh.faults` with the real log lines above (or "the `cdh.fsw_error_count` line in RED"); say where the log is shown (drill-down, after clicking a parameter). | `08-training-manual-authoring` |
| N2 | `03`, `04`, `13`, `13a`, `14`, `14a` ("Order panel", "Order queue") | The on-screen panel titles are **Satellite command** (`<h2>`) and **Command queue** (`<h3>`); no element is titled "Order panel" or "Order queue". `10a` correctly calls it "Satellite command (compose form)". A newcomer scanning for the named panel must guess. | Name the panel as shown ("the **Satellite command** panel (the order form)") once at first use in each module, or say "Order panel = the Satellite command panel"; same for **Command queue**. | `08-training-manual-authoring` |
| N3 | In-app tutorials `co-orbital-threat-escort` (Blue 4, Red 2), `da-asat-crisis` (Blue 2), `sda-custody-hunt` (Red 3); mirrored in `11` | `expect` says "REFUSED (no_command_station) ... White Cell can add a ground station with Force add". Live: **Issue order** is disabled and the red preview reads "No command path — set a ground station ('via') or a stored-program time." (no REFUSED result line). There is also no "Force add" control in the console; force-add is HTTP-only (`12d` WCM-23) and refused after Start (`cannot edit force after start`), so the suggested remedy cannot be done mid-exercise. | Reword the `expect`s to what the learner sees (button disabled, preview text) and drop or qualify "Force add" ("a facilitator can add a station before Start via the HTTP force-add route, see WCM-23"). | `08-vignette-development` |
| N4 | `09` glossary (residual of F10) | Acronyms used in the role manuals, `06` and `11` and defined nowhere in `docs/training/`: SAR, PNT, GNSS, SDA, SATCOM, EW, TT&C, SoC, MEO, SGP4 (grep: 0 definitions; 3-21 uses each). NFR-3600 wants jargon introduced or glossary-linked. | Add one-line glossary entries (and link from first use in `06`/`11`). | `08-training-manual-authoring` |
| N5 | `11` 11.15 (`coa-russia-md`), 11.17 (`coa-china-md`) | The kill is stated as certain ("`destroy_isr` ✓", "`kill_isr` ✓"). It is a chance event and depends on what else was ordered first. Live, Seed 1: cyber first, then observe, then `engage {interceptor_class: mrbm_kkv}` on `coa-russia-md` left `destroy_isr` ✗ (debris created, ISR survives) while observe-then-engage alone gave ✓; `coa-china-md` with cyber and jam first gave `kill_isr` ✗, observe-then-engage alone gave ✓. A learner who follows the full recipe may see ✗ and conclude they erred. (The `coa-china-md` recipe also omits the `engage` params that `coa-russia-md` gives.) | State that the engage is chance-based and the result depends on order of issue; add "if it misses, **Rewind** and re-issue, or change the Seed"; give the engage params for 11.17. | `08-vignette-development` |

### Low

| ID | Artifact | Finding | Exact fix wanted | Owner |
|---|---|---|---|---|
| L1 | `learn-intermediate-recovery` Blue step 5 / `11` 11.13 | `expect` says `recover_to_nominal` is MET at the T+45 min deadline. Live (Seed 1, patch pass 10:40:44): `✗` at 10:42 and at the first click past the deadline when stepping by 1 min; `✓` at 10:52 (with +10m clicks). | "MET a few minutes after the patch pass (about T+50 min); keep clicking +10m". | `08-vignette-development` |
| L2 | `learn-intermediate-recovery` Blue (Seed 2) | Seed 2: Red's cyber misses, the bird stays nominal, and Blue steps 3-4 have nothing to recover (**Begin recovery** does not appear). Step 2's title warns "Red must fire first" but not that Red can miss. | Add "if the bird stays nominal Red missed; have Red fire again (about 62%)" to Blue step 2 (the Red step has it). | `08-vignette-development` |
| L3 | `12b` Save refusal | `12b` quotes `error: no user-save directory configured — set content.user_save_dir in spacesim.config.yaml`; the app shows `error: {"detail":"no user-save directory configured — ..."}` (raw JSON wrapper). | Quote the line as shown, or note the JSON wrapper. | `08-training-manual-authoring` |
| L4 | `04` Blue Step 7 text vs screenshot | "The fleet rollup dot turns red as soon as that telemetry lands": live the row reads `safe_mode ⚠5` at +10 min (fine), but the wording "badge turned red" was not distinguishable headless. Informational: re-check against the screenshot. | None unless the screenshot disagrees. | `08-training-manual-authoring` |

## Dimension evidence

- **Accuracy.** Above: every item in the first review re-walked live; 15 refusal messages triggered and compared (`no_command_station`, `no_downlink_station`, `not_owner`, `no_such_asset`, `roe_kinetic_not_authorized`, `roe_cyber_not_authorized`, `invalid_param`, `insufficient_delta_v`, the White-control 403, the Observer 403, `unknown session`, `vignette 'x' not found`, `unknown cell 'purple'`, the NaN guard text, inject-cancel 403): all match `09a` (reason codes and quoted HTTP text). Note: `unknown_action` for a `jam` by a satellite returns `no_window` on the dry run, not `unknown_command`/"Action not supported" (informational, matches `09a`'s "possibly" wording only loosely).
- **Traceability.** Scripted: every `WCM-/BLU-/RED-n` cited in `15` resolves to a heading and every such heading is cited (no orphans either way); `15.4` has 19 rows, all ids appear in `11` and `16`; `Sources:` footers resolve (`test_training_sources.py`).
- **Feature-spec coverage check (mandatory).** Scripted from the Master Build Plan: 90 package rows -> 36 Feature Specifications, all packages `VERIFIED` for each (none partial). All 36 appear in §15.1 (Spec column) with a manual section (WCM/BLU/RED or a shared `01`-`10` section; FS-118 maps to `01` §2.2) or an explicit not-operator-visible reason (FS-133/134/135). **Misses: none.** FS-108 is cited in 15.1 but has no package (candidate), FS-202 has no package: out of scope for the check.
- **Pedagogy.** Sequencing 01 -> 04 -> role manuals is workable; the `03` branch-and-rewind lesson is now accurate end to end. Gaps are N2 (panel names) and N4 (glossary). R600 not cited by this review: sequencing judgements are "ungrounded, pending R6xx" where not obvious.
- **Activity feed (WCM-6/BLU-2/RED-2).** Live `/activity/{cell}`: White sees both lanes and `ew_jam -> ISR-EO-1 (deny)`; Blue sees its own orders plus `electronic_warfare -> ISR-EO-1 (deny)` and no Red order; Red sees only its own `JAM-NORTH jam -> ISR-EO-1`. Matches the paragraphs.
- **Open Manual-impact backlog items in scope.** Not re-surveyed beyond the pipeline files named in the task (docs/pipeline/ untouched).

## Tests (this commit)

See the end of the file (filled after the final runs).

## Routing

N1, N2, N4, L3, L4: `08-training-manual-authoring`. N3, N5, L1, L2: `08-vignette-development`. No code defects newly found (the Resume-rate behaviour is the earlier `00-intake` item). Next step: one authoring + one vignette pass for the five Medium items; no release blocker (zero High).
