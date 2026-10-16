from __future__ import annotations

from pathlib import Path
from shutil import which
from typing import Any
import subprocess


class BlenderAdapter:
    def __init__(self, executable: str = "blender", timeout: float = 180):
        self.executable = executable
        self.timeout = timeout

    def locate(self) -> str | None:
        path = Path(self.executable).expanduser()
        return str(path.resolve()) if path.is_file() else which(self.executable)

    def doctor(self) -> dict[str, Any]:
        binary = self.locate()
        if not binary:
            return {"available": False, "executable": self.executable, "reason": "Blender executable not found."}
        try:
            proc = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=min(self.timeout, 10), check=False)
            return {"available": proc.returncode == 0, "executable": binary,
                    "version_line": (proc.stdout or proc.stderr).splitlines()[0] if (proc.stdout or proc.stderr) else "",
                    "returncode": proc.returncode}
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"available": False, "executable": binary, "reason": str(exc)}
