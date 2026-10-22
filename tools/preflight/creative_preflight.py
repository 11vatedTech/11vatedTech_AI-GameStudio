#!/usr/bin/env python3
"""Read-only local tool/resource preflight for the 11vatedTech AI Game Studio.

No installation, service start/stop, process termination, model loading, or generation occurs.
Unknown measurements stay unknown. Service HTTP requests are restricted to loopback.
"""
from __future__ import annotations
import argparse, ctypes, json, os, platform, shutil, socket, subprocess, sys, time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

EXECUTABLES = {
    "blender": ("BLENDER_BIN", ("blender",)),
    # The Studio's bundled Windows layout uses godot_console.exe, which is not
    # normally on PATH. Include it as a final, platform-specific fallback.
    "godot": ("GODOT_BIN", ("godot", "godot4", "godot_console.exe")),
    "krita": ("KRITA_BIN", ("krita", "krita.exe")),
    "audacity": ("AUDACITY_BIN", ("audacity", "audacity.exe")),
    "ffmpeg": ("FFMPEG_BIN", ("ffmpeg",)),
    "ffprobe": ("FFPROBE_BIN", ("ffprobe",)),
    "uvx": ("UVX_BIN", ("uvx",)),
    "node": ("NODE_BIN", ("node",)),
    "git": ("GIT_BIN", ("git",)),
    "python": ("PYTHON_BIN", (sys.executable,)),
}


def find_executable(env_name: str, names: tuple[str, ...]) -> dict[str, Any]:
    configured = os.environ.get(env_name)
    candidates = [(configured, env_name)] if configured else []
    candidates.extend((name, "PATH") for name in names)
    for item, source in candidates:
        if not item:
            continue
        expanded = str(Path(item).expanduser())
        p = Path(expanded)
        found = str(p.resolve()) if p.is_file() else shutil.which(item)
        if found:
            return {"available": True, "path": found, "configured_by": source}
    return {"available": False, "path": None, "configured_by": env_name if configured else None}


def bundled_godot_fallback(home: Path, *, is_windows: bool) -> Path | None:
    """Return the Studio's known local Windows Godot path when it exists."""
    if not is_windows:
        return None
    candidate = home / "tools" / "ai-game-studio" / "godot" / "godot_console.exe"
    return candidate.resolve() if candidate.is_file() else None


def memory_info() -> dict[str, Any]:
    # Prefer psutil when present; otherwise use native OS APIs without installing dependencies.
    try:
        import psutil  # type: ignore
        vm = psutil.virtual_memory()
        return {"status": "measured", "total_bytes": int(vm.total), "available_bytes": int(vm.available), "source": "psutil"}
    except Exception:
        pass
    if os.name == "nt":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        try:
            status = MEMORYSTATUSEX(); status.dwLength = ctypes.sizeof(status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                return {"status": "measured", "total_bytes": int(status.ullTotalPhys),
                        "available_bytes": int(status.ullAvailPhys), "source": "GlobalMemoryStatusEx"}
        except Exception:
            pass
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        try:
            values = {}
            for line in meminfo.read_text().splitlines():
                k, rest = line.split(":", 1); values[k] = int(rest.strip().split()[0]) * 1024
            total = values.get("MemTotal"); available = values.get("MemAvailable")
            if total is not None and available is not None:
                return {"status": "measured", "total_bytes": total, "available_bytes": available, "source": "/proc/meminfo"}
        except Exception:
            pass
    return {"status": "unknown", "total_bytes": None, "available_bytes": None, "source": None}


def gpu_info() -> dict[str, Any]:
    binary = shutil.which("nvidia-smi")
    if not binary:
        return {"status": "unknown", "reason": "nvidia-smi is not on PATH; no GPU values inferred."}
    try:
        proc = subprocess.run([binary, "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu",
                               "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5, check=False)
        if proc.returncode != 0:
            return {"status": "unknown", "reason": (proc.stderr or proc.stdout).strip()[:500], "returncode": proc.returncode}
        gpus = []
        for line in proc.stdout.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 5:
                continue
            try:
                gpus.append({"name": parts[0], "total_mib": int(parts[1]), "used_mib": int(parts[2]),
                             "free_mib": int(parts[3]), "utilization_percent": int(parts[4])})
            except ValueError:
                continue
        return {"status": "measured" if gpus else "unknown", "gpus": gpus,
                "source": "nvidia-smi", "returncode": proc.returncode}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "unknown", "reason": str(exc)}


def loopback_http(name: str, url: str, suffix: str = "") -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        return {"status": "refused", "reason": "preflight only calls loopback endpoints"}
    target = url.rstrip("/") + suffix
    started = time.monotonic()
    try:
        req = Request(target, headers={"User-Agent": "11vatedTech-creative-preflight/1.0"}, method="GET")
        with urlopen(req, timeout=0.8) as response:
            return {"status": "responding", "http_status": int(response.status),
                    "latency_ms": round((time.monotonic()-started)*1000, 1), "endpoint": target}
    except Exception as exc:
        return {"status": "not_responding", "endpoint": target, "reason": str(exc)[:250]}


def tcp_probe(host: str, port: int, timeout: float = 0.35) -> dict[str, Any]:
    started = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"status": "tcp-accepting", "host": host, "port": port,
                    "latency_ms": round((time.monotonic()-started)*1000, 1),
                    "note": "TCP acceptance is not proof of MCP protocol or tool functionality."}
    except OSError as exc:
        return {"status": "not_responding", "host": host, "port": port, "reason": str(exc)[:200]}


def resource_policy(memory: dict[str, Any], gpu: dict[str, Any], disk_free: int | None) -> dict[str, Any]:
    reasons = []
    status = "unknown"
    available_ram = memory.get("available_bytes")
    gpu_rows = gpu.get("gpus", []) if gpu.get("status") == "measured" else []
    free_vram = min((x.get("free_mib", 0) for x in gpu_rows), default=None)
    if available_ram is not None and available_ram < 2 * 1024**3:
        status = "pause-heavy-generation"; reasons.append("Available system RAM is below 2 GiB.")
    elif free_vram is not None and free_vram < 2560:
        status = "pause-heavy-generation"; reasons.append("Free VRAM is below conservative 2.5 GiB threshold.")
    elif (available_ram is not None and available_ram < 4*1024**3) or (free_vram is not None and free_vram < 4096):
        status = "sequential-low-memory-only"; reasons.append("RAM or VRAM is below the conservative 4 GiB headroom target.")
    elif available_ram is not None and free_vram is not None:
        status = "preflight-headroom-observed"; reasons.append("Headroom passes basic thresholds; workflow-specific peak margin is still required.")
    else:
        status = "unknown"; reasons.append("RAM or GPU memory data is unknown; do not infer headroom.")
    if disk_free is not None and disk_free < 5*1024**3:
        status = "pause-heavy-generation"; reasons.append("Workspace filesystem has less than 5 GiB free.")
    return {"status": status, "reasons": reasons, "available_ram_bytes": available_ram,
            "minimum_free_vram_mib_observed": free_vram, "disk_free_bytes": disk_free,
            "policy_note": "Conservative defaults only. Compare against the chosen workflow's measured peak + safety margin. Never kill unrelated processes."}


def run_preflight(workspace: Path | None = None) -> dict[str, Any]:
    workspace = (workspace or Path.cwd()).expanduser().resolve()
    executables = {name: find_executable(env_name, names) for name, (env_name, names) in EXECUTABLES.items()}
    if not executables["godot"]["available"]:
        bundled_godot = bundled_godot_fallback(Path.home(), is_windows=os.name == "nt")
        if bundled_godot is not None:
            executables["godot"] = {
                "available": True,
                "path": str(bundled_godot),
                "configured_by": "studio_bundled_fallback",
            }
    memory = memory_info(); gpu = gpu_info()
    try:
        disk = shutil.disk_usage(workspace); disk_info = {"status":"measured","free_bytes":disk.free,"total_bytes":disk.total,"path":str(workspace)}
        disk_free = int(disk.free)
    except OSError as exc:
        disk_info = {"status":"unknown","reason":str(exc)}; disk_free=None
    endpoints = {
        "comfyui": loopback_http("comfyui", os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188"), "/system_stats"),
        "sd_webui": loopback_http("sd-webui", os.environ.get("SD_WEBUI_URL", "http://127.0.0.1:7860"), "/sdapi/v1/options"),
        "freemocap": loopback_http("freemocap", os.environ.get("FREEMOCAP_URL", "http://127.0.0.1:8005"), "/"),
        "blender_mcp_socket": tcp_probe("127.0.0.1", int(os.environ.get("BLENDER_MCP_PORT", "9876"))),
    }
    return {"schema_version":"1.0","generated_at_unix":time.time(),"host":{"platform":platform.platform(),"python":sys.version.split()[0],"workspace":str(workspace)},
            "executables":executables,"resources":{"memory":memory,"gpu":gpu,"disk":disk_info,
            "generation_policy":resource_policy(memory,gpu,disk_free)},"loopback_services":endpoints,
            "mcp_host_configuration":{"status":"not_inspected","reason":"This read-only script does not guess or read private agent settings. Verify the installed host's documented MCP configuration separately."},
            "disclaimers":["No processes were started/stopped/terminated.","A responding port is not proof of MCP handshake or successful creative output.","Tool and model licenses require separate review."]}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON (default output is also JSON).")
    args=parser.parse_args()
    result=run_preflight(args.workspace)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    policy=result["resources"]["generation_policy"]["status"]
    # Non-zero is not a failure of discovery; it warns the caller not to launch heavy generation.
    return 0 if policy in {"preflight-headroom-observed","sequential-low-memory-only","unknown"} else 2

if __name__ == "__main__":
    raise SystemExit(main())
