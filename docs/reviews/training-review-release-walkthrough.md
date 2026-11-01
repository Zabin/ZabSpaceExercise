[↑ Docs index](../INDEX.md) · [Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training review (REV-TRN-010): release learner-walkthrough gate

Independent fresh-session review (authored none of this). Commit reviewed: `c50b6da` on `claude/manuals-catchup-1` (includes vignette/tutorial work `aa68f6a` and modules 09a, 12b, 12c, 12d, 13a, 14a). Review-only: nothing fixed.

**Method.** Real app (uvicorn on loopback 8765) driven by headless Chromium through Playwright, plus the HTTP API for HTTP-only claims. Walked 01, 03, 04 (Blue and Red, literally), the in-app Tutorial panel, and executed the tutorial steps for `mt-isr-sar`, `mt-weather-collect`, `nv-isl-relay-debris`, `learn-intermediate-recovery` (both cells) through the GUI. 12/12a-d/13/13a/14/14a: every bolded UI label was scripted against `index.html` + `static/*.js`; the quoted refusal strings in 09a/12*/13a/14a were scripted against the source; selected HTTP behaviours triggered live. Sampling: 12, 13, 14 procedures were not each driven end to end (inject builder, AAR, Creator forms exist by label but were not exercised). Not exercised: LAN, pop-outs.

**Tests.** `test_doc_integrity.py`, `test_training_sources.py`, `test_training.py`, `test_test_origins.py`, `test_vignette_tutorials.py`: all pass (the only skip is the browser/optional one). Unfiltered suite: see the end of this file.

## Verdict: could a newcomer finish unaided?

| Role | Verdict | Why |
|---|---|---|
| White | Yes with one trap | Load/Start/advance/rewind/inject/save labels all exist as named; 12d honestly lists what is HTTP-only. Trap: `03` Step 4 promises a result that does not happen at T+30 min (F1); Pause/Resume silently resets a custom rate (F8). Facilitating a 4-person LAN session needs curl for gates/ROE/undo/clock rate (stated honestly). |
| Blue | Yes on `training-basics` and `leo-isr-denial`; Not unaided on the four newer vignettes | The Tutorial panel shows `command . SAR-1 {"verb":...}` but the Action menu has no `command` (F3). |
| Red | Yes on `training-basics` after one surprise; Not fully on `mt-isr-sar` | An unexplained cyber confirm dialog (F5); the dazzler step cannot be performed in the GUI (F4); `04` Step 6 describes a rejection the UI prevents (F6). |

## Findings

### High

| ID | Artifact | Finding | Exact fix wanted |
|---|---|---|---|
| F1 | `03-first-exercise.md` Step 4 item 4 | States that after three **+10m** (T+30 min) "Red wins (its own objective, `Deny ISR`, is met)". Live (seed 1): `Deny ISR` is `✗` at 06:30Z and 07:31Z and flips to `✓` only after the T+3 h deadline (`deny_delivery` needs `now >= deadline`, 09:00Z; seen `✓` at 09:31Z). A first-time learner sees `✗` after following the text and concludes they did it wrong. The brief says "Hold denial past T+3 h". | Rewrite item 4: Blue stays `✗ Deliver ISR`, Fleet shows `deny (source unknown)`; then click **+1h** three more times and `Deny ISR` turns `✓` only once the clock passes T+3 h. Remove "Red wins" from the T+30 min point. |

### Medium

| ID | Artifact | Finding | Exact fix wanted |
|---|---|---|---|
| F2 | `03` Step 3 | "Blue wins" after a bare downlink with no collect step, while the `leo-isr-denial` brief says collect and downlink are two window problems. It happens to flip because imagery is on board, which the text does not say. | Add one sentence saying why a downlink alone delivers here, or add the observe step. |
| F3 | `04` Step 8 (compose manually); Tutorial panel text for `mt-isr-sar`, `mt-weather-collect`, `nv-isl-relay-debris`, `learn-intermediate-recovery`; `11` entries | The Action menu has no `command` item: verbs are listed one by one (`def.patch_cyber`, `isr.collect_now`, ...). The panel text `command . SAR-1 {"verb":"isr.collect_now","via":"GS-POLAR"}` and `04` "Action `command`, Params {verb...}" cannot be followed literally. Nothing in `04`/`10a`/`11`/`13` explains the mapping. | Add a boxed note in `04` (before Step 8) and `10a`: "the tutorial's `command` + `verb` means choose the verb itself in **Action** and put only the remaining keys (`via`) in Params." Update `04` Step 8's manual compose line. (Owner: authoring; the panel wording is a vignette/UI matter.) |
| F4 | `11` §11.9 Red step 1; in-app `mt-isr-sar` Red step 2 | `RED-DAZZLE` (`directed_energy`) offers only `jam` in the Action menu; **engage** is not selectable, so "engage -> refused `roe_kinetic_not_authorized`" cannot be done in the GUI (only by HTTP). | State it is an API-only illustration, or reword to what the menu shows. Owner: `08-vignette-development`. |
| F5 | `04` Red Step 4 | **Issue order** for cyber raises a browser confirm dialog ("Cyber effect. Covert but escalatory ... Proceed with cyber on ISR-EO-1?"). `04` never says so (02/10a/13/14 do). Cancelling/auto-dismiss gives `cancelled (consequence not confirmed)`. | Add "a confirmation box appears; click OK". |
| F6 | `04` Red Step 6; `11` §11.0 | Says the engage is "REJECTED". Live the **Issue order** button is disabled and the preview reads "✗ ROE does not authorize kinetic effects." (the code text is correct in 09a/13a/14a). | Reword: "the preview turns red with ..., **Issue order** is disabled". |
| F7 | `16` Stage 3 (five `coa-*` rungs); `11`; `15.4` | The five Red COA rungs link no playbook and `11` has no entry for them (11.0-11.13 = 14 of 19 vignettes); `15.4` says every rung links its playbook (FR-11320). `15.4` also has no per-vignette table, so the three-way linkage cannot be checked from `15`. | Either add one short COA playbook section, or state in `16`/`11`/`15.4` that COA rungs are un-scripted (no tutorial block) by design; add a vignette column table to `15.4`. Owner: `08-vignette-development` + authoring. |
| F8 | `12d` bullet "Pause / Resume only starts and stops the shared clock" | Not true for the rate: **Resume** posts `{running:true}` and the server returns `rate: 1.0`. Live: rate 60 -> Pause (60) -> Resume (1.0). A facilitator running at 60x loses it silently. | Add: "Resume resets the rate to 1; re-send the rate by HTTP after every Resume." Also file a code bug (`00-intake`). |
| F9 | `15-manual-traceability.md` §15.1 | Coverage-check misses (see below): FS-123, FS-124 have no row; FS-129 partial; the table cites no FS/IP/FR id, so the new skill's FS->15.1 check cannot be scripted and was done by title/keyword. | Add a `Spec` column (FS/FR ids) to 15.1; add rows for FS-123 and FS-124; mark FS-133/134/135 "not operator-visible". |
| F10 | `09` glossary | Terms used in the manuals but absent from the glossary: SOH, TLE (defined inline only), RIC, CATS, SSN, TDOA/FDOA, hot-seat, seed, LVLH, A2/AD (undefined anywhere), Gantt. NFR-3600 wants jargon introduced or glossary-linked. | Add entries; the glossary must carry each term used in a role manual. |

### Low

| ID | Artifact | Finding | Exact fix wanted |
|---|---|---|---|
| F11 | `03` | Button is **Issue order**, not **Issue**; **Rewind** returns to 06:00:01Z, not 06:00:00Z; Step 1's "Fleet panel" is titled FLEET SOH ROLLUP. | Correct names/time. |
| F12 | `09a` | Console strings are quoted with " - " but the app uses an em dash (" — "); an exact-text search of the page fails. Other strings match the source. | Use the em dash. |
| F13 | `12` WCM-3 | Menu item is **Pop out (multi-screen)**; text says **Pop out ▸**. | Name it as shown. |
| F14 | `learn-intermediate-recovery` Blue step 2 | Needs Red to have fired first; a solo learner must switch seat; stated but easy to miss. | Move the dependency to the title. |
| F15 | `04` Blue Step 1 | Says objectives read "pending"; UI shows `✗`. | "show ✗". |

## The author's reported findings: does the manual say it honestly, and is it a defect?

| Behaviour | Manual | Verdict |
|---|---|---|
| Creator role matrix not saved, `roles_needed` always [] | `12b` line 88 and `12c` line 23 state it | Honest. Product gap (Medium, code); acceptable for the release if the text stays. |
| Saved vignette invisible unless `user_save_dir` is in `external_vignette_dirs` | `12b` lines 32-37 | Honest. Acceptable. |
| `/start` works on a draft | Not stated (verified live: 200 ok) | Not stated; Low code defect, route to `00-intake`; manual silence acceptable. |
| `roles/assign` accepts unknown asset / junk role | Not stated (the HTTP body names `asset_or_constellation`; my junk-field call returned 422, the accept-junk claim is **not** reproduced by me for a well-formed body) | Unverified; Low. |
| `bulk_import` after Start returns `[]` with no reason | `12d` line 139 says so (verified live: `[]`; `force/tle` gives `cannot edit force after start`) | Honest. Low code defect (give a reason). |
| Pause/Resume resets custom rate | **Not stated and the text implies the opposite** (F8) | Medium. |
| Jammed command still shows "executed" | `13a` line 94, `14a` line 78, `09` line 42 | Honest and well explained. Acceptable (design). |
| Gate approval / ROE / undo / clock-rate are HTTP-only | `12`, `12c`, `12d` | Honest. A real usability gap for a newcomer facilitator (they need curl); acceptable if intended. |
| Observer check reads body cell only | Manual says "the request names the seat" (`12d` line 25); live: `?cell=observer` is refused (403) | Manual accurate for the query form; the body-versus-query nuance is not stated. Low. |

## Author corrections spot-checked

- WCM-7 "force-add only between Load and Start": confirmed (`force/tle` after Start -> `ok:false, cannot edit force after start`; before Start ok). The refusal is an `Ack`, not an HTTP error; the text is fine.
- RED-5 salvo: consistent with the code summary (fired salvo charged hit or miss); not re-fired.
- `03` UI wording: Session menu, Vignette/Seed/Load/Start, seat buttons, Actor/Action selects, `Advanced (raw JSON params)` pre-filled `{"via":"GS-NORTH"}`, green `✓ will queue . ground_uplink . window 2030-03-15T06:05:19Z`, hints `no known targets yet ...` and `type id - untracked ok`, the +1m/+10m/+1h/Rewind buttons vanishing on Blue: all exact (see F11, F1 for the exceptions).

## Tutorials and timings (executed in the GUI)

- `training-basics` Blue: custody `✓ Keep Custody` by 06:40, `✓ Deliver ISR` by 06:50 (window 06:43:51): matches `04`. Red: observe/jam queue as stated, cyber `✓ Disable ISR` after +1m (seed 1), `✓ Deny ISR` after T+1 h; recovery strip shows **Begin recovery** and **Patch (def.patch_cyber)**. Ordering works.
- `mt-isr-sar`: Red jam window 22:17, Blue pass 22:18:30, `collect_sar` stays `✗` under jam, `✓ Survive` at T+90, `✓ Deny Downlink` for Red: as stated.
- `mt-weather-collect`: `✓ Deliver WX` by 00:40, `✓ Wx OP` at T+70, Red `✓ Track BLUE` then `✗` after decay: as stated.
- `nv-isl-relay-debris`: maneuver queues on `isl_relay`, both objectives `✓` at 03:40: as stated.
- `learn-intermediate-recovery`: Red cyber lands (seed 1); patch queues on the GS-LEARN pass; `✓ Recover TO Nominal` by 11:00. Step 4 is a drill-down **Begin recovery** button, not an order: stated in the text.
- `mt-sigint-geolocate` Blue limitation (`characterize_emitter` unreachable by orders) is stated plainly in `11` lines 258-259 and `16` line 70: honest.

## Traceability integrity

- Both directions of `15.1`/`15.2` to the module headings: every `WCM-n`/`BLU-n`/`RED-n` cited in `15` resolves to a heading and every such heading is cited (scripted: no orphans either way). `Sources:` footers resolve (`test_training_sources.py` green).
- `15.4`/`16`/`11`: all 19 vignette ids appear in `16`; 14 of 19 in `11`; none in `15` (prose only). Gap F7.
- Coverage check (VERIFIED FS specs against `15.1`; matching was by title/keyword because 15.1 cites no FS ids):
  - Medium misses: **FS-123** space-weather index coupling (no row; only White mentions it, Blue/Red none); **FS-124** debris persistence estimate (no row; operator-visible display); **FS-129** jam delivery/effect detectability (a delivery-path row exists; the detectability/attribution configuration has no row).
  - Low: **FS-114** hot-seat hand-off (only inside a combined transport row); **FS-133, FS-134, FS-135** (developer/test checks) lack an explicit "not operator-visible" statement.
  - Excluded: FS-108 (candidate, no package) and FS-202 (no package).
  - All other VERIFIED specs (FS-101 to FS-122, FS-125 to FS-128, FS-130 to FS-132, FS-201, FS-301) map to at least one manual section.

## Pedagogy

Sequencing 01 -> 02 -> 03 -> 04 -> role manuals is workable and the 03 branch-and-rewind lesson is strong. Weaknesses: the first-exercise promise is wrong at the key moment (F1); glossary gaps (F10) against NFR-3600; the role manuals run 270-290 lines each plus a/b/c/d satellites, which is long for a first read but modular (NFR-3500 not contravened); the tutorial text is terse by design and relies on the learner translating `command`/`verb` (F3). R600 not cited by this review; sequencing judgements here are "ungrounded, pending R6xx" where not obvious.

## Routing

F1, F2, F5, F6, F8, F9, F10-F13, F15: `08-training-manual-authoring`. F3 (panel wording), F4, F7, F14: `08-vignette-development`. F8 code behaviour, `/start` on draft, `bulk_import` reason: `00-intake`. Next step: authoring pass for F1 first, then re-review `03`/`04` and `10-integration-review`.
