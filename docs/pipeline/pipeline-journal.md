# Pipeline Journal

> **Maintained by the `00-pipeline-manager` skill — single writer.** Humans and other sessions
> read this file; only the manager writes it. It is the manager's persistent memory of where the
> documentation-driven-development pipeline stands (see
> [`.claude/skills/README.md`](../../.claude/skills/README.md) for the pipeline itself). It is a
> **cache of truth, never truth**: the tree's ledgers (`ROADMAP.md`, the Master Build Plan, the
> per-theme indexes) are authoritative, and every manager run reconciles this file against them —
> where they disagree, the tree wins and the correction is logged below.

[↑ Docs index](../INDEX.md) · [Pipeline README](../../.claude/skills/README.md) ·
[Master Build Plan](../implementation/00-master-build-plan.md) · [ROADMAP](../../ROADMAP.md)

## Position

- **Updated:** 2026-07-03 (run #8)
- **Increment:** v1 baseline follow-through — closing the gaps the 2026-07 strategic review and
  feature-planning pass opened (FS-112–115 packaged, four of five packages authorized; **all five
  now implemented** — one independently verified, four `COMPLETE` pending verification. The user's
  "complete outstanding 08 code implementation" request is now fully drained: **zero packages
  remain `READY`** on the Master Build Plan).
- **Pipeline state:**
  - Stages 01–06 ✅ current for this increment: GDS-00…10 authored with closed gates
    (`docs/architecture/INDEX.md` §1); requirements baseline approved (`docs/requirements/`);
    feature-planning corpus complete (`docs/feature-planning/`); all 18 catalog Feature Specs
    authored, FS-108/FS-202 candidates excluded per MSTR-006 §3.
  - Stage 07 ✅ FS-112–115 gap closed run #1: `07-implementation-planning`'s Tranche 1 authored
    `IP-1120`, `IP-1130`, `IP-1140`, `IP-1150`, `IP-1151`. Committed `5d84f2c`.
  - **MSTR-006 §3 authorization round (run #2):** authorized `IP-2010`, `IP-1130`, `IP-1120`,
    `IP-1151`; **did not** authorize `IP-3010`. Committed `765e3c7`.
  - Stage 09 ✅ first VR issued (run #3): `09-package-verification` verified **IP-1150**
    (Vignette Selection) — [`VR-1150`](../implementation/verification/VR-1150-vignette-selection.md),
    full suite 490 passed/3 skipped, both permanent gates green, one Low finding (a factually wrong
    "no test covers zero-overrides" claim in the package — no functional gap). `IP-1150` flipped
    `COMPLETE → VERIFIED`. This cleared `IP-1120`/`IP-1151`'s sole blocking dependency; both
    flipped `BLOCKED → READY` (already authorized). RTM's stale `FR-4110` `Test`/`Impl. Package`
    cells (`UNASSIGNED`) corrected. Committed `5938617`.
  - Stage 07 ✅ IP-2010 design amendment (run #4, this run): the recorded next step
    (`08-code-implementation` on IP-2010) was gated on ripe backlog item `BL-0002` (the "aware vs.
    unaware" divergence-signal design question). `AskUserQuestion` put three resolution options to
    the project owner; the owner chose to instrument an explicit decision-time signal rather than a
    post-hoc heuristic. `07-implementation-planning` amended `IP-2010` to v1.1: added
    `custody_confidence_at_decision` (new `engine/custody.py` helper, captured in
    `engine/orders.py`'s `_exec_payload()`, read back — never recomputed — by
    `score_belief_truth_divergence`); updated Architecture Components, Files to Modify,
    Implementation Tasks, Tests to Add, Definition of Done, Verification Checklist, Risks, and
    Rollback Considerations; corrected the Master Build Plan's stale risk note. No status/
    authorization change — `IP-2010` remains `READY`+authorized. Committed `d07ebe8`, pushed to
    `claude/pipeline-skill-ijwd1f`, draft PR opened:
    [#45](https://github.com/Zabin/ZabSpaceExercise/pull/45) (subscribed to PR activity).
  - Stage 08 ✅ IP-2010 implemented (run #5): `08-code-implementation` built
    `session/assessment.py` (three scoring functions + report) and the `custody_confidence_at_decision`
    capture in `engine/custody.py`/`engine/orders.py`, wired through `session/inprocess.py`, a new
    `/api/sessions/{sid}/assessment` endpoint, and an additive White Cell Dashboard panel. 17 new
    tests; full suite 507 passed/3 skipped (was 490/3), both permanent gates green. `IP-2010`
    `READY` → `COMPLETE`. Cleared `IP-3010`'s "`IP-2010` → `COMPLETE`" blocker (its authorization
    blocker remains). Updated Master Build Plan, `packages/INDEX.md`, RTM (`FR-10110`), `ROADMAP.md`,
    `CLAUDE.md` Code Map. Committed `c5e2751`, pushed to `claude/pipeline-skill-ijwd1f` (same PR
    [#45](https://github.com/Zabin/ZabSpaceExercise/pull/45), still draft).
  - Stage 08 ✅ IP-1120 implemented (run #6, this run, override mode at the user's explicit
    request to "complete outstanding 08 code implementation"): `08-code-implementation` selected
    `IP-1120` (lowest-ID of the three READY+authorized candidates). Resolved one `classification`
    value once in `SessionManager`, threaded through the session-create response, `list_sessions()`
    (so a joining/pop-out tab matches the creating tab — a documented deviation from the package's
    literal "session-state response app.js already polls" text), `aar.export_csv`/`export_json`
    (new `AARReport.classification` field), and `save_state`/`from_state` (also documented as
    restoring on resume, contrary to the package's literal "from_state is unaffected" text — both
    deviations are within already-in-scope files, not a scope expansion). Replaced the hard-coded
    banner literal in `index.html`; added a White-Cell-only override control. 12 new tests; full
    suite 519 passed/3 skipped (was 507/3), both permanent gates green. `IP-1120` `READY` →
    `COMPLETE`. Also discovered and corrected: `IP-1120`'s own package doc had drifted (still read
    `BLOCKED` after `IP-1150` reached `VERIFIED` in run #3 — proceeded on the Master Build Plan's
    authoritative status, fixed the package doc's stale text as bookkeeping) and a malformed RTM row
    for `NFR-3100` (missing its `Impl. Package` column). Updated Master Build Plan, `packages/INDEX.md`,
    RTM (`FR-4510`, `NFR-3100`), `ROADMAP.md`. Committed `c87d77d`, pushed to
    `claude/pipeline-skill-ijwd1f` (same PR [#45](https://github.com/Zabin/ZabSpaceExercise/pull/45)).
    Two packages were simultaneously `READY` and authorized after run #6: `IP-1130` (Observer
    Read-Only Access), `IP-1151` (Seat-to-Role Assignment).
  - Stage 08 ✅ IP-1130 implemented (run #7, this run, override mode, same "complete outstanding 08
    code implementation" request): `08-code-implementation` selected `IP-1130` (the sole remaining
    lower-ID READY+authorized candidate besides `IP-1151`). Added a fourth, White-Cell-designated
    Observer seat: `session/inprocess.py` gains `set_observer_view`/`get_observer_view`/
    `observer_designation` (dispatching unmodified to `get_godview`/`get_view`); `ui_web/server.py`
    gains a `_reject_observer(cell)` guard on 22 mutating routes — re-derived from the live route
    table per the package's own explicit instruction, one more than its own enumerated list
    (`/preview/consequence`); ten cell-less routes gained a `cell` query param, centrally injected
    by `app.js`'s `api.post()` wrapper rather than touching ~30 call sites. 28 new tests
    (parametrized across the full route table); full suite 547 passed/3 skipped (was 519/3), both
    permanent gates green. `IP-1130` `READY` → `COMPLETE`. Updated Master Build Plan,
    `packages/INDEX.md`, RTM (`FR-6510` — also corrected a stale citation there, itself a symptom
    of the same title-mismatch defect the package flagged), `ROADMAP.md`, `CLAUDE.md`. Committed
    `7ea81d9`, pushed (PR #45). Harvested 2 findings → `BL-0011` (route-guard maintenance risk,
    DEFERRED), `BL-0012` (FR-6510 RTM title mismatch, late-harvested from run #1, DEFERRED to `04`).
    One package remains `READY` and authorized, zero remaining gate: `IP-1151` (Seat-to-Role
    Assignment).
  - Stage 08 ✅ IP-1151 implemented (run #8, this run, override mode, same "complete outstanding 08
    code implementation" request — the last package in that queue): `08-code-implementation`
    selected `IP-1151` (the sole remaining `READY`+authorized candidate). Added
    `Vignette.roles_needed`/`RoleRequirement` (additive, absent for all 19 existing vignettes),
    `SessionManager.assign_role`/`_role_covers`/`staffing_report`, and a hard gate in
    `InProcessSession.start()` that refuses to start while any mandatory `roles_needed` entry has
    no covering seat assignment; `/roles/assign`+`/roles/staffing` endpoints; a White-Cell-only
    seat-assignment UI step. Also fixed a pre-existing client bug load-bearing to this package's own
    gate: `app.js`'s `start()` previously ignored the `/start` Ack's `ok` field entirely. 12 new
    tests; full suite 559 passed/3 skipped (was 547/3), both permanent gates green. `IP-1151`
    `READY` → `COMPLETE`. Also discovered and documented, not fixed: the package's own text claimed
    its Role Assignment records were "already `VERIFIED`" as consumed by an `FS-105`/`IP-1050`/
    `IP-1051` command-filtering mechanism — checked against the live code and found **false**; no
    role-based command-authorization concept exists anywhere in the codebase (every check is
    `cell`-based). Documented prominently in `IP-1151`'s own Status/Definition-of-Done/Verification
    Checklist/Dependencies/Risks/Rollback Considerations sections and as Master Build Plan Risk item
    8; not a defect in `IP-1151`'s own scope (`FS-115` explicitly excludes runtime enforcement).
    Updated Master Build Plan, `packages/INDEX.md`, RTM (`FR-4210`), `ROADMAP.md`, `CLAUDE.md`,
    `docs/design/04-data-model.md`. Committed `9e3861a`, pushed (PR #45). Harvested 2 findings →
    `BL-0013` (DONE, fixed same run), `BL-0014` (DEFERRED — the FS-105 consumer-doesn't-exist
    finding, Medium severity, routed to `06-feature-specification`'s territory). **Zero packages
    remain `READY` on the Master Build Plan** — the user's "complete outstanding 08 code
    implementation" request is now fully drained.
  - Stage 09 🚧 five gaps remain: `IP-1140` (Hot-Seat Hand-Off), `IP-2010` (Competency Assessment),
    `IP-1120` (Classification Banner), `IP-1130` (Observer Read-Only Access), and `IP-1151`
    (Seat-to-Role Assignment, new this run) are all `COMPLETE`, awaiting their own verification pass
    (`IP-1140`'s should also adjudicate its documented FR-6610 trigger/menu divergence; `IP-2010`'s
    should confirm `BL-0007`; `IP-1120`'s should confirm the package-doc drift fix and its two
    documented task-text deviations; `IP-1130`'s should confirm the re-derived 22-route guard and
    its two documented deviations; `IP-1151`'s should independently re-confirm the FS-105
    non-consumption finding rather than re-deriving it from scratch, per the package's own
    Verification Checklist note). The original 11 as-built packages (IP-1010…IP-1110) still predate
    the VR-report convention and carry no `VR-xxxx` on disk — a standing gap, unchanged this run,
    not this increment's focus.
  - Stages 10–11 ⛔ never run.
- **Backlog:** 14 open ([`backlog.md`](backlog.md)): `BL-0014` is `NEW` this run (harvested from
  `IP-1151`'s Implementation Summary Outstanding Issues), `DEFERRED` (Medium — routed to `06`, not
  blocking). `BL-0013` harvested and `DONE` same run (fixed as part of `IP-1151`'s own scope).
  `BL-0003`/`BL-0007` (SCHEDULED — ride `09` on `IP-1140`/`IP-2010` respectively), `BL-0005`
  (NEEDS-USER — IP-3010 authorization, still not asked), `BL-0001`/`BL-0004`/`BL-0006`/`BL-0008`/
  `BL-0010`/`BL-0011`/`BL-0012`/`BL-0014` (DEFERRED with named triggers, not yet ripe). `BL-0009`
  `DONE`. No entry is due at the next step.
- **Next step:** `09-package-verification` on any of the five `COMPLETE` packages
  (`IP-1120`/`IP-1130`/`IP-1140`/`IP-1151`/`IP-2010`) — all equally available, no dependency
  ordering between them; verification is now the only per-package work left in this increment
  besides `IP-3010`'s standing authorization gate. Recommend starting with `IP-1151` or `IP-1130`
  (most recently implemented, freshest in context) or `IP-1140` (oldest `COMPLETE`, longest
  unverified).
- **Open gates:** `IP-3010` still requires its own separate MSTR-006 §3 authorization — `BL-0005`
  remains the standing, not-yet-asked `NEEDS-USER` item. PR
  [#45](https://github.com/Zabin/ZabSpaceExercise/pull/45) (carries runs #4–#8's work) is open/draft
  — being monitored for CI/review activity outside the pipeline-manager loop.

## Run log

*(append-only, newest last — one row per manager run, including status/sync/gate-stop runs)*

| # | Date | Mode | Skill invoked | Target | Outcome | Next step recorded |
|---|---|---|---|---|---|---|
| 0 | 2026-07-03 | sync | — | whole tree | Journal initialized; position derived from `ROADMAP.md`, `docs/architecture/INDEX.md`, `docs/implementation/00-master-build-plan.md` + `packages/INDEX.md`, `docs/features/feature-index.md` | `07-implementation-planning` on FS-112–115 |
| 1 | 2026-07-03 | advance | `07-implementation-planning` | FS-112, FS-113, FS-114, FS-115 | Verified each Feature's real build status against `spacesim/`; authored TWBS Tranche 1 + 5 packages (`IP-1120` BLOCKED, `IP-1130` READY, `IP-1140` COMPLETE, `IP-1150` COMPLETE, `IP-1151` BLOCKED); updated Master Build Plan/packages INDEX/ROADMAP/FS cross-links; commit `5d84f2c` | `09-package-verification` on IP-1150 |
| 2 | 2026-07-03 | gate | — | IP-2010, IP-1130, IP-1120, IP-1151, IP-3010 (authorization review) | User reviewed all 5 packages gated on MSTR-006 §3 via `AskUserQuestion`; authorized `IP-2010`, `IP-1130`, `IP-1120`, `IP-1151`; did **not** authorize `IP-3010`. Recorded in each package's own header/Definition-of-Done, Master Build Plan, packages INDEX, ROADMAP. | `08-code-implementation` on IP-1130 or IP-2010, or `09-package-verification` on IP-1150 or IP-1140 (genuinely parallel; IP-1150 verification recommended first) |
| 3 | 2026-07-03 | advance | `09-package-verification` | IP-1150 | Verified against live tree: full suite 490 passed/3 skipped, both permanent gates green; VR-1150 written (VERIFIED); corrected stale RTM FR-4110 Test/Impl. Package cells; IP-1150 COMPLETE→VERIFIED; cleared IP-1120/IP-1151's blocking dependency, both BLOCKED→READY (already authorized); commit `5938617` | `08-code-implementation` on IP-2010 (critical-path leverage; IP-1130/IP-1120/IP-1151 equally READY+authorized in parallel) |
| 4 | 2026-07-03 | advance (gate resolved inline) | `07-implementation-planning` | IP-2010 (amendment) | Gate check: BL-0002 (aware/unaware divergence-signal design question) was ripe on the recorded next step (IP-2010); `AskUserQuestion` offered 3 resolution options, user chose "instrument a new explicit signal." `07-implementation-planning` amended IP-2010 v1.0→v1.1 (custody_confidence_at_decision captured in orders.py `_exec_payload()` via new custody.py helper, read back by score_belief_truth_divergence, never recomputed); corrected Master Build Plan's stale risk note; no status/authorization change. BL-0002 → DONE. Committed `d07ebe8`, pushed, draft PR #45 opened and subscribed. | `08-code-implementation` on IP-2010 (zero remaining gate; IP-1130/IP-1120/IP-1151 equally available in parallel) |
| 5 | 2026-07-03 | advance | `08-code-implementation` | IP-2010 | Implemented per v1.1: session/assessment.py (new, 3 scoring functions + report) + custody_confidence_at_decision capture (custody.py new helper, orders.py's _exec_payload); inprocess.py wrapper, /api/sessions/{sid}/assessment endpoint, White Cell Dashboard panel (index.html + app.js). 17 new tests; full suite 507 passed/3 skipped (was 490/3); both permanent gates green. Updated Master Build Plan/packages-INDEX/RTM(FR-10110)/ROADMAP/CLAUDE.md; IP-2010 READY→COMPLETE; cleared IP-3010's IP-2010-COMPLETE blocker (authorization blocker remains). Harvested 2 findings from Implementation Summary Outstanding Issues → BL-0006 (DEFERRED), BL-0007 (SCHEDULED, rides 09 on IP-2010). Committed `c5e2751`, pushed (PR #45). | `09-package-verification` on IP-2010 (adjudicating BL-0007 in the same pass); IP-1140 verification and IP-1130/IP-1120/IP-1151 coding remain equally available in parallel |
| 6 | 2026-07-03 | override (`run 08-code-implementation`, at user's explicit request to "complete outstanding 08 code implementation") | `08-code-implementation` | IP-1120 (lowest-ID of 3 eligible candidates) | Resolved one classification value in SessionManager, threaded through session-create response, list_sessions(), aar.export_csv/export_json, save_state/from_state (2 documented deviations from the package's literal task text, both within already-in-scope files); replaced hard-coded banner literal; added White-Cell override control. 12 new tests; full suite 519 passed/3 skipped (was 507/3); both permanent gates green. IP-1120 READY→COMPLETE. Also fixed: IP-1120's own package doc had drifted (still read BLOCKED after IP-1150 reached VERIFIED in run #3); a malformed NFR-3100 RTM row (missing Impl. Package column). Updated Master Build Plan/packages-INDEX/RTM(FR-4510,NFR-3100)/ROADMAP. Harvested 3 findings → BL-0008 (DEFERRED), BL-0009 (DONE, fixed same run), BL-0010 (DEFERRED, late-harvest from run #1). Committed `c87d77d`, pushed (PR #45). | `09-package-verification` on IP-1120 (or IP-2010/IP-1140, equally available); IP-1130/IP-1151 coding remain available in parallel |
| 7 | 2026-07-03 | override (`run 08-code-implementation`, same "complete outstanding 08 code implementation" request) | `08-code-implementation` | IP-1130 (lower-ID of 2 remaining eligible candidates) | Added Observer seat: session/inprocess.py (set_observer_view/get_observer_view/observer_designation, dispatching unmodified to get_godview/get_view); ui_web/server.py's _reject_observer(cell) guard on 22 mutating routes, re-derived from the live route table (1 more than the package's own list: /preview/consequence); 10 cell-less routes gained a query param, centrally injected by app.js's api.post() wrapper. 28 new tests (parametrized across the full route table); full suite 547 passed/3 skipped (was 519/3); both permanent gates green. IP-1130 READY→COMPLETE. Also corrected a stale FR-6510 RTM citation (symptom of the same title-mismatch defect the package flagged). Updated Master Build Plan/packages-INDEX/RTM(FR-6510)/ROADMAP/CLAUDE.md. Harvested 2 findings → BL-0011 (DEFERRED, route-guard maintenance risk), BL-0012 (DEFERRED, late-harvest FR-6510 title mismatch from run #1). Committed `7ea81d9`, pushed (PR #45). | `09-package-verification` on IP-1130 (or IP-1120/IP-2010/IP-1140, equally available); IP-1151 is the last READY+authorized package remaining in the "complete outstanding 08" queue |
| 8 | 2026-07-03 | override (`run 08-code-implementation`, same "complete outstanding 08 code implementation" request — last package in that queue) | `08-code-implementation` | IP-1151 (the last remaining READY+authorized candidate) | Added Vignette.roles_needed/RoleRequirement (additive, absent for all 19 existing vignettes); SessionManager.assign_role/_role_covers/staffing_report; InProcessSession.start() hard-gated on any unmet mandatory role; /roles/assign+/roles/staffing endpoints; White-Cell-only seat-assignment UI step. Fixed a pre-existing app.js bug (start() ignored the /start Ack's ok field) load-bearing to this package's own gate. 12 new tests; full suite 559 passed/3 skipped (was 547/3); both permanent gates green. IP-1151 READY→COMPLETE. Discovered and documented (not fixed, not this package's scope): the package's own text claimed its Role Assignment records were "already VERIFIED" as consumed by FS-105/IP-1050/IP-1051's command-filtering — checked against the live code and found false, no role-based command-authorization concept exists anywhere in the codebase. Documented in IP-1151's own Status/DoD/Verification-Checklist/Dependencies/Risks/Rollback-Considerations and Master Build Plan Risk item 8. Updated Master Build Plan/packages-INDEX/RTM(FR-4210)/ROADMAP/CLAUDE.md/data-model.md. Harvested 2 findings → BL-0013 (DONE, fixed same run), BL-0014 (DEFERRED, Medium, routed to 06 — the FS-105 consumer-doesn't-exist finding). Committed `9e3861a`, pushed (PR #45). Zero packages remain READY on the Master Build Plan. | `09-package-verification` on any of the five COMPLETE packages (IP-1120/IP-1130/IP-1140/IP-1151/IP-2010), all equally available; IP-3010's authorization gate (BL-0005) remains the only other open item |
