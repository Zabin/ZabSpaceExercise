# ADR-0017 — Manual adjudication; no automated scoring in v1

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0017
- **Title:** v1 has no automated scoring; White Cell adjudicates and narrates outcomes manually
- **Status:** Accepted

## Context

The tool is a PME wargaming environment run by a human facilitator, not an automated assessment
platform. GDS-01 §10 states: "v1 has no automated scoring; White Cell adjudicates and narrates
consequences by design." `build-spec/01` §3.2 lists "Automated scoring" under explicitly deferred
items, targeted for v2, with rationale "White Cell adjudicates manually in v1."

## Decision

No automated scoring or assessment mechanism exists in v1. Outcomes are adjudicated and narrated
by the White Cell facilitator using the god-view, event log, and AAR replay as their evidence
base.

## Alternatives Considered

- **Rule-based automated scoring** (point values per objective/effect) — explicitly deferred to
  v2 (`build-spec/01` §3.2), not rejected outright; the rationale given is that manual adjudication
  is sufficient and appropriate for v1's PME context, where a human facilitator's judgment is
  itself part of the training value.
- **Exposing raw metrics only, no scoring narrative** — not adopted as the v1 design; White
  Cell's narration of "physically legal but tactically unwise" actions and their natural
  consequences (GDS-01 §10) is treated as a deliberate teaching feature requiring human judgment,
  not a numeric score.

## Rationale

Manual adjudication preserves facilitator judgment as part of the pedagogy (deliberately allowing
tactically unwise-but-legal actions to "play out" rather than being blocked or penalized
automatically) and avoids the design and validation cost of a scoring rubric before the tool's
core mechanics are proven.

## Consequences

- The event log and AAR replay (GDS-01 §7) must carry enough fidelity for a human to adjudicate
  from after the fact — this is why action logging shipped in v1 even though the replay UI itself
  was a later phase (`build-spec/01` §3.1, build-spec/01 Decision D9).
- The "researchers / assessment designers" stakeholder (GDS-01 §3) has no first-class consumption
  path beyond raw AAR/event-log data — left as a genuinely unresolved workflow question; see
  ADR-0029.

## Related

GDS-01 §3, §10; build-spec/01 §3.2, Decision D9.
