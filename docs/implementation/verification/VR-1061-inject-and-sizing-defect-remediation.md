# VR-1061 — Verification Report: Inject Scheduling & Sizing-Cap Defect Remediation

> **Document ID:** VR-1061
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1061](../packages/IP-1061-inject-and-sizing-defect-remediation.md), [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.0 (`FR-4410`), [ADR-0019](../../architecture/adr/ADR-0019-sizing-guideline-not-engine-cap.md) (`NFR-1300`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition for IP-1061
> **Feature Mapping:** FS-106 (`FR-4410` slice) + `NFR-1300`
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/content/inject_library.yaml`](../../../spacesim/content/inject_library.yaml),
> [`spacesim/tests/test_inject_library.py`](../../../spacesim/tests/test_inject_library.py),
> [`spacesim/tests/test_content.py`](../../../spacesim/tests/test_content.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1061 — Inject Scheduling & Sizing-Cap Defect Remediation
- **Version verified:** 1.0
- **Tree state verified:** commit `d2818ff` (branch `claude/chart-prompt-file-90hm9u`). Implementing
  commit: `1475951`. The tree has since gained `IP-1062`'s refactor of the same `_h_inject` body into
  `_apply_inject_effects()`; this report verifies IP-1061's claims against the *current* tree, so it
  also confirms that later refactor did not undo them.
- **Independence:** implemented by `08-code-implementation` in a prior context (commit `1475951`).
  This verification ran in a freshly spawned agent context with no memory of that implementation
  and no part of this conversation touching it. **Disclosure:** the implementing commit's
  `Claude-Session` trailer names the same outer remote session ID this verification agent runs
  under. The agent context is new, but the orchestrating session is shared. Every claim below was
  re-derived from the live source, a fresh test run and independent probe scripts. Nothing was
  taken on the package's word.

## Result

**VERIFIED, with 3 Low findings.** Every Definition of Done item is confirmed against the current
tree. The full suite is green (707 passed, 3 skipped), and both permanent gates are green. None of
the findings is a functional gap.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| A vignette time inject at `at_sim_s: 0` fires exactly once at session start. | `session/manager.py:140-142`: `start()` calls `_arm_schedule(..., initial=True)`. `:176-182`: the initial arm schedules when `at >= from_t`, and the payload carries `inject_id`. `test_time_inject_at_zero_fires_at_start` (`test_inject_library.py:189`) passes and asserts the message is stamped at `start_epoch`. An independent probe with two injects at 0 s and one at 7 s gave 1/1/1 firings. | ✅ Pass |
| No scripted time inject fires twice across any rewind. A rewind to `start_epoch` before the first advance does not lose a 0 s inject. | `manager.py:168-181`: on re-arm, schedule if `at > from_t`, or if `at == from_t` and the inject id is absent from the retained log entries at exactly `from_t`. `engine/simulation.py:82-94` keeps entries with `sim_time <= t`, which this relies on; the engine is read, not modified. `test_rewind_does_not_refire_fired_inject` and `test_rewind_to_start_before_first_advance_keeps_zero_inject` pass. Independent probe: rewinds to 0 s, 3 s and 7 s (the exact firing time of the 7 s inject), each followed by a re-advance, all left every inject at exactly one firing. Two identical rewind scenarios produced byte-identical `WorldState` JSON. | ✅ Pass |
| `_h_inject()` contains one `space_weather` branch. It validates severity (invalid → `minor`), accepts `clear`, and posts a message. | The branch now lives in `_apply_inject_effects()` after IP-1062's extraction; it is still the only one. `grep -c 'kind == "space_weather"' manager.py` returns `1`. `manager.py:845-859`: defaults to `minor`, maps `clear` → `none`, coerces values outside {none, minor, severe} to `minor`, and messages all three cells. Probe: `bogus` → `minor`, missing → `minor`, `severe` → `severe`. | ✅ Pass |
| `inject_library.yaml` names `POST …/inject` + `at_sim_t` and never names `inject_schedule`. | `inject_library.yaml:18-22` names `POST /api/sessions/{sid}/inject` with an `at_sim_t` field. No `inject_schedule` route string appears anywhere in `spacesim/` (see Finding L1 on the checklist's literal grep). | ✅ Pass |
| `build_world()` raises no satellite-count or constellation-size error. The old cap tests are replaced by the "loads" tests. | `content/vignette.py:293-296`: only an ADR-0019/NFR-1300 comment remains, with no raise and no `Counter`. `test_vignette_above_24_satellites_loads` and `test_constellation_above_3_loads` (`test_content.py:178`/`:190`) pass. Probe: `training-basics` plus 30 extra satellites in one group built 36 assets without error. The DoD's "four old cap tests" wording is imprecise (Finding L2). | ✅ Pass |
| FUTURE-WORK §6, `00-LIBRARY-ARCHITECTURE.md:180` and the RTM cells are updated. | `docs/FUTURE-WORK.md:134-141` is rewritten as a soft guideline citing IP-1061. `docs/vignettes/00-LIBRARY-ARCHITECTURE.md:183` is restated per ADR-0019. RTM `FR-4410` (`:171`) and `NFR-1300` (`:303`) cite IP-1061 and name the new tests. | ✅ Pass |
| Full suite green; both permanent gates green. | See Test run. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `grep -c 'kind == "space_weather"'` → `1` | Re-run: `1`. | ✅ Pass |
| `grep -n inject_schedule -r spacesim/` → no hits | **The literal command does hit:** `spacesim/tests/test_inject_library.py:111` (`test_fire_inject_scheduled_does_not_apply_until_advance`). `inject_scheduled` contains the substring `inject_schedule`, so the checklist's own claim that the name "does not match" is wrong. Its intent holds: no route or comment names a nonexistent `inject_schedule` endpoint. Finding L1. | ✅ Pass (with note) |
| `grep -n "satellite cap\|constellation(s) exceed" vignette.py` → no hits | Re-run: no hits. | ✅ Pass |
| Each new test exists and passes | 5 in `test_inject_library.py` (`:189`, `:200`, `:227`, `:238`, `:247`), plus the 2 inverted tests in `test_content.py`. All pass in the full run. | ✅ Pass |
| Intake reproduction re-run (`at_sim_s: 0` → 1 message; `bogus` → `minor`) | Reproduced independently with a scratch script, not the package's own tests. | ✅ Pass |
| Full suite + both gates pass | 707 passed, 3 skipped; gates 14 passed. | ✅ Pass |
| No file under `spacesim/engine/` modified | `git show --stat 1475951` touches no `spacesim/engine/` path. | ✅ Pass |
| RTM `FR-4410`/`NFR-1300` cite IP-1061 | Confirmed; updated this pass to `VERIFIED`. The `NFR-1300` row carries a 9th (Impl. Package) cell that the NFR table header lacks. This is the pre-existing, already-tracked `BL-0009`/`BL-0034` defect class; five other NFR rows share it. Finding L3. | ✅ Pass (with note) |
| Ledger/header status agreement (`COMPLETE`) | Agreed before this pass; now flipped to `VERIFIED` on both ledgers. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-4410 | `session/manager.py` (`start`, `_arm_schedule`, `rewind_to`, `_apply_inject_effects` space-weather branch); `content/inject_library.yaml` comment | `test_inject_library.py` (5 IP-1061 tests + existing suite) | `:171`: correct. Impl. Package updated to `VERIFIED (VR-1061)` this pass. | ✅ Pass |
| NFR-1300 | `content/vignette.py` `build_world()` (caps removed; watchdog `SessionManager._record_catch_up_lag` unchanged) | `test_content.py::test_vignette_above_24_satellites_loads`, `::test_constellation_above_3_loads` | `:303`: correct content. Updated to `VERIFIED (VR-1061)`. Malformed column count noted (L3). | ✅ Pass |

## Test run

Commands run on commit `d2818ff`:

```
PYTHONPATH=. python3 <scratchpad>/p1061.py      # independent A1/A3/A4 probe (not committed)
  → fired 1 1 1 / after rewind0 1 1 1 / after rewind3 1 1 1 / after rewind7 1 1 1
  → deterministic True / uncapped assets 36 / {'severity':'minor'} x2, {'severity':'severe'}

python3 -m pytest -o addopts="" -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
  → 14 passed

python3 -m pytest -o addopts="" -q            (full suite)
  → 707 passed, 3 skipped, 1 warning in 156.06s
    (the warning is the pre-existing StarletteDeprecationWarning about httpx/testclient)
```

The count is above IP-1061's own recorded 603/3. The difference is tests from the six packages
implemented after it (`IP-1174` through `IP-1210`), not a regression.

## Scope audit

`git show --stat 1475951` touches:

- **Production code and content:** `session/manager.py`, `content/vignette.py`,
  `content/inject_library.yaml`.
- **Tests:** `test_inject_library.py`, `test_content.py`.
- **Docs:** `docs/FUTURE-WORK.md`, `docs/vignettes/00-LIBRARY-ARCHITECTURE.md`, the RTM, the
  Master Build Plan, `packages/INDEX.md`, the package document itself, `ROADMAP.md` and
  `01-technical-work-breakdown.md`.

This matches Files to Modify plus the implied ledger/doc updates. No file is outside scope.
The package's Hidden-cap-dependants risk was re-checked: no remaining test asserts the cap. The
only residue is `test_vignette_library.py:4`'s docstring phrase "respects the satellite caps",
which is cosmetic and asserts nothing.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 | Verification Checklist item 2's literal command (`grep -n inject_schedule -r spacesim/`) returns one hit: the test name `test_fire_inject_scheduled_…`. The checklist asserts that name "does not match", but it does, because `inject_schedule` is a substring of it. The intent (no nonexistent route is named) is satisfied. | Low | `07-implementation-planning` (package text) |
| L2 | The DoD says "the four old cap tests are replaced by the two 'loads' tests". As built, 2 enforcement tests were inverted and 2 at-limit tests were kept unchanged. That is a sensible choice and is disclosed in the Status header, but the DoD sentence no longer describes it. | Low | `07-implementation-planning` (package text) |
| L3 | The RTM `NFR-1300` row has 9 cells against the NFR table's 8-column header. This is the same defect class already tracked as `BL-0009`/`BL-0034`, and `NFR-1400`/`1500`/`1600`/`1800`/`2500`/`3100` share it. The shape was not re-flowed here. | Low | `04-requirements-engineering` (existing `BL-0009`/`BL-0034`) |

Observation, not a finding: `SessionManager.undo_last()` does not re-arm scripted injects, unlike
`rewind_to()`. This predates IP-1061 and is outside its scope.

## Related

[IP-1061](../packages/IP-1061-inject-and-sizing-defect-remediation.md) · [FS-106](../../features/FS-106-white-cell-dashboard.md) ·
[ADR-0019](../../architecture/adr/ADR-0019-sizing-guideline-not-engine-cap.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
