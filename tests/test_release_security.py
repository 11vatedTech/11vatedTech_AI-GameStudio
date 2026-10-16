from pathlib import Path
import json
import zipfile
import pytest

from vated_studio.qa.release_audit import audit_release, package_release


def test_release_package_excludes_secrets_state_caches_and_model_weights(tmp_path):
    root = tmp_path / "workspace"
    source = root / "release-src"
    source.mkdir(parents=True)
    (source / "README.md").write_text("public docs")
    (source / ".env.example").write_text("AGS_PORT=8765")
    (source / ".env").write_text("TOKEN=secret")
    (source / "weights.safetensors").write_bytes(b"model")
    (source / "state.db").write_bytes(b"db")
    (source / ".state").mkdir()
    (source / ".state" / "api-token").write_text("private token")
    (source / ".venv").mkdir()
    (source / "package.egg-info").mkdir()
    (source / "package.egg-info" / "PKG-INFO").write_text("generated metadata")
    (source / ".venv" / "pyvenv.cfg").write_text("private env")
    archive = root / "out" / "release.zip"
    result = package_release(root, "release-src", "out/release.zip")
    assert result["zip_integrity"] == "passed"
    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        assert zf.testzip() is None
    assert "README.md" in names and ".env.example" in names
    assert ".env" not in names and "weights.safetensors" not in names and "state.db" not in names
    assert not any(name.startswith(".state/") or name.startswith(".venv/") or name.startswith("package.egg-info/") for name in names)
    manifest = json.loads(Path(result["manifest_file"]).read_text())
    assert any(row["reason"] == "environment_or_secret_file" for row in manifest["excluded_files"])
    assert any(row["reason"] == "model_weight_or_binary_checkpoint" for row in manifest["excluded_files"])
    assert any(row["reason"] == "build_metadata" for row in manifest["excluded_files"])


def test_release_package_refuses_overwrite_without_explicit_flag(tmp_path):
    root = tmp_path / "w"
    src = root / "src"
    src.mkdir(parents=True)
    (src / "file.txt").write_text("first")
    result = package_release(root, "src", "release.zip")
    old_hash = result["sha256"]
    with pytest.raises(ValueError, match="already exists"):
        package_release(root, "src", "release.zip")
    (src / "file.txt").write_text("second")
    replacement = package_release(root, "src", "release.zip", overwrite=True)
    assert replacement["sha256"] != old_hash


def test_release_package_refuses_symlink_and_output_inside_source(tmp_path):
    root = tmp_path / "w"
    src = root / "src"
    src.mkdir(parents=True)
    (src / "x.txt").write_text("x")
    with pytest.raises(ValueError, match="inside the source tree"):
        package_release(root, "src", "src/inside.zip")
    try:
        (src / "escape").symlink_to(root / "outside.txt")
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation unavailable")
    with pytest.raises(ValueError, match="symlink"):
        package_release(root, "src", "out.zip")


def test_release_audit_flags_publication_risks(tmp_path):
    root = tmp_path / "w"
    release = root / "release"
    release.mkdir(parents=True)
    (release / "README.md").write_text("public")
    (release / ".env").write_text("TOKEN=do-not-publish")
    (release / "weights.ckpt").write_bytes(b"weights")
    audit = audit_release(root, "release", required_files=["README.md", "LICENSE"])
    assert audit["status"] == "blocked"
    codes = {item["code"] for item in audit["findings"]}
    assert "environment_or_secret_file" in codes
    assert "model_weight_or_binary_checkpoint" in codes
    assert "required_file_missing" in codes
    assert audit["human_gates"]["cold_playtest"] == "open"
