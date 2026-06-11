# Non-Western Space Control & Orbital Warfare Doctrine

To build a credible Red Cell, the simulator needs the adversary to *think differently*, not
just field mirror-image weapons. This file captures PLA (China) and Russian (VKS) doctrinal
logic and the named programs that should inform Red asset templates.

---

## 1. People's Liberation Army (China)

### Organizational frame
- China created the **PLA Strategic Support Force (PLASSF)** in 2015 to integrate space,
  cyber, and electromagnetic warfare; in **April 2024** it was reorganized and the space
  mission now sits under the **PLA Aerospace Force (PLA ASF)**, reporting directly to the
  Central Military Commission.
- The **PLA Rocket Force** historically controls operationally deployed direct-ascent ASAT
  weapons, while the space organization leads doctrine and on-orbit systems.

### Strategic logic — space as the enabler of US power, therefore the target
The PLA assesses that US military superiority *rests on* space-based C4ISR. Counterspace is
framed as central to **anti-access/area-denial (A2/AD)**: blind and deafen US long-range
kill chains early, ideally before or at the very outset of a conflict (notably over Taiwan).
Key concepts that should shape Red behavior:

- **"Seize the initiative early."** The PLA values striking enabling space systems at the
  *opening* of conflict to maximize disruption to US targeting and comms.
- **Systems-destruction / systems-confrontation warfare** — don't destroy every node; break
  the *system of systems* by hitting the links and key enablers. This favors reversible and
  link-segment effects over wholesale kinetic destruction.
- **Integrated space-cyber-EW.** Because these grew up in one organization, the Red Cell
  should naturally combine a jam + cyber + RPO package rather than treating them separately.

### Named capabilities (use as Red asset templates, publicly reported)
- **Direct-ascent ASAT:** Demonstrated by the 2007 destruction of a defunct Chinese weather
  satellite in LEO (which created a large, long-lived debris cloud — a cautionary data point
  for the sim's debris model). LEO DA-ASAT assessed likely mature; MEO/GEO reach assessed
  developmental.
- **Co-orbital / RPO:** Multiple experimental satellites (e.g., Shijian and Shiyan series)
  observed conducting close approaches and proximity operations in LEO and GEO, including
  closely-spaced maneuvers USSF officials described colloquially as "dogfighting in space"
  (a characterization SWF considers imprecise). Likely on-orbit refueling experiments in
  2025 extend the loiter/endurance picture.
- **Directed energy:** Multiple ground-based lasers able to disrupt/degrade satellite
  sensors, with higher-power damage potential projected for the mid-to-late 2020s.
- **Electronic warfare:** PLA exercises routinely incorporate jammers against satellite
  comms, radars, and GPS-class navigation.

> **Red Cell behavioral signature (China):** Patient SDA and RPO to build custody and
> options; preference for early, reversible, link/EW + cyber effects integrated into a wider
> A2/AD campaign; kinetic DA-ASAT held as a high-end, debris-generating escalation reserved
> for decisive moments.

---

## 2. Russian Federation (VKS)

### Organizational frame
Space forces sit within the **Russian Aerospace Forces (VKS)**, combining air, space, and
air/missile defense. Counterspace is treated as a way to **offset** Western conventional and
aerospace superiority — a continuation of Cold War asymmetric thinking.

### Strategic logic — hedge, offset, and disrupt enabling services
Russian doctrine treats space as critical to modern war and counterspace as a means to
**reduce US/NATO military effectiveness** by degrading the enabling services (PNT, SATCOM,
ISR) on which precision warfare depends. In practice, Russia's *most used* counterspace
tools are non-kinetic EW.

### Named capabilities (Red asset templates, publicly reported)
- **Direct-ascent ASAT — "Nudol" (14Ts033, sometimes associated with the A-235 ABM
  modernization):** Tested repeatedly; in Nov 2021 destroyed a defunct Russian satellite
  (Tselina-D) in LEO, again generating tracked debris.
- **Co-orbital — "Burevestnik" program, supported by "Nivelir" tracking:** Inspector/
  interceptor concepts; **Luch/Olymp-K (2014) and Olymp-K-2 / "Luch-5X" (2023)** conduct
  sustained RPO and close approaches near foreign GEO satellites — useful both for SIGINT
  collection and as latent co-orbital threats. "Nesting-doll" sats that eject sub-satellites have been
  observed in LEO near US assets.
- **Orbital nuclear ASAT (emerging, distinct category):** US, Atlantic Council, and SWF
  open reporting (2024–2026) assesses that Russia is pursuing a **nuclear-detonation-in-orbit
  weapon**, with the Kosmos-2553 (Feb 2022) launch widely reported as a development /
  testbed platform. A high-altitude nuclear burst in LEO would induce trapped-radiation
  belts and persistent EMP/SGEMP effects that would damage or destroy *most* unhardened
  LEO satellites — friendly, neutral, and adversary alike. This is **indiscriminate, not
  window-gated, and ends the space domain for everyone** for months to years; see the
  taxonomy note in `03-counterspace-taxonomy.md` for v1-scope rationale.
- **Directed energy — "Peresvet":** Ground-based laser deployed to strategic missile
  divisions from 2018; assessed able to dazzle/blind optical reconnaissance sensors (likely
  not structurally destructive). "Sokol-Eshelon" airborne laser concept also reported.
- **Electronic warfare (the workhorse):** Mobile systems such as **Tirada-2** (SATCOM
  uplink/downlink jamming) and **Pole-21** / **R-330Zh "Zhitel"** (GNSS jamming/
  suppression). **Bylina (RB-109A)** is an *automated EW command-and-control* system that
  coordinates jammers like the above; the dedicated SATCOM-jamming variant is
  **Bylina-MM** — distinct from RB-109A and easily confused with it in open sources. Used
  pervasively in Ukraine to jam and spoof GPS and degrade Western precision munitions and
  drones, and reportedly to interfere with commercial SATCOM and SAR imaging. This is the
  single most operationally validated counterspace pattern in the data.

> **Red Cell behavioral signature (Russia):** Lead with pervasive, deniable EW (GNSS/SATCOM
> jam & spoof) integrated with ground maneuver; persistent GEO RPO shadowing for intelligence
> and latent threat; directed-energy dazzling of ISR; kinetic DA-ASAT as a strategic
> signaling/escalation option, accepting debris and political cost.

---

## 3. What this means for the simulator's Red Cell

1. **Red is not a mirror of Blue.** Give the Red Cell doctrine-flavored *default postures*
   and *escalation preferences* (selectable by White Cell): "PLA-style early integrated
   disruption" vs. "Russia-style EW-first offset." This is a parameter, not hard-coded.
2. **Non-kinetic first.** Both adversaries' *observed* behavior favors reversible EW/cyber
   and RPO over kinetic strikes. The sim should make non-kinetic effects the common case and
   kinetic strikes rare, costly, and escalatory — matching reality and teaching restraint.
3. **The ground and link segments are the main battleground.** Most real counterspace
   activity is jamming, spoofing, cyber, and proximity — not missiles. The sim's economy of
   effects should reflect that.
4. **Custody and attribution are contested.** Both sides invest in SDA and in deception/
   ambiguity. "Who did that, and can you prove it?" should be a live question, especially for
   RPO and EW.

## Sources

- USCC, *China's Space and Counterspace Capabilities* (2020) and *The Final Frontier:
  China's Ambitions to Dominate Space* (2025).
- ASPI *The Strategist*; CNA, *Deterring China's Use of Force in the Space Domain* (2025).
- Secure World Foundation, *Global Counterspace Capabilities* (2025, 2026).
- Atlantic Council, *Countering Russian Escalation in Space* (2026); CSIS, *Space Threat
  Assessment 2025* and *Extending the Battlespace to Space* (chapter, 2025); Chatham House,
  *Advanced Military Technology in Russia* (2021); *The Space Review* on
  Burevestnik/Peresvet (2020); USSF (HQ Space Force Intelligence) *Space Threat Fact Sheet*
  (2025).
