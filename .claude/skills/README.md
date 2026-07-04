# The documentation-driven-development skill pipeline

The numbered skills in this directory form one pipeline. **The number is the run order**: a
skill's inputs are produced by lower-numbered stages, and its output feeds the next higher stage.
Skills sharing a number (the four `02-research-*` skills) are peers at the same stage — run
whichever owns the gap; they have no ordering among themselves. Unnumbered skills
(`run-spacesim`) are utilities outside the pipeline.

Every pipeline skill ends **every** run with a mandatory chat summary: what changed,
recommendations (findings routed to their owning skill), and an explicit **Next step** naming the
skill to run next. The default way to drive the pipeline is `00-pipeline-manager`: it keeps a
persistent journal at `docs/pipeline/pipeline-journal.md` (position + append-only run log,
reconciled against the tree's real ledgers every run — the tree always wins), executes the next
step by invoking the owning skill, and stops at every human gate. Running a stage skill directly
is always legitimate too — the manager's next `sync` picks up the change.

**Nothing surfaced is forgotten:** every finding/recommendation an invoked skill reports is
harvested by the manager into `docs/pipeline/backlog.md` at the end of the run, and every open
backlog entry is triaged (given an explicit disposition — scheduled / deferred-with-trigger /
needs-user / rejected) at the start of the next run, before the next step is chosen. New work
enters the same backlog through `00-intake` (features, bugs, observations — classified, deduped,
and routed to the pipeline stage where they belong), never by side-channel implementation.

## Stages

| # | Skill | Produces | Where |
|---|---|---|---|
| 00 | `00-pipeline-manager` · `00-intake` | Manager: pipeline journal (position + run log), backlog harvest + triage, and one-step-per-run execution of the next stage (`status`/`triage`/`log`/`sync`/`run` modes). Intake: files new features/bugs/observations into the backlog with a recommended entry stage. | `docs/pipeline/`, chat |
| 01 | `01-vision` | Program vision, GDS-00, strategic assumptions register | `docs/master/`, `docs/architecture/` |
| 02 | `02-research-ow-orbital-mechanics` · `02-research-doctrine-exercises` · `02-research-methods-and-validation` · `02-research-future-operations` · `02-research-training-pedagogy` | Research encyclopedia tiers R100/R300/R400/R500/R600 + primers | `docs/research/` |
| 03 | `03-architecture-design-synthesis` | GDS-01…10 ladder (ConOps, System Context, Architecture, Domain Model, FR/NFR levels, Data Model, UI Architecture, API spec/ICD, RTM level), ADS-xxx, ADRs | `docs/architecture/` |
| 04 | `04-requirements-engineering` | FR-xxxx, NFR-xxxx, Requirements Review, Requirements Traceability Matrix | `docs/requirements/` |
| 05 | `05-feature-decomposition` | Release Plan, Epic Catalog, Feature Catalog, Feature Dependency Graph, Feature Review | `docs/feature-planning/` |
| 06 | `06-feature-specification` | Feature Specifications (FS-xxx, 20-field template) | `docs/features/`, `docs/features/specifications/` |
| 07 | `07-implementation-planning` | Technical Work Breakdown, Implementation Packages (IP-xxxx, 14-field template), Master Build Plan | `docs/implementation/` |
| 08 | `08-code-implementation` · `08-training-manual-authoring` · `08-vignette-development` | Code: source + tests + docs + traceability for exactly one package (status → `COMPLETE`). Training peers: manual modules / learning path / traceability matrix (`docs/training/`), and vignette YAML + playbook/rung linkage + their verification tests. | `spacesim/`, `docs/training/`, ledgers |
| 09 | `09-package-verification` · `09-training-manual-review` | Verification Report (VR-xxxx); the **only** skill that writes `VERIFIED`. Training peer: Training Review report (accuracy/traceability/coverage/pedagogy) under `docs/reviews/`. | `docs/implementation/verification/`, `docs/reviews/` |
| 10 | `10-integration-review` | Integration Report for an epic/release's verified package set | `docs/reviews/` |
| 11 | `11-release-readiness` | Release Assessment (GO/NO-GO) + baseline update on GO | `docs/reviews/`, trackers |

## Iteration loops

The pipeline is iterative, not a one-way waterfall — but every loop re-enters at a numbered stage
and flows forward from there:

- **Per feature:** 06 → 07 → (08 → 09 per package) — repeated for each feature in a release bucket.
- **Per package:** 08 → 09; a `RETURNED` verification loops back to 08 on the same package.
- **Per training artifact:** `08-training-manual-authoring` / `08-vignette-development` →
  `09-training-manual-review`; findings loop back to the owning 08 peer. A feature-changing code
  package (08) that touches operator-visible behavior creates the manual impact this loop works
  off (`docs/training/15-manual-traceability.md` §15.1 is the routing table) — training-corpus
  currency is release-gating (FR-11410; assumption A12).
- **Per release:** 10 → 11; integration findings loop back through 07 → 08 → 09 before 10 re-runs.
- **Upstream findings never get fixed downstream.** A requirements conflict found at stage 05 goes
  back to 04; an architecture gap found at 06 goes back to 03; a domain-knowledge gap anywhere
  goes to the owning 02 skill. Each skill's summary routes its findings to the owning stage.

## Hard rules the stages share

- Each skill writes **only** its own output scope and reads everything upstream as authoritative.
- No skill before 08 writes production code; no skill after 08 fixes code (findings route back).
  Within stage 08, the peers split the write surface: only `08-code-implementation` writes
  `spacesim/` Python; `08-vignette-development` writes vignette/content YAML and its
  verification tests; `08-training-manual-authoring` writes `docs/training/` only.
- Statuses are honest ledgers: `08` may write `IN PROGRESS`/`COMPLETE`/`BLOCKED`; only `09` writes
  `VERIFIED`; only the user's explicit GO lets `11` flip the baseline.
- MSTR-006 §3: a fully-specified package is **not** authorization to build it — the user grants
  that explicitly, per package.
