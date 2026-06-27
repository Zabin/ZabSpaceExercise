# R111 — Power and Thermal Systems Operations

> **Document ID:** R111
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md), [R103](R103-satellite-command-and-control.md)
> **Referenced By:** [R113](R113-attitude-determination-and-control.md), [R114](R114-command-and-data-handling.md), DOM-007, FS-105
> **Produces:** implementation constraints for [`engine/bus.py`](../../../spacesim/engine/bus.py), [`engine/busmodel.py`](../../../spacesim/engine/busmodel.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [`docs/AUDIT-2026-06-UI-TTC.md`](../../AUDIT-2026-06-UI-TTC.md) §2 (the precedent worked example),
> DOM-005 §4 (fidelity-claim validation method), DOM-007 §4 (causality must be surfaced)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Power (EPS/battery/eclipse cycling) and thermal state are the bus subsystems most likely to be
touched by a future feature (new payload power draw, a new thermal model) and are also where the
project has direct, documented experience of an implementation getting the *operational* behavior
wrong despite passing its own unit-level checks (the Jun 2026 power-calibration bug). This topic
exists to make that lesson available to the next implementer rather than buried in an audit report.

## 2. Scope

Covers: the `advance_bus` charge/drain balance, depth-of-discharge (DoD) as the operationally
meaningful quantity, and the documented dead/decoupled-field bug class. Does **not** cover: the
eclipse-fraction geometry feeding `sunlit` ([R101](R101-orbital-mechanics-for-operations.md) §3), ADCS pointing's effect on array
illumination ([R113](R113-attitude-determination-and-control.md)), or sensor-collection power drain itself ([R109](R109-sensor-operations.md)).

## 3. Concepts

**Charge/drain as a continuous balance, not a step function.** `advance_bus(sunlit)` (now taking a
*lit fraction* rather than a boolean — see [R101](R101-orbital-mechanics-for-operations.md) §3) blends `charge·lit − drain·(1−lit)`. Battery
state-of-charge (SoC) is the integral of this balance over the orbit, so its behavior is highly
sensitive to the *relative* magnitude of charge vs. drain rates, not just their individual values.

**Depth of discharge (DoD) is the operationally meaningful quantity, not raw SoC.** A bus cycling
between 1.00 and 0.37 every orbit (63% DoD) — the original miscalibrated baseline — is 3-4× deeper
than a realistic LEO bus, where NASA cell-qualification testing for satellite/orbiter applications
targets 20-40% DoD per 90-minute orbit cycle to meet multi-year cycle-life requirements
([NASA, *Performance and Comparison of Lithium-Ion Batteries*, NTRS 20080008855](https://ntrs.nasa.gov/api/citations/20080008855/downloads/20080008855.pdf)
([Wayback](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20080008855/downloads/20080008855.pdf))),
even though the underlying integration math (`advance_bus`) was completely correct. **A correct
integrator can still produce operationally wrong behavior if its input constants are wrong.** This
is the single most important fact this topic exists to convey.

**Eclipse drives drain causally, and that causality must be visible.** `soh_snapshot` exposing
`in_eclipse` exists because a falling SoC number with no visible cause is operationally
indistinguishable from a bug, even when it's correct physics — see DOM-007 §4.

**Dead/decoupled fields are a known, documented class of bug.** `entities.AssetResources.power_w`
is never read (the model uses `charge_rate_per_s` instead); `propulsion.propellant_frac` is
decoupled from `resources.delta_v_ms` (burning Δv never moves the propellant gauge). These are
**documented, lower-priority follow-ups**, not regressions to silently work around — see §5.

### Sources

- *NASA, Performance and Comparison of Lithium-Ion Batteries for Future NASA Missions and Aerospace
  Applications, NTRS 20080008855* — [live](https://ntrs.nasa.gov/api/citations/20080008855/downloads/20080008855.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20080008855/downloads/20080008855.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

Real LEO bus power budgets are designed around a target DoD (per NASA cell-qualification practice,
commonly 20-40%, well shallower than 60%+, to preserve battery cycle life across 5-7 year missions
running ~5,000-16 cycles/year from 30-40-minute eclipses) and an eclipse fraction that varies with
orbit inclination/altitude and season. Operators monitor SoC trend *relative to the orbit's eclipse
geometry*, not as an isolated number — exactly the causal-legibility requirement in DOM-007 §4.

## 5. Implementation Guidance

- **Before tuning a charge/drain constant, compute the resulting steady-state DoD over a full orbit
  and sanity-check it against a realistic LEO range** — this is the concrete DOM-005 §4 validation
  method applied to this subsystem; don't tune by "looks reasonable in a quick test run."
- **A regression test should pin a baseline SoC range**, the way `test_power_calibration.py` pins
  "baseline SoC ≥ 0.30 over several orbits" — a power-model change without an accompanying
  calibration regression test is incomplete.
- **Any new load (a new payload power draw, a new defensive system) must be wired through the same
  `charge_rate_per_s`-style abstraction**, not a parallel ad hoc drain calculation — and must be
  re-validated against §4's DoD sanity check, since adding load shifts the balance.
- **If you pick up the dead `power_w` field or the decoupled propellant gauge (§2)**, treat it as a
  scoped Implementation Package (derive rates from array W + battery Wh; or pick one Δv source of
  truth) — do not silently patch around the inconsistency in a one-line fix without documenting the
  decision.
- **`ThermalState.temp_c`/`heater_watts`/`radiator_capacity_w` are declared but not yet integrated**
  by `advance_bus` (`temp_c` is static at 20°C) — a feature that reads these fields today is reading
  inert placeholders, not live state; check before assuming.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer. DOM-007 (causality surfacing) and DOM-005
(fidelity validation method) both apply directly to any future power/thermal work.

## 7. Related Topics

`AUDIT-2026-06-UI-TTC.md` §2 (the full incident writeup this topic distills), [R101](R101-orbital-mechanics-for-operations.md) §3 (the
eclipse-fraction model this subsystem consumes), [R113](R113-attitude-determination-and-control.md) (ADCS — pointing affects array
illumination, a coupling not yet modeled), DOM-007 §4 (causality-must-be-surfaced UI principle).
