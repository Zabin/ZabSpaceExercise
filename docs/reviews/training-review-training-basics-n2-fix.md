[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — `training-basics` N2 Fix (tutorial timing, cyber chance, ROE notes, machine checks)

> **Document ID:** REV-TRN-009
> **Skill:** `09-training-manual-review`
> **Scope:** `ade5f66` on `claude/tutorial-fix-1` (diff vs `claude/release-candidate-1`):
> `spacesim/content/vignettes/00-training-basics.yaml` (tutorial blocks, `intro_brief`, ROE notes);
> `docs/training/04-guided-vignette.md`, `11-vignette-playbooks.md` §11.0, `15-manual-traceability.md`
> (one row), `16-learning-path.md` (Stage 0 rung); the new tests in
> `spacesim/tests/test_vignette_tutorials.py`. Closes release-assessment N2.
> **Independence:** fresh agent context; no part in authoring `ade5f66`.
> **Upstream:** `08-vignette-development` · **Downstream:** `10-integration-review`, `11-release-readiness`

## Headline

N2's three defects are fixed in substance and now machine-checked: Red's cyber step is chance-based with a
retry instruction, Blue's confirm-objective step precedes the post-deadline maneuver, and both briefs say
cyber is ON by default (parameter default is `true`). Driven live over HTTP (`TestClient`) as White/Blue/Red,
seeds 0, 1, 2, 3, 7, 11, every objective flip and the T+1 h timing behaved as the new text says. **No
Critical/High.** 4 Medium, 3 Low — most notably a numeric error ("about T+10 h", actual T+11.08 h) that is
repeated in five places and that no test pins.

## What was exercised

- **Accuracy (live).** Blue: observe -> downlink -> `+10m` clicks. `keep_custody` MET at T+40 min,
  `deliver_isr` MET at T+50 min (window T+43.9-52.3 min), both True at T+60 min, `keep_custody` False
  at T+70 min — identical on all 6 seeds. Maneuver window T+11.08-11.18 h (39 879 s), debits 5 m/s.
  Red: jam always queues; `deny_isr` True once past T+1 h on every seed with the bird never safed;
  cyber needed 2, 1, 3, 1, 1, 1 attempts (seeds 0, 1, 2, 3, 7, 11), `/cyber/compute` = 0.625;
  `RED-ASAT` engage -> `rejected roe_kinetic_not_authorized`. Parameter defaults: `cyber_authorized=true`,
  `red_kinetic_authorized=false`. Red brief names (`ISR-EO-1`, jam target) now match the orders.
- **Release-assessment N2 claims.** (a) Red step 4 safe-mode promise: closed. (b) Blue maneuver-after-deadline
  / "custody held": closed in structure, but the replacement number is wrong (F1). (c) ROE note "Cyber OFF":
  closed in both briefs. (d) "not machine-verified": closed for this vignette (F5 for residual gaps).
- **Traceability.** Relative links in the touched files resolve; `15` row names `test_vignette_tutorials.py` and
  `test_training.py`, both exist; `16` rung links `04` and `11` §11.0 (exists); `11` §11.0 is the only
  `training-basics` playbook entry and the rung is unique. Neither `04` nor `11` carries a `> Sources:` footer
  (pre-existing; not required by `test_training_sources.py`).
- **Tests.** Mutation (YAML restored after each): full revert to the release-candidate YAML -> 7 failures
  (Blue order test, 4 Red seeds, ROE test x2); Red step 4 old wording -> Red tests fail; Blue maneuver step
  moved before confirm -> Blue test fails; Blue ROE note back to "Cyber OFF" -> ROE tests fail; dropping
  "deadline" from the maneuver expect -> Blue test fails. **Not caught:** changing "about T+52 min" to
  T+99, "about T+10 h" to T+2 h, `ISR-EO-1 safed` to `BLUE-SAT safed`, or Red `threat_picture` back to
  "Jam GS-TRN" (all passed — see F1, F5). Strict xfail verified real: fixing `mt-isr-sar`'s note to T+90 min
  makes its entry XPASS(strict) -> FAIL, forcing removal.
- **Suites (real exit codes).** Unfiltered `pytest`: exit 0; junit 1830 tests, 0 failures, 0 errors, 10 skipped
  (7 xfail + browser skips). `test_vignette_tutorials.py`: 60 collected, 53 pass + 7 xfail. By name,
  exit 0: `test_doc_integrity`, `test_test_origins`, `test_training`, `test_training_sources`,
  `test_determinism`, `test_import_guard`.

## Author decision needed — 7 strict-xfail brief/deadline disagreements

Each brief's `deadline_note` and `landing_window_start_s` (the deadline the engine scores) disagree; the
two cells' notes agree with each other, so the YAML parameter vs the brief is the question (which is
intended?). The strict xfail will force a fix (XPASS fails the suite) but does not say which side is right.

| Vignette | Brief says | `landing_window_start_s` |
|---|---|---|
| `geo-rpo-shadowing` | T+90 min (5400 s) | 7200 |
| `co-orbital-threat-escort` | T+90 min (5400 s) | 3600 |
| `coa-china-md` | T+75 min (4500 s) | 2700 |
| `coa-china-ml` | T+60 min (3600 s) | 1800 |
| `mt-isr-sar` | T+30 min (1800 s) | 5400 |
| `mt-sigint-geolocate` | T+45 min (2700 s) | 3600 |
| `mt-weather-collect` | T+30 min (1800 s) | 3600 |

**"Observe steps queue past the deadline" (reported, not fixed; no test covers it).** A dry-run of each
vignette's tutorial orders at T+0 shows the first sensor window opening after the deadline for:
`gnss-ew-campaign` blue step 2 (BLUE-RADAR, T+9 286 s vs 3600 s), `co-orbital-threat-escort` blue 2
(T+36 202 s vs 3600), `da-asat-crisis` red 2 (RED-RADAR, T+29 780 s vs 3600), `sda-custody-hunt` blue 2
(T+8 032 s vs 5400) and blue 4 (BLUE-OPT-1, T+14 154 s vs 5400). Some may be intended (long-horizon
objectives); needs a per-vignette author decision.

## Findings

| # | Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|---|
| F1 | Maneuver pass time is wrong | `00-training-basics.yaml` Blue step 6 (`when`, `expect`); `04` Step 6; `11` §11.0; `16` Stage 0 | All say "about T+10 h" / "about 10 h out"; the pass is T+11.08-11.18 h (seeds 0-11 identical; the release assessment itself said ~11 h). The point (after the deadline) still holds, but it is a new factual error in the fix. | Medium | `08-vignette-development` (YAML) + `08-training-manual-authoring` (04/11/16) |
| F2 | `04` Red Step 3 params disagree with the in-app script | `04` Red Step 3 vs YAML/`test_training.py` | `04` shows `{"success_prob":1.0,"outcome":"deny"}`; the Tutorial panel, the test and §11.0 use `{modulation: barrage, power_w: 200.0}`. Both are accepted by the engine, but a learner switching between manual and panel sees two recipes. Pre-existing; missed by this pass though `04` was edited around it. | Medium | `08-training-manual-authoring` |
| F3 | Red is told to retry but not how to see a failure | YAML Red step 4/5; `04` Red 4-5; `04` Blue 7 onward | Cyber resolves after issue; nothing says to advance ~1 min and check the Objectives panel / bus mode, and step 5 then jumps to T+1 h. The Blue "recover from the cyber attack" half opens "Red's cyber flipped `ISR-EO-1`" with no branch for a failed attempt. | Medium | `08-training-manual-authoring` / `08-vignette-development` |
| F4 | `keep_custody` lapses one click after the deadline | `04` Blue 4-5, YAML Blue 4-5 | With `+10m` clicks, T+60 min is the last tick with `keep_custody` MET; T+70 min flips it False. Step 4 says "click until past the window" (T+52, so the 6th click); one extra click shows a red `keep_custody`. "Both are scored at the deadline" is true only if the panel is read at T+60; the panel is live, not latched. Add "stop at T+60" wording. | Medium | `08-vignette-development` |
| F5 | New tests pin behaviour, not the numbers/names the fix is about | `test_vignette_tutorials.py` | Cyber step passes on keyword ("chance"); no test pins ~62% (engine 62.5%), T+52, the maneuver time (F1 would have been caught), the corrected Red brief names, or the YAML <-> `04`/`11`/`16` prose. `test_training.py` still asserts seed-1 cyber success unconditionally. | Low | `08-vignette-development` |
| F6 | Duplicate objective in the Red list | `00-training-basics.yaml` objectives.red | `disable_isr` is declared twice (pre-existing). | Low | `08-vignette-development` |
| F7 | Optional post-deadline maneuver is hard to act on | `04` Blue 6 | Honestly labelled optional and explained; but at `+10m` the learner needs ~66 clicks to see the 5 m/s debit, so "the point is plan-first" is only demonstrable via the order queue. Not misleading; teachable. Also image files 22/23 are now out of numeric order with the steps (correct pairing, regeneration by `tools/render_manual.py` would not shift it). | Low | `08-training-manual-authoring` |

R600 grounding: scaffolding/ordering choice here is not cited to an R6xx topic — recorded as "ungrounded", not a violation.

## Next step

`08-vignette-development` for F1/F4/F6 and the xfail/observe author decisions; `08-training-manual-authoring`
for F2/F3/F7; then re-review. Only after F1 is corrected should `10-integration-review` rely on §11.0.
