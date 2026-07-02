# Requirements Traceability Matrix

This is the per-requirement traceability matrix for the baselined and candidate requirements in
[`01-functional-requirements.md`](01-functional-requirements.md) and
[`02-non-functional-requirements.md`](02-non-functional-requirements.md). It is distinct from
[`docs/architecture/10-requirements-traceability-matrix.md`](../architecture/10-requirements-traceability-matrix.md)
(GDS-10), which remains `⛔ Planned (scaffold only)` per `docs/architecture/INDEX.md` §1 and
contains no authored content — this document is not a substitute for GDS-10's eventual authoring,
it is the `docs/requirements/`-side deliverable the project owner requested directly.

## Method and discipline

Inputs read in full to build this matrix: the research encyclopedia index
([`docs/research/encyclopedia/`](../research/encyclopedia/INDEX.md)), the GDS architecture ladder
(`docs/architecture/00`–`05`), the ADR index
([`docs/architecture/adr/INDEX.md`](../architecture/adr/INDEX.md), ADR-0001–ADR-0031, all
`Accepted`), the Interface Control Document
([`docs/design/05-interface-control-document.md`](../design/05-interface-control-document.md)),
the [Strategic Assumptions Register](../architecture/strategic-assumptions-register.md), and both
requirements documents in full (every FR/NFR/Candidate leaf and its explicit fields).

> **Amended 2026-07** (strategic-review reconciliation) to add rows for `CR-12`–`CR-18` and
> `CNFR-07` and to update the ADR count above from `ADR-0029` to `ADR-0031`. No baselined FR/NFR row
> was added, removed, or altered. See
> [`reviews/requirements-update-report.md`](../reviews/requirements-update-report.md) for the full
> analysis and the "Strategic review reconciliation" section near the end of
> [`01-functional-requirements.md`](01-functional-requirements.md) and
> [`02-non-functional-requirements.md`](02-non-functional-requirements.md) for the corresponding
> sections in the two documents this matrix traces.
>
> **Further amended 2026-07** (DOM-002/004/005 backfill, closing `docs/feature-planning/
> 05-feature-review.md` Finding F-01) to add rows for `CR-19`–`CR-21` and to close the Impl. Package
> `UNASSIGNED` gap for `FR-4610`/`FR-4710`/`FR-4720` (via `IP-1060` v2.0) and `FR-7220` (via
> `IP-1100`), both split from `IP-1060` v1.0 per Finding F-03. No baselined FR/NFR row was added. See
> [`reviews/requirements-domain-backfill-report.md`](../reviews/requirements-domain-backfill-report.md)
> for the full analysis.

Every populated cell below is backed by an explicit, already-written field on the cited
requirement leaf (its own "Related ADRs," "Related Interfaces," "Source Documents," or
"Rationale" field), an explicit named correspondence in `CLAUDE.md`'s Code Map, or a verified
real file path (checked with `ls` against the actual `spacesim/` tree, not guessed from a class
or feature name). **`UNASSIGNED` is written wherever no such explicit evidence exists.** No cell
in this matrix is populated by inferring a connection from filename similarity, topical
resemblance, or "this probably implements/tests that." A heavily `UNASSIGNED` matrix is the
expected, correct state of a baseline whose test suite, future-work backlog, and traceability
ladder do not yet cite requirement IDs directly — it is evidence the matrix was not guessed.

Two structural facts drive most of the `UNASSIGNED` cells:

- **No test file anywhere in `spacesim/tests/` cites an FR-/NFR-/CNFR-/CR- ID directly** (verified
  by grep). The only two Test-column entries that are *not* `UNASSIGNED` are grounded in explicit
  `CLAUDE.md` prose or an explicit Metric field naming the test file, not in inference.
- **No FR-/NFR-/CNFR-/CR- ID is cited anywhere in `docs/FUTURE-WORK.md`** (verified by grep). The
  only Requirement → Future Feature entries that are *not* `UNASSIGNED` are FR-9110 and CNFR-06,
  both of which carry an explicit citation to `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity" in
  their own already-written fields.

Similarly, **no numbered FR/NFR leaf carries an encyclopedia (`R1xx`–`R5xx`) citation** anywhere
in GDS-01 through GDS-05 (verified by grep across all `docs/architecture/*.md`, excluding the
FR-/NFR- ID lines themselves, which found only one unrelated hit — a stakeholder-table row in
`00-vision.md` not tied to any requirement ID). The Research Source column is therefore
`UNASSIGNED` for the numbered baseline throughout; this is reported honestly rather than
backfilled with a plausible-looking encyclopedia ID.

## Architecture Component derivation (Interface → Component)

The Architecture Component column is derived mechanically from each requirement's own "Related
Interfaces" field, via the ICD §4 component list (C1–C12) and each interface's own ICD
description — never assigned independently of an explicit Related Interfaces citation.

| Interface | ICD description (abridged) | Architecture Component(s) |
|---|---|---|
| INT-0001 | Browser ↔ Operator Console | C4 Operator Console, C12 Browser client |
| INT-0002 | White Cell ↔ Console exercise control | C4 Operator Console, C6 White Cell |
| INT-0003 | White Cell ↔ Console scenario builder | C4 Operator Console, C6 White Cell, C5 Content & Data |
| INT-0004 | Blue/Red ↔ Console | C4 Operator Console, C7 Blue Cell, C8 Red Cell |
| INT-0005 | Observer ↔ Console | C4 Operator Console, C9 Observer |
| INT-0006 | Console → SessionAPI seam | C4 Operator Console, C2 Session/Application Layer |
| INT-0007 | CellController → Engine Custody | C2 Session/Application Layer, C1 Simulation Engine |
| INT-0008 | SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem | C2 Session/Application Layer, C1 Simulation Engine |
| INT-0009 | CellController/SessionAPI → Mock SSN | C2 Session/Application Layer, C3 Mock SSN |
| INT-0010 | Mock SSN → Engine delivery | C3 Mock SSN, C1 Simulation Engine |
| INT-0011 | SessionManager → Content & Data load | C2 Session/Application Layer, C5 Content & Data |
| INT-0012 | SessionManager → Content & Data / filesystem save | C2 Session/Application Layer, C5 Content & Data, C11 Local filesystem |
| INT-0013 | Content & Data → Space-Track TLE import | C5 Content & Data, C10 Space-Track.org |
| INT-0014 | AAR/Replay → Engine | C2 Session/Application Layer, C1 Simulation Engine |
| INT-0015 | AI-Red → Engine direct read | C8 Red Cell (or AI-Red), C1 Simulation Engine |
| INT-0016 | White Cell Inject → Engine direct mutation bypass | C6 White Cell, C1 Simulation Engine |

---

## Master matrix — Functional Requirements

Backward traces: Research Source · ADR · Architecture Component · Interface.
Forward traces: Future Feature · Test · Implementation Package.

| Req ID | Title (abridged) | Research | ADR | Arch. Component | Interface | Future Feature | Test | Impl. Package |
|---|---|---|---|---|---|---|---|---|
| FR-1110 | Single clock owner | UNASSIGNED | ADR-0016 | C2, C1 | INT-0002, INT-0008 | UNASSIGNED | UNASSIGNED | `engine/clock.py` |
| FR-1120 | Determinism (`(state, eventlog, seed) → byte-identical`) | UNASSIGNED | ADR-0002 | C2, C1 | INT-0008, INT-0014 | UNASSIGNED | `spacesim/tests/test_determinism.py` | `engine/simulation.py` |
| FR-1130 | (clock/scheduler leaf, ADR-0006) | UNASSIGNED | ADR-0006 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-1210 | (propagation seam, ADR-0009) | UNASSIGNED | ADR-0009 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/propagator.py` |
| FR-1220 | (access provider, ADR-0011) | UNASSIGNED | ADR-0011 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/access.py` |
| FR-1310 | Asset `resources.delta_v_ms` validation | UNASSIGNED | (none directly — restates GDS-04 §3) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/entities.py` |
| FR-1410 | Five-D effects resolution | UNASSIGNED | ADR-0012 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/effects.py` |
| FR-1420 | Cyber exception (non window-gated) | UNASSIGNED | ADR-0012 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/effects.py`, `engine/cyber.py` |
| FR-1510 | Custody/Track confidence decay | UNASSIGNED | ADR-0013 | C2, C1, C3 | INT-0007, INT-0010 | UNASSIGNED | UNASSIGNED | `engine/custody.py` |
| FR-1520 | Weapons-quality gate | UNASSIGNED | ADR-0013 | C2, C1 | INT-0007 | UNASSIGNED | UNASSIGNED | `engine/custody.py` |
| FR-2110 | Bus state model | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/bus.py` |
| FR-2210 | Payload state model | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/bus.py` |
| FR-2310 | Bus evolution / telemetry-contact / downlink handlers | UNASSIGNED | ADR-0004 | C2, C1 | INT-0007, INT-0008 | UNASSIGNED | UNASSIGNED | `engine/busmodel.py` |
| FR-2410 | Bus/payload command verbs | UNASSIGNED | (none directly) | C4, C7, C8, C2, C1 | INT-0004, INT-0008 | UNASSIGNED | UNASSIGNED | `engine/buscommands.py` |
| FR-2510 | Safe-mode / recovery chain | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/recovery.py` |
| FR-3110 | Plan-first command issuance | UNASSIGNED | ADR-0005 | C4, C7, C8, C2, C1 | INT-0004, INT-0006, INT-0008 | UNASSIGNED | UNASSIGNED | `engine/orders.py` |
| FR-3120 | Sensor tasking | UNASSIGNED | ADR-0005 | C4, C7, C8, C2 | INT-0004, INT-0006 | UNASSIGNED | UNASSIGNED | `engine/orders.py` |
| FR-3210 | SSN collection request | UNASSIGNED | ADR-0010 | C2, C3 | INT-0009 | UNASSIGNED | UNASSIGNED | `engine/ssn.py` |
| FR-3220 | SSN delivery | UNASSIGNED | ADR-0010 | C2, C3, C1 | INT-0009, INT-0010 | UNASSIGNED | UNASSIGNED | `engine/ssn.py` |
| FR-3310 | (order queue / cancel leaf) | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-3410 | (order delivery path leaf, ADR-0005/0013) | UNASSIGNED | ADR-0005, ADR-0013 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/orders.py` |
| FR-3510 | Role-Assignment command-filtering consequence | UNASSIGNED | ADR-0004 | C4, C7, C8 | INT-0004 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-3520 | Role-Assignment scoping (bus/payload/both) *(new leaf, CHG-002)* | UNASSIGNED | ADR-0004 | C4, C7, C8, C2 | INT-0004, INT-0006 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-4110 | White Cell exercise-control leaf | UNASSIGNED | (none directly) | C4, C6 | INT-0002 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-4210 | Seat-to-role assignment | UNASSIGNED | (none directly) | C4, C6 | INT-0002 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-4310 | Pause / resume clock control | UNASSIGNED | ADR-0016 | C4, C6 | INT-0002 | UNASSIGNED | UNASSIGNED | `session/manager.py` |
| FR-4410 | Inject authoring / firing | UNASSIGNED | ADR-0005 | C4, C6, C1 | INT-0002, INT-0016 | UNASSIGNED | UNASSIGNED | `session/manager.py` |
| FR-4510 | Observer view | UNASSIGNED | (none directly) | C4, C6, C12 | INT-0002, INT-0001 | UNASSIGNED | UNASSIGNED | `ui_web/server.py` |
| FR-4610 | (manual adjudication / custody-adjacent leaf, ADR-0004) | UNASSIGNED | ADR-0004 | C4, C6, C2, C1 | INT-0002, INT-0007 | UNASSIGNED | UNASSIGNED | `session/manager.py` *(closed 2026-07 via IP-1060 v2.0)* |
| FR-4710 | No automated scoring / manual adjudication | UNASSIGNED | ADR-0017, ADR-0029 | C4, C6 | (none — absence of an interface) | UNASSIGNED | UNASSIGNED | (inspection — no outbound interface returns a score field) *(closed 2026-07 via IP-1060 v2.0)* |
| FR-4720 | Adjust safe-mode dials / live parameters mid-exercise *(new leaf, CHG-003)* | UNASSIGNED | (none directly) | C4, C6 | INT-0002 | UNASSIGNED | UNASSIGNED | `session/manager.py` *(closed 2026-07 via IP-1060 v2.0)* |
| FR-5110 | Scenario builder | UNASSIGNED | ADR-0027 | C4, C6, C5 | INT-0003 | UNASSIGNED | UNASSIGNED | `content/vignette.py` |
| FR-5210 | TLE force-add import | UNASSIGNED | ADR-0018 | C5, C10 | INT-0013 | UNASSIGNED | UNASSIGNED | `content/` (TLE import) |
| FR-5310 | Vignette loading | UNASSIGNED | ADR-0007 | C2, C5 | INT-0011 | UNASSIGNED | UNASSIGNED | `content/vignette.py` |
| FR-6110 | SessionAPI seam (base) | UNASSIGNED | ADR-0002, ADR-0003 | C4, C2 | INT-0006 | UNASSIGNED | UNASSIGNED | `session/api.py` |
| FR-6210 | Fog-of-war filtering | UNASSIGNED | ADR-0004 | C4, C2, C1 | INT-0006, INT-0007 | UNASSIGNED | UNASSIGNED | `session/cells.py` |
| FR-6220 | Observer fog-of-war view | UNASSIGNED | ADR-0004, ADR-0015 | C4, C12, C9 | INT-0001, INT-0005 | UNASSIGNED | UNASSIGNED | `session/cells.py` |
| FR-6310 | Server-authoritative lazy clock | UNASSIGNED | ADR-0014, ADR-0026 | C4, C12, C2 | INT-0001, INT-0006 | UNASSIGNED | UNASSIGNED | `session/manager.py` |
| FR-6320 | Per-session RLock | UNASSIGNED | ADR-0014, ADR-0026 | C4, C2 | INT-0006 | UNASSIGNED | UNASSIGNED | `session/inprocess.py` |
| FR-6410 | Session discovery / join-by-hash | UNASSIGNED | ADR-0014 | C4, C12, C2 | INT-0001, INT-0006 | UNASSIGNED | UNASSIGNED | `session/inprocess.py` |
| FR-6510 | Multi-monitor pop-out windows | UNASSIGNED | ADR-0004 | C4, C9, C2 | INT-0005, INT-0006 | UNASSIGNED | UNASSIGNED | `ui_web/static/app.js` |
| FR-6610 | Hot-seat hand-off / screen-blank menu *(new leaf, CHG-004)* | UNASSIGNED | ADR-0004 | C4, C12, C2 | INT-0001, INT-0006 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-7110 | Event log | UNASSIGNED | ADR-0002 | C2, C1 | INT-0008, INT-0014 | UNASSIGNED | UNASSIGNED | `engine/eventlog.py` |
| FR-7210 | Save / resume | UNASSIGNED | ADR-0022 | C2, C5, C11 | INT-0012 | UNASSIGNED | UNASSIGNED | `session/manager.py` |
| FR-7220 | Save-file content/session ownership split *(new leaf, CHG-007)* | UNASSIGNED | ADR-0022 | C2, C5, C11 | INT-0011, INT-0012 | UNASSIGNED | UNASSIGNED | `session/manager.py` *(closed 2026-07 via IP-1100)* |
| FR-7310 | AAR replay/scrub | UNASSIGNED | ADR-0002 | C2, C1 | INT-0014 | UNASSIGNED | UNASSIGNED | `session/aar.py` |
| FR-7320 | AAR branch compare | UNASSIGNED | ADR-0002 | C2, C1 | INT-0014 | UNASSIGNED | UNASSIGNED | `session/aar.py` |
| FR-8110 | Operator console (web UI over the API) | UNASSIGNED | ADR-0008 | C4, C12 | INT-0001 | UNASSIGNED | UNASSIGNED | `ui_web/server.py`, `ui_web/static/` |
| FR-9110 | AI-Red substitution for unseated Red | UNASSIGNED | ADR-0021, ADR-0024 | C2, C1, C8 | INT-0008, INT-0015 | `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity" | UNASSIGNED | `session/redai.py` |

### Candidate Requirements (CR-01–CR-21) — `CANDIDATE — NOT BASELINED`

Per the `requirements-engineering` skill's own discipline, Candidates get rows but most
forward-trace columns are `UNASSIGNED` by definition (they describe unimplemented or
out-of-scope-for-v1 capabilities). Research/ADR columns reflect each Candidate's own explicit
"Source" field; nothing here is inferred. `CR-12`–`CR-18`, marked *(new 2026-07)*, follow
`strategic-review-2026-07.md`'s disposition — none has an ICD interface, and only `CR-18` cites an
ADR (`ADR-0031`, for the reasoning behind deferring its full treatment to DOM-005); the rest trace
to a not-built GDS-02/03/04 candidate component/concept instead, so Arch. Component/Interface are
`UNASSIGNED` rather than guessed against the C1–C12 list, consistent with `CR-04`/`CR-05` above.

| Req ID | Title (abridged) | Research | ADR | Arch. Component | Interface | Future Feature | Test | Impl. Package |
|---|---|---|---|---|---|---|---|---|
| CR-01 | AI-Red fog-of-war parity | UNASSIGNED | ADR-0024 | C8, C1 | INT-0015 | `FUTURE-WORK.md` §1 | UNASSIGNED | UNASSIGNED |
| CR-02 | Per-connection authentication | UNASSIGNED | ADR-0015 | C4, C12 | INT-0001 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-03 | Push-based delivery (vs. poll) | UNASSIGNED | (none cited) | C4, C12 | INT-0001 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-04 | Command-relationship layering | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-05 | Sustained degradation modeling | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-06 | Observer reassignment mid-exercise | UNASSIGNED | (none cited) | C4, C9 | INT-0005 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-07 | AI-Red preset guidance | UNASSIGNED | (none cited) | C8 | INT-0015 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-08 | Save-file cross-version compatibility | UNASSIGNED | (none cited) | C2, C5, C11 | INT-0012 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-09 | Unified PlannedActivity/SSNRequest supertype | UNASSIGNED | (none cited) | C2, C3, C1 | INT-0009, INT-0010 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-10 | AccessWindow persisted vs. derived | UNASSIGNED | (none cited) | C1 | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-11 | Partial vignette-authoring state ownership | UNASSIGNED | (none cited) | C5, C11 | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-12 *(new 2026-07)* | Proliferated-Constellation Aggregation Layer | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | `FUTURE-WORK.md` §13 | UNASSIGNED | UNASSIGNED |
| CR-13 | Coalition / Multi-Cell Generalization | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | `FUTURE-WORK.md` §13 | UNASSIGNED | UNASSIGNED |
| CR-14 | Commercial / Gray-Actor Class & purchasable SDA services | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | `FUTURE-WORK.md` §7, §13 | UNASSIGNED | UNASSIGNED |
| CR-15 | Campaign / Session-Persistence Container | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | `FUTURE-WORK.md` §13 | UNASSIGNED | UNASSIGNED |
| CR-16 | Ground-Segment-as-Terrain Cyber Model | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | `FUTURE-WORK.md` §13 | UNASSIGNED | UNASSIGNED |
| CR-17 | Persistent Debris / STM Environment Layer | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | `FUTURE-WORK.md` §2, §13 | UNASSIGNED | UNASSIGNED |
| CR-18 | Facilitator / cross-session adjudication-consistency support | UNASSIGNED | ADR-0031 | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-19 *(new 2026-07)* | Automated competency-assessment rubric computation | UNASSIGNED | ADR-0017 | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-20 | Dedicated multi-run/cohort research-export interface | UNASSIGNED | ADR-0029 | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-21 | Human-subjects research authorization/ethics boundary | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |

`CR-19`–`CR-21`, added by the 2026-07 DOM-002/004/005 backfill pass (`docs/feature-planning/
05-feature-review.md` Finding F-01), follow the same discipline as `CR-12`–`CR-18`: neither cites a
research-encyclopedia topic (DOM-002/004 are domain documents, not encyclopedia entries, and the
Research column is reserved for the latter) nor an Architecture Component (DOM-002/004/005 are not
yet represented in the C1–C12 component list at all — a gap this matrix does not resolve by
guessing one). `CR-19`/`CR-20` cite the Accepted ADR each conflicts with (`ADR-0017`, `ADR-0029`
respectively); `CR-21` cites none, since it does not conflict with anything, it simply has no
concrete feature yet to constrain. See `reviews/requirements-domain-backfill-report.md` for the
full derivation.

---

## Master matrix — Non-Functional Requirements

The Architecture Component and Implementation Package columns for NFRs are taken directly from
each NFR's own explicit "Affected subsystems" field (converted to the matching ICD component
where the named subsystem maps onto one), not separately inferred.

| Req ID | Title (abridged) | Research | ADR | Arch. Component | Affected subsystems (= Impl. Package) | Future Feature | Test |
|---|---|---|---|---|---|---|---|
| NFR-1100 | Responsive UI at high time multipliers | UNASSIGNED | ADR-0009, ADR-0014 | C1, C2, C4 | `engine/` (propagator, access provider), `session/` (clock catch-up), `ui_web/` (client poll loop) | UNASSIGNED | UNASSIGNED |
| NFR-1200 | Hardware-floor performance | UNASSIGNED | ADR-0019, ADR-0020 | C4 | `ui_web/static/` (globe.js, world.js, graph.js) | UNASSIGNED | UNASSIGNED |
| NFR-1300 | Sizing soft guideline (~24 sats) | UNASSIGNED | ADR-0019 | C1, C2 | `engine/`, `session/` (clock-lag watchdog — `SessionManager._record_catch_up_lag`) | UNASSIGNED | UNASSIGNED |
| NFR-1400 | LAN concurrency ceiling | UNASSIGNED | ADR-0026, ADR-0014 | C2, C4 | `session/inprocess.py` (`_locked` critical section), `ui_web/server.py` | UNASSIGNED | UNASSIGNED |
| NFR-1500 | Determinism (engine-wide) | UNASSIGNED | ADR-0002 | C1 | `engine/` (all), `engine/eventlog.py`, `engine/simulation.py` | UNASSIGNED | `spacesim/tests/test_determinism.py` |
| NFR-1600 | Robustness to invalid input | UNASSIGNED | (none identified) | C5, C1 | `content/vignette.py`, `engine/orders.py` | UNASSIGNED | UNASSIGNED |
| NFR-1700 | Sub-stepped clock | UNASSIGNED | ADR-0002 | C1 | `engine/clock.py` | UNASSIGNED | UNASSIGNED |
| NFR-1800 | Single-sitting availability | UNASSIGNED | (none identified) | C2 | `session/` (SessionManager) | UNASSIGNED | UNASSIGNED |
| NFR-1900 | UI-agnostic engine + 80% coverage | UNASSIGNED | ADR-0002, ADR-0007 | C1 | `engine/` (all), test suite | UNASSIGNED | `spacesim/tests/test_import_guard.py` |
| NFR-2000 | Content as data | UNASSIGNED | ADR-0007 | C5 | `content/vignette.py`, `content/vignettes/*.yaml` | UNASSIGNED | UNASSIGNED |
| NFR-2100 | Independently testable fidelity seams | UNASSIGNED | ADR-0009 | C1 | `engine/propagator.py`, `engine/access.py`, `engine/effects.py` | `FUTURE-WORK.md` §2 | UNASSIGNED |
| NFR-2200 | Secure development practice | UNASSIGNED | ADR-0018 | C5 + all | `content/vignette.py`, all subsystems | UNASSIGNED | UNASSIGNED |
| NFR-2300 | LAN trust boundary | UNASSIGNED | ADR-0015 | C2, C4 | `session/api.py` (SessionAPI, CellView), `ui_web/server.py` | UNASSIGNED | UNASSIGNED |
| NFR-2400 | State-hash data integrity | UNASSIGNED | ADR-0002 | C1 | `engine/eventlog.py` (Snapshot), `engine/world.py` | UNASSIGNED | UNASSIGNED |
| NFR-2500 | Action log sufficiency | UNASSIGNED | ADR-0002 | C1, C2 | `engine/eventlog.py`, `session/aar.py` | UNASSIGNED | UNASSIGNED |
| NFR-2600 | Complete action log | UNASSIGNED | ADR-0017, ADR-0002 | C1 | `engine/eventlog.py`, `engine/orders.py`, `engine/handlers.py` | UNASSIGNED | UNASSIGNED |
| NFR-2700 | File-based server config | UNASSIGNED | (none identified) | C4 | `spacesim/config.py`, `spacesim/ui_web/server.py` | UNASSIGNED | UNASSIGNED |
| NFR-2800 | Test-driven gated build | UNASSIGNED | ADR-0002 | (all) | `spacesim/tests/` | UNASSIGNED | UNASSIGNED |
| NFR-2900 | Windows-first portability | UNASSIGNED | ADR-0020 | (all) | Build/dependency manifest, `spacesim/` | UNASSIGNED | UNASSIGNED |
| NFR-3000 | Accessible presentation | UNASSIGNED | (none identified) | C4 | `ui_web/static/` (app.js, style.css, globe.js) | UNASSIGNED | UNASSIGNED |
| NFR-3100 | Classification banner | UNASSIGNED | (none identified) | C4, C2 | `ui_web/static/` (banner component), `session/aar.py` | UNASSIGNED | UNASSIGNED |
| NFR-3200 | TLE import with offline fallback | UNASSIGNED | ADR-0018 | C5, C4 | `content/` (TLE import), scenario builder UI | UNASSIGNED | UNASSIGNED |
| NFR-3300 | Browser-only client, no external integration | UNASSIGNED | (none identified) | C4 | `ui_web/server.py` | UNASSIGNED | UNASSIGNED |

### Candidate NFRs (CNFR-01–CNFR-07) — `CANDIDATE — NOT BASELINED`

| Req ID | Title (abridged) | Research | ADR | Arch. Component | Affected subsystems | Future Feature | Test |
|---|---|---|---|---|---|---|---|
| CNFR-01 | Observability | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CNFR-02 | (excluded candidate) | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CNFR-03 | (excluded candidate) | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CNFR-04 | (excluded candidate) | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CNFR-05 | (excluded candidate) | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CNFR-06 | AI-Red epistemic parity / fairness *(new candidate, CHG-010)* | UNASSIGNED | ADR-0024 | C8, C1 | INT-0015 (via FR-9110 cross-ref) | `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity" | UNASSIGNED |
| CNFR-07 | Distributed-simulation / exercise-interoperability federation *(new 2026-07, strategic-review reconciliation)* | UNASSIGNED | (none cited) | C2 | INT-0006 (via ICD §7 item 12 cross-ref) | `FUTURE-WORK.md` §13 "R19" | UNASSIGNED |

---

## Reverse index — Research → Requirement

No numbered FR/NFR leaf carries a per-leaf encyclopedia citation (verified by grep across all of
`docs/architecture/*.md`, excluding FR-/NFR- ID lines, which surfaced only one unrelated
stakeholder-table citation in `00-vision.md` not tied to any requirement ID). **Every requirement
ID in this matrix is `UNASSIGNED` under Research Source.** This is reported as-is rather than
backfilled with a plausible-looking research ID; closing this gap is future authoring work (see
`docs/requirements/requirements-change-log.md`, "Findings deliberately left unactioned," REQ-001 /
REQ-002 / REQ-030, which already flags the related GDS-10/traceability-matrix structural gap).

## Reverse index — ADR → Requirement

Built mechanically from each requirement's own "Related ADRs" field. ADRs with no entry below
have zero numbered FR/NFR leaves citing them back (per ADR-0029 INDEX's own "Scope and method"
note that every ADR traces to a GDS-01/02/03 section or build-spec/01 §4 decision, not
necessarily to a numbered FR/NFR) — listed as `(no citing FR/NFR)` rather than omitted. ADR-0030
and ADR-0031 (both new 2026-07) are included on the same basis.

| ADR | Citing Requirement(s) |
|---|---|
| ADR-0002 | FR-1120, FR-7110, FR-7310, FR-7320, NFR-1500, NFR-1700, NFR-1900, NFR-2400, NFR-2500, NFR-2600, NFR-2800 |
| ADR-0003 | FR-6110 |
| ADR-0004 | FR-2310, FR-3510, FR-3520, FR-4610, FR-6210, FR-6220, FR-6510, FR-6610 |
| ADR-0005 | FR-3110, FR-3120, FR-3410, FR-4410 |
| ADR-0006 | FR-1130 |
| ADR-0007 | FR-5310, NFR-2000, NFR-1900 |
| ADR-0008 | FR-8110 |
| ADR-0009 | FR-1210, NFR-1100, NFR-2100 |
| ADR-0010 | FR-3210, FR-3220 |
| ADR-0011 | FR-1220 |
| ADR-0012 | FR-1410, FR-1420 |
| ADR-0013 | FR-1510, FR-1520, FR-3410 |
| ADR-0014 | FR-6310, FR-6320, FR-6410, NFR-1100, NFR-1400 |
| ADR-0015 | FR-6220, NFR-2300 |
| ADR-0016 | FR-1110, FR-4310 |
| ADR-0017 | FR-4710, NFR-2600, CR-19 *(added 2026-07, DOM-002/004/005 backfill)* |
| ADR-0018 | FR-5210, NFR-3200, NFR-2200 |
| ADR-0019 | NFR-1200, NFR-1300 |
| ADR-0020 | NFR-1200, NFR-2900 |
| ADR-0021 | FR-9110 |
| ADR-0022 | FR-7210, FR-7220 |
| ADR-0024 | FR-9110, CR-01, CNFR-06 |
| ADR-0026 | FR-6310, FR-6320, NFR-1400 |
| ADR-0027 | FR-5110 |
| ADR-0029 | FR-4710, CR-20 *(added 2026-07, DOM-002/004/005 backfill)* |
| ADR-0030 | FR-9110 *(added 2026-07, strategic-review reconciliation)* |
| ADR-0031 | CR-18 *(added 2026-07, strategic-review reconciliation)* |
| ADR-0001 | (no citing FR/NFR) |
| ADR-0023 | (no citing FR/NFR) |
| ADR-0025 | (no citing FR/NFR) |
| ADR-0028 | (no citing FR/NFR) |

## Reverse index — Architecture Component → Requirement

Built mechanically from the Interface → Component derivation table above, applied to each
requirement's own Related Interfaces field. A component with no entry below has no FR/NFR whose
Related Interfaces field maps onto it via the derivation table.

| Component | Citing Requirement(s) |
|---|---|
| C1 Simulation Engine | FR-1110, FR-1120, FR-1130, FR-1210, FR-1220, FR-1310, FR-1410, FR-1420, FR-1510, FR-1520, FR-2110, FR-2210, FR-2310, FR-2410, FR-2510, FR-3110, FR-3120, FR-3220, FR-3310, FR-3410, FR-4410, FR-4610, FR-6210, FR-7110, FR-7220, FR-7310, FR-7320, FR-9110, NFR-1500, NFR-1700, NFR-2400, NFR-2600, NFR-2100, CR-01, CR-09, CR-10, CNFR-06 |
| C2 Session/Application Layer | most FR-6xxx, FR-1xxx–FR-4xxx leaves citing INT-0006/0007/0008/0011/0012/0014 — see master matrix per-row; also CNFR-07 (new 2026-07, via ICD §7 item 12 cross-ref) |
| C3 Mock SSN | FR-1510, FR-3210, FR-3220, CR-09 |
| C4 Operator Console | FR-2410, FR-3110, FR-3120, FR-3510, FR-3520, FR-4110–FR-4720, FR-5110, FR-6110–FR-6610, FR-8110, NFR-1100, NFR-1200, NFR-1400, NFR-2300, NFR-2700, NFR-3000, NFR-3100, NFR-3200, NFR-3300, CR-02, CR-03, CR-06 |
| C5 Content & Data | FR-5110, FR-5210, FR-5310, FR-7210, FR-7220, NFR-1600, NFR-2000, NFR-2200, NFR-3200, CR-08, CR-11 |
| C6 White Cell | FR-4110–FR-4720, FR-5110, FR-9110 (indirectly via INT-0016) |
| C7 Blue Cell | FR-2410, FR-3110, FR-3120, FR-3510, FR-3520 |
| C8 Red Cell (or AI-Red) | FR-2410, FR-3110, FR-3120, FR-3510, FR-3520, FR-9110, CR-01, CR-07, CNFR-06 |
| C9 Observer | FR-6220, FR-6510, CR-06 |
| C10 Space-Track.org | FR-5210 |
| C11 Local filesystem | FR-7210, FR-7220, CR-08, CR-11 |
| C12 Browser client | FR-4510, FR-6220, FR-6310, FR-6410, FR-8110, NFR-1200, CR-02, CR-03 |

## Reverse index — Interface → Requirement

Built directly from each requirement's own already-explicit "Related Interfaces" field — purely
mechanical, no inference.

| Interface | Citing Requirement(s) |
|---|---|
| INT-0001 | FR-4510, FR-6220, FR-6310, FR-6410, FR-6510 (via FR-6510's own field — see master matrix), FR-6610, FR-8110, CR-02, CR-03 |
| INT-0002 | FR-1110, FR-4110, FR-4210, FR-4310, FR-4410, FR-4510, FR-4610, FR-4720 |
| INT-0003 | FR-5110 |
| INT-0004 | FR-2410, FR-3110, FR-3120, FR-3510, FR-3520 |
| INT-0005 | FR-6220, FR-6510, CR-06 |
| INT-0006 | FR-3110, FR-3120, FR-3520, FR-6110, FR-6210, FR-6310, FR-6320, FR-6410, FR-6510, FR-6610, CNFR-07 (via ICD §7 item 12 cross-ref, new 2026-07) |
| INT-0007 | FR-1510, FR-1520, FR-2310, FR-4610, FR-6210 |
| INT-0008 | FR-1110, FR-1120, FR-1130, FR-1210, FR-1220, FR-1310, FR-1410, FR-1420, FR-2110, FR-2210, FR-2310, FR-2410, FR-2510, FR-3110, FR-3310, FR-3410, FR-7110, FR-9110 |
| INT-0009 | FR-3210, FR-3220, CR-09 |
| INT-0010 | FR-1510, FR-3220, CR-09 |
| INT-0011 | FR-5310, FR-7220 |
| INT-0012 | FR-7210, FR-7220, CR-08 |
| INT-0013 | FR-5210 |
| INT-0014 | FR-1120, FR-7110, FR-7310, FR-7320 |
| INT-0015 | FR-9110, CR-01, CR-07, CNFR-06 |
| INT-0016 | FR-4410 |
| (no interface) | FR-4710 |

## Reverse index — Requirement → Future Feature

`docs/FUTURE-WORK.md` contains no FR-/NFR-/CNFR-/CR- ID citation anywhere (verified by grep); every
entry below is citable only because the requirement's *own* field names the future-work item, not
because `FUTURE-WORK.md` cites the requirement back. Seven of the eight entries below were added
2026-07 (CR-12–CR-17, CNFR-07), when the strategic-review reconciliation pass added the
`FUTURE-WORK.md` §13/§7/§2 cross-references those candidates' own Source fields now carry.

| Requirement | Future Feature |
|---|---|
| FR-9110 | `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity" |
| CNFR-06 | `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity" |
| CR-01 | `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity" |
| CR-12 | `FUTURE-WORK.md` §13 (R13 — proliferated-constellation program) *(new 2026-07)* |
| CR-13 | `FUTURE-WORK.md` §13 (R14 — coalition play) *(new 2026-07)* |
| CR-14 | `FUTURE-WORK.md` §7 (mock-SSN commercial feed, already scoped), §13 (R11) *(new 2026-07)* |
| CR-15 | `FUTURE-WORK.md` §13 (R15 — campaign container) *(new 2026-07)* |
| CR-16 | `FUTURE-WORK.md` §13 (R17 — ground-segment cyber deepening) *(new 2026-07)* |
| CR-17 | `FUTURE-WORK.md` §2 (unwired `prop.collision_avoid`), §13 (R16 — persistent debris) *(new 2026-07)* |
| CNFR-07 | `FUTURE-WORK.md` §13 (R19 — distributed-use security growth path + GAP-11 study) *(new 2026-07)* |
| All other FR/NFR/CR/CNFR (including CR-18) | `UNASSIGNED` |

## Reverse index — Requirement → Test

Only two entries exist anywhere in this matrix, both grounded in explicit `CLAUDE.md` prose or an
explicit Metric field naming the test file — not in filename inference. Grepping
`spacesim/tests/` for `FR-[0-9]{4}` / `NFR-[0-9]{4}` returns zero matches; no test file cites a
requirement ID directly.

| Requirement | Test |
|---|---|
| FR-1120 | `spacesim/tests/test_determinism.py` |
| NFR-1500 | `spacesim/tests/test_determinism.py` |
| NFR-1900 | `spacesim/tests/test_import_guard.py` |
| All other FR/NFR/CR/CNFR | `UNASSIGNED` |

## Reverse index — Requirement → Implementation Package

Grouped by real, verified `spacesim/` file (confirmed to exist via `ls`, never an invented path or
ID scheme — there is no `FS-xxx`/`IMP-xxx` convention anywhere in this repo).

| Implementation Package | Citing Requirement(s) |
|---|---|
| `engine/clock.py` | FR-1110 |
| `engine/simulation.py` | FR-1120 |
| `engine/propagator.py` | FR-1210 |
| `engine/access.py` | FR-1220 |
| `engine/entities.py` | FR-1310 |
| `engine/effects.py` | FR-1410, FR-1420 |
| `engine/cyber.py` | FR-1420 |
| `engine/custody.py` | FR-1510, FR-1520 |
| `engine/bus.py` | FR-2110, FR-2210 |
| `engine/busmodel.py` | FR-2310 |
| `engine/buscommands.py` | FR-2410 |
| `engine/recovery.py` | FR-2510 |
| `engine/orders.py` | FR-3110, FR-3120, FR-3410, NFR-1600 |
| `engine/ssn.py` | FR-3210, FR-3220 |
| `engine/eventlog.py` | FR-7110, NFR-2400, NFR-2500, NFR-2600 |
| `engine/world.py` | NFR-2400 |
| `engine/handlers.py` | NFR-2600 |
| `session/manager.py` | FR-4310, FR-4410, FR-7210, FR-6310, NFR-1300, NFR-1800 |
| `session/api.py` | FR-6110, NFR-2300 |
| `session/cells.py` | FR-6210, FR-6220 |
| `session/inprocess.py` | FR-6320, FR-6410, NFR-1400 |
| `session/aar.py` | FR-7310, FR-7320, NFR-2500, NFR-3100 |
| `session/redai.py` | FR-9110 |
| `content/vignette.py` | FR-5110, FR-5310, NFR-1600, NFR-2000 |
| `content/vignettes/*.yaml` | NFR-2000 |
| `content/` (TLE import) | FR-5210, NFR-3200 |
| `ui_web/server.py` | FR-4510, FR-8110, NFR-1400, NFR-2300, NFR-2700, NFR-3300 |
| `ui_web/static/app.js` | FR-6510, FR-8110, NFR-3000 |
| `ui_web/static/` (globe.js, world.js, graph.js, style.css) | NFR-1200, NFR-3000, NFR-3100 |
| `spacesim/config.py` | NFR-2700 |
| `spacesim/tests/` | NFR-2800 |
| Build/dependency manifest, `spacesim/` (whole tree) | NFR-2900 |
| All subsystems (no single file) | NFR-2200 |
| UNASSIGNED | FR-1130, FR-3310, FR-3510, FR-3520, FR-4110, FR-4210, FR-6610, all Candidate Requirements (CR-01–CR-21), all Candidate NFRs (CNFR-01–CNFR-07) |

*(FR-4610/FR-4710/FR-4720 closed 2026-07 via `IP-1060` v2.0; FR-7220 closed 2026-07 via `IP-1100` —
both split from `IP-1060` v1.0 per Finding F-03 — see the master matrix rows above. FR-4110/FR-4210/
FR-6610 remain `UNASSIGNED` here even though `FS-115`/`FS-114` now exist, because those two Feature
Specifications explicitly flag their own build status as unverified — an FS existing is not the
same evidence bar this index requires, per its own stated discipline.)*

## Strategic review reconciliation (strategic-review-2026-07.md)

In response to [`reviews/strategic-review-2026-07.md`](../reviews/strategic-review-2026-07.md) and
its disposition in [`reviews/architecture-update.md`](../reviews/architecture-update.md), this
matrix was extended to keep pace with `01-functional-requirements.md` and
`02-non-functional-requirements.md`'s own reconciliation passes. Full analysis in
[`reviews/requirements-update-report.md`](../reviews/requirements-update-report.md). Summary:

- Added master-matrix rows for **CR-12–CR-18** and **CNFR-07** (both Candidate sections, renamed
  from `CR-01–CR-11`/`CNFR-01–CNFR-06` to `CR-01–CR-18`/`CNFR-01–CNFR-07`).
- Added **ADR-0030** and **ADR-0031** to the ADR → Requirement reverse index.
- Added **CNFR-07** to the Architecture Component → Requirement (C2) and Interface → Requirement
  (INT-0006) reverse indices, both via its own explicit ICD §7 item 12 cross-reference.
- Extended the Requirement → Future Feature reverse index with **CR-12–CR-17** and **CNFR-07**
  (each citable only via its own Source field's `FUTURE-WORK.md` citation, per this index's
  existing discipline).
- Added the new candidates to the Implementation Package reverse index's `UNASSIGNED` bucket
  (honestly — none has shipped code).
- Updated the "Method and discipline" section's ADR range (`ADR-0029` → `ADR-0031`) and added the
  Strategic Assumptions Register as a read input.
- **No baselined FR/NFR row (the numbered, non-Candidate master matrix) was added, removed, or
  altered.**

## DOM-002/004/005 backfill (2026-07)

In response to `docs/feature-planning/05-feature-review.md` Finding F-01, and following the same
pass documented in `01-functional-requirements.md`'s and `02-non-functional-requirements.md`'s own
"DOM-002/004/005 backfill" sections, this matrix was extended. Full analysis in
[`reviews/requirements-domain-backfill-report.md`](../reviews/requirements-domain-backfill-report.md).
Summary:

- Added master-matrix rows for **CR-19–CR-21** (Candidate Requirements section, renamed from
  `CR-01–CR-18` to `CR-01–CR-21`). No new Candidate NFR was added (see `02`'s own reconciliation
  section for why).
- Added **CR-19** to the ADR-0017 reverse-index row and **CR-20** to the ADR-0029 reverse-index row
  — both new Candidates cite the Accepted ADR their underlying capability conflicts with.
- **Closed four pre-existing `UNASSIGNED` Impl. Package cells** as a direct side effect of this
  session's separate `IMP-106A`/`IP-1060` reconciliation work (Finding F-03, not this pass's own
  scope, but landed in the same session): `FR-4610`, `FR-4710`, `FR-4720` (now `session/manager.py`
  via `IP-1060` v2.0) and `FR-7220` (now `session/manager.py` via `IP-1100`). Updated the
  Implementation Package reverse index's `UNASSIGNED` bucket accordingly.
- **No baselined FR/NFR row was added.** Every candidate capability DOM-002/004 describe conflicts
  with an Accepted ADR (`ADR-0017`, `ADR-0029`) or lacks a concrete feature to constrain
  (`CR-21`); DOM-005 yielded no new leaf, baseline or candidate, at all (methodology guidance, not
  a system requirement — see `02`'s own reconciliation section).

## Related

[`01-functional-requirements.md`](01-functional-requirements.md) ·
[`02-non-functional-requirements.md`](02-non-functional-requirements.md) ·
[`requirements-change-log.md`](requirements-change-log.md) ·
[`../reviews/requirements-review.md`](../reviews/requirements-review.md) ·
[`../design/05-interface-control-document.md`](../design/05-interface-control-document.md) ·
[`../architecture/adr/INDEX.md`](../architecture/adr/INDEX.md) ·
[`../architecture/10-requirements-traceability-matrix.md`](../architecture/10-requirements-traceability-matrix.md)
(GDS-10, scaffold-only — not authored by this document)
