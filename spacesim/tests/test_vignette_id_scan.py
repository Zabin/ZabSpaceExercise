"""IP-1311 — vignette id scan robustness (FS-131 v1.1; FR-5310, NFR-1600; closes BL-0252).

One unreadable or malformed file in a vignette folder never turns an id lookup into a 500.
"""

from __future__ import annotations

import shutil

import pytest
import yaml
from fastapi.testclient import TestClient

from spacesim.content import vignette as vmod
from spacesim.content.vignette import (
    VIGNETTE_DIR,
    VignetteValidationError,
    list_vignettes,
    load_vignette,
)
from spacesim.ui_web.server import create_app

pytestmark = pytest.mark.verifies("FR-5310", "NFR-1600")

BAD_YAML = "vignette: [unclosed\n  - : :\n"


@pytest.fixture
def folder(tmp_path, monkeypatch):
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.setattr(vmod, "VIGNETTE_DIR", root)
    monkeypatch.setattr(vmod, "_configured_external_dirs", lambda: [])
    for name in ("01-leo-isr-denial.yaml", "07-sda-custody-hunt.yaml"):
        shutil.copy(VIGNETTE_DIR / name, root / name)
    return root


@pytest.fixture
def client(folder):
    return TestClient(create_app(), raise_server_exceptions=False)


def test_unknown_id_with_bad_file_is_not_found(folder, client):
    (folder / "00-aaa-bad.yaml").write_text(BAD_YAML, encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        load_vignette("nosuch")
    r = client.post("/api/sessions", json={"vignette_id": "nosuch", "seed": 1})
    assert r.status_code == 404
    assert "nosuch" in r.json()["detail"]


def test_valid_vignette_after_bad_file_loads(folder, client):
    (folder / "00-aaa-bad.yaml").write_text(BAD_YAML, encoding="utf-8")
    assert load_vignette("sda-custody-hunt").id == "sda-custody-hunt"
    r = client.post("/api/sessions", json={"vignette_id": "sda-custody-hunt", "seed": 1})
    assert r.status_code == 200, r.text


def test_non_mapping_vignette_block_skipped_in_both_roots(folder, tmp_path):
    (folder / "aaa-list.yaml").write_text("vignette: [1, 2]\n", encoding="utf-8")
    (folder / "aab-str.yaml").write_text("vignette: just a string\n", encoding="utf-8")
    ext = tmp_path / "ext"
    ext.mkdir()
    (ext / "aaa-list.yaml").write_text("vignette: [1, 2]\n", encoding="utf-8")
    shutil.copy(VIGNETTE_DIR / "03-gnss-ew-campaign.yaml", ext / "03-gnss-ew-campaign.yaml")
    with pytest.raises(FileNotFoundError):
        load_vignette("nosuch", external_dirs=[ext])
    assert load_vignette("sda-custody-hunt", external_dirs=[ext]).id == "sda-custody-hunt"
    ext_id = yaml.safe_load((ext / "03-gnss-ew-campaign.yaml").read_text())["vignette"]["id"]
    assert load_vignette(ext_id, external_dirs=[ext]).id == ext_id


def test_exact_name_bad_file_still_refused_precisely(folder, client):
    (folder / "bad-yaml.yaml").write_text(BAD_YAML, encoding="utf-8")
    with pytest.raises(VignetteValidationError) as info:
        load_vignette("bad-yaml")
    assert info.value.problems[0]["where"] == "bad-yaml.yaml"
    assert info.value.problems[0]["reason"].startswith("not valid YAML")
    r = client.post("/api/sessions", json={"vignette_id": "bad-yaml", "seed": 1})
    assert r.status_code == 400
    assert r.json()["detail"]["error"] == "invalid_vignette"


def test_schema_broken_file_found_by_declared_id_is_refused(folder, client):
    data = yaml.safe_load((VIGNETTE_DIR / "07-sda-custody-hunt.yaml").read_text())
    data["vignette"]["id"] = "broken-x"
    data["vignette"]["blue_forces"] = "not-a-list"
    (folder / "zz-broken.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    (folder / "bad-yaml.yaml").write_text(BAD_YAML, encoding="utf-8")
    with pytest.raises(VignetteValidationError):
        load_vignette("broken-x")
    r = client.post("/api/sessions", json={"vignette_id": "broken-x", "seed": 1})
    assert r.status_code == 400


def test_shipped_library_ids_all_resolve():
    for entry in list_vignettes():
        assert load_vignette(entry["id"]).id == entry["id"]
