# IP-1093 — Release Dependency Lock Re-Pin (`NFR-1510`)

> **Package ID:** IP-1093
> **Version:** 1.0
> **Status:** READY (authored 2026-10-31 by `07-implementation-planning`; no package dependency)
> **Authorization (MSTR-006 §3):** **given.** The project owner's go-ahead of 2026-10-31, in the planning session that commissioned this package ("build before release ... the dependency lock re-pin"), covers this package and no other.
> **Dependencies:** none (the procedure is `CLAUDE.md` "Release dependency lock"; input is [release-assessment-release-candidate-5.md](../../reviews/release-assessment-release-candidate-5.md) §2.4, finding `S-3`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [01-technical-work-breakdown.md](../01-technical-work-breakdown.md)
> **Produces:** raised `pyproject.toml` floors and a regenerated `requirements.lock`, only if the new set passes in both fresh-venv modes.
> **Feature Reference:** none (`NFR-1510` is an NFR without a Feature Specification; same shape as the earlier lock work)
> **Supersedes:** none
> **Related Topics:** [`pyproject.toml`](../../../pyproject.toml), [`requirements.lock`](../../../requirements.lock)

[Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID
IP-1093

## Title
Re-run check-latest / try / validate / pin and refresh the lock to the newer set that passed the release assessment.

## Objective
The assessment's fresh-venv run resolved five newer patch/minor versions - `hypothesis 6.170.9 -> 6.170.14`, `opentelemetry-api 1.45.1 -> 1.45.2`, `pydantic 2.14.1 -> 2.14.2`, `pydantic_core 2.50.1 -> 2.50.2`, `pytest 9.1.1 -> 9.2.0` - and the full suite passed (2161 passed, 4 skipped). Repeat the procedure at build time (the set may have moved again), and re-pin only if it passes.

## Requirements Covered
`NFR-1510` (primary); `NFR-1500` context.

## Architecture Components
Packaging metadata only. No source under `spacesim/`. Engine and determinism untouched: if a newer version needs an engine or determinism change, that package is held at its newest compatible version and reported, per the procedure.

## Interfaces
`pyproject.toml` `[project]`/optional-dependency floors (currently `pydantic>=2.14.1`, `pytest>=9.1.1`, `hypothesis>=6.170.9`); `requirements.lock` (33 exact pins, header comment kept, interpreter line updated if the build interpreter differs).

## Files to Create/Modify
Modify `pyproject.toml`, `requirements.lock`. A minimal non-engine compatibility fix in tests/tools only if needed, test-first. No other file.

## Implementation Tasks
1. Fresh venv A: `pip install -U -e ".[content,ui,dev]"`; record what moved (`pip freeze --exclude-editable` vs the lock). 2. Run the unfiltered suite in A: `-m "not browser"`, `-m browser`, the determinism gate; record counts and exit codes. 3. Fix or hold: compatibility fix only outside the engine; otherwise hold that package at its newest compatible version and report why. 4. Raise `pyproject.toml` floors to the validated direct versions (`pydantic`, `hypothesis`, `pytest`, and any other direct package that moved); `pip freeze --exclude-editable` into `requirements.lock`, keep its header. 5. Fresh venv B: `pip install -r requirements.lock && pip install --no-deps -e .`; re-run both suites; `pip freeze` of B must equal the lock. 6. Verify the install-from-lock tests (whatever tests read `requirements.lock`/`pyproject.toml`, e.g. the lock-consistency check under `NFR-1510`; locate by `grep -rn requirements.lock spacesim/tests`) pass. 7. Commit lock and floors together; if the new set does not pass in either mode, change nothing and report.

## Tests to Add
No new test is expected: the existing lock-consistency/install-from-lock checks are the gate. If none exists that asserts floors equal locked direct pins, add one first (`@pytest.mark.verifies("NFR-1510")`) and observe it fail before the pyproject edit. The deliverable evidence is the recorded real exit codes and counts from both fresh-venv runs (not a count-only claim).

## Documentation Updates
**Manual impact:** none - dependency metadata only; no label, route, message or procedure an operator sees (the install procedure in `docs/training/01-install-and-run.md` installs from the lock and does not name versions; the owner-directed check of that sentence is a read-only step in the verification checklist, any needed change handed to `08-training-manual-authoring`). Also update the Master Build Plan, INDEX, ROADMAP rows.

## Definition of Done
Either (re-pinned) floors raised and lock regenerated, both fresh-venv modes green with real exit codes recorded, lock install reproduces the frozen set; or (not re-pinned) a report stating which package failed and why. Full suite and both permanent gates green on the branch; documentation created/updated per Manual impact (none, reasoned), and §15.1/§15.2 rows in sync (no row affected).

## Verification Checklist
- [ ] `requirements.lock` pins equal the venv B freeze; header comment intact.
- [ ] `pyproject.toml` floors equal the locked direct pins.
- [ ] Both suites (`-m "not browser"`, `-m browser`) green in A and B; determinism and import-guard gates green.
- [ ] No `spacesim/engine/` diff.
- [ ] Documentation in sync: `docs/training/01-install-and-run.md` install text still correct, or hand-off recorded.

## Risks
A new release regresses between assessment and build (mitigated: the procedure re-runs); proxy-dependent installs (use the configured proxy and CA bundle, never disable TLS verification).

## Rollback Considerations
Revert the one commit; the previous lock was itself validated.
