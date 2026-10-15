# IP-1221 — CATS Phase-Angle Observation-Gain Refinement for Passive EO Sensors (FR-1670)

> **Package ID:** IP-1221
> **Version:** 1.0
> **Status:** 🟡 IN PROGRESS — `08-code-implementation`, pipeline run #125 (2026-10-15)
> *(Authored 2026-10-15 by `07-implementation-planning`, pipeline run #124.)*
> Authorized by the project owner 2026-10-11 (MSTR-006 §3) through the standing pre-authorization
> of the packages this iteration reaches. Same precedent as `IP-1212`/`IP-1063`/`IP-1262`.
> **Dependencies:** [FS-122](../../features/FS-122-sensor-modality-models.md) v1.1 (`FR-1670`:
> System Behaviour "Normal path — `FR-1670`" and its three edge cases; Acceptance Criteria 7–11;
> Open Questions 3–5, resolved here as Design Decisions 3–5);
> [IP-1220](IP-1220-sensor-modality-models.md) (`VERIFIED`, `VR-1220`; owns the `Sensor` fields and
> the `effective_gain` seam this package extends);
> [IP-1300](IP-1300-ric-frame-view-and-cats-overlay.md) (`VERIFIED`; owns
> `engine/sun.py::cats_phase_angle_deg`, consumed unchanged)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0122`, `BL-0151`,
> `BL-0208`, `BL-0209`
> **Produces:** an optional, author-declared usable phase-angle range on a passive EO `Sensor`. An
> observation whose Sun-target-sensor phase angle at its scheduled instant falls outside that range
> gets a smoothly reduced observation gain.
> **Feature Reference:** [FS-122 — Sensor Modality Models](../../features/FS-122-sensor-modality-models.md)
> v1.1 (`FR-1670`)
> **Related Topics:** [`R109` v1.3](../../research/encyclopedia/R109-sensor-operations.md) §3.11,
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/sun.py`](../../../spacesim/engine/sun.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Source: `BL-0122` (CATS access refinement), via `FR-1670` (run #82),
`FEAT-1600` (run #83) and FS-122 v1.1 (run #123). `FR-1610`–`FR-1660` are built (`IP-1220`), so
this is the next slice in the FS-122 series. Every file, function and line cited below was checked
against the tree at `b0e77a6`.*

## Package ID

IP-1221

## Title

CATS Phase-Angle Observation-Gain Refinement for Passive EO Sensors (FR-1670)

## Objective

Today an observe order's gain comes from `isr.effective_gain` (`isr.py:118-137`), via
`OrderSystem._exec_payload`'s observe branch (`orders.py:653-729`, call at `:702`). The gain is
shaped by beam mode, look angle and (`FR-1630`) altitude-band affinity. It does not depend on how
well lit the target looks from the sensor.

After this package:

- A `Sensor` may declare an optional **usable phase-angle range**: a lower and upper bound in
  degrees, absent by default.
- For an observe order executed by a sensor that declares a range, the engine computes the phase
  angle at the observation's scheduled instant (the window start the execute event is scheduled
  at, `orders.py:441`), using the shared `sun.cats_phase_angle_deg`.
- Inside the range, gain is unchanged. Outside it, gain is multiplied by a factor below 1 that
  falls off smoothly (Design Decision 3).
- Nothing changes for any sensor that declares no range, which today means every sensor in every
  shipped vignette.

### Design Decisions

1. **Gain seam, not window rejection.** FS-122 v1.1 chose degradation (`R109` §3.11 "not a hard
   cliff"). The refinement therefore goes into `effective_gain`, the seam `FR-1630`'s band affinity
   already uses (`isr.py:135-136`). It gets one more optional, additive argument (the phase-angle
   factor or its inputs) and is applied after the existing terms. `AccessProvider` is not touched:
   lighting (`FR-1220`) and exclusion-angle (`FR-1620`) rejections run first and are unchanged, so a
   rejected window can never be re-admitted (FS-122 AC10).
2. **The angle is computed at the scheduled observation instant, from true positions.**
   `_exec_payload(order, win)` already receives the chosen window, and the execute event is
   scheduled at `win.start` (`orders.py:441`). The phase angle is evaluated at `win.start`, not at
   issue time (FS-122 Risks, timing). The positions used:
   - **Target:** the target `Asset`'s orbit (`world.assets[order.target].orbit`) propagated by
     `self.prop`.
   - **Ground sensor:** the site, `ecef_to_eci(geodetic_to_ecef(sensor.location), t)`, as
     `access.py:280-292` already does.
   - **Space-based sensor:** the host Asset's orbit when `host_asset_id` names an asset with an
     orbit (the `FR-1660` rule, `access.py:237-243`), otherwise the sensor's own `orbit`.

   Only `sun.cats_phase_angle_deg` computes the angle (`BL-0152`); no second phase-angle formula is
   written. When the target is not an `Asset` with an orbit, or the positions coincide (the
   function raises `ValueError`, `sun.py:95-96`), the factor is 1. The handler-side path never
   raises (FS-122 Error Handling).
3. **Degradation curve (resolves FS-122 Open Question 3, `BL-0151` residual).** For a declared
   range `[lo, hi]` and phase angle `θ`:
   - inside (`lo ≤ θ ≤ hi`): factor = 1;
   - above (`θ > hi`): factor falls **linearly** from 1 at `hi` to 0 at 180°;
   - below (`θ < lo`): factor falls linearly from 1 at `lo` to 0 at 0°.

   This is the simplest function meeting FS-122's contract: continuous at the bound, non-increasing
   beyond it, strictly below 1 everywhere outside. The 0 endpoint at 180° matches the Lambertian
   diffuse-sphere phase function `R109` §3.11 cites (Africano et al.), whose brightness at full
   backlight is 0. The ramp between the bound and the endpoint is a modelling choice, not a cited
   curve; it is recorded here so it can be revisited if `02-research-ow-orbital-mechanics` ever
   grounds a shape. A bound at the domain edge (`hi == 180`, or `lo == 0`) has no outside region on
   that side, so there is no division by zero.
4. **Malformed range declarations are rejected at model validation (resolves FS-122 Open Question
   4, `BL-0208`).** `Sensor` gains a validator. A declared range must have both bounds in `[0, 180]`
   with `lo ≤ hi`, otherwise `Sensor.model_validate` raises. The vignette loader already builds every
   sensor through `Sensor.model_validate` (`content/vignette.py:303-305`), so a bad vignette fails
   at load with a pydantic message rather than misbehaving at run time. Rejecting rather than
   ignoring follows the repository's pattern for every other typed `Sensor` field (`kind` is a
   `Literal`).
5. **"Passive EO" means `needs_lighting` (resolves FS-122 Open Question 5, `BL-0209`).** The factor
   is applied only when the executing sensor has `needs_lighting` set, the engine's own optical
   flag (`entities.py:75`). A range declared on a sensor without `needs_lighting` (e.g. a ground
   radar) is also rejected by the Design Decision 4 validator, with a reason naming the field. This
   is stricter than the `FR-1620` precedent, which applies `exclusion_angle_deg` with no kind check.
   It is chosen because silently ignoring a declared field is the worse failure for an author, and
   no shipped vignette declares one. If `04-requirements-engineering` later broadens "passive EO",
   only this validator and the one guard change.
6. **No change to any cell-scoped response.** The angle and the factor are not added to the observe
   payload's visible fields or to `dry_run`'s output. The cell sees only the resulting track
   confidence (FS-122 Security). Recording the factor in the eventlog payload is allowed but not
   required. Replay recomputes nothing, because the gain is already in the scheduled payload.

## Feature Reference

- **FS-122** v1.1: System Behaviour "Normal path — `FR-1670`" and its edge cases (window already
  rejected; no declared range; coincident positions); Subsystem Responsibilities (v1.1 rows); Data
  Model Changes (v1.1 bullet); Error Handling (v1.1); Performance (determinism); Security; Acceptance
  Criteria 7–11; Verification Plan (v1.1); Open Questions 3–5.

## Requirements Covered

- `FR-1670` — Phase-angle (CATS) based access-window refinement for passive EO sensors.
  The "observation effectiveness is measurably degraded" branch is implemented; the
  window-rejection branch is not used (Design Decision 1, FS-122 v1.1).

No other requirement is touched. `FR-1220`, `FR-1620`, `FR-1630`, `FR-1660` and `FR-8220` are
consumed and not changed.

## Architecture Components

- **C1 Simulation Engine** only: `engine/entities.py` (`Sensor` field and validator),
  `engine/isr.py` (`effective_gain` and the phase-angle factor), `engine/orders.py` (the observe
  branch computes the angle at `win.start`), and `engine/sun.py` (consumed, unchanged).
- No session, content-loader, server or UI code changes. The FS-122 v1.1 C2 row is satisfied by
  the existing vignette load path.

## Interfaces

- `INT-0008` (SessionManager → Engine OrderSystem), the only interface the RTM lists for `FR-1670`.
  No new interface, route, request field or response field.

## Files to Create

- `spacesim/tests/test_phase_angle_gain.py` — this package's tests (Tests 1–8).

## Files to Modify

- `spacesim/engine/entities.py` — `Sensor` (`:68-90`): add one optional usable-phase-angle-range
  field after `host_asset_id` (`:90`), plus a model validator (Design Decisions 4–5). The
  field's name and representation are the implementer's choice: a two-element pair or two
  optional floats, both absent by default.
- `spacesim/engine/isr.py` — add a pure phase-angle factor helper next to
  `_BAND_AFFINITY_MISMATCH_FACTOR` (`:115`), and extend `effective_gain` (`:118-137`) with an
  optional, additive phase-angle argument applied after the band term. Omitting it must reproduce
  today's result exactly.
- `spacesim/engine/orders.py` — `_exec_payload` observe branch (`:653-729`): for an `actor_sensor`
  with `needs_lighting` and a declared range, compute the phase angle at `win.start` (Design
  Decision 2) and pass it to `_eg(...)` at `:702`. Import `cats_phase_angle_deg` from
  `engine/sun.py` and `ecef_to_eci`/`geodetic_to_ecef` from `engine/geometry.py`, function-local like
  the existing `isr`/`geometry` imports at `:680-682`/`:707`.
- `spacesim/tests/test_cats_angle.py` — extend `test_phase_angle_is_defined_only_once_in_engine`
  (`:57-62`), or add a sibling test, to also assert that `orders.py` references
  `cats_phase_angle_deg` (FS-122 AC11).

## Implementation Tasks

1. Mark this package `IN PROGRESS` on the Master Build Plan, `packages/INDEX.md` and `ROADMAP.md`
   before any edit.
2. Write Tests 1–8 and see them fail. Tests 3, 7 and 8 may pass on arrival, since they assert
   that nothing changes; record which did.
3. Add the `Sensor` field and validator (Design Decisions 4–5).
4. Add the factor helper and extend `effective_gain` (Design Decisions 1, 3).
5. Wire the observe branch: resolve the target and sensor positions at `win.start`, call
   `cats_phase_angle_deg`, guard the undefined cases to factor 1, and pass the result through
   (Design Decision 2).
6. Run the full suite and both permanent gates; fix only what this package broke.
7. Update the documentation and ledgers (Documentation Updates), then mark `COMPLETE`.

## Tests to Add

All in `spacesim/tests/test_phase_angle_gain.py` unless noted. Geometry fixtures reuse the
`test_cats_angle.py` construction (place the target and observer relative to `sun_unit_eci(t)` to
get a chosen angle).

1. **Factor shape (unit).** The helper returns 1 at every angle inside `[lo, hi]`, including both
   bounds. Above `hi` and below `lo` it is strictly below 1, non-increasing moving away from the
   range, tends to 1 approaching the bound, and is 0 at 180° (for `hi < 180`) and at 0° (for
   `lo > 0`). A range with `hi == 180` gives 1 at 180°. *(AC7, AC8; Design Decision 3)*
2. **`effective_gain` composition.** With no phase-angle argument the result equals today's for
   the same inputs (regression). With an angle inside the range it is equal; outside it is
   strictly lower. With band-affinity mismatch present as well, both factors apply. *(AC7, Design
   Decision 1)*
3. **No declared range ⇒ unchanged.** A ground-optical observe with no range produces the same
   scheduled `gain` as before the package, at a backlit geometry. *(AC10)*
4. **Ground-optical end to end.** A minimal world with a `ground_optical` sensor (`needs_lighting`,
   range 0°–90°) and a target satellite is observed twice through `OrderSystem`: once with a
   geometry whose phase angle at `win.start` is inside the range, once outside. The scheduled
   `execute_observe` payload's `gain` is equal to the no-range value in the first case and strictly
   lower in the second. *(AC7)*
5. **Space-based and hosted.** The same check for a `space_based` optical sensor declaring 0°–150°,
   and for a hosted sensor (`host_asset_id`), whose observer position is the host's orbit. Moving the
   host changes the angle and therefore the factor. *(AC9, `FR-1660`)*
6. **Validator.** `Sensor.model_validate` rejects `lo > hi`, a bound outside `[0, 180]`, and a range
   on a sensor without `needs_lighting`; it accepts a valid range on a `needs_lighting` sensor.
   *(Design Decisions 4–5)*
7. **Shipped content unchanged.** Every vignette in `content/vignettes/` loads, and no sensor in any
   of them declares a range. *(AC10)*
8. **Single definition (in `test_cats_angle.py`).** `def cats_phase_angle_deg` appears only in
   `engine/sun.py`, and `engine/orders.py` references it. *(AC11, `BL-0152`)*

The Phase-1 determinism gate (`test_determinism.py`) and the engine import guard
(`test_import_guard.py`) must stay green: the new code is pure, reads no wall clock, draws no RNG
and imports nothing outside `engine/`.

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md` — the `FR-1670` row: implementation
  `IP-1221` and the test names. The `08` precedent for RTM rows is `IP-1212`/`FR-7440`.
- `CLAUDE.md` code map — the `engine/isr.py` bullet (phase-angle factor) and the `engine/sun.py`
  bullet (now consumed by `FR-1670`).
- This package's Status header, the Master Build Plan row, `packages/INDEX.md`, `ROADMAP.md`'s
  implementation-package row, and `FS-122`'s `Referenced By` (metadata only).
- **Manual impact:** route to `08-training-manual-authoring` via the backlog. `FR-1670` is
  author-facing (vignette sensor field); check `training/15` §15.1 for the sensor-modality row.
  There is no operator-visible UI change.

## Definition of Done

- A `needs_lighting` sensor with a declared range yields unchanged gain inside the range and
  strictly lower gain outside it, with the Design Decision 3 shape, for ground, space-based and
  hosted sensors.
- A sensor without a range behaves exactly as before, and every shipped vignette loads with no
  sensor declaring a range.
- A malformed or misplaced range is rejected at `Sensor` validation.
- `cats_phase_angle_deg` remains the only phase-angle definition, and `orders.py` uses it.
- No window-acceptance behaviour changed. No file outside `spacesim/engine/` and
  `spacesim/tests/` changed in code.
- The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green.
- The RTM, `CLAUDE.md`, the ledgers and the `FS-122` cross-link are updated, and the manual-impact
  finding is routed.

## Verification Checklist

- [ ] `git diff` of the implementing commit touches code only in `spacesim/engine/entities.py`,
      `isr.py`, `orders.py` and `spacesim/tests/`; `access.py` and `sun.py` are unchanged.
- [ ] Read `effective_gain`: with the new argument omitted, its arithmetic is identical to
      `isr.py:132-137` at `b0e77a6`.
- [ ] Read the observe branch: the angle is evaluated at `win.start`, the factor is applied only
      for `needs_lighting` sensors with a declared range, and every undefined case falls back to 1
      without raising.
- [ ] Tests 1–8 exist and pass; the Implementation Summary records which were seen failing first.
- [ ] Independent reproduction on a fixture other than the tests': a backlit and a front-lit
      observation by the same declared sensor give strictly lower and unchanged gain respectively.
- [ ] Pre-existing tests are unmodified except `test_cats_angle.py`'s single-definition test, if
      extended in place.
- [ ] `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass.
- [ ] The RTM `FR-1670` row cites `IP-1221`.
- [ ] The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header
      agree on status.

## Dependencies

- **Packages:** `IP-1220` (`VERIFIED`, `VR-1220`) and `IP-1300` (`VERIFIED`). Both are `VERIFIED`,
  so this package is `READY`.
- **Spec/requirement:** `FS-122` v1.1 (run #123) and `FR-1670` (run #82), both landed.
- **Authorization:** granted by the project owner 2026-10-11 (MSTR-006 §3) through the standing
  pre-authorization of this iteration's packages.
- **Parallelism:** there is no ordering constraint with any other open package. `IP-1160`
  (`BLOCKED`, unauthorized) touches `orders.py` validation, not the observe gain path.

## Risks

- **Determinism.** The factor is a pure function of propagated positions and sim time. It is
  computed once at plan time into the scheduled payload, exactly like the existing gain, so replay
  is unaffected. The determinism gate guards it.
- **Silent behaviour change.** Every existing call to `effective_gain` must keep its result. Test 2
  (regression) and Test 7 (no shipped sensor declares a range) guard this.
- **Validator strictness (Design Decision 5).** A future vignette that tags a radar with a range
  fails to load. This is intended and named in the error message. The Vignette Creator
  (`IP-1174`) builds sensors through the same model, so it surfaces the same error.
- **Modelling choice (Design Decision 3).** The linear ramp is not a cited curve. It affects only
  vignettes that opt in, and it is recorded for revisit.
- **Target not an `Asset`.** A target that is not an asset with an orbit gets factor 1. This is
  the documented fallback (no geometry, no refinement), not a gap.

## Rollback Considerations

Reverting the implementing commit removes the field, the validator, the factor and the observe
wiring. No shipped vignette declares the field, so no content needs to change. There are no
`SavedSession`, persisted-format, API or UI changes. A save made while the package was live
replays identically after rollback, because the gain is stored in the scheduled event payload.
The exception is a vignette authored to declare the field. `Sensor` uses pydantic's default config
(no `extra` setting in `entities.py`, so unknown keys are ignored), so after rollback such a
vignette still loads and the range is silently ignored.
