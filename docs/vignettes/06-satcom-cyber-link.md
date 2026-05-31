# Vignette 6 — SATCOM Cyber & Link Interdiction

**Domains:** Cyber, Electromagnetic warfare (link segment) · **Duration:** ~60 min ·
**Red profile:** Russia/integrated (default) · **Difficulty:** Core

## Premise
At the opening of hostilities, Red executes a **cyber attack on the ground/user segment** of a
commercial SATCOM network Blue depends on for drone control and C2 backhaul — modeled on the
Feb 2022 Viasat KA-SAT event — combined with **uplink jamming** of Blue's military SATCOM. The
distinguishing feature: **cyber is not gated by orbital passes.** A single successful access can
produce strategic effect instantly, anywhere — but depends on a modeled vulnerability and the
defender's posture, and may be a one-shot if patched.

## Learning objectives
1. The **ground and link segments are the soft underbelly** — you don't need to touch the
   satellite to defeat the capability.
2. **Cyber acts outside the pass-window logic**, making it uniquely fast and flexible — the
   counterweight is that it needs an access vector and can be patched/closed.
3. **Dependence on commercial space** is a vulnerability: the operator, not the military,
   controls the defense.
4. Resilience comes from **redundancy and disaggregation** (multiple bearers, fall-back comms).

## Order of battle (sketch)
**Blue:** Reliance on 1× commercial SATCOM network (ground modems = the attack surface) + 1×
military protected SATCOM (GEO). Drone and C2 units depend on these links. Cyber defense posture
tunable; alternate bearers (LEO constellation, HF) tunable.
**Red:** Cyber capability with a modeled access vector against the commercial ground segment,
1× SATCOM uplink jammer, optional follow-on EW.

## Key tunable parameters
| Parameter | Default | Effect |
|---|---|---|
| `red_cyber_access` | prepositioned | none / discovered-in-game / prepositioned (ready at T+0) |
| `blue_cyber_posture` | medium | Patch speed / detection; can close the vuln mid-game |
| `red_uplink_jam` | on | Denies the military SATCOM transponder during the campaign |
| `blue_alternate_bearers` | [leo_constellation] | Fall-back comms Blue can switch to |
| `commercial_operator_cooperation` | slow | How fast the commercial operator restores service |
| `attribution_difficulty` | fog | Cyber attribution is the hardest — default to fog |

## Sample injects
- `T+00:00` `fail_ground_station` / `degrade_asset`: commercial modems bricked across the
  theater (instant strategic effect, no pass required).
- `T+00:15` Red uplink jam degrades the military SATCOM fallback.
- `condition` if `blue_cyber_posture` high → `patch_cyber_vuln` can restore the commercial net
  after a delay.

## Victory conditions
- **Blue:** Maintain C2 and drone control above a threshold by surviving on alternate bearers,
  restoring service, and dispersing dependence; recognize and attribute the cyber attack.
- **Red:** Keep Blue C2/drone capability suppressed during the decisive window; remain below the
  attribution/escalation threshold that would justify a strong Blue response.

## Notes for Claude Code
This vignette validates the **cyber subsystem that bypasses access windows** — the single most
important "exception" in the engine. Model cyber as `{access_vector, success_probability,
persistence, patchable}` rather than as a geometry-gated effect. Contrast in the AAR with the
pass-gated EW jam happening alongside it.
