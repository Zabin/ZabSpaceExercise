# MSTR-001 — Program Vision

> **Document ID:** MSTR-001
> **Version:** 1.0
> **Status:** ✅ Stable
> **Dependencies:** none (this is the root document)
> **Referenced By:** MSTR-002, MSTR-003, MSTR-004, MSTR-005, MSTR-006, MSTR-007, all DOM-*, all FS-*
> **Produces:** the mandate for DOM-001..009 and the entire downstream documentation tree
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`MSTR-002`](MSTR-002-architecture-principles.md), [`MSTR-003`](MSTR-003-educational-philosophy.md),
> [`docs/build-spec/01-context-and-scope.md`](../build-spec/01-context-and-scope.md)

[↑ Docs index](../INDEX.md) · [Master index](MSTR-005-documentation-map.md)

## 1. What this program is

The Space Control & Orbital Warfare Exercise Simulator (internally "SpaceSim", repo
`ZabSpaceExercise`) is a **professional military education (PME) wargaming tool**. A White Cell
facilitator runs a scripted or free-play exercise; Red and Blue cells command fleets of space and
ground assets as bus and payload operators, constrained by real orbital geometry — access windows,
fog-of-war, and Δv economics — rather than by an omniscient point-and-click interface.

The program exists to teach three things simultaneously, and refuses to trade any one off against
the others:

1. **Doctrine and tradecraft** — how space operators actually plan, task, and execute under
   custody/SDA constraints, the five-D's effects taxonomy (deceive/disrupt/deny/degrade/destroy),
   and the cyber exception to window-gating.
2. **Decision-making under uncertainty** — Red and Blue act on *belief state* (their own
   `TrackCatalog`), never ground truth; the simulator is a vehicle for practicing judgment under
   imperfect information, not a strategy-game answer key.
3. **After-action reflection** — every exercise is replayable, scrubbable, and branch-comparable
   (P7 capstone + AAR), because the educational payoff of a wargame lives in the debrief, not the
   button-presses.

## 2. Why this document tree exists

This program is now explicitly **documentation-driven**: the prose under `docs/` is the primary
source of design intent, and code is a downstream artifact of it, not the other way around. That
shift exists for a concrete reason — the program's primary "reader" going forward is not only a
human facilitator or instructor but a **future coding LLM agent** tasked with extending the
simulator. An agent that can read a Feature Specification and an Implementation Package and
produce correct, consistent code without reverse-engineering intent from `spacesim/engine/*.py` is
strictly more valuable, over the program's lifetime, than a codebase with good docstrings and no
design trail.

Concretely, this means:

- Every capability the simulator has, or will have, should be traceable from a **training
  objective** through a **domain framework**, through the **research** that justifies it, to a
  **Feature Specification**, to one or more **Implementation Packages**, to the code and tests that
  realize it. See [`MSTR-005`](MSTR-005-documentation-map.md) for the map and
  [`docs/domains/`](../domains/) §Traceability sections for the worked chains.
- Documentation is **versioned, statused, and dependency-tracked** like code — see
  [`MSTR-006`](MSTR-006-governance-principles.md).
- The **training corpus is a co-equal product with the code** (owner decision, 2026-07-04). The
  operator-facing manuals (`docs/training/`), the vignette learning path, and the in-app
  briefs/tutorials are requirement-bearing artifacts in their own right: grounded by their own
  research tier (R600 — training pedagogy & instructional design), governed by their own
  functional and non-functional requirements (FR-11000 family; NFR §16), and produced/reviewed by
  their own pipeline stages (`02-research-training-pedagogy`, `08-training-manual-authoring`,
  `08-vignette-development`, `09-training-manual-review`). A capability is not delivered when its
  code verifies — it is delivered when the training artifacts that teach it are current. The
  pedagogical stance itself lives in [`MSTR-003`](MSTR-003-educational-philosophy.md); this bullet
  makes its artifacts first-class citizens of the engineering baseline.
- The existing `docs/build-spec/`, `docs/design/`, `docs/research/`, `docs/training/`,
  `docs/vignettes/` corpus is **not replaced**. It is the load-bearing foundation this tree builds
  on top of and cross-references; see [`MSTR-005`](MSTR-005-documentation-map.md) §3 for exactly how
  the new (`master/`, `domains/`, `features/`, `implementations/`, `architecture/`, `scenarios/`,
  expanded `research/`) directories relate to the pre-existing five.

## 3. Audience

| Audience | What they read | Why |
|---|---|---|
| White Cell facilitators | `docs/training/`, `docs/vignettes/`, Mission brief panels | Run exercises, write injects, debrief |
| Operators (Red/Blue trainees) | `docs/training/`, in-app tutorial panel | Learn the tool and the doctrine it encodes |
| Human maintainers | `docs/build-spec/` (binding), `docs/design/`, `CLAUDE.md` | Understand what is built and why |
| **Future coding LLM agents** | `docs/master/`, `docs/domains/`, `docs/research/` (R1xx–R5xx), `docs/features/`, `docs/implementations/` | Implement new capability without inferring intent from code |
| Researchers / assessment designers | `docs/domains/DOM-002`, `DOM-004`, `DOM-005`, `docs/research/R200`, `R400` | Build measurement and validation on top of the simulator |

The fifth row is the new audience this expansion is built for. Every document in `docs/master/`,
`docs/domains/`, `docs/features/`, `docs/implementations/`, and the `R1xx`–`R5xx` research tiers is
written so it is **independently retrievable** — an agent that opens exactly one file should have
enough context to act correctly, with explicit pointers (not implicit assumptions) to whatever else
it needs. See [`MSTR-006`](MSTR-006-governance-principles.md) §4 "AI authoring constraints".

## 4. Problem statement

Space is now a contested operational domain, but most professional military education for it is
either (a) classroom doctrine with no hands-on decision practice, or (b) classified
exercise environments inaccessible for broad PME use. There is a gap for an **unclassified,
single-machine-or-LAN, deterministic, replayable** trainer that:

- enforces real orbital access constraints (you cannot command, sense, or attack outside a
  geometrically valid window);
- enforces fog-of-war structurally (Red and Blue render only their own custody picture, never
  ground truth — enforced at the session boundary, not by UI discipline);
- treats most effects as reversible (EW/cyber/proximity), reserving kinetic effects as a
  consequence-laden, confirmed, rare choice;
- is fully deterministic and replayable, so an exercise can be re-run, branched, and debriefed with
  byte-identical fidelity.

SpaceSim is the answer to that gap. Its scope is bounded deliberately (see
[`docs/build-spec/01-context-and-scope.md`](../build-spec/01-context-and-scope.md) §2–3): moderate
orbital fidelity (Keplerian + J2, real TLEs via Skyfield), not a numerical-integration-grade
astrodynamics tool; PME training value, not classified mission rehearsal; cooperative LAN play, not
a hardened multi-tenant service (see the LAN trust model documented in `CLAUDE.md`).

## 5. Success vision

The program succeeds when:

1. A White Cell facilitator with no programming background can stand up a vignette, run a 2-hour
   exercise, and conduct a doctrinally grounded AAR using only the in-app tools and
   `docs/training/`.
2. A new capability — e.g., a new sensor modality, a new effect, a new assessment metric — can be
   specified end-to-end in this documentation tree (Domain → Research → Feature Spec →
   Implementation Package) **before any code is written**, and a coding agent given only that
   trail produces a correct, tested implementation.
3. The research encyclopedia (`docs/research/` R1xx–R5xx, see [`MSTR-007`](MSTR-007-research-philosophy.md))
   is comprehensive enough that an agent never has to guess what "custody" or "OODA loop" or
   "weapons-quality track" means — the term resolves to a concept document with implementation
   implications, not just a definition.
4. Every Feature Specification and Implementation Package can be traced backward to the training
   or research need that motivated it, and forward to the code and tests that satisfy it — closing
   the loop described in [`MSTR-005`](MSTR-005-documentation-map.md) §4.
5. A brand-new operator can walk the **vignette learning path**
   (`docs/training/16-learning-path.md`) unaided — from the training-basics onboarding vignette,
   up the canonical ladder, into the mission-set tracks — because every vignette names the manual
   modules that teach its concepts, every manual section names the features it documents
   (`docs/training/15-manual-traceability.md`), and the same pipeline that changes the code keeps
   both current.

## 6. Non-goals

- **Not** a replacement for classified mission-planning or rehearsal tools.
- **Not** a numerically rigorous astrodynamics package — fidelity is "moderate, behind interfaces"
  by design (`Propagator`/`AccessProvider`/`EffectResolver` seams), so a higher-fidelity model can
  be substituted later without touching session/UI code.
- **Not** hardened against an adversarial LAN participant — the v1 trust model is cooperative (see
  `CLAUDE.md` "LAN trust model").
- **Not** a vehicle for generating code in this documentation-expansion effort — this program's
  current phase produces **only** documentation; see [`MSTR-006`](MSTR-006-governance-principles.md)
  §5 for the implementation-package boundary rule (describe code changes, never write them here).

## 7. Relationship to the build spec

[`docs/build-spec/`](../build-spec/INDEX.md) remains **binding** for v1: "on any conflict, the build
spec wins." This master-document tree does not supersede it — it surrounds it with the
domain/research/feature/implementation scaffolding the build spec assumed but never formalized.
Where this tree and the build spec appear to disagree, treat it as a signal that either (a) the
build spec needs a revision note (tracked as a `BS-0x-REV` item in `ROADMAP.md`), or (b) the new
document has mis-stated intent and should be corrected.
