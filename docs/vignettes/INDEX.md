# Vignettes — Index

[↑ Docs index](../INDEX.md)

The scenario library: a parameter **framework**, the original eight authored vignettes, and a
**four-track library expansion** (mission-set trials, Red COA library, expanded learning stream,
novel concepts) — 19 vignettes total. These are the design documents; the runnable scenarios are
the YAML files in `spacesim/content/vignettes/`. The library architecture lives in
[00-LIBRARY-ARCHITECTURE](00-LIBRARY-ARCHITECTURE.md).

> **Start here:** read [00-LIBRARY-ARCHITECTURE](00-LIBRARY-ARCHITECTURE.md) for the four-track
> design, then dive into individual vignette design notes below.

## Framework & architecture

| Doc | Topic |
|---|---|
| [00-vignette-framework](00-vignette-framework.md) | Vignette framework & parameter schema. |
| [00-LIBRARY-ARCHITECTURE](00-LIBRARY-ARCHITECTURE.md) | Four-track library design, registry, authoring rules. |
| [GROUND-INFRASTRUCTURE](GROUND-INFRASTRUCTURE.md) | Realistic open-source coordinates for ground stations, sensors, jammers, DA-ASAT sites. |

## Original 8 vignettes (design notes)

| Doc | Scenario |
|---|---|
| [01-leo-isr-denial](01-leo-isr-denial.md) | V1 — LEO ISR denial. |
| [02-geo-rpo-shadowing](02-geo-rpo-shadowing.md) | V2 — GEO RPO shadowing. |
| [03-gnss-ew-campaign](03-gnss-ew-campaign.md) | V3 — GNSS / PNT electronic warfare campaign. |
| [04-co-orbital-threat-escort](04-co-orbital-threat-escort.md) | V4 — co-orbital threat & active escort defense. |
| [05-da-asat-crisis](05-da-asat-crisis.md) | V5 — direct-ascent ASAT crisis & escalation. |
| [06-satcom-cyber-link](06-satcom-cyber-link.md) | V6 — SATCOM cyber & link interdiction. |
| [07-sda-custody-hunt](07-sda-custody-hunt.md) | V7 — SDA custody hunt. |
| [08-multi-domain-taiwan](08-multi-domain-taiwan.md) | V8 — multi-domain integrated campaign (capstone). |

## Library expansion — new vignettes (YAML only; design notes inline in each YAML)

| ID | Track | Title |
|---|---|---|
| `mt-isr-sar` | A — mission-set trial | Mission Trial: SAR ISR |
| `mt-sigint-geolocate` | A — mission-set trial | Mission Trial: SIGINT Geolocation |
| `mt-weather-collect` | A — mission-set trial | Mission Trial: Weather Collection |
| `coa-russia-ml` | B — Red COA | Russia ML: Sustained EW Campaign |
| `coa-russia-md` | B — Red COA | Russia MD: DA-ASAT + Cyber Surprise |
| `coa-china-ml` | B — Red COA | China ML: Early Integrated Disruption |
| `coa-china-md` | B — Red COA | China MD: Decisive Counterspace Strike |
| `coa-misc-iran-ml` | B — Red COA | Misc ML (Iran): Regional EW Spoiler |
| `learn-intermediate-recovery` | C — learning | Learning: Safe-Mode Recovery |
| `nv-isl-relay-debris` | D — novel | Novel: ISL Relay + Debris-Corridor Maneuver |

