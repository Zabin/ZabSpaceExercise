[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — Runs #107 and #109 Scope (Target Picker, Export Bounds, Red Bus Reality, White Drill-Down)

> **Document ID:** REV-TRN-004
> **Skill:** `09-training-manual-review`
> **Scope:** the sections two `08-training-manual-authoring` runs touched:
> - **Run #107** (commit `2778526`, closing `BL-0084`/`BL-0177`/`BL-0178`/`BL-0180`/`BL-0182`):
>   `10-ui-reference.md` §10.5 row 5, §10.6 row 4 and the screenshot note; `WCM-15`/`WCM-16`
>   (including the `WCM-6` → §10.13 cross-reference fix); `BLU-13`/`BLU-14`; `RED-12`/`RED-13`;
>   their `> Sources:` footers; `15-manual-traceability.md` §15.1 rows 79–80 and six §15.2 rows.
> - **Run #109** (commit `ef3b6e6`, closing `BL-0186`/`BL-0189`/`BL-0190`): the `RED-7` rewrite,
>   the `RED-13` example, the `WCM-6` any-asset drill-down bullet, the `RED-7`/`WCM-6` footers,
>   the §15.1 telemetry row, and the §15.2 `WCM-6`/`BLU-6`/`RED-7` rows.
>
> Each touched section was read whole, not just the changed lines. Shared onboarding modules that
> describe the same controls (`03`, `04`, `11`) were sampled for coverage (dimension 3).
> **Commit reviewed:** `1887dd6` (branch `claude/chart-prompt-file-90hm9u` tip at review time;
> no commit after `ef3b6e6` touches `docs/training/`).
> **Independence:** this session authored neither run #107 nor run #109, nor any other commit on
> this branch before this review.
> **Upstream:** `08-training-manual-authoring` (runs #107, #109) · **Downstream:**
> `10-integration-review`, `11-release-readiness`

## Headline

Both runs' prose is **accurate against shipped behaviour**, checked in code and driven live on a
fixture different from the authors' and the shipped tests'. Traceability is consistent in both
directions. The playbook suite passed 16/16. **No Critical or High findings.** Two findings, both
outside the two runs' own edits: the shared onboarding modules still describe the target control
as it was before the picker shipped (F1 Medium, F2 Low).

## Dimensions exercised

### 1. Accuracy — prose claims vs. shipped behaviour

**Code reads** (at `1887dd6`): `ui_web/static/app.js` (`TARGET_REQUIRED_ACTIONS`,
`buildTargetGroups`, `targetOptionsHtml`, `populateTargetPicker`, `planTask`, the compose-form
`target` resolution, `renderFleet`, `rollup`, `openDrill`, the `#assets` row-click handler);
`ui_web/static/index.html` (the `or id` inputs; no `<datalist>` anywhere); `session/ephemeris.py`
(`sample_times`, `MAX_EXPORT_SAMPLES`); `ui_web/server.py` (the export routes' `interval_s`
declarations); `engine/telemetry.py` (`_active`, `_baseline`, `_attack_term`).

**Live drives** through the HTTP API (`TestClient`), on **`multi-domain-taiwan` seed 11**, stepped
one hour. The shipped route tests use `leo-isr-denial` seed 1; run #107 used the same family.

| Claim (section) | Result |
|---|---|
| Ephemeris routes reject `interval_s` `0`/`-1`/`nan`/`inf` with 400 (`WCM-15`, `BLU-13`, `RED-12`) | **Accurate.** `/ephemeris/truth` and `/ephemeris/blue` both return 400 for all four. |
| The telemetry export refuses `0`/`-1`/`nan` with **422** and `inf` with 400 (`WCM-16`, `BLU-14`, `RED-13`) | **Accurate.** 422/422/422/400. The 422 comes from FastAPI's `Query(gt=0)`. This is the by-design split recorded under `BL-0184` (`REJECTED`, per `VR-1262`); the manual describes it truthfully. |
| Over 10,000 instants → 400 naming the smallest `interval_s`, "about 0.36 s for a one-hour span" (`WCM-15`/`16`) | **Accurate.** `interval_s=0.1` over 3,600 s returns 400 on both export families: `requested sampling yields 36001 instants … use interval_s >= 0.360038`. The suggested 0.37 s returns 200. |
| Default sampling is span/100, floored at one bus tick, "so at most 101 rows" (`WCM-15`) | **Accurate.** The default truth export over 3,600 s returned 13 rows. The bus-tick floor dominates span/100 = 36 s, so the count is well under the 101 ceiling. |
| Naming your own asset in the cell-observed export returns the header only (`BLU-13`, `RED-12`) | **Accurate**, on both sides: `/ephemeris/blue` on `ISR-EO-1` and `/ephemeris/red` on `RED-INSP` each returned exactly one line. |
| White can export any asset's telemetry; Blue/Red only their own (`WCM-16`) | **Accurate.** `/telemetry/white/RED-INSP/export.csv` returns 200 with 134 lines (7 instants × 19 parameters + header). The same request as `blue` returns 404. |
| White can open the drill-down for any fleet row, Blue or Red (`WCM-6`) | **Accurate.** The `#assets` click handler calls `openDrill(asset)`, which fetches `/telemetry/${CELL}/…`. Live: `/telemetry/white/RED-INSP` returns 200 with subsystems; `/telemetry/blue/RED-INSP` returns 404. The "symptom log" wording matches the drill-down's *Subsystem log (symptoms — …)* heading. |
| No shipped vignette gives a Red satellite a bus (`RED-7`) | **Accurate.** All 19 shipped vignettes were built through `build_world()`: 15 Red space assets (satellite/space-based/interceptor), and none has a `bus_state`. |
| A bus-less asset shows `—` for bus mode and battery, and an uncoloured health dot (`RED-7`) | **Accurate.** `renderFleet` writes `—` for both when `a.bus_state` is absent, and `rollup(undefined)` returns `""` (no colour class). |
| Blue's jam/cyber/DE effects still leave signatures on a bus-less Red satellite (`RED-7`, `RED-13` example) | **Accurate.** `_active` reads flags from `world.active_effects` with no bus check, and the `rx_power`/`cn0`/`ber`/`uplink_lock`, `cpu_load`/`fsw_error`/`cmd_reject` and `snr`/`optics_temp` terms fire on those flags alone. Live: `/telemetry/white/RED-INSP` returns a full subsystem set with `bus_mode: null`. |
| Target picker (§10.5 row 5, §10.6 row 4): known-target dropdown plus an `or id` box that takes precedence; enabled only for `jam`/`engage`/`cyber`/`observe`; the actor's own side left out; White tasks as Blue and sees every non-Blue asset; empty-state text; Plan collection falls back to the compose target | **Accurate**, line by line. Precedence: `$("o-target-manual")?.value \|\| $("o-target").value` and `$("task-target-manual")?.value \|\| $("task-target").value \|\| …`. Gating: `TARGET_REQUIRED_ACTIONS`. Exclusion: `buildTargetGroups(actorOwner)` and `buildTargetGroups(CELL === "white" ? "blue" : CELL)`. Empty-state text: `no known targets yet — …`. Fallback: `planTask`'s third and fourth operands. Targetable kinds match `TARGETABLE_KINDS`. |
| Screenshot note: `ref-05`/`ref-06` predate the picker (§10.6) | **Accurate** as a caveat. Regenerating them is tracked separately (`BL-0185`, `DEFERRED`). |

No claim in either run's scope was found inaccurate.

**Playbook verification suite** (FR-11420/NFR-3400):
`python3 -m pytest spacesim/tests/test_vignette_tutorials.py` → **16 passed** at `1887dd6`.

### 2. Traceability integrity

Checked with a script over `docs/training/` at `1887dd6`:

- Every `WCM-n`/`BLU-n`/`RED-n` ID cited in `15-manual-traceability.md` exists as a heading in
  `12`/`13`/`14`, and every such heading has a §15.2 reverse row. **0 orphans** in either
  direction.
- Every relative `.md` link in `training/10`–`16` resolves. The new
  `10-ui-reference.md#1013-subsystem-drill-down` anchor (used by `WCM-6` and `WCM-16`) matches
  the `### 10.13 Subsystem drill-down` heading.
- Every literal `spacesim/…` path in the three role manuals' footers exists. The only
  non-literal matches are the pre-existing brace-expansion shorthands
  (`engine/{maneuver,isr,jam}.py`, `engine/{jam,engage}.py`). Each expanded file exists, so these
  are not defects.
- Every symbol the new footers name exists where cited: `ephemeris.sample_times`,
  `ephemeris.MAX_EXPORT_SAMPLES`, `aar.worlds_at_times`, `manager.get_telemetry`/`get_series`/
  `telemetry_export`, `app.js::openDrill`/`renderFleet`/`rollup`.
- **Footer ⇄ §15.2 consistency**, for every row in scope: `WCM-6`, `WCM-15`, `WCM-16`, `BLU-6`
  (the series route now in both), `BLU-13`, `BLU-14`, `RED-7` (`app.js` and the vignette YAML
  now in both), `RED-12`, `RED-13`. Each §15.2 row is a faithful subset of its footer.
- **§15.1 ⇄ §15.2**: rows 79–80 (ephemeris and telemetry export) name `WCM-15`/`BLU-13`/`RED-12`
  and `WCM-16`/`BLU-14`/`RED-13`, with backing code matching the reverse rows. The telemetry-
  signatures row now names `WCM-6` for White, closing `BL-0189`'s gap in both directions.

Clean.

### 3. Coverage

- **Role reach (FR-11110).** The export bounds reach all three roles (`WCM-15`/`16`, `BLU-13`/`14`,
  `RED-12`/`13`). White's any-asset drill-down now has a `WCM-n` home (`WCM-6`). The target
  picker is documented once, in the shared UI reference (§10.5/§10.6), which every role's manual
  links to. That is adequate role-scoped reach for a control whose behaviour does not differ by
  cell beyond the side exclusion §10.5/§10.6 already state.
- **Recently shipped features.** The latest `VERIFIED` package, `IP-1063` (inject fire-time
  validation), is not in this scope. Its manual impact is already tracked as `BL-0192`
  (`SCHEDULED` for `08-training-manual-authoring`); not re-filed here.
- **Shared modules for the same control (sampled: `03`, `04`, `11`).** Run #107 brought §10.5/
  §10.6 up to date with the shipped picker. Three shared onboarding modules that walk an operator
  through the same Target field were not updated:
  - `11-vignette-playbooks.md` "How to read a step" says *"Target autocompletes from what your
    cell can see"*. No autocompletion exists: `index.html` has no `<datalist>`, and the control is
    a dropdown plus a free-text `or id` box (**F1**).
  - `03-first-exercise.md` Step 4 item 2 has Red jam `ISR-EO-1`. `04-guided-vignette.md` Blue
    Step 2 and Red Steps 2–5 give a `Target` with no mention of which control to use. At those
    moments the target often is not in the dropdown yet. Live: at the start of `leo-isr-denial`,
    Red's view has `known_tracks: []` and only its own three assets, so the dropdown shows *no
    known targets yet* and `ISR-EO-1` must go in the `or id` box. The empty-state text does say
    "type an id below", so an operator can recover; the walkthrough just does not prepare them
    for it (**F2**).
- **Learning path (FR-11310).** Not in scope; the rung mapping was untouched by both runs.

### 4. Pedagogy

- **Audience fit (MSTR-003/NFR-3600).** The new prose is operator-facing and action-first. Run
  #109's `RED-7` turns a false parity claim into what the Red operator will actually see (`—`,
  an uncoloured dot, no safe-mode events), followed by the conditional rule. That is the
  error-prevention pattern [R606](../research/encyclopedia/R606-minimalist-and-procedural-documentation.md)
  favours: tell the operator what they will see before they go looking for a missing feature.
  The export sections give a worked number ("about 0.36 s for a one-hour span"), verified exact
  above, rather than only the formula.
- **Sentence and module size (NFR-3500).** The run #107/#109 additions use short, single-fact
  sentences. `12-white-cell-manual.md` is now 325 lines, over the ~300-line module guide. This is
  already tracked as `BL-0179` (`DEFERRED`, trigger: the next pass that adds a White-manual
  section). Run #109 added a bullet inside `WCM-6`, not a new section, so the trigger correctly
  did not fire. Not re-filed. `13` (249) and `14` (244) are within the guide.
- **R600 grounding.** R600 is authored 8/8. No sequencing or scaffolding decision in scope
  needed a new citation. The edits are reference and procedure text, not path or rung changes.

## Findings

| Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|
| F1 | `docs/training/11-vignette-playbooks.md` ("How to read a step") | Says *"Target autocompletes from what your cell can see"*. The shipped control is a known-target dropdown plus an `or id` free-text box that takes precedence (§10.5 row 5 / §10.6 row 4). There is no autocompletion (`index.html` has no `<datalist>`). An operator following the playbook will look for a feature that does not exist. Rated Medium, not Critical: the control is mis-described, but every playbook step stays completable, and the dropdown's empty-state text points to the `or id` box. | Medium | `08-training-manual-authoring` |
| F2 | `docs/training/03-first-exercise.md` Step 4 item 2; `docs/training/04-guided-vignette.md` Blue Step 2, Red Steps 2–5 | The guided walkthroughs give `Target = <id>` without saying which control to use. At those steps the target often is not in the known-target dropdown yet (live: Red at the start of `leo-isr-denial` has no tracks and no non-own assets in view), so the id must go in the `or id` box. A one-line orientation (e.g. "pick it from **Target**, or type it in **or id** if it is not listed yet — observing is how it gets listed") would close it. | Low | `08-training-manual-authoring` |

Nothing was fixed in this pass.

## Not findings (checked and confirmed out of scope or already tracked)

- Telemetry export 422 vs. ephemeris 400 on a bad `interval_s`: by design (`BL-0184`, `REJECTED`
  per `VR-1262`). The manual states it accurately.
- `ref-05`/`ref-06` screenshots predate the picker: `BL-0185` (`DEFERRED`); §10.6 carries the
  caveat.
- White manual length: `BL-0179` (`DEFERRED`, trigger not fired).
- `IP-1063`'s inject-builder error text: `BL-0192` (`SCHEDULED`).
