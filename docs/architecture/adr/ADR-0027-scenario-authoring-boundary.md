# ADR-0027 — Scenario-authoring workflow's boundary actor/interface (unresolved)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0027
- **Title:** Whether vignette authoring is an in-system UI feature or an external offline-editing step
- **Status:** Proposed

## Context

GDS-02 §1/§6 describe vignette files crossing the boundary as input, and GDS-01 §5 step 1
describes White Cell "building or loading" a vignette, but GDS-02 Open Question 4 states: "no
document names the in-app builder (or hand-authoring) as a boundary-crossing interaction distinct
from simply 'loading a file.'" Raised by the architecture review (`reviews/architecture-review.md`
§1 finding 2).

## Decision

**No decision has been made.** Whether the in-app scenario builder is a first-class boundary
interface in its own right (i.e. a distinct external-actor interaction pattern alongside "load a
file"), or whether authoring is simply an offline editing step with no architectural distinction
from loading, is unresolved. GDS-02 explicitly left this open "since resolving it means deciding
whether authoring is in-system (a UI feature) or external (an offline editing step) — a real
design question, not a documentation oversight to silently fix."

## Alternatives Considered

Not yet evaluated against each other, pending the underlying design decision:

- Treat the in-app builder as a distinct boundary interaction (its own row in GDS-02 §2/§8),
  since it has different data-flow characteristics (interactive multi-step authoring) than a
  one-shot file load.
- Treat authoring as out-of-system entirely (an offline step a facilitator does with any text/
  YAML editor, with the in-app builder being merely a convenience UI on top of the same "load a
  file" boundary interaction) — i.e. no new actor or interface needed.

## Rationale

Not applicable — resolving this requires a design decision about how central the in-app builder
is meant to be to the v1 user experience, not a documentation fix.

## Consequences

Until resolved: the system-context picture (GDS-02 §1–§9) is silent on whether the in-app builder
deserves its own boundary-crossing description distinct from "vignette file load," which could
under-specify requirements for anyone extending the builder.

## Related

GDS-02 §1, §6, Open Question 4; GDS-01 §5; `reviews/architecture-review.md` §1 finding 2.
