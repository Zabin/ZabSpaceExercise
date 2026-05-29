# Vignette 7 — SDA Custody Hunt

**Domains:** Space Domain Awareness, suppression of counterspace targeting · **Duration:**
~60 min · **Red profile:** selectable · **Difficulty:** Core

## Premise
Red has deployed a new, maneuverable satellite of unknown purpose and is using **deception and
mobility** to break Blue's custody of it. Blue must build and maintain a track (find, fix,
characterize, and keep custody) using a limited set of sensors with their own visibility
windows — while Red maneuvers, exploits eclipse/lighting, and possibly **suppresses Blue's SDA**
(dazzles a sensor, jams a radar). You can't target what you can't find: this vignette is the
sensing fight that underwrites every other one.

## Learning objectives
1. **Custody decays.** Knowing where something was is not knowing where it is; tracks age and
   confidence drops between observations.
2. SDA sensors have **windows too** — radar horizon, optical needs target-sunlit/sensor-dark.
   You schedule sensing against geometry just like everything else.
3. **Maneuver + deception** (a small unobserved burn) can break a track and force costly
   re-acquisition.
4. **Suppression of adversary counterspace targeting** — degrading the *other* side's SDA — is
   itself a counterspace objective.

## Order of battle (sketch)
**Blue:** 3–5 SDA sensors (mix of ground radar, ground optical, and 1× space-based inspector),
each with realistic visibility windows; a custody/track database with decaying confidence.
**Red:** 1× maneuverable satellite of ambiguous purpose; optional dazzler against a Blue optical
sensor; optional radar jammer; deception behaviors (burns during gaps in coverage).

## Key tunable parameters
| Parameter | Default | Effect |
|---|---|---|
| `blue_sensor_count` | 4 | Coverage density / custody robustness |
| `blue_sensor_mix` | radar+optical+space | Which sensor types Blue has (each has different windows) |
| `red_maneuver_deception` | on | Red burns during coverage gaps to break custody |
| `red_sda_suppression` | off | Red can dazzle/jam a Blue sensor to open a gap |
| `custody_decay_rate` | realistic | How fast track confidence degrades between obs |
| `space_weather` | nominal | degraded weather hurts optical sensing |

## Sample injects
- `T+00:20` Red executes an unobserved burn during a coverage gap; next acquisition shows it
  "lost" / displaced — Blue must re-acquire.
- `T+00:35` (if `red_sda_suppression`) Red dazzles a Blue optical sensor, removing it for a window.
- `condition` custody confidence on the Red object falls below threshold → targeting-quality
  data unavailable (ties to other vignettes' engagement gates).

## Victory conditions
- **Blue:** Maintain custody confidence above a threshold for a required duration and correctly
  characterize the Red object's purpose.
- **Red:** Keep Blue's custody confidence low (deny targeting-quality data) and conceal the
  object's true purpose.

## Notes for Claude Code
This is the vignette that proves out the **custody/track model with decay** and the **sensor
visibility-window computation**. Custody confidence here is the same value other vignettes read
when deciding whether a "weapons-quality track" exists for an engagement — implement it once,
reuse everywhere.
