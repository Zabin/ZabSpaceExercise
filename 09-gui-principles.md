# GUI Principles & UX for CAF Space Operators

This document sets the human-factors direction for the tool. It complements
`05-cell-interfaces.md` (what each cell does) and `10-sda-3d-viewer.md` (the 3D view) by
defining *how* the interface should behave for its actual users. Claude Code should treat
these as design constraints, not decoration.

## 1. Who the user is

The operating cells (Red/Blue) are **semi-technical Canadian Armed Forces (CAF) space
operators** — and by extension allied operators in a PME setting. Designing for this user
means:

- **They understand orbits, passes, SDA, and counterspace concepts** — do not dumb down the
  domain or hide orbital reality. The whole point is to train against it.
- **They are not necessarily software power-users or astrodynamicists.** They should not have
  to hand-edit orbital elements, write scripts, or reason about reference frames to play.
  The tool does the math; the operator makes the decisions.
- **They think in tasks and timelines, not menus.** "Get eyes on this object before the
  landing window" is the unit of thought — not "open dialog → select propagator → set epoch."
- **They work under time pressure and ambiguity.** The UI must make the *next decision* and
  the *time remaining to make it* unmistakable.
- **They expect military-style information density and terminology.** Clean, but not sparse;
  doctrinally correct labels (custody, characterization, ROE, keep-out volume), not consumer-
  app euphemisms.

> **Design north star:** an operator who knows the domain should be productive in minutes
> without a manual, and should never be surprised by *why* an action was or wasn't allowed.

## 2. Core UX principles

### P1 — Geometry is never hidden
Every command is bound to a pass/window. The interface continuously shows the next contact
countdown and the pass-timeline ribbon so the operator internalizes that space ops are
scheduling against orbital geometry. The tool should make it *impossible* to forget that you
cannot talk to a satellite that is below the horizon.

### P2 — Plan-first, not click-to-act
Operators **compose intent ahead of time** and the engine executes it when geometry allows
(see `11-command-planning-and-tasking.md`). The default interaction is *plan a command for
the next window*, not *do it now*. Instant actions are the rare exception (e.g., an ISL is
available, or a ground-segment/cyber action that isn't pass-gated).

### P3 — Show belief, mark uncertainty
The operator sees the world **as their SDA believes it to be**, never as ground truth. Every
displayed object, track, and characterization carries a visible **confidence/uncertainty**
indicator. Stale tracks visibly decay. The UI must distinguish *known*, *estimated*, and
*unknown* at a glance (see §3 and the 3D viewer doc).

### P4 — Always answer "why can't I?"
When an action is unavailable, the UI says *why* in plain operator language: "No command
window for SAT-7 until 14:32Z (next STATION-BRAVO pass)," "Insufficient delta-v," "ROE does
not authorize kinetic effects," "No custody — request sensor tasking first." Disabled buttons
must explain themselves on hover/tap. Never a silent dead control.

### P5 — Reversible by design (for the trainee)
Operators experiment. Queued orders are cancellable; planning is non-destructive. (White Cell
gets true time-travel; operators get a safe planning sandbox before commit.) This lowers the
fear of clicking and accelerates learning.

### P6 — One screen, three contexts
Map/3D view, timeline, and decision panel are always co-visible — the operator should not
lose situational awareness to navigate a menu tree. Modal dialogs are minimized; tasking and
planning happen in side panels that keep the world in view.

### P7 — Terminology and symbology are doctrinal and consistent
Use CAF/allied and joint space terms. Where a standardized symbology exists or can be adapted
(an APP-6-style approach for space tracks: friend/hostile/unknown/neutral, plus object type),
use it consistently. Color and shape carry the same meaning everywhere.

## 3. Information hierarchy & visual language

**Affiliation color (consistent across 2D, 3D, lists):**
- Blue = friendly, Red = hostile, Yellow = unknown/uncharacterized, Green = neutral/commercial,
  Grey/hatched = debris or hazard.

**Confidence encoding (the most important non-standard cue):**
- **Solid** symbol + tight marker = high-confidence current custody.
- **Softening/translucency + growing positional ellipse** = aging track; the longer since last
  observation, the larger and fainter.
- **Dashed/ghost** = predicted/propagated position with no recent obs ("last seen 3h ago,
  here's where it probably is").
- **Hollow "?" marker** = detected but uncharacterized (we see something; we don't know what).

**State badges on assets:** health, fuel/power/ammo as compact gauges; posture (e.g., escort/
point-defense) as an icon; an alert ring when the asset is the subject of a pending decision.

**Time is a first-class display:** a persistent sim-clock (UTC + T-relative), the current time
multiplier, and per-asset next-contact countdowns. Color the countdown as it approaches
(amber < 5 min, etc.) so imminent windows draw the eye.

## 4. Interaction patterns

- **Select-then-act:** select an object/asset → the decision panel populates with *only* legal
  options for it, each annotated with cost and execution time.
- **Plan on the timeline:** drag/drop or click a future window on the ribbon to schedule a
  command into it; the queue updates and the 3D/2D view can preview the resulting geometry.
- **Request, don't conjure, information:** to learn about an object the operator **tasks a
  sensor** (space or ground) and waits for the collection window — they cannot simply click an
  enemy sat and read its truth (see tasking doc).
- **Confirm only the consequential:** kinetic/irreversible/escalatory actions get a deliberate
  confirm with the consequence stated ("debris-generating; political cost: HIGH"); routine
  planning does not.
- **Undo/cancel is one action away** for anything not yet executed.

## 5. Accessibility & deployment realities

- **Not color-only:** affiliation and confidence must also be conveyed by shape/fill/label so
  the tool is usable by color-vision-deficient operators and on poor projectors.
- **Readable at distance:** PME often runs on a projector/large display for the White Cell —
  support a high-contrast, large-type presentation mode.
- **Keyboard-friendly:** common actions (select next asset, jump to next window, pause/step
  time for White Cell) have shortcuts; operators should not be mouse-bound.
- **Low-friction multi-display:** a cell may run map/3D on one screen and timeline/queue on
  another; the layout should be re-flowable, not fixed.
- **Latency tolerance:** in LAN multiplayer the UI must stay responsive while awaiting server
  confirmation — optimistic "queued (pending)" states that resolve on server ack.

## 6. Anti-patterns to avoid

- ❌ A "god view" of all objects with perfect truth — destroys the SDA training value.
- ❌ Instant command execution that ignores passes — destroys the core lesson.
- ❌ Burying the next-window/countdown information in a sub-menu.
- ❌ Requiring orbital-element math or frame selection from the operator.
- ❌ Silent disabled controls with no explanation.
- ❌ Consumer-game styling that undercuts the tool's credibility with military users.

## 7. How this maps to build phases
The 2D map, roster, timeline ribbon, order/queue panel, and "why can't I?" affordances are
**Phase 5 (UI)** in the roadmap. The SDA-belief rendering rules (§3) are a shared dependency
of both the 2D map and the **3D viewer** (`10-sda-3d-viewer.md`) and should be implemented
once as a reusable "render-from-custody" layer. Command planning and sensor tasking (§4) are
specified in `11-command-planning-and-tasking.md`.
