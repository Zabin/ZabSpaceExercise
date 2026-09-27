# VR-1210 — Verification Report: Ephemeris Export (Truth and Cell-Observed, ECI/RIC, CSV/CCSDS OEM)

> **Document ID:** VR-1210
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1210](../packages/IP-1210-ephemeris-export.md), [FS-121](../../features/FS-121-ephemeris-export.md) (`FR-7410`, `FR-7420`), [FS-103](../../features/FS-103-custody-management.md) v1.1, [ADS-1500](../../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` return of IP-1210 (RETURNED)
> **Feature Mapping:** FS-121 / FS-103 v1.1
> **Related Topics:** [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/session/aar.py`](../../../spacesim/session/aar.py),
> [`spacesim/engine/maneuver.py`](../../../spacesim/engine/maneuver.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1210 — Ephemeris Export (Truth and Cell-Observed, ECI/RIC, CSV/CCSDS OEM)
- **Version verified:** 1.0
- **Tree state verified:** code at `d2818ff`. Branch tip `c5be8c0` differs only by docs-only
  verification commits. Implementing commit: `0bc628b`.
- **Independence:** implemented by `08-code-implementation` in a prior context. This verification
  ran in a freshly spawned agent context with no memory of that work. **Disclosure:** the
  implementing commit's `Claude-Session` trailer names the same outer remote session ID this agent
  runs under. Every claim was re-derived from the source, a fresh test run, and an independent
  numeric probe with a hand-reasoned expectation: two satellites on the *same* circular orbit, 0.1°
  apart in true anomaly. The target is stationary in the reference's RIC frame, so its RIC position
  is constant and its RIC velocity is ≈ 0.

## Result

**RETURNED: 1 failed check (High H1), plus 2 Medium and 2 Low findings.** What was confirmed:

- The ECI state vectors and the RIC *position* are correct.
- The truth export is reachable only through a no-cell route.
- The cell-observed export never reads ground truth for a non-owned object.
- The wholly-out-of-range span is rejected and the partially-out-of-range span is clamped.
- Output is deterministic.

The RIC *velocity* columns are wrong. `to_ric()` projects the *inertial* relative velocity onto
the reference's R/I/C axes and omits the frame's rotation (the ω × ρ transport term). The co-orbital
probe shows the error: `ric_r` stays fixed at (−10.5, 12004.6, 0) m across 600 s (finite-difference
rate ≈ 1e-13 m/s), yet `ric_v` reports **−13.287 m/s radial**. That is exactly n·ρ for the 12 km
in-track offset. For the RPO and relative-motion analysis this export exists to support, that is
a materially wrong number, and no test checks `ric_v`.

The CCSDS OEM writer also emits a structurally non-conformant file (M1), and it carries no RIC data
even though the DoD and Acceptance Criterion require it (M2). The full suite is green (707 passed,
3 skipped), and both permanent gates are green.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization (MSTR-006 §3). | Granted 2026-09-27; recorded in the package and in the Master Build Plan. | ✅ Pass |
| Given a span and reference object, the truth export's CSV **and CCSDS OEM** files contain state vectors matching engine truth at each sample, **correctly transformed into RIC**, and are reachable only through a no-cell route. | ECI: `truth_ephemeris` rebuilds `aar.state_at_time(mgr, t)` per sample and propagates with `ModeratePropagator.rv`. It matches truth (`test_truth_ephemeris_eci_and_ric_correctness`). RIC position: `basis @ (r_t − r_r)` is correct and tested. **RIC velocity: incorrect** (H1). `basis @ (v_t − v_r)` has no `− ω × ρ` term, and the test never asserts `ric_v`. **OEM:** `write_oem` writes ECI only and carries no RIC data (M2). Its header is also non-conformant (M1). No-cell route: `GET …/ephemeris/truth` (`server.py:721`) has no `cell` parameter. | ❌ **Fail** (H1; M1/M2) |
| A cell-observed export for cell C and object X returns C's own estimated state only: no ground truth, no other cell's belief. | `ephemeris.py` `cell_observed_ephemeris`: the target comes from `world.track_for(cell, object_id).state_estimate`. The reference uses ground truth only when `ref_asset.owner == cell`, and otherwise C's own track `state_estimate`, with no row if C has none. Reading the code confirmed there is no `world.assets[object_id].orbit` read for the target. The four DoD-named tests pass, including the negative leak test. The same RIC-velocity defect (H1) applies to this variant because it uses the same `to_ric`. | ✅ Pass (fog-of-war), ❌ via H1 (RIC velocity) |
| A wholly-out-of-range span is rejected with a specific error; a partially-out-of-range span is clamped. | `_clamp_or_reject`. Hand-built fixtures against the valid range `[lo, hi]`: `(hi+1, hi+10)` rejected; `(lo−10, lo−1)` rejected; `(lo−100 s, lo+1 µs)` clamped, giving 1 row at `lo`; `(hi−1 µs, hi+100 s)` clamped, giving 1 row at `hi−1 µs`. The route maps the rejection to 400 (`test_ephemeris_truth_route_wholly_out_of_range_is_400`). | ✅ Pass |
| Both exports are byte-identical across repeated calls against the same saved session. | `test_truth_ephemeris_deterministic_across_repeated_calls` passes. `state_at_time` (`aar.py:52-67`) is a pure `replay()` with `up_to_seq` and `final_time` and does not touch the live session. `test_aar.py`'s `state_at` tests still pass. | ✅ Pass |
| Full suite and both gates green. | See Test run. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `test_ephemeris.py` tests exist and pass. | 13 tests, all passing. Also `test_aar.py::test_state_at_time_reconstructs_world_at_arbitrary_time` and 4 in `test_web.py`. | ✅ Pass |
| `test_determinism.py` passes. | 14 passed (with the import guard). | ✅ Pass |
| `test_import_guard.py` passes. | Same run. There is no `engine/` change; `lvlh_frame` is reused unmodified. | ✅ Pass |
| Full suite has zero regressions, especially `test_aar.py`. | 707 passed, 3 skipped. | ✅ Pass |
| Independently confirm the cell-observed export never reads `world.assets[...].orbit` for an object the cell does not own. | Confirmed by reading the code (see the DoD row above). | ✅ Pass |
| Independently round-trip a truth and a cell-observed export through the CSV and OEM writers and confirm the numbers match a hand-computed expectation. | ECI positions and velocities are consistent, and OEM applies the km conversion correctly (6878.126524 km for a 6878 km-radius orbit). **The RIC velocity does not match the hand-reasoned expectation** of ≈ 0 for a co-orbital, co-planar neighbour (H1). | ❌ **Fail** (H1) |
| Independently confirm the wholly-versus-partially-out-of-range distinction with hand-built fixtures. | Done (see the DoD rows above), with four fixtures. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-7410 | `session/ephemeris.py` (`truth_ephemeris`, `to_ric`, `write_csv`, `write_oem`), `session/aar.py::state_at_time`, `ui_web/server.py` `…/ephemeris/truth` | `test_ephemeris.py`, `test_aar.py`, `test_web.py` | Annotated **RETURNED (VR-1210)** this pass. | ❌ Fail (H1, M1, M2) |
| FR-7420 | `session/ephemeris.py::cell_observed_ephemeris`, `ui_web/server.py` `…/ephemeris/{cell}` | `test_ephemeris.py` (4 cell-observed tests), `test_web.py::test_ephemeris_cell_observed_route_fog_of_war_enforced` | Annotated likewise. The fog-of-war half is confirmed; the RIC velocity shares H1. | ❌ Fail (H1) |

## Test run

```
PYTHONPATH=. python3 <scratchpad>/p1210.py      # independent numeric probe (not committed)
  # B and R on the same circular orbit (a=6878137 m, i=51.6°), R 0.1° ahead in true anomaly
  → ric_r(m) [-10.5  12004.6  0]  ric_v(m/s) [-13.287  -0.012  0]   (×3 samples, 300 s apart)
  → finite-difference d(ric_r)/dt ≈ [3e-14, -4e-13, -5e-13] m/s     ← true RIC-frame rate ≈ 0
  → n·ρ = sqrt(μ/a³)·12004.6 m ≈ 13.29 m/s                          ← the missing ω×ρ term, exactly
  → OEM text: CCSDS_OEM_VERS / OBJECT_NAME / OBJECT_ID / CENTER_NAME / REF_FRAME=EME2000 /
    TIME_SYSTEM, then an empty META_START/META_STOP pair, then
    "2030-01-01T00:00:00+00:00 6878.126524 7.456635 9.407932 -0.013287 4.728547 5.965942"
  → range fixtures: two wholly-out rejected; two partial clamped to 1 row each

python3 -m pytest -o addopts="" -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py  → 14 passed
python3 -m pytest -o addopts="" -q            → 707 passed, 3 skipped, 1 warning in 156.06s
```

## Scope audit

`git show --stat 0bc628b` touched:

- **Code:** the new `session/ephemeris.py`, and modified `session/aar.py`, `session/inprocess.py`
  and `ui_web/server.py`. These match the package's declared file set.
- **Tests:** the new `test_ephemeris.py`, plus `test_aar.py` and `test_web.py`.
- **Docs:** `CLAUDE.md`, `ROADMAP.md`, the ICD, `FS-103`, `FS-121`, the RTM, the Master Build Plan,
  `packages/INDEX.md`, `01-technical-work-breakdown.md`, the package, and
  `docs/pipeline/pipeline-journal.md` (the same process note as `VR-1190` L2).

No code change falls outside scope.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| H1 | **The RIC velocity is not the velocity in the RIC frame.** `to_ric()` returns `basis @ (v_target − v_ref)`, which is the inertial relative velocity resolved on R/I/C axes. The RIC frame rotates with the reference orbit, so the relative velocity seen in it is `basis @ (v_t − v_r) − ω × ρ_ric`, where ω is the frame's angular velocity (≈ `h/|r|²` about C for a near-circular reference). The probe shows a co-orbital neighbour whose RIC position is constant reported as moving at −13.29 m/s radially, exactly n·ρ. This affects both `FR-7410` and `FR-7420` CSV output, and the `ric_v` columns are untested. **Fix direction:** subtract `ω × ρ` (with ω from the reference's own `h/|r|²`, or its exact rate for an eccentric reference). Add a test with the co-orbital fixture asserting `ric_v ≈ 0`, plus one against a finite-difference of `ric_r`. If the project deliberately wants "inertial relative velocity in RIC axes", the column must be renamed and documented, and the package or FS changed. Either way that is an owner decision, not something to leave implicit. | **High** | `08-code-implementation` re-run on IP-1210 (or `07`/`06` if the inertial convention is intended) |
| M1 | **The CCSDS OEM output is not a conformant OEM (KVN).** Four problems: (a) the metadata keywords (`OBJECT_NAME`, `OBJECT_ID`, `CENTER_NAME`, `REF_FRAME`, `TIME_SYSTEM`) sit *outside* an empty `META_START`/`META_STOP` pair, when they belong between them; (b) the mandatory header `CREATION_DATE`/`ORIGINATOR` and metadata `START_TIME`/`STOP_TIME` are missing; (c) epochs are written as `2030-01-01T00:00:00+00:00`, which is not the CCSDS ASCII time format; (d) `REF_FRAME = EME2000` misstates the engine's frame, which is GMST-based and pseudo-inertial of date, with sgp4 objects in TEME treated as ECI (`engine/propagator.py:92`). A standard OEM reader would reject or misread the file. `test_write_oem_round_trips_expected_fields` asserts only substring presence. | Medium | `08-code-implementation` (same re-run) |
| M2 | **The OEM export carries no RIC data**, while the DoD, `FS-121` Acceptance Criterion 1 and `FR-7410` all say the CSV **and** OEM files contain RIC-transformed state vectors. `write_oem`'s docstring states that OEM "has no native RIC-relative representation". That is defensible, since CCSDS OEM uses local orbital frames (RTN/RSW) only for covariance, not for ephemeris data lines. But then the requirement is infeasible as written, and the package claimed the item met without saying so. | Medium | `04-requirements-engineering`/`07-implementation-planning` (restate `FR-7410`'s AC: RIC in CSV only, or a companion RIC file), then `08` |
| L1 | `FR-7410`'s Inputs say "one or more asset identifiers", but both export functions and routes take exactly one `object_id`. | Low | `07-implementation-planning` |
| L2 | `FR-7410`'s Postcondition and AC say the truth export is reachable only through "the endpoints `FR-6220` already designates" (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`). The implementation adds a **new** no-cell route, `/ephemeris/truth`, which sits next to the cell-scoped `/ephemeris/{cell}` under the same prefix. Its spirit (no cell binding) is satisfied, but the letter is not. Either `FR-6220`'s list should be amended, or the route moved under `/aar*`. | Low | `04-requirements-engineering` |

## Related

[IP-1210](../packages/IP-1210-ephemeris-export.md) · [FS-121](../../features/FS-121-ephemeris-export.md) ·
[ADS-1500](../../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md) · [VR-1070](VR-1070-after-action-review.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
