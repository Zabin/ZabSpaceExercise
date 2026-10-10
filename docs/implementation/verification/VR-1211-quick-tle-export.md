# VR-1211 — Verification Report: Quick TLE Export for a Cell-Visible Satellite

> **Document ID:** VR-1211
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1211](../packages/IP-1211-quick-tle-export.md), [FS-121](../../features/FS-121-ephemeris-export.md) v2.0 (`FR-7440`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1211
> **Feature Mapping:** FS-121 v2.0 (`FR-7440`)
> **Related Topics:** [`spacesim/engine/tle_export.py`](../../../spacesim/engine/tle_export.py),
> [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/tleexport.js`](../../../spacesim/ui_web/static/tleexport.js)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1211 — Quick TLE Export for a Cell-Visible Satellite
- **Version verified:** 1.0
- **Tree state verified:** commit `07f28b1` (branch `claude/chart-prompt-file-90hm9u`, same tip
  this report commits onto). Implementing commit: `bc1e157` (2026-10-10); ledger-only follow-up
  `07f28b1` (pipeline run #92 journal/backlog) layered on top, untouched by this verification.
- **Independence:** first verification pass, fresh session with no involvement in `bc1e157`. No
  prior `09-package-verification` run on this package. (Separately, this session had to recover a
  usable worktree — see note below — but took no part in the implementation itself.)

## Result

**VERIFIED, with 1 Low finding.** `FR-7440` (quick, fog-of-war-filtered, current-epoch TLE export
for a cell-visible satellite) is fully and correctly implemented. The central question this pass
was asked to settle — whether `BL-0164`'s algorithm deviation (safeguarded Newton + fixed-point
correction in place of the package's plain fixed-point iteration) is sound — is adjudicated
**DONE, accepted**: the deviation is real, was independently reproduced as *necessary* (the plain
iteration genuinely diverges for exactly- and near-equatorial GEO states), and the shipped
safeguarded version never emits an out-of-bound TLE across every geometry this pass constructed,
including ones not in the shipped test suite. The fog-of-war claim (stale belief, not new ground
truth, survives a manoeuvre) was independently re-tested end-to-end through `SessionManager.get_tle`
on a fresh vignette/session this session built itself, not reused from the implementer's fixtures.
Full suite 805 passed, 3 skipped (808 collected); both permanent gates green (14/14).

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All tests in Tests to Add exist and pass; written test-first. | Every named test in `test_tle_export.py` (`test_tle_lines_are_well_formed`, `test_tle_fit_round_trip_within_bound` [9 cases], `test_tle_never_emits_outside_bound_for_degenerate_geo` [9 cases, added beyond the package's own list — see `BL-0164` adjudication], `test_tle_fits_every_shipped_vignette_orbit`, `test_tle_epoch_is_given_sim_time`, `test_tle_sourced_identity_and_bstar_carried`, `test_tle_rejects_unrepresentable`, `test_tle_export_is_deterministic`), `test_ephemeris.py` (`test_quick_tle_cell_uses_own_track_belief`, `test_quick_tle_rejects_untracked_and_stateless_track`, `test_quick_tle_own_asset_without_track_rejected`, `test_quick_tle_is_read_only`), `test_web.py` (`test_tle_route_returns_lines_for_tracked_object`, `test_tle_route_untracked_is_404`, `test_tle_route_requires_object_id`, `test_tle_route_white_reads_truth`, `test_tle_export_client_surface_is_served`) confirmed present by direct read and green in the full-suite run below. Test-first claim taken on trust of the project's standing workflow (no commit-granularity evidence available post-hoc); not independently falsifiable from a single squashed commit, same limitation noted in prior VRs. | ✅ Pass |
| A cell holding a `Track` (with `state_estimate`) on X gets a well-formed TLE within 1 km of its *believed* state at `world.now`; White gets truth. | `session/ephemeris.py:186-226::quick_tle()` read directly: cell path calls `world.track_for(cell, object_id)` → `_PROP.rv(tr.state_estimate, t)`, never `asset.orbit`; White (`cell is None`) path calls `_PROP.rv(asset.orbit, t)`. Independently re-tested end-to-end (not reusing the implementer's fixture) — see "Fog-of-war independent re-test" below: Blue's TLE reproduced its pre-manoeuvre belief (3.1 m residual) while truth had moved 61.2 km away; White's TLE reproduced truth (7.0 m residual). | ✅ Pass |
| Untracked / stateless-track / own-asset-without-track / unknown-id / unrepresentable requests are rejected with a reason (404 at the route). | `ephemeris.py:211-218` raises `ValueError` with a distinct reason for each case; `tle_export.py:198-204` raises for non-elliptic and sub-surface-perigee states; `server.py:732-742` catches `ValueError` → `HTTPException(404, detail=str(exc))`. Confirmed by `test_tle_route_untracked_is_404`, `test_quick_tle_rejects_untracked_and_stateless_track`, `test_quick_tle_own_asset_without_track_rejected`, `test_tle_rejects_unrepresentable`, all green. Independently re-probed with a fresh hyperbolic state and a fresh sub-surface-perigee Kepler orbit not in the shipped tests (see below) — both rejected cleanly. | ✅ Pass |
| The console shows the TLE in a copyable text field with a Copy button. | `ui_web/static/tleexport.js` (84 lines) + `index.html:178,785,813` (`#tle-open` menu item, `#tle-panel` markup, `<script src="/tleexport.js">`) + `style.css:395-413` (`#tle-panel` block, monospace textarea). `test_tle_export_client_surface_is_served` confirms `/tleexport.js` is served and references `/tle/`, and that `index.html` includes the script tag. Read `tleexport.js` directly: it fetches on open/selection change only (no polling), uses `navigator.clipboard.writeText` with a `document.execCommand("copy")` fallback — matches Design Decision 4 exactly. Not driven live in an actual browser (see Scope/UI-verification norm note, same standing project bar as `VR-1300`/`VR-1290`). | ✅ Pass |
| Full suite green, zero regressions; `test_determinism.py` and `test_import_guard.py` green. | See Test run below: 805 passed / 3 skipped (808 collected), 0 failed/errored; both gates 14 passed. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Every new test named above exists and is green. | Confirmed above; full-suite run below includes all of them, green. | ✅ Pass |
| `python3 -m pytest spacesim/tests/test_determinism.py` green. | `6 passed` (run jointly with import-guard: `14 passed in 1.28s`). | ✅ Pass |
| `python3 -m pytest spacesim/tests/test_import_guard.py` green. | `8 passed`. `engine/tle_export.py` read directly: imports only `math`, `typing.Optional`, `numpy`, `spacesim.engine.geometry`, `spacesim.engine.orbit`, and lazily (inside functions, exactly like `propagator._tle_rv`) `sgp4.api`/`sgp4.exporter` — no `spacesim.session`/UI/transport import, no `random`, no wall-clock read (`datetime.now`/`time.time`/etc. absent). The import-guard scanner (`test_import_guard.py`) AST-walks every file under `engine/`, so `tle_export.py` is in its scan scope — confirmed by reading the scanner's `_engine_files()` (`ENGINE_DIR.rglob("*.py")`) and `FORBIDDEN_IMPORT_ROOTS`/`WALL_CLOCK_ATTRS` lists directly, not merely trusting the green result. | ✅ Pass |
| Independently hand-check one exported TLE's checksums and its round-trip residual against a fresh orbit not used by the shipped tests. | Constructed a fresh Kepler orbit (`a=7100 km, e=0.015, i=63°, Ω=110°, ω=200°, ν=77°`, epoch `2027-06-15T03:22:10Z` — not in `test_tle_export.py`'s parameter list). `state_to_tle()` produced `L1`/`L2`; hand-computed the mod-10 checksum over columns 1-68 independently of `sgp4`/the test suite's own `_checksum_ok` helper and got `6`/`3`, matching the written checksum digits exactly. Measured `fit_error_m = 6.53 m`, well inside the 1 km bound. | ✅ Pass |
| Independently confirm the cell-scoped path never reads `world.assets[...].orbit` for a non-White request, and that White is wired via `get_godview()`. | `ephemeris.py:210-218` read directly: the `else` (cell) branch resolves `orbit` exclusively from `tr.state_estimate` (via `world.track_for`); it never touches `world.assets[object_id].orbit`. `asset.orbit` is read only inside the `if cell is None:` branch. `manager.py:830-838::get_tle()` read directly: `if cell == "white": return ephemeris.quick_tle(self.get_godview(), None, object_id)` — the identical shape as `get_ric_view()` (`:814-828`), verified `VR-1300`. | ✅ Pass |
| Confirm `export_tle`/`sgp4init` are the only TLE formatting/initialisation paths (no hand-rolled duplicate writer in `engine/`). | `grep -rn "export_tle\|sgp4init\|twoline2rv"` across `spacesim/engine/` shows exactly one `export_tle` call (`tle_export.py:211`) and one `sgp4init` call (`tle_export.py:96`, inside the single `_satrec()` helper reused by both the fit loop and the final build); `propagator.py` only calls `twoline2rv` (parsing an existing TLE, a different direction). No second fixed-width-field writer exists anywhere in `engine/`. | ✅ Pass |

## `BL-0164` adjudication (algorithm deviation)

**Disposition: DONE — deviation accepted, no remediation required.** Full reasoning below.

**What the package specifies (Design Decision 1, `IP-1211` lines 94-100):** "Fixed-point iteration:
start with mean ≈ target; each pass builds an SGP4 satellite record ... evaluates it at `tsince=0`,
converts its output to equinoctial elements the same way, and adds `(target − current)` ... to the
guess. Stop when the SGP4 position at epoch is within 1 cm of the target, or after a fixed maximum
iteration count (50)." This is a *plain* fixed-point iteration with no step-halving, no Jacobian,
and no monotone-acceptance safeguard.

**What shipped (`engine/tle_export.py::_fit_mean_elements`, lines 121-168):** each pass tries a
Newton step (forward-difference Jacobian solved against the wrapped residual) and the plain
fixed-point step, each with up to 12 step-halvings, accepting the first candidate that strictly
reduces a cost `|Δr| + 1000·|Δv|`; if neither candidate improves, the loop stops early with the
best guess found. This is a materially different algorithm from what the package specifies — not
a cosmetic rewording — so the deviation is real and the package text, as written, no longer
describes the shipped code.

**Was the deviation necessary?** Independently reproduced from scratch (not by reading the
implementer's own claim) by lifting out the shipped `_equinoctial_from_rv`/`_evaluate` helpers and
running the *plain* fixed-point loop by hand for several geometries:

- GEO, `e = 0.0002, i = 0.05°` (the shipped vignettes' actual GEO shape): plain fixed-point
  converges cleanly (16.2 km → 2.3 km → 475 m → 93 m → ... → 0.006 m over 10 passes).
- GEO, `e = 0.0, i = 0.0°` (exactly equatorial-circular): plain fixed-point **diverges**
  (18.5 km → 198 m → 367 m → ... → 422 m → 844 m → 1.68 km, growing without bound over 10 passes).
- GEO, `e = 0.0, i = 0.001°` and `i = 0.01°` (near-equatorial): plain fixed-point likewise
  diverges or oscillates without converging (residuals climbing into the multi-km range, then
  oscillating between ~4-20 km with no monotone trend).

This independently confirms the package's own diagnosis almost exactly: the plain iteration is
well-behaved for the shipped vignettes' actual (non-degenerate) GEO shape but genuinely diverges in
exactly the degenerate corner (`e ≈ 0`, `i ≈ 0`) the deviation note names. The safeguarded version
was then independently exercised across the same degenerate band plus several geometries chosen for
this pass specifically (not reused from `test_tle_export.py`): a sweep of GEO inclinations
`i ∈ {0.0, 0.001, 0.005, 0.01, 0.02, 0.05}°` at `e = 0.0` showed a narrow, non-monotonic rejection
island (`i = 0.001°` and `0.005°` reject cleanly with a reason; `i = 0.0°`, `0.01°`, `0.02°`,
`0.05°` all converge within 2-45 m) — odd-shaped, but **never once emitted a TLE outside the 1 km
bound**; every failure was a clean `ValueError`, never silent corruption. Separately constructed
five geometries outside the degenerate band entirely (near-equatorial GEO `i=0.02°`, retrograde
polar LEO, a Tundra-like HEO at `e=0.27`, an exactly-polar `i=90°` case) all converged to within
2-19 m — comfortably inside the bound. The contract (≤1 km bound, deterministic, reject-don't-
corrupt) is preserved exactly; only the *means* of reaching it changed.

**Is the 1 km accuracy claim genuinely sound?** Re-ran `test_tle_fits_every_shipped_vignette_orbit`'s
check independently (own script, not the test file) against all 19 shipped vignettes: 40 on-orbit
assets, round-trip residual range **1.56 m to 69.5 m**, mean 14.9 m — every one comfortably inside
the 1 km bound (margin ≥ 14×, consistent with the package's "deliberate 20× margin" framing for its
own worst-case LEO/GEO/HEO prototype figures). The 1 km bound holds for real.

**One documentation-accuracy note, not a defect in the code:** the pipeline journal's run #92 entry
and the package's own convergence-criterion text both describe "fits to < 1 cm" — that figure is
the *internal* Newton/fixed-point convergence tolerance (`_CONVERGED_M = 0.01` m, the SGP4-model-
match criterion checked *before* the text is quantised into fixed-width TLE fields), not the final
exported/parsed round-trip accuracy a consumer of the TLE text actually gets (which this pass
measured at 1.5-70 m across the shipped fleet, dominated by field quantisation exactly as the
package's own Design Decision 1 text says). Conflating the two in the journal's one-line summary
could mislead a future reader into thinking the *exported* TLE is sub-centimetre accurate, which it
is not and was never claimed to be at the code level (`engine/tle_export.py`'s own docstring and
the package's "1 km... deliberate 20× margin" framing are accurate; only the journal's shorthand is
loose). Filed as `BL-0165` (Low, doc-wording only) below — not a package or code defect, and not a
blocker.

**Verdict:** the deviation is sound, necessary, and faithfully documented in the shipped module's
own docstring (`tle_export.py:11-15`) and the package's own Outstanding Issue note. It does not
change the contract, the bound, the determinism, or the rejection behaviour the package promises.
**`BL-0164` → DONE, adjudicated accepted, no remediation routed to `08` or `07`.**

## Fog-of-war independent re-test

Independently built a fresh vignette/session (seed 42, start epoch `2030-01-01T00:00:00Z`, two
co-planar LEO satellites 30° apart in true anomaly, Blue holding an initial `Track` on Red) — not
reusing `test_ephemeris.py`'s `_two_sat_manager_with_track` fixture object, though the same shape
of scenario (necessary to get a Track in place at all). Applied an out-of-plane impulse burn to
Red's *true* orbit 300 s before `world.now` (after Blue's last observation snapshot), then called
`SessionManager.get_tle("blue", "SAT-RED")` and `SessionManager.get_tle("white", "SAT-RED")`
end-to-end through the full session layer (not the bare `ephemeris.quick_tle()` function the
implementer's own unit test calls):

- `blue` TLE: `source == "track"`; round-trip position **3.1 m** from Blue's stale belief, **61.2 km**
  from the new ground truth. The manoeuvre is not leaked.
- `white` TLE: `source == "truth"`; round-trip position **7.0 m** from ground truth.

This independently confirms the claim exactly as stated, through the full stack (manager → session
→ engine), not merely the engine-level or already-shipped session-level fixture.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-7440 | `engine/tle_export.py::state_to_tle`/`tle_identity`; `session/ephemeris.py::quick_tle`; `session/manager.py`/`inprocess.py::get_tle`; `ui_web/server.py` `GET /tle/{cell}`; `ui_web/static/tleexport.js` | `test_tle_export.py` (9 tests + parametrisations), `test_ephemeris.py::test_quick_tle_*` (4 tests), `test_web.py::test_tle_route_*`/`test_tle_export_client_surface_is_served` (5 tests) | `docs/requirements/03-requirements-traceability-matrix.md:224`'s `FR-7440` row cites `IP-1211` and the correct test names; still says "awaiting `09-package-verification`" — corrected below to reflect `VERIFIED`. | ✅ Pass |

## Test run

```
python3 -m pytest -q --junitxml=/tmp/.../junit_full.xml           # full suite
  → junit summary: tests=808, failures=0, errors=0, skipped=3  →  805 passed, 3 skipped
    (this environment's pytest run did not surface its own dot-stream summary line to the
    capture pipe either, as flagged by the implementing/prior sessions — counted from the
    JUnit XML's own testsuite attributes instead, not assumed)
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
  → 14 passed in 1.28s (6 determinism + 8 import-guard, both files individually itemised)
```
Plus the independent hand-checks recorded above: a fresh-orbit checksum/round-trip hand-check,
five independently-chosen geometries outside the shipped test parametrisation, a GEO-inclination
sweep reproducing the plain-vs-safeguarded divergence claim from scratch, and an end-to-end
fog-of-war re-test through `SessionManager.get_tle` on a freshly built session.

## Scope audit

`git show --stat bc1e157` touches exactly: `CLAUDE.md`, `ROADMAP.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/01-technical-work-breakdown.md`,
`docs/implementation/packages/INDEX.md`, `docs/requirements/03-requirements-traceability-matrix.md`,
`spacesim/engine/tle_export.py`, `spacesim/session/ephemeris.py`, `spacesim/session/inprocess.py`,
`spacesim/session/manager.py`, `spacesim/tests/test_ephemeris.py`, `spacesim/tests/test_tle_export.py`,
`spacesim/tests/test_web.py`, `spacesim/ui_web/server.py`, `spacesim/ui_web/static/index.html`,
`spacesim/ui_web/static/style.css`, `spacesim/ui_web/static/tleexport.js` — 17 files. Every one is
either explicitly named in the package's `Files to Create`/`Files to Modify` tables or is a ledger
file the package's own Documentation Updates section names (Master Build Plan, `packages/INDEX.md`,
`ROADMAP.md`, RTM). `01-technical-work-breakdown.md` is not individually named in the package text
but is the same class of ledger file every prior package's implementing commit also touches (same
pattern accepted without a finding in `VR-1300`/`VR-1290`). No excursion outside declared scope.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 (`BL-0165`, new) | The pipeline journal's run #92 summary ("every shipped-vignette orbit fits to < 1 cm") conflates the *internal* Newton/fixed-point convergence tolerance (`_CONVERGED_M = 0.01` m, checked before TLE-text quantisation) with the *exported/parsed* round-trip accuracy, which this pass independently measured at 1.5-70 m across the shipped fleet (still comfortably inside the 1 km bound, and consistent with the package's own Design Decision 1 text about field-quantisation residuals). The code's own docstrings and the package's "1 km... 20× margin" framing are accurate; only the journal's one-line shorthand overstates exported accuracy. Doc-wording only, no code or contract defect. | Low | `00-pipeline-manager` (journal wording correction on next touch; no code change) |

## Related

[IP-1211](../packages/IP-1211-quick-tle-export.md) · [FS-121](../../features/FS-121-ephemeris-export.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md) ·
[docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0164` (adjudicated `DONE` above), `BL-0165`
(new, this report), `BL-0163` (training-manual coverage, unblocked by this report — routed to
`08-training-manual-authoring`), `BL-0159` (own-asset scope, left `DEFERRED`, unchanged)
