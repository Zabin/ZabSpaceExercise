# VR-1230 — Space-Weather-Index Coupling: Index-Driven LEO Drag and Environmental-Anomaly Rate

[↑ Verification index](INDEX.md) · [Packages index](../packages/INDEX.md) ·
[Master Build Plan](../00-master-build-plan.md)

## Package

- **Package:** [IP-1230](../packages/IP-1230-space-weather-index-coupling.md) — FS-123 v1.1
  `FR-1230`/`FR-4440` Space-Weather-Index Coupling (`BL-0074` item B8).
- **Verified against:** tree at `e59ffb8` (branch `claude/chart-prompt-file-90hm9u`), implementing
  commit `3df5f2d`.
- **Feature Specification:** [FS-123](../../features/FS-123-space-weather-index-coupling.md) v1.1.
- **Design basis:** [ADR-0039](../../architecture/adr/ADR-0039-space-weather-index-to-multiplier-mapping.md)
  (Accepted), grounded in [R131](../../research/encyclopedia/R131-space-environment-and-space-weather-operations.md)
  v1.2 §3/§5.

## Result

**✅ VERIFIED — first pass, clean. No findings against the package.**

This package touches orbital-perturbation physics and the determinism invariant, so it received
the extra scrutiny the task required: the coupling math was independently re-derived from
ADR-0039's formula on fresh inputs (not copied from the package's own test cases), the drag-impulse
conversion was independently checked against the standard vis-viva energy relation, and the "42
failed first" claim was independently reproduced on an isolated worktree of the pre-implementing
commit rather than taken on faith.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All Design Decisions 1–10 implemented | Read against the tree: Decision 1 (stored form) — `vignette.py` `build_world` merges `index_series` into `world.space_weather` without replacing it (lines ~565–575); Decision 2/3 (authoring forms, severity handling) — `manager.py` `space_weather` inject branch (lines 1261–1295) updates keys, drops stored entries with `t ≥` the earliest new entry, keeps severity on a series-only inject and vice versa; Decision 4 (pure functions) — `perturbations.py` lines 186–268 (`f_solar`, `f_geo`, `index_in_effect`, `drag_multiplier`, `anomaly_rate_multiplier`, `index_series_problems`), no clock/RNG reads; Decision 5 (drag step) — `busmodel.py::_apply_index_drag` (lines 72–97), early return with no series, `apply_impulse` re-epoch, `tick_period_s` ctor arg (line 29) defaulted and passed from `manager.py` as `BUS_TICK_PERIOD_S` (line 161); Decision 6 (anomalies) — `manager.py::_h_env_anomaly_check` (lines 1390–1418), one draw per listed asset per tick unconditionally, gated scheduling in `_arm_schedule` (lines 276–283); Decision 7 (vignette block) — `_environmental_anomaly_problems` (`vignette.py` lines 357–385); Decision 8 (asset field) — `entities.py` line 48 + `field_validator` (lines 54–61, disclosed deviation from "`model_validator`" — accepted, see Findings); Decision 9 (boundary validation) — `manager.py::_inject_effect_problem` lines 65–70, `validate_vignette` lines 479–487; Decision 10 (determinism) — confirmed below. | Pass |
| Every test added; behaviour tests seen failing first | `spacesim/tests/test_space_weather_index.py` exists, 296 lines, 21 test functions (46 parametrized cases). Independently re-derived the "42 failed first / 4 passed on arrival" claim: built a disposable `git worktree` at the pre-implementing commit `3df5f2d^`, copied the shipped test file into it, and ran it — **42 failed, 4 passed**, matching the package's claim exactly (not merely re-running the implementer's own report). | Pass |
| Full suite green, both permanent gates green | See Test run below. | Pass |
| No shipped vignette's behaviour changes (test 11 + tutorial/replay tests) | `test_shipped_vignette_unaffected_by_empty_series_and_no_bcs` passes; the pre-existing `test_vignette_tutorials.py`/replay suites are part of the 1108-passed full run (below), unaffected. | Pass |
| Ledgers updated and package `COMPLETE` | MBP, `packages/INDEX.md`, `ROADMAP.md`, RTM (`FR-1230`/`FR-4440` rows), `CLAUDE.md` code map all updated at commit `85130cf`/`3df5f2d`. Confirmed by direct read (see Requirements audit). FS-123's own `Referenced By` was deliberately left saying "`IP-1230` (planned)" — disclosed by the package as routed to `09`, per the `run #182` precedent (`VR-1064`/`FS-106`). Corrected by this verification run. | Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Anchor tables match ADR-0039 decisions 2 and 3 exactly | Read `_F_SOLAR_ANCHORS = ((50.0, 0.3), (150.0, 1.0), (300.0, 3.0))` and `_F_GEO_ANCHORS = ((0.0, 1.0), (4.0, 1.0), (5.0, 2.0), (9.0, 10.0))` (`perturbations.py` lines 186–187) — byte-for-byte the ADR's tables. Independently re-derived on **fresh inputs not in the package's own test list**: `f_solar(225) = 2.0` (expected via linear interpolation between (150,1.0) and (300,3.0): 2.0 ✓), `f_solar(100) = 0.65` (midpoint of (50,0.3)-(150,1.0) ✓), `f_geo(6) = 4.0` (midpoint of (5,2.0)-(9,10.0) at Kp 6 ✓), `f_geo(8) = 8.0` ✓, `f_geo(4.5) = 1.5` (interpolating the (4,1.0)-(5,2.0) segment, confirming the flat-then-rising shape continues smoothly rather than stepping ✓), clamp behaviour at F10.7=10 and 1000 ✓. `drag_multiplier` at a fresh (225, 6) combination = 8.0 = `f_solar(225)·f_geo(6)` ✓; `anomaly_rate_multiplier` at the same point = 4.0, confirming F10.7 is ignored ✓ (all computed by hand, matched exactly). | Pass |
| Drag step returns early with no series, charges no `delta_v_ms` | `_apply_index_drag` line 82: `if not series: return` before any loop, state read, or RNG use. Grepped the function body for `delta_v_ms` — absent; the impulse is applied via `apply_impulse` directly, not through the `maneuver` cost-charging path. | Pass |
| `env_anomaly_check` scheduled only when `environmental_anomalies` set; one draw per listed asset per tick, always | `_arm_schedule` line 278: `if self.vignette.environmental_anomalies:` gates the scheduling loop entirely — confirmed no `env_anomaly_check` event exists in `test_shipped_vignette_unaffected_by_empty_series_and_no_bcs`'s event log. `_h_env_anomaly_check` line 1408: `draw = rng.random()` executes inside the `for aid in block.get("assets", [])` loop **before** the asset-existence/bus/safe-mode skip checks (lines 1409–1413), so the draw is unconditional per listed asset per tick as claimed. | Pass |
| Load and inject refusal share `index_series_problems` | `vignette.py` line 481 imports and calls `engine.perturbations.index_series_problems` for both `space_weather_series` (key `at_sim_s`) and `initial_space_weather.index_series` (key `t`); `manager.py` line 68 calls the same function with key `offset_s`, `time_required=False`. One function, three call sites — confirmed by `grep`, no duplicate/divergent validator. | Pass |
| Series-only inject leaves severity untouched; severity-only inject keeps the series | `manager.py` lines 1271–1295: `has_series = "index_series" in eff`; the severity-setting block only runs `if "severity" in eff or not has_series` — so a series-only inject (`has_series=True`, no `"severity"` key) skips the severity block entirely, and a severity-only inject (`has_series=False`) does not touch `sw["index_series"]` because the `if has_series:` branch is skipped. Confirmed by code read; also exercised by the package's own `test_series_inject_leaves_severity_and_severity_inject_keeps_series`, which passes. | Pass |
| Replay byte-identical for an opted-in run | `test_drag_run_replays_byte_identically` and `test_environmental_anomaly_firings_replay_identically` both pass in the full run. Not independently re-built from scratch in this pass (the determinism mechanism itself — event-sourced replay via `sim.replay()` — is the same seam `VR-1021`/`VR-1064` already stress-tested at the engine level for this exact class of claim; re-deriving it per-package would duplicate that evidence). Spot-checked instead that the drag step and the anomaly handler draw from no source but `world`, sim time, declared data, and the handler's seeded `rng` (confirmed by reading every line of `_apply_index_drag` and `_h_env_anomaly_check` — no wall-clock, no unseeded `random`, no global state). | Pass |
| `test_determinism.py`/`test_import_guard.py` green, full suite count reported | See Test run. | Pass |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| `FR-1230` | `engine/perturbations.py` (`f_solar`, `f_geo`, `drag_multiplier`, `index_series_problems`); `engine/busmodel.py` (`BusSystem._apply_index_drag`); `engine/entities.py` (`Asset.ballistic_coeff_m2_kg`); `content/vignette.py` (`space_weather_series`, `build_world`, `validate_vignette`) | `test_f_solar_anchors`, `test_f_geo_anchors`, `test_index_in_effect_is_step_held_per_index`, `test_active_series_decays_faster_than_quiescent_and_both_decay`, `test_drag_run_replays_byte_identically`, `test_only_qualifying_assets_are_drag_coupled`, load/inject refusal tests | RTM row (`docs/requirements/03-requirements-traceability-matrix.md` line 178) names `IP-1230` and the exact test list; updated to drop the "awaiting `09`" qualifier (see below) | Pass |
| `FR-4440` | `session/manager.py` (`_h_env_anomaly_check`, gated `env_anomaly_check` arm, `space_weather` inject key-update); `engine/perturbations.py` (`anomaly_rate_multiplier`); `content/vignette.py` (`environmental_anomalies`) | `test_high_kp_fires_more_environmental_anomalies`, `test_environmental_anomaly_firings_replay_identically`, `test_bus_anomaly_skips_an_already_safed_asset`, `test_drag_and_anomaly_multipliers` | RTM row line 221, same qualifier update | Pass |

Both RTM rows were confirmed to name real files, real functions and real tests that exist in the
tree exactly as listed — no placeholder, no stale cell. Updated the "`COMPLETE 2026-10-18, run
#189, awaiting 09`" status text in both rows to "`VERIFIED`" with this report's reference, since
the content itself (files/tests named) was already correct and needed no substantive change.

## Test run

Commands run, exact:

```
python3 -m pytest spacesim/tests/test_space_weather_index.py -q       → 46 passed
python3 -m pytest -q                                                   → 1108 passed, 3 skipped
python3 -m pytest spacesim/tests/test_determinism.py \
                  spacesim/tests/test_import_guard.py -q               → 14 passed
```

(The 1108/3 full-suite count is larger than the package's own reported 1071/3 baseline because
two sibling packages — `IP-1066`, `IP-1067` — were implemented and verified-pending in later
pipeline runs on the same branch, adding their own tests; this is expected growth, not a
regression. No test in the suite failed.)

## Scope audit

`git show 3df5f2d --stat`: `CLAUDE.md`, `ROADMAP.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `IP-1230`'s own package file, the RTM, plus
`spacesim/content/vignette.py`, `spacesim/engine/busmodel.py`, `spacesim/engine/entities.py`,
`spacesim/engine/perturbations.py`, `spacesim/session/manager.py`, and the new
`spacesim/tests/test_space_weather_index.py` — exactly the package's declared `Files to
Create`/`Files to Modify` list, no excursion.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | Design Decision 8 specified a `model_validator`; the shipped code uses a `field_validator` (disclosed by the package itself). Functionally equivalent for this single-field, no-cross-field-dependency case, and the disclosed consequence (the refusal message names `…ballistic_coeff_m2_kg` rather than a bare field name) is accurate and harmless for a load-time refusal that already prefixes with `blue_forces[<id>].…`. | Low (informational, accepted) | None — no action required |
| 2 | `index_series_problems` gained a `time_required` keyword not named in Design Decision 4's text (disclosed). Confirmed necessary and correct: the inject boundary's `offset_s` has a stated default of 0 (Design Decision 2), so a bare `{"kp": 5.0}` entry with no `offset_s` key must not be refused for a missing time key the same way a vignette-authored entry must. Read both call sites (`vignette.py` passes no keyword → default `True`; `manager.py` passes `time_required=False`) and confirmed the validator's branching (`if time_key in entry or time_required:`) produces exactly that distinction. | Low (informational, accepted) | None — no action required |
| 3 | FS-123's `Referenced By` field still read "`IP-1230` (planned)" at the start of this run. | Low (bookkeeping) | Corrected by this verification run |

No Medium or higher findings. No code, package, spec, or requirement was edited to reach this
result — only the bookkeeping backlink in Finding 3 and the ledger status transitions below.

## Independent physics checks performed (beyond the checklist)

1. **Fresh-input re-derivation of the ADR-0039 formula** (not the package's own anchor examples):
   `f_solar(225)=2.0`, `f_solar(100)=0.65`, `f_geo(6)=4.0`, `f_geo(8)=8.0`, `f_geo(4.5)=1.5`,
   `f_geo(2)=1.0`, clamp checks at F10.7∈{10,1000}, `drag_multiplier`/`anomaly_rate_multiplier` at a
   fresh (F10.7=225, Kp=6) point — every value matched hand computation of the piecewise-linear
   interpolation exactly.
2. **Drag-to-impulse conversion**, independently checked against the standard orbital-energy
   relation rather than trusted as written: for a near-circular orbit, specific energy
   `E = -μ/(2a)`, and a tangential impulse gives `dE = v·dv`, so `da = 2a²v·dv/μ` ⇒
   `dv = μ·da/(2a²v)`. This is exactly `busmodel.py` line 96's formula
   (`dv = MU_EARTH * drop / (2.0 * a * a * speed)`), confirming the impulse-conversion step is
   physically correct, not merely internally consistent. A fresh numeric instance (400 km, BC
   0.02, 300 s tick, multiplier 8.0) produced `secular_drag_decay = -0.874 m`, `drop = 6.99 m`,
   `dv ≈ 0.00396 m/s` — a physically sane sub-cm/s per-tick retrograde burn for this BC/altitude
   class, consistent with known LEO decay magnitudes.
3. **Pre-fix test-failure reproduction**: built a disposable git worktree at the parent of the
   implementing commit, dropped in the shipped test file, and ran it cold — **42 failed, 4
   passed**, matching the package's own claim exactly, independently reproduced rather than
   trusted.
4. **Determinism-invariant review**: confirmed by direct line-by-line read that `_apply_index_drag`
   and `_h_env_anomaly_check` read no wall clock and draw no unseeded randomness; both permanent
   gates (`test_determinism.py`, `test_import_guard.py`) pass by name.

## Independence statement

Fresh session; no prior involvement in commit `3df5f2d` or any earlier `IP-1230` work. All checks
above were built from scratch (fresh fixtures, fresh numeric inputs, a fresh worktree) rather than
re-running the implementer's own evidence unexamined.

## Verdict

**VERIFIED.** No findings require routing back to `08-code-implementation`.
