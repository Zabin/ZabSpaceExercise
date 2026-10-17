# VR-1280 — Verification Report: Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint

> **Document ID:** VR-1280
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1280](../packages/IP-1280-variable-speed-aar-replay.md), [FS-128](../../features/FS-128-variable-speed-aar-replay.md) v1.0 (`FR-7330`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1280
> **Feature Mapping:** FS-128 (`FR-7330`)
> **Related Topics:** [`spacesim/session/aar.py`](../../../spacesim/session/aar.py),
> [`spacesim/session/cells.py`](../../../spacesim/session/cells.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1280 — Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint
- **Version verified:** 1.0
- **Tree state verified:** commit `d2fc118` (branch `claude/chart-prompt-file-90hm9u`). Implementing
  commit: `100a924` — the last package in this nine-package batch.
- **Independence:** first verification pass, fresh session with no involvement in the implementing
  commit.

## Result

**VERIFIED, with 1 Low finding (same documentation-hygiene pattern as this batch's other
packages).** `FR-7330` is fully implemented: `PlaybackSession` is a read-only wrapper over the
unmodified `state_at_time()`, genuinely dispatches a cell viewpoint through `CellController.view()`
(no parallel filter), preserves the played-back moment across a viewpoint switch, and rejects a
non-participating cell at construction — before any playback state is created. Full suite green
(753 passed, 3 skipped), both permanent gates green.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Cell-viewpoint playback matches `CellController`'s fog-of-war filter at every sampled moment. | `aar.py::PlaybackSession.state()` (`:190-196`): for a non-`"truth"` viewpoint, calls `CellController.view(world, self.viewpoint, objectives)` directly — the same class/method every live cell-scoped view already uses, not a reimplementation. `test_playback_cell_viewpoint_matches_cell_controller_at_sampled_moments` (`test_aar.py:106-117`) — green. | ✅ Pass |
| Ground-truth playback matches the existing no-cell ground-truth view. | `state()`'s `"truth"` branch returns `world.model_dump()` directly — the same `WorldState` `state_at_time()` reconstructs, with no filtering, matching the existing no-cell ground-truth response shape. `test_playback_truth_viewpoint_matches_ground_truth_reconstruction` (`:119-128`) — green. | ✅ Pass |
| Playback at a non-default speed does not disturb the live session. | `advance()` (`:182-188`) only mutates `self.t` (an attribute of `PlaybackSession` itself) and clamps it into `[ctx.start_epoch, mgr.sim.clock.now]` — it never calls any `mgr.sim`/`mgr.osys` mutating method. `test_playback_at_nondefault_speed_does_not_disturb_live_session` (`:91-104`, `speed=4.0`) asserts the live session's clock/eventlog are unchanged after repeated `advance()` calls — green. | ✅ Pass |
| A mid-playback viewpoint switch continues from the same simulated moment. | `set_viewpoint()` (`:173-177`) calls `_validate_viewpoint()` then reassigns `self.viewpoint` only — `self.t` is untouched, exactly as Design Decision 1 requires (the method's own docstring states this explicitly). `test_playback_viewpoint_switch_continues_from_same_moment` (`:130-140`) — green. | ✅ Pass |
| A non-participating cell viewpoint is rejected at the request boundary. | `_validate_viewpoint()` (`:163-171`) is called from `__init__` itself (`:158`) — a `ValueError` is raised before `self.t`/`self.viewpoint` are ever set, so no `PlaybackSession` object is constructed for an invalid viewpoint. `inprocess.py::playback_start()` (`:929-935`) catches this `ValueError` and returns `Ack(ok=False, reason=str(exc))` rather than letting it propagate as an unhandled 500 — confirmed by direct read, not merely the test's own assertion. `test_playback_rejects_a_nonparticipating_cell_viewpoint` (`:142-148`) and `test_web.py`'s route-level companion — both green. | ✅ Pass |
| Full existing test suite green, zero regressions, both permanent gates green. | 753 passed, 3 skipped. `test_determinism.py` 6 passed, `test_import_guard.py` 8 passed. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Every new test named above exists and is green. | `test_aar.py` (5 new tests, `:91`–`:148`) — 9 tests total in the file, all green standalone. `test_web.py`'s new playback-route tests confirmed present and green in the earlier 40-test full-file background run. | ✅ Pass |
| `test_determinism.py` remains green. | 6 passed. `PlaybackSession` is built entirely on `state_at_time()` (unmodified, already deterministic) and its own pure attribute mutation; no wall-clock/RNG use introduced. | ✅ Pass |
| `test_import_guard.py` remains green. | 8 passed. `session/aar.py`/`inprocess.py`/`ui_web/server.py` are all outside `spacesim/engine/`, the guard's scan scope; no engine file touched. | ✅ Pass |
| Independently confirm the playback controller never bypasses `CellController`'s fog-of-war filter for a cell-viewpoint request, by direct code read. | Confirmed above (DoD row 1) — `state()`'s only non-truth branch is a direct `CellController.view(...)` call; `grep -n "CellController\|fog" spacesim/session/aar.py` shows no second, parallel filtering implementation anywhere in the file. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-7330 | `session/aar.py::PlaybackSession`/`_participant_cells`; `session/inprocess.py`'s five `playback_*` methods; `ui_web/server.py`'s five `aar/playback/*` routes | `test_aar.py` (5 tests), `test_web.py` | `docs/requirements/03-requirements-traceability-matrix.md`'s `FR-7330` row cites `IP-1280` — confirmed current. | ✅ Pass |

## Test run

```
python3 -m pytest -q                                                              # full suite (earlier in this session)
  → 753 passed, 3 skipped, 1 warning in 168.20s
python3 -m pytest spacesim/tests/test_determinism.py -q                           # gate 1 → 6 passed
python3 -m pytest spacesim/tests/test_import_guard.py -q                          # gate 2 → 8 passed
python3 -m pytest spacesim/tests/test_aar.py -q                                   # 9 passed
python3 -m pytest spacesim/tests/test_web.py -q                                   # 40 passed (earlier background run, this pass)
```

## Scope audit

`git show --stat 100a924` touches: `CLAUDE.md`, `docs/design/05-interface-control-document.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/session/aar.py`,
`spacesim/session/inprocess.py`, `spacesim/tests/test_aar.py`, `spacesim/tests/test_web.py`,
`spacesim/ui_web/server.py`. `docs/design/05-interface-control-document.md`'s 4-line change is
exactly the package's own Documentation Updates item (`INT-0014`'s citation-only stretch note per
`BL-0093`) — not an excursion. Otherwise exactly the package's own declared `Files to Modify` plus
`session/inprocess.py`'s expected pass-through wrapper and named test files. **Notably absent, as
with this batch's other packages:** `IP-1280`'s own package document and `FS-128`'s
`Referenced By` metadata (see Findings).

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 | Same pattern as this batch's other five first-pass packages: the package's own document (`IP-1280-variable-speed-aar-replay.md`) was never updated by the implementing commit — Status header still `🟡 READY`, DoD/Verification-Checklist boxes unchecked; `FS-128`'s `Referenced By` metadata also not updated. Functional work complete and correct. **This closes the pattern across all six first-pass packages in this batch** (`IP-1220`, `IP-1240`, `IP-1250`, `IP-1270`, `IP-1290`, `IP-1280`) — see the consolidated recommendation in this run's pipeline-journal entry. | Low | `08-code-implementation` (one batch doc-only follow-up across all six) |

## Related

[IP-1280](../packages/IP-1280-variable-speed-aar-replay.md) · [FS-128](../../features/FS-128-variable-speed-aar-replay.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
