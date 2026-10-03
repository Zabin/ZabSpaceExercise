"""Space Control & Orbital Warfare Exercise Simulator.

Top-level package. The deterministic, UI-agnostic engine lives in `spacesim.engine`;
the application/session layer (added in a later phase) will live in `spacesim.session`.
"""

# IP-1200 (FR-5510) — mirrors pyproject.toml's own version field; the fallback
# simulator_version() (spacesim/version.py) uses when no git working tree is available.
__version__ = "0.1.0"
