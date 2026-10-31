# ADR-0007 — Content as data, not code

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0007
- **Title:** Vignettes, the inject library, and TLE sources are data files, not Python
- **Status:** Accepted

## Context

White Cell facilitators and content authors are not expected to write Python. GDS-03 §2.5 names
content & data's purpose as keeping "all scenario-specific and reference content as data, never
code... so White Cell facilitators and content authors never edit Python." `CLAUDE.md` invariant
6 makes this load-bearing. Originally recorded as build-spec/01 Decision D5 (data-driven content,
JSON vignettes from an in-app builder).

## Decision

Vignette definitions (with assets, sensors and effects authored inline) and the inject-template
library are authored as YAML/JSON files (`spacesim/content/`), loaded and validated by pydantic v2 schemas,
not embedded as Python logic.

## Alternatives Considered

- **Vignettes as Python scripts** (programmatic scenario definition) — rejected: would require
  content authors to write code, contradicting the explicit non-programmer-facilitator design
  goal (`build-spec/01` §1.2, GDS-00 §5.1).
- **A proprietary binary scenario format** — not adopted; no document proposes one, and YAML/JSON
  keeps content human-readable and diffable.

## Rationale

Separating content from code keeps scenario logic auditable by non-programmers and prevents
scenario-specific special cases from leaking into the engine, which `CLAUDE.md` explicitly calls
out as a discipline check: "If scenario logic starts leaking into code, move it back into data."

## Consequences

- The Content & Data subsystem owns on-disk file formats exclusively (GDS-03 §2.5); the engine
  only consumes the parsed result.
- Any new scenario mechanic must be expressible as data (parameters/dials/injects) before it can
  ship, constraining feature design.
- Save-file format ownership inherits this same data-not-code split — see ADR-0022.

## Amendment (2026-10-31, `BL-0233`)

The original wording also named asset/effect/sensor template libraries. None was ever built; assets,
sensors and effects are authored inline in the vignette. By owner decision (`BL-0233` option A,
`ADR-0036`) this ADR is amended to the inline-authoring model. The decision (content is data, not
Python) is unchanged.

## Related

GDS-03 §2.5, `CLAUDE.md` invariant 6, build-spec/01 Decision D5.
