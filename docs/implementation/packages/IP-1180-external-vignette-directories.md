# IP-1180 — External Vignette Directories & Safe Scenario Save Target

> **Package ID:** IP-1180
> **Version:** 1.0
> **Status:** ⚪ NOT STARTED *(forward design — not authorized for coding, MSTR-006 §3)*
> **Dependencies:** [FS-118](../../features/FS-118-external-vignette-directories.md) v1.0
> (`FR-5410`/`FR-5420`/`NFR-3700`), [FS-117](../../features/FS-117-vignette-creator.md)/
> [IP-1173](IP-1173-vignette-creator-draft-session.md) (`save_vignette` — the existing, `VERIFIED`
> write path this package modifies, not reimplements), `FR-5310` (load-time vignette validation,
> unchanged and reused unmodified)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0082` (external validation report,
> 26 Sep 2026, item B16), `BL-0094` (this Feature's four Open Questions — three resolved as design
> decisions below, one confirmed via direct code reading)
> **Produces:** an external-vignette-directory load path and a user-directory-scoped
> `save_vignette` write target, satisfying `FR-5410`/`FR-5420`/`NFR-3700` in full
> **Feature Reference:** [FS-118 — External Vignette Directories & Safe Scenario Save Target](../../features/FS-118-external-vignette-directories.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/content/vignette_export.py`](../../../spacesim/content/vignette_export.py),
> [`spacesim/config.py`](../../../spacesim/config.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Confirmed directly against the live code at authoring time: `save_vignette`
in `spacesim/content/vignette_export.py` (lines 57-79) is in fact the single code path `FR-5420`
must retarget — it is called by exactly one caller, `InProcessSession.save_vignette`
(`spacesim/session/inprocess.py` lines 120-128), itself called by exactly one route,
`POST /api/sessions/{sid}/save_vignette` (`spacesim/ui_web/server.py` lines 316-323), itself called
by exactly one client, `creator.js`'s "Save as Vignette" action. This resolves FS-118's Open
Question 1 in full: there is one save mechanism, not two to reconcile — `IP-1173`'s `save_vignette`
is the thing this package changes the write-target resolution of, in place.*

## Package ID

IP-1180

## Title

External Vignette Directories & Safe Scenario Save Target

## Objective

Extend the vignette catalog (`list_vignettes`/`load_vignette` in `content/vignette.py`) to also
enumerate zero or more externally-configured directories alongside the built-in `VIGNETTE_DIR`,
tagging each catalog entry with its origin; and retarget `save_vignette`
(`content/vignette_export.py`) from `VIGNETTE_DIR` to a separately configured user-save directory,
applying the existing path-traversal guard — generalized into a reusable helper — to every content
root this package introduces.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-118 — External Vignette Directories & Safe Scenario Save Target](../../features/FS-118-external-vignette-directories.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-5410 | Load vignettes from configured external directories | `list_vignettes()`/`load_vignette()` extended to enumerate/search a new, configured list of external directories in addition to `VIGNETTE_DIR`, tagging each catalog entry's origin (`"built-in"` or the external directory's basename) and resolving id collisions deterministically (Design Decision 3 below). |
| FR-5420 | `save_vignette` writes only to a configured user directory, no path traversal | `content/vignette_export.py::save_vignette` retargeted from `VIGNETTE_DIR` to a newly configured user-save directory, read from `spacesim.config.yaml`/`SPACESIM_CONFIG`; a save request with no user-save directory configured is rejected (Design Decision 2 below). |
| NFR-3700 | Path-traversal safety generalized to external content roots | The existing traversal guard (`content/vignette.py` lines 139-153: charset + `..`/separator/leading-`~`/`.` rejection, then resolved-path-inside-root re-check) is extracted into a reusable helper and applied identically against every configured external directory and the configured user-save directory, not only `VIGNETTE_DIR`. |

## Architecture Components

- **C5 Content & Data** (`content/vignette.py`, `content/vignette_export.py`) — owns the catalog
  enumeration, the load path, the save path, and the (generalized) traversal guard. No new
  subsystem; this package extends C5's existing responsibility to a plural set of content roots.
- **C2 Session / Application Layer** (`session/inprocess.py`) — no behavioral change; its
  `list_vignettes()`/`load_vignette()`/`save_vignette()` pass-throughs are unmodified (they already
  delegate to C5's functions by name, so the new capability is transparent to this layer).
- **Configuration surface** (`spacesim/config.py`) — gains a new, additive configuration section
  (external vignette directories; user-save directory), read once at startup, extending the
  existing `ServerConfig`/`load_server_config()` pattern rather than a new file format.
- **C4 Operator Console** (`ui_web/`) — no route shape change; `GET /api/vignettes` returns the same
  `list[dict]` shape with one new key per entry (`origin`), additive and backward-compatible for
  any existing client that ignores unknown keys.

## Interfaces

`INT-0011` (Session Layer → Content & Data, vignette/template load) — this package's load-path
extension operates entirely through the existing interface (same call shape, `list_vignettes()`/
`load_vignette(id)`); no ICD edit needed, consistent with FS-118's own Interfaces Used note that
this Feature's use is a closer fit than sibling Must-tier items that do stretch `INT-0011`.
`INT-0012` (Session Layer → Content & Data / Filesystem, save round trip) — `FR-5420`'s retargeted
write operates through this existing interface; the interface's C5-owns-on-disk-format /
C11-owns-physical-write split (`ADR-0022`) is unchanged — only *which* directory C11 writes to
changes.

## Design Decisions (resolving FS-118's Open Questions 1-4)

Per this skill's own workflow ("an explicit `07-implementation-planning` design decision" is the
named resolution path FS-118 itself points to for Open Questions 2-4), this package commits to:

1. **Open Question 1 — resolved by direct code reading, not a decision.** `save_vignette` in
   `content/vignette_export.py` is the one and only code path `FR-5420` retargets (see the header
   note above for the full call-chain citation). Nothing to reconcile.
2. **Open Question 2 — a configured external directory that does not exist or is not readable is
   silently skipped at catalog-build time, logged at `WARNING`, and the catalog build continues
   with the remaining roots.** This mirrors the existing tolerate-one-bad-entry posture
   `list_vignettes()` already applies to a malformed YAML file (`content/vignette.py` lines
   115-126, "Audit Jun 2026 §B/E — tolerate one malformed file rather than 500ing the whole listing
   endpoint") — a missing/unreadable directory is the same class of problem (one bad root should
   not take down the whole catalog) and gets the same answer. **Recommendation to
   `04-requirements-engineering`:** consider baselining this behavior explicitly in a future
   `FR-5410` amendment so it is not left as an implementation-planning-level decision indefinitely
   (routed as a finding, not acted on here).
3. **Open Question 3 — a save request with no user-save directory configured is rejected with a
   `ValueError` naming the missing configuration explicitly** (e.g. "no user-save directory
   configured — set `content.user_save_dir` in spacesim.config.yaml"), consistent with the existing
   "invalid input fails loudly" posture this package's own traversal-rejection path already follows
   and with `FR-5310`'s analogous rule for the load path. This is a precondition failure, not a
   silent no-op or a fallback to `VIGNETTE_DIR` (a fallback would defeat `FR-5420`'s entire purpose).
4. **Open Question 4 — a vignette id collision between the built-in library and a configured
   external directory (or between two external directories) resolves built-in-first, then by
   configured-directory order; the losing entry is skipped from the catalog, not silently merged,
   and a `WARNING`-level log line discloses which file was shadowed by which.** Rationale: the
   built-in library is the one root every deployment shares and already trusts implicitly (it ships
   with the source tree and is covered by the existing test suite); treating it as authoritative on
   a same-id collision is the least-surprising rule and avoids a user's external directory silently
   overriding a canonical numbered/training vignette by accidental id reuse. **Disclosure is
   log-level only in this package** — a facilitator-visible UI affordance (e.g. a "3 external
   vignettes hidden due to id collision" banner) is not required by `FR-5410`'s own Acceptance
   Criteria and is named here as a Risk (below) rather than invented as in-scope work.

## Files to Create

None. This package extends three existing modules; no new file is required.

## Files to Modify

- `spacesim/config.py` — add a `ContentConfig` dataclass (`external_vignette_dirs: tuple[str, ...]
  = ()`, `user_save_dir: Optional[str] = None`) and a `load_content_config(path=None) ->
  ContentConfig` function, mirroring `ServerConfig`/`load_server_config()`'s existing shape exactly
  (same optional-file-falls-back-to-defaults pattern, same `SPACESIM_CONFIG` override). Reads a new
  top-level `content:` section from `spacesim.config.yaml`.
- `spacesim/content/vignette.py` —
  - Extract the existing id-validation block (lines 139-148: charset/traversal/leading-character
    rejection) into a reusable module-level helper, e.g. `_validate_id(path_or_id: str) -> None`
    (raises `ValueError`), called first by both `load_vignette()` and (via the export module) the
    save path.
  - Extract the existing resolved-path-inside-root re-check (lines 150-153) into a reusable helper,
    e.g. `_resolve_within_root(root: Path, filename: str) -> Path` (raises `ValueError` on escape),
    parameterized by root instead of hard-coded to `VIGNETTE_DIR`.
  - `list_vignettes()` gains an optional `external_dirs: Optional[Sequence[Path]] = None` parameter
    (default: read from `load_content_config().external_vignette_dirs`); enumerates each configured
    directory's `*.yaml` files the same tolerant way it already enumerates `VIGNETTE_DIR` (skip a
    malformed file, per the existing `except (yaml.YAMLError, OSError): continue`), tagging each
    entry `{"id", "title", "path", "origin"}` where `origin` is `"built-in"` for `VIGNETTE_DIR` or
    the external directory's own basename. Implements Design Decisions 2 and 4 above (unreadable
    directory skipped + logged; id collision resolved built-in-first, external order thereafter,
    loser skipped + logged).
  - `load_vignette()` extended: after the existing built-in-directory search (by filename, then by
    declared id — unchanged, still checked first per Design Decision 4's built-in-wins rule),
    fall through to search each configured external directory the same two ways, applying the same
    `_validate_id`/`_resolve_within_root` guard against each external root in turn.
- `spacesim/content/vignette_export.py` — `save_vignette()`'s write-target resolution changed from
  `VIGNETTE_DIR` to `load_content_config().user_save_dir` (raising the `ValueError` from Design
  Decision 3 when unset), reusing `vignette.py`'s new `_validate_id`/`_resolve_within_root` helpers
  in place of the module's own local `_ID_RE`/inline-resolve logic (removing the now-duplicated
  charset check).
- `spacesim.config.yaml` — add a commented-out example `content:` section (`external_vignette_dirs:
  []`, `user_save_dir: null`), matching this file's existing documentation-by-example convention for
  the `server:` section.

## Implementation Tasks

1. Write a failing test asserting `load_content_config()` returns empty defaults when no config
   file is present (mirroring `test_config.py::test_load_server_config` for the missing-file case),
   before writing `ContentConfig`/`load_content_config()`.
2. Add `ContentConfig`/`load_content_config()` to `spacesim/config.py`.
3. Write a failing test asserting the existing traversal-token parametrization (path separator,
   `..`, absolute path, disallowed character) is rejected identically whether checked directly or
   through the extracted `_validate_id`/`_resolve_within_root` helpers, before extracting them —
   a pure refactor that must not change `load_vignette()`'s existing observable behavior against
   `VIGNETTE_DIR` (regression-only at this step).
4. Extract `_validate_id`/`_resolve_within_root` from `load_vignette()`'s existing body; re-run the
   full existing vignette-loading test suite to confirm zero behavior change.
5. Write a failing test with a fixture external directory containing one valid vignette file,
   asserting it appears in `list_vignettes()`'s output labeled with the correct `origin`, before
   extending `list_vignettes()` to accept and enumerate `external_dirs`.
6. Write a failing test asserting an unreadable/nonexistent configured external directory is
   skipped (catalog build still succeeds, built-in entries unaffected), before implementing Design
   Decision 2.
7. Write a failing test asserting an id collision between a built-in vignette and an external-
   directory vignette of the same id resolves to the built-in entry (external entry absent from the
   catalog), before implementing Design Decision 4.
8. Extend `load_vignette()` to fall through to configured external directories after exhausting the
   built-in search, applying the same guard per external root; write a failing test loading a
   vignette that exists only in a fixture external directory, asserting it builds successfully via
   `build_world()`.
9. Write a failing test asserting `save_vignette()` raises `ValueError` when no `user_save_dir` is
   configured (Design Decision 3), before implementing the rejection.
10. Write a failing test asserting `save_vignette()`, given a configured `user_save_dir`, writes the
    file there (not to `VIGNETTE_DIR`) and that a traversal-token vignette id is rejected before any
    filesystem access — reusing the same parametrization as the load-path traversal tests (`FS-118`
    Acceptance Criterion 3) — before retargeting `save_vignette()`'s write path.
11. Re-run the full existing suite; confirm the `IP-1173`-authored Creator draft-save tests
    (`test_vignette_creator_session.py`, `test_web.py`'s save-as-vignette flow) still pass once a
    `user_save_dir` is configured in the test fixture (they will need a `tmp_path`-based
    `user_save_dir` fixture added, since `save_vignette()` no longer defaults to `VIGNETTE_DIR`).

## Tests to Add

- `spacesim/tests/test_config.py` — new tests for `ContentConfig`/`load_content_config()`: missing
  file → defaults; a file with a `content:` section → both fields parsed; `SPACESIM_CONFIG`
  override respected (mirroring the existing `ServerConfig` test shapes exactly).
- `spacesim/tests/test_content.py` — new tests: external-directory enumeration + origin tagging;
  empty-configuration baseline-unchanged regression; unreadable/nonexistent external directory
  skipped, catalog build still succeeds; id collision resolves built-in-first, loser skipped;
  `load_vignette()` finds a vignette that exists only in a configured external directory; the full
  traversal-token parametrization (path separator, `..`, absolute path, disallowed character)
  re-run against (a) `VIGNETTE_DIR` (regression), (b) a configured external directory, (c) the
  configured user-save directory, asserting identical rejection with no filesystem mutation in each
  case — this is FS-118's own Acceptance Criterion 3, verbatim.
- `spacesim/tests/test_content.py` (or a new `test_vignette_export.py` if the existing file lacks
  export-path coverage) — `save_vignette()` rejects when no `user_save_dir` is configured; writes to
  the configured `user_save_dir` (not `VIGNETTE_DIR`) when one is configured.
- Existing `spacesim/tests/test_vignette_creator_session.py`/`test_web.py` save-as-vignette tests —
  updated (not rewritten) to configure a `tmp_path` `user_save_dir` via a fixture/monkeypatch, since
  `save_vignette()` no longer has an implicit default target.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
are unaffected in principle (no engine-layer file touched, no wall-clock read or global RNG use
introduced) but must be re-run green per this repository's mandatory workflow.

## Documentation Updates

- `CLAUDE.md` Code Map — `spacesim/config.py`'s entry gains the `ContentConfig`/
  `load_content_config()` addition; `content/vignette.py`'s entry gains the external-directory
  enumeration + generalized traversal-guard note; `content/vignette_export.py`'s entry gains the
  user-save-directory retargeting note.
- `spacesim.config.yaml` — the new `content:` section documented by example (see Files to Modify).
- `docs/design/05-interface-control-document.md` — `INT-0011`/`INT-0012` entries' prose updated to
  note the now-plural set of load/save roots (no interface ID/shape change, per this package's own
  Interfaces section above — a citation update, not an ICD edit).
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-5410`/`FR-5420`/`NFR-3700` rows'
  `Implementation Package` cell updated from `UNASSIGNED` to `IP-1180`; `Test` cell updated once the
  named test files exist.
- `docs/features/FS-118-external-vignette-directories.md` — `Referenced By` metadata gains this
  package's link (metadata cross-link only, per this skill's own rule — the spec's content is not
  edited); its four Open Questions are not struck out by this package (that edit belongs to
  `06-feature-specification`, not to a planning package) but this package's Design Decisions section
  gives `06` everything it needs to close them in a future spec revision.
- `docs/pipeline/backlog.md` — `BL-0094` (this Feature's four Open Questions) updated: 1 of 4
  resolved by code reading (not a design decision), 3 of 4 resolved by this package's Design
  Decisions section — recommend flipping to `DONE` at the next `00-pipeline-manager` harvest, with
  the one sub-item (facilitator-visible collision disclosure, see Risks) optionally re-filed as a
  new, separate Low finding rather than reopening `BL-0094` itself.

## Definition of Done

- [ ] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3) — not yet sought or granted as of this writing.
- [ ] `list_vignettes()` enumerates configured external directories alongside `VIGNETTE_DIR`,
  tagging each entry's origin; empty configuration reproduces baseline behavior byte-for-byte.
- [ ] `load_vignette()` finds a vignette that exists only in a configured external directory.
- [ ] An unreadable/nonexistent configured external directory is skipped without failing the whole
  catalog build.
- [ ] An id collision between the built-in library and a configured external directory resolves to
  the built-in entry, with the external entry absent from the catalog and the shadow logged.
- [ ] `save_vignette()` writes only to a configured `user_save_dir`, never to `VIGNETTE_DIR`, and
  raises a specific, distinguishable error when no `user_save_dir` is configured.
- [ ] The traversal guard (charset + `..`/separator/leading-character rejection, then
  resolved-path-inside-root re-check) rejects an offending identifier identically against
  `VIGNETTE_DIR`, every configured external directory, and the configured user-save directory, with
  no filesystem access on rejection in every case.
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `test_config.py`'s new `ContentConfig`/`load_content_config()` tests exist and are green.
- [ ] `test_content.py`'s (and/or the new export-test file's) new external-directory/collision/
  save-retargeting tests exist and are green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Full existing suite re-run with zero regressions, in particular `IP-1173`'s existing
  save-as-vignette tests (now exercised against a configured `user_save_dir` fixture rather than an
  implicit `VIGNETTE_DIR` default).
- [ ] Independently confirm, by reading the shipped code directly, that `_validate_id`/
  `_resolve_within_root` (or equivalently named helpers) are actually shared between the load path
  and the save path — not two independently-maintained copies of the same guard logic.
- [ ] Independently confirm the built-in-wins collision rule and the unreadable-directory-skip
  behavior against a hand-constructed fixture, not merely by re-reading the tests this package
  itself wrote.

## Dependencies

- **Upstream:** [FS-118](../../features/FS-118-external-vignette-directories.md) v1.0 (approved,
  `✅ Ready for implementation planning`), the existing traversal guard in `content/vignette.py`
  (baseline code, unmodified in spirit — only extracted/generalized), [IP-1173](IP-1173-vignette-creator-draft-session.md)
  (`VERIFIED`) — this package modifies `save_vignette()` in place; it is not a build dependency in
  the sense of needing new code from `IP-1173`, but every one of `IP-1173`'s existing tests exercising
  `save_vignette()` must be re-validated against the new write-target resolution (see
  Implementation Task 11).
- **Downstream:** [FS-120](../../features/FS-120-save-as-scenario.md) (`FR-5510`, save-as-scenario)
  depends on this package's `user_save_dir` configuration surface and traversal-safety guarantee as
  its own write target — the package planned for `FS-120` must build on this package's configuration
  surface, not invent a second one.
- **Build-sequencing:** Independent of the other five Must-tier packages queued this increment
  (different files, no shared seam with `FS-106`/`FS-119`/`FS-121`/`FS-103`) except for `FS-120`,
  which should be sequenced after this package lands.

## Risks

- **Coordination risk with `IP-1173`'s existing tests (see Files to Modify / Implementation Task
  11).** `save_vignette()` losing its implicit `VIGNETTE_DIR` default is a breaking change to any
  test or caller that doesn't configure `user_save_dir` — this package's own tests must update those
  call sites, not merely add new ones alongside them, or the existing suite will regress.
- **Facilitator-visible collision disclosure is log-level only (Design Decision 4).** `FR-5410`'s
  Postcondition says a collision must be "resolved deterministically and disclosed" — this package
  satisfies "resolved deterministically" fully and "disclosed" only at the server log level, not in
  the operator-facing UI. If a facilitator-visible affordance is later judged necessary, that is a
  new, separate finding for `00-intake`/`06-feature-specification`, not a defect in this package as
  scoped (Acceptance Criterion 1 does not require a UI-level disclosure).
  **Recommendation:** file a new Low backlog finding for this at the next pipeline-manager harvest
  rather than silently closing the door on it.
- **Ambiguity risk resolved, not eliminated.** Design Decisions 2-4 are this package's own
  commitments, consistent with FS-118's own text but not literally stated by `FR-5410`/`FR-5420`.
  `06-feature-specification`/`04-requirements-engineering` may wish to formalize them in the
  requirements baseline itself in a future pass (see the Recommendation under Design Decision 2) —
  this package does not treat that as blocking its own execution.

## Rollback Considerations

Both the catalog-enumeration extension and the save-path retargeting are additive/parameterized
changes to existing functions, not new subsystems — reverting `list_vignettes()`/`load_vignette()`
to search only `VIGNETTE_DIR` and reverting `save_vignette()` to its hard-coded `VIGNETTE_DIR`
target fully removes this package's capability with no effect on any vignette file already on disk
(built-in or externally authored) and no data-migration concern: an externally-loaded vignette file
is byte-identical in format to a built-in one, and a scenario already saved to a `user_save_dir`
remains a perfectly ordinary hand-editable/re-loadable YAML file after rollback (it simply would no
longer be found unless copied back into `VIGNETTE_DIR`).
