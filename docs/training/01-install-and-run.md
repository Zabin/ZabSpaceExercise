[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 1. Install — for users new to Python

> **Audience:** this section assumes you have **never used Python before**. If you have, skip to
> §1.3.

### 1.1 Install Python (3.11 or newer)

Pick the option for your operating system:

- **Windows.** Download the official installer from
  [python.org/downloads](https://www.python.org/downloads/). During installation, **check the box
  "Add python.exe to PATH"** on the first wizard screen — without it, the `python3` command won't
  work from a terminal.
- **macOS.** Easiest path is the official installer at
  [python.org/downloads](https://www.python.org/downloads/). Alternatively, if you already have
  [Homebrew](https://brew.sh): `brew install python@3.11`.
- **Linux (Debian / Ubuntu).** `sudo apt update && sudo apt install python3 python3-pip
  python3-venv`. On Fedora: `sudo dnf install python3 python3-pip`.

Verify the install in a fresh terminal window:

```bash
python3 --version    # should print Python 3.11.x or newer
```

### 1.2 Open a terminal in the repository folder

The "repository root" referred to below is the folder containing `README.md`, `spacesim/` and
`docs/`. To open a terminal pointed at it:

- **Windows.** In File Explorer, navigate to the folder, click the address bar, type `cmd` and
  press Enter — a terminal opens already at the right location.
- **macOS.** Right-click the folder in Finder → **Services → New Terminal at Folder** (enable in
  System Settings → Keyboard → Keyboard Shortcuts → Services if it's not visible).
- **Linux.** Right-click the folder in your file manager and pick "Open in Terminal", or run
  `cd /path/to/ZabSpaceExercise` in any terminal.

> **Downloaded the repo as a ZIP from GitHub?** Extracting `ZabSpaceExercise-main.zip` produces a
> folder that contains *another* folder one level down — the repository root ends up at
> `...\ZabSpaceExercise-main\ZabSpaceExercise\`, not at the top-level extracted folder. Make sure
> your terminal's prompt shows that inner `ZabSpaceExercise` path (the one containing
> `spacesim\`) before running any command below — e.g. on Windows:
> ```
> cd C:\Users\<you>\Documents\python\ZabSpaceExercise-main\ZabSpaceExercise
> ```
> Running these commands one level too high (in `ZabSpaceExercise-main`) is the most common cause
> of "module not found" / "no such file or directory" errors in this guide.

### 1.3 (Recommended) create a virtual environment

A *virtual environment* keeps this project's Python packages separate from anything else on your
machine. Run these two commands once, in the repository root:

```bash
python3 -m venv .venv          # macOS / Linux
python -m venv .venv           # Windows (cmd) — Windows installs usually register "python",
                                # not "python3"; if "python" isn't found either, try "py -m venv .venv"

# Activate it (you'll do this every time you open a fresh terminal):
#   Windows (cmd):       .venv\Scripts\activate.bat
#   Windows (PowerShell): .venv\Scripts\Activate.ps1
#   macOS / Linux:       source .venv/bin/activate
```

You'll know it worked when your terminal prompt is prefixed with `(.venv)`.

> **Windows notes.** If `python -m venv .venv` appears to hang, it's usually `venv` waiting on
> `ensurepip` to reach the network — retry with `python -m venv .venv --without-pip` and install
> packages afterward (§1.4 still works the same). If creating the environment fails with
> `PermissionError: [Errno 13] Permission denied: '...\Scripts\activate.bat'`, delete the
> partial `.venv` folder (`rmdir /s /q .venv`) and recreate it; if it keeps happening, your
> project folder is probably under OneDrive-synced `Documents`, which can lock files mid-write —
> either pause OneDrive sync or move the project to a non-synced path (e.g. `C:\dev\...`).

### 1.4 Install the project's Python packages

With the virtual environment activated (or system-wide if you skipped 1.3):

```bash
# Runtime dependencies (the engine + web server):
pip install pydantic numpy sgp4 pyyaml fastapi uvicorn

# Optional — only needed to run the test suite:
pip install pytest hypothesis skyfield httpx
```

If `pip install` fails with a "permission denied" error and you skipped step 1.3, prefix the
command with `pip install --user …` (Linux/macOS) or re-run inside the virtual environment.

### 1.5 Verify the install

```bash
python3 -m pytest
```

All tests should report **passed**. If you only installed the runtime dependencies in 1.4 (no
pytest), this command will say `pytest: command not found` — that's harmless; it just means the
test suite is unavailable.

Everything runs **offline** — the engine uses an analytic Sun model and bundled orbit math, so no
internet connection or ephemeris download is required.

### 1.6 Common install gotchas

- **`python3: command not found`** — you skipped "Add python.exe to PATH" on Windows, or your
  shell hasn't picked up the new PATH. Open a fresh terminal window.
- **`pip: command not found`** — install pip with `python3 -m ensurepip --upgrade`.
- **Older Python** (3.10 and below) — Pydantic v2 and `numpy >= 1.26` require 3.11+. Upgrade
  Python or use a virtual environment built with 3.11.
- **Slow install on Windows** — first-time `pip install numpy` can take a minute or two while it
  fetches a wheel. Subsequent runs are fast.

---

## 2. Run it

Start the web server from the repository root (with your virtual environment activated, if any):

```bash
python3 -m spacesim.ui_web              # macOS / Linux — uses spacesim.config.yaml (default: 127.0.0.1:8000)
python -m spacesim.ui_web               # Windows (cmd) — same launcher, no separate uvicorn command needed
```

This is the **only command you need to start the server** — it launches uvicorn internally, so
you do not have to install or invoke `uvicorn` yourself from the command prompt. (The `uvicorn
spacesim.ui_web.server:app` form mentioned in §2's "Changing the port" note below is an
equivalent alternative for users who prefer the uvicorn CLI directly — it's optional, not
required.)

Then open **http://127.0.0.1:8000/** in a browser. You should see the dark mission-control layout
with the `UNCLASSIFIED // TRAINING` banner. The UI works in any current desktop browser
(Chrome ≥ 100, Firefox ≥ 100, Edge ≥ 100, Safari ≥ 15.4); see
[§9 troubleshooting](09-troubleshooting-and-glossary.md) if you hit a rendering issue.

**Changing the port.** Edit `spacesim.config.yaml` at the repository root:

```yaml
server:
  host: 127.0.0.1   # use 0.0.0.0 to expose on a LAN
  port: 8000        # change this if 8000 is taken
  reload: false     # auto-reload on code change (dev only)
```

Then re-run `python3 -m spacesim.ui_web`. Point the browser at the matching port. Set
`SPACESIM_CONFIG=/path/to/other.yaml` to load a different file. If you prefer the `uvicorn` CLI,
pass `--port N --host H` directly — the config file is only read by the `python3 -m spacesim.ui_web`
launcher.

Press **Ctrl-K** (or **⌘-K** on macOS) any time to open the command palette — the fastest way to
navigate.

> Prefer a script or an air-gapped box with no browser? Every action is also available through the
> in-process Python API and the HTTP API — see [§9](#9-http-api-reference) and the
> *headless walkthrough* at the end of [§4](#4-your-first-exercise).

### 2.1 Multi-tab and LAN multiplayer

The same server supports **multiple cells on multiple tabs (or machines on a LAN)**. The pattern:

1. **White facilitator** opens `http://127.0.0.1:8000/`, clicks **Session ▾** → picks a
   vignette → **Load**, then **▶ Start**. The URL changes to something like `/#sess-1` — that
   is the shareable join link.
2. **Each player** opens that same URL in their own tab (or another LAN machine pointed at the
   host IP — see below). They click their cell button (**Blue** or **Red**). Their tab
   automatically joins `sess-1` and starts polling.
3. The **server-authoritative clock** advances exactly once regardless of how many tabs are
   polling. White's ⏸ Pause / ▶ Resume button drives it for everyone. Manual +1m / +10m / +1h
   jumps are White-only too.

To run across a LAN, bind to the host IP instead of loopback:

```bash
uvicorn spacesim.ui_web.server:app --host 0.0.0.0 --reload
```

Then Blue and Red browse to `http://<host-LAN-IP>:8000/#sess-1`. There's no separate
"multiplayer build" — the same FastAPI server, the same fog-of-war boundary, and the same UI
handle both single-machine and LAN cooperative play. **Trust model:** any tab can pick any cell
(White can't lock cells); appropriate for a facilitator-run PME exercise on a private LAN, not
for hostile-side gaming.

**Multi-monitor pop-outs.** Open **View ▾ → Pop out (multi-screen)** and pick one of the
preset layouts (3D globe, 2D map, Globe + Map, Fleet & telemetry, Order compose, AAR
timeline). Each pop-out is a new window that joins the same session and shows only the
requested panels — drag it to a second monitor. Pop-outs keep working even if the parent tab
closes, since they all talk directly to the server.

---
