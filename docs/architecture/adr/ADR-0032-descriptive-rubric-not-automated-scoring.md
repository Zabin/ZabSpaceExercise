# ADR-0032 — Descriptive rubric-tier reporting is not automated scoring (amends ADR-0017)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0032
- **Title:** Non-adjudicative, descriptive rubric-tier measurement is carved out of ADR-0017's
  "no automated scoring or assessment mechanism" prohibition
- **Status:** Accepted
- **Amends:** [ADR-0017](ADR-0017-manual-adjudication.md) (remains Accepted; this ADR narrows its
  scope, it does not reverse it)

## Context

`docs/reviews/requirements-domain-backfill-report.md` §3.1 (produced by a `requirements-engineering`
pass against DOM-002, the Assessment Framework, and its output `FS-201` Competency Assessment)
found that FS-201's core capability — an always-available, automated computation of qualitative
rubric tiers (custody quality, window discipline, belief-truth divergence, and three deferred
dimensions) per cell per exercise — could not be baselined as a Functional Requirement (it was
instead recorded as Candidate Requirement `CR-19`) because ADR-0017's Decision text reads: *"No
automated scoring **or assessment mechanism** exists in v1."* Read broadly, that phrase blocks any
automated assessment computation at all, including FS-201's rubric.

DOM-002 §5 ("Scoring model principle: rubric, not single score") deliberately designed the rubric
to avoid exactly the thing ADR-0017 was written to prohibit: *"A single composite 'score' collapses
dimensions that are not commensurable... invites gaming a denominator... the framework specifies a
rubric model: each dimension is reported on its own scale... rather than a forced numeric average...
a facilitator-facing summary view presents the rubric, not a single leaderboard number."* FS-201's
own Acceptance Criteria independently commit to the same thing: *"No composite single score is
produced."*

The project owner, asked directly whether to (a) amend ADR-0017 with a narrow carve-out for this
distinction, (b) rescope FS-201 to remove automated computation entirely, or (c) reject the
capability outright, chose (a).

## Decision

ADR-0017's prohibition is narrowed, not reversed. The following remains true, unchanged:

- **No automated scoring exists.** No mechanism computes or displays a single composite numeric
  score, a win/loss determination, or any other collapsed adjudicative verdict. `FR-4710`
  ("the system shall not compute or display an automated score or win/loss determination") is
  unaffected by this ADR and remains baselined exactly as written.
- **White Cell remains the sole adjudication authority.** No automated mechanism narrates outcomes,
  assigns consequence, or substitutes for the facilitator's judgment (ADR-0017's Rationale is
  unchanged).

The following is now **carved out** of ADR-0017's "assessment mechanism" phrase and is permitted:

- An automated computation that reports **multiple independent qualitative dimensions**, each on
  its own descriptive tier scale (e.g. "speculative / adequate / disciplined"), **never aggregated
  into a single number, verdict, or ranking**, and that **does not itself narrate an outcome or
  assign consequence** — it is read-only analytics over existing engine state (eventlog, custody
  history, order log, AAR snapshots), presented alongside, not instead of, White Cell's manual
  adjudication.

This carve-out is deliberately narrow: it applies to FS-201's rubric-tier design specifically
(multi-dimension, non-aggregating, non-adjudicative), not to automated assessment computation in
general. A future feature that aggregates dimensions into one number, or that itself narrates a
consequence, remains squarely inside ADR-0017's original prohibition and is not authorized by this
ADR.

## Alternatives Considered

- **Rescope FS-201 to remove automated computation entirely** (leaving only the facilitator-manual
  and self-assessment/AAR-walkthrough modes DOM-002 §6 already names) — **not adopted**: the project
  owner judged the narrow carve-out preserves more of FS-201's original design value (an
  always-available baseline measurement, not solely dependent on facilitator effort) while still
  respecting ADR-0017's core prohibition.
- **Reject FS-201's automated capability outright, leave ADR-0017 unamended** — **not adopted**:
  would leave `CR-19` permanently blocked and `IP-2010` permanently cancelled with no path forward,
  which the project owner did not choose.
- **Reverse ADR-0017 entirely** (permit composite scoring/win-loss too) — not offered as an option
  and not adopted; ADR-0017's core prohibition (no composite score, no automated win/loss, manual
  adjudication of outcomes) is explicitly preserved, not reconsidered, by this ADR.

## Rationale

The distinction DOM-002 §5 draws — between a single collapsed verdict (which substitutes for
facilitator judgment, the thing ADR-0017 exists to prevent) and multiple independent descriptive
signals (which inform facilitator judgment without substituting for it) — is a real, defensible
line, not a rationalization. ADR-0017's own Rationale is about preserving "facilitator judgment as
part of the pedagogy" and avoiding a scoring rubric that lets tactically-unwise-but-legal play be
penalized automatically rather than narrated by a human. A rubric that reports "this cell's custody
quality was speculative" without saying whether that's good, bad, or how it should be weighed
against other dimensions does not narrate an outcome or assign consequence — it hands the
facilitator more evidence to adjudicate with, the same role the event log and AAR replay already
play per ADR-0017's own Consequences section.

## Consequences

- **`CR-19` (Automated competency-assessment rubric computation) may now be promoted from Candidate
  to the baselined FR tier** — see `docs/requirements/01-functional-requirements.md`'s own
  reconciliation section for the resulting new FR leaf and `docs/reviews/requirements-domain-
  backfill-report.md` for the closure record.
- **`IP-2010-competency-assessment.md`'s blocking condition is resolved at the architecture tier.**
  This ADR does not itself authorize implementation — per `MSTR-006` §3, a package reaching `READY`
  (or having its blocking condition cleared) is not itself an authorization to begin coding;
  `IP-2010` still requires a separate, explicit go-ahead before any code is written.
- **Any future FS-201 revision that proposes aggregating dimensions into one number, or that
  narrates an outcome/consequence automatically, falls back outside this carve-out** and would
  need its own ADR, not an inferred extension of this one.
- `ADR-0017` itself is **not edited** — its Decision, Rationale, and Consequences remain exactly as
  originally accepted; a pointer to this amendment is added to its own file's header for forward
  navigation, per this corpus's established pattern of not silently rewriting an Accepted ADR's own
  text (see `ADR-0031`'s handling of a similar cross-reference correction).

## Related

[ADR-0017](ADR-0017-manual-adjudication.md) (amended by this ADR); `docs/domains/DOM-002-assessment-framework.md`
§5; `docs/features/FS-201-competency-assessment.md`; `docs/requirements/01-functional-requirements.md`
`FR-4710`, `CR-19`; `docs/reviews/requirements-domain-backfill-report.md` §3.1;
`docs/implementation/packages/IP-2010-competency-assessment.md`.
