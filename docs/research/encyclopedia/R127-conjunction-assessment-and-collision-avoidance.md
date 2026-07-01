# R127 — Conjunction Assessment and Collision Avoidance Operations

> **Document ID:** R127
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R102](R102-space-domain-awareness.md), [R105](R105-custody-theory.md), [R112](R112-propulsion-and-maneuver-planning.md)
> **Referenced By:** FS-105, [R131](R131-space-environment-and-space-weather-operations.md)
> **Produces:** implementation constraints for [`engine/conjunction.py`](../../../spacesim/engine/conjunction.py) and the `prop.collision_avoid` verb in [`engine/buscommands.py`](../../../spacesim/engine/buscommands.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R102](R102-space-domain-awareness.md) (SDA — the tracking custody feeds conjunction screening), [R105](R105-custody-theory.md)
> (Custody Theory — confidence the conjunction prediction is itself subject to), [R112](R112-propulsion-and-maneuver-planning.md) (Propulsion and Maneuver
> Planning — the Δv the avoidance maneuver consumes)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 2

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`engine/conjunction.py`'s `predict_conjunctions` (a pure, advisory close-approach predictor that
unlocks the `prop.collision_avoid` catalog verb) is `spacesim`'s deliberately coarse stand-in for a
real, mature operational discipline: conjunction assessment and collision avoidance (CA/COLA). This
topic gives the implementer the real screening-and-decision process so a future fidelity increase
(probability-of-collision scoring, a real CDM-like data product, a maneuver-decision threshold)
extends the model along the real process's actual structure.

## 2. Scope

Covers: the real conjunction-screening pipeline (catalog screening, Conjunction Data Messages,
probability-of-collision thresholds, owner/operator maneuver decisions) and how
`predict_conjunctions`'s range-threshold model is a coarse advisory simplification of it. Does
**not** cover: the custody/tracking confidence model conjunction screening depends on
([R102](R102-space-domain-awareness.md)/[R105](R105-custody-theory.md)), or the maneuver mechanics the avoidance burn itself uses ([R112](R112-propulsion-and-maneuver-planning.md)).

## 3. Concepts

**Real conjunction screening is a standing, scheduled process, not an on-demand query.** The U.S.
Space Force's 18th Space Defense Squadron (18 SDS) "screens the catalogue daily, producing
Conjunction Data Messages (CDMs) for close approaches," with on-orbit conjunction assessment "driven
by screenings conducted three times a day"
([U.S. Space Force 18th Space Defense Squadron conjunction-screening practice, as summarized by
multiple NASA CARA program sources](https://www.nasa.gov/cara/)
([Wayback](https://web.archive.org/web/2026/https://www.nasa.gov/cara/))) — the real-world
precedent for treating conjunction prediction as continuous background screening rather than a
one-shot check; `predict_conjunctions`'s `horizon_s`/`step_s` sampling window is a coarse, on-demand
version of the same idea, intended to be called periodically rather than once.

**NASA's CARA process has three named participants with distinct roles.** The Conjunction
Assessment Risk Analysis (CARA) operations process involves "CARA Orbital Safety Analysts (OSAs)
resident at the 18th Space Control Squadron... operations facility," the NASA CARA team, and the
"mission Owner/Operator (O/O)" who ultimately makes the maneuver decision
([NASA CARA program, *Conjunction Assessment Risk Analysis overview*](https://www.nasa.gov/cara/)
([Wayback](https://web.archive.org/web/2026/https://www.nasa.gov/cara/))) — directly analogous to
`spacesim`'s split between a pure predictor (`predict_conjunctions`, the OSA/CARA-team role: produce
the warning) and the operator who decides whether to issue `prop.collision_avoid` (the O/O role:
decide whether to maneuver) — the engine never auto-maneuvers on a conjunction warning, mirroring
the real division of "who screens" from "who decides."

**A probability-of-collision threshold, not raw miss distance alone, drives the real maneuver
decision.** Real CA practice maneuvers when probability of collision exceeds an agency-set
threshold — "typically 1 in 10,000 for crewed vehicles like the ISS," with uncrewed-mission
thresholds commonly in the 10⁻⁴-10⁻⁵ range depending on agency guidelines
([Orbital Radar / aggregated CA-practice summary, citing 18 SDS/CARA threshold conventions](https://orbitalradar.com/what-is-a-conjunction)
([Wayback](https://web.archive.org/web/2026/https://orbitalradar.com/what-is-a-conjunction))) —
`predict_conjunctions`'s flat `threshold_km=25.0` range gate is a simplified stand-in for this real
probability-weighted decision (which also factors combined covariance/uncertainty, not just miss
distance); a higher-fidelity version should compute an actual Pc, not just tighten the range
threshold.

**Conjunction warnings flow into the same world-state mechanism as any other White Cell inject, not
a parallel alert channel.** Per the `conjunction.py` module docstring, operators "preload
`world.entities["conjunctions"]` (or fire a `conjunction_warning` inject)" to surface a predicted
close approach, which then "unlocks the `prop.collision_avoid` catalog verb on the at-risk asset" —
consistent with how every other White-Cell-curated anomaly (`gs_outage`, `geomagnetic_storm`) is
delivered: as world-state/inject content the operator must notice and act on, not an engine-forced
event.

### Sources

- *NASA CARA Program, Conjunction Assessment Risk Analysis overview* — [live](https://www.nasa.gov/cara/)
  · [snapshot](https://web.archive.org/web/2026/https://www.nasa.gov/cara/)
  · accessed 2026-06-27.
- *Orbital Radar, What Is a Satellite Conjunction (Near Miss)?* — [live](https://orbitalradar.com/what-is-a-conjunction)
  · [snapshot](https://web.archive.org/web/2026/https://orbitalradar.com/what-is-a-conjunction)
  · accessed 2026-06-27.

## 4. Operational Context

Real conjunction assessment is one of the most mature, continuously-running operational disciplines
in spaceflight: a dedicated military squadron screens the entire tracked catalog multiple times
daily, a NASA-side analysis team filters and refines those screenings for NASA assets, and each
mission's own operators retain final maneuver authority informed by a probability-of-collision
score rather than raw distance. `spacesim`'s coarse range-threshold predictor and operator-decided
`prop.collision_avoid` verb compress this real three-party, probability-driven pipeline into a
single pure function plus an operator decision, preserving the most pedagogically important real
property — the warning informs, the operator decides — while deliberately not modeling covariance-
based Pc.

## 5. Implementation Guidance

- **A higher-fidelity conjunction model should replace the `threshold_km` range gate with an actual
  probability-of-collision estimate** (combining miss distance and position-uncertainty/covariance),
  not just tighten the existing distance threshold — a real Pc and a tight range gate are not the
  same fidelity increase.
- **Keep conjunction prediction a pure, non-mutating function** (as `predict_conjunctions` already
  is, explicitly modeled on `AccessProvider`'s pure-predictor pattern) — a future fidelity bump
  should preserve this, not fold collision prediction into a stateful handler.
- **Never have the engine auto-maneuver on a predicted conjunction** — preserve the real CARA-style
  separation between the screening/warning role and the owner/operator's maneuver decision; the
  operator must still issue `prop.collision_avoid` explicitly.
- **A new conjunction-severity tier (e.g. distinguishing "monitor" from "maneuver recommended")
  should be threshold bands on the same predictor output**, not a second parallel prediction
  function — mirrors how real CA practice escalates by Pc band rather than switching processes.
- **Surface new conjunction data the same way the existing inject/world-entities mechanism does**
  (`world.entities["conjunctions"]` or a named inject template) — don't add a separate alert
  pipeline that bypasses the inject/world-state pattern every other White Cell anomaly uses.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any conjunction-fidelity increase or new
collision-avoidance UI must preserve the predictor/operator-decision split this topic documents.

## 7. Related Topics

[R102](R102-space-domain-awareness.md) (the SDA/tracking chain conjunction screening depends on), [R105](R105-custody-theory.md) (the confidence
model a higher-fidelity Pc estimate would need to draw on), [R112](R112-propulsion-and-maneuver-planning.md) (the Δv economy the avoidance
maneuver itself spends).
