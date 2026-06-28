# R316 — Joint and Combined Operations Perspective

> **Document ID:** R316
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R301](R301-campaign-design.md), [R302](R302-operational-art.md), [R305](R305-mission-analysis.md)
> **Referenced By:** [R102](R102-space-domain-awareness.md), [R108](R108-constellation-operations.md), [R119](R119-space-situational-data-fusion.md), [R208](R208-ooda-loops.md), DOM-003, DOM-009
> **Produces:** the doctrinal vocabulary for multi-cell/multi-domain/multinational exercise design — coalition vignettes, joint-targeting-flavored COG/fires objectives, and any future cross-domain or allied-interoperability feature
> **Feature Mapping:** vignette authoring (`docs/scenarios/`), DOM-003 (White Cell Framework — multi-cell command-relationship modeling), candidate future FS for coalition/multi-domain session design
> **Related Topics:** [R301](R301-campaign-design.md) (Campaign Design), [R302](R302-operational-art.md) (Operational Art), [R305](R305-mission-analysis.md) (Mission Analysis), [R306](R306-operational-assessment.md)
> (Operational Assessment), [R309](R309-center-of-gravity-analysis.md) (Center of Gravity Analysis), [R310](R310-effects-based-operations.md) (Effects-Based Operations), [R311](R311-course-of-action-analysis.md)
> (Course of Action Analysis), [R102](R102-space-domain-awareness.md) (Space Domain Awareness), [R108](R108-constellation-operations.md) (Constellation Operations), [R119](R119-space-situational-data-fusion.md)
> (Data Fusion), [R208](R208-ooda-loops.md) (OODA Loops), [R210](R210-decision-support-systems.md) (Decision Support Systems), [R212](R212-multi-criteria-decision-analysis.md) (MCDA),
> [R312](R312-space-strategy.md) (Space Strategy)
> **Last Reviewed:** 2026-06-28
> **Primary Sources Consulted:** 4

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Every other R300-tier topic reasons about a single command echelon making decisions inside one
domain (space) for one side. Real operations — and a faithful PME simulator's eventual ambition —
never stay that simple: a space operation exists to support land, maritime, air, cyber, and
information operations conducted by a joint force, often built from more than one nation's
forces, integrated through a formal command-relationship structure and a planning process with its
own vocabulary. This topic exists so a vignette author, a White Cell facilitator, or a future
feature author reasoning about multi-cell, multi-domain, or coalition exercise design has the
doctrinal vocabulary for *how* real joint and combined forces actually fit space operations into a
bigger campaign — and so this simulator's space-only engine is extended, if it ever is, in a way
that is faithful to how joint force structures actually work rather than inventing a parallel
vocabulary.

This is the broadest-scope topic in Tier R300. Rather than re-deriving content several existing
topics already own at the operational-art/campaign-design/COG/EBO/assessment layer, this topic's
job is the connective layer above and around them: the joint-force command structure, the
multinational dimension, the planning process that produces a joint operation order, and how the
domains cross-reference each other's space dependencies. Every subsection below states explicitly
which existing R3xx topic it builds on rather than restating, and where it is introducing genuinely
new vocabulary not covered elsewhere in the corpus.

## 2. Scope

**Covers:** joint operational art's command-relationship layer (COCOM/OPCON/TACON, JFC/JFACC/JFMCC/
JFLCC/space component roles); the Joint Planning Process (JPP) as the umbrella process [R305](R305-mission-analysis.md)
(mission analysis) and [R311](R311-course-of-action-analysis.md) (COA analysis) are steps inside; the coalition/combined
distinction and interoperability; multi-domain operations (MDO) and cross-domain synchronization;
joint C2 architectures (mission command philosophy, JADC2); information advantage, intelligence
fusion, and the joint targeting cycle (joint fires); data sharing and decision superiority; joint
sustainment; and how the land, air, and maritime domains each depend on space support capabilities.

**Does not cover:** the campaign-sequencing logic itself ([R301](R301-campaign-design.md)), the tactics-to-strategy
connective reasoning within a single command echelon ([R302](R302-operational-art.md)), translating intent into
tasks ([R305](R305-mission-analysis.md)), identifying the COG to target ([R309](R309-center-of-gravity-analysis.md)), the cascading-effects
planning model ([R310](R310-effects-based-operations.md)), comparing courses of action ([R311](R311-course-of-action-analysis.md)), measuring whether
an effect was achieved ([R306](R306-operational-assessment.md)), the SDA task chain or fusion mechanics ([R102](R102-space-domain-awareness.md),
[R119](R119-space-situational-data-fusion.md)), or OODA-loop/decision-support theory ([R208](R208-ooda-loops.md), [R210](R210-decision-support-systems.md)). Each of those remains the
authoritative source for its own concept; this topic only states how that concept sits inside the
joint/combined/multi-domain frame.

## 3. Concepts

### 3.1 Joint operational art and command relationships

[R302](R302-operational-art.md) already covers operational art's tactics-strategy connective function (lines of
operation/effort, operational reach, tempo). What it does not cover is the command-authority
structure joint operational art is exercised *through*. Joint doctrine defines three principal
command-relationship levels: **combatant command (command authority)** (COCOM, non-transferable,
held only by a combatant commander over assigned forces), **operational control (OPCON)** (the
authority to perform functions involving organizing and employing commands/forces, assigning tasks,
and giving direction for all aspects of military operations, normally exercised by a Joint Force
Commander), and **tactical control (TACON)** (limited to the detailed direction and control of
movements/maneuvers within the operational area necessary to accomplish missions/tasks assigned)
([JP 1, *Doctrine for the Armed Forces of the United States*](https://www.jcs.mil/Portals/36/Documents/Doctrine/pubs/jp1_ch1.pdf),
Joint Chiefs of Staff, validated 2017-07-12 [Vol. 1], §III.4). A Joint Force Commander (JFC)
normally delegates execution to **component commanders** — a Joint Force Air Component Commander
(JFACC), Joint Force Maritime Component Commander (JFMCC), Joint Force Land Component Commander
(JFLCC), and, where established, a Joint Force Space Component Commander (JFSCC) — each commanding
their domain's forces under OPCON/TACON from the JFC while contributing capability the other
components draw on ([JP 3-0, *Joint Operations*](https://irp.fas.org/doddir/dod/jp3_0.pdf), Joint
Chiefs of Staff, §III). For US space forces specifically, US Space Command exercises COCOM over
space forces assigned to it, and normally designates a Combined/Joint Force Space Component
Commander to integrate space effects into a given joint operation
([USSF, *Spacepower* Doctrine Document 1](https://www.spaceforce.mil/Portals/2/Space%20Capstone%20Publication_10%20Aug%202020.pdf),
2020-08-10, ch. 4).

This three-level structure (COCOM/OPCON/TACON) is the real-world analog of this simulator's flat
White/Red/Blue cell model — but it is a richer model than the simulator implements. A single
"Blue cell" in this simulator's session model corresponds, in real joint structure, to potentially
several distinct commands (a JFSCC's space component, separately commanded land/air/maritime
components, all under one JFC) each with different OPCON/TACON relationships to the assets they
employ. Today's `CellController`/`SessionAPI` fog-of-war boundary (per-cell, not per-component)
is a deliberate simplification, not a doctrinal claim that real joint command structure is flat.

### 3.2 The Joint Planning Process (JPP)

[R305](R305-mission-analysis.md) covers mission analysis and [R311](R311-course-of-action-analysis.md) covers COA development/comparison/
selection as standalone topics; both are, in real doctrine, specific steps inside a larger seven-step
sequence: **(1)** planning initiation, **(2)** mission analysis, **(3)** COA development, **(4)** COA
analysis and wargaming, **(5)** COA comparison, **(6)** COA approval, **(7)** plan or order
development ([JP 5-0, *Joint Planning*](https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/),
Joint Chiefs of Staff, validated 2020-12-01, §V). The JPP's value for vignette design is the *full
sequence*, not any one step in isolation: a vignette's design process should be traceable through
initiation (why this scenario, for this training objective) → mission analysis ([R305](R305-mission-analysis.md)) → COA
development/analysis/comparison/selection ([R311](R311-course-of-action-analysis.md)) → the resulting `objectives`/`roe`/
`intro_brief` block as the simulator's equivalent of step 7's order. A vignette whose `objectives`
block cannot be traced back through this chain to a stated training rationale is missing the
planning-initiation step's justification, even if each individual objective looks reasonable on its
own.

Joint planning is iterative and parallel, not strictly linear in execution — components plan
concurrently against an evolving common understanding of the mission, not sequentially waiting on
each prior step's complete output (JP 5-0 §V.1). This matters for any future multi-cell coalition
vignette: if Blue's space component and a notional allied land component were both modeled, their
planning should be designed as concurrent and mutually informing, not modeled as one component
waiting idle for another's plan to finish.

### 3.3 Coalition operations vs. combined operations

Joint doctrine and NATO doctrine distinguish two related but distinct multinational concepts.
**Combined operations** is the general doctrinal term (used by both US joint doctrine and NATO) for
military action conducted by forces of two or more allied nations acting together for the
accomplishment of a single mission ([NATO AAP-06, *NATO Glossary of Terms and Definitions*](https://www.coemed.org/files/stanags/01_AAP/AAP-06_2024.pdf),
NATO Standardization Office, 2024 edition, entry "combined"). **Coalition operations** specifically
denotes an ad hoc arrangement between two or more nations for common action, typically formed for a
specific, often unanticipated contingency and lacking the standing command structure, shared
doctrine baseline, and pre-negotiated interoperability of a standing alliance such as NATO ([JP 3-16,
*Multinational Operations*](https://www.jcs.mil/Portals/36/Documents/Doctrine/pubs/jp3_16.pdf), Joint
Chiefs of Staff, validated 2019-07-01, ch. I). The practical consequence of this distinction is
command-relationship maturity: a standing alliance (NATO) has pre-negotiated command relationships,
shared classification/release procedures, and exercised interoperability; a coalition typically must
negotiate all three under time pressure during the crisis that formed it — a directly relevant
design dimension for any future coalition-themed vignette (a "coalition" vignette should model
friction in negotiated command relationships and information-sharing agreements that a "combined,
standing-alliance" vignette would not need to).

Multinational space operations face this distinction acutely because space-derived products
(custody data, SIGINT, imagery) often carry national classification and partner-release
restrictions independent of the tactical urgency of sharing them — a documented friction point in
real multinational space operations ([Secure World Foundation, *Handbook for New Actors in Space*](https://swfound.org/media/206589/swf_handbook_for_new_actors_2018.pdf),
2018, ch. 7 on international cooperation). For this simulator, the closest existing analog is the
SSN's coalition-vs-national affiliation distinction already modeled in `engine/ssn.py`'s
hybrid-turnaround resolution ([R118](R118-space-surveillance-networks.md)) — a real, if narrow, instance of exactly this
release-restriction friction already implemented for one specific subsystem (SSN request priority),
not yet generalized to any other cross-cell data-sharing path.

### 3.4 Multi-domain operations (MDO) and cross-domain synchronization

Multi-domain operations is the doctrinal framing for integrating capabilities across all domains
(land, air, maritime, space, cyberspace) and the information environment to create combined
dilemmas an adversary cannot simultaneously counter in every domain — formalized for the US Army as
[*FM 3-0, Operations*](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN36290-FM_3-0-000-WEB-2.pdf)
(Headquarters, Department of the Army, 2022-10), and pursued jointly under the Department of
Defense's **Joint All-Domain Command and Control (JADC2)** initiative, which aims to connect sensors
from all branches into a single network so any sensor's data can be fused and made available to any
shooter across domains ([GAO-22-104535, *Joint All-Domain Command and Control: Status and Considerations
for Congressional Oversight*](https://www.gao.gov/assets/gao-22-104535.pdf), US Government
Accountability Office, 2022-05-12, pp. 4-7). **Cross-domain synchronization** is the operational
discipline this requires in practice: timing and sequencing actions across domains so each domain's
effect arrives when and where it creates the intended combined dilemma, rather than domains acting
on independent, unsynchronized timelines (JP 3-0 §III.3's "synchronization" principle of joint
operations, applied across domains rather than within one).

For this simulator, MDO/JADC2 is the most directly relevant new vocabulary to the project's own
forward-looking ambitions: this simulator already models one domain (space) with genuine
cross-cutting access-channel/effect/custody mechanics; a future multi-domain extension's central
design challenge would be exactly cross-domain synchronization — timing a space-domain effect (a
jam window, a custody-denial window) against a notional land/air/maritime action's own timeline,
which is a fundamentally different problem from this simulator's current single-domain
access-window scheduling ([R120](R120-access-window-and-geometry-planning.md)). JADC2's "any sensor, any shooter" data-fusion ambition is also the
real-world analog — at a far larger scale and across services rather than within one cell — of this
simulator's already-narrow, documented "last observation wins" fusion model ([R119](R119-space-situational-data-fusion.md)): a
future cross-domain fusion feature should expect the same kind of source-arbitration complexity
JADC2 program assessments flag as a major unsolved engineering challenge (GAO-22-104535 pp. 11-15
on data standardization and integration risk), not assume multi-source fusion is a solved problem
to import wholesale.

### 3.5 Command philosophy: mission command and centralized control/decentralized execution

Joint and Service doctrine converge on **mission command** as the preferred command philosophy: a
commander states intent and end state, then delegates execution authority to subordinates who
exercise disciplined initiative within that intent, rather than commanding by detailed,
centrally-issued instructions for every action ([ADP 6-0, *Mission Command: Command and Control of
Army Forces*](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN30796-ADP_6-0-000-WEB-1.pdf),
Headquarters, Department of the Army, 2019-07, ch. 1). Air and space doctrine express the same
underlying philosophy as **centralized control, decentralized execution**: a single commander
(the JFACC, or for space, the JFSCC/Combined Space Operations Center) retains centralized
*planning and tasking* authority over a domain's assets to ensure unity of effort and efficient
allocation of a scarce, theater-wide resource, while execution of individual missions is delegated
to the tactical level closest to the actual engagement ([AFDP 1, *The Air Force*](https://www.doctrine.af.mil/),
Curtis E. LeMay Center for Doctrine Development and Education, current edition, ch. 3; echoed in
USSF *Spacepower* doctrine, 2020-08-10, ch. 4, for the space-specific case). The doctrinal rationale
is that space and air assets are both theater-wide, scarce, high-demand resources best allocated by
a single authority who can see the whole theater's competing requirements, while the detailed
tactical execution of any one tasking is best left to the operator with the most current local
picture.

This simulator's White Cell role already embodies a version of centralized authority (god-view,
clock/pacing control, DOM-003 §3) but does not yet model the Blue-side internal command-philosophy
question of how *centralized planning/decentralized execution* would distribute authority between a
notional JFSCC-equivalent and individual satellite operators within the Blue cell — today's Blue
cell is a single undifferentiated role, not an internally-tiered command structure. Any future
feature modeling internal Blue-side command tiers (a "space component commander" role distinct from
individual bus/payload operators) should be designed around this real centralized-tasking/
decentralized-execution split, not an arbitrary internal hierarchy.

### 3.6 Information advantage, intelligence fusion, and target development

**Information advantage** is the joint-doctrine term for a position of superiority in the
information environment — current or relative comparative advantage in availability, exploitation,
and protection of information — that, like a center of gravity, is sought to enable favorable
decisions and freedom of action while constraining the adversary's ([JP 3-04, *Information in Joint
Operations*](https://www.jcs.mil/Portals/36/Documents/Doctrine/pubs/jp3_04.pdf), Joint Chiefs of
Staff, validated 2022-09-14, ch. I). This frames the simulator's five-D effect taxonomy
(`research/03-counterspace-taxonomy.md`, [R310](R310-effects-based-operations.md)) at a level above the individual SDA/cyber/jam
mechanic: every disrupt/deny/degrade action against an adversary's space-derived information feed is
also, doctrinally, an information-advantage action, and every custody/SDA gain is doctrinally an
information-advantage gain for the side that achieves it — a useful framing device for vignette
narrative even though the engine does not implement "information advantage" as a distinct scored
dimension.

**Intelligence fusion** at the joint level is the all-source synthesis of intelligence disciplines
(IMINT, SIGINT, HUMINT, MASINT, OSINT, and space-derived SDA products) into a single, coherent
operational picture for the commander, conducted through the **intelligence cycle**: planning and
direction, collection, processing and exploitation, analysis and production, and dissemination and
integration ([JP 2-0, *Joint Intelligence*](https://www.jcs.mil/Portals/36/Documents/Doctrine/pubs/jp2_0.pdf),
Joint Chiefs of Staff, validated 2013-10-22, ch. I-II). [R119](R119-space-situational-data-fusion.md) already documents this
simulator's narrow, single-domain "last observation wins" fusion model for space-track data
specifically; joint intelligence fusion is the doctrinally complete, all-source version of the same
underlying problem (combining heterogeneous sources into one best estimate), at a scale (multiple
intelligence disciplines, multiple domains, multiple echelons) this simulator does not attempt to
model. A future feature claiming to model "joint intelligence fusion" rather than narrow SDA fusion
should be scoped explicitly against JP 2-0's five-phase cycle, not built as an unscoped extension of
[R119](R119-space-situational-data-fusion.md)'s space-only track-fusion logic.

**Target development** is the doctrinal process by which a potential target is analyzed,
characterized, and validated for action through the **joint targeting cycle**: end state and
commander's objectives, target development and prioritization, capabilities analysis, commander's
decision and force assignment, mission planning and force execution, and combat assessment ([JP 3-60,
*Joint Targeting*](https://irp.fas.org/doddir/dod/jp3_60.pdf), Joint Chiefs of Staff, validated
2013-01-31, ch. I, the "six-phase joint targeting cycle"). Deliberate targeting (pre-planned,
following the full six-phase cycle) is distinguished from dynamic targeting (targets that emerge too
quickly for the deliberate cycle, requiring an abbreviated, often **F3EAD** — find, fix, finish,
exploit, analyze, disseminate — process) (JP 3-60 ch. III). This is directly relevant doctrinal
grounding for [R309](R309-center-of-gravity-analysis.md)'s CC/CR/CV chain: target development is the operational process that
*produces* a validated, vetted target from a COG analysis's critical-vulnerability finding — a
vignette's Red or Blue "target" (the asset an effect is aimed at) should be understood as the
*output* of an implicit target-development process the vignette author conducted, even when the
vignette itself only presents the result. The combat-assessment phase closing the cycle is the
joint-targeting-specific instance of [R306](R306-operational-assessment.md)'s MOP/MOE distinction (did the engagement occur
as planned vs. did it achieve the intended effect on the target).

### 3.7 Joint fires and cross-domain effects synchronization

**Joint fires** is the doctrinal term for the use of multiple joint-force fire-support capabilities
(air, land, maritime, space, and cyber/EW "non-kinetic fires") integrated and synchronized to
achieve a desired effect on a target, coordinated through a **Joint Fires Element** or equivalent
cell within the Joint Force Commander's staff ([JP 3-09, *Joint Fire Support*](https://www.jcs.mil/Portals/36/Documents/Doctrine/pubs/jp3_09.pdf),
Joint Chiefs of Staff, validated 2019-12-10, ch. I-II). Space and cyber capabilities are explicitly
recognized as non-kinetic fires options within this framework — a space-domain jam or cyber effect
against an adversary C2 node is, doctrinally, a fires option to be deconflicted and sequenced
against kinetic fires the same way artillery and air strikes are deconflicted against each other,
not a separate category of action outside the fires-coordination process (JP 3-09 ch. II.4 on
"non-kinetic" / electromagnetic and cyberspace fires integration). This is the direct doctrinal
source for why a space-domain effect, in a genuinely joint context, would need deconfliction against
other domains' fires — a synchronization requirement this simulator's single-domain order system
does not need to model today but that any future joint-fires-flavored vignette mechanic should be
designed against, rather than treating space effects as automatically deconfliction-free because
they happen to occur outside the atmosphere.

### 3.8 Joint C2 architectures and data sharing

A **C2 architecture**, in joint-doctrine and systems-engineering use, is the organization,
methodology, and technical means by which a commander exercises authority and direction over
assigned forces — encompassing the command-relationship structure (§3.1), the communications network
connecting echelons, and the information systems that carry the shared operational picture (JP 6-0,
*Joint Communications System*, Joint Chiefs of Staff, validated 2015-06-10, ch. I). The JADC2
initiative (§3.4) is best understood as an attempt to replace today's collection of largely
service-specific, often poorly interoperable C2 architectures with a single, cloud-based,
data-centric architecture in which data is published in standardized formats any authorized
consumer across any domain or service can subscribe to, rather than each system exporting data only
to its own service's downstream systems ([GAO-22-104535](https://www.gao.gov/assets/gao-22-104535.pdf)
pp. 8-10 on the "data-centric" design goal and abstract data layer). **Data sharing** at the joint
level is therefore not primarily a policy question (though release/classification policy, §3.3, is
real friction) but also a genuine technical-architecture problem: format standardization,
common data models, and identity/access management across systems that were never designed to
interoperate (GAO-22-104535 pp. 11-15).

This simulator's `SessionAPI`/`CellController` fog-of-war boundary (CLAUDE.md's "LAN trust model")
is architecturally the opposite design point from JADC2's data-centric ambition: this simulator
deliberately restricts data flow to per-cell views by design (a fog-of-war *feature*, not a
limitation to be engineered away), whereas JADC2's entire premise is to maximize authorized data
flow across previously siloed systems. A future feature that wanted to model "JADC2-style"
cross-domain data sharing within this simulator's frame would need to do so as an explicit,
documented *relaxation* of the fog-of-war boundary for specifically modeled, authorized
cross-component sharing (e.g., a Blue space component voluntarily sharing a custody product with a
notional Blue land/air component) — never as an ambient broadening of what any cell can see, which
would silently violate MSTR-002 §2 invariant 3.

### 3.9 Decision superiority

**Decision superiority** is the joint-doctrine objective of achieving better decisions, made and
acted upon faster than an adversary can react to them, through the combination of information
advantage (§3.6), a shared operational picture, and a streamlined C2 process — not raw information
volume or raw processing speed alone (JP 3-04 ch. I; echoed in the JADC2 program's stated objective,
GAO-22-104535 p. 4). This is the joint-level, cross-domain restatement of [R208](R208-ooda-loops.md)'s OODA-loop
tightness and [R210](R210-decision-support-systems.md)'s decision-support design principles, applied at the scale of an
entire joint force's decision cycle rather than one operator's loop: a faster OODA loop for one
operator does not by itself produce decision superiority for the joint force if the *information*
that operator's decision depends on cannot reach the right decision-maker in time, which is exactly
the data-sharing/C2-architecture problem (§3.8) decision superiority's real-world pursuit is
actually trying to solve. The doctrinal caution directly analogous to [R310](R310-effects-based-operations.md)'s EBO critique
applies here too: decision superiority is frequently invoked as a goal without a correspondingly
rigorous account of how a specific C2 architecture change actually produces it — a future feature
claiming to improve "decision superiority" should be specific about which concrete mechanism (faster
data delivery, better shared picture, fewer approval layers) it changes, not treat the term as
self-evidently achieved by adding more data to a display.

### 3.10 Joint sustainment

**Sustainment** is the joint function providing logistics and personnel services to maintain and
prolong operations until mission accomplishment — and is explicitly named, alongside command and
control, intelligence, fires, movement and maneuver, and protection, as one of the joint functions
every joint operation must integrate (JP 3-0 ch. III). For space operations specifically,
sustainment includes propellant/consumables management, ground-segment maintenance, launch-on-demand
reconstitution, and the orbital-debris-mitigation obligations that constrain how long-duration
assets can be sustained in place ([R112](R112-propulsion-and-maneuver-planning.md)'s Δv budget and [R111](R111-power-and-thermal-operations.md)'s power/thermal margins
are this simulator's existing, if narrowly-scoped, sustainment-adjacent mechanics). [R302](R302-operational-art.md) already
names operational reach/culmination as the campaign-level consequence of sustainment limits; this
topic's addition is naming sustainment itself as the distinct joint function producing that
consequence, and noting that joint sustainment in a real multi-domain operation is shared across
components (e.g., a joint space-launch surge to reconstitute a degraded constellation competing for
the same launch-vehicle/range resources a notional air-domain operation might also need) — a
cross-domain resource-contention dimension this simulator's per-cell, space-only resource model does
not represent.

### 3.11 Interoperability

**Interoperability** is the ability of systems, units, or forces to provide and receive services
from other systems, units, or forces, and to use the services so exchanged to enable them to operate
effectively together — formally distinguished by NATO into technical, procedural, and human
interoperability (shared technical standards, shared procedures/doctrine, and shared
language/training/trust, respectively) (NATO AAP-06, entry "interoperability"; elaborated in
[NATO STANAG 4774/4778](https://nso.nato.int/), the metadata-labeling standards underpinning
coalition information-sharing). Interoperability failures are a recurring, well-documented joint and
combined operations failure mode distinct from any single domain's tactical failure: forces can be
individually proficient and still fail to integrate if their data formats, release procedures, or
shared mental models of the mission do not match — directly continuous with §3.3's coalition-vs-
combined distinction (a coalition's interoperability is, almost by definition, less mature than a
standing alliance's) and §3.8's data-sharing architecture problem (technical interoperability is the
data-format dimension of the same underlying issue).

### 3.12 Lessons from recent joint operations

Post-operation reviews of recent joint and combined campaigns consistently identify a recurring set
of joint-integration failure modes rather than purely domain-specific tactical ones: inadequate
pre-conflict interoperability investment with coalition partners, C2 architectures that could not
keep pace with the tempo of multi-domain operations, and intelligence-sharing procedures that lagged
the speed of the fight ([GAO-22-104535](https://www.gao.gov/assets/gao-22-104535.pdf) pp. 1-3, citing
recent combat-operations and exercise after-action findings as the explicit motivation for the
JADC2 initiative). *Single source (government analyst report).* The specific named after-action
findings GAO-22-104535 draws on are not independently re-derived here from primary after-action
reports (which are largely not publicly releasable); the claim that interoperability and C2-tempo
gaps recur as findings is corroborated at the level of this one Tier-B government oversight
synthesis, not cross-checked against a second independent compilation. This is, doctrinally, the
joint/combined/multi-domain-level restatement of [R310](R310-effects-based-operations.md)'s EBO critique and [R307](R307-wargaming-theory.md)'s wargaming-
validity caution: the most consistently cited *lesson* from recent joint operations is an
integration-process lesson (interoperability, C2 tempo, data sharing), not a domain-specific tactical
lesson — directly relevant to vignette design, since a vignette wanting to teach a "joint operations"
lesson should be built around exactly this integration friction, not around making any single
domain's individual mechanics harder.

### 3.13 How each domain depends on space support

Land, air, and maritime forces each depend on space-domain capabilities in ways this simulator's
engine partially models (PNT, SATCOM, ISR/SDA) and partially only narrates (precision-fires timing,
missile warning, weather):

- **Land domain.** Ground forces depend on space-based positioning, navigation, and timing (PNT) for
  precision-guided munitions and navigation, SATCOM for beyond-line-of-sight C2 to dispersed units,
  and ISR/SDA products for situational awareness of the battlespace — the loss of GPS-quality PNT is
  a frequently cited vulnerability for mechanized and precision-fires-dependent land forces (AFDP 3-14,
  *Space Operations*, LeMay Center, current edition, ch. 2 on space support to surface forces). This
  simulator's `pnt` and `satcom` payload verbs ([`engine/buscommands.py`](../../../spacesim/engine/buscommands.py),
  [R110](R110-communications.md)) are the direct, if abstracted, engine analog of exactly this dependency — a
  vignette depicting land-domain consequences of a space-effect mission should narrate them through
  PNT/SATCOM denial to a notional supported land force, since that is the doctrinally correct
  causal chain, not an arbitrary narrative choice.
- **Air domain.** Air forces depend on space for SATCOM beyond line-of-sight control of remotely
  piloted aircraft, PNT for precision navigation and weapons delivery, missile warning (an early-
  warning function this simulator does not model), and space-based ISR cueing air-tasking decisions
  (AFDP 3-14 ch. 2; USSF *Spacepower* doctrine, 2020-08-10, ch. 3 on space support to air operations).
  The Air Force and Space Force's shared doctrinal lineage (Air Force Space Command's pre-2019
  history, USSF's 2019 stand-up from it) reflects exactly how tightly air and space support have
  historically been organizationally bound — relevant context for why JFACC/JFSCC coordination
  (§3.1) is doctrinally close, not a coincidental pairing.
- **Maritime domain.** Naval forces depend on space-based maritime domain awareness (wide-area ISR
  cueing over-the-horizon targeting), SATCOM for fleet-wide C2 across vast distances no terrestrial
  relay can cover, and PNT for navigation — maritime forces' dependence on persistent, wide-area
  space-based ISR is particularly acute because the maritime domain lacks the terrestrial sensor
  density land/air forces can supplement with (US Naval War College / Andrew Erickson's published
  work on Chinese maritime-space integration is the most-cited open-source treatment of how
  space-based maritime domain awareness changes naval operational reach; cited per
  `docs/research/10-sources-and-methodology.md` §7's canonical registry). This simulator's `isr`
  payload verbs and SAR/EO beam-mode database ([R109](R109-sensor-operations.md)) are the engine analog most directly
  exercised by a maritime-support narrative framing.

## 4. Operational Context

Joint and combined operational practice exists because no single Service or nation possesses every
capability a modern campaign requires, and because the capabilities that do exist only produce
decisive effect when deliberately integrated rather than independently employed — the entire
apparatus described in §3 (command relationships, JPP, MDO/JADC2, joint fires, joint targeting,
interoperability standards) is the accumulated, doctrinally codified answer to "how do you actually
make that integration work in practice, under time pressure, with imperfect information, often
across national lines." Recent doctrine's explicit pivot toward multi-domain operations and JADC2
(§3.4, §3.8) reflects a judgment, reinforced by the recurring after-action findings in §3.12, that
the integration problem itself — not any single domain's individual proficiency — is the limiting
factor in current joint-force effectiveness; that judgment is the single most important takeaway
this topic offers a future feature author reasoning about what a "more realistic" multi-domain
extension of this simulator would actually need to get right.

## 5. Implementation Guidance

- **Treat the simulator's flat per-cell model as a deliberate single-component abstraction, not a
  doctrinal claim that real joint command structure is flat.** Any future feature modeling internal
  Blue-side or coalition command tiers (§3.1, §3.5) should introduce an explicit, documented
  command-relationship layer (e.g., a notional JFSCC role distinct from individual operators) rather
  than silently assuming the existing single Blue cell already represents a full joint force
  structure.
- **A coalition-themed vignette should model negotiated-interoperability friction explicitly, not
  assume seamless data sharing.** Per §3.3/§3.11, the doctrinal distinction between a standing
  alliance and an ad hoc coalition is precisely how much interoperability friction is realistic — a
  vignette depicting a coalition (rather than a single national force) should narrate or mechanically
  represent release-restriction delay or partial-trust SSN-style affiliation gating (`engine/ssn.py`'s
  existing coalition-vs-national distinction, [R118](R118-space-surveillance-networks.md)) as a deliberate design feature, not
  omit it for narrative simplicity.
- **Any future cross-component or cross-domain data-sharing feature must be an explicit, scoped
  relaxation of the fog-of-war boundary, never an ambient broadening of cell visibility.** Per §3.8,
  this simulator's per-cell model is architecturally the opposite of JADC2's data-centric ambition by
  design (MSTR-002 §2 invariant 3); model "JADC2-style" sharing as a specific, authorized,
  documented channel (e.g., a new `share_track` order action with its own validation gate) rather
  than weakening `CellController`'s filtering.
- **A vignette wanting to teach a genuinely "joint" or "multi-domain" lesson should be built around
  cross-domain synchronization friction (§3.4), not around making the space-domain mechanics alone
  harder.** Per §3.12's after-action-finding pattern, the realistic joint-operations lesson is an
  integration-timing lesson — e.g., a space-domain jam window that must be timed against a notional
  land/air action's window, deliberately introducing a scheduling-conflict mechanic — not simply more
  Red assets or tighter ROE in the existing single-domain frame.
- **Frame target-development and joint-fires deconfliction as the doctrinally correct origin story
  for any future "Red/Blue target" mechanic that crosses domains.** Per §3.6/§3.7, a future feature
  letting Blue nominate a target for a notional non-space fires asset (or vice versa) should require
  the same kind of validated-target and fires-deconfliction step real joint targeting does, rather
  than letting cross-domain targeting bypass any gate the existing single-domain order system
  enforces.
- **Don't claim a future feature improves "decision superiority" or "information advantage" without
  naming the specific mechanism changed.** Per §3.6/§3.9's doctrinal caution (directly analogous to
  [R310](R310-effects-based-operations.md)'s EBO critique), these terms describe an *outcome* of specific, named mechanism changes
  (faster data delivery, a better shared picture, fewer approval layers) — a feature description that
  invokes the term without identifying the mechanism is making an EBO-style over-claim in a different
  vocabulary.
- **When narrating domain cross-dependencies (§3.13) in a vignette's `intro_brief`, ground the
  narrative in the correct doctrinal causal chain** (PNT/SATCOM denial → degraded land-force
  precision-fires/C2; SATCOM/ISR denial → degraded air RPA control/targeting cueing; wide-area
  ISR/PNT denial → degraded maritime domain awareness/navigation) rather than a generic "space
  effects matter to everyone" framing — this gives the brief concrete, doctrinally traceable stakes
  for a notional supported force even though that force itself is not separately modeled.

## 6. Feature Mapping

Vignette authoring (`docs/scenarios/`) is the direct consumer for any coalition- or multi-domain-
flavored scenario narrative; DOM-003 (White Cell Framework) is the consumer for any future internal
command-tier or multi-component session-design feature; no dedicated FS-xxx exists yet for a
genuinely multi-domain or coalition-command-relationship feature — this topic is forward-grounding
for whichever future FS first proposes one (most likely an extension of DOM-003's multi-cell model
or a new FS under the candidate "Joint/Coalition Operations" cluster, not yet authorized).

## 7. Related Topics

[R301](R301-campaign-design.md) (Campaign Design — the multi-operation sequencing layer this topic's command structure sits
above), [R302](R302-operational-art.md) (Operational Art — the single-echelon tactics-strategy layer this topic's
command-relationship structure operates through), [R305](R305-mission-analysis.md) (Mission Analysis) and [R311](R311-course-of-action-analysis.md)
(Course of Action Analysis — both JPP steps this topic's §3.2 situates inside the larger process),
[R306](R306-operational-assessment.md) (Operational Assessment — the MOP/MOE distinction §3.6's combat-assessment phase reuses),
[R309](R309-center-of-gravity-analysis.md) (Center of Gravity Analysis — the input §3.6's target-development process formalizes into a
validated target), [R310](R310-effects-based-operations.md) (Effects-Based Operations — the cascading-effects model and EBO
critique §3.9's decision-superiority caution directly parallels), [R102](R102-space-domain-awareness.md) (Space Domain
Awareness) and [R119](R119-space-situational-data-fusion.md) (Data Fusion — the space-only, single-cell instance of §3.6's joint
intelligence-fusion problem), [R108](R108-constellation-operations.md) (Constellation Operations — the per-asset model any future
multi-component command-tier feature would need to compose from, per §3.1's guidance), [R118](R118-space-surveillance-networks.md)
(Space Surveillance Networks — the existing coalition-vs-national affiliation mechanic §3.3/§3.11
cite as the simulator's one real precedent), [R208](R208-ooda-loops.md) (OODA Loops) and [R210](R210-decision-support-systems.md) (Decision Support
Systems — the single-operator-scale concepts §3.9 restates at joint-force scale), [R312](R312-space-strategy.md) (Space
Strategy — the strategic-level theory this topic's operational/tactical-integration layer serves),
DOM-003 (White Cell Framework) and DOM-009 (Doctrine Development Framework — the consumers of this
topic's command-relationship and JPP vocabulary for any future multi-cell or doctrine-translation
work).
