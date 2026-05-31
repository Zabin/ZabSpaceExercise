# Vignette 2 — GEO RPO Shadowing

**Domains:** Orbital warfare (RPO) · **Duration:** ~75 min (compressed) · **Red profile:**
Russia EW-first / GEO shadow (default) · **Difficulty:** Core

## Premise
A Red inspector satellite (Luch/Olymp-style) begins a slow drift along the GEO belt and
maneuvers toward Blue's high-value protected SATCOM satellite, settling into a close-station
"shadow." Red's intent is **ambiguous by design** — the same maneuver supports SIGINT
collection, inspection, or pre-positioning for a co-orbital attack. Blue must decide how to
respond *before* it knows which.

## Learning objectives
1. **RPO intent is unknowable from geometry alone.** A close approach is not inherently
   hostile; doctrine and attribution, not range, drive the response.
2. GEO maneuvers play out over **hours-to-days** — compressed time is essential, and decisions
   are made on *predicted* closest approach, not current range.
3. Options form an escalation ladder: **monitor → query/signal → maneuver Blue away → position
   a Blue escort → suppress Red's tasking → counterattack.**
4. Every Blue GEO maneuver spends **station-keeping fuel** that shortens the satellite's
   service life — a real and painful cost.

## Order of battle (sketch)
**Blue:** 1× high-value protected SATCOM (GEO), 1× GEO SDA/inspector ("bodyguard," tunable
on/off), 2 ground stations with GEO visibility. Fuel budgets tracked.
**Red:** 1× GEO inspector with meaningful delta-v, 1× ground SDA, optional 2nd inspector.

## Key tunable parameters
| Parameter | Default | Effect |
|---|---|---|
| `rpo_closing_speed` | normal | cautious/normal/aggressive — sets Red delta-v & time-to-close |
| `red_payload_ambiguity` | high | How hard it is for Blue to characterize Red's payload |
| `blue_escort_available` | true | Whether Blue has a bodyguard sat to interpose |
| `blue_fuel_budget` | medium | Tight fuel forces hard maneuver-or-not choices |
| `time_compression_default` | 600x | Days of GEO drift fit a session |
| `red_intent` (White-only) | shadow | shadow / inspect / pre-attack — hidden from Blue |
| `attribution_difficulty` | realistic | Speed/confidence of Blue's characterization |

## Sample injects
- `T+00:15` Red inspector executes a phasing burn; SDA shows changed drift rate (Blue sees a
  *prediction* of closer approach).
- `condition` Red closes within keep-out threshold → Blue gets a "declare intent / take action"
  decision prompt.
- `manual` White Cell reveals (or doesn't) Red's true intent to drive AAR discussion.

## Victory conditions
- **Blue:** Preserve the SATCOM satellite's mission availability and survival while minimizing
  fuel burned and avoiding unwarranted escalation. Correctly characterizing Red's intent scores
  highly.
- **Red:** Achieve its (hidden) objective — sustained close collection, or successful pre-
  positioning — without provoking a Blue counterattack it can't justify.

## Notes for Claude Code
This vignette is the reason the engine needs the **RPO closing model** and **predicted
closest-approach** surfaced in the UI. Hidden `red_intent` is a good test of the per-cell
fog-of-war/visibility filter.
