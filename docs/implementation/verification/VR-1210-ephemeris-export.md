# VR-1210 — Verification Report: Ephemeris Export (Truth and Cell-Observed, ECI/RIC, CSV/CCSDS OEM)

> **Document ID:** VR-1210
> **Version:** 2.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1210](../packages/IP-1210-ephemeris-export.md), [FS-121](../../features/FS-121-ephemeris-export.md) (`FR-7410`, `FR-7420`, `FR-7430`), [FS-103](../../features/FS-103-custody-management.md) v1.1, [ADS-1500](../../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1210 (this v2.0 pass)
> **Feature Mapping:** FS-121 / FS-103 v1.1
> **Related Topics:** [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/session/aar.py`](../../../spacesim/session/aar.py),
> [`spacesim/engine/maneuver.py`](../../../spacesim/engine/maneuver.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1210 — Ephemeris Export (Truth and Cell-Observed, ECI/RIC, CSV/CCSDS OEM)
- **Version verified:** 1.0 (remediated)
- **Tree state verified:** commit `d2fc118` (branch `claude/chart-prompt-file-90hm9u`). Remediating
  commit: `6e445c5` (`fix(IP-1210): true RIC-frame velocity, CCSDS-conformant OEM, FR-7430
  companion export (BL-0134/0135/0136)`).
- **Independence:** second verification pass (v2.0), fresh session, no involvement in the
  remediation commit or the v1.0 report. All claims re-derived independently, including an
  from-scratch numeric cross-check of the ω×ρ correction (not merely re-running the package's own
  tests — see Test run).

## Result

**VERIFIED — the v1.0 High finding (ω×ρ rotation term) and both Medium findings (OEM
non-conformance; no RIC representation in OEM) are fixed and independently reconfirmed.** Full
suite green (753 passed, 3 skipped), both permanent gates green. No new findings beyond two
carried-forward Low items already disclosed at v1.0 (unchanged, out of this remediation's scope).

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization for the remediation (MSTR-006 §3). | Package header: "authorized 2026-09-27... fix to true RIC-frame velocity, not rename/document." | ✅ Pass |
| `to_ric()` subtracts the frame's own rotation term (`BL-0134`/H1). | `ephemeris.py:63-86`: computes `omega = |h_ref| / (r_ref·r_ref)`, `omega_cross_ric_r = [-omega*ric_r[1], omega*ric_r[0], 0]`, returns `ric_v_inertial - omega_cross_ric_r`. **Independently re-derived from scratch** (not the package's own closed-form shortcut): computed `omega_vec_eci = h_ref/|r_ref|²` along `h_ref`'s own direction, formed `np.cross(omega_vec_eci, r_target - r_ref)` in ECI, then projected through the same RIC basis — matched `to_ric()`'s output to 1e-6 for an eccentric, inclined, non-degenerate test case the package's own tests don't use. | ✅ Pass |
| The co-orbital-stationary-neighbour case now reports ~0 RIC velocity. | `test_to_ric_velocity_zero_for_co_orbital_ric_stationary_neighbour` (`test_ephemeris.py:83-96`) — green. Independently re-run in isolation: `np.allclose(ric_v, 0, atol=1e-6)` holds. | ✅ Pass |
| Finite-difference cross-check of `ric_r`'s time-derivative matches `to_ric`'s velocity. | `test_to_ric_velocity_matches_finite_difference_of_ric_position` (`:99-124`) — green, `atol=0.5` justified in-test by the (much smaller, separate) J2 nodal-precession residual. | ✅ Pass |
| `write_oem`'s KVN structure is CCSDS-conformant (`BL-0135`/M1). | `ephemeris.py:173-211`: `CREATION_DATE`/`ORIGINATOR` precede a `META_START`/`META_STOP` block that now actually wraps `OBJECT_NAME`/`OBJECT_ID`/`CENTER_NAME`/`REF_FRAME`/`TIME_SYSTEM`/`START_TIME`/`STOP_TIME`; `_ccsds_epoch()` strips the `+00:00` suffix `simtime.to_iso` otherwise appends; `REF_FRAME = TEME` (matches `engine/propagator.py`'s own documented approximation, confirmed by reading that file's comment). `test_write_oem_is_ccsds_conformant` (`:232-251`) asserts every one of these structurally — green, independently re-run. | ✅ Pass |
| `FR-7430`'s companion RIC-specific export exists (`BL-0136`/M2). | `ephemeris.py:214-230::write_ric_csv()` — a plain CSV, RIC-only columns. `server.py:867-870`/`887-888`: a new `format=ric` option on both `/ephemeris/truth` and `/ephemeris/{cell}` routes, alongside existing `csv`/`oem`. `test_write_ric_csv_carries_only_ric_fields` (`:254-264`) and `test_ephemeris_ric_companion_format` (`test_web.py`) both green. | ✅ Pass |
| Full suite green, both permanent gates green. | 753 passed, 3 skipped (up from 700 at implementation time — growth from the other 8 packages in this batch). `test_determinism.py` 6 passed, `test_import_guard.py` 8 passed. | ✅ Pass |
| ECI, RIC position, fog-of-war, range clamp/reject, determinism (v1.0-confirmed, unchanged by this remediation, re-confirmed). | `_clamp_or_reject` unchanged by the diff; `cell_observed_ephemeris`'s fog-scoping (`tr.state_estimate`, never ground truth for a merely-tracked reference) unchanged. Re-run `test_ephemeris.py`'s full file — all 17 tests (up from the v1.0-era count) green. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `test_ephemeris.py` exists and is green, including the four new/strengthened tests. | 17 tests, all green (re-run standalone and full-suite). | ✅ Pass |
| `test_determinism.py` remains green. | 6 passed. `ephemeris.py` is session-layer, reads via `aar.state_at_time` only — no wall-clock/RNG use. | ✅ Pass |
| `test_import_guard.py` remains green. | 8 passed. No `spacesim/engine/` file touched by this remediation (`lvlh_frame` reused unmodified). | ✅ Pass |
| Full suite re-run, zero regressions. | 753 passed, 3 skipped. | ✅ Pass |
| Independently re-derive the ω×ρ correction (not merely re-run the tests). | Done — see the DoD table's first row; an independent from-scratch numeric cross-check, distinct test geometry from the package's own tests. | ✅ Pass |
| Independently confirm OEM structural conformance by parsing the output. | Confirmed by direct read of `write_oem`'s emitted lines against the CCSDS OEM 2.0 KVN grammar (`META_START`/`META_STOP` bracketing, mandatory keywords present, no non-conformant `+00:00` suffix). | ✅ Pass |
| Independently confirm `format=ric` is reachable on both HTTP routes. | Confirmed by direct read of `server.py:855-889` — both `ephemeris_truth` and `ephemeris_cell_observed` branch on `format == "ric"` before falling through to `write_csv`. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-7410 | `ephemeris.py::truth_ephemeris`, `server.py::ephemeris_truth` | `test_ephemeris.py`, `test_web.py` | See RTM correction below | ✅ Pass |
| FR-7420 | `ephemeris.py::cell_observed_ephemeris`, `server.py::ephemeris_cell_observed` | same | See RTM correction below | ✅ Pass |
| FR-7430 *(new, closes `BL-0136`)* | `ephemeris.py::write_ric_csv`, `server.py`'s `format=ric` route option | `test_ephemeris.py::test_write_ric_csv_carries_only_ric_fields`, `test_web.py::test_ephemeris_ric_companion_format` | RTM `:209` already cites `IP-1210` — updated from "implemented... awaiting verification" to `VERIFIED` (this report). | ✅ Pass |

## Test run

Commands run on the `d2fc118` tree:

```
python3 -m pytest -q                                                  # full suite
  → 753 passed, 3 skipped, 1 warning in 168.20s
python3 -m pytest spacesim/tests/test_determinism.py -q               # gate 1 → 6 passed
python3 -m pytest spacesim/tests/test_import_guard.py -q              # gate 2 → 8 passed
python3 -m pytest spacesim/tests/test_ephemeris.py -q                 # package-specific
  → 17 passed
python3 -m pytest spacesim/tests/test_web.py -k ephemeris -q          # web route coverage
  → 5 passed
```

Independent from-scratch numeric cross-check of the ω×ρ fix (eccentric/inclined geometry distinct
from the package's own test cases, not committed):
```
orbit_ref: a=7000km e=0.001 i=51.6 raan=10 argp=5 ta=0
orbit_tgt: a=7000km e=0.001 i=51.6 raan=10 argp=5 ta=45
to_ric() result:        [6.89916513e+00, 6.46891932e-01, -3.78e-14]
independently derived:  [6.89916513e+00, 6.46891932e-01,  6.17e-14]
match to 1e-6: True
```

## Scope audit

`git show --stat 6e445c5` touches: `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/implementation/packages/IP-1210-ephemeris-export.md`,
`docs/pipeline/backlog.md`, `docs/requirements/03-requirements-traceability-matrix.md`,
`spacesim/session/ephemeris.py`, `spacesim/tests/test_ephemeris.py`,
`spacesim/tests/test_web.py`, `spacesim/ui_web/server.py`. All within the package's own declared
surface or its natural test/doc/RTM companions. No `spacesim/engine/` file touched. No unexplained
excursion.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| None (High/Medium) | — | — | — |
| L1 *(carried forward from v1.0, unresolved, out of this remediation's declared scope)* | v1.0's 2 Low findings (see below) were not targeted by this remediation's own stated scope (ω×ρ, OEM conformance, `FR-7430`). Re-checked: neither reappears as a new defect; both remain as originally disclosed. | Low | `07-implementation-planning` |

## RTM correction applied by this report

`docs/requirements/03-requirements-traceability-matrix.md`'s `FR-7430` row (`:209`) updated from
"implemented 2026-09-27/28... awaiting fresh `09-package-verification`" to `VERIFIED` (this
report). `FR-7410`/`FR-7420` rows (if any stale annotation existed) confirmed current.

## Related

[IP-1210](../packages/IP-1210-ephemeris-export.md) · [FS-121](../../features/FS-121-ephemeris-export.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)

## Prior pass (v1.0, superseded)

v1.0 returned this package: High H1 (missing ω×ρ rotation term — a co-orbital stationary
neighbour reported a spurious −13.29 m/s radial velocity), plus 2 Medium (OEM KVN
non-conformance; no RIC representation available in OEM, `BL-0136`) and 2 Low findings. ECI, RIC
position, fog-of-war, range clamp/reject and determinism were already independently confirmed
sound at v1.0. This v2.0 pass confirms all three H/M fixes independently (including a from-scratch
numeric re-derivation of the physics, not merely a test re-run) and closes the package to
`VERIFIED`. **This was the last of the three second-pass remediations in this batch** (alongside
`IP-1174`/`VR-1174` and `IP-1062`/`VR-1062`).
