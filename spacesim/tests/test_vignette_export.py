"""IP-1180 (FR-5420) — save_vignette()'s configured user_save_dir write target.
IP-1200 (FR-5510) — export_vignette()'s start_epoch/tracks/space-weather/version extensions."""
from __future__ import annotations

import pytest

from spacesim.content.vignette import Vignette, VignetteContext
from spacesim.content.vignette_export import export_vignette, save_vignette
from spacesim.engine.custody import Track
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


# -- IP-1200 (FR-5510) — start_epoch / tracks / space-weather / version -----------------------

def test_export_vignette_omitted_start_epoch_reproduces_prior_behavior():
    """Regression: with no start_epoch argument, export_vignette() reproduces IP-1173's exact
    prior output — ctx.start_epoch, not world.now."""
    world, ctx = _empty_world_and_ctx()
    world.now = 999_000_000
    vig = export_vignette(world, ctx, "test-omitted-start-epoch", "Omitted")
    from spacesim.engine import simtime
    assert vig.start_epoch_utc == simtime.to_iso(ctx.start_epoch)


def test_export_vignette_explicit_start_epoch_overrides_ctx_start_epoch():
    world, ctx = _empty_world_and_ctx()
    save_moment = 999_000_000
    vig = export_vignette(world, ctx, "test-explicit-start-epoch", "Explicit", start_epoch=save_moment)
    from spacesim.engine import simtime
    assert vig.start_epoch_utc == simtime.to_iso(save_moment)
    assert vig.start_epoch_utc != simtime.to_iso(ctx.start_epoch)


def test_export_vignette_carries_forward_tracks_space_weather_and_version():
    world, ctx = _empty_world_and_ctx()
    world.tracks.append(Track(object="SAT-RED", owner="blue", confidence=0.7, last_observation=0))
    world.space_weather = {"severity": "severe"}
    vig = export_vignette(world, ctx, "test-carry-forward", "Carry Forward")
    assert len(vig.initial_tracks) == 1
    assert vig.initial_tracks[0]["object"] == "SAT-RED"
    assert vig.initial_tracks[0]["confidence"] == pytest.approx(0.7)
    assert vig.initial_space_weather == {"severity": "severe"}
    assert vig.simulator_version  # non-empty
