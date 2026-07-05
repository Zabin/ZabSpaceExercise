[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Master Build Plan](../implementation/00-master-build-plan.md) · [Release plan](../feature-planning/01-release-plan.md)

# Release Assessment — FS-Tracked Implementation Baseline (MVP → Release 2 scope)

> **Document ID:** REV-REL-001
> **Skill:** `11-release-readiness`
> **Scope:** every package on the Master Build Plan (18 packages, `IP-1010`…`IP-3010`, covering
> `FS-101`–`FS-111`, `FS-112`–`FS-115`, `FS-201`, `FS-301` — every `✅ Done` Feature Specification;
> `FS-108`/`FS-202` excluded per `MSTR-006` §3, not authorized). Per `docs/feature-planning/`'s own
> reading note, these Features are drawn from the **MVP, Release 1, and Release 2** buckets (the
> **Prototype** bucket's two Features, `FEAT-1100` Deterministic Clock and `FEAT-1200` Orbital
> Propagation, plus MVP's `FEAT-1300`/`5100`/`5300`/`6100`/`8100`, are pre-FS-pipeline engine/UI
> substrate with no dedicated Feature Specification or Implementation Package — see "Out-of-IP-scope
> foundational work" below).
> **Commit assessed:** `473072f17861cff0edc748f1a1dd810926697cf2` (branch `claude/pipeline-skill-4qifau`,
> one commit ahead of `origin/main` tip `8574ca9` at assessment time — that commit is this pipeline's
> own journal/backlog bookkeeping, not production code)
> **Authorization to run this assessment:** the project owner explicitly authorized invoking
> `11-release-readiness` now (the standing pipeline-manager gate recorded since run #17).
> **Upstream:** `10-integration-review` ([`integration-review-18-package-tranche.md`](integration-review-18-package-tranche.md),
> clean, no Critical/High), `09-package-verification` (18/18 `VR-xxxx` reports), `09-training-manual-review`
> ([`training-review-runs16-19-scope.md`](training-review-runs16-19-scope.md), clean apart from 1 Medium)
> **Downstream:** the next increment's planning, if GO

## 1. Scope audit — one row per FS-tracked Feature

| FS | Feature(s) (`FEAT-xxxx`) | Bucket | IP(s) | VR(s) | Integration coverage | Delivered? |
|---|---|---|---|---|---|---|
| FS-101 Mission Planning | FEAT-3100 | Release 1 | IP-1010 | VR-1010 (clean) | ✅ (18-pkg review) | ✅ Yes |
| FS-102 Command Scheduling | FEAT-3300, FEAT-3400 | Release 1 | IP-1020 | VR-1020 (1 Medium, `BL-0036`) | ✅ | ⚠️ Partial — see Finding 1 |
| FS-103 Custody Management | FEAT-1500 | MVP | IP-1030 | VR-1030 (clean) | ✅ | ✅ Yes |
| FS-104 SDA Tasking | FEAT-3200 | Release 1 | IP-1040 | VR-1040 (clean) | ✅ | ✅ Yes |
| FS-105 Spacecraft Operations | FEAT-2100–2500, FEAT-1400 | Release 1 + MVP | IP-1050, IP-1051 | VR-1050 (1 Low), VR-1051 (1 Low) | ✅ | ✅ Yes |
| FS-106 White Cell Dashboard v2.0 | FEAT-4300, 4600, 4700 (Rel. 1), FEAT-4400 (Rel. 2) | Release 1 + Release 2 | IP-1060 | VR-1060 (1 Low) | ✅ | ✅ Yes |
| FS-107 After Action Review | FEAT-7300 | Release 1 | IP-1070 | VR-1070 (1 Low) | ✅ | ✅ Yes |
| FS-109 Multiplayer/LAN Session Transport | FEAT-6300, 6400 | Release 1 | IP-1090 | VR-1090 (1 Low) | ✅ | ✅ Yes |
| FS-110 Save & Resume | FEAT-7200 | Release 1 | IP-1100 | VR-1100 (1 Medium `BL-0045`, 2 Low) | ✅ | ✅ Yes (Medium finding is a doc-overclaim, not a functional gap) |
| FS-111 AI-Red Doctrine Automation | FEAT-9100 | Release 2 | IP-1110 | VR-1110 (zero findings) | ✅ | ✅ Yes |
| FS-112 Classification Banner | FEAT-4500 | Release 2 | IP-1120 | VR-1120 (1 Low) | ✅ | ✅ Yes |
| FS-113 Observer Read-Only Access | FEAT-6500 | Release 2 | IP-1130 | VR-1130 (1 Low) | ✅ | ✅ Yes |
| FS-114 Hot-Seat Hand-Off | FEAT-6600 | Release 2 | IP-1140 | VR-1140 (1 High, **accepted risk** `BL-0015`) | ✅ | ⚠️ Yes, with an explicitly user-accepted residual risk |
| FS-115 Session Setup (Vignette Selection + Seat-to-Role) | FEAT-4100, 4200 | Release 1 | IP-1150, IP-1151 | VR-1150 (1 Low), VR-1151 (1 Low) | ✅ | ✅ Yes |
| FS-201 Competency Assessment | FEAT-10100 | Release 2 | IP-2010 | VR-2010 (2 Medium re: FS-201's own scope) | ✅ | ⚠️ Yes, with 2 disclosed scope gaps against FS-201's own Acceptance Criteria (`BL-0019`/`BL-0020`) |
| FS-301 Research Analytics | FEAT-10200 | Release 2 | IP-3010 | VR-3010 (clean) | ✅ | ✅ Yes |
| *(no FS)* | **FEAT-3500** Role-Scoped Command Catalog & Assignment Scoping | Release 1 | *(none)* | *(none)* | *(none)* | ❌ **Not delivered — see Finding 2** |

**Out-of-IP-scope foundational work (Prototype + part of MVP bucket):** `FEAT-1100` (Deterministic
Clock), `FEAT-1200` (Orbital Propagation), `FEAT-1300` (Δv Accounting — exercised inside
`FS-105`/`IP-1050`'s own test coverage per `VR-1010`'s `FR-1310` citation), `FEAT-5100`/`FEAT-5300`
(Vignette Builder/Validation — `content/vignette.py`), `FEAT-6100` (SessionAPI Seam — `session/api.py`),
`FEAT-8100` (Browser Console — `ui_web/static/`). These predate the FS/IP/VR documentation apparatus
entirely (built in Phases P0–P5 before this pipeline existed) and have no dedicated Feature
Specification or Implementation Package to audit against. They are continuously re-verified by the
**permanent gates** (`test_determinism.py`, `test_import_guard.py`, both green every run in this
sweep) and by the full test suite, not by a per-package VR — this is a different verification
instrument for the same shipped code, not a gap.

## 2. Evidence

- **Test suite:** `python3 -m pytest` → **566 passed, 3 skipped**, unchanged from every VR/integration-review
  pass in this tranche's history — no regression at the commit assessed.
- **Permanent gates:** `test_determinism.py` + `test_import_guard.py` → **14 passed**, both green.
- **Verification Reports:** all 18 packages carry a formal `VR-xxxx` (`docs/implementation/verification/INDEX.md`);
  11 retro-verified in the `BL-0004` sweep (runs #18, #20–#29), 7 verified at first-implementation
  time (runs #3, #9, #11–#15). No Critical/High finding in any VR.
- **Integration Report:** [`integration-review-18-package-tranche.md`](integration-review-18-package-tranche.md)
  (run #17) — all 5 dimensions exercised, no Critical/High, 1 Medium (training coverage, since
  closed — see below) + 2 Low (package-doc/feature-index staleness, still open, `BL-0030`/`BL-0031`).
- **Training corpus:** [`training-review-runs16-19-scope.md`](training-review-runs16-19-scope.md)
  (this pipeline cycle) — accuracy/coverage/pedagogy clean, playbook suite 16/16 green, 1 Medium
  traceability finding (`BL-0048`, a wrong filename citation, doc-only).

## 3. Deviations

| Deviation | Authorization trail |
|---|---|
| `IP-1140` (Hot-Seat Hand-Off) ships with a manual-button/auto-cycle trigger, not the automatic seat-relinquish detection `FR-6610`'s full intent implies — a real, unmitigated fog-of-war-leak risk in the one Feature enforced client-side rather than server-side. | **Authorized as an accepted risk.** `VR-1140` adjudicated the gap (High, `BL-0015`); the project owner explicitly chose to accept it over authorizing remediation ("I accept the risk of a cell not blanking the screen during handover as long as hot seat is an option," recorded in `IP-1140`'s own header and Master Build Plan Risk item 6). Re-confirmed unchanged by `10-integration-review` (run #17). |
| `FS-201`'s own Acceptance Criteria promise a longitudinal per-trainee report and self-assessment-mode accessibility for Blue/Red; `IP-2010` delivers neither. | **Partially authorized.** The longitudinal-report gap was disclosed by `IP-2010`'s own Implementation Tasks at authoring time (deliberate, known deferral — needs a trainee-identity model that doesn't exist). The self-assessment-mode gap was **not** flagged anywhere in `IP-2010`'s own text — `VR-2010` found it unannounced (`BL-0020`, Medium, still `DEFERRED`, routed to `06-feature-specification`, no authorization on record for descoping it). |
| **`FEAT-3500` (Role-Scoped Command Catalog & Assignment Scoping) — bucketed Must-priority in Release 1 — has no owning Feature Specification and no implementation anywhere in the codebase.** | **Unauthorized drift — see Finding 2.** No FS was ever authored for it (absent from the FS↔FEAT reconciliation table in `05-feature-review.md`); the release plan's own text calls its RTM `UNASSIGNED` cells "a Release-1-scoped verification task, not new development," but the verification task (independently run twice — `08-code-implementation` run #8, `09-package-verification` run #15) confirmed the opposite: **no role-based command-filtering/enforcement exists anywhere in the codebase.** This was filed as `BL-0014` (Medium, `DEFERRED`) — correctly identified in substance, but never escalated to the release-readiness-blocking severity a wholly-undelivered Must-priority Feature warrants. |

## 4. Residual risks (accepted or open, shipping with this baseline if GO)

1. `IP-1140`'s fog-of-war-leak risk during hot-seat handoff (High, **accepted**, above).
2. `IP-1020`'s Objective/DoD text uses invented lifecycle vocabulary (`executing`/`executed-unconfirmed`/`confirmed`) that doesn't exist in the code; the actual 3-status-plus-derived-label mechanism delivers the same functional guarantee (Medium, `BL-0036`, doc-only).
3. `IP-1100`'s Requirements Covered table falsely claims Role Assignments persist across save/resume (Medium, `BL-0045`, doc-only — nothing functionally relies on this).
4. `FS-201`'s undisclosed self-assessment-mode gap (Medium, `BL-0020`, open, routed to `06`).
5. The LAN trust model (client-side cell selection, ground-truth endpoints with no per-cell auth) — a documented, accepted v1 design boundary (`ADR-0015`), not new to this assessment.
6. `training/15`'s wrong `session/controller.py` citation (Medium, `BL-0048`, doc-only, this pipeline cycle's own finding).
7. Two Low package-doc/feature-index staleness items from the integration review (`BL-0030`/`BL-0031`, cosmetic).
8. **New this assessment — Finding 1:** `FR-3310`'s "single scheduler for commands and collection
   tasks" is not literally implemented as one shared mechanism — `OrderSystem`/`Scheduler` (commands)
   and `SSNNetwork` (collection requests) are two separate, independently-deterministic subsystems.
   No `PlannedActivity` class or unified scheduler abstraction exists anywhere in `spacesim/engine/`
   (confirmed by direct grep this session). `FS-102-command-scheduling.md` itself explicitly
   disclaims citing any FR ("None identified... this is a traceability gap"), so no Feature
   Specification anywhere claims to implement `FR-3310`. The *behavioral* guarantee the FR cares
   about (undo/rewind applies identically to both kinds) is very likely satisfied in practice —
   `VR-1020` and `VR-1040` each independently confirmed their own mechanism is deterministic and
   replay-safe — but this was never verified *as the same claim* across both kinds together, and the
   requirement's literal "single mechanism" framing does not match the shipped architecture.
   **Severity: Medium** (behavioral risk low, documentation/traceability risk real — no FS owns this
   FR at all). Recommended owner: `06-feature-specification` (assign `FR-3310` to `FS-102` or a new
   spec, and either soften the requirement's framing to match two independently-verified mechanisms,
   or add the missing cross-kind rewind test if the "single mechanism" framing is load-bearing).
9. **New this assessment — Finding 2 (blocking):** see §5.

## 5. Finding 2 — `FEAT-3500` is undelivered (blocking)

`FEAT-3500` (Role-Scoped Command Catalog & Assignment Scoping) is bucketed **Must-priority,
Release 1** in `docs/feature-planning/01-release-plan.md`. Its two owned requirements:

- **`FR-3510`** — "the system shall present... only the commands legal for the operator's seated
  role (bus vs. payload)... **rejected if attempted directly**" if outside scope.
- **`FR-3520`** — a Role Assignment's bus/payload/both scope "shall enforce that scope as a system
  behavior in its own right... **rejected at execution time**, whether or not it was also filtered
  from the order panel."

Both are **Must**-priority with an explicit reject-at-execution postcondition. The RTM's `FR-3510`/
`FR-3520` rows are the *only* two Feature-level rows in the entire matrix (alongside `FR-3310`,
Finding 1) with **both** `Test` and `Impl. Package` columns `UNASSIGNED` — and unlike `FR-3310`,
this is not a citation gap masking a real capability: **no role-based command-filtering or
enforcement mechanism exists anywhere in the codebase.** This was independently confirmed twice —
`08-code-implementation` (run #8, implementing the *adjacent* `IP-1151` seat-to-role-assignment
package) grepped `FS-105`/`IP-1050`/`IP-1051`/`buscommands.py`/`session/manager.py` for "role" and
found zero command-authorization hits; `09-package-verification` (run #15, `VR-1151`) independently
re-derived the same result rather than re-citing it. **This session's own grep against the current
tree (`role_assignments`, `_role_covers`, `assign_role`) confirms the record `IP-1151` creates is
read only by `staffing_report()` — nothing consumes it for command authorization.**

What *is* delivered is `FR-4210` (Seat-to-Role Assignment: *creating* the assignment record and
gating session `Start` on mandatory staffing) — a different requirement, owned by `FS-115`/`IP-1151`,
correctly `VERIFIED`. `FEAT-3500`'s own requirements (*using* that assignment to filter or enforce
commands) have no owning Feature Specification at all — absent from the FS↔FEAT reconciliation
table in `05-feature-review.md`, which lists an owning FS for every other Feature in this tranche.

This was already flagged as `BL-0014` (Medium, `DEFERRED`, "revisit the next time `06-feature-specification`
touches `FS-105`... not blocking any current work"). That disposition was reasonable for an ordinary
pipeline finding mid-tranche, but **a release-readiness audit's specific job is to check "is every
planned Feature actually delivered" — and by that test, a wholly unimplemented, unspecified,
Must-priority Feature is not a Low-priority loose end; it is undelivered scope with no authorization
to descope it.** The release plan's own text ("same verification-task framing as `FEAT-3300`... a
traceability gap, not new development") was an assumption, not a finding — this assessment is the
first pass to actually check that assumption against the code, and it does not hold.

**Severity: High.** Not Critical — this is a cooperative-trust PME tool where the cell selector
itself is already client-side trust (documented, accepted, `ADR-0015`), so a missing *role*-level
filter within an already-cooperating cell's own seat is a smaller blast radius than, say, a
cross-cell fog-of-war leak. But it is a Must-priority requirement pair with an explicit
reject-at-execution postcondition that is entirely absent, in a Feature the release plan claims is
in scope.

## 6. Assessment: **NO-GO** (for the full baseline as currently scoped)

Every other Feature in this tranche (16 of 17 FS-tracked Features, plus all Prototype/MVP-bucket
foundational work) is delivered, verified, integration-reviewed, and either clean or carrying an
explicitly authorized/disclosed residual risk. **The sole blocker is `FEAT-3500`** (§5): a
Must-priority, Release-1-bucketed Feature with zero implementation and zero owning specification.
Declaring this baseline release-ready as currently scoped would mean shipping a documented Must
requirement that provably does not hold.

This does not require redoing any of the other 17 Features' work. Two paths close this out, and
**which one is taken is the project owner's call, not this assessment's**:

- **Path A — implement it.** Route `FEAT-3500` through `06-feature-specification` (author the
  missing FS, or fold `FR-3510`/`FR-3520` into `FS-105` alongside the bus/payload command catalog
  they filter) → `07-implementation-planning` → `08-code-implementation` → `09-package-verification`,
  then re-run `10-integration-review` before re-attempting this stage.
- **Path B — descope it, with authorization.** `FEAT-3500` has no dependents in
  `04-feature-dependency-graph.md` (it is on the release plan's own "Optional" list — no sibling
  Feature's construction is blocked by deferring it), so moving it to a future release bucket with
  a recorded rationale is architecturally clean. If the project owner takes this path, this
  assessment can be re-run immediately against the remaining 17-Feature scope with an explicit GO,
  rather than waiting on new implementation work.

No baseline record is flipped by this NO-GO — per this skill's own rule, trackers are updated only
after an explicit user GO. `ROADMAP.md`, the Master Build Plan, `CLAUDE.md`, and the release plan
are left exactly as they stood before this assessment.
