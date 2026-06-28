# ADR-0028 — PyQt build-spec staleness reconciliation

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0028
- **Title:** `build-spec/03-architecture-and-data.md` §7.1/§7.2 is rewritten to describe the shipped FastAPI + browser presentation directly
- **Status:** Accepted

## Context

ADR-0008 records that the as-built presentation subsystem is FastAPI + browser, not the PyQt/
PySide desktop GUI `build-spec/03-architecture-and-data.md` §7.1/§7.2 still describes. GDS-03 Open
Question 1 states this is "flag[ged] ... as stale rather than silently rewriting the binding
spec — resolving the staleness in `build-spec/03` itself is out of this document's authority
(`MSTR-001` §7: build spec wins on conflict; this is a flagged tension, not a unilateral
correction)."

## Decision

`build-spec/03-architecture-and-data.md` §7.1/§7.2 is to be **rewritten directly** to describe the
shipped FastAPI + browser presentation, retiring the PyQt/PySide description as historical. This
ADR is the recorded authorization for that build-spec edit — the project owner, who has the
authority `MSTR-001` §7 reserves for build-spec maintenance, has made the call GDS-03 deliberately
declined to make unilaterally.

## Alternatives Considered

- Leave `build-spec/03` as the historical v1-planning-time record and rely on GDS-03 as the
  as-built source of truth, accepting the permanent textual inconsistency — **not adopted**: the
  project owner chose to correct the spec rather than carry the inconsistency indefinitely.
- Add a lighter-weight stale-flag annotation inside `build-spec/03` pointing forward to GDS-03,
  without a full rewrite — **not adopted**: the project owner chose the full rewrite over the
  lighter annotation.

## Rationale

`MSTR-001` §7 gives the build spec authority on conflict, but that authority sits with whoever
owns build-spec maintenance, not with a GDS-level document. The project owner exercising that
authority directly resolves the tension GDS-03 flagged, rather than leaving a stale binding
document in place indefinitely. A full rewrite (over a lighter annotation) keeps `build-spec/03`
internally coherent for a reader who does not cross-reference GDS-03.

## Consequences

- `build-spec/03-architecture-and-data.md` §7.1/§7.2 needs to be edited to describe FastAPI +
  browser (server process, browser client, `SessionAPI` boundary) in place of the PyQt/PySide
  desktop GUI description, citing ADR-0008/GDS-03 as the as-built reference. This document records
  the decision; the build-spec text edit is the follow-up it authorizes.
- Once edited, GDS-03 Open Question 1 is resolved and its "flagged as stale" framing should be
  updated to reflect that the staleness has been corrected at the source.

## Related

GDS-03 Open Question 1; `build-spec/03-architecture-and-data.md` §7.1–7.2; `MSTR-001` §7;
ADR-0008.
