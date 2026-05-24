# Vignette 3 — GNSS / PNT Electronic Warfare Campaign

**Domains:** Electromagnetic warfare · **Duration:** ~60 min · **Red profile:** Russia EW-first
(default) · **Difficulty:** Core

## Premise
Red conducts a sustained GNSS jamming and spoofing campaign over a theater to degrade Blue's
precision weapons, drones, and timing — the most operationally validated counterspace pattern
in the real world (Ukraine). Blue's PNT satellites are in **MEO and effectively immune to
kinetic attack**, so the entire fight is over the *signal* and the *users*, not the
satellites. Blue must sustain precision operations through anti-jam measures, alternative PNT,
and by geolocating and neutralizing Red's jammers.

## Learning objectives
1. PNT denial is **local, reversible, and deniable** — you create a GPS-denied *bubble*, you
   don't destroy the constellation.
2. **Spoofing is worse than jamming** in some ways: a jammed receiver knows it's lost; a
   spoofed one is confidently wrong.
3. The counter to EW is often **terrestrial**: geolocate the emitter and strike or jam *it*
   (space link interdiction / terrestrial strike), plus user-side anti-jam and inertial backup.
4. MEO regime → kinetic ASAT is essentially off the table; this teaches regime-dependent
   reachability.

## Order of battle (sketch)
**Blue:** GNSS constellation (MEO, mostly a backdrop — can't be killed here), precision-strike
and drone units (terrestrial, PNT-dependent), 1× SIGINT sat (LEO) for emitter geolocation,
anti-jam/M-code receivers (tunable), inertial backup (tunable).
**Red:** 4–8× mobile GNSS jammers (Pole-21/Zhitel-style), 2× spoofers, mobile and concealed;
SATCOM uplink jammer (optional) to widen the campaign.

## Key tunable parameters
| Parameter | Default | Effect |
|---|---|---|
| `red_jammer_count` | 6 | Size of the GPS-denied bubble / coverage |
| `red_spoofing_enabled` | true | Adds deceptive PNT (confidently-wrong users) |
| `red_jammer_mobility` | high | How fast Red shoots-and-scoots to evade geolocation |
| `blue_antijam_level` | medium | M-code/CRPA antennas reduce jam effect |
| `blue_inertial_backup` | on | Degraded-but-usable PNT when denied |
| `blue_geolocation_quality` | realistic | How fast Blue can fix a jammer for counter-fire |
| `red_satcom_jam` | off | Expands campaign to SATCOM uplink denial |

## Sample injects
- `T+00:10` Red jammers activate; Blue drones begin drifting off-target (effect, not message —
  Blue must diagnose).
- `T+00:35` Red repositions jammers (shoot-and-scoot) invalidating Blue's geolocation fix.
- `manual` White Cell toggles spoofing mid-game to contrast jam vs. spoof effects.

## Victory conditions
- **Blue:** Sustain a required precision-strike success rate through the campaign; geolocate
  and neutralize a threshold number of Red emitters.
- **Red:** Hold Blue's precision-effectiveness below threshold during the decisive period while
  preserving its jammers (avoid losing them to counter-fire).

## Notes for Claude Code
No orbital strikes here — this vignette validates the **EW footprint/geolocation loop** and the
idea that some targets (MEO) are simply unreachable by kinetic means. The "diagnose the effect"
mechanic (effects appear before any message explains them) is the key UX test.
