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
   window, weapons-quality, or ROE gate).
2. **Consequence preview** — severity, escalation weight, reversibility, debris risk, and
   **attribution**: Red's escalation-management dashboard. A reversible EW/cyber effect keeps you
   below the threshold a kinetic strike crosses.
3. **Verb assistants** — `maneuver` (six modes, live Δv), `observe` (beam mode + look angle), `jam`
   (modulation/power/bandwidth with an on-map denial footprint).

*See also: [BLU-3](13-blue-cell-manual.md#blu-3--previews-before-you-commit) — the same preview
mechanics from Blue's side.*

> **Sources:** `spacesim/engine/orders.py` `dry_run()` · `POST /preview/consequence` ·
> `spacesim/engine/{maneuver,isr,jam}.py` · [`02-interface.md`](02-interface.md) §"Order-composition assistants"

### RED-4 · Build a targeting picture with SDA

You can only deny what you can see. **Task scarce sensors** to detect, track, and characterize
Blue's assets; a good report raises track confidence and shrinks uncertainty until it reaches
**weapons-quality**, which **unlocks** the engagement actions the gate was blocking. Sensors do one
thing at a time (contention pushes the second task to a later pass), and custody **decays** between
looks — re-task before a firing window or the gate re-locks.

*See also: [BLU-4](13-blue-cell-manual.md#blu-4--sda-task-sensors-build-custody-unlock-actions) —
the same tasking→custody→unlock loop, applied to defense rather than targeting.*

> **Sources:** `spacesim/engine/custody.py` (weapons-quality gate) · `spacesim/engine/access.py` ·
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

Red's satellites have the same **bus** SOH and safe-mode model as Blue's — Blue can hit back.
Watch the fleet rail's worst-subsystem dots and alarm feed, diagnose incoming attacks from
telemetry signatures (same table as [`13-blue-cell-manual.md`](13-blue-cell-manual.md) §BLU-6), and
run the multi-pass recovery chain (patch the root cause or the asset re-safes). As in BLU-6, each
point on a drill-down history graph is your asset's state at that instant, so where the line
breaks is when the effect actually began — the same value your telemetry CSV export (RED-13)
gives at any instant both of them sample.

> **Sources:** `spacesim/engine/bus.py` · `spacesim/engine/recovery.py` ·
> `spacesim/engine/telemetry.py` · `spacesim/session/manager.py` (`get_series`) ·
> `spacesim/session/aar.py` (`worlds_at_times`) ·
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

**View ▾ → Proximity → ⧉ TLE export** gives you a copyable, current-epoch TLE — but only for an
object Red **currently holds a Track on**; your own un-tracked assets are not exportable (task a
sensor on your own bird first — this is the capability's literal scope, not a bug). The export is
fit to **Red's own belief** (the track's `state_estimate`), never Blue's ground truth: a stale
track exports a stale TLE, exactly as stale as your last look.

Use it to hand your believed picture of a target to an outside tool for a quick what-if, or to
compare against White's god-truth export during an AAR debrief on how far your custody had
drifted from reality.

> **Sources:** `spacesim/engine/tle_export.py` (`orbit_to_tle`) ·
> `spacesim/session/ephemeris.py` (`quick_tle`) ·
> `GET /api/sessions/{sid}/tle/{cell}` · `spacesim/ui_web/static/tleexport.js`

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

Use it to pull your targeting picture of Blue's asset into an outside tool, or to compare your
custody's drift against White's ground-truth export (WCM-15) during an AAR debrief.

> **Sources:** `spacesim/session/ephemeris.py` (`cell_observed_ephemeris`, `to_ric`, `write_csv`,
> `write_oem`, `write_ric_csv`) · `GET /api/sessions/{sid}/ephemeris/{cell}` ·
> [FS-121](../features/FS-121-ephemeris-export.md) (`FR-7420`/`FR-7430`)

### RED-13 · Your telemetry CSV export (URL-only)

`GET /api/sessions/{sid}/telemetry/red/{asset}/export.csv?t1=&t2=&interval_s=` exports your own
asset's full 19-parameter telemetry history over a time span as CSV — the time-series sibling of
the live telemetry readout you already use for own-force management (RED-7). Like RED-12, it is
**URL-only**, no console button.

You can only export assets you own; a different cell's asset is rejected (404), the same
fog-of-war rule the live readout already applies. Each row is computed on the world *replayed to
that exact sampled instant*, so a historical anomaly (e.g. a cyber or EW effect that pushed your
own bird into safe mode) shows up starting exactly at its own onset time — never back-dated into
rows sampled before it actually fired. That precision is what lets you reconstruct exactly when a
degradation began, not just that it eventually happened.

> **Sources:** `spacesim/session/manager.py` (`telemetry_export`) ·
> `spacesim/engine/telemetry.py` (`sample`, read via per-instant replay) ·
> `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv` ·
> [FS-126](../features/FS-126-telemetry-csv-export.md) (`FR-2320`)

---
