# Architecture Review — GDS-01 through GDS-04

A principal-systems-architect review of the global design-synthesis ladder's first four authored
levels: [`GDS-01` Concept of Operations](../architecture/01-concept-of-operations.md),
[`GDS-02` System Context](../architecture/02-system-context.md),
[`GDS-03` Architecture](../architecture/03-architecture.md), and
[`GDS-04` Domain Model](../architecture/04-domain-model.md).

**Status:** Review report — informational, non-binding. Does not modify any reviewed document.
**Scope:** GDS-01–GDS-04 only, read against each other and against `CLAUDE.md`'s load-bearing
invariants and `docs/build-spec/` (binding on conflict). `GDS-00` Vision was read for grounding
context but is not itself a review subject. `GDS-05`–`GDS-10` are unauthored scaffolds and out of
scope.
**Method:** Cross-reading for consistency, completeness, and feasibility — not a correctness audit
of the as-built code (`docs/AUDIT-2026-06.md` already covers that ground at the implementation
level). Findings that duplicate an Open Question already recorded in one of the four documents are
called out as *reinforced*, not claimed as new discoveries; findings with no existing counterpart
are called out as *new*.

This document does not alter `GDS-01`–`GDS-04`, `architecture/INDEX.md`, or `ROADMAP.md`. Any
finding the maintainers accept as actionable should be resolved through those documents' own
Open-Questions/merge-gate mechanisms, not by editing them from here.

---

## 1. Missing concepts

1. **Assessment / scoring / after-action evaluation has no owning concept.** `GDS-00` Vision §
   success-vision item 3 anticipates researchers building "measurement and validation" on simulator
   data, and `GDS-01` ConOps Open Question #5 already flags that the assessment/scoring stakeholder
   workflow "is not described." Neither `GDS-03` Architecture nor `GDS-04` Domain Model introduces a
   subsystem or domain object for it — `EventLog`/AAR replay exists as raw material, but there is no
   "Performance Assessment" or "Scorecard" concept consuming it. *(Reinforced — escalated from a
   ConOps-level Open Question to an architecture-level gap, since two further levels were authored
   without addressing it.)*
2. **No concept for exercise/scenario authoring tooling.** `Vignette` (`GDS-04` §1.1) is the
   consumed artifact, but nothing in `GDS-02`/`GDS-03` names how a White Cell facilitator *produces*
   or *edits* one beyond "YAML is content." `CLAUDE.md`'s "content is data" invariant covers the
   storage decision, not the authoring workflow named in `GDS-01` §5 (workflow) as something White
   Cell does before a session starts. *(New.)*
3. **No concept for cross-session / cross-exercise history.** `Session` (`GDS-04` §1.14) is scoped
   to one run. There's no object representing "this cohort ran vignette N three times across two
   weeks" — relevant if the assessment gap above is ever closed, since trend data needs a container
   above a single `Session`. *(New, but contingent on finding 1.)*
4. **AI-Red as a named actor is acknowledged but never modeled as a domain object.** `GDS-02`
   System Context Open Question (AI-Red's actor status) and `GDS-03`'s Open Question (AI-Red's
   subsystem placement) both flag the ambiguity, but `GDS-04` Domain Model has no `Role Assignment`
   variant or equivalent for "the AI plays Red" — `Role Assignment` (`GDS-04` §1.10) reads as
   human-cell-only by its Persistent/Transient state description. *(Reinforced, and sharpened: this
   is now a domain-model gap, not just an architecture-placement gap.)*

## 2. Overlapping responsibilities

1. **`SSN Request` vs. `Planned Activity`.** `GDS-04` §1.13 SSN Request and §1.7 Planned Activity
   independently model "something requested now, resolved at a future time against a turnaround
   SLA." `GDS-04`'s own Open Questions section already flags this as unresolved; this review
   confirms the duplication is real, not cosmetic — both objects carry a request time, a resolution
   time, a priority/SLA field, and a delivery target, modeled separately because one is
   externally-flavored (SSN, per `CLAUDE.md`'s mock-SSN description) and one is internal
   (`OrderSystem`). The architectural justification (`GDS-03`'s SSN subsystem boundary) is sound,
   but `GDS-04` should either name the shared shape as a supertype or explicitly justify why it
   isn't one. *(Reinforced.)*
2. **`scene.py` vs. `telemetry.py` placement split.** Both `GDS-03` and `GDS-04` independently
   flag this as an Open Question: `scene.py` (render-from-custody belief) and `telemetry.py`
   (read-time subsystem telemetry) are both pure, read-only, replay-safe projections living in
   `engine/`, yet conceptually one is "what Red/Blue believe" (a `Cell View`/`Track` concern,
   Session-adjacent) and the other is "what's wrong with my own bus" (an `Asset`-internal concern).
   Two independently-authored levels reaching the same flag is a strong signal this is a genuine
   seam, not a false positive. *(Reinforced, with corroboration weight.)*
3. **Content & Data vs. Session over save-file/Snapshot ownership.** `GDS-03`'s subsystem table
   assigns `Session` ownership of session state and `Content & Data` ownership of vignette/template
   files, but `Snapshot`/save-resume (`SessionManager.save`/`/save` endpoint per `CLAUDE.md`) writes
   a session's runtime state to a file — which subsystem owns the resulting artifact once it's on
   disk? `GDS-03` describes `Content & Data`'s dependency on `Session`/`Engine` as "schema-only," but
   a save file is runtime-generated content, not authored content, and doesn't fit either
   subsystem's stated Ownership-of-data column cleanly. *(New.)*

## 3. Architectural inconsistencies

1. **`build-spec/03` §7 still describes a PyQt/PySide desktop presentation layer** as the planned
   v1 GUI, while `GDS-03` (and `CLAUDE.md` itself) describe the as-built system as FastAPI + web.
   `GDS-03` already self-flags this as an Open Question ("PyQt staleness in build-spec/03"), and per
   `CLAUDE.md`/`GDS-00`, the build spec wins on conflict — meaning the *binding* document currently
   describes a presentation layer that was not built, and the *as-built* description lives one level
   removed from the document that's supposed to be authoritative. This is a real inconsistency
   between what governs and what's true, not merely a documentation gap. *(Reinforced, with the
   governance implication made explicit: until `build-spec/03` is revision-noted per `GDS-00`'s own
   stated remedy — "a signal that build spec needs a revision note" — any reader who follows the
   binding-spec-first reading order in `CLAUDE.md` will be told the wrong presentation technology.)*
2. **Six access channels (`CLAUDE.md`, `GDS-04` §1.6) vs. cyber as a "non-windowed" exception.**
   `GDS-04`'s `Access Window` (§1.6) is described as gating five of the six channels, with cyber
   resolving independently of windows. But `GDS-02` System Context's external-interfaces table and
   `GDS-03`'s six-channel listing both enumerate cyber as a full channel alongside the other five
   without flagging the exception inline — a reader of `GDS-02`/`GDS-03` alone (without `GDS-04`'s
   detail or `CLAUDE.md`) would reasonably assume all six are window-gated uniformly. Not a defect
   in any single document, but the exception is documented in exactly one place per channel-bearing
   level instead of being repeated as a caveat everywhere the six channels are listed. *(New.)*
3. **`GDS-01` ConOps describes "hot-seat" single-machine play and LAN multiplayer as two modes**,
   but `GDS-03`'s Architecture and `GDS-04`'s `Session` entity both model a single `Session` shape
   serving both — which is consistent with the as-built lazy-clock design, but `GDS-01` §8
   (operational modes) reads as if they were more architecturally distinct than the unified
   `Session` object actually makes them. Minor framing inconsistency, not a functional one. *(New,
   low severity.)*

## 4. Violations of separation of concerns

1. **Fog-of-war enforcement boundary vs. the documented LAN trust model.** `CLAUDE.md` states fog-of-
   war is enforced "at the `SessionAPI`/`CellController` boundary, never in the UI" — a clean
   separation. But the same document's LAN trust model section states the no-cell god-view endpoints
   (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`) "deliberately expose ground truth
   without a cell binding," and the cell selector itself is "client-side trust." `GDS-02`/`GDS-03`
   both inherit this as a documented, intentional v1 boundary rather than a defect — and this review
   agrees it is *documented* honestly — but it means the actual separation-of-concerns boundary is
   not "fog-of-war is enforced below the UI" (as the invariant states) so much as "fog-of-war is
   enforced below the UI *for cell-scoped endpoints only*, with a parallel un-gated path that any
   client can reach by URL." `GDS-03`'s Architecture document should state this caveat explicitly
   next to its fog-of-war cross-cutting-concerns section rather than leaving it implicit in
   `CLAUDE.md` alone, since a reader of `GDS-03` in isolation would reasonably believe the boundary
   is total. *(New — a documentation-completeness finding, not a code defect; the code-level finding
   already exists in `docs/AUDIT-2026-06.md` §D5/§F1.)*
2. **`Order`/`OrderSystem` (per `CLAUDE.md`'s engine code map) computes both validation and
   window/delivery-path logic that `dry_run()` mirrors for UI "why can't I?" affordances.** This is
   a reasonable, intentional duplication-avoidance pattern (one read-only mirror function), but
   `GDS-04`'s `Planned Activity` (§1.7) describes only the executed-order lifecycle, not the
   dry-run/preview concern — meaning a UI-facing capability (live command-menu preview) has no
   corresponding domain concept at all. Whether that's correctly out of scope for a *domain* model
   (since dry-run produces no persistent state) or a gap depends on how strictly GDS-04 means to
   scope "domain object" — worth an explicit call-out rather than silence. *(New.)*

## 5. Circular dependencies

1. **No literal circular dependency found in the subsystem graph.** `GDS-03`'s dependency diagram
   (Presentation→Session→Engine; Session→SSN→Engine; Session/Engine→Data) is acyclic as drawn, and
   `CLAUDE.md`'s import-guard test enforces the most safety-critical edge (`engine/` importing
   nothing from UI/transport) at the code level, not just the documentation level.
2. **A conceptual near-cycle exists between `Track` (custody/belief) and `Cell View` (fog-of-war
   projection).** `GDS-04` §1.9 `Track` is described as input to `Cell View` (§1.11), but
   `Cell View` rendering logic (`scene.py`) reads from `Track` state that itself depends on
   `Access Window`/`Sensor` data gated by the very `Cell View` boundary that's supposed to consume
   it. This is not a true cycle — data flows one direction (`Sensor` observation → `Track` update →
   `Cell View` render) — but the documents don't make the directionality explicit enough to
   immediately rule out a cycle on first read, given `scene.py`'s placement ambiguity already noted
   in finding §2.2 above. Recommend `GDS-04` add an explicit note that `Cell View` is read-only/
   derived and never feeds back into `Track`. *(New, low severity — a clarity gap, not an actual
   cycle.)*

## 6. Potential scaling problems

1. **Per-session `RLock` + HTTP polling under multi-tab LAN play.** `CLAUDE.md`'s multiplayer
   workflow describes lazy `catch_up()` on every read, serialized by a per-session `RLock`. `GDS-03`
   inherits this design without flagging a ceiling. As participant/tab count grows (`GDS-01` Open
   Question #2 already flags "no concrete participant-count ceiling for LAN mode"), every read
   across every tab serializes through one lock per session — acceptable at the stated ~24-satellite,
   small-cohort soft-sizing guideline, but `GDS-03`/`GDS-04` give no model for where this degrades,
   and neither document revisits `GDS-01`'s already-open question. *(Reinforced — carried forward
   unaddressed through two further ladder levels.)*
2. **`Track` confidence decay recomputed on every read (`GDS-04` §1.9) compounds with the polling
   model above.** Each `Cell View` read for each connected client recomputes decay for every
   tracked object in that cell's catalog; this is "pure function of elapsed time," so it's cheap per
   call, but the *number* of calls scales with tabs × poll frequency × tracked-object count, with no
   stated upper bound in any of `GDS-01`–`GDS-04`. At the stated ~24-satellite soft cap this is very
   unlikely to matter; it becomes a real question only if the "no engine-enforced cap" note in
   `CLAUDE.md` is exercised by a much larger user vignette. *(New, low severity given current
   sizing guidance.)*
3. **Constellation aggregation is explicitly deferred** (`CLAUDE.md` → `docs/FUTURE-WORK.md`), and
   `GDS-04`'s `Asset` (§1.x) and `Vignette` model individual satellites with "constellations ≤3
   sats, each operated/monitored individually" as the current ceiling. This is a known, already-
   tracked deferral, not a new finding, but it's worth restating here because `GDS-01`'s ConOps
   doesn't mention any operator-cognitive-load ceiling tied to fleet size, and a future larger
   vignette would hit both the per-asset operator UX limit and the polling-scaling limit (finding 1
   above) simultaneously. *(Reinforced/contextualized, not new.)*

## 7. Requirements that appear impossible to implement (as currently specified)

1. **"Researchers build measurement and validation on simulator data" (`GDS-00` success-vision
   item 3) cannot be implemented against the current domain model**, because no domain object
   captures outcome/assessment data (see Missing Concepts #1). This isn't a feasibility problem in
   principle — it's that the requirement has no landing surface in `GDS-04` at all, so "impossible"
   here means *impossible as currently scoped*, not infeasible in the abstract. Closing Missing
   Concepts #1 closes this finding.
2. **`GDS-01`'s assessment/scoring stakeholder workflow (Open Question #5) is stated as a
   stakeholder need but has no architecture-level home** in `GDS-03`'s five subsystems — there is no
   sixth subsystem, and none of the five existing subsystems' stated Responsibilities mention
   scoring. As written, a scoring feature would have nowhere correct to live without either
   stretching an existing subsystem's stated scope or amending `GDS-03`. *(Reinforced — same root
   cause as findings 1/7.1, now stated as an architecture-level blocker rather than a content gap.)*
3. **Nothing else reviewed rises to "impossible."** The remaining Open Questions across all four
   documents (AI-Red placement, PyQt staleness, SSN/Planned-Activity overlap, scene/telemetry split)
   are real design-clarity gaps but each has at least one plausible resolution path already
   sketched in the source document — they are *unresolved*, not *unimplementable*.

## 8. Areas needing clarification

1. **AI-Red's status, end to end.** `GDS-02` (actor status), `GDS-03` (subsystem placement), and
   `GDS-04` (no domain representation, per Missing Concepts #4) all independently flag a piece of
   the same underlying question and none resolves it. Recommend this be the first item picked up
   when any of these documents' Open Questions are next revisited, since three separate levels
   converging on one unresolved actor is a strong signal it's load-bearing for whatever comes next
   (notably `GDS-05` Functional Requirements, which will need to state what AI-Red is allowed to do).
2. **Ground-site data provenance** (`GDS-02` Open Question) — does not block any finding above
   directly, but is inherited as still-open into `GDS-03`/`GDS-04` without either level adding
   information. Worth confirming it's still tracked, not silently dropped.
3. **Whether `Role Assignment`'s fairness/visibility model accounts for an AI-controlled cell.**
   If AI-Red has full ground-truth access (as a code-level "AI doctrine module" plausibly would,
   reading from `redai.py` per `CLAUDE.md`'s code map) while human Red/Blue are fog-of-war-limited,
   that's a fairness-relevant asymmetry that no document — `GDS-01` ConOps, `GDS-02` System Context,
   nor `GDS-04` Domain Model — currently addresses one way or the other. This is the AI-Red question
   from a different angle than findings 1.4/2.4/8.1 (those ask "what is it," this asks "does it play
   by the same epistemic rules"), and is worth keeping distinct because the answer could be "yes,
   intentionally, it's an opponent model" or "no, this is a real fairness gap" — the documents
   currently support either reading. *(New.)*
4. **Whether `Snapshot`/save-file artifacts are versioned across `spacesim` releases.** `GDS-04`
   §1.14 `Session` mentions `Snapshot` as persistent state but none of the four documents say
   whether a save file from one version of the engine is expected to load under a later version —
   relevant given the project's active-development status ("backend feature-complete through Phase
   8") and the stated determinism guarantee, which is about replay *within* a build, not load
   compatibility *across* builds. *(New.)*

---

## Summary table

| # | Category | New findings | Reinforced findings |
|---|---|---|---|
| 1 | Missing concepts | 2, 3 | 1, 4 |
| 2 | Overlapping responsibilities | 3 | 1, 2 |
| 3 | Architectural inconsistencies | 2, 3 | 1 |
| 4 | Separation-of-concerns violations | 1, 2 | — |
| 5 | Circular dependencies | 2 (near-cycle, clarity only) | — (none found) |
| 6 | Scaling problems | 2 | 1, 3 |
| 7 | Impossible requirements | — | 1, 2 |
| 8 | Needing clarification | 3, 4 | 1, 2 |

**Headline take:** no hard architectural defect (no real circular dependency, no invariant
violation at the code level) was found across GDS-01–GDS-04. The most load-bearing open item is the
assessment/scoring gap (Missing Concepts #1, Impossible Requirements #1–2), which is now flagged at
three levels (vision, ConOps, and — via this review — architecture) without an owning subsystem or
domain object; the second most load-bearing is AI-Red's unresolved status, flagged independently by
three different documents and one new fairness angle here. Everything else is a clarity or
documentation-currency gap rather than a structural one.

## Related

[`GDS-00`](../architecture/00-vision.md) · [`GDS-01`](../architecture/01-concept-of-operations.md) ·
[`GDS-02`](../architecture/02-system-context.md) · [`GDS-03`](../architecture/03-architecture.md) ·
[`GDS-04`](../architecture/04-domain-model.md) · [`docs/AUDIT-2026-06.md`](../AUDIT-2026-06.md)
(implementation-level audit; this report is documentation-level) ·
[`docs/FUTURE-WORK.md`](../FUTURE-WORK.md) (tracks the constellation-aggregation and per-cell-token
deferrals referenced in §6/§4 above).
