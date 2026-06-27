#!/usr/bin/env python3
"""Launch the spacesim web UI, drive a full session in a real browser, screenshot it.

This is the agent-facing harness for the FastAPI + browser front end. It:
  1. boots `uvicorn spacesim.ui_web.server:app` as a subprocess (unless --url given),
  2. waits for the backend to answer,
  3. opens the page in the bundled Playwright Chromium,
  4. drives the real UI (load vignette -> start -> step time -> pick a cell -> drill a subsystem),
  5. writes a PNG screenshot, and
  6. tears everything down.

The container has no `chromium-cli` and the Python Playwright's pinned browser revision does
not match the one on disk, so we point Playwright at the Chromium that EXISTS via
`executable_path` (see CHROME_EXE below). Run from the repo root.

Usage:
    python3 .claude/skills/run-spacesim/driver.py                 # boot server + screenshot
    python3 .claude/skills/run-spacesim/driver.py --vignette leo-isr-denial --cell red
    python3 .claude/skills/run-spacesim/driver.py --url http://127.0.0.1:8000  # attach to running server
    python3 .claude/skills/run-spacesim/driver.py --shot /tmp/spacesim.png
"""
from __future__ import annotations

import argparse
import glob
import subprocess
import sys
import time
import urllib.request

# The Chromium that actually ships in this container. Playwright's bundled-revision lookup
# fails ("Executable doesn't exist at .../chrome-headless-shell-..."), so pin the real one.
_CANDIDATES = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
CHROME_EXE = _CANDIDATES[-1] if _CANDIDATES else None


def wait_for(url: str, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


def drive(base: str, vignette: str, cell: str, shot: str) -> None:
    from playwright.sync_api import sync_playwright

    if not CHROME_EXE:
        sys.exit("No Chromium found under /opt/pw-browsers/. Cannot drive the browser.")

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_EXE, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1400, "height": 1600})
        page.goto(base + "/", wait_until="networkidle")
        assert "Orbital Warfare" in page.title(), f"unexpected title: {page.title()!r}"

        # Toolbar refactor: the vignette picker, Load and Start buttons live inside the
        # Session ▾ menu pop-up. Open the menu so its controls become visible/clickable,
        # then drive them. The menu auto-closes on outside-click (e.g. when we click a
        # cell button later).
        page.click("#session-btn")
        page.wait_for_selector("#session-menu:not([hidden])", timeout=5000)
        # Wait until the vignette list is populated (loadVignettes() runs async on boot).
        page.wait_for_function(
            "() => document.querySelectorAll('#vignette option:not([disabled])').length > 0",
            timeout=10000,
        )
        page.select_option("#vignette", vignette)
        page.click("#load")
        page.wait_for_function("() => !document.getElementById('start').disabled", timeout=10000)
        page.click("#start")

        # Close the Session menu before reaching for toolbar buttons — the menu pop-up
        # extends ~220px leftward from the Session ▾ button and at narrow viewports
        # overlays the cell selector and the white-only +10m row. The app's keydown
        # handler closes any open menu on Escape.
        page.keyboard.press("Escape")
        page.wait_for_selector("#session-menu", state="hidden", timeout=5000)

        # Advance sim time WHILE STILL ON WHITE — the +10m buttons are in the
        # `white-only` toolbar group and disappear after the cell switch. Doing this
        # first guarantees the same +30 min of motion regardless of the requested cell.
        for _ in range(3):
            page.click("button[data-step='600']")
            page.wait_for_timeout(400)

        # Switch cell.
        page.click(f".cell[data-cell='{cell}']")
        page.wait_for_timeout(400)

        # Drill into the first fleet row to exercise the telemetry panel, if any rows exist.
        rows = page.query_selector_all("#assets tbody tr")
        if rows:
            rows[0].click()
            page.wait_for_timeout(600)

        # Read back live state to prove the UI actually rendered data, not an error page.
        now = page.text_content("#now") or ""
        n_assets = len(page.query_selector_all("#assets tbody tr"))
        n_actors = page.eval_on_selector_all("#o-actor option", "els => els.length")
        # Verify post-audit features are present (panel manager + valid-target picker +
        # connected thumbnail/large-graph sparklines). A missing feature means the driver
        # and the live UI have drifted again.
        feature = page.evaluate("""() => ({
            panel_tools: document.querySelectorAll('.panel-tools').length,
            panels_menu: !!document.getElementById('panels-section'),
            target_picker: !!document.getElementById('o-target-pick'),
            sparklines: document.querySelectorAll('#drill-params .spark').length,
        })""")
        page.screenshot(path=shot, full_page=True)
        browser.close()

    print(f"OK  vignette={vignette} cell={cell}")
    print(f"    sim-time={now.strip()!r}  fleet_rows={n_assets}  actor_options={n_actors}")
    print(f"    features={feature}")
    print(f"    screenshot -> {shot}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", help="attach to an already-running server instead of booting one")
    ap.add_argument("--vignette", default="training-basics")
    ap.add_argument("--cell", default="blue", choices=["white", "blue", "red"])
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--shot", default="/tmp/spacesim-ui.png")
    args = ap.parse_args()

    proc = None
    base = args.url
    try:
        if not base:
            base = f"http://127.0.0.1:{args.port}"
            proc = subprocess.Popen(
                ["uvicorn", "spacesim.ui_web.server:app", "--port", str(args.port)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        if not wait_for(base + "/api/vignettes"):
            sys.exit(f"server did not come up at {base}")
        drive(base, args.vignette, args.cell, args.shot)
    finally:
        if proc:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    main()
