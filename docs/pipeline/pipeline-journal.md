# Pipeline Journal

> **Where the pipeline stands.** Written only by `00-pipeline-manager`. It is a cache, not the
> truth: the tree's ledgers win, and each run reconciles this file against them.
>
> **Keep rows short.** One row per run, the Outcome at most about 260 characters. The detail is in
> what the run produced (a report, a package, a commit); name it. Rows older than the last fifteen
> or so move verbatim to [`pipeline-journal-archive.md`](pipeline-journal-archive.md), which holds
> runs #0 to #269 in full.

[↑ Docs index](../INDEX.md) · [Backlog](backlog.md) · [Refactor plan](refactor-plan.md) ·
[Pipeline README](../../.claude/skills/README.md) · [Master Build Plan](../implementation/00-master-build-plan.md) · [ROADMAP](../../ROADMAP.md)

## Position

- **Updated:** 2026-11-10 (run #272)
- **Increment:** two tracks. **Repository refactor** (owner-ordered; [`refactor-plan.md`](refactor-plan.md)): steps 1 to 3 done, step 4 (documentation retirement sweep) next. **Release 2.0** (theme: finish-and-trust; `docs/feature-planning/06-release-2-plan.md`), milestone M0, paused behind the refactor's documentation steps.
- **Pipeline state:** all 94 packages `VERIFIED`; Release 1.0 shipped and archived (tag `release-1.0`). No Release 2.0 package exists yet. CI runs the full suite and a dependency audit on every pull request.
- **Backlog:** 111 open rows, all short. 14 came from the two November reviews (`BL-0431`–`BL-0444`), among them 6 Medium product and security defects: 4 scheduled to Release 2.0 M1, 1 to the M0 `04` pass, 1 to M3. No `NEEDS-USER` row is ripe.
- **Next step:** refactor step 4. After the refactor's documentation steps: `04-requirements-engineering`, one Release 2.0 pass covering `BL-0410` (link availability, High), `BL-0407`, `BL-0426`, `BL-0428`, `BL-0421` and `BL-0432` (bus-tick horizon).
- **Open gates:** none. The first Release 2.0 package needs MSTR-006 §3 authorization. Two old branches with unmerged work (`claude/pipeline-skill-h31gs5`, `claude/planning-docs-review-rmZwP`) are the owner's to keep or drop.

## Run log

| # | Date | Mode | Skill | Target | Outcome | Next |
|---|---|---|---|---|---|---|
| 265 | 2026-11-01 | advance (release push, resumed twice … | `08`/`09`/`10`/`07`/`06`/`04` (fresh … | final release candidate | Built and independently verified IP-1089 (FR-7450 ISO bounds), IP-1092 (NFR-3810 retired-docs check), IP-1093 (lock re-pin), IP-1094 (save_format gate + Chromium lookup) after RETURNED rounds; merged to `claude/release-candidate-6` (94 `VERIFIED`) | final `11-release-readiness` on `opus` (recommendation only; GO/NO-GO and the merge route to `main` are the owner's) |
| 266 | 2026-11-01 | advance (release push) | `11` (opus), `09`, `08` (fresh agents) | final candidate | Third `opus` release assessment (REV-REL-004, `docs/reviews/release-assessment-release-candidate-10.md`): NO-GO only on the letter of the documentation gate; no code/test/dependency/verification/integration blocker; 94/94 packages `VERIFIED` | short fresh `opus` `11` confirmation (docs/tutorial-only diff since cfcf47f; recount |
| 267 | 2026-11-01 | advance — release GO | `11` (opus confirmation), `11` (flip) | Release 1 | Final `opus` confirmation (REV-REL-004 addendum, `cd1cc63`): GO recommended — 8 docs-only files since `cfcf47f`; 94/94 `VERIFIED`; unfiltered 2244 / 4 skipped, non-browser 2202 / 5, browser 42 / 0; NFR-1510 met, NFR-2830 met; C-1/C-2/F-1 closed | merge `claude/release-flip` into `main` with a merge commit (owner choice); close PRs #81–#83 as included |
| 268 | 2026-11-01 | owner-requested process change + archive | `11` (opus, skill edit) | Release 1.0 archive | Owner asked that releases be archived as they are released, before further changes; chose tag + release manifest. Release 1.0 = `main` at `82436ba` (PR #84 merge). Archive ref `archive/release-1.0` pushed at `82436ba` | post-release intake backlog; next release cycle may start |
| 269 | 2026-11-03 | triage (owner: M0 intake and triage, no … | — | `BL-0394`–`BL-0430` (plan §7); archive | Reconciled: `main` = `ae7a5f1`; no drift. Release-archive gate: Release 1.0 archive recorded in run #268, so Release 2.0 work may start. Owner cleanup attempted: `git push origin release-1.0` and `gh api` ref creation both refused (HTTP 403, proxy) | `04-requirements-engineering` Release 2.0 pass; parallel `02-research-*` symbology. |
| 270 | 2026-11-09 | override (owner: review Release 1) | `10-integration-review` | Release 1.0, all 94 packages at `82436ba` | `integration-review-release-1.0-whole-release.md`: 0 Critical, 0 High, 5 Medium, 5 Low, all new. Suite 2240 passed / 4 skipped on the lock; 19 of 19 vignettes save, reload and replay identically. | Harvest; M-2 rides the M0 `04` pass. |
| 271 | 2026-11-09 | owner request, no skill | — | pipeline, development, documentation, malicious code | `process-and-security-review-2026-11.md`: no malicious code; 1 Medium and 4 Low vulnerabilities; 3 High process findings. Owner accepted all five refactor recommendations. | The refactor. |
| 272 | 2026-11-10 | owner-authorized maintenance (refactor steps 1 to 3) | — | CI, branches, `CLAUDE.md`, records | CI and branch-cleanup workflows; 120 stale branches removed; `release-1.0` tag created; `CLAUDE.md` 687 to 150 lines; backlog and journal compacted with the full text kept in the archives; 14 review findings harvested (`BL-0431`–`BL-0444`); 7 resolved rows closed. PRs #94, #95 and this one. | Refactor step 4. |
| 273 | 2026-11-10 | owner-authorized maintenance (refactor 4a, 4b, plan pause, B2) | — | retired documents; refactor plan | PRs #97, #98: `docs/implementations/`, the documentation plan and the root decision log retired; June audits moved to `docs/reviews/`; refactor paused with tiered packets. B2: the future-work list retired, 6 open items filed (`BL-0445`–`BL-0450`), `BL-0296`/`BL-0306` closed. | Owner assigns the next packet. |
| 274 | 2026-11-12 | owner-authorized maintenance (refactor A1) | — | refactor plan §8 | Successor map for build-spec and design: 45 cited sections (33 confirmed, 11 partial, 1 none; 1 migrate-first: glossary). ICD moves to `docs/architecture/`; phase plan retires unmigrated. 28 mis-numbered GDS-04 citations found. | B1, when the owner assigns it. |
| 275 | 2026-11-12 | owner-authorized maintenance (refactor A4) | — | behaviour baseline test; refactor plan §2, §3 | `test_behaviour_baseline.py` pins a scripted two-hour run of all 19 vignettes, with save, reload and replay equality, wall time kept out. Stable across runs, hash seeds and SIMD settings. Re-bless rule added. No production code changed. | Owner assigns the next packet. |
