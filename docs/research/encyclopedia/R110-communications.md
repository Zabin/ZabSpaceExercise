# R110 — Communications

> **Document ID:** R110
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R101
> **Referenced By:** R107, R115, FS-105
> **Produces:** implementation constraints for `engine/bus.py` (`CommsState`), `engine/jam.py`
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** R107 (Ground Segment Operations), R115 (Electronic Warfare), R103 (Satellite C2)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Communications is the channel-and-link layer underneath the C2 chain (R103) and the thing an
electronic-warfare effect actually denies — this topic gives the `CommsState` model and its
relationship to jamming so a new comms feature (a new link type, a new anti-jam posture) is wired
into the existing denial/mitigation pipeline rather than around it.

## 2. Concepts

**Link state is bus-side, not link-side, data.** `CommsState` (`uplink_lock`, `downlink_lock`,
`isl_enabled`, `data_rate_kbps`, `freq_hopping`, `antenna_mode`) lives on the satellite's `BusState`
— communications health is part of the spacecraft's SOH model, not a separate subsystem outside it.

**Jamming is experienced as an interference level, then mitigated, not toggled.** A jam effect sets
`PayloadState.interference_level`; `satcom.mitigate_interference`/`satcom.shift_users` raise
`interference_mitigation` (capped at 0.8, applied incrementally per command) which "shrinks the jam
signature but never vanishes" — communications denial and defense are both continuous quantities,
mirroring the custody-confidence and power-balance pattern elsewhere in the engine (R105, R111).

**`is_link_denied` is the actual gate a downlink checks at execution time.** `_h_downlink` re-checks
link denial at the execution moment (not at planning time) before delivering product — consistent
with the re-validate-at-execute pattern R103 §2 describes for commands generally: state can change
between issuance and the window actually arriving.

**Frequency hopping is a defensive posture, not a different channel.** `def.frequency_hop` sets
`bus.comms.freq_hopping`, which (per the jam-effectiveness math, R115) reduces the *experienced*
jam impact without changing which access channel (`jam_footprint`) or window applies — defense
changes the outcome probability, not the geometry gate.

## 3. Operational Context

Real satellite communications planning treats link margin, interference, and anti-jam posture as
continuously managed quantities, not a binary "comms up/down" — operators trade data rate,
frequency agility, and beam configuration against a contested RF environment in real time, which is
exactly what `interference_level`/`interference_mitigation`/`freq_hopping`/`data_rate_kbps` are
built to let an operator practice.

## 4. Implementation Guidance

- **A new link type (e.g. optical crosslink) should extend `CommsState`**, not introduce a separate
  comms-health structure outside `BusState` — comms health must stay part of the unified SOH model.
- **A new anti-jam posture should raise `interference_mitigation` or set a `freq_hopping`-style
  flag that the jam-success-probability math (`jam.effective_success_prob`) already reads** — don't
  add a parallel jam-resistance calculation outside that function.
- **Re-validate link state at execution time for any new comms-gated action**, matching
  `_h_downlink`'s pattern, rather than trusting the state at planning time.
- **Don't let a new feature bypass `is_link_denied`** to "just deliver" data — that is precisely the
  kind of parallel state R102/R105 warn against for fog-of-war-adjacent mechanisms.

## 5. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any new comms-posture command must surface
through the existing bus subsystem panel, not a bespoke comms screen.

## 6. Related Topics

R107 (Ground Segment Operations — the physical endpoint of uplink/downlink), R115 (Electronic
Warfare — the threat this topic's defenses respond to), R103 (Satellite C2 — the chain
communications carries).
