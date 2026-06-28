# ADR-0020 — Tech stack selection

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0020
- **Title:** Python 3.11+ / NumPy / Skyfield+sgp4 / pydantic v2 / pytest / FastAPI+Uvicorn / vanilla JS
- **Status:** Accepted

## Context

The engine needs deterministic, testable physics computation; the presentation layer needs a
browser-compatible transport that makes LAN multiplayer cheap; content needs schema validation.
GDS-03 names the shipped stack across each subsystem: engine (§2.1) — Python 3.11+, NumPy,
Skyfield/sgp4, pydantic v2; session layer (§2.2) — plain Python, framework-free; presentation
(§2.4) — FastAPI + Uvicorn, vanilla JS modules, no client framework; content (§2.5) — YAML/JSON +
pydantic v2 + `httpx` for the optional Space-Track call. `CLAUDE.md` "Tech stack" names this the
"leading recommendation — confirm at Phase 0," now confirmed and shipped.

## Decision

The implementation stack is: Python 3.11+, NumPy, Skyfield/sgp4 (propagation), pydantic v2
(schemas/validation), pytest (test-driven development gate), FastAPI + Uvicorn (server), vanilla
JS with no client-side framework (browser client), YAML/JSON (content), `httpx` (the one optional
network call).

## Alternatives Considered

- **A desktop GUI framework** (PyQt/PySide) — superseded for presentation specifically; see
  ADR-0008. The underlying engine/physics stack choice (Python/NumPy/Skyfield) was unaffected by
  that supersession.
- **A client-side JS framework** (React/Vue/etc.) — rejected: `design/02` recommends vanilla JS
  modules; no document records a reason beyond avoiding framework overhead for a relatively small,
  server-driven UI surface.
- **A non-Python engine language** (e.g. Rust/C++ for performance) — not seriously considered in
  any document; Python's library ecosystem (Skyfield/sgp4/NumPy/pydantic) and the
  one-language-for-engine-and-UI rationale (originally under D3, before the UI choice changed)
  outweighed raw performance concerns.

## Rationale

The chosen stack lets one language span engine, session, and (server-side) presentation code,
reuses mature astrodynamics libraries (Skyfield/sgp4) rather than re-implementing propagation,
and keeps the test-driven workflow (`pytest`) consistent across the whole codebase.

## Consequences

- Any new dependency must justify itself against "no paid dependencies" (build-spec/01 Decision
  D8) and the hardware-floor constraint (`build-spec/01` §3.3).
- The import-guard test enforces that the engine layer specifically stays free of UI/network
  imports regardless of what the presentation stack uses.

## Related

GDS-03 §2.1, §2.2, §2.4, §2.5; `CLAUDE.md` "Tech stack," "Code map"; `design/
02-tech-stack-recommendation.md`; build-spec/01 Decision D3, D8.
