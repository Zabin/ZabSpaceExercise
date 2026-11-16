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
| 4d (B2) | `FUTURE-WORK.md` retired: open items not already in the Release 2.0 plan filed as `BL-0445`–`BL-0450`; 59 documents reworded | Done (PR #99) |
| A1 | Successor map for `build-spec/` and `design/` (§8): 45 cited sections mapped, the two open decisions made, 26 code files listed for C4 | Done (this pull request) |
| A4 | Behaviour baseline: `spacesim/tests/test_behaviour_baseline.py` pins a scripted two-hour run of each of the 19 vignettes (world, event log, pending queue, cell views, acknowledgements) plus save, reload and replay equality; re-bless and float rules added to §3 | Done (this pull request) |
| A5a | Split plan for `session/manager.py` (§9.1): inventory, six target modules, handler rules, nine ordered moves with tier and check, do-not-move list. `orders.py`, `server.py`, `app.js` (A5b to A5d) not planned yet | Done (this pull request) |
| A5b | Split plan for `engine/orders.py` (§9.2): inventory, five target modules, handler rules, seven ordered moves with tier and check, do-not-move list. `server.py`, `app.js` (A5c, A5d) not planned yet | Done (this pull request) |
| B1a | Glossary migration (§8.2 item 1: eight terms into MSTR-004 §2) and the Interface Control Document moved to `docs/architecture/interface-control-document.md` (§8.3 decision 1); live links repointed, old path declared retired; move half of `BL-0294` done | Done (this pull request) |
| B1b | Requirement documents: every build-spec/design citation in a *Source documents* line or candidate source repointed to its §8.1 successor or removed where the successor was already there; 16 mis-numbered GDS-04 citations corrected (1 left: `FR-2310`); `CNFR-05` reworded and `BL-0451` filed; out-of-permission Rationale citations listed in the PR for `04` | Done (PR #106) |
| B1c-1 | Citations of `build-spec/` and `design/` in `docs/architecture/` (not `adr/`), `docs/features/` and `docs/implementation/` (not `verification/`) repointed to the §8.1 successors or named as the retired v1 build specification or design corpus (rule (b)); three commits | Done (PR #107) |
| B1c-2 | Remaining live citations repointed to the §8.1 successors or reworded as the retired v1 specification or design corpus: `docs/master/`, `docs/research/`, training, vignettes, domains, feature-planning, three skill files, `CLAUDE.md`, `README.md`, `ROADMAP.md`, docs index, backlog; one stale link allow-list line removed. Left for B1d: ROADMAP legacy-theme tables, docs index theme rows, release-plan retirement narratives | Done (PR #108) |
| B1d | `build-spec/` (9 files) and `design/` (15 files) deleted and declared in `docs/INDEX.md`; live leftovers cleaned first (ROADMAP BS/DS theme tables, architecture provenance lines, release-plan D-07/D-08, docs index theme rows, skill and MSTR nits); `BL-0288` closed and archived; no allow-list line added or changed. Left open: requirement Rationale/Metric/Why-excluded mentions (for `04`), `BL-0294` re-issue, `spacesim/` comment citations (C4, §8.4) | Done (this pull request) |
| 4c, 4e, 4f, 5, 6, 7 | See the packets below | Paused |

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

### The behaviour baseline (packet A4)

`spacesim/tests/baseline/behaviour_baseline.json` is generated by `test_behaviour_baseline.py`
and never hand-edited. It pins simulator behaviour only; the suite's test counts are not in it.

- A **behaviour-preserving** packet must leave the file byte-identical.
- A **defect-fix package** may re-bless it (`SPACESIM_REBLESS_BASELINE=1 python3 -m pytest
  spacesim/tests/test_behaviour_baseline.py`), but only for the vignettes its fix explains. Its
  pull request lists the old and new hashes per vignette, and its verifier approves them.
- **Float rule.** Floats differ in their last bits between CPUs (OpenBLAS picks a kernel per CPU
  model), so each document is pinned as an exact hash of everything except its floats, plus the
  floats themselves, compared within 1e-8 relative. Nothing is rounded. Replay, save and reload
  stay bit-exact.

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
| **A1** | **Successor map for `build-spec/` and `design/`.** For every section that a live document cites, name the GDS section (or other live document) that now carries it, or say "no successor: migrate first". Decide the new home of the Interface Control Document (`design/05-interface-control-document.md`, backlog `BL-0294`) and of the phase plan in `build-spec/04` §10. Output: a table added to this file. | A wrong row silently misattributes a requirement's source. About 110 documents will be rewritten from it. |
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

### B1 — Retire `build-spec/` and `design/` (step 4c). Input: A1.

1. Read A1's table. If a row says "migrate first", do that migration as its own commit in the
   same pull request: move the text into the named successor, keeping its wording.
2. Run the retirement loop (§3). Declare `build-spec/` and `design/`.
3. Requirements cite these as sources. Change only the **Source documents** line, to the successor
   from A1. Do not touch Description, Rationale or Acceptance Criteria.
4. `CLAUDE.md` names `build-spec/`; update it. Update
   `README.md`'s tree and `MSTR-005`'s tree.
5. Seven source files cite build-spec sections in comments: list them for C4, do not edit them.
6. Backlog: close `BL-0288`, `BL-0292`'s remainder, `BL-0294`, `BL-0301`'s remainder as they are met.
7. Done when: both folders are gone, the integrity test passes, the link allow-list is shorter
   (most of its lines are research-primer links into build-spec), and no live document names
   either folder.

### B2 — Retire the former future-work list (step 4d). No Tier A input.

1. Read all of the former future-work list (about 1,400 lines). For each item decide: already built
   (cite the package or code), already in the backlog (cite the row), in the Release 2.0 plan
   (cite the plan row), or still open.
2. File each still-open item as one short backlog row (`00-intake` shape, Status `DEFERRED`,
   Next = "owner decision or a later release"). Expect a few dozen at most; group near-duplicates.
3. Put the disposition table (item → where it went) in the pull request description, not in the
   repository.
4. Run the retirement loop. 55 documents and 22 code files name it. The code files are comments
   of the form `former future-work list §n`: list them for C4.
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
- citations of moved or retired documents: the retired root decision log in `engine/effects.py`
  (find it with `git grep -n 'memory' spacesim/engine/effects.py`); the June audit
  paths in `engine/buscommands.py`, `engine/engage.py`, `tests/test_bus_commands.py`,
  `tests/test_defensive_audit_2026.py`; build-spec citations listed by B1; future-work-list citations (`FUTURE-WORK §n` comments) in: `spacesim/engine/access.py`, `spacesim/engine/bus.py`, `spacesim/engine/buscommands.py`, `spacesim/engine/conjunction.py`, `spacesim/engine/effects.py`, `spacesim/engine/entities.py`, `spacesim/engine/orders.py`, `spacesim/engine/propagator.py`, `spacesim/engine/recovery.py`, `spacesim/engine/ssn.py`, `spacesim/engine/telemetry.py`, `spacesim/engine/world.py`, `spacesim/session/aar.py`, `spacesim/session/manager.py`, `spacesim/tests/test_future_work.py`, `spacesim/tests/test_future_work_batch11.py`, `spacesim/ui_web/server.py`, `spacesim/ui_web/static/app.js`, `spacesim/ui_web/static/graph.js`, `spacesim/ui_web/static/logo.svg`, `spacesim/ui_web/static/style.css`, `spacesim/ui_web/static/symbology.js`;
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

## 8. A1 output — successor map for build-spec and design

Made 2026-11-12 at `d14882f`. Input to B1. Short forms are used throughout (`build-spec/04`,
`design/09`); GDS-NN means `docs/architecture/NN-*.md`.

**Method.** Every live file was scanned for a folder path, a file basename, `ICD`, or "build spec",
with the section or tag that follows it: 116 live documents and 26 code files cite one or both
folders (about 850 mentions; `ICD` or an `INT-` ID appears in 128 documents). Frozen records were
excluded. **Confirmed** means the cited text and the successor section were both read and the
successor carries the content. **Partial** means the successor carries the requirement-level
content but not all the detail, or was checked only against its own merge-gate statement.

**How B1 uses the table.** (a) In a requirement's *Source documents* line, replace the legacy
citation with the successor in the same row; where the successor is already on that line, just
remove the legacy citation. (b) A GDS level's own "Related Topics", "Merges from", "Departures"
and "Merge gate" text is provenance, not a citation: keep the sentence, and name the source as
"the retired v1 build specification" or "the retired design corpus" plus its section number,
without a path or link. (c) Everywhere else, point at the successor.

### 8.1 The map

| Cited section | Successor (path §section) | Confidence | Citing live documents (count; requirement IDs whose Source documents line cites it) |
|---|---|---|---|
| `build-spec/01` §1 (problem, purpose, objectives, non-goals) | GDS-01 §1; GDS-00 §4, §6; GDS-02 §1 | confirmed | 11 for the whole file (GDS-00, -01, -02, -03, -04, -10, architecture index, ROADMAP, MSTR-001, docs index, `requirements/02`); none |
| `build-spec/01` §2 (stakeholders, users) | GDS-01 §2–§3; GDS-02 §2, §5 | confirmed | GDS-01, GDS-02, GDS-03, GDS-00, MSTR-001; none |
| `build-spec/01` §3.1 (in scope); MSTR-001's "§2–3" (bounded scope) | GDS-01 §1, §4, §10; GDS-00 §6 | confirmed | GDS-00, GDS-01, GDS-02, MSTR-001; none |
| `build-spec/01` §3.2 (deferred list) | none, and none wanted: five of its eight rows have since shipped | no successor (see §8.5 finding 4) | `requirements/02`; `CNFR-05` (an excluded candidate, cited as "decision log") |
| `build-spec/01` §3.3 (round-4 assumptions) | GDS-01 §11 (RIC origin, help, theme); GDS-06 NFR-6 (error handling); GDS-06 NFR-2 (hardware floor) | confirmed | GDS-01; `NFR-1600` (written as "§3.3" after the `build-spec/04` path: GDS-06 NFR-6 is already on that line) |
| `build-spec/01` §4 (decisions D1–D10) | `docs/architecture/adr/INDEX.md` (the ADRs restate or supersede D1–D10); D2 = ADR-0018 | partial (D2 confirmed; no per-decision table exists) | GDS-01, GDS-02, `requirements/03`; none |
| `build-spec/02` §5.1 `FR-E1`–`E8` | GDS-05 §1, same tag | confirmed | `requirements/01`; `FR-1120`, `FR-1210`, `FR-1220`, `FR-1310`, `FR-1410`, `FR-1420`, `FR-1510` |
| `build-spec/02` §5.2 `FR-B1`–`B5` | GDS-05 §2, same tag | confirmed | `requirements/01`; `FR-2110`, `FR-2210`, `FR-2310`, `FR-2410`, `FR-2510` |
| `build-spec/02` §5.3 `FR-P1`–`P5` | GDS-05 §3, same tag | confirmed | `requirements/01`; `FR-3110`, `FR-3210`, `FR-3310`, `FR-3410`, `FR-3510` |
| `build-spec/02` §5.4 `FR-W1`–`W7`, and the file cited bare | GDS-05 §4, same tag (`FR-4710` and `FR-4720`: `FR-W7`) | confirmed | `requirements/01`; `FR-4110`, `FR-4210`, `FR-4310`, `FR-4410`, `FR-4510`, `FR-4610`, `FR-4710`, `FR-4720` |
| `build-spec/02` §5.5 `FR-S1`–`S3` | GDS-05 §5, same tag | confirmed | `requirements/01`; `FR-5310` |
| `build-spec/02` §5.6 `FR-L1`–`L2` | GDS-05 §6, same tag | confirmed | `requirements/01`; `FR-7110` |
| `build-spec/02` §6 `OR-1`–`OR-6` | GDS-05 §7, same tag | confirmed | `requirements/01`, GDS-05; `FR-3520`, `FR-6510`, `FR-6610` |
| `build-spec/02` §5–6 as a whole | GDS-05 (its "Relationship to other requirement artifacts" table needs rule (b)) | confirmed | 7 for the whole file (GDS-05, GDS-10, architecture index, ROADMAP, FS-135, `requirements/01`, `requirements/02`) |
| `build-spec/03` §7 (architecture, technology choices, 2D views, time) | GDS-03 §1–§4; ADR-0020 for §7.2 | confirmed (GDS-03 merge gate; its Open Question 1 records the stale PyQt text) | GDS-00, GDS-03, architecture index, ROADMAP; none |
| `build-spec/03` §8.1–§8.3 (vignette file, template libraries, action log) | GDS-07 §5 (vignette file), §3 (event log); templates were not built (GDS-07 "Departures", ADR-0036) | partial (GDS-07's merge gate names `design/04` only) | `docs/vignettes/00-LIBRARY-ARCHITECTURE.md` (file cited bare); none |
| `build-spec/03` §8.4 (TLE and Space-Track) | GDS-02 §4; GDS-05 `FR-S2`; ADR-0018 | confirmed | GDS-03; none |
| `build-spec/04` §9 `NFR-1`–`NFR-10` | GDS-06, same tag number (already first on each leaf's line: remove the legacy citation) | confirmed | `requirements/02`, GDS-06, GDS-10, architecture index, ROADMAP; `NFR-1100`, `NFR-1200`, `NFR-1500`, `NFR-1600`, `NFR-1900`, `NFR-2100`, `NFR-2200`, `NFR-2400`, `NFR-2900`, `NFR-3000`, `NFR-3100`; candidates `CNFR-02`, `CNFR-03` |
| `build-spec/04` §10 (phase plan M0–M8, demo and v1 definitions of done) | see decision §8.3(2): no migration; `M7` content = GDS-06 NFR-12 + GDS-05 `FR-L1`/`FR-L2`; `P6`/`M6` TLE force-add = GDS-05 `FR-S2` | confirmed for the cited rows | GDS-05, `requirements/02`, R133; `NFR-2500` (both successors are already on its line) |
| `build-spec/04` §11 (risks) | GDS-01 §12 | confirmed for the rows cited (UI stall, Space-Track, orbit credibility); the scope-creep and single-maintainer rows are not carried and nothing cites them | GDS-01, GDS-02, architecture index, ROADMAP; `NFR-1100` |
| `build-spec/04` §12 (glossary) | `docs/master/MSTR-004-glossary.md` §2, after migration §8.2(1) | partial: 8 of 15 terms are missing | MSTR-004; none |
| `build-spec/05` §13 (workflows) | GDS-01 §5 (13.1–13.2), §6 (13.3–13.5); GDS-08 §7 | confirmed | GDS-01, architecture index, ROADMAP; none |
| `build-spec/05` §14 (state machines) | GDS-01 §7 (verbatim); as-built order statuses in GDS-07 "Departures" | confirmed | GDS-01; none |
| `build-spec/06` §15 (test plan; file cited bare) | GDS-06 NFR-7 (already on the line); GDS-10 §3 (permanent gates) | confirmed for the leaf's content; the per-layer test list is not carried and nothing cites it | `requirements/02`, ROADMAP; `NFR-2800` |
| `build-spec/07` §16.1–§16.8, §16.12–§16.14 (console) | GDS-08 §1–§8 (section map in its merge gate); for operators, `docs/training/10-ui-reference.md` | confirmed | 12 for the whole file (GDS-08, GDS-10, architecture index, code map, ROADMAP, DOM-003, DOM-007, `research/04`, `training/10`, `10a`, `10b`, training index); none |
| `build-spec/07` §16.9 (button-state contract) | GDS-08 §6 | confirmed | code only (3 files) |
| `build-spec/07` §16.10 (catalog verbs) | as `design/13` below | partial | GDS-08 |
| `build-spec/07` §16.11 (data and API binding) | GDS-09 §3 | confirmed | GDS-08 |
| `build-spec/08` §17 (mock SSN) | GDS-03 §2.3; GDS-04 §1.13; `FR-3210`, `FR-3220`; FS-104 | partial: the preset table (§17.3), processing delays (§17.6) and capacity rule (§17.8) exist only in `spacesim/engine/ssn.py` | GDS-02, GDS-03, GDS-04, code map, strategic assumptions register, ROADMAP; none |
| `design/01` | GDS-03 §1–§4 | confirmed (merge gate) | GDS-03, GDS-10, architecture index, ROADMAP, MSTR-002, MSTR-005; none |
| `design/02` (tech stack) | ADR-0020; GDS-03 §2 "Likely implementation technologies" | partial | GDS-03, ROADMAP; none |
| `design/03` §1–§7 (engine) | GDS-03 §2.1, §4; §7 (save and replay) = GDS-07 §3, §6 | partial | ROADMAP; code only otherwise (5 files) |
| `design/04` §1–§9 | schema: GDS-07 (§1→§1; §2–§5→§2; §6→§5; §6.5→§2 and "Departures"; §7→§3, §6; §8→§9; §9→§10). Concept: GDS-04 (§2→§1.3; §3→§1.2, §1.4, §1.5; §4→§1.8; §5→§1.9; §6→§1.1, §1.12; §6.5→§1.7; §7→§1.14; §8→§1.11; §9→each entity's "Constraints") | confirmed | 11 (GDS-04, GDS-07, GDS-10, architecture index, ROADMAP, MSTR-005, `research/05`, `requirements/01`, IP-1151, IP-1171, IP-1172); `FR-1460`, `FR-5311`, `FR-5312` (all §9 → GDS-07 §10) |
| `design/05-cell-interfaces` | GDS-08 §4–§7 (fog and attribution §5; White view §7.6) | confirmed (merge gate) | GDS-08, architecture index, ROADMAP; none |
| `design/05-interface-control-document` (`INT-0001`…`INT-0016`, §4, §7 issues 4–14) | the same file, moved: decision §8.3(1) | confirmed | 75 name it or "ICD"; 128 use an `INT-` ID; `FR-3220`, `FR-5110`, `FR-6110`, `FR-6210`, `FR-6510`, `FR-7210`, `FR-7220`, `FR-7310`, `FR-8110`, `FR-9110`; candidate `CNFR-07` |
| `design/06` §1–§5 (White Cell controls) | GDS-08 §7.1, §7.6 and "Departures"; dials for operators: `docs/training/12-white-cell-manual.md` | partial (§2–§5 per the merge gate; §1 dials not checked line by line) | GDS-08, GDS-10, architecture index, ROADMAP; none |
| `design/07` §1–§6 | GDS-09 (§1–§2→§1–§2; §3→§5; §4→§1, §4; §5→§6; §6→§7) | confirmed | GDS-09, GDS-10, architecture index, ROADMAP, `requirements/01` (candidate `CR-03` text), work breakdown, IP-1072; none |
| `design/09` §1–§7 (GUI principles) | GDS-08 (§1→§1; §2→§2; §3→§5; §4→§6–§7; §5→§8, §4; §6→§2; §7 dropped as history); GDS-06 NFR-9 | confirmed | GDS-08, GDS-10, architecture index, ROADMAP, DOM-007, `requirements/02`; `NFR-3000` (GDS-06 NFR-9 is already on its line; add GDS-08 §2, §8) |
| `design/10` §1–§8 (3D viewer) | GDS-08 §5 (§7→§3) | confirmed (merge gate) | GDS-08, architecture index, ROADMAP; none |
| `design/11` (planning and tasking) | GDS-04 §1.7 (Part A), §1.5 and §1.13 (Part B); GDS-08 §7.2, §7.5 | confirmed for Part A, partial for Part B | GDS-04, ROADMAP; none |
| `design/12` (safe-mode loop); also the broken link `build-spec/03-safe-mode-loop.md` in `research/03` | GDS-05 `FR-B5`; GDS-01 §7 (bus-mode state machine); leaf `FR-2510`; dials: `docs/training/12-white-cell-manual.md` | partial: the §6 formulas exist only in `spacesim/engine/effects.py` and `recovery.py` | GDS-05, `requirements/01`, `research/03`, ROADMAP; `FR-2510` (GDS-05 `FR-B5` replaces both legacy citations on its line) |
| `design/13` (command catalog) | no document; the as-built catalog is `spacesim/engine/buscommands.py` (code map), with verb scope in ADS-3500 and parameters in R137 | partial; no requirement cites it | GDS-08 (its merge gate says the catalog "stays with `design/13` and the code": reword to "the code"), ROADMAP |
| `design/14` (delta-v economy) | GDS-05 `FR-E5`; leaves `FR-1310`, `FR-1320`; reference numbers in R112 | partial | GDS-05, feature review, `requirements/01` (`FR-1310` Rationale names the title: see §8.5 finding 5), ROADMAP |
| `design/15` (worked asset templates) | none wanted: templates were not built (ADR-0036; GDS-07 "Departures") | confirmed | ROADMAP only |
| either folder cited as a whole (index files, "the build spec", `design/`) | `docs/architecture/INDEX.md` | confirmed | 45 (build-spec) and 55 (design), among them `CLAUDE.md`, `README.md`, ROADMAP, the docs index, MSTR-001, -002, -004, -005, -006, four skill files, the research index, R313, R314, DOM-009 |

45 cited sections: 33 confirmed, 11 partial (one of them, the glossary, needs a migration first),
1 with no successor (none wanted). The Interface Control Document moves rather than migrates.

### 8.2 Migrate first

1. **Glossary.** From `build-spec/04` §12 into `docs/master/MSTR-004-glossary.md` §2, wording kept,
   the eight terms that have no row there: Bus, ECI / RIC, Hot seat, ISL, PlannedActivity, Payload,
   SDA, TLE. Add "(as built: `engine/orders.py::Order`; GDS-07 Departures)" to PlannedActivity.
   Then reword MSTR-004 §1, which says the build-spec glossary "remains authoritative".
2. Nothing else. The partial rows lose design detail that no live document relies on and that the
   code states as built; migrating it would restate text nobody has checked against the code.

### 8.3 The two decisions

1. **Interface Control Document: `git mv` to `docs/architecture/interface-control-document.md`,
   unnumbered, listed in the architecture index beside the code map.** It is not merged into GDS-07
   or GDS-09. Reasons: its sixteen `INT-` IDs are cited by 128 live documents (99 "Related
   Interfaces" fields in `requirements/01`, every FS, 60 packages), and GDS-09 carries only
   `INT-0001`–`INT-0006` while GDS-07 carries none; GDS-09's merge gate already decided "companion
   inventory, moved under `docs/architecture/`"; and it says of itself that it is "a leaf reference,
   not a ladder rung", so it takes no GDS number. B1 does the move and repoints the file's own
   links (its eight mentions of `design/04` and `design/07` become GDS-07 and GDS-09; its
   `../architecture/` links become siblings). The fuller re-issue against GDS-07/09 stays open as
   `03` work: B1 closes only the "move" half of `BL-0294`. Declare the old path as its own row in
   "Retired documents" with the new path as successor.
2. **Phase plan (`build-spec/04` §10): not migrated; it retires with the folder.** Reasons: every
   milestone M0–M8 is done and the plan steers nothing; current release state lives in
   `docs/feature-planning/01-release-plan.md` ("Release state") and `docs/releases/release-1.0.md`,
   package state in the Master Build Plan, and the one unfinished item (the high-fidelity
   propagator of M7) is row F-38 of the Release 2.0 plan; only one requirement cites it
   (`NFR-2500`, "§10 M7") and that line already names the two sections that carry the content.
   Copying a finished plan into a live document would create a second status ledger just before A3
   reduces them to one. Git history and `archive/release-1.0` keep the text (owner decision 3).

### 8.4 Code files that cite either folder (for C4; not edited by B1)

26 files, not the seven the B1 text expects; `tools/` has none.
`spacesim/content/vignette.py`; `spacesim/engine/`: `access.py`, `buscommands.py`, `clock.py`,
`custody.py`, `effects.py`, `entities.py`, `eventlog.py`, `orbit.py`, `orders.py`, `propagator.py`,
`recovery.py`, `world.py`; `spacesim/session/`: `__init__.py`, `api.py`, `cells.py`,
`inprocess.py`, `manager.py`, `redai.py`, `scene.py`; `spacesim/ui_web/__init__.py`;
`spacesim/ui_web/static/app.js` (lines 81 and 195; the second uses the pre-split name
`00-BUILD-SPECIFICATION.md`); `spacesim/tests/`: `test_bus_commands.py`, `test_import_guard.py`,
`test_validate_order.py`, `test_ssn.py` (uses the pre-split name `docs/SSN-DESIGN.md`).

**B1d recount (2026-11-16, after the deletion).** 38 comment lines in 28 files still cite either folder
or a retired basename (`tools/` has none). The two files not in the list above are `spacesim/engine/bus.py`
(line 1, `12-safe-mode-loop.md` §8: use GDS-05 `FR-B5`) and `spacesim/engine/ssn.py` (three lines, the
pre-split `docs/SSN-DESIGN.md`: use GDS-03 §2.3 and GDS-04 §1.13; the preset table, delays and capacity rule
exist only in this file). C4 uses both lists. The earlier estimate of about 41 lines in 7 files could not be
reproduced; the six-file figure in the release plan and the seven in B1 item 5 are likewise superseded by this count. Most are
bare basenames in module docstrings (`04-data-model.md` §3), which a search for the folder name
misses. C4 uses the table above: for example `07-operator-console.md` §16.9 becomes GDS-08 §6.

### 8.5 Findings that affect B1

1. **No requirement is left without a source.** Every baseline leaf that cites either folder has a
   confirmed successor, and for all but `FR-1460`, `FR-5311`, `FR-5312` (→ GDS-07 §10) and the ICD
   citations (path change only) the successor is already on the same line.
2. **Hidden dependency on `design/04`: 28 citations written "GDS-04 §3", "§6.5", "§7", "§8", "§9"
   or "§10" in `requirements/01` use `design/04`'s section numbers.** GDS-04 has no such sections
   (its §3 is the forward-looking list). In *Source documents* lines: `FR-1310`, `FR-2110`,
   `FR-2210`, `FR-2310`, `FR-2510` (§3); `FR-3110`, `FR-3120`, `FR-3310`, `FR-3410` (§6.5);
   `FR-7110` (§7); `FR-4610`, `FR-6210` (§8); the rest are in Rationale text and the candidate
   list. A search for the folder names does not find them, and once `design/04` is gone nothing
   resolves them. B1 corrects the Source-line ones with the `design/04` row above (GDS-04 column:
   §3→§1.2, §6.5→§1.7, §7→§1.14, §8→§1.11, §9→the entity's "Constraints"; "GDS-04 §10 Open
   Question n" → GDS-04 "Open Questions" n). The Rationale ones are outside B1's permitted edit
   (stop condition 4 does not apply, since the check does not police them): list them for the `04`
   owner in the pull request.
3. **B1's "done when" is wrong about the link allow-list.** Only one of its 36 lines is a link into
   either folder (line 11, `research/03` → `build-spec/03-safe-mode-loop.md`, a file that never
   existed; repoint it per the `design/12` row and delete the line). The other 35 are broken links
   inside the research primers, tagged with the same note; they are `BL-0422` and stay.
4. **`CNFR-05` (excluded candidate) has no successor for its source and its reason is stale:** it
   cites the v1 deferral of save and resume, which has since shipped (FS-110). B1 rewords the
   Source line to "the retired v1 build specification §3.2 (deferred list)" and files a backlog row
   for `04` to re-examine the candidate; it does not reword the "Why excluded" text.
5. **Two requirement texts outside the Source line name a retired file:** `FR-1310` Rationale
   (the title `14-delta-v-economy.md`) and `requirements/01`'s `CR-03` (`design/07-api-and-networking.md`).
   Both are short forms the retired-documents check does not police (it matches the declared
   `docs/…` path), so they do not block B1; list them for `04` with finding 2.
6. **The check polices only the full `docs/…` form.** Most citations are short forms (`build-spec/04`
   §9), so the retirement loop's step 4 search is where nearly all of B1's work is found, not the
   test output. Search for both folder names, all 23 file basenames, and `ICD`.
7. **Frozen records link to the ICD's old path** (9 files under `docs/reviews/`,
   `docs/implementation/verification/` and the ADRs, including the ADR index's link to
   `build-spec/01` §4). They are not edited; if the link check reports them, hand back to Tier A
   rather than adding allow-list lines.
8. **Packages that record edits to the retired files** (IP-1151, IP-1171, IP-1172 on `design/04` §6;
   IP-1160, IP-1173, IP-1180, IP-1210, IP-1280 on the ICD): the content they added is carried
   (`roles_needed`, the payload sub-models and `roe` are in GDS-07 §5). Repoint the ICD ones to the
   new path; reword the `design/04` ones under rule (b).

## 9. A5 split plans

One subsection per file. A5a is `session/manager.py` and A5b is `engine/orders.py`;
`ui_web/server.py` and `static/app.js` (A5c, A5d) are not planned yet. Line numbers are `main` at
`f49f710` (§9.1) and `a6c085c` (§9.2).

### 9.1 `session/manager.py` (1,917 lines)

#### 9.1.1 Responsibility inventory

| Lines | What | Owns |
|---|---|---|
| 34 | `BUS_TICK_PERIOD_S` | Tick period of the bus, condition-check and anomaly grids. Imported from here by `session/ephemeris.py` and 6 test files. |
| 36–46 | `ROLE_SCOPE_BY_VERB` | Verb → `bus` / `payload` role table (imported by 2 test files). |
| 48–142 | `INJECT_EFFECT_TYPES`, `_INJECT_REQUIRED_KEYS`, `_MANEUVER_MODES`, `_inject_effect_problem`, `validate_inject_effects` | Inject validation. Pure; called at the White boundary and inside the replayed handler. |
| 145–194 | `_is_int`, `_row_problem`, `SUPPORTED_SAVE_FORMATS`, `SAVE_FORMAT` | Save row checks and the format gate. |
| 198–203, 1270 | `MAX_EVENTLOG_REPLAY_ENTRIES`, `MAX_CLOCK_RATE`, `MAX_SAVE_SPAN_US` | Class constants, read as `SessionManager.X` by tests, `session/aar.py` and `inprocess.py`. |
| 205–303 | `__init__` | Builds the world, `Simulation`, `OrderSystem`, `BusSystem`, `RecoverySystem`, `SSNSystem`; **registers the four session handlers**; lock and lazy-clock fields. |
| 306–387 | `assign_role`, `_role_covers`, `_entry_covers`, `_roles_needed_covers`, `role_scope_check`, `role_scope_for`, `_role_refusal`, `staffing_report` | Seat-to-role bindings and the role gate (`FR-3510`/`FR-3520`/`FR-4210`). Reads only. |
| 390–453 | `start`, `_arm_schedule` | Lifecycle; queues bus ticks, condition and anomaly checks, scripted injects; re-arms after a rewind from the retained log. |
| 456–503 | `_span_ceiling`, `_require_finite`, `step`, `_span_message`, `advance_to` | Manual time control and its bounds; re-anchors the lazy clock. |
| 505–603 | `set_clock`, `_catch_up_locked`, `_record_catch_up_lag`, `catch_up`, `clock_state` | The server-side lazy clock (the only wall-clock reads in the file) and the lag watchdog. |
| 605–665 | `rewind_to`, `undo_last`, `_rebind` | Rewind and undo; repoints `world`, clears order and SSN registries, rebuilds sensor bookings. |
| 668–698 | `issue_order`, `validate_order`, `_order_ack` | Order intents: role gate, then `OrderSystem`. |
| 700–853, 875–953 | `_authoring_problems`, `add_tle`, `_force_add_tle_object`, `_force_add_omm_object`, `bulk_import`, `save_as_scenario`, `add_ground_asset`, `creator_state`, `creator_set_state`, `creator_edit_asset`, `creator_delete_asset`, `creator_scene`, `declare_seats` | White force edits and the Vignette Creator. Each write re-baselines `sim._initial_state`. |
| 855–873, 956–1025 | `maneuver_ledger`, `list_orders`, `cancel_order`, `decide_gated_order`, `issue_roe_change`, `windows_ahead`, `next_contacts` | Queue reads (fog by owner) and three thin `OrderSystem` wrappers. |
| 1028–1086 | `_RECOVERY_STEPS`, `recovery_status`, `begin_recovery`, four `*ssn*` methods | Recovery strip and SSN wrappers. |
| 1088–1212 | `list_injects`, `_inject_overrides`, `_inject_applied`, `pending_injects`, `cancel_inject`, `edit_inject`, `_pending_row`, `_log_inject_admin`, `_h_inject_admin` | Pending-inject queue (`FR-4450`): state folded from `inject_admin` log entries; cancel and edit are logged events. |
| 1215–1440 | `save_state`, `_check_final_time_span`, `_eventlog_entry_count`, `validate_save`, `from_state` | Save, save validation, resume. |
| 1443–1500 | `alarms`, `fire_inject`, `_inject_effects` | Alarm rollup; the White inject entry point (immediate or future-dated). |
| 1503–1632 | `get_view`, `get_scene`, `get_ric_view`, `get_tle`, `_owns`, `get_telemetry`, `get_series`, `telemetry_export`, `get_godview`, `controller_view`, `get_eventlog`, `objectives` | Reads. `_owns` is the fog check for every per-asset read. |
| 1635–1917 | `_h_inject`, `_apply_inject_effects` (12 effect types), `_h_env_anomaly_check`, `_notice_by_owner`, `_skip_inject_effect`, `_fired_condition_inject_ids`, `_condition_inject_already_fired`, `_h_condition_check` | The replayed handlers and the effect dispatch. |

**Who reaches in** (`git grep`, outside `manager.py`):

- `inprocess.py` calls 60 public methods and reads `world`, `sim`, `osys`, `ctx`, `vignette`,
  `classification`, `started`, `seats_declared`, `load_warnings`, plus the private `_lock`,
  `_catch_up_locked()` and `_clock_running`. `server.py` never touches the manager directly.
- `aar.py`, `ephemeris.py` and `assessment.py` take the manager as an argument and read `sim`,
  `ctx`, `osys`, `world`, `vignette`, `objectives()`, `MAX_SAVE_SPAN_US`; `aar.py` replays with
  `mgr.sim.handlers()`, so the registered callables run against worlds that are not `mgr.world`.
- Tests read or set `_clock_running`, `_wall_anchor`, `_sim_anchor`, `_rate`,
  `_catch_up_lag_history`; call `_record_catch_up_lag`, `_apply_inject_effects` (3 files),
  `_h_inject`, `_force_add_omm_object`; write `sim._initial_state`; patch
  `SessionManager.validate_save` and `manager._time.time`. `tools/render_manual.py` calls `_h_inject`.
- Imported from the module: `SessionManager`, `BUS_TICK_PERIOD_S`, `ROLE_SCOPE_BY_VERB`,
  `INJECT_EFFECT_TYPES`, `validate_inject_effects`.

#### 9.1.2 Target modules

All six are new files under `spacesim/session/`. `SessionManager` keeps every method name it has
today; a moved method becomes a one-line delegate (`return reads.get_series(self, …)`).

| Module | Moves in | Stays on `SessionManager` |
|---|---|---|
| `role_scope.py` | `ROLE_SCOPE_BY_VERB`; bodies of `_role_covers`, `_entry_covers`, `_roles_needed_covers`, `role_scope_check`, `role_scope_for`, `staffing_report` | The delegates; `assign_role`, `_role_refusal`; the `role_assignments` and `seats_declared` attributes. |
| `inject_effects.py` | Lines 48–142 whole; `_apply_inject_effects` as `apply_inject_effects(world, effects, rng, prop)`; `_notice_by_owner`; `_skip_inject_effect` | `_apply_inject_effects(world, effects, rng)`, which passes `self.osys.prop` (read at call time). The two static helpers have no outside caller and are not kept. |
| `inject_queue.py` | `list_injects`, `_inject_overrides`, `_inject_applied`, `pending_injects`, `cancel_inject`, `edit_inject`, `_pending_row`, `_log_inject_admin`, `fire_inject`, `_inject_effects`, `_fired_condition_inject_ids`, `_condition_inject_already_fired`; the bodies of the four handlers (§9.1.3) | The delegates for the five public methods; the four `_h_*` methods; the `_white_inject_seq` attribute. |
| `saves.py` | `_is_int`, `_row_problem`, `SAVE_FORMAT`, `SUPPORTED_SAVE_FORMATS`; bodies of `validate_save`, `_check_final_time_span`, `_eventlog_entry_count`, `save_state` | `validate_save` as a `staticmethod` delegate (a test patches it on the class; `inprocess.py` calls it on the class); `save_state`; **`from_state` whole**; the three class constants, which the delegate passes in as arguments. |
| `force_edit.py` | Bodies of the 13 force-edit and Creator methods (lines 700–853, 875–953) | The delegates for the 10 public methods and `_force_add_omm_object` (a test calls it). |
| `reads.py` | `_owns`; bodies of `get_telemetry`, `get_series`, `telemetry_export`, `alarms`, `windows_ahead`, `next_contacts`, `maneuver_ledger`, `list_orders`, `recovery_status`, `get_ric_view`, `get_tle`, `controller_view`; `_RECOVERY_STEPS` | The delegates. `get_view`, `get_scene`, `get_godview`, `get_eventlog`, `objectives` are one line each and do not move. |

After the six moves `manager.py` is about 800 lines: `__init__`, lifecycle, time control, the lazy
clock, rewind and undo, order intents, `from_state`, the SSN and recovery wrappers, and delegates.

Rules for every move:

1. **Functions that take the manager, not helper objects.** Each moved body becomes a module-level
   function whose first parameter is the manager (`aar.worlds_at_times(mgr, …)` is the existing
   pattern). Nothing is captured at construction: `from_state` replaces `sim.eventlog`, and
   `Simulation._rebuild` replaces `sim.world`, `sim.rng` and `sim.scheduler`, so a cached reference
   goes stale without failing.
2. **Copy each read exactly.** `self.world`, `self.sim.world` and a handler's `world` argument are
   different objects during replay. Do not tidy one into another.
3. **No new module imports `spacesim.session.manager` at run time** (`TYPE_CHECKING` only).
   `ephemeris.py` already imports `BUS_TICK_PERIOD_S` from it, and the manager imports `aar` and
   `ephemeris` inside functions; every function-local import stays function-local.
4. **Names imported from the module stay importable from it:** the manager re-imports
   `ROLE_SCOPE_BY_VERB`, `INJECT_EFFECT_TYPES` and `validate_inject_effects`. `BUS_TICK_PERIOD_S`
   and `manager._time` do not move.
5. **Bodies move verbatim,** comments included; error strings are asserted by tests.
   Package-history comments move with their code (§9.1.6).

#### 9.1.3 Registered handlers

`Simulation` holds one callable per kind and calls it live, in `_rebuild` (rewind, undo, resume),
in `_record_failed_event`, and in every `replay(…, handlers=sim.handlers())` (`aar.py`, tests).

- **What is registered does not change.** `__init__` keeps its four `register_handler` lines where
  they are: `inject`, `condition_check`, `inject_admin`, then `OrderSystem` and `BusSystem`, then
  `env_anomaly_check`, then `RecoverySystem` and `SSNSystem`. The callables stay the bound methods
  `self._h_inject`, `self._h_condition_check`, `self._h_inject_admin`,
  `self._h_env_anomaly_check`. Registering a module function or a `partial` is rejected: it
  changes `sim.handlers()` and breaks the callers of `mgr._h_inject`.
- **Only the bodies move.** Each method becomes
  `inject_queue.h_inject(self, world, payload, rng)` and so on. The moved body:
  - mutates the **same** `payload` dict it was handed (`payload["skipped"]`, `payload["fired"]`);
    `Simulation.advance_to` appends that object to the log after the handler returns. No copy, no
    rebuilt dict, no changed key order inside `fired` rows (`inject_id`, `value`; `asset`, `p`);
  - reads `mgr.sim.eventlog`, `mgr.vignette`, `mgr.ctx` and `mgr.osys.prop` at call time, and
    state only from its `world` argument, never `mgr.world`;
  - applies effects through `mgr._apply_inject_effects(world, …, rng)`, as now;
  - in `h_env_anomaly_check`, draws `rng.random()` once per listed asset **before** any skip, and
    receives the tick period as an argument (`BUS_TICK_PERIOD_S` stays in `manager.py`).
- **`_h_inject_admin`** is nine lines and need not move; it goes with the others only to keep the
  four together.
- **`apply_inject_effects`** keeps the branch order of the 12 effect types, each
  `world.messages.append` in place, and the `continue` inside the `scripted_manoeuvre` `except`.

#### 9.1.4 The moves, in order: invariant, check and tier

One move per pull request, smallest and safest first. **Every move** runs the whole suite, and:
the baseline file is byte-identical (`git diff --exit-code spacesim/tests/baseline/`);
`test_determinism.py` and `test_import_guard.py` pass; no test file is in the diff;
`sorted(dir(SessionManager))` and the module's public names are the same before and after;
`git diff --color-moved=dimmed-zebra` shows moved lines plus delegates and nothing else; a save
written on `main` before the move loads after it and continues to the same world. "Opus" below
means the tier under Tier A can do it against these checks; A6 still assigns it.

| # | Move | Could break | Tests that judge it (beyond the baseline) | Tier |
|---|---|---|---|---|
| 0 | **Tests first** (tests only): the three pins in §9.1.5 | Nothing; it makes moves 5, 7 and 8 judgeable | Itself | Tier A: it defines what the later moves are judged by |
| 1 | `role_scope.py` | Role gate order (ownership before role; a missing seat skips the gate); fog in `role_scope_for` | `test_role_scope_enforcement.py` (29), `test_session_setup.py`, `test_role_scope_console_static.py` | Opus: pure reads, no log, no clock |
| 2 | `reads.py` | Fog: `_owns` must stay the first statement of each per-asset read; White reads through `get_godview()`; `get_series` must keep replaying, not back-dating | `test_telemetry.py` (26), `test_queue.py`, `test_recovery_session.py`, `test_session_features.py`, `test_ephemeris.py`, `test_controller_view.py`, `test_defensive_audit_2026.py` (fog endpoint matrix), `test_web.py` | Opus: read-only and mechanical |
| 3 | `force_edit.py` | The `started` guard; the re-baseline of `sim._initial_state` straight after each write (rewind and the save's content portion depend on it); all-or-nothing `creator_set_state` | `test_vignette_creator_session.py`, `test_vignette_creator_ui.py`, `test_authoring_boundary_validation.py` (27), `test_bulk_import_session.py`, `test_self_contained_save.py` | Opus: mechanical; the baseline is blind here, the named tests are not |
| 4 | `saves.py`, validation half (`validate_save` and its helpers) | Which refusal wins (check order); the class constants; the class-level patch point | `test_save_load_robustness.py` (22), `test_save_format_gate.py`, `test_save_eventlog_cap.py`, `test_undo_clock_floor.py`, `test_defensive_audit_2026.py` | Opus: one pure function |
| 5 | `saves.py`, `save_state` body | The save's keys and content (pre-start edits, force-added assets); old saves | Baseline save → reload → continue; `test_self_contained_save.py` (12); move 0's key pin | Opus, after move 0 |
| 6 | `inject_effects.py` | Replay: branch order, message order, `prop` read at call time, `rng` handed through; validation shared by the boundary and the handler | `test_inject_effects_v2.py` (20), `test_inject_library.py`, `test_inject_notice_fog.py`, `test_space_weather_index.py` | Opus with Tier A reading the diff: verbatim, but it runs inside replay and the baseline fires only some of the 12 types |
| 7 | `inject_queue.py`, queue half (everything but the handler bodies) | Event-log contents: `rev` numbering, `white-<n>` handles, schedule-then-`advance_to(now)` order, `self.world` reassigned after it; `_arm_schedule` re-arms from these folds | `test_pending_inject_queue.py` (19), `test_inject_rewind_rearm.py` (22), `test_activity_fog_matrix.py` | **Tier A only:** it writes the log, and a wrong `rev` or handle passes the baseline |
| 8 | `inject_queue.py`, the four handler bodies | Everything in §9.1.3 | `test_condition_triggered_injects.py`, `test_space_weather_index.py`, `test_failure_atomic_events.py`, `test_aar.py`; move 0's registry pin | **Tier A only:** the baseline never runs two of the four handlers |

Moves 1 to 5 are genuinely mechanical. Move 6 is mechanical in a dangerous place. Moves 7 and 8
are the risky ones; if the owner wants the smallest safe refactor, stop after move 6
(`manager.py` is then about 1,000 lines).

#### 9.1.5 What the baseline does not cover

The baseline loads, starts, orders, cancels an order, submits an SSN request, fires one immediate
and one future-dated inject, changes ROE, steps, saves, reloads and replays. It does **not** run:

| Not in the baseline | Covered by |
|---|---|
| `_h_condition_check` and `_h_env_anomaly_check` (no library vignette declares either) | `test_condition_triggered_injects.py`, `test_space_weather_index.py` (both assert `fired` and replay equality) |
| A skipped inject (`payload["skipped"]`), edit and cancel of a pending inject | `test_pending_inject_queue.py` |
| Rewind and undo, and the re-arm after them | `test_inject_rewind_rearm.py`, `test_undo_clock_floor.py`, `test_time_advance_bound.py`, `test_condition_triggered_injects.py` |
| The role gate (the script names no operator seat) | `test_role_scope_enforcement.py` |
| Force edits and the Creator | Move 3's tests |
| Save refusals, legacy saves | Move 4's tests, `test_self_contained_save.py` |
| Per-asset reads (telemetry, series, export, windows, ledger, recovery) | Move 2's tests |
| The FR-4430 effect types, `reveal_asset`, `conjunction_warning`, `spawn_debris` unless a vignette fires them in two hours | Move 6's tests |
| The lazy clock (frozen by design) | `test_web.py`, `test_white_control_correctness.py`, `test_clock_lag_watchdog.py`; nothing moves |
| **The handler registry:** kinds, order, owning object and method name of every `sim.handlers()` entry | **Uncovered: needs a test first** (move 0) |
| **The save's top-level keys and their order** | **Uncovered: needs a test first** (move 0) |
| **`get_series` for another cell's asset returns `None`** at the manager | **Uncovered: needs a test first** (move 0); the other per-asset reads each have one |

#### 9.1.6 Do not move

| Stays in `manager.py` | Reason |
|---|---|
| `__init__` | Construction order is registration order, and `OrderSystem`, `RecoverySystem` and `SSNSystem` share `osys.access_config`. |
| `start`, `_arm_schedule` | The tick grids' anchor, the `>=` / `>` asymmetry between first arm and re-arm, and the no-double-fire rule live in one place; the baseline only sees the first arm. |
| `set_clock`, `_catch_up_locked`, `_record_catch_up_lag`, `catch_up`, `clock_state`, the anchor fields, `_lock`, `import time as _time` | The only wall-clock reads. Tests set the five fields and patch `manager._time.time`; `inprocess.py` takes `_lock` and calls `_catch_up_locked`. A clock object would need a property shim per field and buys nothing. |
| `step`, `advance_to`, `rewind_to`, `undo_last`, `_span_ceiling`, `_span_message`, `_require_finite` | Each re-anchors the lazy clock after moving time; refusal must come before any state change. |
| `_rebind` | It reaches into private registries of `OrderSystem` and `SSNSystem`; it belongs with their owner until A5b decides `orders.py`. |
| `from_state` | Its order is the resume contract: install the log, `_rebuild`, `_rebind`, pending events, orders and counters, SSN, the inject handle counter. It calls `cls(…)`. |
| `issue_order`, `validate_order`, `_order_ack`, the `OrderSystem`, SSN and recovery wrappers, `begin_recovery` | Already thin; `issue_order` is where the role gate meets the engine. |
| `BUS_TICK_PERIOD_S`, the three class constants | Imported or read from here by `ephemeris.py`, `aar.py`, `inprocess.py` and tests. |

**Ruling for C4:** package-history comments (`IP-xxxx`, `BL-xxxx`) stay and move with their code;
no move edits a comment.

### 9.2 `engine/orders.py` (1,285 lines)

#### 9.2.1 Responsibility inventory

| Lines | What | Owns |
|---|---|---|
| 43–57 | `ACTION_CHANNEL`, `MAX_COMMANDS_PER_PASS` | Action → access channel (`None` = cyber, not window-gated); the per-pass uplink cap (imported by `test_queue.py`). |
| 59–163 | `OBSERVE_NUMERIC_PARAMS`, `_requested_beam_mode`, `_observe_params_ok`, `ORDER_PARAM_RULES`, `_finite_float_ok`, `_param_value_ok`, `_order_params_ok`, `_engage_rounds` | Pure param checks. The two `*_params_ok` functions **delete `None` keys from the order's own `params` dict**, for `dry_run` and `issue` alike. |
| 166–175 | `BAR_DURATION_S` | Gantt bar widths: display data, imported inside a function by `inprocess.py`. |
| 178–190 | `Order` | The order record. Imported by 37 files; a save restores it with `Order(**row)`. |
| 193–203 | `scene_from_world` | World → access `Scene`, dropping degraded sites and sensors. Imported at module level by `ssn.py`, `recovery.py`, `manager.py`, `engine/__init__.py` and 3 test files. |
| 207–256 | `OrderSystem.__init__` | The state (`roe`, `_static_roe`, `resolver`, `prop`, `access_config`, `horizon`, `wq_threshold`, `auto_cue_ssn`, four booking dicts, `orders`, `_order_counter`, `gating_rules`, `_pending`) and **eight handler registrations**. |
| 259–301, 425–452 | `issue`, `dry_run`, `_plan`, `_continue_plan` | The pipeline: mint the id, validate, hold a gated order (appends `effect_gate_request`), dispatch by action, plan jam, engage and downlink inline. `commit` is the only difference between preview and issue. |
| 303–393 | `_order_classification`, `_matching_gate`, `rebuild_pending`, `decide_gated_order`, `_h_noop` | Effect gating (`FR-3430`): appends `effect_gate_decision`; rebuilds `_pending` from the log on resume. |
| 395–423 | `_effective_roe`, `_h_roe_change`, `issue_roe_change` | ROE (`FR-3440`): point-in-time value folded from `_static_roe` and the log's `roe_change` entries; the `self.roe` cache; appends `roe_change`. |
| 454–498 | `_release_bookings_on_execute`, `cancel` | Booking release on execute (from three handlers) and on cancel. The two are **not** symmetric: cancel leaves a zero count in `_pass_bookings`, execute removes the key. |
| 500–559, 752–763 | `_ap`, `_plan_command`, `_best_isl_window`, `_window_endpoints`, `_next_window` | Window search; the three delivery paths (stored program, ground uplink, ISL relay), earliest wins; the per-pass cap. |
| 561–662 | `_plan_collection`, `_candidate_sensors`, `_observe_payload_type`, `_observe_modes`, `_auto_blocked_by_cue`, `_contended`, `_resolve_sensor_id` | Sensor tasking: candidate choice, contention, bookings; adds `sensor_id` and `window_end` to the payload (`_rebind` rebuilds bookings from them). Sets `order.actor`, in preview too. |
| 665–750 | `_validate` | Refusal order: action, params, then observe rules or ownership, then per-action (ROE as of `issued_at`, ammo, weapons-quality track, Δv, verb, station). |
| 766–830 | `_observation_phase_angle_deg`, `_delivery_keys`, `_delivery_jammed`, `_jammed_record` | Phase-angle geometry; delivery-path keys written at plan time and read at execute time. |
| 832–1064 | `_exec_payload` | Builds the `(kind, payload)` the handler will receive, per action. Reads three different clocks: `order.issued_at` (custody confidence), `win.start` (phase angle), `self.world.now` (footprint). Called only when `commit`. |
| 1066–1120 | `_mark_cyber_queued`, `_plan_cyber` | Cyber: no window; builds the effect and schedules it at `clock.now`. |
| 1123–1285 | `_h_effect`, `_h_maneuver`, `_h_downlink`, `_h_command`, `_h_observe` | The replayed execute handlers. |

**Who reaches in** (`git grep`, outside `orders.py`):

- `manager.py` calls `issue`, `dry_run`, `cancel`, `decide_gated_order`, `issue_roe_change`,
  `rebuild_pending`; reads `orders`, `prop`, `access_config`; **writes** `world`, `auto_cue_ssn`,
  `_order_counter`; `_rebind` clears `orders`, `_pending` and the four booking dicts and refills
  `_sensor_bookings`. `inprocess.py` and `assessment.py` read `orders` and `prop`.
- `ssn.py` and `recovery.py` import only `scene_from_world`. `tools/render_manual.py` calls `_ap()`.
- Tests read or set `_pending`, the four booking dicts, `_order_counter`, `_static_roe`, `roe`,
  `prop`, `sim`, `world`, `auto_cue_ssn`; call `_effective_roe`, `_exec_payload`, `_ap`,
  `_h_maneuver`, `_h_command`; and one **patches `OrderSystem._exec_payload` on the class**
  (`test_order_param_hardening.py`). The string `_contended` in the baseline is the refusal reason
  `sensor_contended`, not the method.
- Imported from the module: `Order`, `OrderSystem`, `scene_from_world`, `MAX_COMMANDS_PER_PASS`,
  `BAR_DURATION_S`.

#### 9.2.2 Target modules

All five are new files under `spacesim/engine/`. `OrderSystem` keeps **every** method name it has
today, private ones included; a moved method becomes a one-line delegate
(`return order_planning.plan_command(self, order, commit)`).

| Module | Moves in | Stays in `orders.py` |
|---|---|---|
| `order_params.py` | Lines 43–163 whole: `ACTION_CHANNEL`, `MAX_COMMANDS_PER_PASS`, and the eight param names of §9.2.1. Imports `math`, `typing` and the channel constants from `access.py`; nothing else | A re-import of all ten names, so `orders.ACTION_CHANNEL` and `orders.MAX_COMMANDS_PER_PASS` still resolve. |
| `order_validation.py` | Bodies of `_validate`, `_resolve_sensor_id`, `_observe_payload_type`, `_observe_modes` (read-only; shared by validation, sensor choice and the observe payload) | The four delegates. |
| `order_payloads.py` | Bodies of `_exec_payload`, `_observation_phase_angle_deg`, `_delivery_keys` | The delegates; `_delivery_keys` stays a `staticmethod`. `_exec_payload` **must** stay a method: a test patches it on the class. |
| `order_planning.py` | Bodies of `_plan_command`, `_best_isl_window`, `_plan_collection`, `_candidate_sensors`, `_auto_blocked_by_cue`, `_contended`, `_window_endpoints`, `_next_window`, `_plan_cyber`, `_mark_cyber_queued` | The delegates; `_ap`; the four booking dicts (the moved planners write them through `osys`). |
| `order_handlers.py` | Bodies of the five execute handlers (§9.2.3); `_delivery_jammed`, `_jammed_record` | The five bound `_h_*` methods; the two `staticmethod` delegates. |

`order_params.py` is the leaf that validation, payloads and planning share; `order_handlers.py`
imports none of the other four. After the moves `orders.py` is about 480 lines: the re-import,
`BAR_DURATION_S`, `Order`, `scene_from_world`, `__init__`, `issue`, `dry_run`, `_plan`,
`_continue_plan`, gating, ROE, bookings release, `cancel`, `_ap` and the delegates.

Rules for every move:

1. **Functions that take the order system.** Each moved body becomes a module-level function whose
   first parameter is `osys`. The only edits to a body are `self` → `osys` and the dedent. The
   check is mechanical: dedent the new body, replace `osys` with `self`, and diff it against the
   old method; the diff must be empty.
2. **Every call to another `OrderSystem` method still goes through `osys.<name>(…)`,** never
   straight to the sibling module function. That keeps the class-level patch of `_exec_payload`
   working, and keeps each delegate the single way in.
3. **Read at call time; cache nothing.** `_rebind` replaces `osys.world`; `from_state` replaces
   `osys.sim.eventlog`; `Simulation._rebuild` replaces `sim.world`, `sim.rng`, `sim.scheduler`;
   the manager sets `osys.auto_cue_ssn` after construction. No helper object holds a reference.
4. **Copy each clock read exactly.** `osys.sim.clock.now`, `osys.world.now`, a handler's
   `world.now`, `order.issued_at` and `win.start` are five different things; `_exec_payload` uses
   three of them on purpose.
5. **Import boundary.** A new module imports only the standard library, NumPy and
   `spacesim.engine.*`; never `random`, `time`, `datetime`, `session`, `ui_web` or `content`
   (`test_import_guard.py` scans `engine/` recursively, so new files are covered without an edit).
   **No new module imports `spacesim.engine.orders` at run time** (`Order` and `OrderSystem` under
   `TYPE_CHECKING` only): `orders.py` imports them, and `ssn.py` and `recovery.py` import
   `orders.py` at module level.
6. **Function-local imports stay function-local,** each in the function it is in now. The
   `engine.ssn` import inside `_h_observe` is a real cycle (`ssn` → `orders` → handlers → `ssn`);
   the others (`jam`, `engage`, `cyber`, `isr`, `geometry`, `sun`, `orbit`, `bus`) are not, but
   hoisting them changes what loads when and is not a move. The unused `classify_regime` import in
   the engage branch moves too; packet C3 removes it, not a move.
7. **`commit` branches move whole.** No planner is split into a "compute" half and a "write" half:
   the order *payload → status → booking → schedule* inside each planner is what makes a failed
   payload leave nothing behind (`IP-1052` Design Decision 3).
8. **Bodies move verbatim,** comments included; refusal strings are asserted by tests and pinned in
   the baseline's acknowledgements. `engine/__init__.py` does not change. Each move adds its new
   module to `docs/architecture/code-map.md` in the same pull request.

#### 9.2.3 Registered handlers

`Simulation` holds one callable per kind and calls it live, in `_rebuild` (rewind, undo, resume),
in `_record_failed_event`, and in every `replay(…, handlers=sim.handlers())`. So a handler runs
against worlds that are not `osys.world`, with the session's own `OrderSystem` as `self`.

- **What is registered does not change.** `__init__` keeps its eight `register_handler` lines, in
  this order: `execute_effect`, `execute_maneuver`, `execute_observe`, `execute_downlink`,
  `effect_gate_request`, `effect_gate_decision`, `roe_change`, `execute_command`. The callables
  stay the bound methods `self._h_effect` and so on. A module function or a `partial` is rejected:
  it changes `sim.handlers()`, breaks the tests that call `osys._h_maneuver` and
  `osys._h_command`, and loses the instance state the handlers use.
- **`_h_noop` and `_h_roe_change` do not move** (§9.2.6).
- **Only the bodies of the five execute handlers move,** each to
  `order_handlers.h_effect(osys, world, payload, rng)` and so on. Every moved body:
  - takes world state only from its `world` argument, never `osys.world`; from `osys` it reads
    only `resolver`, `prop`, `auto_cue_ssn` and the three methods below, at call time;
  - keeps every `payload[...]` and `payload.get(...)` as written. `payload["actor"]` raises on a
    missing key and `payload.get("delivery_path") or "ground_uplink"` does not: that difference is
    how a payload saved before `IP-1085` or `IP-1320` still replays (no `delivery_path`, a stray
    `consume.power_w`);
  - passes the `rng` it was handed, untouched.
- **RNG.** Planning draws nothing. The only draws in the file happen inside
  `osys.resolver.resolve(effect, world, rng)` in `h_effect`. Its early return (ammo re-check
  failed) comes **before** that call and must stay before it: no resolution, no draw, nothing
  charged. The ammo charge stays **after** resolution. `issue_roe_change` hands `sim.rng` to
  `_h_roe_change`, which draws nothing; do not add a draw anywhere.
- **Payloads mutated in place.** `h_maneuver` writes `payload["applied"]`, then
  `payload["remaining_delta_v_ms"]`, on the **same** dict it was handed; `Simulation.advance_to`
  appends that object to the log after the handler returns, and the manoeuvre ledger reads it. No
  copy, no rebuilt dict. The other four do not write to `payload`; keep it so.
- **Bookings.** `h_maneuver`, `h_command` and `h_observe` call
  `osys._release_bookings_on_execute(payload.get("__order_id"))` as their **first** statement,
  before any early return. `h_effect` and `h_downlink` do not call it (jam, engage and downlink
  take no booking); do not add it. The call changes the live booking dicts even when the handler
  is replaying; that is today's behaviour.
- **`h_observe`'s auto-cue** calls `osys.auto_cue_ssn.submit_request(…)` from inside a handler:
  it mints an SSN request id and schedules events, live and in replay alike
  (`_record_failed_event` swaps in a scratch scheduler for this reason). Keep the call, its guard
  (`0.3 < confidence < 0.85`, not characterised, no open request) and its place at the end.
- **Plan-time payload keys are log content.** `__order_id`, `sensor_id`, `window_end`,
  `delivery_path`, `relay` and `custody_confidence_at_decision` are written by the planners and by
  `_exec_payload`, logged, and read back (`_rebind`, `assessment.py`, the handlers). Their names
  and the order they are added in do not change.

#### 9.2.4 The moves, in order: invariant, check and tier

One move per pull request, smallest and safest first. **Every move** runs the whole suite, and:
the baseline file is byte-identical (`git diff --exit-code spacesim/tests/baseline/`);
`test_determinism.py` and `test_import_guard.py` pass; no test file is in the diff;
`sorted(dir(OrderSystem))` is unchanged and every name in `dir(spacesim.engine.orders)` is still
there; rule 1's body diff is empty for every moved function; `import spacesim.engine.ssn`,
`import spacesim.engine.recovery` and `import spacesim.engine.orders` each succeed as the first
import of a fresh interpreter (the cycle check); a save written on `main` before the move loads
after it and continues to the same world. "Opus-safe" means the tier under Tier A can do it against
these checks; "Fable-only" means Tier A only. A6 still assigns each one.

| # | Move | Could break | Tests that judge it (beyond the baseline) | Tier |
|---|---|---|---|---|
| 0 | **Tests first** (tests only): the three pins in §9.2.5 | Nothing; it makes moves 2 to 6 judgeable | Itself | Fable-only: it defines what the later moves are judged by |
| 1 | `order_params.py` | The in-place `None` drop; names read as `orders.X` | `test_order_param_hardening.py` (12), `test_observe_order_remediation.py` (9), `test_effect_resource_bounds.py` (13), `test_queue.py` | Opus-safe: pure functions and two constants, no state |
| 2 | `order_validation.py` | Which refusal wins (check order); ROE read as of `order.issued_at` through `osys._effective_roe`; the weapons-quality check at `clock.now` | The baseline's 952 acknowledgements (nine refusal reasons); `test_orders.py` (26), `test_validate_order.py`, `test_beam_mode_modality.py`, `test_sensor_modality_wiring.py`, `test_bus_commands.py` (62), `test_content.py` | Opus-safe: read-only, and the baseline sees every refusal string |
| 3 | `order_payloads.py` | Derived probabilities and gain; the three clocks (rule 4); payload keys; the class-level patch point | `test_derived_probabilities.py` (13), `test_isr.py` (42), `test_phase_angle_gain.py` (14), `test_orders.py` (custody confidence, engage replay), `test_jam_delivery_paths.py`, `test_order_param_hardening.py` (the patch); move 0's key pin | Opus-safe with Tier A reading the diff: verbatim, but 230 lines of numbers and the baseline never builds an engage payload |
| 4 | `order_planning.py`, command half: `_plan_command`, `_best_isl_window`, `_window_endpoints`, `_next_window` | Earliest-wins and its tie-break (`min` keeps the first of stored, ground, ISL); the per-pass cap; no booking for a stored program; preview books nothing | Baseline paths and windows; `test_queue.py`, `test_planning.py`, `test_jam_delivery_paths.py`, `test_bus_commands.py`; move 0's preview pin | Opus-safe, after move 0: mechanical; it writes bookings, which the preview pin watches |
| 5 | `order_planning.py`, sensor and cyber half: the other six | `order.actor` set before the payload is built; `sensor_id` and `window_end` in the payload (`_rebind` rebuilds bookings from them); contended versus no window; cyber effect built before the queued mark, scheduled at `clock.now` | `test_observe_order_remediation.py`, `test_planning.py` (rewind rebuild), `test_queue.py`, `test_orders.py`, `test_derived_probabilities.py`; move 0's preview pin | Opus-safe with Tier A reading the diff: mechanical, but it writes log content that rewind depends on |
| 6 | `order_handlers.py` | Everything in §9.2.3 | `test_orders.py`, `test_effect_resource_bounds.py` (two replay tests), `test_jam_delivery_paths.py` (replay per path), `test_future_work.py` (auto-cue), `test_session.py` (blocked downlink), `test_failure_atomic_events.py`, `test_aar.py`; move 0's execute pin and the registry pin | **Fable-only:** it runs inside replay; the baseline never runs a kinetic engagement, a jammed delivery, a failed re-check or an auto-cue |

Moves 1, 2 and 4 are genuinely mechanical. Moves 3 and 5 are mechanical in places the baseline
sees only in part. Move 6 is the risky one and buys the least (about 190 lines); if the owner wants
the smallest safe refactor, stop after move 5 (`orders.py` is then about 670 lines).

#### 9.2.5 What the baseline does not cover

The baseline issues 952 orders: all seven actions, the three delivery paths, the sensor path and
cyber; every action is queued at least once **except `engage`** (refused all 114 times). It
cancels one order per cell and changes one ROE flag. It does **not** run:

| Not in the baseline | Covered by |
|---|---|
| `dry_run` at all (the script only issues) | `test_validate_order.py` (5, one downlink order), `test_orders.py`, `test_effect_resource_bounds.py`, `test_jam_delivery_paths.py`, `test_order_param_hardening.py`, each for one case |
| **`dry_run` as a mirror:** same status, reason, path, window and actor as `issue` for all seven actions, and no change to the log, RNG state, scheduler, `orders`, `_order_counter`, `_pending` or the four booking dicts | **Uncovered: needs a test first** (move 0, preview pin: the baseline's own order list, previewed then issued, on a few vignettes) |
| Gating and the pending-approval resume (no library vignette declares gating rules) | `test_orders.py` (4), `test_gated_order_resume.py` (14); nothing here moves |
| The ROE point-in-time derivation (the baseline shows it only as a refusal string) | `test_orders.py` (change affects later orders, not earlier ones), `test_content.py`, `test_ssn.py`; it stays in `orders.py` |
| A queued `engage`: its payload, kinetic resolution, the ammo charge, the execute-time re-check | `test_orders.py`, `test_effect_resource_bounds.py`, `test_derived_probabilities.py` |
| Jam and cyber execution: queued 38 and 42 times, but whether a jam window opens inside two hours is not asserted | `test_derived_probabilities.py`, `test_jam_delivery_paths.py` (10), `test_safe_mode.py`, `test_orders.py` |
| Sensor bookings beyond the refusal string: release on execute, on cancel, rebuild after rewind | `test_observe_order_remediation.py`, `test_queue.py`, `test_planning.py`, `test_defensive_audit_2026.py` |
| The per-pass cap (`pass_capacity_full` never occurs) | `test_queue.py` |
| Jammed delivery, blocked downlink, auto-cue, phase angle, beam modes, `requires_cue` | `test_jam_delivery_paths.py`, `test_session.py`, `test_future_work.py`, `test_phase_angle_gain.py`, `test_beam_mode_modality.py`, `test_orders.py` |
| **A manoeuvre that fails at execute** (`payload["applied"]` is `False`: jammed, or Δv gone) and its replay | **Uncovered: needs a test first** (move 0, execute pin: one scripted session that runs all five execute kinds including this and a queued engage, then asserts replay equality) |
| **Payload key names and order** (the baseline hashes with sorted keys) | **Uncovered: needs a test first** (move 0, key pin: the key list of each of the five execute payloads) |
| The handler registry | Uncovered; §9.1 move 0's registry pin covers these eight kinds too and must merge before move 6 |

#### 9.2.6 Do not move

| Stays in `orders.py` | Reason |
|---|---|
| `Order`, `scene_from_world`, `BAR_DURATION_S` | Imported from here by 37 files, by `ssn.py` and `recovery.py` at module level, and by `inprocess.py`. Moving `scene_from_world` would end the `ssn` → `orders` cycle, but that is a design change, not a move. |
| `__init__` | Registration order, and every attribute the manager and the tests read or write. |
| `issue`, `dry_run`, `_plan`, `_continue_plan` | The mirror is only checkable while both entry points and the single `commit` flag sit together. `issue` registers the order **after** planning returns; `dry_run` mints no id. |
| `_order_classification`, `_matching_gate`, `rebuild_pending`, `decide_gated_order`, `_effective_roe`, `issue_roe_change`, `_h_roe_change`, `_h_noop` | They append to the log directly (handler applied, then append; pending entry deleted, decision appended, then planning resumed). The baseline is blind to gating. 130 lines; not worth the risk. |
| `cancel`, `_release_bookings_on_execute`, the four booking dicts, `orders`, `_pending`, `_order_counter` | `_rebind`, `from_state` and nine test files reach them by name. The two release paths differ (§9.2.1); do not unify them. |
| `_ap` | Called by a test and by `tools/render_manual.py`. `_next_window` builds the same provider inline; do not fold one into the other in a move. |

**Not part of any move:** splitting `_exec_payload` per action, hoisting imports, removing the
unused import, unifying the two release paths, or renaming a private method. Each is a separate
package with its own tests.

## 10. Tier reallocation (owner, 2026-11-15: Fable quota at 90%)

Fable is reserved for what only it can do. **Everything else in §4 moves to Opus**, with a fresh Opus
session verifying (not the author). A packet that stops under §3 rule 9 for a reason the plan names
goes to Fable only if it is on the list below.

**Fable, essential only (read-only review and one design):**

| ID | What Fable does | Why it cannot move |
|---|---|---|
| F1 | **A7, `BL-0432` design only** (bus-tick horizon): choose tick-to-ceiling or stop-the-clock, write the requirement text and the save/event-log compatibility rule. | The choice changes every event log and what happens to saved exercises. |
| F2 | **Diff review, not authoring,** of the three risky moves: §9.1 moves 7 and 8 (`manager.py` inject queue and handler bodies) and §9.2 move 6 (`orders.py` handler bodies). Opus writes them; Fable reads the diff against the baseline and the §9 rules and answers approve / change. | A mistake there corrupts replay or saves without failing a test. A review costs a fraction of authoring. |

**Moved to Opus (with what Fable's work leaves behind):**
- **A2** domain-files map: Opus, using A1's method (§8) and its lessons (short-form citations, mis-numbered section references); F2-style spot check is optional.
- **A3** ledger design and **A8** gate inventory: Opus; both are low-urgency (steps 5 and 6).
- **A5c, A5d** `server.py` and `app.js` plans: Opus, same format as §9.1 and §9.2.
- **Move 0** (tests the baseline lacks): Opus writes characterisation tests that pin current behaviour (handler registry, save key order, `dry_run` mirrors `issue`, a failing manoeuvre at execute, execute-payload keys, `get_series` for another cell's asset). They must pass on unmodified code; a verifier checks that each fails when the behaviour is deliberately broken.
- **A6** the `manager.py` and `orders.py` moves: Opus, one move per PR, in §9 order; moves 7, 8 and 6 wait for F2 review.
- **A7, `BL-0431`** (order previews leak truth): Opus designs it; the default is *belief-based preview, refuse when the actor or target is not the caller's own or tracked*; the owner confirms before it is built, because it is a fog-of-war decision.
- **A9** final review: a fresh Opus session; independence matters more than tier.

**Stop rule change.** §3 rule 9 says "hand back to Tier A". Read it as: leave the branch pushed without a PR, write what happened in the chat, and the owner decides whether it is an F1/F2 item or waits.


## 11. A2 output — successor map for the domain documents

Made 2026-11-16 at `140be2f`. Input to B3. Short forms are used throughout (`DOM-003 §4`); GDS-NN
means `docs/architecture/NN-*.md`; "the domains folder" is the folder that holds the domain
documents (its full path is not written here, because B3 declares it retired and the check polices
the full form). §4 and §5 say `DOM-001`…`DOM-008`: **there are nine** (`DOM-009`, Doctrine
Development, exists and is cited by 21 live documents). B3 declares all nine IDs.

**Method.** Every live file (all `*.md`, plus `*.py`, `*.js`, `*.yaml`) was scanned for a `DOM-`
ID, the folder name, "domain document" and "domain framework", with the section that follows
(`§n`, `§§n–m`, ranges and lists expanded). Frozen records were excluded: `docs/reviews/`,
`docs/implementation/verification/`, `docs/architecture/adr/`, the two archive files, the
journal's run log; so were the domain documents themselves and this file. Each DOM section was then
read against the GDS ladder, the requirement leaves, the master documents, the skills and the
pipeline ledgers. **Confirmed** means the DOM text and the successor were both read and the
successor carries the content (or the DOM text is framing that the successor states). **Partial**
means the successor carries the requirement-level or one half of the content, or the content lives
only in a feature specification, a skill or a research topic. **NOT absorbed** means no live
document outside the domain documents states it. **Navigation** means a "Related topics" section
with no content. The journal's claim that "most was absorbed" holds for `DOM-005` §3, §4, §6,
`DOM-007` §3–§6, `DOM-008` §3 and `DOM-002` §5, `DOM-004` §4–§5, and for nothing else:
GDS-06 to GDS-10 each recorded a DOM merge-gate line (`BL-0293`); GDS-00 to GDS-05 predate the
instruction and recorded none, so `DOM-001`, `DOM-003` and `DOM-009` were never checked against
the ladder until this table.

**How B3 uses the table.** (a) A requirement's *Source documents* line: replace the DOM citation
with the successor in the same row, or remove it where the successor is already on the line.
(b) A GDS level's own "Absorbs", "Merge gate" and "Departures" text is provenance: keep the
sentence, name the source as "the retired domain framework (`DOM-005` §3)" only if the ID check
allows it (see §11.6 finding 2), otherwise as "the retired assessment/validation/... domain
document". (c) Body text outside the two permitted places: **repoint to the successor** in the
row, do not merely add "retired". (d) A row marked NOT absorbed or partial in §11.4 is migrated
first, as its own commit, before any citation of it is touched.

### 11.1 Who cites the domain documents

Live documents citing each ID, by folder (a document citing two IDs counts under each; `*` and
`xxx` are the generic forms `DOM-*` and `DOM-xxx`). Frozen records and the domain folder itself
excluded. `training/` has none: the plan's expectation of training citations does not hold.

| ID | requirements | architecture | features | research | master | training | skills | other | **docs** | code |
|---|---|---|---|---|---|---|---|---|---|---|
| `DOM-001` | 0 | 1 | 6 | 3 | 4 | 0 | 0 | 2 | 16 | 0 |
| `DOM-002` | 3 | 4 | 8 | 24 | 4 | 0 | 1 | 6 | 50 | 1 |
| `DOM-003` | 0 | 0 | 9 | 10 | 3 | 0 | 1 | 3 | 26 | 0 |
| `DOM-004` | 2 | 2 | 2 | 1 | 4 | 0 | 0 | 4 | 15 | 0 |
| `DOM-005` | 3 | 4 | 3 | 18 | 5 | 0 | 1 | 5 | 39 | 2 |
| `DOM-006` | 0 | 1 | 0 | 0 | 2 | 0 | 1 | 0 | 4 | 0 |
| `DOM-007` | 1 | 2 | 7 | 2 | 2 | 0 | 1 | 3 | 18 | 0 |
| `DOM-008` | 1 | 1 | 2 | 25 | 3 | 0 | 1 | 1 | 34 | 0 |
| `DOM-009` | 0 | 1 | 4 | 11 | 3 | 0 | 1 | 1 | 21 | 0 |
| `DOM-*` / `DOM-xxx` | 0 | 1 / 1 | 0 / 1 | 0 | 3 / 1 | 0 | 0 / 3 | 0 | 4 / 6 | 0 |

Distinct live documents, any form (an ID, the folder path, or "domain document/framework"):
**116**, with 765 mention lines: `requirements/` 3 (56 lines), `architecture/` 7 (36), `features/` 20
(169), `research/` 59 (359), `master/` 7 (46), `training/` 0, `.claude/skills/` 7 (46), other 13 (53:
`ROADMAP.md`, `docs/INDEX.md`, `docs/pipeline/backlog.md`, three `feature-planning/` files, seven
`implementation/` files). Two code files cite them (`spacesim/session/assessment.py`,
`spacesim/tools/research_batch.py`; §11.6 finding 5). Frozen files that also cite them and are
left alone: 16 (six ADRs, one verification report, seven review reports, the two archives).

The requirements are not where the weight is. Only three baseline leaves name a DOM section on
their *Source documents* line: `FR-10110` (`DOM-002` §§3–6), `FR-10210` (`DOM-004` §§4–6) and
`NFR-2810` (`DOM-005` §3–§4, with GDS-06 NFR-19 already first on the line); three candidates do
the same (`CR-19` `DOM-002` §§3–6, `CR-20` `DOM-004` §5, `CR-21` `DOM-004` §6). Outside Source
lines the requirement files carry 10 more leaf-level mentions that B3 may not reword (Rationale of
`FR-10110`, `FR-10210`, `NFR-2810`, `NFR-3010`, `NFR-3020`, `NFR-3030`, `NFR-3040`, `NFR-3050`,
`NFR-3060`; Postconditions of `FR-10210`), and about 40 lines of change-note, section-heading and
candidate prose (see §11.6 finding 2). The bulk is the 59 research topics (359 lines) and the 20
feature specifications (169 lines), whose metadata blocks name a DOM as *Dependencies*.

### 11.2 The map, `DOM-001` to `DOM-003`

"Cited" is the number of live documents that cite that section in the form `DOM-nnn §n`.

#### `DOM-001` Training Framework (9 sections)

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose: how SpaceSim teaches | MSTR-001 §2 (training corpus co-equal); MSTR-003 §1–§2; GDS-01 and GDS-00 "Training-corpus elevation" | confirmed (framing) | 0 |
| 2 | Scope split against DOM-002, -003, -009 | none wanted: the split dies with the DOM ladder | confirmed (framing) | 0 |
| 3 | Four training-objective classes (mechanical, tactical, operational, judgment) and the `intro_brief` rule | none. GDS-07 §5 has a free-text `learning_objectives` field; `docs/vignettes/00-vignette-framework.md` "Authoring philosophy" says "explicit learning objectives" with no classes | **NOT absorbed** | 0 by section (named by MSTR-005 §4 chain and FS-101 §7) |
| 4 | Five-step skill progression over the 19 vignettes; design rule "assign every new vignette a slot" | GDS-01 "The learning path is an operational workflow"; `FR-11310`, `FR-11320`, `FR-T2`; `docs/training/16-learning-path.md`. The mapping of each step to an objective class travels only with §3 | confirmed (steps and rule); class labels lost with §3 | 1 (FS-201, loosely: it means per-trainee progression, which is DOM-002 §7) |
| 5 | `tutorial:` and `intro_brief:` mechanisms | GDS-07 §5 (fields), GDS-08 §4 "Brief" row and §8 menus, `FR-11420` (machine-verified tutorials); `test_vignette_tutorials.py` | confirmed | 0 |
| 6 | Coaching notes as just-in-time instruction; "inform, never act" | GDS-07 §5 (`coaching`), GDS-08 §7.6 | partial: mechanism carried, the one-line rule "coaching never acts for the cell" is not | 0 |
| 7 | FS must state objective class and progression slot in "Educational Value" | MSTR-003 §9 (FS must name the training objective it serves) | partial: the class and slot parts need §3 | 1 (FS-101) |
| 8 | Open work: `training_objectives:` field; cross-check 19 vignettes | overtaken: `learning_objectives` shipped; placement is `docs/training/16-learning-path.md` and `FR-11310` | partial: class tagging not done, and moot unless §3 migrates | 2 (FS-101, same document) |
| 9 | Related topics | none | navigation | 0 |

#### `DOM-002` Assessment Framework (9 sections)

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose: measuring vs delivering | `FR-10110` Rationale; GDS-07 §8; MSTR-003 §8 | confirmed (framing) | 0 |
| 2 | Scope split against DOM-001, -005 | none wanted | confirmed (framing) | 0 |
| 3 | Binary objective-flip is insufficient | MSTR-003 §8 ("competency, not just completion"); `FR-10110`; ADR-0032 | confirmed | 4 |
| 4 | Six measurement dimensions with data sources | `FR-10110` names all six and implements three; GDS-05 `FR-A1`; GDS-07 §8; FS-201 Scope and System Behaviour (three implemented with sources; the three deferred are named, with a one-line reason each). Definitions and data sources of resource economy, escalation discipline and time-to-decision exist only in `DOM-002` §4 | partial | 13 |
| 5 | Rubric, not a single score | GDS-05 `FR-A1`; GDS-07 §8; `FR-10110` Postconditions; ADR-0032; FS-201 (tier labels for the three dimensions) | confirmed | 9 |
| 6 | Automated, facilitator and self-assessment modes | FS-201 System Behaviour "Assessment modes"; FS-107 (the AAR as self-assessment). Nothing in the GDS ladder or the requirements | partial (feature level only) | 7 |
| 7 | Reporting surface: per exercise, and longitudinal per trainee | per exercise: `FR-10110` Acceptance Criteria, FS-201. Longitudinal: gap, `BL-0303` (DEFERRED), GDS-07 OQ4, Release 2.0 plan F-31, `CR-21` | partial: per-exercise half confirmed, longitudinal half **NOT absorbed** by decision | 3 |
| 8 | What FS-201 must state | FS-201 itself (Scope, Acceptance Criteria) | confirmed (met in place) | 0 |
| 9 | Related topics | none | navigation | 2 (R206, R207) |

#### `DOM-003` White Cell Framework (10 sections)

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose: White Cell as instructional designer | MSTR-003 §7; GDS-01 §5, §7; GDS-08 §7.1, §7.6 | confirmed | 3 |
| 2 | Scope, including session setup (`FS-115`) and classification banner (`FS-112`) | GDS-05 `FR-W1`, `FR-W2`, `FR-W5`; `FR-4110`, `FR-4210`, `FR-4510`; `NFR-3100` | confirmed | 1 |
| 3 | Authority and visibility; "no back door to ground truth" | `CLAUDE.md` Trust model and invariant 3; GDS-05 `FR-W6`, OR-9; `FR-4610`, `FR-6220`; GDS-09 §4; GDS-08 §5, §7.6 | confirmed | 3 |
| 4 | Inject mechanism; library as a living content set; design implication for FS-108 | GDS-05 `FR-W4`, `FR-W8`; `FR-4410`, `FR-4450`, `FR-4460`; GDS-07 §4 (inject library artifact); GDS-08 §7.6 (builder). The "add reusable templates, do not script one-offs into a vignette" rule has no home | partial | 6 |
| 5 | Clock and pacing authority; rewind/undo/branch White-only | GDS-05 `FR-W3`; `FR-4310`, `FR-4320`, `FR-4330`; ADR-0016 | confirmed | 3 |
| 6 | Session administration (save/resume, discovery, join-by-URL, pop-out) | GDS-05 `FR-L3`; GDS-09 §3, §6; GDS-08 §7.1, §7.9, §8; FS-109, FS-110. The "facilitation concern, not infrastructure" framing stays an Open Question in FS-109 and FS-106 | confirmed | 6 |
| 7 | White Cell as red-team enabler: see which preset drives Red, switch or tune it mid-exercise | visibility: `NFR-3060`, GDS-06 NFR-9 last bullet, `FR-9110`. Switching or hand-tuning the preset mid-exercise has no leaf | partial | 4 |
| 8 | What a White-Cell-facing FS must state (authority tier; no new god-view) | no-new-god-view: invariant 3, `FR-6220`. "State the tier" is not in the skill 06 template | partial | 1 |
| 9 | Open work: FS-108; composing injects into a sequence | FS-108 exists (candidate); vignette-scheduled and condition-triggered injects (`FR-4410`, `FR-4420`) cover part of the second item; composing library templates ahead of a session is unspecified | partial (stale) | 3 |
| 10 | Related topics | none | navigation | 1 (R307) |

### 11.3 The map, `DOM-004` to `DOM-009`

#### `DOM-004` Research Framework (9 sections)

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose: encyclopedia program and instrument-grade research | MSTR-007 §1 for the encyclopedia; FS-301 Purpose for instrument-grade use; GDS-00 §3 (researcher audience row) | partial: the umbrella statement is in no GDS or master document | 0 |
| 2 | Scope | none wanted | confirmed (framing) | 0 |
| 3 | Two research activities, not to be conflated; the risk the split guards against | FS-301 Scope ("Two distinct research activities: boundary statement"). MSTR-007 does not state it | partial (feature level only) | 1 |
| 4 | SpaceSim as an instrument: reproducible, full trace, data-driven manipulation | GDS-07 §8 (the event log is the research record); invariant 6; NFR-3 | confirmed | 2 |
| 5 | Gap: no export or cohort layer; FS-301 closes it | GDS-07 §8 (`RunRecord`, `research_batch`); GDS-05 `FR-A2`; `FR-10210`; ADR-0033; FS-301 | confirmed | 4 |
| 6 | Authorization and ethics boundary: no human-subjects feature without go-ahead and the institution's IRB | `CR-21` (candidate, Source cites this section); requirements/01 "Explicitly not authorized by this category"; FS-301 Scope and non-goals; MSTR-006 §3 (authorization gate). Not in the GDS ladder | partial (candidate requirement and FS only) | 3 |
| 7 | The encyclopedia is authored under research-method discipline | MSTR-007 §6 (authoring cadence). A remark, not a rule | confirmed (no successor wanted) | 0 |
| 8 | What FS-301 must state (tag, export schema, non-goal) | FS-301 itself | confirmed (met in place) | 1 |
| 9 | Related topics | none | navigation | 0 |

#### `DOM-005` Validation Framework (8 sections)

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose: verification vs validation | GDS-06 NFR-19 (first two sentences) | confirmed | 1 |
| 2 | Scope: fidelity claims, instrument validity | NFR-19 for fidelity; instrument validity is §5 | confirmed for (a); (b) follows §5 | 0 |
| 3 | Verification is strong; validation is the gap | GDS-06 NFR-19; NFR-3; `NFR-2810` | confirmed | 3 |
| 4 | Validation of fidelity claims against cited reference values; the June 2026 power audit as precedent | GDS-06 NFR-19; `NFR-2810` (Source line already names NFR-19) | confirmed | 6 |
| 5 | Validation of assessment instruments: face validity, internal consistency, sensitivity to manipulation | **none.** GDS-06 NFR-19 says it "is a feature-level method for FS-201, not a system quality attribute, and is not absorbed here"; FS-201 cites it but does not state the three checks; R410 has face validity only | **NOT absorbed** | 7 (R404, R408, FS-201, FS-301, IP-2010, IP-3010, and GDS-06's own "not absorbed" note) and the shipped disclosure string in `session/assessment.py` |
| 6 | Monte Carlo as validation workhorse; variability across seeds, never inside the engine | GDS-06 NFR-3 ("absorbs DOM-005 §6"); `NFR-1500`; `FR-10210` Postconditions; GDS-07 §8; `research_batch.py` | confirmed | 6 |
| 7 | Disclosure rule: an IP or metric claiming meaning must cite which §5 checks it passed | FS-201 System Behaviour "Validation discipline"; IP-2010 Definition of Done; `session/assessment.py::DISCLOSURE`. No baseline rule | partial (feature and code level) | 3 |
| 8 | Related topics | none | navigation | 0 |

#### `DOM-006` Governance Framework (8 sections)

GDS-06's merge gate says "not absorbed: process, not a system quality attribute; belongs with the
MSTR governance documents". Nothing was ever moved there. Live section citations of this document:
none; whole-document citations: GDS-06, MSTR-005 (tree), MSTR-006 (one sentence), the doctrine
research skill (a wrong path, see §11.6 finding 6).

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose: simulator content and feature-scope lifecycle, sibling of MSTR-006 | MSTR-006 §1 names the sibling; the product-content half has no home | **NOT absorbed** | 0 |
| 2 | Scope | none wanted | confirmed (framing) | 0 |
| 3 | Four content-change classes and the authorization each needs | class 4 (large undertaking): MSTR-006 §3. Class 2 (scope-expanding needs an FS first): `00-intake` entry stages, `CLAUDE.md` "Pipeline", skills README. Class 3 (rebalancing needs audit and regression test): `CLAUDE.md` "Test-first", the A4 baseline, `NFR-2810`. Class 1 (additive, low risk: record in ROADMAP or vignette index): none. The table itself has no home | partial | 0 |
| 4 | The former future-work list graduates into FSs; "→ see FS-xxx" | superseded: the list is retired; the successors are `docs/pipeline/backlog.md` (`DEFERRED` rows) and the LATER rows of the Release 2.0 plan (`CLAUDE.md` "Where things are") | confirmed (superseded) | 0 |
| 5 | Audit reports as the shape of a retrospective review | none. The three June 2026 audits remain under `docs/reviews/` as precedent; the shape guidance is nowhere | **NOT absorbed** (low value) | 0 |
| 6 | Decision rights table | row 2: MSTR-006 §3; row 4: MSTR-006 §6 (escalate scope or strategic change to the owner) and `CLAUDE.md` invariants; row 1: `00-intake`; row 3 (White Cell judges doctrine balance): none | partial | 0 |
| 7 | Every FS names the list item it graduates from; every IP names its change class | obsolete for the first half; the second half is in no IP template (skill 07) | **NOT absorbed** | 0 |
| 8 | Related topics | none | navigation | 0 |

#### `DOM-007` Human Factors Framework (8 sections)

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose | GDS-06 NFR-9 intro; GDS-08 Purpose and §2 | confirmed (framing) | 0 |
| 2 | Scope | none wanted | confirmed (framing) | 0 |
| 3 | Intentional vs accidental friction | GDS-06 NFR-9 bullet "Intentional vs accidental friction"; GDS-08 §2; `NFR-3000`; skill 06 "Console Friction" section | confirmed | 5 |
| 4 | Four cognitive-load principles (belief legible, causes surfaced, summary and detail agree, affordances reflect permission) | GDS-06 NFR-9 bullets 3–6; GDS-08 §5, §6; `NFR-3010`–`NFR-3050`; `NFR-2840` (browser suite) | confirmed | 8 |
| 5 | Panels follow the panel-manager contract | GDS-06 NFR-9 panel bullet; GDS-08 §4; `NFR-3030` | confirmed | 3 |
| 6 | Accessibility: consistent keyboard bindings, presentation mode | GDS-06 NFR-9 first bullet; GDS-08 §8; `NFR-3000` | confirmed | 1 |
| 7 | What FS-105 and FS-106 must state ("Human Factors" consideration) | skill 06 "Console Friction" (owner decision `BL-0312`) | confirmed | 0 |
| 8 | Related topics | none | navigation | 0 |

#### `DOM-008` AI Integration Framework (7 sections)

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose: in-world AI vs AI that builds the simulator | R500 index and the future-operations skill restate it; no GDS or master text | partial | 0 |
| 2 | Scope | none wanted | confirmed (framing) | 0 |
| 3 | In-world AI today: presets as data, seeded RNG, legible to White Cell | GDS-06 NFR-3, NFR-7, NFR-9 (last bullet); `NFR-3060`; ADR-0030, ADR-0021; `FR-9110` | confirmed | 12 |
| 4 | Future in-world AI: any AI must preserve plan-first; **advisor, not decider**; anything beyond advisory is pending authorization | determinism and "enters only through logged `SessionAPI` calls": ADR-0030, invariants 1 and 4. The **advisor-only constraint and its authorization gate are in no live document** outside the R501–R509 topics and the future-operations skill | partial: the heaviest-cited section in the folder | 17 (R202, R203, R206, R207, R209, R210, R212, R213, R311, the R200 and R500 indexes, R501, R503, R506, R507, R509, the future-operations skill) |
| 5 | Coding AI: documentation-driven development; a coding agent is not exempt from determinism | MSTR-006 §4, §8; `CLAUDE.md` "Working rules" and "Pipeline"; skills README | confirmed | 3 |
| 6 | Every R501–R509 topic carries a tag (in-world, coding-agent, or both); an FS proposing in-world AI cites §4 and flags pending authorization | the tag: 10 files carry the literal label "DOM-008 §6 tag" (nine topics and the R500 index); the future-operations skill makes it mandatory. The FS-side rule is in no skill 06 text | partial | 11 |
| 7 | Related topics | none | navigation | 0 |

#### `DOM-009` Doctrine Development Framework (7 sections)

| § | Content | Successor | Status | Cited |
|---|---|---|---|---|
| 1 | Purpose: doctrine becomes playable content without flattening it | MSTR-001 §4 (moderate fidelity); `docs/research/01`–`03`, `07`; skill 02 doctrine | confirmed (framing) | 0 |
| 2 | Scope | none wanted | confirmed (framing) | 0 |
| 3 | Translation pipeline (doctrine, then parameters, then vignette or preset content); every threat picture and ROE block traceable to its source | `doctrinal_basis` vignette field: GDS-07 §5, all 19 vignettes, `docs/vignettes/00-vignette-framework.md`. Its values are topic tags (for example `orbital_warfare`), not pointers to research documents, so the traceability the rule asks for is not met | partial | 1 |
| 4 | Translation principles: data not code; calibrated realism; legal and ROE norms are load-bearing | bullet 1: invariant 6, GDS-06 NFR-7. Bullet 2: MSTR-001 §4. Bullet 3: `docs/research/07`, `FR-P7` (per-cell ROE); the rule "a new effect category or weapon class goes through the legal and ROE mapping before it ships" is not carried | partial | 4 (FS-103, FS-104, R212, R213) |
| 5 | Doctrine review cadence: recheck vignettes and presets after a research revision | none. `docs/research/10` has a review cadence for the research corpus, not for the content built on it | **NOT absorbed** | 1 (R305) |
| 6 | Open work: `doctrine_basis:` field; link preset names to research | first item shipped under the name `doctrinal_basis`; second item open, no backlog row | partial (stale) | 1 (FS-104, and it cites §6 for the wrong thing, §11.5) |
| 7 | Related topics | none | navigation | 0 |
