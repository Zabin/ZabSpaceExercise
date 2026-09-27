"""Bulk multi-object import parsing (IP-1190, FR-5220).

Two file-shaped parsers, both returning a common per-object dict shape that
``SessionManager.bulk_import()`` resolves against a caller-supplied side/template assignment
map: multi-object TLE text, and CCSDS OMM in KVN (Key=Value Notation) form only — XML OMM is
explicitly out of scope for this package (see IP-1190's own Risks).

Design Decision 1 (IP-1190): a file that contains zero recognizable blocks of its claimed shape
is rejected outright with a ``ValueError`` *before* any object is processed — distinct from a
recognizable block that later fails element-level validation (an existing block that is itself
malformed is still returned here, for ``bulk_import()``'s per-object force-add attempt to reject
individually; parsing never drops it).
"""

from __future__ import annotations

_TLE_LINE1_PREFIX = "1 "
_TLE_LINE2_PREFIX = "2 "
_TLE_LINE_MIN_LEN = 69

# CCSDS OMM (KVN) keywords whose mere presence marks a file as OMM-shaped, per Design Decision 1.
_OMM_RECOGNITION_KEYS = frozenset({
    "CCSDS_OMM_VERS", "META_START", "META_STOP", "SEMI_MAJOR_AXIS",
})

_OMM_ELEMENT_KEYS = (
    "SEMI_MAJOR_AXIS", "ECCENTRICITY", "INCLINATION",
    "RA_OF_ASC_NODE", "ARG_OF_PERICENTER", "MEAN_ANOMALY",
)


def _looks_like_tle_line1(line: str) -> bool:
    return line.startswith(_TLE_LINE1_PREFIX) and len(line) >= _TLE_LINE_MIN_LEN


def _looks_like_tle_line2(line: str) -> bool:
    return line.startswith(_TLE_LINE2_PREFIX) and len(line) >= _TLE_LINE_MIN_LEN


def parse_multi_tle(text: str) -> list[dict]:
    """Split a multi-object TLE text file into per-object dicts.

    Each object may be preceded by an optional name line. A block is captured (for later
    per-object validation) as soon as a line starting with ``"1 "`` is found, together with
    whatever the following line is — even if that following line is itself malformed — so a
    single bad block never disappears silently. The file as a whole is rejected (``ValueError``)
    only if it contains *zero* fully well-formed blocks (Design Decision 1).
    """
    lines = [ln for ln in (raw.rstrip("\r\n") for raw in text.splitlines()) if ln.strip() != ""]
    n = len(lines)
    objects: list[dict] = []
    well_formed_found = False
    i = 0
    seq = 0
    while i < n:
        line = lines[i]
        name = None
        if line.startswith(_TLE_LINE1_PREFIX):
            l1_idx = i
        elif i + 1 < n and lines[i + 1].startswith(_TLE_LINE1_PREFIX):
            name = line.strip()
            l1_idx = i + 1
        else:
            i += 1
            continue
        l1 = lines[l1_idx]
        l2 = lines[l1_idx + 1] if l1_idx + 1 < n else ""
        if _looks_like_tle_line1(l1) and _looks_like_tle_line2(l2):
            well_formed_found = True
        raw_id = name or (l1[2:7].strip() if len(l1) >= 7 and l1[2:7].strip() else f"OBJECT-{seq}")
        objects.append({"raw_id": raw_id, "format": "tle", "line1": l1, "line2": l2})
        seq += 1
        i = l1_idx + 2
    if not well_formed_found:
        raise ValueError("no recognizable TLE blocks found in file")
    return objects


def _split_omm_kvn_blocks(text: str) -> list[dict]:
    pairs: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("COMMENT") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs.append((key.strip(), value.strip()))

    blocks: list[dict] = []
    current: dict = {}
    seen_object = False
    for key, value in pairs:
        if key == "OBJECT_NAME":
            if seen_object and current:
                blocks.append(current)
            current = {}
            seen_object = True
        if seen_object:
            current[key] = value
    if seen_object and current:
        blocks.append(current)
    return blocks


def parse_ccsds_omm(text: str) -> list[dict]:
    """Parse CCSDS OMM in KVN (Key=Value Notation) form into per-object element dicts.

    A file is recognized as OMM-shaped if it contains at least one line whose keyword is one of
    ``_OMM_RECOGNITION_KEYS``; otherwise rejected outright (Design Decision 1). Objects are split
    on each new ``OBJECT_NAME`` key. A block missing one of the required Keplerian elements is
    still returned (with that key's value ``None``) — the caller's per-object force-add attempt
    reports the specific failure, parsing itself never drops a recognizable block.
    """
    recognizable = any(
        line.split("=", 1)[0].strip() in _OMM_RECOGNITION_KEYS
        for line in text.splitlines() if "=" in line
    )
    blocks = _split_omm_kvn_blocks(text) if recognizable else []
    if not recognizable or not blocks:
        raise ValueError("no recognizable CCSDS OMM (KVN) blocks found in file")

    objects: list[dict] = []
    for seq, block in enumerate(blocks):
        raw_id = block.get("OBJECT_NAME") or block.get("OBJECT_ID") or f"OBJECT-{seq}"

        def _float(key: str) -> float | None:
            value = block.get(key)
            if value is None:
                return None
            try:
                return float(value)
            except ValueError:
                return None

        objects.append({
            "raw_id": raw_id,
            "format": "omm",
            "a_m": (_float("SEMI_MAJOR_AXIS") * 1000.0) if _float("SEMI_MAJOR_AXIS") is not None else None,
            "e": _float("ECCENTRICITY"),
            "i_deg": _float("INCLINATION"),
            "raan_deg": _float("RA_OF_ASC_NODE"),
            "argp_deg": _float("ARG_OF_PERICENTER"),
            "mean_anomaly_deg": _float("MEAN_ANOMALY"),
            "epoch_iso": block.get("EPOCH"),
        })
    return objects
