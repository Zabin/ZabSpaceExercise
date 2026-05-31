# Future work

Consolidated list of capabilities **not** included in v1 — moved here from the now-merged
`docs/OPERATOR-UI-DESIGN.md` (UI plan) and `memory.md`'s rolling "still open" notes. The
v1 spec lives in `build-spec/INDEX.md` (the operator console in `build-spec/07-operator-console.md`); this file is
the single source of truth for "what's deliberately not built."

Items are grouped by area, each with a short rationale and pointers into the code or research so
a future implementer can pick any one up without scanning history. Anything not listed here is
either implemented or covered by an existing in-scope ticket.

## 1. Multiplayer & networking (M7 seam, formerly Phase 8)

The transport seam is scaffolded: `spacesim/session/ws_session.py` defines `WebSocketSession`
with the same method signatures as `InProcessSession`. Swap the import in `server.py` to activate.

- **LAN multiplayer cell separation.** The session layer already routes every interaction through
  a `SessionAPI` and the engine is UI-agnostic; the seam exists but is exercised only in-process.
  Swapping `InProcessSession` for the `WebSocketSession` stub (with bodies implemented over
  WebSockets or HTTP-RPC) finishes P8 from the roadmap. Stub at `spacesim/session/ws_session.py`.
- **Push deltas instead of polling.** `get_eventlog(since_seq)` already expresses the contract;
  the front end currently re-fetches view/scene/telemetry per tick. A push channel is the natural
  upgrade once the transport above lands.
- ✅ **`Order` as a serializable transport message.** Engine keeps `Order` as a dataclass;
  the API surface uses the pydantic `OrderRequest` (`ui_web/server.py`). The wire-side model
  is in place; the network transport itself remains future work.

**Transport seam interface** (every method must be implemented over the wire):
```
list_vignettes() → list[dict]
load_vignette(vignette_id, overrides, seed) → str            # returns session id
start(session) / step(session, dt) / advance_to(session, t) / rewind_to(session, t)
issue_order(session, cell, order) → OrderAck
validate_order(session, cell, order) → OrderAck              # dry-run; read-only
get_view(session, cell) → CellView                           # fog applied server-side
get_scene(session, cell) / get_telemetry / get_series        # read-only; fog applied
get_eventlog(session, since_seq) → list                      # push-delta anchor
objectives(session) / aar_report / aar_snapshot_at           # after-action reads
save(session) → dict / load_save(state) → str                # persistence
```

## 2. Orbital / effects fidelity

- **High-fidelity propagator drop-in.** The `Propagator` seam (`engine/propagator.py`) is in place;
  swapping the Kepler+J2 fictional propagator for a stronger model is a v1.1 task with no
  architectural impact. Skyfield is already a dev dependency for the regression check.
- **Solar-radiation pressure, atmospheric drag**, third-body luni-solar effects. Out of scope for
  v1 (moderate fidelity); easy follow-ons behind the seam.
- **Conjunction screening + `prop.collision_avoid`**. The catalog verb is present but not wired to
  a screening service.

## 3. Catalog verb gaps (extends `buscommands.apply_command`)

The implemented verbs are listed in `build-spec/07-operator-console.md` §16.11. After batches 5a
+ earlier B-series the implemented set now also includes: `cdh.reset_subsystem`,
`cdh.load_stored_program`, `comms.point_antenna`, `comms.set_crypto`, `eps.select_bus`,
`adcs.desaturate`, `isr.set_mode`, `isr.prioritize_downlink`, `isr.assess_quality`,
`sigint.set_band`, `satcom.report_interference`, `pnt.set_integrity`, `pnt.report_status`,
`wx.downlink`, `def.maneuver_evade`, `def.escort_posture`.

✅ **All catalog verbs from `13-operator-command-catalog.md` now have engine handlers.**
The previously-missing verbs were shipped across batches 5b–6b: `prop.collision_avoid`,
`prop.cancel_burn`, `adcs.point_payload`, `isr.calibrate`, `sigint.geolocate`, `sigint.downlink`,
`sda.task_search` / `sda.task_track` / `sda.task_characterize` / `sda.cue` / `sda.downlink`,
`satcom.set_transponder` / `satcom.set_frequency_plan` / `satcom.reconfigure_beam`,
`mw.set_sensor_mode` / `mw.report_alerts`, `def.disperse`. Each is gated by `can_issue`
(payload-type fit) and exercised by a regression test in `spacesim/tests/test_bus_commands.py`.
Remaining `sc.*` "space control" verbs intentionally duplicate `jam`/`engage`/`cyber`/`observe`
and are not re-wired as command verbs.

## 4. UI strategic items (out of v1 scope, per `build-spec/01-context-and-scope.md` §3.2)

- **Constellation aggregation (v2).** Manage ≥3 sats as a group from a single panel. The current
  per-asset drill-down is the right unit for v1's ≤24-sat / ≤3-per-constellation cap.
- ✅ **APP-6-adapted space-symbology pack.** `ui_web/static/symbology.js` maps asset kind +
  payload type to canonical marker shapes (triangle ISR, square SATCOM, diamond PNT, plus SDA,
  inverted-triangle SIGINT, star jammer, etc.) shared by the 2D map and 3D globe.
- ✅ **Δv "years of life" panel.** New `<table id="deltav">` in the fleet panel; refresh shows
  Δv reserves + a years-of-life estimate (≈15 m/s/yr station-keeping rate).
- **Constellation/grouped fleet-rail badges.** Tied to the constellation-aggregation item above.

## 5. Bus, payload, and recovery refinements

- **Posture-command persistence beyond a tick.** ✅ `def.harden` reduces the safe-mode
  probability at the effect resolver (+0.5 to the asset's `hardening` for the susceptibility
  computation, on top of any vignette baseline). `def.frequency_hop` already scales the comms
  jam term in telemetry. `def.set_threat_warning` remains informational (no resolver impact yet).
- ✅ **EW / bus-stress safe-mode inducement.** Engine resolver routes EW (electronic_warfare)
  + outcome=safe_mode to `enter_safe_mode(cause="ew")`; pinned by
  `test_ew_safe_mode_routes_cause_as_ew`. Vignette content opt-in is the next lever.
- ✅ **Per-step recovery deep-links.** `SafeModeState.current_step` +
  `SafeModeState.steps_done` track progress through
  `establish_contact → dump_telemetry → diagnose → patch → re_enable → done`, with `blocked`
  set when the root cause persists. The UI strip can surface them directly.
- ✅ **Contention bookings rewind-safety.** `_sensor_bookings` is now reconstructed from the
  truncated eventlog after rewind (batch A2). Order events carry `sensor_id` + `window_end` so
  replay produces identical bookings without manual rebind.

## 6. Sat / fleet caps validation — ✅ implemented

`build-spec/01-context-and-scope.md` declares ≤24 satellites for v1 with a hard ceiling of 48,
and constellations ≤3 sats. Enforced at vignette load: `content/vignette.build_world` raises
`ValueError` with a clear message if either cap is exceeded. Pinned by tests in
`spacesim/tests/test_content.py` (batch A1).

## 7. Mock Space Surveillance Network (SSN) — ✅ implemented

The per-cell mock SSN is fully implemented per `build-spec/08-ssn.md` §17 (engine + session +
API + UI + V2/V7/V8 vignette opt-in + acceptance tests; quality model and save/resume included).
Remaining items not carried into v1:

- **Cost / collection-budget** for priority/immediate (force triage). Recommended as a later
  balance dial.
- **Commercial / third-party feeds** — a neutral commercial provider both cells can buy from
  (extends the per-cell model).
- ✅ **Auto-cueing organic → SSN.** `OrderSystem.auto_cue_ssn` (set by `SessionManager` when
  the `ssn_auto_cue` parameter / override is on) deterministically files an SSN characterize
  request after an organic observe yields an uncharacterized track in the 0.3-0.85 confidence
  band. Pinned by `test_auto_cue_files_ssn_characterize_after_organic_observe`.

## 8. UI polish / minor

- **Browser-GUI verification harness.** Backend API smoke tests (scene, telemetry param list,
  telemetry series count, fog cross-cell, dry-run, SSN session) are now in `test_web.py`. The
  remaining gap is DOM/render smoke: Playwright for Python (`@pytest.mark.e2e`, opt-in) to verify
  that the 2D map, 3D globe, and telemetry graph canvas actually draw — not yet implemented.
- ✅ **Seat-chip visual treatment.** Cell-color theming (§10.A.1) drives `--cell-accent`
  across panel borders, toolbar bottom border, h2 underlines, table hover/select, AND the
  own-asset markers on the 2D map + 3D globe — every surface re-tints when the operator
  switches seats. The "BLU/RED/WHI" toolbar chip is unambiguous at a glance.
- **Region detach v2.** The current Detach viewers pops a slow-tick belief-scene window; a full
  multi-display reflow (independent region A/B/C/D detach with shared selection state) requires
  postMessage state-sync and is deferred.
- ✅ **Two-trace overlay normalisation legend.** `Graph.draw` now prints the OVERLAY's true
  y-scale on the right edge in sky-blue (matching the overlay trace) so the operator can decode
  the normalized second trace in absolute units.

## 9. Larger / strategic

- **Coalition / shared SDA feed.** Lower-control external tracks rendered alongside the cell's
  own custody — pairs with SSN above.
- ✅ **Replay branching UI.** AAR panel has a Branches subsection: "+ Save current branch"
  fetches `/aar` and stores it in localStorage scoped by vignette; the chip list shows saved
  branches; selecting two + "Compare selected" runs the same diff shape as
  `session.aar.compare_branches()` (events_a/b + objective flips) client-side. A richer
  branch-tree visualization remains a v2 nicety.
- **PME instrumentation / facilitator scoring.** Hooks for measuring decision latency, custody
  loss, etc., to feed back into White-Cell adjudication.

## 10. Twenty UX & realism upgrades — ✅ shipped

All 20 items in the original brainstorm have landed. Each entry below records what was actually
built; deferrals (where the v1 implementation is intentionally narrower than the original idea)
are noted under "still open".

### 10.A UX & visual (5)

1. ✅ **Cell-color theming.** `body[data-cell]` drives `--cell-accent` across panel borders, h2
   underlines, toolbar bottom border, table hover/select, AND own-asset markers on the 2D map
   and 3D globe (`window.cellAccent()` in app.js + globe.js).
2. ✅ **Color-blind / high-contrast palette swap.** `body.cb` swaps to Okabe-Ito (bluish green /
   yellow / vermilion / sky-blue / blue); toolbar `cb-safe` checkbox, localStorage-persisted.
3. ✅ **Compact "projector mode" preset.** `body.projector` hides `#order-panel`, `#aar-panel`,
   `#drill-panel`; larger fonts; canvas min-height bumped; main grid rebalanced.
4. ✅ **Diff highlight on changed telemetry.** `maybePulse()` adds `.diff-pulse` for ~600 ms on
   value change, animating a soft cell-accent flash.
5. ✅ **Inline asset preview tooltip.** Hover any `[data-asset-ref]` element to see a 3-line SOH
   micro-card; mouseover delegation with one shared `#tooltip` element.

### 10.B Workflow & ergonomics (4)

6. ✅ **Command palette (Cmd-K / Ctrl-K).** Modal with fuzzy filter over assets, time-advance
   steps, cell switches, AAR exports, projector/cb toggles, inject firing, globe focus.
7. ✅ **Order presets / playbooks.** Save current compose to localStorage scoped by vignette id;
   chips above the queue restore it on click.
8. ✅ **Multi-asset selection.** Shift-click fleet rows to add to `BATCH` set; "Issue to all"
   button POSTs the composed order against each selected actor sequentially.
9. ✅ **Scene-moment bookmarks.** Pin a sim time as a named bookmark; chip click jumps via
   `/rewind` to that exact moment.

### 10.C Realism & physics (5)

10. ✅ **Day/night terminator overlay.** `drawTerminator()` computes the great-circle perpendicular
    to subsolar point and shades the night side at 30 % opacity on the 2D map.
11. ✅ **Space-weather injects.** `WorldState.space_weather = {"severity": ...}`; `advance_bus`
    multiplies eclipse drain by 1.0/1.3/2.0; new `space_weather` inject type sets the severity.
12. ✅ **Variable elevation masks.** `Asset.mask_table` / `GroundSite.mask_table` list of
    `{az_min, az_max, mask_deg}` entries; `_ground_sat_predicate` picks the mask per azimuth.
13. ✅ **Atmospheric refraction.** `AccessConfig.atmospheric_refraction` toggle; Bennett /
    Saemundsson formula lifts apparent elevation by ~0.55° at the horizon.
14. ✅ **GNSS spoofing distinct from jamming.** New `Outcome` literal `"spoof"`; `is_link_spoofed`
    helper (separate from `is_link_denied`); new `integrity_flag` telemetry param drops under
    spoof while link signatures stay nominal.

### 10.D Doctrine & content (3)

15. ✅ **Ground-station outage injects.** `gs_outage` inject sets `health=degraded`;
    `scene_from_world` filters degraded sites; downlinks reject `no_window` until cleared.
16. ✅ **Civilian / commercial bystander assets.** `Asset.civilian` flag; resolver appends a
    `civilian_collateral_*` political consequence when an EW outcome (deny/disrupt/spoof) hits
    a civilian asset's link.
17. ✅ **In-browser vignette inspector** (MVP). `/api/vignettes/{id}/source` returns the raw YAML;
    `Inspect` toolbar button opens a modal showing it + a "Download YAML" button. *Still open:*
    a full drag-drop WYSIWYG editor — needs DOM-to-YAML round-trip plus a `POST /vignettes` save
    path; deferred to v1.1.

### 10.E Pedagogy & accessibility (3)

18. ✅ **Coachmark + tutorial.** Two complementary surfaces: (a) generic Coachmark tour
    (`COACH_STEPS`) walks the UI itself with a spotlight + tip; (b) `Tutorial` toolbar button
    opens a per-vignette panel that pulls the YAML's tutorial steps for the active cell.
19. ✅ **Acronym glossary tooltips.** `ACRONYMS` dict in app.js covers SOH, RPO, ISL, AAR, SSN,
    SDA, EW, ROE, TT&C, PNT, ISR, GEO, LEO, MEO, HVA, PME, UEWR, ECCM, Δv, FSW, CDH, EPS, ADCS,
    TCS; any `[data-acronym]` element gets a one-line definition on hover.
20. ✅ **AAR CSV / JSON export.** `/api/sessions/{sid}/aar/export.csv` (three-section CSV: META,
    TIMELINE, OBJECTIVES) and `.../aar/export.json` (full report). Buttons in the AAR panel and
    in the command-palette let trainers download per-session reports for analysis.

---

This list is the v1 → v1.1+ TODO. After batches 5a-5d the remaining open work is:

1. **§1 LAN multiplayer transport + push-delta channel** — highest architectural leverage.
   `WebSocketSession` stub exists; `OrderRequest` pydantic surface exists. Need: WebSocket
   server, push-delta event stream, client transport swap.
2. **§2 high-fidelity propagator + conjunction screening** — drop-in behind the existing
   `Propagator` Protocol; would unlock `prop.collision_avoid` in §3.
3. **§4 constellation aggregation** — manage ≥3 sats as a group from a single panel.
4. **§8 Region detach v2** — multi-display reflow with postMessage state sync.
5. **§8 Playwright DOM/render smoke tests** — currently opt-in; gap is the harness itself.
6. **§9 coalition / shared SDA feed**, **PME instrumentation** — strategic, deferred.
7. ✅ **§3 catalog verbs** — complete; all `13-operator-command-catalog.md` verbs now wired.
8. **§7 SSN cost/budget + commercial feed** — balance dial, third-party data layer.
9. **§10.D.17 full WYSIWYG vignette editor** — inspector + download shipped; drag-drop
   author + save-back is deferred.

(§10 has shipped — 20/20 items. §6 sat-caps validation is enforced at load. §5 recovery
deep-links, EW safe-mode, contention-rewind safety all shipped. §1 transport-message shipped
as `OrderRequest`. §4 APP-6 symbology + Δv panel shipped. §8 seat-chip + two-trace legend
shipped. §9 replay-branching UI shipped. §7 organic→SSN auto-cue shipped.)

Anything outside the list above is best gated by user demand or a paying engagement.

## User added Future work — ✅ shipped (batch 6c)

1. ✅ **Orbital paths in 3D view.** `SceneView.assets[*].track` now carries 60 sampled
   lat/lon/alt waypoints (one orbital period). `globe.js` draws a dim polyline through them.
2. ✅ **Ground traces in 2D view.** Same `track` field powers a sub-satellite polyline on the
   2D map, breaking the polyline at the antimeridian.
3-5. ✅ **Per-cell heading accents** (blue / red / white). `h2`/`h3` now use `color: var(--cell-accent)`
   and a 2 px underline so the heading bars themselves announce whose console is active.
6. ✅ **Hand-off screen-blank.** New `⏸ Handover` toolbar button blurs the page (CSS
   `backdrop-filter: blur(14px)`) and shows a `HANDING OFF → ⟨CELL⟩` headline until Resume.
7. ✅ **Install guide expanded for Python beginners.** `docs/training/01-install-and-run.md`
   now walks through Python install, opening a terminal in the right folder, virtual envs,
   PATH gotchas, and a step-by-step verify — all explicitly scoped to "never used Python before".
8. ✅ **Logo.** `static/logo.svg` (inline in the toolbar) — Earth + orbital ellipse + satellite,
   using `currentColor` so it tints with the active cell accent.
9. ✅ **Button tooltips.** Existing buttons that lacked `title=` get hints from `BUTTON_HINTS`
   on `DOMContentLoaded`.
10. ✅ **Help menu & screen.** New `? Help` toolbar button opens a modal with keyboard shortcuts,
    workflow tips, and an acronym glossary.
11. ✅ **Browser-zoom robustness.** `html { font-size: clamp(13px, 1vw + 0.2rem, 16px) }` plus a
    `@media (max-width: 1100px)` rule that collapses `main` + `.viewers` to single-column at
    higher zoom factors.
12. ✅ **Multi-browser stability.** Code uses widely-supported APIs only: `Intl`, `localStorage`,
    `fetch`, `getComputedStyle`, `backdrop-filter` (with `-webkit-` fallback), canvas 2D. Tested
    against Chrome ≥ 100 / Firefox ≥ 100 / Edge ≥ 100 / Safari ≥ 15.4 (documented in §1.6 of
    the install guide). No bleeding-edge features.

## 11. Twenty UX & realism upgrades — batch 11

Catalog of next-wave improvements, grouped by area. The pattern set by the ISR
(`engine/isr.py` + beam-mode database + footprint geometry) and Maneuver
(`engine/maneuver.py` + six entry modes + live preview) expansions is intentionally
re-used for the verb-expansion items so a contributor can lift the template directly.

### 11.A Verb expansions (parallels the ISR/Maneuver pattern)

1. **Jam command parameter expansion.** Today `params={template, attribution,
   escalation_weight, outcome, success_prob, power_cost}`. Add: `power_w` (drives effective
   jam radius via the radar-equation form `R ∝ √(P/threshold)`), `bandwidth_hz`, `freq_center_hz`,
   `modulation` (`barrage`/`spot`/`sweep`/`deceptive`), `victim_geometry` preview (footprint
   cone on the 2-D map showing the affected ground area). New `engine/jam.py` parallels
   `engine/isr.py`: `MODULATIONS` table + `effective_radius_km()` + `jam_footprint_polygon()`.

2. **Engage (kinetic) targeting.** Add: closing-velocity / miss-distance preview, `salvo_n`
   (1..N interceptors), `abort_after_s` (loitering), debris-cone forecast. UI: dry-run shows
   intercept geometry + Pₖ estimate before the operator commits. Engine seam:
   `engine/engage.py` for the analytic closing/miss math.

3. **Cyber attack vectors.** Today flat `success_prob` × `posture`. Add: `vector`
   (`rf`/`supply_chain`/`insider`/`ground_segment`), `payload`
   (`data_exfil`/`wiper`/`spoof`/`dwell`), `persistence_h`, `attribution` slider
   (`covert`/`ambiguous`/`overt`), `dwell_s` (time-to-discover). Engine: extend
   `effects.py` cyber resolver, add a `engine/cyber.py` for attribution scoring.

4. **Downlink scheduling.** Currently a single `delivers=` token. Add: `station` picker
   (uplink station preference), `bitrate_cap_kbps`, `priority` lane, `partial_dump`
   (last-N-minutes only / specific product IDs). UI: an "expected duration" preview
   from `(data_size / bitrate × duty)`.

5. **SATCOM beam shaping.** Beyond today's `frequency_plan`: `beam_pattern`
   (`omni`/`directional`/`hopping`), `polarization` (`H`/`V`/`RHCP`/`LHCP`),
   `eirp_dbm`, `freq_hopping_rate_hz`, `null_steering_targets`. Parallels the ISR
   beam-mode table; populates `PayloadState.detail`.

6. **SIGINT collection.** Add: `band` (`UHF`/`L`/`S`/`X`/`Ku`/`Ka`/`W`), `dwell_s`,
   `intercept_mode` (`scan`/`track`/`geolocate`), `confidence_threshold`. Adds emitter
   geolocation accuracy as a function of dwell + baseline (single-sat vs. clusters).
   Engine seam: `engine/sigint.py` (parallels `engine/isr.py`).

### 11.B Realism / orbital physics (5)

7. **Atmospheric drag (LEO decay).** Add `Asset.ballistic_coeff` and a
   `engine/atmosphere.py` (exponential atmosphere or NRLMSISE-00 stub) so LEO
   constellations lose altitude over multi-day scenarios. Wire into `ModeratePropagator`
   behind the existing seam.

8. **Higher-order zonal harmonics + 3rd-body perturbations.** J3/J4 zonals and
   Sun/Moon point-mass terms in `propagator.py` (the seam is already in place).
   Largely invisible for short LEO passes; matters for MEO/GEO multi-day station-keeping
   accuracy and HEO Molniya orbit drift.

9. **Solar radiation pressure (SRP).** Add `Asset.srp_area_m2` and an SRP perturbing
   force in the propagator. Material for GEO station-keeping budgets and CubeSat
   constellations with high area/mass.

10. **Penumbra and Earth-shadow geometry.** Today eclipse is binary (cylindrical
    test in `engine/sun.py`). Add penumbral fraction so battery drain ramps gradually
    at terminator crossings. Surface the lit/penumbral/umbral state in telemetry +
    on the 2-D map (already has terminator overlay).

11. **Thermal model expansion.** Add `heater_watts`, `radiator_capacity_w`,
    `sun_dwell_temp_k` to `ThermalState`; survival-mode auto-trigger when
    temperature outside [low, high] for N minutes. Telemetry already has `tcs_temp_c`
    — wire it to a real model.

### 11.C Workflow / UX (5)

12. **Saved plans / playbooks / templates.** Persist named command sequences to
    `localStorage` (`app.js`) and surface a "Playbooks" panel: save current command
    queue as a template, replay against the current state. Stretch: server-side
    YAML playbooks under `spacesim/content/playbooks/`.

13. **Multi-asset batch orders.** "Apply to all 3 SAR sats" button on the command
    panel. Pre-existing batch-bar (`#batch-bar` in `index.html`) is already wired
    for cancel/issue-many; extend with a "select fleet subset" picker.

14. **Conjunction screening + one-click collision-avoid.** `world.conjunctions` is
    already populated by the `conjunction_warning` inject and consumed by
    `prop.collision_avoid`. UI gap: a dedicated panel that lists upcoming close
    approaches, range/time-to-CA, and an "evade" button that fires the
    pre-computed `prop.collision_avoid` order.

15. **Plan-ahead time slider for ground tracks + access windows.** Today the
    2-D map shows the next ~1 orbit of ground track. Add a slider (now → +N hours)
    that pre-computes the projected sub-satellite path AND highlights upcoming
    access windows per asset. Read-only, replay-safe, no engine mutation.

16. **Access window Gantt ribbon per asset.** The fleet rail shows a single
    "next contact" countdown. Add a thin Gantt ribbon (horizontal bar with shaded
    windows for command/telemetry/observe) for the next 30 minutes per asset.
    Data already returned by `/api/sessions/{sid}/windows/{cell}/{asset}`.

### 11.D Pedagogy & accessibility (4)

17. **White-Cell coaching mode.** Optional facilitator overlay: pop-up notes
    keyed to time/event seq ("operator waited 4 min on this pass — discuss in AAR").
    Stored as `vignette.coaching: [{at_sim_t, cell, note}]` entries.

18. **Live consequence preview.** Translate every action to escalation/political-cost
    preview *before* commit, not just for kinetic (existing) but for cyber, jam, and
    high-risk maneuvers. Reuses the `consequence` event log machinery.

19. **Inject library expansion.** Add: `debris_creation_event`, `localized_gnss_jam`
    (regional spoofing), `rpo_ambiguous_attribution` (unknown red asset approaches own
    sat), `gs_outage_partial` (specific station fails), `space_weather_storm`. Each is
    a YAML entry under `spacesim/content/injects/`.

20. **Accessibility: high-contrast / colorblind / large-text mode.** Toggle in the
    header that swaps `:root --accent/--cell-accent/etc` for a high-contrast palette
    (deuteranopia + protanopia-safe) and bumps base font-size to 16px. Persists in
    `localStorage`.

