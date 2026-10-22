"""Regression: /health must report the installed package version, not a hardcoded one.

Stdlib-only so it runs without pytest; it starts the real loopback server.
"""
from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen

from vated_studio import __version__
from vated_studio.api.http_server import _Handler, _Server
from vated_studio.config import StudioConfig
from vated_studio.service import StudioService


class HealthVersionTest(unittest.TestCase):
    def test_health_reports_package_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = StudioConfig(workspace=Path(tmp), request_timeout_seconds=5, max_request_bytes=64_000)
            server = _Server(("127.0.0.1", 0), _Handler, StudioService(config), "local-test-token-long-enough", config.max_request_bytes)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with urlopen(f"http://127.0.0.1:{server.server_port}/health", timeout=5) as response:
                    body = json.loads(response.read())
            finally:
                server.shutdown()
                server.server_close()
        self.assertTrue(body["ok"])
        self.assertEqual(body["version"], __version__)


if __name__ == "__main__":
    unittest.main()
