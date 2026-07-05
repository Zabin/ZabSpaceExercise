# R134 — PNT Warfare and Navigation-Denial Operations

> **Document ID:** R134
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R109](R109-sensor-operations.md), [R110](R110-communications.md)
> **Referenced By:** [R137](R137-bus-and-payload-parameter-catalog.md)
> **Produces:** implementation constraints for [`engine/buscommands.py`](../../../spacesim/engine/buscommands.py)'s
> `pnt.set_integrity` / `pnt.flex_power` / `pnt.set_health_flag` / `pnt.report_status` verbs
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R109](R109-sensor-operations.md) (Sensor Operations — the payload-type model
> `pnt` extends), [R110](R110-communications.md) (Communications — the link-denial mechanics PNT
> jamming/spoofing parallels), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic
> Warfare — the jamming taxonomy this topic's GNSS-specific case sits inside), `docs/research/05-mission-types-and-counters.md`
> §4 (the pre-existing mission-type primer's PNT mention, already cited in `pnt.flex_power`'s code
> comment), `docs/FUTURE-WORK.md` §2.2 (the deferred `05b-satcom-pnt.md` primer stub this topic's
> research anticipates)
> **Last Reviewed:** 2026-07-05
> **Primary Sources Consulted:** 3

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Identified as **GAP-09** in the Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3):
`engine/buscommands.py` already implements four real PNT operator verbs — `pnt.set_integrity`
(legacy), `pnt.flex_power`, `pnt.set_health_flag`, and `pnt.report_status` — with code comments
citing IS-GPS-200E and 2 SOPS Master Control Station (MCS) practice, but per `docs/FUTURE-WORK.md`
§2.2 no dedicated R1xx topic exists grounding the *operational pattern* those verbs represent: what
real GNSS jamming/spoofing campaigns look like, and what the defensive playbook (flex power, health
flags, anti-jam receiver hardware) actually buys an operator. This topic closes that gap so an
implementer extending the `pnt` payload type or adding a new PNT-warfare effect has the real
precedent, not just the isolated code comments.

## 2. Scope

Covers: real-world GNSS jamming and spoofing operational patterns (as distinct threat classes, not
interchangeable); the defensive playbook a PNT payload operator and a receiver operator each control
(flex power / health flags on the space-segment side, CRPA/M-code anti-jam receivers on the
user-segment side); and how these map onto the four `pnt.*` verbs already implemented. Does **not**
cover: the jamming-effectiveness math for non-GNSS links (`engine/jam.py`'s barrage/spot/sweep/
deceptive modulation database — [R115](R115-electronic-warfare-in-space-operations.md), unchanged),
general communications link-denial mechanics ([R110](R110-communications.md)), or SIGINT
geolocation of a jammer once detected ([R129](R129-sigint-collection-and-geolocation-accuracy.md),
a related but distinct sensing question).

## 3. Concepts

**GNSS jamming and spoofing are distinct threat classes with different operational signatures, and
the simulator's `Outcome` model already tracks this distinction (`FUTURE-WORK.md` item 14) even
though no R1xx topic previously grounded why the distinction matters.** Jamming denies signal by
overpowering it with noise (a *deny* effect in the five-D taxonomy); spoofing forges a false signal
that a receiver locks onto with high confidence, producing a wrong position/time fix while the
receiver's own link-quality indicators can still read nominal — a *deceive* effect, not a *deny*
one. Both are active in the same real conflict zones simultaneously: Eastern Mediterranean maritime
tracking data documented **117 vessels appearing to simultaneously occupy the same point (Beirut
Rafic Hariri International Airport) in April 2024**, a spoofing signature, not a jamming one, since
jammed receivers typically go dark rather than reporting a coherent false position
([Inside GNSS, "GNSS Spoofing and Jamming in Eastern Europe"](https://insidegnss.com/gnss-spoofing-and-jamming-in-eastern-europe/)
([Wayback](https://web.archive.org/web/2026/https://insidegnss.com/gnss-spoofing-and-jamming-in-eastern-europe/))).

**GNSS interference at military-relevant scale is now a persistent, mapped feature of active
conflict zones, not an occasional incident.** Following Russia's 2022-02-24 invasion of Ukraine,
GNSS jamming and spoofing spread from the immediate conflict zone into the Baltic region, with
Latvia alone documenting **more than 26 confirmed jamming incidents in 2022** and sustained jamming
continuing through 2023 ([Breaking Defense, "As Baltics see spike in GPS jamming, NATO must
respond," 2024-01](https://breakingdefense.com/2024/01/as-baltics-see-spike-in-gps-jamming-nato-must-respond/)
([Wayback](https://web.archive.org/web/2026/https://breakingdefense.com/2024/01/as-baltics-see-spike-in-gps-jamming-nato-must-respond/))).
The Black Sea region shows the same pattern at larger scale: Russian ground-based EW systems
positioned in Crimea have made the Black Sea and the Romanian Flight Information Region one of the
most consistently GNSS-degraded zones in Europe from mid-2024 onward, affecting both maritime AIS
tracking and civil aviation ([Spire Global, "GNSS interference report: Russia — Part 4 of 4: Black
Sea & Romanian airspace"](https://spire.com/blog/space-reconnaissance/gnss-interference-report-black-sea-romanian-airspace/)
([Wayback](https://web.archive.org/web/2026/https://spire.com/blog/space-reconnaissance/gnss-interference-report-black-sea-romanian-airspace/))).
The Secure World Foundation's 2025 *Global Counterspace Capabilities* report (compiled from
open-source evidence, February 2024-February 2025) independently corroborates the trend line: GNSS
jamming against PNT and communications satellites is rising among all three major counterspace
powers, and — notably for this simulator's ROE model — is the one class of counterspace effect
**already in active use in ongoing conflicts**, unlike destructive kinetic capabilities, which remain
untested operationally since the 2022 moratorium-era test pause ([Secure World Foundation, *2025
Global Counterspace Capabilities Report*](https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
([Wayback](https://web.archive.org/web/2026/https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report))).

**The space-segment defense the `pnt.flex_power` verb models is a real, publicly-documented Master
Control Station capability, not an invented mechanic.** IS-GPS-200E's flex-power provision lets the
GPS Master Control Station reallocate a satellite's transmit power budget between the civil P(Y)
signal and the military M-code signal, raising M-code power specifically in a jamming environment at
the cost of civil-signal margin; GPS Block IIIF further adds Regional Military Protection, a
spot-beam capability that concentrates the power increase over a specific theater rather than
broadcasting it globally — exactly the `region` parameter `pnt.flex_power`'s code already threads
through to `payload_state.detail["flex_power_region"]`
(`engine/buscommands.py:pnt.flex_power`, code comment citing IS-GPS-200E and the GAO M-code report
per `docs/FUTURE-WORK.md` §2.2). This is a **space-segment-controlled** defense — it is something
the PNT payload operator (the cell that owns the GPS-analog satellite) does, distinct from anything
a GPS *user* can do.

**The user-segment (receiver-side) defense is a physically different mechanism the simulator does
not yet model at all: spatial-diversity anti-jam antennas.** A Controlled Reception Pattern Antenna
(CRPA) is a multi-element active antenna that exploits the fact that a legitimate GNSS signal and a
ground-based jammer generally arrive from different directions: it forms a beam toward the satellite
constellation and steers deliberate nulls toward detected jammer bearings, and is the standard
companion hardware to M-code military GPS receivers in NAVWAR (navigation warfare)-contested
environments ([GPS World, "Anti-jam technology: Demystifying the CRPA"](https://www.gpsworld.com/anti-jam-technology-demystifying-the-crpa/)
([Wayback](https://web.archive.org/web/2026/https://www.gpsworld.com/anti-jam-technology-demystifying-the-crpa/))).
This is a **user-equipment-side** defense — conceptually the mirror image of `pnt.flex_power`'s
space-segment defense, and currently has no engine analog at all, since the simulator's `pnt`
payload type only models the transmitting satellite, not a downstream GNSS-user asset whose receiver
posture could be separately hardened.

**Realistic baseline PNT accuracy, for authoring a `pnt` payload's default accuracy figure (added
for `BL-0052` grounding).** This topic's existing content covers jamming/spoofing/denial
operationally, but doesn't state what a `pnt` payload's own *undegraded* baseline accuracy should
be — the number a typed sub-schema's default (before any `pnt.set_integrity` degradation is
applied) would need. The official U.S. government performance standard commits GPS's civilian
Standard Positioning Service (SPS) to **≤9 meters horizontal accuracy at 95% confidence** (with
well-implemented receivers routinely doing better in practice, and the older 100 m/95%
specification superseded once Selective Availability was discontinued in 2000)
([GPS.gov / DOT, *Global Positioning System Standard Positioning Service Performance Standard*, 4th
ed.](https://rosap.ntl.bts.gov/view/dot/16930)). A vignette author's `pnt` payload sub-schema
should therefore default `integrity_mode="standard"` to an accuracy figure in the **single-digit-to-
low-tens-of-meters** band (not sub-meter — that requires augmentation this simulator doesn't model),
with `pnt.set_integrity`'s `degraded`/`protected` modes scaling that baseline up/down rather than
inventing an unrelated number.

### Sources

- *Inside GNSS, "GNSS Spoofing and Jamming in Eastern Europe"* — [live](https://insidegnss.com/gnss-spoofing-and-jamming-in-eastern-europe/)
  · [snapshot](https://web.archive.org/web/2026/https://insidegnss.com/gnss-spoofing-and-jamming-in-eastern-europe/)
  · accessed 2026-07-01.
- *U.S. Department of Transportation / GPS.gov, "Global Positioning System Standard Positioning
  Service Performance Standard", 4th edition* — [live](https://rosap.ntl.bts.gov/view/dot/16930)
  · [snapshot](https://web.archive.org/web/2026/https://rosap.ntl.bts.gov/view/dot/16930)
  · accessed 2026-07-05.
- *Breaking Defense, "As Baltics see spike in GPS jamming, NATO must respond"* (2024-01) — [live](https://breakingdefense.com/2024/01/as-baltics-see-spike-in-gps-jamming-nato-must-respond/)
  · [snapshot](https://web.archive.org/web/2026/https://breakingdefense.com/2024/01/as-baltics-see-spike-in-gps-jamming-nato-must-respond/)
  · accessed 2026-07-01.
- *Spire Global, "GNSS interference report: Russia — Part 4 of 4: Black Sea & Romanian airspace"* — [live](https://spire.com/blog/space-reconnaissance/gnss-interference-report-black-sea-romanian-airspace/)
  · [snapshot](https://web.archive.org/web/2026/https://spire.com/blog/space-reconnaissance/gnss-interference-report-black-sea-romanian-airspace/)
  · accessed 2026-07-01.
- *Secure World Foundation, 2025 Global Counterspace Capabilities Report* — [live](https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026/https://www.swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-07-01.
- *GPS World, "Anti-jam technology: Demystifying the CRPA"* — [live](https://www.gpsworld.com/anti-jam-technology-demystifying-the-crpa/)
  · [snapshot](https://web.archive.org/web/2026/https://www.gpsworld.com/anti-jam-technology-demystifying-the-crpa/)
  · accessed 2026-07-01.

## 4. Operational Context

A real PNT operator's day-to-day threat picture is dominated by ambiguity, not clean binary
jam-or-clear signals: the Black Sea and Baltic patterns in §3 show interference that waxes and wanes
geographically and temporally, forcing operators (and downstream GNSS users — aviation, maritime,
military) to continuously assess whether a given fix is trustworthy rather than treating GNSS
availability as a fixed background assumption. This is directly relevant to this simulator's
attack-vs-environment telemetry disambiguation problem that [R131](R131-space-environment-and-space-weather-operations.md)
already names for space-weather effects: GNSS interference telemetry has the same disambiguation
need (is a degraded fix hostile jamming, hostile spoofing, or a benign multipath/atmospheric
artifact?), and a White Cell running a PNT-warfare vignette should expect Blue to face exactly that
judgment call, not a pre-labeled "you are being jammed" indicator.

## 5. Implementation Guidance

- **Keep jam and spoof as distinct `Outcome` values wherever a future PNT effect is modeled**, per
  §3's finding that they have different real signatures (denial vs. false-confidence deception) —
  this already matches the direction of `docs/FUTURE-WORK.md` item 14's `is_link_spoofed` addition;
  this topic supplies the operational-precedent justification for keeping that distinction rather
  than collapsing spoof into a jam variant.
- **`pnt.flex_power`'s `region` parameter should stay theater-scoped, not global, when a future
  effect model consumes it** — per §3, real Regional Military Protection is a deliberate spot-beam
  trade-off (protect one theater's M-code margin without broadcasting the power increase, and its
  civil-signal cost, everywhere) — a future consuming feature that applies `flex_power_region`
  globally would misrepresent the real capability's actual trade-off.
- **A future receiver-side defense (CRPA/anti-jam posture) belongs on a GNSS-*user* asset, not on
  the `pnt` payload type.** Per §3's space-segment/user-segment distinction, `pnt.flex_power` and
  `pnt.set_health_flag` are already correctly modeled as actions the *transmitting* satellite's
  operator takes; a CRPA-equivalent defense is a property of a *receiving* asset (a Blue/Red
  satellite or ground asset that consumes PNT, not the PNT satellite itself) and has no current
  engine home — do not bolt it onto `PayloadState` for the `pnt` type, since that conflates the two
  sides of the same real-world defense pairing.
- **Do not treat GNSS interference telemetry as self-labeling.** Per §4, a future PNT-warfare
  vignette or telemetry signature should follow the same "make the operator disambiguate" pattern
  `engine/telemetry.py`'s existing attack-signature model already uses for jam/cyber/DE — not surface
  a pre-classified "spoofing detected" flag, which would remove the real judgment call this topic's
  operational context describes.
- **A vignette-authoring `pnt` payload sub-schema's default accuracy field should sit in the
  single-digit-to-low-tens-of-meters band** (per the SPS baseline above), not sub-meter — and
  `pnt.set_integrity`'s degraded/protected modes should scale that authored baseline, not replace
  it with an unrelated hardcoded figure.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) — the existing home of the `pnt.*` verb table this topic grounds;
any future receiver-side (CRPA-equivalent) PNT defense feature should cite this topic directly
rather than re-deriving the space-segment/user-segment distinction. The forthcoming Vignette
Creator Feature Specification (`docs/pipeline/backlog.md` `BL-0052`) depends on this topic's
baseline-accuracy subsection above for its typed PNT payload sub-schema.

## 7. Related Topics

[R109](R109-sensor-operations.md) (Sensor Operations — the `PayloadState`/payload-type model `pnt`
extends), [R110](R110-communications.md) (Communications — the link-quality/denial mechanics this
topic's GNSS case parallels), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic
Warfare — the jamming-taxonomy sibling this topic's GNSS-specific defenses sit beside),
[R129](R129-sigint-collection-and-geolocation-accuracy.md) (SIGINT Collection — geolocating a
detected jammer, a distinct downstream question from this topic's jam/spoof/defense scope),
`docs/research/05-mission-types-and-counters.md` §4 (the pre-existing mission-type primer already
cited by `pnt.flex_power`'s code comment).
