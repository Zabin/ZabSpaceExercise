# White Cell Controls — Vignette Selection, Time Travel, Injects

The White Cell is the facilitator. This document specifies the control surface: selecting and
tuning vignettes, controlling time (the user's explicit requirement: real-time flow with
fast-forward, rewind, and undo), and injecting events. These are powers **only** White Cell has.

## 1. Vignette selection & tuning (pre-game and live)

1. **Browse** the vignette library — 19 scenarios in `spacesim/content/vignettes/` covering the
   canonical 8 numbered, the training-basics onboarding, and the four-track expansion. Each
   shows title, domains, learning objectives, and estimated duration.
2. **Select** a vignette → the engine loads its data file (forces, objectives, parameters,
   injects).
3. **Tune parameters** — the UI renders one control per `parameter` (enum→dropdown, int→slider/
   stepper, bool→toggle, multiselect→checkboxes, time/duration→pickers). Defaults are pre-filled
   so a vignette is runnable untouched. Tooltips show each parameter's `affects` text.
4. **Edit forces (optional)** — add/remove/rename assets, including **adding real named
   satellites by TLE** (paste a TLE; the engine validates and places it). Fictional assets get
   Keplerian elements via a simple editor.
5. **Start** — the SessionManager instantiates the WorldState, takes snapshot 0, and begins the
   clock (paused, at the default multiplier).

**Live tuning:** most parameters can be changed mid-session via `modify_parameter`; the change is
logged as a `white_control` event so it appears in the replay and AAR. (Some structural
parameters — e.g., initial force counts — are pre-game only; the schema marks these
`live_editable: false`.)

### 1.1 Safe-mode difficulty dials (live-tunable)
Safe mode is a reversible "off the board" effect, so its balance is **White-Cell-controlled**
rather than baked in (full spec: `12-safe-mode-loop.md`). Five dials appear in the parameter
panel and may be changed mid-exercise to raise or lower pressure on the defender:

| Dial | Options | Default | Effect |
|---|---|---|---|
| `safe_mode_susceptibility` | robust / realistic / fragile | realistic | How easily cyber/EW/bus-stress induces safe mode (master probability multiplier). |
| `safe_mode_recovery_difficulty` | quick / realistic / punishing | realistic | Passes/retries needed to recover (quick = 1 pass; punishing = multi-pass). |
| `safe_mode_detection_aid` | realistic / coached / fog | realistic | coached = early explicit alert; fog = symptom-only detection. |
| `safe_mode_attack_enabled` | bool | true | Whether safe mode may be *attack*-induced at all this vignette. |
| `safe_mode_root_cause_persists` | bool | true | If true, recovery re-safes unless the defender removes the cause (patch vuln / kill jammer). |

Defender preparation (`blue_passive_defenses`, cyber posture) interacts with these: hardening
lowers susceptibility, threat-warning speeds detection, patching prevents re-safing, and
dispersal/proliferation reduces the cost of any single satellite being safed.

## 2. Time controls

The clock is White Cell's instrument. All controls are logged.

| Control | Behavior |
|---|---|
| **Play / Pause** | Start/stop advancing sim time. Paused is the default at load. |
| **Time multiplier** | 1× (real time) up to 600× (and custom). Fast-forward = high multiplier; the engine sub-steps so no window/event is skipped. |
| **Step** | Advance a fixed sim interval then pause (e.g., +5 min) — useful for deliberate AAR-style walkthroughs. |
| **Rewind to T** | Jump sim time *backward* to T. Engine loads nearest snapshot ≤ T and replays the event log to T (exact, by determinism). The session continues from T; events after T are moved to a **branch** (not destroyed). |
| **Undo last action(s)** | Remove the most recent action(s) from the active timeline and re-derive state from the nearest prior snapshot. See semantics below. |
| **Branch / What-if** | After a rewind, continuing with different actions creates a named branch; White Cell can switch between branches for comparison. |
| **Jump to event** | Scrub to any event in the log (great for AAR). |

### Rewind/undo semantics (be precise here)
Because the core is deterministic over `(snapshot, eventlog, seed)`:
- **Rewind to T** is always exact and safe: it never "loses" data — post-T events are retained on
  a branch so White Cell can fast-forward back if desired.
- **Undo last action** drops the last *player/inject* action(s) and recomputes. Because effects
  may have cascaded (a kinetic strike spawned debris that damaged a third asset), undo works by
  **truncating the event log and re-deriving**, not by trying to reverse side effects
  individually. This guarantees a consistent world rather than a half-reverted one.
- Undo and rewind are implemented with the **same mechanism** (truncate/branch + replay); "undo
  last action" is just "rewind to just before the last action."
- White Cell can **lock** a point ("commit") to prevent accidental rewind past a teaching
  milestone.

> Implementation note: keep snapshots frequent enough that replay-to-T is fast at the session's
> object count (every few sim-minutes is plenty at moderate fidelity). Determinism tests
> (`03-simulation-engine.md` §6) are what make all of this trustworthy.

## 3. Injects (driving the scenario)

White Cell fires events to steer the exercise. Injects may be **scripted** (in the vignette,
time- or condition-triggered) or **manual** (fired live from the control panel).

Inject effect types the engine supports:
| Effect type | Use |
|---|---|
| `reveal_asset` | Make an asset visible to a cell (OSINT leak, intel tip) |
| `degrade_asset` / `fail_ground_station` | Impose a malfunction or attack effect |
| `spawn_asset` | Reinforcements, a new threat, a commercial actor |
| `change_roe` | Tighten/loosen what a side may do (escalation control) |
| `inject_debris` | Create a debris hazard region |
| `patch_cyber_vuln` | Close a cyber access vector (defender success) |
| `message` | Send text/intel to specified cells |
| `modify_parameter` | Live parameter change |
| `political_consequence` | Coalition/UN/economic fallout (escalation scoring) |

The manual inject panel lets White Cell pick an effect type, target, and recipients, then fire
immediately or schedule for a sim time. Every inject is logged.

## 4. Monitoring & scoring (facilitator dashboard)
- **Both cells' filtered views** side by side, plus god-view ground truth.
- **Objective & escalation tracker** — progress on each side's objectives and current rung on the
  escalation ladder; flags debris-generating or unattributed-but-overt actions.
- **Resource readouts** — fuel/power/ammo per asset; custody confidence on key tracks.
- **Event log / replay scrubber** — the spine of the **after-action review**: scrub the whole
  session, jump to decision points, branch to explore "what if they'd done X."

## 5. Session lifecycle
`Load vignette → tune → start (paused) → run (play/ff, inject, rewind/undo as needed) → pause for
teaching points → resume → end → AAR replay → save`. Saved sessions store the full
`{initial_state, seed, snapshots, eventlog, branches}` so any session can be reopened and
replayed exactly.
