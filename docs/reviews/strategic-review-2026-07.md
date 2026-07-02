# Independent Strategic Review — SDA Exercise & Experimentation Framework

> **Document ID:** SRB-2026-07
> **Version:** 1.0
> **Status:** Review report — informational, non-binding. Does not modify any reviewed document.
> **Convened as:** Independent Strategic Review Board (long-term project posture review)
> **Panel composition:** Senior Defence Scientist · Space Operations Officer · Systems Architect ·
> Operational Research Analyst · Red Team Lead · Future Concepts Analyst
> **Review horizon:** 10–15 years (2026–2041)
> **Baseline reviewed:** the full design baseline as of 2026-07 — research encyclopedia
> (R100–R509), GDS ladder (`docs/architecture/`, GDS-00–05 authored / GDS-06–10 scaffold),
> ADR-0001–0029, ICD (`design/05-interface-control-document.md`), requirements baseline
> (`docs/requirements/`), domain frameworks (DOM-001–009), feature catalog (FS-101–FS-301),
> implementation packages (IMP-101A–IMP-301A), and the as-built system description in `CLAUDE.md`
> / `docs/FUTURE-WORK.md`.
> **Relationship to prior reviews:** builds on, and does not repeat,
> [`architecture-review.md`](architecture-review.md) (GDS-01–04 consistency),
> [`requirements-baseline-review.md`](requirements-baseline-review.md), and
> [`r313-r317-gap-analysis.md`](r313-r317-gap-analysis.md). Findings duplicated there are cited,
> not re-derived.

[↑ Docs index](../INDEX.md)

---

## Ground rules observed by this board

This review does **not** rewrite approved architecture, create implementation tasks, generate
code, or modify requirements. The design baseline is assumed correct unless strong evidence is
presented otherwise. The board's product is *identified blind spots, strategic risks, and
opportunities* — resolution belongs to the project's own governance mechanisms (Open Questions,
ADRs, `ROADMAP.md`, `FUTURE-WORK.md`), not to this document.

## Executive summary

The project is **unusually well-positioned on engineering fundamentals and unusually exposed on
scale and scope assumptions**. The deterministic, replayable, seam-based core and the
documentation-driven traceability chain are strategic assets that will age well over a 10–15-year
horizon; few training systems anywhere have byte-identical replay as a load-bearing invariant.
The principal strategic risks are that the operational picture the simulator teaches — a
small-fleet (~24 satellites), two-sided, Earth-centric, co-located, facilitator-adjudicated
exercise — is a picture of space operations circa 2020, while the operational environment of
2030–2040 will be proliferated, coalition, commercially entangled, cislunar-extending, and
AI-mediated. None of these shifts invalidates the architecture; all of them stress the *content
and sizing assumptions* baked into requirements and ADRs. The board's highest-priority
recommendations are therefore about widening the aperture (assessment maturity, proliferation,
coalition, commercial actors) rather than re-engineering the core.

---

## Part 1 — Strategic Assessment

### 1.1 Strategic strengths

| # | Strength | Why it endures 10–15 years |
|---|---|---|
| S1 | **Deterministic, replayable core** (ADR-0002; `(initial_state, eventlog, seed) → byte-identical state`) | This is the single most valuable property for institutional *experimentation* use: exact replay, branch-compare, and counterfactual analysis are what turn a trainer into a research instrument. Very few wargaming tools have this; it compounds in value as analytics (FS-301) mature. |
| S2 | **Seam-based fidelity architecture** (`Propagator` / `AccessProvider` / `EffectResolver`, ADR-0009) | Moderate fidelity today is a *choice*, not a ceiling. Higher-fidelity astrodynamics, new effect classes, or external environment models can be substituted without touching session/UI code. This is the correct hedge against fidelity-requirement drift. |
| S3 | **Fog-of-war enforced structurally at the session boundary** (ADR-0004) | Belief-state-only play is the pedagogical core and is architecturally guaranteed, not UI-disciplined. This survives any front-end replacement. |
| S4 | **Content-as-data** (ADR-0007; 19 vignettes as YAML, inject library, doctrine presets) | Scenario currency — the thing that actually decays fastest in training systems — is decoupled from code. A 2035 vignette needs authorship, not a software release. |
| S5 | **Documentation-driven development with an LLM-agent audience** (GDS-00 §2–3, MSTR-005 traceability chain) | Betting that future capability is added by coding agents reading Feature Specs is a forward-leaning and, on current evidence, correct bet. The Training Objective → DOM → R-xxx → FS → IMP → code chain is a genuine differentiator for long-term maintainability under staff turnover. |
| S6 | **Unclassified by design** (GDS-00 §4) | Shareability with PME institutions, allies, and academia is a strategic asset. Classified rehearsal tools cannot occupy this niche; this tool should not try to occupy theirs. |
| S7 | **Offline-first, hardware-floor-respecting runtime** (ADR-0018; government laptop, no GPU) | Deployability into classrooms, deployed settings, and partner nations without infrastructure negotiation. |
| S8 | **The research encyclopedia as a first-class artifact** (R100–R509, ~80 topics) | Encoding *why* the rules are what they are is rare discipline. It makes doctrine-driven revision auditable rather than archaeological. |

### 1.2 Strategic weaknesses

| # | Weakness | Strategic consequence |
|---|---|---|
| W1 | **Fleet-scale assumptions are already dated.** ≤24 satellites soft / 48 hard, constellations ≤3 (ADR-0019, enforced at vignette load per `FUTURE-WORK.md` §6). | The defining feature of the 2025–2040 environment is proliferation (hundreds-to-thousands of objects per architecture). A trainer that *cannot represent* proliferated-architecture play risks teaching a boutique-fleet mental model as if it were the norm. The cap is an engine-load and UI-aggregation problem, not an architectural one — but it is a requirements-level assumption threaded through vignette design, custody workload, and the operator console. |
| W2 | **Assessment and validation are the least mature tier of the stack** (DOM-002 ⛔, DOM-005 ⛔ per `domains/INDEX.md`, while FS-201/FS-301 are marked ✅ — an internal status inconsistency worth resolving). | For the sponsoring research institution, the measurement layer *is* the research product. A simulator that cannot demonstrate training transfer or support instrument-grade measurement is a training aid, not an experimentation framework. This tier lagging the engine by this much is the largest gap between the project's stated research ambition (GDS-00 §5.3–5.4) and its baseline. |
| W3 | **Two-sided, symmetric actor model.** Red and Blue are mirror-image bus/payload operators; no gray/neutral actors, no commercial operators, no third parties (GDS-01 §2). | Real space incidents are dominated by ambiguity about *who* and *what*: dual-use servicing vehicles, commercial constellations under national tasking, third-party collateral. The two-cell model teaches a cleaner world than the one operators will inhabit. |
| W4 | **Co-located, cooperative, trust-based LAN model** (ADR-0015; client-side cell selection, ground-truth endpoints unauthenticated). | Explicitly a v1 design decision, and documented honestly — but it forecloses distributed exercises (multi-site, coalition, remote PME) which are precisely where demand will grow. The RLock single-process ceiling (ADR-0026) compounds this. |
| W5 | **Earth-centric geometry throughout** (GMST ECI↔ECEF frames, Kepler+J2, TLE catalog model). | No representational path to cislunar or xGEO operations, which every allied future-concepts document identifies as an emerging SDA problem. Acceptable now; a hard wall later if frames/catalog assumptions calcify in content and requirements. |
| W6 | **Encyclopedia has a corpus-wide sourcing defect** (every tier index: no mandatory §2 Scope sections, zero `### Sources`, zero frontmatter — self-flagged in R100–R500 indexes). | The encyclopedia's authority claim rests on citation discipline (MSTR-007, `research/10-sources-and-methodology.md`). Uncited forward-looking claims (especially Tier R500) are exactly the ones most likely to be wrong in 10 years and least auditable when challenged. |
| W7 | **Exercise temporality is a single 2-hour session.** No cross-session container (prior architecture review, finding §1.3), no campaign persistence, no multi-week compressed play. | Space competition is a campaign phenomenon (custody decay over weeks, co-orbital loitering over months, Δv budgets over years). The 2-hour vignette teaches engagements, not campaigns. |
| W8 | **AI-Red reads ground truth** (ADR-0024, tracked gap). | Beyond the acknowledged realism defect, this blocks the single most promising research use of the platform: human-vs-machine and machine-vs-machine doctrine exploration under equal information conditions. |

### 1.3 Hidden assumptions (mostly implicit, worth surfacing as a register)

1. **A1 — The adversary is a peer bus/payload operator.** The whole Red model assumes an
   adversary who operates satellites the way Blue does. Adversaries who act primarily through
   ground-segment attack, supply-chain compromise, commercial proxies, or launch-surge
   reconstitution are unrepresented.
2. **A2 — The five-D taxonomy plus the cyber exception is a stable ontology of effects**
   (ADR-0011/0012). Doctrine has already begun re-framing around reversibility, dazzle/deny
   thresholds, and "protect and defend"; the taxonomy is encoded in the effect resolver, the
   requirements, and the vignette schema simultaneously — a change would ripple wide.
3. **A3 — Custody is built from nationally-owned sensors plus a national mock SSN**
   (`build-spec/08-ssn.md`; commercial feed explicitly deferred, `FUTURE-WORK.md` §7). The real
   2030s SDA picture is likely to be commercially dominated and coalition-pooled.
4. **A4 — Human-speed decision loops.** The 1.5 s polling transport and plan-first-at-next-window
   cadence assume all decision-makers are humans. Machine-speed play (AI operators, autonomous
   spacecraft behaviors) breaks the pacing assumptions, not the engine.
5. **A5 — The facilitator is the adjudication authority for everything the engine doesn't model**
   (ADR-0017 manual adjudication). Sound for PME; limiting for unattended experimentation
   campaigns (batch runs, Monte Carlo over seeds) where no human White Cell exists.
6. **A6 — Determinism and AI integration are compatible without a stated doctrine.** The
   deterministic core (invariant 1) and any future non-deterministic AI participant coexist only
   if AI outputs enter the engine as ordered, logged events. This is *achievable within the
   current architecture* — the session layer is the right seam (ADR-0021) — but nothing in the
   baseline states it as a rule, and a future implementer could violate it innocently.
7. **A7 — TLE/Space-Track remains the exchange format and catalog source.** TLE is a legacy
   format being displaced by CCSDS OMM; Space-Track access policy is a single external
   dependency (GDS-02) with no stated fallback beyond manual entry.
8. **A8 — The training audience is CAF/allied space operators in facilitated PME settings.**
   Self-paced individual training, distributed cohorts, and non-space audiences (joint planners
   consuming space effects) are out of the assumed audience but inside plausible demand.

### 1.4 Technology dependencies (with 10–15-year risk posture)

| Dependency | Exposure | Risk trend |
|---|---|---|
| Python 3.11+/NumPy/pydantic/FastAPI (ADR-0020) | Whole stack | Low — mainstream, well-maintained; version-migration burden only. |
| Skyfield/sgp4 + TLE format | Propagation & import | **Medium** — the format (TLE) is the risk, not the library; CCSDS OMM transition is underway. Seam already isolates it. |
| Space-Track (optional, build-time) | Scenario currency | Medium — policy/access risk; commercial SDA APIs are the natural hedge and are already noted as future work. |
| Browser platform (no framework, hand-rolled JS per `ui_web/static/`) | Entire UI | Medium — framework-free is dependency-light but raises the cost of UI-scale features (constellation aggregation, dashboards). A conscious trade, worth re-validating when W1 is addressed. |
| LLM coding agents (GDS-00 §2 — the documentation tree's primary future reader) | Capability growth rate | Low-and-falling — the bet looks right; the risk is *governance* of agent output, which DOM-008 already frames. |
| Single-process in-memory session (ADR-0001/0026) | Scale & distribution | **Medium-high over the horizon** — fine for v1's niche; the binding constraint on every distributed/coalition/large-cohort future. |

### 1.5 Vulnerability to changing military doctrine

- **Proliferation-as-resilience** (SDA Tranche-style architectures, allied equivalents): directly
  stresses W1/A3. If allied doctrine's unit of action becomes the *layer* or *mesh* rather than
  the satellite, the per-asset operator console teaches the wrong unit of thought.
- **Dynamic space operations / sustained maneuver** ("maneuver without regret" enabled by
  refueling and servicing): the Δv-economy model (`design/14-delta-v-economy.md`) currently
  teaches Δv as a non-renewable life budget. That is correct today and possibly wrong within the
  horizon; the lesson it teaches is the kind that has to be *untaught* if logistics change.
- **Protect-and-defend emphasis and norms-constrained kinetics** (post-2022 ASAT-test moratorium
  trend): the baseline already leans reversible-first (GDS-00 §4), which ages well. The gap is
  the *norms/attribution/messaging* dimension of counterspace decisions — R7 legal research
  exists (`research/07-legal-norms-and-roe.md`), but no exercise mechanic makes attribution
  confidence or public-messaging consequence a scored decision variable.
- **Command by intent / mission command for space**: GDS-01 §1 explicitly claims plan-first as
  this system's instance of command-by-intent — a good hook. Doctrine movement toward delegated
  autonomy (machine-executed intent) would require the autonomy concepts in Part 2 to land.

### 1.6 Vulnerability to changing geopolitical conditions

- **Coalition-by-default operations** (CSpO, NATO space domain, bilateral SDA sharing): the
  two-cell model has no representation of multiple Blue nations with different ROE, different
  releasability, or caveated data. This is the most likely near-term sponsor ask the baseline
  cannot serve.
- **Multi-adversary and third-party complexity**: one Red cell assumes one coherent adversary.
  Simultaneous, differently-postured competitors (and non-aligned third parties whose assets
  constrain engagement geometry) are unrepresentable without a session-layer actor generalization.
- **Norm formation and lawfare**: if debris-creating events or interference norms harden into
  treaty-like constraints, ROE modeling must become richer than dials — conditional,
  contested, and asymmetric between cells.

### 1.7 Vulnerability to changing commercial space capabilities

- **Commercial SDA outpacing government catalogs**: already flagged as deferred
  (`FUTURE-WORK.md` §7 commercial feeds). Strategically, the risk is not a missing feature but a
  missing *lesson*: operators trained only on national-sensor scarcity will mis-plan in a world
  of purchasable custody.
- **Commercial augmentation and reserve arrangements** (commercial SATCOM/imagery under national
  tasking): raises targeting-ambiguity and escalation questions the vignette library doesn't
  pose. A Red decision to jam a commercial constellation serving Blue is among the most
  instructive scenarios the framework could offer and is currently unrepresentable as such —
  commercial actors have no standing in the domain model.
- **On-orbit servicing as normalized dual-use RPO**: when servicing vehicles are routine, the
  RPO-ambiguity vignettes (ambiguous-RPO inject exists in the inject library) become the norm
  rather than the exception, and characterization/intent-assessment mechanics deserve more depth
  than a confidence scalar.

---

## Part 2 — Future Concepts

Legend — **Maturity**: research maturity of the underlying concept in the open literature and
allied practice, not this project's readiness. **Timeframe**: estimated implementation effort
window once authorized, not calendar prediction. **Placement**: Current Release (fits v1.x scope
and existing seams) / Future Release (needs new session-layer or content constructs) / Long-Term
Vision (needs new architecture-level thinking or research first).

### FC-01 AI-supported mission planning (COA generation and critique)

- **Description:** An advisory layer that generates, compares, and critiques candidate order
  plans using the existing `dry_run()` validation seam and access-window computation — surfacing
  "here are three feasible COAs and their windows/Δv/risk trade" without deciding for the trainee.
- **Operational motivation:** Space planning is scheduling against geometry (GDS-01 §1); the
  cognitive load of window arithmetic obscures the *judgment* content PME wants to teach.
  DOM-008 §4 and R503 already frame advise-don't-decide.
- **Potential impact:** High — differentiates the platform; doubles as a research instrument for
  human-AI teaming studies (R501).
- **Research maturity:** Medium-high (LLM planning over constrained tool APIs is well-trodden;
  the constraint API — `dry_run` — already exists, which is the hard part).
- **Recommended priority:** High.
- **Timeframe:** 6–12 months from authorization.
- **Placement:** **Future Release** (near-term). The seam exists; the doctrine for
  non-determinism (assumption A6) must be stated first.

### FC-02 Autonomous adversary (AI-Red at fog-of-war parity)

- **Description:** Elevate AI-Red from ground-truth-reading doctrine presets (ADR-0024 gap) to a
  belief-state agent that plans through its own `CellView`, with selectable doctrine profiles.
- **Operational motivation:** Facilitator workload is the binding constraint on exercise
  frequency; a credible AI-Red enables solo/small-group PME and unattended experimentation.
- **Potential impact:** Very high — unlocks self-paced training, batch experimentation, and
  doctrine-exploration self-play (see IN-08).
- **Research maturity:** Medium (belief-state game AI is mature; doctrine-faithful behavior
  validation is not — see GAP-08).
- **Recommended priority:** High (it is already the baseline's own tracked gap).
- **Timeframe:** 3–6 months for fog parity; 12+ for credible doctrine-adaptive play.
- **Placement:** **Current Release** for fog parity (closes an acknowledged defect within
  existing architecture); **Future Release** for adaptive AI-Red.

### FC-03 Autonomous satellite operations (on-board autonomy levels)

- **Description:** Model degrees of spacecraft autonomy (R502): assets that execute stored intent,
  self-safe, auto-evade conjunctions, or refuse unsafe commands — configurable per asset in the
  vignette schema.
- **Operational motivation:** Operators increasingly supervise autonomy rather than command
  buses verb-by-verb; training should exercise *supervision* and *trust calibration*.
- **Potential impact:** Medium-high; changes the operator role the console teaches.
- **Research maturity:** Medium (flight autonomy exists; PME representations of it are immature).
- **Recommended priority:** Medium.
- **Timeframe:** 6–12 months (bus-model and order-system extensions behind existing handlers).
- **Placement:** **Future Release**.

### FC-04 Responsive launch and reconstitution

- **Description:** A launch/reconstitution mechanic — force-add with lead time, cost, and pad/range
  constraints — extending the existing TLE force-add path into a decision variable rather than a
  White Cell fiat.
- **Operational motivation:** Resilience doctrine treats reconstitution as a core response
  option; currently the loss of an asset is strictly terminal within a session.
- **Potential impact:** Medium — most valuable in campaign-length play (FC-13).
- **Research maturity:** High (the operational concept is well documented).
- **Recommended priority:** Medium-low until campaign persistence exists.
- **Timeframe:** 3–6 months as content + session mechanic.
- **Placement:** **Future Release**.

### FC-05 On-orbit servicing, refueling, and space logistics

- **Description:** Servicing vehicles as assets; docking/refuel/repair as order actions; Δv as a
  replenishable (at cost) rather than terminal budget, extending `design/14-delta-v-economy.md`.
- **Operational motivation:** Directly counters the "Δv as life" lesson-decay risk (§1.5);
  servicing vehicles are also the canonical dual-use RPO ambiguity actor.
- **Potential impact:** High for doctrine currency; medium for near-term training demand.
- **Research maturity:** Medium (operations exist; wargame-mechanic treatments are thin).
- **Recommended priority:** Medium.
- **Timeframe:** 6–12 months.
- **Placement:** **Future Release**.

### FC-06 Proliferated constellations and cooperative swarms

- **Description:** Raise the effective object count by an order of magnitude via constellation
  aggregation as a first-class construct — layer-level tasking, health rollups, mesh-routing
  abstractions — rather than per-asset drill-down times N. (Aggregation is already named as v2 in
  `FUTURE-WORK.md` §4; this concept is that item plus the engine-scale and pedagogy work around it.)
- **Operational motivation:** W1 — the environment the trainee will operate in is proliferated;
  the unit of command is becoming the layer.
- **Potential impact:** Very high — this is the single largest content-realism correction
  available.
- **Research maturity:** Medium (mega-constellation C2 literature is young; see GAP-10).
- **Recommended priority:** High.
- **Timeframe:** 12–18 months (engine performance validation + UI aggregation + new vignettes).
- **Placement:** **Future Release** (flagship of the next major release).

### FC-07 Cislunar and xGEO operations

- **Description:** Extend the representational envelope beyond Earth-centric two-body+J2:
  cislunar frames, three-body-regime trajectories (at low fidelity behind the `Propagator` seam),
  xGEO custody with sparse sensing.
- **Operational motivation:** Allied future-concepts documents uniformly identify cislunar SDA as
  an emerging mission; custody scarcity there is *pedagogically* interesting (days-long
  re-acquisition, enormous volumes).
- **Potential impact:** High strategically; low near-term training demand.
- **Research maturity:** Low-medium (operational concepts immature everywhere — an opportunity
  for the sponsoring institution to lead rather than follow).
- **Recommended priority:** Medium as *research*; low as implementation.
- **Timeframe:** 18–36 months; research first.
- **Placement:** **Long-Term Vision**.

### FC-08 Space traffic management and persistent debris environment

- **Description:** A persistent environment layer: conjunction screening wired to the existing
  `prop.collision_avoid` verb (currently unwired, `FUTURE-WORK.md` §2), debris populations that
  *persist across a session* after kinetic events, and STM notification/coordination injects.
- **Operational motivation:** Debris consequence is the strongest argument the five-D ladder
  makes against kinetics; today the debris-cone estimate (`engine/engage.py`) is advisory, not
  world-changing. Making consequence *persistent* makes the escalation lesson visceral.
- **Potential impact:** High pedagogically; medium for research.
- **Research maturity:** High (conjunction assessment R127 exists; debris evolution models are
  mature and simplifiable).
- **Recommended priority:** Medium-high.
- **Timeframe:** 6–12 months.
- **Placement:** **Future Release**.

### FC-09 Coalition operations (multi-national Blue, releasability, caveats)

- **Description:** Generalize the cell model to N cells with asymmetric information-sharing
  policies: coalition Blue cells with national caveats, shared-but-filtered track catalogs,
  differing ROE dials per nation, coalition SSN pooling (the affiliation concept already exists in
  `build-spec/08-ssn.md`'s coalition/national distinction — this extends it to the whole
  information model).
- **Operational motivation:** §1.6 — coalition-by-default is where CAF space operations live;
  R316 (joint and combined) is already in the encyclopedia but has no mechanical expression.
- **Potential impact:** Very high for sponsor relevance; distinctively Canadian value
  proposition (a middle power's exercise framework *should* be coalition-first).
- **Research maturity:** Medium (coalition C2 literature strong; coalition *wargame information
  architecture* thin).
- **Recommended priority:** High.
- **Timeframe:** 12–18 months (fog-of-war engine generalizes; per-cell policy filters are new).
- **Placement:** **Future Release**.

### FC-10 Commercial integration (gray actors, purchasable services)

- **Description:** Commercial operators as a third actor class: purchasable SDA data feeds
  (extending the mock SSN), commercial SATCOM/imagery services either cell can lease, and
  commercial assets as jamming/targeting dilemmas with attribution and escalation consequence.
- **Operational motivation:** §1.7 and A3 — the commercial layer is where much real competition
  already happens; its absence teaches a state-monopoly world that no longer exists.
- **Potential impact:** High; several of the most instructive new vignettes become possible.
- **Research maturity:** Medium; see GAP-03.
- **Recommended priority:** High.
- **Timeframe:** 6–12 months (SSN commercial feed first — already scoped as future work — then
  actor-class generalization).
- **Placement:** **Future Release** (feed) / **Long-Term Vision** (full gray-actor ecology).

### FC-11 Cyber–space convergence (ground segment as terrain)

- **Description:** Deepen the cyber model from per-asset vulnerability resolution (ADR-0012's
  exception) into ground-segment terrain: stations, networks, and the C2 chain as attackable/
  defendable objects, with cyber effects that alter *access* (a compromised station serves
  falsified telemetry or refuses uplink) rather than only asset state.
- **Operational motivation:** The most likely first move in any real space conflict is against
  the ground segment; R107/R116 cover this in research but the domain model treats ground sites
  primarily as access endpoints.
- **Potential impact:** High; also the natural home for deception play (falsified telemetry
  feeds directly into the existing telemetry/attack-signature machinery).
- **Research maturity:** High.
- **Recommended priority:** Medium-high.
- **Timeframe:** 6–12 months.
- **Placement:** **Future Release**.

### FC-12 Multi-domain operations (terrestrial effects abstraction)

- **Description:** A deliberately *abstract* terrestrial layer: joint force demands on space
  (support requests with deadlines), and space effects' terrestrial consequences (a jammed SATCOM
  beam degrades a named terrestrial operation) — scoreboard-level, not a terrestrial simulator.
- **Operational motivation:** R313–R317 (already integrated into GDS-01) establish that space
  mechanics are instances of cross-domain patterns; MDO framing (R505) says space actions only
  matter through terrestrial effect. Without any terrestrial consequence model, counterspace
  choices are scored in space-native terms only.
- **Potential impact:** Medium-high — repositions the tool for joint PME audiences (assumption
  A8's excluded audience).
- **Research maturity:** Medium.
- **Recommended priority:** Medium.
- **Timeframe:** 6–12 months for a scoreboard-level abstraction.
- **Placement:** **Future Release** / **Long-Term Vision** for anything deeper than abstraction.

### FC-13 Campaign persistence and time-scale compression

- **Description:** A cross-session campaign container (prior review §1.3's missing concept):
  persistent world state across sessions, automated quiet-period resolution (fast-forward weeks of
  station-keeping, custody decay, and Δv burn between played episodes), reconstitution timelines.
- **Operational motivation:** W7 — competition is a campaign; custody decay, logistics, and
  co-orbital patience are invisible at 2-hour scale.
- **Potential impact:** High for both PME depth and experimentation (longitudinal studies).
- **Research maturity:** Medium (wargaming literature on campaign-level space play is thin —
  another lead opportunity).
- **Recommended priority:** Medium-high.
- **Timeframe:** 12–18 months.
- **Placement:** **Future Release**.

### FC-14 Digital engineering integration

- **Description:** Treat vignettes, force structures, and doctrine presets as model-based
  artifacts exchangeable with external digital-engineering ecosystems (schema-published, versioned,
  externally validatable), and expose the deterministic engine as a batch experimentation service
  for OR studies (headless Monte Carlo over seeds/parameters — the engine already supports this;
  what is missing is the workflow product around it).
- **Operational motivation:** The sponsoring institution's value chain increasingly runs through digital engineering;
  the deterministic core is a ready-made "authoritative model" candidate.
- **Potential impact:** Medium-high for institutional relevance.
- **Research maturity:** High (practice exists; integration effort only).
- **Recommended priority:** Medium.
- **Timeframe:** 6–12 months for the batch-experimentation workflow; longer for ecosystem exchange.
- **Placement:** **Current Release** for headless batch runs (near-zero engine work) /
  **Future Release** for ecosystem integration.

### FC-15 Human-machine teaming instrumentation

- **Description:** Instrument the platform *as a laboratory* for human-AI teaming research:
  logged advisory interactions (when FC-01 exists), trust-calibration measures, reliance/compliance
  metrics, integrated with FS-301 export and R411/R412 human-subjects methodology.
- **Operational motivation:** The question every force is asking — how do operators calibrate
  trust in AI planning aids — needs exactly this kind of controlled, replayable environment.
- **Potential impact:** Very high for institutional research positioning; modest for training per se.
- **Research maturity:** Medium (measures exist; space-operations-specific findings do not).
- **Recommended priority:** High as a research program anchor.
- **Timeframe:** Staged behind FC-01/FC-02.
- **Placement:** **Long-Term Vision** (with instrumentation hooks considered whenever FC-01/02
  are designed).

### Placement summary

| Placement | Concepts |
|---|---|
| Current Release (fits existing seams/scope) | FC-02 (fog parity), FC-14 (headless batch runs) |
| Future Release | FC-01, FC-02 (adaptive), FC-03, FC-04, FC-05, FC-06, FC-08, FC-09, FC-10 (feed), FC-11, FC-12 (abstraction), FC-13, FC-14 (ecosystem) |
| Long-Term Vision | FC-07, FC-10 (gray-actor ecology), FC-12 (deep), FC-15 |

---

## Part 3 — Research Gap Analysis

The encyclopedia (R100–R509) is broad and unusually well-organized. Two *systemic* defects are
already self-documented (missing §2 Scope sections and missing citations, every tier index) and
are treated here as one gap (GAP-13) rather than re-litigated per topic. The gaps below are
*topical*: places where the 10–15-year horizon needs coverage the current ~80 topics do not give.

| Gap ID | Topic | Why it matters | Operational consequence if unaddressed | Suggested research questions | References / communities | Priority | Architecture impact |
|---|---|---|---|---|---|---|---|
| GAP-01 | **Space environment & space weather operations** | The inject library has a geomagnetic-storm template, but no R-topic grounds environmental effects on drag, comms, sensors, or attack/anomaly disambiguation. | Trainees never practice the hardest real diagnostic: *is this an attack or the environment?* — a core SDA judgment. | How do operators disambiguate environmental vs. adversarial anomalies? What storm-effect fidelity is pedagogically sufficient? | NOAA SWPC; AFRL/RVB; COSPAR; amateur-accessible Dst/Kp indices literature | High | Low — telemetry/effects seams accommodate an environment term |
| GAP-02 | **Debris environment evolution & post-event persistence** | R117 covers kinetic effects; nothing covers debris population behavior after an event, which is the strategic argument against kinetics. | Kinetic decisions in-exercise carry only momentary consequence; the escalation lesson under-teaches. | What minimal debris-evolution model preserves the consequence signal? How should persistent debris gate later access windows? | NASA ODPO; ESA Space Debris Office; IADC guidelines | Medium-high | Medium — persistent world-state layer (supports FC-08) |
| GAP-03 | **Commercial space ecosystem & contested commercial services** | No R-topic on commercial SDA providers, commercial augmentation arrangements, or the targeting/escalation status of commercial assets. | The framework cannot pose the decade's most likely real dilemma: effects against/through commercial systems. | What are the observed patterns of commercial-asset interference? How do allies structure commercial augmentation (e.g., reserve arrangements)? What custody quality do commercial catalogs actually deliver? | Secure World Foundation *Global Counterspace* reports; CSIS Aerospace Security; commercial-SSA provider technical literature | High | Medium — actor-class and SSN-feed generalization (FC-10) |
| GAP-04 | **Cislunar / xGEO operations** | Zero coverage; every allied future-concepts document names it. | The project has no research base from which to even scope FC-07 when asked. | What custody/sensing regimes apply beyond GEO? What C2 latencies and access patterns? What fidelity floor makes cislunar *teachable*? | AFRL Cislunar Highway Patrol literature; NASA CLPS/Artemis SDA work; astrodynamics community (AAS/AIAA) | Medium | High eventually (frames, catalog model) — research now, build later |
| GAP-05 | **Space logistics: launch, reconstitution, servicing economics** | R112 covers maneuver propulsion; nothing covers launch cadence, reconstitution timelines, or servicing logistics as operational variables. | Resilience doctrine (reconstitution as response) unrepresentable; Δv-as-terminal-life lesson decays (§1.5). | What are realistic reconstitution timelines by orbit/class? How does refueling change maneuver doctrine? | Space logistics literature (AIAA); SDA/USSF responsive-space programs; on-orbit servicing consortium (CONFERS) | Medium | Medium (FC-04/FC-05) |
| GAP-06 | **Attribution, signaling, and public messaging in space incidents** | R7/R303/R304/R213 cover legal, deterrence, escalation, signaling in general; the *operational craft* of attribution confidence and messaging as a decision variable is uncovered. | ROE dials stay mechanical; the judgment "act now on 60 % attribution vs. wait" — arguably the central space-crisis decision — is untrained and unscored. | How is attribution confidence built/communicated? What signaling value do reversible effects carry in observed practice? | UNIDIR space security; Lawfare/JAG space literature; SWF; academic deterrence-signaling studies | High | Low-medium — scoring/assessment layer, vignette design |
| GAP-07 | **Training transfer & simulation-based learning effectiveness** | R400 covers experimental design/measurement in general; nothing grounds *does simulator PME transfer to operational performance*, the claim on which the whole program's value rests. | The sponsoring institution cannot defend the platform's training value empirically; assessment layer (DOM-002/005) builds on unstated learning-science assumptions. | What transfer evidence exists for wargame-based PME? Which measured competencies (FS-201) predict operational performance? | I/ITSEC community; military training-effectiveness literature (ARI; allied defence human-effectiveness research); simulation-based medical-education transfer literature (methodologically strongest analog) | **Highest** | Medium — shapes DOM-002/DOM-005 before they harden |
| GAP-08 | **Adversary emulation fidelity & Red behavior validation** | Red doctrine presets exist (`session/redai.py`); no research grounds *how we know* a preset is representative of any real adversary doctrine, or how to validate AI-Red behavior (FC-02). | Exercises may train against a strawman; worse, a *consistent* strawman that players learn to exploit (negative training). | What validation standards exist for red-team behavior models? How should doctrine presets be traceable to observed adversary behavior (R2xx non-Western doctrine docs)? | Red-teaming methodology community (R308's own sources); intelligence-community structured-analytic-techniques literature; wargaming adjudication validity studies | High | Low-medium — validation criteria, not engine change |
| GAP-09 | **PNT warfare and navigation denial operations** | PNT appears as a payload type and verbs (`pnt.set_integrity`), but no R-topic covers GNSS interference operations, spoofing detection, or PNT-denial consequence chains. | A major real-world counterspace activity class (the most *observed* one) is mechanically present but intellectually ungrounded. | What are observed GNSS-interference patterns and their operational signatures? How does PNT denial cascade into terrestrial effect (feeds FC-12)? | GPS/GNSS interference literature; C4ADS/SkAI open-source interference tracking; ION (Institute of Navigation) | Medium-high | Low — mostly content and telemetry-signature grounding |
| GAP-10 | **Proliferated-constellation C2 and mesh operations** | R108 covers constellation operations at the ≤3-sat scale of the current cap; layer-level C2, autonomous mesh routing, and proliferated-fleet operator workload are uncovered. | FC-06 (the flagship correction to W1) would be built without a research base; UI/pedagogy choices would be guesses. | What is the operator's actual unit of command in proliferated architectures? What custody/health abstractions do real proliferated operators use? | SDA (Space Development Agency) public architecture documents; commercial mega-constellation operations talks (SpaceX/OneWeb/Amazon publications); IEEE aerospace | High | High — informs the aggregation constructs |
| GAP-11 | **Distributed simulation & exercise interoperability** | No coverage of federation standards (HLA/DIS/SISO), LVC integration, or how this simulator would participate in larger joint exercises — a standard sponsor ask. | The tool stays a standalone island; joint-exercise integration requests arrive with no research base and an architecture (single-process, polling) never examined against them. | What would federation demand of the SessionAPI seam? Is an eventlog-bridge federation model compatible with determinism? | SISO standards community; NATO M&S Group (NMSG); allied defence M&S practice | Medium | Medium-high — examine *before* any transport rework, not after |
| GAP-12 | **Ground-segment operations as contested terrain** | R107 covers ground-segment ops cooperatively; the *contested* ground segment (cyber/physical/EW attack on stations and networks) has no dedicated treatment. | FC-11 unsupported; the most likely first-move attack surface in real conflict stays a background object. | What ground-segment attack patterns are observed/postulated? What does station compromise look like in telemetry (ties to R121 signatures)? | CISA/space-ISAC advisories; Viasat KA-SAT incident analyses; MITRE SPARTA framework | Medium-high | Medium (FC-11) |
| GAP-13 | **Corpus-wide sourcing & scope defect** (systemic, already self-flagged in every tier index) | The encyclopedia's authority rests on MSTR-007 citation discipline that is currently unmet everywhere; R500 (the tier making the most speculative claims) is entirely uncited. | Any external review (sponsor, peer, academic) can discount the research tier wholesale; forward-looking claims cannot be audited when they age. | N/A — process gap, not topical. | `research/10-sources-and-methodology.md`'s own Tier A–C standard | **Highest** (with GAP-07) | None — documentation hygiene, but it gates the credibility of everything above |

---

## Part 4 — Red Team Review

The board's red-team member was asked to attack the design's assumptions rather than its
implementation. Findings are challenges, not verdicts; several may survive scrutiny.

### 4.1 Over-engineering

1. **The documentation-governance apparatus may exceed the team's carrying capacity.** Three
   authority regimes have already churned (build-spec binding → GDS-level-gated supersession →
   blanket supersession, per `CLAUDE.md` vs. GDS-00 §7 — which, note, still carries the *old*
   "build spec wins" language and now contradicts `CLAUDE.md`'s blanket declaration). A
   traceability chain of Training Objective → DOM → R-xxx → GDS → FS → IMP → code → test is
   seven layers deep for a project of this size. If sustaining the apparatus consumes the effort
   that should go to GAP-07/GAP-13, the apparatus is net-negative. *Challenge: what is the
   minimum governance that preserves the LLM-agent-readability bet?*
2. **Byte-identical determinism may be a stronger invariant than the mission requires.**
   Statistical reproducibility (same seed → same distribution) would suffice for most research
   uses and would remove friction from every future AI/parallelism integration. The board does
   *not* recommend relaxing it — replay-exactness is load-bearing for AAR — but notes the cost is
   paid on every future feature and the trade has never been explicitly re-examined since P1
   (ADR-0002 records the decision, not a re-validation against the AI-era roadmap).
3. **29 ADRs, all `Accepted`.** An ADR corpus with no `Rejected` or `Superseded` entries after
   this much design evolution suggests the record captures conclusions rather than genuine
   decision contests. That weakens its value as a future what-was-considered archive.

### 4.2 Under-engineering

1. **Assessment (DOM-002 ⛔) and validation (DOM-005 ⛔) versus their own shipped features
   (FS-201/FS-301 ✅).** Features built on unauthored frameworks invert the project's own
   traceability doctrine — precisely the failure mode the documentation apparatus exists to
   prevent, occurring in the tier that matters most for the research mission (W2).
2. **Scenario authoring remains White-Cell-hostile** (prior review §1.2, unresolved): YAML
   hand-editing is the only authoring path, against a success vision (GDS-00 §5.1) of a
   no-programming facilitator. FS-108 is a stub. The content-as-data strength (S4) is only
   realized if non-developers can actually author content.
3. **No security architecture beyond "trusted LAN."** Acceptable and honestly documented for v1
   (ADR-0015) — but there is no *documented growth path* (threat model, token design sketch,
   which endpoints would need binding) either, so the first distributed-use request will force
   ad-hoc security decisions under delivery pressure. A deferred design is fine; an undesigned
   deferral is risk.
4. **Data-rights and human-subjects posture for research use is unstated.** FS-301 exports
   cohort performance data; R411 covers human-subjects methodology as research background — but
   no baseline document states who owns exercise-performance data, consent posture, or retention.
   For an institutional experimentation framework, this is a compliance gap, not a nicety.

### 4.3 Missing operational scenarios

- **Attack-vs-environment ambiguity campaign** (GAP-01): a storm and a jamming campaign in the
  same window.
- **Ground-segment-first conflict opening** (GAP-12): Blue loses stations before losing satellites.
- **Commercial-entanglement crisis** (GAP-03/FC-10): Red degrades a commercial service Blue
  depends on but does not own.
- **Reconstitution race** (FC-04): both sides lose assets; the exercise is about recovery, not
  engagement.
- **Sustained campaign / patience play** (FC-13): a multi-week co-orbital stalk compressed into
  playable form — currently every threat conveniently matures inside a 2-hour window.
- **Insider/supply-chain compromise**: an asset that was never trustworthy — tests whether the
  belief-state machinery can represent misplaced *self*-trust, not just adversary uncertainty.

### 4.4 Missing stakeholders and user types

- **Coalition partner cells** with caveated information (FC-09) — stakeholder and user type both.
- **Legal advisor (LEGAD)** as an exercise seat: ROE/attribution decisions currently have no
  advisory role attached, despite R7's research base.
- **Intelligence cell** distinct from operators: fusing SSN + telemetry into assessments is a
  real seat, currently smeared across operator roles.
- **Analyst/OR observer** as a first-class user of live exercise data (beyond post-hoc FS-301
  export).
- **Remote participant** — every user type currently assumes the same room/LAN.
- **The accreditor**: whoever must certify the tool teaches doctrine correctly before an
  institution adopts it. No document names this actor or what evidence they'd need (ties to
  GAP-07/DOM-005).

### 4.5 Missing failure modes

- **Negative training.** Nowhere does the baseline treat "the simulator teaches a wrong lesson
  confidently" as a tracked risk class — e.g., the deterministic AI-Red exploitability problem
  (GAP-08), Δv-terminality (§1.5), or fixed 5-D ontology (A2). The most dangerous failure of a
  trainer is not crashing; it is quietly mis-calibrating its graduates.
- **Facilitator error / adjudication drift**: manual adjudication (ADR-0017) has no
  consistency-support mechanism across facilitators or sessions; assessment comparability
  (FS-201) silently depends on it.
- **Mid-exercise infrastructure failure** with 14 participants: save/resume exists, but there is
  no documented *exercise-recovery drill* (whose job, how fast, what's lost) — an operations
  gap, not a code gap.
- **Content drift**: vignettes encode orbital element sets and doctrine claims that age; nothing
  schedules content revalidation (the governance apparatus versions *documents* but not
  *scenario currency*).

### 4.6 Missing adversary behaviours

- **Deception at catalog scale**: decoys, signature management, and spoofed catalog entries.
  The belief-state machinery is *ideal* terrain for this and it is barely exploited — deception
  currently lives mainly in one D of the effects ladder rather than as a campaign behavior.
- **Proxy and third-party action**: Red acting through a commercial or third-nation asset for
  deniability.
- **Sub-threshold persistent harassment**: reversible interference calibrated to stay below
  response thresholds indefinitely — the actual observed pattern of the last decade — rather
  than vignette-scale discrete attacks.
- **Adaptive exploitation of Blue patterns** across sessions (requires FC-13's campaign memory).

### 4.7 Missing coalition considerations

Consolidated in §1.6 and FC-09: no multi-Blue, no releasability tiers, no national-ROE
asymmetry, no coalition SSN pooling in play (the affiliation hook exists in `build-spec/08-ssn.md`
but is not a player-facing mechanic). The board flags this as the highest-likelihood external
demand the baseline cannot currently meet.

### 4.8 Missing logistics

Launch (FC-04), servicing/refuel (FC-05), ground-network contact scheduling against *allied*
networks (R128 covers scheduling research; the exercise mechanic assumes own-nation stations),
and spares/replenishment economics. Space logistics is on its way to being a named joint
function; the baseline has no hook for it.

### 4.9 Missing training objectives

- Attribution-and-messaging judgment (GAP-06) — decide *and justify* under uncertainty.
- Autonomy supervision and trust calibration (FC-03/FC-15).
- Coalition information-sharing discipline (FC-09).
- Environmental disambiguation (GAP-01).
- Explicit mapping from vignette objectives to an external competency standard (CAF space
  qualification framework or allied equivalent) — FS-201 measures, but against internally
  invented rubrics; the accreditor stakeholder (§4.4) will ask for the external anchor.

### 4.10 Assumptions challenged (summary)

A1–A8 (§1.3) plus: "everyone in the room is on the same team" (ADR-0015) — true until the first
multi-institution or partner-nation use; "the encyclopedia will be finished" — currently a
standing intention with a systemic defect (GAP-13) and no completion forcing-function; "the
build-spec can remain deprecated-but-load-bearing indefinitely" — GDS-06–10 are scaffold-only,
so NFRs, data model, UI architecture, and API currently have *no* authoritative statement at all,
which is strictly worse than a stale one.

---

## Part 5 — Innovation Opportunities

Ranked roughly by value-per-effort. Each leverages something the baseline already has — the
board deliberately avoided ideas requiring new architecture.

| # | Idea | What it leverages | Why it adds value |
|---|---|---|---|
| IN-01 | **Counterfactual AAR ("ghost branch") as a teaching instrument** | Deterministic replay + branch-compare (P7) + `dry_run()` | In debrief, replay the decision point, inject the alternative order the trainee *considered*, and run the branch. "Here is what would actually have happened" is a pedagogical capability almost no wargaming tool can offer honestly — this one can, byte-exactly. Turns S1 from an engineering property into the product's signature. |
| IN-02 | **Headless Monte Carlo experimentation harness** | Determinism + seeded RNG + eventlog + FS-301 export | Batch-run a vignette across seed/parameter sweeps with scripted or AI-Red/Blue policies; distributional outcomes for OR studies (R407 Monte Carlo grounding already exists). Near-zero engine work; converts the trainer into an experimentation framework *literally overnight* for the cost of a runner and an output schema. |
| IN-03 | **Attack-signature diagnosis trainer** | `engine/telemetry.py` attack signatures + nominal-baseline overlay | A micro-drill mode: the system presents telemetry (real cause hidden), the trainee diagnoses jam vs. cyber vs. environment vs. fault against the clock. Converts an existing engine feature into deliberate-practice reps for the single hardest operator judgment (GAP-01). |
| IN-04 | **LLM White Cell assistant** | Inject library + eventlog + vignette schema (all data) | Drafts injects in-schema from facilitator intent, monitors the eventlog for dramatic pacing ("Blue has been idle 20 min; consider inject X"), and drafts the AAR narrative from the log. Attacks the real adoption bottleneck — facilitator workload — without touching the engine or the determinism boundary (assistant output enters as ordinary White Cell actions). |
| IN-05 | **Explainable-constraint tutoring** | `dry_run()` "why can't I" machinery | Extend pre-disabled-button reasons into a Socratic layer: *what would have to change* for this order to be valid (window, custody quality, ROE, Δv). The engine already knows the answer; surfacing it converts every disabled button into a lesson. |
| IN-06 | **Belief-vs-truth divergence analytics** | Fog-of-war architecture: `TrackCatalog` vs. ground truth both exist server-side | Score and visualize *how wrong each cell's picture was, when, and why* (sensor gaps, decay, deception) across the session timeline. This is a genuinely novel exercise metric — most wargames cannot compute it because they don't maintain a rigorous belief/truth split. Feeds assessment (DOM-002) and deception research alike. |
| IN-07 | **Scenario generator (parameterized vignette synthesis)** | Vignette schema + TLE force-add + objectives schema | Generate vignette variants (orbits, timing, force mixes) from a difficulty/learning-objective specification — attacks content-currency decay (§4.5) and enables experimentation designs needing many matched-but-distinct trials (R401 controls). |
| IN-08 | **AI-vs-AI doctrine tournament** | AI-Red (post-FC-02) + IN-02 harness | Self-play across doctrine presets to (a) balance-test vignettes before human use, (b) discover degenerate strategies that would negative-train humans (GAP-08), (c) explore counterspace doctrine space cheaply. A publishable research line in itself. |
| IN-09 | **Live OR-analyst console** | Eventlog + godview endpoints (already ground-truth-exposing by design) | A read-only analyst dashboard: decision latencies, custody quality over time, order/effect chains — during the exercise, not after. Creates the §4.4 analyst seat from existing endpoints. |
| IN-10 | **Cross-exercise cohort progression tracking** | FS-201 rubrics + FS-301 export + the (to-be-created) campaign container | Longitudinal competency trajectories per trainee/cohort across sessions — the artifact instructors and accreditors actually want, and the forcing function for resolving the DOM-002 maturity gap. |

---

## Part 6 — Recommendations

Scales: Value/Difficulty/Research effort/Risk = Low/Medium/High; Confidence = board's confidence
that the recommendation is right, not that it will succeed.

### 6.1 Immediate (governance and posture; no new capability)

| # | Recommendation | Value | Difficulty | Research effort | Risk | Confidence |
|---|---|---|---|---|---|---|
| R1 | **Close the sourcing/scope defect (GAP-13)** tier by tier, R500 first (most speculative claims, zero citations). Treat as a gate for citing the encyclopedia externally. | High | Medium (labor, not skill) | Medium | Low | High |
| R2 | **Author GDS-06–10** (already a standing priority per `CLAUDE.md`) — NFRs, data model, UI architecture, API, RTM currently have no authoritative statement (§4.10). Prioritize GDS-06 NFRs: nearly every Part 2 concept turns on scale/performance/security envelopes that are currently undefined. | High | Medium | Low | Low | High |
| R3 | **Publish a strategic-assumptions register** (A1–A8, §1.3) as a living document with review triggers ("revisit A3 when a commercial SDA feed is added"). Cheap insurance against silent assumption decay. | Medium-high | Low | Low | Low | High |
| R4 | **State the AI-determinism doctrine** (A6) in one short ADR: all non-deterministic components live outside `engine/`, their outputs enter as ordered logged events via the session seam. It is already implicitly true (ADR-0021); making it explicit costs a page and prevents an invariant breach later. | High | Low | Low | Low | High |
| R5 | **Reconcile DOM-002/DOM-005 status with FS-201/FS-301** (§4.2.1) and fix GDS-00 §7's stale "build spec wins" language (§4.1.1) — two internal-consistency defects in the governance record itself. | Medium | Low | Low | Low | High |
| R6 | **Add a negative-training risk section to DOM-005** (validation framework) naming the known candidates: AI-Red exploitability, Δv terminality, fixed effect ontology, adjudication drift (§4.5). | High | Low | Low | Low | Medium-high |

### 6.2 Next Phase (current architecture, new capability)

| # | Recommendation | Value | Difficulty | Research effort | Risk | Confidence |
|---|---|---|---|---|---|---|
| R7 | **Close AI-Red fog-of-war parity (FC-02 / ADR-0024)** — the baseline's own acknowledged gap; prerequisite to every AI research line. | High | Medium | Low | Low | High |
| R8 | **Ship the headless Monte Carlo harness (IN-02/FC-14)** — the cheapest step-change in institutional research value available anywhere in this review. | High | Low-medium | Low | Low | High |
| R9 | **Commission GAP-07 (training transfer) research and let it shape DOM-002/DOM-005 before they harden.** The assessment tier should not be authored twice. | High | Low (commissioning) | High | Medium | High |
| R10 | **Build counterfactual AAR (IN-01) and belief-vs-truth analytics (IN-06)** as the flagship pedagogy features of the next release — both are near-pure leverage of existing invariants. | High | Medium | Low | Low | Medium-high |
| R11 | **Add the commercial SDA feed to the mock SSN** (already scoped, `FUTURE-WORK.md` §7) as the thin end of commercial integration (FC-10), plus one commercial-entanglement vignette (§4.3). | Medium-high | Low-medium | Medium (GAP-03) | Low | High |
| R12 | **Fund GAP-01 (space environment) research + an environment term in the effect/telemetry model**, enabling the attack-vs-environment vignette class and IN-03. | Medium-high | Medium | Medium | Low | Medium-high |

### 6.3 Future Release (new session-layer constructs / major content programs)

| # | Recommendation | Value | Difficulty | Research effort | Risk | Confidence |
|---|---|---|---|---|---|---|
| R13 | **Proliferated-constellation program (FC-06 + GAP-10):** research first, then engine-scale validation, aggregation constructs, and a proliferated vignette family. The flagship correction to W1. | High | High | Medium-high | Medium | Medium-high |
| R14 | **Coalition play (FC-09 + R316):** N-cell generalization with releasability filters and per-nation ROE. Highest-likelihood external demand (§4.7); distinctively Canadian value. | High | High | Medium | Medium | Medium-high |
| R15 | **Campaign container + time compression (FC-13)** — also unblocks reconstitution (FC-04), sub-threshold adversary behavior (§4.6), and cohort progression (IN-10). | Medium-high | Medium-high | Medium | Medium | Medium |
| R16 | **Persistent debris + conjunction wiring (FC-08 + GAP-02).** | Medium-high | Medium | Low-medium | Low | Medium-high |
| R17 | **Ground-segment-as-terrain cyber deepening (FC-11 + GAP-12).** | Medium-high | Medium | Medium | Medium | Medium |
| R18 | **Scenario generator (IN-07) + facilitator authoring UX (FS-108 promotion)** — attacks both content decay and the authoring gap (§4.2.2) together. | Medium-high | Medium | Low | Low | Medium-high |
| R19 | **Document the distributed-use security growth path** (threat model + token design sketch, per §4.2.3) *before* the first multi-site request, alongside a GAP-11 federation-compatibility study of the SessionAPI seam. | Medium | Low-medium | Medium | Low | High |

### 6.4 Long-Term Research (10–15-year positioning)

| # | Recommendation | Value | Difficulty | Research effort | Risk | Confidence |
|---|---|---|---|---|---|---|
| R20 | **Human-AI teaming laboratory program (FC-01 + FC-15 + R501/R503):** advisory planning aid, instrumented trust/reliance measurement, human-subjects studies (R411/R412). The strongest candidate for the platform's defining research contribution. | High | High | High | Medium | Medium-high |
| R21 | **AI-vs-AI doctrine exploration (IN-08):** self-play across doctrine presets for balance validation, degenerate-strategy discovery, and counterspace-doctrine research. | Medium-high | High | High | Medium-high | Medium |
| R22 | **Cislunar research line (FC-07 + GAP-04):** research-only for now; revisit implementation when allied cislunar SDA concepts mature. An area where a middle-power lab can lead the *training/experimentation* niche. | Medium (rising) | High | High | Medium | Medium |
| R23 | **Multi-domain effects abstraction (FC-12 + GAP-09 PNT cascades):** scoreboard-level terrestrial consequence, opening the joint-PME audience. | Medium-high | Medium-high | Medium | Medium | Medium |
| R24 | **Training-transfer longitudinal validation study** (the follow-through on R9): cohort tracking (IN-10) against operational-performance criteria — the evidence base an accreditor (§4.4) will eventually demand. | High | Medium | High | Medium | Medium-high |

### Reading the recommendation set as a strategy

The through-line: **spend the next phase converting existing engineering invariants into research
and pedagogy capability (R7–R12) while governance catches up (R1–R6); spend the following phase
correcting the three big scope assumptions — proliferation, coalition, commercial (R13, R14,
R11→FC-10); and anchor the long term on the human-AI teaming laboratory (R20), which no other
property of this platform's class can offer as credibly as a deterministic, belief-state-rigorous,
fully-replayable exercise engine.**

---

*End of report. Findings should be dispositioned through the project's own mechanisms (Open
Questions, ADRs, `ROADMAP.md`, `FUTURE-WORK.md`). No reviewed document was modified.*
