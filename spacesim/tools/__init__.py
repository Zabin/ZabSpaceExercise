"""Offline/CLI-style utilities that drive the deterministic engine externally (batch runs,
research exports) rather than through the live ``ui_web``/``session`` request path — the first
subpackage of this kind inside ``spacesim`` itself (IP-3010). Distinct from the repo-root
``tools/`` directory, which holds standalone, non-package build scripts (e.g.
``tools/build_coastlines.py``); modules here must be importable by ``spacesim/tests/``.
"""
