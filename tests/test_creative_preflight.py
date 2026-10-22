import json, unittest
from unittest import mock
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("creative_preflight",ROOT/"tools/preflight/creative_preflight.py")
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class TestCreativePreflight(unittest.TestCase):
 def test_resource_policy_pauses_low_memory(self):
  m={"status":"measured","available_bytes":1024**3,"total_bytes":16*1024**3}
  g={"status":"measured","gpus":[{"free_mib":2000,"total_mib":12000}]}
  p=module.resource_policy(m,g,100*1024**3)
  self.assertEqual(p["status"],"pause-heavy-generation")
 def test_unknown_values_are_not_guessed(self):
  p=module.resource_policy({"status":"unknown","available_bytes":None},{"status":"unknown"},None)
  self.assertEqual(p["status"],"unknown");self.assertIsNone(p["minimum_free_vram_mib_observed"])
 def test_http_probe_refuses_remote_host(self):
  p=module.loopback_http("test","https://example.com")
  self.assertEqual(p["status"],"refused")
 def test_preflight_is_structured_and_read_only(self):
  r=module.run_preflight(ROOT)
  self.assertIn("executables",r);self.assertIn("resources",r);self.assertIn("mcp_host_configuration",r)
  self.assertEqual(r["mcp_host_configuration"]["status"],"not_inspected")
 def test_configured_executable_wins_over_path_fallback(self):
  with mock.patch.dict(module.os.environ, {"PREFLIGHT_TEST_BIN": str(ROOT / "pyproject.toml")}):
   r=module.find_executable("PREFLIGHT_TEST_BIN", ("python",))
  self.assertTrue(r["available"])
  self.assertEqual(r["configured_by"], "PREFLIGHT_TEST_BIN")
 def test_missing_configured_executable_reports_path_fallback_source(self):
  with mock.patch.dict(module.os.environ, {"PREFLIGHT_TEST_BIN": "missing-executable-for-test"}):
   with mock.patch.object(module.shutil, "which", lambda name: "C:/test/python.exe" if name == "python" else None):
    r=module.find_executable("PREFLIGHT_TEST_BIN", ("python",))
  self.assertTrue(r["available"])
  self.assertEqual(r["path"], "C:/test/python.exe")
  self.assertEqual(r["configured_by"], "PATH")
 def test_godot_discovery_includes_bundled_console_name(self):
  env_name, names = module.EXECUTABLES["godot"]
  self.assertEqual(env_name, "GODOT_BIN")
  self.assertIn("godot_console.exe", names)
 def test_bundled_godot_fallback_resolves_only_existing_windows_candidate(self):
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   home=Path(tmp)
   candidate=home/'tools'/'ai-game-studio'/'godot'/'godot_console.exe'
   self.assertIsNone(module.bundled_godot_fallback(home, is_windows=False))
   self.assertIsNone(module.bundled_godot_fallback(home, is_windows=True))
   candidate.parent.mkdir(parents=True)
   candidate.write_bytes(b'test executable placeholder')
   self.assertEqual(module.bundled_godot_fallback(home, is_windows=True), candidate.resolve())
 def test_godot_bundled_fallback_is_reported_when_present(self):
  if module.os.name != "nt": self.skipTest("Windows bundled Godot layout only")
  bundled = module.bundled_godot_fallback(Path.home(), is_windows=True)
  if bundled is None: self.skipTest("Studio-bundled Godot executable unavailable")
  r=module.run_preflight(ROOT)
  self.assertTrue(r["executables"]["godot"]["available"])
  self.assertEqual(r["executables"]["godot"]["path"], str(bundled))
if __name__=="__main__":unittest.main()
