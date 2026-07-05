[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — Runs #16/#19 Scope (Observer, Classification/Staffing, Assessment, Research Batch)

> **Document ID:** REV-TRN-001
> **Skill:** `09-training-manual-review`
> **Scope:** the training-corpus sections authored/touched by pipeline runs #16 (R600 tier) and
> #19 (`08-training-manual-authoring` closing `BL-0029`/`BL-0026`) — `docs/training/02-interface.md`,
> `docs/training/12-white-cell-manual.md` (`WCM-1`, `WCM-2`, new `WCM-11`, `WCM-12`),
> `docs/training/13-blue-cell-manual.md`, `docs/training/14-red-cell-manual.md`,
> `docs/training/15-manual-traceability.md` (§15.1/§15.2 new rows, new §15.6), and
> `docs/training/INDEX.md`.
> **Commit reviewed:** `8574ca99d3cfb1441f8b9001dd24373754fa620b` (`origin/main` tip at review time,
> the PR #48 merge — no changes to the reviewed scope since runs #16/#19 landed it)
> **Precondition confirmed:** neither run authored anything in this session; this review is
> independent of both.
> **Upstream:** `08-training-manual-authoring` (run #19), `02-research-training-pedagogy` (run #16)
> **Downstream:** `10-integration-review` (next tranche pass), `11-release-readiness`

## Dimensions exercised

### 1. Accuracy — prose claims vs. shipped code

Read the live source for every claim in scope and confirmed each directly, rather than trusting
the manual's own citations:

- **Observer seat** (`WCM-1`, `02-interface.md` §3): `spacesim/session/inprocess.py` defines
  `set_observer_view`/`get_observer_view`/`observer_designation` (lines 295-320) dispatching to
  `get_godview`/`get_view` as claimed; `ui_web/server.py` exposes
  `POST/GET /api/sessions/{sid}/observer/view` and `GET .../observer/designation`. The "rejected
  even against a request that bypasses the UI entirely" claim matches `IP-1130`'s
  `_reject_observer` guard, independently confirmed by `VR-1130`.
- **Classification override + seat-to-role staffing** (`WCM-2`): `SessionManager.__init__` accepts
  `classification` and defaults to the vignette's own; the value is threaded into `save_state`
  (`manager.py:471`) and restored by `from_state` (`:487`), and into `aar.py`'s `AARReport.classification`
  (read by CSV/JSON export) — confirmed by direct read, matching the "fixed for the session's
  lifetime … carries into every screen, AAR export, and save file" claim. `assign_role`/
  `_role_covers`/`staffing_report` (`manager.py:112-131`) and `InProcessSession.start()`
  (`inprocess.py:131-141`) confirmed to hard-block `Start` with the unmet entry named in the `Ack`
  reason — exactly as described, not a warning.
- **Competency assessment** (`WCM-11`): `session/assessment.py`'s `score_custody_quality`/
  `score_window_discipline`/`score_belief_truth_divergence`/`assessment_report` all exist as named;
  `GET /api/sessions/{sid}/assessment` (`server.py:557-563`) wires to `api.assessment_report`. The
  "no composite score" and "White-Cell-only, current-exercise-only" framing, and the explicit
  `BL-0019`/`BL-0020` cross-reference, match both the code and the open backlog entries verbatim.
- **Offline research batch exports** (`WCM-12`): `spacesim/tools/research_batch.py`'s `run_batch(
  vignette_id, seeds, condition_label, n_steps_or_until)` signature matches exactly, including the
  "omitted → run to the vignette's own horizon" semantics and "no shared mutable state between
  runs" (each iteration constructs a fresh `SessionManager`). `session/research_export.py`'s
  `RunRecord` carries exactly `vignette_id`/`seed`/`condition_label`/`assessment` — confirming the
  "no trainee-identifying or cross-institution data" claim.
- Ran the playbook verification suite against the reviewed commit:
  `python3 -m pytest spacesim/tests/test_vignette_tutorials.py` → **16 passed**, matching every
  prior run's count (FR-11420/NFR-3400 machine-checkable slice, unchanged since run #19).
- `02-interface.md`'s four-cell framing (White/Blue/Red/Observer) is current — the pre-run-#19
  "three cells" staleness this scope was authored to fix is gone.

No claim in the reviewed scope describes removed, renamed, or non-existent behavior. Sampling
note: the six shared-onboarding modules (01, 03-11) and the two AI-Red/AAR-adjacent sections of
`06`/`07` were **not** re-verified — they are outside runs #16/#19's touched scope and were not
part of this review's assignment.

### 2. Traceability integrity

Checked `training/15` §15.1/§15.2's new/touched rows against both directions and against the
`> Sources:` footers in `WCM-1`, `WCM-2`, `WCM-11`, `WCM-12`, `BLU-1`, `RED-1` — forward and
reverse index agree with each other and with every footer's module list, **with one exception**:
see Finding 1. The §15.6 cross-links this scope added (`BLU-9`↔`RED-6`, `BLU-3`↔`RED-3`,
`BLU-4`↔`RED-4`) all resolve to real, correctly-anchored sections in the sibling manual — each
"See also" line's markdown anchor was checked against the target section's actual heading slug.
Learning-path linkage (§15.4) was not touched by this scope and was not re-checked.

### 3. Coverage

All five tranche-2/forward-design features `BL-0029` named as missing (Observer, Classification
override, Seat-to-role staffing, Competency assessment, Research analytics) now have both a manual
section and a §15.1 row, confirmed present. No feature that shipped after run #19 falls inside
this review's scope (the 11 packages retro-verified in runs #20-#29 are pre-existing, as-built
mechanics already covered by the pre-existing shared-onboarding modules, not new capability this
scope needed to add).

### 4. Pedagogy

`WCM-11`/`WCM-12` are appropriately scoped to the White Cell audience (facilitator/researcher
actions only, no Blue/Red-facing prose); `WCM-11`'s disclosure-before-trust framing ("read that
disclosure before treating the tiers as more authoritative than they are") is a sound instructional
choice for a rubric with a stated non-validated design choice. §15.6's layout evaluation is grounded
in an authored R600 topic (R606, cited with its specific success criterion, not just named) — the
R600-grounding gap flagged by earlier reviews does not apply to this scope. Module sizes (`WCM-1`,
`WCM-2`, `WCM-11`, `WCM-12`) all fall well within NFR-3500's per-module budget by inspection.

## Findings

| # | Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|---|
| 1 | Wrong backing-code filename for the fog-of-war boundary | `docs/training/12-white-cell-manual.md` (`WCM-1` Sources), `docs/training/13-blue-cell-manual.md` (`BLU-1` Sources), `docs/training/14-red-cell-manual.md` (`RED-1` Sources), `docs/training/15-manual-traceability.md` (§15.1 "Fog-of-war boundary & per-cell view" row, §15.2 `WCM-1`/`BLU-1`/`RED-1` rows) | All seven citations name `spacesim/session/controller.py` as the fog-filter module. That file does not exist and never has (`git log --all --diff-filter=A` finds no such path ever added). The actual `CellController` class — the fog-of-war boundary these sections describe — lives in `spacesim/session/cells.py`. This is a genuine misattribution, not ordinary line-drift: a developer following the Sources footer or the §15.2 reverse index to "confirm the prose still matches reality" (§15's own stated purpose) would look for a file that isn't there. The underlying behavioral claims in all four sections are otherwise accurate. | Medium | `08-training-manual-authoring` (correct `session/controller.py` → `session/cells.py` in all seven locations at its next touch of any of these four files) |

No Critical or High findings. No accuracy, coverage, or pedagogy defects found beyond Finding 1.

## Independence statement

This review's session authored none of `docs/training/02`, `12`, `13`, `14`, `15`, or `INDEX.md` —
all reviewed content was authored by prior sessions (runs #16/#19 and the earlier PR #46 pass that
first landed the per-cell manuals). No content from this review's own session appears in the
reviewed scope.

## Result

**Clean apart from one Medium finding.** The reviewed scope's behavioral claims are accurate
against the shipped code, machine-verified playbook coverage is unchanged (16/16 passing), and the
bidirectional traceability holds except for the one systemic filename error above. Recommend
routing Finding 1 to `08-training-manual-authoring`'s next touch of any of the four affected files;
it does not block `10-integration-review` or a release pass on its own (Medium, prose-only, no
functional or behavioral impact).
