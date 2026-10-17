# Requirements Update Report — Deferred-Backlog Clearance Batch (2026-10-17)

> **Status:** Complete. No numbered FR or NFR added. Five leaves amended (`FR-6220`, `FR-7410`,
> `FR-7420`, `FR-4420`, `FR-3310`), one NFR verification method amended (`NFR-3400`), three
> candidates added (`CR-26`–`CR-28`), and four RTM defects corrected. One item is closed without
> an edit (`BL-0248`). One item stays with the project owner (`BL-0249`, now candidate `CR-28`).
> **Source:** `docs/pipeline/backlog.md`: `BL-0033`, `BL-0148`, `BL-0138`, `BL-0100`, `BL-0137`,
> `BL-0130`, `BL-0249`, `BL-0050`, `BL-0248`, `BL-0027`. The pipeline manager (run #160) batched
> them in the project owner's 2026-10-17 instruction to clear the `DEFERRED` backlog. The parked
> `NEEDS-USER` entries (`BL-0171`, `BL-0181`, `BL-0187`, `BL-0215`, `BL-0233`) are untouched.
> **Scope (written):** `docs/requirements/01-functional-requirements.md`,
> `02-non-functional-requirements.md` (`NFR-3400` only), `03-requirements-traceability-matrix.md`.
> **Inputs read (the role mapping, per this skill's layout note):**
> - Architecture role: GDS-05 (`docs/architecture/05-functional-requirements.md`) FR-P3; GDS-04
>   §1.2; `strategic-assumptions-register.md` A12.
> - Requirement leaves: `FR-6220`, `FR-6210`, `FR-6510`, `FR-7410`/`FR-7420`/`FR-7430`,
>   `FR-4410`/`FR-4420`, `FR-1460`, `FR-3310`/`FR-3210`, `FR-5410`, `FR-5314`, `NFR-1600`,
>   `NFR-3400`.
> - Intake sources: `BL-0069` (B3), `BL-0070` (B4).
> - Shipped behaviour, for the as-built reading only, never as a source: the `ui_web/server.py`
>   route table at `e1e721c`, `engine/orders.py` (`issue`/`_plan_collection`), `engine/ssn.py`,
>   `content/vignette.py` (`Inject.repeatable`), and the `VR-1062`/`VR-1210`/`VR-1180` findings.
> **No architecture was redesigned and no fact was originated.**

## 1. Changes applied

| Item | Change | Traced to |
|---|---|---|
| `BL-0138` | **`FR-6220` named set enumerated.** The Description listed five flows. A static review of the route table (this leaf's own Inspection method) found more no-cell routes that other baselined leaves already require: the truth ephemeris export (`FR-7410`), the assessment report (`FR-10110`), the Observer view (`FR-6510`, which dispatches to the god-view or a cell view), and White Cell facilitation/authoring reads (inject list, vignette catalogue/source/tutorial, Vignette Creator draft state/preview/seats, role staffing). Each is now named with its owning leaf. `FR-7410`'s Description now defers to that set instead of repeating the five-item list. | `FR-6220` Postcondition and Acceptance Criteria; the owning leaves named. |
| `BL-0137` | **`FR-7410`/`FR-7420`: one asset per export.** "One or more" was this baseline's own wording. The source (B3) does not state a per-file object count, and the Acceptance Criteria were always per export. As built, each export takes one `object_id`. | `BL-0069` (B3); the skill's rule against sharpening beyond the source. |
| `BL-0130` | **`FR-4420` Precondition.** It read "a non-repeatable ... inject must not have already fired", which implied an unspecified re-fire rule. It now states the sourced fire-once behaviour; a re-fire rule is candidate `CR-27`. | `BL-0070` (B4); FUTURE-WORK §13 R18. |
| `BL-0050` | **`FR-3310` Outputs** restated in GDS-05 FR-P3's own terms (the kinds "behave identically" for queue, timeline, undo and time-travel), replacing "queryable through one queue/timeline". The Notes record the as-built mapping. | GDS-05 FR-P3. |
| `BL-0100` | **`CR-26`** (candidate): an unreadable configured external directory is skipped and disclosed. `IP-1180` Design Decision 2 is a planning-level choice, and a package is not a requirements source. | `BL-0100`. |
| `BL-0249` | **`CR-28`** (candidate): a missed salvo consumes its rounds. No input states a rule for a miss. | `BL-0249`; FS-132 OQ3. |
| `BL-0027` | **`NFR-3400` verification method** gains an automated `> Sources:`-anchor check. This is the mitigation A12 names, and A12's revisit trigger fired when `BL-0029` found real drift. The test itself is code (`07`/`08`, `BL-0260`). | A12. |
| `BL-0033` | RTM `FR-1220` Impl. Package attributed to `IP-1010`/`IP-1040`/`IP-1050`/`IP-1051`, all `VERIFIED`. | `VR-1010`/`1040`/`1050`/`1051`. |
| `BL-0148` | RTM NFR master table gains an `Impl. Package` column. The seven rows that carried an unheaded ninth cell are now well-formed; the others read `UNASSIGNED`. A whole-matrix cell-count check finds no remaining malformed row. | `BL-0009`/`BL-0034` defect class. |
| — | RTM Title defects corrected: `FR-3310` ("order queue / cancel leaf"), `FR-6220` ("Observer fog-of-war view"). | `01`'s own headings. |
| `BL-0248` | **No edit.** Re-parenting `FR-5314` under `FR-4200` would need a renumbering, because the ID encodes its parent. That would break every citation of `FR-5314` (RTM, FS-131, `IP-1310`, tests). Ownership by FEAT-4200 is already recorded in `05-feature-review.md` F-14. The finding is cosmetic and is closed. | — |

## 2. Review findings

| Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|
| Decision needed (owner) | `CR-28`, `FR-1460` (`BL-0249`) | Whether a missed salvo consumes its rounds is a game-rule choice. Charging a miss changes shipped behaviour and `RED-5`. | Low | Project owner decides. If adopted, promote `CR-28` to a leaf under `FR-1400` and route a `07` package. |
| Missing verification | `FR-3310` | No test exercises the Acceptance Criterion for an SSN request (rewind before collection, then parity with a command). | Low | `07`: a test-only follow-up (`BL-0259`). |
| Missing verification | `NFR-3400` | The amended method names a test that does not exist yet. | Low | `07`/`08`: author the `> Sources:`-anchor test (`BL-0260`). |
| Consistency (outside scope) | `FR-6220` vs `CLAUDE.md` "LAN trust model" | `CLAUDE.md` still lists only five no-cell endpoints. | Low | Update `CLAUDE.md`'s list at the next baseline-record pass (`BL-0261`). |
| Downstream impact | `FR-7410`/`FR-7420` | No package change: the shipped single-`object_id` export now meets the leaf as written. `FS-121`'s own prose may still say "one or more". | Info | `06`, at its next `FS-121` touch. |

No duplicate, impossible or architecture-violating requirement was found in the touched area.
Every amended leaf remains atomic and testable.

## 3. Traceability matrix delta

- `FR-1220`: Impl. Package cell attributed.
- `FR-3310`, `FR-6220`: Title corrected; row annotated.
- `FR-4420`, `FR-7410`: row annotated.
- NFR master table: `Impl. Package` column added; 25 rows gained `UNASSIGNED`, 7 rows' existing
  ninth cell now sits under a header.
- `CR-26`–`CR-28`: new candidate rows, every forward cell `UNASSIGNED`.

## 4. Quality gate

- [x] Every changed leaf keeps its full field set; every new statement cites a real section.
- [x] The amended leaves are atomic, unambiguous, testable and implementation-independent.
- [x] No requirement now contradicts another or an ADR.
- [x] The review reviewed the final on-disk text.
- [x] Candidates were not promoted; the matrix uses `UNASSIGNED` honestly.

## Addendum — closing straggler (run #172, 2026-10-17)

| Item | Change | Traced to |
|---|---|---|
| `BL-0263` | `FR-5220` Related Interfaces corrected INT-0013 → INT-0006, INT-0011; RTM Arch. Component C5, C10 → C4, C2, C5 and Interface cells corrected; `FR-5220` added to the C2/C4/C5 and INT-0006/INT-0011 reverse-index rows (it was missing from every component row). | ICD pass 3 (run #161): file-based import travels console → SessionAPI and C2 parses through C5; INT-0013 is the Space-Track network fetch only. |
| `BL-0101` | `FR-4430` Notes: the requirement fixes the cause categories and the recorded-not-re-derived Postcondition; no source states which `BusState` change each category produces, so the as-built mapping (`bus` → safe mode with the controller cause, recoverable; `telemetry` → comms red; `IP-1062` DD4 as remediated) is confirmed as satisfying the leaf, and any change to it is a `06`/`07` design change. | `FR-4430` Description/Postcondition; `BL-0128` remediation. |

No new finding. No numbered leaf added or behaviour changed.

## Related

[`01-functional-requirements.md`](../requirements/01-functional-requirements.md) ·
[`02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md) ·
[`03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md) ·
[`docs/pipeline/backlog.md`](../pipeline/backlog.md)
