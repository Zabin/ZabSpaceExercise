"""Curated ground-site catalog for the Vignette Creator's lat/long asset-entry form (IP-1174,
FR-5140). Parses ``docs/vignettes/GROUND-INFRASTRUCTURE.md``'s reference tables — real,
open-source-derived site coordinates already used across the vignette library — so the Creator
can offer them as a picker before a free-entry coordinate fallback, per that document's own
"Code | Real-world site | Lat | Lon | Used by vignettes" table shape (consistent across every
section of the file).

Content is data (CLAUDE.md invariant 6): this module only *reads* that markdown reference file;
it authors nothing. Cached the same way ``inject_library.yaml`` is cached in ``session/inprocess.py``.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

_DOC_PATH = Path(__file__).resolve().parent.parent.parent / "docs" / "vignettes" / "GROUND-INFRASTRUCTURE.md"

_ROW_RE = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(-?\d+(?:\.\d+)?)\s*\|\s*(-?\d+(?:\.\d+)?)\s*\|"
)

_cache: Optional[list[dict]] = None


def load_ground_sites() -> list[dict]:
    """Return ``[{code, site, lat_deg, lon_deg}, ...]`` parsed from the reference doc.

    Skips header/separator rows (``Code`` header row, ``|---|...`` rules) by requiring the Lat/Lon
    columns to parse as numbers. Returns ``[]`` (never raises) if the doc is missing or reshaped —
    the free-entry coordinate fallback the Creator's form already offers stays available either way.
    """
    global _cache
    if _cache is not None:
        return _cache
    sites: list[dict] = []
    try:
        text = _DOC_PATH.read_text(encoding="utf-8")
    except OSError:
        _cache = sites
        return sites
    for line in text.splitlines():
        m = _ROW_RE.match(line.strip())
        if not m:
            continue
        code, site, lat, lon = m.groups()
        if code.lower() == "code":   # header row
            continue
        sites.append({"code": code, "site": site, "lat_deg": float(lat), "lon_deg": float(lon)})
    _cache = sites
    return sites
