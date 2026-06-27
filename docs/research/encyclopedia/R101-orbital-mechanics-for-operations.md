# R101 — Orbital Mechanics for Operations and Implementation

> **Document ID:** R101
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** none (foundational)
> **Referenced By:** [R102](R102-space-domain-awareness.md), [R103](R103-satellite-command-and-control.md), [R107](R107-ground-segment-operations.md), [R108](R108-constellation-operations.md), [R109](R109-sensor-operations.md), [R110](R110-communications.md), [R112](R112-propulsion-and-maneuver-planning.md), [R120](R120-access-window-and-geometry-planning.md), FS-101, FS-105
> **Produces:** implementation constraints for [`engine/orbit.py`](../../../spacesim/engine/orbit.py), [`engine/propagator.py`](../../../spacesim/engine/propagator.py), [`engine/access.py`](../../../spacesim/engine/access.py)
> **Feature Mapping:** FS-101 (Mission Planning), FS-105 (Spacecraft Operations)
> **Related Topics:** [`docs/research/04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md) (full derivations),
> [`docs/research/04a-propagator-fidelity.md`](../04a-propagator-fidelity.md), [R120](R120-access-window-and-geometry-planning.md) (Access Window and Geometry Planning)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 3

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

A coding agent implementing or extending anything that touches orbits, propagation, or access
needs a working model of orbital mechanics *as the simulator actually uses it* — not the full
derivation (that's [`research/04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md)'s job), but the implementation-relevant
facts: what regime gates what, what fidelity tier is in play where, and where the seams are.

## 2. Scope

Covers: orbital regime taxonomy and its gameplay consequences, the propagator fidelity ladder
(Kepler+J2 vs. SGP4), the integer-microsecond clock, and the relationship between orbital state and
the access-window primitive. Does **not** cover: the access-channel/window computation itself
([R120](R120-access-window-and-geometry-planning.md)), or debris/conjunction modeling (`research/04b-debris-and-conjunction.md`).

## 3. Concepts

**Regime as reachability gate.** [`engine/orbit.py`](../../../spacesim/engine/orbit.py)'s `classify_regime` sorts a satellite into one
of five altitude/period bands. Regime is checked *before* any effect resolution because it
determines physical reachability — a ground-based kinetic interceptor sized for one regime cannot
reach another regardless of operator intent; a co-orbital actor can reach anywhere but takes time
to phase there. This is why regime classification is a first-class, early gate in the effect
pipeline rather than a derived display value.

**Fidelity ladder.** Two propagators exist behind the `Propagator` seam (MSTR-002 §4): Kepler+J2
for fictional orbits (fast, deterministic, sufficient for invented vignette assets, following the
secular-J2 treatment in [Vallado, *Fundamentals of Astrodynamics and Applications*](https://celestrak.org/software/vallado-sw.php)),
and the SGP4 model — originally specified in [Hoots & Roehrich, *Spacetrack Report No. 3* (1980-12)](https://celestrak.org/NORAD/documentation/spacetrk.pdf)
([Wayback](https://web.archive.org/web/2026/https://celestrak.org/NORAD/documentation/spacetrk.pdf))
and revisited for modern precision in [Vallado, Crawford, Hujsak & Kelso, "Revisiting Spacetrack
Report #3" (AIAA 2006-6753)](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)
([Wayback](https://web.archive.org/web/2026/https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf))
— via the [Skyfield](https://rhodesmill.org/skyfield/) ([Wayback](https://web.archive.org/web/2026/https://rhodesmill.org/skyfield/))
Python library for real TLE-derived orbits (force-added real objects, sourced from
[CelesTrak](https://celestrak.org/) ([Wayback](https://web.archive.org/web/2026/https://celestrak.org/))).
Both satisfy the determinism invariant — no propagator may read wall-clock time or unseeded RNG. A
third, higher-fidelity numerical propagator is anticipated but does not exist yet;
[`engine/perturbations.py`](../../../spacesim/engine/perturbations.py)'s drag/J3/J4/third-body/SRP functions are pure functions *staged* for that
future propagator, not yet wired into either current tier.

**Integer-microsecond clock.** Sim-UTC is represented as integer microseconds
([`engine/simtime.py`](../../../spacesim/engine/simtime.py)), with ISO conversion only at the UI/API boundary. This is what makes
determinism exact at the bit level rather than approximately reproducible — floating-point time
representations accumulate rounding error across a long replay that integer time does not.

**Sun/eclipse model.** [`engine/sun.py`](../../../spacesim/engine/sun.py) provides both a binary `is_sunlit()` and a smooth
`eclipse_fraction()` (umbra/penumbra interpolation). The smooth version exists specifically because
a binary sunlit/eclipsed model produces a visible discontinuity ("cliff") in power-tick behavior at
the terminator — consistent with the cylindrical-shadow umbra/penumbra geometry in
[Vallado, *Fundamentals of Astrodynamics and Applications*](https://celestrak.org/software/vallado-sw.php),
ch. 5 (shadow/eclipse determination) — see [R111](R111-power-and-thermal-operations.md) §4 for the
consequence this had for the power model before the Jun 2026 fix.

### Sources

- *Hoots & Roehrich, Spacetrack Report No. 3* (1980-12) — [live](https://celestrak.org/NORAD/documentation/spacetrk.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://celestrak.org/NORAD/documentation/spacetrk.pdf)
  · accessed 2026-06-27.
- *Vallado, Crawford, Hujsak & Kelso, "Revisiting Spacetrack Report #3", AIAA 2006-6753* — [live](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)
  · accessed 2026-06-27.
- *Skyfield documentation (Brandon Rhodes)* — [live](https://rhodesmill.org/skyfield/)
  · [snapshot](https://web.archive.org/web/2026/https://rhodesmill.org/skyfield/)
  · accessed 2026-06-27.
- *CelesTrak orbital catalog* — [live](https://celestrak.org/)
  · [snapshot](https://web.archive.org/web/2026/https://celestrak.org/)
  · accessed 2026-06-27.
- *Vallado, Fundamentals of Astrodynamics and Applications* (software/reference page) — [live](https://celestrak.org/software/vallado-sw.php)
  · [snapshot](https://web.archive.org/web/2026/https://celestrak.org/software/vallado-sw.php)
  · accessed 2026-06-27.

## 4. Operational Context

Real space operators plan around exactly these same constraints: which regime an asset/threat
occupies determines what's even possible, propagator fidelity determines how far in advance a
prediction can be trusted, and eclipse geometry determines power budget — none of this is simulator
flavor, it's the actual operational substrate. A vignette author choosing asset orbits is implicitly
choosing the regime-driven menu of what's tactically possible in that scenario ([R104](R104-collection-management.md), [R108](R108-constellation-operations.md)).

## 5. Implementation Guidance

- **Always check regime before assuming an effect is reachable.** A new effect category
  ([R115](R115-electronic-warfare-in-space-operations.md)-[R117](R117-directed-energy-and-kinetic-effects.md)) must declare which regimes it can operate against; don't assume universal
  reachability.
- **Never introduce a third code path that bypasses the `Propagator` seam.** A new fidelity tier
  must implement the existing interface, not branch around it (MSTR-002 §4).
- **Treat eclipse as continuous, not boolean, in any new power/visibility-sensitive logic.** Use
  `eclipse_fraction()`, not `is_sunlit()`, unless a genuine binary is required (e.g. a UI badge) —
  and if so, derive the binary from the fraction rather than maintaining two independent sources.
- **Keep all time as integer microseconds internally.** Convert to ISO/float only at the
  UI/API/display boundary, never inside `engine/`.

## 6. Feature Mapping

FS-101 (Mission Planning) and FS-105 (Spacecraft Operations) both depend on this topic: any planning
or maneuver UI must reflect real regime/propagator constraints, not an idealized free-reachability
model.

## 7. Related Topics

[`research/04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md) (full math), `04a-propagator-fidelity.md` (per-tier
validation depth), `04b-debris-and-conjunction.md`, [R120](R120-access-window-and-geometry-planning.md) (the access-window computation this
orbital state feeds into), [R112](R112-propulsion-and-maneuver-planning.md) (maneuver planning, which consumes orbital state to compute Δv).
