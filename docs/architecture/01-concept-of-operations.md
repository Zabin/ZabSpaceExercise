# GDS-01 — Concept of Operations

> **Document ID:** GDS-01
> **Version:** 1.3
> **Status:** ✅ Authored — merge gate closed (see "Merge gate" below)
> **Dependencies:** GDS-00
> **Referenced By:** GDS-02
> **Produces:** GDS-02
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`build-spec/01-context-and-scope.md`](../build-spec/01-context-and-scope.md),
> [`build-spec/04-nfr-milestones-and-risks.md`](../build-spec/04-nfr-milestones-and-risks.md) §11,
> [`build-spec/05-workflows-and-state-machines.md`](../build-spec/05-workflows-and-state-machines.md)
> §13–14, [`training/05-core-concepts.md`](../training/05-core-concepts.md),
> [`training/07-white-cell-facilitation.md`](../training/07-white-cell-facilitation.md),
> [`CLAUDE.md`](../../CLAUDE.md) ("LAN trust model"), [`FUTURE-WORK.md`](../FUTURE-WORK.md),
> [`reviews/architecture-review.md`](../reviews/architecture-review.md) (reconciled — see "Review
> reconciliation" below), [`adr/ADR-0024-ai-red-boundary-classification.md`](adr/ADR-0024-ai-red-boundary-classification.md),
> [`adr/ADR-0026-rlock-lan-scaling-ceiling.md`](adr/ADR-0026-rlock-lan-scaling-ceiling.md),
> [`adr/ADR-0029-assessment-scoring-workflow-ownership.md`](adr/ADR-0029-assessment-scoring-workflow-ownership.md)
> (Open Questions 2, 5, 6 resolution),
> [`research/encyclopedia/R313-maritime-operator-perspective.md`](../research/encyclopedia/R313-maritime-operator-perspective.md),
> [`research/encyclopedia/R314-land-operator-perspective.md`](../research/encyclopedia/R314-land-operator-perspective.md)
> (draft, citations unverified),
> [`research/encyclopedia/R315-air-operator-perspective.md`](../research/encyclopedia/R315-air-operator-perspective.md),
> [`research/encyclopedia/R316-joint-and-combined-operations.md`](../research/encyclopedia/R316-joint-and-combined-operations.md),
> [`research/encyclopedia/R317-space-operator-perspective.md`](../research/encyclopedia/R317-space-operator-perspective.md)
> (reconciled — see "Research integration (R313–R317)" below),
> [`reviews/r313-r317-gap-analysis.md`](../reviews/r313-r317-gap-analysis.md)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

Describe **how the system is used**, by whom, under what constraints, and across what lifecycle —
the operational picture that sits between GDS-00 (why the program exists) and GDS-02 (what external
systems and interfaces it touches). This document describes operations, not implementation: no
API shapes, schemas, or code-level detail belong here (those are GDS-07/GDS-09's job).

---

## 1. Purpose and mission of the system

SpaceSim exists to give space operators and trainees hands-on practice with **space control and
orbital warfare** under realistic constraints, in an unclassified setting where existing tools
either model orbits without wargaming (e.g. STK) or require classified infrastructure
(`build-spec/01` §1.1). Its mission, restated from GDS-00 §1 and `build-spec/01` §1.2–1.3, is to
teach the *texture* of real space operations — pass-gated command and telemetry, scarce SDA
sensors, finite fuel, doctrinally grounded counterspace effects — alongside the operational art of
contesting the domain, while training:

- that space operations are fundamentally **scheduling against orbital geometry**;
- **bus and payload operation** (state-of-health monitoring, pass planning, payload tasking) across
  mission types;
- the **SDA loop** — task scarce sensors, build and lose custody, characterize threats;
- weighing **counterspace effects** across the escalation ladder (deceive→disrupt→deny→degrade→
  destroy) with attention to reversibility, attribution, and debris;
- **active/passive defense and recovery**, including safe-mode diagnosis and the recovery chain.

The mechanics above are space's own instance of operational concepts that recur, under different
names, across every other domain's doctrine: a generic **decision cycle** (observe/classify →
decide → act → assess), **command by intent** rather than micromanagement, and **resilience**
under sustained contested conditions rather than a single fault event. The custody/track
confidence chain in §7 below is the simulator's one shipped instance of the decision-cycle
pattern; the plan-first invariant (§10) is this system's instance of command-by-intent. See
"Research integration (R313–R317)" below for the cross-domain grounding.

## 2. Intended users

Restated from `build-spec/01` §2 (the stakeholders table) and `training/07` §8:

| User | Role | What they do |
|---|---|---|
| **White Cell facilitator** (1–2 seats) | Exercise owner | Selects/builds the vignette, assigns seats, controls the clock, fires injects, adjudicates, runs the AAR |
| **Blue Cell operators** (up to 6) | Friendly bus/payload ops | Operate assigned Blue assets — SOH monitoring, pass planning, payload tasking, SDA |
| **Red Cell operators** (up to 6) | Adversary bus/payload ops, or AI-Red | Same operator capabilities as Blue, plus offensive counterspace effects; may instead be played by an AI-Red doctrine preset (`training/05` "Red doctrine & AAR") |
| **Observers** (up to 2) | Assessment/learning | Read-only view of god-view or a White-Cell-designated cell |
| **Maintainer** | Builds/evolves the tool | Not an exercise-time role; included for completeness per `build-spec/01` §2 |

A given human may hold multiple roles across an exercise via **hot-seat handoff** (§6 below); the
concurrency model is explicitly many-roles-few-humans, not one human per role (`build-spec/01` §2
"Concurrency model").

## 3. Stakeholders

Beyond the exercise-time users in §2, restated from GDS-00 §3 (`MSTR-001` §3):

| Stakeholder | Interest |
|---|---|
| CAF and allied space operator community | The training population the tool exists to serve (`build-spec/01` §1.1) |
| PME instructors / White Cell facilitators | Run exercises without a programming background (GDS-00 §5.1) |
| Researchers / assessment designers | Build measurement and validation on the simulator's data (GDS-00 §3) |
| Human maintainers | Keep the build-spec-vs-implementation contract honest |
| Future coding LLM agents | Extend the simulator from documentation rather than reverse-engineered code (GDS-00 §2–3) |

## 4. Operational environment

- **Deployment:** single-machine desktop/laptop, **offline-capable**, hot-seat multi-role play; or
  LAN-cooperative with one FastAPI server and N browser tabs/machines polling it
  (`build-spec/01` §1.4, §3.1; `CLAUDE.md` "Multiplayer workflow"). Not internet-public, not a
  dedicated-server architecture.
- **Hardware floor:** must run acceptably on a typical government laptop with integrated graphics
  — no discrete GPU assumed (`build-spec/01` §3.3 "Hardware floor").
- **Network posture:** runtime requires no network; the only network dependency is an *optional*
  Space-Track TLE import at scenario-build time, with manual TLE entry as a fallback
  (`build-spec/01` §3.1, Decision D2).
- **Classification:** all content is unclassified training material with fictional default assets;
  a classification banner (UNCLASSIFIED//EXERCISE or //TRAINING) is set at scenario build
  (`build-spec/01` §1.4, `build-spec/05` §13.1 step 2).
- **Trust model:** cooperative LAN, not adversarial — the cell selector is client-side trust with
  no per-cell authentication; fog-of-war is enforced for cell-scoped endpoints but several
  no-cell ground-truth endpoints (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`)
  deliberately expose ground truth without a cell binding. Documented as an explicit v1 trust
  boundary, not a defect (`CLAUDE.md` "LAN trust model").

## 5. High-level operational workflow

Restated from `build-spec/05` §13.1–13.2 and `training/07` §8:

1. **Set up.** White Cell launches the app, builds or loads a vignette (mission, assets via
   TLE/Keplerian entry, ground sites/sensors, `roles_needed`, tunable parameters and ROE dials,
   injects), validates it, and saves it.
2. **Assign seats.** White Cell maps human seats to roles/assets via a checkbox matrix, marking
   each role bus/payload/both.
3. **Start.** The wall clock begins at a chosen multiplier; the session becomes shareable as a URL
   (hot-seat on one browser, or LAN-cooperative across tabs/machines).
4. **Run.** White Cell watches the god-view (ground truth, both cells' belief, fleet SOH, timeline,
   event log); manages hot-seat handoff; controls time (raise/lower multiplier, pause, rewind);
   fires injects; re-tunes live parameters; adjudicates manually (no auto-scoring in v1).
   Operators plan commands and task sensors against access windows, monitor SOH, diagnose
   attacks from telemetry signatures (never a labelled cause — `training/05` "Diagnosing attacks
   from telemetry"), and weigh counterspace effects.
5. **End.** The exercise ends with the event log written; White Cell can replay it read-only,
   scrub to any decision, and compare two branches in the After-Action Review
   (`training/05` "Red doctrine & After-Action Review").

## 6. Typical user scenarios

Restated from `build-spec/05` §13.3–13.5:

- **Blue bus operator:** un-blanks into an assigned bus role, reads the fleet SOH rollup, drills
  into a satellite's subsystem telemetry, sees "next contact in 00:06:12 via STATION-A," queues
  pass commands (desaturate wheels, manage battery before eclipse, slew attitude), and — if the
  satellite has safed — diagnoses from stored telemetry and queues the multi-step recovery
  procedure, watching for re-safe if the root cause persists.
- **Blue/Red payload operator (by mission type):** SATCOM operators re-plan frequency/beam or
  shift customers when a carrier degrades; ISR operators build a collection schedule against
  target passes and manage storage/downlink backlog; SIGINT/SDA operators task sensors
  (search/track/characterize) under single-task contention and cue radar→optical; space-control
  operators select a target (requiring a weapons-quality track), choose an effect on the five D's,
  and time it inside an engagement/proximity window.
- **Red offensive sequence (representative, Vignette 1):** Red EW pre-plans a downlink jam over
  the landing area for the landing window; Red Orbital tasks SDA to maintain custody of Blue ISR
  satellites; Red cyber attempts a safe-mode inducement on a Blue ISR satellite; Red weighs
  escalation to kinetic effects (default off), aware it spawns debris and a political-consequence
  inject.
- **White Cell mid-exercise:** announces a hot-seat handoff, raises Red EW intensity live via a
  tunable parameter, fires a scheduled inject (e.g. a severe space-weather advisory), and narrates
  consequences for a physically legal but tactically unwise action rather than blocking it
  (`build-spec/01` §3.3 "Error handling").
- **Cross-domain dependency (conceptual, not implemented):** every other military domain's
  doctrine treats space support (PNT, SATCOM, ISR, missile warning) as a precondition for its own
  operations, and a joint force depends on synchronized effects across domains rather than any one
  domain acting alone (`R316` §3.1, §3.6). The simulator models exactly one domain (space) and does
  not implement land/air/maritime components; this scenario is included to illustrate the kind of
  joint dependency a future multi-domain extension would need to represent explicitly, not to claim
  the system already does so.

## 7. Exercise lifecycle

The session state machine, restated verbatim from `build-spec/05` §14.4:

```
SETUP ─▶ ASSIGNED(roles) ─▶ RUNNING ⇄ PAUSED ─▶ ENDED(log written)
RUNNING ─(rewind)─▶ replays to earlier sim_time, continues  (deterministic)
```

Layered onto this, three further state machines an operator/facilitator experiences during a run
(`build-spec/05` §14.1–14.3):

- **Planned Activity** (command or collection): `DRAFT → PLANNED → ACTIVE → EXECUTED` (commands)
  or `→ REPORTED` (collection); cancellable by the operator at any point before execution;
  re-validated at execute time against ownership/window/resources/ROE/track.
- **Bus mode / safe mode:** `NOMINAL` → (fault/power/attitude/thermal/cyber/EW/bus-stress,
  subject to a susceptibility check) → `SAFE_MODE` (payload off, autonomy points to sun, awaits
  ground) → (multi-pass recovery chain, per-step success) → `NOMINAL`, or re-safe if the root
  cause persists.
- **Custody / track confidence:** `UNKNOWN` → (detection) → `TRACKED(low confidence)` →
  (characterization) → `CHARACTERIZED`; confidence decays without observation and may fall below
  the weapons-quality gate (`confidence ≥ threshold AND characterized`).

Because the engine is deterministic on `(initial_state, ordered eventlog, seed)`, rewind/undo and
branch-from-rewind are byte-exact at any point in this lifecycle (GDS-00 §1, item 3; `CLAUDE.md`
invariant 1).

## 8. Major operational modes

- **Hot-seat (single browser/machine):** White loads a vignette and presses Start, then uses cell
  buttons to switch seats between turns; the outgoing operator's screen is blanked during handoff
  (`training/07` §8 "Hot-seat vs. LAN cooperative"; `build-spec/01` §2 "Concurrency model").
- **LAN cooperative (multi-tab / multi-machine):** White starts the session and shares the URL
  (`…/#sess-N`); each player opens it on their own tab/machine and picks a cell. The
  server-authoritative clock advances exactly once regardless of tab count; only the White tab
  controls time (`training/07` §8).
- **Fidelity/fog modes (per-vignette tunable):** `ops_fidelity` (`tactical` / `realistic` /
  `full_ttc`) controls how much subsystem detail is exposed; `fog_of_war` and
  `safe_mode_susceptibility` are further tunable dials White Cell sets at load time
  (`training/07` §8 "Parameters (dials)").
- **Replay / AAR mode:** a read-only mode entered after (or during, via scrub) an exercise — never
  disturbs the live session; supports branch-compare to show how a decision changed the outcome
  (`training/05` "Red doctrine & After-Action Review").
- **AI-Red mode:** Red may be played by a doctrine-flavored AI preset (`russia_ew_first`,
  `china_integrated`, `generic`) instead of human Red operators (`training/05` same section).

Both the hot-seat and LAN-cooperative modes above are served by the same underlying Session object
(GDS-04 §1.14) — they differ only in how many browser clients are connected to it, not in the
session model itself (clarified per the architecture review — see "Review reconciliation" below).

## 9. External systems

- **Space-Track.org** — optional TLE import at scenario-build time only; the runtime never
  requires network access. Manual TLE entry or Keplerian-element synthesis is the fallback if
  Space-Track is unavailable or its auth changes (`build-spec/01` Decision D2;
  `build-spec/04` §11 risk row "Space-Track unavailable or auth changes").
- **Skyfield / sgp4** — the propagation libraries behind real-satellite TLE force-add
  (`training/05` "Adding real satellites by TLE"); an external dependency, not a live external
  system, but worth naming because TLE-sourced orbits are validated against it
  (`build-spec/04` §11 risk row "Moderate-fidelity orbits look 'wrong'").
- No other live external system is in scope for v1 — no identity provider, no telemetry/export
  service, no third-party scoring system. (Confirmed by reviewing `build-spec/01` §3.1–3.2 and
  `CLAUDE.md`; nothing else is referenced as an external dependency.)

## 10. Operational constraints

Restated from `build-spec/01` §3.1, §3.3, and GDS-00 §6:

- **Sizing guideline (not an engine cap):** ~24 satellites is a soft sizing guideline for typical
  White-Cell facilitator hardware; user-authored vignettes may scale beyond it on capable hosts.
  Constellations are capped at 3 satellites each, individually operated/monitored. The
  clock-lag watchdog (`SessionManager._record_catch_up_lag`) is the operational signal that a
  scenario has outgrown its host.
- **Single point of time control:** White Cell alone owns pause/resume/rewind/branch; operators
  never control the clock.
- **Plan-first commanding:** operators plan; they never act instantly on perfect knowledge —
  commands execute at the next valid access window via ground uplink, ISL relay, or stored
  program.
- **Manual adjudication:** v1 has no automated scoring; White Cell adjudicates and narrates
  consequences by design.
- **Error-handling posture:** invalid scenario data fails loudly at load with a precise error;
  in-play illegal actions are blocked with an explanation; physically legal but tactically unwise
  actions are allowed to run and produce their natural consequence (a deliberate teaching
  feature, not a missing guardrail).
- **Cooperative-LAN trust only** — see §4 above; not hardened against an adversarial participant.

## 11. Assumptions

Carried from `build-spec/01` §3.3 ("Assumptions made for round-4 questions," White-Cell
overridable in scenario data) and GDS-00 §6:

- RIC view origin defaults to the seat's first assigned asset, with a one-click re-origin option
  for relative/RPO geometry.
- v1 provides tooltips and a "why can't I?" affordance on disabled controls plus a one-screen role
  cheat-sheet; no full interactive tutorial is assumed — White Cell briefs operators directly
  (though the shipped product has since added a guided training-basics vignette and in-app
  tutorial panel beyond this original v1 assumption — see `CLAUDE.md` "Code map," `training/04`).
- Dark "ops-floor" theme by default, light theme available; NATO/APP-6-style symbology assumed
  legible to the target audience without further explanation.
- The orbital fidelity model (Keplerian + J2, moderate fidelity) is assumed sufficient for the
  training objectives in §1; a higher-fidelity model is a deferred upgrade behind existing
  interfaces, not a v1 requirement.
- Cooperative players are assumed not to exploit the LAN trust model described in §4/§10.

## 12. Risks

Restated from `build-spec/04` §11 (full mitigation table there); risks most relevant to the
operational picture, not the engineering one:

| Risk | Operational impact | Mitigation |
|---|---|---|
| Hot-seat fog leaks (one role sees another's private data) | Training value destroyed — the core "operate on belief, not ground truth" lesson breaks | Fog enforced in the engine `CellView`/`SessionAPI`, not the UI; tested at the API boundary |
| Safe-mode mechanic dominates play | Skews training away from the intended balance of lessons | Tunable dials + detection/recovery counterplay; `realistic` is the default `ops_fidelity` |
| Moderate-fidelity orbits look "wrong" to STK-savvy users | Credibility loss with experienced operators | Validated against Skyfield; fidelity documented explicitly, not hidden |
| Space-Track unavailable or auth changes | Can't seed real TLEs for a session | Bundled snapshot + manual entry + Keplerian synthesis fallback; runtime never depends on network |
| Wall-clock + heavy propagation stalls the UI | Sluggish exercise, breaks immersion at high time multipliers | Off-UI-thread propagation; window caching/precompute |
| Adversarial LAN participant reads another cell's belief state | Breaks the fog-of-war training premise on an uncooperative LAN | Documented v1 trust boundary, not solved — deploy only on trusted cooperative LANs (`CLAUDE.md`) |

## 13. Open Questions

The encyclopedia and existing corpus do not settle the following; flagged here rather than
invented:

1. **No dedicated ConOps-equivalent existed anywhere in the corpus before this document.** The
   merge-gate search (below) confirms `training/` and `build-spec/01` carry the relevant
   operational material in scattered form, but no single document previously stated the full
   operational picture (purpose/users/stakeholders/environment/workflow/lifecycle/modes/external
   systems/constraints/assumptions/risks) in one place. This document is therefore net-new
   synthesis, not a merge of an existing ConOps.
2. ~~Sizing/performance ceiling for LAN-cooperative play~~ — **resolved by ADR-0026.** The stated
   ceiling is the existing `build-spec/01` §2 concurrency model (≤16 total seats: 1–2 White, ≤6
   Blue, ≤6 Red, ≤2 Observers) — the project owner adopted the already-documented sizing as the
   supported ceiling rather than commissioning a new load test. See
   `architecture/adr/ADR-0026-rlock-lan-scaling-ceiling.md`.
3. **Observer role granularity** — `build-spec/01` §2 states observers get "a designated cell view,
   White-Cell-set," but no document describes whether an observer can be reassigned mid-exercise
   or is fixed at session start. Left open.
4. **AI-Red doctrine preset selection criteria** — `training/05` names three presets
   (`russia_ew_first`, `china_integrated`, `generic`) but no document in the operational corpus
   states guidance for *which* preset a White Cell facilitator should choose for a given training
   objective. This may belong in `docs/training/` rather than here; flagged, not resolved.
5. ~~Assessment/scoring stakeholder workflow~~ — **resolved by ADR-0029.** Raw AAR/event-log access
   (replay/scrub/branch-compare, plus the existing CSV/JSON export at
   `/api/sessions/{sid}/aar/export.{csv,json}`) is deemed sufficient for the "researchers /
   assessment designers" stakeholder; researchers do their own downstream analysis externally on
   this exported data. No new dedicated export/analysis interface or owning subsystem is
   introduced, and the question is not scoped to a `docs/domains/` framework. See
   `architecture/adr/ADR-0029-assessment-scoring-workflow-ownership.md`.
6. ~~AI-Red's epistemic parity with human cells.~~ — **resolved by ADR-0024.** AI-Red's current
   ground-truth access (`redai.py` reads `world` directly rather than through a fog-of-war-filtered
   `CellView`) is recorded as a known gap, not accepted as deliberate design — filtered-view parity
   with human cells is required as future work, tracked in `FUTURE-WORK.md` §1 "AI-Red fog-of-war
   parity." AI-Red's permanently-internal boundary classification (Open Question 2 elsewhere in the
   ladder) is locked in separately and is not affected by this gap. See
   `architecture/adr/ADR-0024-ai-red-boundary-classification.md`. The space domain's own historical
   arc independently names autonomy/human-machine teaming as the live frontier issue
   (`R317` §3.7–3.8), corroborating that this gap is doctrinally significant, not just an
   engineering nuisance.
7. **Command-relationship layering (new).** Every other domain's research treats internal command
   relationships (OPCON/TACON-equivalent: who has full command vs. who can only direct execution of
   an assigned task) as load-bearing (`R313` §3.2/§3.7, `R314` §3.1, `R315` §3.8, `R316` §3.1). The
   simulator's flat single-Blue-cell/single-Red-cell model has no such concept. `R316` §3.1
   explicitly cautions against treating the existing flat model as a doctrinal claim that real
   joint structure is flat. Left open — see the forward-looking sketch in `GDS-04` §3, not resolved
   here.
8. **Resilience under sustained denial (new).** The existing safe-mode mechanic (§7 above) models a
   single fault event and its recovery chain. Doctrine across land, air, maritime, and space domains
   treats sustained, contested-environment degradation (comms-denied mission command, persistent EW,
   cyber-EW inseparability per the 2022 Viasat KA-SAT precedent) as a distinct, harder problem from a
   single fault (`R313` §3.7, `R314` §3.5, `R315` §3.17/§3.19, `R317` §3.6). Whether/how the
   simulator should eventually model sustained multi-front degradation rather than discrete fault
   events is a design decision, not a documentation fix — left open.

---

## Review reconciliation (architecture-review.md)

In response to `docs/reviews/architecture-review.md` (a principal-architect review of GDS-01–04),
the following documentation-only clarifications were made. No operational behavior, requirement,
or feature changed — see [`reviews/architecture-review-changelog.md`](../reviews/architecture-review-changelog.md)
for the consolidated, cross-document changelog.

- §7 — capitalized "Planned Activity" for consistency with its formal entity name in GDS-04 §1.7
  (terminology fix, no content change).
- §8 — added a clarifying note that hot-seat and LAN-cooperative modes share one Session object
  (review §3 finding 3).
- §13 — Open Question 5 (assessment/scoring) appended with confirmation that the gap is
  architecture-wide, not ConOps-specific (review §1 finding 1, §7 findings 1–2).
- §13 — added Open Question 6, AI-Red epistemic parity with human cells (review §8 finding 3, new).
- Metadata — added a cross-reference to the architecture review; version bumped 1.0 → 1.1.

## Research integration (R313–R317)

Five operator-perspective research documents
([`R313`](../research/encyclopedia/R313-maritime-operator-perspective.md) Maritime,
[`R314`](../research/encyclopedia/R314-land-operator-perspective.md) Land (draft, citations
unverified),
[`R315`](../research/encyclopedia/R315-air-operator-perspective.md) Air,
[`R316`](../research/encyclopedia/R316-joint-and-combined-operations.md) Joint and Combined
Operations, and
[`R317`](../research/encyclopedia/R317-space-operator-perspective.md) Space Operator Perspective —
Historical Evolution) were synthesized against this document per
[`reviews/r313-r317-gap-analysis.md`](../reviews/r313-r317-gap-analysis.md). **Scope discipline:**
every change below is additive — naming an existing mechanic's doctrinal analog, adding an
illustrative (not implemented) scenario, or adding a genuinely open question. No requirement,
mechanic, or external-system claim changed.

- §1 — added a paragraph naming the cross-domain decision-cycle/command-by-intent/resilience
  concepts the existing mechanics already instantiate, citing R313–R317 (gap-analysis findings C1–C7).
- §6 — added a cross-domain-dependency scenario, explicitly marked as illustrative/conceptual since
  the simulator implements only the space domain (R316 §3.1/§3.6; gap-analysis finding 1.2).
- §13 — added Open Question 7 (command-relationship layering, R313/R314/R315/R316; gap-analysis
  finding 1.3) and Open Question 8 (resilience under sustained denial, R313/R314/R315/R317;
  gap-analysis finding C6). Both left genuinely open — resolving either is a design decision.
- §13 Open Question 6 — appended a corroborating citation to R317's autonomy/human-machine-teaming
  framing (gap-analysis finding C7); the existing ADR-0024 resolution is unchanged.
- Metadata — added cross-references to R313–R317 and the new gap-analysis document; version bumped
  1.2 → 1.3. Status remains `✅ Authored — merge gate closed`; this update does not reopen the gate
  recorded below, it amends the document in place under explicit instruction, consistent with the
  precedent set by the prior architecture-review reconciliation.

## Merge gate (closed)

- [x] **Searched `docs/training/` and `docs/build-spec/01-context-and-scope.md`** for existing
  concept-of-operations material (user roles, session flow, hot-seat/LAN operating model) before
  concluding there was nothing to merge, per the gate's instruction. Found substantial relevant
  material, scattered across multiple documents rather than consolidated:
  - `build-spec/01-context-and-scope.md` §1–3 (purpose, stakeholders, scope, assumptions) — the
    single richest source, absorbed into §1–4, §10–11 above.
  - `build-spec/04-nfr-milestones-and-risks.md` §11 (risk table) — absorbed into §12 above.
  - `build-spec/05-workflows-and-state-machines.md` §13–14 (operator workflow walkthroughs, state
    machines) — absorbed into §5–7 above.
  - `training/05-core-concepts.md` and `training/07-white-cell-facilitation.md` — absorbed into
    §6 (scenarios) and §8 (operational modes) above.
- [x] **Recorded what was found, with citations** — see the inline citations throughout §1–12
  above; every section traces to a specific existing-document section rather than asserting
  uncited claims.
- [x] **Decision recorded:** none of the source documents (`build-spec/01`, `build-spec/04`,
  `build-spec/05`, `training/05`, `training/07`) becomes a pointer to this document or is
  otherwise demoted. **All five stay independently authoritative** for their own audiences
  (`build-spec/` is binding-spec detail for implementers; `training/` is task-level guidance for
  facilitators/operators). `GDS-01` is a **synthesis layer above them**, consolidating the
  operational picture that was previously only inferable by reading all five documents together —
  its value is consolidation and explicit Open Questions, not replacement. This mirrors the
  resolution already recorded for `GDS-00`/`MSTR-001`.
- [x] No contradiction was found between any of the five source documents during this synthesis;
  where a source's framing has since been superseded by shipped functionality (e.g. the v1
  "no full interactive tutorial" assumption, since followed by an in-app tutorial panel), the gap
  is flagged inline (§11) rather than silently corrected in the source document.

## Next

`GDS-02` (System Context) may now begin.
