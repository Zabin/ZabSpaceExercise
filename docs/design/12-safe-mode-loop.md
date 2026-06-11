# Safe-Mode: Attack, Detection & Recovery Loop

Safe mode is a realistic, **reversible** way to take a satellite "off the board" without
debris — which makes it powerful and therefore a balance risk. If inducing safe mode were a
guaranteed one-click effect with no counterplay, it would dominate the game and crowd out the
kinetic/co-orbital lessons. This document specifies the **full loop** — how an attacker induces
it, how a defender *detects, diagnoses, and recovers*, and the **White Cell dials** that make
the whole thing tunable rather than baked in. It builds on
`../research/06-bus-and-payload-operations.md`, `04-data-model.md`, and the cyber/EW effects in
`../research/03-counterspace-taxonomy.md`.

## 1. Design goals
1. **Reversible but costly.** Safe mode should cost the attacker something to induce and the
   defender real passes/effort to recover — not a free kill, not a trivial reset.
2. **Counterplay exists.** The defender can harden against it, detect it faster, and recover
   faster through preparation and good play.
3. **Uncertain and pass-gated.** Inducing it isn't guaranteed; *learning* it happened is gated
   by contact windows; *recovering* it competes for the same scarce windows.
4. **Fully tunable.** White Cell sets how easy it is to induce and how punishing it is to
   recover, so the same mechanic suits an intro vignette or a brutal capstone.

## 2. The loop at a glance
```
ATTACKER                         ENGINE                         DEFENDER
  induce attempt  ───────────▶  susceptibility check  ───────▶  (maybe) enters safe mode
  (cyber/EW/bus stress)           (prob vs. hardening)            payload OFF, autonomy protects bus
                                       │
                                       ▼
                                 DETECTION (pass-gated):
                                 anomaly cues → confirmed at contact
                                       │
                                       ▼
                                 DIAGNOSIS: why did it safe?
                                 (fault vs. attack; which subsystem)
                                       │
                                       ▼
                                 RECOVERY: multi-step procedure
                                 across one or more passes
                                       │
                                       ▼
                                 back to NOMINAL (payload on)
```

## 3. Inducement — how an attacker triggers safe mode
Safe mode can be entered from (a) a genuine **bus fault** (power crisis in long eclipse,
attitude upset, thermal excursion), (b) an **environmental** trigger (space weather), or (c) an
**attack** — specific cyber and EW effects whose *intended_outcome* is to safe the target:

- **Cyber:** a successful command-path or FSW exploit can command safe mode or trip a fault
  monitor. Not pass-gated (cyber's special property), but depends on a modeled access vector
  and the target's cyber posture.
- **EW / link:** sustained uplink jamming can starve the satellite of commands and trip a
  command-loss timer; aggressive interference can induce protective responses.
- **Bus stress:** an attacker who forces excessive maneuvering (e.g., repeated RPO threats
  driving evasions) can drain propellant/power toward a fault.

**Inducement is a probabilistic `susceptibility check`, not automatic** (see §6 formula). It is
modeled as an `EffectInstance` with `intended_outcome: safe_mode` and resolved by the
`EffectResolver`.

## 4. Detection — the defender finds out (pass-gated)
The defender does **not** get an instant "your satellite is in safe mode" banner (that would be
unrealistic and would remove the SDA/telemetry lesson). Instead:

1. **Indirect cues first.** The payload stops producing (no imagery, dropped SATCOM carrier,
   lost track) — the operator notices a *symptom*. Optionally, an SDA observation shows the
   satellite has slewed to a sun-pointing attitude (a safe-mode signature) — but only if the
   defender tasks a sensor and gets a look.
2. **Confirmation at the next contact.** True confirmation comes when the satellite's
   **stored telemetry dumps at the next ground/relay/ISL pass**, revealing it entered safe mode
   (and a timestamp showing how long ago). Until then the operator is reasoning from symptoms.
3. **Detection speed is a function of preparation** (see dials): threat-warning posture, sensor
   tasking on own assets, and ground-station density all shrink time-to-detect.

> Teaching point: a defender who has *let custody of their own fleet's health lapse* (few
> passes, no threat warning) may not realize a satellite is down until a decision window has
> already passed.

## 5. Diagnosis & recovery — the defender's mini-loop
Once detected/confirmed, recovery is a **multi-step procedure executed across contact windows**,
not a button:

### 5.1 Diagnose
- Determine **why** it safed: genuine fault vs. attack, and which subsystem. Diagnosis quality
  depends on telemetry available at contact and the operator's actions. **Attribution of an
  attack-induced safe mode is deliberately hard** (consistent with the cyber/EW ambiguity in the
  taxonomy) — the defender may recover without ever being sure it was attacked.

### 5.2 Recover (procedure across passes)
A recovery is an ordered `PlannedActivity` chain (kind `command`) that must be uplinked over one
or more passes. A representative procedure:
1. **Contact & assess** — establish uplink lock, dump stored telemetry. *(pass 1)*
2. **Clear fault flags / re-enable subsystems** — bring EPS rails, ADCS mode back to nominal.
3. **Re-establish attitude/pointing** — slew from sun-point back to mission attitude.
4. **Re-enable payload** — power and initialize the payload.
5. **Verify nominal** — confirm SOH green before resuming mission. *(may be pass 2+)*

Each step can **fail** (bad pass geometry, persistent cyber presence, insufficient power) and
require a retry on a later pass. **If the inducing cause persists** (e.g., the cyber foothold
isn't evicted, or jamming continues), recovery can be **re-safed** — the defender must address
the root cause (patch the vuln, kill/relocate the jammer) or keep losing the satellite.

### 5.3 Cost
Recovery consumes **passes** (the scarce resource), some **power/propellant**, and **operator
attention** (in `full_ttc` fidelity it competes with other tasking). The mission output lost
during downtime is the real price.

## 6. The tunable model (formulas the engine implements)

### 6.1 Inducement susceptibility
```
P(enter_safe_mode) = base_susceptibility[effect_type]
                     × white_cell_safe_mode_susceptibility   # the master dial (see §7)
                     × (1 − hardening_factor)                # defender passive defense
                     × posture_factor                        # cyber/EW posture, threat-warning
                     × persistence_bonus                     # sustained vs. one-shot attempts
   clamped to [0, 0.98]   # never a guaranteed safe; never fully immune unless hardened off
```

### 6.2 Time-to-detect
```
detect_delay = base_detect_window
             ÷ detection_readiness        # threat-warning + self-SDA tasking + station density
   ── but symptom cues (payload stopped) appear immediately;
      CONFIRMATION still waits for the next telemetry-bearing contact.
```

### 6.3 Recovery difficulty
```
recovery_passes_needed = base_recovery_passes
                        × white_cell_recovery_difficulty       # the second master dial
                        × root_cause_penalty                   # ×N if inducing cause persists
   per-step success gated by pass quality, power, and (for cyber) whether the vuln is patched.
```

## 7. White Cell dials (added to the parameter schema)
These appear in the White Cell parameter panel (`06-white-cell-controls.md`) and are
**live-tunable** so a facilitator can adjust difficulty mid-exercise.

| Parameter | Type | Default | Affects |
|---|---|---|---|
| `safe_mode_susceptibility` | enum: `robust / realistic / fragile` | `realistic` | Master multiplier on `P(enter_safe_mode)`. `robust` = satellites rarely safe (focus on other effects); `fragile` = easy to safe (stress recovery skills). |
| `safe_mode_recovery_difficulty` | enum: `quick / realistic / punishing` | `realistic` | Multiplier on `recovery_passes_needed`. `quick` = 1 pass; `punishing` = multi-pass with retries. |
| `safe_mode_detection_aid` | enum: `realistic / coached / fog` | `realistic` | `coached` gives an early explicit alert (training wheels); `fog` forces pure symptom-based detection. |
| `safe_mode_attack_enabled` | bool | `true` | Whether cyber/EW may target safe mode at all in this vignette. |
| `safe_mode_root_cause_persists` | bool | `true` | If true, recovery fails/re-safes unless the defender removes the cause (patch vuln, kill jammer). |

Defender-side **preparation** that interacts with these (set via `blue_passive_defenses` and
posture, not White-Cell-only):
- **Hardening** → raises `hardening_factor`, lowering inducement probability.
- **Threat warning + redundancy** → raises `detection_readiness`, lowering detect delay.
- **Cyber posture / patching** → reduces cyber inducement and prevents re-safing.
- **Dispersal/proliferation** → one safed satellite matters less (a constellation absorbs it).

## 8. Data-model additions (canonical schema in `04-data-model.md`)
```yaml
# Extends Asset.bus_state:
safe_mode:
  active: false
  entered_at: SimTime | null
  cause: null            # fault | environment | cyber | ew | bus_stress (truth; White-Cell-visible)
  defender_confirmed: false        # has the defender confirmed via contact?
  defender_diagnosis: unknown      # unknown | suspected_attack | fault | <subsystem>
  recovery:
    plan: [PlannedActivity...]     # the recovery procedure chain
    step_index: 0
    passes_used: 0
    blocked_reason: null           # e.g., "root cause persists: unpatched ground_modem"
```
Effect templates that can induce it carry `intended_outcome: safe_mode` and read the §6.1
formula in the `EffectResolver`.

## 9. Build integration
- **Phase 3.5** (bus/payload model) implements `bus_state.safe_mode` and the inducement
  susceptibility check.
- **Phase 4.5** (planning/tasking scheduler) implements the **recovery procedure chain** as a
  `PlannedActivity` sequence and the re-safe-on-persistence logic.
- **Phase 5/5.5** (UI/3D) surface symptom cues, the pass-gated confirmation, the diagnosis
  panel, and the recovery checklist; the 3D viewer can show a tracked own-asset's safe-mode
  attitude signature if a sensor is tasked on it.
- **Done-when (loop test):** with `safe_mode_susceptibility=fragile`, a cyber effect safes a
  Blue ISR sat; Blue sees the payload stop, infers a problem, confirms it at the next pass,
  runs a multi-pass recovery, and — because `safe_mode_root_cause_persists=true` and the modem
  vuln is unpatched — gets **re-safed** until Blue patches the vuln; then setting
  `safe_mode_recovery_difficulty=quick` collapses recovery to a single pass.

## 10. Why this preserves balance
Safe mode becomes a **tempo weapon, not a kill**: the attacker buys *time* (payload downtime)
at the cost of effort and uncertainty, and a prepared, attentive defender can blunt it through
hardening, fast detection, and clean recovery — while a careless one pays in lost passes. White
Cell decides where on that spectrum each exercise sits.
