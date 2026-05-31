# Vignette Framework & Parameter Schema

A **vignette** is a self-contained scenario the White Cell selects and tunes. Vignettes are
**data files** (YAML/JSON) loaded by the engine — never hard-coded — so new ones can be
authored without touching the simulator. This file defines the common structure and the
parameters White Cell can modify. Each of the eight vignette files conforms to this schema.

## Authoring philosophy

- **Teach one or two ideas well.** Each vignette has explicit learning objectives drawn from
  doctrine (e.g., "RPO intent is ambiguous," "PNT denial is local and reversible").
- **Start small, scale via parameters.** The same base scenario can be a 30-minute teaching
  set-piece or a 3-hour free-play depending on White Cell's parameter choices.
- **Realism over balance.** Asymmetry is the point. Red and Blue need not have equal tools.

## Common vignette structure

```yaml
vignette:
  id: leo-isr-denial
  title: "LEO ISR Denial"
  classification: UNCLASSIFIED-TRAINING
  learning_objectives:
    - "Internalize that LEO targets are reachable only during short passes."
    - "Weigh reversible (dazzle/jam) vs. non-reversible (kinetic) effects."
  doctrinal_basis: [orbital_warfare, electromagnetic_warfare, directed_energy]
  red_doctrine_profile: pla_early_disruption   # or russia_ew_first, generic
  estimated_duration_min: 60

  # --- THE SETTING ---
  start_epoch_utc: "2030-03-15T06:00:00Z"
  geography:
    theater: "generic Indo-Pacific island chain"   # fictional by default
    blue_ground_sites: [...]
    red_ground_sites: [...]
  orbital_environment:
    debris_fields: []          # pre-existing hazards
    space_weather: nominal     # nominal | degraded (affects DE/optical)

  # --- ORDERS OF BATTLE (asset instances from templates) ---
  blue_forces: [ ...asset instances... ]
  red_forces:  [ ...asset instances... ]

  # --- WIN CONDITIONS (per doctrine: control of a regime over a window for a purpose) ---
  objectives:
    blue:
      - {id: protect_isr, desc: "Maintain ISR custody of Red surface group", metric: ...}
    red:
      - {id: deny_isr, desc: "Deny Blue imagery during the landing window", metric: ...}
  escalation_thresholds:
    debris_generating_strike: {political_cost: high, triggers_inject: un_condemnation}

  # --- WHITE CELL TUNABLE PARAMETERS (the dials) ---
  parameters: [ ...see schema below... ]

  # --- SCRIPTED INJECTS (optional, White Cell can fire manually too) ---
  injects: [ ...see schema below... ]
```

## Tunable parameter schema (the White Cell "dials")

Every vignette exposes a typed parameter list. The White Cell UI renders each as a control.
**All parameters have safe defaults so a vignette runs unmodified.**

```yaml
parameters:
  - id: red_ew_intensity
    label: "Red EW Intensity"
    type: enum            # enum | int | float | bool | duration | time | asset_count
    options: [none, harassment, sustained, total]
    default: sustained
    affects: "Number/power of Red jammers and how aggressively AI-Red employs them."

  - id: blue_ground_station_count
    label: "Blue Ground Stations Available"
    type: int
    min: 1
    max: 6
    default: 3
    affects: "More stations = more/longer command windows = tighter control loop."

  - id: red_kinetic_authorized
    label: "Red Kinetic ASAT Authorized"
    type: bool
    default: false
    affects: "Whether AI-Red or Red Cell may employ debris-generating strikes."

  - id: time_compression_default
    label: "Default Time Multiplier"
    type: enum
    options: [1x, 10x, 60x, 600x]
    default: 60x
    affects: "How fast sim time runs at start (White Cell can change live)."

  - id: rpo_closing_speed
    label: "Red RPO Aggressiveness"
    type: enum
    options: [cautious, normal, aggressive]
    default: normal
    affects: "Delta-v Red spends to close on Blue assets; faster closing = earlier threat."

  - id: blue_passive_defenses
    label: "Blue Passive Defenses Enabled"
    type: multiselect
    options: [maneuver, deception, hardening, dispersal, redundancy]
    default: [maneuver, deception]
    affects: "Which survivability measures Blue starts with."

  - id: attribution_difficulty
    label: "Attribution Difficulty"
    type: enum
    options: [easy, realistic, fog]
    default: realistic
    affects: "How quickly/confidently a victim can attribute an ambiguous (RPO/EW/DE) attack."

  - id: fog_of_war
    label: "Fog of War"
    type: enum
    options: [full_god_view, realistic_sda, heavy_fog]
    default: realistic_sda
    affects: "How much each cell sees of the other's assets beyond its own SDA custody."
```

### Parameter categories every vignette should expose
1. **Force levels** — counts/quality of each side's assets and ground stations.
2. **Authorities / ROE** — what each side is *allowed* to do (kinetic on/off, escalation
   caps). This is how White Cell teaches restraint and escalation control.
3. **Red behavior** — doctrine profile, aggressiveness, EW intensity, RPO posture.
4. **Environment** — start epoch, debris, space weather, geography.
5. **Fidelity / fog** — SDA visibility, attribution difficulty, time compression.

## Inject schema (events White Cell injects, scripted or manual)

```yaml
injects:
  - id: commercial_imagery_leak
    label: "Commercial imagery reveals Blue carrier position"
    trigger: {type: time, at_sim: "T+00:45:00"}   # or {type: manual} or {type: condition, ...}
    effects:
      - {type: reveal_asset, target: blue_carrier, to: red}
      - {type: message, to: [blue, white], text: "OSINT leak detected."}
    repeatable: false
```

Inject effect types the engine supports: `reveal_asset`, `degrade_asset`, `spawn_asset`,
`change_roe`, `inject_debris`, `message`, `modify_parameter`, `fail_ground_station`,
`patch_cyber_vuln`, `political_consequence`.

## Decision paths & branching

A vignette is not a fixed script — it **forks based on what the cells do**. Branching is what
makes a vignette replayable (rewind and try a different path) and what teaches consequence. The
engine supports branching through **condition-triggered injects** plus an optional explicit
**decision-path map** the author can declare for clarity and for the White Cell's situational
awareness.

### Condition triggers (the mechanism)
Any inject's `trigger` can be a `condition` evaluated continuously against game state:
```yaml
trigger:
  type: condition
  when: "red_inspector.range_to(blue_hva) < 5_km AND sim_time > 'T+00:20'"
  once: true            # fire once, or re-arm
```
Supported condition terms: asset range/relative-geometry, custody/characterization state, an
asset's health/safe-mode/fuel state, whether a specific effect has occurred, ROE level, elapsed
sim time, and parameter values. This lets a scenario react to player choices without scripting.

### The decision-path map (authoring clarity + White Cell SA)
Authors may declare the **key forks** a vignette is designed around, so the White Cell can see
"where are we on the tree" and so the design intent is explicit:
```yaml
decision_paths:
  - id: rpo_response_fork
    label: "Blue's response to Red's close approach"
    branches:
      - id: passive_monitor
        when: "blue takes no action by T+00:40"
        leads_to: "Red achieves sustained collection (Red objective met)"
      - id: maneuver_away
        when: "blue executes def.maneuver_evade"
        leads_to: "HVA safe but burns fuel — see delta-v consequence path"
      - id: interpose_escort
        when: "blue sets escort point-defense"
        leads_to: "standoff; characterization race"
      - id: counterattack
        when: "blue engages red_inspector"
        leads_to: "escalation; attribution/ROE scrutiny inject fires"
```
The decision-path map is **descriptive, not prescriptive** — players can always do something
unforeseen; the map just captures the intended teaching forks and ties each to consequences and
follow-on injects. White Cell sees which branch the exercise is on in the facilitator dashboard.

### Branch consequences chain
A branch typically fires follow-on injects and may open *further* forks, producing a shallow
tree (keep it shallow — 2–3 levels — for a single-sitting exercise). Because the engine is
deterministic, White Cell can **rewind to a fork and let the cell try a different branch** — the
core "learn from your choice" mechanic and the seed of the v2 branch-to-live replay feature.

## The eight vignettes in this package

| # | File | Primary domains | Teaches |
|---|---|---|---|
| 1 | `01-leo-isr-denial.md` | Orbital, EW, DE | LEO pass windows; reversible vs. kinetic |
| 2 | `02-geo-rpo-shadowing.md` | Orbital (RPO) | Ambiguous intent; escort vs. shadow in GEO |
| 3 | `03-gnss-ew-campaign.md` | EW | Local/reversible PNT denial; MEO is kinetically safe |
| 4 | `04-co-orbital-threat-escort.md` | Orbital | Active defense: escort, maneuver-to-evade |
| 5 | `05-da-asat-crisis.md` | Orbital (kinetic) | Escalation, debris, attribution, political cost |
| 6 | `06-satcom-cyber-link.md` | Cyber, EW | Ground/link segment; cyber acts outside passes |
| 7 | `07-sda-custody-hunt.md` | SDA | Custody decay; suppression of counterspace targeting |
| 8 | `08-multi-domain-taiwan.md` | All | Integrated campaign; space enabling joint fires |

Each file below gives the narrative, learning objectives, OOB sketch, the key tunable
parameters, sample injects, and victory conditions — enough for Claude Code to encode it as
a data file and for White Cell to understand what each dial does.
