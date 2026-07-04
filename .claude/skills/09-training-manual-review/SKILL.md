---
name: 09-training-manual-review
description: Independently review the training corpus — manual modules, the learning path, vignette briefs/tutorials/playbook entries, and the bidirectional traceability matrix — against shipped behavior and the FR-11000/NFR-3400–3600 baseline, producing a Training Review report under docs/reviews/. Checks accuracy (prose vs. as-built behavior, driven live where warranted), traceability integrity (Sources footers ⇄ matrix rows ⇄ learning-path links, both directions), coverage (every operator-visible capability reaches every role that exercises it), and pedagogy (audience fit per MSTR-003/NFR-3600, R600-grounded where the tier has authored topics). Use when asked to "review the manual," "check the training docs against the code," "audit the learning path," or after any 08-training-manual-authoring / 08-vignette-development run. A Stage 09 peer of 09-package-verification: review-only — it reports and routes findings, never fixes prose, YAML, or code, and never reviews its own session's authoring work.
---

# Training Manual Review

Independently reviews the **training corpus** the way `09-package-verification` reviews a code
package: against the requirements baseline (FR-11000 family, NFR §16) and against **shipped
behavior**, not against what the authoring pass said it did. The training corpus is a co-equal
product (MSTR-001 §2); this is its verification stage, and assumption **A12** (currency is
enforced procedurally) is only sound if this review actually runs.

## What this is for (and what it is not)

It answers: *does the training corpus, as it stands on disk, teach the tool that actually
ships?* It SHALL NOT fix anything it finds — findings route to the owning skill
(`08-training-manual-authoring` for manual prose, `08-vignette-development` for
vignette/playbook/rung defects, `00-intake` for code bugs the review exposes, upstream skills
for requirements/research gaps). It never reviews training artifacts authored in its own
session — independence is the point.

## Scope selection

One of: the sections touched by a named authoring run (the common case, its "Next step"), a
named module set ("review the White-facing corpus"), the learning path end-to-end, or the whole
corpus (a periodic audit — expect to sample rather than exhaust; say what was sampled).

## What to check (the review dimensions)

1. **Accuracy** — sampled prose claims vs. as-built behavior: verbs/panels/endpoints exist and
   behave as described. Drive the real app (`run-spacesim`) for any claim about an interactive
   flow that hasn't been observed this session; run
   `python3 -m pytest spacesim/tests/test_vignette_tutorials.py` for the machine-checkable
   slice (FR-11420/NFR-3400). A manual describing removed or renamed behavior is a Critical
   finding — it actively mis-trains.
2. **Traceability integrity** — `> Sources:` footers current (named paths exist); `training/15`
   forward and reverse tables mutually consistent and consistent with the footers (FR-11120/
   11210); learning-path rung prerequisites and playbook links resolve (FR-11320); no orphaned
   section IDs anywhere.
3. **Coverage** — every operator-visible capability in the forward index reaches role-scoped
   content for every role that can exercise it (FR-11110); every shipped vignette on exactly one
   rung (FR-11310); recently shipped features (check the Master Build Plan's latest COMPLETE/
   VERIFIED packages) present in the index at all.
4. **Pedagogy** — audience fit per MSTR-003/NFR-3600 (operator actions, jargon introduced or
   glossary-linked, module sizes per NFR-3500); sequencing/scaffolding choices cite authored
   R600 topics; where R600 is unauthored, record "ungrounded, pending R6xx" as a tracked gap,
   not a violation.

## Output

**`docs/reviews/training-review-<scope>.md`** (matching `docs/reviews/`' descriptive naming),
containing: scope + commit reviewed, what was actually exercised per dimension (a clean
dimension states what was checked, not just "OK"), and findings one row each —
`Finding | Artifact(s) | Description | Severity | Recommended owner` — on the project's
Critical/High/Medium/Low scale. Update ROADMAP's review theme if it tracks review documents.

## Quality gate

- [ ] All four dimensions exercised and evidenced; sampling stated where sampling was used.
- [ ] Playbook verification suite run against the reviewed commit, result recorded.
- [ ] Every finding has severity + concrete recommended owner; nothing was fixed in-pass.
- [ ] Independence held: nothing reviewed was authored in this session.
- [ ] Nothing but the report (and review-tracker rows) was written.

## Pipeline position & completion summary (mandatory, every run)

This skill is a **Stage 09 peer** (independent verification) of the documentation-driven-development
pipeline (see [`.claude/skills/README.md`](../README.md)). Upstream:
`08-training-manual-authoring` and `08-vignette-development`. Downstream: `10-integration-review`
(whose documentation-coherence dimension leans on this skill's reports) and `11-release-readiness`
(a release whose training corpus is stale ships mis-training — surface it there).

End **every** invocation with a chat summary containing exactly these three parts:

1. **What changed** — the report written (path), scope, headline result (clean / N findings by
   severity).
2. **Recommendations** — each finding routed: manual prose → `08-training-manual-authoring`;
   vignette/rung/playbook → `08-vignette-development`; code bugs → `00-intake`; requirements
   conflicts → `04-requirements-engineering`; pedagogy grounding gaps →
   `02-research-training-pedagogy`.
3. **Next step** — clean: the pipeline work this review was gating (often `10-integration-review`
   or a release pass); findings: the owning skill for the most severe finding first.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and
the user relies on each stage's summary to know what to invoke next.
