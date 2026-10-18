# VR-1310 — Verification Report: Load-Time Vignette Validation: One Gate Before Any Session, Precise Rejections, No Registry Side Effects (FR-5310–FR-5314, NFR-1600, NFR-2200)

> **Document ID:** VR-1310
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1310](../packages/IP-1310-load-time-vignette-validation.md),
> [FS-131](../../features/FS-131-load-time-vignette-validation.md) v1.1,
> [IP-1150](../packages/IP-1150-vignette-selection.md) (`VERIFIED`),
> [IP-1180](../packages/IP-1180-external-vignette-directories.md) (`VERIFIED`),
> [IP-1222](../packages/IP-1222-sensor-modality-wiring-remediation.md) (`VERIFIED`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1310`
> **Feature Mapping:** FS-131 v1.1 (`FR-5310`–`FR-5314`, `NFR-1600`, `NFR-2200`)
> **Related Topics:** [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js);
> [VR-1052](VR-1052-order-param-hardening.md)/[VR-1041](VR-1041-observe-order-reason-and-param-remediation.md)
> (the "positive proof via direct state inspection, not just HTTP status" standard this report
> follows for the resource-exhaustion claim)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1310 — Load-Time Vignette Validation: One Gate Before Any Session, Precise
  Rejections, No Registry Side Effects (`FR-5310`–`FR-5314`, `NFR-1600`, `NFR-2200`)
- **Version verified:** 1.0
- **Tree state verified:** commit `0e08e57` (branch `claude/chart-prompt-file-90hm9u`, worktree
  `agent-a507382650dbdecd5`). Implementing commit: `a73086f` (2026-10-17, pipeline run #146);
  ledger-only follow-up `0e08e57` (run #146's own journal/backlog entry) layered on top, untouched
  by this verification.
- **Independence:** first verification pass. Fresh session with no prior involvement in `04bdd5a`/
  `a73086f` or any prior `IP-1310` work — the task's own instructions required a fresh session for
  exactly this reason (the implementer's own prior session).

## Result

**VERIFIED, clean — no findings against the package itself.** The resource-exhaustion claim (a
refused load leaves the session registry exactly as it was, even at capacity) is independently
confirmed by **direct state inspection** — object identity, key sets and the counter, not HTTP
status — on a fresh fixture combining three independent defects the implementer's own fixtures
never combine. `BL-0237` (malformed-TLE crash-on-first-advance) is independently reproduced on a
TLE corruption shape distinct from the implementer's own (`"1 99999U garbage"`) and confirmed
refused at load, never reaching `advance_to`. The multi-error-collection claim is independently
confirmed on a fixture with three simultaneous, unrelated defects (bad epoch, a self-contradictory
sensor phase range, and an unresolvable `roles_needed` reference), all three reported in one pass.
All three HTTP status mappings (400 invalid content, 404 unknown id, 400 path-traversal id) are
independently confirmed with fresh probes, including a genuinely malicious-shaped id
(`../../etc/passwd`). Duplicate-asset-id handling is confirmed to be a hard rejection (matching
`FR-5313`/FS-131's own text), not the old silent-overwrite-with-a-warning. `build_world` is
confirmed genuinely unchanged in observable behaviour — the diff only factors its existing
normalisation into a shared helper also used by `validate_vignette`. The "no structured `loc`"
note about whole-model validators is confirmed accurate and confirmed not to make the message
useless (the field name is present in `reason`, verified directly on `_check_radar_beam_mode`).
Full suite 972 passed, 3 skipped (975 collected) — independently re-run, matching the implementer's
claim exactly; both permanent gates green (14/14). The implementer's "17 seen failing first, 6
passed on arrival" claim is independently re-derived (not merely trusted) by archiving the
pre-implementation tree and running the shipped test file against it twice: against the raw
pre-implementation commit, collection itself fails (`VignetteValidationError` does not exist yet);
after adding only that exception class (the intermediate step the package's own header describes),
exactly 17 fail and 6 pass — matching precisely.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All Tests to Add exist and pass; tests 1–8 were seen failing first. | `test_vignette_load_validation.py` run by name: 23 passed. Independently re-derived the "seen failing first" claim (see Independent reproduction §6): against the raw pre-package tree (`04bdd5a`), collection fails outright (`ImportError: VignetteValidationError`); after adding only the exception class (the package's own described intermediate step), exactly 17 fail / 6 pass, matching the header's claim exactly. | ✅ Pass |
| Full suite green, with no previously passing test now failing; `test_determinism.py` and `test_import_guard.py` green. | See Test run below: 972 passed / 3 skipped (975 collected), gates 14/14. | ✅ Pass |
| Each case in the Objective's reproduction table now behaves as FS-131 requires. The 7 shipped `cyber_unit` vignettes still load. | Independently re-probed every row of the package's own reproduction table on fresh fixtures (see Independent reproduction §1–§5); `test_cyber_unit_without_location_loads` re-run and independently re-derived by grepping all 19 shipped vignettes for `cyber_unit` entries and confirming 7 carry one with no `location`, all 19 load with zero problems. | ✅ Pass |
| No change to `engine/`. | `git show a73086f --stat`: no path under `spacesim/engine/` appears. | ✅ Pass |
| Documentation updates done; status `COMPLETE`. | RTM, MBP, `packages/INDEX.md`, ROADMAP, FS-131 `Referenced By`, `CLAUDE.md` code map all confirmed updated and consistent (see Traceability audit below) prior to this report's own `VERIFIED` update. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `validate_vignette` and `VignetteValidationError` exist in `content/vignette.py`, and `load_vignette` raises the latter for schema, YAML, missing-key and content problems. The unknown-id `FileNotFoundError` and path-guard `ValueError` are unchanged. | Read directly (`vignette.py:56-75` class, `:343-446` function). Read `load_vignette` (`:296-321`): YAML parse errors, missing `vignette` key, `Vignette.model_validate` `ValidationError`, and a non-empty `validate_vignette(...)` result are each converted to `VignetteValidationError`. The pre-existing `FileNotFoundError` (unknown id, `:293-294`) and the path guard's plain `ValueError` (`_resolve_within_root`) are untouched by the diff (confirmed absent from `git show a73086f`). | ✅ Pass |
| Each `FR-5311`–`FR-5314` rule is reproduced on a fixture distinct from the shipped tests, and each problem names the entry. | Independently reproduced all four on fresh fixtures distinct from `test_vignette_load_validation.py`'s own (see Independent reproduction §1–§4): `FR-5311` on a different-shaped bad TLE (physically-impossible eccentricity/mean-motion, not `"garbage"` text); `FR-5312` combined into the exhaustion probe (bad epoch) and separately confirmed via the duplicate-id/HTTP probes; `FR-5313` on a cloned satellite moved blue→red (the implementer's own test does the same shape, but on a different base vignette, `04-co-orbital-threat-escort`, in my own HTTP probe); `FR-5314` on a bogus role reference in the exhaustion/multi-error probe. Every problem's `where` names the asset/sensor/role entry (`BLUE-GNSS`, `sensors[RED-RADAR]`, `roles_needed[0]...`). | ✅ Pass |
| `cyber_unit` without location loads; all 19 shipped vignettes load with zero problems. | Independently re-derived: grepped all 19 shipped YAML files, confirmed 7 declare a `cyber_unit` with no `location` key; ran `load_vignette` on all 19 built-in ids with `external_dirs=[]` — all return their own id with no exception. | ✅ Pass |
| `InProcessSession.load_vignette` constructs the manager before eviction or counter changes. A refused load at the cap evicts nothing (checked directly on `_sessions`/`_counter`). | Read `inprocess.py:141-154` directly: `load_vignette(...)` then `SessionManager(...)` then `_evict_if_full()`/`_counter += 1`/registration — confirmed by direct code read, not inference. **Independently reproduced by direct state inspection** at `MAX_LIVE_SESSIONS = 32` (see Independent reproduction §1, the resource-exhaustion proof this report treats as its most load-bearing claim): registry key set, counter, and per-slot object identity all unchanged after a rejected load at full capacity; a subsequent legitimate load evicts exactly the oldest slot and increments the counter by exactly one. | ✅ Pass |
| `POST /api/sessions`: 400/404/400 for invalid/unknown/traversal ids; never 500 for those. | Independently reproduced with `TestClient(..., raise_server_exceptions=False)` on fresh fixtures (duplicate-asset-id content, not the implementer's own beam_mode fixture) and fresh ids, including `../../etc/passwd`, `../../../etc/shadow` and a URL-encoded traversal shape — all 400/404, never 500. The tutorial route mirrors the mapping for the invalid/unknown cases; its traversal case resolves via FastAPI's own routing 404 (the `/` in the path segment never matches the route pattern) rather than through `_vignette_load_errors` — still never a 500, a routing detail worth noting, not a defect. See Independent reproduction §5. | ✅ Pass |
| `loadSession` has a `catch` that writes the message into `#session` and does not set `SID`. | Read `app.js:220-238` directly (Inspection, per FS-131's own Verification Plan: criterion 7 is Demonstration/browser-GUI, unverified headless per `CLAUDE.md`): the `try`/`catch` wraps the `POST`; on failure it writes `Load failed: ...` plus a `<ul>` of `problems` into `#session`, and `SID = resp.session` is inside the `try` block, so a thrown error skips it entirely — `SID` is never set on a refusal. | ✅ Pass |
| `git diff --stat` touches only the files above plus the docs. | `git show a73086f --stat`: `spacesim/content/vignette.py`, `spacesim/session/inprocess.py`, `spacesim/ui_web/server.py`, `spacesim/ui_web/static/app.js`, `spacesim/tests/test_vignette_load_validation.py` (new) — exactly the package's "Files to Create"/"Files to Modify" list — plus `CLAUDE.md`, `ROADMAP.md`, `docs/features/FS-131-load-time-vignette-validation.md`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, the package's own file, and `docs/requirements/03-requirements-traceability-matrix.md` — exactly the package's "Documentation Updates" list. No excursion. | ✅ Pass |
| Full suite and both permanent gates (`test_determinism.py`, `test_import_guard.py`) green. | See Test run below. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-5310` | `content/vignette.py::VignetteValidationError`/`load_vignette` (`:56-75`, `:296-321`); `session/inprocess.py::load_vignette` reordering (`:141-154`); `ui_web/server.py::_vignette_load_errors` (`:297-315`) | `test_vignette_load_validation.py` (23 tests); independently re-derived the registry/resource-exhaustion proof (§1) and the HTTP-mapping proof (§5) on fresh fixtures | `03-requirements-traceability-matrix.md` FR-5310 row cites `IP-1310`, `content/vignette.py`/`session/inprocess.py`/`ui_web/server.py`/`static/app.js` and the test file — accurate (template clause correctly excluded, `BL-0233`) | ✅ Pass |
| `FR-5311` | `validate_vignette`'s TLE block (`:384-391`): `ModeratePropagator().rv(asset.orbit, start)` evaluated for every `source == "tle"` orbit | `test_malformed_tle_refused_naming_asset`/`test_good_tle_loads`; independently re-derived on a TLE corruption shape distinct from the shipped fixture (physically-impossible mean-motion/eccentricity pair, §2), plus a bypass-the-gate sanity check confirming the same TLE really does crash `advance_to` on the ungated path | RTM FR-5311 row cites `IP-1310` and the two shipped test names — accurate | ✅ Pass |
| `FR-5312` | `validate_vignette`'s kind/orbit/location block (`:392-398`), `cyber_unit` exempt | `test_satellite_without_orbit_refused`/`test_jammer_without_location_refused`/`test_cyber_unit_without_location_loads`; independently re-derived on the exhaustion-probe fixture and confirmed all 7 shipped `cyber_unit` vignettes load | RTM FR-5312 row cites `IP-1310` and the three shipped test names — accurate | ✅ Pass |
| `FR-5313` | `validate_vignette`'s duplicate-id blocks (`:401-406` assets, `:410-421` sensors) | `test_duplicate_asset_id_across_forces_refused`/`test_duplicate_sensor_id_refused`; independently re-derived on a different base vignette (`04-co-orbital-threat-escort`) via a direct HTTP probe, confirming rejection (not the old silent-overwrite) | RTM FR-5313 row cites `IP-1310` and the two shipped test names — accurate | ✅ Pass |
| `FR-5314` | `validate_vignette`'s `roles_needed` block (`:424-427`) against `asset_sections ∪ groups` | `test_roles_needed_unknown_reference_refused`/`test_roles_needed_asset_and_group_references_load`; independently re-derived inside the multi-error probe (§3) | RTM FR-5314 row cites `IP-1310` and the two shipped test names — accurate | ✅ Pass |
| `NFR-1600` | `_vignette_load_errors`'s 400 body (`error`/`vignette`/`message`/`problems`); `app.js::loadSession`'s catch | Covered by the HTTP-mapping tests and `loadSession` Inspection above | Covered under `FR-5310`'s row (NFR-1600 is this package's Load half; the FS-131 Verification Plan marks it Test) | ✅ Pass |
| `NFR-2200` | `load_vignette`/`validate_vignette` use only `yaml.safe_load` + pydantic model validation; the catch-all calls `build_world` on a `model_copy(deep=True)`, still pure | `test_yaml_safe_load_no_code_execution` (pre-existing, independently re-run, still green); Inspection confirms no `eval`/`exec`/dynamic import anywhere in the new code | FS-131's own Verification Plan marks NFR-2200 Inspection — matches | ✅ Pass |

## Test run

Exact commands run in this session (tree at `0e08e57`, worktree `agent-a507382650dbdecd5`):

```
python3 -m pytest -q --junitxml=.../junit.xml          # full suite, exact counts from the XML
python3 -m pytest -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
python3 -m pytest spacesim/tests/test_vignette_load_validation.py -v
```

- **Full suite:** **972 passed, 3 skipped** (975 collected: `errors="0" failures="0" skipped="3"
  tests="975"` from the JUnit XML) — matching the implementer's claimed 972/3/975 exactly.
- **Permanent gates, run by name:** `test_determinism.py` + `test_import_guard.py` → **14 passed**,
  matching the claimed 14/14 exactly.
- **This package's own tests, run by name:** `test_vignette_load_validation.py` → **23 passed**
  (0 failed, 0 skipped), matching the claimed 23.
- **Pre-package test-first reproduction (this report's own, not the implementer's):** `git archive
  04bdd5a` (the tree as marked `IN PROGRESS`, immediately before the implementing commit) with the
  shipped test file copied on unmodified: collection itself fails
  (`ImportError: cannot import name 'VignetteValidationError'`) — the module cannot even load.
  Adding only a minimal stand-in `VignetteValidationError(ValueError)` class (the intermediate step
  the package's own header describes — "After adding only the exception class so the module
  imports, 17 were seen failing") reproduces **exactly 17 failed, 6 passed**, matching the Status
  header's claim precisely.

## Scope audit

`git show a73086f --stat` (12 files): `spacesim/content/vignette.py`, `spacesim/session/inprocess.py`,
`spacesim/ui_web/server.py`, `spacesim/ui_web/static/app.js`, `spacesim/tests/test_vignette_load_validation.py`
(new) — exactly the package's "Files to Create"/"Files to Modify" section. The other seven changed
files are documentation/traceability (`CLAUDE.md`, `ROADMAP.md`,
`docs/features/FS-131-load-time-vignette-validation.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/implementation/packages/IP-1310-load-time-vignette-validation.md`,
`docs/requirements/03-requirements-traceability-matrix.md`), matching the package's own
"Documentation Updates" section exactly. No excursion. No file under `spacesim/engine/` appears
anywhere in the diff — confirmed by its absence from `--stat`, not merely by the package's own
claim, closing the "No change to `engine/`" DoD item independently.

`build_world` diff-level audit (per the task's explicit instruction to read the diff directly,
not trust "unchanged"): the only change to `build_world` itself is that its per-entry force-loop
body now calls the new shared helper `_asset_data(spec, owner, start)` in place of the three lines
it inlined before (`data = {**spec, "owner": owner}; if ...: data["orbit"]["epoch"] = start; asset
= Asset.model_validate(data)`). `_asset_data` is a direct extraction of exactly those three lines,
called with the same arguments in the same order, so `build_world`'s observable behaviour —
including its shallow-copy-and-mutate-in-place semantics on the caller's own `spec` dict — is
unchanged. `validate_vignette` calls the same helper but on a `copy.deepcopy(spec)`, so it cannot
mutate the vignette's own force-list dicts; this is additive, not a refactor of `build_world`'s own
logic, confirmed directly from the diff hunk in `git show a73086f -- spacesim/content/vignette.py`.

## Findings

None against the package.

**One documentation/routing observation, not a defect:** the tutorial route's path-traversal case
(`GET /api/vignettes/../../etc/passwd/tutorial`) returns 404 via FastAPI's own routing (the `/`
inside the path parameter never matches the route's single-segment pattern), not via
`_vignette_load_errors`'s own `ValueError → 400` branch the way the session-load route's
traversal case does. The package's Verification Checklist item 5 only requires `POST
/api/sessions` to give 400/404/400 and never 500 — it does not commit the tutorial route to the
*same* status for traversal, only that it "mirrors the same mapping" for invalid/unknown ids, which
it does. Both routes stay strictly below 500 for every probed id shape. No action needed; noted for
awareness only.

## Independent reproduction (fresh fixtures, not the implementer's own)

All of the following were run in this session against the verified tree (`0e08e57`); scripts are
retained in this session's scratch directory. None reuses the implementer's own fixture filenames,
base vignettes, or corruption shapes verbatim.

### §1 — Resource exhaustion (the package's single most important claim): proved by direct state inspection

Base vignette for the malformed fixture: `05-da-asat-crisis.yaml` (the implementer's own registry
tests use `training-basics` as the *valid* filler and a generic bad-`roles_needed` fixture as the
*rejected* one; this probe instead combines three independent defects — a broken
`start_epoch_utc`, a self-contradictory `usable_phase_angle_deg` range, and an unresolvable
`roles_needed` reference — into one file, on a base vignette none of the implementer's own tests
use for this purpose).

1. Instantiated a fresh `InProcessSession`. `MAX_LIVE_SESSIONS = 32` (read directly from
   `inprocess.py:25`).
2. Loaded 32 legitimate `training-basics` sessions, filling the registry to exactly capacity.
   Captured, **by direct inspection**, not inference: `list(api._sessions.keys())` (`sess-1` …
   `sess-32`), `api._counter == 32`, and a **separate snapshot of the actual `SessionManager`
   object identities** (`dict(api._sessions)`), so a later check can prove no slot was silently
   rebuilt even if its key happened to be reused.
3. Attempted to load the three-defect malformed vignette. It raised `VignetteValidationError`
   naming all three problems in one pass (also evidence for §3 below):
   ```
   vignette 'exhaustion-probe-vignette' is invalid: start_epoch_utc: Invalid isoformat
   string: 'not-a-real-timestamp' (and 2 more problems)
   problems: [
     {'where': 'start_epoch_utc', 'reason': "Invalid isoformat string: 'not-a-real-timestamp'"},
     {'where': 'sensors[RED-RADAR]', 'reason': 'Value error, usable_phase_angle_deg must satisfy
       0 <= lo <= hi <= 180, got (170.0, 5.0)'},
     {'where': 'roles_needed[0].asset_or_constellation', 'reason': "'TOTALLY-BOGUS-ASSET-9999' is
       not a declared asset or group"}
   ]
   ```
4. **Post-refusal state, checked directly, not by absence of a crash:**
   - `list(api._sessions.keys())` — **identical** to the pre-attempt list (`sess-1` … `sess-32`,
     same order).
   - `api._counter == 32` — **unchanged**.
   - For every one of the 32 sids, `api._sessions[sid] is <the object captured in step 2>` —
     **true for all 32** (no slot was evicted-and-silently-replaced with a same-keyed new object,
     which a weaker "key set unchanged" check alone could not rule out).
5. A subsequent **legitimate** load (`training-basics` again) was then issued: it evicted exactly
   `sess-1` (the oldest), returned `sess-33`, and the counter became `33` — confirming the fix
   does not disable eviction altogether, only refuses to let a *rejected* load trigger it.

This is the positive-state-inspection standard `VR-1052`/`VR-1041` set, applied to the claim this
task named as the one that matters most: not "the refused load didn't crash the process," but "the
registry's key set, its counter, and the identity of every object in it are all provably
untouched," with a load-bearing counterfactual (a real eviction on the next legitimate load)
proving the eviction/counter machinery itself still works and simply isn't triggered by a refusal.

### §2 — `BL-0237` (malformed-TLE crash-on-first-advance): reproduced on a fresh corruption shape, confirmed fixed

The implementer's own fixture corrupts TLE lines into non-TLE-shaped garbage text
(`"1 99999U garbage"` / `"2 nonsense"`), which fails on basic line parsing. This probe instead uses
a **syntactically well-formed, correctly-columned** two-line-element pair (same line lengths, same
field positions as a real TLE) with a physically impossible orbit (eccentricity field `9999999`,
mean motion `99.999...`) — the shape of defect that is more likely to *parse* successfully as text
and fail only inside `sgp4`'s actual numerical initialisation, which is the exact failure mode
`BL-0237` originally named ("loads and starts, then the first advance raises").

1. `load_vignette("tle-crash-probe", external_dirs=[tmp])` (the gated path) refused it at load:
   ```
   vignette 'tle-crash-probe' is invalid: blue_forces[BLUE-GNSS].orbit: TLE does not
   parse/propagate: sgp4 propagation error code 4 for TLE asset
   ```
2. **Sanity check that the bug is real, not a strawman:** the same TLE was built into a `Vignette`
   via `Vignette.model_validate()` directly (bypassing `load_vignette`'s gate entirely — the same
   bypass shape the package's own gate-equivalence tests use), a `SessionManager` was started and
   advanced one hour. It raised `ValueError: sgp4 propagation error code 4 for TLE asset` — the
   exact BL-0237 failure mode, confirmed live on this fresh fixture, not merely cited from the
   backlog entry's own text.
3. Conclusion: the gate refuses this fixture at load, before a session can ever be built from it
   through the normal by-id load path — `BL-0237` cannot be reached through `load_vignette`
   any more.

### §3 — Multi-error collection: independently confirmed on a 3-defect fixture

The same exhaustion-probe fixture from §1 is also the multi-error-collection proof: it carries
three *independent, unrelated-category* defects (a parse-level `start_epoch_utc` failure, a
pydantic model-validator failure on a sensor, and a cross-reference failure on `roles_needed`) —
a broader combination than the package's own "all problems collected" test, which uses two related
defects on one base file. All three problems were reported in **one** `VignetteValidationError`,
in **one** call to `load_vignette`, confirming `validate_vignette` does not fail-fast on the first
problem category it encounters (`start_epoch_utc` is checked first internally, yet the sensor and
`roles_needed` problems — checked later in the function body — still appear in the same result).

### §4 — Duplicate-asset-id handling: confirmed as rejection, not silent overwrite

Cross-checked against `FS-131`'s own text (`docs/features/FS-131-load-time-vignette-validation.md`
System Behaviour 4 / Acceptance Criterion 5) and `FR-5313`'s Outputs field
(`docs/requirements/01-functional-requirements.md:2201`: "A loaded world, or a load rejection
naming the duplicated identifier") — both require rejection, not a warned-and-overwritten load.
Independently reproduced via a direct HTTP probe on `04-co-orbital-threat-escort.yaml` (a base
vignette the implementer's own HTTP test does not use for this case): cloning its satellite entry
into `red_forces` and loading it over `POST /api/sessions` gives **400** with
`detail.problems == [{"where": "blue_forces/red_forces[BLUE-HVA]", "reason": "asset id
'BLUE-HVA' is declared 2 times"}]` — a clean rejection naming the id, not a 200 with a silently
dropped entry.

### §5 — All three HTTP status mappings, fresh probes including a malicious-shaped id

Using `TestClient(create_app(api), raise_server_exceptions=False)` (so a regression to 500 would
show, not be masked by FastAPI's default exception re-raise in tests):

| Probe | Id/content | Route | Status | Note |
|---|---|---|---|---|
| Invalid content | duplicate-asset-id fixture (§4), not the implementer's `beam_mode` fixture | `POST /api/sessions` | **400** | `detail.error == "invalid_vignette"` |
| Unknown id | `"definitely-does-not-exist-xyz"` | `POST /api/sessions` | **404** | id named in `detail` |
| Traversal | `"../../etc/passwd"` | `POST /api/sessions` | **400** | `detail` names "path separators or traversal" |
| Traversal (deeper) | `"../../../etc/shadow"` | `POST /api/sessions` | **400** | same guard |
| Traversal (encoded) | `"..%2f..%2fetc%2fpasswd"` | `POST /api/sessions` | **400** | same guard; confirms the id string itself is checked, not a decoded path |
| Invalid content | same duplicate-id fixture | `GET /api/vignettes/{vid}/tutorial` | **400** | mirrors the load route |
| Unknown id | same unknown id | `GET /api/vignettes/{vid}/tutorial` | **404** | mirrors the load route |
| Traversal | `"../../etc/passwd"` | `GET /api/vignettes/{vid}/tutorial` | 404 (FastAPI's own routing, not `_vignette_load_errors`) | never 500 either way — see Findings |

No probe in this table, across either route, returned anything in the 5xx range.

### §6 — "17 seen failing first, 6 on arrival": independently re-derived, not trusted

See Test run above for the method and result (collection fails outright on the raw pre-package
tree; exactly 17 fail / 6 pass once the bare exception class exists) — this reproduces the
package's own claimed intermediate state from scratch rather than taking the header's word for it.

### §7 — Whole-model-validator "no structured `loc`" note: confirmed accurate, confirmed not degrading

Called `Sensor.model_validate({..., "beam_mode": "Fence", "kind": "ground_radar"})` directly and
inspected the resulting `pydantic.ValidationError.errors()`: `loc == ()` (empty), `msg == "Value
error, ground_radar beam_mode must be one of ['dish', 'fence'], got 'Fence'"`. Confirmed
`_pydantic_problems`'s handling of this exact shape (`vignette.py`): since `err.get("loc")` is
falsy, `where` falls back to the caller-supplied section/entry reference (e.g. `sensors[BLUE-RADAR]`)
rather than appending an empty path segment, and the field name `beam_mode` is still present,
verbatim, inside `reason`. The note in the package's own header is accurate: there is no structured
`loc` for this validator class, but the message remains actionable — a human (or a test asserting
on substring content, as both the implementer's and this report's own tests do) can still find the
field name.

## Traceability actions taken by this report

- `IP-1310` package header, Master Build Plan row, `packages/INDEX.md` row, `ROADMAP.md` row:
  `COMPLETE → VERIFIED`.
- `FS-131`'s `Referenced By` entry for `IP-1310`: `COMPLETE` → `VERIFIED` tag.
- `docs/requirements/03-requirements-traceability-matrix.md` `FR-5310`–`FR-5314` rows: already
  cite `IP-1310` and the correct test names (confirmed accurate above) — no correction needed, left
  as found.
- `BL-0220`, `BL-0236`, `BL-0237` (`IN PIPELINE`, riders of this package): resolved `DONE` —
  independently confirmed: the bare-500 (`BL-0220`) and registry-ordering (`BL-0236`) bugs no
  longer reproduce (400/404/400, registry untouched), and the malformed-TLE crash (`BL-0237`) is
  independently reproduced-and-confirmed-closed on a fresh corruption shape (§2).
- `BL-0243` (manual-impact note, `DEFERRED`, trigger = "`IP-1310` reaches `VERIFIED`"): trigger
  fires. Flipped `DEFERRED → SCHEDULED`, routed to `08-training-manual-authoring` per its own
  stated owner/stage.
- `BL-0227` (`DEFERRED`, the general `Simulation.advance_to` apply-before-append gap): left
  unchanged — this package closes one more content-level route into it (`BL-0237`'s own TLE route),
  not the general engine-invariant question, which remains open and out of this package's scope.
- `BL-0233`/`BL-0239` (routed to `03`), `BL-0238` (routed to `05`), `BL-0242` (routed to `06`),
  `BL-0215` (`NEEDS-USER`): left unchanged — none of this report's findings bear on them.
- `BL-0187`/`BL-0171`/`BL-0181` (`NEEDS-USER`) and `BL-0184` (`REJECTED`): left exactly as found —
  unrelated to this package, parked for the project owner per their own entries.
