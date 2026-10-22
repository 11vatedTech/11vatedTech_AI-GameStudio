from __future__ import annotations

import json
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from vated_studio.api.http_server import _Server, _Handler
from vated_studio import mcp_server as mcp_module
from vated_studio.mcp_server import MCPServer


def test_mcp_initialize_list_tools_and_dispatch(service):
    mcp = MCPServer(service)
    init = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert init["result"]["serverInfo"]["name"] == "11vatedtech-ai-game-studio"
    tools = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    names = {item["name"] for item in tools["result"]["tools"]}
    assert {"ags_status", "ags_doctor", "ags_capabilities", "ags_skill_search", "ags_command"} <= names
    result = mcp.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "ags_status", "arguments": {}}})
    assert result["result"]["isError"] is False
    assert "11vatedTech AI Game Studio" in result["result"]["structuredContent"]["result"]["name"]


def test_mcp_negotiates_only_supported_protocol_versions(service):
    mcp = MCPServer(service)
    assert mcp_module.SUPPORTED_PROTOCOL_VERSIONS == ("2025-06-18", "2025-03-26", "2024-11-05")
    for version in mcp_module.SUPPORTED_PROTOCOL_VERSIONS:
        init = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": version}})
        assert init["result"]["protocolVersion"] == version
    # A missing, malformed or host-rejected version must never echo through.
    for params in (None, {}, {"protocolVersion": "2025-11-25"}, {"protocolVersion": 7}):
        init = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": params})
        assert init["result"]["protocolVersion"] == "2025-06-18"


def test_mcp_rejects_unknown_tools_and_invalid_methods(service):
    mcp = MCPServer(service)
    error = mcp.handle({"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "unknown", "arguments": {}}})
    assert error["result"]["isError"] is True
    bad = mcp.handle({"jsonrpc": "2.0", "id": 9, "method": None})
    assert bad["error"]["code"] == -32600
    assert mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_http_loopback_api_auth_and_command(service, config):
    token = "local-test-token-long-enough"
    server = _Server(("127.0.0.1", 0), _Handler, service, token, config.max_request_bytes)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/health", timeout=2) as response:
            assert response.status == 200
            assert json.loads(response.read())["ok"] is True
        try:
            urlopen(base + "/v1/status", timeout=2)
            assert False, "Expected authentication failure"
        except HTTPError as exc:
            assert exc.code == 401
        req = Request(base + "/v1/status", headers={"Authorization": f"Bearer {token}"})
        with urlopen(req, timeout=2) as response:
            status = json.loads(response.read())
            assert status["result"]["name"] == "11vatedTech AI Game Studio"
        payload = json.dumps({"command": "capabilities.list", "args": {}}).encode()
        req = Request(base + "/v1/command", data=payload, method="POST", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        with urlopen(req, timeout=2) as response:
            result = json.loads(response.read())
            assert result["ok"] is True
        bad_req = Request(base + "/v1/command", data=b"[]", method="POST", headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        try:
            urlopen(bad_req, timeout=2)
            assert False, "Expected bad request"
        except HTTPError as exc:
            assert exc.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
