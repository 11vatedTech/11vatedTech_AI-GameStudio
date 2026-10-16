from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import math

from ..errors import StudioError
from ..jsonio import atomic_write_json, sha256_file
from .images import require_vision

try:
    import numpy as np
    from PIL import Image, ImageChops, ImageDraw, ImageStat
except ImportError:
    np = None
    Image = ImageChops = ImageDraw = ImageStat = None


def _frame_metrics(image: Any) -> dict[str, Any]:
    rgba = image.convert("RGBA")
    alpha = np.asarray(rgba.getchannel("A"))
    visible = alpha > 0
    ys, xs = np.where(visible)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if visible.any() else None
    return {"bbox": bbox, "visible_pixels": int(visible.sum()), "alpha_unique": int(np.unique(alpha).size)}


def audit_frames(frame_paths: list[str | Path], *, anchor: str = "bottom-center", drift_warning_px: float = 6.0,
                 duplicate_threshold: float = 0.0) -> dict[str, Any]:
    require_vision()
    if not frame_paths:
        raise StudioError("At least one animation frame is required", code="no_frames")
    if anchor not in {"bottom-center", "center", "top-center"}:
        raise StudioError("Unsupported anchor convention", code="invalid_anchor")
    frames = []
    for item in frame_paths:
        path = Path(item)
        if not path.is_file():
            raise StudioError("Animation frame does not exist", code="file_not_found", details={"path": str(path)})
        try:
            with Image.open(path) as opened:
                frame = opened.convert("RGBA").copy()
        except OSError as exc:
            raise StudioError("Could not decode animation frame", code="image_decode_error", details={"path": str(path)}) from exc
        frames.append((path, frame, _frame_metrics(frame)))
    sizes = [list(frame.size) for _, frame, _ in frames]
    dimensions_consistent = len({tuple(size) for size in sizes}) == 1
    anchors: list[tuple[float, float] | None] = []
    for _, frame, metrics in frames:
        bbox = metrics["bbox"]
        if bbox is None:
            anchors.append(None)
        elif anchor == "bottom-center":
            anchors.append(((bbox[0] + bbox[2]) / 2, float(bbox[3] - 1)))
        elif anchor == "top-center":
            anchors.append(((bbox[0] + bbox[2]) / 2, float(bbox[1])))
        else:
            anchors.append(((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2))
    valid_anchors = [point for point in anchors if point is not None]
    if valid_anchors:
        mean_anchor = (sum(point[0] for point in valid_anchors)/len(valid_anchors), sum(point[1] for point in valid_anchors)/len(valid_anchors))
        drift = [round(math.hypot(point[0]-mean_anchor[0], point[1]-mean_anchor[1]), 3) if point is not None else None for point in anchors]
        max_drift = max((value for value in drift if value is not None), default=0.0)
    else:
        drift, max_drift = [None for _ in anchors], None
    frame_hashes = [hashlib.sha256(frame.tobytes()).hexdigest() for _, frame, _ in frames]
    exact_duplicates = sorted({hash_value for hash_value in frame_hashes if frame_hashes.count(hash_value) > 1})
    mean_deltas: list[float] = []
    alpha_deltas: list[float] = []
    for index in range(1, len(frames)):
        a = np.asarray(frames[index-1][1]).astype(np.int16)
        b = np.asarray(frames[index][1]).astype(np.int16)
        if a.shape == b.shape:
            mean_deltas.append(round(float(np.abs(a[:, :, :3] - b[:, :, :3]).mean()), 4))
            alpha_deltas.append(round(float(np.abs(a[:, :, 3] - b[:, :, 3]).mean()), 4))
        else:
            mean_deltas.append(-1.0)
            alpha_deltas.append(-1.0)
    warnings = []
    if not dimensions_consistent:
        warnings.append("frame_dimensions_differ")
    if any(item[2]["bbox"] is None for item in frames):
        warnings.append("empty_or_fully_transparent_frame")
    if max_drift is not None and max_drift > drift_warning_px:
        warnings.append("anchor_drift_exceeds_threshold")
    if exact_duplicates:
        warnings.append("exact_duplicate_frames")
    if mean_deltas and any(delta == 0 for delta in mean_deltas):
        warnings.append("consecutive_identical_rgb_content")
    return {"frame_count": len(frames), "frames": [{"path": str(path), "size": list(frame.size), **metrics, "sha256": sha256_file(path)} for path, frame, metrics in frames],
            "dimensions_consistent": dimensions_consistent, "dimensions": sizes, "anchor": anchor,
            "anchor_positions": anchors, "anchor_drift_px": drift, "max_anchor_drift_px": max_drift,
            "mean_adjacent_rgb_delta": mean_deltas, "mean_adjacent_alpha_delta": alpha_deltas,
            "exact_duplicate_frame_hashes": exact_duplicates, "warnings": warnings,
            "interpretation": "This report detects technical signals, not semantic identity or artistic motion quality. Inspect the animation at target playback speed and in-engine scale."}


def assemble_animation(frame_paths: list[str | Path], output_stem: str | Path, *, fps: float = 10.0,
                       anchor: str = "bottom-center", padding: int = 4, background: str = "transparent") -> dict[str, Any]:
    require_vision()
    if not frame_paths:
        raise StudioError("At least one frame is required", code="no_frames")
    if not math.isfinite(fps) or not 1 <= fps <= 60 or not 0 <= padding <= 128:
        raise StudioError("fps must be 1..60 and padding 0..128", code="invalid_animation_options")
    if background != "transparent":
        raise StudioError("Only transparent output is currently supported; provide compositing as an explicit later stage", code="unsupported_background")
    if anchor not in {"bottom-center", "center", "top-center"}:
        raise StudioError("Unsupported anchor convention", code="invalid_anchor")
    loaded = []
    for value in frame_paths:
        path = Path(value)
        if not path.is_file():
            raise StudioError("Animation frame not found", code="file_not_found", details={"path": str(path)})
        with Image.open(path) as opened:
            image = opened.convert("RGBA").copy()
        bbox = image.getchannel("A").getbbox()
        if bbox is None:
            raise StudioError("Frame has no visible pixels", code="empty_frame", details={"path": str(path)})
        loaded.append((path, image, bbox))
    content_w = max(box[2]-box[0] for _, _, box in loaded)
    content_h = max(box[3]-box[1] for _, _, box in loaded)
    canvas_w = content_w + padding * 2
    canvas_h = content_h + padding * 2
    rendered = []
    positions = []
    for _, image, box in loaded:
        cropped = image.crop(box)
        if anchor == "bottom-center":
            x = (canvas_w - cropped.width) // 2
            y = canvas_h - padding - cropped.height
        elif anchor == "top-center":
            x = (canvas_w - cropped.width) // 2
            y = padding
        else:
            x = (canvas_w - cropped.width) // 2
            y = (canvas_h - cropped.height) // 2
        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        canvas.alpha_composite(cropped, (x, y))
        rendered.append(canvas)
        positions.append({"x": x, "y": y, "content_width": cropped.width, "content_height": cropped.height})
    stem = Path(output_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    gif_path = stem.with_suffix(".gif")
    sheet_path = stem.with_name(stem.name + "_spritesheet.png")
    manifest_path = stem.with_name(stem.name + "_animation.json")
    rendered[0].save(gif_path, save_all=True, append_images=rendered[1:], duration=round(1000/fps), loop=0, disposal=2, transparency=0, optimize=False)
    sheet = Image.new("RGBA", (canvas_w * len(rendered), canvas_h), (0, 0, 0, 0))
    for index, frame in enumerate(rendered):
        sheet.alpha_composite(frame, (index * canvas_w, 0))
    sheet.save(sheet_path, optimize=True)
    audit = audit_frames(frame_paths, anchor=anchor)
    manifest = {"schema_version": "1.0", "animation_id": stem.name, "fps": fps, "loop": True,
                "frame_count": len(rendered), "frame_size": [canvas_w, canvas_h], "anchor": anchor,
                "source_frames": [{"path": str(path), "sha256": sha256_file(path)} for path, _, _ in loaded],
                "layout": positions, "outputs": {"gif": gif_path.name, "spritesheet": sheet_path.name},
                "source_audit": audit, "status": "assembled_requires_visual_review"}
    atomic_write_json(manifest_path, manifest)
    return {"gif": str(gif_path), "spritesheet": str(sheet_path), "manifest": str(manifest_path), "frame_count": len(rendered), "frame_size": [canvas_w, canvas_h], "audit": audit}
