# IP-1065 — White Cell Console and Session Small Fixes (BL-0196, BL-0266, BL-0267, BL-0145, BL-0141, BL-0185, BL-0261)

> **Package ID:** IP-1065
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-17 by `07-implementation-planning`, pipeline run #166.
> Every dependency is `VERIFIED`. **Authorization (MSTR-006 §3):** falls under the project owner's
> standing pre-authorization of 2026-10-11 for the packages this iteration reaches. Authoring the
> package is not itself the authorization.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) (inject Fire),
> [FS-102](../../features/FS-102-command-scheduling.md) v1.1 (executed vs queued visibility),
> [FS-118](../../features/FS-118-external-vignette-directories.md) v1.1 (labelled external group),
> [FS-120](../../features/FS-120-save-as-scenario.md) (save-as-scenario),
> [FS-119](../../features/FS-119-bulk-tle-omm-import.md) (bulk import); packages `IP-1063`,
> `IP-1180`, `IP-1190`, `IP-1200` (all `VERIFIED`).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0196`, `BL-0266`, `BL-0267`, `BL-0145`, `BL-0141`,
> `BL-0185`, `BL-0261`
> **Produces:** five small, independent console/session corrections plus two documentation
> follow-ups, each closing a verified finding.
> **Feature Reference:** the five FS above (one slice each).
> **Related Topics:** [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js),
> [`spacesim/ui_web/static/index.html`](../../../spacesim/ui_web/static/index.html),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`tools/render_manual.py`](../../../tools/render_manual.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design), part of the owner-prioritized `DEFERRED` backlog clearance
(2026-10-17). It bundles small items that share one seam (the White Cell console and the session
methods behind it); the TWBS records why they are one package.*

---

## Package ID

IP-1065 (FS-106 family → `IP-106x`; the next free slot after `IP-1063`).

## Title

White Cell console and session small fixes.

## Objective

Five independent defects, each verified at `e1e721c`:

| Item | As built | After |
|---|---|---|
| `BL-0196` — vignette inject **Fire** | `fireInject` (`app.js`) has no `catch`; a 400 from `POST /inject` is thrown unhandled and nothing appears on screen. | A rejected Fire shows the server's `inject rejected: …` text, as the builder's result line already does. |
| `BL-0266` — activity timeline | `InProcessSession.cell_activity` passes `Order.status` through; it never holds `executed`, so a past order draws as a dashed queued bar and `drawActivityBar`'s `executed` case is unreachable. | A `queued` order whose bar has ended is reported `executed`, matching `SessionManager.list_orders()`'s derived label (FS-102 v1.1 acceptance criterion). `active` is unchanged. |
| `BL-0267` — vignette picker | `loadVignettes` renders one flat list and ignores each entry's `origin`. `FR-5410` requires a separately labelled external group. | Built-in vignettes listed first, then one labelled group per external origin (for example an `<optgroup>` per origin). |
| `BL-0145` — save-as-scenario | Reachable only through `POST /save_vignette` with `as_scenario: true`; no console control. | A White-only Session-menu control asks for an id and title and calls that route with `as_scenario: true`, showing the saved path or the server's error. |
| `BL-0141` — bulk import | Two objects in one file resolving to the same asset id: the second overwrites the first and both report `ok: true`. | The second is refused with a per-object `ok: false` and a reason naming the earlier object; the first is kept. |

Documentation follow-ups riding this package: `BL-0185` (redraw `ref-05-tasking.png`/
`ref-06-compose.png` with the known-target dropdown + "or id" input and remove `10a` §10.6's
screenshot-staleness note) and `BL-0261` (`CLAUDE.md`'s LAN-trust paragraph names `FR-6220`'s full
no-cell set).

## Feature Reference

FS-106 (inject firing), FS-102 v1.1 Acceptance Criteria (executed visibly distinct from queued),
FS-118 v1.1 (`FR-5410` grouping), FS-120 (`FR-5510`), FS-119 (`FR-5220` per-object reports).

## Requirements Covered

| ID | Item |
|---|---|
| `FR-4410` | `BL-0196` — a rejected inject is reported to White Cell. |
| `FR-3310` (FS-102 v1.1's queue/timeline visibility) | `BL-0266`. |
| `FR-5410` | `BL-0267` — separately labelled external group. |
| `FR-5510` | `BL-0145` — White Cell can save from the console. |
| `FR-5220` | `BL-0141` — per-object outcome is truthful. |
| `NFR-3400` | `BL-0185` — manual screenshots match the shipped UI. |

## Architecture Components

- **C4 Operator Console** (`app.js`, `index.html`): `BL-0196`, `BL-0267`, `BL-0145`.
- **C2 Session Layer** (`inprocess.py::cell_activity`, `manager.py::bulk_import`): `BL-0266`,
  `BL-0141`.
- Tooling (`tools/render_manual.py`, `docs/manual/`): `BL-0185`. Engine untouched.

## Interfaces

- **INT-0006** (console → SessionAPI): no new route. `/activity/{cell}` may now return `executed`
  (already in its documented status vocabulary); `/force/bulk_import` reports may now carry a
  duplicate-id failure; `/save_vignette` gains a console caller.

### Design Decisions

1. **`executed` is derived exactly as `list_orders` derives it**: a stored `queued` order whose
   window start has passed and whose bar no longer straddles now. Reuse one rule; do not invent a
   second.
2. **Duplicate detection is per file**, keyed on the resolved asset id within one `bulk_import`
   call. Overwriting an asset that existed before the call is out of scope (unchanged).
3. **Picker grouping uses the existing `origin` field**; no API change. Order: built-in first,
   then external origins in the order the server lists them.
4. **Save-as-scenario control** lives in the White-only Session menu; it is hidden for other seats
   and refused server-side for Observer as every mutating route already is.

## Files to Create

- None beyond tests (below).

## Files to Modify

Checked at `e1e721c`: `spacesim/ui_web/static/app.js` (`fireInject`, `loadVignettes`, a new
save-as-scenario handler), `spacesim/ui_web/static/index.html` (Session menu control),
`spacesim/session/inprocess.py` (`cell_activity`), `spacesim/session/manager.py` (`bulk_import`),
`tools/render_manual.py` (the `ref-05`/`ref-06` drawing), `docs/manual/ref-05-tasking.png`,
`docs/manual/ref-06-compose.png` (regenerated), `CLAUDE.md`.

## Implementation Tasks

1. Tests first (below); confirm the session-level ones fail.
2. `cell_activity`: derive `executed` (Design Decision 1).
3. `bulk_import`: per-file duplicate refusal (Design Decision 2).
4. `fireInject`: catch the error and show it (reuse the builder's result line or a sibling line).
5. `loadVignettes`: group by `origin` (Design Decision 3).
6. Save-as-scenario control (Design Decision 4).
7. Regenerate `ref-05`/`ref-06` with `tools/render_manual.py` (needs Pillow); remove the
   staleness note in `docs/training/10a-ui-reference-orders.md` §10.6 — a `docs/training/` edit,
   so record it for `08-training-manual-authoring` if this package's run may not write there
   (manual impact below).
8. `CLAUDE.md` LAN-trust paragraph: point at `FR-6220`'s named set (`BL-0261`).

## Tests to Add

- `spacesim/tests/test_cell_activity.py`: an order whose window has passed reports `executed`; one
  straddling now reports `active`; one in the future reports `queued`.
- `spacesim/tests/test_bulk_import_session.py`: a TLE file with two objects resolving to one asset
  id → first `ok: true`, second `ok: false` with a duplicate reason; the asset keeps the first
  object's orbit.
- `spacesim/tests/test_web.py` (or the nearest console-asset test): the served `app.js` contains
  the `fireInject` error path and the origin grouping, and `index.html` contains the White-only
  save-as-scenario control — the repository's established static-asset assertion pattern for UI
  changes the headless suite cannot drive.
- Permanent gates: `test_determinism.py`, `test_import_guard.py`.

## Documentation Updates

- Manual impact (§15.1 rows "Activity timeline", "Injects", "Vignette load", "External vignette
  folders"): `10b` §10.15 (remove the as-built `queued` caveat), `10` §10.3 row 2 and `WCM-5`
  (Fire now reports), `01` §2.2 (the list is now grouped), `10` §10.1.1 / `WCM-2` (new
  save-as-scenario control), `10a` §10.6 note. These are `08-training-manual-authoring`'s to write
  after this package (file a manual-impact backlog entry).
- `CLAUDE.md` (LAN trust paragraph; code map if a new handler is notable). RTM Test cells for the
  covered leaves.

## Definition of Done

- [ ] All new tests pass; the session-level ones failed first.
- [ ] Full suite and both permanent gates green.
- [ ] Screenshots regenerated, or the regeneration recorded as blocked with the reason.
- [ ] `CLAUDE.md`, RTM, MBP/INDEX/ROADMAP updated; manual impact filed.

## Verification Checklist

- [ ] Each of the five behaviours reproduced independently (a probe per row of the Objective).
- [ ] `executed` derivation matches `list_orders` on the same orders.
- [ ] Full suite and both gates run by name.

## Dependencies

All named packages `VERIFIED`. Independent of `IP-1021`, `IP-1064`, `IP-1223`, `IP-1131`.

## Risks

- Seven small items in one run: keep each a separate, revertible hunk.
- Static-asset tests check presence, not browser behaviour (the GUI is unverified headless —
  `CLAUDE.md`).

## Rollback Considerations

Each item reverts independently. No data migration; `executed` was already a documented status.
