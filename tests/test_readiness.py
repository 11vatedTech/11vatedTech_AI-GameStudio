from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from vated_studio import readiness

ROOT = Path(__file__).resolve().parents[1]


def passing_preflight() -> dict:
    return {
        "generated_at_unix": 1_800_000_000.0,
        "executables": {
            "godot": {"available": True, "path": "C:/tools/godot.exe", "configured_by": "GODOT_BIN"},
            "blender": {"available": True, "path": "C:/tools/blender.exe", "configured_by": "BLENDER_BIN"},
        },
        "loopback_services": {
            "comfyui": {"status": "responding", "endpoint": "http://127.0.0.1:8188/system_stats", "http_status": 200},
            "sd_webui": {"status": "not_responding", "endpoint": "http://127.0.0.1:7860/"},
        },
        "resources": {
            "memory": {"status": "measured", "available_bytes": 8 * 1024**3},
            "gpu": {"status": "measured", "gpus": [{"free_mib": 8192}]},
            "disk": {"status": "measured", "free_bytes": 20 * 1024**3},
            "generation_policy": {"status": "preflight-headroom-observed"},
        },
    }


def patch_report_dependencies(monkeypatch, workspace: Path, *, quality_status: str = "BLOCKED") -> None:
    preflight = passing_preflight()
    for name in ("godot", "blender"):
        binary = workspace / f"{name}.exe"
        binary.write_bytes(b"test fixture")
        preflight["executables"][name]["path"] = str(binary)
    monkeypatch.setattr(readiness, "_run_preflight", lambda root: (preflight, None))
    monkeypatch.setattr(readiness, "_version_probe", lambda binary: {"status": "PASS", "path": str(binary), "version": "fixture"})
    monkeypatch.setattr(readiness, "_probe_mcp", lambda root: {"status": "PASS", "evidence": ["protocol fixture"]})
    monkeypatch.setattr(readiness, "_host_blender_path", lambda root: (None, "host configuration unavailable"))
    monkeypatch.setattr(readiness, "_pipeline", lambda root: {"status": "PASS", "stages": {}})
    monkeypatch.setattr(readiness, "_repository", lambda root: {"status": "PASS", "git": {"status": "PASS"}, "evidence_manifest": {"status": "PASS"}, "test_results": {"status": "NOT_RUN"}})
    monkeypatch.setattr(readiness, "_collect_manifests", lambda root: {"status": "PASS", "manifests": [], "evidence": []})


def test_quality_gate_missing_approval_prevents_ready(monkeypatch, tmp_path):
    patch_report_dependencies(monkeypatch, tmp_path)
    report = readiness.build_readiness_report(tmp_path)
    assert report["checks"]["mcp_connector"]["status"] == "PASS"
    assert report["checks"]["environment"]["optional_services"]["sd_webui"]["required"] is False
    assert report["checks"]["quality_approval"]["human_approval"]["status"] == "BLOCKED"
    assert report["overall_status"] == "BLOCKED"
    assert "READY" not in report
    assert report["checks"]["production_pipeline"]["status"] == "PASS"


def test_resource_blocker_flows_to_overall_status(monkeypatch, tmp_path):
    preflight = passing_preflight()
    preflight["resources"]["generation_policy"] = {"status": "pause-heavy-generation", "reasons": ["RAM safety floor"]}
    monkeypatch.setattr(readiness, "_run_preflight", lambda root: (preflight, None))
    for name in ("godot", "blender"):
        (tmp_path / f"{name}.exe").write_bytes(b"test fixture")
        preflight["executables"][name]["path"] = str(tmp_path / f"{name}.exe")
    monkeypatch.setattr(readiness, "_version_probe", lambda binary: {"status": "PASS", "version": "fixture"})
    monkeypatch.setattr(readiness, "_host_blender_path", lambda root: (None, "host configuration unavailable"))
    monkeypatch.setattr(readiness, "_probe_mcp", lambda root: {"status": "PASS"})
    monkeypatch.setattr(readiness, "_pipeline", lambda root: {"status": "PASS", "stages": {}})
    monkeypatch.setattr(readiness, "_repository", lambda root: {"status": "PASS"})
    report = readiness.build_readiness_report(tmp_path)
    assert report["checks"]["resource_policy"]["status"] == "BLOCKED"
    assert report["overall_status"] == "BLOCKED"


def test_optional_integrations_do_not_fail_environment_gate(monkeypatch, tmp_path):
    patch_report_dependencies(monkeypatch, tmp_path)
    report = readiness.build_readiness_report(tmp_path)
    env = report["checks"]["environment"]
    assert env["status"] == "PASS"
    assert env["optional_services"]["sd_webui"]["status"] == "BLOCKED"
    assert env["optional_services"]["sd_webui"]["required"] is False


def test_text_output_is_concise_and_labels_each_gate():
    text = readiness.format_readiness_summary({
        "overall_status": "PARTIAL",
        "generated_at": "2026-10-20T12:00:00+00:00",
        "checks": {key: {"status": "PASS"} for key in (
            "mcp_connector", "environment", "resource_policy", "production_pipeline", "quality_approval", "repository_integrity"
        )},
    })
    assert "AGS readiness: PARTIAL" in text
    for label in ("MCP connector", "Environment", "Resource policy", "Production pipeline", "Quality approval", "Repository integrity"):
        assert f"{label}: PASS" in text
    assert "no generation, rendering" in text


def test_pipeline_artifact_hash_is_collected_without_writes(tmp_path):
    artifact = tmp_path / "evidence.bin"
    original = b"verified artifact contents"
    artifact.write_bytes(original)
    record = readiness._artifact(tmp_path, "evidence.bin")
    assert record["status"] == "PASS"
    assert record["sha256"] == hashlib.sha256(original).hexdigest()
    assert artifact.read_bytes() == original


def test_repository_manifest_integrity_reports_missing_and_changed_inputs(tmp_path, monkeypatch):
    monkeypatch.setattr(readiness.subprocess, "run", lambda *args, **kwargs: type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    state = tmp_path / ".state" / "creative-mcp-smoke"
    state.mkdir(parents=True)
    good = tmp_path / "good.bin"
    good.write_bytes(b"good")
    manifest = {
        "generated_at": "2026-10-20",
        "evidence": [
            {"path": "good.bin", "sha256": hashlib.sha256(b"good").hexdigest()},
            {"path": "changed.bin", "sha256": hashlib.sha256(b"old").hexdigest()},
            {"path": "missing.bin", "sha256": hashlib.sha256(b"missing").hexdigest()},
        ],
    }
    (state / "evidence-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "changed.bin").write_bytes(b"new")
    report = readiness._repository(tmp_path)
    assert report["evidence_manifest"]["status"] == "PARTIAL"
    assert report["evidence_manifest"]["missing"] == ["missing.bin"]
    assert report["evidence_manifest"]["mismatched"] == [{"path": "changed.bin", "reason": "sha256 differs from recorded evidence"}]


def test_live_local_mcp_probe_negotiates_and_lists_tools():
    result = readiness._probe_mcp(ROOT)
    assert result["status"] == "PASS"
    assert result["protocol_version"] == "2025-06-18"
    assert result["discovered_tools"]
    assert result["structured_unknown_tool_error"] == "unknown_tool"


def test_cli_json_interface_is_machine_readable_and_read_only(tmp_path):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "vated_studio.cli", "--workspace", str(tmp_path), "readiness", "--json"],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=15, check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["read_only"] is True
    assert report["overall_status"] == "BLOCKED"
    assert report["checks"]["mcp_connector"]["status"] == "BLOCKED"
    assert report["safety"]["generation_or_rendering_run"] is False
    assert list(tmp_path.iterdir()) == []


def test_cli_default_interface_is_concise_text(tmp_path):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "vated_studio.cli", "--workspace", str(tmp_path), "readiness"],
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=15, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("AGS readiness: BLOCKED")
    assert "Quality approval: BLOCKED" in result.stdout
    assert "Repository integrity: NOT_RUN" in result.stdout
    assert len(result.stdout.splitlines()) == 8


def test_readiness_report_declares_no_test_execution_or_artifact_writes(monkeypatch, tmp_path):
    patch_report_dependencies(monkeypatch, tmp_path)
    report = readiness.build_readiness_report(tmp_path)
    assert report["read_only"] is True
    assert report["safety"] == {
        "generation_or_rendering_run": False,
        "evidence_overwritten": False,
        "tests_executed": False,
        "note": "Optional services are reported separately and do not make required local dependencies fail.",
    }
