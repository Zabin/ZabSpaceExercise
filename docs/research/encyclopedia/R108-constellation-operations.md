# R108 — Constellation Operations

> **Document ID:** R108
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R106](R106-mission-operations.md)
> **Referenced By:** FS-105, [R316](R316-joint-and-combined-operations.md)
> **Produces:** implementation constraints for any future constellation-aggregation feature
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R106](R106-mission-operations.md) (Mission Operations), `docs/FUTURE-WORK.md` (constellation aggregation, deferred)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 0 (Tier C only — see §3 Sources)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The simulator deliberately models constellations as a small number of individually-operated
satellites rather than an aggregated fleet object. This topic exists so a future feature touching
multi-satellite coordination understands why that choice was made and doesn't silently reintroduce
fleet-level abstractions the engine doesn't have.

## 2. Scope

Covers: why the simulator deliberately omits a fleet-level constellation aggregation primitive, and
what the clock-lag watchdog actually gates instead. Does **not** cover: the per-satellite operations
loop constellation operations compose from ([R106](R106-mission-operations.md)), or any future aggregation feature's design
(tracked only as a `docs/FUTURE-WORK.md` deferred item, not specified here).

## 3. Concepts

**Constellations are capped at ≤3 satellites by sizing guideline, each operated individually.**
CLAUDE.md's "Key facts" fixes this as the soft guideline for the sample vignette library: there is
no engine-enforced cap (a user vignette may scale up), but the *operational model* — every satellite
is its own `Asset` with its own `BusState`, own orders, own custody — does not change with
constellation size. A "constellation" in this simulator is a labeling/grouping convenience for the
vignette author and operator, not a distinct data structure.

**No fleet-level aggregation primitive exists yet.** There is no "task the constellation" or
"constellation health" object; an operator commanding three satellites in a constellation issues
three separate orders through the same `OrderSystem` each individual satellite would use alone.
Aggregation (a single fleet-level dashboard rollup, batch tasking) is a documented, deferred
capability (`docs/FUTURE-WORK.md`), not a missing bug.

**The clock-lag watchdog is the actual scaling constraint, not a constellation-size cap.**
`SessionManager._record_catch_up_lag` warns White Cell when the hardware can't keep up with the
~24-satellite soft guideline for typical sessions — this is a performance signal about total asset
count across the force, not a constellation-specific gate.

## 4. Operational Context

*Single source (vendor/analyst).* Real constellation operations (e.g. a GPS or remote-sensing
constellation) genuinely do use fleet-level tools — batch tasking, constellation-wide health
dashboards, and automated prioritized scheduling across the fleet ([Cognitive Space, "Satellite
Constellation Management: Challenges and Solutions"](https://www.cognitivespace.com/blog/satellite-constellation-management/)
([Wayback](https://web.archive.org/web/2026/https://www.cognitivespace.com/blog/satellite-constellation-management/));
[a.i. solutions, "Managing Constellations: A Flight Dynamics Perspective"](https://ai-solutions.com/newsroom/managing-constellations-a-flight-dynamics-perspective/)
([Wayback](https://web.archive.org/web/2026/https://ai-solutions.com/newsroom/managing-constellations-a-flight-dynamics-perspective/)))
— that this simulator does not yet model. These are vendor/analyst sources, not a doctrine or
government Tier-A reference; the claim is corroborated across two independent vendor sources but
neither is a primary operator disclosure. The ≤3-sat, individually-operated guideline is a
deliberate v1 scoping choice to keep operator cognitive load and implementation surface bounded
while still letting a vignette author depict a small constellation's *operational character* (e.g.
plane-spacing, revisit cadence) through ordinary per-satellite orders.

### Sources

- *Cognitive Space, "Satellite Constellation Management: Challenges and Solutions"* — [live](https://www.cognitivespace.com/blog/satellite-constellation-management/)
  · [snapshot](https://web.archive.org/web/2026/https://www.cognitivespace.com/blog/satellite-constellation-management/)
  · accessed 2026-06-27.
- *a.i. solutions, "Managing Constellations: A Flight Dynamics Perspective"* — [live](https://ai-solutions.com/newsroom/managing-constellations-a-flight-dynamics-perspective/)
  · [snapshot](https://web.archive.org/web/2026/https://ai-solutions.com/newsroom/managing-constellations-a-flight-dynamics-perspective/)
  · accessed 2026-06-27.

## 5. Implementation Guidance

- **Do not invent a parallel "fleet" or "constellation" engine entity** to implement a
  constellation-flavored feature — compose it from existing per-`Asset` primitives unless and until
  a real aggregation Implementation Package is authorized.
- **If you pick up constellation aggregation from FUTURE-WORK**, scope it as its own Implementation
  Package (batch order issuance, rollup SOH view) rather than smuggling fleet-level state into
  `Asset` or `BusState`, which are deliberately single-satellite models.
- **A vignette depicting a constellation should use ordinary multiple `Asset` entries**, not a new
  schema construct — this is consistent with content-is-data (MSTR-002 invariant 6): constellation
  "shape" is authored data, not new engine logic.
- **Treat the clock-lag watchdog, not a constellation cap, as the authoritative scaling signal**
  when deciding whether a vignette's asset count is too large for typical hardware.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the consumer for any constellation-flavored vignette; a future
fleet-aggregation feature would need its own FS entry, not a silent extension of FS-105.

## 7. Related Topics

[R106](R106-mission-operations.md) (Mission Operations — the per-satellite loop constellation operations compose from),
`docs/FUTURE-WORK.md` (the authoritative deferred-work entry for constellation aggregation).
