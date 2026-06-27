# R116 — Cyber Operations Against Space Systems

> **Document ID:** R116
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](R103-satellite-command-and-control.md)
> **Referenced By:** [R115](R115-electronic-warfare-in-space-operations.md), FS-105
> **Produces:** implementation constraints for [`engine/cyber.py`](../../../spacesim/engine/cyber.py), the cyber exception in [`engine/orders.py`](../../../spacesim/engine/orders.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R103](R103-satellite-command-and-control.md) (Satellite C2 — the chain cyber bypasses), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic Warfare — the
> window-gated contrast), MSTR-002 §2 invariant (the five-D taxonomy's stated cyber exception)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Cyber is the one effect category the simulator explicitly does **not** window-gate — it resolves
against the target's posture and the attack's vector/dwell at the moment it's issued, not at the
next access window. This topic gives the implementer the `cyber.py` model and the doctrinal reason
for the exception so a new cyber capability preserves it correctly.

## 2. Scope

Covers: the cyber exception to window-gating, the vector × payload × posture success derivation,
and attribution/patchability as scored properties. Does **not** cover: the C2 chain a `seize_c2`
payload exploits ([R103](R103-satellite-command-and-control.md)), or the window-gated EW contrast case ([R115](R115-electronic-warfare-in-space-operations.md)).

## 3. Concepts

**Cyber bypasses `ACTION_CHANNEL`'s window gate by design.** `ACTION_CHANNEL["cyber"] = None`, and
`OrderSystem._plan_cyber` schedules execution at `self.sim.clock.now` rather than searching for an
access window — modeling the real-world fact that a cyber access, once established (e.g. via a
prior supply-chain or ground-segment compromise), does not require the same line-of-sight/elevation
geometry a kinetic or RF effect does.

**Success is derived from vector × posture × dwell, not operator-typed.** Per the Jun 2026 Commands
audit (§C2), `cyber.effective_success(vector, target_posture, dwell_s)` is the sole source of
`success_prob`; the legacy raw `base_prob` operator override is removed. `vector` is mandatory —
`_validate` rejects a cyber order with no `vector` (`"no_cyber_vector"`).

**Vectors and payloads are independent axes.** `VECTORS` (`rf`/`supply_chain`/`insider`/
`ground_segment`/`ground_modem`) describe *how* access is gained, each with its own `base_success`,
`attribution_bias`, `patchable`, `detect_rate`, and `min_persistence_h`. `PAYLOADS`
(`data_exfil`/`wiper`/`spoof`/`dwell`/`seize_c2`) describe *what* the access does, each fixing
`reversible`, `escalation_weight`, and `intended_outcome`. A real cyber operation is the product of
both axes — e.g. a `ground_modem` vector with a `seize_c2` payload models the Viasat KA-SAT pattern
(24 Feb 2022: an attacker exploited a VPN-appliance misconfiguration to reach the trusted management
segment, then issued legitimate management commands to tens of thousands of residential modems
simultaneously
([Viasat, *KA-SAT Network cyber attack overview*](https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/)
([Wayback](https://web.archive.org/web/2026/https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/)))),
which is `reversible` (the safe-mode recovery chain lifts it) but high-escalation.

### Sources

- *Viasat, KA-SAT Network cyber attack overview* — [live](https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/)
  · [snapshot](https://web.archive.org/web/2026/https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/)
  · accessed 2026-06-27.

**Attribution is a scored property, not a fixed label.** `attribution_score()` exists because
attribution in cyber is graded (covert/ambiguous/overt by vector bias, modified by detection), not
binary — directly analogous to custody confidence ([R105](R105-custody-theory.md)) and DoD escalation discipline (DOM-002):
cyber attribution is itself an uncertain quantity an analyst assesses, not a ground-truth flag the
engine simply reveals.

**Patchability is the root-cause-removal lever the recovery chain depends on.** `def.patch_cyber`
sets `patched=True` on the matching `cyber_vulnerabilities` entry; the `RecoverySystem`'s
re-safe-on-persistence logic checks this — a `patchable=False` vector (e.g. `supply_chain`) cannot
be fixed by `def.patch_cyber` at all, modeling that some compromises require a harder remediation
than a single patch verb.

## 4. Operational Context

Real space-system cyber risk is dominated by ground/TT&C-segment and supply-chain compromise, not
contested-spectrum-style real-time engagement — the Viasat KA-SAT incident (the doctrinal precedent
behind `ground_modem`/`seize_c2`, see §3 Sources) is the canonical example: an attacker didn't touch
the spacecraft at all, they compromised ground management infrastructure to issue legitimate
commands. This is why cyber's access model (vector-and-posture-based, not geometry-gated) and its
`seize_c2` payload exist.

## 5. Implementation Guidance

- **A new cyber capability must add entries to `VECTORS`/`PAYLOADS`**, not bypass
  `effective_success`/`vector_params`/`payload_params` with bespoke probability logic — this
  preserves the audited vector × posture × dwell derivation.
- **Never make cyber window-gated** for a new feature — that would erase the doctrinal exception
  this topic exists to document; if a feature genuinely needs geometry-gating for an RF-delivered
  cyber payload, model the RF delivery as the `rf` vector's existing `base_success`/`detect_rate`,
  not as an access-window requirement.
- **A new payload's `reversible`/`escalation_weight`/`intended_outcome` must be fixed in the
  `PAYLOADS` table**, not operator-overridable — operator override of these fields was an explicit
  audit-driven removal (§C2); don't reintroduce it.
- **If a new vector should be patchable, ensure `def.patch_cyber`'s vector-match logic covers it** —
  an unpatchable-by-design vector (like `supply_chain`) should stay that way deliberately, not by
  omission.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any cyber-adjacent UI must make clear to
the operator that cyber resolves immediately against posture, not at a future access window.

## 7. Related Topics

[R103](R103-satellite-command-and-control.md) (the C2 chain cyber's `seize_c2` payload exploits), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic Warfare — the
window-gated contrast case), MSTR-002 (the five-D taxonomy's explicit cyber exception).
