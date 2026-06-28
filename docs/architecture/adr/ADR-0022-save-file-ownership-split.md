# ADR-0022 — Save-file ownership split between session layer and content subsystem

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0022
- **Title:** The session layer owns the act of producing a save; content owns the resulting file format
- **Status:** Accepted

## Context

Save files are produced by the running session (a live, in-memory state) but persisted in the same
on-disk-format world that vignette files live in. GDS-03 §2.2 clarifies (per the architecture
review reconciliation): "this subsystem [session layer] owns the *act* of producing a save... §2.5
Content & Data owns the resulting *on-disk file format* once written, identically to how it owns
vignette file formats. Neither subsystem owns the other's half of this round trip."

## Decision

Save-file responsibility is split: the Session/Application layer owns *producing* a save
(serializing current session state on demand or at session end); the Content & Data subsystem owns
the *on-disk file format* of the resulting file, exactly as it owns vignette file formats.

## Alternatives Considered

- **Session layer owns the entire save-file lifecycle** (including format) — rejected: would
  duplicate format-ownership logic that the content subsystem already owns for vignettes,
  creating two divergent on-disk-format authorities for structurally similar files.
- **Content subsystem owns producing saves too** (reaching into a running session to serialize it)
  — rejected: GDS-03 §2.5 states the content subsystem "does not reach back into a running
  session," which this would violate.

## Rationale

This split mirrors the existing vignette-file pattern (content owns format; whoever produces an
instance of that format owns the production act) rather than inventing a new ownership rule
specific to save files.

## Consequences

- A save-format change must be made in the content subsystem's schema definitions even though the
  session layer is what triggers writing one.
- Resume-from-save logic in the session layer must consume exactly the format the content
  subsystem defines — no independent serialization scheme.

## Related

GDS-03 §2.2, §2.5 (Review reconciliation); `reviews/architecture-review.md` §2 finding 3.
