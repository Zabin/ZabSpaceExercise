# Vignette 1 — LEO ISR Denial

**Domains:** Orbital warfare, Electromagnetic warfare, Directed energy
**Duration:** ~60 min · **Red profile:** PLA early-disruption (default) · **Difficulty:** Intro

## Premise
Blue operates a small constellation of LEO electro-optical and SAR imaging satellites
watching a contested island chain where Red is assembling an amphibious surface group. Red
wants to **deny Blue imagery during a critical 90-minute movement window** without (initially)
generating debris or an unambiguous act of war. Blue wants to **maintain custody** of the Red
surface group and get the imagery home.

This is the teaching vignette: it forces both sides to live inside LEO pass windows.

## Learning objectives
1. Imaging a target and downlinking that image are **two separate pass problems** — Blue may
   collect over the target but be unable to downlink until a later ground-station pass.
2. The most effective Red options here are **reversible**: dazzle the optics during a pass,
   or jam the downlink — not kinetic strike.
3. Ground concealment timed to **known pass windows** is a legitimate, cheap counter.
4. Escalating to a kinetic ASAT to solve a temporary problem is disproportionate and creates
   debris that may also threaten Red's own LEO assets.

## Order of battle (sketch)
**Blue:** 3× ISR-EO (LEO Sun-synchronous), 1× ISR-SAR (LEO), 3 ground stations (tunable),
1 imagery processing center. Passive defenses: maneuver, deception (default on).
**Red:** Amphibious surface group (terrestrial), 2× mobile directed-energy dazzlers near the
landing area, 2× mobile downlink jammers, 1× co-orbital inspector (LEO), optional DA-ASAT
(off by default). SDA: regional radar.

## Key tunable parameters
| Parameter | Default | Effect |
|---|---|---|
| `blue_ground_station_count` | 3 | Fewer stations → Blue struggles to downlink in time |
| `red_dazzle_coverage` | partial | How much of the pass the dazzlers can deny |
| `red_downlink_jam` | on | Denies imagery delivery near Red territory |
| `red_kinetic_authorized` | **false** | Unlocks DA-ASAT as a (costly) Red option |
| `blue_passive_defenses` | maneuver, deception | Adds dispersal/redundancy options |
| `attribution_difficulty` | realistic | How fast Blue realizes it's being dazzled vs. "bad imagery" |
| `landing_window_start` | T+00:30 | When the critical Red movement begins |

## Sample injects
- `T+00:20` **manual/auto:** Red dazzlers come online (message to White only; Blue must infer).
- `T+00:45` Commercial SAR imagery leak partially reveals the surface group (helps Blue, models
  the commercial-space reality).
- `condition` if Blue images + downlinks the group before `landing_window_start` → Blue
  partial win inject fires.

## Victory conditions
- **Blue:** Deliver confirmed imagery of the Red surface group to the processing center before
  the landing window closes; bonus for maintaining continuous custody.
- **Red:** Keep Blue from delivering usable imagery during the window using reversible means;
  penalty (political_consequence inject) if Red uses kinetic and generates debris.

## Notes for Claude Code
Good first vignette to implement end-to-end because it exercises: pass-window gating, the
collect-vs-downlink distinction, a reversible-effect resolution, and attribution fog — without
needing the full RPO closing model.
