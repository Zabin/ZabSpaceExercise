# ADR-0028 — PyQt build-spec staleness reconciliation (unresolved)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0028
- **Title:** Whether to correct `build-spec/03-architecture-and-data.md` §7.1/§7.2's stale PyQt description
- **Status:** Deferred

## Context

ADR-0008 records that the as-built presentation subsystem is FastAPI + browser, not the PyQt/
PySide desktop GUI `build-spec/03-architecture-and-data.md` §7.1/§7.2 still describes. GDS-03 Open
Question 1 states this is "flag[ged] ... as stale rather than silently rewriting the binding
spec — resolving the staleness in `build-spec/03` itself is out of this document's authority
(`MSTR-001` §7: build spec wins on conflict; this is a flagged tension, not a unilateral
correction)."

## Decision

**No decision has been made.** GDS-03 deliberately did not correct `build-spec/03`'s stale text,
on the grounds that `MSTR-001` §7 gives the build spec authority on conflict and a GDS-level
document is not authorized to unilaterally rewrite it. Whether `build-spec/03` should itself be
updated to reflect the shipped FastAPI + browser presentation is left to whoever owns build-spec
maintenance — not decided here.

## Alternatives Considered

Not yet evaluated, since no one has yet taken up build-spec/03 maintenance to decide between
them:

- Update `build-spec/03-architecture-and-data.md` §7.1/§7.2 directly to describe FastAPI +
  browser, retiring the PyQt description as historical.
- Leave `build-spec/03` as the historical v1-planning-time record and rely on GDS-03 as the
  as-built source of truth going forward, accepting the permanent textual inconsistency between
  the two documents.
- Add a stale-flag annotation inside `build-spec/03` itself pointing forward to GDS-03, without a
  full rewrite (a lighter-weight reconciliation than a full rewrite).

## Rationale

Not applicable — `MSTR-001` §7 reserves this decision to whoever has authority over the binding
build spec; a GDS-level architecture document cannot make it unilaterally.

## Consequences

Until resolved: a reader of `build-spec/03` alone (without cross-referencing GDS-03) would form an
incorrect belief about the shipped presentation technology.

## Related

GDS-03 Open Question 1; `build-spec/03-architecture-and-data.md` §7.1–7.2; `MSTR-001` §7;
ADR-0008.
