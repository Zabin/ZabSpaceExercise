[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Traceability matrix](15-manual-traceability.md)

## 13. Blue cell manual

The role-scoped manual for a **Blue cell operator** — the defender/friendly-force commander who
protects and exploits Blue's space and ground assets under fog-of-war. Every section carries a
stable ID (`BLU-n`) cross-referenced both directions in
[`15-manual-traceability.md`](15-manual-traceability.md). Blue and Red share almost all
mechanics — this manual frames them from Blue's defensive posture; the Red manual
([`14-red-cell-manual.md`](14-red-cell-manual.md)) frames the same mechanics offensively, and
both defer to the shared concept modules rather than duplicating them.

### BLU-1 · Your view: fog-of-war

You see **only Blue's own assets** at true position, plus whatever Blue's sensors have detected —
other-side objects appear only as **tracks** with an uncertainty volume that grows between looks.
You never see Red's ground truth; the filter is enforced server-side at the
`SessionAPI`/`CellController` boundary, not in the browser. Read your **Mission brief** (auto-opens
on load; reopen from View ▾ → Mission brief) for situation, mission, friendly forces, threat
picture, ROE, deadline, and success criteria before acting.

> **Sources:** `spacesim/session/cells.py` (`CellController`, fog filter) · `spacesim/session/scene.py` ·
> `GET /api/sessions/{sid}/brief/blue` · [`02-interface.md`](02-interface.md) §"A player cell"

### BLU-2 · Plan-first commanding

You never act instantly on perfect knowledge — you **plan** a command and the engine schedules it
to the earliest valid window. A command reaches a satellite three ways and the tool picks the
soonest: **ground-station uplink**, **inter-satellite link (ISL) relay** via a crosslink-capable
peer, or a **stored program** run onboard. Every issued order lands in the **command queue** with
its window and delivery path, and stays **cancellable until it uplinks**. Up to four commands
ride one pass.

> **Sources:** `spacesim/engine/orders.py` (`OrderSystem`, delivery paths) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Plan-first commanding"

### BLU-3 · Previews before you commit

Three assistants show what an order will do before you fire it:

1. **Dry-run validity** — the green ✓ / red ✗ line ("will queue · ground_uplink · window
   14:32:10"); a blocked action tells you *why* it's blocked (pre-disabled Issue button).
2. **Consequence preview** — severity, escalation weight, reversibility, debris risk, attribution;
   civilian-target denial bumps severity a tier.
3. **Verb assistants** — `maneuver` (six entry modes, live Δv + new elements), `observe` (beam
   mode + look-angle + expected swath/resolution/power), `jam` (modulation/power/bandwidth with an
   on-map denial footprint).

*See also: [RED-3](14-red-cell-manual.md#red-3--previews-before-you-commit) — the same preview
mechanics from Red's side.*

> **Sources:** `spacesim/engine/orders.py` `dry_run()` · `POST /preview/consequence` ·
> `spacesim/engine/{maneuver,isr,jam}.py` · [`02-interface.md`](02-interface.md) §"Order-composition assistants"

### BLU-4 · SDA: task sensors, build custody, unlock actions

You don't get the sky for free. **Task scarce sensors** to detect, track, and characterize
objects; a good report raises a track's confidence and shrinks its uncertainty. Once a track is
**weapons-quality** (characterized + confident) it **unlocks** actions that were blocked.
Sensors do one thing at a time — task two collections at once and the second slips to a later pass
(contention). Custody **decays** between looks; the belief map blooms the uncertainty volume until
you re-task. This tasking→custody→unlock loop is Blue's core defensive discipline: know the sky
before you commit.

*See also: [RED-4](14-red-cell-manual.md#red-4--build-a-targeting-picture-with-sda) — the same
tasking→custody→unlock loop, applied to targeting rather than defense.*

> **Sources:** `spacesim/engine/custody.py` (`Track`, weapons-quality gate) ·
> `spacesim/engine/access.py` (`sensor_observation`) · [`05-core-concepts.md`](05-core-concepts.md) §"SDA sensor tasking"

### BLU-5 · Keep your buses healthy

Every Blue satellite has a live **bus** (power/eclipse, attitude, thermal, propulsion, storage,
comms), each limit-checked green/yellow/red. The bus **gates the payload** — no power or a
safe-mode event means no mission. The fleet rail rolls each asset up to one worst-subsystem dot
(red if safed) beside an alarms/event feed. Watch it: as the defender you find out you've been hit
at the next telemetry contact, not the moment it happens.

> **Sources:** `spacesim/engine/bus.py` (`BusState`/`PayloadState`) · `spacesim/engine/busmodel.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Bus state-of-health"

### BLU-6 · Diagnose an attack from telemetry

The tool **never tells you "you are being jammed"** — it shows physics; you infer the cause. Click
a fleet row for the subsystem drill-down (parameter list vs. limits, per-parameter history graph
with a clean "compare to nominal" ghost, symptom log). Read the signature:

| If you see… | Likely cause | Blue response |
|---|---|---|
| `comms.rx_power_dbm` HIGH, `cn0_dbhz` collapses, `ber` spikes | EW jamming | re-plan frequency/beam; geolocate the jammer |
| `cdh.fsw_error_count` / `cmd_reject_count` climbing, FSW→safe | Cyber / command-path intrusion | patch the vulnerability; reset FSW |
| `payload.snr_db` drops, `thermal.optics_temp_c` rises on a pass | Directed-energy / dazzle | re-task off the threat geometry |
| A hostile **track closing** on the view | RPO / co-orbital | maneuver-to-evade; task SDA to characterize |
| `battery_soc` + `bus_voltage_v` sag | eclipse / power fault | shed loads; check the power timeline |
| All telemetry **ceases** | kinetic kill (irreversible) | — |

> **Sources:** `spacesim/engine/telemetry.py` (signatures + nominal baseline) ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Diagnosing attacks from telemetry"

### BLU-7 · Recover a safed satellite

Recovery is a **multi-pass procedure**, not a button. If the root cause persists (e.g. an
unpatched modem vulnerability) the satellite is **re-safed** — you must remove the cause (patch the
vulnerability with `def.patch_cyber`, or get the jammer killed) before recovery sticks. Drive it
from the recovery strip; the bus commands (EPS shed/restore, ADCS mode, storage dump) are issued
like any other command via the command action.

> **Sources:** `spacesim/engine/recovery.py` · `spacesim/engine/buscommands.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Safe-mode recovery"

### BLU-8 · Defensive maneuver and conjunctions

The **Conjunctions** sidebar lists upcoming close approaches (range / time-to-CA); each row's
**Evade** button fires `prop.collision_avoid` on your own asset, consuming a small Δv budget and
queuing to the next command-uplink window. For a closing hostile track, the maneuver assistant's
six entry modes let you plan a deliberate evade with live Δv cost.

> **Sources:** `world.conjunctions` · `prop.collision_avoid` verb · `spacesim/engine/maneuver.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) §"Conjunctions & collision avoidance"

### BLU-9 · Cyber cuts both ways

Cyber effects are **not** gated by orbital passes — off-pass, subject to the defender's posture and
whether the vulnerability is patched. As Blue this is the threat you can't see coming on the pass
timeline *and* your fastest patch lever: harden posture and patch known vulnerabilities before Red
exploits them.

*See also: [RED-6](14-red-cell-manual.md#red-6--cyber-the-off-pass-wildcard) — the same mechanic
from the attacker's side.*

> **Sources:** `spacesim/engine/cyber.py` · [`05-core-concepts.md`](05-core-concepts.md) §"Cyber — the off-pass exception"

### BLU-10 · Win the vignette

Your objectives and their gates (window / weapons-quality / ROE) are laid out move-by-move in the
per-cell playbook. Read your row there, then work the tasking→custody→command loop against the
deadline in your Mission brief.

> **Sources:** [`11-vignette-playbooks.md`](11-vignette-playbooks.md) ·
> `spacesim/tests/test_vignette_tutorials.py` · `GET /api/vignettes/{id}/tutorial`

---
