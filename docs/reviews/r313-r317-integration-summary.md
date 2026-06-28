# Architecture Review Summary — R313–R317 Integration into GDS-01–04

> Phase 5 deliverable: a consistency check across the four updated documents
> ([`GDS-01`](../architecture/01-concept-of-operations.md),
> [`GDS-02`](../architecture/02-system-context.md),
> [`GDS-03`](../architecture/03-architecture.md),
> [`GDS-04`](../architecture/04-domain-model.md)) following the
> [gap analysis](r313-r317-gap-analysis.md) and the edits it drove. Companion to that document and
> to the per-document "Research integration (R313–R317)" sections, which record the same changes
> in place.

## 1. Requirements ↔ architecture alignment

`GDS-05`/`GDS-06` (Functional/Non-functional Requirements) remain unauthored scaffolds — this
update does not touch them, and no new requirement was introduced by this pass (per the
gap-analysis disposition summary: every change is additive documentation, three forward-looking
subsections, six new Open Questions). There is therefore nothing in GDS-05/06 that could newly
contradict GDS-01–04 as a result of this update. `build-spec/02-requirements-and-operations.md`
(the binding v1 requirements) is unaffected — no FR/NFR tag was added, changed, or implied.

## 2. Architecture ↔ CONOPS alignment

GDS-03's new §5 (candidate future subsystems: Decision Support/Assessment, Autonomy Manager,
Command-relationship layer) traces directly back to Open Questions already recorded in GDS-01 (5/6,
7) and GDS-04 (new §3) — each candidate component exists *because* a CONOPS-level or domain-level
gap was already named, not as an independent architectural idea. No new component was invented at
the architecture level without a corresponding operational or domain-level gap motivating it.
Checked: every row in GDS-03 §5's table cites the GDS-01/GDS-04 Open Question it restates from the
architecture angle. Consistent.

## 3. Domain model ↔ architecture alignment

GDS-04's new §3 (Command Relationship, Intent, Decision Cycle) and GDS-03's new §5 cover the same
three forward-looking concepts from their respective altitudes (domain meaning vs. architectural
placement) without duplicating content — GDS-04 §3 describes what each concept *means*; GDS-03 §5
describes what *subsystem* would own it if built. Checked for drift: GDS-03 §5's "Command-
relationship layer" row and GDS-04 §3's "Command Relationship" bullet cite the same research
sections (`R313` §3.2/§3.7, `R316` §3.1) and make the same not-yet-implemented disclaimer in
matching language. Consistent.

## 4. Terminology consistency

- **"Decision Cycle"** is introduced once, in GDS-01 §1 (operational framing) and cross-referenced
  identically in GDS-03 §4 (architectural framing, as a cross-cutting concern) and GDS-04 §3
  (domain framing, as a pattern, not an entity). All three describe the same shape
  (observe/classify → decide → act → assess) and the same existing instance (the custody/track
  chain). No competing name (e.g. "OODA loop," "targeting cycle") was introduced as a synonym in
  the architecture corpus, even though the research uses domain-specific names (D3A, F2T2EA) —
  those stay attributed to their source domain in citations, not imported as alternate names for
  the architectural concept.
- **"Command Relationship"** (the new conceptual term, GDS-04 §3) is kept distinct from the
  existing **"Role Assignment"** entity (GDS-04 §1.10) — the new section explicitly states Role
  Assignment is the only authority concept that exists today and is uniform, while Command
  Relationship is the not-yet-built layer above it. No accidental conflation.
- **"Intent"** (new, GDS-04 §3) is kept distinct from the existing **Vignette "objectives"/ROE**
  (GDS-04 §1.1) — the new section explicitly notes objectives/ROE are not the same as an Intent
  object, and names AI-Red doctrine presets as the closest existing (but not equivalent) analog.
- **R314's draft/unverified status** is flagged consistently at every point it is cited: the
  metadata blocks of GDS-01 and GDS-04 (the only two documents that cite it) both carry the
  "(draft, citations unverified)" qualifier, and the gap-analysis document states the same caveat
  in its preamble. No document treats R314 content as more solid than R313/R315/R316/R317.
- **Title-Case vs. lowercase entity naming** (the existing convention-layering judgment from the
  prior architecture-review reconciliation) was not disturbed — new forward-looking concept names
  (Command Relationship, Intent, Decision Cycle) are introduced in Title Case in GDS-04 §3,
  consistent with that document's existing §1 convention for formal entity names, while GDS-01's
  operational prose refers to them descriptively (lowercase) per its own existing convention.

## 5. No duplicated or conflicting concepts

- Checked GDS-02's new "Candidate future external systems" table against GDS-03's new §5 and
  GDS-04's new §3: no overlap — GDS-02's candidates are external-boundary-crossing systems
  (coalition C2 interface, external mission-planning feed, external intel/SDA feed); GDS-03's are
  internal subsystems; GDS-04's are domain concepts. Each operates at its own document's altitude
  with no entity named in two places with different meanings.
- Checked that no new Open Question duplicates an existing one: the six new Open Questions
  (GDS-01 #7–8, GDS-02 #5, GDS-03 #5, GDS-04 #5–6) were each compared against the existing,
  already-resolved or already-open questions in the same document before being added; none restates
  a question already present under different wording. GDS-04 Open Question 5 explicitly
  corroborates (does not duplicate) the existing Open Question 3.
- Checked for contradiction with `build-spec/`: GDS-02's forward-looking external-systems table and
  GDS-03's forward-looking subsystems section both carry explicit "not current scope" / "not built"
  disclaimers immediately adjacent to the table, and neither edits the pre-existing sentences that
  state current v1 scope (GDS-02 §9: "no other live external system is in scope for v1"; GDS-03 §2:
  the five-subsystem list). Per `MSTR-001` §7, the build spec wins on conflict — no conflict was
  created, because no forward-looking addition asserts current-scope status.

## 6. Scope discipline check (re-verified against the gap analysis's own disposition summary)

- No existing sentence, table row, or resolved Open Question was deleted, reworded to weaken its
  meaning, or had its resolution reopened. Spot-checked: GDS-01 Open Questions 2/5/6 (ADR-resolved)
  remain struck through and resolved exactly as before; only Open Question 6 gained an appended
  corroborating citation, with the resolution itself untouched.
- All four documents' `Status` metadata remains `✅ Authored — merge gate closed`. This update is
  recorded, in each document's own "Research integration (R313–R317)" section, as an
  explicitly-instructed amendment layered on top of an already-closed gate — the same pattern
  already established by the prior architecture-review reconciliation (which performed an
  analogous in-place amendment under explicit instruction without reopening any gate). No ladder
  gating rule was violated: this pass did not advance the ladder past GDS-04, and GDS-05 remains
  the next level to author.

## 7. Items intentionally left unresolved (by design, not oversight)

Per the task's "remain at the architecture level... do not begin implementation planning" charter,
the following were deliberately left as Open Questions rather than resolved, because resolving them
would require a design decision:

- Command-relationship layering (GDS-01 OQ7, GDS-04 OQ6's promotion-trigger question).
- Resilience under sustained denial vs. single-fault safe mode (GDS-01 OQ8, GDS-03 OQ5).
- Whether a coalition-partner actor is ever needed (GDS-02 OQ5).
- Whether/when GDS-04 §3's concepts should become real entities (GDS-04 OQ6).

## Related

[`r313-r317-gap-analysis.md`](r313-r317-gap-analysis.md) (the Phase 2 deliverable this summary
checks) · [`architecture/INDEX.md`](../architecture/INDEX.md) (ladder index — unchanged in
structure by this update; GDS-00–04 keep their `✅ Authored — merge gate closed` status) ·
[`reviews/architecture-review-changelog.md`](architecture-review-changelog.md) (the prior,
structurally analogous in-place-amendment precedent this update follows).
