[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — Run #97 Scope (Ephemeris + Telemetry CSV Exports)

> **Document ID:** REV-TRN-002
> **Skill:** `09-training-manual-review`
> **Scope:** the training-corpus sections authored by pipeline run #97
> (`08-training-manual-authoring`, commit `419c2e4`, closing `BL-0166`/`BL-0167`):
> `WCM-15`/`WCM-16` (`12-white-cell-manual.md`), `BLU-13`/`BLU-14` (`13-blue-cell-manual.md`),
> `RED-12`/`RED-13` (`14-red-cell-manual.md`), the matching `15-manual-traceability.md` §15.1
> forward rows and §15.2 reverse rows, and `INDEX.md`'s three per-manual summaries. Also adjudicates
> backlog entry `BL-0084` (deferred to "the next `09-training-manual-review` run": is the
> command-menu **target dropdown** change documented?).
> **Commit reviewed:** `7c38b20` (branch `claude/chart-prompt-file-90hm9u` tip at review time).
> Run #102 (`6e323bc`) edited `BLU-6`/`RED-7`/`05`/`10` §10.13 after run #97. That work is **out of
> this review's scope**: this session authored it, so it needs a review from a different session.
> **Precondition confirmed:** this session authored none of run #97's sections; the review is
> independent of them.
> **Upstream:** `08-training-manual-authoring` (run #97) · **Downstream:** `10-integration-review`,
> `11-release-readiness`

## Dimensions exercised

### 1. Accuracy — prose claims vs. shipped behaviour

Every claim was checked against the source, and the main ones were driven live in Python against a
two-satellite session (`test_ephemeris.py::_two_sat_manager_with_track`, stepped 600 s):

- **Routes and parameters.** `ui_web/server.py` declares `GET /ephemeris/truth` (`object_id`,
  `reference_id`, `t1`, `t2`, `interval_s`, `format`) before `GET /ephemeris/{cell}`. It also
  declares `GET /telemetry/{cell}/{asset}/export.csv` (`t1`, `t2`, `interval_s` with `gt=0`) before
  the `/{param}` series route. These match WCM-15/BLU-13/RED-12/WCM-16/BLU-14/RED-13. A grep of
  `ui_web/static/` confirms no console control calls either route, so **"URL-only" is accurate**.
- **Formats.** `format=oem` → `write_oem` (CCSDS OEM 2.0 KVN, ECI only). `format=ric` →
  `write_ric_csv`. Default → `write_csv` with ECI and RIC columns. Confirmed; the OEM header was
  produced live.
- **Span rule.** `_clamp_or_reject`: a span partly out of range is clamped (live: a request
  starting 1000 s before the epoch returned the same 3 rows as an in-range request). A span wholly
  out of range raises `ValueError`, naming the recorded range. Both routes map that to **400**.
  Confirmed as described.
- **Default sampling.** `sample_times`: when `interval_s` is omitted, the step is
  `max(span/100, BUS_TICK_PERIOD_S)`. This matches WCM-15's "span/100, floored at one bus-tick
  period".
- **Truth vs belief.** `truth_ephemeris` reads `world.assets` (truth). `cell_observed_ephemeris`
  reads only `world.track_for(cell, …).state_estimate`. An instant with no track is skipped, not
  fabricated (live: Red, holding no track on `SAT-BLUE`, got 0 rows). The reference resolves to
  truth only when `ref_asset.owner == cell`. Confirmed, and this matches `_live_state`'s rule for
  the live RIC view, as BLU-13/RED-12 say.
- **Telemetry export ownership.** `_owns()`: White sees any asset; other cells see only their own.
  Live: `telemetry_export('red', 'SAT-BLUE')` → `None` → 404. White and Blue each got
  3 instants × 19 rows. `len(telemetry.PARAMS) == 19`, matching "19 parameters".
- **Per-instant replay.** `telemetry_export` samples
  `aar.worlds_at_times(...)`-replayed worlds (IP-1261, `VR-1261`). The anomaly-onset guarantee in
  WCM-16/BLU-14/RED-13 is accurate, and since IP-1261 it is the same mechanism the live graphs use.
- **`t1`/`t2` units.** Both are integer microseconds since the Unix epoch, the `simtime` units.
  Accurate.
- *Observed, not a finding:* `write_oem` stamps `CREATION_DATE` with the wall clock. This is in
  `session/`, not `engine/`, so the determinism invariant is not violated, and CCSDS requires a
  creation date. The manual makes no reproducibility claim about OEM bytes.

No prose describes removed or renamed behaviour, so there are no Critical accuracy defects in
run #97's scope.

### 2. Traceability integrity

- **Footers.** Every path in all six `> Sources:` footers exists: `session/ephemeris.py` and its
  functions, `session/manager.py::telemetry_export`, `engine/telemetry.py::sample`, both routes,
  `FS-121` and `FS-126`.
- **Matrix agreement.** §15.1 rows 79–80 name `WCM-15/BLU-13/RED-12` and `WCM-16/BLU-14/RED-13`,
  and the §15.2 reverse rows list each of those six sections under the matching feature. The two
  directions agree, and they agree with the footers.
- **One weak spot (F6).** Since IP-1261, the per-instant replay is `session/aar.py::worlds_at_times`.
  Neither row 80 nor the three telemetry-export footers name it. Run #102's BLU-6/RED-7 footers do,
  so the matrix is now uneven.
- **No orphans.** No dangling section IDs. `16-learning-path.md` correctly has no rung for either
  capability: no vignette YAML was touched (FR-11310).

### 3. Coverage

- **Role reach.** Both capabilities reach every role that can use them (FR-11110): White gets
  truth plus any-asset telemetry; Blue and Red get own-belief ephemeris plus own-asset telemetry.
  The Observer seat is read-only and mutation-rejected. These are GET routes, but the manuals do
  not cover Observer use of them. Observer has no dedicated section anywhere in the corpus, so this
  is not a regression.
- **Recently shipped packages.** The latest `VERIFIED` packages are all indexed in §15.1:
  `IP-1210` (rows 79), `IP-1260` (row 80), and `IP-1261` (row 61 via run #102, and row 80 implicitly).
- **`BL-0084` (target dropdown) — confirmed gap.** The shipped command form
  (`index.html` `#o-target`) and the tasking rail (`#task-target`) each have a **`<select>` of
  known targets** populated by `populateTargetPicker()` from fog-filtered lists, plus an
  **"or id" free-text input** (`#o-target-manual` / `#task-target-manual`) that takes precedence.
  `#o-target` is disabled for any action outside `jam`/`engage`/`cyber`/`observe`. The UI reference
  `10-ui-reference.md` §10.5 row 5 and §10.6 row 4 still say `Target | text`. This is not removed
  behaviour (the text field survives as "or id"), so it is not Critical. But it mis-describes the
  primary control and omits the disabled-unless-targetable rule: **Medium (F2)**. The
  `ref-05-tasking.png`/`ref-06-compose.png` screenshots predate the change, so they likely need
  regeneration too (`tools/render_manual.py`).

### 4. Pedagogy (MSTR-003 / NFR-3500 / NFR-3600, R600)

- **Audience.** Each section opens with the operator action (the URL to build), states the "URL-only"
  constraint plainly, and ends with a concrete use ("hand an analyst…", "compare your belief's drift
  against WCM-15 during a debrief"). This is task-first and minimalist, as R606 recommends. The
  debrief uses tie to R603 (AAR as the payoff step).
- **Module size.** `12-white-cell-manual.md` is now 310 lines, just over NFR-3500's ~300 ceiling
  (F5). `13` (233) and `14` (215) are within range.
- **WCM-16's "naive approach" paragraph.** It leans toward developer explanation (what a wrong
  implementation would do). It earns its place: it tells the facilitator *why* the timestamps can be
  trusted in an AAR. It was judged acceptable, not a finding.
- **Friction worth recording (F7).** All three ephemeris sections tell the operator to find a
  microsecond timestamp in "the event log or a save file". The console displays ISO times, so this
  is a real usability gap in the shipped feature, not a prose defect.

**Playbook suite.** `python3 -m pytest spacesim/tests/test_vignette_tutorials.py` at `7c38b20`:
**16 passed**.

## Findings

| Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|
| F1 | `spacesim/session/ephemeris.py::sample_times`; `GET /ephemeris/truth`, `GET /ephemeris/{cell}`, `GET /telemetry/{cell}/{asset}/export.csv` | **Code defect the review exposed.** `interval_s` has no lower bound beyond the step floor `max(int(interval_s·1e6), 1)`. The ephemeris routes accept `0` or negative values, and the telemetry route's `gt=0` still accepts e.g. `1e-6`. Any of these gives a 1 µs step: live, `sample_times(0, 10 s, 0.0)` builds **10,000,001** instants. Over a real span (hours) the request replays billions of instants while holding the session's read lock, which freezes the exercise for every client. Nothing in `FS-121`/`FS-126` sets a sample cap. | Medium | `00-intake` (code bug → `07` remediation package) |
| F2 | `10-ui-reference.md` §10.5 row 5, §10.6 row 4; `ref-05-tasking.png`, `ref-06-compose.png` | **`BL-0084` confirmed.** Target is documented as a `text` field. The shipped control is a known-target dropdown plus an "or id" text input that takes precedence; the command-form target is disabled unless the action is `jam`/`engage`/`cyber`/`observe`. Screenshots likely predate the change. | Medium | `08-training-manual-authoring` |
| F3 | `BLU-13`, `RED-12` | The sections do not say that exporting **your own asset** as `object_id` returns an empty (header-only) file. A cell holds no track on its own asset, and the export reads only tracks, whereas the live RIC view resolves own assets to truth. This behaviour is consistent with `FR-7420` ("tracked objects"), so it is a prose clarity gap, not a code bug. | Low | `08-training-manual-authoring` |
| F4 | `WCM-16` | WCM-16 refers to "the live telemetry panel (WCM-6's monitoring view…)", but WCM-6 covers god-view, Gantt, objectives and coaching, not the telemetry drill-down. The cross-reference points to the wrong place. | Low | `08-training-manual-authoring` |
| F5 | `12-white-cell-manual.md` | 310 lines, over NFR-3500's ~300-line ceiling. Split at the next substantive White-manual touch, for example by moving the URL-only exports (`WCM-12`/`15`/`16`) into a sub-module. | Low | `08-training-manual-authoring` |
| F6 | `15-manual-traceability.md` §15.1 row 80, §15.2 `WCM-16`/`BLU-14`/`RED-13`; matching footers (and row 79 / `WCM-15`/`BLU-13`/`RED-12` likewise) | Since IP-1261, both exports' per-instant replay goes through `session/aar.py::worlds_at_times`, but these anchors do not name it. Run #102's BLU-6/RED-7 anchors do, so the corpus is inconsistent. | Low | `08-training-manual-authoring` |
| F7 | `WCM-15`, `BLU-13`, `RED-12` (shipped feature) | **Usability observation.** Span bounds must be integer microseconds, and the console shows none. Operators must dig a value out of the event log or a save file. Candidate feature: accept ISO-8601 `t1`/`t2`, or show µs sim time in the console. | Low | `00-intake` (feature) |

## Independence statement

This session (run #103's) authored none of run #97's sections. This session did author run #102's
edits (`BLU-6`, `RED-7`, `05-core-concepts.md`, `10-ui-reference.md` §10.13 row 5, and §15.1 row 61
plus the matching §15.2 rows). Those edits were **excluded** from this review and are left for a
different session. F2 touches the same module (`10-ui-reference.md`) but different rows (§10.5/§10.6),
which run #102 did not edit.

## Result

Run #97's prose is **accurate against shipped behaviour**: every claim was confirmed in code and the
main ones were driven live. Traceability is consistent in both directions, coverage is complete
per role, and the playbook suite passed 16/16.

**7 findings: 0 Critical, 0 High, 2 Medium, 5 Low.**

- F1 (Medium) is a code defect the review exposed. It routes to `00-intake`.
- F2 (Medium) is `BL-0084`, now confirmed. It routes to `08-training-manual-authoring`.
- F3–F6 are small prose and traceability fixes for `08-training-manual-authoring`. They can be
  batched with F2.
- F7 is a feature idea for `00-intake`.
