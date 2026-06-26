# Documentation Index

Master router for the project's prose docs. Each theme is a directory with its own `INDEX.md`;
open a theme index, then the one module you need. Structure & rationale (legacy five-theme corpus):
[`DOCUMENTATION-PLAN.md`](DOCUMENTATION-PLAN.md). Full tree incl. the documentation-driven-development
expansion (`master/`, `domains/`, `research/encyclopedia/`, `features/`, `implementations/`,
`architecture/`, `scenarios/`): [`master/MSTR-005-documentation-map.md`](master/MSTR-005-documentation-map.md).

> **Authority:** on any conflict the **Build Spec** wins — enter it at
> [`build-spec/INDEX.md`](build-spec/INDEX.md).

## Themes

| Theme | What's in it | Start here |
|---|---|---|
| **Master** | Program-defining documents (vision, architecture principles, educational philosophy, glossary, doc map, governance, research philosophy) — read MSTR-001 first. | [`master/INDEX.md`](master/INDEX.md) |
| **Domains** | Capability frameworks (training, assessment, White Cell, research, validation, governance, human factors, AI integration, doctrine development) that generate Feature Specifications. | [`domains/INDEX.md`](domains/INDEX.md) |
| **Build Spec** | The binding v1 specification — context, requirements, architecture, milestones, operator console, SSN. | [`build-spec/INDEX.md`](build-spec/INDEX.md) |
| **Training** | User-facing manual — install, run, first exercise, facilitation, API, troubleshooting. | [`training/INDEX.md`](training/INDEX.md) |
| **Design** | Architecture & design corpus (the *how*) — engine, data model, interfaces, UI, catalog, Δv. | [`design/INDEX.md`](design/INDEX.md) |
| **Research** | Doctrine & domain primers (the *why*) — Western/non-Western doctrine, counterspace taxonomy, orbital mechanics, bus/payload ops. | [`research/INDEX.md`](research/INDEX.md) |
| **Vignettes** | Scenario library — the parameter framework + all 19 vignettes (canonical 8 + training-basics + 5 Red COA + 3 mission-set + 1 learning + 1 novel). | [`vignettes/INDEX.md`](vignettes/INDEX.md) |

## Cross-cutting & generated

- [`../ROADMAP.md`](../ROADMAP.md) — the single authoritative tracker of every document this
  project produces: IDs, dependencies, and completion status. Start here to see what's done, in
  progress, or still planned without re-deriving it from the directories below.
- [`FUTURE-WORK.md`](FUTURE-WORK.md) — the single-source v1.1+ TODO (deferred items).
- [`manual/INDEX.md`](manual/INDEX.md) — generated UI screenshots (`tools/render_manual.py`); the
  training modules embed these.

## Root-level guides (not under `docs/`)

- `../README.md` — project overview & quick start.
- `../CLAUDE.md` — durable agent guide: invariants, code map, build/test commands.
- `../memory.md` — rolling design-decision log.

## Theme-directory mapping (historical note)

Earlier drafts of the Build Spec referred to companions in `01-research/`,
`02-vignettes/`, and `03-software-design/`. Those legacy paths were rewritten
during the Jun 2026 audit (see [`AUDIT-2026-06.md`](AUDIT-2026-06.md) §B3) and
now resolve as `docs/research/`, `docs/vignettes/`, and `docs/design/`. Any
remaining `01-research/` reference in committed prose is a regression.
