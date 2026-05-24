# Vignette 8 — Multi-Domain Integrated Campaign (Capstone)

**Domains:** All (orbital, EW, directed energy, cyber, SDA) · **Duration:** 2–3 h ·
**Red profile:** China integrated A2/AD (default) · **Difficulty:** Capstone

## Premise
The capstone. A major regional crisis (generic Indo-Pacific Taiwan-analog by default) in which
**space superiority is the precondition for joint success**. Red executes an integrated
counterspace campaign — EW-first GNSS/SATCOM denial, cyber on the ground segment, RPO shadowing
of high-value assets, SDA suppression, with kinetic ASAT held as a high-end escalation — all
synchronized to enable a terrestrial A2/AD fight. Blue must **sustain the space-enabled kill
chain** (ISR → PNT → comms → fires) long enough to achieve joint objectives, defending across
all three segments while managing escalation.

This vignette ties together every mechanic in the simulator and every other vignette's lesson.

## Learning objectives
1. **Space superiority enables joint lethality** — the space fight exists to enable (or deny)
   terrestrial effects, not for its own sake.
2. Counterspace is **integrated and synchronized**, not a menu of isolated effects — Red times
   EW + cyber + RPO together for compounding effect.
3. **Escalation management under time pressure** across reversible and non-reversible options,
   with debris and attribution consequences live.
4. **Resilience as strategy** — proliferation, disaggregation, alternate bearers, and pre-
   positioned tasking are what let Blue endure.

## Order of battle (sketch)
**Blue:** full mixed force — LEO ISR (EO + SAR), MEO PNT (backdrop), GEO + LEO SATCOM, GEO/HEO
missile warning, GEO SDA + escort, ground stations, and PNT/SATCOM-dependent terrestrial joint
forces (air, maritime, fires). Full passive-defense suite available.
**Red:** full counterspace force — GNSS/SATCOM jammers, spoofers, ground-segment cyber, GEO and
LEO RPO/co-orbital assets, ground directed-energy dazzlers, ground SDA, and a DA-ASAT capability
(authorization tunable), all supporting a terrestrial A2/AD force.

## Key tunable parameters
A superset of the other vignettes' dials, plus campaign-level controls:
| Parameter | Default | Effect |
|---|---|---|
| `red_doctrine_profile` | china_integrated | china_integrated / russia_ew_first / generic |
| `campaign_tempo` | escalating | How fast Red layers effects |
| `red_kinetic_authorized` | conditional | off / conditional (after threshold) / on |
| `blue_resilience_loadout` | medium | Proliferation/disaggregation/alt-bearers level |
| `coalition_support` | partial | Allied SDA sharing & political constraints (UK/France/NATO) |
| `escalation_caps` | both_capped | Per-side ceilings on the escalation ladder |
| `time_compression_default` | 60x | Capstone runs long; White Cell rides the throttle |
| `fog_of_war` | realistic_sda | Per-cell visibility |

## Sample injects (a synchronized Red campaign)
- `T+00:00` Cyber on commercial SATCOM ground segment (Viasat-style) — instant, no pass needed.
- `T+00:10` GNSS jamming bubble opens over the theater; Blue precision effects degrade.
- `T+00:30` Red RPO assets begin shadowing Blue GEO SATCOM and missile warning.
- `T+01:00` Directed-energy dazzling of a Blue ISR pass at the decisive moment.
- `T+01:30` (if authorized & threshold crossed) Red signals or employs DA-ASAT → debris +
  political-consequence chain.
- `manual` White Cell injects coalition decisions, OSINT leaks, and ROE changes throughout.

## Victory conditions
- **Blue:** Sustain the space-enabled joint kill chain above the threshold needed to achieve the
  terrestrial objective during the decisive window; defend across all segments; manage escalation
  and preserve coalition support.
- **Red:** Suppress Blue's space-enabled effects below the joint-success threshold during the
  decisive window while keeping its own campaign below the escalation/attribution thresholds that
  would forfeit its objectives.

## Notes for Claude Code
Build this **last** — it requires every subsystem (passes, RPO, EW footprints, cyber-outside-
passes, custody/SDA, debris, escalation/political consequences, per-cell fog) working together.
It is the integration test for the whole engine. Everything Red does here is an orchestrated set
of the same inject/effect primitives the other seven vignettes use individually.
