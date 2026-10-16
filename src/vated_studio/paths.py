from __future__ import annotations

import re
from pathlib import Path
from .errors import StudioError


def slugify(value: str, *, fallback: str = "item", limit: int = 72) -> str:
    if not isinstance(value, str):
        raise StudioError("Name must be text", code="invalid_name")
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-_").lower()[:limit].strip("-_")
    return cleaned or fallback


def ensure_inside(root: Path, value: str | Path, *, allow_root: bool = False, resolve: bool = True) -> Path:
    """Resolve a workspace-relative or absolute path and reject traversal/symlink escapes."""
    root_path = root.expanduser().resolve()
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root_path / candidate
    result = candidate.resolve(strict=False) if resolve else candidate.absolute()
    try:
        result.relative_to(root_path)
    except ValueError as exc:
        raise StudioError("Path escapes the configured workspace", code="path_outside_workspace", details={"path": str(value)}, http_status=403) from exc
    if result == root_path and not allow_root:
        raise StudioError("Workspace root is not a valid file target", code="invalid_path")
    return result


def require_file(root: Path, value: str | Path, suffixes: set[str] | None = None) -> Path:
    path = ensure_inside(root, value)
    if not path.is_file():
        raise StudioError("Required file does not exist", code="file_not_found", details={"path": str(path)}, http_status=404)
    if suffixes and path.suffix.lower() not in {s.lower() for s in suffixes}:
        raise StudioError("File type is not allowed", code="invalid_file_type", details={"allowed": sorted(suffixes), "actual": path.suffix})
    return path
