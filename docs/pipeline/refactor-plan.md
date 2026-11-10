# Repository refactor — plan, progress and work packets

[↑ Docs index](../INDEX.md) · [Process and security review](../reviews/process-and-security-review-2026-11.md) · [Whole-release review](../reviews/integration-review-release-1.0-whole-release.md) · [Backlog](backlog.md)

> **What this is.** The working plan for the repository refactor the owner ordered on 2026-11-09,
> and the instructions for whoever picks up each piece. **The refactor is paused** (owner,
> 2026-11-10) after step 4b. Nothing below starts until the owner assigns it.
> Update the progress table in the same pull request as each packet.

## 1. Owner decisions

1. The restructuring is **behaviour-preserving**. The 13 open product and security defects from the two
   reviews (`BL-0431`–`BL-0443`) are fixed as their own packages, never inside a move.
2. **Code** goes through pipeline packages and independent verification. **Records, documents and
   skills** are owner-authorized maintenance changes.
3. Superseded records and documents **may leave the working tree**; Git history and
   `archive/release-1.0` keep them.
4. A GitHub Actions workflow may be added (done).
5. Refactor pull requests **merge on green**.
6. **One open pull request at a time.** Merge it, let its branch be deleted, then open the next.
7. **Work is assigned by capability tier** (2026-11-10). Tier A is the most capable model the owner
   has; Tier B the next; Tier C the routine one. The owner says which model fills each tier. A
   lower tier never does a higher tier's packet.

## 2. Progress

| # | Step | State |
|---|---|---|
| 1 | CI (full suite on the locked dependencies, dependency audit); session hook installs from the lock; branch-cleanup workflow; 120 stale branches removed; `release-1.0` tag created | Done (PR #94) |
| 2 | `CLAUDE.md` cut to the durable guidance; code map moved to `docs/architecture/code-map.md` | Done (PR #95) |
| 3 | Short backlog and journal rows, full text kept in the archive files; 14 review findings harvested | Done (PR #96) |
| 4a | Retired: the earlier `IMP-xxxA` package folder, the earlier documentation plan (now MSTR-005 §1a), the root decision log | Done (PR #97) |
| 4b | The three June audit files moved into `docs/reviews/` | Done (PR #98) |
| 4c–4f, 5, 6, 7 | See the packets below | Paused |

## 3. Rules for every session, whatever its tier

1. **Read first:** `CLAUDE.md`, this file, the Position block of `pipeline-journal.md`.
2. **One open pull request at a time.** Branch from `main`; one packet per pull request; CI green;
   squash-merge; confirm the branch was deleted; only then start the next packet.
3. **Before pushing:** `python3 -m pytest spacesim/tests/test_doc_integrity.py spacesim/tests/test_test_origins.py`
   for a documentation packet; the whole suite (`python3 -m pytest`, about 5 minutes) for anything
   under `spacesim/` or `tools/`.
4. **Never** edit a frozen record: `docs/reviews/`, `docs/implementation/verification/`,
   `docs/architecture/adr/`, the two `*-archive.md` files (append-only), the journal's run log.
5. **Never** add a line to an allow-list under `spacesim/tests/` (they only shrink), skip or delete
   a test to get green, or change a test in a packet labelled behaviour-preserving.
6. **Cloud sessions cannot push tags or delete branches.** Run the `Branch cleanup` workflow.
7. **Scripts** used to make bulk edits live in the scratchpad, not the repository, and must be
   re-runnable from a clean checkout (reset, then run once).
8. **Record the packet:** update §2 here, add one short journal row, close or update the backlog
   rows the packet names. Short rows only (see the backlog header).
9. **Stop and hand back to Tier A** (leave the branch unpushed, write what happened in the chat)
   if any of these occurs:
   - `test_determinism.py`, `test_import_guard.py` or the behaviour baseline (packet A4) fails;
   - a test must change for a "behaviour-preserving" packet to pass;
   - a requirement's meaning, an invariant in `CLAUDE.md`, or the trust model would change;
   - the retired-documents check cannot be satisfied without rewording a requirement's Description
     or Acceptance Criteria (rewording its *Source documents* line is expected and fine);
   - the packet turns out to need a file outside its stated write scope;
   - a save written before the change no longer loads after it.

### The retirement loop (used by every step-4 packet)

1. Delete or move the files with `git rm` / `git mv`.
2. Add one row per retired path to "Retired documents" in `docs/INDEX.md`
   (`| path | former ID or blank | date | successor path or none |`). Leave the ID column blank
   unless the packet says otherwise: a blank ID means only the path is policed.
3. Run the documentation-integrity test. It lists every live reference (`file:line`) and every
   broken link. Fix each one: point it at the successor, or reword it to name the successor.
   Never fix a reference by deleting a requirement's source without giving its successor.
4. Also search for short-form mentions the check does not police (`git grep -n '<folder>/'`) and
   correct those too.
5. Code comments that cite a retired path are **not** touched in a documentation packet; add them
   to packet C4's list.
6. Repeat until the test passes with every allow-list unchanged or shorter.

## 4. Tier A only — highest risk

These either decide something the rest depends on, or can break determinism, replay, saves or fog
of war in ways the suite will not catch. Nobody else starts them.

| ID | Work | Why it is Tier A |
|---|---|---|
| **A1** | **Successor map for `docs/build-spec/` and `docs/design/`.** For every section that a live document cites, name the GDS section (or other live document) that now carries it, or say "no successor: migrate first". Decide the new home of the Interface Control Document (`design/05-interface-control-document.md`, backlog `BL-0294`) and of the phase plan in `build-spec/04` §10. Output: a table added to this file. | A wrong row silently misattributes a requirement's source. About 110 documents will be rewritten from it. |
| **A2** | **Successor map for `docs/domains/` (`DOM-001`…`DOM-008`).** Same shape; 117 documents cite them, many as requirement sources. Confirm for each DOM section that the GDS ladder really absorbed it (journal runs #197–#204 say most was; `BL-0303` records one gap). | Same risk, larger. |
| **A3** | **Ledger design (step 5).** Decide the single source of truth for package status and document status, what is generated from it, and how `test_doc_integrity.py` (ledger agreement) and `baseline_ids.py` (which reads `packages/INDEX.md` and `feature-index.md`) change. Output: a short design in this file plus the package specification for the test change. | It changes what the suite's own integrity checks mean. |
| **A4** | **Behaviour baseline.** Design and build, as the first code package, a test that pins current behaviour: the suite's counts, and for each of the 19 vignettes a hash of the world after a fixed scripted run (orders from both cells, an immediate and a future-dated inject, about two simulated hours), plus save → reload → continue equality. **Trap:** `SessionManager.start()` arms the wall-clock anchor and `set_clock(False)` folds elapsed wall time into the simulation, so a naive script hashes a different world every run. The baseline must never let wall time reach the engine. | Every later code packet is judged against it; if it is unsound, they all are. |
| **A5** | **Split plan for `session/manager.py`, `engine/orders.py`, `ui_web/server.py` and `static/app.js`.** Name the target modules, what moves where, the order of the moves, and for each move the invariant it could break. Output: one package specification per move. | Module boundaries decide whether determinism, the session lock and the fog boundary stay intact. |
| **A6** | **Carry out the `manager.py` and `orders.py` moves** from A5. | These files hold the replay handlers, save and resume, rewind re-arming and the lazy clock. A mistake here corrupts saves or replay without failing a test. |
| **A7** | **Design the two defect fixes that touch invariants.** `BL-0431` (order previews return ground truth: decide belief-based preview or refusal) and `BL-0432` (bus ticks stop at the horizon: decide tick-to-ceiling or stop-the-clock; either changes every event log and therefore saved exercises). Output: requirement text for `04` and a package specification each. | One is the fog-of-war invariant, the other the determinism and save contract. |
| **A8** | **Gate inventory for the pipeline skills (step 6).** List every gate, independence rule and write-scope rule the 21 skills enforce today, with the skill and line that states it. Output: a checklist in this file. Then review every rewritten skill against it. | A rewrite that drops a gate (authorization, fresh-session verification, release archive) goes unnoticed until it matters. |
| **A9** | **Final review** of the whole refactor before Release 2.0 work resumes: rerun the baseline, the full suite and a live probe pass like the November whole-release review. | Independent confirmation that behaviour did not move. |

## 5. Tier B — judgement within a written decision

Each packet has a Tier A input. Do not start one whose input does not exist yet.

### B1 — Retire `docs/build-spec/` and `docs/design/` (step 4c). Input: A1.

1. Read A1's table. If a row says "migrate first", do that migration as its own commit in the
   same pull request: move the text into the named successor, keeping its wording.
2. Run the retirement loop (§3). Declare `docs/build-spec/` and `docs/design/`.
3. Requirements cite these as sources. Change only the **Source documents** line, to the successor
   from A1. Do not touch Description, Rationale or Acceptance Criteria.
4. `CLAUDE.md` names `docs/build-spec/`; update it. Update
   `README.md`'s tree and `MSTR-005`'s tree.
5. Seven source files cite build-spec sections in comments: list them for C4, do not edit them.
6. Backlog: close `BL-0288`, `BL-0292`'s remainder, `BL-0294`, `BL-0301`'s remainder as they are met.
7. Done when: both folders are gone, the integrity test passes, the link allow-list is shorter
   (most of its lines are research-primer links into build-spec), and no live document names
   either folder.

### B2 — Retire `FUTURE-WORK.md` (step 4d). No Tier A input.

1. Read all of `docs/FUTURE-WORK.md` (about 1,400 lines). For each item decide: already built
   (cite the package or code), already in the backlog (cite the row), in the Release 2.0 plan
   (cite the plan row), or still open.
2. File each still-open item as one short backlog row (`00-intake` shape, Status `DEFERRED`,
   Next = "owner decision or a later release"). Expect a few dozen at most; group near-duplicates.
3. Put the disposition table (item → where it went) in the pull request description, not in the
   repository.
4. Run the retirement loop. 55 documents and 22 code files name it. The code files are comments
   of the form `FUTURE-WORK §n`: list them for C4.
5. Backlog: close `BL-0296`, `BL-0306` if answered by the plan's symbology decision.
6. Done when: the file is gone, every open idea in it has a backlog row, the test passes.

### B3 — Retire `docs/domains/` (step 4e). Input: A2.

1. As B1, driven by A2's table. Declare the folder **and** the IDs `DOM-001`…`DOM-008` (this is
   the one packet that fills the ID column), so no live document may name a retired domain ID.
2. This is the largest rewrite (117 documents). Work one target folder per commit:
   `requirements/`, `architecture/`, `features/`, `research/`, `master/`, the rest.
3. In requirements, again change only **Source documents**.
4. Done when: the folder is gone, no live document names a `DOM-` ID, the test passes.

### B4 — Apply the ledger design (step 5). Input: A3.

Follow A3's design exactly. The documentation half (cutting `ROADMAP.md` and the Master Build Plan
to what is current) is a maintenance pull request. The test half is a code package: it goes through
`07` → `08` → `09` with a verifier from a different session.

### B5 — Rewrite the pipeline skills (step 6). Input: A8.

1. State the shared rules once in `.claude/skills/README.md`; each skill links to them.
2. Rewrite one skill per commit. Keep its procedure and its quality gate; remove dated history,
   incident narratives and rules now stated in the README.
3. After each skill, tick A8's checklist: every gate that skill held is still stated, in the
   skill or the README.
4. Add to `09-package-verification` and `10-integration-review` the seam check the process review
   asked for (finding P-4): tests generated from the live route table for fog and for refusals.
   The test itself is a code package.
5. Done when: A8's checklist is fully ticked and Tier A has reviewed the diff.

### B6 — Split `ui_web/server.py` into routers. Input: A5.

Behaviour-preserving code package. Route order matters (`export.csv` is declared before the
`{param}` route so it is not captured), and the guard dependencies are pinned by a route-table
test: the live route table before and after must be identical in path, method, order and guards.
Dump it before, dump it after, diff. The baseline (A4) must be unchanged.

### B7 — Split `static/app.js`. Input: A5.

Behaviour-preserving code package, one extracted file per commit. There is no module system: the
files share globals and load in the order `index.html` lists them. The suite covers the console
only through 42 browser tests, so after each extraction also drive the console by hand with the
`run-spacesim` skill: load a vignette, start, issue an order as Blue, fire an inject as White,
open the AAR, open the Creator. Report what was driven. Stop at the first console error.

### B8 — Defect packages that need care. Inputs: A7 for the first two.

Each through `07` → `08` → `09`, test first, one package each:
`BL-0431` and `BL-0432` (to A7's design), `BL-0433` (parameter change discards setup),
`BL-0435` (order with a bad cell poisons the save), `BL-0440` (script injection: escape at every
HTML sink in `app.js`, validate inject `a`/`b` as ids, add a browser test that an HTML payload
renders as text), `BL-0434` with `BL-0418` (save-as-scenario).

### B9 — Verify Tier C's code packages

Every code package is verified (`09-package-verification`) by a session that did not write it and
is at least one tier above its author. Tier B's packages are verified by Tier A or by a fresh
Tier B session; Tier A's by a fresh Tier B session.

## 6. Tier C — mechanical, with a check that proves it

### C1 — Generated media out of Git (step 4f)

`docs/manual/` holds 57 screenshots, a 1.3 MB GIF and a 4.1 MB video, all produced by
`tools/render_manual.py` and `tools/record_walkthrough.py`. First check which training documents
embed them (`git grep -n 'manual/' docs/training`). Keep every image a manual embeds. Remove the
video and GIF and any image nothing embeds, add them to `.gitignore`, and say in
`docs/manual/`'s index how to regenerate them. Done when the integrity test passes and no
training page shows a broken image.

### C2 — Linter and formatter configuration

Add `ruff` to the `dev` extra and a `[tool.ruff]` section in `pyproject.toml`. Start with the
default rule set and **no automatic fixes**: the first pull request only adds the configuration,
records the current violation count per rule in its description, and adds a CI step that runs
`ruff check` in report-only mode (`--exit-zero`). Do not reformat any file in this packet.

### C3 — Lint fixes, one rule family per pull request

After C2 merges. Apply fixes for one rule family at a time, never in `spacesim/engine/` without
running `test_determinism.py` and the baseline, never `--unsafe-fixes`. The full suite and the
baseline must pass unchanged. When a rule is clean, make CI enforce that rule.

### C4 — Comment corrections (code package, comments only)

One package, through `07` → `08` → `09`. Change comments and docstrings only; the diff must
contain no executable line (the verifier checks this with `python -m compileall` plus an AST
comparison of every touched file before and after). Scope:
- citations of moved or retired documents: `memory.md` in `engine/effects.py`; the June audit
  paths in `engine/buscommands.py`, `engine/engage.py`, `tests/test_bus_commands.py`,
  `tests/test_defensive_audit_2026.py`; build-spec and `FUTURE-WORK` citations listed by B1 and B2;
- nothing else. Package history in comments (`IP-xxxx`, `BL-xxxx`) is left for A5 to rule on.

### C5 — Low-severity defect packages

Each through `07` → `08` → `09`, test first, one package per backlog row, verified by Tier B:
`BL-0436` (seven requests return 500), `BL-0437` (force-add over an existing id),
`BL-0438` (session cap evicts the running exercise), `BL-0439` (unknown cell names accepted),
`BL-0441` (`Host` check), `BL-0442` (size limits), and the rows marked Low among `BL-0394`–`BL-0412`
(read the Sev column; the Medium ones are Tier B).
A fix that needs a design choice not written in the row goes back to Tier B.

### C6 — Hashed dependency lock (`BL-0443`)

Regenerate `requirements.lock` with file hashes (`pip-compile --generate-hashes`, or
`pip download` plus `pip hash`), keeping the same versions. Change the CI install and the session
hook to `pip install --require-hashes -r requirements.lock`. Done when CI is green on the hashed
lock and the versions are byte-for-byte the ones in the current lock.

### C7 — Upkeep after each merged packet

Regenerate the RTM Test column when tests change (`python3 -m pytest --origin-report=rtm`), move
closed backlog rows to the archive, keep `docs/architecture/code-map.md` current when a module
moves.

## 7. Order

```
A1 ─▶ B1 ─┐
B2 ───────┼─▶ B3 (needs A2) ─▶ A3 ─▶ B4 ─▶ A8 ─▶ B5
C1, C6 (any time, documentation and tooling only)
A4 ─▶ C2 ─▶ C3
A4 ─▶ A5 ─▶ B6, B7, A6 ─▶ C4
A7 ─▶ B8;  C5 (after A4)
everything ─▶ A9 ─▶ Release 2.0 resumes at the M0 requirements pass
```

Documentation packets (A1, A2, B1–B3, C1) and the baseline (A4) do not depend on each other, but
the one-open-pull-request rule still serialises them.
