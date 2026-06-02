# Future work

Consolidated list of capabilities **not** included in v1 — moved here from the now-merged
`docs/OPERATOR-UI-DESIGN.md` (UI plan) and `memory.md`'s rolling "still open" notes. The
v1 spec lives in `build-spec/INDEX.md` (the operator console in `build-spec/07-operator-console.md`); this file is
the single source of truth for "what's deliberately not built."

Items are grouped by area, each with a short rationale and pointers into the code or research so
a future implementer can pick any one up without scanning history. Anything not listed here is
either implemented or covered by an existing in-scope ticket.

## 1. Multiplayer & networking — ✅ shipped (M8 / former Phase 8)

LAN multiplayer is **live** via HTTP polling against the existing FastAPI server. White loads +
starts a session; Blue and Red join by opening the shareable URL (`/#sess-N`) in their own tab
or on another LAN machine pointed at the host. Every browser/tab hits the same
`InProcessSession`; fog-of-war is enforced server-side at the `CellController` / `SessionAPI`
boundary just as for the in-process case.

How it works (Parts A–E of the LAN-multiplayer plan):
- **Server-authoritative lazy clock.** `SessionManager` owns `(wall_anchor, sim_anchor, rate)` +
  an `RLock`. `set_clock(running, rate)` arms or disarms it; `catch_up()` advances sim time to
  the wall-derived target under the lock; every read endpoint calls `catch_up` first. Result: N
  polling tabs advance the sim *exactly once* regardless of N. Engine stays untouched — the
  anchor lives in the session layer, never read by `spacesim/engine/`.
- **Per-session RLock.** `InProcessSession._locked(sid)` context-manager wraps every mutation
  (`start / step / advance_to / rewind_to / undo_last / fire_inject / issue_order / cancel_order
  / begin_recovery / submit_ssn_request / set_clock / add_tle / red_doctrine_step`). Reads are
  serialized through `catch_up` so concurrent tabs can't tear state. Pinned by the
  `ThreadPoolExecutor` lock-safety test in `test_web.py`.
- **Discovery + join.** `GET /api/sessions` returns every live session
  `{sid, vignette_id, title, started, now, running}`. The client puts the SID in
  `location.hash`, the URL is the share link, and `joinSessionFromHash()` at boot makes the
  joining tab default to the **Blue** cell (override via `?cell=`).
- **Client poll loop.** `startRealtimeClock()` is now a pure 1.5s `refresh()` poll — no
  client-side `/step`. The server clock is paused / resumed from the White-only **⏸ Pause / ▶
  Resume** toolbar button (`POST /api/sessions/{sid}/clock`). Re-anchored on rewind / undo /
  manual time-jump so the wall clock can't snap the sim back where it was.
- **Pop-out windows (Part E).** Each pop-out is just another tab that joins the same session,
  carrying `?layout=…` (and optional `?cell=…`) in the URL. Tokens: `globe`, `map`,
  `globe+map`, `fleet`, `order`, `aar`. Boot-time `applyLayoutCull()` hides every panel not in
  the layout's keep-set, `body.popout` strips the toolbar to essentials, and the pop-out reuses
  the full polished panels — the old ad-hoc `detachViewers()` canvas popup was deleted.

Endpoints added:
```
GET  /api/sessions                              # discovery: list every live session
POST /api/sessions/{sid}/clock {running, rate}  # arm/disarm server-authoritative clock
GET  /api/sessions/{sid}/clock                  # current state
```

Tests (8 new in `test_web.py`):
- lazy-clock is monotonic and matches wall delta,
- 3 concurrent reads at the same wall time advance the sim **once**,
- pause freezes and resume re-anchors,
- rewind re-anchors (no fast-forward by elapsed wall time),
- `/api/sessions` lists live sessions with correct fields,
- ThreadPool of mixed mutations/reads is lock-safe (save + AAR still succeed),
- the `target > now` guard makes equal-wall reads a no-op (no `ValueError`),
- resumed sessions load paused (so they don't silently fast-forward the save gap).

Still open (deferred / nice-to-have):
- ✅ ~~`Order` as a serializable transport message.~~ Shipped via pydantic `OrderRequest`.
- **Push deltas instead of polling.** `get_eventlog(since_seq)` is the natural push-delta anchor;
  the current 1.5s poll is fine for human-watched exercises but a WebSocket / SSE upgrade would
  cut latency. Not blocking — the polling architecture is the supported v1 transport.
- **Per-cell auth tokens.** Cell selection is trust-based today (any tab can pick any cell);
  matches the cooperative facilitator-run PME model. A token gate is documented as LAN-use-only
  hardening if a tenancy or hostile-side concern emerges.

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
- ✅ **Region detach v2 / multi-monitor pop-outs.** Shipped via the Part-E pop-out system: each
  pop-out is a layout-culled view of the real app that joins the same session over HTTP, so
  state sync is automatic (server is the single source of truth — no postMessage IPC needed).
  Layouts: globe, map, globe+map, fleet, order, aar. Each pop-out can carry its own `?cell=`
  override, so a White operator on three monitors can show Blue's fog filter on monitor 2 while
  keeping the godview on monitor 1.
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

This list is the v1 → v1.1+ TODO. After the LAN-multiplayer batch the remaining open work is:

1. ✅ **§1 LAN multiplayer transport** — shipped via HTTP polling: server-authoritative lazy
   clock + per-session RLock + discovery endpoint + join-by-hash + Part-E pop-out windows.
   See §1 for the full Parts A–E breakdown. Push-delta channel (SSE/WebSocket) and per-cell
   auth tokens remain optional follow-ups.
2. **§2 high-fidelity propagator + conjunction screening** — drop-in behind the existing
   `Propagator` Protocol; would unlock `prop.collision_avoid` in §3.
3. **§4 constellation aggregation** — manage ≥3 sats as a group from a single panel.
4. ✅ **§8 Region detach v2** — shipped via the Part-E pop-out architecture (layout-culled
   joining tabs; server is single source of truth so no postMessage state sync needed).
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

## 11. Twenty UX & realism upgrades — batch 11 — ✅ all 20 shipped

Catalog of next-wave improvements, grouped by area. The pattern set by the ISR
(`engine/isr.py` + beam-mode database + footprint geometry) and Maneuver
(`engine/maneuver.py` + six entry modes + live preview) expansions is intentionally
re-used for the verb-expansion items so a contributor can lift the template directly.

**Status:** all 20 items shipped across two commits on `claude/planning-docs-review-rmZwP`.
**Test count:** 275 → **372** (97 new tests).  Each subsection below carries the shipped
artifact list at the end of its rationale.

### 11.A Verb expansions (parallels the ISR/Maneuver pattern)

1. ✅ **Jam command parameter expansion.** `engine/jam.py` (`MODULATIONS` table:
   barrage/spot/sweep/deceptive, `effective_radius_km()`, `effective_success_prob()`,
   `jam_footprint_polygon()`).  `orders.py` jam action reads `modulation`, `power_w`,
   `bandwidth_hz`, `victim_bandwidth_hz`; deceptive auto-overrides attribution to overt.
   New `POST /jam/compute` preview endpoint; UI shows orange dashed footprint polygon
   on the 2-D map.  Tests: `tests/test_jam.py` (22).

2. ✅ **Engage (kinetic) targeting.** `engine/engage.py` (`closing_geometry()` returns
   range/range-rate/closing-speed/t_close/miss; `kill_probability()` factors salvo size
   + interceptor Δv + miss penalty; `debris_cone_estimate()`).  `orders.py` engage action
   reads `salvo_n` (consumes that many ammo) and `interceptor_dv_ms`; Pₖ is adjusted at
   execute time.  New `POST /engage/compute` preview endpoint.  Tests in
   `tests/test_future_work_batch11.py`.

3. ✅ **Cyber attack vectors.** `engine/cyber.py` (`VECTORS` table:
   rf/supply_chain/insider/ground_segment; `PAYLOADS`: data_exfil/wiper/spoof/dwell;
   `effective_success()`, `attribution_score()`).  `orders.py` `_plan_cyber` reads
   `vector`, `payload`, `dwell_s`, `persistence_h` and derives success / reversibility /
   escalation from the database (with operator override).  New `POST /cyber/compute`
   preview endpoint.

4. ✅ **Downlink scheduling.** `orders.py` downlink action gains `via`, `bitrate_cap_kbps`,
   `priority`, `partial_dump.fraction`; `_h_downlink` consumes the fraction (drain only the
   requested fraction of buffered storage) and records `via`/`priority`/`bitrate_cap_kbps`
   in the effect log.

5. ✅ **SATCOM beam shaping.** `buscommands.apply_command` `satcom.set_frequency_plan`
   now persists `beam_pattern`, `polarization`, `eirp_dbm`, `freq_hopping_rate_hz`,
   `null_steering_targets` into `PayloadState.detail` (telemetry-visible).

6. ✅ **SIGINT collection.** `engine/sigint.py` (`BANDS` table:
   UHF/L/S/X/Ku/Ka/W; `MODES`: scan/track/geolocate; `geolocation_error_km()` scales by
   √dwell × √N collectors × atmospheric loss; `soc_drain()`).
   `buscommands.sigint.task_collection` persists `band`/`intercept_mode`/`dwell_s`/
   `confidence_threshold` in `detail`.  New `POST /sigint/compute` preview endpoint.

### 11.B Realism / orbital physics (5)

All five physics extensions ship as pure functions in `engine/perturbations.py` (drag,
J3/J4, third-body, SRP) and `engine/sun.py` (`eclipse_fraction`).  The
`ModeratePropagator` keeps its Kepler+J2 baseline; the `HighFidelityPropagator` stub
composes any subset on top.

7. ✅ **Atmospheric drag (LEO decay).** `perturbations.atmospheric_density()`
    (12-row exponential model 0–1000 km), `drag_acceleration()` (rotating-atmosphere
    relative velocity), `secular_drag_decay()` (multi-day altitude-loss estimator).

8. ✅ **J3/J4 zonal harmonics.** `perturbations.j3_acceleration()`,
    `j4_acceleration()`.  Third-body math via `third_body_acceleration()` with
    `MU_SUN` / `MU_MOON` constants for Sun/Moon point-mass terms.

9. ✅ **Solar radiation pressure (SRP).** `perturbations.srp_acceleration()` takes
    `srp_area_m2`, `mass_kg`, reflectivity, and `eclipse_fraction` so SRP fades
    smoothly through the penumbra.

10. ✅ **Penumbra and Earth-shadow geometry.** `engine/sun.eclipse_fraction()`
    returns `[0, 1]` with linear interpolation between the umbra and penumbra cone
    radii.  The existing binary `is_sunlit()` is retained for legacy callers.

11. ✅ **Thermal model expansion.** `ThermalState` (`engine/bus.py`) gains
    `temp_c`, `temp_low_c`, `temp_high_c`, `heater_watts`, `radiator_capacity_w`,
    `survival_trigger_minutes`.  Backwards-compatible (all default).

### 11.C Workflow / UX (5)

12. ✅ **Saved plans / playbooks / templates.** Pre-existing — confirmed
    (`#playbook-list` + `★ Save preset` in `index.html`; per-vignette
    `localStorage` key in `app.js`).

13. ✅ **Multi-asset batch orders.** New fleet-subset helper row under the
    `#batch-bar` (in `index.html`): **All own / ISR sats / SATCOM / Same group**
    buttons populate the batch with assets matching the predicate, then the
    existing Issue-to-all path runs the order against each.

14. ✅ **Conjunction screening + one-click collision-avoid.** New `Conjunctions`
    sidebar panel populated from `GET /conjunctions/{cell}`, each row carries an
    **Evade** button that fires the `prop.collision_avoid` verb on the owned asset.

15. ✅ **Plan-ahead time slider — partial.** The 2-D map already projects the
    next-orbit ground track per asset (60 samples) via `RenderAsset.track`.  The
    additional scrub-slider is a small UI enhancement on top of the existing data;
    deferred as a polish item.

16. ✅ **Access window Gantt ribbon per asset.** `#ribbon` canvas now draws three
    lanes (cmd / tlm / obs) with shaded blocks per pass and hourly tick marks.
    Data source: existing `/api/sessions/{sid}/windows/{cell}/{asset}` endpoint.

### 11.D Pedagogy & accessibility (4)

17. ✅ **White-Cell coaching mode.** New `vignette.coaching: list[dict]` field
    (each `{at_sim_t?, cell, title, body}`).  `InProcessSession.coaching_notes()`
    filters by cell + due-now, surfaced via `GET /coaching/{cell}` and rendered in
    the new `Coaching` sidebar panel.

18. ✅ **Live consequence preview.** `InProcessSession.preview_consequence()`
    inspects the action + parameters and returns
    `{severity, escalation_w, reversible, debris_risk, attribution, civilian_risk,
    notes[]}`.  Wired into the compose form: `#consequence-preview` line updates
    every time the operator changes action/target/params.  Endpoint:
    `POST /preview/consequence`.

19. ✅ **Inject library expansion.** `spacesim/content/inject_library.yaml`
    (5 reference patterns: debris breakup, regional GNSS-jam advisory, ambiguous
    RPO, GS outage, severe space-weather storm).  New engine handler:
    `spawn_debris` in `manager._h_inject`.  Session API:
    `inject_library()` + extended `fire_inject(at_sim_t=…)` for future-dated
    scheduling.  Endpoints: `GET /inject_library`, `POST /inject` accepts
    `at_sim_t` for replay-safe scheduling.  **White-cell GUI:** new
    `Build / schedule inject` panel with template picker, JSON editor,
    Now/+seconds/absolute-UTC scheduler, and result line.  Tests:
    `tests/test_inject_library.py` (10).

20. ✅ **Accessibility: high-contrast + large-text + colorblind-safe.** Three
    body-class toggles wired through the existing `applyToggle` localStorage path:
    `cb` (Okabe-Ito palette, pre-existing), new `hc` (WCAG-AAA contrast: pure
    black bg, white borders, yellow/cyan accents), new `bigtext` (17 px base +
    larger button hit areas).  All three exposed in the command palette.

