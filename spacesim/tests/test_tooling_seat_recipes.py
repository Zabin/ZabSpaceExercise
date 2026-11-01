"""IP-1073 (FR-4310) — the walkthrough recorder and the run-spacesim recipe name the White seat for
time control. A text check is a weak guard for a script that cannot run in CI; it exists to stop
the recipe drifting from the server's White-only guards (IP-1068/IP-1072) again."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
pytestmark = pytest.mark.verifies("FR-4310")


def _recipe_posts():
    text = (ROOT / ".claude/skills/run-spacesim/SKILL.md").read_text(encoding="utf-8")
    return [ln for ln in text.splitlines()
            if "curl" in ln and re.search(r"/(start|step|advance|rewind)\b", ln)]


def test_recipe_time_control_calls_carry_the_white_seat():
    posts = _recipe_posts()
    assert posts, "the recipe no longer shows any start/step/advance/rewind call"
    assert all("cell=white" in ln for ln in posts), posts


def test_recorder_advances_time_as_white_and_checks_the_status():
    text = (ROOT / "tools/record_walkthrough.py").read_text(encoding="utf-8")
    assert "stepBy(" not in text.replace("# ", "#"), "a non-White beat must not call stepBy()"
    beat6 = text.split("Beat 6")[1].split("Beat 7")[0]
    assert "cell=white" in beat6 or '"cell": "white"' in beat6
    assert "/advance" in beat6 and ("raise" in beat6 or "status" in beat6)
