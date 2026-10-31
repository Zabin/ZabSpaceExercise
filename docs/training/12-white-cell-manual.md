[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Traceability matrix](15-manual-traceability.md)

## 12. White Cell manual

The role-scoped manual for the **White Cell facilitator** — the person who owns the room, the
clock, and the scenario. Every section carries a stable ID (`WCM-n`) that is cross-referenced
both directions in [`15-manual-traceability.md`](15-manual-traceability.md): the matrix tells a
developer which sections to re-check when a feature changes, and tells you which features back
each section. Shared mechanics (interface tour, core concepts, full control tables) are
deep-linked, not duplicated — this manual is the *facilitator's procedure layer* on top of them.

**More White Cell procedures** are in [12a](12a-white-cell-analysis-and-exports.md) (analysis and exports,
WCM-12–16), [12b](12b-white-cell-vignette-creator.md) (build your own vignette, WCM-17),
[12c](12c-white-cell-rules-and-staffing.md) (operator seats, approval gates, ROE changes, injects in depth,
WCM-18–20) and [12d](12d-white-cell-clock-saves-and-controls.md) (clock refusals, saves, adding assets,
which seat sees which controls, WCM-21–25).

### WCM-1 · Role and view

White Cell is the exercise director, adjudicator, and coach. You see **ground truth** — every
asset on both sides, all objectives, every order and effect — while Blue and Red see only their
own fog-of-war picture. You own everything the players must not: the clock, the scenario
parameters, injects, force changes, and the AAR. The cell selector is client-side trust (no
per-cell login): the tool is built for a cooperative room, and you are the reason that works.

**A fourth seat, Observer, is yours to designate.** From the **📋 Session ▾** menu's Observer
section, set its **View** to Godview or a named cell (Blue/Red) — the Observer then sees exactly
that view, byte-for-byte identical to its native audience, with zero command ability. Every
mutating request from an Observer-seated session is rejected at the server, not merely hidden in
the UI — the rejection holds even against a request that bypasses the browser client entirely.
Use it to seat an extra trainee, an evaluator, or a second facilitator without giving them any way
to affect the exercise.

> **Sources:** `spacesim/session/manager.py` · `spacesim/session/cells.py` (`CellController`, fog boundary) ·
> `spacesim/session/inprocess.py` (`set_observer_view`/`get_observer_view`, FR-6510) ·
> [`02-interface.md`](02-interface.md) §3

### WCM-2 · Set up the exercise

1. **Pick a vignette** from the 19-scenario library in the scenario picker (see
   [`06-the-vignette-library.md`](06-the-vignette-library.md) for what each teaches).
2. **Tune the dials.** Every vignette exposes typed parameters with safe defaults — force levels,
   authorities/ROE (`red_kinetic_authorized`), Red behavior (`red_doctrine_profile`,
   `red_ew_intensity`), environment, and fidelity/fog (`fog_of_war`, `ops_fidelity`,
   `safe_mode_susceptibility`). `ops_fidelity` picks the training altitude: `tactical` collapses
   each bus to one health bar, `realistic` (default) shows [SOH](09-troubleshooting-and-glossary.md#11-glossary), `full_ttc` adds full subsystem
   telemetry for TT&C-operator training. The same panel's **Classification** field overrides the
   vignette's default banner text — set it once here; it is fixed for the session's lifetime and
   carries into every screen, AAR export, and save file.
3. **Assign seats to roles, if the vignette requires it.** Some vignettes declare mandatory
   staffing (a named asset/constellation needs a bus, payload, or both operator seated before
   Start is allowed). The **Seat-to-role assignment** section of the same menu lets you bind a
   seat name to an asset/constellation and a role (Bus / Payload / Both); the **staffing report**
   readout beneath it lists any mandatory requirement still unmet. Most vignettes declare none — no
   assignment is needed and Start is never blocked by this step for them. What the operator seat does for
   players, and how re-binding works, is in [WCM-18](12c-white-cell-rules-and-staffing.md).
4. **Load → Start.** The **Mission brief panel** auto-opens; you see Blue's and Red's briefs
   side-by-side (the players each see only their own). Confirm the ROE chips and objective
   deadlines match your training intent before you let anyone act. If a mandatory seat-to-role
   requirement from step 3 is still unmet, **Start** refuses with the unsatisfied entry named — it
   is a hard gate, not a warning you can click through.

**Writing your own vignette?** Sensors accept optional fields: a solar exclusion angle, a
minimum range, an orbit-regime affinity, a cue requirement, a host satellite, and a usable
phase-angle range. The table in
[`06-the-vignette-library.md`](06-the-vignette-library.md#authoring-sensors-optional-modality-fields)
says what each one does. A radar can also take a default `fence` or `dish` beam mode. A malformed
phase-angle range, an unknown radar beam mode, or a misspelt orbit regime stops the vignette from
loading, so fix it before the session.

**If Load is refused.** The whole vignette is checked when you press **Load**. If it fails, no
session starts and the session line in the **Cell & Time** panel shows **Load failed:** with a list of every problem, each
naming where it is in the YAML and why. Fix them all and press **Load** again; a refused load
leaves any open session alone. The last check (listed under `build`) runs only once nothing else
is wrong, so a retry can turn up one new item. A file that is not valid YAML does not appear in
the vignette picker at all. Besides the sensor rules, Load refuses a satellite with no orbit,
another asset (except a cyber unit) with no location, a [TLE](09-troubleshooting-and-glossary.md#11-glossary) that will not propagate to the start
time, a duplicate asset or sensor id, and a `roles_needed` entry naming an asset or group that is
not in the vignette. The full list is in
[`06-the-vignette-library.md`](06-the-vignette-library.md#when-a-vignette-wont-load).

> **Sources:** `spacesim/content/vignette.py` + `spacesim/content/vignettes/*.yaml` ·
> `GET /api/sessions/{sid}/brief/{cell}` · `spacesim/session/manager.py` (`classification`,
> `assign_role`/`staffing_report`, FR-4510/FR-4210) · `spacesim/engine/entities.py` (`Sensor`
> modality fields and their load-time checks, FR-1610–FR-1670) · `spacesim/content/vignette.py`
> (`validate_vignette`, `VignetteValidationError`, `list_vignettes`) · `spacesim/ui_web/static/app.js`
> (`loadSession`, the **Load failed** readout; FR-5310–FR-5314) ·
> [`07-white-cell-facilitation.md`](07-white-cell-facilitation.md)

### WCM-3 · Run the room: hot-seat and LAN

- **Hot-seat (one browser):** switch seats with the cell buttons between turns; the ⏸ Handover
  button blurs the screen so the incoming player doesn't see the outgoing cell's picture. Pressing it shows a full-screen `HANDING OFF → RED` (from Blue; from Red it says BLUE, from White it says WHITE) with "Pass the keyboard to the RED operator and click Resume." The overlay's **Resume** button switches the console to that seat. (It is a different button from the clock's ▶ Resume.) It hides the screen only; it is not security.
- **LAN cooperative:** launch with `--host 0.0.0.0`, load + start, and share the session URL
  (`…/#sess-N`). Each player opens it and clicks their cell. The server-authoritative clock
  advances exactly once no matter how many tabs are open; every tab converges within ~1.5 s.
- **Multi-monitor:** View ▾ → **Pop out (multi-screen)** opens any panel (globe, 2D map, fleet & telemetry,
  order compose, AAR timeline, tracks & objectives) as a separate window joined to the same
  session — spread your god-view across the facilitator station.

> **Sources:** `spacesim/session/inprocess.py` (lazy clock + per-session lock) ·
> `spacesim/ui_web/server.py` (`/api/sessions`, join-by-hash) ·
> [`01-install-and-run.md`](01-install-and-run.md) §2.1

### WCM-4 · Time control: pause, jump, rewind, undo, branch

Only the White tab carries the ⏸ Pause / ▶ Resume toolbar button (Resume resets the clock rate to 1; see WCM-21) and the `+1m / +10m / +1h`
jumps — they drive the shared clock for every connected client. Because the engine is
deterministic, **rewind** to any point, **undo** the last actions, or **branch** (rewind, then
continue differently) are byte-exact; use rewind-and-branch deliberately as a teaching move
("let's replay that decision"), then show the fork in the AAR branch-compare (WCM-9). The engine
sub-steps to the next scheduled event, so fast-forwarding never skips a short LEO pass.
**Advance bounds.** A jump (the `+1m / +10m / +1h` buttons, the palette's advance entries) can
only move time forward and never past the end of the exercise's span, which is the vignette's start
plus 366 days. A request that goes backwards, is not a finite number, or reaches beyond the span is
refused (HTTP 400) with the reason, and the clock and world are unchanged; use rewind to go back. A
running clock does not stop at the end of the span with an error: it is pinned there, so it simply
stops advancing at the span end while still showing as running.
A rewind must land inside the exercise, between its start and the current moment; the toolbar
Rewind and the palette's "rewind to start" go to the vignette's first instant, and the server
refuses anything outside that span. Undo obeys the same rule: undoing past the first logged
event returns the clock to the exercise start, and an undo with nothing to undo is refused.
Rewind and undo do not pause a running clock: it keeps running from the rewound moment, so pause
first (▶/⏸) if you want to stand at the earlier instant. When a jump, rewind or inject is refused,
the reason appears in the red status line under the session label in the **Cell & Time** panel
(prefixed `Advance:`, `Rewind:` or `Inject:`); nothing about the exercise changes. Only the White seat can rewind: a
Blue or Red tab, or a bookmark clicked from one, gets a refusal instead. The exact refusal text for every bound, the
clock-rate limits and the HTTP-only undo are tabulated in [WCM-21](12d-white-cell-clock-saves-and-controls.md).

> **Sources:** `spacesim/session/manager.py` (`step`/`advance_to`/`_span_ceiling`/`_catch_up_locked`/`rewind_to`/`undo_last`) ·
> `spacesim/ui_web/static/app.js` (`stepBy`, `rewindTo`, `reportControlError`; `#control-status`) ·
> `POST /api/sessions/{sid}/clock` · `…/step` · `…/advance` · `…/rewind` · `…/undo` · `spacesim/engine/clock.py`

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
- **Bad injects are refused whole.** If any effect is malformed or cannot land (e.g. an
  `anomaly` on a satellite with no bus, which includes every shipped Red satellite), the server
  rejects the inject with HTTP 400 and applies none of it. The builder's result line shows
  `✗ server error: … inject rejected: #i <type>: <reason>`; the **Fire** button shows nothing.
  A vignette's own timed or conditional inject with a malformed effect skips just that effect and
  tells only you, in **Messages**: `inject effect skipped (<type>): <reason>`. Full rules:
  [UI reference §10.3](10-ui-reference.md#103-injects-white-cell--build--schedule-inject).

Add your own templates to `spacesim/content/inject_library.yaml`; they appear in the dropdown on
next session load. Facilitation patterns — when to inject what — are in
[`07-white-cell-facilitation.md`](07-white-cell-facilitation.md).

> **Sources:** `spacesim/content/inject_library.yaml` · `POST /api/sessions/{sid}/inject` ·
> `spacesim/session/manager.py` (`fire_inject`, `validate_inject_effects`, `_skip_inject_effect`) ·
> `spacesim/ui_web/static/app.js` (`fireBuiltInject`, `fireInject`) ·
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
- **Any asset's telemetry:** click any fleet row, Blue or Red, to open its subsystem drill-down:
  parameters vs. limits, history graph with the nominal ghost, and symptom log. It shows exactly
  what that cell's operators read in BLU-6/RED-7, so use it to see an attack's signature land.
  Controls: [UI reference §10.13](10b-ui-reference-views.md#1013-subsystem-drill-down).

**Scheduled injects are on your timeline only.** Injects you schedule (including future-dated ones) appear as `inject (N effects)` bars on White's own Activity timeline. Blue and Red never see them, nor your edits or cancels; they only see the effect once it starts on their own assets.

> **Sources:** `spacesim/session/scene.py` · `spacesim/ui_web/static/app.js` (Gantt, objectives,
> `openDrill`) · `spacesim/session/manager.py` (`get_telemetry`/`get_series`, White reads any asset) ·
> `Vignette.coaching` in `spacesim/content/vignette.py`

### WCM-7 · Add real satellites by TLE or OMM (before Start)

You can drop a real satellite into a scenario from its two-line element set (TLE), or a whole file of
them (multi-object TLE or CCSDS OMM), but **only between Load and Start**. Once the exercise is running
the server refuses with `cannot edit force after start`. There is no console form for a loaded session;
it is an API call (`POST /force/tle`, `POST /force/bulk_import`) or part of building a vignette in the
Creator ([WCM-17](12b-white-cell-vignette-creator.md)). The object propagates with SGP4 alongside the
fictional assets, owned by the cell you assign. Use it to drop a real-world reference object into a
scenario or to give a cell a new track to characterize. Step-by-step calls, every refusal message and the
silent-replace and empty-reply traps are in [WCM-23](12d-white-cell-clock-saves-and-controls.md).

> **Sources:** `spacesim/engine/propagator.py` (sgp4 path) · `POST /api/sessions/{sid}/force/tle` ·
> `spacesim/session/manager.py` (`add_tle`, `bulk_import`) ·
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
changed the outcome. A variable-speed **playback** of the recorded exercise also exists, but only
as the HTTP routes under `/aar/playback/` (the console has no playback control). A session holds
one playback cursor, shared by every seat: starting one replaces the last, and it is not kept per
seat. You (White) may start it from ground truth or either cell's viewpoint; Blue and Red may
play back only their own viewpoint, and only while the shared playback is on their own cell;
Observer may only read its state. A refused request is a 403 and nothing changes. The seat is
asserted by the request, not authenticated (WCM-3 trust model). Structure the debrief around the decision points you flagged with coaching
notes (WCM-6) and the objective flips.

> **Sources:** `spacesim/session/aar.py` (`snapshot_at`, branch compare) ·
> `GET /api/sessions/{sid}/aar*` · `POST …/aar/playback/*` ·
> `spacesim/session/inprocess.py` (`playback_seat_decision`) · [`05-core-concepts.md`](05-core-concepts.md) §"Red doctrine & AAR"

### WCM-10 · Save, resume, and when things go wrong

**Save** (**⚙ Settings ▾ → ⬇ Save session**) writes a complete snapshot — history, order queue, pending events — to JSON;
**⬆ Load session** (same menu) resumes it byte-exact, with the clock paused. A save carries the vignette it was started from, so it resumes even if that vignette file has since been edited, renamed or deleted (older saves reload the file by id, and Load tells you so). If the host hardware can't keep the clock at rate, the
**clock-lag watchdog** warns you (consider fewer satellites or a lower rate). For everything
else, start at [`09-troubleshooting-and-glossary.md`](09-troubleshooting-and-glossary.md). The full
list of Load refusals and what to do about each is in [WCM-22](12d-white-cell-clock-saves-and-controls.md).

**If Load of a save is refused.** The file is checked before anything is replayed. A file that is not
JSON, lacks required parts, has a damaged event log, claims an end time earlier than its own last
event or more than 366 days past the exercise start, depends on a vignette file that is gone (older
saves), or embeds an invalid vignette is refused with a reason shown as **Load failed:** in the
session label. Nothing is loaded and your current session is untouched. Only the White seat can load
a save; from a Blue or Red tab the server refuses it.

> **Sources:** `spacesim/engine/simulation.py` (`SavedSession`) · `POST /api/sessions/load_save` (`validate_save`, `_check_final_time_span`) · `GET /api/sessions/{sid}/save` ·
> `SessionManager._record_catch_up_lag` · `SessionManager.save_state` · `SessionManager.from_state`

### WCM-11 · Competency assessment: rubric, not a score

Below the AAR panel, the **Competency assessment** panel reads out three tier-based dimensions per
cell — **custody quality**, **window discipline**, and **belief-truth divergence** — computed
automatically from the exercise's own eventlog. Click **🔄 Refresh** any time after the exercise has
generated enough activity to score. There is deliberately **no composite score**: the three tiers
are shown side-by-side, and the disclosure line beneath them states plainly that the aware/unaware
split on belief-truth divergence is a design choice (reusing the engage weapons-quality threshold as
the "operator-visibly-marginal" band), not a validated psychometric boundary — read that disclosure
before treating the tiers as more authoritative than they are. Two dimensions FS-201 originally
scoped — a longitudinal per-trainee report across exercises, and self-assessment access for Blue/Red
— are not implemented; this panel is White-Cell-only and covers only the current exercise (tracked
as `BL-0019`/`BL-0020` in the pipeline backlog, not a bug — the panel does exactly what it discloses).

> **Sources:** `spacesim/session/assessment.py` (`score_custody_quality`/`score_window_discipline`/
> `score_belief_truth_divergence`/`assessment_report`) · `GET /api/sessions/{sid}/assessment` ·
> [FS-201](../features/FS-201-competency-assessment.md) (FR-10110)

### Analysis and data exports (WCM-12 to WCM-16)

The analysis and export sections (offline research batches, the [RIC](09-troubleshooting-and-glossary.md#11-glossary) frame view and CATS phase
angle, quick TLE export, the time-span ephemeris export and the per-asset telemetry CSV export)
are in [`12a-white-cell-analysis-and-exports.md`](12a-white-cell-analysis-and-exports.md). They keep
their IDs, `WCM-12` to `WCM-16`.

---
