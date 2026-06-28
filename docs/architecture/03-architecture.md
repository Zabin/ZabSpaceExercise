# GDS-03 — Architecture

> **Document ID:** GDS-03
> **Version:** 0.0 (scaffold)
> **Status:** ⛔ Planned (scaffold only — no content authored)
> **Dependencies:** GDS-02
> **Referenced By:** GDS-04
> **Produces:** GDS-04
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`design/01-architecture-overview.md`](../design/01-architecture-overview.md) (merge target)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

High-level subsystem decomposition.

## Status

Scaffold only. No content has been authored yet.

## Merge gate (must close before GDS-04 may begin)

- [ ] Absorb the relevant content of
  [`design/01-architecture-overview.md`](../design/01-architecture-overview.md) into this document.
- [ ] Preserve the load-bearing invariants stated in `CLAUDE.md` §"Load-bearing invariants"
  (deterministic core, UI-agnostic engine, fog-of-war at the boundary, etc.) — this document must
  restate or reference them, not silently drop them.
- [ ] Record the decision in this document once made.

## Next

Use the `architecture-design-synthesis` skill to author this document, then close the merge gate
above, before starting GDS-04.
