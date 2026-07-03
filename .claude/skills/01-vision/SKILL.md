---
name: 01-vision
description: Author or refresh the project's Vision layer — the program vision (docs/master/MSTR-001-program-vision.md), the GDS-00 Vision level of the architecture ladder (docs/architecture/00-vision.md), and the strategic assumptions register (docs/architecture/strategic-assumptions-register.md) — keeping the three consistent with each other and with what the project has actually become. Use when asked "what is this project for," "update the vision," "does the vision still hold," "record a strategic assumption/pivot," or at the start of a new major increment to confirm the vision still governs before research and design work proceeds. This is the top of the pipeline: it makes purpose-level statements only — no architecture decisions (03-architecture-design-synthesis), no requirements (04-requirements-engineering), no research claims (02-research-*), no code. A vision change is the most expensive kind of change in the tree; this skill makes them deliberately, records why, and names everything downstream the change invalidates.
---

# Vision

Owns the **Vision layer** — the answer to "what is this project, for whom, and what must always be
true about it." Everything downstream (research scope, architecture, requirements, features,
packages) traces back to statements made here, which is exactly why this skill is small, slow, and
deliberate: it changes rarely, and every change it makes ripples.

## What this skill owns

| Artifact | Role |
|---|---|
| `docs/master/MSTR-001-program-vision.md` | The program vision — purpose, audience (PME wargaming), scope commitments, the authority rules other documents cite. |
| `docs/architecture/00-vision.md` (GDS-00) | The architecture ladder's Vision level — the design-facing restatement the rest of the GDS ladder builds on. Owned here, not by `03-architecture-design-synthesis` (which owns GDS-01 onward). |
| `docs/architecture/strategic-assumptions-register.md` | The explicit assumptions the vision rests on — each with its trigger ("if this stops being true, revisit X"). |

It SHALL NOT make architecture decisions, originate requirements or research claims, or edit any
downstream artifact — when a vision change invalidates downstream content, it *names* the affected
artifacts and their owning skills; the fixes run through the pipeline in order.

## Workflow

1. **Read the current Vision layer** (all three artifacts) plus `CLAUDE.md`'s load-bearing
   invariants and the project's actual current state (`ROADMAP.md` headline, the release plan).
2. **Determine the mode:**
   - **Consistency check** (default, cheap): do the three artifacts agree with each other and with
     reality? A project that shipped multiplayer while the vision still says "single-machine only"
     has vision drift — fix the record or flag the divergence, whichever direction is true.
   - **Deliberate change**: the user is pivoting scope, audience, or a commitment. Draft the
     change, record the rationale and date in the changed artifact, update the assumptions
     register (retire/add assumptions with triggers), and enumerate the downstream blast radius —
     which GDS levels, requirements, features, and packages now cite a superseded statement.
3. **Keep the three artifacts in lock-step.** MSTR-001 and GDS-00 must never disagree; where they
   share a statement, one carries it and the other points to it (per the merge decision already
   recorded in GDS-00's gate).
4. **Commit** as `docs(vision): <what changed>`.

## Quality gate

- [ ] MSTR-001, GDS-00, and the assumptions register agree — no statement contradicted between them.
- [ ] Every changed statement carries a dated rationale, not a silent rewrite.
- [ ] Every retired/added strategic assumption has a trigger condition.
- [ ] The downstream blast radius of any change is enumerated by artifact and owning skill — none
      of it edited here.
- [ ] No architecture, requirement, research claim, or code was authored.

## Pipeline position & completion summary (mandatory, every run)

This skill is **Stage 01 — Vision**, the top of the documentation-driven-development pipeline (see
[`.claude/skills/README.md`](../README.md); stages run in numeric order, and `00-pipeline-status`
reports where the project currently stands). Upstream: only the user. Downstream: the
`02-research-*` skills and `03-architecture-design-synthesis`.

End **every** invocation — consistency check, deliberate change, or blocked stop — with a chat
summary containing exactly these three parts:

1. **What changed** — artifacts touched (or "consistency confirmed, nothing changed"), assumptions
   added/retired.
2. **Recommendations** — vision drift found, assumptions whose triggers have fired, and the full
   downstream blast radius of any change (artifact → owning skill).
3. **Next step** — say explicitly what to run next and why: after a vision change, the first
   invalidated downstream stage in numeric order (usually a `02-research-*` skill for new
   grounding needs, else `03-architecture-design-synthesis` to reconcile the affected GDS levels);
   after a clean consistency check, whatever stage the current increment is actually at — run
   `00-pipeline-status` if that isn't already known.

Never end a run without naming the next step — the pipeline is driven one stage at a time, and the
user relies on each stage's summary to know what to invoke next.
