# VR-1065 — Verification Report: White Cell Console and Session Small Fixes (FR-4410, FR-3310, FR-5410, FR-5510, FR-5220, NFR-3400)

> **Document ID:** VR-1065
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1065](../packages/IP-1065-console-and-session-small-fixes.md);
> [FS-106](../../features/FS-106-white-cell-dashboard.md), [FS-102](../../features/FS-102-command-scheduling.md) v1.1,
> [FS-118](../../features/FS-118-external-vignette-directories.md) v1.1, [FS-119](../../features/FS-119-bulk-tle-omm-import.md),
> [FS-120](../../features/FS-120-save-as-scenario.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md), [`backlog.md`](../../pipeline/backlog.md)
> `BL-0196`/`BL-0266`/`BL-0267`/`BL-0145`/`BL-0141`/`BL-0185`/`BL-0261`
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1065`
> **Related Topics:** [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js),
> [`spacesim/ui_web/static/index.html`](../../../spacesim/ui_web/static/index.html),
> [`tools/render_manual.py`](../../../tools/render_manual.py), `docs/manual/ref-05-tasking.png`,
> `docs/manual/ref-06-compose.png`

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1065 — White Cell Console and Session Small Fixes (five behaviours plus two
  documentation follow-ups).
- **Version verified:** 1.0
- **Tree state verified:** commit `db5f062` (branch `claude/chart-prompt-file-90hm9u`, local
  tracking branch `verify-batch`; probes were run at `0e4b64c`, and the suite was re-run after
  fast-forwarding to `db5f062`). Implementing commit: `2519c50` (2026-10-17, pipeline run #169).
  Later commits that touch `spacesim/` are `60799fd`/`6c0a4e7` (`IP-1064`/`IP-1131`) and
  `125329a` (`IP-1321`, `engine/orders.py` engage path). None of them touches the hunks this
  package changed.
- **Independence:** first verification pass. Fresh session with no involvement in `2519c50`.

## Result

**VERIFIED, with one Low traceability finding (corrected by this report).** Every one of the five
behaviours was reproduced on fixtures or mechanisms distinct from the implementer's own tests. The
three console behaviours were checked by **running the shipped `app.js` functions** (extracted
verbatim and run under Node 22 with a minimal DOM/`api` mock fed real server responses), not only
by the package's static string assertions. The same harness was run against the pre-fix
`app.js`, and showed the old behaviour.

**Screenshots and Pillow, the flagged scrutiny points:**

- **The regenerated `ref-05`/`ref-06` are correct and reproducible.** Re-rendering both with the
  shipped `tools/render_manual.py` (`s_ref_tasking`/`s_ref_compose`, output redirected to a scratch
  directory) gives images **pixel-identical** to the committed PNGs (`ImageChops.difference(…).getbbox()
  is None`, both 1200×720). Compared visually against the `2519c50^` versions and the shipped
  `index.html`: the Target field is now `[RED-TGT ▾] or id [ ]` in both panels, matching the
  shipped `#task-target` + `#task-target-manual` and `#o-target` + `#o-target-manual` controls; the
  tasking panel's Mode field reads `[auto ▾]` and legend 8 reads "auto + the tasked sensor's own
  modes (radar: fence/dish)", which matches `IP-1223` (landed first, `bba6330`); both legend
  titles now point at `10a-ui-reference-orders.md` §10.5/§10.6 (the `10` → `10a` split) instead of
  the old `10-ui-reference.md` section numbers. Legend items 9–13 overflow the legend box, and
  `ref-06`'s items 12–13 run off the bottom edge. Both images had this before the change (seen
  in the `2519c50^` versions), so this package did not introduce it. Informational only.
- **Pillow is not a new dependency.** `tools/render_manual.py` has imported `PIL` since it was added
  (`3444ad5`, 2026-06-26; `from PIL import …` is unchanged at line 14 of `2519c50^`), and nothing
  under `spacesim/` imports it (`grep -rn "PIL\b" spacesim/` → none), so no runtime path needs it.
  It is already declared in `pyproject.toml` `[project.optional-dependencies] dev`
  (`"pillow>=10.0"`) and in the `run-spacesim` skill's install line. Two small, older doc gaps are
  noted but not caused by this package: the `pyproject.toml` comment says Pillow serves
  `tools/render_screens.py`, a file that no longer exists (it is `render_manual.py`); and
  `CLAUDE.md`'s `pip install …` line has no `pillow` (correct for running and testing, which never
  import it, but not enough to regenerate manual screenshots). Filed as `BL-0277` (Low).

**"5 failed first" re-derived** on a pre-fix scratch tree (a copy of the current tree with exactly
`2519c50`'s hunks to `inprocess.py`, `manager.py`, `app.js` and `index.html` reverse-applied —
confirmed by `grep -c IP-1065` → 0 in each): **5 of 6 fail**. The one that passes is
`test_activity_reports_active_while_the_bar_straddles_now`. It checks the `active` label, which the
package keeps unchanged, so it is meant to pass on both trees.

## Independent reproduction (one probe per Objective row)

| Item | Probe (fixture distinct from the implementer's) | Result |
|---|---|---|
| `BL-0196` Fire reports a rejection | Real server (`create_app(InProcessSession())`): `POST /inject` with an invalid effect → **400** `{"detail":"inject rejected: #0 anomaly: …"}`. That exact response text fed to the shipped `fireInject` under Node via the `api.post` mock (which throws `Error(await r.text())`, as `app.js`'s real `api.post` does). | Post-fix: no throw; `#inject-result` reads `✗ server error: {"detail":"inject rejected: …"}` in `var(--red)`; `refresh()` still runs. A valid inject (`satcom-cyber-link` `patch_modem`, 200) shows `✓ fired patch_modem`. Pre-fix `fireInject`: the error propagates and no result line is written. |
| `BL-0266` timeline shows `executed` | `sda-custody-hunt` seed 777, an **observe** order (`BLUE-RADAR-1` → `RED-OBJ`, `duration_s` 120 — the implementer used a `downlink` on `training-basics`). Clock swept over 11 instants from before the window through `ws+120 s+1 µs` to `we+1 h`, and at each instant `cell_activity`'s bar status was compared with `list_orders()` and with the declared rule. | Bar: `queued` before `ws`; `active` for `ws ≤ now ≤ ws+120 s` (the bar end, clamped to `duration_s`); `executed` from `ws+120 s+1 µs` on. `list_orders`: `executed` for every `now > ws`. **Zero mismatches** against Design Decision 1 ("window start has passed **and** the bar no longer straddles now"): whenever the bar reads `executed`, `list_orders` does too; while the bar straddles now it stays `active`, which the package keeps unchanged. |
| `BL-0267` picker groups by origin | Real `/api/vignettes` with `SPACESIM_CONFIG` naming a scratch external dir `partner-lib` (one copied vignette re-id'd `partner-basics`) → 20 entries, origins `{built-in, partner-lib}`. Fed to the shipped `loadVignettes` under Node. | Post-fix: `<optgroup label="Built-in library">` (19) first, then `<optgroup label="External: partner-lib">` (1); 20 options total = catalog size (nothing dropped). With only built-ins: flat list, no `optgroup` (unchanged look when no external dir). Pre-fix: one flat list of 20, no groups. |
| `BL-0145` save-as-scenario control | `index.html`: `#save-scenario-btn` carries `class="white-only"`; `style.css:13` hides `.white-only` unless `body[data-cell="white"]`, and `app.js` toggles it on seat change. Route driven directly: `POST /save_vignette?cell=white` with `as_scenario: true` on a running `sda-custody-hunt` session; also as `cell=observer`. | White → 200 `{"path": ".../saves/vr1065-scen.yaml"}`; the file loads as a vignette with `start_epoch_utc` = the session's current time and its `initial_tracks` populated (FR-5510). Observer → **403** "the Observer seat is read-only" (Design Decision 4). `saveAsScenario` (read) prompts for id and title, posts `as_scenario: true`, and shows `r.path` or the error. |
| `BL-0141` bulk-import duplicate ids | **CCSDS OMM** format (the implementer used TLE): the two-object `_OMM_TEXT` (SAT-A a=6928 km, i=51.6°; SAT-B a=7000 km, i=98°), both assigned asset id `DUP-OMM`, on `geo-rpo-shadowing` seed 5; repeated through the HTTP route `POST /force/bulk_import`. | Reports `[ok: True, ok: False "duplicate asset id 'DUP-OMM' in this file: already imported from 'SAT-A'"]`; the asset keeps SAT-A's orbit (`a_m` 6 928 000, `i` 51.6), not SAT-B's. HTTP route returns the same per-object reports. |
| `BL-0185` ref-05/06 redrawn | See Result above. | Pixel-identical regeneration; content matches the shipped controls. |
| `BL-0261` `CLAUDE.md` no-cell list | `CLAUDE.md` LAN-trust paragraph compared with `FR-6220` (`01-functional-requirements.md`). | Now names `/assessment`, `/ephemeris/truth`, the Observer view, and the White Cell facilitation/authoring reads, and points to `FR-6220` as the full named set. This covers FR-6220's three clauses. |

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All new tests pass; the session-level ones failed first. | `test_console_small_fixes.py`: 6/6 pass post-fix; on the pre-fix scratch tree 5/6 fail, including both session-level tests (`test_activity_reports_executed_once_the_bar_has_ended`, `test_bulk_import_duplicate_asset_id_in_one_file_keeps_the_first`). | ✅ Pass |
| Full suite and both permanent gates green. | See Test run. | ✅ Pass |
| Screenshots regenerated, or the regeneration recorded as blocked with the reason. | Regenerated; independently reproduced pixel-identical (above). | ✅ Pass |
| `CLAUDE.md`, RTM, MBP/INDEX/ROADMAP updated; manual impact filed. | `CLAUDE.md` ✓ (above). MBP/`packages/INDEX.md`/`ROADMAP.md` read `COMPLETE` ✓. Manual impact filed as `BL-0272` ✓ (covers `10b` §10.15, `10` §10.3 / `WCM-5`, `01` §2.2, `10` §10.1.1 / `WCM-2`, `10a` §10.6 note — every item the package's Documentation Updates lists). RTM: `FR-4410`, `FR-5220`, `FR-5410`, `FR-5510` rows cite `IP-1065` ✓, **but `FR-3310` (`BL-0266`) and `NFR-3400` (`BL-0185`) rows had no `IP-1065` entry** although the package asks for "RTM Test cells for the covered leaves" (Finding 1). The five FS `Referenced By` entries also still read "planned". Both corrected by this report. | ✅ Pass (with Low finding, corrected) |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Each of the five behaviours reproduced independently (a probe per row of the Objective). | Table above: five probes, each on a different vignette, seed, format or order kind from the implementer's tests; the three console items run as code, not only grepped. | ✅ Pass |
| `executed` derivation matches `list_orders` on the same orders. | 11-instant sweep, zero mismatches (above). The rules: `list_orders` says `executed` when `queued and now > window[0]`; `cell_activity` says `active` when `start ≤ now ≤ end`, otherwise `executed` when `queued and earliest_window and now > end`. Because `start = window[0]` and `end ≥ start`, a bar that reads `executed` always agrees with `list_orders`. The two differ only while the bar straddles now, where the package keeps `active` on purpose. | ✅ Pass |
| Full suite and both gates run by name. | See Test run. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-4410` (`BL-0196`) | `app.js` `fireInject` try/catch → `#inject-result`; `index.html` `<pre id="inject-result">` | `test_fire_inject_reports_a_rejection` (static); Node run of the shipped function above | Cites `IP-1065` ✓ → `VERIFIED` | ✅ Pass |
| `FR-3310` (`BL-0266`) | `inprocess.py::cell_activity` `executed` branch | `test_activity_reports_executed_once_the_bar_has_ended`, `…active_while_the_bar_straddles_now`; sweep above | **No `IP-1065` entry before this report** → added (Finding 1) | ✅ Pass |
| `FR-5410` (`BL-0267`) | `app.js` `loadVignettes` optgroups by `origin` | `test_vignette_picker_groups_by_origin` (static); Node run with a real external dir above | Cites `IP-1065` ✓ → `VERIFIED` | ✅ Pass |
| `FR-5510` (`BL-0145`) | `index.html` `#save-scenario-btn.white-only`; `app.js` `saveAsScenario` | `test_save_as_scenario_console_control_is_white_only` (static); route probe above (white 200, observer 403) | Cites `IP-1065` ✓ → `VERIFIED` | ✅ Pass |
| `FR-5220` (`BL-0141`) | `manager.py::bulk_import` `imported_as` per-file map | `test_bulk_import_duplicate_asset_id_in_one_file_keeps_the_first` (TLE); OMM + HTTP probe above | Cites `IP-1065` ✓ → `VERIFIED` | ✅ Pass |
| `NFR-3400` (`BL-0185`) | `tools/render_manual.py` `s_ref_tasking`/`s_ref_compose`; the two PNGs | Inspection plus pixel-identical regeneration (no automated test; matches `NFR-3400`'s inspection-type verification) | **No `IP-1065` entry before this report** → added (Finding 1) | ✅ Pass |

## Test run

Exact commands run in this session:

```
python3 -m pytest -p no:warnings -p no:cacheprovider               # full suite (tree db5f062)
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
# pre-fix scratch tree (2519c50's four code hunks reverse-applied), cwd = scratch copy:
python3 -m pytest -p no:warnings -p no:cacheprovider -q spacesim/tests/test_console_small_fixes.py
node harness (shipped + pre-fix app.js) ; python probe (SPACESIM_CONFIG -> scratch external dir)
python regen script (render_manual.s_ref_tasking/s_ref_compose -> scratch dir, PIL pixel diff)
```

- **Full suite:** **1022 passed, 3 skipped** (1025 collected). The +6 since `VR-1223`'s 1016 are
  `IP-1321`'s new tests, which landed on the branch while this verification was running.
- **Permanent gates, run by name:** **14 passed**.
- **This package's tests:** 6/6 pass; 5/6 fail on the pre-fix scratch tree.

## Scope audit

`git show 2519c50 --stat` (13 files): every Files-to-Modify entry (`app.js`, `index.html`,
`inprocess.py`, `manager.py`, `tools/render_manual.py`, both PNGs, `CLAUDE.md`) plus the ledgers
(`ROADMAP.md`, MBP, `packages/INDEX.md`, RTM) and one new test module. **Informational:** the package
proposed three test locations (`test_cell_activity.py`, `test_bulk_import_session.py`,
`test_web.py` "or the nearest console-asset test"). The implementer put all six tests in one new
module, `test_console_small_fixes.py`. They cover the same cases. "Files to Create: none beyond tests"
allows this, so it is not an excursion. No engine file touched ("Engine untouched" ✓).

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | RTM `FR-3310` and `NFR-3400` rows carried no `IP-1065` entry, although the package asks for "RTM Test cells for the covered leaves". The five FS `Referenced By` entries (FS-102/106/118/119/120) were also still "planned". | Low | Corrected by this report. These are traceability cells only, and the code does close both leaves (see Requirements audit) |
| 2 | Older doc gap, not caused by this package: the `pyproject.toml` `dev` extra's comment names a nonexistent `tools/render_screens.py`, and `CLAUDE.md`'s install line does not mention that regenerating manual screenshots needs `pillow`. | Low | `BL-0277` → `08-code-implementation` (one-line comment fix; `CLAUDE.md` note) |

## Traceability actions taken by this report

- MBP row, `packages/INDEX.md` row, `ROADMAP.md` row: `COMPLETE → VERIFIED`; MBP Package Status line.
- RTM: `FR-4410`, `FR-5220`, `FR-5410`, `FR-5510` cells moved to `VERIFIED … VR-1065`. `IP-1065` and
  its test or inspection evidence added to the `FR-3310` and `NFR-3400` rows (Finding 1).
- FS-102/FS-106/FS-118/FS-119/FS-120 `Referenced By` entries for `IP-1065`: "planned" → `VERIFIED` (`VR-1065`).
- Backlog: `BL-0196`, `BL-0266`, `BL-0267`, `BL-0145`, `BL-0141`, `BL-0185` and `BL-0261` → `DONE`.
  `BL-0270` updated. `BL-0272` (manual impact) left `SCHEDULED`; this report confirms the as-built
  behaviour it describes. New: `BL-0277` (Finding 2).
