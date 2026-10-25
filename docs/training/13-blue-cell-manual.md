[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Traceability matrix](15-manual-traceability.md)

## 13. Blue cell manual

The role-scoped manual for a **Blue cell operator** — the defender/friendly-force commander who
protects and exploits Blue's space and ground assets under fog-of-war. Every section carries a
stable ID (`BLU-n`) cross-referenced both directions in
[`15-manual-traceability.md`](15-manual-traceability.md). Blue and Red share almost all
mechanics — this manual frames them from Blue's defensive posture; the Red manual
([`14-red-cell-manual.md`](14-red-cell-manual.md)) frames the same mechanics offensively, and
both defer to the shared concept modules rather than duplicating them.

**More sections** (BLU-15 to BLU-18) are in [13a](13a-blue-cell-rules-and-delivery.md): the Operator seat field, orders waiting for approval and live ROE changes, which link a jam attacks and what stops a command, and the manoeuvre ledger.


### BLU-1 · Your view: fog-of-war

You see **only Blue's own assets** at true position, plus whatever Blue's sensors have detected —
other-side objects appear only as **tracks** with an uncertainty volume that grows between looks.
You never see Red's ground truth; the filter is enforced server-side at the
`SessionAPI`/`CellController` boundary, not in the browser. Read your **Mission brief** (auto-opens
on load; reopen from View ▾ → Mission brief) for situation, mission, friendly forces, threat
picture, ROE, deadline, and success criteria before acting.

> **Sources:** `spacesim/session/cells.py` (`CellController`, fog filter) · `spacesim/session/scene.py` ·
> `GET /api/sessions/{sid}/brief/blue` · [`02-interface.md`](02-interface.md) §"A player cell"

### BLU-2 · Plan-first commanding

You never act instantly on perfect knowledge — you **plan** a command and the engine schedules it
to the earliest valid window. A command reaches a satellite three ways and the tool picks the
soonest: **ground-station uplink**, **inter-satellite link (ISL) relay** via a crosslink-capable
peer, or a **stored program** run onboard. Every issued order lands in the **command queue** with
its window and delivery path, and stays **cancellable until it uplinks**. Up to four commands
ride one pass.

> **Sources:** `spacesim/engine/orders.py` (`OrderSystem`, delivery paths) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Plan-first commanding"

### BLU-3 · Previews before you commit

Three assistants show what an order will do before you fire it:

1. **Dry-run validity** — the green ✓ / red ✗ line ("will queue · ground_uplink · window
   14:32:10"); a blocked action tells you *why* it's blocked (pre-disabled Issue button). If
   you edit the command menu's raw JSON params by hand, a field with the wrong type or a
   non-number (`"inf"`, words where a number belongs, a `dv` without exactly three numbers) shows
   ✗ `invalid_param`. A number written as text, such as `"200"`, is accepted, and a field set to
   `null` counts as left out.
   [`09` §10](09-troubleshooting-and-glossary.md#10-troubleshooting) lists every reason.
2. **Consequence preview** — severity, escalation weight, reversibility, debris risk, attribution;
   civilian-target denial bumps severity a tier.
3. **Verb assistants** — `maneuver` (six entry modes, live Δv + new elements), `observe` (beam
   mode + look-angle + expected swath/resolution/power), `jam` (modulation/power/bandwidth with an
   on-map denial footprint).

*See also: [RED-3](14-red-cell-manual.md#red-3--previews-before-you-commit) — the same preview
mechanics from Red's side.*

> **Sources:** `spacesim/engine/orders.py` `dry_run()`, `_order_params_ok`/`ORDER_PARAM_RULES` ·
> `POST /preview/consequence` · `spacesim/engine/{maneuver,isr,jam}.py` ·
> [`02-interface.md`](02-interface.md) §"Order-composition assistants"

### BLU-4 · SDA: task sensors, build custody, unlock actions

You don't get the sky for free. **Task scarce sensors** to detect, track, and characterize
objects; a good report raises a track's confidence and shrinks its uncertainty. Once a track is
**weapons-quality** (characterized + confident) it **unlocks** actions that were blocked.
Sensors do one thing at a time — task two collections at once and the second slips to a later pass
(contention). Custody **decays** between looks; the belief map blooms the uncertainty volume until
you re-task. This tasking→custody→unlock loop is Blue's core defensive discipline: know the sky
before you commit.

Some vignettes give a sensor limits of its own. A **cue-dependent** sensor refuses a target you
hold no track on, and the preview shows reason `requires_cue`: get a first look with another
sensor. Leave the sensor on **auto** and the engine skips cue-dependent sensors for an untracked
target. A sensor **hosted** on one of your satellites can be tasked by the sensor's name or by the
satellite's name. Other limits remove windows or reduce gain: a Sun exclusion angle, a minimum
range, an orbit-regime specialty, a usable phase-angle range, or a radar's `fence`/`dish` beam
mode ([`06`](06-the-vignette-library.md#authoring-sensors-optional-modality-fields) lists them).
When you task a radar, leave the **Mode** dropdown on `auto`: any other entry replaces the radar's
own mode. The preview is the quickest check that a sensor can see the target at all. `no_window`
means it can't within the planning horizon (the next 24 hours). `sensor_contended` means it can,
but every window is already booked.

*See also: [RED-4](14-red-cell-manual.md#red-4--build-a-targeting-picture-with-sda) — the same
tasking→custody→unlock loop, applied to targeting rather than defense.*

> **Sources:** `spacesim/engine/custody.py` (`Track`, weapons-quality gate) ·
> `spacesim/engine/access.py` (`sensor_observation`, `_observation_predicate`) ·
> `spacesim/engine/orders.py` (`_validate` `requires_cue`, `_candidate_sensors`,
> `_plan_collection`, `_resolve_sensor_id`, observe mode in `_exec_payload`) ·
> `spacesim/ui_web/static/index.html` (`#task-beam-mode`) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"SDA sensor tasking"

### BLU-5 · Keep your buses healthy

Every Blue satellite has a live **bus** (power/eclipse, attitude, thermal, propulsion, storage,
comms), each limit-checked green/yellow/red. The bus **gates the payload** — no power or a
safe-mode event means no mission. The fleet rail rolls each asset up to one worst-subsystem dot
(red if safed) beside an alarms/event feed. Watch it: as the defender you find out you've been hit
at the next telemetry contact, not the moment it happens.

> **Sources:** `spacesim/engine/bus.py` (`BusState`/`PayloadState`) · `spacesim/engine/busmodel.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Bus state-of-health"

### BLU-6 · Diagnose an attack from telemetry

The tool **never tells you "you are being jammed"** — it shows physics; you infer the cause. Click
a fleet row for the subsystem drill-down (parameter list vs. limits, per-parameter history graph
with a clean "compare to nominal" ghost, symptom log). The graph covers the last hour of sim time (or
since exercise start, if sooner; 120 points), and **each point is the asset's state at that instant** — an attack or anomaly
appears on the graph starting at its own onset, never smeared back over earlier points. So the
point where the line breaks is a trustworthy answer to "when did this start," and it gives
the same value as your telemetry CSV export (BLU-14) at any instant both of them sample. Read the signature:

| If you see… | Likely cause | Blue response |
|---|---|---|
| `comms.rx_power_dbm` HIGH, `cn0_dbhz` collapses, `ber` spikes | EW jamming | re-plan frequency/beam; geolocate the jammer |
| `cdh.fsw_error_count` / `cmd_reject_count` climbing, FSW→safe | Cyber / command-path intrusion | patch the vulnerability; reset FSW |
| `payload.snr_db` drops, `thermal.optics_temp_c` rises on a pass | Directed-energy / dazzle | re-task off the threat geometry |
| A hostile **track closing** on the view | RPO / co-orbital | maneuver-to-evade; task SDA to characterize |
| `battery_soc` + `bus_voltage_v` sag | eclipse / power fault | shed loads; check the power timeline |
| All telemetry **ceases** | kinetic kill (irreversible) | — |

> **Sources:** `spacesim/engine/telemetry.py` (signatures + nominal baseline) ·
> `spacesim/session/manager.py` (`get_series`) · `spacesim/session/aar.py` (`worlds_at_times`,
> per-instant replay) · `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/{param}` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Diagnosing attacks from telemetry"

### BLU-7 · Recover a safed satellite

Recovery is a **multi-pass procedure**, not a button. If the root cause persists (e.g. an
unpatched modem vulnerability) the satellite is **re-safed** — you must remove the cause (patch the
vulnerability with `def.patch_cyber`, or get the jammer killed) before recovery sticks. Drive it
from the recovery strip; the bus commands (EPS shed/restore, ADCS mode, storage dump) are issued
like any other command via the command action.

> **Sources:** `spacesim/engine/recovery.py` · `spacesim/engine/buscommands.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Safe-mode recovery"

### BLU-8 · Defensive maneuver and conjunctions

The **Conjunctions** sidebar lists upcoming close approaches (range / time-to-CA); each row's
**Evade** button fires `prop.collision_avoid` on your own asset, consuming a small Δv budget and
queuing to the next command-uplink window. For a closing hostile track, the maneuver assistant's
six entry modes let you plan a deliberate evade with live Δv cost.

> **Sources:** `world.conjunctions` · `prop.collision_avoid` verb · `spacesim/engine/maneuver.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Conjunctions & collision avoidance"

### BLU-9 · Cyber cuts both ways

Cyber effects are **not** gated by orbital passes — off-pass, subject to the defender's posture and
whether the vulnerability is patched. As Blue this is the threat you can't see coming on the pass
timeline *and* your fastest patch lever: harden posture and patch known vulnerabilities before Red
exploits them.

*See also: [RED-6](14-red-cell-manual.md#red-6--cyber-the-off-pass-wildcard) — the same mechanic
from the attacker's side.*

> **Sources:** `spacesim/engine/cyber.py` · [`05-core-concepts.md`](05-core-concepts.md) §"Cyber — the off-pass exception"

### BLU-10 · Win the vignette

Your objectives and their gates (window / weapons-quality / ROE) are laid out move-by-move in the
per-cell playbook. Read your row there, then work the tasking→custody→command loop against the
deadline in your Mission brief.

> **Sources:** [`11-vignette-playbooks.md`](11-vignette-playbooks.md) ·
> `spacesim/tests/test_vignette_tutorials.py` · `GET /api/vignettes/{id}/tutorial`

### BLU-11 · RIC frame view & CATS phase angle

**View ▾ → Proximity → ⊕ RIC frame view** opens a live, relative-motion plot: pick an **Origin**
and, optionally, a **Chase** and a **Target**. Unlike the god-view (WCM-13), your picker only
offers objects you **own or hold a Track on** — the same fog-of-war rule as every other
cell-scoped view. Selecting anything else is rejected outright (a clear error, never a silent
fallback to a different object or to ground truth). The plot (in-track vs. radial, origin at
centre) and the R/I/C-km table re-render continuously as the clock runs.

This is your tool for reading a true relative-motion picture **from your own belief**, not the
2D map's compressed symbol view — useful when flying a defensive manoeuvre (BLU-8) or escort
(evade a closing track, or hold station on an escorted asset). Selecting your own
sensor/interceptor as **Chase** and the threat as **Target** adds the **CATS phase angle** (0°
front-lit · 90° side-lit · 180° backlit): a quick read on whether your optical sensor would get a
usable look at the target right now, or a silhouette.

*See also: [RED-10](14-red-cell-manual.md#red-10--ric-frame-view--cats-phase-angle) — the same
view from the targeting side.*

> **Sources:** `spacesim/engine/sun.py` (`cats_phase_angle_deg`) ·
> `spacesim/session/ephemeris.py` (`live_ric_view`, `to_ric`) ·
> `GET /api/sessions/{sid}/ric_view/{cell}` · `spacesim/ui_web/static/ricview.js`

### BLU-12 · Quick TLE export

**View ▾ → Proximity → ⧉ TLE export** gives you a copyable, current-epoch TLE for one object.
The picker lists two kinds of object, and the line under the text box says which one you got:

- **Your own satellites** (every Blue on-orbit asset; ground stations are not listed). The TLE is
  fitted to the satellite's **actual orbit**, and the panel reads *from your satellite (actual
  orbit)*. You do not need a track on your own bird. If you also hold a track on it, the actual
  orbit is still used.
- **Objects you currently hold a Track on.** The TLE is fitted to **your own belief** (the
  track's `state_estimate`), never ground truth, and the panel reads *from your track (belief)*.
  If the target has manoeuvred since your last observation and you haven't re-tasked, the
  exported TLE reflects your stale picture, like every other belief-based view.

Another side's satellite you hold no track on is not listed. Asked for by URL, it is refused with
`blue holds no track on '<id>'`; task a sensor on it first. With nothing to list, the panel reads
*no own satellite or tracked object to export*.

Use it to hand a TLE off to an outside tool for a quick what-if, or to compare a believed TLE
against White's god-truth export (WCM-14) during a debrief on how far your custody had drifted.

> **Sources:** `spacesim/engine/tle_export.py` (`orbit_to_tle`) ·
> `spacesim/session/ephemeris.py` (`quick_tle`, own-satellite branch) ·
> `GET /api/sessions/{sid}/tle/{cell}` · `spacesim/ui_web/static/tleexport.js` (`candidates`,
> `SOURCE_LABEL`)

### BLU-13 · Ephemeris export, your own belief (URL-only)

`GET /api/sessions/{sid}/ephemeris/blue?object_id=&reference_id=&t1=&t2=&interval_s=&format=`
exports **your own believed** state-vector history for a tracked object over a time span — the
time-series sibling of the live RIC view (BLU-11): that view shows your belief right now, this
exports it across a span. There is **no console control for it** — construct the URL yourself
(address bar, script, or `curl`).

Each row carries ECI and RIC (relative to `reference_id`) state vectors, sourced from **your
own `Track.state_estimate`** at each sampled time — never ground truth, never another cell's
belief. A sampled instant at which you held no Track on the object produces **no row for that
instant** (an empty result, not a fabricated one) — if your custody lapsed partway through the
span, the gap in the export is the honest record of that lapse. The reference object resolves to
ground truth only when it is your own asset; otherwise it uses your own belief of it too, same
rule as BLU-11's live view. `format=csv` (default) carries both frames; `format=oem` is
ECI-only CCSDS OEM; `format=ric` is the RIC-only companion file. `t1`/`t2` are sim time as
integer microseconds, the same units the event log uses — not a clock-face time.

This export reads **only your tracks**. You hold no track on your own satellites, so naming one
of your own assets as `object_id` returns a file with the header row and no data. The live RIC
view (BLU-11) behaves differently because it shows your own assets at truth. For your own bird's
history, use the telemetry export (BLU-14) or ask White for the truth export (WCM-15).
`interval_s` follows WCM-15's rules. If you set it, it must be a finite number greater than zero.
A request over **10,000 sampled instants** is rejected (HTTP 400), and the message names the
smallest usable `interval_s`.

Use it to pull your own tracked picture of a target into an outside tool, or to compare your
belief's drift against White's ground-truth export (WCM-15) during a debrief.

> **Sources:** `spacesim/session/ephemeris.py` (`cell_observed_ephemeris`, `to_ric`, `write_csv`,
> `write_oem`, `write_ric_csv`, `sample_times`/`MAX_EXPORT_SAMPLES`) ·
> `spacesim/session/aar.py` (`worlds_at_times`, per-instant replay) ·
> `GET /api/sessions/{sid}/ephemeris/{cell}` ·
> [FS-121](../features/FS-121-ephemeris-export.md) (`FR-7420`/`FR-7430`)

### BLU-14 · Your telemetry CSV export (URL-only)

`GET /api/sessions/{sid}/telemetry/blue/{asset}/export.csv?t1=&t2=&interval_s=` exports your own
asset's full 19-parameter telemetry history over a time span as CSV — the time-series sibling of
the live telemetry panel you already read (BLU-6). Like BLU-13, it is **URL-only**, no console
button.

You can only export assets you own; a different cell's asset is rejected (404), the same
fog-of-war rule the live panel already applies. Each row is computed on the world *replayed to
that exact sampled instant*, so a historical anomaly shows up starting exactly at its own onset
time — never back-dated into rows sampled before it actually fired. That precision is what makes
the export trustworthy for reconstructing "when did this subsystem actually start degrading"
after the fact, rather than just confirming it eventually did.

The span and sampling rules are the same as BLU-13's. A request over 10,000 sampled instants
gets a 400 that names the smallest usable `interval_s`. A zero, negative or NaN `interval_s` is
refused with a **422** on this route.

> **Sources:** `spacesim/session/manager.py` (`telemetry_export`) ·
> `spacesim/engine/telemetry.py` (`sample`, read via per-instant replay) ·
> `spacesim/session/aar.py` (`worlds_at_times`) ·
> `spacesim/session/ephemeris.py` (`sample_times`/`MAX_EXPORT_SAMPLES`) ·
> `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv` ·
> [FS-126](../features/FS-126-telemetry-csv-export.md) (`FR-2320`)

---
