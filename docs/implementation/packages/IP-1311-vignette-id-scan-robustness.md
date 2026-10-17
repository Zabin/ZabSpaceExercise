# IP-1311 — Vignette Id Scan Robustness: One Unreadable File Never Turns a Lookup Into a 500 (FR-5310, NFR-1600)

> **Package ID:** IP-1311
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-17 by `07-implementation-planning`, pipeline run #158.
> Every dependency is `VERIFIED`. **Authorization (MSTR-006 §3):** this package falls under the
> project owner's standing pre-authorization of 2026-10-11 for the packages this iteration
> reaches (same precedent as `IP-1310`/`IP-1320`). Authoring the package is not itself the
> authorization; that standing decision is.
> **Dependencies:** [FS-131](../../features/FS-131-load-time-vignette-validation.md) v1.1 (the spec);
> [IP-1310](IP-1310-load-time-vignette-validation.md) (the load gate this hardens) and
> [IP-1180](IP-1180-external-vignette-directories.md) (the external-root scan it mirrors), both
> `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0252`
> **Produces:** a vignette lookup by declared id that skips unreadable or malformed files instead
> of crashing, so an unknown id is always a 404 and a valid vignette always loads, whatever else
> is in the folder.
> **Feature Reference:** [FS-131 — Load-Time Vignette Validation](../../features/FS-131-load-time-vignette-validation.md)
> (`FEAT-5300`)
> **Related Topics:** [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py) (`_vignette_load_errors`),
> [REV-TRN-008](../../reviews/training-review-runs140-148-scope.md) F2

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design) for a defect `IP-1310` left in the id-resolution step that
runs before its gate. It was found by the independent training review REV-TRN-008 (run #156) and
reproduced live.*

---

## Package ID

IP-1311 (FS-131 → `IP-131x`; `IP-1310` is the gate itself, so this remediation slice takes the next
number).

## Title

Vignette id scan robustness: one unreadable or malformed file in a vignette folder never turns an
id lookup into a server error.

## Objective

**Reproduction at `6d75495`** (REV-TRN-008, `TestClient` over `create_app()` with `VIGNETTE_DIR`
pointed at a temporary folder holding copies of `01-leo-isr-denial.yaml`,
`07-sda-custody-hunt.yaml`, a schema-broken `zz-broken-07.yaml` (id `broken-07`), and
`bad-yaml.yaml` (not valid YAML)):

| Request | Expected (FS-131) | As built |
|---|---|---|
| `POST /api/sessions` `nosuch` | 404 naming the id (criterion 6) | **500** — `yaml.parser.ParserError` escapes `load_vignette` |
| `POST /api/sessions` `broken-07` (file name ≠ id, sorts after `bad-yaml.yaml`) | 400 `invalid_vignette` with its problems | **500** — same cause |
| `POST /api/sessions` `leo-isr-denial` / `sda-custody-hunt` (found before the bad file) | 200 | 200 |
| `POST /api/sessions` `bad-yaml` (file name = id) | 400 "not valid YAML" | 400 (correct) |

**Cause.** `load_vignette` (`content/vignette.py`) first tries `<id>.yaml`. Otherwise it scans
`VIGNETTE_DIR/*.yaml` in sort order and calls `yaml.safe_load` on each file with **no** guard. The
external-root scan just below it catches `(yaml.YAMLError, OSError)`, and so does
`list_vignettes`; the built-in scan does not. So the first unparseable file reached before a match
raises out of the loader. `_vignette_load_errors` maps only `VignetteValidationError`,
`FileNotFoundError` and `ValueError`, so the error becomes a 500. Both scans also call
`data_inner["vignette"].get("id")` without checking that the `vignette` value is a mapping, so a
file whose `vignette:` is a list or a string raises `AttributeError` (a 500 in either root).

After this package, a file the scan cannot read, parse, or find a mapping `vignette` block in is
skipped, as `list_vignettes` already skips it. An id that matches no file is a `FileNotFoundError`
(404). A file found by its exact name `<id>.yaml` still goes through `IP-1310`'s gate unchanged, so
it is still refused 400 with "not valid YAML" or "missing 'vignette' key".

## Feature Reference

[FS-131](../../features/FS-131-load-time-vignette-validation.md) v1.1 — System Behaviour 5
("an id that names no vignette … is a rejection naming the id. It is not a server error"),
Acceptance Criterion 6, the Edge case on files that are not valid YAML, and the Outcomes ("Fail:
the load is refused"). This package does not touch criterion 10, which stays blocked on `BL-0233`.

## Requirements Covered

| ID | How |
|---|---|
| `FR-5310` | A valid vignette loads, and an invalid one is refused precisely, regardless of unrelated files in the same root. |
| `NFR-1600` | An unknown id or a broken neighbouring file gives a client error, never a crash. |

Both are in FS-131's Requirements Implemented; none added, none dropped. (`FR-5311`–`FR-5314`
are untouched.)

## Architecture Components

- **C5 Content & Data** (`content/vignette.py::load_vignette`, the declared-id resolution step):
  the only behaviour change.
- **C2 Session Layer** / **C4 Operator Console**: unchanged — `InProcessSession.load_vignette`
  passes the error through, and `_vignette_load_errors` already maps `FileNotFoundError` to 404.

The engine is untouched; the import guard is unaffected.

## Interfaces

- **INT-0011** (load): an id that matches no readable file now always raises
  `FileNotFoundError`; nothing else about its outcomes changes.
- **INT-0001** (HTTP): `POST /api/sessions` returns the specified client error, not a 500, for the
  two failing cases in the table. Response shapes unchanged.

### Design Decisions

1. **One private helper for "the declared id of this file, or none".** For example
   `_declared_vignette_id(path) -> Optional[str]`. It reads and safe-loads the file, and returns
   the `vignette` block's `id`. It returns `None` when the file cannot be read (`OSError`), does
   not parse (`yaml.YAMLError`), is not a mapping, has no `vignette` key, has a `vignette` value
   that is not a mapping, or has no `id`. Both the built-in scan and the external-root scan use it,
   so the two roots cannot drift again. The candidate-by-filename branches (`<id>.yaml`) are
   unchanged.
2. **Skip, don't refuse.** A file the scan skips is not the file asked for: it either declares a
   different id or no readable id at all. Raising for it would make one bad file block every
   other vignette (the defect). Its own problems are still reported precisely when it is loaded by
   its exact name, through `IP-1310`'s gate.
3. **`list_vignettes` is not changed.** It already skips the same files (it checks the mapping
   shape and catches `YAMLError`/`OSError`). The helper may be reused there only if that is a pure
   refactor; if it is reused, the existing picker tests must still pass unchanged.
4. **Determinism and safety.** Content-layer only; no engine, RNG or clock involvement. Parsing
   stays `yaml.safe_load` (NFR-2200 / ADR-0007). The id/path guard (`_validate_id`,
   `_resolve_within_root`) runs first, as now (NFR-3700).

## Files to Create

- `spacesim/tests/test_vignette_id_scan.py`.

## Files to Modify

Checked against the tree at `6d75495`:

- `spacesim/content/vignette.py`:
  - `load_vignette` (starts line 245): the built-in declared-id scan (lines 263–271, unguarded
    `yaml.safe_load` at 266, `.get("id")` at 269) and the external-root declared-id scan (lines
    282–291, `.get("id")` at 289) both go through the new helper.
  - New private helper next to `_resolve_within_root` (line 46) or just above `load_vignette`.

No other production file changes.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, ROADMAP) before editing.
2. Write the tests below and see tests 1–3 fail first; 4–6 should pass on arrival.
3. Implement Design Decisions 1–2.
4. Run the full suite plus `test_determinism.py` and `test_import_guard.py`. Fix only defects this
   package introduced.
5. Do the documentation updates, then mark `COMPLETE`.

## Tests to Add

`spacesim/tests/test_vignette_id_scan.py`. Fixtures: `monkeypatch.setattr(vignette_module,
"VIGNETTE_DIR", tmp_path)` (the pattern `test_defensive_audit_2026.py` uses), with
`external_dirs=[]` passed or `_configured_external_dirs` patched to return `[]`, holding copies of
two shipped vignettes whose file name differs from their id (for example
`07-sda-custody-hunt.yaml` → `sda-custody-hunt`).

1. **Unknown id with a bad file present → not found.** Add `aaa-bad.yaml` containing invalid YAML
   (it sorts first). `load_vignette("nosuch")` raises `FileNotFoundError`. Over HTTP
   (`TestClient(create_app(), raise_server_exceptions=False)`): 404 naming the id.
2. **Valid vignette after a bad file loads.** Same folder: `load_vignette("sda-custody-hunt")`
   returns the vignette; HTTP `POST /api/sessions` → 200 with a session id.
3. **Non-mapping `vignette:` is skipped in both roots.** A file `aaa-list.yaml` with
   `vignette: [1, 2]` in the built-in root, and the same in an external root passed as
   `external_dirs=[ext]`: an unknown id → `FileNotFoundError`; a valid id in either root still
   loads.
4. **Exact-name bad file still refused precisely.** `bad-yaml.yaml` (invalid YAML) loaded as
   `bad-yaml` → `VignetteValidationError` whose problem `where` is `bad-yaml.yaml` and whose
   reason starts `not valid YAML`; HTTP 400 `invalid_vignette`.
5. **Schema-broken file found by declared id is still refused.** A schema-broken copy with
   `id: broken-x` in `zz-broken.yaml`, plus the bad file: `load_vignette("broken-x")` raises
   `VignetteValidationError` (not a YAML error); HTTP 400.
6. **No regression on the shipped library.** Every `list_vignettes()` id loads (the existing
   `test_vignette_library.py`/`test_vignette_load_validation.py` cover this; this test only asserts
   the real `VIGNETTE_DIR` resolves every listed id).

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md`: the `FR-5310` row's Test and
  Implementation Package cells gain `test_vignette_id_scan.py` / `IP-1311`.
- `docs/features/FS-131-load-time-vignette-validation.md`: `Referenced By` only.
- MBP row and counts, `packages/INDEX.md`, ROADMAP row, this header.
- `CLAUDE.md` code map: no change needed (the `content/vignette.py` bullet does not describe the
  scan).
- **Manual impact:** none required. `06`/`09` §10 already say an unknown id reads "not found"; this
  package makes that true in every folder state. REV-TRN-008 deliberately left the 500 out of the
  manual.

## Definition of Done

- All Tests to Add exist and pass; tests 1–3 were seen failing first.
- Full suite green, with no previously passing test now failing; `test_determinism.py` and
  `test_import_guard.py` green.
- Each case in the Objective's reproduction table returns the FS-131 expected status.
- `git diff --stat` touches only `content/vignette.py`, the new test file, and the docs.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. Both declared-id scans in `load_vignette` go through one helper; neither calls `yaml.safe_load`
   or `.get("id")` unguarded.
2. With an unparseable file sorting first in `VIGNETTE_DIR`, an unknown id gives 404 and a valid
   later-sorting id gives 200 (reproduce independently, not only via the package's tests).
3. A non-mapping `vignette:` value is skipped in the built-in and the external root.
4. A broken file loaded by its exact name is still refused 400 with the `IP-1310` message.
5. `list_vignettes` output is unchanged for the shipped library.
6. Full suite and both permanent gates (`test_determinism.py`, `test_import_guard.py`) green.

## Dependencies

`IP-1310` and `IP-1180` (both `VERIFIED`). No package depends on `IP-1311`. No other open package
edits `content/vignette.py` (`IP-1160` edits `engine/orders.py` only).

## Risks

- **Masking a genuinely wanted file.** A user whose vignette has a YAML error, and whose file name
  differs from its id, now gets "not found" instead of a 500. That is the correct client error,
  but the reason (the YAML error) is not shown. Loading by the exact file name still shows it, and
  the manual's "missing from the picker" guidance (`09` §10, run #157) covers the symptom. Whether
  the scan should also report "a file in this folder could not be read" is out of scope; file it
  via `00-intake` if wanted.
- **Sort-order coupling in tests.** Test fixtures should name files so the bad file sorts before
  the target (for example an `aaa-` prefix), or the test passes without exercising the defect.

## Rollback Considerations

Revert the commit. No data, format or persisted-state change.
