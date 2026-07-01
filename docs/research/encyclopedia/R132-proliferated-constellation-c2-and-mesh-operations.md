# R132 — Proliferated-Constellation C2 and Mesh Operations

> **Document ID:** R132
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R108](R108-constellation-operations.md), [R118](R118-space-surveillance-networks.md)
> **Referenced By:** —
> **Produces:** research grounding for any future constellation-aggregation Implementation Package
> (deferred item, `docs/FUTURE-WORK.md` §4)
> **Feature Mapping:** none yet — research-first per this topic's own scope (§2); the eventual
> consumer is a not-yet-authorized aggregation feature, not FS-105 directly
> **Related Topics:** [R108](R108-constellation-operations.md) (Constellation Operations — the ≤3-sat
> individually-operated model this topic explains what changes beyond), [R118](R118-space-surveillance-networks.md)
> (Space Surveillance Networks — request-based tasking at scale), [R104](R104-collection-management.md)
> (Collection Management — tasking contention, which proliferated scale multiplies), ADR-0019
> (sizing guideline, not engine cap), `docs/FUTURE-WORK.md` §4 (constellation aggregation, deferred)
> **Last Reviewed:** 2026-07-01
> **Primary Sources Consulted:** 2

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Identified as **GAP-10** in the Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3,
named as the review's flagship correction to the fleet-scale assumption in
recommendation R13): [R108](R108-constellation-operations.md) documents *why* the simulator
deliberately caps constellations at ≤3 individually-operated satellites (ADR-0019) — a v1 scoping
choice, not a domain fact. This topic supplies the missing other half: what actually changes,
operationally, at real proliferated scale (tens to hundreds of satellites per architecture), so
that if/when constellation aggregation (`docs/FUTURE-WORK.md` §4) is authorized, it is designed
against the real operator's unit of command rather than a scaled-up version of the current
per-asset drill-down. Per this topic's own scope, **it does not design that feature** — it is
research-first grounding, consistent with MSTR-007 §2's "give the implementer domain understanding"
purpose applied *before* the feature exists.

## 2. Scope

Covers: what changes about C2, tasking, and health-monitoring workload when constellation size
moves from single-digits to hundreds; the real operator's unit-of-command shift from
individual-satellite to layer/mesh; inter-satellite mesh routing as an operational (not just
technical) concept; and exception-based health monitoring as the real answer to per-asset
drill-down not scaling. Does **not** cover: the ≤3-sat, individually-operated model itself
([R108](R108-constellation-operations.md), unchanged and still the correct model below that
threshold), the design of any future aggregation feature (explicitly out of scope — tracked only as
a `docs/FUTURE-WORK.md` deferred item), or SSN request-based tasking mechanics
([R118](R118-space-surveillance-networks.md), which this topic's tasking-workload discussion draws
on but does not restate).

## 3. Concepts

**Proliferated architectures are now a named, funded reality, not a speculative future concept.**
The US Space Development Agency's Proliferated Warfighter Space Architecture (PWSA) Tranche 1
totals more than 150 satellites — 126 in the Transport Layer, 35 in the Tracking Layer, 12 in the
Demonstration and Experimentation System — operated from two dedicated SDA Space Operations
Centers (Grand Forks AFB, North Dakota, and Redstone Arsenal, Alabama) plus a global network of
ground entry points, with initial warfighting capability targeted for 2027
([Space Development Agency, *Proliferated Warfighter Space Architecture — Tranche 1* factsheet](https://www.sda.mil/wp-content/uploads/2024/06/Tranche-1-Factsheet_FINAL_06.10.2024.pdf)
([Wayback](https://web.archive.org/web/2026/https://www.sda.mil/wp-content/uploads/2024/06/Tranche-1-Factsheet_FINAL_06.10.2024.pdf))).
This is roughly 50× the simulator's own ~24-satellite soft sizing guideline (ADR-0019) for a single
force, in a single tranche of a single layer of one architecture — the scale gap this topic exists
to characterize is not a modest extrapolation.

**The operator's unit of command shifts from the satellite to the layer.** PWSA's Transport Layer
is explicitly architected as a mesh: each satellite carries optical inter-satellite links (OISLs)
compliant with the SDA Optical Communications Terminal (OCT) Standard, each satellite maintaining
four optical links to neighboring satellites, forming a continuously-reconfiguring mesh network
across the constellation rather than a set of independently-tasked point-to-point links
([Space Development Agency, *Tranche 1 Transport Layer* factsheet](https://www.sda.mil/wp-content/uploads/2024/05/Transport-Layer_distro-A_FINAL.pdf)
([Wayback](https://web.archive.org/web/2026/https://www.sda.mil/wp-content/uploads/2024/05/Transport-Layer_distro-A_FINAL.pdf))
· [GAO-25-106838, *Laser Communications: Space Development Agency Should Create Links Between...*](https://www.gao.gov/assets/gao-25-106838.pdf)
([Wayback](https://web.archive.org/web/2026/https://www.gao.gov/assets/gao-25-106838.pdf))).
Operationally, this means a single asset's health or tasking status is meaningful mainly in
relation to its neighbors and the layer's overall coverage/connectivity — the current simulator's
model (each satellite its own independently-commanded `Asset`, per R108) has no concept of
mesh-adjacency or layer-level coverage state at all, which is the concrete gap any aggregation
feature must close, not merely a UI grouping convenience.

**Real proliferated-fleet operations centers are already automation- and exception-driven, not
per-asset drill-down at scale.** Commercial constellation operators report that fleet-management
tooling must coordinate command execution, telemetry processing, and mission planning *across* the
fleet, with shared configuration/script management to bound the per-satellite configuration burden
([Cognitive Space, "Satellite Constellation Management: Challenges and Solutions"](https://www.cognitivespace.com/blog/satellite-constellation-management/)
([Wayback](https://web.archive.org/web/2026/https://www.cognitivespace.com/blog/satellite-constellation-management/)),
already cited by [R108](R108-constellation-operations.md) §4). More specifically, NASA's Advanced
Architectures and Automation Branch built the REACH (Real-time Evaluation and Analysis of
Consolidated Health) visualization system precisely so that a *small* flight operations team could
remain aware of anomalies across a multi-spacecraft fleet regardless of constellation size, by
surfacing exceptions rather than requiring a per-satellite review pass
([NASA Spinoff, "Mission Control Software Manages Commercial Satellite Fleets"](https://spinoff.nasa.gov/Spinoff2018/it_9.html)
([Wayback](https://web.archive.org/web/2026/https://spinoff.nasa.gov/Spinoff2018/it_9.html))). This
is the real-world precedent for treating **health-and-status rollup with drill-down-on-exception**,
not a scaled-up per-asset panel, as the correct operator-facing abstraction at proliferated scale.

**Autonomy absorbs routine tasking so operator attention scales sub-linearly with fleet size.**
Onboard autonomy — trend-based monitoring, power/thermal/pointing management, and automatic
safe-mode entry on anomaly detection — is what allows a fixed-size human operations team to
supervise a fleet whose size grows much faster than the team does; the operator's role shifts from
issuing individual commands to supervising exceptions the autonomy escalates
([NASA Spinoff, *op. cit.*](https://spinoff.nasa.gov/Spinoff2018/it_9.html)). This is directly
relevant to FC-03 (Autonomous Satellite Operations) in the strategic review's Part 2 — proliferated
scale and on-board autonomy are not two independent future concepts but two faces of the same
operational necessity: neither the current per-asset-command model nor a purely human-supervised
mesh scales to hundreds of satellites without it.

**Tasking contention multiplies combinatorially, not linearly, at proliferated scale.**
[R104](R104-collection-management.md)'s sensor-tasking contention model and
[R118](R118-space-surveillance-networks.md)'s SLA-bound SSN request model both already contend with
scarcity at ≤24-satellite scale; at hundreds of satellites, the same contention problem compounds
because a layer's *aggregate* coverage/tasking capacity, not any single satellite's, is what a
mission planner actually reasons about — the correct abstraction is closer to "layer capacity
budget," an object neither R104 nor R118 currently models, than to per-satellite request queues
scaled up.

### Sources

- *Space Development Agency, Proliferated Warfighter Space Architecture — Tranche 1* (factsheet,
  2024-06-10) — [live](https://www.sda.mil/wp-content/uploads/2024/06/Tranche-1-Factsheet_FINAL_06.10.2024.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.sda.mil/wp-content/uploads/2024/06/Tranche-1-Factsheet_FINAL_06.10.2024.pdf)
  · accessed 2026-07-01.
- *Space Development Agency, Tranche 1 Transport Layer* (factsheet) — [live](https://www.sda.mil/wp-content/uploads/2024/05/Transport-Layer_distro-A_FINAL.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.sda.mil/wp-content/uploads/2024/05/Transport-Layer_distro-A_FINAL.pdf)
  · accessed 2026-07-01.
- *US Government Accountability Office, GAO-25-106838, "Laser Communications: Space Development
  Agency Should Create Links Between..."* — [live](https://www.gao.gov/assets/gao-25-106838.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.gao.gov/assets/gao-25-106838.pdf)
  · accessed 2026-07-01.
- *Cognitive Space, "Satellite Constellation Management: Challenges and Solutions"* — [live](https://www.cognitivespace.com/blog/satellite-constellation-management/)
  · [snapshot](https://web.archive.org/web/2026/https://www.cognitivespace.com/blog/satellite-constellation-management/)
  · accessed 2026-07-01 (already cited by [R108](R108-constellation-operations.md); re-cited here for
  its fleet-automation claim specifically).
- *NASA Spinoff, "Mission Control Software Manages Commercial Satellite Fleets"* — [live](https://spinoff.nasa.gov/Spinoff2018/it_9.html)
  · [snapshot](https://web.archive.org/web/2026/https://spinoff.nasa.gov/Spinoff2018/it_9.html)
  · accessed 2026-07-01.

## 4. Operational Context

Real proliferated-architecture operations (PWSA being the clearest current example) are staffed and
tooled on the explicit premise that individual-satellite command does not scale: dedicated
operations centers, mesh-aware ground segments, and exception-based health monitoring exist because
the alternative — a human operator issuing and reviewing per-satellite commands and telemetry
hundreds of times over — is not merely inconvenient but operationally infeasible at this scale.
This reframes what "training realism" means for a PME tool: below ~24 satellites, individually
commanding each asset (the current simulator model) *is* the realistic operator experience; above
roughly that threshold, individually commanding each asset stops being realistic and starts
teaching a workflow no real proliferated-fleet operator actually uses.

## 5. Implementation Guidance

- **Any future aggregation feature should model a layer/mesh object with its own coverage and
  capacity state**, not a UI grouping over existing per-`Asset` state — per the concepts above, the
  real operational unit at proliferated scale is the layer's aggregate connectivity/capacity, which
  has no current engine analog; a rollup dashboard alone (summing existing per-asset fields) would
  not capture this.
- **Health-and-status should default to exception-based rollup with drill-down**, mirroring REACH's
  design pattern — a proliferated-scale fleet panel that shows every satellite's full state by
  default (as the current per-asset drill-down does at ≤24 scale) will not scale visually or
  cognitively; only anomalous/exception assets should demand default attention.
- **Do not conflate constellation aggregation with autonomy (FC-03).** They are related but
  separable: aggregation is about the *operator-facing* abstraction (what a human sees and tasks at
  scale); autonomy is about what the *spacecraft* does without being told. A proliferated-scale
  feature needs both eventually, but should not bundle them into one Implementation Package —
  aggregation can be built against the current fully-human-commanded model first.
- **Model tasking contention as a layer-level capacity budget for any proliferated-scale extension
  of [R104](R104-collection-management.md)/[R118](R118-space-surveillance-networks.md)'s contention
  logic** — a naive scale-up of per-satellite request queues will not represent the real bottleneck,
  which is aggregate layer capacity, not any single satellite's schedule.
- **This topic does not authorize starting an aggregation Implementation Package.** Per
  `docs/FUTURE-WORK.md` §4 and ADR-0019, constellation aggregation above 3 sats remains a deferred,
  not-yet-scoped v2 item; this topic's role is to ensure that when it *is* scoped, the design starts
  from real proliferated-operations precedent rather than an assumption-free scale-up of R108's
  ≤3-sat model.

## 6. Feature Mapping

None yet, by design (§2) — this is research-first grounding for a not-yet-authorized feature. When
constellation aggregation is scoped, its FS-xxx should cite this topic directly rather than
re-deriving the proliferated-operations precedent.

## 7. Related Topics

[R108](R108-constellation-operations.md) (Constellation Operations — the ≤3-sat model this topic
explains what changes beyond), [R118](R118-space-surveillance-networks.md) (Space Surveillance
Networks — request-based tasking whose contention this topic's layer-capacity concept extends),
[R104](R104-collection-management.md) (Collection Management — sensor-tasking contention at
smaller scale), ADR-0019 (the sizing-guideline decision this topic's real-world scale comparison is
read against), `docs/FUTURE-WORK.md` §4 (constellation aggregation, the deferred consumer).
