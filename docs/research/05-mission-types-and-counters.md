# Satellite Mission Types & Their Counters

The user asked to "include all satellite mission types and the counters to them." This file
is the **asset catalog** for the sim — each mission type becomes a satellite template with a
regime, a value to its owner, the services it provides to terrestrial forces, and the menu of
effects that can hold it at risk. Cross-reference the effect definitions in
`03-counterspace-taxonomy.md` and the reachability rules in `04-orbital-mechanics-primer.md`.

## How to read this

Each mission type lists: **what it does**, **typical regime**, **why it matters in the fight
(the terrestrial effect of denying it)**, and **counters ranked by realism/likelihood**
(non-kinetic before kinetic, matching observed real-world behavior).

---

### 1. ISR — Imagery Intelligence (electro-optical / infrared)
- **Does:** takes pictures; finds and tracks terrestrial forces; battle damage assessment.
- **Regime:** LEO (often Sun-synchronous for consistent lighting).
- **Deny it →** adversary loses eyes on your maneuver; you can mass forces unseen.
- **Counters:** (1) **dazzle/blind** with directed energy during a pass; (2) **downlink jam**
  to deny imagery delivery; (3) **cyber** to corrupt or exfiltrate imagery; (4) **camouflage/
  concealment/deception** on the ground (timed to known pass windows); (5) **co-orbital
  inspection**; (6) DA-ASAT (high-end, debris).

### 2. ISR — Synthetic Aperture Radar (SAR)
- **Does:** all-weather, day/night imaging; sees through cloud.
- **Regime:** LEO.
- **Deny it →** removes the adversary's bad-weather/night surveillance.
- **Counters:** (1) **SAR jamming/EW** of the radar return or downlink; (2) cyber; (3)
  decoys/corner-reflector deception; (4) co-orbital; (5) DA-ASAT.

### 3. SIGINT / ELINT
- **Does:** intercepts communications and emitters; geolocates transmitters.
- **Regime:** LEO and GEO.
- **Deny it →** protects your own emissions; forces adversary to other INTs.
- **Counters:** (1) **emission control (EMCON)/deception** on the ground; (2) uplink jam;
  (3) cyber; (4) co-orbital shadowing; (5) DA-ASAT (GEO very hard).

### 4. GNSS / PNT (positioning, navigation, timing)
- **Does:** GPS/GLONASS/Galileo/BeiDou — position fixes, weapons guidance, network timing.
- **Regime:** MEO (very hard to reach kinetically).
- **Deny it →** degrades precision weapons, drones, logistics, and time-sync — the single
  highest-leverage terrestrial effect (validated daily in Ukraine).
- **Counters:** (1) **downlink jamming** of users (creates a local GPS-denied bubble); (2)
  **spoofing** (false position/time); (3) cyber against ground monitoring stations; (4) DA-
  ASAT essentially impractical at MEO. **Defenses:** M-code/anti-jam antennas, inertial
  backup, alternative PNT.

### 5. SATCOM — military & commercial communications
- **Does:** beyond-line-of-sight comms, data relay, drone control, broadcast.
- **Regime:** GEO (wideband/protected) and LEO (proliferated constellations).
- **Deny it →** cuts C2 and ISR backhaul; isolates forces. (Viasat KA-SAT, Feb 2022.)
- **Counters:** (1) **uplink jam** (denies the whole transponder) or **downlink jam** (local);
  (2) **cyber** against modems/ground/user segment (the Viasat model); (3) co-orbital
  shadow/close-in jam in GEO; (4) DA-ASAT (GEO extremely hard). **Defenses:** frequency
  hopping, spot-beam nulling, proliferation (a LEO mega-constellation is hard to kill).

### 6. Missile Warning / Missile Tracking
- **Does:** detects launches via IR; tracks ballistic/hypersonic threats; cues defense.
- **Regime:** GEO and HEO (legacy), proliferated LEO (emerging tracking layer).
- **Deny it →** blinds strategic/theater warning — highly escalatory to attack.
- **Counters:** (1) **IR sensor dazzle**; (2) uplink jam; (3) cyber to corrupt/delay alerts;
  (4) co-orbital; (5) DA-ASAT (GEO/HEO extremely hard, strategically grave). **Defenses:**
  the emerging proliferated LEO layer exists precisely to be hard to kill.

### 7. Weather / Environmental Monitoring
- **Does:** meteorology and space weather for operational planning.
- **Regime:** LEO and GEO.
- **Deny it →** degrades planning (less escalatory; often a "soft" target).
- **Counters:** downlink jam; cyber data corruption; dazzle; co-orbital; DA-ASAT.

### 8. Space Domain Awareness (space-based SDA / inspector sats)
- **Does:** observes *other satellites*; provides custody, characterization, targeting data.
- **Regime:** GEO (e.g., inspector constellations) and LEO.
- **Deny it →** **suppression of adversary counterspace targeting** — blind the enemy's
  ability to find and target your satellites. A doctrinally explicit objective.
- **Counters:** (1) dazzle its optics; (2) co-orbital interference; (3) cyber; (4) deny its
  ground-station downlink; (5) DA-ASAT. Also countered on the ground by hitting its sensors.

### 9. On-Orbit Servicing / RPO / "Bodyguard" satellites
- **Does:** refuel, inspect, repair, or **escort/defend** friendly sats; dual-use with co-
  orbital attack.
- **Regime:** GEO and LEO.
- **Role in sim:** these are both a *defensive* asset (escort) and an ambiguous *offensive*
  one. Countering an escort may require out-maneuvering it or suppressing its tasking.

---

## Ground & link segment targets (often the easiest counters)

Satellites are expensive to attack in orbit; their **ground and link segments are softer**.
The sim must let players target these directly (USSF "terrestrial strike" / "space link
interdiction"):

| Target | Effect of denying it | Counters |
|---|---|---|
| **Ground/TT&C station** | Owner loses command & data for *all* sats using it | terrestrial strike, cyber, jam the station's uplink |
| **Mission data processing center** | Data collected but unusable | cyber, terrestrial strike |
| **Launch site / integration** | Cannot reconstitute losses | terrestrial strike (pre/post-launch) |
| **User terminals** (e.g., GPS receivers, VSATs) | Local denial without touching the satellite | downlink jam, spoof, cyber |

> **Design point:** because cyber and ground-segment attacks are *not* gated by orbital pass
> windows, they're the flexible, fast options — balanced by requiring a modeled access vector
> and a strong defender cyber/physical posture.

---

## Turning this into asset templates

Each entry becomes a YAML template the engine loads (see `04-data-model.md`):

```yaml
asset_template:
  type: ISR_EO
  regime: LEO_SSO
  owner_value: high            # how much losing it hurts the owner's score
  provides: [imagery]          # terrestrial services enabled
  ground_segment: [station_refs, processing_center_ref]
  vulnerabilities:             # ordered, realism-weighted
    - {effect: directed_energy_dazzle, likelihood: high}
    - {effect: ew_downlink_jam,        likelihood: high}
    - {effect: cyber_corrupt,          likelihood: med}
    - {effect: co_orbital_inspect,     likelihood: med}
    - {effect: da_asat,                likelihood: low, escalation: high}
  defenses_available: [maneuver, deception, hardening, downlink_encryption]
```

## Sources
- USSF *Space Warfighting* (2025) — segment targeting, suppression of counterspace targeting.
- SWF *Global Counterspace Capabilities* (2025/2026) — counter availability by target/regime.
- CSIS *Extending the Battlespace to Space* (2025) — Viasat case; EW vs PNT/SATCOM in Ukraine.
