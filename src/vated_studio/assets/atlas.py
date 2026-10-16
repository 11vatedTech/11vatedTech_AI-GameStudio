from __future__ import annotations

from pathlib import Path
from typing import Any
import math

from ..errors import StudioError
from ..jsonio import atomic_write_json, sha256_file
from .images import require_vision

try:
    from PIL import Image
except ImportError:
    Image = None


def pack_atlas(image_paths: list[str | Path], output_path: str | Path, *, max_width: int = 2048, padding: int = 2) -> dict[str, Any]:
    """Deterministic shelf-pack atlas. It refuses oversize inputs rather than silently rescaling them."""
    require_vision()
    if not image_paths or not 64 <= max_width <= 8192 or not 0 <= padding <= 64:
        raise StudioError("Invalid atlas inputs, max_width, or padding", code="invalid_atlas_options")
    items = []
    for value in image_paths:
        path = Path(value)
        if not path.is_file():
            raise StudioError("Atlas input not found", code="file_not_found", details={"path": str(path)})
        with Image.open(path) as opened:
            image = opened.convert("RGBA").copy()
        if image.width + padding * 2 > max_width:
            raise StudioError("Image exceeds atlas width; rescale explicitly before packing", code="atlas_input_too_wide", details={"path": str(path), "width": image.width})
        items.append((path, image))
    items.sort(key=lambda item: (-item[1].height, -item[1].width, item[0].name.lower()))
    x, y, row_h, used_w = padding, padding, 0, 0
    placements = []
    for path, image in items:
        padded_w, padded_h = image.width + padding * 2, image.height + padding * 2
        if x + padded_w > max_width and x > padding:
            y += row_h
            x, row_h = padding, 0
        placements.append((path, image, x + padding, y + padding))
        x += padded_w
        row_h = max(row_h, padded_h)
        used_w = max(used_w, x)
    height = y + row_h + padding
    width = max(1, min(max_width, used_w))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    atlas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    manifest_items = {}
    for path, image, px, py in placements:
        atlas.alpha_composite(image, (px, py))
        manifest_items[path.name] = {"x": px, "y": py, "width": image.width, "height": image.height,
                                     "sha256": sha256_file(path), "source": str(path)}
    atlas.save(target, optimize=True)
    manifest_path = target.with_suffix(".json")
    manifest = {"schema_version": "1.0", "atlas": target.name, "atlas_sha256": sha256_file(target),
                "size": [width, height], "padding": padding, "items": manifest_items,
                "status": "packed_requires_engine_import_check"}
    atomic_write_json(manifest_path, manifest)
    return {"atlas": str(target), "manifest": str(manifest_path), "size": [width, height], "items": len(items)}
