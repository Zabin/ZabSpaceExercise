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
| A1 | Successor map for `docs/build-spec/` and `docs/design/` (§8): 45 cited sections mapped, the two open decisions made, 26 code files listed for C4 | Done (this pull request) |
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
`test_validate_order.py`, `test_ssn.py` (uses the pre-split name `docs/SSN-DESIGN.md`). Most are
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
