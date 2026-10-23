"""IP-1069 — every console panel is registered with the panel manager (NFR-3030, BL-0305), and the
View > Panels menu does not offer White-only panels to other seats. Static checks of the shipped
console files; rendered float/resize/reset behaviour needs a browser (IP-1340)."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

pytestmark = pytest.mark.verifies("NFR-3030")

STATIC = Path(__file__).resolve().parents[1] / "ui_web" / "static"


class _Panels(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "panel" in (a.get("class") or "").split() and a.get("id"):
            self.ids.add(a["id"])


def _html_panels() -> set[str]:
    p = _Panels()
    p.feed((STATIC / "index.html").read_text(encoding="utf-8"))
    return p.ids


def _registry() -> set[str]:
    js = (STATIC / "panels.js").read_text(encoding="utf-8")
    block = js.split("const PANELS = [", 1)[1].split("];", 1)[0]
    return set(re.findall(r'\{\s*id:\s*"([^"]+)"', block))


def test_every_panel_in_the_page_is_registered_and_vice_versa():
    page, reg = _html_panels(), _registry()
    assert page, "no panels found in index.html"
    assert page - reg == set(), f"panels not registered with the panel manager: {sorted(page - reg)}"
    assert reg - page == set(), f"registered panels missing from index.html: {sorted(reg - page)}"


def test_the_two_white_only_panels_are_registered():
    assert {"compare-panel", "assessment-panel"} <= _registry()


def test_menu_builder_filters_white_only_panels():
    js = (STATIC / "panels.js").read_text(encoding="utf-8")
    menu = js.split("function buildMenu()", 1)[1].split("function syncMenu()", 1)[0]
    assert "white-only" in menu
