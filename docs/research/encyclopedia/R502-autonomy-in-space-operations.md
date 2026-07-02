# R502 — Autonomy in Space Operations

> **Document ID:** R502
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R501](R501-human-ai-teaming.md)
> **Referenced By:** [R507](R507-autonomous-planning-systems.md), [R508](R508-future-command-and-control.md)
> **Produces:** the real-world autonomy-levels vocabulary for any future bus/payload autonomous-mode feature
> **Feature Mapping:** any future autonomous bus/payload behavior feature (e.g. autonomous safe-mode recovery beyond the existing `RecoverySystem`, autonomous collision avoidance)
> **Related Topics:** [R501](R501-human-ai-teaming.md) (Human-AI Teaming, the general framing), [`engine/recovery.py`](../../../spacesim/engine/recovery.py)
> (`RecoverySystem`, the existing deterministic-rule-based autonomy this topic's levels classify),
> [R507](R507-autonomous-planning-systems.md) (Autonomous Planning Systems), [R508](R508-future-command-and-control.md) (Future Command and Control)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A: ECSS space-engineering standard, NASA technical report — see §3 Sources)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** in-world AI (modeling a real spacecraft's onboard autonomy, distinct from any
coding-agent practice).

## 1. Purpose

Real spacecraft already carry meaningful onboard autonomy (autonomous safe-mode entry, autonomous
collision-avoidance maneuvers, increasingly autonomous mission planning on some platforms) —
independent of any "AI" framing, this is existing space-operations practice. This topic gives the
implementer the standard autonomy-levels vocabulary for classifying both the engine's existing
autonomous behavior (`RecoverySystem`'s rule-based safe-mode recovery) and any future addition, so a
new feature's autonomy level is a deliberate design choice rather than an accident of implementation.

## 2. Scope

Covers: the spacecraft-operations-specific autonomy-degree vocabulary (ECSS mission-execution
autonomy levels, rule-based vs. adaptive/learned autonomy) applied to bus/payload commanding and
fault response. Does **not** cover: the general human-AI teaming vocabulary this topic's levels are
an instance of ([R501](R501-human-ai-teaming.md)'s job), the doctrine of autonomous *weapons*
engagement or targeting authority — that is a policy/ROE question for
[R300](R300-index.md)-tier doctrine research, not this topic — nor the internal planning-algorithm
question of *how* an autonomous system generates its plan
([R507](R507-autonomous-planning-systems.md)'s job). This topic is about classifying *how much*
decision latitude a spacecraft's onboard software has, not about the ethics or algorithms of any
specific autonomous decision.

## 3. Concepts

**Levels of autonomy, from ground control to goal-directed onboard replanning.** The European
Cooperation for Space Standardization's operability standard
[ECSS-E-ST-70-11C](https://ecss.nl/wp-content/uploads/standards/ecss-e/ECSS-E-ST-70-11C31July2008.pdf)
defines four mission-execution autonomy levels used across European space-agency operations
practice: **E1** — mission execution under real-time ground control, with only limited onboard
capability reserved for safety-critical responses; **E2** — execution of pre-planned operations
onboard via a time-based command scheduler (commands are ground-generated but stored and executed
onboard without a real-time link); **E3** — execution of adaptive, event-based operations onboard,
including onboard control procedures that react to onboard-detected conditions without waiting for
ground; **E4** — goal-oriented mission execution, where the onboard system can autonomously replan
activities to meet a stated goal rather than execute a fixed command sequence. `RecoverySystem`'s
existing multi-pass safe-mode recovery ([`engine/recovery.py`](../../../spacesim/engine/recovery.py))
sits at roughly the **E3** level for fault response — it reacts to an onboard-detected fault
condition and executes a documented, deterministic recovery procedure without per-event ground
sign-off — but it does not replan mission *goals* (E4), which is a meaningfully higher and
qualitatively different autonomy character.

**Rule-based autonomy vs. adaptive/learned autonomy.** Most real ECSS-classified onboard autonomy,
including at level E3, is rule-based (documented onboard control procedures, deterministic fault
trees) rather than adaptive/learned. The one well-documented flight precedent for a genuinely
AI-based, model-driven autonomous controller is NASA's **Remote Agent**, flown on the *Deep Space 1*
technology-demonstration mission and given closed-loop control of the spacecraft for several days in
May 1999 — the first AI system to control a spacecraft without real-time human supervision, combining
a planner (onboard mission replanning), an execution system, and a model-based fault diagnoser
([Bernard et al., NASA NTRS 20210001175](https://ntrs.nasa.gov/citations/20210001175)). Remote Agent
is the operative existence proof that E4-class, plan-generating autonomy has flown at all — but it
was a bounded technology demonstration on a single mission, not a norm of current operational
practice, and this simulator's deterministic-engine constraint (CLAUDE.md) matches the far more
common rule-based E2/E3 pattern much better than a Remote-Agent-style adaptive planner would.

**Autonomy appropriateness depends on the time-criticality and reversibility of the decision.** A
collision-avoidance maneuver decision (seconds-to-minutes window, often unreversible if missed) is a
classic case for higher autonomy (E3-E4) in real operations; a mission-replanning decision (more time
available, more consequential, more reversible) is more often left at a lower autonomy level (E1-E2)
with a human in the loop — ECSS's own level scheme is explicitly organized around exactly this
graduated-latitude logic, and it is the basis for evaluating where a future autonomy feature in this
simulator should sit on the spectrum.

**Autonomy and the trust-calibration problem ([R501](R501-human-ai-teaming.md)) compound at the
spacecraft level.** An operator who doesn't understand what their own asset's safe-mode autonomy
will or won't do under a given fault condition is poorly equipped to predict their own asset's
behavior — this is a distinct, asset-level instance of the legibility concern
[R501](R501-human-ai-teaming.md) raises at the advisor level, and the ECSS level (E1-E4) is a
practical, standardized way to state that expectation precisely rather than informally.

### Sources

- *ECSS-E-ST-70-11C, Space engineering — Space segment operability* (European Cooperation for Space
  Standardization, 31 July 2008), §5 Mission execution autonomy levels —
  [live](https://ecss.nl/wp-content/uploads/standards/ecss-e/ECSS-E-ST-70-11C31July2008.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://ecss.nl/wp-content/uploads/standards/ecss-e/ECSS-E-ST-70-11C31July2008.pdf)
  · accessed 2026-07-02.
- *Bernard, D.E. et al. Spacecraft Autonomy Flight Experience: The DS1 Remote Agent Experiment.*
  NASA Technical Reports Server, document 20210001175 —
  [live](https://ntrs.nasa.gov/citations/20210001175)
  · [snapshot](https://web.archive.org/web/2026*/https://ntrs.nasa.gov/citations/20210001175)
  · accessed 2026-07-02.

## 4. Operational Context

Levels of autonomy in spacecraft operations is established aerospace engineering and mission-
operations practice — ECSS-E-ST-70-11C is a normative standard used across ESA and European national
agency missions, not a speculative future-AI topic — and Remote Agent's 1999 flight is a
quarter-century-old, well-documented precedent, not a hypothetical. This grounds any future feature
extending the engine's autonomous behavior in existing real-world practice rather than inventing new
territory.

### Sources

Uses the same sources cited inline in §3 (ECSS-E-ST-70-11C; Bernard et al. 2021/NTRS 20210001175); no
additional sources introduced in this section.

## 5. Implementation Guidance

- **Classify any future autonomous bus/payload feature by its ECSS-style autonomy level explicitly**
  (E1 ground-controlled through E4 goal-directed replanning, §3) in its design documentation, the
  same way `RecoverySystem`'s existing rule-based recovery should be described as roughly **E3** if
  not already.
- **Prefer rule-based, deterministic autonomy (E2/E3) over adaptive/learned autonomy (Remote-Agent-
  style E4) for any new feature**, consistent with the engine's load-bearing determinism invariant
  (CLAUDE.md) — an adaptive/learned autonomous controller would be a significant departure from this
  constraint, closer to the single documented Remote Agent precedent than to normal operational
  practice, and should be flagged as such if ever proposed.
- **Place a new autonomous feature's autonomy level according to the decision's time-criticality and
  reversibility** — a time-critical, low-reversibility decision (collision avoidance) is the strongest
  candidate for E3-E4; a higher-reversibility, more time-available decision should default to E1-E2
  with explicit human sign-off.
- **Document, in any vignette or `intro_brief` referencing autonomous behavior, exactly what the
  asset's autonomy will and won't do**, ideally stated as an ECSS level — per the legibility concern
  above, an operator should be able to predict their own asset's autonomous response to a documented
  fault condition.

## 6. Feature Mapping

Any future autonomous bus/payload behavior feature is the direct consumer; [`engine/recovery.py`](../../../spacesim/engine/recovery.py)'s
existing `RecoverySystem` is the current rule-based-autonomy precedent, classified above as
approximately ECSS level E3.

## 7. Related Topics

[R501](R501-human-ai-teaming.md) (Human-AI Teaming), [`engine/recovery.py`](../../../spacesim/engine/recovery.py) (`RecoverySystem`), [R507](R507-autonomous-planning-systems.md) (Autonomous Planning
Systems), [R508](R508-future-command-and-control.md) (Future Command and Control).
