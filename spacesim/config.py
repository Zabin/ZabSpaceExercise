"""Project-wide runtime configuration loaded from ``spacesim.config.yaml``.

The config file lives at the repository root. Fields missing from the YAML fall
back to the defaults below; the file itself is optional. Override the search
path with the ``SPACESIM_CONFIG`` environment variable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


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


@dataclass(frozen=True)
class ContentConfig:
    """IP-1180 (FR-5410/FR-5420) — external vignette directories + the Vignette Creator's
    user-save target. Additive/optional: absent for every deployment that hasn't opted in, in
    which case the catalog is exactly the built-in library and ``save_vignette`` refuses to
    write anywhere (see ``content/vignette_export.py``)."""
    external_vignette_dirs: tuple[str, ...] = ()
    user_save_dir: Optional[str] = None


def load_content_config(path: Path | str | None = None) -> ContentConfig:
    """Return the ``content:`` section of the config file, falling back to defaults.

    Mirrors ``load_server_config()``'s shape exactly: the file is optional, missing fields fall
    back to defaults, and ``SPACESIM_CONFIG`` overrides the search path the same way.
    """
    candidate = Path(path) if path else Path(os.environ.get("SPACESIM_CONFIG", DEFAULT_CONFIG_PATH))
    if not candidate.is_file():
        return ContentConfig()
    import yaml  # local import — pyyaml is only required when a config file exists

    data = yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
    content = (data.get("content") or {}) if isinstance(data, dict) else {}
    defaults = ContentConfig()
    ext_dirs = content.get("external_vignette_dirs", defaults.external_vignette_dirs)
    return ContentConfig(
        external_vignette_dirs=tuple(ext_dirs) if ext_dirs else defaults.external_vignette_dirs,
        user_save_dir=content.get("user_save_dir", defaults.user_save_dir),
    )
