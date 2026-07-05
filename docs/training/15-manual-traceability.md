[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 15. Per-cell manual traceability matrix

The **bidirectional cross-reference** that keeps the three role-scoped cell manuals
([White](12-white-cell-manual.md) · [Blue](13-blue-cell-manual.md) ·
[Red](14-red-cell-manual.md)) cheap to maintain. It exists so a change is never silently stranded
from its documentation:

- **Feature → manual (§15.1):** when you change a code feature, look it up here to see exactly
  which manual sections describe it, and update them in the same change.
- **Manual → feature (§15.2):** when you edit a manual section, this tells you which code and
  endpoints back it, so you can confirm the prose still matches reality.

Every manual section already carries an inline **`> Sources:`** footer naming its backing code —
this matrix is the inverse index that lets you start from the code instead. Keep both directions in
sync: **when you add or renumber a manual section, add its row to §15.2 and add its ID to every
feature row in §15.1 that it touches.** This upkeep rule is enforced by the pipeline hooks in
[`08-code-implementation`](../../.claude/skills/README.md) (code side) and the dedicated
training-corpus skills `08-training-manual-authoring` / `08-vignette-development` /
`09-training-manual-review` (see §15.3). The whole apparatus satisfies **FR-11120/FR-11210** of the
requirements baseline (the training corpus is a co-equal product — MSTR-001 §2).

Section IDs: `WCM-n` = White Cell manual, `BLU-n` = Blue cell manual, `RED-n` = Red cell manual.
The **vignette learning path** ([`16-learning-path.md`](16-learning-path.md)) is the corpus's
fourth traceable surface: it maps each vignette to the manual sections a trainee reads first and to
its playbook — §15.4 records that linkage's maintenance rule.

### 15.1 Feature → manual sections (forward index)

Start here when a **code feature changes**. The "Backing code (primary)" column names the module(s)
most likely to be edited; the manual sections are every place that behavior is documented.

| Feature / capability | Backing code (primary) | White | Blue | Red |
|---|---|---|---|---|
| Fog-of-war boundary & per-cell view | `session/controller.py`, `session/scene.py` | WCM-1, WCM-6 | BLU-1 | RED-1 |
| Mission brief (`intro_brief`) | `content/vignette.py`, `server.py` `/brief` | WCM-2 | BLU-1 | RED-1 |
| Vignette load + parameter dials | `content/vignette.py`, `vignettes/*.yaml` | WCM-2 | — | — |
| `ops_fidelity` (tactical/realistic/full_ttc) | `content/vignette.py`, `bus.py` | WCM-2 | BLU-5 | RED-7 |
| Hot-seat / LAN / pop-out transport | `session/inprocess.py`, `server.py` | WCM-3 | — | — |
| Server-authoritative clock, pause/jump | `session/manager.py`, `engine/clock.py` | WCM-4 | — | — |
| Rewind / undo / branch (determinism) | `session/manager.py`, `engine/simulation.py` | WCM-4, WCM-9 | — | — |
| Injects + builder + library | `content/inject_library.yaml`, `server.py` `/inject` | WCM-5 | — | — |
| Activity timeline (Gantt) | `ui_web/static/app.js`, `session/scene.py` | WCM-6 | BLU-2 | RED-2 |
| Coaching notes | `content/vignette.py` (`Vignette.coaching`) | WCM-6 | — | — |
| Objectives / deadlines | `content/vignette.py`, `server.py` `/objectives` | WCM-6 | BLU-10 | RED-9 |
| TLE force-add | `engine/propagator.py`, `server.py` `/force/tle` | WCM-7 | — | — |
| Red doctrine presets + `red_step` | `session/redai.py` | WCM-8 | — | RED-8 |
| AAR replay / scrub / branch-compare | `session/aar.py` | WCM-9 | — | — |
| Save / resume | `engine/simulation.py`, `server.py` `/save` | WCM-10 | — | — |
| Clock-lag watchdog | `session/manager.py` (`_record_catch_up_lag`) | WCM-10 | — | — |
| Plan-first commanding + delivery paths | `engine/orders.py`, `engine/access.py` | — | BLU-2 | RED-2 |
| Dry-run validity preview | `engine/orders.py` (`dry_run`) | — | BLU-3 | RED-3 |
| Consequence preview | `server.py` `/preview/consequence`, `engine/effects.py` | — | BLU-3 | RED-3, RED-5 |
| Maneuver assistant (6 modes) | `engine/maneuver.py` | — | BLU-3, BLU-8 | RED-3 |
| ISR/observe assistant | `engine/isr.py` | — | BLU-3, BLU-4 | RED-3, RED-4 |
| Jam assistant + footprint | `engine/jam.py` | — | BLU-3, BLU-6 | RED-3, RED-5 |
| SDA tasking → custody → unlock | `engine/custody.py`, `engine/access.py` | — | BLU-4 | RED-4 |
| Weapons-quality gate | `engine/custody.py` | — | BLU-4 | RED-4, RED-5 |
| Bus/payload SOH + safe mode | `engine/bus.py`, `engine/busmodel.py` | WCM-2 | BLU-5 | RED-7 |
| Telemetry signatures + nominal ghost | `engine/telemetry.py` | — | BLU-6 | RED-7 |
| Safe-mode recovery chain | `engine/recovery.py`, `engine/buscommands.py` | — | BLU-7 | RED-7 |
| Bus/payload command verbs | `engine/buscommands.py` | — | BLU-7 | RED-7 |
| Conjunctions + collision avoid | `world.conjunctions`, `prop.collision_avoid` | — | BLU-8 | — |
| Cyber (off-pass exception) | `engine/cyber.py` | — | BLU-9 | RED-6 |
| Five D's effects | `engine/effects.py` | — | — | RED-5 |
| Kinetic engagement + ROE gate | `engine/engage.py` | — | — | RED-5 |
| RPO / co-orbital proximity | `engine/access.py` (`rpo_proximity`) | — | BLU-6 | RED-5 |
| Per-cell playbooks / tutorial | `test_vignette_tutorials.py`, `/vignettes/{id}/tutorial` | WCM-2 | BLU-10 | RED-9 |
| Vignette library (add/move/retire) | `content/vignettes/*.yaml` | WCM-2 | BLU-10 | RED-9 |
| Learning-path sequence & rung linkage | `16-learning-path.md`, `content/vignettes/*.yaml` | WCM-2 | BLU-10 | RED-9 |
| Classification banner | `content/vignette.py` (`Vignette.classification`), `session/manager.py`, `session/aar.py` | WCM-2 | — | — |
| Observer read-only seat (4th cell, no command ability) | `session/inprocess.py` (`set_observer_view`/`get_observer_view`), `ui_web/server.py` (`_reject_observer`) | WCM-1 | — | — |
| Seat-to-role assignment / staffing gate | `content/vignette.py` (`Vignette.roles_needed`), `session/manager.py` (`assign_role`/`staffing_report`) | WCM-2 | — | — |
| Competency assessment (custody/window/divergence rubric) | `session/assessment.py`, `GET /assessment` | WCM-11 | — | — |
| Research analytics (offline batch export) | `tools/research_batch.py`, `session/research_export.py` | WCM-12 | — | — |

### 15.2 Manual section → backing features (reverse index)

Start here when you **edit a manual section** and want to confirm it still matches the code. This
mirrors each section's inline `> Sources:` footer.

#### White Cell manual (`WCM-n`)

| § | Topic | Backing code / endpoints |
|---|---|---|
| WCM-1 | Role and view | `session/manager.py`, `session/controller.py`, `session/inprocess.py` (Observer, FR-6510) |
| WCM-2 | Set up the exercise | `content/vignette.py`, `vignettes/*.yaml`, `/brief/{cell}`, `session/manager.py` (classification, seat-to-role) |
| WCM-3 | Hot-seat / LAN / pop-out | `session/inprocess.py`, `server.py` (`/api/sessions`) |
| WCM-4 | Time control | `session/manager.py`, `engine/clock.py`, `/clock` |
| WCM-5 | Injects | `content/inject_library.yaml`, `/inject` |
| WCM-6 | Monitor both sides | `session/scene.py`, `app.js`, `Vignette.coaching` |
| WCM-7 | TLE add | `engine/propagator.py`, `/force/tle` |
| WCM-8 | AI-Red doctrine | `session/redai.py`, `/red_step` |
| WCM-9 | After-Action Review | `session/aar.py`, `/aar*` |
| WCM-10 | Save/resume + lag watchdog | `engine/simulation.py`, `/save`, `_record_catch_up_lag` |
| WCM-11 | Competency assessment | `session/assessment.py`, `/assessment` |
| WCM-12 | Offline research batch exports | `tools/research_batch.py`, `session/research_export.py` |

#### Blue cell manual (`BLU-n`)

| § | Topic | Backing code / endpoints |
|---|---|---|
| BLU-1 | Fog-of-war view | `session/controller.py`, `session/scene.py`, `/brief/blue` |
| BLU-2 | Plan-first commanding | `engine/orders.py` |
| BLU-3 | Previews before commit | `engine/orders.py` `dry_run`, `/preview/consequence`, `engine/{maneuver,isr,jam}.py` |
| BLU-4 | SDA tasking loop | `engine/custody.py`, `engine/access.py` |
| BLU-5 | Bus health | `engine/bus.py`, `engine/busmodel.py` |
| BLU-6 | Diagnose from telemetry | `engine/telemetry.py` |
| BLU-7 | Recovery | `engine/recovery.py`, `engine/buscommands.py` |
| BLU-8 | Maneuver & conjunctions | `world.conjunctions`, `prop.collision_avoid`, `engine/maneuver.py` |
| BLU-9 | Cyber posture | `engine/cyber.py` |
| BLU-10 | Win the vignette | `11-vignette-playbooks.md`, `/vignettes/{id}/tutorial` |

#### Red cell manual (`RED-n`)

| § | Topic | Backing code / endpoints |
|---|---|---|
| RED-1 | Fog-of-war view | `session/controller.py`, `session/scene.py`, `/brief/red` |
| RED-2 | Plan-first commanding | `engine/orders.py` |
| RED-3 | Previews before commit | `engine/orders.py` `dry_run`, `/preview/consequence`, `engine/{maneuver,isr,jam}.py` |
| RED-4 | SDA targeting | `engine/custody.py`, `engine/access.py` |
| RED-5 | Five D's / effects | `engine/effects.py`, `engine/{jam,engage}.py`, `engine/access.py` |
| RED-6 | Cyber wildcard | `engine/cyber.py` |
| RED-7 | Own-force management | `engine/bus.py`, `engine/recovery.py`, `engine/telemetry.py` |
| RED-8 | Doctrine profiles | `session/redai.py` |
| RED-9 | Win the vignette | `11-vignette-playbooks.md`, `/vignettes/{id}/tutorial` |

### 15.3 Maintenance protocol (how this stays true)

The matrix is only useful if it stays current. Two mechanisms keep it so:

1. **Inline `> Sources:` footers** on every manual section are the ground truth; §15.1/§15.2 are
   the inverse index derived from them. On any edit, the footer and the matrix row move together.
2. **Pipeline hook.** Stage `08-code-implementation` includes the cell manuals in its
   documentation-update step: when an Implementation Package's `Documentation Updates` field (or the
   §15.1 lookup for the code it touched) names a manual section, that section — and this matrix row
   — are updated in the same package. Stage `10-integration-review`'s documentation-coherence
   dimension spot-checks that a shipped feature change did not leave a manual section stale.

If you change a feature in §15.1 and the manual section still reads correctly, no edit is needed —
but confirm it, don't assume it.

### 15.4 Vignette ⇄ learning-path linkage

The learning path ([`16-learning-path.md`](16-learning-path.md)) is the fourth traceable surface,
maintained by `08-vignette-development` and reviewed by `09-training-manual-review`:

- **Every vignette appears on exactly one rung** (FR-11310). Add/move/retire a vignette →
  its rung, its [§11 playbook](11-vignette-playbooks.md) entry, its
  [§6 library](06-the-vignette-library.md) row, and any vignette count in README/CLAUDE.md move
  in the same change set.
- **Every rung links its manual prerequisites and playbook** (FR-11320) — those links resolve to
  real sections here in the corpus. A renamed manual section that a rung's "Read first" points at
  must update the rung too.
- **The playbooks the rungs link to are machine-verified** by
  `spacesim/tests/test_vignette_tutorials.py` (FR-11420) — that test is the one automated staleness
  gate in the whole training corpus; keep it green when a vignette script changes.

### 15.5 Requirements footing

This apparatus is not just convention — it satisfies a requirements-baseline family:
FR-11110 (role-scoped coverage), FR-11120 (source anchoring = the `> Sources:` footers),
FR-11210 (this bidirectional index), FR-11310/FR-11320 (§15.4 learning-path linkage),
FR-11410 (currency rides the changing package), FR-11420 (machine-verified playbooks), and
NFR-3400–3600 (accuracy / modularity / learner-appropriate presentation). See
[`docs/requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md)
§FR-11000 and [`02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md)
§16.

### 15.6 Layout evaluation (`BL-0026`)

**Question:** FR-11110 mandates role-scoped *coverage*, not the current per-cell-monolith layout
(`training/12-14`) specifically — the project owner asked (2026-07-04) whether a task-oriented cut
across cells would serve trainees better, now that
[R606](../research/encyclopedia/R606-minimalist-and-procedural-documentation.md) (minimalist,
task-centered technical documentation — Carroll's *The Nurnberg Funnel*) grounds the decision.

**R606's success criterion:** judge by task-completion speed for a reader mid-task, not by
comprehensiveness — "can a Blue operator who just hit a jam signature find the diagnosis procedure
fast, with minimal irrelevant material in the way," not "does this cover every mechanic somewhere."

**Evaluation.** Two structural options were weighed against that criterion:

1. **Per-cell (current).** Each of `BLU-n`/`RED-n`/`WCM-n` is already a *procedure layer*, not a
   reference — it deep-links shared concept modules (`05-core-concepts.md`,
   `02-interface.md`) rather than re-explaining mechanics, which is already the minimalist instinct
   R606 asks for. Almost every task a Blue or Red operator actually performs mid-exercise is
   inherently role-specific (Blue's SDA custody loop and Red's SDA targeting loop use the same
   engine mechanic but are procedurally distinct decisions), so a reader mid-task lands on exactly
   the section for their own role's version of that task with nothing from the other cell's
   perspective in the way — a fast path by R606's own standard.
2. **Task-oriented (cutting across cells).** A small number of mechanics genuinely mirror each
   other across Blue/Red — cyber (`BLU-9`/`RED-6`), previews-before-commit (`BLU-3`/`RED-3`), and
   SDA (`BLU-4`/`RED-4`) are the same underlying engine behavior read from each side. A unified
   "Cyber" or "Previews" module could serve both roles from one file. But collapsing these into
   cross-cell modules would cost the exact thing each per-cell manual already has going for it: a
   reader mid-task would now have to skip past the *other* cell's half of the module to find their
   own — for a corpus this size (9-10 sections per manual, each within NFR-3500's 50-300-line
   budget), that cost is not clearly recovered by the shared-authoring convenience it buys.

**Recommendation: keep the per-cell layout.** It already satisfies FR-11110's coverage mandate and
R606's task-completion-speed criterion for the large majority of sections. Restructuring the whole
corpus is not warranted by the evidence above. What *is* warranted, and applied in this same pass:
**cross-link the small set of genuinely mirror-image sections** so a reader who wants the other
side's version of the same mechanic can jump directly, rather than searching — `BLU-9`↔`RED-6`
(cyber), `BLU-3`↔`RED-3` (previews-before-commit), `BLU-4`↔`RED-4` (SDA) each now carry a one-line
"see also" cross-reference. This gets R606's cross-cutting benefit at near-zero restructuring cost,
without regressing the per-cell procedure-layer property that already works.

**Revisit trigger:** if the corpus grows enough that a single manual exceeds NFR-3500's module-count
guidance, or if a future role (beyond White/Blue/Red/Observer) needs a mechanic that spans more than
two cells, re-run this evaluation — the "small number of genuine mirrors" premise above would no
longer hold at that scale.

---
