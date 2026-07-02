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
- **AI-Red fog-of-war parity.** `session/redai.py`'s `RedDoctrine` currently reads
  `self.mgr.world` (ground truth) directly when choosing doctrine-flavored orders — e.g. it can
  target an unpatched cyber vulnerability on a Blue asset it would not actually have detected
  through Red's own fog-of-war-filtered `CellView`. Per `docs/architecture/adr/ADR-0024`, this is
  a tracked gap, not yet resolved: AI-Red should eventually read through a `CellView` like a
  human Red operator. No code change scheduled yet.

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

## 12. Research corpus expansion — 10× roadmap (planned, not yet authorized)

The research corpus at `docs/research/` is the documented basis for every realism claim in
the simulator — every Pₖ tier in `engine/engage.py:INTERCEPTORS`, every modulation
effectiveness in `engine/jam.py:MODULATIONS`, every cyber vector base-success in
`engine/cyber.py:VECTORS`, every doctrine profile branch in `session/redai.py`, every COA in
`docs/vignettes/`. The corpus is what makes the simulator a PME tool rather than a stylized
game. This section is the long-form plan for a 10× expansion — what 10× means concretely
(§12.1, §12.2), the five orthogonal levers that compose to a 10× multiplier (§12.3), the six
content tracks and ~18 new files needed (§12.4), and tier-by-tier concrete literature-review
and analysis tasks (§12.5). It is the long version of the short plan that used to live at
`docs/research/EXPANSION-PLAN.md` (now folded in here as the single source of truth).

**Status: planned. Not yet authorized.** The reviewer's sign-off list lives at §12.8.

### 12.1 Why this matters now — project context for the expansion

The simulator has matured rapidly over the last six months. The June 2026 audit pass
(`docs/AUDIT-2026-06.md`) reviewed every layer of the project for completeness, accuracy,
and quality and produced concrete remediation across research, documentation, tests, and
code. The follow-on commands audit (`docs/AUDIT-2026-06-COMMANDS.md`) replaced the
`success_prob` operator override with derived probabilities, introduced the four-class
`INTERCEPTORS` database (`bmd_adapted` / `mrbm_kkv` / `abm_heavy` / `coorbital`) sourced from
the open-source DA-ASAT test record (SC-19, Burnt Frost, Mission Shakti, Nudol), and cut 14
Dead/Cosmetic verbs while adding three realism verbs (`mw.add_stare_area`,
`satcom.geolocate_interference`, `wx.request_sector`). The TT&C audit
(`docs/AUDIT-2026-06-UI-TTC.md`) discovered that the vignette power rates drove a ~63%
depth-of-discharge sawtooth every orbit and recalibrated them to a realistic ~21% DoD. Each
of those changes rests on assertions about how real systems actually work — and yet the
`docs/research/` corpus that should *be* that body of evidence carries **zero cited URLs**
across its 1,152 lines (verified by `grep -c http docs/research/*.md`).

The audit-driven realism work *did* find and use citations — the agent reports that
produced the INTERCEPTORS database cited SWF Global Counterspace 2025, CSIS Space Threat
Assessment 2025, NASA HUSIR/Goldstone Cosmos-1408 debris observations, the IISS Nudol
analysis, CRS RS22652, and several primary-source ASAT test records. Those citations were
folded into engine code comments and into the audit docs, but **not** back into the research
corpus. So we have an unusual mismatch: the engine's numbers are well-sourced (cite an
inline file:line in the relevant `engine/*.py` module and you can trace to the source), but
the research files that should be the canonical source-of-truth still read as one
single-session knowledge dump. This roadmap fixes that asymmetry while also expanding the
corpus to cover the topics the project has grown into needing.

A PME tool earns its credibility by being defensible in front of subject-matter experts:
USSF Guardians, NRO historians, USSPACECOM JAGs, doctrine analysts at CSIS / SWF / IISS,
operator alumni from NSpOC / 2 SOPS / 18 SDS / 53 SOPS. Every claim about Russian EW
doctrine, every named PLA SSF capability, every interceptor's altitude reach, every
debris-persistence regime, every legal interpretation of OST Article IV — must be
traceable to an open-source primary or near-primary citation, ideally with both a live URL
and a Wayback snapshot. We are not there. This roadmap is the path to getting there.

A second dimension matters: the simulator's *breadth* has outgrown the research's breadth.
We now have 19 vignettes spanning four pedagogical tracks (canonical / mission-set / Red
COA / learning), `engine/sigint.py` and `engine/cyber.py` and `engine/engage.py` per-domain
databases that have no corresponding deep-dive research file, the SSN model
(`engine/ssn.py`) with no corresponding research on real SSN tasking practice, and a
growing FUTURE-WORK list of v1.1+ engine work (GNSS spoof distinct from jam, coalition SDA
catalog, mega-constellation resilience, frequency-hop ECCM) that lacks research
underpinning. The corpus needs new tracks (commercial proliferation, emerging tech,
incident-record catalog) and many new files. The 7-file / 1,152-line baseline is simply
not enough corpus for the simulator it has become.

### 12.2 Baseline accounting — what we are 10×-ing

The current corpus, audited file-by-file:

- `01-doctrine-western.md` (144 lines, 0 URLs) — USAF / USSF doctrine summary; covers
  Spacepower, AFDP 3-14, the three counterspace mission areas, allied doctrine. Solid
  primer but no citations.
- `02-doctrine-non-western.md` (129 lines, 0 URLs) — China + Russia at ~50 lines each;
  named PLA and VKS capabilities listed without sources; no India / Iran / DPRK /
  France / UK / Israel / Japan coverage.
- `03-counterspace-taxonomy.md` (165 lines, 0 URLs) — the five D's taxonomy, mapped to
  engine `Outcome` literals. Per-effect descriptions of DA-ASAT, co-orbital, EW, DE,
  cyber. Out-of-scope-for-v1 note on nuclear/EMP.
- `04-orbital-mechanics-primer.md` (145 lines, 0 URLs) — regime physics, access windows,
  the moderate-fidelity model, what operators see. Tight; could grow per-fidelity-tier
  validation discussion.
- `05-mission-types-and-counters.md` (132 lines, 0 URLs) — nine mission types in ~10–15
  lines each. The realism research called this "in better shape than its piecemeal
  history suggests" but it needs depth, especially on the commercial-tasking APIs that
  the realism research used (Maxar, Planet, Capella).
- `06-bus-and-payload-operations.md` (270 lines, 0 URLs) — the longest file; covers
  bus subsystems, SOH, payload ops per type, operator interfaces. Eutelsat Quantum
  citation was added in the June 2026 audit but as a comment line, not a hyperlinked
  source.
- `07-legal-norms-and-roe.md` (151 lines, 0 URLs) — OST, LOAC in space, the 2022
  destructive-DA-ASAT test moratorium, ROE design pattern. Cleanest file structurally;
  needs treaty-text hyperlinks and UNGA resolution citations.

Total: **1,152 lines, 0 URLs**, 7 topic files plus an INDEX. Roughly 30 named systems
without inline cites; roughly 50 numeric claims (altitudes, ranges, dates, counts)
without inline cites. The Sources subsections at the foot of each file *do* name source
families (CSIS, SWF, AU Space Primer, etc.) but as text not links.

The 10× target is precise:

| Metric | Today | 10× target | Delta |
|---|---:|---:|---:|
| Files | 7 + INDEX | 25 + INDEX + this roadmap | +18 |
| Total lines | 1,152 | ~11,500 | ~10×, +10,350 |
| Cited URLs | 0 | ≥500 | from zero |
| Primary sources named | ~30 (text only) | ≥250 (hyperlinked + dated) | ~8× |
| Mission types with deep-dive | 9 at ≤30 lines | ≥15 at ≥200 lines | depth + breadth |
| Adversary actors at deep-dive | 2 (CN, RU) at ~50 lines | 9 at ≥150 lines | breadth |
| Per-engine-module cross-refs | 13 references *to* research from code | ≥80 bidirectional refs | ~6× |
| Date-stamped facts | 0 with explicit dates | every numeric claim dated | from zero |
| Annual-review markers | none | every file carries `last_reviewed:` | from zero |

The "tenfold" is therefore not "one file ten times longer." It is the product of five
orthogonal expansions (§12.3): depth ~1.5×, breadth ~2×, citation density ~2× (a
multiplicative effect from zero to dense), bidirectional cross-linking ~1.5×, currency
maintenance ~1× (constant but newly enabled). 1.5 × 2 × 2 × 1.5 × 1 ≈ 9×, plus a Tier 4
forward-looking track gets to a defensible 10×.

### 12.3 The five expansion levers

#### 12.3.1 Lever 1 — Depth (1.5×)

Depth means going from a primer paragraph on a system to a paragraph plus a sub-section
that an operator or doctrine analyst would recognize as substantive. Today's
`03-counterspace-taxonomy.md` §1 covers DA-ASAT in about a dozen lines, naming SC-19 /
Nudol / SM-3 / PDV without elaborating on their respective programs, test histories, or
the geopolitical context that surrounded each test. A depth expansion would discuss the
SC-19 program's evolution from a midcourse-defense interceptor into a counterspace
weapon; the political signaling of the 2007 FY-1C test (and the resulting ~3,000+
tracked-fragment debris event that remains in orbit); the 2008 Burnt Frost / USA-193
context (a satellite reentry safety pretext used to demonstrate latent capability); the
2019 Mission Shakti test as deliberately calibrated to minimize persistent debris
(283 km altitude → months-to-years decay); and the 2021 Nudol / Cosmos 1408 test that
produced 1,789 tracked fragments at 480 km and triggered the 2022 destructive-test
moratorium that `07-legal-norms-and-roe.md` discusses. Each of those expansions feeds the
engine's `INTERCEPTORS` Pₖ table (`engine/engage.py`) and the
`debris_cone_estimate(persistence)` regime (the audit-introduced field), which is the
cross-link that closes Lever 4 (§12.3.4).

Depth applies similarly across the corpus. `06-bus-and-payload-operations.md` should
grow per-bus-class (Lockheed A2100, Boeing 702, Airbus E3000, SSL/Maxar 1300, modern
software-defined platforms) with named power-system architectures, the moments-of-inertia
ranges that drive desaturation cadence, and the typical battery DoD targets that justify
the audit's recalibration (the realistic 15-25% DoD range that the audit cited but did
not yet add to research). `04-orbital-mechanics-primer.md` should add a per-fidelity-tier
validation discussion: the Kepler+J2 errors against SGP4 catalogs, SGP4's known accuracy
envelope (typically km-class at 1 day, growing nonlinearly), and the published
high-precision orbit determination performance against TLE. Depth, in short, is each
existing topic file extended with the per-system, per-program, per-incident specificity
that a doctrinal SME would actually recognize.

Depth's 1.5× contribution to the 10× target is conservative. The reason it is not larger
is that not every existing file needs to grow uniformly; `07-legal-norms-and-roe.md` is
already nearly the right depth and primarily needs treaty-text hyperlinks (Lever 3, not
Lever 1). The depth growth is concentrated in the doctrine, taxonomy, and
operations files where the current treatment reads as a survey.

#### 12.3.2 Lever 2 — Breadth (2×)

Breadth means adding files that cover topics the current corpus does not address at all.
The most glaring gap is per-actor coverage outside CN/RU: India's DRDO and Mission Shakti
program, Iran's Islamic Revolutionary Guard Corps Aerospace Branch (with documented
GPS-jamming and SATCOM-jamming campaigns over the Strait of Hormuz), North Korea's NADA
and its observed cyber operations against satellite ground infrastructure, allied actors
like France's CSO program and the dedicated *Commandement de l'Espace*, Israel's Ofeq
program and the Yahalom unit's SIGINT work, Japan's space situational awareness mission
under the JASDF. Each of those actors is a credible Red doctrine profile or a coalition
Blue partner in `session/redai.py` and the COA vignettes, and the simulator's
`coa-misc-iran-ml` vignette already implies an Iran-shaped Red without the corresponding
research depth.

A second breadth axis: counterspace systems by class. `03-counterspace-taxonomy.md` is a
single file covering five effect categories; a per-class deep-dive would split into
DA-ASAT systems, co-orbital and RPO systems, EW systems, directed-energy systems, and
cyber systems. Each per-class file would name specific systems (Tirada-2 SATCOM jam,
Pole-21 GNSS jam, Bylina C2, Tobol SDA jammer, Krasukha-4 radar EW for the EW file; SJ-21
/ SJ-15 GEO tug, Burevestnik co-orbital, Olymp-K / Luch-2 GEO observers, USA-270 series
for the co-orbital file), trace each to public statements / sanctions records /
think-tank assessments, and discuss the engagement parameters the engine uses for each.
This breadth axis is where the realism research's already-paid effort yields the most
value — that research already produced per-system citations; folding them into per-class
files makes them findable.

A third breadth axis: cross-cutting topics with no current file. Commercial space
proliferation (Starlink V2, Kuiper, OneWeb) changes the threat calculus by adding
thousands of hardened-by-numbers targets and a non-state actor (SpaceX) into the
strategic mix; allied SDA fusion (Five Eyes SST, the UCSD Vandenberg pipeline) changes
the custody picture; the operational ground segment (AFSCN, NASA Space Network, AWS
Ground Station booking economics) is the un-sexy infrastructure where most real attacks
land. None of those have a research file. The proposed taxonomy (§12.4) adds files for
each. Breadth's 2× contribution is the largest single lever and the easiest to author —
greenfield writing per topic is faster than reworking existing files.

#### 12.3.3 Lever 3 — Citation density (~2×, effectively ∞× from zero)

Citation density is the difference between "Russia leads with electronic warfare" as a
sentence and the same sentence with a hyperlink to the SWF 2025 Global Counterspace
Capabilities Report's Russia chapter, a hyperlink to the CSIS Space Threat Assessment
2025's EW section, and an inline date-stamped paragraph mentioning Tirada-2's first
documented operational use. The corpus today has none of that. Adding ~500 hyperlinked
citations across ~11,500 lines is a citation roughly every ~23 lines, which is the right
density for a PME / doctrine reference: dense enough to be defensible, not so dense it
reads like a bibliography.

Citation density also means citation *integrity*: every external URL gets a Wayback
Machine snapshot beside it (URL rot is real — the SWF reports have moved several times,
the CSIS reports occasionally 404, and government publication portals reorganize), and
every citation carries the date of access. This is the methodology that the
`10-sources-and-methodology.md` deliverable (Tier 1 first output) will codify. A
secondary citation-density move is to use *primary* sources where they exist — for
treaty law, link the UN treaty text directly; for the 2022 moratorium, link the State
Department announcement and the UNGA resolution that followed; for ASAT test records,
link the contemporaneous CelesTrak / 18SDS catalog entries and the Jonathan McDowell
log; for doctrine claims, link the actual doctrinal publication (AFDP 3-14, Joint Pub
3-14, etc.) rather than think-tank summaries of it.

The 2× contribution looks conservative against an "∞× from zero" reality. The reason
it's bounded at 2× is that depth and breadth are doing most of the line-count work; the
citation density is a *quality* multiplier on those lines. A 11,500-line corpus with 500
citations is dramatically more credible than the same 11,500 lines with zero — but the
*lines* themselves come from depth and breadth, not from the citations.

#### 12.3.4 Lever 4 — Cross-linking with code (1.5×)

The audit-driven realism work created an asymmetry: engine modules know which research
they cite (the agent reports left footprints in module docstrings — for instance
`engine/engage.py:INTERCEPTORS` mentions "the four open-source DA-ASAT test records"),
but the research files do not know which engine code they justify. Closing that loop is
Lever 4: every engine module that hard-codes numbers gets a single docstring line
pointing at the research section that sources those numbers, and every research section
that justifies engine parameters gets a single line back pointing at the code. This is
not just a citation-style nicety; it is the mechanism that lets a future audit catch
"the research says X but the code does Y" drift before it ships, and lets a PME
instructor explaining a vignette outcome point at "this Pₖ comes from this database
which comes from this research section which cites this 2007 NASA report on the FY-1C
debris event."

The bidirectional cross-link convention will be:

- Research file: a `Used by:` line at the bottom of every section that names the engine
  module(s) and the database/constant(s) it sources. Example: in
  `03a-da-asat-systems.md` under "SC-19 / FY-1C 2007", a `Used by:
  engine/engage.py:INTERCEPTORS["mrbm_kkv"], engine/engage.py:debris_cone_estimate`
  closing line.
- Engine module: a single `# Source: docs/research/<file>#<anchor>` comment beside the
  hard-coded value. Example, on the `mrbm_kkv` line in `engine/engage.py:INTERCEPTORS`,
  a comment naming the research file.

This convention is the single most enduring artifact of the expansion. Code reviewers
checking a future PR that changes `INTERCEPTORS["mrbm_kkv"]["base_pk"]` from 0.70 to
0.85 will be able to follow the comment to the research file and verify that the
research still supports the change. Conversely, a future expansion of the SC-19 research
section will be able to find the engine code that depends on its claims and propose
matched updates. The 1.5× contribution to the 10× target reflects that this work is a
small line-count delta but a large credibility delta.

#### 12.3.5 Lever 5 — Currency and refresh cadence (1×, ongoing)

The fifth lever does not directly multiply line count or citation count; it preserves
the multiplier the other four levers create. A 11,500-line corpus with 500 citations is
worthless 36 months after authoring if the doctrine references are stale, half the URLs
404, and named systems have been replaced. The methodology file
(`10-sources-and-methodology.md`) will mandate per-file `last_reviewed: YYYY-MM-DD`
frontmatter and an annual review workflow. Files older than 12 months get a "stale"
banner at the top until they pass a review pass; a `/loop` invocation (see the
keybindings / loop skill) can be set to flag stale files monthly.

The 1× contribution to the 10× math is the discipline that *prevents* the corpus from
silently halving its value over time. It is also the lever that protects the
cross-linking from rotting: if a research section is updated, the bidirectional links
let the maintainer know which engine modules to re-verify. Currency is the closest thing
the corpus has to a unit-test suite.

### 12.4 The six content tracks

The 25 target files organize into six thematic tracks. Each track gets its own subsection
here; the per-file deep dive lives in the per-tier task list at §12.5.

#### 12.4.1 Track A — Doctrine (5 files; was 2)

Doctrine is the *why* behind every Red and Blue action. The current corpus has two
doctrine files — Western (`01`) and a single non-Western file lumping China and Russia
together (`02`). The track expands to five files: the two existing files get depth
expansion (Lever 1) for the actors they already cover, and three new files split out
deep-dives:

- `02a-china-deep-dive.md` — the PLA SSF→ASF transition (the April 2024 PLA reorganization
  that dissolved the SSF and created the Aerospace Force, the Cyberspace Force, and the
  Information Support Force), Strategic Support Force history, integrated SoS
  ("System-of-Systems") doctrine, the 36th Test Base and its role in DA-ASAT
  development, the Network Information Coordination System concept.
- `02b-russia-deep-dive.md` — VKS (Aerospace Forces) organization, RVSN (Strategic Rocket
  Forces) overlap with counterspace, Roscosmos military integration, the EW Troops
  (РЭБ войска) and their named systems (Bylina, Tirada-2, Pole-21), Tobol's role as a
  dual-use SDA jammer, and the post-2022 doctrinal shift toward "destructive but
  deniable" counterspace under sanctions.
- `02c-emerging-actors.md` — India (DRDO and Mission Shakti, the conscious
  debris-minimization design choice), Iran (IRGC ASB observed jamming over the Gulf,
  the recent space-launch normalization), DPRK (NADA, observed cyber operations against
  satellite ground infrastructure), Israel (Ofeq program, Yahalom SIGINT unit), and
  rising commercial counterspace actors (the "renegade SpaceX" scenario that several
  doctrine analysts have begun discussing).

The two existing files get depth expansion to cover named systems, organizational
charts, and the strategic logic that drives each actor's counterspace posture. The track
expansion supports the simulator's COA library and `session/redai.py` doctrine profiles
directly: every existing or planned Red doctrine profile traces to a file in this track,
and the track gives the COA author the substrate to write doctrinally-coherent vignettes
without re-researching from scratch. This is the single biggest leverage point for
expanding the vignette library beyond the existing 19.

#### 12.4.2 Track B — Counterspace effects and systems (7 files; was 1)

Track B is the largest expansion, splitting today's single
`03-counterspace-taxonomy.md` (the five D's) into seven files:

- `03-counterspace-taxonomy.md` (expanded, ~3×) — the spine: the five D's, mapped to
  engine `Outcome` literals, cross-linked to per-system files below. The single file
  any user opens first to navigate the track.
- `03a-da-asat-systems.md` (new) — per-system: SC-19/DN-3 (CN), Nudol/A-235 (RU),
  SM-3 (US BMD-adapted), PDV-Mk2 (IN), with per-system altitude reach, salvo
  configuration, seeker type, and test history. Sources the engine's
  `INTERCEPTORS` database directly.
- `03b-coorbital-rpo.md` (new) — per-system: SJ-21/SJ-15 (CN tug behavior, the 2022
  Beidou-G2 relocation episode), Burevestnik (RU), Olymp-K and Luch-2 (RU GEO
  observers), the USA-270 series, GSSAP RPO operations, MEV-1 / MEV-2 commercial
  servicing precedents. Sources `engine/engage.py`'s `coorbital` interceptor class.
- `03c-ew-jamming.md` (new) — the realism research already drafted much of this:
  CCS Block 10.2 (the only acknowledged US offensive counterspace system),
  Tirada-2/Pole-21/Bylina, Tobol, AEHF/Milstar ECCM design, processing-gain
  fundamentals, J/S analysis. Sources `engine/jam.py:MODULATIONS` and the
  defender-modifier multipliers introduced by the audit (`_FREQ_HOP_RESIDUAL`,
  `interference_mitigation`).
- `03d-directed-energy.md` (new) — Soviet/Russian Sokol-Eshelon laser dazzle program,
  Peresvet, reported Chinese Zimu-1 program, optical hardening (MgF₂ coatings),
  shutter / safe-payload defensive verbs. Anchors the engine's directed-energy
  outcome category and the proposed `isr.shutter_sensor` verb from the audit follow-ups.
- `03e-cyber.md` (new) — Viasat KA-SAT (the canonical case): full incident reconstruction
  from primary Viasat statements, SPARTA TTPs, the AcidRain wiper analysis from
  SentinelOne, the EU/UK/US attribution timeline. Plus other historical incidents
  (ROSAT 1998, NASA TDRS attacks, supply-chain compromises). Sources
  `engine/cyber.py:VECTORS` and the `seize_c2` payload introduced by the audit.
- `03f-nuclear-emp.md` (new) — Starfish Prime 1962, the Soviet K-3/4/5 high-altitude
  tests, modern EMP modeling literature, OST Article IV's nuclear-weapon prohibition
  in orbit. Deferred for v1 per `03-counterspace-taxonomy.md` but documented here
  for v2 (and for the 2024 Russian-FOBS / nuclear-counterspace discussion that the
  doctrinal community is actively debating).

Track B's value to the engine is direct: each per-system file is the citation source for
a specific engine database or numeric constant. The cross-linking convention (Lever 4)
makes that explicit.

#### 12.4.3 Track C — Orbital mechanics and physics (3 files; was 1)

Track C exists to back the simulator's "moderate fidelity" claim and to give the
fidelity ladder a defensible foundation. The existing `04-orbital-mechanics-primer.md`
gets depth expansion, and two new files split out specialty topics:

- `04-orbital-mechanics-primer.md` (expanded) — regimes, access windows, the fidelity
  ladder, what the operator sees. Adds inline cites on every Keplerian-element claim,
  on the J2 secular precession rates, on the SGP4 / TEME convention, and on the GMST
  rotation accuracy.
- `04a-propagator-fidelity.md` (new) — the propagator validation discussion the
  simulator has informally claimed but never documented: Kepler+J2 vs SGP4 vs
  high-precision (numeric integration with full perturbation set). Validation against
  the Skyfield reference test that the codebase already runs, against published SGP4
  accuracy assessments, and against the published high-precision OD performance against
  TLE. Names the simulator's chosen tier and its known errors, so a future high-fidelity
  PR has a documented baseline to beat.
- `04b-debris-and-conjunction.md` (new) — NASA ORDEM 3.x model overview, ESA MASTER
  comparison, Cosmos 1408 debris evolution analyses (NASA HUSIR/Goldstone observations,
  CelesTrak catalog growth), Burnt Frost reentry timeline (247 km → all reentered
  within months) vs FY-1C persistence (865 km debris still in catalog in 2026 — the
  decadal persistence the audit cited). Sources the engine's
  `debris_cone_estimate(persistence)` regime that the audit introduced. Critical
  reference for any future `prop.collision_avoid` work and for the FUTURE-WORK
  conjunction-screening primitive.

Track C's 3-file size is small but the credibility return is high. The simulator's
"moderate fidelity" claim is the most-quoted claim in the build spec; backing it with a
validation discussion is overdue.

#### 12.4.4 Track D — Mission sets (4 files; was 1)

Track D pulls the per-mission depth out of today's single
`05-mission-types-and-counters.md` and into per-mission deep-dives:

- `05-mission-types-and-counters.md` (kept, scoped down) — the summary index that
  navigates to the per-mission files. Keeps the "Effect × Mission-type matrix" table
  that closes the file today; that table is heavily cited in the commands audit.
- `05a-isr-eo-sar.md` (new) — Maxar/Planet/Capella commercial tasking APIs (already
  the citation backbone of the audit's realism research), NRO program history (KH-1
  through KH-13 publicly-released material, the NRO open-source historical archive),
  NIIRS scoring, sun-synchronous orbit geometry, NRO/NGA TPED (Tasking, Processing,
  Exploitation, Dissemination) workflow. Critical for the `isr_eo` / `isr_sar` payload
  types and the engine's `BEAM_MODES` database.
- `05b-satcom-pnt.md` (new) — WGS/MUOS/AEHF on the SATCOM side (with citations to
  53 SOPS / 4 SOPS public material and the WGS MAJE upgrade docs that the audit's new
  `satcom.geolocate_interference` verb depends on), Iridium and the commercial side,
  GPS Block IIIF flex power (IS-GPS-200E and the GAO M-code report that the audit's
  new `pnt.flex_power` verb depends on), Galileo PRS, GLONASS, BeiDou. Sources the
  `pnt` payload type and the audit's new PNT verbs.
- `05c-sigint-mw-wx-sda.md` (new) — NRO SIGINT historical material (Trumpet / Mercury /
  Mentor public material), SBIRS scanner+starer ops and the audit's `mw.add_stare_area`
  verb (sourced from 2 SWS / Buckley public material), GOES-R MDS request flow
  (NOAA OSPO process docs, sources the audit's `wx.request_sector` verb), 18/19 SDS
  SSN tasking. A four-mission-in-one file kept tight by the per-mission summaries
  living in `05`.

Track D's value to PME instruction is that a SATCOM-focused exercise has *one* document
to assign the trainees; the same for ISR-focused exercises or SDA-focused exercises.

#### 12.4.5 Track E — Operations, legal, history (4 files; was 2)

Track E expands the operations-and-context layer:

- `06-bus-and-payload-operations.md` (expanded) — the existing 270-line "how operators
  actually fly satellites" deep-dive, expanded with operator console references
  (SCOS-2000, L3Harris InControl, Aerospace TOR-2013-00293, RTI DDS in modern ground
  systems), per-bus-class architectures, and per-payload-class detailed ops flows.
- `06a-ground-segment.md` (new) — AFSCN architecture and history, NASA Space Network
  / TDRSS, AWS Ground Station booking model (already cited in the audit), commercial
  GS providers (KSAT, ATLAS, Viasat-RTE), GS site selection rationale (the polar
  high-cadence requirement, the equatorial low-elevation requirement), and the
  ground-segment-as-attack-surface theme (Viasat KA-SAT, the LinkedIn-published
  insider compromise of NASA TDRS, the Bell-Hardware-Fault SOPS incidents). Cross-
  references heavily into Track B (`03e-cyber.md`).
- `07-legal-norms-and-roe.md` (expanded) — OST treaty text inline-linked, LOAC
  in-space scholarship (Schmitt's *Tallinn Manual* references for cyber, the
  *Woomera Manual* and *MILAMOS Manual* drafts), the 2022 destructive-DA-ASAT
  moratorium full text and the UNGA Resolution 77/41 that followed, UNGA OEWG /
  GGE on PAROS state.
- `07a-incident-record.md` (new) — the PME instructor's reference shelf: a catalog of
  named on-orbit and counterspace incidents, each entry containing date, attribution
  status (confirmed / suspected / disputed), summary, primary-source citation, and
  the engine-relevant lesson. Entries: FY-1C 2007, Burnt Frost 2008, Mission Shakti
  2019, Nudol 2021, Viasat KA-SAT 2022, the Iran-vs-Eutelsat 2009 satellite jamming
  campaign, the SJ-21 / Beidou-G2 relocation, USA-193 deorbit context, the GPS
  Selective Availability era for historical PNT context. This file is what a
  facilitator hands to a Red team to seed their planning.

#### 12.4.6 Track F — Cross-cutting and forward-looking (3 files; was 0)

Track F is greenfield content that the project has grown into needing:

- `08-commercial-and-allied.md` (new) — commercial proliferation (Starlink V2,
  Kuiper, OneWeb), how thousands of small hardened-by-numbers targets change the
  targeting calculus; the allied SDA fusion picture (Five Eyes SST, the UCSD
  Vandenberg pipeline, France's CSO partnership, Japan's SDA contribution); the
  emerging "non-state actor" question (SpaceX as a wartime decision-maker —
  Starlink Ukraine).
- `09-emerging-tech.md` (new) — optical ISLs (Starlink Gen 2, Kuiper, USSF Tranche 1),
  software-defined payloads (Eutelsat Quantum, the audit-cited test of in-orbit
  reconfigurability), on-orbit refueling (Northrop MEV, the upcoming SPRINT-class
  RPO programs), manufactured-in-space concepts. Sources for the v1.1 and v2
  engine work tracked elsewhere in this `FUTURE-WORK.md`.
- `10-sources-and-methodology.md` (new) — the canonical source list with hyperlinks
  and access dates: SWF Global Counterspace Capabilities (annual), CSIS Space Threat
  Assessment (annual), AU Space Primer (chapter list), NRO openly-released history,
  Jonathan McDowell's *Space Reports*, CelesTrak / 18 SDS catalog, treaty repositories
  (UN OOSA, ICRC for LOAC). The methodology file is *Tier 1's first deliverable*
  because it sets the citation convention that every later file follows.

### 12.5 Four tiers — concrete lit-review and analysis tasks

The four tiers prioritize Tier 1 (citation backfill of existing files + methodology) as
required to make today's corpus defensible, then build outward. Each tier subsection
below lists per-file concrete literature-review tasks and concrete analysis tasks.
Literature-review tasks name the specific source families to consult; analysis tasks name
the specific engine code, vignettes, or audit findings the file must reconcile with.

#### 12.5.0 Authoring cadence — one subsection per `deep-research` invocation

The June 2026 Tier 1 Sprint 1 attempt (commit `b39c24f`) revealed the load-bearing
constraint on this expansion: the `deep-research` skill fans out aggressively per
invocation, and a single "rewrite this whole file" brief blew the subagent token
budget in three of four attempted file-level invocations (only `03-counterspace-
taxonomy.md` landed; `04-orbital-mechanics-primer.md`, `05-mission-types-and-counters.md`,
and `06-bus-and-payload-operations.md` hit limits before producing usable content).

The fix — adopted as the binding cadence for the rest of the expansion — is to invoke
`deep-research` **one subsection at a time**. Per-file work decomposes into a sequence
of small, checkpointed steps:

1. **Decompose the target file into subsections.** Use the
   `03-counterspace-taxonomy.md` exemplar as the structural model: a file typically
   carries an intro + 6–10 numbered `##` sections + a cross-references closer. Each
   `##` section is a discrete authoring unit.
2. **Per subsection:** invoke a single `deep-research` agent with a tight brief covering
   only that subsection's lit-review tasks (named source families to consult, specific
   claims that need inline citations, named systems that need date-stamping) and that
   subsection's analysis tasks (which engine module the section sources, which
   `Used by:` cross-link line to close with). Budget ≤ 20k subagent tokens per
   invocation — small enough that the fan-out has no room to runaway.
3. **Document findings immediately.** The agent returns the subsection's markdown.
   Append it to the file under construction (or to a per-file
   `working/<file-id>/<section-id>.md` if the file isn't yet ready to assemble),
   commit the increment with a one-line message
   (`docs(research): <file>#<section> — <one-line summary>`), push.
4. **Move to the next subsection.** No batching: each subsection lands and pushes
   before the next is scoped.
5. **Final integration pass.** When all subsections of a file have landed, run a
   single integration pass (no agent — done in the main session) that:
   regenerates `### Sources` at the foot of each `##` section from the inline cites,
   verifies cross-section consistency (every `Used by:` line names a real engine
   module; every forward-reference to another file exists), and runs the per-file
   quality-bar checklist from §12.6. Commit the integration pass as
   `docs(research): <file> — integration pass`.
6. **Verification pass per tier.** Once all files in a tier have landed, spawn one
   adversarial verification agent that picks a random sample of 20 cited claims across
   the tier's files and re-checks them against the cited sources (per the methodology
   file's §5.3). Findings go into `docs/research/REVIEW-LOG.md`. Any `✗ unsupported`
   finding is a blocker for tier merge.

The advantage of this cadence is that each invocation has bounded scope (one
subsection's worth of claims, typically 5–10 inline citations), bounded token cost
(≤20k subagent tokens), and a small blast radius if it fails (one subsection's worth
of work, ~60 lines, not a whole file). Progress is fully checkpointed in git: a
mid-file failure leaves landed subsections committed and the next subsection still
queued, and any reviewer can read the file as it stands at any commit. The trade-off
is more total agent invocations per file (~6–10 instead of 1) but each is small.

**Why the methodology file did not need this cadence.** `10-sources-and-methodology.md`
was the first Tier 1 deliverable and was authored directly in the main session
(commit `968c4be`) without `deep-research` because it defines convention rather than
synthesizing external claims; it carries zero external citations by design (§9 of
that file).

**Why `03-counterspace-taxonomy.md` did not need this cadence either.** The
`03-counterspace-taxonomy.md` agent completed before hitting limits (the one wave-1
success); its 821-line / 147-URL output is the structural exemplar every later file
follows. The per-subsection cadence is for the files that *come after*.

**The per-subsection brief template.** When invoking `deep-research` for a single
subsection, the brief should fill in this skeleton:

```
You are writing ONE subsection of <docs/research/FILE.md> — the §N "<TITLE>"
subsection. Read docs/research/10-sources-and-methodology.md for the citation
convention and docs/research/03-counterspace-taxonomy.md as the structural exemplar.

DO NOT MODIFY EXISTING FILES. Produce the markdown for this subsection only.

Subsection scope (~50–120 lines): <one-paragraph scope statement>.

Required claims to cite (each inline-linked at the claim site, with Wayback snapshot):
  - <claim 1>: cite <source family>
  - <claim 2>: cite <source family>
  - ...

Engine cross-links (close with a `Used by:` line):
  - <engine module>: <constant or function this subsection sources>

Quality bar: every numerical claim cited; every named system date-stamped at first
mention; per-section ### Sources subsection at the foot; no Wikipedia-only citations.

Output: markdown ready to append to FILE.md under §N. Target ≤120 lines.
```

The brief is intentionally small so the agent does not have room to fan out
unproductively. The remainder of §12.5.1–12.5.4 lists the per-file subsections each
file will be decomposed into; the per-subsection brief is filled in at execution time
from those lists.

#### 12.5.1 Tier 1 — Citation backfill + methodology (highest priority)

Tier 1 covers nine files: the eight existing files of the corpus (citation backfill +
modest depth expansion) plus the new `10-sources-and-methodology.md` as the first
deliverable.

**File 1.0 — `10-sources-and-methodology.md` (NEW, FIRST DELIVERABLE).**
- Lit-review tasks: (a) compile the canonical source list — SWF Global Counterspace
  Capabilities Report (annual, current edition is 2025), CSIS Space Threat Assessment
  (annual, 2025), Secure World Foundation publications archive, Air University Space
  Primer (current edition), NRO Center for the Study of National Reconnaissance public
  releases, Jonathan McDowell's *Space Reports* and personal log, CelesTrak orbital
  catalog snapshots, 18/19 SDS public space catalog, UN Office for Outer Space Affairs
  treaty repository, the ICRC LOAC databases. (b) Test each URL against the current
  state of the web; record any 404s or moves. (c) Add a Wayback Machine snapshot URL
  beside every live URL. Analysis tasks: (a) define the citation-style convention (inline
  hyperlinks at the claim site, plus a per-section `Sources` subsection — the convention
  used by Wikipedia's higher-quality articles); (b) define the `last_reviewed:`
  frontmatter convention and the stale-banner threshold (12 months); (c) define the
  source-quality tiers (peer-reviewed > government/think-tank > journalism > advocacy);
  (d) define the cross-linking convention from §12.3.4. Output: ~400 lines.

**File 1.1 — `01-doctrine-western.md` (existing, ~3× expansion).** Lit-review tasks:
(a) cite USSF Spacepower (Capstone) doctrine; (b) cite AFDP 3-14 Space Operations
publicly-released material; (c) cite Joint Publication 3-14 Space Operations
publicly-released material; (d) cite STARCOM curriculum public material; (e) cite the
2024 SDPP (Space Domain Awareness Policy) where applicable; (f) cite allied doctrine
publicly available (NATO AJP-3.3, AUS Space Power Manual, JP Space Domain Mission Concept,
UK Joint Doctrine Note 1/22). Analysis tasks: (a) reconcile each cited claim with the
engine's `Outcome` mapping in `engine/effects.py`; (b) link each section to the
COA-vignette-pattern it supports; (c) add `Used by:` cross-link lines.

**File 1.2 — `02-doctrine-non-western.md` (existing, ~3× expansion of CN/RU treatment).**
Lit-review tasks: (a) for China, cite CASI (China Aerospace Studies Institute) public
reports, the 2024 PLA reorganization analyses (post-April 2024), Andrew Erickson's
publicly-available PLA Navy/Space work, the SWF China chapter; (b) for Russia, cite the
SWF Russia chapter, the CSIS Russia counterspace assessments, Bart Hendrickx's
Russian-space analyses, the IISS Military Balance Russia chapter. Analysis tasks:
(a) reconcile each named system with the engine's COA library (`coa-russia-ml`,
`coa-russia-md`, `coa-china-ml`, `coa-china-md`); (b) reconcile each named system with
the `russia_ew_first` and `china_integrated` Red doctrine profiles in
`session/redai.py`; (c) add `Used by:` lines.

**File 1.3 — `03-counterspace-taxonomy.md` (existing, ~3× expansion).** Lit-review tasks:
(a) for each of the five D's, cite the canonical doctrinal reference (USAF AFDP 3-14
explicitly defines the five-D scheme); (b) cite the SWF Global Counterspace per-category
overviews; (c) cite the CSIS taxonomy in Space Threat Assessment 2025. Analysis tasks:
(a) reconcile each D with the corresponding `Outcome` literal in `engine/effects.py`
(`deceive`, `disrupt`, `deny`, `degrade`, `destroy`); (b) reconcile each D with the
corresponding category in `engine/effects.py:Category` (`direct_ascent`, `co_orbital`,
`electronic_warfare`, `directed_energy`, `cyber`); (c) write the navigation index
to the per-class files (Track B, Tier 3).

**File 1.4 — `04-orbital-mechanics-primer.md` (existing, ~2× expansion).** Lit-review
tasks: (a) cite the canonical Vallado *Fundamentals of Astrodynamics* sections for
Keplerian elements and J2; (b) cite the original Brouwer-Lyddane mean-element theory
reference for J2 secular rates; (c) cite the SGP4 source paper (Hoots & Roehrich,
1980 and the 2006 Vallado SGP4 revisitation); (d) cite Skyfield's published precision
claims for cross-reference. Analysis tasks: (a) reconcile the cited claims with
`engine/propagator.py`'s implementation seam; (b) document the known accuracy envelope
of the moderate-fidelity tier with reference to the existing Skyfield test in
`spacesim/tests/`; (c) add `Used by:` lines pointing at `propagator.py`, `orbit.py`,
`geometry.py`.

**File 1.5 — `05-mission-types-and-counters.md` (existing, ~1.5× — depth shifts to
per-mission Track D files in Tier 2).** Lit-review tasks: (a) for each of the nine
mission types, cite at least the SWF chapter that names the systems; (b) cite the
per-mission commercial tasking API where applicable (Maxar, Planet, Capella for ISR;
HawkEye 360 for SIGINT; commercial weather providers). Analysis tasks: (a) update the
mission-set × counter matrix with the audit's verb cuts and additions; (b) add
`Used by:` lines pointing at `engine/buscommands.py`'s `_PAYLOAD_TYPES_FOR` map and the
engine's per-domain databases.

**File 1.6 — `06-bus-and-payload-operations.md` (existing, ~2× expansion).** Lit-review
tasks: (a) cite the SCOS-2000 / L3Harris InControl / Aerospace TOR-2013-00293 references
already named at the foot of the file; (b) cite the per-bus-class platform pages
(Lockheed A2100, Boeing 702, Airbus E3000); (c) cite NASA-STD-7009 / ECSS-E-ST-70 for the
operator-procedure perspective; (d) cite the realistic DoD-per-orbit literature that the
TT&C audit (`docs/AUDIT-2026-06-UI-TTC.md`) referenced when recalibrating power rates.
Analysis tasks: (a) reconcile claims with `engine/bus.py` and the recently-calibrated
power rates in every vignette; (b) document the operator-loop-driven structure
(contact → pass-plan → dump → review) that the engine's `bus_tick` / `refresh_ground_view`
implements; (c) add `Used by:` lines.

**File 1.7 — `07-legal-norms-and-roe.md` (existing, ~2× expansion).** Lit-review tasks:
(a) inline-link the OST treaty text from UNOOSA; (b) inline-link the Registration and
Liability Conventions; (c) cite the *Tallinn Manual 2.0* for cyber-in-space LOAC; (d) cite
the *Woomera Manual* and *MILAMOS Manual* drafts where they exist; (e) cite the 2022
US declaration on the DA-ASAT moratorium (State Department release) and UNGA Resolution
77/41 (2022); (f) cite the OEWG (Open-Ended Working Group on PAROS) and the GGE state.
Analysis tasks: (a) reconcile each treaty / norm claim with the engine's ROE flags
(`roe_kinetic_authorized`, `roe_cyber_authorized`); (b) document the
"reversible-effects-first" pattern as a doctrinal choice with sources; (c) add
`Used by:` lines pointing at `session/manager.py`'s ROE handling.

**File 1.8 — `INDEX.md` (existing, regenerated).** Trivial deliverable — re-generate the
index to cover the post-expansion taxonomy. Output: ~50 lines.

Tier 1 total: ~3,500 lines added across nine files, ~250 citations introduced. Tier 1's
completion is the gating event for Tiers 2-4 because it locks the methodology.

##### Tier 1 per-subsection decomposition (the §12.5.0 cadence applied)

Each Tier 1 file is decomposed into the subsections below. Each subsection is a single
`deep-research` invocation per §12.5.0 — the per-subsection brief is built at execution
time from the file-level lit-review list (above) and the subsection scope (below). The
exemplar structure is `03-counterspace-taxonomy.md` (commit `b39c24f`): intro paragraph
+ numbered `##` subsections + a closing `## Cross-references`. Subsection IDs use
`File-N.M.K` notation so commits and the per-section REVIEW-LOG can reference them
unambiguously.

**File 1.1 — `01-doctrine-western.md` (~3× expansion to ~430 lines, ~50 inline cites):**

- §1.1.1 *The core logic: superiority → control → counterspace.* Doctrinal frame from
  USSF Spacepower Capstone (2020) and AFDP 3-14. Inline cite the Capstone definitions
  of "space superiority" and "space control." ~50 lines, ~5 cites. `Used by:`
  `engine/effects.py:Category`, `docs/build-spec/03-architecture-and-data.md`.
- §1.1.2 *The three counterspace mission areas (map to sim effects).* OCS / DCS / SDA
  mapping to `engine/effects.py` outcomes. Inline cite AFDP 3-14 §2 and Joint Pub 3-14
  publicly-released material. ~60 lines, ~6 cites. `Used by:` `engine/effects.py`,
  `content/vignettes/`.
- §1.1.3 *Offensive actions (the Red/Blue offensive menu).* 5-D ordering, reversible-first
  preference, named US offensive systems (CCS Block 10.2 cross-reference). ~70 lines,
  ~8 cites. `Used by:` `engine/orders.py`, the COA library.
- §1.1.4 *Defensive actions (the Red/Blue defensive menu).* Cross-domain protection,
  frequency-hop, hardening, RPO posture. ~60 lines, ~6 cites. `Used by:`
  `engine/buscommands.py` `def.*` verbs, `engine/effects.py:_FREQ_HOP_RESIDUAL`.
- §1.1.5 *Cross-cutting functions the sim must represent.* Custody / weapons-quality
  track / attribution. ~60 lines, ~6 cites. `Used by:` `engine/custody.py`,
  `engine/sigint.py:attribution_score`.
- §1.1.6 *Responsible counterspace & escalation.* Reversibility-first doctrine, 2022
  moratorium framing (cross-link to §1.7 of `07-legal-norms-and-roe.md`). ~50 lines,
  ~6 cites. `Used by:` `engine/effects.py:political_consequence`,
  `engine/effects.py:Outcome="destroy"`.
- §1.1.7 *Allied doctrine.* NATO AJP-3.3, AUS Space Power Manual, UK JDN 1/22, JP Space
  Domain Mission Concept. ~50 lines, ~8 cites. `Used by:` future coalition-SDA work in
  `FUTURE-WORK §9`.
- §1.1.8 *Cross-references.* No new content — anchor links to other research files.
  Done as part of the integration pass, not a `deep-research` invocation.

**File 1.2 — `02-doctrine-non-western.md` (~3× expansion to ~390 lines, ~45 inline
cites). Note: depth on each actor moves to Tier 2 deep-dive files; this file stays at
the spine level.**

- §1.2.1 *PLA — organizational frame (post-April-2024 reorganization).* The PLA SSF→ASF
  / CSF / ISF split. CASI public reports + RAND analyses. ~50 lines, ~8 cites.
  Cross-link to Tier 2's `02a-china-deep-dive.md`. `Used by:` `session/redai.py:china_integrated`.
- §1.2.2 *PLA — strategic logic (space as US enabler, therefore target).* Erickson +
  CASI sourcing. ~40 lines, ~5 cites.
- §1.2.3 *PLA — named capabilities (Red asset templates).* SC-19/DN-3, Shijian series,
  Yaogan SIGINT, GSSAP-equivalents. ~60 lines, ~10 cites. `Used by:`
  `engine/engage.py:INTERCEPTORS["mrbm_kkv"]`, COA vignettes.
- §1.2.4 *VKS — organizational frame.* VKS / VKO / RVSN / Roscosmos military
  integration. SWF Russia chapter. ~40 lines, ~5 cites.
- §1.2.5 *VKS — strategic logic (hedge, offset, disrupt).* Hendrickx + SWF +
  CSIS sourcing. ~40 lines, ~5 cites.
- §1.2.6 *VKS — named capabilities.* Nudol/A-235, Tirada-2, Pole-21, Bylina, Tobol,
  Peresvet, Luch/Olymp-K, Burevestnik/Nivelir. ~80 lines, ~12 cites. `Used by:`
  `engine/engage.py:INTERCEPTORS["abm_heavy"]`, `engine/jam.py:MODULATIONS`,
  `engine/effects.py:Category="directed_energy"`.
- §1.2.7 *What this means for the Red Cell (sim implication).* ML/MD COA pairing rationale.
  ~40 lines, ~3 cites. `Used by:` `content/vignettes/coa-*`, `docs/vignettes/00-LIBRARY-ARCHITECTURE.md`.
- §1.2.8 *Cross-references.* Integration pass.

**File 1.4 — `04-orbital-mechanics-primer.md` (~2× expansion to ~290 lines, ~30 inline
cites). Note: 37 verified URLs already exist from the prior subagent run (preserved in
the agent task transcript referenced from commit `b39c24f`).**

- §1.4.1 *Orbital regimes (sets which actions are even possible).* LEO/MEO/GEO/HEO/
  cislunar. Cite NASA NSSDC + ESA "Types of orbits" + AU Space Primer. ~60 lines, ~6 cites.
  `Used by:` `engine/orbit.py:classify_regime`, `engine/engage.py:INTERCEPTORS["max_alt_km"]`.
- §1.4.2 *The access window — the central game mechanic.* Six access channels.
  Cite CelesTrak TLE format docs, ITU-R P.681, Vallado for geometry. ~70 lines, ~8 cites.
  `Used by:` `engine/access.py` (all six channels), `engine/orders.py`.
- §1.4.3 *Moderate-fidelity propagation model (Kepler+J2 / SGP4 / Skyfield).* Cite Vallado
  *Fundamentals* 4th ed., Brouwer 1959 + Lyddane 1963, Hoots & Roehrich 1980, Vallado
  2006 SGP4 revisitation. ~60 lines, ~8 cites. `Used by:` `engine/propagator.py`,
  `engine/perturbations.py`. Forward-link to Tier 3's `04a-propagator-fidelity.md`.
- §1.4.4 *Time and the timeline (sim-UTC int-microseconds).* Cite IERS Conventions 2010
  TN 36, NIST UTC explainers, USNO leap-second material. ~40 lines, ~5 cites.
  `Used by:` `engine/simtime.py`, `engine/clock.py`.
- §1.4.5 *Eclipse and lighting (penumbra-aware).* Cite Vallado §5.3 cylindrical shadow,
  USNO sidereal time, Curtis OMfES, NASA Landsat SSO geometry. ~40 lines, ~5 cites.
  `Used by:` `engine/sun.py:eclipse_fraction`, `engine/busmodel._sunlit` (audit fix).
- §1.4.6 *What the operator sees (turning physics into UX).* Access ribbon, horizons,
  the +1m/+10m/+1h cadence. No new external cites; cross-link to UI. ~30 lines.
  `Used by:` `ui_web/static/app.js` ribbon + activity timeline.
- §1.4.7 *Cross-references.* Integration pass.

**File 1.5 — `05-mission-types-and-counters.md` (~1.5× expansion to ~210 lines, ~40
inline cites). Note: per-mission depth lives in Tier 2 files — this file stays at index
level.**

- §1.5.1 *How to read this (intro + the row taxonomy).* ~20 lines, ~3 cites.
- §1.5.2 *Per-mission summaries (one paragraph each, ~15 lines × 9 missions = 135
  lines).* Eight `deep-research` invocations, one per mission type (ISR-EO, ISR-SAR,
  SIGINT, GNSS/PNT, SATCOM, MW, weather, SDA, OOS/RPO). Each cites: SWF chapter + one
  primary operator-org source + one commercial-API source where applicable. Each
  closes with an engine-mapping line and forward-link to the Tier 2 deep-dive.
  ~9 invocations × ~15 lines each. `Used by:` `engine/buscommands.py:_PAYLOAD_TYPES_FOR`
  and the per-domain databases (`isr.py`, `sigint.py`, `jam.py`, `cyber.py`,
  `engage.py`).
- §1.5.3 *Ground & link segment targets.* Cross-link to `03e-cyber.md` (Viasat) and
  AWS Ground Station booking material. ~30 lines, ~5 cites.
- §1.5.4 *Effect × mission-type matrix.* The matrix from `03-counterspace-taxonomy.md`
  §2 (reused with attribution to the spine file). ~20 lines.
- §1.5.5 *Cross-references.* Integration pass.

**File 1.6 — `06-bus-and-payload-operations.md` (~2× expansion to ~540 lines, ~70 inline
cites). Note: this file sources the TT&C audit's power-rate recalibration, so the
calibration subsection is the highest-priority single subsection in Tier 1.**

- §1.6.1 *Core bus subsystems (EPS, ADCS, CDH, TCS, comms, propulsion).* Cite Wertz &
  Larson *Space Mission Engineering* 4th ed., NASA-STD-7009, NASA-STD-8729.1A,
  Aerospace TOR-2013-00293, ECSS-E-ST-70-series. ~80 lines, ~10 cites. `Used by:`
  `engine/bus.py` (per-subsystem dataclasses).
- §1.6.2 *State of Health (SOH) and "safe mode."* SCOS-2000 + L3Harris InControl ops
  material. ~50 lines, ~5 cites. `Used by:` `engine/bus.py:SafeModeState`,
  `engine/recovery.py`.
- §1.6.3 *The contact-driven operator reality.* Pre-pass / in-pass / post-pass loop.
  Cite NASA SCAN, ESA SCOS-2000 user guides. ~50 lines, ~5 cites. `Used by:`
  `engine/busmodel.py:_h_contact`, `engine/bus.py:refresh_ground_view`.
- §1.6.4 *Power calibration (NEW, sources the TT&C audit recalibration).* Cite Patel
  *Spacecraft Power Systems*, Larson/Wertz SMAD power chapter, NASA-HDBK-4002A,
  real-LEO performance reports for the 15–25% DoD/orbit range that justifies the audit's
  0.0001 SoC/s drain rate. ~70 lines, ~10 cites. `Used by:` `engine/bus.py:advance_bus`,
  every vignette's `power.drain_rate_per_s`, `docs/AUDIT-2026-06-UI-TTC.md`.
- §1.6.5 *Payload ops — SATCOM.* WGS MAJE + AEHF/Milstar anti-jam + Eutelsat Quantum.
  ~50 lines, ~8 cites. `Used by:` `engine/buscommands.py:satcom.*` verbs.
- §1.6.6 *Payload ops — ISR (EO/IR + SAR).* Maxar / Planet / Capella tasking APIs.
  ~50 lines, ~8 cites. `Used by:` `engine/isr.py:BEAM_MODES`, `engine/buscommands.py:isr.*`.
- §1.6.7 *Payload ops — SIGINT / SDA / Space-control / PNT / MW / Weather (combined,
  brief).* ~80 lines, ~12 cites total. `Used by:` `engine/sigint.py`, `engine/buscommands.py`
  (the audit's new verbs `mw.add_stare_area`, `satcom.geolocate_interference`,
  `wx.request_sector`, `pnt.flex_power`).
- §1.6.8 *Real operator interfaces.* SCOS-2000, RTI DDS, modern ground systems.
  ~40 lines, ~5 cites.
- §1.6.9 *Live modeling gaps (the three TT&C audit follow-ups).* Dead `power_w` field,
  `propellant_frac` ↔ `delta_v_ms` decoupling, thermal integrator not wired. Each item
  cites the relevant standards + the audit doc. ~40 lines, ~6 cites.
- §1.6.10 *How this maps into the simulator.* No new external cites; integration pass.

**File 1.7 — `07-legal-norms-and-roe.md` (~2× expansion to ~300 lines, ~30 inline cites):**

- §1.7.1 *The treaty floor (OST 1967, Registration 1976, Liability 1972).* Inline-link
  treaty texts from UNOOSA. ~60 lines, ~8 cites. `Used by:` `session/manager.py` ROE
  defaults, `docs/AUDIT-2026-06-COMMANDS.md` §M2 framing.
- §1.7.2 *LOAC applied to space.* *Tallinn Manual 2.0* for cyber-in-space, *Woomera
  Manual* and *MILAMOS Manual* drafts. ~50 lines, ~6 cites. `Used by:` ROE chip text in
  `content/vignettes/intro_brief/roe_note`.
- §1.7.3 *The 2022 destructive-DA-ASAT test moratorium.* State Department release,
  UNGA Resolution 77/41 full text, SWF tracker, the 36 states that have joined as of
  2024. ~50 lines, ~8 cites. `Used by:` `engine/effects.py:Outcome="destroy"` political
  cost, `engine/engage.py:INTERCEPTORS` (the test record).
- §1.7.4 *Norms and CBMs under negotiation.* OEWG, GGE on PAROS, UNGA Resolution 75/36
  ("Reducing space threats through norms"). ~40 lines, ~5 cites.
- §1.7.5 *ROE design pattern (how the sim maps law to play).* Reversible-effects-first,
  `roe_kinetic_authorized` and `roe_cyber_authorized` gates, escalation-cost telemetry.
  No new external cites; cross-link to engine. ~40 lines, ~3 cites. `Used by:`
  `session/manager.py` ROE handling, `engine/orders.py` validation gates.
- §1.7.6 *Cross-references.* Integration pass.

**File 1.8 — `INDEX.md`.** Single integration-pass deliverable; no `deep-research`
invocation required.

**Subsection count for Tier 1.** The Tier 1 files decompose into ~45 `deep-research`
invocations (vs. ~10 file-level invocations under the failed cadence): File 1.1 = 7
invocations, File 1.2 = 7, File 1.4 = 6, File 1.5 = 12 (the 9 per-mission summaries
are individually small), File 1.6 = 9, File 1.7 = 5, plus 5 integration passes (one per
file, done in main session). The increase in invocation count is intentional — small
scoped invocations are what made wave 1's `03-counterspace-taxonomy.md` invocation
succeed; small scope per invocation is the load-bearing constraint.

#### 12.5.2 Tier 2 — Per-mission and per-actor deep-dives

Tier 2 covers six new files: the three per-mission files of Track D and the three
per-actor files of Track A.

**File 2.1 — `05a-isr-eo-sar.md`.** Lit-review tasks: (a) cite the Maxar tasking-guide
public docs, Planet Tasking API public docs, Capella tasking API public docs (already
heavily cited in the audit); (b) cite the NRO Center for the Study of National
Reconnaissance KH-program historical releases; (c) cite published NIIRS scoring guides;
(d) cite NRO/NGA TPED workflow references where publicly available; (e) cite the
Sun-synchronous orbit primer references (J2-secular-precession-driven). Analysis tasks:
(a) reconcile per-payload-class claims with `engine/isr.py:BEAM_MODES`; (b) document
the commercial-vs-government tasking timeline difference (commercial tasking is
days-to-hours, government can be minutes); (c) add `Used by:` cross-links. Output: ~700
lines.

**File 2.2 — `05b-satcom-pnt.md`.** Lit-review tasks: (a) cite 53 SOPS / 4 SOPS public
fact sheets, the WGS MAJE upgrade public material (already cited in the audit), AEHF
and Milstar publicly-available anti-jam material; (b) cite GPS interface specifications
(IS-GPS-200E for flex power, IS-GPS-705 for L1C); (c) cite the GAO M-code report (the
audit's source for `pnt.flex_power`); (d) cite the Galileo PRS public material, GLONASS
status pages, BeiDou public roadmap. Analysis tasks: (a) reconcile per-system claims
with the engine's `pnt` and `satcom` payload types and the audit's new PNT verbs
(`pnt.flex_power`, `pnt.set_health_flag`); (b) reconcile the SATCOM section with
`satcom.geolocate_interference` and the existing `satcom.set_frequency_plan`
infrastructure; (c) document the 2 SOPS / 19 SOPS / 4 SOPS organizational split and the
NANU process; (d) add `Used by:` lines. Output: ~700 lines.

**File 2.3 — `05c-sigint-mw-wx-sda.md`.** Lit-review tasks: (a) cite NRO public SIGINT
material (Trumpet, Mercury, Mentor programs that are publicly acknowledged); (b) cite
2 SWS and SBIRS scanner+starer public material (the audit's source for
`mw.add_stare_area`); (c) cite NOAA OSPO process docs for GOES-R MDS requests (the
audit's source for `wx.request_sector`); (d) cite 18 SDS / 19 SDS SSN tasking public
material. Analysis tasks: (a) reconcile per-mission claims with the engine's `sigint`
/ `mw` / `weather` / `sda` payload types; (b) reconcile the SDA section with
`engine/ssn.py`'s mock SSN model; (c) document the AU Space Primer SSN tasking-category
scheme that already informs `engine/ssn.py`'s priority-SLA model; (d) add `Used by:`
lines. Output: ~700 lines.

**File 2.4 — `02a-china-deep-dive.md`.** Lit-review tasks: (a) cite the April 2024 PLA
reorganization analyses (CASI, RAND, CSIS — multiple sources because the reorganization
is still being interpreted); (b) cite the CSIS Space Threat Assessment China chapter,
SWF Global Counterspace China chapter, IISS *Military Balance* China chapter; (c) cite
Andrew Erickson's publicly-available work on PLA force structure; (d) cite the State
Department / DoD China Military Power Report space sections. Analysis tasks: (a)
reconcile per-system claims with `coa-china-ml.yaml` and `coa-china-md.yaml`;
(b) reconcile the `china_integrated` Red doctrine profile (`session/redai.py`) with the
SoS doctrine in this file; (c) tie the 36th Test Base discussion to the
`INTERCEPTORS["mrbm_kkv"]` source (SC-19 is mrbm_kkv class); (d) add `Used by:` lines.
Output: ~600 lines.

**File 2.5 — `02b-russia-deep-dive.md`.** Lit-review tasks: (a) cite Bart Hendrickx's
public Russian-space analyses (the canonical accessible Russian-space scholarship);
(b) cite SWF Russia chapter, CSIS Russia chapter, IISS *Military Balance* Russia chapter;
(c) cite the publicly-acknowledged 2024 Russian co-orbital nuclear-counterspace
discussion (Burevestnik-derived speculation; Schmitt's commentary); (d) cite the EW
Troops doctrinal publications where available. Analysis tasks: (a) reconcile per-system
claims with `coa-russia-ml.yaml` and `coa-russia-md.yaml`; (b) reconcile the
`russia_ew_first` Red doctrine profile (`session/redai.py`); (c) tie the Nudol discussion
to the `INTERCEPTORS["abm_heavy"]` source; (d) add `Used by:` lines. Output: ~600 lines.

**File 2.6 — `02c-emerging-actors.md`.** Lit-review tasks: (a) for India, cite the DRDO
Mission Shakti press releases and the 2019 SWF / CSIS post-test analyses; (b) for Iran,
cite the documented Strait of Hormuz GPS-jamming campaigns (open-source maritime
reporting), IRGC ASB structural overviews; (c) for DPRK, cite the NADA structural
overview and the publicly-attributed cyber operations (Lazarus Group / Bureau 121's
satellite-adjacent operations); (d) for Israel, cite the publicly-acknowledged Yahalom
and Ofeq program material; (e) for the SpaceX-as-non-state-actor discussion, cite the
publicly-discussed Starlink-Ukraine episodes and Walter Isaacson's Musk biography
passages on the same. Analysis tasks: (a) reconcile each actor with the corresponding
COA vignette where one exists (`coa-misc-iran-ml.yaml`) and identify which actors lack
a COA file (potential v1.1 vignettes); (b) add `Used by:` lines. Output: ~700 lines.

Tier 2 total: ~3,000 lines across six files, ~120 new citations.

#### 12.5.3 Tier 3 — Counterspace systems and physics

Tier 3 covers eight new files: the six counterspace-system files of Track B (excluding
the spine which Tier 1 handles) and the two physics files of Track C.

**File 3.1 — `03a-da-asat-systems.md`.** Lit-review tasks: (a) for SC-19/DN-3, cite the
NASA / SWF FY-1C debris analyses, the IISS contemporaneous reporting, the CRS RS22652
report; (b) for Nudol/A-235, cite Jonathan McDowell's Nudol page, IISS analysis, NASA
HUSIR/Goldstone observations; (c) for SM-3, cite the Operation Burnt Frost public DoD
material; (d) for PDV-Mk2, cite the Indian DRDO Mission Shakti public material and the
post-test debris analyses; (e) anchor each test with a primary date-stamped citation
plus a Wayback snapshot. Analysis tasks: (a) author the per-system table that becomes
the inline source for `engine/engage.py:INTERCEPTORS`; (b) cross-reference the audit's
discussion (`docs/AUDIT-2026-06-COMMANDS.md` §M2 and the realism research §14) and
ensure the file is the canonical replacement for that discussion; (c) add bidirectional
`Used by:` / `# Source:` cross-links. Output: ~700 lines.

**File 3.2 — `03b-coorbital-rpo.md`.** Lit-review tasks: (a) for SJ-21 / SJ-15, cite the
CSIS *Dancing Lights in Space* analysis and the 2022 Beidou-G2 relocation public
reporting; (b) for Burevestnik, cite Bart Hendrickx's analyses and the publicly-acknowledged
co-orbital sub-satellite ejection pattern; (c) for Olymp-K / Luch, cite the CSIS GEO RPO
analyses and the Eutelsat / Intelsat operational complaints; (d) for USA-270, cite the
publicly-acknowledged GSSAP material; (e) for the OOS reference precedents, cite MEV-1 /
MEV-2 (Northrop public material). Analysis tasks: (a) author the per-system table sourcing
the `INTERCEPTORS["coorbital"]` parameters; (b) document the dual-use nature of OOS
versus counterspace; (c) add `Used by:` lines. Output: ~700 lines.

**File 3.3 — `03c-ew-jamming.md`.** Lit-review tasks: (a) for CCS Block 10.2, cite the
USSF / Space Delta 3 public material that the audit already cited; (b) for Tirada-2 /
Pole-21 / Bylina, cite Bart Hendrickx and the SWF Russia chapter (already audit-cited);
(c) for Tobol, cite the SWF Tobol entry; (d) for AEHF / Milstar ECCM, cite the
publicly-available program-office material; (e) for processing-gain fundamentals, cite
the canonical EW textbooks (Adamy, *EW 101* through *EW 104*) where citable. Analysis
tasks: (a) author the J/S analysis that grounds `engine/jam.py:effective_success_prob`;
(b) document the modulation database's source basis (the four-modulation taxonomy is
canonical EW practice); (c) document the defender-modifier multipliers introduced by the
audit (`_FREQ_HOP_RESIDUAL = 0.4`) with their processing-gain source; (d) add
`Used by:` lines. Output: ~700 lines.

**File 3.4 — `03d-directed-energy.md`.** Lit-review tasks: (a) cite the Sokol-Eshelon
historical material and the contemporary Peresvet public material; (b) cite the reported
Chinese Zimu-1 program (multiple analyst attributions, multi-source); (c) cite the optical
hardening literature (MgF₂ coatings, Brewster-angle considerations); (d) cite the canonical
DE-vs-satellite analyses (the David Wright / Laura Grego work on optical dazzle).
Analysis tasks: (a) reconcile the engine's DE category with the audit's recommended
`isr.shutter_sensor` verb (currently a planned addition); (b) document the
"dazzle-degrade-destroy" gradient that DE supports; (c) add `Used by:` lines. Output:
~600 lines.

**File 3.5 — `03e-cyber.md`.** Lit-review tasks: (a) for Viasat KA-SAT, cite Viasat's
own incident overview, the SentinelOne AcidRain analysis, the EU/UK/US attribution
statements (each separately dated); (b) cite the SPARTA framework public material;
(c) cite historical incidents (ROSAT 1998 publications, NASA TDRS attack analyses); (d)
cite the publicly-acknowledged supply-chain compromises (the recent Solar Winds /
satellite-adjacent cases). Analysis tasks: (a) author the per-incident table that
sources `engine/cyber.py:VECTORS` (`ground_modem` exists explicitly because of Viasat —
the file makes this clear); (b) document the `seize_c2` payload (`engine/cyber.py:PAYLOADS`)
as the Viasat-style attack model; (c) add `Used by:` lines. Output: ~700 lines.

**File 3.6 — `03f-nuclear-emp.md`.** Lit-review tasks: (a) for Starfish Prime, cite the
publicly-available DOE / DTRA historical material; (b) for the Soviet K-3/4/5 tests,
cite the Hendrickx historical analyses; (c) for modern EMP modeling, cite the EMP
Commission reports (publicly available); (d) for the 2024 Russian co-orbital nuclear
counterspace discussion, cite the publicly-available analytic responses (Schmitt, CSIS).
Analysis tasks: (a) document why this category is deferred for v1
(`03-counterspace-taxonomy.md` already flags it); (b) document what v2 work would need
to include nuclear-EMP; (c) anchor the OST Article IV interpretation. Output: ~500 lines.

**File 3.7 — `04a-propagator-fidelity.md`.** Lit-review tasks: (a) cite the canonical
references for Kepler+J2 errors against SGP4 (Vallado revisitation, Hoots papers);
(b) cite the SGP4-vs-numerical-integration accuracy literature; (c) cite Skyfield's
own published accuracy claims; (d) cite the existing Skyfield test in
`spacesim/tests/`. Analysis tasks: (a) author the per-fidelity-tier accuracy table;
(b) document the simulator's chosen tier ("moderate") and its known errors; (c) add
`Used by:` lines pointing at `engine/propagator.py` and `engine/orbit.py`. Output: ~500
lines.

**File 3.8 — `04b-debris-and-conjunction.md`.** Lit-review tasks: (a) cite the NASA ORDEM
3.x model overview; (b) cite the ESA MASTER overview; (c) cite the Cosmos 1408 debris
evolution analyses (NASA HUSIR/Goldstone, the audit's existing citation); (d) cite the
Burnt Frost reentry timeline (DoD public material); (e) cite FY-1C debris persistence
(NASA ODPO bulletins). Analysis tasks: (a) author the altitude-vs-persistence table that
sources the audit's `debris_cone_estimate(persistence)` regime; (b) document the
conjunction-screening model that future `prop.collision_avoid` work will need; (c) add
`Used by:` lines. Output: ~600 lines.

Tier 3 total: ~5,000 lines across eight files, ~150 new citations.

#### 12.5.4 Tier 4 — Operations, legal, history, forward-looking

Tier 4 covers five new files: Track E's two new files (`06a-ground-segment.md`,
`07a-incident-record.md`) and all three Track F files.

**File 4.1 — `06a-ground-segment.md`.** Lit-review tasks: (a) cite the AFSCN architecture
public material; (b) cite NASA Space Network / TDRSS public material (the Space Network
Users' Guide); (c) cite the AWS Ground Station documentation (already audit-cited);
(d) cite commercial GS provider material (KSAT, ATLAS, Viasat-RTE). Analysis tasks:
(a) document GS site selection rationale; (b) anchor the ground-segment-as-attack-surface
theme with cross-references to `03e-cyber.md`; (c) add `Used by:` lines. Output: ~500
lines.

**File 4.2 — `07a-incident-record.md`.** Lit-review tasks: (a) for each cataloged
incident, identify the primary-source citation and a corroborating secondary source;
(b) for attribution claims, cite the formal attribution statements (state announcements,
Tallinn-style legal opinions where applicable). Analysis tasks: (a) per entry, identify
the engine-relevant lesson (what the simulator demonstrates about that incident pattern);
(b) cross-link each entry to the relevant Track B and Track A files; (c) format as a
catalog (date / actor / target / effect / attribution / primary source / engine lesson);
(d) add `Used by:` lines. Output: ~700 lines.

**File 4.3 — `08-commercial-and-allied.md`.** Lit-review tasks: (a) for proliferation,
cite the Starlink V2 / Kuiper / OneWeb public material and the publicly-acknowledged
constellation roadmaps; (b) for allied SDA, cite Five Eyes SST public material, the
USSPACECOM / 18 SDS public combined-operations material, the French CSO public material,
Japan's SDA contribution material; (c) for the non-state-actor question, cite Walter
Isaacson's Musk biography passages, the publicly-acknowledged Starlink-Ukraine episodes,
and the analyst commentary that followed. Analysis tasks: (a) document how proliferation
changes the Pₖ math and the targeting calculus (a single-shot DA-ASAT becomes
militarily-inadequate against 12,000 LEO satellites); (b) cross-link to FUTURE-WORK
items on mega-constellation resilience; (c) add `Used by:` lines. Output: ~500 lines.

**File 4.4 — `09-emerging-tech.md`.** Lit-review tasks: (a) for optical ISLs, cite the
Starlink Gen 2 public claims, the USSF Tranche 1 transport-layer material; (b) for
software-defined payloads, cite the Eutelsat Quantum public material (already audit-cited);
(c) for on-orbit refueling, cite Northrop MEV-1/MEV-2 public material and the SPRINT
program where citable; (d) for manufactured-in-space, cite the recent
Made-In-Space/Redwire and Varda public material. Analysis tasks: (a) cross-link each
emerging tech to the relevant v1.1+ FUTURE-WORK items (mega-constellation resilience,
GNSS spoof vs jam, coalition SDA, frequency-hop ECCM); (b) document what each emerging
tech would require of the engine to model; (c) add `Used by:` lines. Output: ~500 lines.

**File 4.5 — `08-commercial-and-allied.md` and `09-emerging-tech.md` shared workflow.**
These two files have significant lit-review overlap (constellation proliferation appears
in both); the agent producing them should consult the methodology file's source list and
share lookups.

Tier 4 total: ~2,200 lines across four primary new files (plus the noted shared workflow),
~80 new citations.

### 12.6 Workflow, methodology, quality bar

Workflow (**revised after Sprint 1 results — see §12.5.0**): the binding cadence is
**one `deep-research` invocation per subsection**, iterated sequentially per file, with
a commit and push after each subsection's markdown lands. The pre-Sprint-1 cadence
("one invocation per file, files in parallel within a tier") proved unworkable —
three of four file-level invocations exhausted their token budget before producing
content because `deep-research` fans out aggressively per invocation and a
file-sized brief leaves room for the fan-out to runaway. The per-subsection cadence
caps each invocation at ~20k subagent tokens with a scope small enough that the
fan-out has no room to bloat: a typical subsection brief asks for ~5–10 cited claims
and ~50–120 lines of markdown.

The per-tier sequence is therefore:

1. **Per file, per subsection:** spawn a single `deep-research` invocation with the
   per-subsection brief assembled from the §12.5.X tier task list (file-level
   lit-review tasks) and the per-subsection scope (file-level decomposition table).
   The brief template is in §12.5.0.
2. **Document immediately.** The agent returns ~50–120 lines of cited markdown.
   Append to the file under construction (or to a per-subsection staging file if the
   file is not yet ready to assemble linearly), commit with
   `docs(research): <file>#<section> — <one-line summary>`, push.
3. **Move to the next subsection.** Sequential — no batching. This is the trade-off
   for reliability: total elapsed time per file is longer, but token cost per
   invocation is bounded and progress is fully checkpointed in git.
4. **Per file: integration pass.** After all subsections of a file have landed (~5–10
   commits), run a main-session integration pass that (a) reorders subsections into
   their final §1.X.Y order, (b) regenerates the `### Sources` subsection at the foot
   of each `##` section from the inline cites, (c) verifies every `Used by:` line
   names a real engine module, (d) runs the per-file quality-bar checklist
   (§12.6 — below). Commit as `docs(research): <file> — integration pass`.
5. **Per tier: code cross-linking pass.** After all files in a tier have landed, run
   one `general-purpose` agent invocation that walks every engine module that
   hard-codes numbers, matches the constant to its sourcing research-file anchor, and
   adds `# Source: docs/research/<file>#<anchor>` comments. Commit as
   `docs(research): tier <N> — engine cross-link pass`.
6. **Per tier: adversarial verification pass.** A separate `general-purpose` agent
   with read-only tools picks a random sample of 20 cited claims from the tier's
   files, fetches each cited source, and confirms the claim is supported. Findings
   land in `docs/research/REVIEW-LOG.md` with file:line refs and per-claim verdicts
   (`✓ supported`, `⚠ partial`, `✗ unsupported`). Any `✗ unsupported` is a blocker
   for tier merge until the offending claim is re-cited or removed.

Within a tier, **files** are still independent — multiple files can be in progress
concurrently as long as each is following its own per-subsection sequence. The
constraint that matters is "one invocation per subsection," not "one file at a time."
A reasonable concurrency profile is 2 files in flight at any moment, alternating
subsection invocations between them. Going wider than that risks unverifiable parallel
context.

The
verification pass is the closest thing the corpus has to a test suite.

Methodology: `10-sources-and-methodology.md` (the first Tier 1 deliverable) is the
canonical reference. It defines: linked-citation format (inline link at claim site + a
per-section `Sources` subsection), source-quality tiers (peer-reviewed >
government/think-tank > journalism > advocacy), date-stamping convention (every claim
that names a real event carries the event date inline), annual-review-marker syntax
(`last_reviewed: YYYY-MM-DD` in frontmatter, with a stale-banner threshold of 12
months), and the cross-linking convention from Lever 4. Every later file follows this
convention without re-defining it.

Quality bar (per-file checklist, used by every authoring agent and every reviewer):
(a) Frontmatter `last_reviewed:` + `primary_sources_consulted:` count; (b) every
numerical claim (m/s, kg, $, year, Pₖ, dB) inline-cites at the claim site; (c) every
named system inline-cites at first mention; (d) every doctrinal assertion cites a
primary doctrine source or a published assessment (CSIS, SWF, IISS) — not Wikipedia
alone; (e) `### Sources` subsection at the end of every major section with
bullet-pointed URLs + Wayback snapshots + access dates; (f) bidirectional `Used by:`
cross-link lines per Lever 4; (g) no claim depends on a single source unless that
source is the primary one (the doctrine document itself or the test record itself);
(h) single-source claims are flagged inline. The reviewer agent in the verification
pass checks (a)-(h) per file.

### 12.7 Cost, sequencing, risks

Cost (rough, agent-token-based, **revised per §12.5.0**): the per-subsection cadence
trades fewer-large invocations for more-smaller invocations. Total token cost is
similar; total invocation count goes up ~3×, but each invocation is bounded at
≤20k subagent tokens (vs. ~50–100k under the failed file-level cadence), so any
single failure costs at most one subsection's worth of work.

| Tier | Lines target | Citations | `deep-research` invocations | Integration passes | Code-link + verification |
|---|---:|---:|---:|---:|---:|
| Tier 1 | ~3,500 | ~250 | ~45 (subsection-level) | 5 (one per existing file) | 2 (one each) |
| Tier 2 | ~3,000 | ~120 | ~40 (each new file decomposed into ~7 subsections) | 6 (one per new file) | 2 |
| Tier 3 | ~5,000 | ~150 | ~55 (eight new files × ~7 subsections) | 8 (one per new file) | 2 |
| Tier 4 | ~2,200 | ~80 | ~30 (five new files × ~6 subsections) | 5 (one per new file) | 2 |
| **Total** | **~13,700** | **~600** | **~170 authoring invocations** | **~24 integration passes** | **~8 follow-on passes** |

Total: ~170 `deep-research` invocations + ~24 integration passes (main session, no
agent) + ~8 cross-link/verification passes (`general-purpose` agents). Per-invocation
budget: ≤20k subagent tokens. Total estimated subagent cost: ~3–4 million tokens,
similar magnitude to the file-level estimate but spread across many small bounded
invocations. The integration-pass count is high but they require no subagent tokens —
they are main-session work consolidating the per-subsection drafts.

Sequencing (revised): Tier 1 first (already 2 of 9 files landed: `10-sources-and-methodology.md`
and `03-counterspace-taxonomy.md`). Tiers 2 and 3 can begin as soon as Tier 1's
methodology and the spine files (`03`, `05`) have landed. Tier 4 follows. Each tier
commits and pushes per-subsection so the corpus is usable at every commit boundary.
Recommended pacing under the new cadence: rather than "Sprint 1 = Tier 1 in one
session," plan ~10–15 subsection commits per working session (1–2 files of progress),
across roughly 12–15 working sessions for the full expansion.

Risks: (i) **Source rot.** URLs to government / think-tank sites move or 404 over a
2-3 year horizon. Mitigation: Wayback snapshots beside every live URL (mandated by the
methodology file). (ii) **Classification line.** This is a PME tool — every source
must be unclassified and open. Mitigation: the methodology file enumerates which
categories of content are out of bounds (CDR/SAP/SCI references); the verification
pass spot-checks. (iii) **Attribution claims.** Some named systems rest on a small
number of analyst assessments. Mitigation: multi-source where possible; flag
single-source claims inline (quality-bar criterion h). (iv) **Scope creep into design
docs.** Research is `why`, build-spec is `what is built`, design is `how it is built`.
Mitigation: reviewers reject content that drifts into spec/design territory. (v) **PME
audience drift.** The corpus must remain accessible to a USSF Guardian operator audience
without becoming an academic monograph. Mitigation: the existing `06-bus-and-payload-operations.md`
voice is the model; the verification pass checks tone-consistency.

### 12.8 Status and the next concrete step

**Status as of 2026-06-21 (Sprint 2 mid-flight):**
- ✅ File 1.0 — `10-sources-and-methodology.md` landed (commit `968c4be`, 363 lines).
- ✅ File 1.3 — `03-counterspace-taxonomy.md` landed (commit `b39c24f`, 821 lines,
  147 inline cited URLs). Structural exemplar.
- ✅ File 1.4 — `04-orbital-mechanics-primer.md` landed (commits `dde9739..14c2454`,
  822 lines, 204 cited URLs incl. the §2 access-taxonomy expansion to 25 permutations
  across 7 categories). Six staged subsections + per-file integration pass.
- ✅ File 1.6 — `06-bus-and-payload-operations.md` landed (commit `6c17e04`, 674 lines,
  99 cited URLs). Ten staged subsections (§1.6.1 bus subsystems / §1.6.2 SOH+safe mode /
  §1.6.3 contact loop / §1.6.4 power calibration / §1.6.5 SATCOM ops / §1.6.6 ISR ops /
  §1.6.7 combined SIGINT/SDA/Space-control/PNT/MW/Weather / §1.6.8 operator interfaces /
  §1.6.9 live modeling gaps / §1.6.10 simulator mapping) + integration pass. Sources
  the audit power-rate recalibration end-to-end.
- ✅ File 1.7 — `07-legal-norms-and-roe.md` landed (commits `469c8e8..cd37fe2`, 795
  lines, 106 cited URLs). Five staged subsections (§1.7.1 treaty floor / §1.7.2 LOAC /
  §1.7.3 2022 DA-ASAT moratorium / §1.7.4 CBMs / §1.7.5 ROE design pattern) +
  integration pass.
- ✅ File 1.1 — `01-doctrine-western.md` landed (commit `a4c5780`, 289 lines, 48
  cited URLs; follow-up `6e65e8b` added §1.1.6 responsible-counterspace coverage).
- ✅ File 1.2 — `02-doctrine-non-western.md` landed (commit `25b3b17`, 217 lines,
  57 cited URLs).
- ✅ File 1.5 — `05-mission-types-and-counters.md` landed (commit `2794958`, 360
  lines, 61 cited URLs).
- ✅ File 1.8 — `research/INDEX.md` regenerated with the missing
  `10-sources-and-methodology.md` row.

**Tier 1 is complete.** All 9 files (1.0–1.7 + 1.8) are landed. Every one of the 8
content files now carries a reciprocal "Research encyclopedia" cross-reference
bullet in its Cross-references section, linking forward to the matching R1xx/R2xx/
R3xx/R4xx encyclopedia topics — completing the bidirectional merge between the
doctrine-primer corpus and the R100-R500 encyclopedia. The stale scratch draft
`research/working/07/1.7.5-roe-design-pattern.md` (superseded once File 1.7
integrated it) has been deleted.

**Cadence revision (Sprint 1 → Sprint 2):** the per-subsection workflow in §12.5.0 /
§12.6 / §12.7 supersedes the original "one invocation per file, files in parallel
within a tier" plan. Sprint 2 confirmed the new cadence works at scale: all 8
content files landed with no single invocation exhausting token budget. Average
per-subsection cost ~50k subagent tokens, well under the budget cap.

**Next concrete step.** Tier 1 is done. Tiers 2-4 (per-mission/per-actor deep-dives,
counterspace-systems-and-physics, ops/legal/history) remain scoped but **not yet
authorized** — see §12.1 for the authorization gate before starting any Tier 2+ file.

**Per-tier follow-on passes deferred to end-of-tier:**
- Code cross-link pass — once Tier 1 lands, scan engine modules for the `Used by:`
  back-references and add `# Source:` comments at the named symbols pointing to the
  research file + subsection that grounded the design choice. Targets every engine
  module named in Files 1.4 + 1.6 + 1.7's `Used by:` paragraphs.
- Adversarial verification pass — review every cited URL for primary-source quality,
  flag Tier D (Wikipedia) as standalone-source violations, swap to Tier A/B where
  feasible. Writes findings to `docs/research/REVIEW-LOG.md` (to be created).
  Known item: File 1.6 §7.1 has one Wikipedia link (Orion/Mentor SIGINT class) that
  needs Tier A/B replacement.

**Reviewer sign-off (if revisiting authorization):** (a) the file taxonomy in §12.4
covers the topics the PME audience cares about — anything missing or redundant?
(b) the four-tier prioritization is the right order — Tier 1 first is the strong
recommendation, but Tiers 2-4 are reorderable; (c) the per-file quality bar in §12.6
is the right bar — anything to add or relax? (d) the per-subsection cadence in §12.5.0
is acceptable — or should we attempt a different orchestration (e.g. wider
parallelism)? (e) the revised cost in §12.7 is acceptable — ~170 small invocations
across ~12–15 working sessions vs. the original ~37 large invocations across 3
sessions.

## 13. Strategic review (2026-07) — deferred recommendations

Source: [`reviews/strategic-review-2026-07.md`](reviews/strategic-review-2026-07.md), dispositioned
in full by [`reviews/architecture-update.md`](reviews/architecture-update.md). That document is the
authoritative disposition record (accepted/deferred, with rationale) for all 24 recommendations;
this section is only the durable *tracking* home for the items marked "Accepted (deferred)" there,
so they aren't lost between now and whenever someone picks one up. Each item below cites its
recommendation ID and the review's own priority/difficulty/placement — re-read
`architecture-update.md` before starting any of these, since several depend on another landing
first (noted inline).

- **R1 — Close the encyclopedia sourcing/scope defect (GAP-13).** R500 first (zero citations, most
  speculative claims); gate for citing the encyclopedia externally. Owner: `research-future-
  operations` (R500) then `research-methods-and-validation` (R400), following the existing §12
  cadence discipline above. (R100/R300 are already closed under `research-ow-orbital-mechanics`/
  `research-doctrine-exercises`; R200 has no dedicated skill yet.)
- **R2 — Author GDS-06 (Non-functional Requirements) through GDS-10.** Already the ladder's own next
  scheduled step (`architecture/INDEX.md` §1); GDS-06 first, since "nearly every Part 2 concept
  [of the strategic review] turns on scale/performance/security envelopes that are currently
  undefined."
- **R8 — Headless Monte Carlo experimentation harness (IN-02/FC-14).** Near-zero engine work: a
  batch runner + output schema over the existing deterministic seed/eventlog/FS-301-export seams.
  Value High, Difficulty Low-medium per the review.
- **R9 — Commission GAP-07 (training-transfer) research** to shape DOM-002/DOM-005 before they
  harden (see `architecture-update.md` §3 for why this must land before those frameworks are
  authored, not after).
- **R10 — Counterfactual AAR (IN-01) + belief-vs-truth analytics (IN-06).** Flagship pedagogy
  features for the next release; both are near-pure leverage of the existing determinism/fog-of-war
  invariants, no new subsystem required.
- **R11 — Commercial SDA feed for the mock SSN** (already scoped as §7 below) **+ one
  commercial-entanglement vignette.** Architectural direction already acknowledged in GDS-02/03/04
  (see `architecture-update.md`); this item is the implementation.
- **R12 — Fund GAP-01 (space environment) research + an environment term** in the effect/telemetry
  model, enabling the attack-vs-environment vignette class and an attack-signature-diagnosis drill
  (IN-03).
- **R13 — Proliferated-constellation program (FC-06 + GAP-10).** Research first, then engine-scale
  validation, aggregation constructs, and a proliferated vignette family. High difficulty; flagship
  correction to weakness W1 (fleet-scale assumptions).
- **R14 — Coalition play (FC-09 + R316).** N-cell generalization with releasability filters and
  per-nation ROE. Highest-likelihood external demand per the review; High difficulty.
- **R15 — Campaign container + time compression (FC-13).** Also unblocks reconstitution (FC-04),
  sub-threshold adversary behavior, and cohort progression (IN-10).
- **R16 — Persistent debris + conjunction wiring (FC-08 + GAP-02).** Wires the currently-unwired
  `prop.collision_avoid` verb (§2 above) into a persistent, world-changing consequence.
- **R17 — Ground-segment-as-terrain cyber deepening (FC-11 + GAP-12).**
- **R18 — Scenario generator (IN-07) + facilitator authoring UX (FS-108 promotion).** Attacks both
  content decay and the White-Cell-hostile authoring gap together.
- **R19 — Document the distributed-use security growth path** (threat model, token design sketch,
  which endpoints would need binding) **before the first multi-site/coalition request**, alongside a
  GAP-11 federation-compatibility study of the `SessionAPI` seam (see ICD §7 items 2 and 12).
- **R20 — Human-AI teaming laboratory program (FC-01 + FC-15).** Long-Term Vision; research-first.
  Revisit when FC-01 (AI-supported mission planning) is scheduled.
- **R21 — AI-vs-AI doctrine exploration (IN-08).** Depends on R7 (AI-Red fog parity, already tracked
  in §1 above) and R8 landing first.
- **R22 — Cislunar research line (FC-07 + GAP-04).** Research-only; revisit implementation when
  allied cislunar SDA concepts mature.
- **R24 — Training-transfer longitudinal validation study.** Follow-through on R9; cohort tracking
  (IN-10) against operational-performance criteria.

Not tracked here (no action needed): R3–R7 and R23 were actioned directly as documentation changes
in `architecture-update.md`; R7 was already fully tracked in §1 above before this review.

