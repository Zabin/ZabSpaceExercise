# ADR-0034 — Directed energy reuses the `weapon_engagement` access channel

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0034
- **Title:** A directed-energy (DE) order is gated by the existing `weapon_engagement` access
  channel; DE gets no seventh channel
- **Status:** Accepted

## Context

`FR-1410` names `directed_energy` as one of the five effect categories the engine must resolve to,
alongside kinetic, EW, cyber, and (co-orbital/direct-ascent). The engine already declares
`directed_energy` as an `EffectInstance.Category` and an `Asset.kind`, but as of `32ca02a` no order
ever produces one (backlog `BL-0066`, external validation report A5) — the gap `FS-105` v1.1 exists
to close. `FS-105` v1.1's Open Question (`BL-0088`) asked whether DE reuses `weapon_engagement`
(`ADR-0011`'s six-channel taxonomy) or needs a new channel, since DE's *reachability* (line-of-sight
to the target) and its *effectiveness* (whether the achieved irradiance crosses a dazzle/damage
threshold) are physically distinct questions.

`R117` v1.1 §3.2 grounds the physics: DE effectiveness scales with irradiance at range (power,
aperture, beam quality, and — for ground-based platforms only — atmospheric attenuation), while DE
reachability is a line-of-sight/regime question no different in kind from kinetic's own
`interceptor_mask_deg`/`interceptor_max_alt_m` reachability check (`AccessProvider._weapon_predicate`,
per `R117` §3.1).

**The engine already separates reachability from effectiveness for every existing engagement-class
category, and this is not a coincidence to work around — it is the established pattern:**
`jam_footprint` (`ADR-0011`) gates whether an EW order can reach its target at all;
`engine/jam.py`'s `effective_success_prob()` then computes whether the jam actually succeeds, as a
function of modulation/power/bandwidth, entirely inside the resolver, not as a second channel.
`weapon_engagement` gates whether a kinetic order can reach its target at all;
`engine/engage.py`'s `kill_probability_from_class()` then computes Pₖ, again entirely inside the
resolver. In both cases, the access channel answers only "is a window open," and the effectiveness
math is a distinct, resolver-internal computation layered on top.

## Decision

A DE order is gated by the existing `weapon_engagement` access channel — the same reachability
predicate (`AccessProvider._weapon_predicate`, `interceptor_mask_deg`/`interceptor_max_alt_m`) that
already governs kinetic engagement. No seventh access channel is introduced. DE's effectiveness
(the dazzle/damage-threshold question `R117` v1.1 §3.2 characterizes) is computed inside a new
resolver-internal module (an `engine/engage.py`/`engine/jam.py` sibling — its exact name and
function signatures are an Implementation Package decision, not this ADR's), exactly mirroring how
`engine/jam.py` and `engine/engage.py` already separate their own channel-reachability check from
their own effectiveness math.

## Alternatives Considered

- **A new, seventh access channel** (e.g. `directed_energy_footprint`) — rejected. `ADR-0011`
  already states adding a channel "is not done lightly, since it touches `AccessProvider`'s
  contract everywhere," and no genuine reachability distinction motivates one here: DE's
  reachability geometry (line-of-sight, regime/altitude reach) is the same *kind* of check
  `weapon_engagement` already performs for kinetic engagement, just with different numeric
  parameters (which the existing channel's config already supports per-asset-class, the same way
  it already distinguishes interceptor classes).
- **Folding DE into `jam_footprint`** — rejected. `jam_footprint`'s RF-cone geometry is the wrong
  physical model for a directed, aimed beam (laser or HPM); `weapon_engagement`'s
  line-of-sight/mask-angle model is the closer physical match, per `R117` v1.1 §3.2's own
  characterization of DE range/reachability.

## Rationale

The reachability-vs-effectiveness distinction that motivated the Open Question is real, but it is
already solved architecture, not a new problem: every existing engagement-class category resolves
it the same way (channel = reachability only; resolver = effectiveness). DE fits this pattern
without modification. Introducing a new channel would duplicate `weapon_engagement`'s own
reachability geometry for no distinguishing reason.

## Consequences

- The DE Implementation Package (`07-implementation-planning`, once authorized) gates DE orders
  through `weapon_engagement`, identically to how `engage` orders are gated today — no
  `AccessProvider`/`ADR-0011` change is required.
- A new resolver-internal module computes DE effectiveness from `R117` v1.1 §3.2's irradiance
  model; this module's exact shape is left to the Implementation Package, consistent with this
  skill's own rule against specifying implementation detail.
- `FS-105` v1.1's `BL-0088` Open Question is closed by this decision.

## Related

`ADR-0011` (six access channels); `FS-105` v1.1 (`docs/features/FS-105-spacecraft-operations.md`,
Open Questions); `R117` v1.1 §3.1/§3.2 (`docs/research/encyclopedia/R117-directed-energy-and-kinetic-effects.md`);
backlog `BL-0066`, `BL-0088`.
