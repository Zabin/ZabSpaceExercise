[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 8. White Cell facilitation

**Hot-seat vs. LAN cooperative.** White can run a session two ways:

- **Hot-seat (single browser):** White loads a vignette and presses Start, then uses the cell
  buttons to switch seats between turns. The ⏸ Handover button blurs the screen between cells.
- **LAN cooperative (multi-tab / multi-machine):** White loads + starts the session, copies the
  URL (`…/#sess-N`), and shares it. Each player opens that URL — same machine in another tab,
  or another LAN box pointed at the host — and picks their cell. The server-authoritative
  clock advances exactly once regardless of tab count. White retains time control: only the
  White tab sees ⏸ Pause / ▶ Resume and the +1m/+10m/+1h jumps.

See [§1.2.1 multi-tab and LAN](01-install-and-run.md#21-multi-tab-and-lan-multiplayer) for the
host-binding command (`--host 0.0.0.0`) and pop-out windows (View ▾ → Pop out).

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

**Inject library + builder.** Beyond the per-vignette injects, the White-Cell panel ships a
five-template **library** (`debris_field_500km`, `gnss_jam_regional`, `rpo_ambiguous`,
`gs_outage_diego_garcia`, `space_weather_severe`) and a small builder UI:

1. **Build / schedule inject** disclosure opens an inline form.
2. Pick a template → its effects JSON loads in the editor → adjust any field.
3. Choose schedule: **Now** (immediate), **+ N seconds from now**, or **Absolute UTC**
   (paste-from-UTC-clock).
4. **Schedule / fire** posts to `POST /api/sessions/{sid}/inject` with `at_sim_t` set.

Future-dated injects are scheduled deterministically through the event log — they replay
byte-identical on save/resume and through the AAR scrub. Past timestamps clamp to "now"; no
backwards time travel.

![White-Cell inject builder](../manual/40-inject-builder.png)

```bash
# Schedule a severe space-weather storm to fire 60 s from now
curl -X POST http://127.0.0.1:8000/api/sessions/<SID>/inject -H 'Content-Type: application/json' -d '{
  "inject": {"effects": [
    {"type": "space_weather", "severity": "severe"},
    {"type": "message", "to": ["white","blue","red"], "text": "Geomag storm advisory"}
  ]},
  "at_sim_t": 1893456060000000
}'
```

The library lives at `spacesim/content/inject_library.yaml` — add new entries there and they show
up in the dropdown on next session load.

**Coaching notes.** A vignette can carry an optional `coaching: list[{at_sim_t?, cell, title, body}]`
field. The Coaching sidebar surfaces notes whose target cell matches the active cell (or
`white` = visible to all) and whose `at_sim_t` is in the past. Use these for "discuss this decision
in the AAR" pointers without breaking the player's screen.

**`ops_fidelity`.** `tactical` collapses each satellite's bus to a single health bar (focus on
space-control decisions); `realistic` (default) shows the SOH parameters; `full_ttc` adds detailed
subsystem telemetry for TT&C-operator training.

---
