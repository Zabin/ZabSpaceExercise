# MSTR-004 — Glossary

> **Document ID:** MSTR-004
> **Version:** 1.0
> **Status:** ♻️ Living (extend as new terms enter the corpus)
> **Dependencies:** MSTR-001
> **Referenced By:** all documents in `docs/domains/`, `docs/research/`, `docs/features/`, `docs/implementations/`
> **Produces:** the canonical term set new documents must reuse rather than re-define
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`docs/build-spec/04-nfr-milestones-and-risks.md`](../build-spec/04-nfr-milestones-and-risks.md) §12,
> [`docs/training/09-troubleshooting-and-glossary.md`](../training/09-troubleshooting-and-glossary.md)

[↑ Docs index](../INDEX.md) · [Master index](MSTR-005-documentation-map.md)

## 1. Purpose

A single cross-cutting glossary so that "custody," "fog-of-war," "access window," etc. mean exactly
one thing everywhere in this documentation tree. The build-spec glossary
(`build-spec/04-nfr-milestones-and-risks.md` §12) and the training glossary
(`training/09-troubleshooting-and-glossary.md`) remain authoritative for operator-facing wording;
this document is the superset used by domain/research/feature/implementation authors, including
terms from decision science, military analysis, and research methods that the operator-facing
glossaries do not need.

## 2. Core simulation terms

| Term | Definition |
|---|---|
| **Access window** | A geometrically valid interval during which a given access channel (see below) is usable between an asset and an endpoint. Commands/sensing/effects outside a window have no effect — they are denied, not degraded. |
| **Access channel** | One of six categorized link types: `command_uplink`, `telemetry_downlink`, `sensor_observation`, `jam_footprint`, `weapon_engagement`, `rpo_proximity`. |
| **Custody** | The state of having an actively maintained, sufficiently confident track on an object, modeled by `Track` with on-demand confidence decay. Custody is what makes an object engageable/taskable; losing custody does not delete history but reduces confidence. |
| **Weapons-quality track** | A custody track that has crossed the confidence threshold required to authorize a weapon-class effect against it — a gate, not just a label. |
| **Fog-of-war** | The structural limitation that Red/Blue render only their own belief state (`TrackCatalog`/`CellView`), never ground truth, enforced at the `SessionAPI`/`CellController` boundary. |
| **Five D's** | The effect taxonomy: deceive, disrupt, deny, degrade, destroy. Cyber is the doctrinal exception (resolves against `{access_vector, success_prob, persistence, patchable}`, not window-gated). |
| **Safe mode** | A bus/payload self-protective degraded state entered on persistent anomaly; recovered via `RecoverySystem`'s multi-pass logic, sometimes requiring root-cause fix (e.g. `def.patch_cyber`) before re-safing stops recurring. |
| **State of health (SOH)** | The bus/payload telemetry surface (`BusState`/`PayloadState`) exposing limits, gating, and safe-mode status to the operator. |
| **Sub-stepped clock** | Advancing simulation time to the next scheduled event rather than a fixed step size, so short access windows are never silently skipped at high time-acceleration. |
| **Vignette** | A YAML-defined scenario: initial world state, per-cell objectives, ROE, ISL/coaching notes, and (for the 8 canonical + training-basics) a `tutorial:` script. |
| **Inject** | A White-Cell-triggered scripted event (debris breakup, GNSS-jam advisory, etc.) drawn from `inject_library.yaml` or authored ad hoc. |
| **White Cell** | The facilitator role: runs the exercise, has god-view, authors injects, controls clock/pacing — the instructional designer, not a neutral referee (see MSTR-003 §7). |
| **AAR (After Action Review)** | The post-exercise replay/scrub/branch-compare capability (P7) used to debrief decisions against both belief-at-the-time and ground truth. |
| **Determinism** | `(initial_state, ordered eventlog, seed) → byte-identical state`, always — the property that makes rewind/undo/branch exact. |
| **Replay-safe** | A function that computes a view without mutating `WorldState` or consuming RNG (e.g. `scene.py`, `telemetry.py`, `orders.dry_run()`). |
| **Dry run** | A read-only mirror of `OrderSystem.issue()` that validates and resolves the delivery path without scheduling/booking anything — powers "why can't I do this" UI affordances. |

## 3. Decision-science terms (Tier R200 vocabulary)

| Term | Definition | Primary research doc |
|---|---|---|
| **Bayesian updating** | Revising a probability estimate (e.g., confidence an unknown contact is hostile) in light of new evidence, proportionally to how diagnostic the evidence is. | R201 |
| **Bounded rationality** | Decision-making under real constraints on time, information, and cognitive capacity — the realistic model of how operators actually decide, vs. idealized expected-utility maximization. | R206 |
| **OODA loop** | Observe–Orient–Decide–Act; the canonical model of the plan-execute-update cycle SpaceSim structurally enforces (MSTR-003 §3). | R208 |
| **Cognitive bias** | A systematic deviation from rational judgment (e.g., confirmation bias, anchoring) relevant to how Red/Blue interpret ambiguous custody data. | R207 |
| **Multi-criteria decision analysis (MCDA)** | Structured methods for choosing among options scored on multiple, sometimes conflicting, criteria — relevant to COA selection. | R212 |
| **Signaling theory** | The study of how actions convey (intentional or unintentional) information to an observer — relevant to escalation and deterrence dynamics. | R213 |
| **Utility theory** | The formal framework for representing preferences and risk attitudes as a scalar to be maximized — underlies COA scoring. | R214 |

## 4. Military-analysis terms (Tier R300 vocabulary)

| Term | Definition | Primary research doc |
|---|---|---|
| **Center of gravity (COG)** | The source of an actor's power/freedom of action whose neutralization would be most damaging to their ability to operate. | R309 |
| **Effects-based operations (EBO)** | Planning oriented around the cascading effects an action produces, rather than the action's direct kinetic/physical output alone. | R310 |
| **Course of action (COA)** | A distinct, comparable option for achieving an objective, evaluated against criteria before commitment. | R311 |
| **Escalation** | A shift to a more severe/risky category of action or response; modeled in SpaceSim via the kinetic-confirm gate and ROE chips. | R304 |
| **Deterrence** | Discouraging an adversary action by credibly threatening unacceptable cost; distinguished from compellence (forcing an action). | R303 |
| **Wargaming theory** | The methodological study of what wargames can and cannot validly demonstrate, and how to design them so conclusions are sound. | R307 |
| **Red teaming** | Structured adversarial role-play intended to surface blind spots in a plan or assumption set — the doctrinal basis for the Red cell's role. | R308 |

## 5. Research-methods terms (Tier R400 vocabulary)

| Term | Definition | Primary research doc |
|---|---|---|
| **Hypothesis** | A falsifiable, stated prediction an experiment or assessment is designed to test. | R402 |
| **Control** | A condition held constant (or a comparison group) so an observed effect can be attributed to the manipulated variable. | R401 |
| **Monte Carlo method** | Repeated randomized simulation used to characterize an outcome distribution rather than a single deterministic run — used for vignette balance/sensitivity studies, never inside the deterministic engine itself (MSTR-002 invariant 1 still holds; Monte Carlo studies run the deterministic engine many times with different seeds). | R407 |
| **Sensitivity analysis** | Systematically varying one input to see how much it moves an outcome — used to find which vignette parameters (e.g. drain rate) actually matter. | R408 |
| **Verification vs. validation** | Verification: "did we build the model right" (matches spec). Validation: "did we build the right model" (matches the real-world phenomenon it represents). | R409, R410 |

## 6. Adding a term

New documents that introduce a term not in this glossary should add it here in the same edit, in
the appropriate section (or a new section if the term belongs to a tier not yet represented), with
a one-line definition and a pointer to the document that elaborates it. Do not silently redefine an
existing term — if a document needs a narrower or different sense of an existing term, that is a
signal to either reconcile the definitions or flag a conflict per
[`MSTR-006`](MSTR-006-governance-principles.md) §3.
