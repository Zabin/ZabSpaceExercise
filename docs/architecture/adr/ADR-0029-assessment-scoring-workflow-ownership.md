# ADR-0029 — Assessment/scoring stakeholder workflow ownership

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0029
- **Title:** Raw AAR/event-log access is sufficient for the "researchers / assessment designers" stakeholder; no new subsystem is needed
- **Status:** Superseded 2026-07 by [ADR-0033](ADR-0033-dedicated-research-export-interface.md)
  *(this file is retained, unedited below, for historical reference — see ADR-0033 for the current
  decision: a dedicated multi-run/cohort research-export interface is now authorized, reversing
  this ADR's "no new dedicated export/analysis interface" Decision)*

## Context

ADR-0017 records the accepted decision that v1 has no automated scoring — White Cell adjudicates
manually. Separately, GDS-01 §3 names "researchers / assessment designers" as a stakeholder, but
GDS-01 Open Question 5 states: "how that stakeholder actually consumes exercise output today
(beyond raw AAR/event-log data) is not described in any operational document reviewed." This was
"confirmed still open by the GDS-01–04 architecture review" (`reviews/architecture-review.md` §1
finding 1, §7 findings 1–2): "neither GDS-03's subsystem decomposition nor GDS-04's domain model
was found to own this workflow either, so the gap is architecture-wide, not specific to this
document."

## Decision

Raw AAR/event-log access (replay/scrub/branch-compare, plus the existing CSV/JSON export at
`/api/sessions/{sid}/aar/export.{csv,json}`) is treated as **sufficient** for the "researchers /
assessment designers" stakeholder's needs. Researchers do their own downstream analysis externally
on this exported data; no new dedicated export/analysis interface or owning subsystem is
introduced.

## Alternatives Considered

- Introduce a dedicated export/analysis interface for assessment designers, distinct from both the
  White Cell's adjudication view and the AAR replay UI — **not adopted**: the project owner judged
  the existing raw-data access path sufficient.
- Explicitly scope this to `docs/domains/DOM-002`/`DOM-004`/`DOM-005` as GDS-01 suggested, treating
  it as that domain framework's responsibility — **not adopted**: the project owner resolved the
  question directly rather than handing it to a domain framework.

## Rationale

The existing AAR replay/scrub/branch-compare and CSV/JSON export already give a researcher
complete, ground-truth access to a session's full event history and objective outcomes. Building a
dedicated analysis interface would duplicate that access without a stated unmet need driving it;
the project owner chose not to speculatively build for a stakeholder need that is already
addressable with existing exports.

## Consequences

- The "researchers / assessment designers" stakeholder entry in GDS-01 §3 is now backed by a
  concrete, named capability (AAR export) rather than left unaddressed.
- If a concrete unmet need for assessment designers emerges later (e.g. a specific aggregate metric
  AAR export doesn't capture), that would be a new, separate decision — this ADR does not preclude
  revisiting the question, it closes the currently-open gap with the existing capability.

## Related

GDS-01 §3, Open Question 5; `reviews/architecture-review.md` §1 finding 1, §7 findings 1–2;
ADR-0017; `session/aar.py`.
