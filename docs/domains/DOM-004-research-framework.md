# DOM-004 — Research Framework

> **Document ID:** DOM-004
> **Version:** 1.0
> **Status:** 🚧 In progress
> **Dependencies:** MSTR-001, MSTR-007
> **Referenced By:** DOM-002, DOM-005, FS-301
> **Produces:** the research encyclopedia program (R100-R500, see MSTR-007), FS-301 Research Analytics
> **Feature Mapping:** FS-301
> **Related Topics:** [`docs/FUTURE-WORK.md`](../FUTURE-WORK.md) §12, MSTR-007 (Research Philosophy), DOM-005 (Validation)

[↑ Docs index](../INDEX.md)

## 1. Purpose

DOM-004 governs the **research program** in the broad sense: both (a) the research-encyclopedia
corpus that exists to inform implementation (MSTR-007's subject) and (b) the simulator's potential
use as an actual research instrument — e.g., a PME institution running controlled studies on
decision-making using SpaceSim as the experimental apparatus. MSTR-007 is the philosophy/shape of
(a); this document is the umbrella that also covers (b), and the boundary between them.

## 2. Scope

In scope: the relationship between the encyclopedia corpus and instrument-grade research use; what
FS-301 (Research Analytics) would need to support genuine human-subjects or quasi-experimental
research. Out of scope: the encyclopedia's internal structure (MSTR-007 owns that fully), and
statistical validity methodology specifics (DOM-005/R400 own that).

## 3. Two distinct "research" activities, not to be conflated

| Activity | Purpose | Owning document |
|---|---|---|
| **Encyclopedia authoring** | Equip coding agents with domain knowledge to implement correctly. | MSTR-007 |
| **Instrument-grade research** | Use SpaceSim itself to study questions about human decision-making, training effectiveness, or wargaming methodology — e.g., "does fog-of-war severity affect escalation rate." | DOM-004 (this document) + DOM-005 |

The risk this distinction guards against: encyclopedia content (necessarily simplified, framed for
implementation guidance) being mistaken for a validated research finding, or conversely a research
question being answered casually from "what the docs say" rather than actual data collected from
exercise runs. R401-R413 (Research Methods tier) gives the methodological vocabulary to keep these
separate.

## 4. What SpaceSim offers as a research instrument

Because the engine is deterministic and the eventlog is the full record of a run (MSTR-002 §2),
SpaceSim has properties a research instrument needs and many ad hoc training tools lack:

- **Reproducibility** — a given seed + vignette + identical operator inputs always replays
  identically, so a researcher can isolate the effect of one varied input.
- **Full behavioral trace** — every order, window check, and effect resolution is in the eventlog;
  nothing needs to be hand-coded by an observer in real time.
- **Controlled manipulation surface** — vignette YAML, doctrine presets, and Red AI parameters are
  data, not code (MSTR-002 §2 invariant 6), so a researcher can vary a single parameter (e.g.
  custody decay rate, ROE strictness) across conditions without engine changes.

## 5. What it does not yet offer (gap statement)

There is currently no purpose-built data-export or cohort-management layer — a researcher today
would have to script directly against `eventlog`/`save` artifacts. FS-301 (Research Analytics) is
the candidate Feature Specification to close this gap: structured export of the six DOM-002 §4
measurement dimensions across many runs/cohorts, with metadata (vignette, seed, condition labels)
attached.

## 6. Authorization and ethics boundary

Any future feature enabling human-subjects research (e.g., collecting de-identified trainee
performance across institutions) is **out of scope for this documentation-expansion effort** and
must not be assumed authorized merely because this framework describes the capability gap. Per
MSTR-006 §3, instrument-grade research features are 🅿️ by default pending explicit go-ahead, and
any human-subjects element additionally requires the institution's own IRB/ethics process — this
framework does not substitute for that and should say so explicitly in any FS-301-derived
Implementation Package.

## 7. Relationship to the encyclopedia's authoring cadence

The encyclopedia (MSTR-007 §6) is itself authored under a research-methods-like discipline (scoped
index before content, capped batch size) even though it isn't a human-subjects research activity —
this is a deliberate borrowing of rigor (plan before you execute, review before you scale up) from
DOM-004's research-methods half, applied to a documentation-engineering task.

## 8. What this framework expects from FS-301

FS-301 must explicitly tag itself as supporting DOM-004 §4/§5 (instrument-grade research), state
the export schema's relationship to DOM-002 §4's six measurement dimensions, and carry an explicit
non-goal statement matching §6 (no human-subjects feature is in scope without separate
authorization and ethics review).

## 9. Related topics

MSTR-007 (full encyclopedia philosophy), DOM-005 (Validation — the methodological rigor a
DOM-004-enabled research use would need to apply to its own conclusions), R401-R413 (the concrete
methods vocabulary: hypotheses, controls, Monte Carlo, sensitivity analysis, V&V).
