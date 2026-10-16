from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse


def _read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return values
    for number, line in enumerate(lines, 1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if text.startswith("export "):
            text = text[7:].strip()
        if "=" not in text:
            raise ValueError(f"Invalid .env syntax at line {number}")
        key, val = text.split("=", 1)
        key, val = key.strip(), val.strip()
        if not key or not key.replace("_", "").isalnum() or not (key[0].isalpha() or key[0] == "_"):
            raise ValueError(f"Invalid environment key at line {number}")
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        values[key] = val
    return values


def _bounded_int(env: Mapping[str, str], key: str, default: int, low: int, high: int) -> int:
    raw = env.get(key, "")
    if not raw:
        return default
    try:
        val = int(raw)
    except ValueError as exc:
        raise ValueError(f"{key} must be an integer") from exc
    if not low <= val <= high:
        raise ValueError(f"{key} must be between {low} and {high}")
    return val


def _endpoint(name: str, value: str, allow_remote: bool) -> str:
    url = urlparse(value)
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
        raise ValueError(f"{name} must be an http(s) URL without embedded credentials")
    local = url.hostname.lower() in {"localhost", "127.0.0.1", "::1"}
    if not local and not allow_remote:
        raise ValueError(f"{name} must point to loopback unless AGS_ALLOW_REMOTE_PROVIDERS=true")
    return value.rstrip("/")


@dataclass(frozen=True, slots=True)
class StudioConfig:
    workspace: Path
    host: str = "127.0.0.1"
    port: int = 8765
    token: str | None = None
    request_timeout_seconds: int = 240
    max_request_bytes: int = 2_000_000
    allow_remote_providers: bool = False
    comfyui_url: str = "http://127.0.0.1:8188"
    sd_webui_url: str = "http://127.0.0.1:7860"
    godot_bin: str = "godot"
    blender_bin: str = "blender"
    rife_bin: str | None = None

    @classmethod
    def from_env(cls, workspace: str | Path | None = None, env: Mapping[str, str] | None = None) -> "StudioConfig":
        process_env = dict(os.environ if env is None else env)
        hint = Path(workspace or process_env.get("AGS_WORKSPACE", ".")).expanduser().resolve()
        merged = _read_env(hint / ".env")
        merged.update(process_env)
        root = Path(workspace or merged.get("AGS_WORKSPACE", str(hint))).expanduser().resolve()
        allow_remote = merged.get("AGS_ALLOW_REMOTE_PROVIDERS", "false").lower() in {"1", "true", "yes"}
        host = merged.get("AGS_HOST", "127.0.0.1").strip()
        token = merged.get("AGS_TOKEN") or None
        if host not in {"127.0.0.1", "localhost", "::1"} and not token:
            raise ValueError("Binding to a non-loopback host requires AGS_TOKEN")
        return cls(
            workspace=root,
            host=host,
            port=_bounded_int(merged, "AGS_PORT", 8765, 1, 65535),
            token=token,
            request_timeout_seconds=_bounded_int(merged, "AGS_REQUEST_TIMEOUT_SECONDS", 240, 5, 3600),
            max_request_bytes=_bounded_int(merged, "AGS_MAX_REQUEST_BYTES", 2_000_000, 1024, 20_000_000),
            allow_remote_providers=allow_remote,
            comfyui_url=_endpoint("COMFYUI_URL", merged.get("COMFYUI_URL", "http://127.0.0.1:8188"), allow_remote),
            sd_webui_url=_endpoint("SD_WEBUI_URL", merged.get("SD_WEBUI_URL", "http://127.0.0.1:7860"), allow_remote),
            godot_bin=merged.get("GODOT_BIN", "godot"),
            blender_bin=merged.get("BLENDER_BIN", "blender"),
            rife_bin=merged.get("RIFE_BIN") or None,
        )
