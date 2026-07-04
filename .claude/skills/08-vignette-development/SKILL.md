---
name: 08-vignette-development
description: Author and update vignettes — the YAML scenario files under spacesim/content/vignettes/ with their intro_brief, tutorial, coaching, objectives, and parameter blocks — and keep each vignette wired into the training corpus: its learning-path rung (docs/training/16), its playbook entry (docs/training/11), and the machine-verification that backs them (spacesim/tests/test_vignette_tutorials.py). Use when asked to "add/modify a vignette," "update the brief/tutorial for vignette X," "fix a vignette the engine outgrew," "re-sequence the learning path," or when a code change altered behavior a vignette's script or brief depends on. A Stage 08 peer of 08-code-implementation: vignettes are content-as-data (a load-bearing invariant — scenario logic stays in YAML + inject/effect primitives, never Python), so this skill writes vignette YAML and its linked training-doc entries plus their tests, but never engine/session/UI code — if a vignette needs a mechanic the engine lacks, that's a feature for the pipeline (00-intake), not code written here.
---

# Vignette Development

Executes **vignette work** — the scenario library under
`spacesim/content/vignettes/*.yaml` and its training-corpus linkage — as a Stage 08 peer of
`08-code-implementation`. The vignettes are the learning path's rungs (GDS-01 "The learning path
is an operational workflow"): they are training artifacts that happen to be runnable, and they
carry the same co-equal-product status (MSTR-001 §2) and currency requirements (FR-11310/11320/
11410/11420) as the manuals.

## What this is for (and what it is not)

1. **New vignette**: author the YAML (schema per `spacesim/content/vignette.py`; design framework
   per `docs/vignettes/00-vignette-framework.md`) with its per-cell `intro_brief`, `objectives`,
   parameters, and — for anything on the learning path's core progression — a `tutorial:` step
   script; place it on exactly one learning-path rung with prerequisites (FR-11310/11320); add
   its playbook entry; extend the verification test to drive its script.
2. **Currency update**: shipped behavior changed under an existing vignette (a verb renamed, a
   gate tightened, an objective now unreachable); re-verify the script against the engine, fix
   the YAML/brief/playbook/rung, keep `test_vignette_tutorials.py` green.
3. **Learning-path re-sequencing**: move/re-rank rungs as the library grows — every vignette on
   exactly one rung, prerequisites still a DAG a novice can actually walk.

It SHALL NOT write engine/session/UI code (a vignette needing a missing mechanic files the gap
via `00-intake` — content-as-data cuts both ways), edit manuals beyond the vignette-linked
entries it owns (`training/11` playbook entries, `training/16` rungs — whole-module work belongs
to `08-training-manual-authoring`), or invent doctrine (realism claims trace to `docs/research/`
sources, per the vignette PR checklist).

## Scope (what this skill owns)

- `spacesim/content/vignettes/*.yaml` (and `spacesim/content/inject_library.yaml` when a
  vignette pass extends it).
- The per-vignette entries in `docs/training/11-vignette-playbooks.md`, the rungs of
  `docs/training/16-learning-path.md`, and `docs/vignettes/` index rows.
- `spacesim/tests/test_vignette_tutorials.py` (and the vignette-load tests) — the one place this
  skill writes test code, because FR-11420 makes the test part of the artifact.

## Workflow

1. **Establish the target** and its requirements footing (which FR-11xxx / FR-5000 leaves the
   work serves). For a new vignette: which rung it occupies, what it teaches that the previous
   rung didn't, which cell(s) it exercises — cite R600 topics (R605 progression design) once
   authored; flag the grounding gap until then.
2. **Author/edit the YAML.** Briefs honor fog-of-war at authoring time (Blue's brief never
   reveals Red's hidden dispositions); parameters typed with safe defaults; `intro_brief` and
   `objectives` mutually consistent (per the PR-template check); doctrine/realism claims traced
   to `docs/research/` sources.
3. **Verify against the engine, not by reading.** Load and run it (`python3 -m pytest
   spacesim/tests/test_vignettes.py test_vignette_library.py` + a `run-spacesim` drive when the
   change is behavioral); for tutorial-bearing vignettes, extend/adjust
   `test_vignette_tutorials.py` so every documented objective-flip is asserted (FR-11420).
4. **Wire the training linkage in the same change set** (FR-11320/11410): playbook entry, rung,
   prerequisites, and the `training/15` matrix rows that name vignette-backed features.
5. **Update trackers**: `docs/vignettes/INDEX.md`, vignette counts where they appear (README,
   CLAUDE.md status line) if the library size changed, ROADMAP theme rows.
6. **Full suite green** (`python3 -m pytest`) before calling it done — vignettes are load-bearing
   test fixtures for half the session-layer suite.

## Quality gate (before calling a run done)

- [ ] YAML loads and runs; full suite + `test_vignette_tutorials.py` green.
- [ ] Every tutorial step the docs claim was driven through the real engine by a test, or the
      blocking gate (ROE / weapons-quality / window) is documented in the block's `expect`.
- [ ] The vignette sits on exactly one learning-path rung; prerequisites resolve; playbook entry
      exists and matches the script.
- [ ] Briefs leak nothing across the fog boundary; realism claims carry research sources.
- [ ] No engine/session/UI code was touched; any needed mechanic was filed, not built.

## Pipeline position & completion summary (mandatory, every run)

This skill is a **Stage 08 peer** (artifact execution) of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md)). Upstream: the vignette framework
(`docs/vignettes/`), FR-5000/FR-11000 requirements, R300 (exercise design) and R600 (pedagogy)
research. Downstream: `09-training-manual-review` reviews the training-facing surface;
`09-package-verification` remains the verifier for any code-side package a vignette gap spawned.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — vignettes authored/updated, rungs/playbooks/tests moved, suite result.
2. **Recommendations** — engine gaps filed via `00-intake`, manual-side impacts routed to
   `08-training-manual-authoring`, R600 grounding gaps to `02-research-training-pedagogy`.
3. **Next step** — normally `09-training-manual-review` on the touched training surface, or the
   filed intake item's triage if the run was blocked by a missing mechanic.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
