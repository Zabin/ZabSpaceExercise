"""IP-1180 (FR-5420) — save_vignette()'s configured user_save_dir write target."""
from __future__ import annotations

import pytest

from spacesim.content.vignette import Vignette, VignetteContext
from spacesim.content.vignette_export import export_vignette, save_vignette
from spacesim.engine.world import WorldState


def _empty_world_and_ctx():
    world = WorldState()
    ctx = VignetteContext(start_epoch=0, param_values={}, roe={}, landing_deadline=0)
    return world, ctx


def test_save_vignette_raises_when_no_user_save_dir_configured(tmp_path, monkeypatch):
    monkeypatch.setenv("SPACESIM_CONFIG", str(tmp_path / "missing.yaml"))
    world, ctx = _empty_world_and_ctx()
    with pytest.raises(ValueError, match="no user-save directory configured"):
        save_vignette(world, ctx, "test-no-save-dir", "No Save Dir")


def test_save_vignette_writes_to_configured_user_save_dir_not_vignette_dir(tmp_path, monkeypatch):
    from spacesim.content.vignette import VIGNETTE_DIR
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    cfg_path = tmp_path / "spacesim.config.yaml"
    cfg_path.write_text(f"content:\n  user_save_dir: {save_dir}\n", encoding="utf-8")
    monkeypatch.setenv("SPACESIM_CONFIG", str(cfg_path))
    world, ctx = _empty_world_and_ctx()
    path = save_vignette(world, ctx, "test-configured-save-dir", "Configured Save Dir")
    try:
        assert str(save_dir) in path
        assert not (VIGNETTE_DIR / "test-configured-save-dir.yaml").exists()
    finally:
        from pathlib import Path
        Path(path).unlink(missing_ok=True)


@pytest.mark.parametrize("bad_id", [
    "../../etc/passwd",
    "/etc/passwd",
    "foo/bar",
    "id with space",
])
def test_export_vignette_rejects_traversal_id_before_any_filesystem_access(bad_id, tmp_path, monkeypatch):
    save_dir = tmp_path / "saves"
    save_dir.mkdir()
    cfg_path = tmp_path / "spacesim.config.yaml"
    cfg_path.write_text(f"content:\n  user_save_dir: {save_dir}\n", encoding="utf-8")
    monkeypatch.setenv("SPACESIM_CONFIG", str(cfg_path))
    world, ctx = _empty_world_and_ctx()
    with pytest.raises(ValueError):
        save_vignette(world, ctx, bad_id, "Bad Id")
    assert list(save_dir.iterdir()) == []
