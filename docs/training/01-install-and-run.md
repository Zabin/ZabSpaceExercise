[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 1. Install

**Prerequisites:** Python **3.11 or newer**. (Check with `python3 --version`.)

From the repository root:

```bash
# Runtime dependencies (the engine + web server):
pip install pydantic numpy sgp4 pyyaml fastapi uvicorn

# Optional — only needed to run the test suite:
pip install pytest hypothesis skyfield httpx
```

Verify the install by running the test suite (all should pass):

```bash
python3 -m pytest
```

Everything runs **offline** — the engine uses an analytic Sun model and bundled orbit math, so no
internet connection or ephemeris download is required.

---

## 2. Run it

Start the web server from the repository root:

```bash
uvicorn spacesim.ui_web.server:app
```

Then open **http://127.0.0.1:8000/** in a browser. You should see the dark mission-control layout
with the `UNCLASSIFIED // TRAINING` banner.

> Prefer a script or an air-gapped box with no browser? Every action is also available through the
> in-process Python API and the HTTP API — see [§9](#9-http-api-reference) and the
> *headless walkthrough* at the end of [§4](#4-your-first-exercise).

---
