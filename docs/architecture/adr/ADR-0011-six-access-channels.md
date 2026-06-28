# ADR-0011 — Six access channels as the access-modeling taxonomy

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0011
- **Title:** All interaction with an asset is modeled through six named access channels
- **Status:** Accepted

## Context

The engine must express "you can only command, observe, or attack when orbital geometry and
ground access permit" (`build-spec/01` §1.1) in a way generic enough to cover every order type.
GDS-03 §2.1 names the six channels computed behind the `AccessProvider` seam: `command_uplink`,
`telemetry_downlink`, `sensor_observation`, `jam_footprint`, `weapon_engagement`, `rpo_proximity`.
`CLAUDE.md` "Key facts" restates the same six. Grounded in `research/encyclopedia` R120 (access
window and geometry planning).

## Decision

Every action that depends on orbital/ground geometry is classified into exactly one of six access
channels, each independently computed (with window caching) by the `AccessProvider` seam.
Unknown endpoint ids degrade gracefully to no-access rather than crashing (GDS-03 §2.1).

## Alternatives Considered

- **A single generic "is-accessible" predicate** (no channel distinction) — rejected: different
  channels have materially different geometry constraints (e.g. `jam_footprint`'s RF cone vs.
  `rpo_proximity`'s relative-position window); collapsing them would lose the realism the tool
  is built to teach.
- **More than six channels** (e.g. splitting `sensor_observation` by sensor type) — not adopted;
  no document proposes a finer split, and sensor-type variation is instead handled inside the
  sensor-operations layer (R109), not as a separate access channel.

## Rationale

Six channels is the minimum set that distinguishes every order-verb category the engine supports
(`jam`/`engage`/`observe`/`maneuver`/`downlink`/`cyber`/`command`) while keeping the
`AccessProvider` seam's contract uniform across all of them.

## Consequences

- Cyber is the one documented exception — it does not go through a window-gated access channel
  at all (it is window-independent); see ADR-0012.
- Adding a new order-verb type means deciding which existing channel it maps to, or whether a
  seventh channel is genuinely required — not done lightly, since it touches `AccessProvider`'s
  contract everywhere.

## Related

GDS-03 §2.1; `CLAUDE.md` "Key facts"; `research/encyclopedia/R100-index.md` (R120).
