---
name: 08-training-manual-authoring
description: Author and update the operator-facing training corpus under docs/training/ — the shared onboarding modules, the role-scoped manual content, the learning path, and the bidirectional feature ⇄ manual traceability matrix — against the FR-11000/NFR-3400–3600 requirements baseline and the shipped behavior of spacesim/. Use when asked to "write/update the manual," "document this feature for operators," "restructure the training corpus," "update the traceability matrix," or when a manual-impact finding (a feature changed and its mapped sections are stale) needs working off. A Stage 08 peer of 08-code-implementation: it executes training-artifact work the way 08 executes code packages — but it writes ONLY docs/training/ (plus that theme's tracker rows), never production code, never vignette YAML (08-vignette-development), never requirements/specs, and it documents as-built behavior only — a capability that hasn't shipped doesn't get manual prose. Layout follows the requirements baseline and architecture, not habit: FR-11110 requires role-scoped coverage, not per-cell monoliths.
---

# Training Manual Authoring

Executes **training-corpus work** — the operator-facing manuals under
[`docs/training/`](../../../docs/training/INDEX.md) — as a Stage 08 peer of
`08-code-implementation`. The training corpus is a co-equal product with the code (MSTR-001 §2,
owner decision 2026-07-04); this skill is how that product gets built and kept current.

## What this is for (and what it is not)

Three kinds of run:

1. **Feature-driven update** (the common case): a code change touched operator-visible behavior;
   the `training/15` forward index names the affected sections; this skill brings them — prose,
   `> Sources:` footers, matrix rows, learning-path rungs — back to as-built truth (FR-11410).
2. **Coverage work**: a capability shipped without role-scoped manual coverage (an FR-11110 gap),
   or a new module is needed; this skill writes it.
3. **Restructuring**: the corpus layout itself changes (e.g., away from per-cell monoliths toward
   whatever the architecture/requirements now indicate). Legitimate — FR-11110 mandates
   role-scoped *coverage*, not any particular file shape — but a restructuring run must keep the
   traceability matrix, INDEX, ROADMAP theme rows, and every inbound link coherent in the same
   change set.

It SHALL NOT write production code or vignette YAML, edit requirements/specs/architecture
(gaps route upstream), or document unshipped behavior. If a pass discovers the *code* is wrong
rather than the manual, that's a bug — route it to `00-intake`, don't paper over it in prose.

## Scope (what this skill owns)

- Every module under `docs/training/` including the traceability matrix and learning path, plus
  `docs/training/INDEX.md` and the training-theme rows of `ROADMAP.md`.
- Screenshots referenced from modules are regenerated via `tools/render_manual.py` /
  `run-spacesim` when the UI changed; the generated files under `docs/manual/` may be refreshed
  as part of a run.

## Inputs (read before writing)

The FR-11000 family + NFR §16 (`docs/requirements/01`/`02`) — the requirements this corpus must
satisfy; [`training/15-manual-traceability.md`](../../../docs/training/15-manual-traceability.md)
— the index this skill maintains in both directions; MSTR-003 (audience/philosophy); authored
R600 topics (`docs/research/encyclopedia/R600-index.md`) — cite them for pedagogical choices
where they exist, and flag the grounding gap to `02-research-training-pedagogy` where they
don't; the shipped behavior itself (drive it with `run-spacesim` when prose describes a flow you
haven't personally observed this session).

## Workflow

1. **Establish the target.** From the invoker, a manual-impact finding, or a `training/15` §15.1
   lookup for recently changed code: the exact sections/modules in scope. Verify against the
   requirements baseline which FR-11xxx leaves the work serves.
2. **Verify as-built behavior** for everything the prose will claim — code reading at minimum,
   a live drive via `run-spacesim` for UI flows. Manuals describe what ships, not what specs
   promise.
3. **Write/update the content** to the corpus conventions: modules single-topic and ~50–300
   lines (NFR-3500, split when exceeded); role-scoped procedure layers deep-link shared concept
   modules instead of duplicating them; audience per MSTR-003/NFR-3600 (operator actions, not
   developer internals); every section ends with a `> Sources:` footer (FR-11120).
4. **Update the traceability matrix in both directions** (FR-11210) and the learning path's
   affected rungs (FR-11320) in the same change set — never "in a follow-up."
5. **Update the theme trackers**: `training/INDEX.md` rows, ROADMAP training-theme rows.
6. **Run the checkable slice**: `python3 -m pytest spacesim/tests/test_vignette_tutorials.py`
   still green if playbook-adjacent prose moved; link-resolution spot-check on everything edited.

## Quality gate (before calling a run done)

- [ ] Every claim in touched prose matches behavior verified this run (code or live drive).
- [ ] Every touched section's `> Sources:` footer is current; matrix forward + reverse rows
      agree; no dangling section ID anywhere in the matrix or learning path.
- [ ] Module size/audience conventions held (NFR-3500/3600); pedagogy choices cite authored R600
      topics or the gap is flagged in the summary.
- [ ] INDEX/ROADMAP rows match the files on disk.
- [ ] Nothing outside `docs/training/` (+ its tracker rows + regenerated `docs/manual/`
      screenshots) was written.

## Pipeline position & completion summary (mandatory, every run)

This skill is a **Stage 08 peer** (artifact execution) of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md)). Upstream: the requirements baseline
(04), R600 research (02), and whatever code change created the manual impact (08-code-implementation).
Downstream: `09-training-manual-review` independently reviews this skill's output — this skill
never reviews its own same-session work.

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — modules/sections written or updated, matrix and learning-path rows moved,
   which FR-11xxx leaves the work served.
2. **Recommendations** — code bugs found (→ `00-intake`), R600 grounding gaps
   (→ `02-research-training-pedagogy`), vignette-side staleness (→ `08-vignette-development`).
3. **Next step** — normally `09-training-manual-review` on the touched scope; name anything else
   that must land first.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
