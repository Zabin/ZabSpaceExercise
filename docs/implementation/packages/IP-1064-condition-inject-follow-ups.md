# IP-1064 — Condition-Triggered Inject Follow-Ups: Evaluated Value, Anchored Tick Grid, One Scan per Tick (BL-0131, BL-0132, BL-0133)

> **Package ID:** IP-1064
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-17 ([VR-1064](../verification/VR-1064-condition-inject-follow-ups.md), fresh session; READY before that) — authored 2026-10-17 by `07-implementation-planning`.
> **Earlier status record (superseded by the line above; retained as history, unedited):** 🟢 READY — authored 2026-10-17 by `07-implementation-planning`, pipeline run #166.
> Every dependency is `VERIFIED`. **Authorization (MSTR-006 §3):** falls under the project owner's
> standing pre-authorization of 2026-10-11 for the packages this iteration reaches.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1 (`FR-4420`);
> [IP-1062](IP-1062-condition-triggered-injects-and-new-effects.md) (`VERIFIED`, `VR-1062` v2.0 —
> source of findings L2/L3/L4).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0131`, `BL-0132`, `BL-0133`
> **Produces:** condition-inject log records that carry the measured value, tick grids that do not
> shift after a rewind, and a fired-lookup that scans the log once per tick.
> **Feature Reference:** FS-106 v2.1 (`FEAT-4400`)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/engine/busmodel.py`](../../../spacesim/engine/busmodel.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design), part of the owner-prioritized `DEFERRED` backlog clearance
(2026-10-17). Closes `VR-1062`'s three remaining Low findings.*

---

## Package ID

IP-1064 (FS-106 v2.1 → `IP-106x`).

## Title

Condition-triggered inject follow-ups.

## Objective

Verified at `e1e721c` in `session/manager.py`:

1. **`BL-0131` — evaluated value.** `_h_condition_check` records `{"inject_id", "value": True}`
   for a firing; `_evaluate_metric` returns only a boolean. `FR-4420`'s Outputs ask for "the
   condition's evaluated value". After: the record carries the measured quantity that decided the
   firing — the range in km for `proximity`/`evade`, the track confidence for
   `custody`/`deny_custody` — and, for a metric with no measured quantity, the boolean as now.
2. **`BL-0132` — tick grid after a rewind.** `_arm_schedule(from_t)` queues `condition_check` at
   `from_t + k·step`, and `BusSystem.schedule_ticks(start=from_t)` does the same for `bus_tick`.
   After a rewind to a time off the grid, both grids shift, so "rewind, then re-advance unchanged"
   does not reproduce the original timeline (determinism of replay still holds). After: both grids
   stay anchored to the session's start time — the first tick after `from_t` is the next grid
   point `start + k·step > from_t`.
3. **`BL-0133` — repeated scans.** `_condition_inject_already_fired` scans the whole event log once
   per condition inject per tick. After: one scan per tick builds the set of already-fired inject
   ids, then each inject checks membership. Same results.

## Feature Reference

FS-106 v2.1 — `FR-4420` behaviour (fire at the first scheduled tick the condition holds; the log
records the firing tick and the evaluated value). `FR-4420`'s Precondition (amended 2026-10-17)
keeps fire-once.

## Requirements Covered

| ID | How |
|---|---|
| `FR-4420` | Outputs: evaluated value recorded (1); deterministic tick schedule unaffected by rewind position (2). |
| `NFR-1100` | One log scan per tick instead of one per inject per tick (3). |

## Architecture Components

- **C2 Session Layer** (`session/manager.py`: `_arm_schedule`, `_h_condition_check`,
  `_condition_inject_already_fired`), **C5 Content** (`content/vignette.py`: a measuring companion
  to `_evaluate_metric`), **C1 Engine** (`engine/busmodel.py::schedule_ticks` gains an anchor
  argument, or the caller computes the first grid point). No new engine import; the guard is
  unaffected.

## Interfaces

- **INT-0016** (inject application): unchanged in shape; the `condition_check` log payload's
  `fired[].value` becomes a number for measured metrics.
- **INT-0014** (replay reads): unchanged.

### Design Decisions

1. **Measure without changing the decision.** Add a companion (for example
   `_measure_metric(world, ctx, m) -> value`) that returns the quantity `_evaluate_metric` compares;
   `_evaluate_metric`'s boolean result and every objective that uses it are unchanged.
2. **Anchor = the session's start time** (`SessionManager.start()`'s clock value, kept on the
   manager; a rebuilt/resumed manager must recover the same anchor — use the vignette start epoch
   if that is what `start()` arms from). Both `condition_check` and `bus_tick` use it.
3. **Fired set per tick**, derived from the event log entries strictly before the current tick
   (the same time filter as now), so live run and replay agree.

## Files to Create

- None beyond tests.

## Files to Modify

Checked at `e1e721c`: `spacesim/session/manager.py` (`_arm_schedule` lines ~240–268,
`_condition_inject_already_fired` ~1192, `_h_condition_check` ~1202),
`spacesim/content/vignette.py` (`_evaluate_metric` ~550, new companion), `spacesim/engine/busmodel.py`
(`schedule_ticks` ~31).

## Implementation Tasks

1. Tests first (below); 1 and 2 fail today.
2. Measuring companion + record the value.
3. Anchor both grids.
4. One-scan fired set.
5. Full suite + gates. Check no shipped vignette's playbook outcome changes
   (`test_vignette_tutorials.py`).

## Tests to Add

In `spacesim/tests/test_condition_triggered_injects.py`:
1. A `proximity` condition firing records a numeric range in km ≤ the threshold.
2. Advance past several ticks, rewind to a time off the tick grid, re-advance: the `bus_tick` and
   `condition_check` event times after the rewind equal those of an un-rewound run.
3. The fired-once behaviour and fire tick are unchanged (existing tests stay green); add one test
   with two condition injects checking both fire once at the same ticks as before.
Permanent gates: `test_determinism.py`, `test_import_guard.py`.

## Documentation Updates

- RTM `FR-4420` Test cell. `CLAUDE.md` only if the code-map line for condition injects needs it.
- Manual: `07` §8 or `WCM-5` mention the condition-inject log only if they describe its record
  (check §15.1 "Injects" row; likely no edit).

## Definition of Done

- [ ] Tests 1–2 failed first and pass; existing condition/bus tests green.
- [ ] Full suite and both permanent gates green; playbook suite green.
- [ ] RTM and ledgers updated.

## Verification Checklist

- [ ] Reproduce the rewind-grid case independently on a shipped vignette with a condition inject
      or a fixture.
- [ ] Confirm `_evaluate_metric`'s results are unchanged for every metric kind.
- [ ] Run the full suite and both gates by name.

## Dependencies

`IP-1062` (`VERIFIED`). Independent of the other packages in this tranche. If `IP-1021` lands first,
nothing here conflicts (different functions).

## Risks

- **Bus-tick anchoring changes bus evolution after a rewind** (ticks at different instants than
  today). Intended — it restores the original timeline — but any test that asserted post-rewind
  bus values computed on the shifted grid would change; inspect, don't blindly update.
- Resume from a save must recover the same anchor (Design Decision 2).

## Rollback Considerations

Revert the three files. Logs written with numeric `value`s stay replayable (the field is
informational).
