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
- **`Order` as a serializable transport message.** Today `Order` is an engine dataclass passed
  through the in-process boundary. Moving it to pydantic at the API surface (with the engine
  dataclass kept internal) is a pre-req for the network transport.

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

The implemented verbs are listed in `build-spec/07-operator-console.md` §16.11. Remaining catalog verbs
from `13-operator-command-catalog.md` that have **no engine handler** yet:

- **Bus**: `cdh.load_stored_program`, `cdh.reset_subsystem`, `comms.point_antenna`,
  `comms.set_crypto`, `prop.collision_avoid`, `prop.cancel_burn` (queue is implemented; an explicit
  cancel-by-verb is not), `eps.select_bus`, `adcs.desaturate`, `adcs.point_payload` (the existing
  attitude mode covers the common case).
- **Payload**: `isr.set_mode`, `isr.prioritize_downlink`, `isr.calibrate`, `isr.assess_quality`,
  `sigint.set_band` / `sigint.geolocate` / `sigint.downlink`, `sda.task_search` / `sda.task_track`
  / `sda.task_characterize` / `sda.cue` / `sda.downlink` (today's `observe` action with `intent`
  covers the SDA loop), `satcom.set_transponder` / `satcom.set_frequency_plan` /
  `satcom.reconfigure_beam` / `satcom.report_interference`, `pnt.set_integrity` /
  `pnt.report_status`, `mw.set_sensor_mode` / `mw.report_alerts`, `wx.downlink`.
- **Defense / space control**: `def.maneuver_evade` (would consume Δv like `prop.maneuver`),
  `def.escort_posture`, `def.disperse`, `def.patch_cyber` is implemented; remaining `sc.*` verbs
  largely duplicate the existing `jam`/`engage`/`cyber`/`observe` order actions and are
  intentionally not re-wired as command verbs to avoid aliasing.

Each one follows the same pattern: a small mutation in `apply_command`, a regression test in
`spacesim/tests/test_bus_commands.py`, an entry in the UI's `PARAM_TEMPLATE` / `actionsFor` /
`VERB_SUBSYSTEM` / `VERB_ROLE`. None require architectural work.

## 4. UI strategic items (out of v1 scope, per `build-spec/01-context-and-scope.md` §3.2)

- **Constellation aggregation (v2).** Manage ≥3 sats as a group from a single panel. The current
  per-asset drill-down is the right unit for v1's ≤24-sat / ≤3-per-constellation cap.
- **Formal APP-6-adapted space-symbology pack.** Today's marker/colour system is consistent
  across the 2D map and 3D globe but not formally specified; a future pack would standardize
  shapes per object type for joint-/coalition-use credibility.
- **Δv "years of life" panel.** Dedicated propulsion sub-tab spelled out by
  `14-delta-v-economy.md` — the data exists in `AssetResources.delta_v_ms`, the panel does not.
- **Constellation/grouped fleet-rail badges.** Tied to the constellation-aggregation item above.

## 5. Bus, payload, and recovery refinements

- **Posture-command persistence beyond a tick.** ✅ `def.harden` now reduces the safe-mode
  probability at the effect resolver (operator-commanded hardening adds 0.5 to the asset's
  `hardening` for the susceptibility computation, on top of any vignette baseline).
  `def.frequency_hop` already scales the comms jam term in telemetry. `def.set_threat_warning`
  remains informational (no resolver impact yet).
- **EW / bus-stress safe-mode inducement** (vs. the cyber path that is exercised today). The
  resolver already supports `outcome: safe_mode`; vignettes don't drive it via EW yet.
- **Per-step recovery deep-links.** The recovery strip surfaces a single Patch action and a free-
  text blocked-reason; promoting it to per-step (`establish_contact` / `dump_telemetry` / ... )
  needs additional engine state about which step is currently blocking.
- **Contention bookings rewind-safety.** `OrderSystem._sensor_bookings` is cleared on rewind
  along with the order registry. Future work: persist the bookings in the eventlog so they
  reconstruct on `replay()` identically without manual rebind.

## 6. Sat / fleet caps validation

`build-spec/01-context-and-scope.md` declares ≤24 satellites for v1 with a hard ceiling of 48, and
constellations ≤3 sats. The caps are documented but **not enforced at vignette load**; future
work: validate caps in `content/vignette.build_world` with a clear rejection.

## 7. Mock Space Surveillance Network (SSN) — ✅ implemented

The per-cell mock SSN is fully implemented per `build-spec/08-ssn.md` §17 (engine + session +
API + UI + V2/V7/V8 vignette opt-in + acceptance tests; quality model and save/resume included).
Remaining items not carried into v1:

- **Cost / collection-budget** for priority/immediate (force triage). Recommended as a later
  balance dial.
- **Commercial / third-party feeds** — a neutral commercial provider both cells can buy from
  (extends the per-cell model).
- **Auto-cueing organic → SSN** — let an organic detection auto-cue an SSN characterize request.

## 8. UI polish / minor

- **Browser-GUI verification harness.** Backend API smoke tests (scene, telemetry param list,
  telemetry series count, fog cross-cell, dry-run, SSN session) are now in `test_web.py`. The
  remaining gap is DOM/render smoke: Playwright for Python (`@pytest.mark.e2e`, opt-in) to verify
  that the 2D map, 3D globe, and telemetry graph canvas actually draw — not yet implemented.
- **Stronger seat-chip / role-switcher visual treatment.** The role-filter chips (All/Bus/
  Payload/SDA) ship, but a richer "seat chip" combining cell + role per the original §1.2 of the
  UI plan would clarify hot-seat handoffs in PME.
- **Region detach v2.** The current Detach viewers pops a slow-tick belief-scene window; a full
  multi-display reflow (independent region A/B/C/D detach with shared selection state) requires
  postMessage state-sync and is deferred.
- **Two-trace overlay normalisation legend.** The overlay trace is normalised for shape
  comparison; surfacing the second-trace y-scale explicitly is a polish task.

## 9. Larger / strategic

- **Coalition / shared SDA feed.** Lower-control external tracks rendered alongside the cell's
  own custody — pairs with SSN above.
- **Replay branching UI.** The engine supports rewind/undo and branch comparison
  (`session/aar.py`); a richer branch-tree UI is a v2 nicety.
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

This list is the v1 → v1.1+ TODO. When picking an item, prefer:
1. Items in §3 (catalog-verb gaps) — they are small, test-first, and uniformly wired.
2. Items in §5 (posture persistence / recovery deep-links) — small engine refinements with
   immediate pedagogical value.
3. Items in §1 (multiplayer transport) — the highest-architectural-leverage upgrade.

(§10 has shipped — all 20 items are done; only the full WYSIWYG vignette editor under
§10.D.17 is still partially open.)

Anything else is best gated by user demand or a paying engagement.

## User added Future work
1. orbital paths in 3D view
2. ground traces in 2D view
3. blue accents around headings on blue cell screens
4. red accents around headings on red cell screens
5. white accents around headings on white cell screens
6. add a screen blank button to allow handoff between cells. it should blur the screen and bring up a handover heading
7. expand the install guide with a target audience of someone that has not used python before
8. generate a logo for this tool and integrate it into docs and the UI
9. add on-hover tool tips for all buttons
10. add help menus and screens
11. ensure the UI is robust to users zooming in browsers
12. ensure it is stable in multiple common browsers
