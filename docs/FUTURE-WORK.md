# Future work

Consolidated list of capabilities **not** included in v1 — moved here from the now-merged
`docs/OPERATOR-UI-DESIGN.md` (UI plan) and `memory.md`'s rolling "still open" notes. The
v1 spec lives in `00-BUILD-SPECIFICATION.md` (with the operator console in §16); this file is
the single source of truth for "what's deliberately not built."

Items are grouped by area, each with a short rationale and pointers into the code or research so
a future implementer can pick any one up without scanning history. Anything not listed here is
either implemented or covered by an existing in-scope ticket.

## 1. Multiplayer & networking (M7 seam, formerly Phase 8)

- **LAN multiplayer cell separation.** The session layer already routes every interaction through
  a `SessionAPI` and the engine is UI-agnostic; the seam exists but is exercised only in-process.
  Swapping `InProcessSession` for a WebSocket transport finishes P8 from the roadmap.
- **Push deltas instead of polling.** `get_eventlog(since_seq)` already expresses the contract;
  the front end currently re-fetches view/scene/telemetry per tick. A push channel is the natural
  upgrade once the transport above lands.
- **`Order` as a serializable transport message.** Today `Order` is an engine dataclass passed
  through the in-process boundary. Moving it to pydantic at the API surface (with the engine
  dataclass kept internal) is a pre-req for the network transport.

## 2. Orbital / effects fidelity

- **High-fidelity propagator drop-in.** The `Propagator` seam (`engine/propagator.py`) is in place;
  swapping the Kepler+J2 fictional propagator for a stronger model is a v1.1 task with no
  architectural impact. Skyfield is already a dev dependency for the regression check.
- **Solar-radiation pressure, atmospheric drag**, third-body luni-solar effects. Out of scope for
  v1 (moderate fidelity); easy follow-ons behind the seam.
- **Conjunction screening + `prop.collision_avoid`**. The catalog verb is present but not wired to
  a screening service.

## 3. Catalog verb gaps (extends `buscommands.apply_command`)

The implemented verbs are listed in `00-BUILD-SPECIFICATION.md` §16.11. Remaining catalog verbs
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

## 4. UI strategic items (out of v1 scope, per `00-BUILD-SPECIFICATION.md` §3.2)

- **Constellation aggregation (v2).** Manage ≥3 sats as a group from a single panel. The current
  per-asset drill-down is the right unit for v1's ≤24-sat / ≤3-per-constellation cap.
- **Formal APP-6-adapted space-symbology pack.** Today's marker/colour system is consistent
  across the 2D map and 3D globe but not formally specified; a future pack would standardize
  shapes per object type for joint-/coalition-use credibility.
- **Δv "years of life" panel.** Dedicated propulsion sub-tab spelled out by
  `14-delta-v-economy.md` — the data exists in `AssetResources.delta_v_ms`, the panel does not.
- **Full CesiumJS 3D globe.** The v1.1 follow-on referenced in `00-BUILD-SPECIFICATION.md` §10 M5. The
  self-contained orthographic globe (`ui_web/static/globe.js`) covers the v1 requirement; a
  Cesium variant adds higher-fidelity rendering for projector / White-Cell display.
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

`00-BUILD-SPECIFICATION.md` declares ≤24 satellites for v1 with a hard ceiling of 48, and
constellations ≤3 sats. The caps are documented but **not enforced at vignette load**; future
work: validate caps in `content/vignette.build_world` with a clear rejection.

## 7. Mock Space Surveillance Network (SSN) — ✅ implemented

The per-cell mock SSN is fully implemented per `00-BUILD-SPECIFICATION.md` §17 (engine + session +
API + UI + V2/V7/V8 vignette opt-in + acceptance tests; quality model and save/resume included).
Remaining items not carried into v1:

- **Cost / collection-budget** for priority/immediate (force triage). Recommended as a later
  balance dial.
- **Commercial / third-party feeds** — a neutral commercial provider both cells can buy from
  (extends the per-cell model).
- **Auto-cueing organic → SSN** — let an organic detection auto-cue an SSN characterize request.

## 8. UI polish / minor

- **Browser-GUI verification harness.** The UI is currently unverified-headless; the test suite
  pins every backend path and Playwright-driven smoke runs verify wiring end-to-end, but a human
  has not exercised the visuals.
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

---

This list is the v1 → v1.1+ TODO. When picking an item, prefer:
1. Items in §3 (catalog-verb gaps) — they are small, test-first, and uniformly wired.
2. Items in §5 (posture persistence / recovery deep-links) — small engine refinements with
   immediate pedagogical value.
3. Items in §1 (multiplayer transport) — the highest-architectural-leverage upgrade.

Anything else is best gated by user demand or a paying engagement.
