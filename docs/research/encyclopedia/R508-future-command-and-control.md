# R508 — Future Command and Control

> **Document ID:** R508
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R502](R502-autonomy-in-space-operations.md), [R507](R507-autonomous-planning-systems.md)
> **Referenced By:** —
> **Produces:** forward-looking context for how the simulator's existing CellController/SessionAPI architecture would need to evolve if a future C2 concept (distributed, autonomy-integrated) were ever modeled
> **Feature Mapping:** any future LAN-multiplayer or session-architecture evolution touching `spacesim/session/`
> **Related Topics:** [R502](R502-autonomy-in-space-operations.md) (Autonomy in Space Operations), [R507](R507-autonomous-planning-systems.md) (Autonomous Planning Systems), the
> existing `spacesim/session/` architecture (`SessionManager`, `CellController`, `SessionAPI`) this
> topic's future-C2 concepts would have to extend
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A DARPA/DoD sources — see §3 Sources)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** neither in-world AI nor coding-agent practice directly — forward-looking
architectural context informed by [R502](R502-autonomy-in-space-operations.md)/[R507](R507-autonomous-planning-systems.md)'s AI-adjacent concepts.

## 1. Purpose

Real C2 (command and control) doctrine is evolving toward more distributed, resilient architectures
that anticipate higher autonomy and AI integration at the edge (e.g. resilient mesh C2 designed to
keep functioning if a central node is degraded). This topic gives the implementer forward-looking
context on that evolution, primarily to inform whether/how the existing `spacesim/session/`
architecture (already LAN-multiplayer-capable per P8) would need to evolve if a future vignette
concept wanted to model a degraded or distributed-C2 scenario explicitly.

## 2. Scope

Covers: the centralized-vs-distributed/resilient C2 doctrinal distinction (DARPA Mosaic Warfare, DoD
JADC2) as it applies to (a) this simulator's own `spacesim/session/` infrastructure design and (b) a
vignette's in-fiction C2 architecture as a teachable theme — and the requirement to keep those two
uses distinct. Does **not** cover: the autonomy-degree vocabulary a distributed C2 node's own
decision latitude would use ([R502](R502-autonomy-in-space-operations.md)'s job), the planning-system
question of what an autonomous C2 node would actually compute
([R507](R507-autonomous-planning-systems.md)'s job), or the cross-domain integration question
generally ([R505](R505-multi-domain-operations.md)'s job, referenced here only for its shared JADC2
source).

## 3. Concepts

**Centralized vs. distributed/resilient C2.** Centralized C2 concentrates decision authority at one
node (vulnerable to that node's loss — a clean real-world COG, [R309](R309-center-of-gravity-analysis.md)); distributed/resilient C2
spreads decision authority so the system degrades gracefully if any single node is lost. DARPA's
**Mosaic Warfare** concept, publicly outlined by the Strategic Technology Office in 2017, is the named
U.S. defense-research articulation of this shift: platforms are "decomposed" into smaller functional
nodes forming a networked, resilient "kill web," with **Distributed Battle Management (DBM)** and
**Resilient Synchronized Planning and Assessment for the Contested Environment (RSPACE)** as the
specific programs addressing distributed battle-management C2, and an explicit expectation that
Mosaic-force elements will be "more autonomous, expendable, and short-lived" than current systems
([DARPA, "Strategic Technology Office Outlines Vision for 'Mosaic Warfare,'" 2017](https://www.darpa.mil/news/2017/sto-mosaic-warfare)).
The existing engine's `ground_modem`/`seize_c2` cyber vector ([R116](R116-cyber-operations-against-space-systems.md)) and the COG framing ([R309](R309-center-of-gravity-analysis.md)) already
implicitly model the *vulnerability* of centralized C2; a future vignette explicitly themed around
this tradeoff (Blue choosing centralized vs. distributed C2 architecture as a design decision within
the scenario) does not exist today.

**C2 architectures anticipating AI/autonomy integration.** Future C2 doctrine increasingly assumes
some nodes in the C2 architecture are autonomous decision-makers ([R507](R507-autonomous-planning-systems.md)) rather than purely human
— the DoD's own [JADC2 strategy](https://media.defense.gov/2022/Mar/17/2002958406/-1/-1/1/SUMMARY-OF-THE-JOINT-ALL-DOMAIN-COMMAND-AND-CONTROL-STRATEGY.PDF)
(already cited at [R505](R505-multi-domain-operations.md) §3 for its cross-domain framing) states its
"human enterprise" line of effort explicitly addresses how personnel and automated decision aids
interoperate within the C2 architecture, not just across it. This raises a structural question
distinct from any single autonomous-feature's design ([R501](R501-human-ai-teaming.md)-[R507](R507-autonomous-planning-systems.md)):
who/what is authorized to issue an order, and does the existing engine's `Order`/`OrderSystem`
([`engine/orders.py`](../../../spacesim/engine/orders.py)) model assume a human always originates an order, or could a future autonomous
node originate one within the same system.

**The existing `SessionManager`/`CellController`/`SessionAPI` architecture as today's C2 model.**
The current architecture (server-authoritative lazy clock, per-session RLock, fog-of-war at the
`CellController` boundary, P8's LAN multiplayer) is itself a real C2 architecture choice — a single
authoritative server is closer to centralized C2 than a Mosaic-style distributed/resilient one; this
is an appropriate and deliberate choice for a hot-seat/LAN training tool (simplicity, determinism),
but a future vignette wanting to *teach* the centralized-vs-distributed C2 tradeoff would need to
model that tradeoff narratively/mechanically within the scenario, not by changing the engine's own
session architecture to actually become distributed infrastructure.

**Resilience and graceful degradation as a doctrinal concept, distinct from this engine's own
infrastructure resilience.** Real C2 resilience doctrine (surviving node loss without total mission
failure, the DARPA Mosaic Warfare rationale above) is a candidate *content* theme (a vignette modeling
Blue's ground-segment C2 node being denied, [R116](R116-cyber-operations-against-space-systems.md)/[R309](R309-center-of-gravity-analysis.md), and testing whether Blue's remaining force can still accomplish the mission) — this
is achievable today using existing mechanics (cyber/jam denial of a ground station, [R107](R107-ground-segment-operations.md)) without any
new engine feature; the distinction is doctrinal framing of existing capability, not new capability.

### Sources

- *DARPA, "Strategic Technology Office Outlines Vision for 'Mosaic Warfare'"* (2017) —
  [live](https://www.darpa.mil/news/2017/sto-mosaic-warfare)
  · [snapshot](https://web.archive.org/web/2026*/https://www.darpa.mil/news/2017/sto-mosaic-warfare)
  · accessed 2026-07-02.
- *U.S. Department of Defense. Summary of the Joint All-Domain Command and Control (JADC2) Strategy*
  (signed March 2022) — [live](https://media.defense.gov/2022/Mar/17/2002958406/-1/-1/1/SUMMARY-OF-THE-JOINT-ALL-DOMAIN-COMMAND-AND-CONTROL-STRATEGY.PDF)
  · [snapshot](https://web.archive.org/web/2026*/https://media.defense.gov/2022/Mar/17/2002958406/-1/-1/1/SUMMARY-OF-THE-JOINT-ALL-DOMAIN-COMMAND-AND-CONTROL-STRATEGY.PDF)
  · accessed 2026-07-02. *(Same source cited at [R505](R505-multi-domain-operations.md) §3 for its cross-domain framing; cited
  here specifically for its human-enterprise/automation-interoperation line of effort.)*

## 4. Operational Context

Future C2 doctrine (distributed/resilient architectures anticipating autonomy integration) is an
active area of real military C2 modernization discourse — DARPA's Mosaic Warfare concept (2017-
present) and DoD's JADC2 strategy (signed 2022) are both live, funded programs, not speculative
theory. This simulator's own session architecture already embodies a (deliberate, appropriate-for-its-
purpose) centralized C2 choice, which makes this topic primarily useful for distinguishing "the
engine's own infrastructure design" from "a vignette's in-fiction C2 architecture as a teachable
doctrinal theme," two things easy to conflate.

### Sources

Uses the same sources cited inline in §3 (DARPA Mosaic Warfare 2017; DoD JADC2 Strategy 2022); no
additional sources introduced in this section.

## 5. Implementation Guidance

- **A vignette wanting to teach the centralized-vs-distributed-C2 resilience tradeoff can do so today
  using existing mechanics** (a ground-segment C2 node denial via cyber/jam, [R107](R107-ground-segment-operations.md)/[R116](R116-cyber-operations-against-space-systems.md), testing
  whether Blue's force degrades gracefully — the Mosaic Warfare "kill web" resilience concept, §3, is
  the doctrinal framing to draw on) — this requires vignette-authoring and doctrinal framing,
  not a new engine feature.
- **Do not conflate the engine's own session architecture (`SessionManager`/`CellController`/
  `SessionAPI`) with an in-fiction C2 concept a vignette is teaching** — the former is this project's
  infrastructure design (appropriately centralized for a training tool); the latter is scenario
  content.
- **If a future feature ever lets an autonomous in-world entity ([R507](R507-autonomous-planning-systems.md)) originate an `Order`, check
  whether [`engine/orders.py`](../../../spacesim/engine/orders.py)'s `OrderSystem` model implicitly assumes a human originator** and
  document the assumption explicitly before building on top of it — per JADC2's human-enterprise line
  of effort (§3), this is exactly the kind of human/automation-interoperation question real C2
  modernization efforts have had to make explicit rather than leaving implicit.

## 6. Feature Mapping

Any future LAN-multiplayer or session-architecture evolution, and any future vignette explicitly
themed around C2-resilience doctrine, are the consumers; no specific feature is currently planned.

## 7. Related Topics

[R502](R502-autonomy-in-space-operations.md) (Autonomy in Space Operations), [R507](R507-autonomous-planning-systems.md) (Autonomous Planning Systems), [R505](R505-multi-domain-operations.md) (Multi-Domain
Operations, sharing the JADC2 source), `spacesim/session/`'s existing architecture.
