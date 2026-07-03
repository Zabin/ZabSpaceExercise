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
| **Architecture** | Design Synthesis documents (`ADS-xxx`) — domain+research synthesized into architecture/domain-model/requirements/constraints/risks/decisions, upstream of a Feature Spec. | [`architecture/INDEX.md`](architecture/INDEX.md) |
| **Features** | Feature Specifications (`FS-xxx`) — what each capability must do, with no implementation detail. | [`features/feature-index.md`](features/feature-index.md) |
| **Feature Planning** | `05-feature-decomposition` skill output — Release Plan, Epic Catalog, Feature Catalog (`FEAT-xxxx`), Dependency Graph, and Review, decomposed from the approved requirements baseline. Upstream of, and distinct from, `docs/features/`'s `FS-xxx` specs. | [`feature-planning/INDEX.md`](feature-planning/INDEX.md) |
| **Implementation** | Implementation Packages (`IP-xxxx`) — how each Feature Spec is (or would be) built, as-built docs for FS-101-107 and forward designs for FS-201/FS-301, plus the Master Build Plan (sequence/critical path/dependency graph). Supersedes the prior `implementations/` (`IMP-xxxA`) tier, retained for history. | [`implementation/00-master-build-plan.md`](implementation/00-master-build-plan.md) · [`implementation/packages/INDEX.md`](implementation/packages/INDEX.md) |
| **Pipeline** | The pipeline's persistent memory: the `00-pipeline-manager` journal (position + append-only run log) and the backlog (findings harvested from every run + `00-intake`-filed features/bugs, each with a triage disposition). Writers: the manager (both files) and `00-intake` (backlog appends); the tree's ledgers stay authoritative. | [`pipeline/pipeline-journal.md`](pipeline/pipeline-journal.md) · [`pipeline/backlog.md`](pipeline/backlog.md) |
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
