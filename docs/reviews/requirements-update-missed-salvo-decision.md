# Requirements Update Report — Missed Kinetic Salvo Consumes Its Rounds (2026-10-17)

> **Status:** Complete. **One numbered FR leaf added** (`FR-1480`, under `FR-1400`, promoted from
> candidate `CR-28`). One leaf amended (`FR-1460` Acceptance Criteria and Notes). RTM updated.
> **Source:** `docs/pipeline/backlog.md` `BL-0249` — the project owner decided on 2026-10-17 that
> **a kinetic salvo that misses still consumes its interceptor rounds**: ammunition is charged on
> every shot fired, not only on hits. This is the "documentation gap closed by the owner of the
> missing input" that promotion of a candidate needs (the gap `CR-28` recorded: "no input document
> states a rule for a miss"). Driven by `00-pipeline-manager` in override mode (`run
> 04-requirements-engineering CR-28`).
> **Scope (written):** `docs/requirements/01-functional-requirements.md`,
> `03-requirements-traceability-matrix.md`, this report. `02-non-functional-requirements.md` is
> unaffected.
> **Inputs read (role mapping, per this skill's layout note):**
> - Architecture role: GDS-04 §1.2 "Persistent state" and "Constraints" (ammunition is an Asset
>   resource level; resource levels cannot go negative).
> - Requirement leaves: `FR-1410` (resource consumption as an effect side effect), `FR-1460`
>   (salvo bounded by remaining ammunition), `FR-1470` (jammer power rating), `FR-3410`
>   (execute-time re-validation); candidate `CR-28` (its exact text, promoted).
> - Downstream context, for the as-built reading only, never as a source: FS-132 Open Question 3,
>   `IP-1320` Feature Reference and Design Decision 5, `VR-1320` §4.
> **No architecture was redesigned and no fact was originated.** The rule is the owner's.

## 1. Changes applied

| Item | Change | Traced to |
|---|---|---|
| `CR-28` → **`FR-1480`** | New Must leaf **"Charge a kinetic engagement's salvo against the effector's ammunition whether the engagement hits or misses."** Description: the salvo is deducted whenever the engagement is fired at its execution moment, success or failure, so a miss costs the same rounds as a hit. Precondition: the engagement passed `FR-1460`'s validation bound and its execute-time re-check. Acceptance Criteria: hit → `N − S`; miss → `N − S`; an engagement that fails the execute-time re-check is not fired and charges nothing; outcomes for the same seed are unchanged. Notes: a salvo against a target already destroyed by its execution moment is treated as fired (no source describes an abort; the owner's rule is "every shot fired"). `CR-28` stays in the Candidate section marked `PROMOTED`, for audit continuity (the `CR-19`/`CR-20` precedent). | `BL-0249` owner decision; `CR-28`'s own text ("A missed kinetic salvo consumes its rounds"); GDS-04 §1.2. |
| `FR-1460` | **Acceptance Criteria amended.** Was: "...a successful engagement leaves the effector with `N` minus the salvo" (covered only a hit). Now: "...once it executes — whether it hits or misses — it leaves the effector with `N` minus the salvo (`FR-1480`)". The validation bound (Description), the rejection behaviour and the "never negative" Postcondition are **unchanged**. Notes record the amendment. | `BL-0249`; `FR-1480`. |
| RTM | `FR-1480` row added (C1, INT-0008; Feature/Test/Package `UNASSIGNED` until FS-132 and a package carry it); `FR-1460` row annotated; `CR-28` row marked `PROMOTED`; `FR-1480` added to the C1 and INT-0008 reverse rows. | — |

**Why a new leaf instead of rewording `FR-1460`.** `FR-1460` is a validation bound (refuse an
oversized salvo; never go negative). Charging a miss is an independently testable consumption rule.
Folding it into `FR-1460` would join two behaviours with an "and" (the atomicity rule). `FR-1460`'s
AC is amended only so it no longer states the old hit-only charge.

## 2. Review findings

| Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|
| Downstream impact (spec) | `FR-1480`, FS-132 | FS-132 Open Question 3 deferred this rule and System Behaviour 3 / Acceptance Criterion 2 state the hit-only charge. | Medium | `06`: update FS-132 to implement `FR-1480` and close OQ3 with the owner's answer. |
| Downstream impact (catalog) | `FR-1480`, `FEAT-1400` | `FR-1480` joins `FEAT-1400` by parentage (an `FR-1400` child), the same rule the run #151 sweep applied to `FR-1460`/`FR-1470`, but the catalog row's Included Requirements does not list it yet. | Low | `05`: add `FR-1480` to `FEAT-1400`'s Included Requirements at its next delta pass (the F-13 mechanical check). |
| Downstream impact (code) | `FR-1480` | Shipped `engine/orders.py::_h_effect` charges the salvo only when the outcome succeeds. | Medium | `07`: a remediation package; `08` implements it. |
| Downstream impact (manual) | `FR-1480` | `RED-5` says "Rounds are spent only on success"; the §15.1 effect-resource-bounds row says the same. | Low | `08-training-manual-authoring`, once the package is `VERIFIED`. |

No duplicate, conflict, impossible or architecture-violating requirement was found in the touched
area. `FR-1480` is consistent with `FR-1460` (the re-check still runs first, so the charge cannot
drive ammunition negative) and with `FR-1470` (a jam still consumes nothing).

## 3. Quality gate

- [x] `FR-1480` carries the full field set; every statement cites a real source.
- [x] `FR-1480` is atomic, unambiguous, testable and implementation-independent.
- [x] No requirement now contradicts another or an ADR.
- [x] The candidate was promoted only because its gap was closed by the owner's decision, not in
      the pass that named it (`CR-28` was named in run #160).
- [x] The review reviewed the final on-disk text; the matrix uses `UNASSIGNED` honestly.

## Related

[`01-functional-requirements.md`](../requirements/01-functional-requirements.md) `FR-1460`,
`FR-1480`, `CR-28` ·
[`03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md) ·
[`requirements-update-deferred-clearance-batch.md`](requirements-update-deferred-clearance-batch.md)
(where `CR-28` was recorded) · [FS-132](../features/FS-132-effect-resource-bounds.md)
