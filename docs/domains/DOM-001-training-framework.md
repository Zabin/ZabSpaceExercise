# DOM-001 — Training Framework

> **Document ID:** DOM-001
> **Version:** 1.0
> **Status:** 🚧 In progress (framework stable; full FS coverage pending Phase 4)
> **Dependencies:** MSTR-001, MSTR-003
> **Referenced By:** DOM-002, DOM-003, DOM-007, DOM-009, FS-101, FS-106, FS-107, FS-201
> **Produces:** FS-101 Mission Planning, FS-105 Spacecraft Operations, FS-107 After Action Review, FS-2xx training-progression specs
> **Feature Mapping:** FS-101, FS-105, FS-106, FS-107, FS-201
> **Related Topics:** [`docs/training/INDEX.md`](../training/INDEX.md), [`docs/vignettes/00-vignette-framework.md`](../vignettes/00-vignette-framework.md),
> R208 (OODA loops), R501 (human-AI teaming)

[↑ Docs index](../INDEX.md)

## 1. Purpose

Defines how SpaceSim teaches: the objective taxonomy, the skill-progression model across the
19-vignette library, and the design rules a new vignette or training feature must follow to
actually deliver on MSTR-003's pedagogical claims rather than merely resembling a training tool.

## 2. Scope

In scope: training-objective taxonomy, vignette difficulty progression, the tutorial-script
mechanism, the mission-brief mechanism, onboarding (training-basics vignette). Out of scope:
*measuring* whether training worked (DOM-002, Assessment), *who* runs the session and how
(DOM-003, White Cell), and the doctrinal content being taught (DOM-009, research R100/R300).

## 3. Training-objective taxonomy

Every vignette's per-cell `intro_brief` states a mission and success criteria; DOM-001 normalizes
these into four objective classes so that progression and assessment (DOM-002) can be reasoned
about systematically rather than per-vignette ad hoc:

| Class | Description | Example | Primary mechanic exercised |
|---|---|---|---|
| **Mechanical** | Operate the tool correctly: issue a valid order inside a window, read telemetry. | Training-basics tutorial steps | Plan-execute loop (MSTR-003 §3) |
| **Tactical** | Achieve a stated in-exercise objective against a single, bounded threat picture. | Vignette 1 (LEO ISR denial) | Custody-building, access-window planning |
| **Operational** | Manage a fleet/constellation under competing demands and resource constraints (Δv, power, sensor tasking contention). | Constellation/mission-set vignettes | Resource economy, tasking deconfliction |
| **Judgment** | Decide under genuine ambiguity with consequential, sometimes irreversible options. | Red COA vignettes, capstone Vignette 8 | Escalation/ROE reasoning, kinetic-confirm gate |

A vignette should declare, in its `intro_brief` or a future `training_objectives:` schema field
(see FS-101 candidate scope), which class(es) it primarily exercises — this is what lets DOM-002
build assessment rubrics keyed to objective class rather than per-vignette bespoke criteria.

## 4. Skill-progression model

The 19-vignette library is not flat; it has an implicit progression this framework makes explicit:

1. **Onboarding** (training-basics) — mechanical objectives only, ≥5 tutorial steps per cell,
   reversible effects only.
2. **Canonical 8** — tactical objectives, increasing custody/window complexity, still mostly
   reversible effects with at least one kinetic-confirm-gated option introduced by the later
   numbered vignettes.
3. **Mission-set (3) and Red COA (5)** — operational objectives: multi-asset fleets, Δv economy,
   sensor contention, doctrinally-flavored Red behavior presets.
4. **Learning (1) and Novel (1)** — designed for judgment objectives and for exercising the
   AAR/branch-compare capability itself.
5. **Capstone Vignette 8** — multi-domain (per `docs/vignettes/08-multi-domain-taiwan.md`),
   integrates all four objective classes at once; the terminal exercise of the progression.

**Design rule:** a new vignette should be assigned a slot in this progression (or explicitly
flagged as a side-branch, e.g. a one-off classroom demo) rather than added without regard to
difficulty ordering — otherwise the progression degrades into an unordered pile and DOM-002 has no
stable baseline to assess against.

## 5. The tutorial-script and mission-brief mechanisms

Two existing mechanisms carry the bulk of in-app instructional design and must be preserved/extended
by any new training feature, not bypassed:

- **`tutorial:` block** (the 8 canonical + training-basics vignettes) — a per-cell, move-by-move
  script of how to complete objectives, surfaced via `GET /api/vignettes/{id}/tutorial` and the
  in-UI Tutorial panel, verified mechanically by `test_vignette_tutorials.py`. Any new vignette in
  this tier of the progression should carry one.
- **`intro_brief:` block** (all 19 vignettes) — situation/mission/forces/threat/deadline/ROE/success
  criteria/tool tips, surfaced via the Mission brief panel, combined live with ROE chips and
  objective-deadline countdowns. This is the primary onramp into a session and should be treated as
  load-bearing UX, not flavor text.

## 6. Coaching notes as just-in-time instruction

`Vignette.coaching` (`{at_sim_t?, cell, title, body}`) lets a vignette author inject instructional
content at a specific simulated moment — e.g., right before a contested access window opens. This
is the mechanism for teaching *during* play without breaking the plan-execute loop (MSTR-003 §3):
coaching notes inform, they never act on the cell's behalf.

## 7. What this framework expects from new Feature Specifications

Any Feature Specification that touches training delivery (FS-101 Mission Planning, FS-105
Spacecraft Operations, FS-106 White Cell Dashboard, FS-107 AAR) must state, in its "Educational
Value" section, which objective class(es) (§3) it serves and where in the progression (§4) it
applies. A feature with no stated educational value is a signal it may belong in a different
domain (e.g., pure infrastructure belongs under DOM-006/DOM-008, not DOM-001).

## 8. Open work

- Formalize `training_objectives:` as an explicit vignette schema field (currently implicit in
  `intro_brief` prose) — candidate scope item for FS-101 / a vignette-schema Implementation Package.
- Cross-check every one of the 19 vignettes against the progression model in §4 and record gaps in
  `ROADMAP.md`.

## 9. Related topics

R208 (OODA loops, the theoretical basis for §3's "judgment" objective class), R501 (human-AI
teaming, relevant to how a future AI tutor/coaching-note generator would plug into §6), DOM-002
(how objective classes become measurable), DOM-009 (how doctrine becomes a vignette's threat
picture and ROE).
