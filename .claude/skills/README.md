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
| 01 | `01-vision` | Program vision, GDS-00, strategic assumptions register, the standing MSTR-002…007 principles | `docs/master/`, `docs/architecture/` |
| 02 | `02-research-ow-orbital-mechanics` · `02-research-doctrine-exercises` · `02-research-methods-and-validation` · `02-research-future-operations` · `02-research-training-pedagogy` | Research encyclopedia tiers R100/R300/R400/R500/R600 + primers (`02-research-ow-orbital-mechanics` also owns `06-bus-and-payload-operations.md` and the `10-sources-and-methodology.md` citation standard) | `docs/research/` |
| 03 | `03-architecture-design-synthesis` | GDS-01…10 ladder (ConOps, System Context, Architecture, Domain Model, FR/NFR levels, Data Model, UI Architecture, API spec/ICD, RTM level), ADS-xxx, ADRs, the ICD (`INT-xxxx`) | `docs/architecture/`, `docs/design/05-interface-control-document.md` (moves under `architecture/` with GDS-09) |
| 04 | `04-requirements-engineering` | FR-xxxx, NFR-xxxx, Requirements Review, Requirements Traceability Matrix | `docs/requirements/` |
| 05 | `05-feature-decomposition` | Release Plan, Epic Catalog, Feature Catalog, Feature Dependency Graph, Feature Review | `docs/feature-planning/` |
| 06 | `06-feature-specification` | Feature Specifications (FS-xxx, 20-field template) | `docs/features/`, `docs/features/specifications/` |
| 07 | `07-implementation-planning` | Technical Work Breakdown, Implementation Packages (IP-xxxx, 14-field template; `Documentation Updates` opens with a mandatory **Manual impact** entry), Master Build Plan | `docs/implementation/` |
| 08 | `08-code-implementation` · `08-training-manual-authoring` · `08-vignette-development` | Code: source + tests + docs + traceability for exactly one package (status → `COMPLETE`), including its mandatory **Documentation step** (narrow `docs/training/` slice, or Manual-impact hand-offs). Training peers: manual modules / learning path / traceability matrix (`docs/training/`), and vignette YAML + playbook/rung linkage + the `docs/vignettes/` design docs + their verification tests. | `spacesim/`, `docs/training/`, `docs/vignettes/`, ledgers |
| 09 | `09-package-verification` · `09-training-manual-review` | Verification Report (VR-xxxx, incl. the mandatory **Documentation audit**); the **only** skill that writes `VERIFIED`. Training peer: Training Review report (accuracy/traceability/coverage/pedagogy, plus the per-release **learner-walkthrough gate**) under `docs/reviews/`. | `docs/implementation/verification/`, `docs/reviews/` |
| 10 | `10-integration-review` | Integration Report for an epic/release's verified package set | `docs/reviews/` |
| 11 | `11-release-readiness` | Release Assessment (GO/NO-GO) + baseline update on GO (incl. `README.md` status); at every release also the test relevance audit and the dependency-lock check | `docs/reviews/`, trackers, `README.md` |

**Every document has one owner (owner decision, 2026-10-19, `BL-0293`).** A document no stage above
writes is either legacy (`docs/build-spec/` and `docs/design/` apart from the ICD, both retiring
with GDS-06–10, `BL-0292`; `docs/domains/`, being merged into the GDS ladder and retired) or
historical (one-off reviews and audits, scheduled for archiving). A new document needs an owning
stage named here before it is created. Skill files themselves are changed only by owner-authorized
maintenance commits, recorded in the pipeline journal.

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
- **Per package, documentation (owner direction 2026-10-25).** Documentation is built and
  verified inside the package loop, not after it: `07` names each package's **Manual impact**
  (§15.1 rows, manual sections, tutorials/briefs, reference/troubleshooting entries — or `none —
  reason`) and puts "documentation in sync" in its Definition of Done; `08-code-implementation`'s
  **Documentation step** writes the narrow slice it may write and records every larger item as a
  **Manual-impact item**, which `00-pipeline-manager` harvests into the backlog as *due before
  release*; the 08 training peers work those items off in their **maintain loop** (walking each
  procedure as a first-time learner); `09-package-verification`'s **Documentation audit** returns
  a package with an undocumented, unrecorded operator-visible change (Medium).
- **Per release:** 10 → 11 (10's documentation-coherence dimension sweeps the set's Documentation
  audits and open Manual-impact items; 11 needs a current `09-training-manual-review`
  learner-walkthrough gate report, complete §15.1 coverage, green tutorial tests and no open
  Manual-impact item, else NO-GO; the manager will not recommend 11 before then); integration findings loop back through 07 → 08 → 09 before 10 re-runs.
- **Upstream findings never get fixed downstream.** A requirements conflict found at stage 05 goes
  back to 04; an architecture gap found at 06 goes back to 03; a domain-knowledge gap anywhere
  goes to the owning 02 skill. Each skill's summary routes its findings to the owning stage.

## Hard rules the stages share

- Each skill writes **only** its own output scope and reads everything upstream as authoritative.
- No skill before 08 writes production code; no skill after 08 fixes code (findings route back).
  Within stage 08, the peers split the write surface: only `08-code-implementation` writes
  `spacesim/` Python; `08-vignette-development` writes vignette/content YAML and its
  verification tests; `08-training-manual-authoring` writes `docs/training/` only.
  `08-code-implementation` may also write a **narrow** `docs/training/` slice for its own package —
  §15.1/§15.1a/§15.2 matrix rows, `> Sources:` footers, factual line fixes in already-mapped
  sections, and single reference/troubleshooting entries (`08`, `09`, `10*` modules) quoting the
  exact label/message — and hands everything larger to the training peers as a Manual-impact item.
- **No package is `COMPLETE` or `VERIFIED` with an operator-visible change that is neither
  documented nor recorded as a Manual-impact item** (or deferred by the owner on record).
- Statuses are honest ledgers: `08` may write `IN PROGRESS`/`COMPLETE`/`BLOCKED`; only `09` writes
  `VERIFIED`; only the user's explicit GO lets `11` flip the baseline.
- MSTR-006 §3: a fully-specified package is **not** authorization to build it — the user grants
  that explicitly, per package.
- **Tests name their origin** (owner direction, `BL-0310`): every test carries
  `@pytest.mark.verifies(...)` with the requirement (`FR-xxxx`/`NFR-xxxx`), feature (`FS-xxx`) or
  package (`IP-xxxx`) it verifies. `07` names the IDs in `Tests to Add`, `08` applies the marker, `09`
  checks each new test's tag, `04` builds its matrix's Test column from the markers, and `11` audits
  the whole suite for relevance at every release.
