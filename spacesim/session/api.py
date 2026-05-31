"""SessionAPI contract and the messages that cross the UI<->engine boundary (``07-api-and-networking.md``).

In v1 the API is called in-process; the same message shapes become the network protocol later.
All messages are pydantic models so they serialize cleanly when a transport is added.
"""

from __future__ import annotations

from typing import Optional, Protocol

from pydantic import BaseModel, Field


class Ack(BaseModel):
    ok: bool = True
    reason: str = ""


class OrderAck(BaseModel):
    ok: bool
    id: Optional[str] = None
    reason: str = ""
    status: str = "draft"
    earliest_window: Optional[tuple[int, int]] = None
    delivery_path: Optional[str] = None


class CellView(BaseModel):
    """The fog-filtered picture a single cell is allowed to see."""

    cell: str
    now: int
    own_assets: list[dict] = Field(default_factory=list)
    own_sensors: list[dict] = Field(default_factory=list)
    known_tracks: list[dict] = Field(default_factory=list)     # belief about other-side objects
    visible_effects: list[dict] = Field(default_factory=list)  # symptoms on own assets (attribution-limited)
    effect_windows: list[dict] = Field(default_factory=list)   # start/end of active effects on own assets (for graph shading)
    messages: list[dict] = Field(default_factory=list)
    objectives: dict = Field(default_factory=dict)


class SessionAPI(Protocol):
    def list_vignettes(self) -> list[dict]: ...
    def load_vignette(self, vignette_id: str, overrides: Optional[dict] = None, seed: int = 0) -> str: ...
    def set_parameter(self, session: str, param_id: str, value) -> Ack: ...
    def start(self, session: str) -> Ack: ...

    def step(self, session: str, dt_sim_s: float) -> Ack: ...
    def advance_to(self, session: str, t: int) -> Ack: ...
    def rewind_to(self, session: str, t: int) -> Ack: ...
    def undo_last(self, session: str, n: int = 1) -> Ack: ...

    def fire_inject(self, session: str, inject: str | dict) -> Ack: ...

    def issue_order(self, session: str, cell: str, order) -> OrderAck: ...
    def validate_order(self, session: str, cell: str, order) -> OrderAck: ...

    def get_view(self, session: str, cell: str) -> CellView: ...
    def get_godview(self, session: str): ...
    def get_eventlog(self, session: str, since_seq: int = 0) -> list: ...
    def objectives(self, session: str) -> dict: ...
