"""Web UI layer: a FastAPI server wrapping the in-process SessionAPI (``07-api-and-networking.md``).

This is a thin transport over ``InProcessSession`` — the request/response bodies are the same
pydantic messages the API already speaks, so the engine and session layers are untouched. v1 is
REST (pull); the same boundary takes a WebSocket push later (``get_eventlog(since_seq)`` is the
delta contract). Fog-of-war is applied server-side in ``/view/{cell}`` exactly as in the API.
"""
