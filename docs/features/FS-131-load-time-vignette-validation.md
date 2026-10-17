# FS-131 — Load-Time Vignette Validation

> **Document ID:** FS-131
> **Version:** 1.1 (2026-10-16, run #143: aligned to `FR-5311`–`FR-5314`, added in run #142; see
> the change note at the end)
> **Status:** ✅ Ready for implementation planning, **except** the `FR-5310` template-reference
> clause. That clause and its Acceptance Criterion name a construct the shipped content model does
> not carry (Open Question 1, routed to `04-requirements-engineering`). Every other clause is
> specified in full below, so a package can be planned from it now.
> **Approved input:** the Feature Catalog entry `FEAT-5300` in
> [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md),
> following the FS-130 convention. `Purpose`/`Scope`/`Dependencies`/`Affected Subsystems`/
> `Affected Interfaces`/`Related ADRs` are carried forward from that entry, not re-derived. The
> catalog entry was not edited.
> **Dependencies:** none (per `FEAT-5300`). **Dependent:** [FS-115](FS-115-session-setup.md)
> (`FEAT-4100`, Session Setup — no session can start without a validated vignette).
> **Referenced By:** [IP-1310](../implementation/packages/IP-1310-load-time-vignette-validation.md)
> (Implementation Package, ✅ `VERIFIED` via [VR-1310](../implementation/verification/VR-1310-load-time-vignette-validation.md), criteria 1–9 and 11),
> [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0220` (its first
> concrete error-path case), `BL-0237`, `BL-0240`, [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-5310`–`FR-5314`, [docs/requirements/02-non-functional-requirements.md](../requirements/02-non-functional-requirements.md)
> `NFR-1600`/`NFR-2200`, [`03-feature-catalog.md`](../feature-planning/03-feature-catalog.md) `FEAT-5300`
> **Produces:** a single load-time gate: a vignette either becomes a session, or is refused with an
> error that names the failing element. It never becomes a partly built, silently altered or
> later-crashing session.
> **Feature Mapping:** FS-131 (this document)
> **Related Topics:** [FS-115](FS-115-session-setup.md) (selection/tuning, which runs after this
> gate), [FS-117](FS-117-vignette-creator.md) (in-app-built vignettes reach this gate when loaded),
> [FS-118](FS-118-external-vignette-directories.md) (external roots, path-traversal guard
> `NFR-3700`), [FS-119](FS-119-bulk-tle-omm-import.md) (in-session TLE import, a sibling path
> outside this gate), [FS-122](FS-122-sensor-modality-models.md) (the sensor field checks
> `BL-0220` exposed)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

---

## Feature ID

FS-131 (`FEAT-5300`).

## Title

Load-Time Vignette Validation.

## Purpose

Fail loudly and precisely on an invalid vignette at load time, rather than loading it partially
or silently (`FEAT-5300` Purpose). User value, carried from the catalog: "Invalid scenario data
fails loudly at load". A facilitator gets a fixable error message, not a mysterious partial state.

## Scope

**In scope.**

- The validation every vignette file passes before a session is built from it. This covers
  hand-authored built-in files, files in configured external directories (`FR-5410`), and files
  written by the in-app Vignette Creator or save-as-scenario (`FR-5110`/`FR-5510`). The catalog's
  Technical Value names this as "the gate every vignette ... passes through before it can start a
  session".
- The precision of the resulting error, and how it reaches White Cell (`NFR-1600`: "a precise,
  actionable White Cell error").
- The secure-loading practice (no scenario-embedded code execution, input validation on all
  loaded files), bundled here by the catalog as its nearest architectural home (`NFR-2200`).

**Out of scope** (each owned elsewhere):

- Validity of White Cell's parameter **overrides** chosen at selection time (`FR-4110`,
  `FEAT-4100` / FS-115).
- The **running-engine** half of `NFR-1600`: order validation and `dry_run`, which is already
  specified by FS-102/FS-104/FS-105 and built (`IP-1041`/`IP-1052`).
- In-session TLE force-add and bulk TLE/OMM import (`FR-5210`/`FR-5220`, FS-119). These have
  their own per-object refusal behaviour.
- Fire-time inject-effect validation (`FR-4430`, already built by `IP-1063`).
- The vignette **catalog listing**, which already tolerates one malformed file (`list_vignettes`).

## Requirements Implemented

| ID | Coverage in this spec |
|---|---|
| **FR-5310** | Full, except the template-reference clause (Open Question 1): well-formed TLEs, every declared `roles_needed` satisfiable, rejection with a precise error rather than a partial or silent load, and the postcondition that no partly built `WorldState` survives a failed validation. |
| **FR-5311** | TLE-sourced orbits parse at load, or the asset is rejected by name (System Behaviour 2). |
| **FR-5312** | A satellite needs an orbit and a terrestrial asset needs a location, or the asset is rejected by name (System Behaviour 7). What counts as "terrestrial" is Open Question 6. |
| **FR-5313** | Asset ids, and sensor ids, are each unique within a vignette (System Behaviour 4). |
| **FR-5314** | Every `roles_needed` entry names a declared asset or constellation group (System Behaviour 3). |
| **NFR-1600** | The load-time half: "Invalid scenario JSON or TLEs shall fail at load with a precise, actionable White Cell error." The running-engine half is out of scope (see Scope). |
| **NFR-2200** | The loading part: input validation on all loaded files, and no execution of scenario-embedded code. The dependency-pinning and no-phone-home clauses are project-wide and are not owned by this Feature. |

No requirement was added by this spec, and none was dropped. `FR-5311`–`FR-5314` are child leaves of
`FR-5310`, which `04-requirements-engineering` baselined in run #142 from GDS-04 §1.2/§1.3/§1.10.
They belong to `FEAT-5300` by parentage. The catalog entry's Included Requirements still lists
only `FR-5310`, which is a `05` housekeeping note (the entry was not edited here).

## User Workflows

**W1 — White Cell loads a valid vignette** (the normal path, unchanged). White Cell picks a
vignette in the console and presses **Load**. A session is created, the URL takes the session id,
and **Start** is enabled (FS-115 continues from here).

**W2 — White Cell loads an invalid vignette.** White Cell picks a vignette whose file is invalid
(for example a hand-edited sensor with `beam_mode: Fence`) and presses **Load**. The console shows
an error that names the vignette and the failing element (which force or sensor entry, which
field, and what was wrong). No session is created. White Cell fixes the file, or picks another
vignette, and presses **Load** again.

**W3 — An author checks a vignette before an exercise.** An author drops a new file into a
configured external directory and loads it, as in W1/W2. The rejection message is the author's
debugging tool, so it must be enough to find the line to fix without reading the server log.

**W4 — A non-console caller loads a vignette.** Any other caller that builds a session from a
vignette id hits the same gate and gets the same rejection, in that caller's own error form:
`POST /api/sessions` directly, the offline research batch (`tools/research_batch.py`), or the
tutorial lookup (`GET /api/vignettes/{vid}/tutorial`).

## System Behaviour

**On every load (W1–W4), Content & Data validates the whole vignette before Session Layer
registers any session.** Validation covers:

1. **Schema conformance.** Every field has its declared type and every declared field-level
   rule holds. That includes the per-entity rules the engine entities already declare: the sensor
   checks for `usable_phase_angle_deg`, radar `beam_mode` and `altitude_band_affinity`
   (FS-122/`IP-1221`/`IP-1222`), and the asset, orbit, track and parameter models. Today some of
   these rules fire only while the world is being built (`build_world`). This spec requires that
   **every** such rule is checked as part of load validation, and its failure reported the same
   way as a schema failure.
2. **Well-formed TLEs** (`FR-5310`, `FR-5311`). An asset whose orbit is given as a TLE must be usable as
   one: the element set initialises, and propagates without error at the vignette's start epoch.
   As built, a malformed TLE (`1 99999U garbage`) loads, starts, and then makes the session raise
   `sgp4 propagation error code 2` on its first clock advance (reproduced this run). That is the
   exact "later crash" this Feature exists to prevent. Whether checksum or epoch-sanity checks go
   beyond "initialises and propagates" is answered by the baseline: no, they are candidate `CR-23`
   and not required (closed Open Question 3).
3. **Every declared `roles_needed` entry is satisfiable** (`FR-5310`, `FR-5314`; GDS-04 §1.1
   Constraints, §1.10).
   Each entry's `asset_or_constellation` must name an asset or a constellation group the vignette
   actually declares. As built, an entry naming `NO-SUCH-SAT` loads and starts. Today
   `assign_role` accepts any string, so such a requirement can only ever be met by a seat bound
   to an asset that does not exist.
4. **No silent loss of content** (`FR-5310`: "rather than a partial or silent load"; `FR-5313`). As built,
   two force entries with the same `id` load without complaint, and the later one silently
   replaces the earlier one in the world. That is a silent partial load. Asset ids and sensor ids
   must each be unique, and a collision is a rejection naming the duplicated id.
5. **Unknown or unsafe vignette ids** (`NFR-1600`, `NFR-2200`, `NFR-3700`). An id that names no
   vignette, or that the existing path guard refuses, is a rejection naming the id. It is not a
   server error. As built, both return a bare HTTP 500 from `POST /api/sessions`.
6. **No code execution** (`NFR-2200`). Loading remains data-only: YAML is parsed with the safe
   loader and validated by schema, and no field is evaluated as code (ADR-0007). This holds today.
   The spec records it as a property the gate must keep, not as new work.
7. **Space assets have an orbit, terrestrial assets a location** (`FR-5312`; GDS-04 §1.2
   Constraints). A satellite entry with no orbit is refused, naming the satellite. A terrestrial
   asset with no location is refused, naming the asset. As built, both load, start and advance
   silently (`03-gnss-ew-campaign`: `BLUE-GNSS` without its orbit, `RED-JAM` without its
   location), leaving an asset that can never have access.
   **Shipped-content caution:** 7 shipped vignettes declare a `cyber_unit` (`RED-CYBER`) with no
   location. Cyber is the one effect not gated by geometry (CLAUDE.md "Key facts"). If
   "terrestrial" covered every non-satellite asset, `FR-5312` would refuse those 7 vignettes,
   contradicting criterion 9 and `NFR-2010`. Which kinds count is Open Question 6. Until it is
   answered, the rule applies to satellites and to the kinds that clearly occupy a place on
   the ground and take part in access geometry (`ground_station`, `jammer`, `interceptor`,
   `directed_energy`, `terrestrial_force`), and a `cyber_unit` without a location must still
   load. The shipped library has no violation of the rule read that way (checked this run).

**Outcomes.**

- **Pass:** the session is built and registered exactly as today. A vignette that loads today and
  is valid under 1–5 must load identically, with the same `WorldState`, the same event log and the
  same RNG state (`NFR-2010`'s additive posture).
- **Fail:** the load is refused. The refusal carries every failing element found, or at least the
  first one. Whether to collect all errors or stop at the first is a `07` decision, provided the
  first error is always precise. Each element is identified by vignette id/file, the section
  (`blue_forces`, `red_forces`, `neutral_forces`, `sensors`, `roles_needed`, …), the entry's `id`
  where it has one (otherwise its position), the field, and the reason. The refusal reaches White
  Cell in the console (W2): the **Load** button must not appear to do nothing. This is the
  `BL-0220` symptom: `app.js::loadSession` has no `catch`, so a failed load is invisible.

**Edge cases.**

- A file that is not valid YAML, or has no top-level `vignette` key, is refused with a message
  naming the file. Today it is a bare 500.
- A rule that fails late is a gate defect. If a rule can only be checked by building part of the
  world (for example TLE propagation), the gate builds that part, discards it, and reports the
  failure. A failure discovered after the session is registered means the gate is incomplete.
- Vignettes shipped before this Feature must all still pass. All 19 built-in vignettes are
  expected to pass rules 1–5 and 7 (checked by a data scan this run: no duplicate ids, no
  dangling `roles_needed`, no satellite without an orbit, no located-kind asset without a
  location). Verifying that in the test suite is part of the Verification Plan.

## Subsystem Responsibilities

| Subsystem (GDS-03) | Responsibility |
|---|---|
| **C5 Content & Data** (`content/vignette.py`) | Owns the validation: schema conformance, TLE well-formedness, `roles_needed` resolution, id uniqueness, and the id/path guard. It produces either a validated Vignette or a precise rejection. It is the sole owner of the on-disk format (ADR-0007, GDS-03 §2.5). |
| **C1 Simulation Engine** (`engine/entities.py`, `engine/orbit.py`, `engine/propagator.py`) | Keeps owning the per-entity rules and the propagator that C5's gate invokes. No new engine behaviour. The engine stays free of UI and transport code, and of wall-clock or global-RNG use. |
| **C2 Session Layer** (`session/inprocess.py` `load_vignette`, `session/manager.py`) | Calls the gate before any registry side effect, and registers nothing on a refusal (State Changes). It carries the rejection to its callers (`SessionAPI` seam, INT-0006). |
| **C4 Operator Console** (`ui_web/server.py` load and tutorial routes, `static/app.js` `loadSession`) | Turns a rejection into a client-visible error instead of an unhandled server error, and shows it to White Cell at **Load** (W2). |

No subsystem is invented.

## Interfaces Used

- **INT-0011** (Session Layer → Content & Data, vignette/template load). This Feature fills in its
  "Error handling: Invalid scenario data fails loudly at load" clause and its precondition ("The
  Vignette file validates against its schema"). The interface's shape is unchanged: one parsed
  Vignette per load call, or a rejection.
- **INT-0006** (Operator Console → `SessionAPI`). It carries the rejection out of the session
  layer. No new operation is needed; the existing load call gains a refusal outcome.
- **INT-0001** (Browser ↔ Operator Console, HTTP). It carries the rejection to the browser. The
  wire form (status code, body shape) is not baselined, because INT-0001 has a recorded
  wire-level gap and GDS-09 is unauthored. Open Question 4 leaves this to `07`.

## Data Model Changes

None to the persistent Vignette or `WorldState` models. Validation reads the existing Vignette
fields (`blue_forces`/`red_forces`/`neutral_forces`/`sensors`/`roles_needed`/`start_epoch_utc`,
and orbit `source`/`tle_line1`/`tle_line2`) and the existing `Asset.group` (constellation)
identifier. A rejection is a transient result returned to the caller and is not persisted.

## State Changes

- **On pass:** unchanged from today — one new session in the registry.
- **On refusal:** no session is registered, and no partly built `WorldState` survives
  (`FR-5310` Postcondition). The gate also must not cause other registry side effects. As built,
  `InProcessSession.load_vignette` parses the file, then calls `_evict_if_full()` and increments
  the session counter, and only then builds the `SessionManager`. So a refused build can evict
  another live session when the registry is full, and it consumes a session id (probed: 0
  sessions, counter 1 after one refused load). The required behaviour is that a refused load
  leaves the registry exactly as it found it. The ordering is a `07` decision (Open Question 5).
- No event-log entry and no RNG draw happen during validation, so determinism and replay are
  untouched.

## Error Handling

| Failure | Observable behaviour |
|---|---|
| Field type or field rule violated (e.g. `beam_mode: Fence`, `usable_phase_angle_deg: [100, 20]`, `altitude_band_affinity: Leo`, `estimated_duration_min: "long"`, `start_epoch_utc: "yesterday"`) | Refused. The message names the section, the entry id and the field, and quotes the rule (the existing validator text, e.g. "ground_radar beam_mode must be one of ['dish', 'fence'], got 'Fence'"). |
| Malformed or unpropagatable TLE | Refused at load, naming the asset id. It is never deferred to the first clock advance. |
| `roles_needed` names no declared asset/group | Refused, naming the requirement's `asset_or_constellation` value. |
| Satellite with no orbit, or a located terrestrial asset with no location (`FR-5312`) | Refused, naming the asset. A `cyber_unit` without a location is not refused (Open Question 6). |
| Duplicate asset or sensor id | Refused, naming the id and both sections it appears in. |
| Unknown vignette id, or an id the path guard refuses | Refused, naming the id. This is a client error, not a server error. |
| Not YAML / no `vignette` key | Refused, naming the file. |
| Unexpected internal fault during validation | Still not a silent console. White Cell sees that the load failed. Diagnostics may stay in the server log. |

Every refusal leaves the registry unchanged (State Changes).

## Performance Considerations

- Validation runs once per load, outside the simulation loop. It adds no per-tick cost
  (`NFR-1300` sizing guideline unaffected).
- TLE propagation at the start epoch is one evaluation per TLE asset, which is negligible at the
  ~24-satellite guideline (ADR-0019).
- **Determinism (NFR-1500, invariant 1):** validation is pure with respect to the session. It
  reads no wall clock, draws from no RNG, and appends nothing to the event log. A vignette that
  passes yields a byte-identical session to today's.
- **Offline (ADR-0018):** TLE well-formedness is checked locally. No network call (for example to
  Space-Track) takes part in load validation.

## Security Considerations

- **NFR-2200 / ADR-0007:** load stays data-only, with safe YAML parsing and schema validation and
  no evaluation of content. This must hold for every new rule too: a check is a declarative
  comparison, never an interpreted expression taken from the file.
- **NFR-3700:** the existing id/path-traversal guard is kept for built-in and external roots. A
  refused id now produces a client error rather than a 500. The guard itself is FS-118's and is
  not changed.
- **NFR-2300 / ADR-0015 (LAN trust):** a rejection message may echo ids and values from the
  vignette, including Red force entries, to whoever pressed **Load**. Load is a White Cell action,
  and vignette content is already ground truth under the accepted v1 LAN trust boundary
  (`/api/vignettes/{vid}/source` already serves the raw YAML). So this is consistent with the
  boundary, not a new exposure. It is recorded so `07` does not design a cell-scoped error path
  for it.

## Acceptance Criteria

1. Loading a vignette whose ground radar declares `beam_mode: Fence` is refused. The error names
   the sensor's id and `beam_mode`, and no session is registered. Over HTTP the response is a
   client error with that message, not a 500 (`BL-0220`).
2. The same holds for `usable_phase_angle_deg: [100, 20]` and `altitude_band_affinity: Leo`.
3. Loading a vignette with a TLE asset whose lines do not initialise or propagate at the start
   epoch is refused at load, naming the asset id. No session ever reaches a clock advance with it.
4. Loading a vignette whose `roles_needed` names an id that is no declared asset or group is
   refused, naming that id.
5. Loading a vignette with two force entries sharing one `id` is refused, naming the id.
6. `POST /api/sessions` with an unknown vignette id, or a path-traversal id such as `../etc`,
   returns a client error naming the id, not a 500.
7. In the console, pressing **Load** on an invalid vignette shows the rejection text. The page
   does not stay silently unchanged.
8. After any refused load, the session registry holds exactly the sessions it held before. No
   session is evicted, and no session id is consumed (checked with the registry full and not
   full).
9. Every one of the 19 shipped vignettes still loads, and for a fixed seed produces the same
   initial world and event log as before. The determinism and import-guard gates stay green.
10. *(Blocked on Open Question 1.)* `FR-5310`'s own criterion: "a vignette referencing a
    non-existent asset template is rejected with an error naming the missing template".
11. Loading a vignette whose only defect is a satellite entry without an orbit is refused, naming
    the satellite. The same holds for a `jammer` (or `ground_station`) entry without a location.
    A vignette whose `cyber_unit` has no location still loads, as all 7 shipped ones do
    (`FR-5312`; Open Question 6).

## Verification Plan

| Criterion | Method |
|---|---|
| 1–6, 11 | **Test**: load-path tests over the session layer and HTTP (`TestClient`), using fixture vignettes under a temporary external directory, asserting rejection, message content and status class. |
| 7 | **Demonstration** (browser GUI; headless runs are unverified per CLAUDE.md), backed by a **Test** of the route's client-error response the console displays. |
| 8 | **Test**: registry size, contents and next-id before and after a refused load, at `MAX_LIVE_SESSIONS` and below. |
| 9 | **Test**: every library vignette loads; the existing determinism property test; a fixed-seed world/event-log equality check against pre-change behaviour. |
| NFR-2200 no-eval | **Inspection**: the loader uses safe parsing and schema validation only. |
| 10 | Deferred to Open Question 1. |

`FR-5310`'s Verification Method is Test. `NFR-1600` is Test (scenario-load validation tests), and
`NFR-2200` is Inspection. The plan matches each.

## Dependencies

None (per `FEAT-5300`). FS-115 (`FEAT-4100`) depends on this Feature. The per-entity rules it
surfaces already exist (FS-122 / `IP-1220`–`1222`).

## Risks

- **Late-failing rules.** Some invalidity only shows when the world is built (sensor
  validators) or propagated (TLE). A gate that validates the schema alone would still let these
  through, as `BL-0220` shows. The spec mitigates this by requiring every rule checked at load.
- **Backward compatibility.** A stricter gate could refuse a shipped or user-authored vignette
  that loads today, for example one relying on silent duplicate-id replacement. Criterion 9
  covers the shipped library. User-authored external files could newly fail, which is the
  intended outcome but should be stated in the manual (`06`/`WCM-2`).
- **Scope creep.** "Invalid scenario data" could be read to cover every cross-reference in a
  vignette: objective metrics, inject targets, sensor hosts, asset `kind` values. This spec
  commits only to the references `FR-5310` names, plus id uniqueness, and lists the rest as Open
  Question 2.
- **Requirement/as-built mismatch.** `FR-5310`'s template clause cannot be tested against the
  shipped content model (Open Question 1).
- **Over-broad `FR-5312`.** Implementing "terrestrial" as "not a satellite" would refuse 7
  shipped vignettes (Open Question 6). Criterion 9 and the narrow reading in System Behaviour 7
  guard against it.

## Open Questions

1. **The template-reference clause has nothing to check** (→ `03-architecture-design-synthesis`,
   re-routed from `04` in run #142: the requirement agrees with GDS-03 §2.5, GDS-04 §1.2 and
   ADR-0007, which all describe template libraries the build lacks; `BL-0233`). `FR-5310` requires "every referenced template
   exists", and its only Acceptance Criterion is a vignette "referencing a non-existent asset
   template". GDS-03 §2.5 describes asset/effect/sensor template libraries, and GDS-04 §1.2 lists
   a "template reference" on Asset. The shipped content model has neither: assets and sensors are
   authored inline in the vignette, no template library exists under `spacesim/content/`, and no
   vignette field references one. Either `FR-5310` is amended to cite a reference the model does
   carry (the clause and AC would then be re-pointed, perhaps at the `roles_needed` or id rules
   above), or the template libraries are first built as their own Feature. Until then criterion
   10 cannot be planned. **It matters because** `FR-5310` is Must, and its only stated acceptance
   test cannot currently be run.
2. ~~**Which other in-file cross-references are "invalid scenario data"?**~~ **Closed (run #142,
   `04`):** the baseline answers with `FR-5312`–`FR-5314`. The rest (`host_asset_id`, objective
   ids, scheduled inject targets, free-text `kind`) is candidate `CR-24`, not baselined, so this
   Feature does **not** reject them. The original question follows for the record. (→ `04`.) Candidates
   that load silently today: a sensor's `host_asset_id` naming no asset; an `objectives` metric
   naming an unknown object; a scheduled inject effect targeting an unknown id (checked only at
   fire time by `IP-1063`); a free-text asset `kind` such as `starship`, which is accepted
   because `Asset.kind` is an unconstrained string. `NFR-1600`'s "invalid scenario JSON" is broad
   enough to cover any of them, and `FR-5310` names none of them. **It matters because** each
   added rule can refuse content that loads today. The requirements owner should decide the set,
   not this spec.
3. ~~**What "well-formed TLE" requires beyond initialise-and-propagate**~~ **Closed (run #142,
   `04`):** `FR-5311` requires the TLE to parse into an element set the propagator accepts.
   Checksum and epoch sanity are candidate `CR-23`, not required. The original question follows
   for the record. (→ `04`, aligned with
   `FR-5210`/FS-119's per-object posture so one TLE is judged the same way on both paths). The
   options are line-checksum enforcement and epoch sanity relative to `start_epoch_utc`.
   **It matters because** a TLE can pass a checksum and still fail propagation, and can fail a
   checksum and still propagate.
4. **Rejection wire form** (→ `07-implementation-planning`; INT-0001's wire-level gap). Which
   client-error status, which body shape (a single message or a list of element errors), and
   whether the console shows it in the session summary or a dialog. **It matters because** the
   acceptance criteria require "a client error with a precise message", not a particular shape.
   This is a design-level choice `07` can make without new requirements.
5. **Registry-side-effect ordering** (→ `07`). The required outcome (a refused load leaves the
   registry untouched) is fixed above. Whether validation moves ahead of `_evict_if_full()` and
   the counter increment, or those become conditional, is an implementation choice.
6. **Which asset kinds are "terrestrial" for `FR-5312`?** (→ `04-requirements-engineering`.)
   `FR-5312` and GDS-04 §1.2 say a terrestrial asset must have a location, but do not define
   terrestrial. GDS-04 §1.2's Purpose lists satellites, terrestrial forces, jammers,
   interceptors and cyber units. Seven shipped vignettes declare a `cyber_unit` without a
   location, and cyber is the geometry-free effect. **It matters because** the broad reading
   would refuse those 7 vignettes, contradicting criterion 9 and `NFR-2010`. Resolve by
   amending `FR-5312` to name the kinds (or to exempt `cyber_unit`). Until then this spec
   applies the narrow reading stated in System Behaviour 7. That reading is the only one
   consistent with criterion 9, not a settled answer.

## Related ADRs

ADR-0007 (content as data — the binding decision; from `FEAT-5300`). Also consistent with:
ADR-0018 (offline-first runtime — no network in validation), ADR-0015 (LAN trust model — error
text under the accepted boundary), and ADR-0019 (sizing is a guideline, so no satellite-count
rule is added here).

## Related Interfaces

INT-0003 (in-app scenario builder — its output reaches this gate when loaded), INT-0012 (save
round trip — a resumed save is not a vignette load and is outside this gate), INT-0013 (TLE
import — the in-session sibling path, FS-119).

## Change note

- **v1.1 (2026-10-16, run #143, `BL-0240`).** Added `FR-5311`–`FR-5314` (baselined run #142) to
  Requirements Implemented. Added System Behaviour 7, an Error Handling row and criterion 11 for
  `FR-5312`. Closed Open Questions 2 and 3 against the new leaves and candidates `CR-23`/`CR-24`.
  Re-routed Open Question 1 to `03` (`BL-0233`). Added Open Question 6 (the definition of
  "terrestrial"), found by scanning the shipped library while adding `FR-5312`'s rule.
  Status unchanged: ready for implementation planning except criterion 10.
