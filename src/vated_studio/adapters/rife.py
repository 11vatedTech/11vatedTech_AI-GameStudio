from __future__ import annotations

from pathlib import Path
from shutil import which
from typing import Any
import subprocess
import time

from ..errors import StudioError
from ..jsonio import sha256_file


class RIFEAdapter:
    """Thin RIFE runner. Alpha preservation is checked after execution, never assumed."""
    def __init__(self, executable: str | None = None, timeout: float = 90):
        self.executable = executable or "rife-ncnn-vulkan"
        self.timeout = timeout

    def locate(self) -> str | None:
        path = Path(self.executable).expanduser()
        return str(path.resolve()) if path.is_file() else which(self.executable)

    def doctor(self) -> dict[str, Any]:
        binary = self.locate()
        return {"available": bool(binary), "executable": binary or self.executable,
                "note": "Availability does not establish compatibility with transparent sprite animation."}

    def interpolate_pair(self, frame_a: str | Path, frame_b: str | Path, output: str | Path, *, model: str | None = None) -> dict[str, Any]:
        a, b, out = Path(frame_a).resolve(), Path(frame_b).resolve(), Path(output).resolve()
        for path in (a, b):
            if not path.is_file():
                raise StudioError("RIFE input frame does not exist", code="file_not_found", details={"path": str(path)})
        binary = self.locate()
        if not binary:
            raise StudioError("RIFE executable is unavailable", code="rife_unavailable", http_status=503)
        out.parent.mkdir(parents=True, exist_ok=True)
        command = [binary]
        if model:
            command.extend(["-m", model])
        command.extend(["-0", str(a), "-1", str(b), "-o", str(out)])
        started = time.monotonic()
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=self.timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            raise StudioError("RIFE interpolation timed out", code="rife_timeout", details={"timeout_seconds": self.timeout}) from exc
        except OSError as exc:
            raise StudioError("Could not start RIFE", code="rife_launch_error", details={"reason": str(exc)}) from exc
        present = out.is_file() and out.stat().st_size > 0
        result = {"command": command, "returncode": proc.returncode, "duration_seconds": round(time.monotonic()-started, 3),
                  "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:], "output_exists": present,
                  "output_sha256": sha256_file(out) if present else None, "status": "produced" if proc.returncode == 0 and present else "failed"}
        if result["status"] != "produced":
            raise StudioError("RIFE did not produce a valid output", code="rife_failed", details=result)
        try:
            from PIL import Image
            with Image.open(out) as image:
                rgba = image.convert("RGBA")
                alpha = rgba.getchannel("A")
                result["alpha_unique_values"] = len(set(alpha.getdata()))
                result["alpha_fully_opaque"] = result["alpha_unique_values"] == 1 and alpha.getextrema() == (255, 255)
                result["sprite_alpha_review"] = "reject_or_review" if result["alpha_fully_opaque"] else "alpha_preserved_possible"
        except ImportError:
            result["sprite_alpha_review"] = "not_checked_install_vision_extra"
        return result
