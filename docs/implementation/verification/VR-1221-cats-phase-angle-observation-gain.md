# VR-1221 — Verification Report: CATS Phase-Angle Observation-Gain Refinement for Passive EO Sensors (FR-1670)

> **Document ID:** VR-1221
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1221](../packages/IP-1221-cats-phase-angle-observation-gain.md),
> [FS-122](../../features/FS-122-sensor-modality-models.md) v1.1 (`FR-1670`),
> [IP-1220](../packages/IP-1220-sensor-modality-models.md) (`VERIFIED`, `VR-1220`),
> [IP-1300](../packages/IP-1300-ric-frame-view-and-cats-overlay.md) (`VERIFIED`, `VR-1300`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1221
> **Feature Mapping:** FS-122 v1.1 (`FR-1670`)
> **Related Topics:** [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/sun.py`](../../../spacesim/engine/sun.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1221 — CATS Phase-Angle Observation-Gain Refinement for Passive EO Sensors (`FR-1670`)
- **Version verified:** 1.0
- **Tree state verified:** commit `5dbfd37` (branch `claude/chart-prompt-file-90hm9u`, this session's
  tracking branch `verify-ip1221`). Implementing commit: `d529555` (2026-10-16, pipeline run #125);
  ledger-only follow-up `5dbfd37` (pipeline run #125's own journal/backlog entry) layered on top,
  untouched by this verification.
- **Independence:** first verification pass. Fresh session with no involvement in `d529555` or any
  prior `IP-1221` work (the implementing session's own report; no prior `09-package-verification`
  run exists on this package).

## Result

**VERIFIED, clean — no findings against the package itself.** `FR-1670` is fully and correctly
implemented as designed: a passive-EO (`needs_lighting`) sensor may declare an optional usable
Sun-target-sensor phase-angle range; inside it gain is unchanged, outside it gain falls off
**linearly** from 1 at the declared bound to 0 at 0°/180°, computed from the one shared
`engine/sun.py::cats_phase_angle_deg` at the observation's scheduled instant (`win.start`). Every
sensor that declares no range — every sensor in every shipped vignette — is unaffected, confirmed
both by reading `effective_gain`'s additive signature and by direct numeric comparison. A malformed
range or one on a non-passive-EO sensor is rejected at `Sensor` model validation, i.e. at vignette
load time, not at observation time. `engine/access.py` and `engine/sun.py` are confirmed genuinely
untouched by the implementing commit. `cats_phase_angle_deg` remains the engine's one phase-angle
definition.

The three highest-risk claims — the linear falloff shape, backward compatibility, and the
load-time validator — were independently re-derived from scratch on fresh sample points, fresh
orbit/epoch geometries (different altitude/inclination/RAAN/true-anomaly/epoch than
`test_phase_angle_gain.py`'s own fixtures), and fresh malformed-input cases, at both the pure-helper
level and end-to-end through `OrderSystem`, rather than by re-running the implementer's own tests.
A fourth check — that the refinement cannot leak onto a non-passive-EO sensor even if a range is
forced onto one by bypassing the `Sensor` validator (`model_construct`) — was added as a
defense-in-depth probe beyond what the package's own checklist required, and passed: `orders.py`'s
own `needs_lighting` gate (not only the validator) independently blocks it. Full suite 869 passed,
3 skipped (872 collected); both permanent gates green (14/14) — independently re-run, counts
confirmed by direct dot-stream counting since this pytest build emits no final summary line to a
redirected/background capture (same quirk `VR-1212` noted).

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| A `needs_lighting` sensor with a declared range yields unchanged gain inside the range and strictly lower gain outside it, with the Design Decision 3 (linear) shape, for ground, space-based and hosted sensors. | Independently re-derived: `isr.py::phase_angle_factor` read directly (`lo<=theta<=hi` → 1.0; above `hi` → `(180-theta)/(180-hi)`; below `lo` → `theta/lo`) — this *is* a linear ramp algebraically. Confirmed on 12 fresh sample points spanning both ramps plus both bounds and both domain edges (0°/180°), with three-segment finite-difference slope checks on each side (slopes equal to 1e-9, see Independent reproduction §1). End-to-end: a space-based sensor, a ground-optical sensor, and (via the package's own fixture pattern, cross-checked) a hosted sensor each produce gain == plain-gain inside a declared range and `plain_gain * phase_angle_factor(theta, range)` outside it, on geometries (alt 780 km, i=97.4°, RAAN 201°, epoch offset 5e8 µs) this verification built independently of `test_phase_angle_gain.py` (alt 550 km, i=51.6°, RAAN 33°, epoch 0). | ✅ Pass |
| A sensor without a range behaves exactly as before, and every shipped vignette loads with no sensor declaring a range. | `effective_gain`'s new arguments default to `None` and are applied only when *both* `phase_angle_deg` and `usable_phase_range` are given (`isr.py:152-171`): omitting either reproduces the old call exactly. Independently confirmed with **bit-identical floats** (`==`, not `pytest.approx`) across four look angles (0°/10°/30°/45°) comparing the pre-package call shape against `phase_angle_deg=None`/`usable_phase_range=None` and against a non-`None` phase with `usable_phase_range=None` (short-circuits identically). `test_no_shipped_vignette_sensor_declares_a_range` re-run and independently spot-checked by loading all 19 vignettes and grepping `world.sensors` for a non-`None` `usable_phase_angle_deg` — none found. | ✅ Pass |
| A malformed or misplaced range is rejected at `Sensor` validation. | `entities.py`'s `_check_usable_phase_angle` (`model_validator(mode="after")`) read directly: rejects `lo>hi`, any bound outside `[0,180]`, and a range on a sensor with `needs_lighting=False`. Independently constructed and confirmed rejected at *construction* (not observation) time: `lo>hi` (100,20), negative lo (-10,90), `hi>180` (0,200), a valid-range-but-`needs_lighting=False` sensor, and a non-numeric bound ("abc",90) — all five raise `pydantic.ValidationError` from `Sensor(...)`/`Sensor.model_validate(...)` directly, before any order is ever issued. A valid range on a `needs_lighting=True` sensor is accepted. | ✅ Pass |
| `cats_phase_angle_deg` remains the only phase-angle definition, and `orders.py` uses it. | Independent `grep -rn "def cats_phase_angle_deg" spacesim/engine/` (not reusing the implementer's own `test_cats_angle.py` assertion) returns exactly one hit, `sun.py:81`. `orders.py::_observation_phase_angle_deg` (`:547-571`) read directly: imports and calls `cats_phase_angle_deg` from `engine.sun`, function-local, matching the existing `isr`/`geometry` import pattern. | ✅ Pass |
| No window-acceptance behaviour changed. No file outside `spacesim/engine/` and `spacesim/tests/` changed in code. | `git show d529555 --stat`: code changes confined to `spacesim/engine/entities.py`, `spacesim/engine/isr.py`, `spacesim/engine/orders.py`, `spacesim/tests/test_cats_angle.py`, `spacesim/tests/test_phase_angle_gain.py`; the remaining six changed paths are all documentation/ledger files (`CLAUDE.md`, `ROADMAP.md`, `docs/features/FS-122-...`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, the package's own file, `docs/requirements/03-requirements-traceability-matrix.md`). `access.py` does not appear in the diff at all (confirmed by its absence from `--stat`, not merely by the implementer's claim). The observe branch applies the factor only inside `_exec_payload` (after window selection), never inside `AccessProvider`; the window returned by `osys.issue(...)` is independently confirmed identical (`t_in == t0`, `t_out == t0`) whether or not a range is declared, across every fresh fixture built for this report. | ✅ Pass |
| The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green. | See Test run below. | ✅ Pass |
| The RTM, `CLAUDE.md`, the ledgers and the `FS-122` cross-link are updated, and the manual-impact finding is routed. | RTM `FR-1670` row (`03-requirements-traceability-matrix.md:168`) cites `IP-1221` and both test files/names. `CLAUDE.md`'s `isr.py` and `sun.py` bullets describe the new behavior accurately (matches the shipped code). Master Build Plan, `packages/INDEX.md`, `ROADMAP.md`, the package's own header, and `FS-122`'s `Referenced By` all agreed on `COMPLETE 2026-10-16 … awaiting fresh-session 09-package-verification` prior to this report (independently diffed, see "Audit traceability" below). Manual-impact finding routed as `BL-0211` (`DEFERRED`, trigger = this report reaching `VERIFIED`; fired below). | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `git diff` of the implementing commit touches code only in `entities.py`/`isr.py`/`orders.py`/`spacesim/tests/`; `access.py` and `sun.py` are unchanged. | `git show d529555 --stat` read directly (see table above). `access.py` absent entirely; `sun.py` is **not** in the diff either — the package's own text calls `sun.py` "consumed, unchanged," confirmed literally true: zero lines touched. | ✅ Pass |
| Read `effective_gain`: with the new argument omitted, its arithmetic is identical to the pre-package shape. | Read `isr.py:139-171` directly. The pre-existing computation (`look_rad`/`angle_factor`/`gain = base_gain*bp["gain_factor"]*angle_factor`, then the `band_affinity` term) is untouched above the new two-line addition (`if phase_angle_deg is not None and usable_phase_range is not None: gain *= phase_angle_factor(...)`), which only executes when *both* new arguments are non-`None`. Independently confirmed bit-identical (`==`) across four look angles. | ✅ Pass |
| Read the observe branch: the angle is evaluated at `win.start`, the factor is applied only for `needs_lighting` sensors with a declared range, and every undefined case falls back to 1 without raising. | `orders.py:727-733` read directly: `phase_deg = self._observation_phase_angle_deg(actor_sensor, order.target, win.start)` is called only inside `if usable_range is not None and actor_sensor.needs_lighting:`; `_eg(...)` receives `usable_phase_range=usable_range if phase_deg is not None else None` — so an undefined geometry (target not an `Asset`/no orbit, coincident positions, missing site/orbit) yields `phase_deg is None` and the call degrades to the no-op path, not a raised exception. `_observation_phase_angle_deg` itself (`:547-571`) catches `ValueError` from `cats_phase_angle_deg` and returns `None` on every undefined branch; independently confirmed it never raises by constructing a target with no orbit and a sensor with no location/orbit and calling it directly — both return `None` cleanly. | ✅ Pass |
| Tests 1–8 exist and pass; the Implementation Summary records which were seen failing first. | `test_phase_angle_gain.py` (16 tests, covering Tests 1–7 incl. parametrized cases) and `test_cats_angle.py`'s new `test_fr1670_observe_path_reuses_the_shared_phase_angle_function` (Test 8) both exist and pass (`python3 -m pytest spacesim/tests/test_phase_angle_gain.py spacesim/tests/test_cats_angle.py -v` → 23 passed, 16+7). The implementing commit message records the fail-first claim (ImportError/missing reference); not independently re-run against a pre-package checkout in this pass (not required — see Gotchas: an unmodified pre-existing test suite plus a from-scratch independent reproduction of every behavioral claim is the stronger check here, since the new code is additive and has no pre-package baseline to diff against other than "doesn't exist yet"). | ✅ Pass |
| Independent reproduction on a fixture other than the tests': a backlit and a front-lit observation by the same declared sensor give strictly lower and unchanged gain respectively. | Built fresh (alt 780 km / i 97.4° / RAAN 201° / epoch 5×10⁸ µs, vs. the package's 550 km / 51.6° / RAAN 33° / epoch 0) space-based and ground-optical fixtures from scratch; see §1/§2 below — both reproduce "inside range ⇒ gain unchanged" and "outside range ⇒ strictly lower, matching `plain_gain × phase_angle_factor(theta, range)` exactly." | ✅ Pass |
| Pre-existing tests are unmodified except `test_cats_angle.py`'s single-definition test, if extended in place. | `git show d529555 -- spacesim/tests/test_cats_angle.py` read directly: the diff is a pure *addition* of one new test function after the existing `test_phase_angle_is_defined_only_once_in_engine`; that existing test's own body is untouched (0 lines removed/changed inside it). | ✅ Pass |
| `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass. | See Test run below. | ✅ Pass |
| The RTM `FR-1670` row cites `IP-1221`. | `03-requirements-traceability-matrix.md:168` — confirmed, cites `IP-1221` and the two test files by name. | ✅ Pass |
| The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header agree on status. | All four independently diffed (`git show d529555`) and read post-diff: all read `COMPLETE 2026-10-16 … awaiting 09-package-verification` prior to this report, consistently. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-1670` | `engine/entities.py::Sensor.usable_phase_angle_deg` + `_check_usable_phase_angle`; `engine/isr.py::phase_angle_factor`/`effective_gain`; `engine/orders.py::OrderSystem._observation_phase_angle_deg`, wired into the observe branch (`:727-733`) | `spacesim/tests/test_phase_angle_gain.py` (16 tests) + `spacesim/tests/test_cats_angle.py::test_fr1670_observe_path_reuses_the_shared_phase_angle_function`; independently re-derived at the pure-helper, `effective_gain`-composition, `Sensor`-validator and full-`OrderSystem` levels in this report (§1–§4 below) | `03-requirements-traceability-matrix.md:168` cites `IP-1221` and both test files — accurate, no correction needed | ✅ Pass |

No other requirement is touched (confirmed by the scope audit below); `FR-1220`, `FR-1620`,
`FR-1630`, `FR-1660`, `FR-8220` are consumed unchanged, matching the package's own claim.

## Test run

Exact commands run in this session (tree at `5dbfd37`, worktree `verify-ip1221`):

```
python3 -m pytest -q                                              # full suite
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
python3 -m pytest spacesim/tests/test_phase_angle_gain.py spacesim/tests/test_cats_angle.py -v
```

- **Full suite:** 869 passed, 3 skipped (872 collected). This pytest build emits no final summary
  line to a redirected/background capture (the same quirk `VR-1212` recorded); the count was
  confirmed independently by counting progress-bar dot/`s` characters directly from the captured
  output (891 raw `.` characters include 22 appearing in unrelated warning text after the
  progress bar; isolating only the 13 progress-bar lines gives exactly 869 `.` + 3 `s` = 872),
  matching the implementer's claimed 869/3/872 exactly. Run twice (once piped through `tail`,
  once redirected whole to a file) with the same result both times.
- **Permanent gates, run by name:** `test_determinism.py` + `test_import_guard.py` → **14 passed**
  (6 + 8), matching the claimed 14/14 exactly.
- **This package's own tests, run by name:** `test_phase_angle_gain.py` (16) +
  `test_cats_angle.py` (7, including the one new Test 8) → **23 passed**.

## Scope audit

`git show d529555 --stat` (12 files): `spacesim/engine/entities.py`, `spacesim/engine/isr.py`,
`spacesim/engine/orders.py`, `spacesim/tests/test_cats_angle.py`, `spacesim/tests/test_phase_angle_gain.py`
(new file) — exactly the five code/test files the package's "Files to Create"/"Files to Modify"
sections name. The other seven changed files are documentation/traceability (`CLAUDE.md`,
`ROADMAP.md`, `docs/features/FS-122-sensor-modality-models.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/implementation/packages/IP-1221-cats-phase-angle-observation-gain.md`,
`docs/requirements/03-requirements-traceability-matrix.md`), matching the package's own
"Documentation Updates" section. No excursion.

## Independent reproduction (fresh geometries/scenarios, not the implementer's own fixtures)

### §1 — Linear falloff, fresh sample points (not the package's own test's angles)

Using `phase_angle_factor` directly with a declared range `(20°, 100°)` distinct from every range
`test_phase_angle_gain.py` itself uses:

| θ | factor | note |
|---|---|---|
| 60.0 | 1.000000 | deep inside |
| 20.0 (= lo) | 1.000000 | at bound |
| 100.0 (= hi) | 1.000000 | at bound |
| 120.0 | 0.750000 | 25% of the way from `hi` to 180° |
| 140.0 | 0.500000 | 50% |
| 160.0 | 0.250000 | 75% |
| 180.0 | 0.000000 | domain extreme |
| 15.0 | 0.750000 | 25% of the way from `lo` to 0° |
| 10.0 | 0.500000 | 50% |
| 5.0 | 0.250000 | 75% |
| 0.0 | 0.000000 | domain extreme |

The 25/50/75% ramp points land exactly on 0.75/0.5/0.25 on both sides — a straight line, not a
cosine, quadratic, or any other curve. Finite-difference slopes over three consecutive segments on
each side are equal to 1×10⁻⁹ (above `hi`: −0.0125, −0.0125, −0.0125; below `lo`: 0.0500, 0.0500,
0.0500), confirming constant slope (true linearity), not merely "same value at three points."
Domain-edge cases (`(0°,180°)` → factor 1.0 everywhere; `(0°,90°)`'s upper ramp; `(90°,180°)`'s
lower ramp) all independently reproduced correctly.

### §2 — `effective_gain` backward compatibility, bit-identical

For look angles 0°/10°/30°/45° with `isr_eo` beam params: the pre-package call shape
(`effective_gain(base, look, bp)`), the new signature with both new arguments `None`, and the new
signature with a phase angle given but `usable_phase_range=None`, produced **identical floats**
(`==`, zero ULP difference) in all twelve comparisons — not merely "close." With a declared range
and an inside-range phase angle, the result also equals the plain-gain value exactly; with an
outside-range phase angle it is strictly lower and equals `plain_gain * phase_angle_factor(...)`.

### §3 — Load-time validator, fresh malformed inputs

Five fresh malformed/misplaced declarations — `lo>hi` (100,20), negative lo (−10,90), `hi>180`
(0,200), a syntactically valid range on a `needs_lighting=False` sensor, and a non-numeric bound
("abc", 90) — were each independently constructed via `Sensor(...)`/`Sensor.model_validate(...)`
and each raised `pydantic.ValidationError` **at construction**, before any vignette load, order
issue, or observation. A valid range on a `needs_lighting=True` sensor was accepted.

### §4 — End-to-end through `OrderSystem`, fresh orbit/epoch geometry

Built a fresh fixture (target `OrbitState(alt=780 km, e=0.001, i=97.4°, raan=201°, argp=15°,
epoch=5×10⁸ µs)`; a space-based optical sensor and a ground-optical sensor, both distinct from
`test_phase_angle_gain.py`'s 550 km/51.6°/RAAN 33°/epoch-0 fixtures):

- **Space-based:** plain gain 1.0 at θ≈117.3° (win.start). A declared range covering θ±20° leaves
  the scheduled gain exactly unchanged; a declared range 25° away from θ gives gain 0.7148,
  matching `plain_gain × phase_angle_factor(θ, range)` exactly, strictly lower, with the selected
  window (`win.start`) unchanged in both cases.
- **Ground-optical:** a ground site was found under the fresh target's track with a genuine access
  window; plain gain 1.0 at θ≈89.3°. A range 8° outside θ gives gain 0.9190, again matching the
  formula exactly and leaving the window unchanged.
- **Defense-in-depth probe (beyond the package's own checklist):** a `ground_radar`
  (`needs_lighting=False`) sensor was constructed via `Sensor.model_construct` to **bypass** the
  validator and force a narrow `(0°,10°)` range directly onto a non-passive-EO sensor object — a
  state the validator makes unreachable through normal construction. Observing through
  `OrderSystem` with this forced range produced a gain **bit-identical** to the same sensor with no
  range at all: `orders.py`'s own `actor_sensor.needs_lighting` gate (`:729`) independently blocks
  the refinement even when the validator is circumvented, confirming the gating is enforced twice
  (model validation *and* the observe-branch guard), not once.

### §5 — `cats_phase_angle_deg` single definition and `access.py`/`sun.py` untouched

`grep -rn "def cats_phase_angle_deg" spacesim/engine/` → exactly one hit (`sun.py:81`), run
independently of `test_cats_angle.py`'s own assertion. `git show d529555 --stat` → `access.py`
absent from the diff entirely; `sun.py` likewise absent (not merely "unchanged content," genuinely
not touched by this commit).

## Findings

None against the package. (The manual-impact gap `BL-0211` is a pre-existing, correctly-filed
finding from the implementing session itself, routed per its own stated revisit trigger below —
not a new finding against this package's correctness.)

## Traceability actions taken by this report

- `IP-1221` package header, Master Build Plan row, `packages/INDEX.md` row, `ROADMAP.md` row:
  `COMPLETE → VERIFIED`.
- `FS-122`'s `Referenced By` entry for `IP-1221`: `COMPLETE` → `VERIFIED` tag.
- `docs/requirements/03-requirements-traceability-matrix.md` `FR-1670` row: `IP-1221 (COMPLETE
  2026-10-15, awaiting 09 …)` → `IP-1221 (VERIFIED 2026-10-16, VR-1221)`.
- `BL-0122` (the root backlog item, `IN PIPELINE`): closed `DONE` — `IP-1221` reached `VERIFIED`
  this run, closing the thread from intake through implementation.
- `BL-0211` (manual-impact, `DEFERRED`, trigger = "`IP-1221` reaches `VERIFIED`"): trigger fires.
  Flipped `DEFERRED → SCHEDULED`, routed to `08-training-manual-authoring` per its own stated
  owner/stage.
- `BL-0151`/`BL-0152`/`BL-0208`/`BL-0209`: already `DONE`, left unchanged (no new information from
  this verification bears on them).
- `BL-0187`/`BL-0171`/`BL-0181` (`NEEDS-USER`) and `BL-0184` (`REJECTED`): left exactly as found —
  unrelated to this package, parked for the project owner per their own entries.
