[↑ Docs index](../INDEX.md) · [Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md) · [Previous gate](training-review-final-rc8.md)

# Training review (REV-TRN-013): delta learner-walkthrough gate for release candidate 11

Independent fresh-session review (authored none of this). Commit reviewed: `70fb36c` (branch `claude/release-candidate-11`; worktree `claude/training-review-rc11`). Review-only: no prose, YAML or code was changed. Scope: everything that changed in `docs/training/`, the vignette YAML and `test_vignette_tutorials.py` since REV-TRN-012 (`92c56c8`), i.e. commits `78417d6`, `96b313c`, `62ef8a0`, `70fb36c`, to close conditions C-1 and C-2 and finding F-1 of `release-assessment-release-candidate-10.md`.

**Method.** `uvicorn` on loopback from the worktree plus headless Chromium (`/opt/pw-browsers/chromium-1243`), Seed 1, driven as a first-time learner: HTTP calls for the same orders the console issues, and the real console form for every preview and panel claim.

## Verdict

**The learner-walkthrough review is now current for this release scope (`70fb36c`), with no open High findings.** 0 High, 1 Medium, 2 Low. C-1, C-2 and F-1 are closed (F-1 with one residue, L-1).

| Role | Verdict | Why |
|---|---|---|
| White | Yes | The new WCM-6 Compare procedure works as written, except one false closing sentence (M-1). WCM-22 `save_format` echoes read as quoted. |
| Blue | Yes | The two Blue tutorial previews match the live form. |
| Red | Yes | `11.15` and `11.17` ordered recipes work literally on Seed 1. |

## Closure of the release-assessment conditions

| ID | Status | Evidence |
|---|---|---|
| **C-1** learner-walkthrough gate not current | **Closed** | This review reads all four post-`92c56c8` commits and drove each changed procedure live (below). No High. |
| **C-2** `BL-0286` Compare panel missing from WCM-6 | **Closed in substance** | WCM-6 now has a numbered Compare procedure; title, three columns, refresh and worked example all match the app. One sentence is wrong (M-1), which is a correction, not a gap. |
| **F-1** `15` §15.3 called a manual review step an automated test | **Closed, one residue (L-1)** | The sentence now says there is no repository test for the §15.1 coverage check. Confirmed true: no test file under `spacesim/tests/` reads `15-manual-traceability.md`. All four tests named exist (`test_vignette_tutorials.py`, `test_training_sources.py`, `test_doc_integrity.py`, `test_test_origins.py`). |

## What was driven, and what happened

| Item | Result |
|---|---|
| `11.15` `coa-russia-md`, Seed 1, followed literally (observe, +10m x2, engage, +10m, then cyber) | `destroy_isr` true at the first +10m check after the engage (T+30; the playbook's "T+26" is the finer-grained time). First `seize_c2` attempt did not land, the second did: `safe_satcom` true, Blue `satcom_op` false. As quoted. |
| `11.17` `coa-china-md`, Seed 1 (observe, +10m x2, engage, +10m, then jam and cyber) | `kill_isr`, `deny_pnt`, `safe_satcom` all true. The trap (jam and cyber queued right after the engage, then three +10m) leaves `kill_isr` false, as the text warns. |
| Tutorial previews: `04` Blue step 4 (`BLUE-HVA`), `04` Red step 2 (`RED-COORB`), `05` Blue step 2 (`BLUE-SAT`), `07` Red step 3 (`RED-OBJ`), using the maneuver assistant (Δv Y = 5) in the console | All four show `✗ No access window in the planning horizon — wait for the next pass.`, **Issue order** greyed out, and Params default to `via: GS-NORTH`. The alternative text ("No command path") appears when `via` is absent: the validate route returns `no_command_station` for bare `{dv:[0,5,0]}`, so the "(or ...)" in the YAML is accurate. |
| WCM-22 / `09a` `save_format` | `'2'`, `True`, `None` and `3` each return HTTP 400 `save_format <value> is not supported; supported formats: legacy (absent), 2`, with the value echoed as quoted. |
| Five `09a` refusals spot-checked | White-seat refusal (403), Observer read-only (403), `unknown session sess-999` (404), `unknown cell 'purple'` (400), `vignette 'nope' not found` (404), `cannot change parameters after start`, `step cannot move time backwards ...`, and the `t1: ... is not an ISO-8601 UTC timestamp` message: all match. |
| `15` §15.3 | Every named test exists; the claim about the coverage check being a script is true. |
| Coverage script (every FS whose packages are all VERIFIED appears in §15.1 with a section or reason) | 23 of 23 all-verified FS specs (of 36 listed) present; no misses. |
| Bidirectional traceability | 60 `WCM`/`BLU`/`RED` ids in `15`, all defined as headings, and every heading appears in `15`; all 19 vignettes in `15.4`; `test_training_sources.py` green. |

## The Compare panel and the View menu: the truth

Driven as White, then Blue and Observer.

- Title `⚖ Compare — truth beside each cell's picture`; collapsed at first; **🔄 Refresh** fills `at 2030-...Z` and three columns **Truth**, **Blue's picture**, **Red's picture**. Matches WCM-6.
- Worked example reproduced exactly: Training: Basics, Blue tasks `RADAR-TRN` on `RED-TGT`, 40 minutes in: Truth lists six assets; Blue shows `own: ISR-EO-1, GS-TRN` plus the track `RED-TGT` at confidence 1.00; Red has no tracks.
- Blue and Observer screens do not show the panel or a Compare menu item. `GET .../controller_view?cell=blue` and `?cell=red` return 403 `only White Cell may open the controller view`.
- **The closing sentence is false.** The panel does have a View-menu entry. After clicking its **✕** the panel disappears; **View ▾ → Panels → "Compare (truth / Blue / Red)"** (a checkbox, unticked after ✕) brings it back, and a second ✕ and **↺ Reset layout** also restore it. The same Panels list holds "Competency assessment" for White only. VR-1069 is right; the new WCM-6 text is wrong.

## Findings

| ID | Severity | Finding | Exact fix wanted |
|---|---|---|---|
| **M-1** | Medium | `12-white-cell-manual.md` WCM-6, Compare bullet: "(It has no entry in the View menu; if you closed it with its ✕, **View ▾ → Reset layout** brings it back.)" The first half is false and sends the learner to the heavier remedy (Reset layout also undoes every other panel move). Owner: `08-training-manual-authoring`. | Replace with: "(If you closed it with its ✕, tick **Compare (truth / Blue / Red)** under **View ▾ → Panels** to bring it back; **View ▾ → Reset layout** also restores it, along with every other panel.)" |
| **L-1** | Low | `15` §15.3 (line ~260-262): the F-1 fix inserted sentences, so the following "Since 2026-10-25 it also drives the five Red COA recipes ..." now reads "it" as the learner-walkthrough review, not `test_vignette_tutorials.py`. The same dangling pronoun F-1 named. | Start the sentence "Since 2026-10-25 `test_vignette_tutorials.py` also drives ..." (or move the gates sentence after it). |
| **L-2** | Low | `11` §11.15 step 3 says "driven live: ✓ at T+26" but a learner clicking **+10m** from T+20 first sees the tick at T+30; §11.17 has the same pattern. A learner may think a check at T+30 is late. | Add "(you will see it on the first **+10m** click that passes T+26, that is at T+30)". |

No High and no Medium other than M-1. M-1 is a one-sentence correction and does not block a learner finishing; it does mean WCM-6 carries a statement the app contradicts.

## Gates run

`test_doc_integrity.py`, `test_training_sources.py`, `test_training*.py`, `test_vignette_tutorials.py`, `test_test_origins.py`: 163 passed, 1 skipped (browser-marked tests deselected here; the full unfiltered result at this commit is 2244 passed / 4 skipped per the candidate record).

## Is the learner-walkthrough review now current for this release scope, with no open High findings?

**Yes.** This review (REV-TRN-013, `70fb36c`) reads every change to `docs/training/` and vignette YAML since REV-TRN-012 and drove each on the live app. There is no open High finding. Condition C-1 is closed; C-2 is closed in substance; F-1 is closed. Three residual items (M-1 Medium, L-1 and L-2 Low) are routed to `08-training-manual-authoring` and should be fixed before the next review but do not block the release gate.
