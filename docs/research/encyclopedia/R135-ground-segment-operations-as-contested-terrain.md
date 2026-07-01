# R135 — Ground Segment Operations as Contested Terrain

> **Document ID:** R135
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R107](R107-ground-segment-operations.md), [R116](R116-cyber-operations-against-space-systems.md)
> **Referenced By:** —
> **Produces:** implementation constraints for [`engine/cyber.py`](../../../spacesim/engine/cyber.py)'s
> `ground_segment`/`ground_modem` vectors, [`engine/entities.py`](../../../spacesim/engine/entities.py)'s
> `GroundSite`
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R107](R107-ground-segment-operations.md) (Ground Segment Operations — the
> cooperative-only `GroundSite`/contact model this topic extends to a contested-terrain view),
> [R116](R116-cyber-operations-against-space-systems.md) (Cyber Operations — the vector/payload
> database this topic grounds the `ground_segment`/`ground_modem` entries of), [R110](R110-communications.md)
> (Communications — the uplink/downlink channel the ground segment physically anchors)
> **Last Reviewed:** 2026-07-01
> **Primary Sources Consulted:** 3

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Identified as **GAP-12** in the Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3):
[R107](R107-ground-segment-operations.md) documents the `GroundSite` model purely as a cooperative
resource — an antenna, an elevation mask, a contact-window predicate — with no treatment of the
ground segment as something an adversary attacks. Yet `engine/cyber.py`'s `VECTORS` table already
implements two ground-segment-specific attack entries (`ground_segment`, and the more specific
`ground_modem` — added, per its code comment, explicitly to model "the Viasat KA-SAT pattern"), and
GDS-04's Domain Model gives `GroundSite` no attack-surface property at all. This topic supplies the
missing grounding: what a real ground-segment attack looks like, so the existing `ground_segment`/
`ground_modem` vectors (and any future `GroundSite`-attack-surface modeling) are traceable to real
precedent rather than an invented parameter set.

## 2. Scope

Covers: real-world cyber attacks against satellite ground infrastructure (the operator-station,
gateway, and management-plane compromise pattern), the published cybersecurity-hardening guidance
that responds to that pattern, and what changes if `GroundSite` is treated as contested terrain
rather than a cooperative resource. Does **not** cover: the orbital-geometry/contact-window mechanics
of ground stations ([R107](R107-ground-segment-operations.md), unchanged and still the correct model
for cooperative contact scheduling), the general cyber vector/payload/attribution math
([R116](R116-cyber-operations-against-space-systems.md), which this topic grounds two specific
table entries of but does not restate), or physical/kinetic attacks on ground infrastructure
(no engine analog exists for this and it is out of scope for a PME tool per
`docs/research/10-sources-and-methodology.md` §8's out-of-bounds rule against unverifiable
operational TTPs).

## 3. Concepts

**The single most consequential satellite-ground-segment cyberattack on record is a management-plane
compromise, exactly matching `engine/cyber.py`'s `ground_modem` vector's own citation.** On
**2022-02-24** — the day of Russia's invasion of Ukraine — an attacker exploited a misconfigured VPN
appliance to gain remote access to the trusted management segment of Viasat's KA-SAT network, then
pushed a wiper malware (subsequently identified and named **AcidRain**) to tens of thousands of fixed
satellite modems across Ukraine and wider Europe, permanently disabling them
([CCDCOE, "Viasat KA-SAT attack (2022)"](https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))
([Wayback](https://web.archive.org/web/2026/https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022)))
· [SentinelOne, "AcidRain | A Modem Wiper Rains Down on Europe," 2022-03-31](https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)
([Wayback](https://web.archive.org/web/2026/https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/))).
The attack's collateral effects extended well beyond the intended Ukrainian target: a major German
energy company lost remote monitoring access to more than 5,800 wind turbines, and nearly 9,000
French satellite-internet subscribers experienced an outage — a direct illustration of why a
ground-segment compromise's blast radius is not naturally bounded by the attacker's own intended
target set, unlike a space-segment jam/DE effect aimed at one satellite. On **2022-05-10**, the
European Union, the United States, and the United Kingdom jointly attributed the attack to Russia;
the AcidRain malware shares code lineage with VPNFilter, a 2018 router-compromise operation
previously attributed to Russian military intelligence by the FBI
([CCDCOE, *op. cit.*](https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))).

**The attack chain is the load-bearing fact for how the engine should model it: entry was through the
*management* plane, not the RF/satellite link itself.** The intrusion vector was a VPN-appliance
misconfiguration granting access to the trusted management segment — a ground-infrastructure/
IT-network compromise — after which the attacker used that management-plane access to push malicious
firmware updates over the satellite link to the end-user modems ([CCDCOE, *op. cit.*](https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))).
This two-stage structure (ground-network intrusion → weaponized use of the legitimate command/update
channel) is precisely why `engine/cyber.py` models `ground_modem` as a distinct vector from the
broader `ground_segment` entry and from the RF-injection (`rf`) vector — a ground-segment
management-plane compromise is a different attack surface (IT network hardening, VPN configuration,
credential hygiene) from either an over-the-air RF injection or a generic insider/supply-chain
compromise, even though all four ultimately manipulate the same command/telemetry pipeline.

**Government guidance now treats the ground segment as a first-class, separately-profiled attack
surface, not an afterthought to space-segment security.** NIST Internal Report 8401 (finalized,
published via NIST's Interagency/Internal Report series) applies the NIST Cybersecurity Framework
specifically to the ground segment of space operations, explicitly scoping two components: the
mission operations center (MOC), which issues commands and receives telemetry, and the payload
control center, which communicates with both the MOC and the space vehicle — a decomposition that
maps directly onto this simulator's `GroundSite`/command-uplink/telemetry-downlink channel split
([NIST, *NIST IR 8401*, cybersecurity ground-segment profile](https://nvlpubs.nist.gov/nistpubs/ir/2023/NIST.IR.8270.pdf)
([Wayback](https://web.archive.org/web/2026/https://nvlpubs.nist.gov/nistpubs/ir/2023/NIST.IR.8270.pdf))).
CISA's June 2024 "Recommendations to Space System Operators for Improving Cybersecurity" and
companion "Space Systems Security and Resilience Landscape: Zero Trust in the Space Environment"
report make the same structural point at the policy level: the space sector's cybersecurity guidance
has matured specifically toward ground-segment zero-trust architecture, treating the ground network
as an untrusted-by-default perimeter rather than an implicitly-trusted operational backbone
([CISA, "Recommendations to Space System Operators for Improving Cybersecurity," 2024-06](https://www.cisa.gov/sites/default/files/2024-06/Recommendations%20to%20Space%20System%20Operators%20for%20Improving%20Cybersecurity%20(508).pdf)
([Wayback](https://web.archive.org/web/2026/https://www.cisa.gov/sites/default/files/2024-06/Recommendations%20to%20Space%20System%20Operators%20for%20Improving%20Cybersecurity%20(508).pdf))).

**Ground-segment threats are not exclusively cyber — jamming of the ground uplink/downlink RF path is
a documented, distinct threat the current `ground_segment` cyber vector does not capture.** The
Secure World Foundation's 2025 *Global Counterspace Capabilities* report documents RF jamming against
GNSS and communications satellites as a rising, actively-used capability among major counterspace
actors — and because a ground station's uplink/downlink is itself an RF link, it is exposed to the
same EW jamming category [R115](R115-electronic-warfare-in-space-operations.md) already models for
the space-to-space and space-to-ground link generally, not only the space segment
([Secure World Foundation, *2025 Global Counterspace Capabilities Report*](https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
([Wayback](https://web.archive.org/web/2026/https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report))).
This means "ground segment as contested terrain" spans two of the simulator's five D's through two
different existing subsystems (`engine/cyber.py`'s vectors for the management-plane threat,
`engine/jam.py`'s modulation database for the RF-link threat) rather than needing one new mechanism —
the gap this topic closes is the *grounding*, not a missing engine capability.

### Sources

- *CCDCOE, "Viasat KA-SAT attack (2022)"* — [live](https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))
  · [snapshot](https://web.archive.org/web/2026/https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))
  · accessed 2026-07-01.
- *SentinelOne, "AcidRain | A Modem Wiper Rains Down on Europe"* (2022-03-31) — [live](https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)
  · [snapshot](https://web.archive.org/web/2026/https://www.sentinelone.com/labs/acidrain-a-modem-wiper-rains-down-on-europe/)
  · accessed 2026-07-01.
- *NIST IR 8401, ground-segment cybersecurity profile* — [live](https://nvlpubs.nist.gov/nistpubs/ir/2023/NIST.IR.8270.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://nvlpubs.nist.gov/nistpubs/ir/2023/NIST.IR.8270.pdf)
  · accessed 2026-07-01.
- *CISA, "Recommendations to Space System Operators for Improving Cybersecurity"* (2024-06) — [live](https://www.cisa.gov/sites/default/files/2024-06/Recommendations%20to%20Space%20System%20Operators%20for%20Improving%20Cybersecurity%20(508).pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.cisa.gov/sites/default/files/2024-06/Recommendations%20to%20Space%20System%20Operators%20for%20Improving%20Cybersecurity%20(508).pdf)
  · accessed 2026-07-01.
- *Secure World Foundation, 2025 Global Counterspace Capabilities Report* — [live](https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026/https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-07-01.

## 4. Operational Context

Real ground-segment defenders (network administrators, NOC/SOC operators at the satellite operator,
not the flight-dynamics/mission-ops team [R125](R125-flight-operations-team-roles.md) already
covers) worry about a different threat model than a spacecraft operator: VPN/management-plane
configuration hygiene, patch cadence on ground network appliances, and credential/access control —
IT-security disciplines, not orbital-mechanics or RF-link-budget disciplines. The Viasat incident's
collateral blast radius (wind turbines, unrelated ISP subscribers) is the reason real operators now
treat ground-segment security as inherently a shared-infrastructure risk, not a satellite-specific
one: a compromise of the ground network can cascade to every customer/mission sharing that network
segment, regardless of which specific satellite or mission was the attacker's actual target. A White
Cell running a ground-segment-contested vignette should expect this: a successful `ground_modem`-style
intrusion's consequences should plausibly extend to assets/missions the attacking cell never
targeted, mirroring the real incident's spillover.

## 5. Implementation Guidance

- **Keep `ground_modem` distinct from `ground_segment` in any future vector expansion**, per §3's
  attack-chain finding — the management-plane-entry-then-weaponized-update-channel pattern is a
  materially different attack surface from a generic operator-station compromise, and the existing
  code comment already correctly anchors this distinction to the real Viasat precedent; a future
  refactor should not collapse the two vectors back together.
- **A future `GroundSite` attack-surface property (GDS-04's currently-missing concept) should model
  network/management-plane posture, not just physical/RF hardening.** Per §3's NIST IR 8401 MOC/
  payload-control-center split, the real ground-segment threat model is dominated by IT-network
  configuration hygiene rather than physical intrusion or RF jamming resistance alone — a future
  `GroundSite.cyber_posture`-equivalent field (mirroring `Asset.cyber_posture`, per
  [R116](R116-cyber-operations-against-space-systems.md)) is the more realistic extension than a
  purely physical-hardening property.
- **Model ground-segment compromise consequences as potentially exceeding the attacking cell's
  intended target set.** Per §4's collateral-blast-radius finding, a future feature giving
  `ground_modem`/`ground_segment` effects a shared-infrastructure consequence (affecting other
  assets/cells sharing the compromised ground station) would be more realistic than the current
  implicit assumption that a cyber effect's consequences stay scoped to the ordering cell's intended
  target — though this is a modeling *option* this topic surfaces, not a design this topic authorizes
  building (§2).
- **RF jamming of a ground station's uplink/downlink is already `engine/jam.py`'s domain, not a new
  `ground_segment` cyber-vector variant.** Per §3's fifth finding, do not add a "ground station RF
  jam" entry to `engine/cyber.py`'s `VECTORS` table — the existing jam-modulation database
  ([R115](R115-electronic-warfare-in-space-operations.md)) already covers ground-station RF links as
  one more instance of the link-jamming mechanics it models generally; adding a redundant cyber-side
  entry would duplicate rather than extend existing coverage.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) — the existing home of `engine/cyber.py`'s vector table this topic
grounds; any future `GroundSite` attack-surface extension should cite this topic directly.

## 7. Related Topics

[R107](R107-ground-segment-operations.md) (Ground Segment Operations — the cooperative `GroundSite`
model this topic extends to a contested-terrain view), [R116](R116-cyber-operations-against-space-systems.md)
(Cyber Operations Against Space Systems — the vector/payload/attribution math this topic's
`ground_segment`/`ground_modem` grounding sits inside), [R110](R110-communications.md) (Communications
— the uplink/downlink channel physically anchored at the ground segment), [R115](R115-electronic-warfare-in-space-operations.md)
(Electronic Warfare — the RF-jamming mechanism §3's fifth finding routes ground-station RF threats
through instead of a new cyber vector), [R125](R125-flight-operations-team-roles.md) (Flight
Operations Team Roles — the NOC/SOC ground-network-defender role distinct from the flight-dynamics
team this topic's operational context describes).
