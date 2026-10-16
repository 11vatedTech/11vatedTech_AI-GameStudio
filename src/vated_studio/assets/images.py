from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any
import hashlib
import math

from ..errors import StudioError
from ..jsonio import sha256_file

try:
    import numpy as np
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat, ImageDraw
except ImportError:  # imports stay optional for schema/planning-only use
    np = None
    Image = ImageEnhance = ImageFilter = ImageOps = ImageStat = ImageDraw = None


def require_vision() -> None:
    if Image is None or np is None:
        raise StudioError("Image operations require the optional vision extra: pip install -e '.[vision]'", code="vision_extra_missing", http_status=503)


def inspect_image(path: str | Path) -> dict[str, Any]:
    require_vision()
    file_path = Path(path)
    if not file_path.is_file():
        raise StudioError("Image file does not exist", code="file_not_found", details={"path": str(file_path)}, http_status=404)
    try:
        with Image.open(file_path) as image:
            image.load()
            rgba = image.convert("RGBA")
            alpha = np.asarray(rgba.getchannel("A"))
            visible = alpha > 0
            y, x = np.where(visible)
            bbox = [int(x.min()), int(y.min()), int(x.max()) + 1, int(y.max()) + 1] if visible.any() else None
            total = int(image.width * image.height)
            occupancy = float(visible.sum() / total) if total else 0.0
            alpha_unique = int(np.unique(alpha).size)
            rgb = np.asarray(rgba.convert("RGB"))
            # A deliberately cheap histogram signal, not an aesthetic score.
            hist_entropy = 0.0
            for channel in range(3):
                hist = np.bincount((rgb[:, :, channel] // 4).ravel(), minlength=64).astype(np.float64)
                probs = hist[hist > 0] / hist.sum()
                hist_entropy += float(-(probs * np.log2(probs)).sum()) / 3
            return {"path": str(file_path), "sha256": sha256_file(file_path), "format": image.format,
                    "mode": image.mode, "width": image.width, "height": image.height,
                    "has_alpha": "A" in image.getbands() or image.mode in {"P"},
                    "alpha_unique_values": alpha_unique, "visible_bbox": bbox,
                    "visible_occupancy": round(occupancy, 6), "nonempty": bool(visible.any()),
                    "rgb_coarse_entropy_bits": round(hist_entropy, 4),
                    "interpretation": "Technical diagnostics only. These signals do not establish visual quality or art-direction approval."}
    except (OSError, ValueError) as exc:
        raise StudioError("Could not decode image", code="image_decode_error", details={"path": str(file_path), "reason": str(exc)}) from exc


def trim_transparent(image: Any, threshold: int = 0, padding: int = 0) -> Any:
    require_vision()
    if not 0 <= threshold <= 255 or padding < 0:
        raise StudioError("threshold must be 0..255 and padding non-negative", code="invalid_processing_options")
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    if threshold:
        alpha = alpha.point(lambda val: 255 if val > threshold else 0)
    bbox = alpha.getbbox()
    if bbox is None:
        raise StudioError("Image contains no visible pixels", code="empty_image")
    left, top, right, bottom = bbox
    return rgba.crop((max(0, left-padding), max(0, top-padding), min(rgba.width, right+padding), min(rgba.height, bottom+padding)))


def remove_edge_background(image: Any, color: str | tuple[int, int, int], tolerance: int = 24) -> Any:
    """Make only edge-connected pixels near the selected color transparent.

    This conservative flood-fill protects matching interior details better than global color replacement.
    RGB distance uses int32 to avoid integer overflow. It does not perform semantic matting.
    """
    require_vision()
    if not 0 <= tolerance <= 441:
        raise StudioError("tolerance must be in 0..441", code="invalid_processing_options")
    if isinstance(color, str):
        token = color.strip().lstrip("#")
        if len(token) != 6:
            raise StudioError("color must use #RRGGBB", code="invalid_color")
        try:
            color = tuple(int(token[i:i+2], 16) for i in (0, 2, 4))
        except ValueError as exc:
            raise StudioError("color must use #RRGGBB", code="invalid_color") from exc
    if len(color) != 3 or any(not isinstance(v, int) or not 0 <= v <= 255 for v in color):
        raise StudioError("color must contain 3 integer channels in 0..255", code="invalid_color")
    rgba = np.asarray(image.convert("RGBA")).copy()
    rgb = rgba[:, :, :3].astype(np.int32)
    delta = rgb - np.asarray(color, dtype=np.int32)
    candidates = np.sum(delta * delta, axis=2) <= tolerance * tolerance
    height, width = candidates.shape
    connected = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    def enqueue(y: int, x: int) -> None:
        if candidates[y, x] and not connected[y, x]:
            connected[y, x] = True
            queue.append((y, x))
    for x in range(width):
        enqueue(0, x)
        enqueue(height - 1, x)
    for y in range(height):
        enqueue(y, 0)
        enqueue(y, width - 1)
    while queue:
        y, x = queue.popleft()
        if y > 0: enqueue(y - 1, x)
        if y + 1 < height: enqueue(y + 1, x)
        if x > 0: enqueue(y, x - 1)
        if x + 1 < width: enqueue(y, x + 1)
    rgba[:, :, 3][connected] = 0
    return Image.fromarray(rgba, "RGBA")


def harmonize(image: Any, *, saturation: float = 1.0, contrast: float = 1.0, brightness: float = 1.0, sharpen: float = 0.0) -> Any:
    require_vision()
    if any(not math.isfinite(x) or x < 0 or x > 3 for x in (saturation, contrast, brightness)) or not 0 <= sharpen <= 5:
        raise StudioError("Adjustments out of safe range", code="invalid_processing_options")
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    rgb = ImageEnhance.Color(rgba.convert("RGB")).enhance(saturation)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    if sharpen:
        rgb = ImageEnhance.Sharpness(rgb).enhance(sharpen)
    rgb.putalpha(alpha)
    return rgb


def process_image(source: str | Path, destination: str | Path, operations: dict[str, Any]) -> dict[str, Any]:
    require_vision()
    source_path, dest_path = Path(source), Path(destination)
    if not source_path.is_file():
        raise StudioError("Source image does not exist", code="file_not_found", details={"path": str(source_path)}, http_status=404)
    if not isinstance(operations, dict):
        raise StudioError("operations must be an object", code="invalid_operations")
    allowed = {"remove_background", "trim", "color", "resize"}
    unknown = sorted(set(operations) - allowed)
    if unknown:
        raise StudioError("Unknown image operation", code="unknown_image_operation", details={"unknown": unknown, "allowed": sorted(allowed)})
    for name, opts in operations.items():
        if not isinstance(opts, dict):
            raise StudioError("Operation arguments must be objects", code="invalid_operations", details={"operation": name})
    with Image.open(source_path) as opened:
        result = opened.convert("RGBA")
    if "remove_background" in operations:
        opts = operations["remove_background"]
        result = remove_edge_background(result, opts["color"], int(opts.get("tolerance", 24)))
    if "trim" in operations:
        opts = operations["trim"]
        result = trim_transparent(result, int(opts.get("threshold", 0)), int(opts.get("padding", 0)))
    if "color" in operations:
        result = harmonize(result, **operations["color"])
    if "resize" in operations:
        opts = operations["resize"]
        width, height = int(opts["width"]), int(opts["height"])
        if not 1 <= width <= 8192 or not 1 <= height <= 8192:
            raise StudioError("Resize dimensions must be within 1..8192", code="invalid_dimensions")
        method = str(opts.get("resample", "lanczos")).lower()
        methods = {"nearest": Image.Resampling.NEAREST, "bilinear": Image.Resampling.BILINEAR,
                   "bicubic": Image.Resampling.BICUBIC, "lanczos": Image.Resampling.LANCZOS}
        if method not in methods:
            raise StudioError("Unsupported resampling method", code="invalid_resampling", details={"allowed": sorted(methods)})
        result = result.resize((width, height), methods[method])
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(dest_path, format="PNG", optimize=True)
    return {"source": str(source_path), "destination": str(dest_path), "source_sha256": sha256_file(source_path),
            "output_sha256": sha256_file(dest_path), "operations": operations, "inspection": inspect_image(dest_path)}


def build_contact_sheet(image_paths: list[str | Path], destination: str | Path, *, cell_size: tuple[int, int] = (320, 320), columns: int = 3, labels: list[str] | None = None) -> dict[str, Any]:
    require_vision()
    if not image_paths or not 1 <= columns <= 12 or any(dim < 32 or dim > 2048 for dim in cell_size):
        raise StudioError("Provide images, 1..12 columns, and cell sizes in 32..2048", code="invalid_contact_sheet")
    rows = math.ceil(len(image_paths) / columns)
    label_height = 32
    canvas = Image.new("RGB", (columns * cell_size[0], rows * (cell_size[1] + label_height)), (24, 27, 35))
    draw = ImageDraw.Draw(canvas)
    for index, path_value in enumerate(image_paths):
        path = Path(path_value)
        if not path.is_file():
            raise StudioError("Contact-sheet input is missing", code="file_not_found", details={"path": str(path)})
        with Image.open(path) as opened:
            image = opened.convert("RGBA")
        image.thumbnail(cell_size, Image.Resampling.LANCZOS)
        x = (index % columns) * cell_size[0]
        y = (index // columns) * (cell_size[1] + label_height)
        tile = Image.new("RGBA", cell_size, (36, 42, 52, 255))
        tile.alpha_composite(image, ((cell_size[0]-image.width)//2, (cell_size[1]-image.height)//2))
        canvas.paste(tile.convert("RGB"), (x, y))
        label = labels[index] if labels and index < len(labels) else path.name
        draw.text((x + 8, y + cell_size[1] + 7), label[:64], fill=(233, 236, 242))
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target, format="PNG", optimize=True)
    return {"destination": str(target), "sha256": sha256_file(target), "count": len(image_paths), "columns": columns, "rows": rows}
