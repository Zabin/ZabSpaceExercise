# MSTR-007 — Research Philosophy

> **Document ID:** MSTR-007
> **Version:** 1.0
> **Status:** ✅ Stable
> **Dependencies:** MSTR-001, MSTR-002
> **Referenced By:** DOM-004, all R1xx-R5xx encyclopedia documents, `docs/research/encyclopedia/R*00-index.md`
> **Produces:** the design rules for the entire research encyclopedia (R100-R500)
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`docs/FUTURE-WORK.md`](../FUTURE-WORK.md) §12 (the precedent corpus-expansion plan),
> [`docs/research/INDEX.md`](../research/INDEX.md) (the existing doctrine/physics primers)

[↑ Docs index](../INDEX.md) · [Master index](MSTR-005-documentation-map.md)

## 1. Purpose

States why the research encyclopedia (`docs/research/encyclopedia/`, tiers R100-R500) exists, what
it is *not* for, and the fixed structure every topic document must follow. DOM-004 (Research
Framework) governs the broader research program (including the human-subject/validation research
the simulator might support); this document is specifically about the encyclopedia corpus's
purpose and shape.

## 2. The purpose is domain understanding, not academic research

**This is the single most important distinction in this document.** The encyclopedia is not an
academic literature review and is not trying to advance the state of the art in orbital mechanics,
decision theory, or military analysis. Its purpose is narrower and more practical: **give a future
coding LLM agent enough domain understanding to implement a feature correctly without
misunderstanding the terminology, the operational workflow, or the implementation implications of
a concept it has only seen used, not explained.**

Concretely, this means every topic document should answer "if an agent is about to implement
something touching this concept, what does it need to know to not get it wrong" — not "what is the
complete scholarly treatment of this concept." A document that is rigorous but useless for
implementation guidance has failed at this corpus's actual job.

## 3. The five tiers

| Tier | Subject | Approx. count | Audience need it serves |
|---|---|---|---|
| **R100** | Space Operations Foundation | ~20-30 | Orbital mechanics, SDA, C2, custody, ground/constellation/sensor ops — the simulator's direct subject matter. |
| **R200** | Decision Sciences | ~14 | Probability, Bayesian reasoning, decision/game theory, cognitive bias, OODA, MCDA, signaling, utility, planning — what justifies the simulator's judgment-under-uncertainty design (MSTR-003 §2). |
| **R300** | Military Analysis | ~12 | Campaign design, operational art, deterrence/escalation, wargaming theory, red teaming, COG, EBO, COA analysis — what justifies White Cell / scenario design (DOM-003, DOM-009). |
| **R400** | Research Methods | ~13 | Experiment design, statistics, Monte Carlo, sensitivity analysis, V&V, measurement, uncertainty — what justifies assessment/validation work (DOM-002, DOM-005). |
| **R500** | Future Operations | ~9 | AI/autonomy, human-AI teaming, future C2, multi-domain ops — forward-looking context for DOM-008 (AI Integration) and long-horizon Feature Specs. |

Per-tier index documents (`R100-index.md` ... `R500-index.md`) list every topic in that tier with
its ID, title, one-line scope, status, and dependency on other topics.

## 4. Per-topic document shape (mandatory)

Every R1xx-R5xx document follows the same seven-section shape, because predictable structure is
itself part of what makes a document independently retrievable and quickly skimmable by an agent
under token pressure:

1. **Purpose** — one paragraph: why this topic exists in the corpus.
2. **Scope** — what is and is *not* covered here (the boundary against neighboring topics).
3. **Concepts** — the core definitions and mechanisms, the substantive content.
4. **Operational Context** — how this concept shows up in actual space operations / decision-making
   / military analysis / research practice (the "why a human in this domain cares").
5. **Implementation Guidance** — the part academic treatments never have: concretely, what should
   an implementer do differently *because* this concept is true? (e.g., "because custody confidence
   decays continuously, don't cache a track's engageability boolean — recompute it at the moment of
   use.")
6. **Feature Mapping** — which FS-xxx specifications this topic is foundational to.
7. **Related Topics** — cross-links, including to the pre-existing `research/01-07` primers where
   this topic elaborates or implements something already discussed there.

A topic document missing §5 (Implementation Guidance) has not done the job this corpus exists for,
even if §1-4 and §6-7 are excellent.

## 5. Relationship to the existing `research/01-07` primers

The existing primers (doctrine, counterspace taxonomy, orbital mechanics, mission types, bus/payload
ops, legal norms) are **not superseded**. They answer "why are the simulator's rules what they are"
at a design-rationale level. The encyclopedia answers a narrower, more numerous set of "what does
this term/concept mean and imply for implementation" questions, often at a finer grain (e.g.
`04-orbital-mechanics-primer.md` covers orbital mechanics broadly; R101 "Orbital Mechanics for
Operations and Implementation" is implementation-focused and points back to `04-*` rather than
re-deriving Kepler's equations). When a new encyclopedia topic's content would simply duplicate an
existing primer, prefer making the encyclopedia topic a short pointer + implementation-implications
note rather than re-authoring the primer's content.

## 6. Authoring cadence and authorization

Per MSTR-006 §3-4, the encyclopedia is **not** authored as one giant batch job:

- Each tier has its own index document built first, enumerating every planned topic with ID,
  dependencies, and status, **before** the topic documents themselves are written — this mirrors
  the precedent in `FUTURE-WORK.md` §12 (file-by-file scoping ahead of authoring).
- Topics within a tier may be authored incrementally; later tiers (especially R300-R500, which are
  larger lifts and more speculative/forward-looking) should be explicitly authorized before bulk
  authoring begins, exactly as `FUTURE-WORK.md` §12's Tier 2-4 research items are marked 🅿️ pending
  user go-ahead.
- Per-document size stays in the 3-8 page band (MSTR-006 §4) — depth comes from having many focused
  topics, not from a few sprawling ones.

## 7. What "comprehensively covers the domain" means in practice

The instruction to "continue expanding until the tier comprehensively covers the simulator domain"
is a *coverage* test against the simulator's actual feature surface, not an arbitrary count target.
A practical check: walk the engine code-map in `CLAUDE.md` ("Code map (current)") and the build
spec's functional requirements — every named subsystem (custody, ISR, jam, engage, cyber, SIGINT,
SSN, recovery, telemetry, bus/payload, perturbations, maneuver) should have at least one R1xx topic
that an implementer extending that subsystem would want to read first. Gaps found this way are
tracked in the relevant `R*00-index.md` as new `⛔ Planned` rows, not silently left out.
