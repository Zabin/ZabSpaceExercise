# ADR-0031 — Governance-record consistency: stale supersession language and the DOM-002/DOM-005 status gap

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0031
- **Title:** Correct GDS-00 §7's stale "build spec wins" language; acknowledge (not retroactively
  close) the DOM-002/DOM-005-vs-FS-201/FS-301 status inconsistency
- **Status:** Accepted

## Context

[`strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) §4.1 finding 1 and §6.1
recommendation R5 flag two internal-consistency defects in the governance record itself, distinct
from any defect in the system being governed:

1. **Stale supersession language.** `architecture/00-vision.md` (GDS-00) §7 "Relationship to the
   build spec" still reads: "`docs/build-spec/` remains **binding** for v1: 'on any conflict, the
   build spec wins.'" This directly contradicts `architecture/INDEX.md`'s own header, which states
   the opposite as a "blanket declaration": "This directory is now the single authoritative
   architecture/requirements source for the whole project, superseding `docs/build-spec/` in its
   entirety... This is a blanket declaration, not limited to levels whose merge gate has already
   closed." `CLAUDE.md`'s "Authoritative source & reading order" records the same blanket
   supersession. GDS-00 §7 was written before that supersession was declared and was never updated
   to match — the review's characterization ("still carries the *old* 'build spec wins' language
   and now contradicts `CLAUDE.md`'s blanket declaration") checks out verbatim against the current
   file text.
2. **DOM-002/DOM-005 vs. FS-201/FS-301 status inversion.** `docs/domains/INDEX.md` lists DOM-002
   (Assessment Framework) and DOM-005 (Validation Framework) as `⛔` (not yet authored), while
   `docs/features/feature-index.md` lists FS-201 (Competency Assessment) and FS-301 (Research
   Analytics) — both of which DOM-002/DOM-005 are supposed to generate, per `MSTR-005`'s
   Training-Objective→Domain→Research→Design-Synthesis→Feature→Implementation chain — as `✅ Done`.
   This inverts the traceability chain the project's own documentation apparatus exists to enforce:
   two shipped features currently rest on domain frameworks that don't exist yet.

## Decision

Two sub-decisions, addressing the two defects separately since they have different correct
remedies:

1. **GDS-00 §7 is corrected now.** Its text is rewritten to state the current, already-declared
   supersession accurately — `docs/architecture/` (the GDS ladder) is authoritative over
   `docs/build-spec/` in its entirety, per `architecture/INDEX.md`'s blanket declaration, with the
   caveat that an unauthored GDS level (GDS-06–10) has no authoritative content yet rather than the
   corresponding build-spec module winning by default. This mirrors the precedent already set by
   ADR-0028, which authorized an equivalent direct rewrite of `build-spec/03` §7.1/§7.2 once its
   PyQt description was confirmed stale — a text correction to match already-declared reality, not
   a new architectural decision.
2. **The DOM-002/DOM-005 status inversion is acknowledged, not retroactively resolved.** This ADR
   does **not** author DOM-002 or DOM-005 (that is `docs/domains/` tier work, requires the
   `architecture-design-synthesis`/domain-framework authoring process, and is explicitly out of
   scope for an architecture-document review pass). Nor does it change FS-201/FS-301's `✅ Done`
   status — both features are shipped, working, and correctly documented as such; retroactively
   marking them `🚧` would misdescribe the as-built system to correct a paperwork ordering problem.
   The correct disposition is the one the review itself recommends elsewhere (R9): commission the
   DOM-002/DOM-005 authoring work, informed by GAP-07 (training-transfer research), so the
   framework is written once, correctly, rather than retrofitted twice. That authoring work is
   tracked as a standing gap in `docs/domains/INDEX.md` (already `⛔`, correctly) and in
   `FUTURE-WORK.md`, not invented here.

## Alternatives Considered

- **Leave GDS-00 §7 unedited, flagged only as an Open Question** (the pattern used for genuinely
  unresolved design tensions elsewhere in this corpus). **Rejected** — unlike a real design
  tension, this is not a disagreement to adjudicate; `architecture/INDEX.md` and `CLAUDE.md` already
  settled the supersession question. GDS-00 §7 is simply out of date relative to a decision already
  made elsewhere, which is a text-correction case (ADR-0028's precedent), not an Open-Question case.
- **Retroactively author minimal DOM-002/DOM-005 stubs now, just to close the status gap.**
  **Rejected** — a domain framework authored under time pressure to fix a status color, rather than
  through the actual synthesis process (drawing on DOM-owning research and the features it's
  supposed to generate), would be exactly the "features built on unauthored frameworks" failure mode
  the review criticizes, replaced with "frameworks retrofitted to already-built features" — no
  better. The review's own R9 recommends commissioning GAP-07 research *first* so DOM-002/DOM-005
  are "not authored twice" — a rushed stub now would guarantee exactly that.
- **Downgrade FS-201/FS-301 to `🚧` until DOM-002/DOM-005 exist.** **Rejected** — both features are
  built, tested, and shipping; changing their status would misrepresent the as-built system's
  actual state to satisfy a documentation-ordering convention, which is a worse error than the one
  being corrected.

## Rationale

The two defects have genuinely different correct remedies precisely because one is a stale
statement of an already-settled fact (fix it) and the other is a real, still-open governance gap
whose correct closure is a substantive authoring effort the review itself schedules under R9 —
conflating them into one blanket "fix everything now" action would either under-deliver (a
five-minute text edit dressed up as having "addressed" a domain-framework gap) or over-deliver (a
rushed DOM-002/DOM-005 stub nobody asked to be authored this way).

## Consequences

- `architecture/00-vision.md` §7 is corrected to state the current supersession accurately; its
  Version is bumped and the correction is recorded in its own Merge gate section as an
  explicitly-instructed amendment, consistent with the precedent set by ADR-0028's `build-spec/03`
  rewrite and by GDS-01–04's own "Review reconciliation"/"Research integration" amendment sections.
- `docs/domains/INDEX.md`'s DOM-002/DOM-005 rows are **not** edited by this ADR — they continue to
  read `⛔`, correctly, until actually authored. This ADR is the recorded acknowledgment that the
  inconsistency is real, understood, and intentionally not papered over.
- The DOM-002/DOM-005 authoring gap is carried forward as future work (see
  [`architecture-update.md`](../../reviews/architecture-update.md) recommendation R5/R9 disposition
  and `FUTURE-WORK.md`), to be actioned via the domain-framework authoring process, ideally informed
  by GAP-07 research per R9 — not by this ADR.

## Related

`architecture/00-vision.md` §7; `architecture/INDEX.md` (the blanket-supersession declaration this
ADR aligns GDS-00 §7 with); `CLAUDE.md` "Authoritative source & reading order"; ADR-0028 (the
precedent for a direct stale-text correction); `docs/domains/INDEX.md` (DOM-002, DOM-005);
`docs/features/feature-index.md` (FS-201, FS-301);
[`strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) §4.1 finding 1, §6.1
recommendation R5; [`architecture-update.md`](../../reviews/architecture-update.md).
