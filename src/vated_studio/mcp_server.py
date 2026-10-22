from __future__ import annotations

import json
import logging
import sys
from typing import Any

from . import __version__
from .config import StudioConfig
from .errors import StudioError
from .service import StudioService

# Protocol revisions this server implements, newest first. The installed Freebuff
# host rejects 2025-11-25, so it is deliberately absent; negotiate with the
# client and only add a revision after a real connector test passes.
SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
_COMPATIBILITY_PROTOCOL_VERSION = SUPPORTED_PROTOCOL_VERSIONS[0]


def _tool_definitions(service: StudioService) -> list[dict[str, Any]]:
    return [
        {"name": "ags_status", "description": "Return workspace state, command names, and evidence limitations.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "ags_doctor", "description": "Probe local services and optional tools without generating assets.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "ags_capabilities", "description": "List documented, implemented, and tested studio capabilities with their limits.", "inputSchema": {"type": "object", "properties": {}}},
        {"name": "ags_skill_search", "description": "Search the repository's production skills and return relevant skill references.", "inputSchema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 30}}}},
        {"name": "ags_command", "description": "Execute an explicitly named studio command. Use only documented commands and paths inside the configured workspace unless a command explicitly imports an external source.", "inputSchema": {"type": "object", "required": ["command"], "properties": {"command": {"type": "string", "enum": service.command_names}, "args": {"type": "object"}}}},
    ]


class MCPServer:
    def __init__(self, service: StudioService):
        self.service = service

    def handle(self, request: dict[str, Any]) -> dict[str, Any] | None:
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        if not isinstance(method, str):
            return self._error(request_id, -32600, "Invalid request: method must be a string")
        if method == "notifications/initialized" or method.startswith("notifications/") or method == "$/cancelRequest":
            return None
        if method == "initialize":
            requested = params.get("protocolVersion") if isinstance(params, dict) else None
            negotiated = requested if requested in SUPPORTED_PROTOCOL_VERSIONS else _COMPATIBILITY_PROTOCOL_VERSION
            return {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": negotiated,
                    "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "11vatedtech-ai-game-studio", "version": __version__},
                    "instructions": "Read AGENTS.md first. Use ags_skill_search and ags_capabilities before choosing a workflow. A returned command result is not proof of art quality, commercial rights, or human playtest approval."}}
        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": _tool_definitions(self.service)}}
        if method == "tools/call":
            if not isinstance(params, dict):
                return self._error(request_id, -32602, "tools/call params must be an object")
            name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(arguments, dict):
                return self._error(request_id, -32602, "Tool arguments must be an object")
            try:
                if name == "ags_status":
                    result = self.service.execute("status", {})
                elif name == "ags_doctor":
                    result = self.service.execute("doctor", {})
                elif name == "ags_capabilities":
                    result = self.service.execute("capabilities.list", {})
                elif name == "ags_skill_search":
                    result = self.service.execute("skills.search", arguments)
                elif name == "ags_command":
                    command = arguments.get("command")
                    if command not in self.service.command_names:
                        raise StudioError("Unknown command", code="unknown_command", http_status=404)
                    result = self.service.execute(command, arguments.get("args", {}))
                else:
                    raise StudioError("Unknown MCP tool", code="unknown_tool", details={"name": name}, http_status=404)
                return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2, default=str)}], "structuredContent": result, "isError": False}}
            except (StudioError, ValueError, OSError) as exc:
                payload = exc.as_dict() if isinstance(exc, StudioError) else {"code": type(exc).__name__, "message": str(exc)}
                return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}], "structuredContent": payload, "isError": True}}
        if method == "resources/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": []}}
        if method == "prompts/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"prompts": []}}
        return self._error(request_id, -32601, f"Method not found: {method}") if request_id is not None else None

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def run(config: StudioConfig | None = None) -> None:
    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)
    server = MCPServer(StudioService(config or StudioConfig.from_env()))
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            request = json.loads(raw)
            if not isinstance(request, dict):
                raise ValueError("JSON-RPC payload must be an object")
            response = server.handle(request)
        except (json.JSONDecodeError, ValueError) as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":"), default=str) + "\n")
            sys.stdout.flush()


def main() -> None:
    run(StudioConfig.from_env())


if __name__ == "__main__":
    main()
