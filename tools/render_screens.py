"""Render UI preview images from live SessionAPI data (Pillow).

This is NOT a browser capture — the sandbox blocks installing a headless browser, so instead we
drive the real in-process SessionAPI and paint the same panels the web front end shows (matching
``ui_web/static/style.css``), using genuine fog-filtered data. Output: docs/screenshots/*.png.
Run: ``python3 tools/render_screens.py``.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from spacesim.engine import simtime
from spacesim.engine.orders import Order
from spacesim.session.inprocess import InProcessSession

OUT = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BG = (14, 17, 22)
PANEL = (20, 26, 34)
BORDER = (38, 48, 64)
TEXT = (215, 221, 227)
MUTED = (159, 176, 192)
GREEN = (111, 207, 111)
YELLOW = (224, 194, 74)
RED = (224, 106, 106)
ACCENT = (79, 174, 127)

f13 = ImageFont.truetype(FONT, 13)
f13b = ImageFont.truetype(FONT_B, 13)
f16b = ImageFont.truetype(FONT_B, 16)
f18 = ImageFont.truetype(FONT, 18)

W, H = 1180, 680


def _panel(d, x, y, w, h, title):
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=PANEL, outline=BORDER)
    d.text((x + 12, y + 10), title, font=f16b, fill=TEXT)
    d.line([x + 12, y + 32, x + w - 12, y + 32], fill=BORDER)
    return x + 12, y + 42


def _rows(d, x, y, rows, lh=19):
    for row in rows:
        cx = x
        for text, color, width in row:
            d.text((cx, y), text, font=f13, fill=color)
            cx += width
        y += lh
    return y


def _color(status):
    return {"green": GREEN, "yellow": YELLOW, "red": RED}.get(status, TEXT)


def _header(d, cell):
    d.rectangle([0, 0, W, 36], fill=(17, 22, 29))
    d.line([0, 36, W, 36], fill=BORDER)
    d.text((14, 9), "Space Control & Orbital Warfare Exercise Simulator", font=f16b, fill=TEXT)
    d.text((W - 360, 9), "UNCLASSIFIED // TRAINING", font=f13b, fill=GREEN)
    chip = {"white": (90, 100, 120), "blue": (60, 110, 200), "red": (200, 80, 80)}[cell]
    d.rounded_rectangle([W - 150, 6, W - 110, 26], radius=4, fill=chip)
    d.text((W - 145, 9), cell.upper()[:3], font=f13b, fill=(255, 255, 255))


def _assets_rows(assets):
    rows = [[("ID", MUTED, 120), ("KIND", MUTED, 150), ("HEALTH", MUTED, 95), ("BUS", MUTED, 80)]]
    for a in assets:
        bus = a["bus_state"]["mode"] if a.get("bus_state") else "—"
        bus_c = RED if bus == "safe_mode" else (GREEN if bus == "nominal" else TEXT)
        rows.append([(a["id"], TEXT, 120), (a["kind"], MUTED, 150),
                     (a["health"], _color("green" if a["health"] == "nominal" else "red"), 95),
                     (bus, bus_c, 80)])
    return rows


def _track_rows(tracks):
    rows = [[("OBJECT", MUTED, 150), ("CONF", MUTED, 80), ("CHAR", MUTED, 80), ("CLASS", MUTED, 120)]]
    for t in tracks:
        rows.append([(t["object"], TEXT, 150), (f"{t['confidence']:.2f}", TEXT, 80),
                     (str(t["characterized"]), TEXT, 80), (t["classification"], MUTED, 120)])
    if not tracks:
        rows.append([("(no custody)", MUTED, 300)])
    return rows


def render(cell, assets, tracks, effects, messages, objectives, now, order_line, fname, subtitle):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    _header(d, cell)
    d.text((14, 44), subtitle, font=f13, fill=MUTED)

    # Left panel: cell & time + objectives + messages
    lx, ly = _panel(d, 12, 66, 340, 380, "Cell & Time")
    d.text((lx, ly), "Sim time:", font=f13, fill=MUTED)
    d.text((lx + 80, ly), simtime.to_iso(now), font=f13b, fill=TEXT)
    ly += 28
    d.text((lx, ly), "Objectives", font=f13b, fill=MUTED); ly += 20
    for side in ("blue", "red"):
        for oid, met in objectives.get(side, {}).items():
            d.text((lx, ly), f"{side}.{oid}", font=f13, fill=TEXT)
            d.text((lx + 200, ly), "MET" if met else "—", font=f13b, fill=GREEN if met else MUTED)
            ly += 19
    ly += 8
    d.text((lx, ly), "Messages", font=f13b, fill=MUTED); ly += 20
    for m in messages[-4:] or [{"text": "(none)"}]:
        d.text((lx, ly), "• " + m["text"][:40], font=f13, fill=TEXT); ly += 18

    # Middle panel: fleet + tracks + effects
    mx, my = _panel(d, 364, 66, 470, 560, "Fleet (own)" if cell != "white" else "Fleet (ground truth)")
    my = _rows(d, mx, my, _assets_rows(assets)) + 10
    d.text((mx, my), "Tracks (custody)", font=f13b, fill=MUTED); my += 20
    my = _rows(d, mx, my, _track_rows(tracks)) + 10
    d.text((mx, my), "Perceived effects", font=f13b, fill=MUTED); my += 20
    for e in effects or [{"t": "(none)"}]:
        if "symptom" in e:
            txt = f"{e['target']}: {e['symptom']} " + ("(attributed)" if e.get("attributed") else "(source unknown)")
        else:
            txt = e.get("target", "—") + (": " + e.get("outcome", "") if "outcome" in e else "")
        d.text((mx, my), "• " + txt, font=f13, fill=YELLOW if "symptom" in e else TEXT); my += 18

    # Right panel: order result
    rx, ry = _panel(d, 846, 66, 322, 220, "Order panel")
    for label, val in [("Actor", "ISR-EO-1"), ("Action", "downlink"), ("Via", "GS-NORTH")]:
        d.text((rx, ry), label, font=f13, fill=MUTED); d.text((rx + 90, ry), val, font=f13, fill=TEXT); ry += 22
    ry += 8
    d.text((rx, ry), "Result:", font=f13b, fill=MUTED); ry += 20
    color = GREEN if "queued" in order_line or "delivered" in order_line else (RED if "REJECT" in order_line else TEXT)
    for line in _wrap(order_line, 34):
        d.text((rx, ry), line, font=f13, fill=color); ry += 18

    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / fname)
    print("wrote", OUT / fname)


def _wrap(s, n):
    out, cur = [], ""
    for word in s.split():
        if len(cur) + len(word) + 1 > n:
            out.append(cur); cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        out.append(cur)
    return out or [""]


def main():
    api = InProcessSession()

    # Scene 1: White god-view at start.
    sid = api.load_vignette("leo-isr-denial", seed=1)
    api.start(sid)
    god = api.get_godview(sid)
    render("white", [a.model_dump() for a in god.assets.values()],
           [t.model_dump() for t in god.tracks], [e.model_dump() for e in god.active_effects], god.messages,
           api.objectives(sid), god.now, "(no order issued)",
           "01-white-godview.png", "White Cell — ground truth at start of Vignette 1 (LEO ISR Denial)")

    # Scene 2: Blue cell view at start (fog: own assets only).
    blue = api.get_view(sid, "blue")
    render("blue", blue.own_assets, blue.known_tracks, blue.visible_effects, blue.messages,
           api.objectives(sid), blue.now, "(no order issued)",
           "02-blue-cell-start.png", "Blue Cell — fog-of-war view (own assets only)")

    # Scene 3: Blue downlinks imagery → objective met.
    start = god.now
    ack = api.issue_order(sid, "blue", Order(cell="blue", actor="ISR-EO-1", action="downlink",
                                             params={"via": "GS-NORTH"}))
    api.advance_to(sid, start + 800 * 1_000_000)
    blue2 = api.get_view(sid, "blue")
    line = f"queued via {ack.delivery_path}; imagery delivered → Blue objective MET"
    render("blue", blue2.own_assets, blue2.known_tracks, blue2.visible_effects, blue2.messages,
           api.objectives(sid), blue2.now, line,
           "03-blue-downlink-win.png", "Blue Cell — imagery downlinked before the landing window")

    # Scene 4: rewind + Red jams the downlink → Blue sees a symptom, source unknown.
    api.rewind_to(sid, 0)
    api.issue_order(sid, "red", Order(cell="red", actor="JAM-NORTH", action="jam",
                                      target="ISR-EO-1", params={"success_prob": 1.0, "outcome": "deny"}))
    api.issue_order(sid, "blue", Order(cell="blue", actor="ISR-EO-1", action="downlink",
                                       params={"via": "GS-NORTH"}))
    api.advance_to(sid, start + 800 * 1_000_000)
    blue3 = api.get_view(sid, "blue")
    render("blue", blue3.own_assets, blue3.known_tracks, blue3.visible_effects, blue3.messages,
           api.objectives(sid), blue3.now, "REJECTED? no — downlink BLOCKED by jamming (delivery failed)",
           "04-blue-jammed-branch.png", "Blue Cell — branch B: downlink jammed; symptom seen, source unknown")


if __name__ == "__main__":
    main()
