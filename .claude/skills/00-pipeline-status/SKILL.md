---
name: 00-pipeline-status
description: Survey the documentation-driven-development pipeline end to end and report where the project currently stands — which stage each increment of work is at, which artifacts are missing/stale/blocked, and exactly which numbered skill to run next and on what. Read-only navigator; changes nothing. Use when asked "where are we," "what's next," "what should I run," "show the pipeline status," at the start of a session before picking up pipeline work, or after a release closes to orient the next increment. Do not use it to perform any stage's actual work — it routes to the owning skill (01-vision through 11-release-readiness) and stops.
---

# Pipeline Status

The **navigator** for the documentation-driven-development pipeline. It reads the tree, maps every
stage's artifacts against what the stage's owning skill says "done" looks like, and tells the user
exactly one thing they can act on: **what to run next, on what, and why.** It never performs stage
work itself — a navigator that starts doing the driving stops being trustworthy about the map.

## The pipeline it reports on

| Stage | Skill | Primary artifacts checked |
|---|---|---|
| 01 | `01-vision` | `docs/master/MSTR-001`, `docs/architecture/00-vision.md`, strategic-assumptions register |
| 02 | `02-research-*` (×4, parallel) | `docs/research/encyclopedia/R100/R300/R400/R500-index.md` tier status, primer freshness |
| 03 | `03-architecture-design-synthesis` | `docs/architecture/INDEX.md` §1 GDS ladder statuses + merge gates, ADS corpus, ADRs |
| 04 | `04-requirements-engineering` | `docs/requirements/` four deliverables, review findings adjudicated, changelog |
| 05 | `05-feature-decomposition` | `docs/feature-planning/` five deliverables, Feature Review findings state |
| 06 | `06-feature-specification` | `docs/features/feature-index.md` — which catalog/release-bucket features have approved specs |
| 07 | `07-implementation-planning` | `docs/implementation/` TWBS, `packages/INDEX.md`, Master Build Plan coverage of approved specs |
| 08 | `08-code-implementation` | Master Build Plan statuses: `READY`/`IN PROGRESS`/`BLOCKED`/`COMPLETE` rows + authorization gates |
| 09 | `09-package-verification` | `COMPLETE` packages awaiting VRs; `docs/implementation/verification/` |
| 10 | `10-integration-review` | Tranches fully `VERIFIED` but not integration-reviewed; `docs/reviews/integration-review-*` |
| 11 | `11-release-readiness` | Release buckets whose scope is reviewed clean but unassessed; `docs/reviews/release-assessment-*` |

Cross-cutting: `ROADMAP.md` (does it agree with the per-stage reality?), the test suite's headline
state, and any `BLOCKED` item anywhere with its stated blocker.

## Workflow

1. **Sweep the artifacts** in the table above — status tables and indexes first (`ROADMAP.md`,
   `docs/architecture/INDEX.md` §1, `docs/implementation/00-master-build-plan.md`,
   `docs/feature-planning/01-release-plan.md`, the tier indexes), opening individual documents
   only where a status is ambiguous or suspected stale.
2. **Detect drift**, not just state: a tracker saying ✅ while the artifact contradicts it, an
   index disagreeing with the plan it mirrors, a `VERIFIED` with no Verification Report on disk.
   Drift is a first-class finding — the pipeline's ledgers are only useful while they're honest.
3. **Report** in chat (no file written unless the user asks):
   - **Stage table** — one row per stage: status (✅ current / 🚧 in progress / ⛔ gap / 💤 idle),
     one-line evidence.
   - **Blockers & drift** — anything stopping forward motion, each with its owning skill.
   - **The recommendation** — the single next action: which skill, which target (a GDS level, a
     feature ID, a package ID, a review scope), and why it's the highest-leverage next step.
     Where genuinely parallel work exists (e.g. two `02-research-*` gaps), say so, but still lead
     with one primary recommendation.
4. **Change nothing.** Not even "harmless" tracker fixes — drift found here is routed to the
   owning skill so the correction itself stays traceable.

## Quality gate

- [ ] Every stage row is backed by an artifact actually read this run, not remembered.
- [ ] Every ⛔/🚧/blocker names its owning skill and concrete target.
- [ ] Exactly one primary recommendation, actionable as a single skill invocation.
- [ ] Nothing in the tree was modified.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 00 — the navigator**; it can be run at any time and is the default entry
point when the user doesn't know where the pipeline stands. Its entire output *is* the completion
summary: the stage table, the blockers, and the explicit **Next step** naming the skill and target
to run. Never end a run without that recommendation — routing is this skill's one job.
