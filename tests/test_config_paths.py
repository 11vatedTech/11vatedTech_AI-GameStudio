from pathlib import Path
import pytest

from vated_studio.config import StudioConfig, _endpoint
from vated_studio.errors import StudioError
from vated_studio.paths import ensure_inside, require_file, slugify


def test_config_defaults_are_loopback_and_local(tmp_path):
    config = StudioConfig.from_env(tmp_path, env={})
    assert config.host == "127.0.0.1"
    assert config.port == 8765
    assert config.allow_remote_providers is False
    assert config.workspace == tmp_path.resolve()


def test_env_file_is_overridden_by_process_env(tmp_path):
    (tmp_path / ".env").write_text("AGS_PORT=9000\nCOMFYUI_URL=http://127.0.0.1:9001\n", encoding="utf-8")
    config = StudioConfig.from_env(tmp_path, env={"AGS_PORT": "9001"})
    assert config.port == 9001
    assert config.comfyui_url == "http://127.0.0.1:9001"


@pytest.mark.parametrize("raw", ["file:///tmp", "http://user:pass@localhost:8188", "ftp://localhost", "not-a-url"])
def test_rejects_invalid_provider_endpoint(raw):
    with pytest.raises(ValueError):
        _endpoint("TEST_URL", raw, False)


def test_remote_provider_requires_opt_in():
    with pytest.raises(ValueError):
        StudioConfig.from_env(".", env={"COMFYUI_URL": "http://192.0.2.1:8188"})
    config = StudioConfig.from_env(".", env={"COMFYUI_URL": "http://192.0.2.1:8188", "AGS_ALLOW_REMOTE_PROVIDERS": "true"})
    assert config.comfyui_url == "http://192.0.2.1:8188"


def test_non_loopback_server_binding_requires_token(tmp_path):
    with pytest.raises(ValueError):
        StudioConfig.from_env(tmp_path, env={"AGS_HOST": "0.0.0.0"})
    assert StudioConfig.from_env(tmp_path, env={"AGS_HOST": "0.0.0.0", "AGS_TOKEN": "strong-test-token"}).host == "0.0.0.0"


def test_bounded_config_values(tmp_path):
    with pytest.raises(ValueError):
        StudioConfig.from_env(tmp_path, env={"AGS_PORT": "70000"})
    with pytest.raises(ValueError):
        StudioConfig.from_env(tmp_path, env={"AGS_MAX_REQUEST_BYTES": "1"})


def test_path_containment_and_symlink_escape(tmp_path):
    root = tmp_path / "safe"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    with pytest.raises(StudioError) as exc:
        ensure_inside(root, "../outside.txt")
    assert exc.value.code == "path_outside_workspace"
    try:
        (root / "link").symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is unavailable")
    with pytest.raises(StudioError):
        ensure_inside(root, "link")


def test_slugify_and_require_file(tmp_path):
    assert slugify(" My Beautiful Game! ") == "my-beautiful-game"
    root = tmp_path / "r"
    root.mkdir()
    (root / "x.json").write_text("{}")
    assert require_file(root, "x.json", {".json"}).name == "x.json"
    with pytest.raises(StudioError):
        require_file(root, "x.json", {".png"})
