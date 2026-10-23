import json
from pathlib import Path

import pytest

pytest.importorskip("PIL")
jsonschema = pytest.importorskip("jsonschema")

from PIL import Image, ImageDraw

from vated_studio.assets.animation_review import SEMANTIC_CRITERIA
from vated_studio.assets.import_gate import import_frames_for_review

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/review-record.schema.json").read_text())


def _frame(path: Path, x: int) -> Path:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    ImageDraw.Draw(img).rectangle([x, 20, x + 6, 31], fill=(40, 40, 200, 255))
    img.save(path)
    return path


def test_imported_frames_are_saved_as_a_pending_schema_valid_record(tmp_path):
    frames = [_frame(tmp_path / f"f{i}.png", 8 + i) for i in range(3)]
    review = tmp_path / "review.json"
    result = import_frames_for_review(frames, subject_id="hero-walk", review_path=review)
    saved = json.loads(review.read_text())
    jsonschema.validate(saved, SCHEMA)
    assert saved == result["record"]
    assert saved["reviewer_type"] == "automated"
    assert saved["human_gate"] is True
    assert saved["decision"] == "not_reviewed"
    assert all(saved["criteria_results"][c] == "pending" for c in SEMANTIC_CRITERIA)


def test_duplicate_imported_frames_are_flagged_for_revision(tmp_path):
    a = _frame(tmp_path / "a.png", 10)
    b = _frame(tmp_path / "b.png", 10)
    review = tmp_path / "review.json"
    result = import_frames_for_review([a, b], subject_id="hero-idle", review_path=review)
    assert "exact_duplicate_frames" in result["warnings"]
    assert result["record"]["decision"] == "revise"
    jsonschema.validate(json.loads(review.read_text()), SCHEMA)
