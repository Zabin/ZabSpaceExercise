# Handoff: starting Release 2.0 in a new chat

Written 2026-11-01 after Release 1.0 shipped and the Release 2.0 plan was merged (PR #86). Read this, then act.

## State
- `main` carries Release 1.0 (manifest `docs/releases/release-1.0.md`, archive branch `archive/release-1.0` at 82436ba) plus the Release 2.0 plan.
- The `release-1.0` tag could not be pushed (git proxy blocked it). The owner may create it in GitHub on 82436ba.
- Many stacked Release 1 side branches and scratchpad worktrees are disposable; the owner has not asked for cleanup.
- Journal: `docs/pipeline/pipeline-journal.md` (runs through #268). Backlog: `docs/pipeline/backlog.md`.

## Read first, in order
1. `CLAUDE.md`
2. Position block of `docs/pipeline/pipeline-journal.md`
3. `docs/releases/release-1.0.md`
4. `docs/feature-planning/06-release-2-plan.md` and `06a-release-2-d3-d4-research.md`
5. `.claude/skills/README.md`

## Decisions made by the owner (all 14 recorded in the plan, section 6)
Theme: finish-and-trust. Naming `MAJOR.MINOR` (Release 2.0, tag `release-2.0`, bucket `R2.0`). Availability objectives score link availability (Must). SIGINT characterization uses the corrected ground-emitter path (Should). Role scoping stays optional; Creator derives `roles_needed`; crewed vignettes ship. Configurable size/runtime caps from measurement. No backward compatibility between releases (bump `save_format`, refuse old saves). Red `bus_state` at parity with Blue. Cells see telemetry up to their last downlink. Playback is White-only; cells export telemetry to analyse history. Symbology as close to real APP-6 / MIL-STD-2525 as possible (Must, research first). Retirement sweep of `build-spec/`, DOM files, `FUTURE-WORK.md` (important). Trunk-based, one short-lived branch per package, PR to `main`, squash-merge, no stacked branches. Trusted-LAN model unchanged; coalition play out of scope; Python floor raised to the validated version; FS-108 Could, FS-202 Later.

## First steps (milestone M0, no product code)
1. Run `00-intake` to file the plan's proposed intake rows (section 7).
2. Run `00-pipeline-manager` to triage and archive the closed backlog rows.
3. One `04` requirements pass, one `05` feature-decomposition delta, early dependency check (check latest versions, then pin).
Then M1 trust and integrity, M2 console and Creator, M3 scoring/content/saves, release and archive.

## Process rules
- Every package states "Manual impact:"; `09` verifies documentation; `09-training-manual-review` walkthrough is a per-release gate.
- Archive the release (tag plus manifest) before new changes; GO/NO-GO is the owner's.
- Verification and review run in fresh sessions. Run one or two heavy agents at a time; agents commit and push early.
- Watch the 5-hour session limit; use `send_later` check-ins. GitHub access is via MCP only.
- Never hand-edit the RTM Test column; regenerate with `python3 -m pytest --origin-report=rtm`.

## Open items
Post-release intake candidates: Pause/Resume resets the clock rate; Creator role matrix not saved; t1/t2 swap caught only in the header; observer seat set by body in one route and by query in another; mt-sigint `characterize_emitter` unreachable; save-as-scenario omissions; about 11 test retags; 4 always-skipped tests; Starlette `httpx` deprecation.

## Owner cleanup (the cloud session's git proxy blocks branch deletes and tag pushes)
Run these from a machine with normal GitHub access.
1. Tag the release: `git tag -a release-1.0 82436ba -m "Release 1.0" && git push origin release-1.0` (or create it in the GitHub UI on 82436ba).
2. Delete the merged remote branches (every `claude/*` branch except the two below; their commits are in `main`, or were squash-merged by PRs #86/#87):
   ```bash
   git fetch --prune origin
   git branch -r | sed 's#^ *origin/##' | grep '^claude/' \
     | grep -v -E '^claude/(pipeline-skill-h31gs5|planning-docs-review-rmZwP)$' \
     | xargs -n 20 git push origin --delete
   ```
   Keep `main` and `archive/release-1.0`. Review the two excluded branches (old June/July work with commits never merged to `main`) and delete them too if that work is not wanted.
3. In GitHub Settings, enable "Automatically delete head branches" so PR branches vanish on merge (matches the D11 branching rules).

## First message for the new chat
"Read CLAUDE.md, the journal Position block, docs/pipeline/handoff-release-2.md, docs/releases/release-1.0.md and the Release 2.0 plan. Then run 00-intake for the plan's section 7 rows and continue M0."
