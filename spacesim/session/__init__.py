"""Application/session layer: authoritative SessionManager, fog-of-war CellController, SessionAPI.

This layer is the boundary between the UI and the deterministic engine. The engine never imports
it; everything crossing the boundary is serializable. Fog-of-war and authority live here, so a
future untrusted network client cannot cheat (``07-api-and-networking.md``).
"""

from spacesim.session.api import Ack, CellView, OrderAck, SessionAPI
from spacesim.session.cells import CellController
from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import SessionManager

__all__ = ["Ack", "CellView", "OrderAck", "SessionAPI", "CellController", "InProcessSession", "SessionManager"]
