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
| BL-0002 | 2026-07-03 | design-question | IP-2010 package (run #1) | Unresolved "aware vs. unaware" divergence-signal design question flagged in the package; must be resolved before/during IP-2010 implementation | High | 07 | **Resolved (run #4):** user chose to instrument an explicit decision-time signal rather than a post-hoc heuristic. `07-implementation-planning` amended `IP-2010` to v1.1 (`custody_confidence_at_decision` captured in `engine/orders.py`'s `_exec_payload()` via a new `engine/custody.py` helper, read back — never recomputed — by `score_belief_truth_divergence`); Architecture Components, Files to Modify, Implementation Tasks, Tests to Add, Definition of Done, Verification Checklist, Risks, and Rollback Considerations all updated; `00-master-build-plan.md`'s stale risk note corrected. Committed `d07ebe8`, pushed, draft PR [#45](https://github.com/Zabin/ZabSpaceExercise/pull/45). No open design question remains on `IP-2010`; still `READY`+authorized, unchanged. | DONE |
| BL-0003 | 2026-07-03 | finding | IP-1140 package (run #1) | FR-6610 trigger/menu divergence documented in IP-1140; needs adjudication | Medium | 09 | Rides the `09-package-verification` run on IP-1140 — adjudicate in that pass | SCHEDULED |
| BL-0004 | 2026-07-03 | finding | Journal position (runs #0–#3, standing) | The 11 as-built packages (IP-1010…IP-1110) carry `VERIFIED` with no `VR-xxxx` evidence on disk — statuses predate the VR convention | Medium | 09 | Revisit trigger: before the first `10-integration-review` runs, retro-verify or have the user explicitly accept the evidence gap | DEFERRED |
| BL-0005 | 2026-07-03 | gate | Authorization round (run #2) | IP-3010 (Research Analytics) was explicitly **not** authorized (MSTR-006 §3); its other blocker (IP-2010 → `COMPLETE`) cleared 2026-07-03 (run #5) — authorization is now the sole remaining blocker | — | 08 | Decision needed: ask the user directly whether to authorize `IP-3010` now that its prerequisite work is done, or continue waiting | NEEDS-USER |
| BL-0006 | 2026-07-03 | finding | `08-code-implementation` run (run #5, IP-2010 Outstanding Issue 1) | Cyber orders build their payload in `OrderSystem._plan_cyber`, a separate path from `_exec_payload()` — cyber-effect decisions never carry `custody_confidence_at_decision` and are excluded from `score_belief_truth_divergence`/`score_custody_quality` coverage. In-scope per IP-2010's literal "Files to Modify" (only `_exec_payload` was named), not a defect. | Low | 07 | Defer until either (a) a future package specifically needs cyber-targeted belief-truth-divergence scoring, or (b) `10-integration-review` flags the coverage gap as material | DEFERRED |
| BL-0007 | 2026-07-03 | finding | `08-code-implementation` run (run #5, IP-2010 Outstanding Issue 3) | `spacesim/ui_web/static/index.html` was modified (new assessment panel markup) though not explicitly named in IP-2010's "Files to Modify" — implied by "a new report panel" (mirrors the AAR panel's own markup+JS split), not scope creep, but should be confirmed rather than assumed | Low | 09 | Rides the `09-package-verification` run on IP-2010 — confirm the implied-scope inclusion was appropriate as part of that pass's "no unrelated file touched" checklist item | SCHEDULED |
