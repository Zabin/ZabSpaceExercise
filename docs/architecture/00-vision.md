# GDS-00 — Vision

> **Document ID:** GDS-00
> **Version:** 1.0
> **Status:** ✅ Authored — merge gate closed (see "Merge gate" below)
> **Dependencies:** MSTR-001
> **Referenced By:** GDS-01
> **Produces:** GDS-01
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`MSTR-001-program-vision.md`](../master/MSTR-001-program-vision.md) (merge
> source — see "Merge gate" for the resolution), [`build-spec/01-context-and-scope.md`](../build-spec/01-context-and-scope.md)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

State, once and authoritatively for the whole project, what SpaceSim is for, who it serves, what
problem it answers, what success looks like, and what it deliberately is not. This is the root of
the global design-synthesis ladder (`GDS-00`…`GDS-10`); every later level traces back to this one.

## 1. What this program is

The Space Control & Orbital Warfare Exercise Simulator (internally "SpaceSim", repo
`ZabSpaceExercise`) is a **professional military education (PME) wargaming tool**. A White Cell
facilitator runs a scripted or free-play exercise; Red and Blue cells command fleets of space and
ground assets as bus and payload operators, constrained by real orbital geometry — access windows,
fog-of-war, and Δv economics — rather than by an omniscient point-and-click interface
(MSTR-001 §1).

The program teaches three things simultaneously, and refuses to trade any one off against the
others (MSTR-001 §1):

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

This program is **documentation-driven**: the prose under `docs/` is the primary source of design
intent, and code is a downstream artifact of it (MSTR-001 §2). That shift exists for a concrete
reason — the program's primary "reader" going forward is not only a human facilitator or
instructor but a **future coding LLM agent** tasked with extending the simulator. An agent that can
read a Feature Specification and an Implementation Package and produce correct, consistent code
without reverse-engineering intent from `spacesim/engine/*.py` is strictly more valuable, over the
program's lifetime, than a codebase with good docstrings and no design trail.

Concretely:

- Every capability the simulator has, or will have, should be traceable from a **training
  objective** through a **domain framework**, through the **research** that justifies it, to a
  **Feature Specification**, to one or more **Implementation Packages**, to the code and tests that
  realize it (MSTR-005 — the documentation map).
- Documentation is **versioned, statused, and dependency-tracked** like code (MSTR-006 —
  governance principles).
- The pre-existing `docs/build-spec/`, `docs/design/`, `docs/research/`, `docs/training/`,
  `docs/vignettes/` corpus is **not replaced**. It is the load-bearing foundation this tree builds
  on top of and cross-references (MSTR-005 §3).

## 3. Audience

| Audience | What they read | Why |
|---|---|---|
| White Cell facilitators | `docs/training/`, `docs/vignettes/`, Mission brief panels | Run exercises, write injects, debrief |
| Operators (Red/Blue trainees) | `docs/training/`, in-app tutorial panel | Learn the tool and the doctrine it encodes |
| Human maintainers | `docs/build-spec/` (binding), `docs/design/`, `CLAUDE.md` | Understand what is built and why |
| Future coding LLM agents | `docs/master/`, `docs/domains/`, `docs/research/` (R1xx–R5xx), `docs/features/`, `docs/implementations/` | Implement new capability without inferring intent from code |
| Researchers / assessment designers | `docs/domains/DOM-002`, `DOM-004`, `DOM-005`, `docs/research/R200`, `R400` | Build measurement and validation on top of the simulator |

(MSTR-001 §3; the LLM-agent row is the newest addition to this audience list and the one the
`master/`/`domains/`/`features/`/`implementations/` tiers are written for — independently
retrievable, with explicit pointers rather than implicit assumptions, per MSTR-006 §4.)

## 4. Problem statement

Space is now a contested operational domain, but most professional military education for it is
either (a) classroom doctrine with no hands-on decision practice, or (b) classified exercise
environments inaccessible for broad PME use. There is a gap for an **unclassified,
single-machine-or-LAN, deterministic, replayable** trainer that:

- enforces real orbital access constraints (you cannot command, sense, or attack outside a
  geometrically valid window);
- enforces fog-of-war structurally (Red and Blue render only their own custody picture, never
  ground truth — enforced at the session boundary, not by UI discipline);
- treats most effects as reversible (EW/cyber/proximity), reserving kinetic effects as a
  consequence-laden, confirmed, rare choice;
- is fully deterministic and replayable, so an exercise can be re-run, branched, and debriefed with
  byte-identical fidelity.

SpaceSim is the answer to that gap. Its scope is bounded deliberately
([`build-spec/01-context-and-scope.md`](../build-spec/01-context-and-scope.md) §2–3): moderate
orbital fidelity (Keplerian + J2, real TLEs via Skyfield), not a numerical-integration-grade
astrodynamics tool; PME training value, not classified mission rehearsal; cooperative LAN play, not
a hardened multi-tenant service (the LAN trust model in `CLAUDE.md`). (MSTR-001 §4.)

## 5. Success vision

The program succeeds when (MSTR-001 §5):

1. A White Cell facilitator with no programming background can stand up a vignette, run a 2-hour
   exercise, and conduct a doctrinally grounded AAR using only the in-app tools and
   `docs/training/`.
2. A new capability — e.g., a new sensor modality, a new effect, a new assessment metric — can be
   specified end-to-end in this documentation tree (Domain → Research → Feature Spec →
   Implementation Package) **before any code is written**, and a coding agent given only that
   trail produces a correct, tested implementation.
3. The research encyclopedia (`docs/research/` R1xx–R5xx, MSTR-007) is comprehensive enough that
   an agent never has to guess what "custody" or "OODA loop" or "weapons-quality track" means — the
   term resolves to a concept document with implementation implications, not just a definition.
4. Every Feature Specification and Implementation Package can be traced backward to the training
   or research need that motivated it, and forward to the code and tests that satisfy it (MSTR-005
   §4).

## 6. Non-goals

- **Not** a replacement for classified mission-planning or rehearsal tools.
- **Not** a numerically rigorous astrodynamics package — fidelity is "moderate, behind interfaces"
  by design (`Propagator`/`AccessProvider`/`EffectResolver` seams), so a higher-fidelity model can
  be substituted later without touching session/UI code.
- **Not** hardened against an adversarial LAN participant — the v1 trust model is cooperative (see
  `CLAUDE.md` "LAN trust model").
- **Not** a vehicle for generating code in the documentation-expansion effort — that phase produces
  **only** documentation (MSTR-006 §5: describe code changes, never write them in `master/`/
  `domains/`/`features/`/`implementations/`/`architecture/`).

(MSTR-001 §6.)

## 7. Relationship to the build spec

[`docs/build-spec/`](../build-spec/INDEX.md) remains **binding** for v1: "on any conflict, the
build spec wins." This master-document tree, and this ladder within it, does not supersede it — it
surrounds it with the domain/research/feature/implementation scaffolding the build spec assumed
but never formalized. Where this tree and the build spec appear to disagree, treat it as a signal
that either (a) the build spec needs a revision note (tracked as a `BS-0x-REV` item in
`ROADMAP.md`), or (b) the new document has mis-stated intent and should be corrected. (MSTR-001 §7.)

## Merge gate (closed)

- [x] Absorbed the relevant content of [`MSTR-001`](../master/MSTR-001-program-vision.md) into
  this document — §1–7 above restate MSTR-001 §1–7 in full, with citations back to the source
  section for each paragraph.
- [x] **Decision recorded:** `MSTR-001` **stays authoritative**; this document (`GDS-00`) is a
  **derivative restatement**, not a replacement. Rationale: `MSTR-001` is the root document of the
  entire `master/` tree (`Referenced By: MSTR-002…MSTR-007, all DOM-*, all FS-*`) — dozens of other
  documents cite it by ID. Demoting it to a pointer would break that referential structure for no
  benefit, since `GDS-00`'s content is, by design, identical in substance. `MSTR-001` should be
  updated only if the underlying vision changes; `GDS-00` exists so the design-synthesis ladder has
  a self-contained Vision level to build `GDS-01` on without a cross-tree jump, per the ladder's own
  "Merges from" convention (`architecture/INDEX.md` §1) — the merge step is satisfied by restatement
  with citation, not by surgery on the source document.
- [x] No content conflict was found between `MSTR-001` and any other vision-adjacent document
  (`build-spec/01-context-and-scope.md` §2–3, `CLAUDE.md` "What this is") during authoring — all
  three are consistent on mission, scope, and non-goals.

## Next

`GDS-01` (Concept of Operations) may now begin.
