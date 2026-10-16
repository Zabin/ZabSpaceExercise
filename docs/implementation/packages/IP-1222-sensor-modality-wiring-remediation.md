# IP-1222 — Sensor-Modality Wiring Remediation: Radar Beam Modes, Cue Gate on Auto-Selection, Typed Regime Affinity (FR-1610, FR-1630, FR-1640)

> **Package ID:** IP-1222
> **Version:** 1.0
> **Status:** 🔵 COMPLETE — 2026-10-16, `08-code-implementation`, pipeline run #129. Awaiting
> `09-package-verification` in a fresh session. A radar's `fence`/`dish` (order param, else
> `Sensor.beam_mode`) selects the `ground_radar` table; a radar naming no radar mode stays on
> `isr_sar` `stripmap`. `auto` drops `requires_cue` sensors without a held track (`requires_cue`
> reason when none is left). `altitude_band_affinity` is `Optional[Regime]`, compared through
> `isr.altitude_band`. An unknown radar `beam_mode` fails `Sensor` validation. Tests:
> `test_sensor_modality_wiring.py` (10; 8 seen failing first, Tests 6 and 9 passed on arrival as
> planned). Full suite 879 passed / 3 skipped (882 collected; baseline 869/3/872) (JUnit), gates
> 14/14.
> *(Was 🟢 READY — authored 2026-10-16 by `07-implementation-planning`, pipeline run #128.)*
> Authorized by the project owner 2026-10-11 (MSTR-006 §3) through the standing pre-authorization
> of the packages this iteration reaches. Same precedent as `IP-1221`/`IP-1212`/`IP-1063`.
> **Dependencies:** [FS-122](../../features/FS-122-sensor-modality-models.md) v1.1 (`FR-1610`,
> `FR-1630`, `FR-1640`: User Workflows 1, 3, 4; Data Model Changes; Subsystem Responsibilities);
> [IP-1220](IP-1220-sensor-modality-models.md) (`VERIFIED`, `VR-1220`; the package this remediates);
> [IP-1221](IP-1221-cats-phase-angle-observation-gain.md) (`VERIFIED`, `VR-1221`; owns the `Sensor`
> validator and the observe-gain lines this package sits next to)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0212`, `BL-0213`,
> `BL-0214`
> **Produces:** a ground radar whose declared or requested `fence`/`dish` beam mode actually sets
> its observation gain; a cue-dependent sensor that cannot be reached through `auto` sensor
> selection without a track; and an `altitude_band_affinity` that is a checked orbit regime
> compared by altitude band.
> **Feature Reference:** [FS-122 — Sensor Modality Models](../../features/FS-122-sensor-modality-models.md)
> v1.1 (`FR-1610`, `FR-1630`, `FR-1640`)
> **Related Topics:** [`R109` v1.2](../../research/encyclopedia/R109-sensor-operations.md) §3.6,
> §3.8, §3.9; [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package. Source: `BL-0212`, `BL-0213`, `BL-0214`, all found by
`08-training-manual-authoring` in pipeline run #127 while documenting the `IP-1220` fields as-built.
`IP-1220` stays `VERIFIED`: its unit-level claims hold, but two of its requirements are not reached
end to end. Every file, function and line cited below was checked against the tree at `8f9829c`.*

## Package ID

IP-1222

## Title

Sensor-Modality Wiring Remediation: Radar Beam Modes, Cue Gate on Auto-Selection, Typed Regime
Affinity (FR-1610, FR-1630, FR-1640)

## Objective

Three gaps in the shipped `IP-1220` wiring:

1. **`FR-1610` is unreachable (`BL-0212`, Medium).** `BEAM_MODES["ground_radar"]` (`isr.py:73-80`)
   holds the `fence`/`dish` trade, but no observe order ever reads it. `_exec_payload`'s observe
   branch (`orders.py:681` onward) derives the payload type for a sensor actor from
   `needs_lighting` alone (`:703-707`: `"isr_eo"` or `"isr_sar"`), so a ground radar resolves the
   `isr_sar` table, and `fence`/`dish` fall back to `stripmap`. `Sensor.beam_mode`
   (`entities.py:85`) is never read anywhere. Live (run #127, `leo-isr-denial` seed 4):
   `BLUE-RADAR` observe with `beam_mode` `fence`, `dish` and none all executed as `stripmap`,
   gain 1.0.
2. **`FR-1640` is bypassed by `auto` (`BL-0213`, Medium).** `_validate` returns early for
   `actor == "auto"` (`orders.py:470-471`), and neither `_candidate_sensors` (`:443-449`) nor
   `_plan_collection` (`:411-436`) checks `requires_cue`. Reproduced at engine level: the same
   order is `rejected`/`requires_cue` naming the sensor, and `queued` on that sensor as `auto`.
3. **`FR-1630`'s affinity is unchecked (`BL-0214`, Low).** `altitude_band_affinity` is a free
   `Optional[str]` (`entities.py:88`). A misspelt value loads cleanly and halves every
   observation. The comparison at `isr.py:160` is exact, so a `LEO` sensor treats a `LEO_SSO`
   target as out of band although both are the same altitude band.

After this package, each requirement holds end to end through `OrderSystem`, and every shipped
vignette behaves exactly as before (none declares any of these fields, and no shipped order names
`fence` or `dish`).

### Design Decisions

1. **Which beam-mode table a ground radar uses (`BL-0212`).** In the observe branch, when the
   executing sensor (`actor_sensor`) is `kind == "ground_radar"` and the *effective requested mode*
   is a key of `BEAM_MODES["ground_radar"]`, the payload type is `"ground_radar"`. The effective
   requested mode is the order's `beam_mode` param when given, otherwise the sensor's declared
   `beam_mode`. In every other case the existing resolution (`:700-707`) is kept unchanged. This
   keeps a radar that names no radar mode bit-identical to today: it still resolves `isr_sar`
   `stripmap`, gain factor 1.0. Switching the radar default to `dish` (gain factor 1.6, today's
   `_DEFAULT_MODE["ground_radar"]`) would change every shipped exercise, which `FR-1610` does not
   ask for. The resolved mode is already recorded in the payload (`"beam_mode": resolved_mode`,
   `:762`), so the track's `last_beam_mode` and the scene show `fence`/`dish` with no further change.
2. **The sensor's `beam_mode` is the default, the order's param overrides.** This is the reading
   FS-122 User Workflow 1 gives: the author declares the mode on the sensor; an operator may still
   pick one per order. The sensor default also applies to non-radar sensor actors, resolved
   against whatever table the existing code chooses; an unknown key falls back exactly as
   `beam_params` already does (`isr.py:96-106`).
3. **A declared radar mode must exist (`BL-0212`).** The `Sensor` validator added by `IP-1221`
   (`_check_usable_phase_angle`, `entities.py:97-110`) gains a sibling check: a `ground_radar`
   that declares `beam_mode` must name a `BEAM_MODES["ground_radar"]` key, else
   `Sensor.model_validate` raises and the vignette fails at load. Non-radar sensors are not
   checked, because their table depends on the dual-registered asset's payload type, which the
   `Sensor` model cannot see. `entities.py` may import `BEAM_MODES` from `engine/isr.py`
   (engine-internal, allowed by the import guard). There is no cycle at `8f9829c`: `isr.py`
   imports only `math` and `typing` (`:16-17`).
4. **Auto-selection honours the cue gate (`BL-0213`).** In `_candidate_sensors`' `auto` branch,
   a sensor with `requires_cue` is dropped from the candidates when the cell holds no track on the
   target (`self.world.track_for(order.cell, order.target) is None`, the same test `_validate`
   uses at `:480`). If the filter removes every candidate, `_plan_collection` rejects with reason
   `requires_cue`. If no candidate existed in the first place, the existing `no_window` reason is
   kept. Because `dry_run` and `issue` share `_plan` → `_continue_plan` → `_plan_collection`
   (`:160-169`, `:287-289`), both get the fix from one change. Filtering, rather than rejecting the
   whole order, matches what `auto` means: pick a sensor that can do the job.
5. **Typed affinity, compared by altitude band (`BL-0214`).** `altitude_band_affinity` becomes
   `Optional[Regime]` (`orbit.py:19`), so a misspelt value fails at load like any other `Literal`
   field. For the gain comparison, `LEO_SSO` is treated as the `LEO` band on both sides (sensor
   affinity and target regime); every other regime compares exactly. Rationale: `FR-1630` names an
   *altitude-band* affinity, and SSO is an inclination/node-rate property within the LEO altitude
   band, not a separate band. The normalisation lives in `isr.py` next to
   `_BAND_AFFINITY_MISMATCH_FACTOR` (`:115`). If `04-requirements-engineering` later wants SSO as
   its own band, only that helper changes.
6. **No cell-visible contract change.** No new route, request field or response field. The only
   operator-visible differences are that a `fence`/`dish` request now changes the gain and the
   recorded beam mode, and that an `auto` observe can now be refused with `requires_cue`, a reason
   the UI already knows (it is shown through the existing dry-run reason path in `app.js`).

## Feature Reference

- **FS-122** v1.1: User Workflows 1 (fence-variant sensor), 3 (range/altitude-band affinity) and 4
  (cue-dependent tasking); Data Model Changes (the beam-mode reference and
  `altitude_band_affinity`); Subsystem Responsibilities (`entities.py`, `isr.py`, `orders.py`
  rows).

## Requirements Covered

- `FR-1610` — Fence/dish radar beam-mode variants (end-to-end reachability).
- `FR-1630` — Space-based sensor minimum-range floor and altitude-band affinity (the affinity half
  only; the range floor is unchanged).
- `FR-1640` — Cue-dependent sensor tasking precondition (the `auto` path).

`FR-1220`, `FR-1620`, `FR-1660` and `FR-1670` are consumed and not changed.

## Architecture Components

- **C1 Simulation Engine** only: `engine/orders.py` (observe payload type and beam-mode default;
  `auto` candidate filter), `engine/isr.py` (band normalisation helper), `engine/entities.py`
  (`Sensor` field type and validator).
- No session, content-loader, server or UI code changes. `access.py` is not touched: no
  observation-window predicate changes, consistent with `FR-1610`'s "existing ground/space access
  predicate is unchanged" Postcondition.

## Interfaces

- `INT-0008` (SessionManager → Engine OrderSystem) and `INT-0007` (CellController → Engine
  Custody, for the track lookup), the interfaces the RTM lists for these leaves. No new interface.

## Files to Create

- `spacesim/tests/test_sensor_modality_wiring.py` — this package's tests (Tests 1–9).

## Files to Modify

- `spacesim/engine/orders.py`:
  - `_exec_payload` observe branch (`:681` onward): the effective requested mode and the
    `ground_radar` payload-type selection (Design Decisions 1–2), before `_bp(...)` at `:711`.
  - `_candidate_sensors` (`:443-449`): the `auto` branch's `requires_cue` filter (Design
    Decision 4).
  - `_plan_collection` (`:411-436`): the `requires_cue` rejection reason when the filter emptied
    the candidate list (Design Decision 4). The implementer may return the "filtered by cue"
    signal from `_candidate_sensors` or recompute it; either is fine.
- `spacesim/engine/isr.py` — a pure altitude-band normalisation helper next to `:115`, used by
  `effective_gain`'s band comparison (`:160`). With no affinity, or with matching regimes other
  than `LEO`/`LEO_SSO`, results are unchanged.
- `spacesim/engine/entities.py` — `Sensor.altitude_band_affinity` typed `Optional[Regime]`
  (`:88`; import `Regime` from `engine/orbit.py`); the radar `beam_mode` check beside
  `_check_usable_phase_angle` (`:97-110`) (Design Decisions 3, 5).

## Implementation Tasks

1. Mark this package `IN PROGRESS` on the Master Build Plan, `packages/INDEX.md` and `ROADMAP.md`
   before any edit.
2. Write Tests 1–9 and see them fail. Tests 6 and 9 assert that nothing changes and may pass on
   arrival; record which did.
3. Wire the radar table and the sensor beam-mode default (Design Decisions 1–2).
4. Add the `auto` cue filter and its rejection reason (Design Decision 4).
5. Type the affinity, add the band normalisation, and add the radar `beam_mode` validator (Design
   Decisions 3, 5).
6. Run the full suite and both permanent gates; fix only what this package broke.
7. Update the documentation and ledgers (Documentation Updates), then mark `COMPLETE`.

## Tests to Add

All in `spacesim/tests/test_sensor_modality_wiring.py`. Fixtures may reuse
`test_orders.py`'s `_leo`/`_subpoint`/`_sim_with` construction.

1. **Radar mode by order param, end to end.** A `ground_radar` observes the same target through
   `OrderSystem.issue` three times: `beam_mode: fence`, `beam_mode: dish`, and none. The scheduled
   `execute_observe` payloads record `fence`, `dish` and `stripmap`. Gain is lowest for `fence`,
   highest for `dish`, and the no-mode gain equals today's (`isr_sar` `stripmap`). *(`FR-1610` AC;
   `BL-0212`)*
2. **Radar mode by sensor declaration.** A `ground_radar` declaring `beam_mode: fence` observes
   with no order param and executes as `fence`. The same sensor with an order param `dish`
   executes as `dish` (the param overrides). *(Design Decision 2)*
3. **Radar validator.** `Sensor.model_validate` rejects a `ground_radar` with `beam_mode: wiggle`,
   accepts `fence` and `dish`, and accepts any `beam_mode` on a non-radar sensor. *(Design
   Decision 3)*
4. **Auto respects the cue gate.** One cell owns only a `requires_cue` sensor. An `auto` observe
   against an untracked target is `rejected` with `requires_cue`, through both `issue` and
   `dry_run`. With a track held, the same order is `queued` on that sensor. *(`FR-1640` AC;
   `BL-0213`)*
5. **Auto falls through to a sensor that needs no cue.** The cell owns a `requires_cue` sensor and
   an ordinary sensor that both see the target. An `auto` observe against an untracked target is
   `queued` on the ordinary sensor, never the cue-dependent one. *(Design Decision 4)*
6. **No-candidate reason unchanged.** A cell with no sensors still gets the existing reason for an
   `auto` observe. *(Design Decision 4, regression)*
7. **Typed affinity.** `Sensor.model_validate` rejects `altitude_band_affinity: "leo"` and accepts
   each `Regime` value. *(Design Decision 5; `BL-0214`)*
8. **Band normalisation.** The `effective_gain` factor is unchanged for a `LEO` affinity against a
   `LEO_SSO` target and for a `LEO_SSO` affinity against a `LEO` target, halved for `LEO` against
   `GEO`, and identical to today's result when no affinity is declared. *(Design Decision 5)*
9. **Shipped content unchanged.** Every vignette in `content/vignettes/` loads, and no sensor in any
   of them declares `beam_mode`, `requires_cue: true` or `altitude_band_affinity`. *(Design
   Decision 1 rationale)*

Existing `IP-1220` tests (`test_isr.py::test_ground_radar_fence_vs_dish_trade`,
`test_orders.py`'s three `requires_cue` tests, the band-affinity test at `test_isr.py:189`) must
pass unmodified. The Phase-1 determinism gate (`test_determinism.py`) and the engine import guard
(`test_import_guard.py`) must stay green: the changes are pure engine code, read no wall clock,
draw no RNG and import nothing outside `engine/`.

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md` — the `FR-1610`, `FR-1630` and
  `FR-1640` rows: add `IP-1222` and the new test file.
- `CLAUDE.md` code map — the `engine/isr.py` bullet (ground-radar beam modes now reached; band
  normalisation) if the implementer's change makes the existing text inaccurate.
- This package's Status header, the Master Build Plan row, `packages/INDEX.md`, `ROADMAP.md`'s
  implementation-package row, and `FS-122`'s `Referenced By` (metadata only).
- **Manual impact:** route to `08-training-manual-authoring` via the backlog. The
  `06-the-vignette-library.md` "Authoring sensors" table (run #127) says `beam_mode` has no effect,
  that `auto` skips `requires_cue`, and that `altitude_band_affinity` is unchecked and compares
  `LEO`/`LEO_SSO` as different. All three rows, the `WCM-2` sentence on `beam_mode`, and the
  §15.1 sensor row change once this package is `VERIFIED`.

## Definition of Done

- A ground radar's `fence`/`dish` request, from the order or the sensor, sets the executed beam
  mode and gain; a radar naming no radar mode is unchanged.
- An `auto` observe never lands on a `requires_cue` sensor without a held track, and is refused
  with `requires_cue` when that was the only sensor able to take it, through `issue` and `dry_run`.
- `altitude_band_affinity` accepts only `Regime` values; `LEO` and `LEO_SSO` compare as one band.
- A `ground_radar` declaring an unknown `beam_mode` fails `Sensor` validation.
- Every shipped vignette loads and behaves as before. No code outside `spacesim/engine/` and
  `spacesim/tests/` changed.
- The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green.
- The RTM, the ledgers and the `FS-122` cross-link are updated, and the manual-impact finding is
  routed.

## Verification Checklist

- [ ] `git diff` of the implementing commit touches code only in `spacesim/engine/orders.py`,
      `isr.py`, `entities.py` and `spacesim/tests/`; `access.py` is unchanged.
- [ ] Read the observe branch: the `ground_radar` table is chosen only for a `ground_radar` actor
      sensor whose effective requested mode is a radar key; the existing resolution is otherwise
      untouched.
- [ ] Independent reproduction through the HTTP API on a shipped vignette (e.g. `leo-isr-denial`
      `BLUE-RADAR`): `fence` and `dish` now execute as themselves with different gains, and no
      mode still executes as `stripmap`.
- [ ] Independent reproduction of the `auto` cue gate on a fixture other than the tests'.
- [ ] Tests 1–9 exist and pass; the Implementation Summary records which were seen failing first.
- [ ] Pre-existing tests are unmodified.
- [ ] `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass.
- [ ] The RTM `FR-1610`/`FR-1630`/`FR-1640` rows cite `IP-1222`.
- [ ] The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header
      agree on status.

## Dependencies

- **Packages:** `IP-1220` (`VERIFIED`, `VR-1220`) and `IP-1221` (`VERIFIED`, `VR-1221`). Both are
  `VERIFIED`, so this package is `READY`.
- **Spec/requirement:** `FS-122` v1.1 and `FR-1610`/`FR-1630`/`FR-1640`, all landed. No spec change
  is needed: FS-122 already describes the sensor-declared beam mode and the cue rejection; this
  package makes the code match it.
- **Authorization:** granted by the project owner 2026-10-11 (MSTR-006 §3) through the standing
  pre-authorization of this iteration's packages.
- **Parallelism:** no ordering constraint with any other open package. `IP-1160` (`BLOCKED`,
  unauthorized) also edits `orders.py` validation, in the role-scoped command path, not the
  observe branch; whichever lands second rebases.

## Risks

- **Silent behaviour change in shipped exercises.** Design Decision 1 keeps a radar with no radar
  mode on today's path. Test 1's no-mode case and Test 9 guard it, and the playbook suite
  (`test_vignette_tutorials.py`) covers shipped flows.
- **Gain above 1.** `dish`'s gain factor is 1.6, so a `dish` observation can carry a gain above 1.
  This already happens for `isr_sar` `spotlight` (1.8) and `sda` `fine` (1.8), so custody already
  handles it; no new clamp is introduced.
- **Import cycle (Design Decision 3).** None today. If a later change makes `isr.py` import
  `entities.py`, move the validator's key lookup into a function-local import.
- **Modelling choice (Design Decision 5).** Treating `LEO_SSO` as the `LEO` band is a reading of
  "altitude band", recorded here for `04` to revisit. It only affects sensors that declare an
  affinity, and none is shipped.
- **`FR-1610`'s "detects more transiting objects".** The fence's wider swath changes the gain and
  the recorded footprint, not the number of access windows, because `FR-1610`'s Postcondition
  keeps the access predicate unchanged. This is the same scope `IP-1220` chose; it is not widened
  here.

## Rollback Considerations

Reverting the implementing commit restores the `IP-1220` behaviour: radar modes unreachable,
`auto` bypassing the cue gate, affinity untyped. No shipped vignette declares any affected field,
so no content changes. There are no `SavedSession`, persisted-format, API or UI changes. A save
made while the package was live replays identically after rollback, because the resolved beam mode
and gain are stored in the scheduled event payload. A user vignette that declares a radar
`beam_mode` would still load after rollback (the field already exists) but the mode would again
be ignored.
