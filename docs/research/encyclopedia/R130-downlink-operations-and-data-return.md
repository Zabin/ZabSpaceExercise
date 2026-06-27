# R130 — Downlink Operations and Data Return

> **Document ID:** R130
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](R103-satellite-command-and-control.md), [R114](R114-command-and-data-handling.md)
> **Referenced By:** FS-105
> **Produces:** implementation constraints for [`engine/orders.py`](../../../spacesim/engine/orders.py) (the `downlink` action / `execute_downlink` handler)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R103](R103-satellite-command-and-control.md) (Satellite C2 — the uplink half of the same access-window machinery),
> [R107](R107-ground-segment-operations.md) (Ground Segment Operations — the `GroundSite` the downlink delivers to),
> [R114](R114-command-and-data-handling.md) (Command and Data Handling — the storage buffer a downlink drains),
> [R124](R124-ccsds-telemetry-and-telecommand-standards.md) (CCSDS standards — the uplink-side protocol counterpart; does not itself cover downlink scheduling/prioritization)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 2

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`engine/orders.py`'s `downlink` action — one of the simulator's seven order-verb types alongside
`jam`/`engage`/`observe`/`maneuver`/`cyber`/`command` — is the only one with no R1xx topic an
implementer would read first. R103 (Satellite C2) explicitly scopes itself to the uplink chain and
disclaims "onboard storage/dump mechanics"; R114 (Command and Data Handling) explicitly scopes
itself to the storage buffer and disclaims "the downlink delivery mechanics storage gates into";
R107 (Ground Segment Operations) explicitly scopes itself to the `GroundSite` model and disclaims
the C2 chain a contact delivers. Each of the three adjacent topics names the downlink action as
something it deliberately does *not* cover. This topic closes that gap: it gives the implementer
the real data-return discipline (priority-lane scheduling, partial/selective dump, bitrate-limited
playback) behind `execute_downlink`'s `bitrate_cap_kbps`/`priority`/`partial_dump` parameters
(FUTURE-WORK §11.A.4).

## 2. Scope

Covers: real mission-downlink scheduling and playback-prioritization practice — priority-lane
contention for limited contact time, partial/selective data dumps instead of all-or-nothing buffer
drains, and bitrate-limited playback — as the grounding for `execute_downlink`'s
`bitrate_cap_kbps`, `priority`, and `partial_dump` (`last_n_minutes`/`product_ids`) parameters.
Does **not** cover: the uplink/validation chain that schedules the downlink order itself
([R103](R103-satellite-command-and-control.md)), the onboard storage-fraction gate a downlink
drains ([R114](R114-command-and-data-handling.md)), the `GroundSite` elevation/health model the
contact geometry depends on ([R107](R107-ground-segment-operations.md)), or the wire-level frame
protocol ([R124](R124-ccsds-telemetry-and-telecommand-standards.md)).

## 3. Concepts

**Real downlink contact time is a scheduled, prioritized resource, not an automatic drain.** Earth
observation missions plan playback against a finite downlink budget per contact, ranking which
collected products go down first when not everything fits in the pass — exactly the problem
`execute_downlink`'s `priority` lane (`routine` vs. a higher lane) and `partial_dump` selector model
instead of assuming every contact empties the entire onboard buffer
([CCSDS 130.1-G-3, *Overview of Space Communications Protocols*](https://public.ccsds.org/Pubs/130x1g3.pdf)
([Wayback](https://web.archive.org/web/2026/https://public.ccsds.org/Pubs/130x1g3.pdf))) — real
mission operations centers build a downlink pass plan ahead of the contact rather than discovering
what to send once the link is up.

**Bitrate is itself a planning constraint, not just a link-budget afterthought.** A downlink's
achievable data rate is bounded by the link's actual RF budget for that specific pass (range,
antenna, ground-station EIRP/G/T), and mission planners size playback lists against that
per-contact bitrate ceiling rather than against the satellite's theoretical maximum transmitter
rate — the real-world precedent for `execute_downlink`'s `bitrate_cap_kbps` parameter capping
delivered volume per order independently of the storage-buffer drain itself
([CCSDS 130.1-G-3](https://public.ccsds.org/Pubs/130x1g3.pdf), *op. cit.*, §on space link budgeting).

**Partial/selective dump is standard practice, not a degraded fallback.** Real ground-segment
playback commanding supports requesting a specific time window or specific stored-product set from
onboard storage rather than only a single bulk "dump everything" command — the CCSDS File Delivery
Protocol (CFDP) explicitly supports selective, resumable file-by-file transfer over a space link
rather than treating the downlink as one undifferentiated stream
([CCSDS 727.0-B-5, *CCSDS File Delivery Protocol (CFDP)*](https://public.ccsds.org/Pubs/727x0b5.pdf)
([Wayback](https://web.archive.org/web/2026/https://public.ccsds.org/Pubs/727x0b5.pdf))) — the
real-world precedent for `partial_dump`'s `last_n_minutes`/`product_ids` selectors, as opposed to a
single coarse "downlink everything in the buffer" toggle.

### Sources

- *CCSDS 130.1-G-3, Overview of Space Communications Protocols* —
  [live](https://public.ccsds.org/Pubs/130x1g3.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://public.ccsds.org/Pubs/130x1g3.pdf)
  · accessed 2026-06-27.
- *CCSDS 727.0-B-5, CCSDS File Delivery Protocol (CFDP)* —
  [live](https://public.ccsds.org/Pubs/727x0b5.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://public.ccsds.org/Pubs/727x0b5.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

A real satellite's downlink contact is short, scheduled, and contended against every other use of
that ground/relay asset, so flight operations teams build a per-pass playback plan ahead of time:
which stored products go down first, at what bitrate the link budget for that specific pass
actually supports, and whether a partial selective dump is sufficient instead of waiting for a
longer contact to empty the whole buffer. `execute_downlink`'s extended parameters
(`bitrate_cap_kbps`, `priority`, `partial_dump`) model exactly this planning discipline; the
"legacy single-token `delivers`" default path (FUTURE-WORK §11.A.4) is the simplified case where the
whole buffer goes down in one undifferentiated dump — appropriate as a default but not the real
operational norm once a vignette wants downlink contention to matter.

## 5. Implementation Guidance

- **Treat `priority` as a real scheduling lane, not cosmetic metadata** — if a future feature adds
  multiple competing downlink orders against one contact window, resolve contention by priority
  first (mirroring R128's DSN-style priority-then-relax pattern), not by issue order.
- **`bitrate_cap_kbps` should reflect the pass's actual link budget, not the satellite's nominal
  transmitter rate** — a future higher-fidelity feature that derives this cap from range/antenna
  geometry rather than a flat operator-set number would be following the real CCSDS link-budget
  precedent above.
- **`partial_dump`'s `last_n_minutes`/`product_ids` selectors are the correct shape to extend** —
  any new downlink-selection feature should stay file/product-addressable (CFDP's model) rather than
  collapsing back to all-or-nothing, since that is the real-world precedent for selective space-link
  data return.
- **Keep downlink scheduling decisions plan-time, not discovered live at contact** — consistent with
  the plan-first invariant every other commanding path in `spacesim` already respects.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — `execute_downlink`'s extended parameters
(FUTURE-WORK §11.A.4) are the implemented feature this topic grounds.

## 7. Related Topics

[R103](R103-satellite-command-and-control.md) (the uplink half of the same access-window
machinery the downlink action shares), [R107](R107-ground-segment-operations.md) (the `GroundSite`
model the downlink contact's geometry depends on), [R114](R114-command-and-data-handling.md) (the
onboard storage buffer a downlink drains), [R124](R124-ccsds-telemetry-and-telecommand-standards.md)
(the uplink-side CCSDS protocol counterpart — explicitly does not cover downlink scheduling),
[R128](R128-ground-network-contact-scheduling.md) (the priority-then-relax contention pattern a
future multi-order downlink-scheduling feature should reuse).
