# ADR-0027 — Scenario-authoring workflow's boundary actor/interface

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0027
- **Title:** The in-app vignette builder is a distinct boundary-crossing interaction, separate from "load a file"
- **Status:** Accepted

## Context

GDS-02 §1/§6 describe vignette files crossing the boundary as input, and GDS-01 §5 step 1
describes White Cell "building or loading" a vignette, but GDS-02 Open Question 4 states: "no
document names the in-app builder (or hand-authoring) as a boundary-crossing interaction distinct
from simply 'loading a file.'" Raised by the architecture review (`reviews/architecture-review.md`
§1 finding 2).

## Decision

The in-app scenario builder is a **distinct boundary-crossing interaction**, not merely a
convenience UI layered on top of "load a file." White Cell's interactive, multi-step authoring
session (building a vignette inside the running application) is recognized as its own
boundary-crossing pattern in GDS-02, separate from the one-shot file-load interaction used when
loading a pre-authored or hand-written vignette file.

## Alternatives Considered

- Treat authoring as out-of-system entirely (an offline step with any text/YAML editor, with the
  in-app builder being merely a convenience UI on the same "load a file" interaction) — **not
  adopted**: the project owner chose to recognize the in-app builder as architecturally distinct.
- Explicitly scope this to a domain framework (`docs/domains/`) rather than the architecture
  ladder — **not adopted**: the project owner resolved this at the architecture-ladder level via
  this ADR rather than deferring to a domain document.

## Rationale

The in-app builder is interactive and multi-step (it accumulates partial vignette state across a
session before anything is "loaded"), which has materially different data-flow characteristics
than a single inbound file read. Naming it as its own boundary interaction in GDS-02 makes that
difference visible to anyone extending the builder or reasoning about the system's boundary,
rather than leaving it folded indistinguishably into the "vignette file" input row.

## Consequences

- GDS-02 §2 (External actors) and §8 (External interfaces) should be updated to add the in-app
  scenario builder as its own boundary-crossing interaction for the White Cell actor, distinct
  from the existing "vignette file" input row in §4/§6. This document records the decision; the
  GDS-02 text update is the follow-up edit it authorizes.
- Future requirements work (GDS-05) extending the in-app builder should treat it as a first-class
  boundary interaction with its own requirements, not as an extension of file-load semantics.

## Related

GDS-02 §1, §2, §6, §8, Open Question 4; GDS-01 §5; `reviews/architecture-review.md` §1 finding 2.
