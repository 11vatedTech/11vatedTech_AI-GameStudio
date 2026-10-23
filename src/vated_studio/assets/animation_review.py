from __future__ import annotations

from typing import Any
from datetime import datetime, timezone

# Technical checks are derived from audit_frames warnings. Each maps to a rubric criterion
# that the automated reviewer can fail. Passing them proves only that the signal is absent.
TECHNICAL_WARNING_CRITERIA: dict[str, str] = {
    "frame_dimensions_differ": "frame_dimensions_consistent",
    "empty_or_fully_transparent_frame": "no_empty_frames",
    "anchor_drift_exceeds_threshold": "anchor_stable",
    "exact_duplicate_frames": "no_duplicate_frames",
    "consecutive_identical_rgb_content": "no_frozen_frames",
}

# Semantic criteria are never decided by code. They stay pending until a human or agent review
# records a result against them.
SEMANTIC_CRITERIA: tuple[str, ...] = (
    "identity_matches_reference",
    "action_readable_at_target_speed",
    "timing_and_weight",
    "loop_seam",
    "silhouette_and_palette_consistent",
    "in_engine_scale_and_playback",
)


def build_animation_review(report: dict[str, Any], *, review_id: str, subject_id: str,
                           created_at: str | None = None) -> dict[str, Any]:
    """Build a review-record for an audit_frames report.

    Returns a record that conforms to schemas/review-record.schema.json. The decision is
    "revise" when any technical check fails, and "not_reviewed" otherwise. It is never
    "approved" from automated checks, because semantic criteria are still pending.
    """
    warnings = set(report.get("warnings", []))
    criteria: dict[str, str] = {}
    for warning, criterion in TECHNICAL_WARNING_CRITERIA.items():
        criteria[criterion] = "fail" if warning in warnings else "pass"
    for criterion in SEMANTIC_CRITERIA:
        criteria[criterion] = "pending"
    failed = sorted(name for name, status in criteria.items() if status == "fail")
    decision = "revise" if failed else "not_reviewed"
    notes = (f"Technical checks failed: {', '.join(failed)}." if failed
             else "Technical checks passed. Semantic criteria are pending review.")
    return {
        "schema_version": "1.0",
        "review_id": review_id,
        "review_type": "animation",
        "reviewer_type": "automated",
        "subject_id": subject_id,
        "decision": decision,
        "rating": None,
        "criteria_results": criteria,
        "notes": notes + " Automated checks cannot judge identity, motion quality or readability.",
        "evidence": [frame["path"] for frame in report.get("frames", [])],
        "human_gate": True,
        "created_at": created_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
