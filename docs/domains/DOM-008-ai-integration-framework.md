# DOM-008 — AI Integration Framework

> **Document ID:** DOM-008
> **Version:** 1.0
> **Status:** 🚧 In progress
> **Dependencies:** MSTR-001, MSTR-002, MSTR-006
> **Referenced By:** DOM-003, DOM-009, FS-111, FS-301, R501-R509
> **Produces:** the constraints governing both (a) Red AI doctrine presets and (b) coding-LLM-agent use on this repository
> **Feature Mapping:** N/A as this domain's own primary claim — cross-cutting; touches
> `redai.py`-derived features and the documentation-authoring process itself. `FS-111` (AI-Red
> Doctrine Automation, new 2026-07, split out of FS-106 per `docs/feature-planning/05-feature-
> review.md` Finding F-03) is exactly the `redai.py`-derived feature this line anticipated — it
> cites this domain as a related, cross-cutting input alongside its primary grounding in DOM-009,
> not as this domain's own owned Feature.
> **Related Topics:** [`spacesim/session/redai.py`](../../spacesim/session/redai.py) (code, referenced not duplicated),
> R501-R509 (Future Operations tier), MSTR-006 (AI authoring constraints)

[↑ Docs index](../INDEX.md)

## 1. Purpose

Two genuinely distinct AI-integration surfaces exist in this program, and DOM-008 is the umbrella
that keeps them from being conflated: **(a)** AI *within the simulated world* — Red doctrine
presets (`redai.py`) and any future autonomous Blue/White assistance, and **(b)** AI *building the
simulator* — coding LLM agents (like the one authoring this very document) implementing features
from this documentation tree. Both are "AI integration," but they have different correctness
criteria, different audiences, and different risk profiles.

## 2. Scope

In scope: design principles for in-world Red AI behavior; the standing constraints on coding-agent
use established elsewhere in this corpus (MSTR-006 §4, the CLAUDE.md durable guide) restated here
for discoverability; the boundary between the two. Out of scope: re-deriving MSTR-006's authoring
rules in detail (cite, don't duplicate) and any specific future-operations doctrine content (R500
tier owns that).

## 3. In-world AI: Red doctrine presets

`redai.py`'s doctrine presets exist to make Red a credible, doctrinally-flavored adversary without
requiring a live human Red player for every exercise (DOM-003 §7, R308 Red Teaming). DOM-008's
design principles for this surface:

- **Presets are data-parameterized behavior, not bespoke code paths per vignette** — consistent
  with MSTR-002 §2 invariant 6 (content is data). A new Red posture should be expressible as a new
  preset/parameter set, not a new branch in engine code.
- **Determinism is non-negotiable here too.** Red AI decisions consume the seeded RNG
  (`SeededRng`), never an unseeded source — MSTR-002 §2 invariant 1 applies to Red's "thinking" as
  much as to physics.
- **Red AI should be legible to White Cell**, not a black box — a facilitator needs to know
  *which* preset is active and roughly what behavior to expect, both for pacing (DOM-003 §5) and
  for debrief honesty (you can't credit/fault Blue's read of Red's intent if White itself can't
  characterize what Red was actually doing).

## 4. Future in-world AI: autonomy and human-AI teaming (forward-looking, R500-tier)

`docs/FUTURE-WORK.md`-tracked and R500-tier topics (autonomous planning, machine reasoning, future
C2) describe a horizon where Blue or White might be assisted by an AI planner/advisor inside the
exercise itself — e.g., an AI-suggested COA, an AI custody-fusion assistant. DOM-008's standing
position: **any such feature must preserve the plan-first invariant (MSTR-002 §2 invariant 4) and
the educational philosophy's "judgment must be practiced, not delegated" stance (MSTR-003 §2)** —
an AI that *decides* for the trainee defeats the tool's purpose, even if it would "win" more
often. An AI *advisor* that surfaces information or options (without acting) is the only shape this
should take without further explicit design review; treat anything beyond that as 🅿️ pending
authorization per MSTR-006 §3.

## 5. Coding AI: this repository's documentation-driven development model

The standing rule (MSTR-001 §2, MSTR-006 §4): a coding LLM agent should be able to implement a
feature from a Feature Specification + Implementation Package without inferring intent from code.
DOM-008 adds the in-world/out-of-world boundary explicitly: **a coding agent authoring or extending
`redai.py` doctrine presets is doing (b) acting on (a)** — i.e., when an agent implements a new Red
posture, it is implementing an Implementation Package (governed by MSTR-006 §8's no-code-in-docs
rule and ordinary engineering practice), not authoring a "smarter" AI outside the deterministic,
seeded-RNG constraint. The two roles must not be blurred: a coding agent does not get to relax
determinism "because it's just the AI opponent."

## 6. What this framework expects from R500-tier documents and any future FS touching AI

Every R501-R509 topic must explicitly tag, in its Implementation Guidance section, whether the
concept it describes applies to in-world AI (§3-4) or coding-agent practice (§5) or both, since
conflating them is the most likely failure mode for this tier (a topic on "machine reasoning" could
easily drift into discussing LLM-agent practice when the simulator's actual gap is an in-world
planning assistant, or vice versa). Any Feature Specification proposing an in-world AI capability
must cite §4's plan-first/advisor-only constraint explicitly and flag itself 🅿️ if it goes beyond
advisory.

## 7. Related topics

R308 (red teaming — doctrinal basis for §3), R501 (human-AI teaming), R505-R509 (autonomous
planning / machine reasoning / future C2 — the forward-looking content §4 constrains), MSTR-006 §4
(AI authoring constraints, the source of truth §5 restates for discoverability).
