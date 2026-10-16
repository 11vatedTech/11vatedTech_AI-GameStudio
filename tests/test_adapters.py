from __future__ import annotations

import base64
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from vated_studio.errors import StudioError
from vated_studio.adapters.comfyui import ComfyUIClient, validate_api_workflow
from vated_studio.adapters.klein_workflows import make_klein_txt2img
from vated_studio.adapters.sd_webui import SDWebUIClient
from vated_studio.adapters.zimage_workflows import (
    QWEN_ENCODER, ZIMAGE_UNET, ZIMAGE_VAE, make_zimage_txt2img,
)


def test_comfy_workflow_validation_and_klein_builder():
    with pytest.raises(StudioError):
        validate_api_workflow([])
    with pytest.raises(StudioError):
        validate_api_workflow({"1": {"inputs": {}}})
    workflow = make_klein_txt2img(prompt="A red fox", width=512, height=512, seed=17)
    assert workflow["1"]["inputs"]["weight_dtype"] == "fp8_e4m3fn"
    assert workflow["12"]["class_type"] == "SamplerCustomAdvanced"
    assert workflow["9"]["class_type"] == "Flux2Scheduler"
    assert workflow["7"]["class_type"] == "CFGGuider"
    assert "FluxGuidance" not in {node["class_type"] for node in workflow.values()}
    with pytest.raises(ValueError):
        make_klein_txt2img(prompt="", width=512, height=512)
    with pytest.raises(ValueError):
        make_klein_txt2img(prompt="test", width=513, height=512)


def _server():
    try:
        from PIL import Image
        import io
        image = Image.new("RGB", (8, 8), (150, 50, 20))
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        png = buf.getvalue()
    except ImportError:
        png = b"png-test-bytes"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass
        def _send(self, obj, status=200):
            data = json.dumps(obj).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def do_GET(self):
            if self.path == "/system_stats":
                self._send({"devices": [{"name": "test"}]})
            elif self.path.startswith("/history/"):
                pid = self.path.split("/")[-1]
                self._send({pid: {"status": {"status_str": "success"}, "outputs": {"9": {"images": [{"filename": "sample.png", "subfolder": "", "type": "output"}]}}}})
            elif self.path.startswith("/view?"):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(png)))
                self.end_headers()
                self.wfile.write(png)
            elif self.path == "/sdapi/v1/options":
                self._send({"sd_model_checkpoint": "test"})
            else:
                self._send({"error": "not found"}, 404)
        def do_POST(self):
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size))
            if self.path == "/prompt":
                self._send({"prompt_id": "p1", "node_errors": {}})
            elif self.path == "/sdapi/v1/txt2img":
                self._send({"images": [base64.b64encode(png).decode()], "info": "seed: 1"})
            else:
                self._send({"error": "not found"}, 404)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_comfy_client_end_to_end_with_local_protocol_fixture(tmp_path):
    server, thread = _server()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        client = ComfyUIClient(base_url=base, timeout=3)
        assert client.health()["ok"] is True
        workflow = {"1": {"class_type": "SaveImage", "inputs": {"filename_prefix": "test", "images": ["2", 0]}}}
        result = client.generate_from_workflow(workflow, tmp_path / "gen", timeout=2)
        assert result["status"] == "generated"
        assert Path(result["images"][0]["path"]).is_file()
        assert len(result["images"][0]["sha256"]) == 64
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_sd_webui_client_saves_generated_image(tmp_path):
    server, thread = _server()
    try:
        client = SDWebUIClient(f"http://127.0.0.1:{server.server_port}", timeout=3)
        assert client.health()["ok"] is True
        result = client.generate(prompt="A test image", width=64, height=64, steps=1, output_dir=tmp_path)
        assert result["status"] == "generated"
        assert Path(result["images"][0]["path"]).is_file()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


def test_sd_webui_rejects_invalid_generation(tmp_path):
    client = SDWebUIClient("http://127.0.0.1:1", timeout=1)
    with pytest.raises(StudioError):
        client.generate(prompt="", output_dir=tmp_path)


def test_zimage_workflow_builder_matches_documented_nodes_and_guards_inputs():
    workflow = make_zimage_txt2img(prompt="A painted fantasy lantern", width=512, height=768, seed=1101)
    assert workflow["1"]["class_type"] == "UNETLoader"
    assert workflow["1"]["inputs"]["unet_name"] == ZIMAGE_UNET
    assert workflow["2"]["inputs"]["clip_name"] == QWEN_ENCODER
    assert workflow["3"]["inputs"]["vae_name"] == ZIMAGE_VAE
    assert workflow["9"]["inputs"]["seed"] == 1101
    assert workflow["9"]["inputs"]["steps"] == 8
    assert workflow["11"]["class_type"] == "SaveImage"
    with pytest.raises(ValueError):
        make_zimage_txt2img(prompt="   ")
    with pytest.raises(ValueError):
        make_zimage_txt2img(prompt="test", width=250, height=512)
    with pytest.raises(ValueError):
        make_zimage_txt2img(prompt="test", width=513, height=512)
