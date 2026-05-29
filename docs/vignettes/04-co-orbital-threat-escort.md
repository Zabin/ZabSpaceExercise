# Vignette 4 — Co-Orbital Threat & Active Escort Defense

**Domains:** Orbital warfare (active space defense) · **Duration:** ~75 min (compressed) ·
**Red profile:** China integrated (default) · **Difficulty:** Advanced

## Premise
Red maneuvers a co-orbital ASAT-capable satellite toward a Blue early-warning or wideband
SATCOM asset and demonstrates **hostile intent** (aggressive closing, sensor cueing). Blue has
an **escort/"bodyguard" satellite** and must execute active space defense: interpose the
escort, maneuver the protected asset, suppress Red's targeting, or — if authorized — conduct an
orbital counterattack. This vignette is about the **defensive half** of the doctrine.

## Learning objectives
1. **Active defense options** — escort (point/area), counterattack, and suppression of adversary
   counterspace targeting — and when each applies.
2. Escort is a **positioning game**: the bodyguard must already be in the right phase to
   interpose; you can't summon it instantly.
3. **Maneuver-to-evade** trades fuel/service-life for survival and may break the protected
   asset's mission geometry.
4. The defender often must act on **demonstrated hostile intent** before a shot is fired —
   and getting that judgment wrong is costly either way.

## Order of battle (sketch)
**Blue:** 1× high-value protected asset (GEO or HEO), 1× escort satellite with delta-v, GEO
SDA, 2 ground stations. ROE tunable (when may Blue counterattack?).
**Red:** 1× co-orbital ASAT-capable satellite (delta-v, ambiguous payload), ground SDA, optional
2nd "nesting-doll" sub-satellite that deploys at close range.

## Key tunable parameters
| Parameter | Default | Effect |
|---|---|---|
| `red_aggression` | high | How clearly Red signals hostile intent / how fast it closes |
| `blue_escort_phase` | favorable | Whether the escort is positioned to interpose in time |
| `red_subsat_deploy` | off | Red can split a sub-satellite at close range (raises threat) |
| `blue_roe` | restrictive | restrictive / conditional / permissive — when Blue may counterattack |
| `blue_fuel_budget` | medium | Limits maneuver-to-evade options |
| `attribution_difficulty` | realistic | Confidence needed before Blue may act |

## Sample injects
- `T+00:20` Red asset cues a tracking sensor on the Blue protected asset (demonstrated intent).
- `T+00:40` (if `red_subsat_deploy`) Red deploys a sub-satellite inside the keep-out zone.
- `manual` White Cell adjusts `blue_roe` mid-game to explore decision pressure.

## Victory conditions
- **Blue:** Protected asset survives and stays mission-capable; Blue's defensive response is
  *proportionate and justified* given the intelligence available (scored on judgment, not just
  survival).
- **Red:** Neutralize or suppress the protected asset, or force Blue into a disproportionate,
  attributable escalation.

## Notes for Claude Code
Exercises **escort interpose geometry**, **maneuver-to-evade**, and an **ROE/authority gate**
on counterattack. The judgment-scoring (was Blue's response justified?) is a White-Cell/AAR
feature, not an automatic resolution — surface the decision and its basis for later review.
