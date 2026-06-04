# Vignettes — Index

[↑ Docs index](../INDEX.md)

The scenario library: a parameter **framework**, the original eight authored vignettes, and a
**four-track library expansion** (mission-set trials, Red COA library, expanded learning stream,
novel concepts) — 19 vignettes total. These are the framework + architecture references; the
runnable scenarios are the YAML files in `spacesim/content/vignettes/`.

> **The YAML is canonical.** Each vignette YAML now carries an `intro_brief: {blue, red}` block
> that is the authoritative scenario premise, OoB, ROE, and success criteria — surfaced in the
> in-tool **Mission brief** panel (View ▾ → Mission brief, auto-opens on first session load).
> Operator-facing per-cell playbooks live in
> [`../training/11-vignette-playbooks.md`](../training/11-vignette-playbooks.md). The previous
> stub design notes (`01-leo-isr-denial.md` … `08-multi-domain-taiwan.md`) were stale May-2024
> drafts that did not match the implemented YAMLs and have been removed.

## Framework & architecture

| Doc | Topic |
|---|---|
| [00-vignette-framework](00-vignette-framework.md) | Vignette framework & parameter schema. |
| [00-LIBRARY-ARCHITECTURE](00-LIBRARY-ARCHITECTURE.md) | Four-track library design, registry, authoring rules. |
| [GROUND-INFRASTRUCTURE](GROUND-INFRASTRUCTURE.md) | Realistic open-source coordinates for ground stations, sensors, jammers, DA-ASAT sites. |

## All 19 runnable vignettes

The canonical authoring source is the YAML; the operator-facing brief is the YAML's
`intro_brief.{cell}` (Mission brief panel) and the playbook is
[`../training/11-vignette-playbooks.md`](../training/11-vignette-playbooks.md).

### Track — the original 8 (numbered)

| ID | Title | Notes |
|---|---|---|
| `training-basics` | Training: Basics | Onboarding — learn the UI before the eight. |
| `leo-isr-denial` | V1 — LEO ISR Denial | Pass-window gating, reversible denial. |
| `geo-rpo-shadowing` | V2 — GEO RPO Shadowing | Custody decay, ambiguous intent. |
| `gnss-ew-campaign` | V3 — GNSS / PNT EW Campaign | MEO kinetically safe; local PNT bubble. |
| `co-orbital-threat-escort` | V4 — Co-Orbital Threat & Escort | Active escort defense. |
| `da-asat-crisis` | V5 — DA-ASAT Crisis | Kinetic + debris consequence + UN condemnation. |
| `satcom-cyber-link` | V6 — SATCOM Cyber & Link | Off-pass cyber + recovery loop. |
| `sda-custody-hunt` | V7 — SDA Custody Hunt | Sensor contention; break_custody Red. |
| `multi-domain-taiwan` | V8 — Multi-Domain Capstone | Three concurrent objectives — triage. |

### Track A — mission-set trials

| ID | Title |
|---|---|
| `mt-isr-sar` | Mission Trial: SAR ISR |
| `mt-sigint-geolocate` | Mission Trial: SIGINT Geolocation |
| `mt-weather-collect` | Mission Trial: Weather Collection |

### Track B — Red COA library

| ID | Title |
|---|---|
| `coa-russia-ml` | Russia ML: Sustained EW Campaign |
| `coa-russia-md` | Russia MD: DA-ASAT + Cyber Surprise |
| `coa-china-ml` | China ML: Early Integrated Disruption |
| `coa-china-md` | China MD: Decisive Counterspace Strike |
| `coa-misc-iran-ml` | Misc ML (Iran): Regional EW Spoiler |

### Track C — learning stream

| ID | Title |
|---|---|
| `learn-intermediate-recovery` | Learning: Safe-Mode Recovery |

### Track D — novel concepts

| ID | Title |
|---|---|
| `nv-isl-relay-debris` | Novel: ISL Relay + Debris-Corridor Maneuver |
