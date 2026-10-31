# IP-1094 — Release Polish: Unknown Save Format Refused, Chromium Discovery in the Run Tools

> **Package ID:** IP-1094
> **Version:** 1.0
> **Status:** COMPLETE (built 2026-10-31 by `08-code-implementation`; authored by `07-implementation-planning`; every dependency `VERIFIED`)
> **Authorization (MSTR-006 §3):** **given.** The project owner's go-ahead of 2026-10-31, in the planning session that commissioned this package ("the small release polish items"), covers this package and no other. The owner also approved editing the `run-spacesim` skill files for this seat/path class only; edits stay minimal.
> **Dependencies:** [IP-1101](IP-1101-self-contained-saves.md), [IP-1102](IP-1102-save-load-robustness.md), [IP-1103](IP-1103-save-validation-completion.md), [IP-1340](IP-1340-browser-console-rule-suite.md) (all `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [01-technical-work-breakdown.md](../01-technical-work-breakdown.md)
> **Produces:** a `validate_save` format gate and a Chromium lookup that works on this container's layout in the two run tools.
> **Feature Reference:** [FS-110 Save and Resume](../../features/FS-110-save-and-resume.md) (`FR-7230`); tooling (`NFR-2840` for the browser-lookup precedent)
> **Supersedes:** none
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`tools/record_walkthrough.py`](../../../tools/record_walkthrough.py), [`.claude/skills/run-spacesim/driver.py`](../../../.claude/skills/run-spacesim/driver.py), [release assessment rc5](../../reviews/release-assessment-release-candidate-5.md) `S-1`, `N3`

[Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID
IP-1094

## Title
Refuse unknown or future `save_format` values; make the Chromium path discoverable in `tools/record_walkthrough.py` and the `run-spacesim` driver.

## Objective
(1) `validate_save` tests only `bool(state.get("save_format"))` (`manager.py:1303`, `from_state` ~1385), so `save_format: 999` is silently treated as a v2 save. Refuse any `save_format` that is present and not a supported value with a 400 on `load_save` naming the supported formats; legacy saves (key absent) and format 2 behave exactly as today. (2) `tools/record_walkthrough.py:80` hard-codes `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, and `driver.py:33` globs `chrome-linux/chrome` only, which misses the real `chrome-linux64/` build ("No Chromium found", rc5 `N3`). Use `PLAYWRIGHT_BROWSERS_PATH` (default `/opt/pw-browsers`) and the newest `chromium-*/chrome-linux*/chrome`, as `test_browser_console_rules.resolve_browser` does.

## Requirements Covered
`FR-7230` (a save that cannot be loaded safely is refused before replay), `NFR-1600` (robust load); `NFR-2840` (browser lookup precedent). Note: no requirement leaf states the format-gate itself; rc5 `S-1` routed "is a format check required?" to `04`. The owner's go-ahead for this package is the decision to build; the leaf is `04`'s to add, and the tests tag `FR-7230`.

## Architecture Components
Session layer (`SessionManager.validate_save`, `SAVE_FORMAT` constant, ~line 193); route layer unchanged (the `load_save` route already maps `ValueError` to 400, ~`server.py:1256`); developer tooling. No `engine/` change.

## Interfaces
`validate_save(state)` raises `ValueError("save_format <v> is not supported; supported formats: legacy (absent), 2")` for a present value that is not `2` (including `0`, negatives, `999`, strings, booleans, floats, `None` where the key is present). A module-level tuple of supported formats beside `SAVE_FORMAT` is the single source. Tools: a small `find_chromium()` in each of the two scripts (no shared import across the skill/tools boundary; ~6 lines each) honoring `PLAYWRIGHT_BROWSERS_PATH`, exiting with a message naming the searched root when none exists.

## Files to Create/Modify
Modify `spacesim/session/manager.py` (`validate_save` ~1295, constant ~193); `tools/record_walkthrough.py` (~80); `.claude/skills/run-spacesim/driver.py` (~33, ~53) and the matching two lines in `.claude/skills/run-spacesim/SKILL.md` (~30, ~104, ~135) - minimal, owner-approved. Create `spacesim/tests/test_save_format_gate.py` and `spacesim/tests/test_run_tool_browser_lookup.py`.

## Implementation Tasks
1. Tests first. 2. Add the supported-formats constant and the gate at the top of `validate_save` (after the dict check, before required keys, so the message is the format message). 3. Fix both browser lookups. 4. Also fix the stale probe `document.getElementById('o-target-pick')` in `driver.py:111` (the live id is `o-target`; verified in `index.html`) - rc5 `N3`'s second half; one token.

**Other rc5 Low findings, my choices.** Taken: `N3` (both halves), `S-1`. Not taken, with reason: `N7` Starlette `httpx` deprecation warning (needs a `filterwarnings` entry in `pyproject.toml`, which `IP-1093` also edits - ordering hazard for a cosmetic gain; leave for the owner); `R-2` four always-skipping tests (needs a decision about the data they depend on, not trivially safe); `N4` README refresh and `S-2`/`BL-0271` (excluded, manual-impact doc items for the training author); `N6` release-plan body and `V-1` `VR-1088` header (documents owned by other stages).

## Tests to Add
`test_save_format_gate.py`, `@pytest.mark.verifies("FR-7230")`: save with `save_format` 999, 3, 0, -1, `"2"`, `True`, `2.0`, `None` each refused by `validate_save` and by the `load_save` route with 400 whose detail names the supported formats and the offending value, session registry untouched; a real format-2 save round-trips; a legacy save (no key) loads unchanged; `from_state` still refuses before replay. `test_run_tool_browser_lookup.py`, `@pytest.mark.verifies("IP-1094")`: load the two scripts' finder by file path (no Playwright import at module import; if import needs it, guard) against a synthetic tmp root containing `chromium-1194/chrome-linux64/chrome` and `chromium-1200/chrome-linux/chrome`: newest build chosen, `PLAYWRIGHT_BROWSERS_PATH` honored, empty root gives the named-root message and no hard-coded `chromium-1194` remains (grep assertion). Fail-first: all new cases observed failing before the edit. Existing `test_save_load_robustness.py`, `test_self_contained_save.py` unmodified and green.

## Documentation Updates
**Manual impact:** *update (small)*: `docs/training/08-http-api-reference.md` load-save row (new 400 refusal for an unknown `save_format`) and the `12`-series save/resume troubleshooting entry (a save from a newer simulator version is refused with the supported-formats message) and §15.1 "Save and resume" row Sources; writer `08-training-manual-authoring` (hand-off recorded; nothing written by `08-code-implementation` except route/function docstrings). Skill/tool docs: `run-spacesim/SKILL.md` lines naming the glob are edited by this package (owner-approved). Also ledger rows. README and `BL-0271` are not in this package.

## Definition of Done
Tests green and observed failing first; full suite and both permanent gates green; the two tools find Chromium on this container (`chrome-linux64`) when run, evidence recorded; documentation created/updated per Manual impact, and §15.1/§15.2 rows in sync with the shipped change (or each hand-off recorded as a Manual-impact item).

## Verification Checklist
- [ ] `save_format: 999` through `POST .../load_save` returns 400 naming supported formats; format 2 and legacy unchanged (tests).
- [ ] No `chromium-1194` literal remains in `tools/` or `.claude/skills/run-spacesim/`.
- [ ] `driver.py` `o-target-pick` replaced by the live id.
- [ ] Only the named skill-file lines changed (diff).
- [ ] `test_determinism.py`, `test_import_guard.py` green; no `engine/` diff.
- [ ] Documentation in sync: Manual-impact hand-offs recorded.

## Risks
A future format legitimately added later must extend the constant (single source, documented). A stored save with a stray format value would now be refused - intended. Ordering: touches `session/manager.py`; `IP-1089` also touches `manager.py` (`telemetry_export`, a different region) - sequence them, do not run in parallel branches without a rebase.

## Rollback Considerations
Revert the commit; the gate and the two lookup edits are independent hunks.
