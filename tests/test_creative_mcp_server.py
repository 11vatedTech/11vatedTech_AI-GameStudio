import json
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import importlib.util
spec = importlib.util.spec_from_file_location("creative_mcp_server", ROOT / "tools/creative_mcp_server.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestCreativeMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = mod.CreativeMCPServer(ROOT)

    def test_initialize_and_tools_list(self):
        self.assertEqual(mod.SUPPORTED_PROTOCOL_VERSIONS, ("2025-06-18", "2025-03-26", "2024-11-05"))
        self.assertEqual(mod.LATEST_SUPPORTED_PROTOCOL_VERSION, "2025-06-18")
        self.assertEqual(mod.COMPATIBILITY_PROTOCOL_VERSION, "2025-06-18")
        for version in mod.SUPPORTED_PROTOCOL_VERSIONS:
            self.assertEqual(
                self.server.handle({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":version}})["result"]["protocolVersion"],
                version,
                f"server must echo supported client version {version}",
            )
        initialized = self.server.handle({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}})
        self.assertEqual(initialized["result"]["serverInfo"]["name"], "11vatedtech-creative-tools")
        self.assertEqual(initialized["result"]["protocolVersion"], "2025-06-18")
        tools = self.server.handle({"jsonrpc":"2.0","id":2,"method":"tools/list"})["result"]["tools"]
        names = {tool["name"] for tool in tools}
        self.assertIn("ags_blender_author_action", names)
        self.assertIn("ags_blender_render_action_review", names)
        self.assertIn("ags_creative_preflight", names)
        self.assertGreaterEqual(len(names), 5)

    def test_initialize_falls_back_when_client_requests_unsupported_latest_version(self):
        initialized = self.server.handle({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25"}})
        self.assertEqual(initialized["result"]["protocolVersion"], "2025-06-18")
        self.assertNotIn("2025-11-25", mod.SUPPORTED_PROTOCOL_VERSIONS,
                         "the installed Freebuff host rejects 2025-11-25; do not advertise it")

    def test_initialize_unknown_version_uses_compatibility_version(self):
        initialized = self.server.handle({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2099-01-01"}})
        self.assertEqual(initialized["result"]["protocolVersion"], mod.COMPATIBILITY_PROTOCOL_VERSION)
        self.assertEqual(initialized["result"]["protocolVersion"], "2025-06-18")

    def test_initialize_malformed_params_use_compatibility_version(self):
        initialized = self.server.handle({"jsonrpc":"2.0","id":1,"method":"initialize","params":None})
        self.assertEqual(initialized["result"]["protocolVersion"], "2025-06-18")

    def test_paths_must_stay_inside_workspace(self):
        for raw in ("../outside.txt", "C:\\Windows\\system.ini", str(Path("/etc/passwd"))):
            with self.assertRaises(mod.CreativeMCPError):
                self.server.safe_path(raw)

    def test_path_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"; workspace.mkdir()
            outside = Path(tmp) / "outside"; outside.mkdir()
            try:
                (workspace / "link").symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("This platform does not permit creating symlinks in the test environment")
            server = mod.CreativeMCPServer(workspace)
            with self.assertRaises(mod.CreativeMCPError): server.safe_path("link/file.txt")

    def test_pose_spec_validation_through_tool(self):
        result = self.server.execute("ags_validate_blender_pose_spec", {"pose_spec_path":"examples/blender/torch_sweep_pose_spec.example.json"})
        self.assertTrue(result["valid"], result)

    def test_sequence_validation_through_tool(self):
        result = self.server.execute("ags_validate_animation_sequence", {"manifest_path":"examples/animation/torch_sweep.sequence.example.json"})
        self.assertTrue(result["valid"], result)

    def test_static_image_shortcut_is_reported_as_invalid(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            temp_dir = Path(tmp)
            data = json.loads((ROOT / "examples/animation/torch_sweep.sequence.example.json").read_text(encoding="utf-8"))
            data["method"] = "static-image-pulse"
            path = temp_dir / "bad.json"; path.write_text(json.dumps(data), encoding="utf-8")
            result = self.server.execute("ags_validate_animation_sequence", {"manifest_path":path.relative_to(ROOT).as_posix()})
            self.assertFalse(result["valid"])

    def test_inventory_refuses_json_output_that_would_overwrite_source_blend(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            path = Path(tmp) / "source.blend"
            path.write_bytes(b"source-preservation-test")
            rel = path.relative_to(ROOT).as_posix()
            with self.assertRaises(mod.CreativeMCPError) as err:
                self.server.execute("ags_blender_scene_inventory", {"blend_path": rel, "output_path": rel, "overwrite": True})
            self.assertEqual(err.exception.code, "input_output_collision")
            self.assertEqual(path.read_bytes(), b"source-preservation-test")

    def test_bounded_timeout_has_stage_command_and_output_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            output_dir = workspace / "review-frames"
            output_dir.mkdir()
            partial = output_dir / "frame.png"
            partial.write_bytes(b"partial image")
            server = mod.CreativeMCPServer(workspace)
            timeout_error = subprocess.TimeoutExpired(
                cmd=["blender.exe", "--background"], timeout=3,
                output=b"partial stdout", stderr=b"partial stderr",
            )
            with mock.patch.object(mod.subprocess, "run", side_effect=timeout_error):
                with self.assertRaises(mod.CreativeMCPError) as caught:
                    server.run_bounded(
                        ["C:/Program Files/Blender/blender.exe", str(partial)], 3,
                        output_dirs=[output_dir], stage="blender_render_action_review",
                    )
            error = caught.exception
            self.assertEqual(error.code, "process_timeout")
            details = error.details
            self.assertEqual(details["stage"], "blender_render_action_review")
            self.assertTrue(details["timed_out"])
            self.assertEqual(details["timeout_seconds"], 3)
            self.assertIsNone(details["exit_code"])
            self.assertGreaterEqual(details["elapsed_seconds"], 0)
            self.assertTrue(details["started_at"])
            self.assertTrue(details["finished_at"])
            self.assertTrue(details["outputs_created"])
            self.assertEqual(details["outputs"][0]["sha256"], __import__("hashlib").sha256(b"partial image").hexdigest())
            self.assertEqual(details["stdout"], "partial stdout")
            self.assertEqual(details["stderr"], "partial stderr")
            self.assertEqual(details["command"][0], "<executable>/blender.exe")
            self.assertNotIn(str(workspace), json.dumps(details))
            self.assertFalse(any("--python" in arg or "review-frames" in arg for arg in details["command"]),
                             "sanitized diagnostics must redact execution arguments and workspace paths")
            self.assertTrue(partial.is_file(), "timeout diagnostics must preserve partial outputs")

    def test_successful_bounded_process_reports_stage_timing_and_exit(self):
        server = mod.CreativeMCPServer(ROOT)
        completed = subprocess.CompletedProcess(args=["fixture"], returncode=0, stdout="done", stderr="")
        with mock.patch.object(mod.subprocess, "run", return_value=completed):
            result = server.run_bounded(["C:/Blender/blender.exe", "--background"], 5, stage="blender_inventory")
        self.assertEqual(result["stage"], "blender_inventory")
        self.assertEqual(result["exit_code"], 0)
        self.assertFalse(result["timed_out"])
        self.assertTrue(result["started_at"])
        self.assertTrue(result["finished_at"])
        self.assertGreaterEqual(result["elapsed_seconds"], 0)
        self.assertEqual(result["stdout"], "done")

    def test_blender_call_fails_clearly_when_binary_missing(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            path = Path(tmp) / "source.blend"; path.write_bytes(b"not a real blend; should not be opened without Blender")
            old = __import__("os").environ.get("BLENDER_BIN")
            __import__("os").environ.pop("BLENDER_BIN", None)
            try:
                with self.assertRaises(mod.CreativeMCPError) as err:
                    self.server.execute("ags_blender_scene_inventory", {"blend_path":path.relative_to(ROOT).as_posix(),"output_path":"evidence/test_scene.json"})
                self.assertEqual(err.exception.code, "blender_not_found")
            finally:
                if old is not None: __import__("os").environ["BLENDER_BIN"] = old

if __name__ == "__main__":
    unittest.main()
