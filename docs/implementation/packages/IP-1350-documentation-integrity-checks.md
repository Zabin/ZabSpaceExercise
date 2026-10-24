# IP-1350 — Documentation Integrity Checks: Links, Indexes, Ledgers (NFR-3800, NFR-3820, NFR-3830)

> **Package ID:** IP-1350
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1350](../verification/VR-1350-documentation-integrity-checks.md), fresh session; READY before that) — authored 2026-10-23 by `07-implementation-planning`, pipeline run #223.
> **Authorization (MSTR-006 §3):** **given.** Owner direction `BL-0297` chose the scheme; the master build plan row and the `run #230` ledger note record the owner's go-ahead of 2026-10-23. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [FS-135](../../features/FS-135-documentation-integrity-checks.md) v1.0 (the spec).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0297`
> **Produces:** three of FS-135's four checks in the full suite, each with a shrink-only allow-list
> holding today's defects. The fourth (`NFR-3810`, retired documents) is planned after the owner
> decides where the register lives (`BL-0319`).
> **Feature Reference:** [FS-135](../../features/FS-135-documentation-integrity-checks.md) (`FEAT-12300`)
> **Related Topics:** `spacesim/tests/test_training_sources.py` (the model); [IP-1330](IP-1330-test-origin-marker-and-checks.md)
> (its ledger reader may be shared later; independent)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package; test-only.*

---

## Package ID

IP-1350.

## Objective

**Measured at `3087100`** (scripts in the pipeline run, read-only): 358 live Markdown files;
**82 broken relative links in 10 files** (`ROADMAP.md` 24; research primers `01`–`07` and `10`, 57;
`R101`, 1); of 14 live `INDEX.md` files, **3 documents unlisted** (`docs/INDEX.md` omits
`AUDIT-2026-06-COMMANDS.md` and `AUDIT-2026-06-UI-TTC.md`; `docs/architecture/INDEX.md` omits
`strategic-assumptions-register.md`) under FS-135's listing rule; the Master Build Plan and the
package index agree on all 66 package statuses. After this package the suite fails on any **new**
defect of these kinds, the known ones sit on allow-lists that may only shrink, and the GDS-level
and feature-spec ledger pairs are checked too.

## Design Decisions

1. **Live set.** All `*.md` under the repository root except `.git/` and FS-135 Decision 1's frozen
   history: `docs/implementation/verification/`, `docs/reviews/`, `docs/architecture/adr/`,
   `docs/pipeline/backlog-archive.md`, `docs/pipeline/pipeline-journal-archive.md`, and the run-log
   part of `docs/pipeline/pipeline-journal.md` (everything after its Position block). `.claude/`
   skill files are live (they are maintained documents).
2. **Allow-list form.** One committed text file per check beside the tests, one defect per line
   (file + target, or index + document, or item + ledger pair), each line naming its owning stage.
   A listed defect that no longer occurs fails the check (shrink-only, FS-135 Decision 3).
3. **Ledger pairs** (FS-135 check 4): (i) package status, Master Build Plan status table ↔
   `packages/INDEX.md`; (ii) GDS level status, `docs/architecture/INDEX.md` §1 ↔ `ROADMAP.md`'s
   "Global ladder" table, compared as authored / planned; (iii) FS status, `feature-index.md` row ↔
   the spec's own `Status:` header line, compared as Ready / Done / candidate. Each comparison fails
   loudly if a ledger yields no rows.
4. **Check 2 is a separate, later package** — blocked on `BL-0319` (where the register lives and who
   writes it); not authored now, so no package pretends to an owner decision.

## Requirements Covered

NFR-3800, NFR-3820, NFR-3830.

## Architecture Components

Test suite only; reads documentation.

## Interfaces

None.

## Files to Create/Modify

- **Create** `spacesim/tests/test_doc_integrity.py` — checks 1, 3, 4.
- **Create** `spacesim/tests/doc_integrity_allow_links.txt`, `doc_integrity_allow_indexes.txt`,
  `doc_integrity_allow_ledgers.txt` — today's defects (Decision 2).
- **Docs:** `CLAUDE.md` "Test-driven workflow" (one sentence: documentation checks run with the
  suite; allow-lists only shrink); RTM `NFR-3800`/`NFR-3820`/`NFR-3830` Test cells.

## Implementation Tasks

1. Baseline suite run.
2. Write the synthetic-tree tests first (each check against a small temporary document tree with
   one seeded defect); confirm they fail.
3. Implement the live-set walk, the three checks and allow-list handling.
4. Run against the real tree; record every defect in the allow-lists with its owning stage; confirm
   counts match the Objective (82 / 3 / 0) or explain the difference in the completion note.
5. Full suite, both gates; docs.

## Tests to Add

In `spacesim/tests/test_doc_integrity.py`:

| Test | Verifies | Asserts |
|---|---|---|
| Real tree: no unlisted broken relative link | `NFR-3800` | none outside the allow-list |
| Synthetic: broken link reported with file, line, target; the same in a fenced block or a frozen file is ignored | `NFR-3800` | as stated |
| Real tree: every `INDEX.md` lists its folder's documents (directly, by backticked path, or via a linked sub-index) | `NFR-3820` | none outside the allow-list |
| Synthetic: a new unlisted file is reported with both names | `NFR-3820` | as stated |
| Real tree: the three ledger pairs agree | `NFR-3830` | none outside the allow-list |
| Synthetic: differing package / GDS / FS statuses reported with item and both statuses; a ledger yielding no rows fails loudly | `NFR-3830` | as stated |
| Each allow-list is shrink-only: a listed defect that no longer occurs fails | `NFR-3800`, `NFR-3820`, `NFR-3830` | as stated |

## Documentation Updates

`CLAUDE.md`; RTM rows. The cleanup itself (fixing the 82 links and 3 index rows) belongs to each
document's owning stage and is not this package's work; the allow-lists name those owners.

## Definition of Done

1. Three checks in the full suite; all pass with the committed allow-lists.
2. Allow-lists hold exactly today's defects, each with an owning stage; shrink-only enforced.
3. Synthetic tests prove each check fails on a seeded defect.
4. Every test tagged; failing-first run recorded.
5. Full suite and both gates green; docs updated.

## Verification Checklist

- [ ] Adding a broken link to a live document fails the suite naming it (demonstrate once).
- [ ] Allow-list counts match the Objective's measurements, or the difference is explained.
- [ ] Frozen-history paths are excluded exactly as Decision 1 lists.
- [ ] Both gates green by name; full suite counts recorded.

## Dependencies

None. A later package for check 2 depends on `BL-0319`.

## Risks

- **Over-broad live set** (e.g. vendored Markdown) inflating the allow-lists: Decision 1 is
  explicit; anything surprising is reported in the completion note.
- **Allow-lists that never shrink:** `10`/`11` cite their size (FS-135 Risks).

## Rollback Considerations

Revert the commit; test-only.
