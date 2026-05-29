# Command Planning & Sensor Tasking

This document specifies the two operator workflows the user called out: **planning commands to
send at the next available pass (or rare inter-satellite link), and requesting space- and
ground-based SDA sensor targeting.** Both are expressions of the plan-first principle
(`09-gui-principles.md` P2) and both are gated by the access-window model
(`04-orbital-mechanics-primer.md`).

---

## Part A — Command Planning ("plan now, execute at the window")

### A.1 The mental model
An operator does **not** click "do X" and have it happen. They **compose a command for an
asset**, and the engine **schedules it into the earliest valid window** (or a window the
operator picks). Until that window arrives, the command sits in the queue, fully editable and
cancellable. This mirrors real satellite operations: you build a command load and uplink it on
the next contact.

### A.2 How a command gets to a satellite — the three paths
1. **Ground-station uplink (the normal path).** The command waits for the next pass over one
   of the owning cell's ground stations and uplinks then. The UI shows which station and when.
   If multiple stations are available, the engine picks the earliest (or the operator
   overrides).
2. **Inter-satellite link / crosslink (rare, valued).** If the owning cell has a relay-capable
   asset with a crosslink to the target satellite, a command can be relayed **without waiting
   for a direct ground pass** — potentially much sooner. ISLs are modeled as a scarce, special
   capability (limited assets, limited geometry, possibly limited bandwidth), so using one is a
   real tactical advantage the operator should seek out. The UI surfaces "ISL relay available
   via SAT-RELAY-2 — uplink in 00:01:40" as an alternative to a distant ground pass.
3. **Autonomy / stored program (bounded).** Some commands can be pre-loaded to execute
   onboard at a future time or on a condition (e.g., "begin evasion burn if approached within
   X km"). This lets an operator pre-authorize a time-critical reaction that would otherwise
   miss its window while waiting for a pass — bounded by what the asset's autonomy supports.

### A.3 The planning flow (UI)
1. Select an own asset (3D, map, or roster).
2. The **order panel** shows only commands legal for that asset, each annotated with
   `{resource cost, earliest execution window, delivery path}`.
3. Choose a command and (optionally) a specific future window on the **pass-timeline ribbon**;
   default is earliest valid.
4. The command enters the **command queue** as `PLANNED` with its scheduled execution time and
   delivery path (ground station / ISL / stored).
5. The operator can **chain** commands into a simple plan (e.g., *maneuver at pass 1 → image at
   pass 2 → downlink at pass 3*), seeing the whole sequence on the timeline.
6. At the scheduled window the engine validates again (still legal? still in view? resources
   still available?) and either executes (→ `EXECUTED`) or fails gracefully with a reason
   (→ `FAILED: lost window`), notifying the operator.

### A.4 Command lifecycle / states
```
DRAFT → PLANNED (queued, has scheduled window & path) → [editable/cancellable]
      → UPLINKING (window active) → EXECUTED
                                  ↘ FAILED {reason}   (window missed, resource gone, ROE change)
      → CANCELLED (operator pulled it before uplink)
```

### A.5 What the engine checks before accepting/executing a command
- **Ownership** — the cell owns the asset.
- **Window** — a valid delivery window (ground pass, ISL, or stored-program trigger) exists.
- **Resources** — fuel/delta-v, power, ammo, payload availability.
- **ROE / authorities** — the action is permitted under current rules (kinetic on/off, etc.).
- **Custody/track gate** — for an action *against* another object, the cell must hold a track
  of sufficient quality (you can't strike or precisely image what you can't localize) — which
  is exactly what Part B provides.

### A.6 Data shape (see `04-data-model.md` for the canonical schema)
```yaml
planned_command:
  id:
  asset_ref:
  verb:            # maneuver | image | downlink | jam | rpo_approach | engage | posture_change ...
  params: {...}    # burn vector, target_ref, frequency, keep-out distance, etc.
  delivery:
    path: ground_uplink | isl_relay | stored_program
    via: STATION-BRAVO | SAT-RELAY-2 | onboard
    scheduled_window: {start_utc, end_utc}
  state: PLANNED
  depends_on: [prior_command_id]   # optional chaining
  notes:
```

---

## Part B — SDA Sensor Tasking ("request targeting / collection")

### B.1 The mental model
The operator does not *know* the sky; they **own a finite set of SDA sensors** (space- and
ground-based) and must **task them** to detect, maintain custody of, or characterize objects.
Sensors are scarce, have geometry constraints, and can only do one thing at a time. Tasking is
itself a planning problem against access windows — exactly parallel to commanding a satellite.

### B.2 Sensor types (templates in `04-data-model.md`)
- **Ground-based radar** — tracks LEO/MEO; weather-independent; bounded by horizon/elevation
  and a search-vs-track time budget.
- **Ground-based optical** — tracks MEO/GEO well; **needs target sunlit and site in darkness**
  and clear sky (space-weather/cloud parameter); excellent for GEO custody.
- **Space-based SDA / inspector** — on-orbit sensors (e.g., a GEO inspector) that can observe
  objects unreachable from the ground, including close characterization via RPO; itself
  constrained by its orbit and tasking time.
- **Shared/coalition feeds** — partner SDA contributing tracks to the cell's catalog
  (modeled as periodic external track updates, lower control but extra coverage — the NATO/
  allied flavor from `01-doctrine-western.md`).

### B.3 What a tasking request can ask for
- **Search** a region/regime for new/unknown objects ("survey GEO between longitudes X–Y").
- **Track / maintain custody** of a specific object (keep its uncertainty volume small).
- **Characterize** an object (resolve type/payload/intent — needs a capable sensor and a good
  geometry pass; this is how a "?" becomes a classified Red ASAT).
- **Cue** — hand a track from one sensor to another (radar detects → optical characterizes).

### B.4 The tasking flow (UI)
1. From the 3D/2D view, select an object (or draw a search volume) → **"Task sensor."**
2. The tool shows **which of the cell's sensors can service it and when** — each with its next
   viable collection window, expected quality, and what it will yield (detect vs. track vs.
   characterize). Unavailable sensors explain why ("optical: target in daylight," "radar:
   below horizon until 21:10Z").
3. Operator assigns the task to a sensor (and priority). It enters a **collection plan**
   analogous to the command queue.
4. At the collection window the sensor reports: a new/updated `Track` with reduced uncertainty
   and possibly improved characterization. The 3D viewer's uncertainty volume visibly shrinks.
5. **Contention:** a sensor tasked on A cannot simultaneously service B; the operator must
   prioritize. Losing custody of one object to gain another is a deliberate, visible trade —
   a key teaching moment, especially against the "suppression of counterspace targeting"
   objective where Red is *trying* to make Blue lose custody.

### B.5 Collection request data shape
```yaml
collection_task:
  id:
  sensor_ref:          # or "auto" to let the tool pick best available
  intent: search | track | characterize | cue
  target_ref: | search_volume: {regime, lon/lat/alt bounds}
  priority: routine | priority | immediate
  scheduled_window: {start_utc, end_utc}   # computed from sensor geometry
  expected_yield: detect | track_update | characterization
  state: PLANNED | COLLECTING | REPORTED | FAILED {reason}
```

### B.6 How tasking feeds everything else
- Tasking updates the cell's `TrackCatalog`, which is the **only** thing the 3D/2D viewer
  draws (`10-sda-3d-viewer.md`) and the **only** basis for the custody/track gate that
  Part A §A.5 checks before an engagement.
- This closes the central loop:
  **task sensor → gain custody/characterization → that unlocks a legal command/engagement →
  execute at the next window.**
- It also creates the defender's nightmare and the attacker's aim: **break the loop** — deny
  custody (deception, dispersal, killing/dazzling the sensor) so the opponent can't earn the
  track quality needed to act.

---

## C — Why both workflows share one pattern
Commanding a satellite and tasking a sensor are the *same kind of action*: pick an asset,
express intent, let the engine schedule it into the next viable window against real geometry,
edit/cancel until it fires. Implement them on a **common "planned activity" scheduler** with
two activity kinds (`command`, `collection`) so the UI, the queue, the timeline ribbon, undo,
and White-Cell time-travel all work identically for both. This is the unifying abstraction
Claude Code should build once.
