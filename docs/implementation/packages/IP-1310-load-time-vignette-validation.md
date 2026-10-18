# IP-1310 — Load-Time Vignette Validation: One Gate Before Any Session, Precise Rejections, No Registry Side Effects (FR-5310–FR-5314, NFR-1600, NFR-2200)

> **Package ID:** IP-1310
> **Version:** 1.0
> **Status:** 🔵 COMPLETE — 2026-10-17, `08-code-implementation`, pipeline run #146, awaiting a
> **fresh-session** `09-package-verification`. `VignetteValidationError(ValueError)` + pure
> `validate_vignette` in `content/vignette.py` (with `_asset_data`/`_force_sections` shared with
> `build_world`, whose behaviour is unchanged); `load_vignette` converts YAML/missing-key/schema/
> content failures into it. `InProcessSession.load_vignette` builds the manager before eviction
> and the counter. `server.py::_vignette_load_errors` maps 400 `invalid_vignette` / 404 / 400 on
> the load and tutorial routes. `app.js::loadSession` shows `Load failed:` plus the problem list.
> Tests: `test_vignette_load_validation.py` (23 collected). 17 were seen failing first; the 6
> unchanged-behaviour tests (good TLE, `cyber_unit` without location, valid `roles_needed`, the
> shipped library, gate-does-not-change ×2) passed on arrival as planned. **Mechanism note for
> `09`:** a model-level validator (e.g. `_check_radar_beam_mode`) has an empty pydantic `loc`, so
> its problem's `where` is `sensors[<id>]`; the field name appears in `reason`. Full suite 972
> passed / 3 skipped (975 collected, JUnit; baseline 949/3/952); gates 14/14.
> *(Was 🟡 IN PROGRESS — 2026-10-16, `08-code-implementation`, pipeline run #146.)*
> *(Was 🟢 READY — authored 2026-10-16 by `07-implementation-planning`, pipeline run #145.)*
> Authorized by the project owner 2026-10-11 (MSTR-006 §3), through the standing
> pre-authorization of the packages this iteration reaches. Same precedent as
> `IP-1052`/`IP-1041`/`IP-1222`/`IP-1221`.
> **Dependencies:** [FS-131](../../features/FS-131-load-time-vignette-validation.md) v1.1 (the spec;
> criteria 1–9 and 11). [IP-1150](IP-1150-vignette-selection.md), [IP-1180](IP-1180-external-vignette-directories.md)
> and [IP-1222](IP-1222-sensor-modality-wiring-remediation.md) are all `VERIFIED`: they own the
> load path, the external roots and the sensor validators this gate surfaces.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0220`, `BL-0236`,
> `BL-0237`
> **Produces:** a vignette that either becomes a session or is refused at load with an error naming
> each failing element. Today it can instead become a bare HTTP 500, a silent **Load** button, a
> session that crashes on its first advance (malformed TLE), or a session silently missing a
> declared asset. A refused load leaves the session registry exactly as it was.
> **Feature Reference:** [FS-131 — Load-Time Vignette Validation](../../features/FS-131-load-time-vignette-validation.md)
> (`FEAT-5300`)
> **Related Topics:** [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package for a Must Feature with no prior code: `FEAT-5300` had no Feature
Specification until run #141. It is the first concrete home for `BL-0220` (bare 500, silent
Load) and `BL-0237` (a malformed TLE crashes mid-exercise). It decides FS-131's two `07`-level
Open Questions (4: wire form; 5: registry ordering) as `BL-0236`.*

---

## Package ID

IP-1310 (FS-131 → `IP-1310`, the FS-1xx → `IP-1xx0` convention; `IP-1300` is FS-130's).

## Title

Load-Time Vignette Validation: one gate before any session, precise rejections, no registry side
effects.

## Objective

Every load of a vignette by id (`content/vignette.py::load_vignette`) ends in exactly one of two
ways:

- a validated `Vignette` that builds a session exactly as today; or
- a `VignetteValidationError` listing every failing element found.

The session layer builds the `SessionManager` before it touches the registry, so a refused load
creates, evicts and numbers nothing. The HTTP layer turns refusals into client errors (400 for
invalid content or ids, 404 for unknown ids) instead of 500s, and the console shows the
refusal at **Load**.

**Live reproduction at `6aa6f8f`** (runs #141, #142 and #144 probes; re-checked in this run's
planning):

| Case | As built |
|---|---|
| radar `beam_mode: Fence` / phase range `[100, 20]` / `altitude_band_affinity: Leo` | `load_vignette` passes; `build_world` raises `ValidationError`; `POST /api/sessions` → **500** |
| schema type error (`estimated_duration_min: "long"`) | `POST /api/sessions` → **500**; `/tutorial` → 500 |
| unknown id; `../etc` | `POST /api/sessions` → **500** (the tutorial route already 404s) |
| TLE orbit `tle_line1: "1 99999U garbage"` | loads and starts, then the first advance raises `sgp4 propagation error code 2` |
| satellite without `orbit`; jammer without `location` | loads, starts and advances an hour silently |
| two force entries with one `id` | loads; the later entry silently replaces the earlier |
| `roles_needed` naming `NO-SUCH-SAT` | loads and starts |
| any refused build | `_evict_if_full()` and `_counter += 1` already ran; a session id is consumed, and a live session is evicted when 32 are open |
| `cyber_unit` without `location` (7 shipped vignettes) | loads, and **must keep loading** (`FR-5312` exempts cyber units) |

## Feature Reference

[FS-131](../../features/FS-131-load-time-vignette-validation.md) v1.1 — System Behaviour 1–7, State
Changes, Error Handling, Acceptance Criteria 1–9 and 11. Criterion 10 (`FR-5310`'s
template-reference clause) is **out of scope**: it is blocked on `BL-0233` at
`03-architecture-design-synthesis`.

## Requirements Covered

| ID | How |
|---|---|
| `FR-5310` | The gate itself: the precise rejection, and the postcondition that no partly built `WorldState` survives. Its template clause is excluded (FS-131 criterion 10, `BL-0233`). |
| `FR-5311` | TLE orbits must initialise and propagate at `start_epoch_utc` via the shipped propagator. |
| `FR-5312` | A `satellite` needs an `orbit`; every other kind except `cyber_unit` needs a `location`. |
| `FR-5313` | Asset ids unique across `blue_forces`/`red_forces`/`neutral_forces`; sensor ids unique within `sensors`. |
| `FR-5314` | Each `roles_needed[].asset_or_constellation` must equal a declared asset id or an asset `group`. |
| `NFR-1600` | Load half: a precise, actionable White Cell error, shown at **Load**. |
| `NFR-2200` | Load stays `yaml.safe_load` + schema/model validation; nothing is evaluated. |

This matches FS-131 v1.1's Requirements Implemented exactly; none added, none dropped.

## Architecture Components

- **C5 Content & Data** (`content/vignette.py`): owns the gate.
- **C1 Simulation Engine** (`engine/entities.py` `Asset`/`Sensor`, `engine/custody.py` `Track`,
  `engine/propagator.py` `ModeratePropagator`): called by the gate; **not modified**.
- **C2 Session Layer** (`session/inprocess.py`): registry ordering.
- **C4 Operator Console** (`ui_web/server.py`, `static/app.js`): error mapping and display.

The engine import boundary is unchanged. `content/` already imports `engine/` (`build_world`).

## Interfaces

- **INT-0011** (load). It gains its refusal outcome, `VignetteValidationError`; its shape is
  otherwise unchanged.
- **INT-0006** (`SessionAPI` seam). `InProcessSession.load_vignette` raises the same error through
  to its callers.
- **INT-0001** (HTTP). `POST /api/sessions` and `GET /api/vignettes/{vid}/tutorial` map refusals
  as Design Decision 3 below.

### Design Decisions

1. **One validator, all problems collected.** `content/vignette.py` gains:
   - **`VignetteValidationError(ValueError)`**, carrying `vignette_id` and `problems`. Each problem
     is a small dict `{"where": "<section>[<entry id or index>].<field>", "reason": "<text>"}`.
     Subclassing `ValueError` keeps every existing `pytest.raises(ValueError)` caller valid.
   - **`validate_vignette(vignette) -> list[problem]`** (pure). It checks, in order:
     1. `start_epoch_utc` parses (`simtime.from_iso`).
     2. Each force entry is normalised exactly as `build_world` does (owner injected, orbit
        `epoch` defaulted to the start epoch), then passed to `Asset.model_validate`. A pydantic
        error becomes one problem per error `loc`.
     3. `FR-5312`: `kind == "satellite"` with no orbit; any other kind except `"cyber_unit"` with
        no location.
     4. `FR-5311`: each validated asset whose orbit has `source == "tle"` is evaluated with
        `ModeratePropagator().rv(orbit, start)`. Any exception becomes a problem naming the asset.
     5. Each `sensors` entry goes through `Sensor.model_validate`. This surfaces
        `_check_usable_phase_angle`/`_check_radar_beam_mode`/the `Regime` type at load.
     6. `FR-5313`: duplicate asset ids across the three force lists, and duplicate sensor ids.
     7. `FR-5314`: `roles_needed` references must be in asset ids ∪ asset `group`s.
     8. Each `initial_tracks` entry goes through `Track.model_validate`.
     9. **Catch-all, only when 1–8 found nothing:** `build_world(vignette)` is called and the
        result discarded. Any exception becomes one problem `{"where": "build", ...}`. This keeps
        "every rule `build_world` enforces is enforced at load" true, even for a rule added to an
        entity model later.

   `load_vignette` converts the outcomes into a `VignetteValidationError` naming the file:
   `Vignette.model_validate`'s own `ValidationError` (one problem per `loc`), a `yaml.YAMLError`,
   a missing `vignette` key, and any non-empty `validate_vignette` list. It does this **after**
   the file is found. `FileNotFoundError` (unknown id) and the path guard's plain `ValueError`
   are unchanged.
2. **Registry ordering (FS-131 OQ5).** `InProcessSession.load_vignette` calls `load_vignette`,
   then constructs the `SessionManager`, and only then calls `_evict_if_full()`, increments
   `_counter` and registers. Any exception before registration leaves `_sessions` and `_counter`
   untouched.
3. **Wire form (FS-131 OQ4).** `POST /api/sessions` and `GET /api/vignettes/{vid}/tutorial` map
   errors as follows:
   - `VignetteValidationError` → **400**, `detail = {"error": "invalid_vignette", "vignette": <id>,
     "message": <one line naming the first problem and the count>, "problems": [...]}`;
   - `FileNotFoundError` → **404**, `detail = "vignette '<id>' not found"` (the existing tutorial
     text);
   - any other `ValueError` (path guard) → **400**, `detail = str(exc)`.

   No other route changes.
4. **Console (FS-131 W2, `BL-0220`).** `app.js::loadSession` wraps the `POST` in `try`/`catch`.
   On failure it parses the error text as JSON where possible. It writes `Load failed: <detail.message
   or detail>` (plus each `problems[].where — reason` as a list) into the existing `#session`
   element, leaves `SID`/hash/**Start** unchanged, and does not call `refresh()`.
5. **Determinism and purity.** `validate_vignette` reads no clock, draws no RNG, schedules nothing
   and mutates nothing it did not create. The catch-all `build_world` result is discarded. A
   valid vignette produces a byte-identical session.
6. **Scope boundaries.**
   - `CR-23`/`CR-24` items are not checked: TLE checksum, epoch sanity, `host_asset_id`, objective
     ids, inject targets and free-text `kind`.
   - `SessionManager(vignette)` built directly from an in-memory `Vignette` (tests, Vignette
     Creator drafts) is **not** gated; FS-131 scopes the gate to loading by id.
   - `list_vignettes` is unchanged (it already tolerates malformed files).
   - `research_batch.run_batch` is unchanged; it simply receives the new error.

## Files to Create

- `spacesim/tests/test_vignette_load_validation.py`.

## Files to Modify

Each was checked against the tree at `6aa6f8f`:

- `spacesim/content/vignette.py`: add `VignetteValidationError` and `validate_vignette`; convert
  the outcomes in `load_vignette` (lines 223–278). `build_world` (287) is unchanged.
- `spacesim/session/inprocess.py`: reorder `load_vignette` (lines 140–150) per Design Decision 2.
- `spacesim/ui_web/server.py`: the `load` route (373–377) and the `vignette_tutorial` route
  (356–364) error mapping per Design Decision 3.
- `spacesim/ui_web/static/app.js`: `loadSession` (220–238) per Design Decision 4.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, ROADMAP) before editing.
2. Write the tests below and see each fail first, except the unchanged-behaviour tests (8, 9),
   which should pass on arrival.
3. Implement Design Decision 1 in `content/vignette.py`. Reuse `build_world`'s normalisation by
   factoring the per-entry dict preparation into a private helper that both call, so the two can
   never drift. Do not change `build_world`'s observable behaviour.
4. Implement Design Decisions 2–4.
5. Run the full suite plus `test_determinism.py` and `test_import_guard.py`. Fix only defects this
   package introduced.
6. Do the documentation updates, then mark `COMPLETE`.

## Tests to Add

`spacesim/tests/test_vignette_load_validation.py`. Fixtures write vignette YAML derived from a
shipped file into `tmp_path` and pass `external_dirs=[tmp_path]` (or patch
`_configured_external_dirs` for HTTP).

1. **Sensor field rules at load** (criteria 1–2): `beam_mode: Fence`, `usable_phase_angle_deg:
   [100, 20]` and `altitude_band_affinity: Leo` each raise `VignetteValidationError` from
   `load_vignette`. Each error's `problems` names `sensors[<id>]` and the field.
2. **TLE parse** (criterion 3, `BL-0237`): a TLE asset with garbage lines is refused, naming the
   asset. A known-good TLE (copy one from an existing TLE test fixture) loads.
3. **Orbit/location presence** (criterion 11, `FR-5312`): a satellite without an orbit and a
   jammer without a location are each refused by name. A `cyber_unit` without a location loads.
4. **Duplicate ids** (criterion 5, `FR-5313`): the same id in `blue_forces` and `red_forces`, and
   two identical sensor ids, are each refused naming the id.
5. **`roles_needed`** (criterion 4, `FR-5314`): an unknown reference is refused; a reference to a
   declared asset id, or to a declared `group`, loads.
6. **All problems collected:** a file with two independent defects reports both.
7. **HTTP mapping** (criteria 1, 6; `BL-0220`):
   - an invalid file → 400 with `detail.error == "invalid_vignette"` and the problem text;
   - an unknown id → 404;
   - `../etc` → 400 (via `TestClient(..., raise_server_exceptions=False)`, so a 500 would show);
   - the tutorial route mirrors the same mapping.
8. **Registry untouched** (criterion 8): with a fresh `InProcessSession`, a refused load leaves
   `len(_sessions)` and `_counter` unchanged. With the registry pre-filled to `MAX_LIVE_SESSIONS`,
   a refused load evicts nothing. A following valid load gets `sess-1` (fresh) and evicts exactly
   one session when full.
9. **Shipped library unchanged** (criterion 9): every `list_vignettes()` built-in id loads with no
   problems. For two vignettes (one with a `cyber_unit`), a fixed-seed `SessionManager`'s initial
   world (`model_dump`) and event log equal the same session built from
   `Vignette.model_validate` of the raw YAML, bypassing the gate.
10. **No code execution / determinism** (NFR-2200): validating a vignette leaves an RNG-seeded
    `SessionManager` built afterwards byte-identical to one built without validation (covered by
    Test 9). The existing `test_yaml_safe_load_no_code_execution` stays green.

The console behaviour (criterion 7) is checked by **Inspection** of `loadSession`. The browser GUI
is unverified headless (CLAUDE.md).

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md`: `FR-5310`–`FR-5314` rows, Test and
  Impl. Package cells → `IP-1310`.
- `docs/features/FS-131-load-time-vignette-validation.md`: `Referenced By` only.
- `CLAUDE.md` "Code map" `content/vignette.py` bullet: one clause naming `validate_vignette` /
  `VignetteValidationError`, since the load contract changes.
- MBP row and counts, `packages/INDEX.md`, ROADMAP row, this header.
- Manual impact (`06`/`WCM-2`: what a refused Load looks like) is **not** edited here. It is
  routed to `08-training-manual-authoring` once `VERIFIED`.

## Definition of Done

- All Tests to Add exist and pass; tests 1–8 were seen failing first.
- Full suite green, with no previously passing test now failing; `test_determinism.py` and
  `test_import_guard.py` green.
- Each case in the Objective's reproduction table now behaves as FS-131 requires. The 7 shipped
  `cyber_unit` vignettes still load.
- No change to `engine/`.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. `validate_vignette` and `VignetteValidationError` exist in `content/vignette.py`, and
   `load_vignette` raises the latter for schema, YAML, missing-key and content problems. The
   unknown-id `FileNotFoundError` and path-guard `ValueError` are unchanged.
2. Each `FR-5311`–`FR-5314` rule is reproduced on a fixture distinct from the shipped tests, and
   each problem names the entry.
3. `cyber_unit` without location loads; all 19 shipped vignettes load with zero problems.
4. `InProcessSession.load_vignette` constructs the manager before eviction or counter changes.
   A refused load at the cap evicts nothing (checked directly on `_sessions`/`_counter`).
5. `POST /api/sessions`: 400/404/400 for invalid/unknown/traversal ids; never 500 for those.
6. `loadSession` has a `catch` that writes the message into `#session` and does not set `SID`.
7. `git diff --stat` touches only the files above plus the docs.
8. Full suite and both permanent gates (`test_determinism.py`, `test_import_guard.py`) green.

## Dependencies

`IP-1150`, `IP-1180` and `IP-1222` (all `VERIFIED`). No package depends on `IP-1310`. It does not
touch `orders.py`, so there is no rebase interaction with `IP-1160`.

## Risks

- **Double build cost.** The catch-all builds the world once more per load. At the ~24-satellite
  guideline this is a few milliseconds; it is not on the clock path.
- **Normalisation drift** between the validator and `build_world`. Task 3's shared helper
  mitigates it.
- **External or user content that loads today may be refused.** That is intended. It is stated in
  the routed manual note.
- **TLE validation needs `sgp4`.** It is a declared dependency, and `_tle_rv` already imports it
  lazily. A missing `sgp4` would surface as a load problem for TLE assets only.
- **Error text echoes vignette content to whoever pressed Load.** This is consistent with
  NFR-2300 (FS-131 Security Considerations).

## Rollback Considerations

Revert the commit. There is no data migration and no persisted format change. Saves, event logs
and vignette files are untouched, and `build_world` is unchanged.
