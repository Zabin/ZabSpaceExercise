[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[White Cell manual](12-white-cell-manual.md) · [Traceability matrix](15-manual-traceability.md)

## 12a. White Cell manual — analysis and data exports

The second part of the [White Cell manual](12-white-cell-manual.md). It covers what White Cell
uses to look at, measure and export the exercise: offline research batches, the ground-truth RIC
frame view, and the TLE, ephemeris and telemetry exports. The sections keep the `WCM-n` IDs they
had in the main manual, and [`15-manual-traceability.md`](15-manual-traceability.md) maps them both
ways. It was split out to keep each module near NFR-3500's ~300-line size.

### WCM-12 · Offline research batch exports

Outside a live session, `spacesim/tools/research_batch.py`'s `run_batch(vignette_id, seeds,
condition_label, n_steps_or_until)` runs the same deterministic engine headlessly across a list of
seeds — one fresh session per seed, no shared state between runs — and returns one `RunRecord` per
run: `vignette_id`, `seed`, `condition_label`, and that run's WCM-11 rubric output verbatim (never
recomputed). `spacesim/session/research_export.py`'s `export_csv`/`export_json` flatten a batch of
`RunRecord`s into one row per run for spreadsheet or statistical-tool import — the same pattern the
AAR's own CSV export uses. This is a researcher/instructor tool for comparing conditions across many
seeded runs (e.g. "does `red_ew_intensity: high` change Blue's custody-quality distribution"), not an
in-session facilitator control — there is no UI panel for it; run it from a Python shell or a small
driver script that imports `run_batch`. No trainee-identifying or cross-institution data is collected
by design — only `vignette_id`/`seed`/`condition_label`/the rubric tiers.

> **Sources:** `spacesim/tools/research_batch.py` (`run_batch`) ·
> `spacesim/session/research_export.py` (`RunRecord`, `export_csv`/`export_json`) ·
> [FS-301](../features/FS-301-research-analytics.md) (FR-10210)

### WCM-13 · RIC frame view & CATS phase angle (ground truth)

**View ▾ → Proximity → ⊕ RIC frame view** opens a live panel: pick any on-orbit object as
**Origin**, and optionally a **Chase** and a **Target** (which may be the same object as the
origin, or different). As White you see **every** on-orbit object, at true position, rendered
relative to the origin — not fog-filtered, the same god-view exception every other White-only
view already rides. The panel polls every 1.5 s while open, so the plot and table track the live
clock without a reload.

The view shows an in-track (horizontal) vs. radial (vertical) scatter plot, origin at centre,
auto-scaled to the furthest object, plus a table of **R / I / C** (km) and **range** (km) per
object. Selecting both Chase and Target adds a **CATS illumination-phase-angle** readout — 0°
front-lit, 90° side-lit, 180° backlit — shown as a raw number with no colour or usable/degraded
banding (that visual threshold is a deliberately open design question, not yet decided — see
`BL-0154` in the pipeline backlog). Reselecting any of the three pickers re-renders immediately;
nothing else about the session is disturbed.

Use it in the room to show both cells' true relative geometry during a proximity vignette (e.g.
`geo-rpo-shadowing`), or to sanity-check what a cell's own fogged RIC picture (BLU-11/RED-10)
*should* look like before a debrief.

> **Sources:** `spacesim/engine/sun.py` (`cats_phase_angle_deg`) ·
> `spacesim/session/ephemeris.py` (`live_ric_view`, `to_ric`) ·
> `spacesim/session/manager.py` (`get_ric_view`) ·
> `GET /api/sessions/{sid}/ric_view/{cell}` · `spacesim/ui_web/static/ricview.js`

### WCM-14 · Quick TLE export (ground truth)

**View ▾ → Proximity → ⧉ TLE export** opens a panel: pick any on-orbit satellite and get a
freshly generated, current-epoch two-line element set fitted to its **true** orbit, plus a
**Copy** button (clipboard, with a select-and-Ctrl/⌘+C fallback on plain-HTTP LAN sessions). The
fit is a single-epoch SGP4 mean-element fit computed on the spot, not a stored or re-emitted
source TLE — the panel shows the round-trip fit residual (metres) and the standing limitation
note ("fitted... propagated away from epoch, SGP4 and the simulator's Kepler+J2 model diverge")
under the text box every time.

Use it to hand a real-format TLE for any engine-modelled asset — fictional or TLE-sourced — to an
outside tool (a visualization package, a conjunction checker) without a file-download step. Not
available to the Observer seat, which holds no asset or track ownership of its own to export from.

> **Sources:** `spacesim/engine/tle_export.py` (`orbit_to_tle`) ·
> `spacesim/session/ephemeris.py` (`quick_tle`) · `spacesim/session/manager.py` (`get_tle`) ·
> `GET /api/sessions/{sid}/tle/{cell}` · `spacesim/ui_web/static/tleexport.js`

### WCM-15 · Ephemeris export, ground truth (URL-only)

`GET /api/sessions/{sid}/ephemeris/truth?object_id=&reference_id=&t1=&t2=&interval_s=&format=`
gives you a ground-truth state-vector history for one object over a time span — a different
capability from the *live, current-instant* RIC view (WCM-13): this one is a time-series export
you pull into an outside tool. There is **no console panel or button for it** — it is reachable
only by constructing the URL yourself (paste it into the browser's address bar, or call it from a
script/`curl`), exactly like the offline research export (WCM-12) has no in-session control.

Each sampled row carries both the **ECI** state vector and the **RIC** state vector relative to
your chosen `reference_id` — the same R/T/N radial-in-track-cross-track frame WCM-13's live view
uses, now sampled across the span instead of read live. `format=csv` (the default) carries both
frames in one file; `format=oem` writes a CCSDS OEM 2.0 (Orbit Ephemeris Message) KVN file,
ECI-only (OEM has no native RIC representation); `format=ric` writes a RIC-only companion CSV
pairing with the OEM file. `t1`/`t2` are sim time as **integer microseconds since the Unix
epoch** — the same units `world.now` and the event log use, not a clock-face time you type in
directly; read one off the event log or a save file first. `interval_s` is optional (defaults to
a coarse span/100 sampling, floored at one bus-tick period, so at most 101 rows). If you set it,
it must be a finite number greater than zero, or the request is rejected (HTTP 400). Any request
that would sample more than **10,000 instants** is also rejected with HTTP 400. The error message
names the smallest `interval_s` your span allows (about 0.36 s for a one-hour span).

A requested span **partially** outside the session's own recorded range (from load/start to the
current sim time) is silently clamped to the overlap; a span **wholly** outside it is rejected
(HTTP 400) naming the actual valid range. This is the no-cell, White-Cell-only truth path
(`FR-6220`) — the same binding rule every other no-cell endpoint (`/godview`, `/eventlog`,
`/save`, `/aar*`) already follows; it is not reachable with a `cell` in the URL.

Use it to hand an analyst a real ground-truth ephemeris for a vignette's key asset, or to build an
external conjunction/visualization check against what the engine actually propagated — a job the
live JSON god-view (current instant only) cannot do.

> **Sources:** `spacesim/session/ephemeris.py` (`truth_ephemeris`, `to_ric`, `write_csv`,
> `write_oem`, `write_ric_csv`, `sample_times`/`MAX_EXPORT_SAMPLES`) ·
> `spacesim/session/aar.py` (`worlds_at_times`, per-instant replay) ·
> `GET /api/sessions/{sid}/ephemeris/truth` ·
> [FS-121](../features/FS-121-ephemeris-export.md) (`FR-7410`/`FR-7430`)

### WCM-16 · Per-asset telemetry CSV export (URL-only)

`GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv?t1=&t2=&interval_s=` turns any
asset's subsystem telemetry into a CSV time series — one row per sampled instant × parameter
(19 parameters per asset), covering the same channels the live subsystem drill-down
([UI reference §10.13](10-ui-reference.md#1013-subsystem-drill-down); BLU-6/RED-7 cover the
diagnosis workflow) already shows, now over a requested span
instead of just the current instant. Like WCM-15, **there is no console button for this** — it
is URL-only, by design (`FS-126`'s own scope names only the backing code, no UI affordance).

As White Cell you can request **any** asset's export (`cell=white` bypasses the ownership check
the way every other `/telemetry/{cell}/...` route already does); Blue and Red can only export
their own assets (see BLU-14/RED-13). `t1`/`t2` are the same integer-microsecond sim time units as
WCM-15's ephemeris export; a partially out-of-range span clamps, a wholly out-of-range one is
rejected (400), identically. The same 10,000-instant ceiling applies (400, naming the smallest
usable `interval_s`). A zero, negative or NaN `interval_s` is also refused, but on this route
the status is **422**, not 400.

**The one fact worth understanding precisely:** each exported row is computed on the world
*replayed to that exact sampled instant* — not read off the session's current/final state and
then stamped with an old timestamp. That is why a historical anomaly (e.g. an `FR-4430` anomaly
inject that safed the asset partway through the span) shows up in the export starting from its
own correct onset time, never leaking backward into rows sampled before the inject actually
fired. A naive "read the live value, label it with each requested time" approach would get this
wrong — every pre-onset row would falsely show the anomaly too, because the asset's *current* bus
state (safe-mode, in this example) doesn't know when in the past it actually entered safe mode.
Replaying the event log to each sampled instant is what keeps the export's anomaly timing
trustworthy for AAR analysis.

> **Sources:** `spacesim/session/manager.py` (`telemetry_export`) ·
> `spacesim/engine/telemetry.py` (`sample`, read via per-instant replay) ·
> `spacesim/session/aar.py` (`worlds_at_times`) ·
> `spacesim/session/ephemeris.py` (`sample_times`/`MAX_EXPORT_SAMPLES`) ·
> `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv` ·
> [FS-126](../features/FS-126-telemetry-csv-export.md) (`FR-2320`)

---
