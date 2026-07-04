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
> manual** scoped to your seat, jump to [12 — White Cell](12-white-cell-manual.md),
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
| [06-the-vignette-library](06-the-vignette-library.md) | The full 19-vignette scenario library at a glance. |
| [07-white-cell-facilitation](07-white-cell-facilitation.md) | Running an exercise as White Cell. |
| [08-http-api-reference](08-http-api-reference.md) | The HTTP API surface for clients/integration. |
| [09-troubleshooting-and-glossary](09-troubleshooting-and-glossary.md) | Common issues + glossary. |
| [10-ui-reference](10-ui-reference.md) | Exhaustive UI reference — every control, dropdown, input, keyboard shortcut, and mouse interaction across all 14 panels, with annotated screenshots. |
| [11-vignette-playbooks](11-vignette-playbooks.md) | Per-vignette tutorials — how **each cell** completes its objectives, move by move (verified against the engine), with the window / weapons-quality / ROE gates called out. |
| [12-white-cell-manual](12-white-cell-manual.md) | **Role-scoped manual — White Cell.** The facilitator's procedure layer: set-up, room control (hot-seat/LAN), time control, injects, monitoring, TLE add, AI-Red, AAR, save/resume. Sections `WCM-n`, cross-referenced in §15. |
| [13-blue-cell-manual](13-blue-cell-manual.md) | **Role-scoped manual — Blue cell.** The defender's procedure layer: fog-of-war, plan-first commanding, SDA custody, bus health, attack diagnosis, recovery, defensive maneuver, cyber. Sections `BLU-n`, cross-referenced in §15. |
| [14-red-cell-manual](14-red-cell-manual.md) | **Role-scoped manual — Red cell.** The adversary's procedure layer: fog-of-war, plan-first commanding, SDA targeting, the five D's, cyber wildcard, own-force management, doctrine profiles. Sections `RED-n`, cross-referenced in §15. |
| [15-manual-traceability](15-manual-traceability.md) | **Bidirectional cross-reference** feature ⇄ manual section, so any feature change routes to exactly the cell-manual sections that describe it (and vice versa). The seam that keeps the manuals cheap to maintain. |

## See also

- [`../build-spec/07-operator-console.md`](../build-spec/07-operator-console.md) — the console spec
  the UI implements.
- [`../vignettes/INDEX.md`](../vignettes/INDEX.md) — the authored scenario designs behind §6.
