# R125 — Flight Operations Team Roles and Console Positions

> **Document ID:** R125
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R106](R106-mission-operations.md)
> **Referenced By:** FS-105, FS-107
> **Produces:** implementation constraints for the White/Blue/Red cell model (`session/api.py`, `session/inprocess.py`) and [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js) (subsystem drill-down)
> **Feature Mapping:** FS-105 (Spacecraft Operations), FS-107 (Operator Console)
> **Related Topics:** [R106](R106-mission-operations.md) (Mission Operations — the plan/task/execute/assess loop these roles execute),
> [R123](R123-command-and-telemetry-console-software.md) (Console Software — the subsystem-grouped UI these roles map onto)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 2

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`spacesim` lets one human operate an entire cell's fleet through a single console, but the
subsystem drill-down's EPS/ADCS/CDH/TCS/comms/propulsion card structure ([R123](R123-command-and-telemetry-console-software.md)) is a direct,
collapsed echo of a real flight operations team's console-position structure. This topic gives the
implementer the real multi-seat organization so a future multiplayer "split the cell across several
human operators" feature (one person per subsystem console) extends a real organizational pattern
rather than inventing role boundaries.

## 2. Scope

Covers: the Flight Director / subsystem-console-operator division of responsibility and shift
handover as a real organizational pattern. Does **not** cover: the plan/task/execute/assess loop
each role executes ([R106](R106-mission-operations.md)), or the console software/verb catalog those roles operate
([R123](R123-command-and-telemetry-console-software.md)).

## 3. Concepts

**A Flight Director has overall authority; subsystem controllers have subsystem authority.** NASA's
flight control room model is "leads the flight controllers, monitors the activities of a team of
flight controllers, and has overall responsibility for success and safety," while each console
position controller is "an expert in a specific area" who makes recommendations to the Flight
Director rather than acting unilaterally on cross-subsystem decisions
([Wikipedia, summarizing NASA flight control room organization, *List of NASA's flight control
positions*](https://en.wikipedia.org/wiki/List_of_NASA%27s_flight_control_positions)
([Wayback](https://web.archive.org/web/2026/https://en.wikipedia.org/wiki/List_of_NASA%27s_flight_control_positions))) —
the structural analog to `spacesim`'s White Cell (overall session authority: pause/resume,
injects, AAR) sitting above Blue/Red cell operators who each command their own fleet, and within a
cell, a subsystem console operator's authority would be scoped to one card (EPS, ADCS, etc.), not
the whole bus.

**Console positions are named, fixed, and subsystem-scoped — not ad hoc.** Each console in the
Flight Control Room "is dedicated to a specific area of expertise" and labeled with a fixed
abbreviation used for terse, unambiguous voice-loop communication
(*op. cit.*) — directly analogous to `app.js`'s fixed per-subsystem drill-down cards
(EPS/ADCS/CDH/TCS/comms/propulsion), each scoped to that subsystem's verbs via `verbsForSubsystem`,
rather than one operator screen mixing all subsystems' commands together.

**New controllers train on a back-room/training position before taking a front-room seat.**
Shuttle-era flight controller training used dedicated training positions to introduce operations
principles to new hires, who would graduate to front control room (FCR) seats only once certified,
at which point they were "responsible for appropriately integrating their systems' requirements
with other system operators"
([NASA, *A Review of Three Decades of Flight Controller Training*, NTRS 20110014997](https://ntrs.nasa.gov/api/citations/20110014997/downloads/20110014997.pdf)
([Wayback](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20110014997/downloads/20110014997.pdf))) —
the real-world precedent for treating "integrating across subsystems" as a distinct, higher
competency than "operating one subsystem console," which a future multi-seat `spacesim` feature
should preserve rather than flattening every seat to identical authority.

**Console operators work in continuous shifts with a formal handover, not a hard session
boundary.** The same FCR model staffs console positions "24/7... representing various disciplines
responsible for carrying out the mission" (*op. cit.*, Wikipedia), implying a shift-relief process
that hands off state (current configuration, open issues, pending actions) rather than restarting
context — the real-world precedent for any future `spacesim` feature letting one human operator
hand a live session to another mid-exercise without White Cell needing to pause and re-brief from
scratch.

### Sources

- *Wikipedia, List of NASA's flight control positions* — [live](https://en.wikipedia.org/wiki/List_of_NASA%27s_flight_control_positions)
  · [snapshot](https://web.archive.org/web/2026/https://en.wikipedia.org/wiki/List_of_NASA%27s_flight_control_positions)
  · accessed 2026-06-27.
- *NASA, A Review of Three Decades of Flight Controller Training, NTRS 20110014997* —
  [live](https://ntrs.nasa.gov/api/citations/20110014997/downloads/20110014997.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20110014997/downloads/20110014997.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

Real spaceflight operations have never been single-operator affairs — even a small, uncrewed
mission's ground team divides authority across a Flight Director and subsystem specialists, each
accountable for their domain's health and recommendations, with the Flight Director synthesizing
across them for any decision that crosses subsystem boundaries. `spacesim`'s current model
collapses this onto one operator per cell because the v1 PME use case (a small classroom exercise)
doesn't need multi-seat fidelity yet, but the subsystem-card UI structure already mirrors the real
console-position boundaries, making a future multi-seat split a UI-authority change rather than a
data-model change.

## 5. Implementation Guidance

- **A future multi-seat feature should scope a "console operator" role to one subsystem card's
  verbs**, mirroring `verbsForSubsystem`'s existing grouping — don't invent a different subsystem
  boundary than the one the UI already uses.
- **A cross-subsystem decision (e.g. choosing to shed EPS load to protect a maneuver) should remain
  the cell's single point of authority** (today: the one human operator; in a future multi-seat
  model: a Flight-Director-equivalent role) — don't let a subsystem-scoped seat issue commands
  outside its own card without that authority.
- **If a shift-handover feature is ever built, it should hand off live session state (not restart
  it)** — consistent with the real shift-relief pattern, and consistent with `spacesim`'s existing
  save/resume session model rather than a new ad hoc mechanism.
- **Don't conflate this role model with the White/Blue/Red cell split** — White/Blue/Red is a
  fog-of-war/faction boundary (`CellController`), while Flight-Director-vs-subsystem-console is an
  *intra-cell* authority boundary; a multi-seat feature needs both, not one standing in for the
  other.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) and FS-107 (Operator Console) are the indirect consumers — no
current feature requires multi-seat console splitting, but any future one should be grounded
against this topic rather than inventing role boundaries from scratch.

## 7. Related Topics

[R106](R106-mission-operations.md) (the plan/task/execute/assess loop these roles execute), [R123](R123-command-and-telemetry-console-software.md) (the
subsystem-grouped console UI these roles map onto).
