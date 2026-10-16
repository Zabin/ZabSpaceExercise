[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Traceability matrix](15-manual-traceability.md)

## 14. Red cell manual

The role-scoped manual for a **Red cell operator** — the adversary commander who denies, degrades,
and (when ROE permits) destroys Blue's space capability while protecting Red's own assets under
fog-of-war. Every section carries a stable ID (`RED-n`) cross-referenced both directions in
[`15-manual-traceability.md`](15-manual-traceability.md). Red and Blue share the same mechanics;
this manual frames them from Red's offensive posture, and defers to the shared concept modules
rather than duplicating them. The mirror-image defensive framing is
[`13-blue-cell-manual.md`](13-blue-cell-manual.md).

### RED-1 · Your view: fog-of-war

You see **only Red's own assets** at true position, plus whatever Red's sensors have detected —
Blue's objects appear only as **tracks** with a growing uncertainty volume, never as ground truth.
The filter is enforced server-side at the `SessionAPI`/`CellController` boundary. Read your
**Mission brief** (auto-opens on load; View ▾ → Mission brief) for situation, mission, forces,
threat picture, ROE, and success criteria — Red's brief never reveals Blue's hidden dispositions
and vice versa.

> **Sources:** `spacesim/session/cells.py` (`CellController`, fog filter) · `spacesim/session/scene.py` ·
> `GET /api/sessions/{sid}/brief/red` · [`02-interface.md`](02-interface.md) §"A player cell"

### RED-2 · Plan-first commanding

You **plan** commands that execute at the next valid window — never instant action on perfect
knowledge. A command reaches a satellite via **ground-station uplink**, **ISL relay**, or a
**stored program**, whichever is soonest. Orders queue with their window and delivery path and are
**cancellable until they uplink**; up to four ride one pass. Sequencing your effects to land inside
the same access window is Red's tempo problem.

> **Sources:** `spacesim/engine/orders.py` (`OrderSystem`, delivery paths) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Plan-first commanding"

### RED-3 · Previews before you commit

1. **Dry-run validity** — the green ✓ / red ✗ line; a blocked action tells you *why* (missing
   window, weapons-quality, or ROE gate). A hand-edited raw JSON param with the wrong type or a
   non-number (`"power_w": "inf"`, text for `salvo_n`) shows ✗ `invalid_param`; a field set to
   `null` counts as left out. [`09` §10](09-troubleshooting-and-glossary.md#10-troubleshooting)
   lists every reason.
2. **Consequence preview** — severity, escalation weight, reversibility, debris risk, and
   **attribution**: Red's escalation-management dashboard. A reversible EW/cyber effect keeps you
   below the threshold a kinetic strike crosses.
3. **Verb assistants** — `maneuver` (six modes, live Δv), `observe` (beam mode + look angle), `jam`
   (modulation/power/bandwidth with an on-map denial footprint).

*See also: [BLU-3](13-blue-cell-manual.md#blu-3--previews-before-you-commit) — the same preview
mechanics from Blue's side.*

> **Sources:** `spacesim/engine/orders.py` `dry_run()`, `_order_params_ok`/`ORDER_PARAM_RULES` ·
> `POST /preview/consequence` · `spacesim/engine/{maneuver,isr,jam}.py` ·
> [`02-interface.md`](02-interface.md) §"Order-composition assistants"

### RED-4 · Build a targeting picture with SDA

You can only deny what you can see. **Task scarce sensors** to detect, track, and characterize
Blue's assets; a good report raises track confidence and shrinks uncertainty until it reaches
**weapons-quality**, which **unlocks** the engagement actions the gate was blocking. Sensors do one
thing at a time (contention pushes the second task to a later pass), and custody **decays** between
looks — re-task before a firing window or the gate re-locks.

Some vignettes give a sensor limits of its own. A **cue-dependent** sensor refuses a target you
hold no track on (the preview shows reason `requires_cue`), so cue it from another sensor first;
an **auto** order skips it for an untracked target. A sensor **hosted** on one of your satellites
answers to either name. A Sun exclusion angle, a minimum range, an orbit-regime specialty, a
usable phase-angle range or a radar's `fence`/`dish` beam mode can remove windows or reduce gain
([`06`](06-the-vignette-library.md#authoring-sensors-optional-modality-fields) lists them). Check
the preview before you plan around a look. `no_window` means the sensor can't see the target
within the planning horizon (the next 24 hours). `sensor_contended` means every window it found
is already booked. When you task a radar, leave the **Mode** dropdown on `auto`: any other entry
replaces the radar's own mode.

*See also: [BLU-4](13-blue-cell-manual.md#blu-4--sda-task-sensors-build-custody-unlock-actions) —
the same tasking→custody→unlock loop, applied to defense rather than targeting.*

> **Sources:** `spacesim/engine/custody.py` (weapons-quality gate) · `spacesim/engine/access.py`
> (`_observation_predicate`) · `spacesim/engine/orders.py` (`_validate` `requires_cue`,
> `_candidate_sensors`, `_plan_collection`, `_resolve_sensor_id`, observe mode in `_exec_payload`) ·
> `spacesim/ui_web/static/index.html` (`#task-beam-mode`) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"SDA sensor tasking"

### RED-5 · The five D's: choose your effect

Effects fall in five categories mapped to five D's — **deceive / disrupt / deny / degrade /
destroy** — resolved by the `EffectResolver` seam. Four are **window-gated** (you need the access
channel: `jam_footprint`, `weapon_engagement`, `sensor_observation`, `rpo_proximity`). Prefer the
**reversible** effects (EW, proximity) to hold escalation down; reach for kinetic only when ROE
authorizes it and you accept the debris and attribution cost the consequence preview shows you.

- **Jam** — barrage / spot / sweep / deceptive modulation; the assistant computes the effective
  denial radius and draws the orange footprint on the 2D map.
- **Engage** (kinetic) — closing geometry, salvo Pₖ, debris-cone estimate; gated on
  weapons-quality custody *and* `red_kinetic_authorized` ROE.
- **RPO** — co-orbital proximity to inspect, shadow, or threaten.

> **Sources:** `spacesim/engine/effects.py` (5 D's) · `spacesim/engine/{jam,engage}.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) · [`../research/INDEX.md`](../research/INDEX.md)

### RED-6 · Cyber: the off-pass wildcard

Cyber is the **exception** — not window-gated. With a modeled access vector it resolves any time
against `{access_vector, success_prob, persistence, patchable}` subject to Blue's cyber posture.
This is Red's fastest, hardest-to-attribute lever (the SATCOM/Viasat-style lesson): you can act
between passes when Blue is watching the wrong timeline. A **persistent** unpatched vulnerability
keeps re-safing the target through its recovery attempts.

*See also: [BLU-9](13-blue-cell-manual.md#blu-9--cyber-cuts-both-ways) — the same mechanic from the
defender's side.*

> **Sources:** `spacesim/engine/cyber.py` (`VECTORS × PAYLOADS`, `attribution_score`) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Cyber — the off-pass exception"

### RED-7 · Manage your own force

Blue can hit back. Its jam, cyber and directed-energy effects leave the same telemetry signatures
on your satellites that yours leave on Blue's. Diagnose them from the drill-down (same table as
[`13-blue-cell-manual.md`](13-blue-cell-manual.md) §BLU-6).

**Bus health depends on the vignette.** The engine applies Blue's **bus** SOH and safe-mode model
to any satellite whose vignette gives it a bus. **None of the shipped vignettes gives a Red
satellite a bus yet**, so in practice you will see:

- `—` for bus mode and battery on the fleet rail, and an uncoloured health dot;
- no safe-mode events;
- nothing for the recovery chain to do.

If a vignette does give a Red satellite a bus, the same rules as BLU-5 and BLU-7 apply. Watch the
worst-subsystem dots and alarm feed, and run the multi-pass recovery chain (patch the root cause
or the asset re-safes).

As in BLU-6, each point on a drill-down history graph is your asset's state at that instant, so
where the line breaks is when the effect actually began. Your telemetry CSV export (RED-13) gives
the same value at any instant both of them sample.

> **Sources:** `spacesim/engine/bus.py` · `spacesim/engine/recovery.py` ·
> `spacesim/engine/telemetry.py` · `spacesim/session/manager.py` (`get_series`) ·
> `spacesim/session/aar.py` (`worlds_at_times`) ·
> `spacesim/ui_web/static/app.js` (`renderFleet`/`rollup`, `—` for a bus-less asset) ·
> `spacesim/content/vignettes/*.yaml` (`red_forces`, no `bus_state` authored) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Bus state-of-health"

### RED-8 · Doctrine profiles and the COA vignettes

When Red is played by AI (or you want a doctrinal template), the doctrine presets
`china_integrated`, `russia_ew_first`, and `generic` prioritize Red's COA differently. The five
Red COA vignettes (RC-01 Layered Denial, RC-02 Cyber-First Access Denial, RC-03 Progressive
Escalation, RC-04 High-Altitude ASAT, RC-05 Allied Targeting) are built around these patterns —
study them as Red's playbook of campaign shapes.

> **Sources:** `spacesim/session/redai.py` · [`06-the-vignette-library.md`](06-the-vignette-library.md) ·
> [`11-vignette-playbooks.md`](11-vignette-playbooks.md)

### RED-9 · Win the vignette

Your objectives and the gates that block the rest (window / weapons-quality / ROE) are laid out
move-by-move in the per-cell playbook. Read your Red row there, sequence your effects against the
crisis window in your Mission brief, and keep the consequence preview in view to stay on the right
side of the escalation line.

> **Sources:** [`11-vignette-playbooks.md`](11-vignette-playbooks.md) ·
> `spacesim/tests/test_vignette_tutorials.py` · `GET /api/vignettes/{id}/tutorial`

### RED-10 · RIC frame view & CATS phase angle

**View ▾ → Proximity → ⊕ RIC frame view** opens a live relative-motion plot: pick an **Origin**
and, optionally, a **Chase** and a **Target**. The picker only offers objects Red **owns or holds
a Track on** (fog-of-war, same rule as every other cell-scoped view) — naming anything else is
rejected outright, never silently substituted. The in-track/radial plot and R/I/C-km table update
continuously as the clock runs, relative to whichever origin you've selected.

This is your targeting tool for a true relative-geometry read **from Red's own belief**: select
your chaser/interceptor as **Chase** and Blue's asset as **Target** to add the **CATS phase
angle** (0° front-lit · 90° side-lit · 180° backlit) — a direct read on whether your own optical
sensor would get a usable look at Blue's bird right now, or a silhouette, before you commit to an
RPO/engagement window (RED-5).

*See also: [BLU-11](13-blue-cell-manual.md#blu-11--ric-frame-view--cats-phase-angle) — the same
view from the defender's side.*

> **Sources:** `spacesim/engine/sun.py` (`cats_phase_angle_deg`) ·
> `spacesim/session/ephemeris.py` (`live_ric_view`, `to_ric`) ·
> `GET /api/sessions/{sid}/ric_view/{cell}` · `spacesim/ui_web/static/ricview.js`

### RED-11 · Quick TLE export

**View ▾ → Proximity → ⧉ TLE export** gives you a copyable, current-epoch TLE for one object.
The picker lists:

- **Red's own satellites** (on-orbit assets only). These are fitted to the satellite's **actual
  orbit**, with or without a track on it, and the panel reads *from your satellite (actual
  orbit)*.
- **Objects Red currently holds a Track on.** These are fitted to **Red's own belief** (the
  track's `state_estimate`), never Blue's ground truth, and the panel reads *from your track
  (belief)*. A stale track exports a stale TLE, exactly as stale as your last look.

A Blue satellite you hold no track on is not listed. Asked for by URL, it is refused with
`red holds no track on '<id>'`; task a sensor on it first.

Use it to hand your believed picture of a target to an outside tool for a quick what-if, or to
compare against White's god-truth export during an AAR debrief on how far your custody had
drifted from reality.

> **Sources:** `spacesim/engine/tle_export.py` (`orbit_to_tle`) ·
> `spacesim/session/ephemeris.py` (`quick_tle`, own-satellite branch) ·
> `GET /api/sessions/{sid}/tle/{cell}` · `spacesim/ui_web/static/tleexport.js` (`candidates`,
> `SOURCE_LABEL`)

### RED-12 · Ephemeris export, your own belief (URL-only)

`GET /api/sessions/{sid}/ephemeris/red?object_id=&reference_id=&t1=&t2=&interval_s=&format=`
exports **Red's own believed** state-vector history for a tracked object over a time span — the
time-series sibling of the live RIC view (RED-10): that view shows your belief right now, this
exports it across a span. There is **no console control for it** — construct the URL yourself
(address bar, script, or `curl`).

Each row carries ECI and RIC (relative to `reference_id`) state vectors, sourced from your own
`Track.state_estimate` at each sampled time — never Blue's ground truth, never a Track you don't
hold. An instant where you held no Track on the object produces **no row for that instant** (an
empty result, not a fabricated one) — if your custody lapsed, the gap in the export is the
honest record of that lapse. The reference object resolves to ground truth only when it is your
own asset; otherwise your own belief of it, same rule as RED-10's live view. `format=csv`
(default) carries both frames; `format=oem` is ECI-only CCSDS OEM; `format=ric` is the RIC-only
companion file. `t1`/`t2` are sim time as integer microseconds, the same units the event log
uses — not a clock-face time.

This export reads **only your tracks**. Red holds no track on its own assets, so naming one of
them as `object_id` returns a file with the header row and no data. The live RIC view (RED-10)
behaves differently because it shows your own assets at truth. For your own bird's history, use
the telemetry export (RED-13). `interval_s` follows WCM-15's rules. If you set it, it must be a
finite number greater than zero. A request over **10,000 sampled instants** is rejected
(HTTP 400), and the message names the smallest usable `interval_s`.

Use it to pull your targeting picture of Blue's asset into an outside tool, or to compare your
custody's drift against White's ground-truth export (WCM-15) during an AAR debrief.

> **Sources:** `spacesim/session/ephemeris.py` (`cell_observed_ephemeris`, `to_ric`, `write_csv`,
> `write_oem`, `write_ric_csv`, `sample_times`/`MAX_EXPORT_SAMPLES`) ·
> `spacesim/session/aar.py` (`worlds_at_times`, per-instant replay) ·
> `GET /api/sessions/{sid}/ephemeris/{cell}` ·
> [FS-121](../features/FS-121-ephemeris-export.md) (`FR-7420`/`FR-7430`)

### RED-13 · Your telemetry CSV export (URL-only)

`GET /api/sessions/{sid}/telemetry/red/{asset}/export.csv?t1=&t2=&interval_s=` exports your own
asset's full 19-parameter telemetry history over a time span as CSV — the time-series sibling of
the live telemetry readout you already use for own-force management (RED-7). Like RED-12, it is
**URL-only**, no console button.

You can only export assets you own; a different cell's asset is rejected (404), the same
fog-of-war rule the live readout already applies. Each row is computed on the world *replayed to
that exact sampled instant*, so a historical effect (e.g. Blue jamming or a cyber attack on
your own bird) shows up starting exactly at its own onset time — never back-dated into
rows sampled before it actually fired. That precision is what lets you reconstruct exactly when a
degradation began, not just that it eventually happened.

The span and sampling rules are the same as RED-12's. A request over 10,000 sampled instants gets
a 400 that names the smallest usable `interval_s`. A zero, negative or NaN `interval_s` is refused
with a **422** on this route.

> **Sources:** `spacesim/session/manager.py` (`telemetry_export`) ·
> `spacesim/engine/telemetry.py` (`sample`, read via per-instant replay) ·
> `spacesim/session/aar.py` (`worlds_at_times`) ·
> `spacesim/session/ephemeris.py` (`sample_times`/`MAX_EXPORT_SAMPLES`) ·
> `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv` ·
> [FS-126](../features/FS-126-telemetry-csv-export.md) (`FR-2320`)

---
