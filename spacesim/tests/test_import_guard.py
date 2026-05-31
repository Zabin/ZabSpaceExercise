"""Phase 0 guardrail: the engine must stay UI-agnostic, wall-clock-free, and global-RNG-free.

These are the load-bearing invariants from ``CLAUDE.md``/``01-architecture-overview.md``. If any
of them break, deterministic replay and the future network seam break with them — so this test
fails the build rather than letting the regression land.
"""

from __future__ import annotations

import ast
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"

# Modules the deterministic core may never depend on (UI / application / transport).
FORBIDDEN_IMPORT_ROOTS = {
    "spacesim.session",
    "spacesim.ui",
    "spacesim.ui_web",
    "spacesim.ui_qt",
    "fastapi",
    "starlette",
    "uvicorn",
    "flask",
    "websockets",
    "PyQt5",
    "PyQt6",
    "PySide6",
    "requests",
    "httpx",
}

# Wall-clock reads are forbidden anywhere in the engine (only the sim clock is allowed).
# Expressed as dotted attribute accesses detected on the AST, so docstrings/comments don't trip it.
WALL_CLOCK_ATTRS = {
    "datetime.now",
    "datetime.utcnow",
    "datetime.today",
    "time.time",
    "time.monotonic",
    "time.perf_counter",
    "time.sleep",
    "time.gmtime",
    "time.localtime",
}


def _engine_files() -> list[Path]:
    return sorted(ENGINE_DIR.rglob("*.py"))


def _imported_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            roots.add(node.module)
    return roots


def test_engine_has_files():
    assert _engine_files(), "expected engine modules to scan"


def test_engine_imports_no_ui_session_or_transport():
    offenders = []
    for path in _engine_files():
        tree = ast.parse(path.read_text(), filename=str(path))
        for imported in _imported_roots(tree):
            for forbidden in FORBIDDEN_IMPORT_ROOTS:
                if imported == forbidden or imported.startswith(forbidden + "."):
                    offenders.append(f"{path.name}: imports {imported}")
    assert not offenders, "engine imported forbidden module(s): " + "; ".join(offenders)


def _dotted_attr(node: ast.Attribute) -> str | None:
    """Render ``a.b.c`` attribute chains to a dotted string; None if not a simple chain."""
    parts: list[str] = [node.attr]
    cur = node.value
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        return ".".join(reversed(parts))
    return None


def test_engine_reads_no_wall_clock():
    offenders = []
    for path in _engine_files():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                dotted = _dotted_attr(node)
                if dotted is None:
                    continue
                # Match the trailing two-segment name (e.g. ...datetime.now).
                tail = ".".join(dotted.split(".")[-2:])
                if tail in WALL_CLOCK_ATTRS:
                    offenders.append(f"{path.name}: uses {tail}")
    assert not offenders, "engine reads the wall clock: " + "; ".join(offenders)


def test_only_rng_module_imports_random():
    """All randomness must flow through SeededRng; no other engine file imports ``random``."""
    offenders = []
    for path in _engine_files():
        if path.name == "rng.py":
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        if "random" in _imported_roots(tree):
            offenders.append(path.name)
    assert not offenders, "engine modules importing the global 'random': " + ", ".join(offenders)
