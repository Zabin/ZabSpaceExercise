# R317 — Space Operator Perspective (Historical Evolution)

> **Document ID:** R317
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R301](R301-campaign-design.md), [R302](R302-operational-art.md), [R305](R305-mission-analysis.md), [R312](R312-space-strategy.md)
> **Referenced By:** —
> **Produces:** the historical-evolution narrative that frames why the simulator's load-bearing
> invariants (plan-first, fog-of-war at the session boundary, sub-stepped clock, cyber-as-exception)
> are operator-mindset-correct, not arbitrary engineering choices
> **Feature Mapping:** vignette authoring generally (`docs/scenarios/`), the capstone Vignette 8 and
> any future vignette modeling C2 delegation/autonomy, White Cell facilitator design (DOM-003),
> Red AI posture legibility (DOM-008 §3), future SDA-workflow and constellation-management features
> **Related Topics:** [R102](R102-space-domain-awareness.md) (Space Domain Awareness),
> [R105](R105-custody-theory.md) (Custody Theory), [R118](R118-space-surveillance-networks.md)
> (Space Surveillance Networks), [R120](R120-access-window-and-geometry-planning.md) (Access Window
> and Geometry Planning), [R127](R127-conjunction-assessment-and-collision-avoidance.md) (Conjunction
> Assessment), [R312](R312-space-strategy.md) (Space Strategy), [R313](R313-maritime-operator-perspective.md)
> (Maritime Operator Perspective), [R314](R314-land-operator-perspective.md) (Land Operator
> Perspective), [R315](R315-air-operator-perspective.md) (Air Operator Perspective),
> [R316](R316-joint-and-combined-operations.md) (Joint and Combined Operations Perspective),
> [`research/01-doctrine-western.md`](../01-doctrine-western.md)
> **Last Reviewed:** 2026-06-28
> **Primary Sources Consulted:** 11

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

[R313](R313-maritime-operator-perspective.md)–[R316](R316-joint-and-combined-operations.md) each
import a mature *other* domain's operator mindset as an analogy source for orbital operations. This
topic does the complementary thing the tier was still missing: it traces the **space domain's own**
operator mindset across its historical arc — from a supporting capability flown by communicators and
engineers, to an independently theorized warfighting domain with its own C2 doctrine, its own
domain-awareness discipline, and its own decision-making framework. An implementer who only sees the
simulator's current rules (fog-of-war at the session boundary, plan-first orders, sub-stepped clock,
the five-D severity ladder) needs to know *why* a space operator thinks this way and not some other
way — and the answer is mostly historical: each invariant is the doctrinal residue of a specific
operational lesson learned the hard way, not an arbitrary design choice. This topic is the
narrative spine the rest of [R100](R100-index.md) (technical/operational mechanics) and
[R300](R300-index.md) (strategic/operational-art framing) sit inside.

## 2. Scope

Covers the *evolution of the space operator's mental model, command relationships, and planning
approach* across eight stages: early space support, space as a contested warfighting domain, space
domain awareness, the orbital-mechanics-as-environment perspective (with explicit land/air/maritime
maneuver comparison), space C2 evolution, space's role in joint warfare, a comparative
decision-making framework, and forward-looking evolution (autonomy, proliferation, commercial
integration, servicing). Does **not** catalogue spacecraft programs, sensor specifications, or
platform engineering — those are covered, where the simulator needs them, by the relevant
[R100](R100-index.md)-tier topic (orbital mechanics: [R101](R101-orbital-mechanics-for-operations.md);
custody: [R105](R105-custody-theory.md); SSN: [R118](R118-space-surveillance-networks.md); conjunction
assessment: [R127](R127-conjunction-assessment-and-collision-avoidance.md)) and is referenced rather
than re-derived here. Does not restate [R312](R312-space-strategy.md)'s strategic-school framing or
[`research/01-doctrine-western.md`](../01-doctrine-western.md)'s current-doctrine corpus — this topic
is the *historical path that produced* the doctrine those documents describe synchronically.

## 3. Concepts

### 3.1 Early Space Support Era — "space enables other domains"

**Key terminology.** *Force enhancement* (the doctrinal label, still used today, for space
capabilities that multiply the effectiveness of terrestrial forces rather than act independently);
the four original force-enhancement missions — strategic reconnaissance, communications, navigation,
missile warning — plus environmental monitoring (weather).

**Operator mental model.** The earliest space operators (CORONA-era photo-reconnaissance crews,
early SATCOM and navigation system operators) understood themselves as an extension of the
intelligence and communications professions, not as a separate warfighting community. CORONA
(operational 1960–1972, declassified by executive order 1995-02-22) framed its own product as
*film returned to Earth for human photo-interpretation*, not a real-time operational picture — the
operator's job was collection and physical recovery, with the decision-relevant product arriving
days to weeks later
([CIA, "CORONA: America's First Imaging Satellite Program"](https://www.cia.gov/legacy/museum/exhibit/corona-americas-first-imaging-satellite-program/)).
This is the formative case of the mindset this section names: *space enables*, it does not itself
decide or act — the terrestrial commander remains the locus of decision, and the space operator's
measure of success is whether the terrestrial commander got the product (imagery, a fix, a warning,
a communications path) in time to use it.

**Operational principles / assumptions.** Centralized national-level ownership of space assets
(reconnaissance and missile-warning satellites were treated as strategic national assets, controlled
far above any theater commander) with collection requirements flowing down from national
intelligence priorities, not from a deployed force's immediate tactical need. Decision timelines were
long — CORONA's days-to-weeks film-return cycle, and even the 1973-operational Defense Support
Program missile-warning constellation's minutes-scale alert timeline, were both far slower than the
contemporaneous terrestrial battle rhythm they fed into. The 1990–1991 Gulf War is the doctrinal
inflection point where this changed: Operation Desert Storm is widely characterized as the "first
space war" because GPS navigation (still pre-Full Operational Capability), SATCOM, missile early
warning, and weather support were employed at an unprecedented, tactically-integrated scale —
over 60 military and 20 commercial satellites supporting coalition operations — making space support
materially load-bearing for a terrestrial campaign for the first time in a way every later
joint-doctrine document points back to
([RUSI Journal, "The first space war: the contribution of satellites to the Gulf War," 1991](https://www.tandfonline.com/doi/abs/10.1080/03071849108445553);
[U.S. Army, "SMDC History: 25 years since first 'Space War'"](https://www.army.mil/article/161173/smdc_history_25_years_since_first_space_war)).

**Command structures.** Space assets were owned and tasked by national-level organizations
(intelligence community for reconnaissance, separate Service commands for SATCOM/navigation/missile
warning) entirely outside the terrestrial commander's chain — the terrestrial commander received
*products*, not *control*. This produced a durable command-relationship pattern: space support is a
supporting-command function exercised through a request-and-tasking interface, not an organic asset
the supported commander commands directly — a pattern this simulator's own White/Blue/Red cell split
echoes structurally (the cells request/receive effects through the SessionAPI tasking interface
rather than directly manipulating engine state).

**Vulnerabilities / limitations.** Single-purpose, low-redundancy constellations (a handful of
missile-warning or photo-reconnaissance satellites, each individually mission-critical); long
collection-to-product latency; no concept yet of an adversary actively contesting the space layer
itself — vulnerability was treated as a reliability/coverage-gap problem, not an adversarial-attack
problem.

**Failure modes / lessons learned.** Treating space support as background infrastructure rather than
a contestable capability is precisely the assumption the next era (§3.2) overturned — and the
overturning was driven by adversary action (counterspace testing), not by space operators
themselves discovering the gap.

**Implications for future space operations.** The "space enables" mindset never disappears — it is
still the correct frame for the majority of space missions (ISR, SATCOM, PNT, missile warning,
weather) even after space became contested; what changed in §3.2 is that the *enabling* mission now
has to be actively defended, not that the enabling mission stopped mattering.

#### Sources

- *CIA, "CORONA: America's First Imaging Satellite Program"* —
  [live](https://www.cia.gov/legacy/museum/exhibit/corona-americas-first-imaging-satellite-program/)
  · [snapshot](https://web.archive.org/web/2026/https://www.cia.gov/legacy/museum/exhibit/corona-americas-first-imaging-satellite-program/)
  · accessed 2026-06-28.
- *RUSI Journal, "The first space war: the contribution of satellites to the Gulf War"* (1991) —
  [live](https://www.tandfonline.com/doi/abs/10.1080/03071849108445553)
  · [snapshot](https://web.archive.org/web/2026/https://www.tandfonline.com/doi/abs/10.1080/03071849108445553)
  · accessed 2026-06-28.
- *U.S. Army, "SMDC History: 25 years since first 'Space War'"* —
  [live](https://www.army.mil/article/161173/smdc_history_25_years_since_first_space_war)
  · [snapshot](https://web.archive.org/web/2026/https://www.army.mil/article/161173/smdc_history_25_years_since_first_space_war)
  · accessed 2026-06-28.

### 3.2 Space as a Warfighting Domain — from enabler to contested terrain

**Key terminology.** *Counterspace* (offensive/defensive actions against space capabilities);
*space control* (the competency that produces space superiority, per the 2020 *Space Capstone
Publication*); *mission assurance* (designing/operating so the mission survives degradation, not
just the platform).

**Operator mental model shift.** The 2007-01-11 Chinese SC-19 direct-ascent ASAT test against the
defunct Fengyun-1C weather satellite — generating the largest deliberate debris-creating event in
the tracked catalog at the time — is the doctrinal watershed event most-cited as forcing Western
space operators to internalize that the enabling layer itself could be deliberately attacked, not
merely degraded by reliability/coverage gaps as in §3.1's mindset
([NASA ODPO Quarterly News, Q1 2008](https://orbitaldebris.jsc.nasa.gov/quarterly-news/pdfs/odqnv12i2.pdf)).
The operator's question changed from "is the satellite working" to "is the satellite being actively
denied, and by whom, and can the mission survive that" — the mission-assurance mindset.

**Operational principles.** US Space Command was originally established in 1985, disestablished in
2002 with its forces and missions absorbed into US Strategic Command, then reestablished as a
standalone geographic combatant command on 2019-08-29 — explicitly to give space a dedicated
warfighting command structure separate from the strategic-deterrence-focused STRATCOM
([SpacePolicyOnline, "U.S. Space Command Reestablished After 17-Year Hiatus"](https://spacepolicyonline.com/news/u-s-space-command-reestablished-after-17-year-hiatus/)).
The U.S. Space Force followed as an independent Service on 2019-12-20 under the FY2020 NDAA, and
the 2020 *Space Capstone Publication — Spacepower* then articulated, for the first time, an
independent spacepower theory naming **space superiority** (freedom of action in/from/to space for
friendly forces while denying the same to an adversary) as the strategic end-state and **space
control** as the operational competency that produces it — the superiority→control→counterspace
hierarchy [`research/01-doctrine-western.md`](../01-doctrine-western.md) §1 documents in full.

**Assumptions / constraints.** Space superiority is now doctrinally framed as *scoped and bounded* —
the 2025 *Space Warfighting: A Framework for Planners* introduces explicit spatial (general vs.
local) and temporal (persistent vs. temporary) axes, and CSO Gen. B. Chance Saltzman's public framing
of **"mutual denial"** (protect what you have, deny the adversary what they have) treats stable,
less-than-total outcomes as a legitimate operational end-state, not a failure to achieve absolute
control ([`research/01-doctrine-western.md`](../01-doctrine-western.md) §1). This is the doctrinal
ancestor of [R312](R312-space-strategy.md)'s point that a vignette's victory conditions must not
collapse to a kill-count.

**Failure modes.** An operator (or a White Cell scenario) that treats space control as a binary
"controls space: yes/no" switch repeats the pre-2007 mindset error this section documents — control
is local (to a regime/volume) and temporal (to a window), never global and permanent.

**Implications.** Resilience and mission assurance — architecting for graceful degradation under
attack rather than assuming an undegraded baseline — are now first-order design requirements for any
space system, not an afterthought; this is the doctrinal root of why this simulator treats most
effects as *reversible* (deceive/disrupt/deny/degrade) with destruction rare and consequence-gated,
echoing real doctrine's emphasis on contested-but-recoverable operations over attrition warfare
(MSTR-003 §5; [R312](R312-space-strategy.md) §3's debris-externality discussion).

#### Sources

- *NASA ODPO Quarterly News, Q1 2008* —
  [live](https://orbitaldebris.jsc.nasa.gov/quarterly-news/pdfs/odqnv12i2.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://orbitaldebris.jsc.nasa.gov/quarterly-news/pdfs/odqnv12i2.pdf)
  · accessed 2026-06-28.
- *SpacePolicyOnline, "U.S. Space Command Reestablished After 17-Year Hiatus"* (2019-08-29) —
  [live](https://spacepolicyonline.com/news/u-s-space-command-reestablished-after-17-year-hiatus/)
  · [snapshot](https://web.archive.org/web/2026/https://spacepolicyonline.com/news/u-s-space-command-reestablished-after-17-year-hiatus/)
  · accessed 2026-06-28.
- *USSF Space Capstone Publication — Spacepower* (2020-08-10) — see
  [`research/01-doctrine-western.md`](../01-doctrine-western.md) §1 for the full citation this
  section relies on rather than re-citing.

### 3.3 Space Domain Awareness Evolution — from tracking to understanding

**Key terminology.** *Space Situational Awareness (SSA)* — the older term, now retired in USSF
doctrine; *Space Domain Awareness (SDA)* — the current term; the detect→track→characterize→attribute
chain ([R102](R102-space-domain-awareness.md) §3); *custody* (a track held with enough confidence to
support a decision, [R105](R105-custody-theory.md)); *conjunction assessment* (predicting and
avoiding satellite-satellite or satellite-debris close approaches, [R127](R127-conjunction-assessment-and-collision-avoidance.md)).

**Operator mental model — the SSA-to-SDA shift.** An Air Force Space Command directive issued
around 2019 retired "Space Situational Awareness" in favor of "Space Domain Awareness" Service-wide,
explicitly because SSA had connotations of a *benign-environment* mindset (deconflicting cooperative
orbits, the way air-traffic-control deconflicts a cooperative airspace) while SDA was meant to name
the broader, adversarial-environment discipline of *characterizing intent and threat*, not just
tracking position — explicitly modeled on the Navy's "maritime domain awareness" framing
([SpaceNews, "Air Force: SSA is no more; it's 'Space Domain Awareness'"](https://spacenews.com/air-force-ssa-is-no-more-its-space-domain-awareness/);
formalized later in [Space Doctrine Publication 3-100, *Space Domain Awareness*, USSF, 2023-11](https://www.starcom.spaceforce.mil/Portals/2/SDP%203-100%20SDA%20Executive%20Summary.pdf)).
This terminology shift is the single clearest marker of the operator mindset shift this whole topic
traces: **tracking** an object (where is it) is a necessary but explicitly *insufficient* condition
for **understanding** it (what is it, what can it do, what is it likely to do, and under what
confidence is that assessment held) — SDP 3-100's four-stage chain (detect/track/characterize/
attribute, [R102](R102-space-domain-awareness.md) §3) operationalizes exactly that distinction.

**Decision-making with incomplete information.** A detection is not custody, and custody is not a
weapons-quality track — this simulator's own confidence-decay custody model
([R105](R105-custody-theory.md), `engine/custody.py`) is the engine-level expression of the SDA
chain's central discipline: an operator must act on a *confidence level*, continuously reassessed,
never on a completed, static picture. The 2009-02-10 Iridium 33 / Cosmos 2251 collision — the first
hypervelocity satellite-satellite collision in the catalog, at 789 km altitude over the Taymyr
Peninsula, generating over 2,000 catalogued debris fragments by 2011 — is the doctrinal forcing
event for routinized conjunction assessment as a standing operator workflow rather than an
occasional courtesy check: a same-day SOCRATES screening had predicted only a 584 m miss distance
hours before the actual collision, demonstrating that even a a same-day automated screening can
under-call risk when uncertainty in the underlying tracks is not propagated correctly
([NASA NTRS, "The Collision of Iridium 33 and Cosmos 2251: The Shape of Things to Come," 2010](https://ntrs.nasa.gov/api/citations/20100002023/downloads/20100002023.pdf)).
This event is the historical root of why this simulator's conjunction-assessment treatment
([R127](R127-conjunction-assessment-and-collision-avoidance.md)) is modeled as a continuously-updated
probabilistic miss-distance estimate, not a one-time pass/fail check.

**Pattern-of-life and intent assessment.** Characterizing an object's *mission* and *intent* — is a
maneuvering object repositioning for a benign purpose or shadowing a high-value asset — requires
sustained observation accumulated over many passes, the SDA equivalent of ground-domain pattern-of-
life analysis; a single detection or even a single track update cannot support an intent judgment,
only a accumulated custody history can.

**Failure modes.** Treating a track's existence as equivalent to operational knowledge (the
"tracking is understanding" conflation SDP 3-100 explicitly rejects) is the named historical failure
mode; a White Cell rule or vignette objective that grants Blue an action the moment a sensor produces
*any* detection, without distinguishing detection from custody from weapons-quality track, repeats
exactly the mindset gap the SSA→SDA terminology change was meant to close.

**Implications for future SDA workflows.** Confidence levels, not binary detection flags, should be
the unit every SDA-facing UI surfaces — directly reinforcing this simulator's design choice to never
cache a track's engageability boolean and instead recompute confidence at the moment of use
([R105](R105-custody-theory.md) §5).

#### Sources

- *SpaceNews, "Air Force: SSA is no more; it's 'Space Domain Awareness'"* —
  [live](https://spacenews.com/air-force-ssa-is-no-more-its-space-domain-awareness/)
  · [snapshot](https://web.archive.org/web/2026/https://spacenews.com/air-force-ssa-is-no-more-its-space-domain-awareness/)
  · accessed 2026-06-28.
- *Space Doctrine Publication 3-100, Space Domain Awareness* (USSF, 2023-11) —
  [live](https://www.starcom.spaceforce.mil/Portals/2/SDP%203-100%20SDA%20Executive%20Summary.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.starcom.spaceforce.mil/Portals/2/SDP%203-100%20SDA%20Executive%20Summary.pdf)
  · accessed 2026-06-28.
- *NASA NTRS, "The Collision of Iridium 33 and Cosmos 2251: The Shape of Things to Come"* (2010) —
  [live](https://ntrs.nasa.gov/api/citations/20100002023/downloads/20100002023.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20100002023/downloads/20100002023.pdf)
  · accessed 2026-06-28.

### 3.4 Orbital Operations Perspective — orbital mechanics as the operational environment

**Key terminology.** *Delta-v* (the velocity-change "currency" a maneuver spends, finite and
non-replenishable on orbit absent servicing — see §3.8); *access window* (the bounded time interval
during which a channel — uplink, downlink, sensor, jam, engagement, RPO — is geometrically possible,
[R120](R120-access-window-and-geometry-planning.md)); *phasing* (adjusting orbital position along the
track, the orbital analog of "getting there first"); *relative motion* / *rendezvous and proximity
operations (RPO)* (operating in a moving, curved reference frame relative to another object, not a
fixed terrestrial grid).

**Operator mental model.** A space operator's "terrain" is not fixed ground but a continuously
evolving geometric relationship — Keplerian (plus J2 secular precession) orbital mechanics is the
environment itself, not an obstacle laid over a static map ([`research/04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md);
[R101](R101-orbital-mechanics-for-operations.md)). The operator does not choose to "go" to a
location at will the way a ground or air operator chooses a route; the operator chooses *when* to
act, because the access window — the time during which a given geometric relationship holds — is the
真 unit of opportunity, not distance or position. This is this simulator's load-bearing invariant 5
("sub-step the clock") expressed at the operator-mindset level: a coarse time step that skips a short
LEO access window destroys the only opportunity that window represented, because unlike a ground
unit that can simply move toward an objective whenever it chooses, the orbital operator cannot
manufacture an access window on demand.

**Delta-v as operational currency.** Because no current operational system replenishes propellant on
orbit at scale, every maneuver permanently spends a finite, non-renewable resource
([R112](R112-propulsion-and-maneuver-planning.md)) — the orbital analog of a unit's fuel state, except
with no resupply convoy possible mid-mission for the overwhelming majority of fielded systems. This
makes maneuver decisions *irreversible budget commitments* in a way ground/air fuel decisions
usually are not (a ground vehicle can refuel; ground combat fuel logistics is a sustainment problem,
not a fundamental scarcity). A space operator who maneuvers reflexively the way a ground operator
repositions reflexively will, in the overwhelming majority of real missions, shorten the mission's
total operational life — delta-v budgeting is a mission-duration decision, not a tactical
convenience.

**Comparison to land maneuver.** Land maneuver doctrine (mission command, IPB, the targeting cycle,
per [R314](R314-land-operator-perspective.md)) assumes a maneuver unit can reposition largely at
will, constrained by terrain, logistics, and threat — *when* to move is mostly a tactical choice. The
orbital operator's *when* is instead overwhelmingly an astrodynamic fact: a maneuver to reach a given
relative geometry can only execute at specific, computable phasing points, and committing late or
early can cost disproportionate delta-v or miss the window entirely. **Where the analogy fails:**
land terrain is largely static between observations (a hill does not move), while orbital "terrain"
— the relative geometry between any two objects — is in continuous, deterministic but rapid motion;
an orbital operator's IPB-equivalent (predicting access windows) must be continuously recomputed, not
periodically updated from a relatively stable picture the way terrain intelligence is.

**Comparison to air maneuver.** Air maneuver (per [R315](R315-air-operator-perspective.md)) shares
the orbital domain's three-dimensional, time-perishable-resource character (CAP windows, tanker
tracks, ATO cycle timing) more closely than land maneuver does, and §3.5/§3.6 below draw directly on
that affinity for C2 lessons. **Where the analogy fails:** an aircraft can change its flight path
nearly arbitrarily within its performance envelope at the pilot's discretion in real time; an orbital
object's future position is *fully determined* by its current state and any planned maneuver — there
is no equivalent of "the pilot decided to bank left" as an in-the-moment improvisation once a
trajectory is committed, because every maneuver must be planned, executed at a computed window, and
then the resulting trajectory is fixed by physics until the next planned maneuver. Air maneuver's
moment-to-moment tactical freedom has no true orbital analog.

**Comparison to maritime maneuver.** Naval maneuver (per [R313](R313-maritime-operator-perspective.md))
shares the orbital domain's emphasis on *persistence* (a ship on station, like a satellite in its
operational slot, represents a standing commitment rather than a one-time event) and *distributed
operations* (a dispersed fleet, like a distributed constellation, trades single-point capability for
survivability). **Where the analogy fails:** a ship can loiter indefinitely on station, consuming
fuel/stores at a sustainment-resupply-able rate; an unserviced satellite's station-keeping or
maneuver budget is a hard, non-resuppliable ceiling on how long it can hold its slot or how many
maneuvers it can still perform — the maritime "persistence" concept assumes a sustainment pipeline
the orbital domain has only just begun to develop (§3.8, on-orbit servicing).

**Constellation operations.** Operating several satellites as a coordinated set (CLAUDE.md's
"constellations ≤3 sats, each operated/monitored individually" scoping note) introduces a
coordination problem none of the three terrestrial domains map onto cleanly: relative phasing must
be maintained against natural perturbation-driven drift, and a single maneuver decision for one
satellite can be made meaningless if it desynchronizes the set's coverage geometry — closer to
naval formation-keeping than to land or air formation flying, but with no possibility of a quick
visual/radar-directed correction; correction is itself a planned, windowed maneuver
([R108](R108-constellation-operations.md)).

**Failure modes / lessons learned.** The single most common orbital-operator failure mode this
section's literature documents is *treating an access window as renewable on a tactical timescale*
— planning as if "if I miss this pass, I'll just catch the next one" carries the same low cost a
ground/air retasking decision usually does, when in fact a missed window can mean a multi-orbit or
multi-day delay (depending on regime) during which the tactical situation has moved on. The
simulator's plan-first invariant (CLAUDE.md, load-bearing invariant 4) and dry-run "why can't I?"
pattern ([R120](R120-access-window-and-geometry-planning.md)) exist specifically to make window
scarcity visible to the operator *before* commitment, not after a missed opportunity.

**Implications for future space operations.** As proliferated/distributed constellations (§3.8)
multiply the number of simultaneously relevant access-window decisions an operator must track, the
orbital domain's existing window-scarcity discipline becomes a scaling problem before it becomes an
autonomy problem — informing why automation (§3.5) is being adopted fastest for window/contact
scheduling rather than for higher-stakes engagement decisions.

#### Sources

- [`research/04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md) and
  [R101](R101-orbital-mechanics-for-operations.md) (the simulator's existing orbital-mechanics
  grounding this section specializes to the operator-mindset question rather than re-deriving).
- [R313](R313-maritime-operator-perspective.md), [R314](R314-land-operator-perspective.md),
  [R315](R315-air-operator-perspective.md) (the comparison domains' own mental-model sections, cited
  in full there rather than re-cited here).

### 3.5 Space Command and Control Evolution

**Key terminology.** *Mission Operations Center (MOC)* (the ground-segment facility that commands
and monitors a spacecraft); *Combined Space Operations Center (CSpOC)* (the multinational
operational C2 node for space superiority operations); *battle management* (real-time tasking and
deconfliction of a contested, dynamic operational picture); *human-machine teaming* (a decision loop
where automation handles routine tasking and a human retains authority over consequential decisions).

**Ground control heritage.** Space C2 began as, and for the large majority of missions remains, a
ground-control model: a MOC staffed by flight controllers commands a spacecraft during scheduled
contact windows and otherwise has no real-time visibility or control — the spacecraft executes
autonomously (or simply coasts) between contacts ([R106](R106-mission-operations.md),
[R107](R107-ground-segment-operations.md)). This is the direct historical ancestor of this
simulator's command_uplink/telemetry_downlink access-channel model (CLAUDE.md, "six access
channels") — the ground-control heritage is *why* uplink/downlink are window-gated channels rather
than an always-available link.

**Distributed and centralized control.** The Joint Space Operations Center, established 2005-05-18,
was redesignated the Combined Space Operations Center on 2018-07-18 specifically to formalize
multinational (initially US/UK/Australia/Canada) shared space-superiority C2 — a deliberate move
toward a CSpOC-as-single-coordinating-node model, analogous to the air domain's AOC/JFACC
construct ([R315](R315-air-operator-perspective.md) §3.10) but for space tasking and battle
management rather than air tasking
([Wikipedia/DVIDS coverage of the 2018-07-18 Vandenberg redesignation ceremony](https://www.dvidshub.net/image/4576717/combined-space-operations-center-established-vandenberg-afb);
[U.S. Strategic Command, CSpOC establishment article](https://www.stratcom.mil/Media/News/News-Article-View/Article/1579497/combined-space-operations-center-established-at-vandenberg-afb/)).
This is the space domain's own version of the air domain's centralized-control answer to a scarce,
shared, contested resource — the same structural pattern [R315](R315-air-operator-perspective.md) §4
names at the air-domain level recurs here because it is doctrine's general answer to operating a
fast, contested, resource-constrained domain, not an air-domain peculiarity.

**Autonomy and human-machine teaming.** As constellations proliferate (§3.8) faster than MOC
staffing can scale 1:1, the operator mindset is shifting from "a human commands every contact" toward
"a human sets policy/exception thresholds and automation executes routine tasking, escalating only
exceptions" — the same human-machine-teaming pattern decision science names generally
([R200](R200-index.md) tier) now specifically appearing in space-domain battle management
literature discussing autonomous conjunction-avoidance maneuver execution and automated
contact scheduling. **Decision authority and delegation** follow the same logic as the air domain's
centralized-command/decentralized-execution resolution ([R315](R315-air-operator-perspective.md)
§3.8) but with a space-specific wrinkle: because access windows are short and infrequent relative to
a continuous air-defense problem, pre-delegated authority for time-critical actions (e.g.,
autonomous collision-avoidance maneuver execution without waiting for ground confirmation) is
adopted earlier and more readily in space C2 than analogous full engagement authority typically is
in the air or land domains, precisely because the alternative — waiting for a ground contact window
that may not arrive before the event — is often simply unavailable.

**Automation risk.** The literature's named failure mode is *automation operating on a stale or
miscalibrated input without a human noticing in time* — the same SOCRATES under-call that preceded
the 2009 Iridium/Cosmos collision (§3.3) is also a battle-management lesson: an automated screening
tool's output is only as trustworthy as the uncertainty propagation behind it, and over-trusting an
automated "no conjunction" result without an analyst spot-check was a contributing factor named in
post-event analysis. Rules of engagement for any future autonomous space-defensive action inherit
this caution directly.

**Implications.** A White Cell or Red AI feature modeling realistic space C2 should model the
MOC/CSpOC-style centralized node explicitly (the White Cell facilitator is already structurally this
node, per [R315](R315-air-operator-perspective.md) §3.10's AOC-analogy point) and should treat any
future autonomy feature (autonomous maneuver, automated tasking) as inheriting the SOCRATES-style
stale-input risk unless an explicit confidence/uncertainty signal accompanies the automated output.

#### Sources

- *DVIDS, "Combined Space Operations Center established at Vandenberg AFB"* (2018-07-18) —
  [live](https://www.dvidshub.net/image/4576717/combined-space-operations-center-established-vandenberg-afb)
  · [snapshot](https://web.archive.org/web/2026/https://www.dvidshub.net/image/4576717/combined-space-operations-center-established-vandenberg-afb)
  · accessed 2026-06-28.
- *U.S. Strategic Command, "Combined Space Operations Center established at Vandenberg AFB"* —
  [live](https://www.stratcom.mil/Media/News/News-Article-View/Article/1579497/combined-space-operations-center-established-at-vandenberg-afb/)
  · [snapshot](https://web.archive.org/web/2026/https://www.stratcom.mil/Media/News/News-Article-View/Article/1579497/combined-space-operations-center-established-at-vandenberg-afb/)
  · accessed 2026-06-28.

### 3.6 Space Operations in Joint Warfare

**Key terminology.** *Force enhancement* (§3.1's original framing, still doctrinally current);
*Joint All-Domain Operations (JADO)* (synchronized integration of effects across air, land,
maritime, cyberspace, and space, plus the EMS); *cross-domain dependency* (a capability in one
domain that requires another domain's contribution to function).

**What space contributes / what space requires.** [R315](R315-air-operator-perspective.md) §3.20
already documents, at the air-domain-analogy level, the doctrinal point that matters most here:
space support to the other domains (PNT, SATCOM, missile warning, weather, ISR cueing) was
historically *assumed* largely uncontested, and JADO doctrine's central shift is to stop assuming
that and instead plan explicit degraded-space-support contingencies into every other domain's
campaign — the inverse dependency (land/air/maritime/cyber effects supporting space operations, e.g.
ground-based counter-counterspace, cyber defense of ground segments) is the less-discussed but
equally real other half of the same integration requirement
([USAF Role in Joint All-Domain Operations](https://www.doctrine.af.mil/Portals/61/documents/Notes/Joint%20All-Domain%20Operations%20Doctrine--CSAF%20signed.pdf)).
[R316](R316-joint-and-combined-operations.md) covers the general joint command-relationship and
JPP vocabulary this integration runs through; this section names only the space-specific instance.

**Support to land/air/naval forces.** Each Service-component's dependency on space support is
qualitatively different: land forces depend most heavily on PNT and SATCOM for dispersed,
beyond-line-of-sight operations; air forces depend most heavily on missile warning, weather, and
ISR cueing for strike-package planning ([R315](R315-air-operator-perspective.md) §3.20); naval
forces depend most heavily on SATCOM and ISR for over-the-horizon targeting and on PNT for open-ocean
navigation where terrestrial aids do not reach. A space operator supporting joint operations must
therefore prioritize a finite tasking/bandwidth/collection capacity against qualitatively different
component demands, not a single undifferentiated "support the joint force" requirement.

**Cyber and electromagnetic integration.** Space, cyber, and EW are doctrinally treated as
increasingly inseparable — denying a space capability is achievable through a ground-segment cyber
intrusion (e.g. the well-documented 2022-02-24 Viasat KA-SAT modem-bricking attack, per
[`research/10-sources-and-methodology.md`](../10-sources-and-methodology.md) §7's canonical-source
registry) as readily as through an on-orbit or RF-spectrum action — which is precisely why this
simulator's cyber exception (not window-gated, resolved against
`{access_vector, success_prob, persistence, patchable}`, per CLAUDE.md) is doctrinally faithful: real
cyber threats to space systems do not respect orbital access geometry at all, attacking the
terrestrial/link segment instead.

**Dependencies — implications.** A multi-domain campaign plan that does not explicitly state its
space-support dependencies (which terrestrial effects assume PNT/SATCOM/ISR availability, and what
happens if that availability is denied) repeats the pre-JADO assumption error this section
documents; a future capstone-tier vignette pairing a space effect with a notional supported-domain
timeline ([R315](R315-air-operator-perspective.md) §3.20's "JADO-framed capstone" implementation
note) is the concrete way to extend this simulator from single-domain space operations toward the
joint-integration framing real doctrine now requires.

#### Sources

- See [R315](R315-air-operator-perspective.md) §3.20 and [R316](R316-joint-and-combined-operations.md)
  for the full JADO/USAF-doctrine citations this section relies on rather than re-citing in full.

### 3.7 Space Operator Decision-Making Framework

**Mission objectives.** A space operator's objectives are framed around *access and denial over a
regime, for a window, in service of a purpose* ([`research/01-doctrine-western.md`](../01-doctrine-western.md)
§1) — not territory held, sorties flown, or ships on station, though each of those framings appears
as a structural analog (§3.4).

**Uncertainty and threat assessment.** The operator's threat picture is built from the SDA chain
(§3.3) — confidence-weighted, continuously revised, never complete — and threat assessment is
explicitly an *attribution* problem as much as a detection problem: a degraded link could be a
natural RF interference event, a hardware fault, or a deliberate jam, and doctrine's SDA framework
exists specifically because distinguishing those requires characterization and pattern-of-life
history, not a single measurement.

**Courses of action, risk, resource allocation.** COA comparison for a space operator weighs
delta-v expenditure (§3.4, often irreversible for the mission's remaining life), access-window
opportunity cost (acting now forecloses what the next window could have allowed), and attribution
risk (an overtly offensive action invites the debris/escalation costs [R312](R312-space-strategy.md)
§3 and [R304](R304-escalation-dynamics.md) name) — a risk calculus with no close single-domain analog,
since it combines a maritime-like persistence/sustainment concern, an air-like time-perishable-window
concern, and a domain-unique irreversible-resource and shared-commons-externality concern
simultaneously.

**Escalation management and survivability.** Because most space effects are reversible
(deceive/disrupt/deny/degrade) and destruction is rare and strategically costly to the *initiator*
as well as the target (the debris externality, [R312](R312-space-strategy.md) §3), a space operator's
default escalation posture favors reversible action even when irreversible action is technically
available — the doctrinal opposite of, e.g., a land operator's targeting-cycle bias toward decisive
destruction of a validated target when ROE permits.

**Comparative table — decision style by domain.**

| Domain | Primary planning currency | Dominant time pressure | Reversibility default |
|---|---|---|---|
| Land ([R314](R314-land-operator-perspective.md)) | Terrain and maneuver space | Deliberate-cycle (hours–days), punctuated by close-combat urgency | Often irreversible (close combat) |
| Air ([R315](R315-air-operator-perspective.md)) | Sortie/tanker/AOC throughput | Compressed (ATO cycle to TST minutes) | Mixed — kinetic strike common, but contested-domain control is graded |
| Maritime ([R313](R313-maritime-operator-perspective.md)) | Persistence/sustainment on station | Slow (transit/loiter timescales) | Mixed — sea denial often reversible, strike not |
| Joint ([R316](R316-joint-and-combined-operations.md)) | Synchronization across domains | Set by the slowest-responding domain | Inherits from the contributing domains |
| **Space** | **Delta-v + access-window opportunity** | **Bimodal: long collection latency (§3.1) or seconds-scale autonomous response (§3.5)** | **Reversible-by-default, destruction rare/costly to initiator** |

**Similarities and differences.** Space shares the air domain's time-perishable-window discipline and
the maritime domain's persistence/sustainment framing, but its reversibility default and its
irreversible-resource (delta-v) constraint have no precise single-domain match — which is exactly why
[R313](R313-maritime-operator-perspective.md)–[R316](R316-joint-and-combined-operations.md) are each
*partial* analogy sources rather than one being sufficient on its own, the structural reason this
tier added four separate domain-analogy chapters instead of one.

**Implications.** A White Cell or vignette-authoring decision-support tool should surface delta-v
remaining, access-window countdown, and attribution confidence as the three operator-facing decision
inputs this framework identifies as domain-specific — distinct from a land/air/maritime decision
console's terrain-picture, fuel-state, or station-status equivalents.

#### Sources

- Synthesizes [R313](R313-maritime-operator-perspective.md), [R314](R314-land-operator-perspective.md),
  [R315](R315-air-operator-perspective.md), [R316](R316-joint-and-combined-operations.md), and
  [R312](R312-space-strategy.md) §3 — see each topic's own Sources sections for primary citations;
  no new external sources are introduced in this comparative synthesis.

### 3.8 Future Evolution

**Key terminology.** *Proliferated architecture* (many smaller, individually less-critical
satellites replacing a few high-value ones); *responsive space* (rapid, on-demand launch/reconstitution
of capability); *on-orbit servicing, assembly, and manufacturing (OSAM)*; *space logistics* (the
emerging discipline of resupply, refueling, and repair on orbit).

**Autonomous spacecraft and AI-enabled operations.** The trend identified in §3.5 (automation
absorbing routine tasking) is accelerating toward AI-assisted anomaly detection, automated
conjunction-screening triage, and (more cautiously, given the SOCRATES-style automation-risk lesson)
autonomous maneuver execution — the operator mindset shift is from "operator commands every action"
toward "operator sets policy and reviews automation's judgment by exception," mirroring the
human-machine-teaming trajectory other domains are also on but arriving earlier in space due to the
window/staffing-scaling pressure named in §3.5.

**Proliferated and distributed constellations.** The Space Development Agency, established
2019-03 (originally as the National Defense Space Architecture, renamed the Proliferated Warfighter
Space Architecture in early 2023), deploys capability in two-year "Tranches" specifically to trade
single-satellite criticality for distributed resilience — a deliberate architectural answer to the
counterspace threat §3.2 introduced: a constellation with many individually-replaceable satellites is
far harder to meaningfully degrade with any single counterspace action than the small, high-value
constellations §3.1's era fielded
([Space Development Agency](https://www.sda.mil/); [Via Satellite, "SDA Renames LEO Constellation to
Proliferated Warfighter Space Architecture," 2023-01-23](https://www.satellitetoday.com/government-military/2023/01/23/sda-renames-leo-constellation-to-proliferated-warfighter-space-architecture/)).
This directly reverses §3.1's command-relationship pattern too: proliferated tranches are fielded by
an acquisition-and-operations organization designed for rapid, iterative reconstitution rather than
the decades-long single-program ownership model CORONA-era systems exemplified.

**Responsive space.** Demonstrations of rapid, short-notice launch-on-demand (the doctrinal goal
behind "tactically responsive space" launch exercises) extend the proliferation logic to *time*:
the operator mindset shift is toward treating reconstitution itself as a planned operational
capability rather than a peacetime-only acquisition activity.

**Commercial space integration.** Commercial ISR tasking APIs, commercial SATCOM, and commercial
launch are increasingly treated as a doctrinally-recognized hybrid architecture component rather than
a purely civil/economic activity outside military planning — extending §3.6's joint-integration
point to a commercial-integration point with its own attribution and targeting-law complications
([R312](R312-space-strategy.md) is the strategic-frame topic that should absorb any future expansion
of this point; this section only names the trend).

**On-orbit servicing and debris management.** Northrop Grumman's Mission Extension Vehicle-1 (MEV-1)
docked with the Intelsat-901 communications satellite on 2020-02-25 — the first-ever docking with a
satellite not originally designed for docking, and the first docking between two commercial
spacecraft, restoring Intelsat-901 to revenue service by 2020-04-02 after towing it from a graveyard
orbit back into the geostationary arc
([SpaceNews, "Northrop Grumman's MEV-1 servicer docks with Intelsat satellite"](https://spacenews.com/northrop-grummans-mev-1-servicer-docks-with-intelsat-satellite/);
[Intelsat, "Historic First Docking of Mission Extension Vehicle with Intelsat 901 Satellite"](https://www.intelsat.com/newsroom/northrop-grumman-successfully-completes-historic-first-docking-of-mission-extension-vehicle-with-intelsat-901-satellite/)).
This is the first concrete operational evidence that §3.4's "delta-v is permanently spent, no
resupply" assumption is beginning to loosen for at least the GEO life-extension case — a future
operator mindset that includes "request a servicing mission" as a real, schedulable COA, not a
thought experiment, is now grounded in an actual flown precedent rather than speculative technology.
On the debris-management side, the FCC's 2022-09-29 "5-year rule" (replacing the prior 25-year
post-mission disposal guideline for LEO satellites, full compliance required from 2024-09-29) is the
clearest recent regulatory instance of the debris-externality strategic reasoning
([R312](R312-space-strategy.md) §3) being converted into a binding operational planning constraint —
mission planners must now design disposal into the mission timeline as a first-class requirement, not
an end-of-life afterthought
([FCC, "FCC Adopts New '5-Year Rule' for Deorbiting Satellites"](https://www.fcc.gov/document/fcc-adopts-new-5-year-rule-deorbiting-satellites-0)).

**Increasingly complex orbital environments.** The combined effect of proliferation (more objects),
debris accumulation (more uncontrolled objects), and commercial growth (more independently-operated
objects) compounds the SDA challenge (§3.3) and the conjunction-assessment workload
([R127](R127-conjunction-assessment-and-collision-avoidance.md)) simultaneously — the operator
mindset implication is that SDA and traffic-management capacity, not sensor count alone, will be the
binding constraint on how much proliferation the environment can actually sustain, the same
"the limiting resource is the processing/coordination capacity, not the raw collection capacity"
lesson [R315](R315-air-operator-perspective.md) §3.3 names for the air-ISR PED bottleneck, recurring
here for SDA.

**Implications for future space operations.** A simulator or decision-support tool built for this
emerging environment should model servicing, responsive reconstitution, and disposal-planning as
first-class operator decisions alongside the legacy five-D effects menu — not as a separate "future
work" bolt-on — because the historical arc this section documents shows each of these capabilities
is already operationally real, not speculative.

#### Sources

- *Space Development Agency* — [live](https://www.sda.mil/)
  · [snapshot](https://web.archive.org/web/2026/https://www.sda.mil/) · accessed 2026-06-28.
- *Via Satellite, "SDA Renames LEO Constellation to Proliferated Warfighter Space Architecture"*
  (2023-01-23) —
  [live](https://www.satellitetoday.com/government-military/2023/01/23/sda-renames-leo-constellation-to-proliferated-warfighter-space-architecture/)
  · [snapshot](https://web.archive.org/web/2026/https://www.satellitetoday.com/government-military/2023/01/23/sda-renames-leo-constellation-to-proliferated-warfighter-space-architecture/)
  · accessed 2026-06-28.
- *SpaceNews, "Northrop Grumman's MEV-1 servicer docks with Intelsat satellite"* (2020-02) —
  [live](https://spacenews.com/northrop-grummans-mev-1-servicer-docks-with-intelsat-satellite/)
  · [snapshot](https://web.archive.org/web/2026/https://spacenews.com/northrop-grummans-mev-1-servicer-docks-with-intelsat-satellite/)
  · accessed 2026-06-28.
- *Intelsat, "Historic First Docking of Mission Extension Vehicle with Intelsat 901 Satellite"* —
  [live](https://www.intelsat.com/newsroom/northrop-grumman-successfully-completes-historic-first-docking-of-mission-extension-vehicle-with-intelsat-901-satellite/)
  · [snapshot](https://web.archive.org/web/2026/https://www.intelsat.com/newsroom/northrop-grumman-successfully-completes-historic-first-docking-of-mission-extension-vehicle-with-intelsat-901-satellite/)
  · accessed 2026-06-28.
- *FCC, "FCC Adopts New '5-Year Rule' for Deorbiting Satellites"* (2022-09-29) —
  [live](https://www.fcc.gov/document/fcc-adopts-new-5-year-rule-deorbiting-satellites-0)
  · [snapshot](https://web.archive.org/web/2026/https://www.fcc.gov/document/fcc-adopts-new-5-year-rule-deorbiting-satellites-0)
  · accessed 2026-06-28.

## 4. Operational Context

The eight stages above are not a strict, non-overlapping timeline — they are cumulative layers a
real space operator today must hold simultaneously. A 2026 satellite operator still does §3.1's
force-enhancement mission (most satellites exist to enable something else), still operates inside
§3.2's contested-domain reality (any of those enabling missions can be actively denied), still
practices §3.3's SDA discipline continuously, is still bound by §3.4's orbital-mechanics environment
and §3.5's ground-control heritage (now layered with growing autonomy), still serves §3.6's joint
integration requirement, makes every decision through something like §3.7's framework, and is
increasingly operating inside §3.8's proliferated, serviceable, commercially-integrated environment.
The historical arc matters precisely because each later layer was added in response to a documented
operational failure or threat the earlier mindset alone could not handle — 2007's ASAT test forced
§3.2 onto a §3.1 mindset; 2009's collision forced §3.3's routinized conjunction-assessment discipline;
ongoing constellation scaling is forcing §3.5's automation shift. This simulator's own invariants
(plan-first, fog-of-war at the boundary, sub-stepped clock, cyber-as-exception, reversible-effects-
by-default) are each traceable to one or more of these layers, which is why a vignette author or
White Cell facilitator benefits from knowing the history, not just the current rule.

## 5. Implementation Guidance

**Transferable Principles for Space Operations** — the synthesis a vignette author, White Cell
facilitator, or decision-support-tool builder should carry forward from this chapter:

- **Space enables before it fights, and enabling never stops mattering.** Even a vignette built
  around contested space control should keep the force-enhancement mission (§3.1) visible as the
  *stakes* — Blue/Red are contesting space *because* a terrestrial or strategic purpose depends on
  it, not because space control is an end in itself ([R312](R312-space-strategy.md) §3).
- **Treat space control as graded and bounded, never binary.** §3.2's superiority-spectrum lesson
  (echoed at the air-domain level in [R315](R315-air-operator-perspective.md) §3.1) means any
  objective phrased as "controls space: yes/no" is a design smell — phrase it as access/denial over
  a named regime, for a named window, in service of a named purpose.
- **Distinguish detection, custody, and weapons-quality track explicitly, and surface confidence,
  not binary flags.** §3.3's SSA→SDA shift and the 2009 collision's SOCRATES under-call are the
  historical reasons this simulator's custody model decays confidence continuously
  ([R105](R105-custody-theory.md)) rather than caching an engageability boolean — any new SDA-facing
  UI or workflow should follow that same discipline.
- **Model delta-v and access windows as the operator's two scarce, non-renewable currencies**, with
  COA comparison weighing both explicitly (§3.4, §3.7) — this is the domain-specific risk calculus no
  single terrestrial-domain analogy fully captures; a future decision-support tool's COA-comparison
  view should surface both quantities, not just mission outcome probability.
- **Model the centralized space C2 node (White Cell / a future CSpOC-analog) as a standing process
  with named boards/cells**, not an ad hoc adjudicator each time (§3.5, [R315](R315-air-operator-perspective.md)
  §3.10) — and treat any future autonomy feature as inheriting the automation-risk lesson (an
  automated judgment is only as good as its uncertainty propagation) until an explicit confidence
  signal is attached.
- **State explicit cross-domain dependencies in any joint/multi-domain vignette** (§3.6) — which
  terrestrial effects assume space support, and what the vignette's intended consequence is if that
  support is denied — rather than leaving the dependency implicit.
- **Treat reversibility as the doctrinal default, with destruction rare and consequence-gated**
  (§3.2, §3.7) — this simulator's kinetic consequence-confirm gate and five-D severity ladder are
  historically grounded in the debris/shared-commons externality, not an arbitrary design throttle.
- **Build servicing, responsive reconstitution, and disposal-planning into future feature scope as
  first-class operator decisions**, not speculative future work (§3.8) — MEV-1 and the FCC 5-year
  rule are flown/regulatory precedent, not forecasts.

## 6. Feature Mapping

Vignette authoring generally (`docs/scenarios/`), the capstone Vignette 8 and any successor modeling
C2 delegation or autonomy, White Cell facilitator tooling (DOM-003), Red AI posture legibility
(DOM-008 §3 — a preset's place on the §3.2 graded-control spectrum and its §3.7 escalation posture
should be documented alongside its tactical parameters), and any future SDA-workflow, constellation-
management, or servicing/disposal-planning feature.

## 7. Related Topics

[R102](R102-space-domain-awareness.md) (Space Domain Awareness — §3.3's detect/track/characterize/
attribute chain in full), [R105](R105-custody-theory.md) (Custody Theory — the confidence-decay
mechanics §3.3/§5 depend on), [R108](R108-constellation-operations.md) (Constellation Operations —
§3.4/§3.8's coordination problem), [R112](R112-propulsion-and-maneuver-planning.md) (Propulsion and
Maneuver Planning — §3.4's delta-v currency), [R118](R118-space-surveillance-networks.md) (Space
Surveillance Networks), [R120](R120-access-window-and-geometry-planning.md) (Access Window and
Geometry Planning — §3.4's window-scarcity discipline), [R127](R127-conjunction-assessment-and-collision-avoidance.md)
(Conjunction Assessment — §3.3's 2009-collision grounding), [R301](R301-campaign-design.md) (Campaign
Design), [R302](R302-operational-art.md) (Operational Art), [R304](R304-escalation-dynamics.md)
(Escalation Dynamics — §3.7's reversibility-default reasoning), [R305](R305-mission-analysis.md)
(Mission Analysis), [R312](R312-space-strategy.md) (Space Strategy — the strategic frame §3.2/§3.7
ground), [R313](R313-maritime-operator-perspective.md) (Maritime Operator Perspective),
[R314](R314-land-operator-perspective.md) (Land Operator Perspective),
[R315](R315-air-operator-perspective.md) (Air Operator Perspective),
[R316](R316-joint-and-combined-operations.md) (Joint and Combined Operations Perspective) — the
tier's sibling domain-analogy chapters this topic's §3.4/§3.7 comparisons draw on directly,
[`research/01-doctrine-western.md`](../01-doctrine-western.md) (the current-doctrine corpus this
topic's historical arc leads into).
