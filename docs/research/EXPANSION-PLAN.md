# Research Corpus Expansion Plan — 10× Roadmap

[← Research index](INDEX.md) · [↑ Docs index](../INDEX.md)

**Goal:** grow `docs/research/` from its current 8-file / 1,152-line / 0-cited-URL state into a
**~11,500-line, ~25-file, ~500-citation** corpus that any PME instructor can defend in front of
a doctrinal subject-matter expert, and that the engine's parameters can trace by file:line back
to an open-source source. "Tenfold" here is concrete and measurable — see §1.

This plan is itself a draft for review. It is not yet authorized to spend agent budget on
content production; the user picks which tiers to green-light.

---

## 1. Baseline accounting (what we are 10×-ing)

Current state, as of 2026-06:

| Metric | Today | 10× target |
|---|---:|---:|
| Files in `docs/research/` | 7 + INDEX | ~25 + INDEX |
| Total lines | 1,152 | ~11,500 |
| Cited URLs in body / Sources | **0** | ≥500 |
| Distinct primary sources | ~30 (named in Sources sections, but not linked) | ≥250 |
| Mission types with depth coverage | ~9, ≤30 lines each | ≥15, ≥200 lines each |
| Adversary actors with deep-dive | China, Russia (~50 lines each) | China, Russia, India, Iran, DPRK, France, UK, Japan, allied coalition (≥150 lines each) |
| Cross-references *from code* into research | 13 (grep-counted file references) | ≥80 — every per-domain database (`engine/jam.py`, `cyber.py`, `engage.py`, `isr.py`, `sigint.py`, future ones) cites its source-of-numbers |
| Date-stamped facts | 0 | every numeric claim carries a year |
| Update / review cadence | none | annual review marker per file |

The most embarrassing baseline metric is **zero cited URLs**. The corpus reads as one Claude
session's domain knowledge, with no traceable source-of-truth. The June 2026 commands audit
*did* produce a rigorously cited realism report (the agent output), but that work was
crystallized into the code (INTERCEPTORS database, verb cuts, PNT replacements) without being
folded back into the research corpus. Fixing that traceability gap is the single highest-value
move; it is the spine of Tier 1.

---

## 2. The five levers of expansion (multiplied → 10×)

A 10× corpus is not one file ten times longer. It is the product of five orthogonal expansions:

1. **Depth** (1.5×) — existing topics get more space and more detail.
2. **Breadth** (2×) — new topics the current corpus does not address.
3. **Citation density** (∞× from zero; ~2×-equivalent) — every numeric claim, every named system,
   every doctrinal assertion carries a linked open-source citation.
4. **Cross-linking** (1.5×) — code and build-spec parameters point at research, and research
   sections point at the code that implements them. This converts the corpus from a primer into
   a *verification layer*.
5. **Currency** (1×, ongoing) — annual review markers, dated facts, a documented refresh
   workflow.

1.5 × 2 × 2 × 1.5 × 1 ≈ **9×**, plus a non-trivial Tier 4 "strategic forward-looking" track
gets to 10×. The plan's tier structure (§4) maps each tier onto these levers.

---

## 3. Proposed file set after expansion

The existing 7 files stay (renamed for clarity where useful) and grow ~3× each. ~17 new files
land. Organized into six tracks:

### Track A — Doctrine (5 files; was 2)

| # | File | Status | Coverage |
|---|---|---|---|
| 01 | `01-doctrine-western.md` | **expand** | USSF/STARCOM doctrine (SDPP, Spacepower 2025), USAF AFDP 3-14, Joint Pub 3-14, allied (NATO, AUS, UK, JP) |
| 02 | `02-doctrine-non-western.md` | **expand** | PLA SSF/ASF (post-2024 reorg), VKS/VKO, KMNT (NK), CSO-FR, ISA-IL, ISRO |
| 02a | `02a-china-deep-dive.md` | **NEW** | PLA SSF→ASF transition, Strategic Support Force history, integrated SoS, 36th GA, NICS |
| 02b | `02b-russia-deep-dive.md` | **NEW** | VKS, RVSN, Roscosmos military integration, EW troops, Bylina/Tirada-2/Pole-21 |
| 02c | `02c-emerging-actors.md` | **NEW** | India (DRDO, Mission Shakti), Iran (IRGC ASB), DPRK (NADA), Israel (Ofeq), commercial counterspace |

### Track B — Counterspace effects & systems (7 files; was 1)

| # | File | Status | Coverage |
|---|---|---|---|
| 03 | `03-counterspace-taxonomy.md` | **expand** | The 5 D's, mapping to engine `Outcome` literals; cited per claim |
| 03a | `03a-da-asat-systems.md` | **NEW** | Per-system deep-dive (SC-19/DN-3, Nudol/A-235, SM-3, PDV-Mk2, FY-1C engagement profile). Sources the INTERCEPTORS database. |
| 03b | `03b-coorbital-rpo.md` | **NEW** | SJ-21/SJ-15, Burevestnik, Olymp-K, Luch-2, USA-270 series, GSSAP RPO ops, OOS/MEV-1/MEV-2 |
| 03c | `03c-ew-jamming.md` | **NEW** | CCS Block 10.2 (the realism research already drafted this), Tirada-2/Pole-21/Bylina, Tobol, AEHF/Milstar ECCM, processing-gain math, J/S analysis. Sources `engine/jam.py`. |
| 03d | `03d-directed-energy.md` | **NEW** | Soviet/Russian Sokol-Eshelon laser dazzle, Peresvet, Chinese Zimu-1 reports, Magnesium fluoride satellite hardening |
| 03e | `03e-cyber.md` | **NEW** | Viasat KA-SAT (full incident report), SPARTA TTPs, ROSAT 1998, NASA TDRS attacks, supply-chain compromises. Sources `engine/cyber.py`. |
| 03f | `03f-nuclear-emp.md` | **NEW** | Starfish Prime, Soviet K-3/4/5 high-altitude tests, modern EMP modeling, OST Art. IV (deferred for v1, documented for v2). |

### Track C — Orbital mechanics & physics (3 files; was 1)

| # | File | Status | Coverage |
|---|---|---|---|
| 04 | `04-orbital-mechanics-primer.md` | **expand** | Regime physics, access windows, the fidelity ladder |
| 04a | `04a-propagator-fidelity.md` | **NEW** | Kepler vs J2 vs SGP4 vs high-precision; published validation against TLE catalogs; the sim's chosen tier and its known errors |
| 04b | `04b-debris-and-conjunction.md` | **NEW** | NASA ORDEM, ESA MASTER, Cosmos 1408 debris evolution analysis, Burnt Frost (247 km → reentry months) vs FY-1C (865 km → decades). Sources `engine/engage.debris_cone_estimate` persistence regime. |

### Track D — Mission sets (4 files; was 1)

| # | File | Status | Coverage |
|---|---|---|---|
| 05 | `05-mission-types-and-counters.md` | **expand** | The summary index; each per-mission file gets its own page |
| 05a | `05a-isr-eo-sar.md` | **NEW** | Maxar/Planet/Capella tasking APIs, NRO program history, NIIRS, sun-sync orbits, NRO/NGA TPED |
| 05b | `05b-satcom-pnt.md` | **NEW** | WGS/MUOS/AEHF, Iridium, OneWeb, GPS Block IIIF flex power, Galileo PRS, GLONASS, BeiDou |
| 05c | `05c-sigint-mw-wx-sda.md` | **NEW** | NRO SIGINT history, SBIRS scanner+starer ops, GOES-R MDS, GSSAP, 18/19 SDS tasking |

### Track E — Operations, legal, history (4 files; was 2)

| # | File | Status | Coverage |
|---|---|---|---|
| 06 | `06-bus-and-payload-operations.md` | **expand** | The "how operators fly satellites" deep-dive, expanded with cited operator console references |
| 06a | `06a-ground-segment.md` | **NEW** | AFSCN, NASA Ground Network, AWS Ground Station, commercial GS (KSAT, ATLAS), GS architectures, TDRSS/SN history |
| 07 | `07-legal-norms-and-roe.md` | **expand** | OST, LOAC in space, 2022 moratorium, UNGA resolutions (the OEWG, Group of Governmental Experts on PAROS) |
| 07a | `07a-incident-record.md` | **NEW** | Catalog of named on-orbit and counterspace incidents with date, attribution, and engine-relevant lesson. The PME instructor's reference shelf. |

### Track F — Cross-cutting and forward-looking (3 files; was 0)

| # | File | Status | Coverage |
|---|---|---|---|
| 08 | `08-commercial-and-allied.md` | **NEW** | Commercial proliferation (Starlink, Project Kuiper), allied coalition SDA (Five Eyes / SST / UCSD), how that changes the targeting calculus. |
| 09 | `09-emerging-tech.md` | **NEW** | Optical ISLs, software-defined payloads (Quantum), on-orbit refueling, manufactured-in-space concepts. Source for v1.1 and v2 engine work in FUTURE-WORK. |
| 10 | `10-sources-and-methodology.md` | **NEW** | The canonical source list (SWF Global Counterspace, CSIS Space Threat Assessment, Secure World Foundation, AU Space Primer, NRO openly-released history, etc.) with hyperlinks and access dates. The "single source of truth" for the rest of the corpus's references. |

**File count:** 7 → 25. Each existing file ~3× in length, each new file ~400-700 lines. Total
estimated lines: ~11,500.

---

## 4. Tiered prioritization

Four tiers. Tier 1 is required to make the existing corpus *defensible*; Tiers 2-4 build outward
from there.

### Tier 1 — Citation backfill + crystallize the audit research (highest priority)

**Scope:** the 8 existing files + `10-sources-and-methodology.md` (NEW).

Goal: every numeric claim, every named system, every doctrinal assertion gets a linked source.
The June 2026 commands-audit agent reports (`/tmp/claude-*/tasks/*.output`) contain hundreds of
already-found citations — fold them in. Take the 4 DA-ASAT test records (SC-19, Burnt Frost,
Shakti, Nudol) that already sourced the `INTERCEPTORS` database and add them to
`03-counterspace-taxonomy.md`. Take the SBIRS/GOES/MAJE research that sourced the new realism
verbs and add it to `05-mission-types-and-counters.md`.

Output: ~3,500 lines added across 8 existing files + 1 new methodology file. ~250 citations.

**Quality bar:** every section in every existing file ends with a `### Sources` subsection
listing every URL referenced in the section. Every numerical claim (km, kg, Pₖ, $, year, etc.)
inline-cites the source at the claim site.

### Tier 2 — Per-mission and per-actor deep-dives

**Scope:** the new Track D files (`05a-isr-eo-sar`, `05b-satcom-pnt`, `05c-sigint-mw-wx-sda`)
and Track A China/Russia deep-dives (`02a`, `02b`, `02c`).

Goal: a PME instructor running a SATCOM-focused exercise has one document to read, not five
scattered sections. Each per-mission file inherits and re-uses the citation conventions from
Tier 1. Per-actor deep-dives back the Red doctrine profiles in `session/redai.py` and the COA
library in `docs/vignettes/`.

Output: ~3,000 lines across 6 new files. ~120 new citations (with extensive reuse of Tier 1).

### Tier 3 — Counterspace systems and physics depth

**Scope:** Track B (`03a`-`03f`) and Track C (`04a`, `04b`).

Goal: every per-domain database in `engine/` (`jam.py`, `cyber.py`, `engage.py`, future
`directed_energy.py`) cites its corresponding research file at module-docstring level. The
fidelity ladder in `04a-propagator-fidelity.md` is the canonical reference for "moderate
fidelity" claims in `docs/build-spec/`.

Output: ~2,500 lines across 8 new files. ~100 new citations.

### Tier 4 — Operations, legal, history, forward-looking

**Scope:** Tracks E and F (`06a`, `07a`, `08`, `09`).

Goal: capture the operational context (ground segment, incident record) and forward-looking
content that informs v1.1 and v2 engine work. `09-emerging-tech.md` is the research backing for
FUTURE-WORK items.

Output: ~2,000 lines across 5 new files. ~60 new citations.

**Cumulative target:** ~11,500 lines, ~530 citations across ~25 files.

---

## 5. Workflow

Research is highly parallelizable. The proposed workflow:

1. **Methodology lock first.** Before any content production, write `10-sources-and-methodology.md`
   (Tier 1 first deliverable) so every later file has a single citation convention. Define:
   linked-citation format (footnote-style or inline-link?), source-quality tiers (peer-reviewed
   > government/think-tank > journalism > advocacy), date-stamping convention, annual review
   marker syntax.

2. **Per-file research agents.** Each new file is a single `deep-research` skill invocation with
   a tight scope. The `deep-research` skill already implements fan-out search → adversarial
   verification → synthesis with citations. Each invocation drafts one file end-to-end.

3. **Parallelism.** Within a tier, files are independent. Spawn 3-5 agents in parallel per
   working session. Tier 1's 8 file-rewrites are parallelizable; Tier 2's 6 files are
   parallelizable; Tier 3 and Tier 4 are parallelizable internally.

4. **Code cross-linking pass.** After each tier lands, run a separate pass that adds
   `# Source: docs/research/03a-da-asat-systems.md#sc-19` style comments to the matching
   `engine/*.py` modules. This is mechanical and can run in one agent invocation per tier.

5. **Verification pass.** After each tier, run an adversarial verifier agent that picks a
   random sample of cited claims and re-checks them against the cited source. Findings go into a
   `docs/research/REVIEW-LOG.md`.

6. **Annual refresh.** Each file's header carries `last_reviewed: YYYY-MM-DD`. A scheduled
   task (manual or `/loop`) checks any file >12 months stale and queues a refresh agent.

---

## 6. Cost and sequencing

Per-tier scale (rough estimates; each agent invocation ≈ 50-100k subagent tokens):

| Tier | New lines | New files | Agents needed | Reviewer-effort |
|---|---:|---:|---:|---|
| 1 — citation backfill | ~3,500 | 1 | ~10 | High (every existing file changes) |
| 2 — mission + actor depth | ~3,000 | 6 | ~6 | Medium (greenfield) |
| 3 — counterspace + physics | ~2,500 | 8 | ~8 | Medium-high (touches engine cross-refs) |
| 4 — ops, legal, forward | ~2,000 | 5 | ~5 | Low |
| **Total** | **~11,000** | **17** | **~29** | |

Recommended sequence:

- **Sprint 1 (1 session):** Tier 1 methodology + backfill, ~6 parallel agents per round, two rounds.
- **Sprint 2 (1 session):** Tiers 2 + 3 launched in parallel (independent), ~10-12 agents.
- **Sprint 3 (1 session):** Tier 4 + verification + code cross-link pass.

Each sprint commits and pushes incrementally; PR #2 or a new PR can host it.

---

## 7. Quality bar — what makes a research file "done"

Per-file checklist used by every authoring agent and every reviewer:

- [ ] Frontmatter: `last_reviewed: YYYY-MM-DD`, `primary_sources_consulted: N`.
- [ ] Every numerical claim (m/s, kg, $, year, Pₖ, dB) inline-cites a source.
- [ ] Every named system (e.g. "Tirada-2", "SC-19") inline-cites at first mention.
- [ ] Every doctrinal assertion ("Russia leads with EW") cites a primary doctrine source or a
      published assessment (CSIS, SWF, IISS) — not Wikipedia alone.
- [ ] `### Sources` subsection at the end of every major section with bullet-point URLs.
- [ ] Cross-references both directions: this file's facts link to the engine code that uses
      them; the engine modules' docstrings link back to this file.
- [ ] No claim that depends on a single source unless the source is the primary one (the
      doctrine document or the test record itself).
- [ ] Date-stamp every claim that names a real event ("In 2007, China's SC-19 …" → cite-date).

---

## 8. Risks and known limits

- **Source rot.** URLs to government / think-tank sites move or 404. Methodology should mandate
  an Internet Archive snapshot URL alongside the live URL for every primary citation.
- **Classification line.** This is a PME training tool — every source must be unclassified and
  open. The methodology file should call out which categories of content are out of bounds
  (CDR / SAP / SCI references), and the reviewer pass should spot-check.
- **Attribution claims.** Some named systems (e.g. SJ-21's tug capability) rest on a small
  number of analyst assessments. Multi-source where possible; flag single-source claims as
  such inline.
- **Scope creep into design docs.** Research is `why`, build-spec is `what is built`, design is
  `how it is built`. Reviewers must reject content that drifts into spec/design territory and
  route it to the right directory.

---

## 9. What this plan does *not* do

- Does not change the engine, the vignettes, the UI, or the tests.
- Does not commit to a delivery date — sprint sequencing is a recommendation, not a contract.
- Does not bind us to producing every file at the listed length; the plan describes targets.
- Does not assume Tier 1 alone is "enough"; it is a foundation. Tiers 2-4 are the breadth.

---

## 10. Sign-off checklist (for the human reviewer)

Before authorizing Sprint 1:

1. Does the file taxonomy in §3 cover the topics the PME audience cares about? Anything
   missing or redundant?
2. Is the 4-tier prioritization the right order? (Tier 1 first is the strong recommendation;
   Tiers 2-4 are reorderable.)
3. Is the per-file quality bar in §7 the right bar? Anything to add or relax?
4. Is the methodology-first sequence in §5.1 acceptable, or should production start in parallel
   with methodology?
5. Authorize Sprint 1 budget (estimated ~10 parallel agents, ~500-1M subagent tokens total).
