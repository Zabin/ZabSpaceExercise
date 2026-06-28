# Changelog — GDS-01–04 updates from `architecture-review.md`

Consolidated record of every change made to [`GDS-01`](../architecture/01-concept-of-operations.md),
[`GDS-02`](../architecture/02-system-context.md), [`GDS-03`](../architecture/03-architecture.md), and
[`GDS-04`](../architecture/04-domain-model.md) in response to
[`architecture-review.md`](architecture-review.md). Each document also carries its own "Review
reconciliation" section recording the same changes in place, immediately above its Merge gate; this
file exists as the single cross-document index so a reader doesn't have to open all four to see the
full picture.

**Scope discipline:** every change below is a clarification, cross-reference, terminology fix, or
new Open Question. None adds a feature, subsystem, domain object, or requirement — per the
instruction this update was made under. Where the review's finding, once checked against the
actual document text, turned out not to apply, that is recorded too (see "Findings checked and not
applied" at the end) rather than silently dropped.

All four documents' `Version` metadata was bumped `1.0 → 1.1`. No document's `Status` changed —
all four remain `✅ Authored — merge gate closed`; this update does not reopen any merge gate.

---

## GDS-01 — Concept of Operations

| Section | Change | Review finding |
|---|---|---|
| §7 Exercise lifecycle | Capitalized "Planned activity" → "Planned Activity" | Terminology consistency with GDS-04 §1.7 |
| §8 Major operational modes | Added note that hot-seat and LAN-cooperative modes share one Session object | §3 finding 3 (architectural inconsistency) |
| §13 Open Question 5 | Appended confirmation that the assessment/scoring gap is architecture-wide | §1 finding 1; §7 findings 1–2 |
| §13 Open Question 6 (new) | AI-Red's epistemic parity with human cells (ground truth vs. filtered Cell View) | §8 finding 3 (new) |
| Metadata | Added cross-reference to the architecture review | — |

## GDS-02 — System Context

| Section | Change | Review finding |
|---|---|---|
| §9 structural property 1 | Appended the no-cell god-view endpoints as the documented exception to "every cell-scoped flow is filtered" | §4 finding 1 (separation of concerns) |
| Open Questions, new #4 | Scenario-authoring workflow has no named boundary actor/interface | §1 finding 2 (missing concept) |
| Open Question 2 (AI-Red actor status) | Appended cross-reference noting three ladder levels independently flag the same question | §1 finding 4; §8 finding 1 |
| Metadata | Added cross-reference to the architecture review | — |

## GDS-03 — Architecture

| Section | Change | Review finding |
|---|---|---|
| §2.2 Ownership of data | Fixed stray typo (`` `WorldState* `` → `` `WorldState` ``); aligned `RoleRegistry` naming with GDS-04's "Role Assignment"; added save-file ownership split | §2 finding 3 (new, overlapping responsibilities); typo fix |
| §2.5 Ownership of data | Added corresponding save-file format/write-act split note | §2 finding 3 |
| §4 Fog-of-war cross-cutting concern | Appended the no-cell god-view endpoint exception | §4 finding 1 (new, separation of concerns) |
| Open Question 2 (AI-Red placement) | Appended cross-reference to corroborating findings in GDS-02/GDS-04 | §1 finding 4; §8 finding 1 |
| Open Question 3 (telemetry/scene split) | Appended note that the review independently reached the same flag | §2 finding 2 |
| Open Questions, new #4 | No stated ceiling for per-session `RLock` contention under concurrent LAN clients | §6 findings 1–2 (scaling) |
| Metadata | Added cross-reference to the architecture review | — |

## GDS-04 — Domain Model

| Section | Change | Review finding |
|---|---|---|
| §1.10 Role Assignment | Clarified AI-Red exercises a Role Assignment the same way a human operator does | §1 finding 4 (missing concept) |
| §1.11 Cell View | Made the read-only, one-directional Track relationship explicit | §5 finding 2 (circular-dependency clarity) |
| §1.14 Session, Constraints | Added forward pointer to the new save-file-versioning Open Question | §8 finding 4 |
| Open Question 3 (SSN Request vs. Planned Activity) | Appended the review's supertype-naming suggestion, left unresolved | §2 finding 1 |
| Open Questions, new #4 | Save-file/Snapshot version compatibility across engine builds | §8 finding 4 (new) |
| Metadata | Added cross-reference to the architecture review | — |
| — | Reviewed Title-Case-vs-lowercase terminology between architecture-altitude and ConOps/context-altitude documents; judged intentional convention layering, left unchanged | Terminology consistency check |

---

## Findings checked and not applied

- **Architectural inconsistencies, finding 2** (six access channels vs. cyber enumerated as a
  full channel without flagging the window-independence exception inline): on re-reading GDS-03
  §2.1, the cyber exception is already stated immediately adjacent to the five-D effect categories
  bullet, and the six access channels listed separately do not include cyber at all. GDS-02 does
  not enumerate the six channels at any altitude. No edit made to either document; the original
  finding overstated the inconsistency once checked against the actual text.
- **Overlapping responsibilities, finding 1** (SSN Request/Planned Activity) and **Architectural
  inconsistencies, finding 1** (PyQt staleness in `build-spec/03`): both were already recorded as
  Open Questions before this update. Their existing text was extended with a cross-reference (see
  tables above) rather than re-litigated, since the underlying tension is unresolved either way
  and resolving it would require a design decision, not a documentation fix.
- **Terminology — "SSN request[s]" vs. "SSN Request"** (lowercase generic usage in GDS-01/GDS-02
  vs. the capitalized formal entity name in GDS-04): left as-is, consistent with the same
  intentional convention-layering judgment applied to Track/Asset/Effect/Planned Activity above.

## Not addressed by this update (require a design decision, not a documentation fix)

These review findings produced new Open Questions (see the per-document tables above) but no
resolution, because resolving them would mean making an architectural decision — out of scope for
a "do not introduce new features" documentation pass:

- Assessment/scoring stakeholder workflow has no owning subsystem or domain object (GDS-01 Open
  Question 5/6, GDS-02 Open Question 4, review §1 finding 1, §7 findings 1–2).
- AI-Red's subsystem placement and epistemic parity with human cells (GDS-01 Open Question 6,
  GDS-02 Open Question 2, GDS-03 Open Question 2, review §1 finding 4, §8 findings 1 and 3).
- No stated LAN-scaling/`RLock`-contention ceiling (GDS-01 §13 Open Question 2, GDS-03 Open
  Question 4, review §6 findings 1–2).
- `scene.py`/`telemetry.py` placement split (GDS-03 Open Question 3, review §2 finding 2).
- SSN Request vs. Planned Activity overlap (GDS-04 Open Question 3, review §2 finding 1).
- Save-file/Snapshot version compatibility across engine builds (GDS-04 Open Question 4, review §8
  finding 4).

## Related

[`architecture-review.md`](architecture-review.md) (the source review) ·
[`architecture/INDEX.md`](../architecture/INDEX.md) (ladder index — unchanged by this update; all
four documents keep their existing `✅ Authored — merge gate closed` status) ·
[`ROADMAP.md`](../../ROADMAP.md) (unchanged by this update).
