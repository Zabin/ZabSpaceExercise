# GDS-04 — Domain Model

> **Document ID:** GDS-04
> **Version:** 0.0 (scaffold)
> **Status:** ⛔ Planned (scaffold only — no content authored)
> **Dependencies:** GDS-03
> **Referenced By:** GDS-05
> **Produces:** GDS-05
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`design/04-data-model.md`](../design/04-data-model.md) (merge target — entity/relationship portion only; the schema portion belongs to GDS-07)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

Core entities and relationships.

## Status

Scaffold only. No content has been authored yet.

## Merge gate (must close before GDS-05 may begin)

- [ ] Absorb the entity/relationship content of
  [`design/04-data-model.md`](../design/04-data-model.md) into this document — conceptual
  entities and invariants, not the persistence schema (that split is deliberate; the schema
  portion of the same source file is GDS-07's merge target, not this one).
- [ ] Record the decision in this document once made, including how the GDS-04/GDS-07 split was
  drawn against the single source file.

## Next

Use the `architecture-design-synthesis` skill to author this document, then close the merge gate
above, before starting GDS-05.
