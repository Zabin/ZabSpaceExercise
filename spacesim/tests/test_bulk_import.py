"""IP-1190 (FR-5220) — bulk TLE / CCSDS OMM (KVN) multi-object parsing."""
from __future__ import annotations

import pytest

from spacesim.content.bulk_import import parse_ccsds_omm, parse_multi_tle

_TLE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
_TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49560570999999"
_TLE1B = "1 43013U 17073A   24001.50000000  .00000023  00000-0  12345-4 0  9995"
_TLE2B = "2 43013  98.5691 100.1234 0001234  90.1234 270.1234 14.19560570123456"


def test_parse_multi_tle_with_and_without_name_lines():
    text = "\n".join([
        "ISS (ZARYA)",
        _TLE1, _TLE2,
        _TLE1B, _TLE2B,
    ])
    objects = parse_multi_tle(text)
    assert len(objects) == 2
    assert objects[0]["raw_id"] == "ISS (ZARYA)"
    assert objects[0]["format"] == "tle"
    assert objects[0]["line1"] == _TLE1
    assert objects[0]["line2"] == _TLE2
    # No name line -> raw_id falls back to the NORAD catalog number field.
    assert objects[1]["raw_id"] == "43013"


def test_parse_multi_tle_zero_recognizable_blocks_raises():
    with pytest.raises(ValueError):
        parse_multi_tle("this is not a TLE file\njust some text\n")


def test_parse_multi_tle_malformed_block_still_returned_for_later_per_object_failure():
    # Nine well-formed objects + one malformed (short/garbled second line).
    lines = []
    for _ in range(9):
        lines.append(_TLE1)
        lines.append(_TLE2)
    lines.append(_TLE1)
    lines.append("2 too short")
    objects = parse_multi_tle("\n".join(lines))
    assert len(objects) == 10
    assert objects[-1]["line2"] == "2 too short"


_OMM_TEXT = """CCSDS_OMM_VERS = 2.0
CREATION_DATE = 2024-001T00:00:00
ORIGINATOR = TEST

META_START
OBJECT_NAME = SAT-A
OBJECT_ID = 2024-001A
CENTER_NAME = EARTH
REF_FRAME = TEME
TIME_SYSTEM = UTC
MEAN_ELEMENT_THEORY = KEPLERIAN
META_STOP

EPOCH = 2024-001T12:00:00.000000
SEMI_MAJOR_AXIS = 6928.0
ECCENTRICITY = 0.001
INCLINATION = 51.6
RA_OF_ASC_NODE = 100.0
ARG_OF_PERICENTER = 50.0
MEAN_ANOMALY = 10.0

META_START
OBJECT_NAME = SAT-B
OBJECT_ID = 2024-002A
CENTER_NAME = EARTH
REF_FRAME = TEME
TIME_SYSTEM = UTC
MEAN_ELEMENT_THEORY = KEPLERIAN
META_STOP

EPOCH = 2024-002T12:00:00.000000
SEMI_MAJOR_AXIS = 7000.0
ECCENTRICITY = 0.002
INCLINATION = 98.0
RA_OF_ASC_NODE = 120.0
ARG_OF_PERICENTER = 60.0
MEAN_ANOMALY = 20.0
"""


def test_parse_ccsds_omm_multiple_blocks():
    objects = parse_ccsds_omm(_OMM_TEXT)
    assert len(objects) == 2
    assert objects[0]["raw_id"] == "SAT-A"
    assert objects[0]["a_m"] == pytest.approx(6928.0 * 1000.0)
    assert objects[0]["e"] == pytest.approx(0.001)
    assert objects[1]["raw_id"] == "SAT-B"
    assert objects[1]["mean_anomaly_deg"] == pytest.approx(20.0)


def test_parse_ccsds_omm_zero_recognizable_blocks_raises():
    with pytest.raises(ValueError):
        parse_ccsds_omm("this is not an OMM file\njust some text\n")


def test_parse_ccsds_omm_malformed_block_still_returned_missing_element_is_none():
    text = _OMM_TEXT + "\nMETA_START\nOBJECT_NAME = SAT-C\nMETA_STOP\nEPOCH = 2024-003T00:00:00\nSEMI_MAJOR_AXIS = 7100.0\n"
    objects = parse_ccsds_omm(text)
    assert len(objects) == 3
    assert objects[2]["raw_id"] == "SAT-C"
    assert objects[2]["e"] is None  # missing ECCENTRICITY — a per-object failure downstream


def test_neither_tle_nor_omm_shaped_file_raises_from_both_parsers():
    text = "totally unrelated free text\nwith no structure at all\n"
    with pytest.raises(ValueError):
        parse_multi_tle(text)
    with pytest.raises(ValueError):
        parse_ccsds_omm(text)
