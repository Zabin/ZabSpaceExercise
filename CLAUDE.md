# CLAUDE.md — Space Control & Orbital Warfare Exercise Simulator

Durable guide for Claude Code sessions. Keep it short. Anything that changes with each package
belongs in the [code map](docs/architecture/code-map.md) or the ledgers, not here.

## What this is

A **professional military education (PME) wargaming tool** for space control and orbital warfare.
A White Cell facilitator runs an exercise; Red and Blue cells command fleets of space and ground
assets as bus and payload operators, constrained by orbital geometry (you can only command, observe
or attack when an access window permits). Most effects are reversible (EW, cyber, proximity), not
kinetic. It runs single-machine hot-seat and multi-tab / LAN cooperative: every browser tab points
at one FastAPI server, and fog of war is enforced server-side.

**Status.** Release 1.0 shipped on 2026-11-01 (tag `release-1.0`, manifest
[`docs/releases/release-1.0.md`](docs/releases/release-1.0.md)). All 94 Implementation Packages are
`VERIFIED`. The suite is 2244 tests: 2240 pass and 4 skip for data reasons; 42 of them are
headless-Chromium console tests. The ten known deviations that shipped are in
[REV-REL-004](docs/reviews/release-assessment-release-candidate-10.md) §A.7. The browser GUI is not
verified end to end. Release 2.0 is planned in
[`docs/feature-planning/06-release-2-plan.md`](docs/feature-planning/06-release-2-plan.md). A
repository refactor is in progress: [`docs/pipeline/refactor-plan.md`](docs/pipeline/refactor-plan.md).

## Where things are

| Need | Go to |
|---|---|
| Any document | [`docs/INDEX.md`](docs/INDEX.md) |
| Architecture and requirements (the only binding source) | [`docs/architecture/INDEX.md`](docs/architecture/INDEX.md), the GDS-00…GDS-10 ladder |
| Requirement leaves | `docs/requirements/01-functional-requirements.md`, `02-non-functional-requirements.md`, `03-requirements-traceability-matrix.md` |
| Which module does what | [`docs/architecture/code-map.md`](docs/architecture/code-map.md) |
| The pipeline and its skills | [`.claude/skills/README.md`](.claude/skills/README.md) |
| Where the pipeline stands, and what is owed | `docs/pipeline/pipeline-journal.md` (Position block), `docs/pipeline/backlog.md` |
| Document and package ledgers | [`ROADMAP.md`](ROADMAP.md), `docs/implementation/00-master-build-plan.md` |
| Operator manuals | `docs/training/` (a co-equal product; `15-manual-traceability.md` maps features to manual sections) |
| Deferred ideas | [`docs/FUTURE-WORK.md`](docs/FUTURE-WORK.md) |

`docs/build-spec/` is **deprecated legacy reference**. The GDS ladder supersedes it entirely, by
owner instruction. Never cite it as binding; flag a gap instead.

## Layout

```
spacesim/
├── engine/   # deterministic core: no UI, no network, no wall clock
├── session/  # SessionManager, CellController (fog of war), SessionAPI (the network seam)
├── content/  # vignettes, inject library, ground sites (data) + loaders
├── ui_web/   # FastAPI server + browser console; depends on session, not engine
├── tools/    # offline utilities that drive the engine
└── tests/    # pytest, including the determinism gate
```

Stack: Python 3.11+ (validated on 3.13), NumPy, `sgp4`, pydantic v2, PyYAML, FastAPI, pytest,
hypothesis, Playwright.

## Load-bearing invariants (never compromise these)

1. **Deterministic core.** No wall-clock reads and no global RNG anywhere in `engine/`.
   `(initial_state, ordered eventlog, seed) → byte-identical state`. This is what makes
   rewind, undo and branch exact. The determinism property test must stay green forever.
2. **UI-agnostic engine.** `engine/` imports no UI or transport code (`test_import_guard.py`).
3. **Fog of war at the boundary.** Filtering lives at the `SessionAPI` / `CellController` layer,
   never in the UI. Red and Blue render only their own tracks and view, never ground truth.
4. **Plan-first.** Operators plan commands that execute at the next valid access window and task
   sensors for collection; they never act instantly on perfect knowledge.
5. **Sub-step the clock.** Advance to the next scheduled event, never past it.
6. **Content is data.** Vignettes, asset templates and effect templates are data files. If
   scenario logic leaks into code, move it back into data plus inject and effect primitives.

## Key facts

- **Six access channels:** `command_uplink`, `telemetry_downlink`, `sensor_observation`,
  `jam_footprint`, `weapon_engagement`, `rpo_proximity`.
- **Five effect categories:** deceive, disrupt, deny, degrade, destroy. **Cyber is the exception:**
  it is not window-gated; it resolves against `{access_vector, success_prob, persistence,
  patchable}` and the defender's cyber posture.
- **Orbital fidelity:** moderate (Keplerian + J2, TLE via `sgp4`), behind the `Propagator`,
  `AccessProvider` and `EffectResolver` interfaces.
- **Sizing:** about 24 satellites is a soft guideline, not an engine cap; a clock-lag watchdog warns
  White Cell when the hardware cannot keep up. Constellations of 3 or fewer, each operated
  individually.
- **Library:** 19 vignettes (8 canonical, training-basics, 5 Red COA, 3 mission-set, 1 learning,
  1 novel), each with a per-cell `intro_brief`; the 8 canonical ones also carry a `tutorial`.

## Trust model (load-bearing)

There is **no authentication**. Every seat (`white`, `blue`, `red`, `observer`, and the operator
seat on orders) is asserted by the client. **Deploy only on a trusted LAN with cooperative
participants.**

- Cell-scoped reads are filtered by `SessionAPI` / `CellController`, but a participant can ask for
  another cell's view by naming it.
- No-cell reads (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`, `/assessment`,
  `/ephemeris/truth`, the Observer view, White facilitation reads) expose ground truth by design
  (`FR-6220`).
- White Cell controls are refused (403) unless the request names the `white` seat; the Observer
  seat is refused on every mutating route; AAR playback obeys the requesting seat. These are
  rejection rules, not authentication (`FR-4310`, `FR-4320`, `FR-4330`, `FR-7340`, `FR-3520`).

## Working rules

- **Test-first.** Encode the "done when" check as a failing test, then implement. Add a regression
  test for each defect fixed. Run `pytest` before every commit.
- **Every test names its origin:** `@pytest.mark.verifies("FR-xxxx", …)` (or an `FS-` / `IP-` ID).
  The suite fails on an untagged test or an ID that is not a live baseline item.
- **Generated, never hand-edited:** the RTM Test column (`python3 -m pytest --origin-report=rtm`).
- **Documentation checks run with the suite:** broken relative links, an `INDEX.md` that omits a
  document in its folder, status ledgers that disagree, and retired documents still present or
  still named. The allow-lists under `spacesim/tests/` only shrink.
- **Pipeline.** Work runs through the numbered skills in `.claude/skills/`. Only
  `08-code-implementation` writes `spacesim/` production code; only `09-package-verification`
  writes `VERIFIED`; a specified package is not an authorized one (MSTR-006 §3). New work enters
  through `00-intake`.
- **Git.** Trunk-based. **One open pull request at a time.** CI (the full suite on the locked
  dependencies, plus a dependency audit) must be green; then squash-merge, and the branch-cleanup
  workflow deletes the branch. Never stack branches. Package work still needs its pipeline gates
  before it merges.
- **Releases.** GO or NO-GO is the owner's call. Every release is archived as it ships: an
  annotated tag and `archive/release-<n>.<m>` ref on the release commit, plus a manifest under
  `docs/releases/`, before new work starts.

## Commands

```bash
pip install -r requirements.lock && pip install --no-deps -e .   # the release's exact versions
python3 -m spacesim.ui_web                                       # host/port/reload from spacesim.config.yaml (default 127.0.0.1:8000)
uvicorn spacesim.ui_web.server:app --host 0.0.0.0                # LAN multiplayer: share the URL
python3 -m pytest                                                # whole suite (about 5 minutes)
python3 -m pytest -m "not browser"                               # everything except the Chromium tests
python3 -m pytest -m browser                                     # console-rule tests; skip loudly without Playwright/Chromium
python3 -m pytest spacesim/tests/test_determinism.py             # the determinism gate
python3 -m pytest spacesim/tests/test_import_guard.py            # the engine guardrails
python3 -m pytest spacesim/tests/test_doc_integrity.py spacesim/tests/test_test_origins.py   # documentation and test-origin gates
python3 -m pytest --origin-report [--origin-ids=FR-1120,…]       # read-only: tests by declared origin
python3 -m pytest --origin-report=rtm                            # regenerate the RTM Test column
```

**Dependency lock (`NFR-1510`).** `pyproject.toml` declares minimum versions; each release ships
`requirements.lock`, an exact pin of every dependency. To refresh it: install the latest into a
fresh environment, run both suite modes and the determinism gate, fix or hold anything that breaks
(never change the engine to suit a dependency), raise the `pyproject.toml` floors, re-freeze,
re-install from the new lock in another fresh environment, re-run, commit lock and floors together.

**Server configuration.** `spacesim.config.yaml` at the repository root (`SPACESIM_CONFIG`
overrides the path) sets host, port and reload, and optionally `content.external_vignette_dirs`
and `content.user_save_dir`. The bare `uvicorn` command ignores it.

**Multiplayer.** White loads and starts a session; the URL becomes `…/#sess-N`. Others open that
URL and pick Blue or Red. The server-side clock advances once however many tabs are open. Pop-out
windows (View → Pop out) join the same session for multi-monitor use.
