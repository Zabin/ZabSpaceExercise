# ADR-0036 — Asset/effect/sensor template libraries vs. the shipped inline-authoring model

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0036
- **Title:** Whether the content model keeps (and builds) asset/effect/sensor template libraries,
  or the architecture is amended to the inline-authoring model the build actually ships
- **Status:** **Proposed — decision reserved for the project owner** (backlog `BL-0233`)

## Context

Three closed-gate / accepted records describe a construct the build does not have:

- **GDS-03 §2.5** (Content & Data, `✅ merge gate closed`) lists among the subsystem's
  Responsibilities: "Hold asset/effect/sensor template libraries (regime defaults, payload type,
  telemetry/command databases, vulnerabilities, available defenses) referenced by the engine when
  building a `WorldState`", its Outputs include "template data the engine consults", its Mermaid
  diagram draws a `TPL[(Asset / effect / sensor templates)]` store, and its data ownership names
  "the on-disk vignette/template/save/TLE-cache file formats".
- **GDS-04 §1.2** (Asset, `✅ merge gate closed`) lists "template reference" in the Asset's
  persistent state.
- **ADR-0007** (Accepted) decides that "asset/effect/sensor template libraries … are authored as
  YAML/JSON files".

As built (verified 2026-10-17 against `spacesim/content/`): every asset and sensor in all 19
shipped vignettes is authored **inline** in the vignette's `blue_forces`/`red_forces`/
`neutral_forces`/`sensors` lists; there is no asset, effect or sensor template file anywhere under
`spacesim/content/`; `Asset` and `Sensor` carry no template-reference field; and no vignette field
names a template. The only template library that exists is the **inject** library
(`inject_library.yaml`), which GDS-03 §2.5 lists separately and which is unaffected here. The
Vignette Creator (`IP-1171`–`IP-1174`) and `export_vignette()` also write assets inline.
(`EffectInstance.template` is a free-text label recorded in the effect log, not a reference into a
library. The Creator's ground-site picker, `content/ground_sites.py`, copies a catalogued site's
coordinates into the new asset; the vignette keeps no reference to the catalogue entry.)

`FR-5310`'s description ("every referenced template exists") and its **only** Acceptance Criterion
("a vignette referencing a non-existent asset template … identifies the missing template by name")
derive faithfully from these records, so `04-requirements-engineering` could not drop the clause
(run #142, `requirements-update-load-validation-batch.md` F1) and routed the question here.
`IP-1310` shipped `FR-5310`'s other clauses plus `FR-5311`–`FR-5314`; FS-131's criterion 10 (the
template case) is the one thing blocked.

## Why this ADR does not decide

Either resolution is reserved for the project owner under this corpus's own precedent:

- **Option A** rewrites an existing subsystem description in two closed-gate GDS levels and
  amends an `Accepted` ADR. Every prior amendment to a closed-gate GDS level was an
  "explicitly-instructed amendment, not a gate reopening" (GDS-02/03/04 reconciliation sections),
  each additive and changing no existing subsystem description in §1–§4; and the corpus's one
  supersession of an Accepted ADR (`ADR-0033` → `ADR-0029`) was a direct project-owner decision.
- **Option B** commits the product to a new capability (a template content model plus its
  authoring, loading and Creator support) that no Feature in the catalog owns — a scope decision.

`ADR-0024`–`ADR-0029` set the precedent for this situation: record the question as `Proposed`, say
plainly that no decision has been made, and let the owner resolve it.

## Options

- **A — Amend to the inline-authoring model (recommended).** GDS-03 §2.5 drops the template-library
  responsibility, output, diagram node and format ownership (or moves template libraries to its §5
  "Forward-looking architectural considerations" as not-built, matching how other future
  components are recorded there). GDS-04 §1.2 drops "template reference" from persistent state.
  `ADR-0007` is amended (not superseded): its content-as-data decision stands; only the words
  "asset/effect/sensor template libraries" are narrowed to the inject-template library. Then `04`
  re-points `FR-5310`'s clause and AC to a reference the model actually carries — candidates the
  build already validates or could: a `roles_needed` reference (now `FR-5314`), a sensor's
  `host_asset_id`, or an inject's `target`/asset reference — and FS-131 criterion 10 is re-written
  to match. Cost: documentation only (03 → 04 → 06 deltas); no code. Invariant 6 (content is data)
  is unaffected: inline YAML is still data.
- **B — Keep template libraries and build them.** The records stand; `05` adds a Feature for an
  asset/effect/sensor template content model (template files, a template-reference field on
  `Asset`/`Sensor`, resolution at `build_world`, Creator and `export_vignette()` support, and the
  `FR-5310` missing-template check), then `06`/`07`/`08`. FS-131 criterion 10 stays blocked until
  that Feature ships. Cost: a full feature loop plus migration questions for the 19 shipped
  vignettes (stay inline, or be rewritten to reference templates).
- **C — Defer.** Leave the records as they are, mark FS-131 criterion 10 explicitly deferred against
  a named trigger (for example "when a template Feature is catalogued"), and accept the standing
  record/build mismatch. Cost: none now; the mismatch stays visible in `FR-5310`.

## Recommendation (advisory — not a decision)

**Option A.** The shipped system, all 19 vignettes, the Vignette Creator and the export path are
built on inline authoring, and nothing in the requirements baseline besides `FR-5310`'s one clause
depends on templates. Option A makes the records describe the system that exists without changing
any behaviour; Option B is new scope with no requesting stakeholder on record.

## Decision

**None yet.** Pending the project owner's choice of A, B or C (backlog `BL-0233`, `NEEDS-USER`).

## Consequences (by option, once decided)

- **A:** `03` amends GDS-03 §2.5, GDS-04 §1.2 and `ADR-0007` (recording the owner's instruction
  in each document's reconciliation notes); `04` re-points `FR-5310`; `06` updates FS-131
  criterion 10 (riding `BL-0242`'s FS-131 text fix). This ADR becomes `Accepted`.
- **B:** `05` catalogs a template-library Feature; FS-131 criterion 10 waits for it. This ADR
  becomes `Accepted` with ADR-0007 unchanged.
- **C:** `06` marks FS-131 criterion 10 deferred with its trigger. This ADR stays `Proposed`.

## Related

`ADR-0007` (content as data); GDS-03 §2.5; GDS-04 §1.2; `FR-5310`
(`docs/requirements/01-functional-requirements.md`);
[FS-131](../../features/FS-131-load-time-vignette-validation.md) criterion 10 / Open Question 1;
[`reviews/requirements-update-load-validation-batch.md`](../../reviews/requirements-update-load-validation-batch.md) F1;
backlog `BL-0233`, `BL-0242`.
