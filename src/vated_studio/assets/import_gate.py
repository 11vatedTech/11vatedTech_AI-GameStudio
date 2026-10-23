from __future__ import annotations

from pathlib import Path
from typing import Any

from ..jsonio import atomic_write_json
from .animation import audit_frames
from .animation_review import build_animation_review


def import_frames_for_review(frame_paths: list[str | Path], *, subject_id: str, review_path: str | Path,
                             anchor: str = "bottom-center", drift_warning_px: float = 6.0) -> dict[str, Any]:
    """Audit frames from any source and save a review record next to them.

    Works without a generator: the frames can come from any tool or a human artist. The saved
    record is always reviewer_type "automated" with human_gate true. Semantic criteria stay
    "pending" until a person records a decision.
    """
    report = audit_frames(frame_paths, anchor=anchor, drift_warning_px=drift_warning_px)
    record = build_animation_review(report, review_id=f"review-{subject_id}", subject_id=subject_id)
    atomic_write_json(review_path, record)
    return {"review_path": str(review_path), "record": record, "warnings": report["warnings"]}
