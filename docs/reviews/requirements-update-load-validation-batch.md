# Requirements Update Report — Load-Validation Batch (2026-10-16)

> **Status:** Complete.
> - Five numbered FR leaves added: `FR-5311`–`FR-5314` and `FR-1460`.
> - Three candidates added: `CR-23`–`CR-25`.
> - One RTM forward cell filled: `FR-5310` → `FS-131`.
> - Two questions reported for adjudication rather than resolved: `BL-0233` and `BL-0215`.
> - No NFR changed.
>
> **Source:** `docs/pipeline/backlog.md` `BL-0233`, `BL-0234` and `BL-0235` (FS-131 Open Questions
> 1–3, run #141), plus `BL-0215` and `BL-0226`, whose trigger was "the next
> `04-requirements-engineering` pass". The pipeline manager (run #142) batched them.
> - `BL-0171` (telemetry pass-gating) and `BL-0181` (ISO-8601 export times) are parked
>   `NEEDS-USER` with the project owner. They also name "the next `04` pass" and were
>   **explicitly excluded**; both are untouched.
> - `BL-0187` is likewise untouched.
>
> **Scope (written):**
> - `docs/requirements/01-functional-requirements.md`: header note, `FR-1460`, `FR-5311`–`FR-5314`,
>   `CR-23`–`CR-25`.
> - `docs/requirements/03-requirements-traceability-matrix.md`: header note; rows `FR-1460`,
>   `FR-5310`–`FR-5314` and `CR-23`–`CR-25`; the ADR-0007, C1, C5, INT-0008 and INT-0011
>   reverse-index rows.
> - `02-non-functional-requirements.md` was read and is unchanged.
>
> **Inputs read (the role mapping, per this skill's layout note):**
> - Domain-model role: GDS-04 (`docs/architecture/04-domain-model.md`) §1.1 Vignette, §1.2 Asset,
>   §1.3 Orbit, §1.5 Sensor and §1.10 Role Assignment, each section's "Persistent state",
>   "Relationships" and "Constraints".
> - Architecture role: GDS-03 §2.5 Content & Data, and ADR-0007.
> - Legacy reference: `docs/design/04-data-model.md` §9, read because GDS-04 cites it. It is not
>   binding (CLAUDE.md).
> - Requirement leaves: `FR-5310`, `FR-1310`, `FR-1410`, `FR-1610`, `FR-4210`, `FR-5210`/`FR-5220`,
>   `NFR-1600` and `NFR-2200`; the Feature Spec FS-131; `R109` §3.6, as `FR-1610`'s own source.
> - Shipped behaviour, for the as-built reading only and never as a source:
>   - `content/vignette.py` (`load_vignette`, `build_world`, `Vignette`, `RoleRequirement`);
>   - `engine/entities.py` (`AssetResources`, `Sensor`);
>   - `engine/orders.py` (the `no_ammo` gate, the engage consumption, `ORDER_PARAM_RULES`);
>   - `session/manager.py` (`assign_role`).
>
> **No architecture was redesigned and no fact was originated.** Each added leaf restates a GDS-04
> constraint, or `FR-5310`'s own wording, as an atomic testable statement.

## 1. Changes applied

| Item | Change | Traced to |
|---|---|---|
| `BL-0235` | **`FR-5311` added:** a TLE-sourced orbit that does not parse into an element set the propagator accepts is rejected at load, naming the asset. Checksum and epoch-sanity checks go to **`CR-23`** (no source). | GDS-04 §1.3 Constraints ("TLE-sourced orbits must parse at load or the Asset is rejected with a clear error"); `FR-5310` ("well-formed TLEs"). |
| `BL-0234` | **`FR-5312` added:** a satellite with no orbit, or a terrestrial asset with no location, is rejected at load. | GDS-04 §1.2 Constraints. |
| `BL-0234` | **`FR-5313` added:** two asset entries, or two sensor entries, sharing one id are rejected at load. | `FR-5310` ("rather than a partial or silent load"); GDS-04 §1.2/§1.5 Identity. |
| `BL-0234` | **`FR-5314` added:** a `roles_needed` entry naming no declared asset or constellation group is rejected at load. | `FR-5310` ("every declared `roles_needed` satisfiable"); GDS-04 §1.10 Relationships/Constraints. |
| `BL-0234` | **`CR-24` added:** the remaining cross-references (sensor `host_asset_id`, objective object ids, scheduled inject targets, a free-text asset `kind`). | No input names them; `NFR-1600` is broad enough to cover them but does not commit to any. |
| `BL-0226` | **`FR-1460` added:** an engagement whose salvo exceeds the effector's remaining ammunition is rejected at validation. The other range rules go to **`CR-25`**. | GDS-04 §1.2 ("resource levels cannot go negative"; ammo is a resource level); `FR-1310` precedent. |
| RTM | `FR-5310`'s Future Feature cell set to `FS-131` (written run #141). | `docs/features/FS-131-load-time-vignette-validation.md`. |

**As-built evidence behind each leaf** (probes this run and run #141, recorded so `07` and `09` can
reproduce them):

- **`FR-5311`:** a malformed TLE on `04-co-orbital-threat-escort` loads and starts, then raises
  `sgp4 propagation error code 2` on the first advance (`BL-0237`).
- **`FR-5312`:** on `03-gnss-ew-campaign`, removing `BLUE-GNSS`'s orbit or `RED-JAM`'s location
  loads, starts and advances an hour silently.
- **`FR-5313`:** a duplicate asset id loads, and the later entry replaces the earlier.
- **`FR-5314`:** `roles_needed: [{asset_or_constellation: NO-SUCH-SAT}]` loads and starts.
- **`FR-1460`:** on `da-asat-crisis` seed 142, with `RED-ASAT` set to 1 round and Red kinetic
  authorized, a 5-round salvo is accepted and a successful engagement leaves `ammo = -4`.

## 2. Review findings

| Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|
| **F1** — Conflict (requirement vs. as-built content model; architecture vs. as-built) | `FR-5310` (`BL-0233`); GDS-03 §2.5; GDS-04 §1.2; ADR-0007 | `FR-5310` requires "every referenced template exists", and its **only** Acceptance Criterion is "a vignette referencing a non-existent asset template is rejected …". The architecture describes such templates: GDS-03 §2.5 says Content & Data holds "asset/effect/sensor template libraries"; GDS-04 §1.2 lists a "template reference" in Asset's persistent state; ADR-0007 names "asset/effect/sensor template libraries". But the shipped content model has no template library under `spacesim/content/`. Assets and sensors are authored inline in each vignette, and no vignette field references a template. So the requirement is consistent with the architecture, and both describe something the build does not have. This skill cannot settle it. Dropping the clause would contradict GDS-03/GDS-04/ADR-0007; keeping it leaves a Must requirement whose only test cannot run. | **Medium** | **Escalate to `03-architecture-design-synthesis`** (architecture owner), with the project owner if `03`'s rules reserve a change to a closed-gate GDS level. Options: **(A)** amend GDS-03 §2.5 / GDS-04 §1.2 (and note on ADR-0007) to describe the as-built inline-authoring model, after which `04` re-points `FR-5310`'s template clause and AC at references the model carries (now `FR-5311`–`FR-5314`); **(B)** keep the template libraries as architecture, and plan them as their own Feature through `05`, leaving `FR-5310`'s template AC pending until built. Until then FS-131 criterion 10 stays blocked, and the new leaves give `FR-5310` testable coverage of its other clauses. |
| **F2** — Conflict (Acceptance Criterion vs. its own Postcondition) | `FR-1610` (`BL-0215`) | The AC requires that a fence "detects more transiting objects" than a dish observing the same volume. The Postcondition says "the existing ground/space access predicate is unchanged", and `R109` §3.6 recommends modelling the difference as a `BEAM_MODES` extreme rather than a new access predicate. With the predicate unchanged, a fence and a dish get the same windows; only gain and footprint differ. That is what `IP-1220`/`IP-1222` built and `VR-1220` accepted (the gain-only reading). The source of the requirement is the project owner's own request (`BL-0073`, item B7). | Low | **Project owner decides** (`NEEDS-USER`, not blocking). **(A)** Amend the AC to the gain/footprint trade, matching the Postcondition, R109's recommendation and the shipped build. **(B)** Keep the AC and relax the Postcondition, which means a new access-predicate behaviour for fence radars and a `06`/`07` package. A is the smaller change and matches what is verified. B is closer to the literal request. |
| **F3** — Conflict (domain-model constraint vs. as-built resource model) | GDS-04 §1.2 ("resource levels cannot go negative"), jam power consumption (`BL-0226`) | A successful jam subtracts its power draw from the jammer's `resources.power_w`. Jammers default to 0 W, and no shipped vignette sets a jammer's power, so most successful jams already drive the resource negative. Enforcing GDS-04's constraint on power the way `FR-1460` does for ammunition would refuse almost every shipped jam. Either GDS-04 does not mean jammer power to be a consumable budget, or the as-built consumption is wrong. | Low | **Escalate to `03-architecture-design-synthesis`**: say whether a terrestrial jammer's `power_w` is a consumable, non-negative budget (then `04` adds the leaf and vignettes need a power figure) or a rating that is not consumed (then the consumption is a `07` remediation). Not baselined either way here. |
| **F4** — Missing requirement (recorded as candidates, not baselined) | `CR-23`, `CR-24`, `CR-25` | Each candidate covers behaviour the system accepts silently today, for which no input states a rule. Promotion needs an owner request or an architecture statement, the precedent every intake leaf followed. | Low | Leave as candidates. Re-examine if the owner asks for any of them, or if `03` (F1/F3) adds the missing statement. |
| **F5** — Downstream coherence (no requirement change) | FS-131 vs. `FR-5311`–`FR-5314` | FS-131 (run #141) cites only `FR-5310`/`NFR-1600`/`NFR-2200`, and its rule list covers `FR-5311`, `FR-5313` and `FR-5314` under `FR-5310`'s clauses. It does **not** include `FR-5312` (orbit/location presence), which it folded into Open Question 2 as a candidate. | Low | **Route to `06-feature-specification`**: add `FR-5311`–`FR-5314` to FS-131's Requirements Implemented (all are `FEAT-5300`'s by parentage), add the `FR-5312` rule and an acceptance criterion for it, and drop the CR-24 items it no longer needs to question. This should happen **before** `07` plans FS-131. The catalog's `FEAT-5300` Included Requirements likewise lists only `FR-5310`, which is a `05` housekeeping note, not a scope change. |

No finding was acted on beyond the derivations in §1. The Review proposes; it applies nothing.

## 3. Quality gate

- [x] Every added leaf has the full field set and an exact section citation.
- [x] Each leaf is atomic, testable and implementation-independent (no class or exception names
      in Description or Acceptance Criteria; the as-built names appear only in Rationale/Notes as
      evidence).
- [x] No added leaf contradicts another requirement or an ADR. The two that would have (power
      non-negativity; a template-free `FR-5310`) were reported (F1/F3), not baselined.
- [x] RTM has one row per added leaf and candidate, with `UNASSIGNED` where no downstream artifact
      exists.
- [x] `BL-0171`, `BL-0181` and `BL-0187` were untouched.

## Next step

1. `06-feature-specification` on FS-131 for F5. It is small, and it must precede `07`.
2. `03-architecture-design-synthesis` on F1 (`BL-0233`) and F3 (`BL-0226`'s power residue). F1
   blocks only FS-131 criterion 10, not the rest of FS-131's planning.
3. F2 (`BL-0215`) waits for the project owner and blocks nothing.

## Addendum — run #144 (2026-10-16): `FR-5312` scope (`BL-0241`)

**Trigger:** FS-131 v1.1 (run #143) scanned the shipped library while adding `FR-5312`'s rule.
Seven vignettes (`00-training-basics`, `06-satcom-cyber-link`, `08-multi-domain-taiwan`,
`coa-china-md`, `coa-china-ml`, `coa-russia-md`, `learn-intermediate-recovery`) declare a
`cyber_unit` (`RED-CYBER`) with no location. `FR-5312` as written in run #142 required every
"terrestrial asset" to have a location without defining terrestrial. Read broadly, it would have
refused all seven. That was a defect in this skill's own run #142 wording.

**Sources checked:**

- GDS-04 §1.2 Purpose lists "satellite, ground station-adjacent terrestrial force, jammer,
  interceptor, or cyber unit". Its Constraints do not define terrestrial.
- ADR-0012: cyber is "the one window-independent exception", because cyber operations are
  "persistent compromise, not a live geometric pass".
- `FR-1420` resolves cyber "without requiring an open access window".

**Change applied:** `FR-5312` now exempts cyber units from the location rule. This affects its
Description, Postcondition, Acceptance Criteria (which now name the located kinds and assert that
a location-less cyber unit loads), Source Documents, Related ADRs (ADR-0012 added) and Notes. The
RTM row is updated to match. Every other non-satellite kind, including an unrecognised free-text
one, stays under the rule.

**Review:** the amended leaf is consistent with ADR-0012, `FR-1420` and FS-131 criterion 9. No new
conflict. FS-131 v1.1's narrow reading (System Behaviour 7, criterion 11) already matches this
scope. Its Open Question 6 can be marked closed at the next `06` touch; there is no behavioural
difference to plan around.

**Untouched:** `BL-0171`, `BL-0181`, `BL-0187`, `BL-0215`.

