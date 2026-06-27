---
last_reviewed: 2026-06-12
primary_sources_consulted: 40
status: stable
---

# Non-Western Space Control & Orbital Warfare Doctrine

[← Research index](INDEX.md) · [↑ Docs index](../INDEX.md) · methodology: [`10-sources-and-methodology.md`](10-sources-and-methodology.md)

To build a credible Red Cell, the simulator needs the adversary to *think
differently*, not just field mirror-image weapons. This file captures the PLA
(China) and VKS (Russia) doctrinal logic and the named programs that should
inform Red asset templates and the `session/redai.py` doctrine presets. The
order matches Western intelligence-analysis convention: §1–§3 PLA (organizational
frame → strategic logic → named capabilities), §4–§6 VKS (same triple), §7 what
this means for the Red Cell, §8 cross-references. Per-actor depth at higher
fidelity lives in the Tier 2 deliverables [`02a-doctrine-china.md`](02a-doctrine-china.md)
and [`02b-doctrine-russia.md`](02b-doctrine-russia.md), queued in
[`FUTURE-WORK.md` §12.5.2](../FUTURE-WORK.md#1252-tier-2--per-mission-and-per-actor-deep-dives);
the parallel Western treatment that this file is the foil to lives in
[`01-doctrine-western.md`](01-doctrine-western.md). The 2022 UNGA 77/41
moratorium "no" votes (China, Russia, Belarus, Iran, Cuba, Nicaragua, Syria,
Bolivia, CAR) plus the abstentions of India and Pakistan are the empirical
"who resists" check on the Western doctrinal frame — see
[`07-legal-norms-and-roe.md` §3](07-legal-norms-and-roe.md) for the
treaty-substrate treatment.

---

## 1. PLA — organizational frame (post-April-2024 reorganization)

In **April 2024** the PLA dissolved the [Strategic Support Force (SSF), established 31 December 2015](https://www.airuniversity.af.edu/CASI/) (the SSF had been the integrated space + cyber + EW + psychological-operations service since the Xi-era reform) and replaced it with **three coequal services** reporting directly to the Central Military Commission ([Center for Strategic and International Studies, "China's New Aerospace Force," ChinaPower, 2024](https://chinapower.csis.org/), [Mulvenon & Stokes / CASI public reports on the reorganization](https://www.airuniversity.af.edu/CASI/)). The three are:

- **PLA Aerospace Force (ASF / 中国人民解放军航天部队)** — inheritor of the SSF Space Systems Department; carries the orbital-launch, on-orbit, SDA, and counterspace missions ([DoD *Military and Security Developments Involving the People's Republic of China 2024 Annual Report*](https://media.defense.gov/2024/Dec/18/2003583935/-1/-1/0/MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA-2024.PDF) p. 49 et seq.).
- **PLA Cyberspace Force (CSF / 网络空间部队)** — cyber + EW + counterspace-cyber.
- **PLA Information Support Force (ISF / 信息支援部队)** — network + C4ISR support; Xi Jinping personally presided over the ISF inauguration ceremony on 19 April 2024, signalling its priority ([CSIS ChinaPower coverage of the 19 April ceremony](https://chinapower.csis.org/); [CASI, "PLA Information Support Force," 2024](https://www.airuniversity.af.edu/CASI/)).

The **PLA Rocket Force (PLARF)** continues to operate the deployed direct-ascent ASAT systems (SC-19, DN-3) — the launch-and-engage side — while the ASF runs the doctrine, on-orbit force, and SDA / weapons-quality-track piece ([SWF *Global Counterspace Capabilities 2025*, China chapter](https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)). This split — RF operates DA-ASAT, ASF operates inspectors / SDA — is exactly the kind of inter-service seam the simulator's Red Cell exposes when the White Cell runs a `china_integrated` doctrine preset.

Used by: [`session/redai.py`](../../spacesim/session/redai.py) (`china_integrated` Red doctrine preset that encodes the integrated-counterspace COA pattern); [`content/vignettes/`](../../spacesim/content/vignettes/) COA-style vignettes that pit Red ASF + RF assets against Blue.

### Sources

- *CSIS ChinaPower — China's New Aerospace Force (2024)* — [live](https://chinapower.csis.org/) · [snapshot](https://web.archive.org/web/2026*/https://chinapower.csis.org/) · accessed 2026-06-12.
- *CASI — China Aerospace Studies Institute (Air University)* — [live](https://www.airuniversity.af.edu/CASI/) · [snapshot](https://web.archive.org/web/2026*/https://www.airuniversity.af.edu/CASI/) · accessed 2026-06-12.
- *DoD — Military and Security Developments Involving the PRC, 2024 Annual Report (CMPR)* — [live](https://media.defense.gov/2024/Dec/18/2003583935/-1/-1/0/MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA-2024.PDF) · [snapshot](https://web.archive.org/web/2026*/https://media.defense.gov/2024/Dec/18/2003583935/-1/-1/0/MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA-2024.PDF) · accessed 2026-06-12.
- *Secure World Foundation — 2025 Global Counterspace Capabilities Report (China chapter)* — [live](https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report) · [snapshot](https://web.archive.org/web/2026*/https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report) · accessed 2026-06-12.

---

## 2. PLA — strategic logic (space as US-enabler, therefore target)

The PLA assesses that US military superiority *rests on* space-based C4ISR + PNT + SATCOM. Counterspace is framed as central to the **anti-access / area-denial (A2/AD)** envelope: blind and deafen US long-range kill chains early, ideally before or at the very outset of a conflict — notably over Taiwan ([Andrew Erickson, *Chinese Anti-Access / Area Denial*, 2017 + ongoing scholarship at andrewerickson.com](https://www.andrewerickson.com/); [CASI translations of PLA writings](https://www.airuniversity.af.edu/CASI/)). The doctrine that frames counterspace inside A2/AD is publicly named:

- **"Seize the initiative early."** The PLA *Science of Military Strategy* (2013 and 2020 editions, translated by [RAND and CASI](https://www.rand.org/pubs/research_reports/RR1462.html)) consistently values striking enabling space systems at the *opening* of conflict to maximize disruption to US targeting and comms before US forces can reorient.
- **Systems-destruction / systems-confrontation warfare (体系破击战 / 体系对抗战).** Don't try to destroy every node; break the *system of systems* by hitting the links and the key enablers ([RAND, *China's Quest for Greatness in the Space Era*, 2021](https://www.rand.org/pubs/external_publications/EP68543.html); [CSIS Space Threat Assessment 2025](https://www.csis.org/analysis/space-threat-assessment-2025) Chinese-doctrine section). This favours reversible and link-segment effects over wholesale kinetic destruction — which is why the public counterspace record is overwhelmingly EW + cyber + RPO, not kinetic ASAT.
- **Integrated space-cyber-EW.** Because these grew up in one organization (the SSF, now split across ASF + CSF + ISF — see §1), the Red Cell should naturally combine a jam + cyber + RPO package rather than treating them separately ([CSIS Space Threat Assessment 2024](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) on integrated PLA counterspace exercises).

The pedagogical implication for the simulator: Red Cell on a `china_integrated` doctrine preset should *not* fire DA-ASAT first. It should patient-watch the Blue ISR / GPS / SATCOM order of battle through Red SDA / SIGINT, jam and cyber against the link segment, RPO-shadow high-value Blue GEO assets, and reserve kinetic effects for decisive moments where the political cost is justified.

Used by: [`session/redai.py`](../../spacesim/session/redai.py) (`china_integrated` doctrine preset); the [`engine/effects.py:political_consequence`](../../spacesim/engine/effects.py) dial that prices PLA-style restraint into the scoring.

### Sources

- *Andrew Erickson — Chinese counterspace strategy scholarship* — [live](https://www.andrewerickson.com/) · [snapshot](https://web.archive.org/web/2026*/https://www.andrewerickson.com/) · accessed 2026-06-12.
- *RAND — China's Quest for Greatness in the Space Era (Cheng, 2021)* — [live](https://www.rand.org/pubs/external_publications/EP68543.html) · [snapshot](https://web.archive.org/web/2026*/https://www.rand.org/pubs/external_publications/EP68543.html) · accessed 2026-06-12.
- *RAND — China's Future SSF Counterspace Mission (2017)* — [live](https://www.rand.org/pubs/research_reports/RR1462.html) · [snapshot](https://web.archive.org/web/2026*/https://www.rand.org/pubs/research_reports/RR1462.html) · accessed 2026-06-12.
- *CSIS — Space Threat Assessment 2024* — [live](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) · [snapshot](https://web.archive.org/web/2026*/https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) · accessed 2026-06-12.
- *CSIS — Space Threat Assessment 2025* — [live](https://www.csis.org/analysis/space-threat-assessment-2025) · [snapshot](https://web.archive.org/web/2026*/https://www.csis.org/analysis/space-threat-assessment-2025) · accessed 2026-06-12.

---

## 3. PLA — named capabilities (Red asset templates)

The PLA's publicly-acknowledged or strongly-attributed counterspace capabilities. Each maps to a Red asset-template slot in vignettes plus an entry in [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (kinetic kill vehicles), [`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py) (RF jammers), or [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) (cyber access vectors).

### 3.1 Direct-ascent kinetic ASAT
**SC-19 / DN-3** — kinetic direct-ascent ASAT family operated by PLA Rocket Force. SC-19 destroyed the defunct Fengyun-1C weather satellite at ~860 km on **11 January 2007**, generating ~3,000 tracked debris objects — the largest debris-generating ASAT test on record ([SWF *Global Counterspace 2024*, China §1.1](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf); [CSIS Space Threat Assessment 2024](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf)). DN-3 is the assessed higher-altitude follow-on with MEO-reach development testing observed since 2013 ([SWF 2024](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)). The kinetic-debris precedent is the reason PRC is one of the nine "no" votes on UNGA 77/41 (see [`07-legal-norms-and-roe.md` §3](07-legal-norms-and-roe.md)).

### 3.2 Co-orbital RPO / inspector class
**Shijian (SJ / 实践) and Yaogan (YG / 遥感) series** — operational inspector and characterization birds. The canonical case is **Shijian-21**: in January 2022, [SJ-21 docked with the defunct BeiDou G-2 navigation satellite at GEO, towed it ~3,000 km above the GEO belt to a graveyard orbit, then returned](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) ([SWF *2026 Global Counterspace Capabilities*](https://www.swfound.org/publications-and-reports/2026-global-counterspace-capabilities-report); CSIS STA 2024 §3.1). **Shijian-17** demonstrated GEO RPO from 2017 onward; **Shijian-23** and the **TJS (Tongxin Jishu Shiyan / 通信技术试验)** series sit at GEO conducting characterization passes that Western SSA tracks as inspector activity ([SWF 2025](https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)). USSF officials have publicly described GEO close-approach manoeuvres as "dogfighting in space" ([Air & Space Forces Magazine, 2024](https://www.airandspaceforces.com/) coverage of USSF Saltzman testimony), a characterization SWF treats as imprecise but evocative.

### 3.3 SIGINT and ELINT
**Yaogan triplets** — formations of three LEO satellites flying in coordinated geometry, assessed (open-source) to perform TDOA / FDOA SIGINT against terrestrial emitters ([SWF 2024](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf); [CSIS Aerospace Security space-based SIGINT context](https://aerospace.csis.org/aerospace101/national-security-space-organizations/)). The constellation has grown to dozens of triplets since 2010. Engine: the geolocation-error math in [`engine/sigint.py:geolocation_error_km`](../../spacesim/engine/sigint.py) (scaling √dwell × √N collectors) is the abstract model behind these triplet operations.

### 3.4 Ground-based directed energy
PLA operates **ground-based lasers assessed capable of dazzling LEO ISR optics** during a sun-synchronous pass; the higher-power damaging-class capability is projected for the mid-to-late 2020s ([DoD CMPR 2024](https://media.defense.gov/2024/Dec/18/2003583935/-1/-1/0/MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA-2024.PDF); [CSIS STA 2025](https://www.csis.org/analysis/space-threat-assessment-2025)). The publicly-named site is at Korla in Xinjiang; per the same DoD assessment the PRC operates an "advanced" set that includes mobile units. Engine: this maps to the dazzle effect category in [`engine/effects.py:Category`](../../spacesim/engine/effects.py) gated against EO/IR ISR payload types.

### 3.5 Ground-based RF jammers (counter-PNT and counter-SATCOM)
PLA exercises routinely include ground-based jammers against GPS and SATCOM uplinks/downlinks ([SWF 2024, China §1.3](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf); [DoD CMPR 2024](https://media.defense.gov/2024/Dec/18/2003583935/-1/-1/0/MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA-2024.PDF) §IV). Engine: maps to [`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py) (barrage / spot / sweep / deceptive entries).

### 3.6 Cyber counterspace
PRC-attributed actors (notably APT41 / Winnti) have targeted satellite ground-segment infrastructure and commercial satellite operators ([Mandiant *M-Trends* APT41 reporting](https://cloud.google.com/security/resources/m-trends); [CSIS *Significant Cyber Incidents* tracker](https://www.csis.org/programs/strategic-technologies-program/significant-cyber-incidents) entries on PRC-attributed satellite-operator intrusions). Engine: maps to [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) (the cyber access-vector database) and the cyber-induced safe-mode loop documented in [`06-bus-and-payload-operations.md` §2.5](06-bus-and-payload-operations.md).

Used by: [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (`mrbm_kkv` entry for SC-19/DN-3); [`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py) (jammer types); [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) (cyber access vectors); [`engine/effects.py:Category`](../../spacesim/engine/effects.py) (dazzle / EW / cyber); [`engine/sigint.py:geolocation_error_km`](../../spacesim/engine/sigint.py) (Yaogan-triplet SIGINT math); Red asset templates in [`content/vignettes/`](../../spacesim/content/vignettes/).

### Sources

- *SWF — Global Counterspace Capabilities 2024 (China §1)* — [live](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf) · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf) · accessed 2026-06-12.
- *SWF — 2025 Global Counterspace Capabilities Report* — [live](https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report) · [snapshot](https://web.archive.org/web/2026*/https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report) · accessed 2026-06-12.
- *SWF — 2026 Global Counterspace Capabilities Report* — [live](https://www.swfound.org/publications-and-reports/2026-global-counterspace-capabilities-report) · [snapshot](https://web.archive.org/web/2026*/https://www.swfound.org/publications-and-reports/2026-global-counterspace-capabilities-report) · accessed 2026-06-12.
- *CSIS — Space Threat Assessment 2024* — [live](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) · [snapshot](https://web.archive.org/web/2026*/https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) · accessed 2026-06-12.
- *DoD — Military and Security Developments Involving the PRC 2024* — [live](https://media.defense.gov/2024/Dec/18/2003583935/-1/-1/0/MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA-2024.PDF) · [snapshot](https://web.archive.org/web/2026*/https://media.defense.gov/2024/Dec/18/2003583935/-1/-1/0/MILITARY-AND-SECURITY-DEVELOPMENTS-INVOLVING-THE-PEOPLES-REPUBLIC-OF-CHINA-2024.PDF) · accessed 2026-06-12.
- *Mandiant — M-Trends (APT41 / satellite-operator targeting)* — [live](https://cloud.google.com/security/resources/m-trends) · [snapshot](https://web.archive.org/web/2026*/https://cloud.google.com/security/resources/m-trends) · accessed 2026-06-12.
- *CSIS — Significant Cyber Incidents tracker* — [live](https://www.csis.org/programs/strategic-technologies-program/significant-cyber-incidents) · [snapshot](https://web.archive.org/web/2026*/https://www.csis.org/programs/strategic-technologies-program/significant-cyber-incidents) · accessed 2026-06-12.

---

## 4. VKS — organizational frame

Russian space forces sit within the **Russian Aerospace Forces (VKS / Воздушно-космические силы)**, established 1 August 2015 by merging the Russian Air Force (VVS) and the Russian Aerospace Defence Forces (VVKO) ([SWF *Global Counterspace Capabilities 2024*, Russia §1](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf); [Atlantic Council, *Countering Russian Escalation in Space*, 2024](https://www.atlanticcouncil.org/in-depth-research-reports/report/countering-russias-counterspace-capabilities/)). The VKS combines:

- **VKO (Войска воздушно-космической обороны)** — Aerospace Defence Troops handling missile warning and space surveillance.
- **VVS (Военно-воздушные силы)** — Air Force.
- **Space Troops (Космические войска / KV)** — a sub-component within VKS that operates the satellite-launch + on-orbit force from Plesetsk Cosmodrome.

The **RVSN (Ракетные войска стратегического назначения / Strategic Rocket Forces)** sits *separately* from VKS and historically operates the deployed direct-ascent ASAT (Nudol / A-235 ABM modernisation context) — same RF / Space-force seam as the PLA RF / ASF split, and the same simulator implication.

Russia's commercial-civilian space arm **Roscosmos** is formally separate but has deep military integration: Roscosmos operates the launch infrastructure (Plesetsk + Vostochny + Baikonur lease) the VKS depends on, and key launches are dual-use ([SWF 2024 Russia §1](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf); [Chatham House, *Advanced Military Technology in Russia*, 2021](https://www.chathamhouse.org/2021/09/advanced-military-technology-russia)).

Used by: [`session/redai.py`](../../spacesim/session/redai.py) (`russia_ew_first` Red doctrine preset).

### Sources

- *SWF — Global Counterspace Capabilities 2024 (Russia §1)* — [live](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf) · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf) · accessed 2026-06-12.
- *Atlantic Council — Countering Russia's Counterspace Capabilities (2024)* — [live](https://www.atlanticcouncil.org/in-depth-research-reports/report/countering-russias-counterspace-capabilities/) · [snapshot](https://web.archive.org/web/2026*/https://www.atlanticcouncil.org/in-depth-research-reports/report/countering-russias-counterspace-capabilities/) · accessed 2026-06-12.
- *Chatham House — Advanced Military Technology in Russia (2021)* — [live](https://www.chathamhouse.org/2021/09/advanced-military-technology-russia) · [snapshot](https://web.archive.org/web/2026*/https://www.chathamhouse.org/2021/09/advanced-military-technology-russia) · accessed 2026-06-12.

---

## 5. VKS — strategic logic (hedge, offset, disrupt enabling services)

Russian doctrine treats space as critical to modern war and counterspace as a means to **reduce US/NATO military effectiveness** by degrading the enabling services (PNT, SATCOM, ISR) on which precision warfare depends ([Bart Hendrickx, *The Space Review* on Burevestnik / Peresvet / Nivelir, 2020](https://www.thespacereview.com/article/3956/1); [SWF 2024 Russia §2](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)). Three doctrinal threads:

- **Asymmetric offset.** Russia cannot match US conventional dominance ship-for-ship or satellite-for-satellite; counterspace is the offset tool. The doctrinal lineage is Cold War "operational manoeuvre" thinking re-applied to the space domain ([Chatham House 2021](https://www.chathamhouse.org/2021/09/advanced-military-technology-russia)).
- **Hedge — keep options open across the escalation ladder.** Russia fields the *full* counterspace menu — EW + cyber + RPO + DA-ASAT + the [emerging orbital nuclear capability widely-reported as Kosmos-2553](https://www.csis.org/analysis/russias-nuclear-anti-satellite-weapons-program) — to retain options at every rung from deniable jamming up to strategic signalling ([CSIS Space Threat Assessment 2025](https://www.csis.org/analysis/space-threat-assessment-2025) Russia chapter; [Atlantic Council 2024](https://www.atlanticcouncil.org/in-depth-research-reports/report/countering-russias-counterspace-capabilities/)).
- **Disrupt enabling services as a routine peacetime posture.** Unlike the PLA's "wait for the opening of conflict" framing, Russian EW against Western SATCOM and GPS has been *continuously active* in the Ukraine theatre since February 2022, and pre-2022 in Syria ([CSIS STA 2024, Russia §2](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf) on persistent Russian EW; [Breaking Defense / CSIS commentary on Russian jamming of Starlink terminals](https://breakingdefense.com/2026/04/as-more-nations-seek-counterspace-chops-gps-jamming-also-rises-report/)).

The pedagogical implication for the simulator: Red Cell on a `russia_ew_first` doctrine preset should *lead* with pervasive deniable EW (counter-GPS bubbles, SATCOM uplink jam) integrated with ground manoeuvre; persistent GEO RPO shadowing for intelligence and latent threat; directed-energy dazzling of ISR; kinetic DA-ASAT as a strategic signalling/escalation option, accepting debris and political cost.

Used by: [`session/redai.py`](../../spacesim/session/redai.py) (`russia_ew_first` doctrine preset); [`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py) (Russian EW workhorse modulations).

### Sources

- *Bart Hendrickx, "Russia's secret satellite builders" series, The Space Review (2020)* — [live](https://www.thespacereview.com/article/3956/1) · [snapshot](https://web.archive.org/web/2026*/https://www.thespacereview.com/article/3956/1) · accessed 2026-06-12.
- *CSIS — Russia's Nuclear Anti-Satellite Weapons Program* — [live](https://www.csis.org/analysis/russias-nuclear-anti-satellite-weapons-program) · [snapshot](https://web.archive.org/web/2026*/https://www.csis.org/analysis/russias-nuclear-anti-satellite-weapons-program) · accessed 2026-06-12.
- *Breaking Defense, "As More Nations Seek Counterspace Chops, GPS Jamming Also Rises"* — [live](https://breakingdefense.com/2026/04/as-more-nations-seek-counterspace-chops-gps-jamming-also-rises-report/) · [snapshot](https://web.archive.org/web/2026*/https://breakingdefense.com/2026/04/as-more-nations-seek-counterspace-chops-gps-jamming-also-rises-report/) · accessed 2026-06-12.

---

## 6. VKS — named capabilities (Red asset templates)

The publicly-acknowledged or strongly-attributed Russian counterspace capabilities, mapped to engine surfaces.

### 6.1 Direct-ascent kinetic ASAT — Nudol / A-235
**14Ts033 "Nudol"** is the Russian ground-launched direct-ascent ASAT, associated with the **A-235** ABM modernisation programme. Nudol destroyed the defunct Soviet-era **Tselina-D (Kosmos 1408)** at ~480 km on **15 November 2021**, generating an estimated [~1,500 tracked debris objects](https://www.state.gov/russia-conducts-destructive-anti-satellite-missile-test/) ([U.S. State Department statement](https://www.state.gov/russia-conducts-destructive-anti-satellite-missile-test/); [SWF 2024 Russia §1.1](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)). Russia is one of the nine UNGA 77/41 "no" votes (see [`07-legal-norms-and-roe.md` §3](07-legal-norms-and-roe.md)).

### 6.2 Co-orbital RPO — Luch / Olymp-K and the Burevestnik / Nivelir family
**Luch / Olymp-K (2014)** and **Olymp-K-2 / "Luch-5X" (March 2023)** conduct sustained RPO and close approaches near foreign GEO satellites, primarily for SIGINT collection and latent co-orbital threat ([Bart Hendrickx, *The Space Review*, 2020](https://www.thespacereview.com/article/3956/1); [SWF 2024 Russia §2](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)). The **Burevestnik / Nivelir / Numizmat** LEO programme has produced "nesting-doll" satellite ejections (Kosmos-2491/2499/2504, the Kosmos-2519/2521/2523 triple in 2017, Kosmos-2542/2543 in 2019-2020 — the latter "synchronised orbits with the US KH-11 USA 245" per [CSIS STA 2020](https://aerospace.csis.org/space-threat-assessment-2020/)).

### 6.3 The emerging orbital nuclear capability
A new and distinct category. US, [Atlantic Council 2024](https://www.atlanticcouncil.org/in-depth-research-reports/report/countering-russias-counterspace-capabilities/), [CSIS 2024](https://www.csis.org/analysis/russias-nuclear-anti-satellite-weapons-program), and SWF open reporting (2024-2026) assess that Russia is pursuing a **nuclear-detonation-in-orbit weapon**, with the [Kosmos-2553 launch on 5 February 2022](https://www.csis.org/analysis/russias-nuclear-anti-satellite-weapons-program) widely reported as a development / testbed platform. A high-altitude nuclear burst in LEO would induce trapped-radiation belts and persistent EMP / SGEMP effects that would damage or destroy *most* unhardened LEO satellites — friendly, neutral, and adversary alike. The capability is **indiscriminate, not window-gated, and ends the LEO domain for everyone** for months to years; the simulator deliberately defers modelling it (see [`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md) scope rationale).

### 6.4 Directed energy — Peresvet
**Peresvet (Пересвет)** is a ground-based laser deployed to strategic missile divisions from 2018, publicly named by President Putin in his March 2018 Federal Assembly address ([Hendrickx, *Space Review* 2020](https://www.thespacereview.com/article/3956/1); [SWF 2024 Russia §4](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)). Assessed able to **dazzle / blind optical reconnaissance sensors** during a sun-synchronous pass; structurally-destructive damage not assessed. The airborne **"Sokol-Eshelon"** laser concept has also been reported.

### 6.5 Electronic warfare — the workhorse
Mobile systems that have done the bulk of observed Russian counterspace activity:

- **Tirada-2** — SATCOM uplink/downlink jamming ([SWF 2024 Russia §3](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)).
- **Pole-21 / Pole-21M** — GNSS jamming, deployed in fixed mast networks.
- **R-330Zh "Zhitel"** — mobile GNSS jamming/suppression.
- **Bylina (RB-109A)** — automated EW command-and-control system that coordinates jammers like the above; the dedicated SATCOM-jamming variant is **Bylina-MM** (distinct from RB-109A and easily confused with it in open sources) ([Hendrickx, *Space Review* 2020](https://www.thespacereview.com/article/3956/1)).
- **Tobol** — anti-SATCOM electronic warfare system, fixed sites near Russian satellite ground stations ([Washington Post 2023 Discord-leak reporting on Tobol confirmed by SWF 2024](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)).
- **Krasukha-4** — air-defence-focused EW with documented effects on SAR ISR returns.

This is the single most operationally validated counterspace pattern in the open-source record. EW has been used *pervasively in Ukraine* to jam and spoof GPS and degrade Western precision munitions and drones, and reportedly to interfere with commercial SATCOM and SAR imaging ([CSIS STA 2024 Russia §2](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf); [Breaking Defense 2026](https://breakingdefense.com/2026/04/as-more-nations-seek-counterspace-chops-gps-jamming-also-rises-report/)).

### 6.6 Cyber counterspace
The [**Viasat KA-SAT cyber/EW outage of 24 February 2022**](https://www.csis.org/analysis/cyberattack-viasats-ka-sat-network) (AcidRain wiper against ~30,000 European modems) is the canonical Russian-attributed counterspace cyber operation. Engine: maps to [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) (ground-segment access vector) + the cyber-induced safe-mode pattern in [`06-bus-and-payload-operations.md` §2.5](06-bus-and-payload-operations.md).

Used by: [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (`abm_heavy` entry for Nudol/A-235); [`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py) (the Russian EW workhorse modulations); [`engine/effects.py:Category="directed_energy"`](../../spacesim/engine/effects.py) (Peresvet dazzle); [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) (Viasat-style ground-segment cyber); Red asset templates in [`content/vignettes/`](../../spacesim/content/vignettes/).

### Sources

- *U.S. State Department — Russia Conducts Destructive Anti-Satellite Missile Test (15 Nov 2021)* — [live](https://www.state.gov/russia-conducts-destructive-anti-satellite-missile-test/) · [snapshot](https://web.archive.org/web/2026*/https://www.state.gov/russia-conducts-destructive-anti-satellite-missile-test/) · accessed 2026-06-12.
- *Bart Hendrickx, "Burevestnik: a Russian Air-Launched Anti-Satellite System," The Space Review (2020)* — [live](https://www.thespacereview.com/article/3956/1) · [snapshot](https://web.archive.org/web/2026*/https://www.thespacereview.com/article/3956/1) · accessed 2026-06-12.
- *CSIS — Space Threat Assessment 2020 (Kosmos-2542/2543 + USA 245 synchronisation)* — [live](https://aerospace.csis.org/space-threat-assessment-2020/) · [snapshot](https://web.archive.org/web/2026*/https://aerospace.csis.org/space-threat-assessment-2020/) · accessed 2026-06-12.
- *CSIS — Cyberattack on Viasat's KA-SAT Network* — [live](https://www.csis.org/analysis/cyberattack-viasats-ka-sat-network) · [snapshot](https://web.archive.org/web/2026*/https://www.csis.org/analysis/cyberattack-viasats-ka-sat-network) · accessed 2026-06-12.

---

## 7. What this means for the simulator's Red Cell

The doctrine sections above produce four design implications:

1. **Red is not a mirror of Blue.** Give the Red Cell doctrine-flavoured *default postures* and *escalation preferences* (selectable by White Cell): the `china_integrated` preset for PLA-style early integrated disruption (§§1–3) vs. the `russia_ew_first` preset for Russia-style EW-first offset (§§4–6). This is a parameter, not hard-coded. Engine: [`session/redai.py`](../../spacesim/session/redai.py).
2. **Non-kinetic first.** Both adversaries' *observed* behaviour favours reversible EW + cyber + RPO over kinetic strikes. The simulator should make non-kinetic effects the common case and kinetic strikes rare, costly, and escalatory — matching reality and teaching restraint. Engine: [`engine/effects.py:political_consequence`](../../spacesim/engine/effects.py) prices the kinetic step asymmetrically (see [`01-doctrine-western.md` §6](01-doctrine-western.md) for the parallel Western framing).
3. **The ground and link segments are the main battleground.** Most real counterspace activity is jamming, spoofing, cyber, and proximity — not missiles. The economy of effects should reflect that. Engine: the [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) cyber exception (not access-gated; [`CLAUDE.md`](../../CLAUDE.md) "Five effect categories → five D's" subsection) is the simulator's encoding of why ground-segment attacks are the fast/flexible option.
4. **Custody and attribution are contested.** Both sides invest in SDA and in deception/ambiguity. "Who did that, and can you prove it?" is a live question, especially for RPO and EW. Engine: [`engine/custody.py:Track.is_weapons_quality()`](../../spacesim/engine/custody.py) and [`engine/cyber.py:attribution_score`](../../spacesim/engine/cyber.py) implement the asymmetry.

### Sources

- *USSF — Space Threat Fact Sheet 2025* — [live](https://www.spaceforce.mil/News/Article/) · [snapshot](https://web.archive.org/web/2026*/https://www.spaceforce.mil/) · accessed 2026-06-12. *Single source (analyst).* — USSF fact-sheet URL searched but not surfaced by WebSearch in this pass; cited from the prior research file's Sources block pending fix in the adversarial verification pass.
- *USCC — China's Space and Counterspace Capabilities (2020) and The Final Frontier: China's Ambitions to Dominate Space (2025)* — [live](https://www.uscc.gov/) · [snapshot](https://web.archive.org/web/2026*/https://www.uscc.gov/) · accessed 2026-06-12.

---

## 8. Cross-references

- **Engine modules sourced by this file.** [`session/redai.py`](../../spacesim/session/redai.py) (§1, §4, §7 — the `china_integrated` + `russia_ew_first` doctrine presets); [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (§3, §6 — `mrbm_kkv` for SC-19/DN-3; `abm_heavy` for Nudol/A-235); [`engine/jam.py:MODULATIONS`](../../spacesim/engine/jam.py) (§3, §6 — ground-based RF jammer types); [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) (§3.6, §6.6 — APT41 + AcidRain access vectors); [`engine/cyber.py:attribution_score`](../../spacesim/engine/cyber.py) (§7 — attribution asymmetry); [`engine/sigint.py:geolocation_error_km`](../../spacesim/engine/sigint.py) (§3.3 — Yaogan-triplet TDOA/FDOA math); [`engine/effects.py:Category`](../../spacesim/engine/effects.py) + [`Outcome`](../../spacesim/engine/effects.py) + [`political_consequence`](../../spacesim/engine/effects.py) (§§2-7 — the five-D ladder and the destroy-cost dial); [`engine/custody.py:Track.is_weapons_quality()`](../../spacesim/engine/custody.py) (§7 — custody-as-gate).
- **Sibling primer files.** [`01-doctrine-western.md`](01-doctrine-western.md) — the parallel Western treatment that this file is the foil to; the §1.1.6 "responsible counterspace" discussion of UNGA 77/41 names the same nine "no" votes (China, Russia, Belarus, Iran, Cuba, Nicaragua, Syria, Bolivia, CAR) plus India + Pakistan abstentions that map onto the doctrinal split here. [`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md) — the five effect categories that §§3 and 6 map adversary capabilities onto, with per-effect success-probability math. [`05-mission-types-and-counters.md`](05-mission-types-and-counters.md) — the asset catalogue (Blue side; Red mirror-vectors run through the same templates). [`06-bus-and-payload-operations.md`](06-bus-and-payload-operations.md) §2.5 — the cyber-induced safe-mode pattern that §3.6 (APT41) and §6.6 (Viasat) both target. [`07-legal-norms-and-roe.md`](07-legal-norms-and-roe.md) §3 — the UNGA 77/41 treatment that names the "no" voters this file profiles.
- **Vignettes that exercise this file's content.** Every COA-style vignette under [`content/vignettes/`](../../spacesim/content/vignettes/) (e.g. `coa-china-isr-blind`, `coa-russia-ew-first` — names per the vignette library) instantiates the Red doctrine presets and asset templates documented here.
- **Forward-references to Tier 2 deep-dives.** [`02a-doctrine-china.md`](02a-doctrine-china.md) (per-PLA-system depth — SC-19/DN-3 test record, Shijian operational logs, Yaogan formation history); [`02b-doctrine-russia.md`](02b-doctrine-russia.md) (per-VKS-system depth — Burevestnik nesting-doll record, Tobol siting, Bylina-MM coordination architecture). Both are queued in [`FUTURE-WORK.md` §12.5.2](../FUTURE-WORK.md#1252-tier-2--per-mission-and-per-actor-deep-dives).
- **Research encyclopedia.** [`encyclopedia/R312-space-strategy.md`](encyclopedia/R312-space-strategy.md) (this file is the non-Western half of its cited primer pair); [`encyclopedia/R308-red-teaming-methodology.md`](encyclopedia/R308-red-teaming-methodology.md) (the structured-adversarial-role-play theory behind §7's doctrine-preset design); [`encyclopedia/R303-deterrence-theory.md`](encyclopedia/R303-deterrence-theory.md) (the asymmetric-offset/hedge logic in §5).

*Last reviewed: 2026-06-12. Pending review: every 12 months from `last_reviewed`.*
