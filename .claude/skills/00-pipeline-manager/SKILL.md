---
name: 00-pipeline-manager
description: Run the documentation-driven-development pipeline one step at a time with persistent memory — reconcile the pipeline journal (docs/pipeline/pipeline-journal.md) against the tree's real ledgers, determine the single next step, execute it by invoking the owning numbered skill (01-vision through 11-release-readiness), append the run to the journal, and report what to do next. Modes: no args = advance one step; "status" = read-only survey + recommendation, no execution; "log" = show the journal; "sync" = reconcile the journal only; "run <skill> [target]" = execute a specific step out of recommended order (journaled as an override). Use when asked to "run the pipeline," "do the next step," "continue where we left off," "where are we / what's next," or "show the pipeline log." It always stops at human gates (MSTR-006 §3 package authorization, release GO/NO-GO, Critical review findings) and asks rather than proceeding; it performs no stage work itself beyond invoking the owning skill.
---

# Pipeline Manager

The **driver** for the documentation-driven-development pipeline. Where each numbered skill knows
how to do *its* stage, this skill knows *where the pipeline is*: it keeps a persistent journal,
reconciles it against reality, executes the next step by invoking the owning skill, and logs what
happened — so "continue the pipeline" works across sessions without re-deriving everything, and
the project has an auditable record of every pipeline run.

It performs **no stage work itself**. It reads ledgers, invokes exactly one owning skill per
advance, and writes exactly one file of its own: the journal. A manager that starts doing the
stages' work stops being trustworthy about where the pipeline is.

## The journal — `docs/pipeline/pipeline-journal.md`

The manager's persistent memory. Two parts:

1. **Position block** (rewritten every run):

   ```markdown
   ## Position
   - **Updated:** <date> (run #N)
   - **Increment:** <what body of work the pipeline is currently driving>
   - **Pipeline state:** <one line per stage that isn't ✅ idle-and-current — what's open where>
   - **Next step:** `<skill>` on <target> — <one-line why>
   - **Open gates:** <human decisions pending: authorizations, GO calls, unadjudicated findings — or "none">
   ```

2. **Run log** (append-only, newest last — never rewrite or delete old rows):

   ```markdown
   | # | Date | Mode | Skill invoked | Target | Outcome | Next step recorded |
   ```

   One row per manager run, including `status`/`sync` runs (skill invoked = `—`) and runs that
   stopped at a gate (outcome = `GATE: <what's needed>`), so the log shows stalls, not just wins.

**Rules of the journal:**

- **Single writer.** Only this skill writes the journal. The numbered skills know nothing about
  it — they update their own ledgers (Master Build Plan, indexes, `ROADMAP.md`), and the manager
  reads those.
- **Cache of truth, never truth.** The tree's ledgers are authoritative; the journal is memory.
  Skills may legitimately be run directly without the manager, so every run begins by reconciling
  the Position block against the real ledgers — where they disagree, **the tree wins**, and the
  correction is journaled as a sync note rather than silently absorbed.
- Created on first use with a Run 0 sync entry; committed like any other doc
  (`docs(pipeline): run #N — <what happened>`).

## Modes

| Invocation | Behavior |
|---|---|
| *(no args)* | **Advance**: reconcile → determine next step → gate-check → invoke the owning skill → journal → report. One step per run. |
| `status` | Read-only: reconcile in-memory (no journal write unless drift was found and the user confirms syncing it), print the stage survey + recommendation. |
| `log` | Print the Position block and the last ~10 run-log rows; no reconciliation, no writes. |
| `sync` | Reconcile the journal against the ledgers and rewrite the Position block; invoke nothing. Use after doing pipeline work outside the manager. |
| `run <skill> [target]` | Execute a specific step even if it isn't the recommendation (still gate-checked, never gate-bypassed). Journaled with mode `override` and the recommendation it superseded — an override is legitimate, an unrecorded one is drift. |

## Workflow (advance mode)

### Step 1 — Read the journal, then reconcile it against the ledgers

Read `docs/pipeline/pipeline-journal.md` (create with a Run 0 entry if absent). Then verify its
Position block against the authoritative ledgers — check cheapest-first, and always check the
ledgers that bear on the recorded next step:

`ROADMAP.md` · `docs/architecture/INDEX.md` §1 (GDS ladder) · `docs/requirements/` +
`docs/reviews/` (baseline + findings state) · `docs/feature-planning/01-release-plan.md` +
`05-feature-review.md` · `docs/features/feature-index.md` ·
`docs/implementation/00-master-build-plan.md` + `packages/INDEX.md` ·
`docs/implementation/verification/` · `docs/reviews/integration-review-*` +
`release-assessment-*`.

Drift (a status the journal didn't expect, work done outside the manager, a `VERIFIED` with no
Verification Report) is corrected in the Position block now and noted in this run's log row.

### Step 2 — Determine the single next step

From the reconciled position, pick the **highest-leverage unblocked step**, using the pipeline's
own ordering rules (see `README.md`): upstream findings before downstream work; within a stage,
critical-path first; the per-feature loop (06→07→08→09) drains before the per-release stages
(10→11) run. If the journal's recorded next step is still valid, that's the default. If several
steps are genuinely parallel, pick one and name the others in the report.

### Step 3 — Gate check (hard stops — ask, never assume)

Before invoking anything, stop and ask the user (via `AskUserQuestion`) if the step requires:

- **MSTR-006 §3 authorization** — the step would implement a package with no explicit user
  go-ahead on record;
- **a release GO** — the step would flip baseline records;
- **adjudication** — the step builds on a review with unadjudicated Critical/High findings;
- **spending judgment the user reserved** — anything a stage skill's own rules say needs the user.

A gate stop is a complete, successful run: journal it (`GATE: …`), report what decision unblocks
it, and end. Record the user's answer in the journal when it comes — gates are auditable too.

### Step 4 — Execute by invoking the owning skill

Invoke the owning numbered skill via the `Skill` tool with the specific target (e.g.
`07-implementation-planning` on FS-112–115; `08-code-implementation` on IP-1120;
`09-package-verification` on the package just completed). Follow that skill's own rules
completely — the manager adds no shortcuts and removes no obligations. One skill invocation per
advance run; the invoked skill's own one-unit-per-run discipline stands.

### Step 5 — Journal the run

Append the run-log row (mode, skill, target, outcome, next step) and rewrite the Position block
from the post-run state — including the invoked skill's own "Next step" recommendation, which
becomes the journal's recorded next step unless reconciliation says otherwise. Commit the journal
(and nothing else — the invoked skill committed its own work per its own conventions).

### Step 6 — Report

The mandatory completion summary (below), always ending with what the *next* advance will do —
so the user can simply run the manager again.

## Guardrails

- **One step per advance.** No chaining "while I'm here." The journal makes stopping cheap —
  the next run picks up exactly where this one ended.
- **Never bypass a gate**, even in `run <skill>` override mode. Overrides change *which* step
  runs, never *whether* a human decision is required.
- **Never perform stage work inline.** If the next step looks "too small to bother invoking the
  skill for," invoke the skill anyway — the stage's quality gates and summary duties apply to
  small work too.
- **Never edit any ledger the stages own.** Drift between a ledger and reality is routed to the
  owning skill; the manager only corrects its *own* journal.
- **The journal is honest or it is useless.** A run that failed, stalled, or hit a gate is
  journaled as exactly that.

## Quality gate (every run)

- [ ] The journal was read first, and the Position block was verified against the real ledgers —
      not trusted blind.
- [ ] Exactly one skill was invoked (or zero, for status/log/sync/gate runs).
- [ ] Every gate the step touched was stopped at and asked about — none assumed.
- [ ] The run-log row and Position block were written and committed, and match what actually
      happened this run.
- [ ] Nothing outside `docs/pipeline/` was written by the manager itself.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 00 — the manager**; it can be run at any time and is the default entry point
for all pipeline work. End **every** run — advance, status, log, sync, override, or gate stop —
with a chat summary containing exactly these three parts:

1. **What happened** — mode, skill invoked (if any) and its outcome in one line, journal row
   appended, any drift corrected during reconciliation.
2. **Recommendations** — open gates awaiting the user, parallel steps available, drift found and
   who owns it.
3. **Next step** — what the next `/00-pipeline-manager` advance will execute (skill + target +
   why), or the exact decision needed if the pipeline is gated on the user.

Never end a run without naming the next step — that line is the whole point of having a manager.
