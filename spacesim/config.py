"""Project-wide runtime configuration loaded from ``spacesim.config.yaml``.

The config file lives at the repository root. Fields missing from the YAML fall
back to the defaults below; the file itself is optional. Override the search
path with the ``SPACESIM_CONFIG`` environment variable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "spacesim.config.yaml"


@dataclass(frozen=True)
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False


def load_server_config(path: Path | str | None = None) -> ServerConfig:
    """Return the server section of the config file, falling back to defaults.

    The file is optional; pyyaml is only imported if a file is present.
    """
    candidate = Path(path) if path else Path(os.environ.get("SPACESIM_CONFIG", DEFAULT_CONFIG_PATH))
    if not candidate.is_file():
        return ServerConfig()
    import yaml  # local import — pyyaml is only required when a config file exists

    data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
    server = (data.get("server") or {}) if isinstance(data, dict) else {}
    defaults = ServerConfig()
    return ServerConfig(
        host=str(server.get("host", defaults.host)),
        port=int(server.get("port", defaults.port)),
        reload=bool(server.get("reload", defaults.reload)),
    )
