"""Launch the FastAPI server using settings from ``spacesim.config.yaml``.

Run: ``python3 -m spacesim.ui_web``
"""

from __future__ import annotations

import uvicorn

from spacesim.config import load_server_config


def main() -> None:
    cfg = load_server_config()
    uvicorn.run(
        "spacesim.ui_web.server:app",
        host=cfg.host,
        port=cfg.port,
        reload=cfg.reload,
    )


if __name__ == "__main__":
    main()
