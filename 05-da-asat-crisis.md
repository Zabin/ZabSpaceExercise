# Vignette 5 — Direct-Ascent ASAT Crisis & Escalation

**Domains:** Orbital warfare (kinetic), escalation management · **Duration:** ~60 min ·
**Red profile:** selectable · **Difficulty:** Advanced

## Premise
A crisis is escalating. One side is considering — or has just employed — a **direct-ascent
kinetic ASAT** against a satellite in LEO. The vignette centers on the **decision and its
consequences**: the debris field that follows, the unambiguous and attributable nature of the
act, the political/coalition fallout, and the risk that the debris denies the orbital regime to
*both* sides (Kessler-style mutual denial). This is the escalation-control teaching set-piece.

## Learning objectives
1. Kinetic ASAT is **non-reversible, overt, attributable, and debris-generating** — the top of
   the escalation ladder, not a routine tool.
2. **Debris is indiscriminate**: a strike to deny the adversary an orbital regime can deny it
   to yourself and to neutral/commercial actors — a form of mutual denial.
3. Attribution here is *easy* (unlike RPO/EW), so the political cost lands immediately.
4. There are almost always **reversible alternatives** (EW, cyber, dazzle, RPO) that achieve
   much of the effect without the debris and escalation — recognizing them is the lesson.

## Order of battle (sketch)
**Blue & Red:** each has a small mixed constellation in LEO (ISR, SATCOM) plus a **DA-ASAT
capability** (mobile launcher) that may or may not be authorized. Both have ground SDA to track
the resulting debris. Neutral/commercial LEO assets present in the same shells.

## Key tunable parameters
| Parameter | Default | Effect |
|---|---|---|
| `who_strikes_first` (White) | red | Sets which side faces the decision/consequence first |
| `kinetic_authorized_red` | true | Whether Red may employ DA-ASAT |
| `kinetic_authorized_blue` | false | Whether Blue may respond in kind |
| `target_altitude` | 700 km | Higher altitude → longer-lived, wider debris field |
| `debris_model_severity` | realistic | How aggressively debris threatens nearby assets |
| `political_cost_scaling` | high | Magnitude of coalition/UN/economic consequence injects |
| `reversible_alternatives_offered` | true | Whether the UI surfaces non-kinetic options at the decision |

## Sample injects
- `T+00:05` Intelligence indicates the opponent is preparing a DA-ASAT launch (decision pressure).
- On strike: `inject_debris` spawns a debris field at `target_altitude`; `political_consequence`
  fires (coalition condemnation, neutral-asset operators demand answers).
- `T+strike+20m` Debris conjunction warnings threaten the striker's *own* LEO assets.

## Victory conditions
- **Both sides:** This vignette is scored less on "winning" and more on **escalation
  management** — achieving the objective at the lowest rung of the ladder, preserving the
  orbital commons, and avoiding self-defeating debris. White Cell/AAR evaluates the decision
  quality.

## Notes for Claude Code
Implements the **debris-field model** (coarse in v1: a spawned hazard region with a conjunction
risk per asset per orbit) and the **political-consequence inject** chain. The decision UI should
explicitly present reversible alternatives when `reversible_alternatives_offered` is true so the
lesson is built into the interface.
