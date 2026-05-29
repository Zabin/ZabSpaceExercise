# Operator Command Catalog — Bus & Payload Commands by Mission

This file fills a gap the rest of the package only referenced abstractly: the **actual list of
commands** an operator can issue, split by **bus** vs. **payload** and by **mission type**. It is
the source for each asset template's `command_db` (`04-data-model.md`) and the order panel
(`05-cell-interfaces.md`). Commands here are deliberately **operationally representative, not
exhaustive** — enough to make each role feel real without modeling a true flight command
dictionary. Every command is a `PlannedActivity` of kind `command`
(`11-command-planning-and-tasking.md`).

## How to read each command
```
verb            human label                 delivery        cost / gate                 effect
```
- **delivery:** `uplink` (needs ground pass), `isl` (needs crosslink), `stored` (onboard,
  time/condition-triggered), `realtime` (only while in contact).
- **cost / gate:** resources consumed and preconditions (window, track, ROE, bus health).
- All commands re-validate at execution (FR-P4). Illegal → blocked with reason; legal-but-unwise
  → allowed to run (NFR-6).

---

## PART 1 — BUS COMMANDS (common to all satellites)

These are available to whoever holds the **bus operator** role for the asset (may be the same
person as the payload operator in small exercises — OR-2).

### 1.1 Electrical Power (EPS)
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `eps.shed_load` | Shed non-critical loads | uplink/stored | bus in contact or stored | frees power; may disable payload |
| `eps.restore_load` | Restore loads | uplink | power margin available | re-enables shed items |
| `eps.set_charge_mode` | Set battery charge mode | uplink/stored | — | trickle/fast charge before eclipse |
| `eps.select_bus` | Switch power rail/bus | uplink | — | redundancy management |

### 1.2 Attitude & Pointing (ADCS/GNC)
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `adcs.slew_to` | Slew to attitude/target | uplink/stored | small delta-v if thrusters; wheel momentum | re-points payload/antenna/arrays |
| `adcs.set_mode` | Set pointing mode | uplink | — | nadir / inertial / sun / target-track |
| `adcs.desaturate` | Desaturate reaction wheels | uplink/stored | small delta-v or magnetorquer time | sheds stored momentum |
| `adcs.point_payload` | Point payload at target | realtime/stored | valid geometry | aims sensor/effector |

### 1.3 Propulsion / Maneuver
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `prop.maneuver` | Execute orbit maneuver (burn) | uplink/stored | **delta-v from budget** (see `14-delta-v-economy.md`) | changes orbit elements |
| `prop.stationkeep` | Station-keeping burn | uplink/stored | small delta-v | maintains slot/orbit |
| `prop.collision_avoid` | Collision-avoidance maneuver | uplink/stored | small delta-v; conjunction alert | dodges a tracked hazard |
| `prop.cancel_burn` | Cancel a planned burn | uplink | queued burn not yet executed | removes from plan |

### 1.4 Thermal
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `tcs.set_heater` | Enable/disable heaters | uplink/stored | power | keeps components in limits |
| `tcs.set_mode` | Set thermal mode | uplink | — | survival/operational |

### 1.5 Command & Data Handling (C&DH / OBC)
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `cdh.set_time` | Sync onboard clock | uplink | contact | corrects time drift |
| `cdh.load_stored_program` | Upload stored/time-tagged commands | uplink | storage | enables autonomous actions |
| `cdh.clear_stored_program` | Clear stored commands | uplink | — | cancels onboard autonomy |
| `cdh.dump_storage` | Downlink stored telemetry/data | downlink pass | downlink window | recovers out-of-contact history |
| `cdh.reset_subsystem` | Reset a subsystem/FSW | uplink | — | anomaly recovery |
| `cdh.clear_fault` | Clear fault flags | uplink | — | step in safe-mode recovery |

### 1.6 Comms / TT&C
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `comms.config_link` | Set data rate / modulation | uplink | — | adjusts downlink throughput |
| `comms.point_antenna` | Point/steer antenna | uplink/stored | — | improves link / switches ground site |
| `comms.enable_isl` | Enable inter-satellite link | uplink | ISL-capable + peer geometry | opens crosslink relay path |
| `comms.set_crypto` | Cycle COMSEC/keys | uplink | — | link security hygiene |

### 1.7 Safe-mode recovery (bus) — the ordered chain (`12-safe-mode-loop.md`)
`comms.establish_contact` → `cdh.dump_storage` → `cdh.clear_fault` → `eps.restore_load` →
`adcs.set_mode(nominal)` → `adcs.slew_to(mission)` → `payload.enable` → `verify_nominal`.
Each step is a normal command; the chain spans one or more passes and can fail/retry.

---

## PART 2 — PAYLOAD COMMANDS (by mission type)

Available to whoever holds the **payload operator** role for the asset. Payload commands are
**gated by the bus** (FR-B2): no power/bad attitude/safe mode → most payload verbs are blocked
with that reason.

### 2.1 SATCOM
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `satcom.set_transponder` | Set transponder power/gain | uplink/realtime | power | adjusts capacity/reach |
| `satcom.set_frequency_plan` | Set freq/bandwidth plan | uplink | — | re-plans channels |
| `satcom.reconfigure_beam` | Steer/shape beam (flexible payload) | uplink | flexible-payload asset only | moves coverage |
| `satcom.shift_users` | Move users to another transponder/beam | uplink/realtime | capacity | mitigates interference/jam |
| `satcom.mitigate_interference` | Apply anti-jam (hop/null) | uplink/realtime | anti-jam capability | reduces jam effect |
| `satcom.report_interference` | Characterize interference | realtime | in contact | feeds geolocation/attribution |

### 2.2 ISR — EO/IR and SAR
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `isr.schedule_collection` | Add target to collection plan | uplink/stored | storage; target pass exists | images target on pass |
| `isr.set_mode` | Set imaging mode (spot/strip/IR/SAR mode) | uplink/stored | — | trades resolution/area |
| `isr.collect_now` | Collect this pass | realtime/stored | over target + good attitude | captures imagery |
| `isr.prioritize_downlink` | Order the downlink queue | uplink | — | gets key image home first |
| `isr.downlink` | Downlink imagery | downlink pass | downlink window; storage has data | delivers product |
| `isr.calibrate` | Calibrate sensor | uplink/stored | — | maintains image quality |
| `isr.assess_quality` | Read last image quality | realtime | — | reveals dazzle/weather degradation |

### 2.3 SIGINT / ELINT
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `sigint.task_collection` | Task freq range / region | uplink/stored | over collection area | intercepts emissions |
| `sigint.set_band` | Set receiver band/dwell | uplink | — | trades coverage vs. sensitivity |
| `sigint.geolocate` | Prioritize emitter geolocation | uplink/realtime | multiple looks | produces emitter fix |
| `sigint.downlink` | Downlink intercept product | downlink pass | window | delivers SIGINT/geo product |

### 2.4 SDA (space-based surveillance / inspector) — see also tasking doc Part B
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `sda.task_search` | Search a regime/volume | uplink/stored | sensor geometry; task_capacity | finds new/unknown objects |
| `sda.task_track` | Maintain custody of an object | uplink/stored | a track exists | keeps uncertainty small |
| `sda.task_characterize` | Resolve object type/payload | uplink/stored | capable sensor + good pass | "?" → classified |
| `sda.cue` | Hand a track to another sensor | uplink | two sensors | radar→optical handoff |
| `sda.downlink` | Downlink track data | downlink pass | window | updates TrackCatalog |

### 2.5 Space-control (counterspace effectors)
| verb | label | delivery | cost / gate | effect |
|---|---|---|---|---|
| `sc.ew_jam` | Jam uplink/downlink | realtime/stored | in footprint; ROE | denies link (reversible) |
| `sc.ew_spoof` | Spoof signal | realtime/stored | in footprint; ROE | deceptive false signal |
| `sc.de_dazzle` | Dazzle sensor (directed energy) | realtime | LOS + clear atmosphere; ROE | degrades/blinds optic |
| `sc.rpo_approach` | Approach a target (RPO) | uplink/stored | **delta-v**; closing window | proximity for inspect/effect |
| `sc.rpo_station` | Hold close station | stored | delta-v for station-keep | shadow/escort |
| `sc.inspect` | Characterize at close range | realtime | proximity | high-quality characterization |
| `sc.engage_kinetic` | Kinetic strike | uplink/realtime | **weapons-quality track**; ROE=kinetic; ammo | destroy (debris!) |
| `sc.cyber_effect` | Network attack on target segment | **not pass-gated** | access vector; cyber posture | 5 D's incl. hijack/safe-mode |

### 2.6 PNT, Missile Warning, Weather (lighter set)
| verb | label | delivery | effect |
|---|---|---|---|
| `pnt.set_integrity` / `pnt.report_status` | manage/monitor signal integrity & timing | uplink/realtime | maintains/monitors PNT service |
| `mw.set_sensor_mode` / `mw.report_alerts` | manage IR staring; read alert pipeline | uplink/realtime | warning service; reveals dazzle/cyber tamper |
| `wx.schedule_collection` / `wx.downlink` | schedule sensing; downlink | uplink/downlink | weather product (simple ISR-like chain) |

---

## PART 3 — Defensive / posture commands (active & passive defense)
Available per `01-doctrine-western.md` §4; many are *postures* set once and left.
| verb | label | delivery | effect |
|---|---|---|---|
| `def.set_threat_warning` | Raise threat-warning posture | uplink | faster detection (incl. of safe-mode attacks) |
| `def.maneuver_evade` | Evade an approaching threat | uplink/stored | **delta-v**; breaks intercept geometry |
| `def.escort_posture` | Set escort point/area defense | uplink | bodyguard interposes |
| `def.harden` | Raise hardening posture | uplink | lowers effect/safe-mode susceptibility |
| `def.patch_cyber` | Patch a cyber vulnerability | uplink/realtime | closes a vector; prevents re-safe |
| `def.frequency_hop` | Enable freq hopping | uplink/realtime | reduces jam effect |
| `def.disperse` | Disperse/disaggregate (if capable) | uplink/stored | spreads risk across assets |

---

## PART 4 — How this becomes data
Each **asset template** declares which verbs it supports in its `command_db`, each with:
```yaml
command_db:
  - verb: prop.maneuver
    roles: [bus]                 # which role(s) may issue it
    delivery: [uplink, stored]
    consumes: {delta_v_ms: variable}
    gates: [in_window_or_stored, fuel_available, not_safe_mode]
    params_schema: {burn_vector_ms: vec3, execute_at: time|next_window}
    reversible: true
```
The order panel shows only the verbs whose `roles` match the seated operator's role and whose
`gates` can plausibly be met, annotating each with cost and earliest execution window. Bus vs.
payload separation falls straight out of the `roles` field (OR-2).

## Cross-references
- Delivery/window mechanics: `11-command-planning-and-tasking.md`.
- Effect resolution & ROE: `03-counterspace-taxonomy.md`.
- Delta-v costs and the lifetime trade: `14-delta-v-economy.md`.
- Per-asset legal sets: each template in the asset library (`05-mission-types-and-counters.md`).
