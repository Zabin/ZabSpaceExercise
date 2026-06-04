# Documentation Index

Master router for the project's prose docs. Each theme is a directory with its own `INDEX.md`;
open a theme index, then the one module you need. Structure & rationale:
[`DOCUMENTATION-PLAN.md`](DOCUMENTATION-PLAN.md).

> **Authority:** on any conflict the **Build Spec** wins — enter it at
> [`build-spec/INDEX.md`](build-spec/INDEX.md).

## Themes

| Theme | What's in it | Start here |
|---|---|---|
| **Build Spec** | The binding v1 specification — context, requirements, architecture, milestones, operator console, SSN. | [`build-spec/INDEX.md`](build-spec/INDEX.md) |
| **Training** | User-facing manual — install, run, first exercise, facilitation, API, troubleshooting. | [`training/INDEX.md`](training/INDEX.md) |
| **Design** | Architecture & design corpus (the *how*) — engine, data model, interfaces, UI, catalog, Δv. | [`design/INDEX.md`](design/INDEX.md) |
| **Research** | Doctrine & domain primers (the *why*) — Western/non-Western doctrine, counterspace taxonomy, orbital mechanics, bus/payload ops. | [`research/INDEX.md`](research/INDEX.md) |
| **Vignettes** | Scenario library — the parameter framework + all 19 vignettes (canonical 8 + training-basics + 5 Red COA + 3 mission-set + 1 learning + 1 novel). | [`vignettes/INDEX.md`](vignettes/INDEX.md) |

## Cross-cutting & generated

- [`FUTURE-WORK.md`](FUTURE-WORK.md) — the single-source v1.1+ TODO (deferred items).
- [`manual/INDEX.md`](manual/INDEX.md) — generated UI screenshots (`tools/render_manual.py`); the
  training modules embed these.

## Root-level guides (not under `docs/`)

- `../README.md` — project overview & quick start.
- `../CLAUDE.md` — durable agent guide: invariants, code map, build/test commands.
- `../memory.md` — rolling design-decision log.

## Theme-directory mapping (for the Build Spec's "companion documents")

The Build Spec refers to companions in `01-research/`, `02-vignettes/`, `03-software-design/`.
Those are now realized as `docs/research/`, `docs/vignettes/`, and `docs/design/` respectively.
