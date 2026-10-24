# FS-135 — Documentation Integrity Checks

> **Document ID:** FS-135
> **Version:** 1.0 (2026-10-23, pipeline run #216)
> **Status:** ✅ Done for the three checks `NFR-3800`/`NFR-3820`/`NFR-3830` (built by `IP-1350`,
> `VERIFIED`). The `NFR-3810` retired-document check is unbuilt: Open Question 1 — where the
> register lives (`BL-0319`) — needs an owner decision first.
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
documents are live and which are frozen history; the retired-documents register the second check
reads; the shrink-only allow-list that lets the suite go green before the existing defects are all
fixed; and how the checks run (with the full suite).

Out of scope: fixing the defects the checks find (the cleanup is owned by each document's stage;
the checks only find and track them); prose accuracy and doc coherence that a test cannot judge
(`09-training-manual-review`, `10`, `11` keep those); the training `Sources:` footer check
(`NFR-3400`, already built, FEAT-11100 — kept alongside, not re-specified); the test-origin
resolution check (`NFR-3840`, FS-133), which may share this runner; retiring any document
(`BL-0292`).

## Requirements Implemented

NFR-3800 (relative links in live documents resolve), NFR-3810 (no live reference to a retired
document), NFR-3820 (each index agrees with its folder), NFR-3830 (status ledgers agree) — per
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
2. **A stage retiring a document** (`BL-0292`'s sweep, or any later one) adds the document to the
   retired-documents register in the same commit, updates live references, and runs the suite; any
   live reference left over fails.
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

**Check 2 — no live reference to a retired document** (`NFR-3810`):

- A retired-documents register lists each retired path (and, where the document carried one, its
  ID, such as a build-spec module number), with its retirement date and its successor.
- No live file may name a registered path or ID — as a link, or as a path in backticks. A live
  file may name the **register** itself.
- Edge cases: an empty register passes trivially (the state until `BL-0292` retires anything);
  a register entry whose path still exists in the tree fails ("retired but not removed"), unless
  the entry says it is kept as frozen history; IDs are matched as whole tokens, so `FR-1210` does
  not match `FR-12100`.

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
| `spacesim/tests/` | Hosts the four checks as tests (beside `test_training_sources.py`), with each test carrying `@pytest.mark.verifies(...)` naming its leaf. May share a module and a Markdown-reading helper with FS-133's origin check (FS-133 OQ2). |
| The retired-documents register (location: Open Question 1) | Lists retired paths and IDs with date and successor. Written by whichever stage retires a document, in the same commit. |
| The allow-lists (committed beside the tests) | Record known existing defects; shrink only. |
| Every live document and its owning stage | Fix the defects found (each stage owns its own documents, `.claude/skills/README.md` "Every document has one owner"). |

## Interfaces Used

None of the ICD's interfaces — no runtime component is involved.

## Data Model Changes

None to the Domain Model. The repository gains the register and the allow-lists.

## State Changes

None at runtime. Repository state: the register grows as documents retire; the allow-lists shrink
to empty.

## Error Handling

- A defect not on its allow-list → the suite fails, naming it.
- A stale allow-list entry (the defect no longer occurs) → the suite fails, naming the entry.
- A ledger or register that cannot be read or yields no entries where some are expected (for
  example, a reformatted Master Build Plan table) → the check fails naming the file, rather than
  passing because nothing was compared.
- A live file that cannot be decoded as text → reported as a defect, not skipped.

## Performance Considerations

The checks read every live Markdown file once (about 360 files on 2026-10-23); they must not
render, fetch or execute anything. No NFR sets a time budget.

## Security Considerations

None: the checks read local files only and never follow external links (external URLs are not
checked — `NFR-3800` concerns relative links only).

## Acceptance Criteria

1. With the allow-lists as committed, the four checks pass on the tree.
2. Adding a live document with a broken relative link fails check 1 naming the file, line and
   target; the same link inside a fenced code block, or in a frozen file, does not.
3. Registering a path as retired while a live document still links or names it fails check 2 naming
   the file and line; with the reference removed and the file deleted, it passes.
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
document tree, not by breaking the real one). Criterion 7: Inspection at `09`.

## Dependencies

FEAT-11100 per the catalog (the leaves cite `NFR-3400`; this suite follows the footer check's
pattern) — built. No `FS-xxx` prerequisite. Coordinates with FS-133 (shared runner).

## Risks

- **Allow-lists that never shrink.** A list that only must not grow could sit at 80 entries for
  ever. Mitigation: `10`/`11` cite its size; the owner may set a date to empty it.
- **False positives on legitimate references.** A live document that discusses a retired file
  historically (for example, a supersession note naming `build-spec/02`) would fail check 2.
  Mitigation: such notes belong in frozen records (ADRs, reviews); where a live document must name
  one, the register entry may list it as an allowed referrer (Open Question 4).
- **Ledger formats change.** Check 4 parses Markdown tables; a reformat can silently empty a
  comparison. Mitigation: Error Handling's "no entries" rule.

## Open Questions

1. **Where the retired-documents register lives and who writes it.** `BL-0297` suggests
   `docs/pipeline/`, but `00-pipeline-manager` writes only its journal and backlog there, and every
   document needs one owning stage (`.claude/skills/README.md`). Options: a section of `docs/INDEX.md`;
   a file under `docs/` written by whichever stage retires a document (a shared write, against the
   one-owner rule); or a file owned by `03-architecture-design-synthesis`, which owns the
   supersession of build-spec and design. Matters because check 2 needs a home before it can read
   anything. **Resolution path:** owner decision, then the owning skill's text names the register
   (an owner-authorized skill edit). Until then checks 1, 3 and 4 can be built and check 2 waits.
2. **Ledger pairs.** `NFR-3830` names five ledgers (`ROADMAP.md`, the Master Build Plan, the
   package index, `architecture/INDEX.md` §1, the feature index), but the feature index and
   `ROADMAP.md` use free-text statuses that do not map to the package vocabulary. This spec checks
   the three pairs above; whether `ROADMAP.md`'s feature and phase rows must also be compared needs
   a shared vocabulary that no ledger defines. **Resolution path:** `04` (tighten `NFR-3830`'s
   scope) or the ledgers' owners (adopt a shared status vocabulary); revisit at the next `04` pass.
3. **Index files not named `INDEX.md`.** `docs/features/feature-index.md` is an index in all but
   name; `NFR-3820` says `INDEX.md`. **Resolution path:** `04` widens the wording, or the file is
   renamed by its owner (`06`); neither is decided here.
4. **Allowed referrers for retired documents.** Whether a register entry may name live documents
   that are allowed to mention it (supersession notes). **Resolution path:** decided with Open
   Question 1.
5. **Retirement of requirement leaves** (FS-133 OQ1). The register here covers documents and their
   IDs; whether retired requirement leaves are recorded in the same register or marked in the
   requirements documents is `04`'s call (`BL-0317`). This spec's register can hold leaf IDs if `04`
   chooses it.

## Related ADRs

None identified (documentation governance is set by MSTR documents and `BL-0297`, not an ADR).

## Related Interfaces

None.
