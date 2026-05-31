# Satellite Bus & Payload Operations — How Operators Actually Fly Satellites

This file grounds the simulator in **real satellite operations** so the operator experience
feels authentic to CAF space operators rather than like a strategy game. It covers (1) how the
**bus** is operated and what's monitored, (2) how each **payload type** is operated, (3) what
**real operator interfaces** look like, and (4) **how to work this into the sim for realism**
without crushing playability. It feeds `09-gui-principles.md`, `11-command-planning-and-
tasking.md`, and the `04-data-model.md` schemas.

---

## 1. Bus operations — keeping the satellite alive

Every satellite is **bus + payload**. The **bus** is the vehicle that keeps the satellite
alive and pointed; the **payload** does the mission. Operators must keep the bus healthy or
the payload is worthless. The bus is a set of subsystems, each producing telemetry the
operator watches and each accepting commands.

### 1.1 The core bus subsystems (and what operators watch on each)

| Subsystem | What it does | Key telemetry operators monitor | Typical commands |
|---|---|---|---|
| **EPS** (Electrical Power) | Generates (solar), stores (battery), distributes power | Battery state-of-charge, bus voltage/current, solar array output, eclipse status, power-rail on/off | Shed non-critical loads, switch rails, manage battery charge |
| **ADCS / GNC** (Attitude/Pointing) | Determines and controls orientation; points payload/antennas/arrays | Attitude error, reaction-wheel speeds (momentum), gyro/star-tracker/sun-sensor health, pointing mode | Slew to attitude, set pointing mode, desaturate wheels |
| **Propulsion** | Orbit maintenance & maneuver | Fuel/propellant remaining, tank pressure, thruster status | Plan & execute burns, station-keeping |
| **TCS** (Thermal) | Keeps components in temperature limits | Component temperatures vs. limits, heater states | Enable/disable heaters, change thermal mode |
| **C&DH / OBC** (Command & Data Handling) | The onboard "brain": runs flight software, routes data, stores commands | CPU/memory load, mass-storage fill, time sync, error counters, FSW mode | Upload command loads, set onboard time, manage stored commands, FSW patches |
| **TT&C / Comms** (the link) | Receives commands, sends telemetry, downlinks data | Uplink/downlink lock, signal strength, bit error rate, antenna pointing | Configure transponders, point antenna, set data rate |
| **Structures/Mechanisms** | Deployables, gimbals | Deployment status, gimbal angles | Deploy, gimbal-point |

> The OBC continuously polls subsystems (e.g., querying EPS for available power and shedding
> non-critical loads to protect vital systems) and packages **housekeeping telemetry** for
> downlink. Operators see the *result* of this onboard autonomy, not every internal tick.

### 1.2 State of Health (SOH) and "safe mode"
The single most important operator concept: **state of health**. Operators continuously assess
whether the satellite is nominal. If something goes badly wrong (power, attitude loss, thermal
excursion), the satellite autonomously drops into **safe mode** — a protective configuration
that points solar arrays at the sun, shuts down the payload, and waits for the ground. *A
satellite in safe mode does no mission.* Recovering it costs precious passes. This is a
realistic, teachable failure state for the sim (and a juicy target for an attacker).

### 1.3 The operator's reality: you only see/touch it during a contact
Bus telemetry is **not a live continuous feed** for most satellites — it is received **during
ground-station passes** (or via relay/ISL). Between passes the operator works from the **last
downlinked snapshot** and onboard-stored telemetry that gets dumped at the next contact.
Operators:
- **plan a "pass plan"** — an ordered set of commands and data dumps to execute in the short
  contact window (a LEO pass may be only 5–12 minutes);
- **review stored telemetry** after the pass to reconstruct what happened while out of contact;
- **chase anomalies across passes**, since they often can't see a problem until the next
  contact.

This is exactly the access-window constraint already in the sim — bus operations make it
*personal*: it's not just "can I act," it's "is my satellite even healthy, and I won't know
until 14:32Z."

---

## 2. Payload operations — doing the mission (by type)

The bus is broadly similar across satellites; **payload operations differ sharply by mission
type.** Below is how operators run each payload class the sim supports, what they monitor, and
when they get information. A recurring real-world wrinkle: **the payload operator is often
beholden to the bus** — if the bus maneuvers or goes to safe mode, the payload mission is
interrupted whether the payload operator likes it or not. (In hosted-payload arrangements the
bus and payload may even be run by different teams, with all commands/telemetry separately
encrypted.)

### 2.1 SATCOM (communications)
- **What the operator does:** manages **transponders/beams** — power levels, frequency plans,
  bandwidth allocation, and (on modern *flexible/software-defined payloads* like ESA's
  Quantum class) **reconfigures coverage, power, and frequency on orbit** to follow demand or
  move to a new slot.
- **Monitors:** transponder power/temperature, carrier/interference levels, link utilization,
  and — critically — **interference sources** (the SATCOM operator's daily fight is finding and
  mitigating interference, intentional or not).
- **When they get info:** GEO SATCOM is continuously in view of its control station, so SATCOM
  ops are closer to "real-time" than LEO — a useful contrast for the sim.
- **In-sim hook:** jamming shows up to the operator as **interference telemetry / degraded
  carrier**, not a label saying "you are being jammed." Mitigation = re-plan frequency/beam,
  shift customers, null the interferer.

### 2.2 ISR — imaging (EO/IR and SAR)
- **What the operator does:** runs a **tasking → collection → downlink → processing →
  dissemination** chain. They build a **collection schedule** (which targets to image on which
  passes), point the sensor, manage onboard storage, and schedule downlinks.
- **Monitors:** collection schedule vs. target windows, sensor health/calibration, onboard
  storage fill, downlink backlog, image quality, and **sun angle/weather** (EO/IR needs light
  and clear sky; SAR is all-weather day/night).
- **When they get info:** images are collected over the target pass and **downlinked at a later
  ground/relay pass**; modern systems compress this to minutes (task → image → downlink via a
  global station net → on-prem processing → AI target recognition → product). The operator
  often receives a **processed intelligence product, not a raw image.**
- **In-sim hook:** the **collect-vs-downlink split** (already in Vignette 1) is exactly this.
  Storage limits, downlink scheduling, and "image quality degraded" (from dazzle/weather) are
  realistic operator-facing signals.

### 2.3 SIGINT / ELINT
- **What the operator does:** tasks **receivers** to collect across frequency ranges/geographies;
  manages where and when to "listen"; prioritizes among emitters.
- **Monitors:** intercept activity, signal characteristics, geolocation confidence, storage,
  downlink backlog.
- **When they get info:** like ISR, collection then later downlink; product is **geolocations/
  signal fixes**, often fused on the ground.
- **In-sim hook:** SIGINT is a **sensor-tasking** activity (ties to `11-command-planning-and-
  tasking.md` Part B). It can detect/locate emitters (e.g., find a Red jammer to enable
  counter-fire in Vignette 3) — but only where/when tasked, and the product arrives after
  downlink.

### 2.4 SDA / Space Surveillance payloads (space-based "neighbourhood watch")
- **What the operator does:** tasks the sensor to **search a regime, track an object, or
  characterize** another satellite (inspector ops); manages where the sensor looks.
- **Monitors:** track quality/custody, sensor pointing, and the **uncertainty** on each tracked
  object (this is the data behind the 3D viewer's growing/shrinking ellipsoids).
- **When they get info:** observations arrive when geometry permits and after downlink;
  **custody decays between looks.**
- **In-sim hook:** this *is* the SDA tasking loop and the belief-state 3D viewer
  (`10-sda-3d-viewer.md`). Operating an SDA payload = choosing what to keep custody of with a
  scarce sensor.

### 2.5 Space-control payloads (counterspace effectors)
- **What the operator does:** operates the **effector** — an RF jammer, a dazzling laser, an
  RPO/inspection-and-effect payload, or a co-orbital approach. Selects target, effect level
  (the 5 D's), and timing; manages the engagement geometry.
- **Monitors:** effector status (power/charge/ammo), target track quality (the weapons-quality
  gate), engagement geometry/range, and **effect assessment** (did it work? — often inferred,
  not confirmed).
- **When they get info:** must hold a good track *and* be in an engagement/proximity window;
  battle-damage/effect assessment is delayed and uncertain.
- **In-sim hook:** these are the offensive/defensive actions already modeled; payload framing
  adds **effector resource management** and **uncertain effect assessment** (you rarely get a
  clean "kill confirmed").

### 2.6 PNT (navigation), Missile Warning, Weather (briefly)
- **PNT:** highly automated; operators monitor signal integrity/timing and ground-monitoring
  stations; the fight is mostly at the **user/ground** level (jam/spoof) not the bus.
- **Missile warning:** continuous IR staring; operators monitor sensor health and alert
  pipelines; attacking it (dazzle/cyber) shows as **degraded/altered alerts**.
- **Weather/environmental:** scheduled sensing + downlink, like a simple ISR chain.

---

## 3. What real operator interfaces look like

Real military/commercial satellite **command-and-control (C2) / mission-control software**
(e.g., SCOS-2000, L3Harris InControl, Parsons Ace CtrlPoint, Kratos, NASA OpenMCT, Astro UXDS
patterns, Epsilon3 procedures) share a remarkably consistent feature set the sim should echo:

1. **Constellation/fleet view → drill-down.** A top-level red/yellow/green **status rollup**
   across all satellites and ground stations, one click to drill into a single vehicle, then
   into a subsystem, then into an individual telemetry point ("mnemonic"). *Operators manage
   many satellites with limited contact windows, so at-a-glance health is paramount.*
2. **Telemetry displays with limit checking.** Every telemetry parameter has **soft and hard
   limits**; values are **color-coded** (green nominal / yellow warning / red alarm). Operators
   diagnose by drilling through layers to find the off-nominal point.
3. **Alarms / event log.** Out-of-limit conditions raise **alerts/warnings/errors**, logged and
   often pushed (email/message). "Investigate anomalies" is a primary task.
4. **Command stacks & procedures.** Commands are assembled into **stacks / pass plans**,
   **validated against constraints before release**, and executed manually or automatically
   within a booked pass. Procedures (with conditional logic, waits, pass/fail criteria) can run
   semi-automatically; everything is logged as "as-run" for traceability.
5. **Pass planning & scheduling.** **Pass prediction from TLEs + ground-station availability**,
   pass booking, and a **task scheduler** that fires command procedures at designated times —
   essential for LEO contact management.
6. **2D/3D orbit visualization.** TLE-propagated tracking, ground tracks, and contact
   visibility — used for situational awareness, not as a truth feed.
7. **Telemetry & command databases.** Behind it all: a **telemetry DB** (every parameter, its
   units, and alarm limits) and a **command DB** (every command, its arguments, and
   constraints). These are the authoritative "what can I see / what can I send."

> **Design takeaway:** the operator's job is *monitor SOH against limits → diagnose alarms →
> build and validate a pass plan → execute in the contact window → review stored telemetry
> after.* That loop, not a fps-style "click to shoot," is the authentic experience.

---

## 4. How to work this into the simulator for realism

The goal is **authentic texture without operator overload.** Layer it so White Cell can dial
fidelity up for a TT&C-focused exercise or down for a tactics-focused one.

### 4.1 Give every satellite a small, live **bus health model**
Track a handful of SOH parameters per satellite — **power (battery SoC + eclipse), attitude/
pointing, propellant, thermal, onboard storage, comms lock** — each with green/yellow/red
limits. These evolve over time (battery drains in eclipse, storage fills as ISR collects,
propellant drops with maneuvers) and gate the payload (no power → payload off; bad attitude →
can't point; full storage → can't collect). Implement as a `BusState` block on each asset
(see §5).

### 4.2 Make telemetry **pass-gated**, like reality
The operator sees **fresh** bus/payload telemetry only after a **contact** (ground pass, relay,
or ISL); between contacts the displayed SOH is a **timestamped last-known snapshot** that may
be stale. This reuses the access-window engine and reinforces the core lesson. Stored telemetry
"dumps" at the next pass can reveal that something happened while out of contact — e.g., the
satellite went to safe mode an hour ago and you're only finding out now.

### 4.3 Model **safe mode** as a state and an attack effect
A satellite can enter **safe mode** from a bus fault, a power crisis, an attitude upset, *or as
the result of a cyber/EW effect.* In safe mode the payload is off and the operator must spend
passes recovering it. This is a realistic, non-kinetic way for an attacker to take a satellite
"off the board" temporarily — and a great teaching objective for defenders (detect, diagnose,
recover).

### 4.4 Make payload ops **type-specific** using the loop from §2
Each payload type exposes its real operator actions/monitors:
- **SATCOM:** transponder/beam config; interference telemetry (= how jamming is *experienced*).
- **ISR:** collection schedule, storage, downlink queue, image-quality readout.
- **SIGINT/SDA:** sensor tasking + custody/uncertainty (ties to the tasking & 3D-viewer docs).
- **Space control:** effector resources + uncertain effect assessment.

### 4.5 Echo the **real UI loop**, simplified (see §3 → `09-gui-principles.md`)
- A **fleet SOH rollup** (red/yellow/green) as the operator's home view; drill-down to a
  satellite's subsystem panel; drill-down to individual parameters.
- **Limit-based coloring and alarms** on telemetry; an **event/alarm log**.
- **Pass-plan / command-stack** building that **validates before release** and executes in the
  window — this is literally the `PlannedActivity` queue from `11-command-planning-and-
  tasking.md`, dressed as a pass plan.
- A **telemetry/command "database"** per asset template defining which parameters exist and
  which commands are legal — the authoritative source for what the UI shows and offers.

### 4.6 Tune realism with a White-Cell parameter
Add a vignette parameter `ops_fidelity: {tactical | realistic | full_ttc}`:
- **tactical** — bus is abstracted to a single health bar; focus on space-control decisions.
- **realistic (default)** — the §4.1 SOH parameters, pass-gated telemetry, safe mode.
- **full_ttc** — adds detailed subsystem telemetry, alarms, and explicit pass-plan building for
  TT&C-operator training.

> This keeps the same engine serving both a general's tabletop and a TT&C operator's console.

---

## 5. Data-model additions (summarized; canonical schema in `04-data-model.md`)

```yaml
# Added to Asset:
bus_state:
  power:    {battery_soc: 0..1, in_eclipse: bool, status: green|yellow|red}
  attitude: {pointing_ok: bool, mode: nominal|slew|safe, status: ...}
  thermal:  {status: green|yellow|red}
  propulsion: {propellant_frac: 0..1, status: ...}
  cdh:      {storage_frac: 0..1, fsw_mode: nominal|safe, status: ...}
  comms:    {uplink_lock: bool, downlink_lock: bool, status: ...}
  mode: nominal | safe_mode            # safe_mode disables payload
  last_telemetry_time: SimTime         # when ground last got fresh SOH (pass-gated)

payload_state:                          # shape varies by payload type
  type: satcom | isr_eo | isr_sar | sigint | sda | space_control | pnt | missile_warning | weather
  health: green|yellow|red
  # SATCOM:  {transponders:[...], interference_level: 0..1}
  # ISR:     {collection_queue:[...], storage_frac, downlink_backlog, last_image_quality}
  # SIGINT/SDA: {tasking:[...], (feeds TrackCatalog)}
  # space_control: {effector_resource, last_effect_assessment: unknown|likely|confirmed}

telemetry_db:   # per template: parameters, units, soft/hard limits (drives UI + alarms)
command_db:     # per template: legal commands, args, pre-release constraints
```

`BusState` and `payload_state` evolve in the engine tick; the UI shows the **last pass-gated
snapshot**; alarms fire on limit violations; safe mode disables the payload until recovered.

## Sources
- Bus subsystems & C&DH/OBC, TT&C: IntechOpen (2020); IDST&C; tutorialspoint; Phoenix CubeSat
  FSW; Aerospace Corp. *Mission Assurance Practices for Satellite Operations* (TOR-2013-00293).
- Ground/MCS software & operator UX: ESA SCOS-2000; L3Harris InControl; Parsons Ace CtrlPoint;
  D-Orbit Aurora; Alén Space MCS (OpenMCT); Astro UXDS TT&C case study; Epsilon3.
- Payload ops: AIAA *Flexible Payload Operations of SATCOM Systems* (2018); New Space Economy,
  *Specialized Satellite Payloads* (2024); ICEYE ISR system; JAPCC *Hosted Satellite Payloads*
  (2024); USPTO hosted-payload secure-enclave patents (bus/payload coordination & separate
  COMSEC).
