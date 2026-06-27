# R128 — Ground-Network Contact Scheduling and Conflict Resolution

> **Document ID:** R128
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R107](R107-ground-segment-operations.md), [R118](R118-space-surveillance-networks.md)
> **Referenced By:** FS-105
> **Produces:** implementation constraints for [`engine/access.py`](../../../spacesim/engine/access.py) (`AccessProvider` window allocation)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R107](R107-ground-segment-operations.md) (Ground Segment Operations — the `GroundSite` model this topic's
> scheduling layer sits above), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks — the SLA/concurrency-cap pattern this
> topic's real-world precedent also grounds)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`spacesim`'s `AccessProvider` computes command/telemetry windows per asset-station pair as if every
ground site has unlimited concurrent capacity — a satellite either has a window or doesn't, with no
modeled contention for a station shared across multiple satellites. This topic gives the
implementer the real multi-mission ground-network scheduling discipline (DSN-style) so a future
fidelity increase (a station booked by one asset blocking another) follows a real, proven
conflict-resolution structure rather than an invented contention rule.

## 2. Scope

Covers: the real Deep Space Network-style multi-mission scheduling/conflict-resolution process and
how it would extend `AccessProvider`'s current unlimited-concurrency window model. Does **not**
cover: the per-station elevation-mask/health gating a window already requires ([R107](R107-ground-segment-operations.md)), or the
SSN's own SLA/concurrency-cap request model ([R118](R118-space-surveillance-networks.md)), which already implements a *related*
contention pattern for a different access channel.

## 3. Concepts

**Real multi-mission ground networks treat antenna time as a finite, contested resource requiring
active scheduling, not a free background service.** The DSN scheduling problem is fundamentally
"the problem of assigning the DSN's finite antenna resources to its users within a given time
frame"
([NASA JPL, *Automating Deep Space Network Scheduling and Conflict Resolution*, AAMAS 2006](https://dl.acm.org/doi/10.1145/1160633.1160923)
([Wayback](https://web.archive.org/web/2026/https://dl.acm.org/doi/10.1145/1160633.1160923))) —
the real-world fact `AccessProvider`'s current model elides: a real ground network has far fewer
antennas than missions wanting contact time, so *who gets the window* is itself a planning problem,
not just *whether a window geometrically exists*.

**Conflicts are resolved by priority, then by progressively relaxing request constraints.** When no
conflict-free allocation exists for all requests, a DSN-style scheduling engine resolves contention
by "successively ignor[ing] lower priority activities, then those of equal priority, and finally
all preexisting activities," and if still unresolved, relaxes "(1) timing relationships, (2) gap and
overlap parameters for split tracks, and (3) constraining event windows" in that order
([NASA JPL, *DSN Scheduling Engine*, NTRS 20090016271](https://ntrs.nasa.gov/citations/20090016271)
([Wayback](https://web.archive.org/web/2026/https://ntrs.nasa.gov/citations/20090016271))) — a
priority-then-relax order, not a first-come-first-served or random tie-break, is the real-world
precedent any future `spacesim` contact-contention model should follow, paralleling how
`ssn.py`'s hybrid-turnaround model already resolves SSN requests by priority SLA + processing delay
([R118](R118-space-surveillance-networks.md)).

**Multi-mission scheduling is iterative and human-mediated, not a single batch optimization.**
Distributed mission teams "work with missions and other users of the DSN to determine their
service needs, provide these as input to an initial draft schedule, then iterate among themselves
and work with the users to resolve conflicts and come up with an integrated schedule" (NTRS
20090016271, *op. cit.*) — real contact scheduling is negotiated ahead of execution, not resolved
live at contact time; this is the real-world precedent for any future `spacesim` ground-contention
feature being a planning-time allocation (decided before the access window arrives), consistent with
the plan-first invariant every other commanding path already respects.

### Sources

- *NASA JPL, Automating Deep Space Network Scheduling and Conflict Resolution, AAMAS 2006* —
  [live](https://dl.acm.org/doi/10.1145/1160633.1160923)
  · [snapshot](https://web.archive.org/web/2026/https://dl.acm.org/doi/10.1145/1160633.1160923)
  · accessed 2026-06-27.
- *NASA JPL, DSN Scheduling Engine, NTRS 20090016271* — [live](https://ntrs.nasa.gov/citations/20090016271)
  · [snapshot](https://web.archive.org/web/2026/https://ntrs.nasa.gov/citations/20090016271)
  · accessed 2026-06-27.

## 4. Operational Context

Real multi-mission ground networks (NASA's DSN, AFSCN, and equivalents) never have enough antenna
time to serve every mission's ideal contact schedule simultaneously, so a dedicated automated
scheduling-and-conflict-resolution layer sits above the raw orbital-geometry access-window
calculation every mission's own access predictions already produce. `spacesim`'s `AccessProvider`
currently models only the geometry layer (the DSN's "is a window geometrically possible" question)
and has no equivalent of the network-capacity layer (the DSN's "who actually gets that window when
multiple users want it" question) — appropriate for a sample-vignette scale of a handful of
ground sites and ~24 satellites, but a real gap if a future vignette wants several cells'
satellites genuinely contending for the same finite ground-station roster.

## 5. Implementation Guidance

- **A future ground-contention feature should add a scheduling/allocation layer above
  `AccessProvider`'s existing window computation, not inside it** — `AccessProvider` should keep
  answering "is a window geometrically possible," while a new layer answers "who gets it,"
  mirroring the DSN's separation of geometric access from antenna allocation.
- **Resolve contention by priority, then by relaxing constraints in a fixed order** (timing, then
  gap/overlap, then window bounds) — follow the DSN Scheduling Engine's documented relaxation order
  rather than inventing an ad hoc tie-break (e.g. first-issued-order-wins), which would have no real
  precedent and would be very sensitive to operator click-order.
- **Any contention-resolution decision should be made at planning time, before the contested window
  arrives** — consistent with the plan-first invariant; a feature that resolves contention live at
  the moment of contact would contradict how real ground-network scheduling and every other
  `spacesim` commanding path already work.
- **Reuse the SLA/concurrency-cap pattern `ssn.py` already implements for the SSN's request
  lifecycle** ([R118](R118-space-surveillance-networks.md)) as the starting shape for ground-station contention, rather than designing
  a third, different contention mechanism for what is structurally the same finite-shared-resource
  problem.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the indirect consumer — no current feature requires ground-station
contention modeling at the sample-vignette scale, but a future larger-constellation or
multi-cell-shared-station vignette should ground its scheduling design in this topic rather than
inventing contention logic from scratch.

## 7. Related Topics

[R107](R107-ground-segment-operations.md) (the `GroundSite` elevation/health gating this topic's scheduling layer would sit above), [R118](R118-space-surveillance-networks.md)
(the SSN's already-implemented SLA/concurrency-cap pattern this topic's real-world precedent also
grounds, and a template for a future ground-contact contention model).
