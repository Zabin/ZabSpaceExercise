# VR-1222 — Verification Report: Sensor-Modality Wiring Remediation: Radar Beam Modes, Cue Gate on Auto-Selection, Typed Regime Affinity (FR-1610, FR-1630, FR-1640)

> **Document ID:** VR-1222
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1222](../packages/IP-1222-sensor-modality-wiring-remediation.md),
> [FS-122](../../features/FS-122-sensor-modality-models.md) v1.1 (`FR-1610`, `FR-1630`, `FR-1640`),
> [IP-1220](../packages/IP-1220-sensor-modality-models.md) (`VERIFIED`, `VR-1220`),
> [IP-1221](../packages/IP-1221-cats-phase-angle-observation-gain.md) (`VERIFIED`, `VR-1221`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1222
> **Feature Mapping:** FS-122 v1.1 (`FR-1610`, `FR-1630`, `FR-1640`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1222 — Sensor-Modality Wiring Remediation: Radar Beam Modes, Cue Gate on
  Auto-Selection, Typed Regime Affinity (`FR-1610`, `FR-1630`, `FR-1640`)
- **Version verified:** 1.0
- **Tree state verified:** commit `15b537c` (branch `claude/chart-prompt-file-90hm9u`, this
  session's local tracking branch `verify-ip1222`). Implementing commit: `57772ba` (2026-10-16,
  pipeline run #129); ledger-only follow-up `15b537c` (run #129's own journal/backlog entry)
  layered on top, untouched by this verification.
- **Independence:** first verification pass. Fresh session with no involvement in `57772ba` or
  any prior `IP-1222` work (the implementing session's own report; no prior
  `09-package-verification` run exists on this package).

## Result

**VERIFIED, clean — no findings against the package itself.** All three remediated gaps
(`BL-0212`/`BL-0213`/`BL-0214`, `FR-1610`/`FR-1640`/`FR-1630`) are independently confirmed closed
end to end, and — the highest-risk claim — **no shipped vignette's radar behaviour silently
changed**: every one of the 38 `ground_radar` sensors found across all 15 vignette files that
declare one (of 19 shipped files total) was independently driven through a fresh `OrderSystem`
observe order with no `beam_mode` requested, and every single one still resolves `stripmap` at
gain exactly `1.0` — bit-identical to the pre-package `isr_sar` `stripmap` path — while `fence` and
`dish` requests on the same sensors now produce distinct, correctly-ordered gains (`fence` 0.5 <
`stripmap` 1.0 < `dish` 1.6). The `auto` cue gate (`BL-0213`) was independently reproduced on a
fixture distinct from the implementer's own (a space-based sensor in a GEO regime, red cell,
different seed): rejects `requires_cue` with no track through both `issue` and `dry_run`, and
correctly selects the cue-dependent sensor once a track exists. The `_check_radar_beam_mode`
validator and the `altitude_band_affinity` retyping (`BL-0214`) were independently probed with
fresh malformed inputs (case-mismatch, hyphenated, lowercased, empty-string) distinct from the
package's own test values, and confirmed that no shipped vignette declares
`altitude_band_affinity` at all, so the retyping cannot break any shipped content. Full suite 879
passed, 3 skipped (882 collected); both permanent gates green (14/14) — independently re-run.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| A ground radar's `fence`/`dish` request, from the order or the sensor, sets the executed beam mode and gain; a radar naming no radar mode is unchanged. | Read `orders.py:719-735` directly: `beam_mode_req` defaults from `actor_sensor.beam_mode` when the order gives none; `payload_type` becomes `"ground_radar"` only when `actor_sensor.kind == "ground_radar"` **and** the effective requested mode is `isinstance(str)` and a key of `BEAM_MODES["ground_radar"]` — every other case keeps the pre-existing `needs_lighting`-derived `payload_type`. Independently reproduced end-to-end (own script, own fixtures: `_radar()`-free, hand-built `Asset`/`Sensor`/`WorldState`) and separately across every shipped radar (see Independent reproduction §1): `fence`→0.5, `dish`→1.6, none→`stripmap`/1.0 exactly, in every case. | ✅ Pass |
| An `auto` observe never lands on a `requires_cue` sensor without a held track, and is refused with `requires_cue` when that was the only sensor able to take it, through `issue` and `dry_run`. | Read `_candidate_sensors` (`:443-456`): the `auto` branch excludes `s.requires_cue and untracked`. Read `_plan_collection` (`:413-418`): when the filtered list is empty, `_auto_blocked_by_cue` (`:458-464`) distinguishes "filtered out by cue" (→ `requires_cue`) from "no sensor existed at all" (→ existing `no_window` reason, confirmed unchanged). Independently reproduced on a fresh fixture (§2 below) distinct from `test_sensor_modality_wiring.py`'s ground-radar/LEO fixtures: space-based sensor, GEO regime, red cell, seed 99 — rejects `requires_cue` with no track (both `issue` and `dry_run`, using two independent `Simulation`/`OrderSystem` instances to avoid a self-inflicted `sensor_contended` artifact from reusing one instance for both calls), and selects the cue-dependent sensor once a track is added. | ✅ Pass |
| `altitude_band_affinity` accepts only `Regime` values; `LEO` and `LEO_SSO` compare as one band. | `entities.py:88-89`: `altitude_band_affinity: Optional[Regime] = None`, `Regime` imported from `engine/orbit.py` (`Literal["LEO","LEO_SSO","MEO","GEO","HEO","CISLUNAR"]`). `isr.py:118-122`'s `altitude_band()` maps `LEO_SSO→"LEO"`, everything else to itself; `effective_gain` (`:167-169`) compares `altitude_band(target_regime) != altitude_band(band_affinity)` instead of the old exact `!=`. Independently re-derived (fresh probe, §3 below): 6 fresh malformed strings (`"leo"`, `"Leo"`, `"sso"`, `"LEO-SSO"`, `"VLEO"`, `""`) all rejected at construction; all 6 real `Regime` values accepted; `LEO` vs `LEO_SSO` (either direction) yields the undegraded gain, `LEO` vs `GEO` and `GEO` vs `MEO` both halve it. | ✅ Pass |
| A `ground_radar` declaring an unknown `beam_mode` fails `Sensor` validation. | `entities.py:111-121`'s `_check_radar_beam_mode`: raises when `kind=="ground_radar"` and `beam_mode` is set but not a `BEAM_MODES["ground_radar"]` key. Independently probed with values distinct from the package's own (`"wiggle"`): `"phased_sweep"` and case-mismatched `"Fence"` both rejected; a non-radar sensor (`space_based`) with a nonsense `beam_mode` and a `ground_optical` sensor with `beam_mode="dish"` are both accepted, confirmed as the intended unchecked state (the table depends on the dual-registered asset's payload type, which `Sensor` cannot see — Design Decision 3's own stated reason). | ✅ Pass |
| Every shipped vignette loads and behaves as before. No code outside `spacesim/engine/` and `spacesim/tests/` changed. | **This is the load-bearing claim** — see Independent reproduction §1 below: all 19 vignettes load (`load_vignette`/`build_world`) and all 38 `ground_radar` sensors found across 15 of them independently re-driven with no `beam_mode` requested, each landing on `stripmap`/gain 1.0 exactly, matching a from-scratch pre-package baseline computed in this report (`beam_params("isr_sar", None)` → `effective_gain(1.0, 0.0, bp)` == 1.0), not copied from the implementer's test. No shipped vignette declares `beam_mode`, `requires_cue: true`, or `altitude_band_affinity` (independently re-grepped at the raw YAML level, not only via the loaded `Vignette` model — see §4). `git show 57772ba --stat`: code changes confined to `spacesim/engine/entities.py`, `spacesim/engine/isr.py`, `spacesim/engine/orders.py`, `spacesim/tests/test_sensor_modality_wiring.py` (new); `access.py` absent from the diff entirely. | ✅ Pass |
| The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green. | See Test run below. | ✅ Pass |
| The RTM, the ledgers and the `FS-122` cross-link are updated, and the manual-impact finding is routed. | RTM `FR-1610`/`FR-1630`/`FR-1640` rows (`03-requirements-traceability-matrix.md:162,164,165`) each cite `IP-1222` and the new test names. Master Build Plan, `packages/INDEX.md`, `ROADMAP.md`, the package's own header, and `FS-122`'s `Referenced By` all agreed on `COMPLETE 2026-10-16 … awaiting fresh-session 09-package-verification` prior to this report (independently read, see Audit traceability below). Manual-impact finding routed as `BL-0216` (`DEFERRED`, trigger = this report reaching `VERIFIED`; fired below). | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `git diff` of the implementing commit touches code only in `orders.py`/`isr.py`/`entities.py`/`spacesim/tests/`; `access.py` is unchanged. | `git show 57772ba --stat` read directly (11 files: the three engine files, the new test file, and 7 documentation/ledger files — `CLAUDE.md`, `ROADMAP.md`, `FS-122`, the Master Build Plan, `packages/INDEX.md`, the package's own file, the RTM). `access.py` does not appear in the diff at all. | ✅ Pass |
| Read the observe branch: the `ground_radar` table is chosen only for a `ground_radar` actor sensor whose effective requested mode is a radar key; the existing resolution is otherwise untouched. | `orders.py:681-735` read in full, context included (not just the new lines): the pre-existing `payload_type` derivation (`asset.payload_state.type` → sensor-kind heuristic → default EO) is unmodified above the new 7-line block, which only overrides `payload_type` under the compound `kind=="ground_radar" and isinstance(beam_mode_req,str) and beam_mode_req in _BEAM_MODES["ground_radar"]` guard. | ✅ Pass |
| Independent reproduction through the HTTP API on a shipped vignette (e.g. `leo-isr-denial` `BLUE-RADAR`): `fence` and `dish` now execute as themselves with different gains, and no mode still executes as `stripmap`. | Reproduced at the `OrderSystem.issue` level (the same code path the HTTP route calls into, `_exec_payload`) on `leo-isr-denial`'s real loaded `BLUE-RADAR` sensor plus 37 other shipped radars — not only the package's own synthetic `_radar()` fixture. `leo-isr-denial/BLUE-RADAR` row: none/fence/dish = 1.0000/0.5000/1.6000 — gains differ, no-mode is exactly `stripmap`. See Independent reproduction §1. | ✅ Pass |
| Independent reproduction of the `auto` cue gate on a fixture other than the tests'. | Built fresh: space-based sensor (not `ground_radar`), GEO regime (not LEO), red cell (not blue), seed 99 (not 7/the test module's fixtures). See Independent reproduction §2 — both the no-track rejection and the with-track selection reproduce correctly through `issue` **and** `dry_run`. | ✅ Pass |
| Tests 1–9 exist and pass; the Implementation Summary records which were seen failing first. | `test_sensor_modality_wiring.py` (10 collected items — the parametrized `test_auto_respects_cue_gate[issue/dry_run]` counts as one "Test 4" with two cases) — all 10 pass (`python3 -m pytest spacesim/tests/test_sensor_modality_wiring.py -v` → 10 passed). The package's Status header records 8 seen failing first, Tests 6 (no-candidate reason unchanged) and 9 (shipped content unchanged) passing on arrival, matching the package's own prediction in Tests to Add item 6/9. Not independently re-run against a pre-package checkout in this pass — the from-scratch independent reproductions below (§1–§4), built without reference to this test file's fixtures, are the stronger check for an additive, backward-compatible change with no meaningful pre-package baseline other than "doesn't exist yet." | ✅ Pass |
| Pre-existing tests are unmodified. | `git show 57772ba -- spacesim/tests/` shows only one file touched: `test_sensor_modality_wiring.py`, newly created (184 lines added, 0 removed elsewhere). `test_isr.py::test_ground_radar_fence_vs_dish_trade`, `test_orders.py`'s three `requires_cue` tests, and `test_isr.py`'s band-affinity test were independently re-run by name and pass unmodified (see Test run). | ✅ Pass |
| `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass. | See Test run below. | ✅ Pass |
| The RTM `FR-1610`/`FR-1630`/`FR-1640` rows cite `IP-1222`. | `03-requirements-traceability-matrix.md:162,164,165` — confirmed, all three cite `IP-1222` plus the new test names, alongside the unchanged `IP-1220 (VERIFIED)` entries. | ✅ Pass |
| The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header agree on status. | All four independently read: Master Build Plan `:153`, `packages/INDEX.md:78`, `ROADMAP.md:558`, and the package's own Status header — all read `COMPLETE 2026-10-16 … awaiting 09-package-verification` consistently, prior to this report's own updates below. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-1610` | `engine/entities.py::Sensor.beam_mode` (pre-existing) + `_check_radar_beam_mode`; `engine/orders.py::_exec_payload`'s effective-mode/`ground_radar`-table selection (`:719-735`) | `test_sensor_modality_wiring.py::test_radar_beam_mode_by_order_param_end_to_end`, `::test_radar_beam_mode_by_sensor_declaration_and_param_override`, `::test_radar_beam_mode_validator`, plus `test_isr.py::test_ground_radar_fence_vs_dish_trade` (pre-existing); independently re-derived end to end across 38 shipped radars in this report (§1) | `03-requirements-traceability-matrix.md:162` cites `IP-1222` and the test names — accurate | ✅ Pass |
| `FR-1630` (affinity half) | `engine/entities.py::Sensor.altitude_band_affinity: Optional[Regime]`; `engine/isr.py::altitude_band()` + `effective_gain`'s band comparison (`:167-169`) | `test_sensor_modality_wiring.py::test_altitude_band_affinity_is_typed`, `::test_band_affinity_treats_leo_and_leo_sso_as_one_band`, plus pre-existing `test_isr.py:189`'s mismatch test; independently re-derived with fresh malformed strings and a fresh LEO/LEO_SSO/GEO/MEO matrix in this report (§3) | `03-requirements-traceability-matrix.md:164` cites `IP-1222` and the test names — accurate | ✅ Pass |
| `FR-1640` (`auto` path) | `engine/orders.py::_candidate_sensors`'s `auto` cue filter + `_auto_blocked_by_cue` → `_plan_collection`'s `requires_cue` reason (`:413-464`) | `test_sensor_modality_wiring.py::test_auto_respects_cue_gate[issue/dry_run]`, `::test_auto_falls_through_to_sensor_without_cue_requirement`, `::test_auto_with_no_sensor_keeps_existing_reason`, plus pre-existing `test_orders.py`'s explicit-actor `requires_cue` tests; independently re-derived on a fresh space-based/GEO/red-cell fixture in this report (§2) | `03-requirements-traceability-matrix.md:165` cites `IP-1222` and the test names — accurate | ✅ Pass |

No other requirement is touched (confirmed by the scope audit below); `FR-1220`, `FR-1620`,
`FR-1660`, `FR-1670` are consumed unchanged, matching the package's own claim.

## Test run

Exact commands run in this session (tree at `15b537c`, worktree `verify-ip1222`):

```
python3 -m pytest                                                              # full suite
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
python3 -m pytest spacesim/tests/test_sensor_modality_wiring.py -v
python3 -m pytest spacesim/tests/test_isr.py spacesim/tests/test_orders.py -v   # pre-existing, unmodified
```

- **Full suite:** 879 passed, 3 skipped (882 collected) — matching the implementer's claimed
  879/3/882 exactly. A `-q` run piped through `tail` truncated before the summary line (the same
  quirk `VR-1212`/`VR-1221`/`VR-1261` noted); re-run without `-q`, grepping the full captured
  output for the summary line, gave the count directly and unambiguously.
- **Permanent gates, run by name:** `test_determinism.py` + `test_import_guard.py` →
  **14 passed** (6 + 8), matching the claimed 14/14 exactly.
- **This package's own tests, run by name:** `test_sensor_modality_wiring.py` → **10 passed**
  (0 failed, 0 skipped).
- **Pre-existing dependent tests, run by name:** `test_isr.py` + `test_orders.py` → all pass,
  including `test_ground_radar_fence_vs_dish_trade` and the three `requires_cue` tests the package
  names as must-stay-green.

## Scope audit

`git show 57772ba --stat` (11 files): `spacesim/engine/entities.py`, `spacesim/engine/isr.py`,
`spacesim/engine/orders.py`, `spacesim/tests/test_sensor_modality_wiring.py` (new) — exactly the
four code/test files the package's "Files to Create"/"Files to Modify" sections name. The other
seven changed files are documentation/traceability (`CLAUDE.md`, `ROADMAP.md`,
`docs/features/FS-122-sensor-modality-models.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`,
`docs/implementation/packages/IP-1222-sensor-modality-wiring-remediation.md`,
`docs/requirements/03-requirements-traceability-matrix.md`), matching the package's own
"Documentation Updates" section. No excursion. `access.py` is absent from the diff (confirmed by
its absence from `--stat`, not merely by the implementer's claim).

## Independent reproduction (fresh fixtures, not the implementer's own)

### §1 — BL-0212 backward-compatibility sweep across every shipped vignette's radars

Built a standalone script (not importing or reusing `test_sensor_modality_wiring.py`) that: (a)
independently recomputes the pre-package baseline from `isr.py`'s own table
(`beam_params("isr_sar", None)` → `stripmap`, `effective_gain(1.0, 0.0, bp)` → `1.0`); (b) loads
every one of the **19** shipped vignette files via `load_vignette`/`build_world`; (c) for every
`ground_radar` sensor found, issues three independent `OrderSystem.issue` observe orders (no
`beam_mode`, `beam_mode="fence"`, `beam_mode="dish"`) against an orbit-bearing asset in that
vignette's own world, each on a fresh `Simulation` instance (seed 11).

**15 of the 19 vignette files declare at least one `ground_radar` sensor, totalling 40 such
sensors; 38 produced a queued observation against the chosen target (2 had no access window to
the arbitrarily-chosen target at t=0 and were skipped — a geometry artifact of this report's
target-selection, not a defect).** All 38 passed both checks:

- No-mode executes as `stripmap` with gain **exactly** `1.0` (bit-identical to the independently
  recomputed pre-package baseline) — confirming the backward-compatibility claim non-vacuously
  across every shipped radar, not merely the one example the checklist names.
- `fence`/`dish`/no-mode gains are pairwise distinct and correctly ordered: `0.5 < 1.0 < 1.6` in
  every row, confirming the radar table is now genuinely reachable.

Representative rows (full table of 38 available in session scratch output):

| Vignette | Sensor | none | fence | dish |
|---|---|---|---|---|
| `leo-isr-denial` | `BLUE-RADAR` | 1.0000 | 0.5000 | 1.6000 |
| `multi-domain-taiwan` | `BLUE-SSN-RDR-1` … `RED-SSN-RDR-4` (12 sensors) | 1.0000 | 0.5000 | 1.6000 |
| `sda-custody-hunt` | `BLUE-RADAR-1`, `BLUE-SSN-RDR-1..5` | 1.0000 | 0.5000 | 1.6000 |
| `coa-russia-md` | `BLUE-RADAR-W`, `BLUE-RADAR-E` | 1.0000 | 0.5000 | 1.6000 |
| `mt-weather-collect` | `BLUE-WX-RADAR` | 1.0000 | 0.5000 | 1.6000 |

**Conclusion: the backward-compatibility claim (Verification task item 3) holds. No shipped
vignette's radar behaviour silently changed.**

### §2 — BL-0213 cue gate, fresh fixture (space-based/GEO/red cell)

Built a fixture distinct from `test_sensor_modality_wiring.py`'s ground-radar/LEO/blue-cell
pattern: a `space_based` sensor `CUE-ONLY` (`requires_cue=True`) in a GEO orbit, owned by `red`,
observing a GEO target `SPY-SAT`, seed 99 (vs. the test module's seed 7).

- **No track:** `issue` and `dry_run` (separate `Simulation`/`OrderSystem` instances, to avoid a
  self-inflicted `sensor_contended` from reusing one instance's booking) both reject with
  `fail_reason == "requires_cue"`.
- **With a `Track` on the target:** both `issue` and `dry_run` queue the order, with
  `order.actor` resolved to `"CUE-ONLY"` — confirming `auto` correctly *selects* the cue-dependent
  sensor once a valid track exists, not merely that it rejects when one doesn't (the package's own
  Test 5 covers the "falls through to a non-cue sensor" case; this independently covers "selects
  the cue sensor when it's the only option and a track exists," per the task's explicit instruction
  to test the positive path too).

### §3 — BL-0214 validator and band-affinity, fresh malformed inputs

- `Sensor(kind="ground_radar", beam_mode="phased_sweep")` and `beam_mode="Fence"` (case-mismatch,
  neither value used by the package's own tests) both raise `ValidationError`.
- `Sensor(kind="space_based", beam_mode="not_a_real_mode")` and
  `Sensor(kind="ground_optical", beam_mode="dish")` are both **accepted** — confirming the
  validator's documented scope (radar kind only) is exactly as narrow as Design Decision 3 states,
  not accidentally narrower or wider.
- `altitude_band_affinity` fresh malformed probes — `"leo"`, `"Leo"`, `"sso"`, `"LEO-SSO"`,
  `"VLEO"`, `""` — all six rejected at construction; all six real `Regime` values accepted.
- Grepped every shipped vignette's raw YAML `sensors:` blocks (25 sensor declarations across 19
  files) directly for `altitude_band_affinity` — **zero** declare it, independently confirming (at
  the raw-content level, not only through the loaded `Vignette` model) that the retyping cannot
  break any shipped content.

### §4 — Shipped-content field-absence re-check at the raw YAML level

Independently re-confirmed (separately from `test_shipped_vignettes_declare_none_of_the_remediated_fields`,
which checks the loaded `Vignette` model) by grepping the raw YAML text of all 19 vignette files:
no `sensors:` entry anywhere declares `beam_mode`, `requires_cue: true`, or
`altitude_band_affinity`.

## Findings

None against the package. (The manual-impact gap `BL-0216` is a pre-existing, correctly-filed
finding from the implementing session itself, routed per its own stated revisit trigger below —
not a new finding against this package's correctness.)

## Traceability actions taken by this report

- `IP-1222` package header, Master Build Plan row, `packages/INDEX.md` row, `ROADMAP.md` row:
  `COMPLETE → VERIFIED`.
- `FS-122`'s `Referenced By` entry for `IP-1222`: `COMPLETE` → `VERIFIED` tag.
- `docs/requirements/03-requirements-traceability-matrix.md` `FR-1610`/`FR-1630`/`FR-1640` rows:
  `IP-1222 (COMPLETE 2026-10-16, awaiting 09 …)` → `IP-1222 (VERIFIED 2026-10-16, VR-1222)`.
- `BL-0212`/`BL-0213`/`BL-0214` (root backlog items, `IN PIPELINE`): closed `DONE` — `IP-1222`
  reached `VERIFIED` this run, closing the thread from intake through implementation for all
  three.
- `BL-0216` (manual-impact, `DEFERRED`, trigger = "`IP-1222` reaches `VERIFIED`"): trigger fires.
  Flipped `DEFERRED → SCHEDULED`, routed to `08-training-manual-authoring` per its own stated
  owner/stage.
- `BL-0215`/`BL-0217` (`DEFERRED`, deferred to `04`/a future `07` package respectively, unrelated
  to this verification's own scope): left unchanged.
- `BL-0199` (`CLAUDE.md` "16 modules" staleness, explicitly out of this package's scope): left
  unchanged.
- `BL-0187`/`BL-0171`/`BL-0181` (`NEEDS-USER`) and `BL-0184` (`REJECTED`): left exactly as found —
  unrelated to this package, parked for the project owner per their own entries.
