# Training Manual — Index

[↑ Docs index](../INDEX.md)

A first-time guide to **installing, running, and facilitating** an exercise. No prior setup of
the tool is assumed. The simulator is a professional military education (PME) wargame: a **White
Cell** facilitator runs a scenario while **Red** and **Blue** cells command fleets of space and
ground assets — constrained by orbital geometry, where you can only command, observe, or attack
when an access window permits.

The tool runs both **single-machine hot-seat** (one browser, one operator switching cells with
the toolbar Cell buttons) **and LAN cooperative** (one White facilitator hosts a session; Blue,
Red, and additional pop-out viewers join the same URL from other tabs or LAN machines). Both
modes share the same fog-of-war, the same server-authoritative clock, and the same UI — there
is no separate "multiplayer build." See module 01 for the workflow.

> **First-time operator?** When you load a session, the **Mission brief panel** auto-opens at
> the top of the main column. It carries the per-cell situation, mission, friendly forces,
> threat picture, deadline countdown, ROE, success criteria, and tool tips — read it before
> doing anything else. Open it again any time from **View ▾ → Mission brief**.

> **Which cell are you?** Modules 01–11 are shared onboarding. For a **role-scoped procedure
> manual** scoped to your seat, jump to [12 — White Cell](12-white-cell-manual.md) (with
> [12a](12a-white-cell-analysis-and-exports.md) for analysis and exports),
> [13 — Blue cell](13-blue-cell-manual.md), or [14 — Red cell](14-red-cell-manual.md). Each is the
> thin procedure layer for that role on top of the shared concept modules; every section is
> cross-referenced to its backing code in [15 — traceability matrix](15-manual-traceability.md), so
> a feature change routes straight to the manual sections that must move with it.

> **About the screenshots:** the images embedded in these modules are faithful renderings of the
> web UI's panels, generated from real session data by `tools/render_manual.py` (stored in
> [`../manual/`](../manual/INDEX.md)). They show exactly what each panel reports.

## Modules

| Module | Contents |
|---|---|
| [01-install-and-run](01-install-and-run.md) | Install runtime/optional deps; launch the web server. |
| [02-interface](02-interface.md) | The interface at a glance: scenario picker, White god-view, player fog-of-war, 2D map / 3D globe, command & White menus. |
| [03-first-exercise](03-first-exercise.md) | Your first exercise (Vignette 1): load, plan a downlink, advance time, rewind & branch; headless walkthrough. |
| [04-guided-vignette](04-guided-vignette.md) | The guided training vignette, every step, both cells (Blue custody/imagery; Red reversible denial). |
| [05-core-concepts](05-core-concepts.md) | Plan-first commanding, SDA tasking→custody→unlock, bus SOH & safe mode, recovery, **diagnosing attacks from telemetry**, cyber off-pass exception, TLE add, doctrine & AAR, save/resume. |
| [06-the-vignette-library](06-the-vignette-library.md) | The full 19-vignette scenario library at a glance, plus the optional sensor fields for authoring your own and what **Load** refuses (and how it reports it). |
| [07-white-cell-facilitation](07-white-cell-facilitation.md) | Running an exercise as White Cell. |
| [08-http-api-reference](08-http-api-reference.md) | The HTTP API surface for clients/integration. |
| [09-troubleshooting-and-glossary](09-troubleshooting-and-glossary.md) | Common issues + glossary. |
| [09a-refusal-messages](09a-refusal-messages.md) | Lookup of every order, control, session and save refusal message: exact words, cause, fix. |
| [10-ui-reference](10-ui-reference.md) | Exhaustive UI reference — every control, dropdown, input, keyboard shortcut, and mouse interaction across all 15 panels, with annotated screenshots. This module holds the index and the always-visible panels (§10.1–§10.4). |
| [10a-ui-reference-orders](10a-ui-reference-orders.md) | UI reference, order panels: sensor tasking, compose form, maneuver/jam assistants, batch bar (§10.5–§10.9). |
| [10b-ui-reference-views](10b-ui-reference-views.md) | UI reference, viewers and review panels: globe, map, AAR, drill-down, modals/keys, activity timeline (§10.10–§10.15). |
| [11-vignette-playbooks](11-vignette-playbooks.md) | Per-vignette tutorials — how **each cell** completes its objectives, move by move (verified against the engine), with the window / weapons-quality / ROE gates called out. |
| [12-white-cell-manual](12-white-cell-manual.md) | **Role-scoped manual — White Cell.** The facilitator's procedure layer: set-up (vignette, classification, seat-to-role staffing), Observer designation, room control (hot-seat/LAN), time control, injects, monitoring, TLE add, AI-Red, AAR, save/resume, competency assessment. Sections `WCM-1`–`WCM-11`, cross-referenced in §15; analysis and exports continue in 12a. |
| [12a-white-cell-analysis-and-exports](12a-white-cell-analysis-and-exports.md) | **Role-scoped manual — White Cell, part 2.** Analysis and data exports: offline research batch exports, live RIC-frame view + CATS overlay, quick TLE export, time-span ephemeris export (truth, URL-only), per-asset telemetry CSV export (URL-only). Sections `WCM-12`–`WCM-16`, cross-referenced in §15. |
| [12b-white-cell-vignette-creator](12b-white-cell-vignette-creator.md) | **Role-scoped manual — White Cell, part 2.** Build your own vignette in the Creator: draft, add ground sites and TLE satellites, edit, JSON view, preview, seats and roles, save, and play it; every refusal message. |
| [12c-white-cell-rules-and-staffing](12c-white-cell-rules-and-staffing.md) | **Role-scoped manual — White Cell, part 3.** Operator seats and staffing, approval gates and live ROE changes, injects in depth (schedule, edit, cancel, conditions, who sees what). |
| [12d-white-cell-clock-saves-and-controls](12d-white-cell-clock-saves-and-controls.md) | **Role-scoped manual — White Cell, part 4.** Time-control bounds and exact refusal messages, what a save holds and every Load refusal, adding satellites before Start (TLE/OMM), which seat sees which controls, space weather and debris persistence. |
| [13-blue-cell-manual](13-blue-cell-manual.md) | **Role-scoped manual — Blue cell.** The defender's procedure layer: fog-of-war, plan-first commanding, SDA custody, bus health, attack diagnosis, recovery, defensive maneuver, cyber, live RIC-frame view + CATS overlay, quick TLE export, time-span ephemeris export (own belief, URL-only), own telemetry CSV export (URL-only). Sections `BLU-n`, cross-referenced in §15. |
| [13a-blue-cell-rules-and-delivery](13a-blue-cell-rules-and-delivery.md) | **Role-scoped manual — Blue cell, part 2.** The Operator seat field, orders awaiting approval and ROE changes, delivery paths and what a jam stops, the manoeuvre ledger. |
| [14-red-cell-manual](14-red-cell-manual.md) | **Role-scoped manual — Red cell.** The adversary's procedure layer: fog-of-war, plan-first commanding, SDA targeting, the five D's, cyber wildcard, own-force management, doctrine profiles, live RIC-frame view + CATS overlay, quick TLE export, time-span ephemeris export (own belief, URL-only), own telemetry CSV export (URL-only). Sections `RED-n`, cross-referenced in §15. |
| [14a-red-cell-rules-and-delivery](14a-red-cell-rules-and-delivery.md) | **Role-scoped manual — Red cell, part 2.** The Operator seat field, orders awaiting approval and ROE changes, which link to jam, the manoeuvre ledger. |
| [15-manual-traceability](15-manual-traceability.md) | **Bidirectional cross-reference** feature ⇄ manual section, so any feature change routes to exactly the cell-manual sections that describe it (and vice versa). The seam that keeps the manuals cheap to maintain. |
| [16-learning-path](16-learning-path.md) | **The vignette learning path** — the 19 vignettes sequenced from zero-knowledge onboarding through the canonical mechanics ladder into the mission-set/doctrine tracks, each rung linked to the manual modules to read first and its verified playbook. |

## See also

- [`../build-spec/07-operator-console.md`](../build-spec/07-operator-console.md) — the console spec
  the UI implements.
- [`../vignettes/INDEX.md`](../vignettes/INDEX.md) — the authored scenario designs behind §6.
