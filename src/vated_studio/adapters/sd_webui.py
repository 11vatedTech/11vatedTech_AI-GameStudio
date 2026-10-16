from __future__ import annotations

from pathlib import Path
from typing import Any
import base64

from ..errors import StudioError
from ..jsonio import sha256_file
from .http_json import request_json


class SDWebUIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:7860", timeout: float = 240):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> dict[str, Any]:
        try:
            result = request_json(self.base_url, "/sdapi/v1/options", timeout=min(self.timeout, 5))
            return {"ok": isinstance(result, dict), "endpoint": self.base_url}
        except StudioError as exc:
            return {"ok": False, "endpoint": self.base_url, "error": exc.as_dict()}

    def generate(self, *, prompt: str, negative_prompt: str = "", width: int = 512, height: int = 512,
                 steps: int = 24, cfg_scale: float = 6.0, seed: int = -1, sampler_name: str | None = None,
                 output_dir: str | Path) -> dict[str, Any]:
        if not prompt.strip() or not 64 <= width <= 2048 or not 64 <= height <= 2048 or not 1 <= steps <= 100:
            raise StudioError("Invalid generation prompt, dimensions, or steps", code="invalid_generation_options")
        payload = {"prompt": prompt, "negative_prompt": negative_prompt, "width": width, "height": height,
                   "steps": steps, "cfg_scale": cfg_scale, "seed": seed, "batch_size": 1, "n_iter": 1}
        if sampler_name:
            payload["sampler_name"] = sampler_name
        result = request_json(self.base_url, "/sdapi/v1/txt2img", method="POST", payload=payload, timeout=self.timeout,)
        images = result.get("images") if isinstance(result, dict) else None
        if not isinstance(images, list) or not images:
            raise StudioError("Stable Diffusion WebUI returned no images", code="invalid_provider_response")
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        for index, encoded in enumerate(images, 1):
            if not isinstance(encoded, str):
                continue
            if "," in encoded and encoded.startswith("data:"):
                encoded = encoded.split(",", 1)[1]
            try:
                raw = base64.b64decode(encoded, validate=True)
            except ValueError as exc:
                raise StudioError("Provider returned invalid base64 image data", code="invalid_image_payload") from exc
            dest = target_dir / f"sd-webui-{index:02d}.png"
            dest.write_bytes(raw)
            outputs.append({"path": str(dest), "bytes": len(raw), "sha256": sha256_file(dest)})
        return {"provider": "sd-webui", "images": outputs, "info": result.get("info"), "status": "generated"}
