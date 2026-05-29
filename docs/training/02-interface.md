[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 3. The interface at a glance

The tool is built around three **cells**, selected with the buttons at the top:

- **White** — the facilitator. Sees **ground truth** (both sides), controls time, fires injects.
- **Blue** / **Red** — the players. Each sees only **its own assets** and whatever its sensors
  have detected (*fog-of-war*).

### The scenario picker

White Cell starts by choosing a scenario from the **vignette library** (eight are bundled):

![Vignette picker](../manual/01-vignette-picker.png)

### White Cell god-view

After **Load** → **Start**, White Cell sees the full picture: every asset on both sides, the
objectives, and the belief map.

![White god-view](../manual/02-white-godview.png)

### A player cell (fog-of-war)

Switch to **Blue**: the fleet list now shows **only Blue's assets**, and tracks show only what
Blue's sensors have found. Switch to **Red** and you'll see Red's assets — **never** Blue's.

![Blue cell](../manual/03-blue-cell.png)
![Red cell](../manual/04-red-cell.png)

### Viewers — 2D map and 3D globe

Two synchronized viewers render *render-from-custody* (own assets at true positions; other-side
objects only as **tracks** with an uncertainty volume that grows between looks):

- the **3D globe** — drag to **rotate**, **tilt** slider, **zoom** (wheel or `+/-`), **zoom-to** an
  asset, **spin**, and **reset**;
- the **2D belief map** — **zoom**, **pan** (drag), **center** on an asset, and **layer** toggles
  (tracks / grid).

Both viewers draw a low-resolution **country map** (coastlines + country borders, tied to lat/long)
behind the picture so positions read against real geography; toggle it with the **map** control.

![3D globe](../manual/14-globe-overview.png)

### Commanding & White Cell menus

The **command panel** is a menu: choose an **Actor** and the **Action** list filters to that
asset's legal actions, with a pre-filled parameter template (see §5). White Cell tunes the scenario
from the **control panel** (parameter dials, time controls, injects):

![White Cell controls](../manual/16-white-controls.png)

---
