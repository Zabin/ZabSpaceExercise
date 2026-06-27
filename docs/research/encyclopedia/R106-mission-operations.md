# R106 — Mission Operations

> **Document ID:** R106
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](R103-satellite-command-and-control.md)
> **Referenced By:** [R108](R108-constellation-operations.md), [R125](R125-flight-operations-team-roles.md), FS-101, FS-105, FS-106
> **Produces:** implementation constraints for the operator-console workflow (`ui_web/static/app.js`, [`session/api.py`](../../../spacesim/session/api.py))
> **Feature Mapping:** FS-101 (Mission Planning), FS-105 (Spacecraft Operations), FS-106 (White Cell Dashboard)
> **Related Topics:** [R103](R103-satellite-command-and-control.md) (Satellite C2), MSTR-003 §2 (plan-execute as the unit of learning), DOM-001 (Training Framework)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Mission operations is the operator's recurring day-to-day loop — plan, task, execute, assess —
that everything else in the simulator (orders, custody, telemetry, AAR) exists to support. This
topic gives an implementer the shape of that loop so a new UI surface or workflow feature fits the
existing operational rhythm instead of inventing a parallel one.

## 2. Scope

Covers: the plan/task/execute/assess operator loop and how mission-brief/tutorial/coaching content
anchors it. Does **not** cover: the C2 mechanics the task beat drives ([R103](R103-satellite-command-and-control.md)), or
per-subsystem operational detail (R107-R114).

## 3. Concepts

**The operations loop has four recurring beats.** Real satellite mission operations centers run
continuously on this cadence — mission planning determines tasking based on health constraints and
access windows, command-and-control encodes/executes commands as "the engine of the ops center,"
and the operations team continuously monitors telemetry to assess spacecraft health
([NASA GSFC Mission Operations overview](https://solc.gsfc.nasa.gov/modules/missionops/mainMenu_textOnly.php)
([Wayback](https://web.archive.org/web/2026/https://solc.gsfc.nasa.gov/modules/missionops/mainMenu_textOnly.php));
[The Aerospace Corporation, *Mission Assurance Practices for Satellite Operations*, TOR-2013-00293](https://aerospace.org/sites/default/files/maiw/TOR-2013-00293.pdf)
([Wayback](https://web.archive.org/web/2026/https://aerospace.org/sites/default/files/maiw/TOR-2013-00293.pdf))).
The simulator's loop compresses this real cadence into four beats: (1) *Plan* — the operator reviews current SOH,
custody, and access-window forecasts and decides what to attempt next; `dry_run()` ([R103](R103-satellite-command-and-control.md)) supports
this beat without committing anything. (2) *Task* — the operator issues orders (commands, sensor
tasking, maneuvers) that queue for their windows. (3) *Execute* — the deterministic event loop fires
queued orders at their windows; the operator cannot accelerate this. (4) *Assess* — fresh telemetry,
updated tracks, and effect-log entries arrive and feed the next planning beat. This loop, not any
single screen, is "mission operations."

**The mission brief anchors the loop in intent.** Every vignette's per-cell `intro_brief` (situation,
mission, friendly forces, threat picture, deadline, ROE note, success criteria) is the operator's
standing orders for the session — the planning beat is always planning *against* this brief, not
against an abstract sandbox.

**Tutorials encode the loop as a worked example.** The 8 canonical vignettes' per-cell `tutorial`
block walks the plan→task→execute→assess loop move by move for a specific objective, and is the
concrete reference for "what does a normal operating cycle look like here."

**Coaching notes are loop-aware interjections, not a separate channel.** `Vignette.coaching`
entries fire `{at_sim_t?, cell, title, body}` — timed to land at a specific point in an ongoing
loop, reinforcing or correcting a planning decision while it's still actionable, not after the fact.

### Sources

- *NASA GSFC, Mission Operations overview* — [live](https://solc.gsfc.nasa.gov/modules/missionops/mainMenu_textOnly.php)
  · [snapshot](https://web.archive.org/web/2026/https://solc.gsfc.nasa.gov/modules/missionops/mainMenu_textOnly.php)
  · accessed 2026-06-27.
- *The Aerospace Corporation, Mission Assurance Practices for Satellite Operations, TOR-2013-00293* — [live](https://aerospace.org/sites/default/files/maiw/TOR-2013-00293.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.org/sites/default/files/maiw/TOR-2013-00293.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

Real space operations centers run exactly this loop on a duty-shift cadence: a controller plans
against the day's pass schedule, tasks commands/collections for the windows ahead, watches them
execute, and assesses the resulting telemetry before the next planning cycle — the simulator's loop
is a compressed, replayable version of that real rhythm, not an invented game mechanic.

## 5. Implementation Guidance

- **A new operator-facing feature should declare which beat(s) of the loop it serves** (planning
  preview, tasking, execution visibility, or assessment) — a feature that doesn't fit any beat is
  probably solving the wrong problem.
- **Never let a UI feature collapse plan and execute into one click** — this is the plan-first
  invariant (MSTR-002 §2 invariant 4) applied operationally: every "do X now" feature must still
  go through `OrderSystem`'s window-gated pipeline.
- **New mission-brief or tutorial content is vignette data, not code** (MSTR-002 invariant 6) — a
  feature that needs new brief fields should extend the vignette schema, not hardcode brief text.
- **Coaching-note timing should be tied to `at_sim_t` or an event, not wall-clock** — consistent
  with the determinism invariant (MSTR-002 §1).

## 6. Feature Mapping

FS-101 (Mission Planning) and FS-105 (Spacecraft Operations) are the direct consumers of the
plan/task beats; FS-106 (White Cell Dashboard) is the consumer of the assess beat from White's
cross-cell vantage point.

## 7. Related Topics

[R103](R103-satellite-command-and-control.md) (Satellite C2 — the mechanics the "task" beat drives), [R125](R125-flight-operations-team-roles.md) (Flight Operations Team
Roles — the real multi-seat organization this single-operator loop compresses), MSTR-003 §2 (the
pedagogical argument for why plan-execute is the right unit of learning), DOM-001 (Training
Framework — how the loop maps to training objectives).
