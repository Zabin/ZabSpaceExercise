# Gap Analysis — R313–R317 Operator-Perspective Research vs. GDS-01–04

> Companion to [`r313-r317-integration-summary.md`](r313-r317-integration-summary.md) (the
> Architecture Review Summary / consistency check) and the per-document "Research integration
> (R313–R317)" sections added to `GDS-01`–`GDS-04` themselves. This file is the Phase 2 deliverable:
> a structured gap analysis produced **before** any document edit, per the governing instruction.
> Each finding below cites the specific research section that motivates it and states the specific
> document/section the finding was applied to (or, where left open, why).

**Scope discipline:** every finding below is sourced from
[`R313`](../research/encyclopedia/R313-maritime-operator-perspective.md),
[`R314`](../research/encyclopedia/R314-land-operator-perspective.md) (draft, citations
unverified — used for terminology/analogy only, not as a verified source of fact),
[`R315`](../research/encyclopedia/R315-air-operator-perspective.md),
[`R316`](../research/encyclopedia/R316-joint-and-combined-operations.md), or
[`R317`](../research/encyclopedia/R317-space-operator-perspective.md). No finding below introduces
a claim the research doesn't already make; this document's job is mapping those claims onto the
existing four architecture documents, not inventing new ones.

---

## 1. Cross-cutting findings (apply to more than one document)

| # | Finding | Research source | Disposition |
|---|---|---|---|
| C1 | The simulator's flat single-Blue-cell / single-Red-cell model has no concept of internal command relationships (OPCON/TACON-equivalent) that every other domain's research treats as load-bearing. R316 explicitly warns against silently assuming the existing model already represents full joint structure. | R313 §3.2/§3.7, R314 §3.1, R315 §3.8, R316 §3.1 | Applied as a **forward-looking, explicitly-not-yet-implemented** "Command Relationship" concept in GDS-04 §3 (new), referenced from GDS-01 §2/§14 and GDS-03's forward-looking subsystem note. Framed as candidate future work, not an as-built claim. |
| C2 | Every domain converges on the same generic decision-cycle shape (OODA-family: observe/orient-classify, decide, act, assess) under different names — D3A (land), F2T2EA/dynamic targeting (air), detect→track→characterize→engage (maritime/space SDA), JPP (joint planning). The simulator already implements one instance of this (custody/track confidence → weapons-quality gate → effect) but never names it as a general pattern. | R313 §3.5/§3.6, R314 §3.2, R315 §3.4/§3.5, R316 §3.2, R317 §3.3 | Named explicitly as a reusable **Decision Cycle** architectural concept in GDS-01 §1 (new sub-bullet) and GDS-03 §4 (new cross-cutting concern), citing the existing custody/track chain as the system's one shipped instance. |
| C3 | "Mission command" / command-by-intent / disciplined initiative is the consistent command philosophy across land, air, maritime, and joint doctrine, and is the doctrinal *reason* the simulator's plan-first (not micromanagement) commanding invariant rings true operationally, not just as an engineering constraint. | R313 §3.7, R314 §3.1, R315 §3.8, R316 §3.5 | Cited in GDS-01 §1 and §10 as the doctrinal grounding for the existing plan-first invariant — clarifies *why*, adds no new mechanic. |
| C4 | Planning horizons and "branches and sequels" (joint/land planning vocabulary) map directly onto the simulator's existing AAR branch-compare feature, which previously had no doctrinal framing. | R314 §3.2, R316 §3.2 | Cited in GDS-01 §8 (AAR/replay mode) as the doctrinal name for a feature that already exists; no new capability. |
| C5 | Operational assessment / MOE-MOP (air doctrine's explicit vocabulary) is the doctrinal name for the gap GDS-01 Open Question 5 already flags (no architecture-wide owning subsystem for assessment/scoring), resolved by ADR-0029 as "out of scope for v1, raw AAR export is sufficient." | R315 §3.14, R316 §3.2 | Cited as corroborating context in GDS-01 §13 alongside the existing ADR-0029 resolution; does not reopen the resolved question. |
| C6 | Resilience / mission assurance under contested conditions (comms-denied mission command, EW-degraded ops, cyber-inseparable-from-EW per the 2022 Viasat KA-SAT precedent) is a load-bearing cross-domain theme the existing corpus only partially covers (safe-mode recovery chain), with no architectural concept of graceful degradation *under sustained denial* rather than a single fault event. | R313 §3.7, R314 §3.5, R315 §3.17/§3.19, R317 §3.6 | Added as a new Open Question in GDS-03 (resilience-under-sustained-denial is broader than the existing single-fault safe-mode model) rather than resolved — it is a design question, not a documentation fix. |
| C7 | Autonomy and human-machine teaming is the explicit final-stage theme of the space-domain's own historical arc (R317 §3.7–3.8) and is directly relevant to AI-Red, which the existing corpus already flags as an open epistemic-parity question (GDS-01 Open Question 6, resolved by ADR-0024 as a known gap/future work, not a deliberate design). | R317 §3.5/§3.7/§3.8 | Cited in GDS-01 §13 and GDS-04 §3 (new) as the doctrinal/historical grounding for *why* AI-Red's parity gap matters beyond an engineering nuisance — corroboration, not a new resolution. |

## 2. GDS-01 (Concept of Operations) — specific gaps

| # | Gap | Research source | Disposition |
|---|---|---|---|
| 1.1 | §1 (mission) lists SDA, counterspace effects, recovery — but never states that these are *one domain's instance* of generically reusable operational concepts (decision cycles, mission command, resilience) that the wider corpus's research now names explicitly. | R313–R317 generally | New sub-bullet added to §1 naming the cross-domain concepts and citing C1–C7 above. |
| 1.2 | §6 (typical user scenarios) has no scenario illustrating joint/cross-domain dependency (e.g. how a space effect supports or is supported by another domain), despite R316 §3.6 stating every domain depends on space support and the program's own future-expansion goal (additional military domains, coalition operations). | R316 §3.1/§3.6 | New scenario bullet added to §6, explicitly framed as illustrative/conceptual (the simulator does not implement other domains) rather than a feature claim. |
| 1.3 | §13 has no Open Question about command-relationship layering (C1) or sustained-denial resilience (C6). | R316 §3.1, R313/R314/R315/R317 resilience material | Two new Open Questions added to §13. |

## 3. GDS-02 (System Context) — specific gaps

| # | Gap | Research source | Disposition |
|---|---|---|---|
| 2.1 | §9 states flatly "no other live external system is in scope for v1." The original task prompt's generic instruction to "add external systems like Mission Planning, Intelligence, SDA, Coalition Interfaces" would **contradict this binding build-spec statement** if asserted as current scope. | `build-spec/01` §3.1–3.2 (binding, wins per MSTR-001 §7); R316 §3.4/§3.6 (joint C2 architectures, coalition data sharing) | Resolved by adding a clearly-labeled **forward-looking** subsection ("Candidate future external systems") to §9, explicitly scoped as *not* current v1 scope and citing the specific R316 sections that would motivate each candidate if a coalition/joint extension were ever built. The existing "no other live external system is in scope for v1" sentence is preserved verbatim, not weakened. |
| 2.2 | §5/§8 (user roles, external interfaces) have no actor representing a future coalition partner or joint-force external interface, which R316 explicitly distinguishes from the current Red/Blue/White model. | R316 §3.3 (coalition vs. combined ops) | New Open Question added rather than a new actor — adding an actor without a backing capability would misrepresent current scope. |

## 4. GDS-03 (Architecture) — specific gaps

| # | Gap | Research source | Disposition |
|---|---|---|---|
| 3.1 | §2 enumerates exactly 5 subsystems (Simulation Engine, Session/Application Layer, Mock SSN, Presentation, Content & Data) — none correspond to "Mission Planning Engine," "Decision Support Engine," etc. named in the generic task prompt. Asserting these as existing subsystems would be false; the as-built system has no such components. | All five R-docs' "Implementation Guidance"/transferable-lesson bullets (e.g. R315 §3.19 IADS-as-system, R316 §5 fog-of-war-relaxation guidance) | Resolved by adding a new **forward-looking-only** §5 ("Forward-looking architectural considerations") clearly separated from and subordinate to §2's as-built subsystem list, naming candidate future subsystems (Decision Support / Autonomy Manager / Knowledge Base) each tied to a specific research citation and explicitly marked "not built, not committed, research-grounded placeholder for a future ADS-xxx if a feature is ever proposed." |
| 3.2 | §4 (cross-cutting concerns: determinism, fog-of-war, multiplayer authority, plan-first commanding) has no entry for the Decision Cycle pattern (C2) even though it is arguably as cross-cutting as the other four. | R313/R314/R315/R316/R317 decision-cycle material | New cross-cutting concern added to §4. |
| 3.3 | No Open Question captures the resilience-under-sustained-denial gap (C6). | R315 §3.17/§3.19, R317 §3.6 | New Open Question added to §3's Open Questions list (left unresolved — design decision, not documentation fix). |

## 5. GDS-04 (Domain Model) — specific gaps

| # | Gap | Research source | Disposition |
|---|---|---|---|
| 4.1 | §1's 14 entities have no Command Relationship / Authority concept (C1), no Intent/Commander's-Intent concept (C3), and no generic Decision Cycle concept (C2) — all three are named as load-bearing by multiple independent research documents. | R313 §3.2/§3.7, R314 §3.1, R315 §3.8, R316 §3.1/§3.2, R317 §3.3 | Resolved by adding a new §3 ("Forward-looking domain concepts — not yet implemented") **clearly separated** from §1's as-built entity list, sketching Command Relationship, Intent, and Decision Cycle at the conceptual level only (no schema, no fields, no persistence model — that would be GDS-07's job and would overstate this document's charter). Each concept is tied to its research citation and explicitly marked as not present in `design/04-data-model.md` or any shipped code. |
| 4.2 | Open Question 3 (SSN Request vs. Planned Activity supertype naming) is already flagged; R313's ASW classification chain and R317's SDA detect→track→characterize→attribute chain are additional cross-domain analogs for the same custody/track pattern, corroborating that this is a generic pattern worth a supertype, not a one-off. | R313 §3.5, R317 §3.2 | Appended as corroborating citation to the existing Open Question 3; not re-resolved. |
| 4.3 | No Open Question exists asking whether the new forward-looking §3 concepts should eventually become real GDS-04 §1 entities, and under what trigger. | — (process gap, not a research gap) | New Open Question added, asking this explicitly so the forward-looking section doesn't quietly ossify into unreviewed scope creep. |

---

## Disposition summary

- **6 new Open Questions** added across the four documents (GDS-01: 2, GDS-02: 1, GDS-03: 2, GDS-04: 1) — left genuinely open, not resolved, per the "documentation pass, not a design decision" discipline already established by the prior architecture-review reconciliation.
- **3 new forward-looking-only subsections** added (GDS-02 §9 candidate external systems, GDS-03 §5 candidate subsystems, GDS-04 §3 candidate domain concepts) — each explicitly labeled as research-grounded but not-yet-built, to avoid contradicting `build-spec/`'s actual v1 scope per `MSTR-001` §7.
- **No existing sentence, table row, or Open Question resolution was deleted or weakened.** All edits are additive, consistent with the "expand in place, preserve valid existing content" instruction.
- **No new entity, subsystem, or external system was asserted as built.** Where the generic task prompt's candidate list (Mission Planning Engine, Coalition Interfaces, etc.) would have implied current scope, it was reframed as explicitly future/conceptual to avoid contradicting the binding build-spec.

## Related

[`r313-r317-integration-summary.md`](r313-r317-integration-summary.md) (consistency check across
the four updated documents) ·
[`architecture/01-concept-of-operations.md`](../architecture/01-concept-of-operations.md) §"Research
integration (R313–R317)" ·
[`architecture/02-system-context.md`](../architecture/02-system-context.md) §"Research integration
(R313–R317)" ·
[`architecture/03-architecture.md`](../architecture/03-architecture.md) §"Research integration
(R313–R317)" ·
[`architecture/04-domain-model.md`](../architecture/04-domain-model.md) §"Research integration
(R313–R317)".
