<!--
Thanks for contributing to the Space Control & Orbital Warfare Exercise Simulator.
Fill in the sections below; delete any change-type checklist that doesn't apply.
See CLAUDE.md for the project's load-bearing invariants and test-driven workflow.
-->

## Summary

<!-- 1-3 bullets: what changed and why. Focus on the "why," not a line-by-line diff narration. -->

-

## Change type

<!-- Check all that apply; use the matching checklist(s) below. -->

- [ ] Engine (`spacesim/engine/`)
- [ ] Session / API (`spacesim/session/`)
- [ ] Web UI (`spacesim/ui_web/`)
- [ ] Vignette / content (`spacesim/content/`, `*.yaml`)
- [ ] Docs / research (`docs/`)
- [ ] Other (tooling, tests-only, config)

## Test plan

<!-- What you ran, and what a reviewer should run to confirm. -->

- [ ] `python3 -m pytest` passes locally
- [ ]

---

### If Engine (`spacesim/engine/`)

- [ ] No wall-clock reads, no global RNG outside `engine/rng.py` (the import-guard test enforces this).
- [ ] `engine/` still imports no UI or transport code.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` and `test_import_guard.py` pass.
- [ ] Fog-of-war filtering, if touched, stays at the `SessionAPI`/`CellController` boundary — not pushed into `engine/`.
- [ ] New hard-coded constants carry a `# Source: docs/research/...` comment per `docs/research/10-sources-and-methodology.md` §4, if grounded in real-world data.

### If Session / API or Web UI

- [ ] Cell-scoped endpoints still go through `CellController`'s fog-of-war filter; no new ground-truth leak.
- [ ] Multiplayer-relevant changes (clock, locking, session state) tested with more than one connected client/tab where applicable.
- [ ] UI changes manually exercised in a browser (golden path + at least one edge case) — note what you checked, since automated tests don't cover the front end.

### If Vignette / content

- [ ] Vignette loads and runs (`python3 -m pytest spacesim/tests/` covering vignette load, or manual session start).
- [ ] `intro_brief` and `objectives` are consistent with each other (see `docs/research/encyclopedia/R305-mission-analysis.md`).
- [ ] Any new doctrine/realism claim embedded in the content is traceable to an existing `docs/research/` source, not invented.

### If Docs / research

- [ ] Every doctrinal/numerical/named-system claim has an inline citation at the claim site.
- [ ] Every `##` section ends with a `### Sources` subsection (live URL + Wayback snapshot + accessed date), per `docs/research/10-sources-and-methodology.md`.
- [ ] No claim rests on a single Tier-D (advocacy/Wikipedia) source.
- [ ] If a citation could not be verified (e.g. no network access), it's explicitly flagged `[UNVERIFIED]` rather than guessed, and the file's `Status` reflects that it isn't done.
- [ ] Relevant index file(s) (`docs/research/encyclopedia/R*00-index.md`, `docs/architecture/INDEX.md`, `ROADMAP.md`) updated in the same PR.

---

## Anything reviewers should pay special attention to?

<!-- Optional: ambiguous design calls, deliberate scope cuts, known follow-ups. -->
