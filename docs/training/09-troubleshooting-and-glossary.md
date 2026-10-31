[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 10. Troubleshooting

> **Looking for an exact message?** Every refusal the console and server can show, with its cause and fix,
> is tabulated in [`09a-refusal-messages.md`](09a-refusal-messages.md). This page covers set-up and
> general problems.

- **`uvicorn: command not found`** — run `pip install uvicorn`, or start with
  `python3 -m uvicorn spacesim.ui_web.server:app`.
- **`ModuleNotFoundError: spacesim`** — run from the repository root (the folder containing
  `spacesim/`), or `pip install -e .`.
- **An order is rejected** — read the `reason`: `no_window` (no pass within the planning
  horizon), `sensor_contended` (the sensor can see the target, but every window within the
  planning horizon is already booked; cancel a queued task or try later), `requires_cue` (that
  sensor needs a track on the target first), `invalid_param` (one of the order's params has the
  wrong type or is not a finite number, for any action: for example `power_w: "inf"` on a jam,
  `salvo_n: "three"`, a `dv` that is not exactly three numbers, a non-text `via`, or a list as an
  observe beam mode. Numbers written as text, such as `"200"` or `"3"`, are accepted. Fix the
  field in the order's params, and note that a field set to `null` counts as left out),
  `roe_kinetic_not_authorized` (enable it via the `red_kinetic_authorized` dial, or ask White: the
  rules can change during play), `no_command_station` (add a `via` station or a `stored_at` time),
  `role_scope_not_assigned` / `role_scope_out_of_scope` (see the **Operator seat** entry below),
  `no_weapons_quality_track` (task a sensor first), `no_ammo` (the effector has no rounds left),
  `insufficient_ammo` (the salvo, `salvo_n`, asks for more rounds than the effector has left;
  reduce the salvo), `insufficient_delta_v`, `not_owner`.
- **A queued engagement did nothing at its window** — an earlier engagement by the same
  effector used the rounds first, and what was left no longer covered this salvo. The strike is
  not rolled, spends nothing, and leaves the target untouched. The ground-truth effect log
  records it as `failed` with reason `insufficient_ammo`.
- **The Cell & Time panel says `Load failed:`** — the vignette has errors and no session was made. The list
  under the message names every problem as *section*`[`*entry*`]`.*field* and a reason. Fix each
  one in the YAML and press **Load** again. An open session is not touched by a refused load.
  What the check looks for is listed in
  [`06-the-vignette-library.md`](06-the-vignette-library.md#when-a-vignette-wont-load). If the
  message says the vignette was **not found**, the id is wrong or the file is not in a vignette
  folder.
- **Your vignette is missing from the picker** — the file is not valid YAML, or it has no
  `vignette:` block with an `id`. The picker leaves such files out instead of listing them. Check
  the YAML syntax (indentation, an unclosed `[` or quote) first.
- **My order shows `pending_approval`** — an approval gate holds it until White (or another named role) decides. Tell White the order id; you cannot cancel it meanwhile.
- **A command shows `executed` but the satellite did not change** — its delivery path may have been jammed when it ran, or a re-check failed. Check the manoeuvre ledger and telemetry; see [BLU-17](13a-blue-cell-rules-and-delivery.md).
- **Add-satellite says `cannot edit force after start`** — assets can only be added between Load and Start.
- **Nothing happens after issuing an order** — orders execute at their scheduled **window**;
  advance time (`+10m`) until the clock reaches it.
- **A satellite shows `safe_mode`/red** — it was safed (attack or bus fault); run the recovery
  procedure and remove the root cause.
- **Tests fail to collect** — install the dev extras: `pip install pytest hypothesis skyfield httpx`.

> **Sources:** `spacesim/engine/orders.py` (`_validate`, `_order_params_ok`, `ORDER_PARAM_RULES`,
> `_observe_params_ok`, `_plan_collection`, `_plan_command`, `OrderSystem` `horizon_s`,
> `_engage_rounds`, the execute-time rounds re-check in `_h_effect`) ·
> `spacesim/ui_web/static/app.js` (`REASON_TIPS`, `loadSession`) ·
> `spacesim/content/vignette.py` (`validate_vignette`, `VignetteValidationError`,
> `list_vignettes`) · `spacesim/ui_web/server.py` (`_vignette_load_errors`) · FR-1460 · FR-3110 ·
> FR-3210 · FR-5310

---

## 11. Glossary

- **Access window** — the interval when geometry permits an action on one of the six channels
  (command uplink, telemetry downlink, sensor observation, jam footprint, weapon engagement, RPO
  proximity).
- **Custody / track** — a cell's belief about an object; confidence **decays** between looks.
- **Weapons-quality track** — a track confident and characterized enough to authorize an engagement.
- **Fog-of-war** — a cell sees only its own assets plus what its sensors have detected.
- **Safe mode** — a protective state with the payload off; reversible but costs recovery passes.
- **The five D's** — every offensive effect resolves to *deceive / disrupt / deny / degrade /
  destroy*; the first three are reversible and low-debris, destroy is kinetic and permanent.
- **Cyber exception** — cyber is the one effect not gated by orbital passes.
- **ISL** — inter-satellite (crosslink) relay path for commands.
- **AAR** — After-Action Review: deterministic read-only replay, scrubbing, and branch comparison.
- **Console seat vs operator seat** — the *console seat* is the White / Blue / Red / Observer button (which
  screen you see); an *operator seat* is a name White binds to one asset and one role so a crew can split
  bus and payload work. Neither is a login.
- **Role binding / staffing report** — White's assignment of an operator seat to an asset and a role (Bus,
  Payload, Both); the staffing report lists mandatory bindings still missing and blocks **Start**.
- **Approval gate / `pending_approval`** — a vignette rule that holds matching orders until a named role
  approves or denies; nothing is scheduled while an order waits.
- **ROE flag** — a per-cell switch (`kinetic_authorized`, `cyber_authorized`) that White can change during play.
- **Delivery path** — how a command reaches a satellite: `ground_uplink`, `isl_relay` (crosslink via a
  peer) or `stored_program` (runs onboard at a set time). A jam on a link stops only the paths that use it.
- **Link-scoped jam** — a jam that attacks the uplink, downlink or crosslink (`link_target`); the default is downlink.
- **Manoeuvre ledger** — per-satellite record of executed burns: time, Δv cost, purpose tag, Δv left.
- **Draft session / Creator** — an unstarted scratch session White uses to build a new vignette; it cannot run.
- **Exercise span** — from the start time to start + 366 days; time controls and saves must stay inside it.
- **Event log** — the ordered record of everything that happened; replaying it rebuilds the exercise, which is
  why rewind, undo and saves are exact. A save may hold at most 100,000 entries.
- **Inject handle / pending inject** — `white-1`, `white-2`... name scheduled White injects that have not fired; you can Edit or Cancel them.
- **Condition inject** — an inject that fires when a stated condition becomes true, checked every 5 simulated minutes.
- **Save as scenario** — writes the current state as a new vignette that starts now; not the same as Save session.
- **SOH (state of health)** — the set of readings that say whether a satellite is well: power, attitude, thermal, comms, storage, each green / yellow / red against its limits.
- **TLE (two-line element set)** — two 69-character lines of text describing a real satellite's orbit; paste it to add that satellite (before Start). **OMM** is the newer CCSDS file form of the same idea.
- **RIC (radial / in-track / cross-track)** — a frame centred on one satellite: R points away from Earth, I along its direction of travel, C sideways. The RIC view shows where another object is *relative to* your chosen origin. **LVLH** is the same idea used by the manoeuvre assistant.
- **CATS (Sun–target–sensor phase) angle** — the angle at the target between the Sun and the sensor; passive optical sensors work only inside a usable range of it.
- **SSN (Space Surveillance Network)** — the simulated network of ground sensors a cell can ask for tracking data; a request is `accepted` or fails with a reason such as `no_network`.
- **TDOA / FDOA** — time / frequency difference of arrival: how several receivers locate a radio emitter; used by the SIGINT geolocation vignette.
- **Seed** — the number that fixes the exercise's chance events (a jam's success, a cyber attempt). Same seed and same orders give the same result; change it for a different outcome.
- **Hot-seat** — several cells sharing one browser by switching seats (with **⏸ Handover** to hide the screen), as opposed to each player on their own tab or machine.
- **A2/AD (anti-access / area denial)** — a defender's layered weapons and sensors meant to keep an opponent out of, or hamper them inside, an area; the setting of the China COA vignettes.
- **Gantt (activity timeline)** — the bar-per-activity chart of past, present and scheduled orders and effects.
- **ISR** — intelligence, surveillance and reconnaissance: imaging or sensing satellites such as `ISR-EO-1`. Matters in the LEO ISR Denial vignette (`11.1`).
- **EO / SAR** — electro-optical (a camera: needs daylight) and synthetic-aperture radar (sees through cloud and night) imaging payloads; see the SAR trial `mt-isr-sar` (`11.9`).
- **SDA** — space domain awareness: knowing what is where in orbit. In the tool it is the sensor-tasking → custody loop (BLU-4 / RED-4).
- **SATCOM** — satellite communications payloads, the usual jamming and cyber target (`satcom-cyber-link`, `11.6`).
- **PNT / GNSS** — positioning, navigation and timing; GNSS is the satellite navigation family (GPS and similar) that provides it. Matters in `gnss-ew-campaign` (`11.3`).
- **EW** — electronic warfare: jamming and spoofing of radio links; one of the five D's effects (RED-5).
- **TT&C** — telemetry, tracking and command: the radio link a ground station uses to read a satellite's health and send it commands.
- **FSW** — flight software, the satellite's onboard computer program; the `cdh.fsw_error_count` log line counts its errors.
- **SoC (state of charge)** — how full a satellite's battery is, shown as a percentage in the fleet rail.
- **LEO / MEO / GEO / HEO** — orbit regimes: low Earth (hundreds of km, passes last minutes), medium Earth (navigation satellites), geostationary (about 36,000 km, appears fixed), highly elliptical.
- **ASAT / DA-ASAT** — anti-satellite weapon / direct-ascent ASAT, a ground-launched kinetic interceptor (`da-asat-crisis`, `11.5`).
- **SGP4** — the standard model that turns a TLE into a position; the tool uses it for TLE-sourced satellites.
- **ML / MD** — tags in the Red COA vignette names, normally read as "most likely" and "most dangerous" courses of action; the vignette files do not spell them out.
- **Planning horizon** — how far ahead the engine searches for a window when you plan an order or
  task a sensor: the next 24 hours of sim time. No window inside it gives `no_window`. The console's
  rejection tips use this term.

> **Sources:** `spacesim/session/manager.py` (`role_scope_check`, `staffing_report`, `maneuver_ledger`) ·
> `spacesim/engine/orders.py` (`decide_gated_order`, `_delivery_jammed`) · `spacesim/engine/access.py` (the six channels) · `spacesim/engine/custody.py`
> (`Track`, weapons-quality gate) · `spacesim/session/cells.py` (`CellController`, fog-of-war) ·
> `spacesim/engine/bus.py` (safe mode) · `spacesim/engine/effects.py` (five D's) ·
> `spacesim/engine/orders.py` (cyber exception, ISL delivery, `OrderSystem` `horizon_s`) ·
> `spacesim/session/aar.py` · `spacesim/ui_web/static/app.js` (`REASON_TIPS`)
