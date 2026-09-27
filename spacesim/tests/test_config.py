"""Server config loader: defaults, YAML overrides, and env-var path."""

from __future__ import annotations

from pathlib import Path

import pytest

from spacesim.config import ContentConfig, ServerConfig, load_content_config, load_server_config


def test_defaults_when_no_file(tmp_path: Path) -> None:
    cfg = load_server_config(tmp_path / "missing.yaml")
    assert cfg == ServerConfig()
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 8000
    assert cfg.reload is False


def test_yaml_overrides(tmp_path: Path) -> None:
    p = tmp_path / "spacesim.config.yaml"
    p.write_text("server:\n  host: 0.0.0.0\n  port: 9001\n  reload: true\n", encoding="utf-8")
    cfg = load_server_config(p)
    assert cfg.host == "0.0.0.0"
    assert cfg.port == 9001
    assert cfg.reload is True


def test_partial_override_keeps_other_defaults(tmp_path: Path) -> None:
    p = tmp_path / "c.yaml"
    p.write_text("server:\n  port: 7777\n", encoding="utf-8")
    cfg = load_server_config(p)
    assert cfg.port == 7777
    assert cfg.host == "127.0.0.1"
    assert cfg.reload is False


def test_env_var_overrides_default_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "from-env.yaml"
    p.write_text("server:\n  port: 5555\n", encoding="utf-8")
    monkeypatch.setenv("SPACESIM_CONFIG", str(p))
    cfg = load_server_config()
    assert cfg.port == 5555


def test_empty_file_falls_back_to_defaults(tmp_path: Path) -> None:
    p = tmp_path / "empty.yaml"
    p.write_text("", encoding="utf-8")
    assert load_server_config(p) == ServerConfig()


# -- IP-1180 (FR-5410/FR-5420) — ContentConfig / load_content_config() ---------------------------

def test_content_defaults_when_no_file(tmp_path: Path) -> None:
    cfg = load_content_config(tmp_path / "missing.yaml")
    assert cfg == ContentConfig()
    assert cfg.external_vignette_dirs == ()
    assert cfg.user_save_dir is None


def test_content_yaml_overrides(tmp_path: Path) -> None:
    p = tmp_path / "spacesim.config.yaml"
    p.write_text(
        "content:\n"
        "  external_vignette_dirs:\n"
        "    - /tmp/ext-a\n"
        "    - /tmp/ext-b\n"
        "  user_save_dir: /tmp/saves\n",
        encoding="utf-8",
    )
    cfg = load_content_config(p)
    assert cfg.external_vignette_dirs == ("/tmp/ext-a", "/tmp/ext-b")
    assert cfg.user_save_dir == "/tmp/saves"


def test_content_partial_override_keeps_other_defaults(tmp_path: Path) -> None:
    p = tmp_path / "c.yaml"
    p.write_text("content:\n  user_save_dir: /tmp/saves\n", encoding="utf-8")
    cfg = load_content_config(p)
    assert cfg.user_save_dir == "/tmp/saves"
    assert cfg.external_vignette_dirs == ()


def test_content_env_var_overrides_default_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = tmp_path / "from-env.yaml"
    p.write_text("content:\n  user_save_dir: /tmp/env-saves\n", encoding="utf-8")
    monkeypatch.setenv("SPACESIM_CONFIG", str(p))
    cfg = load_content_config()
    assert cfg.user_save_dir == "/tmp/env-saves"


def test_content_config_and_server_config_share_the_same_file(tmp_path: Path) -> None:
    """content: and server: are independent sections of the same optional file — a config file
    with only one section leaves the other at its own defaults."""
    p = tmp_path / "c.yaml"
    p.write_text("server:\n  port: 9999\n", encoding="utf-8")
    assert load_content_config(p) == ContentConfig()
    p2 = tmp_path / "c2.yaml"
    p2.write_text("content:\n  user_save_dir: /tmp/saves\n", encoding="utf-8")
    assert load_server_config(p2) == ServerConfig()
