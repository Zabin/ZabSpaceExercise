# IP-1084 — Controller-Set Anomalies and Sensor Outages Are Told to the Owner and to White Cell Only, Never to the Opposing Cell (FR-4430, FR-4440, FR-6210)

> **Package ID:** IP-1084
> **Version:** 1.0
> **Status:** READY — authored 2026-10-25 by `07-implementation-planning` (release-push remediation pass 8). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (fix bugs before release; no new features) and the run #262 go-ahead (review the unreviewed packages, then fix before release), covers it: finding `H-1` of the unreviewed-packages integration review is a fog-of-war violation (load-bearing invariant 3) in `VERIFIED` code. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1062](IP-1062-condition-triggered-injects-and-new-effects.md), [IP-1063](IP-1063-inject-effect-fire-time-validation.md), [IP-1064](IP-1064-condition-inject-follow-ups.md), [IP-1230](IP-1230-space-weather-index-coupling.md) (all `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 8"); source: [`integration-review-unreviewed-packages.md`](../../reviews/integration-review-unreviewed-packages.md) `H-1`.
> **Produces:** an `anomaly` / `sensor_outage` notice (scheduled inject, condition-triggered inject, or the environmental-anomaly tick) that reaches White Cell with the controller's true cause, the owning cell without it, and the opposing cell not at all; a cross-cell fog regression matrix over every message-emitting inject effect.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) (inject effects, `FR-4430`); [FS-123 — Space-Weather Index Coupling](../../features/FS-123-space-weather-index-coupling.md) (`FR-4440`)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/cells.py`](../../../spacesim/session/cells.py) (read-only reference: the per-cell message filter)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Bug-fix package (one defect, one seam). Prose only; no code in this document.*

---

## Package ID

IP-1084.

## Title

Address controller-set anomaly and sensor-outage notices by ownership: White gets the cause, the owner gets the fact, the other cell gets nothing.

## Objective

**The defect (review `H-1`, High; reproduced read-only over HTTP in the planning pass).** `SessionManager._apply_inject_effects` (`session/manager.py`, the `anomaly` branch at about line 1631 and the `sensor_outage` branch at about line 1639) appends one world message addressed `["white", "blue", "red"]` with the text `"<ASSET>: anomaly declared (<true cause>)"` or `"<SENSOR>: sensor outage declared (<true cause>)"`. `CellController.view` (`session/cells.py`, line 40) returns exactly the messages whose `to` list contains the cell, so the broadcast reaches both players. Reproduced on `01-leo-isr-denial` (`POST /inject` with an `anomaly` on Blue's `ISR-EO-1`, a `sensor_outage` on Blue's `BLUE-RADAR`): `GET /view/red` returns `ISR-EO-1: anomaly declared (space_weather)` and `BLUE-RADAR: sensor outage declared (jammed-by-ctrl)`. Red learns a Blue-only asset's id, that it is safed or blind, and the controller's true cause; Blue is handed the answer to the diagnose-the-cause step of the recovery loop through a channel its own telemetry would not give. The environmental-anomaly tick (`_h_env_anomaly_check`, `FR-4440`) and the condition-triggered inject path (`_h_condition_check`) both reach the same two branches, so every shipped route to these effects leaks.

**The correct disclosure, derived from the requirements (Design Decision 1).** Nothing in `FR-4430` or `FR-4440` states who is told; the answer comes from the fog rules they sit under, and the gap is routed to `04` (below). `FR-6210` (Postcondition: "no field of another cell's private state appears in the returned `CellView`"; the view exposes "only that cell's own assets, held tracks, perceivable effects, and addressed messages"), `ADR-0004` and `CLAUDE.md` invariant 3 make the message's **address** the fog decision: a notice about a Blue asset's private state may not be addressed to Red. `CellController`'s own header states the principle for effects: a cell sees effects on its own assets "as symptoms whose source is hidden unless the effect is overtly attributable". `FR-4430`'s Postcondition (the true cause "is recorded in the event log exactly as the controller set it, never re-derived") makes the cause a controller-side record, not something the affected player is told. The package therefore fixes:

| Recipient | Sees |
|---|---|
| White Cell | the notice **with** the controller's true cause (today's text, unchanged) |
| The cell that owns the target asset or sensor (`blue` or `red`) | the fact only: `"<ID>: anomaly declared"`, `"<ID>: anomaly cleared"`, `"<ID>: sensor outage declared"`, `"<ID>: sensor outage cleared"`; no cause |
| The opposing cell | nothing. What it can learn about the other side's spacecraft or sensor is what its own custody already gives it (a `Track`), which these effects do not alter |
| Target owned by `neutral` | White only |

**Left alone, by decision (pinned by tests so a later change is deliberate).** The other message-emitting effects keep their recipients: `gs_outage` (all three cells; the existing precedent, and a ground-station outage is arguably public), `space_weather` (all three; public), `spawn_debris`'s optional message (all three; a debris cloud is public), `conjunction_warning` (White and Blue only, as built; see Owner decisions), an authored `message` effect (the author's own `to`, as today), `scripted_manoeuvre` (White only), a skipped-effect notice (White only), `forced_custody_loss` and `reveal_asset` (no message). Whether `gs_outage` and `conjunction_warning` should also be ownership-addressed is an owner question, not a defect this package decides.

## Requirements Covered

| ID | How |
|---|---|
| `FR-6210` | No cell's `CellView` carries a notice about the other cell's private asset or sensor state (the fix; the matrix pins every effect). |
| `FR-4430` | The anomaly and sensor-outage effects still apply exactly as before (safe mode with the controller's cause recorded; comms red; sensor degraded); the cause stays a controller-side record, now also not broadcast; the AC "no other cell's fog-of-war-filtered view is affected" holds for the notices as well as the custody effect. |
| `FR-4440` | An environment-induced anomaly (the seeded tick) is announced under the same rule as a scheduled one. |
| `FR-4420` | A condition-triggered inject firing these effects is announced under the same rule. |
| Determinism (`ADR-0002`, load-bearing invariant 1) | Recipients are a pure function of `(world, effect)`; replay equals live. |

## Architecture Components

`session/manager.py::SessionManager._apply_inject_effects` (the only code that changes), reached from `_h_inject` (scheduled and immediate injects), `_h_condition_check` (`IP-1064`) and `_h_env_anomaly_check` (`IP-1230`). `session/cells.py::CellController.view` is **not** changed: the per-cell filter is correct, the defect is the address. Load-bearing invariants: fog-of-war at the boundary (the point of the package); deterministic core (the recipients are derived inside the existing handler from world state, no clock, no RNG; the env tick's RNG draw order is untouched); content is data (the message strings are the only scenario text in Python, and they keep their wording); UI-agnostic engine (nothing in `engine/` changes).

## Interfaces

No route, request or response shape changes. The `messages` list of `GET /view/{cell}` and of `GET /controller_view` changes content per the table above; the world message dict shape `{"to": [...], "text": ..., "t": ...}` is unchanged. A notice that used to be one message with three recipients becomes up to two messages: one to `["white"]` (with cause) and one to `[owner]` (without).

### Design Decisions

1. **Address by ownership, in the handler, with one helper.** A single private helper in `session/manager.py` takes `(world, owner, white_text, owner_text)` and appends the White message and, when `owner` is `blue` or `red`, the owner message. Both new branches (and any later ownership-scoped notice) call it, so the policy lives in one place. The helper reads only the target's `owner` field (an `Asset.owner` or `Sensor.owner`, both `Literal["blue","red","neutral"]`). No fog logic moves into `CellController`.
2. **Two messages, not one with per-recipient text.** `CellView` filters on `cell in m["to"]`; keeping that filter unchanged and emitting a White-only message plus an owner-only message needs no schema change and no new filtering path (ADR-0004: one filter).
3. **Owner text omits the cause.** Disclosure to the owner is the minimum a player-visible notice needs (the fact and the target), consistent with `FR-4430`'s "never re-derived" cause and with the recovery loop's diagnosis step. **Adjacent exposure, noted not fixed:** `GET /view/{cell}` already returns the owner's own asset in full, including `bus_state.safe_mode.cause` (verified in the planning pass: Blue's own view shows `cause: "space_weather"` while safed). That is the owner's own spacecraft state read through the existing own-asset view, outside this package and outside `H-1`; it is raised for the owner in the completion note, not changed here.
4. **Restore variants follow the same rule.** `restore: true` ("cleared") notices are addressed exactly like the declared ones.
5. **Nothing else changes.** Effect application (safe mode via `enter_safe_mode`, comms status, `Sensor.health`) is untouched; replay of an existing log re-derives the messages under the new addressing, which closes the leak for old saves on load.
6. **Matrix over every message-emitting effect, not only the two fixed ones.** The review swept reads; this package sweeps writes: a parametrised test fires each effect type and asserts, per cell, exactly which message texts are present. A future effect type that appends a message without an addressing decision fails the "every effect type is in the matrix" completeness test.

## Files to Create

- `spacesim/tests/test_inject_notice_fog.py` — the matrix below (a new file avoids touching pinned rows in `test_origin_retag.py`).

## Files to Modify

- `spacesim/session/manager.py` — `_apply_inject_effects`: the `anomaly` and `sensor_outage` branches; one new private addressing helper next to `_skip_inject_effect`.
- `spacesim/tests/test_space_weather_index.py` — line 162 asserts that a message containing `"anomaly declared (space_weather)"` exists in `world.messages` (ground truth, which still holds because White's message keeps the cause); builder confirms it passes unchanged and tightens it to assert the White address.
- `docs/training/07-white-cell-facilitation.md` — lines 78-80 state "Announced to all three cells"; corrected to the table above by the builder's doc step if the tree's rule allows (otherwise routed to `08-training-manual-authoring` as a manual-impact finding; `15-manual-traceability.md` §15.1 rows for `FR-4430`/`FR-4440`).
- `CLAUDE.md` — one sentence in the `manager.py` code-map entry for the addressing helper (doc step).
- `docs/requirements/03-requirements-traceability-matrix.md` — Test column regenerated by `python3 -m pytest --origin-report=rtm` (generated, never hand edited).

## Implementation Tasks

1. Test-first: write the matrix; confirm the Red-cell cases fail on the parent (Red's view contains the Blue notice) and the White and pinned-unchanged cases pass.
2. Add the addressing helper; rewrite the two branches to call it; keep every string the White message carries identical to today's.
3. Run the matrix through all three entry points (immediate `POST /inject`, a future-dated White inject, a condition-triggered inject, the env tick) so a path that bypasses the helper is caught.
4. Replay and save/load checks (below).
5. Run the new tests, `test_inject_effects_v2.py`, `test_condition_triggered_injects.py`, `test_space_weather_index.py`, `test_pending_inject_queue.py`, `test_inject_library.py`, the training-basics and recovery tests that read messages, `test_determinism.py`, `test_import_guard.py`, then the full suite and `python3 -m pytest -m browser`; regenerate the RTM Test column in the same commit.
6. Documentation step; run `test_doc_integrity.py` and `test_test_origins.py`.

## Tests to Add

All through the FastAPI `TestClient` against real routes (`POST /inject`, `GET /view/{cell}`, `GET /controller_view`) on an authored two-side vignette whose Blue asset, Blue sensor, Red asset and Red sensor carry unique sentinel ids (so a leak is a plain substring check), plus engine-level cases where noted. Each carries `@pytest.mark.verifies(...)` with the leaf shown.

**Recipient matrix (`FR-6210`, `FR-4430`).** For each row, assert the exact set of message texts in the White, Blue and Red views (not "contains"): 
1. `anomaly`, `subsystem: bus`, Blue asset: White has the text with the cause; Blue has the fact without the cause; Red has none. Same for a Red asset (roles swapped).
2. `anomaly`, `subsystem: telemetry`, both owners: same as 1.
3. `anomaly` with `restore: true`, both owners: the "cleared" texts follow the same addressing.
4. `anomaly` on a `neutral`-owned asset: White only.
5. `sensor_outage` declared and cleared, a Blue sensor and a Red sensor: same pattern.
6. The cause string appears in no Blue or Red message and no field of Red's view for a Blue-owned target (sentinel cause).

**Pinned-unchanged rows (`FR-6210`, the decisions above).**
7. `gs_outage` declared and cleared: all three views carry it (as today).
8. `space_weather` severity and series messages: all three.
9. `spawn_debris` with and without `message`: all three with it, none without.
10. `conjunction_warning`: White and Blue only.
11. `message` effect with `to: ["blue"]`, `["red"]`, `["white","blue","red"]`: exactly those.
12. `scripted_manoeuvre`: White only; `forced_custody_loss` and `reveal_asset`: no message in any view.
13. A malformed effect: the "inject effect skipped" notice is White only.
14. Completeness: the set of effect types in rows 1-13 equals the set `validate_inject_effects` accepts, so a new type cannot ship unaddressed.

**Entry points (`FR-4420`, `FR-4440`).**
15. A future-dated White inject (`white-N` handle) carrying row 1: the addressing holds when it fires.
16. A condition-triggered inject (`asset_safed` or `proximity` condition) whose effect is an `anomaly`: Red's view never carries the notice.
17. The environmental-anomaly tick (a vignette declaring `environmental_anomalies` on a Blue asset with a high base rate and a fixed seed): after the tick fires, Red's view and every Red cell-scoped read in the sweep below are free of the Blue asset id and the cause; Blue and White carry the expected texts; the firing times equal those of the parent commit (the RNG stream is untouched).

**Sweep (`FR-6210`).**
18. After firing rows 1, 2 and 5 on Blue assets, serialise Red's `view`, `scene`, `alarms`, `activity`, `coaching`, `conjunctions`, `orders`, `next_contacts` and `ssn/*/requests` responses and assert no Blue sentinel id and no cause string appears; the same for Blue against Red-owned targets. (The intro brief, which names opposing assets by authored design, is excluded by using the sentinel vignette.)
19. `GET /controller_view` (White only) carries all of: truth messages with cause, Blue's owner notice, Red's empty list.

**Determinism and persistence (`ADR-0002`, `FR-7220`).**
20. Replay equals live: after rows 1, 5 and 17, `world.model_dump_json()` of a fresh replay equals the live world's.
21. Save/load: a session saved after row 1 and loaded again has the same per-cell messages (and a save written before this fix loads with the leak closed, because messages are re-derived by replay).
22. Rewind past the inject and re-advance: the same messages, no duplicates.

About 22 test functions (several parametrised).

## Documentation Updates

- `docs/training/07-white-cell-facilitation.md` lines 78-80 and the White manual (`12-white-cell-manual.md`) wherever it repeats "announced to all three cells": the corrected recipient table. Edited by the builder's doc step only if the tree's rule for that step allows `docs/training/` edits; otherwise a manual-impact finding for `08-training-manual-authoring` (the Blue and Red manuals gain a sentence that the owner is told the fact, not the cause).
- `CLAUDE.md` code map: the helper, one sentence.
- Not written by this package: `FR-4430` gains the missing "who is told" Postcondition (routed to `04-requirements-engineering`; the build does not wait on it, the tests tag `FR-6210` and `FR-4430`).
- `docs/implementation/00-master-build-plan.md`, `packages/INDEX.md`, the TWBS: written in this planning pass.

## Definition of Done

- With a Blue asset or sensor as the target, no Red cell-scoped read carries the target's id, the fact of the anomaly or outage, or the cause; with a Red target, the same for Blue; White carries the cause; the owner carries the fact.
- The three entry points (inject, condition, env tick) all obey the rule; every pinned-unchanged effect keeps its recipients.
- Effect application, the RNG stream, event-log shape and replay equality are unchanged.
- New tests green; RTM Test column regenerated in the same commit; full suite, `python3 -m pytest -m browser`, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py` green; no allow-list grew.

## Verification Checklist

- [ ] Re-derive `H-1` on the parent commit: an `anomaly` and a `sensor_outage` on Blue assets appear in `GET /view/red`; on this commit they do not, and White still sees the cause.
- [ ] Enumerate the message-appending lines in `session/manager.py` and `engine/ssn.py` from the tree (not from this package's list): each is covered by a matrix row or the completeness test.
- [ ] Owner text never contains the cause string; White text equals the pre-fix text.
- [ ] The env tick fires at the same times as on the parent (RNG untouched); replay equals live; save/load round trip holds.
- [ ] `CellController.view` and `engine/` are byte-unchanged.
- [ ] Permanent gates, documentation checks and the browser suite green.

## Dependencies

All `VERIFIED`: `IP-1062`, `IP-1063`, `IP-1064`, `IP-1230`. Edits `session/manager.py` only (no `server.py`, no `engine/`), so it may run in parallel with `IP-1085` and must precede `IP-1086` and `IP-1087` (shared file; see the Master Build Plan note). `IP-1160` (role-scoped commands) and `IP-1083` (rewind keeps future White injects) also edit `manager.py` in other regions; merge order between them is a textual, not a semantic, concern.

## Risks

- **A test or vignette that reads the broadcast.** The training-basics tutorial and the recovery tests may read `messages` for the anomaly text. The builder greps `spacesim/tests/`, `spacesim/content/vignettes/` and `static/` for `"anomaly declared"`/`"sensor outage declared"` and updates only expectations that assumed the opposing cell is told (a deliberate behaviour change, recorded in the commit).
- **Owner-facing wording.** The owner message is shorter than before; if the console parses it (it should not), the browser suite catches it.
- **Cause visible in the owner's own asset state.** Design Decision 3; not changed here, raised for the owner.
- **Two messages per notice.** The White message count in `/view/white` is unchanged (still one); the owner view gains one where it previously had one. Nothing counts messages per injected effect today (the builder confirms by grep).

## Rollback Considerations

Revert the commit. The two branches return to the three-recipient broadcast (the defect returns); no data format, save format or event-log record changes, so nothing written under this package needs migrating.
