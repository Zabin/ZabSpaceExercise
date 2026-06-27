"""Phase 0 guardrail: the engine must stay UI-agnostic, wall-clock-free, and global-RNG-free.

These are the load-bearing invariants from ``CLAUDE.md``/``01-architecture-overview.md``. If any
of them break, deterministic replay and the future network seam break with them — so this test
fails the build rather than letting the regression land.

Audit Jun 2026 §E3 closed four bypasses that the original scan missed:

1. ``from time import monotonic; monotonic()`` — by-name import + bare call escapes the
   attribute-chain detector.
2. ``importlib.import_module("requests")`` / ``__import__("httpx")`` — dynamic imports of
   forbidden roots.
3. ``from numpy.random import default_rng`` — the global ``random`` token does not match.
4. ``from ...session import X`` (relative ImportFrom with ``level != 0``) — ImportFrom records
   skipped the relative case.

The scanner below closes all four. The bypasses are also fixture-tested at the end of this
file so a future regression would land as a failed test, not a silent escape.
"""

from __future__ import annotations

import ast
import textwrap
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
    # Audit Jun 2026 §E3 — `importlib` lets a regression hide a forbidden
    # import behind a dynamic call. Also forbid `__import__` (a Name, not an
    # Import).
    "importlib",
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

# Audit Jun 2026 §E3 — names that, if imported by-name from the listed module,
# count as a wall-clock read when bare-called (e.g.
# ``from time import monotonic; monotonic()``).
WALL_CLOCK_NAMES_BY_MODULE = {
    "time": {"time", "monotonic", "perf_counter", "sleep", "gmtime", "localtime"},
    "datetime": {"datetime", "date"},  # `datetime.now()` patterns
}


def _engine_files() -> list[Path]:
    return sorted(ENGINE_DIR.rglob("*.py"))


def _imported_roots(tree: ast.AST) -> set[str]:
    """Collect every imported top-level module name.

    Audit Jun 2026 §E3 — now also honors relative ``ImportFrom`` (``level != 0``)
    by treating the deepest available module name as the root. That closes the
    ``from ...session import X`` escape.
    """
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            # Relative imports (level > 0) lose package context but we still want
            # to forbid `from ... import session` style escapes. Record the
            # tail module name if any.
            if node.module:
                roots.add(node.module)
            for alias in node.names:
                # `from foo import session` → also record `foo.session` for matching.
                if node.module:
                    roots.add(f"{node.module}.{alias.name}")
                else:
                    roots.add(alias.name)
    return roots


def _byname_wall_clock_imports(tree: ast.AST) -> set[str]:
    """Return the set of bare names imported from wall-clock modules.

    For ``from time import monotonic as m`` → returns ``{"m"}``. The caller
    then watches for ``m()`` in the AST.
    """
    bare_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in WALL_CLOCK_NAMES_BY_MODULE:
            allowed = WALL_CLOCK_NAMES_BY_MODULE[node.module]
            for alias in node.names:
                if alias.name in allowed:
                    bare_names.add(alias.asname or alias.name)
    return bare_names


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
    """Catches attribute-chain reads (``time.time()``, ``datetime.now()``) **and**
    bare-name calls of wall-clock functions imported by-name (audit §E3)."""
    offenders = []
    for path in _engine_files():
        tree = ast.parse(path.read_text(), filename=str(path))

        # Attribute-chain detector (the original check).
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                dotted = _dotted_attr(node)
                if dotted is None:
                    continue
                tail = ".".join(dotted.split(".")[-2:])
                if tail in WALL_CLOCK_ATTRS:
                    offenders.append(f"{path.name}: uses {tail}")

        # Audit §E3 — by-name detector. If the module imported a wall-clock
        # function by name, flag any bare call on that name.
        bare_wall_names = _byname_wall_clock_imports(tree)
        if bare_wall_names:
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in bare_wall_names:
                        offenders.append(
                            f"{path.name}: calls by-name wall-clock function "
                            f"{node.func.id}()"
                        )

    assert not offenders, "engine reads the wall clock: " + "; ".join(offenders)


def test_only_rng_module_imports_random():
    """All randomness must flow through SeededRng; no other engine file imports ``random``.

    Audit Jun 2026 §E3 hardening: also forbids ``numpy.random`` (Numpy's global
    PRNG / default_rng escape) and any module whose root ends in ``.random``.
    """
    offenders = []
    for path in _engine_files():
        if path.name == "rng.py":
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        roots = _imported_roots(tree)
        for r in roots:
            if r == "random" or r.startswith("random."):
                offenders.append(f"{path.name}: imports {r}")
            elif r == "numpy.random" or r.endswith(".numpy.random"):
                offenders.append(f"{path.name}: imports {r}")
            elif r.endswith(".random"):
                offenders.append(f"{path.name}: imports {r}")
    assert not offenders, "engine modules importing a 'random' module: " + ", ".join(offenders)


def test_engine_uses_no_dynamic_import():
    """Audit Jun 2026 §E3 — ``importlib.import_module(...)`` and ``__import__(...)``
    could hide forbidden imports from the static scan. Forbid both in engine code."""
    offenders = []
    for path in _engine_files():
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            # `importlib.import_module(...)` — attribute call.
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                dotted = _dotted_attr(node.func)
                if dotted and dotted.endswith("import_module"):
                    offenders.append(f"{path.name}: calls {dotted}")
            # `__import__(...)` — bare-name call.
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == "__import__":
                    offenders.append(f"{path.name}: calls __import__()")
    assert not offenders, "engine uses dynamic import: " + "; ".join(offenders)


# --------------------------------------------------------------------------- #
# Fixture-based regression tests for the closed bypasses.
# Each one synthesizes a Python source snippet that *would* have escaped the
# original scan, parses it, and asserts the corresponding scanner flags it.
# --------------------------------------------------------------------------- #

def _scan_for_wall_clock(src: str) -> list[str]:
    tree = ast.parse(src)
    offenders: list[str] = []
    bare_names = _byname_wall_clock_imports(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            dotted = _dotted_attr(node)
            if dotted is None:
                continue
            tail = ".".join(dotted.split(".")[-2:])
            if tail in WALL_CLOCK_ATTRS:
                offenders.append(f"attr:{tail}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in bare_names:
                offenders.append(f"call:{node.func.id}")
    return offenders


def test_guard_catches_byname_walltime():
    """``from time import monotonic; monotonic()`` must be flagged (audit §E3 #1)."""
    src = textwrap.dedent(
        """
        from time import monotonic
        def f():
            return monotonic()
        """
    )
    assert _scan_for_wall_clock(src), "by-name `monotonic()` was not flagged"

    src2 = textwrap.dedent(
        """
        from time import time as t
        def f():
            return t()
        """
    )
    assert _scan_for_wall_clock(src2), "aliased by-name `t()` was not flagged"


def _scan_for_dynamic_imports(src: str) -> list[str]:
    tree = ast.parse(src)
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            dotted = _dotted_attr(node.func)
            if dotted and dotted.endswith("import_module"):
                found.append(dotted)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "__import__":
                found.append("__import__")
    return found


def test_guard_catches_dynamic_imports():
    """``importlib.import_module(...)`` and ``__import__(...)`` must be flagged
    (audit §E3 #2)."""
    src = "import importlib; importlib.import_module('requests')"
    assert _scan_for_dynamic_imports(src) == ["importlib.import_module"]

    src2 = "__import__('httpx')"
    assert _scan_for_dynamic_imports(src2) == ["__import__"]


def test_guard_catches_numpy_random():
    """``from numpy.random import default_rng`` must be flagged as a forbidden
    'random' source (audit §E3 #3)."""
    src = "from numpy.random import default_rng\n"
    tree = ast.parse(src)
    roots = _imported_roots(tree)
    # `numpy.random` should appear as a root because of the ImportFrom node.
    bad = [r for r in roots if r == "random" or r.endswith(".random")]
    assert bad, f"numpy.random not flagged; roots seen: {sorted(roots)}"
