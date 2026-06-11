# Western Space Control & Orbital Warfare Doctrine

This file summarizes US and allied doctrine so the simulator's action set, victory
conditions, and White Cell language match how Western space forces actually frame the
fight. The governing US documents are *Space Force Doctrine Document 1* (SFDD-1, 2025) and
*Space Warfighting: A Framework for Planners* (2025).

## 1. The core logic: superiority → control → counterspace

US doctrine builds a clean hierarchy the simulator should mirror in its scoring:

- **Space superiority** is the objective: the degree of control that lets friendly forces
  operate at a time and place of their choosing without prohibitive interference, while
  denying the same to the adversary. It is *both* protecting friendly space capabilities
  *and* protecting friendly terrestrial forces from space-enabled attack.
- **Space control** is the core function that produces superiority — "the activities
  required to contest and control the space domain."
- **Counterspace operations** are the offensive and defensive actions that make up space
  control. They are conducted across three **segments**: orbital, link, and terrestrial.

Superiority has dimensions the sim can model as victory conditions:

- **General vs. local** — control everywhere your interests lie vs. control in a bounded
  region/orbital regime.
- **Persistent vs. temporary** — time is no longer a strategic factor vs. control for a
  specific window.
- **Supremacy** = general + persistent. **Denial** = you cannot use the domain freely but
  you can stop the other side from using it either (CSO Saltzman public remarks have
  framed mutual denial as a potentially acceptable end state — e.g., a debris field).

> **Sim implication:** Don't score only "kills." Score *control of an orbital regime over a
> time window for a purpose.* A vignette can be won by temporary local denial without
> destroying anything.

## 2. The three counterspace mission areas (map directly to sim effects)

| Mission area | Segment | Sim effect family |
|---|---|---|
| **Orbital warfare** | Orbital | RPO, escort, pursuit/rendezvous, kinetic/non-kinetic orbital strike |
| **Electromagnetic warfare** | Link | Jamming, spoofing, dazzling, uplink/downlink interdiction |
| **Cyberspace warfare** | Link / Terrestrial | Network attack on TT&C, ground stations, mission data |

## 3. Offensive actions (the Red/Blue offensive menu)

From the *Framework for Planners*:

- **Orbital Strike** — destroy/disrupt/degrade adversary space platforms in orbit. Kinetic
  or non-kinetic, reversible or non-reversible. Two delivery modes the sim must distinguish:
  - **Pursuit** — must rendezvous with the target before weapons employment (needs an
    intercept trajectory and a closing window).
  - **Standoff** — space- or terrestrial-based long-range fires that strike without first
    rendezvousing.
- **Space Link Interdiction** — disrupt/deny/degrade the adversary's critical links via
  **electromagnetic attack** or **cyber-network attack**. Non-kinetic only.
- **Terrestrial Strike** — strike launch vehicles, ground stations, C2 nodes, antennas,
  and ground-based SDA sensors in the land/air/maritime domains. This is how a player
  attacks the *ground segment* — often the cheapest counterspace effect.

## 4. Defensive actions (the Red/Blue defensive menu)

**Active space defense** — direct action against ongoing/imminent attacks:

- **Escort** — dedicated space-to-space protection of a friendly satellite; area or point
  defense.
- **Counterattack** — reactive strike on a force that has shown hostile act/intent
  (terrestrial, orbital, or link counterattack).
- **Suppression of Adversary Counterspace Targeting** — deny the adversary the
  weapons-quality targeting data it needs during an engagement (e.g., blind its SDA).

**Passive space defense** — survivability built into design and operations (these are
*posture settings* the sim should let a defender toggle, each with a cost/benefit):

| Measure | In-sim effect |
|---|---|
| Threat warning | Faster reaction; shrinks attacker surprise |
| Military deception | Degrades attacker's custody/targeting confidence |
| Hardening | Raises kill threshold vs. EMP/radiation/physical |
| Dispersal | Forces attacker to search more locations |
| Disaggregation | Splitting functions across platforms; one kill ≠ full loss |
| Mobility | Maneuver out of an engagement; complicates targeting |
| Redundancy / proliferation | Many small sats instead of one exquisite asset |

> **Sim implication:** Passive defenses are the Blue Cell's pre-game loadout choices and
> in-game posture toggles. They cost fuel, money, or capability and change the probabilities
> the engine resolves against.

## 5. Cross-cutting functions the sim must represent

The *Framework* names enabling functions that become sim subsystems:

- **Lines of communication** — orbits, launch trajectories, and the comm links between
  ground and space. Controlling these is the real prize.
- **Movement and maneuver** — repositioning, RPO, changing orbits, frequency hopping,
  shifting customers between satellites. Maneuver costs **delta-v / fuel**, a hard limit the
  sim must track per asset.
- **Space Domain Awareness (SDA), intelligence, and attribution** — you cannot target what
  you cannot find and characterize. **Custody** (knowing where a thing is right now) and
  **attribution** (knowing who did what) are explicit game states.
- **Command and Control** — decentralized execution; tasked units get latitude. Maps to the
  delegation model between White Cell intent and Red/Blue execution.

## 6. "Responsible" counterspace & escalation

Doctrine stresses **avoiding long-lived debris** and keeping actions proportionate.
Reversible/non-reversible and kinetic/non-kinetic are first-class attributes of every
offensive action. This gives the sim a natural **escalation ladder** and a debris model:

```
Deceive (reversible) → Disrupt → Deny → Degrade → Destroy (debris-generating)
```

These are the **five D's** the sim uses end-to-end (see
`../research/03-counterspace-taxonomy.md`, `../build-spec/01-context-and-scope.md`,
and `spacesim/engine/effects.py`).

> **Sim implication:** Every weapon/effect carries `{reversibility, kinetic?, debris_risk,
> escalation_weight}`. White Cell can score "responsible" play and trigger international/
> political consequences when a player crosses thresholds.

## 7. Allied doctrine (lighter touch, for Blue coalition flavor)

- **United Kingdom** — UK Space Command (est. 2021); national space strategy emphasizes SDA,
  protect-and-defend, and operating as part of a coalition. Conducts cooperative RPO with
  the US.
- **France** — *Commandement de l'Espace* (CDE); a 2019 Space Defence Strategy that
  explicitly contemplates active defense, including reported plans for on-orbit
  "bodyguard"/patrol satellites and dazzling lasers (EGIDE/FLAMHE concepts). France conducts
  cooperative RPO with the US.
- **NATO** — declared space an operational domain (2019); coordinates through a Space Centre
  at Ramstein. NATO's role in the sim is coalition SDA sharing and political escalation
  thresholds rather than independent weapons.

> **Sim implication:** Coalition partners are best modeled as *shared SDA feeds and political
> constraints* on the Blue side, plus a small number of allied assets, rather than full
> independent factions in v1.

## Sources

- USSF, *Space Warfighting: A Framework for Planners* (10 Apr 2025).
- USSF, *Space Force Doctrine Document 1* (Apr 2025).
- Air & Space Forces Magazine; Breaking Defense; DefenseScoop; USNI News reporting on the
  2025 framework (Apr 2025).
- Secure World Foundation, *Global Counterspace Capabilities* (2025, 2026) for allied
  programs.
