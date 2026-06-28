# R313 — Maritime Operator Perspective

> **Document ID:** R313
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R301](R301-campaign-design.md), [R303](R303-deterrence-theory.md), [R304](R304-escalation-dynamics.md)
> **Referenced By:** —
> **Produces:** the cross-domain analogical vocabulary White Cell facilitators and vignette authors can use to
> explain orbital-regime control, custody, and constellation employment in terms borrowed from a domain
> (sea power) with a much longer doctrinal pedigree and a trainee-accessible intuition
> **Feature Mapping:** vignette authoring (`docs/scenarios/`), White Cell facilitator briefing material,
> capstone Vignette 8 and successor design, `redai.py` posture documentation
> **Related Topics:** [R301](R301-campaign-design.md) (Campaign Design), [R302](R302-operational-art.md) (Operational Art),
> [R303](R303-deterrence-theory.md) (Deterrence Theory), [R304](R304-escalation-dynamics.md) (Escalation Dynamics),
> [R312](R312-space-strategy.md) (Space Strategy), [R105](R105-custody-theory.md) (Custody Theory),
> [R108](R108-constellation-operations.md) (Constellation Operations), [R120](R120-access-window-and-geometry-planning.md)
> (Access Window and Geometry Planning)
> **Last Reviewed:** 2026-06-28
> **Primary Sources Consulted:** 7

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Naval officers have reasoned about command, control, and risk across durations of months and areas
of millions of square kilometers for over a century longer than anyone has reasoned about orbital
operations — and the two domains share a structural feature no land or air analogy shares as
cleanly: **both are fought across a contested, largely empty medium where presence is intermittent,
detection is uncertain, and the side that controls key geometry (a strait, an access window) controls
disproportionate freedom of action elsewhere.** This topic exists to give vignette authors, White
Cell facilitators, and `redai.py` posture writers a ready vocabulary — sea control, task groups,
convoy escort, ASW custody — that trainees already partially understand from popular culture and
professional military education, and that maps with unusual fidelity onto this simulator's orbital
concepts (access windows, custody decay, constellation employment, the five effect categories). It
is explicitly an **analogical grounding topic**, not a maritime-doctrine corpus in its own right —
where the analogy breaks down (the next section says where), that break is itself instructive.

## 2. Scope

Covers, for each of the 24 maritime operational concepts named below: the operational reasoning a
naval commander uses, the doctrinal assumptions that reasoning rests on, the concept's strengths and
weaknesses as an operational frame, the decision process it drives, how the commander manages
uncertainty within it, and — for every concept — an explicit orbital/space-force-employment analog.
Does **not** cover ship engineering, weapons-system technical specifications, or platform-by-platform
naval order of battle — per this topic's brief, the analogy is at the level of *operational concept*,
not technology. Does **not** re-derive deterrence theory or escalation-ladder theory from first
principles — those are [R303](R303-deterrence-theory.md) and [R304](R304-escalation-dynamics.md);
this topic supplies their *naval instantiation* and points back rather than restating. Where a
maritime concept has no useful orbital analog (this topic flags two: damage control's physical-crew
model, and chokepoints' true geographic chokepoint vs. orbital regime-transition cost), that
disanalogy is stated plainly rather than forced.

A note on form: the user-facing request behind this topic asks for 24 named concepts each addressed
along seven dimensions — broader than this tier's usual single-concept topic. Rather than force that
into the standard 3-8 page band (which would either omit concepts or thin each to a single sentence),
this topic is authored as the tier's deliberate single broad-survey exception, organized into nine
thematic clusters inside §3. A future split into per-cluster topics (e.g., a standalone "Convoy and
High-Value-Asset Escort" topic) is left as an `R3xx`-numbered option if a specific vignette or
`redai.py` posture later needs deeper treatment of one cluster than this survey provides.

## 3. Concepts

### 3.1 Sea control and sea denial

**Sea control** is the condition of having sufficient freedom of action on, over, and under a given
sea area to use it for one's own purposes — power projection, trade protection, amphibious lift —
while denying the same to an adversary; **sea denial** is the lesser, asymmetric goal of preventing an
adversary's use of an area without necessarily being able to use it oneself. [Julian Corbett's *Some
Principles of Maritime Strategy*](https://www.gutenberg.org/files/15076/15076-h/15076-h.htm) (1911)
supplies the foundational reasoning still cited in current doctrine: "command of the sea... means
nothing but the control of maritime communications," not physical occupation of water, because the
sea (unlike land) cannot be held — only the *use* of it can be contested. [Naval Doctrine Publication
1, *Naval Warfare*](https://cimsec.org/wp-content/uploads/2020/08/NDP1_April2020.pdf) (US Navy, April
2020) carries this forward but is explicit that the publication "does not clearly define sea control"
with operational precision, instead stating only that it requires control of surface, subsurface, and
air layers via "superior capabilities and capacities" — a doctrinal admission that sea control is a
*relative, graduated* condition, not a binary one earned and then permanently held.

*Operational reasoning:* a commander asks not "do I control this sea area" but "can I use it for
*this* purpose, against *this* opposition, for *this* window of time" — sea control is always
mission-and-area-scoped, never global. *Doctrinal assumption:* control is contestable and decays
without continued effort — there is no permanent command of an area, only sustained local advantage.
*Strength:* the relative framing avoids the trap of treating "winning" as total and permanent, which
keeps planning realistic about commitment and risk. *Weakness:* the same relativity makes sea control
hard to operationalize into a measurable end-state for an order — NDP-1's own admission that it lacks
a crisp definition is a real, cited doctrinal gap, not an artifact of this topic's summary.
*Decision process:* a commander allocates forces to achieve *local, temporary* control sufficient for
the mission at hand (e.g., control of a strait for the duration of a transit) rather than attempting
area-wide permanent dominance. *Uncertainty management:* because control is graduated and decays, a
commander continuously re-assesses rather than treating an initial assessment as durable — sea
control is monitored, not declared once. *Orbital analog:* this maps almost exactly onto this
simulator's access-window model — "space control" of a given orbital regime or ground-link corridor
is similarly local-and-temporal (you control access *during the window*, not permanently), and sea
denial maps onto a Red posture that can deny Blue's use of a regime (jam, dazzle, threaten engagement)
without itself having custody-quality access there — exactly the asymmetry [R120](R120-access-window-and-geometry-planning.md)'s
windowed-access model and [R105](R105-custody-theory.md)'s custody decay already encode numerically.

#### Sources

- *Julian S. Corbett, Some Principles of Maritime Strategy* (Longmans, Green & Co., 1911; Project
  Gutenberg ebook #15076) — [live](https://www.gutenberg.org/files/15076/15076-h/15076-h.htm)
  · [snapshot](https://web.archive.org/web/2026/https://www.gutenberg.org/files/15076/15076-h/15076-h.htm)
  · accessed 2026-06-28.
- *Naval Doctrine Publication 1, Naval Warfare* (US Navy, April 2020) — [live](https://cimsec.org/wp-content/uploads/2020/08/NDP1_April2020.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://cimsec.org/wp-content/uploads/2020/08/NDP1_April2020.pdf)
  · accessed 2026-06-28.

### 3.2 Fleet operations, task groups, and command relationships

A **fleet** is the standing administrative/operational organization of naval forces under a numbered
or named commander; a **task group** (and its subordinate task units/elements) is the temporary,
mission-tailored grouping actually formed for a given operation — the standard naval pattern of
*organizing around the mission, not the standing structure*. Command relationships among these
echelons are governed in US joint doctrine by [Joint Publication 3-32, *Command and Control for Joint
Maritime Operations*](https://irp.fas.org/doddir/dod/jp3_32.pdf) (Joint Chiefs of Staff), which
specifies that a maritime commander "will normally exercise OPCON [operational control] as a Service
component commander over their own Service forces, and TACON [tactical control] as a functional
component commander over other Services' forces made available for tasking" — a precise,
doctrinally-load-bearing distinction between *who can redirect a force's mission* (OPCON) and *who can
direct its immediate tactical employment without changing its mission* (TACON).

*Operational reasoning:* task organization lets a commander assemble exactly the mix of capability
the mission needs without restructuring the standing fleet, and the OPCON/TACON split lets forces be
*tactically* shared across a joint/coalition structure without surrendering the owning Service's
authority over the force's overall employment. *Doctrinal assumption:* missions are transient and
forces are modular — any asset can be cross-attached to a task group for the operation's duration and
returned afterward. *Strength:* this gives enormous flexibility to mass capability against a specific
problem without a standing-org rewrite. *Weakness:* temporary task organization creates real command-
relationship ambiguity at the seams — exactly the OPCON/TACON distinction exists *because* "who can
tell this ship what to do" is not self-evident once it's cross-attached. *Decision process:* a
commander decomposes a mission into task-group-sized packages, assigns a clear OPCON/TACON chain for
each, and re-task-organizes as the mission's phase changes. *Uncertainty management:* an unambiguous,
written command-relationship designation for every attached force is the primary tool — ambiguity
about "whose call this is" is treated as an operational risk in itself, not just an administrative
nicety. *Orbital analog:* this maps directly onto White-Cell-as-administrative-owner vs.
Blue/Red-cell-as-tactical-employer in the simulator's own session model, and onto a multi-vignette
campaign where a satellite is cross-attached to a joint task group for one vignette's duration —
`SessionManager`/`CellController`'s ownership-vs-tasking split (CLAUDE.md "Code map") is the engine's
own version of the OPCON/TACON seam, and a future multi-cell campaign design should borrow the
explicit-designation discipline this doctrine insists on rather than leaving "who can redirect this
satellite" implicit.

#### Sources

- *Joint Publication 3-32, Command and Control for Joint Maritime Operations* (Joint Chiefs of Staff)
  — [live](https://irp.fas.org/doddir/dod/jp3_32.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://irp.fas.org/doddir/dod/jp3_32.pdf)
  · accessed 2026-06-28.

### 3.3 Carrier operations, distributed maritime operations, and convoy protection

A **carrier strike group (CSG)** concentrates striking power around a single high-value, mission-
critical platform (the carrier) protected by a layered escort screen — per open-source order-of-battle
summaries, typically one to two Aegis cruisers and two to three Arleigh Burke-class destroyers
providing anti-air and anti-submarine protection around the carrier and its air wing
([Wikipedia/secondary-sourced order-of-battle compilation, cross-checked against multiple open
defense-press summaries](https://en.wikipedia.org/wiki/Carrier_strike_group); *single source
(aggregated open press), used only for the generic composition pattern, not for any classified or
disputed capability claim*). **Distributed Maritime Operations (DMO)** is the opposite operational
logic, formalized by the US Navy from 2019 in direct response to adversary anti-access/area-denial
(A2/AD) capability growth: per the [Congressional Research Service's *Defense Primer: Navy Distributed
Maritime Operations (DMO) Concept*](https://www.congress.gov/crs-product/IF12599), DMO means
"dispersing the fleet while concentrating effects" — distributing, integrating, and maneuvering
platforms and data across a wider area and the electromagnetic spectrum so that no single
engagement can decisively attrit the force, even though no single unit carries CSG-scale concentrated
power. **Convoy protection** is the oldest of the three: the historical pattern of escorting
vulnerable, low-value-individually/high-value-collectively shipping in a concentrated formation
inside an escort screen, refined to doctrinal maturity in the Battle of the Atlantic
(1939–1945), where (per [USNI's *Naval History Magazine* retrospective on the convoy battles of
1943](https://www.usni.org/magazines/naval-history-magazine/2018/april/turning-point-atlantic))
convoys suffering "disastrous losses when escorted by a collection of ships strange to one another,
untrained as a team" were turned around once escort groups trained and operated as cohesive,
practiced units rather than ad hoc assemblages — the Convoy ONS-5 action (1943-04-29 to 1943-05-06)
sank 13 merchant ships but eight U-boats, a favorable exchange ratio that, combined with similar
results through May 1943, led the German U-boat command to withdraw from the North Atlantic convoy
routes on 1943-05-24.

*Operational reasoning:* CSG logic concentrates striking power to guarantee decisive force at the
point of main effort and accepts that the concentrated asset is the single most important thing to
protect; DMO logic accepts each individual unit is more vulnerable in isolation but makes the *force
as a whole* harder to decisively defeat in one engagement; convoy logic protects unarmed/lightly-armed
high-value assets by concentrating *escort* around them rather than dispersing protection thinly.
*Doctrinal assumption (shared, then diverging):* all three assume the adversary can detect and
target individual units — they differ on whether the answer is concentrate-and-protect (CSG, convoy)
or disperse-and-survive (DMO). *Strengths/weaknesses:* CSG concentration maximizes striking power and
simplifies escort coordination but creates a single catastrophic-loss point (the entire DMO debate is
a direct response to this weakness as adversary long-range precision strike matured); DMO survives
single engagements better but multiplies the C2 and logistics burden of coordinating dispersed units
and reduces any single point's concentrated lethality; convoy protection trades merchant-ship transit
speed and routing flexibility for survivability and was *the* historically decisive answer to
submarine threat, but only once escort groups achieved the trained cohesion the 1943 turning point
shows was the actual variable, not just convoy formation itself. *Decision process:* the choice among
these three patterns is a direct function of the threat's detection/targeting reach versus the value
and vulnerability of the asset being protected — a high-value, irreplaceable platform facing a
threat that struggles to mass fires favors concentration (CSG); a force facing a threat that can
reliably find and strike concentrations favors dispersal (DMO); a transport mission facing a
distributed, opportunistic threat (historically, submarines) favors convoy concentration around a
trained escort. *Uncertainty management:* all three patterns are explicit bets about adversary
detection/targeting capability under uncertainty — DMO's rise is itself a doctrinal response to
*increased confidence* that adversary A2/AD detection-and-strike reach had grown enough to make CSG-
style concentration alone insufficiently survivable, i.e., a doctrine shift driven by an explicit
re-estimate of adversary capability, not platform technology alone. *Orbital analog:* CSG maps onto a
single high-value flagship satellite (e.g., a GEO comms node) escorted by smaller defensive/sensing
satellites tasked to protect it; DMO maps directly onto a proliferated/disaggregated LEO constellation
design philosophy where no single satellite's loss is decisive — CLAUDE.md's own
"constellations ≤3 sats, each operated/monitored individually" sizing guideline is a *miniature* DMO-
style choice (deliberately bounding concentration risk per constellation); convoy protection maps onto
escorting a vulnerable but mission-critical asset (an ISR or relay satellite with no defensive
capability of its own) inside a screen of capable defensive/jamming assets tasked specifically to its
protection — a vignette built around this pattern should make the escort's tasking explicitly
conditioned on the high-value asset's access windows, exactly as a historical convoy escort's tasking
was conditioned on the convoy's transit schedule.

#### Sources

- *Congressional Research Service, Defense Primer: Navy Distributed Maritime Operations (DMO) Concept*
  (IF12599) — [live](https://www.congress.gov/crs-product/IF12599)
  · [snapshot](https://web.archive.org/web/2026/https://www.congress.gov/crs-product/IF12599)
  · accessed 2026-06-28.
- *USNI Naval History Magazine, "Turning Point in the Atlantic"* (April 2018, Vol. 32 No. 2) —
  [live](https://www.usni.org/magazines/naval-history-magazine/2018/april/turning-point-atlantic)
  · [snapshot](https://web.archive.org/web/2026/https://www.usni.org/magazines/naval-history-magazine/2018/april/turning-point-atlantic)
  · accessed 2026-06-28.
- *Single source (aggregated open press), CSG generic composition* — [live](https://en.wikipedia.org/wiki/Carrier_strike_group)
  · [snapshot](https://web.archive.org/web/2026/https://en.wikipedia.org/wiki/Carrier_strike_group)
  · accessed 2026-06-28. Used only for the uncontested generic-composition pattern (carrier + cruiser/
  destroyer escort screen), not for any disputed or classified capability claim.

### 3.4 Logistics at sea, sustainment, damage control, and survivability

**Underway replenishment (UNREP)**, carried out by the **Combat Logistics Force (CLF)**, is the
mechanism that converts a fleet's theoretical range into actual on-station endurance: per
[GlobalSecurity.org's CLF summary](https://www.globalsecurity.org/military/systems/ship/logistics.htm)
(cross-checked against the US Naval War College's logistics research guide), CLF ships "maximize
deployed battle group on-station time and endurance" by transferring fuel, ordnance, and stores
ship-to-ship while underway, eliminating the need to break off station and transit to port. This is
the doctrinal foundation of **sustainment** as an operational-art concept distinct from administrative
supply: sustainment is *designed into* the operational plan, not handled as logistics' problem alone,
because on-station endurance is itself a tactical resource the commander allocates and protects (the
CLF's own oilers and ammunition ships are themselves escort-protected high-value assets — the convoy
logic of §3.3 nested one level down). **Damage control** is the shipboard discipline of containing and
recovering from battle damage (fire, flooding, structural failure) while remaining in the fight, and
**survivability** is the broader design-and-doctrine property of a platform's or formation's ability to
take a hit and remain mission-capable rather than being instantly removed from the order of battle —
survivability is explicitly *not* the same property as invulnerability; naval design and doctrine both
assume damage will occur and optimize for graceful degradation, redundancy, and recoverability rather
than damage avoidance alone.

*Operational reasoning:* sustainment reasoning treats on-station time as a finite, consumable
resource exactly like fuel or ammunition, to be planned and protected, not assumed; damage-control/
survivability reasoning treats *being hit* as a near-certainty in sustained high-intensity operations
and plans for continued function after the hit, not just avoidance of being hit. *Doctrinal
assumption:* a fleet operating far from home logistics infrastructure for sustained periods cannot
avoid replenishment dependency, and a unit in sustained combat cannot avoid the statistical certainty
of eventual damage — both assumptions push planning toward resilience rather than perfection.
*Strengths:* this reasoning produces realistic, sustainable campaign plans (sustainment) and platforms/
crews that survive engagements other doctrines would write off as catastrophic losses (damage
control/survivability). *Weaknesses:* CLF dependency creates its own vulnerability — the replenishment
ships are themselves targets whose loss can strand an otherwise-intact combat force, and damage-
control discipline has a real, trainable-but-finite ceiling (crew fatigue, cascading systems failure)
that doctrine cannot engineer away. *Decision process:* a commander plans replenishment cycles as a
scheduling constraint coupled to the operational tempo (exactly as a satellite operator plans around
ground-contact windows), and trains/equips for damage control as a standing readiness investment made
*before* any specific engagement, not improvised during one. *Uncertainty management:* sustainment
uncertainty is managed with reserve margins (fuel/stores buffers sized against transit-time
contingency) rather than point estimates; survivability uncertainty is managed by redundant systems
and trained procedure rather than by trying to predict which specific system will be hit.
*Orbital analog:* sustainment maps onto a satellite's consumables (propellant, battery state-of-
charge) and the operator's scheduling discipline around safe-mode recovery windows and ground-contact-
constrained command opportunities (`spacesim/engine/recovery.py`'s multi-pass recovery model is this
simulator's damage-control analog — designed around the assumption that safe-mode entry *will* happen
and recoverability matters more than prevention alone); survivability maps onto a bus/payload's
graceful-degradation behavior under attack (the `BusState`/`PayloadState` SOH model's safe-mode gating
is exactly the "stay in the fight, degraded, rather than total loss" survivability principle). The one
place this analogy genuinely strains is damage control's *physical crew action* (firefighting,
shoring, pumping) — an uncrewed satellite has no analog to a human damage-control party, so the
orbital instantiation is necessarily software/procedure-only (autonomous safe-mode logic and ground-
commanded recovery sequences substituting for what a ship's crew does by hand); this is a genuine
disanalogy, not a gap in this topic's coverage.

#### Sources

- *GlobalSecurity.org, "Combat Logistics Force"* — [live](https://www.globalsecurity.org/military/systems/ship/logistics.htm)
  · [snapshot](https://web.archive.org/web/2026/https://www.globalsecurity.org/military/systems/ship/logistics.htm)
  · accessed 2026-06-28.

### 3.5 Maritime ISR and maritime domain awareness (MDA)

**Maritime domain awareness (MDA)** is formally defined, per the US [*National Plan to Achieve
Maritime Domain Awareness*](https://www.dhs.gov/xlibrary/assets/HSPD_MDAPlan.pdf) (issued under
National Security Presidential Directive-41/Homeland Security Presidential Directive-13,
2005-10), as "the effective understanding of... global maritime domain elements that could impact
the security, safety, economy, or environment" of the nation — explicitly framed as an *enabling*
function, not a decision function: the Plan states MDA "does not direct actions, but enables them to
be done more quickly and with precision," achieved through "decision superiority... by ensuring
global maritime information dominance through the collection, integration and dissemination of
information." **Maritime ISR** is the collection layer that feeds MDA — surface, subsurface, air, and
space-based sensing fused into a common operational picture.

*Operational reasoning:* MDA reasoning explicitly separates *building the picture* from *acting on
it* — a commander invests in awareness as a precondition for good decisions, not as the decision
process itself, and treats a gap in domain awareness as a gap in decision quality even before any
specific threat is identified. *Doctrinal assumption:* the maritime domain is too vast and the
adversary/neutral/friendly mix too ambiguous for any single sensor or organization to achieve
sufficient awareness alone — MDA doctrine is built around multi-source, multi-agency fusion by
necessity, not preference. *Strength:* the awareness/action separation keeps the picture honest —
fusion isn't biased by a single command's immediate tactical agenda. *Weakness:* fusion across many
sources/agencies is a genuine, persistent integration problem (sensor disagreement, latency,
classification-level mismatches between contributing sources) that doctrine names as a standing
challenge rather than a solved one. *Decision process:* a commander tasks collection against
*priority gaps* in the picture (not uniformly), continuously re-prioritizes as the picture and the
mission evolve, and treats the resulting MDA product as an input to, not a substitute for, the actual
operational decision. *Uncertainty management:* MDA's whole premise is managing uncertainty about a
domain too large to fully observe — coverage is necessarily probabilistic and gapped, and the
doctrine's emphasis on "effective understanding" (not "complete understanding") is a deliberate
acknowledgment that the goal is decision-adequate confidence, not omniscience. *Orbital analog:* this
maps essentially one-to-one onto this simulator's space domain awareness and custody model
([R102](R102-space-domain-awareness.md), [R105](R105-custody-theory.md)) — the SSN's per-cell,
priority-SLA-gated collection resolution (`spacesim/engine/ssn.py`) is a direct mechanical analog of
MDA's tasked-against-priority-gaps collection logic, and the fog-of-war architecture's explicit
separation of "what is known" (CellView/TrackCatalog) from "what is decided" (order issuance) mirrors
MDA's awareness/action separation precisely.

#### Sources

- *National Plan to Achieve Maritime Domain Awareness* (issued under NSPD-41/HSPD-13, October 2005)
  — [live](https://www.dhs.gov/xlibrary/assets/HSPD_MDAPlan.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.dhs.gov/xlibrary/assets/HSPD_MDAPlan.pdf)
  · accessed 2026-06-28.

### 3.6 ASW, AAW, surface warfare, and strike warfare

US Navy doctrine organizes shipboard and force-level combat employment into named **warfare areas**,
each with its own commander designation, sensor/weapon suite logic, and tactical doctrine: **anti-
submarine warfare (ASW)** (detecting, tracking, and engaging an undersea threat under conditions of
severe sensor ambiguity), **anti-air warfare (AAW)** (defending the force against airborne and missile
threats, typically the most time-compressed warfare area because of missile closing speeds), **surface
warfare (SUW)** (engaging surface combatants and small craft, including the asymmetric small-boat
threat), and **strike warfare** (offensive power projection ashore, historically carrier air and now
also long-range land-attack missiles). ASW's doctrinal maturity traces directly to the Battle of the
Atlantic's 1943 turning point (§3.3): per the same [USNI retrospective](https://www.usni.org/magazines/naval-history-magazine/2018/april/turning-point-atlantic),
the introduction of high-frequency direction-finding (HF/DF) for U-boat-transmission triangulation
alongside trained, cohesive escort groups is credited as the combination that broke the U-boat threat
— a clear historical lesson that *sensor capability and trained organizational process together*, not
either alone, produced the doctrinal breakthrough.

*Operational reasoning:* each warfare area reasons from its threat's distinctive detectability and
engagement-timeline profile — ASW reasons under persistent target ambiguity (a submarine is rarely
unambiguously localized) and plans for sustained, patient search; AAW reasons under severe time
compression (a missile's flight time leaves seconds for a defensive decision) and plans for
automated, doctrine-pre-authorized engagement; SUW and strike warfare reason more like conventional
target-engagement problems with comparatively better target discrimination. *Doctrinal assumption:*
the warfare-area decomposition assumes a force commander can delegate each area to a specialized
warfare commander (the doctrinal AAWC/ASWC/SUWC roles) operating semi-autonomously within the overall
commander's intent, because no single human can simultaneously manage all four threat pictures at
their differing tempos. *Strength:* tempo-matched delegation lets the fastest-developing threat (AAW)
get a decision cycle fast enough to matter, while slower threats (ASW) get the patience their
ambiguity requires. *Weakness:* warfare-area stovepiping can create cross-domain blind spots at the
seams (a threat that doesn't cleanly fit one warfare area's sensor/doctrine boundary) and demands
disciplined cross-area coordination that doctrine names as a standing training requirement, not a
solved problem. *Decision process:* the overall commander sets engagement authorities and
rules of engagement per warfare area in advance, calibrated to each area's available decision time,
rather than adjudicating every individual engagement personally. *Uncertainty management:* ASW
manages uncertainty by accepting prolonged ambiguous contact and refining classification confidence
over time before committing to engagement; AAW manages uncertainty by pre-delegating engagement
authority under strict, pre-briefed criteria precisely *because* there is no time to resolve
ambiguity live. *Orbital analog:* ASW's patient-classification-under-ambiguity logic maps directly
onto this simulator's custody-confidence-decay and weapons-quality gate ([R105](R105-custody-theory.md))
— a maneuvering or low-signature object should be reasoned about the way an ASW operator reasons
about a submarine contact, accepting low confidence and refining rather than forcing a premature
identification; AAW's pre-delegated, time-compressed engagement-authority logic maps onto a defensive
posture against an inbound kinetic threat where the access-window-bounded decision time mirrors a
missile engagement's compressed timeline, suggesting any future close-approach defensive mechanic
should similarly pre-authorize engagement criteria rather than assume live human adjudication is
always available in time; SUW and strike warfare map more loosely onto direct-engagement and ground/
orbital-target strike actions respectively, with comparatively less novel doctrinal content for this
simulator's purposes than the ASW/AAW pairing.

#### Sources

- *USNI Naval History Magazine, "Turning Point in the Atlantic"* (April 2018) — [live](https://www.usni.org/magazines/naval-history-magazine/2018/april/turning-point-atlantic)
  · [snapshot](https://web.archive.org/web/2026/https://www.usni.org/magazines/naval-history-magazine/2018/april/turning-point-atlantic)
  · accessed 2026-06-28.

### 3.7 Maritime command and control

Maritime C2 is governed, as introduced in §3.2, by [JP 3-32](https://irp.fas.org/doddir/dod/jp3_32.pdf),
which structures authority through functional and Service component commanders exercising OPCON/TACON
over forces made available for a given operation, with maritime domain awareness (§3.5) as the
informational substrate the C2 structure consumes. The doctrinally distinctive feature of maritime C2,
beyond the OPCON/TACON mechanics already covered, is **mission command under communication
denial/degradation**: because a dispersed naval force routinely operates beyond reliable real-time
communication with higher headquarters (and increasingly expects communications-denied conditions
under adversary EW in a high-end fight), maritime C2 doctrine has historically emphasized commander's
intent and pre-briefed authorities *more* heavily than land-component C2, which can more often assume
continuous connectivity.

*Operational reasoning:* a maritime commander plans for subordinate task-group commanders to act
correctly on stated intent during communication gaps, rather than planning for continuous
direction — the C2 architecture is designed for graceful degradation to mission-command-only, not
brittle dependence on a live link. *Doctrinal assumption:* communications with a dispersed,
underway force will be intermittent by the nature of the medium (and adversarial under contested
conditions), so authority must be pre-delegated far enough down to survive the gap. *Strength:* this
produces a C2 structure that degrades gracefully rather than catastrophically when links fail.
*Weakness:* pre-delegated authority under degraded communications creates real risk of subordinate
commanders acting on stale intent or making decisions the higher commander would have countermanded
with current information — a tension doctrine manages but does not eliminate. *Decision process:*
intent and engagement authorities are specified in detail *before* the communications gap occurs, not
improvised during it. *Uncertainty management:* the uncertainty being managed is about the higher
commander's current intent and the broader picture, not (as in MDA) about the adversary — the
doctrinal answer is to over-specify intent and authority up front so a subordinate's decision-under-
uncertainty is bounded by clear, pre-stated limits. *Orbital analog:* this maps with unusual precision
onto this simulator's plan-first invariant (CLAUDE.md's load-bearing invariant #4) and the access-
window-gated command model — a satellite is, by the medium's nature, communications-denied except
during contact windows, so an operator must plan commands in advance for execution at the next valid
window exactly as a maritime task-group commander must act on pre-briefed intent during a
communications gap; this is arguably the single closest one-to-one structural match in this entire
topic, because both domains derive the *same* mission-command-under-intermittent-connectivity
doctrine from the *same* underlying cause (a medium that does not support continuous communication).

#### Sources

- *Joint Publication 3-32, Command and Control for Joint Maritime Operations* — [live](https://irp.fas.org/doddir/dod/jp3_32.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://irp.fas.org/doddir/dod/jp3_32.pdf)
  · accessed 2026-06-28.

### 3.8 Chokepoints, patrol patterns, and presence operations

A **chokepoint** (a strait, canal, or other geographically constrained transit corridor) concentrates
maritime traffic and therefore concentrates both opportunity (control it and you control a
disproportionate share of regional maritime flow) and risk (lose it and an adversary controls the same
leverage); a fleet's **patrol pattern** is the deliberate, repeated search/coverage geometry used to
maintain awareness or deterrent presence over an area too large to observe continuously; **presence
operations** are the sustained forward stationing of forces for deterrence, reassurance, and rapid
crisis response rather than for any single engagement. The doctrinal logic of forward presence is
laid out across decades of analysis — [CNA's "Peacetime Influence Through Forward Naval Presence"](https://www.cna.org/analyses/1993/peacetime-influence)
(1993) and the Navy's own successive strategy documents (*A Cooperative Strategy for 21st Century
Seapower*, 2007; *Forward, Engaged, Ready*, 2015, per the [Naval History and Heritage Command's
survey of forward-presence doctrine](https://www.history.navy.mil/content/dam/nhhc/research/library/online-reading-room/history-surveys/needs-opportunities-modern-history-us-navy/Needs%20Opps%20Mahnken%20Final.pdf))
— consistently frame presence as producing deterrent and influence effects *independent of and prior
to* any actual engagement, simply by being credibly, persistently there.

*Operational reasoning:* chokepoint reasoning treats geography itself as a force multiplier — a
modest force controlling a chokepoint achieves leverage disproportionate to its size, because the
chokepoint's narrowness does the concentrating work the force doesn't have to do itself; patrol-
pattern reasoning trades continuous coverage (impossible at scale) for a statistically adequate
sampling of a large area over time; presence-operations reasoning treats *being seen to be capable
and ready* as itself producing a deterrent/reassurance effect, separate from and prior to any
specific engagement. *Doctrinal assumption (shared):* all three assume an adversary or audience is
rationally responsive to demonstrated capability and position, not just to outcomes after the fact —
this is the same rational-actor assumption [R303](R303-deterrence-theory.md) names directly.
*Strengths:* chokepoint control is efficient leverage; patrol patterns make large-area awareness
tractable; presence achieves deterrent/influence effects at a fraction of the cost of actual
engagement. *Weaknesses:* chokepoint dependence is a double-edged asymmetry (it is exactly as
valuable to an adversary attempting denial as to the side attempting control); patrol patterns are
inherently a sampling compromise with real, quantifiable gaps between passes; presence-operations
deterrent value is hard to measure directly and depends on adversary perception, which a commander
cannot fully observe or control. *Decision process:* a commander allocates disproportionate
collection/protection effort to chokepoints precisely because of their leverage; designs patrol
patterns against an explicit revisit-time requirement balanced against available platforms; and
schedules forward-presence rotations to maintain continuous, credible coverage of a theater rather
than episodic visits. *Uncertainty management:* chokepoint risk is managed by treating the chokepoint
itself as the priority intelligence/protection requirement; patrol-pattern uncertainty (what happened
between passes) is an accepted, quantified gap rather than a denied one; presence-operations
uncertainty about whether deterrence is actually working is managed by treating continuous, credible
presence as the best available proxy for deterrent effect, in the absence of a direct measurement.
*Orbital analog:* chokepoints map directly onto specific orbital regimes/access corridors and onto
the access-window concept itself — a ground-station's command-uplink window or a specific orbital
plane's repeat-ground-track corridor is a chokepoint in exactly Corbett's sense, a place where control
of a narrow resource yields outsized operational leverage; patrol patterns map onto sensor-tasking
sweep patterns for space domain awareness across a large orbital volume with finite sensor-revisit
capacity (directly the SSN's collection-scheduling logic, [R118](R118-space-surveillance-networks.md));
presence operations map onto the doctrinal logic behind maintaining persistent custody/coverage of a
contested orbital regime as a deterrent in itself, independent of any specific engagement — a vignette
built around presence-as-deterrence should reward Blue for sustained, credible coverage of a regime,
not only for successful engagements within it.

#### Sources

- *CNA, "Peacetime Influence Through Forward Naval Presence"* (1993) — [live](https://www.cna.org/analyses/1993/peacetime-influence)
  · [snapshot](https://web.archive.org/web/2026/https://www.cna.org/analyses/1993/peacetime-influence)
  · accessed 2026-06-28.
- *Naval History and Heritage Command, "Forward Presence in the Modern Navy: From the Cold War to a
  Future Tailored Force"* — [live](https://www.history.navy.mil/content/dam/nhhc/research/library/online-reading-room/history-surveys/needs-opportunities-modern-history-us-navy/Needs%20Opps%20Mahnken%20Final.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.history.navy.mil/content/dam/nhhc/research/library/online-reading-room/history-surveys/needs-opportunities-modern-history-us-navy/Needs%20Opps%20Mahnken%20Final.pdf)
  · accessed 2026-06-28.

### 3.9 Deterrence and escalation management (naval instantiation)

This cluster does not re-derive deterrence or escalation theory — [R303](R303-deterrence-theory.md)
and [R304](R304-escalation-dynamics.md) already supply the general theory this simulator's ROE and
kinetic consequence-confirm gate are built on. What naval practice adds is the **graduated-presence
escalation ladder** as a concrete, historically exercised instantiation of [R304](R304-escalation-dynamics.md)'s
abstract rungs: a naval commander has a standard, doctrinally recognized sequence of moves — routine
presence patrol, increased presence/show-of-force, shadowing/intercept, warning shots or non-lethal
deterrent measures, and finally weapons engagement — each a distinct, deliberate rung with its own
signaling value, long predating and directly informing the general escalation-ladder literature
[R304](R304-escalation-dynamics.md) already cites (Kahn 1965; Morgan et al., RAND 2008).

*Operational reasoning:* a naval commander selects the *lowest* rung adequate to the situation and
holds subsequent rungs in reserve, because each step up the ladder is harder to walk back and carries
escalation risk independent of its tactical effect. *Doctrinal assumption:* the adversary is a
rational actor capable of reading and responding to graduated signals — the entire ladder concept
fails against an adversary who cannot or will not distinguish a warning shot from an attack.
*Strength:* graduated response preserves off-ramps at every rung and gives both sides repeated
opportunities to de-escalate without loss of face. *Weakness:* graduated signals can be
misread — exactly [R304](R304-escalation-dynamics.md)'s inadvertent-escalation failure mode — and a
commander under real time pressure may not have the luxury of waiting to see whether a lower rung
worked before the tactical situation forces a higher one. *Decision process:* rules of engagement
pre-authorize specific responses at specific rungs, so the commander's live decision is "which rung
does this situation warrant" against a pre-briefed menu, not an open-ended judgment call invented in
the moment. *Uncertainty management:* uncertainty about adversary intent is managed by choosing
actions whose *signal* is unambiguous even if the adversary's intent is not — a warning shot's
doctrinal meaning is standardized precisely so it cannot be mistaken for an attack, reducing the
inadvertent-escalation risk [R304](R304-escalation-dynamics.md) names. *Orbital analog:* this is the
direct naval-historical precedent for this simulator's own five-D graduated effect taxonomy and the
kinetic consequence-confirm gate (CLAUDE.md's load-bearing invariants) — reversible EW/cyber/RPO
effects are the orbital equivalent of shadowing/show-of-force, and the consequence-confirm dialog on
kinetic action is the orbital equivalent of the doctrinal seriousness with which a warning-shot-to-
engagement transition is treated in naval ROE; a vignette author designing a new inject's escalation
properties should consult this naval ladder as a concrete worked example of how real commanders
sequence graduated responses, not just the abstract theory in [R304](R304-escalation-dynamics.md).

#### Sources

This cluster cites no new sources beyond those already inline-cited in [R303](R303-deterrence-theory.md)
and [R304](R304-escalation-dynamics.md); see those topics' own `### Sources` subsections for Kahn
(1965) and Morgan et al. (RAND, 2008).

## 4. Operational Context

Across all nine clusters, the same higher-order pattern recurs: naval operational art exists because
the sea is vast, communication is intermittent, detection is probabilistic, and control is local and
temporary rather than global and permanent — and every doctrinal concept above (task organization,
DMO dispersal, MDA's awareness/action split, mission command under communications denial, the
escalation ladder) is a specific, historically tested answer to operating *competently under those
exact constraints*, not a generic best-practice borrowed from a domain that doesn't share them. This
is precisely why the analogy to orbital operations is unusually strong rather than merely
illustrative: this simulator's load-bearing invariants (plan-first command, sub-stepped access
windows, fog-of-war at the boundary, custody as a decaying confidence rather than a binary) are
independently-derived answers to the *same* underlying constraints (a vast, sparsely observable medium
with intermittent connectivity and graduated, reversible-by-default effects) that 20th- and 21st-
century naval doctrine derived its answers to over a much longer institutional history. A White Cell
facilitator or trainee already fluent in "carrier strike group," "convoy," or "ASW contact" from
general military education has a faster on-ramp to this simulator's orbital concepts than one starting
from zero, provided the facilitator is explicit about *which* maritime concept maps to *which* orbital
mechanic — which is exactly what each cluster's closing "Orbital analog" paragraph in §3 is for.

## 5. Implementation Guidance

- **Use this topic's per-cluster orbital analogs as facilitator briefing language, not as new engine
  mechanics** — the analogy's value is pedagogical (faster trainee comprehension of access windows,
  custody decay, and graduated effects via a familiar vocabulary), not a license to add maritime-
  specific game mechanics that don't already exist in the build spec; a vignette's `intro_brief` or
  `coaching` notes (per `spacesim/content/vignette.py`) are the natural place to deploy a maritime
  analogy ("this regime functions like a strait — control of it for the access window is
  disproportionately valuable"), not a new YAML schema field.
- **A new constellation-design vignette choosing between concentrated (CSG-like) and disaggregated
  (DMO-like) high-value-asset employment should state which pattern it is teaching explicitly** — per
  §3.3's CSG/DMO/convoy comparison, these are doctrinally distinct bets about adversary detection-and-
  strike reach, and a vignette that mixes the patterns without naming which one is being exercised
  teaches a confused lesson.
- **A custody/contact-classification mechanic for a maneuvering or low-signature threat should be
  designed with ASW's patient-classification-under-ambiguity model in mind** (§3.6) — this reinforces,
  rather than changes, [R105](R105-custody-theory.md)'s existing custody-decay design, but gives a
  facilitator a concrete naval precedent ("treat this like a submarine contact, not a radar track")
  to explain *why* the engine resists letting a trainee force premature high-confidence
  classification.
- **Any future close-approach or inbound-threat defensive mechanic with a hard real-time deadline
  should borrow AAW's pre-delegated-engagement-authority pattern** (§3.6) rather than assume a White
  Cell facilitator or cell operator can always adjudicate live — if the access-window-bounded decision
  time is short enough to matter, the vignette's ROE should pre-authorize the response criteria in
  advance, exactly as AAW doctrine pre-delegates engagement authority because missile-defense
  timelines leave no time for live adjudication.
- **A multi-vignette or campaign-style design that cross-attaches an asset across cells/sessions
  should make the OPCON/TACON-style ownership-vs-tasking distinction explicit** (§3.2/§3.7) — state,
  in the vignette's documentation, who can redirect the asset's overall employment versus who can
  task it tactically for the current vignette, mirroring JP 3-32's discipline about never leaving a
  command relationship implicit.
- **A presence/deterrence-themed vignette should reward sustained credible coverage of a contested
  regime, not only successful engagements within it** (§3.8) — per the forward-presence literature's
  finding that deterrent value accrues from being persistently and credibly present, an objective
  schema that only scores kinetic/EW success misses the doctrinal point a presence vignette is meant
  to teach.

## 6. Feature Mapping

Vignette authoring (`docs/scenarios/`) and White Cell facilitator briefing material are the direct
consumers, particularly any new constellation-design, custody/classification, close-approach-
defense, multi-vignette-campaign, or presence/deterrence-themed vignette. Also informs `redai.py`
posture documentation where a Red doctrine preset's aggressiveness is better explained via a naval
escalation-ladder rung (§3.9) than a bare parameter value.

## 7. Related Topics

[R301](R301-campaign-design.md) (Campaign Design), [R302](R302-operational-art.md) (Operational Art),
[R303](R303-deterrence-theory.md) (Deterrence Theory), [R304](R304-escalation-dynamics.md) (Escalation
Dynamics, the general theory this topic's §3.9 instantiates), [R312](R312-space-strategy.md) (Space
Strategy), [R105](R105-custody-theory.md) (Custody Theory, the direct analog of §3.6's ASW
classification logic), [R108](R108-constellation-operations.md) (Constellation Operations, the direct
analog of §3.3's CSG/DMO comparison), [R118](R118-space-surveillance-networks.md) (Space Surveillance
Networks, the direct analog of §3.8's patrol-pattern logic), [R120](R120-access-window-and-geometry-planning.md)
(Access Window and Geometry Planning, the direct analog of §3.1/§3.7's window-gated control and
mission-command-under-intermittent-connectivity logic).
