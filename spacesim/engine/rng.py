"""The single seeded RNG for the whole engine.

Every random decision in the simulation must draw from an instance of ``SeededRng`` that is
carried with the session state. There is no module-level/global randomness anywhere else in the
engine (the import guard forbids importing ``random`` outside this file), because rewind/replay
only reproduces exactly if the random sequence is a pure function of the seed and the draw order.
"""

from __future__ import annotations

import random


class SeededRng:
    def __init__(self, seed: int) -> None:
        self._seed = seed
        self._r = random.Random(seed)

    @property
    def seed(self) -> int:
        return self._seed

    def random(self) -> float:
        """Float in [0.0, 1.0)."""
        return self._r.random()

    def uniform(self, a: float, b: float) -> float:
        return self._r.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        """Integer in [a, b] inclusive."""
        return self._r.randint(a, b)

    def export_state(self) -> dict:
        """A JSON-serializable capture of the full RNG state (for snapshots/saves)."""
        version, internalstate, gauss_next = self._r.getstate()
        return {
            "seed": self._seed,
            "version": version,
            "internalstate": list(internalstate),
            "gauss_next": gauss_next,
        }

    def import_state(self, state: dict) -> None:
        self._seed = state["seed"]
        self._r.setstate(
            (state["version"], tuple(state["internalstate"]), state["gauss_next"])
        )
