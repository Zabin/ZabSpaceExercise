# R112 — Propulsion and Maneuver Planning

> **Document ID:** R112
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md)
> **Referenced By:** [R111](R111-power-and-thermal-operations.md), [R117](R117-directed-energy-and-kinetic-effects.md), FS-101, FS-105
> **Produces:** implementation constraints for [`engine/maneuver.py`](../../../spacesim/engine/maneuver.py), [`engine/entities.py`](../../../spacesim/engine/entities.py) (`AssetResources`)
> **Feature Mapping:** FS-101 (Mission Planning), FS-105 (Spacecraft Operations)
> **Related Topics:** [R101](R101-orbital-mechanics-for-operations.md) (Orbital Mechanics), [R111](R111-power-and-thermal-operations.md) (Power and Thermal — the sibling decoupled-field
> note on `propellant_frac`), [R117](R117-directed-energy-and-kinetic-effects.md) (Directed Energy and Kinetic Effects — evasion burns)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Maneuver planning is where Δv economy becomes a felt operational constraint — every maneuver order
costs a finite, trackable resource, and the six entry modes in [`engine/maneuver.py`](../../../spacesim/engine/maneuver.py) exist so an
operator can express a maneuver intent in whichever frame is operationally natural without the
engine losing the pure-function, replay-safe property every order execution depends on.

## 2. Concepts

**All six entry modes reduce to one ECI impulse vector.** `compute_maneuver` translates
`eci`/`lvlh`/`finite_burn`/`target_coe`/`hohmann`/`plane_change` parameterizations into the single
`dv: [x, y, z]` ECI vector that `_h_maneuver` actually consumes — the variety is at the planning UI
layer; the executed primitive is uniform and simple, which is what keeps replay exact.

**Δv is a metered resource, not a pass/fail gate.** `actor.resources.delta_v_ms` is checked at both
validation time (`_validate`: "insufficient_delta_v" if the requested `dv` magnitude exceeds the
remaining budget) and again at execution time (`_h_maneuver` re-checks, since resources may have
changed between planning and the window arriving) — the same re-validate-at-execute pattern [R103](R103-satellite-command-and-control.md)
describes for commands generally.

**`hohmann` returns a deferred second burn, not two simultaneous burns.** The Hohmann entry mode
computes the first burn and a `second_burn` dict describing the apoapsis circularization the
operator must separately plan and issue as its own order — modeling that a real two-burn transfer
is genuinely two C2 events separated by a coast arc, not an atomic operation.

**The propellant gauge is currently a known decoupled field.** `PropulsionState.propellant_frac`
does not move when `resources.delta_v_ms` is spent on a burn — this is documented in [R111](R111-power-and-thermal-operations.md) §2 as a
lower-priority follow-up, not a silent bug to route around. A maneuver-planning feature should be
aware its Δv math is correct even though the propellant *display* is currently inert.

## 3. Operational Context

Real maneuver planning is fundamentally Δv-budget management: every burn, evasive or planned,
draws down a finite consumable that cannot be replenished on-orbit, so operators plan maneuvers
against a lifetime Δv ledger, not per-maneuver in isolation — exactly what tracking
`delta_v_ms` across the whole mission (rather than resetting it) is meant to teach.

## 4. Implementation Guidance

- **Any new maneuver-planning UI must go through `compute_maneuver`**, not hand-roll a Δv vector —
  this keeps all six entry modes consistent and pure (no state mutation in the planning layer).
- **A multi-burn maneuver type (Hohmann-like) should return a `second_burn`-style deferred
  descriptor**, not silently schedule a second burn itself — the operator must explicitly plan and
  issue the second leg, preserving plan-first (MSTR-002 invariant 4).
- **Do not assume `propellant_frac` reflects Δv spent** — if a feature needs an accurate propellant
  gauge, treat fixing the decoupling as its own scoped Implementation Package ([R111](R111-power-and-thermal-operations.md) §4), not a
  side effect of an unrelated maneuver feature.
- **Re-validate Δv sufficiency at execution time**, mirroring `_h_maneuver`, for any new
  Δv-consuming order type (e.g. `def.maneuver_evade` in `buscommands.py` already follows this
  pattern).

## 5. Feature Mapping

FS-101 (Mission Planning) and FS-105 (Spacecraft Operations) both depend on accurate Δv-economy
modeling for any new maneuver-adjacent feature.

## 6. Related Topics

[R101](R101-orbital-mechanics-for-operations.md) (the orbital mechanics maneuvers act on), [R111](R111-power-and-thermal-operations.md) §2 (the decoupled propellant-gauge follow-up),
[R117](R117-directed-energy-and-kinetic-effects.md) (kinetic engagement evasion burns reuse the same Δv-resource model).
