# Requirements Update Report — Parked Design-Questions Batch (2026-10-15)

> **Status:** Complete. One numbered leaf amended (`FR-7440`), one candidate added (`CR-22`), and
> two RTM title defects corrected. Two questions are reported for adjudication rather than resolved
> (`BL-0171`, plus `BL-0113`, closed with a no-amendment finding). No new numbered FR or NFR.
> **Source:** `docs/pipeline/backlog.md`: `BL-0171`, `BL-0113`, `BL-0159`, `BL-0181`, `BL-0010`,
> `BL-0012`. The pipeline manager (run #116) batched them because each one's trigger was "the next
> `04-requirements-engineering` pass". `BL-0187` (Red-satellite `bus_state`, a vignette-content
> decision parked with the project owner) was explicitly **excluded** and is untouched.
> **Scope (written):** `docs/requirements/01-functional-requirements.md` (`FR-7440`, header note,
> `CR-22`) and `docs/requirements/03-requirements-traceability-matrix.md` (two Title cells, the
> `FR-7440` row annotation, the `CR-22` row, header note). `02-non-functional-requirements.md` was
> read and is unchanged.
> **Inputs read (the role mapping, per this skill's layout note):**
> - Architecture/ConOps role: `docs/architecture/05-functional-requirements.md` (GDS-05) §FR-B3,
>   and `docs/architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md` Decision 5.
> - Domain role: GDS-04 §3 (`last_telemetry_time`).
> - Requirement leaves: `FR-2310`, `FR-2320`, `FR-1620`, `FR-6210`, `FR-7410`/`FR-7420`/`FR-7440`,
>   `FR-8210`, `FR-4510`, `FR-6510`, and `docs/reviews/training-review-run97-scope.md` F7.
> - Shipped behaviour, for the as-built reading only, never as a source: `session/manager.py`
>   (`get_telemetry`, `get_series`, `telemetry_export`), `engine/telemetry.py::sample`,
>   `engine/access.py` (the `FR-1620` exclusion check) and `IP-1211` Design Decision 5.
> **No architecture was redesigned and no fact was originated.**

## 1. Changes applied

| Item | Change | Traced to |
|---|---|---|
| `BL-0159` | **`FR-7440` amended.** "Visible to the requesting cell" now means what `FR-6210` already exposes: the cell's own satellites plus any satellite it holds a `Track` on. Before, it meant "holds a `Track`", which read literally excluded a cell's own fleet, because a cell never tracks its own assets. A tracked satellite's TLE still reads belief, never truth. An own satellite's TLE reads its actual state, which the cell knows exactly. Description, Inputs, Preconditions, Postconditions, Acceptance Criteria, Source Documents and Notes were updated; priority and verification method are unchanged. | `FR-6210` (a cell's view = own assets + held tracks); `ADS-1500` Decision 5 ("a cell always knows its own asset's true state exactly; custody … only [applies] to its knowledge of *other* objects"); `BL-0109`'s own wording ("any satellite visible to the requesting cell"); `FR-8210`, which already treats a cell's own assets as part of its view. |
| `BL-0181` | **`CR-22` added** (Candidate, not baselined): human-readable time bounds for the time-span exports. | `BL-0181`, from `REV-TRN-002` F7, a review observation. That is not an owner request or architecture statement, so it cannot enter the numbered baseline (the skill's no-invention rule). |
| `BL-0010` | RTM Title of `FR-4510` corrected from "Observer view" to "Classification banner set and displayed". | `01`'s own `FR-4510` heading. |
| `BL-0012` | RTM Title of `FR-6510` corrected from "Multi-monitor pop-out windows" to "Observer read-only view with no command ability". | `01`'s own `FR-6510` heading. |

## 2. Review findings

| Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|
| Conflict (requirement wording vs. its own Postcondition, and vs. as-built) | `FR-2320`, `FR-2310`, GDS-05 FR-B3 (`BL-0171`) | Two readings of the scope:<br>• **Pass-gating covers only the SOH snapshot.** GDS-05 FR-B3 and `FR-2310` require pass-gating of "the displayed SOH snapshot" (updated only at contact, timestamped last-known value between contacts).<br>• **`FR-2320` says otherwise.** Its Description calls the export "the requesting cell's own **pass-gated** telemetry channel history". Its Postcondition requires values "identical to what the same cell's own live telemetry endpoint would show at each sampled point".<br>As built, the live engineering-telemetry endpoint (`get_telemetry`, the drill-down), the history graph (`get_series`) and the export all report every sampled instant, **including between contacts**. Only the SOH snapshot path is gated. So `FR-2320`'s Postcondition matches the shipped system and its "pass-gated" wording does not. The sources do not settle which reading is right. GDS-05 FR-B3's first clause ("Ground-visible telemetry shall be pass-gated") is broader than its own elaboration ("the displayed SOH snapshot"). | Medium | **Adjudication by the project owner / architecture owner — not resolved here.** Two clean options:<br>**(A)** Pass-gating applies to the SOH snapshot only. Amend `FR-2320` to drop "pass-gated" and state that engineering telemetry history is ungated. This matches the as-built system; no code change.<br>**(B)** Pass-gating applies to every ground-visible telemetry read, live and historical. Amend `FR-2320`/`FR-2310`, decide how a between-contact gap reads (held last value, gap or null), and decide whether White's read is exempt. This needs a remediation package for the drill-down, series and export.<br>Option (A) is the smaller change; option (B) is closer to the realism GDS-01 §1 emphasises. Either is a product decision. |
| Ambiguity (judged non-blocking) | `FR-1620` (`BL-0113`) | `FR-1620` does not say whether an exclusion-angle rejection must be distinguishable from a lighting-predicate rejection. Its sources (`BL-0073`, `R109` §3.7) are silent too. As built (`engine/access.py`), both suppress the access window at the same predicate layer, so an operator sees the same "no window" outcome either way. `FR-1620`'s Acceptance Criteria are fully satisfied by that behaviour. | Low | **No amendment.** `FR-1620` as written does not require distinguishable reasons, and nothing in the inputs supports adding one. If the owner wants a distinct operator-visible reason, file it through `00-intake` as a feature (it would enter as a candidate, like `CR-22`). `BL-0113` can close. |
| Consistency (observation, no change) | `FR-7420` vs. amended `FR-7440` | `FR-7420` scopes the cell-observed ephemeris export to "tracked objects", so a cell exporting its own satellite gets a header-only file (documented as-built in `BLU-13`/`RED-12`). Unlike `FR-7440`, that scope is explicit in `FR-7420`'s own Description and Rationale ("as distinct from ground truth", the cell's belief). It is a deliberate scope rather than an accidental literal reading, so it was **not** amended. | Low | None required. Revisit only if the owner asks for own-asset history in that export; `FR-2320` (telemetry) and `FR-7410` (White's truth export) already cover own-asset history. |
| Downstream impact | `FR-7440` → `IP-1211`, `FS-121`, `BLU-12`/`RED-11` | The shipped quick TLE export implements the pre-amendment reading (`IP-1211` Design Decision 5 rejects an own asset with no `Track`), so it now under-delivers the amended `FR-7440`. | Low | `06-feature-specification` updates `FS-121`'s `FR-7440` behaviour, then `07-implementation-planning` writes a small remediation package against `IP-1211`. Afterwards `08-training-manual-authoring` updates `BLU-12`/`RED-11`/`WCM-14` if they describe the rejection. |

No duplicate, impossible or architecture-violating requirement was found in the touched area.
The amended `FR-7440` remains atomic (one export behaviour; the own/tracked split is a definition
of its input domain, not a second behaviour) and testable (three-branch Acceptance Criteria).

## 3. Traceability matrix delta

- `FR-4510`, `FR-6510`: Title cells corrected; no other cell changed.
- `FR-7440`: row annotated with the amendment and the owed remediation. Its forward cells (`FS-121`,
  `IP-1211`, tests) are unchanged until downstream work lands.
- `CR-22`: new candidate row, every forward cell `UNASSIGNED`.

## 4. Quality gate

- [x] Every changed leaf keeps its full field set; every new statement cites a real section.
- [x] The amended leaf is atomic, unambiguous, testable and implementation-independent.
- [x] No requirement now contradicts another or an ADR. The `FR-2320` tension is reported, not
      papered over.
- [x] The review reviewed the final on-disk text.
- [x] Recommendations for findings are proposed, not applied. The applied changes are the four
      items in §1, each the pass's own target.
- [x] `CR-22` is a candidate with `UNASSIGNED` forward cells; nothing guessed.
- [x] No new fact, architecture decision or code.

## Related

[`01-functional-requirements.md`](../requirements/01-functional-requirements.md) ·
[`03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md) ·
[`ADS-1500`](../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md) ·
[`requirements-update-ric-cats-batch.md`](requirements-update-ric-cats-batch.md) (where `FR-7440`
was first baselined)
