# FS-106 — White Cell Dashboard

> **Document ID:** FS-106
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md), [DOM-001](../domains/DOM-001-training-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md)
> **Referenced By:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md)
> **Produces:** the facilitation surface [FS-108](FS-108-inject-authoring.md) (candidate) would extend
> **Feature Mapping:** FS-106 (this document)
> **Related Topics:** [FS-107](FS-107-after-action-review.md) (White-only AAR controls), [DOM-002](../domains/DOM-002-assessment-framework.md) §6 (facilitator-rubric
> assessment mode, hosted here)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## 1. Purpose

The White Cell Dashboard is the facilitator's console: unrestricted god-view across both cells,
inject authoring/scheduling, clock/pacing authority, and session administration. Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §1,
it must trace back to White Cell's role as instructional designer ([`MSTR-003`](../master/MSTR-003-educational-philosophy.md) §7), not a
neutral referee — every capability in this spec exists to let a facilitator *shape* the learning
experience in real time, not merely observe it.

## 2. Scope

In scope: god-view rendering (both cells' belief + ground truth simultaneously), the inject
build/schedule panel, clock pause/resume and AAR-adjacent rewind/undo/branch controls, session
discovery/save-resume/pop-out layout management, and Red-doctrine-preset selection/hand-tuning. Out
of scope: the AAR replay/scrub instrument itself ([FS-107](FS-107-after-action-review.md), though White-only controls for it are
hosted in this dashboard), and the content of specific inject templates (vignette/scenario content).

## 3. Capability requirements

- **Must expose unrestricted god-view without granting Red/Blue any new ground-truth access.** Per
  [DOM-003](../domains/DOM-003-white-cell-framework.md) §3, any new god-view-only capability is acceptable; any capability that would let
  Red/Blue access ground truth through this dashboard is a fog-of-war violation regardless of
  framing.
- **Inject authoring must work against the existing `inject_library.yaml` mechanism, not duplicate
  it.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §4, the dashboard's job is exposing the five reusable templates with an
  editable-JSON + Now/+seconds/absolute-UTC scheduler; the underlying inject *execution* path is
  engine-side and out of this spec's scope to re-implement.
- **Clock/pacing controls must remain a single point of authority.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §5, pause/
  resume and rewind/undo/branch must stay White-only and apply identically to every connected
  client — no per-tab pacing negotiation.
- **Session administration (save/resume, discovery, pop-out layout) is a facilitation concern, not
  a generic platform concern.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §6, design questions here ("can I resume a
  multi-week course's exercise," "can I spread the console across monitors for a classroom") should
  be evaluated against facilitation needs, not treated as infrastructure plumbing.
- **Red-doctrine-preset visibility and control is a tooling requirement, not optional.** Per
  [DOM-003](../domains/DOM-003-white-cell-framework.md) §7, the facilitator needs visibility into which preset drives Red and the ability to
  switch or hand-tune it mid-exercise for pacing reasons — an unconvincing or passive Red undermines
  the training per [R308](../research/encyclopedia/R308-red-teaming-methodology.md).
- **Mission-set/campaign sequencing must be visible to the facilitator.** Per [R301](../research/encyclopedia/R301-campaign-design.md) §5, this
  dashboard is the nearest existing consumer of campaign-design sequencing — a facilitator running a
  mission-set vignette needs to see the sequence, even though full campaign-progression tracking is
  out of this spec's scope.
- **The assess beat must be visible from White's cross-cell vantage point.** Per [R106](../research/encyclopedia/R106-mission-operations.md) §5,
  unlike [FS-105](FS-105-spacecraft-operations.md)'s per-cell plan/task beats, this dashboard's distinct contribution is the assess
  beat viewed across both cells at once.

## 4. Non-goals

- This spec does not include an inject-authoring *UX upgrade* (templated parameter forms, preview-
  before-schedule, library browser/search) — that is [FS-108](FS-108-inject-authoring.md), a separate, currently-candidate
  (not authorized) Feature Specification per [DOM-003](../domains/DOM-003-white-cell-framework.md) §9.
- This spec does not include the AAR replay/scrub mechanics themselves — only the White-only control
  surface for invoking them ([FS-107](FS-107-after-action-review.md) owns the instrument).
- Composing multiple inject templates into a pre-scripted sequence ahead of a session is explicitly
  named as not currently possible ([DOM-003](../domains/DOM-003-white-cell-framework.md) §9) and is out of this spec's scope.

## 5. Required authority-tier statement (DOM-003 §8)

Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §8: this spec touches all four authority tiers — visibility (§3 god-view),
inject (§4), clock (§5), and administration (§6) — and confirms it grants Red/Blue no new god-view
access; every capability described here is additive to White Cell's existing authority, not a
back door into either cell's fog-of-war boundary.

## 6. Related Topics

[DOM-003](../domains/DOM-003-white-cell-framework.md) (owning framework), [R301](../research/encyclopedia/R301-campaign-design.md) (campaign sequencing), [R307](../research/encyclopedia/R307-wargaming-theory.md) (wargaming validity), [R308](../research/encyclopedia/R308-red-teaming-methodology.md) (red-team
realism), [FS-107](FS-107-after-action-review.md) (AAR instrument this dashboard's controls invoke), [FS-108](FS-108-inject-authoring.md) (candidate inject-authoring
UX extension).
