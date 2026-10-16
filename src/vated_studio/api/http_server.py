from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import hmac
import json
import secrets
import sys

from ..config import StudioConfig
from ..errors import StudioError
from ..jsonio import atomic_write_bytes
from ..service import StudioService


class _Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, address: tuple[str, int], handler: type[BaseHTTPRequestHandler], service: StudioService, token: str, max_bytes: int):
        super().__init__(address, handler)
        self.service = service
        self.token = token.encode("utf-8")
        self.max_bytes = max_bytes


class _Handler(BaseHTTPRequestHandler):
    server: _Server
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: Any) -> None:
        # Keep local prompts and image paths out of the default access log.
        sys.stderr.write("[ags-http] " + (format % args) + "\n")

    def _respond(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def _authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return False
        candidate = header[7:].encode("utf-8")
        return hmac.compare_digest(candidate, self.server.token)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._respond(200, {"ok": True, "service": "11vatedTech AI Game Studio", "version": "0.4.0"})
            return
        if not self._authorized():
            self._respond(401, {"error": {"code": "unauthorized", "message": "Bearer token required"}})
            return
        if self.path == "/v1/status":
            self._respond(200, self.server.service.execute("status", {}))
        elif self.path == "/v1/capabilities":
            self._respond(200, self.server.service.execute("capabilities.list", {}))
        elif self.path == "/v1/commands":
            self._respond(200, {"commands": self.server.service.command_names})
        else:
            self._respond(404, {"error": {"code": "not_found", "message": "Unknown endpoint"}})

    def do_POST(self) -> None:
        if not self._authorized():
            self._respond(401, {"error": {"code": "unauthorized", "message": "Bearer token required"}})
            return
        if self.path != "/v1/command":
            self._respond(404, {"error": {"code": "not_found", "message": "Unknown endpoint"}})
            return
        content_length = self.headers.get("Content-Length")
        try:
            size = int(content_length or "0")
        except ValueError:
            self._respond(400, {"error": {"code": "invalid_content_length", "message": "Content-Length must be an integer"}})
            return
        if size <= 0 or size > self.server.max_bytes:
            self._respond(413 if size > self.server.max_bytes else 400,
                          {"error": {"code": "request_size_invalid", "message": "Request body is empty or exceeds the configured limit"}})
            return
        try:
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Request JSON must be an object")
            command = payload.get("command")
            args = payload.get("args", {})
            response = self.server.service.execute(command, args)
            self._respond(200, {"ok": True, "result": response})
        except json.JSONDecodeError:
            self._respond(400, {"error": {"code": "invalid_json", "message": "Request body is not valid JSON"}})
        except ValueError as exc:
            self._respond(400, {"error": {"code": "invalid_request", "message": str(exc)}})
        except StudioError as exc:
            self._respond(exc.http_status, {"error": exc.as_dict()})
        except (BrokenPipeError, ConnectionResetError):
            return


def _load_or_create_token(config: StudioConfig) -> str:
    if config.token:
        return config.token
    token_path = config.workspace / ".state" / "api-token"
    token_path.parent.mkdir(parents=True, exist_ok=True)
    if token_path.is_file():
        token = token_path.read_text(encoding="utf-8").strip()
        if len(token) >= 32:
            return token
    token = secrets.token_urlsafe(36)
    atomic_write_bytes(token_path, (token + "\n").encode("utf-8"))
    try:
        token_path.chmod(0o600)
    except OSError:
        pass
    return token


def serve(config: StudioConfig | None = None) -> None:
    config = config or StudioConfig.from_env()
    is_loopback = config.host in {"127.0.0.1", "localhost", "::1"}
    if not is_loopback and not config.token:
        raise StudioError("Non-loopback HTTP binding requires an explicitly configured token", code="unsafe_bind")
    service = StudioService(config)
    token = _load_or_create_token(config)
    server = _Server((config.host, config.port), _Handler, service, token, config.max_request_bytes)
    print(f"AI Game Studio API listening at http://{config.host}:{config.port}", file=sys.stderr)
    print(f"Token stored at: {config.workspace / '.state' / 'api-token'} (read locally; do not commit it)", file=sys.stderr)
    print("POST /v1/command with Authorization: Bearer <token>; GET /health is unauthenticated.", file=sys.stderr)
    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
