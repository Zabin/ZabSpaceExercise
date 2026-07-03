# ADR-0033 — A dedicated multi-run/cohort research-export interface is authorized (supersedes ADR-0029)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0033
- **Title:** Introduce a dedicated research-export interface for multi-run/cohort instrument-grade
  research use
- **Status:** Accepted
- **Supersedes:** [ADR-0029](ADR-0029-assessment-scoring-workflow-ownership.md) (retained, marked
  Superseded, not deleted)

## Context

`docs/reviews/requirements-domain-backfill-report.md` §3.2 (produced by a `requirements-engineering`
pass against DOM-004, the Research Framework, and its output `FS-301` Research Analytics) found
that FS-301's core capability — a purpose-built export/cohort-management layer producing structured
per-run records (vignette ID, seed, condition-label metadata, per-dimension rubric results) across
many seeded runs — directly conflicts with ADR-0029. ADR-0029's own Decision states that "the
existing CSV/JSON export at `/api/sessions/{sid}/aar/export.{csv,json}}`... is treated as
sufficient for the 'researchers / assessment designers' stakeholder's needs... no new dedicated
export/analysis interface or owning subsystem is introduced," and its Alternatives Considered
section explicitly names and rejects "introduce a dedicated export/analysis interface for
assessment designers" — precisely what FS-301 proposes.

Unlike the ADR-0017/`CR-19` conflict (a narrow carve-out within the existing decision), this
conflict is direct: FS-301 is functionally the alternative ADR-0029 already considered and
rejected. The project owner, asked directly whether to (a) rescope FS-301 to the existing export
path instead, (b) supersede ADR-0029 to authorize FS-301 as designed, or (c) reject the capability
outright, chose (b).

ADR-0029's own Consequences section anticipated this possibility: *"If a concrete unmet need for
assessment designers emerges later (e.g. a specific aggregate metric AAR export doesn't capture),
that would be a new, separate decision — this ADR does not preclude revisiting the question."*
This ADR is that revisit.

## Decision

A dedicated multi-run/cohort research-export interface, as FS-301 describes, is authorized:

- **Structured export across many seeded runs.** The system may batch-run N seeded simulations of
  a vignette and produce structured per-run records — vignette ID, seed, experimental condition
  label, and per-dimension rubric results (FS-201's output, per `CR-19`/ADR-0032) — for external
  analysis by a researcher.
- **A new export surface, distinct from the existing per-session AAR export.** This is,
  deliberately, the alternative ADR-0029 previously rejected: a dedicated interface for the
  researchers/assessment-designers stakeholder, not merely repeated use of the existing
  per-session `/api/sessions/{sid}/aar/export.{csv,json}` path.
- **No relaxation of engine determinism.** Per DOM-005 §6 (already restated in `NFR-1500`), batch
  variability is characterized by driving the engine across many seeds externally — never by
  introducing non-determinism inside `engine/`. This ADR does not touch that invariant.
- **No human-subjects-research feature is authorized by this decision.** Per DOM-004 §6 and
  Candidate Requirement `CR-21`, cross-institution or de-identified human-subjects data collection
  remains out of scope without separate authorization and the institution's own IRB/ethics process
  — this ADR authorizes the export mechanism, not any particular research use of it.

## Alternatives Considered

- **Rescope FS-301 to a documented batch-run procedure over the existing per-session CSV/JSON
  export** (no new interface — concatenate N existing per-session exports with condition-label
  metadata attached externally) — **not adopted**: the project owner judged this insufficiently
  different from the status quo ADR-0029 already found wanting for this use case, and chose to
  authorize the dedicated interface FS-301 originally proposed instead.
- **Reject FS-301's capability outright, leave ADR-0029 unamended** — **not adopted**: would leave
  `CR-20` permanently blocked and `IP-3010` permanently cancelled with no path forward, which the
  project owner did not choose.
- **Leave the decision to a future revisit without acting now** — not adopted: the project owner
  chose to resolve the conflict directly rather than defer it further, consistent with ADR-0029's
  own Consequences section naming this exact revisit path.

## Rationale

ADR-0029 was correct given the evidence available when it was made: no concrete unmet need had
been demonstrated, and building speculative infrastructure ahead of demand is a reasonable default.
`docs/domains/DOM-004-research-framework.md` §4–5 and `FS-301` now state that concrete need
explicitly: instrument-grade research (reproducibility across seeds, full behavioral trace,
controlled manipulation surface via vignette YAML/doctrine presets) is a named strategic capability
of this platform (per the July-2026 Strategic Review's own S1/IN-02 findings — Monte Carlo
experimentation is flagged there as "the cheapest step-change in institutional research value
available anywhere in this review"), and scripting directly against raw `eventlog`/`save`
artifacts is a genuine adoption barrier for that use, not a hypothetical one. The project owner's
choice to supersede rather than work around ADR-0029 reflects that the original "insufficient
demonstrated need" premise no longer holds.

## Consequences

- **`ADR-0029` is marked Superseded by this ADR** — its own file is not rewritten or deleted (its
  Decision, Alternatives Considered, and Rationale remain historically intact, describing a
  decision that was correct given the evidence available at the time), but its Status header now
  points forward to this ADR, consistent with how this corpus already treats superseded documents
  (`IMP-106A`, `docs/implementations/` generally).
- **`CR-20` (Dedicated multi-run/cohort research-export interface) may now be promoted from
  Candidate to the baselined FR tier** — see `docs/requirements/01-functional-requirements.md`'s
  own reconciliation section and `docs/reviews/requirements-domain-backfill-report.md` for the
  closure record.
- **`IP-3010-research-analytics.md`'s blocking condition (dependency on `IP-2010` reaching
  `COMPLETE`) is unaffected by this ADR** — `IP-3010` was blocked on two independent conditions
  (the ADR-0029 conflict, now resolved, and its build-sequencing dependency on `IP-2010`, unrelated
  to this ADR); it remains gated on the latter and on its own separate `MSTR-006` §3 authorization.
  This ADR does not authorize implementation of either package — a package's blocking condition
  being cleared is not itself an authorization to begin coding.
- **This is the first ADR in this corpus's 33-entry history to mark a prior ADR Superseded rather
  than leaving all decisions `Accepted` indefinitely** — the July-2026 Strategic Review's own
  red-team finding (§4.1 item 3) named the all-`Accepted`, zero-`Superseded`/`Rejected` ADR corpus
  as a signal the record might capture conclusions rather than genuine decision contests. This ADR
  (and `ADR-0032`'s amend-in-place pattern) is a direct, substantive response to that finding, not
  merely a procedural one.

## Related

[ADR-0029](ADR-0029-assessment-scoring-workflow-ownership.md) (superseded by this ADR);
`docs/domains/DOM-004-research-framework.md` §§4–6; `docs/features/FS-301-research-analytics.md`;
`docs/requirements/01-functional-requirements.md` `CR-20`, `CR-21`; `docs/reviews/requirements-
domain-backfill-report.md` §3.2; `docs/implementation/packages/IP-3010-research-analytics.md`;
`docs/reviews/strategic-review-2026-07.md` §1.1 S1, Part 5 IN-02.
