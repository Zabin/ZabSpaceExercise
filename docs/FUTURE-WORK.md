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

## 10. Twenty UX & realism upgrades (brainstormed)

These are *additive* enhancements — none of them duplicate items in §1–§9 above. Numbered for
reference, grouped by theme.

### 10.A UX & visual (5)

1. **Cell-color theming propagation.** ✅ *Seeded:* `body[data-cell]` now drives a `--cell-accent`
   that tints panel left borders, h2 underlines, the toolbar bottom border, and table hover/select
   states. Remaining work: also tint own-asset markers on the 2D map and 3D globe with the cell's
   accent (instead of hardcoded green), and add a discreet "you are driving the ⟨BLUE⟩ console"
   text chip in the toolbar so the seat is unambiguous at a glance.
2. **Color-blind / high-contrast palette swap.** A `body.contrast-cb` modifier that replaces the
   default green/yellow/red SOH palette with a colour-blind-safe set (Wong / Okabe-Ito), and bumps
   global font weight. Persisted in localStorage like the existing presentation-mode toggle.
3. **Compact "projector mode" preset.** A White-Cell-friendly layout that maximises the 2D map +
   3D globe, hides the order-compose form, and enlarges the fleet-rail SOH glyphs. Distinct from
   the existing `body.present` (which is a font-size bump only).
4. **Diff highlight on recently-changed telemetry.** Cells whose value crossed a soft/hard limit
   in the last 5 s pulse briefly (no audio, just a subtle background flash). Helps the operator
   notice an attack signature mid-conversation without staring at the panel.
5. **Inline asset preview tooltip.** Hovering an asset ID *anywhere in the UI* (effect log, AAR,
   order queue, recovery strip) pops a 3-line SOH micro-card so the operator doesn't need to scroll
   the fleet to context-check.

### 10.B Workflow & ergonomics (4)

6. **Command palette (Cmd-K / Ctrl-K).** A keyboard-driven quick-action menu: "downlink ISR-EO-1",
   "select RED-INSP", "advance 10 min", "fire inject patch_modem". Searches all assets, actions,
   injects, and parameters in one fuzzy box. Sidesteps deep menu navigation for power users.
7. **Order presets / playbooks.** Save a composed order (action + actor + params) as a named
   preset; bring it back with one click. The "downlink-via-GS-PRIME" sequence an operator runs
   eight times an exercise becomes a one-button action.
8. **Multi-asset selection for batch orders.** Shift-click in the fleet rail to select multiple
   sats, then issue the same command to all of them (e.g. `def.set_threat_warning on=true` to a
   whole constellation). Composes naturally with the constellation-aggregation work in §4.
9. **Scene-moment bookmarks.** Pin "this is the H-hour decision point" at a specific sim time and
   jump back via the AAR scrubber later. Distinct from the rewind primitive — bookmarks survive
   across replay branches.

### 10.C Realism & physics (5)

10. **Day/night terminator overlay.** The engine already exposes `sun_lat_deg` / `sun_lon_deg` in
    `SceneView`; the 2D map and globe should draw the actual terminator curve (not just shade the
    far side as the globe does today). Critical for eclipse-aware SoC planning.
11. **Space-weather / solar-storm injects.** A new inject type that globally scales SoC drain,
    raises FSW error rates, and shrinks comms link margin for a configurable window. Real
    geomagnetic storms are a recurring operations driver.
12. **Variable elevation masks (terrain-aware horizon).** Per-site mask tables that capture
    mountains/buildings on a ground station's local horizon. Today every site uses a single mask
    degree value; real sites have masks that vary by azimuth.
13. **Atmospheric refraction near the horizon.** Bend angle correction (~0.5° at the horizon) so
    the apparent elevation at the start/end of a pass is realistic. Small effect but materially
    changes very-low-elevation pass durations.
14. **GNSS spoofing distinct from jamming.** Today the engine collapses both into a "deny" link
    effect. A `spoof` outcome would leave the link UP but with a corrupted position fix — the
    operator sees telemetry stay green while users in the spoofed region report bad PNT.

### 10.D Doctrine & content (3)

15. **Ground-station outage injects.** Cable cut, antenna damage, commercial-power loss —
    temporarily takes a Blue ground station offline. Today the only way to deny a downlink is to
    jam it; real exercises lose stations to maintenance and sabotage too.
16. **Civilian / commercial bystander assets.** Neutral SATCOM customers, commercial GNSS users
    whose telemetry degrades when Red jams Blue's birds. Visualises the collateral cost of
    "harmless reversible" jamming and gives the White Cell a tool to escalate political pressure.
17. **In-browser vignette editor.** Fork an existing vignette, drag a ground station to a new lat/
    lon on the 2D map, tweak parameters, save back. Lowers the bar for instructors to author
    bespoke scenarios without YAML editing.

### 10.E Pedagogy & accessibility (3)

18. **Coachmark / tutorial overlay.** Live coachmarks pointing at UI elements as the trainee runs
    a `learn-*` vignette tutorial. Today the tutorial step script drives the manual + screenshots
    but is invisible in the live UI; coachmarks bridge the gap.
19. **Acronym glossary tooltips.** Hover any acronym (`SOH`, `RPO`, `ISL`, `EUWR`, `Δv`,
    `cn0_dbhz`) for a one-line definition. Trainees stop having to alt-tab to a glossary doc.
20. **AAR CSV / JSON export.** One-click download of the AAR report (decisions, objectives,
    branch comparisons, custody timelines) as machine-readable files for downstream PME analysis
    or paper-write-up. Today the AAR is HTML-only inside the session.

---

This list is the v1 → v1.1+ TODO. When picking an item, prefer:
1. Items in §3 (catalog-verb gaps) — they are small, test-first, and uniformly wired.
2. Items in §5 (posture persistence / recovery deep-links) — small engine refinements with
   immediate pedagogical value.
3. Items in §10.B (command palette, presets, bookmarks) — high UX leverage for low risk.
4. Items in §1 (multiplayer transport) — the highest-architectural-leverage upgrade.

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
