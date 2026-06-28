# R315 — Air Operator Perspective

> **Document ID:** R315
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R301](R301-campaign-design.md), [R302](R302-operational-art.md), [R305](R305-mission-analysis.md), [R312](R312-space-strategy.md)
> **Referenced By:** [R317](R317-space-operator-perspective.md)
> **Produces:** the air-domain analogy vocabulary that future space-C2 / dynamic-retasking / Red-IADS-style
> feature work and vignette authoring can borrow from a domain with seventy years of doctrinal practice
> **Feature Mapping:** future SSA-tasking-contention features, dynamic re-tasking UI work, Red AI
> integrated-defense postures, vignette authoring (`docs/scenarios/`), `engine/ssn.py` (tasking-category
> precedent), `engine/orders.py` (tasking/queue precedent)
> **Related Topics:** [R301](R301-campaign-design.md) (Campaign Design), [R302](R302-operational-art.md)
> (Operational Art), [R305](R305-mission-analysis.md) (Mission Analysis), [R306](R306-operational-assessment.md)
> (Operational Assessment), [R311](R311-course-of-action-analysis.md) (COA Analysis),
> [R312](R312-space-strategy.md) (Space Strategy), [R313](R313-maritime-operator-perspective.md)
> (Maritime Operator Perspective) and [R314](R314-land-operator-perspective.md) (Land Operator
> Perspective) — the tier's other two domain-analogy chapters, covering sea control/denial/naval C2
> and land-component mission command respectively, rather than air),
> [`research/01-doctrine-western.md`](../01-doctrine-western.md)
> **Last Reviewed:** 2026-06-28
> **Primary Sources Consulted:** 9

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Space doctrine is young; air doctrine is not. The air domain has run a continuous, documented,
institutionalized cycle of campaign planning, contested-domain control, dynamic tasking under
uncertainty, and adversary-IADS attrition for over seventy years, and has written that experience
down in joint and Service doctrine that is unusually explicit about *how operators think*, not just
*what platforms do*. This topic exists to give an implementer or vignette author a second, mature
domain's mental models to borrow from when this simulator's own concepts (access windows, custody,
tasking contention, dynamic targeting of space objects, IADS-style ground threat to satellites) are
under-specified by space doctrine alone — exactly the gap-filling role MSTR-007 §7 describes. It
explicitly does **not** catalogue aircraft, weapons, or platform specifications; every section is
about the operational problem an air operator is solving, not the hardware solving it.

## 2. Scope

Covers, for each of twenty air-operations concepts, the air operator's mental model, planning
assumptions, operational constraints, command philosophy, measures of effectiveness (MOE),
decision-making approach under uncertainty, and an explicit transferable lesson for satellite
constellation / orbital operations. Does **not** cover: aircraft performance figures, weapon system
specifications, classified TTPs, or platform-level engineering (out of bounds per
[`research/10-sources-and-methodology.md`](../10-sources-and-methodology.md) §8 and irrelevant to
the operational-thinking focus this topic exists to capture). Does not re-derive general
operational-art vocabulary already covered by [R301](R301-campaign-design.md)/[R302](R302-operational-art.md)/[R305](R305-mission-analysis.md) — this
topic specializes that vocabulary to the air domain and draws the orbital analogy out explicitly,
which those topics do not.

## 3. Concepts

### 3.1 Air Superiority

**Mental model.** Air superiority is not "winning dogfights" — it is a *degree of control* along a
spectrum from air parity through air superiority to air supremacy, each enabling progressively freer
friendly air operations and progressively more constrained adversary ones
([JP 3-30, *Joint Air Operations*](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf),
2019-07-25). It is treated as an *enabling precondition* for every other joint function — land, sea,
and now space/cyber operations all assume some degree of air control exists before they commit.

**Planning assumptions.** Planners assume air superiority is contested, perishable, and local —
gained in one sector/altitude band does not transfer automatically elsewhere or persist
unmaintained; it must be actively re-won and held, the same logic [R301](R301-campaign-design.md) §3 applies to
phased campaign objectives generally.

**Operational constraints.** Limited by available combat air patrol (CAP) capacity, basing/tanker
range, and the adversary's own counterair posture — a finite resource that must be allocated against
competing demands (escort, CAP, strike support) rather than assumed unlimited.

**Command philosophy.** Centralized control of the air superiority effort under a single airspace
authority (historically the Joint Force Air Component Commander, JFACC) is doctrine's answer to the
problem of deconflicting and prioritizing a scarce, theater-wide resource — see §3.8 below.

**Measures of effectiveness.** Sortie effectiveness rate against air-to-air threats, friendly
attrition rate, freedom-of-maneuver achieved for follow-on missions (i.e., MOEs are about *enabled
freedom of action*, not kill counts alone).

**Decision-making under uncertainty.** Air superiority status is reassessed continuously from an
evolving, incomplete air picture (radar/IFF tracks, EW indicators); commanders act on a *degree of
confidence* in control, not a binary "won/lost" state.

**Transferable lesson.** "Space superiority" in [R312](R312-space-strategy.md) §3 is the same
spectrum concept — a degree-of-control continuum, locally and temporally bounded by access windows,
not a single global "we control space" switch. A vignette or White Cell rule that treats space
control as binary misses the doctrinal precedent this section names explicitly.

### Sources

- *JP 3-30, Joint Air Operations* (Joint Chiefs of Staff, 2019-07-25) —
  [live](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · accessed 2026-06-28.

### 3.2 Offensive and Defensive Counter Air (OCA/DCA)

**Mental model.** Counterair doctrine splits the air-superiority problem into two complementary
halves: OCA destroys, disrupts, or degrades adversary air and missile threats *before* they are
employed (forward of the friendly defended area); DCA detects, identifies, intercepts, and destroys
them *after* launch, inside friendly airspace
([AFDP 3-01, *Counterair Operations*](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf),
2023-06-15; [JP 3-01, *Countering Air and Missile Threats*](https://irp.fas.org/doddir/dod/jp3_01.pdf)).
The two are doctrinally inseparable — DCA buys time and reduces leakage while OCA reduces the
adversary's capacity to generate the next wave.

**Planning assumptions.** OCA is assumed to be the preferred economy-of-force approach (kill the
archer, not just the arrows) but is constrained by access, ROE, and target location uncertainty; DCA
is assumed always-on because zero-leakage interception is unachievable, so defended-asset prioritization
is mandatory.

**Operational constraints.** OCA needs strike access and accurate targeting against often-mobile
or hardened threats; DCA is constrained by sensor coverage, weapons-on-hand, and engagement-zone
geometry (an interceptor can only act inside its kinematic envelope).

**Command philosophy.** Integration of OCA and DCA under one counterair commander prevents the
common failure mode of an offensive plan and a defensive plan each assuming the other handles a gap
([AFDP 3-01](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)).

**Measures of effectiveness.** Leakage rate (threats that penetrate DCA), adversary sortie-generation
degradation (OCA's effect on the threat's capacity to regenerate raids), defended-asset survival rate.

**Decision-making under uncertainty.** Resource allocation between OCA and DCA is a continuous
trade-off made under imperfect knowledge of the adversary's remaining capacity — over-investing in
DCA cedes initiative; over-investing in OCA risks leakage if the adversary's order of battle was
underestimated.

**Transferable lesson.** A satellite constellation's defense-in-depth has the same two-sided
structure: "offensive" preemptive action against an attacking ground station/jammer/cyber actor
(asset-protective fires, when ROE permits) versus "defensive" on-orbit hardening, maneuver, and
mitigation after an attack begins. A White Cell or Red AI posture (`spacesim/session/redai.py`) that
models only the defensive half is doctrinally incomplete by this section's standard — see
[R304](R304-escalation-dynamics.md) for the escalation cost of choosing the offensive half.

### Sources

- *AFDP 3-01, Counterair Operations* (US Air Force, 2023-06-15) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · accessed 2026-06-28.
- *JP 3-01, Countering Air and Missile Threats* (Joint Chiefs of Staff) —
  [live](https://irp.fas.org/doddir/dod/jp3_01.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://irp.fas.org/doddir/dod/jp3_01.pdf)
  · accessed 2026-06-28.

### 3.3 ISR (Intelligence, Surveillance, Reconnaissance)

**Mental model.** ISR is framed as a *cycle* (the PCPAD chain: plan/direct, collect, process/exploit,
analyze/produce, disseminate), not a single sensor event — value is created only when a collection
reaches a decision-maker in time to act on it, per the joint intelligence doctrine this simulator's
own decision-science primer already grounds at [R201](../encyclopedia/R200-index.md)-tier (see also
[`research/05-mission-types-and-counters.md`](../05-mission-types-and-counters.md) for the
simulator's own ISR mission-type taxonomy).

**Planning assumptions.** Collection requirements are prioritized and deconflicted against finite
sensor/platform capacity (a Collection Requirements Management process); the same sensor cannot
satisfy every requester at once, so a tasking authority arbitrates.

**Operational constraints.** Sensor dwell, revisit rate, weather/atmospheric effects, and
processing/exploitation throughput (the PED — processing, exploitation, dissemination — bottleneck,
historically the limiting factor even when collection capacity grows) bound what ISR can actually
deliver in time to matter.

**Command philosophy.** ISR is centrally tasked against a prioritized requirements list (akin to the
ATO's place in air tasking, §3.4) so that high-value, perishable requirements are not starved by
routine ones.

**Measures of effectiveness.** Time from requirement to actionable product (latency), percentage of
priority intelligence requirements answered, confidence/confirmation rate of reported tracks.

**Decision-making under uncertainty.** Commanders act on a confidence-weighted picture, never a
complete one; ISR doctrine explicitly distinguishes *collection* from *confirmed intelligence* — an
unprocessed or unanalyzed sensor hit is not yet actionable.

**Transferable lesson.** This simulator's `Track`/custody-confidence model
([`research/04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md), `engine/custody.py`)
is the orbital-domain expression of exactly this PCPAD discipline: a detection is not custody, and
custody is not a weapons-quality track, mirroring the ISR cycle's collection→exploitation→actionable-
product chain. The PED bottleneck lesson applies directly to SSN tasking contention
(`engine/ssn.py`) — a White Cell scenario that adds more collectors without modeling a
processing/triage bottleneck understates a real-world constraint this section documents.

### Sources

- *JP 3-30, Joint Air Operations* §III (ISR integration into the air tasking cycle) —
  [live](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · accessed 2026-06-28.

### 3.4 Air Tasking Orders (ATO)

**Mental model.** The ATO is the single authoritative document translating the Joint Force Air
Component Commander's (JFACC) air apportionment decision into specific tasked missions (who, what,
when, where, with what ordnance/sensors), produced on a recurring (typically 72-hour-cycle) battle
rhythm — the air domain's central planning artifact
([JP 3-30](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)).

**Planning assumptions.** The ATO assumes a knowable, schedulable future window (the next 24-72
hours) in which most missions can be pre-planned against known targets/requirements, with a known
fraction reserved unplanned for dynamic events (§3.5).

**Operational constraints.** ATO production is constrained by the planning cycle's own length —
the ATO cycle (typically Air Tasking Cycle phases: guidance/apportionment, target development,
weaponeering/allocation, ATO production, execution, assessment) takes real wall-clock time, so the
plan that executes is always somewhat stale relative to current conditions.

**Command philosophy.** Centralized planning (one ATO, one JFACC) with decentralized execution
(individual aircrews exercise tactical judgment within their tasked mission) — the doctrinal
resolution of the control-vs-initiative tension, restated explicitly in
[AFDP 3-0, *Operations*](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
(2025-01-22) as Centralized Command–Distributed Control–Decentralized Execution.

**Measures of effectiveness.** ATO fragmentation/change rate (how often pre-planned missions must
be altered — a high rate signals either poor planning or a highly dynamic environment), sortie
execution rate against planned sorties, planning-cycle latency vs. target dwell time.

**Decision-making under uncertainty.** The ATO is deliberately not treated as immutable — a
fragmentary order (FRAGORD) amends it intra-cycle when conditions change faster than the next
full ATO can be produced; the doctrine accepts the plan will be wrong in detail and builds a
correction mechanism into the battle rhythm rather than re-planning from scratch.

**Transferable lesson.** A multi-asset orbital tasking cycle (sensor tasking, maneuver planning,
uplink scheduling) faces the identical staleness problem: a plan built against predicted access
windows is stale by the time it executes if conditions change. The ATO's FRAGORD pattern — a
recurring base plan plus a lightweight amendment mechanism, rather than full re-planning — is the
precedent this simulator's plan-first invariant (CLAUDE.md §"Load-bearing invariants" item 4) should
be checked against when a future feature adds multi-asset coordinated tasking.

### Sources

- *JP 3-30, Joint Air Operations* (2019-07-25) —
  [live](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · accessed 2026-06-28.
- *AFDP 3-0, Operations* (US Air Force, 2025-01-22) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · accessed 2026-06-28.

### 3.5 Dynamic Targeting

**Mental model.** Dynamic targeting prosecutes targets not on the pre-planned ATO target list —
either targets of opportunity or time-sensitive targets (§3.7) — using a deliberately compressed
version of the full targeting cycle
([JP 3-60, *Joint Targeting*](https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)). It
exists because doctrine accepts that no pre-plan, however good, anticipates every valid target that
will appear during execution.

**Planning assumptions.** A fraction of available sorties/weapons is deliberately held in reserve
(uncommitted or flexibly re-taskable) specifically to service dynamic targets — capacity is planned
*for* unplanned demand, not treated as a planning failure when it occurs.

**Operational constraints.** Compressed timelines mean less time for collateral-damage estimation,
deconfliction, and positive identification — dynamic targeting trades planning rigor for speed, and
doctrine is explicit that this trade is the source of dynamic targeting's higher risk profile.

**Command philosophy.** Pre-delegated engagement authority (within stated ROE) at the lowest level
consistent with risk tolerance is what makes dynamic targeting fast enough to matter — if every
dynamic target required JFC-level approval, the speed advantage is lost; this is the same
decentralized-execution logic as §3.4.

**Measures of effectiveness.** Time from target detection to engagement decision, fraction of valid
dynamic targets successfully prosecuted before the window closed, false-positive/misidentification
rate.

**Decision-making under uncertainty.** Dynamic targeting decisions are made with deliberately less
information than deliberate targeting — the doctrinal acceptance is that *waiting for complete
information forfeits the target*, so the decision calculus is explicitly speed-vs-confidence, not
speed-vs-correctness alone.

**Transferable lesson.** This is the doctrinal ancestor of this simulator's `dry_run()` "why can't
I?" pre-disabled-button pattern (`engine/orders.py`) and its sensor-tasking auto-select/contention
logic: dynamic re-tasking of a constrained resource (sensor, weapon, satellite) against an
unplanned, time-critical requirement is a generalizable mechanic, not air-domain-specific. A future
feature adding dynamic on-orbit re-tasking (e.g., diverting a tasked sensor to an emergent SSA event)
should reuse the "reserved flexible capacity + pre-delegated authority + compressed validation"
triad this section documents, rather than reinventing it.

### Sources

- *JP 3-60, Joint Targeting* (Joint Chiefs of Staff, 2007 ed. archival copy) —
  [live](https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)
  · accessed 2026-06-28.

### 3.6 Kill Chains

**Mental model.** The kill chain is the F2T2EA sequence — Find, Fix, Track, Target, Engage,
Assess — the doctrinal decomposition of "successfully act on a target" into discrete, individually
measurable steps, used for both deliberate and dynamic targeting
([JP 3-60](https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)). Each step has a distinct
failure mode and a distinct owner, which is the entire point of decomposing the chain.

**Planning assumptions.** Each link is assumed independently fallible — a target can be Found but
lost before Fix, Fixed but untrackable through maneuver/concealment, Tracked but untargetable for
lack of weapon-target pairing, and so on; the chain's reliability is the product of every link's
reliability, not the weakest link alone (though the weakest link dominates in practice).

**Operational constraints.** Each link has its own latency and its own sensor/platform dependency;
the chain's total latency is the sum of link latencies, and a target with a short "shelf life"
(mobile, perishable) can expire before the chain completes.

**Command philosophy.** Because links are often owned by different organizations (ISR collects,
an operations center fixes/tracks, a strike asset engages, a separate cell assesses), kill-chain
doctrine is inseparable from command-relationship doctrine (§3.8) — chain speed is largely a
function of how well those handoffs are synchronized, not any single link's intrinsic speed.

**Measures of effectiveness.** Per-link success/dropout rate, end-to-end chain completion rate, total
chain latency against target shelf-life.

**Decision-making under uncertainty.** Doctrine explicitly tracks where in the chain a given
prosecution is most likely to fail and pre-positions redundancy (multiple sensors for Find/Fix,
multiple weapon-target pairing options for Target/Engage) rather than assuming any one link will
succeed.

**Transferable lesson.** This simulator's existing engagement math
([R117](../encyclopedia/R117-directed-energy-and-kinetic-effects.md), `engine/engage.py`,
`engine/custody.py`'s weapons-quality gate) already implements a Find→Fix→Track→Target→Engage
analog (detection → custody → weapons-quality track → engagement order → resolution); this section
makes that lineage explicit and adds the missing **Assess** link as a named, doctrinally-grounded
gap: a future feature scoring post-engagement effect confirmation (did the jam/cyber/kinetic effect
actually achieve the intended degradation) should be framed as closing the F2T2EA loop's final link,
not as an unrelated new mechanic.

### Sources

- *JP 3-60, Joint Targeting* (Joint Chiefs of Staff) —
  [live](https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)
  · accessed 2026-06-28.

### 3.7 Time-Sensitive Targeting (TST)

**Mental model.** A time-sensitive target is one requiring immediate response because it poses a
danger to friendly forces or is a highly lucrative, fleeting opportunity — TST is dynamic targeting
(§3.5) under its most severe time pressure, with a dedicated cross-component coordination process
because no single component typically owns every TST's full kill chain
([JP 3-60](https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)).

**Planning assumptions.** A TST cell/process is pre-established before execution begins, not
improvised when the first TST appears — doctrine treats TST coordination machinery as a planning
deliverable, not an execution-time afterthought.

**Operational constraints.** TST timelines are measured in minutes; any cross-component approval
step not pre-delegated becomes the binding constraint on whether the target is serviceable at all.

**Command philosophy.** TST authority is explicitly pre-delegated to the lowest acceptable level and
rehearsed before execution — the same decentralized-execution logic as §3.4/§3.5, applied to the
single highest-pressure case.

**Measures of effectiveness.** TST nomination-to-engagement timeline, percentage of nominated TSTs
serviced within their window, rate of TST misidentification under time pressure.

**Decision-making under uncertainty.** TST decisions accept materially higher risk of error than
deliberate targeting in exchange for speed — doctrine names this trade-off explicitly rather than
treating TST mistakes as simple process failures; the mitigation is pre-rehearsed procedure, not
slower decision-making in the moment.

**Transferable lesson.** An emergent, fleeting orbital event (a brief access window to a maneuvering
threat, a short-notice conjunction requiring immediate avoidance, a narrow jam-window of
opportunity) is this simulator's TST analog. The doctrinal answer — pre-established coordination
process and pre-delegated authority, rehearsed in advance — argues for any future "urgent window"
UI feature to be designed around a pre-configured fast path (e.g., a standing pre-approved
order template a cell can fire without per-instance White Cell adjudication) rather than an ad hoc
escalation each time, mirroring the TST cell concept.

### Sources

- *JP 3-60, Joint Targeting* (Joint Chiefs of Staff) —
  [live](https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.bits.de/NRANEU/others/jp-doctrine/jp3_60(07).pdf)
  · accessed 2026-06-28.

### 3.8 Command Relationships

**Mental model.** Air doctrine resolves "who decides" through a small, named set of authority types
(combatant command, OPCON, TACON, support relationships) and a designated airspace control authority,
most often a single JFACC exercising centralized control over theater air, land, and sea-based air
assets made available — the doctrinal answer to coordinating a scarce, theater-wide, cross-Service
resource ([JP 3-30](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)).

**Planning assumptions.** Command relationships are established *before* execution, in writing, and
are assumed stable for the duration of the operation unless explicitly changed — ambiguity about who
has authority over a given asset at the moment of decision is treated as a planning failure to be
prevented, not a normal friction to be resolved live.

**Operational constraints.** Different Services/nations bring different command-and-control
cultures and releasability rules to a coalition air operation; the JFACC construct exists partly to
paper over those differences with one theater-wide authority, but coalition caveats still constrain
which forces a given tasking authority can actually direct.

**Command philosophy.** Centralized Command–Distributed Control–Decentralized Execution
([AFDP 3-0](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf),
2025-01-22) is the explicit, named resolution of the tension between unity of effort (one
commander's intent governs) and the tactical initiative every other section in this topic depends on.

**Measures of effectiveness.** Decision latency attributable to command-relationship friction,
rate of cross-component tasking conflicts, coalition-asset utilization rate against caveats.

**Decision-making under uncertainty.** When command relationships are ambiguous mid-execution (a
genuinely contested or newly-formed coalition), doctrine's fallback is to default to the most
restrictive interpretation of authority rather than assume permission — a conservative-by-default
posture under uncertainty.

**Transferable lesson.** This simulator's White/Blue/Red cell structure and the LAN trust-model
limitation documented in CLAUDE.md ("LAN trust model (load-bearing)") is a simplified command-
relationship model; the air-domain lesson is that real command-relationship doctrine treats
authority ambiguity as a *pre-execution planning defect*, which argues that any future multi-
national or multi-cell-authority feature (e.g., a coalition Blue sub-cell) should define its
authority/releasability rules in the vignette's pre-brief, not discover them during play.

### Sources

- *JP 3-30, Joint Air Operations* (2019-07-25) —
  [live](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · accessed 2026-06-28.
- *AFDP 3-0, Operations* (US Air Force, 2025-01-22) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · accessed 2026-06-28.

### 3.9 Air Campaign Planning

**Mental model.** Air campaign planning applies the general operational-art chain ([R301](R301-campaign-design.md)
Campaign Design, [R302](R302-operational-art.md) Operational Art) specifically to the air domain: JFC
guidance → JFACC objectives → air apportionment (the percentage of air effort by mission type:
counterair, interdiction, CAS, etc.) → master air attack plan → ATO (§3.4). Apportionment is the
doctrinally distinct air-specific step — an explicit, recurring resource-allocation decision across
competing mission types, owned by the JFACC and approved by the JFC.

**Planning assumptions.** Campaign planning assumes phased objectives (e.g., gain air superiority
before committing heavily to interdiction) and that apportionment will shift between phases as
conditions change — a static apportionment across a whole campaign is treated as a planning error.

**Operational constraints.** Apportionment is constrained by the finite total sortie-generation
capacity (§3.13) of the available force; competing demands always exceed supply, which is precisely
why apportionment is a named, deliberate decision rather than ad hoc.

**Command philosophy.** The JFACC recommends apportionment; the JFC approves it — a deliberate
check that ties air-specific resource allocation back to the overall campaign's priorities rather
than letting the air component optimize only for air-domain measures.

**Measures of effectiveness.** Achievement of phase objectives on the planned timeline, apportionment-
versus-actual-sortie-execution variance, rate of campaign re-planning (frequent re-planning signals
either poor initial assumptions or a faster-changing environment than planned for).

**Decision-making under uncertainty.** Campaign plans are explicitly revisited at each assessment
cycle (tied to [R306](R306-operational-assessment.md) Operational Assessment) rather than executed
to completion unchanged — the campaign plan is a living hypothesis about how phases will unfold, not
a fixed schedule.

**Transferable lesson.** A vignette author building a multi-phase orbital campaign (e.g., a capstone
vignette per CLAUDE.md's Vignette 8) should explicitly state an "apportionment" analog — how much
of Blue's/Red's effort across the vignette's timeline is allocated to ISR vs. defensive hardening vs.
offensive effects — and revisit it at the vignette's own assessment beats, mirroring the JFACC
apportionment-and-reapportionment cycle rather than leaving effort allocation implicit in player
choice alone.

### Sources

- *JP 3-30, Joint Air Operations* (2019-07-25) —
  [live](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · accessed 2026-06-28.

### 3.10 Air Operations Centers (AOC)

**Mental model.** The AOC is the JFACC's command-and-control node — the physical/organizational
embodiment of the centralized-control half of "centralized control, decentralized execution,"
running the ATO production cycle, the current air picture, and dynamic-targeting cells under one
roof (or distributed network) ([AFDP 3-0.1, *Command and Control*](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0_1/AFDP3-0.1CommandandControl.pdf),
2025-01-22, which superseded the prior standalone AFDP 3-30 C2 publication).

**Planning assumptions.** The AOC assumes a persistent, continuously staffed battle rhythm (shift
structure, standing boards/cells: e.g., a targeting board, an ISR cell, a TST cell) rather than an
ad hoc gathering — the organizational structure itself is doctrine, not just the plans it produces.

**Operational constraints.** AOC throughput (how many ATO lines, dynamic retasking events, and TST
prosecutions it can process per unit time) is itself a finite resource that can become the binding
constraint on tempo, independent of how many aircraft/sensors are physically available.

**Command philosophy.** The AOC exists precisely so that the centralized-control function (§3.8) has
a concrete organizational seat — without it, "centralized control" would be an abstraction with no
process to execute it.

**Measures of effectiveness.** ATO production-cycle adherence, dynamic-tasking response latency,
battle-rhythm board throughput (boards/cells processing their queue within their cycle time).

**Decision-making under uncertainty.** The AOC's standing cells (TST, ISR, targeting) exist
specifically so that uncertain, fast-arriving information has a pre-built process to flow through,
rather than requiring ad hoc routing decisions each time — institutionalizing the decision path is
itself a hedge against decision-making collapse under load.

**Transferable lesson.** The White Cell facilitator role in this simulator is structurally the
AOC's analog — it is the centralized node processing tasking, adjudicating dynamic events, and
maintaining the authoritative picture. The AOC's "boards/cells as standing process, not improvised
each time" lesson argues that White Cell tooling (the inject-authoring panel, the alarm/order-queue
UI in `ui_web/static/app.js`) should keep growing toward named, repeatable workflows for recurring
facilitator decisions (e.g., a standing "contested tasking" resolution process) rather than leaving
each adjudication freeform.

### Sources

- *AFDP 3-0.1, Command and Control* (US Air Force, 2025-01-22) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0_1/AFDP3-0.1CommandandControl.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0_1/AFDP3-0.1CommandandControl.pdf)
  · accessed 2026-06-28.

### 3.11 Mission Planning

**Mental model.** Mission planning is the tactical-level translation of an ATO line into an
executable sortie: route, timing, fuel/tanker plan, weapons/sensor configuration, threat avoidance,
and contingencies — the individual-aircrew-level decomposition of the ATO (§3.4), conceptually the
same "plan-first, execute-at-window" discipline this simulator already enforces
(CLAUDE.md, load-bearing invariant 4).

**Planning assumptions.** Mission planning assumes the broader ATO-level objective and timing are
fixed inputs; the mission planner's freedom is confined to *how* the tasked effect is achieved within
those bounds, not *whether* or *roughly when*.

**Operational constraints.** Threat avoidance (known/suspected IADS coverage, §3.19), fuel/tanker
availability (§3.12), and deconfliction with other simultaneously tasked missions in the same
airspace/time window bound what a feasible mission plan looks like.

**Command philosophy.** Mission planning is delegated to the tactical level (aircrew/squadron) —
the clearest instance of "decentralized execution" in the whole chain, since the AOC does not
dictate exact routing/timing details, only the tasked effect and constraints.

**Measures of effectiveness.** Plan-to-execution deviation rate, contingency-branch utilization rate
(how often the backup plan was needed), fuel/timing margin actually consumed vs. planned.

**Decision-making under uncertainty.** Mission plans are built with explicit branches/contingencies
(alternate routes, abort criteria, bingo fuel) precomputed before execution specifically because
in-flight replanning under threat is slower and riskier than executing a pre-built branch.

**Transferable lesson.** This is a direct doctrinal precedent for this simulator's `dry_run()` /
pre-disabled-button UX and its kinetic consequence-confirm gate (`ui_web`): pre-computing feasible
branches and abort criteria *before* committing an order is the air-domain mission-planning pattern,
not a UI nicety. A future feature adding multi-step contingent orders (e.g., "maneuver, then if
custody is lost, fall back to plan B") should be framed as bringing this simulator's order system
closer to genuine mission-planning contingency branching.

### Sources

- *JP 3-30, Joint Air Operations* §III (mission planning's place inside the ATO cycle) —
  [live](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · accessed 2026-06-28.

### 3.12 Tanking (Air Refueling)

**Mental model.** Air refueling is treated as a force-multiplying *enabler*, not a mission in
itself — it converts basing/range limitations into a scheduling problem (tanker availability and
track timing) rather than a hard range ceiling, and is planned as a tightly time-coupled dependency
of nearly every other long-range air mission ([JP 3-30](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)).

**Planning assumptions.** Tanker support is planned and allocated through the same ATO process as
strike/ISR missions — a tanker track and on-load time are themselves ATO lines, meaning tanking
competes for the same finite planning/scheduling capacity as every other mission type.

**Operational constraints.** Tanker availability (airframe count, basing proximity, track airspace)
is a hard ceiling on how much "extended range" the force actually has, regardless of how many
receiver aircraft exist — tankers are frequently the limiting resource, not the receivers.

**Command philosophy.** Tanker tasking is centrally managed (within the AOC, §3.10) precisely
because a single tanker asset typically supports many receivers across multiple missions — a
classic shared-resource scheduling problem requiring central arbitration, not squadron-level
self-coordination.

**Measures of effectiveness.** Tanker on-time/on-station rate, fuel offload rate against planned
receiver demand, mission-abort rate attributable to tanker unavailability.

**Decision-making under uncertainty.** Receiver aircraft plan fuel margins (bingo fuel) assuming a
tanker rendezvous could fail, and abort criteria are pre-set rather than decided in the moment —
the same precomputed-contingency logic as §3.11, specialized to the single highest-consequence
dependency.

**Transferable lesson.** Tanking is the air domain's clearest analog to this simulator's access-
window/contact-scheduling logic: a capability (extended range) that exists only because a shared,
schedulable resource (the tanker track) was available at the right time and place — directly
analogous to a satellite's command uplink or telemetry downlink only being available during a
ground-station contact window. The "tanker is the limiting resource, not the receiver" lesson
maps onto ground-station/SSN contention: a future feature modeling multiple satellites competing
for the same ground-station pass should expect the *station*, not the satellites, to be the
binding constraint, exactly as tanker availability — not receiver count — typically binds an air
campaign's reach.

### Sources

- *JP 3-30, Joint Air Operations* (2019-07-25) —
  [live](https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/wp-content/uploads/2019/09/JointAirOperations_jp3_30.pdf)
  · accessed 2026-06-28.

### 3.13 Sortie Generation

**Mental model.** Sortie-generation rate — how many missions a given force of aircraft/maintainers/
weapons can launch per day — is the unit of *throughput* the entire air campaign is built on; air
campaign planning ([AFDP 3-0](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf))
treats it as a measurable, finite production-line output, not an assumed-unlimited input.

**Planning assumptions.** Planners assume a sustainable steady-state sortie rate lower than a
short-term surge rate — surge capacity can be drawn down for a critical period but is explicitly
not treated as the planning baseline, because maintenance, aircrew fatigue, and parts supply
constrain sustained throughput.

**Operational constraints.** Maintenance turnaround time, spare-parts/weapons stock, aircrew crew-
rest requirements, and basing/ramp space jointly bound achievable sortie rate — a constraint set
that is logistics-and-personnel-driven, not purely a function of airframe count.

**Command philosophy.** Sortie-generation capacity is a planning input the JFACC must know and
respect when setting apportionment (§3.9) — campaign objectives are checked against sustainable
throughput, not set independently of it and assumed achievable.

**Measures of effectiveness.** Sorties flown per available aircraft per day, mission-capable rate,
maintenance turnaround time, sortie-cancellation rate.

**Decision-making under uncertainty.** Commanders track sortie-generation trend lines (degrading
mission-capable rate, slipping turnaround time) as an early-warning indicator of unsustainable
operating tempo, adjusting apportionment proactively rather than waiting for an outright shortfall.

**Transferable lesson.** This simulator's clock-lag watchdog (`SessionManager._record_catch_up_lag`,
CLAUDE.md "Key facts") and its bus/payload resource model (`engine/bus.py`, EPS/thermal limits) are
the orbital-domain throughput constraints in this lesson's sense — a constellation's sustainable
tasking rate (commands per pass, collection requests per day) is bounded by power/thermal/storage
budgets exactly as sortie rate is bounded by maintenance/aircrew/parts. A future feature explicitly
modeling "constellation tasking throughput" as a tracked MOE (analogous to sortie-generation rate)
would give White Cell the same early-warning signal air commanders get from a degrading mission-
capable rate.

### Sources

- *AFDP 3-0, Operations* (US Air Force, 2025-01-22) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · accessed 2026-06-28.

### 3.14 Readiness

**Mental model.** Readiness is the multi-dimensional capacity to execute the assigned mission *now*
— a composite of personnel, equipment, training, and sustainment status, formally tracked (in the
US system) through status-of-resources-and-training reporting; doctrine treats readiness as a
continuously monitored input to risk, not a binary "ready/not ready" flag.

**Planning assumptions.** Readiness is assumed to degrade under sustained high tempo and must be
deliberately rebuilt (training, maintenance recovery periods) — campaigns that consume readiness
faster than it regenerates are planned as unsustainable past a certain duration.

**Operational constraints.** Readiness recovery (retraining, deferred maintenance burn-down,
personnel rest) takes calendar time that competes directly with operational tempo — a force cannot
simultaneously surge tempo and rebuild readiness.

**Command philosophy.** Commanders are required to report readiness status candidly up the chain
specifically because higher-echelon apportionment/campaign decisions (§3.9) depend on accurate
readiness input — readiness reporting integrity is treated as a command responsibility, not a
local optimization.

**Measures of effectiveness.** Mission-capable rate, qualified-crew ratio, training currency rate,
time-to-recover-readiness after a high-tempo period.

**Decision-making under uncertainty.** Commanders weigh accepted risk (operating below ideal
readiness because the mission demands it) explicitly and document it, rather than silently
absorbing risk — readiness reporting doctrine is built around making degraded-readiness risk
visible to the decision-maker who owns the trade-off.

**Transferable lesson.** A constellation's "readiness" analog spans crew/operator proficiency,
ground-segment availability, and spacecraft SOH margin (`engine/bus.py` limits/safe-mode gating).
The lesson that readiness recovery competes with tempo for the same calendar time argues that a
vignette modeling sustained high-tempo operations should show SOH margin or safe-mode risk actually
degrading over the vignette's duration if operators never throttle back — currently an implicit
consequence of resource draw-down rather than an explicitly surfaced "readiness" metric a White
Cell facilitator could point to in an AAR.

### Sources

- *AFDP 3-0, Operations* (US Air Force, 2025-01-22) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · accessed 2026-06-28.

### 3.15 Attrition

**Mental model.** Attrition is tracked as a rate against a finite, slowly-replenished force
structure — air planners model not just "losses so far" but the *trend* against replacement
capacity, because a sustainable-looking loss rate can still be unsustainable if replacement
(aircrew training pipelines, airframe production/repair) cannot keep pace.

**Planning assumptions.** Pre-campaign attrition estimates are built into the plan (expected loss
rates by mission type, e.g., higher for OCA strike packages into dense IADS than for rear-area
ISR) so that force-structure sustainment is planned proactively, not discovered as a crisis mid-
campaign.

**Operational constraints.** Aircrew training pipelines and airframe production/repair are both
slow relative to a campaign's tempo — attrition that outpaces either becomes an irreversible
capacity loss for the remainder of the campaign, not a recoverable dip.

**Command philosophy.** Commanders are expected to adjust mission selection (favoring lower-
attrition mission types, increasing OCA/SEAD support for high-attrition ones, §3.18) as observed
attrition trends emerge — attrition management is an active campaign-shaping input, not a passive
statistic.

**Measures of effectiveness.** Loss rate by mission type, replacement-to-loss ratio, cumulative
combat power remaining versus campaign-plan assumptions.

**Decision-making under uncertainty.** Early-campaign attrition data is sparse and noisy; doctrine's
answer is to treat early trend estimates with explicit caution and revise mission risk acceptance
as more data accumulates, rather than over-fitting force-structure decisions to a handful of early
data points.

**Transferable lesson.** This simulator currently treats most space effects as reversible
(CLAUDE.md "What this is") with kinetic effects rare and consequence-gated — meaning "attrition" in
this domain is dominated by irreversible kinetic loss and by debris-driven collateral attrition
([R117](../encyclopedia/R117-directed-energy-and-kinetic-effects.md)). The air-domain lesson that
attrition estimates must be tracked as a trend against slow replenishment (here: replacement
satellites have launch-cadence lead times far longer than any vignette's timescale) argues that a
capstone-tier vignette modeling sustained conflict should treat "constellation attrition vs.
no realistic replenishment within the exercise" as a deliberately modeled scarcity, not an
afterthought — directly reinforcing [R312](R312-space-strategy.md) §3's kinetic-restraint framing
from the attrition-economics side rather than the escalation side.

### Sources

- *AFDP 3-01, Counterair Operations* (2023-06-15, attrition-by-mission-type framing) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · accessed 2026-06-28.

### 3.16 Survivability

**Mental model.** Survivability doctrine decomposes into reducing *susceptibility* (don't be
detected/targeted) and *vulnerability* (if hit, don't be destroyed) — a deliberate two-stage
framing (often summarized as "don't be seen, don't be hit, don't be killed") that lets planners
attack each stage with different countermeasures (stealth/EW for susceptibility, hardening/
redundancy for vulnerability).

**Planning assumptions.** No survivability measure is assumed to reduce risk to zero — planners
combine multiple layered measures (tactics, EW, escort, altitude/routing) precisely because each
individually-imperfect layer compounds into materially better aggregate survivability.

**Operational constraints.** Survivability measures often trade against mission performance
(altitude for terrain-masking costs sensor range; EW emissions for self-protection can itself be
a detectable signature) — every survivability choice has a stated operational cost, not a free
improvement.

**Command philosophy.** Mission commanders are expected to actively manage the susceptibility/
vulnerability trade-off mission-by-mission based on the specific threat environment, rather than
applying a single standing posture regardless of context.

**Measures of effectiveness.** Loss rate normalized by sorties into a given threat density,
detection rate by adversary sensors, hit-to-kill ratio for systems that are engaged.

**Decision-making under uncertainty.** Survivability planning is explicitly probabilistic (expected
loss rate given an estimated, uncertain threat density) rather than deterministic — commanders
accept a stated risk level rather than seeking an unachievable guarantee of survival.

**Transferable lesson.** The susceptibility/vulnerability split maps directly onto this simulator's
own design: susceptibility reduction is custody denial (low-observable orbits, maneuver, decoy/
deception per the five D's' "deceive" category) while vulnerability reduction is bus/payload
hardening and safe-mode resilience (`engine/bus.py`, `engine/recovery.py`). Naming this split
explicitly gives vignette authors a doctrinally precise vocabulary for separating "Blue avoided
detection" from "Blue survived being targeted" in an AAR, rather than collapsing both into an
undifferentiated "survived" outcome.

### Sources

- *AFDP 3-01, Counterair Operations* (2023-06-15, susceptibility/vulnerability framing applied to
  asset protection) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · accessed 2026-06-28.

### 3.17 Electronic Warfare

**Mental model.** EW is doctrinally split into three pillars — electronic attack (deny/degrade
adversary use of the EM spectrum), electronic protection (protect friendly use of it), and
electronic warfare support (sense the spectrum to enable the other two) — now folded under the
broader Air Force "Information in Air Force Operations" doctrine alongside EMSO (electromagnetic
spectrum operations) ([AFDP 3-13, *Information in Air Force Operations*](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-13/3-13-AFDP-INFO-OPS.pdf)).

**Planning assumptions.** EW is planned as contested and mutual — both sides are assumed to be
actively jamming/sensing/protecting in the same spectrum, so EW planning explicitly anticipates
adversary EW against friendly systems, not just friendly EW against the adversary.

**Operational constraints.** EM spectrum is a shared, finite physical resource — friendly EA can
self-jam friendly systems sharing the spectrum, so EW planning requires deconfliction (frequency
management) as a hard operational constraint, not just adversary-effect planning.

**Command philosophy.** EW is centrally deconflicted (frequency/spectrum management authority)
precisely because uncoordinated EW employment can degrade friendly systems as readily as
adversary ones — a direct echo of the centralized-control logic in §3.4/§3.8 applied to a shared
physical medium instead of airspace.

**Measures of effectiveness.** Adversary system denial/degradation duration and reliability,
friendly fratricide-jamming incidence, spectrum-access availability for friendly C2/sensors.

**Decision-making under uncertainty.** EW effectiveness against a specific adversary system is
often estimated from incomplete signals intelligence on that system's actual susceptibility —
commanders weigh expected effect against the risk the adversary has more resilience (frequency
agility, hardening) than assessed.

**Transferable lesson.** This simulator's jam modulation database (`engine/jam.py`) and the cyber
exception's non-window-gated resolution (`engine/effects.py`, `engine/cyber.py`) already mirror
the EA/EP/ES three-pillar split conceptually (jamming = EA, cyber posture/patchability = EP,
SIGINT = ES, per `engine/sigint.py`); the explicit transferable lesson is the *mutual contestation
and self-fratricide* point — a future feature should consider whether Blue's own jamming can
degrade Blue's own command_uplink/telemetry_downlink channels sharing the same frequency band, a
constraint the current six-access-channel model does not yet represent and which real EW doctrine
treats as a first-order planning concern, not an edge case.

### Sources

- *AFDP 3-13, Information in Air Force Operations* (US Air Force, 2026-05-01) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-13/3-13-AFDP-INFO-OPS.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-13/3-13-AFDP-INFO-OPS.pdf)
  · accessed 2026-06-28.

### 3.18 SEAD/DEAD Concepts

**Mental model.** Suppression of Enemy Air Defenses (SEAD) temporarily neutralizes adversary IADS
(§3.19) for the duration of a strike package's vulnerability window; Destruction of Enemy Air
Defenses (DEAD) permanently destroys IADS nodes — the same temporary-vs-permanent distinction this
simulator's own five-D taxonomy makes explicit (deceive/disrupt/deny/degrade as reversible,
destroy as not) ([AFDP 3-01](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)).

**Planning assumptions.** SEAD is planned as a tightly time-coupled escort/support function — its
effect must be active precisely when the supported strike package is in the threat envelope, not
merely "at some point during the mission"; DEAD, by contrast, has effects that persist and so can be
front-loaded earlier in a campaign.

**Operational constraints.** SEAD requires accurate, current IADS order-of-battle intelligence
(emitter locations, engagement-zone geometry) — stale or wrong intelligence is the dominant SEAD
failure mode, more often than insufficient SEAD capacity itself.

**Command philosophy.** SEAD support is tasked through the same centralized ATO process as the
strike package it protects, deliberately synchronized rather than independently scheduled, because
SEAD's entire value depends on precise timing coordination with the package it protects.

**Measures of effectiveness.** IADS engagement-radar activity suppressed during the protected
window, strike-package loss rate with vs. without SEAD support, permanent IADS-node attrition (DEAD).

**Decision-making under uncertainty.** Commanders weigh SEAD investment (escort jammers, dedicated
SEAD strikes) against strike-package risk tolerance using an uncertain IADS picture — over-investing
in SEAD wastes scarce capacity if the IADS threat was overestimated; under-investing risks the
package if underestimated.

**Transferable lesson.** SEAD/DEAD is the clearest air-domain precedent for this simulator's own
deny/degrade-vs-destroy split applied at the *system* level rather than the single-target level: a
temporary, escort-synchronized suppression of a ground-based threat (jamming a ground-based
laser/RF threat to satellites, or a cyber/EW action against an adversary's space-surveillance/C2
node) precisely timed to a vulnerable friendly pass, versus a permanent destructive option. A future
Red-IADS-style "space-relevant ground threat network" feature (jam sites, ASAT batteries,
counterspace C2 nodes with engagement-zone-like geometry) would be the natural place to import the
SEAD/DEAD temporary-vs-permanent and escort-timing concepts wholesale.

### Sources

- *AFDP 3-01, Counterair Operations* (2023-06-15, SEAD/DEAD as named sub-missions of OCA) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · accessed 2026-06-28.

### 3.19 Integrated Air Defense (IADS)

**Mental model.** An IADS is modeled by planners as a *system*, not a collection of independent
threats — sensors (early-warning and engagement radars), C2 nodes, and shooters (SAMs, interceptor
aircraft) are netted together, so an effective counter-IADS plan targets the network's connective
tissue (C2, sensor-to-shooter links) as much as the individual shooters
([JP 3-01](https://irp.fas.org/doddir/dod/jp3_01.pdf); [AFDP 3-01](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)).

**Planning assumptions.** A capable IADS is assumed layered (overlapping engagement zones at
different ranges/altitudes, redundant sensors) specifically to deny any single point of failure —
planners assume defeating one layer does not defeat the system, mirroring the layered-defense logic
real defenders apply deliberately.

**Operational constraints.** IADS engagement-zone geometry (radar horizon, missile envelope,
overlapping coverage) creates exploitable seams (gaps in coverage, altitude bands with reduced
overlap) that route planning and SEAD (§3.18) are built to find and use.

**Command philosophy.** Because an IADS is a networked system, doctrine frames counter-IADS
campaigns around degrading network *functions* (detection, identification, engagement
coordination) rather than attriting individual nodes one at a time without regard to network
effect.

**Measures of effectiveness.** Network detection/engagement-coordination degradation (not just
node-count attrition), coverage-gap exploitation rate, friendly penetration success rate against
the netted system as a whole.

**Decision-making under uncertainty.** IADS order-of-battle is rarely fully known — mobile SAMs,
emission-control discipline, and deception (decoy emitters) all degrade planners' confidence in the
picture; doctrine's response is to treat the IADS picture as a continuously-updated, never-complete
estimate, the same posture as §3.3's air-superiority assessment.

**Transferable lesson.** This is the most direct, near-literal transferable concept in this section:
a ground-based or space-based counterspace threat network (jam sites, ASAT/DA-ASAT batteries,
RPO-capable co-orbital assets, cyber C2 nodes, SSA sensors feeding a Red targeting picture) is
structurally an IADS — a netted sensor/C2/shooter system, not a set of independent point threats.
A White Cell or Red AI doctrine preset (`spacesim/session/redai.py`) modeling a sophisticated Red
threat environment should explicitly model network *functions* (Red's detection-to-engagement
coordination chain) as the thing Blue degrades, not just individual Red asset attrition — this is
the single highest-value air-domain import for this simulator's threat-modeling future work, since
no current R1xx topic names the netted-system framing explicitly.

### Sources

- *JP 3-01, Countering Air and Missile Threats* (Joint Chiefs of Staff) —
  [live](https://irp.fas.org/doddir/dod/jp3_01.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://irp.fas.org/doddir/dod/jp3_01.pdf)
  · accessed 2026-06-28.
- *AFDP 3-01, Counterair Operations* (2023-06-15) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-01/3-01-AFDP-COUNTERAIR.pdf)
  · accessed 2026-06-28.

### 3.20 Space Support to Air Operations and Multi-Domain Operations

**Mental model.** Space support to air operations (PNT, SATCOM, missile warning, weather, ISR
cueing) is treated by air doctrine as an assumed enabling layer underneath nearly every other
section above — and the explicit, named recognition that this dependency runs both directions
(air/cyber/land effects can equally support space operations) is now formal doctrine under Joint
All-Domain Operations (JADO): "actions by the joint force in multiple domains integrated in
planning and synchronized in execution, at speed and scale needed to gain advantage," spanning air,
land, maritime, cyberspace, and space plus the EMS
([USAF Role in Joint All-Domain Operations](https://www.doctrine.af.mil/Portals/61/documents/Notes/Joint%20All-Domain%20Operations%20Doctrine--CSAF%20signed.pdf),
content folded into [AFDP 3-0, *Operations*](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf),
2025-01-22, superseding the standalone SDP 3-99 "DAF Role in Joint All-Domain Operations" of
2021-11).

**Planning assumptions.** Air campaign plans historically assumed largely-uncontested space support
(GPS, SATCOM availability) as a given; JADO doctrine's central planning shift is to stop assuming
that and instead plan explicit cross-domain dependencies and degraded-space-support contingencies
into the air campaign itself.

**Operational constraints.** Cross-domain synchronization (an air strike timed against a space-
based ISR cue, or a space effect timed against an air-domain window) is bound by the slowest
domain's own decision/execution cycle — multi-domain tempo is set by whichever domain's kill chain
(§3.6) is least responsive, not the fastest one.

**Command philosophy.** JADO doctrine explicitly resists creating a single all-domain JFACC-
equivalent; instead it emphasizes integration *across* existing component commanders' centralized-
control structures (§3.8) — multi-domain command philosophy is additive coordination between
domain-owning authorities, not a new super-authority replacing them.

**Measures of effectiveness.** Cross-domain effect synchronization rate (effects landing within
their planned mutual-support window), degraded-space-support mission continuity (how well air
operations sustain tempo when a space-support function is denied/degraded), cross-domain sensor-to-
shooter latency.

**Decision-making under uncertainty.** JADO explicitly treats "which domain's effect arrives first
and how that changes the other domains' options" as a live, contestable estimate rather than a
fixed sequencing plan — commanders must be ready for a domain's contribution to be late, denied, or
degraded and have a cross-domain branch plan, the multi-domain analog of §3.11's mission-planning
contingency branches.

**Transferable lesson.** This is the section that should most directly inform this simulator's own
multi-domain posture: the simulator already models a contested-space-support dependency *implicitly*
(jam/cyber denying command_uplink or telemetry_downlink degrades a satellite's usefulness to whatever
it supports), but JADO doctrine's explicit naming of cross-domain *synchronization* as a first-class
planning object — not just dependency — argues that a future capstone vignette pairing space effects
with a notional supported-domain timeline (e.g., "this jam window must align with a notional strike
window") would be a doctrinally faithful way to extend the simulator from single-domain space
operations toward the multi-domain framing JADO requires, consistent with [R312](R312-space-strategy.md)'s
strategic-frame discipline.

### Sources

- *USAF Role in Joint All-Domain Operations* (US Air Force, CSAF-signed) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/Notes/Joint%20All-Domain%20Operations%20Doctrine--CSAF%20signed.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/Notes/Joint%20All-Domain%20Operations%20Doctrine--CSAF%20signed.pdf)
  · accessed 2026-06-28.
- *AFDP 3-0, Operations* (US Air Force, 2025-01-22, JADO integration) —
  [live](https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.doctrine.af.mil/Portals/61/documents/AFDP_3-0/AFDP3-0Operations.pdf)
  · accessed 2026-06-28.
- *SDP 3-99, The DAF Role in Joint All-Domain Operations* (US Department of the Air Force,
  2021-11, superseded by the above but the original Tier-A statement of the JADO definition) —
  [live](https://media.defense.gov/2022/Jan/19/2002924106/-1/-1/0/SDP%203-99,%20THE%20DAF%20ROLE%20IN%20JOINT%20ALL-DOMAIN%20OPERATIONS.PDF)
  · [snapshot](https://web.archive.org/web/2026/https://media.defense.gov/2022/Jan/19/2002924106/-1/-1/0/SDP%203-99,%20THE%20DAF%20ROLE%20IN%20JOINT%20ALL-DOMAIN%20OPERATIONS.PDF)
  · accessed 2026-06-28.

## 4. Operational Context

Every section above shares one structural pattern worth naming once at the chapter level: the air
domain repeatedly resolves the same underlying tension — a scarce, theater-wide, time-perishable
resource (airspace, sortie capacity, tanker tracks, EM spectrum, AOC throughput) contested between
competing demands, governed by *centralized prioritization with decentralized, pre-delegated
execution authority*. That pattern recurs from air superiority (§3.1) through SEAD/DEAD (§3.18) to
JADO (§3.20) because it is the doctrine's general answer to operating a fast, contested, resource-
constrained domain under uncertainty — not a coincidence of separate sub-disciplines. This
simulator's space domain shares the same structural shape (access windows are the scarce,
perishable resource; SessionManager/CellController is the centralized arbitration point; orders are
plan-first with execute-at-window decentralization), which is precisely why the air domain's mature
doctrine is a productive analogy source rather than an arbitrary cross-domain comparison.

## 5. Implementation Guidance

- **Treat "degree of control," not a binary state, as the default framing for any new space-
  control mechanic** — §3.1's air-superiority spectrum is the doctrinal precedent for
  [R312](R312-space-strategy.md)'s same point; a feature or vignette objective phrased as a binary
  "controls space: yes/no" should be revised toward a graded, access-window-bounded formulation.
- **Any future Red-threat-network feature (ground jam sites, ASAT batteries, counterspace C2,
  SSA sensors feeding Red's targeting) should be modeled as a netted IADS-style system** (§3.19) —
  with explicit sensor→C2→shooter connective functions a Blue player can degrade, not as
  independent point threats whose only relationship is being summed for total Red capacity.
- **A future dynamic/urgent-tasking feature (sensor diversion, TST-style emergent-target handling,
  §3.5/§3.7) should reuse the "reserved flexible capacity + pre-delegated authority + compressed
  validation" triad**, not invent a new ad hoc fast path each time a new urgent-event type is added.
- **Multi-step contingent orders and pre-computed abort criteria (§3.11's mission-planning
  contingency branches, §3.12's tanker-rendezvous bingo-fuel logic) are the doctrinal precedent for
  extending `engine/orders.py` beyond single-step plan-and-execute** toward branching plans — worth
  citing explicitly if/when that feature is scoped, rather than treating contingent orders as a
  novel UX idea.
- **A capstone-tier vignette pairing a space effect with a notional other-domain timeline (§3.20)
  is the most direct way to extend this simulator from single-domain to the JADO framing** real
  doctrine now requires of space forces — a concrete, citable design target for a future Vignette
  beyond the current capstone.
- **Vignette authors building multi-phase campaigns should state an explicit "apportionment"
  analog** (§3.9) — effort allocation across ISR/defensive/offensive lines that is revisited at
  assessment beats — rather than leaving phase-level effort allocation implicit.

## 6. Feature Mapping

Future SSA-tasking-contention and dynamic-retasking features; Red AI integrated-threat-network
postures (`spacesim/session/redai.py`); multi-step/contingent order system extensions
(`engine/orders.py`); a future JADO-framed capstone vignette; vignette authoring generally
(`docs/vignettes/`).

## 7. Related Topics

[R301](R301-campaign-design.md) (Campaign Design — the general phased-objective vocabulary §3.9
specializes), [R302](R302-operational-art.md) (Operational Art — the tactics-to-strategy connective
layer this topic's command-philosophy sections instantiate for the air domain),
[R305](R305-mission-analysis.md) (Mission Analysis — the intent-to-task translation §3.4/§3.11
specialize), [R306](R306-operational-assessment.md) (Operational Assessment — the assessment-cycle
logic §3.9/§3.14 depend on), [R311](R311-course-of-action-analysis.md) (COA Analysis — the
comparative-option discipline behind apportionment decisions, §3.9), [R312](R312-space-strategy.md)
(Space Strategy — the strategic frame this topic's air-superiority and JADO sections directly
ground), [R313](R313-maritime-operator-perspective.md) (Maritime Operator Perspective) and
[R314](R314-land-operator-perspective.md) (Land Operator Perspective) — the tier's sibling
domain-analogy chapters; sea control/denial/naval C2 and land-component mission command/sustainment
cover the slower, attrition-and-terrain/sustainment-dominated portions of the cross-domain analogy
this chapter's faster, tasking-cycle-dominated air-domain material complements),
[`research/01-doctrine-western.md`](../01-doctrine-western.md) (the
existing Western counterspace doctrine primer this topic's air-domain analogies supplement, not
duplicate).
