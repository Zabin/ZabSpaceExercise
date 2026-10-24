"""IP-1131 (BL-0260, NFR-3400) — training `> Sources:` footers still point at real code.

Every `docs/training/*.md` section ends with a `> **Sources:**` footer naming the code that backs
it (FR-11120). This test resolves each backticked file path a footer names (as written, or under
`spacesim/` and its subpackages, which the footers abbreviate) and checks that every backticked
identifier following that path in the same `·`-separated segment still occurs in the file. A moved
or renamed code path therefore fails the suite — the mitigation strategic assumption A12 names.
Route segments (`/api/...`) and globs are not checked.
"""
from __future__ import annotations

import pytest
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAINING = ROOT / "docs" / "training"
_PATH = re.compile(r"`((?:spacesim/|tools/)?[\w./-]+\.(?:py|js|yaml|html|css|json))`")
_SYMBOL = re.compile(r"`([A-Za-z_][\w.]*)`")
_PREFIXES = ("", "spacesim/", "spacesim/session/", "spacesim/engine/", "spacesim/ui_web/",
             "spacesim/ui_web/static/", "spacesim/content/")


def _footers(text: str) -> list[str]:
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith("> **Sources:**"):
            block = [lines[i][2:]]
            i += 1
            while i < len(lines) and lines[i].startswith("> ") and not lines[i].startswith("> **"):
                block.append(lines[i][2:])
                i += 1
            out.append(" ".join(block))
        else:
            i += 1
    return out


def _resolve(rel: str) -> Path | None:
    for prefix in _PREFIXES:
        candidate = ROOT / (prefix + rel)
        if candidate.is_file():
            return candidate
    return None


def check_footer(footer: str) -> list[str]:
    """Return a problem string per unresolvable path or missing symbol in one footer."""
    problems = []
    for segment in footer.split(" · "):
        m = _PATH.search(segment)
        if not m:
            continue
        rel = m.group(1)
        if "*" in rel:
            continue
        path = _resolve(rel)
        if path is None:
            problems.append(f"path not found: {rel}")
            continue
        source = path.read_text(encoding="utf-8")
        for symbol in _SYMBOL.findall(segment[m.end():]):
            if symbol.split(".")[-1] not in source:
                problems.append(f"{rel}: symbol not found: {symbol}")
    return problems


@pytest.mark.verifies("NFR-3400")
def test_every_training_footer_resolves():
    problems = []
    count = 0
    for md in sorted(TRAINING.glob("*.md")):
        for footer in _footers(md.read_text(encoding="utf-8")):
            count += 1
            problems += [f"{md.name}: {p}" for p in check_footer(footer)]
    assert count > 50, "footer parser found too few footers — has the footer format changed?"
    assert not problems, "\n".join(problems)


@pytest.mark.verifies("NFR-3400")
def test_checker_fails_on_a_broken_footer():
    """Self-test: the checker is shown to fail on a renamed symbol and on a moved file."""
    assert check_footer("**Sources:** `spacesim/engine/orders.py` (`_validate`)") == []
    assert check_footer("**Sources:** `spacesim/engine/orders.py` (`_no_such_function_xyz`)")
    assert check_footer("**Sources:** `spacesim/engine/no_such_module.py`")
