# FS-135 — Documentation Integrity Checks

> **Document ID:** FS-135
> **Version:** 1.1 (2026-10-31 — check 2 aligned to `NFR-3810` as made checkable in `CHG-049`: the register file is replaced by a `Retired documents` section in the owning folder's `INDEX.md`; owner decisions of 2026-10-31 applied; Open Questions 1, 4 and 5 closed or realigned.) Prior: 1.0 (2026-10-23, pipeline run #216)
> **Status:** 🟢 Ready for new work — `NFR-3800`/`NFR-3820`/`NFR-3830` built (`IP-1350`, `VERIFIED`); the `NFR-3810` check (check 2) is specified here and unbuilt, owner decision 2026-10-31: build before release.
> **Approved input:** the Feature Catalog entry `FEAT-12300` (Epic `EP-12000`) in
> [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md),
> following the FS-130–FS-134 convention. Owner direction it elaborates: `BL-0297` (2026-10-20: "a
> holistic documentation-integrity test scheme, part of release verification", replacing the
> reverted tier-level cleanup rule), in [`docs/pipeline/backlog.md`](../pipeline/backlog.md).
> **Referenced By:** [feature index](feature-index.md); `FEAT-12300`; [IP-1350](../implementation/packages/IP-1350-documentation-integrity-checks.md) (planned 2026-10-23; checks 1, 3, 4)
> **Related Topics:** [FS-133](FS-133-test-origin-traceability.md) (the origin check shares this
> runner, FS-133 OQ2; the retirement question, FS-133 OQ1); `spacesim/tests/test_training_sources.py`
> (the existing `Sources:` footer check, `NFR-3400`, the model for this suite);
> [GDS-06](../architecture/06-non-functional-requirements.md) NFR-18; `BL-0292` (retiring
> `docs/build-spec/` and most of `docs/design/`)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. Its subject is the
documentation tree, not the simulator.*

## Feature ID

FS-135

## Title

Documentation Integrity Checks

## Purpose

Keep the live documentation tree honest as legacy content retires: links resolve, nothing live
cites a retired document, indexes match their folders, and status ledgers agree — per
`FEAT-12300`'s Purpose. The owner chose an automated check over a written cleanup rule (`BL-0297`):
a rule with no check behind it decays, a test does not.

## Scope

In scope: four automated checks over the live documentation (`NFR-3800`–`NFR-3830`); which
documents are live and which are frozen history; the `Retired documents` declaration the second check
reads; the shrink-only allow-list that lets the suite go green before the existing defects are all
fixed; and how the checks run (with the full suite).

Out of scope: fixing the defects the checks find (the cleanup is owned by each document's stage;
the checks only find and track them); prose accuracy and doc coherence that a test cannot judge
(`09-training-manual-review`, `10`, `11` keep those); the training `Sources:` footer check
(`NFR-3400`, already built, FEAT-11100 — kept alongside, not re-specified); the test-origin
resolution check (`NFR-3840`, FS-133), which may share this runner; retiring any document
(`BL-0292`).

## Requirements Implemented

NFR-3800 (relative links in live documents resolve), NFR-3810 (a retired document is deleted, declared, and no live document names it), NFR-3820 (each index agrees with its folder), NFR-3830 (status ledgers agree) — per
`FEAT-12300`'s `Included Requirements`.

## Design Decisions

1. **Live versus frozen** (carried from `BL-0297` and each requirement's verification text). Every
   Markdown file in the repository is live except frozen history: the run log part of
   `docs/pipeline/pipeline-journal.md` (its Position block is live), `docs/pipeline/backlog-archive.md`,
   `docs/pipeline/pipeline-journal-archive.md`, `docs/implementation/verification/`,
   `docs/reviews/`, and `docs/architecture/adr/`. Frozen files are never checked, because they
   record what was true when written.
2. **The checks run with the full suite** (`BL-0297`: "it runs in the full suite, so every `09` run
   gates on it"), as ordinary tests alongside `test_training_sources.py`, and `10`/`11` cite their
   result as evidence.
3. **First green run is the one-time cleanup, through a shrink-only allow-list** (`BL-0297`). Each
   check has a committed allow-list of its known existing defects. A defect on the list does not
   fail the suite; a defect not on the list does; an allow-listed entry that no longer occurs
   fails too, so fixed defects must be removed and the list can only shrink. The target is empty.
   On 2026-10-23 the link check alone finds **82** broken relative links in 10 live files
   (`ROADMAP.md` 24; research primers `01`–`07` and `10`, 57; `R101`, 1) — the same count
   `BL-0297` measured at `e1f81fe`.

## User Workflows

1. **Any stage writing a document** runs the full suite before committing (the project's existing
   rule); a new broken link, a reference to a retired document, an index missing a new file or a
   ledger disagreement fails, naming the file and line.
2. **A stage retiring a document** (`BL-0292`'s sweep, or any later one) deletes the file and, in
   the same commit, adds one row to a `Retired documents` section of the `INDEX.md` of the folder
   that held it (former path, former ID if any, date, successor or `none`), rewrites every live
   reference to name the successor instead, and runs the suite; a declared path left in the tree, a
   live mention outside the section, or an incomplete row fails.
3. **Cleanup** — a stage owning an allow-listed defect fixes it and removes its allow-list entry in
   the same commit; the suite fails if the entry is left behind.
4. **Verification** — `09` runs the full suite (so every package is gated on the checks); `10` and
   `11` cite the result and the allow-lists' remaining size as evidence.

## System Behaviour

**Check 1 — links resolve** (`NFR-3800`):

- For every live Markdown file, every relative link target (a Markdown link whose target is not a
  URL with a scheme and not a page-internal `#anchor`) must name an existing file or folder,
  resolved from the linking file's folder. The fragment after `#` is ignored.
- Edge cases: links inside fenced code blocks are not links and are skipped; an absolute
  repository-root path (`/docs/…`) is reported as a defect rather than resolved, since it breaks
  in the rendered views the project uses; a link to a frozen file is fine if it exists.

**Check 2 — a retired document is deleted, declared, and no live document names it** (`NFR-3810`):

- *Declaration.* A `Retired documents` section is a second-level heading of exactly that title in
  an `INDEX.md`. Each table row gives: the former path, the former document ID (blank if it had
  none, for example a build-spec module number), the retirement date, and the successor path or
  `none`. The path and the successor are written as plain text or in backticks, never as a link (a
  link to a deleted file would fail check 1). Any `INDEX.md` may carry the section; the check reads
  every one. A tree with no such section passes (the state until `BL-0292` retires anything).
- *Failure mode (a), retired but not removed.* A declared path still exists in the tree. Reported
  naming the index, the row and the path.
- *Failure mode (b), a live reference.* A live file other than a `Retired documents` section
  contains a declared path or a declared ID, as a link, in backticks or in plain text. Reported
  naming the file, line and the declared entry, and the declaring index. A path is matched as a
  string; an ID as a whole token (`FR-1210` does not match `FR-12100`). A declaring row names its own
  path, so the section is excluded from the scan, and **only** the section: the rest of the same
  `INDEX.md` is scanned like any live file. A supersession note elsewhere must name the successor,
  not the retired file (owner decision 2026-10-31); there is no allow-list of referrers.
- *Failure mode (c), an incomplete row.* A row with no date, or no successor (`none` is a valid
  successor), or an unparseable date, or no path. Reported naming the index and row.
- *Scan scope.* The live set is check 1's (frozen history exempt). Unlike check 1, fenced code
  blocks and inline code spans are scanned, because `NFR-3810` counts a path in backticks and a
  command snippet naming a retired path is still a live mention.
- *Edge cases.* A successor that is itself later retired is declared by its own row and is then
  forbidden elsewhere like any declared path; a row whose successor does not exist fails check 1 only
  if written as a link, so the successor is checked for existence by this check (reported as
  failure mode (c)); a path that is a prefix of another is matched on whole path boundaries; a
  retired folder is declared as one row with a trailing `/` and matches any path beneath it.
- *Interplay with the shrink-only allow-list.* Check 2 uses the same gate as checks 1, 3 and 4 and
  its own committed allow-list, `doc_integrity_allow_retired.txt`, **empty when check 2 lands** (no
  document is retired yet, so there is no existing defect to carry). It exists so a large retirement
  sweep can land with a counted, shrinking list rather than a pile of simultaneous fixes; an
  entry that no longer occurs fails. Failure modes (a) and (c) are never allow-listable: a row is
  either true or fixed.

**Check 3 — each index agrees with its folder** (`NFR-3820`):

- For every `INDEX.md`, every Markdown document directly in its folder (other than the index
  itself) must be **listed**: linked, or named as a path in backticks, either by the index or by a
  sub-index the index links. Every document the index links must exist (check 1 covers this).
- The sub-index rule is what lets `docs/research/encyclopedia/INDEX.md` list its topics through
  `R100-index.md`…`R600-index.md`. With these rules, measured on 2026-10-23 across the 14 live
  indexes, three documents are unlisted: `docs/INDEX.md` omits `AUDIT-2026-06-COMMANDS.md` and
  `AUDIT-2026-06-UI-TTC.md`, and `docs/architecture/INDEX.md` omits
  `strategic-assumptions-register.md`. They go on the allow-list or are fixed.
- Edge cases: a folder whose index is named otherwise (`docs/features/feature-index.md`) is
  outside `NFR-3820`'s wording (`INDEX.md`) and not checked (Open Question 3); subfolders are not
  "documents in the folder".

**Check 4 — status ledgers agree** (`NFR-3830`):

- The check compares an item's status where two ledgers both report it, for these pairs:
  - each package's status in the Master Build Plan and in `docs/implementation/packages/INDEX.md`;
  - each GDS level's status in `docs/architecture/INDEX.md` §1 and in `ROADMAP.md`;
  - each feature specification's status in `docs/features/feature-index.md` and in its own
    header's Status line.
- "Agree" means the same status word from the ledgers' shared vocabulary (`READY`, `IN PROGRESS`,
  `COMPLETE`, `VERIFIED`, `BLOCKED` for packages; authored/planned for GDS levels; the FS status
  phrases). An item missing from one ledger of a pair is reported.
- Edge cases: an item one ledger reports and the other legitimately omits (for example a ledger
  that lists only open items) is handled by the pair definition, not by guessing; pairs whose
  vocabularies cannot be mapped mechanically are not checked (Open Question 2).

**Every failure names** the check, the file (and line, for checks 1 and 2), and the offending
target, register entry, unlisted document or disagreeing statuses.

## Subsystem Responsibilities

The architecture's component set has no component for documentation (feature review F-16); these
rows name the existing locations.

| Location | Responsibility |
|---|---|
| `spacesim/tests/` | Hosts the four checks as tests (beside `test_training_sources.py`), with each test carrying `@pytest.mark.verifies(...)` naming its leaf. Check 2 reuses the existing module's `live_md_files`/`live_text` (the live set), its table-row reader (`_cells`, the ledger reader's row splitter) for the declaration rows, `broken_links`' line-numbering convention, and the `read_allow`/`_gate` pair; it adds only the section reader and the matcher. It does not run a second link checker: link-form references are caught by its own string match, and dead-link detection stays check 1's. May share a module and a Markdown-reading helper with FS-133's origin check (FS-133 OQ2). |
| The `Retired documents` sections of the folder `INDEX.md` files | Declare retired paths and IDs with date and successor. Written by the stage that owns the folder's index (`NFR-3820` already forces that index to agree with its folder), in the retiring commit; no new file, owner or shared write. |
| The allow-lists (committed beside the tests) | Record known existing defects; shrink only. |
| Every live document and its owning stage | Fix the defects found (each stage owns its own documents, `.claude/skills/README.md` "Every document has one owner"). |

## Interfaces Used

None of the ICD's interfaces — no runtime component is involved.

## Data Model Changes

None to the Domain Model. The repository gains the `Retired documents` sections (as retirements happen) and the allow-lists.

## State Changes

None at runtime. Repository state: the declarations grow as documents retire; the allow-lists shrink
to empty.

## Error Handling

- A defect not on its allow-list → the suite fails, naming it.
- A stale allow-list entry (the defect no longer occurs) → the suite fails, naming the entry.
- A `Retired documents` section whose table cannot be read (no header row, wrong column count) → check 2 fails naming the index, rather than passing because no row was parsed.
- A ledger that cannot be read or yields no entries where some are expected (for
  example, a reformatted Master Build Plan table) → the check fails naming the file, rather than
  passing because nothing was compared.
- A live file that cannot be decoded as text → reported as a defect, not skipped.

## Performance Considerations

The checks read every live Markdown file once (about 360 files on 2026-10-23); they must not
render, fetch or execute anything. Check 2 adds no second pass over the tree beyond one extra scan per live file against the declared entries (declarations are read first, once); with no declaration it returns without scanning, and with N declared entries the cost is N string searches per file, which stays small beside the suite. No NFR sets a time budget.

## Security Considerations

None: the checks read local files only and never follow external links (external URLs are not
checked — `NFR-3800` concerns relative links only).

## Console Friction

Not applicable: no console surface (the subject is the documentation tree).

## Manual Impact

None for the operator manuals. The retirement procedure (`Retired documents` row, same commit) is process text for the stages; it belongs in `.claude/skills/README.md` and the retiring stage's skill, an owner-authorized edit outside this spec's write scope (carried from v1.0 Open Question 1's resolution path).

## Acceptance Criteria

1. With the allow-lists as committed, the four checks pass on the tree.
2. Adding a live document with a broken relative link fails check 1 naming the file, line and
   target; the same link inside a fenced code block, or in a frozen file, does not.
3. Declaring a path as retired while a live document still links, backticks or names it fails check 2
   naming the file and line; with the reference removed and the file deleted, it passes. A path
   still present in the tree, and a row without a date or successor, each fail check 2 naming the row.
   A declared ID matches as a whole token only. A reference inside the declaring `Retired documents`
   section, or in frozen history, does not fail.
4. Adding a Markdown file to a folder with an `INDEX.md` that does not list it (directly or through
   a linked sub-index) fails check 3 naming both.
5. Setting one package's status differently in the Master Build Plan and in the package index fails
   check 4 naming the package and both statuses; the same for a GDS level and for a feature
   specification.
6. Fixing an allow-listed defect without removing its entry fails the suite naming the entry.
7. Each allow-list has a stated owner per entry (the stage owning the document), and its count is
   recorded in the Verification Report of the package that lands the checks.
8. Every test added carries `@pytest.mark.verifies(...)` naming its `NFR-38x0` leaf.

## Verification Plan

Criteria 1–6 and 8: Test (criteria 2–6 by tests that run each check against a small synthetic
document tree, not by breaking the real one). Check 2 synthetic trees, each tagged
`@pytest.mark.verifies("NFR-3810")`: (i) no section passes; (ii) a clean retirement passes; (iii) the
declared file left in place fails (a); (iv) a live link, a backticked path, a plain-text path, and a
whole-token ID each fail (b), while `FR-12100` against declared `FR-1210` does not; (v) a mention
inside a fenced block fails (b); (vi) a mention in a frozen path and in the declaring section passes;
(vii) a missing date, a missing successor and a `none` successor (valid) give (c) fail, fail, pass;
(viii) an unreadable table fails; (ix) an allow-listed (b) defect passes and a stale entry fails.
The real-tree test asserts the committed tree and the empty allow-list pass. Criterion 7: Inspection at `09`.

## Dependencies

FEAT-11100 per the catalog (the leaves cite `NFR-3400`; this suite follows the footer check's
pattern) — built. No `FS-xxx` prerequisite. Coordinates with FS-133 (shared runner).

## Risks

- **Allow-lists that never shrink.** A list that only must not grow could sit at 80 entries for
  ever. Mitigation: `10`/`11` cite its size; the owner may set a date to empty it.
- **False positives on legitimate references.** A live document that discusses a retired file
  historically (for example, a supersession note naming `build-spec/02`) would fail check 2.
  Mitigation: such notes belong in frozen records (ADRs, reviews), and a live note names the
  successor instead (owner decision 2026-10-31; no allowed-referrer list). Residual: a first
  retirement sweep may touch many live files; the empty-at-landing allow-list is the relief valve.
- **Ledger formats change.** Check 4 parses Markdown tables; a reformat can silently empty a
  comparison. Mitigation: Error Handling's "no entries" rule.

## Open Questions

1. **Closed 2026-10-31 — where the declaration lives.** Owner decision (accepting the choice in
   `NFR-3810`'s Notes): a `Retired documents` section in the `INDEX.md` of the folder that held the
   file. v1.0's register file and its three alternatives are withdrawn. Remaining gap: the repository
   root has no `INDEX.md` (see Open Question 6).
2. **Ledger pairs.** `NFR-3830` names five ledgers (`ROADMAP.md`, the Master Build Plan, the
   package index, `architecture/INDEX.md` §1, the feature index), but the feature index and
   `ROADMAP.md` use free-text statuses that do not map to the package vocabulary. This spec checks
   the three pairs above; whether `ROADMAP.md`'s feature and phase rows must also be compared needs
   a shared vocabulary that no ledger defines. **Resolution path:** `04` (tighten `NFR-3830`'s
   scope) or the ledgers' owners (adopt a shared status vocabulary); revisit at the next `04` pass.
3. **Index files not named `INDEX.md`.** `docs/features/feature-index.md` is an index in all but
   name; `NFR-3820` says `INDEX.md`. **Resolution path:** `04` widens the wording, or the file is
   renamed by its owner (`06`); neither is decided here.
4. **Closed 2026-10-31 — allowed referrers.** Owner decision: a declared path or ID is named nowhere
   live except its declaring row; there is no allow-list of referrers. A supersession note elsewhere
   names the successor.
5. **Realigned — retirement of requirement leaves** (FS-133 OQ1). `NFR-3810` puts retired
   requirement leaves out of scope (`BL-0317`); this check covers documents and their IDs only.
   Recording retired leaves, if wanted, is `04`'s call and would be a separate leaf. No action here.
6. **A root-level retired document.** `NFR-3810` says the declaration lives in the `INDEX.md` of the
   folder that held the file, but a root file such as `ROADMAP.md` or `memory.md` has no folder
   index (the root has none). Needs the owner or `04` to name the carrier (most naturally the
   `docs/INDEX.md`, which already routes the root documents); until then the check reads every
   `INDEX.md`, so a declaration there works, and the gap is unexercised.

## Related ADRs

None identified (documentation governance is set by MSTR documents and `BL-0297`, not an ADR).

## Related Interfaces

None.
