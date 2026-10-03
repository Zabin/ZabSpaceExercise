# VR-1200 — Verification Report: Save-as-Scenario

> **Document ID:** VR-1200
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1200](../packages/IP-1200-save-as-scenario.md), [FS-120](../../features/FS-120-save-as-scenario.md) (`FR-5510`), [VR-1180](VR-1180-external-vignette-directories.md) (the save-target work this package was built on)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition for IP-1200
> **Feature Mapping:** FS-120 (`FR-5510`)
> **Related Topics:** [`spacesim/content/vignette_export.py`](../../../spacesim/content/vignette_export.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/version.py`](../../../spacesim/version.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1200 — Save-as-Scenario (Mid-Exercise State → New Starting Vignette)
- **Version verified:** 1.0
- **Tree state verified:** code at `d2818ff`. Branch tip `1f28a05` differs only by docs-only
  verification commits. Implementing commit: `e23e8d3`.
- **Ordering:** verified after `IP-1180`
  ([`VR-1180`](VR-1180-external-vignette-directories.md), `VERIFIED`), as the coordination note in
  both packages requires. IP-1200 was built on IP-1180's `save_vignette()` retarget, and that
  retarget is now independently confirmed.
- **Independence:** implemented by `08-code-implementation` in a prior context. This verification
  ran in a freshly spawned agent context with no memory of that work. **Disclosure:** the
  implementing commit's `Claude-Session` trailer names the same outer remote session ID this agent
  runs under. Every claim was re-derived from the source, a fresh test run, and an independent
  end-to-end round trip. The round trip started a real library vignette, created mid-exercise
  tracks, bus, resource and space-weather state, saved it as a scenario, reloaded the file, and
  compared field by field.

## Result

**VERIFIED, with 2 Low findings.** Every Definition of Done item and `FR-5510`'s Postcondition
were confirmed. After the round trip, all six assets, including their orbits, `bus_state` and
resources, were `model_dump()`-identical to the source session. The full suite is green (707
passed, 3 skipped), and both permanent gates are green.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization (MSTR-006 §3). | Granted 2026-09-27; recorded in the package and in the Master Build Plan. | ✅ Pass |
| With no `start_epoch` argument, `export_vignette()`/`save_vignette()` reproduce the prior output: `IP-1173`'s draft save is unchanged. | `vignette_export.py:24-58`: `start_epoch_utc = to_iso(start_epoch if start_epoch is not None else ctx.start_epoch)`, which is `ctx.start_epoch` when the argument is omitted. `test_export_vignette_omitted_start_epoch_reproduces_prior_behavior` passes. **Qualification:** the *start-epoch* semantics are unchanged, but the default path's output is no longer byte-identical to before IP-1200. The package's own Files to Modify says `simulator_version` is stamped unconditionally, and `initial_tracks`/`initial_space_weather` are populated whenever the draft world has them. The Checklist's "byte-identical" wording contradicts the package's own design (Finding L1). | ✅ Pass (with note) |
| A session at sim time T, saved as a scenario and reloaded, starts at T with the same tracks, resources, health and space weather. | Independent probe on `leo-isr-denial` (seed 1). I fired `space_weather: severe`, `reveal_asset` (which creates a Blue track) and an `anomaly` (which mutates bus state), stepped 1800 s, and set `ISR-EO-1` `delta_v_ms` to 12.5. After `save_vignette(..., as_scenario=True)`, `load_vignette` and `build_world`: start epoch equal to T was `True`; `world.now` equal to T was `True`; the tracks list was `model_dump()`-equal (1 track); space weather was `{'severity': 'severe'}` on both sides; and **no per-asset `model_dump()` difference across all 6 assets**. Orbits keep their own `epoch`, and `build_world` only defaults an absent one (`vignette.py:283-284`), so positions are preserved. The three DoD-named tests pass. | ✅ Pass |
| The resulting file records a non-empty `simulator_version`. | `version.py`: `git rev-parse --short HEAD`, falling back to `spacesim.__version__` (`"0.1.0"`) and never raising. The probe file recorded `d2818ff`. `test_version.py:7` passes. | ✅ Pass |
| Save-as-scenario against an unstarted session is rejected with a specific error. | `manager.py:443-455`: `if not self.started: raise ValueError("cannot save-as-scenario: session has not been started")`. The route maps this to 400. The probe hit that exact message. `test_save_as_scenario_rejected_against_unstarted_session` passes. | ✅ Pass |
| All 19 library vignettes still load unchanged (schema additivity). | `vignette.py:133-135` adds three fields that default to empty/None. `build_world` consumes them only when truthy (`:338-342`). `test_all_library_vignettes_have_no_save_as_scenario_fields` (`test_content.py:212`) passes. | ✅ Pass |
| Full suite and both gates green. | See Test run. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| New tests exist and pass. | `test_vignette_export.py:82`, `test_content.py:212/221/236`, `test_vignette_creator_session.py:102/109`, `test_version.py:7` and `test_web.py:452` all pass. | ✅ Pass |
| `test_determinism.py` passes. | 14 passed (with the import guard). | ✅ Pass |
| `test_import_guard.py` passes. | Same run. There is no `spacesim/engine/` change. `version.py`'s `subprocess` call is outside `engine/`. | ✅ Pass |
| Full suite has zero regressions, especially IP-1173's draft-save tests. | 707 passed, 3 skipped. | ✅ Pass |
| Independently confirm the `start_epoch=None` path is byte-identical to pre-IP-1200 behaviour. | By code reading, the start-epoch value is identical. The *file* is not byte-identical (see L1), and the package's own design mandates that. | ✅ Pass (with note, L1) |
| Independently round-trip a save-as-scenario file and confirm tracks, health, resources and space weather. | Done (see the DoD rows above), on a real library vignette rather than the package's fixtures. | ✅ Pass |
| Independently confirm `save_as_scenario()` is unreachable for a draft session and that the draft-save path is untouched. | A draft session is never `start()`-ed (IP-1173, `VR-1173`), so `save_as_scenario` raises for it by construction. `inprocess.py:120-140` routes to `save_as_scenario` only when `as_scenario=True`. Otherwise it calls the same `vignette_export.save_vignette(...)` as before, with no `start_epoch`. `SaveVignetteRequest.as_scenario` defaults to `False` (`server.py:59`). | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-5510 | `content/vignette.py` (3 fields and `build_world` consumption), `content/vignette_export.py` (`start_epoch`, carry-forward), `version.py`, `__init__.py` (`__version__`), `session/manager.py::save_as_scenario`, `session/inprocess.py`, `ui_web/server.py` | `test_vignette_export.py`, `test_vignette_creator_session.py`, `test_content.py`, `test_version.py`, `test_web.py::test_save_as_scenario_route_end_to_end` | `:192` is accurate. Updated to `VERIFIED (VR-1200)`. | ✅ Pass |

## Test run

```
PYTHONPATH=. python3 <scratchpad>/p1200.py      # independent end-to-end round trip (not committed)
  → unstarted rejected: cannot save-as-scenario: session has not been started
  → saved <tmp>/s/x-scn.yaml
  → start epoch == T True True; tracks equal True 1; space weather severe == severe
  → (no ASSET DIFF lines across 6 assets); version d2818ff

python3 -m pytest -o addopts="" -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py  → 14 passed
python3 -m pytest -o addopts="" -q            → 707 passed, 3 skipped, 1 warning in 156.06s
```

## Scope audit

`git show --stat e23e8d3` touched:

- **Code:** `spacesim/__init__.py`, `content/vignette.py`, `content/vignette_export.py`,
  `session/inprocess.py`, `session/manager.py`, `ui_web/server.py`, and the new `version.py`.
  These match Files to Modify/Create exactly.
- **Tests:** `test_content.py`, `test_vignette_creator_session.py`, `test_vignette_export.py`,
  `test_web.py`, and the new `test_version.py`.
- **Docs:** `CLAUDE.md`, `ROADMAP.md`, `FS-120`, the RTM, the Master Build Plan,
  `packages/INDEX.md`, `01-technical-work-breakdown.md`, the package, and
  `docs/pipeline/pipeline-journal.md` (the same process note as `VR-1190` L2).

No code change falls outside the declared set.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 | The package contradicts itself. Its DoD and Verification Checklist say the `start_epoch=None` path is "byte-identical"/"exact prior output", but its own Files to Modify requires `simulator_version` to be stamped unconditionally, and tracks/space weather to be carried whenever present. The shipped code follows the design, and the default path's start-epoch semantics are unchanged. The checklist wording is the defect. | Low | `07-implementation-planning` (package text) |
| L2 | Save-as-scenario is reachable only through the API (`POST …/save_vignette` with `as_scenario: true`). No `ui_web/static/` control exists (grep for `as_scenario`: server only), so a White Cell facilitator using the browser GUI cannot invoke it. The package's Files to Modify never scoped a UI control, so this is not a package failure. Also note that `FR-5510` says White Cell "shall be able to" save. | Low | `07-implementation-planning` (a small UI follow-on) / `08-training-manual-authoring` once it exists |

## Related

[IP-1200](../packages/IP-1200-save-as-scenario.md) · [FS-120](../../features/FS-120-save-as-scenario.md) ·
[VR-1180](VR-1180-external-vignette-directories.md) · [VR-1173](VR-1173-vignette-creator-draft-session.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
