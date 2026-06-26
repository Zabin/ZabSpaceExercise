# R120 — Access Window and Geometry Planning

> **Document ID:** R120
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md)
> **Referenced By:** [R102](R102-space-domain-awareness.md), [R103](R103-satellite-command-and-control.md), [R104](R104-collection-management.md), [R107](R107-ground-segment-operations.md), [R109](R109-sensor-operations.md), [R110](R110-communications.md), [R115](R115-electronic-warfare-in-space-operations.md), [R117](R117-directed-energy-and-kinetic-effects.md), [R118](R118-space-surveillance-networks.md), FS-101, FS-105
> **Produces:** implementation constraints for [`engine/access.py`](../../../spacesim/engine/access.py)
> **Feature Mapping:** FS-101 (Mission Planning), FS-105 (Spacecraft Operations)
> **Related Topics:** [R101](R101-orbital-mechanics-for-operations.md) (Orbital Mechanics — the geometry this topic gates on), MSTR-002 §4 (the
> seam principle — `AccessProvider` as a substitutable interface), MSTR-002 §5 (sub-step the clock)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Access windows are the single mechanism underneath all six gating channels — every other [R100](R100-index.md)
topic that mentions "window" is ultimately deferring to `AccessProvider`. This topic gives the
implementer the actual window-finding algorithm (sample, detect transition, bisect the edge) so a
new channel or fidelity tier is added correctly rather than by approximation.

## 2. Concepts

**Six gating channels plus one non-gating relay channel share one predicate-and-quality pattern.**
`COMMAND_UPLINK`, `TELEMETRY_DOWNLINK`, `SENSOR_OBSERVATION`, `JAM_FOOTPRINT`, `WEAPON_ENGAGEMENT`,
`RPO_PROXIMITY` are the six gating channels (FR-E4); `ISL_LINK` is a seventh, used only for relay
delivery ([R103](R103-satellite-command-and-control.md)'s stored/ISL path), not one of the six doctrinal channels. Every channel resolves to
an `(access_fn, quality_fn)` pair via `AccessProvider._predicate`.

**Windows are found by sampling, then bisecting the edges — not by closed-form geometry.**
`_find_windows` steps a boolean access predicate at `step_s` (refined for short LEO passes via
`_step_for`, down to `min(period)/120` or `/400` for RPO), and on each detected open/close
transition calls `_bisect_edge` to refine the boundary to within `edge_refine_s` (default 1 s). This
sample-then-bisect approach is what lets one algorithm serve every channel's very different
predicate shapes (elevation mask, range threshold, line-of-sight) without per-channel closed-form
solutions.

**Step size adapts to the shortest relevant orbital period, never a fixed global constant.**
`_step_for` computes step size from `min(periods)` of the satellites involved — this is the
concrete mechanism behind MSTR-002 §5's "sub-step the clock" invariant: a naive fixed large step at
high time-acceleration would skip a short LEO pass entirely; per-channel adaptive stepping prevents
that without requiring the whole simulation to run at a uniformly fine step.

**Missing endpoints degrade to "no access," never an exception.** `_endpoints_present` returns
`False` for any actor/target id not present in the `Scene` for that channel's required entity types
— a command planned `via` a station that doesn't exist (or has dropped out of the scene, e.g. a
degraded ground site, [R107](R107-ground-segment-operations.md)) produces an empty window list, not a `KeyError`. This is the concrete
implementation of "denied, not crashed" (MSTR-002 §6) at the access layer specifically.

**Windows are cached per `(actor, target, channel, t0, horizon)` and invalidated on maneuver.**
`AccessProvider.invalidate(actor)` drops cached windows touching a given actor (or all windows if
unspecified) — called after a maneuver changes an orbit, since a stale cached window would describe
geometry that no longer holds. A new state-mutating action that changes orbital geometry must call
`invalidate()`, or windows computed afterward will silently use pre-mutation geometry.

**Quality is a 0..1 proxy, not a guarantee of effect success.** Each predicate pair also returns a
`quality_fn` (elevation/90°, or 1 − range/threshold) used for window peak-quality reporting (e.g. UI
Gantt charts) — quality is a *geometric* goodness proxy, completely separate from the
physically-derived success probabilities [R115](R115-electronic-warfare-in-space-operations.md)-[R117](R117-directed-energy-and-kinetic-effects.md) compute for the effect itself.

## 3. Operational Context

Real mission planning is fundamentally access-window planning: every operational action — command,
collection, jamming, engagement, proximity operations — is only possible during specific,
geometrically-determined intervals that must be found computationally (not read off a table), and a
naive fixed time-step search genuinely does miss short LEO passes in real orbital-mechanics
software, which is exactly the failure mode `_step_for`'s adaptive stepping exists to prevent.

## 4. Implementation Guidance

- **A new access channel must be added through `_predicate`/`_endpoints_present`/`_step_for`**,
  reusing `_find_windows`/`_bisect_edge` — never hand-roll a separate window-search loop for a new
  channel; that would silently regress the adaptive-stepping and edge-bisection guarantees.
- **Any state mutation that changes orbital geometry (a new maneuver type, a new orbit-changing
  effect) must call `AccessProvider.invalidate()`** for the affected actor — omitting this
  reintroduces exactly the stale-window class of bug the cache-invalidation design exists to
  prevent.
- **A higher-fidelity propagator (the anticipated third tier, [R101](R101-orbital-mechanics-for-operations.md) §3) must still satisfy this same
  predicate/window interface** — `AccessProvider` is itself one of the documented seams (MSTR-002
  §4); a new fidelity tier extends `Propagator`, not `AccessProvider`'s algorithm.
- **Treat `quality` as a UI/preview signal only** — never feed window `quality` directly into an
  effect's success probability; that conflation would blur the access-geometry layer with the
  effect-resolution layer [R115](R115-electronic-warfare-in-space-operations.md)-[R117](R117-directed-energy-and-kinetic-effects.md) deliberately keep separate.

## 5. Feature Mapping

FS-101 (Mission Planning) and FS-105 (Spacecraft Operations) both depend on this topic — any new
planning UI surfacing windows must reflect genuine sampled/bisected geometry, not an idealized
continuous-access assumption.

## 6. Related Topics

[R101](R101-orbital-mechanics-for-operations.md) (the orbital state this topic samples), MSTR-002 §4-5 (the seam and sub-stepping principles
this module is the concrete implementation of), and every other [R100](R100-index.md) effect-category topic
([R109](R109-sensor-operations.md)/[R110](R110-communications.md)/[R115](R115-electronic-warfare-in-space-operations.md)/[R117](R117-directed-energy-and-kinetic-effects.md)) which all consume this module's windows as their gating precondition.
