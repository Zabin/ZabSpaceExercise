"""Simulator version stamp (IP-1200, FR-5510).

Prefers the current git commit (short hash) when a working tree is available; falls back to the
package's own declared version otherwise. Never raises — a save-as-scenario file must always get
a non-empty ``simulator_version``, even in a packaged/non-git deployment.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def simulator_version() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, timeout=2, text=True,
        )
        if result.returncode == 0:
            commit = result.stdout.strip()
            if commit:
                return commit
    except Exception:
        pass  # git unavailable, not a repository, or the call failed/timed out
    from spacesim import __version__
    return __version__
