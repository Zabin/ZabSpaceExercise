# Delta-V Economy — Fuel as the Operator's Hardest Constraint

A maneuverable satellite's propellant is **finite and non-renewable.** Every maneuver spends
from a budget that also has to last the satellite's whole service life. The user specifically
asked that operators see **total remaining delta-v** and understand it **against the typical
annual budget** (e.g., station-keeping and collision avoidance) so they grasp the
**lifetime-vs-large-maneuver trade**: a single aggressive evasion or RPO can burn *years* of
station-keeping fuel and effectively shorten the satellite's life or strand it. This file makes
that trade concrete, with realistic numbers, and specifies how the UI presents it.

## 1. The core teaching point
> **Delta-v is a bank account you can never refill.** A GEO satellite typically spends about
> **50 m/s per year** just holding its slot. If it launched with, say, **~750 m/s** for a
> 15-year life, then a **single 150 m/s maneuver burns three years of station-keeping** — three
> years of mission life gone in one burn. Operators must feel that weight before they spend.

## 2. Realistic reference numbers (for asset templates & the UI gauge)

These are **representative** values for a moderate-fidelity training tool, drawn from public
astrodynamics references. They are tunable per template; the point is the *ratio* between
routine annual upkeep and one-off maneuvers, not exact mission accuracy.

### 2.1 Routine annual upkeep (the baseline operators compare against)
| Regime | Routine annual station-keeping Δv | Notes |
|---|---|---|
| **GEO** | **~50 m/s/year** | ~95% is north-south inclination control (Sun/Moon); east-west longitude hold is <2 m/s/yr |
| **LEO** | **~few–25 m/s/year** (highly altitude-dependent) | drag make-up; negligible up high, significant low |
| **MEO** | **very low** (~a few m/s/year) | stable; rarely the maneuver story |
| **Collision avoidance** | **~0.1–1 m/s per event**, a handful of events/year | small per event, but they add up and are unplanned |

### 2.2 One-off / tactical maneuvers (what burns the budget fast)
| Maneuver | Representative Δv | "Costs how many years of GEO upkeep?" |
|---|---|---|
| Collision-avoidance dodge | ~0.1–1 m/s | days–weeks |
| GEO longitude relocation (slow drift, weeks) | ~5–20 m/s | months |
| Aggressive evasion of a co-orbital threat | ~20–100 m/s | months–2 years |
| GEO RPO approach + station-hold for days | ~50–200+ m/s | 1–4+ years |
| Plane change / large regime shift | hundreds–thousands m/s | often **the rest of the satellite's life** |

### 2.3 Representative launch budgets (lifetime tank) for templates
| Template class | Starting Δv budget (representative) | Implied life at routine rate |
|---|---|---|
| GEO SATCOM (exquisite) | 600–900 m/s | ~12–18 yr @ 50 m/s/yr |
| GEO inspector / RPO asset | 1,000–1,500 m/s | designed to maneuver — but still finite |
| LEO ISR | 50–200 m/s | a few years of drag + some tasking agility |
| Co-orbital effector (Red) | 1,000–2,000 m/s | high agility, the whole point of the asset |

> The **inspector/effector** templates get bigger tanks because maneuvering *is* their mission —
> but the sim still makes them spend it, so an operator who chases every target runs dry and
> becomes a sitting duck. That is a designed lesson.

## 3. What the operator sees (UI — extends `09-gui-principles.md`)

For every maneuverable asset, the bus/SOH panel shows a **Delta-V gauge** with four facts, so
the lifetime trade is impossible to miss:

```
┌──────────────────────────────────────────────────────────┐
│ BLUE-SATCOM-1   ΔV REMAINING                                │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░  612 / 750 m/s   (82%)                 │
│ Routine upkeep: ~50 m/s/yr  →  est. ~12.2 yr remaining      │
│ This planned burn: 150 m/s  →  spends ~3.0 yr of life       │
│ ⚠ After burn: 462 m/s  →  est. ~9.2 yr remaining            │
└──────────────────────────────────────────────────────────┘
```

Elements:
1. **Total remaining** (m/s and % of original) — the bank balance.
2. **Annual upkeep rate** for this asset's regime — the yardstick.
3. **Estimated lifetime remaining** = remaining ÷ annual upkeep (a plain-language "~9 years").
4. **Cost preview of the planned maneuver**, expressed *both* in m/s *and* in **"years of life
   spent"** — the comparison the user asked for. Aggressive burns turn the preview **amber/red**.

When planning a burn (`prop.maneuver`, `def.maneuver_evade`, `sc.rpo_approach`), the order panel
shows the cost preview **before commit**, and a deliberate confirm appears when a single maneuver
would spend more than a threshold (e.g., >1 year of life) — consistent with "confirm only the
consequential" (`09-gui-principles.md` P4/§4).

## 4. Engine model (moderate fidelity; extends `03-simulation-engine.md`)

- Each maneuverable asset carries `delta_v_ms` (remaining) and `delta_v_ms_initial`, plus a
  regime-derived `annual_upkeep_ms`.
- **Routine upkeep accrues over sim time:** station-keeping is auto-debited at `annual_upkeep_ms`
  pro-rated to elapsed sim time (so just *existing* slowly spends fuel — visible on the gauge).
  White Cell can toggle auto-upkeep off for short tactical vignettes where it's noise.
- **Maneuvers debit instantly** by their computed cost:
  - station-keep / collision-avoid: small fixed/at-cost values from §2;
  - regime change / phasing / RPO: from the impulsive-burn math (Hohmann-class transfer +
    phasing) the propagator already computes for the maneuver;
  - evasion: cost scales with how hard/fast the dodge is (a parameter of the command).
- **Empty tank = no maneuver.** At `delta_v_ms ≤ 0` the asset cannot maneuver or station-keep;
  it begins to **drift** (GEO walks off its slot; low LEO decays faster), which the SDA picture
  and mission performance reflect. This is the visible consequence of overspending.
- **Lifetime estimate** surfaced to UI = `delta_v_ms / annual_upkeep_ms` (guards divide-by-zero
  for non-upkeep regimes).

```yaml
# Added to Asset (canonical in 04-data-model.md):
propulsion:
  delta_v_ms: 612.0
  delta_v_ms_initial: 750.0
  annual_upkeep_ms: 50.0          # regime-derived; auto-debited over time if upkeep on
  drifting: false                 # true once budget exhausted
maneuver_cost_preview:            # computed for a candidate burn, shown pre-commit
  dv_ms: 150.0
  years_of_life: 3.0
  post_burn_dv_ms: 462.0
  post_burn_years: 9.2
  severity: amber                 # green|amber|red by years-of-life thresholds
```

## 5. White Cell dials (added to parameter schema, `06-white-cell-controls.md`)
| Parameter | Type | Default | Affects |
|---|---|---|---|
| `delta_v_auto_upkeep` | bool | true | Whether just-existing slowly debits station-keeping fuel. |
| `delta_v_scarcity` | enum: generous / realistic / tight | realistic | Scales starting budgets; `tight` makes every burn a hard choice. |
| `maneuver_confirm_threshold_years` | float | 1.0 | A burn spending more than this many years of life requires a deliberate confirm. |

## 6. Why this matters for the exercise
This converts "maneuver" from a free verb into a **strategic resource decision**, which is the
real operator experience and a frequent failure mode in training: cells that "maneuver to be
safe" early often discover they have stranded an exquisite asset with years of mission still
expected. Surfacing remaining life *and* the per-burn cost in **years** (not just m/s) makes
the consequence legible to a semi-technical operator at the moment of decision — exactly the
understanding the user asked the tool to build. It also sharpens the RPO/escort/evasion
vignettes (2 and 4): the defender's "just dodge it" instinct now has a price tag, and the
attacker can *win by forcing the defender to burn fuel* even without ever striking.

## Sources
- GEO station-keeping ~50 m/s/yr (95% north-south), east-west <2 m/s/yr: station-keeping
  references (daviddarling encyclopedia; USRadioguy GOES drift analysis).
- Delta-v as an additive, non-renewable budget summed over mission maneuvers: Wikipedia
  *Delta-v budget*; NASA NTRS station-keeping analyses (annual SK totals ~58–75 m/s in cited
  lunar cases, same order of magnitude framing).
- Collision-avoidance per-event Δv is small (sub-1 m/s) but unplanned: general operations
  practice.
