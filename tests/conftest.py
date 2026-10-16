from __future__ import annotations

from pathlib import Path
import pytest

from vated_studio.config import StudioConfig
from vated_studio.service import StudioService


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    root = tmp_path / "workspace"
    root.mkdir()
    return root


@pytest.fixture
def config(workspace: Path) -> StudioConfig:
    return StudioConfig(workspace=workspace, request_timeout_seconds=5, max_request_bytes=64_000)


@pytest.fixture
def service(config: StudioConfig) -> StudioService:
    return StudioService(config)
