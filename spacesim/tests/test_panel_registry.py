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


VOID = {"br", "hr", "img", "input", "link", "meta", "source", "col", "area", "base", "embed", "param", "track", "wbr"}


class _Panels(HTMLParser):
    """Panel ids, plus for each panel the (tag, classes) of its descendants and whether it has a
    direct-child <h2> (what `panels.js::headerOf` looks for)."""

    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.descendants: dict[str, list[tuple[str, set[str]]]] = {}
        self.has_h2: set[str] = set()
        self._stack: list[tuple[str, str | None]] = []   # (tag, panel id it opens or None)

    def _open_panels(self):
        return [pid for _, pid in self._stack if pid]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        opens = a["id"] if "panel" in classes and a.get("id") else None
        for pid in self._open_panels():
            self.descendants[pid].append((tag, classes))
            if tag == "h2":
                self.has_h2.add(pid)
        if opens:
            self.ids.add(opens)
            self.descendants[opens] = []
        if tag not in VOID:
            self._stack.append((tag, opens))

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i][0] == tag:
                del self._stack[i:]
                break


def _parsed() -> _Panels:
    p = _Panels()
    p.feed((STATIC / "index.html").read_text(encoding="utf-8"))
    return p


def _html_panels() -> set[str]:
    return _parsed().ids


def _handles() -> dict[str, str | None]:
    """Registry id -> its `handle` selector (None when it relies on the panel's <h2>)."""
    js = (STATIC / "panels.js").read_text(encoding="utf-8")
    block = js.split("const PANELS = [", 1)[1].split("];", 1)[0]
    return {m.group(1): m.group(2) for m in re.finditer(r'\{\s*id:\s*"([^"]+)"[^}]*?(?:handle:\s*"([^"]+)")?\s*\}', block)}


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


def _matches(selector: str, tag: str, classes: set[str]) -> bool:
    return (selector.startswith(".") and selector[1:] in classes) or selector == tag


def test_every_registered_panel_gets_panel_controls():
    """BL-0331: a registered panel with no header for `headerOf` to find gets no close/dock/grip,
    so cannot be floated. Its header is its `handle` selector, else a direct-child <h2>, else any <h2>."""
    parsed, handles = _parsed(), _handles()
    missing = []
    for pid, handle in sorted(handles.items()):
        if handle:
            found = any(_matches(handle, tag, classes) for tag, classes in parsed.descendants[pid])
        else:
            found = pid in parsed.has_h2
        if not found:
            missing.append(f"{pid} (handle={handle!r})")
    assert not missing, f"registered panels with no header to attach controls to: {missing}"


def test_menu_builder_filters_white_only_panels():
    """BL-0332: the check reads the code, not a comment — the filter must test the panel element's class."""
    js = (STATIC / "panels.js").read_text(encoding="utf-8")
    menu = js.split("function buildMenu()", 1)[1].split("function syncMenu()", 1)[0]
    code = "\n".join(line.split("//", 1)[0] for line in menu.split("\n"))
    assert re.search(r'classList\.contains\(\s*"white-only"\s*\)', code)
