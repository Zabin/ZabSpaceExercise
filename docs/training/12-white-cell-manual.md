[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Traceability matrix](15-manual-traceability.md)

## 12. White Cell manual

The role-scoped manual for the **White Cell facilitator** — the person who owns the room, the
clock, and the scenario. Every section carries a stable ID (`WCM-n`) that is cross-referenced
both directions in [`15-manual-traceability.md`](15-manual-traceability.md): the matrix tells a
developer which sections to re-check when a feature changes, and tells you which features back
each section. Shared mechanics (interface tour, core concepts, full control tables) are
deep-linked, not duplicated — this manual is the *facilitator's procedure layer* on top of them.

### WCM-1 · Role and view

White Cell is the exercise director, adjudicator, and coach. You see **ground truth** — every
asset on both sides, all objectives, every order and effect — while Blue and Red see only their
own fog-of-war picture. You own everything the players must not: the clock, the scenario
parameters, injects, force changes, and the AAR. The cell selector is client-side trust (no
per-cell login): the tool is built for a cooperative room, and you are the reason that works.

> **Sources:** `spacesim/session/manager.py` · `spacesim/session/controller.py` (fog boundary) ·
> [`02-interface.md`](02-interface.md) §3

### WCM-2 · Set up the exercise

1. **Pick a vignette** from the 19-scenario library in the scenario picker (see
   [`06-the-vignette-library.md`](06-the-vignette-library.md) for what each teaches).
2. **Tune the dials.** Every vignette exposes typed parameters with safe defaults — force levels,
   authorities/ROE (`red_kinetic_authorized`), Red behavior (`red_doctrine_profile`,
   `red_ew_intensity`), environment, and fidelity/fog (`fog_of_war`, `ops_fidelity`,
   `safe_mode_susceptibility`). `ops_fidelity` picks the training altitude: `tactical` collapses
   each bus to one health bar, `realistic` (default) shows SOH, `full_ttc` adds full subsystem
   telemetry for TT&C-operator training.
3. **Load → Start.** The **Mission brief panel** auto-opens; you see Blue's and Red's briefs
   side-by-side (the players each see only their own). Confirm the ROE chips and objective
   deadlines match your training intent before you let anyone act.

> **Sources:** `spacesim/content/vignette.py` + `spacesim/content/vignettes/*.yaml` ·
> `GET /api/sessions/{sid}/brief/{cell}` · [`07-white-cell-facilitation.md`](07-white-cell-facilitation.md)

### WCM-3 · Run the room: hot-seat and LAN

- **Hot-seat (one browser):** switch seats with the cell buttons between turns; the ⏸ Handover
  button blurs the screen so the incoming player doesn't see the outgoing cell's picture.
- **LAN cooperative:** launch with `--host 0.0.0.0`, load + start, and share the session URL
  (`…/#sess-N`). Each player opens it and clicks their cell. The server-authoritative clock
  advances exactly once no matter how many tabs are open; every tab converges within ~1.5 s.
- **Multi-monitor:** View ▾ → **Pop out ▸** opens any panel (globe, 2D map, fleet & telemetry,
  order compose, AAR timeline, tracks & objectives) as a separate window joined to the same
  session — spread your god-view across the facilitator station.

> **Sources:** `spacesim/session/inprocess.py` (lazy clock + per-session lock) ·
> `spacesim/ui_web/server.py` (`/api/sessions`, join-by-hash) ·
> [`01-install-and-run.md`](01-install-and-run.md) §2.1

### WCM-4 · Time control: pause, jump, rewind, undo, branch

Only the White tab carries the ⏸ Pause / ▶ Resume toolbar button and the `+1m / +10m / +1h`
jumps — they drive the shared clock for every connected client. Because the engine is
deterministic, **rewind** to any point, **undo** the last actions, or **branch** (rewind, then
continue differently) are byte-exact; use rewind-and-branch deliberately as a teaching move
("let's replay that decision"), then show the fork in the AAR branch-compare (WCM-9). The engine
sub-steps to the next scheduled event, so fast-forwarding never skips a short LEO pass.

> **Sources:** `spacesim/session/manager.py` (`set_clock`/`catch_up`/rewind/undo) ·
> `POST /api/sessions/{sid}/clock` · `spacesim/engine/clock.py`

### WCM-5 · Injects: script the friction

Two layers:

- **Vignette injects** — the scenario's scripted events (`commercial_imagery_leak`,
  `patch_modem`, …), fired one-click from the Injects panel or `POST /inject`.
- **The builder + library** — **Build / schedule inject** opens a form with five reusable
  templates (`debris_field_500km`, `gnss_jam_regional`, `rpo_ambiguous`,
  `gs_outage_diego_garcia`, `space_weather_severe`), an editable effects-JSON editor, and three
  schedule modes: **Now**, **+ N seconds**, **Absolute UTC**. Future-dated injects go through
  the deterministic event log — they replay byte-identical on save/resume and AAR scrub. Past
  timestamps clamp to now.

Add your own templates to `spacesim/content/inject_library.yaml`; they appear in the dropdown on
next session load. Facilitation patterns — when to inject what — are in
[`07-white-cell-facilitation.md`](07-white-cell-facilitation.md).

> **Sources:** `spacesim/content/inject_library.yaml` · `POST /api/sessions/{sid}/inject` ·
> [`02-interface.md`](02-interface.md) §"White-Cell inject builder"

### WCM-6 · Monitor both sides

- **God-view:** the fleet, map, and globe show every asset at true position — no uncertainty
  volumes for you.
- **Activity timeline (Gantt):** you see all three lanes — BLUE, RED, NEUTRAL — every order,
  active effect, and scheduled inject, colour-coded by cell and status-coded by bar style. Click
  a bar for `cell · actor · action · status · window · delivery_path`.
- **Objectives panel:** live per-cell objective state with deadline countdowns — your scoreboard
  for pacing the exercise.
- **Coaching notes:** vignettes may carry `coaching:` entries targeted at a cell and a sim time;
  the Coaching sidebar surfaces them without touching the player's screen. Use them to seed AAR
  discussion points.

> **Sources:** `spacesim/session/scene.py` · `spacesim/ui_web/static/app.js` (Gantt, objectives) ·
> `Vignette.coaching` in `spacesim/content/vignette.py`

### WCM-7 · Change the force mid-exercise: TLE add

Paste a real satellite's two-line element set into the TLE force-add form (or
`POST /force/tle`); it validates and then propagates with SGP4 alongside the fictional assets,
owned by the cell you assign. Use it to drop a real-world reference object into a scenario or to
surprise a cell with a new track to characterize.

> **Sources:** `spacesim/engine/propagator.py` (sgp4 path) · `POST /api/sessions/{sid}/force/tle` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Adding real satellites by TLE"

### WCM-8 · AI-Red doctrine presets

When you have no human Red (or want a doctrinally-flavored baseline), pick a Red doctrine
profile — `china_integrated`, `russia_ew_first`, or `generic` — and step the AI with
`POST /red_step`; each step issues one round of doctrine-prioritized Red orders. The five Red
COA vignettes (RC-01…RC-05) are pre-built campaigns around these profiles.

> **Sources:** `spacesim/session/redai.py` · `POST /api/sessions/{sid}/red_step` ·
> [`06-the-vignette-library.md`](06-the-vignette-library.md)

### WCM-9 · The After-Action Review

The AAR is read-only — it never disturbs the live session. **Replay** the whole exercise,
**scrub** to any decision point and read the exact world state (objectives, asset states,
debris), and **branch-compare** a rewind fork against the main timeline to show how a choice
changed the outcome. Structure the debrief around the decision points you flagged with coaching
notes (WCM-6) and the objective flips.

> **Sources:** `spacesim/session/aar.py` (`snapshot_at`, branch compare) ·
> `GET /api/sessions/{sid}/aar*` · [`05-core-concepts.md`](05-core-concepts.md) §"Red doctrine & AAR"

### WCM-10 · Save, resume, and when things go wrong

**Save** (toolbar) writes a complete snapshot — history, order queue, pending events — to JSON;
**Load** resumes it byte-exact. If the host hardware can't keep the clock at rate, the
**clock-lag watchdog** warns you (consider fewer satellites or a lower rate). For everything
else, start at [`09-troubleshooting-and-glossary.md`](09-troubleshooting-and-glossary.md).

> **Sources:** `spacesim/engine/simulation.py` (`SavedSession`) · `GET /api/sessions/{sid}/save` ·
> `SessionManager._record_catch_up_lag`

---
