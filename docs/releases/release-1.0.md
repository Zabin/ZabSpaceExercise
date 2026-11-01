[↑ Releases](INDEX.md) · [Docs index](../INDEX.md) · [Release assessment REV-REL-004](../reviews/release-assessment-release-candidate-10.md)

# Release Manifest — Release 1.0

> **Owner:** `11-release-readiness` (Release archive step). **Written:** 2026-11-01, from the repository at
> `82436ba` (`git show 82436ba:<path>`, `sha256sum`); nothing here is taken from memory.

## 1. Identity

| Item | Value |
|---|---|
| Release | **1.0** (Release 1; the Prototype, MVP, Release 1 and Release 2 buckets released together) |
| Date | **2026-11-01** (owner GO and baseline date) |
| Release commit | **`82436ba2e592d9a9afb91d4f93f8df8fffe07e00`** on `main` — "Release 1: remediation, verification, training corpus and release records (#84)", the merge of PR #84 (parents `79641c7`, `7335362`) |
| Evidence commit | `935fd44` (`claude/release-candidate-12`); `82436ba` descends from it by documentation and record changes only (assessment condition 1) |
| Archive branch ref | **`archive/release-1.0`** → `82436ba` (pushed to `origin`) |
| Archive tag | **tag: pending (push blocked by the environment; create `release-1.0` on `82436ba` in GitHub if desired).** An annotated tag `release-1.0` exists locally in the main checkout only. |

## 2. Assessment and reviews relied on

- **Release Assessment (the GO record):** [REV-REL-004](../reviews/release-assessment-release-candidate-10.md)
  and its final-confirmation addendum (A.1–A.9; owner decision A.8a).
- Earlier assessments: [REV-REL-003](../reviews/release-assessment-release-candidate-5.md) (release candidate 5),
  [REV-REL-002](../reviews/release-assessment-release-candidate-1.md) (release candidate 1),
  [REV-REL-001](../reviews/release-assessment-fs-tracked-baseline.md) (FS-tracked baseline).
- **Integration reviews** (union covers 94 of 94 packages, REV-REL-004 §2.3):
  [18-package tranche](../reviews/integration-review-18-package-tranche.md),
  [Tranche 2](../reviews/integration-review-tranche-2-white-controls-saves-test-origins.md),
  [Tranche 3](../reviews/integration-review-tranche-3-release-push-remediation.md),
  [Release candidate 1](../reviews/integration-review-release-candidate-1.md),
  [Unreviewed packages](../reviews/integration-review-unreviewed-packages.md),
  [RC-3 delta](../reviews/integration-review-rc3-delta.md),
  [RC-7 delta](../reviews/integration-review-rc7.md).
- **Learner-walkthrough (training) reviews:** [REV-TRN-013](../reviews/training-review-final-rc11.md) (the
  current gate report; 0 High, its 1 Medium and 2 Low fixed in `4ce7fb2` and checked in REV-REL-004 A.3),
  preceded by [REV-TRN-012](../reviews/training-review-final-rc8.md),
  [REV-TRN-011](../reviews/training-review-release-walkthrough-recheck.md) and
  [REV-TRN-010](../reviews/training-review-release-walkthrough.md).

## 3. Counts (REV-REL-004 A.2 / A.4)

| Item | Value |
|---|---|
| Packages | **94 / 94 `VERIFIED`**, 94 VRs |
| Unfiltered `python3 -m pytest` | **2244** tests, **0 failed**, **4 skipped**, exit 0 |
| `-m "not browser"` | **2202** passed, **5 skipped**, exit 0 |
| `-m browser` | **42** passed, **0 skipped**, exit 0 |
| Allow-lists | `test_origin_allowlist` 0; `doc_integrity_allow_indexes` 0, `_ledgers` 0, `_retired` 0, `_links` 38 |

## 4. Dependency lock (NFR-1510)

- File: [`requirements.lock`](../../requirements.lock) at `82436ba`, **sha256
  `7e8d0e076e5482ab3157ecddb257dc293f2dfd967a885c45318b985e885953b6`**, 33 exact pins.
- Interpreter validated: **CPython 3.13.17** (lock header; both suite modes green on the pinned set).
  `pyproject.toml` declares `requires-python = ">=3.11"`.
- Key pins: `pydantic==2.14.2`, `numpy==2.5.4`, `sgp4==2.27`, `skyfield==1.55`, `PyYAML==6.0.3`,
  `fastapi==0.162.0`, `starlette==1.10.0`, `uvicorn==0.54.0`, `httpx==0.28.1`, `pytest==9.2.0`,
  `hypothesis==6.170.14`, `playwright==1.64.1`.
- Latest-version check at assessment: identical to the lock; `pyee` 16.0.1 later appeared but is held at the
  locked version by `playwright` 1.64.1 (`pyee<15`), test-only (REV-REL-004 A.5).

## 5. Known deviations that ship (owner-accepted; REV-REL-004 A.7 / A.8a)

1. `FR-3520`: the role gate is checked at submission, and omitting `seat` skips it (`BL-0388`; `FR-3520` amended).
2. Role scoping (`FEAT-3500`) ships **opt-in and dormant**: no shipped vignette declares `roles_needed`, and the
   Creator saves `roles_needed: []` (`BL-0390`); closes O-2.
3. The `FR-5310` template-reference clause was dropped (`BL-0233`, `ADR-0036`).
4. Save-as-scenario omits gating rules, detectability config, the space-weather series and the inject schedule
   (`BL-0389`; v1.1).
5. Gate approve/deny, live ROE change, manoeuvre ledger, undo and clock rate are **HTTP only**, with no console
   control (`BL-0389`).
6. Pause/Resume resets a custom clock rate; the Creator role matrix is not saved; `mt-sigint-geolocate`
   `characterize_emitter` cannot be reached by orders; the Blue availability objectives score the satellite's
   health, not link availability.
7. The hot-seat hand-off is not automatic (`FR-6610`, `BL-0015`).
8. AI-Red reads ground truth (`ADR-0024`).
9. The `NFR-3810` retired-document check has nothing to check on the real tree (`BL-0393` deferred).
10. The LAN trust model: cell seats are client-asserted, with no authentication; trusted LAN only (§9 below).

## 6. Branches merged into the release (names only)

PR #84 head: `claude/release-flip`. Work branches merged into the release-candidate line between `79641c7` and
`7335362`: `claude/dependency-refresh-1`, `claude/fs121-status`, `claude/ip-1073-build`, `claude/ip-1075-build`,
`claude/ip-1079-build`, `claude/ip-1080-build`, `claude/ip-1082-build`, `claude/ip-1083-build`,
`claude/ip-1085-build`, `ip-1093-build`, `claude/ip-1335-build`, `claude/plan-remediation-1`,
`claude/release-assessment-1`, `claude/req-maintenance-pass-3`, `claude/req-maintenance-pass-5`,
`claude/skills-docs-steps`, `claude/skills-every-release`, `claude/stale-docs-claude`,
`claude/stale-docs-features`, `claude/stale-docs-gds`, `claude/stale-docs-training`, `claude/training-fix-1`,
`training-fix-rc4-docs`, `training-fix-rc4-yaml`, `claude/training-review-rc11`, `claude/tutorial-fix-1`,
`claude/vignette-fix-2`. Integration lines they were merged into: `claude/work-base-2`, `work-base-3`,
`test-tag-review-1` and the `release-candidate-*` lines (last: `claude/release-candidate-12`).

## 7. Owner decisions recorded for this release

- **GO, 2026-11-01**, on the REV-REL-004 final-confirmation addendum; baseline flipped on `claude/release-flip`
  (REV-REL-004 A.8a; journal run #267).
- The ten deviations in §5 accepted as the release baseline (journal run #266), including O-2 (role scoping
  dormant, `BL-0390`).
- GO conditions: release from `935fd44` or a documentation-only descendant; publish the §5 list; deploy on a
  trusted LAN only (REV-REL-004 A.9).
- Standing release rules applied: test-relevance audit and dependency lock at every release (`BL-0318`,
  `BL-0310`, `BL-0299`); documentation verified as a release gate (2026-10-25); one owner per document
  (`BL-0293`).
- **Archive releases as they are released, by tag + release manifest** (2026-11-01) — this document.

## 8. How to run

```bash
git checkout archive/release-1.0
pip install -r requirements.lock && pip install --no-deps -e .
python3 -m spacesim.ui_web        # 127.0.0.1:8000 by default
```

Full instructions: the [README](../../README.md) "Quick start" at the release commit.

## 9. Trust model

The Blue / Red / White / Observer seat is **client-asserted**; there is **no authentication**. Fog-of-war is
enforced server-side at `SessionAPI` / `CellController`, but the no-cell ground-truth endpoints (`FR-6220`)
expose ground truth by design, and White-only and Observer rejections act on the seat the request asserts.
**Deploy only on loopback or an isolated, trusted LAN with cooperative participants; never expose the port to
the internet** (README "Security and the LAN trust model"; REV-REL-004 §6).
