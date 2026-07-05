# R121 — Telemetry, Logging, and Attack-Signature Modeling

> **Document ID:** R121
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](R103-satellite-command-and-control.md)
> **Referenced By:** FS-105, [R131](R131-space-environment-and-space-weather-operations.md), [R137](R137-bus-and-payload-parameter-catalog.md)
> **Produces:** implementation constraints for [`engine/telemetry.py`](../../../spacesim/engine/telemetry.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R103](R103-satellite-command-and-control.md) (Satellite Command and Control), [R111](R111-power-and-thermal-operations.md) (Power and Thermal Systems Operations — the bus SOH model telemetry samples from), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic Warfare — one of the four signatures), [R116](R116-cyber-operations-against-space-systems.md) (Cyber Operations — the cyber signature)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`engine/telemetry.py` is the read-time signal layer between ground-truth `WorldState` and what an
operator actually sees on the graphs/logs panel — it deliberately renders **symptoms, not
diagnoses**, so the operator does the troubleshooting work the real job requires instead of reading
an engine-supplied answer key. This topic gives the implementer the seeded-noise + attack-term model
so a new subsystem parameter or a new effect category's signature is added without breaking
determinism or leaking ground-truth labels into the UI.

## 2. Scope

Covers: the pure read-time derivation model (baseline + seeded noise + attack term), the
deliberate symptom-not-diagnosis design of attack signatures, the four-vector signature table
(jam/cyber/directed-energy/kinetic) plus the power-sag and spoof-on-integrity-flag special cases,
and the nominal-baseline overlay. Does **not** cover: the bus/payload state machine the baseline
values are read from ([R111](R111-power-and-thermal-operations.md)), or the effect-resolution math that decides whether/how
strongly an attack is currently active ([R115](R115-electronic-warfare-in-space-operations.md)/[R116](R116-cyber-operations-against-space-systems.md)).

## 3. Concepts

**Telemetry is a pure read-time derived signal, never a state mutation.** `sample`/`series`/
`telemetry_db`/`subsystem_log` all take `world` read-only and never draw the engine RNG — like
`session/scene.py`'s render-from-custody belief scene, this keeps the entire telemetry layer outside
the deterministic event log: replaying the same eventlog against the same seed reproduces byte-
identical telemetry without telemetry itself having been a recorded event.

**Each parameter value is `baseline(real state) + seeded value-noise + attack term`.** `_baseline`
reads the real `BusState`/`PayloadState` fields where they exist (battery SoC, storage fraction,
propellant fraction) and falls back to a gentle analytic orbital-drift sinusoid for free-running
analog params with no underlying state field; `_noise` adds a continuous, interpolated pseudo-random
value computed as a pure hash of `(seed, asset, param, time-bucket)` (`telemetry.py:70-81`), so the
same seed always reproduces the same noise trace at the same simulated time — there is no streaming
random-number-generator state to keep in sync with replay.

**Attack signatures are deliberately symptoms, not labels.** The module's own docstring states the
design intent explicitly: "the value (e.g. receiver RX power) deviates and may breach its own
limit, but nothing here says 'you are being jammed'" (`telemetry.py:9-11`) — the operator is expected
to diagnose the underlying attack from the pattern of which parameters moved, exactly the same
distinction the anomaly-detection literature draws between automated **out-of-limit (OOL) symptom
detection** (a measurement crosses a predefined nominal-range threshold and triggers an alarm) and
the harder **diagnosis** step of attributing that symptom to a specific cause — real spacecraft
operations centers run continuous OOL limit-checking as the first line of anomaly detection, with
causal diagnosis as a separate, often manual, downstream step
([Ibrahim et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry*,
arXiv:2406.17826](https://arxiv.org/abs/2406.17826)
([Wayback](https://web.archive.org/web/2026/https://arxiv.org/pdf/2406.17826))) — `_attack_term`
implements exactly this OOL pattern: it perturbs the raw physical value, and `status_high`/
`status_low` (from `engine/bus.py`) then classify against `soft`/`hard` thresholds, but no field
anywhere carries an attack-type label back to the UI.

**Four effect categories each leave a distinct multi-parameter signature.** Per the module
docstring's table (`telemetry.py:12-17`): EW jam raises `comms.rx_power_dbm` and lowers
`cn0_dbhz`/raises `ber`/intermittently drops `uplink_lock`; cyber raises `cdh.cpu_load_pct` and
accumulates `fsw_error_count`/`cmd_reject_count` over time since onset; directed energy lowers
`payload.snr_db` and raises `thermal.optics_temp_c`; kinetic effects produce loss-of-signal (a
destroyed asset returns `status: "los"`, not a telemetry value) — `_attack_term` keys each
perturbation off `_active`'s per-effect-category flags read from `world.active_effects`, so a new
effect category needs its own `flags[...]` entry and at least one `_attack_term` branch to be
diagnosable at all.

**Operator-applied mitigation shrinks the jam signature multiplicatively, not by removing it.**
`_mitigation` reads `payload_state.interference_mitigation` (set by `satcom.mitigate_interference`)
and bus-level `freq_hopping`, combining to a capped `0.9` mitigation fraction that scales every
jam-driven term in `_attack_term` (`jam = 1.0 - _mitigation(asset)`) — mitigation narrows the
symptom rather than erasing it, so a well-mitigated jam still shows as a smaller deviation, never a
clean nominal trace; this preserves a meaningful contrast against the no-attack nominal overlay.

**Spoofing is modeled as a distinct symptom from jamming by design.** Per the `FUTURE-WORK §10.C.14`
comments at `telemetry.py:61,93,169-171`, a spoof outcome only perturbs `integrity_flag` (toward
`0.0`) while leaving link-quality parameters (`rx_power_dbm`, `cn0_dbhz`, `ber`) at nominal — this is
a deliberate asymmetry: spoofing looks like nothing is wrong on the link itself, distinguishing it
operationally from a jam, which always degrades link quality.

**The nominal-baseline overlay is the same function with the attack term suppressed, not a separate
model.** `sample(..., nominal=True)` skips the `_active`/`_attack_term` call entirely, returning
baseline+noise only — this is the "what it should look like" ghost trace the troubleshooting UI
overlays against the live (possibly attacked) trace (`telemetry.py:178-180`); a destroyed asset still
produces a nominal trace under `nominal=True` even though its live trace reports loss-of-signal,
since loss-of-signal is itself an attack symptom, not the asset's baseline nominal state.

### Sources

- *Ibrahim, S. K. et al., European Space Agency Benchmark for Anomaly Detection in Satellite
  Telemetry, arXiv:2406.17826* — [live](https://arxiv.org/abs/2406.17826)
  · [snapshot](https://web.archive.org/web/2026/https://arxiv.org/pdf/2406.17826)
  · accessed 2026-06-27.

## 4. Operational Context

Real spacecraft operations centers run exactly this two-stage pattern at scale: automated
out-of-limit checking flags a symptom in real time, and a human operator (or a slower offline
diagnosis pass) determines the underlying cause from the pattern of which telemetry points moved
together — out-of-limit checking remains the front-line method precisely because it is cheap and
interpretable, even though it cannot by itself distinguish "why" two correlated parameters moved
(Ibrahim et al., arXiv:2406.17826, *op. cit.*). The simulator's symptom-not-label design forces the
same diagnostic skill from the operator that real telemetry monitoring demands, rather than letting
the UI hand back an attack-type answer.

## 5. Implementation Guidance

- **A new effect category needs its own flag in `_active` and at least one `_attack_term` branch**
  keyed off a real subsystem parameter — never add a UI-visible "attack type" field; the signature
  must remain inferable only from which physical parameters moved, preserving the symptom-not-label
  design.
- **A new parameter added to `PARAMS` must define a real `_baseline` source** (a `BusState`/
  `PayloadState` field) **or an explicit free-running analytic fallback** — don't add a parameter
  that silently returns `0.0`/`nominal` forever, which would make it useless as a troubleshooting
  signal.
- **Any new noise or attack computation must stay a pure function of `(seed, asset, param, t)` and
  ground-truth `world` state** — never draw the engine RNG or mutate `WorldState` inside
  `telemetry.py`, which would reopen exactly the determinism leak `scene.py`'s read-only design
  exists to prevent (MSTR-002 §1).
- **A new mitigation mechanism should scale an existing attack term multiplicatively (like
  `_mitigation`'s jam fraction), not zero it out** — full suppression would erase the diagnostic
  signal the operator needs to confirm the mitigation actually worked.
- **Preserve the nominal-overlay contract**: any new parameter must produce a sensible
  `nominal=True` trace (baseline+noise, no attack term) so the "compare to nominal" UI overlay stays
  meaningful for the new parameter too.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — the subsystem drill-down graphs/logs and the
nominal-comparison overlay are built entirely on `sample`/`series`/`subsystem_log`; a new
troubleshooting UI feature must keep reading through these functions rather than reaching into
`WorldState` directly, which would reintroduce a parallel, possibly inconsistent, signal path.

## 7. Related Topics

[R103](R103-satellite-command-and-control.md) (the C2 chain whose execution telemetry reflects), [R111](R111-power-and-thermal-operations.md) (the bus SOH model
most baseline values are read from), [R115](R115-electronic-warfare-in-space-operations.md)/[R116](R116-cyber-operations-against-space-systems.md) (the two effect categories whose
signatures this topic documents in detail).
