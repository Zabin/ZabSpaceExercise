# AUDIT 2026-06 (Commands) — Satellite Command Realism, Order-Form UX, and Probability Mechanics

**Date:** 2026-06-12 · **Branch:** `claude/planning-docs-review-rmZwP` ·
**Scope:** the order/command layer only — order actions in `spacesim/engine/orders.py`
(`jam`/`engage`/`observe`/`maneuver`/`downlink`/`cyber`/`command`), the ~57 catalog verbs in
`spacesim/engine/buscommands.py`, the per-domain databases (`jam.py`/`cyber.py`/`engage.py`/
`isr.py`/`sigint.py`), and the front-end Satellite Command panel
(`spacesim/ui_web/static/app.js` + `index.html`).

The prior audit (`docs/AUDIT-2026-06.md`) explicitly excluded a deep pass on command realism and
order-form UX — this is that pass. Everything here is open for redesign; no verb, parameter, or
schema is sacred.

---

## Methodology

Three parallel research streams:

1. **Consumer trace** — for every order action and every catalog verb, walk validator
   (`can_issue` / `_validate`) → execution (`apply_command` / `_exec_payload`) → state mutation
   → **the set of consumers that actually read that state back** (telemetry, effects, bus model,
   access, recovery, Red AI, objectives DSL, UI). Classify Live / Cosmetic / Dead.
2. **Probability inventory + back-compat surface + form-schema inventory** — every
   operator-settable `success_prob` / `base_pk` / outcome-dictating knob, the world-state inputs
   already available to derive them from, the vignettes/redai/playbook/test surface that
   references those params, and the exact parameter shape each verb reads (the source data for a
   declarative dynamic form).
3. **Mission-set realism research** — open-source operator-console references (USSF Delta /
   Space Operations Squadron fact sheets, commercial tasking APIs for ISR/SAR, GPS interface
   specs and Block IIIF docs, SBIRS/GOES ops, AWS Ground Station booking model, SWF Global
   Counterspace 2025, CSIS Space Threat Assessment 2025, SPARTA cyber TTPs, the four DA-ASAT
   test records) cross-checked against the in-repo verb catalog and per-domain databases.

---

## Headline findings

1. **The most important finding is invisible at first glance: defensive verbs only change
   telemetry, not effect outcomes.** `def.frequency_hop` sets `bus.comms.freq_hopping = True` —
   read by `telemetry.py:132` to *display* a smaller jam signature, but **not** read by
   `EffectResolver._effective_probability` or `effective_success_prob`, so the actual jam
   success roll is unchanged. The same is true for `satcom.mitigate_interference` /
   `satcom.shift_users` (`interference_mitigation`), and `def.maneuver_evade` (`evasion_active`).
   Only `def.harden` is wired (`effects.py:100` consumes `payload_state.hardened` in the safe-mode
   roll). Blue operators are training on defensive moves that don't actually defend.

2. **Raw operator-settable probabilities exist in 3 of the 4 effect actions** (`jam`, `engage`,
   `cyber` legacy fallback) and dictate the outcome before any physical input is considered. The
   `cyber` vector-driven path (`cyber.effective_success(vector, posture, dwell)`) is already
   fully derived from world state — that's the pattern to generalize.

3. **The catalog is in better shape than its piecemeal history suggests** (the realism research
   independently agreed): bus/TT&C, ISR tasking, SAR modes, SIGINT geolocation scaling, SDA
   tasking, SATCOM payload management, and cyber vector/payload framing all survive contact with
   open-source operations doctrine. The realism debts are concentrated in PNT (`pnt.set_integrity`
   is not a real operator action), three over-abstracted defensive verbs (`def.harden`,
   `def.disperse`, `def.escort_posture`), and the kinetic interceptor model (the operator-typed
   `interceptor_dv_ms` should become an interceptor-class enum).

4. **The single free-text JSON params textbox** (`#o-params` in `index.html:269-270`) is the
   primary UX bottleneck. Only `maneuver` and `jam` have assistant panels with typed fields and
   live preview; the other 5 actions and the ~50 catalog verbs all require operators to hand-edit
   JSON. The existing `#mnvr-panel`/`#jam-panel` pattern generalizes cleanly.

---

## CRITICAL findings (mislead operators or break PME training value)

### C1. Defensive verbs are telemetry-only — they don't actually defend

`def.frequency_hop` (`buscommands.py:175-178`) sets `bus.comms.freq_hopping = True`.
`satcom.mitigate_interference` and `satcom.shift_users` (`:122-128`) raise
`payload_state.interference_mitigation` to ≤0.8. `def.maneuver_evade` (`:241-247`) consumes Δv
and sets `payload_state.evasion_active = True`. **None of these are read by
`engine/effects.py:_effective_probability` (line 155) or by `engine/jam.py:effective_success_prob`
or `engine/engage.py:kill_probability`.** They only change the telemetry signature
(`telemetry.py:127-132` for the first two; `evasion_active` is unread anywhere).

**Impact.** A trainee shifts users to evade a jam, sees the jam signature drop in their telemetry,
and concludes they defeated the jam — but on the resolver's RNG roll, the jam succeeds at exactly
the same rate it would have without the defensive move. Same for frequency-hop vs jam, and
evasion-burn vs engage. This is the opposite of the lesson the exercise is meant to teach.

**Fix.** Extend `effects.py:_effective_probability` (and/or the per-domain `effective_success_*`
functions) to consume these defender-side flags as multiplicative modifiers, with magnitudes
sourced from the realism research (e.g., protected-waveform processing gain → ~0.3-0.5× jam
success; evasion-active during engage fly-out → max(0.05, 1 - target_dv_ms / (0.5 × divert_dv_ms))).
Severity: **CRITICAL** because this is a training-value bug, not a UI polish issue.

### C2. Operator-settable raw `success_prob` lets the trainee dictate the outcome

`orders.py:399` (jam), `:431` (engage), `:556` (cyber legacy fallback): the operator's
`params["success_prob"]` flows through to `EffectInstance.success_prob` and then to
`EffectResolver`'s single seeded RNG roll. The UI's `PARAM_TEMPLATE` (`app.js:70,72`) defaults
both jam and cyber to `success_prob: 1.0` — i.e., the default template is "I always succeed."
The Red AI (`redai.py:44,52-54`) uses the same `1.0` so Red doctrine "just works", and every
vignette tutorial step that hands a participant a model order (`00-training-basics.yaml:99,103`,
`01-leo-isr-denial.yaml:116`, `03-gnss-ew-campaign.yaml:52,76`, `05-da-asat-crisis.yaml:65`,
`06-satcom-cyber-link.yaml:61,85`, `08-multi-domain-taiwan.yaml:123,126`) hands them a `1.0`.

**Impact.** Effect resolution is not a function of physical inputs (modulation, power, geometry,
vector, dwell, target posture, defender hardening) but of whatever number the operator typed.
This invalidates the training value of the whole effect-resolution layer.

**Fix.** Remove `success_prob` from `params` schema for `jam` / `engage` / `cyber`; derive it
entirely from physical inputs (the cyber-with-vector path is the existing-good pattern). The
order form's "estimated Pₛ" display becomes computed/read-only. See **F3** for the foundational
decision question.

### C3. `observe.params.gain` and `observe.params.classification` let the operator dictate ISR
results

`orders.py:488` — `gain = float(p.get("gain", 1.0))` flows into `isr.effective_gain`, then into
the custody confidence boost. An operator typing `gain: 10` gains instant weapons-quality
custody. Similarly `observe.params.classification` (`:507`) lets the operator declare the
target's type ("hostile") without it being derived from the collection. These are not surfaced in
the UI but they are accepted by the order schema.

**Fix.** Drop both from the accepted schema; derive `gain` from beam_mode + look_angle (already
done by `isr.effective_gain`); make `classification` an outcome of `characterize` runs that
accumulate enough confidence, not an operator input.

### C4. `downlink.params.delivers` lets the operator flip arbitrary mission flags

`orders.py:521` — `delivers` defaults to `"imagery_delivered"` but the operator can type any
string. The execute handler sets `world.mission[delivers] = True` (per `_exec_downlink`), which
is the exact key the objectives DSL reads (`vignette.py:263 "deliver_before"`). An operator can
flip an objective by typing the right magic string.

**Fix.** Restrict `delivers` to a per-vignette allowlist derived from `vignette.objectives` or
the asset's payload type; default it from payload type when not specified.

---

## MAJOR findings (Dead/Cosmetic verbs, doctrine mismatches, UX cliff)

### M1. Verb classification table

Methodology: a verb is **Live** if any consumer outside of telemetry-only display branches on the
state it mutates. **Cosmetic** if the mutation is recorded (AAR `consequences`, telemetry signature,
detail dict echoed in UI) but nothing branches on it. **Dead** if there is no consumer at all
(including no UI display).

Consumers checked: `engine/telemetry.py`, `engine/effects.py`, `engine/bus.py` (`can_collect`,
`recompute_status`, `evolve`), `engine/busmodel.py`, `engine/access.py`, `engine/orders.py`,
`engine/recovery.py`, `engine/custody.py`, `engine/ssn.py`, `session/redai.py`, `session/scene.py`,
`content/vignette.py` `_evaluate_metric` (the objectives DSL — kinds: `deliver_before`,
`deny_delivery`, `custody`, `deny_custody`, `characterized`, `asset_destroyed`/`survived`/`safed`/
`operational`, `no_debris`/`debris_present`, `link_denied`, `proximity`, `evade`), and
`ui_web/static/app.js` (drill-down + fleet rail).

| Verb | Mutates | Consumer(s) found | Class | Fix |
|---|---|---|---|---|
| `eps.shed_load` | `power.shed_loads_w`, payload `collecting=False` | bus.py evolve (power margin), bus.py collect | **Live** | keep |
| `eps.restore_load` | `power.shed_loads_w` | bus.py evolve | **Live** | keep |
| `eps.set_charge_mode` | `power.charge_mode` | bus.py evolve | **Live** | keep |
| `eps.select_bus` | `power.charge_mode` | bus.py evolve | **Live** | keep (or fold) |
| `adcs.set_mode` | `attitude.mode`, pointing | bus.py / telemetry signature | **Live** | keep |
| `adcs.desaturate` | `attitude.mode`, pointing | bus.py | **Live** | keep |
| `adcs.point_payload` | `attitude.mode = slew` | bus.py | **Live** | keep |
| `cdh.dump_storage` | `cdh.storage_frac` | bus.py / telemetry storage gauge | **Live** | keep |
| `cdh.clear_fault` | `cdh.fsw_mode` | recovery.py chain | **Live** | keep |
| `cdh.reset_subsystem` | `cdh.fsw_mode`, attitude restore | recovery.py | **Live** | keep |
| `cdh.load_stored_program` | `cdh.fsw_mode = nominal` | recovery.py | **Live** | keep (rename `upload_command_load`?) |
| `comms.set_crypto` | _none_ (admitted no-op) | _none_ | **Dead** | cut, or make it the key-rollover step that re-arms a cyber `patched` vuln |
| `comms.enable_isl` | `comms.isl_enabled` | access.py `_best_isl_window` (would gate ISL delivery — needs verification) | **Live (likely)** | keep, verify ISL gating |
| `comms.config_link` | `comms.data_rate_kbps` | telemetry display | **Cosmetic** | wire into downlink throughput (caps `bitrate_cap_kbps`) |
| `comms.point_antenna` | `comms.antenna_mode` | _none_ | **Dead** | wire into telemetry link-margin signature OR cut |
| `tcs.set_mode` | `tcs.mode` | bus.py thermal | **Live** | keep |
| `tcs.set_heater` | thermal | bus.py thermal | **Live** | keep |
| `prop.cancel_burn` | `consequences.append({type: cancel_burn})` (no-op verb body) | AAR only | **Dead** (intent unfulfilled) | wire to `OrderSystem.cancel_order` for any queued `maneuver` order on `actor_id`; OR cut and surface cancel through existing order-queue UI |
| `prop.collision_avoid` | Δv consumed, `conjunctions` list shrunk | objectives `no_debris`/`evade` indirectly | **Live** | keep |
| `satcom.mitigate_interference` | `interference_mitigation += 0.4` (cap 0.8) | telemetry signature **only** | **Cosmetic** | wire into `effective_success_prob` as defender modifier (**C1**) |
| `satcom.shift_users` | same | telemetry signature **only** | **Cosmetic** | same (**C1**) |
| `satcom.report_interference` | `detail["last_interference_report"] = lvl` | _none_ | **Dead** | cut, OR fold as a one-shot White-Cell message to BLUE-OPS |
| `satcom.set_transponder` | `detail["transponder"]` | _none_ | **Dead** | wire as ground-segment cyber target option OR cut |
| `satcom.reconfigure_beam` | `detail["beam"]` | _none_ | **Dead** | same as above |
| `satcom.set_frequency_plan` | `detail["frequency_plan"]` and sub-params | _none_ | **Dead** | wire into jam coverage gain (a new frequency_plan reduces jam success for a window) |
| `isr.collect_now` / `schedule_collection` | `collecting=True` | bus.py storage growth → objectives via `deliver_before` | **Live** | keep |
| `isr.set_mode` | `payload.mode`, `collecting` | bus.py | **Live** | keep |
| `isr.prioritize_downlink` | `detail["downlink_priority"]` | _none_ | **Cosmetic** | wire into downlink priority resolution OR cut |
| `isr.assess_quality` | `detail["last_quality"]` based on storage | _none_ | **Dead** (and unrealistic — see realism §2) | **cut** |
| `isr.calibrate` | `detail["calibrated_at"]` | _none_ | **Dead** | cut, OR make it a low-frequency Δv/time-cost housekeeping verb |
| `sigint.task_collection` | `collecting=True`, `detail{band,mode,dwell}` | bus.py storage; detail unread | **Live (partial)** | wire `dwell_s`/`band` into the SIGINT geolocation_error_km computation already in `engine/sigint.py` |
| `sigint.set_band` | `detail["band"]` | _none_ | **Cosmetic** | fold into `sigint.task_collection` params, cut as standalone |
| `sigint.geolocate` | `detail["geolocate_mode"]` | _none_ | **Dead** | fold into `task_collection` (`intercept_mode=geolocate` already exists) |
| `sigint.downlink` | `detail["downlink_queued_at"]` | _none_ | **Cosmetic** | route through `downlink` action; cut as standalone |
| `sda.task_search` / `task_track` / `task_characterize` | `collecting=True`, `detail["sda_mode"]` | bus.py storage | **Live (partial)** | keep; detail keys could feed scene rendering |
| `sda.cue` | `detail["sda_cue"]` | _none_ | **Dead** | wire to actually trigger the cued observation (cross-asset task) OR cut |
| `sda.downlink` | `detail["downlink_queued_at"]` | _none_ | **Cosmetic** | route through `downlink`, cut as standalone |
| `wx.schedule_collection` | `collecting=True` | bus.py storage | **Live** | keep |
| `wx.downlink` | `detail["downlink_queued_at"]` | _none_ | **Cosmetic** | route through `downlink`, cut as standalone |
| `pnt.set_integrity` | `payload.integrity_mode` | echoed by `pnt.report_status` only | **Cosmetic** (and unrealistic — see realism §6) | **replace** with `pnt.flex_power` and `pnt.set_health_flag` (see realism §15) |
| `pnt.report_status` | `detail["last_status_report"]` | _none_ | **Cosmetic** | acceptable as a readout-only verb |
| `mw.set_sensor_mode` | `detail["mw_mode"]` | _none_ | **Cosmetic** | replace with `mw.add_stare_area(aoi, revisit)` (realism §7) |
| `mw.report_alerts` | reads `detail["mw_alerts"]` which nothing increments | _none_ | **Dead (broken loop)** | wire into a real `mw_alerts` source (MW payloads seeing a `boost` inject), OR cut |
| `def.patch_cyber` | `cyber_vulnerabilities[].patched=True` | `effects.py:163` (patched vuln → Pₛ=0) | **Live** | keep |
| `def.frequency_hop` | `bus.comms.freq_hopping=True` | telemetry signature **only** | **Cosmetic** | **wire into `effective_success_prob` as defender modifier (C1)** |
| `def.harden` | `payload_state.hardened=True` | `effects.py:100` safe_mode resistance | **Live** | keep, but consider gating to design-time per realism §11 |
| `def.set_threat_warning` | `Asset.threat_warning` | _none_ | **Dead** | wire into Red AI targeting weight (lower Pₐₜₜ for warned assets) OR cut |
| `def.maneuver_evade` | Δv consumed, `evasion_active=True` | Δv resource gate is Live; `evasion_active` **unread** | **Cosmetic** for the post-burn flag | **wire `evasion_active` into `engage.kill_probability` as a Pk-reducing modifier (C1)** |
| `def.escort_posture` | `threat_warning=True`, consequences log | AAR only | **Cosmetic** | acceptable as a doctrine readout |
| `def.disperse` | `threat_warning=True`, `detail["dispersal"]`, consequences log | AAR only | **Cosmetic** | demote to cell-level doctrine toggle (realism §11) OR cut |

**Summary count.** Live: 23. Cosmetic (recorded but unread): 13. Dead (no consumer at all): 13.
That's ≥40% of the catalog with no game-mechanic effect — confirming the user's intuition that
"some commands don't really do anything." See **F1** for the foundational decision question on
how aggressively to cut.

### M2. `engage` lacks an interceptor-class model — operator-typed `interceptor_dv_ms` IS Pk

`engine/engage.py:kill_probability(base_pk, miss_km, interceptor_dv_ms, salvo_n)` uses a 3-tier
capability switch on operator-typed Δv (`<50`/`<200`/`≥200` → 0.3/0.6/1.0×) and salvo combinatorics
on operator-typed `base_pk`. The four open-source DA-ASAT tests (SC-19, Burnt Frost, Mission
Shakti, Nudol) collapse to a much more interesting model where interceptor *class* determines
altitude reach, divert authority, and seeker, and **target maneuver** is the dominant defensive
modifier. See research report §14 for the proposed `INTERCEPTORS` database (4 classes:
`bmd_adapted`, `mrbm_kkv`, `abm_heavy`, `coorbital`) and modifier equations.

**Fix.** Replace the `interceptor_dv_ms` param with `interceptor_class` enum; derive Pk from class
base × track-quality × target-maneuver × altitude-reach. Also fix `engage.debris_cone_estimate`
to scale with target mass + altitude regime (Cosmos 1408 at 480 km left 1,789 tracked fragments
for decades; Burnt Frost at 247 km left 174 that decayed in months — that's the PME lesson).

### M3. `pnt.set_integrity` is fictional; flex power + health flags are the real verbs

`pnt.set_integrity {standard, protected, degraded}` doesn't correspond to a real GPS operator
action. The two well-documented PNT operator actions are:

- **Flex power** (IS-GPS-200E): the MCS commands SVs to reallocate transmit power between P(Y)
  and M-code, raising military signal power in jamming environments. Block IIIF adds Regional
  Military Protection (high-power M-code spot beams).
- **Set SV health flag / issue NANU**: the MCS sets an SV unhealthy and broadcasts the change to
  users via NANU advisories.

**Fix.** Replace `pnt.set_integrity` with `pnt.flex_power` (params: `on/off`, `signal: M-code|PY`,
optional `region`) and `pnt.set_health_flag` (params: `sv_id`, `healthy: bool`, `effective_time`).
Migration: `protected` ≈ flex_power, `degraded` ≈ set_health_flag(unhealthy). The realism §6
research has the full source list.

### M4. Order-form UX cliff

`#o-params` is a single free-text JSON `<input>` for every action. `PARAM_TEMPLATE` (`app.js:67-107`)
seeds it; `previewOrder()` debounces a `/order/validate` dry-run on every `oninput`. Only `maneuver`
and `jam` have dedicated assistant panels with typed fields and `/compute` preview.

**Form-schema redesign data is in §"Form schema for redesign" below** — every verb's exact
parameter shape, grouped by SHAPE-class so the implementation collapses to ~6 dynamic templates
(via-only, via+enum, via+bool, via+number, via+target picker, complex) plus the existing
maneuver/jam assistants and four new assistants (engage, cyber, observe, sigint).

The server-side `/compute` endpoints **already exist** for engage, cyber, sigint (`server.py:303,
309, 315` — found by the inventory agent). They are just unused by the front end. The redesign is
client-side only for those four.

### M5. Documentation drift around `success_prob`

Removing or hiding `success_prob` requires updating:
- 10 vignette YAML tutorial steps (`00-training-basics.yaml:99,103`; `01-leo-isr-denial.yaml:116`;
  `03-gnss-ew-campaign.yaml:52,76`; `05-da-asat-crisis.yaml:65`; `06-satcom-cyber-link.yaml:61,85`;
  `08-multi-domain-taiwan.yaml:123,126`)
- 6 lines of `docs/training/11-vignette-playbooks.md` (46, 81, 118, 136, 176, 177)
- 2 hardcoded literals in `session/redai.py` (44, 52-54)
- 13 direct test sites + ~6 indirectly dependent tests (full list in the probability inventory)

**Save/AAR compat constraint (do not break):** `EffectInstance` keeps `success_prob`,
`sm_susceptibility`, `persistence_bonus`, etc. as fields with identical resolution semantics,
**because event-log payloads bake the dump'd EffectInstance into the snapshot stream** at plan
time. The change is to stop reading `success_prob` from `Order.params`; new orders derive the
value internally and the serialized `EffectInstance` looks the same in the log. Old saves replay
byte-identically because the resolver reads what's already in the dumped payload.

---

## MINOR findings (polish, realism layer-2)

- **N1.** `effects.py:50` — `EffectInstance.success_prob: float = 0.9` default should become a
  required field once derivation is mandatory (no implicit "0.9 if unspecified" path).
- **N2.** `app.js:70` template seeds `success_prob: 1.0`; `app.js:779` jam-assistant default is
  `0.9`. Drop both once params are derived.
- **N3.** `mw.set_sensor_mode` accepts free string `mode` (no enum) — `buscommands.py:414`. Pin
  to `{scan, step_stare, alert}`.
- **N4.** `sigint.set_band` accepts free string `band` — `buscommands.py:307`. Pin to
  `sigint.BANDS` enum (UHF·L·S·X·Ku·Ka·W).
- **N5.** `tcs.set_mode` default is `"operational"` (`buscommands.py:152`) but `_THERMAL_MODES`
  first entry is `"nominal"` — the default doesn't match the canonical default.
- **N6.** `app.js` has 23 implemented catalog verbs that never appear in `actionsFor()` or
  `PARAM_TEMPLATE` and thus are engine-only (operators can't issue them from the UI). Either add
  them or document them as White-Cell / scripted-only.
- **N7.** Jam attribution label `deceptive: attribution_bias="overt"` reads backwards at first
  glance — deceptive jamming is *hard to detect* but *unambiguous once detected*. Document or
  rename.
- **N8.** ~~Missing realistic verbs identified by research §15~~ — **closed.** All eight now
  implemented in `buscommands.py`: `pnt.flex_power`, `pnt.set_health_flag`, `mw.add_stare_area`,
  `satcom.geolocate_interference`, `wx.request_sector`, `prop.station_keep`, `isr.shutter_sensor`,
  and cyber payload `seize_c2` (the last is a `cyber.PAYLOADS` entry consumed by the `cyber` order
  action, not a bus/payload verb). Test coverage: `spacesim/tests/test_bus_commands.py`.
- **N9.** ~~Missing realistic order-action parameter~~ — **closed.** `jam.params.link_target ∈
  {uplink, downlink, crosslink}` (default `downlink`, back-compat) now scopes `EffectInstance` /
  `ActiveEffect`; `is_link_denied(world, target, t, link=...)` takes an optional `link` filter so
  the `downlink` action only checks the `downlink`-scoped jam — an uplink-only jam (CCS Block
  10.2-style) no longer phantom-denies mission-data delivery. Test coverage:
  `spacesim/tests/test_orders.py::test_jam_link_target_*`.
- **N10.** Style consistency: any new form controls (`<select>`, `<input type=number>`,
  `<input type=checkbox>`) must inherit the focus-ring / contrast fixes applied in the prior
  audit (`style.css` D-class fixes); the existing maneuver/jam panels already comply.

---

## Form schema for redesign

The realism research + probability inventory together yield a complete declarative schema. Verbs
group into 6 parameter SHAPE-classes plus 6 assistant-panel actions:

### Assistant-panel actions (already exist or need building)

| Action | Existing | New schema |
|---|---|---|
| `maneuver` | `#mnvr-panel` (6 modes) | keep |
| `jam` | `#jam-panel` (mod + power + bw) | **add** `link_target ∈ {uplink, downlink, crosslink}`; **drop** `success_prob` input; show computed Pₛ as read-only |
| `engage` | none | **new panel**: `interceptor_class` enum (4 classes from §M2); read-only computed Pₖ from class × track-quality × target-maneuver × altitude-reach; `salvo_n` input |
| `cyber` | none | **new panel**: `vector` enum (4), `payload` enum (4 + `seize_c2`), `dwell_s` slider; computed Pₛ from `cyber.effective_success` read-only; drop the legacy `success_prob` path |
| `observe` | none | **new panel**: `intent` enum, `beam_mode` enum (from `isr.BEAM_MODES[payload_type]`), `look_angle_deg` 0-45 slider, `duration_s` numeric; drop `gain`/`classification` operator params |
| `sigint` (verb form) | none | **new panel**: `band` enum (`sigint.BANDS`), `intercept_mode` enum (`sigint.MODES`), `dwell_s`, AOI; computed geolocation_error_km read-only |

### Catalog verbs — 6 shape classes

| Shape | Verbs | Form template |
|---|---|---|
| via-only (no extras) | `eps.shed_load`, `eps.restore_load`, `cdh.dump_storage`, `cdh.clear_fault`, `cdh.reset_subsystem`, `cdh.load_stored_program`, `adcs.desaturate`, `isr.collect_now`, `wx.schedule_collection`, `wx.downlink`, `def.escort_posture`, `prop.cancel_burn` | one `<select id="via">` from pass-window list |
| via + enum `mode` | `eps.set_charge_mode` (CHARGE_MODES), `adcs.set_mode` (ATTITUDE_MODES), `tcs.set_mode` (THERMAL_MODES), `comms.point_antenna` (ANTENNA_MODES), `isr.set_mode` (ISR_MODES), `pnt.set_integrity → flex_power` | via + `<select>` |
| via + bool `on` | `tcs.set_heater`, `comms.enable_isl`, `def.frequency_hop`, `def.harden`, `def.set_threat_warning` | via + `<input type=checkbox>` |
| via + numeric | `comms.config_link` (`data_rate_kbps` 64-16384 step 64), `def.maneuver_evade` (`dv_cost` ≥1 m/s), `prop.collision_avoid` (`dv_cost` ≥1 m/s) | via + range/number |
| via + target picker | `adcs.point_payload`, `sda.task_track`, `sda.task_characterize` | via + `<datalist>` of own assets/tracks |
| complex multi-field | `sigint.task_collection`, `satcom.set_frequency_plan`, `def.patch_cyber` (with optional `vector`) | small assistant panel each |

The realism-research-recommended new verbs (`pnt.flex_power`, `pnt.set_health_flag`,
`mw.add_stare_area`, `satcom.geolocate_interference`, `wx.request_sector`, `prop.station_keep`,
`isr.shutter_sensor`) all fit the existing shape classes — no new template needed.

---

## Foundational decisions (recorded)

User answered all five via `AskUserQuestion`, all landing on the deep-redesign option:

- **F1 — Verb cleanup.** *Rewire where research named a fix; cut the rest.* Phase A wires the
  defender-side modifiers into the resolver; Phase D cuts Dead verbs with no plausible consumer.
- **F2 — `success_prob`.** *Remove the field entirely; derive from physical params.* Migration
  list (19 references) is enumerable; the EffectInstance baked-payload contract is preserved so
  save/AAR replay stays byte-identical.
- **F3 — Engage model.** *Adopt the full 4-class `INTERCEPTORS` database.* Replaces
  `interceptor_dv_ms` with an `interceptor_class` enum; debris persistence by altitude is
  included.
- **F4 — PNT verbs.** *Replace `pnt.set_integrity` with `pnt.flex_power` +
  `pnt.set_health_flag`.* Mechanical vignette migration: `protected` ≈ flex_power,
  `degraded` ≈ unhealthy flag.
- **F5 — Form redesign.** *Progressive: assistants first, then shape templates.* New
  engage / cyber / observe / sigint assistant panels first; declarative shape-class templates
  for the 6 catalog-verb groups second; JSON escape hatch retained collapsed throughout.

---

## Phased implementation plan (post-decisions)

**Phase A — Verb consumer rewiring (C1, M1 Cosmetic→Live conversions).** Most impactful, smallest
diff: `effects.py:_effective_probability` learns to multiply by defender-side modifiers
(frequency_hop, interference_mitigation, evasion_active) sourced from `engine/jam.py` and
`engine/engage.py`. ~30 lines of engine + a property test that monotonicity holds (hop ON ⇒
strictly lower jam Pₛ; evasion ON ⇒ strictly lower kill Pₖ). Determinism stays green because the
RNG roll itself is unchanged — only its threshold is.

**Phase B — Probability derivation closeout (C2, M2, M3).** Drop `success_prob` reads from
`orders.py` for jam/engage/cyber; new `INTERCEPTORS` database in `engage.py`; new PNT verbs in
`buscommands.py`; sync `redai.py` literals + vignette tutorials + playbook docs.

**Phase C — Order-form UX (M4, N7-N10).** Build the 4 new assistant panels and the dynamic
shape-class templates. Existing maneuver/jam panels stay as-is. JSON escape hatch retained
collapsed by default for power users.

**Phase D — Dead/Cosmetic cleanup per F1 decision.** ✓ implemented (F1 = rewire + cut).

  Cuts (14 verbs deleted from `buscommands.py` + their unit tests):
  `comms.point_antenna`, `comms.set_crypto`, `isr.assess_quality`, `isr.calibrate`,
  `sigint.set_band`, `sigint.geolocate`, `sigint.downlink`, `sda.cue`, `sda.downlink`,
  `wx.downlink`, `mw.set_sensor_mode`, `mw.report_alerts`, `satcom.report_interference`,
  `satcom.set_transponder`.

  Adds (3 realism verbs from research §15):
  - `satcom.geolocate_interference` — MAJE-style detect → identify → geolocate of an
    in-band interferer; CEP scales with dwell. Logs a `consequences` event for AAR.
  - `wx.request_sector` — GOES-R mesoscale domain sector request (AOI center + cadence).
  - `mw.add_stare_area` — SBIRS step-stare AOI tasking (center + revisit rate).

  Rewires (Cosmetic → Live, completed in Phase A):
  - `def.frequency_hop`, `satcom.mitigate_interference`/`shift_users`,
    `def.maneuver_evade` — all now multiplied into `_effective_probability`.

  Kept as posture/readout (acceptable Cosmetic):
  - `def.set_threat_warning`, `def.disperse`, `def.escort_posture`, `pnt.report_status`,
    `prop.cancel_burn`, `pnt.set_integrity` (back-compat shim).

**Phase E — Tests (test-first as per `docs/AUDIT-2026-06.md` precedent).**
- Property tests for each defender modifier (monotonicity in [0,1]).
- New `INTERCEPTORS` table tests (Pk bounds; altitude-reach hard cap; target-maneuver knockdown).
- Round-trip tests for every form-schema action through `dry_run()` / `issue()` matching.
- `test_determinism.py` stays green; new `EffectInstance` payloads in saved logs replay
  byte-identically.
- New regression test `test_defensive_modifiers_actually_defend.py` that fixes the C1 trainee
  bug forever.

**Phase F — Manual UI verification per CLAUDE.md "UI changes" rule.**
`python3 -m spacesim.ui_web`; exercise one verb per mission set across Blue and Red; verify
dry-run preview and issue both work and the form's computed-Pₛ display matches the engine's roll
basis. Screenshot a before/after of the order panel.

---

## Sources

- In-repo: `docs/AUDIT-2026-06.md` (prior audit, June 2026), `docs/research/05`, `06`,
  `docs/build-spec/07-operator-console.md`, `docs/build-spec/08-ssn.md`, `docs/FUTURE-WORK.md`.
- External (full citation list in agent reports `/tmp/.../afb2ef58…` and `/tmp/.../a554837…`):
  Maxar/Planet/Capella tasking APIs; AWS Ground Station booking docs; 53/2/18/19 SOPS fact
  sheets; IS-GPS-200E flex power; GPS Block IIIF RMP; SBIRS scanner+starer; GOES-R MDS request;
  AEHF/Milstar anti-jam; Viasat/SPARTA cyber framing; SWF 2025 Global Counterspace; CSIS 2025
  Space Threat Assessment; Operation Burnt Frost, SC-19 / FY-1C, Mission Shakti, Nudol 2021
  open-source records (planet4589, IISS, CRS RS22652).
