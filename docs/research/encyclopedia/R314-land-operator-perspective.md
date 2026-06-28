# R314 — Land Operator Perspective

> **Document ID:** R314
> **Version:** 1.0
> **Status:** 🟡 Draft — citations unverified, see note below
> **Dependencies:** [R301](R301-campaign-design.md), [R302](R302-operational-art.md), [R305](R305-mission-analysis.md)
> **Referenced By:** [R317](R317-space-operator-perspective.md)
> **Produces:** the land-component command/staff vocabulary (mission command, IPB/recon-pull, the
> D3A targeting cycle, sustainment-as-culmination, deception/EW discipline, battle rhythm) used as
> an analogy source for orbital mission planning, vignette authoring, and Red doctrine design
> **Feature Mapping:** DOM-003 (White Cell Framework), DOM-009 (Doctrine Development Framework),
> vignette authoring (`docs/scenarios/`), `docs/training/11-vignette-playbooks.md`
> **Related Topics:** [R301](R301-campaign-design.md) (Campaign Design), [R302](R302-operational-art.md)
> (Operational Art), [R305](R305-mission-analysis.md) (Mission Analysis), [R309](R309-center-of-gravity-analysis.md)
> (Center of Gravity Analysis), [R310](R310-effects-based-operations.md) (Effects-Based Operations),
> [R311](R311-course-of-action-analysis.md) (Course of Action Analysis), [R208](R208-ooda-loops.md)
> (OODA Loops), [R209](R209-planning-theory.md) (Planning Theory), [R303](R303-deterrence-theory.md)/[R304](R304-escalation-dynamics.md)
> (Deterrence Theory / Escalation Dynamics)
> **Last Reviewed:** 2026-06-28
> **Primary Sources Consulted:** 0 (verification blocked this session — see note)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

> ⚠ **Citation status.** Every doctrine citation in §3 below is an **unverified placeholder**. This
> session's `WebFetch` tool returned HTTP 403 for every URL tested — including non-doctrine control
> URLs (`example.com`, Wikipedia) — so no live-URL check or Wayback snapshot could be performed, and
> per the project's standing rule against guessing URLs, no URL is included. Publication titles and
> dates below are drawn from established, stable doctrine identifiers (training knowledge), not
> network-confirmed. **This file must not be treated as `✅ Done` per the quality gate in
> `docs/research/10-sources-and-methodology.md` §6 until a follow-up pass with working network
> access verifies (or corrects) every citation, adds live + Wayback links, and updates
> `primary_sources_consulted`.**

## 1. Purpose

The encyclopedia's existing Tier R300 topics draw their doctrinal grounding almost entirely from
joint- and strategic-level publications (JP 5-0's operational art, mission analysis, and
campaign-design vocabulary in [R301](R301-campaign-design.md)/[R302](R302-operational-art.md)/[R305](R305-mission-analysis.md);
Clausewitz/Strange-and-Iron's center-of-gravity theory in [R309](R309-center-of-gravity-analysis.md)).
Land-component tactical and staff-level practice — the body of process and judgment a career land
officer or NCO internalizes (mission command, the intelligence/targeting cycle, sustainment
discipline, deception/EW tradecraft) — is a separate, richer source of *transferable* operational
principles that has not yet been captured. This topic exists to give a vignette author, White Cell
designer, or Red AI doctrine author that vocabulary, translated into orbital terms, as a deliberate
analogy source — not as an infantry-tactics primer.

## 2. Scope

Covers: mission command philosophy (commander's intent, mission orders, disciplined initiative);
intelligence preparation and reconnaissance-pull as the process that precedes committing force;
the targeting cycle as a decide-detect-deliver-assess loop; sustainment, protection, and reserves as
finite-resource discipline; deception, electronic warfare, and communications discipline; and
battle rhythm / combined-arms / multi-domain integration as staff-synchronization practice. Does
**not** cover: campaign-level sequencing or branches/sequels (that is [R301](R301-campaign-design.md)),
the tactics-to-strategy connective layer (that is [R302](R302-operational-art.md)), center-of-gravity
identification (that is [R309](R309-center-of-gravity-analysis.md)), effects-based cascading-effects
planning (that is [R310](R310-effects-based-operations.md)), formal course-of-action comparison
method (that is [R311](R311-course-of-action-analysis.md)), deterrence/escalation theory (that is
[R303](R303-deterrence-theory.md)/[R304](R304-escalation-dynamics.md)), or OODA-loop/general planning-theory
mechanics (that is [R208](R208-ooda-loops.md)/[R209](R209-planning-theory.md)) — all of those are
already covered elsewhere in this tier and this topic deliberately points to them rather than
re-deriving them.

## 3. Concepts

**Mission command: intent, mission orders, and disciplined initiative.** Land doctrine (the
practitioner reference is *ADP 6-0, Mission Command*, dated 2019-07-31 — citation unverified, see
note above) names mission command as the philosophy of providing subordinates a clear commander's
intent and end state and trusting them to exercise *disciplined initiative* within that intent
rather than waiting for step-by-step direction. Practitioners think this way because communications
degrade — through jamming, displacement, casualties, or simple distance — exactly when decisions
matter most, so a force that can only execute literal, current orders becomes brittle at the worst
possible moment. **Orbital analogy:** a Blue operator working a short, jammed, or otherwise
contested access window cannot pause for live clarification mid-pass; this is the command-philosophy
reason a vignette's `intro_brief` mission statement must carry enough intent for a player to act
correctly without an out-of-band "ask the GM" loop, directly extending [R305](R305-mission-analysis.md)'s
intent-vs-task vocabulary with *why* that intent has to be self-sufficient. **Strength:** tolerant of
degraded links, fast at the point of execution. **Limitation:** it presupposes shared doctrine and
trust built before the operation — a force (or a Red AI posture) that has not internalized intent
will improvise *badly*, not flexibly, under ambiguity; this is a concrete, doctrinally grounded
lever for differentiating Red doctrine presets in `redai.py` beyond raw capability tuning.

**Intelligence preparation and reconnaissance-pull.** Land intelligence doctrine's IPB process (the
practitioner reference is *ATP 2-01.3, Intelligence Preparation of the Battlefield/Battlespace*,
dated 2019-03-01 — citation unverified) runs four steps — define the operational environment,
describe effects, evaluate the threat, determine threat courses of action — before a force commits
to maneuver. Maneuver-warfare doctrine's companion concept, *reconnaissance-pull* (the practitioner
reference is *MCDP 1, Warfighting* — citation unverified), holds that the reconnaissance picture
should actually steer where the main force commits, rather than merely confirming a pre-set plan.
Practitioners think this way because committing before the picture is adequate risks the force into
an unfavorable engagement, while over-committing to a rigid pre-reconnaissance plan wastes the very
information the reconnaissance assets gathered. **Orbital analogy:** this is structurally identical
to the engine's custody theory and weapons-quality gate (`engine/custody.py`) — committing a
kinetic or directed-energy engagement before establishing weapons-quality custody is the orbital
analog of maneuvering blind, and tasking SSN/ISR collection before committing fires
(`engine/ssn.py`'s priority-SLA request, `engine/isr.py`'s beam tasking) is reconnaissance-pull in
this domain. **Limitation:** reconnaissance-pull costs time an access window may not grant — a
tension the engine already encodes structurally rather than abstractly, since a pass simply ends
when it ends.

**The targeting cycle: Decide-Detect-Deliver-Assess (D3A).** Joint targeting doctrine (the
practitioner reference is *JP 3-60, Joint Targeting*, dated 2018-09-28 — citation unverified) frames
targeting as a four-step cycle: *decide* what to target and under what pre-authorized criteria before
an opportunity appears, *detect* it with sufficient confidence, *deliver* the effect, and *assess*
the result, feeding back into the next decide step. The doctrinal point of separating decide from
detect is that a fleeting opportunity should never require inventing engagement criteria on the fly.
**Orbital analogy:** this maps directly onto the engine's existing order lifecycle —
*decide* is the ROE block's pre-authorized engagement criteria, *detect* is custody/track-confidence
build via SSN/ISR/SIGINT, *deliver* is order execution at the access window
(`engine/orders.py`), and *assess* is the telemetry/AAR review that informs the next cycle. A
vignette or White Cell rule that conflates decide with detect — defining engagement criteria only
once a target has already appeared — reproduces the exact anti-pattern D3A's decide/detect split
exists to prevent. **Limitation:** D3A assumes engagement criteria can be specified in advance;
ambiguous, dual-use contacts (a maneuvering object that might be debris, might be hostile) stress the
model — precisely the ambiguous-RPO inject pattern already present in
`spacesim/content/inject_library.yaml`.

**Sustainment, protection, and reserves as finite-resource discipline.** Land sustainment and
protection doctrine (the practitioner references are *ADP 4-0, Sustainment* and *ADP 3-37,
Protection*, both dated 2019-07-31 — citations unverified) treat a force's fuel/ammunition/
maintenance posture as the real ceiling on how long an operation can be sustained — the same
*culmination point* [R302](R302-operational-art.md) already names — while protection and a
deliberately withheld reserve are the means of absorbing an unexpected reverse without it cascading
into a rout. Practitioners think this way because a commander who commits all available combat power
has no capacity to respond to the unexpected, while a commander who never expends a reserve never
achieves a decision either — reserve management is itself a continuous judgment call, not a fixed
rule. **Orbital analogy:** Δv budget, state of charge, and ammo/storage are the literal sustainment
ledger ([R111](R111-power-and-thermal-operations.md), [R112](R112-propulsion-and-maneuver-planning.md));
the decision to hold an asset — or a fraction of fleet Δv — back from the current engagement is the
direct orbital analog of a land reserve decision. **Implementation note carried into §5:** a vignette
author tuning resource budgets per [R302](R302-operational-art.md)'s culmination-point guidance
should explicitly decide whether the scenario rewards holding a reserve, since the engine has no
mechanic that distinguishes a deliberate reserve from simply unused budget — the lesson, if intended,
must come from scenario design alone. **Limitation:** a reserve that is never committed is wasted
potential, and judging *when* to commit it is exactly the kind of judgment-under-uncertainty MSTR-003
§2 identifies as unteachable by lecture.

**Deception, electronic warfare, and communications discipline.** Land information-warfare doctrine
(the practitioner references are *JP 3-13.4, Military Deception*, dated 2017-12-26, and *JP 3-13.1,
Electronic Warfare*, dated 2012-02-08 — citations unverified) formalizes deception and electronic
warfare as distinct mechanisms: deception induces a target to act against its own interest by
manipulating its *perception*, while EW and emissions/communications discipline (EMCON) deny or
degrade the adversary's ability to observe or communicate *at all*. Practitioners separate the two
because a deceived adversary acts confidently on a false picture (often more damaging than a blinded
adversary who knows it is blind), while an adversary denied outright at least knows something is
being hidden from it. **Orbital analogy:** this is the direct doctrinal ancestor of the build spec's
five-D effect taxonomy (deceive / disrupt / deny / degrade / destroy, `engine/effects.py`) — a
vignette author choosing between a deception-themed inject (e.g. spoofed telemetry) and a
jam-themed inject (`engine/jam.py`) is making the same category choice a land EW planner makes
between MILDEC and jamming. **Limitation:** deception requires accurately modeling the target's
perception — a deception the target doesn't notice, or doesn't believe, fails completely, a harder
bar than denial, which still works against a target that knows it is being denied.

**Battle rhythm, combined arms, and multi-domain integration.** Staff battle-rhythm practice (the
practitioner reference is *ATP 6-0.5, Command Post Organization and Operations*, dated 2017-03-01 —
citation unverified) is the discipline of recurring, synchronized staff touchpoints — targeting
boards, intelligence updates, sustainment syncs — that keep a multi-domain staff's many parallel
processes converging on the same shared picture rather than silently drifting apart. Combined-arms
doctrine (the practitioner reference is *ADP 3-90, Offense and Defense* — citation unverified) holds
that distinct capabilities (armor, infantry, fires, aviation) achieve together what none achieves
alone; the U.S. Department of Defense's unclassified Combined Joint All-Domain Command and Control
(CJADC2) concept (publicly summarized circa 2022 — citation unverified) extends the same logic across
domains including space. **Orbital analogy:** White Cell's own facilitation cadence — pause/resume,
inject scheduling, AAR review (DOM-003 §5) — is functionally a battle rhythm for the exercise itself;
a vignette that requires Blue to integrate EW, ISR tasking, and kinetic/DE effects toward one
objective is exercising combined-arms judgment in miniature, and any future feature cueing
terrestrial fires from space-based ISR would be implementing CJADC2's actual integration problem, not
a simulator-only abstraction. **Limitation:** real battle rhythm and combined-arms integration carry
genuine coordination overhead (meeting time, deconfliction friction) that a simplified single-cell
exercise can understate relative to an actual multi-domain staff.

### Sources

*No verified sources. See the citation-status note above.* The following are unverified
practitioner-reference identifiers, pending a follow-up verification pass:

- *Headquarters, Department of the Army, ADP 6-0, Mission Command: Command and Control of Army
  Forces* (2019-07-31) — [UNVERIFIED — needs live + Wayback check].
- *Headquarters, Department of the Army, ATP 2-01.3, Intelligence Preparation of the
  Battlefield/Battlespace* (2019-03-01) — [UNVERIFIED — needs live + Wayback check].
- *Headquarters, United States Marine Corps, MCDP 1, Warfighting* (1997-06-20) —
  [UNVERIFIED — needs live + Wayback check].
- *Joint Chiefs of Staff, JP 3-60, Joint Targeting* (2018-09-28) — [UNVERIFIED — needs live +
  Wayback check].
- *Headquarters, Department of the Army, ADP 4-0, Sustainment* (2019-07-31) —
  [UNVERIFIED — needs live + Wayback check].
- *Headquarters, Department of the Army, ADP 3-37, Protection* (2019-07-31) —
  [UNVERIFIED — needs live + Wayback check].
- *Joint Chiefs of Staff, JP 3-13.4, Military Deception* (2017-12-26) —
  [UNVERIFIED — needs live + Wayback check].
- *Joint Chiefs of Staff, JP 3-13.1, Electronic Warfare* (2012-02-08) —
  [UNVERIFIED — needs live + Wayback check].
- *Headquarters, Department of the Army, ATP 6-0.5, Command Post Organization and Operations*
  (2017-03-01) — [UNVERIFIED — needs live + Wayback check].
- *Headquarters, Department of the Army, ADP 3-90, Offense and Defense* (2019-07-31) —
  [UNVERIFIED — needs live + Wayback check].
- *U.S. Department of Defense, Combined Joint All-Domain Command and Control (CJADC2), public
  summary* (circa 2022) — [UNVERIFIED — needs live + Wayback check].

## 4. Operational Context

Land force commanders and staffs build this mindset through repeated, often high-stakes practice for
one structural reason: communications degrade, situations change faster than orders can be re-issued,
and resources are always finite. Mission command, IPB/reconnaissance-pull, the targeting cycle,
sustainment discipline, and deception/EW tradecraft are not five unrelated techniques — they are a
single coherent response to "you will have to decide with incomplete information, under time
pressure, with a force that cannot be infinitely resupplied, against an adversary actively trying to
mislead or deny you." That is structurally the same problem an orbital operator faces: fog-of-war
custody gaps, window-gated access, finite Δv/state-of-charge, and a Red cell employing deception,
jamming, and cyber. This is precisely why the land-component mindset is a deliberate analogy source
for this simulator rather than an unrelated body of tactics.

## 5. Implementation Guidance

- **A vignette's `intro_brief` should supply commander's-intent-grade guidance** sufficient for a
  player to exercise disciplined initiative during a single access window without out-of-band
  clarification — extends [R305](R305-mission-analysis.md)'s existing intent/task guidance with the
  command-philosophy reason that intent must be self-sufficient.
- **Red doctrine profiles (`redai.py`) modeling a less experienced or doctrinally weaker adversary
  should differ in reconnaissance-pull discipline** — committing an engagement before adequate
  custody, the land analog of committing maneuver before adequate reconnaissance — rather than only
  differing in raw capability or speed. This gives `redai.py` a behaviorally distinct, doctrinally
  grounded lever beyond numeric tuning.
- **A vignette's ROE block should pre-specify engagement criteria (the D3A "decide" step) separately
  from the custody-confidence threshold that triggers using them (the "detect" step).** Don't let a
  White Cell rule or vignette design conflate "what's allowed" with "what's been observed."
- **When tuning a vignette's resource budget** per [R302](R302-operational-art.md)'s
  culmination-point guidance, explicitly decide whether the scenario intends to reward holding a
  reserve, and make that legible in the `intro_brief` or `tutorial` block — the engine has no
  dedicated reserve mechanic, so the lesson must come from scenario design alone.
- **Author a deception-vs-denial inject as a deliberate category choice mapped onto the existing
  five-D taxonomy** (`engine/effects.py`), not as an ad hoc narrative flourish — reuse the existing
  deceive/deny distinction rather than inventing a new one.
- **Don't model "battle rhythm" as literal real-time meeting overhead in a vignette** — it is White
  Cell's own facilitation discipline (DOM-003 §5), not a trainee-facing mechanic. The combined-arms
  lesson should come from requiring genuinely multi-effect-category objectives, not from simulating
  staff-meeting friction.

## 6. Feature Mapping

DOM-003 (White Cell Framework) and DOM-009 (Doctrine Development Framework) are the direct
consumers; vignette authoring (`docs/scenarios/`) and `docs/training/11-vignette-playbooks.md` are
where this topic's analogies should surface in author-facing and player-facing material. No
dedicated FS exists yet for a reserve mechanic or a deception/denial inject-authoring UI
distinction — both are candidate future scope this topic motivates rather than requires.

## 7. Related Topics

[R301](R301-campaign-design.md) (Campaign Design, branches/sequels), [R302](R302-operational-art.md)
(Operational Art, the culmination-point concept extended above), [R305](R305-mission-analysis.md)
(Mission Analysis, the intent/task vocabulary extended above), [R309](R309-center-of-gravity-analysis.md)
(Center of Gravity Analysis, what the targeting cycle ultimately targets), [R310](R310-effects-based-operations.md)
(Effects-Based Operations), [R311](R311-course-of-action-analysis.md) (Course of Action Analysis),
[R208](R208-ooda-loops.md) (OODA Loops, the decision-cycle counterpart to D3A),
[R209](R209-planning-theory.md) (Planning Theory), [R303](R303-deterrence-theory.md)/[R304](R304-escalation-dynamics.md)
(Deterrence Theory / Escalation Dynamics, the strategic-level counterpart to deception/EW tradecraft),
[R313](R313-maritime-operator-perspective.md) (Maritime Operator Perspective) and
[R315](R315-air-operator-perspective.md) (Air Operator Perspective) — this tier's other two
domain-analogy chapters; land's slow, attrition-and-terrain-bound tempo is the third leg of the
land/sea/air cross-domain comparison the tier now spans.
