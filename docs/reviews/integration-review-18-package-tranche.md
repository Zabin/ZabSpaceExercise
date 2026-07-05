[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Master Build Plan](../implementation/00-master-build-plan.md)

# Integration Review — 18-Package Implementation Tranche

> **Document ID:** REV-INT-001
> **Skill:** `10-integration-review`
> **Scope:** every package on `docs/implementation/00-master-build-plan.md` (18 packages,
> `IP-1010`…`IP-3010`) — the full set covering FS-101–107, FS-109–111, FS-112–115, FS-201, FS-301
> **Commit reviewed:** `0e2aa136a4cea2e3288b4e95691ce53b06102358` (`origin/main` tip at review time)
> **Precondition confirmed:** all 18 packages carry `✅ VERIFIED` on the Master Build Plan (7 with
> a formal `VR-xxxx` report: `IP-1120`/`IP-1130`/`IP-1140`/`IP-1150`/`IP-1151`/`IP-2010`/`IP-3010`;
> the original 11 as-built packages predate the VR convention — see Finding 4 below)
> **Upstream:** `09-package-verification` (7 `VR-xxxx` reports, runs #3, #9, #11–#15)
> **Downstream:** `11-release-readiness`

## Package list in scope

IP-1010, IP-1020, IP-1030, IP-1040, IP-1050, IP-1051, IP-1060, IP-1070, IP-1090, IP-1100, IP-1110,
IP-1120, IP-1130, IP-1140, IP-1150, IP-1151, IP-2010, IP-3010 — the complete Master Build Plan.

## Evidence gathered per dimension

### 1. Interface consistency

Ran the full test suite against the reviewed commit: **566 passed, 3 skipped**, matching every
prior `VR-xxxx` report's count exactly (no regression since the last package, `IP-1151`, was
verified). The suite exercises every package's endpoints/interfaces end-to-end via
`fastapi.testclient`, including the parametrized 21-route `_reject_observer` sweep
(`test_observer.py`) that spans `IP-1130`'s own guard plus every mutating route added by later
packages (`IP-1151`'s `/roles/assign`, etc.) — the load-bearing cross-package interface (fog-of-war
at the `SessionAPI` boundary) is exercised, not just each package's own slice of it.

Independently re-derived the live mutating-route table from `spacesim/ui_web/server.py` (25 `POST`
routes total) against `test_observer.py`'s `_MUTATING_ROUTES` table (21 entries) to spot-check
`BL-0011`'s predicted drift risk (a route added after `IP-1130` shipped silently losing guard
coverage):

- 21 routes: covered by the explicit `cell="observer"` → `403` denylist test.
- 2 routes (`POST /observer/view`, `POST /roles/assign`): **not** in the denylist test, but
  confirmed by direct code read (`session/inprocess.py:145-146`, `:297-298`) to reject
  `cell="observer"` via a stricter White-Cell-only `if cell != "white"` allowlist check —
  functionally rejected (returns `Ack(ok=False)` rather than an HTTP `403`, a different mechanism
  but the same outcome: no mutation). This is exactly `BL-0023`/`BL-0024`'s already-tracked
  test-coverage gap, re-confirmed still accurate and still non-functional in nature.
- 2 routes (`POST /api/sessions`, `POST /api/sessions/load_save`): correctly out of scope — both
  create/load a session before any cell is bound to it, so "reject Observer" has no meaning yet.

**No new drift found** — `BL-0011`'s predicted risk has still not materialized, consistent with
`VR-1130`'s (run #14) independent finding.

### 2. Invariant sweep

Ran both permanent gates directly against the reviewed commit:

```
spacesim/tests/test_determinism.py .....   (6 passed)
spacesim/tests/test_import_guard.py ........   (8 passed)
```

Both green. `engine/` remains free of wall-clock reads and non-`rng.py` randomness (import-guard
AST scan); the Phase-1 determinism property test still holds byte-identical replay. Fog-of-war
enforcement at the `SessionAPI`/`CellController` boundary was exercised as part of dimension 1
above (the Observer-seat sweep is itself an invariant check — no package after `IP-1130` shipped a
route that leaks past the boundary). No cross-package invariant violation found.

### 3. Behavioral coherence

No duplicated or divergent implementation of the same behavior was found across the 18 packages.
`BL-0014` (the `IP-1151` Role Assignment record having no runtime consumer anywhere in the shipped
code — a workflow that "dead-ends at a seam" in this dimension's terms) remains the one standing
instance of this class; it has already been independently re-derived twice (`08` run #8, `VR-1151`
run #15) and is tracked `DEFERRED` pending a future `06-feature-specification` decision on whether
`FS-105` should specify a consumer. Not re-derived a third time here — re-verification of an
already-adjudicated single-package finding is `09`'s job, not this dimension's.

### 4. Traceability coherence

Cross-checked the Master Build Plan, `packages/INDEX.md`, the RTM, `feature-index.md`, and each
package's own header against each other.

- **`docs/implementation/verification/` contains exactly 7 `VR-xxxx` files** for the 7
  tranche-2/forward-design packages (`IP-1120`, `IP-1130`, `IP-1140`, `IP-1150`, `IP-1151`,
  `IP-2010`, `IP-3010`). **None exist for the original 11 as-built packages** (`IP-1010`…`IP-1110`)
  — `BL-0004` re-confirmed still true, unchanged, on direct evidence rather than citation.
- **Finding 2 (new):** `IP-1150`'s own package-doc header (`docs/implementation/packages/
  IP-1150-vignette-selection.md:5`) still reads `Status: 🔵 COMPLETE`, and its `Referenced By`
  field (line 10) still says `IP-1120`/`IP-1151` are "both `BLOCKED` on this package reaching
  `VERIFIED`" — both facts are stale. `VR-1150` (run #3, 2026-07-03) flipped `IP-1150` to
  `VERIFIED` over a dozen runs ago, and `IP-1120`/`IP-1151` have themselves been `VERIFIED` since
  runs #13/#15. The Master Build Plan (line 118) and `packages/INDEX.md` (line 60) both correctly
  show `VERIFIED` — only `IP-1150`'s own header text drifted. This is precisely the drift class
  `BL-0008` predicted and was first observed fixing (for `IP-1120`, in run #6) — it has now
  materialized on a second package, and specifically on the one package whose own header was never
  touched again after its `VR` shipped (unlike `IP-1120`, which got a later, unrelated edit that
  incidentally caught its stale header).
- **Finding 3 (new, Low):** `docs/features/feature-index.md`'s one-line descriptions for
  `FS-112`/`FS-113`/`FS-114`/`FS-115` still end in "...; build status unverified" — stale prose
  from before this tranche's `07`/`08`/`09` passes resolved exactly that uncertainty (all four
  Features' packages are now `VERIFIED`). The `✅ Done` status column itself is accurate; only the
  trailing clause is stale.

### 5. Documentation coherence

Spot-checked `docs/training/15-manual-traceability.md` §15.1 (the feature→manual forward index)
against the 7 tranche-2/forward-design packages, then confirmed by direct search of the three
per-cell manuals (`docs/training/12-14`) for each feature's own vocabulary.

- **`IP-1140` (Hot-Seat Hand-Off)** — documented: `WCM-3` ("Run the room: hot-seat and LAN")
  explicitly describes the ⏸ Handover blur mechanism, matching the shipped behavior.
- **Finding 1 (new, Medium): five of the seven tranche-2/forward-design features have zero
  mentions anywhere in the per-cell manuals, and no row in §15.1.** Confirmed by case-insensitive
  search across all three manuals for each feature's own terms — zero hits in every case:
  - `IP-1120` Classification Banner — no mention of "classification" anywhere in `12-14`.
  - `IP-1130` Observer Read-Only Access — no mention of "Observer" anywhere in `12-14`.
  - `IP-1151` Seat-to-Role Assignment — no mention of "assign_role"/"seat-to-role"/"staffing"
    anywhere in `12-14` (the closest §15.1 row, "Vignette load + parameter dials" → `WCM-2`, does
    not cover seat/role staffing).
  - `IP-2010` Competency Assessment — no mention of "assessment"/"competency"/"rubric" anywhere in
    `12-14`; the White-Cell-only assessment panel this package shipped has no facilitator-facing
    manual section at all, not even in `WCM-6` ("Monitor both sides"), the section that documents
    every other White-Cell-only ground-truth surface.
  - `IP-3010` Research Analytics — no mention of "research_batch"/"RunRecord"/batch export anywhere
    in `12-14`.

  This is a real coverage gap, not a stale-citation nit: these are five `VERIFIED`, shipped,
  operator-facing (four of five White-Cell-facing) capabilities with no procedural instruction
  anywhere in the training corpus, and no §15.1 row telling a future maintainer which section to
  update if the code changes again. Given the project's 2026-07-04 elevation of the training
  corpus to a co-equal, requirement-bearing product (`MSTR-001` §2; `FR-11110`'s role-scoped
  *coverage* mandate; assumption **A12**'s named currency risk), this is a material gap for a
  tranche that has otherwise fully cleared verification — not a cosmetic one. It also converts
  `BL-0027`'s previously abstract "A12 risk" into a concrete, scoped instance: the corpus's
  currency gap is not hypothetical, it is these five features, today.
- `CLAUDE.md`'s Code Map and status line, and the affected `ROADMAP.md`/`docs/architecture/`
  `INDEX.md` files, were spot-checked and found current for this tranche (each package's own `08`
  run updated them at implementation time; no drift found in this pass beyond Findings 2–3 above,
  which are package/feature-index-local, not `CLAUDE.md`/`ROADMAP.md`-level).

## Backlog items spot-checked this review

| Item | Disposition this review |
|---|---|
| `BL-0004` (11 as-built packages carry `VERIFIED` with no `VR-xxxx` evidence) | **Reconfirmed true**, directly (dimension 4). Still open — a user decision (retro-verify vs. explicitly accept) is now due; see Recommendations. |
| `BL-0008` (package-doc header drift vs. Master Build Plan) | **Materialized a second time**, on `IP-1150` (Finding 2). The systemic risk this entry named is no longer hypothetical. |
| `BL-0011` (Observer route-guard maintenance drift) | **Reconfirmed clean** (dimension 1) — no new route has lost guard coverage since `VR-1130`. |
| `BL-0015` (`IP-1140`'s accepted FR-6610 risk) | **Reconfirmed unchanged** — the project owner's risk acceptance still stands; no new information found that would reopen it. |
| `BL-0027` (training-corpus doc-coherence risk, A12) | **Concretized**, not merely reconfirmed — see Finding 1, which supersedes this entry's abstract framing with a scoped, owned finding. |

## Findings

| # | Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|---|
| 1 | Training corpus has no coverage for 5 of 7 tranche-2/forward-design features | `IP-1120`, `IP-1130`, `IP-1151`, `IP-2010`, `IP-3010`; `docs/training/12-14`, `15-manual-traceability.md` §15.1 | Zero mentions in any per-cell manual, zero §15.1 rows, for classification banner, Observer seat, seat-to-role staffing, competency assessment, and research analytics — all `VERIFIED`, shipped, mostly White-Cell-facing capabilities. `IP-1140` is the one tranche-2 feature that *is* documented (`WCM-3`), showing this is a gap, not a policy of omission. | **Medium** | `08-training-manual-authoring` (author the missing WCM/BLU sections + §15.1 rows); governing requirement is `FR-11110` |
| 2 | `IP-1150`'s own package-doc header is stale | `docs/implementation/packages/IP-1150-vignette-selection.md` | `Status:` still reads `COMPLETE` and `Referenced By` still calls `IP-1120`/`IP-1151` `BLOCKED`, though `VR-1150` verified it in run #3 and both downstream packages have been `VERIFIED` since runs #13/#15. Master Build Plan and `packages/INDEX.md` are both correct — only this file's own header drifted. Materializes `BL-0008`'s predicted risk. | Low | `07-implementation-planning` (fold into next touch of `IP-1150`, per `BL-0008`'s own precedent) |
| 3 | `feature-index.md` descriptions stale for FS-112–115 | `docs/features/feature-index.md` | Trailing "...; build status unverified" clause is stale — that uncertainty was resolved by this tranche's `07`/`08`/`09` passes. Status column (`✅ Done`) itself is accurate. | Low | `06-feature-specification` / `05-feature-decomposition` (next touch of the feature index) |

No Critical or High findings. Both pre-existing High-severity items in this tranche's history
(`BL-0002`, `BL-0015`) were already resolved/adjudicated by the project owner before this review
ran, and both were re-confirmed still resolved (dimension 3, backlog table above).

## Conclusion

The 18-package tranche **composes cleanly** at the level this review can check: interfaces agree
end-to-end (full suite green, no regression), the load-bearing invariants hold across every
package (both permanent gates green), and no behavioral divergence or dead-end workflow was found
beyond the single already-adjudicated `BL-0014` instance. The three findings above are all
documentation/traceability-coherence issues, not defects in shipped behavior — none blocks a
`11-release-readiness` pass on functional grounds. Finding 1 (Medium) is the one item worth
resolving, or at minimum explicitly accepting, before this tranche's coverage is presented as
complete, given the project's own stated position that the training corpus is a co-equal,
release-gating product.

## Related

[`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md) ·
[`docs/pipeline/backlog.md`](../pipeline/backlog.md) ·
[`docs/training/15-manual-traceability.md`](../training/15-manual-traceability.md) ·
[`docs/features/feature-index.md`](../features/feature-index.md)
