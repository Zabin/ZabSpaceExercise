# Strategic Assumptions Register

> **Status:** ♻️ Living — reviewed whenever a trigger below fires, or at least whenever the GDS
> ladder or ADR set changes in a way that touches one of these assumptions.
> **Origin:** [`reviews/strategic-review-2026-07.md`](../reviews/strategic-review-2026-07.md) §1.3
> ("Hidden assumptions"), recommendation R6.1-R3. Created per
> [`reviews/architecture-update.md`](../reviews/architecture-update.md)'s disposition of that
> review.
> **Related:** [`architecture/01-concept-of-operations.md`](01-concept-of-operations.md) (GDS-01)
> §11 "Assumptions" and §13 "Open Questions" — this register consolidates and extends both rather
> than duplicating them; [`architecture/adr/ADR-0030-ai-determinism-doctrine.md`](adr/ADR-0030-ai-determinism-doctrine.md)
> (resolves A6, below).

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

`strategic-review-2026-07.md` §1.3 observed that several assumptions load-bearing across the whole
design baseline are nowhere written down as assumptions — they are simply the shape every document
takes for granted. Cheap insurance against silent assumption decay (the review's own framing):
name each one once, state what would have to change in the world for it to stop holding, and give
it a concrete review trigger so a future reader checks it deliberately rather than discovering the
drift after the fact. This register does not resolve any of these — resolving one is a design
decision (an ADR, a GDS revision, or a new capability), not a bookkeeping exercise. Where an
assumption *has* since been resolved, that is recorded here with a pointer to the resolving
document, and the entry is kept (not deleted) so the register remains a complete historical record.

## How to use this register

- **Adding an assumption:** any future review, ADR, or design-synthesis pass that surfaces a new
  load-bearing, previously-unstated assumption should add a row here, not just flag it inline in
  whatever document it was found in.
- **Reviewing an assumption:** when its trigger condition fires (a new feature ships, a new
  external dependency changes, a new research topic is authored), re-read the row and either
  reaffirm it (update "Last reviewed"), resolve it (add the resolving document, mark ✅), or open a
  formal design question if the assumption is starting to strain (a new GDS Open Question or ADR,
  not an edit to this register's own prose).
- **This register is descriptive, not binding.** It names what the baseline currently assumes; it
  does not itself authorize or forbid anything. Changing an assumption's disposition requires the
  same governance mechanism any other architectural change would (an ADR, a GDS revision, or an
  explicit project-owner decision), exactly as `strategic-review-2026-07.md`'s own ground rules
  require.

## Register

| ID | Assumption | What would have to change for it to break | Review trigger | Status |
|---|---|---|---|---|
| A1 | **The adversary is a peer bus/payload operator.** The Red model assumes an adversary who operates satellites the way Blue does; adversaries acting primarily through ground-segment attack, supply-chain compromise, commercial proxies, or launch-surge reconstitution are unrepresented. | A vignette or Red-doctrine preset is authored that assumes ground-segment-first or proxy-based Red behavior without an underlying mechanic to represent it. | Revisit when FC-11 (ground-segment-as-terrain, GDS-03 §5) or FC-04 (responsive launch/reconstitution) is scheduled. | Open — tracked, not resolved |
| A2 | **The five-D taxonomy plus the cyber exception (ADR-0011/0012) is a stable ontology of effects.** Doctrine is already re-framing around reversibility, dazzle/deny thresholds, and "protect and defend." | A new doctrine source or vignette needs an effect category the five-D + cyber-exception model cannot express. | Revisit if/when a research encyclopedia update (R1xx/R2xx tier) documents a doctrinal effects taxonomy shift. | Open — tracked, not resolved |
| A3 | **Custody is built from nationally-owned sensors plus a national mock SSN** (`build-spec/08-ssn.md`); commercial feed explicitly deferred (`FUTURE-WORK.md` §7). | A commercial SDA feed is added to the mock SSN (recommendation R11). | Revisit when R11/FC-10's "thin end" (commercial feed) ships — see GDS-02's "Candidate future external systems" table, commercial SDA/services row. | Open — tracked, not resolved |
| A4 | **Human-speed decision loops.** The 1.5 s HTTP-polling transport and plan-first-at-next-window cadence assume all decision-makers are humans; machine-speed play (AI operators, autonomous spacecraft behaviors) breaks the pacing assumptions, not the engine. | FC-01 (AI-supported planning), FC-02 (adaptive AI-Red), or FC-03 (on-board autonomy levels) reaches design. | Revisit when any of FC-01/02/03 is scheduled past "Current Release" status in `strategic-review-2026-07.md` Part 2. | Open — tracked, not resolved |
| A5 | **The facilitator is the adjudication authority for everything the engine doesn't model** (ADR-0017). Sound for PME; limiting for unattended experimentation campaigns (batch runs, Monte Carlo over seeds) where no human White Cell exists. | The headless Monte Carlo harness (R8/IN-02/FC-14) ships and is used for unattended runs. | Revisit when R8 ships — confirm whether unattended-run adjudication needs its own rule set or can rely on ROE dials alone. | Open — tracked, not resolved |
| A6 | **Determinism and AI integration are compatible without a stated doctrine.** | — | — | ✅ **Resolved** by [`ADR-0030`](adr/ADR-0030-ai-determinism-doctrine.md): non-deterministic components must stay outside `spacesim/engine/` and enter only via ordered, logged `SessionAPI` events. |
| A7 | **TLE/Space-Track remains the exchange format and catalog source.** TLE is a legacy format being displaced by CCSDS OMM; Space-Track access policy is a single external dependency with no stated fallback beyond manual entry. | Space-Track changes its access policy, or a CCSDS OMM migration becomes necessary for a new data source. | Revisit if Space-Track access changes (already named as a risk in GDS-01 §12) or if a commercial SDA feed (A3) is added that natively speaks OMM. | Open — tracked, not resolved |
| A8 | **The training audience is CAF/allied space operators in facilitated PME settings.** Self-paced individual training, distributed cohorts, and non-space audiences (joint planners consuming space effects) are out of the assumed audience but inside plausible demand. | A coalition (FC-09/R14), multi-domain (FC-12/R23), or self-paced/AI-Red-facilitated (FC-02) feature is scheduled that serves one of these excluded audiences. | Revisit when R14 or R23 is scheduled past "Future Release." | Open — tracked, not resolved |
| A9 (new) | **"Everyone in the room is on the same team" (ADR-0015).** The LAN trust model is cooperative-only; true until the first multi-institution or partner-nation use. | A distributed/multi-site or partner-nation exercise is planned (per R19's "before the first multi-site request"). | Revisit before authorizing any multi-site or cross-institution session — see R19's security-growth-path recommendation. | Open — tracked, not resolved |
| A10 (new) | **"The encyclopedia will be finished."** A standing intention with a systemic sourcing/scope defect (GAP-13) and no completion forcing-function. | The encyclopedia is cited externally (to a sponsor, partner, or academic reviewer) before GAP-13 (R1) is closed. | Revisit before any external citation of `docs/research/encyclopedia/`; R1 names this as a gate condition. | Open — tracked, not resolved |
| A11 (new) | **"The build-spec can remain deprecated-but-load-bearing indefinitely."** GDS-06–10 are scaffold-only, so NFRs, data model, UI architecture, and API currently have no authoritative statement at all — strictly worse than a stale one. | GDS-06 (Non-functional Requirements) is authored, per `architecture/INDEX.md` §1's stated next step. | Revisit as each of GDS-06–10 is authored; retire this row once GDS-10 closes. | Open — tracked, not resolved |
| A12 (new 2026-07-04) | **Training-artifact currency is enforceable procedurally.** The training-corpus elevation (MSTR-001 §2; GDS-00/GDS-01 same-dated sections) makes manuals/vignettes co-equal with code, but the currency mechanism — the `training/15` traceability matrix plus prose hooks in pipeline stages 08/09/10 and the dedicated training skills — is discipline-based: no automated gate fails when a manual section or learning-path rung goes stale against shipped behavior. The vignette playbooks are the one machine-verified slice (`spacesim/tests/test_vignette_tutorials.py`). | A release ships with a manual section or vignette that documents behavior the code no longer has — i.e., the procedural hooks demonstrably missed a drift. | Revisit at the first `10-integration-review` doc-coherence pass and at each release GO; if drift is found, open a design question on automating staleness detection (extend the playbook-test pattern to manual `Sources:` anchors). | Open — tracked, not resolved |

## Related

[`reviews/strategic-review-2026-07.md`](../reviews/strategic-review-2026-07.md) §1.3, §4.10;
[`reviews/architecture-update.md`](../reviews/architecture-update.md);
[`architecture/01-concept-of-operations.md`](01-concept-of-operations.md) §11, §13;
[`architecture/adr/ADR-0030-ai-determinism-doctrine.md`](adr/ADR-0030-ai-determinism-doctrine.md).
