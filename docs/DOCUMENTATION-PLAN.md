# Documentation Plan & Information Architecture

How the project's prose documentation is organized, and **why it is shaped for Claude Code
reference**. This file is the rationale; `docs/INDEX.md` is the live router you actually navigate
from.

## Goals

1. **Single-topic files Claude can read whole.** Every file is small enough (~50–300 lines) that
   Claude Code can open it fully and spend its context on the *relevant* topic instead of scrolling
   a 1,200-line monolith. The two former monoliths — the Build Specification (1,200+ lines) and the
   Training Manual (500+ lines) — are split into focused section modules.
2. **An index at every level.** A master `docs/INDEX.md` plus one `INDEX.md` per theme act as
   routers: Claude reads an index, then opens exactly the module it needs. No guessing which file
   holds a topic.
3. **Stable, descriptive filenames.** Files are named by topic, not by an opaque running number, so
   a glob/search lands on the right file. Within each theme the numeric prefix only sets reading
   order; it never collides (the old flat layout had three different `04-*.md` files at the root).
4. **Themed directories.** Five themes, each a directory: `build-spec/`, `training/`, `design/`,
   `research/`, `vignettes/`. The previous flat root interleaved three unrelated numbered series
   (research 01–06, vignettes 00–08, design 01–15) so leading numbers repeated and the implied
   `01-research/` / `02-vignettes/` directories (referenced in `CLAUDE.md`) did not actually exist.
   This plan makes those directories real.

## Hierarchy

```
docs/
├── INDEX.md                     ← master router (start here)
├── DOCUMENTATION-PLAN.md        ← this file
├── FUTURE-WORK.md               ← cross-cutting living TODO (v1.1+)
│
├── build-spec/                  ← THEME 1: the binding v1 spec (was 00-BUILD-SPECIFICATION.md)
│   ├── INDEX.md
│   ├── 01-context-and-scope.md            (§0–4: how-to-read, context, stakeholders, scope, decisions)
│   ├── 02-requirements-and-operations.md  (§5–6: functional requirements, hot-seat ops)
│   ├── 03-architecture-and-data.md        (§7–8: architecture, data formats)
│   ├── 04-nfr-milestones-and-risks.md     (§9–12: NFRs, milestones M0–M7, risks, glossary)
│   ├── 05-workflows-and-state-machines.md (§13–14: operator workflows, state machines)
│   ├── 06-test-plan-and-schedule.md       (§15–17 Part 3: test plan, schedule, open items)
│   ├── 07-operator-console.md             (§16 Part 4: the v1 operator console / UI spec)
│   └── 08-ssn.md                          (§17 Part 4: mock Space Surveillance Network)
│
├── training/                    ← THEME 2: user training (was docs/TRAINING-MANUAL.md)
│   ├── INDEX.md
│   ├── 01-install-and-run.md
│   ├── 02-interface.md
│   ├── 03-first-exercise.md
│   ├── 04-guided-vignette.md
│   ├── 05-core-concepts.md
│   ├── 06-the-eight-vignettes.md
│   ├── 07-white-cell-facilitation.md
│   ├── 08-http-api-reference.md
│   └── 09-troubleshooting-and-glossary.md
│
├── design/                      ← architecture & design corpus (the "how")
│   ├── INDEX.md
│   └── 01-architecture-overview … 15-worked-asset-templates.md
│
├── research/                    ← doctrine & domain primers (the "why")
│   ├── INDEX.md
│   └── 01-doctrine-western … 06-bus-and-payload-operations.md
│
├── vignettes/                   ← scenario library (framework + 19 vignettes)
│   ├── INDEX.md
│   └── 00-vignette-framework … 08-multi-domain-taiwan.md
│
└── manual/                      ← generated UI screenshots (tools/render_manual.py) + INDEX.md
```

`README.md`, `CLAUDE.md`, and `memory.md` stay at the repo root (entry points / agent guides).

## What changed in the refactor

- **Build Specification** `00-BUILD-SPECIFICATION.md` → eight modules under `build-spec/`. Its old
  Part 3 / Part 4 split (which produced a confusing duplicate `§16`/`§17` numbering) is resolved:
  the Part 4 console/SSN sections — the ones cited from code — own `07-operator-console.md` and
  `08-ssn.md`; the Part 3 schedule/open-items live in `06-test-plan-and-schedule.md`, labelled as
  Part 3 so the numbers no longer appear to clash.
- **Training Manual** `docs/TRAINING-MANUAL.md` → nine modules under `training/`. Screenshot links
  changed from `manual/…png` to `../manual/…png` (the screenshots stay in `docs/manual/`, written
  by `tools/render_manual.py`).
- **Root corpus** (research 01–06, vignettes 00–08, design 01–15) → moved by `git mv` into
  `design/`, `research/`, `vignettes/` with filenames preserved (history intact; bare prose
  mentions still resolve by name).
- **`docs/OPERATOR-UI-DESIGN.md`** (a retired pointer stub) removed; its routing role is taken by
  `build-spec/INDEX.md` and the master index.
- **Section anchors preserved.** Module files keep their original `§N.x` headings, so the four
  source-code docstrings that cite `…§16.9` / `§10` still point at a real heading — only the file
  path in those citations was updated to the new module.

## Reference rules (for future edits)

- **Authority unchanged:** on any conflict the Build Spec wins — now read it via
  `docs/build-spec/INDEX.md`.
- **Add a doc:** drop it in the right theme dir, give it the next numeric prefix, and add one line
  to that theme's `INDEX.md`. If it introduces a new theme, add a dir + `INDEX.md` and link it from
  `docs/INDEX.md`.
- **Keep modules small.** If a module passes ~300 lines, split it and update the theme index.
- **Cross-link by name.** Prose may mention a file by bare name (e.g. `04-data-model.md`); the
  indexes carry the authoritative path. Only the master/theme indexes and `CLAUDE.md` must carry
  full paths.
