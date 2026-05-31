# Worked Example: Asset Template Library

This is the **concrete copy-me reference** for Claude Code. Everything else in the package
describes the schemas; this file *fills three of them in completely* so the pattern is
unambiguous, then shows one of them instantiated inside a vignette. Replicate this pattern for
the remaining mission types in `05-mission-types-and-counters.md`.

Conventions used here:
- Field names match `04-data-model.md` exactly (do not rename).
- `command_db` entries are drawn from `13-operator-command-catalog.md` (verbs are authoritative).
- `telemetry_db` limits and delta-v figures follow `06-bus-and-payload-operations.md` and
  `14-delta-v-economy.md`.
- Format is JSON (matches the vignette file format in `../build-spec/03-architecture-and-data.md` §8). Comments
  are shown as `"_comment"` keys since JSON has no comments; Claude Code may strip them.

Templates define **defaults**; a vignette's asset instance overrides only what differs (orbit/
TLE, name, owner, starting fuel, etc.).

---

## Template 1 — `ISR_EO` (LEO electro-optical imaging satellite, e.g., Blue)

```json
{
  "template_id": "ISR_EO",
  "_comment": "LEO Sun-synchronous electro-optical imager. The teaching workhorse: short passes, collect-vs-downlink split, dazzle/weather degradation.",
  "kind": "satellite",
  "payload_type": "isr_eo",
  "default_regime": "LEO_SSO",
  "provides": ["imagery"],
  "resources_default": {
    "delta_v_ms": 120,
    "delta_v_ms_initial": 120,
    "annual_upkeep_ms": 15,
    "_comment_dv": "LEO drag make-up is modest at SSO altitudes; ~8 yr of upkeep. A big phasing burn to retask coverage costs real life.",
    "power_w": 1800,
    "ammo": 0
  },
  "comms_default": { "isl_capable": false, "isl_peers": [], "stored_program": true },
  "telemetry_db": {
    "_comment": "Each parameter: units, soft (yellow) and hard (red) limits. Drives SOH rollup + alarms. Pass-gated to the UI.",
    "bus": {
      "battery_soc":        { "units": "frac", "soft_low": 0.40, "hard_low": 0.25 },
      "bus_voltage_v":      { "units": "V",    "soft_low": 26.0, "hard_low": 24.0, "soft_high": 33.0, "hard_high": 34.5 },
      "wheel_momentum_pct": { "units": "%",    "soft_high": 70,  "hard_high": 90, "_comment": "near saturation → must desaturate" },
      "attitude_error_deg": { "units": "deg",  "soft_high": 0.5, "hard_high": 2.0, "_comment": "pointing quality for imaging" },
      "component_temp_c":   { "units": "C",    "soft_low": -10,  "hard_low": -20, "soft_high": 45, "hard_high": 60 },
      "propellant_frac":    { "units": "frac", "soft_low": 0.20, "hard_low": 0.05 },
      "storage_frac":       { "units": "frac", "soft_high": 0.80, "hard_high": 0.95, "_comment": "full storage blocks collection" },
      "uplink_lock":        { "units": "bool" },
      "downlink_lock":      { "units": "bool" }
    },
    "payload": {
      "sensor_temp_c":      { "units": "C",  "soft_high": 30, "hard_high": 40 },
      "last_image_quality": { "units": "frac", "soft_low": 0.6, "hard_low": 0.3, "_comment": "drops under dazzle/cloud → operator infers an effect" },
      "calibration_age_hr": { "units": "hr", "soft_high": 168, "hard_high": 336 },
      "collection_backlog": { "units": "count", "soft_high": 10, "hard_high": 20 },
      "downlink_backlog_mb":{ "units": "MB", "soft_high": 4000, "hard_high": 8000 }
    }
  },
  "command_db": [
    { "verb": "adcs.slew_to",        "roles": ["bus"],     "delivery": ["uplink","stored"], "consumes": {"wheel_momentum": "variable"}, "gates": ["in_window_or_stored","not_safe_mode"], "params_schema": {"target":"attitude|object","execute_at":"time|next_window"}, "reversible": true },
    { "verb": "adcs.desaturate",     "roles": ["bus"],     "delivery": ["uplink","stored"], "consumes": {"delta_v_ms": 0.2}, "gates": ["in_window_or_stored"], "reversible": true },
    { "verb": "adcs.set_mode",       "roles": ["bus"],     "delivery": ["uplink"], "gates": ["in_window"], "params_schema": {"mode":"nadir|inertial|sun|target_track"}, "reversible": true },
    { "verb": "eps.shed_load",       "roles": ["bus"],     "delivery": ["uplink","stored"], "gates": [], "reversible": true, "_comment": "may disable payload" },
    { "verb": "eps.set_charge_mode", "roles": ["bus"],     "delivery": ["uplink","stored"], "gates": [], "reversible": true },
    { "verb": "prop.maneuver",       "roles": ["bus"],     "delivery": ["uplink","stored"], "consumes": {"delta_v_ms": "variable"}, "gates": ["in_window_or_stored","fuel_available","not_safe_mode"], "params_schema": {"burn_vector_ms":"vec3","execute_at":"time|next_window"}, "reversible": false, "cost_preview": "delta_v" },
    { "verb": "prop.collision_avoid","roles": ["bus"],     "delivery": ["uplink","stored"], "consumes": {"delta_v_ms": 0.5}, "gates": ["conjunction_alert"], "reversible": false },
    { "verb": "cdh.dump_storage",    "roles": ["bus"],     "delivery": ["downlink"], "gates": ["in_downlink_window"], "reversible": true, "_comment": "recovers out-of-contact history incl. safe-mode discovery" },
    { "verb": "cdh.clear_fault",     "roles": ["bus"],     "delivery": ["uplink"], "gates": ["in_window"], "reversible": true },
    { "verb": "cdh.load_stored_program","roles":["bus"],   "delivery": ["uplink"], "gates": ["in_window","storage_available"], "reversible": true },
    { "verb": "comms.point_antenna", "roles": ["bus"],     "delivery": ["uplink","stored"], "gates": [], "reversible": true },
    { "verb": "isr.schedule_collection","roles":["payload"],"delivery":["uplink","stored"], "gates": ["target_pass_exists","storage_available","not_safe_mode"], "params_schema": {"target":"ground_point|object","mode":"spot|strip"}, "reversible": true },
    { "verb": "isr.collect_now",     "roles": ["payload"], "delivery": ["realtime","stored"], "gates": ["over_target","attitude_ok","storage_available","not_safe_mode"], "reversible": true },
    { "verb": "isr.set_mode",        "roles": ["payload"], "delivery": ["uplink","stored"], "params_schema": {"mode":"pan|multispectral|ir"}, "gates": [], "reversible": true },
    { "verb": "isr.prioritize_downlink","roles":["payload"],"delivery":["uplink"], "gates": [], "reversible": true },
    { "verb": "isr.downlink",        "roles": ["payload"], "delivery": ["downlink"], "gates": ["in_downlink_window","has_data"], "reversible": true },
    { "verb": "isr.assess_quality",  "roles": ["payload"], "delivery": ["realtime"], "gates": ["in_contact"], "reversible": true },
    { "verb": "isr.calibrate",       "roles": ["payload"], "delivery": ["uplink","stored"], "gates": [], "reversible": true },
    { "verb": "def.maneuver_evade",  "roles": ["bus"],     "delivery": ["uplink","stored"], "consumes": {"delta_v_ms": "variable"}, "gates": ["fuel_available"], "reversible": false, "cost_preview": "delta_v" },
    { "verb": "def.harden",          "roles": ["bus"],     "delivery": ["uplink"], "gates": [], "reversible": true }
  ],
  "vulnerabilities": [
    { "effect": "directed_energy_dazzle", "likelihood": "high", "_comment": "shows as last_image_quality drop during a pass" },
    { "effect": "ew_downlink_jam",        "likelihood": "high", "_comment": "blocks isr.downlink near the jammer" },
    { "effect": "cyber_corrupt",          "likelihood": "med",  "intended_outcome": "degrade" },
    { "effect": "cyber_safe_mode",        "likelihood": "med",  "intended_outcome": "safe_mode", "vector": "ground_modem" },
    { "effect": "co_orbital_inspect",     "likelihood": "med" },
    { "effect": "da_asat",                "likelihood": "low",  "escalation": "high", "debris_risk": "high" }
  ],
  "defenses_available": ["maneuver","deception","hardening","dispersal","redundancy","frequency_hop","patch_cyber"]
}
```

---

## Template 2 — `SATCOM_GEO` (exquisite GEO communications satellite, e.g., Blue HVA)

```json
{
  "template_id": "SATCOM_GEO",
  "_comment": "High-value GEO wideband SATCOM. Near-continuous contact (control station always in view). Almost unkillable kinetically; the fight is jam/cyber/RPO. Big lifetime fuel tank but every km/s of relocation costs years.",
  "kind": "satellite",
  "payload_type": "satcom",
  "default_regime": "GEO",
  "provides": ["satcom","data_relay"],
  "resources_default": {
    "delta_v_ms": 750,
    "delta_v_ms_initial": 750,
    "annual_upkeep_ms": 50,
    "_comment_dv": "~50 m/s/yr station-keeping → ~15 yr design life. A 150 m/s slot relocation = 3 yr of life. Surfaced in the delta-v gauge.",
    "power_w": 12000,
    "ammo": 0
  },
  "comms_default": { "isl_capable": true, "isl_peers": [], "stored_program": true,
    "_comment": "ISL-capable: can relay commands to peers without their ground pass." },
  "telemetry_db": {
    "bus": {
      "battery_soc":        { "units": "frac", "soft_low": 0.50, "hard_low": 0.30, "_comment": "eclipse season matters even at GEO" },
      "bus_voltage_v":      { "units": "V",    "soft_low": 95,  "hard_low": 90, "soft_high": 105, "hard_high": 110 },
      "ns_stationkeep_err_deg": { "units": "deg", "soft_high": 0.04, "hard_high": 0.05, "_comment": "inclination drift; the 95% delta-v cost" },
      "ew_stationkeep_err_deg": { "units": "deg", "soft_high": 0.04, "hard_high": 0.05, "_comment": "longitude hold" },
      "propellant_frac":    { "units": "frac", "soft_low": 0.20, "hard_low": 0.05 },
      "component_temp_c":   { "units": "C",    "soft_high": 50, "hard_high": 65 }
    },
    "payload": {
      "transponder_power_pct": { "units": "%", "soft_high": 90, "hard_high": 100 },
      "transponder_temp_c":    { "units": "C", "soft_high": 55, "hard_high": 70 },
      "interference_level":    { "units": "frac", "soft_high": 0.3, "hard_high": 0.6, "_comment": "HOW JAMMING IS EXPERIENCED — not a 'you are jammed' label" },
      "link_utilization_pct":  { "units": "%", "soft_high": 85, "hard_high": 98 },
      "carrier_to_noise_db":   { "units": "dB", "soft_low": 8, "hard_low": 5 }
    }
  },
  "command_db": [
    { "verb": "prop.stationkeep",    "roles": ["bus"], "delivery": ["uplink","stored"], "consumes": {"delta_v_ms": 1.0}, "gates": ["in_window_or_stored"], "reversible": false },
    { "verb": "prop.maneuver",       "roles": ["bus"], "delivery": ["uplink","stored"], "consumes": {"delta_v_ms": "variable"}, "gates": ["fuel_available","not_safe_mode"], "params_schema": {"target_longitude_deg":"float","execute_at":"time|next_window"}, "reversible": false, "cost_preview": "delta_v", "_comment": "slot relocation; preview shows years-of-life spent" },
    { "verb": "prop.collision_avoid","roles": ["bus"], "delivery": ["uplink","stored"], "consumes": {"delta_v_ms": 0.5}, "gates": ["conjunction_alert"], "reversible": false },
    { "verb": "eps.set_charge_mode", "roles": ["bus"], "delivery": ["uplink","stored"], "gates": [], "reversible": true },
    { "verb": "cdh.dump_storage",    "roles": ["bus"], "delivery": ["downlink","realtime"], "gates": ["in_contact"], "reversible": true },
    { "verb": "cdh.clear_fault",     "roles": ["bus"], "delivery": ["uplink","realtime"], "gates": ["in_contact"], "reversible": true },
    { "verb": "comms.enable_isl",    "roles": ["bus"], "delivery": ["uplink"], "gates": ["isl_capable","peer_in_geometry"], "reversible": true },
    { "verb": "satcom.set_transponder",     "roles": ["payload"], "delivery": ["uplink","realtime"], "consumes": {"power_w":"variable"}, "gates": ["not_safe_mode"], "reversible": true },
    { "verb": "satcom.set_frequency_plan",  "roles": ["payload"], "delivery": ["uplink"], "gates": [], "reversible": true },
    { "verb": "satcom.reconfigure_beam",    "roles": ["payload"], "delivery": ["uplink"], "gates": ["flexible_payload"], "reversible": true, "_comment": "only if asset is flexible/SDR payload" },
    { "verb": "satcom.shift_users",         "roles": ["payload"], "delivery": ["uplink","realtime"], "gates": ["capacity_available"], "reversible": true, "_comment": "key jam-mitigation move" },
    { "verb": "satcom.mitigate_interference","roles": ["payload"], "delivery": ["uplink","realtime"], "gates": ["antijam_capability"], "reversible": true },
    { "verb": "satcom.report_interference", "roles": ["payload"], "delivery": ["realtime"], "gates": ["in_contact"], "reversible": true, "_comment": "feeds geolocation/attribution" },
    { "verb": "def.frequency_hop",   "roles": ["payload"], "delivery": ["uplink","realtime"], "gates": [], "reversible": true },
    { "verb": "def.patch_cyber",     "roles": ["bus"], "delivery": ["uplink","realtime"], "gates": [], "reversible": true },
    { "verb": "def.escort_posture",  "roles": ["bus"], "delivery": ["uplink"], "gates": ["escort_available"], "reversible": true }
  ],
  "vulnerabilities": [
    { "effect": "ew_uplink_jam",   "likelihood": "high", "_comment": "denies the whole transponder; seen as interference_level spike" },
    { "effect": "ew_downlink_jam", "likelihood": "med" },
    { "effect": "cyber_hijack",    "likelihood": "med",  "intended_outcome": "deny", "vector": "ground_modem", "_comment": "the Viasat-style ground/user segment attack" },
    { "effect": "cyber_safe_mode", "likelihood": "low",  "intended_outcome": "safe_mode", "vector": "ttc_path" },
    { "effect": "co_orbital_shadow","likelihood": "med", "_comment": "GEO RPO close-in collection / latent threat" },
    { "effect": "da_asat",         "likelihood": "very_low", "_comment": "GEO kinetic intercept extremely hard" }
  ],
  "defenses_available": ["maneuver","hardening","frequency_hop","patch_cyber","escort","disaggregation"]
}
```

---

## Template 3 — `CO_ORBITAL_EFFECTOR` (Red co-orbital ASAT / inspector)

```json
{
  "template_id": "CO_ORBITAL_EFFECTOR",
  "_comment": "Red maneuverable inspector/effector. Maneuvering IS its mission, so a big tank — but still finite: chase everything and it strands itself. Ambiguous payload (inspect vs. grapple vs. close-jam vs. dazzle) drives attribution uncertainty.",
  "kind": "satellite",
  "payload_type": "space_control",
  "default_regime": "GEO",
  "provides": ["rpo","inspection","co_orbital_effect"],
  "resources_default": {
    "delta_v_ms": 1400,
    "delta_v_ms_initial": 1400,
    "annual_upkeep_ms": 50,
    "_comment_dv": "Large tank for phasing/closing. RPO approach + multi-day station-hold can cost 50-200+ m/s each; the operator must ration across the exercise.",
    "power_w": 4000,
    "ammo": 0
  },
  "comms_default": { "isl_capable": false, "isl_peers": [], "stored_program": true },
  "telemetry_db": {
    "bus": {
      "battery_soc":     { "units": "frac", "soft_low": 0.40, "hard_low": 0.25 },
      "propellant_frac": { "units": "frac", "soft_low": 0.25, "hard_low": 0.05, "_comment": "watch this — running dry strands the asset" },
      "attitude_error_deg": { "units": "deg", "soft_high": 0.5, "hard_high": 2.0 }
    },
    "payload": {
      "range_to_target_km":   { "units": "km", "_comment": "the core RPO number; no alarm — it's tactical state" },
      "closing_rate_ms":      { "units": "m/s" },
      "effector_charge_pct":  { "units": "%", "soft_low": 20, "hard_low": 5, "_comment": "for jam/dazzle payloads" },
      "last_effect_assessment": { "units": "enum", "_comment": "unknown|likely|confirmed — effect BDA is uncertain" }
    }
  },
  "command_db": [
    { "verb": "prop.maneuver",     "roles": ["bus"], "delivery": ["uplink","stored"], "consumes": {"delta_v_ms":"variable"}, "gates": ["fuel_available","not_safe_mode"], "reversible": false, "cost_preview": "delta_v" },
    { "verb": "prop.stationkeep",  "roles": ["bus"], "delivery": ["uplink","stored"], "consumes": {"delta_v_ms":1.0}, "gates": [], "reversible": false },
    { "verb": "adcs.point_payload","roles": ["bus"], "delivery": ["realtime","stored"], "gates": ["valid_geometry"], "reversible": true },
    { "verb": "cdh.dump_storage",  "roles": ["bus"], "delivery": ["downlink"], "gates": ["in_downlink_window"], "reversible": true },
    { "verb": "sc.rpo_approach",   "roles": ["payload"], "delivery": ["uplink","stored"], "consumes": {"delta_v_ms":"variable"}, "gates": ["fuel_available","track_of_target"], "params_schema": {"target":"object","standoff_km":"float"}, "reversible": false, "cost_preview": "delta_v", "_comment": "closing window computed from phasing; observable by defender SDA" },
    { "verb": "sc.rpo_station",    "roles": ["payload"], "delivery": ["stored"], "consumes": {"delta_v_ms":"variable"}, "gates": ["at_proximity"], "reversible": false },
    { "verb": "sc.inspect",        "roles": ["payload"], "delivery": ["realtime"], "gates": ["at_proximity"], "reversible": true },
    { "verb": "sc.ew_jam",         "roles": ["payload"], "delivery": ["realtime","stored"], "gates": ["at_proximity","roe_permits"], "reversible": true, "intended_outcome": "deny" },
    { "verb": "sc.de_dazzle",      "roles": ["payload"], "delivery": ["realtime"], "gates": ["line_of_sight","roe_permits"], "reversible": true, "intended_outcome": "disrupt" },
    { "verb": "sc.engage_kinetic", "roles": ["payload"], "delivery": ["uplink","realtime"], "consumes": {"delta_v_ms":"variable"}, "gates": ["weapons_quality_track","roe_kinetic","at_proximity"], "reversible": false, "debris_risk": "high", "intended_outcome": "destroy", "_comment": "high-end escalation; spawns debris + political consequence" }
  ],
  "vulnerabilities": [
    { "effect": "co_orbital_inspect", "likelihood": "med", "_comment": "Blue can inspect it back" },
    { "effect": "ew_uplink_jam",      "likelihood": "med" },
    { "effect": "cyber_safe_mode",    "likelihood": "low", "intended_outcome": "safe_mode", "vector": "ttc_path" },
    { "effect": "da_asat",            "likelihood": "low", "escalation": "high" },
    { "effect": "fuel_exhaustion",    "likelihood": "self_inflicted", "_comment": "the real risk: over-maneuvering strands it" }
  ],
  "defenses_available": ["maneuver","deception"]
}
```

---

## Instantiation example — these templates inside a vignette

Asset instances reference a template and override only instance-specific fields (orbit/TLE,
name, owner, ground segment, starting fuel if scenario-specific). From the Vignette 2 (GEO RPO)
setup:

```json
{
"assets": [
  {
    "id": "BLUE-SATCOM-1", "name": "MAPLE-1", "template": "SATCOM_GEO", "owner": "blue",
    "tle": ["1 40000U 25001A   30074.50000000  .00000000  00000-0  00000-0 0  9990",
            "2 40000   0.0300  90.0000 0001000   0.0000 110.0000  1.00270000 00010"],
    "ground_segment": ["STATION-MAPLE","PROC-1"],
    "comms": { "isl_capable": true, "isl_peers": ["BLUE-SATCOM-2"] }
  },
  {
    "id": "RED-INSP-1", "name": "object 2030-099B", "template": "CO_ORBITAL_EFFECTOR", "owner": "red",
    "tle": ["1 40099U 25099B   30074.50000000  .00000000  00000-0  00000-0 0  9991",
            "2 40099   0.0500  91.0000 0002000   0.0000 108.5000  1.00250000 00012"],
    "ground_segment": ["RED-GS-1"],
    "_comment": "Starts ~1.5 deg east of MAPLE-1 in the GEO belt; will phase toward it."
  }
],
"roles_needed": {
  "blue": [
    {"role_id":"blue_satcom_bus","label":"Blue SATCOM Bus Op","kind":"bus","assets":["BLUE-SATCOM-1","BLUE-SATCOM-2"]},
    {"role_id":"blue_satcom_pld","label":"Blue SATCOM Payload Op","kind":"payload","assets":["BLUE-SATCOM-1","BLUE-SATCOM-2"]},
    {"role_id":"blue_sda","label":"Blue SDA Op","kind":"payload","assets":["BLUE-SDA-1"]}
  ],
  "red": [
    {"role_id":"red_orbital","label":"Red Orbital Op","kind":"both","assets":["RED-INSP-1"]}
  ]
}
}
```

> Note how the **role split** uses the template's `command_db.roles` field: the *bus* op sees
> `prop.maneuver` / `cdh.*`; the *payload* op sees `satcom.*`. One person can hold both roles in
> a small exercise (assign both `role_id`s to one seat), or two people split them for realism.

---

## Checklist for replicating to the remaining templates
For each remaining mission type in `05-mission-types-and-counters.md` (ISR_SAR, SIGINT, SDA_GEO,
PNT_MEO, MISSILE_WARNING, WEATHER, plus Red EW/DE/cyber/DA-ASAT effector variants), produce a
template with:
1. `template_id`, `kind`, `payload_type`, `default_regime`, `provides`.
2. `resources_default` with delta-v sized to the regime/role and the right `annual_upkeep_ms`
   (`14-delta-v-economy.md` §2).
3. `telemetry_db` — the handful of bus SOH params (reuse the common set) plus 3–5 payload-
   specific params with soft/hard limits.
4. `command_db` — bus verbs (mostly common) + the payload verbs for that type from
   `13-operator-command-catalog.md`, each tagged with `roles`, `delivery`, `gates`, `consumes`.
5. `vulnerabilities` — ordered, realism-weighted, from the effect×mission matrix in
   `03-counterspace-taxonomy.md`, including a `cyber_safe_mode` entry where plausible.
6. `defenses_available`.

Keep the **bus block nearly identical** across satellite templates (the bus is generic); vary
the **payload block** by mission. That mirrors reality and minimizes Claude Code's work.
