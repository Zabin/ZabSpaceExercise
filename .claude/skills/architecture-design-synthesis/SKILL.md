---
name: architecture-design-synthesis
description: Synthesize a capability cluster's domain framework (DOM-xxx) and research grounding (research/encyclopedia R1xx-R5xx + research/01-07 primers) into a Design Synthesis document (ADS-xxx) under docs/architecture/ — the bridge between domain+research and a Feature Specification. Use when asked "what are the core concepts," "which mechanics are actually required," "which requirements conflict," "what assumptions must be made," "what is the minimum viable implementation," "what is deferred," or to produce/refresh an Executive Design Overview, System Architecture, Domain Model, User Stories, Functional/Non-functional Requirements, Constraints, Risks, Open Questions, or Decision Log for a capability before drafting or revising an FS-xxx. This produces design documents, not research documents — do not use it to add new doctrinal/orbital-mechanics claims (that's research-doctrine-exercises / research-ow-orbital-mechanics).
---

# Architecture / Design Synthesis

Produces `docs/architecture/ADS-xxx-<slug>.md` — the **Design Synthesis** tier defined in
[`MSTR-005`](../../../docs/master/MSTR-005-documentation-map.md) §3a/§4 and tracked in
[`docs/architecture/INDEX.md`](../../../docs/architecture/INDEX.md). Read both before producing
anything; this skill operationalizes them, it does not restate them.

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
| [`architecture/INDEX.md`](../../../docs/architecture/INDEX.md) + `ADS-xxx-*.md` | The Design Synthesis tier this skill authors. |
| Grounding inputs | `docs/domains/DOM-xxx-*.md` (which framework owns the capability), `docs/research/encyclopedia/R1xx-R5xx` + `docs/research/01-07` primers (what domain knowledge constrains the design), `docs/build-spec/` (binding v1 spec — wins on any conflict), `docs/design/` (existing architecture for capabilities already built). |
| Downstream consumer | `docs/features/FS-xxx-*.md` — the next stage in the chain; an `ADS-xxx`'s Decision Log and Functional Requirements should read as direct inputs to drafting or revising the corresponding FS-xxx. |

## Workflow

1. **Identify the capability cluster.** Which `DOM-xxx` owns it? Which `R-xxx` topics ground it?
   Is there already an `FS-xxx` (even a stub/candidate) this synthesis would feed? Read all of them
   before drafting anything — per `MSTR-006` §4, documents in this corpus are independently
   retrievable, but that means *this* document must do the reading, not assume context.
2. **Check existing coverage first.** Read [`architecture/INDEX.md`](../../../docs/architecture/INDEX.md)
   — has this cluster already been synthesized? Is there a related `ADS-xxx` whose Decision Log
   already settled part of this?
3. **If a gap exists:** add a row to `architecture/INDEX.md`'s corpus table (status `⛔ Planned`)
   and to `ROADMAP.md`'s Architecture / Design Synthesis theme table, before writing the document —
   index-before-content, the same convention `research-doctrine-exercises` uses.
4. **Draft the ten fixed sections** (`MSTR-005` §3a), in order:
   1. Executive Design Overview — one paragraph: the cluster, the problem, the biggest design
      tension this synthesis resolves.
   2. System Architecture — seams/interfaces/data flow at the `design/01-architecture-overview.md`
      level (engine/session/content/ui boundaries), never literal code (`MSTR-006` §8).
   3. Domain Model — entities, relationships, invariants, independent of UI/API shape.
   4. User Stories — cell-perspective ("as Blue/Red/White, I need to...") scenarios, traceable to a
      vignette or training objective.
   5. Functional Requirements — numbered, each citing the `DOM-xxx`/`R-xxx` source that justifies it.
   6. Non-functional Requirements — which load-bearing invariants (`CLAUDE.md` §"Load-bearing
      invariants": determinism, UI-agnostic engine, fog-of-war at the boundary, plan-first,
      sub-stepped clock, content-as-data) constrain this cluster specifically.
   7. Constraints — fixed boundaries not up for revision here (existing engine seams, the six
      access channels, the five-D taxonomy, the cyber exception).
   8. Risks — what could go wrong (scope creep into an adjacent FS's territory, an invariant
      violation, an unstated assumption) and how this synthesis mitigates or flags each.
   9. Open Questions — genuine ambiguity not resolved here, flagged per `MSTR-006` §6 rather than
      silently decided — and escalated to the user if it changes scope or strategic direction.
   10. Decision Log — the choices actually made among competing options, one line of rationale
       each, so a later reader (or an `FS-xxx` author) sees what was considered and rejected.
5. **Carry the required metadata block** (`MSTR-006` §5: Document ID, Version, Status, Dependencies,
   Referenced By, Produces, Feature Mapping, Related Topics) — `Dependencies` lists the `DOM-xxx`/
   `R-xxx` it synthesizes; `Produces` names the `FS-xxx` it feeds (or "candidate scope for a future
   FS-xxx" if none exists yet).
6. **Size discipline.** ~8-15 pages equivalent (`MSTR-006` §4). A synthesis that needs more room
   should split into `ADS-xxxA`/`ADS-xxxB` rather than growing one oversized document.
7. **Cross-link both directions** — add this `ADS-xxx` to the grounding `DOM-xxx`/`R-xxx` documents'
   `Referenced By`, and to the downstream `FS-xxx`'s `Dependencies` if that document already exists.
8. **Flip status to `✅`** once the quality gate below is satisfied; update `architecture/INDEX.md`
   and `ROADMAP.md` together so they never drift.
9. **Verify, then commit.** Commit as `docs(architecture): ADS-xxx — <what changed>`, consistent
   with this branch's existing commit style.

## Quality gate (before calling an `ADS-xxx` done)

- [ ] All ten sections present, in order, none reduced to a placeholder.
- [ ] Every Functional Requirement traces to a specific `DOM-xxx`/`R-xxx` citation, not a generic
      claim invented for this document.
- [ ] Non-functional Requirements explicitly check against `CLAUDE.md`'s load-bearing invariants —
      silence on an invariant that's actually relevant to this cluster is a gap, not an "N/A."
- [ ] Open Questions are genuinely open (not a place to bury a decision that was actually made) —
      decisions belong in the Decision Log.
- [ ] No production code, no literal API/schema definitions (that's `IMP-xxx`'s job downstream).
- [ ] Frontmatter `Dependencies`/`Referenced By`/`Produces` are bidirectionally consistent with the
      `DOM-xxx`/`R-xxx`/`FS-xxx` documents it touches.
- [ ] Added to `architecture/INDEX.md`'s corpus table and `ROADMAP.md`'s theme table, in sync.
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
