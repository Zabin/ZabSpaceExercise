# IP-1223 — Beam-Mode Choice Follows the Sensor's Modality (FS-122 v1.2, FR-1610, BL-0265)

> **Package ID:** IP-1223
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-17 by `07-implementation-planning`, pipeline run #166.
> Every dependency is `VERIFIED`. **Authorization (MSTR-006 §3):** falls under the project owner's
> standing pre-authorization of 2026-10-11 for the packages this iteration reaches.
> **Dependencies:** [FS-122](../../features/FS-122-sensor-modality-models.md) v1.2 (the spec delta);
> [IP-1222](IP-1222-sensor-modality-wiring-remediation.md) and
> [IP-1041](IP-1041-observe-order-reason-and-param-remediation.md) (both `VERIFIED`).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0265` (from `BL-0224`; REV-TRN-007 F1/F2)
> **Produces:** an observe order whose beam mode always comes from the executing sensor's own
> modality, at the console and at the server.
> **Feature Reference:** FS-122 v1.2 (`FEAT-1600`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

---

## Package ID

IP-1223 (FS-122 → `IP-122x`, after `IP-1222`).

## Title

Beam-mode choice follows the executing sensor's modality.

## Objective

Verified at `e1e721c`:

- **Server.** In `OrderSystem._exec_payload`'s observe branch, a ground radar whose requested mode
  is a radar mode uses the `ground_radar` table; any other requested name is resolved against the
  payload type chosen by the sensor-kind heuristic (`isr_eo` if `needs_lighting`, else
  `isr_sar`) — `IP-1222` Design Decision 2. So a radar asked for `spotlight` is scored on the
  imaging-SAR table (gain 1.8 > its own `dish` 1.6).
- **Console.** `#task-beam-mode` (`index.html`) is a fixed EO/SAR list; a radar's `fence`/`dish`
  are reachable only through the raw JSON params box.

After (FS-122 v1.2 System Behaviour and Acceptance Criterion):
- an observe order naming a mode the executing sensor's modality does not offer is refused
  `invalid_param` at preview and issue, and nothing is scheduled;
- the console's choices for the selected sensor are `auto` plus that sensor's modality modes (a
  radar: `fence`, `dish`).

## Feature Reference

FS-122 v1.2 — "Beam-mode choice follows the executing sensor's modality"; Acceptance Criterion
(v1.2); Open Question (v1.2) on auto-selected sensors, decided below.

## Requirements Covered

| ID | How |
|---|---|
| `FR-1610` | Radar beam modes selectable; a foreign mode never silently substitutes. |
| `NFR-1600` | An illegal parameter is blocked with a reason, not mis-scored. |

## Architecture Components

- **C1 Engine** (`engine/orders.py`: observe validation and the observe branch of
  `_exec_payload`; `engine/isr.py`: mode tables, read only) — the server rule.
- **C4 Console** (`app.js`, `index.html`) — the mode list.

## Interfaces

- **INT-0006/INT-0008**: `POST /order` and `/order/validate` may now return `invalid_param` for a
  foreign mode. No new route.

### Design Decisions

1. **One helper names a sensor's modality table**, used by validation and by `_exec_payload`, so
   the two cannot disagree: a ground radar → `ground_radar`; an asset with `payload_state` → its
   type; otherwise the existing lighting heuristic.
2. **Explicit sensor:** the requested mode must be a key of that table, or the order is refused
   `invalid_param` in `_validate` (so `dry_run` and `issue` refuse alike), before any window search
   or booking. `auto`/absent mode → the sensor's own mode, as now.
3. **Auto-selected sensor (FS-122 v1.2 Open Question):** candidate selection considers only the
   cell's sensors whose table offers the requested mode; if none does, `invalid_param`. Recorded
   here as this package's decision.
4. **Console list** is built from the selected sensor's kind (the client already has each asset's
   `kind`); for `auto`, show the union of the cell's own sensors' modes. The client mirrors the
   server table names; the server stays authoritative.

## Files to Create

- None beyond tests.

## Files to Modify

Checked at `e1e721c`: `spacesim/engine/orders.py` (`_observe_params_ok`/`_validate` observe path,
`_candidate_sensors`/`_plan_collection` for Design Decision 3, the observe branch of
`_exec_payload` ~836–859), `spacesim/ui_web/static/app.js` (`#task-beam-mode` population near the
`task-sensor` refresh ~1319, `updateIsrInfo`), `spacesim/ui_web/static/index.html`
(`#task-beam-mode` options become dynamic).

## Implementation Tasks

1. Tests first; the radar-`spotlight` case fails today (it queues and scores 1.8).
2. Helper (Design Decision 1); validation (2); auto filtering (3); console list (4).
3. Full suite + gates; re-run `test_sensor_modalities*.py`/`test_vignette_tutorials.py`.

## Tests to Add

In the existing sensor-modality test module (or `spacesim/tests/test_beam_mode_modality.py`):
1. Explicit radar + `spotlight` → `invalid_param` from `dry_run` and `issue`; scheduler unchanged.
2. Explicit radar + `fence`/`dish`/absent → queued; gains 0.5 / 1.6 / own mode (unchanged).
3. Explicit EO sensor + `fence` → `invalid_param`.
4. `auto` + `dish` picks a radar when one is a candidate; `auto` + a mode no own sensor offers →
   `invalid_param`.
5. Static-asset check: `app.js` builds the mode list from the sensor kind.
Permanent gates: `test_determinism.py`, `test_import_guard.py`.

## Documentation Updates

- Manual impact (§15.1 "ISR/observe assistant" and "Sensor modality authoring fields" rows):
  `10a` §10.5 row 8 (dynamic list), `06` beam-mode row, `BLU-4`/`RED-4`. For
  `08-training-manual-authoring` after this package.
- RTM `FR-1610` Test cell; FS-122 `Referenced By`.

## Definition of Done

- [ ] Tests 1, 3, 4 failed first; all pass. Full suite + both gates green.
- [ ] Ledgers, RTM updated; manual impact filed.

## Verification Checklist

- [ ] Probe a shipped vignette with a ground radar (`sda-custody-hunt`): `spotlight` refused,
      `dish` queued at 1.6.
- [ ] Read the helper and confirm validation and execution call it.
- [ ] Full suite and both gates by name.

## Dependencies

`IP-1222`, `IP-1041` (`VERIFIED`). Independent of the rest of this tranche.

## Risks

- A vignette or tutorial that names a SAR mode on a radar would now be refused: grep shipped
  vignettes and playbooks for `beam_mode` before changing behaviour.
- Auto filtering changes which sensor auto picks only when a mode is requested.

## Rollback Considerations

Revert the three files. No data migration.
