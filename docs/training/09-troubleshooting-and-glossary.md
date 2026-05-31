[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 10. Troubleshooting

- **`uvicorn: command not found`** — run `pip install uvicorn`, or start with
  `python3 -m uvicorn spacesim.ui_web.server:app`.
- **`ModuleNotFoundError: spacesim`** — run from the repository root (the folder containing
  `spacesim/`), or `pip install -e .`.
- **An order is rejected** — read the `reason`: `no_window` (no pass in the look-ahead),
  `roe_kinetic_not_authorized` (enable it via the `red_kinetic_authorized` dial),
  `no_weapons_quality_track` (task a sensor first), `insufficient_delta_v`, `not_owner`.
- **Nothing happens after issuing an order** — orders execute at their scheduled **window**;
  advance time (`+10m`) until the clock reaches it.
- **A satellite shows `safe_mode`/red** — it was safed (attack or bus fault); run the recovery
  procedure and remove the root cause.
- **Tests fail to collect** — install the dev extras: `pip install pytest hypothesis skyfield httpx`.

---

## 11. Glossary

- **Access window** — the interval when geometry permits an action on one of the six channels
  (command uplink, telemetry downlink, sensor observation, jam footprint, weapon engagement, RPO
  proximity).
- **Custody / track** — a cell's belief about an object; confidence **decays** between looks.
- **Weapons-quality track** — a track confident and characterized enough to authorize an engagement.
- **Fog-of-war** — a cell sees only its own assets plus what its sensors have detected.
- **Safe mode** — a protective state with the payload off; reversible but costs recovery passes.
- **The five D's** — every offensive effect resolves to *deceive / disrupt / deny / degrade /
  destroy*; the first three are reversible and low-debris, destroy is kinetic and permanent.
- **Cyber exception** — cyber is the one effect not gated by orbital passes.
- **ISL** — inter-satellite (crosslink) relay path for commands.
- **AAR** — After-Action Review: deterministic read-only replay, scrubbing, and branch comparison.
