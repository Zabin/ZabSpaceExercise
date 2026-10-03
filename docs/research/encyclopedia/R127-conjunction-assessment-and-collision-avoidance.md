# R127 — Conjunction Assessment and Collision Avoidance Operations

> **Document ID:** R127
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R102](R102-space-domain-awareness.md), [R105](R105-custody-theory.md), [R112](R112-propulsion-and-maneuver-planning.md), [R101](R101-orbital-mechanics-for-operations.md) (v1.1, the RIC/LVLH transform grounding)
> **Referenced By:** FS-105, [R131](R131-space-environment-and-space-weather-operations.md), [R109](R109-sensor-operations.md) (v1.3, cross-references this topic's RIC-display work)
> **Produces:** implementation constraints for [`engine/conjunction.py`](../../../spacesim/engine/conjunction.py) and the `prop.collision_avoid` verb in [`engine/buscommands.py`](../../../spacesim/engine/buscommands.py); (v1.1) RIC/RTN-frame relative-motion display grounding for `BL-0107`/`BL-0108`, consumed by [`session/ephemeris.py`](../../../spacesim/session/ephemeris.py)'s existing `to_ric()`
> **Feature Mapping:** FS-105 (Spacecraft Operations); (v1.1) `FEAT-8200` ([`docs/feature-planning/03-feature-catalog.md`](../../feature-planning/03-feature-catalog.md))
> **Related Topics:** [R102](R102-space-domain-awareness.md) (SDA — the tracking custody feeds conjunction screening), [R105](R105-custody-theory.md)
> (Custody Theory — confidence the conjunction prediction is itself subject to), [R112](R112-propulsion-and-maneuver-planning.md) (Propulsion and Maneuver
> Planning — the Δv the avoidance maneuver consumes), [R101](R101-orbital-mechanics-for-operations.md) (RIC/LVLH transform math, v1.1), [R109](R109-sensor-operations.md) (CATS/illumination phase angle shown alongside the same RIC view, v1.1)
> **Last Reviewed:** 2026-10-03
> **Primary Sources Consulted:** 5 (2 for the v1.0 content; 3 new for v1.1's RIC-display grounding)

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

### RIC/RTN-frame relative-motion display as the standard operator presentation (v1.1, `BL-0107`/`BL-0108`)

**Real conjunction/RPO analysis is never presented to an operator in raw ECI coordinates — it is
presented relative to one object, in that object's own rotating RIC (Radial/In-track/Cross-track,
equivalently RTN — Radial/Transverse/Normal) frame.** This is not a cosmetic display choice: the
CCSDS Conjunction Data Message standard — the real, operationally-exchanged data product
`predict_conjunctions` is a coarse stand-in for (§3 above) — defines its relative state vector
(`RELATIVE_POSITION_R/T/N`, `RELATIVE_VELOCITY_R/T/N`) and covariance *natively* in the RTN frame of
the primary object, with screening-volume geometry likewise expressed in RTN or the closely related
TVN (Transverse/Velocity/Normal) frame
([CCSDS 508.0-B-1, *Conjunction Data Message*, Recommended Standard](https://ccsds.org/Pubs/508x0b1e2c2.pdf))
([Wayback](https://web.archive.org/web/2026/https://ccsds.org/Pubs/508x0b1e2c2.pdf)). NASA's own
CARA program (§3 above) builds its operator-facing conjunction visualizations directly on this
frame: the real "2D conjunction plane" display used by CARA analysts and mission operators projects
the encounter onto the plane normal to the relative-velocity vector, with the relative-position
vector and out-of-plane component as the two displayed axes — a rotating-frame, one-object-relative
presentation, not an ECI one
([White & Baars, "Methods \[for\] Visualizing Conjunctions," NASA Technical Reports Server,
2025](https://ntrs.nasa.gov/api/citations/20250006946/downloads/White_2025_Methods_Visualizing_Conjunctions.pdf))
([Wayback](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20250006946/downloads/White_2025_Methods_Visualizing_Conjunctions.pdf)).
Commercial mission-planning tooling makes the operator-selectable-origin convention explicit: a
widely-used orbital-analysis package's relative-motion display defines the RIC frame's origin at
the analyst-chosen "chief" object's center of mass, describing every other ("deputy") object's
position/velocity in radial/in-track/cross-track components relative to that chosen chief — the
chief selection is an ordinary user interaction, not a fixed, hard-coded reference
([AGI, "RIC Coordinates"](https://help.agi.com/stk/Subsystems/dataProviders/Content/html/dataProviders/RIC_Coordinates.htm))
([Wayback](https://web.archive.org/web/2026/https://help.agi.com/stk/Subsystems/dataProviders/Content/html/dataProviders/RIC_Coordinates.htm)).
This closes `docs/pipeline/backlog.md` `BL-0108`'s research gap: RIC-frame relative-motion display,
with an operator-selectable origin/chief object, is a real, standard, operationally load-bearing
console convention — not a novel UI idea this project would be inventing from scratch. It directly
grounds `FR-8210` (`FEAT-8200`, [`docs/feature-planning/03-feature-catalog.md`](../../feature-planning/03-feature-catalog.md)),
the live, operator-selectable RIC-frame view `BL-0107` requested, and reuses the same physical frame
`FR-7410`/`FR-7420`/`FR-7430`'s one-shot CSV/CCSDS-OEM export already computes via
`engine/maneuver.py::lvlh_frame`/`session/ephemeris.py::to_ric()` — this topic grounds the *display*
concept; [R101](R101-orbital-mechanics-for-operations.md)/[R112](R112-propulsion-and-maneuver-planning.md)
already ground the *transform math* itself (RIC/RSW as an LVLH frame instance), and neither R101 nor
R112 claims to cover the display/console convention, which is this subsection's own, distinct
contribution.

### Sources (RIC/RTN-frame relative-motion display, v1.1)

- *CCSDS 508.0-B-1, "Conjunction Data Message," Recommended Standard, Issue 1, June 2013* —
  [live](https://ccsds.org/Pubs/508x0b1e2c2.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://ccsds.org/Pubs/508x0b1e2c2.pdf)
  · accessed 2026-10-03.
- *White, E.H. & Baars, L.G., "Methods [for] Visualizing Conjunctions," NASA Technical Reports
  Server, 2025* — [live](https://ntrs.nasa.gov/api/citations/20250006946/downloads/White_2025_Methods_Visualizing_Conjunctions.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20250006946/downloads/White_2025_Methods_Visualizing_Conjunctions.pdf)
  · accessed 2026-10-03.
- *AGI, "RIC Coordinates" (STK help documentation)* —
  [live](https://help.agi.com/stk/Subsystems/dataProviders/Content/html/dataProviders/RIC_Coordinates.htm)
  · [snapshot](https://web.archive.org/web/2026/https://help.agi.com/stk/Subsystems/dataProviders/Content/html/dataProviders/RIC_Coordinates.htm)
  · accessed 2026-10-03.

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
- **A live, operator-selectable RIC-frame view (`FR-8210`) should present relative motion exactly
  the way real CDM/CARA tooling does — relative to one chosen origin object, in that object's own
  RIC/RTN basis, not ECI** — reuse `session/ephemeris.py::to_ric()`/`engine/maneuver.py::lvlh_frame`
  directly rather than a second RIC-transform implementation; the "chosen origin" is an ordinary
  live UI selection (mirroring AGI STK's chief-object pick, above), re-rendered on every clock
  advance, not a one-time, session-start-only configuration choice.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any conjunction-fidelity increase or new
collision-avoidance UI must preserve the predictor/operator-decision split this topic documents.
(v1.1) `FEAT-8200` ([`docs/feature-planning/03-feature-catalog.md`](../../feature-planning/03-feature-catalog.md))
— the live, operator-selectable RIC-frame relative-motion view (`FR-8210`, `BL-0107`) — is also a
direct consumer, grounded by this topic's own new RIC/RTN-frame-display subsection above; it closes
the `BL-0108` research gap that Feature's `06-feature-specification` pass is blocked on.

## 7. Related Topics

[R102](R102-space-domain-awareness.md) (the SDA/tracking chain conjunction screening depends on), [R105](R105-custody-theory.md) (the confidence
model a higher-fidelity Pc estimate would need to draw on), [R112](R112-propulsion-and-maneuver-planning.md) (the Δv economy the avoidance
maneuver itself spends), [R101](R101-orbital-mechanics-for-operations.md) (the RIC/LVLH transform
math this topic's own RIC-display subsection presents operationally, v1.1), [R109](R109-sensor-operations.md)
(Sensor Operations — its own §3.11, v1.3, grounds the CATS/illumination-phase-angle readout the
same `FEAT-8200` RIC view also displays).
