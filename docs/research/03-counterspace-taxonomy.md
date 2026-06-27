---
last_reviewed: 2026-06-12
primary_sources_consulted: 18
status: stable
---

# Counterspace Threat Taxonomy & Effects Model

[← Research index](INDEX.md) · [↑ Docs index](../INDEX.md) · methodology: [`10-sources-and-methodology.md`](10-sources-and-methodology.md)

This file defines the **counterspace taxonomy** the simulator's effect resolver is built
around — the "five D's" outcome ladder and the five doctrinal **categories** of
counterspace weapon (direct-ascent, co-orbital, electronic warfare, directed energy,
cyber) — and maps each D and each category to the corresponding literal in
[`engine/effects.py`](../../spacesim/engine/effects.py). This file is the **spine**:
per-system depth (specific interceptor classes, specific jammers, specific RPO
maneuvers, specific cyber vectors) lives in the per-class child files
(`03a-da-asat-systems.md`, `03b-coorbital-rpo.md`, `03c-ew-jamming.md`,
`03d-directed-energy.md`, `03e-cyber.md`, `03f-nuclear-emp.md`) authored in Tier 3 of the
[corpus expansion](../FUTURE-WORK.md#125-tier-1--citation-backfill--methodology). When
this file mentions a system at "first name" level the child file carries the per-system
deep-dive with the primary-source numbers.

The taxonomy used here is the **Secure World Foundation five-category scheme**, adopted
in the SWF *Global Counterspace Capabilities* report annually since 2018 and the closest
thing the open-source counterspace community has to a standard
([SWF 2025 Global Counterspace](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
The CSIS *Space Threat Assessment* uses a near-identical scheme
([CSIS STA 2025 PDF](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)),
and the US Space Force / Joint Pub doctrinal frame folds onto it cleanly via the segment
model (orbital / link / terrestrial) discussed in
[`01-doctrine-western.md`](01-doctrine-western.md).

---

## 1. The effects spine — the five D's

Counterspace effects exist to **deceive, disrupt, deny, degrade, or destroy** an
adversary space capability. The "five D's" appear as the operational verbs in
**USSF Spacepower (Capstone) doctrine** (June 2020) and the subsequent **Space Doctrine
Publications** under STARCOM, and predate Spacepower in joint information-operations
doctrine ([Space Capstone Publication, June 2020](https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF);
[SDP 3-104 Electromagnetic Spectrum Operations, 19 September 2025](https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf)).
The framework explicitly orders effects from reversible at the low end to irreversible
at the high end:

```
deceive ≈ disrupt ≈ deny    (reversible; debris-free; minutes-to-hours)
        → degrade            (semi-reversible; performance loss; days)
        → destroy            (irreversible; debris-generating; permanent)
```

This is the same ordering CSIS uses to frame its annual *Space Threat Assessment*
([CSIS STA 2025](https://aerospace.csis.org/space-threat-assessment-2025/)) and is the
ordering the engine's [`Outcome`](../../spacesim/engine/effects.py) literal enumerates.
Each D maps to exactly one literal:

| Five D (doctrine) | `Outcome` literal | Reversibility | Engine semantics |
|---|---|---|---|
| Deceive | `deceive`, `spoof` | reversible | target acts on false belief; appears in `world.active_effects` as a reversible `ActiveEffect` |
| Disrupt | `disrupt` | reversible | temporary link loss or service interruption; `is_link_denied()` returns true during the window |
| Deny | `deny` | reversible | full denial of a service during the window |
| Degrade | `degrade` | semi-reversible | `target.health` flips to `"degraded"`; payload performance reduced until repair |
| Destroy | `destroy` | irreversible | `target.health` flips to `"destroyed"`; if `kinetic`, a `DebrisField` is appended to `world.debris` |

The engine adds two beyond-doctrine literals — `safe_mode` (the bus enters
recovery-strip safe mode, doctrinally a *defensive* outcome an attacker can *induce*; see
[`docs/build-spec/03-safe-mode-loop.md`](../build-spec/03-safe-mode-loop.md)) and
`none` (the action resolved but produced no effect, e.g. the seeker missed). Both are
read by [`ModerateEffectResolver.resolve()`](../../spacesim/engine/effects.py) and emit
the same telemetry shape as a D outcome.

**Doctrinal sourcing of each D.**

- **Deceive.** AFDP 3-13 Information Operations defines deception as "those actions
  executed to deliberately mislead adversary military, paramilitary, or violent extremist
  organization decision-makers" ([AFDP 3-13, 1 February 2023](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-13/3-13-AFDP-INFO-OPS.pdf)).
  In counterspace the canonical case is **GNSS spoofing** — inject false PNT so the
  victim acts on bad position/time. Engine literal: `deceive` and `spoof`. See
  [`is_link_spoofed()`](../../spacesim/engine/effects.py) for the spoof-vs-deny
  distinction (link stays up, content corrupt; an integrity flag must catch it).
- **Disrupt.** Temporary loss of access — a jam burst across a single pass, an outage
  of minutes. Engine literal: `disrupt`. The resolver writes an `ActiveEffect` with
  a finite `[start, end]` window; once `world.now > end` the link is restored.
- **Deny.** Sustained denial of an entire service. The same `ActiveEffect` mechanism
  with a longer window; the difference between disrupt and deny is duration and
  scope, not engine semantics. Engine literal: `deny`.
- **Degrade.** Permanent (or until repair) performance loss without destruction —
  the canonical case is a laser dazzle that scars an optical detector, or sustained
  RF heating that reduces an amplifier's effective output. Engine literal: `degrade`;
  `target.health = "degraded"`.
- **Destroy.** Irrecoverable loss. Engine literal: `destroy`; the resolver
  additionally appends a `DebrisField` and a `political_consequence` side effect when
  the action is `kinetic` with `debris_risk != "none"`.

> **Why "destroy" carries political weight in the engine.** The 2022 US-led moratorium
> on destructive direct-ascent ASAT testing
> ([US State Department / White House fact sheet, 18 April 2022](https://www.state.gov/u-s-national-statement-on-the-international-norm-against-destructive-direct-ascent-anti-satellite-missile-testing/))
> and the follow-on **UNGA Resolution 77/41 (7 December 2022)** — adopted 155-9-9 —
> establish a clear international norm that *destructive* counterspace effects
> generate diplomatic cost beyond the tactical effect
> ([UNGA First Committee vote, 31 October 2022](https://press.un.org/en/2022/gadis3703.doc.htm);
> [SWF *State Positions on the Moratorium*, October 2023](https://www.swfound.org/publications-and-reports/direct-ascent-anti--satellite-missile-tests-state-positions-on-the-moratorium-unga-resolution-and-lessons-for-the-future)).
> The engine's `political_consequence` side effect models this: an irreversible kinetic
> action's escalation cost is *higher than the tactical payoff* in most COA scoring,
> mirroring the doctrinal "reversible-first" preference codified in
> [`07-legal-norms-and-roe.md`](07-legal-norms-and-roe.md) §3.

Used by: [`engine/effects.py:Outcome`](../../spacesim/engine/effects.py) (the literal
union), [`engine/effects.py:ModerateEffectResolver`](../../spacesim/engine/effects.py)
(branch-per-outcome), [`engine/effects.py:is_link_denied`](../../spacesim/engine/effects.py)
and `is_link_spoofed` (the deny-vs-spoof distinction the operator must detect from
integrity telemetry, not link-loss symptoms).

### Sources

- *SWF 2025 Global Counterspace Capabilities Report* — [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2025*, full PDF — [live](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · accessed 2026-06-12.
- *USSF Doctrine Hierarchy Fact Sheet* (Space Capstone Publication, June 2020) —
  [live](https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF)
  · [snapshot](https://web.archive.org/web/2024*/https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF)
  · accessed 2026-06-12.
- *Space Doctrine Publication 3-104 Electromagnetic Spectrum Operations* (STARCOM,
  19 September 2025) — [live](https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf)
  · accessed 2026-06-12.
- *AFDP 3-13 Information Operations* (1 February 2023) — [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-13/3-13-AFDP-INFO-OPS.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-13/3-13-AFDP-INFO-OPS.pdf)
  · accessed 2026-06-12.
- *US State Department statement on the destructive DA-ASAT moratorium*
  (18 April 2022) — [live](https://www.state.gov/u-s-national-statement-on-the-international-norm-against-destructive-direct-ascent-anti-satellite-missile-testing/)
  · [snapshot](https://web.archive.org/web/2023*/https://www.state.gov/u-s-national-statement-on-the-international-norm-against-destructive-direct-ascent-anti-satellite-missile-testing/)
  · accessed 2026-06-12.
- *UN GA First Committee press release on Resolution 77/41* (31 October 2022) —
  [live](https://press.un.org/en/2022/gadis3703.doc.htm)
  · [snapshot](https://web.archive.org/web/2024*/https://press.un.org/en/2022/gadis3703.doc.htm)
  · accessed 2026-06-12.
- *SWF Direct-Ascent ASAT — State Positions on the Moratorium* (October 2023) —
  [live](https://www.swfound.org/publications-and-reports/direct-ascent-anti--satellite-missile-tests-state-positions-on-the-moratorium-unga-resolution-and-lessons-for-the-future)
  · [snapshot](https://web.archive.org/web/2024*/https://www.swfound.org/publications-and-reports/direct-ascent-anti--satellite-missile-tests-state-positions-on-the-moratorium-unga-resolution-and-lessons-for-the-future)
  · accessed 2026-06-12.

---

## 2. Effect × mission-type matrix

The matrix below pairs the five D's with the nine mission types defined in
[`05-mission-types-and-counters.md`](05-mission-types-and-counters.md). Cells name the
**dominant** counter-vs-mission pairing observed in the open record; per-cell rationale
is inline-cited.

| Target mission ↓ / Effect → | DA-ASAT | Co-orbital / RPO | EW jam/spoof | Directed energy | Cyber |
|---|---|---|---|---|---|
| ISR / imaging (LEO) | destroy (FY-1C 2007 ([NASA ODPO Q1 2008](https://orbitaldebris.jsc.nasa.gov/newsletter/pdfs/ODQNv12i1.pdf))) | inspect / shadow ([Kosmos-2542/2543 trailing USA-245, 2019-2020](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)) | downlink jam (X-band TT&C; [CCS Block 10.2 IOC 9 Mar 2020](https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/)) | **dazzle / scar** the focal-plane array (Peresvet-class; *Single source (analyst).* [The Space Review, Hendrickx 2021](https://www.thespacereview.com/article/3967/1)) | corrupt imagery / hijack downlink ([CSIS STA 2025](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)) |
| SIGINT (LEO/GEO) | destroy (Cosmos-1408 was a Tselina-D SIGINT bird; [SWF 2025](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)) | shadow / co-locate ([Luch/Olymp-K at 18.1°W between Intelsat-7 and Intelsat-901, 2015](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)) | uplink jam (S/X-band) | sensor degrade | exfil / corrupt processing chain |
| GNSS / PNT (MEO) | physically hard at ~20,200 km MEO | rare at MEO (no reported Western, Russian, or Chinese co-orbital ASAT operating at MEO; [SWF 2025](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)) | **jam / spoof users** (Pole-21, Tirada-2, NK proliferated jammers; [SWF 2025](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report); [CSIS STA 2025](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)) | rare | spoof ground monitoring, NANU injection |
| SATCOM (GEO/LEO) | destroy is moot at GEO due to altitude reach | shadow / close-jam (Luch/Olymp pattern) | **uplink / downlink jam** (CCS Block 10.2 against C/Ku/X) | degrade amplifier | **hijack / deny — Viasat KA-SAT, 24 Feb 2022** ([Viasat overview](https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/); [SentinelOne *AcidRain* analysis, 31 Mar 2022](https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)) |
| Missile warning (GEO/HEO) | very hard (GEO altitude) | shadow | uplink jam (defeated by relay) | dazzle IR sensor | inject false alerts (highest-escalation cyber case) |
| Weather / environmental | destroy is possible (LEO) | inspect | downlink jam | dazzle | corrupt forecast data |
| White-cell SDA sensors (ground) | terrestrial strike | n/a | jam radar | dazzle optics | network attack |

> **Sim implication.** Orbital regime gates which counters are even *available*. LEO
> targets are reachable by every category; GEO targets are largely safe from kinetic and
> reachable mainly by EW, cyber, RPO, and DE. This single fact — encoded in
> [`engine/access.py`](../../spacesim/engine/access.py)'s per-channel reachability and
> [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py)'s `max_alt_km` field
> — is the core teaching point of the simulator's orbital-mechanics framing.

Used by: [`engine/effects.py:Category`](../../spacesim/engine/effects.py) (the five
categorical literals indexed by this matrix's columns);
[`engine/access.py`](../../spacesim/engine/access.py) (per-channel reachability gates
the rows-to-columns coverage); [`content/vignettes/`](../../spacesim/content/vignettes/)
(the per-mission counter pairings the vignettes script).

### Sources

- *NASA ODPO Quarterly News* (Q1 2008, the FY-1C debris-cloud post-mortem) —
  [live](https://orbitaldebris.jsc.nasa.gov/newsletter/pdfs/ODQNv12i1.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://orbitaldebris.jsc.nasa.gov/newsletter/pdfs/ODQNv12i1.pdf)
  · accessed 2026-06-12.
- *CSIS Aerospace Security, "Unusual Behavior in GEO: Luch/Olymp-K"* —
  [live](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
  · [snapshot](https://web.archive.org/web/2025*/https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
  · accessed 2026-06-12.
- *USSF fact sheet, "Counter Communications System Block 10.2 achieves IOC"*
  (9 March 2020) — [live](https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/)
  · accessed 2026-06-12.
- *Bart Hendrickx, "Peresvet: a Russian mobile laser system to dazzle enemy satellites"*,
  The Space Review (2021) — [live](https://www.thespacereview.com/article/3967/1)
  · [snapshot](https://web.archive.org/web/2024*/https://www.thespacereview.com/article/3967/1)
  · accessed 2026-06-12.
- *Viasat, "KA-SAT Network cyber attack overview"* (30 March 2022) —
  [live](https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/)
  · accessed 2026-06-12.
- *SentinelOne Labs, "AcidRain | A Modem Wiper Rains Down on Europe"* (31 March 2022)
  — [live](https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)
  · accessed 2026-06-12.

---

## 3. Direct-Ascent ASAT (DA-ASAT)

A ground-, air-, or sea-launched interceptor that strikes a satellite without first
being placed in orbit. The defining doctrinal feature is that **the interceptor is on a
sub-orbital trajectory** — it crosses the target's orbital track at one point in space
and time, then falls back — which makes DA-ASAT a precision-timing problem rather than
a sustained orbital presence
([SWF 2025 Global Counterspace](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report);
[CSIS STA 2025](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)).

**Doctrinal segment / outcome.** Segment: orbital (target) launched from terrestrial.
Default `Outcome`: `destroy` (kinetic hit-to-kill); `kinetic=True`,
`debris_risk="high"`, `attribution="overt"`. The 2022 moratorium frames a destructive
DA-ASAT test as a politically-costly category: see §1 above and
[`07-legal-norms-and-roe.md`](07-legal-norms-and-roe.md) §3 for the engine's ROE wiring.

**Reversibility / escalation / attribution profile.** DA-ASAT is the **least reversible**
category in the taxonomy — once the kill vehicle hits, the target is destroyed and the
debris cloud persists for **weeks to decades** depending on altitude. It is also the
**most attributable**: launch is detectable by missile-warning systems, the booster
plume is visible on overhead IR, and the resulting debris field reveals the strike
geometry. The high attribution + high persistence drives the **high escalation weight**
the engine assigns DA-ASAT effects.

**The four open-source test records.** Every DA-ASAT capability claim in the simulator is
sourced to one of four publicly-documented intercepts of a real satellite by an actual
interceptor:

- **SC-19 / DN-3 against Fengyun-1C** (11 January 2007). PRC interceptor impacted the
  defunct 880 kg FY-1C weather satellite at ~865 km altitude at ~9 km/s closing speed.
  By the end of 2007 the USSPACECOM catalog held **>2,500 large tracked fragments** and
  the event was assessed as the most severe deliberate debris-generating event in
  history; cataloged debris from this event still populates the LEO regime at the time
  of writing ([NASA ODPO Quarterly News, Q1 2008](https://orbitaldebris.jsc.nasa.gov/newsletter/pdfs/ODQNv12i1.pdf);
  [SWF 2025 China chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
  Maps to the engine's `mrbm_kkv` interceptor class
  ([engage.py:INTERCEPTORS](../../spacesim/engine/engage.py)) with `max_alt_km: 1000`
  and `base_pk: 0.70`.
- **Operation Burnt Frost (USA-193)** (21 February 2008, 03:26 UTC). USN
  Aegis cruiser USS Lake Erie (CG-70) fired a modified SM-3 against the failing NRO
  USA-193 satellite, intercepting at ~247 km altitude at ~11 km/s closing. The
  intercept was timed so debris reentered within days; the **174 tracked fragments**
  all reentered within ~40 days
  ([Lieber Institute, "Operation Burnt Frost: A View From Inside"](https://www.sciencedirect.com/science/article/abs/pii/S0265964621000035);
  [SWF 2025 US chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
  Maps to `bmd_adapted` (`max_alt_km: 600`, `base_pk: 0.85` — high Pₖ because the SM-3
  was operating well inside its envelope on a cooperative non-maneuvering target).
- **Mission Shakti (Microsat-R)** (27 March 2019). DRDO PDV Mk-II interceptor struck
  the Indian Microsat-R at ~283 km altitude; the deliberately-low target altitude was
  chosen so debris reentered within months
  ([Carnegie, "India's ASAT Test: An Incomplete Success", April 2019](https://carnegieendowment.org/research/2019/04/indias-asat-test-an-incomplete-success?lang=en);
  [SWF 2025 India chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
  Maps to `mrbm_kkv` (same physical envelope as SC-19).
- **Nudol / PL-19 against Cosmos-1408** (15 November 2021). Russian PL-19 Nudol
  interceptor destroyed the 2,000 kg defunct Tselina-D SIGINT satellite at ~480 km
  altitude. USSPACECOM and LeoLabs assessed **>1,500 tracked fragments**; the ISS
  manoeuvred multiple times to dodge the debris over the following 24 months
  ([Carnegie, "The Dangerous Fallout of Russia's Anti-Satellite Missile Test", 16 November 2021](https://carnegieendowment.org/posts/2021/11/the-dangerous-fallout-of-russias-anti-satellite-missile-test?lang=en);
  [IISS, "Russia conducts direct-ascent anti-satellite test", November 2021](https://www.iiss.org/online-analysis/online-analysis/2021/11/russia-conducts-direct-ascent-anti-satellite-test/);
  [SWF 2025 Russia chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
  Maps to `abm_heavy` (`max_alt_km: 2000`, `base_pk: 0.75`).

**Why the engine encodes interceptor *class* and not Δv.** The four-test record makes the
**class** of interceptor (the booster's altitude reach + the kill vehicle's seeker
authority + the salvo-correlation floor of shared track and target-maneuver failure
modes) the dominant variable; operator-typed Δv is a derived value. This is the model
encoded in [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) and
documented in [`docs/AUDIT-2026-06-COMMANDS.md`](../AUDIT-2026-06-COMMANDS.md) §M2;
per-class numbers and the salvo-correlation floor are sourced in
[`03a-da-asat-systems.md`](03a-da-asat-systems.md).

**Sim role.** High-end escalation. Long flight time on the timeline (the engine's
`flyout_s` field, sized at 180-420 s by class), an unambiguous overt act, and the only
category that can deny an entire orbital regime to *both* sides for years. Vignette 5
(DA-ASAT crisis) is built around this category specifically and uses the FY-1C /
Cosmos-1408 debris-persistence record as its in-fiction lesson.

Used by: [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (all four
class entries: `bmd_adapted`, `mrbm_kkv`, `abm_heavy`, `coorbital`);
[`engine/engage.py:kill_probability_from_class`](../../spacesim/engine/engage.py)
(class × altitude × salvo math); [`engine/engage.py:debris_cone_estimate`](../../spacesim/engine/engage.py)
(the "weeks-to-months / years-to-decades / decades" persistence regimes are direct
read-outs of the Burnt-Frost / Cosmos-1408 / FY-1C altitude split).

### Sources

- *NASA ODPO Quarterly News* (Q1 2008, FY-1C post-mortem) —
  [live](https://orbitaldebris.jsc.nasa.gov/newsletter/pdfs/ODQNv12i1.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://orbitaldebris.jsc.nasa.gov/newsletter/pdfs/ODQNv12i1.pdf)
  · accessed 2026-06-12.
- *Operation Burnt Frost: A View From Inside* (Acta Astronautica) —
  [live](https://www.sciencedirect.com/science/article/abs/pii/S0265964621000035)
  · [snapshot](https://web.archive.org/web/2024*/https://www.sciencedirect.com/science/article/abs/pii/S0265964621000035)
  · accessed 2026-06-12.
- *Carnegie Endowment, "India's ASAT Test: An Incomplete Success"* (April 2019) —
  [live](https://carnegieendowment.org/research/2019/04/indias-asat-test-an-incomplete-success?lang=en)
  · [snapshot](https://web.archive.org/web/2024*/https://carnegieendowment.org/research/2019/04/indias-asat-test-an-incomplete-success?lang=en)
  · accessed 2026-06-12.
- *Carnegie Endowment, "The Dangerous Fallout of Russia's Anti-Satellite Missile Test"*
  (16 November 2021) — [live](https://carnegieendowment.org/posts/2021/11/the-dangerous-fallout-of-russias-anti-satellite-missile-test?lang=en)
  · [snapshot](https://web.archive.org/web/2024*/https://carnegieendowment.org/posts/2021/11/the-dangerous-fallout-of-russias-anti-satellite-missile-test?lang=en)
  · accessed 2026-06-12.
- *IISS, "Russia conducts direct-ascent anti-satellite test"* (November 2021) —
  [live](https://www.iiss.org/online-analysis/online-analysis/2021/11/russia-conducts-direct-ascent-anti-satellite-test/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.iiss.org/online-analysis/online-analysis/2021/11/russia-conducts-direct-ascent-anti-satellite-test/)
  · accessed 2026-06-12.
- *SWF 2025 Global Counterspace Capabilities Report* (per-country chapters) —
  [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-06-12.

---

## 4. Co-orbital ASAT / Rendezvous-and-Proximity Operations (RPO)

A satellite manoeuvred into the **same orbital regime** as its target to inspect,
shadow, grapple, dazzle from close range, jam from close range, or strike. Crucially,
the same physical capability (the bus, the propulsion, the proximity sensors) supports
all of inspect, service, *and* attack — which is why
[**intent and attribution are ambiguous**](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
in the open record. The engine encodes this category as
`Category="co_orbital"` with `attribution="ambiguous"` as the default.

**Doctrinal segment / outcome.** Segment: orbital. Outcome: any of the five D's
depending on payload (an RPO satellite carrying an optical inspector achieves
`deceive`/`disrupt`; one carrying a grappler or kill vehicle achieves `degrade`/
`destroy`). The engine's `coorbital` interceptor class explicitly carries
`reversible_option: True` — co-orbital can tow a target to a graveyard orbit rather
than impact it, which is a lower-escalation outcome than a destructive hit
([engage.py:INTERCEPTORS["coorbital"]](../../spacesim/engine/engage.py)).

**Reversibility / escalation / attribution profile.** RPO is the **most ambiguous**
counterspace category. Approach manoeuvres are observable to SDA — the defender's
[GSSAP](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197772/geosynchronous-space-situational-awareness-program/)
or commercial trackers like [LeoLabs](https://leolabs.space/) or ExoAnalytic see the
phasing — but the **payload at the end** of the approach is opaque. A close approach
might be an inspection (legal under the OST), an eavesdropping co-location (a Luch/Olymp
behaviour), a tug operation (an SJ-21 behaviour), or a prepositioned grappler. The
defender's response calculus depends on this attribution-ambiguity gap, which is exactly
what the simulator's belief-vs-truth split forces the trainee to reason about.

**Named examples.**

- **GSSAP (US, geosynchronous belt)** — first pair launched 28 July 2014; current
  constellation of four operates "near the geosynchronous belt … capable of performing
  Rendezvous and Proximity Operations" supporting USSPACECOM
  ([USSF GSSAP fact sheet](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197772/geosynchronous-space-situational-awareness-program/)).
  The Western canonical RPO platform; doctrinally an inspector, technically capable of
  any RPO payload.
- **Luch / Olymp-K (Russia, GEO)** — launched 27 September 2014; moved to 18.1°W in
  2015 and parked between [Intelsat-7 and Intelsat-901](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/),
  reportedly closing to within ~5 km of an Intelsat satellite. Has since visited 19
  distinct GEO slots in 11 years per CSIS Aerospace Security tracking
  ([CSIS Aerospace, "Unusual Behavior in GEO"](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)).
  The canonical SIGINT-shadowing RPO.
- **Burevestnik / Nivelir "nesting doll" satellites (Russia, LEO)** — Project 14K167
  Nivelir launches a host satellite which deploys a smaller inspector subsatellite,
  which has on at least one occasion ejected a high-speed projectile (Cosmos-2543 /
  Cosmos-2542 / Cosmos-2535 sequence, 2017-2020). The Kosmos-2542/2543 pair was
  inserted into the orbital plane of the US KH-11 reconnaissance satellite USA-245
  in 2020 and made repeated close approaches
  ([SWF Russian Co-orbital Anti-satellite Testing Fact Sheet, June 2025](https://www.swfound.org/publications-and-reports/russian-co-orbital-anti-satellite-testing-fact-sheet);
  [CSIS STA 2025 Russia chapter](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)).
  *Single source (analyst).* Per-projectile attribution rests on a small analyst
  community (SWF, CSIS, Bart Hendrickx); Russian sources have not confirmed the
  projectile ejection.
- **Shijian-21 / Beidou-G2 tug (China, GEO)** — Shijian-21 (launched 24 October 2021)
  approached and docked with the defunct **Beidou-2 G2** satellite in late
  December 2021; on 22 January 2022 it executed a large burn that placed Beidou-2 G2
  **~3,000 km above the GEO belt** — well beyond the standard ~300 km graveyard —
  then undocked on 26 January 2022
  ([SpaceNews, 27 January 2022](https://spacenews.com/chinas-shijian-21-spacecraft-docked-with-and-towed-a-dead-satellite/);
  [Breaking Defense, 27 January 2022](https://breakingdefense.com/2022/01/chinas-sj-21-tugs-dead-satellite-out-of-geo-belt-trackers/)).
  The first publicly-documented operational tug; demonstrates the reversible-co-orbital
  pattern (move, not destroy) that the engine's `reversible_option` flag encodes.

**Engine mapping.** Category literal: `co_orbital`. Interceptor class for co-orbital
kinetic intercepts: `coorbital` (no `max_alt_km` — the bus phases to wherever it needs
to be; `base_pk: 0.60` set by RPO custody, not endgame homing). Per-mission RPO numbers
(closing rates, sensor cones, propellant budgets for typical phasing manoeuvres) live
in [`03b-coorbital-rpo.md`](03b-coorbital-rpo.md).

**Sim role.** The centerpiece of *orbital warfare* play — shadowing, escort vs. escort,
the decision of when proximity becomes a threat, the defender's maneuver-to-evade. The
SJ-21 case in particular teaches the **reversible escalation** lesson: the actor that
*tugs* rather than *hits* preserves the option to recover, and the defender's response
calculus changes accordingly.

Used by: [`engine/engage.py:INTERCEPTORS["coorbital"]`](../../spacesim/engine/engage.py)
(the no-altitude-ceiling, reversible-option co-orbital class);
[`engine/effects.py:Category="co_orbital"`](../../spacesim/engine/effects.py);
[`engine/orders.py`](../../spacesim/engine/orders.py) (`rpo` access channel gating
RPO-class effects on `rpo_proximity` window).

### Sources

- *USSF GSSAP fact sheet* — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197772/geosynchronous-space-situational-awareness-program/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197772/geosynchronous-space-situational-awareness-program/)
  · accessed 2026-06-12.
- *CSIS Aerospace Security, "Unusual Behavior in GEO: Luch/Olymp-K"* —
  [live](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
  · [snapshot](https://web.archive.org/web/2025*/https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
  · accessed 2026-06-12.
- *SWF Russian Co-orbital Anti-satellite Testing Fact Sheet* (June 2025) —
  [live](https://www.swfound.org/publications-and-reports/russian-co-orbital-anti-satellite-testing-fact-sheet)
  · [snapshot](https://web.archive.org/web/2025*/https://www.swfound.org/publications-and-reports/russian-co-orbital-anti-satellite-testing-fact-sheet)
  · accessed 2026-06-12.
- *SpaceNews, "China's Shijian-21 spacecraft docked with and towed a dead satellite"*
  (27 January 2022) — [live](https://spacenews.com/chinas-shijian-21-spacecraft-docked-with-and-towed-a-dead-satellite/)
  · [snapshot](https://web.archive.org/web/2024*/https://spacenews.com/chinas-shijian-21-spacecraft-docked-with-and-towed-a-dead-satellite/)
  · accessed 2026-06-12.
- *Breaking Defense, "China's SJ-21 'tugs' dead satellite out of GEO belt"*
  (27 January 2022) — [live](https://breakingdefense.com/2022/01/chinas-sj-21-tugs-dead-satellite-out-of-geo-belt-trackers/)
  · [snapshot](https://web.archive.org/web/2024*/https://breakingdefense.com/2022/01/chinas-sj-21-tugs-dead-satellite-out-of-geo-belt-trackers/)
  · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2025* — [live](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · accessed 2026-06-12.

---

## 5. Electronic Warfare (EW)

Attacks on the **link segment** via the electromagnetic spectrum. Doctrinally,
counterspace EW falls under the broader joint **Electromagnetic Spectrum Operations**
umbrella ([SDP 3-104, 19 September 2025](https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf)),
and SWF's 2025 assessment makes the load-bearing observation that EW is the
**most operationally-used** counterspace family in active conflicts — the only
category that has been used in every armed conflict since 2014
([SWF 2025](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report);
[CSIS STA 2025](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)).

**Sub-types (doctrinal).**

- **Uplink jamming** — overpower the command/control uplink to a satellite, denying
  every user on the bird, not just one ground site. Wide blast radius. The canonical
  US capability is the **Counter Communications System Block 10.2** (CCS Block 10.2),
  declared IOC 9 March 2020 — explicitly the Space Force's "first offensive weapon
  system" ([USSF CCS Block 10.2 IOC announcement](https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/);
  [SpaceNews, "U.S. Space Force declares 'offensive' communications jammer ready"](https://spacenews.com/u-s-space-force-declares-offensive-communications-jammer-ready-for-deployment/)).
  CCS is **uplink-only** — a doctrinally important choice that is captured in the
  engine by `jam.link_target ∈ {uplink, downlink, crosslink}`
  ([docs/AUDIT-2026-06-COMMANDS.md §N9](../AUDIT-2026-06-COMMANDS.md)).
- **Downlink jamming** — jam the receiver where users *consume* the signal. Local in
  effect (a GPS-denied bubble over a city), wide in deployment (every receiver in the
  bubble is denied). The Russian **Pole-21** networked jammer is the canonical
  large-scale downlink-denial system: dozens of jam nodes deployed on cellular masts to
  form a regional GNSS-denial network, first observed in occupied Luhansk in early 2019
  ([TASS, on Pole-21 entering service](https://tass.com/defense/1088451);
  [SWF 2025 Russia chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
- **Spoofing** — inject false signals so the receiver acts on a corrupted PNT solution
  or corrupted command. GNSS spoofing in and around conflict zones is now pervasive;
  CSIS STA 2025 catalogs the 2024 GPS spoofing incidents in the Black Sea, the
  eastern Mediterranean, and around Kaliningrad
  ([CSIS STA 2025](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)).
- **SATCOM jam from space** — the **Tirada-2** programme has been in development since
  ~2001; the system is reported as a **ground-based SATCOM-jammer** explicitly designed
  to suppress communications satellites
  ([SWF 2025 Russia chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report);
  [Kyiv Post, "Ukrainian Special Ops Report Destruction of Russian 'Tirada-2'", May 2024](https://www.kyivpost.com/post/26469)).
  A separate **Bylina-MM** acquisition is reported but less well-documented.

**Doctrinal segment / outcome.** Segment: link. Outcome: `deny`, `disrupt`, `deceive`
(spoof); never `destroy`. Reversible (the link comes back when the jammer turns off or
the victim moves). `debris_risk: none`. Attribution typically **ambiguous** — the
jamming source must be geolocated before it can be attributed, which is the SIGINT
problem [`engine/sigint.py`](../../spacesim/engine/sigint.py) encodes.

**Engine encoding.** The four jam modulations in
[`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py) — `barrage`, `spot`,
`sweep`, `deceptive` — capture the dominant tactical EW decisions an operator makes.
The defender's **frequency-hop modifier** in [`engine/effects.py`](../../spacesim/engine/effects.py)
(`_FREQ_HOP_RESIDUAL = 0.4`) is sourced to the protected-waveform processing-gain
literature on AEHF/Milstar nulling antennas: 20-30 dB of anti-jam processing typically
leaves ~0.4× residual success for the attacker. Per-modulation numbers and per-system
deep-dives live in [`03c-ew-jamming.md`](03c-ew-jamming.md).

**Reversibility / escalation / attribution.** EW is the **bread-and-butter reversible**
effect. Cheap (a jammer is a fraction of a satellite's cost), deniable (geolocation is
nontrivial and contested), geographically bounded (the jam footprint is finite), and
defeated by frequency hopping, nulling antennas, or moving the user
([SWF 2025](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
Escalation weight is **low** in the engine's scoring — this is the default
"reversible-first" counterspace effect Western doctrine prefers
([07-legal-norms-and-roe.md](07-legal-norms-and-roe.md) §3).

Used by: [`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py) (the four-modulation
database); [`engine/effects.py:_FREQ_HOP_RESIDUAL`](../../spacesim/engine/effects.py)
(defender-side modifier sourced to the protected-waveform literature);
[`engine/effects.py:Category="electronic_warfare"`](../../spacesim/engine/effects.py);
[`engine/sigint.py:geolocation_error_km`](../../spacesim/engine/sigint.py)
(the geolocation problem that gates attribution of a jamming source).

### Sources

- *SWF 2025 Global Counterspace Capabilities Report* — [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2025* — [live](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · accessed 2026-06-12.
- *SDP 3-104 Electromagnetic Spectrum Operations* (19 September 2025) —
  [live](https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf)
  · accessed 2026-06-12.
- *USSF CCS Block 10.2 IOC announcement* (9 March 2020) —
  [live](https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/)
  · accessed 2026-06-12.
- *SpaceNews, "U.S. Space Force declares 'offensive' communications jammer ready for deployment"* —
  [live](https://spacenews.com/u-s-space-force-declares-offensive-communications-jammer-ready-for-deployment/)
  · [snapshot](https://web.archive.org/web/2024*/https://spacenews.com/u-s-space-force-declares-offensive-communications-jammer-ready-for-deployment/)
  · accessed 2026-06-12.
- *TASS, "Latest jamming system arrives for electronic warfare troops"* (on Pole-21) —
  [live](https://tass.com/defense/1088451)
  · [snapshot](https://web.archive.org/web/2024*/https://tass.com/defense/1088451)
  · accessed 2026-06-12.
- *Kyiv Post, "Ukrainian Special Ops Report Destruction of Russian 'Tirada-2' Satcom Jamming System"*
  (May 2024) — [live](https://www.kyivpost.com/post/26469)
  · [snapshot](https://web.archive.org/web/2024*/https://www.kyivpost.com/post/26469)
  · accessed 2026-06-12.

---

## 6. Directed Energy (DE)

Lasers, high-power microwave (HPM), or focused RF used to **dazzle** (temporarily blind
a sensor), **degrade** (scar a detector / heat an amplifier), or — at higher power —
**damage** a satellite. The lowest-power application (dazzle) is reversible and leaves
no debris; the highest-power application (sustained burn) overlaps with destructive
DA-ASAT in effect.

**Doctrinal segment / outcome.** Segment: orbital target from terrestrial (today's
operational systems are all ground-based) or potentially space (rumored on-orbit
concepts). Outcome ladder: `disrupt` → `degrade` → at very high power, `destroy`.
Reversible at low power (dazzle), not reversible at high power (scarred focal plane).
`debris_risk: none-to-low`. Attribution: **covert/ambiguous** — the victim sensor sees
"this pass returned bad imagery", not "I was lased", and must *infer* an attack from
the degradation pattern.

**Named examples.**

- **Peresvet (Russia)** — Russian president Vladimir Putin announced the system on
  1 March 2018; it entered "experimental combat duty" on 1 December 2018 and full
  service in December 2019. Mobile truck-mounted laser. *Single source (analyst).*
  Hendrickx assesses the system could "blind satellites orbiting at altitudes up to
  1,500 km" — but the assessment rests primarily on a single analyst piece in
  *The Space Review*; Russian sources confirm only the system's existence and not its
  anti-satellite capability
  ([Bart Hendrickx, "Peresvet: a Russian mobile laser system to dazzle enemy satellites", The Space Review, 2021](https://www.thespacereview.com/article/3967/1);
  [SWF 2025 Russia chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report);
  [Breaking Defense, "Don't be dazzled by Russia's laser weapons claims", May 2022](https://breakingdefense.com/2022/05/dont-be-dazzled-by-russias-laser-weapons-claims-experts/)).
- **Chinese ground-based laser facilities** — SWF and CSIS assess multiple PRC
  ground-based laser sites with counterspace dazzle/degrade potential, including
  facilities in Xinjiang
  ([SWF 2025 China chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report);
  [CSIS STA 2025 China chapter](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)).
  *Single source (analyst).* Capability assessment is open-source IMINT-derived;
  no publicly-confirmed dazzle event has been attributed to a Chinese facility.

**Access constraint.** DE requires **line of sight + clear atmosphere**. Ground-based
DE is weather- and elevation-angle-dependent; the target must be above the horizon for
the DE site during a pass. The simulator gates DE effects on the
`sensor_observation` access channel (line-of-sight is the same physics for "I can see
you" as for "I can lase you") in
[`engine/access.py`](../../spacesim/engine/access.py).

**Engine encoding.** Category literal: `directed_energy`. Default attribution
`covert`. The engine treats a sustained DE engagement as either `disrupt` (during the
pass) or `degrade` (post-pass health flip), with the operator's reported power level
gating which outcome is reachable. Per-system DE numbers (power, beam divergence,
atmospheric-transmission models) live in [`03d-directed-energy.md`](03d-directed-energy.md).

**Sim role.** The "invisible" effect — degrades an ISR satellite's imagery during a
pass without obvious attribution, forcing the defender to *infer* an attack from
degraded product. Vignette 4 (ISR-DE) is built around this category.

Used by: [`engine/effects.py:Category="directed_energy"`](../../spacesim/engine/effects.py);
[`engine/access.py`](../../spacesim/engine/access.py) (line-of-sight gate).

### Sources

- *Bart Hendrickx, "Peresvet: a Russian mobile laser system to dazzle enemy satellites"*,
  The Space Review (2021) — [live](https://www.thespacereview.com/article/3967/1)
  · [snapshot](https://web.archive.org/web/2024*/https://www.thespacereview.com/article/3967/1)
  · accessed 2026-06-12.
- *Breaking Defense, "Don't be dazzled by Russia's laser weapons claims: Experts"*
  (May 2022) — [live](https://breakingdefense.com/2022/05/dont-be-dazzled-by-russias-laser-weapons-claims-experts/)
  · [snapshot](https://web.archive.org/web/2024*/https://breakingdefense.com/2022/05/dont-be-dazzled-by-russias-laser-weapons-claims-experts/)
  · accessed 2026-06-12.
- *SWF 2025 Global Counterspace Capabilities Report*, China and Russia chapters —
  [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2025*, China chapter — [live](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · accessed 2026-06-12.

---

## 7. Cyber

Attacks on the **link and terrestrial segments' networks** — ground stations, mission
data systems, modem networks, and the command path — to intercept, corrupt, hijack,
or deny. Doctrinally cyber is the **only** category not gated by orbital geometry:
once an access vector is established, the effect can be triggered at any time, from
anywhere with network connectivity ([SWF 2025](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report);
[CSIS STA 2025](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)).

**Doctrinal segment / outcome.** Segment: link / terrestrial. Outcome: any of the five
D's, plus the engine-only `safe_mode` (the attacker triggers the bus's own recovery
strip) and `seize_c2` (the attacker issues legitimate-looking management commands from
a compromised gateway — the Viasat pattern). `debris_risk: none`. Attribution:
**covert** by default — the hardest to attribute of all categories.

**The canonical case: Viasat KA-SAT, 24 February 2022.** At ~05:00 UTC on the day
Russia invaded Ukraine, a wiper malware later named **AcidRain** (by SentinelOne Labs)
was pushed to ~tens of thousands of Viasat KA-SAT consumer modems from a compromised
management plane. Spillover affected ~5,800 Enercon wind turbines in Germany that
relied on KA-SAT for remote telemetry
([Viasat's own incident overview, 30 March 2022](https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/);
[SentinelOne, "AcidRain", 31 March 2022](https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)).
In May 2022 the US, EU, UK, and the Five Eyes formally attributed the attack to the
GRU — one of the largest formal cyber-attribution events to date. The case is the
load-bearing precedent for the engine's `ground_modem` cyber vector in
[`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py)
([docs/AUDIT-2026-06-COMMANDS.md §C2](../AUDIT-2026-06-COMMANDS.md)).

**Why cyber is the engine's "wildcard."** Cyber is the **only** category not gated by
the access-channel windows in [`engine/access.py`](../../spacesim/engine/access.py).
Every other category requires a window:

- DA-ASAT and co-orbital require an `engagement` or `rpo_proximity` window.
- EW requires the jammer to be in the victim's beam footprint (`jam_footprint`).
- DE requires line-of-sight (`sensor_observation` gate).

Cyber requires only a modeled **access vector** on the target — a vulnerability
sitting in the `cyber_vulnerabilities` list on the `Asset` or on its `GroundSite`. The
trade-off the engine balances: cyber has the highest flexibility, but it depends on the
defender's cyber posture (the `_POSTURE_FACTOR` map in
[`effects.py`](../../spacesim/engine/effects.py): low=1.25×, medium=1.0×, high=0.6×)
and a vulnerability that has been **patched** zeros the vector. A successful cyber
attack can be "one-shot" — once the vulnerability is patched, the access vector is
closed.

**Five vectors, five payloads.** [`engine/cyber.py`](../../spacesim/engine/cyber.py)
encodes five access vectors (`rf`, `supply_chain`, `insider`, `ground_segment`,
`ground_modem`) and four payloads (`data_exfil`, `wiper`, `spoof`, `dwell`) plus the
audit-added `seize_c2` payload for the Viasat-style legitimate-command pattern. The
`supply_chain` vector is the **least-patchable** (its persistence is set at 24 hours
minimum because pulling a firmware push is operationally hard); `rf` is the
**most-patchable** (0.5 hours minimum because the link can be cut). Per-vector numbers
and per-payload deep-dives live in [`03e-cyber.md`](03e-cyber.md).

**Sim role.** The wildcard. Not gated by orbital passes, can produce strategic effect
from a single successful access (the Viasat case denied tactical SATCOM to Ukraine on
the opening day of the war), but depends on the defender's cyber posture and may be
one-shot if the vulnerability is patched. Vignette 6 (SATCOM cyber-link) is built
around this category specifically.

Used by: [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) (the five-vector
database, including the `ground_modem` vector sourced to the Viasat KA-SAT case);
[`engine/cyber.py:PAYLOADS`](../../spacesim/engine/cyber.py) (the four-plus-`seize_c2`
payload database); [`engine/effects.py:_POSTURE_FACTOR`](../../spacesim/engine/effects.py)
(defender-posture modifier on cyber `success_prob`);
[`engine/effects.py:Category="cyber"`](../../spacesim/engine/effects.py).

### Sources

- *Viasat, "KA-SAT Network cyber attack overview"* (30 March 2022) —
  [live](https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/)
  · accessed 2026-06-12.
- *SentinelOne Labs, "AcidRain | A Modem Wiper Rains Down on Europe"* (31 March 2022)
  — [live](https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)
  · accessed 2026-06-12.
- *CCDCOE Cyber Law Toolkit, "Viasat KA-SAT attack (2022)"* —
  [live](https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))
  · [snapshot](https://web.archive.org/web/2024*/https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))
  · accessed 2026-06-12.
- *SWF 2025 Global Counterspace Capabilities Report*, cyber sections —
  [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2025*, cyber sections — [live](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · accessed 2026-06-12.

---

## 8. Nuclear / EMP (deferred to `03f-nuclear-emp.md`; out of scope for v1 effect catalog)

A nuclear detonation in orbit — a category the open-source community refers to as
"nuclear ASAT" — is **legally prohibited** by Outer Space Treaty Article IV: "States
Parties to the Treaty undertake not to place in orbit around the Earth any objects
carrying nuclear weapons or any other kinds of weapons of mass destruction, install
such weapons on celestial bodies, or station such weapons in outer space in any other
manner" ([OST text via UNOOSA](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html);
[Arms Control Association, "Outer Space Treaty at a Glance"](https://www.armscontrol.org/factsheets/outer-space-treaty-glance)).
The OST entered into force on 10 October 1967 and has 115 States Parties.

Despite the treaty prohibition, public reporting since early 2024 has discussed an
**alleged** Russian space-based nuclear-ASAT development programme (sometimes referred
to as "Burevestnik-K" in open sources, though the naming is contested). The
international-law framing of the alleged programme is discussed in
[Lieber Institute, "Russia's Alleged Nuclear Anti-Satellite Weapon"](https://lieber.westpoint.edu/russias-nuclear-anti-satellite-weapon-international-law/).
*Single source (analyst).* The capability assessment rests on US-government public
statements and a small analyst community; no Russian source has confirmed the
programme.

**Why the simulator excludes orbital-nuclear from the effect catalog (v1).** A nuclear
detonation in LEO has three properties that make it incompatible with a
gameplay-style escalation choice:

1. **Indiscriminate.** A nuclear detonation in LEO damages friendly, neutral, and
   adversary satellites alike via prompt radiation (X-ray, gamma) and the longer-term
   radiation-belt pumping that takes months-to-years to dissipate.
2. **Not window-gated.** The detonation is not a per-pass event; once the radiation
   belts are pumped, the regime is degraded for everyone for the duration.
3. **No reversible variant.** Unlike every other category, there is no low-escalation
   "test" version of an orbital nuclear weapon.

The canonical Vignette 5 (DA-ASAT crisis) already teaches the
"denial-of-the-regime-to-both-sides" lesson at a smaller, tractable scale, so the
simulator does not need orbital-nuclear in the effect catalog to teach the lesson.
White Cell may discuss it as an injected geopolitical event without it being a
player-issuable order. Per-technology nuclear-EMP depth lives in
[`03f-nuclear-emp.md`](03f-nuclear-emp.md).

Used by: [`engine/effects.py:Category`](../../spacesim/engine/effects.py) (explicitly
**does not** include a `nuclear` literal; the omission is doctrinal, not an oversight);
[`07-legal-norms-and-roe.md`](07-legal-norms-and-roe.md) §1 (OST Article IV as the
legal frame).

### Sources

- *Outer Space Treaty text, UNOOSA* — [live](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)
  · [snapshot](https://web.archive.org/web/2024*/https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)
  · accessed 2026-06-12.
- *Arms Control Association, "The Outer Space Treaty at a Glance"* —
  [live](https://www.armscontrol.org/factsheets/outer-space-treaty-glance)
  · [snapshot](https://web.archive.org/web/2024*/https://www.armscontrol.org/factsheets/outer-space-treaty-glance)
  · accessed 2026-06-12.
- *Lieber Institute West Point, "Russia's Alleged Nuclear Anti-Satellite Weapon: International Law and Political Rhetoric"* —
  [live](https://lieber.westpoint.edu/russias-nuclear-anti-satellite-weapon-international-law/)
  · [snapshot](https://web.archive.org/web/2024*/https://lieber.westpoint.edu/russias-nuclear-anti-satellite-weapon-international-law/)
  · accessed 2026-06-12.

---

## 9. The effect-template attribute block (engine schema)

Every effect template the simulator loads carries the attribute block below, which maps
onto [`EffectInstance`](../../spacesim/engine/effects.py) at runtime:

```yaml
effect_template:
  category:        # direct_ascent | co_orbital | electronic_warfare | directed_energy | cyber
  segment:         # orbital | link | terrestrial
  outcome:         # deceive | disrupt | deny | degrade | destroy | safe_mode | spoof
  reversible:      true|false
  kinetic:         true|false
  debris_risk:     none|low|high
  attribution:     overt | ambiguous | covert
  escalation_weight: 0-10
  access_constraint:
    requires: line_of_sight | rendezvous | uplink_window | ground_access | none
  engagement_time: seconds | minutes | hours
  consumes:        delta_v | ammo | power | none
```

The five fields that matter most for resolution semantics — `category`, `outcome`,
`reversible`, `kinetic`, `debris_risk` — are the same five fields the resolver branches
on in [`ModerateEffectResolver.resolve()`](../../spacesim/engine/effects.py). The
`attribution` field drives the `attribution_signal` side effect's confidence.

Used by: [`engine/effects.py:EffectInstance`](../../spacesim/engine/effects.py) (the
schema this YAML maps to); [`content/vignette.py`](../../spacesim/content/vignette.py)
(the loader that reads YAML effect templates from
[`content/vignettes/`](../../spacesim/content/vignettes/)).

---

## 10. Cross-references

- **Engine literals.** [`engine/effects.py:Outcome`](../../spacesim/engine/effects.py)
  and [`engine/effects.py:Category`](../../spacesim/engine/effects.py) — the union
  types this file is the spine for.
- **DA-ASAT class database.** [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py)
  — sourced to the four open-source DA-ASAT tests (§3).
- **EW modulation database.** [`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py)
  — sourced to the SWF/CSIS EW assessments (§5).
- **Cyber vector database.** [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py)
  — sourced to the Viasat KA-SAT case for `ground_modem` (§7).
- **Per-class depth files** (Tier 3 deliverables, in authoring queue):
  [`03a-da-asat-systems.md`](03a-da-asat-systems.md),
  [`03b-coorbital-rpo.md`](03b-coorbital-rpo.md),
  [`03c-ew-jamming.md`](03c-ew-jamming.md),
  [`03d-directed-energy.md`](03d-directed-energy.md),
  [`03e-cyber.md`](03e-cyber.md),
  [`03f-nuclear-emp.md`](03f-nuclear-emp.md).
- **Doctrine + ROE.** [`01-doctrine-western.md`](01-doctrine-western.md) (the segment
  model + reversibility framing); [`02-doctrine-non-western.md`](02-doctrine-non-western.md)
  (CN/RU counterspace organization); [`07-legal-norms-and-roe.md`](07-legal-norms-and-roe.md)
  (OST Article IV, the 2022 moratorium, UNGA 77/41, the engine's ROE flags).
- **Mission counters.** [`05-mission-types-and-counters.md`](05-mission-types-and-counters.md)
  — the per-mission counter matrix this file's §2 is the column-key for.
- **Audit predecessor.** [`docs/AUDIT-2026-06-COMMANDS.md`](../AUDIT-2026-06-COMMANDS.md)
  — the commands-layer audit that produced the interceptor-class model (§M2), the
  defender-side modifiers (§C1), and the `ground_modem` cyber vector (§C2) cited
  throughout.
- **Research encyclopedia.** [`encyclopedia/R310-effects-based-operations.md`](encyclopedia/R310-effects-based-operations.md) (this file's five-D taxonomy is its cited engine-mapping source); [`encyclopedia/R115-electronic-warfare-in-space-operations.md`](encyclopedia/R115-electronic-warfare-in-space-operations.md), [`encyclopedia/R116-cyber-operations-against-space-systems.md`](encyclopedia/R116-cyber-operations-against-space-systems.md), [`encyclopedia/R117-directed-energy-and-kinetic-effects.md`](encyclopedia/R117-directed-energy-and-kinetic-effects.md) (the implementation-focused counterparts to §5/§7/§3-4); [`encyclopedia/R504-future-space-warfare-concepts.md`](encyclopedia/R504-future-space-warfare-concepts.md) (forward-looking extensions beyond this file's current five-D scope).

*Last reviewed: 2026-06-12. Pending review: every 12 months from `last_reviewed`.*
