# Feature Catalog

> **Namespacing note (read first):** This repository already has a `docs/features/` directory
> populated with full **Feature Specification** documents (`FS-101`…`FS-301`, governed by
> `MSTR-005`'s Domain → Research → ADS → **FS-xxx** → IMP-xxx → code chain — see
> `docs/features/feature-index.md`). This catalog is a **different, upstream artifact**: a
> planning-grain decomposition of the approved requirements baseline, produced by the
> `05-feature-decomposition` skill, which sits *between* `docs/requirements/` and the point where a
> `FS-xxx` document would be written. To avoid colliding with the existing `FS-xxx` ID space and
> document type, this catalog's rows use the prefix **`FEAT-xxxx`** and live under
> `docs/feature-planning/` (not `docs/features/`). A `FEAT-xxxx` row is a summary the project would
> expand into a full `FS-xxx` specification later — it is not itself a specification. See
> `05-feature-review.md`'s mapping note for the full disposition, including how the 11 existing
> `FS-1xx`/`FS-2xx`/`FS-3xx` documents map onto this catalog's `FEAT-xxxx` rows.
>
> **Amended 2026-10-03** (`05-feature-decomposition`, targeting six new FR leaves baselined this
> run for `BL-0107`/`BL-0109`/`BL-0111`/`BL-0122`/`BL-0079`): added **FEAT-1600** (Sensor
> Modality-Specific Access & Effectiveness Models, owning `FR-1610`-`FR-1670`), **FEAT-7400**
> (State-Vector/Ephemeris & TLE Export, owning `FR-7410`-`FR-7440`), and **FEAT-8200** (Live
> RIC-Frame Relative-Motion View & CATS Overlay, owning `FR-8210`/`FR-8220`, new parent `FR-8200`);
> extended the existing **FEAT-4400** (+`FR-4450`) and **FEAT-4600** (+`FR-4620`). This run's scope
> was explicitly the six new leaves only — it does **not** re-baseline this catalog against every
> FR added to the requirements document since this catalog's original 49-FR pass (the Must-tier,
> Should-tier, FS-117, and `FR-7430` intake batches between the original pass and this run remain
> **not yet decomposed** outside the three leaves — `FR-1610`-`FR-1660`, `FR-7410`-`FR-7430` — that
> rode into `FEAT-1600`/`FEAT-7400` as natural siblings of this run's own new leaves). See
> `05-feature-review.md`'s Finding log for the full disposition of this partial-staleness gap.
>
> **Amended 2026-10-17 — full inventory sweep** (`05-feature-decomposition`, run #151, `BL-0153`,
> with `BL-0238`/`BL-0245` riding): Step 0 re-run against the whole current baseline. The 37 FR and
> 5 NFR leaves no Feature owned were assigned — 28 into existing Features by parentage (FEAT-1200,
> 1300, 1400, 2300, 3400, 4200, 4400, 5100, 5200, 5300, 7300), the rest into **four new Features**:
> **FEAT-5400** (external vignette directories), **FEAT-5500** (save-as-scenario), and, under new
> Epic **EP-11000**, **FEAT-11100** (manuals) and **FEAT-11300** (learning path). `FR-1460`/`FR-1470`
> (salvo ammunition bound; jammer power rating, ADR-0037) join FEAT-1400. Every baselined FR/NFR is
> now owned exactly once. Each added leaf carries a *(sweep 2026-10-17, run #151)* tag.
>
> **Amended 2026-10-23 — GDS ladder alignment sweep** (`05-feature-decomposition`, run #212, a
> delta over the 21 leaves `04` added in run #211 — see
> [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md)).
> Fourteen leaves join existing Features by subject: FEAT-1100 (+`NFR-1610`, `NFR-2410`), FEAT-1200
> (+`NFR-2810`), FEAT-4300 (+`FR-4320`), FEAT-6100 (+`NFR-3710`), FEAT-7200 (+`FR-7230`), FEAT-8100
> (+`NFR-3010`–`NFR-3050`), FEAT-9100 (+`NFR-3060`). The mechanical check also found `FR-1480`
> (a fired salvo is charged hit or miss, IP-1321) owned by no Feature; it joins FEAT-1400 beside
> `FR-1460`. The remaining nine — test traceability, the
> browser suite and documentation integrity — have no product-feature home, so they form new Epic
> **EP-12000** with **FEAT-12100**, **FEAT-12200** and **FEAT-12300**. Each added leaf carries a
> *(sweep 2026-10-23, run #212)* tag. GDS-06–GDS-10 are now authored, so the architecture inputs
> listed below are extended by `docs/architecture/06`–`10`.

Source baseline read in full: `docs/requirements/01-functional-requirements.md` (49 baselined FR
leaves + 18 Candidate Requirements CR-01–CR-18), `docs/requirements/02-non-functional-requirements.md`
(23 baselined NFR leaves + 7 Candidate CNFR-01–CNFR-07), `docs/requirements/03-requirements-
traceability-matrix.md`, `docs/architecture/00`–`05` (GDS-00–05, all merge-gate-closed), the ADR
index (`ADR-0001`–`ADR-0031`, all Accepted), `docs/design/05-interface-control-document.md` (ICD,
`INT-0001`–`INT-0016`), `docs/domains/DOM-001`–`009`, and `docs/reviews/strategic-review-2026-07.md`
(Future Concepts FC-01–FC-15, Gap Analysis GAP-01–GAP-13).

**Only the 49 baselined FR + 23 baselined NFR leaves are decomposed into Features below** — per
this skill's own constraint, Candidate Requirements (CR-01–18, CNFR-01–07) and the strategic
review's FC-01–15/GAP-01–13 are explicitly *not baselined/approved*, so they are not grouped into
Features here. Their disposition (why they don't yet qualify, and what closes that) is reported in
`05-feature-review.md`, not resolved by inventing Features for them.

Architecture Component key (ICD §4, C1–C12): **C1** Simulation Engine · **C2** Session/Application
Layer · **C3** Mock SSN · **C4** Operator Console · **C5** Content & Data · **C6** White Cell ·
**C7** Blue Cell · **C8** Red Cell (incl. AI-Red) · **C9** Observer · **C10** Space-Track.org
(external) · **C11** Local filesystem (external) · **C12** Browser client.

---

## Epic EP-1000 — Simulation Engine Core & Determinism

### FEAT-1100 — Deterministic, Sub-Stepped Simulation Clock

| Field | Content |
|---|---|
| **Feature ID** | FEAT-1100 |
| **Title** | Deterministic, Sub-Stepped Simulation Clock |
| **Purpose** | Guarantee that one authoritative clock, advanced without skipping scheduled events, produces byte-identical replay from `(state, eventlog, seed)`. |
| **Description** | Maintains exactly one authoritative simulated-UTC clock per session; advances state strictly as a function of current time, state, and the ordered event log; sub-steps to the next scheduled event rather than a naive large step; guarantees byte-identical reconstruction on replay. |
| **Scope** | The clock/scheduler mechanism and the determinism guarantee over it. Does *not* cover who is authorized to command the clock (FEAT-4300) or the event log's own storage format (FEAT-7100, a dependency). |
| **Included Requirements** | FR-1110, FR-1120, FR-1130, NFR-1500, NFR-1700, NFR-1900, NFR-2400, NFR-2800, NFR-1610, NFR-2410 *(sweep 2026-10-23, run #212)* |
| **Excluded Requirements** | FR-4310 (clock *control authority* — FEAT-4300); FR-7110 (event log *storage* — FEAT-7100, a dependency of this Feature, not part of it) |
| **Dependencies** | FEAT-7100 (replay requires an ordered event log to replay against); FEAT-5300 (`NFR-1610` builds on `NFR-1600`, robustness to invalid input) *(sweep 2026-10-23)* |
| **Dependent Features** | FEAT-4300, FEAT-4400, FEAT-6300, FEAT-10200; FEAT-1200, FEAT-3400 *(sweep 2026-10-17)*; FEAT-8100, FEAT-12100 *(sweep 2026-10-23)* |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008, INT-0014 |
| **Related ADRs** | ADR-0016, ADR-0002, ADR-0006 |
| **User Value** | Every rewind, undo, branch-compare, and AAR replay a facilitator or trainee uses depends on this being exact — it is invisible when it works and catastrophic (silently wrong lessons) when it doesn't. |
| **Technical Value** | The single load-bearing invariant the rest of the engine is built on (`CLAUDE.md` invariant 1); every other engine Feature assumes it holds. |
| **Complexity** | High — sub-stepped scheduling and byte-identical replay across all engine modules is a whole-system property, not a local one. |
| **Risk** | Any future engine change (new effect type, new subsystem) that reads wall-clock time or unseeded randomness silently breaks this; the import-guard test is the only automated defense. |
| **Suggested Verification Strategy** | The permanent determinism property test (already the project's Phase-1 gate); scheduler tests confirming no scheduled event is skipped at high time multipliers. |
| **Open Questions** | A found circular citation between this Feature's FR-1110 ("Dependencies: FR-4300") and FEAT-4300's FR-4310 ("Dependencies: FR-1110") — resolved for this graph by treating FR-1110→FR-4300 as an authority/access-control constraint, not a build-order dependency (see `04-feature-dependency-graph.md`); the requirements owner may want to tighten FR-1110's Dependencies field to avoid the appearance of a cycle. Same pattern with FR-7110's back-reference to FR-1120 (see `04`). |

### FEAT-1200 — Orbital Propagation & Access-Window Geometry

| Field | Content |
|---|---|
| **Feature ID** | FEAT-1200 |
| **Title** | Orbital Propagation & Access-Window Geometry |
| **Purpose** | Compute where every asset is and when any of the six access channels (command uplink, telemetry downlink, sensor observation, jam footprint, weapon engagement, RPO proximity) is geometrically possible. |
| **Description** | Propagates each asset's orbit (Keplerian+J2 for fictional assets, SGP4-class for TLE-sourced real satellites) behind a common `Propagator` interface, and computes `AccessWindow` intervals for all six channels from that geometry. |
| **Scope** | Orbit propagation and access-window computation only. Does not cover maneuver application (FEAT-1300, a dependent) or effect resolution once a window is open (FEAT-1400, a dependent). |
| **Included Requirements** | FR-1210, FR-1220, FR-1230 *(sweep 2026-10-17, run #151)*, NFR-2100, NFR-1300, NFR-2810 *(sweep 2026-10-23, run #212)* |
| **Excluded Requirements** | FR-4440 (space-weather anomaly-rate scaling — FEAT-4400, which owns the anomaly inject it scales; it consumes FR-1230's index series) |
| **Dependencies** | FEAT-1100 *(FR-1230: index-driven drag is computed from simulated time, FR-1120)* |
| **Dependent Features** | FEAT-1300, FEAT-1400, FEAT-1500, FEAT-1600, FEAT-2300, FEAT-3100, FEAT-3200, FEAT-5200, FEAT-8200; FEAT-4400 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008 |
| **Related ADRs** | ADR-0009, ADR-0011, ADR-0019 |
| **User Value** | "You can only command, observe, or attack when access windows permit" is the game's central constraint — every operator decision is scheduling against this Feature's output. |
| **Technical Value** | The most heavily depended-on Feature in the catalog (7 direct dependents) — it is the geometric substrate nearly everything else reads. |
| **Complexity** | High — dual-fidelity propagation behind one seam, six independently-computed channel types, caching/invalidation as sim time advances. |
| **Risk** | Moderate-fidelity is a deliberate scope choice (ADR-0009), but any future high-fidelity swap must not change this Feature's output contract for its seven dependents. |
| **Suggested Verification Strategy** | Reference-SGP4 ground-track comparison within documented tolerance; access-window start/end times checked against known pass geometry for each of the six channels. |
| **Open Questions** | None. |

### FEAT-1300 — Impulsive Maneuver & Δv Budget Accounting

| Field | Content |
|---|---|
| **Feature ID** | FEAT-1300 |
| **Title** | Impulsive Maneuver & Δv Budget Accounting |
| **Purpose** | Let an asset change its orbit while enforcing a hard, non-negative delta-v budget. |
| **Description** | Applies impulsive maneuvers (six entry modes) that edit orbital elements and decrement `delta_v_ms`; rejects any maneuver that would drive the budget negative, at validation time, before any state change. |
| **Scope** | Maneuver math and budget enforcement only; does not cover the plan-first scheduling wrapper around a maneuver order (FEAT-3100) or logistics/refueling (out of baseline scope — see CR-15/FC-05 in `05-feature-review.md`). |
| **Included Requirements** | FR-1310, FR-1320 *(sweep 2026-10-17, run #151)* |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-1200; FEAT-3100 and FEAT-7100 *(FR-1320: purpose tags are entered at plan time and the ledger is read from the event log)* |
| **Dependent Features** | FEAT-3400 |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008 |
| **Related ADRs** | None directly (restates a GDS-04 validation rule) |
| **User Value** | Δv is described as "the operator's hardest constraint" — this Feature is the entire fuel-scarcity lesson. |
| **Technical Value** | A finite, non-renewable resource model that other systems (custody, effects) can assume is enforced rather than re-checking themselves. |
| **Complexity** | Medium — six maneuver entry modes (`engine/maneuver.py`) share one budget-enforcement rule. |
| **Risk** | Low technical risk; the strategic review (§1.5) flags a *pedagogical* risk that Δv-as-terminal may need to be untaught once servicing/refueling doctrine matures — noted as a future concept, not a defect in this Feature. |
| **Suggested Verification Strategy** | Given `delta_v_ms = X`, a maneuver costing `> X` is rejected pre-state-change; a maneuver costing `≤ X` leaves `delta_v_ms = X - cost` exactly. |
| **Open Questions** | None within baseline scope. |

### FEAT-1400 — Five-D's Counterspace Effect Resolution

| Field | Content |
|---|---|
| **Feature ID** | FEAT-1400 |
| **Title** | Five-D's Counterspace Effect Resolution |
| **Purpose** | Resolve a counterspace action to a doctrinally-grounded outcome (deceive/disrupt/deny/degrade/destroy) with reversibility, debris, attribution, and resource side effects tracked explicitly. |
| **Description** | Resolves an `EffectInstance` in one of five categories (direct-ascent, co-orbital, EW, DE, cyber) to an `EffectOutcome`; cyber is the one category resolved outside the access-window gate, instead gated on access vector and target cyber posture/vulnerabilities. |
| **Scope** | Effect resolution and its side-effect bookkeeping. Does not cover the custody/weapons-quality precondition an engagement-intent effect must satisfy (FEAT-1500, a peer dependency reached via order validation, not this Feature directly). *(Sweep 2026-10-17:)* now also owns the resource-side-effect bounds (`FR-1460` ammunition, `FR-1470` jammer power rating, per ADR-0037), the debris-persistence estimate (`FR-1430`), delivery-path jamming (`FR-1440`) and per-class detectability (`FR-1450`) — all `FR-1400` children by parentage. |
| **Included Requirements** | FR-1410, FR-1420, FR-1430, FR-1440, FR-1450, FR-1460, FR-1470 *(sweep 2026-10-17, run #151)*, FR-1480 *(sweep 2026-10-23, run #212 — missed by the run #151 sweep)* |
| **Excluded Requirements** | FR-1310 (Δv bound — FEAT-1300); FR-3420 (ROE gate on engage/cyber — FEAT-3400) |
| **Dependencies** | FEAT-1200; FEAT-3100 and FEAT-3400 *(FR-1440: uplink/crosslink jamming acts on the delivery path and the execute-time check)* |
| **Dependent Features** | None |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008 |
| **Related ADRs** | ADR-0012, ADR-0037 |
| **User Value** | The five-D's-plus-cyber-exception taxonomy *is* the simulator's doctrinal model of counterspace operations — this Feature is what makes an order mean something doctrinally, not just numerically. |
| **Technical Value** | A single resolution seam (`EffectResolver`) that every effect category routes through, keeping the five-D ontology consistent. |
| **Complexity** | High — five categories, each with its own sub-model (`jam.py`, `engage.py`, `cyber.py`, `isr.py`), unified behind one outcome contract. |
| **Risk** | The strategic review (A2) flags the fixed five-D ontology itself as a hidden assumption that doctrine may reframe; that is a requirements-tier question, out of this Feature's scope to resolve. |
| **Suggested Verification Strategy** | Given a kinetic template with `debris_risk` set, a successful resolution always produces a `spawn_debris` side effect; given a reversible template, never. Given no open window, a cyber effect is still resolvable. |
| **Open Questions** | `FR-1460`/`FR-1470` are unimplemented (RTM `UNASSIGNED`) and have no FS yet — `06` next (FS-105 or a new remediation FS). Both touch the same success-path consumption step and may share one package. |

### FEAT-1500 — Custody, Track Confidence & Weapons-Quality Gate

| Field | Content |
|---|---|
| **Feature ID** | FEAT-1500 |
| **Title** | Custody, Track Confidence & Weapons-Quality Gate |
| **Purpose** | Model custody as decaying confidence that must clear a threshold-plus-characterization bar before an engagement-intent action is permitted. |
| **Description** | Decays each held `Track`'s confidence with time since last observation, resets it on new observation, and gates engagement-intent actions on confidence ≥ threshold AND `characterized = true`, rejecting otherwise with a reason. |
| **Scope** | Custody/track confidence modeling and the weapons-quality gate check. Does not cover how a Track is populated in the first place (FEAT-3200, sensor tasking) or fog-of-war filtering of tracks between cells (FEAT-6200). |
| **Included Requirements** | FR-1510, FR-1520 |
| **Excluded Requirements** | FR-3210/FR-3220 (Track population via SSN tasking — FEAT-3200); FR-6210 (per-cell Track filtering — FEAT-6200) |
| **Dependencies** | FEAT-1200 |
| **Dependent Features** | FEAT-3400, FEAT-6200, FEAT-10100 |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0007, INT-0010 |
| **Related ADRs** | ADR-0013 |
| **User Value** | Custody-before-engagement is the doctrinal control this simulator most directly teaches — "you cannot shoot what you have not confirmed." |
| **Technical Value** | The single gate every engagement-kind order must clear, keeping the rule centralized rather than re-implemented per effect type. |
| **Complexity** | Medium — an on-demand decay function plus a two-condition gate. |
| **Risk** | Low. |
| **Suggested Verification Strategy** | Given a Track observed at T0 with confidence C0, confidence at T1 > T0 with no observation is < C0; an engagement against a sub-threshold or uncharacterized Track is rejected at both plan-time and execute-time. |
| **Open Questions** | None within baseline scope. |

### FEAT-1600 — Sensor Modality-Specific Access & Effectiveness Models

| Field | Content |
|---|---|
| **Feature ID** | FEAT-1600 |
| **Title** | Sensor Modality-Specific Access & Effectiveness Models |
| **Purpose** | Model the real phenomenological differences between sensor modalities (radar beam modes, optical lighting/exclusion-angle constraints, space-based range/band specialization, cue-dependent sensors, passive-RF multilateration) as access/effectiveness refinements layered on the baseline `sensor_observation` channel, rather than treating every sensor as uniformly capable. |
| **Description** | Adds fence/dish radar beam-mode variants, a configurable optical solar/lunar exclusion angle, a space-based minimum-range floor and altitude-band affinity, a cue-dependent tasking precondition, a passive-RF ≥3/≥4-receiver multilateration network, satellite-hosted-sensor orbit-following, and (newly, `FR-1670`, 2026-10-03) a general Sun-target-observer illumination phase-angle (CATS) access-window refinement for any passive EO sensor — each an optional, opt-in refinement a sensor declares; a sensor declaring none of them falls back to the baseline lighting-only predicate (`FR-1220`) unaffected. |
| **Scope** | The seven sensor-modality-specific predicates/effectiveness models themselves. Does not cover the baseline access-window geometry they layer on top of (FEAT-1200, a dependency) or SSN network aggregation generally (FEAT-3200, a peer the passive-RF leaf, `FR-1650`, explicitly reuses rather than duplicates). |
| **Included Requirements** | FR-1610, FR-1620, FR-1630, FR-1640, FR-1650, FR-1660, FR-1670 |
| **Excluded Requirements** | FR-1210/FR-1220 (the baseline propagation/lighting predicate these all layer on — FEAT-1200); FR-3210/FR-3220 (SSN network aggregation `FR-1650` reuses — FEAT-3200) |
| **Dependencies** | FEAT-1200 |
| **Dependent Features** | None |
| **Affected Subsystems** | C1 Simulation Engine, C2 Session/Application Layer, C3 Mock SSN |
| **Affected Interfaces** | INT-0008, INT-0009, INT-0010 |
| **Related ADRs** | ADR-0010, ADR-0011 |
| **User Value** | Lets a vignette author or White Cell model real sensor-type differences (a GEODSS-class optical sensor cannot stare at the Sun; a laser-ranging sensor cannot cold-detect; a TDOA network needs ≥3 simultaneous receivers) rather than one undifferentiated "sensor" abstraction. |
| **Technical Value** | Each predicate is additive and independently opt-in — no existing sensor's behavior changes unless it declares the new field, keeping the baseline `FR-1220` predicate's existing guarantees intact. |
| **Complexity** | Medium-High — six independently-testable predicate/effectiveness models (`FR-1610`-`FR-1660`) plus a seventh, newer one (`FR-1670`) sharing the same opt-in, compose-don't-replace discipline. |
| **Risk** | `FR-1610`-`FR-1660` are `VERIFIED` built (`IP-1220`, per `VR-1220` — `engine/isr.py`, `engine/access.py`, `engine/ssn.py`). `FR-1670` (2026-10-03) is a brand-new, unimplemented leaf with an open research gap on its concrete default phase-angle range/degradation curve (`BL-0112`/`BL-0151`, routed to `06-feature-specification`) — this Feature is **partially built**, not uniformly at one maturity level; a reader should not assume `FR-1670` carries the same verified status as its six siblings. |
| **Suggested Verification Strategy** | Per-leaf acceptance criteria already stated in each FR; for `FR-1670` specifically, given a declared usable phase-angle range and a geometry outside it, the access window is rejected or degraded, composing with (not replacing) `FR-1220`/`FR-1620`. |
| **Open Questions** | This Feature bundles one brand-new FR (`FR-1670`, this run's own scope) together with six pre-existing, already-`VERIFIED` siblings (`FR-1610`-`FR-1660`) that predate this `05-feature-decomposition` run and had no Feature Catalog entry of their own before now — a pre-existing gap this Feature closes as a side effect, flagged explicitly rather than silently; see `05-feature-review.md`. `FR-8220` (the CATS-angle *display* overlay, FEAT-8200) and `FR-1670` (CATS-angle *access-gating*) should share one phase-angle computation per `BL-0152` — a cross-Feature implementation note, not a dependency edge, since neither Feature's own behavior requires the other to exist first. |

---

## Epic EP-2000 — Bus & Payload Operations

### FEAT-2100 — Bus Subsystem State-of-Health Modeling

| Field | Content |
|---|---|
| **Feature ID** | FEAT-2100 |
| **Title** | Bus Subsystem State-of-Health Modeling |
| **Purpose** | Give every asset a live, limit-evaluated health status per subsystem (power, attitude, thermal, propellant, CDH, comms). |
| **Description** | Maintains live SOH values per subsystem, evaluated against configured soft/hard limits to produce green/yellow/red status, transitioning as parameters cross thresholds. |
| **Scope** | SOH value/status modeling only. Payload gating on this status is FEAT-2200; ground-visible (pass-gated) display of this status is FEAT-2300. |
| **Included Requirements** | FR-2110 |
| **Excluded Requirements** | FR-2210 (bus-gates-payload — FEAT-2200); FR-2310 (pass-gated ground visibility — FEAT-2300) |
| **Dependencies** | None |
| **Dependent Features** | FEAT-2200, FEAT-2300, FEAT-2500 |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008 |
| **Related ADRs** | None directly |
| **User Value** | SOH-against-limits is the core bus-operator training objective — the operator's entire situational picture of asset health. |
| **Technical Value** | The health substrate every payload-availability and safe-mode rule reads. |
| **Complexity** | Medium — six subsystem types, each with soft/hard limit evaluation. |
| **Risk** | Low. |
| **Suggested Verification Strategy** | A parameter crossing its soft limit transitions status green→yellow at the next evaluation; crossing the hard limit transitions yellow→red. |
| **Open Questions** | None. |

### FEAT-2200 — Bus-Gates-Payload Availability

| Field | Content |
|---|---|
| **Feature ID** | FEAT-2200 |
| **Title** | Bus-Gates-Payload Availability |
| **Purpose** | Prevent payload operation whenever a prerequisite bus resource (power, pointing, storage) is unavailable, regardless of operator intent. |
| **Description** | Rejects a payload action when its prerequisite bus subsystem is unavailable, independent of whether the operator attempts it — a structural gate, not a UI-only warning. |
| **Scope** | The gating rule itself. Type-specific payload actions are FEAT-2400. |
| **Included Requirements** | FR-2210 |
| **Excluded Requirements** | FR-2410 (type-specific action catalog — FEAT-2400) |
| **Dependencies** | FEAT-2100 |
| **Dependent Features** | FEAT-2400, FEAT-2500 |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008 |
| **Related ADRs** | None directly |
| **User Value** | Realistic bus/payload coupling — you cannot point a full-storage sensor or run a payload with no power, exactly as in real operations. |
| **Technical Value** | Centralizes the coupling rule so every payload verb doesn't need to re-check bus state independently. |
| **Complexity** | Low-Medium. |
| **Risk** | Low. |
| **Suggested Verification Strategy** | Zero-power asset: payload-power-on rejected. Full-storage asset: ISR collection rejected. |
| **Open Questions** | None. |

### FEAT-2300 — Pass-Gated Telemetry & Stored-Dump Catch-Up

| Field | Content |
|---|---|
| **Feature ID** | FEAT-2300 |
| **Title** | Pass-Gated Telemetry & Stored-Dump Catch-Up |
| **Purpose** | Show the operator a ground-visible SOH snapshot that only updates at a telemetry-downlink contact — "belief, not ground truth" applied to health data. |
| **Description** | Freezes the ground-visible SOH snapshot between contacts at its last-known, timestamped value; supports a stored-telemetry dump at the next contact revealing events that occurred out of contact. |
| **Scope** | Telemetry visibility timing only; SOH value computation itself is FEAT-2100. |
| **Included Requirements** | FR-2310, FR-2320 *(sweep 2026-10-17, run #151)* |
| **Excluded Requirements** | FR-2110 (SOH computation — FEAT-2100) |
| **Dependencies** | FEAT-1200, FEAT-2100; FEAT-6200 and FEAT-4400 *(FR-2320: the export is cell-filtered and must show anomaly-inject perturbation, FR-4430)* |
| **Dependent Features** | None |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0007, INT-0008 |
| **Related ADRs** | ADR-0004 |
| **User Value** | Directly enacts the "operate on belief, not ground truth" invariant for the health picture, not just the tactical picture. |
| **Technical Value** | Reuses the fog-of-war philosophy (ADR-0004) at the telemetry layer specifically. |
| **Complexity** | Medium — requires an access-window-gated snapshot plus a separate stored-dump payload path. |
| **Risk** | Low. |
| **Suggested Verification Strategy** | An SOH change between two contacts is invisible until the next telemetry-downlink contact occurs. |
| **Open Questions** | None. |

### FEAT-2400 — Payload-Type-Specific Operator Actions

| Field | Content |
|---|---|
| **Feature ID** | FEAT-2400 |
| **Title** | Payload-Type-Specific Operator Actions |
| **Purpose** | Give each supported payload type (SATCOM, ISR-EO/SAR, SIGINT, SDA, space-control, PNT, missile warning, weather) its own action set and monitors. |
| **Description** | Exposes, per payload type, the operator actions and monitoring displays specific to that type — a SATCOM payload offers frequency/beam-replan; a SIGINT payload does not. |
| **Scope** | Action/monitor catalog per type. Does not cover the bus-availability gate on those actions (FEAT-2200, a dependency). |
| **Included Requirements** | FR-2410 |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-2200 |
| **Dependent Features** | None |
| **Affected Subsystems** | C1 Simulation Engine, C4 Operator Console |
| **Affected Interfaces** | INT-0004, INT-0008 |
| **Related ADRs** | None directly |
| **User Value** | Operating distinct mission types (not one generic "satellite") is an explicit training objective. |
| **Technical Value** | Keeps mission-type variability in a data-driven catalog rather than hard-coded per payload. |
| **Complexity** | Medium-High — eight payload types' worth of distinct verbs (`buscommands.py`). |
| **Risk** | Low; growth risk is additive (new payload type = new catalog entry), not structural. |
| **Suggested Verification Strategy** | Given a SATCOM payload, frequency/beam-replan and customer-shift actions appear and a SIGINT-only action does not. |
| **Open Questions** | None. |

### FEAT-2500 — Safe-Mode Entry, Diagnosis & Recovery Loop

| Field | Content |
|---|---|
| **Feature ID** | FEAT-2500 |
| **Title** | Safe-Mode Entry, Diagnosis & Recovery Loop |
| **Purpose** | Model the full defensive-operations cycle: an asset safes itself on a qualifying fault/attack, and ground drives a multi-pass recovery that either succeeds or re-safes if the root cause persists. |
| **Description** | Transitions an asset to safe mode (payload disabled, sunward-pointed) on a qualifying condition; supports ground-driven multi-pass recovery back to nominal, or re-entry to safe mode if the root cause is unaddressed. |
| **Scope** | The safe-mode state machine and recovery loop. Root-cause fixes themselves (e.g. `def.patch_cyber`) are FEAT-2400's catalog verbs, invoked through this loop. |
| **Included Requirements** | FR-2510 |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-2100, FEAT-2200 |
| **Dependent Features** | None |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008 |
| **Related ADRs** | None directly |
| **User Value** | The defensive-operations and recovery training centerpiece — trainees must diagnose and fix a root cause, not just click "recover." |
| **Technical Value** | Reuses SOH (FEAT-2100) and payload-gating (FEAT-2200) rather than duplicating health logic. |
| **Complexity** | High — multi-pass state machine with persistence-detection re-safing. |
| **Risk** | Low technical risk; the strategic review's negative-training risk register (§4.5) names "facilitator/adjudication drift" around recovery correctness as a process risk, out of this Feature's scope. |
| **Suggested Verification Strategy** | An unaddressed root cause after a completed recovery procedure re-enters safe mode rather than reaching a stable nominal state. |
| **Open Questions** | None. |

---

## Epic EP-3000 — Command Planning & Sensor Tasking

### FEAT-3100 — Plan-First Command Authoring & Delivery Path

| Field | Content |
|---|---|
| **Feature ID** | FEAT-3100 |
| **Title** | Plan-First Command Authoring & Delivery Path |
| **Purpose** | Let an operator plan a command for the earliest valid access window (or a chosen future one) via uplink, ISL relay, or stored program, remaining editable/cancellable until uplink. |
| **Description** | Creates a `PlannedActivity` (command-kind) with a delivery path and scheduled window; supports edit/cancel at any point before the `ACTIVE`/execution transition. |
| **Scope** | Command-kind planned-activity creation and pre-execution editability. Collection-kind tasking is FEAT-3200; the shared scheduling mechanism both kinds ride on is FEAT-3300. |
| **Included Requirements** | FR-3110, FR-3120 |
| **Excluded Requirements** | FR-3210 (collection-kind tasking — FEAT-3200); FR-3310 (shared scheduler — FEAT-3300) |
| **Dependencies** | FEAT-1200 |
| **Dependent Features** | FEAT-3300, FEAT-3400, FEAT-9100; FEAT-1300, FEAT-1400 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C1 Simulation Engine, C2 Session/Application Layer |
| **Affected Interfaces** | INT-0004, INT-0006, INT-0008 |
| **Related ADRs** | ADR-0005 |
| **User Value** | "Plan-first, never instant action on perfect knowledge" is one of the project's five load-bearing invariants — this Feature is its command-side embodiment. |
| **Technical Value** | Every operator-issued command and AI-Red-issued activity (FEAT-9100) flows through this Feature's lifecycle. |
| **Complexity** | Medium-High. |
| **Risk** | Low; well-covered by existing tests per `CLAUDE.md`'s code map (`test_orders.py`, `test_validate_order.py`). |
| **Suggested Verification Strategy** | A `PLANNED`-state activity cancelled before its window opens is removed with no `WorldState` effect. |
| **Open Questions** | None. |

### FEAT-3200 — SSN Sensor Tasking Under Contention

| Field | Content |
|---|---|
| **Feature ID** | FEAT-3200 |
| **Title** | SSN Sensor Tasking Under Contention |
| **Purpose** | Let an operator task a scarce sensor (search/track/characterize/cue) subject to single-task contention, modeling real sensor scarcity as a "request and wait" texture. |
| **Description** | Submits an SSN request against a sensor's `task_capacity`; a request exceeding capacity is rejected or queued, never silently double-booked; a resolved request delivers a Track into the requester's `TrackCatalog`, unless cancelled before collection. |
| **Scope** | Request submission, contention, and delivery. Track confidence decay after delivery is FEAT-1500. |
| **Included Requirements** | FR-3210, FR-3220 |
| **Excluded Requirements** | FR-1510/FR-1520 (post-delivery Track confidence/gate — FEAT-1500) |
| **Dependencies** | FEAT-1200 |
| **Dependent Features** | FEAT-3300 |
| **Affected Subsystems** | C1 Simulation Engine, C2 Session/Application Layer, C3 Mock SSN |
| **Affected Interfaces** | INT-0009, INT-0010 |
| **Related ADRs** | ADR-0010 |
| **User Value** | Scarce SDA sensors and contention are an explicit training objective — you cannot task everything, all the time. |
| **Technical Value** | The mock-SSN request/delivery lifecycle other custody-consuming Features (FEAT-1500) build on. |
| **Complexity** | Medium-High — priority-SLA-plus-processing-delay resolution timing, cancel-before-collect tag-skip. |
| **Risk** | Low. |
| **Suggested Verification Strategy** | A `task_capacity = 1` sensor already serving one task rejects/queues a second concurrent request; a cancelled-before-resolution request produces no Track update. |
| **Open Questions** | None. |

### FEAT-3300 — Unified Planned-Activity Scheduler

| Field | Content |
|---|---|
| **Feature ID** | FEAT-3300 |
| **Title** | Unified Planned-Activity Scheduler |
| **Purpose** | Give command-kind and collection-kind activities identical queueing, timeline, undo, and time-travel behavior on one scheduling mechanism. |
| **Description** | Implements both activity kinds on a single scheduler so undo/rewind treats a collection-kind activity exactly as it treats a command-kind one. |
| **Scope** | The shared scheduling mechanism itself, not either kind's own creation rules (FEAT-3100, FEAT-3200). |
| **Included Requirements** | FR-3310 |
| **Excluded Requirements** | FR-3110 (command creation — FEAT-3100); FR-3210 (collection creation — FEAT-3200) |
| **Dependencies** | FEAT-3100, FEAT-3200 |
| **Dependent Features** | None |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008 |
| **Related ADRs** | None directly |
| **User Value** | Consistent undo/rewind behavior regardless of what kind of action a trainee took — no special-case confusion during AAR scrub. |
| **Technical Value** | Avoids divergent behavior between the two "request now, result later" activity kinds (a divergence CR-09 in the requirements baseline separately flags as an open unification question at the entity-supertype level). |
| **Complexity** | Medium. |
| **Risk** | The RTM lists this leaf's Impl. Package as `UNASSIGNED` (no direct code citation) — a traceability gap to close, not a build gap (see `05-feature-review.md`). |
| **Suggested Verification Strategy** | Rewinding to before a collection-kind activity's execution returns it to its pre-execution state exactly as a command-kind activity would under the same rewind. |
| **Open Questions** | Whether this should eventually share a formal supertype with SSN Request entities (CR-09) is an open architecture question, not resolved by this catalog. |

### FEAT-3400 — Execute-Time Re-Validation

| Field | Content |
|---|---|
| **Feature ID** | FEAT-3400 |
| **Title** | Execute-Time Re-Validation |
| **Purpose** | Re-check ownership, window validity, resources, ROE, and the weapons-quality gate at the moment an activity actually executes, since state can change between plan-time and execute-time. |
| **Description** | Re-validates every Planned Activity against five checks at its scheduled execution point; fails gracefully to a `FAILED` state with a recorded reason on any check failure, consuming no resources. |
| **Scope** | The re-validation checks themselves. The activities being validated are created by FEAT-3100/FEAT-3200; the resource and custody rules being checked are owned by FEAT-1300/FEAT-1500 respectively. *(Sweep 2026-10-17:)* also owns per-cell ROE (`FR-3420`), optional role-authorization gating (`FR-3430`) and live logged ROE changes (`FR-3440`) — ROE is one of `FR-3410`'s five execute-time gates, so the family stays with its parent. |
| **Included Requirements** | FR-3410, FR-3420, FR-3430, FR-3440 *(sweep 2026-10-17, run #151)* |
| **Excluded Requirements** | FR-1310 (Δv rule itself — FEAT-1300); FR-1520 (weapons-quality rule itself — FEAT-1500) |
| **Dependencies** | FEAT-3100, FEAT-1300, FEAT-1500; FEAT-4200, FEAT-4700, FEAT-7100, FEAT-1100 *(FR-3430/FR-3440: role-authorization gating uses role assignments, live ROE changes are a manual-adjudication action, both logged and replay-safe)* |
| **Dependent Features** | FEAT-9100, FEAT-10100; FEAT-1400 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008 |
| **Related ADRs** | ADR-0005, ADR-0013 |
| **User Value** | Prevents a stale plan from executing illegally just because it was legal when planned — a resource depleted or a window closed in the meantime is caught, not ignored. |
| **Technical Value** | The single choke point every activity passes through immediately before taking effect, keeping five independent rule sets enforced consistently. |
| **Complexity** | Medium-High. |
| **Risk** | Low. |
| **Suggested Verification Strategy** | An activity whose resource requirement became unaffordable after planning transitions to `FAILED` with a resource-related reason and consumes nothing. |
| **Open Questions** | None. |

### FEAT-3500 — Role-Scoped Command Catalog & Assignment Scoping

| Field | Content |
|---|---|
| **Feature ID** | FEAT-3500 |
| **Title** | Role-Scoped Command Catalog & Assignment Scoping |
| **Purpose** | Ensure an operator only ever sees, and can only ever execute, commands legal for their seated role (bus/payload/both) and assigned asset. |
| **Description** | Filters the order panel to the seated role's legal commands, and independently enforces that scope as a system behavior at execution time — not merely a UI filter — per a Role Assignment scoped bus-only, payload-only, or both. |
| **Scope** | Command filtering and scope enforcement. Role Assignment *creation* itself (who assigns whom) is FEAT-4200. |
| **Included Requirements** | FR-3510, FR-3520 |
| **Excluded Requirements** | FR-4210 (Role Assignment creation at setup — FEAT-4200) |
| **Dependencies** | None |
| **Dependent Features** | None |
| **Affected Subsystems** | C4 Operator Console |
| **Affected Interfaces** | INT-0004, INT-0006 |
| **Related ADRs** | ADR-0004 |
| **User Value** | Prevents an operator from issuing commands outside their assigned responsibility — a bus-only operator cannot execute a payload verb even by bypassing the UI. |
| **Technical Value** | This leaf (FR-3520) was added specifically because FR-3510 alone described only the UI-filtering *consequence*, leaving no independently testable enforcement leaf (GDS-05 rationale) — the two together close that gap. |
| **Complexity** | Medium. |
| **Risk** | Both included FRs show `UNASSIGNED` in the RTM's Impl. Package column — a traceability gap flagged in `05-feature-review.md`, not necessarily a build gap. |
| **Suggested Verification Strategy** | A bus-only Role Assignment: payload-only command does not appear in the offered list, and is rejected if submitted directly bypassing the panel. |
| **Open Questions** | Confirm code-level citation for FR-3510/FR-3520 to close the RTM `UNASSIGNED` gap. |

---

## Epic EP-4000 — White Cell Exercise Control

### FEAT-4100 — Vignette Selection & Parameter Tuning

| Field | Content |
|---|---|
| **Feature ID** | FEAT-4100 |
| **Title** | Vignette Selection & Parameter Tuning |
| **Purpose** | Let White Cell pick a vignette and adjust its tunable parameters before starting an exercise, with every parameter runnable unmodified. |
| **Description** | Selects a Vignette and applies optional parameter overrides at session start; any unmodified parameter takes its documented default. |
| **Scope** | Selection/tuning at session start. The vignette file's own validity is FEAT-5300 (a dependency); in-app authoring of a new vignette is FEAT-5100. |
| **Included Requirements** | FR-4110 |
| **Excluded Requirements** | FR-5310 (vignette validation — FEAT-5300, a dependency); FR-5110 (vignette authoring — FEAT-5100) |
| **Dependencies** | FEAT-5300 |
| **Dependent Features** | FEAT-4200; FEAT-11300 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C6 White Cell |
| **Affected Interfaces** | INT-0002 |
| **Related ADRs** | None directly |
| **User Value** | White Cell facilitators are assumed non-programmers — a runnable-unmodified default set is what makes the tool usable without a config file edit. |
| **Technical Value** | Gates FEAT-4200 (seat assignment reads the vignette's `roles_needed`). |
| **Complexity** | Low-Medium. |
| **Risk** | RTM Impl. Package `UNASSIGNED` — a traceability gap; the existing `FS-106-white-cell-dashboard.md` narratively covers vignette selection as part of "session admin," so this is very likely a citation gap, not a missing capability (see `05-feature-review.md`). |
| **Suggested Verification Strategy** | A vignette with no overrides starts using every documented default value. |
| **Open Questions** | Close the RTM citation gap. |

### FEAT-4200 — Seat-to-Role Assignment

| Field | Content |
|---|---|
| **Feature ID** | FEAT-4200 |
| **Title** | Seat-to-Role Assignment |
| **Purpose** | Let White Cell bind operator seats to roles/assets per the vignette's declared `roles_needed`, and refuse to silently understaff a mandatory seat. |
| **Description** | Assigns each seat one or more roles (bus/payload/both) per Asset/constellation; reports any unmet mandatory `roles_needed` entry rather than allowing a silently understaffed start. |
| **Scope** | Assignment creation/validation at setup. The runtime enforcement of an assignment's scope is FEAT-3500. *(Sweep 2026-10-17:)* also owns the load-time check that each `roles_needed` entry names a declared asset or group (`FR-5314`), which is about the integrity of this Feature's own records; it runs inside FEAT-5300's gate. |
| **Included Requirements** | FR-4210, FR-5314 *(sweep 2026-10-17, run #151)* |
| **Excluded Requirements** | FR-5160 (the Vignette Creator's seat/role matrix — FEAT-5100, an authoring surface over this Feature's records) |
| **Dependencies** | FEAT-4100; FEAT-5300 *(FR-5314 runs inside the load-time validation gate)* |
| **Dependent Features** | FEAT-3400, FEAT-5100 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C6 White Cell |
| **Affected Interfaces** | INT-0002 |
| **Related ADRs** | None directly |
| **User Value** | Prevents starting an exercise where a mandatory role has no seated operator — catches a setup mistake before it wastes exercise time. |
| **Technical Value** | Produces the Role Assignment records FEAT-3500 enforces at runtime. |
| **Complexity** | Low-Medium. |
| **Risk** | RTM Impl. Package `UNASSIGNED` — traceability gap (see `05-feature-review.md`); narratively covered by `FS-106`. |
| **Suggested Verification Strategy** | A vignette with an unmet mandatory `roles_needed` entry is reported as unsatisfied rather than allowed to start silently understaffed. |
| **Open Questions** | Close the RTM citation gap. |

### FEAT-4300 — Single-Point-of-Time Clock Control

| Field | Content |
|---|---|
| **Feature ID** | FEAT-4300 |
| **Title** | Single-Point-of-Time Clock Control |
| **Purpose** | Restrict start/pause/resume/fast-forward/rewind of the simulated clock — and, since run #212, every other White Cell lifecycle and facilitation control (FR-4320) — to the White Cell role, so no operator gains a tempo or information advantage. |
| **Description** | Accepts clock-control requests only from the White Cell role; rejects the same request from a Blue or Red cell role with no clock-state change. FR-4320 extends the same server-side refusal to the White Cell's other lifecycle and facilitation controls (inject firing, role assignment, force edits, session start). Enforcement is at the asserted-seat trust level of the LAN trust model (FR-6220), the same level as the Observer refusal. |
| **Scope** | Authority/permission over clock control. The clock mechanism itself is FEAT-1100. |
| **Included Requirements** | FR-4310, FR-4320 *(sweep 2026-10-23, run #212)* |
| **Excluded Requirements** | FR-1110/FR-1120/FR-1130 (clock mechanism — FEAT-1100) |
| **Dependencies** | FEAT-1100 |
| **Dependent Features** | None |
| **Affected Subsystems** | C6 White Cell |
| **Affected Interfaces** | INT-0002 |
| **Related ADRs** | ADR-0016 |
| **User Value** | Keeps the exercise narratively coherent and fair — no cell can privately fast-forward or rewind to gain advantage. |
| **Technical Value** | The authority layer over FEAT-1100's mechanism; cleanly separable from it (see the resolved circular-citation note under FEAT-1100). |
| **Complexity** | Low. |
| **Risk** | **Not met as built** (requirements review R1, High): IP-1060/VR-1060 recorded FR-4310 as enforced, but the server accepts `/clock`, `/step`, `/advance`, `/rewind` and `/undo` from any non-Observer seat (GDS-09 §4); only five White-only actions are refused server-side. Remediation is `BL-0307`. |
| **Suggested Verification Strategy** | A clock-control request, and each FR-4320 control, from a Blue or Red role is rejected with the session state unchanged — asserted by a test per route, since a package claim alone proved insufficient (R1). |
| **Open Questions** | See FEAT-1100's Open Questions for the resolved circular-dependency note this Feature is one side of. |

### FEAT-4400 — Inject Authoring & Firing

| Field | Content |
|---|---|
| **Feature ID** | FEAT-4400 |
| **Title** | Inject Authoring & Firing |
| **Purpose** | Let White Cell apply a scripted or manual inject immediately or at a scheduled simulated time, as the documented bypass of plan-first commanding for narrative control. |
| **Description** | Applies an Inject's effects outside the normal Planned-Activity/access-window path, immediately or at a future `at_sim_t`; a scheduled inject survives save/resume and fires byte-identically. Also lets White Cell edit the parameters of, or cancel, a scheduled inject before it fires (`FR-4450`, added 2026-10-03). |
| **Scope** | Inject application/scheduling, plus pre-fire edit/cancel of an already-scheduled inject. The *authoring UX* around this (templated/preview inject-authoring, the FS-108 candidate) is a presentation-layer concern layered on top, not part of this Feature's own requirement scope. |
| **Included Requirements** | FR-4410, FR-4420, FR-4430, FR-4440 *(sweep 2026-10-17, run #151)*, FR-4450 |
| **Excluded Requirements** | None baselined-adjacent (the richer authoring UX has no baselined FR — it is FS-108, an unauthorized candidate spec per `docs/features/feature-index.md`). |
| **Dependencies** | FEAT-1100; FEAT-6100 and FEAT-1200 *(FR-4430 delivers new inject types through the SessionAPI; FR-4440 reads FR-1230's index series)* |
| **Dependent Features** | FEAT-2300 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C6 White Cell, C1 Simulation Engine |
| **Affected Interfaces** | INT-0002, INT-0016 |
| **Related ADRs** | ADR-0005 |
| **User Value** | Injects are White Cell's accepted narrative-control tool — the mechanism behind every "unexpected debris event" or "GNSS jamming advisory" moment; `FR-4450` adds the ability to correct or withdraw one before it fires, per `BL-0079` (Could-tier). |
| **Technical Value** | A documented, bounded escape hatch from plan-first commanding rather than an ad hoc one. |
| **Complexity** | Medium (the original `FR-4410` scheduling mechanism); Low (`FR-4450`'s edit/cancel addition — mutates/removes an already-modeled pending-inject record, no new mechanism). |
| **Risk** | `FR-4410` low; verified (`session/manager.py`). `FR-4450` is a brand-new, unimplemented Could-tier leaf (RTM `UNASSIGNED`) — a genuine future-build item, not yet a traceability-only gap like the rest of this Feature. |
| **Suggested Verification Strategy** | A session saved and resumed before a scheduled inject's `at_sim_t` still fires it at the correct time with identical effects to an unsaved run; a cancel request against a scheduled, not-yet-fired inject removes it from the pending queue and it does not subsequently fire. |
| **Open Questions** | None within baseline scope for `FR-4410`; FS-108's richer authoring UX remains a separate, unauthorized candidate (see `05-feature-review.md`). `FR-4450` has no implementation yet — a future `06-feature-specification`/`07-implementation-planning` pass. |

### FEAT-4500 — Classification Banner

| Field | Content |
|---|---|
| **Feature ID** | FEAT-4500 |
| **Title** | Classification Banner |
| **Purpose** | Make explicit, on every screen and export, that all content is unclassified training material. |
| **Description** | Lets White Cell set a classification banner (`UNCLASSIFIED//EXERCISE` or `UNCLASSIFIED//TRAINING`) at scenario build; displays it on every screen and embeds it in every export with no omission. |
| **Scope** | Banner value setting and universal display/embedding. |
| **Included Requirements** | FR-4510, NFR-3100 |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-5100 |
| **Dependent Features** | None |
| **Affected Subsystems** | C6 White Cell, C4 Operator Console |
| **Affected Interfaces** | INT-0002, INT-0001 |
| **Related ADRs** | None directly |
| **User Value** | A PME tool must never be mistaken for, or resemble, real classified material — this is a safety-of-use property, not decoration. |
| **Technical Value** | One value, universally rendered — simple mechanism, high consequence if it silently fails to appear anywhere. |
| **Complexity** | Low. |
| **Risk** | **This Feature has no owning Feature Specification anywhere in the existing `docs/features/` corpus and its RTM Impl. Package is `UNASSIGNED`** — the audit that motivated this catalog specifically flagged this as undocumented; see `05-feature-review.md`. |
| **Suggested Verification Strategy** | Every screen render and every AAR export produced during a session with banner X set displays/embeds banner X — a static sweep across all render/export paths with none omitted. |
| **Open Questions** | Confirm build status directly against `ui_web/static/` and `session/aar.py` export paths; author the missing Feature Specification. |

### FEAT-4600 — God-View & Per-Cell View-As

| Field | Content |
|---|---|
| **Feature ID** | FEAT-4600 |
| **Title** | God-View & Per-Cell View-As |
| **Purpose** | Let White Cell see ground truth plus both cells' belief states combined, and switch to viewing exactly as Red or Blue would, for fair adjudication. |
| **Description** | Provides a combined god-view and a view-as-cell mode that never grants White Cell write access to that cell's state through the view-as path. Also provides a simultaneous side-by-side presentation of ground truth plus each cell's belief state (`FR-4620`, added 2026-10-03), distinct from view-as-cell's sequential one-at-a-time switching. |
| **Scope** | The White Cell view mechanism, both sequential (view-as) and simultaneous (side-by-side). The underlying per-cell filtering it borrows is FEAT-6200 (a dependency). |
| **Included Requirements** | FR-4610, FR-4620 |
| **Excluded Requirements** | FR-6210 (the underlying fog-of-war filter — FEAT-6200) |
| **Dependencies** | FEAT-6200 |
| **Dependent Features** | None |
| **Affected Subsystems** | C6 White Cell |
| **Affected Interfaces** | INT-0002, INT-0007 |
| **Related ADRs** | ADR-0004 |
| **User Value** | White Cell must adjudicate using each side's *actual* belief state, not an assumption about it — this Feature makes that literally checkable; `FR-4620` additionally lets White Cell compare both cells' belief against truth at a glance rather than switching back and forth, per `BL-0079` (Could-tier). |
| **Technical Value** | Reuses FEAT-6200's filter rather than a separate, potentially-diverging White-Cell-only view path, for both the sequential and simultaneous presentations. |
| **Complexity** | Medium (`FR-4610`); Low-Medium (`FR-4620` — a layout/rendering addition over the same already-filtered data, no new filtering mechanism). |
| **Risk** | `FR-4610`'s RTM Impl. Package `UNASSIGNED` — traceability gap; narratively covered by `FS-106`. `FR-4620` is a brand-new, unimplemented Could-tier leaf (RTM `UNASSIGNED`) — a genuine future-build item, not yet a traceability-only gap. |
| **Suggested Verification Strategy** | White Cell viewing as Red sees exactly what a Red-seated operator would see via INT-0004, no more, no less; White Cell's side-by-side view simultaneously displays ground truth and both cells' `CellView`s, each matching that same exact-match standard. |
| **Open Questions** | Close the RTM citation gap for `FR-4610`. `FR-4620` has no implementation yet — a future `06-feature-specification`/`07-implementation-planning` pass. |

### FEAT-4700 — Manual Adjudication & Live Parameter Adjustment

| Field | Content |
|---|---|
| **Feature ID** | FEAT-4700 |
| **Title** | Manual Adjudication & Live Parameter Adjustment |
| **Purpose** | Keep outcome adjudication entirely manual (no automated score/win-loss), while letting White Cell tune live exercise parameters (e.g. safe-mode dials) mid-session without a restart. |
| **Description** | No interface computes or displays a score/win-loss verdict — White Cell adjudicates from raw state/event-log data; a running session's White-Cell-configurable parameters can be adjusted live, taking effect on next evaluation with no restart. |
| **Scope** | The absence-of-scoring guarantee and the live-tuning mechanism. |
| **Included Requirements** | FR-4710, FR-4720 |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | None |
| **Dependent Features** | FEAT-3400 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C6 White Cell |
| **Affected Interfaces** | (none — FR-4710 is an absence-of-interface requirement); INT-0002 (FR-4720) |
| **Related ADRs** | ADR-0017, ADR-0029 |
| **User Value** | Manual adjudication is an explicit v1 design decision — the facilitator's judgment stays authoritative, not a hidden scoring formula. |
| **Technical Value** | Keeps the "no automated scoring" invariant checkable by inspection (a review of every outbound interface). |
| **Complexity** | Low (FR-4710 is a negative/absence requirement); Medium (FR-4720's live-tuning mechanism). |
| **Risk** | Both leaves show RTM Impl. Package `UNASSIGNED` — traceability gap; the strategic review (§4.5) separately flags "facilitator/adjudication drift" as an unmitigated negative-training risk, a process concern outside this Feature's own scope (tracked as CR-18). |
| **Suggested Verification Strategy** | A review of every outbound interface confirms none returns a computed score/win-loss field; a live safe-mode dial adjustment takes effect on next evaluation with no restart. |
| **Open Questions** | Close the RTM citation gap; CR-18 (adjudication-consistency support) is a related but distinct future concept, not part of this Feature. |

---

## Epic EP-5000 — Scenario / Vignette Authoring

### FEAT-5100 — In-App Iterative Vignette Builder

| Field | Content |
|---|---|
| **Feature ID** | FEAT-5100 |
| **Title** | In-App Iterative Vignette Builder |
| **Purpose** | Let White Cell compose a vignette (force lay-down, parameters, injects, intro briefs) across multiple round trips before a single save/build emits a complete file. |
| **Description** | Accumulates partial authoring state across an authoring session; emits a complete vignette file only on an explicit save/build action; no partial/incomplete file is ever written from an in-progress session. |
| **Scope** | Iterative composition mechanics. TLE import during authoring is FEAT-5200; validation of the resulting file is FEAT-5300. |
| **Included Requirements** | FR-5110, FR-5120, FR-5130, FR-5140, FR-5150, FR-5160, FR-5170, FR-5180 *(sweep 2026-10-17, run #151)*, NFR-2000, NFR-2010 *(sweep 2026-10-17, run #151)* |
| **Excluded Requirements** | FR-5210/FR-5220 (TLE/OMM import — FEAT-5200); FR-5310–FR-5313 (validation — FEAT-5300); FR-5420 (where `save_vignette` may write — FEAT-5400) |
| **Dependencies** | FEAT-4200 *(FR-5160: the Creator's seat/role matrix authors role assignments)* |
| **Dependent Features** | FEAT-4500; FEAT-5200 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C5 Content & Data, C6 White Cell |
| **Affected Interfaces** | INT-0003 |
| **Related ADRs** | ADR-0027, ADR-0007 |
| **User Value** | The success vision of a no-programming facilitator authoring scenarios depends entirely on this Feature, not YAML hand-editing. |
| **Technical Value** | Content-as-data (NFR-2000) is only realized as a real workflow advantage if this authoring path exists and is usable. |
| **Complexity** | Medium-High. |
| **Risk** | The strategic review (§4.2 item 2) flags scenario authoring as still "White-Cell-hostile" in practice — YAML hand-editing may remain the only *actually used* path even where this Feature's requirement is nominally met; CR-11 separately leaves open where in-progress authoring state lives (server- vs. browser-session-scoped). |
| **Suggested Verification Strategy** | An authoring session with several incremental inputs but no final save/build writes no vignette file to disk. |
| **Open Questions** | CR-11 (partial-authoring-state ownership) is unresolved upstream; not decided by this catalog. |

### FEAT-5200 — TLE Import with Manual/Keplerian Fallback

| Field | Content |
|---|---|
| **Feature ID** | FEAT-5200 |
| **Title** | TLE Import with Manual/Keplerian Fallback |
| **Purpose** | Import real-satellite TLEs from Space-Track at build time when reachable, falling back to manual entry so the tool never depends on network reachability once a vignette exists. |
| **Description** | Attempts Space-Track import at build time; accepts manual TLE/Keplerian entry as fallback; no network access is required after vignette creation. |
| **Scope** | Import mechanics and offline-first guarantee. |
| **Included Requirements** | FR-5210, FR-5220 *(sweep 2026-10-17, run #151)*, NFR-3200 |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-1200; FEAT-5100 *(FR-5220: bulk import adds assets through the Creator's asset entry, FR-5140)* |
| **Dependent Features** | None |
| **Affected Subsystems** | C5 Content & Data, C10 Space-Track.org (external) |
| **Affected Interfaces** | INT-0013 |
| **Related ADRs** | ADR-0018 |
| **User Value** | Lets White Cell build realistic, real-satellite vignettes without a permanent internet dependency for the training room. |
| **Technical Value** | Offline-first is a load-bearing invariant this Feature is the sole network-touching exception to, cleanly bounded to build time only. |
| **Complexity** | Medium. |
| **Risk** | Low; the external dependency (Space-Track availability/policy) is a documented medium-term risk per the strategic review (§1.4), out of this Feature's control. |
| **Suggested Verification Strategy** | With Space-Track unreachable, manual TLE entry still produces a valid `OrbitState`. |
| **Open Questions** | None within baseline scope. |

### FEAT-5300 — Load-Time Vignette Validation

| Field | Content |
|---|---|
| **Feature ID** | FEAT-5300 |
| **Title** | Load-Time Vignette Validation |
| **Purpose** | Fail loudly and precisely on an invalid vignette at load time rather than partially or silently loading it. |
| **Description** | Validates each vignette in full at load — well-formed TLEs that propagate (`FR-5311`), an orbit or location per asset kind (`FR-5312`), unique identifiers (`FR-5313`), entity field rules — and rejects with a precise, actionable error identifying every failing element. The template clause of `FR-5310` awaits `ADR-0036` (owner decision). |
| **Scope** | Validation logic and error precision. Secure-loading practice (no scenario-embedded code execution) is bundled here as the nearest architectural home. |
| **Included Requirements** | FR-5310, FR-5311, FR-5312, FR-5313 *(sweep 2026-10-17, run #151)*, NFR-1600, NFR-2200 |
| **Excluded Requirements** | FR-5314 (`roles_needed` references — owned by FEAT-4200, which owns the `roles_needed` concept, FR-4210; placing it here would make FEAT-5300 → FEAT-4200 → FEAT-4100 → FEAT-5300 circular — see `05-feature-review.md` F-14); FR-5410/FR-5420 (external directories — FEAT-5400) |
| **Dependencies** | None |
| **Dependent Features** | FEAT-4100; FEAT-4200, FEAT-5400 *(sweep 2026-10-17)*; FEAT-1100, FEAT-12100 *(sweep 2026-10-23)* |
| **Affected Subsystems** | C5 Content & Data |
| **Affected Interfaces** | INT-0011 |
| **Related ADRs** | ADR-0007 |
| **User Value** | "Invalid scenario data fails loudly at load" — a facilitator gets a fixable error message, not a mysterious partial state. |
| **Technical Value** | The gate every vignette (hand-authored, in-app-built, or TLE-imported) passes through before it can start a session. |
| **Complexity** | Medium. |
| **Risk** | Low. |
| **Suggested Verification Strategy** | A vignette with a missing satellite orbit, a duplicate id, or an unpropagatable TLE is refused at load with every problem named, and no session is created. (The template case waits for `ADR-0036`.) |
| **Open Questions** | `FR-5310`'s template clause — `ADR-0036` `Proposed`, owner decision pending (`BL-0233`); FS-131 criterion 10 blocked until then. |

### FEAT-5400 — External Vignette Library Directories *(sweep 2026-10-17, run #151)*

| Field | Content |
|---|---|
| **Feature ID** | FEAT-5400 |
| **Title** | External Vignette Library Directories *(sweep 2026-10-17, run #151)* |
| **Purpose** | Let a site keep its own vignettes outside the shipped library, and keep authored files out of the built-in directory. |
| **Description** | Loads vignettes from configured external directories after the built-in library (built-in wins on an id collision, disclosed), and restricts `save_vignette` to a configured user directory, with the same path-traversal guard on every root. |
| **Scope** | Where vignettes may be read from and written to. Validation of what is read is FEAT-5300. |
| **Included Requirements** | FR-5410, FR-5420, NFR-3700 |
| **Excluded Requirements** | FR-5310–FR-5313 (validation — FEAT-5300); NFR-2200 (built-in-root path safety — FEAT-5300, which NFR-3700 generalizes) |
| **Dependencies** | FEAT-5300 (FR-5410 depends on FR-5310; NFR-3700 on NFR-2200) |
| **Dependent Features** | FEAT-5500 |
| **Affected Subsystems** | C5 Content & Data, C11 Local filesystem (external) |
| **Affected Interfaces** | INT-0011, INT-0012 |
| **Related ADRs** | ADR-0007, ADR-0018, ADR-0022 |
| **User Value** | A facilitator's own scenario library survives upgrades and stays separate from shipped content (FR-5410/FR-5420 Rationale). |
| **Technical Value** | One guarded resolution path for every content root. |
| **Complexity** | Low-Medium. |
| **Risk** | Low; built and verified (`IP-1180`, FS-118). Path safety across several roots is the main exposure, covered by NFR-3700. |
| **Suggested Verification Strategy** | A vignette in a configured external directory loads by id; a built-in id wins a collision with a warning; a traversal id is refused for every root; `save_vignette` never writes into the built-in directory. |
| **Open Questions** | None within baseline scope. |

### FEAT-5500 — Save Running Session as a New Starting Vignette *(sweep 2026-10-17, run #151)*

| Field | Content |
|---|---|
| **Feature ID** | FEAT-5500 |
| **Title** | Save Running Session as a New Starting Vignette *(sweep 2026-10-17, run #151)* |
| **Purpose** | Let White Cell turn a mid-exercise state into the starting point of a new vignette, for follow-on or branched exercises. |
| **Description** | Writes the running session's current state (assets, tracks, space weather) as a new vignette file that loads like any other, without altering the live session. |
| **Scope** | The save-as-scenario export. Save/resume of a session itself is FEAT-7200. |
| **Included Requirements** | FR-5510 |
| **Excluded Requirements** | FR-7210 (session save/resume — FEAT-7200) |
| **Dependencies** | FEAT-5400 (writes to the user directory, FR-5420), FEAT-7200 (FR-7210) |
| **Dependent Features** | None |
| **Affected Subsystems** | C5 Content & Data, C2 Session/Application Layer |
| **Affected Interfaces** | INT-0011, INT-0012 |
| **Related ADRs** | ADR-0022, ADR-0007 |
| **User Value** | Campaign-style continuation without re-authoring (FR-5510 Rationale). |
| **Technical Value** | Reuses the content model and export path rather than a parallel snapshot format. |
| **Complexity** | Medium. |
| **Risk** | Low; built and verified (`IP-1200`, FS-120). A single-requirement Feature — see `05-feature-review.md` F-15. |
| **Suggested Verification Strategy** | Saving a running session produces a vignette that loads, carries the session's tracks and space weather, and leaves the live session unchanged. |
| **Open Questions** | None within baseline scope. |

---

## Epic EP-6000 — Session, Multiplayer & Fog-of-War

### FEAT-6100 — SessionAPI Single Seam

| Field | Content |
|---|---|
| **Feature ID** | FEAT-6100 |
| **Title** | SessionAPI Single Seam |
| **Purpose** | Force every access to simulation state/control — from Operator Console, AI-Red, or AAR — through one seam, so the engine stays UI-agnostic and presentation is swappable. |
| **Description** | No component outside the Session Layer holds a direct structural dependency on engine internals; every mutating call through the seam is logged to the `EventLog`. |
| **Scope** | The seam's existence and universality as an architectural boundary. Fog-of-war filtering *at* that boundary is FEAT-6200. |
| **Included Requirements** | FR-6110, NFR-3710 *(sweep 2026-10-23, run #212)* |
| **Excluded Requirements** | FR-6210 (fog-of-war filtering at the boundary — FEAT-6200) |
| **Dependencies** | None |
| **Dependent Features** | FEAT-6200; FEAT-4400 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C2 Session/Application Layer |
| **Affected Interfaces** | INT-0006 |
| **Related ADRs** | ADR-0002, ADR-0003 |
| **User Value** | Indirect — this is the architectural property that keeps the front end replaceable, which protects every future UI investment. |
| **Technical Value** | The single most important structural boundary in the codebase (`CLAUDE.md` invariant 2); everything cell-facing routes through it. |
| **Complexity** | Low to state, High to keep true under pressure to add a shortcut. |
| **Risk** | The only automated defense is a static-review acceptance criterion (Verification Method: Inspection) rather than a test — a future contributor could add a direct engine import without a failing test catching it. |
| **Suggested Verification Strategy** | A static review of the Operator Console codebase confirms no import of an engine-internal module outside the Session Layer's seam. |
| **Open Questions** | Whether this should be enforced by an automated import-guard test (as the engine/UI boundary already is, `test_import_guard.py`) rather than manual inspection is worth raising upstream — noted, not decided, here. |

### FEAT-6200 — Fog-of-War Filtering at the Session Boundary

| Field | Content |
|---|---|
| **Feature ID** | FEAT-6200 |
| **Title** | Fog-of-War Filtering at the Session Boundary |
| **Purpose** | Produce each cell's view of the world by filtering ground truth at the session boundary — never by the UI withholding data — with a documented, named exception set. |
| **Description** | Filters `CellView` to each cell's own assets/tracks/effects/messages; permits exactly the documented no-cell ground-truth endpoints (god-view, event log, save, AAR, objectives) to bypass filtering as an explicit, bounded v1 trust exception. |
| **Scope** | The filter mechanism and its named exception set. God-view/view-as itself (a White-Cell-specific consumer of this filter) is FEAT-4600. |
| **Included Requirements** | FR-6210, FR-6220, NFR-2300 |
| **Excluded Requirements** | FR-4610 (White Cell's own god-view/view-as consumer — FEAT-4600) |
| **Dependencies** | FEAT-6100, FEAT-1500 |
| **Dependent Features** | FEAT-4600, FEAT-6500, FEAT-7400, FEAT-8200; FEAT-2300, FEAT-7300 *(sweep 2026-10-17)*; FEAT-8100, FEAT-12200 *(sweep 2026-10-23)* |
| **Affected Subsystems** | C2 Session/Application Layer, C1 Simulation Engine |
| **Affected Interfaces** | INT-0006, INT-0007, INT-0001, INT-0005 |
| **Related ADRs** | ADR-0004, ADR-0015 |
| **User Value** | "Operate on belief, not ground truth" — the single most important pedagogical property of the whole simulator, structurally guaranteed rather than UI-disciplined. |
| **Technical Value** | Survives any future front-end replacement, since the guarantee lives at the boundary, not in `ui_web/`. |
| **Complexity** | High. |
| **Risk** | The named ground-truth exception set is also the documented v1 LAN trust boundary — a hostile LAN participant can read another cell's belief state by naming that cell in a URL (ADR-0015, `CLAUDE.md`); this is an accepted, documented v1 risk, not a defect of this Feature, but it is the correct place to flag it for any future hardening pass. |
| **Suggested Verification Strategy** | Red/Blue with disjoint custody: a Blue `CellView` request never includes a Red-only Track Blue has no custody of; a static review confirms the ground-truth exception applies only to the named endpoint set. |
| **Open Questions** | Per-cell token hardening (CNFR-04/CR-02) is a tracked future-work item, not part of this Feature's baseline scope. |

### FEAT-6300 — Server-Authoritative Lazy Clock & Mutation Locking

| Field | Content |
|---|---|
| **Feature ID** | FEAT-6300 |
| **Title** | Server-Authoritative Lazy Clock & Mutation Locking |
| **Purpose** | Advance a session's clock exactly once per real interval regardless of connected client count, and serialize concurrent mutations so no interleaved partial update is ever observable. |
| **Description** | Uses a server-authoritative lazy-catch-up clock (not a per-client clock) so simultaneous readers observe one consistent timeline; serializes all mutating operations against a session with a per-session lock. |
| **Scope** | The multiplayer clock and locking mechanism. Sharing one Session object across hot-seat/LAN modes is FEAT-6400 (a dependent). |
| **Included Requirements** | FR-6310, FR-6320, NFR-1400 |
| **Excluded Requirements** | FR-6410 (hot-seat/LAN mode sharing — FEAT-6400) |
| **Dependencies** | FEAT-1100 |
| **Dependent Features** | FEAT-6400 |
| **Affected Subsystems** | C2 Session/Application Layer |
| **Affected Interfaces** | INT-0001, INT-0006 |
| **Related ADRs** | ADR-0014, ADR-0026 |
| **User Value** | Makes LAN-cooperative play actually consistent — every connected participant sees the same simulated time and no lost updates from concurrent action submission. |
| **Technical Value** | This Feature — plus FEAT-6400 — is the entirety of what the codebase calls "P8 LAN multiplayer transport," currently undifferentiated inside the existing `FS-106-white-cell-dashboard.md` document despite carrying two dedicated ADRs of its own (ADR-0014, ADR-0026); flagged in `05-feature-review.md` as a strong candidate for its own Feature Specification. |
| **Complexity** | High. |
| **Risk** | ADR-0026 explicitly records the ~16-participant concurrency ceiling as a documented estimate, not a load-tested guarantee (NFR-1400) — a known, accepted limitation. |
| **Suggested Verification Strategy** | Two simulated clients polling concurrently observe an identical simulated clock value within the same catch-up cycle; two concurrent order submissions against the same asset apply sequentially with no lost update. |
| **Open Questions** | None beyond the documented NFR-1400 ceiling. |

### FEAT-6400 — Hot-Seat & LAN-Cooperative Session Sharing

| Field | Content |
|---|---|
| **Feature ID** | FEAT-6400 |
| **Title** | Hot-Seat & LAN-Cooperative Session Sharing |
| **Purpose** | Serve both single-browser hot-seat play and multi-tab/multi-machine LAN play from the same underlying Session object, differing only in client count. |
| **Description** | One Session model serves both modes; the same sequence of operator actions produces identical `WorldState` whether issued via one hot-seat browser or several LAN-connected browsers. |
| **Scope** | Session-sharing semantics across modes. The screen-blank hand-off UX between hot-seat role changes is FEAT-6600 (a dependent). |
| **Included Requirements** | FR-6410 |
| **Excluded Requirements** | FR-6610 (hot-seat hand-off screen-blank — FEAT-6600) |
| **Dependencies** | FEAT-6300 |
| **Dependent Features** | FEAT-6600 |
| **Affected Subsystems** | C2 Session/Application Layer |
| **Affected Interfaces** | INT-0001, INT-0006 |
| **Related ADRs** | ADR-0014 |
| **User Value** | The same tool serves a single-laptop classroom and a multi-machine LAN room without behavioral surprises. |
| **Technical Value** | One session model, not two, halves the maintenance surface for a defect class ("does mode X behave differently from mode Y"). |
| **Complexity** | Medium. |
| **Risk** | Low; part of the same undifferentiated FS-106 bucket noted under FEAT-6300. |
| **Suggested Verification Strategy** | The same action sequence via single-hot-seat vs. multi-LAN-client produces an identical resulting `WorldState`. |
| **Open Questions** | None. |

### FEAT-6500 — Observer Read-Only Access

| Field | Content |
|---|---|
| **Feature ID** | FEAT-6500 |
| **Title** | Observer Read-Only Access |
| **Purpose** | Give an Observer seat a White-Cell-designated read-only view (god-view or a specific cell's view) with no command authority whatsoever. |
| **Description** | Serves the designated view read-only; rejects any mutating request from an Observer-seated session with no `WorldState` change. |
| **Scope** | Observer view designation and the read-only enforcement. |
| **Included Requirements** | FR-6510 |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-6200 |
| **Dependent Features** | None |
| **Affected Subsystems** | C4 Operator Console, C9 Observer |
| **Affected Interfaces** | INT-0005, INT-0006 |
| **Related ADRs** | ADR-0004 |
| **User Value** | Observers are an explicit assessment/learning role (instructors, evaluators, additional trainees) distinct from either cell — this is their entire interaction model. |
| **Technical Value** | Reuses FEAT-6200's filter rather than a bespoke Observer-only path. |
| **Complexity** | Low-Medium. |
| **Risk** | **This Feature has zero mentions anywhere in the existing 11 `FS-xxx` documents and its RTM Impl. Package is `UNASSIGNED`** — one of the two capabilities this catalog's motivating audit specifically identified as undocumented. See `05-feature-review.md`. |
| **Suggested Verification Strategy** | An Observer-seated session attempting to submit a command has the request rejected with no `WorldState` change. |
| **Open Questions** | Confirm build status against `ui_web/server.py`/`session/` directly; author the missing Feature Specification; CR-06 (mid-exercise Observer reassignment) is a related, separately-tracked open question. |

### FEAT-6600 — Hot-Seat Hand-Off Screen-Blank Menu

| Field | Content |
|---|---|
| **Feature ID** | FEAT-6600 |
| **Title** | Hot-Seat Hand-Off Screen-Blank Menu |
| **Purpose** | Blank a departing operator's sensitive belief-state content during a pending hot-seat role change, so the next person at the keyboard never sees it. |
| **Description** | On a pending hot-seat hand-off, blanks the previously displayed cell's content and presents a seat-selection menu until a new seat is selected; no prior cell's content remains visible in the interim. |
| **Scope** | The blank/hand-off menu behavior itself. |
| **Included Requirements** | FR-6610 |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-6400 |
| **Dependent Features** | None |
| **Affected Subsystems** | C4 Operator Console, C2 Session/Application Layer |
| **Affected Interfaces** | INT-0001, INT-0006 |
| **Related ADRs** | ADR-0004 |
| **User Value** | Prevents a genuine fog-of-war leak at the physical hot-seat hand-off moment — the one place a belief-state boundary is enforced by screen content, not server filtering, and therefore the one place this catalog's Feature-level reasoning must note the exception explicitly. |
| **Technical Value** | Closes GDS-05's own previously-open Open Question 1 (OQ1) — this leaf was added specifically because no prior FR leaf covered hand-off blanking. |
| **Complexity** | Low-Medium (UI behavior), but sits at the end of this catalog's longest dependency chain (see `04-feature-dependency-graph.md`). |
| **Risk** | **This Feature has zero mentions anywhere in the existing 11 `FS-xxx` documents and its RTM Impl. Package is `UNASSIGNED`** — the second of the two capabilities this catalog's motivating audit specifically identified as undocumented. See `05-feature-review.md`. |
| **Suggested Verification Strategy** | A hot-seat hand-off from Red to Blue on the same browser leaves no Red-cell data visible once the hand-off menu appears, and none reappears until a seat is explicitly selected. |
| **Open Questions** | Confirm build status directly; author the missing Feature Specification. |

---

## Epic EP-7000 — Logging, Replay & After-Action Review

### FEAT-7100 — Ordered Event Log

| Field | Content |
|---|---|
| **Feature ID** | FEAT-7100 |
| **Title** | Ordered Event Log |
| **Purpose** | Append every state-changing event to an ordered, timestamped log sufficient to deterministically reconstruct the exercise. |
| **Description** | Appends orders, executions, effects, injects, White-Cell controls, and time controls to an `EventLogEntry` sequence; combined with initial state and seed, sufficient to reproduce the exercise exactly. |
| **Scope** | The log's own append/ordering mechanism. The determinism guarantee that reconstructs state *from* the log is FEAT-1100 (a dependent, not this Feature's own scope). |
| **Included Requirements** | FR-7110, NFR-2500, NFR-2600 |
| **Excluded Requirements** | FR-1120 (determinism/replay guarantee — FEAT-1100) |
| **Dependencies** | None |
| **Dependent Features** | FEAT-1100, FEAT-7200, FEAT-7300, FEAT-7400; FEAT-1300, FEAT-3400 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C1 Simulation Engine |
| **Affected Interfaces** | INT-0008, INT-0014 |
| **Related ADRs** | ADR-0002 |
| **User Value** | The evidence base White Cell adjudicates from (per manual-adjudication, FEAT-4700) — with no automated scoring, this log is the only record. |
| **Technical Value** | Foundational to three dependents (determinism, save/resume, AAR) — the second-most depended-on Feature in the catalog. |
| **Complexity** | Medium. |
| **Risk** | A found circular citation with FEAT-1100 (FR-7110's own "Dependencies: FR-1120") is resolved here by treating this Feature as the more primitive one (an append-only log does not itself require a determinism proof to exist) — see `04-feature-dependency-graph.md`. |
| **Suggested Verification Strategy** | Replaying a completed exercise's event log from its initial state reproduces a `WorldState` history identical to the one recorded live. |
| **Open Questions** | See FEAT-1100's Open Questions for the resolved circular-dependency note. |

### FEAT-7200 — Deterministic Save/Resume & Content-Session Split

| Field | Content |
|---|---|
| **Feature ID** | FEAT-7200 |
| **Title** | Deterministic Save/Resume & Content-Session Split |
| **Purpose** | Persist a complete session snapshot and reproduce it exactly on resume, with the save file's content portion independently extractable from its session/event-log portion. |
| **Description** | Saves `WorldState`, full `EventLog`, Snapshots, and Role Assignments on demand or at exercise end; a resumed session is identical to the pre-save state; the Vignette/content portion of a save file can be loaded as a fresh vignette independent of that save's own session history. |
| **Scope** | Save/resume round-trip and the content/session ownership split within one save file. |
| **Included Requirements** | FR-7210, FR-7220, NFR-1800, FR-7230 *(sweep 2026-10-23, run #212)* |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-7100 |
| **Dependent Features** | FEAT-5500 *(sweep 2026-10-17)* |
| **Affected Subsystems** | C2 Session/Application Layer, C5 Content & Data, C11 Local filesystem (external) |
| **Affected Interfaces** | INT-0011, INT-0012 |
| **Related ADRs** | ADR-0022 |
| **User Value** | Multi-sitting exercises are possible at all only because of this Feature. |
| **Technical Value** | This Feature — along with the multiplayer transport (FEAT-6300/6400) and AI-Red (FEAT-9100) — is currently undifferentiated inside the existing `FS-106-white-cell-dashboard.md` catch-all document despite carrying its own dedicated ADR (ADR-0022) and its own ICD issue closure (§7 issue 4); flagged in `05-feature-review.md` as a candidate for its own Feature Specification. |
| **Complexity** | Medium-High. |
| **Risk** | FR-7220 is **not met as built** (requirements review R2): a save carries only the vignette ID and parameter overrides (GDS-07 §6), so its content portion is not extractable on its own. FR-7230 (owner decision `BL-0302`: the save carries its active scenario regardless of the original vignette file) closes FR-7220 too — the specification should say how. |
| **Suggested Verification Strategy** | A session saved at sim time T and immediately resumed is identical to the pre-save state at T; a save file's content portion loads as a fresh vignette's starting state independent of that save's event-log history; a save resumes after its original vignette file is edited or removed (FR-7230). |
| **Open Questions** | CR-08 (cross-version save compatibility) is a related, separately-tracked open question, out of this Feature's baseline scope (same-build round trips only). |

### FEAT-7300 — AAR Replay, Scrub & Branch-Compare

| Field | Content |
|---|---|
| **Feature ID** | FEAT-7300 |
| **Title** | AAR Replay, Scrub & Branch-Compare |
| **Purpose** | Let White Cell (and designated Observers) replay/scrub the event log read-only, and compare two diverging branches from a common rewind point, without disturbing the live session. |
| **Description** | Reconstructs `WorldState` at any scrubbed-to point for display only, never altering the live session; compares two branches sharing a common ancestor without altering either's underlying log. |
| **Scope** | Replay/scrub/branch-compare mechanics. |
| **Included Requirements** | FR-7310, FR-7320, FR-7330 *(sweep 2026-10-17, run #151)* |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-7100; FEAT-6200 *(FR-7330: a single-cell replay is fog-filtered)* |
| **Dependent Features** | FEAT-10100 |
| **Affected Subsystems** | C2 Session/Application Layer, C1 Simulation Engine |
| **Affected Interfaces** | INT-0014 |
| **Related ADRs** | ADR-0002 |
| **User Value** | The core after-action learning instrument — trainees and facilitators see exactly how a decision changed the outcome. |
| **Technical Value** | Purely additive over the event log; read-only by construction, so it cannot itself introduce a determinism regression. |
| **Complexity** | Medium-High. |
| **Risk** | Low; well-covered (`session/aar.py`, `test_aar.py` per `CLAUDE.md`'s code map). |
| **Suggested Verification Strategy** | Scrubbing to `T-100s` from a live session at T does not change the live session's clock/state; two branches diverging at T each correctly attribute their own post-T state. |
| **Open Questions** | None. |

### FEAT-7400 — State-Vector/Ephemeris & TLE Export

| Field | Content |
|---|---|
| **Feature ID** | FEAT-7400 |
| **Title** | State-Vector/Ephemeris & TLE Export |
| **Purpose** | Let White Cell (truth) and any cell (its own belief) export orbital state out of the simulator for use in external tools — as time-span state vectors (ECI/RIC, CSV/CCSDS-OEM) and, separately, as a quick current-epoch TLE for any satellite the requesting cell can currently see. |
| **Description** | Exports ground-truth and cell-observed state vectors over a time span in ECI and RIC-relative form, as CSV, CCSDS OEM (ECI only), and a dedicated RIC-only companion file; separately, exports a current two-line element set for any satellite the requesting cell holds a `Track` on, as a copyable/clipboard string (added `FR-7440`, 2026-10-03). Every cell-scoped export path is fog-of-war-filtered; the truth export rides only the existing no-cell ground-truth endpoints. |
| **Scope** | The export mechanisms themselves (serialization + the fog-of-war/no-cell-endpoint rule they follow). Does not cover the underlying RIC-transform math (`engine/maneuver.py::lvlh_frame`, a shared utility, not owned by any one Feature) or the fog-of-war filter itself (FEAT-6200, a dependency). |
| **Included Requirements** | FR-7410, FR-7420, FR-7430, FR-7440 |
| **Excluded Requirements** | FR-6210/FR-6220 (the fog-of-war filter and its no-cell exception these all ride — FEAT-6200) |
| **Dependencies** | FEAT-7100, FEAT-6200 |
| **Dependent Features** | None |
| **Affected Subsystems** | C2 Session/Application Layer, C1 Simulation Engine, C3 Mock SSN |
| **Affected Interfaces** | INT-0014, INT-0007, INT-0006 |
| **Related ADRs** | ADR-0004, ADR-0015, ADR-0013 |
| **User Value** | Lets an operator or analyst take orbital state out of the simulator into real external orbital-mechanics tooling (STK, GMAT, a spreadsheet) for further analysis — the ECI/RIC export for rigorous state-vector work, the quick TLE export for anything that consumes two-line elements directly. |
| **Technical Value** | All four leaves reuse the same underlying RIC-transform (`to_ric()`/`lvlh_frame()`) and the same fog-of-war posture, rather than each inventing its own export convention. |
| **Complexity** | High (`FR-7410`/`FR-7420`/`FR-7430` — dual-format, dual-frame, truth-vs-cell-observed serialization); Medium (`FR-7440` — simpler output shape, but its Acceptance Criteria depend on resolving `BL-0110`'s mean-element-fit design question first). |
| **Risk** | `FR-7410`/`FR-7420`/`FR-7430` are `VERIFIED` built (`IP-1210`, per `VR-1210` v2.0). `FR-7440` (2026-10-03) is a brand-new, unimplemented leaf, and its own Notes field flags that generating a current-epoch TLE from an arbitrary propagated state is not a simple format conversion (`BL-0110`) — a real implementation-shape decision a future `06`/`07` pass must make before this leaf can be built. This Feature is **partially built**, not uniformly at one maturity level. |
| **Suggested Verification Strategy** | Per-leaf acceptance criteria already stated in each FR; for `FR-7440` specifically, given a cell holding a `Track` on satellite X, a TLE-export request for X returns a well-formed TLE, and the same request for an untracked satellite Y is rejected. |
| **Open Questions** | This Feature bundles one brand-new FR (`FR-7440`, this run's own scope) together with three pre-existing, already-`VERIFIED` siblings (`FR-7410`-`FR-7430`) that predate this `05-feature-decomposition` run and had no Feature Catalog entry of their own before now — a pre-existing gap this Feature closes as a side effect, flagged explicitly rather than silently; see `05-feature-review.md`. `BL-0110`'s mean-element-fit design question remains open for `FR-7440` specifically. |

---

## Epic EP-8000 — Operator Console Presentation

### FEAT-8100 — Browser-Based Operator Console Presentation

| Field | Content |
|---|---|
| **Feature ID** | FEAT-8100 |
| **Title** | Browser-Based Operator Console Presentation |
| **Purpose** | Present all human-facing interaction through a browser client talking to a FastAPI server, making every documented capability reachable without a desktop GUI toolkit. |
| **Description** | Every user-facing capability in the baseline is reachable through a standards-compliant browser session against the running server; no interaction path requires a non-browser client. |
| **Scope** | The presentation-layer choice and its cross-cutting quality attributes (performance, hardware floor, accessibility, portability, configuration, external-integration boundary). Does not include any specific screen's business logic (owned by the Feature the screen exposes). |
| **Included Requirements** | FR-8110, NFR-1100, NFR-1200, NFR-2700, NFR-2900, NFR-3000, NFR-3300, NFR-3010, NFR-3020, NFR-3030, NFR-3040, NFR-3050 *(sweep 2026-10-23, run #212)* |
| **Excluded Requirements** | None adjacent (this Feature intentionally absorbs the UI-wide cross-cutting NFRs rather than splitting them across every screen-owning Feature). |
| **Dependencies** | FEAT-6200 (`NFR-3010` cites `FR-6210`), FEAT-1100 (`NFR-3020` cites `NFR-2410`) *(sweep 2026-10-23)* |
| **Dependent Features** | FEAT-8200; FEAT-12200 *(sweep 2026-10-23)* |
| **Affected Subsystems** | C4 Operator Console, C12 Browser client |
| **Affected Interfaces** | INT-0001 |
| **Related ADRs** | ADR-0008, ADR-0019, ADR-0020 |
| **User Value** | The entire trainee/facilitator experience is this Feature's surface — every other Feature's value is realized (or lost) through it. |
| **Technical Value** | Made the LAN-multiplayer seam (Epic EP-6000) "nearly free" by choosing browser-over-PyQt (ADR-0008) — a foundational architectural bet the rest of the catalog benefits from without depending on it structurally. |
| **Complexity** | High (a large hand-rolled, framework-free JS client per `CLAUDE.md`'s code map). |
| **Risk** | The strategic review (§1.4) flags framework-free JS as raising the cost of future UI-scale features (e.g. constellation aggregation, FC-06) — a noted future cost, not a current defect. |
| **Suggested Verification Strategy** | Every documented user-facing capability in the baseline is reachable through a standards-compliant browser session; interactive frame rates hold on reference hardware (16 GB RAM, integrated graphics) up to the sizing guideline. |
| **Open Questions** | None within baseline scope. |

### FEAT-8200 — Live RIC-Frame Relative-Motion View & CATS Overlay

| Field | Content |
|---|---|
| **Feature ID** | FEAT-8200 |
| **Title** | Live RIC-Frame Relative-Motion View & CATS Overlay |
| **Purpose** | Let an operator select a target satellite as the origin of a live, interactive RIC (Radial-In-track-Cross-track) relative-motion view, and, for a selected chase satellite within that view, see a live illumination phase-angle (CATS) readout predicting whether an optical sensor would get a usable view of the target. |
| **Description** | Renders other objects' position/motion live, relative to an operator-selected origin satellite, in the RIC frame, updating as the session clock advances and fog-of-war-filtered for a cell-scoped operator (`FR-8210`); when a chase/observer satellite is also selected, computes and displays the Sun-target-observer illumination phase angle for that pair as a live, read-only readout (`FR-8220`), extending `FR-8210` rather than standing alone. Distinct from the existing one-shot CSV/CCSDS-OEM RIC export (FEAT-7400), which is non-interactive and not rendered live. |
| **Scope** | The live, interactive view and its CATS overlay. Does not cover the underlying RIC-transform math (`engine/maneuver.py::lvlh_frame`, a shared utility) or the one-shot export format (FEAT-7400, a sibling, not a dependency — neither Feature requires the other to exist first). Does not cover using the same CATS angle as an access-window *gate* for sensor tasking generally (`FR-1670`, FEAT-1600, a distinct, broader-scope capability). |
| **Included Requirements** | FR-8210, FR-8220 |
| **Excluded Requirements** | FR-7410/FR-7420/FR-7430 (the one-shot export this reuses transform grounding from — FEAT-7400); FR-1670 (the CATS angle used as an access-gating criterion rather than a display readout — FEAT-1600); FR-6210 (the underlying fog-of-war filter — FEAT-6200) |
| **Dependencies** | FEAT-6200, FEAT-1200, FEAT-8100 |
| **Dependent Features** | None |
| **Affected Subsystems** | C4 Operator Console, C12 Browser client, C2 Session/Application Layer, C1 Simulation Engine |
| **Affected Interfaces** | INT-0001, INT-0006, INT-0007 |
| **Related ADRs** | ADR-0004, ADR-0008 |
| **User Value** | Direct Blue/Red RPO/proximity situational-awareness tool, and White Cell oversight aid — an operator reasoning about a chase satellite's relative geometry and lighting no longer has to mentally reconstruct the RIC frame from a raw ECI readout or a one-shot export file. |
| **Technical Value** | Reuses the already-implemented, already-tested RIC transform (`to_ric()`/`lvlh_frame()`, FEAT-7400's own underlying math) for a new, live rendering use, rather than a second implementation of the same geometry. |
| **Complexity** | High (`FR-8210` — a new live, interactive, fog-of-war-aware rendering surface); Low-Medium (`FR-8220` — one additional computed readout layered on `FR-8210`'s existing selection state). |
| **Risk** | Both leaves are brand-new and entirely unimplemented (RTM `UNASSIGNED` for both). `FR-8210` carries an open research gap on RIC-frame-display-as-operational-concept (`BL-0108`, no R1xx grounding exists yet, revisit before `06-feature-specification`). `FR-8220` carries an open research gap on the concrete default phase-angle range/degradation semantics (`BL-0112`/`BL-0151`) and a shared-computation note with `FR-1670` (`BL-0152`) that a future implementation should resolve by using one phase-angle function for both Features, not two. |
| **Suggested Verification Strategy** | Given an operator selecting satellite X as the RIC-frame origin, displayed relative positions match `to_ric()`-computed values at the current sim time, and update when a different origin is selected; given a cell-scoped request, rendered objects are limited to that cell's own `TrackCatalog`; given a selected chase/target pair, the displayed CATS angle matches the geometrically computed Sun-target-chaser angle to within floating-point tolerance. |
| **Open Questions** | Both `BL-0108` and `BL-0112`'s research gaps are correctly still open (their revisit trigger is before `06-feature-specification`, not before this decomposition) — flagged here so whoever specifies this Feature next knows to check their status first. |

---

## Epic EP-9000 — AI-Red

### FEAT-9100 — Doctrine-Preset-Driven AI-Red Automation

| Field | Content |
|---|---|
| **Feature ID** | FEAT-9100 |
| **Title** | Doctrine-Preset-Driven AI-Red Automation |
| **Purpose** | Substitute for an unseated Red cell by generating Planned Activities consistent with a configured doctrine preset, through the same path a human Red operator would use. |
| **Description** | When Red's seat is AI-Red-configured, generates Red-attributed Planned Activities per the selected preset (`russia_ew_first`, `china_integrated`, `generic`), indistinguishable in the event log from human-issued activities, and passing the same execute-time re-validation. |
| **Scope** | Doctrine-preset-driven activity generation for an unseated Red. Does not cover fog-of-war-parity for AI-Red's own reads (explicitly out of baseline scope — CR-01/CNFR-06, a tracked future-work gap, not part of this Feature). |
| **Included Requirements** | FR-9110, NFR-3060 *(sweep 2026-10-23, run #212)* |
| **Excluded Requirements** | CR-01/CNFR-06 (AI-Red fog-of-war parity — candidate, not baselined; see `05-feature-review.md`) |
| **Dependencies** | FEAT-3100, FEAT-3400 |
| **Dependent Features** | None |
| **Affected Subsystems** | C1 Simulation Engine, C8 Red Cell (AI-Red) |
| **Affected Interfaces** | INT-0008, INT-0015 |
| **Related ADRs** | ADR-0021, ADR-0024, ADR-0030 |
| **User Value** | Enables under-staffed exercises to run at all with a credible, doctrine-consistent opponent instead of no Red cell. |
| **Technical Value** | Reuses the human command path exactly (FEAT-3100/FEAT-3400) rather than a parallel, potentially-diverging execution path — this is also *why* AI-Red-issued activities are indistinguishable from human ones in the log. |
| **Complexity** | Medium-High. |
| **Risk** | **This is the strategic review's single highest-priority tracked gap (FC-02/GAP-08)** — AI-Red reads `WorldState` directly rather than through a fog-of-war-filtered `CellView` (ADR-0024, INT-0015), an accepted v1 asymmetry, not remediated here. It is also currently undifferentiated inside the existing `FS-106-white-cell-dashboard.md` catch-all despite having two dedicated ADRs (ADR-0021, ADR-0024) and its own module (`session/redai.py`) — flagged in `05-feature-review.md` as the strongest candidate in this catalog for its own Feature Specification. |
| **Suggested Verification Strategy** | Under the `china_integrated` preset, resulting Planned Activities are consistent with that doctrinal profile and pass the same execute-time re-validation (FEAT-3400) as a human-issued activity. |
| **Open Questions** | CR-01/CNFR-06 (fog-of-war parity) is the named future-work item that would close this Feature's largest known gap; not resolved by this catalog. |

---

## Epic EP-10000 — Assessment & Research Instrumentation *(new 2026-07)*

Added following `01-functional-requirements.md`'s `FR-10000` category (promoted from `CR-19`/`CR-20`
once `ADR-0032`/`ADR-0033` resolved their blocking conflicts) — an incremental catalog update per
this skill's own recommended usage ("re-run Step 0 against the delta... not a full regeneration"),
not a re-decomposition of the whole baseline.

### FEAT-10100 — Automated Non-Aggregating Competency Rubric Computation

| Field | Content |
|---|---|
| **Feature ID** | FEAT-10100 |
| **Title** | Automated Non-Aggregating Competency Rubric Computation |
| **Purpose** | Replace the engine's binary objective-flip signal with a richer, per-dimension qualitative measurement of how a cell demonstrated a vignette's intended competency, without ever collapsing dimensions into one score. |
| **Description** | Computes rubric-tier results (custody quality, window discipline, belief-truth divergence in the first iteration) per cell per exercise, read-only over existing eventlog/custody/order-log/AAR-snapshot state; never aggregates into a composite score or win/loss determination. |
| **Scope** | The computation and its non-aggregation guarantee. Does not cover rubric-tier *authoring* tooling (a separate, unauthorized candidate — `FS-202`) or the facilitator's own qualitative judgment mode (DOM-002 §6's "facilitator rubric," which requires no new engine feature). |
| **Included Requirements** | FR-10110 |
| **Excluded Requirements** | FR-4710 (the sibling "no automated score/win-loss" prohibition this Feature must not cross — owned by FEAT-4700) |
| **Dependencies** | FEAT-1500 (custody), FEAT-3400 (execute-time re-validation/rejection data), FEAT-7300 (AAR snapshot diff) |
| **Dependent Features** | FEAT-10200 |
| **Affected Subsystems** | C1 Simulation Engine, C2 Session/Application Layer |
| **Affected Interfaces** | None — no ICD interface currently names this boundary (FS-201's own Open Questions flag the same gap) |
| **Related ADRs** | ADR-0017, ADR-0032 |
| **User Value** | Gives a facilitator a richer debrief instrument than "did the cell win," and a trainer a longitudinal per-trainee competency signal. |
| **Technical Value** | A read-only analytics layer reusing custody/order/AAR data other Features already produce, rather than a parallel measurement path. |
| **Complexity** | Medium-High — three independently-derived dimensions, each with its own data source and tier scale. |
| **Risk** | Was blocked on a direct conflict with `ADR-0017` until `ADR-0032`'s narrow carve-out (2026-07); any future extension that aggregates dimensions into one number falls back outside that carve-out and would need its own ADR. |
| **Suggested Verification Strategy** | Given a completed exercise, the report presents rubric-tier results for the three first-iteration dimensions side-by-side per cell without collapsing them into one number; the computation produces zero `WorldState` mutations. |
| **Open Questions** | Whether the rubric-tier result record needs a new Domain Model entity or extends `EventLog`/`SavedSession` is unresolved (FS-201's own Open Questions). |

### FEAT-10200 — Multi-Run/Cohort Structured Research-Data Export

| Field | Content |
|---|---|
| **Feature ID** | FEAT-10200 |
| **Title** | Multi-Run/Cohort Structured Research-Data Export |
| **Purpose** | Let a researcher batch-run N seeded simulations of a vignette and export structured, condition-labeled per-run records, closing the gap that today requires scripting directly against raw `eventlog`/`save` artifacts. |
| **Description** | Exports one structured record per seeded run (vignette ID, seed, condition label, `FEAT-10100` rubric-tier output), without relaxing engine determinism to characterize run-to-run variability. |
| **Scope** | The batch-run/export mechanism. Does not cover statistical analysis of the exported data (the researcher's own responsibility) or any human-subjects-research feature (explicitly out of scope — `CR-21`, unaffected by this Feature). |
| **Included Requirements** | FR-10210 |
| **Excluded Requirements** | None adjacent. |
| **Dependencies** | FEAT-10100, `FEAT-1100` (Deterministic Clock — replay/reproducibility) |
| **Dependent Features** | None |
| **Affected Subsystems** | C1 Simulation Engine, C2 Session/Application Layer |
| **Affected Interfaces** | None — no ICD interface currently names this export boundary (FS-301's own Open Questions flag the same gap) |
| **Related ADRs** | ADR-0029 (superseded), ADR-0033 |
| **User Value** | Turns the platform into a usable instrument-grade research tool without requiring a researcher to script against raw artifacts. |
| **Technical Value** | Reuses `FEAT-10100`'s per-run output and the engine's existing seeded-replay determinism rather than a parallel measurement or replay path. |
| **Complexity** | Medium. |
| **Risk** | Was blocked on a direct conflict with `ADR-0029` (which had explicitly considered and rejected this exact capability) until `ADR-0033` superseded it (2026-07) — the first ADR reversal, not merely a narrowing, in this catalog's history. |
| **Suggested Verification Strategy** | Given a batch of N seeded runs of the same vignette, the exported record set contains exactly N entries, each tagged with its own seed/vignette-ID/condition label; re-running the same seed reproduces byte-identical underlying state. |
| **Open Questions** | The exact export record schema is implied but not formally specified (FS-301's own Open Questions); whether it requires a new Domain Model entity is unresolved. |

---

## Epic EP-11000 — Training Corpus & Learning Path *(new 2026-10-17, run #151 sweep)*

Added for `01-functional-requirements.md`'s `FR-11000` family (training-corpus elevation, 2026-07-04),
which no earlier pass of this catalog decomposed (`BL-0153`).

### FEAT-11100 — Role-Scoped, Source-Anchored, Current Operator Manuals *(sweep 2026-10-17, run #151)*

| Field | Content |
|---|---|
| **Feature ID** | FEAT-11100 |
| **Title** | Role-Scoped, Source-Anchored, Current Operator Manuals *(sweep 2026-10-17, run #151)* |
| **Purpose** | Give every seat a manual that covers what that role does, says where each claim comes from, and stays true as the code changes (MSTR-001 §2 training-corpus elevation). |
| **Description** | Role-scoped manual coverage per seat; a `Sources:` anchor per section; a bidirectional feature ⇄ manual index; manual updates riding the package that changes the behaviour; as-built-only accuracy; modular, learner-appropriate modules. |
| **Scope** | The manuals and their traceability apparatus. The vignette learning path is FEAT-11300. |
| **Included Requirements** | FR-11110, FR-11120, FR-11210, FR-11410, NFR-3400, NFR-3500, NFR-3600 |
| **Excluded Requirements** | FR-11310/FR-11320/FR-11420 (learning path and playbook verification — FEAT-11300) |
| **Dependencies** | None at Feature grain — it documents whatever has shipped; each manual section depends on the Feature it describes, tracked by `training/15`, not by graph edges |
| **Dependent Features** | FEAT-11300; FEAT-12300 *(sweep 2026-10-23)* |
| **Affected Subsystems** | None in the C1–C12 component set — the training corpus (`docs/training/`) is not an ICD component (see `05-feature-review.md` F-16) |
| **Affected Interfaces** | None — documentation artifact |
| **Related ADRs** | None identified (governed by MSTR-001 §2 and GDS-00/GDS-01 "Training-corpus elevation") |
| **User Value** | A trainee or facilitator can learn the tool from its manual without a developer in the room (FR-11110 Rationale). |
| **Technical Value** | The index makes manual impact of a code change mechanically findable. |
| **Complexity** | Medium — breadth, not depth. |
| **Risk** | Drift between prose and behaviour; mitigated by FR-11410 and independent `09-training-manual-review` passes. |
| **Suggested Verification Strategy** | Inspection: each seat has role-scoped coverage; every section has a `Sources:` footer; the matrix agrees in both directions; a sampled feature change updated its mapped sections. |
| **Open Questions** | None within baseline scope. |

### FEAT-11300 — Vignette Learning Path & Verified Playbooks *(sweep 2026-10-17, run #151)*

| Field | Content |
|---|---|
| **Feature ID** | FEAT-11300 |
| **Title** | Vignette Learning Path & Verified Playbooks *(sweep 2026-10-17, run #151)* |
| **Purpose** | Sequence the vignette library into a progression, link each rung to the manual sections it assumes, and prove each playbook's moves actually work. |
| **Description** | A rung ladder over the shipped vignettes, each rung naming its manual prerequisites and verified playbook; playbook objective-flips are machine-verified. |
| **Scope** | The learning path and playbook verification. |
| **Included Requirements** | FR-11310, FR-11320, FR-11420 |
| **Excluded Requirements** | FR-11110/FR-11210 (manuals and index — FEAT-11100) |
| **Dependencies** | FEAT-11100 (FR-11320 links manual sections), FEAT-4100 (the vignette library it sequences, FR-11310/FR-11420's "FR-5000 family") |
| **Dependent Features** | None |
| **Affected Subsystems** | C5 Content & Data (vignette tutorial blocks); otherwise documentation (F-16) |
| **Affected Interfaces** | None |
| **Related ADRs** | None identified |
| **User Value** | Trainees meet concepts in an order that builds (FR-11310 Rationale). |
| **Technical Value** | `test_vignette_tutorials.py` turns playbook drift into a failing test. |
| **Complexity** | Medium. |
| **Risk** | Engine changes that break a playbook; caught by FR-11420's test. |
| **Suggested Verification Strategy** | Each rung names prerequisites that exist; `test_vignette_tutorials.py` passes. |
| **Open Questions** | None within baseline scope. |


## Epic EP-12000 — Verification & Documentation Integrity *(new 2026-10-23, run #212 sweep)*

Added for the verification and documentation-integrity leaves `04` baselined in run #211
(`NFR-1510`, `NFR-2820`–`NFR-2840`, `NFR-3800`–`NFR-3840`). They constrain how the product is
verified, released and documented rather than what it does for a cell, so no product Feature owns
them naturally (see `05-feature-review.md` F-22).

### FEAT-12100 — Test-Origin Traceability & Major-Release Verification *(sweep 2026-10-23, run #212)*

| Field | Content |
|---|---|
| **Feature ID** | FEAT-12100 |
| **Title** | Test-Origin Traceability & Major-Release Verification *(sweep 2026-10-23, run #212)* |
| **Purpose** | Make every test say what it verifies, so the traceability matrix's Test column is read rather than inferred, and give each major release a relevance audit and a reproducible dependency set (owner directions `BL-0310`, `BL-0299`). |
| **Description** | Every test declares its origin (requirement leaf, else feature specification, else package) in a machine-readable marker; every declared ID resolves to a live baseline item; at each major release the suite is audited for unmarked, orphaned and duplicate tests and for in-scope requirements with no test, and the release ships with every dependency locked to an exact version. |
| **Scope** | The marker convention and its registration, the backfill of the existing suite, the resolution check, the major-release audit and the dependency lock. The audit's and lock's execution belongs to `11-release-readiness`; this Feature supplies what they check. |
| **Included Requirements** | NFR-1510, NFR-2820, NFR-2830, NFR-3840, NFR-2850 *(2026-10-23, `BL-0322`)* |
| **Excluded Requirements** | NFR-2840 (browser suite — FEAT-12200); NFR-3800–NFR-3830 (documentation integrity — FEAT-12300); NFR-1900 (engine test coverage and import guard — FEAT-1100) |
| **Dependencies** | FEAT-1100, FEAT-5300 (`NFR-1510` cites `NFR-1500` and `NFR-2200`) |
| **Dependent Features** | None (the browser suite's tests will carry the marker, but no leaf there cites a leaf here) |
| **Affected Subsystems** | None in C1–C12 — `spacesim/tests/` and `pyproject.toml` (test and build configuration, not an ICD component; see F-16) |
| **Affected Interfaces** | None |
| **Related ADRs** | None identified |
| **User Value** | Indirect — a reviewer can see which requirement each test protects, and a release can show which requirements have none (`NFR-2820` Rationale). |
| **Technical Value** | Closes GDS-10 finding F3 (test traceability by inference) and lets `04` fill the RTM Test column mechanically. |
| **Complexity** | Medium — mechanical, but the backfill touches every test module and needs a judgment per test about its origin. |
| **Risk** | A backfill that tags by file name rather than by what a test asserts would reproduce the inference it replaces; mitigated by `09` checking new tags and the major-release audit. |
| **Suggested Verification Strategy** | Collecting the suite lists a `verifies` origin for every test; every declared ID resolves; `--strict-markers` passes; a deliberately unknown ID fails the resolution check. |
| **Open Questions** | Whether the resolution check (NFR-3840) runs in the default suite or a separate documentation-check run — the same question FEAT-12300 raises. |

### FEAT-12200 — Automated Browser Verification of Load-Bearing Console Rules *(sweep 2026-10-23, run #212)*

| Field | Content |
|---|---|
| **Feature ID** | FEAT-12200 |
| **Title** | Automated Browser Verification of Load-Bearing Console Rules *(sweep 2026-10-23, run #212)* |
| **Purpose** | Verify in a real browser what the backend tests cannot: what the console actually shows (owner decision `BL-0304`). |
| **Description** | A small headless-browser suite drives the shipped console and asserts that a cell seat never renders ground truth for objects outside its custody, that a refused command is shown disabled with its reason before issue, and that kinetic and cyber orders require a consequence confirmation. |
| **Scope** | The three rules NFR-2840 names, the browser tooling, and how the suite is run. Not a general UI regression suite. |
| **Included Requirements** | NFR-2840 |
| **Excluded Requirements** | NFR-3010/NFR-3020 (the console rules themselves — FEAT-8100); FR-6210 (fog-of-war filtering — FEAT-6200) |
| **Dependencies** | FEAT-8100 (the rules it checks: `NFR-3010`, `NFR-3020`), FEAT-6200 (the filtered views it renders: `FR-6210`) |
| **Dependent Features** | None |
| **Affected Subsystems** | C12 Browser client, C4 Operator Console |
| **Affected Interfaces** | INT-0002 (the HTTP surface the suite drives) |
| **Related ADRs** | ADR-0004, ADR-0008 |
| **User Value** | The training value of fog-of-war and plan-first depends on what the trainee sees; today that is unverified (GDS-08 "Verification status"). |
| **Technical Value** | First automated check of the browser client; turns console regressions on the three rules into failing tests. |
| **Complexity** | Medium — the tooling is new to the test environment (requirements review R7); the assertions themselves are few. |
| **Risk** | Headless-browser tests are slower and more brittle than backend tests; the specification must decide whether they run in the default suite. The tooling is not yet in the dependency list or the session hook (R7). |
| **Suggested Verification Strategy** | The suite runs headless in the test environment and fails when each rule is deliberately broken (a seeded ground-truth leak, a pre-enabled refused command, a removed confirmation). |
| **Open Questions** | Tooling choice and run mode (R7); whether the console-design "intentional friction" rule (`BL-0312`, review R6) belongs in the specification template — this is the first console-touching specification since it was deferred. |

### FEAT-12300 — Documentation Integrity Checks *(sweep 2026-10-23, run #212)*

| Field | Content |
|---|---|
| **Feature ID** | FEAT-12300 |
| **Title** | Documentation Integrity Checks *(sweep 2026-10-23, run #212)* |
| **Purpose** | Keep the live documentation tree honest as legacy content retires: links resolve, nothing live cites a retired document, indexes match their folders and status ledgers agree (owner direction on `BL-0297`). |
| **Description** | An automated check over the live documentation reports unresolved relative links, live references to retired documents, index/folder disagreement and disagreeing status ledgers; it runs as part of release verification. |
| **Scope** | The four documentation checks. The test-origin resolution check (NFR-3840) is FEAT-12100's, though both may share one runner. |
| **Included Requirements** | NFR-3800, NFR-3810, NFR-3820, NFR-3830 |
| **Excluded Requirements** | NFR-3840 (test origins resolve — FEAT-12100); NFR-3400–NFR-3600 (training-corpus quality — FEAT-11100) |
| **Dependencies** | FEAT-11100 (each leaf cites `NFR-3400`) |
| **Dependent Features** | None |
| **Affected Subsystems** | None in C1–C12 — documentation (F-16) |
| **Affected Interfaces** | None |
| **Related ADRs** | None identified |
| **User Value** | Indirect — readers stop following dead links and retired guidance. |
| **Technical Value** | Makes the build-spec/design retirement (`BL-0292`) safe to execute and checkable afterwards. |
| **Complexity** | Low-Medium. |
| **Risk** | The "retired document" list must be maintained; a check against a stale list passes falsely. |
| **Suggested Verification Strategy** | The check passes on the current tree after cleanup and fails on a seeded dead link, a seeded reference to a retired file, an index missing a file, and two ledgers disagreeing on one status. |
| **Open Questions** | Default suite or separate run (shared with FEAT-12100). |

---

## Summary

| Epic | Features | Count |
|---|---|---|
| EP-1000 Simulation Engine Core & Determinism | FEAT-1100–1600 | 6 |
| EP-2000 Bus & Payload Operations | FEAT-2100–2500 | 5 |
| EP-3000 Command Planning & Sensor Tasking | FEAT-3100–3500 | 5 |
| EP-4000 White Cell Exercise Control | FEAT-4100–4700 | 7 |
| EP-5000 Scenario / Vignette Authoring | FEAT-5100–5500 *(5400/5500 new 2026-10-17)* | 5 |
| EP-6000 Session, Multiplayer & Fog-of-War | FEAT-6100–6600 | 6 |
| EP-7000 Logging, Replay & AAR | FEAT-7100–7400 | 4 |
| EP-8000 Operator Console Presentation | FEAT-8100–8200 | 2 |
| EP-9000 AI-Red | FEAT-9100 | 1 |
| EP-10000 Assessment & Research Instrumentation *(new 2026-07)* | FEAT-10100–10200 | 2 |
| EP-11000 Training Corpus & Learning Path *(new 2026-10-17)* | FEAT-11100, FEAT-11300 | 2 |
| EP-12000 Verification & Documentation Integrity *(new 2026-10-23)* | FEAT-12100–12300 | 3 |
| **Total** | | **48** |

**As of the 2026-10-17 sweep (run #151, `BL-0153`), every baselined FR leaf (103) and every
baselined NFR leaf (28) in `docs/requirements/` is owned by exactly one Feature above** — checked
mechanically against the requirements documents' own leaf headings, with no leaf missing and none
included twice (see `05-feature-review.md` F-13). The Candidate Requirements (`CR-01`–`CR-18`,
`CR-21`–`CR-25`) and Candidate NFRs are deliberately **not** included in any Feature's `Included
Requirements` — they are not yet an approved baseline to decompose (see `05-feature-review.md` for
their disposition and what would be required to promote them).

**As of the 2026-10-23 sweep (run #212), every baselined FR leaf (106) and NFR leaf (47) is owned by
exactly one Feature** — re-checked mechanically the same way (`05-feature-review.md` F-21).
*(Delta 2026-10-23, `BL-0322`: `NFR-2850` joins FEAT-12100 — 48 NFR leaves; re-checked, F-27.)*
