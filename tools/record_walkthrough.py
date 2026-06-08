"""Record a short pitch walkthrough of the spacesim UI as WebM + GIF.

Drives the running FastAPI server at http://127.0.0.1:8000 with Playwright,
loading the training-basics vignette and stepping through the core operator
loop. Outputs:

    docs/manual/walkthrough.webm   — crisp recording for slack/email/web
    docs/manual/walkthrough.gif    — autoplay anywhere (README, mobile)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "manual"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR = ROOT / "tmp_walkthrough"
TMP_DIR.mkdir(exist_ok=True)

VIEWPORT = {"width": 1440, "height": 900}
URL = "http://127.0.0.1:8000/"


def caption(page, text: str, duration_ms: int = 2200) -> None:
    """Show a bottom-center caption banner for the next beat."""
    page.evaluate(
        """({text, duration}) => {
            let el = document.getElementById('__pitch_caption');
            if (!el) {
                el = document.createElement('div');
                el.id = '__pitch_caption';
                el.style.cssText = `
                    position: fixed; bottom: 36px; left: 50%;
                    transform: translateX(-50%); z-index: 99999;
                    background: rgba(10,20,32,0.92);
                    color: #e6edf7; padding: 14px 28px;
                    border-radius: 10px; font: 600 20px/1.3 system-ui, sans-serif;
                    border: 1px solid #4a7ab8;
                    box-shadow: 0 4px 24px rgba(0,0,0,0.6);
                    max-width: 80%;
                `;
                document.body.appendChild(el);
            }
            el.textContent = text;
            el.style.opacity = '1';
            clearTimeout(window.__pitch_caption_timer);
            window.__pitch_caption_timer = setTimeout(() => {
                el.style.transition = 'opacity 400ms';
                el.style.opacity = '0';
            }, duration);
        }""",
        {"text": text, "duration": duration_ms},
    )
    page.wait_for_timeout(duration_ms)


def click_if(page, selector: str, timeout: int = 2000) -> bool:
    try:
        page.locator(selector).first.click(timeout=timeout)
        return True
    except Exception:
        return False


def run() -> None:
    frames_dir = TMP_DIR / "frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)

    with sync_playwright() as pw:
        chrome_bin = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
        browser = pw.chromium.launch(headless=True, executable_path=chrome_bin)
        ctx = browser.new_context(
            viewport=VIEWPORT,
            record_video_dir=str(TMP_DIR / "video"),
            record_video_size=VIEWPORT,
        )
        page = ctx.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(800)

        # Frame snapshotter for the GIF
        frame_idx = [0]
        def snap():
            frame_idx[0] += 1
            page.screenshot(path=str(frames_dir / f"f{frame_idx[0]:04d}.png"))

        # === Beat 1: Title / scenario picker ===
        caption(
            page,
            "Space Control & Orbital Warfare PME wargame — 19 vignettes, 4 tracks",
            2400,
        )
        snap()

        # Pick training-basics + load (open Session ▾ menu first)
        page.click("#session-btn")
        page.wait_for_selector("#session-menu:not([hidden])", timeout=3000)
        page.wait_for_timeout(400)
        snap()
        page.select_option("#vignette", "training-basics")
        page.wait_for_timeout(300)
        snap()

        page.click("#load")
        page.wait_for_selector("#brief-panel:not([hidden])", timeout=8000)
        page.wait_for_timeout(900)
        # Close the menu by clicking its button again
        page.click("#session-btn")
        page.wait_for_timeout(300)
        snap()

        # === Beat 2: Mission brief auto-opens ===
        caption(
            page,
            "Mission brief auto-opens: situation, mission, ROE, success criteria",
            2600,
        )
        snap()

        # === Beat 3: Start the session (re-open Session ▾ to access Start) ===
        page.click("#session-btn")
        page.wait_for_selector("#session-menu:not([hidden])", timeout=3000)
        page.wait_for_timeout(300)
        page.click("#start")
        page.wait_for_timeout(900)
        page.click("#session-btn")  # close menu
        page.wait_for_timeout(400)
        # Collapse brief so we can see the world
        click_if(page, "#brief-toggle")
        page.wait_for_timeout(400)
        snap()

        caption(
            page,
            "Server-authoritative clock — every tab/cell sees the same sim time",
            2600,
        )
        snap()

        # === Beat 4: Switch to Blue cell ===
        page.click('button.cell[data-cell="blue"]')
        page.wait_for_timeout(900)
        snap()

        caption(
            page,
            "Blue cell: fog-of-war filter — only Blue's belief state, never ground truth",
            2800,
        )
        snap()

        # === Beat 5: Scroll to the globe / map / fleet ===
        page.evaluate("document.getElementById('globe-panel')?.scrollIntoView({block:'start'})")
        page.wait_for_timeout(600)
        snap()
        snap()

        caption(
            page,
            "3D orbital globe + 2D belief map — render only what the cell knows",
            2800,
        )
        snap()
        snap()

        # === Beat 6: Advance time +10m (use stepBy directly — white-only buttons hidden in Blue) ===
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(400)
        page.evaluate("stepBy(600)")
        page.wait_for_timeout(1400)
        snap()
        snap()

        caption(
            page,
            "Plan-first: orders queue, execute only when a pass / window opens",
            2800,
        )
        snap()

        # === Beat 7: Show fleet / Gantt activity ===
        page.evaluate("document.getElementById('activity-panel')?.scrollIntoView({block:'center'})")
        page.wait_for_timeout(800)
        snap()
        snap()

        caption(
            page,
            "Pass-timeline Gantt: 24 h window, realistic durations, 4 commands/pass",
            2800,
        )
        snap()

        # === Beat 8: Switch to Red ===
        page.evaluate("window.scrollTo(0, 0)")
        page.click('button.cell[data-cell="red"]')
        page.wait_for_timeout(900)
        snap()

        caption(
            page,
            "Red cell: jam, cyber, ASAT (when ROE permits) — five D's of counterspace",
            2800,
        )
        snap()
        snap()

        # === Beat 9: Back to White godview + final shot ===
        page.click('button.cell[data-cell="white"]')
        page.wait_for_timeout(900)
        snap()
        snap()

        caption(
            page,
            "Open-source. Python + FastAPI. 419 tests. Deterministic. LAN-ready.",
            3200,
        )
        snap()
        snap()
        page.wait_for_timeout(1200)
        snap()

        # Finalize
        video_path = page.video.path()
        ctx.close()
        browser.close()

    # Move WebM
    out_webm = OUT_DIR / "walkthrough.webm"
    shutil.move(video_path, out_webm)
    print(f"WebM written: {out_webm} ({out_webm.stat().st_size // 1024} KB)")

    # Stitch GIF from frames (downscaled for size)
    frames = sorted(frames_dir.glob("*.png"))
    if not frames:
        print("No frames captured — skipping GIF", file=sys.stderr)
        return
    print(f"Stitching {len(frames)} frames into GIF…")
    images = []
    for f in frames:
        img = Image.open(f).convert("RGB")
        # Downscale to ~720 wide for a reasonable file size
        w, h = img.size
        nw = 720
        nh = int(h * nw / w)
        img = img.resize((nw, nh), Image.LANCZOS).convert("P", palette=Image.ADAPTIVE, colors=128)
        images.append(img)

    out_gif = OUT_DIR / "walkthrough.gif"
    images[0].save(
        out_gif,
        save_all=True,
        append_images=images[1:],
        duration=600,  # ms per frame
        loop=0,
        optimize=True,
    )
    print(f"GIF written: {out_gif} ({out_gif.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    run()
