# R123 — Real Satellite Command-and-Telemetry Console Software

> **Document ID:** R123
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](R103-satellite-command-and-control.md), [R114](R114-command-and-data-handling.md)
> **Referenced By:** FS-105, FS-107
> **Produces:** implementation constraints for [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js) (command menu, subsystem
> drill-down verb buttons), [`engine/buscommands.py`](../../../spacesim/engine/buscommands.py) (`BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS`)
> **Feature Mapping:** FS-105 (Spacecraft Operations), FS-107 (Operator Console)
> **Related Topics:** [R103](R103-satellite-command-and-control.md) (Satellite C2 — the validate/window/execute chain this UI exposes),
> [R114](R114-command-and-data-handling.md) (Command and Data Handling — the CDH verbs surfaced in the console), [R124](R124-ccsds-telemetry-and-telecommand-standards.md)
> (CCSDS Standards — the protocol layer beneath the command database)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 2

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`spacesim`'s operator console (the command menu, dry-run preview, subsystem drill-down verb
buttons) is a simplified stand-in for a real spacecraft command-and-telemetry (T&C) ground system.
This topic gives the implementer the real-world shape of that software class — database-driven
command catalogs, pre-flight validation, and real-time telemetry display — so a new console feature
extends the existing `app.js`/`buscommands.py` pattern in a way a real flight controller would
recognize, rather than inventing an ad hoc command-entry UX.

## 2. Scope

Covers: the command-database/catalog model real T&C systems use, the pre-send validation step real
consoles perform before uplink, and how `spacesim`'s verb table + dry-run preview is a deliberate
simplification of that pattern. Does **not** cover: the wire-level packet/frame format the database
ultimately encodes to ([R124](R124-ccsds-telemetry-and-telecommand-standards.md)), or the access-window gating that determines *when* a
validated command can actually be sent ([R103](R103-satellite-command-and-control.md)/[R120](R120-access-window-and-geometry-planning.md)).

## 3. Concepts

**Real T&C consoles are database-driven, not hand-coded per command.** NASA Goddard's two flagship
T&C systems, ASIST and ITOS, are "robust, mature, configurable, and reliable real-time T&C systems"
that process CCSDS-framed telemetry/command and can be driven "only by a database with Systems Test
and Operations Language (STOL) procedures" rather than per-mission bespoke code
([NASA GSFC Engineering and Technology Directorate, *Telemetry and Command (T&C) Systems*](https://etd.gsfc.nasa.gov/capabilities/capabilities-listing/telemetry-and-command-systems/)
([Wayback](https://web.archive.org/web/2026/https://etd.gsfc.nasa.gov/capabilities/capabilities-listing/telemetry-and-command-systems/))) —
directly analogous to `buscommands.py`'s `BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS` sets acting as
the command catalog and `can_issue`/`apply_command` as the database-driven dispatch, rather than a
giant per-command if/else tree scattered across the UI.

**Modern open-source and commercial C2 platforms generalize the same database-driven pattern across
many satellite types.** OpenC3's COSMOS provides "Telemetry Display, Telemetry Graphing, Operational
and Test Scripting, Command Sending, Logging, and Log File Playback" as a single configurable
product with flight heritage across multiple commercial/government missions (RAVAN, Capella,
Kepler, FalconSat)
([OpenC3, *COSMOS — Command, Control, and Communication for Embedded Systems*](https://docs.openc3.com/docs)
([Wayback](https://web.archive.org/web/2026/https://docs.openc3.com/docs))); Kratos's EPOCH IPS is
described by its vendor as "a hardware-independent, database-driven, open architecture satellite
fleet management system capable of controlling an array of satellites with minimal personnel," used
operationally across 300+ satellite missions
([Kratos, *EPOCH IPS product page*](https://www.kratosspace.com/products/satellites/command-and-control/epoch-ips)
([Wayback](https://web.archive.org/web/2026/https://www.kratosspace.com/products/satellites/command-and-control/epoch-ips))) —
both reinforce the same lesson `spacesim`'s console implements at much smaller scale: one generic
verb-dispatch engine driven by a per-asset-type capability table, not one UI screen per satellite
design.

**Real consoles validate a command against the current configuration before it is ever sent.**
The same NASA GSFC source notes ASIST/ITOS can validate commands against a software or hardware
simulation before uplink — this is the real-world precedent for `spacesim`'s `dry_run()`
([R103](R103-satellite-command-and-control.md)) and `buscommands.py`'s `can_issue` plan-time gate: a command that would be
rejected on the real bus (wrong mode, payload unavailable, bus down) should never reach the
"Issue" button enabled in the first place, mirroring how a real console pre-disables or flags
commands the current telemetry state would reject.

**The console groups commands by subsystem ownership, mirroring real subsystem console
positions.** `app.js`'s subsystem drill-down attaches each card's `verbsForSubsystem` buttons to the
owning subsystem (EPS, ADCS, CDH, TCS, comms, propulsion) rather than listing all verbs in one flat
menu — this mirrors how real T&C consoles and FOT console positions ([R125](R125-flight-operations-team-roles.md)) are organized around
subsystem ownership, so an operator drills into the EPS card to find `eps.shed_load`/
`eps.restore_load`/`eps.set_charge_mode` rather than searching a global command list.

### Sources

- *NASA GSFC Engineering and Technology Directorate, Telemetry and Command (T&C) Systems* —
  [live](https://etd.gsfc.nasa.gov/capabilities/capabilities-listing/telemetry-and-command-systems/)
  · [snapshot](https://web.archive.org/web/2026/https://etd.gsfc.nasa.gov/capabilities/capabilities-listing/telemetry-and-command-systems/)
  · accessed 2026-06-27.
- *OpenC3, COSMOS documentation* — [live](https://docs.openc3.com/docs)
  · [snapshot](https://web.archive.org/web/2026/https://docs.openc3.com/docs)
  · accessed 2026-06-27.
- *Kratos, EPOCH IPS product page* — [live](https://www.kratosspace.com/products/satellites/command-and-control/epoch-ips)
  · [snapshot](https://web.archive.org/web/2026/https://www.kratosspace.com/products/satellites/command-and-control/epoch-ips)
  · accessed 2026-06-27.

## 4. Operational Context

Real flight operations never type free-form command strings at a satellite — they select a named
command from a validated database, the console fills in required parameters from a template, checks
the command against current telemetry/configuration state, and only then queues it for the next
valid contact, exactly the pattern `spacesim`'s "select verb → param template → dry-run preview →
Issue" command-menu flow (`app.js:779-1944`) compresses into a browser UI. The real-world products
cited above exist precisely because hand-built command interfaces don't scale past one mission —
the database-driven pattern is the industry's answer to needing the same console software to fly
many different satellite designs.

## 5. Implementation Guidance

- **A new command verb belongs in `buscommands.py`'s verb sets (`BUS_VERBS`/`PAYLOAD_VERBS`/
  `DEFENSE_VERBS`) and `can_issue`, never as a one-off UI special case in `app.js`** — this keeps the
  database-driven dispatch pattern real T&C systems use, rather than letting verb logic leak into
  the presentation layer.
- **Any new console feature must keep `dry_run()`/`can_issue` as the single source of truth for
  whether a button is enabled** — never duplicate validation logic in JS that could drift from the
  engine's actual `_validate`/`can_issue` checks, which would let the UI show a command as available
  when the engine would actually reject it (or vice versa).
- **Group new verbs under their owning subsystem's drill-down card (`verbsForSubsystem`)** rather
  than a flat global command list, preserving the subsystem-console-position mental model real FOTs
  and real T&C UIs use.
- **Don't add a free-text command-entry path** — every real T&C system cited here is database/
  catalog-driven specifically to prevent invalid or malformed commands from ever being constructible;
  a free-text path would reopen exactly the validation gap the catalog model exists to close.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) and FS-107 (Operator Console) are the direct consumers — any new
command-surfacing UI work should extend the existing verb-catalog/dry-run-preview pattern rather than
introduce a parallel command-entry mechanism.

## 7. Related Topics

[R103](R103-satellite-command-and-control.md) (the validate/window/execute chain the console exposes), [R114](R114-command-and-data-handling.md) (the CDH
verbs surfaced in the drill-down), [R124](R124-ccsds-telemetry-and-telecommand-standards.md) (the protocol layer the command database ultimately
encodes to), [R125](R125-flight-operations-team-roles.md) (the subsystem-console-position model the drill-down mirrors).
