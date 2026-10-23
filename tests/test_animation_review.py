import json
from pathlib import Path

import pytest

pytest.importorskip("PIL")
jsonschema = pytest.importorskip("jsonschema")

from PIL import Image, ImageDraw

from vated_studio.assets.animation import audit_frames
from vated_studio.assets.animation_review import SEMANTIC_CRITERIA, build_animation_review

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/review-record.schema.json").read_text())


def _frame(path: Path, x: int, size=(32, 32)) -> Path:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([x, 20, x + 6, 31], fill=(200, 40, 40, 255))
    img.save(path)
    return path


def test_clean_sequence_is_not_approved_and_semantic_criteria_stay_pending(tmp_path):
    frames = [_frame(tmp_path / f"f{i}.png", 10 + i) for i in range(3)]
    report = audit_frames(frames)
    record = build_animation_review(report, review_id="rev-1", subject_id="hero-idle")
    jsonschema.validate(record, SCHEMA)
    assert record["decision"] == "not_reviewed"
    assert record["reviewer_type"] == "automated"
    assert record["human_gate"] is True
    assert all(record["criteria_results"][name] == "pending" for name in SEMANTIC_CRITERIA)


def test_duplicate_frames_fail_the_matching_criterion(tmp_path):
    a = _frame(tmp_path / "a.png", 10)
    b = _frame(tmp_path / "b.png", 10)
    report = audit_frames([a, b])
    record = build_animation_review(report, review_id="rev-2", subject_id="hero-walk")
    jsonschema.validate(record, SCHEMA)
    assert "exact_duplicate_frames" in report["warnings"]
    assert record["criteria_results"]["no_duplicate_frames"] == "fail"
    assert record["decision"] == "revise"


def test_drift_fails_anchor_criterion_without_approving_motion(tmp_path):
    a = _frame(tmp_path / "a.png", 2)
    b = _frame(tmp_path / "b.png", 20)
    report = audit_frames([a, b], drift_warning_px=2.0)
    record = build_animation_review(report, review_id="rev-3", subject_id="hero-run")
    jsonschema.validate(record, SCHEMA)
    assert record["criteria_results"]["anchor_stable"] == "fail"
    assert record["decision"] == "revise"
    assert record["criteria_results"]["timing_and_weight"] == "pending"
