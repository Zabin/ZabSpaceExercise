# DOM-003 — White Cell Framework

> **Document ID:** DOM-003
> **Version:** 1.0
> **Status:** 🚧 In progress (most mechanics shipped; framework formalizes existing capability + states gaps)
> **Dependencies:** MSTR-001, MSTR-003
> **Referenced By:** DOM-001, DOM-009, FS-106, FS-107, FS-108 (candidate)
> **Produces:** FS-106 White Cell Dashboard, FS-108 (candidate) Inject Authoring
> **Feature Mapping:** FS-106, FS-107
> **Related Topics:** [`docs/training/07-white-cell-facilitation.md`](../training/07-white-cell-facilitation.md),
> [`docs/build-spec/07-operator-console.md`](../build-spec/07-operator-console.md), R307 (wargaming theory), R308 (red teaming)

[↑ Docs index](../INDEX.md)

## 1. Purpose

Formalizes the White Cell's role, authority, and tooling needs, consistent with MSTR-003 §7's
framing of White Cell as instructional designer rather than neutral referee. This is the
domain document FS-106 (White Cell Dashboard) and future facilitation features must trace back to.

## 2. Scope

In scope: White Cell authority/visibility model, the inject mechanism, clock/pacing control,
session administration (save/resume, multiplayer session discovery). Out of scope: the content of
specific injects (that's vignette/scenario content, `docs/scenarios/` + `vignettes/`) and assessment
reporting consumed by White Cell but owned by DOM-002.

## 3. Authority and visibility model

White Cell is the only role with unrestricted god-view (`/godview`, `/eventlog`, `/save`, `/aar*`,
`/objectives` — the no-cell-binding endpoints documented in `CLAUDE.md`'s LAN trust model). This is
intentional and necessary for the instructional-designer role (MSTR-003 §7): a facilitator must be
able to see both cells' belief states *and* ground truth simultaneously to run a useful debrief and
to author injects that land correctly against the current world state.

**Design rule:** any new god-view-only capability is fine to add to the White Cell surface; any
capability that would let Red/Blue access ground truth through a back door is a fog-of-war
violation per MSTR-002 §2 invariant 3, regardless of how it's framed.

## 4. The inject mechanism

`inject_library.yaml` ships five reusable templates (debris breakup, GNSS-jam advisory, ambiguous
RPO, ground-station outage, geomagnetic storm), loaded via `InProcessSession.inject_library()` and
surfaced in the White Cell's "Build / schedule inject" panel with editable JSON and a Now/+seconds/
absolute-UTC scheduler. This is the primary lever a facilitator has to *adapt* an exercise in
real time — to introduce friction when a cell is coasting, or to clear an obstacle when a session
is running long. DOM-003 treats the inject library as a living content set: new reusable templates
should be added here (not one-off scripted into a single vignette) whenever a pattern proves useful
across multiple exercises.

**Design implication for FS-108 (candidate "Inject Authoring"):** a feature that makes inject
*authoring* easier (templated parameter forms, a preview-before-schedule step, a library browser
with search) is squarely DOM-003 territory; the underlying inject *execution* mechanism is already
engine-side and should not be duplicated.

## 5. Clock and pacing authority

White-only ⏸ Pause / ▶ Resume drives `/api/sessions/{sid}/clock` for every connected client — this
is deliberately a single point of control (server-authoritative lazy clock, P8) so that pacing
decisions are the facilitator's alone, not negotiable per-tab. Rewind/undo/branch (AAR, P7) is also
White-only. This authority model exists because pacing and time-control are pedagogical decisions
(when to let an access window play out vs. when to skip ahead) as much as technical ones.

## 6. Session administration

Save/resume, the multiplayer session discovery surface (`/api/sessions`), join-by-URL-hash, and
pop-out window layout management are White Cell administrative capabilities. These are
infrastructure-adjacent but stay under DOM-003 (not DOM-006/DOM-008) because their design questions
are facilitation questions first ("can I resume a multi-week course's exercise across sessions,"
"can I spread the console across monitors for a classroom") rather than generic platform questions.

## 7. White Cell as red-team enabler

Per R308 (Red Teaming) and R307 (Wargaming Theory), a facilitator's ability to credibly play or
steer Red (via doctrine presets in `redai.py`, or by hand) is part of what makes the Blue cell's
practice meaningful — an unconvincing or passive Red teaches a false sense of security. DOM-003
treats Red-doctrine-preset quality and variety as a White Cell tooling concern, not purely a
content concern: the facilitator needs visibility into *which* preset is driving Red and the
ability to switch or hand-tune it mid-exercise for pacing reasons (§5).

## 8. What this framework expects from new Feature Specifications

Any White-Cell-facing Feature Specification must state explicitly which authority tier it touches
(§3 visibility, §4 inject, §5 clock, §6 administration) and confirm it does not grant Red/Blue any
new god-view access. Features that primarily serve Red/Blue (even if White can also see them)
belong under DOM-001 or the relevant operational domain, not DOM-003.

## 9. Open work

- FS-108 (Inject Authoring UX) is currently only a candidate ID — not yet a written Feature
  Specification. Track in `ROADMAP.md` once scoped.
- No current mechanism exists for a facilitator to *compose* multiple inject templates into a
  scripted sequence ahead of a session (today: ad hoc, one at a time, live). Candidate future scope
  for FS-108 or a successor.

## 10. Related topics

R307 (wargaming theory — what makes a wargame's conclusions valid, informs how much White Cell
intervention is appropriate before the exercise stops teaching what it claims to), R308 (red
teaming — the doctrinal basis for why Red needs to be genuinely adversarial), DOM-001 §6
(coaching notes as White-Cell-authored just-in-time instruction, a narrower cousin of the inject
mechanism).
