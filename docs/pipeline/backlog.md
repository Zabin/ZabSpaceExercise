# Pipeline Backlog

> **Findings & intake register for the documentation-driven-development pipeline.** Two writers:
> **`00-pipeline-manager`** (harvests every invoked skill's findings/recommendations/Outstanding
> Issues after each run, triages every open entry at the start of the next run, and flips
> statuses) and **`00-intake`** (appends `NEW` entries for user-submitted features, bugs, and
> observations). Stage skills never write here — their findings reach this file via the manager's
> harvest step, which is what guarantees a finding stated in a chat summary survives the session
> that stated it. Rows are never deleted: resolved entries flip to `DONE`, rejected ones to
> `REJECTED` with the reason kept.

[↑ Docs index](../INDEX.md) · [Pipeline journal](pipeline-journal.md) ·
[Pipeline README](../../.claude/skills/README.md)

## Lifecycle

```
NEW ──triage──▶ SCHEDULED (rides a named step)  ──that step runs──▶ DONE
        ├─────▶ DEFERRED  (named revisit trigger) ──trigger fires──▶ NEW (re-triage)
        ├─────▶ NEEDS-USER (named decision)       ──user decides───▶ SCHEDULED / REJECTED
        └─────▶ REJECTED  (reason recorded)
IN PIPELINE = the entry's work is the current/next step's explicit target
```

Every open entry carries a live disposition — `SCHEDULED` names the step it rides with,
`DEFERRED` names its revisit trigger, `NEEDS-USER` names the exact decision required. A
Critical/High entry may not be `DEFERRED` without the user's explicit agreement.

## Entries

| ID | Filed | Type | Source | Summary | Sev/Pri | Entry stage | Disposition | Status |
|---|---|---|---|---|---|---|---|---|
| BL-0001 | 2026-07-03 | finding | [VR-1150](../implementation/verification/VR-1150-vignette-selection.md) (run #3, Low) | IP-1150's package text claims "no test covers zero-overrides," contradicted by the shipped tests — package prose correction only, no functional gap | Low | 07 | Fold into IP-1150's next package-maintenance edit; no dedicated run | DEFERRED |
| BL-0002 | 2026-07-03 | design-question | IP-2010 package (run #1) | Unresolved "aware vs. unaware" divergence-signal design question flagged in the package; must be resolved before/during IP-2010 implementation | High | 08 | Decision needed: resolve with the user in the gate check of the `08-code-implementation` run on IP-2010 (the recorded next step) | NEEDS-USER |
| BL-0003 | 2026-07-03 | finding | IP-1140 package (run #1) | FR-6610 trigger/menu divergence documented in IP-1140; needs adjudication | Medium | 09 | Rides the `09-package-verification` run on IP-1140 — adjudicate in that pass | SCHEDULED |
| BL-0004 | 2026-07-03 | finding | Journal position (runs #0–#3, standing) | The 11 as-built packages (IP-1010…IP-1110) carry `VERIFIED` with no `VR-xxxx` evidence on disk — statuses predate the VR convention | Medium | 09 | Revisit trigger: before the first `10-integration-review` runs, retro-verify or have the user explicitly accept the evidence gap | DEFERRED |
| BL-0005 | 2026-07-03 | gate | Authorization round (run #2) | IP-3010 (Research Analytics) was explicitly **not** authorized (MSTR-006 §3); also blocked on IP-2010 reaching `COMPLETE` | — | 08 | Decision needed: re-ask authorization after IP-2010 reaches `VERIFIED` | NEEDS-USER |
| BL-0006 | 2026-07-04 | research-gap | Training-corpus elevation (owner, 2026-07-04) | R600 tier (Training Pedagogy & Instructional Design) scaffolded — index + 8 planned topics — but 0 authored. Downstream manual/vignette skills currently cite R600 as "pending" (NFR-3600, RTM). Author R601 first (everything depends on it). | Medium | 02 | Rides `02-research-training-pedagogy`, R601 → R608 by dependency order; not release-gating for v1 but blocks full NFR-3600 verification | NEW |
| BL-0007 | 2026-07-04 | design-question | Training-corpus elevation (owner, 2026-07-04) | FR-11110 mandates role-scoped *coverage*, not the current per-cell monolith layout (`training/12–14`). Whether to restructure the corpus (e.g. task-oriented modules cutting across cells) is an architecture/requirements-led decision, deferred until R600 (esp. R606 minimalist docs) grounds it. | Low | 03 | Revisit after R606 authors; `08-training-manual-authoring` may then restructure — current layout is an explicitly-recorded seed, not a defect | NEW |
| BL-0008 | 2026-07-04 | doc-defect | Training-corpus elevation (owner, 2026-07-04) | Assumption A12 names the residual risk that training-artifact currency is procedural (no automated gate beyond `test_vignette_tutorials.py`). Consider extending the playbook-test pattern to manual `> Sources:` anchors so a moved code path fails a test. | Low | 04 | Revisit at first `10-integration-review` doc-coherence pass or first observed drift (A12's trigger); candidate NFR if pursued | NEW |
