from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import shutil

from .errors import StudioError
from .jsonio import atomic_write_json
from .paths import ensure_inside, slugify


class ProjectFactory:
    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()
        self.projects_root = self.workspace / "projects"
        self.projects_root.mkdir(parents=True, exist_ok=True)

    def create_godot_2d(self, title: str, *, slug: str | None = None) -> dict[str, Any]:
        clean_slug = slugify(slug or title, fallback="new-game")
        target = ensure_inside(self.workspace, Path("projects") / clean_slug)
        if target.exists() and any(target.iterdir()):
            raise StudioError("Project directory already exists and is not empty", code="project_exists", details={"path": str(target)}, http_status=409)
        if target.exists():
            target.rmdir()
        template = Path(__file__).resolve().parent / "templates" / "godot-2d"
        if not template.is_dir():
            raise StudioError("Bundled Godot template is missing", code="template_missing", http_status=500)
        shutil.copytree(template, target)
        project_file = target / "project.godot"
        content = project_file.read_text(encoding="utf-8").replace("__PROJECT_TITLE__", json.dumps(title, ensure_ascii=False))
        project_file.write_text(content, encoding="utf-8")
        metadata = {"schema_version": "1.0", "project_id": clean_slug, "title": title, "engine": "Godot 4", "status": "starter_created_not_a_finished_game"}
        atomic_write_json(target / "studio-project.json", metadata)
        return {"project_path": str(target), "project_id": clean_slug, "title": title,
                "status": "created", "next_steps": ["Replace the sample loop with the scoped game design.", "Create an art bible and asset specs before batch generation.", "Implement one playable loop and verify it before expanding content."]}
