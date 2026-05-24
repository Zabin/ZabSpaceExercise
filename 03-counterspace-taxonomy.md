# Counterspace Threat Taxonomy & Effects Model

The simulator's weapon/effect catalog is built on the **Secure World Foundation (SWF)**
five-category taxonomy (used in its annual *Global Counterspace Capabilities* reports), which
is the de-facto open-source standard and aligns cleanly with USSF's orbital/link/terrestrial
segment model. Each category below is written as an **engine effect** with the attributes the
resolver needs.

## The effects spine: the 5 D's

Counterspace effects exist to **deceive, disrupt, deny, degrade, or destroy** a space system.
The sim resolves every offensive action to one of these outcomes, scaled by the escalation
ladder from Western doctrine:

```
deceive ≈ disrupt ≈ deny  (reversible, low debris)
        → degrade          (semi-reversible)
        → destroy          (non-reversible, debris-generating)
```

Every effect template carries a common attribute block:

```yaml
effect_template:
  category:        # direct_ascent | co_orbital | electronic_warfare | directed_energy | cyber
  segment:         # orbital | link | terrestrial
  outcome:         # deceive | disrupt | deny | degrade | destroy
  reversible:      true|false
  kinetic:         true|false
  debris_risk:     none|low|high
  attribution:     overt | ambiguous | covert     # how easily the victim can attribute it
  escalation_weight: 0-10
  access_constraint:   # what physics gates this effect (see orbital primer)
    requires: line_of_sight | rendezvous | uplink_window | ground_access | none
  engagement_time: seconds|minutes|hours  # time to achieve effect once in window
  consumes:        # delta_v, ammo, power, none
```

---

## 1. Direct-Ascent ASAT (DA-ASAT)

A ground/air/sea-launched interceptor that strikes a satellite without being placed in
orbit first. The classic "standoff" kinetic strike in USSF terms.

- **Segment:** orbital (target) launched from terrestrial.
- **Outcome:** destroy (usually); debris_risk: **high**, non-reversible.
- **Access constraint:** target must be within the interceptor's reachable altitude/inclination
  *and* over/near the launch site's engagement geometry at intercept time. LEO is most
  reachable; MEO/GEO require far more capable (and rarer) interceptors.
- **Real templates:** US SM-3 (residual, demonstrated 2008 USA-193); Russia Nudol (2021);
  China DA-ASAT (2007); India Mission Shakti (2019).
- **Sim role:** high-end escalation. Long flight time on the timeline, an unambiguous overt
  act, creates a persistent debris field that can deny an orbital regime to *both* sides.

## 2. Co-Orbital ASAT / RPO

A satellite maneuvered into the same orbital regime as its target to inspect, shadow, grapple,
dazzle, jam from close range, or strike. **Rendezvous & Proximity Operations (RPO)** are the
dual-use enabler — the same maneuver supports inspection, servicing, *or* attack, which is
why **intent and attribution are ambiguous**.

- **Segment:** orbital. **Outcome:** any of the 5 D's depending on payload.
- **Access constraint:** requires a **phasing/transfer trajectory** and **delta-v** to close;
  closing takes hours-to-days in the sim's compressed time, and the approach itself is
  observable by the defender's SDA.
- **Real templates:** US GSSAP (GEO inspection); Russia Luch/Olymp, Burevestnik/Nivelir,
  "nesting-doll" sats; China Shijian/Shiyan series, likely on-orbit refueling.
- **Sim role:** the centerpiece of *orbital warfare* play — shadowing, escort vs. escort,
  the decision of when proximity becomes a threat, and the defender's maneuver-to-evade.

## 3. Electronic Warfare (EW)

Attacks on the **link segment** via the electromagnetic spectrum. The most *operationally
used* counterspace family in the real world.

- **Uplink jamming** — overpower the command/control uplink to a satellite (affects everyone
  using that bird).
- **Downlink jamming** — jam the signal where users receive it (local, e.g., a GPS-denied
  bubble over a battlefield).
- **Spoofing** — inject false signals (false GPS position/time; false telemetry).
- **Segment:** link. **Outcome:** deny/disrupt/deceive. Reversible, debris_risk: none,
  attribution: often **ambiguous** (jamming source must be geolocated).
- **Access constraint:** jammer must have **line of sight / be within the beam footprint**;
  uplink jamming needs to be within the satellite's receive footprint, downlink jamming
  within the victim receiver's vicinity.
- **Real templates:** US Counter Communications System (CCS), Remote Modular Terminal (RMT);
  Russia Tirada-2 (SATCOM), Pole-21 / R-330Zh Zhitel (GNSS); pervasive PLA exercise jamming.
- **Sim role:** the bread-and-butter reversible effect. Cheap, deniable, geographically
  bounded, defeated by frequency hopping / nulling antennas / moving the user.

## 4. Directed Energy (DE)

Lasers, high-power microwave, or RF used to **dazzle** (temporarily blind a sensor),
**degrade**, or — at higher power — **damage** a satellite.

- **Segment:** orbital (target) from terrestrial or space. **Outcome:** disrupt → degrade →
  (high power) destroy. Reversible at low power (dazzle), debris_risk: none-to-low,
  attribution: **covert/ambiguous** (hard for the victim to know it was lased).
- **Access constraint:** **line of sight + clear atmosphere** (ground-based DE is weather-
  and elevation-angle-dependent); target must be above the horizon for the DE site during
  a pass.
- **Real templates:** Russia Peresvet (dazzle), Sokol-Eshelon (airborne); Chinese ground-
  based lasers; reported French EGIDE/FLAMHE on-orbit concepts.
- **Sim role:** the "invisible" effect — degrades an ISR satellite's imagery during a pass
  without obvious attribution, forcing the defender to *infer* an attack from degraded
  product.

## 5. Cyber

Attacks on the **link and terrestrial segments' networks** — ground stations, mission data
systems, and the command path — to intercept, corrupt, hijack, or deny.

- **Segment:** link / terrestrial. **Outcome:** any of the 5 D's, including *hijack* (take
  control). Reversible-ish, debris_risk: none, attribution: **covert** and hardest of all.
- **Access constraint:** requires a **network access vector** (a modeled vulnerability on a
  ground station, TT&C path, or supply chain) rather than orbital geometry — so cyber can
  act *outside* of pass windows, which makes it uniquely flexible in the sim.
- **Real templates:** the Feb 24 2022 Viasat KA-SAT modem attack at the opening of the
  Ukraine invasion is the canonical case (ground/user-segment cyber with strategic effect).
- **Sim role:** the wildcard. Not gated by orbital passes, can produce strategic effect from
  a single successful access, but depends on the defender's cyber posture and may be
  one-shot if the vulnerability is patched.

---

## Effect × Mission-type matrix (which counters bite which targets)

| Target mission ↓ / Effect → | DA-ASAT | Co-orbital/RPO | EW jam/spoof | Directed energy | Cyber |
|---|---|---|---|---|---|
| ISR / imaging (LEO) | destroy | inspect/dazzle/grapple | downlink jam | **dazzle/blind** | corrupt imagery, hijack |
| SIGINT (LEO/GEO) | destroy | shadow/jam-close | uplink jam | degrade | exfil/corrupt |
| GNSS / PNT (MEO) | hard (high alt) | rare (high alt) | **jam/spoof users** | rare | spoof ground monitoring |
| SATCOM (GEO/LEO) | destroy (GEO hard) | shadow/jam-close | **uplink/downlink jam** | degrade | **hijack/deny (Viasat)** |
| Missile warning (GEO/HEO) | destroy (very hard) | shadow | uplink jam | dazzle IR sensor | corrupt alerts |
| Weather/environmental | destroy | inspect | downlink jam | dazzle | corrupt data |
| The attacker's own SDA sensors (ground) | terrestrial strike | — | jam radar | dazzle optics | network attack |

> **Sim implication:** Orbital regime gates which counters are even *available* — LEO targets
> are reachable by everything; GEO/MEO targets are largely safe from kinetic and reachable
> mainly by EW, cyber, RPO, and DE. This is a core teaching point and falls straight out of
> the orbital-mechanics model in the next file.

## Sources

- Secure World Foundation, *Global Counterspace Capabilities* (2025, 2026) — five-category
  taxonomy and program details.
- USSF *Space Warfighting* (2025) — segment model and reversibility framing.
- CSIS *Extending the Battlespace to Space* (2025) — Viasat/Ukraine EW & cyber cases.
- NSSA Space Threat Fact Sheet (2025); SpaceNews; Breaking Defense reporting (2025).
