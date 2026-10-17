[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — Run #102 Scope (Telemetry History Graph, Per-Instant)

> **Document ID:** REV-TRN-003
> **Skill:** `09-training-manual-review`
> **Scope:** the sections run #102 authored (`08-training-manual-authoring`, commit `6e323bc`,
> closing `BL-0172`). Those are `BLU-6` (`13-blue-cell-manual.md`), `RED-7`
> (`14-red-cell-manual.md`), `05-core-concepts.md` §"Diagnosing attacks from telemetry",
> `10-ui-reference.md` §10.13 row 5, the `15-manual-traceability.md` §15.1 "Telemetry signatures
> + nominal ghost" row, and the §15.2 `BLU-6`/`RED-7` rows. Each touched section was reviewed
> whole, not just the added lines.
> **Commit reviewed:** `cddb111` (branch `claude/chart-prompt-file-90hm9u` tip at review time).
> **Independence:** this session (pipeline runs #107–#108) did not author run #102. It did author
> run #107 (`2778526`: `10` §10.5/§10.6, `WCM-15`/`16`, `BLU-13`/`14`, `RED-12`/`13`, §15.1 rows
> 79–80 and the matching §15.2 rows). Those edits are **excluded** here and need a review from a
> different session.
> **Upstream:** `08-training-manual-authoring` (run #102) · **Downstream:** `10-integration-review`,
> `11-release-readiness`

## Dimensions exercised

### 1. Accuracy — prose claims vs. shipped behaviour

Every run #102 claim was checked in code. The load-bearing ones were then driven live through the
HTTP API (`TestClient`) on fixtures **different from the implementer's and author's**:
`geo-rpo-shadowing` at seed 7 (the shipped parity test uses `leo-isr-denial`/`ISR-EO-1`/`snr_db`).

- **Window and point count** (`BLU-6`, `10` §10.13 row 5). `session/manager.py::get_series`
  defaults to `t0 = max(start_epoch, now − 3600 s)`, `t1 = now` and `n = 120`.
  `ui_web/static/app.js::drawParam` requests `?n=120` for the series, the `&nominal=1` ghost and
  the overlay parameter. Live checks:
  - 1,800 s into the exercise: 120 points, starting at the exercise epoch and ending at `now`.
  - After stepping past one hour: exactly a 3,600 s span with 120 points.
  - "Last hour of sim time (or since exercise start, if sooner)" is therefore **accurate**, and
    the old "60-pt rolling" text was rightly removed.
- **Per-instant, not back-dated** (`BLU-6`, `RED-7`, `05`). `get_series` evaluates
  `engine/telemetry.py::sample` on each world that `session/aar.py::worlds_at_times` yields. Live
  test: a `subsystem: bus` anomaly on `BLUE-HVA` at +900 s, then 900 s more. Comparing all 19
  parameters against the nominal ghost:
  - Two parameters deviated (`attitude_error_deg` yellow, `snr_db` red).
  - Each first deviates at the **first sample after onset** (+7.6 s at the 15.1 s point spacing).
  - There are **zero pre-onset deviations**.
  - "An attack or anomaly appears on the graph starting at its own onset" is **accurate**.
- **Parity with the CSV export** (`BLU-6` ⇄ `BLU-14`, `RED-7` ⇄ `RED-13`). Run as a Red-cell
  request (`/telemetry/red/RED-INSP/bus_voltage_v`, `n=7`) against
  `/telemetry/red/RED-INSP/export.csv` at `interval_s=300` over the same span: 7 shared instants,
  **0 value/status mismatches**. "The same value as your telemetry CSV export at any instant both
  of them sample" is **accurate**, independently of the shipped `snr_db`/Blue test.
- **Nominal ghost** (`10` §10.13 row 3). `?nominal=1` returns `nominal: true` and the same points
  with the attack term dropped (all green after the anomaly). **Accurate.**
- **Fog** (`BLU-6`/`RED-7` imply own assets only). `/telemetry/blue/RED-INSP/...` → **404**.
  Accurate.
- **RED-7's opening sentence** predates run #102 but sits in a touched section, so it is in
  scope. It says *"Red's satellites have the same bus SOH and safe-mode model as Blue's — Blue can
  hit back"* and tells Red to watch worst-subsystem dots and run the recovery chain. The engine is
  symmetric: `BusState` is an optional `Asset` field for both sides, and `build_world` treats
  `red_forces` exactly like `blue_forces`. **But the content is not.** Checks:
  - Building every shipped vignette shows **9 of 9 Red satellites have no `bus_state`**, against
    1 of 31 Blue satellites.
  - Live on `RED-INSP`: `bus_mode` is `None`; the Red scene carries no SOH fields.
  - A `subsystem: bus` anomaly inject on it is accepted with `ok: true` and changes nothing
    (`bus_mode` stays `None`).
  - So in every shipped vignette a Red trainee will never see a safed bird, an SOH dot, or a
    reason to run the recovery chain. **→ F1.**
  - The telemetry-signature half of RED-7 does hold. `engine/telemetry.py` draws attack terms from
    `world.active_effects`, not from `bus_state`, so jam/cyber/DE signatures still appear on a
    bus-less Red asset's graph.
- **Pass-gating consistency** (`BLU-5` → `BLU-6`). `BLU-5` (unchanged) says the defender finds
  out *"at the next telemetry contact, not the moment it happens"*. That is true of the fleet rail,
  whose SOH comes from `engine/bus.py`'s pass-gated `ground_view`. The drill-down graph run #102
  describes is **not** pass-gated: `get_series` samples every instant in the window. Both
  statements are accurate as built, but the reader is not told that they describe different
  surfaces. **→ F3**, tied to the open design question `BL-0171`.

**Playbook suite.** `python3 -m pytest spacesim/tests/test_vignette_tutorials.py` at `cddb111`:
**16 passed**.

### 2. Traceability integrity

- Every path in the `BLU-6` and `RED-7` `> Sources:` footers exists, and every named symbol is
  defined there: `engine/telemetry.py`, `session/manager.py::get_series`,
  `session/aar.py::worlds_at_times`, `engine/bus.py` and `engine/recovery.py`. The `BLU-6` route
  `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/{param}` is declared in `ui_web/server.py`.
  The `05` cross-link resolves.
- The §15.1 "Telemetry signatures + nominal ghost (history graph, per-instant)" row names the same
  code as both footers and maps to `BLU-6`/`RED-7`. The §15.2 `RED-7` row mirrors its footer
  exactly. The §15.2 `BLU-6` row omits the series route that its footer and §15.1 both name (**→ F5**).
- A whole-corpus section-ID check of `15-manual-traceability.md` and `16-learning-path.md` found
  43 IDs referenced, **0 orphans**, and **0 manual headings missing from the matrix**.
- No section IDs were added or renumbered, so `INDEX.md`, the learning path and ROADMAP need no
  changes. That is correct.

### 3. Coverage

- Both roles that own satellites, Blue and Red, have role-scoped history-graph content (`BLU-6`,
  `RED-7`).
- **White** can open the same drill-down for any asset. The fleet-row click (`app.js::openDrill`)
  is not cell-gated, and live `/telemetry/white/ISR-EO-1/snr_db` and `/telemetry/white/RED-ASAT/snr_db`
  both return **200**. Even so, §15.1 shows `—` in the White column, and no `WCM-n` section
  describes the drill-down. White's only pointer is `10-ui-reference.md` §10.13, reached from
  `WCM-16` since run #107. **→ F4** (FR-11110).
- The recently verified packages behind this behaviour (`IP-1261`, and the `IP-1262` sampling
  path that `get_series` does *not* use) are both present in the forward index.

### 4. Pedagogy

- **Audience fit** (MSTR-003/NFR-3600). The added prose is operator-facing: "where the line breaks
  is when it started". The one developer term, "per-instant replay", appears only in footers.
- **Module size** (NFR-3500): `13` is 249 lines, `14` 230, `05` 167, all within ~300.
  `10-ui-reference.md` is 442 lines. That is pre-existing for a reference module and outside run
  #102's change.
- **Sequencing/scaffolding:** run #102 made no sequencing choice, so no R600 grounding is
  required.
- **F3** is the pedagogical risk worth naming. Two adjacent Blue sections teach opposite mental
  models ("you find out at the next contact" vs. "the graph shows the exact onset") without saying
  why.

## Findings

| Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|
| F1 | `RED-7` (`14-red-cell-manual.md`); all 19 shipped vignettes' `red_forces` | **Safe-mode/recovery parity does not hold in any shipped vignette.** RED-7 says Red's satellites share Blue's bus SOH and safe-mode model, and tells Red to watch SOH dots and run the recovery chain. All 9 shipped Red satellites are authored without `bus_state`, so none can safe, show SOH, or need recovery. A bus anomaly inject on one is accepted and does nothing. The engine is symmetric; the content is not. The prose therefore mis-trains Red on mechanics they will never meet. This is not Critical: nothing was removed or renamed, and the capability exists for any vignette that authors a Red bus. The sentence predates run #102. | Medium | **Decision first**, then one of two owners. Option (a): `08-vignette-development` gives Red satellites authored `bus_state`, which changes vignette balance. Option (b): `08-training-manual-authoring` qualifies RED-7 ("…when the vignette gives Red a bus; none of the shipped vignettes do yet"). (b) is cheap and accurate now; (a) is a content/feature choice. |
| F2 | `session/manager.py` inject path (`anomaly`, `subsystem: bus`) | **Silent no-op exposed by F1.** A `subsystem: bus` anomaly targeting an asset with no `bus_state` returns `{"ok": true}` and changes nothing. White gets no signal that the inject failed to land. | Low | `00-intake` (bug → `07`) |
| F3 | `BLU-5` ⇄ `BLU-6` (and `RED-7`) | **Pass-gating tension.** The fleet rail's SOH is pass-gated (`ground_view`): "you find out at the next telemetry contact". The drill-down history graph samples every instant, so it can show an onset before any contact. Each statement is accurate as built, but neither says which surface it describes. Whether the graph *should* be pass-gated is the open `04` question `BL-0171`. | Low | `04-requirements-engineering` via `BL-0171` (adjudicate); then `08-training-manual-authoring` adds one clause to `BLU-6`/`RED-7` either way |
| F4 | `15-manual-traceability.md` §15.1 "Telemetry signatures" row (White = `—`); `12-white-cell-manual.md` | **White coverage gap (FR-11110).** White can open the subsystem drill-down and history graph for any asset (verified live), but no `WCM-n` section covers it and the matrix records no White mapping. | Low | `08-training-manual-authoring`. Add a sentence to `WCM-6` and map it in §15.1. Mind `BL-0179`: the White manual is already 320 lines. |
| F5 | `15-manual-traceability.md` §15.2 `BLU-6` row | The reverse row omits the `GET /telemetry/{cell}/{asset}/{param}` route that `BLU-6`'s footer and the §15.1 row both name. §15.2 is meant to mirror the footer. | Low | `08-training-manual-authoring` |

## Result

Run #102's own additions are **accurate against shipped behaviour**. That covers the
120-point/last-hour window, per-instant onset, export parity and the nominal ghost, all
independently driven live on a vignette, cells and parameters different from the shipped tests.
Footers resolve, and the playbook suite passed 16/16.

**5 findings: 0 Critical, 0 High, 1 Medium, 4 Low.** The Medium (F1) is in pre-existing RED-7
prose that this review reached because RED-7 was in scope. It is not in run #102's additions.

- F1 needs a cheap decision: qualify the prose now, or author Red buses as content.
- F2 is a small code-side validation bug for `00-intake`.
- F3 rides the existing `BL-0171`.
- F4 and F5 are small `08-training-manual-authoring` fixes and can be batched with F1(b).
