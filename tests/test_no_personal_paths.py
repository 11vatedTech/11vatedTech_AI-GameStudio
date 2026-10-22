"""Regression: tracked files must not expose the maintainer's personal machine paths.

Stdlib-only. Markers are assembled from fragments so this file does not match itself.
The audit document is allow-listed because it describes the finding in prose.
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".blend", ".wav", ".ogg", ".mp3",
                   ".ttf", ".otf", ".safetensors", ".ckpt", ".zip", ".whl", ".pyc"}
ALLOWED = {"docs/audits/2026-10-22-upgrade-audit.md", "tests/test_no_personal_paths.py"}
MARKERS = [
    re.compile(r"Users[\\/]+" + "11" + "vat" + r"\b"),
    re.compile("AI-GameStudio_by_" + "11vatedTech"),
    re.compile("Comfy-" + "Desktop"),
    re.compile("One" + "Drive"),
]


def tracked_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return [ROOT / line for line in out.splitlines() if line]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]


class NoPersonalPathsTest(unittest.TestCase):
    def test_tracked_text_files_have_no_personal_machine_paths(self) -> None:
        offenders = []
        for path in tracked_files():
            rel = path.relative_to(ROOT).as_posix()
            if path.suffix.lower() in BINARY_SUFFIXES or rel in ALLOWED or not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for marker in MARKERS:
                if marker.search(text):
                    offenders.append(f"{rel}: {marker.pattern}")
                    break
        self.assertEqual(offenders, [], "personal machine paths found; use repo-relative paths")


if __name__ == "__main__":
    unittest.main()
