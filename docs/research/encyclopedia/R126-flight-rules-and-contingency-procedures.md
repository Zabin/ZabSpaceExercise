# R126 — Flight Rules and Contingency Procedures

> **Document ID:** R126
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](R103-satellite-command-and-control.md), [R122](R122-safe-mode-recovery.md)
> **Referenced By:** FS-105
> **Produces:** implementation constraints for the ROE dict in [`engine/orders.py`](../../../spacesim/engine/orders.py) (`OrderSystem._validate`) and [`engine/recovery.py`](../../../spacesim/engine/recovery.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R103](R103-satellite-command-and-control.md) (Satellite C2 — the order pipeline ROE gates), [R122](R122-safe-mode-recovery.md)
> (Safe-Mode Recovery — the scripted-procedure-chain pattern this topic grounds)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 2

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`spacesim`'s `OrderSystem.roe` dict (`kinetic_authorized`/`cyber_authorized` booleans gating
`engage`/`cyber` orders) and `RecoverySystem`'s confirm→diagnose→patch→re-enable step chain
([R122](R122-safe-mode-recovery.md)) are both small, code-level stand-ins for a real-world document class: the flight
rules and contingency-procedure books real mission operations teams write and follow. This topic
gives the implementer the real shape of that document class so a future ROE expansion (more than
two booleans) or a new scripted procedure follows real flight-rule structure rather than an
invented format.

## 2. Scope

Covers: the real flight-rule condition→action format and its role as operator-facing constraint
documentation, and how it grounds both ROE-as-authorization-gate and procedure-as-scripted-chain.
Does **not** cover: the ROE check site itself ([R103](R103-satellite-command-and-control.md)), or the recovery chain's actual step
mechanics ([R122](R122-safe-mode-recovery.md)).

## 3. Concepts

**Flight rules are written as condition/phase pairs, not free narrative.** NASA flight mission
rules documents carry "a condition/malfunction column that defines the failure, and a phase column
that identifies the time interval in which the condition/malfunction occurs"
([NASA, *Final Flight Mission Rules*, Apollo 10, 1969-04-15](https://www.nasa.gov/wp-content/uploads/static/history/afj/ap10fj/pdf/a10-mission-rules-19690415.pdf)
([Wayback](https://web.archive.org/web/2026/https://www.nasa.gov/wp-content/uploads/static/history/afj/ap10fj/pdf/a10-mission-rules-19690415.pdf))),
derived from "analysis of mission equipment configuration, systems operations and constraints,
flight crew procedures, and mission objectives"
([NASA, *The Role of Flight Mission Rules in Spacecraft Missions*, NTRS 19750002893](https://ntrs.nasa.gov/api/citations/19750002893/downloads/19750002893.pdf)
([Wayback](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/19750002893/downloads/19750002893.pdf))) —
this condition→constrained-action shape is the real-world precedent for `OrderSystem`'s
`roe.get("kinetic_authorized")`/`roe.get("cyber_authorized")` checks: each is a degenerate
one-line flight rule ("if kinetic engagement is attempted and not authorized, reject"), not an
arbitrary game-balance toggle.

**Flight rules constrain real-time decisions; they are not rigid law.** Flight rules "aren't
ironclad laws that incur civil punishment if broken, or rote checklists that must be followed like
some tax form's flow chart. Rather, they provide flexible guidance that allows mission controllers
to make decisions based on real-time conditions," and flight controllers "supervise the application
of mission rules... to the conduct of the flight" (NTRS 19750002893, *op. cit.*) — the real-world
grounding for treating ROE as a pre-flight-authored *gate* an operator's order is checked against
at issue-time (`_validate`), rather than the engine making the kinetic/cyber go/no-go judgment call
itself; the rule is set in advance, the operator's order either satisfies it or doesn't.

**Contingency procedures are a separate document class: scripted multi-step responses to a
specific anomaly, not a single rule.** Flight rule documents pair with procedure books that script
out the specific sequence of actions a controller executes once a rule's condition is met
(*op. cit.* sources; same Apollo-era and shuttle-era operations literature) — this is the real-world
precedent for `RecoverySystem`'s fixed confirm→diagnose→patch→re-enable step sequence
([R122](R122-safe-mode-recovery.md)): once a safe-mode condition is detected, the response is a scripted procedure
with a defined step order, not a fresh judgment call each time.

**A documented rule set survives the controllers who wrote it.** Flight rules are produced ahead of
the mission by engineering analysis, then "applied" by whichever controller is on console at the
time the condition arises (*op. cit.*) — directly analogous to a vignette's `roe_note`/`roe` dict
being authored by White Cell before the exercise starts, then enforced uniformly by `OrderSystem`
regardless of which human is operating Red or Blue at the moment a kinetic order is attempted.

### Sources

- *NASA, Final Flight Mission Rules, Apollo 10 (1969-04-15)* —
  [live](https://www.nasa.gov/wp-content/uploads/static/history/afj/ap10fj/pdf/a10-mission-rules-19690415.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.nasa.gov/wp-content/uploads/static/history/afj/ap10fj/pdf/a10-mission-rules-19690415.pdf)
  · accessed 2026-06-27.
- *NASA, The Role of Flight Mission Rules in Spacecraft Missions, NTRS 19750002893* —
  [live](https://ntrs.nasa.gov/api/citations/19750002893/downloads/19750002893.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/19750002893/downloads/19750002893.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

Every crewed and most uncrewed NASA missions since Apollo have flown with a written flight-rule
book and contingency-procedure set prepared before launch — these documents exist precisely because
real-time, in-the-moment authorization decisions for high-consequence actions (a kinetic-equivalent
abort, an anomaly response) should be pre-negotiated and written down, not improvised under
pressure. `spacesim`'s ROE dict and `RecoverySystem` step chain are both compressed, code-level
versions of that same principle: decide the rule in advance (a vignette's ROE/procedure design),
then enforce it mechanically and consistently during the exercise.

## 5. Implementation Guidance

- **A new ROE-gated action type should follow the existing `roe.get("<action>_authorized", False)`
  pattern in `OrderSystem._validate`**, with a vignette-settable boolean — this keeps ROE as
  pre-authored, fail-closed flight-rule-style gates rather than introducing a new in-engine judgment
  call.
- **If ROE needs to grow beyond a boolean** (e.g. authorized only against certain target classes or
  during certain mission phases, mirroring the real condition/phase column structure), extend the
  `roe` dict schema explicitly and document the new fields in the vignette schema — don't bury
  phase/target conditioning inside `_validate`'s control flow without a corresponding documented
  field.
- **A new scripted multi-step response to a detected condition belongs in a `RecoverySystem`-style
  step chain, not a single-shot handler** — preserve the real flight-rule/procedure-book separation:
  the *authorization gate* (ROE) and the *scripted response* (procedure chain) are different
  documents in real ops and should stay different code paths here too.
- **ROE values are vignette data (White Cell's pre-authored rule book), never operator-overridable
  at runtime** — consistent with the real principle that flight rules are set before the mission,
  not renegotiated mid-flight by whoever is on console.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any new ROE-gated action or contingency
procedure must extend the existing `OrderSystem`/`RecoverySystem` patterns this topic grounds.

## 7. Related Topics

[R103](R103-satellite-command-and-control.md) (the order-validation pipeline ROE gates), [R122](R122-safe-mode-recovery.md) (the scripted multi-pass
procedure chain this topic's contingency-procedure concept grounds).
