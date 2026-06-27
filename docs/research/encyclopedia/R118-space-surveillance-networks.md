# R118 — Space Surveillance Networks

> **Document ID:** R118
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R102](R102-space-domain-awareness.md)
> **Referenced By:** [R104](R104-collection-management.md), [R119](R119-space-situational-data-fusion.md), FS-104
> **Produces:** implementation constraints for [`engine/ssn.py`](../../../spacesim/engine/ssn.py)
> **Feature Mapping:** FS-104 (SDA Tasking)
> **Related Topics:** [R102](R102-space-domain-awareness.md) (Space Domain Awareness), [R104](R104-collection-management.md) (Collection Management), [R119](R119-space-situational-data-fusion.md) (Data Fusion)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The SSN is a mock, per-cell off-board collection enterprise distinct from organic sensor tasking
([R104](R104-collection-management.md)/[R109](R109-sensor-operations.md)) — request-based, SLA-bound, and dispersion-preset-driven. This topic gives the
implementer the `ssn.py` model so a new SSN-adjacent feature (a new preset, a new request type)
fits the existing request-lifecycle and fog-of-war scoping.

## 2. Scope

Covers: the per-cell `SSNNetwork`/dispersion-preset model, the hybrid-turnaround SLA, and
coalition-vs-national economics. Does **not** cover: the SDA chain stage SSN products advance
([R102](R102-space-domain-awareness.md)), or organic sensor tasking itself ([R104](R104-collection-management.md)/[R109](R109-sensor-operations.md)).

## 3. Concepts

**Each cell owns an independent `SSNNetwork`, instantiated from a dispersion preset.** Presets
(`sparse`/`regional`/`global`/`proliferated`) fix site count/spread for radar and optical ground
sites plus a count of `space_based` sensors, and a per-preset concurrency cap (`_CONCURRENCY`:
1/2/3/5) — more dispersed networks can run more requests at once, modeling real capacity scaling
with sensor count, mirroring the real U.S. Space Surveillance Network's globally-dispersed mix of
phased-array radars (e.g. Space Fence, Kwajalein) and electro-optical telescope sites (GEODSS, four
detachments worldwide) commanded as a single global sensor enterprise by the 18th Space Defense
Squadron
([U.S. Space Force, *18th Space Defense Squadron Fact Sheet*](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/)
([Wayback](https://web.archive.org/web/2026/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/))).

### Sources

- *U.S. Space Force, 18th Space Defense Squadron Fact Sheet* — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/)
  · [snapshot](https://web.archive.org/web/2026/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/)
  · accessed 2026-06-27.

**Requests resolve via the existing `AccessProvider`, not a new geometry model.** `submit_request`
picks the earliest viable window inside the priority's SLA using the same access-window machinery
[R120](R120-access-window-and-geometry-planning.md) documents — the SSN is a tasking/queuing layer on top of existing access computation, not a
parallel geometry engine.

**The hybrid SLA couples a max-wait ceiling to a fixed downstream processing delay.** `MAX_WAIT_S`
(immediate/priority/routine: 900/3600/21600 s) bounds how long a request may wait for a viable
window; `PROCESSING_DELAY_S` (120/600/1800 s) is added *after* collection before delivery — two
deterministic events, `ssn_collect` then `ssn_deliver`, are scheduled to model "collected" and
"processed and disseminated" as genuinely separate moments, mirroring [R103](R103-satellite-command-and-control.md)'s
issuance-vs-confirmation distinction.

**Coalition (Blue) vs. national (Red) affiliation changes network economics, not capability.**
Blue's coalition affiliation applies a broader site spread, a `COALITION_DELAY_MULTIPLIER` (1.5×
processing delay, modeling a partner-shared product queue) and a −1 concurrency adjustment (floor 1)
relative to the same preset run as national — an operational-realism distinction (coalition
products are shared/queued) rather than a difficulty dial.

**Priority has a budget cost, forcing triage on a finite resource.** `PRIORITY_COST`
(`immediate`/`priority`/`routine`: 20/7/2) consumes a finite collection-management budget
(FUTURE-WORK §7) — calibrated so a 100-unit budget covers roughly 5 immediate / 15 priority / 50
routine requests per session, forcing White Cell and operators to genuinely triage rather than
mark everything "immediate."

**Cancel-before-collect is replay-safe via tag-cancel, like other order cancellation.** Cancelling
an SSN request before its `ssn_collect` event fires uses the scheduler's tag-cancel mechanism — the
events never get logged, so replay reproduces exactly the same outcome as if the cancelled request
had never been submitted.

## 4. Operational Context

Real SSN-style collection enterprises are exactly this: a finite, geographically-dispersed sensor
network serving competing requests under priority-tiered SLAs, with collection and
processing/dissemination as genuinely separate steps that take real wall-clock-equivalent time —
the simulator's dispersion presets and hybrid-turnaround model exist to make the *enterprise-level*
collection-management problem (not just single-sensor tasking) a real planning constraint.

## 5. Implementation Guidance

- **A new dispersion preset must define both site layouts and a concurrency cap**, consistent with
  the existing four-preset table — don't add an unbounded-concurrency preset, which would erase the
  scarcity the SSN model exists to create.
- **A new request priority tier must define both `MAX_WAIT_S` and `PROCESSING_DELAY_S` entries**,
  and a `PRIORITY_COST` if the budget system is in play — an SLA without a budget cost reopens the
  "mark everything immediate" failure mode the cost system exists to prevent.
- **Coalition-vs-national differences should be modeled as economics (delay/concurrency
  multipliers), not capability gates** — preserve the existing pattern rather than making coalition
  cells categorically unable to access certain presets.
- **A new request type's lifecycle must still emit `ssn_collect`/`ssn_deliver` as the deterministic
  schedule pair** — collapsing them into one event loses the collected-vs-delivered distinction this
  topic's §2 explicitly models.

## 6. Feature Mapping

FS-104 (SDA Tasking) is the direct consumer — any SSN-facing UI must surface the priority/SLA
tradeoff and the collected-vs-delivered distinction, not present requests as instant.

## 7. Related Topics

[R102](R102-space-domain-awareness.md) (the SDA chain SSN requests advance), [R104](R104-collection-management.md) (the organic-tasking counterpart and the
auto-cue bridge between them), [R119](R119-space-situational-data-fusion.md) (Data Fusion — combining SSN products with organic tracks).
