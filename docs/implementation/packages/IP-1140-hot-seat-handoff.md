# IP-1140 — Hot-Seat Hand-Off Screen-Blank Menu

> **Package ID:** IP-1140
> **Version:** 1.1 (2026-07-03 — independently verified; see Status below.)
> **Status:** ✅ VERIFIED *(2026-07-03, [`VR-1140`](../verification/VR-1140-hot-seat-handoff.md) —
> the hard postcondition (no leaked content, persists until Resume) confirmed against the live tree;
> full suite green (559 passed/3 skipped), both permanent gates green. **The documented FR-6610
> trigger/menu divergence was adjudicated, not waived**: `09-package-verification` determined the
> shipped manual-button/auto-cycle mechanism does **not** satisfy FR-6610's full intent — the
> missing automatic-trigger detection is a real, unmitigated risk in the one Feature enforcing
> fog-of-war client-side with no server backstop. Filed as a High-severity finding (`BL-0015`),
> routed to `07-implementation-planning` for a gap-closing package pending the user's
> prioritization — see `VR-1140`'s Adjudication section and the Master Build Plan's Risk item 6.
> **Risk-acceptance decision (2026-07-04, project owner, via `00-pipeline-manager`):** the user
> explicitly accepted this risk rather than authorizing a gap-closing package now — "I accept the
> risk of a cell not blanking the screen during handover as long as hot seat is an option." No
> gap-closing package is authorized at this time; `BL-0015` closes `DEFERRED` with the revisit
> trigger "if hot-seat mode's continued availability is ever reconsidered, or before the next
> `10-integration-review`." This does not change this package's own `VERIFIED` status: it
> accurately, non-overclaimingly documented exactly this gap and asked for exactly this
> adjudication. Was 🔵 COMPLETE *(entered `COMPLETE`, not `VERIFIED`,
> per this skill's rule that an as-built package may be born `VERIFIED` only after an actual
> `09-package-verification` pass — the authoring pass confirmed the cited code exists, but was not
> that independent pass).*)*
> **Dependencies:** FS-114, [IP-1090](IP-1090-multiplayer-session-transport.md) (the one-Session-
> object hot-seat/LAN sharing mechanism this hand-off menu sits on top of, per FS-114's own
> Dependencies field) — `VERIFIED`
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the screen-blank/resume overlay shown during a hot-seat hand-off
> **Feature Reference:** [FS-114 — Hot-Seat Hand-Off Screen-Blank Menu](../../features/FS-114-hot-seat-handoff.md)
> **Supersedes:** none — new package, first Implementation Package written against FS-114
> **Related Topics:** [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js),
> [`spacesim/ui_web/static/index.html`](../../../spacesim/ui_web/static/index.html)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This package was authored after `07-implementation-planning`'s required build-status verification
pass (`docs/implementation/01-technical-work-breakdown.md` Tranche 1) found FS-114's core
postcondition (no previously-displayed cell content visible during a hand-off) already implemented
— but via a mechanism that diverges from FR-6610's stated trigger and menu semantics. That
divergence is documented below, not smoothed over, per this skill's own guidance that a package
contradicting its spec is a defect to surface, not to paper past.*

## Package ID

IP-1140

## Title

Hot-Seat Hand-Off Screen-Blank Menu

## Objective

Document the existing "⏸ Handover" blank/blur/resume mechanism (`ui_web/static/app.js:2717-2733`,
`index.html:597-601`) against FS-114's Acceptance Criteria, and flag precisely where it satisfies
FR-6610's hard postcondition (no leaked content) while diverging from its stated trigger and menu
mechanism, so `09-package-verification` can adjudicate whether the divergence needs a follow-on
fix or is an acceptable implementation choice within FR-6610's intent.

**Situation: already implemented, in production use, with a documented spec divergence — not a
clean as-built match.**

## Feature Reference

[FS-114 — Hot-Seat Hand-Off Screen-Blank Menu](../../features/FS-114-hot-seat-handoff.md)

## Requirements Covered

| Req ID | Title (abridged) | How the existing code covers it (and where it diverges) |
|---|---|---|
| FR-6610 | Screen-blank pending-handoff menu between hot-seat role changes | **Postcondition met:** clicking `⏸ Handover` (`app.js:2717-2733`) opens the `#handover` overlay (`index.html:597-601`), which blurs/blanks the departing operator's cell content — no previously displayed cell's content is visible while the overlay is open, and it stays open until `Resume` is clicked (`app.js:2729-2732`), satisfying "no previously displayed cell's content reappears... before a new seat is selected" as a hard, not best-effort, postcondition. **Trigger diverges:** FR-6610 describes an *automatically detected* trigger ("the current seat's occupancy has ended and a new seat has not yet been selected") — the shipped mechanism is a *manually clicked* button; nothing detects seat relinquishment on its own. **Menu diverges:** FR-6610 describes a *seat-selection menu* persisting "until a seat is selected" — the shipped `Resume` button does not present a choice; it auto-computes the next cell by a fixed cycle (`CELL === "blue" ? "red" : CELL === "red" ? "blue" : "white"`, `app.js:2724`) and switches to it immediately on click, with no seat picker. |

## Architecture Components

- **C4 Operator Console** — `ui_web/static/app.js` (the `#6` "User-added future work" block,
  `:2713-2733`) and `ui_web/static/index.html` (`#handover` dialog markup, `:596-601`).
- **C2 Session / Application Layer** — none touched; this is a purely client-side mechanism (see
  Security Considerations below, inherited from FS-114's own explicit exception note).

## Interfaces

**INT-0001** (Browser ↔ Operator Console) — the client-side blank/blur/resume behavior occurs
entirely over this interface, with no `SessionAPI` (`INT-0006`) call in the current implementation
(the cycle-computation in `app.js:2724` reads only the client-local `CELL` variable, not any
server-provided seat-occupancy state) — a further divergence from FS-114's own Subsystem
Responsibilities table, which names `session/inprocess.py`/`session/manager.py` as providing "the
underlying seat/role-occupancy state this Feature's trigger condition... reads from." No such read
currently exists; the trigger is purely client-local.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code as-is. (If `09-package-verification` or a future
package elects to close the divergences noted above, that is out of this package's scope — see
Risks.)

### Reference files

- `spacesim/ui_web/static/index.html:596-601` — the `#handover` dialog markup (`handover-title`,
  `handover-who`, `handover-resume`).
- `spacesim/ui_web/static/app.js:2717-2733` — the click handler (blank/blur trigger) and Resume
  handler (auto-cycle + `setCell`).
- `spacesim/ui_web/static/app.js:2752` — the button-hint tooltip text ("Blank/blur the screen for
  hot-seat handoff").
- `spacesim/ui_web/static/index.html:624` — the in-app Help panel's own description ("⏸ Handover
  blanks the screen for hot-seat handoffs between operators").

## Implementation Tasks

All **already complete** (as shipped; see Requirements Covered for what is and is not literally
satisfied):

1. ✅ Implement a screen-blank/blur overlay that hides all previously displayed cell content until
   an explicit Resume action.
2. ✅ Ensure no previously displayed cell's content reappears before Resume is clicked (the hard
   postcondition FR-6610 states).
3. ⬜ *(not implemented, out of this package's scope to add)* Automatic detection of a
   seat-relinquish trigger (as opposed to a manually clicked button).
4. ⬜ *(not implemented, out of this package's scope to add)* A seat-selection menu offering an
   explicit choice among available seats (as opposed to an auto-computed next cell).

## Tests to Add

None proposed by this package — FR-6610's own stated Verification Method is "Demonstration," not
"Test" (`docs/requirements/01-functional-requirements.md:1216`), and no automated test exists or is
proposed for this client-side-only mechanism, consistent with this project's existing pattern of
no automated coverage for `ui_web/static/` behavior (`CLAUDE.md`: "browser GUI unverified
headless"). `09-package-verification` should perform the Acceptance Criteria demonstration by hand
against a running session.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `docs/features/FS-114-hot-seat-handoff.md`'s `Referenced By` metadata — add this package
  (cross-link only).
- `CLAUDE.md`'s Code Map — no change needed (existing `ui_web/static/` entries already cover the
  touched files).

## Definition of Done

- [x] No previously displayed cell's content is visible while the hand-off overlay is open (hard
  postcondition met).
- [x] The overlay persists until an explicit Resume click (no time-out/default-selection leak).
- [ ] *(Open — routed to verification, not claimed done by this package)* The trigger is an
  automatically detected seat-relinquish event, per FR-6610's literal description.
- [ ] *(Open — routed to verification, not claimed done by this package)* Resume presents an
  explicit seat-selection choice rather than auto-cycling to a computed next cell.

## Verification Checklist

- [x] `app.js:2717-2733`, `index.html:596-601` read and confirmed against the current tree.
  **Corrected 2026-07-03 (`VR-1140`): these line numbers had drifted** — the code now lives at
  `app.js:2805-2821`/`:2840` and `index.html:640-645` (content unchanged, citation stale from other
  work landing above this block). See `VR-1140` Findings #2.
- [x] `09-package-verification` should perform FS-114's Acceptance Criteria demonstration by hand:
  hand off from Red to Blue on the same browser, confirm no Red-cell data remains visible once the
  overlay is shown, and confirm nothing reappears before Resume. **Done 2026-07-03 (`VR-1140`)** —
  verified by static analysis of the CSS stacking context (`#handover`'s `z-index`/`position: fixed`
  occlusion guarantee), dispositive for both Acceptance Criteria bullets; see `VR-1140`.
- [x] `09-package-verification` should explicitly adjudicate the two open Definition-of-Done items
  above — either accept the manual-trigger/auto-cycle mechanism as satisfying FR-6610's intent (the
  hard postcondition, which is what carries the fog-of-war-leak consequence FS-114's Security
  Considerations flags, is met) or route a gap-closing package back through this pipeline.
  **Adjudicated 2026-07-03 (`VR-1140`): NOT accepted as satisfying FR-6610's full intent** — routed
  to `07-implementation-planning` for a gap-closing package as a High-severity finding, pending the
  user's prioritization. See `VR-1140`'s own Adjudication section for the full reasoning.

## Dependencies

- **Upstream:** [IP-1090](IP-1090-multiplayer-session-transport.md) (Multiplayer / LAN Session
  Transport) — `VERIFIED`; the one-Session-object hot-seat/LAN sharing mechanism FS-114 depends on
  already exists and is confirmed. No blocking dependency on this package.
- **Downstream:** None in this pass.
- **Build-sequencing:** None — already shipped.

## Risks

- **This is the one Feature in the catalog where a fog-of-war boundary is enforced client-side, not
  server-side** (FS-114's own Security Considerations, restated here because it is this package's
  single highest-consequence fact): a defect in this mechanism is a direct data leak with no
  server-side backstop. The current implementation's hard postcondition (no visible leak while the
  overlay is open) does hold by inspection of the cited code — but because the trigger is manual
  (a button click) rather than automatically detected, an operator who **forgets to click ⏸
  Handover** before walking away leaves their cell's content on screen indefinitely with no
  system-side prompt to blank it. This is the practical consequence of the trigger divergence
  noted in Requirements Covered, and is the single most important finding this package surfaces
  for `09-package-verification` to weigh.
- **Client-local trigger state, not server-read seat-occupancy state:** because `app.js:2724`'s
  cycle computation reads only the client-local `CELL` variable, this mechanism has no way to know
  whether the "next" cell it computes is actually unoccupied, actually the next intended operator,
  or itself needs to reject/redirect — a gap FS-114's own Subsystem Responsibilities table assumed
  would be closed by reading `session/inprocess.py`/`session/manager.py`'s seat-occupancy state,
  which does not currently happen.
- **A defect fix here, if authorized later, is architecturally small** (client-side JS only) but
  behaviorally significant given the leak-consequence profile above — flagged as a strong
  candidate for prioritization if `09-package-verification` or the user elects to close the
  divergence, consistent with FS-114's own Open Questions note ("should likely be prioritized
  given the consequence profile").
- **Adjudicated 2026-07-03 (`VR-1140`): this risk materialized as a formal High-severity finding,
  not merely a documented possibility.** `09-package-verification` determined the manual-trigger gap
  does not satisfy FR-6610's intent and recommended, at minimum, an idle/visibility-based fallback
  trigger as defense-in-depth alongside the existing manual button (a full automatic
  seat-relinquish-detection redesign is a larger, separate scoping question). Routed to
  `07-implementation-planning` for a gap-closing package; required the user's explicit
  prioritization/authorization before that package could be built, per MSTR-006 §3.
- **Risk accepted, 2026-07-04 (project owner):** rather than authorizing a gap-closing package now,
  the project owner explicitly accepted this risk as a known limitation of hot-seat mode ("I accept
  the risk of a cell not blanking the screen during handover as long as hot seat is an option"). No
  further remediation is planned unless hot-seat mode's continued availability is reconsidered, or
  the next `10-integration-review` re-raises it. `BL-0015` closed `DEFERRED` on that basis.

## Rollback Considerations

Rollback surface: `ui_web/static/app.js:2713-2733` and the `#handover` markup block in
`index.html:596-601` (both explicitly marked "User-added future work" in the source, suggesting
they were added outside this project's own numbered-pipeline discipline). Since this package
proposes no code change, there is nothing for it to roll back — this section is retained for
template consistency and to note that removing the mechanism entirely would reopen FR-6610 as a
fully unimplemented gap, not merely revert an in-progress change.
