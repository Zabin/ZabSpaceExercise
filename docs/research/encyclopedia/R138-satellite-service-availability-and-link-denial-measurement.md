# R138 — Satellite Service Availability and Link-Denial Measurement

> **Document ID:** R138
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R110](R110-communications.md), [R115](R115-electronic-warfare-in-space-operations.md), [R134](R134-pnt-warfare-and-navigation-denial-operations.md)
> **Referenced By:** `docs/feature-planning/06a-release-2-d3-d4-research.md` (Release 2.0 decision D3)
> **Produces:** implementation constraints for [`content/vignette.py`](../../../spacesim/content/vignette.py) (`_evaluate_metric` — the `asset_operational` / `link_denied` kinds and a proposed interval-scored service-availability kind), [`engine/effects.py`](../../../spacesim/engine/effects.py) (`is_link_denied`, `is_link_spoofed`, `ActiveEffect`)
> **Feature Mapping:** Release 2.0 candidate F-03 / B-18 (link-availability objective metric); FS-105 (Spacecraft Operations) for the link state it reads
> **Related Topics:** [R110](R110-communications.md) (Communications — the `CommsState` link model and the execute-time `is_link_denied` gate), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic Warfare — how a jam becomes an `ActiveEffect`), [R134](R134-pnt-warfare-and-navigation-denial-operations.md) (PNT Warfare — GNSS jam-vs-spoof distinction), [R121](R121-telemetry-logging-and-attack-signatures.md) (Telemetry — the RX-power signature an operator sees), [R306](R306-operational-assessment.md) (Operational Assessment — MOE/MOP doctrine)
> **Last Reviewed:** 2026-11-01
> **Primary Sources Consulted:** 4
> **Verification note:** authored 2026-11-01 in an environment where direct page fetch was blocked for every external host; each claim below was checked against search-index abstracts of the cited page, not its full text. The snapshot links follow the corpus's `web/2026/` convention and were not individually confirmed. This file is queued for the §5.3 verification pass of [`10-sources-and-methodology.md`](../10-sources-and-methodology.md) before any number in it is treated as settled.

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Eleven Blue objectives across eight shipped vignettes ask "is the SATCOM/PNT **service** available
to users?" They score it with the `asset_operational` metric: not destroyed, not in safe mode, at the
deadline instant. That metric measures **asset health**, so it reads MET while the users' link is
jammed for the whole window (REV-REL-004 §A.7 item 6; Release 2.0 plan B-18). This topic sets out
how real operators and standards bodies define and measure service availability, so that the
replacement metric (Release 2.0 decision D3) measures what the objective's prose claims.

## 2. Scope

Covers: the difference between asset (system) availability and link/service availability; how
availability is expressed (fraction of time over an interval) and what counts as an outage; link
margin and jamming as causes of outage; where denial applies geographically (uplink vs. downlink
jamming); integrity (spoofing) as a separate form of unavailability for PNT; and the moderate-fidelity
simplifications that are defensible. Does **not** cover: jam-effectiveness math
([R115](R115-electronic-warfare-in-space-operations.md)), the `CommsState` model
([R110](R110-communications.md)), or the doctrine of operational assessment in general
([R306](R306-operational-assessment.md)).

## 3. Concepts

### 3.1 Asset availability and service availability are different measures

**Asset (materiel) availability** is the reliability-engineering quantity. DoD defines operational
availability (A_o) as uptime ÷ (uptime + downtime), and says the result depends on how uptime and
downtime are defined
([DTIC, ADA518378, operational availability paper](https://apps.dtic.mil/sti/pdfs/ADA518378.pdf)
([Wayback](https://web.archive.org/web/2026/https://apps.dtic.mil/sti/pdfs/ADA518378.pdf))).
DoD sustainment-metrics policy names materiel availability and operational availability as the
two top-level sustainment metrics
([DoDI 3110.05](https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/311005p.pdf)
([Wayback](https://web.archive.org/web/2026/https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/311005p.pdf))).
A_o says whether the *platform* can do its job. It says nothing about whether a user in a contested
area can use the signal.

**Service availability** is defined at the user's end of the link. The GPS Standard Positioning
Service Performance Standard (5th ed., April 2020) keeps the two apart. It has separate standards for
signal-in-space (SIS) availability per orbital slot and for the constellation (§3.7), and for **PDOP
availability**: ≥98% of the time globally with PDOP ≤ 6, and ≥88% at the worst site (§3.8). It also
sets **position service availability** targets of 99% average-location and 90% worst-location
([GPS.gov, *GPS SPS Performance Standard*, 5th ed., 2020](https://www.gps.gov/technical/ps/2020-SPS-performance-standard.pdf)
([Wayback](https://web.archive.org/web/2026/https://www.gps.gov/technical/ps/2020-SPS-performance-standard.pdf));
targets as tabulated on [GPS.gov *GPS Performance*](https://archive.gps.gov/systems/gps/performance/)
([Wayback](https://web.archive.org/web/2026/https://archive.gps.gov/systems/gps/performance/))).
Every one of these is a **fraction of time over an interval**, measured at a user location. A
satellite can be 100% healthy while the service at a given place falls short.
*Single source (Tier A, read via search abstract).* The standard's own text on whether local
interference is outside its availability commitment was not readable in this environment. Treat the
statement "the SPS PS excludes jamming" as unverified.

**Commercial SATCOM contracts measure the same thing at the terminal.** Starlink's Priority-plan
service-level agreement commits to 99.9% network availability per line per monthly billing period. It
counts an outage when the user terminal cannot exchange pings with a Starlink point of presence, and
it excludes force majeure
([Starlink, *Service Level Agreement*, DOC-1729-34307-72](https://starlink.com/legal/documents/DOC-1729-34307-72)
([Wayback](https://web.archive.org/web/2026/https://starlink.com/legal/documents/DOC-1729-34307-72))).
So the SLA defines availability as user-to-network reachability, timed over an interval. It does not
use satellite health.

### 3.2 An outage has an entry rule, not just a threshold

Telecommunications error-performance standards do not let a single bad instant count as
unavailability. ITU-T G.821/G.826 (and Y.1563 for IP) declare a link **unavailable** after 10
consecutive severely errored seconds, and **available** again after 10 consecutive non-severely-errored
seconds. The 10 entry seconds are moved from the errored count to the unavailable count
([Anritsu, *G.821 Measurement Definitions*](https://dl.cdn-anritsu.com/en-us/test-measurement/ohs/10450-00021J/Measurements/A_Glossary.62.4.html)
([Wayback](https://web.archive.org/web/2026/https://dl.cdn-anritsu.com/en-us/test-measurement/ohs/10450-00021J/Measurements/A_Glossary.62.4.html));
[Juniper, *Unavailable Seconds (UAS)*, citing Y.1563](https://cns.paa.juniper.net/static/4.4.3.41/support/metrics/uas.html)
([Wayback](https://web.archive.org/web/2026/https://cns.paa.juniper.net/static/4.4.3.41/support/metrics/uas.html))).
*Secondary sources for an ITU-T rule; the ITU text itself was not reachable.* The point for this
simulator is that availability is **time-integrated, with a minimum outage duration**. It is not a
yes/no at one instant.

### 3.3 Link margin, fade and jamming are all "margin consumed"

A link is usable while the received energy-per-bit to noise-plus-interference ratio stays above the
demodulator's threshold. **Link margin** is the headroom above that threshold. Satellite link design
sizes margin to a target availability. The ITU-R P.618 method sets the rain-fade margin for a link to
be available a stated percentage of the time, and 99.99% (≈53 min/yr outage) is the common design
point
([RF Essentials, *Fade margin for a given link availability*](https://rfessentials.com/rf-knowledge-base/how-do-i-calculate-the-fade-margin-required-for-a-given-link-availability-percen/)
([Wayback](https://web.archive.org/web/2026/https://rfessentials.com/rf-knowledge-base/how-do-i-calculate-the-fade-margin-required-for-a-given-link-availability-percen/));
[MathWorks, *Antenna size analysis using ITU-R P.618*](https://www.mathworks.com/help/satcom/ug/antenna-size-analysis-using-itu-r-p618-propagation-model.html)
([Wayback](https://web.archive.org/web/2026/https://www.mathworks.com/help/satcom/ug/antenna-size-analysis-using-itu-r-p618-propagation-model.html))).
Jamming uses up the same margin on purpose. A spread-spectrum anti-jam margin is the processing gain
minus the required E_b/N_0 (and losses), and a jammer wins when its jamming-to-signal ratio (J/S) is
larger than that margin
([RF Essentials, *Spread spectrum anti-jam capability*](https://rfessentials.com/rf-knowledge-base/how-does-spread-spectrum-technology-provide-anti-jam-capability-for-military-com/)
([Wayback](https://web.archive.org/web/2026/https://rfessentials.com/rf-knowledge-base/how-does-spread-spectrum-technology-provide-anti-jam-capability-for-military-com/))).
*Tier C/D engineering reference. Use it for the structure of the argument only, never for a dB figure
in the engine.* So fade and jamming are the same physical event at the receiver: margin exhausted,
link unusable. An availability metric has to count both, and it has to be blind to whether the
satellite bus is healthy.

### 3.4 Where denial applies: uplink jamming vs. downlink jamming

The two kinds of jamming deny different users. **Uplink jamming** attacks the satellite's receiver,
"so effects may be global": every user of that transponder is denied, and it needs more jammer power.
**Downlink jamming** attacks user terminals and is local. The jammer generally has to be near (and,
for sky-pointed antennas, roughly above) the terminals it denies
([CSIS Aerospace Security, *Space Threat Assessment / Space System Threats*](https://aerospace.csis.org/wp-content/uploads/2018/09/Space-System-Threats.pdf)
([Wayback](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2018/09/Space-System-Threats.pdf));
[CSIS *On the Radar*, *Satellite Jamming*](https://ontheradar.csis.org/issue-briefs/satellite-jamming/)
([Wayback](https://web.archive.org/web/2026/https://ontheradar.csis.org/issue-briefs/satellite-jamming/))).
GNSS denial is the clearest case of downlink denial: the satellites stay healthy and receivers inside
the interference area lose service. The 2024 Baltic disruptions around Kaliningrad affected tens of
thousands of civil flights while GPS itself stayed nominal. Researchers traced a jamming episode in
April 2025 and a spoofing episode in May 2025 to near the Okunevo antenna site
([Defense News, 2025-07-02](https://www.defensenews.com/global/europe/2025/07/02/researchers-home-in-on-origins-of-russias-baltic-gps-jamming/)
([Wayback](https://web.archive.org/web/2026/https://www.defensenews.com/global/europe/2025/07/02/researchers-home-in-on-origins-of-russias-baltic-gps-jamming/));
[Spire, *GNSS interference report: Russia 2024/2025, Part 1*](https://spire.com/blog/space-reconnaissance/gnss-interference-report-russia/)
([Wayback](https://web.archive.org/web/2026/https://spire.com/blog/space-reconnaissance/gnss-interference-report-russia/))).
This is the "satellite healthy, bubble denied" teaching point that `coa-russia-ml`'s brief makes and
its current objective cannot score.

### 3.5 Integrity loss is unavailability for PNT

A spoofed PNT user still has a signal, but the position it gives is wrong. The SPS PS treats
integrity as its own commitment, next to availability (the misleading-information standards, same
document as §3.1). For a user, hazardously misleading information is worse than no service, which is
why the 2024 aviation advisories treated spoofing as a navigation outage. [R134](R134-pnt-warfare-and-navigation-denial-operations.md)
§3 covers the jam-vs-spoof operational distinction. `engine/effects.py` already models them
separately (`is_link_denied` vs. `is_link_spoofed`).

### Sources

- *DTIC ADA518378 (operational availability)* — [live](https://apps.dtic.mil/sti/pdfs/ADA518378.pdf) · [snapshot](https://web.archive.org/web/2026/https://apps.dtic.mil/sti/pdfs/ADA518378.pdf) · accessed 2026-11-01.
- *DoDI 3110.05, Sustainment Health Metrics* — [live](https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/311005p.pdf) · [snapshot](https://web.archive.org/web/2026/https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/311005p.pdf) · accessed 2026-11-01.
- *GPS SPS Performance Standard, 5th ed. (Apr 2020)* — [live](https://www.gps.gov/technical/ps/2020-SPS-performance-standard.pdf) · [snapshot](https://web.archive.org/web/2026/https://www.gps.gov/technical/ps/2020-SPS-performance-standard.pdf) · accessed 2026-11-01.
- *GPS.gov, GPS Performance* — [live](https://archive.gps.gov/systems/gps/performance/) · [snapshot](https://web.archive.org/web/2026/https://archive.gps.gov/systems/gps/performance/) · accessed 2026-11-01.
- *Starlink Service Level Agreement, DOC-1729-34307-72* — [live](https://starlink.com/legal/documents/DOC-1729-34307-72) · [snapshot](https://web.archive.org/web/2026/https://starlink.com/legal/documents/DOC-1729-34307-72) · accessed 2026-11-01.
- *Anritsu, G.821 Measurement Definitions* — [live](https://dl.cdn-anritsu.com/en-us/test-measurement/ohs/10450-00021J/Measurements/A_Glossary.62.4.html) · [snapshot](https://web.archive.org/web/2026/https://dl.cdn-anritsu.com/en-us/test-measurement/ohs/10450-00021J/Measurements/A_Glossary.62.4.html) · accessed 2026-11-01.
- *Juniper Paragon, Unavailable Seconds (UAS)* — [live](https://cns.paa.juniper.net/static/4.4.3.41/support/metrics/uas.html) · [snapshot](https://web.archive.org/web/2026/https://cns.paa.juniper.net/static/4.4.3.41/support/metrics/uas.html) · accessed 2026-11-01.
- *RF Essentials, fade margin for a given availability* — [live](https://rfessentials.com/rf-knowledge-base/how-do-i-calculate-the-fade-margin-required-for-a-given-link-availability-percen/) · [snapshot](https://web.archive.org/web/2026/https://rfessentials.com/rf-knowledge-base/how-do-i-calculate-the-fade-margin-required-for-a-given-link-availability-percen/) · accessed 2026-11-01.
- *MathWorks, ITU-R P.618 antenna sizing example* — [live](https://www.mathworks.com/help/satcom/ug/antenna-size-analysis-using-itu-r-p618-propagation-model.html) · [snapshot](https://web.archive.org/web/2026/https://www.mathworks.com/help/satcom/ug/antenna-size-analysis-using-itu-r-p618-propagation-model.html) · accessed 2026-11-01.
- *RF Essentials, spread-spectrum anti-jam* — [live](https://rfessentials.com/rf-knowledge-base/how-does-spread-spectrum-technology-provide-anti-jam-capability-for-military-com/) · [snapshot](https://web.archive.org/web/2026/https://rfessentials.com/rf-knowledge-base/how-does-spread-spectrum-technology-provide-anti-jam-capability-for-military-com/) · accessed 2026-11-01.
- *CSIS, Space System Threats (2018)* — [live](https://aerospace.csis.org/wp-content/uploads/2018/09/Space-System-Threats.pdf) · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2018/09/Space-System-Threats.pdf) · accessed 2026-11-01.
- *CSIS On the Radar, Satellite Jamming* — [live](https://ontheradar.csis.org/issue-briefs/satellite-jamming/) · [snapshot](https://web.archive.org/web/2026/https://ontheradar.csis.org/issue-briefs/satellite-jamming/) · accessed 2026-11-01.
- *Defense News, "Researchers home in on origins of Russia's Baltic GPS jamming", 2025-07-02* — [live](https://www.defensenews.com/global/europe/2025/07/02/researchers-home-in-on-origins-of-russias-baltic-gps-jamming/) · [snapshot](https://web.archive.org/web/2026/https://www.defensenews.com/global/europe/2025/07/02/researchers-home-in-on-origins-of-russias-baltic-gps-jamming/) · accessed 2026-11-01.
- *Spire, GNSS interference report: Russia 2024/2025, Part 1* — [live](https://spire.com/blog/space-reconnaissance/gnss-interference-report-russia/) · [snapshot](https://web.archive.org/web/2026/https://spire.com/blog/space-reconnaissance/gnss-interference-report-russia/) · accessed 2026-11-01.

## 4. Operational Context

In doctrine terms, "keep SATCOM available" is a **measure of effectiveness**: it assesses a change in
the operational environment tied to an objective. "The satellite is not in safe mode" is closer to a
**measure of performance**, which assesses whether friendly actions were done
([JP 5-0 definitions as quoted in AcqNotes, *Measures of Effectiveness*](https://acqnotes.com/acqnote/tasks/measures-of-effectivenessrequirements)
([Wayback](https://web.archive.org/web/2026/https://acqnotes.com/acqnote/tasks/measures-of-effectivenessrequirements));
see [R306](R306-operational-assessment.md) for the assessment doctrine). The shipped vignettes use the
MOP as if it were the MOE. A space operations crew judging SATCOM support to a theater looks at the
user's view: are the terminals in the area of operations passing traffic, for how much of the
mission window, and for how long was the longest gap? An operator who manages a jam by shifting users,
hopping frequency or rerouting through a ground relay (the `satcom.shift_users` /
`def.frequency_hop` / rebroadcast answers in [R110](R110-communications.md)) should score better than
one whose satellite is merely healthy. Only a time-integrated, link-aware metric can tell them apart.

### Sources

- *AcqNotes, Measures of Effectiveness (quoting JP 5-0)* — [live](https://acqnotes.com/acqnote/tasks/measures-of-effectivenessrequirements) · [snapshot](https://web.archive.org/web/2026/https://acqnotes.com/acqnote/tasks/measures-of-effectivenessrequirements) · accessed 2026-11-01. *Secondary quotation of a Tier-A doctrine definition; check the wording against the current JP 5-0 edition.*

## 5. Implementation Guidance

**What a service-availability objective should compute (the D3 metric).** For one service asset
`target`, a service link `link` and a scoring interval `[t0, t1]` (`t0` = the vignette start or an
authored `from_s`; `t1` = `by_s`):

1. An instant `t` is **unavailable** if any of these holds (all are already in the replayed state):
   (a) `asset.health == "destroyed"` from its destruction time on; (b) `bus_state.safe_mode.active`;
   (c) `is_link_denied(world, target, t, link)` (an `ActiveEffect` with outcome `deny`/`disrupt`
   covering `t`); (d) for a `pnt` payload only, `is_link_spoofed(world, target, t)` (integrity loss,
   §3.5).
2. `availability = 1 − |unavailable ∩ [t0, t1]| / (t1 − t0)`.
3. The objective is **MET** iff `now ≥ t1` and `availability ≥ min_fraction`. Before `t1`, the UI shows
   the running fraction so far as *in progress*. Never show MET early.
4. Optionally also report the **longest single outage** (seconds). This is the second number a real
   crew reports (§3.2). An authored `max_outage_s` may gate MET as well.

- **Do compute it by interval arithmetic over state the engine already keeps.** `world.active_effects`
  is never pruned and carries `start`/`end`/`outcome`/`link_target`, so denial intervals come straight
  from it. Safe-mode and destroyed intervals come from the event log through replay
  (`session/aar.py::worlds_at_times` / `replay_stepwise`). Interval arithmetic is exact, deterministic
  and cannot alias. **Don't** sample at a coarse cadence and count samples: a short jam between
  samples would vanish, which is the same failure invariant 5 (sub-step the clock) exists to prevent.
- **Do use the same predicate on both sides.** Red's `link_denied` and Blue's availability must call
  the same `is_link_denied(..., link)`, so at every instant "Red denies" and "Blue available" are
  mutually exclusive. A scoring pair that can both read MET at the same instant is a trust defect, and
  the acceptance test should check exactly that.
- **Do scope by service link.** In this engine, `link_target="uplink"` is the TT&C **command** path
  (IP-1290: an uplink jam fails command delivery). A command-uplink jam does not by itself cut user
  service, so a service metric should count `downlink`, plus unscoped legacy effects, by default.
  **Flag, don't fix silently:** the engine has no separate *transponder/user uplink*, which §3.4 says
  is the global-effect jamming case. Until it does, an author who wants uplink jamming to count sets
  `link: any`.
- **Don't add a ground-terminal location model to fix B-18.** Physically, downlink denial is regional
  (§3.4). The engine's denial is asset-scoped, with `jam_footprint` gating jammer→satellite geometry.
  At moderate fidelity, treating "an active deny/disrupt on the asset's service link" as "the
  theater's users are denied" is a defensible simplification. It holds because each vignette declares
  one theater and one user population. Write that assumption into the metric's docstring. A user-area
  `GroundSite` (the entity's docstring already lists "user area") is the growth path for regional
  scoping, and it is a later feature.
- **Don't model DOP / constellation geometry for PNT.** One `BLUE-PNT` asset stands in for a
  constellation. SPS-style PDOP availability (§3.1) needs ≥4 satellites in view and is out of scope.
  The asset-plus-link predicate is the right moderate-fidelity proxy.
- **Don't add a link-budget computation to decide "usable".** The engine's jam model already decides
  margin exhaustion as a probabilistic `ActiveEffect` outcome ([R115](R115-electronic-warfare-in-space-operations.md)).
  A parallel E_b/N_0 calculation inside an objective would be a second, inconsistent jam model.
  `interference_level`/`interference_mitigation` remain telemetry and mitigation inputs. They are not
  an availability source unless a later requirement says so.
- **Don't debounce by default.** The G.826 10-second entry rule (§3.2) exists to filter bit-error
  noise. Engine effects last minutes, so the default `min_outage_s` is 0, and an authored value is
  allowed.
- **Keep `asset_operational`.** It is a correct MOP ("the bird survived"). Rename the objectives that
  mean *service* and point them at the new metric. Don't redefine the old kind, because saved sessions
  and other vignettes depend on its current meaning (`save_format` additive policy, Release 2.0 D7).

## 6. Feature Mapping

Release 2.0 F-03 / B-18 (the link-availability objective metric), and the vignette objectives that
consume it: `03-gnss-ew-campaign` `maintain_service`, `06-satcom-cyber-link` `keep_service`,
`08-multi-domain-taiwan` `keep_satcom`, `coa-china-md`, `coa-china-ml`, `coa-misc-iran-ml`,
`coa-russia-md` and `coa-russia-ml`'s PNT/SATCOM availability objectives. Mission-survival objectives
(`mt-isr-sar`, `mt-weather-collect`, `learn-intermediate-recovery`, `nv-isl-relay-debris`,
`mt-sigint-geolocate` `preserve_constellation`) are correctly `asset_operational` and are not
affected. The decision memo is
[`docs/feature-planning/06a-release-2-d3-d4-research.md`](../../feature-planning/06a-release-2-d3-d4-research.md).

## 7. Related Topics

[R110](R110-communications.md) (the link state and execute-time denial gate this metric reads),
[R115](R115-electronic-warfare-in-space-operations.md) (how jams become `ActiveEffect`s),
[R134](R134-pnt-warfare-and-navigation-denial-operations.md) (GNSS jam vs. spoof),
[R121](R121-telemetry-logging-and-attack-signatures.md) (the RX-power signature the operator sees
while availability drops), [R306](R306-operational-assessment.md) (MOE vs. MOP doctrine),
[R139](R139-passive-rf-emitter-characterization-and-geolocation.md) (the companion Release 2.0 D4
topic).
