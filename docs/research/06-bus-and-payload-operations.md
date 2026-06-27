---
last_reviewed: 2026-06-12
primary_sources_consulted: 99
status: stable
---

# Satellite Bus & Payload Operations — How Operators Actually Fly Satellites

[← Research index](INDEX.md) · [↑ Docs index](../INDEX.md) · methodology: [`10-sources-and-methodology.md`](10-sources-and-methodology.md)

This file grounds the simulator's bus-and-payload model in primary engineering and
mission-operations doctrine so the operator experience matches the texture a CAF space
operator sees on the job. The order matches the operator's own mental model: §1 the
six core bus subsystems they fly the bird with, §2 the state-of-health discipline plus
the safe-mode FDIR fallback that gates everything else, §3 the pre-pass / in-pass /
post-pass loop that organises every shift, §4 the power calibration that sources the
June 2026 TT&C audit recalibration, §5–§7 the per-mission payload-ops verbs (SATCOM,
ISR, then the combined SIGINT/SDA/Space-control/PNT/MW/Weather treatment), §8 the
real operator-console software the simulator's UI grammar is copied from, §9 the three
named live modeling gaps the audit catalogued, and §10 the consolidated mapping back
into the engine modules and vignette content that exercise the doctrine in play. Each
subsection carries its own inline-cited primary sources at the claim site plus a
per-subsection Sources block; §10 is a pure integration pass over §1–§9 with no new
external citations. Cross-references to the rest of the corpus and to the audit doc
live in §11 at the foot of the file.

---

## 1. Core bus subsystems (EPS, ADCS, CDH, TCS, comms, propulsion)

Every operational satellite carries the same **six common bus subsystems** — electrical power (EPS), attitude determination and control (ADCS), command and data handling (CDH), thermal control (TCS), communications, and propulsion — sized differently per mission but architecturally identical from a smallsat to a strategic GEO bird. The canonical engineering reference that defines the per-subsystem sizing rules the simulator's bus model is calibrated against is **Wertz, Everett, and Puschell**, *Space Mission Engineering: The New SMAD*, 4th ed. (Microcosm Press, 2011) — the "New SMAD" that succeeded the original Larson/Wertz *Space Mission Analysis and Design* and is the standard textbook in every operational program-office and primer course ([Microcosm Press SME-SMAD listing](https://microcosmpress.com/publishing/space-mission-engineering/)). Each subsection below names a deeper-specialist reference beside Wertz/Larson for the per-subsystem physics. The engine collapses the six subsystems into the six dataclasses on [`engine/bus.py:BusState`](../../spacesim/engine/bus.py) — `PowerState`, `AttitudeState`, `CdhState`, `ThermalState`, `CommsState`, `PropulsionState` — plus a seventh `SafeModeState` that tracks the meta-subsystem covered in §2.

### 1.1 EPS — Electrical Power System

**What it does.** Generates power (solar arrays sized for end-of-life worst-case eclipse season), stores it (rechargeable Li-ion or NiH₂ battery sized for the maximum eclipse-period depth-of-discharge), regulates the bus (PDU / PCU regulating the 28 V or 100 V bus voltage), and distributes it to loads through switched feeders that can be shed under power-red conditions. The canonical specialist reference is **Patel**, *Spacecraft Power Systems* (CRC Press, 2004) — the textbook engineering treatment of solar-array sizing, battery sizing, eclipse cycle life, and end-of-life degradation ([Routledge / CRC catalog](https://www.routledge.com/Spacecraft-Power-Systems/Patel/p/book/9780849327865)), paired with [Wertz / Larson](https://microcosmpress.com/publishing/space-mission-engineering/) §11 for system-level integration.

**What operators watch.** Battery state of charge (SoC); eclipse vs. sunlit state; load shed status; charge-mode (nominal / fast / trickle); current draw vs. array output. The plan-side question is always "will SoC stay above the soft floor through the next eclipse season at this duty cycle." Engine: [`bus.py:PowerState`](../../spacesim/engine/bus.py) carries `battery_soc`, `in_eclipse`, `charge_rate_per_s`, `drain_rate_per_s`, `loads_shed`, and `charge_mode`; the soft/hard thresholds at the top of the module (`SOC_SOFT = 0.30`, `SOC_HARD = 0.15`) drive the status-light cascade. Forward-link to §4 (power-calibration subsection) for the per-mission `charge_rate_per_s` values and to [`engine/buscommands.py`](../../spacesim/engine/buscommands.py) `eps.shed_load` / `eps.restore_load` / `eps.set_charge_mode` for the operator verbs.

### 1.2 ADCS — Attitude Determination and Control

**What it does.** Determines attitude from a sensor suite (star trackers for arc-second-class precision, IMUs for short-interval rate integration, sun sensors as a coarse safe-mode reference, magnetometers in LEO) and commands attitude with a actuator stack (reaction wheels for precise pointing, magnetorquers for momentum dumping in LEO, thrusters for slews and momentum dumping at higher altitudes). Modes typically include **nadir-pointing** (Earth observation), **sun-safe** (arrays into the sun for power recovery), **inertial-hold** (astronomy / SDA), **target-track** (rendezvous, RPO, ISR slew-to-target), and **safe** (sun-pointing minimum-rate). The specialist reference is **Sidi**, *Spacecraft Dynamics and Control: A Practical Engineering Approach* (Cambridge University Press, 1997, reissued 2000) — the textbook engineering treatment of quaternion attitude representation, control-law synthesis, and per-actuator sizing ([Cambridge University Press catalog](https://www.cambridge.org/core/books/spacecraft-dynamics-and-control/F60C2D7EE9D33F2BCBAE53C5DA0F4FAB)), paired with [Wertz / Larson](https://microcosmpress.com/publishing/space-mission-engineering/) §10 for system-level sizing.

**What operators watch.** Pointing knowledge vs. requirement; reaction-wheel momentum (wheel desaturation is a recurring health task); mode transitions (a drop into safe almost always blocks mission payload); slew completion. Engine: [`bus.py:AttitudeState`](../../spacesim/engine/bus.py) carries `pointing_ok`, `mode ∈ {nominal, slew, safe}`, and `status`; the operator verbs `adcs.set_mode`, `adcs.desaturate`, and `adcs.point_payload` live in [`engine/buscommands.py`](../../spacesim/engine/buscommands.py).

### 1.3 CDH — Command and Data Handling

**What it does.** Hosts the flight software on a radiation-tolerant flight computer, decodes uplinked commands from the command receivers (validating against the spacecraft's command authentication / authority table), formats telemetry frames for the downlink chain, and manages onboard data storage (a few-GB to multi-TB solid-state recorder for ISR / SAR / SIGINT payloads). The specialist reference is **Eickhoff**, *Onboard Computers, Onboard Software and Satellite Operations: An Introduction* (Springer Aerospace Technology, 2012) — the textbook treatment of flight-software architecture, command/telemetry processing chains, and operations-friendly fault-management design ([Springer Link catalog](https://link.springer.com/book/10.1007/978-3-642-25170-2)), paired with [Wertz / Larson](https://microcosmpress.com/publishing/space-mission-engineering/) §16 for system-level CDH sizing.

**What operators watch.** Flight-software (FSW) mode (nominal vs. safe); onboard storage fill fraction (full storage blocks further ISR collect until a downlink); command receipt counters; telemetry-frame error rate. Engine: [`bus.py:CdhState`](../../spacesim/engine/bus.py) carries `fsw_mode ∈ {nominal, safe}` and `storage_frac`, with `STORAGE_SOFT = 0.85` / `STORAGE_HARD = 0.98` driving the status cascade and `can_collect()` gating further ISR storage growth; the operator verbs `cdh.dump_storage`, `cdh.clear_fault`, `cdh.reset_subsystem`, and `cdh.load_stored_program` live in [`engine/buscommands.py`](../../spacesim/engine/buscommands.py).

### 1.4 TCS — Thermal Control System

**What it does.** Holds every box on the bus inside its operational temperature limits across the full orbit-environmental swing (full sun ↔ deep eclipse ↔ payload-on heat dump). **Passive** thermal — multilayer insulation (MLI), second-surface mirror radiators, optical solar reflectors, thermal-control coatings and paints — handles the bulk of the steady-state heat balance; **active** thermal — survival heaters, operational heaters, variable-conductance heat pipes, deployable / louvered radiators — handles the transient and off-nominal cases. The canonical specialist reference is **Gilmore (ed.)**, *Spacecraft Thermal Control Handbook* (Aerospace Press / AIAA, two-volume 2nd ed., 2002, ISBN 1-884989-11-X — Vol. I *Fundamental Technologies*, Vol. II *Cryogenics*) — the textbook engineering reference for radiator sizing, heater sizing, MLI design, and orbit-thermal-environment modeling ([Aerospace Corp. publication listing](https://aerospace.org/sites/default/files/2018-05/Welch_ThermalControl.pdf)), paired with [Wertz / Larson](https://microcosmpress.com/publishing/space-mission-engineering/) §11 for system-level integration.

**What operators watch.** Bus baseplate temperature relative to the survival floor / operational ceiling; heater duty cycle; radiator margin; mode (operational vs. survival). When the temperature drops below the survival floor (or rises above the operational ceiling) for the configured trigger interval, the FSW typically forces the bus into safe mode. Engine: [`bus.py:ThermalState`](../../spacesim/engine/bus.py) carries `mode ∈ {nominal, survival, operational}`, `temp_c`, `temp_low_c` / `temp_high_c` (survival triggers), `heater_on`, `heater_watts`, `radiator_capacity_w`, and `survival_trigger_minutes`; the operator verbs `tcs.set_mode` and `tcs.set_heater` live in [`engine/buscommands.py`](../../spacesim/engine/buscommands.py).

### 1.5 Comms — Communications

**What it does.** Carries the TT&C (telemetry, tracking, and command) chain — S-band typical for civil and legacy military, X-band for some military / high-rate, Ka-band for very-high-rate — plus the mission-data downlink (often a separate higher-rate chain) and, increasingly, an inter-satellite link (ISL) for relay between birds. Subsystems include the transponders, the antenna pattern (omni for safe-mode TT&C, high-gain steerable for mission data), frequency-hopping or spread-spectrum waveforms for anti-jam, and command crypto / message authentication. The canonical specialist reference is **Maral, Bousquet, and Sun**, *Satellite Communications Systems: Systems, Techniques and Technology*, 5th ed. (Wiley, 2009) — the textbook treatment of link budgets, modulation, antenna patterns, and frequency planning ([Wiley catalog](https://www.wiley.com/en-us/Satellite+Communications+Systems%3A+Systems%2C+Techniques+and+Technology%2C+5th+Edition-p-9780470714584)), paired with **ITU-R Recommendations** on propagation ([P.681 land/maritime mobile-satellite](https://www.itu.int/rec/R-REC-P.681/en)) and on geostationary station-keeping geometry ([S.484-3](https://www.itu.int/rec/R-REC-S.484/en)), and with [Wertz / Larson](https://microcosmpress.com/publishing/space-mission-engineering/) §13 for system-level integration.

**What operators watch.** Uplink and downlink lock status; frequency-hopping state (anti-jam on?); antenna pointing mode; ISL availability; jam interference level on the receive band. Engine: [`bus.py:CommsState`](../../spacesim/engine/bus.py) carries `uplink_lock`, `downlink_lock`, `isl_enabled`, `data_rate_kbps`, `freq_hopping`, and `antenna_mode`; the operator verbs `comms.enable_isl`, `comms.config_link`, `satcom.mitigate_interference`, `satcom.shift_users`, and `def.frequency_hop` (the anti-jam toggle) live in [`engine/buscommands.py`](../../spacesim/engine/buscommands.py).

### 1.6 Propulsion

**What it does.** Carries the main engine (apogee-kick or station-keeping) and the RCS thruster set (attitude control, momentum dump, fine translation for RPO), draws from one or more propellant tanks (mono- or bi-propellant chemical; xenon for SEP / electric birds), and exposes a delta-v budget that the bus spends over its lifetime — every maneuver, every desaturation burn, every collision-avoidance burn, every end-of-life graveyard or deorbit burn. The canonical specialist reference is **Sutton and Biblarz**, *Rocket Propulsion Elements*, 9th ed. (Wiley, 2017) — the textbook treatment of specific impulse, thrust sizing, propellant-tank sizing, and on-orbit propulsion-system architecture ([Wiley catalog](https://www.wiley.com/en-us/Rocket+Propulsion+Elements%2C+9th+Edition-p-9781118753651)), paired with [Wertz / Larson](https://microcosmpress.com/publishing/space-mission-engineering/) §17 for system-level integration and mission-Δv budgeting.

**What operators watch.** Propellant fraction remaining; delta-v budget remaining vs. planned manoeuvres for the rest of the mission; thruster duty cycle and any single-thruster failures; pending collision-avoidance (COLA) burns. Engine: [`bus.py:PropulsionState`](../../spacesim/engine/bus.py) carries `propellant_frac` with `PROP_SOFT = 0.15` / `PROP_HARD = 0.05` driving the status cascade; `Asset.resources.delta_v_ms` carries the manoeuvre budget itself. The operator verbs `prop.cancel_burn` and `prop.collision_avoid` live in [`engine/buscommands.py`](../../spacesim/engine/buscommands.py), and the six manoeuvre entry modes (`eci / lvlh / finite_burn / target_coe / hohmann / plane_change`) live in [`engine/maneuver.py`](../../spacesim/engine/maneuver.py).

### 1.7 The seventh state — safe mode

When any of the six subsystems trips its hard limit (power-red, attitude-lost, thermal-survival, propellant-red, storage-red, comms-fail) the flight software drops the bus into **safe mode**: the payload is gated off, the attitude controller goes sun-safe, the CDH goes safe-FSW, and the bus waits for ground recovery action. The engine encodes this as a seventh dataclass, [`bus.py:SafeModeState`](../../spacesim/engine/bus.py), tracking `active`, `entered_at`, `cause`, `current_step`, and `steps_done` (the deterministic recovery-chain progress). Forward-link to §2 (SOH / safe-mode subsection) for the recovery-loop deep-dive.

Used by: [`engine/bus.py:BusState`](../../spacesim/engine/bus.py) (the six per-subsystem dataclasses `PowerState`, `AttitudeState`, `CdhState`, `ThermalState`, `CommsState`, `PropulsionState`, plus `SafeModeState` and `PayloadState`); [`engine/buscommands.py:BUS_VERBS`](../../spacesim/engine/buscommands.py) and `PAYLOAD_VERBS` and `DEFENSE_VERBS` (the operator-facing command catalogue that mutates each subsystem); [`engine/busmodel.py`](../../spacesim/engine/busmodel.py) (the time-stepping that evolves the bus over the sim clock).

### Sources

- *Wertz, Everett, Puschell — Space Mission Engineering: The New SMAD* (Microcosm Press, 4th ed., 2011) — [live](https://microcosmpress.com/publishing/space-mission-engineering/)
  · [snapshot](https://web.archive.org/web/2026*/https://microcosmpress.com/publishing/space-mission-engineering/)
  · accessed 2026-06-21.
- *Patel — Spacecraft Power Systems* (CRC Press, 2004) — [live](https://www.routledge.com/Spacecraft-Power-Systems/Patel/p/book/9780849327865)
  · [snapshot](https://web.archive.org/web/2026*/https://www.routledge.com/Spacecraft-Power-Systems/Patel/p/book/9780849327865)
  · accessed 2026-06-21.
- *Sidi — Spacecraft Dynamics and Control: A Practical Engineering Approach* (Cambridge University Press, 1997 / 2000) — [live](https://www.cambridge.org/core/books/spacecraft-dynamics-and-control/F60C2D7EE9D33F2BCBAE53C5DA0F4FAB)
  · [snapshot](https://web.archive.org/web/2026*/https://www.cambridge.org/core/books/spacecraft-dynamics-and-control/F60C2D7EE9D33F2BCBAE53C5DA0F4FAB)
  · accessed 2026-06-21.
- *Eickhoff — Onboard Computers, Onboard Software and Satellite Operations* (Springer, 2012) — [live](https://link.springer.com/book/10.1007/978-3-642-25170-2)
  · [snapshot](https://web.archive.org/web/2026*/https://link.springer.com/book/10.1007/978-3-642-25170-2)
  · accessed 2026-06-21.
- *Gilmore (ed.) — Spacecraft Thermal Control Handbook, Vol. I Fundamental Technologies* (Aerospace Press / AIAA, 2nd ed., 2002; ISBN 1-884989-11-X) — [reference summary](https://aerospace.org/sites/default/files/2018-05/Welch_ThermalControl.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://aerospace.org/sites/default/files/2018-05/Welch_ThermalControl.pdf)
  · accessed 2026-06-21.
- *Maral, Bousquet, Sun — Satellite Communications Systems: Systems, Techniques and Technology*, 5th ed. (Wiley, 2009) — [live](https://www.wiley.com/en-us/Satellite+Communications+Systems%3A+Systems%2C+Techniques+and+Technology%2C+5th+Edition-p-9780470714584)
  · [snapshot](https://web.archive.org/web/2026*/https://www.wiley.com/en-us/Satellite+Communications+Systems%3A+Systems%2C+Techniques+and+Technology%2C+5th+Edition-p-9780470714584)
  · accessed 2026-06-21.
- *ITU-R Recommendation P.681* (propagation, land/maritime mobile-satellite) — [live](https://www.itu.int/rec/R-REC-P.681/en)
  · [snapshot](https://web.archive.org/web/2026*/https://www.itu.int/rec/R-REC-P.681/en)
  · accessed 2026-06-21.
- *ITU-R Recommendation S.484-3* (geostationary station-keeping geometry) — [live](https://www.itu.int/rec/R-REC-S.484/en)
  · [snapshot](https://web.archive.org/web/2024*/https://www.itu.int/rec/R-REC-S.484/en)
  · accessed 2026-06-21.
- *Sutton, Biblarz — Rocket Propulsion Elements*, 9th ed. (Wiley, 2017) — [live](https://www.wiley.com/en-us/Rocket+Propulsion+Elements%2C+9th+Edition-p-9781118753651)
  · [snapshot](https://web.archive.org/web/2026*/https://www.wiley.com/en-us/Rocket+Propulsion+Elements%2C+9th+Edition-p-9781118753651)
  · accessed 2026-06-21.
## 2. State of Health (SOH) and safe mode

The six bus subsystems in §1 are not what the operator *watches* in flight — what the operator watches is the **state-of-health (SOH) panel** that rolls each subsystem up into a green / yellow / red traffic light, and the **safe-mode flag** that the flight software trips when any one of those lights goes hard-red. SOH is the operator's primary instrument panel; safe mode is the bus's autonomous fallback when the panel says the bird is no longer safe to operate at full mission. The two are tightly coupled — the SOH limits are the trigger for safe mode, and the recovery chain back out of safe mode is the only path the operator has to restore nominal — so the canonical research treats them as one topic, and so does the engine (the six per-subsystem dataclasses on [`engine/bus.py:BusState`](../../spacesim/engine/bus.py) plus the seventh [`SafeModeState`](../../spacesim/engine/bus.py) that tracks recovery progress, plus the multi-pass [`engine/recovery.py:RecoverySystem`](../../spacesim/engine/recovery.py) that walks the chain).

### 2.1 The SOH discipline — soft / hard thresholds, traffic-light rollup

Every operational mission control system in the open-source record — the ESA SCOS-2000 family on the institutional side, L3Harris InControl on the commercial side, NASA OpenMCT in the open-source plug-in space — formats SOH the same way: each telemetry parameter carries a **nominal value**, a **soft limit** that flips the indicator yellow at first crossing, and a **hard limit** that flips it red and (typically) latches a ground alarm; the per-subsystem rollup takes the worst color across all parameters that subsystem owns, and the per-asset rollup takes the worst across all subsystems. The canonical reference is [Peccia 2003 on SCOS-2000](https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf) — the ESA mission-control system whose "out-of-limit checking, status reporting, and event logging" subsystem (Peccia §3) is the exemplar every later console copied — paired with the commercial-side [L3Harris InControl product description](https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control) (constellation overview → per-spacecraft drill-down → per-subsystem traffic-light SOH). The simulator encodes the same discipline as the two helpers [`engine/bus.py:status_low`](../../spacesim/engine/bus.py) (for quantities healthy when high — battery SoC, propellant) and [`engine/bus.py:status_high`](../../spacesim/engine/bus.py) (for quantities unhealthy when high — onboard storage fill), with the module-level constants `SOC_SOFT = 0.30` / `SOC_HARD = 0.15`, `STORAGE_SOFT = 0.85` / `STORAGE_HARD = 0.98`, and `PROP_SOFT = 0.15` / `PROP_HARD = 0.05` driving the cascade. [`engine/bus.py:recompute_status`](../../spacesim/engine/bus.py) refreshes each subsystem's status field every bus-evolution tick and `overall_status` rolls up to the per-asset worst-color the GUI renders.

The broader operations-engineering frame that codifies SOH as a *discipline* (not just a UI pattern) lives in the NASA technical-standards corpus — specifically [NASA-STD-7009A *Standard for Models and Simulations*](https://standards.nasa.gov/standard/nasa/nasa-std-7009) and [NASA-STD-8729.1A *NASA Reliability and Maintainability Standard for Spaceflight and Support Systems*](https://standards.nasa.gov/standard/nasa/nasa-std-87291) — which together require any flight system to expose a documented, threshold-driven SOH telemetry stream that ground operators can monitor against published limits. The simulator's per-parameter telemetry definitions follow this convention exactly.

### 2.2 The per-parameter ParamSpec model

Each leaf telemetry channel is a [`engine/telemetry.py:ParamSpec`](../../spacesim/engine/telemetry.py) row carrying `id`, `subsystem`, `label` (human-readable), `unit`, `nominal` (the reference value), `amp` (the seeded value-noise amplitude in physical units), `soft` + `hard` thresholds, and a `higher_is_bad` flag that picks between the `status_high` and `status_low` helpers above. The 19 channels in the `PARAMS` registry span all six subsystems (battery SoC, bus voltage and array current for EPS; attitude error and wheel RPM for ADCS; payload + optics temperatures for TCS; propellant fraction and tank pressure for propulsion; CPU load, FSW errors, command rejects, storage for CDH; RX power, C/N0, BER, uplink lock for comms; payload SNR and integrity flag for the payload itself). The `amp` field makes the panel *look real* (a stable battery voltage shows a few-tenths-of-a-volt ripple, not a perfect 28.0); the `higher_is_bad` field makes the same panel work for "good when high" and "bad when high" channels without per-channel logic in the renderer. The 19 ParamSpec rows are what the operator GUI's per-subsystem drill-down panels graph — forward-link to §8 (operator interfaces) for the rendering side, and to §2.5 below for the attack-symptom overlay that perturbs these same channels under jam / cyber / directed-energy effects.

### 2.3 Safe mode as designed-in FDIR — "safe + listen for help"

When any per-subsystem status goes hard-red the flight software is supposed to *autonomously* drop the bus into **safe mode** — a minimum-power, sun-pointed, mission-payload-off configuration that holds the bird alive and listening for command-uplink contact while the ground figures out what broke. This is the canonical **fault detection, isolation, and recovery (FDIR)** pattern, codified in the satellite-engineering literature for forty years. The doctrinal reference is [Wertz, Everett & Puschell, *Space Mission Engineering: The New SMAD* (Microcosm Press, 4th ed., 2011)](https://microcosmpress.com/publishing/space-mission-engineering/), Chapter 11 (EPS, which sources the SoC-floor safe-mode trigger) and Chapter 13 (FDIR, which formalizes the autonomy ladder — detect, isolate, react, recover — and the "go safe and listen" terminal state when the on-board diagnoser cannot localize the fault). The Wertz / Larson framing is deliberate: safe mode is not a failure, it is a *designed-in product* of the bus, the configuration the bus was always going to fall back to. The engine encodes that design in [`engine/bus.py:enter_safe_mode`](../../spacesim/engine/bus.py): on a hard limit (or a cyber resolution with `outcome=safe_mode`) the bus flips `mode = "safe_mode"`, the attitude controller forces `mode = "safe"`, the CDH `fsw_mode` forces `"safe"`, and a fresh [`SafeModeState`](../../spacesim/engine/bus.py) records `entered_at`, `cause` (one of `fault | environment | cyber | ew | bus_stress`), and the recovery-chain starting step. The gating predicate [`engine/bus.py:payload_available`](../../spacesim/engine/bus.py) collapses to false until the bus exits safe mode — exactly the "payload off" half of the design.

### 2.4 The multi-pass recovery chain

Safe mode is "easy" to enter and *expensive* to exit. The recovery chain operators actually walk in flight — documented in NASA Goddard's published anomaly-response procedures for [Hubble Space Telescope safe-mode recoveries](https://science.nasa.gov/mission/hubble/observatory/safe-mode-anomalies/) (which has logged ~30 entry-and-recovery cycles over its lifetime, each one a multi-day ground campaign across multiple command-uplink passes) and in NOAA's [OSPO satellite-anomaly bulletins](https://www.ospo.noaa.gov/news.html) — is **establish contact → dump telemetry → diagnose → patch → re-enable**, and each step takes a real command-uplink pass to complete. The simulator's [`engine/recovery.py:RecoverySystem`](../../spacesim/engine/recovery.py) is built around this chain: `begin_recovery(sat_id, via_station)` enumerates the next 24 hours of command-uplink windows via the `AccessProvider`, schedules a `recovery_confirm` event on the first window (which records `establish_contact` + `dump_telemetry` and advances `current_step` to `diagnose`), and schedules a `recovery_finish` event on window N — where N is the `passes_needed()` lookup `{quick: 1, realistic: 2, punishing: 3}` keyed on the vignette's difficulty dial. The finish handler appends the remaining steps (`patch`, `re_enable`) and calls [`engine/bus.py:exit_safe_mode`](../../spacesim/engine/bus.py). The whole chain is a sequence of scheduled events on real access windows — deterministic, replay-safe, and exactly the multi-pass shape the Hubble and NOAA anomaly records describe. Vignettes that exercise this end-to-end include [`content/vignettes/learn-intermediate-recovery.yaml`](../../spacesim/content/vignettes/learn-intermediate-recovery.yaml), which forces the trainee through the full chain on a Blue ISR bird.

### 2.5 Cyber-induced safe mode — the "re-safed until you patch" pattern

The vignette twist the engine adds is the **persistent root cause**: if the SafeModeState `cause` is `cyber`, [`engine/recovery.py:RecoverySystem._h_finish`](../../spacesim/engine/recovery.py) checks whether any entry in `sat.cyber_vulnerabilities` is still unpatched, and if so sets `blocked_reason = "root cause persists (cyber)"`, leaves `current_step = "blocked"`, and **does not exit safe mode** — the bird is re-safed at the end of the recovery chain. The defender has to first patch the vulnerability (the `def.patch_cyber` operator verb in [`engine/buscommands.py`](../../spacesim/engine/buscommands.py)) and *then* re-run `begin_recovery`. This is the engine's encoding of the **`seize_c2`** cyber payload pattern from [`03-counterspace-taxonomy.md` §7](03-counterspace-taxonomy.md): a legitimate-looking management command drops the target into safe mode through its own flight software, and until the underlying access vector is closed the bird re-safes itself every time the operator tries to recover it. The pedagogical claim — and the reason this loop exists as a first-class engine system — is that *recovery from a cyber-induced safe mode is structurally different from recovery from a power-red safe mode*, and the operator who treats them the same will spend the rest of the exercise watching the same bird re-safe on every pass.

Used by: [`engine/bus.py:SafeModeState`](../../spacesim/engine/bus.py); [`engine/bus.py:enter_safe_mode`](../../spacesim/engine/bus.py) / [`exit_safe_mode`](../../spacesim/engine/bus.py); [`engine/bus.py:recompute_status`](../../spacesim/engine/bus.py); [`engine/bus.py:status_low`](../../spacesim/engine/bus.py) / [`status_high`](../../spacesim/engine/bus.py) (+ the `SOC_*`, `STORAGE_*`, `PROP_*` threshold constants); [`engine/recovery.py:RecoverySystem`](../../spacesim/engine/recovery.py) (`begin_recovery`, `_h_confirm`, `_h_finish`, `_root_cause_unresolved`); [`engine/telemetry.py:ParamSpec`](../../spacesim/engine/telemetry.py) and the 19-row `PARAMS` registry; [`content/vignettes/learn-intermediate-recovery.yaml`](../../spacesim/content/vignettes/learn-intermediate-recovery.yaml).

### Sources

- *Peccia, "SCOS-2000 — ESA's Spacecraft Control for the 21st Century"* (Ground System Architectures Workshop 2003 — the canonical reference for the out-of-limit checking, status reporting, and event-logging pattern every later mission-control console copied) — [live](https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf)
  · accessed 2026-06-12.
- *L3Harris InControl — Satellite Command and Control* (commercial mission-operations system product description; per-subsystem traffic-light SOH on the constellation overview + per-spacecraft drill-down) — [live](https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control)
  · [snapshot](https://web.archive.org/web/2026*/https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control)
  · accessed 2026-06-12.
- *NASA-STD-7009A — Standard for Models and Simulations* (NASA Technical Standards System; documented threshold-driven SOH telemetry requirement) — [live](https://standards.nasa.gov/standard/nasa/nasa-std-7009)
  · [snapshot](https://web.archive.org/web/2026*/https://standards.nasa.gov/standard/nasa/nasa-std-7009)
  · accessed 2026-06-12.
- *NASA-STD-8729.1A — NASA Reliability and Maintainability Standard for Spaceflight and Support Systems* (NASA Technical Standards System; the broader operations-engineering frame for FDIR-ready SOH instrumentation) — [live](https://standards.nasa.gov/standard/nasa/nasa-std-87291)
  · [snapshot](https://web.archive.org/web/2026*/https://standards.nasa.gov/standard/nasa/nasa-std-87291)
  · accessed 2026-06-12.
- *Wertz, Everett, Puschell — Space Mission Engineering: The New SMAD* (Microcosm Press, 4th ed., 2011) — Chapter 11 (EPS, SoC-floor safe-mode trigger) and Chapter 13 (FDIR — detect / isolate / react / recover ladder and the "go safe and listen" terminal state) — [live](https://microcosmpress.com/publishing/space-mission-engineering/)
  · [snapshot](https://web.archive.org/web/2026*/https://microcosmpress.com/publishing/space-mission-engineering/)
  · accessed 2026-06-12.
- *NASA Hubble Space Telescope — Safe-Mode Anomalies* (NASA Goddard mission page documenting Hubble's ~30 safe-mode entry-and-recovery cycles and the multi-pass ground-recovery procedure) — [live](https://science.nasa.gov/mission/hubble/observatory/safe-mode-anomalies/)
  · [snapshot](https://web.archive.org/web/2026*/https://science.nasa.gov/mission/hubble/observatory/safe-mode-anomalies/)
  · accessed 2026-06-12.
- *NOAA Office of Satellite and Product Operations — Satellite News* (NOAA OSPO anomaly bulletins; the canonical open-source record of GOES / JPSS / DMSP safe-mode entries and the per-incident ground-recovery campaigns) — [live](https://www.ospo.noaa.gov/news.html)
  · [snapshot](https://web.archive.org/web/2026*/https://www.ospo.noaa.gov/news.html)
  · accessed 2026-06-12.
## 3. The contact-driven operator reality (pre-pass / in-pass / post-pass)

Satellite operators do not work over a continuous link. They work over a sequence of **scheduled passes**, and every shift is organised around the next contact. Mission-operations doctrine going back to Wertz & Larson's *Space Mission Analysis and Design* (Ch. 14, "Mission Operations") splits each contact into three distinct activities: a **pre-pass** planning and command-load build, an **in-pass** live commanding and telemetry-monitoring window, and a **post-pass** data-pull, log review and hand-off ([SMAD Ch. 14, "Mission Operations"](https://dta0yqvfnusiq.cloudfront.net/tsti/2015/06/SMAD_Fronts.pdf)). The same three-phase framing structures ESA's mission control software: [Peccia 2003](https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf) (already cited in §1.6.2) describes SCOS-2000 as a generic MCS that archives telemetry, telecommands and events across the pass lifecycle, with operator consoles for [real-time and off-line retrieval](https://www.esa.int/esapub/bulletin/bullet108/chapter8_bul108.pdf).

### 3.1 Pre-pass: build the command load

Operators spend most of their time *between* passes. The deliverable of pre-pass is a **command load** — a pre-built, time-ordered sequence of commands prepared on the ground and uplinked in one shot on the next contact, then executed autonomously by the on-board command sequencer. NASA's Mars Global Surveyor flight-operations reference defines the two command classes precisely: **real-time commands (RTCs)** that execute on receipt, and **stored-sequence command (SSC) files** that are "a series of commands and/or calls to on-board stored scripts, each with an associated time tag," where the tag is "either an absolute execution time or a time relative to the execution of the previous command" ([MGS Spacecraft Subsystems §5](https://mars.nasa.gov/mgs/scsys/e3/e35.html)). JPL deep-space missions formalise this with [VML (Virtual Machine Language)](https://fprime.jpl.nasa.gov/latest/Svc/CmdSequencer/docs/sdd/), "an advanced procedural sequencing language which simplifies spacecraft operations [and] minimizes uplink product size." The Command Management System (CMS) "generates planned sequences of spacecraft commands (command loads)" and checks that they are "free from known operational constraint violations or conflicts" ([NASA GSFC, *Satellite Ground Operations Automation*](https://ntrs.nasa.gov/api/citations/20020023390/downloads/20020023390.pdf)). Typical cadence on a stable science mission is a **weekly command load** built on the ground and uplinked once per week.

### 3.2 In-pass: short window, no time to think

Pass-duration physics dictates the rhythm. From a single ground station, a LEO satellite is in view for roughly **5–12 minutes per pass**, frequent but short (cross-link to [04-orbital-mechanics-primer.md §2](04-orbital-mechanics-primer.md) for the geometry derivation). GEO assets, by contrast, sit in [continuous view](https://en.wikipedia.org/wiki/Geosynchronous_satellite) of any one well-placed station — but operators still maintain **multiple ground stations** for redundancy, weather diversity, and steerable-antenna load balancing, which is why the [AFSCN](https://en.wikipedia.org/wiki/Satellite_Control_Network) and NASA's [TDRSS / White Sands Complex](https://www.nasa.gov/smallsat-institute/sst-soa/ground-data-systems-and-mission-operations/) exist as networks rather than single sites. During the in-pass window the operator executes the pre-built load, watches telemetry stream in, and — if a parameter goes red — has only minutes to abort, send a real-time command, or accept the anomaly and clean it up later. AFSCN users "submit a schedule request to the [Network Operations Center](https://en.wikipedia.org/wiki/Satellite_Control_Network) for arbitration" days in advance; the contact itself is a scheduled, contested resource.

### 3.3 Post-pass: pull, log, hand off

The pass closes with telemetry playback, an anomaly write-up, and a shift hand-off. SCOS-2000's archive is the canonical event-log substrate: PARC stores "all packet based data (telemetry, telecommand history and event data)" on Oracle/MySQL, and "different applications and external interfaces are available for retrieving data both in real-time and off-line" ([ESA Bulletin 115](https://www.esa.int/esapub/bulletin/bullet115/chapter8_bul115.pdf)) — i.e. the same event stream the on-shift console rendered is replayed by the next shift. Hubble's STOCC formalises the anomaly side: an [Anomaly Response Manager (ARM)](https://science.nasa.gov/mission/hubble/observatory/mission-operations/) "monitors the results of operations procedures as they are executed during anomaly situations," and "if an anomaly occurs … when the facility is unoccupied, a high-reliability text messaging system immediately alerts the appropriate members of the operations team." That alert plus the event-log replay is how the next shift inherits state.

### 3.4 Why this drives the simulator's window-gated UX

The engine encodes this loop literally. Operators **plan** during the long inactive stretches and **act** only during access windows — exactly the [engine/orders.py:OrderSystem.issue](../../spacesim/engine/orders.py) flow (validate → next valid window → execute), the [engine/orders.py:OrderSystem.dry_run](../../spacesim/engine/orders.py) read-only mirror that powers the UI's "why can't I?" pre-disabled buttons, and the [session/manager.py:next_contacts](../../spacesim/session/manager.py) fleet countdown that tells each cell when its next pass opens. The in-pass moment — "what the ground operator sees while the satellite is overhead" — is encoded by the contact-tick handler [engine/busmodel.py:_h_contact](../../spacesim/engine/busmodel.py) (line 56), which gates link state during the window, and by [engine/bus.py:refresh_ground_view](../../spacesim/engine/bus.py) (line 238), which refreshes operator-visible SOH only while the pass is open. Outside the window the ground view goes stale on purpose — that's the fog of "no contact yet."

### Sources

- *Space Mission Analysis and Design (SMAD), 3rd Ed., front matter / TOC (Ch. 14 = Mission Operations)* — [live](https://dta0yqvfnusiq.cloudfront.net/tsti/2015/06/SMAD_Fronts.pdf) · [snapshot](https://web.archive.org/web/2026*/https://dta0yqvfnusiq.cloudfront.net/tsti/2015/06/SMAD_Fronts.pdf) · accessed 2026-06-12.
- *Peccia, "SCOS-2000 Release 4.0," GSAW 2003* — [live](https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf) · [snapshot](https://web.archive.org/web/2026*/https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf) · accessed 2026-06-12.
- *ESA Bulletin 108 — "Promoting ESA Software as a European Asset: the SCOS-2000 Example"* — [live](https://www.esa.int/esapub/bulletin/bullet108/chapter8_bul108.pdf) · [snapshot](https://web.archive.org/web/2026*/https://www.esa.int/esapub/bulletin/bullet108/chapter8_bul108.pdf) · accessed 2026-06-12.
- *ESA Bulletin 115 — Technical & Operational Support (SCOS-2000 archive)* — [live](https://www.esa.int/esapub/bulletin/bullet115/chapter8_bul115.pdf) · [snapshot](https://web.archive.org/web/2026*/https://www.esa.int/esapub/bulletin/bullet115/chapter8_bul115.pdf) · accessed 2026-06-12.
- *NASA Mars Global Surveyor — Spacecraft Subsystem Functions §5 (RTC vs. SSC command loads)* — [live](https://mars.nasa.gov/mgs/scsys/e3/e35.html) · [snapshot](https://web.archive.org/web/2026*/https://mars.nasa.gov/mgs/scsys/e3/e35.html) · accessed 2026-06-12.
- *NASA GSFC, "Satellite Ground Operations Automation — Lessons Learned" (CMS / command-load generation)* — [live](https://ntrs.nasa.gov/api/citations/20020023390/downloads/20020023390.pdf) · [snapshot](https://web.archive.org/web/2026*/https://ntrs.nasa.gov/api/citations/20020023390/downloads/20020023390.pdf) · accessed 2026-06-12.
- *JPL F-Prime, Svc::CmdSequencer SDD (on-board command sequencer reference)* — [live](https://fprime.jpl.nasa.gov/latest/Svc/CmdSequencer/docs/sdd/) · [snapshot](https://web.archive.org/web/2026*/https://fprime.jpl.nasa.gov/latest/Svc/CmdSequencer/docs/sdd/) · accessed 2026-06-12.
- *NASA SST-SOA §11 — Ground Data Systems & Mission Operations (TDRSS / WSC ground architecture)* — [live](https://www.nasa.gov/smallsat-institute/sst-soa/ground-data-systems-and-mission-operations/) · [snapshot](https://web.archive.org/web/2026*/https://www.nasa.gov/smallsat-institute/sst-soa/ground-data-systems-and-mission-operations/) · accessed 2026-06-12.
- *NASA Hubble Mission Operations (STOCC, ARM, anomaly alerting)* — [live](https://science.nasa.gov/mission/hubble/observatory/mission-operations/) · [snapshot](https://web.archive.org/web/2026*/https://science.nasa.gov/mission/hubble/observatory/mission-operations/) · accessed 2026-06-12.

Used by: [engine/orders.py:OrderSystem.issue](../../spacesim/engine/orders.py), [engine/orders.py:OrderSystem.dry_run](../../spacesim/engine/orders.py), [engine/busmodel.py:_h_contact](../../spacesim/engine/busmodel.py), [engine/bus.py:refresh_ground_view](../../spacesim/engine/bus.py), [session/manager.py:next_contacts](../../spacesim/session/manager.py).
## 4. Power calibration (sources the TT&C audit recalibration)

This subsection sources the per-second SoC charge and drain rates that the engine's
[`engine/bus.py:advance_bus`](../../spacesim/engine/bus.py) integrates each tick, and
explains why the June 2026 [TT&C audit](../AUDIT-2026-06-UI-TTC.md) §2 had to
recalibrate every vignette's `bus_state.power` block to match real LEO-bus behaviour.
The upstream input — the eclipse lit-fraction the audit also wired in — is sourced in
[`04-orbital-mechanics-primer.md`](04-orbital-mechanics-primer.md) §5; the rates
documented here are the per-tick coefficients that lit-fraction multiplies against.

**Realistic LEO depth-of-discharge per orbit.** A LEO bus running lithium-ion cells is
sized for a **15–25% depth-of-discharge (DoD) per ~95-minute orbit** at end-of-life
capacity, with the upper bound set by the cycle-life budget the mission lifetime demands
([Wertz, Everett & Puschell, *Space Mission Engineering: The New SMAD*, Microcosm
Press](https://microcosmpress.com/publishing/space-mission-engineering-the-new-smad/) Ch. 11
EPS sizing). The trade is well-characterized: cells cycled at 40–60% DoD reach the
~30,000 LEO eclipse cycles a five-year mission needs only with aggressive thermal
management, and cycle life falls off super-linearly past ~30% DoD, which is why
mission-design houses pick 15–25% as the operating point and accept the array-mass
penalty
([Patel, *Spacecraft Power Systems*, CRC Press, ISBN 0-8493-2786-5](https://www.routledge.com/Spacecraft-Power-Systems/Patel/p/book/9780849327865)
Ch. 9). The general battery-longevity guidance — DoD vs. cycle-life curves, thermal
derating, charge-rate limits — is consolidated in [NASA-HDBK-4002A (*Mitigating In-Space
Charging Effects*)](https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/Historical/nasa-hdbk-4002a-w-Change-1_revalidated.pdf)
§5, the design-guideline standard NASA flight-systems programs cite as the longevity
reference.

**Real-mission anchor points.** The ISS is the most-documented LEO-bus example. Its
original 38 Ni-H₂ batteries were sized for **35% DoD** at end-of-life cycle limits
([Dalton et al., *International Space Station Lithium-Ion Battery*, NASA TM
20160012048](https://ntrs.nasa.gov/citations/20160012048)). The 2017–2019 LIB ORU
upgrade replaced them with lithium-ion ORUs operating at **~10% DoD per orbit** at
beginning-of-life — the lower number both because Li-ion cells gain capacity-per-mass
relative to Ni-H₂ and because the upgrade was sized for ~20-year orbital life
([Dakermanji et al., *ISS Li-Ion Battery Start-Up and Cycling*, NASA TM
20180003481](https://ntrs.nasa.gov/citations/20180003481)). The Landsat-class LEO ISR
bus runs at the **20–25% DoD** band typical of remote-sensing missions: Landsat 8 carries
a 125 Ah Ni-H₂ battery sized for the 5-year design life with consumables for 10 years
([Landsat 8 Mission Details, NASA
GSFC](https://landsat.gsfc.nasa.gov/satellites/landsat-8/landsat-8-mission-details/)) —
the canonical anchor for the sim's ISR vignettes, which run sun-synchronous mid-morning
LTAN orbits with the same eclipse-fraction profile.

**Sun-synchronous eclipse profile dominates the calibration.** The per-orbit DoD scales
directly with the **eclipse fraction** the orbit lighting profile imposes. A 600-km mid-
morning SSO (LTAN ≈ 10:00–10:30, the Landsat / Sentinel-2 design point) spends roughly
**30–35% of each orbit in Earth's shadow**, the geometry sourced in detail in
[`04-orbital-mechanics-primer.md`](04-orbital-mechanics-primer.md) §5 and pinned to
[NASA Landsat, *Geometry of a Sun-Synchronous
Orbit*](https://landsat.gsfc.nasa.gov/article/geometry-of-a-sun-synchronous-orbit). A
dawn-dusk SSO (LTAN ≈ 06:00 / 18:00) sees near-zero eclipse for much of the year, which
is why dawn-dusk SSO is the preferred design when constant illumination matters more than
imaging geometry. The eclipse fraction is what makes the array-W ↔ drain-rate ratio a
sizing constraint rather than a free parameter: an orbit-averaged drain that exceeds
sunlit-fraction × charge produces a monotonic SoC decline regardless of starting state.

**Sizing rules of thumb.** Two rules govern EPS sizing. The **array rule** is
`P_array ≈ E_orbit / (f_sunlit · η)` — the solar array must deliver the orbit's total
energy demand within the sunlit fraction, derated by harness-and-conversion efficiency η
(typically 0.7–0.85 for LEO Ni-H₂ / Li-ion systems)
([Wertz/Larson SMAD](https://microcosmpress.com/publishing/space-mission-engineering-the-new-smad/)
Ch. 11). The **battery rule** is `usable_Wh = DoD_limit · rated_Wh`, with `DoD_limit`
set by the cycle-life budget — 15–25% for LEO at 5-year missions, 40–60% only for
short-life missions or once-per-orbit emergency loads
([Patel](https://www.routledge.com/Spacecraft-Power-Systems/Patel/p/book/9780849327865)
Ch. 9; [NASA-HDBK-4002A](https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/Historical/nasa-hdbk-4002a-w-Change-1_revalidated.pdf)
§5). Both rules collapse into the sim's two scalars, [`PowerState.charge_rate_per_s` and
`PowerState.drain_rate_per_s`](../../spacesim/engine/bus.py), with the per-tick
integration `delta = (charge·lit − drain·(1−lit))·dt` mirroring the orbit-averaged
energy balance.

**The audit recalibration.** Pre-audit, every vignette's `bus_state.power` carried
`charge_rate_per_s: 0.0002` and `drain_rate_per_s: 0.0003` — values that produced a
**1.00 → 0.37 sawtooth per ~97-minute orbit** (~63% DoD with **zero Red action**), 3–4×
deeper than any real LEO bus and well outside the 15–25% Wertz/Larson band
([audit §2](../AUDIT-2026-06-UI-TTC.md)). The per-orbit margin was net 0% at eclipse
fraction 0.40, so any added payload load tipped the battery into a death spiral and the
operator saw an unexplained SoC collapse on the telemetry graph. The audit recalibrated
to `charge_rate_per_s: 0.00012` and `drain_rate_per_s: 0.0001` across all ten vignettes
(verifiable in [`spacesim/content/vignettes/`](../../spacesim/content/vignettes/) — every
`bus_state.power` block), which produces a **0.79 → 1.00 cycle (~21% DoD per orbit)**
squarely in the Wertz/Larson and Patel realistic band. The audit paired this with the
penumbra-aware lit-fraction blend so terminator crossings ramp smoothly rather than
stepping (see [`04-orbital-mechanics-primer.md`](04-orbital-mechanics-primer.md) §5
for that geometry).

**Named follow-up.** The [audit §2 follow-ups](../AUDIT-2026-06-UI-TTC.md) flag
[`entities.AssetResources.power_w`](../../spacesim/engine/entities.py) (1500 W in
vignette 1) as a **dead field** — the engine currently uses the abstract per-second
`charge_rate_per_s` scalar instead of deriving rates from `array_W + battery_Wh +
eclipse_fraction`. A future tightening would wire this end-to-end: the vignette author
specifies array W and battery Wh (the physical inputs a real EPS designer works in), and
the engine derives the SoC rates via the array and battery rules above. The current
abstract-rate model is sufficient for PME training (operators see the SoC curve respond
correctly to attack and recovery) but loses the design-review surface a high-fidelity
follow-on would expose.

Used by: [`engine/bus.py:PowerState.charge_rate_per_s`](../../spacesim/engine/bus.py)
and [`engine/bus.py:PowerState.drain_rate_per_s`](../../spacesim/engine/bus.py) (the
two scalars the audit recalibrated); [`engine/bus.py:advance_bus`](../../spacesim/engine/bus.py)
(the per-tick `delta = (charge·lit − drain·(1−lit))·dt` integration that consumes them);
every vignette's `bus_state.power` block under
[`spacesim/content/vignettes/`](../../spacesim/content/vignettes/) (all ten vignettes
carry the recalibrated `0.00012 / 0.0001` rates);
[`spacesim/tests/test_power_calibration.py`](../../spacesim/tests/test_power_calibration.py)
(the regression that pins baseline SoC ≥ 0.30 over multiple orbits).

### Sources

- *Wertz, Everett & Puschell, Space Mission Engineering: The New SMAD* (Microcosm Press),
  Ch. 11 EPS sizing — array rule, battery rule, LEO DoD band — [live](https://microcosmpress.com/publishing/space-mission-engineering-the-new-smad/)
  · [snapshot](https://web.archive.org/web/2026*/https://microcosmpress.com/publishing/space-mission-engineering-the-new-smad/)
  · accessed 2026-06-12.
- *Patel, Spacecraft Power Systems* (CRC Press, ISBN 0-8493-2786-5), Ch. 9 DoD vs.
  cycle-life trade — [live](https://www.routledge.com/Spacecraft-Power-Systems/Patel/p/book/9780849327865)
  · [snapshot](https://web.archive.org/web/2026*/https://www.routledge.com/Spacecraft-Power-Systems/Patel/p/book/9780849327865)
  · accessed 2026-06-12.
- *NASA-HDBK-4002A w/Change 1 (Revalidated), Mitigating In-Space Charging Effects — A
  Guideline*, §5 design guidelines — [live](https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/Historical/nasa-hdbk-4002a-w-Change-1_revalidated.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://standards.nasa.gov/sites/default/files/standards/NASA/B/0/Historical/nasa-hdbk-4002a-w-Change-1_revalidated.pdf)
  · accessed 2026-06-12.
- *Dalton et al., International Space Station Lithium-Ion Battery*, NASA TM 20160012048
  — original Ni-H₂ DoD baseline + LIB ORU sizing — [live](https://ntrs.nasa.gov/citations/20160012048)
  · [snapshot](https://web.archive.org/web/2026*/https://ntrs.nasa.gov/citations/20160012048)
  · accessed 2026-06-12.
- *Dakermanji et al., ISS Li-Ion Battery Start-Up and Cycling*, NASA TM 20180003481 —
  post-2017 ~10% DoD operating point — [live](https://ntrs.nasa.gov/citations/20180003481)
  · [snapshot](https://web.archive.org/web/2026*/https://ntrs.nasa.gov/citations/20180003481)
  · accessed 2026-06-12.
- *Landsat 8 Mission Details*, NASA GSFC — 125 Ah Ni-H₂ battery, 5-yr design / 10-yr
  consumables — [live](https://landsat.gsfc.nasa.gov/satellites/landsat-8/landsat-8-mission-details/)
  · [snapshot](https://web.archive.org/web/2026*/https://landsat.gsfc.nasa.gov/satellites/landsat-8/landsat-8-mission-details/)
  · accessed 2026-06-12.
- *NASA Landsat, Geometry of a Sun-Synchronous Orbit* — SSO eclipse-fraction profile by
  LTAN — [live](https://landsat.gsfc.nasa.gov/article/geometry-of-a-sun-synchronous-orbit)
  · [snapshot](https://web.archive.org/web/2026*/https://landsat.gsfc.nasa.gov/article/geometry-of-a-sun-synchronous-orbit)
  · accessed 2026-06-12.
- *Project audit* (`docs/AUDIT-2026-06-UI-TTC.md` §2: drain `0.0003→0.0001`, charge
  `0.0002→0.00012`, ~63% DoD sawtooth → ~21% DoD cycle) — [local file](../AUDIT-2026-06-UI-TTC.md).
## 5. Payload ops — SATCOM (WGS, AEHF/Milstar, Eutelsat Quantum, anti-jam techniques)

SATCOM payloads are *operated*, not just pointed: the operator manages channels, steers beams, hops frequencies, nulls jammers, sheds non-priority users to free capacity, and — on the ground side — geolocates the source of interference. This subsection grounds the engine's three SATCOM payload verbs (`satcom.mitigate_interference`, `satcom.shift_users`, `satcom.geolocate_interference`) in the public record on three representative platforms (US WGS, US AEHF/Milstar, commercial Eutelsat Quantum) plus the underlying anti-jam techniques.

### 5.1 WGS + MAJE (mitigation + anti-jam enhancement)

The Wideband Global SATCOM (WGS) constellation is the US military's primary wideband X/Ka-band SATCOM backbone (10 Boeing GEO satellites as of program testing). Because the original WGS birds were not designed for a contested EW environment, the Space Force funded the **Mitigation and Anti-Jam Enhancement (MAJE)** ground-segment upgrade, which "[doubles the anti-jam capabilities for 16,000+ users](https://www.losangeles.spaceforce.mil/News/Article/2507386/wgs-mitigation-and-anti-jam-enhancement-program-successfully-completes-major-te/)" and gives operators the ability to "[isolate unwanted signals interfering with WGS and restore affected communications faster than before](https://www.losangeles.spaceforce.mil/News/Article/2507386/wgs-mitigation-and-anti-jam-enhancement-program-successfully-completes-major-te/)." Critically, MAJE testing verified the system's ability to "[provide telemetry and successfully locate signals interfering with WGS satellites](https://www.satellitetoday.com/government-military/2021/02/19/space-force-tested-geo-location-of-jamming-signals-for-wgs-satellites/)" — i.e. uplink-jammer geolocation, which is the real-world referent for `satcom.geolocate_interference`. MAJE upgrades the Global SATCOM Configuration Control Element (GSCCE) ground segment operated by the Army, with [system-level testing completed in 2021 and fielding planned 2022+](https://www.defensenews.com/battlefield-tech/space/2021/02/18/space-force-says-new-anti-jamming-upgrade-coming-in-2022/).

### 5.2 AEHF + legacy Milstar — protected SATCOM done in hardware

The Advanced Extremely High Frequency (AEHF) constellation is the US protected-SATCOM backbone — the explicit successor to Milstar. Per the USSF fact sheet, AEHF provides "[survivable, global, secure, protected, and jam-resistant communications for high-priority military ground, sea and air assets](https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197713/advanced-extremely-high-frequency-system/)" and is "[protected from nuclear effects and jamming activities](https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197713/advanced-extremely-high-frequency-system/)." The protection mechanisms are baked into the bus: [frequency-hopping radios plus phased-array antennas that adapt their radiation patterns to null sources of jamming](https://media.defense.gov/2022/Apr/08/2002973439/-1/-1/1/AEHF%20FACTSHEET.PDF), operating at 44 GHz uplink (EHF) / 20 GHz downlink (SHF). Operationally the constellation is flown by [the 4th Space Operations Squadron at Schriever](https://media.defense.gov/2022/Apr/08/2002973439/-1/-1/1/AEHF%20FACTSHEET.PDF). AEHF is the pedagogical counterexample to WGS: anti-jam built in at the payload, not retrofitted at the ground.

### 5.3 Eutelsat Quantum — the commercial software-defined payload

Eutelsat Quantum, launched on Ariane 5 on 30 July 2021, is the [world's first commercial software-defined satellite](https://www.airbus.com/en/newsroom/press-releases/2021-06-airbus-built-eutelsat-quantum-satellite-shipped-to-launch-site), built by Airbus Defence and Space under an ESA public-private partnership with Eutelsat. The payload carries the [ELSA+ multibeam active antenna with eight independent reconfigurable Ku-band beams](https://www.eoportal.org/satellite-missions/eutelsat-quantum) whose shape, frequency, bandwidth, and power are reprogrammable on orbit — including beam-hopping in near real time. This is the commercial template for `satcom.shift_users`: the operator literally redraws coverage to follow demand or to move users off a contested footprint. [In-orbit testing completed Nov 2021 at 48° E](https://www.eoportal.org/satellite-missions/eutelsat-quantum).

### 5.4 Frequency hopping — the canonical anti-jam technique

Frequency-hopping spread spectrum (FHSS) was patented by Hedy Lamarr and George Antheil in [US Patent 2,292,387 (filed 1941, granted 1942)](https://standards.ieee.org/beyond-standards/hedy-lamarr/) explicitly as an anti-jamming method for torpedo guidance. The principle — pseudo-randomly hopping the carrier across a wide band on a schedule shared between transmitter and receiver — is what makes a barrage or spot jammer expensively inefficient: the jammer must either jam the whole band (huge power budget) or guess the hop sequence. AEHF inherits this lineage directly; Bluetooth and 802.11 FHSS variants inherit the civilian branch. In the engine, FHSS-grade payloads should resist the `barrage` and `spot` modulations in [engine/jam.py](../../spacesim/engine/jam.py) much better than fixed-channel SATCOM.

### 5.5 Beam nulling and electronic beam steering

Modern phased-array SATCOM payloads suppress jammers by adaptively placing nulls in the antenna pattern at the jammer's angle of arrival. Per IEEE MTT, "[silicon-based phased arrays… high gain, electronically steerable patterns, narrow beamwidths, high tolerance to interference and adaptive nulling capabilities](https://resourcecenter.mtt.ieee.org/education/webinars/mtt_edu_web_rebeiz_101425)" are now the norm for protected SATCOM. The state-of-the-art uplink architecture is an array of digital receivers where "[the number of undesirable sources that can be nulled equals one less than the number of digital receivers](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12537566)" — a hard cap that makes the choice of *which* jammer to null a tactical decision. This backs `satcom.mitigate_interference` and explains why a swarm of cheap jammers is a credible threat even against an AEHF-class antenna.

### 5.6 Interference geolocation — TDOA/FDOA cross-correlation

Uplink-jammer geolocation is a ground-side technique: the interfering carrier leaks into the downlink of the target satellite *and* an adjacent satellite, and the two retransmissions are cross-correlated. The [USPTO record](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10972191) describes the canonical chain: "[measurements generated by satellites are filtered and cross-correlated to determine time and frequency differences of arrival used to locate the source](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10444371)" — i.e. TDOA + FDOA. Commercial systems like Kratos satID + Monics fuse this with "[carrier-under-carrier detection… integrating interference geolocation with RF carrier system monitoring](https://arxiv.org/pdf/1805.06567)" so the operator can identify the offending carrier *and* locate its uplink. MAJE is the military instance of the same workflow on WGS.

### 5.7 Mapping verbs to real-world operator actions

Each engine verb in [engine/buscommands.py:PAYLOAD_VERBS](../../spacesim/engine/buscommands.py) corresponds to one of the techniques above: `satcom.mitigate_interference` ≈ adaptive beam nulling + onboard FHSS (AEHF lineage); `satcom.shift_users` ≈ Quantum-style beam reconfiguration + traffic reallocation; `satcom.geolocate_interference` ≈ MAJE / satID-style TDOA-FDOA cross-correlation. Success probability and political cost should track the threat: a barrage jammer is easy to geolocate but hard to null with one receiver; a cooperative-uplink spoof is easy to shift users away from but hard to attribute. The Russian counterspace pattern documented by CSIS — "[repeated attempts to jam Starlink terminals supporting Ukrainian forces](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf)" — and the US offensive analogue documented by SWF — "[L3Harris Counterspace Communications System (CCS), the only acknowledged offensive counterspace capability of the United States, used to attack SATCOM receivers](https://breakingdefense.com/2026/04/as-more-nations-seek-counterspace-chops-gps-jamming-also-rises-report/)" — give the wargame realistic Red-vs-Blue tradeoffs. See [03-counterspace-taxonomy.md §4](03-counterspace-taxonomy.md) (EW) and the jam-modulation database in [engine/jam.py](../../spacesim/engine/jam.py) for the corresponding attacker side.

Used by: [engine/buscommands.py:satcom.mitigate_interference](../../spacesim/engine/buscommands.py), [engine/buscommands.py:satcom.shift_users](../../spacesim/engine/buscommands.py), [engine/buscommands.py:satcom.geolocate_interference](../../spacesim/engine/buscommands.py), and the jam-modulation tradeoffs in [engine/jam.py](../../spacesim/engine/jam.py).

### Sources

- *WGS MAJE Program Successfully Completes Major Testing (LA SF Base)* — [live](https://www.losangeles.spaceforce.mil/News/Article/2507386/wgs-mitigation-and-anti-jam-enhancement-program-successfully-completes-major-te/) · [snapshot](https://web.archive.org/web/2026*/https://www.losangeles.spaceforce.mil/News/Article/2507386/wgs-mitigation-and-anti-jam-enhancement-program-successfully-completes-major-te/) · accessed 2026-06-12.
- *Space Force Tested Geo-Location of Jamming Signals for WGS (Via Satellite)* — [live](https://www.satellitetoday.com/government-military/2021/02/19/space-force-tested-geo-location-of-jamming-signals-for-wgs-satellites/) · [snapshot](https://web.archive.org/web/2026*/https://www.satellitetoday.com/government-military/2021/02/19/space-force-tested-geo-location-of-jamming-signals-for-wgs-satellites/) · accessed 2026-06-12.
- *Space Force says new anti-jamming upgrade coming in 2022 (Defense News)* — [live](https://www.defensenews.com/battlefield-tech/space/2021/02/18/space-force-says-new-anti-jamming-upgrade-coming-in-2022/) · [snapshot](https://web.archive.org/web/2026*/https://www.defensenews.com/battlefield-tech/space/2021/02/18/space-force-says-new-anti-jamming-upgrade-coming-in-2022/) · accessed 2026-06-12.
- *AEHF System — USSF Fact Sheet* — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197713/advanced-extremely-high-frequency-system/) · [snapshot](https://web.archive.org/web/2026*/https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197713/advanced-extremely-high-frequency-system/) · accessed 2026-06-12.
- *AEHF Factsheet (DoD media)* — [live](https://media.defense.gov/2022/Apr/08/2002973439/-1/-1/1/AEHF%20FACTSHEET.PDF) · [snapshot](https://web.archive.org/web/2026*/https://media.defense.gov/2022/Apr/08/2002973439/-1/-1/1/AEHF%20FACTSHEET.PDF) · accessed 2026-06-12.
- *Airbus-built EUTELSAT QUANTUM shipped to launch site (Airbus press release)* — [live](https://www.airbus.com/en/newsroom/press-releases/2021-06-airbus-built-eutelsat-quantum-satellite-shipped-to-launch-site) · [snapshot](https://web.archive.org/web/2026*/https://www.airbus.com/en/newsroom/press-releases/2021-06-airbus-built-eutelsat-quantum-satellite-shipped-to-launch-site) · accessed 2026-06-12.
- *Eutelsat Quantum mission page (ESA eoPortal)* — [live](https://www.eoportal.org/satellite-missions/eutelsat-quantum) · [snapshot](https://web.archive.org/web/2026*/https://www.eoportal.org/satellite-missions/eutelsat-quantum) · accessed 2026-06-12.
- *Hedy Lamarr and the IEEE — frequency hopping history (IEEE SA)* — [live](https://standards.ieee.org/beyond-standards/hedy-lamarr/) · [snapshot](https://web.archive.org/web/2026*/https://standards.ieee.org/beyond-standards/hedy-lamarr/) · accessed 2026-06-12.
- *Silicon-Based Phased Arrays and Their Impact on SATCOM (IEEE MTT webinar)* — [live](https://resourcecenter.mtt.ieee.org/education/webinars/mtt_edu_web_rebeiz_101425) · [snapshot](https://web.archive.org/web/2026*/https://resourcecenter.mtt.ieee.org/education/webinars/mtt_edu_web_rebeiz_101425) · accessed 2026-06-12.
- *Radio system using phase-reconfigurable reflectarray for adaptive beamforming (US Patent 12,537,566)* — [live](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12537566) · [snapshot](https://web.archive.org/web/2026*/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12537566) · accessed 2026-06-12.
- *Uplink interference geolocation method (US Patent 10,972,191)* — [live](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10972191) · [snapshot](https://web.archive.org/web/2026*/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10972191) · accessed 2026-06-12.
- *Interference geolocation using a satellite constellation (US Patent 10,444,371)* — [live](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10444371) · [snapshot](https://web.archive.org/web/2026*/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10444371) · accessed 2026-06-12.
- *Identification of source of interferer via known carriers using a single satellite (arXiv 1805.06567)* — [live](https://arxiv.org/pdf/1805.06567) · [snapshot](https://web.archive.org/web/2026*/https://arxiv.org/pdf/1805.06567) · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2024 (Swope & Bingen)* — [live](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) · [snapshot](https://web.archive.org/web/2026*/https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) · accessed 2026-06-12.
- *SWF 2026 Counterspace report — CCS jammer (Breaking Defense)* — [live](https://breakingdefense.com/2026/04/as-more-nations-seek-counterspace-chops-gps-jamming-also-rises-report/) · [snapshot](https://web.archive.org/web/2026*/https://breakingdefense.com/2026/04/as-more-nations-seek-counterspace-chops-gps-jamming-also-rises-report/) · accessed 2026-06-12.
## 6. Payload ops — ISR (EO/IR optical + SAR radar)

ISR (Intelligence, Surveillance, Reconnaissance) payloads are the simulator's primary
sensing channel for ground- and air-target custody. Operators don't "look" — they *task* a
collect against an access window, then wait for the bits to flow through processing and
arrive at an analyst as a usable image. This subsection captures the doctrinal cycle, the
phenomenology split (optical vs. radar), the standard scoring (NIIRS), and the commercial
tasking timelines that anchor the engine's beam-mode and ordering math.

### 6.1 TPED — the canonical ISR ops cycle

US joint and Air Force doctrine treats ISR as a synchronised loop of **Tasking →
Processing → Exploitation → Dissemination** (TPED), embedded inside the broader
intelligence cycle of planning → collection → processing/exploitation → analysis/production
→ dissemination/integration → evaluation. The Joint Chiefs of Staff
[ISR white paper](https://www.jcs.mil/Portals/36/Documents/Doctrine/concepts/cjcs_wp_isr.pdf?ver=2017-12-28-162054-447)
defines ISR as the "synchronized and integrated planning and operation of sensors…and
processing, exploitation, and dissemination systems in direct support of current and
future operations" — i.e. PED is *part of* ISR, not a downstream afterthought.
[AFDP 2-0 (Intelligence)](https://www.doctrine.af.mil/Portals/61/documents/AFDP_2-0/2-0-AFDP-INTELLIGENCE.pdf)
spells out the airborne-ISR PED requirement and the AOD's PED guidance for platform
employment, while the JCS
[Intelligence Operations focal-point primer](https://www.jcs.mil/Portals/36/Documents/Doctrine/fp/intell_ops_fp.pdf)
gives the full joint cycle that TPED subsumes. The engine models the **T** explicitly
(orders schedule a collect against an access window) and abstracts P/E/D into a
deterministic delay between collection and a `Track` update.

### 6.2 NIIRS — the 0-9 interpretability scale

Image *quality* is reported on the **National Imagery Interpretability Rating Scale**
(NIIRS), a 0-9 task-based scale where 0 is uninterpretable and 9 corresponds to
sub-10cm detail. The FAS-hosted
[NIIRS reference](https://irp.fas.org/imint/niirs.htm) and
[Civil NIIRS Reference Guide](https://irp.fas.org/imint/niirs_c/guide.htm) enumerate the
criterion tasks at each level across visible, IR, radar, and multispectral scales (e.g.
"identify automobiles as sedan/station-wagon" at NIIRS 6). Irvine's SPIE methodology
paper,
[*NIIRS: Overview and Methodology*](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/3128/0000/National-imagery-interpretability-rating-scales-NIIRS-overview-and-methodology/10.1117/12.279081.short),
explains *why* GSD alone fails to predict interpretability — sensor MTF, SNR, and
exploitation context all matter — which is exactly why the engine's `gain_factor` per
beam-mode (not GSD) drives custody confidence.

### 6.3 EO/IR vs SAR — geometry vs. all-weather

The two ISR phenomenologies model very differently. EO/IR is passive optical, so it
needs sunlit, cloud-free targets: Maxar's operational tasking docs
([Placing a WorldView 2D Tasking Request: EO](https://pro-docs.maxar.com/en-us/Tasking/Tasking_requests_EO.htm))
expose this directly — orders carry a cloud-cover threshold (default <15%, capped 50%)
and a sun-elevation minimum. SAR is *active* RF, so it images through cloud and at
night: Capella's primer
[SAR 101](https://www.capellaspace.com/resources/sar-101-an-introduction-to-synthetic-aperture-radar)
describes SAR penetrating "clouds, fog, darkness, and smoke";
[NASA Earthdata](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar)
states the same — SAR is an active sensor that "produces high resolution imagery night
or day, regardless of weather conditions." ESA's
[Sentinel-1 mission page](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1)
gives the third independent confirmation: C-band SAR delivers "all-weather,
day-and-night" imagery. The simulator therefore lets a SAR pass complete in eclipse or
under weather injects where an EO pass cannot.

### 6.4 Beam modes — survey vs. spot

Both EO and SAR trade swath against resolution via *beam mode*. Capella's
[collect-mode catalogue](https://support.capellaspace.com/what-are-capellas-collect-modes)
documents the canonical SAR trio — **Stripmap** (continuous strip, lower-res, much
longer image), **Sliding Spotlight** (better area coverage than spotlight at slightly
reduced resolution), and **Spotlight** (0.5m, ~5×5km footprint) — plus Spotlight Ultra
(0.25m). ESA's
[Sentinel-1 Acquisition Modes](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/acquisition-modes)
quantifies the wide-area end (Interferometric Wide 250km / 5×20m, Extra Wide 400km /
20×40m). This is exactly the structure carried by
[engine/isr.py:BEAM_MODES](../../spacesim/engine/isr.py) (line 27): per-payload-class
× beam-mode dict with `swath_km`, `resolution_m`, `power_factor`, `duty_cycle`,
`gain_factor`. [engine/isr.py:effective_gain](../../spacesim/engine/isr.py) (line 77)
applies the cosine off-nadir penalty and the per-mode gain multiplier;
[engine/isr.py:soc_drain](../../spacesim/engine/isr.py) (line 89) scales battery draw
by `power_factor × duration / 300s`, so a spotlight pass costs ~2.5× a stripmap pass —
matching Capella's higher-duty thermal limit.

### 6.5 Commercial tasking timelines — and the government gap

Commercial tasking SLAs have collapsed from days to sub-hour at the priority tier.
Maxar's [Rapid Access Program](https://www.maxar.com/products/rapid-access-program)
gives customers priority tasking across the WorldView constellation with delivery
within hours of collection (the
[data sheet](https://resources.maxar.com/rapid-access-program/rapid-access-program-data-sheet)
advertises image delivery as fast as ~15 minutes via cloud-connected ground stations).
Planet's [Tasking API docs](https://developers.planet.com/docs/tasking/basics/)
documents Standard vs. Fast Track delivery for SkySat/Pelican, with Pelican targeting
sub-four-hour delivery from capture. Capella's
[Collection Tiers](https://support.capellaspace.com/hc/en-us/articles/360059287311-What-are-Capella-s-Collection-Tiers)
defines five SAR tiers — **Urgent, Priority, Standard, Flexible, Routine** — with
sub-24h (and sub-hour) Window Close times and a scheduler that runs every 20 minutes
on a one-week horizon. The government side is harder to publish openly:
[GAO-23-106042](https://www.gao.gov/products/gao-23-106042) inventories federal
commercial-imagery contracts and explicitly names "needed revisit rates, rapid tasking,
resolution, or wavelengths outside the visible spectrum" as the drivers — i.e. NRO/NGA
buy commercial *to fill responsiveness gaps* national systems can't, while CSIS
[*Commercial Space Remote Sensing and Its Role in National Security*](https://aerospace.csis.org/commercial-space-remote-sensing-and-its-role-in-national-security/)
cites BlackSky's sub-90-minute global revisit against the orbital-mechanics baseline
of "hours or days" between passes. The engine models this gap as a tiered scheduling
delay on `isr.schedule_collection` and an immediate-but-window-gated path on
`isr.collect_now` ([engine/buscommands.py:PAYLOAD_VERBS](../../spacesim/engine/buscommands.py)
line 33). See [03-counterspace-taxonomy.md §3](03-counterspace-taxonomy.md) for the
matching ISR-denial counters (EO dazzle, SAR jam, optical-window weather injects).

### Sources

- *AFDP 2-0, Intelligence (US Air Force)* — [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_2-0/2-0-AFDP-INTELLIGENCE.pdf) · [snapshot](https://web.archive.org/web/2026*/https://www.doctrine.af.mil/Portals/61/documents/AFDP_2-0/2-0-AFDP-INTELLIGENCE.pdf) · accessed 2026-06-12.
- *JCS Intelligence Operations focal-point primer* — [live](https://www.jcs.mil/Portals/36/Documents/Doctrine/fp/intell_ops_fp.pdf) · [snapshot](https://web.archive.org/web/2026*/https://www.jcs.mil/Portals/36/Documents/Doctrine/fp/intell_ops_fp.pdf) · accessed 2026-06-12.
- *CJCS ISR White Paper* — [live](https://www.jcs.mil/Portals/36/Documents/Doctrine/concepts/cjcs_wp_isr.pdf?ver=2017-12-28-162054-447) · [snapshot](https://web.archive.org/web/2026*/https://www.jcs.mil/Portals/36/Documents/Doctrine/concepts/cjcs_wp_isr.pdf) · accessed 2026-06-12.
- *FAS IMINT NIIRS reference* — [live](https://irp.fas.org/imint/niirs.htm) · [snapshot](https://web.archive.org/web/2026*/https://irp.fas.org/imint/niirs.htm) · accessed 2026-06-12.
- *Civil NIIRS Reference Guide (FAS)* — [live](https://irp.fas.org/imint/niirs_c/guide.htm) · [snapshot](https://web.archive.org/web/2026*/https://irp.fas.org/imint/niirs_c/guide.htm) · accessed 2026-06-12.
- *Irvine, NIIRS: Overview and Methodology, SPIE 3128 (1997)* — [live](https://www.spiedigitallibrary.org/conference-proceedings-of-spie/3128/0000/National-imagery-interpretability-rating-scales-NIIRS-overview-and-methodology/10.1117/12.279081.short) · [snapshot](https://web.archive.org/web/2026*/https://www.spiedigitallibrary.org/conference-proceedings-of-spie/3128/0000/National-imagery-interpretability-rating-scales-NIIRS-overview-and-methodology/10.1117/12.279081.short) · accessed 2026-06-12.
- *Capella SAR 101 primer* — [live](https://www.capellaspace.com/resources/sar-101-an-introduction-to-synthetic-aperture-radar) · [snapshot](https://web.archive.org/web/2026*/https://www.capellaspace.com/resources/sar-101-an-introduction-to-synthetic-aperture-radar) · accessed 2026-06-12.
- *NASA Earthdata — Synthetic Aperture Radar* — [live](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar) · [snapshot](https://web.archive.org/web/2026*/https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar) · accessed 2026-06-12.
- *ESA Sentinel-1 mission page* — [live](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1) · [snapshot](https://web.archive.org/web/2026*/https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1) · accessed 2026-06-12.
- *Maxar — Placing a WorldView 2D Tasking Request: EO* — [live](https://pro-docs.maxar.com/en-us/Tasking/Tasking_requests_EO.htm) · [snapshot](https://web.archive.org/web/2026*/https://pro-docs.maxar.com/en-us/Tasking/Tasking_requests_EO.htm) · accessed 2026-06-12.
- *Capella — What are Capella's collect modes?* — [live](https://support.capellaspace.com/what-are-capellas-collect-modes) · [snapshot](https://web.archive.org/web/2026*/https://support.capellaspace.com/what-are-capellas-collect-modes) · accessed 2026-06-12.
- *Sentinel-1 SAR — Acquisition Modes (ESA)* — [live](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/acquisition-modes) · [snapshot](https://web.archive.org/web/2026*/https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/acquisition-modes) · accessed 2026-06-12.
- *Maxar Rapid Access Program* — [live](https://www.maxar.com/products/rapid-access-program) · [snapshot](https://web.archive.org/web/2026*/https://www.maxar.com/products/rapid-access-program) · accessed 2026-06-12.
- *Maxar Rapid Access Program Data Sheet* — [live](https://resources.maxar.com/rapid-access-program/rapid-access-program-data-sheet) · [snapshot](https://web.archive.org/web/2026*/https://resources.maxar.com/rapid-access-program/rapid-access-program-data-sheet) · accessed 2026-06-12.
- *Planet Tasking API documentation* — [live](https://developers.planet.com/docs/tasking/basics/) · [snapshot](https://web.archive.org/web/2026*/https://developers.planet.com/docs/tasking/basics/) · accessed 2026-06-12.
- *Capella Collection Tiers* — [live](https://support.capellaspace.com/hc/en-us/articles/360059287311-What-are-Capella-s-Collection-Tiers) · [snapshot](https://web.archive.org/web/2026*/https://support.capellaspace.com/hc/en-us/articles/360059287311-What-are-Capella-s-Collection-Tiers) · accessed 2026-06-12.
- *GAO-23-106042 — National Security Space: Overview of Contracts for Commercial Satellite Imagery* — [live](https://www.gao.gov/products/gao-23-106042) · [snapshot](https://web.archive.org/web/2026*/https://www.gao.gov/products/gao-23-106042) · accessed 2026-06-12.
- *CSIS — Commercial Space Remote Sensing and Its Role in National Security* — [live](https://aerospace.csis.org/commercial-space-remote-sensing-and-its-role-in-national-security/) · [snapshot](https://web.archive.org/web/2026*/https://aerospace.csis.org/commercial-space-remote-sensing-and-its-role-in-national-security/) · accessed 2026-06-12.

Used by: [engine/isr.py:BEAM_MODES](../../spacesim/engine/isr.py), [engine/isr.py:effective_gain](../../spacesim/engine/isr.py), [engine/isr.py:soc_drain](../../spacesim/engine/isr.py), [engine/buscommands.py:PAYLOAD_VERBS](../../spacesim/engine/buscommands.py) (`isr.collect_now`, `isr.schedule_collection`, `isr.set_mode`), [engine/orders.py](../../spacesim/engine/orders.py) (`observe` action).
## 7. Payload ops — combined (SIGINT, SDA, Space-control, PNT, Missile-warning, Weather)

### 7.1 SIGINT
Space SIGINT collects comms/radar emissions from orbit. The NRO-operated GEO ELINT/COMINT class (Mentor/Orion) is the textbook anchor — [GEO platforms intercept UHF/VHF comms while LEO/MEO collectors pick up air-defence and early-warning radars](https://www.globalsecurity.org/space/systems/sigint.htm); the [Orion family of geosynchronous SIGINT spacecraft has been operated by the NRO since 1995](https://en.wikipedia.org/wiki/Orion_(satellite)).
Dual-satellite TDOA/FDOA is the standard geolocation: [accuracy is bounded by the Cramér–Rao lower bound, degrading with range/SNR](https://ieeexplore.ieee.org/document/5339159/), and the [dual-LEO/HEO TDOA+FDOA formulation](https://ieeexplore.ieee.org/document/8042318) shows error scaling roughly as 1/(SNR × dwell × baseline-projected-velocity). The simulator codifies this in [engine/sigint.py:geolocation_error_km](../../spacesim/engine/sigint.py) (√dwell × √N collectors × atmospheric loss) and the per-band SNR table in [engine/sigint.py:band_params](../../spacesim/engine/sigint.py).

### 7.2 SDA
U.S. SDA flows through the [18th Space Defense Squadron at Vandenberg, executing USSPACECOM's SDA mission and running the Space Surveillance Network](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/), publishing the catalogue of ~16,000 tracked objects via [Space-Track.org, hosted by 18 SDS](https://www.space-track.org/documentation). Products include launch detection, conjunction assessment, manoeuvre detection, and re-entry forecasting.
Conjunction warnings ride a standardised wire format: [CCSDS 508.0-B-1, the Conjunction Data Message Blue Book](https://ccsds.org/Pubs/508x0b1e2c2.pdf), defines KVN/XML/JSON encodings carrying object state, covariance, and miss-distance per screening event — the same shape adopted by NOAA's [TraCSS CDM specification](https://space.commerce.gov/wp-content/uploads/2025/07/TraCSS-_CDM_Spec_Version_2.1.pdf). The simulator's mock catalogue + request-driven collection model lives in [engine/ssn.py](../../spacesim/engine/ssn.py).

### 7.3 Space-control / Co-orbital RPO
Co-orbital RPO is the most-watched space-control thread: the [CSIS Space Threat Assessment 2024 chronicles Russia's Kosmos-2542/2543 deploy and shadowing of USA-245, plus China's SJ-17 and SJ-21 GEO RPO — including SJ-21 grappling a defunct Beidou into a graveyard orbit](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf). The Western analogue is USSF's [Geosynchronous Space Situational Awareness Program (GSSAP), a dedicated near-GEO SSN element operating at ~35,970 km to characterise other objects via manoeuvre and close inspection](https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197772/geosynchronous-space-situational-awareness-program/).
GSSAP anchors the simulator's RPO/inspect tasking — operators plan a phasing burn, drift, and station-keep relative to a target, all gated by the window/contact logic in [engine/orders.py](../../spacesim/engine/orders.py) (`maneuver` + `observe`). The reversible-effect taxonomy is in [03-counterspace-taxonomy.md §5](03-counterspace-taxonomy.md).

### 7.4 PNT
GPS's space ↔ user air interface is fixed by [IS-GPS-200, the Navstar GPS Interface Specification covering L1/L2 RF links, navigation message, and signal structure](https://www.gps.gov/technical/icwg/IS-GPS-200K.pdf), maintained by the Navstar GPS Joint Program Office. The military M-code signal — designed to operate through jamming via spot-beam high-power delivery and spectrally-separated PRN — is the live PNT-flex lever operators care about.
Ground modernisation has been chronic: the [GAO's 2024 GPS Modernisation report tracks Next-Generation OCX delays and the M-code user-equipment fielding gap](https://www.gao.gov/assets/gao-24-106841.pdf), with OCX Blocks 1+2 completing qualification testing only in December 2023. The simulator surfaces the flex-power lever via [engine/buscommands.py:PAYLOAD_VERBS](../../spacesim/engine/buscommands.py) (`pnt.flex_power`).

### 7.5 Missile Warning
The current U.S. missile-warning constellation is SBIRS: [a GEO + HEO infrared system that follows DSP, providing missile warning, missile defence, battlespace characterisation, and technical intelligence](https://www.spaceforce.mil/about-us/fact-sheets/article/2197746/space-based-infrared-system/), with scanning and staring sensors that survey large theatres and zoom on a tactical area of interest. SBIRS GEO-6 closed the GEO series in 2022.
Its successor Next-Gen OPIR is the subject of [multiple GAO assessments warning about schedule and cost risk on the GEO and Polar segments](https://www.gao.gov/products/gao-21-105249), with first GEO launch now NET 2026. The simulator's stare/scan tasking maps to [engine/buscommands.py:PAYLOAD_VERBS](../../spacesim/engine/buscommands.py) (`mw.add_stare_area`): operator hands the payload a polygon + revisit cadence rather than a per-frame steer.

### 7.6 Weather
NOAA's two operational weather constellations anchor the wx verb. GEO coverage comes from the [GOES-R Series, whose Advanced Baseline Imager (ABI) scans 16 spectral bands and runs a 10-minute full-disk / 5-minute CONUS / 1-minute mesoscale flex schedule](https://www.goes-r.gov/spacesegment/abi.html). Polar/global coverage comes from [NOAA's Joint Polar Satellite System (NOAA-20/JPSS-1, NOAA-21/JPSS-2), pole-to-pole 14× daily with VIIRS, ATMS, CrIS, and CERES payloads](https://www.nesdis.noaa.gov/our-satellites/currently-flying/joint-polar-satellite-system).
The operator-meaningful action is *sector tasking* — a polygon + revisit + band tuple consumed by the next contact — which is what [engine/buscommands.py:PAYLOAD_VERBS](../../spacesim/engine/buscommands.py) (`wx.request_sector`) models.

### Sources
- *SIGINT from Space (GlobalSecurity overview)* — [live](https://www.globalsecurity.org/space/systems/sigint.htm) · [snapshot](https://web.archive.org/web/2026*/https://www.globalsecurity.org/space/systems/sigint.htm) · accessed 2026-06-12.
- *Orion / Mentor NRO SIGINT class* — [live](https://en.wikipedia.org/wiki/Orion_(satellite)) · [snapshot](https://web.archive.org/web/2026*/https://en.wikipedia.org/wiki/Orion_(satellite)) · accessed 2026-06-12.
- *Mobile Emitter Geolocation Using TDOA and FDOA (IEEE)* — [live](https://ieeexplore.ieee.org/document/5339159/) · [snapshot](https://web.archive.org/web/2026*/https://ieeexplore.ieee.org/document/5339159/) · accessed 2026-06-12.
- *Dual-Satellite Geolocation Based on TDOA and FDOA (IEEE/Wiley)* — [live](https://ieeexplore.ieee.org/document/8042318) · [snapshot](https://web.archive.org/web/2026*/https://ieeexplore.ieee.org/document/8042318) · accessed 2026-06-12.
- *18th Space Defense Squadron fact sheet (USSF)* — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/) · [snapshot](https://web.archive.org/web/2026*/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/) · accessed 2026-06-12.
- *Space-Track.org documentation* — [live](https://www.space-track.org/documentation) · [snapshot](https://web.archive.org/web/2026*/https://www.space-track.org/documentation) · accessed 2026-06-12.
- *CCSDS 508.0-B-1 Conjunction Data Message Blue Book* — [live](https://ccsds.org/Pubs/508x0b1e2c2.pdf) · [snapshot](https://web.archive.org/web/2026*/https://ccsds.org/Pubs/508x0b1e2c2.pdf) · accessed 2026-06-12.
- *TraCSS CDM Specification v2.1 (NOAA Office of Space Commerce)* — [live](https://space.commerce.gov/wp-content/uploads/2025/07/TraCSS-_CDM_Spec_Version_2.1.pdf) · [snapshot](https://web.archive.org/web/2026*/https://space.commerce.gov/wp-content/uploads/2025/07/TraCSS-_CDM_Spec_Version_2.1.pdf) · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2024* — [live](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) · [snapshot](https://web.archive.org/web/2026*/https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) · accessed 2026-06-12.
- *GSSAP fact sheet (USSF)* — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197772/geosynchronous-space-situational-awareness-program/) · [snapshot](https://web.archive.org/web/2026*/https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197772/geosynchronous-space-situational-awareness-program/) · accessed 2026-06-12.
- *IS-GPS-200K (gps.gov)* — [live](https://www.gps.gov/technical/icwg/IS-GPS-200K.pdf) · [snapshot](https://web.archive.org/web/2026*/https://www.gps.gov/technical/icwg/IS-GPS-200K.pdf) · accessed 2026-06-12.
- *GAO-24-106841 GPS Modernization* — [live](https://www.gao.gov/assets/gao-24-106841.pdf) · [snapshot](https://web.archive.org/web/2026*/https://www.gao.gov/assets/gao-24-106841.pdf) · accessed 2026-06-12.
- *SBIRS fact sheet (USSF)* — [live](https://www.spaceforce.mil/about-us/fact-sheets/article/2197746/space-based-infrared-system/) · [snapshot](https://web.archive.org/web/2026*/https://www.spaceforce.mil/about-us/fact-sheets/article/2197746/space-based-infrared-system/) · accessed 2026-06-12.
- *GAO-21-105249 Missile Warning Satellites* — [live](https://www.gao.gov/products/gao-21-105249) · [snapshot](https://web.archive.org/web/2026*/https://www.gao.gov/products/gao-21-105249) · accessed 2026-06-12.
- *GOES-R ABI program page (NOAA/NESDIS)* — [live](https://www.goes-r.gov/spacesegment/abi.html) · [snapshot](https://web.archive.org/web/2026*/https://www.goes-r.gov/spacesegment/abi.html) · accessed 2026-06-12.
- *JPSS program page (NOAA/NESDIS)* — [live](https://www.nesdis.noaa.gov/our-satellites/currently-flying/joint-polar-satellite-system) · [snapshot](https://web.archive.org/web/2026*/https://www.nesdis.noaa.gov/our-satellites/currently-flying/joint-polar-satellite-system) · accessed 2026-06-12.

Used by: [engine/sigint.py](../../spacesim/engine/sigint.py), [engine/ssn.py](../../spacesim/engine/ssn.py), [engine/orders.py](../../spacesim/engine/orders.py), [engine/buscommands.py](../../spacesim/engine/buscommands.py).
## 8. Real operator interfaces — what the simulator's drill-down panel copies from

The simulator's fleet rail + per-asset drill-down + per-subsystem telemetry sparklines + per-subsystem command-verb buttons is not an arbitrary UI choice — it is a deliberate copy of the **operator-console grammar** that has stabilized across institutional and commercial mission-operations software over the last two decades. This subsection surveys the six systems whose UI conventions inform the simulator's [`spacesim/ui_web/static/app.js`](../../spacesim/ui_web/static/app.js) drill-down and its [`engine/telemetry.py:PARAMS`](../../spacesim/engine/telemetry.py) 19-channel sparkline registry, so the pedagogical mapping is auditable against the real interfaces a PME trainee will see on assignment.

### 8.1 ESA SCOS-2000 — the institutional reference

[SCOS-2000](https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf) is the **ESA Generic Mission Control System**, fielded on virtually every ESA spacecraft launched after MSG-1 (Aug 2002) including XMM-Newton, Rosetta, Mars Express, GAIA, and the Sentinel Copernicus series — the [ESA Bulletin 108 article on SCOS-2000](https://www.esa.int/esapub/bulletin/bullet108/chapter8_bul108.pdf) is the agency's own primary-source description. Its out-of-limit checking, status reporting, event-logging, and per-parameter trend-plot panels are the canonical reference every later commercial console copied. SCOS-2000's successor is the [ESA EGS-CC (European Ground Systems Common Core)](https://egscc.esa.int/), the cross-agency M&C infrastructure intended to unify ESA institutional ground systems going forward.

### 8.2 NASA Open MCT — the open-source plug-in console

[Open MCT (Open Mission Control Technologies)](https://github.com/nasa/openmct) is the open-source mission-control framework developed at NASA Ames Research Center; the [NASA Software Catalog entry ARC-15256-1D](https://software.nasa.gov/software/ARC-15256-1D) confirms its Ames provenance and describes its use as a next-generation mission-control framework for spacecraft data analysis. The framework's hierarchical "domain object" tree (fleet → spacecraft → subsystem → parameter) and its plot-based telemetry views are the open-source reference the simulator's fleet rail and per-subsystem drill-down most closely resemble — Open MCT is the system a PME trainee is most likely to be able to inspect and run themselves.

### 8.3 L3Harris InControl — the commercial constellation console

[L3Harris InControl](https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control) is the commercial mission-operations C2 system whose product description explicitly advertises a *constellation view with one-click drill-down to assess individual satellite performance* — exactly the fleet-rail-to-per-asset-drill-down pattern the simulator copies. The [L3Harris InControl sell sheet](https://www.l3harris.com/sites/default/files/2020-09/l3harris-InControl_SellSheet_FINAL_web-sas.pdf) documents telemetry processing, command procedure execution, payload management, and ground-equipment monitoring; commercial users include Sidus Space's LizzieSat constellation.

### 8.4 GMV Hifly — the European commercial standard

[GMV Hifly](https://www.gmv.com/en/products/space/hifly) is the dominant European commercial satellite monitoring & control system, with ~1,000 combined operator-years across Eutelsat, Arabsat, Hispasat, StarOne, SES (since 2004), Turksat, Measat, and OneWeb fleets, spanning GEO commercial telecom heritage through OneWeb LEO constellations. Its industry-leading telemetry-archive retrieval performance (one year of TM in <5 s) is the production benchmark for the per-parameter sparkline overlays the simulator's [`graph.js`](../../spacesim/ui_web/static/graph.js) draws against the live telemetry stream.

### 8.5 Kratos OpenSpace — the cloud-native platform

[Kratos OpenSpace](https://www.kratosdefense.com/systems-and-platforms/space-systems/dynamic-ground/platform) is the cloud-native, software-defined satellite ground platform built as orchestrated VNFs on commodity x86 (no FPGA/GPU), marketed as the *industry's only commercially available, fully orchestrated* multi-mission ground system. Named users include Intelsat (next-gen network), SSC Space (Go LEO service), and the U.S. Army Futures Command virtualized-SATCOM demonstration over SES O3b MEO. OpenSpace is the reference for the simulator's architectural decision to keep the engine UI-agnostic — the fleet view is the UI-layer rendering of an underlying data-centric session API, not a hard-wired display.

### 8.6 RTI Connext DDS — the real-time data bus

[RTI Connext DDS](https://www.rti.com/products/dds-standard) is the production implementation of the [OMG Data Distribution Service v1.4 specification](https://www.omg.org/spec/DDS/1.4/About-DDS) — the data-centric publish-subscribe (DCPS) standard that defines QoS semantics for high-throughput real-time telemetry distribution across operator workstations. RTI Connext is a core component of NASA Artemis 1's Spacecraft Command and Control System (SCCS) and is used by ESA aboard the ISS, establishing DDS as the canonical real-time data-bus pattern that any production mission-control console — and any future multi-monitor pop-out in the simulator's P8 LAN multiplayer layer — would adopt to fan out per-cell telemetry views at scale.

### 8.7 Pedagogical mapping — what the simulator deliberately copies

The simulator's drill-down panel ([`spacesim/ui_web/static/app.js`](../../spacesim/ui_web/static/app.js)) renders a fleet rail (constellation overview, à la InControl) → per-asset drill-down (per-spacecraft view) → per-subsystem cards carrying both a traffic-light SOH rollup (SCOS-2000 / InControl pattern from §1.6.2) **and** the per-subsystem command verbs (the operator's "what can I do about this?" buttons). Each card carries a per-subsystem telemetry sparkline drawn by [`graph.js`](../../spacesim/ui_web/static/graph.js) against the 19 channels declared in [`engine/telemetry.py:PARAMS`](../../spacesim/engine/telemetry.py) — directly analogous to the per-parameter trend plots in SCOS-2000 and the plot views in Open MCT. The point of mirroring this grammar exactly is that a PME trainee who has been taught the simulator's drill-down has been taught the *transferable* mental model — the fleet → asset → subsystem → parameter hierarchy and the SOH-plus-verb panel — they will encounter on any operational console they sit in front of after assignment.

Used by: [`spacesim/ui_web/static/app.js`](../../spacesim/ui_web/static/app.js) (fleet rail + per-asset drill-down + per-subsystem cards + command-verb buttons); [`spacesim/ui_web/static/graph.js`](../../spacesim/ui_web/static/graph.js) (per-parameter sparklines); [`engine/telemetry.py:PARAMS`](../../spacesim/engine/telemetry.py) (the 19-channel ParamSpec registry the sparklines render); cross-link to §1.6.2 (SOH traffic-light discipline, where SCOS-2000 + InControl are first cited as the institutional and commercial references).

### Sources

- *Peccia, "SCOS-2000 — ESA's Spacecraft Control for the 21st Century"* (Ground System Architectures Workshop 2003 — the canonical SCOS-2000 reference paper) — [live](https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf) · [snapshot](https://web.archive.org/web/2026*/https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf) · accessed 2026-06-12.
- *ESA Bulletin 108 — "The SCOS-2000 Example"* (ESA's own primary-source description of SCOS-2000 as its Generic Mission Control System) — [live](https://www.esa.int/esapub/bulletin/bullet108/chapter8_bul108.pdf) · [snapshot](https://web.archive.org/web/2026*/https://www.esa.int/esapub/bulletin/bullet108/chapter8_bul108.pdf) · accessed 2026-06-12.
- *ESA EGS-CC — European Ground Systems Common Core* (official ESA project site for SCOS-2000's successor cross-agency M&C infrastructure) — [live](https://egscc.esa.int/) · [snapshot](https://web.archive.org/web/2026*/https://egscc.esa.int/) · accessed 2026-06-12.
- *NASA Open MCT — nasa/openmct on GitHub* (official NASA repository, Ames Research Center, next-gen mission-control framework) — [live](https://github.com/nasa/openmct) · [snapshot](https://web.archive.org/web/2026*/https://github.com/nasa/openmct) · accessed 2026-06-12.
- *NASA Software Catalog — Open Mission Control Technologies (ARC-15256-1D)* (NASA Software Catalog entry confirming Ames provenance) — [live](https://software.nasa.gov/software/ARC-15256-1D) · [snapshot](https://web.archive.org/web/2026*/https://software.nasa.gov/software/ARC-15256-1D) · accessed 2026-06-12.
- *L3Harris InControl — Satellite Command and Control* (commercial mission-ops C2 product page; constellation view + per-spacecraft drill-down + per-subsystem SOH) — [live](https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control) · [snapshot](https://web.archive.org/web/2026*/https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control) · accessed 2026-06-12.
- *L3Harris InControl Sell Sheet* (InControl capability summary PDF) — [live](https://www.l3harris.com/sites/default/files/2020-09/l3harris-InControl_SellSheet_FINAL_web-sas.pdf) · [snapshot](https://web.archive.org/web/2026*/https://www.l3harris.com/sites/default/files/2020-09/l3harris-InControl_SellSheet_FINAL_web-sas.pdf) · accessed 2026-06-12.
- *GMV Hifly* (official GMV product page for the Hifly satellite monitoring & control system; Eutelsat / SES / OneWeb / Hispasat / Arabsat / Turksat / Measat users) — [live](https://www.gmv.com/en/products/space/hifly) · [snapshot](https://web.archive.org/web/2026*/https://www.gmv.com/en/products/space/hifly) · accessed 2026-06-12.
- *Kratos OpenSpace Platform* (cloud-native software-defined satellite ground platform; Intelsat / SSC Space / U.S. Army Futures Command users) — [live](https://www.kratosdefense.com/systems-and-platforms/space-systems/dynamic-ground/platform) · [snapshot](https://web.archive.org/web/2026*/https://www.kratosdefense.com/systems-and-platforms/space-systems/dynamic-ground/platform) · accessed 2026-06-12.
- *RTI Connext DDS — DDS Standard product page* (Real-Time Innovations' production implementation of OMG DDS; NASA Artemis 1 SCCS + ESA ISS use) — [live](https://www.rti.com/products/dds-standard) · [snapshot](https://web.archive.org/web/2026*/https://www.rti.com/products/dds-standard) · accessed 2026-06-12.
- *OMG Data Distribution Service (DDS) v1.4 specification* (Object Management Group standards page; data-centric publish-subscribe APIs and QoS semantics) — [live](https://www.omg.org/spec/DDS/1.4/About-DDS) · [snapshot](https://web.archive.org/web/2026*/https://www.omg.org/spec/DDS/1.4/About-DDS) · accessed 2026-06-12.
## 9. Live modeling gaps — the three TT&C audit follow-ups

The June 2026 TT&C audit ([`docs/AUDIT-2026-06-UI-TTC.md`](../AUDIT-2026-06-UI-TTC.md) §2 "Other SOH findings") flagged three subsystem-state fields that are declared on the bus model but never integrated by the simulation loop. Each is grounded below in the engineering standard that defines the missing equation, so the fix is anchored in primary sources.

### 9.1 Dead `power_w` field

`AssetResources.power_w` (e.g. 1500 W on vignette-1 buses) is declared on [`engine/entities.py:AssetResources`](../../spacesim/engine/entities.py) but never read by the bus model — [`engine/bus.py:advance_bus`](../../spacesim/engine/bus.py) uses the abstract `charge_rate_per_s` instead. The canonical fix is to derive `charge_rate_per_s` from solar-array end-of-life power (W) divided by battery capacity (Wh), the standard SMAD Chapter 11 power-budget chain ([Wertz, Everett & Puschell, *Space Mission Engineering: The New SMAD*, Microcosm Press, 2011](https://microcosmpress.com/publishing/space-mission-engineering-the-new-smad/)). The battery-Wh-to-charge-rate conversion (depth-of-discharge, C-rate, eclipse-vs-sunlit duty cycle) is the subject of [Patel, *Spacecraft Power Systems*, CRC Press / Routledge, Chapter 3](https://www.routledge.com/Spacecraft-Power-Systems/Patel-Beik/p/book/9781032383484). Until wired, the declared array wattage is decorative.

### 9.2 `propellant_frac` decoupled from `delta_v_ms`

The SOH gauge `propulsion.propellant_frac` and the maneuver budget `resources.delta_v_ms` are tracked independently — burning Δv via any of the six entry modes in [`engine/maneuver.py`](../../spacesim/engine/maneuver.py) never moves the propellant gauge, and topping up propellant never restores Δv. The two are physically the same variable, related by Tsiolkovsky's ideal rocket equation Δv = Iₛₚ · g₀ · ln(m₀/m_f) ([NASA Glenn Research Center, *Ideal Rocket Equation*, Beginners Guide to Aeronautics](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation/)). The standard derivation, plus the Iₛₚ values typical of mono-/bi-prop and electric stages used in PME vignettes, is in [Sutton & Biblarz, *Rocket Propulsion Elements*, 9th ed., Wiley, 2016](https://www.wiley.com/en-us/Rocket+Propulsion+Elements,+9th+Edition-p-9781118753651). Pick one field as source of truth and compute the other.

### 9.3 Thermal integrator not wired

[`engine/bus.py:ThermalState`](../../spacesim/engine/bus.py) carries `temp_c`, `heater_watts`, and `radiator_capacity_w`, but [`engine/bus.py:advance_bus`](../../spacesim/engine/bus.py) never integrates them — `temp_c` is pinned at 20 °C. The minimum-fidelity fix is a lumped-mass node: dT/dt = (Q_heater + Q_solar − Q_radiator) / (m · c_p), the standard first-cut model in [Gilmore (ed.), *Spacecraft Thermal Control Handbook, Vol. I: Fundamental Technologies*, The Aerospace Press / AIAA, 2002](https://arc.aiaa.org/doi/book/10.2514/4.989117). The full requirements envelope (heater control bands, radiator sizing margins, qualification ranges) lives in the ESA standard [ECSS-E-ST-31C *Space engineering — Thermal control general requirements*, 15 November 2008](https://ecss.nl/standard/ecss-e-st-31c-thermal-control/). If a fully integrated thermal node is out of scope for v1, the audit's alternative — explicitly marking `ThermalState` not-yet-live in the SOH panel — is the honest fallback.

### Sources

- *Space Mission Engineering: The New SMAD (Wertz, Everett & Puschell, 2011)* — [live](https://microcosmpress.com/publishing/space-mission-engineering-the-new-smad/) · [snapshot](https://web.archive.org/web/2026*/https://microcosmpress.com/publishing/space-mission-engineering-the-new-smad/) · accessed 2026-06-12.
- *Spacecraft Power Systems (Patel & Beik, 2nd ed., Routledge)* — [live](https://www.routledge.com/Spacecraft-Power-Systems/Patel-Beik/p/book/9781032383484) · [snapshot](https://web.archive.org/web/2026*/https://www.routledge.com/Spacecraft-Power-Systems/Patel-Beik/p/book/9781032383484) · accessed 2026-06-12.
- *NASA Glenn Beginners Guide — Ideal Rocket Equation* — [live](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation/) · [snapshot](https://web.archive.org/web/2026*/https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation/) · accessed 2026-06-12.
- *Rocket Propulsion Elements, 9th ed. (Sutton & Biblarz, Wiley)* — [live](https://www.wiley.com/en-us/Rocket+Propulsion+Elements,+9th+Edition-p-9781118753651) · [snapshot](https://web.archive.org/web/2026*/https://www.wiley.com/en-us/Rocket+Propulsion+Elements,+9th+Edition-p-9781118753651) · accessed 2026-06-12.
- *Spacecraft Thermal Control Handbook, Vol. I (Gilmore, ed., AIAA / Aerospace Press)* — [live](https://arc.aiaa.org/doi/book/10.2514/4.989117) · [snapshot](https://web.archive.org/web/2026*/https://arc.aiaa.org/doi/book/10.2514/4.989117) · accessed 2026-06-12.
- *ECSS-E-ST-31C — Thermal control (15 Nov 2008)* — [live](https://ecss.nl/standard/ecss-e-st-31c-thermal-control/) · [snapshot](https://web.archive.org/web/2026*/https://ecss.nl/standard/ecss-e-st-31c-thermal-control/) · accessed 2026-06-12.

Used by: [`engine/bus.py`](../../spacesim/engine/bus.py) (`ThermalState`, `advance_bus`), [`engine/maneuver.py`](../../spacesim/engine/maneuver.py), [`engine/entities.py`](../../spacesim/engine/entities.py) (`AssetResources.power_w`, `delta_v_ms`), and [`docs/AUDIT-2026-06-UI-TTC.md`](../AUDIT-2026-06-UI-TTC.md) §2.
## 10. How this maps into the simulator

The nine preceding subsections cite primary doctrine for *what real satellite operations look like*. This closing subsection pulls those threads together into a single map from the doctrine to the engine modules and the vignette content that exercise them. Nothing here is new external content — every claim is a pointer back to §1–§9 above, paired with the engine path that realises it.

### 10.1 Bus subsystems → engine dataclasses
The six core bus subsystems documented in §1 (EPS, ADCS, CDH, TCS, comms, propulsion) are realised one-for-one as pydantic dataclasses in [`engine/bus.py`](../../spacesim/engine/bus.py): [`PowerState`](../../spacesim/engine/bus.py) (line 47), [`AttitudeState`](../../spacesim/engine/bus.py) (line 57), [`ThermalState`](../../spacesim/engine/bus.py) (line 63), [`PropulsionState`](../../spacesim/engine/bus.py) (line 76), [`CdhState`](../../spacesim/engine/bus.py) (line 81), and [`CommsState`](../../spacesim/engine/bus.py) (line 87). The aggregate roll-up object is [`BusState`](../../spacesim/engine/bus.py) (line 127); per-step evolution lives in [`advance_bus`](../../spacesim/engine/bus.py) (line 176). The Wertz/Larson SMAD Chapter 11 citations in §1 source the SoC-floor safe-mode trigger; the Patel *Spacecraft Power Systems* citations in §1 and §4 source the abstract `charge_rate_per_s` formulation; the ECSS-E-ST-70-series citations underwrite the per-subsystem decomposition pattern itself.

### 10.2 SOH discipline → telemetry registry + status helpers
The SOH soft/hard limit + traffic-light roll-up discipline documented in §2 (sourced to Peccia 2003 SCOS-2000 + L3Harris InControl + NASA-STD-7009A/8729.1A) is realised as the 19-row [`PARAMS`](../../spacesim/engine/telemetry.py) registry in `engine/telemetry.py` (each row is a [`ParamSpec`](../../spacesim/engine/telemetry.py) carrying `nominal`/`amp`/`soft`/`hard`/`higher_is_bad`), the [`status_low`](../../spacesim/engine/bus.py) and [`status_high`](../../spacesim/engine/bus.py) helpers in `engine/bus.py`, the module-level threshold constants (`SOC_SOFT = 0.30` / `SOC_HARD = 0.15`, `STORAGE_SOFT = 0.85` / `STORAGE_HARD = 0.98`, `PROP_SOFT = 0.15` / `PROP_HARD = 0.05`), and the per-step [`recompute_status`](../../spacesim/engine/bus.py) cascade that drives the per-asset `overall_status` rolled up to the GUI's fleet rail. Safe mode itself is the [`SafeModeState`](../../spacesim/engine/bus.py) dataclass (line 97) plus the [`enter_safe_mode`](../../spacesim/engine/bus.py) / [`exit_safe_mode`](../../spacesim/engine/bus.py) transitions; the [`payload_available`](../../spacesim/engine/bus.py) predicate gates payload behaviour to false until recovery completes.

### 10.3 Contact loop → orders, scheduler, ground-view refresh
The pre-pass / in-pass / post-pass discipline documented in §3 (sourced to SMAD Ch. 14 + NASA MGS RTC-vs-SSC + JPL F-Prime CmdSequencer) is realised as the three-stage validate → window → execute pipeline in [`engine/orders.py:OrderSystem.issue`](../../spacesim/engine/orders.py) (the in-pass step), the [`AccessProvider`](../../spacesim/engine/access.py) seam that supplies the next-window enumeration (the pre-pass plan), and the [`engine/bus.py:refresh_ground_view`](../../spacesim/engine/bus.py) call invoked from [`engine/busmodel.py:_h_contact`](../../spacesim/engine/busmodel.py) (the post-pass telemetry pull). The pass countdown surfaced to the operator GUI is [`session/manager.py:next_contacts`](../../spacesim/session/manager.py). The "command load" idea — pre-built sequence built on the ground, uplinked once, executed by the on-board sequencer — is realised in the order queue's `delivery` field (`uplink` vs. `stored`) which the order system materialises through ISL or stored-delivery paths.

### 10.4 Power calibration → vignette parameters + recovery loop
The 15-25 % depth-of-discharge per-orbit target documented in §4 (sourced to Landsat 8 mission docs + NASA TM 20160012048 + Wertz/Larson SMAD Ch. 11) drives the calibration of every vignette's `power.drain_rate_per_s` parameter and the eclipse-fraction multiplier in [`engine/bus.py:advance_bus`](../../spacesim/engine/bus.py). The recalibration documented in [`docs/AUDIT-2026-06-UI-TTC.md`](../AUDIT-2026-06-UI-TTC.md) §2 (0.0002/0.0003 → 0.00012/0.0001 → ~63 % DoD to ~21 % DoD) is anchored in these numbers. The dead-field follow-up flagged in §9 (`entities.AssetResources.power_w`) is the eventual fix to derive `charge_rate_per_s` from `power_w / (battery_Wh × 3600)` rather than carrying it as an abstract.

### 10.5 Payload verbs → buscommands catalogue
Each payload-type subsection in §5 (SATCOM), §6 (ISR), and §7 (SIGINT/SDA/Space-control/PNT/MW/Weather) anchors a slice of the verb catalogue in [`engine/buscommands.py`](../../spacesim/engine/buscommands.py):

- SATCOM verbs (`satcom.mitigate_interference`, `satcom.shift_users`, `satcom.geolocate_interference`, `satcom.null_steer` — the last added Sprint 2 from §5.5 below for the angle-specific N-1-capped beam-nulling distinct from the FHSS + broad-antijam `mitigate_interference`) → §5 (WGS+MAJE, AEHF, Quantum, anti-jam techniques).
- ISR verbs (`isr.collect_now`, `isr.schedule_collection`, `isr.set_mode`) → §6 (TPED workflow, NIIRS scoring, EO vs. SAR, commercial tasking timelines). The beam-mode dictionary [`engine/isr.py:BEAM_MODES`](../../spacesim/engine/isr.py) and the [`effective_gain`](../../spacesim/engine/isr.py) + [`soc_drain`](../../spacesim/engine/isr.py) helpers encode the per-mode scaling.
- PNT verb (`pnt.flex_power`) → §7.4 (IS-GPS-200 + GAO M-code report + GPS Modernization Fact Sheet).
- Missile-warning verb (`mw.add_stare_area`) → §7.5 (USSF SBIRS + SSC Next-Gen OPIR + GAO).
- Weather verb (`wx.request_sector`) → §7.6 (NOAA GOES-R + JPSS + USSF DMSP).
- SIGINT and SDA do not currently expose dedicated buscommands verbs — they sit behind the `engine/sigint.py` and `engine/ssn.py` request/staging pipelines respectively. §7.1 and §7.2 anchor those mechanisms in TDOA/FDOA geolocation math and CCSDS 508.0-B-1 CDM standards.

The [`apply_command`](../../spacesim/engine/buscommands.py) handler at line 77 dispatches all verbs deterministically inside `execute_command` events; [`can_issue`](../../spacesim/engine/buscommands.py) at line 485 is the plan-time validator that gates payload verbs by payload-type + bus-availability.

### 10.6 Operator UI grammar → drill-down panels and sparklines
The six real operator consoles surveyed in §8 (SCOS-2000, NASA Open MCT, L3Harris InControl, GMV Hifly, Kratos OpenSpace, RTI Connext DDS) establish a stable UI grammar that the simulator's web GUI deliberately mirrors: the fleet-rail roll-up + per-asset drill-down + per-subsystem traffic-light SOH + telemetry sparklines + per-subsystem command-verb buttons in [`spacesim/ui_web/static/app.js`](../../spacesim/ui_web/static/app.js) and the line-graph rendering in [`spacesim/ui_web/static/graph.js`](../../spacesim/ui_web/static/graph.js). The 19 sparkline channels rendered in the drill-down are the [`PARAMS`](../../spacesim/engine/telemetry.py) registry from §2 above. The compare-to-nominal overlay is the `nominal=1` series form documented in `CLAUDE.md` (read-time-seeded; never mutates state/RNG).

### 10.7 Live modeling gaps → follow-up backlog
The three live modeling gaps catalogued in §9 (dead `power_w` field, `propellant_frac` decoupled from `delta_v_ms`, thermal integrator not wired) are not flaws in the simulator's pedagogy — they are honest *not-yet-live* markers that the audit doc surfaced and §9 grounded against the relevant engineering standards (Wertz/Larson SMAD, Patel/Beik *Spacecraft Power Systems*, NASA Glenn Ideal Rocket Equation, Sutton/Biblarz *Rocket Propulsion Elements*, Gilmore *Spacecraft Thermal Control Handbook*, ECSS-E-ST-31C). Each entry in [`docs/AUDIT-2026-06-UI-TTC.md`](../AUDIT-2026-06-UI-TTC.md) §2 names the standard the eventual fix will land against. The simulator already exposes the *shape* of each (the `ThermalState` dataclass is declared at line 63 of `engine/bus.py`; the `power_w` field is declared on `AssetResources`; the `propellant_frac` and `delta_v_ms` fields both exist) — what's missing is the integrator, not the model surface.

### 10.8 Vignettes that exercise this
The training-basics vignette ([`spacesim/content/vignettes/00-training-basics.yaml`](../../spacesim/content/vignettes/00-training-basics.yaml)) walks new operators through the pre-pass / in-pass / post-pass loop §3 documents. The intermediate-recovery vignette ([`spacesim/content/vignettes/learn-intermediate-recovery.yaml`](../../spacesim/content/vignettes/learn-intermediate-recovery.yaml)) forces trainees through the full safe-mode recovery chain §2.4 documents (establish contact → dump telemetry → diagnose → patch → re-enable). The cyber-induced re-safed-until-patched loop §2.5 documents is exercised by any vignette that uses the `seize_c2` cyber payload against a Blue asset (the matching defender response is `def.patch_cyber` followed by `begin_recovery`). The remaining 17 vignettes each exercise a different slice of the payload-ops verbs §5–§7 catalogue.

Used by: every engine module referenced inline above ([`engine/bus.py`](../../spacesim/engine/bus.py), [`engine/busmodel.py`](../../spacesim/engine/busmodel.py), [`engine/buscommands.py`](../../spacesim/engine/buscommands.py), [`engine/recovery.py`](../../spacesim/engine/recovery.py), [`engine/orders.py`](../../spacesim/engine/orders.py), [`engine/access.py`](../../spacesim/engine/access.py), [`engine/isr.py`](../../spacesim/engine/isr.py), [`engine/sigint.py`](../../spacesim/engine/sigint.py), [`engine/ssn.py`](../../spacesim/engine/ssn.py), [`engine/telemetry.py`](../../spacesim/engine/telemetry.py), [`session/manager.py`](../../spacesim/session/manager.py)), the operator GUI ([`spacesim/ui_web/static/app.js`](../../spacesim/ui_web/static/app.js), [`graph.js`](../../spacesim/ui_web/static/graph.js)), and the vignettes referenced ([`content/vignettes/00-training-basics.yaml`](../../spacesim/content/vignettes/00-training-basics.yaml), [`learn-intermediate-recovery.yaml`](../../spacesim/content/vignettes/learn-intermediate-recovery.yaml)). No new external sources; this subsection is an integration pass over §1–§9.

---

## 11. Cross-references

- **Engine modules sourced by this file.** [`engine/bus.py`](../../spacesim/engine/bus.py) (§1 — the six subsystem dataclasses + `SafeModeState` + the `SOC_*`/`STORAGE_*`/`PROP_*` thresholds + `status_low`/`status_high`/`recompute_status`/`enter_safe_mode`/`exit_safe_mode`/`payload_available`/`advance_bus`/`refresh_ground_view`); [`engine/busmodel.py`](../../spacesim/engine/busmodel.py) (§3 — the contact-tick handler `_h_contact` + the per-step `_h_tick` evolution); [`engine/buscommands.py`](../../spacesim/engine/buscommands.py) (§1 + §5–§7 — the BUS / PAYLOAD / DEFENSE verb catalogues mutating each subsystem; `apply_command` / `can_issue`); [`engine/recovery.py:RecoverySystem`](../../spacesim/engine/recovery.py) (§2 — multi-pass safe-mode recovery chain + cyber-induced re-safed-until-patched loop); [`engine/orders.py`](../../spacesim/engine/orders.py) (§3 — `OrderSystem.issue` + `dry_run` pipelines); [`engine/access.py`](../../spacesim/engine/access.py) (§3 — `AccessProvider` next-window enumeration); [`engine/telemetry.py`](../../spacesim/engine/telemetry.py) (§2 — `ParamSpec` + the 19-row `PARAMS` registry); [`engine/isr.py`](../../spacesim/engine/isr.py) (§6 — `BEAM_MODES` + `effective_gain` + `soc_drain`); [`engine/sigint.py`](../../spacesim/engine/sigint.py) (§7.1 — `geolocation_error_km` + `band_params` + `mode_params`); [`engine/ssn.py`](../../spacesim/engine/ssn.py) (§7.2 — mock SSN with dispersion presets); [`engine/maneuver.py`](../../spacesim/engine/maneuver.py) (§9.2 — six manoeuvre entry modes); [`engine/entities.py`](../../spacesim/engine/entities.py) (§9.1 — `AssetResources.power_w` + `delta_v_ms`); [`engine/jam.py`](../../spacesim/engine/jam.py) (§5 — anti-jam modulation database); [`session/manager.py:next_contacts`](../../spacesim/session/manager.py) (§3 — fleet pass countdown).
- **Operator UI surfaces sourced by this file.** [`spacesim/ui_web/static/app.js`](../../spacesim/ui_web/static/app.js) and [`graph.js`](../../spacesim/ui_web/static/graph.js) (§8 — the fleet rail + per-asset drill-down + per-subsystem traffic-light SOH + sparkline + per-subsystem command-verb buttons grammar copied from SCOS-2000 / InControl / Open MCT / Hifly / OpenSpace / DDS).
- **Vignettes that exercise this file's content.** [`content/vignettes/00-training-basics.yaml`](../../spacesim/content/vignettes/00-training-basics.yaml) (§3 pre/in/post-pass loop tutorial); [`content/vignettes/learn-intermediate-recovery.yaml`](../../spacesim/content/vignettes/learn-intermediate-recovery.yaml) (§2.4 multi-pass safe-mode recovery + §2.5 cyber-induced re-safed-until-patched loop); the remaining 17 vignettes under [`spacesim/content/vignettes/`](../../spacesim/content/vignettes/) each exercise a different slice of the §5–§7 payload-ops verb catalogue.
- **Sibling primer files.** [`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md) for the counterspace categories and the five D's that §2.5 (cyber re-safed-until-patched) and §5 (jam mitigation) and §6 (ISR-denial counters) and §7.3 (RPO / space-control) cross-link to; [`04-orbital-mechanics-primer.md`](04-orbital-mechanics-primer.md) §2 (access-window taxonomy that §3.2 grounds the LEO 5–12 min pass window in) and §5 (eclipse / lighting model that §4 power calibration consumes).
- **Audit predecessor.** [`docs/AUDIT-2026-06-UI-TTC.md`](../AUDIT-2026-06-UI-TTC.md) §2 — the TT&C audit that surfaced the §4 power-rate recalibration (drain `0.0003 → 0.0001`, charge `0.0002 → 0.00012`, ~63 % DoD sawtooth → ~21 % DoD cycle) and the three §9 live-modeling gaps (dead `power_w`, decoupled `propellant_frac` ↔ `delta_v_ms`, unwired thermal integrator). Every fix the audit names lands against a standard cited in this file.
- **Forward-references to Tier 2/3 deep-dives.** Per-mission deep-dives — [`05a-isr-eo-sar.md`](05a-isr-eo-sar.md) extends §6, [`05b-satcom-pnt.md`](05b-satcom-pnt.md) extends §5 and §7.4, [`05c-sda-and-orbital-warfare.md`](05c-sda-and-orbital-warfare.md) extends §7.2 / §7.3 — and per-actor deep-dives ([`01a-doctrine-us-allies.md`](01a-doctrine-us-allies.md), [`02a-doctrine-china.md`](02a-doctrine-china.md), [`02b-doctrine-russia.md`](02b-doctrine-russia.md)) are queued in [`FUTURE-WORK.md` §12.5.2](../FUTURE-WORK.md#1252-tier-2--per-mission-and-per-actor-deep-dives) and Tier 3 (counterspace-systems-and-physics) in [`FUTURE-WORK.md` §12.5.3](../FUTURE-WORK.md#1253-tier-3--counterspace-systems-and-physics).
- **Research encyclopedia.** [`encyclopedia/R103-satellite-command-and-control.md`](encyclopedia/R103-satellite-command-and-control.md) and [`encyclopedia/R106-mission-operations.md`](encyclopedia/R106-mission-operations.md) for the operator-process counterparts to this file's bus/payload model; [`encyclopedia/R111-power-and-thermal-operations.md`](encyclopedia/R111-power-and-thermal-operations.md), [`encyclopedia/R112-propulsion-and-maneuver-planning.md`](encyclopedia/R112-propulsion-and-maneuver-planning.md), [`encyclopedia/R113-attitude-determination-and-control.md`](encyclopedia/R113-attitude-determination-and-control.md), [`encyclopedia/R114-command-and-data-handling.md`](encyclopedia/R114-command-and-data-handling.md) for the per-subsystem deep dives behind §1's six dataclasses.

*Last reviewed: 2026-06-12. Pending review: every 12 months from `last_reviewed`.*
