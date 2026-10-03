# VR-1180 — Verification Report: External Vignette Directories & Safe Scenario Save Target

> **Document ID:** VR-1180
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1180](../packages/IP-1180-external-vignette-directories.md), [FS-118](../../features/FS-118-external-vignette-directories.md) (`FR-5410`, `FR-5420`, `NFR-3700`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md), [VR-1200](VR-1200-save-as-scenario.md)
> **Produces:** the `COMPLETE → VERIFIED` transition for IP-1180
> **Feature Mapping:** FS-118
> **Related Topics:** [`spacesim/config.py`](../../../spacesim/config.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/content/vignette_export.py`](../../../spacesim/content/vignette_export.py),
> [`spacesim.config.yaml`](../../../spacesim.config.yaml)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1180 — External Vignette Directories & Safe Scenario Save Target
- **Version verified:** 1.0
- **Tree state verified:** code at `d2818ff`. The branch tip is `01dc3b7`; everything after
  `d2818ff` is docs-only verification commits. Implementing commit: `9479f7d`. `IP-1200` (commit
  `e23e8d3`) was later built on top of the same two files. This report verifies IP-1180's claims
  against the current tree, so it also confirms that IP-1200 did not regress them. IP-1180 is
  verified before IP-1200 on purpose, per the coordination note both packages carry.
- **Independence:** implemented by `08-code-implementation` in a prior context. This verification
  ran in a freshly spawned agent context with no memory of that work. **Disclosure:** the
  implementing commit's `Claude-Session` trailer names the same outer remote session ID this agent
  runs under. Every claim was re-derived from the source, a fresh test run and hand-built temporary
  directory fixtures.

## Result

**VERIFIED, with 1 Low finding.** Every Definition of Done and Verification Checklist item was
confirmed against the current tree. The full suite is green (707 passed, 3 skipped), and both
permanent gates are green.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization (MSTR-006 §3). | Granted 2026-09-27; recorded in the package and in the Master Build Plan. | ✅ Pass |
| `list_vignettes()` enumerates external directories alongside `VIGNETTE_DIR` and tags each entry's origin. Empty configuration reproduces baseline behaviour. | `content/vignette.py:153-206`. Probe: `list_vignettes([])` returned the 19 built-ins, all tagged `origin: "built-in"`. With fixture directories `extA`/`extB` the listing returned 21 entries, and each external entry was tagged with its directory basename. The one additive difference from baseline is the new `origin` key, which is by design. `test_list_vignettes_empty_external_dirs_reproduces_baseline` and `…enumerates_external_directory_with_origin_tag` pass. | ✅ Pass |
| `load_vignette()` finds a vignette that exists only in an external directory. | `vignette.py:209-262`: after the built-in search it falls through, in order, to each external directory, first by filename and then by declared id. Probe: `load_vignette("ext-only", [A, B])` returned `extA`'s copy ("EXT A"). The test passes. | ✅ Pass |
| An unreadable or nonexistent external directory is skipped without failing the build. | `vignette.py:179-183`: `not ext_dir.is_dir()` produces a WARNING and `continue`. Probe: a `missing` directory placed between `extA` and `extB` was logged and skipped, and `extB` was still enumerated. A malformed YAML file inside `extA` was skipped silently, using the pre-existing per-file tolerance. | ✅ Pass |
| A built-in versus external id collision resolves to built-in, with the shadow logged. | `seen_ids` is seeded from the built-in scan. Probe: `extA/x.yaml`, declaring id `training-basics` with title "SHADOW", was skipped with the WARNING "shadowed by an earlier entry". The catalog kept the built-in title "Training: Basics", and `load_vignette("training-basics", [A])` returned the built-in. External-versus-external collisions (`ext-only` in both A and B) resolved to the first configured directory, also logged. | ✅ Pass |
| `save_vignette()` writes only to a configured `user_save_dir`, never `VIGNETTE_DIR`, and raises a specific error when that is unconfigured. | `vignette_export.py:62-90`: reads `load_content_config().user_save_dir`, raises `ValueError("no user-save directory configured — set content.user_save_dir …")`, then resolves through `_resolve_within_root`. There is no `VIGNETTE_DIR` reference in the module. Probe: through `InProcessSession`, an unconfigured save raised that exact error. A configured save wrote `saves/saved-one.yaml`, and `VIGNETTE_DIR/saved-one.yaml` did not exist. The route (`server.py:329-340`) maps the error to HTTP 400. | ✅ Pass |
| The traversal guard rejects identically against `VIGNETTE_DIR`, every external directory and the user-save directory, with no filesystem access on rejection. | `_validate_id` (`vignette.py:32-43`) runs first in `load_vignette` and in `export_vignette` (`vignette_export.py:34`), which `save_vignette` calls before any path work. `_resolve_within_root` (`:46-53`) is parameterized by root and used for the built-in directory, each external directory and the save directory. Probe: `../etc/passwd`, `..`, `~root`, `.hidden`, `a/b` and `x y` were all rejected on the load path, and `../esc` was rejected on the save path. | ✅ Pass |
| Full suite green; both gates green. | See Test run. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| New `ContentConfig`/`load_content_config()` tests in `test_config.py` exist and pass. | `test_config.py:54-92` (5 tests), all passing. `config.py:47-74` mirrors `load_server_config()`: optional file, `SPACESIM_CONFIG` override. | ✅ Pass |
| New external-directory, collision and save-retargeting tests exist and pass. | All 9 DoD-named tests found (in `test_content.py` and `test_vignette_export.py`) and passing. The regression `test_load_vignette_rejects_path_traversal` lives in `test_defensive_audit_2026.py` and passes. | ✅ Pass |
| `test_determinism.py` passes. | 14 passed (with the import guard). | ✅ Pass |
| `test_import_guard.py` passes. | Same run. No `spacesim/engine/` change. | ✅ Pass |
| Full suite has zero regressions, especially IP-1173's save tests. | 707 passed, 3 skipped. `test_vignette_creator_session.py`'s save tests now use an autouse `user_save_dir` fixture that also registers the save directory as an external directory. This is a regression-preserving update, not a rewrite. | ✅ Pass |
| Independently confirm `_validate_id`/`_resolve_within_root` are shared between the load and save paths, not duplicated. | `vignette_export.py:18` imports both from `content.vignette`. The module's former local `_ID_RE` is gone (grep: no `_ID_RE` in `vignette_export.py`). There is one copy of the guard. | ✅ Pass |
| Independently confirm the built-in-wins rule and the unreadable-directory skip with hand-built fixtures. | Done with temporary-directory fixtures written for this report (see the DoD rows above). | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-5410 | `config.py` (`ContentConfig`, `load_content_config`); `content/vignette.py` (`list_vignettes`, `load_vignette`, `_configured_external_dirs`) | `test_content.py` (external-directory, collision and traversal tests), `test_config.py` | `:190` is accurate. Updated to `VERIFIED (VR-1180)`. | ✅ Pass |
| FR-5420 | `content/vignette_export.py::save_vignette`; `ui_web/server.py` save route (400 on `ValueError`) | `test_vignette_export.py`, `test_vignette_creator_session.py`, `test_web.py` | `:191` is accurate. Updated to `VERIFIED (VR-1180)`. | ✅ Pass |
| NFR-3700 | `content/vignette.py` (`_validate_id`, `_resolve_within_root`), `content/vignette_export.py` | `test_content.py::test_load_vignette_rejects_traversal_against_external_directory_too`, `test_vignette_export.py::test_export_vignette_rejects_traversal_id_before_any_filesystem_access`, `test_defensive_audit_2026.py::test_load_vignette_rejects_path_traversal` | `:328` is accurate. This NFR-table row has no Impl. Package column; the Affected-subsystems cell already names `IP-1180`. Left as is. | ✅ Pass |

## Test run

```
PYTHONPATH=. python3 <scratchpad>/p1180.py      # independent fixture probe (not committed)
  → LOG shadowed 'training-basics' in extA; LOG missing dir skipped; LOG 'ext-only' in extB shadowed
  → builtin count 19, total 21; [('ext-only','extA','EXT A'), ('b-only','extB','B')]
  → load ext-only → EXT A; load training-basics → Training: Basics
  → 6 traversal ids rejected; unconfigured save → ValueError(...content.user_save_dir...)
  → configured save → <tmp>/saves/saved-one.yaml, not in VIGNETTE_DIR; '../esc' save → ValueError

python3 -m pytest -o addopts="" -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py  → 14 passed
python3 -m pytest -o addopts="" -q            → 707 passed, 3 skipped, 1 warning in 156.06s
```

## Scope audit

`git show --stat 9479f7d` touched:

- **Production code:** `spacesim/config.py`, `content/vignette.py`, `content/vignette_export.py`,
  `spacesim.config.yaml`.
- **Tests:** `test_config.py`, `test_content.py`, `test_vignette_creator_session.py`, `test_web.py`,
  and the new `test_vignette_export.py`.
- **Docs:** `CLAUDE.md`, `ROADMAP.md`, the ICD, `FS-118`, the RTM, the Master Build Plan,
  `packages/INDEX.md`, `01-technical-work-breakdown.md`, the package, and
  `docs/pipeline/pipeline-journal.md`.

The code falls inside Files to Modify. The journal edit is the same process-scope note recorded
in `VR-1190` L2 (combined pipeline-manager run). It is not repeated as a separate finding here.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 | A file written by "Save as Vignette" (or IP-1200's save-as-scenario) lands in `user_save_dir`. That directory is **not** automatically part of the load catalog, so the file cannot be loaded back until the facilitator also lists it under `external_vignette_dirs`. The example `content:` block in `spacesim.config.yaml` does not say so. The test suite's own fixture configures both keys, which shows the need. It is not a requirement failure: `FR-5410` and `FR-5420` are each met as written. | Low | `07-implementation-planning`/`06-feature-specification` (either auto-include `user_save_dir` in the catalog or document the two-key setup), and `08-training-manual-authoring` for the operator-facing note |

## Related

[IP-1180](../packages/IP-1180-external-vignette-directories.md) · [FS-118](../../features/FS-118-external-vignette-directories.md) ·
[VR-1173](VR-1173-vignette-creator-draft-session.md) · [VR-1200](VR-1200-save-as-scenario.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
