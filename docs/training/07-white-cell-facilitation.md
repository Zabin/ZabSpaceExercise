[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 8. White Cell facilitation

**Parameters (dials).** Every vignette exposes typed parameters with safe defaults — force levels,
authorities/ROE (e.g. `red_kinetic_authorized`), Red behavior (`red_doctrine_profile`,
`red_ew_intensity`), environment (`landing_window_start_s`), and fidelity/fog (`fog_of_war`,
`ops_fidelity`, `safe_mode_susceptibility`). Set them at load time:

```python
api.load_vignette("leo-isr-denial", overrides={"red_kinetic_authorized": True})
```

**Time control.** White Cell owns the clock: step forward (`+1m/+10m/+1h`), **rewind** to any
point, **undo** the last actions, and **branch** by continuing differently after a rewind — all
byte-exact thanks to the deterministic core.

**Injects.** Scripted or manual events (`commercial_imagery_leak`, `patch_modem`, …) reveal assets,
patch vulnerabilities, raise political consequences, or message a cell. Fire one with the
**Fire inject…** button or `POST /inject`.

**`ops_fidelity`.** `tactical` collapses each satellite's bus to a single health bar (focus on
space-control decisions); `realistic` (default) shows the SOH parameters; `full_ttc` adds detailed
subsystem telemetry for TT&C-operator training.

---
