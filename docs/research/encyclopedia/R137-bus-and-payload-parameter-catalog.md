# R137 — Bus and Payload Configuration Parameter Catalog

> **Document ID:** R137
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R109](R109-sensor-operations.md), [R110](R110-communications.md), [R111](R111-power-and-thermal-operations.md), [R112](R112-propulsion-and-maneuver-planning.md), [R113](R113-attitude-determination-and-control.md), [R114](R114-command-and-data-handling.md), [R115](R115-electronic-warfare-in-space-operations.md), [R116](R116-cyber-operations-against-space-systems.md), [R118](R118-space-surveillance-networks.md), [R121](R121-telemetry-logging-and-attack-signatures.md), [R129](R129-sigint-collection-and-geolocation-accuracy.md), [R134](R134-pnt-warfare-and-navigation-denial-operations.md)
> **Referenced By:** `docs/pipeline/backlog.md` `BL-0052` (Vignette Creator)
> **Produces:** a completeness index for [`engine/entities.py`](../../../spacesim/engine/entities.py) (`Asset`/`AssetResources`/`GroundSite`/`Sensor`), [`engine/bus.py`](../../../spacesim/engine/bus.py) (`BusState`/`PayloadState` and their sub-states), [`engine/isr.py`](../../../spacesim/engine/isr.py), [`engine/jam.py`](../../../spacesim/engine/jam.py), [`engine/cyber.py`](../../../spacesim/engine/cyber.py), [`engine/sigint.py`](../../../spacesim/engine/sigint.py), [`engine/engage.py`](../../../spacesim/engine/engage.py)
> **Feature Mapping:** the forthcoming Vignette Creator Feature Specification (`BL-0052`), FS-105 (Spacecraft Operations)
> **Related Topics:** every topic in Dependencies above; [R101](R101-orbital-mechanics-for-operations.md) (orbital-element parameters, out of this catalog's scope — see §2)
> **Last Reviewed:** 2026-07-05
> **Primary Sources Consulted:** 0 (this topic cites no external sources of its own — see §2)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`BL-0052` (the Vignette Creator, a forthcoming White-Cell authoring feature) needs a definitive
answer to "what configuration parameters exist for a bus subsystem or payload type, and where is
each one's realistic behavior/range already documented?" before it can build typed per-payload-type
and per-bus-subsystem authoring sub-schemas without missing a field or duplicating existing
research. This topic exists to answer exactly that question, once, in one place — it is a
**completeness/navigation index, not a characterization document**: every row below points to the
topic that already defines what a parameter means and what values are realistic; this topic adds
no new numbers of its own beyond what is needed to state which field exists.

## 2. Scope

Covers: every field on `Asset`/`AssetResources`/`GroundSite`/`Sensor` (`engine/entities.py`), every
field on `BusState`'s six sub-states and `PayloadState` (`engine/bus.py`), the beam-mode/band/vector
databases that parameterize payload behavior at task/effect time (`isr.py`/`jam.py`/`cyber.py`/
`sigint.py`/`engage.py`). Does **not** cover: orbital elements themselves (`OrbitState`,
[R101](R101-orbital-mechanics-for-operations.md)'s territory — an orbit is not a "bus/payload
configuration parameter" in the sense this catalog means); ROE/vignette-level `Parameter`s (content
schema, not engine state); the *characterization* (behavior, realistic ranges, real-world grounding)
of any parameter listed here — that is exclusively the cited topic's job, and this document does
not restate it.

## 3. Concepts

### 3.1 Asset-level fields (`entities.py`)

| Parameter | Type / notes | Characterized in |
|---|---|---|
| `owner` | `blue`\|`red`\|`neutral` | Session/cell model — not an R1xx topic (fog-of-war boundary, `CLAUDE.md`) |
| `kind` | free-form string (`satellite`\|`ground_station`\|`sensor`\|`jammer`\|`interceptor`\|`directed_energy`\|…) | [R115](R115-electronic-warfare-in-space-operations.md) (jammer), [R117](R117-directed-energy-and-kinetic-effects.md) (interceptor/DE) |
| `orbit` | `OrbitState`, optional | [R101](R101-orbital-mechanics-for-operations.md) — out of this catalog's own scope (§2) |
| `location` | `GeoPoint`, optional | [R107](R107-ground-segment-operations.md) (ground siting) |
| `elevation_mask_deg` | float, default 5.0 | [R107](R107-ground-segment-operations.md) §3 (siting subsection, this session) |
| `resources.delta_v_ms` | float, default 0.0 | [R112](R112-propulsion-and-maneuver-planning.md) §3 (Δv-budget-by-class subsection, this session) |
| `resources.power_w` | float, default 0.0 — **dead field, never read** | [R111](R111-power-and-thermal-operations.md) §3/§5 (dead-field note + power-budget-by-class subsection, this session) |
| `resources.ammo` | int, default 0 | [R117](R117-directed-energy-and-kinetic-effects.md) (interceptor/kinetic effector consumption) |
| `health` | `nominal`\|`degraded`\|`destroyed` | [R107](R107-ground-segment-operations.md) (site exclusion), [R117](R117-directed-energy-and-kinetic-effects.md) (kinetic/DE damage) |
| `hardening` | float 0..1, passive-defense factor | **Not yet characterized by any R1xx topic** — a candidate gap (see §5) |
| `cyber_posture` | `low`\|`medium`\|`high` | [R116](R116-cyber-operations-against-space-systems.md) (`POSTURE_FACTORS`) |
| `cyber_vulnerabilities` | `list[{vector, patchable, patched}]` | [R116](R116-cyber-operations-against-space-systems.md), [R122](R122-safe-mode-recovery.md) (recovery-chain gate) |
| `bus_state` | `Optional[BusState]` | §3.3 below |
| `payload_state` | `Optional[PayloadState]` | §3.4 below |
| `group` | `Optional[str]`, constellation identifier | [R108](R108-constellation-operations.md) |
| `civilian` | bool | `docs/FUTURE-WORK.md` §10.D.16 — not yet R1xx-characterized (political-cost consequence unmodeled) |
| `isl_capable` / `isl_peers` | bool / `list[str]` | [R103](R103-satellite-command-and-control.md) (C2 chain, ISL relay) |
| `stored_program` | bool, default true | [R103](R103-satellite-command-and-control.md), [R114](R114-command-and-data-handling.md) |
| `threat_warning` | bool, informational posture | `docs/architecture/ADS-3500-role-scoped-command-enforcement.md` §3 (role-scope classification — bus-scope), no R1xx characterization (informational-only field) |
| `mask_table` | `list[dict]`, per-azimuth horizon mask | [R107](R107-ground-segment-operations.md) §5 |

### 3.2 `GroundSite` / `Sensor` fields

| Parameter | Type / notes | Characterized in |
|---|---|---|
| `GroundSite.location`/`elevation_mask_deg`/`mask_table` | same fields as Asset §3.1 | [R107](R107-ground-segment-operations.md) |
| `Sensor.kind` | `ground_radar`\|`ground_optical`\|`space_based` | [R109](R109-sensor-operations.md) §3 (access-predicate split) |
| `Sensor.needs_lighting` | bool | [R109](R109-sensor-operations.md) (twilight/lighting gate) |
| `Sensor.max_range_m` | `Optional[float]`, `None` = unlimited | [R109](R109-sensor-operations.md) (geometry-only access) |
| `Sensor.network` | bool, SSN membership | [R118](R118-space-surveillance-networks.md) |

### 3.3 Bus subsystem fields (`bus.py`, `BusState`'s six sub-states)

| Sub-state | Parameter | Type / notes | Characterized in |
|---|---|---|---|
| `PowerState` | `battery_soc`, `in_eclipse`, `status`, `charge_rate_per_s`, `drain_rate_per_s`, `loads_shed`, `charge_mode` | float/bool/enum | [R111](R111-power-and-thermal-operations.md) (DoD model, size-class power-budget subsection this session) |
| `AttitudeState` | `pointing_ok`, `mode`, `status` | bool/enum | [R113](R113-attitude-determination-and-control.md) |
| `ThermalState` | `status`, `mode`, `heater_on`, `temp_c`, `temp_low_c`, `temp_high_c`, `heater_watts`, `radiator_capacity_w`, `survival_trigger_minutes` | float/bool/enum — **declared but not yet integrated by `advance_bus`** (`temp_c` static) | [R111](R111-power-and-thermal-operations.md) §5 (explicit inert-placeholder note) |
| `PropulsionState` | `propellant_frac`, `status` | float 0..1/enum — **decoupled from `resources.delta_v_ms`** | [R111](R111-power-and-thermal-operations.md) §3, [R112](R112-propulsion-and-maneuver-planning.md) §3 (both cite the same decoupling) |
| `CdhState` | `storage_frac`, `fsw_mode`, `status` | float 0..1/enum | [R114](R114-command-and-data-handling.md) |
| `CommsState` | `uplink_lock`, `downlink_lock`, `status`, `isl_enabled`, `data_rate_kbps`, `freq_hopping`, `antenna_mode` | bool/enum/int(64-16384 clamp)/bool/str | [R110](R110-communications.md) (bandwidth-by-class subsection this session), [R115](R115-electronic-warfare-in-space-operations.md) (`freq_hopping` anti-jam) |
| `SafeModeState` | `active`, `entered_at`, `cause`, `defender_confirmed`, `defender_diagnosis`, `passes_used`, `blocked_reason`, `current_step`, `steps_done` | bool/int/enum/… | [R122](R122-safe-mode-recovery.md) |
| `BusState.mode` (top-level) | `nominal`\|`safe_mode` | enum | [R122](R122-safe-mode-recovery.md) |

### 3.4 Payload fields (`PayloadState`, generic across all 8 types)

| Parameter | Type / notes | Characterized in |
|---|---|---|
| `type` | `satcom`\|`isr_eo`\|`isr_sar`\|`sigint`\|`sda`\|`weather`\|`pnt`\|`mw` (string, not a closed enum in code) | this catalog's own §3.5 per-type table |
| `health` | `Status` enum | [R109](R109-sensor-operations.md) generally |
| `collecting` / `collect_rate_per_s` | bool / float | [R109](R109-sensor-operations.md) (ISR storage-fill coupling) |
| `interference_level` / `interference_mitigation` | float 0..1 | [R110](R110-communications.md) (SATCOM jam-experience/mitigation) |
| `last_effect_assessment` | `unknown`\|`likely`\|`confirmed` | space-control payload type — not yet R1xx-characterized (candidate gap, §5) |
| `hardened` | bool (`def.harden`) | `ADS-3500` §3 (payload-scope classification); no R1xx behavioral characterization beyond the effect-susceptibility comment in code |
| `mode` | str, meaning varies by payload `type` (ISR wide/narrow/standby/nominal; PNT reuses `integrity_mode` instead) | [R109](R109-sensor-operations.md) (ISR `isr.set_mode`) |
| `integrity_mode` | `standard`\|`protected`\|`degraded` | [R134](R134-pnt-warfare-and-navigation-denial-operations.md) (baseline-accuracy subsection this session) |
| `evasion_active` | bool (`def.maneuver_evade`) | [R112](R112-propulsion-and-maneuver-planning.md) (shares the Δv-resource model) |
| `deception_active` | bool (`def.set_deception_mode`) | cited in code to the USSF Space Warfighting Framework passive-measure taxonomy; no dedicated R1xx topic yet (candidate gap, §5) |
| `shutter_closed` | bool (`isr.shutter_sensor`) | [R109](R109-sensor-operations.md) generally (optics-protection concept, not separately characterized) |
| `detail` | `dict`, free-form per-type bag (e.g. `sda_mode`, `track_target`, `beam`, `mw_stare_areas`) | per-type, §3.5 |

### 3.5 Per-payload-type parameterization (`isr.py` `BEAM_MODES` + related)

| Payload type | Mode-level parameters | Characterized in |
|---|---|---|
| `isr_eo` | `swath_km`, `resolution_m`, `power_factor`, `duty_cycle`, `gain_factor` per mode (`wide_area`/`stripmap`/`spotlight`/`scan`) | [R109](R109-sensor-operations.md) §3 |
| `isr_sar` | same five fields per mode (`wide_area`/`stripmap`/`fine`/`spotlight`/`polarimetric`) | [R109](R109-sensor-operations.md) §3 |
| `sda` | same five fields per mode (`wide_area`/`nominal`/`fine`) | [R109](R109-sensor-operations.md) §3 |
| `satcom` | `interference_level`/`interference_mitigation` (PayloadState, §3.4) + `CommsState.data_rate_kbps` (§3.3, bus-level) | [R110](R110-communications.md) |
| `sigint` | `BANDS` (frequency/atmos-loss), `MODES` (scan/track/geolocate, dwell defaults) — `engine/sigint.py`, not `isr.py` | [R129](R129-sigint-collection-and-geolocation-accuracy.md) |
| `pnt` | `integrity_mode` (§3.4) | [R134](R134-pnt-warfare-and-navigation-denial-operations.md) |
| `weather` | **no `BEAM_MODES` entry — falls back to generic `isr_eo` numbers** | **Not yet characterized/parameterized** — [R109](R109-sensor-operations.md) §3 names this gap explicitly (this session) |
| `mw` (missile warning) | **no `BEAM_MODES` entry — same fallback** | **Not yet characterized/parameterized** — [R109](R109-sensor-operations.md) §3 names this gap explicitly (this session) |

### 3.6 Effect/weapon-modality databases (selected at order-issue time, not persistent asset state)

These parameterize a *command's* effect rather than a persistent bus/payload field, but are still
configuration a White Cell/Red-Blue operator selects among, and so are in scope for completeness:

| Database | Location | Parameters | Characterized in |
|---|---|---|---|
| `MODULATIONS` | `engine/jam.py` | barrage/spot/sweep/deceptive — power/radius/bandwidth-overlap terms | [R115](R115-electronic-warfare-in-space-operations.md) |
| `VECTORS` / `PAYLOADS` / `POSTURE_FACTORS` | `engine/cyber.py` | access-vector × payload success-probability terms, posture multiplier | [R116](R116-cyber-operations-against-space-systems.md) |
| `BANDS` / `MODES` | `engine/sigint.py` | frequency band × collection mode (scan/track/geolocate) | [R129](R129-sigint-collection-and-geolocation-accuracy.md) |
| `INTERCEPTORS` | `engine/engage.py` | interceptor class × base Pₖ/closing-geometry terms | [R117](R117-directed-energy-and-kinetic-effects.md) |
| Attack-signature model | `engine/telemetry.py` | per-effect signature (jam→RX power, cyber→FSW errors, DE→SNR, kinetic→LOS) | [R121](R121-telemetry-logging-and-attack-signatures.md) |

## 4. Operational Context

A vignette author (or the eventual Vignette Creator UI) configuring a new asset needs the same
completeness guarantee a real systems engineer's interface-control document provides: every
parameter that affects behavior is somewhere on a form, and every form field maps to a real,
documented effect — no field that looks configurable but is actually inert (the `power_w` and
`propellant_frac` dead/decoupled fields this catalog flags explicitly), and no engine-modeled
behavior with no field to configure it at all (the `weather`/`mw` `BEAM_MODES` gap). This catalog
exists so that gap-finding is a lookup against one table, not a fresh code audit every time a new
authoring surface is planned.

## 5. Implementation Guidance

- **When adding a new bus/payload field to `entities.py`/`bus.py`, add a row here** in the same
  pull request that adds it, pointing to whichever topic characterizes its realistic
  behavior/range — a field with no catalog row is a field a future authoring surface will miss.
- **When a field's *characterization* changes (a new realistic-range subsection, a new
  Implementation Guidance bullet), this catalog's own row text does not need to change** — it only
  ever names *which* topic to read, never restates what that topic says; keep it that way, or this
  document will drift into a second, competing characterization surface.
- **Four candidate gaps this pass surfaced, beyond the already-flagged `weather`/`mw` BEAM_MODES
  gap:** `Asset.hardening` (passive-defense factor, 0..1, no topic characterizes what a realistic
  value is or what it actually does numerically beyond "lowers safe-mode susceptibility"),
  `PayloadState.last_effect_assessment` (space-control payload type, effectively unused/uncharacterized
  in current vignettes), `PayloadState.deception_active`'s full behavioral consequence (code comment
  cites USSF SWF passive measure #2 but no R1xx topic elaborates the custody/attribution
  consequence the comment itself says is "left as a separate change"), and `Asset.civilian`'s
  political-cost consequence (declared in `FUTURE-WORK.md`, not yet modeled or characterized). None
  block `BL-0052`'s typed sub-schemas (none are fields that pass currently exposes for authoring),
  but each is a real, named gap for whoever eventually wires them — flag as future
  `02-research-ow-orbital-mechanics` maintenance work, not silently left implicit.
- **Do not use this catalog as a substitute for reading the cited topic.** A future Feature
  Specification citing "R137" alone for a behavioral claim has cited the wrong document — always
  cite the characterizing topic (e.g. R110 for SATCOM bandwidth), with R137 only as the completeness
  cross-check that nothing was missed.

## 6. Feature Mapping

The forthcoming Vignette Creator Feature Specification (`docs/pipeline/backlog.md` `BL-0052`) is
the direct consumer: every typed per-payload-type and per-bus-subsystem parameter sub-schema it
specifies should be checked against this catalog for completeness before that spec is considered
done. FS-105 (Spacecraft Operations) is the existing home of the underlying fields' runtime
behavior.

## 7. Related Topics

[R109](R109-sensor-operations.md), [R110](R110-communications.md), [R111](R111-power-and-thermal-operations.md),
[R112](R112-propulsion-and-maneuver-planning.md), [R113](R113-attitude-determination-and-control.md),
[R114](R114-command-and-data-handling.md), [R115](R115-electronic-warfare-in-space-operations.md),
[R116](R116-cyber-operations-against-space-systems.md), [R118](R118-space-surveillance-networks.md),
[R121](R121-telemetry-logging-and-attack-signatures.md), [R129](R129-sigint-collection-and-geolocation-accuracy.md),
[R134](R134-pnt-warfare-and-navigation-denial-operations.md) — every topic this catalog cross-references above.
