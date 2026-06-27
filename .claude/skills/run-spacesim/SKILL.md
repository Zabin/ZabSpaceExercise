---
name: run-spacesim
description: Build, launch, drive, and screenshot the Space Control & Orbital Warfare Exercise Simulator (spacesim) — the FastAPI + browser PME wargaming web app. Use when asked to run, start, serve, smoke-test, screenshot, or drive the spacesim UI, or to exercise its session/scene/telemetry endpoints.
---

# Run spacesim (Space Control & Orbital Warfare Exercise Simulator)

`spacesim` is a single-machine PME wargaming tool: a deterministic Python engine behind a
FastAPI server (`spacesim.ui_web.server:app`) that serves a self-contained browser front end
(vanilla JS canvas — 3D globe + 2D belief map + telemetry drill-down). No CDN, no build step
for the front end; the engine is offline and deterministic.

The browser is driven headlessly with **Playwright** pointed at the container's bundled
Chromium. The agent path is the driver script:
**`.claude/skills/run-spacesim/driver.py`** — it boots the server, drives a full session in a
real browser, and writes a screenshot.

All paths below are relative to the repo root (`/home/user/ZabSpaceExercise`). Run from there.

## Prerequisites

Python 3.11. The engine + UI + test deps and Playwright are already importable in this
container. To reproduce on a clean machine:

```bash
pip install pydantic numpy sgp4 pyyaml pytest hypothesis skyfield fastapi uvicorn httpx pillow playwright
```

The driver does **not** use Playwright's pinned browser revision (it's missing on disk). It
auto-detects the Chromium that ships under `/opt/pw-browsers/chromium-*/chrome-linux/chrome`
and launches it headless with `--no-sandbox` (no `xvfb` needed).

## Run (agent path) — drive the UI + screenshot

One command boots the server, drives a session, and screenshots the rendered UI:

```bash
python3 .claude/skills/run-spacesim/driver.py --shot /tmp/spacesim-ui.png
```

Expected output (and a 1400-wide full-page PNG at the `--shot` path):

```
OK  vignette=training-basics cell=blue
    sim-time='2030-03-15T06:30:01Z'  fleet_rows=3  actor_options=2
    features={'panel_tools': 10, 'panels_menu': True, 'target_picker': True, 'sparklines': 19}
    screenshot -> /tmp/spacesim-ui.png
```

The driver opens the `Session ▾` menu (the vignette picker, Load and Start live there since the
toolbar refactor), loads the vignette → clicks Start → presses Escape to close the menu so the
toolbar buttons aren't overlaid → steps sim time 3× (+10 min) **while still on White** (the
+10m buttons are in the `white-only` group and disappear after the cell switch) → switches to
the requested cell → clicks the first fleet row to populate the telemetry drill-down →
screenshots full page. It reads back `sim-time`, fleet row count, actor-option count, AND a
post-audit `features` probe (panel-manager tool bars + Panels menu section + valid-target
picker + sparklines present) so a drift between the live UI and the driver fails loudly with
zero counts instead of a confusing screenshot. Options:

```bash
python3 .claude/skills/run-spacesim/driver.py --vignette leo-isr-denial --cell red --shot /tmp/spacesim-red.png
python3 .claude/skills/run-spacesim/driver.py --url http://127.0.0.1:8000   # attach to an already-running server
```

`--cell` is one of `white|blue|red`. Get vignette ids from `GET /api/vignettes` (e.g.
`training-basics`, `leo-isr-denial`, `geo-rpo-shadowing`).

## Run (backend only) — no browser

Serve the app and drive it with `curl` (the front end is just a client of these endpoints; the
browser never touches the engine):

```bash
uvicorn spacesim.ui_web.server:app --port 8000    # then open http://127.0.0.1:8000/
```

Full session lifecycle via the API (each call verified to return 200 / real JSON):

```bash
B=http://127.0.0.1:8000
SID=$(curl -s -X POST $B/api/sessions -H 'Content-Type: application/json' \
      -d '{"vignette_id":"training-basics","seed":0}' \
      | python3 -c 'import sys,json;print(json.load(sys.stdin)["session"])')
curl -s -X POST $B/api/sessions/$SID/start
curl -s -X POST $B/api/sessions/$SID/step -H 'Content-Type: application/json' -d '{"dt_sim_s":600}'
curl -s $B/api/sessions/$SID/scene/blue       # fog-filtered belief scene for the Blue cell
curl -s $B/api/sessions/$SID/godview          # White-cell ground truth
curl -s $B/api/sessions/$SID/objectives
```

Route prefix is `/api`; the front end is mounted at `/`. See `grep -nE '@app\.(get|post)'
spacesim/ui_web/server.py` for all 29 routes (sessions, step/advance/rewind/undo, order/cancel,
windows, view/scene/telemetry, godview, eventlog, objectives, aar, alarms, save/load).

## Test

```bash
python3 -m pytest                  # 473 passed, 3 skipped (~95s); testpaths = spacesim/tests
python3 -m pytest spacesim/tests/test_determinism.py    # the canonical determinism gate
```

## Gotchas

- **Playwright's pinned browser is missing.** A plain `p.chromium.launch()` fails with
  `Executable doesn't exist at .../chrome-headless-shell-1223/...`. The on-disk browser is
  `chromium-1194`. The driver works around this with `executable_path=` to the real binary —
  do **not** run `playwright install` (it tries to fetch over the network). Reuse the driver's
  `CHROME_EXE` detection if you write your own browser script.
- **API routes live under `/api`**, but the static front end is mounted at `/` with
  `html=True`. `GET /` returns the SPA; `GET /api/vignettes` returns JSON. Don't hit `/scene`
  expecting JSON — it's `/api/sessions/{sid}/scene/{cell}`.
- **Fog-of-war is enforced server-side.** `scene/blue` and `scene/red` are filtered belief
  views; only `godview` has ground truth. A cell cannot read another cell's telemetry — the
  endpoint will refuse. This is by design, not a bug.
- **The front end is canvas-rendered** (globe, map, telemetry graphs). There's little semantic
  DOM inside the canvases, so assert on the surrounding controls (`#now`, `#assets tbody tr`,
  `#o-actor option`) and verify visuals from the screenshot, as the driver does.
- **Toolbar buttons live behind a Session ▾ menu pop-up.** The vignette picker, Load and Start
  are inside `#session-menu` and are `hidden` until you click `#session-btn`. The menu pop also
  overlays the cell-selector / +10m buttons at common viewport widths, so close it (press
  Escape — the app's keydown handler closes any open menu) before clicking other toolbar
  controls. The driver does both.
- **The +10m / Pause / Rewind buttons are `white-only`.** They are hidden when the cell isn't
  White. Advance sim time before switching cell, or switch back to White to drive them.
- **`step` sub-steps the clock**; stepping `dt_sim_s` past short LEO passes still resolves
  intermediate scheduled events. Expect `sim-time` to advance by exactly the step you asked.
- The engine is deterministic: same `(vignette, seed)` → identical run. Vary `--vignette`/
  `seed` to see different state, not re-runs.

## Troubleshooting

- `server did not come up at http://127.0.0.1:8000` → a previous uvicorn may hold the port.
  `pkill -f 'uvicorn spacesim'` (note: that pattern also matches the driver's own command line
  if it's running) or pass `--port 8001`.
- `No Chromium found under /opt/pw-browsers/` → the bundled browser isn't present; this skill's
  screenshot path won't work, but the backend/curl path and `pytest` still do.
- Screenshot looks blank/partial → give the sim more motion: the driver already steps time 3×;
  increase the loop or step size in `driver.py` if a vignette starts with assets below the
  horizon.
