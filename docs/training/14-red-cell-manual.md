[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Traceability matrix](15-manual-traceability.md)

## 14. Red cell manual

The role-scoped manual for a **Red cell operator** — the adversary commander who denies, degrades,
and (when ROE permits) destroys Blue's space capability while protecting Red's own assets under
fog-of-war. Every section carries a stable ID (`RED-n`) cross-referenced both directions in
[`15-manual-traceability.md`](15-manual-traceability.md). Red and Blue share the same mechanics;
this manual frames them from Red's offensive posture, and defers to the shared concept modules
rather than duplicating them. The mirror-image defensive framing is
[`13-blue-cell-manual.md`](13-blue-cell-manual.md).

### RED-1 · Your view: fog-of-war

You see **only Red's own assets** at true position, plus whatever Red's sensors have detected —
Blue's objects appear only as **tracks** with a growing uncertainty volume, never as ground truth.
The filter is enforced server-side at the `SessionAPI`/`CellController` boundary. Read your
**Mission brief** (auto-opens on load; View ▾ → Mission brief) for situation, mission, forces,
threat picture, ROE, and success criteria — Red's brief never reveals Blue's hidden dispositions
and vice versa.

> **Sources:** `spacesim/session/controller.py` (fog filter) · `spacesim/session/scene.py` ·
> `GET /api/sessions/{sid}/brief/red` · [`02-interface.md`](02-interface.md) §"A player cell"

### RED-2 · Plan-first commanding

You **plan** commands that execute at the next valid window — never instant action on perfect
knowledge. A command reaches a satellite via **ground-station uplink**, **ISL relay**, or a
**stored program**, whichever is soonest. Orders queue with their window and delivery path and are
**cancellable until they uplink**; up to four ride one pass. Sequencing your effects to land inside
the same access window is Red's tempo problem.

> **Sources:** `spacesim/engine/orders.py` (`OrderSystem`, delivery paths) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Plan-first commanding"

### RED-3 · Previews before you commit

1. **Dry-run validity** — the green ✓ / red ✗ line; a blocked action tells you *why* (missing
   window, weapons-quality, or ROE gate).
2. **Consequence preview** — severity, escalation weight, reversibility, debris risk, and
   **attribution**: Red's escalation-management dashboard. A reversible EW/cyber effect keeps you
   below the threshold a kinetic strike crosses.
3. **Verb assistants** — `maneuver` (six modes, live Δv), `observe` (beam mode + look angle), `jam`
   (modulation/power/bandwidth with an on-map denial footprint).

*See also: [BLU-3](13-blue-cell-manual.md#blu-3--previews-before-you-commit) — the same preview
mechanics from Blue's side.*

> **Sources:** `spacesim/engine/orders.py` `dry_run()` · `POST /preview/consequence` ·
> `spacesim/engine/{maneuver,isr,jam}.py` · [`02-interface.md`](02-interface.md) §"Order-composition assistants"

### RED-4 · Build a targeting picture with SDA

You can only deny what you can see. **Task scarce sensors** to detect, track, and characterize
Blue's assets; a good report raises track confidence and shrinks uncertainty until it reaches
**weapons-quality**, which **unlocks** the engagement actions the gate was blocking. Sensors do one
thing at a time (contention pushes the second task to a later pass), and custody **decays** between
looks — re-task before a firing window or the gate re-locks.

*See also: [BLU-4](13-blue-cell-manual.md#blu-4--sda-task-sensors-build-custody-unlock-actions) —
the same tasking→custody→unlock loop, applied to defense rather than targeting.*

> **Sources:** `spacesim/engine/custody.py` (weapons-quality gate) · `spacesim/engine/access.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"SDA sensor tasking"

### RED-5 · The five D's: choose your effect

Effects fall in five categories mapped to five D's — **deceive / disrupt / deny / degrade /
destroy** — resolved by the `EffectResolver` seam. Four are **window-gated** (you need the access
channel: `jam_footprint`, `weapon_engagement`, `sensor_observation`, `rpo_proximity`). Prefer the
**reversible** effects (EW, proximity) to hold escalation down; reach for kinetic only when ROE
authorizes it and you accept the debris and attribution cost the consequence preview shows you.

- **Jam** — barrage / spot / sweep / deceptive modulation; the assistant computes the effective
  denial radius and draws the orange footprint on the 2D map.
- **Engage** (kinetic) — closing geometry, salvo Pₖ, debris-cone estimate; gated on
  weapons-quality custody *and* `red_kinetic_authorized` ROE.
- **RPO** — co-orbital proximity to inspect, shadow, or threaten.

> **Sources:** `spacesim/engine/effects.py` (5 D's) · `spacesim/engine/{jam,engage}.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) · [`../research/INDEX.md`](../research/INDEX.md)

### RED-6 · Cyber: the off-pass wildcard

Cyber is the **exception** — not window-gated. With a modeled access vector it resolves any time
against `{access_vector, success_prob, persistence, patchable}` subject to Blue's cyber posture.
This is Red's fastest, hardest-to-attribute lever (the SATCOM/Viasat-style lesson): you can act
between passes when Blue is watching the wrong timeline. A **persistent** unpatched vulnerability
keeps re-safing the target through its recovery attempts.

*See also: [BLU-9](13-blue-cell-manual.md#blu-9--cyber-cuts-both-ways) — the same mechanic from the
defender's side.*

> **Sources:** `spacesim/engine/cyber.py` (`VECTORS × PAYLOADS`, `attribution_score`) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Cyber — the off-pass exception"

### RED-7 · Manage your own force

Red's satellites have the same **bus** SOH and safe-mode model as Blue's — Blue can hit back.
Watch the fleet rail's worst-subsystem dots and alarm feed, diagnose incoming attacks from
telemetry signatures (same table as [`13-blue-cell-manual.md`](13-blue-cell-manual.md) §BLU-6), and
run the multi-pass recovery chain (patch the root cause or the asset re-safes).

> **Sources:** `spacesim/engine/bus.py` · `spacesim/engine/recovery.py` ·
> `spacesim/engine/telemetry.py` · [`05-core-concepts.md`](05-core-concepts.md) §"Bus state-of-health"

### RED-8 · Doctrine profiles and the COA vignettes

When Red is played by AI (or you want a doctrinal template), the doctrine presets
`china_integrated`, `russia_ew_first`, and `generic` prioritize Red's COA differently. The five
Red COA vignettes (RC-01 Layered Denial, RC-02 Cyber-First Access Denial, RC-03 Progressive
Escalation, RC-04 High-Altitude ASAT, RC-05 Allied Targeting) are built around these patterns —
study them as Red's playbook of campaign shapes.

> **Sources:** `spacesim/session/redai.py` · [`06-the-vignette-library.md`](06-the-vignette-library.md) ·
> [`11-vignette-playbooks.md`](11-vignette-playbooks.md)

### RED-9 · Win the vignette

Your objectives and the gates that block the rest (window / weapons-quality / ROE) are laid out
move-by-move in the per-cell playbook. Read your Red row there, sequence your effects against the
crisis window in your Mission brief, and keep the consequence preview in view to stay on the right
side of the escalation line.

> **Sources:** [`11-vignette-playbooks.md`](11-vignette-playbooks.md) ·
> `spacesim/tests/test_vignette_tutorials.py` · `GET /api/vignettes/{id}/tutorial`

---
