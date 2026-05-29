# Build Specification — Index

[↑ Docs index](../INDEX.md)

The **binding v1 specification** (Project Start Document) for the Space Control & Orbital Warfare
Exercise Simulator. **On any conflict, the build spec wins.** This was one monolith; it is now eight
section modules. Section numbers (`§N`) are preserved so existing citations (incl. source-code
docstrings that cite `§16.9` / `§10`) still resolve to a real heading.

- **Status:** Baseline for v1 implementation · **Classification:** UNCLASSIFIED // TRAINING
- **Audience:** Claude Code (implementer & maintainer), White Cell facilitators, future maintainers
- **Companion themes:** [`design/`](../design/INDEX.md) (software design), [`research/`](../research/INDEX.md),
  [`vignettes/`](../vignettes/INDEX.md). This spec is the authoritative entry point; where it
  references a companion file, that file holds the detailed design.

## Modules

| Module | Sections | Contents |
|---|---|---|
| [01-context-and-scope](01-context-and-scope.md) | §0–4 | How to read; project context & purpose; stakeholders & users; scope; key decisions log. |
| [02-requirements-and-operations](02-requirements-and-operations.md) | §5–6 | Functional requirements; operations & hot-seat model. |
| [03-architecture-and-data](03-architecture-and-data.md) | §7–8 | Architecture (v1); data formats. |
| [04-nfr-milestones-and-risks](04-nfr-milestones-and-risks.md) | §9–12 | Non-functional requirements; milestones & acceptance (M0–M7); risks & mitigations; glossary. |
| [05-workflows-and-state-machines](05-workflows-and-state-machines.md) | §13–14 (Part 3) | Operator workflow walkthroughs; key state machines. |
| [06-test-plan-and-schedule](06-test-plan-and-schedule.md) | §15–17 (Part 3) | Test plan; phased schedule & effort; open items to confirm with White Cell. |
| [07-operator-console](07-operator-console.md) | §16 (Part 4) | The v1 operator console / UI specification — fleet rail, drill-down, command compose, recovery strip, data/API binding, accessibility. |
| [08-ssn](08-ssn.md) | §17 (Part 4) | Mock Space Surveillance Network — per-cell networks, dispersion presets, coverage, hybrid turnaround, determinism, API/UI, vignette wiring. |

> **Note on numbering.** The original document had a Part 3 and a Part 4 that each restarted at
> §16/§17. Here the Part 4 console/SSN sections (the ones cited from code) live in
> `07-operator-console.md` / `08-ssn.md`; the Part 3 schedule/open-items live in
> `06-test-plan-and-schedule.md` and are labelled *Part 3* to disambiguate.

## Phase status (from §10 / §16)

Backend feature-complete through Phase 7; the operator console (§16) and SSN (§17) are implemented
and test-covered. Deferred items are tracked in [`../FUTURE-WORK.md`](../FUTURE-WORK.md).
