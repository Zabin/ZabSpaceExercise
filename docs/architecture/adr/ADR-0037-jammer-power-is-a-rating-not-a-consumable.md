# ADR-0037 — A jammer's `power_w` is a rating, not a consumable resource

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0037
- **Title:** A terrestrial jammer's `AssetResources.power_w` is not consumed by jamming; the
  success-path subtraction is a defect against GDS-04 §1.2
- **Status:** Accepted

## Context

GDS-04 §1.2 (Asset) lists "resource levels (fuel/power/ammo)" in an asset's persistent state and
states the constraint "resource levels cannot go negative (e.g. `delta_v_ms`)".

As built (verified 2026-10-17): `AssetResources.power_w` defaults to `0.0`
(`engine/entities.py`). A jam order's transmit power is the **order's** `power_w` parameter (default
100 W, console default 200 W), which drives success probability and footprint radius
(`engine/orders.py` jam planning; `engine/jam.py` `effective_radius_km`). On a *successful* jam,
the effect handler subtracts the modulation-scaled draw (`jam.power_draw_w`) from the jammer's
`resources.power_w` (`orders.py`, the `consume` step in the effect handler). Nothing reads
`resources.power_w` afterwards: no validation compares the order's power to it, no handler gates
on it, and `advance_bus` never reads it (`R111` §2 already records it as a dead field for
satellites; `FR-5180` forbids exposing it as a bus power budget for that reason). Only one shipped
vignette sets it (`01-leo-isr-denial`, 1500 W on a satellite). So every successful jam drives the
jammer's `power_w` below zero, visibly in god view and save files, contrary to GDS-04 §1.2.
`04-requirements-engineering` reported this as a conflict, not a baselined leaf (run #142, report
F3; `FR-1460` Notes), and routed the interpretation here (`BL-0239`).

## Decision

`AssetResources.power_w` on a jammer is a **power rating** (watts — a rate), not a depleting energy
budget. Jamming does not consume it. GDS-04 §1.2's "cannot go negative" constraint applies to it as
it does to every resource level, and a rating that is never decremented satisfies it trivially.
The success-path subtraction of the jam draw from `resources.power_w` is therefore a **defect**,
to be removed by a remediation package; the `ammo` subtraction in the same step (a genuine
consumable, governed by `FR-1460`) is unaffected.

Enforcing a rating — refusing a jam whose requested `power_w` exceeds the jammer's
`resources.power_w` — is **not** part of this decision. It is new behaviour (every shipped jammer is
rated 0 W, so it would refuse every shipped jam until vignettes author figures) and, if wanted,
comes through `00-intake` as a feature.

## Alternatives Considered

- **A consumable, non-negative budget** — rejected. Watts measure power, not energy, so
  subtracting a watt figure once per jam has no physical meaning: a transmitter's power capability
  is not used up by transmitting. A real consumable would be an energy store in watt-hours,
  depleted at the draw rate over the jam's duration — which, for a satellite, already exists as the
  bus EPS state of charge (`R111`). Making `power_w` a budget would also mean refusing almost every
  shipped jam (jammers are rated 0 W) or authoring a figure into every jammer in every vignette,
  for a model that is still dimensionally wrong.
- **Clamp at zero** (keep the subtraction, floor it at 0) — rejected. It hides the symptom, keeps a
  field that changes meaning after the first jam, and still implies power is "used up".
- **Amend GDS-04 §1.2** to drop "power" from the resource levels — not needed. The constraint is
  correct as written; the code violates it. This decision interprets the closed-gate text, it does
  not change it.

## Rationale

The decision keeps GDS-04 §1.2 intact, matches the physics (`R111`'s power/energy distinction),
matches how the jam model already works (power is an order parameter that scales effectiveness
inside the resolver, the same reachability-vs-effectiveness split `ADR-0034` records), and changes
no shipped jam's outcome — only a field nobody reads stops drifting negative.

## Consequences

- `04-requirements-engineering`: baseline a leaf under the effect-resolution family (for example
  "a jam does not change the jammer's `power_w`"), and update `FR-1460`'s Notes, which currently
  report jammer power as an unresolved conflict.
- Then the usual chain (`05` assignment to `FEAT-1400`, `06` FS-105 or the owning FS, `07` a
  remediation package) removes the `power_w` subtraction. It can share a package with `FR-1460`
  (`BL-0238`), which touches the same consumption step.
- No vignette change is required; no shipped jam's success probability, footprint or effect
  changes.

## Related

GDS-04 §1.2 "Persistent state" / "Constraints"; `FR-1460` Notes, `FR-5180`
(`docs/requirements/01-functional-requirements.md`);
[`R111`](../../research/encyclopedia/R111-power-and-thermal-operations.md) §2/§5;
`ADR-0034` (reachability vs. effectiveness);
[`reviews/requirements-update-load-validation-batch.md`](../../reviews/requirements-update-load-validation-batch.md) F3;
backlog `BL-0238`, `BL-0239`.
