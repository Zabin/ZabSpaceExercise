# ADR-0029 — Assessment/scoring stakeholder workflow ownership (unresolved)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0029
- **Title:** No subsystem or domain object owns how the "researchers / assessment designers" stakeholder consumes exercise output
- **Status:** Proposed

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

**No decision has been made.** Manual adjudication (ADR-0017) covers the White Cell's in-the-
moment adjudication need, but the separate question of how a researcher/assessment-designer
stakeholder would systematically consume exercise output (beyond reading raw AAR/event-log data
themselves) has no owning subsystem, domain object, or documented workflow anywhere in GDS-01
through GDS-04.

## Alternatives Considered

Not yet evaluated, since no subsystem has been proposed to own this workflow:

- Treat it as already satisfied by raw AAR/event-log access (no new subsystem needed; researchers
  do their own analysis externally) — implicitly the current de facto position, but never stated
  as a deliberate decision.
- Introduce a dedicated export/analysis interface for assessment designers, distinct from both the
  White Cell's adjudication view and the AAR replay UI.
- Explicitly scope this to `docs/domains/DOM-002`/`DOM-004`/`DOM-005` as GDS-01 suggests, and treat
  it as that domain framework's responsibility to resolve rather than the architecture ladder's.

## Rationale

Not applicable — this requires a design decision (does this stakeholder need a dedicated
interface, or is raw log/AAR access sufficient?) that no document has made, and is explicitly
named as likely belonging to a different documentation tier (`docs/domains/`) than the
architecture ladder.

## Consequences

Until resolved: the "researchers / assessment designers" stakeholder entry in GDS-01 §3 names a
need with no corresponding capability anywhere in the architecture — a stakeholder whose
requirements are acknowledged but architecturally unaddressed.

## Related

GDS-01 §3, Open Question 5; `reviews/architecture-review.md` §1 finding 1, §7 findings 1–2;
ADR-0017.
