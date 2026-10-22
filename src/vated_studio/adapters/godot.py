from __future__ import annotations

from pathlib import Path
from shutil import which
import os
from typing import Any
import json
import subprocess
import time

from ..errors import StudioError
from ..paths import ensure_inside


class GodotAdapter:
    def __init__(self, executable: str = "godot", timeout: float = 180):
        self.executable = executable
        self.timeout = timeout

    def locate(self) -> str | None:
        candidate = Path(self.executable).expanduser()
        if candidate.is_file():
            return str(candidate.resolve())
        resolved = which(self.executable)
        if resolved:
            return resolved
        # Match preflight's PATH candidate order even when a configured alias
        # (or configured path) is missing.
        for name in ("godot", "godot4", "godot_console.exe"):
            if name == self.executable:
                continue
            resolved = which(name)
            if resolved:
                return resolved
        # The Studio's Windows developer layout bundles Godot outside PATH.
        # Keep this fallback deterministic; explicit config and PATH take priority.
        if os.name == "nt":
            bundled = Path.home() / "tools" / "ai-game-studio" / "godot" / "godot_console.exe"
            if bundled.is_file():
                return str(bundled.resolve())
        return None

    def doctor(self) -> dict[str, Any]:
        located = self.locate()
        if not located:
            return {"available": False, "executable": self.executable, "reason": "Godot executable was not found on PATH or at the configured path."}
        try:
            result = subprocess.run([located, "--version"], capture_output=True, text=True, timeout=min(self.timeout, 10), check=False)
            return {"available": result.returncode == 0, "executable": located, "version": (result.stdout or result.stderr).strip(), "returncode": result.returncode}
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"available": False, "executable": located, "reason": str(exc)}

    def validate_project(self, project_path: str | Path, *, run_engine: bool = False) -> dict[str, Any]:
        root = Path(project_path).expanduser().resolve()
        project_file = root / "project.godot"
        errors = []
        if not root.is_dir():
            errors.append("project_directory_missing")
        if not project_file.is_file():
            errors.append("project_godot_missing")
        else:
            data = project_file.read_text(encoding="utf-8", errors="replace")
            if "[application]" not in data:
                errors.append("application_section_missing")
            main_match = None
            for line in data.splitlines():
                stripped = line.strip()
                if stripped.startswith("run/main_scene="):
                    main_match = stripped.split("=", 1)[1].strip().strip('"')
                    break
            if not main_match:
                errors.append("main_scene_not_configured")
            elif not (root / main_match.replace("res://", "")).is_file():
                errors.append("main_scene_file_missing")
        result: dict[str, Any] = {"project": str(root), "static_valid": not errors, "errors": errors, "runtime_validation": "not_run"}
        if run_engine and not errors:
            executable = self.locate()
            if not executable:
                result["runtime_validation"] = "blocked"
                result["blocker"] = "Godot executable unavailable"
                return result
            run = self._run([executable, "--headless", "--path", str(root), "--editor", "--quit"], cwd=root)
            result["runtime_validation"] = "passed" if run["returncode"] == 0 else "failed"
            result["engine_run"] = run
        return result

    def export(self, project_path: str | Path, preset: str, output_path: str | Path) -> dict[str, Any]:
        if not preset or preset.strip() != preset:
            raise StudioError("Export preset is required", code="missing_export_preset")
        root = Path(project_path).expanduser().resolve()
        static = self.validate_project(root)
        if not static["static_valid"]:
            raise StudioError("Godot project failed static validation", code="project_invalid", details=static, http_status=409)
        preset_file = root / "export_presets.cfg"
        if not preset_file.is_file() or f'name="{preset}"' not in preset_file.read_text(encoding="utf-8", errors="replace"):
            raise StudioError("Named export preset was not found in export_presets.cfg", code="export_preset_missing", details={"preset": preset})
        executable = self.locate()
        if not executable:
            raise StudioError("Godot executable is unavailable", code="godot_unavailable", http_status=503)
        out = Path(output_path).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        result = self._run([executable, "--headless", "--path", str(root), "--export-release", preset, str(out)], cwd=root)
        exists = out.is_file() and out.stat().st_size > 0
        return {"project": str(root), "preset": preset, "output": str(out), "returncode": result["returncode"],
                "output_exists": exists, "output_bytes": out.stat().st_size if exists else 0,
                "status": "passed" if result["returncode"] == 0 and exists else "failed", "process": result}

    def _run(self, command: list[str], *, cwd: Path) -> dict[str, Any]:
        start = time.monotonic()
        try:
            process = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=self.timeout, check=False)
            return {"command": command, "cwd": str(cwd), "returncode": process.returncode,
                    "stdout": process.stdout[-12000:], "stderr": process.stderr[-12000:],
                    "duration_seconds": round(time.monotonic()-start, 3), "timed_out": False}
        except subprocess.TimeoutExpired as exc:
            return {"command": command, "cwd": str(cwd), "returncode": None,
                    "stdout": (exc.stdout or b"").decode("utf-8", errors="replace")[-12000:] if isinstance(exc.stdout, bytes) else str(exc.stdout or "")[-12000:],
                    "stderr": (exc.stderr or b"").decode("utf-8", errors="replace")[-12000:] if isinstance(exc.stderr, bytes) else str(exc.stderr or "")[-12000:],
                    "duration_seconds": round(time.monotonic()-start, 3), "timed_out": True}
        except OSError as exc:
            return {"command": command, "cwd": str(cwd), "returncode": None, "stdout": "", "stderr": str(exc),
                    "duration_seconds": round(time.monotonic()-start, 3), "timed_out": False}
