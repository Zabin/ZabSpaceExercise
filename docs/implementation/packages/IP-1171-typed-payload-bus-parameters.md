# IP-1171 — Typed Payload & Bus Parameter Domain Model

> **Package ID:** IP-1171
> **Version:** 1.0
> **Status:** 🔵 COMPLETE *(implemented 2026-07-05 by `08-code-implementation` — [IP-1170](IP-1170-isr-beam-mode-coverage.md)
> reached `VERIFIED` first (2026-07-05, `VR-1170`), so all 8 typed sub-models, including
> `weather`/`mw`, were built with full engine-wiring from the start, no inert placeholder needed.
> 8 new tests in `spacesim/tests/test_typed_payload_params.py`, full suite 594 passed/3 skipped
> (up from 586/3, +8), both permanent gates green. Awaiting `09-package-verification`.)*
> **Dependencies:** [FS-117](../../features/FS-117-vignette-creator.md) v1.1 (`FR-5170`,
> `FR-5180`), [ADS-5100B](../../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md) §3.1,
> [IP-1170](IP-1170-isr-beam-mode-coverage.md) (weather/mw `BEAM_MODES` — not `VERIFIED` yet),
> [FS-105](../../features/FS-105-spacecraft-operations.md) / [IP-1050](IP-1050-spacecraft-operations-bus-payload.md)
> (`PayloadState`/`BusState`/`AssetResources` this package extends — `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** typed `PayloadState` sub-models per payload type, consumed by
> [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s parameter-authoring forms
> **Feature Reference:** [FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md)
> (`FR-5170`/`FR-5180` slice)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/bus.py`](../../../spacesim/engine/bus.py),
> [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`docs/research/encyclopedia/R109-sensor-operations.md`](../../research/encyclopedia/R109-sensor-operations.md),
> [`R110`](../../research/encyclopedia/R110-communications.md),
> [`R111`](../../research/encyclopedia/R111-power-and-thermal-operations.md),
> [`R112`](../../research/encyclopedia/R112-propulsion-and-maneuver-planning.md),
> [`R134`](../../research/encyclopedia/R134-pnt-warfare-and-navigation-denial-operations.md),
> [`R137`](../../research/encyclopedia/R137-bus-and-payload-parameter-catalog.md)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package — `FEAT-5100` (which `FS-117` consolidates) is 0% built. The bridging
mechanism below (typed fields directly on the engine's `PayloadState`, not a UI-side conversion to
the existing generic `detail: dict`) was resolved by the project owner during this same
`07-implementation-planning` pass (`AskUserQuestion`, the same class of in-pass resolution
`IP-2010`'s run #4 amendment used), closing `ADS-5100B` Open Question 1 / `FS-117` Open Question 4.*

## Package ID

IP-1171

## Title

Typed Payload & Bus Parameter Domain Model

## Objective

Replace the generic, untyped parameter surface for payload configuration with named, validated,
per-payload-type sub-models on `PayloadState`, and confirm the bus power/propulsion parameters
`FR-5180` requires (`charge_rate_per_s`/`drain_rate_per_s`/`delta_v_ms`) are exposed to the
authoring surface as the already-live fields they are — never `AssetResources.power_w`.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md) (`FR-5170`/`FR-5180` slice)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-5170 | Typed per-payload-type parameter sub-schemas | Adds one new typed pydantic sub-model per payload type (`satcom`/`isr_eo`/`isr_sar`/`sigint`/`sda`/`weather`/`pnt`/`mw`) as an optional field on `PayloadState`, populated according to `PayloadState.type`; each sub-model's fields are grounded in `R109`/`R110`/`R134`/`R137`, replacing the untyped `detail: dict` for these purposes (which remains for any genuinely free-form extension). `weather`/`mw` sub-models are wired to [IP-1170](IP-1170-isr-beam-mode-coverage.md)'s new `BEAM_MODES` entries; if that package is not yet `VERIFIED`, this package's `weather`/`mw` sub-models exist but have no observable engine effect, per `FR-5170`'s own Postcondition. |
| FR-5180 | Typed bus parameter sub-schemas (power, propulsion) | Confirms and documents (no new engine field needed — checked directly against `bus.py`/`entities.py`) that the authoring surface for bus power exposes `PowerState.charge_rate_per_s`/`drain_rate_per_s` and propulsion exposes `AssetResources.delta_v_ms`; adds the vignette-schema/loader plumbing so a vignette's per-asset override for these fields lands on the correct live field, never `AssetResources.power_w`. |

## Architecture Components

- **C1 Simulation Engine** — `engine/bus.py` gains 8 new typed sub-models (one per payload type)
  and a corresponding optional field per type on `PayloadState` (e.g.
  `satcom_params: Optional[SatcomParams] = None`), populated when `PayloadState.type` matches. No
  change to `BusState`/`PowerState`/`PropulsionState` — `FR-5180`'s fields already exist.
- **C5 Content & Data** — `content/vignette.py`'s asset-spec dicts (`blue_forces`/`red_forces`/
  `neutral_forces` entries) gain the ability to set the new typed sub-model fields and the existing
  `PowerState.charge_rate_per_s`/`drain_rate_per_s`/`AssetResources.delta_v_ms` fields directly at
  `build_world()` time (today, `Asset.model_validate(data)` already accepts nested dict data for any
  field pydantic knows about — this package's own verification task must confirm whether any
  additional loader logic is needed beyond what `model_validate` already provides for granular
  power/propulsion overrides at the per-asset level, since `resources`/`bus_state` are already
  `Asset` fields).

## Interfaces

None — this is a Domain Model/content-schema extension, consistent with `FR-5170`/`FR-5180`'s own
Related Interfaces field ("none directly"). No new interface; the existing vignette-loading path
(`Asset.model_validate`) is extended with more fields to validate, not a new call surface.

## Files to Create

None proposed — new sub-models live inside the existing `bus.py` module (mirrors `IP-1130`/
`IP-1151`'s restraint principle: extend, don't create a parallel schema file).

## Files to Modify

- `spacesim/engine/bus.py` *(proposed)* — add 8 new `BaseModel` sub-classes, one per payload type:
  - `SatcomParams` — bandwidth/data-rate fields grounded in `R110` (e.g. `bandwidth_class`,
    `data_rate_kbps_max`, matching `R110`'s realistic class-based ranges).
  - `IsrEoParams`/`IsrSarParams` — resolution/swath/effective-range fields grounded in `R109`,
    consistent with (not duplicating) `engine/isr.py`'s `BEAM_MODES` — these are *authored defaults*
    an asset carries, distinct from the per-beam-mode runtime table.
  - `SigintParams` — band/mode fields grounded in `R109`'s SIGINT-adjacent content and
    `engine/sigint.py`'s existing `geolocation_error_km()` inputs.
  - `SdaParams` — fields consistent with `engine/isr.py`'s `"sda"` `BEAM_MODES` entry.
  - `WeatherParams`/`MwParams` — fields grounded in `R109`'s GOES-R/SBIRS content, consuming
    [IP-1170](IP-1170-isr-beam-mode-coverage.md)'s new `BEAM_MODES["weather"]`/`["mw"]` entries.
  - `PntParams` — accuracy-adjacent fields grounded in `R134`'s GPS SPS ~9m/95% baseline.
  - Each `PayloadState` gains one new `Optional[...] = None` field per sub-model above (named after
    the payload type, e.g. `satcom: Optional[SatcomParams] = None`), populated only when
    `PayloadState.type` matches that type — an asset's non-matching sub-model fields stay `None`.
- `spacesim/engine/entities.py` *(no change expected)* — `AssetResources.delta_v_ms` and
  `bus.py`'s `PowerState.charge_rate_per_s`/`drain_rate_per_s` are already live fields; this
  package's own verification task confirms `Asset.model_validate()` already accepts nested
  per-asset overrides for them via the existing `resources`/`bus_state` fields with no change
  needed, or documents precisely what minimal loader change is needed if not.
- `spacesim/content/vignette.py` *(proposed, if the verification task above finds a gap)* — any
  small loader-side normalization needed so a vignette YAML author can set these fields cleanly
  (e.g. a helper in `build_world()`'s asset-construction loop), scoped only if the direct
  `model_validate` path proves insufficient.

**Explicitly out of scope for this package:** the Creator's UI forms presenting these typed fields
— that is [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s concern. This package only builds
the Domain Model the UI will be a thin client over.

## Implementation Tasks

**Complete (2026-07-05, `08-code-implementation`).** [IP-1170](IP-1170-isr-beam-mode-coverage.md)
had already reached `VERIFIED` before this package started, so the proposed sequence's "inert
until IP-1170 ships" branch never applied — all 8 sub-models, including `weather`/`mw`, were built
with full engine-wiring from the start:

1. ✅ Confirmed [IP-1170](IP-1170-isr-beam-mode-coverage.md) is `VERIFIED` (`VR-1170`) before
   starting — `weather`/`mw` sub-models mirror real `BEAM_MODES["weather"]`/`["mw"]` values, no
   inert-placeholder disclosure needed.
2. ✅ Wrote 8 failing tests first in `spacesim/tests/test_typed_payload_params.py` (test-first,
   per `CLAUDE.md`), confirmed all 8 failed (2 additional tests in the same file — the bus
   power/propulsion override and the 19-vignette regression check — passed immediately, since
   they exercise pre-existing `Asset.model_validate`/`build_world` behavior needing no change).
3. ✅ Added the 8 sub-models (`SatcomParams`/`IsrEoParams`/`IsrSarParams`/`SigintParams`/
   `SdaParams`/`WeatherParams`/`PntParams`/`MwParams`) and their `Optional[...] = None`
   `PayloadState` fields, auto-populated via a `model_validator(mode="after")` keyed on
   `PayloadState.type`. Every field traces to a cited source: `SatcomParams` to `R110`'s
   bandwidth-by-class table; `IsrEoParams`/`IsrSarParams`/`SdaParams`/`WeatherParams`/`MwParams`
   to their own type's already-`R109`-grounded `engine/isr.py` `BEAM_MODES` `_DEFAULT_MODE` entry
   (no second number invented — mirrored, not re-derived); `SigintParams` to `engine/sigint.py`'s
   own `BANDS`/`MODES` defaults (re-attributed to `R129`, not `R109`, per `R137` §3.5 — see
   Outstanding Issues); `PntParams.accuracy_m` to `R134`'s GPS SPS ≤9m/95% baseline.
4. ✅ Confirmed (no addition needed) `Asset.model_validate()` already accepts nested per-asset
   overrides for `resources.delta_v_ms`/`bus_state.power.charge_rate_per_s`/`drain_rate_per_s` via
   plain pydantic nested-model coercion — `content/vignette.py` untouched.
5. ✅ Full suite re-run: 594 passed/3 skipped (up from 586/3, +8 — the exact new tests), zero
   regressions; `test_typed_payload_params.py`'s own regression test confirms all 19 currently
   shipped vignettes load/build unchanged.

## Tests to Add

- `spacesim/tests/test_typed_payload_params.py` *(new)* — 8 tests, all passing:
  `test_isr_eo_asset_gets_isr_eo_params_only`, `test_satcom_asset_gets_bandwidth_params`,
  `test_weather_and_mw_sub_models_mirror_ip1170_beam_modes`, `test_pnt_asset_gets_baseline_accuracy`,
  `test_explicit_sub_model_override_is_respected_not_overwritten`,
  `test_space_control_type_gets_no_typed_sub_model`,
  `test_bus_power_and_propulsion_override_reaches_live_fields_not_dead_power_w`,
  `test_all_currently_shipped_vignettes_load_and_build_unchanged`.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — this package's row updated to `COMPLETE`.
- `docs/features/FS-117-vignette-creator.md`'s `Referenced By` metadata — stale "(all `BLOCKED`,
  not authorized)" parenthetical corrected to reflect current per-package status.
- `docs/design/04-data-model.md` §6 — gained the 8 new `PayloadState` sub-model entries, mirroring
  `IP-1151`'s `RoleRequirement` precedent.
- `CLAUDE.md`'s Code Map — `engine/bus.py`'s entry updated with the 8 typed sub-models.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-05, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #45).
- [x] All 8 typed payload sub-models exist on `PayloadState`, each `Optional`, each populated only
  when `PayloadState.type` matches.
- [x] Every sub-model field traces to a specific `R109`/`R110`/`R129`/`R134`/`R137` citation —
  none invented (`SigintParams` traces to `R129`, not `R109`, per `R137` §3.5 — see Outstanding
  Issues for the package's own citation-set imprecision this corrects).
- [x] Bus power/propulsion authoring reaches `PowerState.charge_rate_per_s`/`drain_rate_per_s`/
  `AssetResources.delta_v_ms`; `AssetResources.power_w` is never written by this path (confirmed
  by direct grep of `engine/bus.py` — zero hits — and a dedicated round-trip test).
- [x] `weather`/`mw` sub-models' engine-effectiveness is honestly gated on
  [IP-1170](IP-1170-isr-beam-mode-coverage.md) reaching `VERIFIED` — it already had, before this
  package started, so both mirror real `BEAM_MODES` values from the start (confirmed by a
  dedicated test asserting parity with `BEAM_MODES["weather"]["conus"]`/`["mw"]["scan"]`).
- [x] All 19 currently shipped vignettes load and build unchanged.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `spacesim/tests/test_typed_payload_params.py` exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (pure Domain Model
  extension, no RNG/wall-clock/mutation-order change).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Full existing suite re-run with zero regressions.
- [ ] Independently confirm (not merely re-cite) that `weather`/`mw` sub-model values actually reach
  `engine/isr.py`'s beam-parameter resolution once [IP-1170](IP-1170-isr-beam-mode-coverage.md) is
  `VERIFIED` — a live-code check, not a documentation cross-reference.
- [ ] Independently confirm `AssetResources.power_w` is not written anywhere by this package's new
  code paths (grep + read, per this project's own established anti-drift discipline).

## Dependencies

- **Upstream:** [FS-117](../../features/FS-117-vignette-creator.md) v1.1 (no open design questions
  blocking this slice), [ADS-5100B](../../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md)
  §3.1 (binding grounding for the bridging-mechanism decision), [IP-1170](IP-1170-isr-beam-mode-coverage.md)
  (weather/mw engine parameterization — not yet `VERIFIED`), [IP-1050](IP-1050-spacecraft-operations-bus-payload.md)
  (`PayloadState`/`BusState`/`AssetResources` this package extends — `VERIFIED`).
- **Downstream:** [IP-1174](IP-1174-vignette-creator-ui-surfaces.md) — the Creator's parameter forms
  present these typed sub-models; cannot be meaningfully built until this package's schema exists.
- **Build-sequencing:** After [IP-1170](IP-1170-isr-beam-mode-coverage.md); independent of
  [IP-1172](IP-1172-per-cell-roe-enforcement.md) and [IP-1173](IP-1173-vignette-creator-draft-session.md)
  (different seams, no shared file).

## Risks

- **`weather`/`mw` sub-schemas are a plausible-but-inert field until `IP-1170` ships** — the same
  risk `FS-117` itself already discloses; this package's Definition of Done is written to make that
  gating explicit rather than silently claiming full coverage.
- **Field-level research gaps are possible** — `R137`'s own §5 already flags four smaller candidate
  gaps (`Asset.hardening`'s numeric effect, `PayloadState.last_effect_assessment`'s characterization,
  `deception_active`'s custody consequence, `Asset.civilian`'s political cost) that are explicitly
  **not** part of this package's typed-parameter scope (`BL-0054`, Low, deferred) — if
  `08-code-implementation` finds it needs one of these four to complete a sub-model field, that is
  a research gap to flag, not license to invent a number.
- **Two-package dependency (`IP-1170` + this package) for one Feature's two payload types** adds a
  small sequencing burden — accepted because the alternative (folding `IP-1170` into this package)
  would mix a pure `engine/isr.py` data fix with a genuine Domain Model extension, a different seam.

### Outstanding Issues (Implementation Summary)

- **`SigintParams`'s own field-grounding citation, as this package's `Files to Modify` text
  originally stated it, said "`R109`'s SIGINT-adjacent content" — checked against `R137` §3.5
  (the completeness index both this package and `R109` itself defer to) during implementation and
  found imprecise: `R137` attributes SIGINT's actual characterization to `R129`, not `R109`.**
  Not a functional defect (`SigintParams.default_band`/`default_mode` mirror `engine/sigint.py`'s
  own already-correct `BANDS`/`MODES` defaults either way) — corrected in this package's own
  Definition of Done and the RTM `FR-5170` Research column (`R129` added) rather than silently
  matched to the imprecise original wording.

## Rollback Considerations

Every new field is `Optional`, defaulting to `None` — reverting the 8 sub-models and their
`PayloadState` fields fully restores today's generic-`detail`-dict-only behavior with no data
migration concern for any of the 19 currently shipped vignettes (none populate the new fields). If
the vignette-loader gained any new normalization logic (task 4), that logic is additive to
`build_world()`'s existing asset-construction loop and can be reverted independently.
