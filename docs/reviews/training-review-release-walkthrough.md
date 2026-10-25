[← Reviews index](INDEX.md)

# Training review: release learner-walkthrough gate (PARTIAL, in progress)

Reviewer: independent fresh session. Commit reviewed: `c50b6da` (branch `claude/manuals-catchup-1`). Driven live: uvicorn on loopback + headless Chromium (Playwright). Findings below are provisional and will be extended.

## Findings so far

| # | Sev | Artifact | Finding | Fix wanted |
|---|---|---|---|---|
| 1 | High | `03-first-exercise.md` Step 4 item 4 | Says that after three **+10m** (T+30 min) "Red wins (its own objective, `Deny ISR`, is met)". Live: `Deny ISR` stays `✗` until the T+3 h deadline passes (`deny_delivery` needs `now >= deadline`, 09:00Z); verified `✗` at 06:30, 07:31 and `✓` only at 09:31. | Rewrite: Blue's objective stays `✗`; Red's `Deny ISR` flips only after T+3 h (+1h x3). |
| 2 | Medium | `03` Step 3 | "Blue wins" after only a downlink; the brief says collect and downlink are two window problems. | Say what is actually delivered or add the observe step. |
| 3 | Medium | `04` Step 8; tutorials for `mt-isr-sar`, `mt-weather-collect`, `nv-isl-relay-debris`, `learn-intermediate-recovery` (Tutorial panel text `command · SAR-1 {"verb":...}`) | The Action menu has no `command` entry: bus/payload verbs are listed individually (`def.patch_cyber`, `isr.collect_now`). Nothing in `04`/`11`/`13` tells a learner how to translate `command` + `verb` into the menu. | Add one sentence + example to `04` and `10a`: pick the verb itself as Action; the `verb` key is implied. |
| 4 | Medium | `11` mt-isr-sar Red step 1 / in-app tutorial Red step 2 | `RED-DAZZLE` (kind `directed_energy`) offers only `jam` in the Action menu; **engage** cannot be chosen, so the "refused `roe_kinetic_not_authorized`" step cannot be performed in the GUI. | State it is API-only, or reword the step to what the GUI shows. |
| 5 | Medium | `04` Step 4 | Cyber **Issue** opens a browser confirm dialog ("Cyber effect. ... Proceed with cyber on ISR-EO-1?"); `04` never mentions it (documented in 02/10a/13/14). Dismissing it silently cancels the order. | Add "click OK on the consequence dialog". |
| 6 | Low | `04` Step 6 | Describes **REJECTED**; the real UI pre-disables **Issue order** and shows "✗ ROE does not authorize kinetic effects." (accurate in 09a/13a/14a). | Align wording. |
| 7 | Low | `03` | Button is **Issue order**, not **Issue**; Rewind returns to 06:00:01Z, not 06:00:00Z. | Fix names/time. |

Verified OK live: 01 launch command; 03 Steps 1-2 and the rewind/branch flow (labels, hints, preview text, `queued . ground_uplink . window 2030-03-15T06:05:19Z`); 04 Blue Steps 1-5 (Keep Custody and Deliver ISR flips, T+60 min stop), Red Steps 2-5, Blue recovery strip (**Begin recovery**, **Patch (def.patch_cyber)**); `mt-isr-sar` Blue/Red timings (jam window T+17, pass T+18.5, `collect_sar` unmet under jam, `deny_downlink` met, `survive` met). `test_vignette_tutorials.py` + `test_training.py`: green.
