# Repository refactor — plan and progress

[↑ Docs index](../INDEX.md) · [Process and security review](../reviews/process-and-security-review-2026-11.md) · [Whole-release review](../reviews/integration-review-release-1.0-whole-release.md)

> **What this is.** The working plan for the repository refactor the owner ordered on 2026-11-09.
> It is the memory a session needs to pick the work up: what is decided, what is done, what is next.
> Update the progress table in the same pull request as each step.

## Owner decisions (2026-11-09 and 2026-11-10)

1. The restructuring is **behaviour-preserving**. The 14 product and security defects from the two
   reviews are fixed as their own packages, never inside a move.
2. **Code** goes through pipeline packages and independent verification. **Records, documents and
   skills** are owner-authorized maintenance changes.
3. Superseded records and documents **may leave the working tree**; Git history and
   `archive/release-1.0` keep them.
4. A GitHub Actions workflow may be added.
5. Refactor pull requests **merge on green**.
6. **Few branches and few pull requests.** One open pull request at a time; merge it and let its
   branch be deleted before the next one opens. Never leave branches behind.

## Steps

| # | Step | State |
|---|---|---|
| 1 | Safety net: CI (full suite on the locked dependencies, dependency audit); session hook installs from the lock; branch-cleanup workflow; 120 stale branches removed; `release-1.0` tag created | **Done** (PR #94, 2026-11-10) |
| 2 | `CLAUDE.md` cut to the durable guidance; code map moved to `docs/architecture/code-map.md` | **Done** (PR #95, 2026-11-10) |
| 3 | Pipeline records: harvest the two reviews' findings into the backlog; short journal and backlog rows; the manager and intake skills updated to the new shape. The archive files stay in the tree: they are frozen, are not read in a normal run, and hold the full text | **Done** (this pull request) |
| 4 | Documentation retirement sweep (plan item D-08): `docs/build-spec/`, `docs/design/`, `docs/domains/`, `docs/implementations/`, the June audit files, `FUTURE-WORK.md`, `DOCUMENTATION-PLAN.md`, `memory.md`; one traceability matrix; generated media out of Git | Next |
| 5 | Ledgers: one source of truth for package and document status; `ROADMAP.md` and the Master Build Plan reduced to what is current | Planned |
| 6 | Pipeline skills: shared rules stated once; dated history removed; a route-table seam check added to verification | Planned |
| 7 | Code, through packages: a behaviour baseline test first (suite counts and a world hash per vignette); then behaviour-preserving splits of `app.js`, `manager.py`, `server.py`; lint and type checks; package history moved out of comments | Planned |

## Rules for every step

- The full suite and the documentation-integrity checks pass before the pull request opens, and CI
  is green before it merges.
- A step that deletes a document removes or rewrites every live reference to it in the same pull
  request, and declares it under "Retired documents" in the owning `INDEX.md`.
- No product behaviour changes in steps 1 to 6. In step 7 the behaviour baseline must be unchanged
  by every restructuring package.
- Findings discovered along the way go to the backlog, not into the step.
