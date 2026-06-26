# DOM-007 — Human Factors Framework

> **Document ID:** DOM-007
> **Version:** 1.0
> **Status:** 🚧 In progress
> **Dependencies:** MSTR-001, MSTR-003
> **Referenced By:** DOM-001, DOM-002, FS-106, FS-105
> **Produces:** UX/cognitive-load constraints consumed by every operator-console Feature Specification
> **Feature Mapping:** FS-105, FS-106
> **Related Topics:** [`docs/design/09-gui-principles.md`](../design/09-gui-principles.md),
> [`docs/AUDIT-2026-06-UI-TTC.md`](../AUDIT-2026-06-UI-TTC.md), R207 (cognitive bias), R206 (bounded rationality)

[↑ Docs index](../INDEX.md)

## 1. Purpose

States the human-factors constraints the operator console (and any future UI feature) must respect
so that the tool measures and trains *domain* judgment, not UI literacy or incidental cognitive
load the interface itself introduces. `docs/design/09-gui-principles.md` is the detailed UX design
document; this framework is the constraint set that document and every Feature Specification
touching the console must satisfy.

## 2. Scope

In scope: cognitive-load management, panel/layout ergonomics, accessibility, and the principle that
UI friction must be *intentional* (reflecting a real domain constraint) rather than *accidental*
(a UI design gap). Out of scope: visual design system specifics (design corpus), the pedagogical
rationale for plan-first interaction (MSTR-003 §3, which this framework assumes as given).

## 3. The central distinction: intentional friction vs. accidental friction

SpaceSim deliberately makes some things hard: you cannot act outside an access window, you cannot
see Red's ground truth, you must confirm before a kinetic effect. This is **intentional friction**
— it is the point (MSTR-003). The Jun 2026 UI/TT&C audit's findings (panel layout shuffling,
mismatched thumbnail/large-graph scaling, no valid-target dropdown) were **accidental friction** —
UI gaps that made the *tool* harder to use without teaching anything about the *domain*. DOM-007's
core rule: **every Feature Specification touching the console must identify which friction it
introduces is intentional (and justify it by domain/pedagogy) vs. incidental (and minimize it).**

## 4. Cognitive load principles

- **Belief-state legibility.** A cell's custody/confidence picture must be visually distinguishable
  from ground truth at a glance (color, iconography, explicit confidence indicators) — conflating
  "what I believe" and "what is true" in the UI undermines the entire fog-of-war pedagogy
  (MSTR-003 §4), independent of whether the backend correctly enforces the boundary.
- **State-of-health causality must be surfaced, not just displayed.** The audit's `in_eclipse`
  exposure fix (`AUDIT-2026-06-UI-TTC.md` §2) is the precedent: a falling SoC number with no visible
  cause reads as a bug to the operator, defeating the lesson (eclipse-driven drain is expected
  physics). Any new telemetry surface should ask "can the operator tell *why* this number is
  moving," not just "is the number accurate."
- **Consistency between summary and detail views.** The thumbnail-vs-large-graph fix (same audit,
  §3) generalizes: any UI element that previews a fuller view (a sparkline, a summary badge) must
  share data source, window, and scaling policy with the detail view it previews, or the operator
  will (correctly) distrust the preview.
- **Affordances should reflect actual permission, not just visual style.** The pre-disabled-button
  pattern (powered by `dry_run()`, MSTR-002 §5) is the model: don't let an operator discover "you
  can't do that" only after committing — surface it before the click whenever the engine can tell
  you in advance.

## 5. Layout and panel ergonomics

The panel manager (movable/scalable/closeable/openable, `panels.js`) exists because a fixed grid
layout where one panel's height could "shuffle the flow of everything else" is accidental friction
by §3's definition — operators were fighting the console layout instead of the domain. DOM-007's
rule for future panels: every new panel must be a first-class citizen of the panel manager (close,
float, resize, reset-to-dock) from the start, not bolted on as a fixed grid cell that later needs
retrofitting.

## 6. Accessibility

`docs/build-spec/07-operator-console.md` already specifies accessibility requirements for the v1
console. DOM-007 elevates this to a standing constraint for *every* future Feature Specification
touching the UI: keyboard navigation (the existing `j/k/c/g` pattern should be extended
consistently, not forked per-feature with different bindings) and presentation-mode compatibility
(classroom/projector use) are not optional polish — they are part of what makes the tool usable in
its actual PME deployment context (a room of trainees, a shared display, possibly a facilitator
running it without a mouse-heavy workflow).

## 7. What this framework expects from FS-105 / FS-106

Any Feature Specification touching the operator console (FS-105 Spacecraft Operations, FS-106
White Cell Dashboard) must include a short "Human Factors" consideration (even if folded into
Non-Functional Requirements) addressing: which friction is intentional (§3), how belief-vs-truth
stays legible (§4), and whether new panels follow the panel-manager contract (§5).

## 8. Related topics

R207 (cognitive bias — relevant to why belief-state legibility matters: an operator under cognitive
load is more likely to default to assuming their belief is ground truth), R206 (bounded
rationality — the realistic baseline this framework designs for, not idealized attention/memory),
DOM-002 (assessment dimensions like "belief-truth divergence" depend on the operator being able to
see and act on their actual belief state, which is what this framework protects).
