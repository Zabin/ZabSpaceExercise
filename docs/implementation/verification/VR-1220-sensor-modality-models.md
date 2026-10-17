# VR-1220 — Verification Report: Sensor Modality Models

> **Document ID:** VR-1220
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1220](../packages/IP-1220-sensor-modality-models.md), [FS-122](../../features/FS-122-sensor-modality-models.md) v1.0 (`FR-1610`–`FR-1660`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1220
> **Feature Mapping:** FS-122 (`FR-1610`–`FR-1660`)
> **Related Topics:** [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py),
> [`spacesim/engine/access.py`](../../../spacesim/engine/access.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/ssn.py`](../../../spacesim/engine/ssn.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1220 — Sensor Modality Models
- **Version verified:** 1.0
- **Tree state verified:** commit `d2fc118` (branch `claude/chart-prompt-file-90hm9u`). Implementing
  commit: `7bfe86f`.
- **Independence:** first verification pass, fresh session with no involvement in the implementing
  commit. All claims re-derived from the live source and a fresh test run.

## Result

**VERIFIED, with 1 Low finding.** All six requirements (`FR-1610`–`FR-1660`) are confirmed
implemented and tested. Full suite green (753 passed, 3 skipped), both permanent gates green. One
Low finding: the package's own `IP-1220-sensor-modality-models.md` document was never updated by
the implementing commit (Status header still reads `🟡 READY`, every DoD/Verification-Checklist
box still unchecked `[ ]`) even though the Master Build Plan, `packages/INDEX.md`, `CLAUDE.md`, and
the RTM were all correctly updated — a documentation-completeness gap in the package's own file,
not in the shipped code or its actual status.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All six new `Sensor` fields exist, default-absent, zero behavior change when unset. | `entities.py:85-90`: `beam_mode`, `exclusion_angle_deg`, `min_range_km`, `altitude_band_affinity: Optional[str] = None`, `requires_cue: bool = False`, `host_asset_id: Optional[str] = None` — all `Optional`/default-`None`/`False`. `_sensor_orbit()` (`access.py:237-243`) falls back to `sensor.orbit` when `host_asset_id is None`; every new check (`min_range_km`, `exclusion_angle_deg`, `requires_cue`) is guarded by an `is not None`/`if sensor.requires_cue` test before altering behavior. | ✅ Pass |
| Fence/dish beam-mode trade produces the expected detection/gain contrast. | `isr.py`'s `BEAM_MODES["ground_radar"]` (`:77-89`) has both `"fence"` (wide-FoR, low-gain) and `"dish"` (narrow, high-gain) sub-entries. `test_ground_radar_fence_vs_dish_trade`/`test_ground_radar_default_mode_is_dish` (`test_isr.py:203-220`) — both green. | ✅ Pass |
| Exclusion-angle check rejects/grants per the declared boundary, composing with the existing lighting predicate. | `access.py:280-312`: `_sun_exclusion_angle_deg()` computed after the existing `needs_lighting` check; `sensor.exclusion_angle_deg is not None` gate. `test_exclusion_angle_rejects_near_sun_and_accepts_far_from_sun` (`test_access.py:144`) — green. | ✅ Pass |
| Min-range floor rejects below threshold; altitude-band affinity degrades gain outside the declared band. | `access.py:258`: hard reject before the existing max-range/LOS checks. `isr.py::effective_gain()` (`:118+`) gains a band-affinity degradation term. `test_min_range_floor_rejects_too_close_space_sensor` (`test_access.py:182`), `test_effective_gain_band_affinity_mismatch_degrades_gain` (`test_isr.py`, cited by RTM `:147`) — both green. | ✅ Pass |
| Cue-dependent sensor tasking rejected without an existing `Track`, accepted with one. | `orders.py:480-481`: `if sensor.requires_cue and self.world.track_for(order.cell, order.target) is None: return False, "requires_cue"`. Three tests in `test_orders.py:356-393` (rejected/accepted/`fail_reason` value) — all green. | ✅ Pass |
| Passive-RF network fix produced only with a sufficient receiver count and an emitting target. | `ssn.py::passive_rf_fix()` (`:406-426`): non-emitting → `None` immediately; `needed = 4 if three_d else 3`; counts member sensors with an active `SENSOR_OBSERVATION` window at `t`; `< needed` → `None`. `test_passive_rf_fix_requires_min_receivers_and_emitting_target` (`test_ssn.py:255-281`) parametrizes 2/3/4 receivers × 2D/3D × emitting/non-emitting — green. | ✅ Pass |
| Hosted-sensor position reflects the host Asset's current state, including post-manoeuvre; both naming identifiers produce identical results. | `_sensor_orbit()` (`access.py:237-243`) resolves live from `self.scene.satellites[host_asset_id]` at call time, not a cached position — so a post-manoeuvre update to the host's orbit is picked up automatically. `_resolve_sensor_id()`/`_candidate_sensors()` (`orders.py:443-460`) let an order name either the sensor's own id or its `host_asset_id`. `test_hosted_sensor_follows_host_asset_orbit_and_both_identifiers_match` (`test_access.py:197`) — green. | ✅ Pass |
| Full existing test suite green, zero regressions, both permanent gates green. | 753 passed, 3 skipped. `test_determinism.py` 6 passed, `test_import_guard.py` 8 passed. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Every new test named above exists and is green. | Re-run standalone: `test_access.py`, `test_isr.py`, `test_orders.py`, `test_ssn.py` — 96 tests combined, all green. | ✅ Pass |
| `test_determinism.py` remains green. | 6 passed. None of the five touched files is called from a code path with wall-clock/RNG use; all new logic is a pure function of `(sensor, t, world)`. | ✅ Pass |
| `test_import_guard.py` remains green. | 8 passed. All five touched files are already inside `spacesim/engine/`, which the guard already scans; no new forbidden import/wall-clock/random pattern introduced (confirmed by reading each diff hunk). | ✅ Pass |
| Independently confirm the six fields are genuinely additive/optional (byte-identical behavior when unset). | Confirmed by direct read: every one of the six checks (`min_range_km`, `exclusion_angle_deg`, `requires_cue`, `host_asset_id`, `altitude_band_affinity`, `beam_mode`) is gated by an explicit `is not None`/truthiness test that short-circuits to the pre-existing behavior when the field is unset — no new code path is unconditionally reached. Every one of the 19 shipped library vignettes' `Sensor` declarations was checked (`grep -rn "beam_mode\|exclusion_angle_deg\|min_range_km\|altitude_band_affinity\|requires_cue\|host_asset_id" spacesim/content/vignettes/*.yaml` — zero matches), confirming zero behavior change for any shipped vignette. | ✅ Pass |
| Independently confirm `FR-1650`'s network fix never bypasses `CellController`'s fog-of-war filter when delivering into a cell's `TrackCatalog`. | **`passive_rf_fix()` is a standalone pure function with no caller anywhere in `spacesim/` outside its own test file** (`grep -rn passive_rf_fix spacesim/` confirms only `ssn.py`'s definition and `test_ssn.py`'s calls). It returns the list of contributing sensor ids only; it never touches `world.tracks`, any `TrackCatalog`, or `CellController`. There is therefore no delivery path to bypass — the check passes vacuously, not because a delivery path was audited and found safe. `FR-1650`'s own Requirements text ("Outputs: A geolocation fix... or no fix") does not require delivery into a `Track`, so this is not a DoD gap against the requirement as written, but it means the function is presently unreachable from any operator- or White-Cell-facing flow (see Findings). | ✅ Pass (see L1) |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-1610 | `isr.py::BEAM_MODES["ground_radar"]` | `test_isr.py::test_ground_radar_fence_vs_dish_trade` | RTM `:145` — `IP-1220`, correct. | ✅ Pass |
| FR-1620 | `access.py::_observation_predicate` (ground branch) | `test_access.py::test_exclusion_angle_rejects_near_sun_and_accepts_far_from_sun` | RTM `:146` — correct. | ✅ Pass |
| FR-1630 | `access.py::_observation_predicate` (space branch), `isr.py::effective_gain` | `test_access.py::test_min_range_floor_rejects_too_close_space_sensor`, `test_isr.py::test_effective_gain_band_affinity_mismatch_degrades_gain` | RTM `:147` — correct. | ✅ Pass |
| FR-1640 | `orders.py::_validate` | `test_orders.py::test_cue_dependent_sensor_rejected_without_existing_track` | RTM `:148` — correct. | ✅ Pass |
| FR-1650 | `ssn.py::passive_rf_fix` | `test_ssn.py::test_passive_rf_fix_requires_min_receivers_and_emitting_target` | RTM `:149` — correct as written; see L1 for the unwired-delivery observation. | ✅ Pass |
| FR-1660 | `access.py::_sensor_orbit`, `orders.py::_resolve_sensor_id`/`_candidate_sensors` | `test_access.py::test_hosted_sensor_follows_host_asset_orbit_and_both_identifiers_match` | RTM `:150` — correct. | ✅ Pass |

## Test run

```
python3 -m pytest -q                                                              # full suite
  → 753 passed, 3 skipped, 1 warning in 168.20s
python3 -m pytest spacesim/tests/test_determinism.py -q                           # gate 1 → 6 passed
python3 -m pytest spacesim/tests/test_import_guard.py -q                          # gate 2 → 8 passed
python3 -m pytest spacesim/tests/test_access.py spacesim/tests/test_isr.py \
  spacesim/tests/test_orders.py spacesim/tests/test_ssn.py -q                     # package-specific
  → 96 passed
```

## Scope audit

`git show --stat 7bfe86f` touches: `CLAUDE.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/requirements/03-requirements-traceability-matrix.md`,
`spacesim/engine/access.py`, `spacesim/engine/entities.py`, `spacesim/engine/isr.py`,
`spacesim/engine/orders.py`, `spacesim/engine/ssn.py`, `spacesim/tests/test_access.py`,
`spacesim/tests/test_isr.py`, `spacesim/tests/test_orders.py`, `spacesim/tests/test_ssn.py`. This
is exactly the package's own declared `Files to Modify` list plus its named test files and doc
companions — no excursion. **Notably absent:** `docs/implementation/packages/IP-1220-sensor-
modality-models.md` itself (see Findings L1) and `docs/features/FS-122-sensor-modality-models.md`
(the package's own Documentation Updates section named both).

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 | The package's own document (`IP-1220-sensor-modality-models.md`) was never updated by the implementing commit: its Status header still reads `🟡 READY`, and every Definition-of-Done and Verification-Checklist checkbox is still `[ ]` unchecked, even though the actual work is complete, tested, and (as of this report) independently verified. The Master Build Plan row, `packages/INDEX.md`, `CLAUDE.md`'s Code Map, and the RTM were all correctly updated — only the package's own file was missed. `FS-122-sensor-modality-models.md`'s `Referenced By` metadata was also not updated, as the package's own Documentation Updates section required. This is a process-hygiene gap, not a functional defect — every requirement is genuinely met. | Low | `08-code-implementation` (a small doc-only follow-up; does not block `VERIFIED`) |
| L2 | `passive_rf_fix()` (`FR-1650`) is a pure, correctly-tested function with no caller anywhere in the session/UI layers — nothing currently invokes it from an order, inject, or White-Cell-facing flow, unlike the existing `ssn_collect`/`ssn_deliver` two-handler pattern it was modeled on. `FR-1650`'s own Requirements text does not mandate delivery, so this is not a DoD failure, but the capability is presently inert from an operator's perspective. | Low | `07-implementation-planning` (a future package to wire delivery, if White Cell wants an in-session passive-RF collection flow) |

## Related

[IP-1220](../packages/IP-1220-sensor-modality-models.md) · [FS-122](../../features/FS-122-sensor-modality-models.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
