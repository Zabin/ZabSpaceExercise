# IP-1092 — Retired-Documents Check (`NFR-3810`, FS-135 Check 2)

> **Package ID:** IP-1092
> **Version:** 1.0
> **Status:** READY (authored 2026-10-31 by `07-implementation-planning`; every dependency `VERIFIED`)
> **Authorization (MSTR-006 §3):** **given.** The project owner's go-ahead of 2026-10-31, in the planning session that commissioned this package ("build before release `NFR-3810`"), covers this package and no other.
> **Dependencies:** [FS-135](../../features/FS-135-documentation-integrity-checks.md) v1.1, [IP-1350](IP-1350-documentation-integrity-checks.md) (`VERIFIED`, `VR-1350`; supplies the live-set walker, link reader and allow-list gate)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [01-technical-work-breakdown.md](../01-technical-work-breakdown.md)
> **Produces:** check 2 in `spacesim/tests/test_doc_integrity.py`, the committed empty `doc_integrity_allow_retired.txt`, and the `Retired documents` section convention.
> **Feature Reference:** [FS-135](../../features/FS-135-documentation-integrity-checks.md) Check 2
> **Supersedes:** none
> **Related Topics:** [`spacesim/tests/test_doc_integrity.py`](../../../spacesim/tests/test_doc_integrity.py)

[Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID
IP-1092

## Title
Retired documents are deleted, declared in a `Retired documents` section of an `INDEX.md`, and named by no live document.

## Objective
Add check 2 to the documentation-integrity suite exactly as FS-135 v1.1 specifies: failure modes (a) declared path still present, (b) live reference outside the declaring section (path as string, ID as whole token, fenced code and code spans scanned), (c) incomplete/unparseable row (no path, no date, bad date, no successor, successor nonexistent); unreadable section table fails naming the index; a trailing-`/` row retires a folder; modes (a) and (c) never allow-listable, (b) gated by an empty shrink-only allow-list.

## Requirements Covered
`NFR-3810` (primary); reuses `NFR-3800`/`NFR-3820` machinery (unchanged), `NFR-3400`.

## Architecture Components
Test-only (`spacesim/tests/`). Reuses `live_md_files`, `live_text`, `_prose_lines` precedent, `read_allow`/`_gate`. The only new scanner differs from check 1 by design: it does not strip fences or code spans.

## Interfaces
New pure functions in `test_doc_integrity.py` (same style as `broken_links`): `retired_declarations(root)` -> rows with index, line, path, id, date, successor, plus malformed rows; `retired_findings(root)` -> `(mode, where, detail)` set. Allow-list key format follows the existing files (one line per finding key). No product code, no route.

## Files to Create/Modify
Modify `spacesim/tests/test_doc_integrity.py` (verified; helpers at lines 32-260). Create `spacesim/tests/doc_integrity_allow_retired.txt` (empty, with the same header-comment convention as the sibling `doc_integrity_allow_*.txt`). Modify (docs): `docs/INDEX.md` (add the section, see decision below); `ROADMAP.md`.

## Implementation Tasks
1. Write synthetic-tree tests first (below), observe failing. 2. Implement the section reader: second-level heading exactly `Retired documents`, table columns former path, former ID (may be blank), date (ISO), successor (`none` valid); never links. 3. Implement modes (a), (b), (c); exclude only the declaring section's lines from the scan, scan the rest of the same `INDEX.md`; path match on whole path boundaries; ID as whole token. 4. Wire a real-tree test using `_gate` and the new allow-list. 5. Initial content (below).

**Initial content (checked now).** `git log --diff-filter=D -- '*.md'` over the available history (559 commits, shallow clone) lists no deleted Markdown document, so there is nothing currently referenced to declare: the section is added to `docs/INDEX.md` with a single row-less body line "none", and the check must treat a section whose only body is `none` as zero rows (not "unreadable table"); this case is a test. Re-run the deleted-file scan at build time (history may be deeper on the build seat) and declare only retired paths a live document still references.

**Root-level retired document (FS-135 OQ6; owner choice flagged).** Simplest consistent option, applied unless the owner objects: a retired ROOT-level document (`ROADMAP.md`, `memory.md`, `CLAUDE.md`-class files) is declared in `docs/INDEX.md`'s `Retired documents` section, the index that already routes the root documents, with the path written as the repo-relative root path (`ROADMAP.md`). The check already reads every `INDEX.md`, so no code special case is needed; a test pins that a root path declared in `docs/INDEX.md` is enforced. A real `INDEX.md` at the repo root is not created (it would trip check 3 against root files). Recorded in the package, to be echoed by `04`/`06` in `NFR-3810` Notes/FS-135 OQ6.

## Tests to Add
`@pytest.mark.verifies("NFR-3810")` on all (synthetic trees via the existing `_w` helper, written before the code): (a) declared path present -> reported with index, row, path; absent -> clean. (b) reference as link, in backticks, in plain text, inside a fenced block, in a sibling `INDEX.md` body each reported with file, line, entry, declaring index; declaring section itself exempt; frozen-history folders exempt; ID `FR-1210` does not match `FR-12100`; path prefix matched on whole-boundary only (`docs/a.md` vs `docs/a.md.bak`, `docs/old/` folder row covers beneath). (c) missing date, bad date, missing successor, missing path, successor nonexistent each reported; `none` valid; table with no header or wrong column count fails naming the index; `none` body is zero rows. Root-path row in `docs/INDEX.md` enforced. A tree with no section passes. Allow-list: (b) allow-listable and shrink-only (stale entry fails); (a)/(c) ignore the allow-list. Real-tree test green with empty allow-list. Fail-first demonstrated by the synthetic cases before the implementation. `test_test_origins.py` and the origin guard accept the new tags; `--origin-report=rtm` regenerated if `NFR-3810`'s Test column changes.

## Documentation Updates
**Manual impact:** none - developer/process check only; no operator-visible label, route, message or procedure (operators never see `test_doc_integrity.py`). Process text for the retiring stages (`.claude/skills/README.md` and the retiring skills) is owner-authorized separately and is a hand-off to `04`/`06` and the owner, not written here. Also update `docs/INDEX.md` (new section), the Master Build Plan, `packages/INDEX.md`, `ROADMAP.md`. Do not edit FS-135 or `NFR-3810` text.

## Definition of Done
Check 2 implemented per FS-135 v1.1 with all tests above green and observed failing first; empty `doc_integrity_allow_retired.txt` committed; full suite and both permanent gates green; `test_doc_integrity.py`/`test_test_origins.py` green; documentation created/updated per Manual impact (none, reasoned), and §15.1/§15.2 rows in sync (no row affected).

## Verification Checklist
- [ ] Modes (a), (b), (c) each have a failing-first synthetic test.
- [ ] Check 2 does not strip fences/code spans; check 1 behavior unchanged (diff of existing tests nil).
- [ ] Allow-list file exists, empty, shrink-only gate applied to (b) only.
- [ ] `docs/INDEX.md` carries the section and passes check 3.
- [ ] Root-level declaration choice recorded and tested.
- [ ] Determinism and import-guard gates pass; full suite green; documentation in sync (Manual impact `none`, reasoned).

## Risks
False positives from legitimate historical mentions in live docs (mitigated: nothing is declared now). Declaring a path that live docs reference would fail the suite at once - intended. The root-level convention may need the owner's confirmation (flagged).

## Rollback Considerations
Revert the commit; test-only plus one docs section; no product behavior depends on it.
