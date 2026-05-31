"""Generate spacesim/ui_web/static/world.json (low-res world coastlines + country borders).

Run once at build time; the output JSON is COMMITTED so the app stays fully offline at runtime
(no map data download, no CDN). Source is the pip-installable Basemap dataset; polylines are
Douglas-Peucker simplified and rounded to keep the file small. If Basemap can't be imported, a
coarse vendored fallback outline is written so the viewers always have *something* to draw.

    python3 tools/build_coastlines.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "spacesim" / "ui_web" / "static" / "world.json"
EPSILON_DEG = 0.4   # drop vertices closer than this (degrees) to the last kept vertex


def _decimate(points, eps):
    """Shape-preserving decimation: keep a vertex only if it is >= eps from the last kept one.

    Unlike Douglas-Peucker this never collapses closed coastline rings to a point, so islands and
    continents both survive at low resolution."""
    if len(points) < 2:
        return points
    out = [points[0]]
    for p in points[1:-1]:
        if abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) >= eps:
            out.append(p)
    out.append(points[-1])
    return out


def _simplify(segs):
    out = []
    for seg in segs:
        pts = [(round(float(x), 2), round(float(y), 2)) for x, y in seg]
        s = _decimate(pts, EPSILON_DEG)
        if len(s) >= 2 and len(set(s)) >= 2:  # keep anything with two distinct vertices
            out.append(s)
    return out


def _from_basemap():
    from mpl_toolkits.basemap import Basemap
    m = Basemap(projection="cyl", resolution="l")
    coast = list(m.coastsegs)  # already (lon, lat) in cylindrical
    try:
        borders, _ = m._readboundarydata("countries")  # list of (lon,lat) polylines
    except Exception:
        borders = []
    return _simplify(coast), _simplify(borders)


def _fallback():
    """A very coarse continental outline (used only if Basemap is unavailable)."""
    box = lambda w, e, s, n: [(w, s), (e, s), (e, n), (w, n), (w, s)]
    coast = [box(-170, -30, 8, 72), box(-82, -34, -56, 13), box(-12, 60, 35, 71),
             box(10, 52, -35, 37), box(60, 150, 8, 75), box(112, 154, -39, -10)]
    return coast, []


def main():
    try:
        coast, borders = _from_basemap()
        src = "basemap (resolution=l)"
    except Exception as exc:  # noqa: BLE001 — any import/runtime failure → fallback
        print(f"basemap unavailable ({exc}); writing coarse fallback outline")
        coast, borders = _fallback()
        src = "fallback"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"coast": coast, "borders": borders}, separators=(",", ":")))
    pts = sum(len(s) for s in coast) + sum(len(s) for s in borders)
    print(f"wrote {OUT} from {src}: {len(coast)} coast + {len(borders)} border polylines, "
          f"{pts} points, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
