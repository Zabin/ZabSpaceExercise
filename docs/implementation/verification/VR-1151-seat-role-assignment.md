# VR-1151 — Verification Report: Seat-to-Role Assignment

> **Document ID:** VR-1151
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1151](../packages/IP-1151-seat-role-assignment.md), [FS-115](../../features/FS-115-session-setup.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition for IP-1151; re-confirmation of `BL-0014`
> **Feature Mapping:** FS-115 (FR-4210 portion)
> **Related Topics:** [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py), [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py), [`spacesim/tests/test_session_setup.py`](../../../spacesim/tests/test_session_setup.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1151 — Session Setup: Seat-to-Role Assignment (FS-115, FR-4210 slice)
- **Version verified:** 1.1
- **Tree state verified:** commit `580153ed7ef7457d0d67c23fbd9ecaee6290119c` (branch `claude/pipeline-skill-ijwd1f`)
- **Independence:** implemented in run #8 of this same overall conversation; this is run #15 (the
  final verification of the "iterate through all `09-package-verification`" sweep). Several runs
  and at least one context-compaction boundary separate implementation from this verification.
  Every claim below was independently re-derived from the live source and a fresh test run — none
  taken from the Implementation Summary or the package's own prose.

## Result

**VERIFIED** — every Definition of Done and Verification Checklist item is confirmed against the
current tree; full suite green; both permanent gates green; requirements traceability audited and
corrected. **`BL-0014`'s negative finding (no role-based command-filtering consumer exists) was
independently re-derived, not merely re-cited, and is still true**: `role_assignments` is written
by `assign_role()` and read only by `staffing_report()` — no file in `engine/orders.py`,
`engine/buscommands.py`, `session/manager.py`'s command paths, or anywhere else in the shipped
code consults it for command authorization. One new Low finding, in the same family as `BL-0023`
(IP-1130's verification, run #14): `assign_role`'s White-Cell-only gate is tested against
`cell="blue"`, not `cell="observer"` specifically.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization obtained (MSTR-006 §3). | `docs/pipeline/pipeline-journal.md` run #2. | ✅ Pass |
| `Vignette.roles_needed` exists and defaults to an empty/absent list; no breakage of the 19 existing vignette YAML files. | `content/vignette.py:44-50` (`RoleRequirement`), `:89` (`roles_needed: list[RoleRequirement] = Field(default_factory=list)`). `test_roles_needed_defaults_to_empty_on_existing_vignettes` loads `leo-isr-denial` and asserts `vig.roles_needed == []`. | ✅ Pass |
| Seat-to-role assignment against `roles_needed` produces Role Assignment records in a plausible, self-consistent shape. | `session/manager.py:112-113` (`assign_role`), `:46` (`self.role_assignments: dict[str, dict] = {}`), `:116-118` (`_role_covers`, "both" covers either bus or payload). Six unit tests in `test_session_setup.py` (lines 51-99) cover empty/mandatory/optional/exact-match/both-covers/mismatch cases, all passing. | ✅ Pass |
| ⚠️ "Consumable by FS-105's existing command-filtering mechanism" — **not satisfied, and not claimed to be** (package's own item 3 already marks this `[~]`). | See "Re-confirmation of `BL-0014`" below — independently re-derived as still false. Package text (Status, Implementation Tasks item 6, Dependencies, Risks) all still state this honestly; no overclaim found. | ✅ Pass (honesty of the caveat, which is what this item actually requires) |
| An unmet mandatory `roles_needed` entry is reported as unsatisfied and hard-blocks exercise start (not merely advisory). | `session/inprocess.py:131-141` (`InProcessSession.start()`): calls `mgr.staffing_report()`; if non-empty, returns `Ack(ok=False, reason=...)` **before** `mgr.start()` is ever called. `test_start_refused_with_unmet_mandatory_role_via_api` confirms `ack.ok is False` and `mgr.started is False`. | ✅ Pass |
| A vignette with no `roles_needed` declared is never blocked from starting. | `test_existing_vignette_starts_without_any_role_assignment` loads `leo-isr-denial` (declares no `roles_needed`) via the real `InProcessSession.load_vignette`/`start` path and asserts `ack.ok is True`. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `spacesim/tests/test_session_setup.py` exists and is green. | 12 tests, all passing (confirmed by direct run, not by re-citing the Implementation Summary's count). | ✅ Pass |
| `test_determinism.py` remains green. | 14 passed (with `test_import_guard.py`), run by name. This package's staffing gate lives entirely in `session/`/`ui_web/`, touching no `engine/` file. | ✅ Pass |
| Re-run every existing vignette-loading test (`test_content.py`, `test_vignette_tutorials.py`) — no regression from the additive `roles_needed` field. | `python3 -m pytest spacesim/tests/test_content.py spacesim/tests/test_vignette_tutorials.py spacesim/tests/test_session_setup.py` → 35 passed, 0 failed. | ✅ Pass |
| Manual review: confirm the produced Role Assignment record shape is actually consumable by the existing FS-105/IP-1050 command-filtering mechanism. | **Independently re-derived, result unchanged: no such mechanism exists.** `grep -rni "role" spacesim/engine/buscommands.py docs/features/FS-105-spacecraft-operations.md docs/implementation/packages/IP-1050*.md docs/implementation/packages/IP-1051*.md` → zero matches. `grep -n "role_assignment\|role_covers" spacesim/engine/orders.py spacesim/session/inprocess.py spacesim/session/manager.py` shows `role_assignments`/`_role_covers` referenced only inside `manager.py`'s own `assign_role`/`staffing_report` — never read by `orders.py`'s command validate/issue path or by `buscommands.py`'s `can_issue`/`apply_command`. Every existing command authorization check remains `cell`-based (confirmed by reading `orders.py`'s validation path — no role parameter anywhere in it). | ✅ Confirmed (checklist item correctly left unsatisfied — this is the honest, expected outcome, not a defect) |

## Re-confirmation of `BL-0014` (FS-105 non-consumption finding)

**Claim to re-check:** the package's own text asserts that no role-based (bus/payload/both)
command-authorization concept exists anywhere in the codebase, and that the Role Assignment
records this package produces have no consumer.

**Independently re-derived: still true, unchanged since run #8.** Nothing landed between run #8
and this run (`IP-1130`'s Observer seat, `IP-1120`'s classification banner, `IP-2010`'s assessment
scoring, `IP-3010`'s research batch runner) introduces role-based command filtering — none of
those packages' own scopes touch command authorization, and a direct search confirms it:

- `spacesim/engine/orders.py`'s validation path checks only `cell` ownership (Blue/Red/White),
  never a seat's assigned role.
- `spacesim/engine/buscommands.py`'s `can_issue` gates only on payload type + bus availability, no
  role concept.
- `session/manager.py`'s `role_assignments` dict is populated by `assign_role()` and consumed
  *only* by `staffing_report()` — a pre-start staffing check, not a runtime command filter.

`FS-115`'s own Scope still explicitly excludes runtime enforcement from this Feature (confirmed by
reading `FS-115-session-setup.md`'s Data Model Changes section: "this Feature *produces* Role
Assignment records that FS-105/`FEAT-3500` later enforces at runtime" — a forward-looking
statement about a different Feature, not a claim this package itself must satisfy). `IP-1151`'s
own scope is therefore unaffected by this finding, exactly as the package states. `BL-0014` stands
as an accurate, still-open finding — no change to its `DEFERRED` disposition is warranted.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-4210 (seat-to-role assignment at setup) | `content/vignette.py` (`RoleRequirement`/`roles_needed`), `session/manager.py` (`assign_role`/`_role_covers`/`staffing_report`), `session/inprocess.py` (`start()` hard gate, `assign_role`/`staffing_report` wrappers), `ui_web/server.py` (`/roles/assign`+`/roles/staffing`), `ui_web/static/app.js`+`index.html` (seat-assignment UI step) | `tests/test_session_setup.py` (12 tests, covers schema default, registry/gate logic, HTTP endpoints, and the White-Cell-only assignment gate) | `Impl. Package` cell read "`IP-1151` *(implemented 2026-07-03, COMPLETE, pending 09-package-verification)*" — **corrected this pass** to cite `VR-1151`/`VERIFIED`. `Research`/`Future Feature` columns remain `UNASSIGNED`, consistent with every sibling row in this tranche (`FR-4110`, `FR-4510`, `FR-6510`) and out of this package's scope to populate. | ✅ Pass |

## Test run

Commands run, in order, on commit `580153ed7ef7457d0d67c23fbd9ecaee6290119c`:

```
python3 -m pytest -q spacesim/tests/test_content.py spacesim/tests/test_vignette_tutorials.py spacesim/tests/test_session_setup.py -v
  → 35 passed, 1 warning (StarletteDeprecationWarning, unrelated) in 3.31s

python3 -m pytest -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
  → 14 passed

python3 -m pytest -q   (full suite)
  → 566 passed, 3 skipped, 0 failed (counted programmatically — this pytest configuration
    suppresses the usual summary line)
```

Both permanent gates green. Full suite unchanged from the count recorded at `IP-1130`'s
verification (run #14) — no regression introduced between that run and this one.

## Scope audit

Diff re-derived from the implementing commit (`9e3861a`): `spacesim/content/vignette.py`,
`spacesim/session/inprocess.py`, `spacesim/session/manager.py`, `spacesim/ui_web/server.py`,
`spacesim/ui_web/static/app.js`, `spacesim/ui_web/static/index.html`,
`spacesim/tests/test_session_setup.py` (new). Every source file the package's `Files to Modify`
names was touched (`content/vignette.py`, `session/manager.py`, `ui_web/server.py`,
`ui_web/static/app.js`); `session/inprocess.py` and `index.html` were not literally named in that
field but are directly implied by Implementation Tasks items 3-4 (the start-time gate lives in
`InProcessSession.start()`, not `SessionManager.start()`; the UI step needs markup for the JS to
bind to) and are explicitly covered by the package's own Rollback Considerations section — the same
"implied companion file" pattern already accepted for `IP-1120`/`IP-2010`/`IP-1130`'s own
verification passes. No file outside this set was touched by the implementing commit.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | `assign_role`'s White-Cell-only gate (`inprocess.py:145-146`, `if cell != "white": return Ack(ok=False, ...)`) is tested via `test_only_white_cell_can_assign_roles`, which exercises `cell="blue"` — not `cell="observer"` specifically. Same family as `BL-0023` (IP-1130's verification, run #14): functional risk is effectively nil (the check is an unconditional equality test against the literal string `"white"`, which trivially covers `"observer"` too), but explicit coverage is missing. | Low | Optional: fold into the same future maintenance pass `BL-0023` already names for `test_session_setup.py`/`test_observer.py`; not blocking, no dedicated run justified. |
| 2 | (Re-confirmed, not new) `BL-0014` — no role-based command-filtering consumer exists for the Role Assignment records this package produces. Independently re-derived this pass (see section above), unchanged. Already `DEFERRED`, routed to `06-feature-specification`. | Medium (unchanged from original filing) | Already tracked; no new action from this pass. |

No Critical/High findings. No test failure, no scope excursion, no unchecked DoD item requiring a
fail. Finding 1 is filed as a new Low entry (`BL-0024`); Finding 2 is a re-confirmation of the
standing `BL-0014`, not a new item.

## Related

[IP-1151](../packages/IP-1151-seat-role-assignment.md) · [FS-115](../../features/FS-115-session-setup.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
