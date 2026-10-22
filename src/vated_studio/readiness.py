from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import ntpath
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any


STATUSES = {"BLOCKED", "PARTIAL", "PASS", "NOT_RUN"}


def _digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _run_preflight(root: Path) -> tuple[dict[str, Any] | None, str | None]:
    script = root / "tools" / "preflight" / "creative_preflight.py"
    if not script.is_file():
        return None, "Read-only creative preflight script is missing."
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--workspace", str(root), "--json"],
            cwd=root, capture_output=True, text=True, timeout=30, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"Preflight could not complete: {exc}"
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None, f"Preflight returned invalid JSON (exit {result.returncode})."
    return payload, None


def _host_blender_path(root: Path) -> tuple[Path | None, str]:
    """Read only the known local MCP's Blender override; never execute host config."""
    config = root / ".agents" / "mcp.json"
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
        raw = data["mcpServers"]["11vatedtech-creative-tools"]["env"]["BLENDER_BIN"]
        candidate = Path(raw).expanduser()
        return (candidate.resolve(), ".agents/mcp.json") if candidate.is_file() else (None, ".agents/mcp.json path unavailable")
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        return None, "host configuration unavailable"


def _version_probe(binary: Path, timeout: float = 10) -> dict[str, Any]:
    try:
        result = subprocess.run([str(binary), "--version"], capture_output=True, text=True,
                                timeout=timeout, check=False, shell=False,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        output = (result.stdout or result.stderr).strip().splitlines()
        return {"status": "PASS" if result.returncode == 0 else "BLOCKED",
                "path": str(binary), "version": output[0] if output else None,
                "returncode": result.returncode}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "BLOCKED", "path": str(binary), "reason": str(exc)}


def _probe_mcp(root: Path) -> dict[str, Any]:
    server = root / "tools" / "creative_mcp_server.py"
    if not server.is_file():
        return {"status": "BLOCKED", "reason": "Creative MCP server script is missing.", "evidence": []}
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "ags_readiness_unknown_probe", "arguments": {}}},
    ]
    try:
        result = subprocess.run(
            [sys.executable, str(server)], input="\n".join(json.dumps(item) for item in requests) + "\n",
            cwd=root, capture_output=True, text=True, timeout=15, check=False, shell=False,
            env={**os.environ, "AGS_WORKSPACE": str(root), "PYTHONDONTWRITEBYTECODE": "1"},
        )
        responses = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        if len(responses) != len(requests):
            raise ValueError(f"Expected {len(requests)} MCP responses, received {len(responses)}.")

        initialized = responses[0]["result"] if len(responses) > 0 else {}
        tools = responses[1]["result"]["tools"] if len(responses) > 1 else []
        error = responses[2]["result"] if len(responses) > 2 else {}
        structured = error.get("structuredContent", {})
        valid = (result.returncode == 0 and initialized.get("protocolVersion") == "2025-06-18"
                 and initialized.get("serverInfo", {}).get("name") == "11vatedtech-creative-tools"
                 and len(tools) > 0 and error.get("isError") is True
                 and structured.get("code") == "unknown_tool")
        return {"status": "PASS" if valid else "BLOCKED",
                "protocol_version": initialized.get("protocolVersion"),
                "server_name": initialized.get("serverInfo", {}).get("name"),
                "discovered_tools": [tool.get("name") for tool in tools if isinstance(tool, dict)],
                "structured_unknown_tool_error": structured.get("code"),
                "process_returncode": result.returncode,
                "evidence": ["initialize", "tools/list", "unknown-tool structured error"] if valid else [],
                **({} if valid else {"reason": "MCP protocol, discovery, or structured error probe failed."})}
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return {"status": "BLOCKED", "reason": f"MCP stdio probe failed: {exc}", "evidence": []}


def _collect_manifests(root: Path) -> dict[str, Any]:
    validator_path = root / "tools" / "animation" / "validate_sequence.py"
    if not validator_path.is_file():
        return {"status": "BLOCKED", "manifests": [], "reason": "Animation manifest validator is missing."}
    records = []
    for manifest_path in sorted((root / "builds" / "anim").glob("*_animation.json")):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            result = subprocess.run(
                [sys.executable, str(validator_path), str(manifest_path), "--check-files"],
                cwd=root, capture_output=True, text=True, timeout=10, check=False, shell=False,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            validation = json.loads(result.stdout)
            frame_checks = []
            for frame in data.get("source_frames", []):
                raw_path = Path(frame.get("path", ""))
                frame_path = raw_path.resolve() if raw_path.is_absolute() else (manifest_path.parent / raw_path).resolve()
                if not _inside(root, frame_path):
                    frame_checks.append({"path": str(frame.get("path", "")), "status": "BLOCKED", "reason": "Source path escapes workspace."})
                elif not frame_path.is_file():
                    frame_checks.append({"path": str(frame_path.relative_to(root)), "status": "BLOCKED", "reason": "Source frame missing."})
                else:
                    actual = _digest(frame_path)
                    frame_checks.append({"path": str(frame_path.relative_to(root)), "status": "PASS" if actual == frame.get("sha256") else "BLOCKED",
                                         "sha256": actual, "expected_sha256": frame.get("sha256")})
            valid = result.returncode == 0 and validation.get("valid") and all(item["status"] == "PASS" for item in frame_checks)
            records.append({"path": manifest_path.relative_to(root).as_posix(),
                            "status": "PASS" if valid else "BLOCKED",
                            "structural_status": validation.get("status"),
                            "review_status": validation.get("review_status"),
                            "frame_count": data.get("frame_count"),
                            "source_frames_verified": sum(item["status"] == "PASS" for item in frame_checks),
                            "source_frames": frame_checks,
                            "errors": validation.get("errors", [])})
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            records.append({"path": manifest_path.relative_to(root).as_posix(), "status": "BLOCKED", "reason": str(exc)})
    status = "PASS" if records and all(record["status"] == "PASS" for record in records) else "NOT_RUN" if not records else "BLOCKED"
    return {"status": status, "manifests": records,
            "evidence": [record["path"] for record in records]}


def _artifact(root: Path, relative: str) -> dict[str, Any]:
    path = (root / relative).resolve()
    if not _inside(root, path) or not path.is_file():
        return {"path": relative, "status": "BLOCKED", "reason": "Missing or outside workspace."}
    return {"path": relative, "status": "PASS", "bytes": path.stat().st_size, "sha256": _digest(path)}


def _pipeline(root: Path) -> dict[str, Any]:
    artifacts = [_artifact(root, path) for path in (
        ".state/creative-mcp-smoke/vertical-slice/source_rig.blend",
        ".state/creative-mcp-smoke/vertical-slice/torch_sweep_candidate.blend",
        ".state/creative-mcp-smoke/vertical-slice/torch_sweep_candidate.glb",
        "projects/prismatic-creature-battler/artifacts/torch_sweep_candidate.glb",
        "projects/prismatic-creature-battler/artifacts/torch_sweep_candidate.glb.import",
    )]
    source, candidate, export, imported, import_sidecar = artifacts
    same_glb = export.get("sha256") == imported.get("sha256") and export["status"] == imported["status"] == "PASS"
    vertical = root / ".state" / "creative-mcp-smoke" / "vertical-slice"
    try:
        audit = json.loads((vertical / "action-audit.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        audit = {}
    render_dir = vertical / "render-frames"
    render_frames = sorted(path for path in render_dir.glob("*.png") if path.is_file()) if render_dir.is_dir() else []
    import_log = vertical / "godot-import-review.log"
    runtime_log = vertical / "godot-action-runtime.log"
    export_log = vertical / "gltf-export.log"
    import_text = import_log.read_text(encoding="utf-8", errors="replace") if import_log.is_file() else ""
    runtime_text = runtime_log.read_text(encoding="utf-8", errors="replace") if runtime_log.is_file() else ""
    export_text = export_log.read_text(encoding="utf-8", errors="replace") if export_log.is_file() else ""
    import_ok = "torch_sweep_candidate.glb" in import_text and "[ DONE ]" in import_text
    runtime_ok = "ACTION_RUNTIME_PLAYING" in runtime_text and audit.get("action") in runtime_text
    export_ok = "GLTF_EXPORTED" in export_text
    manifest_check = _collect_manifests(root)
    stages = {
        "blender_action": {"status": "PASS" if audit.get("fcurve_count", 0) > 0 and audit.get("keyframe_count", 0) > 0 else "BLOCKED",
                           "action": audit.get("action"), "fcurves": audit.get("fcurve_count"), "keyframes": audit.get("keyframe_count"),
                           "evidence": [".state/creative-mcp-smoke/vertical-slice/action-audit.json"] if audit else []},
        "glb_export": {"status": "PASS" if export_ok and candidate["status"] == "PASS" and export["status"] == "PASS" else "BLOCKED",
                       "source_sha256": candidate.get("sha256"), "glb_sha256": export.get("sha256"), "evidence": [".state/creative-mcp-smoke/vertical-slice/gltf-export.log"]},
        "godot_import": {"status": "PASS" if import_ok and same_glb and import_sidecar["status"] == "PASS" else "BLOCKED",
                         "same_glb_hash_in_project": same_glb, "evidence": [".state/creative-mcp-smoke/vertical-slice/godot-import-review.log", import_sidecar["path"]]},
        "godot_runtime": {"status": "PASS" if runtime_ok and same_glb else "BLOCKED",
                          "playback_marker_observed": runtime_ok, "evidence": [".state/creative-mcp-smoke/vertical-slice/godot-action-runtime.log"]},
        "rendered_evidence": {"status": "PASS" if render_frames else "NOT_RUN", "frame_count": len(render_frames),
                              "frames": [{"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
                                          "sha256": _digest(path)} for path in render_frames],
                              "evidence": [path.relative_to(root).as_posix() for path in render_frames[:12]]},
        "animation_manifests": manifest_check,
    }
    required = ("blender_action", "glb_export", "godot_import", "godot_runtime", "animation_manifests")
    status = "PASS" if all(stages[key]["status"] == "PASS" for key in required) else "PARTIAL"
    return {"status": status, "stages": stages, "artifacts": artifacts,
            "note": "Pipeline evidence demonstrates a technical mannequin workflow; it is not finished game art or gameplay-contact verification."}


def _repository(root: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(["git", "-C", str(root), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                                capture_output=True, text=False, timeout=10, check=False, shell=False)
        if result.returncode == 0:
            changed = []
            entries = result.stdout.split(bytes([0])) if isinstance(result.stdout, bytes) else result.stdout.split(chr(0))
            index = 0
            while index < len(entries):
                entry = entries[index]
                index += 1
                if not entry:
                    continue
                if isinstance(entry, bytes):
                    status = os.fsdecode(entry[:2])
                    path = os.fsdecode(entry[3:])
                else:
                    status = entry[:2]
                    path = entry[3:]
                if path.startswith('"'):
                    try:
                        decoded_path = json.loads(path)
                    except json.JSONDecodeError:
                        decoded_path = path
                    path = decoded_path
                path = path.replace("\\\\", "/")
                rename_or_copy = status.startswith(("R", "C"))
                if rename_or_copy:
                    if index < len(entries) and entries[index]:
                        # Rename records include the source path after destination.
                        index += 1
                changed.append({"state": status, "path": path})
            git_status = "PASS" if not changed else "PARTIAL"
            git_result: dict[str, Any] = {"status": git_status, "changed_file_count": len(changed), "changed_files": changed}
        else:
            git_stderr = result.stderr if isinstance(result.stderr, bytes) else str(result.stderr).encode()
            if b"not a git repository" in git_stderr.lower():
                git_result = {"status": "NOT_RUN", "reason": "Workspace is not inside a Git working tree."}
            else:
                git_result = {"status": "BLOCKED", "reason": "git status failed."}
    except (OSError, subprocess.TimeoutExpired) as exc:
        git_result = {"status": "BLOCKED", "reason": f"git status unavailable: {exc}"}

    tests = {"status": "NOT_RUN", "command": "python -m pytest", "reason": "Readiness is read-only and does not execute or reuse stale test results."}
    manifest_path = root / ".state" / "creative-mcp-smoke" / "evidence-manifest.json"
    integrity: dict[str, Any] = {"status": "NOT_RUN", "evidence": []}
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            mismatches = []
            missing = []
            for entry in manifest.get("evidence", []):
                if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                    mismatches.append({"path": None, "reason": "invalid evidence entry"})
                    continue
                relative = entry["path"]
                raw = Path(relative)
                path = (raw.resolve() if raw.is_absolute() else (root / raw).resolve())
                if not _inside(root, path):
                    mismatches.append({"path": relative, "reason": "outside workspace"})
                elif not path.is_file():
                    missing.append(relative)
                elif not isinstance(entry.get("sha256"), str) or _digest(path) != entry["sha256"]:
                    mismatches.append({"path": relative, "reason": "sha256 differs from recorded evidence"})
            integrity = {"status": "PASS" if not missing and not mismatches else "PARTIAL",
                         "captured_at": manifest.get("generated_at"), "entry_count": len(manifest.get("evidence", [])),
                         "missing": missing, "mismatched": mismatches,
                         "evidence": [manifest_path.relative_to(root).as_posix()]}
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            integrity = {"status": "BLOCKED", "reason": f"Evidence manifest unreadable: {exc}", "evidence": [".state/creative-mcp-smoke/evidence-manifest.json"]}
    status = ("BLOCKED" if git_result["status"] == "BLOCKED" or integrity["status"] == "BLOCKED"
              else "PARTIAL" if git_result["status"] == "PARTIAL" or integrity["status"] == "PARTIAL"
              else "PASS" if git_result["status"] == "PASS" and integrity["status"] == "PASS"
              else "NOT_RUN")
    return {"status": status, "git": git_result, "evidence_manifest": integrity, "test_results": tests}


def build_readiness_report(workspace: str | Path) -> dict[str, Any]:
    """Collect current read-only evidence; this function never repairs or writes artifacts."""
    root = Path(workspace).expanduser().resolve()
    preflight, preflight_error = _run_preflight(root)
    executable_data = preflight.get("executables", {}) if preflight else {}
    godot_row = executable_data.get("godot", {})
    blender_row = executable_data.get("blender", {})
    configured_blender, blender_config_source = _host_blender_path(root)
    tools: dict[str, Any] = {}
    for name, row in (("godot", godot_row), ("blender", blender_row)):
        binary = Path(str(row.get("path"))).expanduser() if row.get("available") and row.get("path") else None
        tools[name] = _version_probe(binary) if binary and binary.is_file() else {"status": "BLOCKED", "reason": "Executable not found."}
        if row.get("configured_by"):
            tools[name]["configured_by"] = row["configured_by"]
    host_blender = (_version_probe(configured_blender) if configured_blender else
                    {"status": "BLOCKED", "reason": "No usable Blender override in .agents/mcp.json."})
    if blender_config_source:
        host_blender["configured_by"] = blender_config_source
    services = (preflight or {}).get("loopback_services", {})
    comfy = services.get("comfyui", {})
    optional_services = {name: {"status": "PASS" if data.get("status") == "responding" else "BLOCKED",
                                "required": False, "available": data.get("status") == "responding",
                                "endpoint": data.get("endpoint"), "reason": data.get("reason")}
                        for name, data in services.items() if name != "comfyui"}
    blender_path_usable = tools["blender"]["status"] == "PASS" or host_blender["status"] == "PASS"
    env_pass = tools["godot"]["status"] == "PASS" and tools["blender"]["status"] == "PASS" and comfy.get("status") == "responding"
    environment_status = ("BLOCKED" if tools["godot"]["status"] != "PASS" or not blender_path_usable
                          else "PARTIAL" if not tools["blender"]["status"] == "PASS" or not env_pass
                          else "PASS")
    standalone_blender_available = tools["blender"]["status"] == "PASS"
    environment = {"status": environment_status,
                   "reason": "Standalone preflight cannot resolve Blender; the configured MCP host path is version-verified." if not standalone_blender_available and host_blender["status"] == "PASS" else "Required local tool or service is not available." if environment_status == "BLOCKED" else "Optional local generation service is unavailable." if environment_status == "PARTIAL" else None,
                   "standalone_preflight": {"blender_available": standalone_blender_available,
                                            "reason": None if standalone_blender_available else "Standalone preflight cannot resolve Blender without BLENDER_BIN; host MCP config does provide a usable override." if host_blender["status"] == "PASS" else "Blender unavailable in standalone and MCP host environments."},
                   "executables": tools,
                   "mcp_host_environment": {"blender": host_blender,
                                            "note": "This host override is reported separately; it does not change the standalone preflight result."},
                   "comfyui": {"status": "PASS" if comfy.get("status") == "responding" else "BLOCKED",
                               "required_for": "local image generation", "endpoint": comfy.get("endpoint"),
                               "http_status": comfy.get("http_status"), "latency_ms": comfy.get("latency_ms"),
                               "reason": comfy.get("reason")},
                   "optional_services": optional_services,
                   "preflight_error": preflight_error,
                   "evidence": ["tools/preflight/creative_preflight.py", "ags readiness executable version probes"]}
    resources = (preflight or {}).get("resources", {})
    policy = resources.get("generation_policy", {})
    policy_status = policy.get("status")
    resource_status = "BLOCKED" if policy_status == "pause-heavy-generation" else "PASS" if policy_status == "preflight-headroom-observed" else "PARTIAL"
    resource_check = {"status": resource_status, "measured_at_unix": (preflight or {}).get("generated_at_unix"),
                      "memory": resources.get("memory"), "gpu": resources.get("gpu"), "disk": resources.get("disk"),
                      "generation_policy": policy,
                      "evidence": ["tools/preflight/creative_preflight.py"] if preflight else []}
    mcp = _probe_mcp(root)
    host_config = root / ".agents" / "mcp.json"
    if host_config.is_file():
        try:
            host_data = json.loads(host_config.read_text(encoding="utf-8"))
            server_config = host_data.get("mcpServers", {}).get("11vatedtech-creative-tools", {})
            args = server_config.get("args", [])
            configured_command = str(server_config.get("command", ""))
            command_exists = Path(configured_command).is_file() if configured_command else False
            registered = (server_config.get("type") == "stdio" and command_exists
                          and isinstance(args, list) and any(ntpath.basename(str(item)).lower() == "creative_mcp_server.py" for item in args)
                          and os.path.normcase(os.path.normpath(str(server_config.get("cwd", ""))))
                          == os.path.normcase(os.path.normpath(str(root))))
            mcp["host_config"] = {"status": "PASS" if registered else "PARTIAL", "path": ".agents/mcp.json",
                                  "server_registered": registered}
        except (OSError, TypeError, json.JSONDecodeError):
            mcp["host_config"] = {"status": "BLOCKED", "path": ".agents/mcp.json", "server_registered": False,
                                  "reason": "MCP host configuration is invalid JSON or unreadable."}
    else:
        mcp["host_config"] = {"status": "NOT_RUN", "path": ".agents/mcp.json", "server_registered": False}
    pipeline = _pipeline(root)
    animation_manifests = pipeline.get("stages", {}).get("animation_manifests", {"status": "NOT_RUN", "evidence": []})
    rendered_evidence = pipeline.get("stages", {}).get("rendered_evidence", {"status": "NOT_RUN", "frame_count": 0, "evidence": []})
    quality = {"status": "BLOCKED", "required": True,
               "structural_validation": {"status": animation_manifests.get("status", "NOT_RUN"),
                                         "evidence": animation_manifests.get("evidence", [])},
               "rendered_evidence": rendered_evidence,
               "human_review": {"status": "NOT_RUN", "reason": "Existing artifacts contain no recorded human playback/art review decision."},
               "human_approval": {"status": "BLOCKED", "reason": "No verified human approval reference is recorded; approval cannot be inferred from structural or runtime evidence."},
               "evidence": [".state/creative-mcp-smoke/vertical-slice/action-audit.json", "evidence/prismatic-creature-battler/release-qa.json"]}
    repository = _repository(root)
    checks = {"mcp_connector": mcp, "environment": environment, "resource_policy": resource_check,
              "production_pipeline": pipeline, "quality_approval": quality, "repository_integrity": repository}
    required_statuses = [check.get("status", "NOT_RUN") for check in checks.values()]
    overall = "BLOCKED" if "BLOCKED" in required_statuses else "PARTIAL" if any(status != "PASS" for status in required_statuses) else "PASS"
    overall = "BLOCKED" if quality["human_approval"]["status"] != "PASS" else overall
    return {"schema_version": "1.0", "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "workspace": str(root), "read_only": True, "overall_status": overall, "checks": checks,
            "safety": {"generation_or_rendering_run": False, "evidence_overwritten": False,
                       "tests_executed": False, "note": "Optional services are reported separately and do not make required local dependencies fail."}}


def format_readiness_summary(report: dict[str, Any]) -> str:
    checks = report.get("checks", {})
    labels = (("mcp_connector", "MCP connector"), ("environment", "Environment"),
              ("resource_policy", "Resource policy"), ("production_pipeline", "Production pipeline"),
              ("quality_approval", "Quality approval"), ("repository_integrity", "Repository integrity"))
    lines = [f"AGS readiness: {report.get('overall_status', 'NOT_RUN')}  |  {report.get('generated_at', 'timestamp unavailable')}"]
    for key, label in labels:
        check = checks.get(key, {})
        lines.append(f"{label}: {check.get('status', 'NOT_RUN')}")
    lines.append("Read-only: no generation, rendering, artifact repair, or test execution.")
    return "\n".join(lines)
