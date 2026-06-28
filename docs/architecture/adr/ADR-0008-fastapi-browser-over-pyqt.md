# ADR-0008 — FastAPI + browser presentation (supersedes the original PyQt plan)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0008
- **Title:** Presentation layer shipped as FastAPI + browser ("Option A"), not the originally-scoped PyQt desktop GUI
- **Status:** Accepted

## Context

Build-spec/01 Decision D3 originally specified "Python engine + desktop GUI (PyQt/PySide)." GDS-03
§2.4 records that the as-built system instead shipped FastAPI + browser
(`design/02-tech-stack-recommendation.md` "Option A"), and explicitly flags that
`build-spec/03-architecture-and-data.md` §7.1/§7.2 still describes the PyQt alternative, "written
before the web path... was chosen and shipped" — a stale-but-not-yet-corrected binding-spec
passage (GDS-03 Open Question 1).

## Decision

The presentation subsystem is FastAPI (server) + a browser client (vanilla JS, no framework),
serving a thin HTTP layer over `SessionAPI`. This is treated as the as-built, authoritative
presentation choice, superseding D3 in practice though not yet in the binding spec text itself.

## Alternatives Considered

- **PyQt/PySide desktop GUI** (the original D3 choice) — superseded: GDS-03 §2.4 notes it "was not
  built." `design/02` records the reasoning: FastAPI + browser makes the LAN-multiplayer seam
  "nearly free" (`CLAUDE.md` "Tech stack"), whereas a desktop GUI would need a separate
  multiplayer transport bolted on later.
- **A native cross-platform app framework** (e.g. Electron) — not considered in any document;
  out of scope.

## Rationale

Choosing a browser-based client up front meant the LAN-cooperative multiplayer feature (P8) could
reuse the same HTTP interface the single-machine hot-seat mode already used, rather than requiring
a second transport layer to be designed later.

## Consequences

- `build-spec/03-architecture-and-data.md` §7.1/§7.2 remains textually stale (still describes
  PyQt) — GDS-03 explicitly declines to silently rewrite the binding spec, since
  `MSTR-001` §7 gives the build spec authority on conflict. This residual inconsistency is its
  own unresolved decision — see ADR-0028.
- The hardware-floor requirement (integrated graphics, no discrete GPU, `build-spec/01` §3.3)
  shaped the 2D-first rendering approach inside the browser client rather than a native-GUI
  rendering stack.
- No native desktop binary exists or is planned; deployment is "run a Python process, open a
  browser."

## Related

GDS-03 §2.4, Open Question 1; build-spec/01 Decision D3; `design/02-tech-stack-recommendation.md`.
