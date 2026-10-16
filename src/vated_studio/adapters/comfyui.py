from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import time
import uuid

from ..errors import StudioError
from ..jsonio import sha256_file
from .http_json import request_bytes, request_json


def validate_api_workflow(workflow: Any) -> dict[str, Any]:
    if not isinstance(workflow, dict) or not workflow:
        raise StudioError("ComfyUI workflow must be a non-empty object", code="invalid_workflow")
    for node_id, node in workflow.items():
        if not isinstance(node, dict) or not isinstance(node.get("class_type"), str) or not isinstance(node.get("inputs"), dict):
            raise StudioError("Workflow must use ComfyUI API-format nodes", code="invalid_workflow", details={"node": str(node_id)})
    return workflow


class ComfyUIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8188", timeout: float = 240.0, client_id: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client_id = client_id or f"11vatedtech-{uuid.uuid4().hex[:12]}"

    def health(self) -> dict[str, Any]:
        try:
            stats = request_json(self.base_url, "/system_stats", timeout=min(5.0, self.timeout))
            return {"ok": True, "endpoint": self.base_url, "device_count": len(stats.get("devices", [])) if isinstance(stats, dict) else None}
        except StudioError as exc:
            return {"ok": False, "endpoint": self.base_url, "error": exc.as_dict()}

    def submit(self, workflow: dict[str, Any], *, extra_data: dict[str, Any] | None = None) -> str:
        data = {"prompt": validate_api_workflow(workflow), "client_id": self.client_id}
        if extra_data:
            data["extra_data"] = extra_data
        result = request_json(self.base_url, "/prompt", method="POST", payload=data, timeout=min(self.timeout, 30.0))
        if not isinstance(result, dict) or not result.get("prompt_id"):
            raise StudioError("ComfyUI did not return a prompt_id", code="invalid_provider_response", details={"response": result})
        if result.get("node_errors"):
            raise StudioError("ComfyUI rejected one or more workflow nodes", code="workflow_node_errors", details={"node_errors": result["node_errors"]})
        return str(result["prompt_id"])

    def history(self, prompt_id: str) -> dict[str, Any]:
        value = request_json(self.base_url, f"/history/{prompt_id}", timeout=min(self.timeout, 30.0))
        if not isinstance(value, dict):
            raise StudioError("ComfyUI history response was not an object", code="invalid_provider_response")
        return value

    def wait_for_completion(self, prompt_id: str, *, poll_interval: float = 0.5, timeout: float | None = None) -> dict[str, Any]:
        deadline = time.monotonic() + (timeout if timeout is not None else self.timeout)
        while time.monotonic() < deadline:
            data = self.history(prompt_id)
            entry = data.get(prompt_id)
            if isinstance(entry, dict):
                status = entry.get("status", {})
                if isinstance(status, dict) and status.get("status_str") == "error":
                    raise StudioError("ComfyUI generation failed", code="generation_failed", details={"prompt_id": prompt_id, "status": status})
                outputs = entry.get("outputs")
                if isinstance(outputs, dict) and outputs:
                    images = [image for node in outputs.values() if isinstance(node, dict) for image in node.get("images", []) if isinstance(image, dict) and image.get("filename")]
                    if images:
                        return {"prompt_id": prompt_id, "entry": entry, "images": images}
            time.sleep(max(0.1, min(5.0, poll_interval)))
        raise StudioError("Timed out waiting for ComfyUI output", code="generation_timeout", details={"prompt_id": prompt_id, "timeout_seconds": timeout or self.timeout}, http_status=504)

    def download_image(self, descriptor: dict[str, Any], destination: str | Path) -> dict[str, Any]:
        if not isinstance(descriptor.get("filename"), str) or not descriptor["filename"]:
            raise StudioError("ComfyUI image descriptor has no filename", code="invalid_image_descriptor")
        raw = request_bytes(self.base_url, "/view", query={"filename": descriptor["filename"], "subfolder": descriptor.get("subfolder", ""), "type": descriptor.get("type", "output")}, timeout=self.timeout)
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return {"path": str(path), "bytes": len(raw), "sha256": sha256_file(path), "source": descriptor}

    def generate_from_workflow(self, workflow: dict[str, Any], destination_dir: str | Path, *, timeout: float | None = None) -> dict[str, Any]:
        prompt_id = self.submit(workflow)
        complete = self.wait_for_completion(prompt_id, timeout=timeout)
        target_dir = Path(destination_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        downloaded = []
        for index, image_info in enumerate(complete["images"], start=1):
            filename = Path(str(image_info["filename"])).name
            suffix = Path(filename).suffix.lower() or ".png"
            dest = target_dir / f"{index:02d}_{Path(filename).stem}{suffix}"
            downloaded.append(self.download_image(image_info, dest))
        return {"provider": "comfyui", "prompt_id": prompt_id, "images": downloaded,
                "status": "generated", "note": "Generation completed. Candidate approval and engine integration are separate gates."}


def load_api_workflow(path: str | Path) -> dict[str, Any]:
    try:
        workflow = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StudioError("Could not load workflow JSON", code="workflow_load_error", details={"path": str(path), "reason": str(exc)}) from exc
    return validate_api_workflow(workflow)
