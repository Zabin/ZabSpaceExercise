# Requirements Traceability Matrix

This is the per-requirement traceability matrix for the baselined and candidate requirements in
[`01-functional-requirements.md`](01-functional-requirements.md) and
[`02-non-functional-requirements.md`](02-non-functional-requirements.md). It is the
leaf-grain companion of
[`docs/architecture/10-requirements-traceability-matrix.md`](../architecture/10-requirements-traceability-matrix.md)
(GDS-10, authored 2026-10-22), which traces at the GDS tag grain and reports chain completeness;
this document stays authoritative for leaf-level traces. *(Corrected 2026-10-23: the prior text said
GDS-10 was unauthored.)*

## Method and discipline

> **Amended 2026-10-23, `BL-0322`** (see
> [`reviews/requirements-update-bl-0322.md`](../reviews/requirements-update-bl-0322.md)): added row
> `NFR-2850`. **The Test column is now to be generated, not edited** (`NFR-2850`): each cell lists
> exactly the tests whose `@pytest.mark.verifies(...)` origin names that requirement, produced by
> the origin report (`IP-1330`). The marker tooling is planned but not built, and no test carries a
> marker yet, so the column could not be generated in this pass. **The Test cells below are the
> earlier hand-filled values, kept as hints for the backfill (`IP-1331`–`IP-1333`), not as verified
> traceability.** The first `04` pass after `IP-1330` lands replaces the whole column with the
> generated one, `UNASSIGNED` wherever no test declares the requirement.

> **Amended 2026-10-23** (GDS ladder alignment, see
> [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md)):
> added rows `FR-4320`, `FR-7230` and 19 NFR rows (`NFR-1510`, `1610`, `2410`, `2810`–`2840`,
> `3010`–`3060`, `3710`, `3800`–`3840`); reworded `FR-5210`, `NFR-1900`, `NFR-3200`; corrected
> `FR-3120`'s title; marked `FR-4310` and `FR-7220` not met as built; marked six foundational leaves
> as pre-package builds; rewrote the Requirement → Test and Requirement → Implementation Package
> index notes (GDS-10 F2). No other row changed.

> **Amended 2026-10-15** (parked-questions batch, see
> [`reviews/requirements-update-parked-questions-batch.md`](../reviews/requirements-update-parked-questions-batch.md)):
> corrected the Title column of `FR-4510` and `FR-6510` (copy/paste defects, `BL-0010`/`BL-0012`);
> annotated `FR-7440`'s amendment (`BL-0159`); added candidate row `CR-22` (`BL-0181`). No other
> row changed.
>
> **Amended 2026-10-16** (load-validation batch, see
> [`reviews/requirements-update-load-validation-batch.md`](../reviews/requirements-update-load-validation-batch.md)):
> added rows `FR-1460` and `FR-5311`–`FR-5314`; set `FR-5310`'s Future Feature to `FS-131`; added
> candidate rows `CR-23`–`CR-25`. No other row changed.
>
> **Amended 2026-10-17** (run #150, `BL-0245`, second addendum of the same report): added row
> `FR-1470`; added `ADR-0036`/`ADR-0037` reverse-index rows; added `FR-1470` to the C1 and
> INT-0008 reverse-index rows. No other row changed.
>
> **Amended 2026-10-17** (run #160, owner-prioritized `DEFERRED` clearance, see
> [`reviews/requirements-update-deferred-clearance-batch.md`](../reviews/requirements-update-deferred-clearance-batch.md)):
> `FR-1220` Impl. Package attributed to its four verified packages (`BL-0033`); `FR-3310` Title
> corrected; `FR-6220`/`FR-7410`/`FR-4420` rows annotated; NFR master table given its own
> `Impl. Package` column so the seven rows that carried a ninth cell are well-formed (`BL-0148`);
> candidate rows `CR-26`–`CR-28` added.
>
> **Amended 2026-10-17** (run #172, closing straggler of the same clearance pass): `FR-5220`
> Interface/Component cells corrected to INT-0006/INT-0011 and C4/C2/C5 (`BL-0263`); `FR-4430`
> row annotated (`BL-0101`, mapping confirmed in Notes). No other row changed.
>
> **Amended 2026-10-17** (project-owner decision on `BL-0249`, see
> [`reviews/requirements-update-missed-salvo-decision.md`](../reviews/requirements-update-missed-salvo-decision.md)):
> added row `FR-1480` (promoted from `CR-28`; forward cells `UNASSIGNED` until FS-132 and a package
> carry it); `FR-1460` row annotated (Acceptance Criteria amended); `CR-28` row marked `PROMOTED`;
> `FR-1480` added to the C1 and INT-0008 reverse-index rows. No other row changed.

Inputs read in full to build this matrix: the research encyclopedia index
([`docs/research/encyclopedia/`](../research/encyclopedia/INDEX.md)), the GDS architecture ladder
(`docs/architecture/00`–`05`), the ADR index
([`docs/architecture/adr/INDEX.md`](../architecture/adr/INDEX.md), ADR-0001–ADR-0035, 34
`Accepted` and 1 `Superseded` — `ADR-0029` by `ADR-0033`), the Interface Control Document
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
>
> **Further amended 2026-07** (`ADR-0032`/`ADR-0033` conflict resolution) to add master-matrix rows
> for **`FR-10110`** and **`FR-10210`** (promoted from `CR-19`/`CR-20` once the project owner
> resolved their blocking ADR conflicts) and to mark those two Candidate rows `PROMOTED` in place
> rather than deleting them. Updated the ADR index range above to `ADR-0033` and its `Accepted`/
> `Superseded` split.
>
> **Further amended 2026-07-04** (training-corpus elevation, MSTR-001 §2 / GDS-00/GDS-01
> same-dated sections) to add master-matrix rows for the new **`FR-11000` family**
> (`FR-11110`–`FR-11420`) and NFR rows **`NFR-3400`–`NFR-3600`**. These trace to documentation
> and process artifacts (the training corpus) rather than `spacesim/` code — see the note under
> the FR-11000 rows for how the cells are populated honestly under that difference. No existing
> row was altered.
>
> **Further amended 2026-07-04, same day** (pipeline-manager run #16, `02-research-training-pedagogy`
> authored the R600 tier 0/8→8/8) to fill in the Research cells on `FR-11110`, `FR-11120`, `FR-11210`,
> `FR-11310`, `FR-11320`, `FR-11420`, and `NFR-3600` — previously `UNASSIGNED`/"index only, not yet
> citable" — with the specific R601–R608 topic(s) each leaf's Feature Mapping names. `FR-11410` stays
> `UNASSIGNED` (no single topic names it specifically). No existing baselined FR/NFR row outside this
> family was touched.
>
> **Further amended 2026-09-27** (Should-tier external-validation-report intake batch) to add
> thirteen new master-matrix rows: `FR-1230`, `FR-1320`, `FR-1430`, `FR-1440`, `FR-1450`,
> `FR-1610`–`FR-1660` (six rows, new parent `FR-1600`), `FR-2320`, `FR-3430`, `FR-3440`, `FR-4440`,
> `FR-7330` — all with every forward-trace column (`Future Feature`/`Test`/`Impl. Package`) honestly
> `UNASSIGNED` (no `FS-xxx`/`IP-xxxx`/test exists yet for any of the nine backlog items these trace
> to). Five rows (`FR-1230`, `FR-1430`, `FR-1610`–`FR-1650`, `FR-4440`) cite a Research column
> (`R109`/`R117`/`R131`) for the first time on a fresh leaf — no existing row's Research cell was
> changed. See
> [`reviews/requirements-update-should-tier-batch.md`](../reviews/requirements-update-should-tier-batch.md)
> for the full analysis.
>
> **Further amended 2026-10-03** (RIC-view/CATS-angle/TLE-export/controller-view intake batch) to
> add seven new master-matrix rows: `FR-1670`, `FR-4450`, `FR-4620`, `FR-7440`, `FR-8210`,
> `FR-8220` (new parent `FR-8200`) — all with every forward-trace column (`Future Feature`/`Test`/
> `Impl. Package`) honestly `UNASSIGNED` (no `FS-xxx`/`IP-xxxx`/test exists yet for any of these
> five backlog items). No row's Research column is populated — `BL-0108`/`BL-0112`'s research gaps
> remain open (`DEFERRED`, revisited before `06-feature-specification`), so `FR-8210`/`FR-8220`/
> `FR-1670` cite only backlog rows and existing FR/engine-code Source Documents, consistent with
> this matrix's own discipline against inferring a Research cell with no explicit citation. See
> [`reviews/requirements-update-ric-cats-batch.md`](../reviews/requirements-update-ric-cats-batch.md)
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
| FR-1110 | Single clock owner | UNASSIGNED | ADR-0016 | C2, C1 | INT-0002, INT-0008 | UNASSIGNED | UNASSIGNED | `engine/clock.py` *(pre-package build, Phases 0–5; no IP — GDS-10 F4)* |
| FR-1120 | Determinism (`(state, eventlog, seed) → byte-identical`) | UNASSIGNED | ADR-0002, ADR-0038 | C2, C1 | INT-0008, INT-0014 | UNASSIGNED | `spacesim/tests/test_determinism.py::test_cannot_advance_backwards`, `spacesim/tests/test_determinism.py::test_different_seed_changes_random_outcome`, `spacesim/tests/test_determinism.py::test_property_replay_is_byte_identical`, `spacesim/tests/test_determinism.py::test_replay_from_midway_snapshot_matches_live`, `spacesim/tests/test_determinism.py::test_replay_from_scratch_matches_live`, `spacesim/tests/test_determinism.py::test_save_round_trip_reproduces_state` | `engine/simulation.py` — `IP-1021` *(VERIFIED 2026-10-17, `VR-1021`, failure-atomic `advance_to`)* |
| FR-1130 | (clock/scheduler leaf, ADR-0006) | UNASSIGNED | ADR-0006 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-1210 | (propagation seam, ADR-0009) | UNASSIGNED | ADR-0009 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/propagator.py` *(pre-package build, Phases 0–5; no IP — GDS-10 F4)* |
| FR-1220 | (access provider, ADR-0011) | UNASSIGNED | ADR-0011 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/access.py` — shared by `IP-1010`, `IP-1040`, `IP-1050`, `IP-1051`, all `VERIFIED` (`VR-1010`/`VR-1040`/`VR-1050`/`VR-1051`, runs #18/#22/#23/#24) *(attributed 2026-10-17, `BL-0033`)* |
| FR-1230 *(new 2026-09-27, `BL-0074`/B8)* | Space-weather-index-driven LEO drag coupling | R131 (v1.2) | ADR-0002, ADR-0039 | C2, C1 | INT-0008 | FS-123 | UNASSIGNED | IP-1230 *(✅ VERIFIED 2026-10-18, run #194, VR-1230)* — `engine/perturbations.py` (`f_solar`, `f_geo`, `drag_multiplier`, `index_series_problems`), `engine/busmodel.py` (`BusSystem._apply_index_drag`), `engine/entities.py` (`Asset.ballistic_coeff_m2_kg`), `content/vignette.py` (`space_weather_series`, `build_world`, `validate_vignette`) |
| FR-1310 | Asset `resources.delta_v_ms` validation | UNASSIGNED | (none directly — restates GDS-04 §3) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/entities.py`; `IP-1052` *(VERIFIED 2026-10-16, `VR-1052` — `engine/orders.py::_order_params_ok`/`ORDER_PARAM_RULES` reject malformed params `invalid_param` in `_validate`; planners build the payload before committing, `BL-0222`)* |
| FR-1320 *(new 2026-09-27, `BL-0072`/B6)* | Per-asset manoeuvre ledger with purpose tags and export | UNASSIGNED | (none directly) | C2, C1, C4 | INT-0006, INT-0008 | FS-125 | UNASSIGNED | IP-1250 *(VERIFIED 2026-09-28 via VR-1250)* |
| FR-1410 | Five-D effects resolution | UNASSIGNED | ADR-0012 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `IP-1051` *(closed 2026-07-04 via VR-1051)*; `IP-1052` *(VERIFIED 2026-10-16, `VR-1052` — `engine/orders.py::_order_params_ok`/`ORDER_PARAM_RULES` reject malformed params `invalid_param` in `_validate`; planners build the payload before committing, `BL-0222`)* |
| FR-1420 | Cyber exception (non window-gated) | UNASSIGNED | ADR-0012 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `IP-1051` *(effects.py/cyber.py half closed 2026-07-04 via VR-1051; the `orders.py` routing half remains shared with `IP-1020`)*; `IP-1052` *(VERIFIED 2026-10-16, `VR-1052` — `engine/orders.py::_order_params_ok`/`ORDER_PARAM_RULES` reject malformed params `invalid_param` in `_validate`; planners build the payload before committing, `BL-0222`)* |
| FR-1430 *(new 2026-09-27, `BL-0077`/B11)* | Debris-field persistence estimate by altitude | R117 | (none directly — informational estimate, not a new engine mechanism) | C1 | INT-0008 | FS-124 | UNASSIGNED | IP-1240 *(VERIFIED 2026-09-28 via VR-1240)* |
| FR-1440 *(new 2026-09-27, `BL-0081`/B15)* | Uplink/crosslink jamming degrades command and relay delivery paths | UNASSIGNED | (none directly — extends ADR-0011's six-channel model) | C2, C1 | INT-0008 | FS-129 | UNASSIGNED | IP-1290 *(VERIFIED 2026-09-28 via VR-1290)* |
| FR-1450 *(new 2026-09-27, `BL-0081`/B15)* | Per-effect-class detectability and attribution-difficulty configuration | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | FS-129 | UNASSIGNED | IP-1290 *(VERIFIED 2026-09-28 via VR-1290 — schema confirmed identical to IP-1270's landed enumeration)* |
| FR-1460 *(new 2026-10-16, `BL-0226`; AC amended 2026-10-17, `BL-0249` — charge stated for hit and miss, see FR-1480)* | Kinetic salvo bounded by remaining ammunition | UNASSIGNED | (none directly) | C1 | INT-0008 | FS-132 | UNASSIGNED | `IP-1320` *(VERIFIED 2026-10-17 via VR-1320 — `engine/orders.py::_engage_rounds`/`_validate` reject `insufficient_ammo`; `_h_effect` re-checks rounds at execution; all three gate points independently reproduced on fresh fixtures)*; amended AC (hit or miss charged) by `IP-1321` *(VERIFIED 2026-10-17 via VR-1321 — fresh session, clean)* |
| FR-1470 *(new 2026-10-17, `BL-0245`)* | Jamming leaves the jammer's power rating unchanged | R111 | ADR-0037 | C1 | INT-0008 | FS-132 | UNASSIGNED | `IP-1320` *(VERIFIED 2026-10-17 via VR-1320 — `engine/orders.py` jam plan emits no `power_w` consumption; `_h_effect` has no `power_w` branch; independently confirmed unchanged across three sequential jam orders)* |
| FR-1480 *(new 2026-10-17, `BL-0249`, promoted from `CR-28`)* | Kinetic salvo charged whether it hits or misses | UNASSIGNED | (none directly) | C1 | INT-0008 | FS-132 (v1.1) | UNASSIGNED | `IP-1321` *(VERIFIED 2026-10-17 via VR-1321 — fresh session, clean; `engine/orders.py::OrderSystem._h_effect` charges `consume.ammo` for every engagement that reaches resolution; the `outcome.success` condition removed; independently reproduced for hit/miss/destroyed-target/re-check-failure cases plus replay determinism)* |
| FR-1510 | Custody/Track confidence decay | UNASSIGNED | ADR-0013 | C2, C1, C3 | INT-0007, INT-0010 | UNASSIGNED | UNASSIGNED | `IP-1030` *(closed 2026-07-04 via VR-1030)* |
| FR-1520 | Weapons-quality gate | UNASSIGNED | ADR-0013 | C2, C1 | INT-0007 | UNASSIGNED | UNASSIGNED | `IP-1030` *(closed 2026-07-04 via VR-1030)* |
| FR-1610 *(new 2026-09-27, `BL-0073`/B7)* | Fence/dish radar beam-mode variants | R109 | ADR-0011 | C1 | INT-0008 | FS-122 | UNASSIGNED | IP-1220 *(VERIFIED 2026-09-28 via VR-1220)*; IP-1222 *(VERIFIED 2026-10-16 via VR-1222 — end-to-end wiring, `engine/orders.py` observe branch + `engine/entities.py` validator, `BL-0212`)*; IP-1041 *(VERIFIED 2026-10-16 via VR-1041 — a non-string `beam_mode` request is rejected `invalid_param` in `engine/orders.py::_validate` (`_observe_params_ok`), and `engine/isr.py::beam_params` falls back instead of raising, `BL-0217`)*; IP-1223 *(COMPLETE 2026-10-17 — `engine/orders.py` `_requested_beam_mode`/`_observe_modes`/`_observe_payload_type` in `_validate` + `_candidate_sensors`; `app.js` `populateBeamModes`; VERIFIED 2026-10-17 via VR-1223)* |
| FR-1620 *(new 2026-09-27, `BL-0073`/B7)* | Optical sensor solar/lunar exclusion angle | R109 | ADR-0011 | C1 | INT-0008 | FS-122 | UNASSIGNED | IP-1220 *(VERIFIED 2026-09-28 via VR-1220)* |
| FR-1630 *(new 2026-09-27, `BL-0073`/B7)* | Space-based sensor minimum-range floor and altitude-band affinity | R109 | ADR-0011 | C1 | INT-0008 | FS-122 | UNASSIGNED | IP-1220 *(VERIFIED 2026-09-28 via VR-1220)*; IP-1222 *(VERIFIED 2026-10-16 via VR-1222 — `Regime`-typed affinity in `engine/entities.py`, `isr.altitude_band`, `BL-0214`)* |
| FR-1640 *(new 2026-09-27, `BL-0073`/B7)* | Cue-dependent sensor tasking precondition | R109 | ADR-0011 | C1 | INT-0008 | FS-122 | UNASSIGNED | IP-1220 *(VERIFIED 2026-09-28 via VR-1220)*; IP-1222 *(VERIFIED 2026-10-16 via VR-1222 — `auto` candidate filter in `engine/orders.py` `_candidate_sensors`/`_plan_collection`, `BL-0213`)* |
| FR-1650 *(new 2026-09-27, `BL-0073`/B7)* | Passive-RF multilateration sensor network | R109 | ADR-0011, ADR-0010 | C2, C3, C1 | INT-0008, INT-0009, INT-0010 | FS-122 | UNASSIGNED | IP-1220 *(VERIFIED 2026-09-28 via VR-1220 — `passive_rf_fix()` confirmed pure/unwired to any TrackCatalog delivery path, per VR-1220 Finding L2)* |
| FR-1660 *(new 2026-09-27, `BL-0083`/B17)* | Satellite-hosted sensor follows host orbit | UNASSIGNED | ADR-0011 | C1 | INT-0008 | FS-122 | UNASSIGNED | IP-1220 *(VERIFIED 2026-09-28 via VR-1220)* |
| FR-1670 *(new 2026-10-03, `BL-0122`)* | Phase-angle (CATS) access-window refinement for passive EO sensors | R109 *(v1.3 §3.11)* | ADR-0011 | C2, C1 | INT-0008 | FS-122 *(v1.1, 2026-10-15)* | UNASSIGNED | **IP-1221** *(VERIFIED 2026-10-16, `VR-1221` — `engine/entities.py::Sensor.usable_phase_angle_deg` + validator, `engine/isr.py::phase_angle_factor`/`effective_gain`, `engine/orders.py::OrderSystem._observation_phase_angle_deg` (via `engine/sun.py::cats_phase_angle_deg`))* |
| FR-2110 | Bus state model | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `IP-1050` *(closed 2026-07-04 via VR-1050)* |
| FR-2210 | Payload state model | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `IP-1050` *(closed 2026-07-04 via VR-1050)* |
| FR-2310 | Bus evolution / telemetry-contact / downlink handlers | UNASSIGNED | ADR-0004 | C2, C1 | INT-0007, INT-0008 | UNASSIGNED | UNASSIGNED | `engine/busmodel.py` |
| FR-2320 *(new 2026-09-27, `BL-0075`/B9)* | Per-asset telemetry CSV export over a time span | UNASSIGNED | ADR-0004 | C2, C1, C4 | INT-0006, INT-0007 | FS-126 | UNASSIGNED | IP-1260 *(VERIFIED 2026-10-10 via VR-1260 — `session/manager.py::telemetry_export`, `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv`)*; IP-1261 *(COMPLETE 2026-10-11, `BL-0170` remediation — cross-route parity Postcondition: `session/manager.py::get_series` + `telemetry_export` share `session/aar.py::worlds_at_times` / `engine/simulation.py::replay_stepwise`; awaiting `09-package-verification`)*; IP-1262 *(COMPLETE 2026-10-11, `BL-0176` remediation — telemetry export sampling capped via the shared `session/ephemeris.py::sample_times`/`MAX_EXPORT_SAMPLES`; plus `BL-0174` rider. Tests: `spacesim/tests/test_telemetry.py::test_telemetry_export_over_ceiling_rejected_without_replay`, `::test_series_reversed_window_matches_forward_reversed`, `spacesim/tests/test_web.py::test_telemetry_export_route_rejects_over_ceiling_interval_400`; awaiting `09-package-verification`)* |
| FR-2410 | Bus/payload command verbs | UNASSIGNED | (none directly) | C4, C7, C8, C2, C1 | INT-0004, INT-0008 | UNASSIGNED | UNASSIGNED | `IP-1050` *(closed 2026-07-04 via VR-1050)* |
| FR-2510 | Safe-mode / recovery chain | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/recovery.py` |
| FR-3110 | Plan-first command issuance | UNASSIGNED | ADR-0005 | C4, C7, C8, C2, C1 | INT-0004, INT-0006, INT-0008 | UNASSIGNED | UNASSIGNED | `engine/orders.py`; `IP-1052` *(VERIFIED 2026-10-16, `VR-1052` — `engine/orders.py::_order_params_ok`/`ORDER_PARAM_RULES` reject malformed params `invalid_param` in `_validate`; planners build the payload before committing, `BL-0222`)* |
| FR-3120 | Cancellation and editing before uplink *(title corrected 2026-10-23; was "Sensor tasking")* | UNASSIGNED | ADR-0005 | C4, C7, C8, C2 | INT-0004, INT-0006 | UNASSIGNED | UNASSIGNED | `engine/orders.py` *(pre-package build; no IP — GDS-10 F4)* |
| FR-3210 | SSN collection request | UNASSIGNED | ADR-0010 | C2, C3 | INT-0009 | UNASSIGNED | UNASSIGNED | `IP-1040` *(closed 2026-07-04 via VR-1040)*; `IP-1041` *(VERIFIED 2026-10-16 via VR-1041 — `engine/orders.py::_plan_collection` reports `sensor_contended` only when a window was found and all were booked, else `no_window`; malformed observe params rejected before booking, `BL-0219`/`BL-0217`)* |
| FR-3220 | SSN delivery | UNASSIGNED | ADR-0010 | C2, C3, C1 | INT-0009, INT-0010 | UNASSIGNED | UNASSIGNED | `IP-1040` *(closed 2026-07-04 via VR-1040)* |
| FR-3310 *(Outputs restated 2026-10-17, `BL-0050`)* | Single scheduler for commands and collection tasks | UNASSIGNED | (none directly) | C2, C1 | INT-0008 | UNASSIGNED *(feature ownership routed to `06`, `BL-0050`)* | UNASSIGNED | `engine/orders.py`, `engine/ssn.py`, `engine/clock.py` (shared `Scheduler`); IP-1131 *(VERIFIED 2026-10-17 via VR-1131, test-only — mutation-checked)*; IP-1065 *(VERIFIED 2026-10-17 via VR-1065 — `session/inprocess.py::cell_activity` reports `executed` once a queued order's bar has ended, same rule as `list_orders`, `BL-0266`; RTM cell added by VR-1065)* |
| FR-3410 | (order delivery path leaf, ADR-0005/0013) | UNASSIGNED | ADR-0005, ADR-0013 | C2, C1 | INT-0008 | UNASSIGNED | UNASSIGNED | `engine/orders.py` |
| FR-3420 | Per-cell independent ROE | UNASSIGNED | (none directly) | C1 | (none — engine-internal validation change) | FS-117 | UNASSIGNED | IP-1172 *(VERIFIED 2026-07-11)* |
| FR-3430 *(new 2026-09-27, `BL-0076`/B10)* | Optional per-effect-type controller-role authorization gating | UNASSIGNED | (none directly) | C2, C6 | INT-0002, INT-0008 | FS-127 | UNASSIGNED | IP-1270 *(VERIFIED 2026-09-28 via VR-1270)* |
| FR-3440 *(new 2026-09-27, `BL-0076`/B10)* | Live, logged mid-session ROE flag changes | UNASSIGNED | ADR-0002 | C2, C6 | INT-0002, INT-0008 | FS-127 | UNASSIGNED | IP-1270 *(VERIFIED 2026-09-28 via VR-1270)* |
| FR-3510 | Role-Assignment command-filtering consequence | UNASSIGNED | ADR-0004 | C4, C7, C8 | INT-0004 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-3520 | Role-Assignment scoping (bus/payload/both) *(new leaf, CHG-002)* | UNASSIGNED | ADR-0004 | C4, C7, C8, C2 | INT-0004, INT-0006 | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| FR-4110 | White Cell exercise-control leaf | UNASSIGNED | (none directly) | C4, C6 | INT-0002 | UNASSIGNED | UNASSIGNED | `IP-1150` *(closed 2026-07-03 via VR-1150)* |
| FR-4210 | Seat-to-role assignment | UNASSIGNED | (none directly) | C4, C6 | INT-0002 | UNASSIGNED | UNASSIGNED | `IP-1151` *(closed 2026-07-04 via VR-1151)*; IP-1131 *(VERIFIED 2026-10-17 via VR-1131, test-only — mutation-checked)* |
| FR-4310 | Pause / resume clock control | UNASSIGNED | ADR-0016 | C4, C6 | INT-0002 | UNASSIGNED | `spacesim/tests/test_white_only_controls.py::test_clock_controls_accepted_for_white`, `spacesim/tests/test_white_only_controls.py::test_clock_controls_refused_for_non_white`, `spacesim/tests/test_white_only_controls.py::test_config_controls_accepted_for_white`, `spacesim/tests/test_white_only_controls.py::test_config_controls_refused_for_non_white`, `spacesim/tests/test_white_only_controls.py::test_load_save_refused_for_non_white_accepted_for_white`, `spacesim/tests/test_white_only_controls.py::test_seat_assignment_and_observer_designation_refused_for_player_seats`, `spacesim/tests/test_white_only_controls.py::test_unknown_session_is_404_before_the_seat_check` | `IP-1060` *(closed 2026-07-04 via VR-1060)*; `IP-1068` *(`VERIFIED` 2026-10-24 via VR-1068: server refuses clock control from any seat but `white`)* |
| FR-4320 *(new 2026-10-23)* | White Cell controls refused for other seats | UNASSIGNED | ADR-0016, ADR-0015 | C4, C6 | INT-0002, INT-0003 | UNASSIGNED | `spacesim/tests/test_white_only_controls.py::test_clock_controls_accepted_for_white`, `spacesim/tests/test_white_only_controls.py::test_clock_controls_refused_for_non_white`, `spacesim/tests/test_white_only_controls.py::test_config_controls_accepted_for_white`, `spacesim/tests/test_white_only_controls.py::test_config_controls_refused_for_non_white`, `spacesim/tests/test_white_only_controls.py::test_load_save_refused_for_non_white_accepted_for_white`, `spacesim/tests/test_white_only_controls.py::test_seat_assignment_and_observer_designation_refused_for_player_seats`, `spacesim/tests/test_white_only_controls.py::test_unknown_session_is_404_before_the_seat_check` | `IP-1068` *(`VERIFIED` 2026-10-24 via VR-1068; `BL-0307`)* |
| FR-4410 | Inject authoring / firing | UNASSIGNED | ADR-0005 | C4, C6, C1 | INT-0002, INT-0016 | UNASSIGNED | UNASSIGNED | `IP-1060` *(closed 2026-07-04 via VR-1060)*, `IP-1061` (2026-09-26 — `BL-0062`–`BL-0064` remediation; `VERIFIED` 2026-09-27 via `VR-1061`), `IP-1063` (2026-10-11 — `BL-0129`/`BL-0188` inject fire-time validation, `spacesim/session/manager.py` `validate_inject_effects`; `COMPLETE`, awaiting `09-package-verification`); IP-1065 *(VERIFIED 2026-10-17 via VR-1065 — `app.js` `fireInject` shows a rejection)* |
| FR-4420 *(new 2026-09-26, `BL-0070`/B4; Precondition amended 2026-10-17, `BL-0130`)* | Condition-triggered injects, evaluated deterministically | UNASSIGNED | ADR-0002, ADR-0005, ADR-0006 | C2, C1 | INT-0016 | FS-106 | UNASSIGNED | IP-1062 *(VERIFIED 2026-09-28 via `VR-1062` v2.0, second pass)*; IP-1064 *(VERIFIED 2026-10-17 via `VR-1064` v2.0, second pass — `BL-0278` fix independently reconfirmed and generalized beyond the two shipped regression cases; as built: measured value in the firing record (`content/vignette.py::_measure_metric`, captured before `_apply_inject_effects` in `manager.py::_h_condition_check`), start-anchored tick grids (`_arm_schedule`, `BusSystem.schedule_ticks`), one log scan per tick)* |
| FR-4430 *(new 2026-09-26, `BL-0070`/B4)* *(Notes added 2026-10-17, `BL-0101`)* | New inject effect types (anomaly, sensor outage, custody loss, scripted manoeuvre) | UNASSIGNED | ADR-0004, ADR-0005 | C2, C1 | INT-0016 | FS-106 | UNASSIGNED | IP-1062 *(VERIFIED 2026-09-28 via `VR-1062` v2.0, second pass — the v1.0 `anomaly`/bus H1 defect (`BL-0128`) is fixed: `enter_safe_mode()`/`exit_safe_mode()` are now called, independently reconfirmed including `begin_recovery` acceptance. `BL-0129` (malformed-payload mid-handler exception) remains open, tracked separately)*, `IP-1063` (2026-10-11 — `BL-0129`/`BL-0188` inject fire-time validation, `spacesim/session/manager.py` `validate_inject_effects`; `COMPLETE`, awaiting `09-package-verification`) |
| FR-4440 *(new 2026-09-27, `BL-0074`/B8)* | Space-weather-index-driven anomaly rate scaling | R131 (v1.2) | ADR-0002, ADR-0006, ADR-0039 | C2, C1 | INT-0016 | FS-123 | UNASSIGNED | IP-1230 *(✅ VERIFIED 2026-10-18, run #194, VR-1230)* — `session/manager.py` (`_h_env_anomaly_check`, gated `env_anomaly_check` arm in `_arm_schedule`, `space_weather` inject key-update + `index_series`), `engine/perturbations.py` (`anomaly_rate_multiplier`), `content/vignette.py` (`environmental_anomalies`) |
| FR-4450 *(new 2026-10-03, `BL-0079`/B13)* | Edit or cancel a scheduled inject before it fires | UNASSIGNED | ADR-0005, ADR-0002 | C4, C6, C1 | INT-0002, INT-0016 | FS-106 (v2.3) | UNASSIGNED | IP-1066 *(✅ VERIFIED 2026-10-18, run #194, VR-1066)* — `session/manager.py` (`pending_injects`, `cancel_inject`, `edit_inject`, `_inject_overrides`, `_h_inject_admin`, `_h_inject` skip, `_h_condition_check`, `_arm_schedule` re-arm, `fire_inject` handle), `session/inprocess.py`, `ui_web/server.py` (`/injects/pending`, `/injects/{handle}/cancel`, `/edit`), `ui_web/static/app.js` (`renderPendingInjects`) |
| FR-4510 | Classification banner set and displayed | UNASSIGNED | (none directly) | C4, C6, C12 | INT-0002, INT-0001 | UNASSIGNED | UNASSIGNED | `IP-1120` *(closed 2026-07-04 via VR-1120 — VERIFIED; Title column defect above re-confirmed present, tracked as BL-0010)* |
| FR-4610 | (manual adjudication / custody-adjacent leaf, ADR-0004) | UNASSIGNED | ADR-0004 | C4, C6, C2, C1 | INT-0002, INT-0007 | UNASSIGNED | UNASSIGNED | `session/manager.py` *(closed 2026-07 via IP-1060 v2.0, independently confirmed 2026-07-04 via VR-1060)* |
| FR-4620 *(new 2026-10-03, `BL-0079`/B13)* | Side-by-side controller view: each cell's picture beside truth | UNASSIGNED | ADR-0004 | C4, C6, C2, C1 | INT-0002, INT-0007 | FS-106 (v2.3) | UNASSIGNED | IP-1067 *(✅ VERIFIED 2026-10-18, run #194, VR-1067)* — `session/manager.py` (`controller_view`), `session/inprocess.py` (`controller_view`, one `_locked_read`), `ui_web/server.py` (`/controller_view`, White-only), `ui_web/static/app.js` (`refreshComparePanel`), `index.html` (`#compare-panel`) |
| FR-4710 | No automated scoring / manual adjudication | UNASSIGNED | ADR-0017, ADR-0029 | C4, C6 | (none — absence of an interface) | UNASSIGNED | UNASSIGNED | (inspection — no outbound interface returns a score field) *(closed 2026-07 via IP-1060 v2.0, independently reconfirmed 2026-07-04 via VR-1060 — grepped `session/manager.py`/`ui_web/server.py` for any score/win-loss field, zero hits)* |
| FR-4720 | Adjust safe-mode dials / live parameters mid-exercise *(new leaf, CHG-003)* | UNASSIGNED | (none directly) | C4, C6 | INT-0002 | UNASSIGNED | UNASSIGNED | `session/manager.py` *(closed 2026-07 via IP-1060 v2.0, independently confirmed 2026-07-04 via VR-1060)* |
| FR-5110 | Scenario builder | UNASSIGNED | ADR-0027 | C4, C6, C5 | INT-0003 | UNASSIGNED | UNASSIGNED | IP-1173 *(VERIFIED 2026-07-11; corrects this cell's prior `content/vignette.py` citation, which named the vignette schema/loader, not the iterative-composition capability `FR-5110` actually describes)* |
| FR-5120 | Synchronized JSON view | UNASSIGNED | (none directly) | C4, C2 | INT-0003 | FS-117 | UNASSIGNED | `IP-1174` *(VERIFIED 2026-09-28 via `VR-1174` v2.0, second pass — the v1.0 `FR-5160` defect this row's prior annotation described has been remediated (`BL-0123`) and independently reconfirmed)* |
| FR-5130 | 2D/3D initial-state preview | UNASSIGNED | ADR-0004 | C4, C2 | (none — reuses existing render pipeline) | FS-117 | UNASSIGNED | `IP-1174` *(VERIFIED 2026-09-28 via `VR-1174` v2.0, second pass)* |
| FR-5140 | TLE/lat-long asset entry | R101, R107 | (none directly) | C4, C2 | INT-0003 | FS-117 | UNASSIGNED | `IP-1174` *(VERIFIED 2026-09-28 via `VR-1174` v2.0, second pass; `BL-0124`/`BL-0125` input-validation fixes on `force/ground` independently reconfirmed)* |
| FR-5150 | Asset menu (edit/reassign/delete) | UNASSIGNED | (none directly) | C4, C2 | INT-0003 | FS-117 | UNASSIGNED | `IP-1174` *(VERIFIED 2026-09-28 via `VR-1174` v2.0, second pass)* |
| FR-5160 | Seat-count declaration + role matrix | UNASSIGNED | (none directly) | C4, C2 | INT-0002 | FS-117 | UNASSIGNED | `IP-1174` *(VERIFIED 2026-09-28 via `VR-1174` v2.0, second pass — `BL-0123`'s caller/target-cell conflation is fixed: `declare_seats` now takes caller identity as the `cell` query param, target cell as `req.cell`; independently reconfirmed per-cell (white/blue/red) seat declaration)* |
| FR-5170 | Typed per-payload-type parameter sub-schemas | R109, R110, R129, R134, R137 | (none directly) | C1, C5 | (none — Domain Model/content-schema extension) | FS-117 | UNASSIGNED | IP-1170 *(`VERIFIED` — closes the weather/mw engine-precondition slice, `BL-0053`)*, IP-1171 *(`VERIFIED` 2026-07-12, `VR-1171` — closes the typed-sub-schema/UI-facing scope)* |
| FR-5180 | Typed bus parameter sub-schemas (power/propulsion) | R111, R112 | (none directly) | C1, C5 | (none directly) | FS-117 | UNASSIGNED | IP-1171 *(`VERIFIED` 2026-07-12, `VR-1171`)* |
| FR-5210 | Manual TLE / Keplerian asset entry *(reworded 2026-10-23: Space-Track dropped, `BL-0299`)* | UNASSIGNED | ADR-0018 | C5, C10 | INT-0013 | UNASSIGNED | UNASSIGNED | `content/` (TLE import) |
| FR-5220 *(new 2026-09-26, `BL-0067`/B1)* | Bulk TLE and CCSDS OMM multi-object import | UNASSIGNED | ADR-0018 | C4, C2, C5 *(corrected 2026-10-17, `BL-0263`; was C5, C10)* | INT-0006, INT-0011 *(ICD pass 3; was INT-0013, stretched shape)* | FS-119 | UNASSIGNED | IP-1190 *(`VERIFIED` 2026-09-27 via `VR-1190`)*; IP-1065 *(VERIFIED 2026-10-17 via VR-1065 — `SessionManager.bulk_import` per-file duplicate refusal)* |
| FR-5310 | Vignette loading | UNASSIGNED | ADR-0007 | C2, C5 | INT-0011 | FS-131 *(2026-10-16)* | UNASSIGNED | `content/vignette.py` (`validate_vignette`, `VignetteValidationError`, `load_vignette`), `session/inprocess.py` (`load_vignette`), `ui_web/server.py` (`_vignette_load_errors`), `static/app.js` (`loadSession`) — IP-1310 |
| FR-5311 *(new 2026-10-16, `BL-0235`)* | TLE-sourced orbits parse at load | UNASSIGNED | ADR-0007 | C5, C1 | INT-0011 | FS-131 | UNASSIGNED | `content/vignette.py` (`validate_vignette`) — IP-1310 |
| FR-5312 *(new 2026-10-16, `BL-0234`; amended run #144, `BL-0241`)* | Space assets carry an orbit, non-cyber terrestrial assets a location | UNASSIGNED | ADR-0007, ADR-0012 | C5 | INT-0011 | FS-131 (v1.1) | UNASSIGNED | `content/vignette.py` (`validate_vignette`) — IP-1310 |
| FR-5313 *(new 2026-10-16, `BL-0234`)* | Unique asset/sensor identifiers within a vignette | UNASSIGNED | ADR-0007 | C5 | INT-0011 | FS-131 | UNASSIGNED | `content/vignette.py` (`validate_vignette`) — IP-1310 |
| FR-5314 *(new 2026-10-16, `BL-0234`)* | `roles_needed` names a declared asset or group | UNASSIGNED | ADR-0007 | C5, C2 | INT-0011 | FS-131 | UNASSIGNED | `content/vignette.py` (`validate_vignette`) — IP-1310 |
| FR-5410 *(new 2026-09-26, `BL-0082`/B16)* | Load vignettes from configured external directories | UNASSIGNED | ADR-0007, ADR-0018 | C2, C5 | INT-0011 | FS-118 | UNASSIGNED | IP-1180 *(`VERIFIED` 2026-09-27 via `VR-1180`)*; IP-1065 *(VERIFIED 2026-10-17 via VR-1065 — `app.js` `loadVignettes` groups by `origin`)* |
| FR-5420 *(new 2026-09-26, `BL-0082`/B16)* | `save_vignette` writes only to a configured user directory | UNASSIGNED | ADR-0007, ADR-0022 | C2, C5 | INT-0011, INT-0012 | FS-118 | UNASSIGNED | IP-1180 *(`VERIFIED` 2026-09-27 via `VR-1180`)* |
| FR-5510 *(new 2026-09-26, `BL-0071`/B5)* | Save a running session's current state as a new starting vignette | UNASSIGNED | ADR-0022, ADR-0007 | C2, C5, C11 | INT-0011, INT-0012 | FS-120 | UNASSIGNED | IP-1200 *(`VERIFIED` 2026-09-27 via `VR-1200`)*; IP-1065 *(VERIFIED 2026-10-17 via VR-1065 — White-only Session-menu control)* |
| FR-6110 | SessionAPI seam (base) | UNASSIGNED | ADR-0002, ADR-0003 | C4, C2 | INT-0006 | UNASSIGNED | UNASSIGNED | `session/api.py` *(pre-package build, Phases 0–5; no IP — GDS-10 F4)* |
| FR-6210 | Fog-of-war filtering | UNASSIGNED | ADR-0004 | C4, C2, C1 | INT-0006, INT-0007 | UNASSIGNED | UNASSIGNED | `session/cells.py` |
| FR-6220 *(named set enumerated 2026-10-17, `BL-0138`)* | Documented no-cell ground-truth exception | UNASSIGNED | ADR-0004, ADR-0015 | C4, C12, C9 | INT-0001, INT-0005 | UNASSIGNED | UNASSIGNED | `session/cells.py` |
| FR-6310 | Server-authoritative lazy clock | UNASSIGNED | ADR-0014, ADR-0026 | C4, C12, C2 | INT-0001, INT-0006 | UNASSIGNED | UNASSIGNED | `IP-1090` *(closed 2026-07-04 via VR-1090)* |
| FR-6320 | Per-session RLock | UNASSIGNED | ADR-0014, ADR-0026 | C4, C2 | INT-0006 | UNASSIGNED | UNASSIGNED | `IP-1090` *(closed 2026-07-04 via VR-1090)* |
| FR-6410 | Session discovery / join-by-hash | UNASSIGNED | ADR-0014 | C4, C12, C2 | INT-0001, INT-0006 | UNASSIGNED | UNASSIGNED | `IP-1090` *(closed 2026-07-04 via VR-1090)* |
| FR-6510 | Observer read-only view with no command ability | UNASSIGNED | ADR-0004 | C4, C9, C2 | INT-0005, INT-0006 | UNASSIGNED | UNASSIGNED | `IP-1130` *(closed 2026-07-04 via VR-1130 — VERIFIED; Title column defect above re-confirmed present, tracked as BL-0012)*; IP-1131 *(VERIFIED 2026-10-17 via VR-1131, test-only — mutation-checked)* |
| FR-6610 | Hot-seat hand-off / screen-blank menu *(new leaf, CHG-004)* | UNASSIGNED | ADR-0004 | C4, C12, C2 | INT-0001, INT-0006 | UNASSIGNED | UNASSIGNED | `IP-1140` *(closed 2026-07-03 via VR-1140 — hard postcondition only; trigger/menu literal wording adjudicated NOT satisfied, see VR-1140's Adjudication section)* |
| FR-7110 | Event log | UNASSIGNED | ADR-0002 | C2, C1 | INT-0008, INT-0014 | UNASSIGNED | UNASSIGNED | `engine/eventlog.py` *(pre-package build, Phases 0–5; no IP — GDS-10 F4)* |
| FR-7210 | Save / resume | UNASSIGNED | ADR-0022 | C2, C5, C11 | INT-0012 | UNASSIGNED | `spacesim/tests/test_self_contained_save.py::test_content_portion_extracts_and_loads_as_a_fresh_vignette`, `spacesim/tests/test_self_contained_save.py::test_content_portion_world_matches_baseline_without_force_edits`, `spacesim/tests/test_self_contained_save.py::test_force_added_assets_survive`, `spacesim/tests/test_self_contained_save.py::test_immediate_round_trip_every_shipped_vignette`, `spacesim/tests/test_self_contained_save.py::test_invalid_baseline_refused_and_no_session`, `spacesim/tests/test_self_contained_save.py::test_invalid_content_portion_refused_with_problems_and_no_session`, `spacesim/tests/test_self_contained_save.py::test_legacy_save_resumes_by_id_with_warning`, `spacesim/tests/test_self_contained_save.py::test_resume_after_vignette_file_deleted_or_renamed`, `spacesim/tests/test_self_contained_save.py::test_resume_after_vignette_file_is_edited`, `spacesim/tests/test_self_contained_save.py::test_resume_in_a_fresh_inprocess_session`, `spacesim/tests/test_self_contained_save.py::test_save_keeps_every_pre_existing_key`, `spacesim/tests/test_self_contained_save.py::test_simulator_version_mismatch_resumes_with_warning_naming_both` | `IP-1100` *(closed 2026-07-04 via VR-1100)*; `IP-1101` *(VERIFIED 2026-10-24 via VR-1101)* |
| FR-7220 | Save-file content/session ownership split *(new leaf, CHG-007)* | UNASSIGNED | ADR-0022 | C2, C5, C11 | INT-0011, INT-0012 | UNASSIGNED | `spacesim/tests/test_self_contained_save.py::test_content_portion_extracts_and_loads_as_a_fresh_vignette`, `spacesim/tests/test_self_contained_save.py::test_content_portion_world_matches_baseline_without_force_edits` | `session/manager.py` *(closed 2026-07 via IP-1100, independently confirmed 2026-07-04 via VR-1100)* — **not met as built (2026-10-23): the save carries only the vignette ID and overrides, not its content (GDS-07 §6); `FR-7230`**; `IP-1101` *(VERIFIED 2026-10-24 via VR-1101)* — *"not met as built" note stands until `VERIFIED`* |
| FR-7230 *(new 2026-10-23)* | Resume independent of the original vignette file | UNASSIGNED | ADR-0022, ADR-0002 | C2, C5 | INT-0012 | UNASSIGNED *(`BL-0302`: feature specification pending)* | `spacesim/tests/test_self_contained_save.py::test_content_portion_extracts_and_loads_as_a_fresh_vignette`, `spacesim/tests/test_self_contained_save.py::test_content_portion_world_matches_baseline_without_force_edits`, `spacesim/tests/test_self_contained_save.py::test_force_added_assets_survive`, `spacesim/tests/test_self_contained_save.py::test_immediate_round_trip_every_shipped_vignette`, `spacesim/tests/test_self_contained_save.py::test_invalid_baseline_refused_and_no_session`, `spacesim/tests/test_self_contained_save.py::test_invalid_content_portion_refused_with_problems_and_no_session`, `spacesim/tests/test_self_contained_save.py::test_legacy_save_resumes_by_id_with_warning`, `spacesim/tests/test_self_contained_save.py::test_resume_after_vignette_file_deleted_or_renamed`, `spacesim/tests/test_self_contained_save.py::test_resume_after_vignette_file_is_edited`, `spacesim/tests/test_self_contained_save.py::test_resume_in_a_fresh_inprocess_session`, `spacesim/tests/test_self_contained_save.py::test_save_keeps_every_pre_existing_key`, `spacesim/tests/test_self_contained_save.py::test_simulator_version_mismatch_resumes_with_warning_naming_both` | `IP-1101` *(VERIFIED 2026-10-24 via VR-1101)* |
| FR-7310 | AAR replay/scrub | UNASSIGNED | ADR-0002 | C2, C1 | INT-0014 | UNASSIGNED | UNASSIGNED | `IP-1070` *(closed 2026-07-04 via VR-1070)* |
| FR-7320 | AAR branch compare | UNASSIGNED | ADR-0002 | C2, C1 | INT-0014 | UNASSIGNED | UNASSIGNED | `IP-1070` *(closed 2026-07-04 via VR-1070)* |
| FR-7330 *(new 2026-09-27, `BL-0078`/B12)* | Variable-speed AAR replay from truth or a single cell's viewpoint | UNASSIGNED | ADR-0002, ADR-0004 | C2, C1, C4 | INT-0014, INT-0006 | FS-128 | UNASSIGNED | IP-1280 *(VERIFIED 2026-09-28 via VR-1280)* |
| FR-7410 *(new 2026-09-26, `BL-0069`/B3; one asset per export, 2026-10-17, `BL-0137`)* | Truth ephemeris export (ECI/RIC, CSV/CCSDS OEM) | R101 | ADR-0004, ADR-0015 | C2, C1 | INT-0014 *(stretched shape — see `reviews/requirements-update-must-tier-batch.md` Finding 6)* | FS-121 | UNASSIGNED | IP-1210 *(remediated 2026-09-27/28 — ω×ρ term added, OEM CCSDS-conformant; awaiting fresh `09-package-verification`)*; IP-1261 *(COMPLETE 2026-10-11 — time-span sampling migrated onto `session/aar.py::worlds_at_times`, output unchanged, `spacesim/tests/test_ephemeris.py::test_ephemeris_exports_unchanged_after_migration`; awaiting `09-package-verification`)*; IP-1262 *(COMPLETE 2026-10-11, `BL-0176` remediation — explicit `interval_s` must be finite/`> 0` and sampling is capped at `session/ephemeris.py::MAX_EXPORT_SAMPLES` (10,000) in `sample_times`; 400 at the route. Tests: `spacesim/tests/test_ephemeris.py::test_sample_times_rejects_non_positive_or_non_finite_interval`, `::test_sample_times_enforces_sample_count_ceiling_arithmetically`, `::test_ephemeris_exports_propagate_over_ceiling_rejection`, `spacesim/tests/test_web.py::test_ephemeris_routes_reject_non_positive_interval_400`; awaiting `09-package-verification`)* |
| FR-7420 *(new 2026-09-26, `BL-0069`/B3 — blocked on `BL-0068`/B2, see `reviews/requirements-update-must-tier-batch.md` Finding 4)* | Cell-observed ephemeris export (ECI/RIC, CSV/CCSDS OEM) | UNASSIGNED | ADR-0004, ADR-0013 | C2, C1, C3 | INT-0007 | FS-121 | UNASSIGNED | IP-1210 *(remediated 2026-09-27/28 — ω×ρ term added, OEM CCSDS-conformant; awaiting fresh `09-package-verification`)*; IP-1261 *(COMPLETE 2026-10-11 — time-span sampling migrated onto `session/aar.py::worlds_at_times`, output unchanged, `spacesim/tests/test_ephemeris.py::test_ephemeris_exports_unchanged_after_migration`; awaiting `09-package-verification`)*; IP-1262 *(COMPLETE 2026-10-11, `BL-0176` remediation — explicit `interval_s` must be finite/`> 0` and sampling is capped at `session/ephemeris.py::MAX_EXPORT_SAMPLES` (10,000) in `sample_times`; 400 at the route. Tests: `spacesim/tests/test_ephemeris.py::test_sample_times_rejects_non_positive_or_non_finite_interval`, `::test_sample_times_enforces_sample_count_ceiling_arithmetically`, `::test_ephemeris_exports_propagate_over_ceiling_rejection`, `spacesim/tests/test_web.py::test_ephemeris_routes_reject_non_positive_interval_400`; awaiting `09-package-verification`)* |
| FR-7430 *(new 2026-09-27, owner decision closing `BL-0136`)* | Companion RIC-specific ephemeris export file | UNASSIGNED | (none directly) | C2, C1 | INT-0014 | FS-121 *(v2.0, 2026-10-10)* | UNASSIGNED | IP-1210 *(implemented 2026-09-27/28 as part of the same remediation pass — `write_ric_csv()` + `format=ric` route option; awaiting fresh `09-package-verification`)* |
| FR-7440 *(new 2026-10-03, `BL-0109`; amended 2026-10-15, `BL-0159` — own satellites now in scope, remediation package owed against `IP-1211`)* | Quick TLE export for a cell-visible satellite (own or tracked) | R101 *(TLE format)* | ADR-0004 | C4, C2, C1 | INT-0006, INT-0007 | FS-121 *(v2.0, 2026-10-10)* | UNASSIGNED | IP-1211 *(VERIFIED 2026-10-10 via [VR-1211](../implementation/verification/VR-1211-quick-tle-export.md) — `engine/tle_export.py::state_to_tle`/`tle_identity`, `session/ephemeris.py::quick_tle`, `SessionManager`/`InProcessSession.get_tle`, `GET /tle/{cell}`, `ui_web/static/tleexport.js`; `BL-0164` adjudicated `DONE`, accepted)*; **IP-1212** *(VERIFIED 2026-10-15 via [VR-1212](../implementation/verification/VR-1212-own-satellite-tle-export.md) — own-satellite scope of the amended `FR-7440`: `session/ephemeris.py::quick_tle` own-asset branch, `ui_web/static/tleexport.js` picker; tests `test_ephemeris.py::test_quick_tle_own_satellite_uses_actual_orbit`/`::test_quick_tle_other_cell_still_rejected_for_untracked_satellite`/`::test_quick_tle_ownership_beats_a_held_track`, `test_web.py::test_tle_route_own_satellite_200`/`::test_tle_export_client_lists_own_satellites`; `BL-0201`/`BL-0159` closed, accepted)* |
| FR-8110 | Operator console (web UI over the API) | UNASSIGNED | ADR-0008 | C4, C12 | INT-0001 | UNASSIGNED | UNASSIGNED | `ui_web/server.py`, `ui_web/static/` *(pre-package build, Phases 0–5; no IP — GDS-10 F4)* |
| FR-8210 *(new 2026-10-03, `BL-0107`)* | Live, operator-selectable RIC-frame relative-motion view | R127 *(v1.1)* | ADR-0004, ADR-0008 | C4, C12, C2, C1 | INT-0001, INT-0006, INT-0007 | FS-130 | UNASSIGNED | IP-1300 *(VERIFIED 2026-10-10 via VR-1300 — `session/ephemeris.py::live_ric_view`, `SessionManager`/`InProcessSession.get_ric_view`, `GET /ric_view/{cell}`, `ui_web/static/ricview.js`)* |
| FR-8220 *(new 2026-10-03, `BL-0111`)* | CATS illumination-phase-angle overlay for the RIC view's selected chase satellite | R109 *(v1.3 §3.11)* | ADR-0004 | C4, C12 | INT-0001 | FS-130 | UNASSIGNED | IP-1300 *(VERIFIED 2026-10-10 via VR-1300 — `engine/sun.py::cats_phase_angle_deg` (the single shared phase-angle function, `BL-0152`), unbanded readout per Design Decision 4)* |
| FR-9110 | AI-Red substitution for unseated Red | UNASSIGNED | ADR-0021, ADR-0024 | C2, C1, C8 | INT-0008, INT-0015 | `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity" | UNASSIGNED | `IP-1110` *(closed 2026-07-04 via VR-1110)* |
| FR-10110 *(new 2026-07, promoted from CR-19)* | Automated non-aggregating competency rubric-tier computation | R306, R310 | ADR-0017, ADR-0032 | C2, C1 | INT-0002 | UNASSIGNED | `tests/test_assessment.py`, `tests/test_orders.py` | `IP-2010` *(closed 2026-07-04 via VR-2010 — VERIFIED; two Medium findings filed against FS-201's own Acceptance Criteria scope, not against this closure, see VR-2010)* |
| FR-10210 *(new 2026-07, promoted from CR-20)* | Multi-run/cohort structured research-data export | UNASSIGNED | ADR-0029, ADR-0033 | C1, C2 | UNASSIGNED | UNASSIGNED | `tests/test_research_batch.py` | `IP-3010` *(closed 2026-07-04 via VR-3010 — VERIFIED)* |

`FR-10210`'s Interface cell remains honestly `UNASSIGNED` even after implementation — FS-301's own
Open Questions flag that no ICD interface covers the research-export boundary (it is an
offline/CLI-style utility, not a live session-facing seam), and `IP-3010`'s implementation
confirms this: `run_batch()` is a plain importable function, not a route over any existing
`INT-xxxx`. Arch. Component/Test/Impl. Package cells closed 2026-07-04 via `IP-3010`. `FR-10110`'s
cells were filled 2026-07-03 once `IP-2010` reached `COMPLETE` — Arch. Component/Interface follow
that package's own Architecture Components/Interfaces fields exactly (no interface is invented;
`INT-0002` is the pre-existing surface `IP-2010`'s report panel is hosted within, not a new ICD
boundary — the interface gap FS-201's Open Questions flagged is a Phase 8 "should this get its own
`INT-xxxx`" question, unaffected by this cell now being filled).

| FR-11110 *(new 2026-07-04, training-corpus elevation)* | Role-scoped manual coverage per seat | R601, R602 | (none identified) | UNASSIGNED | (none — documentation artifact) | UNASSIGNED | UNASSIGNED | `docs/training/12-white-cell-manual.md`, `docs/training/13-blue-cell-manual.md`, `docs/training/14-red-cell-manual.md` |
| FR-11120 *(new 2026-07-04)* | Section-level source anchoring | R606 | (none identified) | UNASSIGNED | (none — documentation artifact) | UNASSIGNED | UNASSIGNED | `docs/training/12-white-cell-manual.md`–`14-red-cell-manual.md` (`> Sources:` footers) |
| FR-11210 *(new 2026-07-04)* | Feature ⇄ manual bidirectional index | R606 | (none identified) | UNASSIGNED | (none — documentation artifact) | UNASSIGNED | UNASSIGNED | `docs/training/15-manual-traceability.md` |
| FR-11310 *(new 2026-07-04)* | Sequenced learning path over the vignette library | R605 | (none identified) | UNASSIGNED | (none — documentation artifact) | UNASSIGNED | UNASSIGNED | `docs/training/16-learning-path.md` |
| FR-11320 *(new 2026-07-04)* | Per-rung manual linkage | R601, R605 | (none identified) | UNASSIGNED | (none — documentation artifact) | UNASSIGNED | UNASSIGNED | `docs/training/16-learning-path.md` |
| FR-11410 *(new 2026-07-04)* | Training-artifact update rides the changing package | UNASSIGNED | (none identified) | UNASSIGNED | (none — process requirement) | UNASSIGNED | UNASSIGNED | `.claude/skills/08-code-implementation/SKILL.md`, `.claude/skills/10-integration-review/SKILL.md` (hook text) |
| FR-11420 *(new 2026-07-04)* | Machine-verified vignette playbooks | R605, R608 | (none identified) | UNASSIGNED | (none) | UNASSIGNED | `spacesim/tests/test_vignette_tutorials.py` | `spacesim/content/vignettes/*.yaml` (`tutorial:` blocks), `docs/training/11-vignette-playbooks.md` |

The `FR-11000` family *(training-corpus elevation, 2026-07-04)* traces to documentation and
process artifacts rather than `spacesim/` code — its "Impl. Package" cells name the real, on-disk
training artifacts that satisfy each leaf today (verified paths, not placeholders), while Arch.
Component/Interface cells are structurally `(none)`/`UNASSIGNED` because no ICD component or
interface models the documentation corpus. Research cells cite the R600 tier
(`docs/research/encyclopedia/R600-index.md`, authored 2026-07-04, 8/8 topics — pipeline run #16)
per each topic's own Feature Mapping field; `FR-11410` stays `UNASSIGNED` (a pure process
requirement with no single research topic as its direct grounding — R601-R608 collectively inform
it, but no one topic's Feature Mapping names it specifically). `FR-11420`'s Test cell is the
family's one live automated gate. R600's citations rest on this session's WebSearch-corroborated
sourcing rather than a fetch-and-confirm pass (see `encyclopedia/INDEX.md`'s R600 note, BL-0028) —
these Research cells should be re-confirmed once that verification pass runs.

### Candidate Requirements (CR-01–CR-25) — `CANDIDATE — NOT BASELINED`

Per the `04-requirements-engineering` skill's own discipline, Candidates get rows but most
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
| CR-19 *(new 2026-07 — **PROMOTED to FR-10110**, see master matrix above)* | Automated competency-assessment rubric computation | UNASSIGNED | ADR-0017 | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-20 *(**PROMOTED to FR-10210**, see master matrix above)* | Dedicated multi-run/cohort research-export interface | UNASSIGNED | ADR-0029 | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-21 | Human-subjects research authorization/ethics boundary | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-22 *(new 2026-10-15, `BL-0181`)* | Human-readable time bounds for time-span exports | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-23 *(new 2026-10-16, `BL-0235`)* | TLE checksum and epoch-sanity checks at load | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-24 *(new 2026-10-16, `BL-0234`)* | Load-time integrity of other in-vignette cross-references | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-25 *(new 2026-10-16, `BL-0226`)* | Range rules for order parameters | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-26 *(new 2026-10-17, `BL-0100`)* | Unreadable external vignette directory skipped and disclosed | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-27 *(new 2026-10-17, `BL-0130`)* | Re-fire rule for a repeatable condition-triggered inject | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| CR-28 *(new 2026-10-17, `BL-0249` — **PROMOTED to FR-1480** 2026-10-17, see master matrix above)* | A missed kinetic salvo consumes its rounds | UNASSIGNED | (none cited) | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED | UNASSIGNED |

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

The Architecture Component and Affected subsystems columns for NFRs are taken directly from
each NFR's own explicit "Affected subsystems" field (converted to the matching ICD component
where the named subsystem maps onto one), not separately inferred. The Impl. Package column
*(added 2026-10-17, `BL-0148`)* names a package only where a verification pass attributed one;
otherwise it is `UNASSIGNED`. Before this column existed, seven rows carried the attribution as an
unheaded ninth cell (`NFR-1300`/`1400`/`1500`/`1600`/`1800`/`2500`/`3100`).

| Req ID | Title (abridged) | Research | ADR | Arch. Component | Affected subsystems | Future Feature | Test | Impl. Package |
|---|---|---|---|---|---|---|---|---|
| NFR-1100 | Responsive UI at high time multipliers | UNASSIGNED | ADR-0009, ADR-0014 | C1, C2, C4 | `engine/` (propagator, access provider), `session/` (clock catch-up), `ui_web/` (client poll loop) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-1200 | Hardware-floor performance | UNASSIGNED | ADR-0019, ADR-0020 | C4 | `ui_web/static/` (globe.js, world.js, graph.js) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-1300 | Sizing soft guideline (~24 sats) | UNASSIGNED | ADR-0019 | C1, C2 | `engine/`, `session/` (clock-lag watchdog — `SessionManager._record_catch_up_lag`) | UNASSIGNED | `spacesim/tests/test_clock_lag_watchdog.py::test_average_above_point_eight_is_high`, `spacesim/tests/test_clock_lag_watchdog.py::test_average_falling_below_threshold_clears_the_warning`, `spacesim/tests/test_clock_lag_watchdog.py::test_fewer_than_four_samples_never_warn`, `spacesim/tests/test_clock_lag_watchdog.py::test_four_samples_above_threshold_give_a_medium_warning`, `spacesim/tests/test_clock_lag_watchdog.py::test_only_the_last_eight_samples_count`, `spacesim/tests/test_clock_lag_watchdog.py::test_warning_reaches_white_through_the_clock_route` | `IP-1061` (2026-09-26, `VERIFIED` 2026-09-27 via `VR-1061` — `BL-0065` removed the hard `ValueError` this row's own guideline had never been enforced-against; row's own `Impl. Package` cell was previously missing entirely, same defect class as `BL-0009`/`BL-0034`); `IP-1091` (2026-10-23, `VERIFIED` 2026-10-24 via `VR-1091` — test-only; the clock-lag watchdog's verification target, `_record_catch_up_lag`, now has the six tests) |
| NFR-1400 | LAN concurrency ceiling | UNASSIGNED | ADR-0026, ADR-0014 | C2, C4 | `session/inprocess.py` (`_locked` critical section), `ui_web/server.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-1500 | Determinism (engine-wide) | UNASSIGNED | ADR-0002 | C1 | `engine/` (all), `engine/eventlog.py`, `engine/simulation.py` | UNASSIGNED | `spacesim/tests/test_determinism.py::test_cannot_advance_backwards`, `spacesim/tests/test_determinism.py::test_different_seed_changes_random_outcome`, `spacesim/tests/test_determinism.py::test_property_replay_is_byte_identical`, `spacesim/tests/test_determinism.py::test_replay_from_midway_snapshot_matches_live`, `spacesim/tests/test_determinism.py::test_replay_from_scratch_matches_live`, `spacesim/tests/test_determinism.py::test_save_round_trip_reproduces_state` | `engine/simulation.py` |
| NFR-1510 *(new 2026-10-23)* | Released builds install identical dependency versions | UNASSIGNED | ADR-0002, ADR-0020 | (build) | `pyproject.toml`, release lock file | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-1600 | Robustness to invalid input | UNASSIGNED | (none identified) | C5, C1 | `content/vignette.py`, `engine/orders.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-1610 *(new 2026-10-23)* | Failure-atomic event application | UNASSIGNED | ADR-0038, ADR-0002 | C1 | `engine/simulation.py`, `engine/handlers.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-1700 | Sub-stepped clock | UNASSIGNED | ADR-0002 | C1 | `engine/clock.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-1800 | Single-sitting availability | UNASSIGNED | (none identified) | C2 | `session/` (SessionManager) | UNASSIGNED | `spacesim/tests/test_self_contained_save.py::test_invalid_baseline_refused_and_no_session`, `spacesim/tests/test_self_contained_save.py::test_invalid_content_portion_refused_with_problems_and_no_session`, `spacesim/tests/test_self_contained_save.py::test_resume_in_a_fresh_inprocess_session` | UNASSIGNED; `IP-1101` *(VERIFIED 2026-10-24 via VR-1101)* |
| NFR-1900 | UI-agnostic engine *(80% coverage figure removed 2026-10-23, `BL-0299`)* | UNASSIGNED | ADR-0002, ADR-0007 | C1 | `engine/` (all), test suite | UNASSIGNED | `spacesim/tests/test_import_guard.py::test_engine_has_files`, `spacesim/tests/test_import_guard.py::test_engine_imports_no_ui_session_or_transport`, `spacesim/tests/test_import_guard.py::test_engine_reads_no_wall_clock`, `spacesim/tests/test_import_guard.py::test_engine_uses_no_dynamic_import`, `spacesim/tests/test_import_guard.py::test_guard_catches_byname_walltime`, `spacesim/tests/test_import_guard.py::test_guard_catches_dynamic_imports`, `spacesim/tests/test_import_guard.py::test_guard_catches_numpy_random`, `spacesim/tests/test_import_guard.py::test_only_rng_module_imports_random` | UNASSIGNED |
| NFR-2000 | Content as data | UNASSIGNED | ADR-0007 | C5 | `content/vignette.py`, `content/vignettes/*.yaml` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2010 | Additive vignette-schema evolution | UNASSIGNED | (none directly) | C5, C1 | `content/vignette.py`, `engine/bus.py`, `engine/orders.py` | FS-117 | UNASSIGNED | UNASSIGNED |
| NFR-2100 | Independently testable fidelity seams | UNASSIGNED | ADR-0009 | C1 | `engine/propagator.py`, `engine/access.py`, `engine/effects.py` | `FUTURE-WORK.md` §2 | UNASSIGNED | UNASSIGNED |
| NFR-2200 | Secure development practice | UNASSIGNED | ADR-0018 | C5 + all | `content/vignette.py`, all subsystems | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2300 | LAN trust boundary | UNASSIGNED | ADR-0015 | C2, C4 | `session/api.py` (SessionAPI, CellView), `ui_web/server.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2400 | State-hash data integrity | UNASSIGNED | ADR-0002 | C1 | `engine/eventlog.py` (Snapshot), `engine/world.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2410 *(new 2026-10-23)* | Read paths leave state unchanged | UNASSIGNED | ADR-0002 | C1, C2, C4 | `session/scene.py`, `engine/telemetry.py`, `engine/orders.py` (`dry_run`), `session/aar.py`, `session/ephemeris.py`, `session/manager.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2500 | Action log sufficiency | UNASSIGNED | ADR-0002 | C1, C2 | `engine/eventlog.py`, `session/aar.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2600 | Complete action log | UNASSIGNED | ADR-0017, ADR-0002, ADR-0038 | C1 | `engine/eventlog.py`, `engine/orders.py`, `engine/handlers.py` | UNASSIGNED | UNASSIGNED | `IP-1021` *(VERIFIED 2026-10-17, `VR-1021`)* |
| NFR-2700 | File-based server config | UNASSIGNED | (none identified) | C4 | `spacesim/config.py`, `spacesim/ui_web/server.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2800 | Test-driven gated build | UNASSIGNED | ADR-0002 | (all) | `spacesim/tests/` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2810 *(new 2026-10-23)* | Fidelity claims validated against cited reference values | UNASSIGNED | ADR-0009 | C1 | `engine/` (calibrated models), `docs/research/encyclopedia/` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-2820 *(new 2026-10-23)* | Every test declares the requirement or feature it verifies | UNASSIGNED | (none identified) | (all) | `spacesim/tests/`, `pyproject.toml` | UNASSIGNED | `spacesim/tests/test_test_origins.py::test_a_hand_edited_cell_is_reported_by_row_and_an_unknown_row_id_is_reported`, `spacesim/tests/test_test_origins.py::test_a_ledger_yielding_no_ids_fails_loudly`, `spacesim/tests/test_test_origins.py::test_a_misspelt_marker_fails_collection_under_strict_markers`, `spacesim/tests/test_test_origins.py::test_allowlist_only_shrinks`, `spacesim/tests/test_test_origins.py::test_every_collected_test_outside_the_allowlist_declares_an_origin`, `spacesim/tests/test_test_origins.py::test_every_declared_id_in_the_real_suite_resolves`, `spacesim/tests/test_test_origins.py::test_real_shaped_ids_resolve`, `spacesim/tests/test_test_origins.py::test_regeneration_changes_only_test_cells_and_is_idempotent`, `spacesim/tests/test_test_origins.py::test_report_lists_tests_for_an_id_and_requirements_no_test_names_and_writes_nothing`, `spacesim/tests/test_test_origins.py::test_the_committed_matrix_test_column_equals_the_generated_one`, `spacesim/tests/test_test_origins.py::test_the_live_baseline_resolves_one_of_each_kind`, `spacesim/tests/test_test_origins.py::test_the_report_command_names_the_determinism_gate_under_nfr_1500`, `spacesim/tests/test_test_origins.py::test_unknown_malformed_and_candidate_ids_are_reported_with_test_and_id`, `spacesim/tests/test_test_origins.py::test_untagged_synthetic_test_outside_the_allowlist_is_reported_by_name`, `spacesim/tests/test_test_origins.py::test_untagged_test_in_an_allowlisted_module_is_tolerated_but_a_fully_tagged_one_is_stale` | `IP-1330` *(`COMPLETE` 2026-10-23, awaiting `09`)* |
| NFR-2830 *(new 2026-10-23)* | Test relevance audited at each major release | UNASSIGNED | (none identified) | (none — process) | `spacesim/tests/`, `docs/requirements/` | UNASSIGNED | `spacesim/tests/test_test_origins.py::test_report_lists_tests_for_an_id_and_requirements_no_test_names_and_writes_nothing`, `spacesim/tests/test_test_origins.py::test_the_report_command_names_the_determinism_gate_under_nfr_1500` | `IP-1330` *(`COMPLETE` 2026-10-23, awaiting `09`)* |
| NFR-2840 *(new 2026-10-23)* | Load-bearing UI rules verified by automated browser tests | UNASSIGNED | ADR-0004, ADR-0008 | C4 | `ui_web/static/`, `spacesim/tests/` | UNASSIGNED | `spacesim/tests/test_browser_console_rules.py::test_a_refused_order_disables_issue_with_its_reason_before_any_issue`, `spacesim/tests/test_browser_console_rules.py::test_a_tracked_object_is_drawn_with_its_confidence_encoding`, `spacesim/tests/test_browser_console_rules.py::test_blue_view_names_no_red_object_blue_has_not_detected`, `spacesim/tests/test_browser_console_rules.py::test_cyber_asks_for_a_consequence_confirmation`, `spacesim/tests/test_browser_console_rules.py::test_engage_asks_for_a_consequence_confirmation`, `spacesim/tests/test_browser_console_rules.py::test_malformed_parameters_disable_issue_and_a_click_while_disabled_sends_nothing`, `spacesim/tests/test_browser_console_rules.py::test_observe_issues_with_no_confirmation`, `spacesim/tests/test_browser_console_rules.py::test_red_view_names_no_blue_object_red_has_not_detected`, `spacesim/tests/test_browser_console_rules.py::test_white_view_shows_the_objects_the_cells_cannot_see`, `spacesim/tests/test_browser_console_rules.py::test_without_a_browser_the_lookup_skips_with_a_reason_naming_the_missing_tool` | `IP-1340` *(`COMPLETE` 2026-10-23, awaiting `09`)* |
| NFR-2850 *(new 2026-10-23, `BL-0322`)* | Matrix Test column generated from declared test origins | UNASSIGNED | None | — | `requirements/03`, `spacesim/tests/` | UNASSIGNED | `spacesim/tests/test_test_origins.py::test_a_hand_edited_cell_is_reported_by_row_and_an_unknown_row_id_is_reported`, `spacesim/tests/test_test_origins.py::test_regeneration_changes_only_test_cells_and_is_idempotent`, `spacesim/tests/test_test_origins.py::test_the_committed_matrix_test_column_equals_the_generated_one` | `IP-1330` *(`COMPLETE` 2026-10-23, awaiting `09`)* |
| NFR-2900 | Windows-first portability | UNASSIGNED | ADR-0020 | (all) | Build/dependency manifest, `spacesim/` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3000 | Accessible presentation | UNASSIGNED | (none identified) | C4 | `ui_web/static/` (app.js, style.css, globe.js) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3010 *(new 2026-10-23)* | Belief visibly distinguishable from ground truth | UNASSIGNED | (none identified) | C4 | `ui_web/static/` (globe.js, world.js, symbology.js) | UNASSIGNED | `spacesim/tests/test_browser_console_rules.py::test_a_tracked_object_is_drawn_with_its_confidence_encoding`, `spacesim/tests/test_browser_console_rules.py::test_blue_view_names_no_red_object_blue_has_not_detected`, `spacesim/tests/test_browser_console_rules.py::test_red_view_names_no_blue_object_red_has_not_detected` | UNASSIGNED |
| NFR-3020 *(new 2026-10-23)* | Unavailable action states its reason before commit | UNASSIGNED | (none identified) | C1, C4 | `engine/orders.py` (`dry_run`), `ui_web/static/app.js` | UNASSIGNED | `spacesim/tests/test_browser_console_rules.py::test_a_refused_order_disables_issue_with_its_reason_before_any_issue`, `spacesim/tests/test_browser_console_rules.py::test_malformed_parameters_disable_issue_and_a_click_while_disabled_sends_nothing` | UNASSIGNED |
| NFR-3030 *(new 2026-10-23)* | Every panel obeys the panel-manager contract | UNASSIGNED | (none identified) | C4 | `ui_web/static/panels.js`, `index.html` | UNASSIGNED | `spacesim/tests/test_panel_registry.py::test_every_panel_in_the_page_is_registered_and_vice_versa`, `spacesim/tests/test_panel_registry.py::test_every_registered_panel_gets_panel_controls`, `spacesim/tests/test_panel_registry.py::test_menu_builder_filters_white_only_panels`, `spacesim/tests/test_panel_registry.py::test_the_two_white_only_panels_are_registered` | `IP-1069` *(`COMPLETE` 2026-10-24 after re-run, awaiting `09`)* |
| NFR-3040 *(new 2026-10-23)* | Summary and detail views agree | UNASSIGNED | (none identified) | C4 | `ui_web/static/graph.js`, `app.js` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3050 *(new 2026-10-23)* | Cause of a moving telemetry value shown | UNASSIGNED | (none identified) | C1, C4 | `engine/telemetry.py`, `ui_web/static/app.js` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3060 *(new 2026-10-23)* | White Cell sees the active Red doctrine preset | UNASSIGNED | ADR-0021, ADR-0024 | C2, C4 | `session/redai.py`, `ui_web/static/app.js` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3100 | Classification banner | UNASSIGNED | (none identified) | C4, C2 | `ui_web/static/` (banner component), `session/aar.py` | UNASSIGNED | UNASSIGNED | `IP-1120` *(closed 2026-07-04 via VR-1120 — VERIFIED)* |
| NFR-3200 | No network access; TLE/OMM by paste or file *(reworded 2026-10-23, `BL-0299`)* | UNASSIGNED | ADR-0018 | C5, C4 | `content/` (TLE/OMM parsing), `session/` (force-add) | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3300 | Browser-only client, no external integration | UNASSIGNED | (none identified) | C4 | `ui_web/server.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3400 *(new 2026-07-04, training-corpus elevation)* | Training-artifact accuracy (as-built only) | UNASSIGNED | (none identified) | (none — documentation) | `docs/training/`, `spacesim/content/vignettes/*.yaml` | UNASSIGNED | UNASSIGNED | IP-1131 *(VERIFIED 2026-10-17 via VR-1131, test-only — mutation-checked)*; IP-1065 *(VERIFIED 2026-10-17 via VR-1065 — `tools/render_manual.py` `s_ref_tasking`/`s_ref_compose` redraw `docs/manual/ref-05-tasking.png`/`ref-06-compose.png` to the shipped known-target picker, `BL-0185`; verified by inspection + pixel-identical regeneration, no automated test; RTM cell added by VR-1065)* |
| NFR-3500 *(new 2026-07-04)* | Modularity/retrievability of training modules | UNASSIGNED | (none identified) | (none — documentation) | `docs/training/` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3600 *(new 2026-07-04)* | Learner-appropriate presentation | R601–R608 (8/8 authored — see each topic's Feature Mapping for its specific manual/vignette target) | (none identified) | (none — documentation) | `docs/training/`, vignette `intro_brief`/`tutorial`/`coaching` blocks | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3800 *(new 2026-10-23)* | Relative links in live documents resolve | UNASSIGNED | (none identified) | (none — documentation) | `docs/` | UNASSIGNED | `spacesim/tests/test_doc_integrity.py::test_allow_list_gate_is_shrink_only`, `spacesim/tests/test_doc_integrity.py::test_real_tree_has_no_unlisted_broken_relative_link`, `spacesim/tests/test_doc_integrity.py::test_synthetic_broken_link_reported_with_file_line_target_and_exemptions` | `IP-1350` *(`COMPLETE` 2026-10-23, awaiting `09`)* |
| NFR-3810 *(new 2026-10-23)* | No live reference to a retired document | UNASSIGNED | (none identified) | (none — documentation) | `docs/` | UNASSIGNED | UNASSIGNED | UNASSIGNED |
| NFR-3820 *(new 2026-10-23)* | Each index agrees with its folder | UNASSIGNED | (none identified) | (none — documentation) | `docs/**/INDEX.md` | UNASSIGNED | `spacesim/tests/test_doc_integrity.py::test_allow_list_gate_is_shrink_only`, `spacesim/tests/test_doc_integrity.py::test_real_tree_every_index_lists_its_folders_documents`, `spacesim/tests/test_doc_integrity.py::test_synthetic_sub_index_listing_counts`, `spacesim/tests/test_doc_integrity.py::test_synthetic_unlisted_document_reported_with_index_and_document` | `IP-1350` *(`COMPLETE` 2026-10-23, awaiting `09`)* |
| NFR-3830 *(new 2026-10-23)* | Status ledgers agree | UNASSIGNED | (none identified) | (none — documentation) | `ROADMAP.md`, `docs/implementation/`, `docs/architecture/INDEX.md`, `docs/features/`, `spacesim/tests/` | UNASSIGNED | `spacesim/tests/test_doc_integrity.py::test_allow_list_gate_is_shrink_only`, `spacesim/tests/test_doc_integrity.py::test_real_tree_status_ledgers_agree`, `spacesim/tests/test_doc_integrity.py::test_synthetic_ledger_disagreements_name_item_and_both_statuses`, `spacesim/tests/test_doc_integrity.py::test_synthetic_ledger_with_no_rows_fails_loudly` | `IP-1350` *(`COMPLETE` 2026-10-23, awaiting `09`)* |
| NFR-3840 *(new 2026-10-23)* | Every declared test origin resolves | UNASSIGNED | (none identified) | (none — documentation) | `spacesim/tests/`, `docs/requirements/` | UNASSIGNED | `spacesim/tests/test_test_origins.py::test_a_ledger_yielding_no_ids_fails_loudly`, `spacesim/tests/test_test_origins.py::test_every_declared_id_in_the_real_suite_resolves`, `spacesim/tests/test_test_origins.py::test_real_shaped_ids_resolve`, `spacesim/tests/test_test_origins.py::test_the_live_baseline_resolves_one_of_each_kind`, `spacesim/tests/test_test_origins.py::test_unknown_malformed_and_candidate_ids_are_reported_with_test_and_id` | `IP-1330` *(`COMPLETE` 2026-10-23, awaiting `09`)* |
| NFR-3700 *(new 2026-09-26, `BL-0082`/B16)* | Path-traversal safety generalized to external content roots | UNASSIGNED | ADR-0007, ADR-0018 | C5 | `content/vignette.py` (`_validate_id`/`_resolve_within_root`, `IP-1180`), `content/vignette_export.py` | FS-118 | UNASSIGNED | UNASSIGNED |
| NFR-3710 *(new 2026-10-23)* | Bounded work on untrusted input | UNASSIGNED | ADR-0015 | C2 | `session/inprocess.py`, `session/ephemeris.py` | UNASSIGNED | UNASSIGNED | UNASSIGNED |

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
| ADR-0002 | FR-1120, FR-7110, FR-7310, FR-7320, FR-4420, NFR-1500, NFR-1700, NFR-1900, NFR-2400, NFR-2500, NFR-2600, NFR-2800 |
| ADR-0003 | FR-6110 |
| ADR-0004 | FR-2310, FR-3510, FR-3520, FR-4610, FR-5130, FR-6210, FR-6220, FR-6510, FR-6610, FR-4430, FR-7410, FR-7420, FR-4620, FR-7440, FR-8220 |
| ADR-0005 | FR-3110, FR-3120, FR-3410, FR-4410, FR-4420, FR-4430, FR-4450 |
| ADR-0006 | FR-1130, FR-4420 |
| ADR-0007 | FR-5310, FR-5311, FR-5312, FR-5313, FR-5314, NFR-2000, NFR-1900, FR-5410, FR-5420, FR-5510, NFR-3700 |
| ADR-0008 | FR-8110, FR-8210 |
| ADR-0009 | FR-1210, NFR-1100, NFR-2100 |
| ADR-0010 | FR-3210, FR-3220 |
| ADR-0011 | FR-1220, FR-1670 |
| ADR-0012 | FR-1410, FR-1420, FR-5312 |
| ADR-0013 | FR-1510, FR-1520, FR-3410, FR-7420 |
| ADR-0014 | FR-6310, FR-6320, FR-6410, NFR-1100, NFR-1400 |
| ADR-0015 | FR-6220, NFR-2300, FR-7410 |
| ADR-0016 | FR-1110, FR-4310 |
| ADR-0017 | FR-4710, NFR-2600, FR-10110 *(added 2026-07: CR-19 promoted to FR-10110 once ADR-0032 resolved the conflict)* |
| ADR-0018 | FR-5210, NFR-3200, NFR-2200, FR-5220, FR-5410, NFR-3700 |
| ADR-0019 | NFR-1200, NFR-1300 |
| ADR-0020 | NFR-1200, NFR-2900 |
| ADR-0021 | FR-9110 |
| ADR-0022 | FR-7210, FR-7220, FR-5420, FR-5510 |
| ADR-0024 | FR-9110, CR-01, CNFR-06 |
| ADR-0026 | FR-6310, FR-6320, NFR-1400 |
| ADR-0027 | FR-5110 |
| ADR-0029 *(Superseded by ADR-0033)* | FR-4710, FR-10210 *(added 2026-07: CR-20 promoted to FR-10210 once ADR-0033 superseded this ADR — retained here for historical traceability since FR-10210's own Related ADRs still cites ADR-0029 as the superseded decision)* |
| ADR-0030 | FR-9110 *(added 2026-07, strategic-review reconciliation)* |
| ADR-0031 | CR-18 *(added 2026-07, strategic-review reconciliation)* |
| ADR-0032 *(new 2026-07)* | FR-10110 |
| ADR-0033 *(new 2026-07)* | FR-10210 |
| ADR-0001 | (no citing FR/NFR) |
| ADR-0023 | (no citing FR/NFR) |
| ADR-0025 | (no citing FR/NFR) |
| ADR-0028 | (no citing FR/NFR) |
| ADR-0034 *(new 2026-07, DE Open Questions — no numbered FR cites it yet, pending the not-yet-authorized DE Implementation Package)* | (no citing FR/NFR) |
| ADR-0035 *(new 2026-07, DE Open Questions — same status as ADR-0034)* | (no citing FR/NFR) |
| ADR-0036 *(new 2026-10-17, `Proposed` — template libraries, `BL-0233`)* | (no citing FR/NFR yet — `FR-5310`'s template clause awaits the owner's decision) |
| ADR-0037 *(new 2026-10-17)* | FR-1470 |

## Reverse index — Architecture Component → Requirement

Built mechanically from the Interface → Component derivation table above, applied to each
requirement's own Related Interfaces field. A component with no entry below has no FR/NFR whose
Related Interfaces field maps onto it via the derivation table.

| Component | Citing Requirement(s) |
|---|---|
| C1 Simulation Engine | FR-1110, FR-1120, FR-1130, FR-1210, FR-1220, FR-1310, FR-1410, FR-1420, FR-1460, FR-1470, FR-1480, FR-1510, FR-1520, FR-1670, FR-2110, FR-2210, FR-2310, FR-2410, FR-2510, FR-3110, FR-3120, FR-3220, FR-3310, FR-3410, FR-3420, FR-4410, FR-4450, FR-4610, FR-4620, FR-5170, FR-5180, FR-6210, FR-7110, FR-7220, FR-7310, FR-7320, FR-7440, FR-8210, FR-9110, NFR-1500, NFR-1700, NFR-2010, NFR-2400, NFR-2600, NFR-2100, CR-01, CR-09, CR-10, CNFR-06 |
| C2 Session/Application Layer | most FR-6xxx, FR-1xxx–FR-4xxx leaves citing INT-0006/0007/0008/0011/0012/0014 — see master matrix per-row; also CNFR-07 (new 2026-07, via ICD §7 item 12 cross-ref), FR-5220 *(2026-10-17, `BL-0263`)* |
| C3 Mock SSN | FR-1510, FR-3210, FR-3220, CR-09 |
| C4 Operator Console | FR-2410, FR-3110, FR-3120, FR-3510, FR-3520, FR-4110–FR-4720, FR-5110, FR-5120, FR-5130, FR-5140, FR-5150, FR-5160, FR-6110–FR-6610, FR-7440, FR-8110, FR-8210, FR-8220, NFR-1100, NFR-1200, NFR-1400, NFR-2300, NFR-2700, NFR-3000, NFR-3100, NFR-3200, NFR-3300, CR-02, CR-03, CR-06, FR-5220 *(2026-10-17, `BL-0263`)* |
| C5 Content & Data | FR-5110, FR-5170, FR-5180, FR-5210, FR-5310, FR-5311, FR-5312, FR-5313, FR-5314, FR-7210, FR-7220, NFR-1600, NFR-2000, NFR-2010, NFR-2200, NFR-3200, CR-08, CR-11, FR-5220 *(2026-10-17, `BL-0263`)* |
| C6 White Cell | FR-4110–FR-4720, FR-5110, FR-9110 (indirectly via INT-0016) |
| C7 Blue Cell | FR-2410, FR-3110, FR-3120, FR-3510, FR-3520 |
| C8 Red Cell (or AI-Red) | FR-2410, FR-3110, FR-3120, FR-3510, FR-3520, FR-9110, CR-01, CR-07, CNFR-06 |
| C9 Observer | FR-6220, FR-6510, CR-06 |
| C10 Space-Track.org | FR-5210 |
| C11 Local filesystem | FR-7210, FR-7220, CR-08, CR-11 |
| C12 Browser client | FR-4510, FR-6220, FR-6310, FR-6410, FR-8110, FR-8210, FR-8220, NFR-1200, CR-02, CR-03 |

## Reverse index — Interface → Requirement

Built directly from each requirement's own already-explicit "Related Interfaces" field — purely
mechanical, no inference.

| Interface | Citing Requirement(s) |
|---|---|
| INT-0001 | FR-4510, FR-6220, FR-6310, FR-6410, FR-6510 (via FR-6510's own field — see master matrix), FR-6610, FR-8110, FR-8210, FR-8220, CR-02, CR-03 |
| INT-0002 | FR-1110, FR-4110, FR-4210, FR-4310, FR-4410, FR-4450, FR-4510, FR-4610, FR-4620, FR-4720 |
| INT-0003 | FR-5110 |
| INT-0004 | FR-2410, FR-3110, FR-3120, FR-3510, FR-3520 |
| INT-0005 | FR-6220, FR-6510, CR-06 |
| INT-0006 | FR-3110, FR-3120, FR-3520, FR-6110, FR-6210, FR-6310, FR-6320, FR-6410, FR-6510, FR-6610, FR-7440, FR-8210, CNFR-07 (via ICD §7 item 12 cross-ref, new 2026-07), FR-5220 |
| INT-0007 | FR-1510, FR-1520, FR-2310, FR-4610, FR-4620, FR-6210, FR-7440, FR-8210 |
| INT-0008 | FR-1110, FR-1120, FR-1130, FR-1210, FR-1220, FR-1310, FR-1410, FR-1420, FR-1460, FR-1470, FR-1480, FR-1670, FR-2110, FR-2210, FR-2310, FR-2410, FR-2510, FR-3110, FR-3310, FR-3410, FR-7110, FR-9110 |
| INT-0009 | FR-3210, FR-3220, CR-09 |
| INT-0010 | FR-1510, FR-3220, CR-09 |
| INT-0011 | FR-5310, FR-5311, FR-5312, FR-5313, FR-5314, FR-7220, FR-5220 |
| INT-0012 | FR-7210, FR-7220, CR-08 |
| INT-0013 | FR-5210 |
| INT-0014 | FR-1120, FR-7110, FR-7310, FR-7320 |
| INT-0015 | FR-9110, CR-01, CR-07, CNFR-06 |
| INT-0016 | FR-4410, FR-4450 |
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
| All other FR/NFR/CR/CNFR (including CR-18 — the entire 2026-09-26 Must-tier batch is now assigned: `FR-5220`→`IP-1190`, `FR-5410`/`FR-5420`/`NFR-3700`→`IP-1180`, `FR-4420`/`FR-4430`→`IP-1062`, `FR-5510`→`IP-1200`, `FR-7410`/`FR-7420`→`IP-1210`, see their own rows above) | `UNASSIGNED` |

## Reverse index — Requirement → Test

**How this column is filled (from 2026-10-23, `NFR-2820`, `BL-0310`):** every test declares the
requirement or feature it verifies with `@pytest.mark.verifies(...)`, and a requirement's tests are
the ones whose marker names it. **No test carries the marker yet** — registering it and backfilling
the existing suite is a pending package (`BL-0310`) — so the entries below and the Test cells in the
master matrices remain the earlier, file-level attributions (from `CLAUDE.md`, Metric fields and
Verification Reports), and every other requirement stays `UNASSIGNED` until its tests are tagged.
For package-grain attribution in the meantime, see GDS-10 §4.

| Requirement | Test |
|---|---|
| FR-1120 | `spacesim/tests/test_determinism.py::test_cannot_advance_backwards`, `spacesim/tests/test_determinism.py::test_different_seed_changes_random_outcome`, `spacesim/tests/test_determinism.py::test_property_replay_is_byte_identical`, `spacesim/tests/test_determinism.py::test_replay_from_midway_snapshot_matches_live`, `spacesim/tests/test_determinism.py::test_replay_from_scratch_matches_live`, `spacesim/tests/test_determinism.py::test_save_round_trip_reproduces_state` |
| NFR-1500 | `spacesim/tests/test_determinism.py::test_cannot_advance_backwards`, `spacesim/tests/test_determinism.py::test_different_seed_changes_random_outcome`, `spacesim/tests/test_determinism.py::test_property_replay_is_byte_identical`, `spacesim/tests/test_determinism.py::test_replay_from_midway_snapshot_matches_live`, `spacesim/tests/test_determinism.py::test_replay_from_scratch_matches_live`, `spacesim/tests/test_determinism.py::test_save_round_trip_reproduces_state` |
| NFR-1900 | `spacesim/tests/test_import_guard.py::test_engine_has_files`, `spacesim/tests/test_import_guard.py::test_engine_imports_no_ui_session_or_transport`, `spacesim/tests/test_import_guard.py::test_engine_reads_no_wall_clock`, `spacesim/tests/test_import_guard.py::test_engine_uses_no_dynamic_import`, `spacesim/tests/test_import_guard.py::test_guard_catches_byname_walltime`, `spacesim/tests/test_import_guard.py::test_guard_catches_dynamic_imports`, `spacesim/tests/test_import_guard.py::test_guard_catches_numpy_random`, `spacesim/tests/test_import_guard.py::test_only_rng_module_imports_random` |
| All other FR/NFR/CR/CNFR | `UNASSIGNED` |

## Reverse index — Requirement → Implementation Package

Grouped by real, verified `spacesim/` file (confirmed to exist via `ls`). *(Corrected 2026-10-23:
the prior note said no `FS-xxx`/`IMP-xxx` convention exists. Feature specifications (`docs/features/`)
and implementation packages (`docs/implementation/packages/IP-xxxx`) do exist; package attribution
by ID is in the master matrices' Impl. Package cells and in GDS-10 §4.)*

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
| `engine/bus.py` | FR-2110, FR-2210, FR-5170 *(typed sub-models slice, IP-1171, COMPLETE — pending VERIFIED)*, FR-5180 *(bus power/propulsion confirmation slice, IP-1171, COMPLETE — pending VERIFIED)*, NFR-2010 |
| `engine/busmodel.py` | FR-2310 |
| `engine/buscommands.py` | FR-2410 |
| `engine/recovery.py` | FR-2510 |
| `engine/orders.py` | FR-3110, FR-3120, FR-3410, FR-3420, NFR-1600, NFR-2010 |
| `engine/ssn.py` | FR-3210, FR-3220 |
| `engine/eventlog.py` | FR-7110, NFR-2400, NFR-2500, NFR-2600 |
| `engine/world.py` | NFR-2400 |
| `engine/handlers.py` | NFR-2600 |
| `session/manager.py` | FR-4110 *(closed 2026-07-03 via IP-1150)*, FR-4310, FR-4410, FR-7210, FR-6310, NFR-1300, NFR-1800, FR-4510 *(closed 2026-07-03 via IP-1120)*, FR-4210 *(closed 2026-07-03 via IP-1151)* |
| `session/api.py` | FR-6110, NFR-2300 |
| `session/cells.py` | FR-6210, FR-6220 |
| `session/inprocess.py` | FR-6320, FR-6410, NFR-1400, FR-5110 *(draft-session slice, IP-1173, VERIFIED)* |
| `session/aar.py` | FR-7310, FR-7320, NFR-2500, NFR-3100 |
| `session/redai.py` | FR-9110 |
| `session/assessment.py` | FR-10110 *(closed 2026-07-03 via `IP-2010`)* |
| `session/research_export.py` | FR-10210 *(closed 2026-07-04 via `IP-3010`)* |
| `spacesim/tools/research_batch.py` | FR-10210 *(closed 2026-07-04 via `IP-3010`)* |
| `content/vignette.py` | FR-4110 *(closed 2026-07-03 via IP-1150)*, FR-5110, FR-5120, FR-5130, FR-5140, FR-5150, FR-5160, FR-5170, FR-5180, FR-5310, NFR-1600, NFR-2000, NFR-2010, FR-4210 *(closed 2026-07-03 via IP-1151)* |
| `content/vignette_export.py` | FR-5110 *(reverse-serialization slice, IP-1173, VERIFIED)* |
| `content/vignettes/*.yaml` | NFR-2000 |
| `content/` (TLE import) | FR-5210, NFR-3200 |
| `ui_web/server.py` | FR-4510, FR-8110, NFR-1400, NFR-2300, NFR-2700, NFR-3300, NFR-3100 *(closed 2026-07-03 via IP-1120)*, FR-4210 *(closed 2026-07-03 via IP-1151)* |
| `ui_web/static/app.js` | FR-6510, FR-8110, NFR-3000, FR-4510 *(closed 2026-07-03 via IP-1120)*, NFR-3100 *(closed 2026-07-03 via IP-1120)*, FR-4210 *(closed 2026-07-03 via IP-1151)*, FR-6610 *(closed 2026-07-03 via IP-1140/VR-1140 — hard postcondition only, see VR-1140's Adjudication section)* |
| `ui_web/static/` (globe.js, world.js, graph.js, style.css) | NFR-1200, NFR-3000, NFR-3100 |
| `spacesim/config.py` | NFR-2700 |
| `spacesim/tests/` | NFR-2800 |
| Build/dependency manifest, `spacesim/` (whole tree) | NFR-2900 |
| All subsystems (no single file) | NFR-2200 |
| UNASSIGNED | FR-1130, FR-3310, FR-3510, FR-3520 *(the entire 2026-09-26 Must-tier batch is now assigned — `FR-5220`→`spacesim/content/bulk_import.py`/`session/manager.py::bulk_import` (`IP-1190`); `FR-5410`/`FR-5420`/`NFR-3700`→`spacesim/content/vignette.py`/`vignette_export.py`/`config.py` (`IP-1180`); `FR-4420`/`FR-4430`→`spacesim/session/manager.py`/`engine/entities.py`/`engine/orders.py` (`IP-1062`); `FR-5510`→`spacesim/content/vignette_export.py`/`session/manager.py::save_as_scenario`/`spacesim/version.py` (`IP-1200`); `FR-7410`/`FR-7420`→`spacesim/session/ephemeris.py`/`session/aar.py::state_at_time` (`IP-1210`))*, all remaining Candidate Requirements (CR-01–CR-18, CR-21 — CR-19/CR-20 promoted, see master matrix), all Candidate NFRs (CNFR-01–CNFR-07) |

*(FR-4610/FR-4710/FR-4720 closed 2026-07 via `IP-1060` v2.0; FR-7220 closed 2026-07 via `IP-1100` —
both split from `IP-1060` v1.0 per Finding F-03 — see the master matrix rows above. **FR-4110
closed 2026-07-03 via `IP-1150`/`VR-1150`, and FR-6610 closed 2026-07-03 via `IP-1140`/`VR-1140`**
— `09-package-verification` independently confirmed each against the live tree, clearing the "FS/IP
existing is not the same evidence bar" caveat this note previously applied to both. FR-6610's
closure is a **hard-postcondition-only** closure: `VR-1140` adjudicated the trigger/menu literal
wording as *not* satisfied and filed a High-severity finding for a future gap-closing package — see
`VR-1140`'s own Adjudication section, not restated here. **FR-4210 was implemented 2026-07-03 via
`IP-1151`** but remains `COMPLETE`, not yet `VERIFIED` — this reverse-index row now correctly
excludes it (real implementing files exist, listed in the per-file rows above), but its primary row
above still carries the "pending `09-package-verification`" caveat until that pass runs.)*

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

## ADR-0017/ADR-0029 conflict resolution — CR-19/CR-20 promotion (2026-07)

Following direct project-owner decision, `ADR-0032` (amends `ADR-0017`) and `ADR-0033` (supersedes
`ADR-0029`) resolved both blocking conflicts the backfill above found. This matrix was updated to
match `01-functional-requirements.md`'s own promotion of `CR-19`→`FR-10110` and `CR-20`→`FR-10210`.
Summary:

- Added master-matrix rows for **`FR-10110`** and **`FR-10210`** (both `UNASSIGNED` on every
  forward-trace column, honestly — neither has shipped code, an assigned architecture component,
  or an ICD interface yet).
- Marked the **`CR-19`** and **`CR-20`** Candidate rows `PROMOTED` in place rather than deleting
  them, preserving the audit trail of why each was originally blocked.
- Updated the **`ADR-0017`** reverse-index row to cite `FR-10110` (replacing its prior `CR-19`
  citation) and the **`ADR-0029`** row to cite `FR-10210` (its `Superseded` status noted inline);
  added new reverse-index rows for **`ADR-0032`** (→`FR-10110`) and **`ADR-0033`** (→`FR-10210`).
- Updated the Implementation Package reverse index's `UNASSIGNED` bucket to include `FR-10110`/
  `FR-10210` explicitly (baselined but not yet implemented) and to note `CR-19`/`CR-20`'s removal
  from the still-Candidate list there.
- Updated the "Method and discipline" section's ADR range (`ADR-0031` → `ADR-0033`) and its
  `Accepted`/`Superseded` split.

## Must-tier external-validation-report intake batch (2026-09-26)

Following the Must-tier `04-requirements-engineering` intake batch (`docs/pipeline/backlog.md`
`BL-0082`/`BL-0070`/`BL-0071`/`BL-0067`/`BL-0069`, items B16/B4/B5/B1/B3 — see
[`reviews/requirements-update-must-tier-batch.md`](../reviews/requirements-update-must-tier-batch.md)
for the full derivation and review), this matrix gained:

- Nine new master-matrix rows: `FR-4420`, `FR-4430`, `FR-5220`, `FR-5410`, `FR-5420`, `FR-5510`,
  `FR-7410`, `FR-7420`, `NFR-3700` — all `UNASSIGNED` on every forward-trace column, honestly (none
  has shipped code, an assigned architecture component beyond the C1–C12 list, or a test yet).
- `FR-5220`'s and `FR-7410`/`FR-7420`'s Interface cells cite the closest existing ICD interface
  (`INT-0013`, `INT-0014` respectively) with an inline note that the review report's Findings 5/6
  flag as an interface-model stretch, not a clean fit — an architecture-owner decision, not
  resolved in this matrix.
- `FR-7420`'s row is annotated as blocked on `BL-0068` (item B2, entering the pipeline at
  `03-architecture-design-synthesis`) per the review report's Finding 4 — baselined, not yet
  independently verifiable.
- Reverse-index updates: `ADR-0002`, `ADR-0004`, `ADR-0005`, `ADR-0006`, `ADR-0007`, `ADR-0013`,
  `ADR-0015`, `ADR-0018`, `ADR-0022` each gained the new leaves citing them back; `ADR-0034`/
  `ADR-0035` (authored earlier in the same increment for the DE Open Questions, `FS-105` v1.1) were
  added to the ADR reverse index with `(no citing FR/NFR)`, since no requirement in this baseline
  yet implements the not-authorized DE Implementation Package.
- The Requirement → Future Feature / Test / Implementation Package reverse indexes' `UNASSIGNED`
  catch-all rows were extended to list all nine new leaves explicitly, rather than leaving them
  silently absent.
- The ADR range note below was updated to `ADR-0001` through `ADR-0035`.

## Related

[`01-functional-requirements.md`](01-functional-requirements.md) ·
[`02-non-functional-requirements.md`](02-non-functional-requirements.md) ·
[`requirements-change-log.md`](requirements-change-log.md) ·
[`../reviews/requirements-review.md`](../reviews/requirements-review.md) ·
[`../design/05-interface-control-document.md`](../design/05-interface-control-document.md) ·
[`../architecture/adr/INDEX.md`](../architecture/adr/INDEX.md) ·
[`../architecture/10-requirements-traceability-matrix.md`](../architecture/10-requirements-traceability-matrix.md)
(GDS-10, scaffold-only — not authored by this document)
