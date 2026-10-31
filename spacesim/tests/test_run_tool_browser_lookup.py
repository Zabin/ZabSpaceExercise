"""IP-1094 — the two run tools find Chromium via PLAYWRIGHT_BROWSERS_PATH / newest build."""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.verifies("IP-1094")

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLS = [ROOT / "tools" / "record_walkthrough.py",
         ROOT / ".claude" / "skills" / "run-spacesim" / "driver.py"]


def _finder(path: pathlib.Path):
    """Compile just ``find_chromium`` out of the script (the scripts import Playwright/PIL)."""
    tree = ast.parse(path.read_text())
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "find_chromium"), None)
    assert fn is not None, f"{path.name} has no find_chromium()"
    ns: dict = {}
    exec(compile(ast.Module([fn], []), str(path), "exec"), ns)
    return ns["find_chromium"]


def _mk(root: pathlib.Path, rel: str) -> str:
    p = root / rel
    p.parent.mkdir(parents=True)
    p.write_text("")
    return str(p)


@pytest.mark.parametrize("tool", TOOLS, ids=lambda p: p.name)
def test_newest_build_and_env_root(tool, tmp_path, monkeypatch):
    _mk(tmp_path, "chromium-1194/chrome-linux64/chrome")
    new = _mk(tmp_path, "chromium-1200/chrome-linux/chrome")
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(tmp_path))
    assert _finder(tool)() == new


@pytest.mark.parametrize("tool", TOOLS, ids=lambda p: p.name)
def test_linux64_layout_found(tool, tmp_path, monkeypatch):
    only = _mk(tmp_path, "chromium-1243/chrome-linux64/chrome")
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(tmp_path))
    assert _finder(tool)() == only


@pytest.mark.parametrize("tool", TOOLS, ids=lambda p: p.name)
def test_empty_root_names_the_root(tool, tmp_path, monkeypatch):
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(tmp_path))
    with pytest.raises(SystemExit) as e:
        _finder(tool)()
    assert str(tmp_path) in str(e.value)


def test_no_hardcoded_build_and_probe_fixed():
    for t in TOOLS:
        assert "chromium-1194" not in t.read_text(), t.name
    skill = ROOT / ".claude" / "skills" / "run-spacesim"
    d = (skill / "driver.py").read_text()
    assert "o-target-pick" not in d and "'o-target'" in d
