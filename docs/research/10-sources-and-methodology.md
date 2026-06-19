---
last_reviewed: 2026-06-12
primary_sources_consulted: 0
status: methodology — applies to every file in this corpus
---

# Sources & Methodology — the citation convention for `docs/research/`

[← Research index](INDEX.md) · [↑ Docs index](../INDEX.md)

This file defines the **citation convention, source-quality tiers, and review cadence**
that every file under `docs/research/` follows. It is the first deliverable of the
Tier 1 corpus expansion (see `docs/FUTURE-WORK.md` §12) and the canonical reference for
"what does a citation look like in this corpus." Every later authoring agent and every
later reviewer consults this file. The convention is intentionally conservative — it
mirrors the practice of higher-quality Wikipedia articles and most think-tank reports,
so external reviewers find it familiar.

---

## 1. Citation format

### 1.1 Inline citations at the claim site

Every numerical claim, every named system, every doctrinal assertion, every dated
event, and every legal interpretation **inline-links** to its source at the claim site.
The link uses standard Markdown — no footnote-style references, no
deferred-to-end-of-section citations, no parenthetical author-year fragments.

**Good:**

> The 2007 Chinese SC-19 / DN-3 test against [Fengyun-1C](https://celestrak.org/events/asat.php)
> generated more than 3,000 tracked debris fragments at ~865 km altitude — the largest
> deliberate debris-generating event in the historical orbital catalog
> ([NASA ODPO Q1 2008](https://orbitaldebris.jsc.nasa.gov/quarterly-news/pdfs/odqnv12i2.pdf)).

**Bad** (no inline link, even though the Sources subsection has the URL):

> The 2007 Chinese SC-19 test against Fengyun-1C generated more than 3,000 tracked debris
> fragments at ~865 km altitude (NASA ODPO).

The "good" form lets a reader following along online click the source while reading the
claim. The "bad" form forces the reader to scroll, find the source list, and match by
name. A claim without an inline link is treated as **uncited** even when the source
appears in the per-section list at the foot of the file.

### 1.2 Per-section `Sources` subsection at the foot

Every major section (every `##` heading) ends with a `### Sources` subsection that
lists every URL used in the section as a bullet, in the same order they appeared
inline. Each entry carries the live URL, a [Wayback Machine snapshot](https://web.archive.org/)
URL beside it, and the date the live URL was last verified by the authoring agent.

**Format:**

```markdown
### Sources

- *NASA ODPO Quarterly News, Q1 2008* — [live](https://orbitaldebris.jsc.nasa.gov/quarterly-news/pdfs/odqnv12i2.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://orbitaldebris.jsc.nasa.gov/quarterly-news/pdfs/odqnv12i2.pdf)
  · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2025*, China chapter — [live](https://www.csis.org/analysis/space-threat-assessment-2025)
  · [snapshot](https://web.archive.org/web/2026*/https://www.csis.org/analysis/space-threat-assessment-2025)
  · accessed 2026-06-12.
```

The Wayback snapshot is **mandatory** for every external URL because government and
think-tank URLs move on a ~2-3 year cadence (the SWF Counterspace report has moved
twice; CSIS occasionally 404s during site reorganizations; government publication
portals reorganize when administrations change). A live URL without a snapshot is
treated as a citation-rot risk and flagged in the verification pass (§5).

### 1.3 Date-stamping every event claim

Every claim that names a real event carries the event date inline at first mention.

**Good:**

> Operation Burnt Frost (2008-02-21) used a [modified SM-3 from USS Lake Erie](url) …

**Bad:**

> Operation Burnt Frost used a modified SM-3 from USS Lake Erie …

Date-stamping at the claim site removes ambiguity that arises when two events share a
name (e.g. multiple Iranian GPS-jamming campaigns over the Strait of Hormuz) and makes
the corpus self-dating: a reader 5 years from now can immediately distinguish what was
known when from what is recent.

---

## 2. Source-quality tiers

Sources are tiered. Higher tiers are preferred; lower tiers are used only when no
higher-tier source addresses the claim. Single-source claims at any tier are flagged
inline (§3).

### Tier A — Primary or near-primary sources

The actual doctrine document, the test record, the treaty text, the government
announcement, the program-office release, the operator-organization fact sheet, the
primary-source reporting from the participant organization. Examples: USSF Spacepower
publications, AFDP 3-14, Joint Pub 3-14, OST treaty text from UN OOSA, Viasat's own
incident overview of the KA-SAT attack, NASA ODPO Quarterly News, CelesTrak orbital
catalog snapshots, the Jonathan McDowell *Space Reports*, the IS-GPS-200E interface
spec, the 53/4/18/19 SOPS public fact sheets, the State Department / UNGA resolution
text.

### Tier B — Peer-reviewed academic + recognized think-tank assessments

Peer-reviewed journal articles (*Acta Astronautica*, *Astrodynamics*, *Space Policy*),
NRO Center for the Study of National Reconnaissance historical monographs, recognized
think-tank annual reports (SWF Global Counterspace Capabilities, CSIS Space Threat
Assessment, IISS *Military Balance*, RAND space studies, CASI China Aerospace Studies
Institute reports), congressional research service reports (CRS), Government Accountability
Office reports (GAO).

### Tier C — Reputable journalism + analyst commentary

Major outlets with editorial standards (the *New York Times*, *Wall Street Journal*,
the *Financial Times*, the *Washington Post*, *Defense News*, *Breaking Defense*, *Space
News*), independent space-specialist outlets (*Ars Technica* space, *Aviation Week*,
*The Space Review*), and recognized analyst blogs (Bart Hendrickx on Russian space,
Andrew Erickson on Chinese maritime / space, the Brian Weeden / SWF written work). Used
for claims where Tier A/B sources do not exist or have not yet been published.

### Tier D — Advocacy and Wikipedia

Advocacy publications (anti-debris coalitions, arms-control advocacy groups) and
Wikipedia. Used **only** as a tertiary cross-check or as a navigational pointer to a
Tier-A/B/C primary source. **Wikipedia is never used as a stand-alone citation.** A
claim cited only to Wikipedia is treated as uncited and flagged in the verification
pass.

---

## 3. Single-source claims and uncertainty

Some claims rest on a small number of analyst assessments — particularly claims about
clandestine programs (SJ-21's tug capability, Burevestnik's co-orbital sub-satellite
ejection, the rumored Chinese Zimu-1 directed-energy program). These claims are
permitted in the corpus but **must be flagged inline** so a reader knows the
provenance.

**Single-source flag format:**

> *Single source (analyst).* The [SJ-21 reportedly executed a GEO tug
> maneuver](https://www.csis.org/...) against Beidou-G2 in early 2022, relocating the
> defunct satellite ~3,000 km above the GEO belt. The maneuver is widely accepted by
> analysts but has not been formally confirmed by Chinese authorities.

The italicized "*Single source (analyst).*" prefix triggers the verification-pass
spot-check (§5) to specifically check that no higher-tier corroboration was missed.

**Single-source claims that rely on a Tier-D source alone are not permitted.** If only
Wikipedia or advocacy material covers a claim, the claim is dropped or rewritten to
state only what Tier-A/B/C sources support.

---

## 4. Cross-linking with engine code (Lever 4 — bidirectional)

Every research section that justifies engine numbers carries a `Used by:` closing line
naming the engine module(s) and the database/constant(s) it sources. Every engine
module that hard-codes numbers carries a `# Source:` comment beside the hard-coded value
naming the research file and anchor.

**Research-file side (closing line of a section):**

```markdown
Used by: `engine/engage.py:INTERCEPTORS["mrbm_kkv"]` (base_pk, max_alt_km, divert_dv_ms,
salvo_correlation); `engine/engage.py:debris_cone_estimate` (the "decades" persistence
regime for >600 km LEO debris).
```

**Engine-code side (comment line at the hard-coded value):**

```python
"mrbm_kkv": {  # Source: docs/research/03a-da-asat-systems.md#sc-19-2007
    "base_pk": 0.70, "max_alt_km": 1000, "seeker": "ir_hit_to_kill",
    ...
},
```

The convention is enforced by the **code cross-linking pass** that runs after each tier
lands (see `docs/FUTURE-WORK.md` §12.6). The pass walks engine modules, matches hard-coded
constants to research-file anchors, and adds the comments. A future audit catching "the
research says X but the code does Y" drift uses this convention to find the discrepancy.

---

## 5. Annual review cadence + verification

### 5.1 Per-file frontmatter

Every file under `docs/research/` carries YAML frontmatter at the top:

```yaml
---
last_reviewed: YYYY-MM-DD
primary_sources_consulted: N
status: stable | needs-refresh | draft
---
```

`last_reviewed` is the date a human reviewer last passed §6's quality bar against the
file. `primary_sources_consulted` is the count of Tier-A sources actually cited (not
just listed in Sources). `status` reflects the file's review state.

### 5.2 Stale-banner threshold

A file with `last_reviewed` older than **12 months** is treated as stale. The next
authoring or reviewer agent that touches the corpus adds a stale banner at the top of
each stale file:

```markdown
> ⚠ This file's last review was YYYY-MM-DD. It may contain outdated dates, broken URLs,
> or doctrine claims that have been superseded. Pending refresh.
```

The banner stays until a refresh pass updates `last_reviewed`.

### 5.3 Verification pass

After each tier of `docs/FUTURE-WORK.md` §12 lands, a separate **verification pass**
runs as an adversarial reviewer agent. The agent:

1. Picks a random sample of 20 cited claims across the files modified in the tier.
2. Fetches each cited source and confirms the claim is supported.
3. Spot-checks the quality bar (§6) on a random sample of 3 files.
4. Writes findings to `docs/research/REVIEW-LOG.md` with file:line references and a
   verdict per checked claim (`✓ supported`, `⚠ partial`, `✗ unsupported`).
5. Any `✗ unsupported` finding is a blocker for the tier's merge.

The verification pass is the corpus's closest analog to a unit-test suite.

---

## 6. Per-file quality bar (the reviewer's checklist)

Every file under `docs/research/` must pass this checklist before merge:

- [ ] Frontmatter present and `last_reviewed:` ≤ 12 months old.
- [ ] Every numerical claim (m/s, km, kg, $, year, Pₖ, dB, %) inline-cites at the claim site.
- [ ] Every named system (SC-19, Tirada-2, SBIRS, etc.) inline-cites at first mention.
- [ ] Every doctrinal assertion ("Russia leads with EW") cites a Tier-A or Tier-B source.
- [ ] Every event-naming claim ("Operation Burnt Frost") is date-stamped inline.
- [ ] `### Sources` subsection at the end of every `##` section, with live + Wayback
      snapshot + access-date per URL.
- [ ] `Used by:` closing line on every section that justifies engine code.
- [ ] No claim relies on a single Tier-D (advocacy / Wikipedia) source.
- [ ] Single-source Tier A/B/C claims carry the italicized `*Single source (...).*` flag.
- [ ] Stale-banner removed (if it was present at start) and `last_reviewed:` updated.

The reviewer agent that runs at the end of each tier checks (a)-(j) per file and
records pass/fail in `docs/research/REVIEW-LOG.md`.

---

## 7. The canonical source registry

The following Tier-A and Tier-B sources are consulted by ~every file in the corpus. The
authoring agents are expected to know these without re-discovery.

### Open-source counterspace assessments (annual or near-annual)

- **SWF Global Counterspace Capabilities** (Secure World Foundation, annual since
  ~2018; current edition 2025) — [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report).
  Per-actor capability assessment with named systems, dates, and attribution status.
  *The single most-cited Tier-B source in the corpus.*
- **CSIS Space Threat Assessment** (Aerospace Security Project, annual since 2018;
  current edition 2025) — [live](https://www.csis.org/analysis/space-threat-assessment-2025).
  Per-actor counterspace capability assessment, paired with SWF for cross-validation.
- **IISS *Military Balance*** (annual) — [live](https://www.iiss.org/publications/the-military-balance/).
  Per-country military assessments with space forces sections from 2020 onward.

### Doctrine + operator-organization sources

- **USSF Spacepower (Capstone) doctrine** — [live](https://www.spaceforce.mil/About-Us/About-Space-Force/Doctrine/).
- **AFDP 3-14 Space Operations** — published via the LeMay Doctrine Center.
- **Joint Pub 3-14 Space Operations** — published via the Joint Chiefs of Staff.
- **AU Space Primer** (Air University) — [live](https://www.airuniversity.af.edu/AUPress/).
  Multi-edition; the SSN tasking-category scheme that informs `engine/ssn.py`.
- **53 SOPS / 4 SOPS / 2 SOPS / 18 SDS / 19 SDS fact sheets** — published via
  https://www.spaceforce.mil/About-Us/Fact-Sheets/.

### Treaty + international-law sources

- **Outer Space Treaty (1967), Registration Convention (1976), Liability Convention
  (1972)** — UN Office for Outer Space Affairs treaty repository at
  [unoosa.org](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties.html).
- **2022 US destructive-DA-ASAT moratorium declaration** — State Department release.
  Followed by UNGA Resolution 77/41 (2022).
- **OEWG (Open-Ended Working Group on PAROS) and GGE-PAROS** — UN Office for
  Disarmament Affairs.

### Orbital-mechanics + propagation sources

- **Vallado, *Fundamentals of Astrodynamics and Applications*** — the canonical
  reference for Keplerian elements, J2 secular precession, and SGP4 internals.
  The 2006 SGP4 revisitation paper is widely cited.
- **Hoots & Roehrich (1980)** — the original SGP4 specification.
- **CelesTrak orbital catalog** — [live](https://celestrak.org/). Snapshots of the
  18 SDS public catalog.
- **NASA ODPO Quarterly News** — [live](https://orbitaldebris.jsc.nasa.gov/quarterly-news/).
  Authoritative source for debris-event counts and reentry-timeline analyses.

### Mission-specific operator references

- **Commercial ISR tasking APIs** — Maxar / Planet / Capella developer documentation.
  Cited by the audit's mission-set realism research; the canonical Tier-A source for
  realistic ISR operator parameters.
- **AWS Ground Station** documentation — [live](https://aws.amazon.com/ground-station/).
  Cited by the audit for commercial ground-station booking economics.
- **IS-GPS-200E** (Interface Specification, GPS L1/L2 navigation message including the
  flex-power authorization) — the canonical Tier-A source for the audit's
  `pnt.flex_power` verb.

### Russian-space + Chinese-space analyst sources

- **Bart Hendrickx** — the most-cited independent analyst on Russian space, published
  through *The Space Review* and his own archives.
- **Andrew Erickson** (US Naval War College) — Chinese space + maritime / national
  power studies.
- **CASI China Aerospace Studies Institute** — US Air University center publishing
  open-source Chinese-space analysis.

### Incident-record corroborating sources

- **Jonathan McDowell's *Space Reports* and personal log** — [live](https://planet4589.org/).
  Comprehensive incident catalog with primary-source citations.
- **Viasat's own incident overview** of the KA-SAT attack — [live](https://www.viasat.com/perspectives/corporate/2022/ka-sat-network-cyber-attack-overview/).
  The canonical Tier-A source for the audit's `engine/cyber.py` VECTORS table.
- **SentinelOne AcidRain analysis** — the malware analysis underpinning the Viasat
  attribution timeline.

---

## 8. Out-of-bounds content

This corpus is a PME / training reference for an unclassified simulator. The following
content is **out of bounds** and must not appear:

- Classified material (CDR, SAP, SCI) — anything with handling markings.
- Tactics, techniques, or procedures (TTPs) specific to ongoing or recent real-world
  operations that have not been independently disclosed.
- Specific cryptographic key material, satellite vehicle ID-to-classified-program
  mappings, or other identifiers that aggregate to a classified picture.
- Operationally-sensitive timing data on ongoing reconnaissance operations.

If an authoring agent encounters source material whose classification status is
ambiguous, it must flag the question in the file's draft rather than including the
material. The verification pass spot-checks for content that drifted into out-of-bounds
territory.

---

## 9. Sources

This file consults no external sources directly — it defines convention. The canonical
source registry in §7 lists the sources the rest of the corpus consults.

*Last reviewed: 2026-06-12. Pending review: every 12 months from `last_reviewed`.*
