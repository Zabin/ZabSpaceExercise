# R110 — Communications

> **Document ID:** R110
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md)
> **Referenced By:** [R107](R107-ground-segment-operations.md), [R115](R115-electronic-warfare-in-space-operations.md), [R131](R131-space-environment-and-space-weather-operations.md), [R134](R134-pnt-warfare-and-navigation-denial-operations.md), [R135](R135-ground-segment-operations-as-contested-terrain.md), FS-105
> **Produces:** implementation constraints for [`engine/bus.py`](../../../spacesim/engine/bus.py) (`CommsState`), [`engine/jam.py`](../../../spacesim/engine/jam.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R107](R107-ground-segment-operations.md) (Ground Segment Operations), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic Warfare), [R103](R103-satellite-command-and-control.md) (Satellite C2)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Communications is the channel-and-link layer underneath the C2 chain ([R103](R103-satellite-command-and-control.md)) and the thing an
electronic-warfare effect actually denies — this topic gives the `CommsState` model and its
relationship to jamming so a new comms feature (a new link type, a new anti-jam posture) is wired
into the existing denial/mitigation pipeline rather than around it.

## 2. Scope

Covers: the `CommsState` link model, continuous interference/mitigation mechanics, and execution-
time link-denial re-validation. Does **not** cover: jam-effectiveness math itself ([R115](R115-electronic-warfare-in-space-operations.md)), the
ground-segment physical endpoint ([R107](R107-ground-segment-operations.md)), or the C2 chain communications carries ([R103](R103-satellite-command-and-control.md)).

## 3. Concepts

**Link state is bus-side, not link-side, data.** `CommsState` (`uplink_lock`, `downlink_lock`,
`isl_enabled`, `data_rate_kbps`, `freq_hopping`, `antenna_mode`) lives on the satellite's `BusState`
— communications health is part of the spacecraft's SOH model, not a separate subsystem outside it.

**Jamming is experienced as an interference level, then mitigated, not toggled.** A jam effect sets
`PayloadState.interference_level`; `satcom.mitigate_interference`/`satcom.shift_users` raise
`interference_mitigation` (capped at 0.8, applied incrementally per command) which "shrinks the jam
signature but never vanishes" — communications denial and defense are both continuous quantities,
mirroring the custody-confidence and power-balance pattern elsewhere in the engine ([R105](R105-custody-theory.md), [R111](R111-power-and-thermal-operations.md)).

**`is_link_denied` is the actual gate a downlink checks at execution time.** `_h_downlink` re-checks
link denial at the execution moment (not at planning time) before delivering product — consistent
with the re-validate-at-execute pattern [R103](R103-satellite-command-and-control.md) §2 describes for commands generally: state can change
between issuance and the window actually arriving.

**Frequency hopping is a defensive posture, not a different channel.** `def.frequency_hop` sets
`bus.comms.freq_hopping`, modeling the same frequency-hopping spread-spectrum (FHSS) anti-jam
technique used in protected military satcom waveforms such as the Protected Tactical Waveform,
which improves rejection of jamming signals at the cost of not eliminating a sufficiently
sophisticated reactive jammer's effect entirely
([DTIC, *Robust Satellite Communications Under Hostile Interference*, ADA614712](https://apps.dtic.mil/sti/tr/pdf/ADA614712.pdf)
([Wayback](https://web.archive.org/web/2026/https://apps.dtic.mil/sti/tr/pdf/ADA614712.pdf))) —
which (per the jam-effectiveness math, [R115](R115-electronic-warfare-in-space-operations.md)) reduces the *experienced*
jam impact without changing which access channel (`jam_footprint`) or window applies — defense
changes the outcome probability, not the geometry gate.

### Sources

- *DTIC, Robust Satellite Communications Under Hostile Interference, ADA614712* — [live](https://apps.dtic.mil/sti/tr/pdf/ADA614712.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://apps.dtic.mil/sti/tr/pdf/ADA614712.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

Real satellite communications planning treats link margin, interference, and anti-jam posture as
continuously managed quantities, not a binary "comms up/down" — operators trade data rate,
frequency agility, and beam configuration against a contested RF environment in real time, which is
exactly what `interference_level`/`interference_mitigation`/`freq_hopping`/`data_rate_kbps` are
built to let an operator practice.

## 5. Implementation Guidance

- **A new link type (e.g. optical crosslink) should extend `CommsState`**, not introduce a separate
  comms-health structure outside `BusState` — comms health must stay part of the unified SOH model.
- **A new anti-jam posture should raise `interference_mitigation` or set a `freq_hopping`-style
  flag that the jam-success-probability math (`jam.effective_success_prob`) already reads** — don't
  add a parallel jam-resistance calculation outside that function.
- **Re-validate link state at execution time for any new comms-gated action**, matching
  `_h_downlink`'s pattern, rather than trusting the state at planning time.
- **Don't let a new feature bypass `is_link_denied`** to "just deliver" data — that is precisely the
  kind of parallel state [R102](R102-space-domain-awareness.md)/[R105](R105-custody-theory.md) warn against for fog-of-war-adjacent mechanisms.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any new comms-posture command must surface
through the existing bus subsystem panel, not a bespoke comms screen.

## 7. Related Topics

[R107](R107-ground-segment-operations.md) (Ground Segment Operations — the physical endpoint of uplink/downlink), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic
Warfare — the threat this topic's defenses respond to), [R103](R103-satellite-command-and-control.md) (Satellite C2 — the chain
communications carries).
