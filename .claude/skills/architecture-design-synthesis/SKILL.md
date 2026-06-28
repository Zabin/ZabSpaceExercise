---
name: architecture-design-synthesis
description: Synthesize domain framework (DOM-xxx) and research grounding (research/encyclopedia R1xx-R5xx + research/01-07 primers) into Design Synthesis documents under docs/architecture/ — either the global, gated GDS-00...GDS-10 ladder (Vision -> ConOps -> System Context -> Architecture -> Domain Model -> Functional Requirements -> Non-functional Requirements -> Data Model -> UI Architecture -> API Specification -> Requirements Traceability Matrix) or a per-capability-cluster ADS-xxx document, the bridge between domain+research and a Feature Specification. Use when asked "what are the core concepts," "which mechanics are actually required," "which requirements conflict," "what assumptions must be made," "what is the minimum viable implementation," "what is deferred," to advance the next level of the GDS ladder, or to produce/refresh an Executive Design Overview, System Architecture, Domain Model, User Stories, Functional/Non-functional Requirements, Constraints, Risks, Open Questions, or Decision Log before drafting or revising an FS-xxx. This produces design documents, not research documents — do not use it to add new doctrinal/orbital-mechanics claims (that's research-doctrine-exercises / research-ow-orbital-mechanics).
---

# Architecture / Design Synthesis

Produces two kinds of document under `docs/architecture/`, both defined in
[`MSTR-005`](../../../docs/master/MSTR-005-documentation-map.md) §3a/§3b/§4 and tracked in
[`docs/architecture/INDEX.md`](../../../docs/architecture/INDEX.md):

1. **The global ladder (`GDS-00`…`GDS-10`)** — one instance for the whole project, strictly
   sequential and gated. This is the primary, currently-active workflow: the ladder is scaffolded
   with stub files and merge gates, and the next unauthored `GDS-NN` is the default thing to work
   on when this skill is invoked without a more specific target. See "Workflow A" below.
2. **Per-cluster `ADS-xxx`** — zero-or-more documents, one per capability cluster with real design
   tension the ladder doesn't resolve at the system level. See "Workflow B" below.

Read `MSTR-005` §3a/§3b and `architecture/INDEX.md` before producing anything; this skill
operationalizes them, it does not restate them.

## What this is for (and what it is not)

This skill answers, for one capability cluster, the questions a designer must answer **before** a
Feature Specification can commit to a shape:

- What are the core concepts?
- Which mechanics are actually required (vs. nice-to-have)?
- Which candidate requirements conflict, and how is the conflict resolved?
- What assumptions must be made explicit, because the domain/research inputs don't settle them?
- What is the minimum viable implementation?
- What is deferred to a later release?

It consumes [`docs/domains/`](../../../docs/domains/INDEX.md) (the DOM-xxx framework that owns the
capability) and [`docs/research/`](../../../docs/research/INDEX.md) (both the `01-07` primers and
the `encyclopedia/` R1xx-R5xx tiers) as **inputs**, never as something it adds to. If a synthesis
reveals a genuine domain-knowledge gap (a doctrine question with no R3xx grounding, an orbital
mechanics question with no R1xx grounding), that gap is handed to
`research-doctrine-exercises`/`research-ow-orbital-mechanics` to close first — this skill does not
write research content itself.

It produces **design documents, not research documents**: synthesis, decision, and explicit
tradeoffs, not new domain-knowledge claims. An `ADS-xxx` cites its grounding `DOM-xxx`/`R-xxx`
documents; it does not re-derive or duplicate their content.

**Not every feature needs this.** Per `MSTR-005` §4, a small/uncontested feature can go straight to
`FS-xxx` — the FS author absorbs the synthesis work into that document's own §1-2. Reach for this
skill when a capability cluster has real design tension: conflicting candidate requirements,
multiple plausible architectures, or load-bearing assumptions nobody has written down yet.

## Scope (what this skill owns)

| Asset | Role |
|---|---|
| [`architecture/INDEX.md`](../../../docs/architecture/INDEX.md) + `00-vision.md`…`10-requirements-traceability-matrix.md` + `ADS-xxx-*.md` | The Design Synthesis tier this skill authors. |
| Grounding inputs | `docs/domains/DOM-xxx-*.md`, `docs/research/encyclopedia/R1xx-R5xx` + `docs/research/01-07` primers, `docs/build-spec/` (binding v1 spec — wins on any conflict), `docs/design/`, `docs/training/`, `MSTR-001` — and, for the ladder specifically, the per-level "merges from" existing document named in `architecture/INDEX.md` §1. |
| Downstream consumer | `docs/features/FS-xxx-*.md` — the next stage in the chain; both the ladder's `GDS-05`/`GDS-06` and a cluster's `ADS-xxx` Decision Log should read as direct inputs to drafting or revising an FS-xxx. |

## Workflow A — the global ladder (`GDS-00`…`GDS-10`)

This is the default workflow: when invoked without a specific capability cluster named, advance
the ladder.

1. **Find the next unauthored level.** Read [`architecture/INDEX.md`](../../../docs/architecture/INDEX.md)
   §1's table top to bottom; the first row still `⛔ Planned (scaffold only)` is the level to work
   on. Levels must be done in order — do not jump ahead even if a later level looks easier or more
   interesting.
2. **Confirm the gate on the *previous* level is actually closed**, not just that its file exists.
   Re-open the previous `GDS-NN`'s "Merge gate" checklist; every box must be checked and the
   merge decision actually recorded in that document, not merely referenced. If it isn't, finish
   that gate first — do not author the next level on top of an open gate.
3. **Author the level's content**, replacing its stub body, using:
   - The level's stated Purpose (already in the stub).
   - The "Merges from" document(s) named in its own file and in `architecture/INDEX.md` §1 — pull
     the actual content in, don't just cite it from a distance.
   - Cross-cutting grounding as relevant: `CLAUDE.md` load-bearing invariants, `docs/build-spec/`
     (wins on conflict), `docs/domains/`, `docs/research/` for any domain claim the level needs.
4. **Close that level's merge gate**, checking off each box in its "Merge gate" section and
   recording the actual merge decision (not just "done") — e.g. whether the existing document
   becomes a pointer to this one, stays authoritative, or some other resolution.
5. **Update the level's `Status`** to `✅` (or `🚧` if substantively drafted but the merge isn't
   fully closed — in which case the *next* level still may not start) and flip the row in
   `architecture/INDEX.md` §1 and `ROADMAP.md`'s "Global ladder" table together, so they never
   drift.
6. **Cross-link** — update the merged-from document's own metadata/cross-references if the merge
   decision calls for it (e.g. `MSTR-001` pointing back to `GDS-00`).
7. **Verify, then commit.** Commit as `docs(architecture): GDS-NN — <what changed>`.
8. **Stop at the level just closed** — do not cascade into the next level in the same pass unless
   explicitly asked to advance multiple levels; each level is a reviewable unit.

### Quality gate (before flipping a `GDS-NN` to `✅`)

- [ ] The stub's placeholder body has been replaced with real content addressing its stated Purpose.
- [ ] Every box in that level's own "Merge gate" checklist is checked, with the actual decision
      recorded in prose, not just a checked box.
- [ ] No production code, no literal API/schema definitions where the level doesn't call for them
      (e.g. `GDS-09` API Specification may sketch contracts; `GDS-00` Vision should not).
- [ ] `architecture/INDEX.md` §1 and `ROADMAP.md`'s "Global ladder" table both updated, in sync.
- [ ] The level does not silently contradict `docs/build-spec/` (`MSTR-001` §7 — build spec wins);
      a real tension is an Open Question, not a unilateral resolution.

## Workflow B — per-cluster `ADS-xxx`

Use this when a specific capability cluster (not the whole system) has design tension the ladder
doesn't resolve at the system level — see `MSTR-005` §3a.

1. **Identify the capability cluster.** Which `DOM-xxx` owns it? Which `R-xxx` topics ground it?
   Is there already an `FS-xxx` (even a stub/candidate) this synthesis would feed?
2. **Check existing coverage first.** Read `architecture/INDEX.md` §2 — has this cluster already
   been synthesized?
3. **If a gap exists:** add a row to `architecture/INDEX.md` §2's corpus table (status
   `⛔ Planned`) and to `ROADMAP.md`'s Architecture / Design Synthesis theme table, before writing
   the document — index-before-content.
4. **Draft the ten fixed sections** (`MSTR-005` §3a), in order: Executive Design Overview, System
   Architecture, Domain Model, User Stories, Functional Requirements, Non-functional Requirements,
   Constraints, Risks, Open Questions, Decision Log.
5. **Carry the required metadata block** (`MSTR-006` §5) — `Dependencies` lists the `DOM-xxx`/
   `R-xxx` it synthesizes; `Produces` names the `FS-xxx` it feeds.
6. **Size discipline.** ~8-15 pages equivalent; split into `ADS-xxxA`/`ADS-xxxB` rather than one
   oversized document.
7. **Cross-link both directions**, flip status to `✅` once done, update `architecture/INDEX.md` §2
   and `ROADMAP.md` together, commit as `docs(architecture): ADS-xxx — <what changed>`.

### Quality gate (before calling an `ADS-xxx` done)

- [ ] All ten sections present, in order, none reduced to a placeholder.
- [ ] Every Functional Requirement traces to a specific `DOM-xxx`/`R-xxx` citation.
- [ ] Non-functional Requirements explicitly check against `CLAUDE.md`'s load-bearing invariants.
- [ ] Open Questions are genuinely open; decisions belong in the Decision Log.
- [ ] No production code, no literal API/schema definitions.
- [ ] Frontmatter `Dependencies`/`Referenced By`/`Produces` bidirectionally consistent.
- [ ] Added to `architecture/INDEX.md` §2's corpus table and `ROADMAP.md`'s theme table, in sync.
- [ ] File length stays in the 8-15 page band; oversized syntheses get split.

## Gotchas

- Don't let this skill become a backdoor for adding research content. A claim that needs a new
  citation belongs in `research-doctrine-exercises`/`research-ow-orbital-mechanics` first; this
  skill cites, it doesn't originate domain knowledge.
- Don't write an `ADS-xxx` for a feature that doesn't need one — per `MSTR-005` §4 this is optional,
  and a one-paragraph-scope feature absorbing the synthesis into its own `FS-xxx` §1-2 is the
  expected, lighter-weight path.
- `docs/build-spec/` still wins on any conflict (`MSTR-001` §7) — an `ADS-xxx`'s System Architecture
  or Constraints section cannot quietly contradict the binding spec; flag the tension as an Open
  Question instead of resolving it unilaterally.
- This skill does not touch `docs/design/` (architecture for capabilities already built) or
  `docs/scenarios/` (still an open, unresolved directory per `ROADMAP.md` — do not start populating
  it under this skill's authority).
- An `ADS-xxx`'s Decision Log is the load-bearing artifact for whoever drafts the downstream
  `FS-xxx` — if a decision isn't recorded there with its rationale, the synthesis effectively didn't
  happen.
- Never skip a level in the global ladder, even if a later `GDS-NN` looks easier or more urgent —
  the ladder is strictly sequential by design (`MSTR-005` §3b).
- Never start `GDS-(N+1)` before `GDS-N`'s merge gate is **fully closed and the merge decision
  recorded in prose** — a checked box with no recorded decision, or a merge gate left partially
  open, means `GDS-N` is not actually done, regardless of whether its file exists and reads well.
- The ladder is new, separate content layered on top of the existing corpus — it does not silently
  supersede `MSTR-001`, `build-spec/`, or `design/`. Those stay authoritative until a given
  `GDS-NN`'s merge step explicitly folds their content in and records that decision; don't treat a
  `GDS-NN` file's mere existence as having already superseded its merge target.
