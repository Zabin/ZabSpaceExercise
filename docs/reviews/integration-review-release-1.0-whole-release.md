# Integration Review — Release 1.0, whole release as shipped

> **Stage:** 10 — Integration Review (fresh session and a different model from every earlier review; took no part in implementing or verifying any package in scope)
> **Reviewed commit:** `82436ba2e592d9a9afb91d4f93f8df8fffe07e00` (`archive/release-1.0`, the Release 1.0 commit), checked out clean in a separate worktree
> **Date:** 2026-11-09
> **Scope (release bucket):** Release 1.0 — all 94 `VERIFIED` Implementation Packages, reviewed together as the shipped product. This is a post-release review: the owner declared GO on 2026-11-01 ([REV-REL-004](release-assessment-release-candidate-10.md)).
> **Headline:** **0 Critical, 0 High, 5 Medium, 5 Low. All ten findings are new to the record** (none is on the release's known-deviation list, in the backlog, or in the Release 2.0 plan; the manual already warns about L-2 and L-3). The release composes: the full suite passes on the locked dependencies, and all 19 vignettes save, reload and replay to an identical world. Nothing here calls the GO into question. The five Mediums are real defects in shipped behaviour and belong in Release 2.0 milestone M1.
> **Previous reviews:** [RC-7 delta](integration-review-rc7.md), [RC-3 delta](integration-review-rc3-delta.md), [unreviewed packages](integration-review-unreviewed-packages.md), [release candidate 1](integration-review-release-candidate-1.md), [tranche 3](integration-review-tranche-3-release-push-remediation.md), [tranche 2](integration-review-tranche-2-white-controls-saves-test-origins.md), [18-package tranche](integration-review-18-package-tranche.md).

## 1. Scope confirmation and evidence base

A scripted recount at `82436ba` found 94 package rows in the Master Build Plan, 0 of them not `VERIFIED`, and 94 `VR-` files. The dependency lock's sha256 is `7e8d0e07…953b6`, the value the [release manifest](../releases/release-1.0.md) records.

The review ran on the release's own pinned dependencies: a fresh virtual environment built from `requirements.lock` (CPython 3.13.18; `pydantic` 2.14.2, `numpy` 2.5.4, as locked).

| Run | Command | Result |
|---|---|---|
| Full suite, locked dependencies | `python -m pytest` (Chromium present) | exit 0; **2240 passed, 4 skipped, 0 failed** (2244 collected). The four skips are the ones the manifest names. |
| RTM Test column | `python -m pytest --origin-report=rtm` | no change to the tree (the generated column is current) |
| Tree after the suite | `git status` | clean (the suite writes nothing into the repository) |
| Live server | `uvicorn spacesim.ui_web.server:app` from the release worktree | five probe scripts, about 1,000 requests, every route family |
| Replay and save equality | in-process, all 19 vignettes | see §2.2 |

The permanent gates (determinism, import guard, documentation integrity, test origins) and the 42 browser tests ran inside the full suite and passed.

**What this review did not do.** It did not re-verify any package. It read `ui_web/server.py`, `session/manager.py`, `session/inprocess.py` and `content/vignette_export.py` in full and the rest of the code only where a probe led. It did not drive the browser by hand; the browser evidence is the 42-test suite. No shipped vignette declares `roles_needed` or effect-gating rules, so the role gate and the approval gate were not exercised through shipped content.

## 2. Evidence per dimension

### 2.1 Interface consistency

Every mutating and reading route family was called on a live server with well-formed, malformed and cross-cell requests. The White-only guards, the Observer refusal, the non-finite guard and the time-control bounds behaved as their packages describe. Five disagreements between packages were found: M-1, M-3, M-5, L-1 and L-4.

### 2.2 Invariant sweep

- **Determinism.** For each of the 19 vignettes: start, eight rounds of Red-doctrine orders plus Blue observe, jam, cyber, engage, downlink, command and manoeuvre orders, an immediate inject and a future-dated inject, 2 hours of simulated time. Then (a) save and reload, (b) continue both copies 30 minutes, (c) replay the event log to the live instant. **All 19: reloaded world equals live, continued worlds equal, replayed world equals live, 0 `handler_error` entries.**
- **Engine import boundary, no wall clock, no global RNG.** `test_import_guard.py` and `test_determinism.py` passed in the full run.
- **Fog of war.** For each of the 19 vignettes and both cells, 17 cell-scoped read routes (view, scene, orders, alarms, next contacts, conjunctions, SSN requests and coverage, activity, role scope, telemetry, telemetry CSV, windows, manoeuvre ledger, recovery, RIC view, TLE) were searched for the id of every opposing asset and sensor the cell holds no track on. **No leak in any read route.** The only hits were Red's own orders naming their Blue targets, which is the known AI-Red deviation (REV-REL-004 A.7 item 8). The order-preview routes are a different matter: finding M-1.
- **Plan-first, sub-stepped clock, content as data.** No violation found. M-2 is a gap in what the clock schedules, not a skipped event.

### 2.3 Behavioural coherence

Four places where packages that each pass on their own give a wrong combined result: M-2 (clock span against the bus tick schedule), M-3 (parameters against force edits, seats and roles), M-4 (save-as-scenario against objectives, parameters and SSN), M-5 (order registry against the save validator).

### 2.4 Traceability coherence

94 packages, 94 `VERIFIED`, 94 `VR-` files. The RTM Test column regenerates with no difference. The status-ledger, index and broken-link checks passed in the suite. One stale count inside `CLAUDE.md`: L-5.

### 2.5 Documentation coherence

- **Per-package documentation audit.** 89 of the 94 `VR-` files have no "Documentation audit" section. This is covered by the owner's recorded decision (`BL-0391`): release-level documentation coverage for Release 1, per-package rules for new work. The release-level coverage is [REV-TRN-013](training-review-final-rc11.md). Not a finding.
- **Manual-impact items open for this scope:** none in the backlog.
- **Tutorials:** `test_vignette_tutorials.py` passed in the full run.
- **Manual against behaviour, spot checks.** The manual does warn that adding an object under an existing id replaces it (`12b`, `12d`), and that the oldest session is dropped at 32 (`09a`). It does not mention the bus freeze (M-2) or the parameter reset (M-3), and its list of what save-as-scenario leaves out is incomplete (M-4).

## 3. Findings

| Finding | Packages / artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| **M-1** Order previews return ground truth to a cell | `inprocess.py` `compute_jam`, `compute_engage`, `compute_maneuver`, `compute_cyber`; `app.js` `computeEngage`; invariant 3; `FR-6210` | The four preview routes take the caller's `cell` and ignore it: no ownership check on the actor, no custody check on the target. In `geo-rpo-shadowing`, with Blue holding **zero tracks**, a Blue-named `maneuver/compute` on `RED-INSP` returned its true orbit (a, e, i, RAAN, argument of perigee); `engage/compute` returned the true range (441.54 km) and altitude; `jam/compute` on a Red ground asset returned its true latitude and longitude. The matching read routes (`telemetry`, `windows`) correctly answer 404. The Blue console's engage preview displays the truth-derived kill probability and target altitude. `CLAUDE.md` states the fog filter is applied to every cell-scoped response. A hostile participant gains nothing new (`/godview` is open on the trusted LAN), but an honest console now shows numbers the cell's own tracks do not support. | Medium | `07-implementation-planning` (remediation package: previews use the caller's own assets and its own Track estimate, or refuse) |
| **M-2** The bus model stops at four times the estimated duration; the clock does not | `manager.py` `horizon`, `_arm_schedule`; `IP-1076` span ceiling; `busmodel.py` | Bus ticks, condition-inject checks and environmental-anomaly checks are scheduled only to `start + 4 × estimated_duration_min`. The clock, orders and access windows run on to 366 days. In `leo-isr-denial` the last `bus_tick` is at +4.00 h; at +12 h the battery state of charge and `in_eclipse: true` are unchanged from +4 h, with no message. The horizon is 2 h for four vignettes. At the 60× clock rate that is two minutes of wall time. No shipped objective deadline lies past its horizon. Not in any manual. | Medium | `04-requirements-engineering` (state the rule: tick to the span ceiling, or stop the clock at the horizon with a White message), then `07` |
| **M-3** Changing a parameter before Start silently discards earlier setup | `inprocess.py` `set_parameter`; `IP-1101`/`IP-1174` force edits; `IP-1151` roles; `IP-1174` seats | `set_parameter` rebuilds the session from the vignette file. Sequence on a live server: add a TLE object, bind a role, declare two seats, edit an asset's group, then `POST /param`. Reply `{"ok": true}`. Afterwards the TLE object is gone, the group edit is gone, the seat list is `{}` and the seat is unbound. By the code, a vignette that declares mandatory roles would then refuse Start again (no shipped vignette declares roles, so this part was not run). Not in the manual. | Medium | `07-implementation-planning` (remediation package; carry the setup across, or refuse and say why) |
| **M-4** Save-as-scenario changes the objectives' deadlines and drops more than is documented | `vignette_export.py`; `FR-5510`; `12d` White manual; REV-REL-004 A.7 item 4 | The exported vignette carries forces, sensors, tracks, ROE, objectives and space weather only. Saving each vignette at +30 min and loading the result: **objective deadlines differ in 18 of 19** (deadlines relative to the start move 30 minutes later; parameter-derived ones fall back to the default, so `leo-isr-denial`'s landing deadline moves from 09:00 to 07:00 UTC). SSN networks are dropped (`geo-rpo-shadowing`, `sda-custody-hunt`, `multi-domain-taiwan`), all parameters are dropped, and the estimated duration resets to 60 minutes. The manual says the objectives are kept and lists injects, gates, brief, tutorial, Red doctrine and live ROE changes as the omissions; deadlines, SSN and parameters are not mentioned. The known-deviation list names four omissions. | Medium | `06-feature-specification` (widen `BL-0418`, the save-as-scenario completeness item); `08-training-manual-authoring` for the `12d` list until then |
| **M-5** A saved session can be refused by its own loader | `orders.py` order registry; `manager.py` `save_state`, `validate_save` (`IP-1103`) | `POST /order` with a `cell` other than `blue` or `red` (for example `white`, or a mistyped name) is rejected but still registered, with an order id. `save_state` writes it. `validate_save` requires every order's cell to be `blue` or `red`, so loading that save returns 400 `save key 'orders' entry 0 is malformed`. One stray request makes every later save of that session unloadable, and nothing says so at save time. The console maps a White order to the asset's owner, so the trigger is an off-console request or a neutral-owned actor. | Medium | `07-implementation-planning` (remediation package: refuse the cell at the route, and do not register it) |
| **L-1** Seven requests answer 500 | `server.py` `session_brief` (no session check); `inprocess.py` `set_parameter`, `preview_consequence`, `compute_jam`, `compute_engage`, `compute_cyber`, `compute_sigint`; `NFR-1600` | `GET /brief/{cell}` on an unknown session; `POST /param` with `ssn_blue_budget: "abc"`; `preview/consequence` with a non-numeric `escalation_weight`; `jam`, `engage`, `cyber` and `sigint` previews with a non-numeric parameter. Each is an unhandled exception. The same bad override on `POST /api/sessions` is a correct 400. | Low | `07` (fold into the M1 session-control refusals package) |
| **L-2** Force-add under an existing id replaces the asset | `manager.py` `_force_add_tle_object`, `add_ground_asset` | Adding a TLE as `ISR-EO-1` replaced the authored satellite: owner blue to red, bus state and payload gone. Documented as a trap in `12b` and `12d`, but there is no refusal and bulk import already refuses duplicates within one file. | Low | `07` (with the authoring-validation package) |
| **L-3** The session cap can drop the running exercise | `inprocess.py` `_evict_if_full`; `server.py` creation routes | The 33rd session evicts the oldest one whether or not it is running, and creation is open to a request that names no seat. 33 draft creations by a seatless client turned a started session into 404. The cause is documented in `09a`. | Low | `07` (evict unstarted sessions first) |
| **L-4** Unknown cell names are accepted on reads | cell-scoped `GET` routes; `creator/seats` | `view`, `scene`, `orders`, `alarms`, `next_contacts`, `coaching`, `conjunctions`, `ssn/…` and `brief` answer 200 for a cell named `junk`; only `/activity` refuses (400, `IP-1088`). `creator/seats` stores any string as a cell and accepts a negative count. | Low | `07` (with the seat-uniformity package) |
| **L-5** `CLAUDE.md` gives two browser-test counts | `CLAUDE.md` status line and build/test commands block | The status line says 42 browser tests (correct); the commands block still says "IP-1340, 33 tests". | Low | `08-code-implementation` doc step (the `CLAUDE.md` currency item in M0) |

Reproduction detail for each Medium is in the Description cell; every one was observed on the live release server or in-process on the release worktree, not inferred from reading code.

## 4. What was exercised to earn the clean dimensions

- Determinism, replay and save/resume: 19 of 19 vignettes under mixed orders and injects (§2.2), plus the suite's own gates.
- Fog of war on read routes: 19 vignettes × 2 cells × 17 routes, no leak.
- White-only and Observer refusals, non-finite guard, time-control bounds, unknown-session handling (one miss, L-1), load-time vignette validation, save validation: probed live, behaved as specified.
- Live ROE change is reflected in the mission brief on the next read.
- Traceability: package, VR and ledger counts; RTM regeneration.

## 5. Quality gate

- [x] Every package in scope confirmed `VERIFIED` before the review began (94 of 94).
- [x] All five dimensions exercised; each says what was checked.
- [x] Documentation coherence includes the per-package documentation-audit sweep and the open manual-impact list (none).
- [x] Full suite and permanent gates run against the reviewed commit, results recorded.
- [x] Every finding has a severity and a recommended owner; none was fixed in this pass.
- [x] Nothing but this report and its `ROADMAP.md` review row was written.
