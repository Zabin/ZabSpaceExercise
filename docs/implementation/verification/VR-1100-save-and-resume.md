[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md) ·
[Verification index](INDEX.md) · [Docs index](../../INDEX.md)

# VR-1100 — Verification Report: Save & Resume

## Package

- **ID:** IP-1100
- **Title:** Save & Resume
- **Version verified:** 1.0
- **Commit hash verified:** `0242efc5ce042d437eee1435118844115860601b`

**Process note:** 10 of 11 as-built packages in the `BL-0004` retro-verification sweep.

## Result

**✅ VERIFIED** (0 hard failures; 1 Medium finding — a factual overclaim in the package's own
Requirements Covered table; 2 Low citation findings)

## Definition of Done audit

| Item | Evidence | Pass/fail |
|---|---|---|
| A session saved at sim time T and immediately resumed is identical to the pre-save state at T | `from_state()` (`manager.py:483-509`) calls `mgr.sim._rebuild(stop_time=state["final_time"])` — replays history to the exact saved sim-time, then restores pending events/orders/SSN requests from the saved dict. `test_save_resume_reproduces_state_and_queue` exercises this directly. | ✅ Pass |
| A save file's content portion loads as a fresh vignette's starting state independent of that save's own event-log history | `from_state()`'s first action is `_load(state["vignette_id"])` (loading fresh vignette content) *before* any event-log/session restoration — confirmed the content and session portions are structurally separable steps, not one monolithic blob. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/fail |
|---|---|---|
| `manager.py:286,430,450` read and confirmed | All three citations drifted by the same uniform +32/+33 this sweep has repeatedly found in `manager.py` (`add_tle` `:286→318`, `save_state` `:430→462`, `from_state` `:450→483`). Content confirmed correct at every new location. | ✅ Pass (Finding 2, citation drift) |
| `spacesim/tests/test_session.py` present and green | **`test_session.py` has zero save/resume-related tests** — grepped for `save_state`/`from_state`, no hits. The actual coverage (`test_save_resume_reproduces_state_and_queue`) lives in `spacesim/tests/test_session_features.py`, a different file than the package cites. Coverage exists and is genuine; the file name is wrong. | ⚠️ Pass on substance, citation wrong (Finding 3) |
| FR-7220's content/session split confirmed structurally present | Confirmed directly (see DoD audit above) — `save_state()`'s dict cleanly separates `vignette_id`/`overrides`/`classification` (content) from `eventlog`/`pending`/`orders`/`ssn_requests` (session), and `from_state()` reloads the content half independently before restoring the session half. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state (before → after) | Pass/fail |
|---|---|---|---|---|
| FR-7210 | `session/manager.py` (`save_state`, `from_state`) | `test_session_features.py::test_save_resume_reproduces_state_and_queue` | Test: `UNASSIGNED` → filled with the *correct* file (the package's own citation was wrong); Impl. Package → `IP-1100` | ✅ Pass |
| FR-7220 | `session/manager.py` (content/session split) | Same test | Impl. Package annotated as independently confirmed this pass | ✅ Pass |
| NFR-1800 | Absence of a crash-recoverable mechanism (inspection) | — | Test: filled with the inspection finding (confirmed: no such mechanism exists in `manager.py`) | ✅ Pass |

**Finding 1 (Medium) — a factual overclaim, not a traceability gap:** this package's own
"Requirements Covered" table states `save_state()`/`from_state()` "persist and reconstruct
`WorldState`/`EventLog`/Snapshots/**Role Assignments**." Direct code read of `save_state()`'s
returned dict (`manager.py:468-480`: `vignette_id`, `overrides`, `classification`, `seed`,
`final_time`, `started`, `eventlog`, `pending`, `orders`, `ssn_requests`) shows **no
`role_assignments` key at all**, and `from_state()` never restores `self.role_assignments`
(`manager.py:46`, populated only by `assign_role()`). This is not a new discovery — `IP-1151`'s own
Rollback Considerations already states explicitly: *"`role_assignments` is in-memory `SessionManager`
state, not persisted to `save_state()`/`from_state()`, so no existing save file encodes it."*
`IP-1100`'s Requirements Covered table simply contradicts a fact its sibling package already
disclosed correctly. No functional defect — nothing relies on Role Assignments surviving a
save/resume cycle — but the claim itself is false as written.

## Test run

```
$ python3 -m pytest
566 passed, 3 skipped, 1 warning in 106.89s

$ python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
14 passed in 1.22s

$ python3 -m pytest spacesim/tests/test_session_features.py -v
3 passed in 1.27s
```

No regression from `VR-1090` (run #27)'s count.

## Scope audit

**Files to Create: none. Files to Modify: none.** The single "Reference file" (`session/manager.py`)
was read for this verification, including the `role_assignments` field this finding traces.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | The package's own Requirements Covered table claims `save_state()`/`from_state()` persist "Role Assignments" — confirmed false by direct code read; `role_assignments` is absent from the saved dict and never restored, exactly as `IP-1151`'s own Rollback Considerations already discloses. | Medium | `07-implementation-planning`, next touch of `IP-1100` — correct the Requirements Covered table to remove the Role Assignments claim |
| 2 | `manager.py`'s three citations (`add_tle`, `save_state`, `from_state`) drifted by the same uniform +32/+33 this sweep has repeatedly found in this file (`BL-0042`, `BL-0044`). Content confirmed correct at every new location. | Low | Fold into `IP-1100`'s next package-maintenance touch; no dedicated run. Same file-wide shift as `BL-0042`/`BL-0044`. |
| 3 | The package's "Tests to Add" section cites `spacesim/tests/test_session.py` as the save-resume round-trip coverage; that file has zero save/resume tests. The actual test (`test_save_resume_reproduces_state_and_queue`) lives in `spacesim/tests/test_session_features.py`. Coverage is genuine, just misattributed to the wrong file — the same class of informational naming imprecision as `BL-0022` (`IP-1120`'s `aar.export_json` citation). | Low | Correct the file citation at `IP-1100`'s next package-maintenance touch; no dedicated run |

## Related

[`IP-1100`](../packages/IP-1100-save-and-resume.md) ·
[`FS-110`](../../features/FS-110-save-and-resume.md) ·
[`00-master-build-plan.md`](../00-master-build-plan.md) ·
[`03-requirements-traceability-matrix.md`](../../requirements/03-requirements-traceability-matrix.md)
